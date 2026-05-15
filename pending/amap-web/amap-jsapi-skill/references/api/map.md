## 地图




## Map

地图对象类，封装了地图的属性设置、图层变更、事件交互等接口的类。</br>
[相关示例][10]

### Parameters

-   `div` **(String \| HTMLDivElement)** 构造一个地图对象，参数container中传入地图容器DIV的ID值或者DIV对象，
    opts地图初始化参数对象，参数详情参看MapOptions列表。注意：地图容器在创建之前必须拥有实际大小，否则可能出现底图无法渲染的问题。
-   `opts` **MapOptions** 地图初始化参数
    -   `opts.center` **(\[Number, Number] | LngLat)** 初始中心经纬度
    -   `opts.zoom` **Number** 地图显示的缩放级别，可以设置为浮点数；若center与level未赋值，地图初始化默认显示用户所在城市范围。
    -   `opts.rotation` **Number** 地图顺时针旋转角度，取值范围 [0-360]，默认值：0 (optional, default `0`)
    -   `opts.pitch` **Number** 俯仰角度，默认 0，最大值根据地图当前 zoom 级别不断增大，2D地图下无效 。 (optional, default `0`)
    -   `opts.viewMode` **String** 地图视图模式, 默认为‘2D’，可选’3D’，选择‘3D’会显示 3D 地图效果。 (optional, default `'2D'`)
    -   `opts.features` **Array&lt;String>** 设置地图上显示的元素种类, 支持'bg'（地图背景）、'point'（POI点）、'road'（道路）、'building'（建筑物） (optional, default `['bg','point','road','building']`)
    -   `opts.layers` **Array&lt;Layer>** 地图图层数组，数组可以是图层 中的一个或多个，默认为普通二维地图。
        当叠加多个[图层][15]时，普通二维地图需通过实例化一个TileLayer类实现。
        如果你希望创建一个默认底图图层，使用 AMap.createDefaultLayer()
    -   `opts.zooms` **\[Number, Number]** 地图显示的缩放级别范围, 默认为[2, 20]，取值范围[2 ~ 30] (optional, default `[2,20]`)
    -   `opts.dragEnable` **Boolean** 地图是否可通过鼠标拖拽平移, 默认为 true。此属性可被 setStatus/getStatus 方法控制 (optional, default `true`)
    -   `opts.zoomEnable` **Boolean** 地图是否可缩放，默认值为 true。此属性可被 setStatus/getStatus 方法控制 (optional, default `true`)
    -   `opts.jogEnable` **Boolean** 地图是否使用缓动效果，默认值为true。此属性可被setStatus/getStatus 方法控制 (optional, default `true`)
    -   `opts.pitchEnable` **Boolean** 是否允许设置俯仰角度, 3D 视图下为 true, 2D 视图下无效。 (optional, default `true`)
    -   `opts.rotateEnable` **Boolean** 地图是否可旋转, 图默认为true (optional, default `true`)
    -   `opts.animateEnable` **Boolean** 地图平移过程中是否使用动画（如调用panBy、panTo、setCenter、setZoomAndCenter等函数,
        将对地图产生平移操作, 是否使用动画平移的效果）, 默认为true, 即使用动画 (optional, default `true`)
    -   `opts.keyboardEnable` **Boolean** 地图是否可通过键盘控制, 默认为true, 方向键控制地图平移，"+"和"-"可以控制地图的缩放,
        Ctrl+“→”顺时针旋转，Ctrl+“←”逆时针旋转。此属性可被setStatus/getStatus 方法控制 (optional, default `true`)
    -   `opts.doubleClickZoom` **Boolean** 地图是否可通过双击鼠标放大地图, 默认为true。此属性可被setStatus/getStatus 方法控制 (optional, default `true`)
    -   `opts.scrollWheel` **Boolean** 地图是否可通过鼠标滚轮缩放浏览，默认为true。此属性可被setStatus/getStatus 方法控制 (optional, default `true`)
    -   `opts.touchZoom` **Boolean** 地图在移动终端上是否可通过多点触控缩放浏览地图，默认为true。关闭手势缩放地图，请设置为false。 (optional, default `true`)
    -   `opts.touchZoomCenter` **Boolean** 可缺省，当touchZoomCenter=1的时候，手机端双指缩放的以地图中心为中心，否则默认以双指中间点为中心。 (optional, default `1`)
    -   `opts.showLabel` **Boolean** 是否展示地图文字和 POI 信息。 (optional, default `true`)
    -   `opts.defaultCursor` **String** 地图默认鼠标样式。参数 defaultCursor 应符合 CSS 的 cursor 属性规范。
    -   `opts.isHotspot` **Boolean** 是否开启地图热点和标注的 hover 效果。PC端默认是true, 移动端默认是 false。
    -   `opts.mapStyle` **String** 设置地图的显示样式，目前支持两种地图样式：
        第一种：自定义地图样式，如 "amap://styles/d6bf8c1d69cea9f5c696185ad4ac4c86"
        可前往地图自定义平台定制自己的个性地图样式；
        第二种：官方样式模版,如"amap://styles/grey"。
        其他模版样式及自定义地图的使用说明见开发指南
    -   `opts.wallColor` **(String \| Array&lt;Number>)** 地图楼块的侧面颜色
    -   `opts.roofColor` **(String \| Array&lt;Number>)** 地图楼块的顶面颜色
    -   `opts.showBuildingBlock` **Boolean** 是否展示地图 3D 楼块，默认 true (optional, default `true`)
    -   `opts.showIndoorMap` **Boolean** 是否自动展示室内地图，默认是 false (optional, default `false`)
    -   `opts.skyColor` **(String \| Array&lt;Number>)** 天空颜色，3D 模式下带有俯仰角时会显示
    -   `opts.labelRejectMask` **Boolean** 文字是否拒绝掩模图层进行掩模 (optional, default `false`)
    -   `opts.mask` **Array&lt;Number>** 为 Map 实例指定掩模的路径，各图层将只显示路径范围内图像，3D视图下有效。
        格式为一个经纬度的一维、二维或三维数组。 </br> [相关示例][16] </br>
        一维数组时代表一个普通多边形路径，如: </br>
        [lng1,lat1], [lng2,lat2], [lng3,lat3]]
        二维数组时代表一个带洞的多边形路径，如: </br>
        \[[lng4,lat4], [lng5,lat5], [lng6,lat6]],
        \[[lng7,lat7], [lng8,lat8], [lng9,lat9]]
        ]
        三维数组时代表多个多边形路径，如: </br>
        \[
        \[[lng1,lat1], [lng2,lat2], [lng3,lat3]], // 一个普通多边形
        \[ //一个带洞多边形
        \[[lng4,lat4], [lng5,lat5], [lng6,lat6]],
        \[[lng7,lat7], [lng8,lat8], [lng9,lat9]]
        ]
        ]
    -   `opts.WebGLParams` **any** 额外配置的WebGL参数 eg: preserveDrawingBuffer (optional, default `{}`)

