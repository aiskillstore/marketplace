## 点标记

用于在地图上添加点状地图要素的类型


## Marker

点标记

### Parameters

-   `opts` **MarkerOptions** 点标记参数
    -   `opts.map` **Map** 要显示该marker的地图对象
    -   `opts.position` **(Vector2 | LngLat)** 点标记在地图上显示的位置
    -   `opts.icon` **(Icon \| string)** 在点标记中显示的图标。可以传一个图标地址，也可以传Icon对象。有合法的content内容设置时，此属性无效。
    -   `opts.content` **(string \| HTMLElement)** 点标记显示内容。可以是HTML要素字符串或者HTML DOM对象。content有效时，icon属性将被覆盖。
    -   `opts.title` **string** 鼠标滑过点标记时的文字提示。不设置则鼠标滑过点标无文字提示。
    -   `opts.visible` **boolean** 点标记是否可见，默认值：true
    -   `opts.zIndex` **number** 点标记的叠加顺序。地图上存在多个点标记叠加时，通过该属性使级别较高的点标记在上层显示，默认zIndex：12
    -   `opts.offset` **(Vector2 | Pixel)** 点标记显示位置偏移量，默认值为[0,0]。Marker指定position后，默认以marker左上角位置为基准点（若设置了anchor，则以anchor设置位置为基准点），对准所给定的position位置，若需使marker指定位置对准在position处，需根据marker的尺寸设置一定的偏移量。
    -   `opts.anchor` **(string | Vector2)** 设置点标记锚点，可选值：'top-left','top-center','top-right', 'middle-left', 'center', 'middle-right', 'bottom-left', 'bottom-center', 'bottom-right' [相关示例][72]
    -   `opts.angle` **number** 点标记的旋转角度，，广泛用于改变车辆行驶方向。默认值：0
    -   `opts.clickable` **boolean** 点标记是否可点击，默认值: true
    -   `opts.draggable` **boolean** 设置点标记是否可拖拽移动，默认值：false
    -   `opts.bubble` **boolean** 事件是否冒泡，默认为 false
    -   `opts.zooms` **Vector2** 点标记显示的层级范围，超过范围不显示。默认值：zooms: [2, 20]
    -   `opts.cursor` **string** 指定鼠标悬停时的鼠，默认值：'pointer'
    -   `opts.topWhenClick` **boolean** 鼠标点击时marker是否置顶，默认false ，不置顶
    -   `opts.label` **object** 添加文本标注
        -   `opts.label.content` **string** 文本标注的内容
        -   `opts.label.offset` **(Pixel | Vector2 | Array&lt;number>)** 为偏移量。如设置了 direction，以 direction 方位为基准点进行偏移。
        -   `opts.label.direction` **string** 文本标注方位 可选值：'top'|'right'|'bottom'|'left'|'center'，默认值: 'right'。
    -   `opts.extData` **any** 用户自定义属 ，支持JavaScript API任意数据类型，如 Marker的id等。可将自定义数据保存在该属性上，方便后续操作使用。

### Examples

```javascript
var marker = new AMap.Marker({
    position: new AMap.LngLat(116.397428, 39.90923),
    icon: 'https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png',
    anchor: 'bottom-center',
});
map.add(marker);
```

### getTitle

获取点标记的文字提示

Returns **(string \| undefined)** 

### setTitle

设置鼠标滑过点标记时的文字提示

#### Parameters

-   `title` **string** 点标记的文字提示

### getIcon

当点标记未自定义图标时，获取Icon内容

Returns **(Icon \| string \| undefined)** 

### setIcon

设置点标记的显示图标，设置了有效 content 则 icon 不生效

#### Parameters

-   `icon` **(Icon \| string)** 点标记中显示的图标

### getLabel

获取点标记文本标签内容

Returns **LabelOptions** 文本标签设置项

### setLabel

设置点标记文本标签内容

#### Parameters

-   `opts` **LabelOptions** 

### getClickable

获取点标记是否支持鼠标单击事件

Returns **boolean** 

### setClickable

设置点标记是否支持鼠标单击事件

#### Parameters

-   `clickable` **boolean** 默认值: true

### getDraggable

获取点标记对象是否可拖拽移动

Returns **boolean** 

### setDraggable

设置点标记对象是否可拖拽移动

#### Parameters

-   `draggable` **boolean** 

### getTop

获取该点标记是否置顶

Returns **boolean** 

### setTop

地图上有多个marker时，设置是否置顶该点标记

#### Parameters

-   `isTop` **boolean** 

### getCursor

获取鼠标悬停时的光标设置

Returns **string** 

### setCursor

设置鼠标悬停时的光标

#### Parameters

-   `cursor` **string** 

### getExtData

获取用户自定义数据

Returns **(any | undefined)** 

### setExtData

设置用户自定义数据

#### Parameters

-   `extData`  用户自定义数据

### remove

移除点标记 [相关示例][73]

### moveTo

以给定时长/速度移动点标记到指定位置, 需加载 AMap.MoveAnimation 插件才可使用

#### Parameters

-   `targetPosition` **(LngLat | Vector2)** 指定位置
-   `opts` **MoveToOptions** moveTo 动画参数
    -   `opts.duration` **number** 每段动画持续时长, 单位：ms
    -   `opts.speed` **number** 动画速度，已废弃
    -   `opts.easing` **EasingCallback** easing 时间函数
    -   `opts.autoRotation` **boolean** 点标记方向是否沿路径旋转

#### Examples

```javascript
AMap.plugin('AMap.MoveAnimation', function(){
    // 加载完 AMap.MoveAnimation 插件以后，创建一个 Marker 实例
    const animationMarker = new AMap.Marker({
        position: new AMap.LngLat(116.397389,39.909466),
        icon: "https://a.amap.com/jsapi_demos/static/demo-center-v2/car.png",
        offset: new AMap.Pixel(-13, -26),
    });
    // 调用 moveTo 方法
    animationMarker.moveTo([116.397389, 39.909466], {
        duration: 1000,
        delay: 500,
    });
});
```

### moveAlong

