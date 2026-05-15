## 矢量图形

用于在地图上绘制线、面等矢量地图要素的类型


## Polygon

构造多边形对象，通过PolygonOptions指定多边形样式

### Parameters

-   `opts` **PolygonOptions** 
    -   `opts.path` **(Array&lt;LngLat> | Array&lt;Array&lt;LngLat>> | Array&lt;Array&lt;Array&lt;LngLat>>>)** 多边形轮廓线的节点坐标数组。
        支持 单个普通多边形({Array<LngLat>})，单个带孔多边形({Array&lt;Array<LngLat>>})，多个带孔多边形({Array&lt;Array&lt;Array<LngLat>>>})
    -   `opts.zIndex` **number** 多边形覆盖物的叠加顺序。地图上存在多个多边形覆盖物叠加时，通过该属性使级别较高的多边形覆盖物在上层显示 (optional, default `10`)
    -   `opts.bubble` **boolean** 是否将覆盖物的鼠标或touch等事件冒泡到地图上（自v1.3 新增） (optional, default `false`)
    -   `opts.cursor` **string?** 指定鼠标悬停时的鼠标样式，自定义cursor，IE仅支持cur/ani/ico格式，Opera不支持自定义cursor
    -   `opts.strokeColor` **string** 线条颜色，使用16进制颜色代码赋值。默认值为#00D3FC (optional, default `#00D3FC`)
    -   `opts.strokeOpacity` **number** 轮廓线透明度，取值范围[0,1]，0表示完全透明，1表示不透明。默认为0.9 (optional, default `0.9`)
    -   `opts.strokeWeight` **number** 轮廓线宽度 (optional, default `2`)
    -   `opts.fillColor` **string** 多边形填充颜色，使用16进制颜色代码赋值，如：#00B2D5 (optional, default `#00B2D5`)
    -   `opts.fillOpacity` **number** 多边形填充透明度，取值范围[0,1]，0表示完全透明，1表示不透明。默认为0.5 (optional, default `0.5`)
    -   `opts.draggable` **boolean** 设置多边形是否可拖拽移动，默认为false (optional, default `false`)
    -   `opts.extrusionHeight` **number** 设置多边形是否拉伸为的多面体厚度值。默认值为0 (optional, default `0`)
    -   `opts.wallColor` **(Array&lt;String> | String)** 多面体侧面颜色，支持 rgba、rgb、十六进制等。默认为#00D3FC (optional, default `#00D3FC`)
    -   `opts.roofColor` **(Array&lt;String> | String)** 多面体顶面颜色，支持 rgba、rgb、十六进制等。默认为#00B2D5 (optional, default `#00B2D5`)
    -   `opts.extData` **object?** 用户自定义属性，支持JavaScript API任意数据类型，如Polygon的id等。
    -   `opts.strokeStyle` **(`"solid"` \| `"dashed"`)** 轮廓线样式，实线:solid，虚线:dashed (optional, default `solid`)
    -   `opts.strokeDasharray` **Array&lt;number>?** 勾勒形状轮廓的虚线和间隙的样式，此属性在strokeStyle 为dashed 时有效， 此属性在ie9+浏览器有效 取值：
        实线：[0,0,0]
        虚线：[10,10] ，[10,10] 表示10个像素的实线和10个像素的空白（如此反复）组成的虚线
        点画线：[10,2,10]， [10,2,10] 表示10个像素的实线和2个像素的空白 + 10个像素的实线和10个像素的空白 （如此反复）组成的虚线

### hide

隐藏多边形

### show

显示多边形

### getExtData

获取用户自定义属性

Returns **Object** 

### setExtData

设置用户自定义属性，支持JavaScript API任意数据类型

#### Parameters

-   `extData` **Object** 

### getOptions

获取多边形的属性

Returns **Object** [多边形配置][84]

### setOptions

修改多边形属性（样式风格，包括组成多边形轮廓线的节点、轮廓线样式等。属性详情参看PolygonOptions列表）

#### Parameters

-   `optsArg` **PolygonOptions** 

### getPath

获取多边形轮廓线节点数组。

Returns **(Array&lt;LngLat> | Array&lt;Array&lt;LngLat>> | Array&lt;Array&lt;Array&lt;LngLat>>>)** 返回路径

### setExtrusionHeight

设置多面体拉伸高度值

### getExtrusionHeight

获取多边形当前拉伸高度值

Returns **number** 返回路径

### getBounds

获取当前多边形的矩形范围对象。

Returns **Bounds** 

### getArea

获取多边形的面积（单位：平方米）

Returns **number** 

### destroy

销毁内存-多边形

### contains

