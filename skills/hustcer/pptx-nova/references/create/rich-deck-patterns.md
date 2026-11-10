# Rich Deck Patterns —— 客户演示级 7 页 deck 起手势

本文档解决一个反复出现的问题：**用 recipe 拼出来的 deck 看起来很平**。

> 出处：这份文档来自一次实战 —— 用户做 Q2 季度回顾 deck，第一版用 12 个
> recipe ops 出了 5 页 PPTX，反馈"不够美观，不够丰富"。重写成 312 个 ops 的 7
> 页 deck 后才达标。本文档把那份 patch.json 里**可复用的模式**抽出来。

## 核心理念

Recipe 把布局和字号默认值预设好，并编译为普通 patch operations；具体内容仍须通过
schema、语义和视觉验证。部分 recipe 已提供 eyebrow、KPI delta 等内容，但不会自动
覆盖每个任务的视觉需求。按内容需要，可通过 DeckKit 或显式 patch 补充：

- 顶部品牌色横条 / 左侧 accent 竖条 / eyebrow / 页脚 / 页码
- KPI 卡片的顶部色条 / delta pill / 注脚
- chart 旁的 highlight callout 卡片
- 全色 hero 收尾

这些元素可用原生形状、文本和连接线实现，也可由 DeckKit 生成。是否添加由内容和
视觉层级决定，不要求每页堆满装饰。

## 构建规模与质量

`jq '.ops | length'` 只记录 authored ops 数量。一个 recipe 或 macro 可以展开为多个操作，
同一对象的样式也可以集中在一个聚合 op 中，因此操作数不能判断视觉是否丰富或是否可交付。
不设操作数下限；按叙事、信息层级、可读性、可编辑性和真实渲染结果验收。

---

## 推荐调色板（Google Material 风格）

```json
{
  "accent1": "1A73E8", // 主蓝
  "accent1Dark": "0B57D0", // hero 深蓝
  "accent2": "34A853", // 绿（成功 / 正增长）
  "accent3": "FBBC04", // 黄（提醒）
  "accent4": "EA4335", // 红（风险 / 负增长）
  "textPrimary": "1F1F1F",
  "textSecondary": "5F6368",
  "textMuted": "9AA0A6",
  "cardBg": "F8F9FA",
  "divider": "E8EAED",
  "white": "FFFFFF"
}
```

字号节奏（16:9 / 13.333in 宽）：

| 用途                 | 字号    |
| -------------------- | ------- |
| Hero title（收尾页） | 54pt    |
| 封面主标题           | 60pt    |
| 内容页主标题         | 32-36pt |
| KPI 大数字           | 44pt    |
| 章节标题             | 22-28pt |
| 正文                 | 14-16pt |
| Delta pill           | 12pt    |
| Eyebrow              | 10-11pt |
| 页脚 / 注脚          | 9-10pt  |

字体默认 `Inter`（西文）+ `Source Han Sans SC`（中文）。

---

## 7 页 deck 推荐结构

```
01 封面    title-slide 风格
02 议程    5 个编号卡片
03 KPI     4 across 卡片网格
04 主数据  chart 左 2/3 + 右 1/3 callout
05 对比    表格 + 结论 banner
06 行动    3 列支柱
07 收尾    全色 hero + 3 个 takeaway
```

下面每节给出**可粘贴的 op 序列**（坐标按 16:9 / 13.333in × 7.5in 调好）。

---

## §1 通用：每页顶部品牌条 + 页脚（每页都加）

