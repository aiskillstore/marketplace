## 高德官方图层

由高德官方提供数据或图像的地图图层


## TileLayer

**Extends Layer**

切片图层类，该类为基础类。 </br>
[相关示例][37]

### Parameters

-   `opts` **TileLayerOptions** 
    -   `opts.tileUrl` **String** 切片取图地址
        如：'[https://abc{0,1,2,3}.amap.com/tile?x=\[x\]&y=\[y\]&z=\[z\]][39]'
        [x]、[y]、[z]分别替代切片的xyz。
    -   `opts.zooms` **\[Number, Number]** 支持的缩放级别范围，默认范围 [2-30] (optional, default `[2,30]`)
    -   `opts.dataZooms` **\[Number, Number]** 数据支持的缩放级别范围，默认范围 [2-30] (optional, default `[2,30]`)
    -   `opts.opacity` **Number** 透明度，默认 1 (optional, default `1`)
    -   `opts.visible` **Boolean** 是否显示，默认 true (optional, default `true`)
    -   `opts.zIndex` **Number** 图层叠加的顺序值，1 表示最底层。默认 zIndex：4 (optional, default `4`)
    -   `opts.tileSize` **Number** 切片大小，取值：
        256，表示切片大小为256_256，
        128，表示切片大小为128_128，
        64，表示切片大小为64\*64。默认值为256 (optional, default `256`)

### setTileUrl

设置图层的取图地址

#### Parameters

-   `url` **String** 瓦片图地址

### reload

重新加载图层资源，重新渲染

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

## Traffic

**Extends TileLayer**

实时交通图层类，继承自TileLayer。 </br>
[相关示例][40]

### Parameters

-   `opts` **TrafficLayerOptions** 
    -   `opts.autoRefresh` **Boolean** 是否自动更新数据，默认开启
    -   `opts.interval` **Number** 自动更新数据的间隔毫秒数，默认 180ms
    -   `opts.zooms` **\[Number, Number]** 支持的缩放级别范围，默认范围 [2-30] (optional, default `[2,30]`)
    -   `opts.opacity` **Number** 透明度，默认 1 (optional, default `1`)
    -   `opts.visible` **Boolean** 是否显示，默认 true (optional, default `true`)
    -   `opts.zIndex` **Number** 图层叠加的顺序值，1 表示最底层。默认 zIndex：4 (optional, default `4`)
    -   `opts.tileSize` **Number** 切片大小，取值：
        256，表示切片大小为256_256，
        128，表示切片大小为128_128，
        64，表示切片大小为64\*64。默认值为256 (optional, default `256`)

### stopFresh

停止自动更新数据

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

## Satellite

**Extends TileLayer**

### Parameters

-   `opts`   (optional, default `satelliteDefaultOptions`)

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

## Satellite

**Extends TileLayer**

### Parameters

-   `opts`   (optional, default `satelliteDefaultOptions`)

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

## Satellite

**Extends TileLayer**

### Parameters

-   `opts`   (optional, default `satelliteDefaultOptions`)

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

## Satellite

**Extends TileLayer**

### Parameters

-   `opts`   (optional, default `satelliteDefaultOptions`)

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

## Satellite

**Extends TileLayer**

### Parameters

-   `opts`   (optional, default `satelliteDefaultOptions`)

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

## Satellite

**Extends TileLayer**

### Parameters

-   `opts`   (optional, default `satelliteDefaultOptions`)

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

## Satellite

**Extends TileLayer**

卫星图层类，继承自 TileLayer。
[相关示例][41]

### Parameters

-   `opts` **SatelliteLayerOptions** 
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

## RoadNet

**Extends TileLayer**

路网图层，展示道路信息 </br>
[相关示例][42]

### Parameters

