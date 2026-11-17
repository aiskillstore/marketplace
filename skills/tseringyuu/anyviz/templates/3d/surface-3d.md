# 3D 曲面图（3D Surface Plot）

## 用途
- 双变量函数 z = f(x, y) 的曲面形态
- 科学计算、工程模拟结果、响应面分析
- 最佳数据点：网格 20×20 到 100×100

## 数据

**方式一：网格数据（推荐）**
```json
{
  "grid": {
    "x": [0, 1, 2, 3, 4],
    "y": [0, 1, 2, 3, 4],
    "z": [
      [1, 2, 3, 4, 5],
      [2, 4, 5, 6, 7],
      [3, 5, 7, 8, 9],
      [4, 6, 8, 10, 11],
      [5, 7, 9, 11, 13]
    ]
  },
  "x_label": "变量 X",
  "y_label": "变量 Y",
  "z_label": "响应值 Z"
}
```

**方式二：散点数据**
```json
{
  "points": [
    { "x": 0, "y": 0, "z": 1 },
    { "x": 1, "y": 0, "z": 2 },
    { "x": 0, "y": 1, "z": 2 }
  ]
}
```

## 参数

```json
{
  "surface": {
    "color_palette": "Viridis",
    "wireframe_enabled": true,
    "wireframe_color": "#CCCCCC",
    "wireframe_width_px": 0.5,
    "opacity": 0.9
  },
  "light": {
    "ambient": { "intensity": 0.4 },
    "directional": {
      "intensity": 0.8,
      "elevation_deg": 45,
      "azimuth_deg": 45
    }
  },
  "camera": {
    "elevation_angle_deg": 30,
    "azimuth_angle_deg": -60,
    "z_scale_factor": 1.0
  },
  "axis": {
    "grid_color": "#E8E8E8",
    "grid_width_px": 0.5,
    "label_font_size_px": 10,
    "color": "#CCCCCC"
  }
}
```

## 规则

- **色板映射**：Viridis 多色相色板，Z 值从最小（暗紫 #440154）到最大（亮黄 #FDE725），色盲友好
- **光照模型**：
   - 环境光强度 0.4（基础照亮）
   - 方向光强度 0.8，仰角 45°、方位角 45°（左上角照射），创造立体感
- **曲面网格**：灰色 #CCCCCC，0.5px 线条，帮助感知曲面弯曲趋势
- **视角参数**：仰角 30°，方位角 -60°（等距视角），Z 轴缩放 1.0×；支持交互旋转调整
- **坐标轴范围**：自动归一化或按用户指定范围；刻度标签字号 10px，距离轴 8px
- **交互功能**：支持旋转、缩放、平移；静态导出时选择信息量最大的视角（通常仰角 20-40°）

## 变体

- **3D 等高线图（3D Contour）**：曲面顶视投影为等高线，结合侧视图高度条形，减少 3D 渲染复杂度

- **线框图（Wireframe）**：取消曲面填充，仅显示网格线条，强调几何结构和奇点
