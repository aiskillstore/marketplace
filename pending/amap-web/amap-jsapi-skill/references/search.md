# 搜索服务 (Search)

搜索服务主要包含 POI 搜索 (`PlaceSearch`) 和 输入提示 (`AutoComplete`)。

## 1. 输入提示 (AutoComplete)

根据输入关键字提示匹配信息，通常与搜索组合使用。

```javascript
const autoOptions = {
    city: '北京', // 限制城市
    input: 'tipinput' // 绑定输入框的 ID，自动监听输入
};

const autoComplete = new AMap.AutoComplete(autoOptions);

// 监听选中事件
autoComplete.on('select', function(e) {
    console.log('选中：', e.poi.name);
    // 选中后通常调用 PlaceSearch 进行详细搜索
    placeSearch.search(e.poi.name);
});
```

## 2. POI 搜索 (PlaceSearch)

查询兴趣点（POI）信息，如餐厅、酒店、景点等。

### 基础配置

```javascript
const placeSearch = new AMap.PlaceSearch({
    map: map, // 结果自动展示在地图上
    panel: 'panel', // 结果列表容器
    pageSize: 5, // 每页结果数
    pageIndex: 1, // 当前页码
    city: '010', // 兴趣点城市
    citylimit: true, // 是否强制限制在设置的城市内
});
```

### 搜索方式

#### 关键字搜索

```javascript
placeSearch.search('北京大学', function(status, result) {
    // result.poiList.pois 包含 POI 数组
});
```

#### 周边搜索 (NearBy)

查询中心点周边的 POI。

```javascript
const center = [116.405467, 39.907761];
const radius = 500; // 半径 (米)
const type = '餐饮服务'; // POI 类型

placeSearch.searchNearBy(type, center, radius, function(status, result) {
    // ...
});
```

#### 多边形内搜索 (InBounds)

查询矩形或多边形范围内的 POI。

```javascript
const polygon = new AMap.Polygon({
    path: [[116.39, 39.91], [116.41, 39.91], [116.41, 39.93], [116.39, 39.93]]
});

placeSearch.searchInBounds('酒店', polygon, function(status, result) {
    // ...
});
```
## POI 类型编码

常用类型编码示例：

| 编码 | 类型 |
| :--- | :--- |
| 050000 | 餐饮服务 |
| 060000 | 购物服务 |
| 070000 | 生活服务 |
| 080000 | 体育休闲服务 |
| 090000 | 医疗保健服务 |
| 100000 | 住宿服务 |
| 110000 | 风景名胜 |
| 120000 | 商务住宅 |
| 130000 | 政府机构及社会团体 |
| 140000 | 科教文化服务 |
| 150000 | 交通设施服务 |
| 160000 | 金融保险服务 |

## 注意事项

1. **城市设置**: 不设置 city 时默认全国搜索
2. **结果数量**: pageSize 最大为 50
3. **详细信息**: 需要电话、网址等信息时设置 `extensions: 'all'`
4. **距离字段**: 只有周边搜索时才有 distance 字段
5. **自动渲染**: 设置 map 和 panel 后会自动渲染结果，无需手动处理
