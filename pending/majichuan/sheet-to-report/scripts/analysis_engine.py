from __future__ import annotations

import hashlib
import numbers
import re
from pathlib import Path
from typing import Any

import pandas as pd

from analysis_profiles import enrich_metric_contract, resolve_analysis_profile
from analysis_periods import validate_comparison_scope


SUPPORTED_AGGREGATIONS = {"sum", "ratio", "average", "last", "distinct_count", "sum_product", "median"}
QUALITY_IMPACT_AGGREGATIONS = {"sum", "sum_product"}
COMPARISON_ALIASES = {
    "period_over_period": {"period_over_period", "mom", "wow"},
    "year_over_year": {"year_over_year", "yoy"},
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def period_labels(dates: pd.Series, period_type: str, week_start: str) -> pd.Series:
    if period_type == "monthly":
        return dates.dt.to_period("M").astype(str)
    if period_type == "weekly":
        end_day = "SUN" if week_start.lower() in {"monday", "mon"} else "SAT"
        return dates.dt.to_period(f"W-{end_day}").map(
            lambda period: period.start_time.date().isoformat()
        )
    return dates.dt.date.astype(str)


def normalize_metric_contracts(
    request: Any, source_columns: set[str] | None = None
) -> list[dict[str, Any]]:
    supplied: dict[str, dict[str, Any]] = {}
    for raw in request.metric_contracts:
        name = str(raw.get("name") or raw.get("metric") or "").strip()
        if name:
            supplied[name] = dict(raw)

    contracts: list[dict[str, Any]] = []
    for name in request.primary_metrics:
        raw = supplied.get(name, {})
        forbidden = {key for key in raw if str(key).lower() in {"expression", "code", "eval", "python"}}
        if forbidden:
            raise ValueError("指标合同不允许自由执行字段：" + ", ".join(sorted(forbidden)))
        aggregation = str(raw.get("aggregation", "sum"))
        if aggregation not in SUPPORTED_AGGREGATIONS:
            raise ValueError(f"未知 aggregation 聚合方式：{aggregation}")
        metric_type = str(raw.get("metric_type", _default_metric_type(name, aggregation)))
        if "aggregation" not in raw and metric_type in {
            "ratio", "average", "balance", "distinct_count", "median", "sum_product"
        }:
            raise ValueError(
                f"非加总指标“{name}”需要在 metric_contracts 中明确聚合口径；"
                "比率需提供 numerator/denominator，均值需使用 average，余额需使用 last。"
            )
        if aggregation == "ratio" and not (
            raw.get("numerator") and raw.get("denominator")
        ):
            raise ValueError(f"比率指标缺少 numerator 或 denominator：{name}")
        source_field = raw.get("source_field")
        factors = raw.get("factors")
        if aggregation in {"distinct_count", "median"} and not source_field:
            raise ValueError(f"{aggregation} 缺少 source_field：{name}")
        if aggregation == "sum_product":
            if not isinstance(factors, (list, tuple)) or len(factors) != 2 or not all(str(value).strip() for value in factors):
                raise ValueError(f"sum_product 需要严格两个 factors：{name}")
        unit = str(raw.get("unit", _infer_unit(name)))
        contract = {
                "metric_id": str(raw.get("metric_id", f"metric:{name}")),
                "name": name,
                "metric_type": metric_type,
                "aggregation": aggregation,
                "numerator": raw.get("numerator"),
                "denominator": raw.get("denominator"),
                "source_field": source_field,
                "factors": tuple(str(value) for value in factors) if isinstance(factors, (list, tuple)) else (),
                "unit": unit,
                "scale": float(raw.get("scale", 100 if aggregation == "ratio" else 1)),
                "formula": str(raw.get("formula", _default_formula(name, aggregation, raw))),
                "confidence": "confirmed" if raw else "inferred",
                "display_name": raw.get("display_name"),
                "role": raw.get("role"),
                "direction": raw.get("direction"),
                "definition": raw.get("definition"),
                "formula_display": raw.get("formula_display"),
                "derived": raw.get("derived"),
        }
        if "zero_denominator_policy" in raw:
            contract["zero_denominator_policy"] = raw["zero_denominator_policy"]
        validate_metric_contract(contract)
        contracts.append(enrich_metric_contract(contract, source_columns))
    return contracts


def validate_metric_contract(contract: Any) -> None:
    """Validate the declarative aggregation contract used by analysis and followups."""

    if not isinstance(contract, dict):
        raise ValueError("invalid_metric_contract")
    name = contract.get("name")
    aggregation = contract.get("aggregation")
    if "zero_denominator_policy" in contract and (
        aggregation != "ratio" or contract["zero_denominator_policy"] not in {"exclude_row", "include_in_totals"}
    ):
        raise ValueError("invalid zero_denominator_policy")
    if not isinstance(name, str) or not name.strip() or not isinstance(aggregation, str) or aggregation not in SUPPORTED_AGGREGATIONS:
        raise ValueError("invalid_metric_contract")
    source_field = contract.get("source_field")
    if source_field is not None and (not isinstance(source_field, str) or not source_field.strip()):
        raise ValueError("invalid_metric_contract")
    if aggregation in {"distinct_count", "median"} and not isinstance(source_field, str):
        raise ValueError("invalid_metric_contract")
    if aggregation == "sum_product":
        factors = contract.get("factors")
        if not isinstance(factors, (list, tuple)) or len(factors) != 2 or not all(isinstance(value, str) and value.strip() for value in factors):
            raise ValueError("invalid_metric_contract")
    if aggregation == "ratio" and not all(
        isinstance(contract.get(field), str) and contract[field].strip()
        for field in ("numerator", "denominator")
    ):
        raise ValueError("invalid_metric_contract")
    if "scale" in contract and contract["scale"] is not None and (
        isinstance(contract["scale"], bool) or not isinstance(contract["scale"], (int, float))
    ):
        raise ValueError("invalid_metric_contract")
    metric_type = contract.get("metric_type")
    if metric_type is not None:
        if not isinstance(metric_type, str) or metric_type not in _METRIC_TYPES_BY_AGGREGATION[aggregation]:
            raise ValueError("invalid_metric_contract")
    formula = contract.get("formula")
    if isinstance(formula, str):
        parsed_formula = _parse_structured_formula(formula)
        if parsed_formula is not None:
            formula_aggregation, formula_fields = parsed_formula
            if formula_aggregation != aggregation:
                raise ValueError("invalid_metric_contract")
            if not _formula_fields_match_contract(contract, formula_fields):
                raise ValueError("invalid_metric_contract")


def _comparison_enabled(request: Any, comparison: str) -> bool:
    configured = {str(value).lower() for value in request.comparisons}
    return bool(configured & COMPARISON_ALIASES[comparison])


def required_source_fields(contract: dict[str, Any]) -> list[str]:
    aggregation = str(contract["aggregation"])
    if aggregation == "ratio":
        return [str(value) for value in (contract.get("numerator"), contract.get("denominator")) if value]
    if aggregation in {"distinct_count", "median"}:
        return [str(contract["source_field"])]
    if aggregation == "sum_product":
        return [str(value) for value in contract["factors"]]
    return [str(contract.get("source_field") or contract["name"])]


def numeric_source_fields(contract: dict[str, Any]) -> list[str]:
    if contract["aggregation"] == "distinct_count":
        return []
    return required_source_fields(contract)


def _numeric_fields(contracts: list[dict[str, Any]]) -> list[str]:
    fields: list[str] = []
    for contract in contracts:
        fields.extend(numeric_source_fields(contract))
    return list(dict.fromkeys(fields))


def _validate_numeric_fields(
    frame: pd.DataFrame,
    contracts: list[dict[str, Any]],
    policy: str,
) -> list[str]:
    warnings: list[str] = []
    for field in _numeric_fields(contracts):
        source = frame[field]
        nonblank = source.notna() & source.astype(str).str.strip().ne("")
        parsed = pd.to_numeric(source, errors="coerce")
        invalid_count = int((nonblank & parsed.isna()).sum())
        if not invalid_count:
            continue
        message = f"数值字段“{field}”有 {invalid_count} 个非空值无法解析"
        if policy == "fail":
            raise ValueError(f"{message}；请清洗数据或显式选择 coerce_and_warn。")
        warnings.append(f"{message}，已按缺失值处理。")
    return warnings


def _infer_metric_type(name: str) -> str:
    lowered = name.lower()
    if any(marker in lowered for marker in ("率", "占比", "ratio", "rate")):
        return "ratio"
    if any(marker in lowered for marker in ("余额", "库存", "balance", "stock")):
        return "balance"
    if any(marker in lowered for marker in ("均", "客单价", "average", "avg")):
        return "average"
    if any(marker in lowered for marker in ("收入", "金额", "成本", "gmv", "revenue")):
        return "amount"
    return "count"


_METRIC_TYPES_BY_AGGREGATION = {
    "sum": {"sum", "additive", "amount", "count"},
    "ratio": {"ratio"},
    "average": {"average"},
    "last": {"last", "balance"},
    "distinct_count": {"distinct_count"},
    "sum_product": {"sum_product"},
    "median": {"median"},
}


def _default_metric_type(name: str, aggregation: str) -> str:
    if aggregation in {"distinct_count", "sum_product", "median"}:
        return aggregation
    if aggregation == "last":
        return "balance"
    if aggregation == "average":
        return "average"
    if aggregation == "ratio":
        return "ratio"
    return _infer_metric_type(name)


def _parse_structured_formula(formula: str) -> tuple[str, tuple[str, ...]] | None:
    """Parse only a small, display-safe formula grammar; leave legacy prose unknown."""

    text = formula.strip()
    if not text:
        return None
    ratio_parts = _split_top_level(text, "/")
    if ratio_parts is not None and len(ratio_parts) == 2:
        left = _parse_function_formula(ratio_parts[0])
        right = _parse_function_formula(ratio_parts[1])
        if (
            left is not None
            and right is not None
            and left[0] == right[0] == "sum"
            and len(left[1]) == len(right[1]) == 1
        ):
            return "ratio", (left[1][0], right[1][0])
        return None
    chinese_ratio_parts = _split_top_level(text, "÷")
    if chinese_ratio_parts is not None and len(chinese_ratio_parts) == 2:
        left = _bare_chinese_formula_field(chinese_ratio_parts[0])
        right = _bare_chinese_formula_field(chinese_ratio_parts[1])
        return ("ratio", (left, right)) if left is not None and right is not None else None
    chinese_formula = re.fullmatch(r"(.+?)(去重计数|中位数|平均值|期末值|合计)", text)
    if chinese_formula:
        field = _bare_chinese_formula_field(chinese_formula.group(1))
        aggregations = {
            "去重计数": "distinct_count",
            "中位数": "median",
            "平均值": "average",
            "期末值": "last",
            "合计": "sum",
        }
        return (
            (aggregations[chinese_formula.group(2)], (field,))
            if field is not None
            else None
        )
    return _parse_function_formula(text)


def _parse_function_formula(text: str) -> tuple[str, tuple[str, ...]] | None:
    count_distinct = re.fullmatch(
        r"count\s+distinct\s*\((.*)\)", text.strip(), flags=re.IGNORECASE | re.DOTALL
    )
    if count_distinct:
        field = _structured_formula_field(count_distinct.group(1))
        return ("distinct_count", (field,)) if field is not None else None

    match = re.fullmatch(
        r"([A-Za-z_]+)\s*\((.*)\)", text.strip(), flags=re.IGNORECASE | re.DOTALL
    )
    if not match:
        return None
    function = match.group(1).lower().replace("_", "")
    arguments = match.group(2)
    if function == "count":
        distinct = re.fullmatch(r"distinct\s+(.+)", arguments.strip(), flags=re.IGNORECASE | re.DOTALL)
        field = _structured_formula_field(distinct.group(1) if distinct else arguments)
        if field is None:
            return None
        return ("distinct_count" if distinct else "count"), (field,)
    if function == "countdistinct":
        field = _structured_formula_field(arguments)
        return ("distinct_count", (field,)) if field is not None else None
    if function == "sumproduct":
        fields = _two_structured_formula_fields(arguments, ",")
        return ("sum_product", fields) if fields is not None else None
    if function == "sum":
        product = _two_structured_formula_fields(arguments, "×") or _two_structured_formula_fields(arguments, "*")
        if product is not None:
            return "sum_product", product
        field = _structured_formula_field(arguments)
        return ("sum", (field,)) if field is not None else None
    aliases = {
        "median": "median",
        "mean": "average",
        "average": "average",
        "avg": "average",
        "last": "last",
    }
    if function in aliases:
        field = _structured_formula_field(arguments)
        return (aliases[function], (field,)) if field is not None else None
    if function == "ratio":
        fields = _two_structured_formula_fields(arguments, ",")
        return ("ratio", fields) if fields is not None else None
    return None


def _split_top_level(text: str, separator: str) -> list[str] | None:
    depth = 0
    pieces: list[str] = []
    start = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                return None
        elif char == separator and depth == 0:
            pieces.append(text[start:index])
            start = index + 1
    if depth != 0:
        return None
    pieces.append(text[start:])
    return pieces


def _structured_formula_field(value: str) -> str | None:
    field = value.strip()
    if not field or any(token in field for token in ("(", ")", ",", "*", "×", "/")):
        return None
    return field


def _bare_chinese_formula_field(value: str) -> str | None:
    field = _structured_formula_field(value)
    if field is None or any(
        token in field for token in (":", "：", "。", "；", ";", "？", "?", "！", "!", "、")
    ):
        return None
    return field


def _two_structured_formula_fields(value: str, separator: str) -> tuple[str, str] | None:
    parts = _split_top_level(value, separator)
    if parts is None or len(parts) != 2:
        return None
    left = _structured_formula_field(parts[0])
    right = _structured_formula_field(parts[1])
    return (left, right) if left is not None and right is not None else None


def _formula_fields_match_contract(contract: dict[str, Any], fields: tuple[str, ...]) -> bool:
    aggregation = str(contract["aggregation"])
    if aggregation == "ratio":
        return fields == (str(contract["numerator"]), str(contract["denominator"]))
    if aggregation == "sum_product":
        # Multiplication is commutative, so reverse factor order remains the same calculation.
        return sorted(fields) == sorted(str(value) for value in contract["factors"])
    source_field = str(contract.get("source_field") or contract["name"])
    return fields == (source_field,)


def _infer_unit(name: str) -> str:
    metric_type = _infer_metric_type(name)
    if metric_type == "ratio":
        return "%"
    if metric_type == "amount":
        return "currency"
    return "count"


def _default_formula(name: str, aggregation: str, raw: dict[str, Any]) -> str:
    if aggregation == "ratio":
        numerator = raw.get("numerator", "numerator")
        denominator = raw.get("denominator", "denominator")
        return f"sum({numerator}) / sum({denominator})"
    if aggregation == "average":
        return f"mean({raw.get('source_field') or name})"
    if aggregation == "last":
        return f"last({raw.get('source_field') or name})"
    if aggregation == "distinct_count":
        return f"count_distinct({raw.get('source_field')})"
    if aggregation == "median":
        return f"median({raw.get('source_field')})"
    if aggregation == "sum_product":
        left, right = raw["factors"]
        return f"sum({left} × {right})"
    return f"sum({raw.get('source_field') or name})"


def _chart_display_contract(
    contract: dict[str, Any],
    values: list[float],
    *,
    scope_label: str,
    takeaway: str,
) -> dict[str, Any]:
    unit = str(contract.get("unit", ""))
    max_value = max((abs(float(value)) for value in values), default=0.0)
    display_scale = 1.0
    display_unit = unit or "数值"
    if unit in {"元", "currency"}:
        if max_value >= 100_000_000:
            display_scale = 100_000_000.0
            display_unit = "亿元" if unit == "元" else "亿"
        elif max_value >= 10_000:
            display_scale = 10_000.0
            display_unit = "万元" if unit == "元" else "万"
    elif unit in {"单", "count"} and max_value >= 10_000:
        display_scale = 10_000.0
        display_unit = "万单" if unit == "单" else "万"
    elif unit == "%":
        display_unit = "%"
    elif unit == "x":
        display_unit = "倍"
    number_format = "0.00" if unit in {"%", "x"} else (
        "0.0" if display_scale != 1 else "#,##0"
    )
    return {
        "unit": unit,
        "display_unit": display_unit,
        "display_scale": display_scale,
        "number_format": number_format,
        "scope_label": scope_label,
        "takeaway": takeaway,
    }


def _source_valid_mask(frame: pd.DataFrame, contract: dict[str, Any]) -> pd.Series:
    """Return source records that can genuinely participate in a metric."""

    aggregation = str(contract["aggregation"])
    if aggregation == "ratio":
        numerator = pd.to_numeric(frame[str(contract["numerator"])], errors="coerce")
        denominator = pd.to_numeric(frame[str(contract["denominator"])], errors="coerce")
        valid = numerator.notna() & denominator.notna()
        if contract.get("zero_denominator_policy", "exclude_row") == "include_in_totals":
            return valid
        return valid & denominator.ne(0)
    if aggregation == "sum_product":
        factors = [pd.to_numeric(frame[field], errors="coerce") for field in contract["factors"]]
        return pd.concat(factors, axis=1).notna().all(axis=1)
    if aggregation == "distinct_count":
        source = frame[str(contract["source_field"])]
        return source.notna() & source.astype(str).str.strip().ne("")
    source = pd.to_numeric(frame[str(contract.get("source_field") or contract["name"])], errors="coerce")
    return source.notna()


def _calculation_exclusion_note(contract: dict[str, Any]) -> str:
    if contract["aggregation"] == "ratio":
        if contract.get("zero_denominator_policy") == "include_in_totals":
            return "保留单行分母为零的分子数值；仅排除分子或分母缺失行，汇总分母为零时不可计算"
        return "排除分母为零或指标不可计算行"
    if contract["aggregation"] == "sum_product":
        return "排除逐行乘积因子缺失或不可计算行"
    return "排除指标源字段缺失或不可计算行"


def _provenance_scope(
    contract: dict[str, Any],
    *,
    periods: list[str] | tuple[str, ...],
    filters: list[tuple[str, Any]] | tuple[tuple[str, Any], ...] = (),
) -> str:
    period_text = "、".join(str(value) for value in periods) or "当前完整分析窗口"
    parts = [f"分析/比较周期：{period_text}"]
    if filters:
        parts.append("等值过滤：" + "、".join(f"{field}={value}" for field, value in filters))
    parts.append(_calculation_exclusion_note(contract))
    return "；".join(parts)


def _aggregate_series(
    frame: pd.DataFrame,
    contract: dict[str, Any],
    group_field: str | list[str],
) -> pd.Series:
    aggregation = contract["aggregation"]
    name = contract["name"]
    groupers = [frame[field] for field in group_field] if isinstance(group_field, list) else frame[group_field]
    if aggregation == "ratio":
        numerator = contract.get("numerator")
        denominator = contract.get("denominator")
        if not numerator or not denominator:
            raise ValueError(f"比率指标缺少分子或分母：{name}")
        valid = _source_valid_mask(frame, contract)
        num = pd.to_numeric(frame[numerator], errors="coerce").where(valid).groupby(groupers).sum(min_count=1)
        den = pd.to_numeric(frame[denominator], errors="coerce").where(valid).groupby(groupers).sum(min_count=1)
        return (num / den.replace(0, pd.NA) * float(contract.get("scale", 100))).dropna()
    if aggregation == "distinct_count":
        source = frame[str(contract["source_field"])]
        clean = source.where(source.notna() & source.astype(str).str.strip().ne(""))
        return clean.groupby(groupers).nunique(dropna=True).astype(float)
    if aggregation == "sum_product":
        left, right = (pd.to_numeric(frame[field], errors="coerce") for field in contract["factors"])
        return (left * right).groupby(groupers).sum(min_count=1).dropna()
    source = str(contract.get("source_field") or name)
    numeric = pd.to_numeric(frame[source], errors="coerce")
    grouped = numeric.groupby(groupers)
    if aggregation == "average":
        return grouped.mean().dropna()
    if aggregation == "last":
        return grouped.last().dropna()
    if aggregation == "median":
        return grouped.median().dropna()
    return grouped.sum(min_count=1).dropna()


def _aggregate_total(frame: pd.DataFrame, contract: dict[str, Any]) -> float | None:
    aggregation = contract["aggregation"]
    name = contract["name"]
    if aggregation == "ratio":
        numerator = contract.get("numerator")
        denominator = contract.get("denominator")
        if not numerator or not denominator:
            raise ValueError(f"比率指标缺少分子或分母：{name}")
        valid = _source_valid_mask(frame, contract)
        num = pd.to_numeric(frame[numerator], errors="coerce").where(valid).sum(skipna=True)
        den = pd.to_numeric(frame[denominator], errors="coerce").where(valid).sum(skipna=True)
        return (
            None
            if den == 0
            else float(num / den * float(contract.get("scale", 100)))
        )
    if aggregation == "distinct_count":
        source = frame[str(contract["source_field"])]
        clean = source[source.notna() & source.astype(str).str.strip().ne("")]
        return float(clean.nunique())
    if aggregation == "sum_product":
        left, right = (pd.to_numeric(frame[field], errors="coerce") for field in contract["factors"])
        value = (left * right).sum(min_count=1)
        return None if pd.isna(value) else float(value)
    source = str(contract.get("source_field") or name)
    numeric = pd.to_numeric(frame[source], errors="coerce")
    if aggregation == "average":
        value = numeric.mean(skipna=True)
    elif aggregation == "last":
        clean = numeric.dropna()
        value = clean.iloc[-1] if not clean.empty else None
    elif aggregation == "median":
        value = numeric.median(skipna=True)
    else:
        value = numeric.sum(skipna=True)
    return None if value is None or pd.isna(value) else float(value)


def dimension_yoy_source_sample_counts(
    *,
    latest_frame: pd.DataFrame,
    comparison_frame: pd.DataFrame,
    contract: dict[str, Any],
    dimension: str,
) -> dict[str, dict[tuple[type[Any], Any], int]]:
    """Preaggregate participating rows for one dimension/metric YoY pair."""

    def grouped_counts(frame: pd.DataFrame) -> dict[tuple[type[Any], Any], int]:
        valid = _source_valid_mask(frame, contract)
        return {
            _dimension_value_key(value): int(count)
            for value, count in frame.loc[valid].groupby(dimension, dropna=True).size().items()
        }

    return {
        "latest": grouped_counts(latest_frame),
        "comparison": grouped_counts(comparison_frame),
    }


def _dimension_value_key(value: Any) -> tuple[type[Any], Any]:
    """Keep pandas grouping keys typed: ``1`` and ``\"1\"`` are distinct."""

    return (type(value), value)


def _dimension_value_type_label(value: Any) -> str:
    if isinstance(value, str):
        return "文本"
    if isinstance(value, bool):
        return "布尔值"
    if isinstance(value, numbers.Number):
        return "数值"
    return type(value).__name__


def dimension_yoy_value_identities(
    values: Any,
) -> dict[tuple[type[Any], Any], dict[str, str]]:
    """Build display and ID metadata for one typed YoY value set in O(values)."""

    items = list(values)
    display_groups: dict[str, list[Any]] = {}
    for value in items:
        display_groups.setdefault(str(value), []).append(value)
    identities: dict[tuple[type[Any], Any], dict[str, str]] = {}
    for text, grouped_values in display_groups.items():
        typed_keys = {_dimension_value_key(value) for value in grouped_values}
        for value in grouped_values:
            has_collision = len(typed_keys) > 1
            identities[_dimension_value_key(value)] = {
                "display": (
                    f"{text}（{_dimension_value_type_label(value)}）"
                    if has_collision
                    else text
                ),
                "evidence_suffix": (
                    f":{_dimension_value_evidence_suffix(value)}"
                    if has_collision
                    else ""
                ),
            }
    return identities


def _dimension_value_displays(values: Any) -> dict[tuple[type[Any], Any], str]:
    """Add a type suffix only when distinct typed keys share visible text."""

    items = list(values)
    display_groups: dict[str, list[Any]] = {}
    for value in items:
        display_groups.setdefault(str(value), []).append(value)
    displays: dict[tuple[type[Any], Any], str] = {}
    for text, grouped_values in display_groups.items():
        typed_keys = {_dimension_value_key(value) for value in grouped_values}
        for value in grouped_values:
            displays[_dimension_value_key(value)] = (
                f"{text}（{_dimension_value_type_label(value)}）"
                if len(typed_keys) > 1
                else text
            )
    return displays


def _dimension_value_evidence_suffix(value: Any) -> str:
    identity = f"{type(value).__module__}.{type(value).__qualname__}"
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:8]
    return f"type-{type(value).__name__.lower()}-{digest}"


