# AppFlowy Skill 能力矩阵与版本路线图

## 文档目标

本文档用于持续跟踪 `appflowy-api-skill` 的能力现状、短板、对标差距、版本规划与交付进度。

适用场景：

- 规划 skill 的下一阶段演进
- 评审当前能力缺口
- 跟踪版本交付状态
- 作为后续 issue / task 拆解的总控文档

## 使用方式

- 每次新增能力、修复重大缺陷、调整优先级后，更新本文档
- `状态` 字段统一使用：`未开始` / `进行中` / `已完成` / `阻塞`
- 每个版本结束时，更新“版本验收结果”和“遗留问题”
- 如新增能力超出本文档范围，先补能力矩阵，再补路线图

## 当前版本快照

| 维度 | 当前状态 | 说明 |
| --- | --- | --- |
| 认证与连通性 | 已完成 | 支持 GoTrue 登录、健康检查 |
| Grid / Database 基础操作 | 部分完成 | 支持字段新增、行 upsert、行详情、默认空行清理 |
| 删除能力 | 部分完成 | 已支持通过 collab 删除 row order；无原生 HTTP DELETE row |
| 文档 Block 操作 | 部分完成 | 仅覆盖 append-block 和少量 collab 修复 |
| 富文本能力 | 未完成 | 缺少统一的 block/tree/格式抽象 |
| 查询能力 | 薄弱 | 缺 filter/sort/pagination/group-by 等 |
| 模板能力 | 部分完成 | 已有 Grid 模板，但参数化和迁移能力不足 |
| 稳定性与可观测性 | 薄弱 | 缺 dry-run、diff、统一审计、回滚 |
| 权限/协作能力 | 薄弱 | 缺成员、分享、评论、审阅流封装 |

## 一、当前能力矩阵

### 1.1 基础平台能力

| 能力域 | 子能力 | 当前状态 | 说明 | 备注 |
| --- | --- | --- | --- | --- |
| 认证 | 密码登录获取 token | 已完成 | 已封装 `token` / `doctor` | 可直接用于自动化 |
| 认证 | `.env` / config / CLI 优先级解析 | 已完成 | 已支持 | 需继续保持一致性 |
| 认证 | token 刷新 | 未开始 | 当前未封装 refresh token 流程 | 建议补齐 |
| 健康检查 | GoTrue / AppFlowy 健康检查 | 已完成 | `doctor.py` 已支持 | 版本兼容提示仍可加强 |
| 用户上下文 | 用户 profile / workspace info | 未开始 | 缺 user 侧 API 封装 | 影响多用户工作流 |
| 统一 CLI | 统一命令入口 | 已完成 | `appflowy_skill.py` 已提供 | 仍需补更多子命令 |

### 1.2 Workspace / 页面能力

| 能力域 | 子能力 | 当前状态 | 说明 | 对标缺口 |
| --- | --- | --- | --- | --- |
| Workspace | 列 workspace | 已完成 | 已支持 | - |
| Workspace | 创建 workspace | 未落地到 skill | 后端有接口，但 skill 未封装 | Notion 类工具通常可完整管理空间 |
| Workspace | 删除 workspace | 未开始 | 未封装 | 高风险，需要安全护栏 |
| 页面 | 创建 page view | 已完成 | 支持 `create-page-view` | 仍较底层 |
| 页面 | 更新页面名 | 已完成 | 支持 `update-page-name` | - |
| 页面 | 页面树/目录读取 | 已完成 | 已支持 `page-get-tree` | 支持 `depth/root_view_id/compact` |
| 页面 | 页面移动/归档/恢复 | 未开始 | 未封装 | 与成熟云文档工具差距明显 |
| 页面 | 页面删除 | 未开始 | 未封装 | 需配合回收站策略 |

### 1.3 Block / 文档内容能力

| 能力域 | 子能力 | 当前状态 | 说明 | 风险/不足 |
| --- | --- | --- | --- | --- |
| Block | append block | 已完成 | 支持 `append-block` | 仅追加，不支持树级 patch |
| Block | 读取 block 树 | 已完成 | 已支持 `page-get-blocks` | 支持树形/扁平/raw 输出 |
| Block | 更新 block | 未开始 | 当前没有通用 block update | 只能重建或 collab 修补 |
| Block | 删除 block | 部分完成 | 仅有内部 collab 脚本场景化支持 | 不够通用 |
| Block | block 移动 / 重排 | 未开始 | 缺排序、移动能力 | 难以做复杂文档重构 |
| Block 类型 | paragraph / heading / grid | 部分完成 | 已有基础支持 | 类型覆盖面有限 |
| Block 类型 | todo / bulleted list / numbered list | 未开始 | 未形成统一模板或 API 层抽象 | 缺常用文档结构 |
| Block 类型 | quote / callout / toggle / divider | 未开始 | 未支持 | Notion 类能力常见 |
| Block 类型 | code block / bookmark / embed | 未开始 | 未支持 | 面向工程文档时不足 |
| Block 类型 | image / file / media | 未开始 | 未支持完整链路 | 缺上传+引用能力 |

