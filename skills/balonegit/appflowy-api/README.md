# AppFlowy API Skill

用于自托管 AppFlowy 的 API 调用与自动化：登录获取 token、文档/视图/数据库操作、搜索、协作数据更新等。

当前发布版本：`0.3.0`（详见 `references/v0.3_release_notes.md`）

## 入口方式
本技能提供两类入口：
1. **单脚本入口**：直接运行某个脚本，如 `python scripts/doctor.py ...`  
   - 优点：脚本即文档，参数最清晰  
   - 适合：脚本级调试、精细控制
2. **统一入口**：`python scripts/appflowy_skill.py <command> ...`  
   - 优点：命令风格统一、便于上层工具封装  
   - 适合：自动化流程、对外集成

查看统一入口可用命令：
```bash
python skills/appflowy-api/scripts/appflowy_skill.py list
```

查看某个命令帮助：
```bash
python skills/appflowy-api/scripts/appflowy_skill.py help apply-grid
python skills/appflowy-api/scripts/appflowy_skill.py help database-query
python skills/appflowy-api/scripts/appflowy_skill.py help page-get-tree
python skills/appflowy-api/scripts/appflowy_skill.py help page-get-blocks
python skills/appflowy-api/scripts/appflowy_skill.py help page-delete-blocks
python skills/appflowy-api/scripts/appflowy_skill.py help rename-db-field
python skills/appflowy-api/scripts/appflowy_skill.py help delete-db-field
python skills/appflowy-api/scripts/appflowy_skill.py help bulk-upsert-rows
python skills/appflowy-api/scripts/appflowy_skill.py help schema-diff
python skills/appflowy-api/scripts/appflowy_skill.py help schema-migration-plan
python skills/appflowy-api/scripts/appflowy_skill.py help apply-schema-migration
python skills/appflowy-api/scripts/appflowy_skill.py help render-template
python skills/appflowy-api/scripts/appflowy_skill.py help repair-runner
python skills/appflowy-api/scripts/appflowy_skill.py help snapshot-collab
python skills/appflowy-api/scripts/appflowy_skill.py help rollback-collab
```

## 结构
- `SKILL.md`：技能说明（供 Codex/Claude/OpenClaw 读取）
- `scripts/`：可复用脚本与通用库
- `references/`：API 参考与模板文件（UTF-8）
- `references/v0.3_release_notes.md`：v0.3.0 发布说明
- `APPFLOWY_SKILL_CAPABILITY_MATRIX_AND_ROADMAP.md`：能力矩阵与版本路线图（任务进度跟踪）
- `examples/`：示例命令与用法

