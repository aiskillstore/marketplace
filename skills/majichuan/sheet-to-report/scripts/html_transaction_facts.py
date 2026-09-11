"""交易表的中性覆盖计算。无国家/商品值分支，无经营结论或行动模板。"""
from __future__ import annotations

import copy
import math
import re
import pandas as pd


def fields(contract):
    return {role: v if isinstance(v, str) else v["source_field"] for role, v in contract["field_mappings"].items()}


def nonblank(series):
    return series.notna() & series.astype(str).str.strip().ne("")


def fee_signal(name):
    """Auditable textual hints only; ambiguous words inside product names do not classify them."""
    if re.fullmatch(r"\s*(carriage|manual|adjust|adjustment|discount)\s*", name, re.I):
        return "独立费用或调整名称（待业务确认）"
    if re.search(r"\b(postage|fees?|charges?|commission|adjust|adjustment|discount)\b", name, re.I):
        return "明确费用或调整词（待业务确认）"
    if re.search(r"\b(next day|delivery|shipping|freight)\s+carriage\b", name, re.I):
        return "配送语境中的运费词（待业务确认）"
    return "未命中；不代表已确认实物商品"


def metrics(group, mapping):
    amount = pd.to_numeric(group[mapping["quantity"]]) * pd.to_numeric(group[mapping["unit_price"]])
    orders = int(group.loc[nonblank(group[mapping["order"]]), mapping["order"]].nunique())
    result = {"net": float(amount.sum()), "orders": orders,
              "units": float(pd.to_numeric(group[mapping["quantity"]]).sum()),
              "order_value": float(amount.sum()) / orders if orders else None}
    if "customer" in mapping:
        result["customers"] = int(group.loc[nonblank(group[mapping["customer"]]), mapping["customer"]].nunique())
    if "product" in mapping:
        result["products"] = int(group.loc[nonblank(group[mapping["product"]]), mapping["product"]].nunique())
    return result


