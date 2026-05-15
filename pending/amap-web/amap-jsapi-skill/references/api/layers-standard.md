## 行业标准图层

符合 OGC 标准或者行业通行规范的的图层类型


## WMS

**Extends TileLayer**

用于加载OGC标准的WMS地图服务的一种图层类，仅支持EPSG3857坐标系统的WMS图层。 </br>
[查看 WMS的OGC标准][53]。

### Parameters

-   `opts` **WMSLayerOptions** 默认图层参数
    -   `opts.url` **String** wmts服务的url地址，如：'[https://services.arcgisonline.com/arcgis/rest/services/'+][54]
        'Demographics/USA_Population_Density/MapServer/WMTS/'
    -   `opts.blend` **Boolean** 地图级别切换时，不同级别的图片是否进行混合，如图层的图像内容为部分透明请设置为false
    -   `opts.param` **Object** OGC标准的WMS地图服务的GetMap接口的参数，包括VERSION、LAYERS、STYLES、FORMAT、TRANSPARENT等， </br>
        CRS、BBOX、REQUEST、WIDTH、HEIGHT等参数请勿添加，例如： </br>
        { </br>
            LAYERS: 'topp:states', </br>
            VERSION:'1.3.0', </br>
            FORMAT:'image/png' </br>
        }
    -   `opts.zooms` **\[Number, Number]** 支持的缩放级别范围，默认范围 [2-30] (optional, default `[2,30]`)
    -   `opts.opacity` **Number** 透明度，默认 1 (optional, default `1`)
    -   `opts.visible` **Boolean** 是否显示，默认 true (optional, default `true`)
    -   `opts.zIndex` **Number** 图层叠加的顺序值，1 表示最底层。默认 zIndex：4 (optional, default `4`)

### setParams

设置OGC标准的WMS getMap接口的参数，包括VERSION、LAYERS、STYLES、FORMAT、TRANSPARENT等

#### Parameters

-   `params` **Object** 参数集合，{VERSION: '1.0', ...}

### getParams

获取 OGC 标准的 WMS getMap 接口的参数

### setUrl

设置 WMS 服务地址

#### Parameters

-   `url` **String** 服务地址

### setUrl

设置 WMS 服务地址

#### Parameters

-   `url` **String** 服务地址

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

## WMTS

**Extends TileLayer**

用于加载 OGC 标准的 WMTS 地图服务的一种图层类，仅支持 EPSG3857 坐标系统的 WMTS 图层 </br>
[查看 WMTS 标准][55] </br>
[相关示例][56]

### Parameters

-   `opts` **WMTSLayerOptions** 默认图层参数
    -   `opts.url` **String** wms服务的url地址，如'[https://ahocevar.com/geoserver/wms][57]'
    -   `opts.blend` **Boolean** 地图级别切换时，不同级别的图片是否进行混合，如图层的图像内容为部分透明请设置为false
    -   `opts.param` **Object** OGC标准的WMTS地图服务的GetTile接口的参数，包括Version、Layer、
        Style、Format、Service等，TileMatrixSet、TileRow、TileCol、Request等参数请勿添加，例如： </br>
        { </br>
            Layer: '0', </br>
            Version:'1.0.0', </br>
            Format: 'image/png' </br>
        }
    -   `opts.zooms` **\[Number, Number]** 支持的缩放级别范围，默认范围 [2-30] (optional, default `[2,30]`)
    -   `opts.opacity` **Number** 透明度，默认 1 (optional, default `1`)
    -   `opts.visible` **Boolean** 是否显示，默认 true (optional, default `true`)
    -   `opts.zIndex` **Number** 图层叠加的顺序值，1 表示最底层。默认 zIndex：4 (optional, default `4`)

### setParams

设置 OGC 标准的 WMTS getTile接口的参数，包括Version、Layer、Style、Format、Service等

#### Parameters

-   `params` **Object** 参数集合，{VERSION: '1.0', ...}

### getParams

获取 OGC 标准的 WMTS getMap 接口的参数

### getUrl

