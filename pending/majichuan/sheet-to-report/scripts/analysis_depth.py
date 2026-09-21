"""Evidence-shape depth and aggregate identity shared by planning and acceptance."""
from __future__ import annotations

import math
import re
from typing import Any

from canonical_json import canonical_sha256


def _number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _positive(value: Any) -> bool:
    return _number(value) and value > 0


def _groups(evidence: dict) -> tuple[tuple[str, ...], dict[tuple[str, ...], float]]:
    result = evidence.get("result", {})
    dimensions = evidence.get("dimensions") or result.get("dimensions") or [evidence.get("source_dimension") or evidence.get("dimension")]
    dimensions = tuple(str(value) for value in dimensions if value)
    rows = result.get("groups", evidence.get("rows", []))
    groups = {}
    for row in rows:
        if not isinstance(row, dict) or row.get("is_other") or not _number(row.get("metric")):
            continue
        keys = row.get("dimensions") or [row.get("key", row.get("value"))]
        if any(value is None for value in keys) or len(keys) != len(dimensions):
            continue
        groups[tuple(str(value) for value in keys)] = float(row["metric"])
    return dimensions, groups


def evidence_roles(evidence: dict) -> set[str]:
    """A type label only selects a validator; it does not itself prove depth."""
    if not isinstance(evidence, dict) or not _positive(evidence.get("sample_count")):
        return set()
    kind = evidence.get("kind")
    result = evidence.get("result", {})
    if kind == "metric_trend":
        return {"fact"} if _number(evidence.get("latest")) or any(_number(value) for value in evidence.get("values", [])) else set()
    if kind in {"dimension_yoy", "dimension_slice_yoy", "seasonality"}:
        if not all(_number(evidence.get(key)) for key in ("latest", "comparison")):
            return set()
        counts = evidence.get("sample_counts", {})
        before = counts.get("comparison", evidence.get("comparison_sample_count"))
        after = counts.get("latest", evidence.get("latest_sample_count"))
        current = evidence.get("periods") or [evidence.get("latest_period")]
        baseline = evidence.get("comparison_periods") or [evidence.get("comparison_period")]
        if not (_positive(before) and _positive(after) and all(current) and all(baseline) and set(current).isdisjoint(baseline)):
            return {"fact"}
        if kind != "seasonality" and not evidence.get("dimension"):
            return {"fact"}
        return {"fact", "driver", "segment"}
    if kind == "transaction_driver_bridge":
        drivers = evidence.get("semantics", {}).get("drivers", {})
        if not evidence.get("latest_period") or not evidence.get("comparison_period") or evidence["latest_period"] == evidence["comparison_period"]:
            return set()
        for period in ("previous", "latest"):
            values = [drivers.get(metric, {}).get(period) for metric in ("sales", "orders", "average_order_value")]
            if not all(_number(value) for value in values) or values[1] <= 0 or not math.isclose(values[0], values[1] * values[2], rel_tol=1e-8, abs_tol=1e-6):
                return {"fact"} if _number(evidence.get("latest")) else set()
        return {"fact", "driver"}
    if kind in {"dimension_contribution", "dimension_breakdown", "cross_breakdown"}:
        dimensions, groups = _groups(evidence)
        if not groups:
            return set()
        roles = {"fact"}
        if len(dimensions) >= 2 and len(groups) >= 2 and len(set(groups.values())) >= 2:
            # A pair must actually vary on both axes, not be a renamed single slice.
            if all(len({key[index] for key in groups}) >= 2 for index in range(len(dimensions))):
                roles.update(("driver", "segment"))
        decomposition = [row for row in evidence.get("rows", []) if not row.get("is_other") and _positive(row.get("order_count"))
                         and _number(row.get("average_order_value")) and _number(row.get("metric"))
                         and math.isclose(row["metric"], row["order_count"] * row["average_order_value"], rel_tol=1e-8, abs_tol=1e-6)]
        if len(decomposition) >= 2 and len({row["average_order_value"] for row in decomposition}) >= 2:
            roles.update(("driver", "segment"))
        history = evidence.get("semantics", {}).get("concentration_continuity", [])
        valid_history = [row for row in history if row.get("period") and _number(row.get("top_5_share"))]
        if len({row["period"] for row in valid_history}) >= 2:
            roles.update(("driver", "segment"))
        return roles
    if kind == "period_comparison":
        return {"fact", "driver"} if all(_number(result.get(key)) for key in ("baseline", "current", "delta")) else set()
    if kind == "quality_impact":
        if all(_number(result.get(key)) for key in ("baseline_total", "affected_total", "unaffected_total")) and result["baseline_total"] > 0:
            if math.isclose(result["baseline_total"], result["affected_total"] + result["unaffected_total"], rel_tol=1e-8):
                return {"fact", "driver", "segment"}
    if kind == "quality_diagnostic":
        if all(_number(evidence.get(key)) for key in ("affected_rows", "affected_absolute_amount", "baseline_absolute_amount")):
            if 0 <= evidence["affected_rows"] <= evidence["sample_count"] and 0 <= evidence["affected_absolute_amount"] <= evidence["baseline_absolute_amount"] + 1e-6:
                return {"fact", "driver", "segment"} if evidence["affected_rows"] else {"fact"}
    if kind == "concentration" and _number(result.get("top_share")) and _positive(result.get("group_count")):
        return {"fact"}
    return set()


