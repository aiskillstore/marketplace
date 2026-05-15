# 高德地图综合服务 Skill

高德地图综合服务向开发者提供完整的地图数据服务，包括地点搜索、路径规划、旅游规划和数据可视化等功能。

## 功能特性

- ✅ 自动管理高德 Web Service Key
- ✅ POI 搜索功能
- ✅ 路径规划（步行、驾车、骑行、公交）
- ✅ 智能旅游规划助手
- ✅ 地图可视化链接生成
- ✅ 热力图数据可视化
- ✅ 支持命令行脚本执行
- ✅ 配置本地持久化

## 安装依赖

```bash
npm install
```

## 配置 API Key

首次使用需要配置高德 Web Service Key：

```bash
# 方式1: 运行时通过环境变量
export AMAP_WEBSERVICE_KEY=your_key
node scripts/poi-search.js --keywords=肯德基 --city=北京

# 方式2: 运行时自动提示输入（会保存到 config.json）
node scripts/poi-search.js --keywords=肯德基 --city=北京

# 方式3: 手动创建配置文件
cp config.example.json config.json
# 然后编辑 config.json 填入你的 Key
```

获取 API Key：访问 [高德开放平台](https://lbs.amap.com/api/webservice/create-project-and-key) 创建应用并获取 Key

## 使用方法

### 1. POI 搜索

```bash
# 基础搜索
node scripts/poi-search.js --keywords=肯德基 --city=北京

# 带更多参数的搜索
node scripts/poi-search.js --keywords=餐厅 --city=上海 --page=1 --offset=20

# 周边搜索（需要提供中心点坐标和半径）
node scripts/poi-search.js --keywords=酒店 --location=116.397428,39.90923 --radius=1000
```

### 2. 路径规划

```bash
# 步行路线
node scripts/route-planning.js --type=walking --origin=116.397428,39.90923 --destination=116.427281,39.903719

# 驾车路线（带途经点）
node scripts/route-planning.js --type=driving --origin=116.397428,39.90923 --destination=116.427281,39.903719 --waypoints=116.410000,39.910000

# 骑行路线
node scripts/route-planning.js --type=riding --origin=116.397428,39.90923 --destination=116.427281,39.903719

# 公交路线
node scripts/route-planning.js --type=transfer --origin=116.397428,39.90923 --destination=116.427281,39.903719 --city=北京
```

### 3. 智能旅游规划

```bash
# 基础旅游规划
node scripts/travel-planner.js --city=北京 --interests=景点,美食,酒店

# 指定路线类型
node scripts/travel-planner.js --city=杭州 --interests=西湖,美食,茶馆 --routeType=walking

# 驾车游览
node scripts/travel-planner.js --city=上海 --interests=外滩,南京路,城隍庙 --routeType=driving
```

### 4. 在代码中使用

```javascript
const { 
  searchPOI, 
  walkingRoute, 
  drivingRoute, 
  travelPlanner,
  generateMapLink 
} = require('./index');

// POI 搜索
async function searchExample() {
  const result = await searchPOI({
    keywords: '肯德基',
    city: '北京',
    page: 1,
    offset: 10
  });
  console.log(result);
}

// 步行路线规划
async function routeExample() {
  const result = await walkingRoute({
    origin: '116.397428,39.90923',
    destination: '116.427281,39.903719'
  });
  console.log(result);
}

// 旅游规划
async function travelExample() {
  const result = await travelPlanner({
    city: '北京',
    interests: ['景点', '美食', '酒店'],
    routeType: 'walking'
  });
  console.log(result.mapLink); // 地图可视化链接
}

// 生成地图链接
function mapLinkExample() {
  const mapData = [
    { 
      type: 'poi', 
      lnglat: [116.397428, 39.90923], 
      sort: '风景名胜', 
      text: '故宫博物院', 
      remark: '明清两代的皇家宫殿' 
    },
    {
      type: 'route',
      routeType: 'walking',
      start: [116.397428, 39.90923],
      end: [116.427281, 39.903719],
      remark: '步行路线'
    }
  ];
  
  const link = generateMapLink(mapData);
  console.log(link);
}
```

## API 参数说明

### POI 搜索参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keywords | string | 是 | 查询关键字 |
| city | string | 否 | 城市名称或城市编码 |
| types | string | 否 | POI类型编码，多个用\|分隔 |
| location | string | 否 | 中心点坐标（经度,纬度） |
| radius | number | 否 | 搜索半径，单位：米 |
| page | number | 否 | 当前页数，默认1 |
| offset | number | 否 | 每页记录数，默认10，最大25 |

### 路径规划参数

#### 步行路线 (walkingRoute)
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| origin | string | 是 | 起点坐标 "经度,纬度" |
| destination | string | 是 | 终点坐标 "经度,纬度" |

#### 驾车路线 (drivingRoute)
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| origin | string | 是 | 起点坐标 "经度,纬度" |
| destination | string | 是 | 终点坐标 "经度,纬度" |
| waypoints | string | 否 | 途经点，多个用;分隔，最多16个 |
| strategy | number | 否 | 驾车策略，默认10（躲避拥堵） |

#### 骑行路线 (ridingRoute)
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| origin | string | 是 | 起点坐标 "经度,纬度" |
| destination | string | 是 | 终点坐标 "经度,纬度" |

#### 公交路线 (transitRoute)
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| origin | string | 是 | 起点坐标 "经度,纬度" |
| destination | string | 是 | 终点坐标 "经度,纬度" |
| city | string | 是 | 城市名称或城市编码 |
| strategy | number | 否 | 公交策略，0-5，默认0（最快捷） |
| nightflag | boolean | 否 | 是否计算夜班车，默认false |

### 旅游规划参数 (travelPlanner)
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| city | string | 是 | 城市名称 |
| interests | array | 否 | 兴趣点关键词数组，默认['景点','美食'] |
| routeType | string | 否 | 路线类型：walking/driving/riding/transfer，默认walking |

## 项目结构

```
jsapi-skills/
├── index.js                    # 主入口文件，包含核心功能
├── scripts/
│   ├── poi-search.js           # POI 搜索脚本
│   ├── route-planning.js       # 路径规划脚本
│   └── travel-planner.js       # 智能旅游规划脚本
├── config.json                 # 配置文件（自动生成，不要提交）
├── config.example.json         # 配置示例
├── package.json                # 依赖配置
├── .gitignore                  # Git 忽略配置
├── SKILL.md                    # OpenClaw Skill 描述文件
└── README.md                   # 本文件
```

## 地图可视化

所有规划结果都会生成地图可视化链接，格式如下：

```
https://a.amap.com/jsapi_demo_show/static/openclaw/travel_plan.html?data=<encoded_json_data>
```

数据格式符合 MapTaskData 接口规范，支持：
- **POI 任务**：展示兴趣点位置和信息
- **路线任务**：展示路径规划结果

示例数据结构：
```javascript
[
  // POI 兴趣点
  { 
    type: 'poi', 
    lnglat: [116.397428, 39.90923], 
    sort: '风景名胜', 
    text: '故宫博物院', 
    remark: '明清两代的皇家宫殿，旧称紫禁城。' 
  },
  // 路线规划
  {
    type: 'route',
    routeType: 'walking',
    start: [116.397428, 39.90923],
    end: [116.427281, 39.903719],
    remark: '步行路线'
  }
]
```

## 注意事项

1. 请妥善保管你的 Web Service Key，不要提交到公开仓库
2. `config.json` 已在 `.gitignore` 中，不会被提交
3. 高德 Web 服务 API 有调用频率限制，请合理使用
4. 免费用户每日调用量有限制，具体请查看高德开放平台说明

## 相关链接

- [高德开放平台](https://lbs.amap.com/)
- [创建应用和获取 Key](https://lbs.amap.com/api/webservice/create-project-and-key)
- [POI 搜索 API 文档](https://lbs.amap.com/api/webservice/guide/api-advanced/newpoisearch)
- [Web 服务 API 总览](https://lbs.amap.com/api/webservice/summary)

## License

MIT
