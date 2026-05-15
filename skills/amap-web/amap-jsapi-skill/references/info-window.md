# 信息窗体 (InfoWindow)

信息窗体用于在地图上弹出一个浮层，展示详细信息。它可以绑定到特定位置或覆盖物上。

## 基础用法

```javascript
// 1. 创建信息窗体
const infoWindow = new AMap.InfoWindow({
    content: '<h4>标题</h4><div>这是信息窗体的内容</div>', // 支持 HTML 字符串或 DOM 元素
    anchor: 'bottom-center', // 锚点位置: top-left, top-center, top-right, middle-left, center, middle-right, bottom-left, bottom-center, bottom-right
    offset: new AMap.Pixel(0, -30), // 偏移量，避免遮挡标记
    isCustom: false, // 是否自定义外观 (设为 true 则不显示默认边框和关闭按钮)
    autoMove: true, // 是否自动调整地图视野使窗体可见
    closeWhenClickMap: true, // 点击地图其他空白处关闭窗体
});

// 2. 打开信息窗体
infoWindow.open(map, [116.397, 39.909]); // 在指定位置打开

// 或者绑定点击事件
marker.on('click', function(e) {
    infoWindow.open(map, e.target.getPosition());
});
```

## 自定义样式

如果将 `isCustom` 设为 `true`，则可以完全控制窗体的外观。

```javascript
const customInfoWindow = new AMap.InfoWindow({
    isCustom: true,
    content: createCustomContent(), // 返回一个 DOM 元素
    offset: new AMap.Pixel(16, -45)
});

function createCustomContent() {
    const div = document.createElement('div');
    div.className = 'my-info-window';
    div.innerHTML = `
        <div class="info-title">高德地图</div>
        <div class="info-body">自定义样式的窗体</div>
        <button onclick="closeInfoWindow()">关闭</button>
    `;
    return div;
}

// 需要手动实现关闭逻辑
window.closeInfoWindow = function() {
    map.clearInfoWindow();
}
```

## 更新内容

```javascript
infoWindow.setContent('<div>新的内容</div>');
infoWindow.setPosition([116.40, 39.90]);
```
## 配置项

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| content | String/HTMLElement | - | 内容，支持 HTML 字符串或 DOM 元素 |
| anchor | String | 'bottom-center' | 锚点位置 |
| offset | Pixel | - | 偏移量 |
| isCustom | Boolean | false | 是否自定义样式 |
| autoMove | Boolean | false | 是否自动调整地图视野 |
| closeWhenClickMap | Boolean | false | 点击地图其他区域是否关闭 |
| size | Size | - | 窗体大小 |
| avoid | Array | - | 避让的像素区域 |

### 锚点位置 (anchor)

- `top-left` - 左上
- `top-center` - 上中
- `top-right` - 右上
- `middle-left` - 左中
- `center` - 中心
- `middle-right` - 右中
- `bottom-left` - 左下
- `bottom-center` - 下中（默认）
- `bottom-right` - 右下

## 与标记配合使用

```javascript
const marker = new AMap.Marker({
  position: [116.397, 39.909],
  title: '点击查看详情'
});
map.add(marker);

const infoWindow = new AMap.InfoWindow({
  content: '<div>POI 详情信息</div>',
  offset: new AMap.Pixel(0, -30)
});

marker.on('click', function(e) {
  infoWindow.open(map, e.target.getPosition());
});
```

## 自定义样式

设置 `isCustom: true` 完全控制窗体外观：

```javascript
const customInfoWindow = new AMap.InfoWindow({
  isCustom: true,
  content: createCustomContent(),
  offset: new AMap.Pixel(16, -45)
});

function createCustomContent() {
  const div = document.createElement('div');
  div.className = 'custom-info-window';
  div.innerHTML = `
    <div class="info-header">
      <span class="info-title">高德地图</span>
      <span class="info-close" onclick="closeInfoWindow()">×</span>
    </div>
    <div class="info-body">
      <p>自定义样式的信息窗体</p>
      <button onclick="doSomething()">操作按钮</button>
    </div>
    <div class="info-arrow"></div>
  `;
  return div;
}

// 全局关闭方法
window.closeInfoWindow = function() {
  map.clearInfoWindow();
};
```

### 自定义样式 CSS

```css
.custom-info-window {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  min-width: 200px;
  position: relative;
}

.info-header {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;
  padding: 12px 16px;
  border-radius: 8px 8px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-title {
  font-weight: 600;
}

.info-close {
  cursor: pointer;
  font-size: 18px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.info-close:hover {
  background: rgba(255,255,255,0.2);
}

.info-body {
  padding: 16px;
}

.info-arrow {
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid #fff;
}
```

## 动态更新内容

```javascript
// 更新内容
infoWindow.setContent('<div>新的内容</div>');

// 更新位置
infoWindow.setPosition([116.40, 39.90]);

// 获取当前位置
const position = infoWindow.getPosition();

// 获取是否打开
const isOpen = infoWindow.getIsOpen();
```

## 事件监听

```javascript
infoWindow.on('open', function() {
  console.log('信息窗体已打开');
});

infoWindow.on('close', function() {
  console.log('信息窗体已关闭');
});

infoWindow.on('change', function() {
  console.log('信息窗体内容或位置已改变');
});
```

## 完整示例

```javascript
const map = new AMap.Map('container', {
  zoom: 14,
  center: [116.397, 39.909]
});

// POI 数据
const pois = [
  { name: '天安门', address: '北京市东城区', position: [116.397428, 39.90923] },
  { name: '故宫', address: '北京市东城区景山前街4号', position: [116.397026, 39.918058] },
  { name: '王府井', address: '北京市东城区', position: [116.410904, 39.913904] }
];

// 创建信息窗体
const infoWindow = new AMap.InfoWindow({
  isCustom: true,
  offset: new AMap.Pixel(0, -40)
});

// 添加标记
pois.forEach(poi => {
  const marker = new AMap.Marker({
    position: poi.position,
    title: poi.name
  });
  
  marker.on('click', function(e) {
    const content = `
      <div class="poi-info-window">
        <div class="poi-header">
          <h3>${poi.name}</h3>
          <span class="close-btn" onclick="map.clearInfoWindow()">×</span>
        </div>
        <div class="poi-body">
          <p>${poi.address}</p>
          <div class="poi-actions">
            <button onclick="navigateTo(${poi.position[0]}, ${poi.position[1]})">导航</button>
            <button onclick="shareLocation('${poi.name}')">分享</button>
          </div>
        </div>
      </div>
    `;
    
    infoWindow.setContent(content);
    infoWindow.open(map, e.target.getPosition());
  });
  
  map.add(marker);
});

// 全局方法
window.navigateTo = function(lng, lat) {
  console.log('导航到:', lng, lat);
};

window.shareLocation = function(name) {
  console.log('分享位置:', name);
};
```

## 关闭信息窗体

```javascript
// 方式一：调用 close 方法
infoWindow.close();

// 方式二：清除地图上的信息窗体
map.clearInfoWindow();
```

## 注意事项

1. **同时只能打开一个**: 地图上同时只能打开一个信息窗体
2. **自定义样式**: `isCustom: true` 时不显示默认的边框和关闭按钮
3. **偏移量**: 根据标记图标大小调整 offset，避免遮挡
4. **自动调整**: `autoMove: true` 可以自动调整地图视野使窗体可见
5. **事件冒泡**: 窗体内的点击事件需要阻止冒泡，否则可能触发地图点击事件