以指定的时长，点标记沿指定的路径移动，加载 AMap.MoveAnimation 后可以使用
JSAPI 2.0 可支持分段设置速度和时长 [相关示例][75]

#### Parameters

-   `path` **(Array&lt;LngLat> | Array&lt;Vector2> | Array&lt;MoveAlongObj>)** 路径数组
-   `opts` **MoveAlongOptions** moveAlong 动画参数 可选
    -   `opts.duration` **(number \| AnimationCallback)** 每段动画持续时长, 单位：ms
    -   `opts.speed` **(number \| AnimationCallback)** 每段动画速度，已废弃
    -   `opts.easing` **EasingCallback** easing 时间函数
    -   `opts.circlable` **boolean** 动画是否循环
    -   `opts.delay` **(number \| AnimationCallback)** 延迟动画时长
    -   `opts.aniInterval` **number** 每段完整动画间隔时长
    -   `opts.autoRotation` **boolean** 覆盖物是否沿路径旋转

#### Examples

```javascript
const path = [
    new AMap.LngLat(116.397389, 39.909466),
    new AMap.LngLat(116.379707, 39.968168),
    new AMap.LngLat(116.434467, 39.95001),
    new AMap.LngLat(116.46365, 39.979481),
    new AMap.LngLat(116.397389, 39.909466),
];
// 分段设置时长
const customData = [
    { position: path[0], duration: 200 },
    { position: path[1], duration: 400 },
    { position: path[2], duration: 600 },
    { position: path[3], duration: 800 },
    { position: path[4], duration: 1000 },
];
AMap.plugin('AMap.MoveAnimation', function(){
    // 加载完 AMap.MoveAnimation 插件以后，创建一个 Marker 实例
    const animationMarker = new AMap.Marker({
        position: new AMap.LngLat(116.397389,39.909466),
        angle: 90,
    });
    // 调用 moveAlong 方法
    animationMarker.moveAlong(customData);
});
```

### startMove

开启点标记动画，加载 AMap.MoveAnimation 后创建的点标记可以使用

#### Examples

```javascript
animationMarker.startMove();
```

### stopMove

停止点标记动画，加载 AMap.MoveAnimation 后创建的点标记可以使用

#### Examples

```javascript
animationMarker.stopMove();
```

### pauseMove

暂停点标记动画，加载 AMap.MoveAnimation 后创建的点标记可以使用

#### Examples

```javascript
animationMarker.pauseMove();
```

### resumeMove

重新启动点标记动画，加载 AMap.MoveAnimation 后创建的点标记可以使用

#### Examples

```javascript
animationMarker.resumeMove();
```

### getMap

获取覆盖物的地图实例

Returns **(Map | null)** 

### setMap

将覆盖物设置到地图上

#### Parameters

-   `map` **(Map | null)** 

### addTo

将覆盖物加到地图上

#### Parameters

-   `map` **Map** 

### add

将覆盖物加到地图上

#### Parameters

-   `map` **Map** 

### show

显示覆盖物

### hide

隐藏覆盖物

### getPosition

获取覆盖物位置

Returns **any** 

### setPosition

设置覆盖物位置

#### Parameters

-   `position` **Vector2** 

### getAnchor

获取覆盖物锚点

Returns **(string | Vector2 | undefined)** 

### Marker

设置覆盖物锚点

#### Parameters

-   `anchor` **string** 

### getOffset

获取覆盖物偏移量

Returns **(Vector2 | Pixel \| undefined \| Array&lt;number>)** 

### setOffset

设置覆盖物偏移量

#### Parameters

-   `offset` **(Vector2 | Pixel)** 

### getAngle

获取覆盖物旋转角度

Returns **(number \| undefined)** 

### setAngle

设置覆盖物旋转角度

#### Parameters

-   `angle` **number** 

### getSize

如设置了尺寸，获取设置的尺寸

Returns **Vector2** 

### setSize

设置尺寸

#### Parameters

-   `size` **(Vector2 | Size)** 

### getzIndex

获取覆盖物的叠加顺序

Returns **(number \| undefined)** 

### setzIndex

设置覆盖物的叠加顺序

#### Parameters

-   `zIndex` **number** 

### getOptions

获取覆盖物的所有属性

Returns **OverlayOptions** 

### getContent

获取点标记显示的自定义内容

Returns **(string \| HTMLElement \| undefined)** 

### setContent

设置点标记显示的自定义内容，可以是HTML要素字符串或者HTML DOM对象

#### Parameters

-   `content` **(HTMLDOM | string)** 

### getBounds

获取点标记范围

Returns **Bounds** 

## Text

文本标记

### Parameters

-   `opts` **TextOptions** 文本参数
    -   `opts.map` **Map** 要显示该marker的地图对象
    -   `opts.position` **(Vector | LngLat)** 点标记在地图上显示的位置
    -   `opts.text` **LabelOptions** 标记显示的文本内容
    -   `opts.title` **string** 鼠标滑过点标记时的文字提示
    -   `opts.visible` **boolean** 点标记是否可见，默认为true
    -   `opts.zIndex` **number** 点标记的叠加顺序
    -   `opts.offset` **(Vector | Pixel)** 点标记显示位置偏移量，默认值[0, 0]。[图解说明][78]
    -   `opts.anchor` **(string | Vector)** 设置点标记锚点。默认值：'center'。可选值：'top-left'|'top-center'|'top-right'|'middle-left'|'center'|'middle-right'|'bottom-left'|'bottom-center'|'bottom-right'
    -   `opts.angle` **number** 点标记的旋转角度。默认值：0 。注：angle属性是使用CSS3来实现的，支持IE9及以上版本
    -   `opts.clickable` **boolean** 点标记是否可点击。默认值: true
    -   `opts.draggable` **boolean** 设置点标记是否可拖拽移动。默认值：false
    -   `opts.bubble` **boolean** 事件是否冒泡，默认值：false
    -   `opts.zooms` **Vector** 点标记显示的层级范围，超过范围不显示。默认值：zooms: [2, 20]。
    -   `opts.cursor` **string** 指定鼠标悬停时的鼠标样式。
    -   `opts.topWhenClick` **boolean** 鼠标点击时marker是否置顶，默认值: false
    -   `opts.extData` **any** 用户自定义属性 ，支持JavaScript API任意数据类型，如 Marker的id等。可将自定义数据保存在该属性上，方便后续操作使用。
    -   `opts.style` **object** 设置文本样式，Object同css样式表，如:{'background-color':'red'}

