#!/usr/bin/env node
/**
 * images2pptx.js - 将图片文件夹打包成 PPT
 *
 * 用法: node images2pptx.js <图片目录> [输出文件名]
 * 示例: node images2pptx.js ./slides output.pptx
 */

const pptxgen = require('pptxgenjs');
const fs = require('fs');
const path = require('path');

// 参数解析
const args = process.argv.slice(2);
if (args.length < 1) {
  console.log('用法: node images2pptx.js <图片目录> [输出文件名]');
  console.log('示例: node images2pptx.js ./slides output.pptx');
  process.exit(1);
}

const inputDir = path.resolve(args[0]);
const outputFile = args[1] || 'output.pptx';
const outputPath = path.resolve(inputDir, outputFile);

// 检查目录
if (!fs.existsSync(inputDir)) {
  console.error(`错误: 目录不存在 - ${inputDir}`);
  process.exit(1);
}

// 获取图片文件
const imageExts = ['.jpg', '.jpeg', '.png', '.gif', '.webp'];
const images = fs.readdirSync(inputDir)
  .filter(f => imageExts.includes(path.extname(f).toLowerCase()))
  .sort((a, b) => {
    // 尝试按数字排序（支持 "第1页", "slide1", "1" 等格式）
    const numA = parseInt(a.match(/\d+/)?.[0] || '0');
    const numB = parseInt(b.match(/\d+/)?.[0] || '0');
    if (numA !== numB) return numA - numB;
    return a.localeCompare(b, 'zh-CN');
  });

if (images.length === 0) {
  console.error('错误: 目录中没有找到图片文件');
  process.exit(1);
}

console.log(`找到 ${images.length} 张图片:`);
images.forEach((img, i) => console.log(`  ${i + 1}. ${img}`));

// 创建 PPT
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_16x9';
pptx.title = path.basename(inputDir);

images.forEach((filename) => {
  const slide = pptx.addSlide();
  slide.addImage({
    path: path.join(inputDir, filename),
    x: 0,
    y: 0,
    w: '100%',
    h: '100%'
  });
});

// 保存
pptx.writeFile({ fileName: outputPath })
  .then(() => {
    console.log(`\n✅ PPT 生成成功: ${outputPath}`);
    console.log(`   共 ${images.length} 页`);
  })
  .catch(err => {
    console.error('生成失败:', err);
    process.exit(1);
  });