def population_identity(evidence: dict, scope_catalog=()) -> str | None:
    catalog = {scope["scope_id"]: scope for scope in scope_catalog}
    current = evidence.get("scope_id")
    if current not in catalog or not catalog[current].get("population_sha256"):
        return None
    chain, seen = [], set()
    while current in catalog and current not in seen:
        seen.add(current)
        scope = catalog[current]
        if scope.get("kind") == "comparison":
            return None
        chain.append(scope.get("rules", {}))
        current = scope.get("parent_scope_id")
    filters = {canonical_sha256(rule): rule for rules in chain for rule in rules.get("filters", [])}
    return canonical_sha256({
        "population_sha256": catalog[evidence["scope_id"]].get("population_sha256"),
        "time": next((rules["time_scope"] for rules in chain if rules.get("time_scope")), None),
        "filters": [filters[key] for key in sorted(filters)],
        "comparison": [rules.get("comparison") or rules.get("comparison_scope") for rules in chain if rules.get("comparison") or rules.get("comparison_scope")],
        "window": next((scope_id for scope_id in seen if catalog[scope_id].get("rules", {}).get("stage") == "analysis_window"), "source_rows"),
    })


def _role_map(ids, evidence_index, scope_catalog):
    roles = {key: evidence_roles(evidence_index.get(key, {})) for key in ids}
    # Comparing two different metrics over the same actual business objects is
    # a structural cross-check; table-wide dimension declarations are not.
    grouped = {key: _groups(evidence_index[key]) for key in ids if roles[key] and key in evidence_index}
    for left, (left_dims, left_groups) in grouped.items():
        for right, (right_dims, right_groups) in grouped.items():
            if left >= right or not left_dims or left_dims != right_dims or evidence_index[left].get("metric") == evidence_index[right].get("metric"):
                continue
            population = population_identity(evidence_index[left], scope_catalog)
            if population is None or population != population_identity(evidence_index[right], scope_catalog):
                continue
            common = set(left_groups) & set(right_groups)
            if len(common) >= 2 and (len({left_groups[key] for key in common}) >= 2 or len({right_groups[key] for key in common}) >= 2):
                roles[left].update(("driver", "segment"))
                roles[right].update(("driver", "segment"))
    return roles


def formal_action_is_complete(action: dict, *, require_judgement_source: bool = True) -> bool:
    """Typed execution/verification content, not truthy placeholders, proves closure."""
    def text(value):
        return isinstance(value, str) and bool(value.strip())

    if action.get("formal") is not True or not all(text(action.get(key)) for key in (
        "action_id", "target", "basis", "rationale", "success_signal",
    )):
        return False
    for key in ("steps", "guardrails", "evidence_ids"):
        values = action.get(key)
        if not isinstance(values, list) or not values or not all(text(value) for value in values):
            return False
    sources = action.get("source_insight_ids", [])
    if not isinstance(sources, list) or not all(text(value) for value in sources) or (require_judgement_source and not sources):
        return False
    limitations = action.get("limitations")
    if not isinstance(limitations, list) or not all(text(value) for value in limitations):
        return False
    kind = action.get("action_type")
    if kind not in {"act_now", "controlled_test", "monitor", "data_governance"}:
        return False
    normalized = lambda value: re.sub(r"[\W_]+", "", str(value or "")).lower()
    if kind in {"controlled_test", "monitor"} and normalized(action["success_signal"]) in {
        normalized(action.get(key)) for key in ("basis", "text", "headline")
    }:
        return False
    return True


