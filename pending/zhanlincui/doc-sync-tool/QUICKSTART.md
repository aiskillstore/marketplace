# 快速开始指南

## 最简单的使用方式

### 1️⃣ 手动同步（推荐新手）

在项目根目录执行：

```bash
cd "/Users/ben/Downloads/go to wild"
./auto-website-system/_skills/doc-sync-tool/run-sync.sh
```

或者指定目录：

```bash
./auto-website-system/_skills/doc-sync-tool/run-sync.sh /path/to/your/project
```

### 2️⃣ 自动监听（推荐日常使用）

启动监听服务（会持续运行）：

```bash
cd "/Users/ben/Downloads/go to wild"
./auto-website-system/_skills/doc-sync-tool/run-watch.sh
```

按 `Ctrl+C` 停止监听。

### 3️⃣ 后台运行（推荐生产环境）

使用 PM2 在后台运行：

```bash
# 安装 PM2
npm install -g pm2

# 启动服务
pm2 start "/Users/ben/Downloads/go to wild/auto-website-system/_skills/doc-sync-tool/watch.js" \
  --name doc-sync \
  --cwd "/Users/ben/Downloads/go to wild"

# 查看状态
pm2 status

# 查看日志
pm2 logs doc-sync

# 停止服务
pm2 stop doc-sync
```

## 使用场景

### 场景 A：新项目初始化

1. 在项目文件夹创建 `claude.md`
2. 运行同步工具：`./run-sync.sh`
3. 自动生成 `Agents.md` 和 `gemini.md`

### 场景 B：编辑文档自动同步

1. 启动监听：`./run-watch.sh`
2. 编辑任意一个文件（如 `claude.md`）
3. 保存后自动同步到其他两个文件

### 场景 C：批量同步多个项目

```bash
# 在包含多个项目的根目录执行
cd "/Users/ben/Downloads/go to wild"
./auto-website-system/_skills/doc-sync-tool/run-sync.sh
```

## 常见问题

**Q: 如何验证工具是否工作？**

创建一个测试文件：
```bash
mkdir -p /tmp/test-sync
echo "# Test" > /tmp/test-sync/claude.md
./run-sync.sh /tmp/test-sync
ls /tmp/test-sync
# 应该看到: Agents.md  claude.md  gemini.md
```

**Q: 监听模式下如何知道同步成功？**

终端会实时显示：
```
[10:35:20] 📝 检测到文件变化: /path/to/claude.md
[10:35:20] 📁 处理目录: /path/to
[10:35:20]    ✅ 更新: Agents.md
[10:35:20]    🎉 成功同步 1 个文件
```

**Q: 可以修改同步的文件名吗？**

可以！编辑 `sync.js` 中的配置：
```javascript
const CONFIG = {
  targetFiles: ['Agents.md', 'claude.md', 'gemini.md', 'your-custom.md'],
  // ...
};
```

**Q: 如何排除某些目录？**

编辑 `sync.js` 中的配置：
```javascript
const CONFIG = {
  excludeDirs: ['node_modules', '.git', 'your-custom-dir'],
  // ...
};
```

## 最佳实践

1. **开发阶段**: 使用监听模式 (`run-watch.sh`)
2. **CI/CD**: 在构建前运行 `run-sync.sh`
3. **团队协作**: 将同步工具加入 Git Hooks
4. **生产环境**: 使用 PM2 在后台运行

## 下一步

- 阅读完整文档: [README.md](./README.md)
- 查看技能描述: [SKILL.md](./SKILL.md)
- 自定义配置: 编辑 `sync.js` 中的 CONFIG 对象

---

**需要帮助？** 联系 Ben (@littlebena)
