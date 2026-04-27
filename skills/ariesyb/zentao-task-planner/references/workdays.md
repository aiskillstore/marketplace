# 查询工作日

脚本：`skills/zentao-task-planner/scripts/get_next_workdays.py`

## 用途

查看当前或下一段连续工作日，用于任务规划阶段确认排期日期。

## 参数

- `--week-type {current,next}`：`current` 为当前连续工作日，`next` 为下一段连续工作日

## 示例

查看当前连续工作日：

```bash
python skills/zentao-task-planner/scripts/get_next_workdays.py --week-type current
```

查看下一段连续工作日：

```bash
python skills/zentao-task-planner/scripts/get_next_workdays.py --week-type next
```