def validate_action_chapter_links(model: dict) -> None:
    """Validate the final bidirectional graph, including the owner of depth five."""
    from analysis_scope import record_evidence_ids

    chapters = {item["chapter_id"]: item for item in model.get("analysis_chapters", [])}
    actions = {item.get("action_id"): item for item in model.get("actions", [])}
    if len(actions) != len(model.get("actions", [])) or any(not isinstance(key, str) or not key.strip() for key in actions):
        raise ValueError("action closure requires unique nonblank action_id")
    questions = {item["question_id"]: item for item in model.get("analysis_lenses", [])}
    insights = {}
    for raw in model.get("insights", []):
        item = dict(raw)
        canonical = "q_" + str(item.get("lens") or "")
        if not item.get("question_id") and canonical in questions:
            item["question_id"] = canonical
        insights[item.get("insight_id")] = item
    for aid, action in actions.items():
        if not formal_action_is_complete(action, require_judgement_source=False):
            raise ValueError("formal action closure content is incomplete or invalid")
        owners = action.get("source_chapter_ids", [])
        if action.get("formal") is not True or not isinstance(owners, list) or not owners:
            raise ValueError("formal action closure requires chapter ownership")
        for cid in owners:
            chapter = chapters.get(cid, {})
            if chapter.get("selection_status") != "selected" or aid not in chapter.get("action_ids", []):
                raise ValueError("action closure chapter links must be bidirectional and selected")
            source_ids = action.get("source_insight_ids", [])
            if source_ids and not any(
                iid in chapter.get("insight_ids", [])
                and insights.get(iid, {}).get("question_id") == chapter.get("question_id")
                for iid in source_ids
            ):
                raise ValueError("formal action closure cannot borrow another question's insight")
        # Every declared source judgement needs its own actual chapter owner;
        # one valid source cannot lend this action to another question.
        for iid in action.get("source_insight_ids", []):
            if not any(iid in chapters[cid].get("insight_ids", [])
                       and insights.get(iid, {}).get("question_id") == chapters[cid].get("question_id") for cid in owners):
                raise ValueError("formal action closure source insight has no owning chapter")
    for cid, chapter in chapters.items():
        refs = chapter.get("action_ids", [])
        if not isinstance(refs, list) or len(refs) != len(set(refs)) or any(
            aid not in actions or cid not in actions[aid].get("source_chapter_ids", []) for aid in refs
        ):
            raise ValueError("chapter action closure references are missing or inconsistent")
        if chapter.get("achieved_depth") == 5:
            representative = insights.get(chapter.get("judgement_insight_id"), {})
            actual = assess_depth(questions.get(chapter.get("question_id"), {}),
                evidence_index=model.get("evidence_index", {}), evidence_ids=record_evidence_ids(chapter),
                insights=[representative], actions=[actions[aid] for aid in refs], scope_catalog=model.get("scope_catalog", []))
            if actual["achieved_depth"] != 5:
                raise ValueError("chapter depth five requires a retained action closing its own judgement")