```json
[
  { "op": "add-shape", "slide": N, "kind": "rectangle",
    "x": "0in", "y": "0in", "w": "13.333in", "h": "0.08in",
    "name": "TopBrandBar" },
  { "op": "set-shape", "slide": N, "shape": { "name": "TopBrandBar" },
    "fill": { "type": "solid", "color": "1A73E8" } },
  { "op": "set-shape", "slide": N, "shape": { "name": "TopBrandBar" },
    "line": { "noLine": true } },

  { "op": "add-text-box", "slide": N,
    "x": "0.6in", "y": "7.05in", "w": "6in", "h": "0.3in",
    "name": "PageFooter" },
  { "op": "set-text-frame", "slide": N, "shape": { "name": "PageFooter" },
    "text": "Q2 2026 业务回顾  ·  0N / 07" },
  { "op": "set-run", "slide": N, "shape": { "name": "PageFooter" },
    "paragraph": 0, "run": 0,
    "font": { "name": "Inter", "size": "9pt", "color": "9AA0A6" } },

  { "op": "add-text-box", "slide": N,
    "x": "11.5in", "y": "0.2in", "w": "1.7in", "h": "0.3in",
    "name": "Watermark" },
  { "op": "set-text-frame", "slide": N, "shape": { "name": "Watermark" },
    "text": "structurify.io" },
  { "op": "set-run", "slide": N, "shape": { "name": "Watermark" },
    "paragraph": 0, "run": 0,
    "font": { "name": "Inter", "size": "9pt", "bold": true, "color": "E8EAED" } }
]
```

shape name 用 `TopBrandBar_S{N}` 等区分，避免跨 slide selector 歧义。

---

## §2 封面页（slide 0）

要素：顶部品牌条 + 左侧 accent 竖条 + eyebrow + 主标题 + 副标题 + tagline + 页脚。

```json
[
  { "op": "add-slide", "layout": "blank" },

  {
    "op": "add-shape",
    "slide": 0,
    "kind": "rectangle",
    "x": "0in",
    "y": "0in",
    "w": "13.333in",
    "h": "0.08in",
    "name": "CoverTopBar"
  },
  {
    "op": "set-shape",
    "slide": 0,
    "shape": { "name": "CoverTopBar" },
    "fill": { "type": "solid", "color": "1A73E8" }
  },
  {
    "op": "set-shape",
    "slide": 0,
    "shape": { "name": "CoverTopBar" },
    "line": { "noLine": true }
  },

  {
    "op": "add-shape",
    "slide": 0,
    "kind": "rectangle",
    "x": "0.6in",
    "y": "2.4in",
    "w": "0.12in",
    "h": "2.2in",
    "name": "CoverAccentBar"
  },
  {
    "op": "set-shape",
    "slide": 0,
    "shape": { "name": "CoverAccentBar" },
    "fill": { "type": "solid", "color": "1A73E8" }
  },
  {
    "op": "set-shape",
    "slide": 0,
    "shape": { "name": "CoverAccentBar" },
    "line": { "noLine": true }
  },

  {
    "op": "add-text-box",
    "slide": 0,
    "x": "1in",
    "y": "2.4in",
    "w": "10in",
    "h": "0.4in",
    "name": "CoverEyebrow"
  },
  {
    "op": "set-text-frame",
    "slide": 0,
    "shape": { "name": "CoverEyebrow" },
    "text": "QUARTERLY BUSINESS REVIEW"
  },
  {
    "op": "set-run",
    "slide": 0,
    "shape": { "name": "CoverEyebrow" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "11pt", "bold": true, "color": "1A73E8" }
  },

  {
    "op": "add-text-box",
    "slide": 0,
    "x": "1in",
    "y": "2.9in",
    "w": "11in",
    "h": "1.4in",
    "name": "CoverTitle"
  },
  {
    "op": "set-text-frame",
    "slide": 0,
    "shape": { "name": "CoverTitle" },
    "text": "Q2 2026 业务回顾"
  },
  {
    "op": "set-run",
    "slide": 0,
    "shape": { "name": "CoverTitle" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "60pt", "bold": true, "color": "1F1F1F" }
  },

  {
    "op": "add-text-box",
    "slide": 0,
    "x": "1in",
    "y": "4.4in",
    "w": "11in",
    "h": "0.5in",
    "name": "CoverSubtitle"
  },
  {
    "op": "set-text-frame",
    "slide": 0,
    "shape": { "name": "CoverSubtitle" },
    "text": "Aug 2026  ·  业务部"
  },
  {
    "op": "set-run",
    "slide": 0,
    "shape": { "name": "CoverSubtitle" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "22pt", "color": "5F6368" }
  }
]
```

加 tagline、footer 同 §1 模式。

---

## §3 议程页（slide 1）：5 个编号卡片

布局：2×2 + 底部 1 个，最后一个高亮（蓝色边框 + 浅蓝底）。