def coverage(snapshot, raw, work, request, transaction):
    from html_analysis import add_evidence, scope
    mapping = fields(request.semantic_contract)
    money_unit = next((c["unit"] for c in snapshot["metrics"] if c["aggregation"] == "sum_product"), "金额单位待确认")
    cols = {"net": {"label": "净销售额", "unit": money_unit}, "orders": {"label": "交易单数", "unit": "单"},
            "customers": {"label": "可识别客户数", "unit": "人"}, "units": {"label": "净数量", "unit": "件"},
            "products": {"label": "条目覆盖数", "unit": "种"}, "order_value": {"label": "每交易单净金额", "unit": money_unit}}
    sc = scope(work, request)
    sc["denominator"] = "净销售额=数量×单价的带符号合计；交易单包含负向单据；每交易单净金额=净销售额÷去重交易单数；客户仅含可识别 ID；未自动剔除费用候选"
    totals = metrics(work, mapping)
    add_evidence(snapshot, "overview", [totals], "完整分析期基本盘", sc, {k: cols[k] for k in totals})
    periods = sorted(work["__period"].unique())
    timeline = [{"period": str(p), **metrics(g, mapping)} for p, g in work.groupby("__period", sort=True)]
    add_evidence(snapshot, "commerce_trend", timeline, "月度多指标对读", sc,
                 {"period": {"label": "周期", "unit": ""}, **{k: cols[k] for k in totals}})
    if len(timeline) > 1:
        previous, current = timeline[-2:]
        decomposition = [{"comparison": previous["period"]+" → "+current["period"],
            "net_change": current["net"]-previous["net"],
            "order_component": (current["orders"]-previous["orders"])*previous["order_value"],
            "value_component": current["orders"]*(current["order_value"]-previous["order_value"]),
            "net_pct": (current["net"]/previous["net"]-1)*100 if previous["net"] else None,
            "orders_pct": (current["orders"]/previous["orders"]-1)*100 if previous["orders"] else None,
            "value_pct": (current["order_value"]/previous["order_value"]-1)*100 if previous["order_value"] else None}]
        dcols = {"comparison": {"label": "比较期", "unit": ""}, "net_change": {"label": "净销售变化", "unit": money_unit},
                 "order_component": {"label": "交易单数量贡献", "unit": money_unit}, "value_component": {"label": "单均金额贡献", "unit": money_unit},
                 **{k: {"label": label, "unit": "%"} for k, label in [("net_pct", "净销售变动"), ("orders_pct", "交易单变动"), ("value_pct", "单均金额变动")]}}
        dscope = {**sc, "periods": [previous["period"], current["period"]],
                  "denominator": "顺序数学分解：单数贡献=(本期单数−前期单数)×前期单均；单均贡献=本期单数×(本期单均−前期单均)。交互项归单均；不是因果。"}
        add_evidence(snapshot, "period_decomposition", decomposition, "最新完整期的规模与单均变化分解", dscope, dcols, "decomposition")
        add_evidence(snapshot, "period_components", [{"component": dcols[k]["label"], "amount": decomposition[0][k]} for k in ["order_component", "value_component"]],
                     "净销售变动的数学组成", dscope, {"component": {"label": "组成", "unit": ""}, "amount": {"label": "贡献金额", "unit": money_unit}}, "decomposition")
    for role in ["geography", "product"]:
        if role not in mapping:
            continue
        dimension = mapping[role]
        object_rows = []
        for value, group in work.groupby(dimension, dropna=False, sort=False):
            row = {"object": str(value) if pd.notna(value) else "未填写", **metrics(group, mapping)}
            row["share"] = row["net"] / totals["net"] * 100 if totals["net"] else None
            if role == "product":
                row["code"] = row["object"]
                display = request.semantic_contract["field_mappings"]["product"].get("display_field")
                if not display:
                    display = (request.semantic_contract.get("display_bindings", {}).get("product") or {}).get("display_field")
                if display and display in group:
                    labels = group.loc[nonblank(group[display]), display].astype(str)
                    row["object"] = str(labels.mode().iloc[0]) if len(labels) else "未命名条目"
                row["unit_realization"] = row["net"] / row["units"] if row["units"] else None
                # An explicit, visible textual candidate screen; never a cleaning rule.
                row["classification_basis"] = fee_signal(row["object"])
                row["classification"] = "未命中费用文字线索" if row["classification_basis"].startswith("未命中") else "待确认费用/调整候选"
            object_rows.append(row)
        object_rows.sort(key=lambda r: (-r["net"], r["object"]))
        if role == "product":
            duplicates = pd.Series([r["object"] for r in object_rows]).value_counts()
            for row in object_rows:
                if duplicates[row["object"]] > 1:
                    row["object"] += " · " + row["code"]
        ocols = {"object": {"label": "地域" if role == "geography" else "条目名称", "unit": ""},
                 **{k: cols[k] for k in totals}, "share": {"label": "占全期净销售", "unit": "%"}}
        if role == "product":
            ocols.update(code={"label": "条目编码", "unit": ""}, classification={"label": "文字线索分类（未确认）", "unit": ""},
                         classification_basis={"label": "文字线索依据", "unit": ""},
                         unit_realization={"label": "净销售额/净数量", "unit": money_unit})
        add_evidence(snapshot, role+"_totals", object_rows, "地域规模与效率" if role == "geography" else "全部条目的金额与数量对读", sc, ocols)
        if role == "product":
            regular = [r for r in object_rows if r["classification"] == "未命中费用文字线索"]
            pending = [r for r in object_rows if r["classification"] != "未命中费用文字线索"]
            regular_scope = {**sc, "denominator": "未命中费用文字线索的条目视图；不是已确认商品清洗结果。占比仍以全体净销售为分母；费用候选另列，总额未剔除。"}
            add_evidence(snapshot, "product_view", regular, "未命中费用文字线索的条目排名", regular_scope, ocols)
            add_evidence(snapshot, "pending_items", pending, "待确认费用/调整条目（仍计入总额）", sc, ocols)
        # The full period-by-object table is deliberately a dynamic query, not basic coverage.
    if "customer" in mapping:
        customer_facts(snapshot, work, mapping, money_unit, sc)
    quality_facts(snapshot, raw, work, request, mapping, money_unit, sc)
    snapshot["initial_scan"]["declared_coverage"] += ["transaction_multimetric", "period_scale_value", "entity_distribution", "purchase_frequency", "quality_reconciliation"]


