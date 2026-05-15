## 路线规划

用于驾车、货车、骑行、步行、公交等的路线规划查询


## Driving

驾车路线规划服务，提供起、终点坐标的驾车导航路线[查询功能][109]。AMap. Driving构造函数的参数为 DrivingOptions 对象。DrivingOptions 允许设置驾车策略和返回信息详略。用户可以通过自定义回调函数取回并显示查询结果。若服务请求失败，系统将返回错误信息

### Parameters

-   `opts` **DrivingOptions** 参数信息
    -   `opts.map` **Map** AMap.Map对象, 展现结果的地图实例。当指定此参数后，搜索结果的标注、线路等均会自动添加到此地图上。可选
    -   `opts.policy` **number?** [驾车路线规划策略][110]
    -   `opts.extensions` **string** 默认值：base，返回基本地址信息\\n当取值为：all，返回DriveStep基本信息+DriveStep详细信息 (optional, default `'base'`)
    -   `opts.ferry` **number** 默认为0，表示可以使用轮渡，为1的时候表示不可以使用轮渡 (optional, default `0`)
    -   `opts.panel` **(string \| HTMLElement)?** 结果列表的HTML容器id或容器元素，提供此参数后，结果列表将在此容器中进行展示。可选
    -   `opts.hideMarkers` **boolean** 设置隐藏路径规划的起始点图标
        设置为true：隐藏图标；设置false：显示图标\\n默认值为：false (optional, default `false`)
    -   `opts.showTraffic` **boolean?** 设置是否显示实时路况信息，默认设置为true。
        显示绿色代表畅通，黄色代表轻微拥堵，红色代表比较拥堵，灰色表示无路况信息。
    -   `opts.province` **string?** 车牌省份的汉字缩写，用于判断是否限行，与number属性组合使用，可选。例如：京
    -   `opts.number` **string?** 除省份之外车牌的字母和数字，用于判断限行相关，与province属性组合使用，可选。例如:NH1N11
    -   `opts.isOutline` **boolean?** 使用map属性时，绘制的规划线路是否显示描边。缺省为true
    -   `opts.outlineColor` **string?** 使用map属性时，绘制的规划线路的描边颜色。缺省为'white'
    -   `opts.autoFitView` **boolean?** 用于控制在路径规划结束后，是否自动调整地图视野使绘制的路线处于视口的可见范围

### Examples

```javascript
var driving;
mapObj.plugin(["AMap.Driving"], function() { //加载驾车服务插件
   var drivingOptions = {
       //驾车策略，包括 LEAST_TIME，LEAST_FEE, LEAST_DISTANCE,REAL_TRAFFIC
       policy: AMap.DrivingPolicy.LEAST_TIME
   };
   driving = new AMap.Driving(drivingOptions);
   AMap.Event.addListener(driving, "complete", driving_CallBack); //返回导航查询结果
   //根据起终点坐标规划驾车路线
   MDrive.search(new AMap.LngLat(116.379018, 39.865026), new AMap.LngLat(116.42732, 39.903752));
});
```

### search

根据起点、终点和途经点（可选）坐标或名称，实现驾车路线规划，途经点通过opts设定

#### Parameters

-   `origin` **LngLat** 起点经纬度
-   `destination` **LngLat** 终点经纬度
-   `opts` **Object** 
    -   `opts.waypoints` **Array&lt;LngLat>** 途径点,最多支持16个
-   `callback` **DrivingCallback** status为complete时，result为DrivingResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果。

### search

根据起点、终点和途经点（可选）坐标或名称，实现驾车路线规划，途经点通过opts设定

#### Parameters

-   `points` **Array&lt;Object>** 终点经纬度points为起点、终点和途经点（可选）名称及对应城市的数组，例如：
    [{keyword:‘北京南站’,city:‘北京市’},{keyword:‘广东大厦’,city:’北京市’},{ keyword:‘北京西站’,city:‘北京市’}]
    系统取数组第一个元素和最后一个元素作为起点和终点，中间元素为途经点；
-   `callback` **DrivingCallback** status为complete时，result为DrivingResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果。

### clear

清除搜索结果

### setAvoidPolygons

设置避让区域，最大支持三个避让区域，参数为LngLat的二维数组

#### Parameters

-   `areas` **Array&lt;Array&lt;LngLatLike>>** 

### clearAvoidPolygons

清除避让区域

### getAvoidPolygons

获取避让区域，返回LngLat的二维数组

Returns **Array&lt;Array&lt;LngLat>>** 避让区域

### setAvoidRoad

设置避让道路名称，只支持一条避让道路
注：避让道路和避让区域不能同时使用

#### Parameters

-   `value` **string** 

### clearAvoidRoad

清除避让道路

### getAvoidRoad

获取避让道路

Returns **string** 

### setProvinceAndNumber

设置车牌的汉字首字符和首字后的号码，设置后路线规划的结果将考虑该车牌在当前时间的限行路段

#### Parameters

-   `province` **string** 
-   `number` **string** 

