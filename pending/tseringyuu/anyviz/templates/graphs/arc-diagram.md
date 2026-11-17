# 弧形图（Arc Diagram）

## 用途
- 一维线性布局中的网络关系
- 网络节点沿水平或垂直轴排列，弧形表示连接
- 时序关系、引用网络、配对关系
- 弧形高度或颜色代表连接强度
- 最佳节点数：20-200 个；边数：30-500 条

## 数据
```json
{
  "nodes": [
    { "id": "1", "name": "文章A", "year": 2020 },
    { "id": "2", "name": "文章B", "year": 2021 },
    { "id": "3", "name": "文章C", "year": 2022 },
    { "id": "4", "name": "文章D", "year": 2023 }
  ],
  "links": [
    { "source": "1", "target": "2", "value": 5 },
    { "source": "1", "target": "3", "value": 8 },
    { "source": "2", "target": "4", "value": 3 }
  ]
}
```

## 参数

```json
{
  "arc_diagram": {
    "node_radius": 4.5,
    "node_stroke_width": 2.0,
    "node_stroke_color": "#FFFFFF",
    "node_color": "#4269d0",
    "arc_width_min": 0.5,
    "arc_width_max": 3.0,
    "arc_color": "#CCCCCC",
    "arc_opacity": 0.4,
    "arc_opacity_highlight": 0.8,
    "arc_opacity_deemphasis": 0.1,
    "node_spacing": 30,
    "arc_height_ratio": 0.5,
    "label_font_size": 10,
    "label_offset": 8,
    "transition_duration_ms": 300
  }
}
```

## 规则

- **节点线性排列**：节点沿水平轴均匀分布，间距 30px；节点圆形，半径 4.5px，颜色 #4269d0，#FFFFFF 描边 2.0px；节点可按自然顺序（如时间）或按度数（连接数）排序
- **弧形绘制与权重**：连接用平滑贝塞尔曲线弧形表示，弧高与两节点距离成正比，最高不超过节点间距 50%；弧宽映射连接强度（value），范围 0.5-3.0px；基础 opacity 0.4 避免拥挤
- **弧形颜色**：可按源到目标渐变、按权重加深，或统一 `#CCCCCC`；同源/同类同色
- **交互与高亮**：鼠标悬停节点时，高亮该节点及其所有相邻边，相邻边 opacity 升至 0.8；其他边降至 0.1；悬停弧形时高亮源目标节点和该条边；支持点击筛选特定节点的关系
- **标签与可读性**：节点标签字号 10px，位置在节点上方（水平布局）或右侧（垂直布局），距离 8px；长标签可自动截断或水平翻转以优化排版；关键节点可加粗标签或图标突出
- **无障碍**：节点形状（圆点）+ 标签完整编码，确保色盲用户无需色彩识别；高权重弧线用加粗替代颜色深浅的强弱对比；提供排序或聚类选项，帮助用户快速定位关键连接

## 变体

- **双向弧形图（Bidirectional Arc Diagram）**：节点分列于轴的上下两侧，弧形连接上下两侧节点，适合展示二部图或来源-目标关系（如引用、流转）

- **分组弧形图（Grouped Arc Diagram）**：节点按类别分组布置，同组节点靠近，组与组之间分离；弧形按来源组和目标组着色，强调组间关系
