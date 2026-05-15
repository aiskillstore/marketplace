## 基础类

经纬度、像素、边界、大小、这些是地图 JSAPI 开发必须了解的基本类型


## LngLat

### Parameters

-   `lng`  
-   `lat`  
-   `noWrap`   (optional, default `false`)

### lat

纬度

Type: number

### lng

经度

Type: number

### setLng

设置经度值

#### Parameters

-   `lng` **number** 经度

### setLat

设置纬度值

#### Parameters

-   `lat` **number** 

### getLng

获取经度值

Returns **number** 

### getLat

获取纬度值

Returns **number** 

### equals

判断经纬度坐标和另外一个经纬度坐标是否相等

#### Parameters

-   `another` **LngLat** 另外一个经纬度坐标

Returns **Boolean** 是否相等

### add

与另外一个经纬度相加

#### Parameters

-   `another` **LngLat** 另外一个经纬度坐标
-   `noWrap` **boolean** 是否将相加的结果经度值修正到 [-180,180] 区间内

Returns **LngLat** 两个经纬度相加的结果

### subtract

与另外一个经纬度相减

#### Parameters

-   `another` **LngLat** 另外一个经纬度坐标
-   `noWrap` **boolean** 是否将相减的结果经度值修正到 [-180,180] 区间内

Returns **LngLat** 两个经纬度相减的结果

### offset

获取从当前经纬度位置向东移动 E 米，向北移动 N 米的坐标位置

#### Parameters

-   `E` **Number** 经度方向移动，向东为正
-   `N` **Number** 维度方向移动，向北为正

Returns **LngLat** 移动后的新经纬度

### toString

LngLat对象以字符串的形式返回

Returns **string** 格式如'lng值,lat值'的字符串

### toArray

LngLat对象以字符串的形式返回

Returns **string** 格式如'lng值,lat值'的字符串

### distance

计算当前经纬度距离另一个经纬度或者经纬度数组组成的路径的距离
[相关示例][5]

Returns **number** 距离值，单位为米

## LngLat

经纬度坐标，用来描述地图上的一个点位置,
目前高德地图使用的是 GCJ-02 坐标，如果你采集的是 WGS84 坐标，请先进行坐标转换

### Parameters

-   `lng` **number** 经度值
-   `lat` **number** 纬度值
-   `noWrap` **boolean** 是否自动将经度值修正到 [-180,180] 区间内，缺省为false;
    noWrap 为false时传入[190,30]，会被自动修正为[-170,30],
    noWrap 为true时不会自动修正，可以用来进行跨日期限的覆盖物绘制

### Examples

```javascript
var lnglat = new AMap.LngLat(116, 39);
```

### lat

纬度

Type: number

### lng

经度

Type: number

### setLng

设置经度值

#### Parameters

-   `lng` **number** 经度

### setLat

设置纬度值

#### Parameters

-   `lat` **number** 

### getLng

获取经度值

Returns **number** 

### getLat

获取纬度值

Returns **number** 

### equals

判断经纬度坐标和另外一个经纬度坐标是否相等

#### Parameters

-   `another` **LngLat** 另外一个经纬度坐标

Returns **Boolean** 是否相等

### add

与另外一个经纬度相加

#### Parameters

-   `another` **LngLat** 另外一个经纬度坐标
-   `noWrap` **boolean** 是否将相加的结果经度值修正到 [-180,180] 区间内

Returns **LngLat** 两个经纬度相加的结果

### subtract

与另外一个经纬度相减

#### Parameters

-   `another` **LngLat** 另外一个经纬度坐标
-   `noWrap` **boolean** 是否将相减的结果经度值修正到 [-180,180] 区间内

Returns **LngLat** 两个经纬度相减的结果

### offset

获取从当前经纬度位置向东移动 E 米，向北移动 N 米的坐标位置

#### Parameters

-   `E` **Number** 经度方向移动，向东为正
-   `N` **Number** 维度方向移动，向北为正

Returns **LngLat** 移动后的新经纬度

### toString

LngLat对象以字符串的形式返回

Returns **string** 格式如'lng值,lat值'的字符串

### toArray

LngLat对象以字符串的形式返回

Returns **string** 格式如'lng值,lat值'的字符串

### distance

计算当前经纬度距离另一个经纬度或者经纬度数组组成的路径的距离
[相关示例][5]

Returns **number** 距离值，单位为米

## Bounds

地物对象的经纬度矩形范围。

### Parameters

-   `southWest` **LngLat** 西南角经纬度
-   `northEast` **LngLat** 东北角经纬度值

### getSouthWest

获取西南角坐标。

Returns **LngLat** 

### getNorthEast

获取东北角坐标

Returns **LngLat** 

### getNorthEast

获取西北角坐标

Returns **LngLat** 

### getNorthEast

获取东南角坐标

Returns **LngLat** 

### contains

指定点坐标是否在矩形范围内
[相关示例][6]

#### Parameters

-   `obj` **LngLat** 

#### Examples

```javascript
bounds.contains(new AMap.LngLat(116,39));
```

Returns **Boolean** 

### getCenter

获取当前Bounds的中心点经纬度坐标。

Returns **LngLat** 

### toString

以字符串形式返回地图对象的矩形范围

Returns **String** 

## Pixel

像素坐标，确定地图上的一个像素点。

### Parameters

-   `x` **number** 
-   `y` **number** 

### getX

获取像素横坐标

Returns **Number** 

### getY

获取像素纵坐标

Returns **Number** 

### toString

以字符串形式返回像素坐标对象

Returns **string** 

### equals

当前像素坐标与传入像素坐标是否相等

#### Parameters

-   `point` **Pixel** 

Returns **boolean** 

## Size

地物对象的像素尺寸

### Parameters

-   `width` **number** 宽度
-   `height` **number** 高度

### getWidth

获取像素横坐标

Returns **Number** 

### getHeight

获取像素纵坐标

Returns **Number** 

### toString

以字符串形式返回尺寸大小对象

Returns **string** 
