## 自有数据图层

用于加载展示开发者自己拥有的数据或者图像的图层类型


## HeatMap

热力图，基于第三方heatmap.js实现，以特殊高亮的形式显示数据密集程度。根据密集程度的不同，图上会呈现不同的颜色，以直观的形式展现数据密度。API引用了heatmap.js最新版本v2.0，v2.0基于新的渲染模型，具有更高的渲染效率和更强的性能。支持chrome、firefox、safari、ie9及以上浏览器。

### Parameters

-   `map` **Map** 要叠加热力图的地图对象
-   `opts` **HeatMapOptions** 热力图属性配置
    -   `opts.radius` **number** 热力图中单个点的半径，默认：30，单位：pixel
    -   `opts.gradient` **object** 热力图的渐变区间，热力图按照设置的颜色及间隔显示热力图，例{0.4:'rgb(0, 255, 255)',0.85:'rgb(100, 0, 255)',},其中 key 表示间隔位置，取值范围： [0,1]，value 为颜色值。默认：heatmap.js标准配色方案
    -   `opts.opacity` **array** 热力图透明度区间数组，取值范围[0,1]，0表示完全透明，1表示不透明，默认：[0,1]
    -   `opts.zooms` **array** 支持的缩放级别范围，取值范围[3-20]，默认：[3,20]
    -   `opts.visible` **boolean** 是否可见
    -   `opts.zIndex` **number** 热力图层在地图上的叠加顺序，默认 130
    -   `opts.3d` **HeatMap3DOptions** 3D热力图属性
        -   `opts.3d.heightScale` **number** 高度缩放因子，表示在单位高度上的缩放比例， 默认为 1
        -   `opts.3d.heightBezier` **array** 影响高度平滑度的贝塞尔曲线因子，默认 [0.5, 0, 1, 0.5],
        -   `opts.3d.gridSize` **number** 取样精度，越小越平滑，越大性能越高

### Examples

```javascript
var heatmap;
var points = [
   {"lng":116.191031,"lat":39.988585,"count":10},
   {"lng":116.389275,"lat":39.925818,"count":11},
   {"lng":116.287444,"lat":39.810742,"count":12},
   {"lng":116.481707,"lat":39.940089,"count":13},
   {"lng":116.410588,"lat":39.880172,"count":14},
   {"lng":116.394816,"lat":39.91181,"count":15},
   {"lng":116.416002,"lat":39.952917,"count":16},
];
// 加载热力图插件
map.plugin(["AMap.HeatMap"],function(){
   // 在地图对象叠加热力图
   heatmap = new AMap.Heatmap({map:map});
   // 设置热力图数据集
   heatmap.setDataSet({data:points,max:100});
});
```

### getMap

获取热力图叠加地图对象

Returns **Map** 

### setMap

设置热力图要叠加的地图实例，也可以在Map中的layers属性中设置为默认显示的图层

#### Parameters

-   `map` **Map** 地图实例

### getOptions

获取热力图的属性信息

Returns **HeatMapOptions** 

### setOptions

设置热力图属性，请参考 HeatMapOptions 列表中的说明

#### Parameters

-   `options` **HeatMapOptions** 热力图配置

### getDataSet

输出热力图的数据集，数据结构同setDataSet中的数据集

Returns **object** 

### setDataSet

设置热力图展现的数据集，dataset数据集格式为：
{
 max: Number 权重的最大值,
 data: Array 坐标数据集
}，
其中max不填则取数据集count最大值
例： {
  max: 100,
  data: [{lng: 116.405285, lat: 39.904989, count: 65},{}, …]
  }
也可以通过url来加载数据，格式为
{
  data：jsonp格式数据的服务地址URL,
  dataParser: 数据格式转换function //当jsonp返回结果和官方结构不一致的时候，用户可以传递一个函数用来进行数据格式转换；
}
例：
{
  data:'[http://abc.com/jsonp.js'][61],
  dataParser:function(data){
   return doSomthing(data);//返回的对象结果应该与上面例子的data字段结构相同
  }
}

#### Parameters

-   `dataset` **object** 数据集

### addDataPoint

向热力图数据集中添加坐标点，count不填写时默认：1

#### Parameters

-   `longitude` **string** 经度
-   `latitude` **string** 纬度
-   `count` **number** 权重

### getzIndex

获得热力图层叠加层级

Returns **number** 

### setzIndex