## 快速示例
```bash
# 自检
python skills/appflowy-api/scripts/appflowy_skill.py doctor --config skills/appflowy-api/references/config.example.json --email <email> --password <password>

# 应用 Grid 模板（就地修改）
python skills/appflowy-api/scripts/appflowy_skill.py apply-grid --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --view-id <view_id> --template-file skills/appflowy-api/references/templates/fitness_plan.example.json
python skills/appflowy-api/scripts/appflowy_skill.py apply-grid --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --view-id <view_id> --template-file skills/appflowy-api/references/templates/grid_plan.with_vars.example.json --vars-file skills/appflowy-api/references/templates/grid_plan.vars.example.json

# 删除行（通过 collab 更新 row_orders）
python skills/appflowy-api/scripts/appflowy_skill.py delete-rows --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --row-ids <row_id_1,row_id_2>

# 查询数据库（推荐 query-file）
python skills/appflowy-api/scripts/appflowy_skill.py database-query --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --query-file .tmp/db_query.json

# 读取页面树
python skills/appflowy-api/scripts/appflowy_skill.py page-get-tree --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --depth 3 --compact

# 读取页面 block（树形 / 扁平）
python skills/appflowy-api/scripts/appflowy_skill.py page-get-blocks --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --view-id <view_id>
python skills/appflowy-api/scripts/appflowy_skill.py page-get-blocks --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --view-id <view_id> --flat

# 删除页面 block（支持 dry-run）
python skills/appflowy-api/scripts/appflowy_skill.py page-delete-blocks --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --view-id <view_id> --block-id <block_id> --dry-run
python skills/appflowy-api/scripts/appflowy_skill.py page-delete-blocks --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --view-id <view_id> --block-id <block_id>

# 字段改名（支持 field_id / field_name）
python skills/appflowy-api/scripts/appflowy_skill.py rename-db-field --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --field-id <field_id> --new-name <new_name> --dry-run
python skills/appflowy-api/scripts/appflowy_skill.py rename-db-field --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --field-id <field_id> --new-name <new_name>

# 字段删除（默认 dry-run，执行需 --execute --yes）
python skills/appflowy-api/scripts/appflowy_skill.py delete-db-field --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --field-id <field_id>
python skills/appflowy-api/scripts/appflowy_skill.py delete-db-field --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --field-id <field_id> --execute --yes

# 批量 upsert 行（输出新增/更新/失败摘要）
python skills/appflowy-api/scripts/appflowy_skill.py bulk-upsert-rows --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --rows-file .tmp/rows.json --pre-hash-prefix biz --dry-run
python skills/appflowy-api/scripts/appflowy_skill.py bulk-upsert-rows --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --rows-file .tmp/rows.json --pre-hash-prefix biz

# v0.3 M1：schema diff（仅分析差异）
python skills/appflowy-api/scripts/appflowy_skill.py schema-diff --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --target-template-file skills/appflowy-api/references/templates/fitness_plan.example.json
python skills/appflowy-api/scripts/appflowy_skill.py schema-diff --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --target-database-id <target_database_id>

# v0.3 M1：migration plan（仅输出计划，不执行）
python skills/appflowy-api/scripts/appflowy_skill.py schema-migration-plan --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --target-template-file skills/appflowy-api/references/templates/fitness_plan.example.json
python skills/appflowy-api/scripts/appflowy_skill.py schema-migration-plan --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --target-database-id <target_database_id> --rename-apply-threshold 0.80

# v0.3 M2：应用 migration（默认 dry-run）
python skills/appflowy-api/scripts/appflowy_skill.py apply-schema-migration --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --target-template-file skills/appflowy-api/references/templates/fitness_plan.example.json
python skills/appflowy-api/scripts/appflowy_skill.py apply-schema-migration --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --plan-file .tmp/migration_plan.json

# v0.3 M2：执行 migration（高风险需显式放行）
python skills/appflowy-api/scripts/appflowy_skill.py apply-schema-migration --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --plan-file .tmp/migration_plan.json --execute --yes --allow-high-risk --allow-delete-fields

# v0.3 M3：模板渲染（vars 注入）
python skills/appflowy-api/scripts/appflowy_skill.py render-template --template-file skills/appflowy-api/references/templates/grid_plan.with_vars.example.json --vars-file skills/appflowy-api/references/templates/grid_plan.vars.example.json --output-file .tmp/grid_plan.rendered.json

# v0.3 M3：修复器框架（默认 dry-run）
python skills/appflowy-api/scripts/appflowy_skill.py repair-runner --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --template-file skills/appflowy-api/references/templates/fitness_plan.example.json
python skills/appflowy-api/scripts/appflowy_skill.py repair-runner --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --template-file .tmp/grid_plan.rendered.json --repair ensure-template-fields --repair repair-select-options --execute --yes

# v0.3 M4：快照与回滚
python skills/appflowy-api/scripts/appflowy_skill.py snapshot-collab --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id>
python skills/appflowy-api/scripts/appflowy_skill.py rollback-collab --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --snapshot-file .tmp/snapshots/<snapshot>.json
python skills/appflowy-api/scripts/appflowy_skill.py rollback-collab --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --snapshot-file .tmp/snapshots/<snapshot>.json --execute --yes
```

> 约定：`SingleSelect`/`MultiSelect` 行值请使用选项名称，不要直接提交 `selected_option_ids`。
>
> 兼容性：`database-query` 读取 `--query-file` 时支持 UTF-8 与 UTF-8 BOM（Windows PowerShell 默认 UTF-8 输出可直接使用）。
>
> 保护策略：`delete-db-field` 默认不执行删除（dry-run），并且禁止删除主字段。
>
> 统一输出：M3 起删除类/批量命令会返回 `change_report`，包含 `before`/`plan`/`after`/`summary` 四段。
>
> v0.3 补充：`schema-diff` 与 `schema-migration-plan` 也输出 `change_report`，其中 `rename_candidates` 仅为建议，不直接作为执行依据。
>
> v0.3 M2 补充：`apply-schema-migration` 默认 `dry-run`；执行必须 `--execute --yes`。高风险操作需额外传 `--allow-high-risk`，删除字段还需 `--allow-delete-fields`。
>
> 编码兼容：`--plan-file` 支持 UTF-8 / UTF-8 BOM / UTF-16（PowerShell `>` 重定向文件可直接读取）。
>
> v0.3 M3 补充：`render-template` 与 `repair-runner` 会自动生成 `audit_log`，默认写入 `.tmp/audit_logs/`。
>
> v0.3 M4 补充：`snapshot-collab` 对 database 会额外保存 `database_schema_fields`，`rollback-collab` 在 auto 模式下优先使用 `schema-database` 策略回滚。
>
> 回归记录：`references/v0.2_m1_regression.md`、`references/v0.2_m2_regression.md`、`references/v0.2_m3_regression.md`、`references/v0.2_m4_regression.md`、`references/v0.3_m1_regression.md`、`references/v0.3_m2_regression.md`、`references/v0.3_m3_regression.md`、`references/v0.3_m4_regression.md`。
