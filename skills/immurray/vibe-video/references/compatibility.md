# 兼容性与调用

本技能是标准 SKILL.md + Python/Node 脚本，不含模型供应商 SDK、API Key 或 Codex 专属工具调用。能否执行取决于宿主能否加载技能、读写文件、运行命令、研究资料和查看图片；模型负责文案和代码，脚本负责可重复的渲染与检查。

## 安装位置

将整个 vibe-video 文件夹复制到对应技能目录。不要只复制 SKILL.md。

| 宿主 | 默认目录 | 调用 |
| --- | --- | --- |
| Codex | ~/.agents/skills/vibe-video | `$vibe-video 主题：……` |
| DeepSeek Harness / DSH | ~/.dsh/skills/vibe-video，或共享 ~/.agents/skills/vibe-video | 让代理使用 vibe-video；在当前版本技能选择器中选择它 |
| Hermes | ~/.hermes/skills/vibe-video | `/vibe-video 主题：……` |

DSH 自定义配置可能改变扫描目录；项目技能应放在项目根 .dsh/skills 或 .agents/skills。Hermes 的不同 profile 各有技能目录。安装后查看目录/技能列表并确认加载内容；能发现不代表执行完成。

DeepSeek、GPT、Claude 等模型可由宿主选择，本技能不切换模型、不保存凭据。对没有图片理解能力的模型，必须提供可看图工具或人工审片，才能完整验收视频。普通网页对话若没有终端和文件执行环境，不能独立完成渲染。

## 验证口径

已在 macOS 上验证辅助脚本、Canvas 预览与 MP4 导出。DSH 与 Hermes 的格式/目录依据官方文档适配；各模型的完整“新主题→成片”仍需单独验收。不能以格式兼容推断质量一致。Linux/Windows 尚未跑完整渲染。

建议宿主验证：目录可发现 → 加载当前 SKILL.md → 新目录运行 doctor/prepare → 渲染短样片 → 新主题完整出片。不要把 shell 测试写成模型端到端成功。

## 官方资料

- Agent Skills 格式：https://agentskills.io/specification
- Codex：https://learn.chatgpt.com/docs/build-skills
- DSH：https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md
- Hermes：https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/