def contribution_judgement_binding(evidence: dict) -> dict | None:
    """Bind a monitoring decision to observed structure, not an arbitrary label."""
    semantics = evidence.get('semantics', {})
    rows = evidence.get('rows') or []
    history = semantics.get('concentration_continuity') or []
    valid = [r for r in history if _positive(r.get('total')) and _number(r.get('top_5_share'))
             and _number(r.get('top_5_amount')) and r.get('scope_id')
             and math.isclose(r['top_5_amount'] / r['total'], r['top_5_share'], abs_tol=1e-9)]
    if (evidence.get('kind') != 'dimension_contribution' or not evidence.get('scope_id')
            or not rows or len({r['period'] for r in valid}) < 2
            or not _positive(rows[0].get('order_count')) or not _number(rows[0].get('average_order_value'))
            or (semantics.get('value_kind') == 'identifier' and not semantics.get('display_field'))):
        return None
    return {'kind': 'contribution_history', 'evidence_id': evidence['evidence_id'],
            'scope_id': evidence['scope_id'], 'object': rows[0].get('key', rows[0]['value']),
            'observations': {key: rows[0][key] for key in ('metric', 'order_count', 'average_order_value')},
            'history_periods': [r['period'] for r in valid],
            'top_5_share_min': min(r['top_5_share'] for r in valid),
            'top_5_share_max': max(r['top_5_share'] for r in valid),
            'decision_rule': 'review_on_historical_range_exit'}


def has_bound_contribution_judgement(insight: dict, evidence_index: dict) -> bool:
    binding = insight.get('claim_binding') or {}
    key = binding.get('evidence_id')
    return (binding.get('kind') == 'contribution_history' and key in insight.get('evidence_ids', [])
            and binding == contribution_judgement_binding(evidence_index.get(key, {})))


def assess_depth(question: dict, *, evidence_index: dict, evidence_ids=None, insights=(), actions=(), scope_catalog=()) -> dict:
    ids = list(dict.fromkeys(str(value) for value in (question.get("evidence_ids", []) if evidence_ids is None else evidence_ids)))
    roles = _role_map(ids, evidence_index, scope_catalog)
    fact = [key for key in ids if "fact" in roles[key]]
    driver = [key for key in ids if "driver" in roles[key]]
    segment = [key for key in ids if "segment" in roles[key]]
    depth = 3 if driver and segment else 2 if driver else 1 if fact else 0
    judgement_ids = []
    for insight in insights:
        refs = set(insight.get("evidence_ids", []))
        if not refs or not refs <= set(fact) or not refs & set(driver) or not refs & set(segment):
            continue
        if question.get("question_id") and insight.get("question_id") != question.get("question_id"):
            continue
        own_roles = _role_map(sorted(refs), evidence_index, scope_catalog)
        if not any("driver" in value for value in own_roles.values()) or not any("segment" in value for value in own_roles.values()):
            continue
        # A structural result still needs an explicit decision claim. Plain
        # contribution copy and a generic suggestion to keep watching are not
        # automatically upgraded just because richer numbers exist nearby.
        histories = [evidence_index[key].get("semantics", {}).get("concentration_continuity", []) for key in refs]
        binding = insight.get('claim_binding') or {}
        bound_claim = bool(binding)
        if binding.get('kind') == 'contribution_history':
            bound_claim = (binding.get('evidence_id') in refs
                           and binding == contribution_judgement_binding(evidence_index.get(binding.get('evidence_id'), {})))
            if not bound_claim:
                continue
        contextual_claim = (insight.get("signal_type") in {"risk", "opportunity"}
                            or bound_claim
                            or sum(len(history) >= 2 for history in histories) >= 2
                            or any(evidence_index[key].get("kind") == "seasonality" for key in refs))
        if not contextual_claim:
            continue
        implication = str(insight.get("implication") or insight.get("decision_impact") or "").strip()
        statement = str(insight.get("statement") or insight.get("resolved_answer") or "").strip()
        if (not statement or not implication or implication == statement or implication == insight.get("headline")
                or implication in {"支持当前分析目标的决策", "决定下一周期资源与验证优先级"}
                or implication.startswith(("当前表缺少", "先判断"))
                or insight.get("answer_status") not in {None, "answered", "partial"}):
            continue
        judgement_ids.append(str(insight.get("insight_id") or ""))
    if depth >= 3 and judgement_ids:
        depth = 4
    action_ids = []
    if depth == 4:
        for action in actions:
            refs = set(action.get("evidence_ids", []))
            if (formal_action_is_complete(action) and refs <= set(fact)
                    and set(action.get("source_insight_ids", [])) & set(judgement_ids)):
                action_ids.append(action["action_id"])
        if action_ids:
            depth = 5
    return {"achieved_depth": depth, "fact_evidence_ids": fact, "driver_evidence_ids": driver,
            "segment_evidence_ids": segment, "judgement_insight_ids": judgement_ids, "action_ids": action_ids,
            "depth_gaps": [name for level, name in ((1, "facts"), (2, "drivers"), (3, "segments"), (4, "operating_judgement"), (5, "action_closure"))
                           if depth < level <= int(question.get("required_depth") or 0)]}


