"""Explainable Chinese AI-style pattern scan.

The scanner adapts editorial warning signs documented by Humanizer-zh into
local, deterministic observations. It does not estimate authorship
probability and must not be treated as provenance evidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PatternSpec:
    pattern_id: str
    category: str
    label: str
    explanation: str
    expression: re.Pattern[str]


def _compiled(expression: str) -> re.Pattern[str]:
    return re.compile(expression, re.IGNORECASE)


PATTERNS = (
    PatternSpec(
        "inflated_significance",
        "content",
        "夸大意义或问题规模",
        "把普通事实包装成重大、长期被忽略或具有根本性意义的问题。",
        _compiled(
            r"(?:长期|一直)(?:以来)?被.{0,16}忽视|无法回避的事实|从根源上|"
            r"(?:历史)?真实性|"
            r"至关重要|关键(?:性)?作用|深远影响|标志着.{0,12}(?:转变|时刻)"
        ),
    ),
    PatternSpec(
        "vague_attribution",
        "content",
        "模糊权威或资料归因",
        "援引史学界、专家或大量资料，却没有给出可核验的具体来源。",
        _compiled(
            r"史学界|史料记载|查阅了?(?:大量|相关|多方|现有)(?:的)?(?:资料|文献|信息)|"
            r"资料显示|研究表明|"
            r"专家(?:普遍)?认为|业内人士(?:指出|认为)|多项研究"
        ),
    ),
    PatternSpec(
        "formulaic_transition",
        "structure",
        "公式化调查转折",
        "使用‘起初—进一步审视—原来’式的预设发现路径推动文本。",
        _compiled(
            r"起初.{0,36}(?:但|然而)|进一步(?:审视|分析|探讨|研究)|"
            r"(?:我|我们)?带着(?:这些|上述|这一)?(?:疑问|问题)|(?:原来|结果发现)[，,:：]"
        ),
    ),
    PatternSpec(
        "overexplained_reveal",
        "reader_trust",
        "揭晓后继续解释包袱",
        "结论已经清楚后，再用正式因果句或惊叹句复述其显然含义。",
        _compiled(
            r"天[！!].{0,30}原来|(?:时间|逻辑|背景|条件|技术)(?:上|层面)?(?:的)?"
            r"(?:错位|差异|限制).{0,36}(?:阻断|导致|意味着|不可能)|"
            r"即便.{0,36}也会.{0,30}(?:真实性|完整性|可信度)"
        ),
    ),
    PatternSpec(
        "ai_lexicon_cluster",
        "language",
        "抽象正式词汇簇",
        "多个常见的概括性、分析性词汇集中出现，使表达显得比信息本身更正式。",
        _compiled(
            r"进一步|审视|详尽(?:的)?描述|从根源上|长期(?:被)?|"
            r"无法回避|强行植入|生活形态|相互作用|格局|深入探讨|彰显"
        ),
    ),
    PatternSpec(
        "negative_parallelism",
        "language",
        "否定式排比",
        "连续使用‘没有／更没有’或‘不仅／而是’制造整齐对比。",
        _compiled(
            r"没有.{0,36}(?:更没有|也没有)|不仅(?:仅)?.{0,40}(?:而且|而是)"
        ),
    ),
    PatternSpec(
        "generic_closure",
        "structure",
        "概括性收束",
        "用抽象后果完成论证，而不是增加新的可验证信息。",
        _compiled(
            r"即便.{0,45}(?:也会|仍会)|由此可见|综上所述|"
            r"从而.{0,24}(?:确保|推动|促进|彰显)"
        ),
    ),
    PatternSpec(
        "chatbot_trace",
        "communication",
        "聊天助手残留",
        "包含常见助手应答、邀请继续提问或知识截止免责声明。",
        _compiled(
            r"希望这对您有帮助|如果您想让我|请告诉我|当然[！!]|"
            r"您说得完全正确|根据我最后的训练|基于可用信息"
        ),
    ),
    PatternSpec(
        "promotional_language",
        "content",
        "宣传性语言",
        "使用空泛的强力形容词、转型承诺或景观式赞美。",
        _compiled(
            r"令人叹为观止|充满活力|开创性|改变一切|无缝.{0,8}体验|"
            r"不断演变的.{0,8}格局|必游之地|卓越之旅"
        ),
    ),
    PatternSpec(
        "overqualification",
        "language",
        "过度限定",
        "叠加多个可能性或缓和词，回避直接陈述。",
        _compiled(r"可能.{0,8}(?:潜在地|也许|或许).{0,12}可能|可以潜在地可能"),
    ),
    PatternSpec(
        "formulaic_enumeration",
        "structure",
        "标准连接词阶梯",
        "密集使用‘首先—其次—此外—综上’等连接词，把内容组织成高度可预测的阶梯。",
        _compiled(r"首先|其次|此外|与此同时|值得注意的是|更重要的是|综上所述|由此可见"),
    ),
    PatternSpec(
        "balanced_template",
        "language",
        "对称关联模板",
        "反复使用‘不仅—而且／更’或‘一方面—另一方面’形成整齐论证。",
        _compiled(r"不仅.{0,50}(?:而且|更|还)|一方面.{0,80}另一方面|既要.{0,50}也要"),
    ),
    PatternSpec(
        "generic_conditional_closure",
        "structure",
        "条件式抽象收束",
        "用‘只有—才能’或‘最终实现长期价值’式句子收束，但没有增加可核验事实。",
        _compiled(r"只有.{0,80}才能|最终实现.{0,30}(?:长期)?(?:价值|目标|增长)"),
    ),
)


def _excerpt(text: str, start: int, end: int, limit: int = 120) -> str:
    left = max(0, start - 24)
    right = min(len(text), end + 48)
    value = re.sub(r"\s+", " ", text[left:right]).strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def _regex_matches(text: str, spec: PatternSpec) -> list[str]:
    return list(
        dict.fromkeys(_excerpt(text, match.start(), match.end()) for match in spec.expression.finditer(text))
    )[:3]


def _structural_matches(text: str) -> list[dict]:
    findings: list[dict] = []

    questions = list(re.finditer(r"(?:为什么|为何)[^？?]{0,90}[？?]", text))
    if len(questions) >= 3:
        findings.append(
            {
                "pattern_id": "rhetorical_question_chain",
                "category": "structure",
                "label": "连续修辞问句",
                "count": len(questions),
                "excerpts": [_excerpt(text, item.start(), item.end()) for item in questions[:3]],
                "interpretation": "连续同构问句形成机械推进；在段子中也可能是有意的节奏设计。",
            }
        )

    repeated_starts: list[re.Match[str]] = []
    for expression in (r"(?:^|[。！？?])\s*为什么", r"(?:^|[。；])\s*他写"):
        repeated_starts.extend(re.finditer(expression, text, re.MULTILINE))
    if len(repeated_starts) >= 3:
        findings.append(
            {
                "pattern_id": "mechanical_parallelism",
                "category": "structure",
                "label": "机械平行结构",
                "count": len(repeated_starts),
                "excerpts": [_excerpt(text, item.start(), item.end()) for item in repeated_starts[:3]],
                "interpretation": "相同句首反复出现，使段落呈现高度可预测的生成节奏。",
            }
        )

    quoted_lists = list(
        re.finditer(
            r"[“\"][^”\"]*(?:、[^”\"]*){2,}[”\"]|"
            r"(?:[“\"][^”\"]{1,20}[”\"][、，,]?){3,}",
            text,
        )
    )
    if len(quoted_lists) >= 2:
        findings.append(
            {
                "pattern_id": "enumeration_stacking",
                "category": "structure",
                "label": "连续列举堆叠",
                "count": len(quoted_lists),
                "excerpts": [_excerpt(text, item.start(), item.end()) for item in quoted_lists[:3]],
                "interpretation": "多处三项以上列举让文本显得全面，也可能是游戏机制说明或喜剧升级。",
            }
        )

    positive_affect = list(
        re.finditer(r"喜欢|爱(?:你|大家|这个|上)?|感谢|感激|温暖|甜蜜|幸福|开心|惊喜|太棒|美好|治愈|可爱", text)
    )
    if len(positive_affect) >= 3:
        findings.append(
            {
                "pattern_id": "positive_affect_saturation",
                "category": "sentiment",
                "label": "积极情感词饱和",
                "count": len(positive_affect),
                "excerpts": [_excerpt(text, item.start(), item.end()) for item in positive_affect[:3]],
                "interpretation": "多次使用喜爱、温暖或赞美词；中文微博研究发现这类情感词在 LLM-Bot 评论中偏多，但营销和粉丝语境也会产生同样现象。",
            }
        )

    assertive_words = list(
        re.finditer(r"显然|毫无疑问|绝对|肯定|一定|必然|不可否认|毋庸置疑|事实证明", text)
    )
    if len(assertive_words) >= 3:
        findings.append(
            {
                "pattern_id": "assertive_language_cluster",
                "category": "pragmatics",
                "label": "确定性措辞聚集",
                "count": len(assertive_words),
                "excerpts": [_excerpt(text, item.start(), item.end()) for item in assertive_words[:3]],
                "interpretation": "多处绝对化判断形成语义均一性；这在已验证 LLM-Bot 评论中较常见，也可能来自宣传或论战文体。",
            }
        )
    return findings


def _context_signals(text: str) -> tuple[list[dict], list[str]]:
    counter_signals: list[dict] = []
    confounds: list[str] = []
    if re.search(r"\b(?:19|20)\d{2}\b|公元\s*\d{3,4}\s*年", text):
        counter_signals.append(
            {
                "signal": "concrete_dates",
                "detail": "文本包含具体日期或年代；具体性降低了纯通用模板的解释力，但不证明人工来源。",
            }
        )
    if len(set(re.findall(r"我|真的|天[！!]|哈哈|居然|没想到", text))) >= 2:
        counter_signals.append(
            {
                "signal": "personal_or_comedic_voice",
                "detail": "文本存在第一人称或明显喜剧语气；模型与人类都可以产生这种声音。",
            }
        )
    platform_markers = len(re.findall(r"@\w+|#[^\s#]+|https?://|[\U0001F300-\U0001FAFF]", text))
    if platform_markers >= 2:
        counter_signals.append(
            {
                "signal": "platform_specific_markers",
                "detail": "文本包含多个 @、标签、链接或 emoji，显示出平台适配；这些元素在真人内容中常见，但也可由模型模仿。",
            }
        )
    if re.search(r"游戏|英雄|技能|上线|皮肤|双排|王者", text) and re.search(
        r"历史|史料|公元|元朝|游记", text
    ):
        confounds.append(
            "文本把游戏语汇与历史语汇故意错置，属于讽刺或段子体裁；部分‘机械’结构可能是刻意的喜剧装置。"
        )
    if "#" in text:
        confounds.append("社交媒体标签和平台文体会增加列举与关键词重复，不能直接按普通散文解释。")
    return counter_signals, confounds


def analyze_style_patterns(
    text: str | None,
    language: str,
    *,
    platform: str = "unknown",
    declared_purpose: str = "unknown",
) -> dict:
    """Return local style resemblance indicators, never an AI probability."""

    normalized = re.sub(r"\s+", " ", text or "").strip()
    han_characters = sum(1 for character in normalized if "\u4e00" <= character <= "\u9fff")
    base = {
        "method": "humanizer_zh_reverse_v1",
        "language": language,
        "platform": platform,
        "declared_purpose": declared_purpose,
        "han_characters": han_characters,
        "assessment": "not_applicable",
        "ai_assistance_inference": "unknown",
        "pattern_count": 0,
        "occurrence_count": 0,
        "matches": [],
        "counter_signals": [],
        "genre_confounds": [],
        "limitations": [
            "Style patterns are editable and can be produced by humans, templates, translators, or language models.",
            "This method has no calibrated AI-generation probability, false-positive rate, or authorship threshold.",
            "Do not use this assessment as provenance or as proof of human authorship.",
        ],
    }
    if not normalized:
        return base
    if language != "zh":
        base["limitations"].append("humanizer_zh_reverse_v1 is implemented only as an uncalibrated Chinese editorial heuristic.")
        return base
    if han_characters < 200:
        base["limitations"].append(
            "Short Chinese text provides unstable pattern density; interpret isolated matches conservatively."
        )

    findings: list[dict] = []
    for spec in PATTERNS:
        matches = _regex_matches(normalized, spec)
        if matches:
            count = sum(1 for _ in spec.expression.finditer(normalized))
            findings.append(
                {
                    "pattern_id": spec.pattern_id,
                    "category": spec.category,
                    "label": spec.label,
                    "count": count,
                    "excerpts": matches,
                    "interpretation": spec.explanation,
                }
            )
    findings.extend(_structural_matches(normalized))
    findings.sort(key=lambda item: (-item["count"], item["pattern_id"]))

    pattern_count = len(findings)
    occurrence_count = sum(item["count"] for item in findings)
    if pattern_count >= 6 and occurrence_count >= 10:
        assessment = "strong_ai_style_patterns"
        inference = "ai_assistance_plausible"
    elif pattern_count >= 3 and occurrence_count >= 4:
        assessment = "some_ai_style_patterns"
        inference = "ai_assistance_possible"
    else:
        assessment = "few_ai_style_patterns"
        inference = "not_supported_by_style_alone"

    counter_signals, confounds = _context_signals(normalized)
    return {
        **base,
        "assessment": assessment,
        "ai_assistance_inference": inference,
        "pattern_count": pattern_count,
        "occurrence_count": occurrence_count,
        "matches": findings,
        "counter_signals": counter_signals,
        "genre_confounds": confounds,
    }
