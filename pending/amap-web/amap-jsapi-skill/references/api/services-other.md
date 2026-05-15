## 其他服务

行政区查询、天气查询、公交站点和公交线路查询


## DistrictSearch

**Extends AMap.Event**

行政区查询服务（AMap.DistrictSearch）提供行政区信息的查询，
使用该服务可以获取到行政区域的区号、城市编码、中心点、边界、下辖区域等详细信息，为基于行政区域的地图功能提供支持。

### Parameters

-   `opts` **DistrictSearchOptions** 默认参数
-   `level` **string** 关键字对应的行政区级别或商圈，可选值：
    country：国家
    province：省/直辖市
    city：市
    district：区/县
    biz_area：商圈
-   `showbiz` **boolean** 是否显示商圈，默认值true
    可选为true/false，为了能够精准的定位到街道，特别是在快递、物流、送餐等场景下，强烈建议将此设置为false
-   `extensions` **string** 是否返回行政区边界坐标点，默认值：base，不返回行政区边界坐标点，取值：all，返回完整行政区边界坐标点
-   `subdistrict` **number** 显示下级行政区级数（行政区级别包括：国家、省/直辖市、市、区/县4个级别），商圈为区/县下一
    级，可选值：0、1、2、3，默认值：1
    0：不返回下级行政区
    1：返回下一级行政区
    2：返回下两级行政区
    3：返回下三级行政区

### Examples

```javascript
AMap.plugin('AMap.DistrictSearch', function () {
  var districtSearch = new AMap.DistrictSearch({
    // 关键字对应的行政区级别，country表示国家
    level: 'country',
    //  显示下级行政区级数，1表示返回下一级行政区
    subdistrict: 1
  })
  // 搜索所有省/直辖市信息
  districtSearch.search('中国', function(status, result) {
    // 查询成功时，result即为对应的行政区信息
  })
})
// 除了获取所有省份/直辖市信息外，您可以通过修改level和subdistrict并配合search传入对应keyword查询对应信息。
```

### setLevel

设置关键字对应的行政区级别或商圈，可选值：
country：国家
province：省/直辖市
city：市
district：区/县
biz_area：商圈

#### Parameters

-   `level` **string** 设置级别

### setSubdistrict

设置下级行政区级数（行政区级别包括：国家、省/直辖市、市、区/县4个级别），商圈为区/县下一级，默认值：1
可选值：0、1、2、3
0：不返回下级行政区；
1：返回下一级行政区；
2：返回下两级行政区；
3：返回下三级行政区；

#### Parameters

-   `subdistrict` **string** 下级行政区级数

### search

根据关键字查询行政区或商圈信息 关键字支持：行政区名、citycode、adcode、商圈名。默认值：“全国”
当status为complete时，result为DistrictSearchResult；
当status为error时，result为错误信息info；
当status为no_data时，代表检索返回0结果

#### Parameters

-   `keyword`  
-   `DistrictSearchCallBack` **function (status: String, result: info/DistrictSearchResult)** 回调函数
-   `keywords` **string** 查询的关键字

## Weather

天气查询服务，根据城市名称或区域编码返回城市天气预报信息，包括实时天气信息和四天天气预报。

### Examples

```javascript
map.plugin(['AMap.Weather'], function() {
	//构造 Weather 类
	var amapWeather = new AMap.Weather(); 

	//查询实时天气信息，cityName 见 http://restapi.amap.com/v3/config/district?level=city&sublevel=0&extensions=all&output=xml&key=d9fba2f3196b6a4419358693a2b0d9a9
	amapWeather.getLive('北京'); 

	//查询四天预报天气，包括查询当天天气信息
	amapWeather.getForecast('北京'); 

	AMap.event.addListener(amapWeather, "complete", function callback(){
		//当查询成功时触发 complete 事件
	}); 
});
```

### getLive

查询实时天气信息。

#### Parameters

-   `city` **String** 城市名称/区域编码（如：“杭州市”/“330100”）
-   `callback` **WeatherLiveResult** 回调函数

### getForecast

查询四天预报天气，包括查询当天天气信息

#### Parameters

-   `city` **String** 
-   `callback` **WeatherForecastResult** 回调函数

