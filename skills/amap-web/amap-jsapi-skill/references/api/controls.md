## 地图控件

固定于地图最上层的用于控制地图某些状态的 DOM 组件类型


## Control

**Extends \_Event.Event**

### Parameters

-   `opts`  

### addTo

添加控件到地图上

#### Parameters

-   `map` **Map** 地图实例

### remove

从地图上移除控件

### show

设置控件可见

### hide

设置控件隐藏

## Control

**Extends Event**

地图控件基类，可扩展做自定义地图控件。

### Parameters

-   `opts` **ControlConfig** 默认参数
    -   `opts.position` **(string \| object)** 控件停靠位置
        { top: 5; left: 5; right: 5; bottom: 5 } 或者
        'LT': 左上角, 'RT': 右上角, 'LB': 左下角, 'RB': 右下角
    -   `opts.offset` **\[number, number]** 相对于地图容器左上角的偏移量，正数代表向右下偏移。默认为AMap.Pixel(10,10)

### addTo

添加控件到地图上

#### Parameters

-   `map` **Map** 地图实例

### remove

从地图上移除控件

### show

设置控件可见

### hide

设置控件隐藏

## Scale

**Extends AMap.Control**

比例尺插件。位于地图右下角，用户可控制其显示与隐藏。继承自 AMap.Control </br>
[相关示例][87]

### Parameters

-   `opts` **ControlConfig** 默认参数
    -   `opts.position` **(string \| object)** 控件停靠位置
        { top: 5; left: 5; right: 5; bottom: 5 } 或者
        'LT': 左上角, 'RT': 右上角, 'LB': 左下角, 'RB': 右下角
    -   `opts.offset` **\[number, number]** 相对于地图容器左上角的偏移量，正数代表向右下偏移。默认为AMap.Pixel(10,10)

### Examples

```javascript
mapObj.plugin(["AMap.Scale"],function(){
    var scale = new AMap.Scale();
    mapObj.addControl(scale);
});
```

### addTo

添加控件到地图上

#### Parameters

-   `map` **Map** 地图实例

### removeFrom

从地图上移除控件

### show

设置控件可见

### hide

设置控件隐藏

## ToolBar

**Extends AMap.Control**

地图操作工具条插件。可支持方向导航、位置定位、视野级别缩放、视野级别选择等操作。继承自 AMap.Control </br>
[相关示例][87]

### Parameters

-   `opts` **ControlConfig** 默认参数
    -   `opts.position` **(String \| Object)** 控件停靠位置
        { top: 5; left: 5; right: 5; bottom: 5 } 或者
        'LT': 左上角, 'RT': 右上角, 'LB': 左下角, 'RB': 右下角
    -   `opts.offset` **\[Number, Number]** 相对于地图容器左上角的偏移量，正数代表向右下偏移。默认为AMap.Pixel(10,10)

### Examples

```javascript
mapObj.plugin(["AMap.ToolBar"],function(){
    //加载工具条
    var tool = new AMap.ToolBar();
    mapObj.addControl(tool);
});
```

### addTo

添加控件到地图上

#### Parameters

-   `map` **Map** 地图实例

### remove

从地图上移除控件

### show

设置控件可见

### hide

设置控件隐藏

## ControlBar

**Extends AMap.Control**

组合了旋转、倾斜、复位在内的地图控件。 </br>
[相关示例][87]

### Parameters

-   `opts` **ControlConfig** 默认参数
    -   `opts.position` **(string \| object)** 控件停靠位置
        { top: 5; left: 5; right: 5; bottom: 5 } 或者
        'LT': 左上角, 'RT': 右上角, 'LB': 左下角, 'RB': 右下角
    -   `opts.offset` **\[number, number]** 相对于地图容器左上角的偏移量，正数代表向右下偏移。默认为AMap.Pixel(10,10)
    -   `opts.showControlButton` **boolean** 是否显示倾斜、旋转按钮。默认为 true

### Examples

```javascript
var mapObj = new AMap.Map("container",{
    center: new AMap.LngLat(116.368904,39.913423),
    zoom:16
});
mapObj.plugin(["AMap.ControlBar"],function() {
    var controlBar = new AMap.ControlBar(Options)
    map.addControl(controlBar)
});
//map.reoveControl(controlBar)
```

### addTo

添加控件到地图上

#### Parameters

-   `map` **Map** 地图实例

### remove

从地图上移除控件

### show

设置控件可见

### hide

设置控件隐藏

## MapType

**Extends AMap.Control**

### Parameters

-   `opts`  

### addLayer

添加一个图层

#### Parameters

