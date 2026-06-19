#!/usr/bin/env python3
from pathlib import Path


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by skill_report_model.py to calculate overview report metrics."

REPORT_EVIDENCE = [
    "skill-ir.json",
    "compiled_targets.json",
    "intent-dialogue.json",
    "intent-confidence.json",
    "reference-synthesis.json",
    "output_quality_scorecard.json",
    "conformance_matrix.json",
    "security_trust_report.json",
    "skill_atlas.json",
    "registry_audit.json",
    "package_verification.json",
    "install_simulation.json",
    "upgrade_check.json",
    "adoption_drift_report.json",
    "review_waivers.json",
    "artifact-design-profile.json",
    "prompt-quality-profile.json",
    "system-model.json",
    "iteration-directions.json",
    "output-risk-profile.json",
]


def clamp(value: int) -> int:
    return max(0, min(100, int(value)))


def metric(label: str, score: int, reasons: list[str]) -> dict:
    return {
        "label": label,
        "score": clamp(score),
        "reasons": [reason for reason in reasons if reason],
    }


def text_or_empty(path: Path) -> str:
    if not path.exists() or path.is_dir():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def has_files(path: Path) -> bool:
    return path.exists() and path.is_dir() and any(path.iterdir())


def parse_description(skill_text: str) -> str:
    lines = skill_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    try:
        end_index = lines[1:].index("---") + 1
    except ValueError:
        return ""
    for line in lines[1:end_index]:
        if line.strip().startswith("description:"):
            return line.split(":", 1)[1].strip().strip('"')
    return ""


def approximate_words(text: str) -> int:
    cjk = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
    latin = len([token for token in text.replace("\n", " ").split(" ") if token.strip()])
    return cjk + latin


def completeness_metric(skill_dir: Path) -> dict:
    checks = [
        ("SKILL.md", 22, "SKILL.md 已存在，是 Skill 的入口。"),
        ("README.md", 10, "README.md 已存在，便于人工阅读。"),
        ("agents/interface.yaml", 14, "agents/interface.yaml 已存在，便于跨平台适配。"),
        ("manifest.json", 14, "manifest.json 已存在，生命周期信息可追踪。"),
        ("reports", 14, "reports/ 已存在，生成证据可以随包体迁移。"),
        ("references", 10, "references/ 已存在，长指导可以从入口文件拆出。"),
        ("scripts", 8, "scripts/ 已存在，确定性逻辑有位置承载。"),
        ("evals", 8, "evals/ 已存在，触发或质量检查可以随包体迁移。"),
    ]
    score = 0
    reasons = []
    for rel_path, weight, reason in checks:
        target = skill_dir / rel_path
        exists = target.exists() if target.suffix else has_files(target)
        if rel_path in {"reports", "references", "scripts", "evals"}:
            exists = has_files(target)
        if exists:
            score += weight
            reasons.append(reason)
        else:
            reasons.append(f"{rel_path} 未发现或为空，完整度扣分。")
    return metric("完整度", score, reasons[:5])


def trigger_metric(skill_dir: Path) -> dict:
    skill_text = text_or_empty(skill_dir / "SKILL.md")
    description = parse_description(skill_text)
    score = 0
    reasons = []
    if description:
        score += 35
        reasons.append("frontmatter description 已存在，具备基础路由面。")
    else:
        reasons.append("description 证据不足，触发边界不稳定。")
    if len(description) >= 40:
        score += 20
        reasons.append("description 有足够长度说明任务边界。")
    else:
        reasons.append("description 偏短，建议补充输入、输出或非目标。")
    if any(word in description.lower() for word in ("use", "when", "用于", "不要", "not")):
        score += 15
        reasons.append("description 已包含使用场景或排除边界信号。")
    else:
        reasons.append("description 缺少明确使用场景或排除边界。")
    if has_files(skill_dir / "evals"):
        score += 15
        reasons.append("evals/ 已存在，可承载触发样例或质量检查。")
    else:
        reasons.append("evals/ 证据不足，误触发检查仍偏弱。")
    if (skill_dir / "reports" / "intent-confidence.json").exists():
        score += 15
        reasons.append("intent-confidence 报告已生成，可辅助判断触发稳定性。")
    else:
        reasons.append("intent-confidence 证据不足。")
    return metric("触发清晰", score, reasons[:5])


