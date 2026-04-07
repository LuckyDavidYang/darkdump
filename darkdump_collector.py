"""Programmatic collection helpers for Darkdump."""

from darkdump import Darkdump


def collect_dark_net(key_word, amount):
    if not isinstance(key_word, str):
        raise TypeError("key_word must be a string.")

    normalized_keyword = key_word.strip()
    if not normalized_keyword:
        raise ValueError("key_word must not be empty.")

    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an integer.")

    if amount <= 0:
        raise ValueError("amount must be greater than 0.")

    return Darkdump().collect(
        normalized_keyword,
        amount,
        use_proxy=True,
        scrape_sites=True,
        scrape_images=False,
    )

if __name__ == '__main__':
    result = collect_dark_net('长沙', 20)
    print(result)