-   `opts` **RoadnetLayerOptions** 
    -   `opts.zooms` **\[Number, Number]** 支持的缩放级别范围，默认范围 [2-30] (optional, default `[2,30]`)
    -   `opts.opacity` **Number** 透明度，默认 1 (optional, default `1`)
    -   `opts.visible` **Boolean** 是否显示，默认 true (optional, default `true`)
    -   `opts.zIndex` **Number** 图层叠加的顺序值，1 表示最底层。默认 zIndex：4 (optional, default `4`)
    -   `opts.tileSize` **Number** 切片大小，取值： </br>
        256，表示切片大小为256_256， </br>
        128，表示切片大小为128_128， </br>
        64，表示切片大小为64\*64。默认值为256 (optional, default `256`)

### show

设置图层可见

### hide

设置图层隐藏

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

### destroy

销毁图层

## Buildings

**Extends Layer**

建筑楼块 3D 图层 </br>
[相关示例][43]

### Parameters

-   `opts` **BuildingLayerOpts** 
    -   `opts.wallColor` **(Array&lt;String> | String)** 楼块侧面颜色，支持 rgba、rgb、十六进制等
    -   `opts.roofColor` **(Array&lt;String> | String)** 楼块顶面颜色，支持 rgba、rgb、十六进制等
    -   `opts.heightFactor` **Number** 楼块的高度系数因子，默认为 1，也就是正常高度
    -   `opts.styleOpts` **BuildingStyleOptions** 楼块的围栏和样式设置
    -   `opts.zooms` **\[Number, Number]** 图层缩放等级范围，默认 [2, 20] (optional, default `[2,20]`)
    -   `opts.opacity` **Number** 图层透明度，默认为 1 (optional, default `1`)
    -   `opts.visible` **Boolean** 图层是否可见，默认为 true (optional, default `true`)
    -   `opts.zIndex` **Number** 图层的层级，默认为 11 (optional, default `11`)

### Examples

```javascript
var buildingLayer = new AMap.Buildings({
    heightFactor: 1,
    wallColor: [255, 0, 0, 1],
    roofColor: 'rgba(0,0,255,0.5)',
});
map.addLayer(buildingLayer);
```

### setStyle

设置楼块图层样式 </br>
[相关示例][43]

#### Parameters

-   `styleOpts` **BuildingStyleOptions** 样式
    -   `styleOpts.hideWithoutStyle` **Boolean** 是否隐藏围栏之外的楼块
    -   `styleOpts.areas` **Array&lt;Area>** 围栏信息数组
        -   `styleOpts.areas.rejectTexture` **Boolean** 是否隐藏围栏之外的楼块
        -   `styleOpts.areas.visible` **Boolean** 围栏信息数组
        -   `styleOpts.areas.path` **Array&lt;Number>** 围栏经纬度列表
        -   `styleOpts.areas.color1` **(Array&lt;String> | String)** 围栏区域内楼块顶面颜色，支持 rgba、rgb、十六进制等
        -   `styleOpts.areas.color2` **(Array&lt;String> | String)** 围栏区域内楼块侧面颜色，支持 rgba、rgb、十六进制等

#### Examples

```javascript
var options = {
    hideWithoutStyle:false,//是否隐藏设定区域外的楼块
    areas:[{ //围栏1
          //visible:false,//是否可见
          rejectTexture:true,//是否屏蔽自定义地图的纹理
          color1: 'ffffff00',//楼顶颜色
          color2: 'ffffcc00',//楼面颜色
          path: [[116.473606,39.995997],[116.473005,39.995482],[116.474179,39.996516],[116.473606,39.995997]]
   }, { //围栏2
          color1: 'ff99ff00',
          color2: 'ff999900',
          path: [[116.474609,39.993478],[116.474489,39.993495],[116.47469,39.99348],[116.474609,39.993478]]
  }]
};
buildingLayer.setStyle(options); //此配色优先级高于自定义mapStyle
```

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

## DistrictLayer

**Extends \_Layer.CoreDistrictLayer**

### Parameters

-   `opts`  

### setSOC

设定显示的国家 SOC

#### Parameters

-   `SOC` **String** SOC

### setDistricts

设置 adcodes 值

#### Parameters

