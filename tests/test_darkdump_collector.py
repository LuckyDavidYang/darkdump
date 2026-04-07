import importlib
import sys
import unittest
import warnings
from unittest.mock import patch


class FakeResponse:
    def __init__(self, status_code=200, content="", json_data=None):
        self.status_code = status_code
        self.content = content.encode("utf-8") if isinstance(content, str) else content
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


HOMEPAGE_HTML = """
<html>
  <body>
    <form id="searchForm">
      <input type="hidden" name="nonce" value="abc123">
    </form>
  </body>
</html>
"""

SEARCH_RESULTS_HTML = """
<div id="ahmiaResultsPage">
  <li class="result">
    <a>Alpha Market</a>
    <cite>alpha.onion</cite>
    <p>Primary listing</p>
  </li>
  <li class="result">
    <a>Beta Market</a>
    <cite>http://beta.onion</cite>
    <p>Secondary listing</p>
  </li>
</div>
"""

SEARCH_RESULTS_HTML_THREE = """
<div id="ahmiaResultsPage">
  <li class="result"><a>One</a><cite>one.onion</cite><p>One desc</p></li>
  <li class="result"><a>Two</a><cite>two.onion</cite><p>Two desc</p></li>
  <li class="result"><a>Three</a><cite>three.onion</cite><p>Three desc</p></li>
</div>
"""

SITE_HTML = """
<html>
  <head>
    <meta name="description" content="test metadata">
  </head>
  <body>
    <a href="https://example.com">Example</a>
    <a href="docs/report.pdf">Report</a>
    Contact: ops@alpha.onion
  </body>
</html>
"""

SITE_HTML_BETA = """
<html>
  <head>
    <meta property="og:title" content="beta metadata">
  </head>
  <body>
    <a href="https://beta.example.com">Beta</a>
    Reach us at admin@beta.onion
  </body>
</html>
"""


def get_collect_dark_net():
    module = importlib.import_module("darkdump_collector")
    return module.collect_dark_net


