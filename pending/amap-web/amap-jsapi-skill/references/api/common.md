## 通用库

一些通用的函数库


## GeometryUtil

### distance

计算两个经纬度点之间的实际距离。单位：米

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 

Returns **number** 

### distance

计算两个经纬度点之间的实际距离。单位：米

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 

Returns **number** 

### ringArea

计算一个经纬度路径围成区域的实际面积。单位：平米

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **number** 

### ringArea

计算一个经纬度路径围成区域的实际面积。单位：平米

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **number** 

### isClockwise

判断一个经纬度路径是否为顺时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isClockwise

判断一个经纬度路径是否为顺时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### typePolygon

判断一个经纬度路径面类型

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### typePolygon

判断一个经纬度路径面类型

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### makesureClockwise

将一个路径变为顺时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **Array&lt;\[number, number]>** 

### makesureClockwise

将一个路径变为顺时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **Array&lt;\[number, number]>** 

### makesureAntiClockwise

将一个路径变为逆时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **Array&lt;\[number, number]>** 

### makesureAntiClockwise

将一个路径变为逆时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **Array&lt;\[number, number]>** 

### distanceOfLine

计算一个经纬度路径的实际长度。单位：米

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **number** 

### distanceOfLine

计算一个经纬度路径的实际长度。单位：米

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **number** 

### ringRingClip

计算两个经纬度面的交叉区域。只适用于凸多边形

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

### ringRingClip

计算两个经纬度面的交叉区域。只适用于凸多边形

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

### doesSegmentsIntersect

判断两个线段是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 
-   `p4` **LngLatLike** 

Returns **boolean** 

### doesSegmentsIntersect

判断两个线段是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 
-   `p4` **LngLatLike** 

Returns **boolean** 

### doesSegmentLineIntersect

判断线段和一个路径是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesSegmentLineIntersect

判断线段和一个路径是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesSegmentRingIntersect

判断线段和一个环是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesSegmentRingIntersect

判断线段和一个环是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesSegmentPolygonIntersect

判断线段和多个环是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 

Returns **boolean** 

### doesSegmentPolygonIntersect

判断线段和多个环是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 

Returns **boolean** 

### doesLineLineIntersect

判断两个经纬度路径是否相交

#### Parameters

-   `line` **Array&lt;LngLatLike>** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesLineLineIntersect

判断两个经纬度路径是否相交

#### Parameters

-   `line` **Array&lt;LngLatLike>** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesLineRingIntersect

判断经纬度路径和经纬度面是否交叉

#### Parameters

-   `line` **Array&lt;LngLatLike>** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesLineRingIntersect

判断经纬度路径和经纬度面是否交叉

#### Parameters

-   `line` **Array&lt;LngLatLike>** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesRingRingIntersect

判断两个经纬度面是否交叉

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesRingRingIntersect

判断两个经纬度面是否交叉

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

Returns **boolean** 

### pointInRing

判断点是否在环内，支持任意坐标系

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### pointInRing

判断点是否在环内，支持任意坐标系

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInRing

判断点是否在环内

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInRing

判断点是否在环内

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInBbox

判断点是否在环内

#### Parameters

-   `p` **LngLatLike** 
-   `bbox` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInBbox

判断点是否在 bbox内

#### Parameters

-   `p` **LngLatLike** 
-   `rect` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isRingInRing

判断环是否在另一个环内

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isRingInRing

判断环是否在另一个环内

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInPolygon

判断点是否在多个环组成区域内

#### Parameters

-   `p` **LngLatLike** 
-   `rings` **\[Array&lt;ringLngLatLike>]** 

Returns **boolean** 

### isPointInPolygon

判断点是否在多个环组成区域内

#### Parameters

-   `p` **LngLatLike** 
-   `rings` **\[Array&lt;ringLngLatLike>]** 

Returns **boolean** 

### isPointInPolygons

判断点是否在带洞多多边型内

#### Parameters

-   `p` **LngLatLike** 
-   `polygons` **\[\[Array&lt;ringLngLatLike>]]** 

Returns **boolean** 

### isPointOnSegment

判断P1是否在P2P3上，tolerance为误差范围

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 
-   `tolerance` **Number** 

Returns **boolean** 

### isPointOnSegment

判断P1是否在P2P3上，tolerance为误差范围

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 
-   `tolerance` **Number** 

Returns **boolean** 

### isPointOnLine

判断P是否在line上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnLine

判断P是否在line上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnRing

判断P是否在ring的边上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnRing

判断P是否在ring的边上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnPolygon

判断P是否在多个ring的边上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnPolygon

