#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔄 快速重命名文件...\n');

let count = 0;

// 使用 find 命令快速查找文件
try {
  // 重命名 Agents.md
  const agentsFiles = execSync('find . -name "Agents.md" -type f 2>/dev/null', {
    cwd: process.cwd(),
    encoding: 'utf8'
  }).trim().split('\n').filter(f => f);

  for (const file of agentsFiles) {
    if (!file) continue;
    const dir = path.dirname(file);
    const newPath = path.join(dir, 'AGENTS.md');
    try {
      fs.renameSync(file, newPath);
      console.log(`✓ ${file} -> AGENTS.md`);
      count++;
    } catch (err) {
      // 忽略错误
    }
  }

  // 重命名 Gemini.md
  const geminiFiles = execSync('find . -name "Gemini.md" -type f 2>/dev/null', {
    cwd: process.cwd(),
    encoding: 'utf8'
  }).trim().split('\n').filter(f => f);

  for (const file of geminiFiles) {
    if (!file) continue;
    const dir = path.dirname(file);
    const newPath = path.join(dir, 'GEMINI.md');
    try {
      fs.renameSync(file, newPath);
      console.log(`✓ ${file} -> GEMINI.md`);
      count++;
    } catch (err) {
      // 忽略错误
    }
  }

  console.log(`\n✅ 完成！共重命名 ${count} 个文件`);
} catch (error) {
  console.error('❌ 错误:', error.message);
}
