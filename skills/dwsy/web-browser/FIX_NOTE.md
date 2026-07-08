# Web Browser Skill - 修复说明

## 修复内容

### 问题
- 原始脚本会执行 `killall 'Google Chrome'`，关闭用户正在使用的浏览器
- 没有独立的浏览器实例，会与主浏览器冲突
- 固定端口 9222 可能与其他服务冲突

### 解决方案
1. **移除强制关闭浏览器的代码**
   - 删除了 `killall 'Google Chrome'` 命令
   - 改为先检查端口是否已被占用

2. **使用独立的浏览器配置**
   - 独立的用户数据目录：`~/.cache/scraping-web-browser`
   - 独立的 Chrome 实例，不影响主浏览器
   - 持久化的 session 存储（cookies、localStorage）

3. **随机端口支持** ⭐ 新功能
   - 首次启动时生成随机端口（9222-9999）
   - 端口信息保存在 `~/.cache/scraping-web-browser/port.txt`
   - 下次启动自动复用相同端口
   - 删除 port.txt 可生成新随机端口

4. **优化启动参数**
   - 添加 `--no-proxy-server` 避免网络代理问题
   - 添加更多禁用选项提高稳定性

## 使用方法

### 1. 启动浏览器

```bash
# 启动独立浏览器实例（全新配置）
cd ~/.pi/agent/skills/web-browser
node scripts/start.js

# 如果需要复制你的主浏览器配置（cookies、登录状态）
node scripts/start.js --profile
```

**重要说明**：
- 浏览器会在后台运行，不会弹出窗口
- 使用独立的配置文件，**不会影响你正在使用的 Chrome**
- cookies、localStorage 等会持久化保存
- 如果浏览器已经在运行，会提示并退出（不会重复启动）
- 端口会自动生成并保存，无需手动指定

### 1.1 端口管理

```bash
# 查看当前使用的端口
node scripts/get-port.js

# 重置端口（使用新的随机端口）
rm ~/.cache/scraping-web-browser/port.txt
node scripts/start.js

# 停止浏览器
node scripts/stop.js
```

### 2. 导航网页

```bash
# 打开新页面
node scripts/nav.js https://example.com

# 在新标签页打开
node scripts/nav.js https://example.com --new
```

### 3. 执行 JavaScript

```bash
# 获取页面标题
node scripts/eval.js 'document.title'

# 获取所有链接
node scripts/eval.js 'document.querySelectorAll("a").length'

# 设置 localStorage
node scripts/eval.js 'localStorage.setItem("key", "value")'

# 读取 localStorage
node scripts/eval.js 'localStorage.getItem("key")'

# 读取 cookies
node scripts/eval.js 'document.cookie'
```

### 4. 截图

```bash
# 截取当前页面
node scripts/screenshot.js
# 返回临时文件路径
```

### 5. 选择元素

```bash
# 交互式元素选择器
node scripts/pick.js "描述要选择的元素"
```

## 验证修复

### 测试独立浏览器

```bash
# 1. 启动技能浏览器
cd ~/.pi/agent/skills/web-browser
node scripts/start.js

# 2. 查看随机端口
node scripts/get-port.js
# 输出类似: 9347

# 3. 设置测试数据
node scripts/eval.js 'localStorage.setItem("test", "hello")'

# 4. 重启浏览器
node scripts/stop.js
node scripts/start.js

# 5. 验证数据持久化
node scripts/eval.js 'localStorage.getItem("test")'
# 应该输出: hello

# 6. 验证端口保持不变
node scripts/get-port.js
# 应该输出与步骤 2 相同的端口
```

### 验证不影响主浏览器

```bash
# 查看所有 Chrome 进程
ps aux | grep -i "Google Chrome" | grep -v grep

# 应该看到两组进程：
# 1. 你的主 Chrome（没有 scraping-web-browser 参数）
# 2. 技能的 Chrome（有 --user-data-dir=...scraping-web-browser）
```

## 技术细节

### 配置文件位置
- **主浏览器**：`~/Library/Application Support/Google/Chrome/`
- **技能浏览器**：`~/.cache/scraping-web-browser/`
- **端口文件**：`~/.cache/scraping-web-browser/port.txt`

### 端口管理
- **随机范围**：9222-9999
- **首次生成**：使用 crypto.randomInt() 生成
- **持久化**：保存到 port.txt
- **自动复用**：每次启动读取 port.txt
- **冲突检测**：启动前检查端口是否被占用

### 进程管理
```bash
# 查看技能浏览器进程
ps aux | grep "scraping-web-browser" | grep -v grep

# 停止技能浏览器
node scripts/stop.js

# 强制停止
pkill -f "scraping-web-browser"
```

## 注意事项

1. **不要同时运行多个实例**
   - 端口只能被一个 Chrome 实例占用
   - 如果启动失败，先执行 `node scripts/stop.js`

2. **网络问题**
   - 如果遇到 `ERR_CONNECTION_CLOSED`，检查网络代理设置
   - 脚本已添加 `--no-proxy-server` 选项

3. **内存使用**
   - 独立浏览器实例会占用一定内存
   - 不使用时可以手动停止

4. **安全性**
   - 独立浏览器有独立的 cookies 和登录状态
   - 使用 `--profile` 选项会复制主浏览器的登录信息

5. **端口冲突**
   - 随机端口极大降低了冲突概率
   - 如果仍有冲突，删除 port.txt 重新生成

## 常见问题

### Q: 启动后无法访问网页？
A: 检查网络连接，可能需要重启浏览器：
```bash
node scripts/stop.js
node scripts/start.js
```

### Q: 如何清除 cookies？
A: 删除配置文件：
```bash
rm -rf ~/.cache/scraping-web-browser
node scripts/start.js
```

### Q: 可以同时使用主浏览器和技能浏览器吗？
A: 可以！它们是完全独立的实例，互不影响。

### Q: 如何查看浏览器界面？
A: 打开 Chrome 访问 `chrome://inspect`，点击 "Configure" 添加 `localhost:<端口>`（端口通过 `node scripts/get-port.js` 查看），然后就可以看到远程调试界面了。

### Q: 如何更改端口？
A: 删除 port.txt 文件，然后重新启动：
```bash
rm ~/.cache/scraping-web-browser/port.txt
node scripts/start.js
```

### Q: 端口被占用怎么办？
A: 删除 port.txt 重新生成随机端口：
```bash
rm ~/.cache/scraping-web-browser/port.txt
node scripts/start.js
```

## 总结

修复后的 web-browser 技能：
✅ **完全独立** - 不影响你的主浏览器
✅ **持久化存储** - cookies、localStorage 会保存
✅ **随机端口** - 自动生成并复用，避免冲突
✅ **稳定可靠** - 优化了启动参数和错误处理
✅ **易于使用** - 简单的命令行接口
✅ **安全隔离** - 独立的用户数据目录

现在可以放心使用这个技能进行网页调研和自动化操作了！