### setPolicy

设置驾车路线规划策略

#### Parameters

-   `policy` **Object** 驾车路线规划策略

## DrivingCallback

Driving.search 的回调函数

Type: Function

### Parameters

-   `status` **string** status为complete时，result为DrivingResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果
-   `result` **(info | DrivingResult)** 

## DrivingResult

DrivingResult 对象

Type: Object

### Properties

-   `info` **string** 成功状态说明
-   `origin` **LngLat** 驾车规划起点坐标
-   `destination` **LngLat** 驾车规划终点坐标
-   `start` **Poi** 驾车规划起点
-   `end` **Poi** 驾车规划终点
-   `waypoints` **Poi** 驾车规划途经点
-   `taxi_cost` **number** 打车费用，仅extensions为“all”时返回. 单位: 元
-   `routes` **Array&lt;DriveRoute>** 驾车规划路线列表
    -   `routes.route` **DriveRoute** 驾车规划路线列表元素
        -   `routes.route.distance` **number** 起点到终点的驾车距离，单位：米
        -   `routes.route.time` **number** 时间预计，单位：秒
        -   `routes.route.policy` **string** 驾车规划策略
        -   `routes.route.tolls` **number** 此驾车路线收费金额，单位：元
        -   `routes.route.tolls_distance` **number** 收费路段长度，单位：米
        -   `routes.route.restriction` **number** 限行结果,0 代表限行已规避或未限行，即该路线没有限行路段,1 代表限行无法规避，即该线路有限行路段
-   `steps` **Array&lt;(DriveStepBasic \| DriveStepDetail)>** 子路段DriveStep集合

## DriveStepBasic

DriveStep 对象(基本信息)

Type: Object

### Properties

-   `start_location` **LngLat** 此路段起点
-   `end_location` **LngLat** 此路段终点
-   `instruction` **string** 此路段说明，如“沿北京南站路行驶565米右转”
-   `action` **string** 本驾车子路段完成后动作
-   `assist_action` **string** 驾车子路段完成后辅助动作，一般为到达某个目的地时返回
-   `orientation` **string** 驾车方向
-   `road` **string** 驾车方向
-   `distance` **number** 此路段距离，单位：米
-   `tolls` **number** 此段收费，单位：元
-   `tolls_distance` **number** 收费路段长度，单位：米
-   `toll_road` **string** 主要收费道路
-   `time` **number** 此路段预计使用时间，单位：秒
-   `path` **Array&lt;LngLat>** 此路段坐标集合

## DriveStepDetail

DriveStep 对象(详细信息)

Type: Object

### Properties

-   `cities` **Array&lt;ViaCity>** 途径城市列表
    -   `cities.city` **ViaCity** 途径城市列表元素
        -   `cities.city.name` **string** 途径名称
        -   `cities.city.citycode` **string** 城市编码
        -   `cities.city.adcode` **string** 区域编码
        -   `cities.city.districts` **Array&lt;District>** 途径行政区列表
            -   `cities.city.districts.district` **District** 途径行政区列表元素
                -   `cities.city.districts.district.name` **string** 区域名称
                -   `cities.city.districts.district.adcode` **string** 区域编码
-   `tmcs` **Array&lt;TMC>** 实时交通信息列表
    -   `tmcs.tmc` **TMC** 实时交通信息列表元素
        -   `tmcs.tmc.lcode` **string** 路况信息对应的编码
            如果direction是正向 lcode返回值大于0；否则lcode，返回值小于0；
            如果返回0则说明此路段无lcode
        -   `tmcs.tmc.distance` **number** 此lcode对应的路段长度，单位: 米
        -   `tmcs.tmc.status` **string** 路况状态，可能的值有：未知，畅通，缓行，拥堵

## TruckDriving

驾车路线规划服务，提供起、终点坐标的驾车导航路线[查询功能][115]。AMap. Driving构造函数的参数为 DrivingOptions 对象。DrivingOptions 允许设置驾车策略和返回信息详略。用户可以通过自定义回调函数取回并显示查询结果。若服务请求失败，系统将返回[错误信息][116]

### Parameters

