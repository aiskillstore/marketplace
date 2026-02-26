---
name: doc-sync-tool
description: 自动同步项目中的 Agents.md、claude.md 和 gemini.md 文件，保持内容一致性。支持自动监听和手动触发。
---

# 文档同步工具 (Doc Sync Tool)

## 功能说明

这个工具用于自动同步项目中的 AI Agent 配置文档，确保 `Agents.md`、`claude.md` 和 `gemini.md` 三个文件内容保持一致。

### 核心功能

1. **自动发现**: 递归扫描当前目录下所有文件夹，查找这三个文档
2. **智能同步**: 发现任意一个文档时，自动创建/更新其余两个
3. **文件监听**: 实时监听文件变化，自动同步最新内容
4. **手动触发**: 支持命令行手动执行同步

## 使用场景

- 在多个 AI Agent 之间共享相同的项目配置
- 自动保持不同 AI 的工作指令一致
- 避免手动维护多个相同文档的麻烦

## 使用方法

### 安装依赖

```bash
cd /Users/ben/Downloads/go\ to\ wild/auto-website-system/_skills/doc-sync-tool
pnpm install
```

### 手动同步（单次执行）

```bash
# 在项目根目录执行
node /Users/ben/Downloads/go\ to\ wild/auto-website-system/_skills/doc-sync-tool/sync.js

# 或者使用 npm script
pnpm run sync
```

### 自动监听（持续运行）

```bash
# 启动文件监听服务
node /Users/ben/Downloads/go\ to\ wild/auto-website-system/_skills/doc-sync-tool/watch.js

# 或者使用 npm script
pnpm run watch
```

### 后台运行（推荐）

```bash
# 使用 PM2 在后台运行
pm2 start /Users/ben/Downloads/go\ to\ wild/auto-website-system/_skills/doc-sync-tool/watch.js --name doc-sync

# 查看状态
pm2 status

# 停止服务
pm2 stop doc-sync
```

## 工作原理

1. **扫描阶段**: 递归遍历指定目录，查找 `Agents.md`、`claude.md`、`gemini.md` 文件
2. **分组阶段**: 将同一文件夹下的这三个文件归为一组
3. **同步阶段**:
   - 如果某组只有一个文件，复制内容创建其余两个
   - 如果某组有多个文件，选择最新修改的作为源，同步到其他文件
4. **监听阶段** (watch 模式): 持续监听文件变化，触发同步

## 配置选项

可以在 `sync.js` 中修改以下配置：

```javascript
const CONFIG = {
  targetFiles: ['Agents.md', 'claude.md', 'gemini.md'],  // 目标文件列表
  scanPath: process.cwd(),                                // 扫描路径（默认当前目录）
  excludeDirs: ['node_modules', '.git', '.next', 'dist'] // 排除目录
};
```

## 注意事项

- 工具会自动跳过 `node_modules`、`.git`、`.next`、`dist` 等目录
- 同步时会保留文件的原始格式和内容
- 建议在 Git 仓库中使用，方便追踪文件变化
- 监听模式会持续运行，建议使用 PM2 管理进程

## 故障排除

### 权限问题
```bash
chmod +x sync.js watch.js
```

### Node.js 版本要求
需要 Node.js 14+ 版本

### 依赖安装失败
```bash
rm -rf node_modules package-lock.json
pnpm install
```
