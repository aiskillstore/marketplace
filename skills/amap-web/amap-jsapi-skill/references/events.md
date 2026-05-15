# 事件系统 (Event System)

JSAPI v2.0 提供了一套类似于 DOM 的事件机制，支持对地图及覆盖物进行事件绑定和解绑。

## 事件绑定 (on)

```javascript
// 绑定地图点击事件
const clickHandler = function(e) {
    console.log('点击位置：', e.lnglat.getLng(), e.lnglat.getLat());
    console.log('触发对象：', e.target);
    console.log('像素坐标：', e.pixel);
};

map.on('click', clickHandler);

// 绑定覆盖物事件
marker.on('mouseover', function(e) {
    marker.setLabel({ content: '鼠标移入' });
});
```

## 事件解绑 (off)

**注意**: 解绑时需要传入绑定时的**同一个函数引用**。

```javascript
// 正确方式
map.off('click', clickHandler);



## 一次性事件 (once)

事件只触发一次后自动解绑。

```javascript
map.once('click', function(e) {
  console.log('只触发一次');
});
```

## 常用事件列表

### 地图事件 (Map Events)

| 事件名 | 说明 | 回调参数 |
| :--- | :--- | :--- |
| complete | 地图资源加载完成 | - |
| click | 左键单击 | MapsEvent |
| dblclick | 左键双击 | MapsEvent |
| rightclick | 右键单击 | MapsEvent |
| mousemove | 鼠标移动 | MapsEvent |
| mousewheel | 鼠标滚轮 | MapsEvent |
| mouseover | 鼠标移入 | MapsEvent |
| mouseout | 鼠标移出 | MapsEvent |
| mousedown | 鼠标按下 | MapsEvent |
| mouseup | 鼠标抬起 | MapsEvent |
| touchstart | 触摸开始 | MapsEvent |
| touchmove | 触摸移动 | MapsEvent |
| touchend | 触摸结束 | MapsEvent |
| zoomstart | 缩放开始 | - |
| zoomend | 缩放结束 | - |
| zoomchange | 缩放级别变化 | - |
| movestart | 平移开始 | - |
| moveend | 平移结束 | - |
| mapmove | 地图移动中 | - |
| rotatestart | 旋转开始 | - |
| rotateend | 旋转结束 | - |
| rotatechange | 旋转角度变化 | - |
| dragstart | 拖拽开始 | - |
| dragging | 拖拽中 | - |
| dragend | 拖拽结束 | - |
| resize | 地图容器大小变化 | - |
| hotspotclick | 热点点击 | { type, lnglat, name, id } |
| hotspotover | 热点移入 | { type, lnglat, name, id } |
| hotspotout | 热点移出 | { type, lnglat, name, id } |

### 覆盖物事件 (Overlay Events)

适用于 `Marker`, `Polygon`, `Polyline`, `Circle` 等。

| 事件名 | 说明 |
| :--- | :--- |
| `click` | 点击覆盖物 |
| `mouseover` | 鼠标移入 |
| `mouseout` | 鼠标移出 |
| `dragstart` | 开始拖拽 (需设置 `draggable: true`) |
| `dragging` | 拖拽中 |
| `dragend` | 拖拽结束 |

## 完整示例

### 基础事件监听

```javascript
const map = new AMap.Map('container', {
  zoom: 14,
  center: [116.397, 39.909]
});

// 地图加载完成
map.on('complete', function() {
  console.log('地图加载完成');
});

// 点击事件
map.on('click', function(e) {
  console.log('点击坐标:', e.lnglat.getLng(), e.lnglat.getLat());
  
  // 在点击位置添加标记
  new AMap.Marker({
    map: map,
    position: e.lnglat
  });
});

// 缩放事件
map.on('zoomend', function() {
  console.log('当前缩放级别:', map.getZoom());
});

// 移动事件
map.on('moveend', function() {
  console.log('当前中心点:', map.getCenter());
});
```
### 覆盖物事件

```javascript
const marker = new AMap.Marker({
  position: [116.397, 39.909],
  draggable: true
});
map.add(marker);

// 点击事件
marker.on('click', function(e) {
  console.log('点击了标记');
});

// 鼠标移入移出
marker.on('mouseover', function() {
  marker.setLabel({ content: '鼠标移入' });
});

marker.on('mouseout', function() {
  marker.setLabel({ content: '' });
});

// 拖拽事件
marker.on('dragstart', function() {
  console.log('开始拖拽');
});

marker.on('dragend', function(e) {
  console.log('拖拽结束，新位置:', e.target.getPosition());
});
```

## 自定义事件上下文

可以通过 `context` 参数指定回调函数中的 `this` 指向。

```javascript
map.on('click', function() {
    this.foo(); // this 指向 myObj
}, myObj);
```

## 注意事项

1. **函数引用**: 解绑事件时必须传入绑定时的同一个函数引用
2. **避免匿名函数**: 如果需要解绑，不要使用匿名函数
3. **内存管理**: 组件销毁前解绑事件，防止内存泄漏
4. **事件冒泡**: 覆盖物事件会冒泡到地图，必要时阻止冒泡
5. **触摸事件**: 移动端需要监听 touch 系列事件
6. **异步加载**: complete 事件在地图资源加载完成后触发