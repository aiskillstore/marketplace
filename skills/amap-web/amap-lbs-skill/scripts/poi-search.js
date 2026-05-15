#!/usr/bin/env node

/**
 * POI 搜索脚本
 * 使用方法:
 * node scripts/poi-search.js --keywords=肯德基 --city=北京
 * 或设置环境变量: AMAP_KEY=your_key node scripts/poi-search.js --keywords=肯德基
 */

const { searchPOI } = require('../index');

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
  if (!args.keywords) {
    console.error('❌ 缺少必需参数: --keywords');
    console.log('\n使用方法:');
    console.log('node scripts/poi-search.js --keywords=关键词 [--city=城市] [--types=类型] [--page=页码] [--offset=每页数量]');
    console.log('\n示例:');
    console.log('node scripts/poi-search.js --keywords=肯德基 --city=北京 --page=1 --offset=20');
    process.exit(1);
  }
  
  // 检查是否设置了 AMAP_KEY
  if (!process.env.AMAP_KEY) {
    console.error('❌ 请设置环境变量 AMAP_KEY');
    console.log('\n示例:');
    console.log('export AMAP_KEY=your_amap_key');
    console.log('node scripts/poi-search.js --keywords=美食 --location=116.397428,39.90923 --radius=1000');
    process.exit(1);
  }
  
  // 构建搜索参数
  const params = {
    keywords: args.keywords,
    city: args.city || '',
    types: args.types || '',
    page: parseInt(args.page) || 1,
    offset: parseInt(args.offset) || 10
  };
  
  // 可选参数
  if (args.location) params.location = args.location;
  if (args.radius) params.radius = parseInt(args.radius);
  if (args.cityLimit !== undefined) params.cityLimit = args.cityLimit === 'true';
  
  try {
    const result = await searchPOI(params);
    
    if (result && result.pois && result.pois.length > 0) {
      console.log(`\n📍 共找到 ${result.count} 条结果，当前显示第 ${params.page} 页:\n`);
      console.log('='.repeat(80));
      
      result.pois.forEach((poi, index) => {
        const num = (params.page - 1) * params.offset + index + 1;
        console.log(`\n${num}. ${poi.name}`);
        console.log(`   📍 地址: ${poi.address || '无'}`);
        console.log(`   🏷️  类型: ${poi.type}`);
        console.log(`   📞 电话: ${poi.tel || '无'}`);
        console.log(`   🗺️  坐标: ${poi.location}`);
        if (poi.distance) {
          console.log(`   📏 距离: ${poi.distance}米`);
        }
      });
      
      console.log('\n' + '='.repeat(80));
      
      // 输出分页信息
      const totalPages = Math.ceil(result.count / params.offset);
      console.log(`\n第 ${params.page}/${totalPages} 页`);
      
      if (params.page < totalPages) {
        console.log(`\n💡 查看下一页: node scripts/poi-search.js --keywords=${params.keywords} --city=${params.city} --page=${params.page + 1}`);
      }
    } else {
      console.log('\n❌ 未找到相关结果');
    }
  } catch (error) {
    console.error('\n❌ 执行失败:', error.message);
    process.exit(1);
  }
}

// 执行主函数
main();
