"""Programmatic collection helpers for Darkdump."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
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


DEFAULT_KEY_WORDS_STR = '中联重科,Zoomlion,三一重工,三一集团,Sany,华菱钢铁,湖南钢铁集团,湖南广电,芒果TV,芒果超媒,爱尔眼科,Aier Eye,长沙银行,Bank of Changsha,湖南银行,华融湘江银行,财信金控,Chasing Financial,绝味食品,绝味鸭脖,茶颜悦色,湖南茶悦,步步高商业,老百姓大药房,益丰药房,景嘉微,Jingjia Micro,蓝思科技,Lens Technology,拓维信息,Talkweb,威胜信息,Wasion,铁建重工,CRCHI,山河智能,Sunward,楚天科技,Truking,盐津铺子,水羊股份,御家汇,澳优乳业,Ausnutria,湖南建投,湖南建工,湖南路桥,湖南轨道交通,湖南航空,红土航空,远大空调,远大住工,Broad Group,隆平高科,电广传媒,湖南省供销合作社,湖南供销,湖南省供销合作总社,AI+新供销,中南传媒,中南出版,友谊阿波罗,友阿股份,通程控股,湖南黄金,长城信息,圣湘生物,Sansure Biotech,达嘉维康,尔康制药,九芝堂,克明面业,华纳大药厂,宇环数控,泰嘉股份,金杯电工,湘佳股份,梦洁家纺,三诺生物,可孚医疗,松井股份,国科微,Goke Micro,水清木华,天仪研究院,Spacety,兴盛优选,Xingsheng Selected,安克创新,Anker,湖南投资,华天酒店,Huatian Hotel,现代投资,湘财股份,湘财证券,华升股份,湖南海利,湘邮科技,科力远,Corun,航天环宇,华曙高科,Farsoon,军信股份,军信环保,族兴新材,华菱线缆,长沙水业集团,长沙城发集团,长沙市交通投资,湖南高速集团,湖南交水建,湖南轻盐集团,雪天盐业,@zoomlion.com,@sany.com.cn,@hnxg.com.cn,@mgtv.com,@hunantv.com,@aierchina.com,@bankofchangsha.com,@hunan-bank.com,@chasing.com.cn,@juewei.cn,@chayan.com,@bbg.com.cn,@lbxcn.com,@yfpharmacy.com,@jingjiamicro.com,@lensgroup.com,@talkweb.com.cn,@wasion.com,@crchi.com,@sunward.com.cn,@truking.cn,@yanjinfood.com,@syounggroup.com,@ausnutria.com,@hnjg.com,@hnrb.cn,@hngdjt.com,@airhunan.com,@broad.net,@lpht.com.cn,@hncatv.com,@zndw.com,@youa.com.cn,@tongcheng.com,@hngold.com,@gwic.com.cn,@sansure.com.cn,@dajiaweikang.com,@erkang.com,@jiuzhitong.com,@sinocare.com,@cofo.com.cn,@gokemicro.com,@anker.com,@htej.com,@modern-invest.com,@xcsc.com,@hn-haili.com,@corun.com,@farsoon.com,@watercs.com,@csgdjt.com,@xnsalt.com,詹纯新,向文波,梁稳根,李建宇,龚政文,蔡怀军,陈邦,李力,赵小中,黄卫忠,程蓓,戴文军,吕良,王填,谢子龙,高毅,曾万辉,周群飞,郑俊龙,李新宇,吉为,赵晖,何清华,唐岳,张学武,戴跃锋,颜卫砖,蔡典维,王术飞,吴重阳,张跃,毛长青,王艳忠,彭玻,胡子敬,周兆达,王建华,戴立忠,王毅清,帅放文,李振国,陈克明,许世雄,方正,吴学愚,姜天武,李少波,张敏,向平,阳萌,侯代林,杨宏伟,马玉学,高军,刘卫东,李立新,钟发平,李茂,许小曙,李自明,彭坚,张胜,李建红,陈金辉,胡贺波,冯传良,oa.zoomlion.com,vpn.zoomlion.com,git.zoomlion.com,oa.sany.com.cn,vpn.sany.com.cn,git.sany.com.cn,mail.mgtv.com,jira.mgtv.com,oa.aierchina.com,hr.bbg.com.cn,mail.bankofchangsha.com,oa.talkweb.com.cn,git.talkweb.com.cn,vpn.lensgroup.com,oa.hnjg.com,mail.chasing.com.cn,admin.anker.com,内部资料泄露,核心源代码,员工通讯录,高管邮箱密码,数据库备份,后台管理权限,财务报表泄露,服务器凭证,SSH密钥,API_KEY泄露,未授权访问,勒索软件受害者,被黑客攻击,暗网交易数据,拖库,SQL注入数据,gitlab账号,默认密码,敏感信息,商业机密,并购计划,裁员名单,实名举报,职务侵占,利益输送,税务违规,资金链断裂,债务违约,config.php,database.yml,id_rsa,password.txt,shadow,dump.sql,users.sql,admin_password,ftp_credentials,rdp_access,cpanel_login,AWS_SECRET_ACCESS_KEY'
DEFAULT_KEY_WORDS = DEFAULT_KEY_WORDS_STR.split(',')

DEFAULT_AMOUNT = 20
DEFAULT_RETRY_TIMES = 3
DEFAULT_PROCESSES = 10


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


def _validate_retry_times(retry_times):
    if isinstance(retry_times, bool) or not isinstance(retry_times, int):
        raise TypeError("retry_times must be an integer.")

    if retry_times < 0:
        raise ValueError("retry_times must be greater than or equal to 0.")

    return retry_times


def _validate_processes(processes):
    if isinstance(processes, bool) or not isinstance(processes, int):
        raise TypeError("processes must be an integer.")

    if processes <= 0:
        raise ValueError("processes must be greater than 0.")

    return processes


def _serialize_excel_value(value):
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value


def _print_collect_summary(query, returned_count, tor_ip, error_count, error_message=None):
    summary = (
        f"[collect_dark_net] query={query} "
        f"returned_count={returned_count} "
        f"tor_ip={tor_ip} "
        f"error_count={error_count}"
    )
    if error_message is not None:
        summary += f" error={error_message}"
    print(summary)


def _execute_collect_dark_net(key_word, amount, retry_times, print_summary):
    normalized_keyword = _validate_keyword(key_word)
    amount = _validate_amount(amount)
    retry_times = _validate_retry_times(retry_times)

    last_exception = None
    for _ in range(retry_times + 1):
        try:
            result = Darkdump().collect(
                normalized_keyword,
                amount,
                use_proxy=True,
                scrape_sites=True,
                scrape_images=False,
            )
        except Exception as exc:
            last_exception = exc
            continue

        if print_summary:
            _print_collect_summary(
                result.get("query", normalized_keyword),
                result.get("returned_count", 0),
                result.get("tor_ip"),
                len(result.get("errors") or []),
            )
        return result

    if print_summary:
        _print_collect_summary(
            normalized_keyword,
            0,
            None,
            1,
            str(last_exception),
        )
    raise last_exception


def _batch_collect_worker(index, key_word, amount, retry_times):
    now = datetime.now()
    item = {
        "collected_date": now.strftime("%Y-%m-%d"),
        "collected_time": now.strftime("%H:%M:%S"),
        "search_keyword": key_word,
    }

    try:
        collect_result = _execute_collect_dark_net(
            key_word,
            amount,
            retry_times,
            print_summary=False,
        )
    except Exception as exc:
        item["status"] = "error"
        item["error"] = str(exc)
    else:
        item["status"] = "success"
        item["collect_result"] = collect_result

    return {
        "index": index,
        "item": item,
    }


def collect_dark_net(key_word, amount, retry_times=DEFAULT_RETRY_TIMES):
    return _execute_collect_dark_net(
        key_word,
        amount,
        retry_times,
        print_summary=True,
    )


def batch_collect_dark_net(key_words, amount, processes=DEFAULT_PROCESSES):
    amount = _validate_amount(amount)
    processes = _validate_processes(processes)

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

    worker_count = min(processes, len(normalized_keywords))
    ordered_items = [None] * len(normalized_keywords)

    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        future_to_index = {
            executor.submit(
                _batch_collect_worker,
                index,
                key_word,
                amount,
                DEFAULT_RETRY_TIMES,
            ): index
            for index, key_word in enumerate(normalized_keywords)
        }

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            key_word = normalized_keywords[index]

            try:
                worker_result = future.result()
                item = worker_result["item"]
            except Exception as exc:
                now = datetime.now()
                item = {
                    "collected_date": now.strftime("%Y-%m-%d"),
                    "collected_time": now.strftime("%H:%M:%S"),
                    "search_keyword": key_word,
                    "status": "error",
                    "error": str(exc),
                }

            ordered_items[index] = item

            if item["status"] == "success":
                batch_result["success_count"] += 1
                collect_result = item["collect_result"]
                _print_collect_summary(
                    collect_result.get("query", key_word),
                    collect_result.get("returned_count", 0),
                    collect_result.get("tor_ip"),
                    len(collect_result.get("errors") or []),
                )
            else:
                batch_result["failure_count"] += 1
                _print_collect_summary(
                    key_word,
                    0,
                    None,
                    1,
                    item["error"],
                )

    batch_result["items"] = ordered_items

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


def main():
    key_words = DEFAULT_KEY_WORDS
    amount = DEFAULT_AMOUNT
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"darkdump_batch_results_{timestamp}.xlsx"

    batch_result = batch_collect_dark_net(key_words, amount)
    excel_path = save_batch_collect_dark_net_to_excel(batch_result, output_path)

    print(f"Keyword count: {len(key_words)}")
    print(f"Amount per keyword: {amount}")
    print(
        "Success count: "
        f"{batch_result['success_count']}, Failure count: {batch_result['failure_count']}"
    )
    print(f"Excel saved to: {excel_path}")

    return {
        "key_words": key_words,
        "amount": amount,
        "batch_result": batch_result,
        "excel_path": excel_path,
    }


if __name__ == "__main__":
    main()
