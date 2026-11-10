# Feedback Mode

Use Feedback Mode when the user explicitly asks for skill feedback, such as
`need feedback`, `needs feedback`, `give feedback`, `provide feedback`,
`feedback wanted`, `feedback expected`, `给反馈`, `需要反馈`,
`有什么使用反馈`, or asks to audit a previous
pptx-nova run for workflow friction.

Feedback Mode is an add-on to the user's main task. Complete the requested PPTX
generation, edit, export, or investigation first, then add skill feedback from
the perspective of a pptx-nova workflow reviewer.

For Create, Refurbish, and Translation workflows, Feedback Mode also requires a
seven-dimension scorecard for the execution process. This scorecard evaluates
how well the Agent operated the PPTX workflow, not whether the user's subject
matter was good. Each dimension is scored from 0 to 10, includes a concise
evidence-based evaluation, and contributes to a weighted overall score out of 10. The weights below are fixed defaults so scores remain comparable across
runs of the same workflow.

## Final Gate

Feedback Mode must be checked immediately before the final response. If the
original user prompt is available as text or saved in the run directory, run:

```bash
node <skill-root>/scripts/cli/review/feedback-gate.mjs \
  --run-dir <run-dir> \
  --prompt-file <run-dir>/prompt.txt \
  --workflow <create|refurbish|translation|other> \
  --strict \
  --overwrite \
  --json > <run-dir>/feedback-gate.json
```

If the prompt was not saved but the agent knows feedback was requested, use
`--require-feedback` instead of `--prompt-file`. For Create, Refurbish, and
Translation, always pass the explicit `--workflow`; prompt/artifact inference is
only a fallback. A strict gate failure means `skill-feedback.md` is missing,
still a scaffold, or lacks a valid scorecard and matching weighted score.
`--write-template` may create a workflow-specific scaffold, but the template
itself does not pass the gate.

## Execution Process Scorecard

Use the exact seven dimensions and weights for the detected workflow. Put the
weight in the dimension cell so the table keeps the user-requested three-column
shape:

```markdown
| 维度            |     分数 | 评价                                      |
| --------------- | -------: | ----------------------------------------- |
| 维度名称（20%） | 8.5 / 10 | 用本次 run 的具体证据说明得分和扣分原因。 |
```

Scores may use integers or decimals, but must remain within `0..10`. Avoid vague
comments such as “很好” or “基本完成”; cite concrete workflow evidence such as
content coverage, validation gates, visual review, selector/op behavior,
recovery work, repeated renders, or publication binding. Compute the weighted
overall score as `sum(score × weight) / 100`, rounded to one decimal:

```markdown
加权综合评分：8.7 / 10
```

### Create: Seven Dimensions

| 维度                            | 分数 | 评价                                                                                                        |
| ------------------------------- | ---: | ----------------------------------------------------------------------------------------------------------- |
| 需求与内容准确性（20%）         | 0–10 | 判断 outline、用户事实、标题、证明对象和最终内容是否忠于需求，是否存在遗漏或未经披露的 AI 假设。            |
| 最终文件可靠性（18%）           | 0–10 | 判断最终 PPTX 是否可打开、结构有效、可编辑，并且交付文件与通过验证的候选文件一致。                          |
| 验证闭环（17%）                 | 0–10 | 判断 content validation、check-lock、dry-run、apply、vision、preview、clean-open 等适用 gate 是否完整闭环。 |
| 视觉设计质量（15%）             | 0–10 | 判断层级、网格、节奏、可读性、视觉丰富度和跨页一致性是否达到目标，而非只判断“成功生成”。                    |
| DeckKit 与 op 使用正确性（12%） | 0–10 | 判断 DeckKit/page type/slot 选择和 patch op、selector、asset binding 是否准确、可维护且没有隐藏的手工补丁。 |
| 异常恢复与状态管理（10%）       | 0–10 | 判断失败、中断、候选分叉、旧证据或工具升级后，Agent 是否找到当前权威状态并安全续跑。                        |
| 流程效率（8%）                  | 0–10 | 判断是否避免无效探测、重复生成、重复全量渲染和不必要的上下文/命令成本。                                     |

