## 地理编码

用于经纬度与地址之间的相互查询


## Geocoder

**Extends AMap.Event**

AMap.Geocoder 地理编码与逆地理编码类，用于地址描述与经纬度坐标之间的转换。用户可以通过回调函数获取查询结果。
[相关示例][103]

### Parameters

-   `opts` **GeocoderOptions** 
    -   `opts.city` **string** <div>
        <div>城市，地理编码时，设置地址描述所在城市</div>
        <div>可选值：城市名（中文或中文全拼）、citycode、adcode</div>
        <div>默认值：“全国”</div>
        </div>
    -   `opts.radius` **number** <div>
        <div>逆地理编码时，以给定坐标为中心点，单位：米</div>
        <div>取值范围：0 - 3000</div>
        <div>默认值：1000</div>
        </div>
    -   `opts.lang` **string** <div>设置语言类型</div>
        <div>可选值：zh_cn（中文）、en(英文)</div>
        <div>默认值：zh_cn（中文</div>
    -   `opts.batch` **boolean** 是否批量查询<div>batch 设置为 false 时，只返回第一条记录</div>
    -   `opts.extensions` **string** 逆地理编码时，返回信息的详略<div>默认值：base，返回基本地址信息 </div>
        <div>取值为：all，返回地址信息及附近poi、道路、道路交叉口等信息 </div>

### Examples

```javascript
var geocoder;
//加载地理编码插件
mapObj.plugin(["AMap.Geocoder"], function() { //加载地理编码插件
   geocoder = new AMap.Geocoder({
       radius: 1000, //以已知坐标为中心点，radius为半径，返回范围内兴趣点和道路信息
       extensions: "all" //返回地址描述以及附近兴趣点和道路信息，默认“base”
   });
   //返回地理编码结果
   geocoder.on("complete", geocoder_CallBack);
   //逆地理编码
   geocoder.getAddress(new AMap.LngLat(116.359119, 39.972121));
});
```

### getLocation

将地址信息转化为高德经纬度坐标信息

#### Parameters

-   `keyword` **String** 关键字
-   `cbk` **GeocoderCallback** 回调函数

### setCity

地理编码时，设置地址描述所在城市

#### Parameters

-   `city` **String** 所在城市

### getAddress

将高德经纬度坐标信息转化为结构化的地址信息

#### Parameters

-   `location` **(LngLat \| Array&lt;LngLat>)** 给定坐标
-   `cbk` **ReGeocoderCallback** 回调函数

## GeocoderCallback

Geocoder getLocation 回调函数

Type: Function

### Parameters

-   `status` **string** 当status为complete时，result为GeocodeResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果
-   `result` **(info | GeocodeResult)** 地理编码 [详查rest文档][106]

## ReGeocoderCallback

Geocoder getAddress 回调函数

Type: Function

### Parameters

-   `status` **string** 当status为complete时，result为GeocodeResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果
-   `result` **(info | ReGeocodeResult)** 逆地理编码 [详查rest文档][107]

## convertFrom

地球上同一个地理位置的经纬度，在不同的坐标系中，会有少于偏移，国内目前常见的坐标系主要分为三种： </br>
1\. 地球坐标系——WGS84：常见于 GPS 设备，Google 地图等国际标准的坐标体系。 </br>
2\. 火星坐标系——GCJ-02：中国国内使用的被强制加密后的坐标体系，高德坐标就属于该种坐标体系。 </br>
3\. 百度坐标系——BD-09：百度地图所使用的坐标体系，是在火星坐标系的基础上又进行了一次加密处理。 </br>
因此在使用不同坐标系前，我们需要使用 AMap.convertFrom() 方法将这些非高德坐标系进行转换。 </br>
[相关示例][108]

### Parameters

-   `lnglat` **LngLat** 需要转换的坐标或者坐标组
-   `type` **String** 坐标类型 (optional, default `'gps'`)
-   `cbk` **Function?** 转换成功后的回调函数

### Examples

```javascript
var gps = [116.3, 39.9];
AMap.convertFrom(gps, 'gps', function (status, result) {
  if (result.info === 'ok') {
    var lnglats = result.locations; // Array.<LngLat>
  }
});
```
