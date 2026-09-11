from __future__ import annotations

from typing import Any, Iterable

from adapter_registry import get_adapter_registry, resolve_adapter
from analysis_questions import normalize_question_contract


TRANSACTIONAL_FIELDS = (
    "order", "product", "customer", "time", "geography", "quantity",
    "unit_price", "amount", "status",
)
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_VALUE_KINDS = {"identifier", "business_object"}
ALLOWED_FILTER_PREDICATES = {"equals", "not_equals", "in", "not_in", "is_null", "not_null"}
FORBIDDEN_EXECUTION_KEYS = {"expression", "code", "eval", "python"}
UNAMBIGUOUS_TRANSACTION_GRAINS = {"order", "order_line"}
TRANSACTIONAL_REQUIRED_FIELDS = {"order", "quantity", "unit_price"}
ALLOWED_TABLE_GRAINS = {
    "transaction",
    "order",
    "order_line",
    "user_snapshot",
    "user_event",
    "content_record",
    "project_task",
    "other_confirmed",
}
OBJECT_ROLES = {"order", "product", "customer", "user", "content", "project", "task"}
METRIC_ROLES = {"quantity", "unit_price", "amount", "metric", "value"}
TIME_ROLES = {"time", "date", "period"}
DISPLAY_FIELD_ALIASES = {
    "product": ("description", "productname", "producttitle", "商品名称", "产品名称", "品名"),
    "content": ("内容标题", "contenttitle", "title"),
    "project": ("项目名称", "projectname"),
    "task": ("任务名称", "taskname"),
}


def _needs_input(contract: dict[str, Any], questions: list[str]) -> dict[str, Any]:
    return {"status": "needs_input", "contract": contract, "questions": questions}


