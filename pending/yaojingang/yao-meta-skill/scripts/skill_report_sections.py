SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by skill_report_model.py to assemble overview report quality, risk, and asset sections."


def artifact_design_highlights(profile: dict) -> list[str]:
    primary = profile.get("primary_artifact", {})
    highlights = []
    if primary.get("direction"):
        highlights.append(primary["direction"])
    highlights.extend(profile.get("quality_gates", [])[:3])
    return highlights[:4]


def prompt_quality_highlights(profile: dict) -> list[str]:
    highlights = []
    primary = profile.get("primary_task_family", {})
    complexity = profile.get("complexity", {})
    if primary.get("label"):
        highlights.append(f"Primary prompt task family: {primary['label']}.")
    if complexity.get("band"):
        highlights.append(f"Complexity: {complexity['band']} — {complexity.get('reason', '')}")
    for item in profile.get("quality_matrix", [])[:2]:
        highlights.append(f"{item.get('label', 'Quality')}: {item.get('score', 'n/a')}/100.")
    return highlights[:4]


def system_model_highlights(model: dict) -> list[str]:
    highlights = []
    stability = model.get("stability", {})
    if stability:
        highlights.append(f"Stability: {stability.get('band', 'unknown')} ({stability.get('score', 'n/a')}/100).")
    boundary = model.get("boundary_map", {})
    if boundary.get("owned_job"):
        highlights.append(f"Owned job: {boundary['owned_job']}")
    for point in model.get("leverage_points", [])[:2]:
        if point.get("point"):
            highlights.append(f"Leverage: {point['point']} — {point.get('move', '')}")
    return highlights[:4]


def risk_governance(output_risk: dict, system_model: dict, scorecard: dict) -> dict:
    risk_names = [
        ("误触发风险", "trigger_score"),
        ("输出漂移风险", "evidence_score"),
        ("证据不足风险", "evidence_score"),
        ("包体膨胀风险", "maintainability_score"),
        ("跨平台迁移风险", "portability_score"),
    ]
    risks = []
    for index, (name, metric_key) in enumerate(risk_names):
        score = scorecard.get(metric_key, {}).get("score", 50)
        probability = max(1, min(3, 4 - round(score / 34)))
        impact = 3 if index in {0, 2, 4} else 2
        risks.append(
            {
                "name": name,
                "impact": impact,
                "probability": probability,
                "signal": scorecard.get(metric_key, {}).get("reasons", ["证据不足"])[0],
                "response": "先补证据和边界，再增加包体复杂度。",
            }
        )
    human_boundary = system_model.get("boundary_map", {}).get("human_judgment_boundary", [])
    return {
        "risks": risks,
        "risk_families": output_risk.get("risk_families", []),
        "human_judgment_boundary": human_boundary,
    }


def quality_review(
    strengths: list[str],
    scorecard: dict,
    artifact_design: dict,
    prompt_quality: dict,
    system_model: dict,
) -> dict:
    gaps = []
    for key, payload in scorecard.items():
        if payload.get("score", 0) < 70:
            gaps.append(f"{payload.get('label', key)}需要补强：{payload.get('reasons', ['证据不足'])[0]}")
    return {
        "strengths": strengths,
        "gaps": gaps or ["当前关键证据较完整，优先保持轻量。"],
        "recommendations": [
            "先改触发边界，再扩展工作流。",
            "只把重复且稳定的步骤沉淀为脚本。",
            "每次升级后重新生成报告并检查分数原因。",
        ],
        "artifact_design": {
            "design_system": artifact_design.get("design_system", "content-led editorial"),
            "highlights": artifact_design_highlights(artifact_design),
        },
        "prompt_quality": {
            "overall_quality_score": prompt_quality.get("overall_quality_score", "n/a"),
            "highlights": prompt_quality_highlights(prompt_quality),
        },
        "system_model": {
            "stability": system_model.get("stability", {}),
            "highlights": system_model_highlights(system_model),
        },
    }


def package_assets(package_map: list[dict]) -> dict:
    files = sum(item.get("file_count", 0) for item in package_map if item.get("kind") == "file")
    folders = [item for item in package_map if item.get("kind") == "folder"]
    distribution = [{"label": item["path"], "value": max(1, item.get("file_count", 1))} for item in package_map]
    return {
        "entries": package_map,
        "file_count": files + sum(item.get("file_count", 0) for item in folders),
        "folder_count": len(folders),
        "distribution": distribution,
    }