### Examples

```javascript
var map = new AMap.Map('map', {
  viewMode: '3D',
  center: [116.397083, 39.874531],
  layers: [AMap.createDefaultLayer()],  // layers 字段为空或者不赋值将会自动创建默认底图。
  zoom: 12,
})
```

### resize

重新计算容器大小

### setCenter

设置中心点 </br>
[相关示例][17]

#### Parameters

-   `center` **(\[number, number] | LngLat)** 中心点经纬度
-   `immediately` **Boolean** 是否立即过渡到目标位置 (optional, default `false`)
-   `duration` **Number?** 如果使用动画过度，动画过度的时长控制，单位 ms，默认值是内部自动计算的一个动态值。

### setZoomAndCenter

地图缩放至指定级别并以指定点为地图显示中心点 </br>
[相关示例][18]

#### Parameters

-   `zoom` **Number** 缩放等级
-   `center` **(LngLat | \[number, number])** 地图中心点位置
-   `immediately` **Boolean** 是否立即过渡到目位置 (optional, default `false`)
-   `duration` **Number?** 如果使用动画过度，动画过度的时长控制，单位 ms，默认值是内部自动计算的一个动态值。

### getBounds

获取当前地图视图范围/可视区域。 </br>
[相关示例][19]

Returns **Bounds** 边界经纬度

### getCenter

获取地图中心点经纬度坐标值。 </br>
[相关示例][21]

Returns **LngLat** 地图中心点经纬度

### setZoom

设置地图显示的缩放级别，参数 zoom 可设范围：[2, 30]

#### Parameters

-   `zoom` **Number** 地图缩放等级
-   `immediately` **Boolean** 是否立即过渡到目标位置 (optional, default `false`)
-   `duration` **Number?** 如果使用动画过度，动画过度的时长控制，单位 ms，默认值是内部自动计算的一个动态值。

### getZoom

获取当前地图缩放级别, 默认取值范围为[2, 20]

#### Parameters