-   `opts` **TruckDrivingOptions** 参数信息
    -   `opts.map` **Map** AMap.Map对象, 展现结果的地图实例。当指定此参数后，搜索结果的标注、线路等均会自动添加到此地图上。可选
    -   `opts.policy` **number?** [货车路线规划策略strategy][117]
    -   `opts.size` **number** 车型大小，必填，1-4分别对应小型至大型
    -   `opts.width` **number** 宽度，缺省2.5米 (optional, default `2.5`)
    -   `opts.height` **number** 高度,缺省1.6米 (optional, default `1.6`)
    -   `opts.load` **number** 载重,缺省0.9t (optional, default `0.9`)
    -   `opts.weight` **number** 自重，缺省10t (optional, default `10`)
    -   `opts.axlesNum` **number** 轴数，缺省2轴 (optional, default `2`)
    -   `opts.extensions` **string** 默认值：base，返回基本地址信息\\n当取值为：all，返回DriveStep基本信息+DriveStep详细信息 (optional, default `'base'`)
    -   `opts.panel` **(string \| HTMLElement)?** 结果列表的HTML容器id或容器元素，提供此参数后，结果列表将在此容器中进行展示。可选
    -   `opts.hideMarkers` **boolean** 设置隐藏路径规划的起始点图标
        设置为true：隐藏图标；设置false：显示图标\\n默认值为：false (optional, default `false`)
    -   `opts.showTraffic` **boolean?** 设置是否显示实时路况信息，默认设置为true。
        显示绿色代表畅通，黄色代表轻微拥堵，红色代表比较拥堵，灰色表示无路况信息。
    -   `opts.province` **string?** 车牌省份的汉字缩写，用于判断是否限行，与number属性组合使用，可选。例如：京
    -   `opts.number` **string?** 除省份之外车牌的字母和数字，用于判断限行相关，与province属性组合使用，可选。例如:NH1N11
    -   `opts.isOutline` **boolean?** 使用map属性时，绘制的规划线路是否显示描边。缺省为true
    -   `opts.outlineColor` **string?** 使用map属性时，绘制的规划线路的描边颜色。缺省为'white'
    -   `opts.autoFitView` **boolean?** 用于控制在路径规划结束后，是否自动调整地图视野使绘制的路线处于视口的可见范围

### Examples

```javascript
var driving;
mapObj.plugin(["AMap.TruckDriving"], function() { //加载驾车服务插件
   var drivingOptions = {
       //驾车策略，包括 LEAST_TIME，LEAST_FEE, LEAST_DISTANCE,REAL_TRAFFIC
       policy: AMap.DrivingPolicy.LEAST_TIME
   };
   driving = new AMap.TruckDriving(drivingOptions);
   AMap.Event.addListener(driving, "complete", driving_CallBack); //返回导航查询结果
   //根据起终点坐标规划驾车路线
   MDrive.search(new AMap.LngLat(116.379018, 39.865026), new AMap.LngLat(116.42732, 39.903752));
});
```

```javascript
var TruckDriving;
mapObj.plugin(["AMap.TruckDriving"], function() { //加载驾车服务插件
   var TruckDrivingOptions = {
       //驾车策略，包括 LEAST_TIME，LEAST_FEE, LEAST_DISTANCE,REAL_TRAFFIC
       policy: AMap.TruckDrivingPolicy.LEAST_TIME
   };
   TruckDriving = new AMap.TruckDriving(TruckDrivingOptions);
   AMap.Event.addListener(TruckDriving, "complete", TruckDriving_CallBack); //返回导航查询结果
   //根据起终点坐标规划驾车路线
   MDrive.search(new AMap.LngLat(116.379018, 39.865026), new AMap.LngLat(116.42732, 39.903752));
});
```

### clear

清除搜索结果

### search

根据起点、终点和途经点（可选）坐标或名称，实现驾车路线规划，途经点通过opts设定

#### Parameters

-   `locations` **Array&lt;Truck~Location>** 途经点列表
    -   `locations.location` **Truck~Location** 某一个途经点
        -   `locations.location.lnglat` **\[number, number]** 经纬度
        -   `locations.location.pid` **string** POI ID,可缺省
        -   `locations.location.type` **string** POI类型，可缺省
-   `callback` **DrivingCallback** status为complete时，result为TruckResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果。

### search

根据起点、终点和途经点（可选）坐标或名称，实现驾车路线规划，途经点通过opts设定

#### Parameters

-   `points` **Array&lt;Truck~Path>** 途经点列表 例如 : [{keyword:'北京站',city:'010'},//起点
    {keyword:'北京西站',city:'010'},//途径
    {keyword:'北京大学',city:'010'}//终点
    ]
    -   `points.point` **Truck~Path** 某个途经点
        -   `points.point.keyworkd` **string** 关键字
        -   `points.point.city` **string** 城市code
-   `callback` **DrivingCallback** status为complete时，result为TruckResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果。

### setProvinceAndNumber

修改车牌号

#### Parameters

-   `province` **string** 
-   `number` **number** 

### setPolicy

设置驾车路线规划策略,参考opts.policy

#### Parameters

-   `policy` **Object** 驾车路线规划策略，参考opts.policy

## Walking

步行路线规划服务，提供起、终点坐标的驾车导航路线[查询功能][119]。AMap. Driving构造函数的参数为 DrivingOptions 对象。DrivingOptions 允许设置驾车策略和返回信息详略。用户可以通过自定义回调函数取回并显示查询结果。若服务请求失败，系统将返回[错误信息][116]

### Parameters

