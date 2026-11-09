# Design Lock and Assets

本文件定义 `pptx-nova` 的轻量运行契约：`deck_lock.json`、按需生成的 `assets_manifest.json`、
split handoff 使用的 `resume_manifest.json` 和 `cli/create/check-lock.mjs`。它们只服务 xdoc 原生 PPTX / DeckKit / patch
工作流，不引入 SVG executor、逐页手写或 `spec_lock.md` 阶段。

## 1. 何时生成

创建型 deck 在 `outline.json` 之后、`content.json` / `patch.json` 之前生成：

```
prompt / 用户大纲
  -> outline.json
  -> deck_lock.json (+ assets_manifest.json when external/reused assets exist)
  -> resume_manifest.json (only when split handoff is chosen)
  -> DeckKit content.json 或 patch.json
  -> check-lock
  -> dry-run -> apply -> vision-check -> PNG
```

Express 模式自动推断并继续，不阻塞用户。Studio / 高风险模式先做一次短确认，
确认后把决策写入 `deck_lock.json`。这个确认包不是额外仪式，而是后续 DeckKit 选择、
页级节奏、模板融合、资源状态和 chart/table 语义验证的 source of truth；确认后不要凭记忆
改风格、页型、素材来源或图表口径。
当用户选择 split，或长 deck / 高风险 deck 需要换新会话继续时，在 `deck_lock.json` 和必要的
`assets_manifest.json` 完成后写 `resume_manifest.json` 并停止；恢复规则见
`references/runtime/resume-split-mode.md`。

修改已有 deck 时也可以生成 `deck_lock.json`，但只锁定本次允许修改的范围、品牌约束、
资源和输出路径；不要强行要求 slide count 与源 deck 完全一致。

## 2. Studio 确认包

Studio / 高风险场景只做一次 bundled confirmation，内容保持短。Express / Micro Edit
不触发这一步；用户已经明确给出的项直接采用，不重复追问。

1. 画布与输出比例
2. 页数与页序
3. 目标受众与使用场景
4. 风格目标与密度
5. 色彩 / 品牌来源
6. 字体策略
7. 公式策略（`mixed` / `text-only` / `rendered` / `native-omml`，无公式时写 `none`）
8. 图标 / 图表风格
9. 图片 / logo / 第三方素材策略

确认完成后，至少把下面这些结果写入 lock，而不是只留在对话里：

- `canvas`、`deckProfile`、`colors`、`typography`。
- 每页 `rhythm`、`layoutIntent`、`visualDensity`，正式说服型页还要写
  `claimTitle` 和 `proofObject`。
- `templateFusion` 的 identity / structure / deck 来源。
- 外部、复用、生成或公式资产的 `assets_manifest.json` 状态。
- chart/table 页的数据来源、语义角色和验证要求。

缺项能合理推断时给推荐值；只有品牌口径、
页序、敏感数据、外部素材授权或输出路径存在真实风险时才阻塞。

## 3. `deck_lock.json` 最小结构

`deck_lock.json` 是 run 级 source of truth，负责锁定“本轮生成为什么样的 deck”。
它不保存完整正文，也不替代 `content.json`。

当当前 deck 存在用户明确声明的 future/carryover 规则时，可以增加相对路径
`sessionRulesPath: "session-rules.json"`。`cli/create/check-lock.mjs` 会验证该文件存在且符合
`pptx-nova-session-rules/v1`。规则的生命周期、解析和 Edit Contract 接入见
`../edit/session-rules.md`；不要把规则正文复制进 `deck_lock.json`。

