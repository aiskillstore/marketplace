# 点标记 (Markers)

高德地图 JSAPI v2.0 提供了多种类型的点标记，适用于不同的业务场景。

## 1. 基础点标记 (Marker)

最常用的点标记，支持自定义图标或 DOM 内容。

```javascript
// 默认蓝色水滴图标
const marker = new AMap.Marker({
    position: [116.397, 39.909], // 位置
    icon: new AMap.Icon({
        size: new AMap.Size(40, 50),
        image: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png',
        imageSize: new AMap.Size(40, 50),
    }),
    title: '北京',              // 鼠标悬停文本
});
map.add(marker);

// 自定义图标
const iconMarker = new AMap.Marker({
    position: [116.397, 39.909],
    icon: new AMap.Icon({
        size: new AMap.Size(40, 50),
        image: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png',
        imageSize: new AMap.Size(40, 50),
    }),
    offset: new AMap.Pixel(-20, -50), // 锚点偏移
});

// 自定义 DOM 内容 (灵活性最强，但性能消耗较高)
const contentMarker = new AMap.Marker({
    position: [116.397, 39.909],
    content: '<div class="custom-marker">我的标记</div>',
    offset: new AMap.Pixel(-15, -15),
});
```
### 自定义图标样式

以下是几种常用的 Marker 样式，可直接复制使用。

#### 带徽标的定位点

适用于用户头像、 Logo 等场景。

```javascript
const marker = new AMap.Marker({
  position: [116.397, 39.909],
  content: `
    <div class="avatar-marker">
      <img src="https://example.com/avatar.jpg" alt="头像" />
      <span class="status online"></span>
    </div>
  `,
  offset: new AMap.Pixel(-20, -20),
});
```

```css
.avatar-marker {
  position: relative;
  width: 40px;
  height: 40px;
}
.avatar-marker img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  object-fit: cover;
}
.avatar-marker .status {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid #fff;
}
.avatar-marker .status.online { background: #52c41a; }
.avatar-marker .status.offline { background: #999; }
.avatar-marker .status.busy { background: #f5222d; }
```

#### 信息卡片式 Marker

适用于 POI 展示、信息等场景。

```javascript
const marker = new AMap.Marker({
  position: [116.397, 39.909],
  content: `
    <div class="card-marker">
      <div class="card-content">
        <span class="card-price">¥288</span>
        <span class="card-unit">/晚</span>
      </div>
      <div class="card-arrow"></div>
    </div>
  `,
  offset: new AMap.Pixel(-40, -52),
});
```

```css
.card-marker {
  position: relative;
  cursor: pointer;
  transition: transform 0.2s;
}
.card-marker:hover {
  transform: scale(1.05);
}
.card-content {
  background: #fff;
  border-radius: 8px;
  padding: 6px 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  white-space: nowrap;
}
.card-price {
  font-size: 14px;
  font-weight: 600;
  color: #1890ff;
}
.card-unit {
  font-size: 12px;
  color: #999;
}
.card-arrow {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid #fff;
}
/* 选中状态 */
.card-marker.active .card-content {
  background: #1890ff;
}
.card-marker.active .card-price,
.card-marker.active .card-unit {
  color: #fff;
}
.card-marker.active .card-arrow {
  border-top-color: #1890ff;
}
```

#### 带数字序号的 Marker

适用于路线规划、排序展示等场景。

```javascript
function createNumberMarker(number, isStart = false, isEnd = false) {
  let bgColor = '#1890ff';
  if (isStart) bgColor = '#52c41a';
  if (isEnd) bgColor = '#f5222d';
  
  return new AMap.Marker({
    position: [116.397, 39.909],
    content: `
      <div class="number-marker" style="background: ${bgColor}">
        <span>${number}</span>
      </div>
    `,
    offset: new AMap.Pixel(-15, -15),
  });
}

// 使用示例
const startMarker = createNumberMarker('起', true);
const endMarker = createNumberMarker('终', false, true);
const waypoint = createNumberMarker(1);
```

```css
.number-marker {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  border: 2px solid #fff;
}
```

#### 分类图标 Marker

适用于 POI 分类展示。

```javascript
// 定义分类图标
const categoryIcons = {
  restaurant: { icon: '🍽️', color: '#fa8c16' },
  hotel: { icon: '🏨', color: '#1890ff' },
  scenic: { icon: '🏞️', color: '#52c41a' },
  shopping: { icon: '🛍️', color: '#eb2f96' },
  hospital: { icon: '🏥', color: '#f5222d' },
};

function createCategoryMarker(category, name) {
  const { icon, color } = categoryIcons[category] || { icon: '📍', color: '#1890ff' };
  
  return new AMap.Marker({
    position: [116.397, 39.909],
    content: `
      <div class="category-marker" style="--marker-color: ${color}">
        <div class="marker-icon">${icon}</div>
        <div class="marker-label">${name}</div>
        <div class="marker-arrow"></div>
      </div>
    `,
    offset: new AMap.Pixel(-50, -58),
  });
}

// 使用示例
const restaurantMarker = createCategoryMarker('restaurant', '海底捞火锅');
```

```css
.category-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.marker-icon {
  width: 36px;
  height: 36px;
  background: var(--marker-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  border: 2px solid #fff;
}
.marker-label {
  margin-top: 4px;
  padding: 2px 8px;
  background: #fff;
  border-radius: 4px;
  font-size: 12px;
  color: #333;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  white-space: nowrap;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.marker-arrow {
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 5px solid #fff;
}
```

## 2. 带文字标记

```javascript
const marker = new AMap.Marker({
  position: [116.397, 39.909],
  label: {
    content: '北京天安门',
    direction: 'top', // top, right, bottom, left, center
    offset: new AMap.Pixel(0, -5),
  },
});
```

## 2. 海量标注 (LabelMarker)

**强烈推荐**用于海量点位（千级/万级以上）展示。它是基于 WebGL 的矢量标注，支持文字和图标避让，性能极佳。

> **注意**：必须配合 `LabelsLayer` 图层使用。

```javascript
// 1. 创建图层
const layer = new AMap.LabelsLayer({
    zooms: [3, 20],
    zIndex: 1000,
    collision: true, // 开启碰撞避让
    allowCollision: false, // 允许被避让隐藏
});
map.add(layer);

// 2. 创建 LabelMarker
const labelMarker = new AMap.LabelMarker({
    position: [116.397, 39.909],
    icon: {
        type: 'image',
        image: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
        size: [6, 10],
        anchor: 'bottom-center',
    },
    text: {
        content: '北京天安门',
        direction: 'top',
        style: {
            fontSize: 12,
            fillColor: '#fff',
            strokeColor: '#000',
            strokeWidth: 1,
        }
    }
});

// 3. 添加到图层
layer.add(labelMarker);
```

## 3. 灵活点标记 (ElasticMarker)

适用于随地图缩放需要动态改变样式或大小的场景。

```javascript
const elasticMarker = new AMap.ElasticMarker({
    position: [116.397, 39.909],
    zooms: [14, 20],
    styles: [{
        icon: {
            img: '...',
            size: [16, 16],
            ancher: [8, 16],
            fitZoom: 14, // 适用于 zoom >= 14
            scaleFactor: 2, // 缩放比例
        }
    }]
});
map.add(elasticMarker);
```

## 常用操作

```javascript
marker.setPosition([lng, lat]); // 更新位置
marker.setMap(null);            // 从地图移除
marker.hide();                  // 隐藏
marker.show();                  // 显示
```
