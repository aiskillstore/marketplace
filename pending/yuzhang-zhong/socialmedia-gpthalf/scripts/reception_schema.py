"""Validation for blind Human Reception assessments."""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any


METHOD = "stance_personas_v1"
VALIDATION_PROFILE = "grounded_reception_v1"
PERSONAS = {"supporter", "neutral", "skeptic"}
RISKS = {"low", "medium", "high", "unknown"}
DIMENSIONS = {
    "specificity",
    "genericness",
    "emotional_fit",
    "reader_agency",
    "credibility_friction",
    "platform_fit",
    "commercial_pressure",
    "disclosure_expectation",
    "media_text_fit",
    "empathy",
}
BANNED_KEYS = {
    "rewrite",
    "rewritten_text",
    "suggested_copy",
    "improved_version",
    "replacement_post",
    "human_score",
    "human_likeness_score",
    "aversion_score",
    "protected_traits",
    "protected_attributes",
    "demographics",
    "diagnosis",
    "psychological_diagnosis",
    "detector_evasion",
    "evasion_advice",
    "humanization_advice",
}
BANNED_KEY_FRAGMENTS = {
    "bypass",
    "diagnos",
    "evasion",
    "humanize",
    "humanization",
    "protected_attribute",
    "protected_trait",
}
TOP_LEVEL_KEYS = {
    "method", "audience_assumptions", "reader_views", "cross_reader_patterns", "uncertainties"
}
VIEW_KEYS = {
    "persona", "likely_reaction", "aversion_risk", "friction_points", "positive_signals", "uncertainty"
}
FRICTION_KEYS = {"dimension", "excerpt", "reason"}
CONCLUSION_KEYS = {"statement", "excerpt", "evidence", "reason", "personas"}
EVIDENCE_KEYS = {"kind", "locator", "detail"}

PROHIBITED_TEXT_PATTERNS = (
    (
        "unsupported author-attribute inference",
        re.compile(
            r"(?i)\b(?:author|writer|poster|creator|user)\b.{0,20}"
            r"\b(?:is|seems|appears|looks|must be|likely is|probably is)\b"
            r"(?!\s*(?:unknown|unclear|not known|not visible|unavailable)\b)\s*.{1,80}"
            r"|(?:作者|发帖者|创作者|用户).{0,12}(?:是|属于|看起来是|似乎是|很可能是)"
            r"(?!(?:未知|不明|无法判断|不可见)).{1,40}"
        ),
    ),
    (
        "protected-attribute inference",
        re.compile(
            r"(?i)(?:infer|assume|suggests?|indicates?|likely|probably).{0,48}"
            r"\b(?:race|ethnicity|nationality|religion|gender|sex|sexual orientation|age|disability)\b"
            r"|\b(?:author|writer|poster|creator|user)(?:'s| is| appears)?[^.。]{0,32}"
            r"\b(?:race|ethnicity|nationality|religion|gender|sex|sexual orientation|age|disabled|disability)\b"
            r"|(?:推断|判断|猜测|说明|看出).{0,32}(?:种族|民族|国籍|宗教|性别|性取向|年龄|残障|残疾)"
            r"|(?:作者|发帖者|创作者|用户).{0,24}(?:种族|民族|国籍|宗教|性别|性取向|年龄|残障|残疾)"
            r"|(?i:\b(?:author|writer|poster|creator|user)\b.{0,32}\b(?:muslim|christian|jewish|hindu|buddhist|atheist|democrat|republican|conservative|liberal|left[- ]wing|right[- ]wing|gay|lesbian|bisexual|transgender|nonbinary)\b)"
            r"|(?:作者|发帖者|创作者|用户).{0,24}(?:穆斯林|基督徒|犹太人|佛教徒|印度教徒|民主党|共和党|保守派|自由派|左翼|右翼|同性恋|双性恋|跨性别)"
        ),
    ),
    (
        "psychological diagnosis",
        re.compile(
            r"(?i)\b(?:narcissist|psychopath|sociopath|depressed|bipolar|mentally ill)\b"
            r"|(?:心理诊断|精神疾病|人格障碍|自恋型人格|反社会人格|抑郁症|躁郁症|双相障碍)"
        ),
    ),
    (
        "rewrite or optimization advice",
        re.compile(
            r"(?i)\b(?:rewrite|replacement copy|replace (?:this|it) with|better version|"
            r"change the tone|add (?:a|the)|delete (?:this|the)|remove (?:this|the))\b"
            r"|\bshould (?:add|remove|delete|shorten|revise|change|replace)\b"
            r"|(?:改写|重写|润色成|建议改成|可以改为|替换文案|删掉|删除这|增加一段|调整语气)"
            r"|(?:应该|应当|可以)(?:增加|补充|删除|删去|缩短|修改|调整|替换)"
            r"|(?i:\b(?:vary|personalize|shorten|lengthen|insert|include)\b.{0,50}\b(?:sentence|text|post|copy|anecdote|tone|syntax)\b)"
            r"|(?i:\b(?:lower|reduce|minimi[sz]e)\b.{0,36}\b(?:automated )?(?:screening|detection) risk\b)"
            r"|(?:调整|改变|加入|添加|插入|缩短|拉长).{0,30}(?:句子|句长|文本|帖子|故事|轶事|语气|句法).{0,30}(?:检测|筛查|识别)"
        ),
    ),
    (
        "detector-evasion advice",
        re.compile(
            r"(?i)(?:evade|bypass|fool|beat).{0,24}(?:ai )?detector|pass as human|"
            r"avoid ai detection|humanize (?:the )?(?:text|post|copy)"
            r"|(?:绕过|规避|骗过|避开).{0,18}(?:AI|人工智能)?检测|降低AI率|去AI味|伪装成人类"
        ),
    ),
)


