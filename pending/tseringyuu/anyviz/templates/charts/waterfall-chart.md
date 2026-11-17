# 瀑布图（Waterfall Chart）

## 用途
- 从初始值到最终值的逐步变化过程
- 财务分析：收入、中间成本、利润分解
- 多个增量/减量对总值的累积影响
- 最佳步骤数：4-12 步

## 数据
```json
{
  "categories": ["期初余额", "销售收入", "成本支出", "税费扣除", "期末余额"],
  "values": [1000, 800, -300, -150, 1350],
  "is_total": [true, false, false, false, true]
}
```

## 参数

```json
{
  "waterfall": {
    "bar_width_ratio": 0.6,
    "bar_corner_radius_px": 5,
    "connector_line_width_px": 1.0,
    "connector_line_color": "#CCCCCC",
    "connector_line_dash": [2, 2],
    "increase_color": "#3ca951",
    "decrease_color": "#ff725c",
    "total_color": "#4269d0",
    "neutral_color": "#9696a0",
    "bar_fill_opacity": 0.85,
    "label_offset_px": 6
  }
}
```

## 规则

- **颜色语义**：增长柱用 #3ca951，减少柱用 #ff725c，总计/起始柱用 #4269d0，中间过渡柱用 #9696a0，opacity 0.85
- **起始与总计标记**：第一柱（起始值）和最后一柱（总计）用 #4269d0，其余按增减变化着色，易于追踪资金流向
- **连接线设计**：柱体间用浅灰虚线连接（#CCCCCC，线宽 1.0px，虚线 [2,2]），标高显示累积值
- **数值标签**：每柱上方显示绝对值；增减柱旁显示 ±变化量；总计柱显示最终结果，标签距柱顶 6px
- **无障碍冗余**：仅靠颜色区分增减不够，设计要点中必须用 ↑↓ 箭头或显式标签标注变化方向，色盲用户也能读懂
- **水平对齐**：所有柱体基线对齐（可用堆叠的起始位置表示），不用悬浮柱（floating bar）容易误导读者

## 变体

- **堆叠瀑布图（Stacked Waterfall）**：每个步骤细分为多个子成分，用堆叠柱体展示，适合展示成本分类（直接成本、间接成本、其他）对利润的影响

- **水平瀑布图（Horizontal Waterfall）**：柱体改为横向条形，便于展示较长的类别标签或移动设备展示

- **双向瀑布图（Diverging Waterfall）**：从中间基准线向两侧延伸，增长向上，减少向下，更直观地展示正负变化
