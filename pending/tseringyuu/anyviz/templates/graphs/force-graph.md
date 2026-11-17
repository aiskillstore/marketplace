# 力导向图（Force-Directed Graph）

## 用途
- 实体间的网络关系和结构
- 社交网络、引用关系、知识图谱、人物关联
- 最佳节点数：20-500 个；超过 500 个考虑过滤或聚类
- 无明显层次的互相连接的数据

## 数据
```json
{
  "nodes": [
    { "id": "1", "name": "节点A", "group": 1, "value": 25 },
    { "id": "2", "name": "节点B", "group": 2, "value": 15 },
    { "id": "3", "name": "节点C", "group": 1, "value": 20 }
  ],
  "links": [
    { "source": "1", "target": "2", "value": 5 },
    { "source": "1", "target": "3", "value": 8 }
  ]
}
```

## 参数

```json
{
  "force_graph": {
    "node_size_range": [6, 24],
    "node_stroke_width": 2.0,
    "node_stroke_color": "#FFFFFF",
    "link_width_px": 0.8,
    "link_color": "#CCCCCC",
    "link_opacity": 0.5,
    "link_opacity_highlight": 0.8,
    "link_opacity_deemphasis": 0.2,
    "hover_highlight_opacity": 0.9,
    "force_link_distance": 60,
    "force_charge_strength": -300,
    "label_font_size": 10,
    "label_color": "#555555",
    "label_offset": 8
  }
}
```

## 规则

- **节点大小**：按 value 字段映射直径 6-24px；无 value 时按 degree（连接数）映射，范围 8-18px
- **节点颜色**：按 group 用 categorical 色板（首色 #4269d0、第二色 #3ca951 等）；节点描边 #FFFFFF, 2.0px
- **连线**：基础灰色 #CCCCCC, 0.8px, opacity 0.5；悬停高亮至 opacity 0.8，反链接降至 opacity 0.2
- **布局参数**：link_distance 60px 控制连接松紧度；charge_strength -300 控制节点斥力（节点数越多斥力越强）
- **交互**：支持拖拽单个节点、缩放全图、悬停高亮相邻节点及相连边；标签字号 10px，颜色 #555555，与节点距离 8px
- **无障碍**：颜色+节点标签冗余编码，确保色盲用户可读；连接数高的关键节点可加粗边框或图标区分

## 变体

- **弧形图（Arc Diagram）**：按线性排列节点，用圆弧连接，适合展示单一方向的关系链或时间序列关系

- **邻接矩阵（Adjacency Matrix）**：网格状排列显示节点对之间的连接强度，适合稠密网络或需精确对比的场景

- **径向图（Radial Layout）**：以中心节点为圆心放射状排列，强调中心节点的重要性和外层节点的层级关系
