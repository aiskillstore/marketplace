# 查看当前任务

脚本：`skills/zentao-task-planner/scripts/list_tasks.py`

## 用途

查看指定任务视图，并支持汇总输出或 TSV 输出。

说明：
不同任务视图对应不同禅道端点，视图之间是互斥的，不支持在脚本内再按状态二次过滤。

## 参数

- `--view {active,assignedTo,finishedBy,closedBy}`：任务视图，默认 `active`
  - `active`：`my-task.json`，当前激活任务
  - `assignedTo`：`my-task-assignedTo.json`，指派给我的全部任务
  - `finishedBy`：`my-task-finishedBy.json`，已完成任务
  - `closedBy`：`my-task-closedBy.json`，已关闭任务
- `--summary-only`：仅输出常用字段
- `--output {json,tsv}`：输出格式，默认 `json`
- `--env-file`：技能包或本地的 `.env` 文件路径

## 示例

默认查看未关闭任务摘要：

```bash
python skills/zentao-task-planner/scripts/list_tasks.py --summary-only
```

输出 TSV：

```bash
python skills/zentao-task-planner/scripts/list_tasks.py --output tsv
```

查看指派给我的全部任务：

```bash
python skills/zentao-task-planner/scripts/list_tasks.py --view assignedTo
```

查看已完成任务：

```bash
python skills/zentao-task-planner/scripts/list_tasks.py --view finishedBy
```

查看已关闭任务：

```bash
python skills/zentao-task-planner/scripts/list_tasks.py --view closedBy
```