判断P是否在多个ring的边上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `tolerance` **number** 

Returns **boolean** 

### closestOnSegment

计算P2P3上距离P1最近的点

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 

Returns **boolean** 

### closestOnSegment

计算P2P3上距离P1最近的点

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 

Returns **boolean** 

### closestOnLine

计算line上距离P最近的点

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### closestOnLine

计算line上距离P最近的点

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### distanceToSegment

计算P2P3到P1的距离。单位：米

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 

Returns **LngLat** 

### distanceToSegment

计算P2P3到P1的距离。单位：米

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 

Returns **LngLat** 

### distanceToLine

计算P到line的距离。单位：米

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **number** 

### distanceToLine

计算P到line的距离。单位：米

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **number** 

## GeometryUtil

GeometryUtil为一组空间数据计算的函数库，v1.4.2新增。支持点线面的空间关系计算、长度、面积计算等等，

### distance

计算两个经纬度点之间的实际距离。单位：米

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 

Returns **number** 

### distance

计算两个经纬度点之间的实际距离。单位：米

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 

Returns **number** 

### ringArea

计算一个经纬度路径围成区域的实际面积。单位：平米

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **number** 

### ringArea

计算一个经纬度路径围成区域的实际面积。单位：平米

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **number** 

### isClockwise

判断一个经纬度路径是否为顺时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isClockwise

判断一个经纬度路径是否为顺时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### typePolygon

判断一个经纬度路径面类型

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### typePolygon

判断一个经纬度路径面类型

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### makesureClockwise

将一个路径变为顺时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **Array&lt;\[number, number]>** 

### makesureClockwise

将一个路径变为顺时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **Array&lt;\[number, number]>** 

### makesureAntiClockwise

将一个路径变为逆时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **Array&lt;\[number, number]>** 

### makesureAntiClockwise

将一个路径变为逆时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **Array&lt;\[number, number]>** 

### distanceOfLine

计算一个经纬度路径的实际长度。单位：米

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **number** 

### distanceOfLine

计算一个经纬度路径的实际长度。单位：米

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **number** 

### ringRingClip

计算两个经纬度面的交叉区域。只适用于凸多边形

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

### ringRingClip

计算两个经纬度面的交叉区域。只适用于凸多边形

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

### doesSegmentsIntersect

判断两个线段是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 
-   `p4` **LngLatLike** 

Returns **boolean** 

### doesSegmentsIntersect

判断两个线段是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 
-   `p4` **LngLatLike** 

Returns **boolean** 

### doesSegmentLineIntersect

判断线段和一个路径是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesSegmentLineIntersect

判断线段和一个路径是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesSegmentRingIntersect

判断线段和一个环是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesSegmentRingIntersect

判断线段和一个环是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesSegmentPolygonIntersect

判断线段和多个环是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 

Returns **boolean** 

### doesSegmentPolygonIntersect

判断线段和多个环是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 

Returns **boolean** 

### doesLineLineIntersect

判断两个经纬度路径是否相交

#### Parameters

-   `line` **Array&lt;LngLatLike>** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesLineLineIntersect

判断两个经纬度路径是否相交

#### Parameters

-   `line` **Array&lt;LngLatLike>** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesLineRingIntersect

判断经纬度路径和经纬度面是否交叉

#### Parameters

-   `line` **Array&lt;LngLatLike>** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesLineRingIntersect

判断经纬度路径和经纬度面是否交叉

#### Parameters

-   `line` **Array&lt;LngLatLike>** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesRingRingIntersect

判断两个经纬度面是否交叉

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesRingRingIntersect

判断两个经纬度面是否交叉

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

Returns **boolean** 

### pointInRing

判断点是否在环内，支持任意坐标系

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### pointInRing

判断点是否在环内，支持任意坐标系

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInRing

判断点是否在环内

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInRing

判断点是否在环内

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInBbox

判断点是否在环内

#### Parameters

-   `p` **LngLatLike** 
-   `bbox` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInBbox

判断点是否在 bbox内

#### Parameters

-   `p` **LngLatLike** 
-   `rect` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isRingInRing

判断环是否在另一个环内

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isRingInRing

判断环是否在另一个环内

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInPolygon

判断点是否在多个环组成区域内

#### Parameters

-   `p` **LngLatLike** 
-   `rings` **\[Array&lt;ringLngLatLike>]** 

Returns **boolean** 

### isPointInPolygon

判断点是否在多个环组成区域内

#### Parameters

-   `p` **LngLatLike** 
-   `rings` **\[Array&lt;ringLngLatLike>]** 

Returns **boolean** 

### isPointInPolygons

