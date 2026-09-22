# Birdview 0.2.0

[English](release-notes-0.2.0.md)

用 Birdview 来改变开发的流程！真正地从关注代码到关注架构！解决 AI coding 的黑盒！

本版增加通过第三方 skills CLI 为 Codex、Claude Code 安装的说明，并适配 DeepSeek Harness 原生技能目录安装，无需额外插件。

- `mode --agent claude-code` 管理 `CLAUDE.md`；`codex`（默认）和 `deepseek` 管理 `AGENTS.md`，保留管理段以外的已有规则。
- `doctor` 在内存中校验并渲染内置示例，检查依赖和模板资源，不写入项目文件。
- 中英文安装和模式文档同步。默认仍为自动模式，项目显式按需设置继续优先。

按照[安装指南](installation.zh.md)操作，或解压本版完整源码压缩包，在技能目录内运行 `npm ci`，再运行 `node scripts/birdview.mjs doctor`。保留全部资源和许可证声明。本版发布到 GitHub，不发布到 npm。

已验证：48 项自动化测试、示例校验、示例构建可复现、覆盖视图/指引/视口的三项浏览器检查，以及通过 skills CLI 在临时目录安装到 Claude Code 后安装依赖并运行 doctor。双语文档和本地链接也已检查。

尚未进行 Claude Code 和 DeepSeek Harness 实际会话触发的端到端验证。Harness 技能发现已对照文件系统提供器源码核对。Birdview 展示 Agent 声明的活动并提供指令，不独立观察编辑，也不强制执行流程。