### Refurbish: Seven Dimensions

| 维度                      | 分数 | 评价                                                                                                             |
| ------------------------- | ---: | ---------------------------------------------------------------------------------------------------------------- |
| 内容保真（20%）           | 0–10 | 判断页数、文本、图表、表格、媒体、备注和对象语义是否被完整保留，任何变化是否经过批准。                           |
| 最终文件可靠性（18%）     | 0–10 | 判断 PPTX 是否结构有效、PowerPoint 可正常打开，且最终发布文件与验证候选哈希绑定。                                |
| 验证闭环（17%）           | 0–10 | 判断 vision-diff、refurbish-audit、fidelity、semantic diff、preview/compare 和 clean-open 等适用 gate 是否闭环。 |
| 视觉翻新质量（15%）       | 0–10 | 判断输出是否明显采用目标 DeckKit 的网格、层级、色彩和空间节奏，而不是只做轻量换色或 chrome。                     |
| op 使用正确性（12%）      | 0–10 | 判断 fallback/native op、selector、dry-run、apply 和对象级变更是否准确，是否需要额外 inspect 才能补证。          |
| 异常恢复与状态管理（10%） | 0–10 | 判断中断、旧 manifest、多候选文件和工具合同变化后，Agent 是否避免使用陈旧结果并恢复到正确发布状态。              |
| 流程效率（8%）            | 0–10 | 判断是否控制重复 inspect、diff、preview、compare 和候选分叉，同时没有为了提速跳过保真或视觉检查。                |

### Translation: Seven Dimensions

| 维度                                | 分数 | 评价                                                                                                                           |
| ----------------------------------- | ---: | ------------------------------------------------------------------------------------------------------------------------------ |
| 翻译完整性与准确性（20%）           | 0–10 | 判断形状、表格、图表、属性文本和语言不确定单元是否全部分类处理，译文是否准确且无源语言残留。                                   |
| 布局与格式保真（18%）               | 0–10 | 判断字体样式、段落属性、对象位置、动画和多栏布局是否保留，布局修复是否未引入溢出、遮挡或拥挤。                                 |
| 最终文件可靠性（17%）               | 0–10 | 判断翻译后的 PPTX 是否结构有效、可编辑、可正常打开，且最终发布文件与验证候选一致。                                             |
| 验证闭环（15%）                     | 0–10 | 判断 i18n scan/plan、replace records、style diff、candidate 一致性 gate、vision-diff、preview/compare 和 clean-open 是否闭环。 |
| 文本替换与布局修复 op 正确性（12%） | 0–10 | 判断 replace-text/chart-text、run/style preservation、autofit 和几何修复 op 是否作用于正确目标且没有破坏格式。                 |
| 异常恢复与状态管理（10%）           | 0–10 | 判断翻译数据修订、语言分类补录、候选分叉或 gate 失败后，Agent 是否维护稳定 unit id、哈希和最终状态。                           |
| 流程效率（8%）                      | 0–10 | 判断是否复用扫描/分类结果、减少重复翻译和全量渲染，同时保持完整覆盖与布局检查。                                                |

## Terminal Output Requirement

For Create, Refurbish, and Translation feedback, always print the complete
seven-row score table and `加权综合评分` in the final terminal/conversation
response. This requirement applies even when there are more than three detailed
feedback items and the detailed findings themselves are file-only. Read the
validated values from `feedback-gate.json#processScorecard`; do not recompute or
silently change the scores while composing the final response.

## What To Capture

- Record actual skill usage problems, such as unclear reference routing,
  excessive command chains, unstable DeckKit selection, hard-to-act-on
  dry-run/vision output, weak repair suggestions, slot/budget doc mismatch, or
  missing examples.
- For each issue, propose the best fix for `pptx-nova`: documentation, script,
  DeckKit schema, benchmark, catalog, xdoc capability, or final response
  convention.
- Separate these classes clearly: existing capability not used by the agent,
  current tool gap, documentation guidance gap, stale historical run evidence,
  or expected manual review boundary.
- Keep the feedback focused on workflow friction, cognitive load, validation
  closure, and maintainability. Do not turn it into generic praise or a design
  review of the user's slide content.

