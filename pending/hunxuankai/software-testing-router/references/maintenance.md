# 版本与本地维护

当前技能版本：**1.1.0**，由本包 `SKILL.md` 的字符串 `metadata.version` 标识。这个目录是运行包，包含入口、代理配置、运行脚本、参考页、许可与小型历史证据；不包含仓库测试或维护工具。独立发行包与来源见 [GitHub Release](https://github.com/hunxuankai/software-testing-router/releases/tag/v1.1.0)；各市场的收录和审核状态应分别核验。

Windows UIA 运行需要 Python 3.10+ 标准库、Windows、PowerShell 7 和可交互桌面。macOS AX 运行需要 macOS、64 位 Python 3.10+ 标准库、已有辅助功能授权和可交互桌面，不需要 PowerShell、PyObjC 或 Xcode；详情见 [Mac 原生路线](macos-accessibility.md)。可以在本目录执行 `python scripts/run_desktop.py --help`（POSIX 为 `python3`）；旧 Windows `python scripts/run_uia.py --help` 仍可用。帮助成功不等于桌面动作已验证，Linux 暂无本包原生 GUI 驱动。

源码唯一位置是维护仓库的 `skills/software-testing-router/`，公开快照位于 [GitHub](https://github.com/hunxuankai/software-testing-router/tree/main/skills/software-testing-router)。维护者在维护仓库运行校验与跨平台 Python 安装工具，Windows 保留 PowerShell 包装器；不要直接修改安装副本或把缓存当作源文件。安装使用普通目录复制，拒绝链接/祖先链接、额外文件、路径重叠与冲突，更新前备份完整旧副本，复制后核对校验清单哈希。失败时保留备份并停止，按仓库维护文档恢复。

安装器用已有目录的文件系统身份补充词法包含检查，识别路径别名；仅对有歧义的缺失尾段查询大小写策略。策略未知时拒绝有歧义的自定义路径配置，常规默认位置正常使用；不放宽链接规则，不写探测文件。

版本遵循 SemVer：PATCH 用于兼容修正，MINOR 用于兼容新增，MAJOR 用于不兼容变化。仅仓库维护工具或开发文档变化不要求升级技能。同一发行版本固定内容，发行标签不重写。安装环境与机器信息不会写回本包。

1.0.1 为公开发行加入 MIT 许可，并将三份历史 JSON 中的本机目录替换为占位符；原始证据及旧标签保留在本地维护历史。具体字段、原始哈希和派生文件见 [公开证据说明](evidence/public-redactions-1.0.1.md)。1.0.2 将两份纯文本历史日志的扩展名由 .log 改为 .txt，以适配 GitHub 导入的文件类型限制；日志字节未变。运行脚本和测试选型行为未变。

1.1.0 为兼容 MINOR 扩展：新增 Mac AX 入口与跨平台安装，保留原 Windows 四个脚本和步骤格式。Mac Intel/Apple Silicon 的原生 ABI、权限与真实窗口均未实机验证，不把 opt-in 测试的 skipped 计入通过。安装器和编译测试 fixture 不进入运行包。

覆盖、历史结果和限制见 [验证摘要](validation.md)，测试选型入口见 [SKILL.md](../SKILL.md)。完整开发回归、备份恢复和发行记录保留在维护仓库，不是本运行包的依赖。普通使用者可从 GitHub Release 获取已发布版本的独立包，或用 skills CLI 选择明确版本更新；完整目录和所引用文件必须保留。
