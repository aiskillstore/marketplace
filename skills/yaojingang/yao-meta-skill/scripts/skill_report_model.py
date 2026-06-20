#!/usr/bin/env python3
from datetime import date
from pathlib import Path

from skill_ir_paths import find_skill_ir
from skill_report_metrics import calculate_scorecard
from skill_report_sources import (
    extract_title,
    load_json,
    load_yaml,
    package_entries,
    parse_frontmatter,
    parse_sections,
    summarize_logic,
    summarize_usage,
)
from skill_report_sections import package_assets, quality_review, risk_governance
from skill_report_world_class import world_class_readiness, world_class_roadmap_item


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by render_skill_overview.py to build the v2 report data model."

REPORT_NAV_V2 = [
    {"label": "技能概述", "label_en": "Overview", "href": "overview"},
    {"label": "总览指标", "label_en": "Metrics", "href": "metrics"},
    {"label": "能力画像", "label_en": "Profile", "href": "capability"},
    {"label": "原理结构", "label_en": "Principle", "href": "principle"},
    {"label": "契约边界", "label_en": "Contract", "href": "contract"},
    {"label": "质量评估", "label_en": "Quality", "href": "quality"},
    {"label": "风险治理", "label_en": "Risk", "href": "risk"},
    {"label": "包体资产", "label_en": "Assets", "href": "assets"},
    {"label": "迭代路线", "label_en": "Roadmap", "href": "roadmap"},
]


def context_payload(intent: dict) -> dict:
    context = intent.get("context", {}) if isinstance(intent, dict) else {}
    return context if isinstance(context, dict) else {}


def as_text_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def compact_unique(items: list[str], limit: int = 6) -> list[str]:
    seen = set()
    result = []
    for item in items:
        normalized = str(item).strip()
        if not normalized or normalized.lower() in seen:
            continue
        seen.add(normalized.lower())
        result.append(normalized)
        if len(result) >= limit:
            break
    return result


def derive_strengths(skill_dir: Path, metadata: dict) -> list[str]:
    strengths = ["触发面保持精简，并锚定在 frontmatter description。"]
    if (skill_dir / "reports" / "skill-ir.json").exists() or (skill_dir / "skill-ir" / "examples").exists():
        strengths.append("已生成 Skill IR，核心语义可先于平台打包被审查和迁移。")
    if (skill_dir / "reports" / "compiled_targets.json").exists():
        strengths.append("已生成目标编译报告，可审查 IR 到 OpenAI、Claude、generic 等目标契约的映射。")
    if (skill_dir / "reports" / "output_quality_scorecard.json").exists():
        strengths.append("已生成 Output Eval Lab scorecard，可比较 with-skill 与 baseline 输出质量。")
    if (skill_dir / "reports" / "output_execution_runs.json").exists():
        strengths.append("已生成 Output Execution Runs，可区分记录样本、命令执行和模型执行证据。")
    if (skill_dir / "reports" / "output_review_adjudication.json").exists():
        strengths.append("已生成 Output Review Adjudication，可记录盲评决策、一致率和待评审项。")
    if (skill_dir / "reports" / "conformance_matrix.json").exists():
        strengths.append("已生成 Runtime Conformance Matrix，可审查目标端消费能力。")
    if (skill_dir / "reports" / "security_trust_report.json").exists():
        strengths.append("已生成 Security Trust Report，可审查脚本、依赖、secret 和包完整性风险。")
    if (skill_dir / "reports" / "skill_atlas.json").exists():
        strengths.append("已生成 Skill Atlas，可审查多 Skill 组合中的路由冲突、过期资产和 owner 缺口。")
    if (skill_dir / "reports" / "registry_audit.json").exists():
        strengths.append("已生成 Registry Audit，可审查版本、owner、license、checksum 和目标兼容矩阵。")
    if (skill_dir / "reports" / "install_simulation.json").exists():
        strengths.append("已生成 Install Simulation，可审查 zip 解压、入口加载、接口元数据和 adapter 可读性。")
    if (skill_dir / "reports" / "adoption_drift_report.json").exists():
        strengths.append("已生成 Adoption Drift Report，可把本地使用反馈转为下一轮迭代信号。")
    if (skill_dir / "reports" / "review_waivers.json").exists():
        strengths.append("已生成 Review Waivers 台账，可记录 reviewer 对 warning 风险的批准、理由和到期时间。")
    if (skill_dir / "reports" / "review_annotations.json").exists():
        strengths.append("已生成 Review Annotations 台账，可把 reviewer 批注挂到 gate、文件和行号。")
    if (skill_dir / "reports" / "review-studio.json").exists():
        strengths.append("已生成 Review Studio 2.0，可在一页中查看 blocker、warning、证据路径和发布闸门。")
    if (skill_dir / "agents" / "interface.yaml").exists():
        strengths.append("已打包 agents/interface.yaml，便于后续做跨平台适配。")
    if (skill_dir / "references").exists() and any((skill_dir / "references").iterdir()):
        strengths.append("长指导被拆到 references 中，入口文件可以保持轻量。")
    if (skill_dir / "scripts").exists() and any((skill_dir / "scripts").iterdir()):
        strengths.append("确定性辅助逻辑放在 scripts 中，而不是藏在提示词里。")
    if (skill_dir / "evals").exists() and any((skill_dir / "evals").iterdir()):
        strengths.append("包内包含可随 Skill 迁移的质量门禁或触发检查。")
    if metadata.get("maturity_tier"):
        strengths.append(f"生命周期元数据清晰，成熟度层级为 `{metadata['maturity_tier']}`。")
    return strengths[:6]


