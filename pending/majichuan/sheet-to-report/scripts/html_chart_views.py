"""Validated, deterministic chart projections. Evidence remains untouched."""
from __future__ import annotations

from math import fsum, isfinite


def validate_chart(chart, record):
    required = {"evidence_id", "kind", "x", "y", "title", "limit"}
    if not isinstance(chart, dict) or not required <= set(chart) or set(chart) - required - {"order", "y2", "emphasis"}:
        raise ValueError("图表字段不符合合同")
    if chart["kind"] not in {"line", "bar", "paired", "contribution"}:
        raise ValueError("不支持的图表类型")
    if type(chart["limit"]) is not int or not 1 <= chart["limit"] <= 24:
        raise ValueError("图表 limit 必须是一至二十四的整数")
    if chart.get("order", "source" if chart["kind"] == "line" else "descending") not in {"source", "descending", "absolute"}:
        raise ValueError("图表 order 非法")
    if chart.get("emphasis", "supporting") not in {"primary", "supporting"}:
        raise ValueError("图表 emphasis 非法")
    if (chart["kind"] == "paired") != ("y2" in chart):
        raise ValueError("paired 必须提供 y2，其他图不接受 y2")
    if not isinstance(chart["evidence_id"], str) or not chart["evidence_id"] or not isinstance(chart["title"], list) or not chart["title"]:
        raise ValueError("图表标题与证据标识非法")
    keys = [chart["x"], chart["y"]] + ([chart["y2"]] if "y2" in chart else [])
    if any(not isinstance(k, str) or k not in record["columns"] for k in keys) or len(set(keys)) != len(keys):
        raise ValueError("图表字段不存在或重复")
    for key in keys:
        meta = record["columns"][key]
        if not isinstance(meta.get("label"), str) or not isinstance(meta.get("unit"), str):
            raise ValueError("图表缺少字段名称或单位")
    if chart["kind"] == "contribution" and record["columns"][chart["y"]].get("additive") is not True:
        raise ValueError("贡献图只接受声明可加总的指标")
    if not isinstance(record["rows"], list) or not record["rows"]:
        raise ValueError("图表证据为空")
    labels = set()
    for row in record["rows"]:
        value = row.get(chart["x"])
        if type(value) not in (str, int, float) or (type(value) in (int, float) and not isfinite(value)) or not str(value).strip():
            raise ValueError("图表对象必须是有效标量")
        if str(value) in labels:
            raise ValueError("图表对象重复，需要确定性单系列证据")
        labels.add(str(value))
        for key in keys[1:]:
            if type(row.get(key)) not in (int, float) or not isfinite(row[key]):
                raise ValueError("图表数值必须有限，不得忽略缺失值")


def chart_series(chart, record):
    """Return labels, aligned series and optional reconciled contribution metadata."""
    validate_chart(chart, record)
    x, y = chart["x"], chart["y"]
    rows = list(record["rows"])
    if chart["kind"] == "contribution":
        positive = [r for r in rows if r[y] > 0]
        leader = max(positive or rows, key=lambda r: r[y] if positive else abs(r[y]))
        remainder = fsum(r[y] for r in rows if r is not leader)
        total = fsum(r[y] for r in rows)
        values = [leader[y], remainder, total]
        return {"labels": [str(leader[x]), "其余对象合计", "全部对象净变动"],
                "series": [{"key": y, **record["columns"][y], "values": values}],
                "roles": ["leader", "remainder", "total"], "source_count": len(rows),
                "reconciliation": {"leader": leader[y], "remainder": remainder, "total": total}}
    order = chart.get("order", "source" if chart["kind"] == "line" else "descending")
    if order != "source":
        rows.sort(key=lambda r: abs(r[y]) if order == "absolute" else r[y], reverse=True)
    rows = rows[:chart["limit"]]
    return {"labels": [str(r[x]) for r in rows], "source_count": len(record["rows"]),
            "series": [{"key": key, **record["columns"][key], "values": [r[key] for r in rows]}
                       for key in [y] + ([chart["y2"]] if "y2" in chart else [])]}