## Unexpected xdoc Rendering Problems

During xdoc PPTX generation or modification in Feedback Mode, treat each newly
observed rendering result that differs from the requested or expected appearance
and is not already a known limitation as a possible product bug. Identify the
affected candidate, slide/object, expected appearance, and actual appearance.
Check whether the discrepancy is caused by the source content, an intentional
layout choice, or a documented limitation before calling it a new xdoc issue.

- If a PowerPoint-native screenshot of the same candidate and slide already
  exists, compare it with the xdoc render. Check that the screenshot belongs to
  the relevant candidate bytes; do not rely on an old or different candidate.
- Otherwise, when the optional macOS/PowerPoint/Nushell prerequisites are
  available, try `nu <skill-root>/scripts/cli/office/powerpoint-snapshot.nu
  <candidate.pptx> --slides <suspect-slides> --out
  <run-dir>/powerpoint/slide-%d.png --method pdf-render --json >
  <run-dir>/powerpoint-native-render.json` and retain the report and images in
  the current run. Follow the PowerPoint screenshot route in
  `references/common-workflow.md` if PDF rendering fails.
- Compare the same slides and objects, then record the conclusion and paths to
  both sides of the comparison in `skill-feedback.md`. If PowerPoint shows the
  same unexpected result, record a confirmed problem in the generated PPTX. If
  only the xdoc render is wrong, record a confirmed xdoc preview/render problem.
  Describe the visible effect and a likely component only when evidence
  supports it.
- If PowerPoint-native evidence cannot be obtained, is stale, or does not settle
  the discrepancy, mark the observation `unverified` and explain why. Do not
  present it as a confirmed product bug.

After the main task ends, report **every** newly confirmed unexpected xdoc
rendering problem in the final summary, including affected slide/object and
the PowerPoint comparison result. This reporting rule applies even when there
are more than three other feedback items; keep detailed evidence in
`skill-feedback.md` and link that file. Fixing a problem in the delivered deck
does not remove the reporting requirement for the newly discovered issue.

## Current-Capability Check

When feedback audits an old run, compares behavior after an upgrade, or says a
capability is missing, verify the current state before concluding:

1. Re-probe the current `xdoc` runtime when relevant.
2. Check current references and command/schema/help evidence.
3. Treat old run artifacts as historical observations, not current capability
   facts.
4. If the issue only existed because an agent skipped an existing documented
   path, say that directly.

## Output Location

- When Feedback Mode is triggered, always write `<run-dir>/skill-feedback.md`
  before the final response. The gate exists to prevent feedback from being
  lost in long PPTX delivery workflows.
- If there are 1-3 short feedback points, write the file and also include the
  feedback path plus the feedback details in the current conversation under
  `SKILL 使用反馈`.
- If there are more than 3 feedback points, or the feedback needs evidence,
  categories, priorities, or longer explanations, write the file and only
  mention the detailed-feedback path in the final response; do not duplicate
  the detailed issue report in chat. The required execution scorecard and
  weighted overall score are the exception and must still be printed. Newly
  confirmed unexpected xdoc rendering problems are also an exception: summarize
  each one in the final response.
- When the task already has a run directory, use that current run directory. If
  the user only asks for standalone feedback and no run exists, create a small
  feedback run directory under `.pptx-nova/<slug>-<timestamp>/` and place
  `skill-feedback.md` there.
- Do not save feedback outside the run directory unless the user explicitly asks
  for another location.
- Keep `feedback-gate.json` alongside `skill-feedback.md`.

## Suggested Report Shape

For file-based feedback, use this compact structure:

```markdown
# pptx-nova SKILL 使用反馈

任务：...
时间：...

## 总体评价

...

## 具体反馈

### 1. ...

- 现象：
- 影响：
- 建议：
- 状态分类：文档引导不足 / 工具缺口 / 已有能力未使用 / 历史 run 过期

## 建议优先级

1. ...

## 执行过程评分

| 维度                               |     分数 | 评价 |
| ---------------------------------- | -------: | ---- |
| 使用当前 workflow 对应的维度和权重 | ... / 10 | ...  |

加权综合评分：... / 10
```