## WeatherLiveResult

Type: Function

### Parameters

-   `err` **Object** 正确时为空
-   `LiveData` **Object** 返回数据
    -   `LiveData.info` **String** 成功状态文字描述
    -   `LiveData.province` **String** 省份名
    -   `LiveData.city` **String** 城市名
    -   `LiveData.adcode` **String** 区域编码
    -   `LiveData.weather` **String** 天气现象，详见天气现象列表
    -   `LiveData.temperature` **String** 实时气温，单位：摄氏度
    -   `LiveData.windDirection` **String** 风向，风向编码对应描述
    -   `LiveData.windPower` **Number** 风力，风力编码对应风力级别，单位：级
    -   `LiveData.humidity` **String** 空气湿度（百分比）
    -   `LiveData.reportTime` **String** 数据发布的时间

## WeatherForecastResult

Type: Function

### Parameters

-   `err` **Object** 正确时为空
-   `ForecastData` **Object** 返回数据
    -   `ForecastData.info` **String** 成功状态文字描述
    -   `ForecastData.province` **String** 省份名
    -   `ForecastData.city` **String** 城市名
    -   `ForecastData.adcode` **String** 区域编码
    -   `ForecastData.reportTime` **String** 数据发布的时间
    -   `ForecastData.forecast` **Array** 天气预报数组，包括当天至第三天的预报数据
        -   `ForecastData.forecast.date` **String** 日期，格式为“年-月-日”
        -   `ForecastData.forecast.week` **String** 星期
        -   `ForecastData.forecast.dayWeather` **String** 白天天气现象，详见天气现象列表
        -   `ForecastData.forecast.nightWeather` **String** 夜间天气现象，详见天气现象列表
        -   `ForecastData.forecast.dayTemp` **Number** 白天温度
        -   `ForecastData.forecast.nightTemp` **Number** 白天温度
        -   `ForecastData.forecast.dayWindDir` **String** 白天风向
        -   `ForecastData.forecast.dayWindPower` **String** 白天风力
        -   `ForecastData.forecast.nightWindPower` **String** 夜间风力

## StationSearch

**Extends AMap.Event**

AMap.StationSearch 公交站点查询服务，根据输入关键字、ID查询公交站点信息。
用户可以通过自定义回调函数取回并显示查询结果。若服务请求失败，系统将返回错误信息。

### Parameters

-   `opts` **StationSearchOptions** 参数信息
    -   `opts.pageIndex` **Number** 页码（如pageIndex为2，pageSize为10，那么显示的应是第11-20条返回结果）
        默认值：1，取值范围：1-100，超过取值范围按默认，超出实际页数按最大值返回
    -   `opts.pageSize` **Number** 单页显示结果条数，默认值：20，取值范围：1-100，超过取值范围按默认
    -   `opts.city` **String** 公交站点所在城市，默认值：“全国”，可选值：cityname（中文或中文全拼）、citycode、adcode

### Examples

```javascript
//加载公交站点查询插件
mapObj.plugin(["AMap.StationSearch"], function() {
   //实例化公交站点查询类
   var station = new AMap.StationSearch({
       pageIndex: 1, //页码
       pageSize: 10, //单页显示结果条数
       city:'010'    //确定搜索城市
   });
   station.search('东直门'); //查询
   AMap.event.addListener(station, 'complete', stationSearch_CallBack);
   AMap.event.addListener(station, 'error', function(e) {alert(e.info);});
});
```

### setPageIndex

设置查询结果页码，默认值：1 取值范围：1-100，超过取值范围按默认

#### Parameters

-   `pageIndex` **Number** 结果页码

### setPageSize

设置单页显示结果条数，默认值：20 取值范围：1-100，超过取值范围按默认

#### Parameters

-   `pageSize` **Number** 单页显示结果条数

### setCity

设置查询城市，默认值：“全国” 可选值：cityname（中文或中文全拼）、citycode、adcode

#### Parameters

-   `city` **String** 查询城市

### setCity

根据给定的公交站点id进行公交站点详情检索，id是公交站点的唯一标识
当status为complete时，result为StationSearchResult；
当status为error时，result为错误信息info；
当status为no_data时，代表检索返回0结果