```json
{
  "schemaVersion": "pptx-nova-deck-lock/v1",
  "mode": "express",
  "objective": "Q2 business review for leadership",
  "outlinePath": "outline.json",
  "contentPath": "content.json",
  "patchPath": "patch.json",
  "assetsManifestPath": "assets_manifest.json",
  "output": {
    "finalPptx": "/abs/path/q2-review.pptx",
    "runDir": "/abs/path/.pptx-nova/q2-review-20260609-153000"
  },
  "canvas": {
    "format": "ppt169",
    "width": "13.333in",
    "height": "7.5in"
  },
  "deckkit": {
    "id": "consulting-dark",
    "readiness": "production"
  },
  "themePack": {
    "id": "corporate-blue"
  },
  "stylePack": {
    "id": "consulting"
  },
  "colors": {
    "background": "FFFFFF",
    "text": "1F1F1F",
    "primary": "1A73E8",
    "success": "34A853",
    "warning": "FBBC04",
    "risk": "EA4335"
  },
  "typography": {
    "title": "Inter, Source Han Sans SC, Microsoft YaHei, sans-serif",
    "body": "Inter, Source Han Sans SC, Microsoft YaHei, sans-serif",
    "code": "Consolas, Courier New, monospace",
    "strategy": "concord",
    "formulaPolicy": "mixed",
    "formulaFallback": "rendered",
    "mathFont": "Cambria Math, Latin Modern Math, Noto Sans Math",
    "bodyPtMin": 10.5,
    "labelPtMin": 9
  },
  "icons": {
    "library": "tabler-outline",
    "style": "outline",
    "inventory": ["chart-line", "users", "target"]
  },
  "templateFusion": {
    "sources": [
      { "kind": "brand", "id": "acme-brand", "path": "assets/brands/acme/profile.json" },
      { "kind": "layout", "id": "executive-grid" }
    ],
    "identityFrom": "brand:acme-brand",
    "structureFrom": "layout:executive-grid",
    "deckFrom": null
  },
  "slides": [
    {
      "index": 0,
      "title": "Q2 performance review",
      "claimTitle": "Q2 growth slowed, but retention and margin quality improved.",
      "purpose": "Frame the quarter and decision needed",
      "slideType": "heroSlide",
      "rhythm": "anchor",
      "layoutIntent": "opening-thesis",
      "visualDensity": "low",
      "macroLayout": "cover-with-kpi-rail",
      "proofObject": {
        "kind": "metric-rail",
        "proves": "Growth, retention, and margin can be read together"
      },
      "assets": ["company_logo"]
    },
    {
      "index": 1,
      "title": "Revenue and retention",
      "claimTitle": "Expansion revenue offset weaker new-logo conversion.",
      "purpose": "Show core KPI trend",
      "slideType": "kpiRowSlide",
      "rhythm": "dense",
      "layoutIntent": "evidence-chart",
      "visualDensity": "high",
      "macroLayout": "kpi-row-with-context",
      "proofObject": {
        "kind": "column-chart",
        "proves": "Retention is the main bridge between revenue and margin"
      },
      "chart": {
        "kind": "column",
        "semanticSource": "content.slides[1].data",
        "validation": ["category-series-length", "legend-label-clearance"]
      },
      "formulas": []
    }
  ],
  "deckProfile": {
    "primary": "finance-ir",
    "secondaryGates": ["strategy-leadership"],
    "requiredProofObjects": ["metric bridge", "source-backed KPI table"],
    "knownMissingInputs": ["No customer cohort detail supplied"]
  },
  "contactSheetPlan": {
    "maxConsecutiveSameMacroLayout": 2,
    "avoid": ["three repeated card-grid slides", "topic-only titles"]
  },
  "assumptions": ["No user-provided brand guide; use corporate-blue consulting defaults."]
}
```

字段取舍原则：

- 必填：`schemaVersion`、`mode`、`slides[]`、`canvas`、输出路径或 run 目录。
- 创建型：写 `deckkit`、`themePack`、`stylePack`、`colors`、`typography`。
- `typography` 不只写首选字体；标题、正文、代码栈要带可用 fallback，并说明是
  `concord`（同族/同调）、`contrast`（明确对比）还是品牌指定。相似但不同的系统字体
  适合做同一栈 fallback，不适合分别担任标题和正文角色。
- 所有创建型 deck：每页至少写 `rhythm`、`layoutIntent` 或 `macroLayout`。建议写
  `visualDensity`，取值 `low` / `medium` / `high`。这些字段只描述页面节奏和结构意图，
  不替代 DeckKit 的具体坐标。
- `deck_lock.slides[].rhythm` 的合法值是：
  - `anchor`：开场、结论或需要停顿强调的主张页；
  - `dense`：信息密度较高的证据、指标或对比页；
  - `breathing`：刻意留白、转场或视觉缓冲页；
  - `appendix`：附录/来源页，可免除正式叙事页的 claim/proof 检查。
    `appendix` 是设计锁的节奏值；若具体 DeckKit 的 `content.json` schema 没有声明它，
    不要把它写入内容页的 `rhythm` 字段。
- 正式说服型 deck：写 `deckProfile`，并在每个非 appendix slide 写 `claimTitle`、
  `proofObject`、`rhythm`、`layoutIntent`、`visualDensity`；详情见
  `references/create/narrative-quality.md`。
- 技术 / 学术 / 培训 deck：在 `typography.formulaPolicy` 写公式策略，并在相关 slide
  用 `formulas[]` 引用公式资产 id；详情见 `references/content/formulas.md`。
