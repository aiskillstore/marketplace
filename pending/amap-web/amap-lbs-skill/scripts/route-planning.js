#!/usr/bin/env node

/**
 * 路径规划脚本
 * 使用方法:
 * node scripts/route-planning.js --type=walking --origin=116.397428,39.90923 --destination=116.427281,39.903719
 */

const { walkingRoute, drivingRoute, ridingRoute, transitRoute, generateMapLink } = require('../index');

// 解析命令行参数
function parseArgs() {
  const args = {};
  process.argv.slice(2).forEach(arg => {
    if (arg.startsWith('--')) {
      const [key, value] = arg.slice(2).split('=');
      args[key] = value;
    }
  });
  return args;
}

// 主函数
async function main() {
  const args = parseArgs();
  
  // 检查必需参数
  if (!args.type || !args.origin || !args.destination) {
    console.error('❌ 缺少必需参数');
    console.log('\n使用方法:');
    console.log('node scripts/route-planning.js --type=路线类型 --origin=起点坐标 --destination=终点坐标 [其他参数]');
    console.log('\n路线类型:');
    console.log('  walking  - 步行');
    console.log('  driving  - 驾车');
    console.log('  riding   - 骑行');
    console.log('  transfer - 公交（需要额外提供 --city 参数）');
    console.log('\n示例:');
    console.log('# 步行路线');
    console.log('node scripts/route-planning.js --type=walking --origin=116.397428,39.90923 --destination=116.427281,39.903719');
    console.log('\n# 驾车路线（带途经点）');
    console.log('node scripts/route-planning.js --type=driving --origin=116.397428,39.90923 --destination=116.427281,39.903719 --waypoints=116.410000,39.910000');
    console.log('\n# 公交路线');
    console.log('node scripts/route-planning.js --type=transfer --origin=116.397428,39.90923 --destination=116.427281,39.903719 --city=北京');
    process.exit(1);
  }
  
  const { type, origin, destination } = args;
  
  try {
    let result = null;
    let mapTaskData = [];
    
    // 解析起点和终点坐标
    const [originLng, originLat] = origin.split(',').map(Number);
    const [destLng, destLat] = destination.split(',').map(Number);
    
    // 根据类型调用不同的路径规划API
    switch (type) {
      case 'walking':
        result = await walkingRoute({ origin, destination });
        if (result && result.route) {
          mapTaskData.push({
            type: 'route',
            routeType: 'walking',
            start: [originLng, originLat],
            end: [destLng, destLat],
            remark: `步行路线，距离约 ${(result.route.paths[0].distance / 1000).toFixed(2)} 公里`
          });
          
          console.log('📊 路线信息:');
          console.log(`   距离: ${(result.route.paths[0].distance / 1000).toFixed(2)} 公里`);
          console.log(`   预计时间: ${Math.round(result.route.paths[0].duration / 60)} 分钟\n`);
        }
        break;
        
      case 'driving':
        const drivingParams = { origin, destination };
        if (args.waypoints) {
          drivingParams.waypoints = args.waypoints;
        }
        if (args.strategy) {
          drivingParams.strategy = parseInt(args.strategy);
        }
        
        result = await drivingRoute(drivingParams);
        if (result && result.route) {
          const path = result.route.paths[0];
          mapTaskData.push({
            type: 'route',
            routeType: 'driving',
            start: [originLng, originLat],
            end: [destLng, destLat],
            remark: `驾车路线，距离约 ${(path.distance / 1000).toFixed(2)} 公里`
          });
          
          console.log('📊 路线信息:');
          console.log(`   距离: ${(path.distance / 1000).toFixed(2)} 公里`);
          console.log(`   预计时间: ${Math.round(path.duration / 60)} 分钟`);
          console.log(`   过路费: ${path.tolls || 0} 元`);
          console.log(`   红绿灯: ${path.traffic_lights || 0} 个\n`);
        }
        break;
        
      case 'riding':
        result = await ridingRoute({ origin, destination });
        if (result && result.data) {
          const path = result.data.paths[0];
          mapTaskData.push({
            type: 'route',
            routeType: 'riding',
            start: [originLng, originLat],
            end: [destLng, destLat],
            remark: `骑行路线，距离约 ${(path.distance / 1000).toFixed(2)} 公里`
          });
          
          console.log('📊 路线信息:');
          console.log(`   距离: ${(path.distance / 1000).toFixed(2)} 公里`);
          console.log(`   预计时间: ${Math.round(path.duration / 60)} 分钟\n`);
        }
        break;
        
      case 'transfer':
        if (!args.city) {
          console.error('❌ 公交路线规划需要提供 --city 参数');
          process.exit(1);
        }
        
        const transitParams = {
          origin,
          destination,
          city: args.city,
          strategy: args.strategy ? parseInt(args.strategy) : 0,
          nightflag: args.nightflag === 'true'
        };
        
        result = await transitRoute(transitParams);
        if (result && result.route) {
          mapTaskData.push({
            type: 'route',
            routeType: 'transfer',
            start: [originLng, originLat],
            end: [destLng, destLat],
            city: args.city,
            remark: `公交路线，共 ${result.route.transits.length} 个方案`
          });
          
          console.log('📊 路线信息:');
          console.log(`   方案数量: ${result.route.transits.length} 个`);
          if (result.route.transits.length > 0) {
            const transit = result.route.transits[0];
            console.log(`   预计时间: ${Math.round(transit.duration / 60)} 分钟`);
            console.log(`   费用: ${transit.cost} 元`);
            console.log(`   步行距离: ${transit.walking_distance} 米\n`);
          }
        }
        break;
        
      default:
        console.error(`❌ 不支持的路线类型: ${type}`);
        process.exit(1);
    }
    
    if (result && mapTaskData.length > 0) {
      // 生成地图链接
      const mapLink = generateMapLink(mapTaskData);
      console.log('🗺️  地图可视化链接:');
      console.log(mapLink);
      console.log('\n💡 提示: 复制链接到浏览器打开即可查看路线详情\n');
    } else {
      console.log('\n❌ 路线规划失败，请检查参数是否正确');
    }
  } catch (error) {
    console.error('\n❌ 执行失败:', error.message);
    process.exit(1);
  }
}

// 执行主函数
main();