def customer_facts(snapshot, work, mapping, unit, sc):
    from html_analysis import add_evidence
    known = work[nonblank(work[mapping["customer"]])].copy()
    known["amount"] = pd.to_numeric(known[mapping["quantity"]])*pd.to_numeric(known[mapping["unit_price"]])
    amounts = known.groupby(mapping["customer"])["amount"].sum().sort_values(ascending=False)
    purchases = known[(known["amount"] > 0) & (pd.to_numeric(known[mapping["quantity"]]) > 0)]
    frequency = purchases.groupby(mapping["customer"])[mapping["order"]].nunique()
    entities = pd.DataFrame({"net": amounts, "frequency": frequency}).fillna({"frequency": 0})
    count, total = len(entities), float(amounts.sum())
    cs = {**sc, "rows": len(known), "denominator": "仅可识别客户；消费为窗口内净销售，非 LTV；频次为正金额正数量的去重交易单，非完整留存；零次表示仅有非正向记录。"}
    from canonical_json import canonical_sha256
    cs["population_sha256"] = canonical_sha256(sorted(int(i) for i in known.index))
    curve = []
    for percent in [1, 5, 10, 20, 50, 100]:
        n = math.ceil(count*percent/100)
        value = float(amounts.head(n).sum())
        curve.append({"layer": f"净消费最高的约{percent}%客户", "people": n, "net": value, "share": value/total*100 if total else None})
    columns = {"layer": {"label": "客户组", "unit": ""}, "people": {"label": "客户数", "unit": "人"},
               "net": {"label": "窗口净销售", "unit": unit}, "share": {"label": "占可识别客户净销售", "unit": "%"}}
    add_evidence(snapshot, "customer_concentration", curve, "客户累计贡献（重叠累计组，不能相加）", cs, columns, "distribution")
    tiers = []
    for label, mask in [("仅非正向记录", entities.frequency == 0), ("一次正向购买", entities.frequency == 1),
                        ("两至四次正向购买", entities.frequency.between(2,4)), ("五次及以上正向购买", entities.frequency >= 5)]:
        part = entities[mask]
        tiers.append({"layer": label, "people": len(part), "net": float(part.net.sum()),
                      "share": float(part.net.sum())/total*100 if total else None})
    add_evidence(snapshot, "customer_frequency", tiers, "购买频次与收入贡献（互斥组）", cs, columns, "distribution")
    summary = [{"identified_net": total, "identified_people": count,
                "repeat_people": int((entities.frequency >= 2).sum()),
                "repeat_share": float(entities.loc[entities.frequency >= 2, "net"].sum())/total*100 if total else None,
                "identified_share": total/snapshot["evidence"]["overview"]["rows"][0]["net"]*100}]
    add_evidence(snapshot, "customer_summary", summary, "客户覆盖与窗口重复购买", cs,
                 {"identified_net": {"label": "可识别客户净销售", "unit": unit}, "identified_people": {"label": "可识别客户", "unit": "人"},
                  "repeat_people": {"label": "窗口内重复购买客户", "unit": "人"}, "repeat_share": {"label": "重复购买客户收入占比", "unit": "%"},
                  "identified_share": {"label": "可识别客户金额占全体净销售", "unit": "%"}})


def quality_facts(snapshot, raw, work, request, mapping, unit, sc):
    from html_analysis import add_evidence
    q = pd.to_numeric(work[mapping["quantity"]])
    p = pd.to_numeric(work[mapping["unit_price"]])
    amount = q*p
    masks = [("负数量（不自动认定退货）", q < 0), ("零单价", p == 0), ("负单价", p < 0)]
    if "customer" in mapping:
        masks.append(("缺少客户标识（仍保留销售）", ~nonblank(work[mapping["customer"]])))
    # Report observed nonnumeric prefixes, without declaring them cancellations.
    prefix = work[mapping["order"]].astype(str).str.extract(r"^([A-Za-z]+)", expand=False)
    masks.append(("交易单带字母前缀（状态待确认）", prefix.notna()))
    quality = [{"issue": label, "rows": int(mask.sum()), "net": float(amount[mask].sum()),
                "share": float(amount[mask].sum())/float(amount.sum())*100 if amount.sum() else None} for label, mask in masks]
    qs = {**sc, "denominator": "各质量条件可能重叠，行数和金额不能直接相加；缺失客户不等同收入损失；字母前缀只是可观察线索，不宣称已确认取消；异常价格尚无业务阈值。"}
    add_evidence(snapshot, "quality", quality, "完整分析期质量影响（条件可能重叠）", qs,
                 {"issue": {"label": "观察项", "unit": ""}, "rows": {"label": "影响记录", "unit": "行"},
                  "net": {"label": "带符号金额", "unit": unit}, "share": {"label": "占净销售", "unit": "%"}}, "quality")
    reconciliation = [{"part": "正金额合计", "net": float(amount[amount > 0].sum())},
                      {"part": "负金额合计", "net": float(amount[amount < 0].sum())},
                      {"part": "净销售额", "net": float(amount.sum())}]
    add_evidence(snapshot, "reconciliation", reconciliation, "完整分析期金额对账", sc,
                 {"part": {"label": "金额组成", "unit": ""}, "net": {"label": "金额", "unit": unit}}, "reconciliation")
    raw_amount = pd.to_numeric(raw[mapping["quantity"]], errors="coerce")*pd.to_numeric(raw[mapping["unit_price"]], errors="coerce")
    excluded = raw.loc[~raw.index.isin(work.index)]
    excluded_amount = raw_amount.loc[excluded.index]
    source_rows = [{"part": "原表全部记录", "rows": len(raw), "net": float(raw_amount.sum())},
                   {"part": "完整分析期保留", "rows": len(work), "net": float(amount.sum())},
                   {"part": "周期及已确认规则排除", "rows": len(excluded), "net": float(excluded_amount.sum())}]
    add_evidence(snapshot, "source_reconciliation", source_rows, "原表与分析期对账", {**sc, "denominator": "原表=完整分析期保留+周期/已确认规则排除；原表范围与正文分析期不同。"},
                 {"part": {"label": "范围", "unit": ""}, "rows": {"label": "记录数", "unit": "行"}, "net": {"label": "净金额", "unit": unit}}, "reconciliation")
