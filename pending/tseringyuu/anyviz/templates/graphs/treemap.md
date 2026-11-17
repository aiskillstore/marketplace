# 树图（Treemap）

## 用途
- 层次化数据的比例关系和占用空间
- 磁盘空间分析、预算分配、市场份额分布、文件系统可视化
- 最佳叶子节点数：20-100 个；超过 200 个考虑分页或过滤
- 最多层级：2-3 层；过深时考虑用旭日图或分页展示

## 数据
```json
{
  "children": [
    {
      "name": "分类A",
      "value": 300,
      "children": [
        { "name": "项目A1", "value": 120 },
        { "name": "项目A2", "value": 180 }
      ]
    },
    {
      "name": "分类B",
      "value": 250,
      "children": [
        { "name": "项目B1", "value": 250 }
      ]
    }
  ]
}
```

## 参数

```json
{
  "treemap": {
    "layout_algorithm": "squarified",
    "rect_border_color": "#FFFFFF",
    "rect_border_width": 1.5,
    "rect_fill_opacity": 0.85,
    "parent_label_font_size": 11,
    "leaf_label_font_size": 10,
    "label_color": "#FFFFFF",
    "label_color_dark_bg": "#1A1A1A",
    "label_contrast_threshold": 0.5,
    "inner_padding": 6,
    "outer_padding": 8
  }
}
```

## 规则

- **矩形颜色**：第一层按分类用 categorical 色板首颜色（#4269d0、#3ca951、#ff725c 等）；嵌套子级用同色相的不同亮度或透明度，fill_opacity 0.85
- **边框**：白色 #FFFFFF, 1.5px，区分相邻矩形；内层间距 6px，最外层间距 8px
- **标签**：
   - 顶层分类标签：11px，颜色 #FFFFFF（高对比）或 #1A1A1A（面积足够时）
   - 叶子节点标签：10px，显示名称 + 数值；面积小于 800px² 时仅显示百分比或省略
   - 用对比度阈值 0.5 动态判断文字颜色
- **布局**：Squarified Treemap 算法，优先保持矩形接近正方形，从左上到右下逐行排列，提高标签可读性
- **排序**：按面积降序排列，确保大矩形靠近左上角，小矩形紧凑在角落
- **无障碍**：矩形颜色+数值标签冗余编码，色盲用户可通过数值和邻近关系判断比例；建议提供数据表格补充

## 变体

- **旭日图（Sunburst）**：圆形分层树图，每层为一个圆环，中心为根节点，适合多层级且数据量大的场景

- **圆形填充图（Circle Packing）**：用大小不同的圆代替矩形，相同父级的圆紧凑堆放，视觉效果更柔和

- **冰柱图（Icicle）**：垂直堆叠的树图，每层为一条水平条带，从上到下依次为层级关系，适合展示时间序列或顺序层次
