## 事件

地图 JSAPI 具有完备的事件体系，在 2.0 版本中所有类型的实例均使用 on/off 方法进行时间的绑定和移除


## Event

JSAPI 的所有类型（地图、图层、覆盖物等）都实现了事件接口，用于给当前实例对象绑定、移除、清理事件回调

### Examples

```javascript
// 声明点击事件的回调函数
function onClick(e){
    console.log(e);
}
// 给地图实例绑定点击事件 onClick
map.on('click', onClick);

// 移除地图实例的 onClick 事件绑定
map.off('click', onClick);

// 清除地图实例上的所有 click 事件绑定
map.clearEvents('click');

// 覆盖物绑定鼠标移动事件
polygon.on('mousemove',console.log);

// 覆盖物绑定事件判断
polygon.hasEvents('mousemove',console.log);
```

### on

给实例绑定事件回调函数，同一个类型、同一个回调函数、同一个上下文只会绑定一次

#### Parameters

-   `type` **String** 事件类型
-   `function` **Function** 回调函数
-   `context` **Object** 事件上下文，缺省为实例本身
-   `once` **Boolean** 是否只执行一次

Returns **Object** 当前实例

### once

给实例绑定只执行一次的事件回调

#### Parameters

-   `type` **String** 事件类型
-   `fn` **Function** 回调函数
-   `context` **Object** 事件上下文，缺省为实例本身

Returns **Object** 当前实例

### off

移除当前实例的某一个事件回调

#### Parameters

-   `type` **String** 事件类型
-   `function` **Function** 事件回调函数
-   `context` **Object** 事件上下文，缺省为当前实例

Returns **Object** 当前实例

### hasEvents

判断当前实例是否已经绑定了某个事件回调

#### Parameters

-   `type` **String** 事件类型
-   `function` **Function** 事件回调
-   `context` **Object** 事件上下文

Returns **Boolean** 

### clearEvents

清除当前实例某一类型的全部事件回调

#### Parameters

-   `type` **String** 事件类型，如果此参数为空，清除实例上的所有绑定的事件回调

Returns **Object** 当前实例

### emit

模拟触发当前实例的某个事件

#### Parameters

-   `type` **String** 事件类型
-   `data` **Object** 事件回调时返回的数据，模拟的事件体应该完整，否则可能导致报错

Returns **Object** 当前实例