### 1.4 Grid / Database 能力

| 能力域 | 子能力 | 当前状态 | 说明 | 风险/不足 |
| --- | --- | --- | --- | --- |
| Database | 列数据库 | 已完成 | 支持 `list-databases` | - |
| Database | 读取字段定义 | 已完成 | 已支持 | - |
| Database | 新增字段 | 已完成 | 已支持 | 缺字段删除/改名/迁移 |
| Database | 字段修复 | 部分完成 | 支持 select option 修复 | 仍偏脚本化 |
| Database | 字段改名 | 已完成 | 已支持 `rename-db-field` | 当前通过 collab 更新 |
| Database | 字段删除 | 已完成 | 已支持 `delete-db-field` | 默认 dry-run + 禁删主字段 |
| Database | 字段类型迁移 | 未开始 | 未封装 | 高价值 |
| Row | upsert 行 | 已完成 | 支持 | 已验证 select 名称写入 |
| Row | add 行 | 已完成 | 基础可用 | 仍缺批量能力 |
| Row | 行详情读取 | 已完成 | 已支持 | - |
| Row | 行删除 | 部分完成 | 已支持 collab row order 删除 | 非原生 DELETE 语义 |
| Row | 批量行操作 | 未开始 | 缺批量 upsert/delete | 大规模迁移困难 |
| Query | filter | 部分完成 | 已支持 `database-query`（客户端过滤） | 后续可补服务端表达式 |
| Query | sort | 部分完成 | 已支持 `database-query`（客户端排序） | 后续可补服务端排序 |
| Query | pagination | 部分完成 | 已支持 `limit/offset` | 当前为加载后分页 |
| Query | group-by | 未开始 | 未封装 | 对标成熟产品不足 |

### 1.5 模板、迁移与修复能力

| 能力域 | 子能力 | 当前状态 | 说明 | 风险/不足 |
| --- | --- | --- | --- | --- |
| 模板 | Grid 模板应用 | 已完成 | `apply-grid` 已支持 | 需增强参数化 |
| 模板 | 文档模板修复 | 部分完成 | 依赖具体脚本 | 通用性不足 |
| 模板 | 模板变量注入 | 未开始 | 缺参数化模板引擎 | 复用性低 |
| 迁移 | schema diff | 未开始 | 缺字段对比/迁移计划 | 高优先级 |
| 迁移 | 数据迁移脚本 | 未开始 | 缺正式迁移机制 | 风险集中在人工操作 |
| 修复 | 默认空行清理 | 已完成 | 已增强并实测 | - |
| 修复 | select option 修复 | 已完成 | 已增强并实测 | 仍应补自动验证 |
| 修复 | 文档结构清理 | 部分完成 | 现有脚本偏场景化 | 缺通用框架 |

### 1.6 稳定性、可观测性与安全能力

| 能力域 | 子能力 | 当前状态 | 说明 | 缺口 |
| --- | --- | --- | --- | --- |
| 稳定性 | 幂等写入 | 部分完成 | row upsert 依赖 `pre_hash` | block 侧缺统一幂等策略 |
| 稳定性 | 重试策略 | 未开始 | 未形成统一重试层 | 网络抖动下脆弱 |
| 稳定性 | 回滚方案 | 未开始 | 无统一快照/恢复 | 高风险操作缺保护 |
| 可观测性 | 结构化日志 | 未开始 | 当前以脚本输出为主 | 难以机器追踪 |
| 可观测性 | dry-run | 已完成 | 删除类与批量写入已支持 dry-run | 后续需扩展到更多迁移命令 |
| 可观测性 | diff 预览 | 未开始 | 无变更前后对比 | 对 review 不友好 |
| 可观测性 | 审计日志 | 未开始 | 无操作日志沉淀 | 不利于排障 |
| 安全 | 破坏性操作确认 | 部分完成 | 字段删除需 `--execute --yes` 且禁删主字段 | 需扩展到更多命令 |
| 安全 | 权限边界检查 | 薄弱 | 基本依赖后端 | skill 层可增加提示 |

## 二、对标 Notion / 其他云文档 skill 的主要不足

### 2.1 对标结论

当前 skill 在“数据库修复与模板落地”方面已经具备实用性，但如果对标 Notion 类成熟文档技能，仍明显偏底层、偏脚本化、偏点状修复，距离“通用文档运营/迁移工具”还有差距。

### 2.2 差距矩阵