def evidence_metric(skill_dir: Path) -> dict:
    reports_dir = skill_dir / "reports"
    present = []
    for name in REPORT_EVIDENCE:
        if name == "skill-ir.json":
            if (reports_dir / name).exists() or any((skill_dir / "skill-ir" / "examples").glob("*.json")):
                present.append(name)
            continue
        if (reports_dir / name).exists():
            present.append(name)
    score = round(len(present) / len(REPORT_EVIDENCE) * 100)
    reasons = []
    if present:
        reasons.append(f"已生成 {len(present)} / {len(REPORT_EVIDENCE)} 类报告证据。")
        reasons.extend([f"{name} 已存在。" for name in present[:3]])
    missing = [name for name in REPORT_EVIDENCE if name not in present]
    if missing:
        reasons.append(f"证据不足：缺少 {', '.join(missing[:3])}。")
    return metric("证据充分", score, reasons[:5])


def maintainability_metric(skill_dir: Path) -> dict:
    skill_text = text_or_empty(skill_dir / "SKILL.md")
    words = approximate_words(skill_text)
    score = 35
    reasons = [f"SKILL.md 约 {words} 个词/字。"]
    if words <= 900:
        score += 20
        reasons.append("入口文件保持克制，可维护性较好。")
    else:
        reasons.append("入口文件偏长，建议继续拆到 references/。")
    if has_files(skill_dir / "references"):
        score += 15
        reasons.append("references/ 已承载扩展指导。")
    else:
        reasons.append("references/ 证据不足，长指导可能堆在入口。")
    if has_files(skill_dir / "scripts"):
        score += 15
        reasons.append("scripts/ 已承载确定性逻辑。")
    else:
        reasons.append("scripts/ 证据不足，重复执行逻辑可能仍靠人工。")
    if has_files(skill_dir / "evals"):
        score += 15
        reasons.append("evals/ 已承载可迁移检查。")
    else:
        reasons.append("evals/ 证据不足。")
    return metric("可维护性", score, reasons[:5])


def portability_metric(skill_dir: Path) -> dict:
    score = 0
    reasons = []
    if (skill_dir / "agents" / "interface.yaml").exists():
        score += 35
        reasons.append("agents/interface.yaml 已存在。")
    else:
        reasons.append("agents/interface.yaml 证据不足，跨平台接口不清晰。")
    if (skill_dir / "manifest.json").exists():
        score += 25
        reasons.append("manifest.json 已存在。")
    else:
        reasons.append("manifest.json 证据不足，生命周期信息不完整。")
    manifest_text = text_or_empty(skill_dir / "manifest.json")
    interface_text = text_or_empty(skill_dir / "agents" / "interface.yaml")
    if any(target in manifest_text + interface_text for target in ("openai", "claude", "generic")):
        score += 25
        reasons.append("目标平台或 adapter target 已声明。")
    else:
        reasons.append("目标平台证据不足。")
    skill_text = text_or_empty(skill_dir / "SKILL.md")
    if "/Users/" not in skill_text and "C:\\" not in skill_text:
        score += 15
        reasons.append("入口文件未发现明显私有绝对路径。")
    else:
        reasons.append("入口文件含私有绝对路径，迁移风险较高。")
    return metric("可迁移性", score, reasons[:5])


def context_cost_metric(skill_dir: Path) -> dict:
    skill_words = approximate_words(text_or_empty(skill_dir / "SKILL.md"))
    reference_words = 0
    references = skill_dir / "references"
    if references.exists():
        for path in references.rglob("*"):
            if path.is_file():
                reference_words += approximate_words(text_or_empty(path))
    total = skill_words + reference_words
    if total <= 900:
        score = 95
    elif total <= 1800:
        score = 78
    elif total <= 3200:
        score = 60
    else:
        score = 42
    reasons = [
        f"入口约 {skill_words} 个词/字，references 约 {reference_words} 个词/字。",
        "分数越高代表上下文成本越低。",
    ]
    if total > 1800:
        reasons.append("上下文成本偏高，建议压缩入口或拆分 references。")
    else:
        reasons.append("上下文成本处于可控区间。")
    return metric("上下文成本", score, reasons)


def calculate_scorecard(skill_dir: Path) -> dict:
    skill_dir = skill_dir.resolve()
    return {
        "completeness_score": completeness_metric(skill_dir),
        "trigger_score": trigger_metric(skill_dir),
        "evidence_score": evidence_metric(skill_dir),
        "maintainability_score": maintainability_metric(skill_dir),
        "portability_score": portability_metric(skill_dir),
        "context_cost": context_cost_metric(skill_dir),
    }
