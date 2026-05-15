# 路径规划 (Routing)

高德地图提供了驾车、步行、骑行和公交等多种路径规划服务。

## 1. 驾车路线规划 (Driving)

支持策略配置（如躲避拥堵、不走高速等）和多点路径规划。

```javascript
// 构造路线规划类
const driving = new AMap.Driving({
    map: map, // 绑定地图，自动绘制路线
    panel: 'panel-id', // 结果列表的容器 ID (可选)
    policy: AMap.DrivingPolicy.LEAST_TIME, // 策略：最快
});

// 根据经纬度规划
// 参数：起点，终点，(可选)途经点，回调
driving.search(
    [116.379028, 39.865042], // 起点
    [116.427281, 39.903719], // 终点
    function(status, result) {
        if (status === 'complete') {
            console.log('绘制驾车路线完成');
        } else {
            console.error('获取驾车数据失败：' + result);
        }
    }
);

// 根据关键字规划
driving.search([
    {keyword: '北京站', city: '北京'},
    {keyword: '北京大学', city: '北京'}
], function(status, result) {
    // ...
});
// 根据关键字规划
driving.search([
    {keyword: '北京站', city: '北京'},
    {keyword: '北京大学', city: '北京'}
], function(status, result) {
    // ...
});
```
## 完整示例

```javascript
const map = new AMap.Map('container', {
  zoom: 12,
  center: [116.397, 39.909]
});

const driving = new AMap.Driving({
  policy: AMap.DrivingPolicy.LEAST_TIME,
  showTraffic: true
});

function planDriving(start, end) {
  // 清除之前的路线
  driving.clear();
  
  driving.search(start, end, function(status, result) {
    if (status === 'complete') {
      const route = result.routes[0];
      
      // 提取路径点
      const path = [];
      route.steps.forEach(step => {
        path.push(...step.path);
      });
      
      // 绘制路线
      const polyline = new AMap.Polyline({
        path: path,
        strokeColor: '#1890ff',
        strokeWeight: 6,
        strokeOpacity: 0.9,
        lineJoin: 'round',
        lineCap: 'round'
      });
      map.add(polyline);
      
      // 显示信息
      showRouteInfo(route);
      
      // 调整视野
      map.setFitView();
    } else {
      alert('驾车规划失败：' + result);
    }
  });
}

function showRouteInfo(route) {
  const distance = (route.distance / 1000).toFixed(1) + ' 公里';
  const time = formatTime(route.time);
  const tolls = route.tolls ? route.tolls + ' 元' : '无';
  
  console.log(`距离: ${distance}, 时间: ${time}, 过路费: ${tolls}`);
}

function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.round((seconds % 3600) / 60);
  if (hours > 0) {
    return `${hours} 小时 ${minutes} 分钟`;
  }
  return `${minutes} 分钟`;
}

// 使用
planDriving([116.379028, 39.865042], [116.427281, 39.903719]);
```

## 自定义路线样式

```javascript
driving.search(start, end, function(status, result) {
  if (status === 'complete') {
    const route = result.routes[0];
    const path = [];
    
    route.steps.forEach(step => {
      path.push(...step.path);
    });
    
    // 底层阴影
    const shadowLine = new AMap.Polyline({
      path: path,
      strokeColor: '#0d47a1',
      strokeWeight: 10,
      strokeOpacity: 0.5
    });
    
    // 主路线
    const mainLine = new AMap.Polyline({
      path: path,
      strokeColor: '#1890ff',
      strokeWeight: 6,
      strokeOpacity: 0.9
    });
    
    map.add([shadowLine, mainLine]);
  }
});
```

## 清除路线

```javascript
// 使用内置方法
driving.clear();

// 或手动移除
map.remove(polyline);
```

## 注意事项

1. **起终点格式**: 支持经纬度数组或关键字对象
2. **途经点限制**: 最多支持 16 个途经点
3. **路况显示**: 设置 `showTraffic: true` 显示实时路况
4. **车牌限行**: 设置 `number` 参数可判断限行路段
5. **自动渲染**: 设置 map 和 panel 后会自动渲染路线和结果面板

