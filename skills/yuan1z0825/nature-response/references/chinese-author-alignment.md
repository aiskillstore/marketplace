# Chinese author alignment

Use this file when the user writes in Chinese, provides Chinese author notes, or asks for
`中文核对`, `中英对照`, `审稿意见回复`, `逐点回复`, `修回信`, `大修回复`, or `小修回复`.

## Default behavior

- Accept Chinese reviewer summaries, author notes, manuscript-change notes, and mixed Chinese-English inputs.
- Draft the final point-by-point response letter in English unless the user explicitly asks for Chinese only.
- Keep a short `中文核对` section for unresolved author actions when it helps the author act.
- Translate intent, not literal wording.
- Convert vague Chinese notes into concrete response evidence requirements.

## Common Chinese note conversions

| Chinese note | Problem | Better handling |
|---|---|---|
| `我们已经改了` | Too vague | Ask what changed, where it appears, and whether revised text is available |
| `按审稿人意见修改` | No action mapping | Convert to `AUTHOR_INPUT_NEEDED` until action and location are known |
| `我们补了实验` | Missing evidence | Request experiment name, conditions, replicate/sample details, result summary, and figure/table location |
| `我们补了分析` | Missing analysis detail | Request analysis method, data source, key result, statistical output, and manuscript location |
| `这个问题不重要` | Defensive and unsupported | Reframe as scope, evidence, or claim-boundary reasoning if scientifically justified |
| `由于时间原因没做` | High-risk excuse | Replace with study-design or scope boundary only if true; otherwise flag risk |
| `审稿人误解了` | Accusatory | Reframe as manuscript clarity issue and add clarification |
| `详见正文` | Not traceable | Require section, page, line, figure, table, or supplement |
| `我们认为足够了` | Unsupported sufficiency claim | Explain what evidence addresses the concern or mark remaining limitation |

## Chinese confirmation section

Use concise Chinese action notes:

```text
中文核对
- R1.1: 请补充验证分析的主要结果、样本量或数据集规模，以及 Fig. 5 对应的正文位置。
- R1.2: 请确认统计检验名称、重复单位、样本量和多重检验校正方法。
- R2.1: 目前不能声称已完成动物验证；建议改为范围说明 + Discussion limitation。
```

## Bilingual drafting pattern

When the user supplies Chinese notes:

1. Preserve reviewer comments in their supplied language unless asked to translate.
2. Build the tracker using English action labels.
3. Draft the response letter in polished English.
4. Add `中文核对` only for decisions, missing facts, and high-risk issues.

## Tone correction examples

Chinese author note:

```text
审稿人没有理解我们的方法。
```

Response stance:

```text
We agree that the original Methods description did not make this distinction sufficiently clear.
We have revised the Methods to clarify [specific distinction and location].
```

Chinese author note:

```text
这个实验超出了我们的能力。
```

Response stance:

```text
We agree that this experiment would provide an additional test of [claim]. However, it would require
[new cohort/system/longitudinal design], which is outside the scope of the present study. We have
therefore softened the claim and added a limitation in [location].
```