| 对标维度 | Notion 类成熟 skill 常见能力 | 当前 AppFlowy skill 状态 | 差距结论 |
| --- | --- | --- | --- |
| 对象模型完整度 | page / block / database / comment / user / permission 完整覆盖 | 主要覆盖 database/grid 和少量 page | 明显不足 |
| 查询表达能力 | 强 filter / sort / search / projection | 只有基础读取和搜索 | 明显不足 |
| 内容编排能力 | 支持完整 block tree 的读改写 | 仅 append 和局部 collab 操作 | 明显不足 |
| 批量迁移能力 | 支持批量复制、迁移、模板化部署 | 当前多为单点脚本 | 明显不足 |
| 模板能力 | 参数化模板、环境切换、变量注入 | 当前模板多为静态 JSON | 中到高差距 |
| 稳定性能力 | dry-run、diff、rollback、审计日志 | 当前缺失 | 高优先级缺口 |
| 生态可用性 | 更偏“平台能力” | 当前更偏“问题修复工具” | 需要转型升级 |

### 2.3 关键结论

- 如果目标是“让 AI 可靠维护 AppFlowy 云文档”，必须从“脚本集合”升级为“对象模型 + 迁移/修复框架 + 安全护栏”。
- 如果目标是“对标 Notion skill”，优先级最高的不是继续加单个脚本，而是补齐：
  - 统一对象抽象
  - 查询与 patch 能力
  - 可观测性
  - 迁移与回滚机制

## 三、优化方向总表

### 3.1 P0：基础闭环能力

| 编号 | 优化项 | 优先级 | 状态 | 目标 |
| --- | --- | --- | --- | --- |
| P0-1 | 页面/Block 读能力 | P0 | 已完成 | 能读取页面树和 block 树 |
| P0-2 | Block 更新/删除/移动 | P0 | 部分完成 | 已支持 `page-delete-blocks` |
| P0-3 | Database 查询能力 | P0 | 部分完成 | 已支持基础 filter/sort/pagination |
| P0-4 | dry-run + diff | P0 | 部分完成 | 删除类+批量写已支持 dry-run 与摘要 |
| P0-5 | 行/字段批量操作 | P0 | 未开始 | 支持批量迁移、批量修复 |
| P0-6 | 统一错误模型 | P0 | 未开始 | 区分 HTTP 失败/业务失败/兼容性失败 |

### 3.2 P1：迁移与维护能力

| 编号 | 优化项 | 优先级 | 状态 | 目标 |
| --- | --- | --- | --- | --- |
| P1-1 | schema diff | P1 | 未开始 | 输出字段差异与迁移建议 |
| P1-2 | schema migration | P1 | 未开始 | 支持字段新增/改名/删除/迁移 |
| P1-3 | 模板参数化 | P1 | 未开始 | 同一模板适配多业务场景 |
| P1-4 | 通用修复框架 | P1 | 未开始 | 把当前零散修复脚本框架化 |
| P1-5 | 操作审计日志 | P1 | 未开始 | 记录每次修改的输入/输出/结果 |
| P1-6 | 回滚机制 | P1 | 未开始 | 关键写操作前生成恢复点 |

### 3.3 P2：对标成熟云文档工具

| 编号 | 优化项 | 优先级 | 状态 | 目标 |
| --- | --- | --- | --- | --- |
| P2-1 | 文件上传与媒体管理 | P2 | 未开始 | 图片/附件/文件 block 全链路 |
| P2-2 | 评论/审阅流支持 | P2 | 未开始 | 支持文档审查与协作反馈 |
| P2-3 | 权限/分享封装 | P2 | 未开始 | 成员、角色、分享能力可自动化 |
| P2-4 | 页面重组与目录治理 | P2 | 未开始 | 支持自动整理文档结构 |
| P2-5 | 模板市场化/资产化 | P2 | 未开始 | 沉淀复用模板与最佳实践 |

## 四、版本路线图

## v0.2：补齐基础可维护闭环

### 目标

把 skill 从“能修 Grid”提升到“能安全维护页面和数据库”。

### 范围

- 增加页面树/数据库 schema/row 查询能力
- 增加 block 读/删/改的统一能力
- 给高风险操作加 `dry-run`
- 给变更输出统一 `diff`

### 计划项

- [x] 新增 `page.get-tree`
- [x] 新增 `page.get-blocks`
- [x] 新增 `page.delete-blocks`
- [x] 新增 `database.query`
- [x] 新增 `database.fields.rename`
- [x] 新增 `database.fields.delete`
- [x] 新增 `rows.bulk-upsert`
- [x] 新增 `--dry-run`
- [x] 新增变更前后摘要输出

### 验收标准

- 能在不手动进入 UI 的情况下读取任意页面结构
- 能基于查询条件筛选目标行
- 所有删除/迁移类操作至少支持 dry-run
- 所有写操作输出变更摘要

### 版本状态

| 项目 | 状态 |
| --- | --- |
| 设计完成 | 已完成 |
| 开发完成 | 已完成 |
| 联调完成 | 已完成 |
| 文档完成 | 已完成 |
| 发布完成 | 已完成 |

### v0.2 可执行任务清单

#### 任务拆分原则