判断坐标是否在多边形内

#### Parameters

-   `originPoint` **LngLatLike** 

Returns **boolean** true 包含，false 不包含

### setPath

多边形轮廓线的节点坐标数组。支持 单个普通多边形({Array<LngLat>})，单个带孔多边形({Array&lt;Array<LngLat>>})，多个带孔多边形({Array&lt;Array&lt;Array<LngLat>>>})

#### Parameters

-   `path` **(Array&lt;LngLatLike> | Array&lt;Array&lt;LngLatLike>> | Array&lt;Array&lt;Array&lt;LngLatLike>>>)?** 

### generateBuffer

#### Parameters

-   `gl`  

### getStatus

获取折线绘制状态的时间点

Returns **any** 

## Polyline

构造折线对象，支持 lineString 和 MultiLineString

### Parameters

-   `opts`  {PolylineOptions}
    -   `opts.path` **(Array&lt;LngLat> | Array&lt;Array&lt;LngLat>>)** polyline 路径，支持 lineString 和 MultiLineString
    -   `opts.zIndex` **number** 多边形覆盖物的叠加顺序。地图上存在多个多边形覆盖物叠加时，通过该属性使级别较高的多边形覆盖物在上层显示 (optional, default `10`)
    -   `opts.bubble` **boolean** 是否将覆盖物的鼠标或touch等事件冒泡到地图上（自v1.3 新增） (optional, default `false`)
    -   `opts.cursor` **string?** 指定鼠标悬停时的鼠标样式，自定义cursor，IE仅支持cur/ani/ico格式，Opera不支持自定义cursor
    -   `opts.strokeColor` **string** 线条颜色，使用16进制颜色代码赋值。默认值为#00D3FC (optional, default `#00D3FC`)
    -   `opts.strokeOpacity` **number** 轮廓线透明度，取值范围[0,1]，0表示完全透明，1表示不透明。默认为0.5 (optional, default `0.5`)
    -   `opts.strokeWeight` **number** 轮廓线宽度 (optional, default `2`)
    -   `opts.borderWeight` **number** 描边线宽度 (optional, default `2`)
    -   `opts.isOutline` **boolean** 是否显示描边,默认false (optional, default `false`)
    -   `opts.borderWeight` **number** 描边的宽度，默认为1 (optional, default `1`)
    -   `opts.outlineColor` **string** 线条描边颜色，此项仅在isOutline为true时有效，默认：#00B2D5 (optional, default `#00B2D5`)
    -   `opts.draggable` **boolean** 设置多边形是否可拖拽移动，默认为false (optional, default `false`)
    -   `opts.extData` **object?** 用户自定义属性，支持JavaScript API任意数据类型，如Polygon的id等
    -   `opts.strokeStyle` **(`"solid"` \| `"dashed"`)** 轮廓线样式，实线:solid，虚线:dashed (optional, default `solid`)
    -   `opts.strokeDasharray` **Array&lt;number>?** 勾勒形状轮廓的虚线和间隙的样式，此属性在strokeStyle 为dashed 时有效， 此属性在ie9+浏览器有效 取值：
        实线：[0,0,0]
        虚线：[10,10] ，[10,10] 表示10个像素的实线和10个像素的空白（如此反复）组成的虚线
        点画线：[10,2,10]， [10,2,10] 表示10个像素的实线和2个像素的空白 + 10个像素的实线和10个像素的空白 （如此反复）组成的虚线
    -   `opts.lineJoin` **(`"miter"` \| `"round"` \| `"bevel"`)** 折线拐点的绘制样式，默认值为'miter'尖角，其他可选值：'round'圆角、'bevel'斜角 (optional, default `miter`)
    -   `opts.lineCap` **(`"butt"` \| `"round"` \| `"square"`)** 折线两端线帽的绘制样式，默认值为'butt'无头，其他可选值：'round'圆头、'square'方头 (optional, default `butt`)
    -   `opts.geodesic` **boolean** 是否绘制成大地线，默认false (optional, default `false`)
    -   `opts.showDir` **boolean** 是否延路径显示白色方向箭头,默认false。建议折线宽度大于6时使用-   @param {boolean} [opts.animate=false] 是否使用纹理动画，开启后，如果线有纹理，将会有流动动画
        -   @param {boolean} [opts.speed=100] 纹理流动动画的速度，单位 m/s (optional, default `false`)

### hide

隐藏折线

### show

显示折线

### getExtData

获取用户自定义属性

Returns **Object** 

### getOptions

获取线的属性

Returns **PolylineOptions** 

### getPath

获取折线路径的节点数组。

Returns **(Array&lt;LngLat> | Array&lt;Array&lt;LngLat>>)** 

