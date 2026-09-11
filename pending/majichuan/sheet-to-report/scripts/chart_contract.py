"""Versioned chart validation and device-independent evidence projection."""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from math import fsum, isclose, isfinite

VERSION = "chart-spec/1"
KINDS = {"line", "bar", "column", "grouped", "paired", "stacked", "donut", "scatter", "waterfall", "histogram"}
TASK_KINDS = {
    "trend": {"line", "column", "grouped", "paired"},
    "comparison": {"bar", "column", "grouped", "paired", "line"},
    "composition": {"stacked", "donut", "bar", "column", "grouped"},
    "distribution": {"histogram", "line", "bar", "column"},
    "relationship": {"scatter", "paired"},
    "contribution": {"waterfall", "bar", "column", "grouped"},
}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _number(value):
    return type(value) in (int, float) and isfinite(value)


def _close(a, b):
    return isclose(a, b, rel_tol=1e-9, abs_tol=1e-6)


def _keys(chart):
    if chart["kind"] in {"grouped", "stacked"}:
        return chart["series"]
    return [chart["y"]] + ([chart["y2"]] if chart["kind"] == "paired" else [])


def _scale(chart):
    return chart.get("x_scale", "linear" if chart["kind"] == "scatter" else "category")


def _order(chart):
    return chart.get("order", "source" if chart["kind"] in {"line", "waterfall", "histogram", "scatter"} else "descending")


def _time_value(value, frequency):
    _require(isinstance(value, str), "时间标签必须是 ISO 字符串")
    try:
        if frequency == "month":
            _require(len(value) == 7, "月份必须使用 YYYY-MM")
            result = date.fromisoformat(value + "-01")
        else:
            result = date.fromisoformat(value)
            _require(result.isoformat() == value, "日期必须使用 YYYY-MM-DD")
        return result
    except (ValueError, TypeError) as exc:
        raise ValueError("无效 ISO 时间值") from exc


def _next_date(value, frequency):
    if frequency == "month":
        return date(value.year + (value.month == 12), value.month % 12 + 1, 1)
    return value + timedelta(days=7 if frequency == "week" else 1)


