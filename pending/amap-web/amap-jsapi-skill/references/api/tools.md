## 工具类

用于满足一定专门功能的工具类型


## RangingTool

构造一个距离量测插件对象。参数map为地图实例。 opts属性参考RangingToolOptions列表中的说明

### Parameters

-   `map` **Map** 要添加到的地图实例
-   `opts` **RangingToolOptions** 鼠标工具配置参数
    -   `opts.startMarkerOptions` **Object** 设置量测起始点标记属性对象，包括点标记样式、大小等，参考 MarkerOptions
    -   `opts.midMarkerOptions` **Object** 设置量测中间点标记属性对象，包括点标记样式、大小等，参考 MarkerOptions
    -   `opts.endMarkerOptions` **Object** 设置量测结束点标记属性对象，包括点标记样式、大小等，参考 MarkerOptions
    -   `opts.lineOptions` **Object** 设置距离量测线的属性对象，包括线样式、颜色等，参考 PolylineOptions
    -   `opts.tmpLineOptions` **Object** 设置距离量测过程中临时量测线的属性对象，包括线样式、颜色，参考 PolylineOptions
    -   `opts.startLabelText` **String** 设置量测起始点标签的文字内容，默认为“起点”
    -   `opts.midLabelText` **String** 设置量测中间点处标签的文字内容，默认为当前量测结果值
    -   `opts.endLabelText` **String** 设置量测结束点处标签的文字内容，默认为当前量测结果值
    -   `opts.startLabelOffset` **Pixel** 设置量测起始点标签的偏移量。默认值：Pixel(-6, 6)
    -   `opts.midLabelOffset` **Pixel** 设置量测中间点标签的偏移量。默认值：Pixel(-6, 6)
    -   `opts.endLabelOffset` **Pixel** 设置量测结束点标签的偏移量。默认值：Pixel(-6, 6)

### Examples

```javascript
map.plugin(["AMap.MouseTool"],function(){
   var ruler = new AMap.RangingTool(map);
});
```

### turnOn

启动测距工具

### turnOff

关闭测距工具

#### Parameters

-   `removeOverlays` **Boolean** 是否删除测距过程产生的覆盖物

## MouseTool

鼠标工具插件。通过该插件，可进行鼠标画标记点、线、多边形、矩形、圆、距离量测、面积量测、拉框放大、拉框缩小等功能。

### Parameters

-   `map` **Map** 鼠标工具添加到的地图实例

### Examples

```javascript
map.plugin(["AMap.MouseTool"],function(){
   var mousetool = new AMap.MouseTool(map);
   // 使用鼠标工具，在地图上画标记点
   mousetool.marker();
});
```

### marker

开启鼠标画点标注模式。鼠标在地图上单击绘制点标注，标注样式参考MarkerOptions设置

#### Parameters

-   `opts` **MarkerOptions** 参考MarkerOptions设置

### circle

开启鼠标画圆模式。鼠标在地图上拖动绘制相应的圆形。圆形样式参考CircleOptions设置

#### Parameters

-   `opts` **CircleOptions** 参考CircleOptions设置

### rectangle

开启鼠标画矩形模式。鼠标在地图上拉框即可绘制相应的矩形。矩形样式参考PolygonOptions设置

#### Parameters

-   `opts` **PolygonOptions** 矩形样式参考PolygonOptions设置

### polyline

开启鼠标画折线模式。鼠标在地图上点击绘制折线，鼠标左键双击或右键单击结束绘制，折线样式参考PolylineOptions设置

#### Parameters

-   `opts` **PolylineOptions** 参考PolylineOptions设置

### polygon

开启鼠标画多边形模式。鼠标在地图上单击开始绘制多边形，鼠标左键双击或右键单击结束当前多边形的绘制，多边形样式参考PolygonOptions设置

#### Parameters

-   `opts` **PolygonOptions** 参考PolygonOptions设置

### measureArea

开启面积量测模式。鼠标在地图上单击绘制量测区域，鼠标左键双击或右键单击结束当前量测操作，并显示本次量测结果。量测面样式参考PolygonOptions设置

#### Parameters

-   `opts` **PolygonOptions** 参考PolygonOptions设置

### rule

开启距离量测模式。鼠标在地图上单击绘制量测节点，并计算显示两两节点之间的距离，鼠标左键双击或右键单击结束当前量测操作。量测线样式参考 PolylineOptions 设置
注：不能同时使用rule方法和RangTool插件进行距离量测

#### Parameters

-   `opts` **PolylineOptions** 参考PolylineOptions设置

### rectZoomIn

开启鼠标拉框放大模式。鼠标可在地图上拉框放大地图。矩形框样式参考PolygonOptions设置

#### Parameters

-   `opts` **PolygonOptions** 参考PolygonOptions设置

### rectZoomOut

开启鼠标拉框缩小模式。鼠标可在地图上拉框缩小地图。矩形框样式参考PolygonOptions设置

#### Parameters

-   `opts` **PolygonOptions** 参考PolygonOptions设置

### close

关闭当前鼠标操作。参数arg设为true时，鼠标操作关闭的同时清除地图上绘制的所有覆盖物对象；设为false时，保留所绘制的覆盖物对象。默认为false

#### Parameters

-   `ifClear` **boolean** 是否清除地图上的覆盖物

## PolygonEditor

Polygon 编辑器

### Parameters

