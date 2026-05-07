# 修复任务完成日期

脚本：`skills/zentao-task-planner/scripts/repair_task_finish_date.py`

## 用途

修复任务完成日期填错的问题。脚本会先激活任务，再把该任务历史工时记录的日期修改为任务截止日期。

## 参数

- `--task-id`：要修复的禅道任务 ID
- `--assigned-to`：激活后指派人，默认使用任务当前指派人或登录账号
- `--left`：激活时填写的剩余工时，默认 `1`
- `--comment`：激活任务时提交的备注
- `--env-file`：技能包或本地的 `.env` 文件路径
- `--execute`：实际执行修复

## 执行规则

- 默认只预览，不修改禅道。
- 预览会读取任务截止日期和历史工时记录 ID。
- 只有用户确认预览结果后，才能加 `--execute`。
- 执行时会访问 `task-recordEstimate-{taskID}.html?onlybody=yes` 获取历史工时记录，再提交 `task-editEstimate-{recordID}.html?onlybody=yes` 修改日期。

## 示例

预览：

```bash
python skills/zentao-task-planner/scripts/repair_task_finish_date.py --task-id 220603 --env-file .env
```

执行：

```bash
python skills/zentao-task-planner/scripts/repair_task_finish_date.py --task-id 220603 --assigned-to yangbiao --env-file .env --execute
```