设置热力图层叠加层级

#### Parameters

-   `zIndex` **number** 热力图层叠加层级

### show

显示热力图

### hide

隐藏热力图

## VectorLayer

**Extends \_Layer.CoreVectorLayer**

### add

添加矢量覆盖物到集合中，不支持添加重复的覆盖物

#### Parameters

-   `vectors` **(VectorOverlay | Array&lt;VectorOverlay>)** 矢量覆盖物或矢量覆盖物数组

### remove

删除矢量覆盖物

#### Parameters

-   `vectors` **(VectorOverlay | Array&lt;VectorOverlay>)** 矢量覆盖物或矢量覆盖物数组

### show

显示图层

### hide

隐藏图层

### has

判断传入的矢量覆盖物实例是否在VectorLayer这中

#### Parameters

-   `vector` **VectorOverlay** 

Returns **boolean** 

### clear

清空 VectorLayer

### setOptions

批量修改矢量覆盖物属性(包括线样式、样色等等)

#### Parameters

-   `opt` **Object** 

### query

根据经纬度查询矢量覆盖物信息

#### Parameters

-   `geometry` **LngLatLike** 

Returns **(VectorOverlay | undefined)** vector 矢量覆盖物

### getBounds

获取 VectorOverlay 所有覆盖物显示的范围

Returns **(Bounds \| undefined)** 经纬度范围值

## VectorLayer

**Extends \_Layer.CoreVectorLayer**

### Parameters

-   `opts` **Object** 
    -   `opts.visible` **boolean** 是否显示 (optional, default `true`)
    -   `opts.zIndex` **number** 是否显示 (optional, default `110`)

### Examples

```javascript
var layer = new AMap.VectorLayer();
map.add(layer);
var circle = new AMap.circle({center: [116.4, 39.9], radius:1000});
layer.add(circle);
```

### add

添加矢量覆盖物到集合中，不支持添加重复的覆盖物

#### Parameters

-   `vectors` **(VectorOverlay | Array&lt;VectorOverlay>)** 矢量覆盖物或矢量覆盖物数组

### remove

删除矢量覆盖物

#### Parameters

-   `vectors` **(VectorOverlay | Array&lt;VectorOverlay>)** 矢量覆盖物或矢量覆盖物数组

### show

显示图层

### hide

隐藏图层

### has

判断传入的矢量覆盖物实例是否在VectorLayer这中

#### Parameters

-   `vector` **VectorOverlay** 

Returns **boolean** 

### clear

清空 VectorLayer

### setOptions

批量修改矢量覆盖物属性(包括线样式、样色等等)

#### Parameters

-   `opt` **Object** 

### query

根据经纬度查询矢量覆盖物信息

#### Parameters

-   `geometry` **LngLatLike** 

Returns **(VectorOverlay | undefined)** vector 矢量覆盖物

### getBounds

获取 VectorOverlay 所有覆盖物显示的范围

Returns **(Bounds \| undefined)** 经纬度范围值

## LabelsLayer

标注层

### Parameters

-   `opts` **LabelsLayerOptions** 标注层参数
    -   `opts.visible` **boolean** 标注层是否可见，默认值:true
    -   `opts.zIndex` **number** 标注层与其它图层的叠加顺序，默认值：120
    -   `opts.opacity` **number** 标注层透明度
    -   `opts.collision` **boolean** 标注层内的标注是否避让
    -   `opts.allowCollision` **boolean** 标注层内的标注是否允许其它标注层对它避让
    -   `opts.zooms` **\[number, number]** 标注层展示层级范围

### Examples

```javascript
// 创建一个标注层实例
var labelsLayer = new AMap.LabelsLayer({
     collision: true,
     opacity: 1,
     zIndex: 120,
     allowCollision: true,
});
// 将标注层添加到地图上
map.add(labelsLayer);
```

### getCollision

获取标注层是否支持内部标注避让

Returns **any** 

### setCollision

设置标注层是否支持内部标注避让

#### Parameters

-   `collision` **boolean** 默认值: true

### getAllowCollision

获取标注层是否允许其它层标注避让

Returns **boolean** 

### setAllowCollision

设置标注层是否允许其它层标注避让，开启该功能可实现地图标注对 LabelMarker 的避让，[相关示例][63]

#### Parameters

-   `allowCollision` **boolean** 

### getOpacity

获取标注层透明度

Returns **number** 

### setOpacity