-   `opts` **WalkingOptions** 参数信息
    -   `opts.map` **Map** AMap.Map对象, 展现结果的地图实例。当指定此参数后，搜索结果的标注、线路等均会自动添加到此地图上。可选
    -   `opts.panel` **(string \| HTMLElement)?** 结果列表的HTML容器id或容器元素，提供此参数后，结果列表将在此容器中进行展示。可选
    -   `opts.hideMarkers` **boolean** 设置隐藏路径规划的起始点图标
        设置为true：隐藏图标；设置false：显示图标\\n默认值为：false
        显示绿色代表畅通，黄色代表轻微拥堵，红色代表比较拥堵，灰色表示无路况信息。 (optional, default `false`)
    -   `opts.isOutline` **boolean?** 使用map属性时，绘制的规划线路是否显示描边。缺省为true
    -   `opts.outlineColor` **string?** 使用map属性时，绘制的规划线路的描边颜色。缺省为'white'
    -   `opts.autoFitView` **boolean?** 用于控制在路径规划结束后，是否自动调整地图视野使绘制的路线处于视口的可见范围

### Examples

```javascript
var mwalk;
  mapObj.plugin(["AMap.Walking"], function() { //加载步行导航插件
   mwalk = new AMap.Walking (); //构造步行导航类
   AMap.event.addListener(mwalk, "complete", walking_CallBack); //返回导航查询结果
   //根据起、终点坐标规划步行路线
   mwalk.search(new AMap.LngLat(116.379018, 39.865026), new AMap.LngLat(116.42732, 39.903752));
 });
```

```javascript
var mwalk;
  mapObj.plugin(["AMap.Walking"], function() { //加载步行导航插件
   mwalk = new AMap.Walking (); //构造步行导航类
   AMap.Event.addListener(mwalk, "complete", walking_CallBack); //返回导航查询结果
   //根据起、终点坐标规划步行路线
   mwalk.search(new AMap.LngLat(116.379018, 39.865026), new AMap.LngLat(116.42732, 39.903752));
 });
```

### clear

清除搜索的结果

### search

根据起点、终点坐标，实现步行路线规划

#### Parameters

-   `origin` **LngLat** 起点经纬度
-   `destination` **LngLat** 终点经纬度
-   `callback` **WalkingCallback** status为complete时，result为 WalkingResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果。

### search

根据起点、终点名称，实现步行路线规划

#### Parameters

-   `points` **Array&lt;Object>** 终点经纬度points为起点、终点和途经点（可选）名称及对应城市的数组，例如：
    [{keyword:‘方恒国际中心A座’},{keyword:‘望京站’}]
    系统取数组第一个元素和最后一个元素作为起点和终点，中间元素为途经点；
-   `callback` **WalkingCallback** status为complete时，result为 WalkingResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果。

## WalkingCallback

Walking.search 的回调函数

Type: Function

### Parameters

-   `status` **string** status为complete时，result为 WalkingResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果
-   `result` **(info | WalkingResult)** 

## WalkingResult

WalkingResult 对象

Type: Object

### Properties

-   `info` **string** 成功状态说明
-   `origin` **LngLat** 步行规划起点坐标
-   `destination` **LngLat** 步行规划终点坐标
-   `start` **Poi** 步行规划起点
-   `end` **Poi** 步行规划终点
-   `count` **number** 步行导航路段数目
-   `routes` **Array&lt;WalkRoute>** 步行规划路线列表
    -   `routes.distance` **number** 起点到终点总步行距离，单位：米
    -   `routes.time` **number** 步行时间预计，单位：秒
    -   `routes.steps` **Array&lt;WalkStep>** 路段列表，以道路名称作为分段依据，将整个步行导航方案分隔成若干路段
        -   `routes.steps.instruction` **string** 步行子路段描述,规则：沿 road步行 distance 米 action，例：”沿北京站街步行351米”
        -   `routes.steps.distance` **number** 步行子路段距离，单位：米
        -   `routes.steps.time` **number** 步行子路段预计使用时间，单位：秒
        -   `routes.steps.path` **Array&lt;LngLat>** 步行子路段坐标集合
        -   `routes.steps.road` **string** 道路
        -   `routes.steps.action` **string** 本步行子路段完成后动作
        -   `routes.steps.assist_action` **string** 步行子路段完成后辅助动作，一般为到达某个公交站点或目的地时返回

## Transfer

公交换乘服务，提供起始点公交路线规划服务，目前公交换乘仅支持同一城市的公交路线规划，跨城市出行规划请参考驾车导航查询。公交换乘查询返回结果整合步行信息，若换乘路段（Segment）换乘类型为地铁 “SUBWAY”，则至少包含一条地铁口信息（SubwayEntrance）。用户可以通过自定义回调函数取回并显示查询结果。若服务请求失败，系统将返回错误信息。

### Parameters

