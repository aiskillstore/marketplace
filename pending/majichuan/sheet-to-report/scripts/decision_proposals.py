"""Compile AI-authored decisions from immutable calculated evidence, not rows.

The caller supplies judgement and action language after inspecting evidence.
Numbers, questions, proof scopes and depth are never supplied by that language.
"""
from __future__ import annotations

from copy import deepcopy
import math
import re

from analysis_depth import assess_depth, formal_action_is_complete
from analysis_engine import _year_over_year_label
from canonical_json import canonical_sha256


def _fail(message):
    raise ValueError("decision_proposal: " + message)


def _fields(value, required, optional=()):
    if not isinstance(value, dict) or set(required) - set(value) or set(value) - set(required) - set(optional):
        _fail("missing or unknown fields")


def _text(value):
    if not isinstance(value, str) or not value.strip():
        _fail("nonblank text required")
    return value


def _texts(values):
    if not isinstance(values, list) or not values:
        _fail("nonempty text list required")
    return [_text(value) for value in values]


def _number(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        _fail("proof must contain a finite calculated number")
    return value


def _has_free_quantity(text, subjects):
    # Object labels may legitimately contain numerals. Remove only observed
    # labels, longest first; remaining quantitative prose is not a proof.
    for subject in sorted(set(subjects), key=len, reverse=True):
        text = text.replace(subject, "")
    numerals = r"[零〇一二两三四五六七八九十百千万亿壹贰叁肆伍陆柒捌玖拾佰仟点]+"
    return bool(re.search(
        rf"\d|(?:百分之|千分之|万分之)|(?:翻倍|翻番|加倍|减半|一半)|"
        rf"{numerals}\s*(?:倍|成|个百分点|元|人|件|次|天|周|个月)|"
        rf"(?:提高|增加|增长|降低|下降|减少|达到|至少|至多)\s*{numerals}", text))


def prepare_decision_context(questions, evidence_index, registry):
    """Freeze exact question unions while calculation-owned members still exist."""
    contexts = []
    for question in questions:
        if (question.get("selection_status") != "selected" or question.get("supportability", {}).get("status") != "supported"
                or not question.get("evidence_ids")):
            continue
        context = {"question_id": question["question_id"], "evidence_ids": list(question["evidence_ids"])}
        registry.bind(context, evidence_index)
        contexts.append(context)
    return contexts


def _context(seed, question):
    matches = [c for c in seed.get("decision_context", []) if c.get("question_id") == question["question_id"]]
    if len(matches) != 1:
        _fail("missing or duplicate calculation-owned question context")
    context = matches[0]
    if context.get("evidence_ids") != question.get("evidence_ids"):
        _fail("question evidence context drift")
    catalog = {s["scope_id"]: s for s in seed["scope_catalog"]}
    records = seed["evidence_index"]
    scope = catalog.get(context.get("scope_id"), {})
    refs = context["evidence_ids"]
    if len(refs) != len(set(refs)) or any(ref not in records for ref in refs):
        _fail("invalid question evidence references")
    scopes = {records[ref].get("scope_id") for ref in refs}
    if (not scopes or not scopes <= set(catalog) or not scope.get("population_sha256")
            or context.get("scope_disclosure") != scope.get("definition")):
        _fail("unverified question scope")
    if scopes != {context["scope_id"]} and not (
        scope.get("kind") == "comparison" and set(scope.get("member_scope_ids", [])) == scopes
        and scope.get("relationship") == "separate_denominators"
    ):
        _fail("question context does not preserve exact separate scopes")
    return context


def _proof(seed, question, spec):
    _fields(spec, {"evidence_id", "view"}, {"current_period", "baseline_period"})
    ref = spec["evidence_id"]
    if ref not in question["evidence_ids"]:
        _fail("proof is outside its concrete question")
    record = seed["evidence_index"][ref]
    if spec["view"] != "period_change":
        _fail("unsupported proof view")
    kind = record.get("kind")
    if kind in {"dimension_yoy", "dimension_slice_yoy", "seasonality"}:
        if set(spec) != {"evidence_id", "view"}:
            _fail("a calculated slice already fixes both comparison periods")
        current, baseline = record.get("latest"), record.get("comparison")
        current_period, baseline_period = record.get("latest_period"), record.get("comparison_period")
    elif kind == "metric_trend":
        _fields(spec, {"evidence_id", "view", "current_period", "baseline_period"})
        labels, values = record.get("periods", []), record.get("values", [])
        current_period, baseline_period = spec["current_period"], spec["baseline_period"]
        if (len(labels) != len(values) or len(labels) != len(set(labels))
                or current_period not in labels or baseline_period not in labels):
            _fail("periods not present in calculated series")
        current, baseline = values[labels.index(current_period)], values[labels.index(baseline_period)]
        declared = question.get("comparison_scope")
        if declared:
            if isinstance(declared, dict):
                if (declared["period_field"] != "__period" or declared["current"] != [current_period]
                        or declared["baseline"] != [baseline_period]):
                    _fail("proof comparison differs from declared question scope")
            else:
                labels = sorted(labels)
                request = seed["request"]
                allowed = {labels[-2]} if len(labels) >= 2 else set()
                if declared == "latest_complete_vs_previous_and_year_over_year":
                    allowed.add(_year_over_year_label(labels[-1], request["period_type"], request["week_start"]))
                if current_period != labels[-1] or baseline_period not in allowed:
                    _fail("proof comparison differs from declared question scope")
    else:
        _fail("proof view has no verified calculation")
    if not current_period or not baseline_period or current_period == baseline_period:
        _fail("comparison periods must be distinct")
    current, baseline = _number(current), _number(baseline)
    metric = next((m for m in seed["metric_contracts"] if m["name"] == record.get("metric")), None)
    if not metric:
        _fail("proof metric has no contract")
    subject = str(record.get("value") or "整体")
    if record.get("secondary_dimension"):
        subject += "／" + str(record["secondary_value"])
    display = str(metric.get("display_name") or metric["name"])
    claims = [{"evidence_id": ref, "dimension": record.get("dimension"), "subject_value": subject,
               "metric": metric["name"], "display_metric": display, "actual_value": value,
               "relation": "observed", "period": period, "period_role": role,
               "scope_id": record["scope_id"]}
              for role, value, period in [("current", current, current_period), ("baseline", baseline, baseline_period)]]
    unit = str(metric.get("unit") or "")
    baseline_text = f"{baseline:,.6f}".rstrip("0").rstrip(".")
    current_text = f"{current:,.6f}".rstrip("0").rstrip(".")
    text = f"{subject}的{display}：{baseline_period}为{baseline_text}{unit}，{current_period}为{current_text}{unit}"
    direction = metric.get("direction")
    change = (current > baseline) - (current < baseline)
    favourable = change * ({"higher_is_better": 1, "lower_is_better": -1}.get(direction, 0))
    return claims, text, subject, favourable


def compile_decision_proposals(seed, proposals):
    """Strict proposal boundary. Never enrich away an error or mutate the seed."""
    if not isinstance(proposals, list) or not proposals:
        _fail("proposals must be a nonempty list")
    if seed.get("request", {}).get("analysis_intent") == "engineering_regression":
        _fail("engineering regression cannot receive business decisions")
    required = {"proposal_id", "question_id", "headline", "operating_implication", "signal_type", "claim_type",
                "proofs", "limitations", "action"}
    action_fields = {"action_type", "target", "headline", "rationale", "steps", "success_signal", "guardrails", "limitations"}
    questions = seed.get("analysis_lenses", [])
    insights, actions, seen = [], [], set()
    for proposal in proposals:
        _fields(proposal, required)
        pid, qid = _text(proposal["proposal_id"]), _text(proposal["question_id"])
        if pid in seen:
            _fail("duplicate proposal_id")
        seen.add(pid)
        owners = [q for q in questions if q.get("question_id") == qid]
        if (len(owners) != 1 or owners[0].get("selection_status") != "selected"
                or owners[0].get("supportability", {}).get("status") != "supported"):
            _fail("unsupported or ambiguous question")
        question = owners[0]
        context = _context(seed, question)
        if proposal["claim_type"] not in {"diagnostic", "inference"} or proposal["signal_type"] not in {"risk", "opportunity"}:
            _fail("decision type must be explicit and bounded")
        headline, implication = _text(proposal["headline"]), _text(proposal["operating_implication"])
        limitations = _texts(proposal["limitations"])
        proofs = proposal["proofs"]
        if not isinstance(proofs, list) or not proofs or len({canonical_sha256(p) for p in proofs}) != len(proofs):
            _fail("proofs must be nonempty and unique")
        claims, proof_texts, subjects, changes = [], [], [], []
        for proof in proofs:
            bound, text, subject, change = _proof(seed, question, proof)
            claims.extend(bound)
            proof_texts.append(text)
            subjects.append(subject)
            changes.append(change)
        raw_action = proposal["action"]
        _fields(raw_action, action_fields)
        for field in ("steps", "guardrails", "limitations"):
            _texts(raw_action[field])
        for field in action_fields - {"steps", "guardrails", "limitations"}:
            _text(raw_action[field])
        target = raw_action["target"]
        if target == "整体" or target not in subjects:
            _fail("action target must exactly match one proved business object")
        target_changes = [change for subject, change in zip(subjects, changes) if subject == target]
        required_change = 1 if proposal["signal_type"] == "opportunity" else -1
        if required_change not in target_changes:
            _fail("decision signal lacks a target comparison consistent with metric direction")
        language = [headline, implication, *limitations, *[raw_action[k] for k in action_fields
                    if isinstance(raw_action[k], str)], *raw_action["steps"], *raw_action["guardrails"], *raw_action["limitations"]]
        # The AI writes qualitative decisions. Calculated facts are projected
        # above, not copied as editable numeric literals into business prose.
        for text in language:
            if _has_free_quantity(text, subjects):
                _fail("numeric prose must use calculated proof, not free literals")
        suffix = canonical_sha256({"question_id": qid, "proposal_id": pid})[:20]
        iid, aid = "decision-insight-" + suffix, "decision-action-" + suffix
        if any(item.get("insight_id") == iid for item in seed.get("insights", [])) or any(
            item.get("action_id") == aid for item in seed.get("actions", [])
        ):
            _fail("proposal cannot overwrite existing content IDs")
        scope = {key: deepcopy(context[key]) for key in ("scope_id", "scope_disclosure", "evidence_ids")}
        # A judgement summary is not the proof appendix. Keep a single actual
        # target/direction anchor here; every proof remains in claim_binding,
        # immutable evidence and the chapter's checked visible proof tables.
        anchor_index = next(index for index, (subject, change) in enumerate(zip(subjects, changes))
                            if subject == target and change == required_change)
        statement = headline + "；" + proof_texts[anchor_index] + "。"
        finding = {"insight_id": iid, "question_id": qid, "lens": question["lens"], "kind": proposal["claim_type"],
            "claim_type": proposal["claim_type"], "headline": headline, "statement": statement, "resolved_answer": headline,
            "implication": implication, "decision_impact": implication, "business_question": question["business_question"],
            "signal_type": proposal["signal_type"], "limitations": limitations, "actionable": True,
            "claim_binding": {"question_id": qid, "claims": claims}, "presentation_role": "featured", "evidence_strength": "medium",
            "value_score": 4, **deepcopy(scope)}
        action = {"action_id": aid, "question_id": qid, "lens": question["lens"], "formal": True,
            **deepcopy(raw_action), "text": raw_action["headline"], "basis": statement,
            "verification_signal": raw_action["success_signal"], "source_insight_ids": [iid], **deepcopy(scope)}
        actual = assess_depth(question, evidence_index=seed["evidence_index"],
            evidence_ids=list(dict.fromkeys(p["evidence_id"] for p in proofs)),
            insights=[{**finding, "evidence_ids": list(dict.fromkeys(p["evidence_id"] for p in proofs))}],
            scope_catalog=seed["scope_catalog"])
        if actual["achieved_depth"] < 4 or not formal_action_is_complete(action):
            _fail("proposed decision lacks structural proof or executable closure")
        insights.append(finding)
        actions.append(action)
    return insights, actions
