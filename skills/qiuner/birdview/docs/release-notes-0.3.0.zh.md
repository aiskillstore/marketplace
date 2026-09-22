# Birdview 0.3.0

[English](release-notes-0.3.0.md)

Birdview 现在默认按需调用，并要求用户确认已展示的地图与修改计划后再实施。

- Codex 使用 `/skills` 或 `$birdview` 选择技能；Claude Code 使用 `/birdview`。其他宿主使用自己的技能选择器或明确请求。
- 自动模式仍可通过 `mode auto` 主动开启。新项目默认 `on-demand`，初始化保留已有自动、按需和停用设置。
- 两种激活模式下，Agent 都先准备并展示地图、涉及文件、约束与验证计划，再等待确认。同一方案的确认可复用；范围实质变化时再次确认。用户明确的单次任务豁免优先。
- 约束发现、已审查规则图、来源证据、历史和架构集成现已具备类型化契约及渲染流程。来源收集、适用性和合规验证仍分别表达。
- TypeScript 源码、浏览器构建产物、生成 Schema 和安装检查现已覆盖分发实现。保留生成后的 JavaScript，技能用户无需编译。

按[安装指南](installation.zh.md)安装完整源码包，在技能目录运行 `npm ci` 和 `node scripts/birdview.mjs doctor`。升级后，对已配置项目执行 `setup --project <project-root>`，刷新管理指令并保留已有模式。要将已有自动模式项目改为手动调用，使用 `mode on-demand`。新建 Agent 任务以避免旧指令缓存，并保留本地定制。通过 GitHub 分发，不发布到 npm。

发布验证覆盖类型检查、生成产物一致性、单元测试、示例校验、演示生成、Chromium 浏览器测试、双语文档及已提交源码的干净安装。发布流程在公开版本前记录实际结果。

Birdview 展示 Agent 声明的快照。确认步骤是 Agent 指令，不是文件写入锁，也不是 HTML 查看器强制执行的批准按钮。尚未独立验证所有支持 Agent 的真实会话调用与确认行为。本次发布不包含私有 DeepSeek 来源清单或本地预览。
