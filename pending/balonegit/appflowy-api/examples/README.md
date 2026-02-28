# 示例

以下示例使用仓库内置的 UTF-8 模板，适合演示与测试。

## 健身计划文档（Grid）
```bash
python skills/appflowy-api/scripts/appflowy_skill.py apply-grid \
  --config skills/appflowy-api/references/config.example.json \
  --email <email> --password <password> \
  --workspace-id <workspace_id> --view-id <view_id> \
  --template-file skills/appflowy-api/references/templates/fitness_plan.example.json
```

## 用户管理系统文档（就地修正 + Grid）
```bash
python skills/appflowy-api/scripts/appflowy_skill.py update-user-management-doc \
  --config skills/appflowy-api/references/config.example.json \
  --email <email> --password <password> \
  --workspace-id <workspace_id> --view-id <view_id>
```

## 通用 Grid 模板
```bash
python skills/appflowy-api/scripts/appflowy_skill.py apply-grid \
  --config skills/appflowy-api/references/config.example.json \
  --email <email> --password <password> \
  --workspace-id <workspace_id> --view-id <view_id> \
  --template-file skills/appflowy-api/references/templates/grid_plan.example.json
```