### setExtData

设置用户自定义属性，支持JavaScript API任意数据类型

#### Parameters

-   `extData` **Object** 

### destroy

销毁内存-折线

### getBounds

获取当前折线的矩形范围对象

Returns **(Bounds \| undefined)** 

### setPath

设置组成该折线的节点数组,支持单条折线(LngLatLike\[]) 多条折线（LngLatLike[][]）

#### Parameters

-   `path` **(Array&lt;LngLatLike> | Array&lt;Array&lt;LngLatLike>>)?** 

Returns **any** 

### moveWithPos

#### Parameters

-   `dx`  
-   `dy`  

### getLength

获取折线的总长度（单位：米）

Returns **number** 

### getEndDistance

### generateBuffer

#### Parameters

-   `gl`  

### setOptions

修改折线属性（包括路径的节点、线样式、是否绘制大地线等。属性详情参看PolylineOptions列表)

#### Parameters

-   `optsArg` **PolylineOptions** 

### contains

判断坐标是否在折线内

#### Parameters

-   `point` **LngLatLike** 

Returns **boolean** 

### getStatus

获取折线绘制状态的时间点

Returns **any** 

## BezierCurve

**Extends \_Polyline.CombinePolyline**

### Parameters

-   `opts`   (optional, default `{}`)

### setOptions

修改折线属性（包括路径的节点、线样式、是否绘制大地线等。属性详情参看 BezierCurveOptions 列表）

#### Parameters

-   `optsArg` **BezierCurveOptions** 

### generateBuffer

#### Parameters

-   `gl`  

### getPath

获取贝塞尔曲线路径的节点数组

Returns **(Array&lt;Array&lt;number>> | Array&lt;Array&lt;Array&lt;number>>>)** 

### setPath

设置组成该折线的节点数组

#### Parameters

-   `path` **(Array&lt;Array&lt;number>> | Array&lt;Array&lt;Array&lt;number>>>)** 贝瑟尔曲线的路径。描述为一个二维数组规则如下：第一个元素是起点，
    之后的元素同时描述控制点和途经点，之后每个元素可以有0个到2个控制点
    控制点在前，途经点在最后
    \[
      [lng,lat],//起点0
      [lng,lat,lng,lat,lng,lat],//控制点、控制点、途经点2
      [lng,lat,lng,lat]//控制点、途经点3
    ]
    或者
    \[
      \[ [lng,lat] ],//起点0
      \[ [lng,lat] , [lng,lat] ],//控制点、途经点1
      \[ [lng,lat] , [lng,lat] , [lng,lat]],//控制点、控制点、途经点2
      \[ [lng,lat] , [lng,lat] ]//控制点、途经点3
    ]

### getBounds

获取当前折线的矩形范围对象

Returns **(Bounds \| undefined)** 

### getBounds

获取当前折线的矩形范围对象

Returns **(Bounds \| undefined)** Bounds对象，未设置路径时为 undefined

### hide

隐藏贝塞尔线

### show

显示贝塞尔曲线

### getExtData

获取用户自定义属性

Returns **Object** 

### setExtData

设置用户自定义属性，支持JavaScript API任意数据类型

#### Parameters

-   `extData` **Object** 

### destroy

销毁内存-贝塞尔曲线

### getOptions

获取线的属性

Returns **BezierCurveOptions** 

### contains

判断坐标是否在曲线内

#### Parameters

-   `point` **LngLatLike** 

Returns **boolean** 

### getLength

获取曲线的总长度（单位：米）

Returns **number** 

## BezierCurve

贝塞尔曲线

### Parameters