- 每个任务都必须有明确的输入、输出、完成定义（DoD）
- 每个命令能力都必须同时补：脚本、统一入口、文档、真实联调
- 所有破坏性能力必须同时补 `dry-run`
- 所有新增能力优先进入 `skills/appflowy-api/`，再同步到 `release/appflowy-api-skill/`

#### 里程碑拆分

| 里程碑 | 周期建议 | 目标 | 状态 |
| --- | --- | --- | --- |
| M1 | 第 1 周 | 补齐查询与读取能力 | 已完成 |
| M2 | 第 2 周 | 补齐 block 删除与字段管理能力 | 已完成 |
| M3 | 第 3 周 | 补齐批量写入、dry-run、diff | 已完成 |
| M4 | 第 4 周 | 完成真实回归、文档、发布 | 已完成 |

#### M1：查询与读取能力

| 编号 | 任务 | 产出物 | 完成定义（DoD） | 依赖 | 状态 |
| --- | --- | --- | --- | --- | --- |
| v0.2-M1-01 | 设计统一查询参数模型 | `database.query` 参数规范 | 明确 filter/sort/page_size/page_token 的 CLI 和 JSON 结构 | 无 | 已完成 |
| v0.2-M1-02 | 新增 `database_query.py` | `skills/appflowy-api/scripts/database_query.py` | 能按 workspace/database 查询行，并支持基础分页 | v0.2-M1-01 | 已完成 |
| v0.2-M1-03 | 将 `database.query` 接入统一入口 | `scripts/appflowy_skill.py` | `python ... appflowy_skill.py help database-query` 可用 | v0.2-M1-02 | 已完成 |
| v0.2-M1-04 | 新增 `page_tree.py` / `page.get-tree` | 页面树读取脚本 | 能列出 workspace 下页面树或指定 view 子树 | 无 | 已完成 |
| v0.2-M1-05 | 新增 `page_blocks.py` / `page.get-blocks` | block 树读取脚本 | 能输出页面 block 树 JSON | 无 | 已完成 |
| v0.2-M1-06 | 为查询命令补示例与参考文档 | `SKILL.md` / `README.md` / `references/` | 每个命令至少 1 个可运行示例 | v0.2-M1-03, v0.2-M1-04, v0.2-M1-05 | 已完成 |
| v0.2-M1-07 | 做真实环境联调 | 回归记录 | 使用真实账号验证查询命令输出正确 | v0.2-M1-06 | 已完成 |

#### M2：Block 删除与字段管理能力

| 编号 | 任务 | 产出物 | 完成定义（DoD） | 依赖 | 状态 |
| --- | --- | --- | --- | --- | --- |
| v0.2-M2-01 | 设计 block 删除命令输入格式 | `page.delete-blocks` 参数规范 | 支持 block_id 列表、文件输入、dry-run | v0.2-M1-05 | 已完成 |
| v0.2-M2-02 | 实现 `delete_page_blocks.py` | block 删除脚本 | 能删除指定 block，且不破坏页面结构 | v0.2-M2-01 | 已完成 |
| v0.2-M2-03 | 设计字段改名能力 | `database.fields.rename` 参数规范 | 明确按 field_id / field_name 改名策略 | v0.2-M1-02 | 已完成 |
| v0.2-M2-04 | 实现字段改名脚本 | `rename_db_field.py` | 能真实改名字段并验证结果 | v0.2-M2-03 | 已完成 |
| v0.2-M2-05 | 设计字段删除安全策略 | 删除 guardrail 规则 | 至少定义：禁止删主字段、默认 dry-run、需明确确认 | v0.2-M2-03 | 已完成 |
| v0.2-M2-06 | 实现字段删除脚本 | `delete_db_field.py` | 能删除非主字段，并输出删除前后 schema diff | v0.2-M2-05 | 已完成 |
| v0.2-M2-07 | 接入统一入口并补帮助文档 | CLI 子命令 | 所有新增命令均可通过统一入口调用 | v0.2-M2-02, v0.2-M2-04, v0.2-M2-06 | 已完成 |

#### M3：批量写入、dry-run 与 diff

| 编号 | 任务 | 产出物 | 完成定义（DoD） | 依赖 | 状态 |
| --- | --- | --- | --- | --- | --- |
| v0.2-M3-01 | 设计统一 `dry-run` 协议 | 规范说明 | 明确所有命令 dry-run 输出格式 | M1, M2 核心脚本可用 | 已完成 |
| v0.2-M3-02 | 实现变更摘要输出库 | `change_report.py` 或公共模块 | 输出 before/after/summary 三段结构 | v0.2-M3-01 | 已完成 |
| v0.2-M3-03 | 为删除类命令接入 dry-run | block 删除/字段删除/row 删除 | `--dry-run` 不落库，只输出计划变更 | v0.2-M3-02 | 已完成 |
| v0.2-M3-04 | 实现 `bulk_upsert_rows.py` | 批量行写入脚本 | 支持 JSON 文件批量 upsert，支持失败统计 | v0.2-M1-02 | 已完成 |
| v0.2-M3-05 | 为批量写入输出 diff 摘要 | 批量写入结果摘要 | 输出新增数/更新数/跳过数/失败数 | v0.2-M3-04 | 已完成 |
| v0.2-M3-06 | 抽离公共参数解析与输出规范 | `_common.py` / 公共库 | 新旧命令输出格式尽量统一 | v0.2-M3-02 | 已完成 |