设置标注层透明度

#### Parameters

-   `opacity` **number** 

### getZooms

获取标注层显示层级范围

Returns **any** 

### setZooms

设置标注层显示层级范围

#### Parameters

-   `zooms` **\[number]** 

### getzIndex

获取标注层叠加顺序

Returns **number** 

### setzIndex

设置标注层叠加顺序

#### Parameters

-   `zIndex` **number** 

### add

将 labelMarker 添加到标注层上

#### Parameters

-   `labelMarkers` **Array&lt;LabelMarker>** 可添加单个标注或标注数组

### remove

将 labelMarker 从标注层上移除

#### Parameters

-   `labelMarkers` **(LabelMarker \| Array&lt;LabelMarker>)** 可移除单个标注或标注数组

### clear

清空标注层上的标注

### show

显示标注层

### hide

隐藏标注层

### getAllOverlays

获取标注层内的所有标注对象

Returns **Array&lt;any>** 

## CustomLayer

**Extends \_Layer.CoreCustomLayer**

### Parameters

-   `canvas`  
-   `opts`  

### getOptions

获取图层参数信息

Returns **Object** 图层参数信息

### getzIndex

获取图层层级

Returns **Number** zIndex 图层层级

### setzIndex

设置图层层级，数字越大图层层级越高

#### Parameters

-   `zIndex` **Number** 图层层级值

### setzIndex

设置图层层级

#### Parameters

-   `zIndex` **number** 图层层级

### getOpacity

获取图层透明度

Returns **Number** opacity 图层透明度

### setOpacity

设置图层透明度，范围 [0 ~ 1]

#### Parameters

-   `opacity` **Number** 图层透明度

### getZooms

获取该图层可显示的级别范围，默认取值范围为[2-20]

Returns **\[Number, Number]** 缩放范围

### setZooms

获取该图层可显示的级别范围

#### Parameters

-   `zooms` **\[Number, Number]** 缩放范围

### show

设置图层可见

### hide

设置图层隐藏

### setMap

添加到地图上

#### Parameters

-   `地图实例对象` **Map** 

## CustomLayer

**Extends Layer**

自定义图层是一种完全由开发者来指定绘制方法的图层 </br>
[相关示例][65]

### Parameters

-   `canvas` **HTMLCanvasElement** canvas 对象
-   `opts` **CustomLayerOption** 默认图层参数
    -   `opts.render` **Function** 绘制函数，初始化完成时候，开发者需要给该图层设定render方法， </br>
        该方法需要实现图层的绘制，API会在合适的时机自动调用该方法
    -   `opts.zooms` **\[Number, Number]** 图层缩放等级范围，默认 [2, 20] (optional, default `[2,20]`)
    -   `opts.opacity` **Number** 图层透明度，默认为 1 (optional, default `1`)
    -   `opts.visible` **Boolean** 图层是否可见，默认为 true (optional, default `true`)
    -   `opts.zIndex` **Number** 图层的层级，默认为 120 (optional, default `120`)
    -   `opts.alwaysRender` **Boolean** 是否主动 (optional, default `false`)

### Examples

```javascript
var cLayer = new AMap.CustomLayer(canvas, {
     zooms: [2, 18],
     zIndex: 120,
     render() {
         // 对 canvas 进行绘制
     }
})
```

### getOptions

获取图层参数信息

Returns **Object** 图层参数信息

### getzIndex

获取图层层级

Returns **Number** zIndex 图层层级

### setzIndex

设置图层层级，数字越大图层层级越高

#### Parameters

-   `zIndex` **Number** 图层层级值

### setzIndex

设置图层层级

#### Parameters

-   `zIndex` **number** 图层层级

### getOpacity

获取图层透明度

Returns **Number** opacity 图层透明度

### setOpacity

设置图层透明度，范围 [0 ~ 1]

#### Parameters

-   `opacity` **Number** 图层透明度

### getZooms

获取该图层可显示的级别范围，默认取值范围为[2-20]

Returns **\[Number, Number]** 缩放范围

### setZooms

获取该图层可显示的级别范围

#### Parameters

-   `zooms` **\[Number, Number]** 缩放范围

### show

设置图层可见

### hide

设置图层隐藏

### setMap

添加到地图上

#### Parameters

-   `地图实例对象` **Map** 

## Flexible

**Extends TileLayer**

