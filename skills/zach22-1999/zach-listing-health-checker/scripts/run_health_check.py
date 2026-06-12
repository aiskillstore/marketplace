#!/usr/bin/env python3
"""
run_health_check.py — Listing 健康检查总控脚本

一行命令完成：抓取商品页 → 搜索可见性 → 状态判断 → 生成 Markdown 报告。
可部署到 Mac Mini 做定时巡检（cron），不依赖 Claude Code。

用法：
    python3 run_health_check.py --asins B0PUBLIC01,B0PUBLIC02 --seller YourBrand --keywords "karaoke machine"
    python3 run_health_check.py --asins B0PUBLIC01  # 最简，默认 US，不检查卖家和搜索

依赖：pip install beautifulsoup4
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime
from typing import Optional

# 确保能 import 同目录下的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from browser_utils import fetch_page, get_site_config, throttle
from fetch_amazon_page import extract_product_data
from fetch_amazon_search import extract_search_results
import urllib.parse


# ── 状态常量 ──────────────────────────────────────────────

PASS = "pass"
WARN = "warn"
FAIL = "fail"

STATUS_ICON = {PASS: "✅", WARN: "⚠️", FAIL: "❌"}
OVERALL_ICON = {PASS: "🟢", WARN: "🟡", FAIL: "🔴"}


# ── BSR 清洗 ──────────────────────────────────────────────

def clean_bsr_category(raw: str) -> str:
    """去除 BSR 类目名后面混入的 product details 文本"""
    # 先处理多个 BSR 合并的情况：截取到第一个 "#数字 in" 之前
    m = re.search(r"\s+#\d+\s+in\s+", raw)
    if m:
        raw = raw[:m.start()]

    # 在 "Date First Available"、"Color Name" 等字段名前截断
    stop_patterns = [
        r"\s{3,}",  # 3 个以上连续空格
        r"Date First Available",
        r"Color Name",
        r"Compatible Devices",
        r"Connector Type",
        r"Speaker Count",
        r"Output Wattage",
        r"Size\s",
        r"Battery type",
        r"Media Format",
        r"Power Source",
        r"Voltage",
        r"Speaker Amplification",
        r"Charging Time",
    ]
    for pat in stop_patterns:
        m = re.search(pat, raw)
        if m:
            raw = raw[:m.start()]
    return raw.strip()


# ── 状态判断 ──────────────────────────────────────────────

def evaluate_product(data: dict, expected_seller: str = None) -> dict:
    """对单个 ASIN 的抓取数据做 9 项检查判断，返回 {检查项: (status, detail)}"""

    checks = {}

    # 1. 页面可访问性
    if data["page_status"] == "ok":
        checks["页面可访问性"] = (PASS, "正常显示")
    else:
        checks["页面可访问性"] = (FAIL, f"异常: {data['page_status']}")
        return checks  # 页面都打不开，后续项无意义

    # 2. 价格与优惠
    price = data.get("price", {})
    if price.get("current"):
        parts = [f"${price['current']}"]
        if price.get("list_price"):
            lp = price["list_price"]
            # 检查 list_price 是否大于 current（避免解析错误的数据）
            try:
                lp_num = float(re.sub(r"[^\d.]", "", lp))
                cur_num = float(price["current"])
                if lp_num > cur_num:
                    parts.insert(0, f"~~{lp}~~")
            except (ValueError, TypeError):
                pass
        if price.get("savings"):
            parts.append(f"({price['savings']})")
        if price.get("coupon"):
            parts.append(f"Coupon: {price['coupon']}")
        detail = " ".join(parts)
        checks["价格与优惠"] = (PASS, detail)
    else:
        checks["价格与优惠"] = (FAIL, "未获取到价格")

    # 3. 卖家信息
    sold_by = data.get("seller", {}).get("sold_by", "")
    ships_from = data.get("seller", {}).get("ships_from", "")
    if expected_seller:
        if sold_by.lower() == expected_seller.lower():
            checks["卖家信息"] = (PASS, f"Sold by: **{sold_by}** — 匹配")
        elif sold_by:
            checks["卖家信息"] = (FAIL, f"Sold by: **{sold_by}** — 期望 {expected_seller}，不匹配")
        else:
            checks["卖家信息"] = (FAIL, f"未获取到卖家信息，期望 {expected_seller}")
    else:
        checks["卖家信息"] = (PASS, f"Sold by: {sold_by or '未获取'}")
    if ships_from:
        checks["卖家信息"] = (checks["卖家信息"][0], checks["卖家信息"][1] + f" | Ships from: {ships_from}")

    # 4. 购物车状态
    cart = data.get("cart", {})
    has_cart = cart.get("add_to_cart", False)
    has_buy = cart.get("buy_now", False)
    if has_cart and has_buy:
        checks["购物车状态"] = (PASS, "Add to Cart ✅ / Buy Now ✅")
    elif has_cart:
        checks["购物车状态"] = (WARN, "Add to Cart ✅ / Buy Now ❌")
    elif cart.get("see_all_buying_options"):
        checks["购物车状态"] = (FAIL, "仅显示 See All Buying Options，无 Buy Box")
    else:
        checks["购物车状态"] = (FAIL, "无购买按钮")

    # 5. 配送信息
    delivery = data.get("delivery", {})
    d_text = delivery.get("text", "")
    d_prime = delivery.get("prime", False)
    if d_text:
        prime_str = " · Prime ✅" if d_prime else ""
        checks["配送信息"] = (PASS, d_text[:100] + prime_str)
    elif d_prime:
        checks["配送信息"] = (WARN, "配送文本未获取到，Prime 标识存在")
    else:
        checks["配送信息"] = (FAIL, "无配送信息")

    # 6. 类目与节点
    cat = data.get("category", {})
    breadcrumb = cat.get("breadcrumb", "")
    dept = cat.get("search_department", "")
    if breadcrumb:
        checks["类目与节点"] = (PASS, breadcrumb)
    elif dept:
        checks["类目与节点"] = (WARN, f"大类: {dept}，面包屑未获取")
    else:
        checks["类目与节点"] = (WARN, "类目信息未获取")

    # 7. BSR 排名
    bsr = data.get("bsr", [])
    if bsr:
        bsr_parts = []
        for entry in bsr:
            cat_name = clean_bsr_category(entry.get("category", ""))
            bsr_parts.append(f"#{entry['rank']:,} {cat_name}")
        checks["BSR 排名"] = (PASS, " · ".join(bsr_parts))
    else:
        checks["BSR 排名"] = (FAIL, "无 BSR 排名数据")

    # 8. 差评监控
    ratings = data.get("ratings", {})
    reviews = data.get("reviews_on_page", [])
    neg_reviews = [r for r in reviews if r.get("is_negative", False)]
    neg_count = len(neg_reviews)
    score_str = f"{ratings.get('score', '?')}⭐ ({ratings.get('count', '?'):,}条)" if ratings.get("score") else "未获取"
    if neg_count == 0:
        checks["差评监控"] = (PASS, f"{score_str} · 首页差评: 0 条")
    elif neg_count <= 2:
        checks["差评监控"] = (WARN, f"{score_str} · 首页差评: {neg_count} 条")
    else:
        checks["差评监控"] = (FAIL, f"{score_str} · 首页差评: {neg_count} 条")

    return checks


# ── 搜索可见性判断 ────────────────────────────────────────

def evaluate_search(search_data: dict, asin: str) -> tuple:
    """从搜索结果数据中判断指定 ASIN 的可见性"""
    if search_data.get("captcha"):
        return (FAIL, "搜索页被验证码拦截")

    # 在 first_page_results 中查找 ASIN
    for item in search_data.get("first_page_results", []):
        if item.get("asin", "").upper() == asin.upper():
            pos = item["position"]
            typ = item["type"]
            if typ == "organic":
                return (PASS, f"自然位 #{pos}")
            else:
                return (WARN, f"广告位 #{pos}（自然位未找到）")

    return (FAIL, "首页未找到")


# ── 历史对比 ──────────────────────────────────────────────


def find_latest_report(output_dir: str, asins: list[str]) -> Optional[str]:
    """在 output_dir 中找同批 ASIN 的最近一次报告（跳过今天的）"""
    pattern = os.path.join(output_dir, "*健康检查报告.md")
    files = sorted(glob.glob(pattern), reverse=True)
    today = datetime.now().strftime("%Y-%m-%d")
    for f in files:
        if os.path.basename(f).startswith(today):
            continue
        try:
            with open(f, "r", encoding="utf-8") as fh:
                content = fh.read(8000)
            if any(asin in content for asin in asins):
                return f
        except Exception:
            continue
    return None


def extract_history_metrics(filepath: str, asins: list[str]) -> dict:
    """从历史报告中提取关键指标，用于对比"""
    metrics = {"date": "", "asins": {}}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 报告日期
        date_m = re.search(r"created:\s*(\d{4}-\d{2}-\d{2})", content)
        metrics["date"] = date_m.group(1) if date_m else os.path.basename(filepath)[:10]

        # 按 ASIN 段落提取指标
        for asin in asins:
            asin_metrics = {}

            # 找到 ASIN 对应的段落（从 "### ASIN N: BXXXXXXXXX" 到下一个 "### ASIN" 或 "## "）
            pattern = re.compile(
                rf"###\s+ASIN\s+\d+:\s+{re.escape(asin)}(.*?)(?=###\s+ASIN\s+\d+:|##\s+[^#]|\Z)",
                re.DOTALL,
            )
            m = pattern.search(content)
            if not m:
                metrics["asins"][asin] = asin_metrics
                continue

            section = m.group(1)

            # BSR 排名: "#数字 类目名" 或 "#数字,数字 类目名"
            bsr_matches = re.findall(r"#([\d,]+)\s+(.+?)(?:\s+·|\s*\||\s*$)", section)
            if bsr_matches:
                asin_metrics["bsr"] = [
                    {"rank": int(r.replace(",", "")), "category": c.strip()}
                    for r, c in bsr_matches
                ]

            # 评分和评论数: "4.5⭐ (1,234条)"
            rating_m = re.search(r"([\d.]+)⭐\s*\(([\d,]+)条\)", section)
            if rating_m:
                asin_metrics["score"] = float(rating_m.group(1))
                asin_metrics["review_count"] = int(rating_m.group(2).replace(",", ""))

            # 搜索排名: "自然位 #N" 或 "广告位 #N"
            search_matches = re.findall(r"(?:自然位|广告位)\s+#(\d+)", section)
            if search_matches:
                asin_metrics["search_positions"] = [int(p) for p in search_matches]

            metrics["asins"][asin] = asin_metrics

    except Exception:
        pass
    return metrics


def format_history_comparison(
    current_data: list[dict],
    current_checks: list[dict],
    current_search: dict,
    history: dict,
    history_file: str,
) -> list[str]:
    """生成历史对比的 Markdown 段落"""
    lines = []
    lines.append("## 历史对比")
    lines.append("")
    lines.append(f"> 对比基准: {history['date']} 的报告（`{os.path.basename(history_file)}`）")
    lines.append("")

    has_content = False

    for data in current_data:
        asin = data["asin"]
        h = history.get("asins", {}).get(asin, {})
        if not h:
            continue

        asin_lines = []

        # BSR 对比
        h_bsr = h.get("bsr", [])
        c_bsr = data.get("bsr", [])
        if h_bsr and c_bsr:
            for hb in h_bsr:
                # 找当前同类目的 BSR
                match = next(
                    (cb for cb in c_bsr if hb["category"] in clean_bsr_category(cb.get("category", ""))),
                    None,
                )
                if match:
                    diff = match["rank"] - hb["rank"]
                    if diff < 0:
                        arrow = f"↑ 上升 {abs(diff)} 位"
                    elif diff > 0:
                        arrow = f"↓ 下降 {diff} 位"
                    else:
                        arrow = "→ 持平"
                    cat_name = clean_bsr_category(hb["category"])
                    asin_lines.append(f"  - BSR {cat_name}: #{hb['rank']:,} → #{match['rank']:,}（{arrow}）")

        # 评论数对比
        h_reviews = h.get("review_count")
        c_reviews = data.get("ratings", {}).get("count")
        if h_reviews and c_reviews:
            diff = c_reviews - h_reviews
            asin_lines.append(f"  - 评论数: {h_reviews:,} → {c_reviews:,}（{'+' if diff >= 0 else ''}{diff:,}）")

        # 搜索排名对比
        h_positions = h.get("search_positions", [])
        if h_positions and current_search:
            # 取当前搜索排名
            for kw, asin_results in current_search.items():
                if asin in asin_results:
                    c_status, c_detail = asin_results[asin]
                    c_pos_m = re.search(r"#(\d+)", c_detail)
                    if c_pos_m and h_positions:
                        c_pos = int(c_pos_m.group(1))
                        h_pos = h_positions[0]
                        diff = c_pos - h_pos
                        if diff < 0:
                            arrow = f"↑ 上升 {abs(diff)} 位"
                        elif diff > 0:
                            arrow = f"↓ 下降 {diff} 位"
                        else:
                            arrow = "→ 持平"
                        asin_lines.append(f"  - 搜索「{kw}」排名: #{h_pos} → #{c_pos}（{arrow}）")
                    break

        if asin_lines:
            has_content = True
            lines.append(f"**{asin}**:")
            lines.extend(asin_lines)
            lines.append("")

    if not has_content:
        lines.append("历史报告中未找到可对比的指标。")
        lines.append("")

    lines.append("---")
    lines.append("")
    return lines


# ── 报告生成 ──────────────────────────────────────────────

def generate_report(
    all_product_data: list[dict],
    all_checks: list[dict],
    search_results: dict,  # {keyword: {asin: (status, detail)}}
    site_code: str,
    zip_code: str,
    seller: str,
    keywords: list[str],
    now: datetime,
    history: Optional[dict] = None,
    history_file: Optional[str] = None,
) -> str:
    """生成完整的 Markdown 健康检查报告"""

    lines = []

    # ── 元数据 ──
    time_str = now.strftime("%Y-%m-%d %H:%M")
    date_str = now.strftime("%Y-%m-%d")
    domain = get_site_config(site_code)["domain"]
    kw_str = ", ".join(keywords) if keywords else "无"

    lines.append("---")
    lines.append(f"created: {time_str}")
    lines.append(f"topic: {seller or 'ASIN'} Listing 健康检查")
    lines.append("type: 健康检查报告")
    lines.append("data_sources: 亚马逊官网页面抓取（curl + BeautifulSoup）")
    lines.append("---")
    lines.append("")

    # ── 标题 ──
    if len(all_product_data) == 1:
        lines.append(f"# {all_product_data[0]['asin']} Listing 健康检查报告")
    else:
        lines.append(f"# {seller or 'Batch'} Listing 批量健康检查报告")
    lines.append("")
    lines.append(f"> 检查时间：{time_str}")
    lines.append(f"> 站点：{site_code} ({domain}) | 邮编：{zip_code}")
    if seller:
        lines.append(f"> 卖家：{seller} | 关键词：{kw_str}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── 总体评估 ──
    total_pass = 0
    total_warn = 0
    total_fail = 0
    for checks in all_checks:
        for _, (status, _) in checks.items():
            if status == PASS:
                total_pass += 1
            elif status == WARN:
                total_warn += 1
            else:
                total_fail += 1
    # 搜索可见性计入（搜索不可见可能是正常的变体行为，降级为 warn 计入总评）
    for kw, asin_results in search_results.items():
        for asin, (status, _) in asin_results.items():
            if status == PASS:
                total_pass += 1
            else:
                # 搜索 FAIL 和 WARN 都按 warn 计入总评（不拉高严重度）
                total_warn += 1

    if total_fail > 0:
        overall = FAIL
    elif total_warn > 0:
        overall = WARN
    else:
        overall = PASS

    overall_desc = {
        PASS: "所有检查项均正常",
        WARN: f"有 {total_warn} 项需关注，无异常",
        FAIL: f"有 {total_fail} 项异常，需处理",
    }

    lines.append("## 总体评估")
    lines.append("")
    lines.append("| 状态 | 说明 |")
    lines.append("|------|------|")
    lines.append(f"| {OVERALL_ICON[overall]} | {overall_desc[overall]} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── 汇总一览表（多 ASIN 时） ──
    if len(all_product_data) > 1:
        lines.append("## 汇总一览")
        lines.append("")
        lines.append("| ASIN | 产品 | 价格 | 卖家 | 购物车 | BSR 大类 | BSR 子类 | 评分 | 首页差评 | 搜索 |")
        lines.append("|------|------|------|------|--------|----------|----------|------|----------|------|")

        for data, checks in zip(all_product_data, all_checks):
            asin = data["asin"]
            title_short = data.get("title", "")[:40] + ("..." if len(data.get("title", "")) > 40 else "")
            price_str = checks.get("价格与优惠", (PASS, ""))[1][:40]
            seller_icon = STATUS_ICON[checks.get("卖家信息", (PASS, ""))[0]]
            seller_name = data.get("seller", {}).get("sold_by", "?")
            cart_icon = STATUS_ICON[checks.get("购物车状态", (FAIL, ""))[0]]

            bsr_list = data.get("bsr", [])
            bsr_main = f"#{bsr_list[0]['rank']:,}" if bsr_list else "—"
            bsr_sub = ""
            if len(bsr_list) > 1:
                cat_name = clean_bsr_category(bsr_list[1].get("category", ""))
                bsr_sub = f"#{bsr_list[1]['rank']:,} {cat_name}"

            ratings = data.get("ratings", {})
            rating_str = f"{ratings.get('score', '?')}⭐ ({ratings.get('count', '?'):,})" if ratings.get("score") else "—"

            neg_count = len([r for r in data.get("reviews_on_page", []) if r.get("is_negative")])
            neg_str = f"{neg_count} {STATUS_ICON[PASS if neg_count == 0 else (WARN if neg_count <= 2 else FAIL)]}"

            # 搜索
            search_str = "—"
            for kw, asin_results in search_results.items():
                if asin in asin_results:
                    s_status, s_detail = asin_results[asin]
                    search_str = f"{s_detail} {STATUS_ICON[s_status]}" if s_status != FAIL else f"{STATUS_ICON[FAIL]} 未找到"
                    break

            lines.append(f"| {asin} | {title_short} | {price_str} | {seller_name} {seller_icon} | {cart_icon} | {bsr_main} | {bsr_sub} | {rating_str} | {neg_str} | {search_str} |")

        lines.append("")
        lines.append("---")
        lines.append("")

    # ── 逐项检查详情 ──
    lines.append("## 逐项检查详情")
    lines.append("")

    for i, (data, checks) in enumerate(zip(all_product_data, all_checks)):
        asin = data["asin"]
        title = data.get("title", "未知")

        lines.append(f"### ASIN {i+1}: {asin}")
        lines.append("")
        lines.append(f"**标题**：{title}")
        lines.append("")
        lines.append("| 检查项 | 状态 | 详情 |")
        lines.append("|--------|------|------|")

        for check_name in ["页面可访问性", "价格与优惠", "卖家信息", "购物车状态", "配送信息", "类目与节点", "BSR 排名", "差评监控"]:
            if check_name in checks:
                status, detail = checks[check_name]
                lines.append(f"| {check_name} | {STATUS_ICON[status]} | {detail} |")

        # 搜索可见性
        for kw, asin_results in search_results.items():
            if asin in asin_results:
                s_status, s_detail = asin_results[asin]
                lines.append(f"| 搜索可见性 | {STATUS_ICON[s_status]} | \"{kw}\" → {s_detail} |")

        # 库存
        stock = data.get("stock", {})
        if stock.get("in_stock"):
            lines.append(f"| 库存 | ✅ | {stock.get('text', 'In Stock')} |")
        elif stock.get("text"):
            lines.append(f"| 库存 | ❌ | {stock['text']} |")

        lines.append("")
        lines.append("---")
        lines.append("")

    # ── 搜索可见性详情 ──
    if search_results:
        lines.append("## 搜索可见性详情")
        lines.append("")
        for kw, asin_results in search_results.items():
            lines.append(f"**关键词**：{kw} | **搜索范围**：All Departments")
            lines.append("")
            lines.append("| ASIN | 是否找到 | 位置 | 类型 |")
            lines.append("|------|----------|------|------|")
            for asin in [d["asin"] for d in all_product_data]:
                if asin in asin_results:
                    s_status, s_detail = asin_results[asin]
                    if s_status == FAIL:
                        lines.append(f"| {asin} | ❌ 否 | — | — |")
                    else:
                        # 解析 "自然位 #2" 或 "广告位 #5"
                        typ = "自然位 (Organic)" if "自然" in s_detail else "广告位 (Sponsored)"
                        pos = s_detail
                        lines.append(f"| {asin} | ✅ 是 | {pos} | {typ} |")
            lines.append("")
        lines.append("---")
        lines.append("")

    # ── 历史对比 ──
    if history and history.get("date"):
        history_lines = format_history_comparison(
            current_data=all_product_data,
            current_checks=all_checks,
            current_search=search_results,
            history=history,
            history_file=history_file,
        )
        lines.extend(history_lines)

    # ── 问题清单 ──
    problems = []
    for i, (data, checks) in enumerate(zip(all_product_data, all_checks)):
        asin = data["asin"]
        for name, (status, detail) in checks.items():
            if status == FAIL:
                problems.append(("🔴 高", asin, name, detail))
            elif status == WARN:
                problems.append(("🟡 低", asin, name, detail))
    for kw, asin_results in search_results.items():
        for asin, (status, detail) in asin_results.items():
            if status == FAIL:
                problems.append(("🟡 低", asin, f"搜索「{kw}」", detail))

    lines.append("## 问题清单与建议")
    lines.append("")
    if problems:
        lines.append("| 优先级 | ASIN | 问题 | 详情 |")
        lines.append("|--------|------|------|------|")
        for priority, asin, name, detail in problems:
            lines.append(f"| {priority} | {asin} | {name} | {detail} |")
    else:
        lines.append("无异常或需关注项。")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── 数据说明 ──
    lines.append("## 数据说明")
    lines.append("")
    lines.append(f"- 本报告所有数据来自 {time_str} 抓取的亚马逊前台页面快照（curl + BeautifulSoup）")
    lines.append("- 价格、排名、评分等数据实时波动，仅代表检查时刻状态")
    lines.append("- 搜索结果受地域、用户画像等因素影响")
    lines.append("- 差评趋势：需与历史报告对比")
    lines.append("")

    return "\n".join(lines)


# ── 主流程 ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Amazon Listing 健康检查（独立运行，不依赖 Claude Code）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 run_health_check.py --asins B0PUBLIC01,B0PUBLIC02 --seller YourBrand --keywords "karaoke machine"
  python3 run_health_check.py --asins B0PUBLIC01
        """,
    )
    parser.add_argument("--asins", required=True, help="ASIN 列表，逗号分隔")
    parser.add_argument("--site", default="US", help="站点代码（默认 US）")
    parser.add_argument("--seller", default="", help="期望卖家名称（用于 Sold By 校验）")
    parser.add_argument("--keywords", default="", help="核心关键词，逗号分隔（用于搜索可见性检查）")
    parser.add_argument("--output-dir", default=".", help="报告输出目录（默认当前目录）")
    args = parser.parse_args()

    asins = [a.strip() for a in args.asins.split(",") if a.strip()]
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else []
    site_code = args.site.upper()
    seller = args.seller
    output_dir = args.output_dir

    if not asins:
        print("错误：至少需要一个 ASIN", file=sys.stderr)
        sys.exit(1)

    site_config = get_site_config(site_code)
    domain = site_config["domain"]
    zip_code = site_config["zip"]
    now = datetime.now()

    print(f"🔍 Listing 健康检查")
    print(f"   站点: {site_code} ({domain}) | 邮编: {zip_code}")
    print(f"   ASIN: {', '.join(asins)}")
    if seller:
        print(f"   卖家: {seller}")
    if keywords:
        print(f"   关键词: {', '.join(keywords)}")
    print()

    # ── Step 1: 逐 ASIN 抓取商品页 ──
    all_product_data = []
    all_checks = []

    for i, asin in enumerate(asins):
        if i > 0:
            throttle(1.5, 3.0)

        print(f"  [{i+1}/{len(asins)}] 抓取 {asin} ...", end=" ", flush=True)
        url = f"https://www.{domain}/dp/{asin}"
        html = fetch_page(url)
        data = extract_product_data(html, asin, site_code, domain)
        data["zip_code"] = zip_code

        checks = evaluate_product(data, seller if seller else None)
        all_product_data.append(data)
        all_checks.append(checks)

        # 简要输出
        status = data["page_status"]
        if status == "ok":
            fail_items = [name for name, (s, _) in checks.items() if s == FAIL]
            if fail_items:
                print(f"⚠️  异常项: {', '.join(fail_items)}")
            else:
                print("✅")
        else:
            print(f"❌ {status}")

    # ── Step 2: 搜索可见性检查 ──
    search_results = {}  # {keyword: {asin: (status, detail)}}

    for kw in keywords:
        throttle(1.5, 3.0)
        print(f"  🔎 搜索 \"{kw}\" ...", end=" ", flush=True)

        encoded_kw = urllib.parse.quote_plus(kw)
        url = f"https://www.{domain}/s?k={encoded_kw}"
        html = fetch_page(url)
        raw_search = extract_search_results(html, asins[0])  # target_asin 不影响全量解析

        asin_results = {}
        for asin in asins:
            asin_results[asin] = evaluate_search(raw_search, asin)

        search_results[kw] = asin_results

        found = [a for a, (s, _) in asin_results.items() if s != FAIL]
        print(f"找到 {len(found)}/{len(asins)} 个 ASIN")

    print()

    # ── Step 3: 历史对比 ──
    history = None
    history_file = None
    prev_report = find_latest_report(output_dir, asins)
    if prev_report:
        history_file = prev_report
        history = extract_history_metrics(prev_report, asins)
        print(f"  📊 找到历史报告: {os.path.basename(prev_report)}（{history.get('date', '?')}）")
        print()

    # ── Step 4: 生成报告 ──
    report = generate_report(
        all_product_data=all_product_data,
        all_checks=all_checks,
        search_results=search_results,
        site_code=site_code,
        zip_code=zip_code,
        seller=seller,
        keywords=keywords,
        now=now,
        history=history,
        history_file=history_file,
    )

    # ── Step 5: 保存文件 ──
    os.makedirs(output_dir, exist_ok=True)
    date_str = now.strftime("%Y-%m-%d")
    name_part = seller if seller else asins[0]
    if len(asins) > 1 and seller:
        filename = f"{date_str}_{name_part}_{len(asins)}ASIN_健康检查报告.md"
    else:
        filename = f"{date_str}_{name_part}_健康检查报告.md"

    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)

    # ── Step 6: 终端摘要 ──
    # 统计
    total_checks = sum(len(c) for c in all_checks) + sum(
        len(ar) for ar in search_results.values()
    )
    fail_count = sum(
        1 for c in all_checks for _, (s, _) in c.items() if s == FAIL
    )
    warn_count = sum(
        1 for c in all_checks for _, (s, _) in c.items() if s == WARN
    ) + sum(
        1 for ar in search_results.values() for _, (s, _) in ar.items() if s != PASS
    )
    pass_count = total_checks - fail_count - warn_count

    if fail_count > 0:
        icon = "🔴"
    elif warn_count > 0:
        icon = "🟡"
    else:
        icon = "🟢"

    print(f"{icon} 检查完成：通过 {pass_count} / 需关注 {warn_count} / 异常 {fail_count}")
    print(f"📄 报告已保存: {filepath}")


if __name__ == "__main__":
    main()
