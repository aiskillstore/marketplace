---
name: flow-attention-refresh
description: "注意力刷新协议。在关键时刻强制读取核心文档，防止目标遗忘。被 flow-dev, flow-ralph 等命令引用。"
---

# Flow Attention Refresh - 注意力刷新协议

## Overview

解决 "Lost in the Middle" 效应：当上下文过长时，原始目标被"推出"注意力窗口。

```
问题:
上下文开始: [原始目标 - 距离很远，被"遗忘"]
     ↓
... 50+ 工具调用 ...
     ↓
上下文末尾: [最近的工具输出 - 在注意力窗口]

解决:
在关键时刻强制读取目标文档 → 将目标"拉回"注意力窗口
```

## The Iron Law

```
BEFORE MAJOR DECISION → READ GOAL FILES → THEN ACT
```

## Refresh Protocols

### Protocol 1: Flow Entry (每个 flow-* 命令开始)

**触发点**: 任何 `/flow-*` 命令的 Entry Gate

**动作**:
```yaml
read:
  - BRAINSTORM.md "成功标准" 章节
  - TASKS.md 当前阶段任务列表
focus: 本次命令要达成什么？
```

**实现**: 已由现有 Brainstorm Alignment Check 覆盖

---

### Protocol 2: Task Start (flow-dev 每个任务开始)

**触发点**: `flow-dev` TDD 循环中，每个任务执行前

**动作**:
```yaml
read:
  - TASKS.md 当前任务 T### 段落 + DoD
  - quickstart.md 相关命令
focus: 这个任务的验收标准是什么？
```

**实现位置**: flow-dev.md 阶段 3 TDD 循环

**代码片段**:
```markdown
**注意力刷新** (Protocol 2):
→ Read: TASKS.md 当前任务 T### 段落
→ Focus: 任务目标和 DoD
→ Then: 开始执行任务
```

---

### Protocol 3: Ralph Iteration (Ralph 循环每次迭代)

**触发点**: `/flow-ralph` 每次迭代开始

**动作**:
```yaml
read:
  - TASKS.md 第一个未完成任务
  - ERROR_LOG.md 最近 5 条记录
focus: 下一步行动 + 避免重复错误
```

**实现位置**: flow-ralph.md Ralph Loop 开始处

**代码片段**:
```markdown
**注意力刷新** (Protocol 3):
→ Read: TASKS.md 找到第一个 `- [ ]` 任务
→ Read: ERROR_LOG.md 最近 5 条（如存在）
→ Focus: 下一步行动是什么？有什么错误需要避免？
→ Then: 执行任务
```

---

### Protocol 4: Error Recovery (遇到错误后)

**触发点**: 测试失败、构建错误、运行时异常后

**动作**:
```yaml
read:
  - ERROR_LOG.md 当前错误记录
  - TASKS.md 当前任务定义
focus: 错误根因 + 解决方案
```

**实现位置**: flow-tdd skill 错误处理部分

**代码片段**:
```markdown
**错误恢复刷新** (Protocol 4):
→ Record: 将错误追加到 ERROR_LOG.md
→ Read: ERROR_LOG.md 当前错误 + 历史相似错误
→ Read: TASKS.md 当前任务
→ Focus: 根因分析，避免盲目修复
→ Then: 有针对性地修复
```

---

## Integration Map

```
现有机制:
┌──────────────────────────────────────┐
│ flow-brainstorming skill             │
│ ↓ 触发于 /flow-init                  │
│ ↓ 输出 BRAINSTORM.md                 │
└──────────────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ Brainstorm Alignment Check           │
│ ↓ 在每个 flow-* Entry Gate           │
│ ↓ 读取 BRAINSTORM.md 验证对齐        │
│ ↓ = Protocol 1                       │
└──────────────────────────────────────┘

新增机制:
┌──────────────────────────────────────┐
│ flow-attention-refresh skill (本文件) │
│ ↓ 被 flow-dev, flow-ralph 引用       │
│ ↓ 在更细粒度的时刻刷新注意力          │
│ ↓ Protocol 2, 3, 4                   │
└──────────────────────────────────────┘
```

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "我记得目标是什么" | 上下文 50+ 工具调用后，你真的不记得了 |
| "读文件浪费时间" | 读文件 < 1秒，返工 > 10分钟 |
| "这个任务很简单" | 简单任务也会偏离目标 |
| "刚刚读过了" | 每次迭代都要读，这是协议 |

## Red Flags - STOP

如果你发现自己：
- 开始任务前没有读取 TASKS.md
- 遇到错误后没有先记录 ERROR_LOG.md
- Ralph 循环中忘记读取上次错误
- 做决策时没有参考 BRAINSTORM.md

**STOP。执行对应的 Protocol。**

---

**[PROTOCOL]**: 变更时更新此头部，然后检查 CLAUDE.md
