# Birdview 0.3.1

[English](release-notes-0.3.1.md)

本次补丁修复符号链接下的 CLI 启动问题，加强安装诊断，并在保持布局不变的前提下优化查看器动效。

- 各工作 CLI 现在能通过符号链接识别自己的入口，包括 Node 的 `--preserve-symlinks-main` 模式（#25）。
- `doctor` 实际执行已安装的校验 CLI，并检查退出状态及 JSON 报告。静默退出、异常报告和执行失败不会再被判定为通过（#26、#27）。
- 仍处于活动状态的流动标记保持动画连续；缩短过渡并允许指引动画中途切换。尊重减少动态效果设置，键盘导航保持即时响应（#28、#29）。
- 删除迁移专用的冻结旧实现与 Schema 副本，保留当前行为测试、运行时与导出 Schema 对照，以及可复现构建检查（#28、#29）。

按[安装指南](installation.zh.md)更新完整技能包，在技能目录运行 `npm ci` 和 `node scripts/birdview.mjs doctor`。通过 `setup --project <project-root>` 刷新已配置项目，并新建 Agent 任务；保留本地定制。已有调用模式保持不变。包含生成后的 JavaScript，使用者无需编译 TypeScript。继续通过 GitHub 分发，npm 包保持私有。

验证覆盖 87 项单元测试、七组 Chromium 测试、严格类型检查、可复现产物、示例校验、演示生成、双语文档和已提交源码的干净安装。CI 检查 Windows、Linux 及 Node.js 18、24。

`doctor` 探测一个已安装的工作 CLI 并在内存中渲染，不会执行所有命令，也不能证明技能在 Agent 会话中成功激活。Birdview 展示 Agent 声明的快照与指令，不独立观测修改或强制限制文件写入。本补丁不宣称已测得 AI 编码质量提升。
