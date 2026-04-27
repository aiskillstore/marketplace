---
name: zentao-task-planner
description: 规划禅道任务，以及对禅道操作，创建任务、录入工时、完成任务。
---

## 概述

你需要对任务进行规划、澄清、标准化和确认，让用户一次性输入相关信息，工作日可以调用脚本查询，随后可以调用脚本操作禅道。

## 脚本
### 普通脚本
- `get_next_workdays.py` 用于查询当前或下一段连续工作日，在规划阶段使用，一般情况下是规划本周或者下周工作日的任务。

### 禅道脚本
- `list_tasks.py` 查看用户当前任务列表
- `create_tasks.py` 创建任务，只能在任务表确认后使用
- `finish_tasks_by_date.py` 按日期范围批量完成任务
- `close_finished_tasks.py` 关闭已完成但未关闭的任务

### 脚本执行规则

1. 未经用户明确确认，不要执行有副作用的禅道操作。
2. 脚本用法、参数、命令示例统一以 [references/commands.md](references/commands.md) 及其分脚本文档为准。
3. 不要为了了解脚本怎么用而直接通读源码。

## 资源

- [references/plan-task.md](references/plan-task.md)：规划任务规则说明
- [references/commands.md](references/commands.md)：命令索引、环境要求、公共执行规则
- [references/workdays.md](references/workdays.md)：查询连续工作日
- [references/list-tasks.md](references/list-tasks.md)：查看任务列表
- [references/create-tasks.md](references/create-tasks.md)：批量创建任务
- [references/finish-tasks.md](references/finish-tasks.md)：按日期完成任务
- [references/close-tasks.md](references/close-tasks.md)：关闭已完成任务
- `scripts/zentao_common.py`：本技能内部实现逻辑，通常无需直接阅读