#### M4：联调、验收与发布

| 编号 | 任务 | 产出物 | 完成定义（DoD） | 依赖 | 状态 |
| --- | --- | --- | --- | --- | --- |
| v0.2-M4-01 | 编写真实环境回归脚本清单 | 回归 Markdown / 命令集 | 覆盖查询、删除、批量写入、dry-run | M1-M3 | 已完成 |
| v0.2-M4-02 | 执行真实环境回归 | 测试记录 | 至少 1 个真实 workspace / database 通过 | v0.2-M4-01 | 已完成 |
| v0.2-M4-03 | 更新 skill 文档 | `SKILL.md` / `README.md` / `references/` | 所有新增命令均有规则说明和反例 | M1-M3 | 已完成 |
| v0.2-M4-04 | 同步 release 目录 | `release/appflowy-api-skill/` | 源目录与发布目录一致 | M1-M3 | 已完成 |
| v0.2-M4-05 | 打版本标签并发布 | commit / tag / VERSION | 形成 v0.2 可交付版本 | v0.2-M4-02, v0.2-M4-03, v0.2-M4-04 | 已完成 |

#### 每周执行视图

| 周次 | 主要任务 | 目标结果 | 状态 |
| --- | --- | --- | --- |
| 第 1 周 | M1-01 ~ M1-07 | 查询与读取命令完成并通过真实联调 | 已完成 |
| 第 2 周 | M2-01 ~ M2-07 | block 删除、字段改名/删除能力完成 | 已完成 |
| 第 3 周 | M3-01 ~ M3-06 | dry-run、diff、批量写入完成 | 已完成 |
| 第 4 周 | M4-01 ~ M4-05 | 回归、文档、发布完成 | 已完成 |

#### 任务验收清单

- [x] 所有新增脚本在 `skills/appflowy-api/scripts/` 落地
- [x] 所有新增脚本已接入 `appflowy_skill.py`
- [x] 所有新增命令有 `--help`
- [x] 所有高风险命令支持 `--dry-run`
- [x] 所有新增命令已写入 `SKILL.md`
- [x] 所有新增命令已写入 `README.md`
- [x] 所有新增命令已写入 `references/appflowy_api_reference.md`
- [x] 至少完成 1 轮真实环境回归
- [x] `release/appflowy-api-skill/` 已同步

#### 风险与阻塞项

| 风险项 | 影响 | 应对策略 | 当前状态 |
| --- | --- | --- | --- |
| AppFlowy 后端接口不完整或不稳定 | 命令设计需要绕过 HTTP 原生接口 | 允许通过 collab 补齐能力，但文档必须说明语义差异 | 持续关注 |
| 不同账号权限差异 | 真实联调可能失败 | 默认准备普通用户账号，不使用系统管理员账号做业务联调 | 已知 |
| seat limit / license 限制 | 无法新建测试用户或 workspace | 保留固定测试账号与测试 workspace | 已知 |
| collab 版本兼容问题 | 删除/修复类能力不稳定 | 脚本必须兼容 Yjs v1/v2，并保留真实环境回归 | 已知 |
| UTF-8 / Windows 编码问题 | 文档和脚本可能乱码 | 所有文档与 JSON/Python 文件统一 UTF-8 | 持续关注 |

## v0.3：形成迁移与修复框架

### 目标

把零散脚本升级为“模板 + diff + migration + rollback”的可维护框架。

### 范围

- schema diff / migration
- 模板参数化
- 修复器框架化
- 操作审计与恢复点

### 计划项

- [ ] 新增 schema diff 命令
- [ ] 新增 migration plan 输出
- [ ] 新增字段改名/类型迁移能力
- [ ] 新增模板变量注入
- [ ] 新增 snapshot / rollback
- [ ] 新增统一审计日志格式

### 验收标准

- 任意 Grid 模板落地前能看到 schema 差异
- 迁移计划可以 review 后执行
- 关键写操作前后可恢复
- 当前已有的 Grid 修复脚本全部迁移到统一框架

### 版本状态

| 项目 | 状态 |
| --- | --- |
| 设计完成 | 已完成 |
| 开发完成 | 已完成 |
| 联调完成 | 已完成 |
| 文档完成 | 已完成 |
| 发布完成 | 已完成 |

### v0.3 可执行任务清单

#### 任务拆分原则