-   `opts` **DrivingOptions** 参数信息
    -   `opts.map` **Map** AMap.Map对象, 展现结果的地图实例。当指定此参数后，搜索结果的标注、线路等均会自动添加到此地图上。可选
    -   `opts.city` **string** 公交换乘的城市，支持城市名称、城市区号、电话区号，此项为必填
    -   `opts.policy` **number** [公交换乘策略strategy][122]
    -   `opts.nightflag` **boolean** 是否计算夜班车，默认为不计算。true：计算，false：不计算 (optional, default `false`)
    -   `opts.extensions` **string** 默认值：base，返回基本地址信息\\n当取值为：all，返回DriveStep基本信息+DriveStep详细信息 (optional, default `'base'`)
    -   `opts.panel` **(string \| HTMLElement)?** 结果列表的HTML容器id或容器元素，提供此参数后，结果列表将在此容器中进行展示。可选
    -   `opts.hideMarkers` **boolean** 设置隐藏路径规划的起始点图标
        设置为true：隐藏图标；设置false：显示图标\\n默认值为：false (optional, default `false`)
    -   `opts.isOutline` **boolean?** 使用map属性时，绘制的规划线路是否显示描边。缺省为true
    -   `opts.outlineColor` **string?** 使用map属性时，绘制的规划线路的描边颜色。缺省为'white'
    -   `opts.autoFitView` **boolean?** 用于控制在路径规划结束后，是否自动调整地图视野使绘制的路线处于视口的可见范围

### Examples

```javascript
var trans;
mapObj.plugin(["AMap.Transfer"], function() { //加载公交换乘插件
   transOptions = {
       city: '北京市', //公交城市
       policy: AMap.TransferPolicy.LEAST_TRANSFER //乘车策略
   };
   trans = new AMap.Transfer (transOptions); //构造公交换乘类
   AMap.Event.addListener(trans, "complete", trans_CallBack); //返回导航查询结果
   AMap.Event.addListener(trans, "error", function(e){alert(e.info);}); //返回错误信息
   //根据起、终点坐标查询公交换乘路线
   trans.search(new AMap.LngLat(116.379018, 39.865026), new AMap.LngLat(116.42732, 39.903752));
});
```

### search

根据起点和终点坐标，进行公交换乘查询

#### Parameters

-   `origin` **LngLat** 起点经纬度
-   `destination` **LngLat** 终点经纬度
-   `callback` **TransferCallback** status为complete时，result为DrivingResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果。

### search

根据起点和终点坐标，进行公交换乘查询

#### Parameters

-   `points` **Array&lt;Object>** 当根据起、终点名称查询时，point为包含起点、终点的数组，例：
    [{keyword:‘北京南站’},{keyword:‘北京西站’}]
    当数组超过两个元素时，取前两个元素为起点、终点，其余元素忽略
-   `callback` **TransferCallback** status为complete时，result为DrivingResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果。

### leaveAt

设置公交路径规划出发时间

#### Parameters

-   `time` **string** 
-   `date` **string** 

### clear

清除结果显示

### setPolicy

设置公交换乘策略

#### Parameters

-   `policy` **TransferPolicy** 公交换乘策略

### setCity

设置公交换乘查询的城市

#### Parameters

-   `city` **String** 城市

### setCityd

设置公交换乘查询的目的地城市

#### Parameters

-   `cityd` **String** 城市

## TransferCallback

Transfer.search 的回调函数 [相关示例][124]

Type: Function

### Parameters

-   `status` **string** 当status为complete时，result为TransferResult；
    当status为error时，result为错误信息info；
    当status为no_data时，代表检索返回0结果
-   `result` **(info | TransferResult)** 

## TransferResult

TransferResult 对象 [详细文档][122],查阅rest接口 '返回结果参数说明'

Type: Object

## Riding

骑行路线规划服务，提供起、终点坐标的驾车导航路线[查询功能][119]。AMap. Driving构造函数的参数为 DrivingOptions 对象。DrivingOptions 允许设置驾车策略和返回信息详略。用户可以通过自定义回调函数取回并显示查询结果。若服务请求失败，系统将返回[错误信息][116]

### Parameters

-   `opts` **RidingOptions** 参数信息
    -   `opts.map` **Map** AMap.Map对象, 展现结果的地图实例。当指定此参数后，搜索结果的标注、线路等均会自动添加到此地图上。可选
    -   `opts.policy` **number** 骑行路线规划策略；默认值：0可选值为：
        0：推荐路线及最快路线综合
        1：推荐路线
        2：最快路线 (optional, default `0`)
    -   `opts.panel` **(string \| HTMLElement)?** 结果列表的HTML容器id或容器元素，提供此参数后，结果列表将在此容器中进行展示。可选
    -   `opts.hideMarkers` **boolean** 设置隐藏路径规划的起始点图标
        设置为true：隐藏图标；设置false：显示图标\\n默认值为：false
        显示绿色代表畅通，黄色代表轻微拥堵，红色代表比较拥堵，灰色表示无路况信息。 (optional, default `false`)
    -   `opts.isOutline` **boolean?** 使用map属性时，绘制的规划线路是否显示描边。缺省为true
    -   `opts.outlineColor` **string?** 使用map属性时，绘制的规划线路的描边颜色。缺省为'white'
    -   `opts.autoFitView` **boolean?** 用于控制在路径规划结束后，是否自动调整地图视野使绘制的路线处于视口的可见范围