def scenario_items(description: str, usage_steps: list[str], metadata: dict) -> list[str]:
    scenarios = []
    if "workflow" in description.lower() or "流程" in description:
        scenarios.append("把重复流程沉淀为可复用的 agent skill。")
    if "prompt" in description.lower() or "提示" in description:
        scenarios.append("把分散提示词、对话记录或操作规范整理为稳定能力。")
    if metadata.get("maturity_tier") in {"production", "library", "governed"}:
        scenarios.append("团队复用前，需要明确触发边界、质量证据和维护责任。")
    if usage_steps:
        scenarios.append(f"用户说出类似需求时：{usage_steps[0]}")
    scenarios.append("已有原始资料，但还没有清晰输入、输出和后续迭代路径。")
    return compact_unique(scenarios, limit=4)


def trigger_contract(interface_data: dict, description: str) -> dict:
    compatibility = interface_data.get("compatibility", {})
    activation = compatibility.get("activation", {})
    execution = compatibility.get("execution", {})
    return {
        "description": description,
        "activation": activation.get("mode", "manual"),
        "execution": execution.get("context", "inline"),
        "shell": execution.get("shell", "bash"),
    }


def io_contract(intent: dict, package_map: list[dict], description: str) -> dict:
    context = context_payload(intent)
    inputs = as_text_list(context.get("real_inputs")) or [
        "用户提供的工作流、提示词、文档、记录或散乱笔记",
        "期望沉淀的复用场景、排除项、约束和质量标准",
    ]
    outputs = as_text_list(context.get("primary_output")) or [
        "可路由的 SKILL.md",
        "agents/interface.yaml 元数据",
        "必要的 references、scripts、evals、reports 证据",
    ]
    if package_map:
        outputs.append(f"结构化 Skill 目录，共 {len(package_map)} 类关键资产。")
    if description and not outputs:
        outputs.append(f"围绕该能力边界交付：{description}")
    return {
        "inputs": compact_unique(inputs, limit=5),
        "outputs": compact_unique(outputs, limit=5),
    }