### Examples

```javascript
var text = new AMap.Text({
    position: new AMap.LngLat(116.397428, 39.90923),
    anchor: 'bottom-center',
    text: '文本标记',
    style: {'background-color':'red'},
});
map.add(text);
```

### getText

获取文本标记内容

Returns **(string \| undefined)** 

### text

设置文本标记内容

#### Parameters

-   `text` **string** 

### setStyle

修改文本标记样式。Object同css样式表，如:{'background-color':'red'}

#### Parameters

-   `style`  

### getTitle

获取文本标记的文字提示

Returns **(string \| undefined)** 

### setTitle

设置鼠标滑过文本标记时的文字提示

#### Parameters

-   `title` **string** 文本标记的文字提示

### getClickable

获取文本标记是否支持鼠标单击事件

Returns **boolean** 

### setClickable

设置文本标记是否支持鼠标单击事件

#### Parameters

-   `clickable` **boolean** 默认值: true

### getDraggable

获取文本标记对象是否可拖拽移动

Returns **boolean** 

### setDraggable

设置文本标记对象是否可拖拽移动

#### Parameters

-   `draggable` **boolean** 

### getTop

获取该文本标记是否置顶

Returns **boolean** 

### getMap

获取文本标记的地图实例

Returns **(Map | null)** 

### setMap

将文本标记设置到地图上

#### Parameters

-   `map` **(Map | null)** 

### addTo

将文本标记加到地图上，不推荐使用。推荐使用 map.add(text);

#### Parameters

-   `map` **Map** 

### add

将文本标记加到地图上

#### Parameters

-   `map` **Map** 

### show

显示文本标记

### hide

隐藏文本标记

### getPosition

获取文本标记位置

Returns **any** 

### setPosition

设置文本标记位置

#### Parameters

-   `position` **Vector** 

### getAnchor

获取文本标记锚点

Returns **(string | Vector | undefined)** 

### Text

设置文本标记锚点

#### Parameters

-   `anchor` **string** 

### getOffset

获取文本标记偏移量

Returns **(Vector | Pixel \| undefined \| Array&lt;number>)** 

### setOffset

设置文本标记偏移量，相对 anchor 后的偏移位置

#### Parameters

-   `offset` **(Array&lt;number> | Pixel)** 

### getAngle

获取文本标记旋转角度

Returns **(number \| undefined)** 

### setAngle

设置文本标记旋转角度

#### Parameters

-   `angle` **number** 

### getzIndex

获取文本标记的叠加顺序

Returns **(number \| undefined)** 

### setzIndex

设置文本标记的叠加顺序

#### Parameters

-   `zIndex` **number** 

### getOptions

获取文本标记的所有属性

Returns **OverlayOptions** 

### getBounds

获取文本标记范围

Returns **Bounds** 

### moveTo

以给定速度移动文本标记到指定位置, 需加载 AMap.MoveAnimation 插件才可使用

#### Parameters

-   `targetPosition` **(LngLat | Vector)** 指定位置
-   `opts` **MoveToOptions** moveTo 动画参数
    -   `opts.duration` **number** 每段动画持续时长, 单位：ms
    -   `opts.speed` **number** 动画速度，已废弃
    -   `opts.easing` **EasingCallback** easing 时间函数
    -   `opts.autoRotation` **boolean** 覆盖物是否沿路径旋转

#### Examples

```javascript
AMap.plugin('AMap.MoveAnimation', function(){
    // 加载完 AMap.MoveAnimation 插件以后，创建一个 Text 实例
    const animationText = new AMap.Text({
        text: '文本标记',
        position: new AMap.LngLat(116.397389,39.909466),
    });
    animationText.moveTo([116.397389, 39.909466], {
        duration: 1000,
        delay: 500,
    });
});
```

### moveAlong

以指定的时长，文本标记沿指定的路径移动，加载 AMap.MoveAnimation 后可以使用

#### Parameters

-   `path` **(Array&lt;LngLat> | Array&lt;Vector> | Array&lt;MoveAlongObj>)** 路径数组
-   `opts` **MoveAlongOptions** moveAlong 动画参数 可选
    -   `opts.duration` **(number \| AnimationCallback)** 每段动画持续时长, 单位：ms
    -   `opts.speed` **(number \| AnimationCallback)** 每段动画速度，已废弃
    -   `opts.easing` **EasingCallback** easing 时间函数
    -   `opts.circlable` **boolean** 动画是否循环
    -   `opts.delay` **(number \| AnimationCallback)** 延迟动画时长
    -   `opts.aniInterval` **number** 每段完整动画间隔时长
    -   `opts.autoRotation` **boolean** 覆盖物是否沿路径旋转

#### Examples

```javascript
const path = [
    new AMap.LngLat(116.397389, 39.909466),
    new AMap.LngLat(116.379707, 39.968168),
    new AMap.LngLat(116.434467, 39.95001),
    new AMap.LngLat(116.46365, 39.979481),
    new AMap.LngLat(116.397389, 39.909466),
];
const customData = [
    { position: path[0], duration: 200 },
    { position: path[1], duration: 400 },
    { position: path[2], duration: 600 },
    { position: path[3], duration: 800 },
    { position: path[4], duration: 1000 },
];
AMap.plugin('AMap.MoveAnimation', function(){
    // 加载完 AMap.MoveAnimation 插件以后，创建一个 Text 实例
    const animationText = new AMap.Text({
        text: '文本标记',
        position: new AMap.LngLat(116.397389,39.909466),
    });
    animationText.moveAlong(customData);
});
```

### startMove

开启文本标记动画，加载 AMap.MoveAnimation 后可以使用