```json
[
  {
    "op": "add-shape",
    "slide": 1,
    "kind": "rounded-rectangle",
    "x": "0.6in",
    "y": "2in",
    "w": "5.6in",
    "h": "1.3in",
    "name": "AgendaCard1"
  },
  {
    "op": "set-shape",
    "slide": 1,
    "shape": { "name": "AgendaCard1" },
    "fill": { "type": "solid", "color": "F8F9FA" }
  },
  {
    "op": "set-shape",
    "slide": 1,
    "shape": { "name": "AgendaCard1" },
    "line": { "noLine": true }
  },

  {
    "op": "add-text-box",
    "slide": 1,
    "x": "0.9in",
    "y": "2.2in",
    "w": "0.6in",
    "h": "0.5in",
    "name": "AgendaNum1"
  },
  { "op": "set-text-frame", "slide": 1, "shape": { "name": "AgendaNum1" }, "text": "01" },
  {
    "op": "set-run",
    "slide": 1,
    "shape": { "name": "AgendaNum1" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "28pt", "bold": true, "color": "1A73E8" }
  },

  {
    "op": "add-text-box",
    "slide": 1,
    "x": "1.8in",
    "y": "2.3in",
    "w": "4.2in",
    "h": "0.8in",
    "name": "AgendaLabel1"
  },
  {
    "op": "set-text-frame",
    "slide": 1,
    "shape": { "name": "AgendaLabel1" },
    "text": "Q2 核心指标"
  },
  {
    "op": "set-run",
    "slide": 1,
    "shape": { "name": "AgendaLabel1" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "16pt", "bold": true, "color": "1F1F1F" }
  }
]
```

复制 5 份，编号颜色循环 `1A73E8 / 34A853 / FBBC04 / EA4335 / 1A73E8`。

---

## §4 KPI 网格（slide 2）：4-across 卡片（最常踩坑）

**不要用 `add-slide` 的 `recipe.kind: "kpi-grid"`**，它出来是 3+1 不是 4-across。手堆：

```json
[
  // 卡片 1（重复 4 次，x 间距 = (13.333 - 0.6*2 - 2.6*4) / 3 ≈ 0.27in）
  {
    "op": "add-shape",
    "slide": 2,
    "kind": "rounded-rectangle",
    "x": "0.6in",
    "y": "2.8in",
    "w": "2.6in",
    "h": "2.4in",
    "name": "KpiCard1"
  },
  {
    "op": "set-shape",
    "slide": 2,
    "shape": { "name": "KpiCard1" },
    "fill": { "type": "solid", "color": "FFFFFF" }
  },
  {
    "op": "set-shape",
    "slide": 2,
    "shape": { "name": "KpiCard1" },
    "line": { "width": "0.75pt", "color": "E8EAED" }
  },

  // 顶部色条（4 张卡用 4 个颜色）
  {
    "op": "add-shape",
    "slide": 2,
    "kind": "rectangle",
    "x": "0.6in",
    "y": "2.8in",
    "w": "2.6in",
    "h": "0.08in",
    "name": "KpiTopBar1"
  },
  {
    "op": "set-shape",
    "slide": 2,
    "shape": { "name": "KpiTopBar1" },
    "fill": { "type": "solid", "color": "1A73E8" }
  },
  {
    "op": "set-shape",
    "slide": 2,
    "shape": { "name": "KpiTopBar1" },
    "line": { "noLine": true }
  },

  // Label
  {
    "op": "add-text-box",
    "slide": 2,
    "x": "0.85in",
    "y": "3.1in",
    "w": "2.2in",
    "h": "0.4in",
    "name": "KpiLabel1"
  },
  { "op": "set-text-frame", "slide": 2, "shape": { "name": "KpiLabel1" }, "text": "营收" },
  {
    "op": "set-run",
    "slide": 2,
    "shape": { "name": "KpiLabel1" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "12pt", "color": "5F6368" }
  },

  // 大数字（44pt）
  {
    "op": "add-text-box",
    "slide": 2,
    "x": "0.85in",
    "y": "3.5in",
    "w": "2.2in",
    "h": "1in",
    "name": "KpiValue1"
  },
  { "op": "set-text-frame", "slide": 2, "shape": { "name": "KpiValue1" }, "text": "$42M" },
  {
    "op": "set-run",
    "slide": 2,
    "shape": { "name": "KpiValue1" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "44pt", "bold": true, "color": "1F1F1F" }
  },

  // Delta pill（绿底白字）
  {
    "op": "add-shape",
    "slide": 2,
    "kind": "rounded-rectangle",
    "x": "0.85in",
    "y": "4.55in",
    "w": "1.3in",
    "h": "0.3in",
    "name": "KpiDelta1"
  },
  {
    "op": "set-shape",
    "slide": 2,
    "shape": { "name": "KpiDelta1" },
    "fill": { "type": "solid", "color": "E6F4EA" }
  },
  {
    "op": "set-shape",
    "slide": 2,
    "shape": { "name": "KpiDelta1" },
    "line": { "noLine": true }
  },
  { "op": "set-text-frame", "slide": 2, "shape": { "name": "KpiDelta1" }, "text": "▲ +12% YoY" },
  {
    "op": "set-run",
    "slide": 2,
    "shape": { "name": "KpiDelta1" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "12pt", "bold": true, "color": "188038" }
  },

  // 注脚
  {
    "op": "add-text-box",
    "slide": 2,
    "x": "0.85in",
    "y": "4.9in",
    "w": "2.2in",
    "h": "0.3in",
    "name": "KpiNote1"
  },
  {
    "op": "set-text-frame",
    "slide": 2,
    "shape": { "name": "KpiNote1" },
    "text": "GAAP 口径,含订阅收入"
  },
  {
    "op": "set-run",
    "slide": 2,
    "shape": { "name": "KpiNote1" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "10pt", "color": "9AA0A6" }
  }
]
```

