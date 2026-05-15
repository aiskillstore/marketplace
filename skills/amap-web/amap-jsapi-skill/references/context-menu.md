# 右键菜单 (ContextMenu)

右键菜单可以绑定到地图底图或覆盖物上，提供快捷操作功能。

## 创建菜单

```javascript
// 创建右键菜单实例
const contextMenu = new AMap.ContextMenu();

// 添加菜单项
contextMenu.addItem('放大一级', function() {
    map.zoomIn();
}, 0); // 第三个参数是排序权重

contextMenu.addItem('缩小一级', function() {
    map.zoomOut();
}, 1);

contextMenu.addItem('设置中心点', function() {
    map.setCenter(contextMenuPos); // 使用保存的点击位置
}, 2);
```

## 绑定事件

### 1. 绑定到地图

```javascript
let contextMenuPos;

map.on('rightclick', function(e) {
    contextMenuPos = e.lnglat; // 记录右键点击的位置
    contextMenu.open(map, e.lnglat);
});
```

### 2. 绑定到覆盖物 (如 Marker)

```javascript
const marker = new AMap.Marker({
    position: [116.397, 39.909]
});
map.add(marker);

const markerMenu = new AMap.ContextMenu();
markerMenu.addItem('删除标记', function() {
    map.remove(marker);
});

marker.on('rightclick', function(e) {
    markerMenu.open(map, e.lnglat);
});
```

## 动态菜单

你可以在事件回调中动态修改菜单项。

```javascript
map.on('rightclick', function(e) {
    contextMenu.removeItem('添加标记', function(){}); // 先移除旧的（如果需要）
    
    // 根据条件动态添加
    if (map.getZoom() < 10) {
        contextMenu.addItem('缩放至详细级别', () => map.setZoom(15), 0);
    }
    
    contextMenu.open(map, e.lnglat);
});
```