def principle_nodes(system_model: dict) -> list[dict]:
    boundary = system_model.get("boundary_map", {}) if isinstance(system_model, dict) else {}
    loops = system_model.get("feedback_loops", []) if isinstance(system_model, dict) else []
    drift = system_model.get("drift_watch", []) if isinstance(system_model, dict) else []
    leverage = system_model.get("leverage_points", []) if isinstance(system_model, dict) else []
    return [
        {"title": "意图澄清", "body": boundary.get("owned_job", "先确认真实任务、输入材料和交付结果。")},
        {"title": "边界路由", "body": "用 frontmatter description 决定是否触发，并写明相邻非目标。"},
        {"title": "资产分层", "body": "把入口、参考、脚本、评估和报告拆到各自目录，避免 SKILL.md 膨胀。"},
        {
            "title": "证据回路",
            "body": loops[0].get("response") if loops else "通过评估、报告和复盘把真实使用反馈变成下一轮改进。",
        },
        {
            "title": "漂移观察",
            "body": drift[0].get("countermeasure") if drift else "持续观察触发漂移、输出漂移和治理漂移。",
        },
        {
            "title": "杠杆升级",
            "body": leverage[0].get("move") if leverage else "优先改边界、触发和一个最小自修复检查。",
        },
    ]


def roadmap_items(iteration: dict, readiness: dict | None = None) -> list[dict]:
    directions = iteration.get("directions", []) if isinstance(iteration, dict) else []
    items = []
    evidence_item = world_class_roadmap_item(readiness or {})
    if evidence_item:
        items.append(evidence_item)
    for item in directions[:3]:
        items.append(
            {
                "title": item.get("title", "下一步"),
                "why": item.get("why", "提升复用稳定性。"),
                "actions": item.get("actions", [])[:3],
                "unlocks": item.get("unlocks", ""),
            }
        )
        if len(items) >= 3:
            break
    if items:
        return items
    return [
        {
            "title": "收紧触发",
            "why": "先让 Skill 在正确场景被调用，再扩展资产。",
            "actions": ["增加正例、反例和近邻用例。", "压缩 frontmatter description。"],
            "unlocks": "更稳定的路由边界。",
        }
    ]


def capability_profile(manifest: dict, interface_data: dict, prompt_quality: dict) -> dict:
    maturity = manifest.get("maturity_tier", "scaffold")
    task_family = prompt_quality.get("primary_task_family", {}).get("label", "Skill workflow")
    execution = interface_data.get("compatibility", {}).get("execution", {})
    adapter_targets = interface_data.get("compatibility", {}).get("adapter_targets", [])
    certainty = 72 if execution.get("context", "inline") == "inline" else 58
    knowledge = 80 if prompt_quality.get("complexity", {}).get("band") in {"expert", "complex"} else 62
    return {
        "archetype": manifest.get("skill_archetype", maturity),
        "task_family": task_family,
        "maturity": maturity,
        "trigger_strength": "手动触发 + description 路由",
        "reuse_scope": "跨平台" if len(adapter_targets) >= 2 else "本地复用",
        "matrix": {"execution_certainty": certainty, "knowledge_density": knowledge},
    }


