# Mapbox GL JS 适配器

## 用途
- 交互 Web 地图、自定义底图、大规模矢量瓦片。

## 映射

### 底图样式
```javascript
// 浅色主题（适合数据叠加）
map.setStyle('mapbox://styles/mapbox/light-v11');

// 或自定义浅色底图
const customStyle = {
  version: 8,
  sources: { /* ... */ },
  layers: [
    // 陆地：浅灰 #F5F5F5
    // 水域：浅蓝 #E8F4FD
    // 道路：不显示或极浅
  ]
};
```

### 色板适配
```javascript
// Choropleth: 使用 sequential Blues
const stops = [
  [minValue, '#F7FBFF'],
  [medianValue, '#6BAED6'],
  [maxValue, '#08306B']
];

map.addLayer({
  id: 'choropleth-fill',
  type: 'fill',
  paint: {
    'fill-color': [
      'interpolate', ['linear'],
      ['get', 'value'],
      ...stops.flat()
    ],
    'fill-opacity': 0.8,
    'fill-outline-color': '#FFFFFF'  // 边界白色分隔
  }
});
```

### 气泡地图
```javascript
map.addLayer({
  id: 'bubbles',
  type: 'circle',
  paint: {
    'circle-radius': [
      'interpolate', ['linear'],
      ['get', 'value'],
      minValue, 4,           // min radius
      maxValue, 40           // max radius
    ],
    'circle-color': '#4269d0',
    'circle-opacity': 0.7,
    'circle-stroke-color': '#FFFFFF',
    'circle-stroke-width': 1
  }
});
```

### 排版
```javascript
// 地图注记保持轻量，重点在数据
// 只显示必要的地理名称（大比例尺时）
map.setLayoutProperty('place-label', 'text-size', [
  'interpolate', ['linear'], ['zoom'],
  0, 10,
  10, 12
]);
```

## 默认

- 中心按数据范围；`fitBounds`，padding 50px。
- 默认 Mercator；中国范围 Albers。
- 仅保留必要缩放控件；支持滚轮与拖拽。
- 底图/边界优先本地资产；远程失败时保留无瓦片数据层与表格降级。
