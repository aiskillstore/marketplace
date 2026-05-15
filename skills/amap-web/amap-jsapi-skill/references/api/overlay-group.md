## 群组

用于批量操作图层和覆盖物的群组类型，可以简化代码书写


## LayerGroup

LayerGroup类用来包装其它图层类的实例， 对实例集合做批量操作， 避免开发者对多个需要设置同样属性的图层实例做循环处理。</br>
同时只要对LayerGroup执行过setMap方法后， 新添加到该LayerGroup中的图层会自动将其map属性修改到该group对应的map，</br>
此外从group中移除该图层时，也会将该图层从group对应的map中移除。</br>
如果对图层集合添加对某个事件的监听或解除监听， 图层集合会对集合中所有图层实例做集合处理， </br>
只要该图层支持此事件， 该事件绑定/解除即对图层生效
[相关示例][86]

### Parameters

-   `layers` **Array&lt;Layer>** 图层数组

### setMap

添加到地图上面

#### Parameters

-   `map` **Map** 地图对象

Returns **any** 

### hasLayer

判断传入的图层实例是否在集合中

#### Parameters

-   `layer` **Layer** 

### setOptions

修改图层属性(包括线样式、样色等等)

#### Parameters

-   `opts` **LayerOptions** 参数
    -   `opts.visible` **Boolean** 是否可见
    -   `opts.opacity` **Number** 透明度
    -   `opts.zIndex` **Number** 层级
    -   `opts.zooms` **Array&lt;Number>** 集合可见范围

Returns **any** 

### eachLayer

对集合中的图层做迭代操作，其中iterator的函数定义是：</br>
function(layer, index, collections)，相关含义如下：</br>
layer: 当前迭代到的图层 </br>
index: 该图层在集合中的序列号(从0开始) </br>
collections: 所有图层实例 </br>

#### Parameters

-   `iterator` **Function** 

### addLayer

添加单个图层到集合中，不支持添加重复的图层

#### Parameters

-   `layer` **Layer** 图层对象

### addLayers

添加图层数组到集合中，不支持添加重复的图层

#### Parameters

-   `layers` **Array&lt;Layer>** 图层数组

### removeLayer

从集合中删除传入的图层实例

#### Parameters

-   `layer` **Layer** 图层对象

### removeLayers

从集合中删除传入的图层实例数组

#### Parameters

-   `layers` **Array&lt;Layer>** 图层数组

### getLayers

获取组里所有对象，包括图层和覆盖物

Returns **Array&lt;Layers>** 

### clearLayers

清空图层

### hide

设置图层隐藏

### show

设置图层可见

### on

事件批量绑定

#### Parameters

-   `type` **String** 事件名称, 比如: click、mouseover
-   `事件回调函数` **Function** 

### reload

重新加载图层资源，重新渲染

Returns **any** 

## OverlayGroup

OverlayGroup 类用来包装其它覆盖物类的实例，对实例集合做整体操作，避免开发者对多个需要设置同样属性的覆盖物实例做循环处理。
此外从group中移除该覆盖物时，也会将该覆盖物从group对应的map中移除。
目前OverlayGroup支持Marker, Polygon, Polyline, Circle,CircleMarker, Rectangle, Ellipse 和 BezierCurve。

### Parameters

-   `overlays` **Array&lt;Overlay>** 

### addOverlay

添加单个覆盖物到集合中，不支持添加重复的覆盖物

#### Parameters

-   `overlay` **Overlay** 

### type

### className

### addOverlays

添加覆盖物数组到集合中，不支持添加重复的覆盖物

#### Parameters

-   `overlays` **Array&lt;Overlay>** 

### getOverlays

返回当前集合中所有的覆盖物

Returns **Array** 

### hasOverlay

判断传入的覆盖物实例是否在集合中

#### Parameters

-   `overlay` **Overlay** 

Returns **boolean** 

### removeOverlay

从集合中删除传入的覆盖物实例

#### Parameters

-   `overlay` **Overlay** 

### removeOverlays

从集合中删除传入的覆盖物实例数组

#### Parameters

-   `overlays` **Array** 

### clearOverlays

清空集合

### eachOverlay

对集合中的覆盖物做迭代操作，其中iterator的函数定义是：
function(overlay, index, collections)，相关含义如下：
overlay: 当前迭代到的覆盖物
index: 该覆盖物在集合中的序列号(从0开始)
collections: 所有覆盖物实例

#### Parameters

-   `iterator` **Function** 

### show

在地图上显示集合中覆盖物

### hide

在地图上隐藏集合中覆盖物

### setOptions

修改覆盖物属性(包括线样式、样色等等)

#### Parameters

-   `opt` **Object** 
