# 使用示例

以下是文档同步工具的实际使用场景和示例。

## 场景 1: 新项目初始化

你正在创建一个新的网站项目，需要为 Claude、Agents 和 Gemini 创建配置文档。

### 步骤

```bash
# 1. 创建项目目录
mkdir -p /Users/ben/Downloads/go\ to\ wild/websites/my-new-site

# 2. 创建 Claude 配置文档
cat > /Users/ben/Downloads/go\ to\ wild/websites/my-new-site/claude.md << 'EOF'
# My New Site - Claude Configuration

## Project Overview
A new website for...

## Key Commands
- `pnpm dev` - Start development server
- `pnpm build` - Build for production

## Important Files
- `src/app/page.tsx` - Homepage
- `next.config.js` - Next.js config
EOF

# 3. 运行同步工具
cd /Users/ben/Downloads/go\ to\ wild
./auto-website-system/_skills/doc-sync-tool/run-sync.sh
```

### 结果

```
websites/my-new-site/
├── Agents.md     ✨ 自动创建
├── claude.md     ✓ 原有文件
└── gemini.md     ✨ 自动创建
```

所有三个文件内容完全相同！

---

## 场景 2: 更新现有配置（手动同步）

你修改了某个项目的 `claude.md`，需要同步到其他文件。

### 步骤

```bash
# 1. 编辑文件
vim /Users/ben/Downloads/go\ to\ wild/websites/example-site/claude.md

# 2. 保存后运行同步
cd /Users/ben/Downloads/go\ to\ wild
./auto-website-system/_skills/doc-sync-tool/run-sync.sh
```

### 输出示例

```
🚀 开始扫描文档...
📂 扫描路径: /Users/ben/Downloads/go to wild

✓ 找到 5 个目录包含目标文件

📁 处理目录: /Users/ben/Downloads/go to wild/websites/example-site
   📄 源文件: claude.md (2025-11-27 15:30:00)
   ✅ 更新: Agents.md
   ✅ 更新: gemini.md
   🎉 成功同步 2 个文件

============================================================
✅ 同步完成！
   📊 处理目录: 5 个
   📝 更新文件: 2 个
   ⏱️  耗时: 0.18s
============================================================
```

---

## 场景 3: 实时监听（开发模式）

你正在频繁修改配置文档，希望自动同步而不用手动运行命令。

### 步骤

```bash
# 启动监听服务
cd /Users/ben/Downloads/go\ to\ wild
./auto-website-system/_skills/doc-sync-tool/run-watch.sh
```

### 输出示例

```
🚀 启动文档监听服务...
🔍 正在扫描现有文件...
✓ 找到 5 个目录包含目标文件

============================================================
👀 文件监听已启动！
📂 监听目录: /Users/ben/Downloads/go to wild
📋 目标文件: Agents.md, claude.md, gemini.md
🗂️  监听中的目录: 145 个
💡 按 Ctrl+C 停止监听
============================================================
```

### 编辑文件时

当你保存 `claude.md` 时，终端会实时显示：

```
[15:35:20] 📝 检测到文件变化: /Users/ben/.../claude.md
[15:35:20] 📁 处理目录: /Users/ben/.../websites/example-site
[15:35:20]    📄 源文件: claude.md
[15:35:20]    ✅ 更新: Agents.md
[15:35:20]    ✅ 更新: gemini.md
[15:35:20]    🎉 成功同步 2 个文件
```

---

## 场景 4: 批量同步多个项目

你有多个网站项目，希望一次性同步所有文档。

### 目录结构

```
/Users/ben/Downloads/go to wild/websites/
├── site-a/
│   └── claude.md
├── site-b/
│   └── gemini.md
├── site-c/
│   └── Agents.md
└── site-d/
    ├── claude.md
    └── Agents.md (内容过时)
```

### 步骤

```bash
cd /Users/ben/Downloads/go\ to\ wild/websites
node ../auto-website-system/_skills/doc-sync-tool/sync.js
```

### 结果

```
site-a/
├── Agents.md     ✨ 新建
├── claude.md     ✓ 原有
└── gemini.md     ✨ 新建

site-b/
├── Agents.md     ✨ 新建
├── claude.md     ✨ 新建
└── gemini.md     ✓ 原有

site-c/
├── Agents.md     ✓ 原有
├── claude.md     ✨ 新建
└── gemini.md     ✨ 新建

site-d/
├── Agents.md     ✅ 更新为最新内容
├── claude.md     ✓ 原有（最新）
└── gemini.md     ✨ 新建
```

---

## 场景 5: PM2 后台运行（生产环境）

你希望工具在后台持续运行，开机自启动。

### 安装 PM2

```bash
npm install -g pm2
```

### 启动服务

```bash
pm2 start /Users/ben/Downloads/go\ to\ wild/auto-website-system/_skills/doc-sync-tool/watch.js \
  --name doc-sync \
  --cwd "/Users/ben/Downloads/go to wild"
```

### 管理服务

```bash
# 查看状态
pm2 status
```

输出：
```
┌─────┬────────────┬─────────┬──────┬─────────┬──────────┐
│ id  │ name       │ status  │ cpu  │ memory  │ restart  │
├─────┼────────────┼─────────┼──────┼─────────┼──────────┤
│ 0   │ doc-sync   │ online  │ 0%   │ 45.2mb  │ 0        │
└─────┴────────────┴─────────┴──────┴─────────┴──────────┘
```