灵活切片图层，继承自AMap.TileLayer，开发者可通过构造时传入给其传入createTile字段来指定每一个切片的内容 </br>
[相关示例][67]

### Parameters

-   `opts` **FlexibleLayerOptions** 
    -   `opts.cacheSize` **Number** 缓存瓦片数量
    -   `opts.createTile` **function (x, y, z, success, fail)** 由开发者实现，由API自动调用，xyz分别为切片横向纵向编号和层级，切片大小
        256。假设每次创建的贴片为A(支持img或者canvas)，当创建或者获取成功时请回调success(A)，不需要显示或者失败时请回调fail()
    -   `opts.zooms` **\[Number, Number]** 支持的缩放级别范围，默认范围 [2-30] (optional, default `[2,30]`)
    -   `opts.opacity` **Number** 透明度，默认 1 (optional, default `1`)
    -   `opts.visible` **Boolean** 是否显示，默认 true (optional, default `true`)
    -   `opts.zIndex` **Number** 图层叠加的顺序值，1 表示最底层。默认 zIndex：4 (optional, default `4`)
    -   `opts.tileSize` **Number** 切片大小，取值： </br>
        256，表示切片大小为256_256， </br>
        128，表示切片大小为128_128， </br>
        64，表示切片大小为64\*64。默认值为256 (optional, default `256`)

### getOptions

获取图层参数信息

Returns **Object** 图层参数信息

### getzIndex

获取图层层级

Returns **Number** zIndex 图层层级

### setzIndex

设置图层层级，数字越大图层层级越高

#### Parameters

-   `zIndex` **Number** 图层层级值

### getOpacity

获取图层透明度

Returns **Number** opacity 图层透明度

### setOpacity

设置图层透明度，范围 [0 ~ 1]

#### Parameters

-   `opacity` **Number** 图层透明度

### getZooms

获取该图层可显示的级别范围，默认取值范围为[2-30]

Returns **\[Number, Number]** 缩放范围

### setZooms

获取该图层可显示的级别范围

#### Parameters

-   `zooms` **\[Number, Number]** 缩放范围

### show

设置图层可见

### hide

设置图层隐藏

### destroy

销毁图层

## ImageLayer

**Extends Layer**

图片图层类，用户可以将一张静态图片作为图层添加在地图上，图片图层会随缩放级别而自适应缩放。 </br>
[相关示例][68]

### Parameters

-   `opts` **ImageLayerOptions** 传入默认参数列表
    -   `opts.url` **String** 图片地址链接
    -   `opts.zooms` **\[Number, Number]** 图层缩放等级范围，默认 [2, 30] (optional, default `[2,30]`)
    -   `opts.bounds` **(\[Number, Number, Number, Number] | Bounds)** 图片的范围大小经纬度，如果传递数字数组类型: [minlng,minlat,maxlng,maxlat]
    -   `opts.opacity` **Number** 图层透明度，默认为 1 (optional, default `1`)
    -   `opts.visible` **Boolean** 图层是否可见，默认为 true (optional, default `true`)
    -   `opts.zIndex` **Number** 图层的层级，默认为 6 (optional, default `6`)

### Examples

```javascript
var imageLayer = new AMap.ImageLayer({
     url: 'https://amappc.cn-hangzhou.oss-pub.aliyun-inc.com/lbs/static/img/dongwuyuan.jpg',
     bounds: new AMap.Bounds(
         [116.327911, 39.939229],
         [116.342659, 39.946275]
     ),
     zooms: [10, 18]
 });
```

### getImageUrl

获取图片的地址

### setImageUrl

设置图片的地址

#### Parameters

-   `url` **String** 图片地址

### getBounds

获取 ImageLayer显示的范围

Returns **Bounds** 经纬度范围值

### setBounds

设置 ImageLayer显示的范围

### getOptions

获取图层参数信息

Returns **object** 图层参数信息

### getzIndex

获取图层层级

Returns **Number** zIndex 图层层级

### setzIndex

设置图层层级，数字越大图层层级越高

#### Parameters

-   `zIndex` **Number** 图层层级值

### getOpacity

获取图层透明度

Returns **Number** opacity 图层透明度

### setOpacity

设置图层透明度，范围 [0 ~ 1]

#### Parameters

-   `opacity` **Number** 图层透明度

### getZooms

获取该图层可显示的级别范围，默认取值范围为[2-20]

Returns **\[number, number]** 缩放范围

### setZooms

获取该图层可显示的级别范围

