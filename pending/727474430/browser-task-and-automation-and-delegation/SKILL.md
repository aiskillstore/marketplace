---
name: browser-task-and-automation-and-delegation
description: 【强制】所有浏览器操作必须使用本技能，禁止在主对话中直接使用 mcp__chrome-devtools 工具。触发关键词：打开/访问/浏览网页、点击/填写/提交表单、截图/快照、性能分析、自动化测试、数据采集/爬取、网络模拟。本技能通过 chrome-devtools-expert agent 执行浏览器操作，避免大量页面快照、截图、网络请求数据污染主对话上下文。
---

# 浏览器自动化调度技能

本技能负责将浏览器自动化任务委派给专业的 `chrome-devtools-expert` agent 执行，通过 agent 隔离来保持主对话上下文的清晰，避免浏览器操作过程中的大量 token 消耗污染主对话。

## 核心功能

识别需要浏览器自动化操作的场景，并将任务委派给 `chrome-devtools-expert` agent，该 agent 专门使用 Chrome DevTools MCP 工具进行 Web 界面交互、自动化测试和性能分析。

## 适用场景

本技能适用于以下场景：

1. **页面导航与浏览**
   - 打开指定 URL 的网页
   - 在页面间导航（前进、后退）
   - 管理多个浏览器标签页

2. **元素交互操作**
   - 点击按钮、链接等元素
   - 悬停在元素上触发效果
   - 拖拽元素到指定位置

3. **表单填写与提交**
   - 填写输入框、文本域
   - 选择下拉菜单选项
   - 提交表单并等待响应

4. **页面截图与快照**
   - 截取整个页面或特定元素
   - 获取页面的文本快照
   - 保存截图到文件

5. **性能分析与测试**
   - 启动性能跟踪
   - 分析页面加载性能
   - 获取核心 Web 指标（CWV）

6. **自动化测试**
   - 执行功能测试流程
   - 验证页面元素状态
   - 检查控制台错误

7. **数据采集**
   - 从网页提取信息
   - 执行 JavaScript 获取数据
   - 监控网络请求

8. **网络与设备模拟**
   - 模拟不同网络条件
   - 模拟 CPU 性能限制
   - 调整页面尺寸

## 调用规则

### 1. 委派方式

使用 Task tool 调用 `chrome-devtools-expert` agent：

```
Task tool 参数：
- subagent_type: "chrome-devtools-expert"
- description: 简短描述任务（3-5个字）
- prompt: 详细的操作需求和目标
```

## 场景示例

### 示例 1：打开页面并截图

**用户需求**: "打开 example.com 并截图"

**执行方式**:
```
调用 Task tool:
- subagent_type: "chrome-devtools-expert"
- description: "打开页面并截图"
- prompt: "打开 https://example.com，等待页面加载完成后截图，将截图保存到桌面"
```

### 示例 2：表单自动化

**用户需求**: "帮我填写这个登录表单并提交"

**执行方式**:
```
调用 Task tool:
- subagent_type: "chrome-devtools-expert"
- description: "填写登录表单"
- prompt: "在当前页面找到登录表单，填写用户名'test@example.com'，密码'password123'，然后点击登录按钮，等待响应并告诉我是否成功"
```

### 示例 3：性能分析

**用户需求**: "分析这个页面的加载性能"

**执行方式**:
```
调用 Task tool:
- subagent_type: "chrome-devtools-expert"
- description: "页面性能分析"
- prompt: "对 https://example.com 进行性能分析，启动性能跟踪，刷新页面，停止跟踪，提供核心 Web 指标和性能洞察"
```

### 示例 4：自动化测试

**用户需求**: "测试购物车添加商品的功能"

**执行方式**:
```
调用 Task tool:
- subagent_type: "chrome-devtools-expert"
- description: "测试购物车功能"
- prompt: "打开商城页面，找到商品列表中的第一个商品，点击'加入购物车'按钮，然后检查购物车图标的数量是否增加，验证功能是否正常"
```

### 示例 5：数据采集

**用户需求**: "从这个页面提取所有产品标题"

**执行方式**:
```
调用 Task tool:
- subagent_type: "chrome-devtools-expert"
- description: "提取产品标题"
- prompt: "从当前页面使用 JavaScript 提取所有产品标题，返回一个标题列表"
```

### 示例 6：网络条件测试

**用户需求**: "在慢速 3G 网络下测试页面加载"

**执行方式**:
```
调用 Task tool:
- subagent_type: "chrome-devtools-expert"
- description: "慢速网络测试"
- prompt: "设置网络模拟为 Slow 3G，打开 https://example.com，记录页面加载时间和用户体验，然后恢复正常网络"
```

### 示例 7：多步骤操作

**用户需求**: "打开网站，登录，然后导航到设置页面并截图"

**执行方式**:
```
调用 Task tool:
- subagent_type: "chrome-devtools-expert"
- description: "登录并截图设置页"
- prompt: "1) 打开 https://example.com
2) 填写登录表单（用户名：test@example.com，密码：password123）并提交
3) 等待登录成功
4) 点击导航栏的'设置'链接
5) 等待设置页面加载完成
6) 截取设置页面的完整截图并保存"
```

## 执行原则

1. **自动识别**: 当判断需要浏览器操作时，自动激活本技能
2. **快速委派**: 不在主对话中尝试浏览器操作，直接委派给专业 agent
3. **上下文隔离**: 将大量的浏览器输出数据隔离在 agent 上下文中
4. **结果精简**: agent 只返回关键操作结果，过滤冗余信息
5. **效率优先**: agent 会采用最优策略执行浏览器操作，最小化 token 消耗

通过本技能，主 agent 可以高效地将浏览器自动化任务委派给专业 agent，保持对话流程清晰，优化 token 使用。