-   `adcodes` **(Array&lt;any> | string \| number)** adcodes

### getDistricts

获取 adcodes

Returns **any** adcodes

### setStyles

设置样式信息

#### Parameters

-   `styles` **DistrictLayerStyle** 样式信息

### getStyles

获取样式信息

Returns **DistrictLayerStyle** 样式

### setAdcode

设置 adcodes 值

#### Parameters

-   `adcodes` **(Array&lt;any> | string \| number)** adcodes

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

### World

世界级行政区
[相关示例][46]

### Country

国家级行政区
[相关示例][47]

### Province

省份级行政区,只支持中国区域
[相关示例][48]

## DistrictLayer

**Extends Layer**

### Parameters

-   `opts` **DistrictLayerOptions** 图层初始化参数
    -   `opts.adcode` **String** 行政区的编码 [adcode与省市行政区对照表][49]
    -   `opts.SOC` **String** 设定显示的国家
        [SOC 国家代码、名称、Bounds对照表下载][50] (optional, default `'CHN'`)
    -   `opts.depth` **Number** 设定数据的层级深度，depth为0的时候只显示国家面，depth为1的时候显示省级，
        当国家为中国时设置depth为2的可以显示市一级 (optional, default `0`)
    -   `opts.zIndex` **Number** 图层的层级，默认为 80 (optional, default `80`)
    -   `opts.opacity` **Number** 图层透明度，默认为 1 (optional, default `1`)
    -   `opts.visible` **Boolean** 图层是否可见，默认为 true (optional, default `true`)
    -   `opts.zooms` **\[number, number]** 图层缩放等级范围，默认 [2, 20] (optional, default `[2,20]`)
    -   `opts.styles` **DistrictLayerStyle** 为简易行政区图设定各面的填充颜色和描边颜色。
        styles各字段的值可以是颜色值，也可以是一个返回颜色值\* 的回调函数function。支持的颜色格式有： </br>
        1\. #RRGGBB，如：'#FFFFFF' </br>
        2\. rgba()，如：'rgba(255,255,255,1)' </br>
        3\. rgb()，如：'rgb(255,255,255)' </br>
        4\. [r,g,b,a]，如：[1,1,1,1] </br>
        5\. ''，代表不赋予颜色
        -   `opts.styles.stroke-width` **(Number \| Function)** 描边线宽 (optional, default `1`)
        -   `opts.styles.zIndex` **(Number \| Function)** 图层中每个区域层级，数值越大，层级越高 (optional, default `0`)
        -   `opts.styles.coastline-stroke` **(Array&lt;String> | String \| Function)** 海岸线颜色 (optional, default `[0.18,0.63,0.94,1]`)
        -   `opts.styles.nation-stroke` **(Array&lt;String> | String \| Function)** 国境线颜色 (optional, default `[0.35,0.35,0.35,1]`)
        -   `opts.styles.province-stroke` **(Array&lt;String> | String \| Function)** 省界颜色 (optional, default `[0.5,0.5,0.5,1]`)
        -   `opts.styles.city-stroke` **(Array&lt;String> | String \| Function)** 城市界颜色 (optional, default `[0.7,0.7,0.7,1]`)
        -   `opts.styles.county-stroke` **(Array&lt;String> | String \| Function)** 区/县界颜色 (optional, default `[0.85,0.85,0.85,1]`)
        -   `opts.styles.fill` **(Array&lt;String> | String \| Function)** 填充色 (optional, default `[1,1,1,1]`)

### setSOC

设定显示的国家 SOC

#### Parameters

-   `SOC` **String** SOC

### setDistricts

设置 adcodes 值

#### Parameters

-   `adcodes` **(Array&lt;any> | string \| number)** adcodes

### getDistricts

获取 adcodes

Returns **any** adcodes

### setStyles

设置样式信息

#### Parameters

-   `styles` **DistrictLayerStyle** 样式信息

### getStyles

获取样式信息

Returns **DistrictLayerStyle** 样式

### setAdcode

设置 adcodes 值

#### Parameters