def validate_chart(chart, record):
    required = {"version", "id", "task", "reason", "constraints", "evidence_id", "kind", "x", "y", "title", "limit"}
    optional = {"series", "y2", "x_scale", "order", "emphasis", "highlight", "label"}
    _require(isinstance(chart, dict) and required <= set(chart) and not set(chart) - required - optional, "图表字段不符合 chart-spec/1")
    _require(chart["version"] == VERSION, "不支持的图表合同版本")
    for key in ("id", "task", "reason", "evidence_id", "kind", "x", "y"):
        _require(isinstance(chart[key], str) and bool(chart[key].strip()), "图表标识、任务和理由必须非空")
    kind, x, y = chart["kind"], chart["x"], chart["y"]
    _require(kind in KINDS and kind in TASK_KINDS.get(chart["task"], set()), "任务与图型不匹配")
    _require(isinstance(chart["title"], list) and bool(chart["title"]), "标题必须使用证据文本片段")
    _require(isinstance(chart["constraints"], list) and all(isinstance(s, str) and s.strip() for s in chart["constraints"]), "约束必须是字符串数组")
    _require(type(chart["limit"]) is int and 1 <= chart["limit"] <= 500, "limit 必须为 1 至 500 整数")
    scale, order = _scale(chart), _order(chart)
    _require(scale in {"category", "time", "linear"} and order in {"source", "descending", "absolute"}, "坐标尺度或排序不合法")
    _require(chart.get("emphasis", "supporting") in {"primary", "supporting"}, "图表层级不合法")
    _require((kind == "paired") == ("y2" in chart), "仅 paired 必须提供 y2")
    _require((kind in {"grouped", "stacked"}) == ("series" in chart), "仅 grouped/stacked 必须提供 series")
    if "series" in chart:
        _require(isinstance(chart["series"], list) and 2 <= len(chart["series"]) <= 6 and chart["series"][0] == y, "series 必须为 2 至 6 列且以 y 开始")
    _require("label" not in chart or kind == "scatter", "label 仅供散点对象标识")
    _require(scale != "linear" or kind in {"line", "scatter"}, "数值横轴仅用于线图和散点")
    _require(kind != "scatter" or scale == "linear", "散点必须使用数值横轴")
    _require(scale != "time" or kind in {"line", "column", "grouped", "paired"}, "此图型不支持时间横轴")
    _require(scale == "category" or order == "source", "时间与数值横轴不能按数值排名重排")
    _require(kind not in {"waterfall", "histogram"} or order == "source", "贡献步骤和箱边界不可重排")
    _require(isinstance(record, dict) and isinstance(record.get("columns"), dict) and isinstance(record.get("rows"), list) and bool(record["rows"]), "图表证据为空或非法")
    columns, rows = record["columns"], record["rows"]
    series = _keys(chart)
    keys = [x, *series] + ([chart["label"]] if "label" in chart else [])
    _require(all(isinstance(k, str) and k in columns for k in keys) and len(set(keys)) == len(keys), "列不存在或重复")
    for key in keys:
        _require(isinstance(columns[key].get("label"), str) and isinstance(columns[key].get("unit"), str), "列缺少名称或单位")
    if kind in {"grouped", "stacked"}:
        _require(len({columns[k]["unit"] for k in series}) == 1, "同轴系列单位必须一致")
        if columns[y]["unit"] == "%":
            _require(all(isinstance(columns[k].get("denominator"), str) and columns[k]["denominator"] for k in series), "比例系列必须声明分母")
    if chart["task"] == "contribution":
        _require(all(columns[k].get("additive") is True for k in series), "贡献只能使用可加总指标")
        _require(len(rows) <= chart["limit"], "贡献视图不得截掉尾部")
    labels = []
    numeric_x = []
    for row in rows:
        _require(isinstance(row, dict), "证据行必须是对象")
        value = row.get(chart.get("label", x))
        _require(type(value) in (str, int, float) and bool(str(value).strip()) and (type(value) is str or _number(value)), "对象标签无效")
        labels.append(str(value))
        for key in series:
            _require(_number(row.get(key)), "全部证据数值必须有限，不得忽略尾部缺失")
        if scale == "linear":
            _require(_number(row.get(x)), "数值横轴必须使用有限数值")
            numeric_x.append(row[x])
    if kind != "scatter" or "label" in chart:
        _require(len(set(labels)) == len(labels), "对象标签重复")
    if kind == "line" and scale == "linear":
        _require(all(a < b for a, b in zip(numeric_x, numeric_x[1:])), "数值横轴必须严格递增")
    highlight = chart.get("highlight", [])
    _require(isinstance(highlight, list) and all(isinstance(v, str) and v in labels for v in highlight) and len(set(highlight)) == len(highlight), "重点对象必须存在且不重复")
    if kind in {"line", "donut", "stacked", "waterfall", "histogram"}:
        _require(len(rows) <= chart["limit"], "此图型必须完整展示，不能截尾")
    readable_limit = {"bar": 30, "paired": 30, "column": 24, "grouped": 24, "stacked": 24, "waterfall": 24, "donut": 6, "histogram": 40}.get(kind, 500)
    _require(min(len(rows), chart["limit"]) <= readable_limit, "类别过多，需显式选择可读图型或计算聚合证据")
    semantics = record.get("chart_semantics", {})
    _require(isinstance(semantics, dict), "图形语义必须由计算端提供")
    if scale == "time":
        temporal = semantics.get("time", {})
        frequency = temporal.get("frequency")
        expected = temporal.get("expected_values")
        _require(frequency in {"day", "week", "month"} and isinstance(expected, list) and bool(expected), "时间图缺少完整周期域")
        domain = [_time_value(v, frequency) for v in expected]
        _require(all(_next_date(a, frequency) == b for a, b in zip(domain, domain[1:])), "预期时间域必须连续且有序")
        observed = [_time_value(r[x], frequency) for r in rows]
        _require(all(v in domain for v in observed) and all(a < b for a, b in zip(observed, observed[1:])), "实际时间必须有序且位于周期域内")
        _require(len(expected) <= chart["limit"], "时间域不可截尾")
    if kind == "donut":
        partition = semantics.get("partition", {})
        _require(partition.get("mutually_exclusive") is True and partition.get("complete") is True, "环形图需要完整互斥分组")
        _require(columns[y]["unit"] == "%" and isinstance(columns[y].get("denominator"), str) and bool(columns[y]["denominator"]), "环形图需要已计算的同分母百分比")
        _require(2 <= len(rows) <= 6 and all(r[y] >= 0 for r in rows) and _close(fsum(r[y] for r in rows), 100), "环形图必须为 2 至 6 个非负完整组成部分")
    if kind == "stacked":
        partition = semantics.get("series_partition", {})
        _require(partition.get("mutually_exclusive") is True and partition.get("complete") is True, "堆叠图需要同一行跨系列完整互斥")
        _require(all(columns[k].get("additive") is True for k in series), "堆叠系列必须可加总")
        _require(all(r[k] >= 0 for r in rows for k in series), "构成堆叠不能含负值")
        if columns[y]["unit"] == "%":
            _require(len({columns[k]["denominator"] for k in series}) == 1 and all(_close(fsum(r[k] for k in series), 100) for r in rows), "百分比堆叠必须同分母且逐行对账")
    if kind == "line" and "cumulative" in semantics:
        cumulative = semantics["cumulative"]
        _require(scale == "linear" and cumulative.get("x_key") == x and cumulative.get("y_key") == y and cumulative.get("total") == 100 and cumulative.get("order") == "descending", "累计曲线语义不匹配")
        _require(columns[x]["unit"] == columns[y]["unit"] == "%" and all(0 <= v <= 100 for v in numeric_x) and _close(numeric_x[-1], 100) and _close(rows[-1][y], 100), "累计曲线横轴与终点必须完整对账")
    if kind == "histogram":
        hist = semantics.get("histogram", {})
        lower, upper = hist.get("lower_key"), hist.get("upper_key")
        _require(lower in columns and upper in columns and lower != upper and hist.get("count_key") == y and type(hist.get("sample_count")) is int and hist["sample_count"] >= 0, "直方图缺少已计算分箱语义")
        _require(isinstance(columns[lower].get("unit"), str) and columns[lower]["unit"] == columns[upper].get("unit"), "分箱边界单位必须一致")
        _require(all(_number(r.get(lower)) and _number(r.get(upper)) and r[lower] < r[upper] and type(r[y]) is int and r[y] >= 0 for r in rows), "箱边界或计数无效")
        _require(all(_close(a[upper], b[lower]) for a, b in zip(rows, rows[1:])) and sum(r[y] for r in rows) == hist["sample_count"], "箱边界有空隙/重叠或样本数不对账")
        _require(all(_close(r[upper] - r[lower], rows[0][upper] - rows[0][lower]) for r in rows), "计数直方图要求等宽箱，不等宽需要另行计算密度证据")
    if kind == "waterfall":
        waterfall = semantics.get("waterfall", {})
        role, base, end = (waterfall.get(k) for k in ("role_key", "base_key", "end_key"))
        _require(all(k in columns for k in (role, base, end)) and columns[y].get("additive") is True and len(rows) >= 3, "瀑布图缺少可加总贡献与已计算坐标")
        _require([r.get(role) for r in rows] == ["start", *(["delta"] * (len(rows) - 2)), "end"], "瀑布图必须首尾总计、中间贡献")
        _require(all(_number(r.get(base)) and _number(r.get(end)) for r in rows), "瀑布图坐标必须有限")
        for index, row in enumerate(rows):
            if index in (0, len(rows) - 1):
                _require(_close(row[base], 0) and _close(row[end], row[y]), "总计必须从零到总额")
                if index:
                    _require(_close(row[y], rows[index - 1][end]), "终点与贡献不对账")
            else:
                _require(_close(row[base], rows[index - 1][end]) and _close(row[end], row[base] + row[y]), "贡献步骤不对账")


