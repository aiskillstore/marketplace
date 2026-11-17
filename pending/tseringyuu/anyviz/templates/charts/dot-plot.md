# 点图（Dot Plot / Cleveland Plot）

## 用途
- 精确对比多个类别的数值，类别间无天然顺序
- 替代柱状图，突出数值而非柱体面积（尤其数值范围跨越零）
- 排名变化或两个时间点的对比（哑铃图）
- 最佳类别数：5-30 个

## 数据
```json
{
  "categories": ["城市 A", "城市 B", "城市 C", "城市 D"],
  "values": [42, 38, 55, 31],
  "sort_order": "descending"
}
```

## 参数

```json
{
  "dot": {
    "point_radius_px": 4.5,
    "point_opacity": 0.8,
    "point_stroke_width_px": 2.0,
    "point_stroke_color": "#FFFFFF",
    "connector_line_width_px": 1.2,
    "connector_line_color": "#CCCCCC"
  },
  "axis": {
    "x_axis": { "include_zero": false },
    "y_axis": { "label_alignment": "right" }
  }
}
```

## 规则

- **排序与连接线**：类别应按数值降序排列，每个类别名称左对齐，从名称右侧引出 1.2px 灰色连接线 (#CCCCCC) 到点
- **点的设计**：点半径 4.5px，opacity 0.8，#FFFFFF 2.0px 描边，指向准确数值；点颜色可用 #4269d0 或按分组/阶段分配 categorical 色
- **X 轴起点**：数据非负时不必从零开始，但应有参考线标注起点和可用的关键位置（如均值）
- **数据标签**：直接在点右侧显示精确数值（10px 字体），或在悬停时展示
- **高亮与强调**：需突出的类别用 #a463f2 高亮，对比类别用 #ff725c；其他用 #4269d0
- **无障碍**：若按正负值分组，除颜色外用虚实线区分（正值实线、负值虚线），点形状可变（上三角/下三角）

## 变体

- **哑铃图（Dumbbell Plot）**：两个时间点或方案对比，用连接线和两端圆点展示变化方向和大小；连接线可用 #3ca951（增长）或 #ff725c（下降）

- **误差点图（Error Dot Plot）**：在中心点两侧显示误差范围（置信区间），用竖线表示区间，突出不确定性

- **棒棒糖图（Lollipop Plot）**：用连接线和末端点替代柱体，简化视觉，常与排序结合用于排名展示