- 使用模板资产：写 `templateFusion`，并记录每个来源的 kind/id/path。
- 使用图片/logo/外部素材：才写 `assetsManifestPath`，并让 slide 通过 asset id 引用。
- 图表和表格页：在 slide 里写 `chart` / `table` 语义对象，至少记录 kind、数据来源和
  需要验证的语义点；不要只把图表当作一组坐标或截图。
- 不确定项写进 `assumptions[]`，不要在后续 generator 里隐式改掉。
- 源大纲只有标题、占位或留白时，AI 补全的事实性内容也必须写进 `assumptions[]`，包括
  竞品名称、产品判断、市场指标、案例、时间线和来源不明的结论；交付摘要要逐条披露。
- `claimTitle` 只能表达已由用户/source 提供或可验证推导出的结论；如果证明材料不足，把缺口写进
  `slides[].omissionNotes[]` 或 `assumptions[]`，不要用更强的措辞掩盖事实缺口。
- `claimTitle` 是叙事锁，不等于必须上屏的完整标题。`content.json` 的展示 `title` /
  `subtitle` 应短、可扫读、适配槽位；完整结论过长时拆到 subtitle、callout、正文或
  `proofObject`。
- 展示主标题和副标题默认不使用句末句号；问号/感叹号仅在刻意提问或强调时使用。
- 用户大纲明确指定的展示主标题/副标题优先；保留原文，并在 slide 上写
  `titleSource: "user"` / `subtitleSource: "user"`。除非出现硬性溢出、事实错误或用户要求润色，
  不用 `claimTitle` 或风格规范静默覆盖用户指定文案。

## 4. `assets_manifest.json`

`assets_manifest.json` 只在使用外部图片、logo、复用素材、数据截图或本轮生成资源时创建；
纯 DeckKit/native shape deck 不要创建空 manifest。它只管资源可用性、来源和 PPTX 使用方式。
所有临时资源放在 run 目录或其子目录，例如 `.pptx-nova/<run>/assets/`。
正式 schema 位于 `assets/schemas/assets-manifest.schema.json`；它约束 manifest 形状，
`cli/create/check-lock.mjs` 负责跨文件引用、文件存在、图片槽位和 AI prompt guard。
公式按 [formulas.md](../content/formulas.md) 选择原生 OMML、已有排版 SVG 或草稿文字 SVG。
bundled `formula-render.mjs` 只生成 LaTeX 原文 SVG，且会覆盖传入 manifest 中每个 formula
条目的目标文件，不按状态跳过。只对明确需要此草稿表示的条目使用独立 manifest 与新路径，
审阅后再合并；不要把已有用户公式、外部排版 SVG 或 native 条目一起交给它批量重写。

```json
{
  "schemaVersion": "pptx-nova-assets-manifest/v1",
  "assetRoot": "assets",
  "entries": [
    {
      "id": "company_logo",
      "kind": "logo",
      "status": "available",
      "path": "assets/company-logo.png",
      "usage": "logo",
      "licenseRisk": "none",
      "source": {
        "kind": "user",
        "originalPath": "/abs/path/company-logo.png",
        "licenseNote": "Provided by user for this deck",
        "licenseRisk": "none"
      },
      "pptxUse": {
        "role": "brand-mark",
        "crop": "contain",
        "noCrop": true
      }
    },
    {
      "id": "objective_loss",
      "kind": "formula",
      "status": "rendered",
      "path": "assets/formulas/objective_loss.svg",
      "source": {
        "kind": "formula",
        "latex": "L(\\theta)=\\sum_{i=1}^{n}(y_i-f_\\theta(x_i))^2",
        "display": "block"
      },
      "pptxUse": {
        "role": "formula-block",
        "crop": "contain",
        "noCrop": true
      }
    },
    {
      "id": "formula_native_example",
      "kind": "formula",
      "status": "native",
      "source": {
        "kind": "formula",
        "latex": "E=mc^2",
        "display": "inline"
      },
      "pptxUse": {
        "role": "formula-inline",
        "noCrop": true
      }
    },
    {
      "id": "hero_photo",
      "kind": "image",
      "status": "placeholder",
      "licenseRisk": "unknown",
      "source": {
        "kind": "placeholder",
        "reason": "User has not supplied approved campaign photo"
      },
      "pptxUse": {
        "role": "hero-background",
        "slotId": "hero.full_bleed",
        "ratio": "16:9",
        "fitPolicy": "cover",
        "crop": "cover",
        "noSlideChrome": true,
        "promptGuard": {
          "noSlideChrome": true,
          "forbid": ["title text", "page number", "footer", "logo", "slide border"]
        }
      }
    }
  ]
}
```

`status` 语义：