#### Examples

```javascript
animationText.startMove();
```

### stopMove

停止文本标记动画，加载 AMap.MoveAnimation 后可以使用

#### Examples

```javascript
animationText.stopMove();
```

### pauseMove

暂停文本标记动画，加载 AMap.MoveAnimation 后可以使用

#### Examples

```javascript
animationText.pauseMove();
```

### resumeMove

重新启动文本标记动画，加载 AMap.MoveAnimation 后可以使用

#### Examples

```javascript
animationText.resumeMove();
```

### setTop

地图上有多个marker时，设置是否置顶该文本标记

#### Parameters

-   `isTop` **boolean** 

### getCursor

获取鼠标悬停时的光标设置

Returns **string** 

### setCursor

设置鼠标悬停时的光标

#### Parameters

-   `cursor` **string** 

### getExtData

获取用户自定义数据

Returns **(any | undefined)** 

### setExtData

设置用户自定义数据

#### Parameters

-   `extData`  用户自定义数据

### remove

移除点标记

## Icon

### Parameters

-   `opts`  

## Icon

## LabelMarker

标注类

### Parameters

-   `opts` **LabelMarkerOptions** 标注参数
    -   `opts.name` **string** 标注名称，作为标注标识，并非最终在地图上显示的文字内容，显示文字内容请设置 opts.text.content
    -   `opts.position` **(Vector2 | LngLat)** 标注位置
    -   `opts.zooms` **Vector2** 标注显示级别范围， 可选值：[2,20]
    -   `opts.opacity` **number** 标注透明度，默认值: 1
    -   `opts.rank` **number** 避让优先级，获取标注的优先级，该优先级用于 labelsLayer 支持避让时，rank 值大的标注会避让掉 rank 值低的标注。默认值：1
    -   `opts.zIndex` **number** 同一 LabelsLayer 内标注显示层级，数字越大越靠前，默认值: 1
    -   `opts.visible` **boolean** 标注是否可见， 默认值: true
    -   `opts.extData` **any** 用户自定义类型数据，可将自定义数据保存在该属性上，方便后续操作使用。
    -   `opts.icon` **IconOptions** 标注图标设置
        -   `opts.icon.image` **string** 图标 url。
        -   `opts.icon.size` **(Vector2 | Size)** 图标大小，默认值：[36, 36]
        -   `opts.icon.clipOrigin` **(Vector2 | Pixel)** 图标所在图片偏移位置，默认值: [0, 0]
        -   `opts.icon.clipSize` **(Vector2 | Size)** 图标所在图片裁剪大小，若未设置，则使用图片大小
        -   `opts.icon.anchor` **(Vector2 | Pixel \| string)** 图标锚点，锚点位置对应设置的 position 位置。可选值：'top-left'| 'top-center'|'top-right'|'middle-left'|'center'| 'middle-right'| 'bottom-left'| 'bottom-center'| 'bottom-right' 。默认值：'top-left'。
    -   `opts.text` **TextOptions** 标注文本设置
        -   `opts.text.content` **string** 文本标注的内容，该属性为直接显示在标注上的文本内容。
        -   `opts.text.direction` **string** 文本标注方位。若设置了 icon，则 direction 是以 icon 为中心的偏移，若未设置 icon，则相对 position 偏移。
            可选值：'top'|'right'|'bottom'|'left'|'center'。默认值: right
        -   `opts.text.offset` **(Pixel | Vector2)** 为偏移量，在 direction 基础上的偏移。默认值[0, 0]
        -   `opts.text.zooms` **Vector2** 文本显示级别范围，可单独设置文本显示范围
        -   `opts.text.style` **TextStyleOptions** 文本样式设置
            -   `opts.text.style.fontSize` **number** 文字大小，默认值： 12
            -   `opts.text.style.fillColor` **string** 文字颜色
            -   `opts.text.style.strokeColor` **string** 文字描边颜色
            -   `opts.text.style.padding` **(string \| Array&lt;(string \| number)>)** 文字 padding。默认值：[3, 3, 3, 3]
            -   `opts.text.style.backgroundColor` **string** 文字背景颜色
            -   `opts.text.style.borderColor` **string** 文字背景描边颜色
            -   `opts.text.style.borderWidth` **number** 文字背景描边粗细
            -   `opts.text.style.fold` **boolean** 文字是否折行（6个字一折行）

### Examples

```javascript
// 创建一个 LabelMarker 实例
var labelMarker = new AMap.LabelMarker({
    position: [116.468599, 39.995847],
    opacity: 1,
    zIndex: 2,
    icon: {
        image: 'https://a.amap.com/jsapi_demos/static/images/poi-marker.png',
        anchor: 'bottom-center',
        size: [25, 34],
        clipOrigin: [459, 92],
        clipSize: [50, 68]
    },
    text: {
        content: '香猪坊',
        direction: 'right',
        style: {
            fontSize: 15,
            fillColor: '#fff',
            strokeColor: 'rgba(255,0,0,0.5)',
            strokeWidth: 2,
            padding: [3, 10],
            backgroundColor: 'yellow',
            borderColor: '#ccc',
            borderWidth: 3,
        }
    }
});
// 创建一个 LabelsLayer 实例来承载 LabelMarker，[LabelsLayer 文档](https://lbs.amap.com/api/jsapi-v2/documentation#labelslayer)
var labelsLayer = new LabelsLayer({
    collision: true,
});
// 将 LabelMarker 实例添加到 LabelsLayer 上
labelsLayer.add(labelMarker);
// 将 LabelsLayer 添加到地图上
map.add(labelsLayer);
```

### getName

获取标注的名称，作为标注标识，并非最终在地图上显示的文字内容

Returns **(string \| undefined)** 

### setName

设置标注的名称，作为标注标识，并非最终在地图上显示的文字内容

#### Parameters

-   `name` **string** 

### getPosition

获取标注的显示位置

Returns **LngLat** 

### setPosition

设置标注的位置

#### Parameters

-   `position` **(LngLat | \[number] | string)** 

### getZooms

