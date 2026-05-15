# 官方图层 (Official Layers)

高德地图 JSAPI v2.0 内置了多种标准图层，开发者可以按需叠加使用。

## 1. 标准切片图层 (TileLayer)

基础的栅格瓦片图层。

```javascript
// 默认标准图层
const layer = new AMap.TileLayer();
map.add(layer);
```

### 衍生图层

- **卫星图层 (Satellite)**
  ```javascript
  const satellite = new AMap.TileLayer.Satellite();
  map.add(satellite);
  ```

- **路网图层 (RoadNet)**
  通常叠加在卫星图上使用，展示道路网络。
  ```javascript
  const roadNet = new AMap.TileLayer.RoadNet();
  map.add(roadNet);
  ```

- **实时路况图层 (Traffic)**
  展示实时的交通拥堵情况。
  ```javascript
  const traffic = new AMap.TileLayer.Traffic({
      zIndex: 10,
      autoRefresh: true, // 是否自动刷新
      interval: 180,     // 刷新间隔 (秒)
  });
  map.add(traffic);
  ```

## 2. 3D 楼块图层 (Buildings)

用于展示 3D 建筑物模型，仅在 `viewMode: '3D'` 下有效。

```javascript
const buildings = new AMap.Buildings({
    zooms: [16, 20],    // 显示层级范围
    zIndex: 10,
    heightFactor: 2,    // 楼块高度系数
});
map.add(buildings);

// 设置楼块样式
buildings.setStyle({
    hideWithoutStyle: false, // 是否隐藏未设置样式的楼块
    areas: [{ 
        color1: 'red', // 顶面颜色
        color2: 'blue', // 侧面颜色
        path: [[116.403322, 39.920255], ...], // 围栏区域
    }]
});
```

## 3. 室内地图图层 (IndoorMap)

当缩放级别达到一定程度且地图中心位于支持室内地图的建筑（如大型商场、机场）时自动显示。

```javascript
const indoor = new AMap.IndoorMap({
    alwaysShow: true, // 是否始终显示
});
map.add(indoor);

// 监听楼层切换
indoor.on('floor_change', function(e) {
    console.log('当前楼层：', e.floor);
});
```
