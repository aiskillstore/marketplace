## 搜索

用于进行 POI 搜索联想与数据查询的相关类型


## AutoComplete

根据输入关键字提示匹配信息，可将Poi类型和城市作为输入提示的限制条件。用户可以通过自定义回调函数取回并显

### Parameters

-   `opts` **object** 输入提示参数
    -   `opts.type` **string** 输入提示时限定POI类型，多个类型用“|”分隔，目前只支持Poi类型编码如“050000” 默认值：所有类别
    -   `opts.city` **string** 输入提示时限定城市。可选值：城市名（中文或中文全拼）、citycode、adcode；默认值：“全国”
    -   `opts.datatype` **string** 返回的数据类型。可选值：all-返回所有数据类型、poi-返回POI数据类型、bus-返回公交站点数据类型、busline-返回公交线路数据类型目前暂时不支持多种类型
    -   `opts.citylimit` **boolean** 是否强制限制在设置的城市内搜索,默认值为：false，true：强制限制设定城市，false：不强制限制设定城市
    -   `opts.input` **(string \| HTMLDivElement)** 可选参数，用来指定一个input输入框，设定之后，在input输入文字将自动生成下拉选择列表。支持传入输入框DOM对象的id值，或直接传入输入框的DOM对象。
    -   `opts.output` **(string \| HTMLDivElement)** 可选参数，指定一个现有的div的id或者元素，作为展示提示结果的容器，当指定了input的时候有效，缺省的时候将自动创建一个显示结果面板
    -   `opts.outPutDirAuto` **boolean** 默认为true，表示是否在input位于页面较下方的时候自动将输入面板显示在input上方以避免被遮挡
    -   `opts.closeResultOnScroll` **boolean** 页面滚动时关闭搜索结果列表，默认 true
    -   `opts.lang` **string** 设置检索语言类型，默认中文 'zh_cn'

### Examples

```javascript
var auto;
//加载输入提示插件
map.plugin(['AMap. Autocomplete'], function() {
    let autoOptions = {
        city: '010' //城市，默认全国
    };
    auto = new AMap.Autocomplete(autoOptions);
}};
```

### setType

设置提示Poi类型，多个类型用“|”分隔，POI相关类型请在网站“相关下载”处下载，目前只支持Poi类型编码如“050000” 默认值：所有类别

#### Parameters

-   `type` **String** 提示Poi类型

### setCity

设置城市

#### Parameters

-   `city` **String** 城市

### setCityLimit

设置是否强制限制城市

#### Parameters

-   `citylimit` **boolean** 是否强制限制城市

### search

根据输入关键字提示匹配信息，支持中文、拼音

#### Parameters

-   `keyword` **String** 关键字
-   `callback` **AutoCompleteSearchCallback** 搜索结果回调

## AutoCompleteSearchCallback

搜索结果回调

Type: function

### Parameters

-   `status` **string** 返回信息状态 可取值：'complete': result 为 AutocompleteResult; 'error': result为错误信息；'no_data': result 为 0
-   `result` **searchResult** 返回结果详细信息
    -   `result.info` **string** 查询状态说明
    -   `result.count` **number** 输入提示条数
    -   `result.tips` **Array&lt;Tip>** 输入提示列表
        -   `result.tips.name` **string** 名称
        -   `result.tips.district` **string** 所属区域
        -   `result.tips.adcode` **string** 区域编码

## PlaceSearch

地点搜索服务插件，提供某一特定地区的位置查询服务。

### Examples

```javascript
mapObj.plugin(['AMap.PlaceSearch'], function() {
    var PlaceSearchOptions = { //设置PlaceSearch属性
        city: "北京", //城市
        type: "", //数据类别
        pageSize: 10, //每页结果数,默认10
        pageIndex: 1, //请求页码，默认1
        extensions: "base" //返回信息详略，默认为base（基本信息）
    };
    var MSearch = new AMap.PlaceSearch(PlaceSearchOptions); //构造PlaceSearch类
    AMap.event.addListener(MSearch, "complete", keywordSearch_CallBack); //返回结果
    MSearch.search('方恒国际中心'); //关键字查询
});
```

### search

根据输入关键字提示匹配信息，支持中文、拼音

#### Parameters

-   `keyword` **string** 关键字
-   `callback` **searchCallback** 搜索结果回调

### searchInBounds

根据范围和关键词进行范围查询

#### Parameters

-   `keyword` **string** 关键词
-   `bounds` **AMap.Bounds** 范围
-   `callback` **searchCallback** 搜索结果回调

### searchNearBy

根据中心点经纬度、半径以及关键字进行周边查询 radius取值范围：0-50000

#### Parameters

