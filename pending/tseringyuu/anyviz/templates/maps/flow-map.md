# 流向地图（Flow Map）

## 用途
- 起点到终点的流动量（如人口迁徙、贸易流向、物流网络）
- 揭示空间转移/连接模式
- 最佳流向数：10-100 条

## 数据
```json
{
  "flows": [
    {
      "from": { "id": "110000", "name": "北京", "lon": 116.4, "lat": 39.9 },
      "to": { "id": "310000", "name": "上海", "lon": 121.5, "lat": 31.2 },
      "value": 2500
    },
    {
      "from": { "id": "110000", "name": "北京", "lon": 116.4, "lat": 39.9 },
      "to": { "id": "440100", "name": "广州", "lon": 113.3, "lat": 23.1 },
      "value": 1800
    }
  ],
  "total_flow": 12000
}
```

## 参数

```json
{
  "flow_line": {
    "base_width_px": 2.0,
    "max_width_px": 12.0,
    "color": "#4269d0",
    "opacity": 0.6,
    "curve_type": "quadratic_bezier"
  },
  "flow_arrow": {
    "enabled": true,
    "arrow_size_px": 6.0,
    "threshold_width_px": 3.0
  },
  "location_node": {
    "radius_px": 5.0,
    "fill_color": "#4269d0",
    "stroke_color": "#FFFFFF",
    "stroke_width_px": 1.5
  },
  "filter": {
    "min_percentage": 0.05
  }
}
```

## 规则

- **线条宽度映射**：用平方根缩放，$width = base + (value / maxValue)^{0.5} \times (max - base)$，范围 2.0px~12.0px
- **线条颜色**：默认 #4269d0，opacity 0.6；多来源可用 categorical 色板区分
- **弧线曲率**：二次贝塞尔曲线，高度与距离成正比（$height = distance \times 0.15$）
- **方向箭头**：宽度 > 3.0px 的流向线上加 6.0px 箭头，指向终点
- **节点标注**：高流量节点（> 中位数的 1.5 倍）在旁标注城市名称，字号 10px
- **流量过滤**：隐藏低于总流量 5% 的线路，减少视觉噪音

## 变体

- **弧线地图（Arc Flow Map）**：简化为纯弧线，取消节点圆圈，强调流向轨迹本身

- **迁徙动画图（Animated Flow）**：线条沿着流向方向移动，用动画长度表示流量大小，适合演讲和探索
