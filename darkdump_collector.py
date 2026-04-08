"""Programmatic collection helpers for Darkdump."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from darkdump import Darkdump


TOP_LEVEL_EXPORT_COLUMNS = [
    "query",
    "requested_amount",
    "returned_count",
    "proxy_enabled",
    "scrape_enabled",
    "images_enabled",
    "tor_checked",
    "tor_ok",
    "tor_ip",
    "errors",
]

RESULT_EXPORT_COLUMNS = [
    "index",
    "title",
    "description",
    "onion_link",
    "keywords",
    "sentiment",
    "metadata",
    "links",
    "link_count",
    "emails",
    "documents",
]

EXCEL_COLUMNS = [
    "采集日期",
    "采集时间",
    "搜索关键词",
    *TOP_LEVEL_EXPORT_COLUMNS,
    *RESULT_EXPORT_COLUMNS,
]


def _validate_keyword(key_word):
    if not isinstance(key_word, str):
        raise TypeError("key_word must be a string.")

    normalized_keyword = key_word.strip()
    if not normalized_keyword:
        raise ValueError("key_word must not be empty.")

    return normalized_keyword


def _validate_amount(amount):
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount must be an integer.")

    if amount <= 0:
        raise ValueError("amount must be greater than 0.")

    return amount


def _serialize_excel_value(value):
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value


def collect_dark_net(key_word, amount):
    normalized_keyword = _validate_keyword(key_word)
    amount = _validate_amount(amount)

    return Darkdump().collect(
        normalized_keyword,
        amount,
        use_proxy=True,
        scrape_sites=True,
        scrape_images=False,
    )


def batch_collect_dark_net(key_words, amount):
    amount = _validate_amount(amount)

    if not isinstance(key_words, (list, tuple)):
        raise TypeError("key_words must be a list or tuple of strings.")
    if not key_words:
        raise ValueError("key_words must not be empty.")

    normalized_keywords = [_validate_keyword(key_word) for key_word in key_words]

    batch_result = {
        "requested_amount": amount,
        "keywords": normalized_keywords,
        "success_count": 0,
        "failure_count": 0,
        "items": [],
    }

    for key_word in normalized_keywords:
        now = datetime.now()
        item = {
            "collected_date": now.strftime("%Y-%m-%d"),
            "collected_time": now.strftime("%H:%M:%S"),
            "search_keyword": key_word,
        }

        try:
            collect_result = collect_dark_net(key_word, amount)
        except Exception as exc:
            item["status"] = "error"
            item["error"] = str(exc)
            batch_result["failure_count"] += 1
        else:
            item["status"] = "success"
            item["collect_result"] = collect_result
            batch_result["success_count"] += 1

        batch_result["items"].append(item)

    return batch_result


def save_batch_collect_dark_net_to_excel(batch_result, output_path):
    from openpyxl import Workbook

    if not isinstance(batch_result, dict):
        raise TypeError("batch_result must be a dict.")
    if "items" not in batch_result or not isinstance(batch_result["items"], list):
        raise ValueError("batch_result must contain an items list.")

    output_path = Path(output_path)
    if not output_path.name:
        raise ValueError("output_path must point to a file.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "results"
    worksheet.append(EXCEL_COLUMNS)

    for item in batch_result["items"]:
        if item.get("status") != "success":
            continue

        collect_result = item.get("collect_result") or {}
        result_rows = collect_result.get("results") or []
        if not result_rows:
            continue

        top_level_values = {
            column: _serialize_excel_value(collect_result.get(column))
            for column in TOP_LEVEL_EXPORT_COLUMNS
        }

        for result_row in result_rows:
            row = [
                item.get("collected_date"),
                item.get("collected_time"),
                item.get("search_keyword"),
            ]

            row.extend(top_level_values[column] for column in TOP_LEVEL_EXPORT_COLUMNS)
            row.extend(_serialize_excel_value(result_row.get(column)) for column in RESULT_EXPORT_COLUMNS)
            worksheet.append(row)

    workbook.save(output_path)
    return str(output_path.resolve())