-   `opts` **BezierCurveOptions** BezierCurve配置项
    -   `opts.path` **Array** 贝瑟尔曲线的路径。描述为一个二维数组规则如下：第一个元素是起点，
        之后的元素同时描述控制点和途经点，之后每个元素可以有0个到2个控制点
        控制点在前，途经点在最后
        \[
          [lng,lat],//起点0
          [lng,lat,lng,lat,lng,lat],//控制点、控制点、途经点2
          [lng,lat,lng,lat]//控制点、途经点3
        ]
        或者
        \[
          \[ [lng,lat] ],//起点0
          \[ [lng,lat] , [lng,lat] ],//控制点、途经点1
          \[ [lng,lat] , [lng,lat] , [lng,lat]],//控制点、控制点、途经点2
          \[ [lng,lat] , [lng,lat] ]//控制点、途经点3
        ]
    -   `opts.path` **(Array&lt;LngLat> | Array&lt;Array&lt;LngLat>>)** polyline 路径，支持 lineString 和 MultiLineString
    -   `opts.zIndex` **number** 多边形覆盖物的叠加顺序。地图上存在多个多边形覆盖物叠加时，通过该属性使级别较高的多边形覆盖物在上层显示 (optional, default `10`)
    -   `opts.bubble` **boolean** 是否将覆盖物的鼠标或touch等事件冒泡到地图上（自v1.3 新增） (optional, default `false`)
    -   `opts.cursor` **string?** 指定鼠标悬停时的鼠标样式，自定义cursor，IE仅支持cur/ani/ico格式，Opera不支持自定义cursor
    -   `opts.strokeColor` **string** 线条颜色，使用16进制颜色代码赋值。默认值为#00D3FC (optional, default `#00D3FC`)
    -   `opts.strokeOpacity` **number** 轮廓线透明度，取值范围[0,1]，0表示完全透明，1表示不透明。默认为0.5 (optional, default `0.5`)
    -   `opts.strokeWeight` **number** 轮廓线宽度 (optional, default `2`)
    -   `opts.borderWeight` **number** 描边线宽度 (optional, default `2`)
    -   `opts.isOutline` **boolean** 是否显示描边,默认false (optional, default `false`)
    -   `opts.borderWeight` **number** 描边的宽度，默认为1 (optional, default `1`)
    -   `opts.outlineColor` **string** 线条描边颜色，此项仅在isOutline为true时有效，默认：#00B2D5 (optional, default `#00B2D5`)
    -   `opts.draggable` **boolean** 设置多边形是否可拖拽移动，默认为false (optional, default `false`)
    -   `opts.extData` **object?** 用户自定义属性，支持JavaScript API任意数据类型，如Polygon的id等
    -   `opts.strokeStyle` **(`"solid"` \| `"dashed"`)** 轮廓线样式，实线:solid，虚线:dashed (optional, default `solid`)
    -   `opts.strokeDasharray` **Array&lt;number>?** 勾勒形状轮廓的虚线和间隙的样式，此属性在strokeStyle 为dashed 时有效， 此属性在ie9+浏览器有效 取值：
        实线：[0,0,0]
        虚线：[10,10] ，[10,10] 表示10个像素的实线和10个像素的空白（如此反复）组成的虚线
        点画线：[10,2,10]， [10,2,10] 表示10个像素的实线和2个像素的空白 + 10个像素的实线和10个像素的空白 （如此反复）组成的虚线
    -   `opts.lineJoin` **(`"miter"` \| `"round"` \| `"bevel"`)** 折线拐点的绘制样式，默认值为'miter'尖角，其他可选值：'round'圆角、'bevel'斜角 (optional, default `miter`)
    -   `opts.lineCap` **(`"butt"` \| `"round"` \| `"square"`)** 折线两端线帽的绘制样式，默认值为'butt'无头，其他可选值：'round'圆头、'square'方头 (optional, default `butt`)
    -   `opts.geodesic` **boolean** 是否绘制成大地线，默认false (optional, default `false`)
    -   `opts.showDir` **boolean** 是否延路径显示白色方向箭头,默认false。建议折线宽度大于6时使用 (optional, default `false`)

### setOptions

修改折线属性（包括路径的节点、线样式、是否绘制大地线等。属性详情参看 BezierCurveOptions 列表）

#### Parameters

-   `optsArg` **BezierCurveOptions** 

### generateBuffer

#### Parameters

-   `gl`  

### getPath

获取贝塞尔曲线路径的节点数组

Returns **(Array&lt;Array&lt;number>> | Array&lt;Array&lt;Array&lt;number>>>)** 

### setPath

设置组成该折线的节点数组

#### Parameters

-   `path` **(Array&lt;Array&lt;number>> | Array&lt;Array&lt;Array&lt;number>>>)** 贝瑟尔曲线的路径。描述为一个二维数组规则如下：第一个元素是起点，
    之后的元素同时描述控制点和途经点，之后每个元素可以有0个到2个控制点
    控制点在前，途经点在最后
    \[
      [lng,lat],//起点0
      [lng,lat,lng,lat,lng,lat],//控制点、控制点、途经点2
      [lng,lat,lng,lat]//控制点、途经点3
    ]
    或者
    \[
      \[ [lng,lat] ],//起点0
      \[ [lng,lat] , [lng,lat] ],//控制点、途经点1
      \[ [lng,lat] , [lng,lat] , [lng,lat]],//控制点、控制点、途经点2
      \[ [lng,lat] , [lng,lat] ]//控制点、途经点3
    ]

### getBounds

获取当前折线的矩形范围对象

Returns **(Bounds \| undefined)** 

### getBounds