KPI 4 个卡片 x 坐标 = `0.6 / 3.5 / 6.4 / 9.3 in`（间距 0.3in）。

顶部色条颜色循环：`1A73E8 / 34A853 / FBBC04 / EA4335`。

Delta pill 颜色：

- 正增长 → bg `E6F4EA` / text `188038`（绿）
- 负增长 → bg `FCE8E6` / text `C5221F`（红）

---

## §5 chart 页（slide 3）：chart + 右侧 callout

```
┌─ slide ────────────────────────────────┐
│ eyebrow                                │
│ title                                  │
│ subtitle                               │
│ ┌── chart 8.5in ──┐  ┌─ callout 3in ─┐│
│ │                  │  │ H1 同比       ││
│ │                  │  │ +21.9%        ││
│ │                  │  ├───────────────┤│
│ │                  │  │ Q2 单季新高   ││
│ │                  │  │ $42M          ││
│ │                  │  ├───────────────┤│
│ │                  │  │ H2 预测       ││
│ │                  │  │ $96M          ││
│ └──────────────────┘  └───────────────┘│
└────────────────────────────────────────┘
```

chart：

```json
{
  "op": "add-chart",
  "slide": 3,
  "kind": "column",
  "variant": "clustered",
  "x": "0.6in",
  "y": "2.4in",
  "w": "8.5in",
  "h": "4.3in",
  "name": "RevChart",
  "legend": "bottom",
  "data": {
    "categories": ["Q1", "Q2", "Q3 (预测)", "Q4 (预测)"],
    "series": [
      { "name": "2025", "values": [30, 34, 36, 38] },
      { "name": "2026", "values": [36, 42, 46, 50] }
    ]
  }
}
```

> ⚠️ Q3/Q4 不要填 `0` —— 看起来像业务断崖。要么填预测值并标 `(预测)`，要么改用
> partial categories。

样式：

```json
[
  {
    "op": "set-chart",
    "slide": 3,
    "shape": { "name": "RevChart" },
    "series": [
      { "series": 0, "fill": { "type": "solid", "color": "BDC1C6" } },
      { "series": 1, "fill": { "type": "solid", "color": "1A73E8" } }
    ],
    "dataLabels": [{ "scope": { "series": 1 }, "showValue": true, "position": "outside-end" }],
    "axes": [
      {
        "axis": "value",
        "line": { "color": "9AA0A6" },
        "gridlines": { "color": "EEEEEE" }
      }
    ]
  }
]
```