获取标注显示级别范围

Returns **(Vector2 | undefined)** 

### setZooms

设置显示级别范围

#### Parameters

-   `zooms` **\[number]** 

### getOpacity

获取标注透明度值

Returns **(number \| undefined)** 

### setOpacity

设置标注透明度

#### Parameters

-   `opacity` **number** 

### setRotation

设置标注旋转角度

#### Parameters

-   `angle` **number** 旋转角度

### getRotation

获取标注旋转角度

Returns **(number \| `0`)** 旋转角度

### getzIndex

获取标注的叠加顺序

Returns **(number \| undefined)** 

### setzIndex

设置标注的叠加顺序

#### Parameters

-   `zIndex` **number** 

### getRank

获取标注的优先级，该优先级用于 labelsLayer 支持避让时，rank 值大的标注会避让掉 rank 值低的标注。

Returns **(number \| undefined)** 

### setRank

设置标注的优先级，该优先级用于 labelsLayer 支持避让时，rank 值大的标注会避让掉 rank 值低的标注。

#### Parameters

-   `rank` **number** 

### getText

获取标注的文本设置

Returns **(LabelMarkerTextOptions | undefined)** 

### setText

设置标注的文本设置，可设置显示的文字内容和文字样式等

#### Parameters

-   `textOpts` **LabelMarkerTextOptions** 

### getIcon

获取标注的图标设置

Returns **(LabelMarkerIconOptions | undefined)** 

### setIcon

设置标注的图标设置，可设置显示的标注图片

#### Parameters

-   `iconOpts` **LabelMarkerIconOptions** 

### getOptions

获取标注的全部属性配置

Returns **LabelMarkerOptions** 

### getExtData

获取用户自定义属性

Returns **(any | undefined)** 

### setExtData

设置用户自定义属性

#### Parameters

-   `extData`  

### setTop

是否设置置顶标注，设置为 true 表示该标注会显示在所有标注之前

#### Parameters

-   `isTop` **boolean** 

### setVisible

设置该标注的可见性

#### Parameters

-   `visible` **boolean** 

### getVisible

获取该标注的可见性

Returns **(boolean \| undefined)** 

### getCollision

获取该标注是否被避让，从而没有显示

Returns **(boolean \| undefined)** 

### show

标注显示

### hide

标注隐藏

### remove

将自身从标注层移除

### getStatus

获取函数执行状态时间节点

Returns **Array&lt;string>** 

### moveTo

以给定速度移动标注到指定位置, 需加载 AMap.MoveAnimation 插件才可使用

#### Parameters

-   `targetPosition` **(LngLat | Vector2)** 指定位置
-   `opts` **MoveToOptions** moveTo 动画参数
    -   `opts.duration` **number** 每段动画持续时长, 单位：ms
    -   `opts.speed` **number** 动画速度，已废弃
    -   `opts.easing` **EasingCallback** easing 时间函数
    -   `opts.autoRotation` **boolean** 覆盖物是否沿路径旋转

#### Examples

```javascript
AMap.plugin('AMap.MoveAnimation', function(){
    // 加载完 AMap.MoveAnimation 插件以后，创建一个 LabelMarker 实例
    const animationLabel = new AMap.LabelMarker({
        content: '标注',
        position: new AMap.LngLat(116.397389,39.909466),
        text: {
            content: '动画标注'
        }
    });
    labelsLayer.add(animationLabel);
    // 调用 moveTo 方法
    animationLabel.moveTo([116.397389, 39.909466], {
        duration: 1000,
        delay: 500,
    });
});
```

### moveAlong

以指定的时长，标注沿指定的路径移动，加载 AMap.MoveAnimation 后可以使用

#### Parameters

-   `path` **(Array&lt;LngLat> | Array&lt;Vector2> | Array&lt;MoveAlongObj>)** 路径数组
-   `opts` **MoveAlongOptions** moveAlong 动画参数 可选
    -   `opts.duration` **(number \| AnimationCallback)** 每段动画持续时长, 单位：ms
    -   `opts.speed` **(number \| AnimationCallback)** 每段动画速度，已废弃
    -   `opts.easing` **EasingCallback** easing 时间函数
    -   `opts.circlable` **boolean** 动画是否循环
    -   `opts.delay` **(number \| AnimationCallback)** 延迟动画时长
    -   `opts.aniInterval` **number** 每段完整动画间隔时长
    -   `opts.autoRotation` **boolean** 覆盖物是否沿路径旋转

#### Examples

```javascript
const path = [
    new AMap.LngLat(116.397389, 39.909466),
    new AMap.LngLat(116.379707, 39.968168),
    new AMap.LngLat(116.434467, 39.95001),
    new AMap.LngLat(116.46365, 39.979481),
    new AMap.LngLat(116.397389, 39.909466),
];
const customData = [
    { position: path[0], duration: 200 },
    { position: path[1], duration: 400 },
    { position: path[2], duration: 600 },
    { position: path[3], duration: 800 },
    { position: path[4], duration: 1000 },
];
AMap.plugin('AMap.MoveAnimation', function(){
    // 加载完 AMap.MoveAnimation 插件以后，创建一个 LabelMarker 实例
    const animationLabel = new AMap.LabelMarker({
        content: '标注',
        position: new AMap.LngLat(116.397389,39.909466),
        text: {
            content: '动画标注'
        }
    });
    labelsLayer.add(animationLabel);
    // 调用 moveAlong 方法
    animationLabel.moveAlong(customData);
});
```

### startMove

开启标注动画，加载 AMap.MoveAnimation 后创建的标注可以使用

#### Examples

```javascript
animationLabel.startMove();
```

### stopMove

停止标注动画，加载 AMap.MoveAnimation 后创建的标注可以使用

#### Examples

```javascript
animationLabel.stopMove();
```

### pauseMove

暂停标注动画，加载 AMap.MoveAnimation 后创建的标注可以使用

#### Examples

```javascript
animationLabel.pauseMove();
```

### resumeMove

重新启动标注动画，加载 AMap.MoveAnimation 后创建的标注可以使用