_FOLLOWUP_FILTER_OPERATORS = {"eq", "in"}
_FOLLOWUP_TOOLS = {
    "period_comparison",
    "dimension_breakdown",
    "cross_breakdown",
    "concentration",
    "quality_impact",
}


def execute_readonly_aggregation(
    frame: pd.DataFrame,
    contract: dict[str, Any],
    *,
    tool: str,
    dimensions: list[str] | tuple[str, ...] = (),
    filters: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    comparison_scope: dict[str, Any] | None = None,
    quality_filter: dict[str, Any] | None = None,
    scope_registry=None,
    scope_parent_id: str = "source_rows",
) -> dict[str, Any]:
    """Run one fixed aggregate-only tool with its own declared semantics."""

    if tool not in _FOLLOWUP_TOOLS:
        raise ValueError("unsupported_tool")
    if not isinstance(frame, pd.DataFrame):
        raise ValueError("frame 必须是 DataFrame")
    validate_metric_contract(contract)
    dimension_list = [str(value) for value in dimensions]
    if len(set(dimension_list)) != len(dimension_list):
        raise ValueError("dimensions 不能重复")
    missing_dimensions = sorted(set(dimension_list) - set(frame.columns))
    if missing_dimensions:
        raise ValueError("missing_required_field:" + ",".join(missing_dimensions))
    if tool in {"dimension_breakdown", "concentration"} and len(dimension_list) != 1:
        raise ValueError("missing_required_field:dimension")
    if tool == "cross_breakdown" and len(dimension_list) != 2:
        raise ValueError("missing_required_field:cross_dimensions")
    if tool in {"period_comparison", "quality_impact"} and dimension_list:
        raise ValueError("invalid_tool_contract")

    def apply_filters(source: pd.DataFrame, predicates: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> pd.DataFrame:
        scoped = source
        for predicate in predicates:
            if not isinstance(predicate, dict):
                raise ValueError("invalid_filter")
            field = str(predicate.get("field") or "")
            operator = str(predicate.get("operator") or "")
            if field not in source.columns or operator not in _FOLLOWUP_FILTER_OPERATORS:
                raise ValueError("invalid_filter")
            if operator == "eq":
                if "value" not in predicate:
                    raise ValueError("invalid_filter")
                scoped = scoped.loc[scoped[field] == predicate["value"]]
            else:
                values = predicate.get("values")
                if not isinstance(values, (list, tuple)):
                    raise ValueError("invalid_filter")
                scoped = scoped.loc[scoped[field].isin(list(values))]
        return scoped

    scoped = apply_filters(frame, filters)

    def scoped_result(result, rows, *, bindings=None):
        if scope_registry is None:
            return result
        def register(source, role):
            valid = source.loc[_source_valid_mask(source, contract)]
            return scope_registry.register(valid, parent_scope_id=scope_parent_id, rules={
                "metric_contract": contract, "filters": list(filters),
                "comparison_scope": comparison_scope, "quality_filter": quality_filter,
                "tool": tool, "role": role, "dimensions": dimension_list,
                "missing_dimension_policy": "include_unclassified",
            }, definition=f"{contract['name']}追问：{tool}，{role}；使用已确认分析窗口及声明筛选。")
        scope_id = register(rows, "baseline" if tool == "quality_impact" else "result")
        return {**result, "scope_id": scope_id,
                "sample_count": scope_registry.record(scope_id)["included_rows"],
                "scope_bindings": {role: register(source, role) for role, source in (bindings or {}).items()}}
    if tool == "period_comparison":
        validate_comparison_scope(comparison_scope)
        if not isinstance(comparison_scope, dict):
            raise ValueError("invalid_comparison_scope")
        period_field = str(comparison_scope.get("period_field") or "")
        baseline = comparison_scope.get("baseline")
        current = comparison_scope.get("current")
        if period_field not in frame.columns or not isinstance(baseline, (list, tuple)) or not baseline or not isinstance(current, (list, tuple)) or not current:
            raise ValueError("invalid_comparison_scope")
        baseline_frame = scoped.loc[scoped[period_field].astype(str).isin([str(value) for value in baseline])]
        current_frame = scoped.loc[scoped[period_field].astype(str).isin([str(value) for value in current])]
        if baseline_frame.empty or current_frame.empty:
            raise ValueError("missing_scope_data")
        baseline_total = _aggregate_total(baseline_frame, contract)
        current_total = _aggregate_total(current_frame, contract)
        if baseline_total is None or current_total is None:
            raise ValueError("insufficient_evidence")
        return scoped_result({
            "tool": tool, "period_field": period_field, "baseline": baseline_total,
            "current": current_total, "delta": float(current_total - baseline_total),
            "change_pct": None if baseline_total == 0 else float((current_total - baseline_total) / abs(baseline_total)),
        }, pd.concat([baseline_frame, current_frame]).loc[lambda rows: ~rows.index.duplicated()],
            bindings={"baseline": baseline_frame, "current": current_frame})
    if tool == "quality_impact":
        if contract["aggregation"] not in QUALITY_IMPACT_AGGREGATIONS:
            raise ValueError("unsupported_metric_for_tool")
        if not isinstance(quality_filter, dict):
            raise ValueError("invalid_quality_filter")
        affected_frame = apply_filters(scoped, [quality_filter])
        unaffected_frame = scoped.drop(index=affected_frame.index)
        if scoped.empty or affected_frame.empty or unaffected_frame.empty:
            raise ValueError("missing_scope_data")
        baseline_total = _aggregate_total(scoped, contract)
        affected_total = _aggregate_total(affected_frame, contract)
        unaffected_total = _aggregate_total(unaffected_frame, contract)
        if baseline_total is None or affected_total is None or unaffected_total is None:
            raise ValueError("evidence_insufficient")
        if baseline_total <= 0 or affected_total < 0 or unaffected_total < 0:
            raise ValueError("evidence_insufficient")
        affected_share = float(affected_total / baseline_total)
        if not 0 <= affected_share <= 1:
            raise ValueError("evidence_insufficient")
        return scoped_result({
            "tool": tool, "baseline_total": baseline_total,
            "affected_total": affected_total, "unaffected_total": unaffected_total,
            "impact": affected_total,
            "affected_share": affected_share,
        }, scoped, bindings={"baseline": scoped, "affected": affected_frame, "unaffected": unaffected_frame})

    def grouped_values(source: pd.DataFrame) -> list[dict[str, Any]]:
        if not dimension_list:
            return []
        grouped_source = source.copy()
        for field in dimension_list:
            # Match the primary dimension summary: missing objects remain a
            # visible group, not hidden rows still included in the denominator.
            grouped_source[field] = grouped_source[field].astype(object).fillna("未分类")
        series = _aggregate_series(grouped_source, contract, dimension_list)
        rows: list[dict[str, Any]] = []
        for key, value in series.dropna().items():
            values = list(key) if isinstance(key, tuple) else [key]
            rows.append({"dimensions": [str(value) for value in values], "metric": float(value)})
        return sorted(rows, key=lambda item: tuple(item["dimensions"]))

    groups = grouped_values(scoped)
    total = _aggregate_total(scoped, contract)
    if total is None:
        raise ValueError("insufficient_evidence")
    if tool == "concentration":
        if not groups or total == 0:
            raise ValueError("insufficient_evidence")
        shares = [float(item["metric"]) / float(total) for item in groups]
        return scoped_result({
            "tool": tool, "dimension": dimension_list[0], "total": total,
            "top_share": max(shares), "herfindahl_index": sum(value * value for value in shares),
            "group_count": len(groups),
        }, scoped)
    return scoped_result({
        "tool": tool, "kind": tool, "dimensions": dimension_list,
        "total": total, "groups": groups, "group_count": len(groups),
    }, scoped)
def _dimension_summary(
    frame: pd.DataFrame,
    contract: dict[str, Any],
    dimension: str,
    *,
    top_n: int = 5,
    display_field: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return decision-safe Top-N rows without silently dropping the long tail."""
    scoped = frame.copy()
    scoped[dimension] = scoped[dimension].fillna("未分类")
    grouped = _aggregate_series(scoped, contract, dimension).sort_values(
        ascending=False
    )
    top = grouped.head(top_n)
    rest_values = list(grouped.index[top_n:])
    display_values = _dimension_value_displays(top.index)
    rows = [
        {
            "value": display_values[_dimension_value_key(value)],
            "metric": float(amount),
            "rank": index + 1,
            "is_other": False,
        }
        for index, (value, amount) in enumerate(top.items())
    ]
    if display_field and display_field in scoped.columns and display_field != dimension:
        # Keep the grouping identity and all calculations unchanged.  Names
        # come only from the confirmed object binding within this same scope.
        name_source = scoped.loc[_source_valid_mask(scoped, contract)]
        for row, value in zip(rows, top.index):
            names = name_source.loc[name_source[dimension].eq(value), display_field].dropna().astype(str).str.strip()
            names = names.loc[names.ne("")]
            row["key"] = row["value"]
            row["display_value"] = str(names.mode().iloc[0]) if not names.empty else row["value"]
            row["display_missing"] = names.empty
    if rest_values:
        other_frame = scoped[scoped[dimension].isin(rest_values)]
        other_value = _aggregate_total(other_frame, contract)
        if other_value is not None:
            rows.append(
                {
                    "value": "其他",
                    "metric": float(other_value),
                    "rank": None,
                    "is_other": True,
                    "member_count": len(rest_values),
                }
            )

    aggregation = str(contract["aggregation"])
    top_n_coverage: float | None = None
    if aggregation in {"sum", "sum_product"}:
        total = _aggregate_total(scoped, contract)
        if total not in (None, 0):
            top_n_coverage = round(float(top.sum() / total), 6)
    semantics = {
        "view_type": "contribution" if aggregation in {"sum", "sum_product"} else "performance",
        "aggregation": aggregation,
        "direction": str(contract.get("direction", "neutral")),
        "ranking": "metric_descending",
        "top_n": top_n,
        "top_n_coverage": top_n_coverage,
        "total_member_count": int(len(grouped)),
        "other_member_count": int(len(rest_values)),
        "other_is_reaggregated": bool(rest_values),
    }
    if display_field:
        semantics["display_field"] = display_field
        semantics["display_policy"] = "confirmed_field_mode_in_scope; missing_name_uses_identifier"
    return rows, semantics


def _change_pct(latest: float | None, previous: float | None) -> float | None:
    if latest is None or previous in (None, 0):
        return None
    return round((latest - previous) / abs(previous) * 100, 2)


def _finding_text(name: str, change_pct: float | None) -> str:
    if change_pct is None:
        return f"{name}当前缺少可比较的上一周期。"
    direction = "上升" if change_pct > 0 else "下降" if change_pct < 0 else "持平"
    return f"{name}较上一周期{direction}{abs(change_pct):.2f}%。"


def _year_over_year_label(
    latest_period: str, period_type: str, week_start: str
) -> str:
    if period_type == "monthly":
        return str(pd.Period(latest_period, freq="M") - 12)
    if period_type == "weekly":
        prior_date = pd.Timestamp(latest_period) - pd.DateOffset(years=1)
        return str(
            period_labels(pd.Series([prior_date]), "weekly", week_start).iloc[0]
        )
    return (pd.Timestamp(latest_period) - pd.DateOffset(years=1)).date().isoformat()


def _display_period_label(value: str | None, period_type: str) -> str:
    if not value:
        return "—"
    if period_type == "monthly":
        period = pd.Period(str(value), freq="M")
        return f"{period.year}年{period.month}月"
    if period_type == "weekly":
        date = pd.Timestamp(value)
        return f"{date.year}年{date.month}月{date.day}日当周"
    date = pd.Timestamp(value)
    return f"{date.year}年{date.month}月{date.day}日"


def _analysis_window_label(periods: list[str], period_type: str) -> str:
    if not periods:
        return "—"
    start = _display_period_label(periods[0], period_type)
    end = _display_period_label(periods[-1], period_type)
    return start if start == end else f"{start}—{end}"


def _first_metric_name(
    contracts: list[dict[str, Any]], markers: tuple[str, ...]
) -> str | None:
    for contract in contracts:
        lowered = str(contract["name"]).lower()
        if any(marker in lowered for marker in markers):
            return str(contract["name"])
    return None


def enrich_question_graph_with_preliminary_scan(
    plan: dict[str, Any],
    *,
    analysis: dict[str, Any],
) -> dict[str, Any]:
    """Score candidate questions from already-computed deterministic aggregates."""
    metrics = analysis.get("metrics", {})
    dimensions = analysis.get("dimensions", {})
    warning_source = analysis.get("warnings")
    if warning_source is None:
        warning_source = analysis.get("validation", {}).get("warnings", [])
    warnings = list(warning_source)
    all_metric_evidence = [
        str(item.get("evidence_id"))
        for item in metrics.values()
        if isinstance(item, dict) and item.get("evidence_id")
    ]

    max_change = max(
        (
            abs(float(item["change_pct"]))
            for item in metrics.values()
            if isinstance(item, dict) and isinstance(item.get("change_pct"), (int, float))
        ),
        default=0.0,
    )
    dimension_evidence: list[str] = []
    max_coverage = 0.0
    for dimension, metric_map in dimensions.items():
        if not isinstance(metric_map, dict):
            continue
        for metric_name, rows in metric_map.items():
            evidence_id = f"dimension:{dimension}:{metric_name}"
            dimension_evidence.append(evidence_id)
            evidence = analysis.get("evidence_index", {}).get(evidence_id, {})
            coverage = evidence.get("semantics", {}).get("top_n_coverage") if isinstance(evidence, dict) else None
            if isinstance(coverage, (int, float)):
                max_coverage = max(max_coverage, abs(float(coverage)))

    def abnormality_score(question_type: str) -> int:
        if question_type == "anomaly_quality":
            return 3 if warnings else 1
        if question_type in {"contribution", "concentration", "structure_breakdown", "cross_segment"}:
            return 3 if max_coverage >= 0.8 else 2 if max_coverage >= 0.5 else 1 if dimension_evidence else 0
        return 3 if max_change >= 20 else 2 if max_change >= 5 else 1 if max_change > 0 else 0

    candidates: list[dict[str, Any]] = []
    active_ids = {str(item.get("question_id") or "") for item in plan.get("questions", [])}
    for raw in plan.get("candidate_questions", plan.get("questions", [])):
        item = dict(raw)
        question_type = str(item.get("question_type") or "structure_breakdown")
        signals = list(item.get("preliminary_signals", []))
        if question_type in {"result", "trend", "opportunity_risk"} and all_metric_evidence:
            signals.append({
                "signal_id": "metric_change_scan",
                "signal_type": "period_change",
                "value": max_change,
                "evidence_ids": all_metric_evidence,
            })
        if question_type in {"contribution", "concentration", "structure_breakdown", "cross_segment", "opportunity_risk"} and dimension_evidence:
            signals.append({
                "signal_id": "dimension_structure_scan",
                "signal_type": "structure_concentration",
                "value": round(max_coverage, 6),
                "evidence_ids": dimension_evidence,
            })
        if question_type == "anomaly_quality":
            signals.append({
                "signal_id": "quality_warning_scan",
                "signal_type": "quality_warning_count",
                "value": len(warnings),
                "evidence_ids": [],
            })
        scores = dict(item.get("selection_scores", {}))
        scores["abnormality"] = abnormality_score(question_type)
        scores["evidence_completeness"] = 3 if any(signal.get("evidence_ids") for signal in signals) else scores.get("evidence_completeness", 0)
        scores["redundancy_penalty"] = 1 if question_type in {"result", "trend"} and (max_change or dimension_evidence) else 0
        scores["total"] = sum(
            int(scores.get(field, 0))
            for field in (
                "importance", "abnormality", "decision_leverage",
                "evidence_completeness", "action_value", "story_coverage",
            )
        ) - int(scores.get("redundancy_penalty", 0))
        item["preliminary_signals"] = signals
        item["selection_scores"] = scores
        if str(item.get("question_id") or "") in active_ids:
            item["selection_reason"] = (
                f"可支持性通过；确定性初扫得分 {scores['total']}，"
                f"异常/差异信号 {scores['abnormality']}。"
            )
        candidates.append(item)

    ranked = sorted(
        (
            item for item in candidates
            if str(item.get("question_id") or "") in active_ids
        ),
        key=lambda item: (-int(item.get("selection_scores", {}).get("total", 0)), str(item.get("question_id") or "")),
    )
    rank_by_id = {
        str(item.get("question_id") or ""): index
        for index, item in enumerate(ranked, start=1)
    }
    for item in candidates:
        item["selection_rank"] = rank_by_id.get(str(item.get("question_id") or ""))
    candidate_by_id = {
        str(item.get("question_id") or ""): item for item in candidates
    }
    questions = [
        candidate_by_id.get(str(item.get("question_id") or ""), dict(item))
        for item in plan.get("questions", [])
    ]
    return {
        **plan,
        "questions": questions,
        "candidate_questions": candidates,
        "selected_question_ids": [str(item.get("question_id")) for item in ranked],
        "rejected_question_ids": [
            str(item.get("question_id"))
            for item in candidates
            if item.get("selection_status") == "rejected"
        ],
    }


def prepare_analysis_frame(
    frame: pd.DataFrame, request: Any, *, retained_periods: list[str] | None = None,
) -> tuple[pd.DataFrame, list[dict[str, Any]], list[str], list[str]]:
    """Single row-policy path for initial analysis, narrative and follow-ups.

    Replays use the already selected periods rather than making a second
    wall-clock-dependent completeness decision. The returned frame is local
    computation state, never a persisted row-level artifact.
    """
    work = frame.copy()
    duplicate_rows = int(work.duplicated().sum())
    warnings: list[str] = []
    duplicate_policy = str(getattr(request, "duplicate_policy", "keep"))
    if duplicate_rows and duplicate_policy == "drop_exact":
        work = work.drop_duplicates().copy()
        warnings.append(f"检测到并删除 {duplicate_rows} 条完全重复行。")
    elif duplicate_rows:
        warnings.append(
            f"检测到 {duplicate_rows} 条完全重复行；默认按合法业务记录保留，未参与自动去重。"
        )
    work[request.date_column] = pd.to_datetime(work[request.date_column], errors="coerce")
    work = work.dropna(subset=[request.date_column])
    work = work.sort_values(request.date_column, kind="stable")
    work["__period"] = period_labels(
        work[request.date_column], request.period_type, request.week_start
    )
    excluded_incomplete_periods: list[str] = []
    if retained_periods is not None:
        retained = {str(value) for value in retained_periods}
        period_values = work["__period"].astype(str)
        excluded_incomplete_periods = sorted(set(period_values) - retained)
        work = work.loc[period_values.isin(retained)].copy()
    elif request.incomplete_period_policy in {"exclude", "exclude_and_note"} and not work.empty:
        now = pd.Timestamp.now(tz=request.timezone).tz_localize(None)
        current_label = str(
            period_labels(
                pd.Series([now]), request.period_type, request.week_start
            ).iloc[0]
        )
        period_values = work["__period"].astype(str)
        if current_label in set(period_values):
            excluded_incomplete_periods.append(current_label)
        latest_label = str(period_values.iloc[-1])
        latest_date = pd.Timestamp(work[request.date_column].iloc[-1]).normalize()
        historical_trailing_incomplete = False
        semantic_contract = getattr(request, "semantic_contract", None)
        transactional_event_grain = (
            isinstance(semantic_contract, dict)
            and str(semantic_contract.get("domain") or semantic_contract.get("profile") or "")
            == "transactional_commerce"
            and str(semantic_contract.get("table_grain") or "") in {"order", "order_line"}
        )
        if request.period_type == "monthly" and transactional_event_grain:
            coverage = pd.DataFrame({
                "period": period_values,
                "day": work[request.date_column].dt.normalize(),
            })
            prior = coverage.loc[coverage["period"] != latest_label]
            prior_day_counts = (
                prior.groupby("period")["day"]
                .nunique()
                .astype(float)
            )
            baseline_days = float(prior_day_counts.median()) if len(prior_day_counts) >= 2 else 0.0
            trailing_days = float(coverage.loc[coverage["period"] == latest_label, "day"].nunique())
            historical_trailing_incomplete = (
                latest_date < latest_date.to_period("M").end_time.normalize()
                and baseline_days >= 7
                and trailing_days < baseline_days * 0.8
            )
        if historical_trailing_incomplete and latest_label not in excluded_incomplete_periods:
            excluded_incomplete_periods.append(latest_label)
        if excluded_incomplete_periods:
            work = work[~period_values.isin(excluded_incomplete_periods)].copy()
            for label in excluded_incomplete_periods:
                warnings.append(f"未完成周期 {label} 已按策略排除。")
    if work.empty:
        raise ValueError("排除未完成周期后没有可分析的完整数据")
    contracts = normalize_metric_contracts(request, set(str(value) for value in work.columns))
    warnings.extend(
        _validate_numeric_fields(
            work,
            contracts,
            str(getattr(request, "numeric_error_policy", "fail")),
        )
    )
    for contract in contracts:
        if contract["aggregation"] != "sum_product":
            continue
        factors = [pd.to_numeric(work[field], errors="coerce") for field in contract["factors"]]
        uncomputable = int(pd.concat(factors, axis=1).isna().any(axis=1).sum())
        if uncomputable:
            warnings.append(
                f"指标“{contract['name']}”有 {uncomputable} 行因 factors 缺失而未参与逐行乘积计算。"
            )
    return work, contracts, warnings, excluded_incomplete_periods


def analyse_frame(frame: pd.DataFrame, request: Any, *, scope_registry=None) -> dict[str, Any]:
    from analysis_scope import ScopeRegistry
    if scope_registry is None:
        frame = frame.reset_index(drop=True)
        scope_registry = ScopeRegistry(frame)
    work, contracts, warnings, excluded_incomplete_periods = prepare_analysis_frame(frame, request)
    time_scope = {
        "field": request.date_column, "period_type": request.period_type, "week_start": request.week_start,
        "periods": sorted(work["__period"].astype(str).unique().tolist()),
    }
    semantic = getattr(request, "semantic_contract", None) or {}
    display_fields = {
        binding["identifier_field"]: binding["display_field"]
        for binding in semantic.get("object_bindings", [])
        if binding.get("confirmation_status") == "confirmed"
        and binding.get("identifier_field") in work.columns
        and binding.get("display_field") in work.columns
    }
    window_scope_id = scope_registry.register(work, rules={
        "stage": "analysis_window", "time_scope": time_scope,
        "incomplete_period_policy": request.incomplete_period_policy,
        "filters": semantic.get("filters", semantic.get("filter_rules", [])),
        "duplicate_policy": str(getattr(request, "duplicate_policy", "keep")),
        "invalid_date_policy": "exclude", "numeric_error_policy": str(getattr(request, "numeric_error_policy", "fail")),
    }, definition="已确认分析窗口：" + "、".join(time_scope["periods"]) + "；按请求处理重复及无效日期。")

    def metric_scope(source, contract, *, filters=None, comparison=None, missing_dimensions=None):
        valid_rows = source.loc[_source_valid_mask(source, contract)]
        periods = sorted(source["__period"].astype(str).unique().tolist())
        return scope_registry.register(valid_rows, parent_scope_id=window_scope_id, rules={
            "metric_contract": contract, "time_scope": {**time_scope, "periods": periods},
            "filters": filters or [], "comparison": comparison,
            "missing_dimension_policy": missing_dimensions,
        }, definition=(str(contract.get("display_name") or contract["name"]) + "；" + "、".join(periods)
                       + "；" + _calculation_exclusion_note(contract)
                       + ("；按已声明对象条件细分" if filters else "")))
    analysis_profile = resolve_analysis_profile(request, contracts)
    is_retail_growth = analysis_profile["resolved"] == "retail_growth"
    comparison_label = {
        "monthly": "上月",
        "weekly": "上周",
    }.get(request.period_type, "上一完整周期")

    metrics: dict[str, dict[str, Any]] = {}
    kpis: list[dict[str, Any]] = []
    evidence_index: dict[str, dict[str, Any]] = {}
    insights: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    charts: list[dict[str, Any]] = []

    for index, contract in enumerate(contracts):
        name = contract["name"]
        series = _aggregate_series(work, contract, "__period").sort_index()
        periods = [str(value) for value in series.index.tolist()]
        values = [round(float(value), 6) for value in series.tolist()]
        latest = values[-1] if values else None
        previous = (
            values[-2]
            if len(values) > 1 and _comparison_enabled(request, "period_over_period")
            else None
        )
        change = _change_pct(latest, previous)
        change_delta = (
            None
            if latest is None or previous is None
            else round(float(latest) - float(previous), 6)
        )
        yoy_previous = None
        yoy_change = None
        if periods and _comparison_enabled(request, "year_over_year"):
            latest_period = periods[-1]
            yoy_label = _year_over_year_label(
                latest_period, request.period_type, request.week_start
            )
            if yoy_label in periods:
                yoy_previous = values[periods.index(yoy_label)]
                yoy_change = _change_pct(latest, yoy_previous)
        total = _aggregate_total(work, contract)
        evidence_id = f"metric:{name}:trend"
        metric = {
            "metric_id": contract["metric_id"],
            "total": total,
            "latest": latest,
            "previous": previous,
            "change_pct": change,
            "change_delta": change_delta,
            "yoy_previous": yoy_previous,
            "yoy_change_pct": yoy_change,
            "periods": periods,
            "values": values,
            "unit": contract["unit"],
            "evidence_id": evidence_id,
        }
        metrics[name] = metric
        direction = str(contract.get("direction", "neutral"))
        if change is None or direction == "neutral" or change == 0:
            status = "neutral"
        elif (direction == "higher_is_better" and change > 0) or (
            direction == "lower_is_better" and change < 0
        ):
            status = "positive"
        else:
            status = "negative"
        kpis.append(
            {
                "kpi_id": f"kpi-{index + 1:02d}",
                "name": name,
                "display_name": contract["display_name"],
                "value": latest,
                "previous_value": previous,
                "total": total,
                "change_pct": change,
                "change_delta": change_delta,
                "yoy_change_pct": yoy_change,
                "unit": contract["unit"],
                "role": contract["role"],
                "direction": direction,
                "status": status,
                "evidence_ids": [evidence_id],
            }
        )
        evidence_index[evidence_id] = {
            "evidence_id": evidence_id,
            "kind": "metric_trend",
            "scope_id": metric_scope(work, contract),
            "scope_bindings": {"periods": {
                period: metric_scope(work.loc[work["__period"].astype(str) == period], contract)
                for period in periods
            }},
            "metric": name,
            "periods": periods,
            "values": values,
            "formula": contract["formula"],
            "filter_scope": _provenance_scope(contract, periods=periods),
            "sample_count": int(_source_valid_mask(work, contract).sum()),
            "observation_count": len(values),
            "provenance_source": "analysis_engine",
        }
        statement = _finding_text(name, change)
        insight = {
            "insight_id": f"insight-{index + 1:02d}",
            "statement": statement,
            # This is a deterministic metric fact backed by its just-created
            # evidence record, so it may satisfy the explicit answer contract.
            "answer_text": statement,
            "resolved_answer": statement,
            "answer_status": "answered",
            "evidence_strength": "high",
            "kind": "fact",
            "confidence": "high",
            # A metric fact establishes direction only.  It must not masquerade
            # as a completed driver diagnosis or hand a table-contained drill
            # down back to the reader.
            "implication": "",
            "display_priority": "supporting",
            "presentation_role": "supporting",
            "value_score": 1,
            "actionable": False,
            "evidence_ids": [evidence_id],
        }
        insights.append(insight)
        findings.append({"text": statement, "evidence_ids": [evidence_id]})
        if index < 3:
            takeaway = _finding_text(name, change)
            charts.append(
                {
                    "chart_id": f"chart-trend-{index + 1:02d}",
                    "chart_type": "line",
                    "title": f"{contract['display_name']}周期趋势",
                    "editable": True,
                    "aspect_ratio": 2.35,
                    "categories": periods,
                    "series": [{"name": contract["display_name"], "values": values}],
                    "evidence_ids": [evidence_id],
                    **_chart_display_contract(
                        contract,
                        values,
                        scope_label=_analysis_window_label(periods, request.period_type),
                        takeaway=takeaway,
                    ),
                }
            )

    dimensions: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for dimension in request.dimensions:
        dimension_metrics: dict[str, list[dict[str, Any]]] = {}
        for contract in contracts:
            name = contract["name"]
            rows, semantics = _dimension_summary(work, contract, dimension,
                                                  display_field=display_fields.get(dimension))
            dimension_metrics[name] = rows
            evidence_id = f"dimension:{dimension}:{name}"
            evidence_index[evidence_id] = {
                "evidence_id": evidence_id,
                "kind": "dimension_contribution",
                "scope_id": metric_scope(work, contract, missing_dimensions={"fields": [dimension], "policy": "include_unclassified"}),
                "dimension": dimension,
                "metric": name,
                "rows": rows,
                "semantics": semantics,
                "filter_scope": _provenance_scope(
                    contract, periods=metrics[name]["periods"]
                ),
                "sample_count": int(_source_valid_mask(work, contract).sum()),
                "group_count": len(rows),
                "provenance_source": "analysis_engine",
            }
        dimensions[dimension] = dimension_metrics

    top_contribution_context: dict[str, Any] | None = None
    if request.dimensions and contracts:
        dimension = request.dimensions[0]
        name = contracts[0]["name"]
        rows = dimensions[dimension][name]
        evidence_id = f"dimension:{dimension}:{name}"
        charts.append(
            {
                "chart_id": "chart-dimension-01",
                "chart_type": "bar",
                "title": f"{name}按{dimension}贡献",
                "editable": True,
                "aspect_ratio": 1.85,
                "categories": [row["value"] for row in rows],
                "series": [{"name": name, "values": [row["metric"] for row in rows]}],
                "evidence_ids": [evidence_id],
                **_chart_display_contract(
                    contracts[0],
                    [float(row["metric"]) for row in rows],
                    scope_label=_analysis_window_label(
                        metrics[name]["periods"], request.period_type
                    ),
                    takeaway=(
                        f"{dimension}“{rows[0]['value']}”贡献最高。"
                        if rows
                        else f"按{dimension}比较{name}结构。"
                    ),
                ),
            }
        )
        if rows:
            top = rows[0]
            top_contribution_context = {
                "dimension": dimension,
                "metric": name,
                "value": str(top["value"]),
                "evidence_id": evidence_id,
            }

    dimension_yoy_records: list[dict[str, Any]] = []
    for dimension in request.dimensions:
        for contract in contracts:
            name = contract["name"]
            periods = metrics[name]["periods"]
            if not periods or "year_over_year" not in request.comparisons:
                continue
            latest_period = periods[-1]
            comparison_period = _year_over_year_label(
                latest_period, request.period_type, request.week_start
            )
            if comparison_period not in periods:
                continue
            latest_frame = work[work["__period"].astype(str) == latest_period]
            comparison_frame = work[
                work["__period"].astype(str) == comparison_period
            ]
            latest_values = _aggregate_series(latest_frame, contract, dimension)
            comparison_values = _aggregate_series(
                comparison_frame, contract, dimension
            )
            source_counts = dimension_yoy_source_sample_counts(
                latest_frame=latest_frame,
                comparison_frame=comparison_frame,
                contract=contract,
                dimension=dimension,
            )
            common_values = latest_values.index.intersection(comparison_values.index)
            value_identities = dimension_yoy_value_identities(common_values)
            for value in common_values:
                latest_value = float(latest_values.loc[value])
                comparison_value = float(comparison_values.loc[value])
                change = _change_pct(latest_value, comparison_value)
                delta = latest_value - comparison_value
                value_identity = value_identities[_dimension_value_key(value)]
                display_value = value_identity["display"]
                evidence_id = f"dimension-yoy:{dimension}:{name}:{value}"
                evidence_id += value_identity["evidence_suffix"]
                latest_sample_count = source_counts["latest"].get(
                    _dimension_value_key(value), 0
                )
                comparison_sample_count = source_counts["comparison"].get(
                    _dimension_value_key(value), 0
                )
                record = {
                    "dimension": dimension,
                    "value": display_value,
                    "metric": name,
                    "unit": contract["unit"],
                    "latest": latest_value,
                    "comparison": comparison_value,
                    "change_pct": change,
                    "delta": delta,
                    "latest_period": latest_period,
                    "comparison_period": comparison_period,
                    "evidence_id": evidence_id,
                }
                dimension_yoy_records.append(record)
                evidence_index[evidence_id] = {
                    "evidence_id": evidence_id,
                    "kind": "dimension_yoy",
                    "scope_id": metric_scope(
                        work.loc[work["__period"].astype(str).isin([latest_period, comparison_period]) & work[dimension].eq(value)], contract,
                        filters=[{"field": dimension, "operator": "eq", "value": value.item() if hasattr(value, "item") else value, "comparison": "pandas_typed_equality"}],
                        comparison={"current": [latest_period], "baseline": [comparison_period], "aggregation": "metric_aggregate"},
                    ),
                    **record,
                    "formula": contract["formula"],
                    "filter_scope": _provenance_scope(
                        contract,
                        periods=[latest_period, comparison_period],
                        filters=[(dimension, display_value)],
                    ),
                    "sample_count": latest_sample_count + comparison_sample_count,
                    "sample_counts": {
                        "latest": latest_sample_count,
                        "comparison": comparison_sample_count,
                    },
                    "provenance_source": "analysis_engine",
                }

    # Explicit temporal structure requests need the latest composition and
    # previous-period slices as well as the legacy year-over-year comparison.
    # Calculate them while the confirmed row window is still available; never
    # manufacture these numbers in the proposal compiler or HTML renderer.
    requested_pairs = set()
    for question in getattr(request, "analysis_questions", ()):
        if question.get("comparison_scope") not in (
            "latest_complete_period_vs_prior_period", "latest_complete_vs_previous_and_year_over_year"
        ) or request.incomplete_period_policy not in {"exclude", "exclude_and_note"}:
            continue
        confirmed = set(question.get("confirmed_fields", [])) | set(question.get("required_fields", []))
        if request.date_column not in confirmed:
            continue
        required = set(question.get("required_metrics", []))
        for dimension in question.get("dimensions", []):
            if dimension not in request.dimensions or dimension not in confirmed:
                continue
            for contract in contracts:
                if required and "any_primary_metric" not in required and not required & {contract["name"], contract["metric_id"]}:
                    continue
                requested_pairs.add((dimension, contract["name"]))
    for dimension, name in sorted(requested_pairs):
        contract = next(c for c in contracts if c["name"] == name)
        periods = metrics[name]["periods"]
        if len(periods) < 2:
            continue
        latest_period, previous_period = periods[-1], periods[-2]
        latest_frame = work.loc[work["__period"].astype(str) == latest_period]
        previous_frame = work.loc[work["__period"].astype(str) == previous_period]
        rows, semantics = _dimension_summary(latest_frame, contract, dimension,
                                              display_field=display_fields.get(dimension))
        total = _aggregate_total(latest_frame, contract)
        if contract["aggregation"] == "sum" and total and total > 0 and all(row["metric"] >= 0 for row in rows):
            rows = [{**row, "share": row["metric"] / total} for row in rows]
        ref = f"dimension-current:{dimension}:{name}"
        evidence_index[ref] = {
            "evidence_id": ref, "kind": "dimension_contribution", "dimension": dimension,
            "metric": name, "unit": contract["unit"], "periods": [latest_period],
            "scope_id": metric_scope(latest_frame, contract, missing_dimensions={"fields": [dimension], "policy": "include_unclassified"}),
            "rows": rows, "semantics": semantics, "formula": contract["formula"],
            "filter_scope": _provenance_scope(contract, periods=[latest_period]),
            "sample_count": int(_source_valid_mask(latest_frame, contract).sum()),
            "group_count": len(rows), "provenance_source": "analysis_engine",
        }
        current_values = _aggregate_series(latest_frame, contract, dimension)
        previous_values = _aggregate_series(previous_frame, contract, dimension)
        common = current_values.dropna().index.intersection(previous_values.dropna().index)
        identities = dimension_yoy_value_identities(common)
        for value in common:
            identity = identities[_dimension_value_key(value)]
            current_rows = latest_frame.loc[latest_frame[dimension].eq(value)]
            prior_rows = previous_frame.loc[previous_frame[dimension].eq(value)]
            current, previous = float(current_values.loc[value]), float(previous_values.loc[value])
            ref = f"dimension-pop:{dimension}:{name}:{value}" + identity["evidence_suffix"]
            counts = {"latest": int(_source_valid_mask(current_rows, contract).sum()),
                      "comparison": int(_source_valid_mask(prior_rows, contract).sum())}
            record = {"evidence_id": ref, "kind": "dimension_yoy", "dimension": dimension,
                "value": identity["display"], "metric": name, "unit": contract["unit"],
                "latest": current, "comparison": previous, "delta": current - previous,
                "change_pct": _change_pct(current, previous), "latest_period": latest_period,
                "comparison_period": previous_period, "formula": contract["formula"],
                "sample_counts": counts, "sample_count": sum(counts.values()),
                "scope_id": metric_scope(pd.concat([current_rows, prior_rows]), contract,
                    filters=[{"field": dimension, "operator": "eq", "value": value.item() if hasattr(value, "item") else value, "comparison": "pandas_typed_equality"}],
                    comparison={"current": [latest_period], "baseline": [previous_period], "aggregation": "metric_aggregate"}),
                "filter_scope": _provenance_scope(contract, periods=[latest_period, previous_period], filters=[(dimension, identity["display"])]),
                "provenance_source": "analysis_engine"}
            if contract["aggregation"] == "ratio":
                record["ratio_components"] = {}
                for role, source_rows in (("latest", current_rows), ("comparison", prior_rows)):
                    valid = source_rows.loc[_source_valid_mask(source_rows, contract)]
                    record["ratio_components"][role] = {
                        "numerator": float(valid[contract["numerator"]].sum()),
                        "denominator": float(valid[contract["denominator"]].sum())}
            evidence_index[ref] = record

    diagnostic_insights: list[dict[str, Any]] = []
    targeted_actions: list[dict[str, Any]] = []
    covered_metrics: set[str] = set()

    def add_diagnostic(
        *,
        headline: str,
        statement: str,
        implication: str,
        evidence_ids: list[str],
        action_headline: str,
        action_text: str,
        verification_signal: str,
        action_target: str,
        action_dimensions: list[str],
        metric_name: str,
        signal_type: str,
        display_label: str,
        title_clause: str,
        action_mode: str = "controlled_test",
    ) -> None:
        insight_id = f"diagnostic-{len(diagnostic_insights) + 1:02d}"
        diagnostic_insights.append(
            {
                "insight_id": insight_id,
                "headline": headline,
                "statement": statement,
                # `statement` is retained for rendering, while these explicit
                # fields make the evidence-backed diagnostic consumable by the
                # value selector without granting that privilege to arbitrary
                # legacy statements.
                "answer_text": statement,
                "resolved_answer": statement,
                "answer_status": "answered",
                "evidence_strength": "high",
                "kind": "diagnostic",
                "signal_type": signal_type,
                "display_label": display_label,
                "title_clause": title_clause,
                "metric_name": metric_name,
                "display_priority": "primary",
                "presentation_role": "featured",
                "value_score": 5,
                "actionable": True,
                "confidence": "high",
                "implication": implication,
                "evidence_ids": list(dict.fromkeys(evidence_ids)),
            }
        )
        # Actions use only observed metrics with confirmed directions. A
        # diagnostic is evidence for a trial, never proof that its mechanism works.
        observed_metrics = {
            str(evidence_index[eid].get("metric"))
            for eid in evidence_ids if eid in evidence_index
            and str(evidence_index[eid].get("value", "")) == action_target
        }
        guard_metrics = [
            contract for contract in contracts
            if contract["name"] in observed_metrics and contract["name"] != metric_name
            and contract.get("role") in {"conversion", "quality", "efficiency"}
            and contract.get("direction") in {"higher_is_better", "lower_is_better"}
        ]
        favorable = "高于" if contract_by_name[metric_name].get("direction") == "higher_is_better" else "低于"
        unfavorable = "低于" if favorable == "高于" else "高于"
        stable = "、".join(
            f"{display_metric_name(contract['name'])}{'不低于' if contract['direction'] == 'higher_is_better' else '不高于'}试验前"
            for contract in guard_metrics
        )
        stop = "或".join(
            f"{display_metric_name(contract['name'])}{'下降' if contract['direction'] == 'higher_is_better' else '上升'}"
            for contract in guard_metrics
        )
        limitations = ["观察到的结构差异不证明资源调整的因果效果；对象或统计口径不可比时不作效果归因。"]
        if action_mode == "data_governance":
            typed_action = {
                "action_type": "data_governance",
                "rationale": "先补足业务原因与口径核验，避免把聚合异常直接当作原因并实施错误治理。",
                "steps": [f"在{action_target}已定位的切面核对原始记录、统计口径与业务原因。",
                          "保留可追溯的例外依据，确认原因后再小范围治理，并复核下一完整周期。"],
                "success_signal": f"例外记录与原因可追溯、口径核对完成；下一完整周期{metric_name}{favorable}治理前。",
                "guardrails": ["业务原因未核实则暂停原因归属与扩大治理；口径不一致时停止跨期效果比较。"],
                "limitations": ["现有聚合仅定位异常切面，缺少业务原因时不能完成原因归因。"],
            }
        elif not guard_metrics:
            typed_action = {
                "action_type": "monitor",
                "headline": f"监控{action_target}的{metric_name}并补足质量边界",
                "text": f"下一完整周期{metric_name}{unfavorable}本期则暂停扩大资源，并复核同口径结构。",
                "rationale": "当前缺少可确认方向的质量或效率护栏，规模变化不足以授权放量试验。",
                "steps": [f"按相同范围记录{action_target}下一完整周期的{metric_name}。",
                          f"若{metric_name}{unfavorable}本期，暂停扩大资源并复核对象结构；补足质量口径后再决定试验。"],
                "success_signal": f"{metric_name}未向不利方向变化；质量边界确认后再评估是否进入试验。",
                "guardrails": [f"{metric_name}{unfavorable}本期则暂停扩大资源；未补足质量证据不得因规模增长直接放量。"],
                "limitations": ["缺少可确认方向的质量或效率证据，当前只支持监控与补证据。"],
            }
        else:
            typed_action = {
                "action_type": "controlled_test",
                "rationale": f"待验证假设：在可比对象内小范围调整资源配置，能使{metric_name}{favorable}试验前且不损伤质量与效率。",
                "steps": [f"在{action_target}已定位的独立切面选择可比对象，记录试验前指标并保留未调整对照。",
                          "仅在小范围调整资源配置；下一完整周期比较试验组与对照，达到成功条件后再分层扩大。"],
                "success_signal": f"下一完整周期可比试验对象的{metric_name}{favorable}试验前，且{stable}；同步核对未调整对照。",
                "guardrails": [f"{stop}则暂停扩展并恢复到试验前配置；对象或口径不可比时停止效果归因。"],
                "limitations": limitations,
            }
        targeted_actions.append(
            {
                "action_id": f"action-diagnostic-{len(targeted_actions) + 1:02d}",
                "priority": len(targeted_actions) + 1,
                "headline": action_headline,
                "text": action_text,
                "rationale": statement,
                "target": action_target,
                "analysis_dimensions": list(dict.fromkeys(action_dimensions)),
                "source_insight_ids": [insight_id],
                "evidence_ids": list(dict.fromkeys(evidence_ids)),
                **typed_action,
                "verification_signal": typed_action["success_signal"],
            }
        )
        covered_metrics.add(metric_name)

    contract_by_name = {str(contract["name"]): contract for contract in contracts}
    channel_dimension = next(
        (value for value in request.dimensions if "渠道" in value), None
    ) if is_retail_growth else None
    category_dimension = next(
        (value for value in request.dimensions if "品类" in value), None
    ) if is_retail_growth else None
    revenue_name = _first_metric_name(contracts, ("收入", "revenue", "gmv"))
    roas_name = _first_metric_name(contracts, ("roas", "投入产出"))
    refund_name = _first_metric_name(contracts, ("退款率", "refund rate"))
    order_name = _first_metric_name(contracts, ("订单", "orders"))
    conversion_name = _first_metric_name(contracts, ("转化率", "conversion"))
    cost_name = _first_metric_name(contracts, ("营销成本", "成本", "cost"))
    user_dimension = next(
        (
            value
            for value in request.dimensions
            if "用户" in value or "层级" in value or "user" in value.lower()
        ),
        None,
    ) if is_retail_growth else None
    region_dimension = next(
        (
            value
            for value in request.dimensions
            if "区域" in value or "地区" in value or "region" in value.lower()
        ),
        None,
    ) if is_retail_growth else None

    def display_metric_name(name: str | None) -> str:
        if not name:
            return "指标"
        return str(contract_by_name.get(name, {}).get("display_name") or name)

    def dimension_record(
        dimension: str, value: str, metric_name: str | None
    ) -> dict[str, Any] | None:
        if not metric_name:
            return None
        return next(
            (
                item
                for item in dimension_yoy_records
                if item["dimension"] == dimension
                and item["value"] == value
                and item["metric"] == metric_name
            ),
            None,
        )

    def change_fragment(record: dict[str, Any] | None) -> str | None:
        if not record or record.get("change_pct") is None:
            return None
        display_name = display_metric_name(str(record["metric"]))
        if str(record.get("unit")) == "%":
            delta = float(record["delta"])
            verb = "上升" if delta > 0 else "下降" if delta < 0 else "持平"
            return f"{display_name}{verb}{abs(delta):.2f}个百分点"
        change = float(record["change_pct"])
        verb = "增长" if change > 0 else "下降" if change < 0 else "持平"
        return f"{display_name}{verb}{abs(change):.1f}%"

    def build_slice_yoy_record(
        *,
        primary_dimension: str,
        primary_value: str,
        secondary_dimension: str,
        secondary_value: str,
        metric_name: str,
        latest_period: str,
        comparison_period: str,
    ) -> dict[str, Any] | None:
        contract = contract_by_name[metric_name]
        latest_frame = work[work["__period"].astype(str) == latest_period]
        comparison_frame = work[
            work["__period"].astype(str) == comparison_period
        ]
        for field, value in (
            (primary_dimension, primary_value),
            (secondary_dimension, secondary_value),
        ):
            latest_frame = latest_frame[latest_frame[field].astype(str) == value]
            comparison_frame = comparison_frame[
                comparison_frame[field].astype(str) == value
            ]
        latest_value = _aggregate_total(latest_frame, contract)
        comparison_value = _aggregate_total(comparison_frame, contract)
        if latest_value is None or comparison_value is None:
            return None
        evidence_id = (
            f"dimension-slice-yoy:{primary_dimension}:{primary_value}:"
            f"{secondary_dimension}:{secondary_value}:{metric_name}"
        )
        record = {
            "dimension": primary_dimension,
            "value": primary_value,
            "secondary_dimension": secondary_dimension,
            "secondary_value": secondary_value,
            "metric": metric_name,
            "unit": contract["unit"],
            "latest": float(latest_value),
            "comparison": float(comparison_value),
            "change_pct": _change_pct(float(latest_value), float(comparison_value)),
            "delta": float(latest_value) - float(comparison_value),
            "latest_period": latest_period,
            "comparison_period": comparison_period,
            "evidence_id": evidence_id,
        }
        evidence_index[evidence_id] = {
            "evidence_id": evidence_id,
            "kind": "dimension_slice_yoy",
            "scope_id": metric_scope(
                pd.concat([latest_frame, comparison_frame]), contract,
                filters=[{"field": field, "operator": "eq", "value": value, "comparison": "string_equality"}
                         for field, value in ((primary_dimension, primary_value), (secondary_dimension, secondary_value))],
                comparison={"current": [latest_period], "baseline": [comparison_period], "aggregation": "metric_aggregate"},
            ),
            **record,
            "formula": contract["formula"],
            "filter_scope": _provenance_scope(
                contract,
                periods=[latest_period, comparison_period],
                filters=[
                    (primary_dimension, primary_value),
                    (secondary_dimension, secondary_value),
                ],
            ),
            "sample_count": int(
                _source_valid_mask(latest_frame, contract).sum()
                + _source_valid_mask(comparison_frame, contract).sum()
            ),
            "sample_counts": {
                "latest": int(_source_valid_mask(latest_frame, contract).sum()),
                "comparison": int(_source_valid_mask(comparison_frame, contract).sum()),
            },
            "provenance_source": "analysis_engine",
        }
        return record

    def select_dimension_slices(
        *,
        primary_dimension: str,
        primary_value: str,
        secondary_dimensions: list[str],
        metric_name: str,
        latest_period: str,
        comparison_period: str,
        prefer: str,
    ) -> list[dict[str, Any]]:
        """Resolve one evidence-backed, decision-relevant slice per lens."""

        selected: list[dict[str, Any]] = []
        period_work = work[
            work["__period"].astype(str).isin([latest_period, comparison_period])
            & (work[primary_dimension].astype(str) == primary_value)
        ]
        for secondary_dimension in secondary_dimensions:
            candidates: list[dict[str, Any]] = []
            grouped = period_work.groupby(
                ["__period", secondary_dimension], dropna=True, sort=False
            )
            period_groups = {
                (str(period), str(value)): group
                for (period, value), group in grouped
            }
            candidate_values = sorted({
                value for period, value in period_groups
                if period == latest_period
            } & {
                value for period, value in period_groups
                if period == comparison_period
            })
            contract = contract_by_name[metric_name]
            for secondary_value in candidate_values:
                latest_value = _aggregate_total(
                    period_groups[(latest_period, secondary_value)], contract
                )
                comparison_value = _aggregate_total(
                    period_groups[(comparison_period, secondary_value)], contract
                )
                if latest_value is None or comparison_value is None:
                    continue
                change_pct = _change_pct(float(latest_value), float(comparison_value))
                if change_pct is not None:
                    candidates.append({
                        "secondary_value": secondary_value,
                        "change_pct": change_pct,
                    })
            if candidates:
                chosen = (
                    min(candidates, key=lambda item: float(item["change_pct"]))
                    if prefer == "lowest"
                    else max(candidates, key=lambda item: float(item["change_pct"]))
                )
                record = build_slice_yoy_record(
                    primary_dimension=primary_dimension,
                    primary_value=primary_value,
                    secondary_dimension=secondary_dimension,
                    secondary_value=str(chosen["secondary_value"]),
                    metric_name=metric_name,
                    latest_period=latest_period,
                    comparison_period=comparison_period,
                )
                if record is not None:
                    selected.append(record)
        return selected

    def actual_period_pair(record: dict[str, Any]) -> tuple[str, str]:
        return (
            _display_period_label(str(record["latest_period"]), request.period_type),
            _display_period_label(
                str(record["comparison_period"]), request.period_type
            ),
        )

    def is_unfavorable(record: dict[str, Any]) -> bool:
        contract = contract_by_name.get(str(record.get("metric")), {})
        direction = str(contract.get("direction", "neutral"))
        change = (
            float(record.get("delta", 0.0))
            if str(record.get("unit")) == "%"
            else float(record.get("change_pct", 0.0))
        )
        return (direction == "higher_is_better" and change < 0) or (
            direction == "lower_is_better" and change > 0
        )

    if top_contribution_context:
        top_dimension = str(top_contribution_context["dimension"])
        top_value = str(top_contribution_context["value"])
        top_metric = str(top_contribution_context["metric"])
        primary_record = dimension_record(top_dimension, top_value, top_metric)
        role_order = {"conversion": 0, "quality": 1, "cost": 2, "efficiency": 3}
        related_records = [
            record
            for record in dimension_yoy_records
            if record["dimension"] == top_dimension
            and record["value"] == top_value
            and record["metric"] != top_metric
            and contract_by_name.get(str(record["metric"]), {}).get("role")
            in role_order
        ]
        related_records.sort(
            key=lambda record: role_order[
                str(contract_by_name[str(record["metric"])]["role"])
            ]
        )
        related_fragments = [
            fragment
            for fragment in (change_fragment(record) for record in related_records)
            if fragment
        ]
        analysis_label = _analysis_window_label(
            list(metrics[top_metric].get("periods", [])), request.period_type
        )
        statement = (
            f"{analysis_label}，{top_dimension}“{top_value}”对"
            f"{display_metric_name(top_metric)}贡献最高。"
        )
        if primary_record:
            latest_label, comparison_period_label = actual_period_pair(primary_record)
            statement = (
                statement[:-1]
                + f"；{latest_label}较{comparison_period_label}，"
                + f"{change_fragment(primary_record)}。"
            )
        if related_fragments:
            detail_text = "、".join(related_fragments)
            if sum(is_unfavorable(record) for record in related_records) >= 2:
                implication = (
                    f"同期{detail_text}，规模贡献领先，但质量与效率没有同步改善。"
                )
            elif any(is_unfavorable(record) for record in related_records):
                implication = f"同期{detail_text}，规模贡献领先，但综合表现存在短板。"
            else:
                implication = f"同期{detail_text}，规模与综合表现同步改善。"
        else:
            implication = "当前表缺少可用于成本、质量或效率交叉分析的同比指标。"
        top_evidence_ids = [str(top_contribution_context["evidence_id"])]
        if primary_record:
            top_evidence_ids.append(str(primary_record["evidence_id"]))
        top_evidence_ids.extend(
            str(record["evidence_id"]) for record in related_records
        )
        insights.append(
            {
                "insight_id": f"insight-{len(insights) + 1:02d}",
                "headline": f"{top_value}是{display_metric_name(top_metric)}最大贡献项",
                "statement": statement,
                "answer_text": statement,
                "resolved_answer": statement,
                "answer_status": "answered",
                "evidence_strength": "high" if related_records else "medium",
                "kind": "inference",
                "presentation_role": "featured",
                "value_score": 4,
                "actionable": False,
                "confidence": "high" if related_records else "medium",
                "implication": implication,
                "evidence_ids": list(dict.fromkeys(top_evidence_ids)),
            }
        )

    if channel_dimension and roas_name:
        candidates = [
            row
            for row in dimension_yoy_records
            if row["dimension"] == channel_dimension
            and row["metric"] == roas_name
            and row["change_pct"] is not None
            and row["change_pct"] < 0
        ]
        if candidates:
            row = min(candidates, key=lambda value: float(value["change_pct"]))
            latest_label, comparison_period_label = actual_period_pair(row)
            supporting = [
                dimension_record(channel_dimension, row["value"], metric_name)
                for metric_name in (revenue_name, conversion_name, refund_name, cost_name)
            ]
            supporting = [value for value in supporting if value]
            supporting_fragments = [
                value for value in (change_fragment(item) for item in supporting) if value
            ]
            roas_display = display_metric_name(roas_name)
            overall_roas = metrics[roas_name].get("latest")
            benchmark_text = (
                f"；同期全渠道为{float(overall_roas):.2f}倍"
                if overall_roas is not None
                else ""
            )
            paid_dimensions = [
                value for value in (category_dimension, region_dimension, user_dimension)
                if value
            ]
            paid_slice_records = select_dimension_slices(
                primary_dimension=channel_dimension,
                primary_value=str(row["value"]),
                secondary_dimensions=paid_dimensions,
                metric_name=roas_name,
                latest_period=str(row["latest_period"]),
                comparison_period=str(row["comparison_period"]),
                prefer="lowest",
            )
            paid_slice_text = "、".join(
                f"{item['secondary_dimension']}“{item['secondary_value']}”"
                for item in paid_slice_records
            )
            add_diagnostic(
                headline=(
                    f"{latest_label}{row['value']}{roas_name}较{comparison_period_label}下降"
                    f"{abs(float(row['change_pct'])):.1f}%"
                ),
                statement=(
                    f"{latest_label}较{comparison_period_label}，"
                    f"{channel_dimension}“{row['value']}”的{roas_display}下降"
                    f"{abs(float(row['change_pct'])):.1f}%，当前为{row['latest']:.2f}倍"
                    f"{benchmark_text}。"
                ),
                implication=(
                    f"{row['value']}{'、'.join(supporting_fragments[:3])}，"
                    "效率压力来自量质表现共同承压，不宜继续惯性扩量。"
                ),
                evidence_ids=[
                    row["evidence_id"],
                    *[item["evidence_id"] for item in supporting],
                    *[item["evidence_id"] for item in paid_slice_records],
                ],
                action_headline=f"暂停{row['value']}惯性扩量；修复转化与{roas_name}后再恢复预算。",
                action_text=(
                    f"暂停{row['value']}的惯性扩量；对{paid_slice_text or row['value']}等独立切面"
                    f"分别复核并治理，每个切面均以对应证据确认后再收缩；{roas_name}与转化率连续改善后再分阶段恢复预算。"
                ),
                verification_signal=f"{row['value']}的{roas_name}与转化率连续两个周期回升",
                action_target=str(row["value"]),
                action_dimensions=paid_dimensions,
                metric_name=roas_name,
                signal_type="risk",
                display_label="效率风险",
                title_clause=f"{row['value']}投放效率承压",
            )

    if channel_dimension and revenue_name:
        candidates = [
            row
            for row in dimension_yoy_records
            if row["dimension"] == channel_dimension
            and row["metric"] == revenue_name
            and row["change_pct"] is not None
            and row["change_pct"] > 0
        ]
        if candidates:
            row = max(candidates, key=lambda value: float(value["change_pct"]))
            latest_label, comparison_period_label = actual_period_pair(row)
            supporting = [
                dimension_record(channel_dimension, row["value"], metric_name)
                for metric_name in (conversion_name, roas_name, refund_name)
            ]
            supporting = [value for value in supporting if value]
            slice_records: list[dict[str, Any]] = []
            if user_dimension:
                user_values = [
                    str(value)
                    for value in work[user_dimension].dropna().astype(str).unique()
                ]
                new_user_value = next(
                    (value for value in user_values if "新" in value or "new" in value.lower()),
                    None,
                )
                if new_user_value:
                    for metric_name in (
                        revenue_name,
                        conversion_name,
                        refund_name,
                        roas_name,
                    ):
                        if not metric_name:
                            continue
                        record = build_slice_yoy_record(
                            primary_dimension=channel_dimension,
                            primary_value=str(row["value"]),
                            secondary_dimension=user_dimension,
                            secondary_value=new_user_value,
                            metric_name=metric_name,
                            latest_period=str(row["latest_period"]),
                            comparison_period=str(row["comparison_period"]),
                        )
                        if record:
                            slice_records.append(record)
            fragments = [
                value for value in (change_fragment(item) for item in supporting) if value
            ]
            new_user_refund = next(
                (item for item in slice_records if item["metric"] == refund_name),
                None,
            )
            new_user_fragment = change_fragment(new_user_refund)
            new_user_note = f"；新用户{new_user_fragment}" if new_user_fragment else ""
            content_dimensions = [
                value for value in (category_dimension, region_dimension, user_dimension)
                if value
            ]
            content_slice_records = select_dimension_slices(
                primary_dimension=channel_dimension,
                primary_value=str(row["value"]),
                secondary_dimensions=content_dimensions,
                metric_name=revenue_name,
                latest_period=str(row["latest_period"]),
                comparison_period=str(row["comparison_period"]),
                prefer="highest",
            )
            content_slice_text = "、".join(
                f"{item['secondary_dimension']}“{item['secondary_value']}”"
                for item in content_slice_records
            )
            add_diagnostic(
                headline=(
                    f"{latest_label}{row['value']}{revenue_name}较{comparison_period_label}增长"
                    f"{float(row['change_pct']):.1f}%"
                ),
                statement=(
                    f"{latest_label}较{comparison_period_label}，"
                    f"{channel_dimension}“{row['value']}”的{revenue_name}增长"
                    f"{float(row['change_pct']):.1f}%，是当前最强的结构性增长机会。"
                ),
                implication=(
                    f"{row['value']}{'、'.join(fragments)}{new_user_note}，"
                    "增长动能成立，但收入质量仍需同步控制。"
                ),
                evidence_ids=[
                    row["evidence_id"],
                    *[item["evidence_id"] for item in supporting],
                    *[item["evidence_id"] for item in slice_records],
                    *[item["evidence_id"] for item in content_slice_records],
                ],
                action_headline=f"{row['value']}先做分层放量，并用转化、退款和投入产出设置止损线。",
                action_text=(
                    f"为{row['value']}在{content_slice_text or row['value']}等独立增长切面分别开展小规模测试，"
                    "每个切面均以对应证据复核后再分层放量，并同步设置转化率、退款率和投入产出止损线。"
                ),
                verification_signal=f"{row['value']}放量后{revenue_name}增长且效率指标不恶化",
                action_target=str(row["value"]),
                action_dimensions=content_dimensions,
                metric_name=revenue_name,
                signal_type="opportunity",
                display_label="增长机会",
                title_clause=f"{row['value']}驱动增长",
            )

    if category_dimension and refund_name:
        candidates = [
            row
            for row in dimension_yoy_records
            if row["dimension"] == category_dimension
            and row["metric"] == refund_name
            and row["delta"] > 0
        ]
        if candidates:
            row = max(candidates, key=lambda value: float(value["delta"]))
            latest_label, comparison_period_label = actual_period_pair(row)
            refund_slice_records: list[dict[str, Any]] = []
            for secondary_dimension in (
                channel_dimension,
                region_dimension,
                user_dimension,
            ):
                if not secondary_dimension:
                    continue
                dimension_records: list[dict[str, Any]] = []
                for secondary_value in sorted(
                    str(value)
                    for value in work[secondary_dimension].dropna().unique()
                ):
                    record = build_slice_yoy_record(
                        primary_dimension=category_dimension,
                        primary_value=str(row["value"]),
                        secondary_dimension=secondary_dimension,
                        secondary_value=secondary_value,
                        metric_name=refund_name,
                        latest_period=str(row["latest_period"]),
                        comparison_period=str(row["comparison_period"]),
                    )
                    if record and float(record.get("delta") or 0) > 0:
                        dimension_records.append(record)
                if dimension_records:
                    refund_slice_records.append(
                        max(
                            dimension_records,
                            key=lambda item: float(item.get("delta") or 0),
                        )
                    )
            refund_dimensions = [
                str(item["secondary_dimension"])
                for item in refund_slice_records
            ]
            refund_dimension_text = "、".join(refund_dimensions) or category_dimension
            concentration_text = "、".join(
                f"{item['secondary_dimension']}“{item['secondary_value']}”上升"
                f"{float(item['delta']):.1f}个百分点"
                for item in refund_slice_records
            )
            implication = (
                f"{row['value']}退款抬升在{concentration_text}的细分范围更突出；"
                "现有表已完成结构定位，但缺少退款原因或商品明细，不能归因具体原因。"
                if concentration_text
                else "现有表可确认品类风险，但缺少可用交叉维度、退款原因或商品明细。"
            )
            add_diagnostic(
                headline=(
                    f"{latest_label}{row['value']}{refund_name}较{comparison_period_label}上升"
                    f"{float(row['delta']):.1f}个百分点"
                ),
                statement=(
                    f"{latest_label}较{comparison_period_label}，"
                    f"{category_dimension}“{row['value']}”的{refund_name}上升"
                    f"{float(row['delta']):.1f}个百分点，收入质量风险显著抬升。"
                ),
                implication=implication,
                evidence_ids=[
                    row["evidence_id"],
                    *[item["evidence_id"] for item in refund_slice_records],
                ],
                action_headline=f"{row['value']}先定位退款集中区，再补充原因字段完成治理闭环。",
                action_text=(
                    f"优先治理{row['value']}在{refund_dimension_text}已定位的高风险细分范围；"
                    "如需归因具体原因，再补充退款原因或商品明细字段。"
                ),
                verification_signal=f"{row['value']}的{refund_name}连续两个周期回落",
                action_target=str(row["value"]),
                action_dimensions=refund_dimensions,
                metric_name=refund_name,
                signal_type="risk",
                display_label="质量风险",
                title_clause=f"{row['value']}退款风险抬升",
                action_mode="data_governance",
            )
            chart_rows = [
                value
                for value in dimension_yoy_records
                if value["dimension"] == category_dimension
                and value["metric"] == refund_name
            ]
            chart_rows.sort(key=lambda value: float(value["latest"]), reverse=True)
            if chart_rows:
                charts.append(
                    {
                        "chart_id": "chart-diagnostic-refund-category",
                        "chart_type": "bar",
                        "title": f"{refund_name}按{category_dimension}同比对比",
                        "editable": True,
                        "aspect_ratio": 1.65,
                        "categories": [value["value"] for value in chart_rows],
                        "series": [
                            {
                                "name": chart_rows[0]["latest_period"],
                                "values": [value["latest"] for value in chart_rows],
                            },
                            {
                                "name": chart_rows[0]["comparison_period"],
                                "values": [
                                    value["comparison"] for value in chart_rows
                                ],
                            },
                        ],
                        "evidence_ids": [
                            value["evidence_id"] for value in chart_rows
                        ],
                        **_chart_display_contract(
                            contract_by_name[refund_name],
                            [
                                float(value)
                                for row_value in chart_rows
                                for value in (row_value["latest"], row_value["comparison"])
                            ],
                            scope_label=(
                                f"{_display_period_label(chart_rows[0]['latest_period'], request.period_type)}"
                                f" vs {_display_period_label(chart_rows[0]['comparison_period'], request.period_type)}"
                            ),
                            takeaway=f"{row['value']}{refund_name}风险最突出。",
                        ),
                    }
                )

    if is_retail_growth and request.period_type == "monthly" and revenue_name:
        revenue_metric = metrics[revenue_name]
        period_value_pairs = list(
            zip(revenue_metric["periods"], revenue_metric["values"])
        )
        candidate_years = sorted({period[:4] for period, _ in period_value_pairs}, reverse=True)
        complete_q4_suffixes = {"-10", "-11", "-12"}
        complete_h1_suffixes = {"-01", "-02", "-03", "-04", "-05", "-06"}
        latest_year = next(
            (
                year
                for year in candidate_years
                if {
                    period[-3:] for period, _ in period_value_pairs
                    if period.startswith(year)
                } >= complete_q4_suffixes | complete_h1_suffixes
            ),
            "",
        )

        year_end_pairs = [
            (period, value)
            for period, value in period_value_pairs
            if period.startswith(latest_year) and period[-3:] in complete_q4_suffixes
        ]
        regular_pairs = [
            (period, value)
            for period, value in period_value_pairs
            if period.startswith(latest_year) and period[-3:] in complete_h1_suffixes
        ]
        if latest_year and year_end_pairs and regular_pairs:
            peak_average = sum(float(value) for _, value in year_end_pairs) / len(
                year_end_pairs
            )
            regular_average = sum(float(value) for _, value in regular_pairs) / len(
                regular_pairs
            )
            uplift = _change_pct(peak_average, regular_average)
            if uplift is not None and uplift >= 20:
                evidence_id = f"seasonality:{revenue_name}:year-end"
                revenue_contract = contract_by_name[revenue_name]
                peak_periods = [period for period, _ in year_end_pairs]
                baseline_periods = [period for period, _ in regular_pairs]
                peak_frame = work[work["__period"].astype(str).isin(peak_periods)]
                baseline_frame = work[work["__period"].astype(str).isin(baseline_periods)]
                evidence_index[evidence_id] = {
                    "evidence_id": evidence_id,
                    "kind": "seasonality",
                    "scope_id": metric_scope(
                        pd.concat([peak_frame, baseline_frame]), revenue_contract,
                        comparison={"current": peak_periods, "baseline": baseline_periods, "aggregation": "monthly_mean"},
                    ),
                    "metric": revenue_name,
                    "latest": peak_average,
                    "comparison": regular_average,
                    "change_pct": uplift,
                    "periods": peak_periods,
                    "comparison_periods": baseline_periods,
                    "formula": revenue_contract["formula"],
                    "filter_scope": (
                        f"旺季窗口：{latest_year}年Q4（{'、'.join(peak_periods)}）；"
                        f"基线窗口：{latest_year}年H1（{'、'.join(baseline_periods)}）；"
                        f"{_calculation_exclusion_note(revenue_contract)}"
                    ),
                    "sample_count": int(
                        _source_valid_mask(peak_frame, revenue_contract).sum()
                        + _source_valid_mask(baseline_frame, revenue_contract).sum()
                    ),
                    "sample_counts": {
                        "latest": int(_source_valid_mask(peak_frame, revenue_contract).sum()),
                        "comparison": int(_source_valid_mask(baseline_frame, revenue_contract).sum()),
                    },
                    "observation_count": len(peak_periods) + len(baseline_periods),
                    "provenance_source": "analysis_engine",
                }
                for chart in charts:
                    if chart.get("chart_id") == "chart-trend-01":
                        chart["evidence_ids"] = list(
                            dict.fromkeys([*chart["evidence_ids"], evidence_id])
                        )
                add_diagnostic(
                    headline=f"年末旺季{revenue_name}显著抬升，资源需要提前联动",
                    statement=(
                        f"年末旺季的{revenue_name}月均较常态高{uplift:.1f}%，"
                        "备货、预算与履约容量需要提前联动。"
                    ),
                    implication="旺季增长具有季节性，不能把峰值直接外推为常态基线。",
                    evidence_ids=[evidence_id],
                    action_headline="提前六周联动旺季备货、预算与履约，并规划峰值后的库存回落。",
                    action_text="提前六周滚动校准旺季备货、投放预算与履约产能，并设置峰值后的库存回落方案。",
                    verification_signal=f"旺季{revenue_name}达成且退款率、履约时效未突破警戒线",
                    action_target="年末旺季",
                    action_dimensions=[],
                    metric_name=revenue_name,
                    signal_type="seasonality",
                    display_label="季节性",
                    title_clause=f"{revenue_name}呈现明显旺季峰值",
                )

    existing_chart_evidence = {
        evidence_id
        for chart in charts
        for evidence_id in chart.get("evidence_ids", [])
    }
    diagnostic_chart_keys: set[tuple[str, str]] = set()
    for insight in diagnostic_insights:
        matching_records = [
            record
            for record in dimension_yoy_records
            if record["evidence_id"] in set(insight.get("evidence_ids", []))
        ]
        if not matching_records or any(
            record["evidence_id"] in existing_chart_evidence
            for record in matching_records
        ):
            continue
        target = next(
            (
                record
                for record in matching_records
                if str(record["metric"]) == str(insight.get("metric_name"))
            ),
            matching_records[0],
        )
        key = (str(target["dimension"]), str(target["metric"]))
        if key in diagnostic_chart_keys:
            continue
        chart_rows = [
            record
            for record in dimension_yoy_records
            if (str(record["dimension"]), str(record["metric"])) == key
        ]
        chart_rows.sort(key=lambda value: float(value["latest"]), reverse=True)
        if len(chart_rows) < 2:
            continue
        diagnostic_chart_keys.add(key)
        contract = contract_by_name[str(target["metric"])]
        charts.append(
            {
                "chart_id": f"chart-diagnostic-evidence-{len(diagnostic_chart_keys):02d}",
                "chart_type": "bar",
                "title": f"{target['metric']}按{target['dimension']}同比对比",
                "editable": True,
                "aspect_ratio": 1.65,
                "categories": [record["value"] for record in chart_rows],
                "series": [
                    {
                        "name": chart_rows[0]["latest_period"],
                        "values": [record["latest"] for record in chart_rows],
                    },
                    {
                        "name": chart_rows[0]["comparison_period"],
                        "values": [record["comparison"] for record in chart_rows],
                    },
                ],
                "evidence_ids": [record["evidence_id"] for record in chart_rows],
                "supports_insight_ids": [insight["insight_id"]],
                **_chart_display_contract(
                    contract,
                    [
                        float(value)
                        for record in chart_rows
                        for value in (record["latest"], record["comparison"])
                    ],
                    scope_label=(
                        f"{_display_period_label(chart_rows[0]['latest_period'], request.period_type)}"
                        f" vs {_display_period_label(chart_rows[0]['comparison_period'], request.period_type)}"
                    ),
                    takeaway=str(insight.get("headline") or insight["statement"]),
                ),
            }
        )

    if diagnostic_insights:
        insights = diagnostic_insights + insights

    actions: list[dict[str, Any]] = list(targeted_actions)
    for index, contract in enumerate(contracts[: max(3, min(len(contracts), 5))]):
        name = contract["name"]
        if name in covered_metrics:
            continue
        evidence_ids = [f"metric:{name}:trend"]
        if request.dimensions:
            dimension = request.dimensions[index % len(request.dimensions)]
            dimension_evidence_id = f"dimension:{dimension}:{name}"
            evidence_ids.append(dimension_evidence_id)
            dimension_evidence = evidence_index.get(dimension_evidence_id, {})
            visible_rows = [
                row
                for row in dimension_evidence.get("rows", [])
                if not row.get("is_other")
            ]
            top_row = visible_rows[0] if visible_rows else None
            semantics = dimension_evidence.get("semantics", {})
            if top_row and semantics.get("view_type") == "contribution":
                total = metrics[name].get("total")
                share = (
                    float(top_row["metric"]) / float(total)
                    if total not in (None, 0)
                    else None
                )
                share_text = (
                    f"占分析期{name}的{share:.1%}"
                    if share is not None
                    else "是分析期最大贡献项"
                )
                text = (
                    f"优先复核{dimension}“{top_row['value']}”的{name}：其{share_text}；"
                    "对照下一完整周期确认主要贡献项是否延续，并记录结构变化。"
                )
                rationale = (
                    f"现有数据已确认{top_row['value']}是{name}的最大贡献项。"
                )
                verification_signal = (
                    f"下一完整周期{top_row['value']}的{name}贡献占比及整体{name}变化"
                )
            elif top_row:
                direction = str(contract.get("direction", "neutral"))
                interpretation = (
                    "当前风险最高值"
                    if direction == "lower_is_better"
                    else "当前最高表现"
                    if direction == "higher_is_better"
                    else "当前最高值"
                )
                text = (
                    f"优先检查{dimension}“{top_row['value']}”的{name}："
                    f"该项为{interpretation}（{float(top_row['metric']):,.2f}{contract.get('unit', '')}）；"
                    "下一完整周期按同口径复测，确认差异是否收敛。"
                )
                rationale = (
                    f"现有数据已定位{top_row['value']}为{name}的{interpretation}。"
                )
                verification_signal = (
                    f"下一完整周期{top_row['value']}的{name}及其与其他{dimension}的差距"
                )
            else:
                text = f"复核{name}变化对应的业务事件，并在下一完整周期验证是否延续。"
                rationale = "当前表可以确认趋势，但维度明细不足以定位结构来源。"
                verification_signal = f"下一完整周期{name}变化及补充的结构明细"
        else:
            text = f"复核{name}变化对应的业务事件与统计口径，并在下一周期验证是否延续。"
            rationale = "当前表只提供时间趋势，尚无可用于定位结构来源的维度。"
            verification_signal = f"下一完整周期{name}变化及对应业务事件"
        actions.append(
            {
                "action_id": f"action-{len(actions) + 1:02d}",
                "priority": len(actions) + 1,
                "text": text,
                "rationale": rationale,
                "verification_signal": verification_signal,
                "evidence_ids": evidence_ids,
            }
        )

    def compact_metric(name: str) -> str:
        metric = metrics[name]
        value = metric["latest"]
        unit = metric["unit"]
        periods = list(metric.get("periods", []))
        previous_period_label = (
            _display_period_label(periods[-2], request.period_type)
            if len(periods) >= 2
            else comparison_label
        )
        if value is None:
            value_text = "—"
        elif unit in {"元", "currency"} and abs(float(value)) >= 10_000:
            value_text = f"{float(value) / 10_000:.2f}万"
        elif unit == "%":
            value_text = f"{float(value):.2f}%"
        elif unit == "x":
            value_text = f"{float(value):.2f}倍"
        elif abs(float(value)) >= 10_000:
            value_text = f"{float(value) / 10_000:.2f}万"
        else:
            value_text = f"{float(value):,.2f}"
        change = metric["change_pct"]
        if change is None:
            comparison_text = f"暂无{previous_period_label}可比数据"
        elif unit == "%" and metric.get("change_delta") is not None:
            comparison_text = (
                f"较{previous_period_label}{float(metric['change_delta']):+.2f}个百分点"
            )
        else:
            comparison_text = f"较{previous_period_label}{float(change):+.1f}%"
        return f"{display_metric_name(name)} {value_text}，{comparison_text}"

    if is_retail_growth:
        lever_definitions = [
            ("规模", [revenue_name, order_name]),
            ("转化", [conversion_name]),
            ("收入质量", [refund_name]),
            ("成本效率", [cost_name, roas_name]),
        ]
    else:
        role_groups = (
            ("结果与规模", {"outcome", "volume"}),
            ("转化", {"conversion"}),
            ("质量", {"quality"}),
            ("成本与效率", {"cost", "efficiency"}),
            ("其他核心指标", {"unknown"}),
        )
        lever_definitions = [
            (
                label,
                [
                    str(contract["name"])
                    for contract in contracts
                    if contract.get("role") in roles
                ],
            )
            for label, roles in role_groups
        ]
    levers: list[dict[str, Any]] = []
    for label, metric_names in lever_definitions:
        present_names = list(dict.fromkeys(name for name in metric_names if name))
        if not present_names:
            continue
        related_diagnostic = next(
            (
                insight
                for insight in diagnostic_insights
                if insight.get("metric_name") in present_names
            ),
            None,
        )
        related_dimension_record = None
        if not related_diagnostic:
            candidates = [
                record
                for record in dimension_yoy_records
                if record.get("metric") in present_names
                and record.get("change_pct") is not None
            ]
            if candidates:
                related_dimension_record = max(
                    candidates,
                    key=lambda record: abs(
                        float(
                            record.get("delta")
                            if record.get("unit") == "%"
                            else record.get("change_pct")
                        )
                    ),
                )
        headline = (
            str(related_diagnostic["headline"])
            if related_diagnostic
            else "；".join(compact_metric(name) for name in present_names)
        )
        if related_diagnostic:
            takeaway = str(related_diagnostic["implication"])
        elif related_dimension_record:
            latest_label = _display_period_label(
                str(related_dimension_record["latest_period"]), request.period_type
            )
            comparison_period_label = _display_period_label(
                str(related_dimension_record["comparison_period"]), request.period_type
            )
            takeaway = (
                f"{latest_label}较{comparison_period_label}，"
                f"{related_dimension_record['dimension']}“{related_dimension_record['value']}”的"
                f"{change_fragment(related_dimension_record)}，是该模块变化最显著的结构项。"
            )
        else:
            takeaway = (
                "现有数据可确认"
                + "；".join(compact_metric(name) for name in present_names)
                + "；当前表未提供可继续归因的维度或同比证据。"
            )
        lever_evidence = [metrics[name]["evidence_id"] for name in present_names]
        if related_diagnostic:
            lever_evidence.extend(related_diagnostic.get("evidence_ids", []))
        elif related_dimension_record:
            lever_evidence.append(str(related_dimension_record["evidence_id"]))
        levers.append(
            {
                "lever_id": f"lever-{len(levers) + 1:02d}",
                "label": label,
                "metric_names": present_names,
                "headline": headline,
                "items": [
                    {
                        "name": name,
                        "display_name": next(
                            contract["display_name"]
                            for contract in contracts
                            if contract["name"] == name
                        ),
                        "value": metrics[name]["latest"],
                        "previous_value": metrics[name]["previous"],
                        "change_pct": metrics[name]["change_pct"],
                        "change_delta": metrics[name]["change_delta"],
                        "unit": metrics[name]["unit"],
                    }
                    for name in present_names
                ],
                "takeaway": takeaway,
                "evidence_ids": list(dict.fromkeys(lever_evidence)),
            }
        )

    opportunities = [
        item for item in diagnostic_insights if item.get("signal_type") == "opportunity"
    ]
    risks = [
        item for item in diagnostic_insights if item.get("signal_type") == "risk"
    ]
    if opportunities and risks:
        report_title = (
            f"{opportunities[0]['title_clause']}，但{risks[0]['title_clause']}"
        )
    elif diagnostic_insights:
        report_title = str(
            diagnostic_insights[0].get("title_clause")
            or diagnostic_insights[0]["headline"]
        )
    else:
        comparable_statuses = [
            str(kpi["status"])
            for kpi in kpis
            if kpi.get("change_pct") is not None and kpi.get("status") != "neutral"
        ]
        if comparable_statuses and all(status == "positive" for status in comparable_statuses):
            report_title = "核心指标整体改善，仍需验证结构贡献与持续性"
        elif comparable_statuses and all(status == "negative" for status in comparable_statuses):
            report_title = "核心指标整体承压，需要优先定位主要拖累项"
        elif comparable_statuses:
            report_title = "核心指标表现分化，需要联合判断结果、质量与效率"
        else:
            report_title = "核心指标基线已经建立，仍需后续周期验证"

    narrative_insights = list(
        dict.fromkeys(
            [
                *[item["insight_id"] for item in opportunities[:1]],
                *[item["insight_id"] for item in risks[:2]],
                *[item["insight_id"] for item in diagnostic_insights],
            ]
        )
    )
    insight_by_id = {item["insight_id"]: item for item in diagnostic_insights}
    summary_statements = [
        str(insight_by_id[insight_id]["statement"]).rstrip("。")
        for insight_id in narrative_insights[:3]
    ]
    summary_evidence_ids = [
        list(insight_by_id[insight_id].get("evidence_ids", []))
        for insight_id in narrative_insights[:3]
    ]
    if not summary_statements:
        summary_statements = [
            str(item["text"]).rstrip("。") for item in findings[:3]
        ]
        summary_evidence_ids = [
            list(item.get("evidence_ids", [])) for item in findings[:3]
        ]
    else:
        for finding in findings:
            candidate = str(finding["text"]).rstrip("。")
            if candidate not in summary_statements:
                summary_statements.append(candidate)
                summary_evidence_ids.append(list(finding.get("evidence_ids", [])))
            if len(summary_statements) == 3:
                break
    priority_actions = [
        str(item.get("headline") or item["text"]).rstrip("。")
        for item in actions[:2]
    ]
    report_summary = "；".join(summary_statements)
    if priority_actions:
        report_summary += f"。下一周期优先：{'；'.join(priority_actions)}"
    elif report_summary:
        report_summary += "。"

    all_periods = sorted({period for metric in metrics.values() for period in metric["periods"]})
    latest_period = all_periods[-1] if all_periods else None
    previous_period = (
        all_periods[-2]
        if len(all_periods) > 1 and _comparison_enabled(request, "period_over_period")
        else None
    )
    period_overview_kpis = [
        {
            **kpi,
            "value": kpi.get("total"),
            "previous_value": None,
            "change_pct": None,
            "change_delta": None,
            "status": "neutral",
            "scope": "analysis_window",
        }
        for kpi in kpis
    ]
    latest_snapshot_kpis = [
        {
            **kpi,
            "scope": "latest_complete_period",
            "period_label": _display_period_label(latest_period, request.period_type),
            "comparison_period_label": _display_period_label(
                previous_period, request.period_type
            ),
        }
        for kpi in kpis
    ]
    return {
        "analysis_profile": analysis_profile,
        "analysis_window_scope_id": window_scope_id,
        "scope_catalog": scope_registry.export(),
        "metric_contracts": contracts,
        "periods": {
            "type": request.period_type,
            "labels": all_periods,
            "latest": latest_period,
            "previous": previous_period,
            "analysis_label": _analysis_window_label(all_periods, request.period_type),
            "latest_display": _display_period_label(latest_period, request.period_type),
            "previous_display": _display_period_label(previous_period, request.period_type),
            "comparison_label": comparison_label,
            "incomplete_period_policy": request.incomplete_period_policy,
            "excluded_incomplete_periods": excluded_incomplete_periods,
        },
        "metrics": metrics,
        "kpis": kpis,
        "period_overview": {
            "label": _analysis_window_label(all_periods, request.period_type),
            "start_period": all_periods[0] if all_periods else None,
            "end_period": latest_period,
            "kpis": period_overview_kpis,
        },
        "latest_snapshot": {
            "label": _display_period_label(latest_period, request.period_type),
            "period": latest_period,
            "comparison_label": _display_period_label(
                previous_period, request.period_type
            ),
            "comparison_period": previous_period,
            "kpis": latest_snapshot_kpis,
        },
        "dimensions": dimensions,
        "findings": findings,
        "insights": insights,
        "actions": actions,
        "levers": levers,
        "charts": charts,
        "evidence_index": evidence_index,
        "report_title": report_title,
        "judgement_headline": report_title,
        "executive_summary": {
            "key_conclusions": summary_statements[:3],
            "key_conclusion_evidence_ids": summary_evidence_ids[:3],
            "priority_actions": priority_actions[:2],
        },
        "report_summary": report_summary,
        "warnings": warnings,
    }
