const fs = require('fs');
const path = require('path');
const axios = require('axios');

// 配置文件路径
const CONFIG_FILE = path.join(__dirname, 'config.json');

/**
 * 读取配置文件
 */
function readConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      const data = fs.readFileSync(CONFIG_FILE, 'utf8');
      return JSON.parse(data);
    }
  } catch (error) {
    console.error('读取配置文件失败:', error.message);
  }
  return {};
}

/**
 * 保存配置文件
 */
function saveConfig(config) {
  try {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf8');
    console.log('配置已保存到:', CONFIG_FILE);
    return true;
  } catch (error) {
    console.error('保存配置文件失败:', error.message);
    return false;
  }
}

/**
 * 获取高德 Web Service Key
 */
function getWebServiceKey() {
  const config = readConfig();
  return config.webServiceKey || null;
}

/**
 * 设置高德 Web Service Key
 */
function setWebServiceKey(key) {
  const config = readConfig();
  config.webServiceKey = key;
  return saveConfig(config);
}

/**
 * 检查并提示用户输入 Key
 */
async function ensureWebServiceKey() {
  // 优先从环境变量读取
  let key = process.env.AMAP_KEY || process.env.AMAP_WEBSERVICE_KEY;
  
  if (!key) {
    // 尝试从配置文件读取
    key = getWebServiceKey();
  }
  
  if (!key) {
    console.log('\n⚠️  未找到高德 Web Service Key');
    console.log('请访问以下地址创建应用并获取 Key:');
    console.log('https://lbs.amap.com/api/webservice/create-project-and-key\n');
    throw new Error('请设置环境变量 AMAP_KEY 或提供高德 Web Service Key');
  }
  
  return key;
}

/**
 * POI 搜索
 * @param {Object} params - 搜索参数
 * @param {string} params.keywords - 查询关键字
 * @param {string} params.city - 城市名称或城市编码
 * @param {string} params.types - POI类型编码
 * @param {string} params.location - 中心点坐标
 * @param {number} params.radius - 搜索半径(米)
 * @param {number} params.page - 当前页数
 * @param {number} params.offset - 每页记录数
 */
async function searchPOI(params) {
  const key = await ensureWebServiceKey();
  
  const url = 'https://restapi.amap.com/v5/place/text';
  
  const requestParams = {
    key: key,
    keywords: params.keywords || '',
    region: params.city || '',
    city_limit: params.cityLimit !== false,
    ...params,
    appname: 'amap-lbs-skill',
  };
  
  try {
    console.log('🔍 正在搜索 POI...');
    const response = await axios.get(url, { params: requestParams });
    
    if (response.data.status === '1') {
      console.log(`✅ 搜索成功，共找到 ${response.data.count} 条结果\n`);
      return response.data;
    } else {
      console.error('❌ 搜索失败:', response.data.info);
      return null;
    }
  } catch (error) {
    console.error('❌ 请求失败:', error.message);
    return null;
  }
}

/**
 * 步行路径规划
 * @param {Object} params - 规划参数
 * @param {string} params.origin - 起点坐标 "经度,纬度"
 * @param {string} params.destination - 终点坐标 "经度,纬度"
 */
async function walkingRoute(params) {
  const key = await ensureWebServiceKey();
  
  const url = 'https://restapi.amap.com/v3/direction/walking';
  
  const requestParams = {
    key: key,
    origin: params.origin,
    destination: params.destination,
    appname: 'amap-lbs-skill',
  };
  
  try {
    console.log('🚶 正在规划步行路线...');
    const response = await axios.get(url, { params: requestParams });
    
    if (response.data.status === '1') {
      console.log('✅ 步行路线规划成功\n');
      return response.data;
    } else {
      console.error('❌ 步行路线规划失败:', response.data.info);
      return null;
    }
  } catch (error) {
    console.error('❌ 请求失败:', error.message);
    return null;
  }
}

/**
 * 驾车路径规划
 * @param {Object} params - 规划参数
 * @param {string} params.origin - 起点坐标 "经度,纬度"
 * @param {string} params.destination - 终点坐标 "经度,纬度"
 * @param {string} params.waypoints - 途经点坐标，多个用;分隔
 * @param {number} params.strategy - 驾车策略，默认10
 */
async function drivingRoute(params) {
  const key = await ensureWebServiceKey();
  
  const url = 'https://restapi.amap.com/v3/direction/driving';
  
  const requestParams = {
    key: key,
    origin: params.origin,
    destination: params.destination,
    strategy: params.strategy || 10,
    extensions: 'base',
    appname: 'amap-lbs-skill',
  };
  
  if (params.waypoints) {
    requestParams.waypoints = params.waypoints;
  }
  
  try {
    console.log('🚗 正在规划驾车路线...');
    const response = await axios.get(url, { params: requestParams });
    
    if (response.data.status === '1') {
      console.log('✅ 驾车路线规划成功\n');
      return response.data;
    } else {
      console.error('❌ 驾车路线规划失败:', response.data.info);
      return null;
    }
  } catch (error) {
    console.error('❌ 请求失败:', error.message);
    return null;
  }
}

/**
 * 骑行路径规划
 * @param {Object} params - 规划参数
 * @param {string} params.origin - 起点坐标 "经度,纬度"
 * @param {string} params.destination - 终点坐标 "经度,纬度"
 */
async function ridingRoute(params) {
  const key = await ensureWebServiceKey();
  
  const url = 'https://restapi.amap.com/v4/direction/bicycling';
  
  const requestParams = {
    key: key,
    origin: params.origin,
    destination: params.destination,
    appname: 'amap-lbs-skill',
  };
  
  try {
    console.log('🚴 正在规划骑行路线...');
    const response = await axios.get(url, { params: requestParams });
    
    if (response.data.errcode === 0) {
      console.log('✅ 骑行路线规划成功\n');
      return response.data;
    } else {
      console.error('❌ 骑行路线规划失败:', response.data.errmsg);
      return null;
    }
  } catch (error) {
    console.error('❌ 请求失败:', error.message);
    return null;
  }
}