#### Examples

```javascript
animationLabel.resumeMove();
```

### richText

设置富文本

#### Parameters

-   `richText` **any** 

### richText

获取富文本属性信息

Returns **any** 

## ElasticMarker

灵活点标记

### Parameters

-   `opts` **ElasticMarkerOptions** 灵活点标记参数
    -   `opts.map` **Map** 要显示该marker的地图对象
    -   `opts.position` **(Vector | LngLat)** 点标记在地图上显示的位置
    -   `opts.visible` **boolean** 点标记是否可见，默认为true
    -   `opts.zIndex` **number** 点标记的叠加顺序
    -   `opts.offset` **(Vector | Pixel)** 点标记显示位置偏移量
    -   `opts.clickable` **boolean** 点标记是否可点击
    -   `opts.draggable` **boolean** 设置点标记是否可拖拽移动
    -   `opts.bubble` **boolean** 事件是否冒泡，默认为 false
    -   `opts.cursor` **string** 指定鼠标悬停时的鼠标样式
    -   `opts.topWhenClick` **boolean** 鼠标点击时marker是否置顶
    -   `opts.zoomStyleMapping` **Record&lt;string, number>** 表示地图级别与styles中样式的映射，{14:0,15:0,16:1,17:1,}表示14到15级使用styles中的第0个样式，16-17级使用第二个样式
    -   `opts.extData` **any** 用户自定义属性
    -   `opts.styles` **Array&lt;ElasticStyle>** 多个不同样式的数组
        -   `opts.styles.icon` **ElasticIcon** 灵活标注图标样式类型
            -   `opts.styles.icon.img` **string** 图标 url
            -   `opts.styles.icon.size` **Vector** 图标显示大小
            -   `opts.styles.icon.anchor` **(Vector | string)** 图标锚点
            -   `opts.styles.icon.imageOffset` **(Vector | string)** 图片偏移量
            -   `opts.styles.icon.imageSize` **number** 图片大小
            -   `opts.styles.icon.fitZoom` **number** 最合适的级别，在此级别下显示为原始大小
            -   `opts.styles.icon.scaleFactor` **number** 地图放大一级的缩放比例系数
            -   `opts.styles.icon.maxScale` **number** 最大放大比例
            -   `opts.styles.icon.minScale` **number** 最小放大比例
        -   `opts.styles.label` **ElasticLabel** 灵活标注文本样式类型
            -   `opts.styles.label.content` **ElasticLabel** 文本内容
            -   `opts.styles.label.position` **ElasticLabel** 文本位置相对于图标的基准点，可选值：BL、BM、BR、ML、MR、TL、TM、TR分别代表左下角、底部中央、右下角、左侧中央、右侧中央、左上角、顶部中央、右上角
            -   `opts.styles.label.offset` **ElasticLabel** 相对position的偏移量
            -   `opts.styles.label.minZoom` **ElasticLabel** label的最小显示级别

### Examples

```javascript
// 样式列表
var stylesArr = [{
   icon: {
       img: 'https://a.amap.com/jsapi_demos/static/resource/img/men3.png',
       size: [16, 16],//可见区域的大小
       anchor: 'bottom-center',//锚点
       fitZoom: 14,//最合适的级别
       scaleFactor: 2,//地图放大一级的缩放比例系数
       maxScale: 2,//最大放大比例
       minScale: 1//最小放大比例
   },
   label: {
       content: '百花殿',
       position: 'BM',
       minZoom: 15
   }
}, {
   icon: {
       img: 'https://a.amap.com/jsapi_demos/static/resource/img/tingzi.png',
       size: [48, 63],
       anchor: 'bottom-center',
       fitZoom: 17.5,
       scaleFactor: 2,
       maxScale: 2,
       minScale: 0.125
   },
   label: {
       content: '万寿亭',
       position: 'BM',
       minZoom: 15
   }
}];
zoom 与样式的映射
var zoomStyleMapping1 = {
   14: 0,  // 14级使用样式 0
   15: 0,
   16: 0,
   17: 0,
   18: 1,
   19: 1,
   20: 1,
};
// 加载灵活点标记的插件
AMap.plugin(['AMap.ElasticMarker'], function(){
    var elasticMarker = new AMap.ElasticMarker({
        position: [116.405562, 39.881166],
        // 指定样式列表
        styles: stylesArray,
        // 指定 zoom 与样式的映射
        zoomStyleMapping: zoomStyleMapping,
    });
    map.add(elasticMarker);
});
```

### getTitle

获取获取灵活点标记标记的文字提示

Returns **(string \| undefined)** 

### setTitle

设置鼠标滑过灵活点标记时的文字提示

#### Parameters

-   `title` **string** 灵活点标记的文字提示

### getClickable

获取灵活点标记是否支持鼠标单击事件

Returns **boolean** 

### setClickable

设置灵活点标记是否支持鼠标单击事件

#### Parameters

-   `clickable` **boolean** 默认值: true

### getMap

获取覆盖物的地图实例

Returns **(Map | null)** 

### setMap

将覆盖物设置到地图上

#### Parameters

-   `map` **(Map | null)** 

### show

显示覆盖物

### hide

隐藏覆盖物

### getPosition

获取覆盖物位置

Returns **any** 

### setPosition

设置灵活点标记位置

#### Parameters

-   `position` **Vector** 

### setAnchor

设置灵活点标记锚点

#### Parameters

-   `anchor` **string** 

### getzIndex

获取覆盖物的叠加顺序

Returns **(number \| undefined)** 

### setzIndex

设置覆盖物的叠加顺序

#### Parameters

-   `zIndex` **number** 

### getOptions

获取覆盖物的所有属性

Returns **OverlayOptions** 

### getBounds

Returns **Bounds** 

### getDraggable

获取灵活点标记对象是否可拖拽移动

Returns **boolean** 

### setDraggable

设置灵活点标记对象是否可拖拽移动

#### Parameters

-   `draggable` **boolean** 

### getTop

获取该灵活点标记是否置顶

Returns **boolean** 

### setTop

