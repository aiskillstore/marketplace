"""
fetch_amazon_page.py — 抓取亚马逊商品页面，提取健康检查所需数据

用法：
    python3 fetch_amazon_page.py <ASIN> [--site US]

输出：JSON 到 stdout，包含所有检查项数据
依赖：pip install beautifulsoup4
"""

import json
import re
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_utils import fetch_page, get_site_config, check_captcha
from bs4 import BeautifulSoup


def extract_product_data(html: str, asin: str, site_code: str, domain: str) -> dict:
    """从 HTML 中提取商品页面所有检查项数据"""

    result = {
        "asin": asin,
        "site": site_code,
        "url": f"https://www.{domain}/dp/{asin}",
        "page_status": "unknown",
        "captcha": False,
        "title": "",
        "price": {},
        "seller": {},
        "cart": {},
        "delivery": {},
        "category": {},
        "bsr": [],
        "ratings": {},
        "reviews_on_page": [],
        "variants": {},
        "stock": {},
        "anomalies": [],
    }

    # 0. 检查是否拿到内容
    if not html or len(html) < 1000:
        result["page_status"] = "fetch_failed"
        result["anomalies"].append("页面抓取失败，未获取到内容")
        return result

    # 1. 检测验证码
    if check_captcha(html):
        result["page_status"] = "captcha"
        result["captcha"] = True
        result["anomalies"].append("被亚马逊验证码拦截")
        return result

    soup = BeautifulSoup(html, "html.parser")

    # 2. 检测异常页面
    html_lower = html.lower()
    if "looking for something?" in html_lower and "the web address you entered" in html_lower:
        result["page_status"] = "dog_page"
        result["anomalies"].append("狗狗页面 - ASIN 可能已下架或不存在")
        return result

    if "currently unavailable" in html_lower and "we don't know when or if this item will be back" in html_lower:
        result["page_status"] = "unavailable"
        result["anomalies"].append("商品显示 Currently Unavailable")
        return result

    # 3. 标题
    title_el = soup.select_one("#productTitle")
    result["title"] = title_el.get_text(strip=True) if title_el else ""

    if not result["title"]:
        result["page_status"] = "no_content"
        result["anomalies"].append("页面无商品标题，可能加载失败")
        return result

    result["page_status"] = "ok"

    # 4. 价格
    # 当前售价
    price_whole = soup.select_one("span.a-price-whole")
    price_frac = soup.select_one("span.a-price-fraction")
    if price_whole:
        whole = price_whole.get_text(strip=True).rstrip(".")
        frac = price_frac.get_text(strip=True) if price_frac else "00"
        result["price"]["current"] = f"{whole}.{frac}"

    # 划线价
    list_price_el = soup.select_one("span.a-text-price span.a-offscreen")
    if list_price_el:
        result["price"]["list_price"] = list_price_el.get_text(strip=True)

    # 折扣
    savings_el = soup.select_one(".savingsPercentage, #dealprice_savings .a-color-price")
    if savings_el:
        result["price"]["savings"] = savings_el.get_text(strip=True)

    # 优惠券
    coupon_el = soup.select_one("#couponText, #vpcButton span, .couponLabelText")
    if coupon_el:
        result["price"]["coupon"] = coupon_el.get_text(strip=True)

    # 5. 卖家信息
    # 直接从 sellerProfileTriggerId
    seller_el = soup.select_one("#sellerProfileTriggerId")
    if seller_el:
        result["seller"]["sold_by"] = seller_el.get_text(strip=True)

    # tabular buybox（新版页面）
    tabular_rows = soup.select("#tabular-buybox .tabular-buybox-container .a-row")
    for row in tabular_rows:
        text = row.get_text(" ", strip=True)
        if "ships from" in text.lower():
            parts = row.select(".tabular-buybox-text span, .tabular-buybox-text")
            if parts:
                result["seller"]["ships_from"] = parts[-1].get_text(strip=True)
        if "sold by" in text.lower() and not result["seller"].get("sold_by"):
            parts = row.select(".tabular-buybox-text span, .tabular-buybox-text a")
            if parts:
                result["seller"]["sold_by"] = parts[-1].get_text(strip=True)

    # 兜底：merchant-info
    if not result["seller"].get("sold_by"):
        merchant = soup.select_one("#merchant-info")
        if merchant:
            m = re.search(r"[Ss]old by\s+(.+?)(?:\s+and|\.|$)", merchant.get_text())
            if m:
                result["seller"]["sold_by"] = m.group(1).strip()

    # 6. 购物车
    result["cart"]["add_to_cart"] = soup.select_one("#add-to-cart-button") is not None
    result["cart"]["buy_now"] = soup.select_one("#buy-now-button") is not None
    result["cart"]["see_all_buying_options"] = soup.select_one(
        "#buybox-see-all-buying-choices-announce"
    ) is not None

    # 7. 配送
    delivery_el = soup.select_one(
        "#mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE, "
        "#deliveryBlockMessage, "
        "#delivery-message"
    )
    if delivery_el:
        result["delivery"]["text"] = delivery_el.get_text(" ", strip=True)[:200]

    prime_el = soup.select_one("i.a-icon-prime, #prime-tag")
    result["delivery"]["prime"] = prime_el is not None

    # 8. 类目
    # 搜索栏大类
    search_dd = soup.select_one("#searchDropdownBox option[selected]")
    result["category"]["search_department"] = search_dd.get_text(strip=True) if search_dd else ""

    # 面包屑
    breadcrumb_links = soup.select(
        "#wayfinding-breadcrumbs_feature_div a, #wayfinding-breadcrumbs_container a"
    )
    result["category"]["breadcrumb"] = " › ".join(
        a.get_text(strip=True) for a in breadcrumb_links
    ) if breadcrumb_links else ""

    # 9. BSR
    bsr_entries = []
    # 方式1: productDetails table
    for table_sel in ["#productDetails_detailBullets_sections1", "#prodDetails", "#detailBulletsWrapper_feature_div"]:
        section = soup.select_one(table_sel)
        if section:
            text = section.get_text()
            if "best sellers rank" in text.lower():
                ranks = re.findall(r"#([\d,]+)\s+in\s+(.+?)(?:\s*\(|$|\n)", text)
                for rank_num, category in ranks:
                    bsr_entries.append({
                        "rank": int(rank_num.replace(",", "")),
                        "category": category.strip(),
                    })
                if bsr_entries:
                    break
    result["bsr"] = bsr_entries

    # 10. 评分
    rating_el = soup.select_one("#acrPopover .a-icon-alt, [data-hook='rating-out-of-text']")
    if rating_el:
        m = re.search(r"([\d.]+)\s+out of\s+5", rating_el.get_text())
        if m:
            result["ratings"]["score"] = float(m.group(1))

    review_count_el = soup.select_one("#acrCustomerReviewText")
    if review_count_el:
        m = re.search(r"([\d,]+)", review_count_el.get_text())
        if m:
            result["ratings"]["count"] = int(m.group(1).replace(",", ""))

    # 11. 首页评论
    review_els = soup.select("[data-hook='review']")
    for rev in review_els[:10]:
        review = {}
        # 星级
        star_el = rev.select_one(".review-rating .a-icon-alt")
        if star_el:
            sm = re.search(r"([\d.]+)", star_el.get_text())
            if sm:
                review["stars"] = float(sm.group(1))

        # 标题
        title_el = rev.select_one("[data-hook='review-title'] span")
        if title_el:
            # 取最后一个 span（第一个可能是星级文本）
            spans = rev.select("[data-hook='review-title'] span")
            review["title"] = spans[-1].get_text(strip=True) if spans else ""

        # 日期
        date_el = rev.select_one("[data-hook='review-date']")
        if date_el:
            review["date"] = date_el.get_text(strip=True)

        # 内容
        body_el = rev.select_one("[data-hook='review-body'] span")
        if body_el:
            review["body"] = body_el.get_text(strip=True)[:300]

        if review:
            review["is_negative"] = review.get("stars", 5) <= 3
            result["reviews_on_page"].append(review)

    # 12. 变体
    variant_names = []
    for label in soup.select("#variation_label span.selection, .twisterSwatchWrapper .a-text-bold"):
        variant_names.append(label.get_text(strip=True))
    selected = []
    for sel in ["#variation_size_name .selection", "#variation_color_name .selection", "#variation_style_name .selection"]:
        el = soup.select_one(sel)
        if el:
            selected.append(el.get_text(strip=True))
    if variant_names or selected:
        result["variants"]["labels"] = variant_names
        result["variants"]["selected"] = selected

    # 13. 库存
    avail_el = soup.select_one("#availability span")
    if avail_el:
        avail_text = avail_el.get_text(strip=True)
        result["stock"]["text"] = avail_text
        result["stock"]["in_stock"] = "in stock" in avail_text.lower()
    else:
        result["stock"]["text"] = ""
        result["stock"]["in_stock"] = False

    return result


def main():
    parser = argparse.ArgumentParser(description="抓取亚马逊商品页面")
    parser.add_argument("asin", help="商品 ASIN")
    parser.add_argument("--site", default="US", help="站点代码（默认 US）")
    args = parser.parse_args()

    site_config = get_site_config(args.site)
    url = f"https://www.{site_config['domain']}/dp/{args.asin}"

    html = fetch_page(url)
    data = extract_product_data(html, args.asin, args.site.upper(), site_config["domain"])
    data["zip_code"] = site_config["zip"]

    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
