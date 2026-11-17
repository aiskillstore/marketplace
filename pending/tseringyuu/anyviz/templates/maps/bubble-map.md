# 气泡地图（Bubble Map）

## 用途
- 离散地理位置上的数值（如城市销售额、门店客流量）
- 城市级别或多地点的数据对比
- 最佳数据点：15-100 个

## 数据
```json
{
  "points": [
    { "id": "BJ", "name": "北京", "lon": 116.4, "lat": 39.9, "value": 45000, "category": "一线城市" },
    { "id": "SH", "name": "上海", "lon": 121.5, "lat": 31.2, "value": 52000, "category": "一线城市" },
    { "id": "CS", "name": "长沙", "lon": 112.9, "lat": 28.2, "value": 8500, "category": "二线城市" }
  ],
  "value_range": { "min": 1000, "max": 52000 },
  "categories": ["一线城市", "二线城市"]
}
```

## 参数

```json
{
  "bubble": {
    "size_scale": "sqrt",
    "min_radius_px": 6.0,
    "max_radius_px": 40.0,
    "opacity_single": 0.7,
    "opacity_multi": 0.65,
    "stroke_color": "#FFFFFF",
    "stroke_width_px": 1.5
  },
  "color": {
    "single_category": "#4269d0",
    "multi_category_palette": "categorical"
  },
  "basemap": {
    "background_color": "#F0F0F0",
    "border_color": "#D0D0D0",
    "border_width_px": 0.8
  },
  "label": {
    "show_high_value_labels": true,
    "threshold_percentile": 0.75,
    "font_size_px": 10,
    "color": "#1A1A1A"
  }
}
```

## 规则

- **气泡大小映射**：用平方根缩放（面积 ∝ value），范围 6.0px~40.0px；避免用面积比例造成的视觉膨胀
- **气泡颜色**：
   - 单色：#4269d0, opacity 0.7
   - 多类别：按 categorical 色板 (#4269d0 #3ca951 #ff725c ...)
- **底图设计**：浅灰 #F0F0F0 背景 + 浅色边界 #D0D0D0（0.8px），不抢夺数据视觉权重
- **重叠处理**：绘制顺序按气泡大小升序，小气泡在上，确保高值气泡可见
- **数据标注**：前 25% 高值气泡（百分位 75）旁标注城市名称，字号 10px，距离气泡 8px
- **颜色无障碍**：多类别时附加图例和色盲提示（配合形状或纹理区分）

## 变体

- **符号地图（Symbol Map）**：气泡改为方形/菱形/三角形等几何符号，适合强调类别而非连续值

- **分级符号地图（Graduated Symbol）**：结合符号类型和大小表示两个分类变量，形成二维编码

- **点密度图（Dot Density Map）**：将数值转换为点群，每个点代表固定数量（如 100 个用户），适合展示空间分布密度
