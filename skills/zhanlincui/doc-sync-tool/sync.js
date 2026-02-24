#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  targetFiles: ['AGENTS.md', 'CLAUDE.md', 'GEMINI.md'],  // 全部大写
  scanPath: process.cwd(),
  excludeDirs: ['node_modules', '.git', '.next', 'dist', '.obsidian', 'build', 'out', '_pagefind']
};

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  red: '\x1b[31m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// 递归扫描目录，查找目标文件
function scanDirectory(dir, fileGroups = new Map()) {
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        // 跳过排除目录
        if (CONFIG.excludeDirs.includes(entry.name)) {
          continue;
        }
        scanDirectory(fullPath, fileGroups);
      } else if (entry.isFile() && CONFIG.targetFiles.includes(entry.name)) {
        // 找到目标文件
        const dirPath = path.dirname(fullPath);

        if (!fileGroups.has(dirPath)) {
          fileGroups.set(dirPath, []);
        }

        fileGroups.get(dirPath).push({
          name: entry.name,
          path: fullPath,
          mtime: fs.statSync(fullPath).mtime
        });
      }
    }
  } catch (error) {
    // 跳过无权限访问的目录
    if (error.code !== 'EACCES' && error.code !== 'EPERM') {
      log(`❌ 扫描目录出错 ${dir}: ${error.message}`, 'red');
    }
  }

  return fileGroups;
}

// 同步文件组
function syncFileGroup(dirPath, files) {
  log(`\n📁 处理目录: ${dirPath}`, 'cyan');

  // 按修改时间排序，最新的作为源文件
  files.sort((a, b) => b.mtime - a.mtime);
  const sourceFile = files[0];

  log(`   📄 源文件: ${sourceFile.name} (${sourceFile.mtime.toLocaleString()})`, 'blue');

  try {
    // 读取源文件内容
    const content = fs.readFileSync(sourceFile.path, 'utf8');

    let syncCount = 0;

    // 同步到其他文件
    for (const targetFileName of CONFIG.targetFiles) {
      const targetFilePath = path.join(dirPath, targetFileName);
      const existingFile = files.find(f => f.name === targetFileName);

      if (existingFile) {
        // 文件已存在，检查内容是否相同
        const existingContent = fs.readFileSync(existingFile.path, 'utf8');

        if (existingContent !== content) {
          fs.writeFileSync(targetFilePath, content, 'utf8');
          log(`   ✅ 更新: ${targetFileName}`, 'green');
          syncCount++;
        } else {
          log(`   ⏭️  跳过: ${targetFileName} (内容相同)`, 'yellow');
        }
      } else {
        // 文件不存在，创建新文件
        fs.writeFileSync(targetFilePath, content, 'utf8');
        log(`   ✨ 创建: ${targetFileName}`, 'green');
        syncCount++;
      }
    }

    if (syncCount > 0) {
      log(`   🎉 成功同步 ${syncCount} 个文件`, 'bright');
    } else {
      log(`   ✓ 所有文件已是最新`, 'green');
    }

    return syncCount;
  } catch (error) {
    log(`   ❌ 同步失败: ${error.message}`, 'red');
    return 0;
  }
}

// 主函数
function main() {
  log('\n🚀 开始扫描文档...', 'bright');
  log(`📂 扫描路径: ${CONFIG.scanPath}`, 'blue');
  log(`📋 目标文件: ${CONFIG.targetFiles.join(', ')}`, 'blue');

  const startTime = Date.now();

  // 扫描目录
  const fileGroups = scanDirectory(CONFIG.scanPath);

  if (fileGroups.size === 0) {
    log('\n⚠️  未找到任何目标文件', 'yellow');
    return;
  }

  log(`\n✓ 找到 ${fileGroups.size} 个目录包含目标文件`, 'green');

  // 同步每个文件组
  let totalSynced = 0;
  for (const [dirPath, files] of fileGroups) {
    totalSynced += syncFileGroup(dirPath, files);
  }

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

  log('\n' + '='.repeat(60), 'cyan');
  log(`✅ 同步完成！`, 'bright');
  log(`   📊 处理目录: ${fileGroups.size} 个`, 'blue');
  log(`   📝 更新文件: ${totalSynced} 个`, 'blue');
  log(`   ⏱️  耗时: ${elapsed}s`, 'blue');
  log('='.repeat(60) + '\n', 'cyan');
}

// 导出供 watch.js 使用
if (require.main === module) {
  main();
} else {
  module.exports = { scanDirectory, syncFileGroup, CONFIG };
}