获取当前折线的矩形范围对象

Returns **(Bounds \| undefined)** Bounds对象，未设置路径时为 undefined

### hide

隐藏贝塞尔线

### show

显示贝塞尔曲线

### getExtData

获取用户自定义属性

Returns **Object** 

### setExtData

设置用户自定义属性，支持JavaScript API任意数据类型

#### Parameters

-   `extData` **Object** 

### destroy

销毁内存-贝塞尔曲线

### getOptions

获取线的属性

Returns **BezierCurveOptions** 

### contains

判断坐标是否在曲线内

#### Parameters

-   `point` **LngLatLike** 

Returns **boolean** 

### getLength

获取曲线的总长度（单位：米）

Returns **number** 

## Circle

构造圆形对象，通过CircleOptions指定多边形样式

### Parameters

-   `opts` **CircleOptions** 
    -   `opts.center` **LngLat** 圆心位置
    -   `opts.radius` **number** 圆半径，单位:米
    -   `opts.zIndex` **number** 多边形覆盖物的叠加顺序。地图上存在多个多边形覆盖物叠加时，通过该属性使级别较高的多边形覆盖物在上层显示 (optional, default `10`)
    -   `opts.bubble` **boolean** 是否将覆盖物的鼠标或touch等事件冒泡到地图上（自v1.3 新增） (optional, default `false`)
    -   `opts.cursor` **string?** 指定鼠标悬停时的鼠标样式，自定义cursor，IE仅支持cur/ani/ico格式，Opera不支持自定义cursor
    -   `opts.strokeColor` **string** 轮廓线颜色，使用16进制颜色代码赋值。默认值为#00D3FC (optional, default `#00D3FC`)
    -   `opts.strokeOpacity` **number** 轮廓线透明度，取值范围[0,1]，0表示完全透明，1表示不透明。默认为0.9 (optional, default `0.9`)
    -   `opts.strokeWeight` **number** 轮廓线宽度 (optional, default `2`)
    -   `opts.fillColor` **string** 多边形填充颜色，使用16进制颜色代码赋值，如：#00B2D5 (optional, default `#00B2D5`)
    -   `opts.fillOpacity` **number** 多边形填充透明度，取值范围[0,1]，0表示完全透明，1表示不透明。默认为0.5 (optional, default `0.5`)
    -   `opts.draggable` **boolean** 设置多边形是否可拖拽移动，默认为false (optional, default `false`)
    -   `opts.extData` **object?** 用户自定义属性，支持JavaScript API任意数据类型，如Polygon的id等
    -   `opts.strokeStyle` **(`"solid"` \| `"dashed"`)** 轮廓线样式，实线:solid，虚线:dashed (optional, default `solid`)
    -   `opts.strokeDasharray` **Array&lt;number>?** 勾勒形状轮廓的虚线和间隙的样式，此属性在strokeStyle 为dashed 时有效， 此属性在ie9+浏览器有效 取值：
        实线：[0,0,0]
        虚线：[10,10] ，[10,10] 表示10个像素的实线和10个像素的空白（如此反复）组成的虚线
        点画线：[10,2,10]， [10,2,10] 表示10个像素的实线和2个像素的空白 + 10个像素的实线和10个像素的空白 （如此反复）组成的虚线

### svgDom

### svgDom

### setCenter

设置圆中心点

#### Parameters

-   `center` **LngLatLike** 

### setRadius

设置圆形的半径

#### Parameters

-   `radius` **number** 

### getCenter

获取圆中心点

Returns **LngLat** center

### getRadius

获取圆形的半径

Returns **number** radius

### generateBuffer

#### Parameters

-   `gl`  

### contains

判断指定点坐标是否在圆内

#### Parameters

-   `point` **LngLatLike** 

Returns **boolean** 

### setOptions

修改圆属性（样式风格，包括组成圆形轮廓线的节点、轮廓线样式等。属性详情参看CircleOptions列表）

#### Parameters

-   `optsArg` **CircleOptions** 

### hide

隐藏圆形

### show

显示圆形

### getExtData

获取用户自定义属性

Returns **Object** 

### setExtData

设置用户自定义属性，支持JavaScript API任意数据类型

#### Parameters

-   `extData` **Object** 

### destroy

销毁内存-圆形

### getArea

获取面积,平米

Returns **number** 

### getOptions

获取圆形的属性

Returns **CircleOptions** 

### getPath

获取圆面路径的节点数组

Returns **(Array&lt;LngLat> | Array&lt;Array&lt;LngLat>>)** 

## CircleMarker

构造圆形对象，通过CircleOptions指定多边形样式

### Parameters

