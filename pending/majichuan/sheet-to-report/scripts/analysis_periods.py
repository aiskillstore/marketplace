"""Resolve declared comparisons against an existing, calculated analysis window."""
from __future__ import annotations


NAMED_COMPARISONS = {
    "latest_complete_period_vs_prior_period": ("previous",),
    "latest_complete_vs_previous_and_year_over_year": ("previous", "year_over_year"),
}


def validate_comparison_scope(scope):
    if scope is None:
        return
    if isinstance(scope, str) and scope in NAMED_COMPARISONS:
        return
    if not isinstance(scope, dict) or set(scope) != {"period_field", "baseline", "current"}:
        raise ValueError("invalid_comparison_scope")
    if not isinstance(scope["period_field"], str) or not scope["period_field"].strip():
        raise ValueError("invalid_comparison_scope")
    for side in ("baseline", "current"):
        values = scope[side]
        if (not isinstance(values, (list, tuple)) or not values
                or any(not isinstance(value, str) or not value.strip() for value in values)
                or len(values) != len(set(values))):
            raise ValueError("invalid_comparison_scope")
    if set(scope["baseline"]) & set(scope["current"]):
        raise ValueError("invalid_comparison_scope")


def resolve_comparison_scopes(question, frame, registry, parent_scope_id):
    """Do not alter the root question or persist a second mutable time contract.

    Explicit scopes retain their exact meaning. Named complete-period scopes use
    the primary engine's retained labels and period conventions, not the clock
    or a guessed date column. Missing requested baselines remain explicit paths
    so the executor can report missing_scope_data rather than substitute data.
    """
    import pandas as pd
    from analysis_engine import _year_over_year_label, period_labels

    scope = question.get("comparison_scope")
    validate_comparison_scope(scope)
    if scope is None:
        return []
    if isinstance(scope, dict):
        return [scope]
    rules = registry.record(parent_scope_id).get("rules", {})
    time = rules.get("time_scope", {})
    if (rules.get("stage") != "analysis_window"
            or rules.get("incomplete_period_policy") not in {"exclude", "exclude_and_note"}
            or time.get("period_type") not in {"monthly", "weekly"}
            or not time.get("periods") or "__period" not in frame):
        raise ValueError("missing_scope_data")
    field = time.get("field")
    confirmed = {*question.get("confirmed_fields", []), *question.get("required_fields", [])}
    if field not in confirmed or field not in frame:
        raise ValueError("missing_required_field")
    labels = sorted(set(str(value) for value in time["periods"]))
    actual = period_labels(pd.to_datetime(frame[field], errors="coerce"), time["period_type"], time["week_start"])
    if (actual.isna().any() or not actual.equals(frame["__period"])
            or sorted(actual.unique().tolist()) != labels):
        raise ValueError("missing_scope_data")
    current = labels[-1]
    if len(labels) < 2:
        raise ValueError("missing_scope_data")
    baselines = {"previous": labels[-2],
                 "year_over_year": _year_over_year_label(current, time["period_type"], time["week_start"])}
    return [{"period_field": "__period", "baseline": [baselines[kind]], "current": [current]}
            for kind in NAMED_COMPARISONS[scope]]
