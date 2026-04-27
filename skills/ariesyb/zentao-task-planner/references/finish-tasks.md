# 批量完成任务

脚本：`skills/zentao-task-planner/scripts/finish_tasks_by_date.py`

## 用途

按日期范围预览或批量完成禅道任务。

## 参数

- `--start-date`：开始日期，格式 `YYYY-MM-DD`
- `--end-date`：结束日期，默认等于开始日期
- `--date-field {range,estStarted,deadline}`：筛选依据字段
- `--statuses`：允许处理的状态列表，逗号分隔
- `--comment`：完成备注
- `--env-file`：技能包或本地的 `.env` 文件路径
- `--execute`：实际执行完成

## 执行规则

- 默认只预览，不完成任务。
- 只有用户确认预览结果后，才能加 `--execute`。

## 示例

预览：

```bash
python skills/zentao-task-planner/scripts/finish_tasks_by_date.py --start-date 2026-04-20
```

执行：

```bash
python skills/zentao-task-planner/scripts/finish_tasks_by_date.py --start-date 2026-04-20 --execute
```
