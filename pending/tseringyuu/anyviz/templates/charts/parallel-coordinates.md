# 平行坐标图（Parallel Coordinates）

## 用途
- 对比多个高维数据样本在各维度上的特征
- 发现多维数据中的模式、聚类和异常值
- 高维数据探索（5-15 个维度）
- 最佳样本数：20-500 个；超过 500 个需配合过滤或聚类

## 数据
```json
{
  "dimensions": [
    { "name": "销售额", "type": "number", "min": 0, "max": 100000 },
    { "name": "市场占有率", "type": "number", "min": 0, "max": 100 },
    { "name": "客户满意度", "type": "number", "min": 0, "max": 10 },
    { "name": "地区", "type": "category", "values": ["华东", "华南", "华北"] }
  ],
  "records": [
    { "销售额": 85000, "市场占有率": 45, "客户满意度": 8.5, "地区": "华东" },
    { "销售额": 62000, "市场占有率": 32, "客户满意度": 7.2, "地区": "华南" }
  ]
}
```

## 参数

```json
{
  "parallel_coordinates": {
    "axis_line_width": 0.8,
    "axis_color": "#CCCCCC",
    "line_width": 1.2,
    "line_opacity": 0.3,
    "line_opacity_highlight": 0.8,
    "line_opacity_deemphasis": 0.1,
    "category_color": "#4269d0",
    "axis_label_font_size": 10,
    "axis_value_font_size": 9,
    "brush_highlight_color": "#a463f2",
    "brush_highlight_opacity": 0.8
  }
}
```

## 规则

- **轴的归一化与缩放**：数值型维度需归一化到 0-1 范围展示，保留原始刻度标签；分类维度按出现顺序等间距排列，垂直刻度标签文本
- **线条透明度处理**：基础线条 opacity 0.3 防止过度绘制；鼠标悬停时高亮至 0.8，其他线条降至 0.1，形成焦点对比
- **轴顺序可调**：提供交互拖拽重排轴序，帮助发现维度间的相关性或聚类模式；初始顺序按数据文件顺序
- **刷选交互（Brushing）**：支持在任一轴上拖拽选择数值范围或分类，自动高亮满足条件的多条线；支持多轴同时刷选（与逻辑）
- **标签与刻度**：轴标签字号 10px，位置在轴顶部；数值刻度标签 9px，左对齐；分类刻度文本垂直排列以节省空间
- **无障碍**：线条色盲友好配置（用 categorical 色板首色 #4269d0），关键样本可用标签注解；提供数据表切换视图，让色盲用户能获取精确数值

## 变体

- **分类平行坐标（Categorical Parallel Coordinates）**：所有维度均为分类数据，用色点或符号替代连线，强调类别间的对应关系

- **平行集合图（Parallel Sets）**：将多个平行坐标的线条按流量宽度聚合，用带状流（如桑基图风格）展示维度间的连接强度和流向