#### Parameters

-   `id` **String** 公交站点 id

### setCity

根据给定公交站点名称进行公交站点详情查询，多个关键字用"|"分割，status说明同上 [相关示例][134]

#### Parameters

-   `keyword` **String** 公交站点名称
-   `StationSearchCallback` **String** 回调函数

### StationSearchOptions

Type: Object

#### Properties

-   `pageIndex` **Number** 页码（如pageIndex为2，pageSize为10，那么显示的应是第11-20条返回结果），默认值：1 取值范围：1-100，超过取值范围按默认; 超出实际页数，按最大值
-   `pageSize` **Number** 单页显示结果条数，默认值：20
-   `city` **String** 公交线路所在城市

## LineSearch

**Extends AMap.Event**

AMap.LineSearch 公交路线查询类，通过extensions属性控制返回信息详略。
公交线路信息包括起、终点、途径站点，首、末班车时间等信息。用户可以通过自定义回调函数取回并显示查询结果。
若服务请求失败，系统将返回[错误信息][135]。

### Parameters

-   `opts` **LineSearchOptions** 参数信息
    -   `opts.pageIndex` **Number** 页码（如pageIndex为2，pageSize为10，那么显示的应是第11-20条返回结果）
        默认值：1，取值范围：1-100，超过取值范围按默认，超出实际页数按最大值返回
    -   `opts.pageSize` **Number** 单页显示结果条数，默认值：20，取值范围：1-100，超过取值范围按默认
    -   `opts.city` **String** 公交站点所在城市，默认值：“全国”，可选值：cityname（中文或中文全拼）、citycode、adcode
-   `extensions` **String** 此项仅公交路线查询时有效，默认值：base，返回公交路线基本信息，当取值为：all，返回公交路线基本信息+详细信息

### Examples

```javascript
//加载公交线路查询插件
mapObj.plugin(["AMap.LineSearch"], function() {
    //实例化公交线路查询类
    var linesearch = new AMap.LineSearch({
        pageIndex:1,
        pageSize:1,
        extensions:'all'
    });
    //搜索“536”相关公交线路
    linesearch.search('536');
    AMap.event.addListener(linesearch, "complete", lineSearch_Callback);
   AMap.event.addListener(citysearch, "error", function(e){alert(e.info);});
});
```

### setPageIndex

设置查询结果页码，默认值：1 取值范围：1-100，超过取值范围按默认

#### Parameters

-   `pageIndex` **Number** 结果页码

### setPageSize

设置单页显示结果条数，默认值：20 取值范围：1-100，超过取值范围按默认

#### Parameters

-   `pageSize` **Number** 单页显示结果条数

### setCity

设置查询城市，默认值：“全国” 可选值：cityname（中文或中文全拼）、citycode、adcode

#### Parameters

-   `city` **String** 城市

### setCity

设置查询城市，默认值：“全国” 可选值：cityname（中文或中文全拼）、citycode、adcode

#### Parameters

-   `city` **String** 查询城市

### setCity

根据给定的公交站点id进行公交站点详情检索，id是公交站点的唯一标识
当status为complete时，result为LineSearchResult；
当status为error时，result为错误信息info；
当status为no_data时，代表检索返回0结果

#### Parameters

-   `id` **String** 公交站点 id

### setCity

根据给定公交站点名称进行公交站点详情查询，多个关键字用"|"分割，status说明同上 [相关示例][136]

#### Parameters

-   `keyword` **String** 公交站点名称
-   `LineSearchCallback` **String** 回调函数

### LineSearchOptions

Type: Object

#### Properties

-   `pageIndex` **Number** 页码（如pageIndex为2，pageSize为10，那么显示的应是第11-20条返回结果），默认值：1 取值范围：1-100，超过取值范围按默认; 超出实际页数，按最大值
-   `pageSize` **Number** 单页显示结果条数，默认值：20
-   `city` **String** 公交线路所在城市
-   `extensions` **String** 此项仅公交路线查询时有效 默认值：base，返回公交路线基本信息 当取值为：all，返回公交路线基本信息+详细信息