-   `map` **Map** AMap.Map 的实例
-   `polygon` **Polygon?** 编辑对象
-   `opts` **Object?** 设置参数
    -   `opts.createOptions` **Object?** 新创建的对象样式
    -   `opts.editOptions` **Object?** 编辑样式
    -   `opts.controlPoint` **Object?** 顶点样式 CircleMarkerOptions
    -   `opts.midControlPoint` **Object?** 中间点样式 CircleMarkerOptions

### open

开始编辑对象

### setTarget

设置编辑对象

#### Parameters

-   `tar`  
-   `overlay` **Polygon** 

### getTarget

获取编辑对象

Returns **(Polygon \| undefined)** 

### setAdsorbPolygons

设置吸附多边形

#### Parameters

-   `list` **(Polygon \| Array&lt;Polygon>)** 

### clearAdsorbPolygons

清空所有的吸附多边形

### addAdsorbPolygons

添加吸附多边形

#### Parameters

-   `list` **(Polygon \| Array&lt;Polygon>)** 

### removeAdsorbPolygons

删除吸附多边形

#### Parameters

-   `list` **(Polygon \| Array&lt;Polygon>)** 

### close

停止编辑对象

## PolylineEditor

折线编辑插件，用于编辑AMap.Polyline对象，支持通过鼠标调整折线的形状。

### Parameters

-   `map` **Map** AMap.Map 的实例
-   `polygon` **Polygon?** 编辑对象
-   `opts` **Object?** 设置参数
    -   `opts.createOptions` **Object?** 新创建的对象样式
    -   `opts.editOptions` **Object?** 编辑样式
    -   `opts.controlPoint` **Object?** 顶点样式 CircleMarkerOptions
    -   `opts.midControlPoint` **Object?** 中间点样式 CircleMarkerOptions

### setTarget

设置编辑对象

#### Parameters

-   `overlay` **Polyline?** 

### getTarget

获取编辑对象

Returns **(Polyline \| undefined)** 当前编辑对象

### open

开始编辑对象

### close

停止编辑对象

## CircleEditor

圆编辑插件。用于编辑AMap.Circle对象，功能包括使用鼠标改变圆半径大小、拖拽圆心改变圆的位置。

### Parameters

-   `map` **Map** AMap.Map 实例
-   `circle` **Circle?** 可选参数， AMap.Circle 实例
-   `opts` **Object?** 设置参数
    -   `opts.createOptions` **Object?** 新创建的对象样式
    -   `opts.editOptions` **Object?** 编辑样式
    -   `opts.movePoint` **Object?** 移动点样式 MarkerOptions
    -   `opts.resizePoint` **Object?** reaize点样式 MarkerOptions

### setTarget

设置编辑对象

#### Parameters

-   `overlay` **Circle?** 编辑对象

### getTarget

获取编辑对象

Returns **(Circle \| undefined)** 当前编辑对象

### open

打开编辑功能

### close

关闭编辑功能

## BezierCurveEditor

贝塞尔曲线编辑器

### Parameters

-   `map` **Map** AMap.Map 实例
-   `bezier` **BezierCurve?** 曲线示例
-   `opts` **Object?** 设置参数
    -   `opts.createOptions` **Object?** 新创建的对象样式
    -   `opts.editOptions` **Object?** 编辑样式
    -   `opts.controlPoint` **Object?** 顶点样式 MarkerOptions
    -   `opts.midControlPoint` **Object?** 中间点样式 MarkerOptions
    -   `opts.bezierControlPoint` **Object?** 贝塞尔控制点样式MarkerOptions
    -   `opts.bezierControlLine` **Object?** 贝塞尔控制线样式PolylineOptions

### setTarget

设置编辑对象

#### Parameters

-   `overlay` **BezierCurve?** 

### getTarget

获取编辑对象

Returns **(BezierCurve \| undefined)** [overlay] 当前编辑对象

### open

开始编辑对象

### close

结束编辑对象

## EllipseEditor

椭圆编辑器

### Parameters

-   `map` **Map** AMap.Map 的实例
-   `ellipse` **Ellipse?** AMap.Ellipse 的实例
-   `opts` **Object?** 设置参数
    -   `opts.createOptions` **Object?** 新创建的对象样式
    -   `opts.editOptions` **Object?** 编辑样式
    -   `opts.movePoint` **Object?** 移动点样式 MarkerOptions
    -   `opts.resizeXPoint` **Object?** reaizeX点样式 MarkerOptions
    -   `opts.resizeYPoint` **Object?** reaizeY点样式 MarkerOptions

### setTarget

设置编辑对象

#### Parameters

-   `overlay` **Ellipse?** 编辑对象

### getTarget

获取编辑对象

Returns **(Ellipse \| undefined)** 当前编辑对象

### open

打开编辑功能

### close

关闭编辑功能

## RectangleEditor

矩形编辑器

### Parameters

-   `map` **Map** AMap.Map 的实例
-   `rect` **Rectangle?** AMap.Rectangle 的实例
-   `opts` **Object?** 设置参数
    -   `opts.createOptions` **Object?** 新创建的对象样式
    -   `opts.editOptions` **Object?** 编辑样式
    -   `opts.southWestPoint` **Object?** 西南点样式 MarkerOptions
    -   `opts.northEastPoint` **Object?** 东北点样式 MarkerOptions

### setTarget

设置编辑对象

#### Parameters

-   `overlay` **Rectangle?** 编辑对象

### getTarget

获取编辑对象

Returns **(Rectangle \| undefined)** 当前编辑对象

### open

打开编辑功能

### close

关闭编辑功能
