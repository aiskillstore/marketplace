## 右键菜单




## ContextMenu

**Extends OverlayDOM**

右键菜单 [亲手试一试][82]

### Parameters

-   `opts` **OverlayOptions** 右键菜单参数
    -   `opts.position` **(Vector2 | LngLat)** 右键菜单显示的位置
    -   `opts.content` **(string \| HTMLElement)** 右键菜单内容（针对自定义菜单时，添加菜单内容及功能。可以是HTML要素字符串或者HTML DOM对象。）

### Examples

```javascript
// 创建一个右键菜单实例
var contextMenu = new AMap.ContextMenu();
//右键放大
contextMenu.addItem("放大一级", function () {
    var zoom = map.getZoom();
    map.setZoom(zoom++);
}, 0);
// 在地图上指定位置打开右键菜单
contextMenu.open(map, [116.397389,39.909466]);
```

### open

打开右键菜单

#### Parameters

-   `map` **Map** 
-   `position` **Vector2** 

### close

关闭右键菜单

### addItem

菜单添加一条内容

#### Parameters

-   `text` **string** 
-   `fn` **EventListener** 
-   `num` **number** 

### removeItem

菜单移除一条内容

#### Parameters

-   `text` **string** 
-   `fn` **EventListener** 
