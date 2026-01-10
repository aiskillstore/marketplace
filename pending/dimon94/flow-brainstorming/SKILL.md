---
name: flow-brainstorming
description: "在 /flow-init 阶段强制触发，用于捕捉需求的原始意图、探索方案、记录决策。确保后续流程有明确的北极星可追溯。"
---

# Flow Brainstorming - 需求头脑风暴

## Overview

将用户的模糊想法转化为清晰的设计规格，通过自然对话捕捉原始意图。

**核心原则**：需求的原始意图是整个开发流程的「北极星」，后续每个阶段都应能追溯并验证是否偏离。

## The Iron Law

```
NO FLOW EXECUTION WITHOUT BRAINSTORM ALIGNMENT
```

每个后续 flow-* 阶段开始前，必须确认与 BRAINSTORM.md 一致。

## The Process

### Phase 1: Understanding the Idea

**一次问一个问题**，不要用多个问题压垮用户：

1. 检查项目现状（文件、文档、最近提交）
2. 问问题来细化想法：
   - 优先多选题（更容易回答）
   - 一个消息只问一个问题
   - 如果话题需要更多探索，分成多个问题
3. 聚焦理解：**目的、约束、成功标准**

**问题示例**：
```
这个需求主要解决什么问题？
A) 新增功能
B) 修复现有问题
C) 性能优化
D) 重构/技术债
```

### Phase 2: Exploring Approaches

- 提出 2-3 种不同方案，说明取舍
- 给出你的推荐方案及理由
- 让用户做决策

**方案呈现格式**：
```markdown
### 方案 A: {名称} ⭐ 推荐

**描述**: ...
**优势**: ...
**劣势**: ...
**适用场景**: ...

### 方案 B: {名称}
...
```

### Phase 3: Presenting the Design

一旦理解了要构建什么：

1. 分段呈现设计（每段 200-300 字）
2. 每段后询问是否正确
3. 涵盖：架构、组件、数据流、错误处理、测试
4. 准备好返回澄清

### Phase 4: Documentation

将验证过的设计写入 BRAINSTORM.md：

```
devflow/requirements/${REQ}/BRAINSTORM.md
```

**必须包含**：
- 原始需求（用户原话，一字不改）
- 核心问题定义
- 成功标准
- 约束条件
- 方案探索（2-3种）
- 最终决策及理由

## Key Principles

| 原则 | 说明 |
|------|------|
| **一次一个问题** | 不要用多个问题压垮用户 |
| **多选题优先** | 比开放问题更容易回答 |
| **YAGNI 无情** | 从所有设计中移除不必要的功能 |
| **探索替代方案** | 在确定前总是提出 2-3 种方案 |
| **增量验证** | 分段呈现设计，验证每段 |
| **灵活应变** | 有不明白的地方就返回澄清 |

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "需求已经很清楚了" | Brainstorm 确保没有遗漏假设 |
| "用户赶时间，跳过吧" | 头脑风暴节省的是后续返工时间 |
| "这是小需求" | 小需求也有核心问题和成功标准 |
| "方案很明显" | 明显的选择也需要记录理由 |
| "已经讨论过了" | 口头讨论不是文档，没有追溯性 |
| "先做再说" | 先想清楚再做，节省 3 倍时间 |

## Red Flags - STOP

如果你发现自己：
- 跳过问问题直接开始做
- 用户说"我知道要什么"就不问了
- 没有记录方案取舍就选定
- 没有写 BRAINSTORM.md 就进入下一阶段

**STOP。返回正确流程。**

## Integration with CC-DevFlow

### flow-init 阶段

```yaml
Entry Gate:
  - 解析 REQ-ID 和标题
  - 触发 flow-brainstorming skill

Brainstorm Phase:
  1. 问问题理解需求（一次一个）
  2. 探索 2-3 种方案
  3. 确认最终方案
  4. 输出 BRAINSTORM.md

Exit Gate:
  - 验证 BRAINSTORM.md 存在
  - 验证包含必要章节
```

### 后续 flow-* 阶段

```yaml
Entry Gate 添加:
  step: Brainstorm Alignment Check
    - read: devflow/requirements/${REQ}/BRAINSTORM.md
    - verify:
        - 原始问题是否仍然是解决目标？
        - 选定方案是否仍然适用？
        - 约束条件是否发生变化？
    - if 发现偏离:
        - ask_user: "发现与原始意图偏离，是否更新 BRAINSTORM.md？"
        - action: 记录偏离原因，更新文档
```

## Output Template

参见 `.claude/docs/templates/BRAINSTORM_TEMPLATE.md`

---

**[PROTOCOL]**: 变更时更新此头部，然后检查 CLAUDE.md