def _reject_executable_content(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).strip().lower() in FORBIDDEN_EXECUTION_KEYS:
                raise ValueError(f"语义合同不允许自由执行字段：{key}")
            _reject_executable_content(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            _reject_executable_content(nested)


def _normalize_mapping(value: Any, role: str) -> dict[str, str]:
    if isinstance(value, str):
        return {"source_field": value, "confidence": "high"}
    if not isinstance(value, dict):
        raise ValueError(f"字段映射“{role}”必须提供 source_field 和 confidence")
    source_field = str(value.get("source_field") or value.get("field") or "").strip()
    confidence = str(value.get("confidence") or "").strip().lower()
    if not source_field:
        raise ValueError(f"字段映射“{role}”缺少 source_field")
    if confidence not in ALLOWED_CONFIDENCE:
        raise ValueError(f"字段映射“{role}”的 confidence 仅支持 high、medium、low")
    normalized = {"source_field": source_field, "confidence": confidence}
    display_field = str(
        value.get("display_field") or value.get("display_name_field") or ""
    ).strip()
    if display_field:
        normalized["display_field"] = display_field
    value_kind = str(value.get("value_kind") or "").strip().lower()
    if value_kind:
        if value_kind not in ALLOWED_VALUE_KINDS:
            raise ValueError(
                f"字段映射“{role}”的 value_kind 仅支持 identifier、business_object"
            )
        normalized["value_kind"] = value_kind
    return normalized


def _normalized_field_name(value: Any) -> str:
    return "".join(character.lower() for character in str(value or "") if character.isalnum())


def _looks_like_identifier(field: str) -> bool:
    normalized = _normalized_field_name(field)
    return any(
        marker in normalized
        for marker in ("id", "key", "code", "number", "编号", "代码", "编码")
    )


def _infer_display_field(
    role: str,
    source_field: str,
    columns: list[str],
) -> tuple[str, str]:
    """Return a deterministic display binding without guessing business meaning."""
    if role in {"customer", "user", "order"}:
        return "", "未自动绑定可能包含个人或交易标识的展示字段"
    if not _looks_like_identifier(source_field):
        return source_field, "源字段本身是可读业务标签"
    aliases = DISPLAY_FIELD_ALIASES.get(role, ())
    normalized_columns = {_normalized_field_name(column): column for column in columns}
    matches = [
        normalized_columns[_normalized_field_name(alias)]
        for alias in aliases
        if _normalized_field_name(alias) in normalized_columns
    ]
    matches = list(dict.fromkeys(matches))
    if len(matches) == 1:
        return matches[0], "字段名命中唯一的高置信展示字段别名"
    if len(matches) > 1:
        return "", "存在多个展示字段候选，需确认后绑定"
    return "", "未发现唯一的高置信展示字段"


def _infer_table_grain(mappings: dict[str, dict[str, str]]) -> str:
    roles = set(mappings)
    if "task" in roles or "project" in roles:
        return "project_task"
    if "content" in roles:
        return "content_record"
    if "user" in roles:
        return "user_snapshot"
    return "other_confirmed"


def _scope_ids_for_object(object_id: str, *, transactional: bool) -> list[str]:
    if not transactional:
        return ["all_rows"]
    if object_id in {"product", "customer", "order"}:
        return ["all_rows", "normal_sales"]
    return ["all_rows"]


def _field_affordance(
    role: str,
    mapping: dict[str, str],
    *,
    display_field: str = "",
) -> dict[str, Any]:
    field_ids = [mapping["source_field"]]
    if display_field and display_field not in field_ids:
        field_ids.append(display_field)
    if role in OBJECT_ROLES:
        supported = ["contribution", "concentration", "structure"]
        calculations = ["group_aggregate", "rank", "share"]
        evidence_shapes = ["grouped_metric", "ranked_entities"]
        charts = ["bar", "table"]
        limitations = [] if display_field else ["缺少已确认展示字段，观众表达只能使用标识符或聚合标签"]
    elif role in TIME_ROLES:
        supported = ["trend", "period_comparison", "change_point"]
        calculations = ["period_aggregate", "period_delta"]
        evidence_shapes = ["time_series"]
        charts = ["line", "column"]
        limitations = ["周期完整性与比较基期仍由时间合同控制"]
    elif role in METRIC_ROLES:
        supported = ["trend", "contribution", "quality_impact"]
        calculations = ["aggregate", "delta", "share"]
        evidence_shapes = ["scalar", "time_series", "grouped_metric"]
        charts = ["kpi", "line", "bar"]
        limitations = ["聚合方式必须来自已确认指标合同"]
    else:
        supported = ["structure", "segment_comparison", "cross_breakdown"]
        calculations = ["group_aggregate", "share"]
        evidence_shapes = ["grouped_metric"]
        charts = ["bar", "table"]
        limitations = ["仅在与已确认指标组合时支持经营判断"]
    return {
        "field_ids": field_ids,
        "supported_question_types": supported,
        "required_calculations": calculations,
        "evidence_shapes": evidence_shapes,
        "chart_families": charts,
        "limitations": limitations,
    }


def _semantic_capabilities(
    mappings: dict[str, dict[str, str]],
    *,
    columns: list[str],
    transactional: bool,
    confirmed_professional: bool,
    material_fields: Iterable[str] | None,
    confirmed_fields: Iterable[str] | None,
    contract: dict[str, Any],
) -> dict[str, Any]:
    object_bindings: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    affordances: list[dict[str, Any]] = []
    used_reasons: dict[str, set[str]] = {}
    needs_confirmation: dict[str, set[str]] = {}

    for field in confirmed_fields or ():
        field_id = str(field)
        if field_id in columns:
            used_reasons.setdefault(field_id, set()).add("已确认指标合同依赖该字段")

    attribute_fields = [
        mapping["source_field"]
        for role, mapping in mappings.items()
        if role not in OBJECT_ROLES | METRIC_ROLES | TIME_ROLES
    ]
    metric_fields = [
        mapping["source_field"]
        for role, mapping in mappings.items()
        if role in METRIC_ROLES
    ]
    for role, mapping in mappings.items():
        source_field = mapping["source_field"]
        used_reasons.setdefault(source_field, set()).add(f"已绑定语义角色 {role}")
        display_field = str(mapping.get("display_field") or "").strip()
        display_reason = "由语义合同显式确认"
        if role in OBJECT_ROLES:
            inferred_field, inferred_reason = _infer_display_field(role, source_field, columns)
            # Re-resolving an already bound contract must be idempotent.  A
            # canonical snapshot contains the inferred field, but that does
            # not turn a field-name match into a different binding reason.
            if not display_field or display_field == inferred_field:
                display_field, display_reason = inferred_field, inferred_reason
            if display_field:
                mapping["display_field"] = display_field
        if display_field:
            used_reasons.setdefault(display_field, set()).add(f"作为 {role} 的展示字段")
        confidence = mapping["confidence"]
        if confidence != "high" and not (confidence == "medium" and confirmed_professional):
            needs_confirmation.setdefault(source_field, set()).add(
                f"{role} 映射置信度为 {confidence}"
            )
        if role in OBJECT_ROLES:
            confirmation_status = (
                "confirmed"
                if confidence == "high" or (confidence == "medium" and confirmed_professional)
                else "needs_confirmation"
            )
            object_bindings.append({
                "object_id": role,
                "identifier_field": source_field,
                "display_field": display_field,
                "display_field_reason": display_reason,
                "attribute_fields": list(attribute_fields),
                "metric_fields": list(metric_fields),
                "scope_ids": _scope_ids_for_object(role, transactional=transactional),
                "confidence": confidence,
                "confirmation_status": confirmation_status,
            })
            if display_field and display_field != source_field:
                relationships.append({
                    "relationship_type": "identifier_display",
                    "source_fields": [source_field, display_field],
                    "target_object_id": role,
                    "confidence": confidence,
                    "evidence": display_reason,
                })
        affordances.append(_field_affordance(role, mapping, display_field=display_field))

    explicit_material = {
        str(field)
        for field in (
            list(material_fields or ())
            + list(contract.get("material_fields", ()))
            + list(contract.get("selected_fields", ()))
        )
        if str(field).strip()
    }
    column_set = set(columns)
    material_unmapped = {
        field: {"用户已选择或指标合同依赖该字段，但语义合同尚未绑定"}
        for field in explicit_material
        if field in column_set and field not in used_reasons
    }
    reasonably_ignored = {
        field: {"当前未被对象、指标或显式分析选择使用"}
        for field in columns
        if field not in used_reasons
        and field not in needs_confirmation
        and field not in material_unmapped
    }

    def records(values: dict[str, set[str]]) -> list[dict[str, str]]:
        return [
            {"field_id": field, "reason": "；".join(sorted(reasons))}
            for field, reasons in values.items()
        ]

    return {
        "object_bindings": object_bindings,
        "field_question_affordances": affordances,
        "semantic_relationships": relationships,
        "semantic_coverage": {
            "used": records(used_reasons),
            "reasonably_ignored": records(reasonably_ignored),
            "needs_confirmation": records(needs_confirmation),
            "material_unmapped": records(material_unmapped),
        },
    }


def _validate_filters(contract: dict[str, Any]) -> None:
    filters = contract.get("filters", contract.get("filter_rules", ()))
    if not isinstance(filters, (list, tuple)):
        raise ValueError("filters 必须是白名单谓词列表")
    for rule in filters:
        if not isinstance(rule, dict):
            raise ValueError("filters 每项必须是字段与 predicate")
        _reject_executable_content(rule)
        predicate = str(rule.get("predicate") or rule.get("operator") or "").strip().lower()
        if predicate not in ALLOWED_FILTER_PREDICATES:
            raise ValueError(f"filters predicate 不在白名单中：{predicate or '缺失'}")
        if not str(rule.get("field") or "").strip():
            raise ValueError("filters 每项缺少 field")


def _resolve_contract_adapter(
    contract: dict[str, Any],
    *,
    mode: str,
    confirmed_professional: bool,
    questions: list[str],
) -> None:
    declared_id = str(contract.get("adapter_id") or "").strip()
    domain_id = str(contract.get("domain") or contract.get("profile") or "").strip()
    if declared_id and domain_id and declared_id != domain_id:
        raise ValueError("adapter_id 必须与 domain/profile 一致")
    adapter_id = declared_id or domain_id or "general"
    registry = get_adapter_registry()
    adapter = registry.get(adapter_id)
    if adapter is None:
        questions.append(f"adapter '{adapter_id}' is unavailable")
        contract.update(
            {
                "adapter_id": adapter_id,
                "adapter_maturity": "unavailable",
                "adapter_selection_reason": "unavailable",
                "execution_profile": "",
            }
        )
        return
    selected_adapter = adapter
    selection_reason = "auto_verified" if not (declared_id or domain_id) else "explicit_verified"
    if adapter["maturity"] == "experimental" and not declared_id:
        selected_adapter = registry["general"]
        selection_reason = "experimental_not_enabled"
        # A domain tag is not permission to select an experimental adapter.
        # Keep the tag as provenance, while making the executable contract
        # internally consistent and safe to resolve again during replay.
        contract["declared_domain_hint"] = domain_id
        for key in ("domain", "profile"):
            if key in contract:
                contract[key] = "general"
    elif (
        adapter_id == "general"
        and registry.get(str(contract.get("declared_domain_hint") or ""), {}).get("maturity")
        == "experimental"
    ):
        # This hint can only retain general execution; it cannot override the
        # strict adapter/domain check above or grant experimental confirmation.
        selection_reason = "experimental_not_enabled"
    execution_profile = str(contract.get("execution_profile") or "").strip()
    if execution_profile and execution_profile != selected_adapter["execution_profile"]:
        raise ValueError(
            f"adapter '{selected_adapter['adapter_id']}' 的 execution_profile 必须为 {selected_adapter['execution_profile']}"
        )
    if selected_adapter["maturity"] == "experimental":
        if mode == "quick":
            questions.append(
                f"Quick 仅可自动使用 verified 适配器；'{adapter_id}' 当前为 experimental。"
            )
            selection_reason = "quick_rejected_experimental"
        elif confirmed_professional:
            resolve_adapter(adapter_id, allow_experimental=True)
            selection_reason = "confirmed_experimental"
        else:
            questions.append(
                f"实验适配器 '{adapter_id}' 需要确认分析计划后才能启用。"
            )
            selection_reason = "confirmation_required"
    else:
        resolve_adapter(
            selected_adapter["adapter_id"],
            auto_select=not (declared_id or domain_id),
        )

    contract.update(
        {
            "adapter_id": selected_adapter["adapter_id"],
            "adapter_maturity": selected_adapter["maturity"],
            "adapter_selection_reason": selection_reason,
            "execution_profile": selected_adapter["execution_profile"],
        }
    )


def resolve_semantic_contract(
    contract: dict[str, Any] | None,
    *,
    source_columns: Iterable[str] | None = None,
    mode: str = "professional",
    material_fields: Iterable[str] | None = None,
    confirmed_fields: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Validate declarative business semantics without evaluating user input.

    The returned machine-readable status lets Quick ask for confirmation rather
    than silently adopting uncertain transactional assumptions.
    """
    if contract is None:
        return {"status": "ready", "contract": None, "questions": []}
    if not isinstance(contract, dict):
        raise ValueError("semantic_contract 必须是对象")
    _reject_executable_content(contract)
    _validate_filters(contract)
    normalized = dict(contract)
    mappings = contract.get("field_mappings", contract.get("mappings", {}))
    if not isinstance(mappings, dict):
        raise ValueError("semantic_contract.field_mappings 必须是对象")
    normalized_mappings = {
        str(role): _normalize_mapping(value, str(role)) for role, value in mappings.items()
    }
    normalized["field_mappings"] = normalized_mappings
    normalized.pop("mappings", None)
    questions: list[str] = []
    confirmed_professional = (
        mode == "professional"
        and str(contract.get("confirmation_status") or "") == "confirmed"
    )
    _resolve_contract_adapter(
        normalized,
        mode=mode,
        confirmed_professional=confirmed_professional,
        questions=questions,
    )
    column_list = [str(column) for column in (() if source_columns is None else source_columns)]
    columns = set(column_list)
    transactional = str(contract.get("domain") or contract.get("profile") or "").strip() == "transactional_commerce"
    grain = str(contract.get("table_grain") or "").strip()
    if transactional:
        if grain not in UNAMBIGUOUS_TRANSACTION_GRAINS:
            questions.append("交易表粒度不明确，请明确为 order 或 order_line。")
        missing_roles = [role for role in TRANSACTIONAL_REQUIRED_FIELDS if role not in normalized_mappings]
        if missing_roles:
            questions.append("交易语义合同缺少字段映射：" + ", ".join(missing_roles))
    elif grain and grain not in ALLOWED_TABLE_GRAINS:
        questions.append("表粒度不在允许范围内，请确认后继续。")
    elif not grain:
        normalized["table_grain"] = _infer_table_grain(normalized_mappings)
    for role, mapping in normalized_mappings.items():
        source_field = mapping["source_field"]
        confidence = mapping["confidence"]
        if columns and source_field not in columns:
            questions.append(f"字段映射“{role}”指向不存在的字段：{source_field}。")
        display_field = str(mapping.get("display_field") or "")
        if columns and display_field and display_field not in columns:
            questions.append(f"字段映射“{role}”的 display_field 指向不存在的字段：{display_field}。")
        if confidence == "low" or (mode == "quick" and confidence != "high"):
            questions.append(f"Quick 仅可自动采用 high 置信度；“{role}”当前为 {confidence}。")
        elif confidence == "medium" and not confirmed_professional:
            questions.append(f"Professional 使用 medium 置信度前需显式确认；“{role}”尚未确认。")
    conflicts = contract.get("conflicts", ())
    if conflicts:
        questions.append("语义合同存在显式冲突，请确认后继续：" + ", ".join(str(item) for item in conflicts))
    capabilities = _semantic_capabilities(
        normalized_mappings,
        columns=column_list,
        transactional=transactional,
        confirmed_professional=confirmed_professional,
        material_fields=material_fields,
        confirmed_fields=confirmed_fields,
        contract=contract,
    )
    normalized.update(capabilities)
    material_unmapped = capabilities["semantic_coverage"]["material_unmapped"]
    if material_unmapped:
        questions.append(
            "存在会影响正式分析的实质未映射字段："
            + ", ".join(str(item["field_id"]) for item in material_unmapped)
        )
    return _needs_input(normalized, questions) if questions else {"status": "ready", "contract": normalized, "questions": []}


def resolve_request_semantic_contract(
    request: Any,
    *,
    source_columns: Iterable[str],
    metric_dependencies: dict[str, list[str]],
) -> dict[str, Any]:
    """Record confirmed request usage without inferring unmapped business objects.

    The caller supplies dependencies from the same normalized metric contracts
    used by calculation. No field-name guesses or source access occur here.
    """
    columns = [str(field) for field in source_columns]
    column_set = set(columns)
    uses: dict[str, set[str]] = {}
    request_affordances: list[dict[str, Any]] = []

    def add_usage(role: str, fields: list[str], reason: str) -> None:
        fields = list(dict.fromkeys(field for field in fields if field in column_set))
        if not fields:
            return
        for field in fields:
            uses.setdefault(field, set()).add(reason)
        affordance = _field_affordance(role, {"source_field": fields[0]})
        affordance["field_ids"] = fields
        request_affordances.append(affordance)

    add_usage("time", [str(getattr(request, "date_column", ""))], "已确认分析时间字段")
    for field in getattr(request, "dimensions", ()):
        add_usage("dimension", [str(field)], "已确认分析维度")
    for metric, fields in metric_dependencies.items():
        add_usage("metric", fields, f"已确认指标 {metric} 的计算依赖")

    result = resolve_semantic_contract(
        getattr(request, "semantic_contract", None),
        source_columns=columns,
        mode=str(getattr(request, "mode", "professional")),
        confirmed_fields=uses,
    )
    semantic = result.get("contract")
    if not isinstance(semantic, dict):
        return result
    for row in semantic["semantic_coverage"]["used"]:
        reasons = set(row["reason"].split("；"))
        if row["field_id"] in uses:
            reasons.discard("已确认指标合同依赖该字段")
            reasons.update(uses[row["field_id"]])
        row["reason"] = "；".join(sorted(reasons))
    affordances = semantic["field_question_affordances"]
    for affordance in request_affordances:
        if affordance not in affordances:
            affordances.append(affordance)
    return result


def validate_analysis_questions(value: Any) -> tuple[dict[str, Any], ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise ValueError("analysis_questions 必须是问题列表")
    questions: list[dict[str, Any]] = []
    question_ids: set[str] = set()
    for index, raw in enumerate(value, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"analysis_questions 第 {index} 项必须是对象")
        missing = [field for field in ("lens", "priority", "required_fields") if not raw.get(field)]
        if not raw.get("business_question") and not raw.get("question"):
            missing.append("business_question")
        if missing:
            raise ValueError(f"analysis_questions 第 {index} 项缺少：{', '.join(missing)}")
        required_fields = raw["required_fields"]
        if not isinstance(required_fields, (list, tuple)) or not all(str(field).strip() for field in required_fields):
            raise ValueError(f"analysis_questions 第 {index} 项 required_fields 必须是非空字段列表")
        normalized = normalize_question_contract({**raw, "required_fields": list(required_fields)})
        if normalized["question_id"] in question_ids:
            raise ValueError("analysis_questions 包含重复 question_id")
        question_ids.add(normalized["question_id"])
        questions.append(normalized)
    return tuple(questions)