-   `digits` **Number** zoom级别的小数位精度，缺省为2

Returns **Number** 地图缩放等级

### zoomIn

地图放大一级显示

### zoomOut

地图缩小一级显示

### getPitch

获取地图当前俯仰角

Returns **Number** 角度

### setPitch

设置地图俯仰角

#### Parameters

-   `Pitch` **Number** 角度
-   `immediately` **Boolean** 是否立即过渡到目标位置 (optional, default `false`)
-   `duration` **Number?** 如果使用动画过度，动画过度的时长控制，单位 ms，默认值是内部自动计算的一个动态值。

### getRotation

获取地图顺时针旋转角度, 范围: [0 ~ 360]

Returns **Number** 旋转角度值

### setRotation

设置地图顺时针旋转角度, 旋转原点为地图容器中心点, 取值范围: 任意数字

#### Parameters

-   `rotation` **Number** 旋转角度
-   `immediately` **Boolean** 是否立即过渡到目标位置 (optional, default `false`)
-   `duration` **Number?** 动画过度的时长控制，单位 ms，默认值是内部自动计算的一个动态值。

### setBounds

指定当前地图显示范围，参数 bounds 为指定的范围

#### Parameters

-   `bounds` **(Array&lt;number> | Bounds)** 经纬度范围
-   `immediately` **boolean** 立即缩放到指定位置 (optional, default `false`)
-   `avoid` **Array&lt;number>** 距离边框的内边距，顺序：上、下、左、右 (optional, default `[0,0,0,0]`)

### panTo

地图中心点平移至指定点位置

#### Parameters

-   `lnglat` **(\[number, number] | LngLat)** 
-   `duration` **Number?** 动画过度的时长控制，单位 ms，默认值是内部自动计算的一个动态值。

### getContainer

返回地图对象的容器

Returns **HTMLElement** 地图 DOM 容器

### getSize

获取地图容器尺寸，单位：像素

Returns **Size** 地图容器尺寸

### panBy

以像素为单位, 沿 x 方向和 y 方向移动地图, x 向右为正, y 向下为正

#### Parameters

-   `x` **Number** 横轴方向
-   `y` **Number** 纵轴方向
-   `duration` **Number?** 如果使用动画过度，动画过度的时长控制，单位 ms，默认值是内部自动计算的一个动态值。

### addLayer

添加图层到地图上

#### Parameters

-   `layer` **Layer** 地图图层对象

### removeLayer

从地图上移除图层

#### Parameters

-   `layer` **Layer** 地图图层

### setLayers

将多个图层一次替代地图上原有图层，会移除地图原有图层

#### Parameters

-   `layers` **Array&lt;Layer>** 地图图层数组

### getLayers

获取地图图层数组，数组为一个或多个图层

Returns **Array&lt;Layer>** 地图图层数组

### add

添加覆盖物/图层。参数为单个覆盖物/图层，或覆盖物/图层的数组。

#### Parameters

-   `features` **(VectorOverlay | Array&lt;any>)** 覆盖物对象或者数组

### getStatus

获取当前地图状态信息，包括是否可鼠标拖拽移动地图、地图是否可缩放、地图是否可旋转（rotateEnable）、
是否可双击放大地图、是否可以通过键盘控制地图旋转（keyboardEnable）等

Returns **object** 地图状态信息映射集合

### remove

删除覆盖物/图层。参数为单个覆盖物/图层，或覆盖物/图层的数组。

#### Parameters

-   `features` **(Overlay | Layer \| Array&lt;(Overlay | Layer)>)** 覆盖物对象或者数组

### setStatus

设置当前地图显示状态，包括是否可鼠标拖拽移动地图、地图是否可缩放、地图是否可旋转（rotateEnable）、
是否可双击放大地图、是否可以通过键盘控制地图旋转（keyboardEnable）等，
[相关示例][24]

#### Parameters

-   `status` **object** 地图状态值映射集合

### lngLatToCoords

经纬度转莫卡托坐标（单位：米）

#### Parameters

-   `lnglat` **(\[number, number] | LngLat)** 经纬度

Returns **any** 莫卡托坐标（单位：米）

### coordsToLngLat

莫卡托坐标（单位：米）转经纬度

#### Parameters

-   `coords` **(\[number, number])** 莫卡托坐标（单位：米）

Returns **any** 经纬度

### lngLatToContainer

地图经纬度坐标转为地图容器像素坐标 </br>
[相关示例][25]

#### Parameters