-   `opts` **CircleMarkerOptions** 
    -   `opts.center` **LngLat** 圆心位置
    -   `opts.radius` **number** 圆半径，单位:px 最大值64
    -   `opts.zIndex` **number** 多边形覆盖物的叠加顺序。地图上存在多个多边形覆盖物叠加时，通过该属性使级别较高的多边形覆盖物在上层显示 (optional, default `10`)
    -   `opts.bubble` **boolean** 是否将覆盖物的鼠标或touch等事件冒泡到地图上（自v1.3 新增） (optional, default `false`)
    -   `opts.cursor` **string?** 指定鼠标悬停时的鼠标样式，自定义cursor，IE仅支持cur/ani/ico格式，Opera不支持自定义cursor
    -   `opts.strokeColor` **string** 轮廓线颜色，使用16进制颜色代码赋值。默认值为#00D3FC (optional, default `#00D3FC`)
    -   `opts.strokeOpacity` **number** 轮廓线透明度，取值范围[0,1]，0表示完全透明，1表示不透明。默认为0.9 (optional, default `0.9`)
    -   `opts.strokeWeight` **number** 轮廓线宽度 (optional, default `2`)
    -   `opts.fillColor` **string** 多边形填充颜色，使用16进制颜色代码赋值，如：#00B2D5 (optional, default `#00B2D5`)
    -   `opts.fillOpacity` **number** 多边形填充透明度，取值范围[0,1]，0表示完全透明，1表示不透明。默认为0.5 (optional, default `0.5`)
    -   `opts.draggable` **boolean** 设置多边形是否可拖拽移动，默认为false (optional, default `false`)
    -   `opts.extData` **object?** 用户自定义属性，支持JavaScript API任意数据类型，如Polygon的id等

### contains

判断指定点坐标是否在圆内

#### Parameters

-   `point` **LngLatLike** 

Returns **boolean** 

### hide

隐藏圆点

### setRadius

设置圆点的半径

#### Parameters

-   `radius` **number** 

### generateBuffer

### getCenter

获取圆点中心

Returns **LngLat** 

### getRadius

获取圆点的半径

Returns **number** 

### show

显示CircleMarker

### setOptions

修改圆点标记的属性（样式风格，包括轮廓线、填充色等。属性详情参看CircleMarkerOptions列表）

#### Parameters

-   `optsArg` **CircleMarkerOptions** 

### getOptions

获取圆点的属性

Returns **CircleMarkerOptions** 

### getExtData

获取用户自定义属性

Returns **Object** 

### setExtData

设置用户自定义属性，支持JavaScript API任意数据类型

#### Parameters

-   `extData` **Object** 

### destroy

销毁内存-CircleMarker

## Ellipse

**Extends \_Polygon.CombinePolygon**

### Parameters

-   `opts`   (optional, default `{}`)

### path

### svgDom

### setCenter

设置椭圆的中心点

#### Parameters

-   `center` **LngLatLike** 

### setRadius

设置椭圆的半径

#### Parameters

-   `radius` **\[number, number]** 

### getCenter

获取椭圆的圆心

Returns **LngLat** 

### getRadius

获取椭圆的半径

Returns **number** 

### generateBuffer

#### Parameters

-   `gl`  

### hide

隐藏椭圆

### setOptions

修改椭圆属性（样式风格，包括组成椭圆轮廓线的节点、轮廓线样式等。属性详情参看Ellipse

#### Parameters

-   `optsArg` **EllipseOptions** 

### show

显示椭圆

### getExtData

获取用户自定义属性

Returns **Object** 

### setExtData

设置用户自定义属性，支持JavaScript API任意数据类型

#### Parameters

-   `extData` **Object** 

### destroy

销毁内存-椭圆

### getArea

获取面积,平米

Returns **number** 

### contains

判断指定点坐标是否在椭圆内

#### Parameters

-   `point` **LngLatLike** 

### getOptions

获取椭圆的属性

Returns **EllipseOptions** 

### getPath

获取椭圆面路径的节点数组

Returns **(Array&lt;LngLat> | Array&lt;Array&lt;LngLat>>)** 

## Ellipse

构造多边形对象，通过EllipseOptions指定多边形样式

### Parameters