/**
 * 公交路径规划
 * @param {Object} params - 规划参数
 * @param {string} params.origin - 起点坐标 "经度,纬度"
 * @param {string} params.destination - 终点坐标 "经度,纬度"
 * @param {string} params.city - 城市名称或城市编码
 * @param {number} params.strategy - 公交策略，默认0（最快捷）
 * @param {boolean} params.nightflag - 是否计算夜班车，默认false
 */
async function transitRoute(params) {
  const key = await ensureWebServiceKey();
  
  const url = 'https://restapi.amap.com/v3/direction/transit/integrated';
  
  const requestParams = {
    key: key,
    origin: params.origin,
    destination: params.destination,
    city: params.city,
    strategy: params.strategy || 0,
    nightflag: params.nightflag ? 1 : 0,
    appname: 'amap-lbs-skill',
  };
  
  try {
    console.log('🚌 正在规划公交路线...');
    const response = await axios.get(url, { params: requestParams });
    
    if (response.data.status === '1') {
      console.log('✅ 公交路线规划成功\n');
      return response.data;
    } else {
      console.error('❌ 公交路线规划失败:', response.data.info);
      return null;
    }
  } catch (error) {
    console.error('❌ 请求失败:', error.message);
    return null;
  }
}

/**
 * 生成地图可视化链接
 * @param {Array} mapTaskData - 地图任务数据数组
 * @returns {string} 可视化链接
 */
function generateMapLink(mapTaskData) {
  const baseUrl = 'https://a.amap.com/jsapi_demo_show/static/openclaw/travel_plan.html';
  const dataStr = encodeURIComponent(JSON.stringify(mapTaskData));
  return `${baseUrl}?data=${dataStr}`;
}

/**
 * 旅游规划助手
 * @param {Object} params - 规划参数
 * @param {string} params.city - 城市名称
 * @param {Array<string>} params.interests - 兴趣点关键词数组，如 ['景点', '美食', '酒店']
 * @param {string} params.routeType - 路线类型：driving/walking/riding/transfer
 * @returns {Object} 包含 pois、mapTaskData、mapLink 和 htmlLink
 */
async function travelPlanner(params) {
  const { city, interests = [], routeType = 'walking' } = params;
  
  console.log(`\n🗺️  开始为您规划 ${city} 的旅游行程...\n`);
  
  const mapTaskData = [];
  const poiResults = [];
  
  // 搜索各类兴趣点
  for (const interest of interests) {
    console.log(`📍 搜索 ${interest}...`);
    const result = await searchPOI({
      keywords: interest,
      city: city,
      page: 1,
      offset: 5
    });
    
    if (result && result.pois && result.pois.length > 0) {
      poiResults.push(...result.pois);
      
      // 添加到地图数据 - 严格按照 PoiTask 接口格式
      result.pois.forEach(poi => {
        const [lng, lat] = poi.location.split(',').map(Number);
        mapTaskData.push({
          type: 'poi',
          lnglat: [lng, lat],
          sort: poi.type || interest,
          text: poi.name,
          remark: poi.address || `${interest}推荐`
        });
      });
    }
  }
  
  // 如果有多个POI，规划路线
  if (poiResults.length >= 2) {
    console.log(`\n🛣️  规划游览路线（${routeType}）...\n`);
    
    for (let i = 0; i < poiResults.length - 1; i++) {
      const start = poiResults[i];
      const end = poiResults[i + 1];
      
      const [startLng, startLat] = start.location.split(',').map(Number);
      const [endLng, endLat] = end.location.split(',').map(Number);
      
      // 添加路线到地图数据 - 严格按照 RouteTask 接口格式
      const routeTask = {
        type: 'route',
        routeType: routeType,
        start: [startLng, startLat],
        end: [endLng, endLat],
        remark: `从 ${start.name} 到 ${end.name}`
      };
      
      // 如果是公交路线，添加 city 参数
      if (routeType === 'transfer') {
        routeTask.city = city;
      }
      
      mapTaskData.push(routeTask);
    }
  }
  
  
  console.log('\n✅ 旅游规划完成！\n');
  console.log('📍 推荐地点：');
  poiResults.forEach((poi, index) => {
    console.log(`${index + 1}. ${poi.name}`);
    console.log(`   地址: ${poi.address}`);
    console.log(`   类型: ${poi.type}\n`);
  });
  
  return {
    pois: poiResults,
  };
}

// 导出函数供其他脚本使用
module.exports = {
  readConfig,
  saveConfig,
  getWebServiceKey,
  setWebServiceKey,
  ensureWebServiceKey,
  searchPOI,
  walkingRoute,
  drivingRoute,
  ridingRoute,
  transitRoute,
  generateMapLink,
  travelPlanner
};

// 如果直接运行此文件，执行示例搜索
if (require.main === module) {
  (async () => {
    try {
      // 示例：搜索北京的肯德基
      const result = await searchPOI({
        keywords: '肯德基',
        city: '北京',
        page: 1,
        offset: 10
      });
      
      if (result && result.pois) {
        console.log('搜索结果:');
        result.pois.forEach((poi, index) => {
          console.log(`${index + 1}. ${poi.name}`);
          console.log(`   地址: ${poi.address}`);
          console.log(`   类型: ${poi.type}`);
          console.log(`   坐标: ${poi.location}\n`);
        });
      }
    } catch (error) {
      console.error('执行失败:', error.message);
      process.exit(1);
    }
  })();
}
