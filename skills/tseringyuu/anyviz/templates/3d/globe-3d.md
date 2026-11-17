# 3D 地球（3D Globe）

## 用途
- 全球范围的数据展示（如气候变化、航线网络、出口贸易）
- 需展示球面几何的场景（地震分布、卫星轨道）
- 最佳数据点：10-500 个

## 数据

**方式一：区域聚合**
```json
{
  "regions": [
    { "id": "CHN", "name": "中国", "lon": 105, "lat": 35, "value": 98000 },
    { "id": "USA", "name": "美国", "lon": -95, "lat": 37, "value": 87500 },
    { "id": "IND", "name": "印度", "lon": 78, "lat": 20, "value": 45000 }
  ],
  "color_palette": "Viridis"
}
```

**方式二：航线网络**
```json
{
  "routes": [
    {
      "from": { "lon": 116.4, "lat": 39.9, "name": "北京" },
      "to": { "lon": 2.4, "lat": 48.9, "name": "巴黎" },
      "value": 250
    }
  ],
  "line_color": "#4269d0",
  "line_opacity": 0.6
}
```

## 参数

```json
{
  "globe": {
    "texture": "natural",
    "ocean_color": "#1a4d8f",
    "land_color": "#5a9d6f",
    "atmosphere_enabled": true,
    "atmosphere_color": "#87CEEB",
    "atmosphere_opacity": 0.15
  },
  "data_layer": {
    "marker_type": "bar",
    "marker_color": "Viridis",
    "bar_height_scale": 1.0,
    "marker_opacity": 0.85
  },
  "light": {
    "ambient_intensity": 0.4,
    "directional_intensity": 0.8,
    "direction": { "x": 1, "y": 1, "z": 1 }
  },
  "rotation": {
    "auto_rotate": true,
    "auto_rotate_speed_rpm": 0.5,
    "enable_interactive": true
  },
  "axis": {
    "graticule_enabled": true,
    "graticule_color": "#CCCCCC",
    "graticule_width_px": 0.3
  }
}
```

## 规则

- **地球纹理**：
   - 自然风格：蓝色海洋 #1a4d8f + 绿色陆地 #5a9d6f
   - 简约风格：浅灰 #F0F0F0（黑白地图）
   - 可选淡蓝色大气光晕，opacity 0.15，增强立体感
- **数据标记**：
   - 柱状图模式：高度 = 数值，色板 Viridis（色盲友好），opacity 0.85
   - 颜色填充：区域按数值着色，连续渐变
   - 点标记：简化为小圆点 3.0px，用于网络节点
- **光照**：环境光强度 0.4（基础照亮）+ 方向光强度 0.8（方向 1, 1, 1），模拟太阳照射，创造昼夜对比
- **旋转与交互**：默认缓慢自动旋转（0.5 rpm），支持鼠标拖拽旋转、滚轮缩放、双指触摸操作
- **网格与参考线**：可选经纬线网格（灰色 #CCCCCC，0.3px），帮助识别地理位置
- **航线弧图**：连接线用贝塞尔曲线，#4269d0 opacity 0.6，宽度与流量成比例；弧线高度 = 两地距离×0.2

## 变体

- **航线弧图地球（Great Circle Arc Globe）**：仅显示弧线连接和节点，突出空间流向，适合展示国际贸易、航班网络

- **扁平等距投影（Equirectangular Projection）**：保留地球概念但展开为平面矩形图，减少透视失真，适合数据标注密集的场景
