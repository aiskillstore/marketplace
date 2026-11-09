# Resume / Split Mode

`pptx-nova` 的 split mode 是会话控制机制，不是新的生成路线：它仍然走
`outline.json` -> `deck_lock.json` -> DeckKit/content/patch -> check-lock ->
dry-run -> apply -> vision-check -> PNG 的原生 PPTX 工作流。区别是把长 deck 或高风险
deck 拆成两个阶段，让新会话从 run 目录里的锁定状态继续，减少上下文压缩导致的漂移。

## 1. 何时建议 split

遇到下列任一信号时，在完成 `outline.json`、`deck_lock.json` 和必要的
`assets_manifest.json` 后建议 split：

- 用户明确要求分阶段、先做大纲/设计锁、换新会话继续、`resume` 或 `继续生成`。
- 页数较长，通常 `>= 12` 页，或每页内容/图表/表格都比较密。
- 投资人路演、董事会、客户正式汇报、品牌合规、公司口径敏感等高风险场景。
- Reference Create 需要读取较大的参考 PPTX、抽风格、做页型映射或模板融合。
- source 材料很长，或来自多个 Markdown/文本、粘贴表格、CSV/JSON、PDF/网页提取内容或
  对话片段，需要先压缩成稳定大纲；不把任意 DOCX/XLSX 当作已实现的直接输入。
- 公式、外部图片、logo、授权素材、数据截图等资源较多，`assets_manifest.json` 本身需要审计。

Express 模式中 split 只是推荐项：用户没有选择 split 时继续同会话自动交付。Studio / 高风险
场景在一次性确认设计锁时同时给出 split 选项；用户确认 split 后，在 Phase A handoff 处停止。

## 2. 两个阶段

### Phase A: Plan / Lock Handoff

目标是把旧会话里的需求、来源和设计决策固化到磁盘，让 Phase B 不需要旧上下文。

必须产出：

| 文件                   | 作用                                                                       |
| ---------------------- | -------------------------------------------------------------------------- |
| `outline.json`         | 自包含页序、每页标题、目的、关键信息、数据/图表意图和页型                  |
| `deck_lock.json`       | 本轮 deck 的画布、输出、DeckKit/theme/style、颜色、字体、资源、页型/节奏锁 |
| `resume_manifest.json` | resume 入口文件，记录阶段、必需文件、输出碰撞检查和下一步                  |
| `source_brief.md`      | 当用户来源来自长文档/对话或 outline 不能承载全部事实时必写的来源摘要       |
| `assets_manifest.json` | 仅当使用外部图片、logo、公式、复用素材或生成资源时创建                     |

可选产物：

- `reference-inspect.json`、`reference-style.json`、`reference-map.json`
- `template_fusion.json`
- `theme-pack.json`、`style-pack.json`
- `assets/` 下的图片、logo、公式 SVG 或数据截图

Phase A 不写 `content.json` / `patch.json`，不 dry-run，不生成 `.pptx`，除非用户明确要求同会话继续。
如果已进入 content/patch 生产，就不应再把当前状态称为 Phase A handoff；此时要么继续完成，要么
以当前 run 目录作为普通中断恢复，resume 时先检查 stale content/patch。

### Phase B: Resume Execution

目标是从一个新会话继续执行，不依赖 Phase A 的对话上下文：

1. 读取 `resume_manifest.json`、`outline.json`、`deck_lock.json` 和必要的
   `assets_manifest.json` / `source_brief.md`。
2. 做 sanity check；缺必需文件时停止，不从记忆重建。
3. 重新检查最终输出路径是否已存在；若存在且不是本 run 中间文件，按 `../common-workflow.md` 的输出防碰撞规则阻塞。
4. 检查资源状态；`missing` / `needs-user` / 未授权 placeholder 在正式交付中阻塞。
5. 从 `outline.json` + `deck_lock.json` 选择 DeckKit 或 generator，生成 `content.json` 或 `patch.json`。
6. 从 `../common-workflow.md` 的 shared pipeline 继续：check-lock -> dry-run -> fix -> apply -> vision-check -> PNG -> final output。

## 3. `resume_manifest.json`

最小结构：

```json
{
  "schemaVersion": "pptx-nova-resume/v1",
  "phase": "ready-for-execution",
  "createdAt": "2026-06-09T15:30:00+08:00",
  "mode": "studio",
  "objective": "Investor roadshow deck for Lumina",
  "runDir": "/abs/path/.pptx-nova/lumina-seed-20260609-153000",
  "finalPptx": "/abs/path/lumina-seed.pptx",
  "handoffAfter": ["outline.json", "deck_lock.json", "assets_manifest.json"],
  "requiredFiles": [
    "outline.json",
    "deck_lock.json",
    "resume_manifest.json",
    "assets_manifest.json"
  ],
  "optionalFiles": ["source_brief.md", "reference-map.json"],
  "nextStep": "generate-content-or-patch",
  "gates": {
    "outputCollisionChecked": true,
    "outlineSelfContained": true,
    "deckLockWritten": true,
    "assetsReady": true,
    "userConfirmedSplit": true
  },
  "notes": [
    "Resume in a fresh session with: 继续生成 /abs/path/.pptx-nova/lumina-seed-20260609-153000"
  ]
}
```