判断点是否在带洞多多边型内

#### Parameters

-   `p` **LngLatLike** 
-   `polygons` **\[\[Array&lt;ringLngLatLike>]]** 

Returns **boolean** 

### isPointOnSegment

判断P1是否在P2P3上，tolerance为误差范围

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 
-   `tolerance` **Number** 

Returns **boolean** 

### isPointOnSegment

判断P1是否在P2P3上，tolerance为误差范围

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 
-   `tolerance` **Number** 

Returns **boolean** 

### isPointOnLine

判断P是否在line上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnLine

判断P是否在line上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnRing

判断P是否在ring的边上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnRing

判断P是否在ring的边上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnPolygon

判断P是否在多个ring的边上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnPolygon

判断P是否在多个ring的边上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `tolerance` **number** 

Returns **boolean** 

### closestOnSegment

计算P2P3上距离P1最近的点

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 

Returns **boolean** 

### closestOnSegment

计算P2P3上距离P1最近的点

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 

Returns **boolean** 

### closestOnLine

计算line上距离P最近的点

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### closestOnLine

计算line上距离P最近的点

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### distanceToSegment

计算P2P3到P1的距离。单位：米

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 

Returns **LngLat** 

### distanceToSegment

计算P2P3到P1的距离。单位：米

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 

Returns **LngLat** 

### distanceToLine

计算P到line的距离。单位：米

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **number** 

### distanceToLine

计算P到line的距离。单位：米

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **number** 

## GeometryUtil

平面的计算库

### distance

计算两个经纬度点之间的实际距离。单位：米

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 

Returns **number** 

### distance

计算两个经纬度点之间的实际距离。单位：米

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 

Returns **number** 

### ringArea

计算一个经纬度路径围成区域的实际面积。单位：平米

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **number** 

### ringArea

计算一个经纬度路径围成区域的实际面积。单位：平米

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **number** 

### isClockwise

判断一个经纬度路径是否为顺时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isClockwise

判断一个经纬度路径是否为顺时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### typePolygon

判断一个经纬度路径面类型

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### typePolygon

判断一个经纬度路径面类型

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### makesureClockwise

将一个路径变为顺时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **Array&lt;\[number, number]>** 

### makesureClockwise

将一个路径变为顺时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **Array&lt;\[number, number]>** 

### makesureAntiClockwise

将一个路径变为逆时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **Array&lt;\[number, number]>** 

### makesureAntiClockwise

将一个路径变为逆时针

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **Array&lt;\[number, number]>** 

### distanceOfLine

计算一个经纬度路径的实际长度。单位：米

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **number** 

### distanceOfLine

计算一个经纬度路径的实际长度。单位：米

#### Parameters

-   `ring` **Array&lt;LngLatLike>** 

Returns **number** 

### ringRingClip

计算两个经纬度面的交叉区域。只适用于凸多边形

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

### ringRingClip

计算两个经纬度面的交叉区域。只适用于凸多边形

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

### doesSegmentsIntersect

判断两个线段是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 
-   `p4` **LngLatLike** 

Returns **boolean** 

### doesSegmentsIntersect

判断两个线段是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 
-   `p4` **LngLatLike** 

Returns **boolean** 

### doesSegmentLineIntersect

判断线段和一个路径是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesSegmentLineIntersect

判断线段和一个路径是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesSegmentRingIntersect

判断线段和一个环是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesSegmentRingIntersect

判断线段和一个环是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesSegmentPolygonIntersect

判断线段和多个环是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 

Returns **boolean** 

### doesSegmentPolygonIntersect

判断线段和多个环是否相交

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 

Returns **boolean** 

### doesLineLineIntersect

判断两个经纬度路径是否相交

#### Parameters

-   `line` **Array&lt;LngLatLike>** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesLineLineIntersect

判断两个经纬度路径是否相交

#### Parameters

-   `line` **Array&lt;LngLatLike>** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesLineRingIntersect

判断经纬度路径和经纬度面是否交叉

#### Parameters

-   `line` **Array&lt;LngLatLike>** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesLineRingIntersect

判断经纬度路径和经纬度面是否交叉

#### Parameters

-   `line` **Array&lt;LngLatLike>** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesRingRingIntersect

判断两个经纬度面是否交叉

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

Returns **boolean** 

### doesRingRingIntersect

判断两个经纬度面是否交叉

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

Returns **boolean** 

### pointInRing

判断点是否在环内，支持任意坐标系

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### pointInRing

判断点是否在环内，支持任意坐标系

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInRing

判断点是否在环内

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInRing

判断点是否在环内

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInBbox

判断点是否在环内

