# Geo Content Brief Skill

## What It Does

`geo-content-brief-skill` is a reusable skill package for this job:

> 将 GEO 内容访谈、关键词笔记、竞品线索和渠道约束整理成可执行的中文内容简报。用于团队复用、选题规划、内容生产交接和质量评审；不用于直接代写完整长文或替代品牌策略判断。

## 中文使用方式

1. 输入访谈纪要、关键词、渠道限制、竞品摘要、品牌禁区或已有内容方向。
2. 先判断请求是否属于“生成内容简报”，而不是完整长文、广告口号或品牌策略。
3. 按 `references/brief-structure.md` 输出一页中文简报。
4. 用 `references/review-checklist.md` 检查事实、结构、证据、风险和下一步动作。
5. 用 `evals/trigger_cases.jsonl` 和 `evals/output_cases.jsonl` 做轻量回归。

## How To Use

1. Load the skill through `SKILL.md`.
2. Start with `reports/intent-dialogue.md` to tighten the real job, outputs, exclusions, and the standards you care about.
3. Open `reports/reference-scan.md` to capture external benchmarks and any user-supplied references worth learning from.
4. Review `reports/intent-confidence.md` to see whether the real job, inputs, outputs, and exclusions are clear enough yet.
5. Open `reports/reference-synthesis.md` to see the GitHub benchmarks plus curated official, research, and principle tracks in one place.
6. Follow the workflow steps in `SKILL.md`.
7. Check `reports/skill-overview.html` for the generated bilingual HTML skill audit report: overview, metrics, capability profile, principle, contract, quality, risk, assets, and iteration roadmap. It defaults to Simplified Chinese and includes an English switch in the top right.
8. Open `reports/review-studio.html` for the one-page Review Studio 2.0 gate view.
9. Record source-line reviewer comments in `reports/review_annotations.md` when review needs follow-up.
10. Open `reports/review-viewer.html` for a compact visual review of the package.
11. Check `reports/output-risk-profile.md` to see likely output mistakes and self-repair checks.
12. Check `reports/artifact-design-profile.md` to see the intended artifact direction, layout patterns, visual quality gates, and anti-patterns.
13. Check `reports/prompt-quality-profile.md` to see the need model, RTF-to-skill mapping, complexity, and prompt-facing quality matrix.
14. Review `reports/skill-ir.json` for the platform-neutral Skill IR contract before platform-specific packaging.
15. Review `reports/compiled_targets.md` to see how Skill IR compiles into OpenAI, Claude, generic, and Agent Skills compatible target contracts.
16. Review `reports/iteration-directions.md` for the three most valuable next moves.
17. Review `reports/system-model.md` to understand the boundary, feedback loops, drift watch, failure map, and highest-leverage next changes.
18. Review `reports/adoption_drift_report.md` to see local-first metadata-only adoption and drift signals.
19. Review `reports/review_waivers.md` to see human reviewer risk approvals and expiry dates.

## Honest Boundaries

- This package starts from the current intent frame and should not pretend to cover unclear adjacent jobs.
- The first version should ask for clarification when the real input, output, or exclusion boundary is still fuzzy.
- New structure should be added only when it earns its keep through evidence, validation, or reviewer need.
- It should not fabricate search volume, competitor rankings, customer quotes, or third-party evidence.

## Package Map

- `SKILL.md`: trigger and workflow entrypoint
- `agents/interface.yaml`: portable interface metadata
- `manifest.json`: lifecycle and packaging metadata
- `references/brief-structure.md`: 中文 GEO 内容简报结构、字段说明和质量标准
- `references/review-checklist.md`: 交付前编辑复核清单
- `evals/trigger_cases.jsonl`: 应触发和不应触发样例
- `evals/output_cases.jsonl`: 输出结构验收样例
- `reports/intent-dialogue.md`: front-loaded discovery questions for better boundary design and clearer human alignment
- `reports/intent-confidence.md`: current clarity score, open gaps, and the next follow-up questions worth asking
- `reports/github-benchmark-scan.md`: top public benchmark repositories, extracted patterns, and borrow or avoid notes
- `reports/reference-scan.md`: benchmark notes from public references, user references, and local constraints
- `reports/reference-synthesis.md`: a combined view of GitHub benchmarks plus curated world-class pattern tracks
- `reports/output-risk-profile.md`: predicted output failure modes and self-repair constraints for this skill
- `reports/artifact-design-profile.md`: artifact-specific design direction, layout patterns, visual quality gates, and anti-patterns
- `reports/prompt-quality-profile.md`: prompt-facing need model, RTF mapping, complexity, and quality matrix
- `reports/system-model.md`: systems-thinking model for boundary, feedback loops, drift, failure patterns, and leverage points
- `reports/skill-ir.json`: platform-neutral 2.0 Skill IR contract for trigger, workflow, resources, evals, risk, and governance
- `reports/compiled_targets.md`: target compiler report showing generated contracts, adapter modes, preserved semantics, warnings, and unsupported features
- `reports/skill-overview.html`: white-background bilingual HTML skill audit report with sticky four-character Chinese navigation, a top-right language switch, metrics, SVG charts, contract boundary, quality review, risk governance, assets, and iteration roadmap
- `reports/review-studio.html`: Review Studio 2.0 gate page for intent, trigger, output eval, context, runtime conformance, trust, atlas, and release readiness
- `reports/review-viewer.html`: compact review page for architecture, usage, feedback, and next steps
- `reports/iteration-directions.md`: the top three next iteration directions
- `reports/adoption_drift_report.md`: local-first metadata-only telemetry summary for adoption, missed triggers, bad outputs, script errors, and review drift
- `reports/review_waivers.md`: human reviewer risk approval ledger for warning acceptance and expiry
- `reports/review_annotations.md`: source-line reviewer comments linked to Review Studio gates