### Examples

```javascript
var mwalk;
  mapObj.plugin(["AMap.Riding"], function() { //加载步行导航插件
   mwalk = new AMap.Riding (); //构造步行导航类
   AMap.Event.addListener(mwalk, "complete", riding_CallBack); //返回导航查询结果
   //根据起、终点坐标规划步行路线
   mwalk.search(new AMap.LngLat(116.379018, 39.865026), new AMap.LngLat(116.42732, 39.903752));
 });
```

### clear

清除搜索的结果

### setPolicy

骑行路线规划策略

#### Parameters

-   `policy` **number** 可选值为：
    0：推荐路线及最快路线综合
    1：推荐路线
    2：最快路线

### search

根据起点、终点坐标，实现骑行路线规划

#### Parameters

-   `origin` **LngLat** 起点经纬度
-   `destination` **LngLat** 终点经纬度
-   `callback` **RidingCallback** status为complete时，result为 RidingResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果。

### search

根据起点、终点名称，实现骑行路线规划

#### Parameters

-   `points` **Array&lt;Object>** 包含起点、终点的数组，例：[{keyword:‘方恒国际中心A座’},{keyword:‘望京站’}]
    当数组超过两个元素时，取前两个元素为起点、终点，其余元素忽略；
-   `callback` **RidingCallback** status为complete时，result为 RidingResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果。

## RidingCallback

Riding.search 的回调函数

Type: Function

### Parameters

-   `status` **string** status为complete时，result为 RidingResult；当status为error时，result为错误信息info；当status为no_data时，代表检索返回0结果
-   `result` **(info | RidingResult)** 

## RidingResult

RidingResult [详细文档][128],查阅rest接口'返回结果参数说明'

Type: Object

## DragRoute

### Parameters

-   `map` **Map** 指定的地图对象
-   `path` **Array&lt;LngLat>** 导航的起点、途经点、终点的经纬度坐标数组
-   `policy` **String** [指定驾车策略][110]
-   `opts` **DragRouteOptions** 配置项
    -   `opts.polyOption` **PolylineOptions?** 设置拖拽路线插件的路线属性对象，包括线样式、宽度、颜色等，参考PolylineOptions列表
    -   `opts.startMarkerOptions` **MarkerOptions?** 设置拖拽路线插件起点点标记属性对象，包括点标记样式、大小等，参考MarkerOptions列表
    -   `opts.midMarkerOptions` **MarkerOptions?** 设置拖拽路线插件途经点点标记属性对象，包括点标记样式、大小等，参考MarkerOptions列表
    -   `opts.endMarkerOptions` **MarkerOptions?** 设置拖拽路线插件终点点标记属性对象，包括点标记样式、大小等，参考MarkerOptions列表
    -   `opts.showTraffic` **boolean** 设置显示实时路况信息，true：路线中显示实时路况信息，false：关闭实时路况信息。 默认值：true (optional, default `true`)

### Examples

```javascript
var arr = new Array();//经纬度坐标数组
arr.push(new AMap.LngLat("116.403322","39.920255")); //初始的导航起点
arr.push(new AMap.LngLat("116.420703","39.897555")); //初始的导航途经点
arr.push(new AMap.LngLat("116.430703","39.897555")); //初始的导航途经点
arr.push(new AMap.LngLat("116.410703","39.897555")); //初始的导航终点
AMap.plugin(['AMap.DragRoute'],function(){
   dragRoute = new AMap.DragRoute(mapObj, arr, AMap.DrivingPolicy.LEAST_FEE);
   dragRoute.search(); //查询导航路径并开启拖拽导航
});
```

### search

开始路径导航。支持鼠标拖拽导航路径节点，更改途经点时，系统实时重新计算并显示导航路径

### getWays

返回除了起点和终点之外的所有点返回导航的所有途经点，即所有途径点的坐标数组

Returns **Array&lt;LngLat>** 所有途经点坐标

### getRoute

返回当前导航路径，即导航路径的经纬度坐标数组

Returns **Array&lt;LngLat>** 当前导航路径

### destroy

销毁拖拽导航插件。

## DragRouteTruck

可拖拽货车路径规划

### Parameters

