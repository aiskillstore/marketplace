"""Offline GPTZero-inspired text signals without pretending to reproduce GPTZero.

The public GPTZero literature describes likelihood-based signals, document and
sentence classification, burstiness, and a hierarchical Human/AI/Mixed model.
Its production architecture, weights, and hyperparameters are proprietary.
This module therefore implements a deterministic, explainable proxy that uses
only local text. Its indicator points are decision aids, never probabilities.
"""

from __future__ import annotations

import math
import re
import statistics
import zlib
from collections import Counter


METHOD = "zh_descriptive_pattern_proxy_v2"


def _normalize(text: str | None) -> str:
    return re.sub(r"[ \t\f\v]+", " ", (text or "").replace("\r\n", "\n").replace("\r", "\n")).strip()


def _split_sentences(text: str) -> list[str]:
    sentences = [
        re.sub(r"\s+", " ", match.group(0)).strip()
        for match in re.finditer(r"[^。！？!?；;\n]+(?:[。！？!?；;]+|$)", text)
    ]
    return [sentence for sentence in sentences if sentence]


def _units(text: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fff]|[A-Za-z]+(?:'[A-Za-z]+)?|\d+(?:\.\d+)?", text.casefold())


def _cv(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = statistics.fmean(values)
    return statistics.pstdev(values) / mean if mean else 0.0


def _normalized_entropy(units: list[str]) -> float:
    if len(units) < 2:
        return 0.0
    counts = Counter(units)
    if len(counts) < 2:
        return 0.0
    total = len(units)
    entropy = -sum((count / total) * math.log2(count / total) for count in counts.values())
    return entropy / math.log2(len(counts))


def _repeated_ngram_ratio(units: list[str], n: int = 4) -> float:
    if len(units) < n:
        return 0.0
    ngrams = [tuple(units[index : index + n]) for index in range(len(units) - n + 1)]
    counts = Counter(ngrams)
    repeated_occurrences = sum(count - 1 for count in counts.values() if count > 1)
    return repeated_occurrences / len(ngrams)


def _self_surprisal(sentence_units: list[str], document_counts: Counter[str], total: int) -> float:
    if not sentence_units or not total:
        return 0.0
    return statistics.fmean(-math.log2(document_counts[unit] / total) for unit in sentence_units)


def _opener(sentence: str) -> str:
    units = _units(sentence)
    return "".join(units[:2])


def _sentence_cues(sentence: str) -> list[dict]:
    cues: list[dict] = []
    rules = (
        (
            "formulaic_investigation",
            2,
            r"起初|进一步(?:审视|分析|研究)|(?:我|我们)?带着(?:这些|上述|这一)?(?:疑问|问题)|"
            r"查阅了?(?:大量|相关|多方|现有)(?:的)?(?:资料|文献|信息)|原来[，,:：]",
            "预设的‘调查—揭晓’推进结构",
        ),
        (
            "inflated_problem_frame",
            2,
            r"(?:长期|一直)(?:以来)?被.{0,18}忽视|无法回避的事实|从根源上|"
            r"(?:真实性|完整性|可信度|长期价值)",
            "把普通包袱包装为重大问题或根本性结论",
        ),
        (
            "rhetorical_question",
            2,
            r"(?:为什么|为何).{0,100}[？?]",
            "修辞问句推动预设答案",
        ),
        (
            "vague_authority",
            2,
            r"史学界|史料记载|研究表明|专家认为|大量(?:的)?资料",
            "使用宽泛权威或资料归因",
        ),
        (
            "overexplained_reveal",
            2,
            r"天[！!].{0,40}原来|(?:时间|逻辑|背景|条件|技术)(?:上|层面)?(?:的)?"
            r"(?:错位|差异|限制).{0,50}(?:阻断|导致|意味着|不可能)|即便.{0,50}也会",
            "揭晓包袱后继续正式解释显然结论",
        ),
        (
            "formal_abstract_cluster",
            1,
            r"进一步|详尽|审视|概念|生活形态|完全脱节|强行植入|从根源上|"
            r"持续赋能|长期价值|竞争格局|核心优势",
            "抽象分析词汇提高了模板化程度",
        ),
        (
            "formulaic_disclosure",
            2,
            r"首先|其次|此外|与此同时|值得注意的是|更重要的是|综上所述|由此可见",
            "标准连接词把段落组织成可预测的信息阶梯",
        ),
        (
            "balanced_template",
            2,
            r"不仅.{0,50}(?:而且|更|还)|一方面.{0,80}另一方面|既要.{0,50}也要",
            "对称关联结构形成模板化论证",
        ),
        (
            "generic_conclusion",
            2,
            r"这(?:充分)?说明|这意味着|只有.{0,80}才能|最终实现.{0,30}(?:价值|目标|增长)",
            "抽象结论或条件句收束全文",
        ),
    )
    for cue_id, weight, expression, explanation in rules:
        matches = re.findall(expression, sentence)
        if matches:
            cues.append(
                {
                    "cue": cue_id,
                    "weight": weight,
                    "count": len(matches),
                    "explanation": explanation,
                }
            )
    if len(re.findall(r"[“\"][^”\"]+[”\"]", sentence)) >= 3:
        cues.append(
            {
                "cue": "stacked_enumeration",
                "weight": 1,
                "count": len(re.findall(r"[“\"][^”\"]+[”\"]", sentence)),
                "explanation": "连续引号列举形成可预测的完备感",
            }
        )
    return cues


def analyze_local_text(
    text: str | None,
    language: str,
    *,
    style_assessment: dict | None = None,
) -> dict:
    """Return local document/sentence indicators inspired by public detector principles."""

    normalized = _normalize(text)
    han_count = sum("\u4e00" <= character <= "\u9fff" for character in normalized)
    normalized_count = len(re.sub(r"\s+", "", normalized))
    threshold = 500
    measured_length = han_count
    sufficient = measured_length >= threshold
    limited = measured_length >= (200 if language == "zh" else 400)
    coverage_level = "full" if sufficient else "limited" if limited else "insufficient"
    limitations = [
        "This is an offline deterministic heuristic, not GPTZero and not a trained reproduction of its proprietary model.",
        "Document self-surprisal, compression, and repetition are predictability proxies; they are not language-model perplexity.",
        "Indicator points are transparent rule weights, not an AI probability or calibrated likelihood.",
        "The bundled tests verify rule behavior, not real-world accuracy, recall, or false-positive rates on a blind corpus.",
        "Edited AI text and formulaic human genres can both change these signals substantially.",
    ]

    base = {
        "method": METHOD,
        "model_kind": "deterministic_untrained_descriptive_proxy",
        "document_classification": "insufficient_evidence",
        "signal_strength": "unknown",
        "not_a_probability": True,
        "coverage": {
            "language": language,
            "han_characters": han_count,
            "normalized_characters": normalized_count,
            "threshold": threshold,
            "measured_length": measured_length,
            "level": coverage_level,
            "sufficient_for_strong_label": sufficient,
        },
        "decision": {
            "indicator_points": 0,
            "strong_pattern_threshold": 8,
            "converging_feature_families": [],
            "drivers": [],
        },
        "statistical_features": {},
        "sentence_findings": [],
        "limitations": limitations,
    }
    if not normalized:
        return base
    if language != "zh":
        base["document_classification"] = "unsupported_language"
        base["coverage"]["level"] = "unsupported"
        base["coverage"]["sufficient_for_strong_label"] = False
        base["limitations"].append(
            "The bundled rule proxy is limited to Simplified Chinese. English, mixed, and other languages require a separately calibrated model."
        )
        return base

    sentences = _split_sentences(normalized)
    document_units = _units(normalized)
    counts = Counter(document_units)
    total_units = len(document_units)
    sentence_units = [_units(sentence) for sentence in sentences]
    lengths = [float(len(units)) for units in sentence_units if units]
    surprisals = [_self_surprisal(units, counts, total_units) for units in sentence_units]
    mean_length = statistics.fmean(lengths) if lengths else 0.0
    median_length = statistics.median(lengths) if lengths else 0.0
    length_cv = _cv(lengths)
    surprisal_cv = _cv(surprisals)
    entropy = _normalized_entropy(document_units)
    repeated_ratio = _repeated_ngram_ratio(document_units)
    raw = normalized.encode("utf-8")
    compression_ratio = len(zlib.compress(raw, level=9)) / len(raw) if raw else 0.0

    opener_counts = Counter(_opener(sentence) for sentence in sentences if _opener(sentence))
    reused_openers = sum(count for count in opener_counts.values() if count > 1)
    opener_reuse_rate = reused_openers / len(sentences) if sentences else 0.0
    median_surprisal = statistics.median(surprisals) if surprisals else 0.0

    sentence_findings: list[dict] = []
    high_signal_count = 0
    for index, (sentence, units, surprisal) in enumerate(zip(sentences, sentence_units, surprisals), start=1):
        cues = _sentence_cues(sentence)
        points = sum(cue["weight"] for cue in cues)
        opener = _opener(sentence)
        if opener and opener_counts[opener] > 1:
            points += 1
            cues.append(
                {
                    "cue": "reused_opener",
                    "weight": 1,
                    "count": opener_counts[opener],
                    "explanation": f"句首‘{opener}’在文中重复",
                }
            )
        if len(sentences) >= 5 and median_length and abs(len(units) - median_length) / median_length <= 0.25:
            points += 1
            cues.append(
                {
                    "cue": "regular_sentence_length",
                    "weight": 1,
                    "count": 1,
                    "explanation": "句长接近全文中位数；这是较弱的节奏一致性信号",
                }
            )
        if len(sentences) >= 5 and surprisal <= median_surprisal:
            points += 1
            cues.append(
                {
                    "cue": "low_relative_self_surprisal",
                    "weight": 1,
                    "count": 1,
                    "explanation": "相对全文而言用字更可预测；这不是语言模型困惑度",
                }
            )
        label = "pattern_match" if points >= 4 else "uncertain"
        if label == "pattern_match":
            high_signal_count += 1
        sentence_findings.append(
            {
                "sentence_index": index,
                "excerpt": sentence[:180] + ("…" if len(sentence) > 180 else ""),
                "classification": label,
                "indicator_points": points,
                "self_surprisal": round(surprisal, 4),
                "cues": cues,
            }
        )

    high_signal_share = high_signal_count / len(sentences) if sentences else 0.0
    style = style_assessment or {}
    style_label = style.get("assessment")
    pattern_count = int(style.get("pattern_count") or 0)
    occurrence_count = int(style.get("occurrence_count") or 0)
    occurrence_density = occurrence_count / max(measured_length, 1) * 100

    points = 0
    drivers: list[str] = []
    families: list[str] = []
    if style_label == "strong_ai_style_patterns":
        points += 5
        drivers.append("dense_explainable_style_patterns:+5")
        families.append("template_and_style")
    elif style_label == "some_ai_style_patterns":
        points += 2
        drivers.append("moderate_explainable_style_patterns:+2")
        families.append("template_and_style")
    if pattern_count >= 8:
        points += 2
        drivers.append("broad_pattern_family_coverage:+2")
    if occurrence_density >= 2.0:
        points += 2
        drivers.append("high_pattern_occurrence_density:+2")
    if high_signal_share >= 0.45:
        points += 3
        drivers.append("sentence_level_signal_concentration:+3")
        families.append("sentence_level_concentration")
    elif high_signal_share >= 0.25:
        points += 2
        drivers.append("partial_sentence_level_signal_concentration:+2")
        families.append("sentence_level_concentration")
    if len(sentences) >= 5 and (length_cv <= 0.40 or opener_reuse_rate >= 0.30):
        points += 1
        drivers.append("low_rhythm_variation_or_reused_openers:+1")
        families.append("structural_regularity")
    lexical_predictability = False
    if repeated_ratio >= 0.05:
        points += 1
        drivers.append("repeated_four_unit_sequences:+1")
        lexical_predictability = True
    if compression_ratio <= 0.55 and len(raw) >= 500:
        points += 1
        drivers.append("high_compressibility:+1")
        lexical_predictability = True
    if lexical_predictability:
        families.append("lexical_predictability_proxy")

    families = list(dict.fromkeys(families))
    if sufficient and points >= 8 and len(families) >= 3 and high_signal_share >= 0.45:
        classification = "strong_pattern_match"
        strength = "descriptive_only"
    elif limited and points >= 5 and len(families) >= 2:
        classification = "localized_pattern_match"
        strength = "descriptive_only"
    elif not limited:
        classification = "insufficient_evidence"
        strength = "unknown"
    else:
        classification = "unresolved"
        strength = "low"

    base["document_classification"] = classification
    base["signal_strength"] = strength
    base["decision"] = {
        "indicator_points": points,
        "strong_pattern_threshold": 8,
        "converging_feature_families": families,
        "drivers": drivers,
    }
    base["statistical_features"] = {
        "sentence_count": len(sentences),
        "mean_sentence_units": round(mean_length, 3),
        "sentence_length_cv": round(length_cv, 4),
        "document_self_surprisal_mean": round(statistics.fmean(surprisals), 4) if surprisals else 0.0,
        "document_self_surprisal_cv": round(surprisal_cv, 4),
        "normalized_unit_entropy": round(entropy, 4),
        "repeated_four_unit_ratio": round(repeated_ratio, 4),
        "compression_ratio": round(compression_ratio, 4),
        "opener_reuse_rate": round(opener_reuse_rate, 4),
        "pattern_match_sentence_share": round(high_signal_share, 4),
        "style_occurrences_per_100_units": round(occurrence_density, 4),
    }
    base["sentence_findings"] = sentence_findings
    if not sufficient:
        base["limitations"].append(
            f"Text is below the strong-label threshold ({threshold} measured characters/units)."
        )
    return base
