## 信息窗体

用于在地图上展示复杂的说明性信息的类型


## InfoWindow

**Extends OverlayDOM**

信息窗体，地图仅可同时展示一个信息窗体，推荐为信息窗体通过样式显示设置尺寸。 \* // [亲手试一试][79]

### Parameters

-   `opts` **InfoOptions** 信息窗体参数
    -   `opts.isCustom` **boolean** 是否自定义窗体。设为true时，信息窗体外框及内容完全按照content所设的值添加（默认为false，即在系统默认的信息窗体外框中显示content内容）
    -   `opts.autoMove` **boolean** 是否自动调整窗体到视野内（当信息窗体超出视野范围时，通过该属性设置是否自动平移地图，使信息窗体完全显示）
    -   `opts.avoid` **Array&lt;number>** autoMove 为 true 时，自动平移到视野内后的上右下左的避让宽度。默认值：[20, 20, 20, 20]
    -   `opts.closeWhenClickMap` **boolean** 控制是否在鼠标点击地图后关闭信息窗体，默认false，鼠标点击地图后不关闭信息窗体
    -   `opts.content` **(String \| HTMLElement)** 显示内容，可以是HTML要素字符串或者HTMLElement对象, [自定义窗体示例][81]
    -   `opts.size` **Size** 信息窗体尺寸（isCustom为true时，该属性无效）
    -   `opts.anchor` **string** 信息窗体锚点。默认值：'bottom-center'。可选值：'top-left'|'top-center'|'top-right'|'middle-left'|'center'|'middle-right'|'bottom-left'|'bottom-center'|'bottom-right'
    -   `opts.offset` **(Vector | Pixel)** 信息窗体显示位置偏移量。默认基准点为信息窗体的底部中心。默认值: [0, 0]
    -   `opts.position` **(Vector | LngLat)** 信息窗体显示基点位置

### Examples

```javascript
var infoWindow = new AMap.InfoWindow({
   content: '信息窗体',
   anchor: 'bottom-center',
});
// 在地图上打开信息窗体
infoWindow.open(map, [116.397389,39.909466]);
```

### open

打开信息窗体

#### Parameters

-   `map` **Map** 
-   `position` **Vector2** 
-   `height` **number** 

### getIsOpen

获取信息窗体是否打开

Returns **boolean** 

### setSize

设置信息窗体大小（isCustom为false时有效）

#### Parameters

-   `size` **(Size | Vector2)** 

### setContent

获取信息窗体大小

#### Parameters

-   `content` **(HTMLElement \| string)** 

### setAnchor

设置信息窗体锚点 默认值：'bottom-center'。可选值：'top-left'|'top-center'|'top-right'|'middle-left'|'center'|'middle-right'|'bottom-left'|'bottom-center'|'bottom-right'

#### Parameters

-   `anchor` **string** 

### getExtData

获取用户自定义属性

Returns **(any | undefined)** 

### setExtData

设置用户自定义属性

#### Parameters

-   `extData`  
