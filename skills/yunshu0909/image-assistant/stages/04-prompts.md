# 阶段4：提示词封装（Prompt Pack：可执行生成包）

**目标：** 把阶段3的 Copy Spec 原样封装成"可复制/可调用"的提示词包（Prompt Pack），并支持批量出图。阶段4不负责改文案，只负责：模板拼装、风格一致、参数/约束齐全、避免模型乱加字、把提示词整理成可批量请求的结构化请求包。

## 封装原则（避免和阶段3混淆）

- **Copy Spec 是唯一真值**：提示词中“必须逐字放入”的文字，直接来自阶段3，不在这里重写。
- **提示词负责“怎么画”**：画幅、版式、留白、对齐、图标隐喻、风格块、强制约束、负面提示、参数。
- **封面类默认“禁额外小字”**：明确写“除指定文字外不要生成任何额外文字”。

## 生成步骤（按顺序）

1. 选定结构模板（与 Copy Spec 的版式一致）
2. 粘贴通用风格块：`templates/style-block.md`
   - **风格基准锁定**：每张图都必须以 `templates/style-block.md` 定义的风格作为**唯一允许的基础风格**来生成（奶油纸 + 彩铅线稿 + 淡水彩 + 轻涂鸦、少字高可读）。
   - **不得换风格**：不要让模型自行切换成扁平矢量海报风/3D/摄影写实等“更像信息图默认风格”的路线。
   - 允许你用自己的话描述该风格，但不能删掉关键要素与负面约束（否则风格会被模型先验带偏）。
3. 写清楚画幅/用途（PPT远看 vs 手机近看）与排版硬约束（对齐、留白、字号）
4. 粘贴 Copy Spec 的"必须逐字放入的文字"
5. 加强制约束 + 负面提示（无乱码/不加字/不密集小字/不背景杂乱）
6. 生成**批量请求包（JSONL）**：把每张图的 Prompt 内容写入一行（参考 `templates/apimart-requests-jsonl.md`）
7. 用户选择批量API方式后：直接生成JSONL并执行批量出图（不再二次确认）

## 模板使用

- 通用风格块：`templates/style-block.md`
- 结构模板：
  - 封面路线图（目录/5步）：`templates/16x9-cover-roadmap.md`
  - 对比两卡：`templates/16x9-contrast-2cards.md`
  - 三卡洞察：`templates/16x9-3cards-insights.md`
  - 五格漫画：`templates/16x9-5panel-comic.md`
  - 通用信息图：`templates/16x9-infographic.md`

## 本阶段输出物

- **Prompt Pack**：按"图1/图2/…"编号输出；每张图一个独立代码块（便于复制/脚本调用）；代码块外最多 1–2 句说明
- **Batch Request Pack（JSONL）**：例如 `out/apimart.requests.jsonl`（一行一张图，字段见下文）
- **执行方式**：当用户在阶段4明确选择"批量API"时，先输出提示词让用户查看（选项A：手动出图 或 选项B：批量API），一旦用户选择B，直接生成JSONL并执行，不再二次确认

## 为什么“阶段4”容易风格跑偏（解释逻辑）

阶段4本质是“用文字去约束一个带强默认审美的出图模型”，风格会被多方力量拉扯：

1. **模型先验（Style Prior）**：很多模型看到 “infographic/信息图” 会自动偏向“干净的扁平矢量/海报风”，即使你写了彩铅水彩，也可能只被当作弱建议。
2. **可读性约束会压过质感**：当你同时要求“中文大字号、严格对齐、少字、清晰”，模型会优先保证字清楚与版式稳定，牺牲纸纹、彩铅笔触等“质感细节”。
3. **风格基准不够“排他”会降权**：如果不强调“这是唯一允许风格，不能换”，模型会把它当成“可选项”，然后自动回到信息图的默认风格（常见是扁平矢量/海报风）。
4. **风格词太短/太抽象**：仅写“彩铅水彩”不足以锁定细节，需要补“纸纹可见、笔触可见、轻晕染”等可观察特征，并配合负面约束（已在风格块中补强）。

实操上要提升稳定性：在每张图的 prompt 里都明确“以该风格为唯一基础，不得换风格”，并加入“不要扁平矢量/不要3D/不要摄影”等负面约束来对冲模型的默认风格。

---

## 批量调用 APIMart API 出图（用户选择后直接执行）

> 规则：**先封装 Prompt Pack 并展示给用户 → 询问"手动出图"还是"批量API" → 用户选择"批量API"后直接生成JSONL并执行**。不在生成JSONL后再次确认。

### 需要的两个东西

1. **API 配置**（建议放本地文件）：`scripts/apimart.env`（参考 `scripts/apimart.env.example` 与 `templates/api-config.md`）
2. **批量请求包**（JSONL）：例如 `out/apimart.requests.jsonl`（参考 `templates/apimart-requests-jsonl.md`）

### 请求包字段（每行一张图）

- `id`：建议 `01` / `02` / …
- `prompt`：阶段4输出的 Prompt 内容（可直接粘贴）
- `size`：默认 `16:9`
- `n`：默认 `1`
- `resolution`：默认 `2K`
- `model`：默认 `gemini-3-pro-image-preview`
- `pad_url`：可留空（暂不需要垫图 URL）

### 运行方式（二选一）

**A) 用脚本批量出图（推荐）**

```bash
python3 scripts/apimart_batch_generate.py \
  --config scripts/apimart.env \
  --input out/apimart.requests.jsonl
```

**B) dry-run（不请求；把 curl 与请求信息写入单个 `run.json`）**

```bash
python3 scripts/apimart_batch_generate.py \
  --config scripts/apimart.env \
  --input out/apimart.requests.jsonl \
  --dry-run
```

> curl 格式参考：`templates/apimart-curl.md`