| status         | 含义                                              | 是否阻塞交付 |
| -------------- | ------------------------------------------------- | ------------ |
| `available`    | 文件或内置资源已可用                              | 否           |
| `built-in`     | 来自 skill 内置图标/模板                          | 否           |
| `generated`    | 本轮生成并已落在 run 目录                         | 否           |
| `rendered`     | 本轮由 LaTeX/公式 manifest 渲染                   | 否           |
| `native`       | 本轮写入 PowerPoint 原生公式对象                  | 否           |
| `placeholder`  | 可用于草稿，正式交付需确认                        | 通常阻塞     |
| `needs-review` | 文件已在 run 目录，但授权、裁切或语义仍需人工确认 | 正式交付阻塞 |
| `needs-user`   | 缺用户提供或授权确认                              | 是           |
| `missing`      | manifest 中声明但文件不存在                       | 是           |
| `forbidden`    | 已确认不可用于本 deck                             | 是           |

公式资源使用 `kind: "formula"`，`source.kind: "formula"`，并保留原始 `latex` 与
`display`。公式必须 `pptxUse.noCrop: true`；若正式交付仍是 `placeholder` 或
`needs-user`，视为阻塞。更多策略见 `references/content/formulas.md`。

`licenseRisk` 语义：

- `none`：来源和使用权已足够明确。
- `unknown`：可以用于内部草稿，但正式客户、投资人、公开或品牌敏感交付前必须确认。
- `blocked`：不得交付，改为用户提供素材、官方来源、内置图形或原生 shape。

### Identity Asset Provenance

Logo、客户 mark、产品 UI、产品截图、App icon、人物照片、活动照片、第三方品牌图形等身份资产必须有
可说明来源。正式交付只允许这些来源：

- `source.kind: "user"`：用户提供并允许用于本 deck。
- `source.kind: "source-deck"`：来自模板/参考 deck，且用户明确允许复用。
- `source.kind: "official"`：官方或可验证公开来源，manifest 中记录 URL、访问日期或来源说明。
- `source.kind: "built-in"`：来自 skill 内置资产或图标包，并带有 license 信息。

不要生成假 logo、假产品截图、假 App icon、假客户 mark 或伪官方 UI。无法确认来源时，使用
`status: "needs-user"` / `needs-review`，或改为文字/原生 shape 占位；正式客户、投资人、
公开或品牌敏感交付不得带着未确认身份资产继续。

图片 / 截图 / AI 生成素材要显式登记使用槽位：

- `pptxUse.slotId` 或 `slot.id`：语义槽位，如 `hero.full_bleed`、`product.mockup`、
  `case.study.photo`。
- `pptxUse.ratio` 或 `slot.ratio`：只用 `21:9`、`16:10`、`16:9`、`4:3`、`3:2`、
  `3:4`、`1:1`。
- `pptxUse.fitPolicy` 或 `slot.fitPolicy`：只用 `cover`、`contain`、`no-crop`、
  `crop-safe`；旧字段 `crop: "cover"` / `"contain"` 仍可兼容，但新 manifest 优先写
  `fitPolicy`。
- AI 生成图片必须写 `pptxUse.noSlideChrome: true` 或 `slot.noSlideChrome: true`。prompt
  只生成照片、插画、纹理、产品图或场景素材，不要生成 PPT 页面本身；禁止让图片自带标题、
  页眉、页脚、页码、logo、边框、卡片框、图表轴、按钮或任何 slide chrome。标题、数据、
  页码、logo 和边框统一由 DeckKit / xdoc 原生 shape 绘制。
- AI 生成素材不能充当真实公司的 logo、真实产品 UI、客户证据、人物照片、新闻/活动照片或
  第三方品牌资产；这类证据只能来自用户、源 deck 授权资产或官方可验证来源。

`cli/create/check-lock.mjs` 会检查：`missing` / `needs-user` / `forbidden` 为 error；
`placeholder` / `needs-review` 和 `licenseRisk: "unknown"` 为 warning；身份资产来源不在
`user` / `source-deck` / `official` / `built-in` 时为 error；图片资产缺 slot、ratio、
fitPolicy 时给 warning；AI 生成图片缺 `noSlideChrome` 时给 error；`deck_lock.json` /
`content.json` 中的 `assets[]` 和 `imageSlots{}` 引用必须能在 `assets_manifest.json` 中找到。

## 5. `resume_manifest.json`

`resume_manifest.json` 只在 split handoff 时创建。它不是设计锁，也不参与 PPTX 生成；它告诉新会话
当前 run 是否已经完成 Phase A、需要哪些文件、下一步从哪里继续。

最小要求：

