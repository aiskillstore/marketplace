# 关闭已完成任务

脚本：`skills/zentao-task-planner/scripts/close_finished_tasks.py`

## 用途

预览或关闭已完成但未关闭的禅道任务。

## 参数

- `--comment`：关闭备注
- `--env-file`：技能包或本地的 `.env` 文件路径
- `--execute`：实际执行关闭

## 执行规则

- 默认只预览，不关闭任务。
- 只有用户确认预览结果后，才能加 `--execute`。

## 示例

预览：

```bash
python skills/zentao-task-planner/scripts/close_finished_tasks.py
```

执行：

```bash
python skills/zentao-task-planner/scripts/close_finished_tasks.py --execute
```