callout 卡片（3 个，纵向排列）：

```json
[
  {
    "op": "add-shape",
    "slide": 3,
    "kind": "rounded-rectangle",
    "x": "9.5in",
    "y": "2.4in",
    "w": "3.2in",
    "h": "1.3in",
    "name": "Callout1"
  },
  {
    "op": "set-shape",
    "slide": 3,
    "shape": { "name": "Callout1" },
    "fill": { "type": "solid", "color": "E8F0FE" }
  },
  {
    "op": "set-shape",
    "slide": 3,
    "shape": { "name": "Callout1" },
    "line": { "noLine": true }
  },
  {
    "op": "add-text-box",
    "slide": 3,
    "x": "9.7in",
    "y": "2.55in",
    "w": "3in",
    "h": "0.4in",
    "name": "CalloutLabel1"
  },
  { "op": "set-text-frame", "slide": 3, "shape": { "name": "CalloutLabel1" }, "text": "H1 同比" },
  {
    "op": "set-run",
    "slide": 3,
    "shape": { "name": "CalloutLabel1" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "12pt", "bold": true, "color": "1F1F1F" }
  },
  {
    "op": "add-text-box",
    "slide": 3,
    "x": "9.7in",
    "y": "2.95in",
    "w": "3in",
    "h": "0.7in",
    "name": "CalloutValue1"
  },
  { "op": "set-text-frame", "slide": 3, "shape": { "name": "CalloutValue1" }, "text": "+21.9%" },
  {
    "op": "set-run",
    "slide": 3,
    "shape": { "name": "CalloutValue1" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "36pt", "bold": true, "color": "1F1F1F" }
  }
]
```

callout 颜色循环（淡蓝 / 淡绿 / 淡黄）：bg `E8F0FE / E6F4EA / FEF7E0`。

y 坐标：`2.4 / 3.85 / 5.3 in`（每张 1.3in 高 + 0.15in 间距）。

---

## §6 对比表（slide 4）：表格 + 结论 banner

```json
[
  {
    "op": "add-table",
    "slide": 4,
    "rows": 7,
    "columns": 3,
    "x": "0.8in",
    "y": "2.4in",
    "w": "11.7in",
    "h": "3.6in",
    "name": "CompareTable",
    "data": [
      ["维度", "旧方案", "新方案"],
      ["技术栈", "python-pptx + 手工脚本", "xdoc CLI + 声明式 patch"],
      ["编辑性", "部分可编辑、样式易丢失", "原生可编辑,保留主题"],
      ["预演能力", "无 dry-run", "支持 --dry-run --json"],
      ["错误处理", "Python 异常,难以恢复", "结构化错误 + 目标绑定修复"],
      ["审计回放", "无", "sidecar 记录,支持回滚"],
      ["上线速度", "1-2 周", "1-2 天"]
    ]
  },

  {
    "op": "set-table",
    "slide": 4,
    "shape": { "name": "CompareTable" },
    "cells": [
      {
        "row": 0,
        "column": 0,
        "style": {
          "fill": { "type": "solid", "color": "1A73E8" },
          "font": { "bold": true, "color": "FFFFFF" }
        }
      }
    ]
  },
  // ... 其他表头列同样设置（追加到 cells 数组即可）

  // 结论 banner（蓝底白字）
  {
    "op": "add-shape",
    "slide": 4,
    "kind": "rounded-rectangle",
    "x": "0.8in",
    "y": "6.2in",
    "w": "11.7in",
    "h": "0.65in",
    "name": "ConclusionBanner"
  },
  {
    "op": "set-shape",
    "slide": 4,
    "shape": { "name": "ConclusionBanner" },
    "fill": { "type": "solid", "color": "1A73E8" }
  },
  {
    "op": "set-shape",
    "slide": 4,
    "shape": { "name": "ConclusionBanner" },
    "line": { "noLine": true }
  },
  {
    "op": "set-text-frame",
    "slide": 4,
    "shape": { "name": "ConclusionBanner" },
    "text": "结论:Q2 完成切换后,deck 生产链路提速约 5-7 倍,人/人 错误下降 80%+"
  },
  {
    "op": "set-run",
    "slide": 4,
    "shape": { "name": "ConclusionBanner" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "14pt", "bold": true, "color": "FFFFFF" }
  }
]
```