#### Parameters

-   `p` **LngLatLike** 
-   `bbox` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInBbox

判断点是否在 bbox内

#### Parameters

-   `p` **LngLatLike** 
-   `rect` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isRingInRing

判断环是否在另一个环内

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isRingInRing

判断环是否在另一个环内

#### Parameters

-   `ring1` **Array&lt;LngLatLike>** 
-   `ring2` **Array&lt;LngLatLike>** 

Returns **boolean** 

### isPointInPolygon

判断点是否在多个环组成区域内

#### Parameters

-   `p` **LngLatLike** 
-   `rings` **\[Array&lt;ringLngLatLike>]** 

Returns **boolean** 

### isPointInPolygon

判断点是否在多个环组成区域内

#### Parameters

-   `p` **LngLatLike** 
-   `rings` **\[Array&lt;ringLngLatLike>]** 

Returns **boolean** 

### isPointInPolygons

判断点是否在带洞多多边型内

#### Parameters

-   `p` **LngLatLike** 
-   `polygons` **\[\[Array&lt;ringLngLatLike>]]** 

Returns **boolean** 

### isPointOnSegment

判断P1是否在P2P3上，tolerance为误差范围

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 
-   `tolerance` **Number** 

Returns **boolean** 

### isPointOnSegment

判断P1是否在P2P3上，tolerance为误差范围

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 
-   `tolerance` **Number** 

Returns **boolean** 

### isPointOnLine

判断P是否在line上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnLine

判断P是否在line上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnRing

判断P是否在ring的边上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnRing

判断P是否在ring的边上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `ring` **Array&lt;LngLatLike>** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnPolygon

判断P是否在多个ring的边上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `tolerance` **number** 

Returns **boolean** 

### isPointOnPolygon

判断P是否在多个ring的边上，tolerance为误差范围

#### Parameters

-   `p` **LngLatLike** 
-   `tolerance` **number** 

Returns **boolean** 

### closestOnSegment

计算P2P3上距离P1最近的点

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 

Returns **boolean** 

### closestOnSegment

计算P2P3上距离P1最近的点

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 

Returns **boolean** 

### closestOnLine

计算line上距离P最近的点

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### closestOnLine

计算line上距离P最近的点

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **boolean** 

### distanceToSegment

计算P2P3到P1的距离。单位：米

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 

Returns **LngLat** 

### distanceToSegment

计算P2P3到P1的距离。单位：米

#### Parameters

-   `p1` **LngLatLike** 
-   `p2` **LngLatLike** 
-   `p3` **LngLatLike** 

Returns **LngLat** 

### distanceToLine

计算P到line的距离。单位：米

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **number** 

### distanceToLine

计算P到line的距离。单位：米

#### Parameters

-   `p` **LngLatLike** 
-   `line` **Array&lt;LngLatLike>** 

Returns **number** 

## DomUtil

### getViewport

获取DOM元素的大小

#### Parameters

-   `obj` **HTMLElement** 

Returns **\[number, number]** 

### getViewportOffset

获取DOM元素距离窗口左上角的距离

#### Parameters

-   `element` **HTMLElement** 

Returns **\[number, number]** 

### create

在parentNode内部创建一个className类名的tagName元素

#### Parameters

-   `tagName` **string** 节点类型
-   `container` **HTMLElement** 上级节点对象
-   `className` **string** 
-   `position` **string** 插入位置

Returns **HTMLElement** 

### hasClass

DOM元素是否包含className

#### Parameters

-   `el` **HTMLElement** 
-   `name` **string** 

Returns **boolean** 

### addClass

给DOM元素添加一个className

#### Parameters

-   `el` **HTMLElement** 
-   `name` **string** 

### setClass

给DOM元素设置为className样式

#### Parameters

-   `el` **HTMLElement** 
-   `name` **string** 

### removeClass

给DOM元素删除一个className

#### Parameters

-   `el` **HTMLElement** 
-   `name` **string** 

### remove

将DOM元素从父节点删除

#### Parameters

-   `el` **HTMLElement** 

### empty

清空DOM元素

#### Parameters

-   `el` **HTMLElement** 

### rotate

给DOM元素旋转一个角度，以center为中心，center以元素左上角为坐标原点

#### Parameters

-   `target` **HTMLElement** 
-   `angle` **number** 
-   `center` **Pixel** 

### setCss

给DOM元素删除一组样式，Object同样式表

#### Parameters

-   `obj` **(HTMLElement \| Array&lt;HTMLElement>)** 
-   `css` **Object** 

### setOpacity

给DOM元素设定一个透明度

#### Parameters