#### Parameters

-   `zooms` **\[number, number]** 缩放范围

### show

设置图层可见

### hide

设置图层隐藏

## CanvasLayer

**Extends ImageLayer**

Canvas图层类，用户可以将一个 Canvas 作为图层添加在地图上，Canvas图层会随缩放级别而自适应缩放。 </br>
[相关示例][69]

### Parameters

-   `opts` **ImageLayerOptions** 传入默认参数列表
    -   `opts.canvas` **HTMLCanvasElement** Canvas DOM 对象
    -   `opts.zooms` **\[Number, Number]** 图层缩放等级范围，默认 [2, 30] (optional, default `[2,30]`)
    -   `opts.bounds` **(\[Number, Number, Number, Number] | Bounds)** canvas 的范围大小经纬度, 如果传递数字数组类型: [minlng,minlat,maxlng,maxlat]
    -   `opts.opacity` **Number** 图层透明度，默认为 1 (optional, default `1`)
    -   `opts.visible` **Boolean** 图层是否可见，默认为 true (optional, default `true`)
    -   `opts.zIndex` **Number** 图层的层级，默认为 6 (optional, default `6`)

### setCanvas

修改显示的Canvas

#### Parameters

-   `canvas` **HTMLCanvasElement** 

### getElement

返回 Canvas 对象

Returns **HTMLCanvasElement** canvas 对象

### getBounds

返回 canvas 范围的经纬度

Returns **Bounds** 范围经纬度

### getBounds

当canvas的内容发生改变是用于刷新图层，3D视图下调用，2D视图不需要调用

### setBounds

设置 CanvasLayer 显示的范围

### getOptions

获取图层参数信息

Returns **object** 图层参数信息

### getzIndex

获取图层层级

Returns **number** zIndex 图层层级

### setzIndex

设置图层层级，数字越大图层层级越高

#### Parameters

-   `zIndex` **number** 图层层级值

### getOpacity

获取图层透明度

Returns **number** opacity 图层透明度

### setOpacity

设置图层透明度，范围 [0 ~ 1]

#### Parameters

-   `opacity` **number** 图层透明度

### getZooms

获取该图层可显示的级别范围，默认取值范围为[2-20]

Returns **\[number, number]** 缩放范围

### setZooms

获取该图层可显示的级别范围

#### Parameters

-   `zooms` **\[number, number]** 缩放范围

### show

设置图层可见

### hide

设置图层隐藏

## GLCustomLayer

3d 自定义图层

### Parameters

-   `opts` **GlCustomLayerOptions** 
    -   `opts.init` **Function** 初始化的时候，开发者可以在这个函数参数里面获取 gl 上下文，进行一些初始化的操作。
    -   `opts.render` **Function** 绘制函数，初始化完成时候，开发者需要给该图层设定render方法， </br>
        该方法需要实现图层的绘制，API会在合适的时机自动调用该方法
    -   `opts.zooms` **\[Number, Number]** 图层缩放等级范围，默认 [2, 20] (optional, default `[2,20]`)
    -   `opts.opacity` **Number** 图层透明度，默认为 1 (optional, default `1`)
    -   `opts.visible` **Boolean** 图层是否可见，默认为 true (optional, default `true`)
    -   `opts.zIndex` **Number** 图层的层级，默认为 120 (optional, default `10`)

### Examples

```javascript
var glCustomLayer = new GLCustomLayer({
    init: function(gl){
        // init shader or sth...
    },
    render: function(gl, state){
        // render every frame
    },
});
```

### getMap

获取GLCustomLayer所属地图实例

Returns **(Map | null)** 

### getzIndex

获取GLCustomLayer叠加顺序

Returns **number** 

### setzIndex

设置GLCustomLayer叠加顺序

#### Parameters

-   `zIndex` **number** 叠加值

Returns **void** 

### getOpacity

获取GLCustomLayer透明度

Returns **number** 

### setOpacity

设置GLCustomLayer透明度

#### Parameters

-   `opacity` **number** 透明度

Returns **void** 

### getZooms

获取GLCustomLayer显示层级范围

Returns **number** 

### setZooms

设置GLCustomLayer显示层级范围

#### Parameters

-   `zooms` **Vector** 显示层级范围，默认[3, 20]

Returns **number** 

### show

显示GLCustomLayer

Returns **void** 

### hide

隐藏GLCustomLayer

Returns **void** 