> ⚠️ `add-table` 默认坐标小、表格紧凑，必须显式指定 `w` / `h`，否则 slide 看起来
> "空荡"。一份 7 行 × 3 列的表格建议 11in × 3.6in（占据 slide 80% 宽度）。

---

## §7 行动计划（slide 5）：3 列支柱

3 列等宽卡片，顶部各一条不同色横条。

```json
[
  // 卡片 1（蓝）
  {
    "op": "add-shape",
    "slide": 5,
    "kind": "rounded-rectangle",
    "x": "0.6in",
    "y": "2.4in",
    "w": "4in",
    "h": "4in",
    "name": "Pillar1"
  },
  {
    "op": "set-shape",
    "slide": 5,
    "shape": { "name": "Pillar1" },
    "fill": { "type": "solid", "color": "F8F9FA" }
  },
  {
    "op": "set-shape",
    "slide": 5,
    "shape": { "name": "Pillar1" },
    "line": { "noLine": true }
  },
  // 顶部色条
  {
    "op": "add-shape",
    "slide": 5,
    "kind": "rectangle",
    "x": "0.6in",
    "y": "2.4in",
    "w": "4in",
    "h": "0.1in",
    "name": "Pillar1Bar"
  },
  {
    "op": "set-shape",
    "slide": 5,
    "shape": { "name": "Pillar1Bar" },
    "fill": { "type": "solid", "color": "1A73E8" }
  },
  {
    "op": "set-shape",
    "slide": 5,
    "shape": { "name": "Pillar1Bar" },
    "line": { "noLine": true }
  }
  // ... + eyebrow / 标题 / bullet 正文
]
```

3 列 x 坐标 = `0.6 / 4.85 / 9.1 in`（间距 0.25in），3 个色条颜色 `1A73E8 /
34A853 / FBBC04`。

---

## §8 收尾页（slide 6）：全色 hero

整页 `0B57D0`（深蓝）背景 + 左侧黄色 accent 竖条 + 白字 54pt 大标题 + 底部 3 个透
明白色 takeaway 卡片。

```json
[
  // 背景：set-slide-background
  { "op": "set-slide-background", "slide": 6, "fill": { "type": "solid", "color": "0B57D0" } },

  // 左侧黄色 accent 竖条
  {
    "op": "add-shape",
    "slide": 6,
    "kind": "rectangle",
    "x": "0.5in",
    "y": "2in",
    "w": "0.12in",
    "h": "2.8in",
    "name": "HeroAccentBar"
  },
  {
    "op": "set-shape",
    "slide": 6,
    "shape": { "name": "HeroAccentBar" },
    "fill": { "type": "solid", "color": "FBBC04" }
  },
  {
    "op": "set-shape",
    "slide": 6,
    "shape": { "name": "HeroAccentBar" },
    "line": { "noLine": true }
  },

  // Eyebrow
  {
    "op": "add-text-box",
    "slide": 6,
    "x": "0.9in",
    "y": "2in",
    "w": "10in",
    "h": "0.4in",
    "name": "HeroEyebrow"
  },
  {
    "op": "set-text-frame",
    "slide": 6,
    "shape": { "name": "HeroEyebrow" },
    "text": "PART 05  ·  结语与展望"
  },
  {
    "op": "set-run",
    "slide": 6,
    "shape": { "name": "HeroEyebrow" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "13pt", "bold": true, "color": "FBBC04" }
  },

  // 54pt 大标题
  {
    "op": "add-text-box",
    "slide": 6,
    "x": "0.9in",
    "y": "2.5in",
    "w": "12in",
    "h": "1.5in",
    "name": "HeroTitle"
  },
  {
    "op": "set-text-frame",
    "slide": 6,
    "shape": { "name": "HeroTitle" },
    "text": "稳健增长,持续投入"
  },
  {
    "op": "set-run",
    "slide": 6,
    "shape": { "name": "HeroTitle" },
    "paragraph": 0,
    "run": 0,
    "font": { "name": "Inter", "size": "54pt", "bold": true, "color": "FFFFFF" }
  },

  // 底部 3 个透明白色 takeaway
  {
    "op": "add-shape",
    "slide": 6,
    "kind": "rounded-rectangle",
    "x": "0.6in",
    "y": "5.6in",
    "w": "4in",
    "h": "1.4in",
    "name": "Takeaway1"
  },
  {
    "op": "set-shape",
    "slide": 6,
    "shape": { "name": "Takeaway1" },
    "fill": { "type": "solid", "color": "FFFFFF" }
  },
  {
    "op": "set-shape",
    "slide": 6,
    "shape": { "name": "Takeaway1" },
    "line": { "noLine": true }
  }
  // ... takeaway 文字注入
]
```

