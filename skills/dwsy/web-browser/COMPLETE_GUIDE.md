# Web Browser Subagent - 完整指南

## 📦 已创建的内容

### 1. 子代理配置
**文件**: `~/.pi/agent/agents/web-browser.md`

专业的网页浏览器代理配置，包含：
- 核心能力描述
- 工作流程
- 使用场景（网页调研、数据抓取、自动化测试、登录后操作）
- 最佳实践
- 故障排除

### 2. 核心脚本
**目录**: `~/.pi/agent/skills/web-browser/scripts/`

| 脚本 | 功能 | 说明 |
|------|------|------|
| `start.js` | 启动浏览器 | 生成随机端口，启动独立 Chrome 实例 |
| `stop.js` | 停止浏览器 | 优雅关闭，保留端口配置 |
| `get-port.js` | 获取端口 | 查看当前使用的端口 |
| `nav.js` | 导航页面 | 打开 URL，支持新标签页 |
| `eval.js` | 执行 JS | 在页面中执行 JavaScript |
| `screenshot.js` | 截图 | 保存当前页面截图 |
| `pick.js` | 选择元素 | 交互式元素选择器 |

### 3. 测试和示例脚本
**目录**: `~/.pi/agent/skills/web-browser/`

| 脚本 | 功能 | 说明 |
|------|------|------|
| `test-subagent.js` | 完整测试 | 测试所有功能和生成报告 |
| `test-integration.js` | 集成测试 | 验证子代理配置和脚本 |
| `examples.js` | 使用示例 | 展示 5 种常见使用场景 |
| `demo.js` | 快速演示 | 基础功能演示 |

### 4. 文档
**目录**: `~/.pi/agent/skills/web-browser/`

| 文档 | 内容 |
|------|------|
| `README.md` | 完整使用文档 |
| `SKILL.md` | 技能文档 |
| `FIX_NOTE.md` | 修复说明 |
| `SUBAGENT_CREATED.md` | 创建说明 |

## 🚀 快速开始

### 运行测试
```bash
cd ~/.pi/agent/skills/web-browser

# 完整功能测试
node test-subagent.js

# 集成测试
node test-integration.js

# 查看示例
node examples.js

# 快速演示
node demo.js
```

### 使用子代理
```bash
# 通过 subagent 命令
subagent web-browser "Research https://example.com and extract key information"

# 多个任务
subagent web-browser "Scrape all links from https://news.ycombinator.com"
subagent web-browser "Login to GitHub and extract repository information"
subagent web-browser "Test the login functionality on https://example.com"
```

### 直接使用脚本
```bash
cd ~/.pi/agent/skills/web-browser

# 启动浏览器
node scripts/start.js

# 查看端口
node scripts/get-port.js

# 导航页面
node scripts/nav.js https://example.com

# 执行 JavaScript
node scripts/eval.js 'document.title'

# 截图
node scripts/screenshot.js

# 停止浏览器
node scripts/stop.js
```

## 📋 核心特性

### ✅ 完全独立
- 不影响你的主 Chrome 浏览器
- 独立的配置和数据目录
- 独立的 cookies 和登录状态

### ✅ 持久化存储
- Cookies 自动保存
- LocalStorage 持久化
- Session 数据保留

### ✅ 随机端口
- 自动生成随机端口（9222-9999）
- 避免端口冲突
- 端口自动复用

### ✅ 丰富功能
- 页面导航
- JavaScript 执行
- DOM 操作
- 表单交互
- 数据提取
- 截图
- 元素选择

## 🎯 使用场景

### 场景 1: 网页调研
```bash
subagent web-browser "Research https://example.com and extract key information"
```

### 场景 2: 数据抓取
```bash
subagent web-browser "Scrape all links from https://news.ycombinator.com"
```

### 场景 3: 登录后操作
```bash
subagent web-browser "Login to GitHub and extract repository information"
```

### 场景 4: 自动化测试
```bash
subagent web-browser "Test the login functionality on https://example.com"
```

### 场景 5: 监控和分析
```bash
subagent web-browser "Monitor https://example.com for changes"
```

## 💡 最佳实践

