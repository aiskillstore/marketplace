# 旭日图（Sunburst Chart）

## 用途
- 层次结构的多级嵌套比例关系
- 从中心向外表示从总体到细节的分解过程
- 支持点击下钻交互，逐层探索数据
- 最佳层级数：2-4 级；最佳叶子节点数：30-100 个

## 数据
```json
{
  "name": "全公司销售",
  "value": 500000,
  "children": [
    {
      "name": "华东",
      "value": 200000,
      "children": [
        { "name": "上海", "value": 120000 },
        { "name": "浙江", "value": 80000 }
      ]
    },
    {
      "name": "华南",
      "value": 150000,
      "children": [
        { "name": "广东", "value": 100000 },
        { "name": "福建", "value": 50000 }
      ]
    },
    {
      "name": "华北",
      "value": 150000,
      "children": [
        { "name": "北京", "value": 90000 },
        { "name": "天津", "value": 60000 }
      ]
    }
  ]
}
```

## 参数

```json
{
  "sunburst": {
    "inner_radius_ratio": 0.3,
    "outer_radius_ratio": 0.95,
    "center_label_font_size": 12,
    "level_label_font_size": 10,
    "level_label_color": "#FFFFFF",
    "stroke_width": 2.0,
    "stroke_color": "#FFFFFF",
    "opacity": 0.85,
    "highlight_opacity": 1.0,
    "deemphasis_opacity": 0.3,
    "transition_duration_ms": 500,
    "color_saturation_by_level": true
  }
}
```

## 规则

- **环形尺度与角度映射**：最内环半径占画布 30%，最外环 95%；每个扇形的角度与其数值占比成正比（占比 = value / parent_value × 360°），确保面积感知准确
- **色彩层级分配**：第一层用 categorical 色板首色 #4269d0；同层级兄弟节点用同色相的不同亮度（亮度由 sequential Blues 色板梯度表示）；子层级对比前一层降低饱和度 10-15%
- **标签与可读性**：外环标签显示在扇形中心，字号 10px，文本色 #FFFFFF 确保在色彩背景上清晰；内环标签可选，字号 8px；中心显示当前选中节点的名称和占比百分比，字号 12px
- **描边与分割**：所有扇形间用 #FFFFFF 2.0px 描边分割，opacity 0.85 降低过度绘制感；悬停高亮选中扇形及其祖先路径至根节点，高亮 opacity 1.0，其他降至 0.3
- **点击下钻交互**：单击扇形进入该层级（中心向外重新布局）；返回按钮或单击中心区域返回上一层；动画过渡时长 500ms，流畅展现层级变化
- **无障碍**：色盲用户可通过纹理/条纹区分同层级节点；提供数据表视图切换；标签+百分比信息完整传达，不依赖纯颜色识别

## 变体

- **冰柱图（Icicle Chart）**：垂直方向的层级展示，每层为水平条形，宽度与数值成正比；适合强调层级关系而非圆形美学

- **嵌套环形图（Nested Ring Chart）**：多个同心环表示不同分类维度，每个环的弧段颜色按分类着色；适合展示多个层级的分类统计
