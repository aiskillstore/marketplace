# Express Mode —— 简单 prompt 一键出客户演示级 deck

> 用户给一句话 / 几句话的 prompt，或已经给出大纲时的**默认创建路径**：自动走完
> outline（生成或标准化）→ deck_lock（有资源时 assets_manifest）→ 选择可用 DeckKit →
> content manifest → check-lock → dry-run → vision-check 闭环 → PNG 复核，最小确认、零手算坐标。
> 长 deck 或高风险 deck 可以在 deck_lock 后写 `resume_manifest.json`，让用户新会话
> `继续生成 <run-dir>`；这只是会话切分，不改变 Express 的 DeckKit-first 路线。
>
> **express ≠ 草稿**：它默认也按客户演示级的内容与视觉质量产出，只是把
> `../common-workflow.md` 的完整工作流自动串起来、不逐项追问。要草稿请明说「简单/速记版」。

## 目录

1. [何时用 Express（vs Studio / Edit）](#1-何时用-expressvs-studio--edit)
2. [Express 黄金路径（自动化 12 步）](#2-express-黄金路径自动化-12-步)
3. [prompt → outline → DeckKit/content](#3-prompt--outline--deckkitcontent)
4. [风格选择（themePack / stylePack）](#4-风格选择themepack--stylepack)
5. [质量门与丰富度](#5-质量门与丰富度)
6. [vision-check 自动闭环](#6-vision-check-自动闭环)
7. [最小确认策略](#7-最小确认策略)
8. [升级信号：何时转 Studio / Edit](#8-升级信号何时转-studio--edit)

---

## 1. 何时用 Express（vs Studio / Edit）

| 信号                                                   | 走哪个模式           | 去向                                                             |
| ------------------------------------------------------ | -------------------- | ---------------------------------------------------------------- |
| 简单 prompt、要快、没给细节（"做一份 Q2 业务回顾"）    | **Express**          | 本文档                                                           |
| 提供参考 PPTX + 新大纲 / 新主题                        | **Reference Create** | `reference-create.md`                                            |
| 要像素级控制 / 自定义形状 / 复杂 chart 样式 / 投资人级 | **Studio**           | 先选 DeckKit；无匹配时见 `deck-generator-workflow.md`            |
| 指定品牌 profile / 要做品牌合规检查                    | **Studio**           | `../content/styles-and-themes.md`（`set-theme` / `remap-theme`） |
| 改已有 `.pptx`（增删改某页/某对象/换数据）             | **Edit**             | `../edit/edit-mode.md` + `../edit/inspect-and-edit.md`           |

Express 和 Studio 共用同一套 DeckKit / generator / op 基础设施，区别只在
**ceremony**：express 自动选默认、最小确认、自动闭环；studio 让你逐项控制。
两者的新建交付路径都先走 production/default DeckKit；generator 只用于没有匹配
DeckKit、需要新页型或需要改组件结构时的创建/扩展阶段。
中途发现需要精控，随时按 §8 升级，不用重来。

### DeckKit 快路径（同套件二次创作）

如果目标场景已有冻结的 DeckKit（检查 `assets/deckkits/catalog.json`），Express 可走
更短的 **DeckKit 模式** 路径：不写 generator，只写 content manifest。

```
prompt / 用户大纲 → outline.json → deck_lock.json（有外部/复用资源时加 assets_manifest.json）
  → 读取 selected DeckKit visualGrammar（定位 / signature / composition / avoid）
  → content.json（~200 行纯数据）
  → validate-content.mjs 校验（schema / density / layout contract / diversity）
  → createDeck(content) 生成 patch
  → check-lock → dry-run → apply → vision-check → PNG/contact sheet review
```

判断条件：`catalog.json` 中存在匹配的 `id`，`supportedSlideTypes` 覆盖 outline
所需的全部页型，`visualGrammar` 足够完整，且 `--target delivery` readiness audit 通过。交付型自动选择只允许
`readiness in ["production", "default"]`；`candidate` 只能用于草稿、迁移验证，
或人工确认后的交付。不满足时进入创建/扩展 DeckKit 流程，而不是把通用 generator
作为最终交付路径。

详见 `deckkit-mode.md` 和 `deck-generator-workflow.md`「二次创作快路径」。

---

## 2. Express 黄金路径（自动化 12 步）

正式创建按 [create-runner.md](create-runner.md) 调用 `cli/create/run.mjs`，由 runner
执行机器检查和 canonical PDF/PNG 取证；实际审阅后再以 `--finalize --visual-review`
发布同一候选。下面拆解低层步骤供诊断和 DeckKit 开发使用，不替代 runner 的交付门禁。

```bash
# 0. 从用户大纲标准化 outline.json；若无大纲，再从 prompt 提炼 deckBrief/outline → 见 §3、§7
# 0b. 自动生成 deck_lock.json；只有使用外部/复用资源时生成 assets_manifest.json。Express 不阻塞确认，假设写入 assumptions[]
# 0c. 若用户选择 split，写 resume_manifest.json + 必要的 source_brief.md，停止并给出“继续生成 <run-dir>”
# 1. 选择 production/default DeckKit
node <skill-root>/scripts/cli/deckkits/select.mjs \
  --scenario roadshow \
  --language mixed \
  --density dense \
  --slide-types heroSlide,multiCardSlide,benchmarkSlide,timelineSlide,askSlide \
  --target delivery \
  --json

# 1b. 对 selected.id 再跑 delivery readiness audit
node <skill-root>/scripts/cli/deckkits/readiness.mjs --deckkit <selected-id> --target delivery

# 当前 catalog 已有 production/default 套件；选择结果仍取决于页型覆盖、场景与 readiness。
# 若没有合适结果，先扩展 DeckKit；用户明确指定 candidate 时按 deckkit-mode.md
# 的 explicit 路线处理，不把候选提升到 production 或伪造自动选择成功。

# 1c. 使用 selected.visualGrammar 约束内容创作：
#     positioning 决定风格判断，signatureElements/compositionRules 决定页面构成，
#     avoid 清单用于拒绝不匹配的视觉选择。

# 1d. 生成槽位速查，按字段、数组上限和字数/行数预算写 content
node <skill-root>/scripts/cli/deckkits/slots.mjs \
  --deckkit consulting-dark \
  > deckkit-slots.md

# 2. 写 content manifest（纯数据，不写坐标/配色/组件逻辑）
cp <skill-root>/assets/deckkits/consulting-dark/examples/content.json content.json
#    按 outline.json 改 slides[].type 和 slides[].data

# 3. 校验 content（schema + density + layout contract + diversity + fit diagnostics）
node <skill-root>/assets/deckkits/validate-content.mjs \
  content.json \
  --deckkit consulting-dark \
  --mode delivery

# 4. 生成 patch
node <skill-root>/scripts/cli/create/build.mjs \
  --deckkit consulting-dark \
  content.json \
  -o patch.json \
  --quality-json quality.json

# 5. 设计锁漂移检查（deck_lock/assets/content/patch 一致性 + image slot/prompt guard）
node <skill-root>/scripts/cli/create/check-lock.mjs \
  --lock deck_lock.json \
  --content content.json \
  --patch patch.json \
  --json
# 有 assets_manifest.json 时加：--assets assets_manifest.json

# 6. 记录操作数，并按 §5 检查内容和视觉质量
jq '.ops | length' patch.json

# 7. 首次提交前保存上下文，再 dry-run（运行时需披露 remediationSchema）
node <skill-root>/scripts/cli/runtime/remediation.mjs run \
  --patch patch.json --capsule run/remediation-context --output out.pptx \
  --dry-run > dry.json
#    读 semanticChanges[] / visualRisks[] / resolvedSelectors[]

# 8. 修复：按 kind 分派、核对自己保有的身份与上下文，再 dry-run/授权/执行
#    见 ../runtime/troubleshooting.md；不得将完整 replacement request 追加执行

# 9. 无需修复时，用首次提交的冻结请求/资产真 apply（保留 sidecar）
#    若步骤 8 已经成功写出修复后的 out.pptx，直接继续步骤 10
xdoc pptx apply -p run/remediation-context/request.json \
  --asset-root run/remediation-context/assets -o out.pptx --daemon

# 10. 几何自检闭环（render-free，见 §6）
xdoc pptx vision-check out.pptx --json > vision.json
#    核对一条文档 remediation 并执行 → 重新诊断新文档 → 处理剩余 medium/high

# 11. 转 PNG 像素复核（对比度/装饰挡标题等几何看不到的，见 §5 与 ../common-workflow.md）
xdoc convert out.pptx --to png -o previews --overwrite
#    逐页检查字符重叠、换行压字、截断、页脚/来源撞正文

# 12. 这些是中间产物：out.pptx + outline.json + deck_lock.json + content.json + patch.json + dry.json + vision.json + previews/
#     若使用外部/复用资源，再包含 assets_manifest.json
#     正式交付仍须完成 create-runner.md 的 canonical evidence、绑定审阅和 finalize
```

四道闸门分层：**check-lock（设计锁漂移 + 资产槽位）→ dry-run（语义 + touched
shape 文本溢出估算）→ vision-check（全 deck 静态几何/文本门禁，可自动闭环）→ PNG（像素）**。
创建型 deck 的 `vision-check` high/medium 都必须为 0；任何一道不过都回去改对应
DeckKit 页型或 content 重跑，不要跳步、不要在没过闸门时声称完成。

如果 readiness audit 没有合适 DeckKit、outline 缺页型或需要改组件结构，先进入
`deck-generator-workflow.md` 创建/扩展 DeckKit；不要把临时 generator 当作最终交付路径。

---

## 3. prompt → outline → DeckKit/content

### 3.1 outline 中间表示

先得到一份结构化 outline（参考 `assets/examples/create/qbr-outline.json`），用页型 `kind`
描述每页。该示例用到的 5 种 `kind`：

| `kind`    | 用途         | 关键字段                            |
| --------- | ------------ | ----------------------------------- |
| `title`   | 封面 / 扉页  | `title` / `subtitle`                |
| `section` | 章节分割     | `title` / `subtitle` / `eyebrow`    |
| `kpi`     | KPI 卡片网格 | `items[].{label,value,delta}`       |
| `two-col` | 左右对照     | `left/right.{heading,text,bullets}` |
| `compare` | 比较表格     | `headers[]` / `rows[][]`            |

outline 顶层还带 `out`（输出路径）和 `themePack` / `stylePack`（如 `corporate-blue` /
`consulting`）。主题色、字体、底色、字号节奏先从 themePack/stylePack 派生；用户给了
`rebrand.{colors,fonts,background}` 时再覆盖并走 `set-theme` / `remap-theme`。`kind` 是页型意图、不强制枚举——
探索生成器时可修改模板的 `executive-grid` 中 8 个示例：`slideCover` / `slideAgenda` / `slideKPI` /
`slideChart` / `slideTable` / `slidePillars`（多列支柱）/ `slideWorkflow` / `slideHero`（全色收尾），
挑最接近的页型改内容。

如果用户已经提供页序、章节、标题、Markdown 大纲、表格结构或逐页内容，直接采用用户大纲并
标准化为 `outline.json`；不要擅自重排叙事、替换页序或删改核心观点。允许做的改动仅限于：
结构化字段、映射 DeckKit 页型、压缩过长标题、补齐缺省受众/风格/输出路径。只有大纲自相矛盾、
页数/内容明显装不下、缺少生成所必需的信息，或用户要求优化结构时，才给一个短修订版或问题让
用户确认。

Express 生成的 `deck_lock.json` 必须记录这些推断值和 `assumptions[]`，但不等待用户批准。
如果后续 DeckKit 选择、theme/style 或 slide type 发生变化，先更新 lock，再生成 content/patch；
不要让 patch 里的颜色、字体或资源来源绕过 lock。没有外部图片、logo、复用素材或本轮生成资产时，
不要创建空的 `assets_manifest.json`。

### 3.2 无可用 DeckKit 时：创建/扩展 DeckKit

只有 readiness audit 没有合适 DeckKit、outline 缺页型或需要改组件结构时，才把
`assets/examples/generator/deck-generator-template.mjs` 和相邻的 `theme-packs.generated.mjs`
一起复制到 run 目录。目标是抽取/扩展 DeckKit，再回到
content manifest 生产路径；不要把临时 generator 当作最终交付路径。按 outline 改这三处即可，
**不要重写 helper**：

1. **theme/style 选择** —— 默认 `--theme corporate-blue --style consulting`；可换成
   `consulting-grey` / `startup-vibrant` / `academic-formal` / `gov-blue` /
   `tech-dark` / `health-soft` / `minimal-mono` / `cartesian-warm`，style 可换 `minimal` /
   `product` / `cartesian`，或用
   `--theme-pack ./theme.json --style-pack ./style.json` 加载外部 pack。
2. **各 slide 函数内容** —— 填 outline 里的标题、KPI 数据、表格行、bullet。
3. **`TOTAL` + `variantSlideSets` 中所选布局的函数列表** —— 改成实际页数与页序。

helper（`nm()` 双向命名 / `grid()` 网格 / `_txH()` 字号→盒高 / `pageChrome()` / `pageHeader()`）
的签名与避坑细节见 `deck-generator-workflow.md`，express 直接用、不展开。

---

## 4. 风格选择（themePack / stylePack）

当前 express 的"选风格"= 选一个 themePack + 一个 stylePack：

- 用户**明确指定**色/品牌 → 遵守，优先映射到已有 themePack；没有命中就临时写外部
  themePack JSON，并在生成后用 `remap-theme` / `swap-theme` 保持 deck 主题一致。
- 用户**没指定** → 按内容领域推断一个安全牌，并在产出说明里记录理由（避免自嗨）。
  默认安全牌是 `corporate-blue` + `consulting`，字体 `Inter` + `Source Han Sans SC`。
- 可用 catalog：`xdoc pptx catalog themes --json`，或查看
  `assets/themes/catalog.json` / `references/content/theme-packs.md`。

生成后换风格不用改 `C` 重跑：直接执行
`xdoc pptx swap-theme out.pptx --theme consulting-grey -o out-grey.pptx` 或
`xdoc pptx swap-style out.pptx --style minimal -o out-minimal.pptx`。

---

## 5. 质量门与丰富度

express 默认按**客户演示级**产出，不交 recipe-only 草稿。硬指标（详见
`create-studio.md` 的可读性红线与 `rich-deck-patterns.md` 的视觉模式）：

- **op 量级**：`jq '.ops|length'` 仅用于了解构建规模，不设操作数下限；是否需要补充视觉元素，
  应根据内容、页面结构和渲染结果判断。
- **每页有视觉锚点**：页眉/页脚/章节标记/导航 或 全屏 hero 之一。
- **chart 页必须有结论 callout**：右 1/3 放 2-3 个数字卡，别让用户自己解读图。
- **长文本压缩**成结论 / 表格 / callout / notes，不堆满正文。
- **字号有阅读底线**：核心正文 ≥ `10.5pt`；label / badge / chart / table ≥ `9pt`；
  页脚 / 来源可到 `8.5-9pt` 但不承载关键信息。内容塞不下时删字或换布局，不靠缩小字号。
- **构图有几何纪律**：对比页中轴、VS 圆、流程中心框、连接线和箭头端点必须从 shape bbox
  推导；同排文字与形状垂直居中，左右对称布局要数学居中。

每页该长什么样、可粘贴的 patch 骨架和 7 页推荐结构见 `rich-deck-patterns.md`。

---

## 6. vision-check 自动闭环

apply 后跑 `xdoc pptx vision-check out.pptx --json`（render-free 几何自检；公共门禁见 `../common-workflow.md`）。
闭环规则：

- **允许尝试的修复**：选择一条 `remediation.autoRetry == true` 的建议，核对
  `kind="apply-to-document"` 及文档摘要，在精确旧文档上仅执行它的完整 repair patch。
  假设 `/issues/0` 是检查后选中的具体建议，并已有步骤 7 的首次提交 capsule：

  ```bash
  node <skill-root>/scripts/cli/runtime/remediation.mjs apply \
    --capsule run/remediation-context --report vision.json --pointer /issues/0 \
    --document out.pptx --output run/repaired.pptx
  xdoc pptx vision-check run/repaired.pptx --json > run/vision-after.json
  ```

- **人工确认**：`autoRetry==false` 的静态视觉问题（overlap / overflow / unexpected-wrap / alignment）
  不是可忽略项；它们是需要人工处理的候选修复。放大盒子或挪形状可能引入**新**碰撞，
  看 `reason` 后改 generator / layout / 文案 / textbox 尺寸，再重 apply。
  `font-too-small` 无自动修复（放大字号会反触发 overflow），但创建型 deck 不能把它当装饰性
  warning：删字、放大容器或换版式后重跑。

- **交付门槛**：创建型 deck 必须让 `summary.bySeverity.high == 0` 且
  `summary.bySeverity.medium == 0`。`text-overflow-estimate`、`geometry-overlap`、
  `text-unexpected-wrap`、`text-edge-margin` 这类 medium 常常对应真实字符重叠、
  换行压字、subtitle 孤行或页脚撞正文，不能因为不是 high 就放行。

vision-check 是静态估算；**字符实际重叠 / 字体换行压字 / 小字号可读性 / 对比度 /
箭头是否歪、连接线是否接上 / 中轴标识是否真居中 / 装饰是否真盖住文字 / 配色协调仍靠
§2 第 11 步的 PNG 复核**（公共检查清单见 `../common-workflow.md`），不可省。

---

## 7. 最小确认策略

express 的核心是**不像 ppt-master 那样逐项确认**（它要 8 次 BLOCKING 确认）。原则：

- **能合理推断的全部用默认**，并在最终回复里**说明做了哪些假设**（受众、页数、风格、配色）。
- **用户已给大纲时默认采用**，只做标准化和页型映射；不要为了展示能力重新设计结构。若需要
  调整页序、增删页或改核心表达，先用短版修订大纲请求确认。
- **没有大纲时也必须先生成内部 `outline.json`**，但 Express 默认自动继续，不把大纲确认作为
  阻塞步骤；最终摘要中列出主要假设。
- **只在缺少以下任一关键信息且无法合理推断时**，才**一次性**问清（用一个 AskUserQuestion 合并问，
  不要来回追问）：
  - **主题/内容**：完全不知道要讲什么（连领域都推不出来）。
  - **页数**：内容体量差异巨大、推断区间太宽（如可能 5 页也可能 20 页）。
  - **关键数据**：deck 以数据为主（财报/实验），但用户没给数也没给数据文件。
- 风格、配色、字体、版式密度**一律不问**，按内容领域选安全牌并记录理由；用户不满意时
  用 `swap-theme` / `swap-style` 秒级换一版。
- **长 deck / 高风险 deck 可以推荐 split，但不默认阻塞**：当页数 `>= 12`、source 材料很长、
  Reference Create 信息多、资源/公式多，或用户要正式投资人/董事会/客户汇报时，在生成
  `outline.json` + `deck_lock.json` 后说明“可在新会话继续生成”。用户接受时按
  `../runtime/resume-split-mode.md` 写 `resume_manifest.json` 并停止；用户没接受就同会话继续。

---

## 8. 升级信号：何时转 Studio / Edit

express 跑到一半发现下列任一信号，就升级（DeckKit / generator / op 基础设施共用，无需重来）：

| 信号                                       | 升级到           | 去向                                                        |
| ------------------------------------------ | ---------------- | ----------------------------------------------------------- |
| 要像素级定位 / 自由布局 / 演示动效拟态     | **Studio**       | `create-studio.md` + `../edit/patch-ops-cheatsheet.md`      |
| 要自定义 chart 样式 / 二轴 combo / chartEx | **Studio**       | `../content/charts.md`                                      |
| 要套已有品牌 profile / 做品牌合规          | **Studio**       | `../content/styles-and-themes.md` + `../content/recipes.md` |
| 用户给参考 PPTX，要求按新大纲生成新 deck   | Reference Create | `reference-create.md`                                       |
| 要把一份 JSON/CSV 批量套进模板             | 数据驱动         | `../content/data-driven.md`                                 |
| 用户改口"在这份已有 deck 上改/加"          | **Edit**         | `../edit/edit-mode.md` + `../edit/inspect-and-edit.md`      |
| op 数已超 ~100、手维护吃力                 | 仍 Express       | 先选 DeckKit；无匹配时扩展 DeckKit（见 §3.2）               |

> Express 不是能力天花板，是**默认省事路径**。它产出的就是原生可编辑 PPTX + sidecar，
> 任何时候都能用 Edit 模式继续 inspect / patch / 回滚。
