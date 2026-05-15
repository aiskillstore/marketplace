#!/usr/bin/env node

/**
 * 旅游规划脚本
 * 使用方法:
 * node scripts/travel-planner.js --city=北京 --interests=景点,美食,酒店 --routeType=walking
 */

const { travelPlanner } = require('../index');

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
  if (!args.city) {
    console.error('❌ 缺少必需参数: --city');
    console.log('\n使用方法:');
    console.log('node scripts/travel-planner.js --city=城市名 [--interests=兴趣点1,兴趣点2] [--routeType=路线类型]');
    console.log('\n示例:');
    console.log('node scripts/travel-planner.js --city=北京 --interests=景点,美食,酒店 --routeType=walking');
    console.log('\n路线类型选项:');
    console.log('  walking  - 步行（默认）');
    console.log('  driving  - 驾车');
    console.log('  riding   - 骑行');
    console.log('  transfer - 公交');
    process.exit(1);
  }
  
  // 解析兴趣点
  const interests = args.interests ? args.interests.split(',') : ['景点', '美食'];
  const routeType = args.routeType || 'walking';
  
  // 验证路线类型
  const validRouteTypes = ['walking', 'driving', 'riding', 'transfer'];
  if (!validRouteTypes.includes(routeType)) {
    console.error(`❌ 无效的路线类型: ${routeType}`);
    console.log('有效的路线类型:', validRouteTypes.join(', '));
    process.exit(1);
  }
  
  try {
    const result = await travelPlanner({
      city: args.city,
      interests: interests,
      routeType: routeType
    });
    
    if (result && result.pois.length > 0) {
      console.log('═'.repeat(80));
      console.log('\n📊 规划数据统计：');
      console.log(`   兴趣点数量: ${result.pois.length} 个`);
      console.log(`   路线数量: ${result.mapTaskData.filter(item => item.type === 'route').length} 条`);
      console.log(`   出行方式: ${routeType === 'walking' ? '步行' : routeType === 'driving' ? '驾车' : routeType === 'riding' ? '骑行' : '公交'}`);
      console.log('\n' + '═'.repeat(80));
      console.log('\n🎉 规划完成！\n');
      console.log('📋 数据格式符合 MapTaskData 接口规范');
      console.log('   - PoiTask: 兴趣点任务');
      console.log('   - RouteTask: 路线规划任务\n');
    } else {
      console.log('\n❌ 未找到相关地点，请尝试更换关键词或城市。');
    }
  } catch (error) {
    console.error('\n❌ 执行失败:', error.message);
    process.exit(1);
  }
}

// 执行主函数
main();