- `schemaVersion: "pptx-nova-resume/v1"`。
- `phase: "ready-for-execution"`。
- `runDir` 与 `deck_lock.output.runDir` 一致。
- `finalPptx` 与 `deck_lock.output.finalPptx` 一致。
- `requiredFiles` 至少包含 `outline.json`、`deck_lock.json`、`resume_manifest.json`。
- 如果需要外部、复用、生成资源或公式，`requiredFiles` 必须列出 `assets_manifest.json`，且正式交付不得有
  `missing` / `needs-user` / 未授权或未确认的 `placeholder` 阻塞项。
- 如果 `outline.json` 不足以承载完整事实，必须列出 `source_brief.md` 或可读取的 source 文件。

Phase B 恢复时先读取 manifest 做 sanity check；通过后才生成 `content.json` / `patch.json`。
不要从旧会话记忆补写缺失的 `outline.json`、`deck_lock.json` 或资源清单。

完整 schema 和 handoff 模板见 `references/runtime/resume-split-mode.md`。

## 6. Lock Drift Check

在生成 `patch.json` 后、`xdoc pptx apply --dry-run` 前运行：

```bash
node <skill-root>/scripts/cli/create/check-lock.mjs \
  --lock deck_lock.json \
  --content content.json \
  --patch patch.json \
  --json
# 有 assets_manifest.json 时加：--assets assets_manifest.json
```

检查范围：

- `deck_lock.json` 和 `assets_manifest.json` schemaVersion。
- lock 的 slide count / slideType 与 `content.json` 是否一致。
- lock/content 的 `rhythm`、`layoutIntent` / `macroLayout`、`visualDensity` 是否漂移；
  长 deck 连续多页同一 rhythm 会提示接触表复核。
- 正式 deck 的 `deckProfile`、`claimTitle`、`proofObject`、`rhythm` 是否缺失（缺失先给 warning，
  由 `narrative-quality.md` 和 PNG 复核决定是否阻塞）。
- DeckKit、themePack 等关键选择是否漂移。
- typography 栈是否缺少常见 PowerPoint fallback，以及标题/正文是否使用相似但不同的系统字体组合。
- `assets_manifest.json` 是否有 missing / needs-user / 重复 id / 不存在的文件。
- 图片 / 截图资产是否声明 slot、ratio、fitPolicy；AI 生成图片是否设置 `noSlideChrome`。
- `deck_lock.json` / `content.json` 中的 `assets[]`、`imageSlots{}`、`formulas[]`
  是否能在 `assets_manifest.json` 找到。
- patch 是否为 `schemaVersion: "pptx-patch/v1"`，是否使用 lock 外颜色、字体或绝对资源路径。
- patch 中 chart/table ops 的明显语义错误：chart series/category 长度不一致、combo 不是
  真实组合、table data 行列不齐、未设置 `resize` 却和表格维度冲突。
- patch 里任何 `assetSource.path` 是否登记在 `assets_manifest.json`；只要 patch 引用外部资源，
  `--assets` 就是必需项。

DeckKit-first run 会自动把选中 DeckKit `.kit.mjs` 里的调色板 HEX 和 `FONT_*` token 视为锁内来源。
`font.size`、`font.color` 等样式值不会被当成字体名；如果仍出现 `patch-font-outside-lock`，优先检查是否
真的引入了 lock 和 DeckKit 都未声明的新字体。

默认策略是“硬错误拦真实漂移，颜色/字体越界先 warning”。正式品牌合规或客户交付时，
加 `--strict-colors --strict-fonts` 把 lock 外颜色/字体也变成 error。

`check-lock` 不是 `dry-run` 的替代品：它只证明生成材料没有偏离设计锁；schema 语义、
selector、visualRisks 仍交给 `xdoc pptx apply --dry-run --json`。

## 7. 与 DeckKit / generator 的关系

- DeckKit-first：`deck_lock.json` 锁定 DeckKit 和主题；`content.json` 只放数据。
  如果 `content.json` 需要改 slide type，应先更新 lock。
- 手写 patch：`deck_lock.json` 锁定颜色、字体、资源、页型；patch 只实现这些决策。
- Reference Create：参考 deck 的可复用部分先进入 `templateFusion` 和
  `assets_manifest.json`（仅当允许复用或需要补齐资源时），不要把参考页旧文字、旧图片隐式带入新 deck。
- Template Following：复制源 slide 时，允许保留模板 chrome 和被授权素材；所有被替换、删除或新增的
  身份资产必须进入 `assets_manifest.json` 或 `template-edit-plan.json`，不能用 overlay 掩盖未处理的
  旧素材。
- Edit：lock 可只覆盖本次允许改的范围；不要要求所有源 deck 颜色都被 lock 枚举。
