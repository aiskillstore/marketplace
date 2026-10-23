#!/usr/bin/env python3
"""TypeSafe Jev System One Decision Gate for Product Design Harness.

Provides sub-second, strongly-typed classification and boundary generation
for autonomous multi-agent workflows without generating prose or stalling pipelines.

Usage:
  python scripts/jev_gate.py route "Fix typo in README"
  python scripts/jev_gate.py evaluate --task task.json
  python scripts/jev_gate.py boundary --task task.json
"""
import argparse
import json
import os
import sys
from pathlib import Path
from urllib import error, request

SEVERITY = {"stop_reframe": 2, "verify": 1, "continue": 0}
VERDICTS = ["continue", "verify", "stop_reframe"]

ROUTINE_KEYWORDS = [
    "typo", "css", "style", "format", "lint", "comment", "readme",
    "docs", "rename", "cleanup", "refactor test", "fix test"
]

HIGH_RISK_KEYWORDS = [
    "drop table", "alter table", "migration", "secret", "auth",
    "payment", "billing", "token", "privacy", "delete user",
    "external api", "webhook", "telemetry", "export data"
]


def classify_route_baseline(prompt, context=None):
    prompt_lower = prompt.lower()
    for kw in HIGH_RISK_KEYWORDS:
        if kw in prompt_lower:
            return "commitment"
    for kw in ROUTINE_KEYWORDS:
        if kw in prompt_lower:
            return "routine"
    if context and context.get("files_changed", 0) > 5:
        return "commitment"
    return "discovery"


def evaluate_three_lanes_baseline(state):
    prompt = state.get("prompt", "")
    prompt_lower = prompt.lower()
    evidence_tier = state.get("evidence_tier", "t0")
    files = [f.lower() for f in state.get("files", [])]

    # Evidence flow
    if evidence_tier == "t0" or any(kw in prompt_lower for kw in ["maybe", "i think", "someone said"]):
        evidence_verdict = "stop_reframe"
        evidence_tier = "t0"
    elif evidence_tier == "t1":
        evidence_verdict = "verify"
    else:
        evidence_verdict = "continue"

    # Business flow (cost / trust / risk)
    if any(kw in prompt_lower for kw in ["bypass auth", "disable security", "free tier exploit"]):
        business_verdict = "stop_reframe"
    elif any(kw in prompt_lower for kw in ["billing", "payment", "paid"]):
        business_verdict = "verify"
    else:
        business_verdict = "continue"

    # User flow (actor clarity / usability)
    if any(kw in prompt_lower for kw in ["everyone", "anyone", "all users"]) and "commitment" in prompt_lower:
        user_verdict = "verify"
    else:
        user_verdict = "continue"

    # Worst verdict calculation
    lane_verdicts = {
        "user_flow": user_verdict,
        "evidence_flow": evidence_verdict,
        "business_flow": business_verdict,
    }
    max_sev = max(SEVERITY[v] for v in lane_verdicts.values())
    combined_verdict = VERDICTS[max_sev]

    # Determine weakest flow
    priority = {"evidence_flow": 0, "user_flow": 1, "business_flow": 2}
    def flow_sort(flow):
        return (-SEVERITY[lane_verdicts[flow]], priority[flow])
    weakest_flow = sorted(lane_verdicts.keys(), key=flow_sort)[0]

    return {
        "user_flow": user_verdict,
        "evidence_flow": evidence_verdict,
        "business_flow": business_verdict,
        "evidence_tier": evidence_tier,
        "combined_verdict": combined_verdict,
        "weakest_flow": weakest_flow,
    }


def generate_boundary(state):
    eval_result = evaluate_three_lanes_baseline(state)
    prompt = state.get("prompt", "")
    target_files = state.get("files", [])

    may_do = []
    must_not_do = []
    stop_conditions = []

    if eval_result["combined_verdict"] == "stop_reframe":
        must_not_do.append("Do not implement ungrounded features without observable evidence.")
        stop_conditions.append("Stop immediately and reframe problem hypothesis with user.")
        return {
            "verdict": "stop_reframe",
            "may_do": ["Investigate local evidence or build disposable prototype."],
            "must_not_do": must_not_do,
            "stop_conditions": stop_conditions,
        }

    # Bounded allowed edits
    for f in target_files:
        may_do.append(f"Implement changes inside {f}")

    # Standard negative constraints
    must_not_do.append("Do not modify database schema without explicit migration plan.")
    must_not_do.append("Do not introduce unauthorized external network calls.")
    must_not_do.append("Do not expand scope beyond assigned task package.")

    stop_conditions.append("Stop when scope drift or unverified assumptions appear.")
    stop_conditions.append("Stop if tests fail due to unexpected architectural conflicts.")

    return {
        "verdict": eval_result["combined_verdict"],
        "weakest_flow": eval_result["weakest_flow"],
        "may_do": may_do or ["Implement bounded task as specified."],
        "must_not_do": must_not_do,
        "stop_conditions": stop_conditions,
    }


def call_jev_live(state, questions):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return None
    url = "https://openrouter.ai/api/alpha/decisions"
    payload = {
        "model": "~typesafe/jev-latest",
        "state": state,
        "questions": questions,
    }
    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=5.0) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except (error.URLError, TimeoutError, ValueError):
        return None
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    route_p = subparsers.add_parser("route")
    route_p.add_argument("prompt", help="User intent or task description")
    route_p.add_argument("--live", action="store_true", help="Call live Jev API if available")

    eval_p = subparsers.add_parser("evaluate")
    eval_p.add_argument("--task", required=True, help="Path to task JSON state")
    eval_p.add_argument("--live", action="store_true", help="Call live Jev API if available")

    bound_p = subparsers.add_parser("boundary")
    bound_p.add_argument("--task", required=True, help="Path to task JSON state")

    args = parser.parse_args()

    if args.command == "route":
        route = classify_route_baseline(args.prompt)
        print(json.dumps({"route": route, "bypass": route == "routine"}))
        return 0

    if args.command == "evaluate":
        state = json.loads(Path(args.task).read_text(encoding="utf-8"))
        res = evaluate_three_lanes_baseline(state)
        print(json.dumps(res, indent=2))
        return 0

    if args.command == "boundary":
        state = json.loads(Path(args.task).read_text(encoding="utf-8"))
        res = generate_boundary(state)
        print(json.dumps(res, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