-   `keyword` **string** 关键字
-   `center` **AMap.LngLat** 中心点经纬度
-   `radius` **number** 半径

### getDetails

根据PGUID 查询POI 详细信息

#### Parameters

-   `PGUID` **string** PGUID

### setType

设置查询类别，多个类别用“|”分割

#### Parameters

-   `type` **string** 类别

### setPageIndex

设置显示查询结果页码

#### Parameters

-   `pageIndex` **number** 结果页码

### setPageSize

设置每页显示查询结果数量

#### Parameters

-   `pageSize` **number** 页数

### setCity

设置查询城市, 支持cityname（中文或中文全拼）、citycode、adcode

#### Parameters

-   `city` **string** 城市标识

### setCityLimit

设置是否强制限制城市

#### Parameters

-   `citylimit` **boolean** 是否开启

### poiOnAMAP

唤起高德地图客户端marker页
Object 参数：{
    id: "B000A7BD6C", POIID
    name:String, 必要参数
    location:LngLat|position属性  必须参数
}
例如：{
   id: "B000A7BD6C",
   location: LngLat,
   name: "清华大学",
   address: "地址"
}

#### Parameters

-   `p`  
-   `opts` **object** 调起参数

### detailOnAMAP

唤起高德地图客户端POI详情页
Object 参数：{
    id: "B000A7BD6C", POIID
    name:String, 必要参数
    location:LngLat|position属性  必须参数
}

#### Parameters

-   `p`  
-   `opts` **object** 调起

## searchCallback

搜索结果回调

Type: function

### Parameters

-   `status` **string** 返回信息状态 可取值：'complete': result 为 AutocompleteResult; 'error': result为错误信息；'no_data': result 为 0
-   `result` **SearchResult** 返回结果详细信息
    -   `result.info` **string** 成功状态说明
    -   `result.keywordList` **Array&lt;keyword>** 发生事件且查无此关键字时，返回建议关键字列表，可根据建议关键字查询
    -   `result.cityList` **Array&lt;cityInfo>** 发生事件且查无此关键字且 city 为“全国”时，返回城市建议列表，该列表中每个城市包含一个或多个相关Poi点信息
        -   `result.cityList.name` **string** 建议城市名称
        -   `result.cityList.citycode` **string** 城市编码
        -   `result.cityList.adcode` **string** 行政区编码
        -   `result.cityList.count` **string** 该城市的建议结果数目
    -   `result.poiList` **object** 发生事件时返回兴趣点列表
        -   `result.poiList.pageIndex` **number** 页码
        -   `result.poiList.pageSize` **number** 单页结果数
        -   `result.poiList.count` **number** 查询结果总数
        -   `result.poiList.pois` **Array&lt;POI>** Poi列表
            -   `result.poiList.pois.id` **string** 兴趣点id
            -   `result.poiList.pois.name` **string** 名称
            -   `result.poiList.pois.type` **string** 兴趣点类型
            -   `result.poiList.pois.location` **LngLat** 兴趣点经纬度
            -   `result.poiList.pois.address` **string** 地址
            -   `result.poiList.pois.distance` **number** 离中心点距离，仅周边查询返回
            -   `result.poiList.pois.tel` **string** 电话
            -   `result.poiList.pois.website` **string** 网址
            -   `result.poiList.pois.pcode` **string** poi所在省份编码
            -   `result.poiList.pois.citycode` **string** poi所在城市编码
            -   `result.poiList.pois.adcode` **string** poi所在区域编码
            -   `result.poiList.pois.postcode` **string** 邮编
            -   `result.poiList.pois.pname` **string** poi所在省份
            -   `result.poiList.pois.cityname` **string** poi所在城市名称
            -   `result.poiList.pois.adname` **string** poi所在行政区名称
            -   `result.poiList.pois.email` **string** 电子邮箱
            -   `result.poiList.pois.entr_location` **LngLat** 入口经纬度，POI点有出入口信息时返回，否则返回空字符串
            -   `result.poiList.pois.exit_location` **LngLat** 出口经纬度，POI点有出入口信息时返回，否则返回空字符串

## CloudDataSearch

云数据检索服务类

### Parameters

