# daftai-cloudflare-billing-audit/
> L2 | 父级: ../../CLAUDE.md

成员清单

- `SKILL.md`: 离线、只读 Cloudflare 账单风险审计入口，限定目标/输出路径和稳定输入边界，路由渐进加载的工作流、证据指南与报告契约。
- [agents/CLAUDE.md](agents/CLAUDE.md): 技能发现元数据地图。
- [references/CLAUDE.md](references/CLAUDE.md): 按产品渐进加载的参考地图。
- `agents/openai.yaml`: Codex 技能列表显示名称、摘要和调用提示。
- `references/workflow.md`: 仓库边界识别、调用链/跨重调度进度与额度范围、有限SQL迁移/YAML辅助证据、竞态/估算边界及未执行验收建议。
- `references/report-schema.md`: 分离脚本候选和 agent 核实结论的报告格式，记录允许检查的源/辅助路径、SHA/stat 指纹、实际平台/适配器模式与受控重读结果。
- `references/scanner.md`: 本地配置清点辅助脚本的调用、范围、窄范围 SQL/YAML 文件清单、Linux 描述符与 macOS/Windows 稳定树边界、安装后原生烟测矩阵；脚本不是静态分析器。
- `references/workers.md`, `d1.md`, `durable-objects.md`, `storage.md`, `queues.md`, `compute-ai.md`, `operations.md`: 按实际命中产品渐进加载的计费机制和风险证据。
- `references/sources.json`: 产品指南来源、日期、来源类型和本地证据元数据。
- `references/maintenance.md`: 仅用于单独维护公开来源证据；项目审计不更新指南。
- [scripts/CLAUDE.md](scripts/CLAUDE.md): 脚本模块分层、导入方向与测试入口；维护代码前先读。
- `scripts/audit.ts`: CLI 与既有导出 API 门面；不执行目标代码、SQL 或 YAML 工作流。
- `scripts/audit-engine.ts`: 有界清点、报告输出与 inventory SHA/stat 指纹校验后的单文件受控读取。
- `scripts/audit-types.ts`: 报告、候选、证据、额度与适配器选项类型。
- `scripts/audit-fs.ts`: 按实际宿主平台选择文件系统适配器；测试可显式选择便携模式，不伪造宿主平台。
- `scripts/linux-fs.ts`, `scripts/portable-fs.ts`, `scripts/fs-common.ts`: Linux 描述符锚定、macOS/Windows 稳定树检查及共享身份/路径工具；便携模式不承诺抵御恶意并发。
- `scripts/config.ts`, `scripts/discovery.ts`, `scripts/source-scan.ts`: 配置解析/投影、有界发现与排除规则、词法候选分析；不推断部署或完整调用链。
- `scripts/audit.test.ts`, `scripts/audit.security.test.ts`, `scripts/audit.portable.test.ts`, `scripts/audit.regression.test.ts`: 解析、辅助证据、指纹读取、Linux 安全边界与真实宿主/显式便携模式契约测试；用 `bun test scripts/*.test.ts` 运行，不固定测试数量。
- `scripts/installed-smoke.ts`: 对解包技能运行合成夹具、CLI 与全部已安装测试套件，记录非 Linux 宿主跳过的 Linux 专属覆盖，记录真实平台/运行时/模式、文件哈希与未运行平台的 `NOT_RUN`。

依赖边界

`SKILL.md` 编排审计。scanner 只负责配置清点并输出候选/未知信息；agent 要独立追踪真实入口、触发条件和调用链，核实产品计费单位，并把未覆盖范围写入报告。产品参考应按路径命中加载，不将声明的 binding 本身当作计费风险。审计不得读取凭据、运行目标项目、复制目标源码或访问 Cloudflare 账户。目标、祖先和输出树须保持稳定；前后身份检查不是原子快照，不允许以原始路径手工读取绕过拒绝。每个代码文件不超过 800 行，超出时沿职责边界拆分并同步本层和脚本层映射。原生验收必须在对应宿主运行，不以显式便携模式代替其他平台。

[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