-   `adcodes` **(Array&lt;any> | string \| number)** adcodes

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

### World

世界级行政区
[相关示例][46]

### Country

国家级行政区
[相关示例][47]

### Province

省份级行政区,只支持中国区域
[相关示例][48]

## IndoorMap

**Extends \_layer.IndoorLayer**

### Parameters

-   `opts`  

### showIndoorMap

显示指定 POI 的室内地图

#### Parameters

-   `indoorid` **String** 建筑物 POIID (必填) [如何获取][51]
-   `floor` **Number** 楼层
-   `shopid` **String** 商铺 ID

### showFloor

显示指定的楼层

#### Parameters

-   `floor` **number** 楼层

### show

显示室内地图

### hide

隐藏室内地图

### setMap

设置显示室内图层的地图对象

#### Parameters

-   `map` **Map** 

### setzIndex

设置室内地图的显示顺序

#### Parameters

-   `index` **number** 

### showFloorBar

显示楼层切换控件

### hideFloorBar

隐藏楼层切换控件

### setOpacity

设置室内图层透明度

#### Parameters

-   `opacity` **number** 

### getOpacity

获取室内图层透明度

Returns **number** 

### showLabels

显示室内图层上的标注

### hideLabels

隐藏室内图层上的标注

### getSelectedBuildingId

获取被选中室内的 POIID

### getSelectedBuilding

获取被选中的室内地图的一些基本信息，包含名称、当前楼层、所有楼层信息、POIID等

## IndoorMap

室内图层，用于在适当级别展示室内地图，并提供显示商铺tip、切换楼层等功能。

### Parameters

-   `opts` **IndoorMapOptions** 
    -   `opts.zIndex` **Number** 室内图层叠加的顺序值
    -   `opts.opacity` **Number** 图层的透明度，取值范围[0,1]
    -   `opts.cursor` **String** 指定鼠标悬停到店铺面时的鼠标样式
    -   `opts.hideFloorBar` **Boolean** 是否隐藏楼层切换控件，默认值：false

### Examples

```javascript
用法一：创建独立的室内图层
var indoorMap = new AMap.IndoorMap({
 zIndex: 1000, // 设置室内图层叠加顺序
 opacity: 1, // 设置室内图层透明度
});
var map = new AMap.Map('mapDiv', {
 showIndoorMap: false, //隐藏地图默认的室内地图图层
 layers: [indoorMap, AMap.createDefaultLayer()] // 添加室内等图层
});
indoorMap.showIndoorMap('B0FFFAB6J2'); // 显示指定 POI 室内信息

用法二：调用默认室内图层
var map = new AMap.Map('mapDiv',{
 showIndoorMap: true, //显示地图默认的室内地图图层
});
map.on('indoor_create',function(){
 map.indoorMap.showIndoorMap('B000A8VT15',4); // 显示指定 POI 室内信息
})
```

### showIndoorMap

显示指定 POI 的室内地图

#### Parameters

-   `indoorid` **String** 建筑物 POIID (必填) [如何获取][51]
-   `floor` **Number** 楼层
-   `shopid` **String** 商铺 ID

### showFloor

显示指定的楼层

#### Parameters

-   `floor` **number** 楼层

### show

显示室内地图

### hide

隐藏室内地图

### setMap

设置显示室内图层的地图对象

#### Parameters

-   `map` **Map** 

### setzIndex

设置室内地图的显示顺序

#### Parameters

-   `index` **number** 

### showFloorBar

显示楼层切换控件

### hideFloorBar

隐藏楼层切换控件

### setOpacity

设置室内图层透明度

#### Parameters

-   `opacity` **number** 

### getOpacity

获取室内图层透明度

Returns **number** 

### showLabels

显示室内图层上的标注

### hideLabels

隐藏室内图层上的标注

### getSelectedBuildingId

获取被选中室内的 POIID

### getSelectedBuilding

获取被选中的室内地图的一些基本信息，包含名称、当前楼层、所有楼层信息、POIID等