> 提示：纯白卡片在深蓝背景上对比度强，可直接放黑色文字；要"透明白色"效果可以用
> 浅色 fill 比如 `FFFFFF` + 后续 `set-shape` 的 `effect` 字段调整。

---

## §9 视觉验证清单（apply 完必做）

1. `xdoc convert out.pptx --to png -o previews --overwrite`
2. 用 Read 逐页看 PNG（7 张）
3. 检查：
   - [ ] 字符重叠 / 换行压字 / 文字溢出 / 截断
   - [ ] 字号可读（核心正文 ≥ `10.5pt`；label / badge / chart / table ≥ `9pt`；页脚 / 来源不低于 `8.5pt`）
   - [ ] 卡片、编号圆、中轴标识、VS 圆、中心框对齐（等距、宽度一致、bbox 中心线一致）
   - [ ] 连接线 / 箭头完整（水平线不歪，端点接到目标 shape 或保留一致间隙，箭头头方向正确）
   - [ ] 颜色对比度（白底文字 ≥ `1F1F1F`、蓝底文字 = `FFFFFF`）
   - [ ] 页码连续（`01 / 07` … `07 / 07` 没跳号）
   - [ ] 节奏统一（每页顶部品牌条都在、每页 eyebrow 字号一致）
   - [ ] chart 有数据标签 / 图例 / 轴标，没光秃秃的柱子
4. 不过则改 patch.json 重 `apply --overwrite`。创建型 deck 的 `vision-check`
   `high` 和 `medium` 也必须清零后才能交付；PNG 仍要人工确认没有字符重叠。

---

## §10 常见返工原因

| 现象                                | 根因                                                                |
| ----------------------------------- | ------------------------------------------------------------------- |
| KPI 渲染成 3+1 不是 4-across        | 用了 `add-slide.recipe.kind="kpi-grid"` — 手堆 4 个卡片即可         |
| 表格紧贴左上角看起来很小            | `add-table` 没显式给 `w` / `h`                                      |
| chart Q3/Q4 是 0 看起来塌方         | 时间序列别留 0 占位 — 填预测值并标 "(预测)"                         |
| 第二次 apply `output_exists`        | 加 `--overwrite`，或先 `pptx rollback --from-sidecar`               |
| `titleStyle.bold` 报错              | 移到 `font: { bold: true }` 子对象，顶层不接受                      |
| `legend: "b"` 被拒                  | 用全名 `"bottom"`，shorthand 不接受                                 |
| `dataLabels` 的 `scope: "all"` 被拒 | scope 是对象，省略 = all；要某系列写 `{ "scope": { "series": 0 } }` |
| 文字遮挡 watermark / 页脚           | 文本 textbox 区域和 watermark 重叠 — 缩 textbox 的 `w`              |
| 装饰元素挡住主标题                  | 装饰放右上 (10+, 2-4)，与 11in 主标题碰撞 — 改放右下 (10+, 5.4-6.8) |

---

## §11 装饰元素布局通用规则（dry-run 抓不到的坑）

13.333in × 7.5in 幕布上，**主标题 textbox 通常吃 11in 宽**（x≈0.95 → x≈11.95）。
装饰元素（圆形 / 圆角矩形 / 强调块）若放右上 (10+, 2-4) 区域，几乎必然与主标题
重叠 —— dry-run 看到的只是两个 shape 各自合法的 bounding box，不报告几何重叠。

### 安全区分布（封面页）

