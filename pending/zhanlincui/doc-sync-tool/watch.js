#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { scanDirectory, syncFileGroup, CONFIG } = require('./sync.js');

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  red: '\x1b[31m',
  magenta: '\x1b[35m'
};

function log(message, color = 'reset') {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`${colors[color]}[${timestamp}] ${message}${colors.reset}`);
}

// 防抖处理 - 避免短时间内重复触发
const debounceTimers = new Map();

function debounce(key, callback, delay = 1000) {
  if (debounceTimers.has(key)) {
    clearTimeout(debounceTimers.get(key));
  }

  const timer = setTimeout(() => {
    debounceTimers.delete(key);
    callback();
  }, delay);

  debounceTimers.set(key, timer);
}

// 监听文件变化
function watchFiles() {
  log('🔍 正在扫描现有文件...', 'cyan');

  // 初始扫描
  const fileGroups = scanDirectory(CONFIG.scanPath);

  if (fileGroups.size === 0) {
    log('⚠️  未找到任何目标文件，将持续监听新文件创建...', 'yellow');
  } else {
    log(`✓ 找到 ${fileGroups.size} 个目录包含目标文件`, 'green');
  }

  // 存储所有需要监听的目录
  const watchedDirs = new Set();
  const watchers = new Map();

  // 使用递归监听（macOS/Windows 原生支持）
  function addDirWatch(dir) {
    if (watchedDirs.has(dir)) return;

    try {
      // 使用递归模式监听整个目录树
      const watcher = fs.watch(dir, { recursive: true }, (eventType, filename) => {
        if (!filename) return;

        const fullPath = path.join(dir, filename);

        // 跳过排除的目录
        const pathParts = filename.split(path.sep);
        if (pathParts.some(part => CONFIG.excludeDirs.includes(part))) {
          return;
        }

        // 检查是否是目标文件
        const baseName = path.basename(filename);
        if (CONFIG.targetFiles.includes(baseName)) {
          debounce(fullPath, () => {
            log(`\n📝 检测到文件变化: ${fullPath}`, 'yellow');

            try {
              // 重新扫描该文件所在目录
              const fileDir = path.dirname(fullPath);
              const fileGroups = scanDirectory(fileDir);
              const files = fileGroups.get(fileDir);

              if (files && files.length > 0) {
                syncFileGroup(fileDir, files);
              }
            } catch (error) {
              log(`❌ 同步失败: ${error.message}`, 'red');
            }
          });
        }
      });

      watchedDirs.add(dir);
      watchers.set(dir, watcher);
    } catch (error) {
      // 跳过无权限访问的目录
      if (error.code !== 'EACCES' && error.code !== 'EPERM') {
        log(`❌ 监听目录失败 ${dir}: ${error.message}`, 'red');
      }
    }
  }

  // 开始监听
  addDirWatch(CONFIG.scanPath);

  log('\n' + '='.repeat(60), 'cyan');
  log('👀 文件监听已启动！', 'bright');
  log(`📂 监听目录: ${CONFIG.scanPath}`, 'blue');
  log(`📋 目标文件: ${CONFIG.targetFiles.join(', ')}`, 'blue');
  log(`🗂️  监听中的目录: ${watchedDirs.size} 个`, 'blue');
  log('💡 按 Ctrl+C 停止监听', 'magenta');
  log('='.repeat(60) + '\n', 'cyan');

  // 处理优雅退出
  process.on('SIGINT', () => {
    log('\n\n🛑 正在停止监听...', 'yellow');

    // 关闭所有 watchers
    for (const watcher of watchers.values()) {
      watcher.close();
    }

    log('✅ 已安全退出', 'green');
    process.exit(0);
  });
}

// 启动监听
if (require.main === module) {
  log('\n🚀 启动文档同步监听服务...', 'bright');
  watchFiles();
} else {
  module.exports = { watchFiles };
}