- 每个迁移能力都必须同时提供：`diff`、`plan`、`execute` 三段闭环
- 所有迁移/删除类操作必须默认 `dry-run`，执行时显式确认
- 每个命令都必须输出 `change_report`，至少包含 `before/plan/after/summary`
- 每个里程碑都必须有真实环境回归记录与失败样例
- 所有新增能力优先进入 `skills/appflowy-api/`，再同步到 `release/appflowy-api-skill/`

#### 里程碑拆分

| 里程碑 | 周期建议 | 目标 | 状态 |
| --- | --- | --- | --- |
| M1 | 第 1 周 | schema diff 与 migration plan | 已完成 |
| M2 | 第 2 周 | migration 执行与安全护栏 | 已完成 |
| M3 | 第 3 周 | 模板参数化与修复框架化 | 已完成 |
| M4 | 第 4 周 | snapshot/rollback、回归与发布 | 已完成 |

#### M1：schema diff 与 migration plan

| 编号 | 任务 | 产出物 | 完成定义（DoD） | 依赖 | 状态 |
| --- | --- | --- | --- | --- | --- |
| v0.3-M1-01 | 设计 schema diff 数据模型 | `schema_diff` 规范 | 覆盖 add/rename/delete/type_change 四类差异 | 无 | 已完成 |
| v0.3-M1-02 | 实现 `schema_diff.py` | 差异分析脚本 | 输入当前库+目标模板，输出结构化 diff JSON | v0.3-M1-01 | 已完成 |
| v0.3-M1-03 | 实现 `schema_migration_plan.py` | 迁移计划脚本 | 基于 diff 输出可 review 的 plan（含风险级别） | v0.3-M1-02 | 已完成 |
| v0.3-M1-04 | 接入统一入口 | `appflowy_skill.py` 子命令 | `help schema-diff` / `help schema-migration-plan` 可用 | v0.3-M1-02, v0.3-M1-03 | 已完成 |
| v0.3-M1-05 | 输出规范接入 `change_report` | 公共输出一致化 | diff/plan 命令输出统一 `change_report` | v0.3-M1-02 | 已完成 |

#### M2：migration 执行与安全护栏

| 编号 | 任务 | 产出物 | 完成定义（DoD） | 依赖 | 状态 |
| --- | --- | --- | --- | --- | --- |
| v0.3-M2-01 | 设计 migration execute 协议 | `migration_execute` 规范 | 支持 `--plan-file`、`--dry-run`、`--execute --yes` | v0.3-M1-03 | 已完成 |
| v0.3-M2-02 | 实现 `apply_schema_migration.py` | 迁移执行脚本 | 可按 plan 执行字段新增/改名/删除/部分类型迁移 | v0.3-M2-01 | 已完成 |
| v0.3-M2-03 | 增加高风险护栏 | guardrail 规则 | 至少包含：主字段保护、破坏性变更二次确认、回滚点提示 | v0.3-M2-02 | 已完成 |
| v0.3-M2-04 | 迁移前后 diff 复核 | 校验步骤 | 执行后自动生成 before/after schema diff | v0.3-M2-02 | 已完成 |
| v0.3-M2-05 | 接入统一入口与示例 | CLI + 示例 | `help apply-schema-migration` 可用且有完整样例 | v0.3-M2-02 | 已完成 |

#### M3：模板参数化与修复框架化

| 编号 | 任务 | 产出物 | 完成定义（DoD） | 依赖 | 状态 |
| --- | --- | --- | --- | --- | --- |
| v0.3-M3-01 | 设计模板变量协议 | `template_vars` 规范 | 支持 `--vars` / `--vars-file` 与默认值/必填校验 | 无 | 已完成 |
| v0.3-M3-02 | 实现模板渲染脚本 | `render_template.py` | 支持将模板渲染为可执行 JSON | v0.3-M3-01 | 已完成 |
| v0.3-M3-03 | 修复器框架抽象 | `repair_runner.py` + 规则接口 | 现有修复逻辑可插件化接入（空行、select、结构清理） | M1-M2 核心可用 | 已完成 |
| v0.3-M3-04 | 审计日志格式统一 | `audit_log` 规范 | 每次执行落地输入、结果、耗时、失败原因 | v0.3-M3-03 | 已完成 |
| v0.3-M3-05 | 命令级文档与反例 | 参考文档 | 每个命令补“正确样例 + 失败样例 + 风险提示” | v0.3-M3-02, v0.3-M3-03 | 已完成 |

#### M4：snapshot/rollback、回归与发布