-   `el` **HTMLElement** 
-   `value` **number** 

## Browser

### Properties

-   `us` **string** 当前浏览器userAgent
-   `mobile` **boolean** 是否移动设备
-   `plat` **string** 平台类型，如：'windows'、'mac'、'ios'、'android'、'other'
-   `windows` **boolean** 是否windows设备
-   `ios` **boolean** 是否iOS设备
-   `iPad` **boolean** 是否iPad
-   `Phone` **boolean** 是否iPhone
-   `android` **boolean** 是否安卓设备
-   `android23` **boolean** 是否安卓4以下系统
-   `chrome` **boolean** 是否Chrome浏览器
-   `firefox` **boolean** 是否火狐浏览器
-   `safari` **boolean** 是否Safari浏览器
-   `wechat` **boolean** 是否微信
-   `uc` **boolean** 是否UC浏览器
-   `qq` **boolean** 是否QQ或者QQ浏览器
-   `ie` **boolean** 是否IE
-   `ie6` **boolean** 是否IE6
-   `ie7` **boolean** 是否IE7
-   `ie8` **boolean** 是否IE8
-   `ie9` **boolean** 是否IE9
-   `ie10` **boolean** 是否IE10
-   `ie11` **boolean** 是否IE11
-   `ielt9` **boolean** 是否IE9以下
-   `edge` **boolean** 是否Edge浏览器
-   `isLocalStorage` **boolean** 是否支持LocaStorage
-   `isGeolocation` **boolean** 是否支持Geolocation
-   `mobileWebkit` **boolean** 是否Webkit移动浏览器
-   `mobileWebkit3d` **boolean** 是否支持Css3D的Webkit移动端浏览器
-   `retina` **boolean** 是否高清屏幕，devicePixelRatio>1
-   `touch` **boolean** 是否触屏
-   `msPointer` **boolean** 是否msPointer设备
-   `pointer` **boolean** 是否pointer设备
-   `webkit` **boolean** 是否webkit浏览器
-   `webkit3d` **boolean** 是否支持Css3D的Webkit浏览器
-   `gecko3d` **boolean** 是否支持Css3D的gecko浏览器
-   `ie3d` **boolean** 是否支持Css3D的ie浏览器
-   `any3d` **boolean** 是否支持Css3D的浏览器
-   `opera3d` **boolean** 是否支持Css3D的opera浏览器
-   `isCanvas` **boolean** 是否支持canvas
-   `isSvg` **boolean** 是否支持svg
-   `isVML` **boolean** 是否支持vml
-   `isWorker` **boolean** 是否支持WebWorker
-   `isWebsocket` **boolean** 是否支持WebSocket
-   `isWebGL` **boolean** 是否支持webgl

## Util

### isDOM

判断参数是否为DOM元素

#### Parameters

-   `obj` **any** 

Returns **boolean** 

### colorNameToHex

#### Parameters

-   `colorName` **string** 

Returns **string** 如#FFFFFF的颜色值

### rgbHex2Rgba

将16进制RGB转为rgba(R,G,B,A)

#### Parameters

-   `hex` **string** 

Returns **string** 

### argbHex2Rgba

将16进制RGBA转为rgba(R,G,B,A)

#### Parameters

-   `hex` **string** 

Returns **string** 

### isEmpty

判断一个对象是否为空

#### Parameters

-   `obj` **any** 

Returns **boolean** 

### deleteItemFromArray

从数组删除元素

#### Parameters

-   `array` **any** 
-   `item` **any** 

### deleteItemFromArrayByIndex

按索引删除数组元素

#### Parameters

-   `array` **any** 
-   `index` **number** 

### indexOf

返回元素索引

#### Parameters

-   `array` **any** 
-   `item` **any** 

Returns **number** 

### format

保留小数点后digits位

#### Parameters

-   `num` **number** 
-   `digits` **number** 

Returns **number** 

### isArray

判断是否数组

#### Parameters

-   `obj` **any** 

Returns **boolean** 

### includes

判断数组是否包含某个元素

#### Parameters

-   `array` **Array&lt;any>** 
-   `item` **any** 

Returns **boolean** 

### requestIdleCallback

同原生requestIdleCallback

#### Parameters

-   `func` **Function** 

Returns **number** 

### cancelIdleCallback

同原生 cancelIdleCallback

#### Parameters

-   `id` **number** 

### requestAnimFrame

同原生 Util.requestAnimFrame

#### Parameters

-   `func` **Function** 

Returns **number** 

### cancelAnimFrame

同原生 Util.cancelAnimFrame

#### Parameters

-   `id` **number** 
