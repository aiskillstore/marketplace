---
name: zentao-task-planner
description: Plan Zentao tasks, and perform Zentao operations including creating tasks, logging work hours, and completing tasks.规划禅道任务，以及对禅道操作，创建任务、录入工时、完成任务。
---

## Overview

You need to plan, clarify, standardize, and confirm tasks so that users can input all relevant information at once. Workdays can be queried via scripts, and then scripts can be used to operate Zentao.

## 脚本
### 普通脚本
- `get_next_workdays.py` 用于查询当前或下一段连续工作日，在规划阶段使用，一般情况下是规划本周或者下周工作日的任务。

### 禅道脚本
- `get_task_types.py` 从禅道页面获取任务类型枚举
- `list_tasks.py` 查看用户当前任务列表
- `create_tasks.py` 创建任务，只能在任务表确认后使用
- `finish_tasks_by_date.py` 按日期范围批量完成任务
- `repair_task_finish_date.py` 修复任务填错的完成日期
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
- [references/get-task-types.md](references/get-task-types.md)：获取任务类型枚举
- [references/create-tasks.md](references/create-tasks.md)：批量创建任务
- [references/finish-tasks.md](references/finish-tasks.md)：按日期完成任务
- [references/repair-finish-date.md](references/repair-finish-date.md)：修复任务完成日期
- [references/close-tasks.md](references/close-tasks.md)：关闭已完成任务
- `scripts/zentao_common.py`：本技能内部实现逻辑，通常无需直接阅读