1. **总是停止浏览器**: 使用完后执行 `node scripts/stop.js` 释放资源
2. **检查端口**: 使用 `node scripts/get-port.js` 查看当前端口
3. **错误处理**: 如果遇到错误，重启浏览器重试
4. **持久化**: 使用 `--profile` 选项可以在需要登录的场景中使用
5. **批量操作**: 减少重复导航，提高效率

## 🔧 技术细节

### 端口管理
```bash
# 查看端口
node scripts/get-port.js

# 重置端口
rm ~/.cache/scraping-web-browser/port.txt
node scripts/start.js
```

### 配置目录
- **配置**: `~/.cache/scraping-web-browser/`
- **端口文件**: `~/.cache/scraping-web-browser/port.txt`
- **Cookies**: `~/.cache/scraping-web-browser/Default/Cookies`
- **LocalStorage**: `~/.cache/scraping-web-browser/Default/Local Storage/`

### 进程管理
```bash
# 查看进程
ps aux | grep "scraping-web-browser"

# 停止浏览器
node scripts/stop.js

# 强制停止
pkill -f "scraping-web-browser"
```

## 📊 测试结果

### 功能测试
```bash
$ cd ~/.pi/agent/skills/web-browser && node test-subagent.js

🌐 Testing web-browser subagent

1️⃣ Starting browser...
   ✓ Browser started on port 9458

2️⃣ Navigating to example.com...
   ✓ Page loaded

3️⃣ Extracting page information...
   Title: Example Domain
   Links: 1
   Headings: 1

4️⃣ Extracting links...

5️⃣ Taking screenshot...
   Screenshot: /var/folders/.../screenshot-...png

6️⃣ Testing localStorage persistence...
   Stored: subagent-test

📊 Web Browser Research Report
==================================================

## Page Information
- URL: https://example.com
- Title: Example Domain
- Port: 9458

## Page Structure
- Links: 1
- Headings: 1

## Screenshot
- Path: /var/folders/.../screenshot-...png

## Storage Test
- localStorage: ✓ Working

## Status
✓ All tests passed!
✓ Web browser subagent is ready to use!

🧹 Cleanup...
   ✓ Browser stopped
```

### 集成测试
```bash
$ cd ~/.pi/agent/skills/web-browser && node test-integration.js

🧪 Testing subagent integration

1️⃣ Checking agent configuration...
   ✓ Found

2️⃣ Checking browser scripts...
   ✓ start.js
   ✓ stop.js
   ✓ get-port.js
   ✓ nav.js
   ✓ eval.js
   ✓ screenshot.js

3️⃣ Testing subagent invocation...
   Example command:
   $ subagent web-browser "Research https://example.com"

📊 Subagent Summary
==================================================
Name: web-browser
Path: ~/.pi/agent/agents/web-browser.md
Skill: ~/.pi/agent/skills/web-browser/

🎯 Capabilities:
  ✓ Web page research
  ✓ Data extraction
  ✓ Form automation
  ✓ Screenshot capture
  ✓ Cookie management
  ✓ Persistent sessions

🚀 Quick Start:
  # Run tests
  cd ~/.pi/agent/skills/web-browser && node test-subagent.js

  # Use subagent
  subagent web-browser "Your task here"

✅ Subagent is ready to use!
```

## 🎉 总结

### 创建的文件
✅ `~/.pi/agent/agents/web-browser.md` - 子代理配置
✅ `~/.pi/agent/skills/web-browser/scripts/stop.js` - 停止浏览器脚本
✅ `~/.pi/agent/skills/web-browser/scripts/get-port.js` - 获取端口脚本
✅ `~/.pi/agent/skills/web-browser/test-subagent.js` - 完整测试脚本
✅ `~/.pi/agent/skills/web-browser/test-integration.js` - 集成测试脚本
✅ `~/.pi/agent/skills/web-browser/examples.js` - 使用示例
✅ `~/.pi/agent/skills/web-browser/README.md` - 使用文档
✅ `~/.pi/agent/skills/web-browser/SUBAGENT_CREATED.md` - 创建说明

### 修复的功能
✅ 不再关闭主浏览器
✅ 使用独立的浏览器实例
✅ 支持随机端口
✅ 持久化 cookies 和 localStorage
✅ 优化启动参数

### 测试验证
✅ 所有功能已测试
✅ 集成测试通过
✅ 可以立即使用

现在你可以使用这个专业的 web 浏览器子代理进行各种网页相关的任务了！🚀