-   `map` **Map** 指定的地图对象
-   `opts` **DragRouteTruckOptions** 配置项
    -   `opts.polyOption` **PolylineOptions?** 设置拖拽路线插件的路线属性对象，包括线样式、宽度、颜色等，参考PolylineOptions列表
    -   `opts.startMarkerOptions` **MarkerOptions?** 设置拖拽路线插件起点点标记属性对象，包括点标记样式、大小等，参考MarkerOptions列表
    -   `opts.midMarkerOptions` **MarkerOptions?** 设置拖拽路线插件途经点点标记属性对象，包括点标记样式、大小等，参考MarkerOptions列表
    -   `opts.endMarkerOptions` **MarkerOptions?** 设置拖拽路线插件终点点标记属性对象，包括点标记样式、大小等，参考MarkerOptions列表
    -   `opts.showTraffic` **boolean** 设置显示实时路况信息，true：路线中显示实时路况信息，false：关闭实时路况信息。 默认值：true (optional, default `true`)
    -   `opts.policy` **number?** 驾车路线规划策略
        1躲避拥堵
        2不走高速
        3避免收费
        4躲避拥堵且不走高速
        5避免收费且不走高速
        6躲避拥堵且避免收费
        7躲避拥堵且避免收费且不走高速
        8高速优先
        9躲避拥堵且高速优先
    -   `opts.size` **number** 车型大小，必填，1-4分别对应小型至大型
    -   `opts.width` **number** 宽度，缺省2.5米 (optional, default `2.5`)
    -   `opts.height` **number** 高度,缺省1.6米 (optional, default `1.6`)
    -   `opts.load` **number** 载重,缺省0.9t (optional, default `0.9`)
    -   `opts.weight` **number** 自重，缺省10t (optional, default `10`)
    -   `opts.axlesNum` **number** 轴数，缺省2轴 (optional, default `2`)
    -   `opts.extensions` **string** 默认值：base，返回基本地址信息\\n当取值为：all，返回DriveStep基本信息+DriveStep详细信息 (optional, default `'base'`)
    -   `opts.panel` **(string \| HTMLElement)?** 结果列表的HTML容器id或容器元素，提供此参数后，结果列表将在此容器中进行展示。可选
    -   `opts.hideMarkers` **boolean** 设置隐藏路径规划的起始点图标
        设置为true：隐藏图标；设置false：显示图标\\n默认值为：false (optional, default `false`)
    -   `opts.showTraffic` **boolean?** 设置是否显示实时路况信息，默认设置为true。
        显示绿色代表畅通，黄色代表轻微拥堵，红色代表比较拥堵，灰色表示无路况信息。
    -   `opts.province` **string?** 车牌省份的汉字缩写，用于判断是否限行，与number属性组合使用，可选。例如：京
    -   `opts.number` **string?** 除省份之外车牌的字母和数字，用于判断限行相关，与province属性组合使用，可选。例如:NH1N11
    -   `opts.isOutline` **boolean?** 使用map属性时，绘制的规划线路是否显示描边。缺省为true
    -   `opts.outlineColor` **string?** 使用map属性时，绘制的规划线路的描边颜色。缺省为'white'
    -   `opts.autoFitView` **boolean?** 用于控制在路径规划结束后，是否自动调整地图视野使绘制的路线处于视口的可见范围
    -   `opts.cartype` **number** 车辆类型 0：普通货车（默认值）1：纯电动货车 2：插电混动货车 (optional, default `0`)
    -   `opts.showpolyline` **number** 是否返回路线数据 当取值为1时，steps与tmcs下的polyline数据会正常返回；当取值为0时，steps与tmcs下的polyline数据为空。 (optional, default `1`)
    -   `opts.nosteps` **number** 是否返回steps字段内容 当取值为0时，steps字段内容正常返回；当取值为1时，steps字段内容为空。 (optional, default `1`)
    -   `opts.autoRefresh` **boolean** 是否拖拽后自动更新驾车轨迹 (optional, default `true`)
    -   `opts.refreshTime` **number** 拖拽后自动更新的延迟时间 (optional, default `300`)
    -   `opts.apiVersion` **number** 货车接口版本支持 'v4','v5' (optional, default `'v4'`)
    -   `opts.showFields` **string?** 仅 v5货车接口版本支持 1、具体可指定返回的字段类请见下方返回结果说明中的“show_fields”内字段类型；
        2、多个字段间采用“,”进行分割；
        3、show_fields未设置时，只返回基础信息类内字段；
        4、目前取值支持以下四种："toll_gate"，"cameras"，"general"，"incident"；
        "toll_gate"：收费站信息
        "cameras"：电子眼信息
        "general"：交通设施信息
        "incident"：交通事件信息

### Examples

```javascript
var arr = new Array();//经纬度坐标数组
path.push({ lnglat: [116.303843, 39.983412] });//起点
path.push({ lnglat: [116.321354, 39.896436] });//途径
path.push({ lnglat: [116.407012, 39.992093] });//终点
AMap.plugin(['AMap.DragRouteTruck'],function(){
   dragRoute = new AMap.DragRouteTruck(mapObj, opts);
   dragRoute.search(path); //查询导航路径并开启拖拽导航
});
```

### setAvoidPolygons

设置避让区域，最大支持三个避让区域，参数为LngLat的二维数组

#### Parameters

-   `areas` **Array&lt;Array&lt;LngLatLike>>** 

### clearAvoidPolygons

清除避让区域

### getAvoidPolygons

获取避让区域，返回LngLat的二维数组

Returns **Array&lt;Array&lt;LngLat>>** 避让区域

### search

开始路径导航。支持鼠标拖拽导航路径节点，更改途经点时，系统实时重新计算并显示导航路径

#### Parameters

-   `locations`  : Array&lt;{lnglat:LngLatLike}>

