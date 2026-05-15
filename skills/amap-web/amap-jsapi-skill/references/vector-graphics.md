# 矢量图形 (Vector Graphics)

JSAPI v2.0 支持在地图上绘制各种矢量图形，如折线、多边形、圆和贝塞尔曲线。所有矢量图形均支持 WebGL 渲染。

## 1. 折线 (Polyline)

用于绘制路径、轨迹或边界线。

```javascript
const path = [
    [116.368904, 39.913423],
    [116.382122, 39.901176],
    [116.387271, 39.912501],
    [116.398258, 39.904600]
];

const polyline = new AMap.Polyline({
    path: path,
    isOutline: true,         // 是否显示描边
    outlineColor: '#ffeeff', // 描边颜色
    borderWeight: 3,         // 描边宽度
    strokeColor: "#3366FF",  // 线颜色
    strokeOpacity: 1,        // 线透明度
    strokeWeight: 6,         // 线宽
    strokeStyle: "solid",    // 线样式: solid, dashed
    strokeDasharray: [10, 5], // 虚线间隔
    lineJoin: 'round',       // 折线拐点样式
    lineCap: 'round',        // 折线端点样式
    zIndex: 50,
});

map.add(polyline);
```

### Polyline 配置项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| path | Array | - | 路径坐标 `[[lng, lat], ...]` |
| strokeColor | String | '#00D' | 线条颜色 |
| strokeOpacity | Number | 1 | 线条透明度 0-1 |
| strokeWeight | Number | 1 | 线条宽度（像素） |
| strokeStyle | String | 'solid' | 线条样式：solid / dashed |
| strokeDasharray | Array | - | 虚线间隔，如 `[10, 5]` |
| isOutline | Boolean | false | 是否显示描边 |
| outlineColor | String | '#000' | 描边颜色 |
| borderWeight | Number | 1 | 描边宽度 |
| lineJoin | String | 'miter' | 拐点样式：miter / round / bevel |
| lineCap | String | 'butt' | 端点样式：butt / round / square |
| geodesic | Boolean | false | 是否大地线（地球曲面最短路径） |
| showDir | Boolean | false | 是否显示方向箭头 |
| zIndex | Number | 10 | 层叠顺序 |
| extData | Any | - | 自定义数据 |

## 2. 多边形 (Polygon)

用于绘制区域、围栏或建筑物轮廓。

```javascript
const polygonPath = [
    [116.403322, 39.920255],
    [116.410703, 39.897555],
    [116.402292, 39.892353],
    [116.389846, 39.891365]
];

const polygon = new AMap.Polygon({
    path: polygonPath,
    fillColor: '#ccebc5',   // 填充颜色
    fillOpacity: 0.5,       // 填充透明度
    strokeColor: '#2b8cbe', // 轮廓线颜色
    strokeWeight: 2,        // 轮廓线宽度
});

map.add(polygon);
```

### Polygon 配置项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| path | Array | - | 多边形路径 `[[lng, lat], ...]`，支持带孔 `[外环, 孔1, 孔2]` |
| fillColor | String | '#00D' | 填充颜色 |
| fillOpacity | Number | 0.5 | 填充透明度 0-1 |
| strokeColor | String | '#00D' | 边框颜色 |
| strokeOpacity | Number | 1 | 边框透明度 0-1 |
| strokeWeight | Number | 1 | 边框宽度（像素） |
| strokeStyle | String | 'solid' | 边框样式：solid / dashed |
| strokeDasharray | Array | - | 虚线间隔 |
| zIndex | Number | 10 | 层叠顺序 |
| extData | Any | - | 自定义数据 |

## 3. 圆 (Circle)

用于绘制圆形区域，常用于周边搜索范围展示。

```javascript
const circle = new AMap.Circle({
    center: [116.403322, 39.920255], // 圆心
    radius: 1000,           // 半径 (米)
    fillColor: '#ee2200',
    fillOpacity: 0.5,
    strokeColor: '#F33',
    strokeWeight: 1,
});

map.add(circle);
```

## 4. 贝塞尔曲线 (BezierCurve)

绘制平滑曲线，常用于航线或流向图。

```javascript
const path = [
    // 起点
    [116.39, 39.91, 116.37, 39.91], // 控制点1, 控制点2
    // 途经点
    [116.38, 39.92, 116.38, 39.93, 116.39, 39.93], 
    // ...
];

const bezier = new AMap.BezierCurve({
    path: path,
    isOutline: true,
    outlineColor: '#ffeeff',
    borderWeight: 3,
    strokeColor: "#3366FF", 
    strokeWeight: 6,
    strokeOpacity: 0.9,
});

map.add(bezier);
```

## 矢量图形编辑器

高德提供了 `AMap.PolyEditor`, `AMap.CircleEditor` 等插件，允许用户在地图上交互式编辑矢量图形。

```javascript
// 需先加载插件 AMap.PolyEditor
const polyEditor = new AMap.PolyEditor(map, polyline);

polyEditor.open(); // 开启编辑
// polyEditor.close(); // 结束编辑

polyEditor.on('end', function(event) {
    console.log('编辑结束，新路径：', event.target.getPath());
});
```
## 5. 最佳实践

### 性能优化

```javascript
// 大量坐标点时，使用 setPath 而非重新创建
polyline.setPath(newPath);  // 推荐
// map.remove(old); map.add(new);  // 不推荐

// 批量操作使用数组
map.add([polyline1, polyline2, polygon1]);
map.remove([polyline1, polyline2]);
```

### 常见问题

**Q: 多边形不显示？**

检查路径是否闭合（首尾相连），确保至少 3 个点。

**Q: 编辑器报错？**

确保先加载插件：

```javascript
AMap.plugin(['AMap.PolyEditor', 'AMap.CircleEditor'], function() {
  // 使用编辑器
});
```

**Q: 如何判断点是否在多边形内？**

```javascript
const isInside = polygon.contains([lng, lat]);
```