```bash
# 查看实时日志
pm2 logs doc-sync
```

```bash
# 停止服务
pm2 stop doc-sync

# 重启服务
pm2 restart doc-sync

# 删除服务
pm2 delete doc-sync
```

### 开机自启动

```bash
# 生成启动脚本
pm2 startup

# 保存当前服务列表
pm2 save
```

---

## 场景 6: 与 Git 集成

自动在 Git 提交时同步文档。

### 创建 Git Hook

```bash
# 创建 post-commit hook
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
echo "🔄 同步文档..."
node auto-website-system/_skills/doc-sync-tool/sync.js
EOF

# 添加执行权限
chmod +x .git/hooks/post-commit
```

### 效果

每次 `git commit` 后自动同步文档：

```bash
git commit -m "Update configuration"
```

输出：
```
[main abc1234] Update configuration
 1 file changed, 10 insertions(+)
🔄 同步文档...
✅ 同步完成！处理 3 个目录，更新 2 个文件
```

---

## 场景 7: CI/CD 集成

在 GitHub Actions 中自动同步文档。

### `.github/workflows/sync-docs.yml`

```yaml
name: Sync Agent Docs

on:
  push:
    paths:
      - '**/claude.md'
      - '**/Agents.md'
      - '**/gemini.md'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Sync Documents
        run: |
          node auto-website-system/_skills/doc-sync-tool/sync.js

      - name: Commit Changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add -A
          git diff --quiet && git diff --staged --quiet || \
            git commit -m "chore: sync agent docs [skip ci]"
          git push
```

---

## 场景 8: 自定义配置

你想同步更多文件类型，或排除特定目录。

### 编辑配置

编辑 `sync.js` 文件：

```javascript
const CONFIG = {
  // 添加更多要同步的文件
  targetFiles: [
    'Agents.md',
    'claude.md',
    'gemini.md',
    'chatgpt.md',    // 新增
    'perplexity.md'  // 新增
  ],

  scanPath: process.cwd(),

  // 排除更多目录
  excludeDirs: [
    'node_modules',
    '.git',
    '.next',
    'dist',
    'build',
    'temp',          // 新增
    'backup'         // 新增
  ]
};
```

### 运行

```bash
./run-sync.sh
```

现在工具会同步 5 个文件：`Agents.md`、`claude.md`、`gemini.md`、`chatgpt.md`、`perplexity.md`

---

## 场景 9: 调试模式

遇到问题时查看详细信息。

### 方法 1: 直接运行 Node 脚本

```bash
cd /Users/ben/Downloads/go\ to\ wild
node auto-website-system/_skills/doc-sync-tool/sync.js 2>&1 | tee sync.log
```

### 方法 2: 查看 PM2 日志

```bash
pm2 logs doc-sync --lines 100
```

### 方法 3: 添加调试输出

临时修改 `sync.js`，在 `log` 函数中添加：

```javascript
function log(message, color = 'reset') {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${colors[color]}${message}${colors.reset}`);
}
```

---

## 常见问题解决

### 问题 1: 找不到文件

**症状**: 运行后显示"未找到任何目标文件"

**解决**:
```bash
# 检查当前目录
pwd

# 列出所有匹配的文件
find . -name "claude.md" -o -name "Agents.md" -o -name "gemini.md"

# 确保不在排除目录中
cat sync.js | grep excludeDirs
```

### 问题 2: 权限错误

**症状**: `EACCES: permission denied`

**解决**:
```bash
# 添加执行权限
chmod +x run-sync.sh run-watch.sh sync.js watch.js

# 检查文件权限
ls -la /Users/ben/Downloads/go\ to\ wild/auto-website-system/_skills/doc-sync-tool/
```

### 问题 3: 监听不生效

**症状**: 修改文件后没有触发同步

**解决**:
```bash
# 确认监听服务正在运行
ps aux | grep watch.js

# 或使用 PM2
pm2 status

# 重启服务
pm2 restart doc-sync
```

---

## 性能测试

### 小型项目 (< 100 个目录)

```bash
time ./run-sync.sh
```

输出：
```
⏱️  耗时: 0.12s
```

### 中型项目 (100-500 个目录)

```bash
time ./run-sync.sh
```

输出：
```
⏱️  耗时: 0.45s
```

### 大型项目 (500+ 个目录)

```bash
time ./run-sync.sh
```

输出：
```
⏱️  耗时: 1.2s
```

---

## 最佳实践

1. **开发时使用监听模式**
   ```bash
   ./run-watch.sh
   ```

2. **提交前手动同步一次**
   ```bash
   ./run-sync.sh && git add . && git commit -m "..."
   ```

3. **生产环境用 PM2**
   ```bash
   pm2 start watch.js --name doc-sync
   ```

4. **定期检查日志**
   ```bash
   pm2 logs doc-sync
   ```

5. **结合 Git Hooks 自动化**
   - 在 `pre-commit` 中运行同步
   - 确保提交前文档一致

---

需要更多帮助？查看 [README.md](./README.md) 或联系 Ben (@littlebena)
