---
name: techdoc-search-and-orchestrate
description: 【强制】所有技术文档查询必须使用本技能，禁止在主对话中直接使用 mcp__context7-mcp 工具。触发关键词：查询/学习/了解某个库或框架的文档、API用法、配置参数、错误解释、版本差异、代码示例、最佳实践。本技能通过 context7-researcher agent 执行查询，避免大量文档内容污染主对话上下文，保持 token 效率。
---

# 技术文档查询调度技能

本技能负责将技术文档查询任务委派给专业的 `context7-researcher` agent 执行，通过 agent 隔离来保持主对话上下文的清晰，避免 token 消耗污染。

## 核心功能

识别需要技术文档查询的场景，并将任务委派给 `context7-researcher` agent，该 agent 专门使用 Context7 MCP 工具检索最新的技术文档。

## 适用场景

当需要查询技术文档时，本技能负责将任务委派给 `context7-researcher` agent 执行，避免技术文档检索过程污染主对话上下文。

## 调用规则

### 1. 委派方式

使用 Task tool 调用 `context7-researcher` agent：

```
Task tool 参数：
- subagent_type: "context7-researcher"
- description: 简短描述任务（3-5个字）
- prompt: 详细的查询需求
```

### 2. 任务编排策略

当有多个技术文档查询需求时，可以选择以下两种方式：

**方式一：顺序执行（单 Agent 多任务）**
- 调用 1 个 `context7-researcher` agent
- 在 prompt 中列出多个查询任务
- Agent 按顺序依次完成所有任务
- **优点**：简单直接，适合任务间有关联的场景
- **缺点**：速度较慢，需要等待所有任务顺序完成

**方式二：并行执行（多 Agent 并行）**
- 同时调用多个 `context7-researcher` agents
- 每个 agent 分配 1 个或多个任务
- 所有 agents 并行工作
- **优点**：速度快，多个查询同时进行
- **缺点**：编排稍复杂

**选择建议**：
- **默认策略**：尽可能拆分查询主题，使用并行执行，速度更快
- **顺序执行**：仅当查询任务有强依赖关系（必须先查出答案 A 才能查询问题 B）时使用
- 主 agent 应理解用户需求，判断任务是否可拆分为独立主题

**示例对比**：

用户问："帮我查询 Supabase 的 realtime 如何对接和 Supabase 的 JS SDK 如何使用"

顺序执行方式：
```
调用 1 个 agent:
- subagent_type: "context7-researcher"
- description: "查询 Supabase 文档"
- prompt: "请完成以下查询：
  1. 查询 Supabase realtime 的对接方法和示例
  2. 查询 Supabase JS SDK 的使用方法和示例"
```

并行执行方式（**推荐**）：
```
同时调用 2 个 agents:

Agent 1:
- subagent_type: "context7-researcher"
- description: "查询 Supabase realtime"
- prompt: "查询 Supabase realtime 的对接方法和示例"

Agent 2:
- subagent_type: "context7-researcher"
- description: "查询 Supabase SDK"
- prompt: "查询 Supabase JS SDK 的使用方法和示例"
```

这两个查询虽然都关于 Supabase，但是独立的主题（一个是 realtime 功能，一个是 SDK 使用），没有强依赖关系，**应该优先选择并行执行**以提高效率。

## 场景示例

### 示例 1：单一 API 查询

**用户需求**: "Supabase 怎么实现用户注册？"

**执行方式**:
```
调用 Task tool:
- subagent_type: "context7-researcher"
- description: "查询 Supabase 用户注册"
- prompt: "查询 Supabase 的用户注册 API 用法，包括代码示例"
```

### 示例 2：多个独立查询

**用户需求**: "Next.js 的 App Router 怎么配置和 Server Actions 如何使用？"

**执行方式**:
```
并行调用 2 个 agents（推荐）:

Agent 1:
- subagent_type: "context7-researcher"
- description: "查询 App Router 配置"
- prompt: "查询 Next.js App Router 的配置方法和示例"

Agent 2:
- subagent_type: "context7-researcher"
- description: "查询 Server Actions"
- prompt: "查询 Next.js Server Actions 的使用方法和示例"
```

**说明**: 虽然都是 Next.js 的功能，但 App Router 配置和 Server Actions 是两个独立主题，没有强依赖，应优先并行查询。

### 示例 3：强依赖查询（顺序执行）

**用户需求**: "我的 Next.js 项目报错 'Error: ENOENT: no such file or directory'，这是什么原因？怎么解决？"

**执行方式**:
```
调用 1 个 agent 顺序执行:
- subagent_type: "context7-researcher"
- description: "排查 Next.js 错误"
- prompt: "请按顺序完成：
  1. 先查询 Next.js 中 'ENOENT: no such file or directory' 错误的常见原因
  2. 根据查到的原因，再查询对应的解决方案和最佳实践"
```

**说明**: 这是典型的强依赖场景，必须先了解错误原因，才能针对性地查询解决方案，因此使用顺序执行。

### 示例 4：单一复杂查询

**用户需求**: "Next.js 13 和 14 的路由有什么区别？"

**执行方式**:
```
调用 Task tool:
- subagent_type: "context7-researcher"
- description: "对比 Next.js 路由差异"
- prompt: "对比 Next.js 13 和 14 版本的路由系统差异，说明主要变更"
```

**说明**: 这是单一查询任务，无需拆分，直接委派给一个 agent 执行。

## 执行原则

1. **自动识别**: 当判断需要技术文档信息时，自动激活本技能
2. **快速委派**: 不在主对话中尝试查询，直接委派给专业 agent
3. **保持清洁**: 避免技术文档检索过程污染主对话上下文
4. **灵活编排**: 根据任务特点选择顺序或并行执行方式

通过本技能，主 agent 可以高效地将技术文档查询委派给专业 agent，保持对话流程清晰，优化 token 使用。