class ReceptionValidationError(ValueError):
    """Raised when a reception assessment violates the contract."""


def _reject_unknown_keys(value: dict, allowed: set[str], path: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ReceptionValidationError(f"{path} contains unknown fields: {', '.join(unknown)}")


def _require_string(value: Any, path: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise ReceptionValidationError(f"{path} must be a string")
    result = value.strip()
    if not allow_empty and not result:
        raise ReceptionValidationError(f"{path} must not be empty")
    return result


def _require_string_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        raise ReceptionValidationError(f"{path} must be a list")
    return [_require_string(item, f"{path}[{index}]") for index, item in enumerate(value)]


def _reject_prohibited_text(value: str, path: str) -> None:
    for label, pattern in PROHIBITED_TEXT_PATTERNS:
        if pattern.search(value):
            raise ReceptionValidationError(f"{path} contains prohibited {label}")


def _find_banned_keys(value: Any, path: str = "human_reception") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            folded_key = key.lower()
            if (
                folded_key in BANNED_KEYS
                or any(marker in folded_key for marker in BANNED_KEY_FRAGMENTS)
                or "rewrite" in folded_key
                or folded_key.startswith("suggested_")
                or folded_key.startswith("replacement_")
            ):
                raise ReceptionValidationError(f"{path}.{key} is prohibited")
            _find_banned_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _find_banned_keys(child, f"{path}[{index}]")


def _evidence_items(case: dict) -> list[dict]:
    content = case.get("content") or {}
    items: list[dict] = []
    if content.get("text"):
        items.append({"locator": "content.text", "text": str(content["text"])})
    for index, image in enumerate(content.get("images") or []):
        image_id = str(image.get("id") or index)
        if image.get("id"):
            items.append(
                {"locator": f"content.images[{image_id}].id", "text": str(image["id"])}
            )
        if image.get("alt_text"):
            items.append(
                {
                    "locator": f"content.images[{image_id}].alt_text",
                    "text": str(image["alt_text"]),
                }
            )
    for index, observation in enumerate(case.get("observations") or []):
        if observation.get("value"):
            items.append(
                {
                    "locator": f"observations[{index}].value",
                    "text": str(observation["value"]),
                }
            )
    return items


def _locate_excerpt(excerpt: str, evidence_items: list[dict], path: str) -> str:
    folded = excerpt.casefold()
    for item in evidence_items:
        if folded in item["text"].casefold():
            return str(item["locator"])
    raise ReceptionValidationError(f"{path} is not grounded in case content or observations")


def _normalize_conclusions(
    value: Any,
    path: str,
    evidence_items: list[dict],
    *,
    require_personas: bool = False,
) -> tuple[list[str], list[dict]]:
    """Require every positive or cross-reader conclusion to cite case evidence."""

    if not isinstance(value, list):
        raise ReceptionValidationError(f"{path} must be a list")
    statements: list[str] = []
    evidence_index: list[dict] = []
    valid_locators = {item["locator"] for item in evidence_items}
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if isinstance(item, str):
            statement = _require_string(item, item_path)
            _reject_prohibited_text(statement, item_path)
            raise ReceptionValidationError(
                f"{item_path} must be an object with statement plus excerpt or structured evidence"
            )
        elif isinstance(item, dict):
            _reject_unknown_keys(item, CONCLUSION_KEYS, item_path)
            statement = _require_string(item.get("statement"), f"{item_path}.statement")
            _reject_prohibited_text(statement, f"{item_path}.statement")
            reason = _require_string(item.get("reason"), f"{item_path}.reason")
            _reject_prohibited_text(reason, f"{item_path}.reason")
            excerpt_value = item.get("excerpt")
            structured = item.get("evidence")
            if excerpt_value is not None:
                excerpt = _require_string(excerpt_value, f"{item_path}.excerpt")
                if len(excerpt) > 200:
                    raise ReceptionValidationError(
                        f"{item_path}.excerpt must be 200 characters or fewer"
                    )
                evidence = {
                    "kind": "excerpt",
                    "locator": _locate_excerpt(excerpt, evidence_items, f"{item_path}.excerpt"),
                    "excerpt": excerpt,
                }
            elif isinstance(structured, dict):
                _reject_unknown_keys(structured, EVIDENCE_KEYS, f"{item_path}.evidence")
                kind = _require_string(structured.get("kind"), f"{item_path}.evidence.kind")
                locator = _require_string(
                    structured.get("locator"), f"{item_path}.evidence.locator"
                )
                if locator not in valid_locators:
                    raise ReceptionValidationError(
                        f"{item_path}.evidence.locator does not identify case evidence"
                    )
                evidence = {"kind": kind, "locator": locator}
                detail = structured.get("detail")
                if detail is not None:
                    detail_value = _require_string(detail, f"{item_path}.evidence.detail")
                    _reject_prohibited_text(detail_value, f"{item_path}.evidence.detail")
                    evidence["detail"] = detail_value[:500]
            else:
                raise ReceptionValidationError(
                    f"{item_path} requires excerpt or structured evidence"
                )
        else:
            raise ReceptionValidationError(f"{item_path} must be a string or object")
        personas: list[str] = []
        if require_personas:
            raw_personas = item.get("personas")
            if not isinstance(raw_personas, list):
                raise ReceptionValidationError(f"{item_path}.personas must be a list")
            personas = [_require_string(persona, f"{item_path}.personas") for persona in raw_personas]
            if len(set(personas)) < 2 or len(personas) != len(set(personas)) or not set(personas) <= PERSONAS:
                raise ReceptionValidationError(
                    f"{item_path}.personas must contain two or three unique valid stances"
                )
        elif item.get("personas") is not None:
            raise ReceptionValidationError(f"{item_path}.personas is only valid for cross-reader patterns")
        statements.append(statement)
        indexed = {"statement": statement, "reason": reason, **evidence}
        if require_personas:
            indexed["personas"] = personas
        evidence_index.append(indexed)
    return statements, evidence_index


def validate_reception(value: Any, case: dict) -> dict:
    """Validate and normalize a Human Reception object."""

    if not isinstance(value, dict):
        raise ReceptionValidationError("human_reception must be an object")
    _find_banned_keys(value)
    _reject_unknown_keys(value, TOP_LEVEL_KEYS, "human_reception")

    result = deepcopy(value)
    if result.get("method") != METHOD:
        raise ReceptionValidationError(f"method must be {METHOD}")
    result["validation_profile"] = VALIDATION_PROFILE

    result["audience_assumptions"] = _require_string_list(
        result.get("audience_assumptions"), "audience_assumptions"
    )
    evidence_items = _evidence_items(case)
    result["cross_reader_patterns"], result["cross_reader_evidence"] = _normalize_conclusions(
        result.get("cross_reader_patterns"), "cross_reader_patterns", evidence_items,
        require_personas=True,
    )
    result["uncertainties"] = _require_string_list(result.get("uncertainties"), "uncertainties")
    for index, assumption in enumerate(result["audience_assumptions"]):
        _reject_prohibited_text(assumption, f"audience_assumptions[{index}]")
    for index, uncertainty in enumerate(result["uncertainties"]):
        _reject_prohibited_text(uncertainty, f"uncertainties[{index}]")

    views = result.get("reader_views")
    if not isinstance(views, list) or len(views) != 3:
        raise ReceptionValidationError("reader_views must contain exactly three entries")

    normalized_views: list[dict] = []
    seen: set[str] = set()

    for index, view in enumerate(views):
        path = f"reader_views[{index}]"
        if not isinstance(view, dict):
            raise ReceptionValidationError(f"{path} must be an object")
        _reject_unknown_keys(view, VIEW_KEYS, path)
        persona = _require_string(view.get("persona"), f"{path}.persona")
        if persona not in PERSONAS:
            raise ReceptionValidationError(f"{path}.persona is invalid")
        if persona in seen:
            raise ReceptionValidationError(f"duplicate persona: {persona}")
        seen.add(persona)

        risk = _require_string(view.get("aversion_risk"), f"{path}.aversion_risk")
        if risk not in RISKS:
            raise ReceptionValidationError(f"{path}.aversion_risk is invalid")

        friction_points = view.get("friction_points")
        if not isinstance(friction_points, list):
            raise ReceptionValidationError(f"{path}.friction_points must be a list")
        normalized_points: list[dict] = []
        for point_index, point in enumerate(friction_points):
            point_path = f"{path}.friction_points[{point_index}]"
            if not isinstance(point, dict):
                raise ReceptionValidationError(f"{point_path} must be an object")
            _reject_unknown_keys(point, FRICTION_KEYS, point_path)
            dimension = _require_string(point.get("dimension"), f"{point_path}.dimension")
            if dimension not in DIMENSIONS:
                raise ReceptionValidationError(f"{point_path}.dimension is invalid")
            excerpt = _require_string(point.get("excerpt"), f"{point_path}.excerpt")
            reason = _require_string(point.get("reason"), f"{point_path}.reason")
            _reject_prohibited_text(reason, f"{point_path}.reason")
            if len(excerpt) > 200:
                raise ReceptionValidationError(f"{point_path}.excerpt must be 200 characters or fewer")
            if len(reason) > 1000:
                raise ReceptionValidationError(f"{point_path}.reason must be 1000 characters or fewer")
            locator = _locate_excerpt(excerpt, evidence_items, f"{point_path}.excerpt")
            normalized_points.append(
                {
                    "dimension": dimension,
                    "excerpt": excerpt,
                    "locator": locator,
                    "reason": reason,
                }
            )

        likely_reaction = _require_string(
            view.get("likely_reaction"), f"{path}.likely_reaction"
        )
        uncertainty = _require_string(view.get("uncertainty"), f"{path}.uncertainty")
        _reject_prohibited_text(likely_reaction, f"{path}.likely_reaction")
        _reject_prohibited_text(uncertainty, f"{path}.uncertainty")
        positive_signals, positive_evidence = _normalize_conclusions(
            view.get("positive_signals"), f"{path}.positive_signals", evidence_items
        )
        if risk == "high" and len(normalized_points) < 2:
            raise ReceptionValidationError(
                f"{path}.aversion_risk high requires at least two grounded friction points"
            )

        normalized_views.append(
            {
                "persona": persona,
                "likely_reaction": likely_reaction,
                "aversion_risk": risk,
                "friction_points": normalized_points,
                "positive_signals": positive_signals,
                "positive_signal_evidence": positive_evidence,
                "uncertainty": uncertainty,
            }
        )

    if seen != PERSONAS:
        raise ReceptionValidationError("reader_views must include supporter, neutral, and skeptic")

    order = {"supporter": 0, "neutral": 1, "skeptic": 2}
    result["reader_views"] = sorted(normalized_views, key=lambda item: order[item["persona"]])
    return result
