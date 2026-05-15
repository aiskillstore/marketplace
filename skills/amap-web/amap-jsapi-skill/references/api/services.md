## 服务类

用于调用 Web 服务 API，直接透传查询条件和返回结果


## WebService

用于调用 Web 服务 API，直接透传查询条件和返回结果，提供GET和POST两种请求方式，具体请求接口和返回结果，请参考 [https://lbs.amap.com/api/webservice/summary/][96]

### get

以 GET 请求方式请求指定的 Web 服务 API 接口

#### Parameters

-   `path` **string** Web服务API的接口路径
-   `params` **object** Web服务 API 的查询参数
-   `callback` **WebServiceCallback** 查询回调函数
-   `opts` **HttpOptions** HTTP 请求参数配置 (optional, default `{}`)

#### Examples

```javascript
AMap.WebService.get('https://restapi.amap.com/v3/place/text',
    {
        keywords : '首开广场',
        types : '写字楼',
        city : '010'
    },function (error, result) {
        console.log(error, result);
    }
);
```

### post

以 POST 请求方式请求指定的 Web 服务 API 接口, 目前只有轨迹纠偏接口需要使用 POST 方式

#### Parameters

-   `path` **string** Web服务API的接口路径
-   `params` **any** Web服务 API 的查询参数
-   `callback` **WebServiceCallback** 查询回调函数

#### Examples

```javascript
AMap.WebService.post('https://restapi.amap.com/v4/grasproad/driving',
  [
      {"x":116.478928,"y":39.997761,"sp":19,"ag":0, "tm":1478031031},
      {"x":116.478907,"y":39.998422,"sp":10,"ag":0, "tm":2},
      {"x":116.479384,"y":39.998546,"sp":10,"ag":110,"tm":3},
      {"x":116.481053,"y":39.998204,"sp":10,"ag":120,"tm":4},
      {"x":116.481793,"y":39.997868,"sp":10,"ag":120,"tm":5}
  ],function (error, result) {
      console.log(error, result);
  }
);
```

## WebServiceCallback

WebService 的回调函数类型

Type: Function

### Parameters

-   `status` **string** 服务查询的状态结果，'complete' 或 'error'
-   `data` **any** Web服务API返回的数据