-   `opts` **EllipseOptions** 
    -   `opts.center` **LngLatLike** 椭圆圆心
    -   `opts.radius` **\[number, number]** 椭圆的半径，用2个元素的数组表示，单位：米
        如： radius: [1000, 2000] 表示横向半径是1000，纵向的半径是2000
        默认值：[1000, 1000]
    -   `opts.zIndex` **number** 椭圆覆盖物的叠加顺序。地图上存在多个多边形覆盖物叠加时，通过该属性使级别较高的多边形覆盖物在上层显示 (optional, default `10`)
    -   `opts.bubble` **boolean** 是否将覆盖物的鼠标或touch等事件冒泡到地图上 (optional, default `false`)
    -   `opts.cursor` **string?** 指定鼠标悬停时的鼠标样式，自定义cursor，IE仅支持cur/ani/ico格式，Opera不支持自定义cursor
    -   `opts.strokeColor` **string** 线条颜色，使用16进制颜色代码赋值。默认值为#00D3FC (optional, default `#00D3FC`)
    -   `opts.strokeOpacity` **number** 轮廓线透明度，取值范围[0,1]，0表示完全透明，1表示不透明。默认为0.9 (optional, default `0.9`)
    -   `opts.strokeWeight` **number** 轮廓线宽度 (optional, default `2`)
    -   `opts.fillColor` **string** 椭圆填充颜色，使用16进制颜色代码赋值，如：#00B2D5 (optional, default `#00B2D5`)
    -   `opts.fillOpacity` **number** 椭圆填充透明度，取值范围[0,1]，0表示完全透明，1表示不透明。默认为0.5 (optional, default `0.5`)
    -   `opts.draggable` **boolean** 设置椭圆是否可拖拽移动，默认为false (optional, default `false`)
    -   `opts.extData` **object?** 用户自定义属性，支持JavaScript API任意数据类型，如 id 等
    -   `opts.strokeStyle` **(`"solid"` \| `"dashed"`)** 轮廓线样式，实线:solid，虚线:dashed (optional, default `solid`)
    -   `opts.strokeDasharray` **Array&lt;number>?** 勾勒形状轮廓的虚线和间隙的样式，此属性在strokeStyle 为dashed 时有效， 此属性在ie9+浏览器有效 取值：
        实线：[0,0,0]
        虚线：[10,10] ，[10,10] 表示10个像素的实线和10个像素的空白（如此反复）组成的虚线
        点画线：[10,2,10]， [10,2,10] 表示10个像素的实线和2个像素的空白 + 10个像素的实线和10个像素的空白 （如此反复）组成的虚线

### path

### svgDom

### setCenter

设置椭圆的中心点

#### Parameters

-   `center` **LngLatLike** 

### setRadius

设置椭圆的半径

#### Parameters

-   `radius` **\[number, number]** 

### getCenter

获取椭圆的圆心

Returns **LngLat** 

### getRadius

获取椭圆的半径

Returns **number** 

### generateBuffer

#### Parameters

-   `gl`  

### hide

隐藏椭圆

### setOptions

修改椭圆属性（样式风格，包括组成椭圆轮廓线的节点、轮廓线样式等。属性详情参看Ellipse

#### Parameters

-   `optsArg` **EllipseOptions** 

### show

显示椭圆

### getExtData

获取用户自定义属性

Returns **Object** 

### setExtData

设置用户自定义属性，支持JavaScript API任意数据类型

#### Parameters

-   `extData` **Object** 

### destroy

销毁内存-椭圆

### getArea

获取面积,平米

Returns **number** 

### contains

判断指定点坐标是否在椭圆内

#### Parameters

-   `point` **LngLatLike** 

### getOptions

获取椭圆的属性

Returns **EllipseOptions** 

### getPath

获取椭圆面路径的节点数组

Returns **(Array&lt;LngLat> | Array&lt;Array&lt;LngLat>>)** 

## Rectangle

构造矩形对象，通过RectangleOptions指定多边形样式

### Parameters

