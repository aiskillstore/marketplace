"""Deterministic origin evidence policy and report rendering."""

from __future__ import annotations

import json
import re
from collections import defaultdict


VERDICTS = {
    "verified_ai_provenance",
    "strong_ai_indicators",
    "conflicting_evidence",
    "no_reliable_ai_evidence",
    "insufficient_evidence",
}

PLATFORM_AI_LABELS = {
    "ai-generated",
    "ai generated",
    "generated with ai",
    "made with ai",
    "created using generative ai",
    "edited using generative ai",
    "ai 生成",
    "ai生成",
    "由 ai 生成",
    "由ai生成",
}

NEGATION_OR_META_PATTERNS = (
    r"\b(?:i|we)\s+(?:deny|denied|dispute|reject)\s+that\b.{0,120}\bai\b",
    r"\bit\s+is\s+(?:false|untrue|incorrect)\s+that\b.{0,120}\bai\b",
    r"\b(?:not|isn['’]t|wasn['’]t|never)\b.{0,45}\b(?:ai[- ]generated|generated (?:with|by) ai)\b",
    r"\b(?:claim|discussion|debate|question|rumou?r|allegation)\b.{0,45}\bai[- ]generated\b",
    r"\bai[- ]generated\b.{0,45}\b(?:false|incorrect|misleading|untrue|claim)\b",
    r"(?:不是|并非|非|没有|未曾|从未).{0,18}(?:ai|人工智能).{0,8}(?:生成|创作|辅助)",
    r"(?:讨论|声称|质疑|传言|所谓).{0,20}(?:ai|人工智能).{0,8}(?:生成|创作|辅助)",
    r"(?:ai|人工智能).{0,8}(?:生成|创作|辅助).{0,18}(?:说法|指控|传言).{0,8}(?:不实|错误|虚假)",
    r"\b(?:said|wrote|reads|quote|quoted|quoting|alleged)\b.{0,100}\b(?:i|we)\s+(?:made|created|generated|edited|wrote)\b.{0,80}\bai\b",
    r"(?:引述|引用|原文|写着|他说|她说|对方说).{0,100}(?:我|我们).{0,30}(?:ai|人工智能).{0,12}(?:生成|创作|撰写|改写|编辑)",
    r"(?:fabricated|forged|fake|false).{0,50}(?:quote|sentence|caption|statement)|(?:quote|sentence|caption|statement).{0,50}(?:fabricated|forged|fake|false)",
    r"(?:伪造|捏造|虚构|不实).{0,30}(?:引文|引述|句子|说明)|(?:引文|引述|句子|说明).{0,30}(?:伪造|捏造|虚构|不实)",
    r"(?:我|我们|作者|本人).{0,8}(?:否认|驳斥|澄清并非|澄清不是).{0,100}(?:ai|人工智能).{0,16}(?:生成|创作|撰写|改写|编辑)",
)

AUTHOR_DISCLOSURE_PATTERNS = (
    r"\b(?:i|we)\s+(?:made|created|generated|edited|wrote|rewrote)\s+(?:(?:this|the)\s+(?:post|image|text|content)|this)\s+(?:with|using|by)\s+(?:generative\s+)?ai\b",
    r"\b(?:(?:this|the)\s+(?:post|image|text|content)|this)\s+(?:was|is)\s+(?:made|created|generated|edited|written|rewritten)\s+(?:with|using|by)\s+(?:generative\s+)?ai\b",
    r"(?:我|我们)\s*(?:使用|用了|借助|通过)\s*(?:生成式)?(?:ai|人工智能)\s*(?:生成|创作|撰写|改写|编辑)(?:了)?\s*(?:这|本|该)?(?:篇|张|段|条)?(?:帖子|图片|文本|内容|文章)",
    r"(?:这|本|该)(?:篇|张|段|条)?(?:帖子|图片|文本|内容|文章)\s*(?:由|是我用|是我们用)\s*(?:生成式)?(?:ai|人工智能)\s*(?:生成|创作|撰写|改写|编辑)",
)


