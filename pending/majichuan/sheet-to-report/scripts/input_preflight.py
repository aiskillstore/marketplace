from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from semantic_contract import resolve_semantic_contract


SENSITIVE_MARKERS = (
    "姓名",
    "名字",
    "手机号",
    "电话",
    "身份证",
    "证件号",
    "邮箱",
    "email",
    "e-mail",
    "地址",
)
DATE_MARKERS = ("日期", "时间", "date", "time", "月份", "month", "周")
IDENTIFIER_MARKERS = ("id", "编号", "代码", "编码", "手机号", "电话", "邮编")
DIMENSION_MARKERS = (
    "渠道",
    "区域",
    "品类",
    "类目",
    "用户层级",
    "用户分层",
    "部门",
    "团队",
    "项目",
    "来源",
    "类型",
    "状态",
    "channel",
    "region",
    "category",
    "segment",
    "department",
)


class PreflightNeedsInput(ValueError):
    def __init__(self, result: dict[str, Any]):
        self.result = result
        super().__init__("Quick 预检需要确认：" + "；".join(result.get("questions", [])))


def _normalized(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "").replace("_", "")


def _contains_marker(name: str, markers: tuple[str, ...]) -> bool:
    value = _normalized(name)
    return any(_normalized(marker) in value for marker in markers)


def _read_csv_with_fallback(path: Path) -> tuple[pd.DataFrame, str]:
    errors: list[str] = []
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return pd.read_csv(path, encoding=encoding), encoding
        except UnicodeDecodeError as exc:
            errors.append(f"{encoding}: {exc}")
    raise ValueError(f"CSV 编码无法识别：{'; '.join(errors)}")


