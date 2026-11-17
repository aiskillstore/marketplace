# 弦图（Chord Diagram）

## 用途
- 实体之间的双向关系和交互强度
- 贸易往来、跨部门协作、引用关系、人物互动网络
- 最佳实体数：5-20 个；超过 20 个视觉混乱度上升
- 适合关系矩阵对称或接近对称的数据

## 数据
```json
{
  "nodes": [
    { "id": "A", "name": "部门A", "group": 1 },
    { "id": "B", "name": "部门B", "group": 2 },
    { "id": "C", "name": "部门C", "group": 2 }
  ],
  "links": [
    { "source": "A", "target": "B", "value": 45 },
    { "source": "B", "target": "A", "value": 38 },
    { "source": "B", "target": "C", "value": 28 }
  ]
}
```

## 参数

```json
{
  "chord": {
    "arc_width_px": 25,
    "arc_fill_opacity": 0.85,
    "chord_opacity": 0.35,
    "chord_opacity_highlight": 0.7,
    "chord_opacity_deemphasis": 0.1,
    "chord_stroke_width": 0,
    "label_font_size": 10,
    "label_color": "#333333",
    "label_radius_offset": 15,
    "arc_separator_gap": 3
  }
}
```

## 规则

- **弧段颜色**：按 group 用 categorical 色板（#4269d0、#3ca951、#ff725c 等），填充 opacity 0.85；弧段之间 3px 分离间隔增强可读性
- **弧段宽度**：固定 25px；弧段弧长与该实体总流量（出入度和）成正比
- **弦颜色**：继承源弧段的颜色，opacity 0.35；悬停高亮至 0.7，无关弦降至 0.1
- **弦宽度**：与流量（link value）成正比；无描边（stroke_width 0）
- **标签**：实体名称标注在弧段外侧 15px，字号 10px，颜色 #333333；考虑旋转适应圆周方向
- **无障碍**：弧段颜色+流量数值冗余编码；弦宽度视觉递减难区分时，建议数据提示或交互高亮关键关系

## 变体

- **有向弦图（Directed Chord）**：弦带有方向指示（箭头或渐变），用于展示有明确流向的双向关系（如商品进出口）

- **分层弦图（Hierarchical Chord）**：加入第二层级分类，内外两圈弦，展示更复杂的多维关系结构