def project_chart(chart, record):
    """Validate before selecting any rows; never derive new business measures."""
    validate_chart(chart, record)
    kind, x, y, scale, order = chart["kind"], chart["x"], chart["y"], _scale(chart), _order(chart)
    rows = list(record["rows"])
    if order != "source":
        rows.sort(key=lambda r: abs(r[y]) if order == "absolute" else r[y], reverse=True)
    source_count = len(rows)
    rows = rows[:chart["limit"]]
    shown_count = len(rows)
    semantics, columns = record.get("chart_semantics", {}), record["columns"]
    labels = [str(r[chart.get("label", x)]) for r in rows]
    x_values = [r[x] if scale == "linear" else str(r[x]) for r in rows]
    gap_indices = []
    if scale == "time":
        temporal = semantics["time"]
        labels = temporal["expected_values"][:]
        lookup = {r[x]: r for r in rows}
        rows = [lookup.get(label) for label in labels]
        gap_indices = [i for i, row in enumerate(rows) if row is None]
        x_values = [int(datetime.combine(_time_value(label, temporal["frequency"]), datetime.min.time(), timezone.utc).timestamp() * 1000) for label in labels]
    series = [{"key": key, "label": columns[key]["label"], "unit": columns[key]["unit"],
               **({"denominator": columns[key]["denominator"]} if "denominator" in columns[key] else {}),
               "values": [r[key] if r is not None else None for r in rows]} for key in _keys(chart)]
    view = {key: deepcopy(chart[key]) for key in ("version", "id", "task", "kind", "title", "reason", "constraints", "evidence_id")}
    view.update({"scope": deepcopy(record.get("scope", {})), "labels": labels, "x_values": x_values, "series": series,
                 "source_count": source_count, "shown_count": shown_count, "omitted_count": source_count - shown_count,
                 "truncated": shown_count < source_count, "tail_note": f"展示 {shown_count} / {source_count} 个对象；其余 {source_count - shown_count} 个未展示" if shown_count < source_count else "",
                 "order": order, "emphasis": chart.get("emphasis", "supporting"), "highlight": chart.get("highlight", [])[:],
                 "highlight_indices": [i for i, label in enumerate(labels) if label in chart.get("highlight", [])],
                 "axes": {"x": {"key": x, "label": columns[x]["label"], "unit": columns[x]["unit"], "scale": scale},
                          "y": {"independent": kind == "paired"}, "zero_baseline": kind not in {"line", "scatter"}}})
    if scale == "time":
        view["gap_indices"] = gap_indices
    if kind == "line" and "cumulative" in semantics:
        values = series[0]["values"]
        signed = any(v < 0 or v > 100 for v in values) or any(a > b for a, b in zip(values, values[1:]))
        view.update(signed_cumulative=signed, warnings=["净贡献包含负值影响，累计曲线可能下降或超过百分之百"] if signed else [])
    if kind == "stacked":
        bases = [0] * len(rows)
        for item in series:
            item["bases"] = bases[:]
            item["ends"] = [a + b for a, b in zip(bases, item["values"])]
            bases = item["ends"]
    if kind == "waterfall":
        meta = semantics["waterfall"]
        view.update(roles=[r[meta["role_key"]] for r in rows], bases=[r[meta["base_key"]] for r in rows], ends=[r[meta["end_key"]] for r in rows])
    if kind == "histogram":
        meta = semantics["histogram"]
        view.update(bin_lower=[r[meta["lower_key"]] for r in rows], bin_upper=[r[meta["upper_key"]] for r in rows])
        view["axes"]["x"]["unit"] = columns[meta["lower_key"]]["unit"]
    return view