### updatePath

手动更新路径。设置 autoRefresh 为 false 之后，通过调用这个方法来手动更新路径规划

### getWays

返回除了起点和终点之外的所有点返回导航的所有途经点，即所有途径点的坐标数组

Returns **Array&lt;LngLat>** 所有途经点坐标

### getRoute

返回当前导航路径，即导航路径的经纬度坐标数组

Returns **Array&lt;LngLat>** 当前导航路径

### destroy

销毁拖拽导航插件。

### setOption

修改配置项

#### Parameters

-   `opts` **Object** 
    -   `opts.policy` **number?** 驾车路线规划策略
        1躲避拥堵
        2不走高速
        3避免收费
        4躲避拥堵且不走高速
        5避免收费且不走高速
        6躲避拥堵且避免收费
        7躲避拥堵且避免收费且不走高速
        8高速优先
        9躲避拥堵且高速优先
    -   `opts.size` **number** 车型大小，必填，1-4分别对应小型至大型
    -   `opts.width` **number** 宽度，缺省2.5米 (optional, default `2.5`)
    -   `opts.height` **number** 高度,缺省1.6米 (optional, default `1.6`)
    -   `opts.load` **number** 载重,缺省0.9t (optional, default `0.9`)
    -   `opts.weight` **number** 自重，缺省10t (optional, default `10`)
    -   `opts.axlesNum` **number** 轴数，缺省2轴 (optional, default `2`)
    -   `opts.extensions` **string** 默认值：base，返回基本地址信息\\n当取值为：all，返回DriveStep基本信息+DriveStep详细信息 (optional, default `'base'`)
    -   `opts.panel` **(string \| HTMLElement)?** 结果列表的HTML容器id或容器元素，提供此参数后，结果列表将在此容器中进行展示。可选
    -   `opts.hideMarkers` **boolean** 设置隐藏路径规划的起始点图标
        设置为true：隐藏图标；设置false：显示图标\\n默认值为：false (optional, default `false`)
    -   `opts.showTraffic` **boolean?** 设置是否显示实时路况信息，默认设置为true。
        显示绿色代表畅通，黄色代表轻微拥堵，红色代表比较拥堵，灰色表示无路况信息。
    -   `opts.province` **string?** 车牌省份的汉字缩写，用于判断是否限行，与number属性组合使用，可选。例如：京
    -   `opts.number` **string?** 除省份之外车牌的字母和数字，用于判断限行相关，与province属性组合使用，可选。例如:NH1N11
    -   `opts.isOutline` **boolean?** 使用map属性时，绘制的规划线路是否显示描边。缺省为true
    -   `opts.outlineColor` **string?** 使用map属性时，绘制的规划线路的描边颜色。缺省为'white'
    -   `opts.autoFitView` **boolean?** 用于控制在路径规划结束后，是否自动调整地图视野使绘制的路线处于视口的可见范围
    -   `opts.cartype` **number** 车辆类型 0：普通货车（默认值）1：纯电动货车 2：插电混动货车 (optional, default `0`)
    -   `opts.showpolyline` **number** 是否返回路线数据 当取值为1时，steps与tmcs下的polyline数据会正常返回；当取值为0时，steps与tmcs下的polyline数据为空。 (optional, default `1`)
    -   `opts.nosteps` **number** 是否返回steps字段内容 当取值为0时，steps字段内容正常返回；当取值为1时，steps字段内容为空。 (optional, default `1`)

## GraspRoad

**Extends AMap.Event**

轨迹纠偏服务插件。用于将一组带方向的、可能偏离道路的经纬度轨迹，纠正为准确沿着道路的一条经纬度路径。比如根据间隔采集的车辆位置和朝向信息生成行驶轨迹

### driving

用于驾车轨迹的纠偏。

#### Parameters

-   `OriginPath` **Array&lt;Object>** 
    -   `OriginPath.x` **number** 经度
    -   `OriginPath.y` **number** 纬度
    -   `OriginPath.ag` **number** 与正北方向的顺时针夹角，[ 0, 360 ]
    -   `OriginPath.tm` **number** 轨迹点采集的时间，以s为单位 OriginPath数组第一个元素的tm值为从1970年开始的unix的时间戳，精确到秒。
        其余元素的tm值为当前采集点的时间减去第一个元素的采集时间的差值
    -   `OriginPath.sp` **number** 轨迹点的速度，单位 km/h，小数、整数均可
-   `callback` **GraspRoadCallback** 回调函数

## GraspRoadCallback

Type: Function

### Parameters

-   `err` **Object** 正确时为空
-   `GraspedPath` **Object** 返回数据，[详查rest文档][131]
    -   `GraspedPath.distance` **number** 总距离
    -   `GraspedPath.data` **Object** 
        -   `GraspedPath.data.points` **Array&lt;Object>** 轨迹点数据
            -   `GraspedPath.data.points.x` **number** 经度
            -   `GraspedPath.data.points.x` **number** 纬度