-   `tableid` **string** 
-   `opts` **CloudDataSearchOptions** 
    -   `opts.map` **Map** AMap.Map对象, 展现结果的地图实例。当指定此参数后，搜索结果的标注、线路等均会自动添加到此地图上。可选值
    -   `opts.keywords` **string** 云检索关键字，仅支持对建立了文本索引的字段进行模糊检索（请在[云数据管理平台][100]中管理文本索引）
    -   `opts.filter` **string** 云检索的筛选条件,仅支持对建立了排序筛选索引的字段进行筛选（请在云数据管理平台中管理排序筛选索引）；支持多个筛选条件，支持对文本字段的精确匹配和对数值字段的区间筛选。筛选条件之间使用“+”代表“与”关系,如：filter:"\_name:酒店+star:[3,5]"(等同于SOL语句的：WHERE_name="酒店" AND star BETWEEN 3 AND 5)
    -   `opts.orderBy` **string** 返回数据的排序规则。1.支持系统预设排序规则：\_distance：坐标与中心点距离升序排序（仅对周边检索有效；）\_weight：权重降序排序。默认值：1)当设置了keywords时，默认按"\_weight"权重排序；2)当未设置keywords时，默认按"\_distance"距离排序。2.支持对建立了排序筛选索引的整数或小数字段进行排序（请在云数据管理平台中管理排序筛选索引）。升降序分别为"ASC"、"DESC",若仅填字段不填升降序则默认按升序排列，如：orderBy:"age:ASC"
    -   `opts.pageSize` **number** 单页显示结果数，取值范围[0-100],超过取值范围取默认值，默认：20
    -   `opts.pageIndex` **number** 当前页码，取值>=1,默认1
    -   `opts.panel` **(string \| HTMLElement)** 结果列表的HTML容器id或容器元素，提供此参数后，结果列表将在此容器中进行展示。可选值
    -   `opts.autoFitView` **boolean** 用于控制在搜索结束后，是否自动调整地图视野使绘制的Marker点都处于视口的可见范围

### Examples

```javascript
AMap.plugin('AMap.CloudDataSearch'， function(){
    var map = new AMap.Map("map", {
       resizeEnable: true,
       zoom: 12 //地图显示的缩放级别
    });
    var search, center = new AMap.LngLat(116.39946, 39.910829);
    var searchOptions = {
       map: map,
       panel: 'panel',
       keywords: '',
       pageSize: 5,
       orderBy: '_id:ASC'
    };
    search = new AMap.CloudDataSearch('532b9b3ee4b08ebff7d535b4', searchOptions);
    search.searchNearBy(center, 1000);
});
```

### setOptions

设置云数据检索属性

#### Parameters

-   `opts` **CloudDataSearchOptions** 

### clear

清除搜索结果

### searchNearBy

周边检索，根据指定的中心点和半径检索位置数据。

#### Parameters

-   `center` **LngLat** 搜索中心
-   `radius` **number** 取值范围[0-50000]，超过取值范围按3000，单位：米
-   `callback` **CloudDataSearchCallback** 搜索回调

### searchById

根据数据id检索位置数据，id检索时不需要设置CloudDataSearchOptions

#### Parameters

-   `id` **string** 
-   `callback` **CloudDataSearchCallback** 搜索回调

### searchByDistrict

根据行政区划（包括全国/省/市/区县）名称，检索行政区划内位置数据.

#### Parameters

-   `district` **string** district为“全国”，则对全表搜索当district非法或不正确时，按照district为“全国”返回
-   `callback` **CloudDataSearchCallback** 搜索回调

### searchInPolygon

多边形检索，根据给定的多边形节点坐标数组，检索位置数据。如果数组只有两个坐标元素，则认为多边形为矩形，这两个点为矩形的左下、右上点。多边形坐标数组的起、终点必须保证多边形闭合（起、终点坐标相同）

#### Parameters

-   `path` **Array&lt;LngLat>** 检索范围路径
-   `callback` **CloudDataSearchCallback** 搜索回调

## CloudDataSearchCallback

搜索结果回调

Type: function

### Parameters

-   `status` **string** 返回信息状态 可取值：'complete': result 为 AutocompleteResult; 'error': result为错误信息；'no_data': result 为 0
-   `result` **object** 返回结果详细信息
    -   `result.info` **string** 成功状态文字描述
    -   `result.count` **number** 查询结果总数
    -   `result.datas` **Array&lt;CloudData>** 云数据数组，当根据数据id检索时，数据仅包含一个CloudData
    -   `result._id` **string** 数据id，id为数据唯一标识
    -   `result._name` **string** 名称
    -   `result._location` **LngLat** 坐标
    -   `result._address` **string** 地址
    -   `result._updatetime` **string** 数据更新时间
    -   `result._distance` **number** 距离中心点距离(仅周边查询时返回)
    -   `result.custom_field1` **any** 用户自定义字段1
    -   `result._image` **Array&lt;Image>** 图片信息
        -   `result._image._id` **string** 图片的id标识
        -   `result._image._preurl` **string** 经过压缩处理的图片地址,尺寸为400\*400，若期望获取体积较小的图片文件，建议使用此地址
        -   `result._image._url` **string** 最大限制获取1024\*1024，若您的原始图片小于该尺寸，将返回原图。