获取 WMTS 服务地址

Returns **String** 地址

### setUrl

设置 WMTS 服务地址

#### Parameters

-   `url` **String** 服务地址

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

## MapboxVectorTileLayer

**Extends Layer**

为了满足基于矢量瓦片块的数据可视化、矢量瓦片边界展示等开发需求，通过 AMap.MapboxVectorTileLayer 插件提供了简易矢量瓦片图层</br>
此图层可以使用标准的 MVT 瓦片服务作为数据源。</br>
可以配合[GeoHub-数据中心][58]发布的矢量瓦片服务。
注意：使用高德数据平台发布服务，由于服务 URL 地址是明文，建议自行做服务代理转发，防止服务 ID 和 Key 明文传输导致数据泄露。</br>
[相关示例][59]

### Parameters

-   `opts` **MapboxVTLayerOptions** 图层初始化参数
    -   `opts.zIndex` **Number** 图层的层级 (optional, default `80`)
    -   `opts.opacity` **Number** 图层透明度 (optional, default `1`)
    -   `opts.url` **String?** MVT 数据的链接地址
    -   `opts.visible` **Boolean** 图层是否可见 (optional, default `true`)
    -   `opts.zooms` **\[number, number]** 图层缩放等级范围 (optional, default `[2,22]`)
    -   `opts.dataZooms` **\[number, number]** 瓦片数据等级范围，超过范围会使用最大/最小等级的数据 (optional, default `[2,18]`)
    -   `opts.styles` **MapboxVTLayerStyle** 
        -   `opts.styles.polygon` **PolygonStyle?** 面类型的样式
            -   `opts.styles.polygon.sourceLayer` **String** 使用数据中的哪个图层，默认使用 default 图层 (optional, default `'default'`)
            -   `opts.styles.polygon.color` **(String \| Function)?** 面填充颜色
            -   `opts.styles.polygon.borderWidth` **(Number \| Function)?** 描边宽度
            -   `opts.styles.polygon.dash` **(Array&lt;Number> | Function)?** 描边线的虚线配置，例如：[10,5,8,5]
            -   `opts.styles.polygon.borderColor` **(String \| Function)?** 描边颜色
            -   `opts.styles.polygon.injection` **Array&lt;Any>?** 其他属性值中对于函数形式的值，假如需要获取外部变量，要使用数组的形式传入，便于在函数内部访问外部变量。请看下面的示例。
            -   `opts.styles.polygon.visible` **(Boolean \| Function)?** 是否显示
        -   `opts.styles.line` **LineStyle?** 线类型数据的样式
            -   `opts.styles.line.sourceLayer` **String** 使用数据中的哪个图层，默认使用 default 图层 (optional, default `'default'`)
            -   `opts.styles.line.color` **(String \| Function)?** 线填充颜色
            -   `opts.styles.line.lineWidth` **(Number \| Function)?** 宽度
            -   `opts.styles.line.dash` **(String \| Function)?** 虚线配置，例如：[10,5,8,5]
            -   `opts.styles.line.injection` **Array&lt;Any>?** 其他属性值中对于函数形式的值，假如需要获取外部变量，要使用数组的形式传入，便于在函数内部访问外部变量。请看下面的示例。
            -   `opts.styles.line.visible` **(Boolean \| Function)?** 是否显示
        -   `opts.styles.point` **PointStyle?** 点类型数据的样式
            -   `opts.styles.point.sourceLayer` **String** 使用数据中的哪个图层，默认使用 default 图层 (optional, default `'default'`)
            -   `opts.styles.point.radius` **(String \| Function)?** 圆点的半径，单位像素
            -   `opts.styles.point.color` **(Number \| Function)?** 圆的填充颜色
            -   `opts.styles.point.borderWidth` **(String \| Function)?** 描边的宽度
            -   `opts.styles.point.borderColor` **(String \| Function)?** 描边的颜色
            -   `opts.styles.point.injection` **Array&lt;Any>?** 其他属性值中对于函数形式的值，假如需要获取外部变量，要使用数组的形式传入，便于在函数内部访问外部变量。请看下面的示例。
            -   `opts.styles.point.visible` **(Boolean \| Function)?** 是否显示
        -   `opts.styles.polyhedron` **PolyhedronStyle?** 多面体类型的样式
            -   `opts.styles.polyhedron.sourceLayer` **String** 使用数据中的哪个图层，默认使用 default 图层 (optional, default `'default'`)
            -   `opts.styles.polyhedron.topColor` **(String \| Function)?** 顶面颜色
            -   `opts.styles.polyhedron.sideColor` **(String \| Function)?** 侧面颜色
            -   `opts.styles.polyhedron.texture` **(String \| Function)?** 侧面纹理，优先级高于侧面颜色
            -   `opts.styles.polyhedron.injection` **Array&lt;Any>?** 其他属性值中对于函数形式的值，假如需要获取外部变量，要使用数组的形式传入，便于在函数内部访问外部变量。请看下面的示例。
            -   `opts.styles.polyhedron.visible` **(Boolean \| Function)?** 是否显示

