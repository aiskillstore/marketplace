# 3D 散点图（3D Scatter Plot）

## 用途
- 三个连续数值变量之间的关系
- 聚类分析（用颜色表示第 4 维—分类或连续值）
- 最佳数据点：100-5,000 个

## 数据
```json
{
  "points": [
    { "x": 2.5, "y": 3.1, "z": 4.2, "category": "A", "size": 10 },
    { "x": 3.2, "y": 2.8, "z": 5.1, "category": "B", "size": 12 },
    { "x": 1.9, "y": 4.5, "z": 3.8, "category": "A", "size": 9 }
  ],
  "x_label": "特征1",
  "y_label": "特征2",
  "z_label": "特征3",
  "category_list": ["A", "B", "C"]
}
```

## 参数

```json
{
  "point": {
    "shape": "sphere",
    "radius_px": 4.5,
    "opacity": 0.75,
    "stroke_width_px": 1.5,
    "stroke_color": "#FFFFFF"
  },
  "color": {
    "by_category": "categorical",
    "by_continuous": "Viridis"
  },
  "projection": {
    "enabled": true,
    "shadow_opacity": 0.2,
    "planes": ["xy", "xz", "yz"]
  },
  "camera": {
    "type": "perspective",
    "elevation_angle_deg": 30,
    "azimuth_angle_deg": -60,
    "fov_deg": 45
  },
  "axis": {
    "color": "#CCCCCC",
    "width_px": 0.8,
    "label_font_size_px": 10
  }
}
```

## 规则

- **点样式**：球体，半径 4.5px，opacity 0.75，白色 1.5px 描边，增强空间感
- **颜色编码**：
   - 分类分组：categorical 色板（首色 #4269d0）
   - 连续值：Viridis 多色相色板，色盲友好
- **投影和深度**：可选三个正交平面投影（xy/xz/yz，opacity 0.2 阴影），帮助理解 3D 位置
- **默认视角**：仰角 30°，方位角 -60°（等距透视），适合多数场景；支持交互旋转和缩放
- **坐标轴**：灰色 0.5px 线条，标签字号 10px；刻度标签同步旋转以保持可读性
- **性能优化**：超过 2000 个点时启用点聚集或抽样，防止过度渲染

## 变体

- **3D 气泡图（3D Bubble）**：点的大小表示第 5 维数据，结合颜色可同时编码 6 个变量

- **带投影散点图（Projected Scatter）**：简化投影为单个平面（如 xy 平面），配合高度差异突出聚类