-   `lnglat` **(Array&lt;number> | LngLat)** 经纬度

Returns **Pixel** 容器像素坐标

### getDefaultCursor

获取地图默认鼠标指针样式

Returns **string** 地图鼠标指针样式

### setDefaultCursor

设置地图默认鼠标指针样式

#### Parameters

-   `cursor` **string** 设置鼠标指针默认样式，参数cursor应符合CSS的cursor属性规范。可为CSS标注中的光标样式，
    如：setCursor(“pointer”)等；或者自定义的光标样式，
    如：setCursor("url('[https://lbs.amap.com/webapi/static/Images//0.png'][26]),pointer")

### containerToLngLat

地图容器坐标转换成经纬度 </br>
[相关示例][25]

#### Parameters

-   `pixel` **(Array&lt;number> | Pixel)** 容器像素坐标

Returns **LngLat** 转换成功的经纬度

### coordToContainer

莫卡托（单位：米）转成地图容器坐标

#### Parameters

-   `coord` **Array&lt;Number>** 莫卡托坐标（单位：米）

Returns **Array&lt;Number>** 容器像素坐标

### destroy

注销地图对象，并清空地图容器

### containerToCoord

地图容器坐标转成莫卡托（单位：米）

#### Parameters

-   `pixel` **(Array&lt;Number> | Pixel)** 容器像素坐标

Returns **Array&lt;Number>** 莫卡托坐标（单位：米）

### pixelToLngLat

平面地图像素坐标转换为地图经纬度坐标

#### Parameters

-   `pixel` **(Array&lt;number> | Pixel)** 像素坐标
-   `zoom` **Number?** 某个地图级别

Returns **LngLat** 

### getLimitBounds

获取Map的限制区域

### lngLatToPixel

经纬度坐标转换成平面地图像素坐标

#### Parameters

-   `lnglat` **(Array&lt;number> | LngLat)** 经纬度
-   `zoom` **Number?** 某个地图级别，默认是地图当前级别

Returns **Pixel** 转换后的平面像素坐标

### setLimitBounds

设置 Map 的限制区域，设定区域限制后，传入参数为限制的 Bounds。地图仅在区域内可拖拽
[相关示例][27]

### clearLimitBounds

清除 Map 的限制区域

### getZooms

获取地图缩放等级范围

Returns **\[number, number]** zooms

### setZooms

设置地图缩放等级范围

#### Parameters

-   `zooms` **\[number, number]** 

### getResolution

获取指定位置的地图分辨率，单位：米/像素。
参数point有指定值时，返回指定点地图分辨率，point缺省时，默认返回当前地图中心点位置的分辨率

Returns **Number** 分辨率

### getScale

获取当前地图比例尺。表示当前屏幕距离一米代表实际距离多少米

#### Parameters

-   `dpi` **Number** 

Returns **Number** 比例尺的值

### getCity

获取地图中心点所在区域，回调函数返回对象属性分别对应为{省，市，区/县} </br>
[相关示例][28]

#### Parameters

-   `getCityCallBack` **Function** 查询成功的回调函数
-   `lnglat` **Array&lt;Number>** 查询的经纬度

### setCity

按照行政区名称或adcode来设置地图显示的中心点。 </br>
行政区名称支持中国、省、市、区/县名称，如遇重名的情况，会按城市编码表顺序返回第一个。adcode请在城市编码表中查询。 </br>
建议不要同时使用center/setCenter()和setCity()，如一起使用程序将以setCity()作为最后结果。 </br>
[相关示例][29]

#### Parameters

-   `cityName` **String** 城市名称

### setFitView

根据地图上添加的覆盖物分布情况，自动缩放地图到合适的视野级别，参数均可缺省。</br>
overlayList为覆盖物数组，缺省时为当前地图上添加的所有覆盖物图层，</br>
immediately代表是否需要动画过程，avoid代表上下左右的像素避让宽度，maxZoom代表fitView之后的最大级 </br>
[相关示例][30]

#### Parameters

-   `overlays` **Array&lt;Overlay>** 覆盖物
-   `immediately` **Boolean** 是否立即过渡 (optional, default `false`)
-   `avoid` **Array&lt;Number>** 四周边距，上、下、左、右 (optional, default `[60,60,60,60]`)
-   `maxZoom` **Number** 最大 zoom 级别 (optional, default `zooms[1]`)

#### Examples

