# 地理编码 (Geocoder)

地理编码服务提供了将地址转换为经纬度（正向地理编码）和将经纬度转换为地址（逆向地理编码）的功能。

## 1. 加载插件

使用 `AMapLoader` 加载时需要包含 `AMap.Geocoder` 插件。

```javascript
AMapLoader.load({
    key: '您的Key',
    version: '2.0',
    plugins: ['AMap.Geocoder'] // 预加载插件
}).then((AMap) => {
    // ...
});
```

## 2. 正向地理编码 (地址 -> 坐标)

将详细的结构化地址转换为经纬度坐标。

```javascript
const geocoder = new AMap.Geocoder({
    city: '010', // 城市，默认全国
});

geocoder.getLocation('北京市朝阳区阜通东大街6号', function(status, result) {
    if (status === 'complete' && result.info === 'OK') {
        // result.geocodes 是一个数组
        const { location, formattedAddress } = result.geocodes[0];
        console.log('坐标：', location.lng, location.lat);
        console.log('规范地址：', formattedAddress);
        
        // 在地图上标记
        map.setCenter(location);
        new AMap.Marker({
            map: map,
            position: location
        });
    } else {
        console.error('地理编码失败');
    }
});
```

## 3. 逆向地理编码 (坐标 -> 地址)

将经纬度坐标转换为详细地址信息。

```javascript
const lnglat = [116.396574, 39.992706];

geocoder.getAddress(lnglat, function(status, result) {
    if (status === 'complete' && result.info === 'OK') {
        // result.regeocode 包含详细地址信息
        const address = result.regeocode.formattedAddress;
        console.log('地址：', address);
        
        // 获取周边 POI、道路等详细信息
        const { roads, pois, aois } = result.regeocode.addressComponent;
    } else {
        console.error('逆地理编码失败');
    }
});
```
## 完整示例

### 地址搜索定位

```javascript
const map = new AMap.Map('container', {
  zoom: 14,
  center: [116.397, 39.909]
});

const geocoder = new AMap.Geocoder({
  city: '北京',
  extensions: 'all'
});

const input = document.getElementById('addressInput');
const btn = document.getElementById('searchBtn');

btn.onclick = function() {
  const address = input.value.trim();
  if (!address) return;
  
  geocoder.getLocation(address, function(status, result) {
    if (status === 'complete' && result.geocodes.length > 0) {
      const geocode = result.geocodes[0];
      
      // 清除之前的标记
      map.clearMap();
      
      // 添加标记
      const marker = new AMap.Marker({
        map: map,
        position: geocode.location
      });
      
      // 信息窗体
      const infoWindow = new AMap.InfoWindow({
        content: `
          <div>
            <h4>${geocode.formattedAddress}</h4>
            <p>坐标: ${geocode.location.lng}, ${geocode.location.lat}</p>
          </div>
        `,
        offset: new AMap.Pixel(0, -30)
      });
      
      marker.on('click', function() {
        infoWindow.open(map, marker.getPosition());
      });
      
      // 移动视角
      map.setZoomAndCenter(16, geocode.location);
      
      // 自动打开信息窗体
      infoWindow.open(map, geocode.location);
    } else {
      alert('未找到该地址');
    }
  });
};
```

### 点击地图获取地址

```javascript
const map = new AMap.Map('container', {
  zoom: 14,
  center: [116.397, 39.909]
});

const geocoder = new AMap.Geocoder({
  extensions: 'all'
});

const infoWindow = new AMap.InfoWindow({
  offset: new AMap.Pixel(0, -15)
});

map.on('click', function(e) {
  const lnglat = [e.lnglat.getLng(), e.lnglat.getLat()];
  
  geocoder.getAddress(lnglat, function(status, result) {
    if (status === 'complete') {
      const address = result.regeocode.formattedAddress;
      
      infoWindow.setContent(`
        <div style="padding: 10px;">
          <p><strong>地址:</strong> ${address}</p>
          <p><strong>坐标:</strong> ${lnglat[0].toFixed(6)}, ${lnglat[1].toFixed(6)}</p>
        </div>
      `);
      
      infoWindow.open(map, e.lnglat);
    }
  });
});
```

## 注意事项

1. **城市限制**: 设置 city 可以提高编码准确度
2. **详细信息**: 需要 POI、道路等信息时设置 `extensions: 'all'`
3. **批量查询**: 批量查询需要设置 `batch: true`
4. **结果数量**: 正向编码可能返回多个结果，需要根据 level 判断准确度
5. **坐标格式**: 逆向编码支持数组 `[lng, lat]` 或 LngLat 对象