地图上有多个marker时，设置是否置顶该灵活点标记

#### Parameters

-   `isTop` **boolean** 

### getCursor

获取鼠标悬停时的光标设置

Returns **string** 

### setCursor

设置鼠标悬停时的光标

#### Parameters

-   `cursor` **string** 

### getExtData

获取用户自定义数据

Returns **(any | undefined)** 

### setExtData

设置用户自定义数据

#### Parameters

-   `extData`  用户自定义数据

### remove

移除点标记

## MarkerCluster

用于展示大量点标记，将点标记按照距离进行聚合，以提高绘制性能。点聚合支持用户自定义样式，以插件形式调用。

### Parameters

-   `map` **Map** 要添加点聚合的地图对象
-   `dataOptions` **Array** 需要进行聚合显示的点数据
    -   `dataOptions.lnglat` **Array** 点标记的经纬度信息
    -   `dataOptions.weight` **number** 点标记的权重信息，以权重高的点为中心进行聚合
-   `MarkerClusterOptions` **Object** 点聚合属性设置
    -   `MarkerClusterOptions.gridSize` **Number** 聚合计算时网格的像素大小，默认60
    -   `MarkerClusterOptions.maxZoom` **Number** 最大的聚合级别，大于该级别就不进行相应的聚合。默认值为 18，即小于 18 级的级别均进行聚合，18 及以上级别不进行聚合
    -   `MarkerClusterOptions.averageCenter` **Boolean** 聚合点的图标位置是否是所有聚合内点的中心点。默认为 true。数据中如果含有权重值，以权重高的点为中心进行聚合
    -   `MarkerClusterOptions.clusterByZoomChange` **Boolean** 地图缩放过程中是否聚合。默认值 false。
    -   `MarkerClusterOptions.styles` **Array&lt;Object>** <div>
         <div>指定聚合后的点标记的图标样式，可缺省，缺省时为默认样式</div>
         <div>数据元素分别对应聚合量在1-10,11-100,101-1000…的聚合点的样式；</div>
         <div>当用户设置聚合样式少于实际叠加的点数，未设置部分按照系统默认样式显示；</div>
         <div>单个图标样式包括以下几个属性：</div>
         <div>1. {string} url：图标显示图片的url地址（必选）</div>
         <div>2. {AMap.Size} size：图标显示图片的大小（必选）</div>
         <div>3. {AMap.Pixel} offset：图标定位在地图上的位置相对于图标左上角的偏移值。默认为(0,0),不偏移（可选）</div>
         <div>4. {AMap.Pixel} imageOffset：图片相对于可视区域的偏移值，此功能的作用等同CSS中的background-position属性。默认为(0,0)，不偏移（可选）</div>
         <div>5. {String} textColor：文字的颜色，默认为"#000000"（可选）</div>
         <div>6. {Number} textSize：文字的大小，默认为10（可选）</div>
        </div>
    -   `MarkerClusterOptions.renderClusterMarker` **function** <div>
         <div>该方法用来实现聚合点的自定义绘制，由开发者自己实现，API 将在绘制每个聚合点的时候调用这个方法，可以实现聚合点样式的灵活设定，指定了 renderClusterMarker 后 styles 无效。</div>
         <div>该函数的入参为一个Object，包含如下属性：</div>
         <div>1. count: 当前聚合点下聚合的 Marker 的数量</div>
         <div>2. marker: 当前聚合点显示的 Marker</div>
        </div>
    -   `MarkerClusterOptions.renderMarker` **function** <div>
         <div>该方法用来实现非聚合点的自定义绘制，由开发者自己实现，API 将在绘制每个非聚合点的时候调用这个方法</div>
         <div>该函数的入参为一个Object，包含如下属性：</div>
         <div>marker: 非聚合点 Marker 对象</div>
        </div>

### Examples

```javascript
// 数据格式为一组含有经纬度信息的数组，如下所示。其中【经纬度】lnglat 为必填字段，【权重】weight 为可选字段。
var points = [
 { weight: 8, lnglat: ["108.939621", "34.343147"] },
 { weight: 1, lnglat: ["112.985037", "23.15046"] },
 { weight: 1, lnglat: ["110.361899", "20.026695"] },
 { weight: 1, lnglat: ["121.434529", "31.215641"] }
];
// 加载点聚合插件
map.plugin(["AMap.MarkerCluster"],function(){
 var cluster = new AMap.MarkerCluster(map, points, {
     gridSize: 80 // 聚合网格像素大小
 });
});
```

### addData

在原数据基础上添加数据，格式同 dataOptions

#### Parameters

-   `dataOptions` **dataOptions** 

### setData

设置数据，格式同 dataOptions

#### Parameters

-   `dataOptions` **dataOptions** 

### getClustersCount

获取聚合点的总数量

Returns **Number** 

### getGridSize

获取聚合网格的像素大小

Returns **Number** 

### setGridSize

设置聚合网格的像素大小

#### Parameters

-   `size` **Number** 像素大小

### getMaxZoom

获取地图中点标记的最大聚合级别

Returns **Number** 

### setMaxZoom

设置地图中点标记的最大聚合级别

#### Parameters

-   `zoom` **Number** 级别

### setStyles

设置样式聚合点，格式同 opts.styles

#### Parameters

-   `Map` **Map** 

### getStyles

获取样式

Returns **Array** 

### getMap

获取地图对象

Returns **Map** 

### setMap

设置地图对象

#### Parameters

-   `Map` **Map** 

### isAverageCenter

获取单个聚合点位置是否是聚合内所有标记的平均中心

Returns **Boolean** 

### setAverageCenter

设置聚合点位置是否是所有聚合点的中心

#### Parameters

-   `averageCenter` **Boolean** 

## MassMarks

**Extends AMap.Event**

海量点类

### Parameters

-   `data` **Array&lt;MassData>** 海量点数据参数
    -   `data.lnglat` **LngLat** 经纬度
    -   `data.style` **number** 样式索引值
