---
name: geo-content-brief-skill
description: "将 GEO 内容访谈、关键词笔记、竞品线索和渠道约束整理成可执行的中文内容简报。用于团队复用、选题规划、内容生产交接和质量评审；不用于直接代写完整长文或替代品牌策略判断。"
---

# Geo Content Brief Skill

## When To Use This Skill

- 用户提供访谈纪要、关键词、竞品片段、产品卖点或渠道限制，希望沉淀为中文内容简报。
- 团队需要把零散输入转换成可执行的 GEO 内容选题、角度、结构、证据和交付要求。
- 需要先明确触发边界、输入缺口和输出验收标准，再进入内容生产。

## Workflow

1. 读取用户输入，识别目标受众、内容渠道、关键词、品牌边界、禁止表达和必须覆盖的信息。
2. 对照 `references/brief-structure.md` 生成简报骨架：目标、洞察、角度、关键词、结构、证据、风险和验收标准。
3. 如果缺少核心输入，先提出最多三个澄清问题，不用假设补全用户没有提供的事实。
4. 用 `evals/trigger_cases.jsonl` 检查当前请求是否属于 GEO 内容简报场景。
5. 用 `evals/output_cases.jsonl` 检查输出是否包含输入摘要、内容结构、证据要求、禁区和下一步动作。
6. 交付前回看渠道限制和品牌禁区，删除空泛营销话术、无来源断言和不可执行建议。

## Inputs

- 访谈纪要、销售反馈、客户问题或专家观点。
- 关键词、搜索意图、竞品页面摘要或排名线索。
- 目标渠道、目标读者、品牌口径、禁用词和交付格式。

## Outputs

- 一页中文内容简报，包含目标、受众、核心洞察、推荐角度、文章结构、关键词布置、证据需求和风险提示。
- 缺口清单，说明继续生产前必须补齐的信息。
- 下一步动作，面向写作者、编辑或 SEO/GEO 负责人。

## Output Quality Guardrails

- Before final output, apply the likely failure modes in `reports/output-risk-profile.md` when that report is present.
- Before rendering reports, tutorials, review pages, dashboards, or visual artifacts, apply the artifact direction and visual quality gates in `reports/artifact-design-profile.md` when that report is present.
- When prompt behavior, role design, dialogue quality, or output contracts matter, apply `reports/prompt-quality-profile.md` when that report is present.
- Before adding more structure, apply the boundary, feedback-loop, drift, and leverage-point checks in `reports/system-model.md` when that report is present.
- Repair generic headings, cluttered notes, fragile visual assumptions, weak tables, and missing verification cues before handing work back.
- Map role, task, and format into skill behavior rather than copying a large prompt template into `SKILL.md`.
- Let the artifact's content choose the visual system; do not copy a fixed palette or report style from another skill without a clear reason.
- If output-specific evidence is missing, state the gap instead of inventing screenshots, citations, data, or examples.

## Honest Boundaries

- 不直接代写完整长文，不替代品牌策略判断，不伪造竞品数据、搜索量、排名或引用来源。
- 当用户只想要标题灵感、广告文案、舆情分析或完整文章撰写时，不应触发本 Skill。
- 缺少目标读者、渠道或关键词时，先收紧输入，再输出简报。

## Reference Map

- `references/brief-structure.md`: 中文 GEO 内容简报结构、字段说明和质量标准。
- `references/review-checklist.md`: 交付前的编辑复核清单。
- `evals/trigger_cases.jsonl`: 应触发和不应触发样例。
- `evals/output_cases.jsonl`: 输出结构验收样例。
