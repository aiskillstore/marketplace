#!/usr/bin/env python3
"""Assess whether a dialogue-collected student resume ledger is ready to render."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"[0-9][0-9\s()+-]{5,}[0-9]")
FORBIDDEN_PRIVATE_KEYS = {
    "id_card",
    "identity_number",
    "password",
    "token",
    "secret",
    "marital_status",
    "religion",
    "full_address",
}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def private_key_hits(value: Any, prefix: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key).lower() in FORBIDDEN_PRIVATE_KEYS:
                hits.append(path)
            hits.extend(private_key_hits(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(private_key_hits(child, f"{prefix}[{index}]"))
    return hits


def assess(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    next_questions: list[str] = []

    target = data.get("target") if isinstance(data.get("target"), dict) else {}
    if not nonempty(target.get("role")):
        errors.append("缺少明确的目标岗位")
        next_questions.append("你这份简历首先要投哪个岗位或岗位族？")

    basics = data.get("basics") if isinstance(data.get("basics"), dict) else {}
    if not nonempty(basics.get("name")):
        errors.append("缺少姓名")
        next_questions.append("最终简历使用什么姓名？")
    phone = basics.get("phone", "")
    email = basics.get("email", "")
    if not nonempty(phone) or not PHONE_RE.search(str(phone)):
        errors.append("缺少可用手机号")
        next_questions.append("最终简历使用哪个可公开手机号？")
    if not nonempty(email) or not EMAIL_RE.match(str(email).strip()):
        errors.append("缺少可用邮箱")
        next_questions.append("最终简历使用哪个可公开邮箱？")

    education = data.get("education") if isinstance(data.get("education"), list) else []
    valid_education = [
        item
        for item in education
        if isinstance(item, dict)
        and nonempty(item.get("school"))
        and (nonempty(item.get("major")) or nonempty(item.get("degree")))
        and nonempty(item.get("end"))
    ]
    if not valid_education:
        errors.append("缺少可确认的学校、专业或学历、毕业时间")
        next_questions.append("你的学校、专业、学历和预计毕业年月是什么？")

    evidence_items = data.get("evidence_items") if isinstance(data.get("evidence_items"), list) else []
    confirmed_items: list[dict[str, Any]] = []
    ids: set[str] = set()
    for item in evidence_items:
        if not isinstance(item, dict):
            continue
        if nonempty(item.get("id")):
            ids.add(str(item["id"]).strip())
        complete = (
            item.get("status") == "confirmed"
            and nonempty(item.get("id"))
            and nonempty(item.get("name"))
            and nonempty(item.get("ownership"))
            and isinstance(item.get("actions"), list)
            and any(nonempty(action) for action in item.get("actions", []))
            and nonempty(item.get("result"))
            and nonempty(item.get("proof"))
        )
        if complete:
            confirmed_items.append(item)
    if len(confirmed_items) < 2:
        errors.append("至少需要两项形成个人贡献、行动、结果与证据闭环的经历")
        next_questions.append("除当前最强经历外，还有哪项项目、实习、课程、竞赛或校园实践最能证明岗位能力？")

    job_requirements = data.get("job_requirements") if isinstance(data.get("job_requirements"), list) else []
    supported_requirements: list[dict[str, Any]] = []
    requirement_gaps: list[dict[str, Any]] = []
    if target.get("jd_available") is True and not job_requirements:
        errors.append("已提供 JD，但尚未建立要求—证据映射")
        next_questions.append("这份 JD 最关键的硬门槛或职责是什么？我会先关联你已有的事实证据。")
    for index, requirement in enumerate(job_requirements, 1):
        if not isinstance(requirement, dict) or not nonempty(requirement.get("requirement")):
            errors.append(f"job_requirements[{index}] 缺少要求描述")
            continue
        status = requirement.get("status")
        refs = requirement.get("evidence_ids") if isinstance(requirement.get("evidence_ids"), list) else []
        valid_refs = [str(ref).strip() for ref in refs if str(ref).strip() in ids]
        if status == "supported":
            if not valid_refs:
                errors.append(f"job_requirements[{index}] 标记为 supported，但没有关联有效证据")
            else:
                supported_requirements.append(requirement)
        elif status == "gap":
            requirement_gaps.append(requirement)
        else:
            errors.append(f"job_requirements[{index}] status 必须为 supported 或 gap")

    skills = data.get("skills") if isinstance(data.get("skills"), list) else []
    linked_skills = [
        skill
        for skill in skills
        if isinstance(skill, dict)
        and skill.get("status") == "confirmed"
        and nonempty(skill.get("name"))
        and isinstance(skill.get("evidence_ids"), list)
        and any(str(ref).strip() in ids for ref in skill.get("evidence_ids", []))
    ]
    if not linked_skills:
        errors.append("技能尚未关联到可解释的经历证据")
        next_questions.append("你最有把握在面试中解释的技能是什么？它具体用在哪段经历里？")

    uncertainties = data.get("uncertainties") if isinstance(data.get("uncertainties"), list) else []
    blocking = [
        item
        for item in uncertainties
        if isinstance(item, dict) and item.get("blocking") is True and item.get("resolved") is not True
    ]
    if blocking:
        errors.append(f"仍有 {len(blocking)} 项阻断性疑点未解决")
        next_questions.append("先解决事实账本中优先级最高的时间线、归属或数字疑点。")

    confirmation = data.get("confirmation") if isinstance(data.get("confirmation"), dict) else {}
    if confirmation.get("status") != "confirmed":
        errors.append("尚未获得用户对最终事实摘要的明确确认")
        next_questions.append("以上事实可以作为最终简历依据吗？需要改哪一项？")

    private_hits = private_key_hits(data)
    if private_hits:
        errors.append("事实账本包含不应收集的敏感字段：" + ", ".join(private_hits))

    if len(evidence_items) > len(confirmed_items):
        warnings.append(f"{len(evidence_items) - len(confirmed_items)} 项经历尚未形成完整证据闭环")
    if requirement_gaps:
        warnings.append(f"目标岗位仍有 {len(requirement_gaps)} 项明确要求缺口；交付时必须如实说明")

    return {
        "ok": not errors,
        "state": "ready" if not errors else "needs_interview",
        "counts": {
            "education": len(valid_education),
            "evidence_items": len(evidence_items),
            "confirmed_evidence_items": len(confirmed_items),
            "linked_skills": len(linked_skills),
            "job_requirements": len(job_requirements),
            "supported_requirements": len(supported_requirements),
            "requirement_gaps": len(requirement_gaps),
            "blocking_uncertainties": len(blocking),
        },
        "errors": errors,
        "warnings": warnings,
        "next_questions": next_questions[:3],
        "evidence_boundary": "deterministic completeness check; it cannot prove that user-provided facts are true",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="检查对话式简历访谈是否达到最终生成门禁。")
    parser.add_argument("input", help="interview-ledger.json 路径")
    parser.add_argument("--output", "-o", help="写出 JSON 报告")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("interview ledger 根节点必须是对象")
    result = assess(payload)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if not result["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