-   `layerInfo` **LayerInfo** 图层信息，需要包含图层对象
    -   `layerInfo.id` **String** 图层 id
    -   `layerInfo.enable` **String** 图层是否可用
    -   `layerInfo.name` **String** 图层暂时名称
    -   `layerInfo.type` **(`"base"` \| `"overlay"`)** 图层类型，base 是属于底图图层，overlay 属于叠加图层。
    -   `layerInfo.layer` **Layer** 图层对象
    -   `layerInfo.show` **Boolean** 图层是否显示

### removeLayer

移除一个图层

#### Parameters

-   `id` **String** 图层 id

### addTo

添加控件到地图上

#### Parameters

-   `map` **Map** 地图实例

### remove

从地图上移除控件

### show

设置控件可见

### hide

设置控件隐藏

## MapType

**Extends AMap.Control**

### Parameters

-   `opts`  

### addLayer

添加一个图层

#### Parameters

-   `layerInfo` **LayerInfo** 图层信息，需要包含图层对象
    -   `layerInfo.id` **String** 图层 id
    -   `layerInfo.enable` **String** 图层是否可用
    -   `layerInfo.name` **String** 图层暂时名称
    -   `layerInfo.type` **(`"base"` \| `"overlay"`)** 图层类型，base 是属于底图图层，overlay 属于叠加图层。
    -   `layerInfo.layer` **Layer** 图层对象
    -   `layerInfo.show` **Boolean** 图层是否显示

### removeLayer

移除一个图层

#### Parameters

-   `id` **String** 图层 id

### addTo

添加控件到地图上

#### Parameters

-   `map` **Map** 地图实例

### remove

从地图上移除控件

### show

设置控件可见

### hide

设置控件隐藏

## MapType

**Extends AMap.Control**

地图类型切换插件。用户通过该插件进行地图切换。

### Parameters

-   `opts` **MaptypeOptions** 控件默认参数
    -   `opts.defaultType` **number** 初始化默认图层类型。 取值为0：默认底图 取值为1：卫星图 默认值：0 (optional, default `0`)
    -   `opts.showTraffic` **boolean** 叠加实时交通图层 默认值：false (optional, default `false`)
    -   `opts.showRoad` **boolean** 叠加路网图层 默认值：false (optional, default `false`)

### Examples

```javascript
mapObj = new AMap.Map("container",{
    center:new AMap.LngLat(116.368904,39.913423),
    zoom: 16
});
mapObj.plugin(["AMap.MapType"],function(){
    //地图类型切换
    var type= new AMap.MapType({
        defaultType: 0,
    });
    mapObj.addControl(type);
});
```

### addLayer

添加一个图层

#### Parameters

-   `layerInfo` **LayerInfo** 图层信息，需要包含图层对象
    -   `layerInfo.id` **String** 图层 id
    -   `layerInfo.enable` **String** 图层是否可用
    -   `layerInfo.name` **String** 图层暂时名称
    -   `layerInfo.type` **(`"base"` \| `"overlay"`)** 图层类型，base 是属于底图图层，overlay 属于叠加图层。
    -   `layerInfo.layer` **Layer** 图层对象
    -   `layerInfo.show` **Boolean** 图层是否显示

### removeLayer

移除一个图层

#### Parameters

-   `id` **String** 图层 id

### addTo

添加控件到地图上

#### Parameters

-   `map` **Map** 地图实例

### remove

从地图上移除控件

### show

设置控件可见

### hide

设置控件隐藏

## HawkEye

**Extends AMap.Control**

鹰眼控件，用于显示缩略地图，显示于地图右下角，可以随主图的视口变化而变化，也可以配置成固定位置实现类似于南海附图的效果。

### Parameters

-   `options` **HawkEyeOptions** 初始化参数
    -   `options.autoMove` **boolean** 是否随主图视口变化移动
    -   `options.showRectangle` **boolean** 是否显示视口矩形
    -   `options.showButton` **boolean** 是否显示打开关闭的按钮
    -   `options.opened` **boolean** 默认是否展开
    -   `options.mapStyle` **string** 缩略图要显示的地图自定义样式，如'amap://styles/dark'
    -   `options.layers` **array** 缩略图要显示的图层类型，默认为普通矢量地图
    -   `options.width` **string** 缩略图的宽度，同CSS，如'200px'
    -   `options.height` **string** 缩略图的高度，同CSS，如'200px'
    -   `options.offset` **\[number, number]** 缩略图距离地图右下角的像素距离，如[2,2]
    -   `options.borderStyle` **string** 缩略图的边框样式，同CSS，如"double solid solid double"
    -   `options.borderColor` **string** 缩略图的边框颜色，同CSS，如'silver'
    -   `options.borderRadius` **string** 缩略图的圆角半径，同CSS，如'5px'
    -   `options.borderWidth` **string** 缩略图的边框宽度，同CSS，如'2px'
    -   `options.buttonSize` **string** 缩略图的像素尺寸，同CSS，如'12px'

### show

恢复鹰眼控件的正常大小

### hide

最小化鹰眼控件
