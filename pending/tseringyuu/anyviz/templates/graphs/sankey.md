# 桑基图（Sankey Diagram）

## 用途
- 流量、能量、资金、用户在多阶段的流动和转化
- 漏斗分析、客户旅程追踪、预算分配追溯
- 阶段数：2-6 个；每阶段节点数 3-20 个为佳
- 最佳链接数：50-500 条（过多时考虑过滤或分组）

## 数据
```json
{
  "nodes": [
    { "id": "A0", "name": "来源", "stage": 0 },
    { "id": "B1", "name": "中间环节1", "stage": 1 },
    { "id": "C2", "name": "目标", "stage": 2 }
  ],
  "links": [
    { "source": "A0", "target": "B1", "value": 120 },
    { "source": "B1", "target": "C2", "value": 95 }
  ]
}
```

## 参数

```json
{
  "sankey": {
    "node_width_px": 15,
    "node_padding_y": 12,
    "node_fill_color": "categorical",
    "node_opacity": 0.85,
    "link_opacity": 0.45,
    "link_opacity_highlight": 0.75,
    "link_opacity_deemphasis": 0.15,
    "link_stroke_width": 0,
    "label_font_size": 10,
    "label_color": "#333333",
    "label_offset_x": 6,
    "stage_gap_x": 80
  }
}
```

## 规则

- **节点颜色**：按 stage 用 categorical 色板首颜色（第一阶段 #4269d0、第二阶段 #3ca951 等）；节点填充 opacity 0.85
- **连线颜色**：继承源节点的颜色，opacity 0.45；悬停高亮至 0.75，无关连线降至 0.15，确保流向清晰
- **节点宽度**：固定 15px；节点高度与通过该节点的总流量成正比；节点间纵向间距 12px
- **连线宽度**：与流量（link value）成正比；无描边（stroke_width 0）减少视觉混乱
- **标签**：节点名称 + 总量（单位可选）标注在节点右侧 6px，字号 10px，颜色 #333333；各阶段之间横向间隔 80px
- **无障碍**：节点颜色+流量数值冗余编码，色盲用户可通过数值和节点位置判断流向；建议为关键流向或异常值添加数据标签

## 变体

- **冲积图（Alluvial Diagram）**：时间维度的桑基图，每列代表一个时间点，用于展示群体随时间的流动变化

- **漏斗图（Funnel）**：简化的桑基图，仅有单一流向，每阶段单一节点，强调转化率的逐级递减