```javascript
var map = new AMap.Map({
    zoom: 10,
});

var marker = new AMap.Marker({
    map: map,
    position: [112, 30],
    icon: "https://webapi.amap.com/images/car.png",
    offset: new AMap.Pixel(-26, -13),
});
var marker1 = new AMap.Marker({
    map: map,
    position: [110, 31],
    icon: "https://webapi.amap.com/images/car.png",
    offset: new AMap.Pixel(-26, -13),
});
map.setFitView(
    [marker, marker1],  // 覆盖物数组
    false,  // 动画过渡到制定位置
    [60, 60, 60, 60],  // 周围边距，上、下、左、右
    10,  // 最大 zoom 级别
);
```

Returns **Bounds** bounds 新的地图视口范围

### getFitZoomAndCenterByOverlays

根据 overlays 计算出合适的中心点和 zoom 级别

#### Parameters

-   `overlays` **Array&lt;Overlay>** 覆盖物
-   `avoid` **Array&lt;Number>** 四周边距，上、下、左、右 (optional, default `[0,0,0,0]`)
-   `maxZoom` **Number** 最大 zoom 级别 (optional, default `CoreMap.defaultZooms[1]`)

Returns **\[number, LngLat]** zoom 级别和中心点经纬度

### getFitZoomAndCenterByBounds

根据 bounds 计算出合适的中心点和 zoom 级别

#### Parameters

-   `bounds` **(Array&lt;number> | Bounds)** 需要计算的范围
-   `avoid` **Array&lt;Number>** 四周边距，上、下、左、右 (optional, default `[0,0,0,0]`)
-   `maxZoom` **Number** 最大 zoom 级别 (optional, default `20`)

Returns **\[number, LngLat]** zoom 级别和中心点经纬度

### addControl

添加控件。参数可以是插件列表中的任何插件对象，如：ToolBar、OverView、Scale等 </br>
[相关示例][31]

#### Parameters

-   `control` **Control** 控件对象

### removeControl

移除地图上的指定控件 </br>
[相关示例][31]

#### Parameters

-   `control` **Control** 控件对象

### setMapStyle

设置地图的显示样式，目前支持两种地图样式： </br>
第一种：自定义地图样式，如 "amap://styles/d6bf8c1d69cea9f5c696185ad4ac4c86" </br>
可前往地图自定义平台定制自己的个性地图样式； </br>
第二种：官方样式模版,如 "amap://styles/grey"。 </br>
其他模版样式及自定义地图的使用说明见 [开发指南][33] </br>
[相关示例][34] </br>

#### Parameters

-   `value` **String** 

### getMapStyle

获取地图显示样式

### getAllOverlays

返回添加的覆盖物对象，可选类型包括marker、circle、polyline、polygon； </br>
Type可缺省，缺省时返回所有覆盖物（marker、circle、polyline、polygon）。 </br>
返回结果不包含官方覆盖物等，比如定位marker，周边搜索圆等 </br>
[相关示例][35]

#### Parameters

-   `type` **String?** 可选，覆盖物类型

Returns **Array&lt;Overlay>** 覆盖物数组

### clearMap

删除地图上所有的覆盖物

### clearInfoWindow

清除地图上的信息窗体。

### getFeatures

获取地图显示元素种类

Returns **Array&lt;String>** 返回 features 的集合，可能有 bg（地图背景）、point（兴趣点）、
road（道路）、building（建筑物）

### setFeatures

设置地图上显示的元素种类，支持bg（地图背景）、point（兴趣点）、 </br>
road（道路）、building（建筑物） </br>
[相关示例][36]

#### Parameters

-   `features` **Array&lt;string>** 类型数组

#### Examples

```javascript
map.setFeatures(['bg', 'road']);
```

### setMask

#### Parameters

-   `maskPath` **Array&lt;Array&lt;number>>** 掩模范围
-   `maskPath` **Array&lt;Number>** 掩模范围

### setLabelRejectMask

设置文字是否拒绝掩模，true：不进行掩模，false：掩模

#### Parameters

-   `reject` **boolean** 是否拒绝掩模

### customCoords

### mapStyle

获取审图号

## MapsEvent

此对象用于表示地图、覆盖物、叠加层上的各种鼠标事件返回，包含以下字段：

Type: Object

### Properties

-   `lnglat` **LngLat** 发生事件时光标所在处的经纬度坐标。
-   `pixel` **Pixel** 发生事件时光标所在处的像素坐标。
-   `type` **string** 事件类型。
-   `target` **Object** 发生事件的目标对象，不同类型返回target不同。例如，事件对象是Marker，则target表示目标对象为Marker，事件对象是其他，则随之改变。