## 2. 其他出行方式

接口调用方式与 `Driving` 类似。

### 步行 (Walking)

```javascript
const walking = new AMap.Walking({
    map: map,
    panel: 'panel'
});

walking.search([116.399028, 39.845042], [116.436281, 39.880719], function(status, result) {});
```
## 完整示例

```javascript
const map = new AMap.Map('container', {
  zoom: 14,
  center: [116.397, 39.909]
});

const walking = new AMap.Walking();

function planWalking(start, end) {
  walking.search(start, end, function(status, result) {
    if (status === 'complete') {
      const route = result.routes[0];
      
      // 提取路径点
      const path = [];
      route.steps.forEach(step => {
        path.push(...step.path);
      });
      
      // 绘制路线（虚线样式）
      const polyline = new AMap.Polyline({
        path: path,
        strokeColor: '#52c41a',
        strokeWeight: 5,
        strokeOpacity: 0.9,
        strokeStyle: 'dashed', // 虚线
        strokeDasharray: [10, 5]
      });
      map.add(polyline);
      
      // 添加起点终点标记
      addStartEndMarkers(start, end);
      
      // 显示信息
      const distance = formatDistance(route.distance);
      const time = formatTime(route.time);
      console.log(`步行距离: ${distance}, 预计时间: ${time}`);
      
      // 调整视野
      map.setFitView();
    } else {
      alert('步行规划失败');
    }
  });
}

function addStartEndMarkers(start, end) {
  // 起点
  new AMap.Marker({
    map: map,
    position: start,
    content: createMarkerContent('起', '#52c41a'),
    offset: new AMap.Pixel(-16, -40)
  });
  
  // 终点
  new AMap.Marker({
    map: map,
    position: end,
    content: createMarkerContent('终', '#f5222d'),
    offset: new AMap.Pixel(-16, -40)
  });
}

function createMarkerContent(text, color) {
  return `
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="40" viewBox="0 0 32 40">
      <path d="M16 0C7.163 0 0 7.163 0 16c0 12 16 24 16 24s16-12 16-24C32 7.163 24.837 0 16 0z" fill="${color}"/>
      <circle cx="16" cy="14" r="6" fill="#fff"/>
      <text x="16" y="18" text-anchor="middle" fill="${color}" font-size="10" font-weight="bold">${text}</text>
    </svg>
  `;
}

function formatDistance(distance) {
  if (distance < 1000) {
    return Math.round(distance) + ' 米';
  }
  return (distance / 1000).toFixed(1) + ' 公里';
}

function formatTime(seconds) {
  if (seconds < 60) {
    return Math.round(seconds) + ' 秒';
  }
  return Math.round(seconds / 60) + ' 分钟';
}

// 使用
planWalking([116.379028, 39.865042], [116.385281, 39.870719]);
```

### 骑行 (Riding)

```javascript
const riding = new AMap.Riding({
    map: map
});

riding.search([116.399028, 39.845042], [116.436281, 39.880719]);
```
## 完整示例

