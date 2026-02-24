# 文档同步工具 (Doc Sync Tool)

自动同步项目中的 `Agents.md`、`claude.md` 和 `gemini.md` 文件，确保内容一致性。

## 🎯 功能特性

- ✅ **自动发现**: 递归扫描所有文件夹，查找目标文档
- ✅ **智能同步**: 以最新文件为准，自动创建/更新其他文件
- ✅ **实时监听**: 文件变化时自动触发同步
- ✅ **手动触发**: 支持命令行一键同步
- ✅ **排除无关目录**: 自动跳过 node_modules、.git 等目录
- ✅ **防抖处理**: 避免短时间内重复触发

## 📦 安装

无需额外依赖，只需要 Node.js 14+ 环境。

```bash
# 克隆或下载工具到你的项目
cd path/to/doc-sync-tool
chmod +x sync.js watch.js
```

## 🚀 使用方法

### 方式一：手动同步（单次执行）

在项目根目录执行：

```bash
node path/to/doc-sync-tool/sync.js
```

或者使用相对路径：

```bash
cd your-project-root
node doc-sync-tool/sync.js
```

输出示例：
```
🚀 开始扫描文档...
📂 扫描路径: /path/to/your-project
📋 目标文件: AGENTS.md, CLAUDE.md, GEMINI.md

✓ 找到 3 个目录包含目标文件

📁 处理目录: /path/to/your-project/websites/example
   📄 源文件: CLAUDE.md (2025-11-27 10:30:45)
   ✨ 创建: AGENTS.md
   ✨ 创建: GEMINI.md
   🎉 成功同步 2 个文件

============================================================
✅ 同步完成！
   📊 处理目录: 3 个
   📝 更新文件: 5 个
   ⏱️  耗时: 0.23s
============================================================
```

### 方式二：自动监听（持续运行）

启动监听服务：

```bash
node path/to/doc-sync-tool/watch.js
```

输出示例：
```
🚀 启动文档同步监听服务...
🔍 正在扫描现有文件...
✓ 找到 3 个目录包含目标文件

============================================================
👀 文件监听已启动！
📂 监听目录: /path/to/your-project
📋 目标文件: AGENTS.md, CLAUDE.md, GEMINI.md
🗂️  监听中的目录: 1 个
💡 按 Ctrl+C 停止监听
============================================================

[10:35:20] 📝 检测到文件变化: /path/to/CLAUDE.md
[10:35:20] 📁 处理目录: /path/to
[10:35:20]    📄 源文件: CLAUDE.md
[10:35:20]    ✅ 更新: AGENTS.md
[10:35:20]    🎉 成功同步 1 个文件
```

按 `Ctrl+C` 停止监听。

### 方式三：后台运行（推荐生产环境）

使用 PM2 管理进程：

```bash
# 安装 PM2（如果还没有）
npm install -g pm2

# 启动服务
pm2 start path/to/doc-sync-tool/watch.js --name doc-sync --cwd /path/to/your-project

# 查看状态
pm2 status

# 查看日志
pm2 logs doc-sync

# 停止服务
pm2 stop doc-sync

# 删除服务
pm2 delete doc-sync

# 开机自启动
pm2 startup
pm2 save
```

## ⚙️ 配置选项

可以编辑 `sync.js` 修改配置：

```javascript
const CONFIG = {
  // 要同步的文件名列表
  targetFiles: ['AGENTS.md', 'CLAUDE.md', 'GEMINI.md'],

  // 扫描的根目录（默认为当前工作目录）
  scanPath: process.cwd(),

  // 排除的目录（不会扫描和监听）
  excludeDirs: [
    'node_modules',
    '.git',
    '.next',
    'dist',
    '.obsidian',
    'build',
    'out',
    '_pagefind'
  ]
};
```

## 📝 工作原理

1. **扫描阶段**: 递归遍历指定目录，查找三个目标文件
2. **分组阶段**: 将同一文件夹下的文件归为一组
3. **同步阶段**:
   - 选择最新修改的文件作为源文件
   - 将内容复制到同目录下的其他两个文件
   - 如果文件不存在则创建，存在则更新
   - 内容相同则跳过
4. **监听阶段** (watch 模式):
   - 监听所有目录的文件变化
   - 检测到目标文件变化时触发同步
   - 使用防抖机制避免重复触发

## 🔍 使用场景

### 场景 1: 新建项目

在项目中创建 `CLAUDE.md`，工具会自动创建 `AGENTS.md` 和 `GEMINI.md`。

### 场景 2: 更新配置

修改任意一个文件（如 `CLAUDE.md`），其他两个文件会自动同步更新。

### 场景 3: 批量同步

对多个项目的文档进行手动同步：

```bash
cd your-project-root
node doc-sync-tool/sync.js
```

## ⚠️ 注意事项

1. **内容覆盖**: 同步时会以最新文件为准，覆盖其他文件的内容
2. **Git 追踪**: 建议在 Git 仓库中使用，方便追踪文件变化
3. **权限问题**: 确保对目标目录有读写权限
4. **文件锁定**: 如果文件被其他程序占用，同步可能失败
5. **大型项目**: 扫描大量文件时可能需要几秒钟

## 🐛 故障排除

### 问题：权限被拒绝

```bash
chmod +x sync.js watch.js
```

### 问题：找不到文件

确保在正确的目录下执行：

```bash
pwd  # 查看当前目录
ls -la doc-sync-tool/  # 确认文件存在
```

### 问题：Node.js 版本过低

```bash
node --version  # 查看版本（需要 14+）
```

### 问题：监听未生效

检查是否有文件被 Git 忽略或权限限制。

## 📊 性能说明

- **扫描速度**: 约 1000 个文件/秒
- **同步速度**: 几乎即时（取决于文件大小）
- **内存占用**: < 50MB
- **CPU 占用**: 空闲时几乎为 0，同步时瞬时峰值 < 5%

## 🔗 集成建议

### 与 Git Hooks 集成

在 `.git/hooks/post-commit` 中添加：

```bash
#!/bin/bash
node path/to/doc-sync-tool/sync.js
```

### 与 CI/CD 集成

在 GitHub Actions 中添加：

```yaml
- name: Sync Doc Files
  run: |
    node doc-sync-tool/sync.js
    git add -A
    git commit -m "chore: sync agent docs" || true
```

## 📜 许可证

MIT License

## 👤 作者

Ben (@littlebena)

---

**提示**: 建议使用 PM2 在后台运行监听服务，确保文档始终保持同步！