def aggregate_identity(evidence: dict, scope_catalog=()) -> str | None:
    """Compare query meaning, not IDs, rendering, sample text or result hashes."""
    kind = evidence.get("kind")
    grouped_kinds = {"dimension_contribution", "dimension_breakdown", "cross_breakdown", "concentration"}
    if kind not in grouped_kinds | {"period_comparison", "quality_impact"}:
        return None
    dimensions, _ = _groups(evidence)
    if kind in grouped_kinds and not dimensions:
        return None
    catalog = {scope["scope_id"]: scope for scope in scope_catalog}
    scope_id = evidence.get("scope_id")
    if scope_id not in catalog or not catalog[scope_id].get("population_sha256"):
        return None
    chain, current, seen = [], scope_id, set()
    while current in catalog and current not in seen:
        seen.add(current)
        scope = catalog[current]
        chain.append(scope.get("rules", {}))
        current = scope.get("parent_scope_id")
    # Predicate syntax and stage names do not create information when the
    # metric, actual rows and comparison roles are unchanged.
    metric = next((rules["metric_contract"] for rules in chain if rules.get("metric_contract")), None)
    roles = {}
    for role in ({"baseline", "current"} if kind == "period_comparison" else
                 {"baseline", "affected", "unaffected"} if kind == "quality_impact" else set()):
        binding = catalog.get(evidence.get("scope_bindings", {}).get(role), {})
        if not binding.get("population_sha256"):
            return None
        roles[role] = binding["population_sha256"]
    return canonical_sha256({"metric": metric or evidence.get("metric"), "dimensions": sorted(dimensions),
                             "population_sha256": catalog[scope_id].get("population_sha256"),
                             "rows": catalog[scope_id]["included_rows"], "roles": roles,
                             "family": "groups" if kind in grouped_kinds else kind})


def _period_series_covers(known: dict, candidate: dict, scope_catalog) -> bool:
    """Existing one-period aggregates prove the same pair, never a new subset."""
    if known.get("kind") != "metric_trend" or candidate.get("kind") != "period_comparison":
        return False
    catalog = {scope["scope_id"]: scope for scope in scope_catalog}
    known_scope = catalog.get(known.get("scope_id"), {})
    candidate_scope = catalog.get(candidate.get("scope_id"), {})
    metric = known_scope.get("rules", {}).get("metric_contract")
    if not metric or metric != candidate_scope.get("rules", {}).get("metric_contract"):
        return False
    periods, values = known.get("periods", []), known.get("values", [])
    if len(periods) != len(values):
        return False
    available = {
        catalog.get(known.get("scope_bindings", {}).get("periods", {}).get(period), {}).get("population_sha256")
        for period, value in zip(periods, values) if _number(value)
    } - {None}
    roles = candidate.get("scope_bindings", {})
    return bool(available) and all(
        catalog.get(roles.get(role), {}).get("population_sha256") in available
        for role in ("baseline", "current")
    )


def aggregate_covers(known: dict, candidate: dict, scope_catalog=()) -> bool:
    """A complete breakdown implies concentration, but not the reverse."""
    if _period_series_covers(known, candidate, scope_catalog):
        return True
    identity = aggregate_identity(candidate, scope_catalog)
    if identity is None or aggregate_identity(known, scope_catalog) != identity:
        return False
    if known.get("kind") == "concentration":
        return candidate.get("kind") == "concentration"
    if known.get("kind") in {"dimension_contribution", "dimension_breakdown", "cross_breakdown"}:
        rows = known.get("result", {}).get("groups", known.get("rows", []))
        if not rows or any(row.get("is_other") for row in rows):
            return False
        _, groups = _groups(known)
        expected = known.get("semantics", {}).get("total_member_count", len(rows))
        return len(groups) == len(rows) == expected
    return True