```javascript
const map = new AMap.Map('container', {
  zoom: 13,
  center: [116.397, 39.909]
});

const riding = new AMap.Riding();

function planRiding(start, end) {
  riding.search(start, end, function(status, result) {
    if (status === 'complete') {
      const route = result.routes[0];
      
      // 提取路径点
      const path = [];
      route.rides.forEach(ride => {
        path.push(...ride.path);
      });
      
      // 绘制路线（橙色，表示骑行）
      const polyline = new AMap.Polyline({
        path: path,
        strokeColor: '#fa8c16',
        strokeWeight: 5,
        strokeOpacity: 0.9,
        lineJoin: 'round',
        lineCap: 'round'
      });
      map.add(polyline);
      
      // 添加起点终点标记
      addStartEndMarkers(start, end);
      
      // 显示信息
      showRouteInfo(route);
      
      // 调整视野
      map.setFitView();
    } else {
      alert('骑行规划失败');
    }
  });
}

function addStartEndMarkers(start, end) {
  // 起点
  new AMap.Marker({
    map: map,
    position: start,
    content: createBikeMarker('起', '#52c41a'),
    offset: new AMap.Pixel(-16, -40)
  });
  
  // 终点
  new AMap.Marker({
    map: map,
    position: end,
    content: createBikeMarker('终', '#fa541c'),
    offset: new AMap.Pixel(-16, -40)
  });
}

function createBikeMarker(text, color) {
  return `
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="40" viewBox="0 0 32 40">
      <path d="M16 0C7.163 0 0 7.163 0 16c0 12 16 24 16 24s16-12 16-24C32 7.163 24.837 0 16 0z" fill="${color}"/>
      <circle cx="16" cy="14" r="6" fill="#fff"/>
      <text x="16" y="18" text-anchor="middle" fill="${color}" font-size="10" font-weight="bold">${text}</text>
    </svg>
  `;
}

function showRouteInfo(route) {
  const distance = formatDistance(route.distance);
  const time = formatTime(route.time);
  
  // 估算消耗卡路里（约 30 卡/公里）
  const calories = Math.round(route.distance / 1000 * 30);
  
  console.log(`
    骑行距离: ${distance}
    预计时间: ${time}
    预计消耗: ${calories} 卡路里
  `);
}

function formatDistance(distance) {
  if (distance < 1000) {
    return Math.round(distance) + ' 米';
  }
  return (distance / 1000).toFixed(1) + ' 公里';
}

function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.round((seconds % 3600) / 60);
  if (hours > 0) {
    return `${hours} 小时 ${minutes} 分钟`;
  }
  return `${minutes} 分钟`;
}

// 使用
planRiding([116.379028, 39.865042], [116.420281, 39.890719]);
```

## 自定义路线样式

```javascript
// 橙色渐变效果（骑行风格）
const colors = ['#fa8c16', '#ffa940', '#ffc069'];

riding.search(start, end, function(status, result) {
  if (status === 'complete') {
    const route = result.routes[0];
    const path = [];
    
    route.rides.forEach(ride => {
      path.push(...ride.path);
    });
    
    // 底层阴影
    const shadowLine = new AMap.Polyline({
      path: path,
      strokeColor: '#d46b08',
      strokeWeight: 8,
      strokeOpacity: 0.4
    });
    
    // 主路线
    const mainLine = new AMap.Polyline({
      path: path,
      strokeColor: '#fa8c16',
      strokeWeight: 5,
      strokeOpacity: 0.9,
      lineJoin: 'round',
      lineCap: 'round'
    });
    
    map.add([shadowLine, mainLine]);
  }
});
```

## 电动车模式

```javascript
const riding = new AMap.Riding({
  policy: 1 // 1 表示电动车
});

riding.search(start, end, function(status, result) {
  // 电动车路线规划
});
```

## 清除路线

```javascript
riding.clear();
```

## 注意事项

1. **路径特点**: 骑行路线会优先选择非机动车道、自行车道
2. **速度估算**: 默认按照 15km/h（普通自行车）或 20km/h（电动车）估算
3. **距离限制**: 骑行规划适合中短距离，过长距离可能无结果
4. **颜色区分**: 建议使用橙色与驾车（蓝色）、步行（绿色）路线区分
5. **上下坡**: 骑行路线会尽量避免陡坡路段

### 公交 (Transfer)

```javascript
const transfer = new AMap.Transfer({
    map: map,
    city: '北京市',
    policy: AMap.TransferPolicy.LEAST_TIME // 最快捷模式
});

transfer.search([116.291, 39.887], [116.436, 39.880], function(status, result) {});
```
## 完整示例

