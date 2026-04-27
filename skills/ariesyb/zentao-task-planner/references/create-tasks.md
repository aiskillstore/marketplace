# 创建任务

脚本：`skills/zentao-task-planner/scripts/create_tasks.py`

## 用途

根据标准化 TSV 任务表批量创建禅道任务。

## 参数

- `--plan-text`：直接传入任务列表文本
- `--plan-file`：任务列表文件路径
- `--username-mapping`：用户名映射 JSON 文本
- `--username-mapping-file`：用户名映射 JSON 文件
- `--env-file`：技能包或本地的 `.env` 文件路径
- `--execute`：实际执行创建

## 执行规则

- 默认只预览，不创建任务。
- 只有用户确认预览结果后，才能加 `--execute`。

## 示例

先预览：

```bash
python skills/zentao-task-planner/scripts/create_tasks.py --plan-file task-plan.tsv --username-mapping "{\"张三\":\"zhangsan\"}"
```

确认后执行：

```bash
python skills/zentao-task-planner/scripts/create_tasks.py --plan-file task-plan.tsv --username-mapping "{\"张三\":\"zhangsan\"}" --execute
```