### Examples

```javascript
var globalVar = ['这是', '一个', '外部', '变量'];
var mvtl = new AMap.MapboxVectorTileLayer({
     zIndex: 150,
     opacity: 1,
     // URL可以使用数据服务平台的服务，也可以使用自己发布的 MVT 数据服务
     url: 'https://restapi.amap.com/rest/lbs/geohub/tiles/mvt?z=[z]&x=[x]&y=[y]&size=512&key=您申请的key值&id=数据服务ID',
     dataZooms: [2, 18],
     zooms: [2, 20],
     tileSize: 256,
     styles: {
         point: {
             sourceLayer: 'default',
             visible: function (f, inject) {
                 // 这里的 inject 参数就是一个数组，他的值就是 injection 字段的数组值：[visis]。
                 return inject[0].indexOf('这是') > -1;
             },
             injection: [globalVar],
             radius: function (props) {
                 return Math.random() * 20 + 5;
             },
             color: 'red',
             borderWidth: 20 || function (props) {
                 return Math.random() * 5 + 2;
             },
             borderColor: 'rgba(255,255,255,1)',
         },
         polygon: {
             sourceLayer: 'default',
             color: function (props) {
                 return 'rgba(0,0,0,1)';
             },
             dash: [10, 0, 10, 0],
             borderColor: 'rgba(30,112,255,1)',
             borderWidth: 5,
         },
         line: {
             sourceLayer: 'default',
             color: 'rgba(20,140,40,1)',
             lineWidth: 5,
             dash: [10, 0, 10, 0],
         },
         polyhedron: {
             sourceLayer: 'default',
             topColor: 'rgba(230,230,230,0.9)',
             sideColor: 'rgba(240,240,240,0.9)',
         },
     }
 });
```

### setStyles

设置样式信息

#### Parameters

-   `styles` **MapboxVTLayerStyle** 样式信息

### filterByRect

获取矩形范围的要素

#### Parameters

-   `rect` **Polygon** 多边型，例如：\[[lng,lat],[lng,lat],[lng,lat],[lng,lat],[lng,lat]]
-   `type` **String** 想要获取的要素类型，默认选择所有：all。可选值：all、point、polygon、line (optional, default `"all"`)

Returns **Array&lt;Feature>** 

### getStyles

获取样式信息

Returns **MapboxVTLayerStyle** 样式

### on

图层级别监听鼠标事件
获取当前图层中鼠标位置的要素

#### Parameters

-   `type` **String** 监听事件类型，目前支持 click、mousemove
-   `fn` **Function** 监听的回调函数，参数中的 features 是获取的鼠标位置的要素
-   `option` **Object** 拾取参数，featType：代表需要拾取的要素类型，参考 filterByRect() 函数中的 type；buffer：5, 代表以鼠标为中心点，范围为 5 的方形区域为鼠标拾取范围。值越大，拾取的范围越大，建议使用默认值。

### hide

设置图层隐藏

### hide

设置图层隐藏

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