```javascript
const map = new AMap.Map('container', {
  zoom: 12,
  center: [116.397, 39.909]
});

const transfer = new AMap.Transfer({
  city: '北京市',
  policy: AMap.TransferPolicy.LEAST_TIME
});

function planTransit(start, end) {
  transfer.search(start, end, function(status, result) {
    if (status === 'complete' && result.plans && result.plans.length > 0) {
      const plan = result.plans[0]; // 取第一个方案
      
      // 遍历每个段落
      plan.segments.forEach((segment, index) => {
        // 乘车段
        if (segment.transit && segment.transit.path) {
          const polyline = new AMap.Polyline({
            path: segment.transit.path,
            strokeColor: '#1890ff',
            strokeWeight: 6,
            strokeOpacity: 0.9
          });
          map.add(polyline);
          
          // 添加上下车站标记
          addStationMarker(segment.transit.on_station, '上');
          addStationMarker(segment.transit.off_station, '下');
        }
        
        // 步行段
        if (segment.walking && segment.walking.path) {
          const polyline = new AMap.Polyline({
            path: segment.walking.path,
            strokeColor: '#52c41a',
            strokeWeight: 4,
            strokeOpacity: 0.8,
            strokeStyle: 'dashed'
          });
          map.add(polyline);
        }
      });
      
      // 显示方案信息
      showPlanInfo(plan);
      
      // 调整视野
      map.setFitView();
    } else {
      alert('公交规划失败');
    }
  });
}

function addStationMarker(station, type) {
  if (!station) return;
  
  new AMap.Marker({
    map: map,
    position: station.location,
    content: `<div style="
      background: ${type === '上' ? '#1890ff' : '#fa541c'};
      color: #fff;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 12px;
    ">${type} ${station.name}</div>`,
    offset: new AMap.Pixel(-20, -10)
  });
}

function showPlanInfo(plan) {
  const distance = formatDistance(plan.distance);
  const time = formatTime(plan.time);
  const cost = plan.cost ? plan.cost + ' 元' : '未知';
  const walkDistance = formatDistance(plan.walking_distance);
  
  console.log(`
    总距离: ${distance}
    预计时间: ${time}
    票价: ${cost}
    步行距离: ${walkDistance}
  `);
  
  // 显示换乘详情
  plan.segments.forEach((segment, index) => {
    if (segment.transit) {
      const t = segment.transit;
      console.log(`第${index + 1}段: ${t.name} (${t.on_station.name} → ${t.off_station.name})`);
    }
  });
}

function formatDistance(distance) {
  if (distance < 1000) {
    return Math.round(distance) + ' 米';
  }
  return (distance / 1000).toFixed(1) + ' 公里';
}

function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.round((seconds % 3600) / 60);
  if (hours > 0) {
    return `${hours} 小时 ${minutes} 分钟`;
  }
  return `${minutes} 分钟`;
}

// 使用
planTransit([116.379028, 39.865042], [116.527281, 39.950719]);
```

## 显示多个方案

```javascript
transfer.search(start, end, function(status, result) {
  if (status === 'complete' && result.plans) {
    // 显示所有方案供用户选择
    result.plans.forEach((plan, index) => {
      const info = {
        index: index + 1,
        time: formatTime(plan.time),
        cost: plan.cost + ' 元',
        transfers: plan.segments.filter(s => s.transit).length - 1 // 换乘次数
      };
      console.log(`方案${info.index}: ${info.time}, ${info.cost}, 换乘${info.transfers}次`);
    });
  }
});
```

## 清除路线

```javascript
transfer.clear();
```

## 注意事项

1. **城市参数必填**: Transfer 必须指定城市参数
2. **跨城市**: 不支持跨城市公交规划
3. **换乘策略**: 不同策略会返回不同的方案
4. **夜班车**: 设置 `nightflag: true` 计算夜班车路线
5. **多方案**: 通常会返回多个方案，可供用户选择
6. **路径绘制**: 需要分别处理乘车段和步行段


## 3. 拖拽导航

开启 `showTraffic` 可显示实时路况，部分插件支持拖拽修改路径。

```javascript
const driving = new AMap.Driving({
    map: map,
    showTraffic: true, // 显示路况
});
```
