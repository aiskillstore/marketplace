# 树形图（Dendrogram）

## 用途
- 树状层次结构和聚类关系
- 表现节点之间的包含关系或分类体系
- 系统发育树、组织结构、文件树展示
- 支持水平、垂直、径向三种布局
- 最佳节点数：20-500 个

## 数据
```json
{
  "name": "A公司",
  "value": 1000,
  "children": [
    {
      "name": "销售部",
      "value": 500,
      "children": [
        { "name": "华东团队", "value": 300 },
        { "name": "华南团队", "value": 200 }
      ]
    },
    {
      "name": "技术部",
      "value": 400,
      "children": [
        { "name": "后端组", "value": 250 },
        { "name": "前端组", "value": 150 }
      ]
    },
    {
      "name": "运营部",
      "value": 100
    }
  ]
}
```

## 参数

```json
{
  "dendrogram": {
    "link_width": 1.5,
    "link_color": "#CCCCCC",
    "link_opacity": 0.6,
    "node_radius": 4.0,
    "node_stroke_width": 1.5,
    "node_stroke_color": "#FFFFFF",
    "node_opacity": 0.8,
    "leaf_color": "#4269d0",
    "internal_node_color": "#9696a0",
    "node_label_font_size": 10,
    "node_label_offset": 6,
    "layout": "horizontal",
    "vertical_spacing": 40,
    "horizontal_spacing": 80,
    "transition_duration_ms": 300
  }
}
```

## 规则

- **节点和连线样式**：内部节点（有子节点）用圆形，半径 4.0px，颜色 #9696a0；叶子节点（无子节点）用 #4269d0，半径稍大 4.5px；所有节点描边 #FFFFFF 1.5px，opacity 0.8
- **连接线绘制**：连线宽度 1.5px，颜色 #CCCCCC，opacity 0.6；连线用弧形（贝塞尔曲线）或直线（可配置），提高视觉连贯性；聚类高度用 Y 轴（垂直布局）或 X 轴（水平布局）表示距离
- **三种布局选项**：
   - 水平布局（Horizontal）：根节点在左，子树向右展开；叶子对齐右边界；Y 轴间距 40px
   - 垂直布局（Vertical）：根节点在上，子树向下展开；叶子对齐下边界；X 轴间距 80px
   - 径向布局（Radial）：根节点在中心，子树放射状展开；层级深度映射到径向距离
- **标签与悬停**：节点标签字号 10px，颜色 #555555，位置在节点右侧（水平）或下侧（垂直），距离 6px；悬停时高亮节点及其所有后代，降低其他分支 opacity 至 0.2，帮助聚焦子树
- **聚类高度标记**：可选添加参考线或注解标示关键高度阈值（如距离 0.5、1.0 处），辅助理解聚类划分；参考线用虚线 [4,4], opacity 0.5
- **无障碍**：节点色编码（内部/叶子）+ 形状冗余（圆点标记位置）；提供数据表或列表视图，展示节点名称和聚类关系；悬停时显示完整路径信息

## 变体

- **径向树（Radial Dendrogram）**：以中心点为根，子节点按角度均匀分布放射状排列，适合展示对称或高分枝因子的结构

- **矩形树（Rectangular Tree）**：用矩形表示节点，子节点在父节点内排列；常用于文件系统或组织结构展示，强调包含关系