```
┌──────────────────────────────────────────┐
│ ▌ 顶部品牌条 (0-13.333, 0-0.12)           │
├──────────────────────────────────────────┤
│  ← 上半屏 (y=0.6-5.4)：主标题 + 副标 + tagline 区域 →
│  ← 装饰元素禁区 (x=10+, y=2-4) ──────────  ←
│  ← 因为主标题 11in textbox 必然覆盖此处   ←
├──────────────────────────────────────────┤
│                              ┌──┐┌──┐    │ ← 装饰安全区 (10+, 5.4-6.8)
│                              │  ││  │    │
│                              └──┘└──┘    │
├──────────────────────────────────────────┤
│  Hero strip (0-13.333, 6.95-7.5) ← 装饰也别放这，会被 strip 盖
└──────────────────────────────────────────┘
```

### 各页型的装饰安全区参考

| 页型            | 主要内容区 (避开)              | 装饰安全区                  |
| --------------- | ------------------------------ | --------------------------- |
| 封面页          | x=0.6-12, y=2.4-5.4            | 右下 (10+, 5.4-6.8)         |
| 议程页 / KPI 页 | x=0.6-12.7, y=2-7              | 左上 logo 区 (0-0.5, 0-0.5) |
| chart 页        | x=0.6-9.1 (chart) + 右 callout | 左下 / 右下角小图标         |
| hero 收尾页     | 整页 accent 背景               | 角落圆形 / 极简水印         |

### 设计原则

1. **先框 textbox 边界，再画装饰** —— 把所有 textbox 的 (x, x+w, y, y+h)
   写下来，装饰只能落在并集之外。
2. **装饰宁可小一点** —— 1.4in × 1.4in 圆角矩形比 2.3in × 2.3in 更难碰撞，
   也更精致。
3. **装饰 z-order 默认在 textbox 之下** —— 但 PPTX 顺序按 op 顺序决定，
   先 `add-shape` 再 `add-text-box` 文字在上；若反了，用 `remove-shape`
   删掉后按正确顺序重新添加。
4. **不要用纯白装饰在白底页** —— 看不见的装饰等于浪费 op。卡片底用浅色调
   （`C.cardBg` / `C.pale`），与背景拉开 ≥10% 亮度差。
5. **hero 页装饰用主色变体** —— 深底 (`primaryDk`) + 中色装饰 (`primary`)
   层次最稳。

### 文字 textbox 高度防溢出规则

dry-run 的 `text-overflow-estimate` 与 `vision-check` 复用同一套静态文本溢出估算。
按字号给最小高度，尽量在写文件前消掉 medium 风险：

| 字号 | 单行最小 h | 推荐 h | 两行推荐 h |
| ---- | ---------- | ------ | ---------- |
| 54pt | 1.0in      | 1.5in  | 2.4in      |
| 44pt | 0.85in     | 1.4in  | 2.2in      |
| 32pt | 0.6in      | 1.0in  | 1.6in      |
| 24pt | 0.45in     | 0.7in  | 1.2in      |
| 16pt | 0.3in      | 0.5in  | 0.85in     |
| 12pt | 0.25in     | 0.4in  | 0.7in      |
| 9pt  | 0.2in      | 0.3in  | 0.5in      |

中文环境因为字符高度比西文略大，按表上推荐值用即可，不必再加。

### 字号与几何底线

- 核心正文不要低于 `10.5pt`；label / badge / chart / table 不要低于 `9pt`。
- 页脚、来源、页码可以 `8.5-9pt`，但不能承载用户必须读懂的关键信息。
- 圆形编号、VS 标识、流程节点等小组件如果需要靠近屏幕看，直接返工：放大组件、删字或换版式。
- 对称布局用公式推导中心：`gapCenter = (left.x + left.w + right.x) / 2`，再放置中间标识。
- 连接线用 shape bbox 端点推导；不要用未旋转 triangle 当箭头头。

### 与生成器模板的关系

`assets/examples/generator/deck-generator-template.mjs` 里的 `slideCover` 函数已经按
"装饰右下安全区"实现，可直接复用；改主题色只动 `C` 调色板，不动布局。详见
[deck-generator-workflow.md](deck-generator-workflow.md)。
