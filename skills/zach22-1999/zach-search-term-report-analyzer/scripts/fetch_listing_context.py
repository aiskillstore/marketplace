#!/usr/bin/env python3
"""抓取任意 ASIN 的亚马逊前台 Listing 上下文。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from browser_utils import check_captcha, fetch_page, get_site_config  # type: ignore


def clean_text(value: str) -> str:
    text = value.replace("\u200b", " ").replace("\xa0", " ").replace("\ufeff", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def unique_nonempty(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        text = clean_text(item)
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def extract_bullets(soup: BeautifulSoup) -> list[str]:
    bullets: list[str] = []
    selectors = [
        "#feature-bullets .a-list-item",
        "#feature-bullets li span",
        "#featurebullets_feature_div .a-list-item",
        "#featurebullets_feature_div li span",
    ]
    for selector in selectors:
        for node in soup.select(selector):
            text = clean_text(node.get_text(" ", strip=True))
            if not text or text.lower() in {"", "make sure this fits"}:
                continue
            if len(text) < 8:
                continue
            bullets.append(text)
    return unique_nonempty(bullets)[:12]


def extract_description(soup: BeautifulSoup) -> str:
    candidates = [
        soup.select_one("#productDescription"),
        soup.select_one("#aplus_feature_div"),
        soup.select_one("meta[name='description']"),
    ]
    for node in candidates:
        if not node:
            continue
        text = node.get("content", "") if node.name == "meta" else node.get_text(" ", strip=True)
        cleaned = clean_text(text)
        if len(cleaned) >= 20:
            return cleaned
    return ""


def extract_brand(soup: BeautifulSoup) -> str:
    selectors = [
        "#bylineInfo",
        "#brand",
        "#productOverview_feature_div tr td",
    ]
    for selector in selectors[:2]:
        node = soup.select_one(selector)
        if node:
            text = clean_text(node.get_text(" ", strip=True))
            if text:
                match = re.search(r"visit the\s+(.+?)\s+store", text, flags=re.IGNORECASE)
                return clean_text(match.group(1)) if match else text

    for row in soup.select("#productOverview_feature_div tr"):
        cells = row.select("td, th")
        if len(cells) >= 2 and "brand" in cells[0].get_text(" ", strip=True).lower():
            return clean_text(cells[1].get_text(" ", strip=True))
    return ""


def extract_overview(soup: BeautifulSoup) -> dict[str, str]:
    overview: dict[str, str] = {}
    for table_selector in [
        "#productOverview_feature_div table",
        "#productDetails_techSpec_section_1",
        "#productDetails_detailBullets_sections1",
    ]:
        table = soup.select_one(table_selector)
        if not table:
            continue
        for row in table.select("tr"):
            cells = row.select("th, td")
            if len(cells) < 2:
                continue
            key = clean_text(cells[0].get_text(" ", strip=True)).rstrip(":")
            value = clean_text(cells[1].get_text(" ", strip=True))
            if key and value and key not in overview:
                overview[key] = value
    return overview


def extract_breadcrumb(soup: BeautifulSoup) -> str:
    links = soup.select("#wayfinding-breadcrumbs_feature_div a, #wayfinding-breadcrumbs_container a")
    return " › ".join(clean_text(node.get_text(" ", strip=True)) for node in links if clean_text(node.get_text(" ", strip=True)))


def extract_price_text(soup: BeautifulSoup) -> str:
    for selector in [
        "span.a-price span.a-offscreen",
        "#corePriceDisplay_desktop_feature_div .a-offscreen",
        "#corePrice_feature_div .a-offscreen",
    ]:
        node = soup.select_one(selector)
        if node:
            text = clean_text(node.get_text(" ", strip=True))
            if text:
                return text
    return ""


def extract_listing_context(html: str, asin: str, site_code: str, domain: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "asin": asin.upper(),
        "site": site_code.upper(),
        "url": f"https://www.{domain}/dp/{asin.upper()}",
        "page_status": "unknown",
        "captcha": False,
        "title": "",
        "brand": "",
        "bullets": [],
        "description": "",
        "breadcrumb": "",
        "price": "",
        "product_overview": {},
        "context_text": "",
        "anomalies": [],
    }
    if not html or len(html) < 1000:
        result["page_status"] = "fetch_failed"
        result["anomalies"].append("页面抓取失败，未获取到有效 HTML")
        return result
    if check_captcha(html):
        result["page_status"] = "captcha"
        result["captcha"] = True
        result["anomalies"].append("被亚马逊验证码拦截")
        return result

    soup = BeautifulSoup(html, "html.parser")
    title_node = soup.select_one("#productTitle")
    title = clean_text(title_node.get_text(" ", strip=True)) if title_node else ""
    if not title:
        result["page_status"] = "no_content"
        result["anomalies"].append("未提取到商品标题")
        return result

    result["page_status"] = "ok"
    result["title"] = title
    result["brand"] = extract_brand(soup)
    result["bullets"] = extract_bullets(soup)
    result["description"] = extract_description(soup)
    result["breadcrumb"] = extract_breadcrumb(soup)
    result["price"] = extract_price_text(soup)
    result["product_overview"] = extract_overview(soup)

    parts = [result["title"], result["brand"], result["breadcrumb"], result["description"], *result["bullets"]]
    parts.extend(f"{key}: {value}" for key, value in result["product_overview"].items())
    result["context_text"] = "\n".join(part for part in parts if part)
    return result


def fetch_listing_context(asin: str, site_code: str) -> dict[str, Any]:
    site = get_site_config(site_code)
    domain = site["domain"]
    url = f"https://www.{domain}/dp/{asin.upper()}"
    html = fetch_page(url)
    return extract_listing_context(html, asin, site_code, domain)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抓取亚马逊前台 Listing 上下文")
    parser.add_argument("asin", help="目标 ASIN")
    parser.add_argument("--site", default="US", help="站点代码，默认 US")
    parser.add_argument("--output", help="可选：输出 JSON 文件路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = fetch_listing_context(args.asin, args.site)
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
