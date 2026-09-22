# 安装 Birdview

[English](installation.md)

## 多 Agent 安装

使用第三方 [skills CLI](https://github.com/vercel-labs/skills) 选择 Agent 和安装范围：

```sh
npx skills add Qiuner/birdview --skill birdview
npx skills add Qiuner/birdview --skill birdview --agent codex --global --copy --yes
npx skills add Qiuner/birdview --skill birdview --agent claude-code --global --copy --yes
```

省略 `--global` 则安装到项目。这些命令安装仓库当前版本；固定版本使用下方压缩包方式。在安装器输出的目录执行 `npm ci`（包括开发依赖），再执行 `node scripts/birdview.mjs doctor`。只读自检会通过安装路径调用实际校验 CLI、检查 JSON 报告，并在内存中渲染内置示例。它不覆盖全部工作 CLI，也不验证 Agent 触发。安装器或 Agent 可能要求比 Birdview 更高的 Node.js 版本。

Claude Code 也支持手动安装到 `~/.claude/skills/birdview` 或 `<project-root>/.claude/skills/birdview`，按下文保留完整目录。模式命令添加 `--agent claude-code` 后写入/查询 `CLAUDE.md`，默认管理的是 `AGENTS.md`。

## DeepSeek Harness

Harness 原生发现 `.dsh/skills` 和 `.agents/skills`，直接安装完整目录，无需单独插件（适用于 PowerShell 或 POSIX shell）：

```sh
git clone https://github.com/Qiuner/birdview.git "$HOME/.dsh/skills/birdview"
npm --prefix "$HOME/.dsh/skills/birdview" ci
node "$HOME/.dsh/skills/birdview/scripts/birdview.mjs" doctor
```

自定义了 `DSH_HOME` 时，将 `$HOME/.dsh` 替换为该目录。项目级安装使用 `<project-root>/.dsh/skills/birdview`。已有的 `~/.agents/skills/birdview` 也可被发现，避免重复安装。共享根目录可被 `DSH_AGENTS_HOME` 或宿主配置覆盖。模式命令添加 `--agent deepseek`，管理 `AGENTS.md`。

此适配面向启用了文件系统技能提供器的 Harness，已对照[源码版本 7a0b768](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/packages/skill/skill-filesystem/src/index.ts)核对。Node.js 版本遵循 Harness 自身要求。这不是向 DeepSeek 聊天网站安装技能。本次未进行 Claude Code 和 Harness 实际会话的端到端测试，请按下文在新任务中验证触发。

## 手动安装（Codex）

安装 Node.js 18 或更高版本。从本仓库的 GitHub Releases 页面下载所需版本的源码压缩包并解压。将完整目录放到 `~/.agents/skills/birdview`（`~` 是用户主目录）。`SKILL.md` 必须直接位于 `birdview` 下，不能多嵌套一层目录。保留脚本、Schema、资源、参考文档、文档、示例、包文件及许可证声明；只复制 `SKILL.md` 不够。

在该目录安装渲染器依赖：

```powershell
# Windows PowerShell
npm --prefix "$HOME/.agents/skills/birdview" ci
node "$HOME/.agents/skills/birdview/scripts/validate.mjs" "$HOME/.agents/skills/birdview/examples/architecture.json"
```

```sh
# macOS / Linux
npm --prefix "$HOME/.agents/skills/birdview" ci
node "$HOME/.agents/skills/birdview/scripts/validate.mjs" "$HOME/.agents/skills/birdview/examples/architecture.json"
```

校验器应报告 `"ok": true`。在目标项目新建 Codex 任务，要求：“用 Birdview 展示这个项目的架构，不修改代码。”确认 Codex 读取了 Skill、报告是否发现已有地图，并生成或更新 HTML 预览。校验通过本身不代表 Agent 触发验证通过。

Codex [官方技能文档](https://developers.openai.com/codex/skills) 指定用户级技能目录为 `~/.agents/skills`，仓库级为 `.agents/skills`。Codex 会自动检测变化；技能未出现时重启。避免重复安装同名 `birdview`，包括旧客户端专用技能目录中的副本。

## 选择模式

安装完整技能后，对每个选定项目启用持续生效的基础约束：

```sh
node <skill-root>/scripts/birdview.mjs setup --project <project-root>
```

Claude Code 添加 `--agent claude-code`，Harness 添加 `--agent deepseek`，默认目标为 Codex。初始化为新项目选择按需模式，保留已有自动、按需或停用设置。第三方安装器仅安装技能文件，不会执行这一步。按需模式下，基础约束仍指导编码，不要求加载技能或生成地图。状态显示两项设置。保留安装但关闭两者使用 `mode off`。这些规则依赖宿主加载项目指令文件，请在新任务中验证。

分发版本默认**按需调用**。Codex 输入 `/skills` 选择 Birdview 或使用 `$birdview`；Claude Code 使用 `/birdview`。未开启自动模式时，普通修改不触发。其他宿主的斜杠入口取决于宿主支持。将下列占位符替换为绝对路径后配置或查询：

```sh
node <skill-root>/scripts/birdview.mjs mode on-demand --project <project-root>
node <skill-root>/scripts/birdview.mjs mode --project <project-root>
```

使用 `mode auto` 开启自动触发，`mode on-demand` 恢复按需调用。写入和查询均选择相同的 `--agent codex`（默认）、`--agent claude-code` 或 `--agent deepseek`。项目显式设置优先于默认值。CLI 管理目标项目 `AGENTS.md`（Claude Code 使用 `CLAUDE.md`）中的一段规则，不会配置全部项目或同步不同指令文件。详见[模式说明](../references/modes.zh.md)。这些是 Agent 指令，不是强制编辑拦截。

## 更新或卸载

更新前保留本地技能定制并记录安装版本。使用选定版本替换已安装源码，再运行 `npm ci`；版本默认值可能覆盖本地定制。各项目的模式段落仍保留在项目中。不要将旧副本留在另一个会被扫描的技能目录下。

更新后，对各已配置项目重新执行 `setup`，刷新基础约束并保留已有模式。移除已安装的 `birdview` 目录前，对各已配置指令文件使用相同 `--agent` 执行 `node <skill-root>/scripts/birdview.mjs uninstall --project <project-root>`。此命令只删除管理段，不删除用户规则或安装文件。技能已移除时，手动仅删除 `<!-- birdview:mode:start -->` 到 `<!-- birdview:mode:end -->` 之间的完整段落。项目地图与活动记录保留。仅移除规则会恢复已安装技能的默认模式，不是持久停用。

npm 包保持私有；`npm install -g birdview` 不是本项目的安装方式。从源码检出进行开发请参考 [CONTRIBUTING.zh.md](../CONTRIBUTING.zh.md)。