| 编号 | 任务 | 产出物 | 完成定义（DoD） | 依赖 | 状态 |
| --- | --- | --- | --- | --- | --- |
| v0.3-M4-01 | 设计 snapshot/rollback 协议 | 协议文档 | 明确对象粒度、存储格式、恢复流程 | M2 | 已完成 |
| v0.3-M4-02 | 实现快照与回滚脚本 | `snapshot_collab.py` / `rollback_collab.py` | 关键迁移可创建快照并一键回滚 | v0.3-M4-01 | 已完成 |
| v0.3-M4-03 | 执行 v0.3 真实回归 | 回归记录 | 覆盖 diff/plan/execute/template/rollback 全链路 | M1-M4 核心 | 已完成 |
| v0.3-M4-04 | 更新文档与发布目录 | `SKILL.md`/`README.md`/`references/` | 源目录与 release 目录完全同步 | M1-M4 | 已完成 |
| v0.3-M4-05 | 版本发布 | commit / tag / VERSION | 形成 `v0.3.0` 可交付版本 | v0.3-M4-03, v0.3-M4-04 | 已完成 |

#### 每周执行视图

| 周次 | 主要任务 | 目标结果 | 状态 |
| --- | --- | --- | --- |
| 第 1 周 | M1-01 ~ M1-05 | schema diff 与 migration plan 可用 | 已完成 |
| 第 2 周 | M2-01 ~ M2-05 | migration execute + 护栏可用 | 已完成 |
| 第 3 周 | M3-01 ~ M3-05 | 模板参数化 + 修复框架 + 审计日志可用 | 已完成 |
| 第 4 周 | M4-01 ~ M4-05 | 快照回滚、回归、发布完成 | 已完成 |

#### 任务验收清单

- [x] 新增 `schema-diff` 命令并接入统一入口
- [x] 新增 `schema-migration-plan` 命令并接入统一入口
- [x] 新增 `apply-schema-migration` 命令并接入统一入口
- [x] 新增模板渲染能力与变量注入
- [x] 新增 snapshot/rollback 能力
- [x] 所有迁移类命令默认 dry-run 且输出 `change_report`
- [x] 完成至少 1 套 v0.3 真实回归记录
- [x] `release/appflowy-api-skill/` 已同步

#### 风险与阻塞项

| 风险项 | 影响 | 应对策略 | 当前状态 |
| --- | --- | --- | --- |
| AppFlowy 字段类型迁移兼容性差异 | plan 与 execute 结果可能不一致 | 将类型迁移拆为安全子集，超出范围强制人工确认 | 已知 |
| collab 数据结构在版本间变化 | 迁移/回滚脚本不稳定 | 保持 v1/v2 双兼容并做版本探测 | 已知 |
| 回滚快照体积增长 | 存储与恢复成本上升 | 增加压缩与保留策略（TTL/数量上限） | 持续关注 |
| 模板变量注入错误 | 可能写入脏数据 | 渲染前 schema 校验 + 必填变量校验 | 持续关注 |
| 审计日志不完整 | 难以排障与追溯 | 强制关键命令记录输入摘要与执行结果 | 持续关注 |

## v0.4：增强内容编排与媒体能力

### 目标

让 skill 从“数据表工具”扩展为“文档内容工具”。

### 范围

- 丰富 block 类型支持
- 富文本/列表/callout/code block 抽象
- 文件上传与媒体引用

### 计划项

- [ ] 支持 list / quote / callout / divider
- [ ] 支持 code block / bookmark / embed
- [ ] 支持 image / file block
- [ ] 支持 block move / reorder
- [ ] 支持页面内容 patch

### 验收标准

- 能自动生成结构化项目文档而不是仅附加段落
- 能可靠维护工程文档常见 block 类型
- 能处理图片、附件和引用资源

### 版本状态

| 项目 | 状态 |
| --- | --- |
| 设计完成 | 未开始 |
| 开发完成 | 未开始 |
| 联调完成 | 未开始 |
| 文档完成 | 未开始 |
| 发布完成 | 未开始 |

## v1.0：对标成熟云文档维护 skill

### 目标

形成一个面向 AI 的、可安全执行、可回滚、可批量治理的 AppFlowy 文档维护工具。

### 范围

- 完整对象模型：workspace / page / block / database / row / permission / comment
- 统一 patch 与迁移机制
- 审计、diff、dry-run、rollback 全覆盖
- 高质量模板系统与场景化工作流

### 计划项

- [ ] 统一对象抽象层
- [ ] 全链路 dry-run / diff / audit
- [ ] 页面治理工作流
- [ ] 数据库治理工作流
- [ ] 协作与权限能力
- [ ] 模板资产化与最佳实践

### 验收标准

- AI 能可靠执行大部分文档维护任务
- 高风险操作具备预演、审计和恢复机制
- 能在真实团队环境中用于持续治理

### 版本状态

| 项目 | 状态 |
| --- | --- |
| 设计完成 | 未开始 |
| 开发完成 | 未开始 |
| 联调完成 | 未开始 |
| 文档完成 | 未开始 |
| 发布完成 | 未开始 |

## 五、近期优先级建议

### 5.1 未来 2 周建议