def build_report_model(skill_dir: Path) -> dict:
    skill_dir = skill_dir.resolve()
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(skill_text)
    sections = parse_sections(body)
    interface_data = load_yaml(skill_dir / "agents" / "interface.yaml")
    manifest = load_json(skill_dir / "manifest.json")
    intent = load_json(skill_dir / "reports" / "intent-confidence.json")
    artifact_design = load_json(skill_dir / "reports" / "artifact-design-profile.json")
    prompt_quality = load_json(skill_dir / "reports" / "prompt-quality-profile.json")
    system_model = load_json(skill_dir / "reports" / "system-model.json")
    output_risk = load_json(skill_dir / "reports" / "output-risk-profile.json")
    output_quality = load_json(skill_dir / "reports" / "output_quality_scorecard.json")
    output_execution = load_json(skill_dir / "reports" / "output_execution_runs.json")
    output_blind_review = load_json(skill_dir / "reports" / "output_blind_review_pack.json")
    output_review_kit = load_json(skill_dir / "reports" / "output_review_kit.json")
    output_review_adjudication = load_json(skill_dir / "reports" / "output_review_adjudication.json")
    benchmark_reproducibility = load_json(skill_dir / "reports" / "benchmark_reproducibility.json")
    conformance = load_json(skill_dir / "reports" / "conformance_matrix.json")
    runtime_permissions = load_json(skill_dir / "reports" / "runtime_permission_probes.json")
    trust_report = load_json(skill_dir / "reports" / "security_trust_report.json")
    skill_atlas = load_json(skill_dir / "reports" / "skill_atlas.json")
    registry_audit = load_json(skill_dir / "reports" / "registry_audit.json")
    package_verification = load_json(skill_dir / "reports" / "package_verification.json")
    install_simulation = load_json(skill_dir / "reports" / "install_simulation.json")
    upgrade_check = load_json(skill_dir / "reports" / "upgrade_check.json")
    adoption_drift = load_json(skill_dir / "reports" / "adoption_drift_report.json")
    review_waivers = load_json(skill_dir / "reports" / "review_waivers.json")
    review_annotations = load_json(skill_dir / "reports" / "review_annotations.json")
    world_class_evidence = load_json(skill_dir / "reports" / "world_class_evidence_plan.json")
    world_class_evidence_ledger = load_json(skill_dir / "reports" / "world_class_evidence_ledger.json")
    compiled_targets = load_json(skill_dir / "reports" / "compiled_targets.json")
    reference_synthesis = load_json(skill_dir / "reports" / "reference-synthesis.json")
    iteration = load_json(skill_dir / "reports" / "iteration-directions.json")

    name = frontmatter.get("name", skill_dir.name)
    skill_ir, skill_ir_path = find_skill_ir(skill_dir, name)
    description = frontmatter.get("description", "No description found.")
    title = extract_title(body, name.replace("-", " ").title())
    display_name = interface_data.get("interface", {}).get("display_name", title)
    default_prompt = interface_data.get("interface", {}).get("default_prompt", "")
    logic_steps = summarize_logic(sections)
    usage_steps = summarize_usage(sections, default_prompt, description)
    package_map = package_entries(skill_dir)
    scorecard = calculate_scorecard(skill_dir)
    strengths = derive_strengths(skill_dir, manifest)
    trigger = trigger_contract(interface_data, description)
    io = io_contract(intent, package_map, description)
    principles = principle_nodes(system_model)
    readiness = world_class_readiness(world_class_evidence_ledger)
    roadmap = roadmap_items(iteration, readiness)
    metadata = {
        "canonical_format": interface_data.get("compatibility", {}).get("canonical_format", "agent-skills"),
        "targets": interface_data.get("compatibility", {}).get("adapter_targets", []),
        "maturity_tier": manifest.get("maturity_tier", "scaffold"),
        "skill_archetype": manifest.get("skill_archetype", manifest.get("maturity_tier", "scaffold")),
        "updated_at": manifest.get("updated_at", str(date.today())),
    }
    deliverables = [
        "SKILL.md",
        "agents/interface.yaml",
        skill_ir_path or "reports/skill-ir.json",
        "reports/compiled_targets.md",
        "reports/output_quality_scorecard.md",
        "reports/conformance_matrix.md",
        "reports/security_trust_report.md",
        "reports/skill_atlas.html",
        "reports/registry_audit.md",
        "reports/package_verification.md",
        "reports/install_simulation.md",
        "reports/upgrade_check.md",
        "reports/adoption_drift_report.md",
        "reports/review_waivers.md",
        "reports/review_annotations.md",
        "reports/review-studio.html",
        "reports/skill-interpretation.html",
        "reports/skill-overview.html",
    ]
    if (skill_dir / "reports" / "runtime_permission_probes.md").exists():
        insert_after = deliverables.index("reports/security_trust_report.md") + 1
        deliverables.insert(insert_after, "reports/runtime_permission_probes.md")
    if (skill_dir / "reports" / "output_blind_review_pack.md").exists():
        insert_after = deliverables.index("reports/output_quality_scorecard.md") + 1
        deliverables.insert(insert_after, "reports/output_blind_review_pack.md")
    if (skill_dir / "reports" / "output_execution_runs.md").exists():
        insert_after = deliverables.index("reports/output_quality_scorecard.md") + 1
        deliverables.insert(insert_after, "reports/output_execution_runs.md")
    if (skill_dir / "reports" / "output_blind_answer_key.json").exists():
        insert_after = deliverables.index("reports/output_blind_review_pack.md") + 1 if "reports/output_blind_review_pack.md" in deliverables else deliverables.index("reports/output_quality_scorecard.md") + 1
        deliverables.insert(insert_after, "reports/output_blind_answer_key.json")
    if (skill_dir / "reports" / "output_review_kit.md").exists():
        insert_after = deliverables.index("reports/output_blind_review_pack.md") + 1 if "reports/output_blind_review_pack.md" in deliverables else deliverables.index("reports/output_quality_scorecard.md") + 1
        deliverables.insert(insert_after, "reports/output_review_kit.md")
    if (skill_dir / "reports" / "output_review_adjudication.md").exists():
        insert_after = deliverables.index("reports/output_review_kit.md") + 1 if "reports/output_review_kit.md" in deliverables else deliverables.index("reports/output_quality_scorecard.md") + 1
        deliverables.insert(insert_after, "reports/output_review_adjudication.md")
    if (skill_dir / "reports" / "benchmark_reproducibility.md").exists():
        insert_after = deliverables.index("reports/output_review_adjudication.md") + 1 if "reports/output_review_adjudication.md" in deliverables else deliverables.index("reports/output_quality_scorecard.md") + 1
        deliverables.insert(insert_after, "reports/benchmark_reproducibility.md")
    if (skill_dir / "reports" / "world_class_evidence_plan.md").exists():
        insert_after = deliverables.index("reports/review_waivers.md") + 1
        deliverables.insert(insert_after, "reports/world_class_evidence_plan.md")
    if (skill_dir / "reports" / "world_class_evidence_ledger.md").exists():
        insert_after = (
            deliverables.index("reports/world_class_evidence_plan.md") + 1
            if "reports/world_class_evidence_plan.md" in deliverables
            else deliverables.index("reports/review_waivers.md") + 1
        )
        deliverables.insert(insert_after, "reports/world_class_evidence_ledger.md")

    skill_summary = {
        "name": name,
        "title": title,
        "display_name": display_name,
        "description": description,
        "maturity": metadata["maturity_tier"],
        "updated_at": metadata["updated_at"],
        "core_value": "把一次性经验沉淀为可复用、可评估、可迁移的 Skill 包体。",
        "audience": "Skill 作者、复用团队和后续 reviewer。",
        "deliverables": deliverables,
        "flow": ["输入材料", "Skill 包体", "可复用能力"],
    }
    contract = {
        "trigger": trigger,
        "inputs": io["inputs"],
        "outputs": io["outputs"],
        "should_trigger": scenario_items(description, usage_steps, manifest)[:3],
        "should_not_trigger": [
            "只需要一次性回答、没有复用价值的临时请求。",
            "要求直接执行相邻任务，而不是沉淀或使用这个 Skill。",
            "缺少必要事实且用户不允许澄清的场景。",
        ],
        "boundary_cards": [
            {"label": "Owned", "body": description},
            {"label": "Adjacent", "body": "相邻任务需要先确认是否应转为独立 Skill。"},
            {"label": "Excluded", "body": "不替代人工事实核查，也不静默扩大职责。"},
        ],
    }
    synthesis = reference_synthesis.get("synthesis", {}).get("borrow_now", [])[:3]
    q_review = quality_review(strengths, scorecard, artifact_design, prompt_quality, system_model)
    report_contract = {
        "schema_version": "2.0",
        "html_report": "reports/skill-overview.html",
        "language": "zh-CN",
        "default_language": "zh-CN",
        "languages": ["zh-CN", "en"],
        "layout": "kami-white-audit-v2",
        "nav_labels": [item["label"] for item in REPORT_NAV_V2],
        "nav_labels_en": [item["label_en"] for item in REPORT_NAV_V2],
    }
    model = {
        "skill_summary": skill_summary,
        "scorecard": scorecard,
        "capability_profile": capability_profile(manifest, interface_data, prompt_quality),
        "principle_model": {"nodes": principles, "layers": ["入口层", "参考层", "脚本层", "评估层", "报告层"]},
        "contract_boundary": contract,
        "quality_review": q_review,
        "risk_governance": risk_governance(output_risk, system_model, scorecard),
        "world_class_readiness": readiness,
        "package_assets": package_assets(package_map),
        "iteration_roadmap": {"items": roadmap},
        "report_contract": report_contract,
        # Backward-compatible fields consumed by existing review tooling.
        "name": name,
        "title": title,
        "display_name": display_name,
        "description": description,
        "logic_steps": logic_steps,
        "usage_steps": usage_steps,
        "package_map": package_map,
        "strengths": strengths,
        "scenarios": scenario_items(description, usage_steps, manifest),
        "trigger_contract": trigger,
        "io_contract": io,
        "principles": principles,
        "roadmap": roadmap,
        "cards": [],
        "introduction": [
            "这份报告用于快速理解新生成 Skill 的定位、原理、触发边界和交付内容。",
            "先确认重复任务、真实输入形态和可交付输出，再决定是否继续加 references、scripts 或 evals。",
            "如果需求仍然模糊，优先回到 intent dialogue 收紧边界，再扩展包体结构。",
        ],
        "benchmark_highlights": [],
        "skill_ir": {
            "schema_version": skill_ir.get("schema_version", ""),
            "source_path": skill_ir_path,
            "target_count": len(skill_ir.get("targets", [])),
            "trigger_samples": len(skill_ir.get("trigger_surface", {}).get("should_trigger", [])),
            "output_eval_cases": len(skill_ir.get("eval_plan", {}).get("output", [])),
        },
        "compiled_targets": {
            "ok": compiled_targets.get("ok", False),
            "schema_version": compiled_targets.get("schema_version", ""),
            "summary": compiled_targets.get("summary", {}),
            "targets": [
                {
                    "target": item.get("target", ""),
                    "status": item.get("status", ""),
                    "adapter_mode": item.get("target_transform", {}).get("adapter_mode", ""),
                    "degradation_strategy": item.get("target_transform", {}).get("degradation_strategy", ""),
                    "native_surface": item.get("target_native_contract", {}).get("native_surface", ""),
                    "permission_enforcement": item.get("target_native_contract", {}).get("permissions", {}).get("enforcement", ""),
                    "generated_files": item.get("target_transform", {}).get("generated_files", []),
                    "unsupported_features": item.get("unsupported_features", []),
                    "warnings": item.get("warnings", []),
                }
                for item in compiled_targets.get("targets", [])
                if isinstance(item, dict)
            ],
            "failures": compiled_targets.get("failures", []),
            "warnings": compiled_targets.get("warnings", []),
        },
        "output_quality": output_quality.get("summary", {}),
        "output_execution": {
            "ok": output_execution.get("ok", False),
            "summary": output_execution.get("summary", {}),
            "runner": output_execution.get("runner", {}),
            "failures": output_execution.get("failures", []),
        },
        "output_blind_review": {
            "summary": output_blind_review.get("summary", {}),
            "seed": output_blind_review.get("seed", ""),
            "pair_count": output_blind_review.get("summary", {}).get("pair_count", 0),
            "answer_key_separate": output_blind_review.get("summary", {}).get("answer_key_separate", False),
        },
        "output_review_kit": {
            "ok": output_review_kit.get("ok", False),
            "summary": output_review_kit.get("summary", {}),
            "artifacts": output_review_kit.get("artifacts", {}),
            "failures": output_review_kit.get("failures", []),
        },
        "output_review_adjudication": {
            "ok": output_review_adjudication.get("ok", False),
            "summary": output_review_adjudication.get("summary", {}),
            "reviewer": output_review_adjudication.get("reviewer", ""),
            "reviewed_at": output_review_adjudication.get("reviewed_at", ""),
            "failures": output_review_adjudication.get("failures", []),
        },
        "benchmark_reproducibility": {
            "ok": benchmark_reproducibility.get("ok", False),
            "summary": benchmark_reproducibility.get("summary", {}),
            "commit": benchmark_reproducibility.get("commit", ""),
            "missing_artifacts": benchmark_reproducibility.get("missing_artifacts", []),
            "limitations": benchmark_reproducibility.get("limitations", []),
        },
        "runtime_conformance": conformance.get("summary", {}),
        "runtime_permissions": {
            "ok": runtime_permissions.get("ok", False),
            "summary": runtime_permissions.get("summary", {}),
            "expected_capabilities": runtime_permissions.get("expected_capabilities", []),
            "targets": [
                {
                    "target": item.get("target", ""),
                    "status": item.get("status", ""),
                    "assurance": item.get("assurance", ""),
                    "native_enforcement": item.get("native_enforcement"),
                    "metadata_fallback_explicit": item.get("metadata_fallback_explicit", False),
                    "residual_risks": item.get("residual_risks", []),
                }
                for item in runtime_permissions.get("targets", [])
                if isinstance(item, dict)
            ],
            "failures": runtime_permissions.get("failures", []),
        },
        "trust_security": trust_report.get("summary", {}),
        "skill_atlas": skill_atlas.get("summary", {}),
        "registry_distribution": {
            "ok": registry_audit.get("ok", False),
            "package": registry_audit.get("package", {}),
            "failures": registry_audit.get("failures", []),
            "warnings": registry_audit.get("warnings", []),
        },
        "package_verification": {
            "ok": package_verification.get("ok", False),
            "summary": package_verification.get("summary", {}),
            "failures": package_verification.get("failures", []),
            "warnings": package_verification.get("warnings", []),
        },
        "install_simulation": {
            "ok": install_simulation.get("ok", False),
            "summary": install_simulation.get("summary", {}),
            "failures": install_simulation.get("failures", []),
            "warnings": install_simulation.get("warnings", []),
        },
        "upgrade_check": {
            "ok": upgrade_check.get("ok", False),
            "summary": upgrade_check.get("summary", {}),
            "upgrade_diff": upgrade_check.get("upgrade_diff", {}),
            "release_notes": upgrade_check.get("release_notes", []),
            "failures": upgrade_check.get("failures", []),
            "warnings": upgrade_check.get("warnings", []),
        },
        "adoption_drift": {
            "ok": adoption_drift.get("ok", False),
            "summary": adoption_drift.get("summary", {}),
            "next_iteration_candidates": adoption_drift.get("next_iteration_candidates", []),
            "privacy_contract": adoption_drift.get("privacy_contract", {}),
            "failures": adoption_drift.get("failures", []),
        },
        "review_waivers": {
            "ok": review_waivers.get("ok", False),
            "summary": review_waivers.get("summary", {}),
            "policy": review_waivers.get("policy", {}),
            "failures": review_waivers.get("failures", []),
            "warnings": review_waivers.get("warnings", []),
        },
        "review_annotations": {
            "ok": review_annotations.get("ok", False),
            "summary": review_annotations.get("summary", {}),
            "annotations": review_annotations.get("annotations", [])[:8],
            "failures": review_annotations.get("failures", []),
        },
        "world_class_evidence_plan": {
            "ok": world_class_evidence.get("ok", False),
            "summary": world_class_evidence.get("summary", {}),
            "tasks": world_class_evidence.get("tasks", [])[:8],
            "source_audit": world_class_evidence.get("source_audit", {}),
        },
        "world_class_evidence_ledger": {
            "ok": world_class_evidence_ledger.get("ok", False),
            "summary": world_class_evidence_ledger.get("summary", {}),
            "entries": world_class_evidence_ledger.get("entries", [])[:8],
            "source_plan": world_class_evidence_ledger.get("source_plan", {}),
        },
        "synthesis_highlights": synthesis,
        "artifact_design": q_review["artifact_design"],
        "prompt_quality": q_review["prompt_quality"],
        "system_model": q_review["system_model"],
        "metadata": metadata,
    }
    return model
