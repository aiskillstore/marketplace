---
name: context7
description: Fetch up-to-date library documentation via Context7 CLI. Use when researching external dependencies, finding implementation examples, or checking API usage for any library.
---

# Context7 - Library Documentation Fetcher

Fetch library documentation directly from the terminal using the `ctx7` CLI. Resolve any library by name and query its up-to-date docs without opening a browser.

## 执行环境

| 路径类型 | 说明 |
|---------|------|
| **CLI** | `npx ctx7` (无需全局安装) |
| **认证** | 大部分命令无需认证，`ctx7 skills generate` 需要 |
| **API Key** | 可选：`export CONTEXT7_API_KEY=your_key` |

## 工作流程

### Step 1: 解析库名 → 获取 Library ID

```bash
# 基础搜索
npx ctx7 library react

# 带自然语言查询（提高相关性）
npx ctx7 library react "How to clean up useEffect with async operations"
npx ctx7 library nextjs "How to set up app router with middleware"
npx ctx7 library prisma "How to define one-to-many relations"

# 输出 JSON 便于脚本处理
npx ctx7 library react --json | jq '.[0].id'
```

返回字段：
- **Library ID** — 格式 `/org/project`，传给 `ctx7 docs`
- **Code Snippets** — 索引的代码示例数量
- **Source Reputation** — High/Medium/Low/Unknown
- **Benchmark Score** — 0-100 质量分

### Step 2: 查询文档

```bash
# 基础查询
npx ctx7 docs /facebook/react "How to clean up useEffect with async operations"
npx ctx7 docs /vercel/next.js "How to add middleware that redirects unauthenticated users"
npx ctx7 docs /prisma/prisma "How to define one-to-many relations with cascade delete"

# 指定版本
npx ctx7 docs /vercel/next.js/v14.3.0-canary.87 "How to set up app router"

# JSON 输出
npx ctx7 docs /facebook/react "How to use hooks for state management" --json
```

⚠️ Library ID 必须以 `/` 开头，必须先用 `ctx7 library` 获取。

## 常用库参考

| 库 | Library ID | 典型查询 |
|----|-----------|---------|
| React | `/facebook/react` | hooks, state management, effects |
| Next.js | `/vercel/next.js` | app router, middleware, API routes |
| Prisma | `/prisma/prisma` | schema, relations, migrations |
| Vue | `/vuejs/core` | composition API, reactivity |
| Tailwind | `/tailwindlabs/tailwindcss` | configuration, plugins |
| Express | `/expressjs/express` | routing, middleware |
| TypeScript | `/microsoft/typescript` | generics, utility types |

## Skills 管理

```bash
# 搜索技能
npx ctx7 skills search pdf
npx ctx7 skills search react typescript

# 安装技能
npx ctx7 skills install /anthropics/skills pdf
npx ctx7 skills install /anthropics/skills --all

# 列出已安装
npx ctx7 skills list

# 生成技能（需要认证）
npx ctx7 skills generate
```

## Setup（配置 MCP）

```bash
# 交互式配置
npx ctx7 setup

# MCP 模式（IDE 集成）
npx ctx7 setup --mcp --claude
npx ctx7 setup --mcp --cursor

# CLI + Skills 模式（无需 MCP）
npx ctx7 setup --cli --universal
```

## 认证

```bash
# 登录（浏览器 OAuth）
npx ctx7 login
npx ctx7 login --no-browser  # 不打开浏览器

# 检查状态
npx ctx7 whoami

# 退出
npx ctx7 logout
```

## 高级用法

```bash
# 组合：搜索 + 获取 docs
LIB_ID=$(npx ctx7 library react "hooks" --json | jq -r '.[0].id')
npx ctx7 docs "$LIB_ID" "How to use useContext for global state"

# 管道输出
npx ctx7 docs /facebook/react "useEffect cleanup" | head -50

# 带版本的精确查询
npx ctx7 library nextjs "app router" --json | jq '.[].id' | grep v14
```

## 常见问题

| 问题 | 解决 |
|------|------|
| `Library ID must start with /` | 先运行 `ctx7 library` 获取 ID |
| 结果不相关 | 用自然语言描述具体场景，避免单词 |
| Rate limit | 登录解锁更高速率限制 |
| 无安装 | `npx ctx7` 无需安装，或 `npm install -g ctx7` |

## 参考

- 官方文档: https://context7.com/docs/clients/cli
- Skills 文档: https://context7.com/docs/skills