def load_source_table(
    source_path: Path,
    sheet_name: str | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    source_path = Path(source_path)
    if not source_path.exists():
        raise ValueError(f"source_path 不存在：{source_path}")
    suffix = source_path.suffix.lower()
    if suffix == ".csv":
        frame, encoding = _read_csv_with_fallback(source_path)
        return frame, {"sheet_names": [], "sheet_name": None, "encoding": encoding}
    if suffix != ".xlsx":
        raise ValueError("仅支持 .xlsx 或 .csv 文件")

    with pd.ExcelFile(source_path) as workbook:
        sheet_names = list(workbook.sheet_names)
        if sheet_name is None:
            if len(sheet_names) != 1:
                return pd.DataFrame(), {
                    "sheet_names": sheet_names,
                    "sheet_name": None,
                    "encoding": None,
                    "needs_sheet_choice": True,
                }
            sheet_name = sheet_names[0]
        if sheet_name not in sheet_names:
            raise ValueError(
                f"sheet_name 不存在：{sheet_name}；可选 Sheet：{', '.join(sheet_names)}"
            )
        frame = pd.read_excel(workbook, sheet_name=sheet_name)
    return frame, {
        "sheet_names": sheet_names,
        "sheet_name": sheet_name,
        "encoding": None,
    }


def _parse_rate(series: pd.Series, kind: str) -> float:
    nonblank = series[series.notna() & series.astype(str).str.strip().ne("")]
    if nonblank.empty:
        return 0.0
    if kind == "date":
        parsed = pd.to_datetime(nonblank, errors="coerce")
    else:
        parsed = pd.to_numeric(nonblank, errors="coerce")
    return round(float(parsed.notna().mean()), 4)


def _date_candidates(frame: pd.DataFrame) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for column in frame.columns:
        name = str(column)
        marker = _contains_marker(name, DATE_MARKERS)
        datetime_dtype = pd.api.types.is_datetime64_any_dtype(frame[column])
        if not marker and not datetime_dtype:
            continue
        rate = _parse_rate(frame[column], "date")
        if rate >= 0.8:
            candidates.append(
                {
                    "name": name,
                    "parse_rate": rate,
                    "reason": "字段名和数据格式均符合日期特征" if marker else "数据类型为日期",
                }
            )
    return candidates


def _numeric_candidates(frame: pd.DataFrame, date_column: str | None) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for column in frame.columns:
        name = str(column)
        if name == date_column or _contains_marker(name, IDENTIFIER_MARKERS):
            continue
        rate = _parse_rate(frame[column], "numeric")
        if rate < 0.95:
            continue
        metric_type = _infer_metric_type(name)
        candidates.append(
            {
                "name": name,
                "parse_rate": rate,
                "metric_type": metric_type,
                "aggregation_suggestion": {
                    "additive": "sum",
                    "average": "average",
                    "balance": "last",
                    "ratio": None,
                }[metric_type],
            }
        )
    return candidates


def _infer_metric_type(name: str) -> str:
    value = _normalized(name)
    if any(marker in value for marker in ("率", "占比", "ratio", "rate")):
        return "ratio"
    if any(marker in value for marker in ("余额", "库存", "balance", "stock")):
        return "balance"
    if any(marker in value for marker in ("平均", "均值", "客单价", "average", "avg")):
        return "average"
    return "additive"


def _find_column(columns: list[str], aliases: tuple[str, ...]) -> str | None:
    normalized = {_normalized(column): column for column in columns}
    for alias in aliases:
        target = _normalized(alias)
        if target in normalized:
            return normalized[target]
    for alias in aliases:
        target = _normalized(alias)
        for key, column in normalized.items():
            if target and target in key:
                return column
    return None


def _known_contracts(columns: list[str]) -> dict[str, dict[str, Any]]:
    revenue = _find_column(columns, ("收入", "销售额", "成交额", "GMV", "revenue", "sales"))
    orders = _find_column(columns, ("订单数", "订单量", "orders"))
    visits = _find_column(columns, ("访问量", "访客数", "流量", "visits", "sessions"))
    refunds = _find_column(columns, ("退款金额", "退货金额", "refund amount", "refund"))
    cost = _find_column(columns, ("营销成本", "广告成本", "投放成本", "spend", "marketing cost"))
    contracts: dict[str, dict[str, Any]] = {}
    for field in (revenue, orders, cost):
        if field:
            contracts[field] = {"name": field, "aggregation": "sum"}
    if orders and visits:
        contracts["转化率"] = {
            "name": "转化率",
            "aggregation": "ratio",
            "numerator": orders,
            "denominator": visits,
            "unit": "%",
            "scale": 100,
        }
    if refunds and revenue:
        contracts["退款率"] = {
            "name": "退款率",
            "aggregation": "ratio",
            "numerator": refunds,
            "denominator": revenue,
            "unit": "%",
            "scale": 100,
        }
    if revenue and cost:
        contracts["ROAS"] = {
            "name": "ROAS",
            "aggregation": "ratio",
            "numerator": revenue,
            "denominator": cost,
            "unit": "x",
            "scale": 1,
        }
    return contracts


def _suggest_metrics(
    numeric_candidates: list[dict[str, Any]],
) -> tuple[list[str], list[dict[str, Any]], list[str]]:
    columns = [str(item["name"]) for item in numeric_candidates]
    known = _known_contracts(columns)
    ordered_names = [
        _find_column(columns, ("收入", "销售额", "成交额", "GMV", "revenue", "sales")),
        _find_column(columns, ("订单数", "订单量", "orders")),
        "转化率" if "转化率" in known else None,
        "退款率" if "退款率" in known else None,
        _find_column(columns, ("营销成本", "广告成本", "投放成本", "spend", "marketing cost")),
        "ROAS" if "ROAS" in known else None,
    ]
    selected = [name for name in ordered_names if name]
    unresolved: list[str] = []
    for candidate in numeric_candidates:
        name = str(candidate["name"])
        if candidate["metric_type"] != "additive" and name not in known:
            unresolved.append(name)
            continue
        if name not in selected and len(selected) < 6:
            selected.append(name)
            known.setdefault(name, {"name": name, "aggregation": "sum"})
    selected = list(dict.fromkeys(selected))[:6]
    contracts = [known[name] for name in selected]
    return selected, contracts, unresolved


def _dimension_candidates(
    frame: pd.DataFrame,
    date_column: str | None,
    numeric_names: set[str],
    object_fields: set[str] | None = None,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    object_fields = set(object_fields or ())
    row_count = max(len(frame), 1)
    for column in frame.columns:
        name = str(column)
        if name == date_column or name in numeric_names or _contains_marker(name, SENSITIVE_MARKERS):
            continue
        unique = int(frame[column].nunique(dropna=True))
        high_cardinality = unique > min(100, max(20, int(row_count * 0.5)))
        if unique < 2 or (high_cardinality and name not in object_fields):
            continue
        priority = 0 if _contains_marker(name, DIMENSION_MARKERS) else 1
        candidates.append({
            "name": name,
            "unique_count": unique,
            "priority": priority,
            "object_candidate": name in object_fields,
            "high_cardinality": high_cardinality,
            "eligible_for_default": not high_cardinality,
        })
    return sorted(candidates, key=lambda item: (item["priority"], item["unique_count"], item["name"]))


def inspect_source(
    source_path: Path,
    *,
    sheet_name: str | None = None,
    date_column: str | None = None,
    primary_metrics: list[str] | tuple[str, ...] | None = None,
    dimensions: list[str] | tuple[str, ...] | None = None,
    metric_contracts: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    allow_sensitive_fields: bool = False,
    semantic_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    frame, source_meta = load_source_table(Path(source_path), sheet_name)
    questions: list[str] = []
    if source_meta.get("needs_sheet_choice"):
        questions.append(f"检测到多个 Sheet，请选择一个：{', '.join(source_meta['sheet_names'])}")
        return {
            "status": "needs_input",
            "questions": questions,
            "source": source_meta,
            "profile": {"columns": []},
            "suggested_request": {},
        }

    columns = [str(column) for column in frame.columns]
    semantic_result = resolve_semantic_contract(
        semantic_contract, source_columns=columns, mode="quick"
    )
    questions.extend(semantic_result["questions"])
    dates = _date_candidates(frame)
    if date_column:
        if date_column not in columns:
            raise ValueError(f"date_column 不存在：{date_column}")
        selected_date = date_column
    elif len(dates) == 1:
        selected_date = str(dates[0]["name"])
    elif not dates:
        selected_date = None
        questions.append("未识别到可靠的日期字段，请指定 date_column。")
    else:
        selected_date = None
        questions.append(
            "识别到多个日期字段，请选择 date_column："
            + ", ".join(str(item["name"]) for item in dates)
        )

    numeric = _numeric_candidates(frame, selected_date)
    suggested_metrics, suggested_contracts, unresolved = _suggest_metrics(numeric)
    supplied_contracts = [dict(item) for item in (metric_contracts or [])]
    supplied_names = {
        str(item.get("name") or item.get("metric") or "") for item in supplied_contracts
    }
    selected_metrics = list(primary_metrics or suggested_metrics)
    selected_contracts = supplied_contracts or [
        contract for contract in suggested_contracts if contract["name"] in selected_metrics
    ]
    unresolved_selected = [
        name for name in unresolved if not primary_metrics or name in selected_metrics
    ]
    unresolved_selected = [name for name in unresolved_selected if name not in supplied_names]
    if unresolved_selected:
        questions.append(
            "以下非加总指标无法自动确认口径，请提供 metric_contracts："
            + ", ".join(unresolved_selected)
        )
    if not selected_metrics:
        questions.append("未识别到可靠的数值指标，请指定 primary_metrics。")

    semantic_bindings = (semantic_result.get("contract") or {}).get("object_bindings", [])
    object_fields = {
        str(binding.get("identifier_field"))
        for binding in semantic_bindings
        if isinstance(binding, dict) and binding.get("identifier_field")
    }
    dimension_candidates = _dimension_candidates(
        frame,
        selected_date,
        {str(item["name"]) for item in numeric},
        object_fields,
    )
    default_dimensions = [
        str(item["name"])
        for item in dimension_candidates
        if item.get("eligible_for_default", True)
    ]
    selected_dimensions = list(
        dimensions
        if dimensions is not None
        else default_dimensions[:4]
    )
    sensitive_columns = [
        column for column in columns if _contains_marker(column, SENSITIVE_MARKERS)
    ]
    selected_sensitive = sorted(
        set(selected_dimensions + selected_metrics) & set(sensitive_columns)
    )
    if selected_sensitive and not allow_sensitive_fields:
        questions.append(
            "选择了疑似敏感字段，请确认后设置 allow_sensitive_fields=true："
            + ", ".join(selected_sensitive)
        )

    confirmed_fields: set[str] = set()
    if selected_date in columns:
        confirmed_fields.add(str(selected_date))
    for metric_contract in selected_contracts:
        for key in ("source_field", "numerator", "denominator"):
            field = str(metric_contract.get(key) or "")
            if field in columns:
                confirmed_fields.add(field)
    material_fields = {
        field
        for field in [selected_date, *selected_metrics, *selected_dimensions]
        if field in columns
    }
    if semantic_contract is not None:
        semantic_result = resolve_semantic_contract(
            semantic_contract,
            source_columns=columns,
            mode="quick",
            material_fields=material_fields,
            confirmed_fields=confirmed_fields,
        )
        questions.extend(
            question
            for question in semantic_result["questions"]
            if question not in questions
        )

    return {
        "status": "needs_input" if questions else "ready",
        "questions": questions,
        "source": source_meta,
        "profile": {
            "row_count": int(len(frame)),
            "column_count": int(len(columns)),
            "columns": columns,
            "date_candidates": dates,
            "numeric_candidates": numeric,
            "dimension_candidates": dimension_candidates,
            "sensitive_columns": sensitive_columns,
        },
        "suggested_request": {
            "sheet_name": source_meta.get("sheet_name"),
            "date_column": selected_date,
            "primary_metrics": selected_metrics,
            "metric_contracts": selected_contracts,
            "dimensions": selected_dimensions,
        },
        "semantic_contract": semantic_result,
    }


def resolve_quick_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    result = inspect_source(
        Path(payload["source_path"]),
        sheet_name=payload.get("sheet_name"),
        date_column=payload.get("date_column"),
        primary_metrics=payload.get("primary_metrics"),
        dimensions=payload.get("dimensions"),
        metric_contracts=payload.get("metric_contracts"),
        allow_sensitive_fields=bool(payload.get("allow_sensitive_fields", False)),
        semantic_contract=payload.get("semantic_contract"),
    )
    if result["status"] != "ready":
        raise PreflightNeedsInput(result)
    suggested = result["suggested_request"]
    resolved = {
        **payload,
        "audience": payload.get("audience", "业务负责人"),
        "objective": payload.get("objective", "识别经营变化、定位主要驱动并形成下一步建议"),
        "sheet_name": suggested.get("sheet_name"),
        "date_column": suggested["date_column"],
        "primary_metrics": suggested["primary_metrics"],
        "metric_contracts": suggested["metric_contracts"],
        "dimensions": suggested["dimensions"],
    }
    return resolved, result
