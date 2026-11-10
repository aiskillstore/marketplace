# Visual QA and Asset Slots

本文件把 guizang 可借鉴的视觉验收经验转成 pptx-nova 可执行规则：PPTX 仍由 DeckKit / xdoc
原生 shape 生成，图片只作为素材进入明确槽位，不生成整页 slide chrome。

## P0 必修项

交付前任何 P0 都必须清零：

- 文字重叠、截断、换行压字、低于阅读底线的字号。
- 数字和单位被拆开，如 `50%`、`+82%`、`12 months`、季度、年份、短英文标签。
- 页脚、来源、caption 与正文或图表相撞。
- 深色页上出现低对比黑字，浅色页上出现低对比浅字。
- 图片里自带 PPT 标题、页码、页脚、logo、边框、卡片框或整页 chrome。
- 连接线 / 箭头没有从目标 shape bounding box 推导，端点漂浮或穿过正文。
- 输出路径误覆盖用户已有文件。

## P1 质量项

P1 不一定阻塞草稿，但客户演示级 / 投资人级 / 董事会 deck 需要修到可解释：

- 非 appendix 页有明确观点或方向，而不是只有 topic label；展示主标题/副标题短、可扫读、
  不因完整结论而破坏布局，证明对象能支撑 `claimTitle`。
- 展示主标题和副标题没有句末句号；问号/感叹号只在刻意提问或强调时出现。
- 长 deck 的 layout group 有足够变化，避免连续多页同一张卡片网格。
- 卡片、表格、caption、footnote 不贴边，安全区和内边距节奏一致。
- 图片按 `slotId + ratio + fitPolicy` 放置，人物脸、产品主体、截图关键区域不被裁掉。
- 图表页有结论 callout，legend / axis / data label 不互相遮挡。
- 每页节奏可归类为 `anchor`、`dense` 或 `breathing`，相邻页面不要全是同一种密度。
- `layoutIntent` 和 `visualDensity` 与最终 PNG 一致；如果 lock 写的是 breathing，PNG
  不应呈现为高密度表格墙。
- 容器、箭头、badge、icon 需要表达分组、方向、层级或数据关系；只为填空的装饰应删除。

## Asset Slot Manifest

使用图片、截图、AI 生成素材、logo 或公式时，先在 `assets_manifest.json` 登记，再让
`deck_lock.json` / `content.json` 用 asset id 引用。图片槽位最小字段：

```json
{
  "id": "hero_photo",
  "kind": "image",
  "status": "generated",
  "licenseRisk": "none",
  "path": "assets/hero-photo.png",
  "source": {
    "kind": "ai",
    "prompt": "Photographic background of an urban mobility team, no text, no slide frame"
  },
  "pptxUse": {
    "role": "hero-background",
    "slotId": "hero.full_bleed",
    "ratio": "16:9",
    "fitPolicy": "cover",
    "noSlideChrome": true
  }
}
```

规则：

- `slotId` 表示设计意图，不表示文件名。
- `ratio` 只用 `21:9`、`16:10`、`16:9`、`4:3`、`3:2`、`3:4`、`1:1`。
- `fitPolicy` 只用 `cover`、`contain`、`no-crop`、`crop-safe`。
- AI 图片 prompt 只描述素材本身；不要要求模型生成 PPT 页面、文字、图表、页码或品牌 chrome。
- `content.json` 可用 `slides[].assets` 引用普通资产，用 `slides[].imageSlots` 表达语义槽位：

```json
{
  "type": "heroSlide",
  "rhythm": "anchor",
  "assets": ["hero_photo"],
  "imageSlots": {
    "hero.full_bleed": "hero_photo"
  },
  "data": {
    "title": "Q2 performance review"
  }
}
```

`cli/create/check-lock.mjs` 会检查 manifest id 覆盖、图片 slot 字段和 AI 图片
`noSlideChrome`；`missing` / `needs-user` / `forbidden` 会阻塞，`placeholder` /
`needs-review` 会提示复核；`validate-content.mjs` 会检查 DeckKit 的 layout contract 与
diversity gate。

DeckKit 的页型槽位参考（`node <skill-root>/scripts/cli/deckkits/slots.mjs --deckkit <id> [--format md|json]`）
还会列出 `layoutContract.slideTypes[*].assetSlots`。其中
`acceptsAsset: false` 表示该页型只有可编辑的占位框：`imageLabel` / `caption` 等字段只
负责显示说明文字，不能通过 `content.json.imageSlots` 绑定图片。若需要真实图片，应改用
声明了可注入资产的页型，或先扩展 DeckKit 的资产合同；不要把资产 id 填入
placeholder-only 槽位后继续生成。

`acceptsAsset: true` 表示 build 会从 `assets_manifest.json` 解析对应 asset id。运行
`cli/create/build.mjs` 或标准 create runner 时必须同时传 `--assets`；runner 会把 manifest
所在目录作为 xdoc 的 `--asset-root`，patch 中只保留受限的相对路径。Cartesian 的
`image.editorial` 默认使用 `contain`，没有 `imageSlots` 绑定时继续渲染 crossed shell，
因此无合法图片的任务不会被迫使用伪造素材。
