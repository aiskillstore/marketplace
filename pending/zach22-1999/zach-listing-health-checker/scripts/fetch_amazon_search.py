"""
fetch_amazon_search.py — 抓取亚马逊搜索结果页，检查 ASIN 搜索可见性

用法：
    python3 fetch_amazon_search.py <keyword> <asin> [--site US]

输出：JSON 到 stdout
依赖：pip install beautifulsoup4
"""

import json
import re
import sys
import os
import argparse
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_utils import fetch_page, get_site_config, check_captcha
from bs4 import BeautifulSoup


def extract_search_results(html: str, target_asin: str) -> dict:
    """从搜索结果 HTML 中提取数据"""

    result = {
        "captcha": False,
        "search_department": "All Departments",
        "total_results": "",
        "target_found": False,
        "target_position": None,
        "target_type": None,
        "first_page_results": [],
    }

    if not html or len(html) < 1000:
        result["captcha"] = True
        return result

    if check_captcha(html):
        result["captcha"] = True
        return result

    soup = BeautifulSoup(html, "html.parser")

    # 搜索范围
    dept_el = soup.select_one("#searchDropdownBox option[selected]")
    if dept_el:
        result["search_department"] = dept_el.get_text(strip=True)

    # 总结果数
    count_el = soup.select_one(".s-desktop-toolbar .a-text-normal, .sg-col-inner span")
    if count_el:
        result["total_results"] = count_el.get_text(strip=True)[:100]

    # 搜索结果列表
    items = soup.select("[data-component-type='s-search-result']")
    position = 0

    for item in items[:48]:
        position += 1
        item_asin = item.get("data-asin", "")
        if not item_asin:
            continue

        # 判断是否广告
        is_sponsored = bool(
            item.select_one(".puis-label-popover-default, .s-label-popover-default, [data-component-type='sp-sponsored-result']")
        )
        if not is_sponsored:
            item_text = item.get_text()[:200].lower()
            is_sponsored = "sponsored" in item_text

        # 标题
        title_el = item.select_one("h2 a span, .a-size-medium.a-text-normal")
        title = title_el.get_text(strip=True)[:120] if title_el else ""

        item_data = {
            "position": position,
            "asin": item_asin,
            "type": "sponsored" if is_sponsored else "organic",
            "title": title,
        }
        result["first_page_results"].append(item_data)

        # 检查目标 ASIN
        if item_asin.upper() == target_asin.upper():
            result["target_found"] = True
            result["target_position"] = position
            result["target_type"] = item_data["type"]

    return result


def main():
    parser = argparse.ArgumentParser(description="搜索亚马逊关键词并检查ASIN可见性")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("asin", help="目标 ASIN")
    parser.add_argument("--site", default="US", help="站点代码")
    args = parser.parse_args()

    site_config = get_site_config(args.site)
    encoded_kw = urllib.parse.quote_plus(args.keyword)
    url = f"https://www.{site_config['domain']}/s?k={encoded_kw}"

    html = fetch_page(url)
    data = extract_search_results(html, args.asin)
    data["keyword"] = args.keyword
    data["target_asin"] = args.asin
    data["url"] = url

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
