# Web Browser Skill - 使用示例

## 基础示例

### 示例 1：访问网页并获取信息

```bash
# 打开网页
agent-browser open https://example.com

# 获取页面标题
agent-browser get title

# 获取当前 URL
agent-browser get url

# 截图
agent-browser screenshot /path/to/screenshot.png
```

### 示例 2：表单填写与提交

```bash
# 打开登录表单
agent-browser open https://example.com/login

# 获取可交互元素
agent-browser snapshot -i
# 输出示例：
# textbox "Email" [ref=e1]
# textbox "Password" [ref=e2]
# button "Sign In" [ref=e3]

# 填写表单
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "mysecretpassword"

# 提交表单
agent-browser click @e3

# 等待登录完成
agent-browser wait --load networkidle

# 验证登录成功
agent-browser get title
```

### 示例 3：使用语义定位器

```bash
# 语义定位 + 操作
agent-browser find role button click --name "Submit"
agent-browser find text "Sign Up" click
agent-browser find label "Email Address" fill "test@example.com"
```

## CDP 模式示例

### 示例 4：连接到 Electron 应用

```bash
# 启动 Electron 应用时启用调试（应用端配置）
# my-electron-app --remote-debugging-port=9222

# 连接并操作
agent-browser --cdp 9222 snapshot
agent-browser --cdp 9222 click @e1
agent-browser --cdp 9222 screenshot electron-app.png
```

### 示例 5：连接到 Chrome 远程调试

```bash
# 终端 1：启动 Chrome 随远程调试
google-chrome-stable --remote-debugging-port=9222

# 终端 2：使用 agent-browser 控制
agent-browser --cdp 9222 open https://github.com
agent-browser --cdp 9222 snapshot -i
agent-browser --cdp 9222 click @e5
```

## 测试场景示例

### 示例 6：完整的测试流程

```bash
# 1. 导航到测试页面
agent-browser open https://example.com/tests

# 2. 获取初始状态
agent-browser snapshot -i --json > initial-state.json

# 3. 执行测试操作
agent-browser click @e1  # 点击按钮
agent-browser wait 500   # 等待动画
agent-browser fill @e2 "test data"

# 4. 验证结果
agent-browser snapshot -i --json > final-state.json
agent-browser get text @result-container

# 5. 截图保存
agent-browser screenshot --full test-result.png

# 6. 关闭浏览器
agent-browser close
```

### 示例 7：数据抓取

```bash
# 打开列表页面
agent-browser open https://example.com/products

# 批量获取数据
agent-browser get text @product-list

# 使用 JavaScript 批量抓取
agent-browser eval `
  Array.from(document.querySelectorAll('.product')).map(p => ({
    name: p.querySelector('.name').textContent,
    price: p.querySelector('.price').textContent
  }))
`
```

## 会话管理示例

### 示例 8：并行浏览多个网站

```bash
# 会话 1：浏览站点 A
agent-browser --session site-a open https://site-a.com
agent-browser --session site-a snapshot

# 会话 2：浏览站点 B
agent-browser --session site-b open https://site-b.com
agent-browser --session site-b snapshot

# 列出所有活动会话
agent-browser session list

# 关闭特定会话
agent-browser --session site-a close
```

## 高级功能示例

### 示例 9：状态保持（登录会话复用）

```bash
# 首次登录流程
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "username"
agent-browser fill @e2 "password"
agent-browser click @login-btn
agent-browser wait --url "**/dashboard"

# 保存登录状态
agent-browser state save logged-in.json

# 后续会话：直接加载状态
agent-browser state load logged-in.json
agent-browser open https://app.example.com/dashboard
agent-browser snapshot -i
```

### 示例 10：网络拦截和 Mocking

```bash
# 拦截 API 响应
agent-browser network route "*/api/user*" --body '{"name": "Test User", "id": 123}'

# 拦截并中止请求
agent-browser network route "*/analytics/**" --abort

# 查看请求历史
agent-browser network requests --filter "api"

# 清除路由规则
agent-browser network unroute "*/api/user*"
```

### 示例 11：浏览器设置

```bash
# 设置视口大小（模拟移动设备）
agent-browser set viewport 375 812
agent-browser open https://example.com
agent-browser screenshot mobile-view.png

# 设置地理位置
agent-browser set geo 37.7749 -122.4194

# 模拟离线
agent-browser set offline on
agent-browser reload
agent-browser set offline off
```

### 示例 12：深度调试

```bash
# 显示浏览器窗口
agent-browser open https://example.com --headed

# 查看控制台日志
agent-browser console

# 查看页面错误
agent-browser errors

# 高亮元素以定位问题
agent-browser highlight @e1

# 记录性能追踪
agent-browser trace start trace.json
# 执行操作...
agent-browser trace stop
```

## JSON 输出示例

### 示例 13：JSON 格式解析

```bash
# 获取可解析的 JSON 输出
agent-browser snapshot -i --json > elements.json
# 输出格式：{"success":true,"data":{"snapshot":"...","refs":{...}}}

# 获取文本内容为 JSON
agent-browser get text @e1 --json

# 解析 JSON 输出（示例）
curl_path="\$data.snapshot"
content=$(jq -r "$curl_path" elements.json)
echo "$content"
```

## 错误处理示例

### 示例 14：带等待和重试的操作

```bash
# 等待元素出现
agent-browser wait @loading-spinner
agent-browser wait 1000  # 额外等待 1 秒

# 等待特定文本出现
agent-browser wait --text "Success"

# 等待网络空闲（所有请求完成）
agent-browser wait --load networkidle

# 检查元素是否可见
agent-browser is visible @result-element
```

## 完整工作流示例

### 示例 15：电商测试流程

```bash
#!/bin/bash

# 1. 打开首页
agent-browser open https://shop.example.com

# 2. 搜索商品
agent-browser snapshot -i
agent-browser fill @search-input "wireless earbuds"
agent-browser press Enter
agent-browser wait --load networkidle

# 3. 选择第一个商品
agent-browser snapshot -i
agent-browser click @product-1
agent-browser wait --load networkidle

# 4. 添加到购物车
agent-browser click @add-to-cart
agent-browser wait --text "Added to cart"

# 5. 查看购物车
agent-browser click @cart-icon
agent-browser wait --load networkidle
agent-browser get text @cart-items

# 6. 截图记录
agent-browser screenshot --full cart-full.png

# 7. 清理
agent-browser close
```

## 自动化脚本示例

### 示例 16：批量数据采集

```bash
#!/bin/bash

urls=(
  "https://example.com/page1"
  "https://example.com/page2"
  "https://example.com/page3"
)

for url in "${urls[@]}"; do
  echo "Processing: $url"

  agent-browser open "$url"
  agent-browser wait --load networkidle
  agent-browser get title
  agent-browser get text @content-area

  # 保存数据
  agent-browser screenshot "output/$(basename $url).png"

  # 添加随机延迟避免被检测
  sleep 2
done

agent-browser close
```

## 常见问题解决

### 元素定位失败

```bash
# 1. 重新获取 snapshot（页面可能已变化）
agent-browser snapshot -i

# 2. 使用语义定位器替代 refs
agent-browser find role button click --name "Submit"

# 3. 滚动元素到可见区域
agent-browser scrollintoview @e1
agent-browser click @e1

# 4. 等待元素加载
agent-browser wait @e1
agent-browser click @e1
```

### 页面加载慢

```bash
# 使用网络空闲等待
agent-browser wait --load networkidle

# 或等待特定元素出现
agent-browser wait @main-content

# 增加超时时间
agent-browser open https://slow-site.com --timeout 30000
```