字段规则：

- `phase` 必须是 `ready-for-execution` 才能作为 Phase B 入口。
- `runDir` 和 `deck_lock.output.runDir` 必须一致。
- `finalPptx` 和 `deck_lock.output.finalPptx` 必须一致；若用户在 Phase B 覆盖输出路径，先更新
  `deck_lock.json` 和 `resume_manifest.json`，再继续。
- `requiredFiles` 中的文件必须全部存在。
- 使用外部、复用、生成资源或公式时，`assets_manifest.json` 必须进入 `requiredFiles`；
  不得只放在 `optionalFiles`。
- 如果 `assets_manifest.json` 存在，`gates.assetsReady` 只有在没有 `missing` / `needs-user` /
  `forbidden`，且没有未授权或未确认的 `placeholder` / `needs-review` 阻塞项时才写 `true`。
- `outlineSelfContained` 为 `false` 时，必须存在 `source_brief.md` 或可读取的 source 文件引用。

## 4. Phase A handoff 回复模板

split 时最后回复必须短而完整：

```text
Phase A 已完成，可以在新会话继续。

继续命令：
继续生成 /abs/path/.pptx-nova/<run>

已写入：
- outline.json
- deck_lock.json
- resume_manifest.json
- assets_manifest.json（如有）
- source_brief.md（如有）

当前状态：
- 输出路径已检查：<finalPptx>
- 资源状态：ready / placeholder / needs-user / missing
- 下一步：生成 content/patch，然后执行 check-lock、dry-run、vision-check 和 PNG 复核
```

不要在 split handoff 中声称已生成 PPTX。只有最终 `.pptx` 真实写出并通过门禁后，才能使用完成摘要。

## 5. Resume 触发语句

新会话中识别这些模式：

| 用户说法                                                  | 处理                      |
| --------------------------------------------------------- | ------------------------- |
| `继续生成 .pptx-nova/<run>`                               | 用该 run 目录进入 Phase B |
| `继续生成 /abs/path/.pptx-nova/<run>`                     | 用绝对路径进入 Phase B    |
| `恢复生成 <run-dir>` / `resume pptx-nova <run-dir>`       | 用该 run 目录进入 Phase B |
| 给出 run 目录路径，并说“接着做 / 继续 / 做完 / finish it” | 用该 run 目录进入 Phase B |

如果用户只说“继续”但没有 run 目录，不要猜最近的 `.pptx-nova` 目录；请用户给出 run 目录路径。

## 6. Phase B sanity check

恢复后先做这些检查，再生成任何新文件：

1. 确认 run 目录存在。
2. 读取 `resume_manifest.json`；没有该文件时，只能按普通中断恢复处理，先报告缺失并要求用户确认。
3. 确认 `schemaVersion == "pptx-nova-resume/v1"` 且 `phase == "ready-for-execution"`。
4. 确认 `outline.json`、`deck_lock.json` 存在且可解析。
5. 如果 manifest 要求 `source_brief.md` 或 `assets_manifest.json`，确认文件存在；若
   `deck_lock.json` 使用外部、复用、生成资源或公式，但 `assets_manifest.json` 未列入
   `requiredFiles` 或文件缺失，停止并要求补齐 manifest。
6. 确认 `deck_lock.output.runDir` 与当前 run 目录一致。
7. 重新检查 `deck_lock.output.finalPptx` 是否已存在；存在则按创建型输出防碰撞规则停止。
8. 资源 manifest 中有 `missing` / `needs-user` / 未授权或未确认的 `placeholder` 时停止，
   列出缺失项和需要用户确认或替换的占位资源。
9. 若 `content.json` 或 `patch.json` 已存在，先运行 check-lock 判断是否与当前 lock 一致；不一致就重建。

sanity check 通过后，从 `../common-workflow.md` 的 content/patch 生成步骤继续。

## 7. 失败处理

- 缺 `outline.json` / `deck_lock.json`：停止，说明 Phase A 未完成，不能从旧会话记忆补写。
- 缺 `resume_manifest.json`：询问用户是否按普通中断恢复；若同意，先补写 manifest 再继续。
- `source_brief.md` 缺失且 outline 不含具体事实：停止，请用户提供来源文件或允许重新生成大纲。
- 输出路径已存在：停止，请用户重命名、删除现有文件或提供新输出路径。
- 资源缺失或授权未确认：停止在 Phase B sanity check，不进入 patch/dry-run。

## 8. 与其他模式的关系

- Express：默认同会话完成；长 deck 时可以在 Phase A 后推荐 split。
- Studio：高风险 deck 推荐 split；用户确认后 Phase A 停止，Phase B 专注生成和验证。
- Reference Create：split 尤其有用；Phase A 保存 `reference-style.json` 与 `reference-map.json`。
- Edit：通常不需要 split；只有大规模重构或多轮品牌改装时才作为普通中断恢复使用，不强制
  `outline.json`。