def normalize_text(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def count_han(text: str) -> int:
    return sum(1 for character in text if "\u4e00" <= character <= "\u9fff")


def text_sufficiency(text: str | None, language: str) -> dict:
    normalized = normalize_text(text)
    han_count = count_han(normalized)
    sufficient = han_count >= 500 if language == "zh" else len(normalized) >= 1000
    threshold = "500 Han characters" if language == "zh" else "1,000 normalized characters"
    return {
        "present": bool(normalized),
        "normalized_characters": len(normalized),
        "han_characters": han_count,
        "language": language,
        "sufficient": sufficient,
        "threshold": threshold,
    }


def _is_verified_disclosure(observation: dict) -> bool:
    """Accept only a platform label or an explicit asset-scoped author admission."""

    assertion = str(observation.get("assertion") or "").casefold()
    if assertion in {"denied", "quoted", "discussed", "uncertain"}:
        return False
    value = normalize_text(str(observation.get("value") or ""))
    folded = value.casefold().strip(" .:：!！")
    if any(re.search(pattern, folded, flags=re.IGNORECASE) for pattern in NEGATION_OR_META_PATTERNS):
        return False

    observation_type = observation.get("type")
    if observation_type == "author_disclosure":
        for quoted in re.findall(r"[\"“‘]([^\"”’]{1,300})[\"”’]", folded):
            if re.search(r"(?<![a-z])ai(?![a-z])|人工智能", quoted) and re.search(
                r"generated|created|made|edited|written|rewritten|生成|创作|撰写|改写|编辑",
                quoted,
            ):
                return False
    if observation_type == "platform_ai_label":
        return folded in PLATFORM_AI_LABELS
    if observation_type == "author_disclosure":
        return any(re.search(pattern, folded, flags=re.IGNORECASE) for pattern in AUTHOR_DISCLOSURE_PATTERNS)
    return False


def _observation_scope(observation: dict) -> str:
    scope = normalize_text(str(observation.get("scope") or "post"))
    return scope


def _signal_direction(signal: dict, text_info: dict) -> tuple[str | None, str]:
    provider = signal.get("provider")
    if provider == "hive":
        ai_score = signal.get("ai_generated_score")
        not_ai_score = signal.get("not_ai_generated_score")
        if isinstance(ai_score, (int, float)) and ai_score >= 0.9:
            return "positive", "strong"
        if isinstance(not_ai_score, (int, float)) and not_ai_score >= 0.9:
            return "negative", "strong"
        if isinstance(ai_score, (int, float)) and ai_score >= 0.5:
            return "positive", "medium"
        if isinstance(not_ai_score, (int, float)) and not_ai_score >= 0.5:
            return "negative", "medium"
        return None, "weak"

    direction = signal.get("direction")
    strength = signal.get("strength", "weak")
    if direction in {"positive", "negative"} and strength in {"weak", "medium", "strong"}:
        return direction, strength
    return None, "weak"


def _provider_detail(signal: dict, direction: str | None, strength: str) -> str:
    provider = signal.get("provider", "unknown")
    if provider == "hive":
        return (
            f"Hive ai_generated={signal.get('ai_generated_score')} and "
            f"not_ai_generated={signal.get('not_ai_generated_score')}; "
            f"policy strength={strength}."
        )
    return f"{provider} direction={direction or 'none'}; policy strength={strength}."


def assess_origin(case: dict, provider_signals: list[dict], c2pa_results: list[dict]) -> dict:
    """Apply the fixed evidence hierarchy without using Human Reception."""

    content = case.get("content") or {}
    text_info = text_sufficiency(content.get("text"), content.get("language", "unknown"))
    images = content.get("images") or []
    valid_scopes = {"post"} | ({"text"} if normalize_text(content.get("text")) else set()) | {
        str(image.get("id")) for image in images if image.get("id")
    }
    evidence: list[dict] = []
    verified_scopes: set[str] = set()
    strong_positive: set[str] = set()
    strong_negative: set[str] = set()
    medium_positive: set[str] = set()

    for observation in case.get("observations") or []:
        value = str(observation.get("value") or "")
        if _is_verified_disclosure(observation):
            scope = _observation_scope(observation)
            if scope not in valid_scopes:
                evidence.append(
                    {
                        "type": "invalid_disclosure_scope",
                        "strength": "warning",
                        "scope": "unknown",
                        "detail": "A disclosure-like observation referenced an unknown scope and was not used.",
                        "source": observation.get("source_url"),
                    }
                )
                continue
            verified_scopes.add(scope)
            evidence.append(
                {
                    "type": "explicit_disclosure",
                    "strength": "verified",
                    "scope": scope,
                    "detail": value[:300],
                    "source": observation.get("source_url"),
                }
            )

    c2pa_by_scope: dict[str, dict] = {}
    for item in c2pa_results:
        scope = str(item.get("scope") or item.get("id") or "image")
        result = item.get("result") if isinstance(item.get("result"), dict) else item
        c2pa_by_scope[scope] = result
        if result.get("valid") and result.get("ai_generated"):
            verified_scopes.add(scope)
            evidence.append(
                {
                    "type": "c2pa",
                    "strength": "verified",
                    "scope": scope,
                    "detail": "Valid C2PA manifest contains a generative digital source assertion.",
                    "source": None,
                }
            )
        elif result.get("valid") and result.get("generative_involvement"):
            verified_scopes.add(scope)
            evidence.append(
                {
                    "type": "c2pa",
                    "strength": "verified",
                    "scope": scope,
                    "detail": "Valid C2PA manifest records an edit involving generative AI; it does not say the whole asset was generated.",
                    "source": None,
                }
            )
        elif result.get("status") == "invalid":
            evidence.append(
                {
                    "type": "c2pa",
                    "strength": "warning",
                    "scope": scope,
                    "detail": "C2PA metadata was present but did not validate cleanly.",
                    "source": None,
                }
            )

    provider_by_scope: dict[str, list[dict]] = defaultdict(list)
    for signal in provider_signals:
        scope = str(signal.get("scope") or signal.get("modality") or "unknown")
        provider_by_scope[scope].append(signal)
        direction, strength = _signal_direction(signal, text_info)
        if scope == "text" and not text_info["sufficient"] and strength == "strong":
            strength = "medium"
        if direction == "positive" and strength == "strong":
            strong_positive.add(scope)
        elif direction == "negative" and strength == "strong":
            strong_negative.add(scope)
        elif direction == "positive" and strength == "medium":
            medium_positive.add(scope)
        evidence.append(
            {
                "type": "provider_signal",
                "strength": strength,
                "scope": scope,
                "detail": _provider_detail(signal, direction, strength),
                "source": signal.get("provider"),
            }
        )

    conflict_scopes = strong_positive & strong_negative
    if verified_scopes:
        verdict, confidence = "verified_ai_provenance", "high"
    elif conflict_scopes:
        verdict, confidence = "conflicting_evidence", "low"
    elif strong_positive:
        verdict, confidence = "strong_ai_indicators", "medium"
    elif strong_negative:
        verdict, confidence = "no_reliable_ai_evidence", "medium"
    else:
        verdict, confidence = "insufficient_evidence", "low"

    text_provider_checked = any(signal.get("modality") == "text" for signal in provider_signals)
    image_provider_checked = sum(
        1 for signal in provider_signals if signal.get("modality") == "image"
    )
    coverage = {
        "text": {
            **text_info,
            "provider_checked": text_provider_checked,
        },
        "images": {
            "total": len(images),
            "c2pa_checked": len(c2pa_results),
            "provider_checked": image_provider_checked,
            "skipped": max(0, len(images) - len(c2pa_results)),
        },
    }

    asset_findings: list[dict] = []
    for image in images:
        scope = str(image.get("id") or "image")
        asset_findings.append(
            {
                "id": scope,
                "sha256": image.get("sha256"),
                "c2pa": c2pa_by_scope.get(scope),
                "provider_signals": provider_by_scope.get(scope, []),
            }
        )

    limitations = [
        "AI detectors can produce false positives and false negatives.",
        "Missing AI evidence does not prove human authorship.",
        "Findings apply only to the inspected text and assets.",
        "High-stakes decisions require corroboration and human review.",
    ]
    if text_info["present"] and not text_info["sufficient"]:
        limitations.append(
            f"Text is below the policy threshold of {text_info['threshold']}."
        )
    if text_info["language"] != "zh" and text_info["present"]:
        limitations.append("The bundled local text-pattern proxy is currently limited to Simplified Chinese; other languages require a separately calibrated model.")
    if medium_positive and not strong_positive:
        limitations.append("Positive provider signals did not meet the strong-evidence policy.")
    if len(c2pa_results) < len(images):
        limitations.append("Not every image was checked.")

    return {
        "verdict": verdict,
        "confidence": confidence,
        "verified_scopes": sorted(verified_scopes),
        "coverage": coverage,
        "asset_findings": asset_findings,
        "evidence": evidence,
        "limitations": limitations,
    }


def assess_practical(origin: dict, style: dict, local_text: dict | None = None) -> dict:
    """Combine independent findings into a user-facing, non-probabilistic inference."""

    origin_verdict = origin.get("verdict")
    style_assessment = style.get("assessment")
    local_text = local_text or {}
    local_classification = local_text.get("document_classification")
    basis: list[str] = []
    counterweights: list[str] = []

    if origin_verdict == "verified_ai_provenance":
        label, confidence = "verified_ai_provenance_present", "high"
        scopes = origin.get("verified_scopes") or []
        basis.append(
            "Verified provenance or an unambiguous disclosure identifies generative-AI involvement "
            f"for: {', '.join(scopes) if scopes else 'an inspected scope'}."
        )
    elif origin_verdict == "conflicting_evidence":
        label, confidence = "conflicting_ai_evidence", "low"
        basis.append("Strong positive and negative evidence conflict for the same asset.")
    elif origin_verdict == "strong_ai_indicators":
        label, confidence = "strong_model_signal", "medium"
        basis.append("An explicitly versioned external model supplied a strong signal; this is not provenance.")
    elif local_classification == "strong_pattern_match":
        label, confidence = "strong_ai_like_drafting_signals", "descriptive_only"
        basis.append(
            "The uncalibrated offline analysis found a dense AI-like drafting pattern "
            f"across {len(local_text.get('decision', {}).get('converging_feature_families', []))} "
            "overlapping feature families; this does not establish authorship."
        )
        basis.append(
            f"The transparent indicator reached {local_text.get('decision', {}).get('indicator_points', 0)} "
            "points; this is a rule index, not a probability."
        )
    elif local_classification == "localized_pattern_match":
        label, confidence = "localized_ai_like_patterns", "descriptive_only"
        basis.append("The offline scan found localized formulaic patterns, without a calibrated authorship inference.")
    elif local_classification in {"insufficient_evidence", "unsupported_language"}:
        label, confidence = "no_conclusion", "low"
        basis.append(
            "Text length or language coverage is insufficient for the bundled local pattern analysis."
        )
    elif style_assessment in {"strong_ai_style_patterns", "some_ai_style_patterns"}:
        label, confidence = "style_patterns_only", "descriptive_only"
        basis.append(
            f"The local style scan returned {style_assessment}; style resemblance alone cannot identify origin."
        )
    elif origin_verdict == "no_reliable_ai_evidence":
        label, confidence = "no_reliable_ai_signal", "medium"
        basis.append("A completed calibrated check supplied a strong negative signal.")
    else:
        label, confidence = "no_conclusion", "low"
        basis.append("No verified provenance, strong provider result, or dense style-pattern cluster is available.")

    if origin_verdict != "verified_ai_provenance":
        counterweights.append("No verified generative-AI provenance is available.")
    if style.get("genre_confounds"):
        counterweights.extend(style["genre_confounds"])
    counterweights.extend(
        signal.get("detail", "")
        for signal in style.get("counter_signals", [])
        if signal.get("detail")
    )

    return {
        "label": label,
        "confidence": confidence,
        "basis": basis,
        "counterweights": list(dict.fromkeys(counterweights)),
        "not_a_probability": True,
        "scope": "inspected assets only",
    }


def render_markdown(report: dict) -> str:
    """Render a concise Chinese report without rewriting the source content."""

    origin = report["origin_assessment"]
    reception = report["human_reception"]
    style = report.get("style_pattern_assessment") or {}
    local_text = report.get("local_text_assessment") or {}
    admitted_model = report.get("local_model_research_assessment") or {}
    practical = report.get("practical_assessment") or {}
    detector_coverage = report.get("detector_coverage") or {}
    verdict_text = {
        "verified_ai_provenance": "发现可验证的生成式 AI 来源证据。",
        "strong_ai_indicators": "发现较强 AI 迹象，但不是确定性来源证明。",
        "conflicting_evidence": "来源证据互相冲突，无法可靠下结论。",
        "no_reliable_ai_evidence": "完成的检查中未发现可靠 AI 证据，但这不证明由人类创作。",
        "insufficient_evidence": "现有内容或检查覆盖不足，无法可靠判断来源。",
    }[origin["verdict"]]

    practical_text = {
        "verified_ai_provenance_present": "至少一个明确标注的检查范围存在经过验证的生成式 AI 来源或参与。",
        "strong_model_signal": "版本化外部模型给出强信号，但这不是来源证明。",
        "strong_ai_like_drafting_signals": "本地规则发现密集的 AI 式起草模式；仅作描述，不能据此认定作者身份。",
        "localized_ai_like_patterns": "局部存在模板化或 AI 式模式；仅作描述。",
        "style_patterns_only": "发现风格相似性，但风格不能识别来源。",
        "conflicting_ai_evidence": "AI 来源证据互相冲突。",
        "no_reliable_ai_signal": "完成的检查未发现可靠 AI 信号，但不能证明人工来源。",
        "no_conclusion": "当前无法形成可靠来源判断。",
    }.get(practical.get("label"), "实用判断未知。")

    lines = [
        "# SocialMedia GPTHalf 报告",
        "",
        f"**实用判断：** {practical_text} 置信等级：`{practical.get('confidence', 'low')}`。",
        "",
        "## 实用 AI 辅助推断",
        "",
        f"- 标签：`{practical.get('label', 'no_conclusion')}`",
        f"- 置信等级：`{practical.get('confidence', 'low')}`",
        "- 该标签不是 AI 百分比；未校准的本地模式只作描述，不能单独认定来源。",
    ]
    for item in practical.get("basis", []):
        lines.append(f"- 判断依据：{item}")
    for item in practical.get("counterweights", []):
        lines.append(f"- 反向因素：{item}")

    lines.extend([
        "",
        "## AI 来源证据",
        "",
        f"- 结论：`{origin['verdict']}`",
        f"- 置信等级：`{origin['confidence']}`",
        f"- 解释：{verdict_text}",
    ])
    if origin["evidence"]:
        for item in origin["evidence"]:
            lines.append(
                f"- [{item['strength']}] {item['scope']}: {item['detail']}"
            )
    else:
        lines.append("- 未获得可报告的来源或检测器信号。")
    local_coverage = detector_coverage.get("local_text", {})
    hive = detector_coverage.get("hive", {})
    lines.append(f"- 本地文本检测：`{local_coverage.get('status', 'unknown')}`")
    lines.append(f"- 本地研究模型元数据校验：`{admitted_model.get('status', 'not_configured')}`")
    if admitted_model.get("status") == "evaluation_metadata_passed":
        lines.append(
            f"- 研究基线输出：`{admitted_model.get('predicted_label', 'abstain')}`；"
            "归一化类分数不是校准概率，且不影响来源结论。"
        )
    lines.append(f"- Hive：`{hive.get('status', 'unknown')}`")

    lines.extend(["", "## 本地逐句检测", ""])
    lines.append(f"- 方法：`{local_text.get('method', 'unknown')}`")
    lines.append(f"- 文档分类：`{local_text.get('document_classification', 'insufficient_evidence')}`")
    lines.append(f"- 信号强度：`{local_text.get('signal_strength', 'unknown')}`")
    decision = local_text.get("decision", {})
    lines.append(
        f"- 规则指标：{decision.get('indicator_points', 0)} / "
        f"阈值 {decision.get('ai_like_threshold', 8)}；这是透明规则点数，不是 AI 百分比。"
    )
    families = decision.get("converging_feature_families", [])
    lines.append(f"- 收敛特征族：{', '.join(families) if families else '无'}")
    features = local_text.get("statistical_features", {})
    if features:
        lines.append(
            "- 统计代理：句长 CV={sentence_length_cv}，自惊异度 CV={document_self_surprisal_cv}，"
            "四单位重复率={repeated_four_unit_ratio}，逐句模式命中占比={pattern_match_sentence_share}。".format(
                **features
            )
        )
    highlighted = [
        finding
        for finding in local_text.get("sentence_findings", [])
        if finding.get("classification") == "pattern_match"
    ]
    for finding in sorted(highlighted, key=lambda item: -item.get("indicator_points", 0))[:6]:
        cue_names = "、".join(cue.get("cue", "") for cue in finding.get("cues", [])[:4])
        lines.append(
            f"- 句 {finding.get('sentence_index')}（{finding.get('indicator_points')} 点；{cue_names}）："
            f"“{finding.get('excerpt', '')}”"
        )
    for limitation in local_text.get("limitations", []):
        lines.append(f"- 方法限制：{limitation}")

    lines.extend(["", "## AI 风格模式", ""])
    lines.append(f"- 风格判断：`{style.get('assessment', 'not_applicable')}`")
    lines.append(f"- AI 辅助推断：`{style.get('ai_assistance_inference', 'unknown')}`")
    lines.append(
        f"- 命中 {style.get('pattern_count', 0)} 类模式，"
        f"共 {style.get('occurrence_count', 0)} 处；这不是 AI 概率。"
    )
    for finding in style.get("matches", []):
        excerpts = "；".join(f"“{item}”" for item in finding.get("excerpts", [])[:2])
        lines.append(
            f"- {finding['label']}（{finding['pattern_id']}，{finding['count']} 处）："
            f"{excerpts}——{finding['interpretation']}"
        )
    for signal in style.get("counter_signals", []):
        lines.append(f"- 反向语境信号：{signal['detail']}")
    for confound in style.get("genre_confounds", []):
        lines.append(f"- 体裁干扰：{confound}")
    for limitation in style.get("limitations", []):
        lines.append(f"- 方法限制：{limitation}")

    labels = {
        "supporter": "支持者视角",
        "neutral": "中立读者视角",
        "skeptic": "怀疑者视角",
    }
    for view in reception["reader_views"]:
        lines.extend(
            [
                "",
                f"## {labels[view['persona']]}",
                "",
                f"- 推测反应：{view['likely_reaction']}",
                f"- 反感风险：`{view['aversion_risk']}`",
            ]
        )
        for point in view["friction_points"]:
            excerpt = point["excerpt"].replace("\n", " ")[:300]
            lines.append(
                f"- 阅读摩擦（{point['dimension']}）：“{excerpt}”——{point['reason']}"
            )
        if not view["friction_points"]:
            lines.append("- 未识别到有充分文本依据的主要阅读摩擦。")
        lines.append(f"- 不确定性：{view['uncertainty']}")

    lines.extend(["", "## 跨读者共同点", ""])
    cross_evidence = reception.get("cross_reader_evidence") or []
    if cross_evidence:
        for item in cross_evidence:
            locator = item.get("excerpt") or item.get("locator", "case evidence")
            personas = "、".join(item.get("personas") or [])
            lines.append(
                f"- {item.get('statement')}（视角：{personas}；依据：“{locator}”；理由：{item.get('reason')}）"
            )
    elif reception["cross_reader_patterns"]:
        lines.extend(f"- {item}" for item in reception["cross_reader_patterns"])
    else:
        lines.append("- 未识别到跨立场共同模式。")

    positive = [
        (view["persona"], signal)
        for view in reception["reader_views"]
        for signal in view.get("positive_signal_evidence", [])
    ]
    lines.extend(["", "## 正向的人类感受信号", ""])
    if positive:
        for persona, item in positive:
            locator = item.get("excerpt") or item.get("locator", "case evidence")
            lines.append(
                f"- [{labels[persona]}] {item.get('statement')}（依据：“{locator}”；理由：{item.get('reason')}）"
            )
    else:
        lines.append("- 未提供明确的正向信号。")

    lines.extend(["", "## 覆盖范围与限制", ""])
    lines.append(
        "- 覆盖：" + json.dumps(origin["coverage"], ensure_ascii=False, sort_keys=True)
    )
    lines.extend(f"- {item}" for item in origin["limitations"])
    lines.extend(f"- {item}" for item in reception["uncertainties"])

    lines.extend(["", "## 来源与验证建议", ""])
    if report["sources"]:
        lines.extend(f"- {source}" for source in report["sources"])
    else:
        lines.append("- 未提供公开来源链接。")
    lines.append("- Human Reception 是推测，不是实际用户测试；重要发布请用真实读者验证。")

    if report["provider_errors"]:
        lines.extend(["", "### 未完成的检查", ""])
        for error in report["provider_errors"]:
            lines.append(
                f"- {error['provider']} / {error['category']}: {error['message']}"
            )
    return "\n".join(lines) + "\n"
