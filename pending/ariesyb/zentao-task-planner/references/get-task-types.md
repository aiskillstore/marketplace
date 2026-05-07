# 获取任务类型枚举

脚本：`skills/zentao-task-planner/scripts/get_task_types.py`

## 用途

从禅道"创建任务"页面解析任务类型选项，输出中文名称与英文值的映射。若动态获取失败则自动回退到内置静态映射。

## 参数

- `--env-file`：技能包或本地的 `.env` 文件路径

## 示例

获取任务类型：

```bash
python skills/zentao-task-planner/scripts/get_task_types.py
```

指定环境文件：

```bash
python skills/zentao-task-planner/scripts/get_task_types.py --env-file /path/to/.env
```
