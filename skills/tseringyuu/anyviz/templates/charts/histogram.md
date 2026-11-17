# 直方图（Histogram）

## 用途
- 单个数值变量的分布形态
- 识别数据的偏度、峰度、多峰等特征
- 检测数据的正态性和异常分布
- 最佳数据点：100-100,000；箱数：Sturges 公式或 Freedman-Diaconis 规则

## 数据
```json
{
  "values": [45, 52, 48, 55, 50, 62, 58, 60, 49, 95, 51, 54, 57, 61, 59],
  "bins": 10,
  "bin_method": "sturges"
}
```

## 参数

```json
{
  "histogram": {
    "bar_fill_color": "#4269d0",
    "bar_fill_opacity": 0.8,
    "bar_stroke_width_px": 0.5,
    "bar_stroke_color": "#FFFFFF",
    "density_line_width_px": 1.5,
    "density_line_color": "#ff725c",
    "density_line_opacity": 0.7
  }
}
```

## 规则

- **箱数选择**：默认 Sturges 公式 k = ⌈log₂(n) + 1⌉；数据点 > 10,000 用 Freedman-Diaconis 规则避免过度合并
- **柱体颜色与边界**：填充色 #4269d0，opacity 0.8；白色细边框 0.5px 分隔各箱，增强可读性
- **X 轴连续性**：所有箱等宽且相邻无间隙，强调值的连续性（不同于分类柱状图）
- **密度曲线**：可选叠加核密度估计曲线（#ff725c，线宽 1.5px，opacity 0.7），帮助识别分布形态
- **Y 轴标签**：显示频数或频率（百分比），清晰标注 Y 轴含义以避免混淆
- **无障碍**：仅用颜色区分填充与曲线不足，应在图例明确标注「直方图」与「密度曲线」，若有多组需用虚线区分

## 变体

- **密度直方图（Density Histogram）**：Y 轴改为密度而非频数，面积积分为 1，便于与概率论结合

- **双变量直方图（2D Histogram / Heatmap Histogram）**：两个数值变量的联合分布，用二维箱体与颜色深度表示密度，类似于热力图

- **金字塔直方图（Population Pyramid）**：两组数据相对排列，一组向左一组向右，常用于人口统计按年龄段和性别展示
