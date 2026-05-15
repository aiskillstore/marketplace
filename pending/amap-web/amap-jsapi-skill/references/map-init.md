# 地图加载与初始化 (Map Initialization)

本指南介绍如何使用 `@amap/amap-jsapi-loader` 异步加载高德地图 JSAPI v2.0，并初始化地图实例。

## 前置条件

在加载地图前，**必须**先完成安全配置。请参考 [安全配置文档](./security.md)。

```javascript
// 必须在加载前执行
window._AMapSecurityConfig = {
  securityJsCode: '您的安全密钥',
};
```

## 1. 引入加载器
使用 script 标签加载 loader.js：
```bash
<script src="https://webapi.amap.com/loader.js"></script>
```

## 2. 异步加载 JSAPI

使用 `AMapLoader.load` 方法加载 API。

```javascript
import AMapLoader from '@amap/amap-jsapi-loader';

AMapLoader.load({
    key: '您的Key',              // 必填，申请的 Web 端开发者 Key
    version: '2.0',             // 必填，指定版本号
    plugins: ['AMap.Scale'],    // 预加载插件列表
}).then((AMap) => {
    // JSAPI 加载完成，可以开始初始化地图
    initMap(AMap);
}).catch((e) => {
    console.error('地图加载失败', e);
});
```

## 3. 进阶配置 (Advanced Configuration)

### 加载 Loca 数据可视化库
Loca 是高德地图基于 WebGL 的高性能数据可视化库。需要在加载器中显式声明 `Loca` 配置。

```javascript
AMapLoader.load({
    key: '您的Key',
    version: '2.0',
    Loca: {
        version: '2.0.0' // 指定 Loca 版本
    }
}).then((AMap) => {
    const map = new AMap.Map('container');
    
    // 初始化 Loca 容器
    const loca = new Loca.Container({
        map: map,
    });
});
```


```

### 加载器参数详解

| 参数 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `key` | String | 是 | 申请好的 Web 端开发者 Key |
| `version` | String | 是 | 指定要加载的 JSAPI 版本，如 "2.0" |
| `plugins` | Array | 否 | 需要预加载的插件列表，如 `['AMap.Scale', 'AMap.ToolBar']` |
| `Loca` | Object | 否 | Loca 库配置，包含 `{ version: '2.0.0' }` |
| `AMapUI` | Object | 否 | AMapUI 库配置，包含 `{ version: '1.1', plugins: [] }` |
| `serviceHost` | String | 否 | 代理服务器地址（通常在安全配置中全局设置，此处也可覆盖） |

## 3. 初始化地图实例

创建 `AMap.Map` 实例，建议开启 3D 视图模式以获得最佳性能。

```javascript
function initMap(AMap) {
    const map = new AMap.Map('container', {
        viewMode: '3D',    // 开启 3D 模式 (推荐)
        zoom: 11,          // 初始化缩放级别 [2, 20]
        center: [116.397428, 39.90923], // 初始化中心点坐标 [lng, lat]
        pitch: 45,         // 俯仰角度，有效范围 [0, 83]
        rotation: 0,       // 旋转角度
        mapStyle: 'amap://styles/normal', // 地图样式
    });

    // 添加控件
    map.addControl(new AMap.Scale());
}
```
### 常用配置项

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| viewMode | String | '2D' | 渲染模式：'2D' 或 '3D' |
| zoom | Number | - | 初始缩放级别 |
| center | Array | - | 初始中心点 [lng, lat] |
| pitch | Number | 0 | 俯仰角度 (3D 模式有效) |
| rotation | Number | 0 | 旋转角度 |
| mapStyle | String | - | 地图样式 URL |
| zooms | Array | [2, 20] | 缩放级别范围 |

## 4. 地图生命周期管理
### 地图加载完成

```javascript
map.on('complete', function() {
  console.log('地图加载完成');
});
```

### 销毁地图
在组件卸载或不再需要地图时，务必调用 `destroy` 方法以释放 WebGL 上下文和内存资源。

```javascript
// 销毁地图实例
if (map) {
    map.destroy();
    map = null;
}
```
## 5. 地图样式

### 官方主题样式

```javascript
const map = new AMap.Map('container', {
  mapStyle: 'amap://styles/normal', // 标准
  // mapStyle: 'amap://styles/dark',      // 幻影黑
  // mapStyle: 'amap://styles/light',     // 月光银
  // mapStyle: 'amap://styles/whitesmoke',// 远山黛
  // mapStyle: 'amap://styles/fresh',     // 草色青
  // mapStyle: 'amap://styles/grey',      // 雅士灰
  // mapStyle: 'amap://styles/graffiti',  // 涂鸦
  // mapStyle: 'amap://styles/macaron',   // 马卡龙
  // mapStyle: 'amap://styles/blue',      // 靛青蓝
  // mapStyle: 'amap://styles/darkblue',  // 极夜蓝
  // mapStyle: 'amap://styles/wine',      // 酱籽
});

// 动态切换样式
map.setMapStyle('amap://styles/dark');
```

## 完整示例 (Vue 3)

```vue
<template>
  <div id="map-container" style="width: 100%; height: 500px;"></div>
</template>

<script setup>
import { onMounted, onUnmounted, shallowRef } from 'vue';
import AMapLoader from '@amap/amap-jsapi-loader';

const map = shallowRef(null); // 使用 shallowRef 避免深层响应式带来的性能损耗

onMounted(() => {
  window._AMapSecurityConfig = { securityJsCode: '您的安全密钥' };

  AMapLoader.load({
    key: '您的Key',
    version: '2.0',
    plugins: ['AMap.Scale'], // 按需加载插件
  }).then((AMap) => {
    map.value = new AMap.Map('map-container', {
      viewMode: '3D',
      zoom: 12,
      center: [120.15, 30.28],
    });
    // 添加插件
    map.value.addControl(new AMap.Scale());
  }).catch(e => console.error(e));
});

onUnmounted(() => {
  map.value?.destroy();
});
</script>
```
## 5. 地图控件

```javascript
// 比例尺
map.addControl(new AMap.Scale());

// 工具条（缩放、定位）
map.addControl(new AMap.ToolBar({
  position: 'RT' // 右上角
}));

// 3D 控制（旋转、俯仰）
map.addControl(new AMap.ControlBar({
  position: { right: '10px', top: '10px' }
}));

// 鹰眼（缩略图）
map.addControl(new AMap.HawkEye());

// 图层切换
map.addControl(new AMap.MapType());
```

## 完整示例 (React Hooks)

```jsx
import React, { useEffect, useRef } from 'react';
import AMapLoader from '@amap/amap-jsapi-loader';

export default function MapComponent() {
  const mapRef = useRef(null);

  useEffect(() => {
    // 安全密钥配置
    window._AMapSecurityConfig = { securityJsCode: '您的安全密钥' };

    AMapLoader.load({
      key: '您的Key',
      version: '2.0',
      plugins: ['AMap.Scale'], // 预加载插件
    }).then((AMap) => {
      mapRef.current = new AMap.Map('map-container', {
        viewMode: '3D',
        zoom: 11,
        center: [116.397428, 39.90923],
      });

      // 添加控件
      mapRef.current.addControl(new AMap.Scale());
    }).catch((e) => {
      console.error('地图加载失败', e);
    });

    // 销毁地图
    return () => {
      mapRef.current?.destroy();
    };
  }, []);

  return <div id="map-container" style={{ width: '100%', height: '500px' }} />;
}
```