-   `opts` **RectangleOptions** 
    -   `opts.map` **Map** 要显示该覆盖物的地图对象
    -   `opts.bounds` **Bounds** 矩形的范围
    -   `opts.zIndex` **number** 矩形覆盖物的叠加顺序。地图上存在多个矩形覆盖物叠加时，通过该属性使级别较高的矩形覆盖物在上层显示 (optional, default `10`)
    -   `opts.bubble` **boolean** 是否将覆盖物的鼠标或touch等事件冒泡到地图上（自v1.3 新增） (optional, default `false`)
    -   `opts.cursor` **string?** 指定鼠标悬停时的鼠标样式，自定义cursor，IE仅支持cur/ani/ico格式，Opera不支持自定义cursor
    -   `opts.strokeColor` **string** 线条颜色，使用16进制颜色代码赋值。默认值为#00D3FC (optional, default `#00D3FC`)
    -   `opts.strokeOpacity` **number** 轮廓线透明度，取值范围[0,1]，0表示完全透明，1表示不透明。默认为0.9 (optional, default `0.9`)
    -   `opts.strokeWeight` **number** 轮廓线宽度 (optional, default `2`)
    -   `opts.fillColor` **string** 矩形填充颜色，使用16进制颜色代码赋值，如：#00B2D5 (optional, default `#00B2D5`)
    -   `opts.fillOpacity` **number** 矩形填充透明度，取值范围[0,1]，0表示完全透明，1表示不透明。默认为0.5 (optional, default `0.5`)
    -   `opts.draggable` **boolean** 设置矩形是否可拖拽移动，默认为false (optional, default `false`)
    -   `opts.extData` **object?** 用户自定义属性，支持JavaScript API任意数据类型，如Polygon的id等
    -   `opts.strokeStyle` **(`"solid"` \| `"dashed"`)** 轮廓线样式，实线:solid，虚线:dashed (optional, default `solid`)
    -   `opts.strokeDasharray` **Array&lt;number>?** 勾勒形状轮廓的虚线和间隙的样式，此属性在strokeStyle 为dashed 时有效， 此属性在ie9+浏览器有效 取值：
        实线：[0,0,0]
        虚线：[10,10] ，[10,10] 表示10个像素的实线和10个像素的空白（如此反复）组成的虚线
        点画线：[10,2,10]， [10,2,10] 表示10个像素的实线和2个像素的空白 + 10个像素的实线和10个像素的空白 （如此反复）组成的虚线

### contains

判断坐标是否在矩形上

#### Parameters

-   `point` **LngLatLike** 

Returns **boolean** 

### setBounds

设置矩形的范围

#### Parameters

-   `bounds` **Bounds** 

Returns **void** 

### generateBuffer

#### Parameters

-   `gl`  

### setOptions

修改矩形属性（样式风格，包括组成矩形轮廓线的节点、轮廓线样式等。属性详情参看RectangleOptions列表）

#### Parameters

-   `optsArg` **RectangleOptions** 

### getBounds

获取当前矩形路径的节点数组。

Returns **(Array&lt;LngLat> | Array&lt;Array&lt;LngLat>>)** 

### getBounds

获取当前矩形的范围对象

Returns **Bounds** 

### hide

隐藏矩形

### getCenter

获取矩形的中心点

Returns **LngLat** 

### show

显示矩形

### getExtData

获取用户自定义属性

Returns **Object** 

### setExtData

设置用户自定义属性，支持JavaScript API任意数据类型

#### Parameters

-   `extData` **Object** 

### destroy

销毁内存-矩形

### getArea

获取面积,平米

Returns **number** 

### getOptions

获取矩形的属性

Returns **RectangleOptions** 

## GeoJSON

**Extends AMap.OverlayGroup**

### Parameters

-   `opts`  

### importData

加载新的GeoJSON对象，转化为覆盖物，旧的覆盖物将移除

#### Parameters

-   `geoJSON` **any** 

### toGeoJSON

将当前对象包含的覆盖物转换为GeoJSON对象

Returns **Object** GeoJSONObject

## GeoJSON

**Extends AMap.OverlayGroup**

### Parameters

-   `opts`  

### importData

加载新的GeoJSON对象，转化为覆盖物，旧的覆盖物将移除

#### Parameters

-   `geoJSON` **any** 

### toGeoJSON

将当前对象包含的覆盖物转换为GeoJSON对象

Returns **Object** GeoJSONObject

## GeoJSON

**Extends OverlayGroup**

GeoJSON类，继承自OverLayGroup，可实现GeoJSON对象与OverlayGroup的相互转换

### Parameters

-   `opts` **GeoJSONOptions** 创建一个GeoJSON对象，ops为初始构造参数
    -   `opts.geoJSON` **Object** 要加载的标准GeoJSON对象
    -   `opts.getMarker` **function (geojson, lnglat)** 指定点要素的绘制方式，缺省时为Marker的默认样式。geojson为当前要素对应的GeoJSON对象，lnglats为对应的线的路径
    -   `opts.getPolyline` **function (geojson, lnglat)** 指定线要素的绘制方式，缺省时为Marker的默认样式。geojson为当前要素对应的GeoJSON对象，lnglats为对应的线的路径
    -   `opts.getPolygon` **function (geojson, lnglat)** 指定面要素的绘制方式，缺省时为Marker的默认样式。geojson为当前要素对应的GeoJSON对象，lnglats为对应的线的路径

### importData

加载新的GeoJSON对象，转化为覆盖物，旧的覆盖物将移除

#### Parameters

-   `geoJSON` **any** 

### toGeoJSON

将当前对象包含的覆盖物转换为GeoJSON对象

Returns **Object** GeoJSONObject