class CollectDarkNetTests(unittest.TestCase):
    def test_importing_darkdump_collector_has_no_syntax_warnings(self):
        for module_name in ("darkdump_collector", "darkdump"):
            sys.modules.pop(module_name, None)

        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            collect_dark_net = get_collect_dark_net()

        self.assertTrue(callable(collect_dark_net))
        syntax_warnings = [warning for warning in caught_warnings if issubclass(warning.category, SyntaxWarning)]
        self.assertEqual(syntax_warnings, [])

    @patch("darkdump.Darkdump.analyze_text")
    @patch("darkdump.Darkdump.extract_keywords")
    @patch("darkdump.Platform.check_tor_connection", return_value=True)
    @patch("darkdump.requests.get")
    def test_collect_dark_net_returns_structured_results(
        self,
        mock_get,
        _mock_tor_check,
        mock_extract_keywords,
        mock_analyze_text,
    ):
        mock_extract_keywords.side_effect = [["alpha", "market"], ["beta", "market"]]
        mock_analyze_text.side_effect = [
            {"top_words": [("alpha", 2)], "sentiment": {"polarity": 0.4, "subjectivity": 0.2}},
            {"top_words": [("beta", 2)], "sentiment": {"polarity": 0.1, "subjectivity": 0.3}},
        ]
        mock_get.side_effect = [
            FakeResponse(content=HOMEPAGE_HTML),
            FakeResponse(content=SEARCH_RESULTS_HTML),
            FakeResponse(content=SITE_HTML),
            FakeResponse(content=SITE_HTML_BETA),
        ]

        collect_dark_net = get_collect_dark_net()
        result = collect_dark_net(" markets ", 2)

        self.assertEqual(result["query"], "markets")
        self.assertEqual(result["requested_amount"], 2)
        self.assertEqual(result["returned_count"], 2)
        self.assertTrue(result["proxy_enabled"])
        self.assertTrue(result["scrape_enabled"])
        self.assertFalse(result["images_enabled"])
        self.assertTrue(result["tor_checked"])
        self.assertTrue(result["tor_ok"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["results"]), 2)

        first_result = result["results"][0]
        self.assertEqual(first_result["index"], 1)
        self.assertEqual(first_result["title"], "Alpha Market")
        self.assertEqual(first_result["description"], "Primary listing")
        self.assertEqual(first_result["onion_link"], "http://alpha.onion")
        self.assertEqual(first_result["keywords"], ["alpha", "market"])
        self.assertEqual(first_result["sentiment"], {"polarity": 0.4, "subjectivity": 0.2})
        self.assertEqual(first_result["metadata"], {"description": "test metadata"})
        self.assertEqual(first_result["link_count"], 2)
        self.assertIn("https://example.com", first_result["links"])
        self.assertIn("ops@alpha.onion", first_result["emails"])
        self.assertEqual(first_result["documents"], ["docs/report.pdf"])

    def test_collect_dark_net_rejects_invalid_keyword(self):
        collect_dark_net = get_collect_dark_net()

        with self.assertRaises(TypeError):
            collect_dark_net(None, 1)

        with self.assertRaises(ValueError):
            collect_dark_net("   ", 1)

    def test_collect_dark_net_rejects_invalid_amount(self):
        collect_dark_net = get_collect_dark_net()

        with self.assertRaises(TypeError):
            collect_dark_net("markets", "1")

        with self.assertRaises(TypeError):
            collect_dark_net("markets", True)

        with self.assertRaises(ValueError):
            collect_dark_net("markets", 0)

    @patch("darkdump.Platform.check_tor_connection", return_value=False)
    @patch("darkdump.requests.get")
    def test_collect_dark_net_raises_when_tor_check_fails(self, mock_get, _mock_tor_check):
        mock_get.side_effect = [
            FakeResponse(content=HOMEPAGE_HTML),
            FakeResponse(content=SEARCH_RESULTS_HTML),
        ]

        collect_dark_net = get_collect_dark_net()
        with self.assertRaises(RuntimeError) as context:
            collect_dark_net("markets", 2)

        self.assertIn("Tor", str(context.exception))

    @patch("darkdump.requests.get")
    def test_collect_dark_net_raises_on_ahmia_homepage_failure(self, mock_get):
        mock_get.return_value = FakeResponse(status_code=500)

        collect_dark_net = get_collect_dark_net()
        with self.assertRaises(RuntimeError) as context:
            collect_dark_net("markets", 1)

        self.assertIn("Couldn't fetch", str(context.exception))

    @patch("darkdump.requests.get")
    def test_collect_dark_net_raises_when_nonce_is_missing(self, mock_get):
        mock_get.return_value = FakeResponse(content="<html><body></body></html>")

        collect_dark_net = get_collect_dark_net()
        with self.assertRaises(RuntimeError) as context:
            collect_dark_net("markets", 1)

        self.assertIn("nonce", str(context.exception))

    @patch("darkdump.requests.get")
    def test_collect_dark_net_raises_when_results_container_is_missing(self, mock_get):
        mock_get.side_effect = [
            FakeResponse(content=HOMEPAGE_HTML),
            FakeResponse(content="<html><body>No results container</body></html>"),
        ]

        collect_dark_net = get_collect_dark_net()
        with self.assertRaises(RuntimeError) as context:
            collect_dark_net("markets", 1)

        self.assertIn("extract results", str(context.exception))

    @patch("darkdump.Darkdump.analyze_text", return_value={"top_words": [], "sentiment": {"polarity": 0.0, "subjectivity": 0.0}})
    @patch("darkdump.Darkdump.extract_keywords", return_value=["survivor"])
    @patch("darkdump.Platform.check_tor_connection", return_value=True)
    @patch("darkdump.requests.get")
    def test_collect_dark_net_records_site_errors_and_continues(
        self,
        mock_get,
        _mock_tor_check,
        _mock_extract_keywords,
        _mock_analyze_text,
    ):
        mock_get.side_effect = [
            FakeResponse(content=HOMEPAGE_HTML),
            FakeResponse(content=SEARCH_RESULTS_HTML),
            RuntimeError("dead onion"),
            FakeResponse(content=SITE_HTML_BETA),
        ]

        collect_dark_net = get_collect_dark_net()
        result = collect_dark_net("markets", 2)

        self.assertEqual(result["returned_count"], 1)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["stage"], "site")
        self.assertEqual(result["errors"][0]["url"], "http://alpha.onion")
        self.assertIn("dead onion", result["errors"][0]["message"])

    @patch("darkdump.Darkdump.analyze_text", return_value={"top_words": [], "sentiment": {"polarity": 0.0, "subjectivity": 0.0}})
    @patch("darkdump.Darkdump.extract_keywords", return_value=["limited"])
    @patch("darkdump.Platform.check_tor_connection", return_value=True)
    @patch("darkdump.requests.get")
    def test_collect_dark_net_limits_results_to_requested_amount(
        self,
        mock_get,
        _mock_tor_check,
        _mock_extract_keywords,
        _mock_analyze_text,
    ):
        mock_get.side_effect = [
            FakeResponse(content=HOMEPAGE_HTML),
            FakeResponse(content=SEARCH_RESULTS_HTML_THREE),
            FakeResponse(content=SITE_HTML),
            FakeResponse(content=SITE_HTML_BETA),
            FakeResponse(content=SITE_HTML),
        ]

        collect_dark_net = get_collect_dark_net()
        result = collect_dark_net("markets", 2)

        self.assertEqual(result["returned_count"], 2)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(mock_get.call_count, 4)


if __name__ == "__main__":
    unittest.main()
