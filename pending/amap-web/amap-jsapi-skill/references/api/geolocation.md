## 定位

用于进行城市定位或者精确定位的插件类型


## Geolocation

**Extends AMap.Control**

AMap.Geolocation 定位服务插件。融合了浏览器定位、高精度IP定位、安卓定位sdk辅助定位等多种手段，提供了获取当前准确位置、获取当前城市信息、持续定位(浏览器定位)等功能。用户可以通过两种当时获得定位的成败和结果，一种是在 getCurrentPosition的时候传入回调函数来处理定位结果，一种是通过事件监听来取得定位结果。

### Parameters

-   `options` **GeolocationOptions** 初始化参数
    -   `options.position` **string** 悬停位置，默认为"RB"，即右下角
    -   `options.offset` **\[number, number]** 缩略图距离悬停位置的像素距离，如[2,2]
    -   `options.borderColor` **string** 按钮边框颜色值，同CSS，如'silver'
    -   `options.borderRadius` **string** 按钮圆角边框值，同CSS，如'5px'
    -   `options.buttonSize` **string** 箭头按钮的像素尺寸，同CSS，如'12px'
    -   `options.convert` **boolean** 是否将定位结果转换为高德坐标
    -   `options.enableHighAccuracy` **boolean** 进行浏览器原生定位的时候是否尝试获取较高精度，可能影响定位效率，默认为false
    -   `options.timeout` **number** 定位的超时时间，毫秒
    -   `options.maximumAge` **number** 浏览器原生定位的缓存时间，毫秒
    -   `options.showButton` **boolean** 是否显示定位按钮，默认为true
    -   `options.showCircle` **boolean** 是否显示定位精度圆，默认为true
    -   `options.showMarker` **boolean** 是否显示定位点，默认为true
    -   `options.markerOptions` **MarkerOptions** 定位点的样式
    -   `options.circleOptions` **CircleOptions** 定位圆的样式
    -   `options.panToLocation` **boolean** 定位成功后是否自动移动到响应位置
    -   `options.zoomToAccuracy` **boolean** 定位成功后是否自动调整级别
    -   `options.GeoLocationFirst` **boolean** 优先使用H5定位，默认移动端为true，PC端为false
    -   `options.noIpLocate` **number** 是否禁用IP精确定位，默认为0，0:都用  1:手机上不用  2:PC上不用   3:都不用
    -   `options.noGeoLocation` **number** 是否禁用浏览器原生定位，默认为0，0:都用  1:手机上不用  2:PC上不用   3:都不用
    -   `options.useNative` **boolean** 是否与高德定位SDK能力结合，需要同时使用安卓版高德定位sdk，否则无效
    -   `options.getCityWhenFail` **boolean** 定位失败之后是否返回基本城市定位信息
    -   `options.needAddress` **boolean** 是否需要将定位结果进行逆地理编码操作
    -   `options.extensions` **string** 是否需要详细的逆地理编码信息，默认为'base'只返回基本信息，可选'all'

### getCurrentPosition

获取 用户的精确位置，有失败几率

#### Parameters

-   `callback` **GeolocationCallBack** 定位回调函数，成功或者失败均会回调

### getCityInfo

根据用户 IP 获取 用户所在城市信息

#### Parameters

-   `callback` **GeolocationCallBack** 

## GeolocationCallBack

Geolocation插件的定位回调函数

Type: Function

### Parameters

-   `status` **string** 'complete' 或者 'error'
-   `result` **GeolocationResult** 定位结果

## GeolocationResult

浏览器定位的定位结果，定位的过程和失败信息可以从 message 字段中获取

Type: Object

### Properties

-   `position` **LngLat** 定位到的经纬度位置
-   `accuracy` **number** 定位精度，米
-   `location_type` **number** 定位的类型，ip/h5/sdk/ipcity
-   `message` **number** 定位过程的信息，用于排查定位失败原因
-   `isConverted` **number** 是否已经转换为高德坐标
-   `info` **number** 'SUCCESS' 或者 'PERMISSION_DENIED' 或者 'TIME_OUT' 或者 'POSITION_UNAVAILABLE'
-   `addressComponent` **number** needAddress的时候返回，结构化地址信息
-   `formattedAddress` **number** needAddress的时候返回，规范地址
-   `pois` **number** needAddress的时候返回，定位点附近的POI信息
-   `roads` **number** needAddress的时候返回，定位点附近的道路信息
-   `crosses` **number** needAddress的时候返回，定位点附近的交叉口信息

## CitySearch

**Extends AMap.Event**

AMap.CitySearch 根据IP返回对应城市信息，提供根据输入IP或自动获取IP获取对应城市信息功能。
用户可以通过自定义回调函数取回并显示[查询结果][139]。
若服务请求失败，系统将返回[错误信息][140]。

### getLocalCity

自动获取用户IP，回调返回当前用户所在城市
当status为complete时，result为CitySearchResult；
当status为error时，result为错误信息info；
当status为no_data时，代表检索返回0结果

#### Parameters

-   `CitySearchCallback` **function** 查询的回调函数
-   `cbk` **function (status: String, result: info)** 回调函数

### getCityByIp

根据输入IP地址返回对应城市信息，status同上

#### Parameters

-   `ip` **String** IP地址
-   `CitySearchCallback` **function (status: String, result: info)** 回调函数