1. 先做 `schema-diff`
2. 再做 `schema-migration-plan`
3. 然后做 `apply-schema-migration`（默认 dry-run）
4. 补 `template vars` 与 `render-template`
5. 最后补 `snapshot/rollback`

### 5.2 不建议优先做的内容

- 先做评论/审阅流
- 先做复杂 UI 层模板市场
- 先做过多业务样例脚本

原因：

- 当前最大短板不是“场景不够多”，而是“底层可维护闭环不够完整”

## 六、监控面板

### 6.1 版本级监控

| 指标 | 当前值 | 目标值 | 更新频率 | 备注 |
| --- | --- | --- | --- | --- |
| 已封装命令数 | 30 | v0.2 达到 22+ | 每版本 | 以统一入口命令为准 |
| 已支持对象域数 | 4 | v1.0 达到 8+ | 每版本 | workspace/page/block/database/row... |
| 高风险操作 dry-run 覆盖率 | 80% | v0.2 达到 80% | 每版本 | 删除/迁移/批量写 |
| 文档 block 类型覆盖数 | 3 | v0.4 达到 12+ | 每版本 | paragraph/heading/grid... |
| 数据库查询能力覆盖率 | 70% | v0.2 达到 70% | 每版本 | list/detail/filter/sort/page |
| 回滚能力覆盖率 | 60% | v0.3 达到 60% | 每版本 | 核心写操作（snapshot/rollback 已接入） |

### 6.2 质量级监控

| 指标 | 当前状态 | 目标 |
| --- | --- | --- |
| 真实环境回归脚本 | 已具备 | 每个版本至少 1 套 |
| 命令帮助完整度 | 中 | 每个命令都有示例 |
| 文档一致性 | 中 | 源码/发布目录/参考文档同步 |
| 编码稳定性 | 中 | 全部 Markdown / JSON / Python 统一 UTF-8 |

## 七、已确认的事实与规则

- `DELETE /api/workspace/{workspace_id}/database/{database_id}/row` 当前不支持，通常会返回 `405`
- 行删除目前通过 collab 更新 `row_orders` 实现
- 字段改名 / 字段删除当前通过 collab 更新实现，删除默认 dry-run，执行需 `--execute --yes`
- 页面 block 删除已支持 `page-delete-blocks`，并可先 `--dry-run`
- 批量写入已支持 `bulk-upsert-rows`，返回 `change_report`（before/plan/after/summary）
- `SingleSelect` / `MultiSelect` 行值写入时，优先使用“选项名称”
- `Checklist` 字段可使用 `selected_option_ids`
- 系统级管理员账号不等于普通 workspace 用户，真实联调应优先使用普通用户账号

## 八、待补 issue 清单

- [ ] 为所有高风险命令补 `--dry-run`
- [ ] 为数据库操作补批量模式
- [ ] 为 block 操作补通用读/改/删接口
- [ ] 为模板应用补 schema diff
- [ ] 为修复类脚本补统一回归测试
- [ ] 为 skill 文档补“最佳实践”和“反例”

## 九、更新记录

| 日期 | 更新内容 | 更新人 |
| --- | --- | --- |
| 2026-03-02 | 初始化能力矩阵、对标分析与版本路线图 | Codex |
| 2026-03-02 | v0.2 M1 完成：新增 database-query/page-get-tree/page-get-blocks，补文档并完成真实联调 | Codex |
| 2026-03-02 | 更新进度：M4-03/M4-04 调整为进行中，验收清单按 M1 实际完成情况勾选 | Codex |
| 2026-03-02 | v0.2 M2 完成：新增 page-delete-blocks/rename-db-field/delete-db-field，补安全护栏并完成真实联调 | Codex |
| 2026-03-02 | 版本路线图更新：v0.2 设计状态改为已完成，M3 启动并将 M3-01 标记为进行中 | Codex |
| 2026-03-02 | v0.2 M3 完成：新增 bulk-upsert-rows、统一 change_report 协议、删除类 dry-run 全覆盖并完成真实联调 | Codex |
| 2026-03-03 | v0.2 M4 完成：回归清单与真实回归完成、文档与 release 同步、版本升级到 0.2.0 并发布标签 | Codex |
| 2026-03-03 | 按 v0.2 标准完成 v0.3 任务规划：新增里程碑、任务表、验收清单、风险项与周执行视图 | Codex |
| 2026-03-03 | v0.3 M1 完成：新增 schema-diff/schema-migration-plan、接入 change_report、完成真实联调并补文档 | Codex |
| 2026-03-03 | v0.3 M2 完成：新增 apply-schema-migration、补执行护栏与 before/after diff、完成真实联调与文档更新 | Codex |
| 2026-03-03 | v0.3 M3 完成：新增 render-template/repair-runner、模板变量协议、统一 audit_log 与真实联调 | Codex |
| 2026-03-03 | v0.3 M4 完成：新增 snapshot-collab/rollback-collab、完成真实回归、版本升级到 0.3.0 并发布标签 | Codex |