-   `opts` **Array&lt;MassMarkersOptions>** 海量点参数
    -   `opts.zIndex` **number** 图标 url
    -   `opts.opacity` **number** 图标显示大小
    -   `opts.zooms` **Vector2** 旋转角度
    -   `opts.cursor` **string** 锚点位置
    -   `opts.style` **(MassMarkersStyleOptions | Array&lt;MassMarkersStyleOptions>)** 点展示优先级
        -   `opts.style.url` **string** 图标 url
        -   `opts.style.size` **(Vector2 | Size)** 图标显示大小
        -   `opts.style.rotation` **number** 旋转角度
        -   `opts.style.anchor` **Pixel** 锚点位置
        -   `opts.style.zIndex` **number** 点展示优先级，默认为使用样式的索引值。

### Examples

```javascript
// 创建 MassMarks 实例，[亲手试一试](https://lbs.amap.com/api/jsapi-v2/example/marker/massmarks)
var massMarks = new AMap.MassMarks(data, {
    opacity: 0.8,
    zIndex: 111,
    cursor: 'help',
    style: style,
});
// 将海量点实例添加到地图上
map.add(massMarks);
```

### setMap

设置显示MassMark的地图对象

#### Parameters

-   `map` **Map** 

### getMap

获取Marker所在地图对象

Returns **any** 

### getData

输出MassMark的数据集，数据结构同setDatas中的数据集

Returns **Array&lt;MassData>** 

### setData

设置MassMark展现的数据集

#### Parameters

-   `data` **Array&lt;MassData>** 

### getStyle

获取MassMark的显示样式

Returns **Array&lt;MassMarkersStyleOptions>** 

### setStyle

设置MassMark的显示样式，可设置单个样式或样式列表，每条数据通过设置的样式索引值获取对应样式

#### Parameters

-   `style` **(MassMarkersStyleOptions | Array&lt;MassMarkersStyleOptions>)** 

### setOpacity

获取海量点图层的透明度

Returns **number** 

### setzIndex

设置海量点图层透明度

#### Parameters

-   `opacity` **number** 透明度

### setzIndex

设置海量点图层叠加顺序

#### Parameters

-   `zIndex` **number** 叠加顺序

### getzIndex

获取海量点图层的透明度

Returns **number** 

### getZooms

获取海量点图层可见层级范围

Returns **Vector2** 

### setZooms

设置海量点图层可见层级范围

#### Parameters

-   `zooms` **Vector2** 可见层级范围

### show

显示海量点图层

### hide

隐藏海量点图层

### clear

清除海量点

## MoveAnimation

用于实现点标记沿线段或者路径轨迹移动的动画基类，可用于满足轨迹回放、实时轨迹等场景。MoveAnimation无需单独声明或初始化，Marker、Text、LabelMarker均已继承了 MoveAnimation的实现。

### moveTo

以给定时间移动点标记到指定位置，加载 AMap.MoveAnimation 后可以使用

#### Parameters

-   `targetPosition` **(LngLat | Vector)** 指定位置
-   `opts` **MoveToOptions** moveTo 动画参数
    -   `opts.duration` **number** 每段动画持续时长, 单位：ms
    -   `opts.speed` **number** 动画速度，已废弃
    -   `opts.easing` **EasingCallback** easing 时间函数
    -   `opts.autoRotation` **boolean** 覆盖物是否沿路径旋转

#### Examples

```javascript
AMap.plugin('AMap.MoveAnimation', function(){
     const animationMarker = new AMap.Marker({
        position: new AMap.LngLat(116.397389,39.909466),
     });
    animationMarker.moveTo([116.397389, 39.909466], {
        duration: 1000,
        delay: 500,
    });
});
```

### moveAlong

以指定的时长，点标记沿指定的路径移动，加载 AMap.MoveAnimation 后可以使用

#### Parameters

-   `path` **(Array&lt;LngLat> | Array&lt;Vector> | Array&lt;MoveAlongObj>)** 路径数组
-   `opts` **MoveAlongOptions** moveAlong 动画参数 可选
    -   `opts.duration` **(number \| AnimationCallback)** 每段动画持续时长, 单位：ms
    -   `opts.speed` **(number \| AnimationCallback)** 每段动画速度，已废弃
    -   `opts.easing` **EasingCallback** easing 时间函数
    -   `opts.circlable` **boolean** 动画是否循环
    -   `opts.delay` **(number \| AnimationCallback)** 延迟动画时长
    -   `opts.aniInterval` **number** 每段完整动画间隔时长
    -   `opts.autoRotation` **boolean** 覆盖物是否沿路径旋转

#### Examples

```javascript
const path = [
    new AMap.LngLat(116.397389, 39.909466),
    new AMap.LngLat(116.379707, 39.968168),
    new AMap.LngLat(116.434467, 39.95001),
    new AMap.LngLat(116.46365, 39.979481),
    new AMap.LngLat(116.397389, 39.909466),
];
const customData = [
    { position: path[0], duration: 200 },
    { position: path[1], duration: 400 },
    { position: path[2], duration: 600 },
    { position: path[3], duration: 800 },
    { position: path[4], duration: 1000 },
];
AMap.plugin('AMap.MoveAnimation', function(){
    const animationMarker = new AMap.Marker({
        position: new AMap.LngLat(116.397389,39.909466),
        angle: 90,
    });
    animationMarker.moveAlong(customData);
});
```

### startMove

开启点标记动画，加载 AMap.MoveAnimation 后可以使用

#### Examples

```javascript
animationMarker.startMove();
```

### stopMove

停止点标记动画，加载 AMap.MoveAnimation 后可以使用

#### Examples

```javascript
animationMarker.stopMove();
```

### resumeMove

重新启动点标记动画，加载 AMap.MoveAnimation 后可以使用

#### Examples

```javascript
animationMarker.resumeMove();
```

## AnimationCallback

MoveAnimation 回调函数

Type: function

### Parameters

-   `index` **number** 运行到点的索引
-   `data` **LngLat** 当前点经纬度

Returns **number** 

## EasingCallback

时间函数回调

Type: function

### Parameters

-   `passedTime` **number** 已经过去的时长

Returns **number** 
