# 软件自动化测试选型

从要证明的行为出发，先探测软件已有的测试入口，再选择能产生有效证据的自动化方法。适用于 CLI/API、网页和桌面应用；帮助减少逐次截图、点击和等待的操作成本，不承诺固定加速倍数。

## 可以做什么

- **业务与文件结果：** 使用已有函数测试、正式 CLI 或 HTTP API，检查退出码、业务状态和本次实际产物。
- **网页交互：** 使用 DOM 自动化验证按钮、表单、导航和异步状态；沿用项目已有工具，按需使用 Playwright 等框架。
- **Windows 桌面：** 探测 UI Automation 控件树和所需 Pattern；支持只有 EXE 的应用在目标进程范围内执行控件动作。
- **Mac 桌面：** 提供 Python 标准库实现的 macOS Accessibility（AX）执行器，适用于可访问的原生窗口和 .app；实现尚未经过 Mac 实机验证。
- **有源码的 Qt 应用：** 按项目已有 PySide/PyQt 环境选择 pytest-qt 等内部测试入口，验证控件、信号、线程和取消行为。
- **外观验收：** 对排版、裁切、颜色和绘图结果补充受控截图或导出图比较；接口成功不能代替视觉验收。

Windows UIA 与 Mac AX 助手提供 set、invoke、wait，并核对目标 PID、可执行文件、窗口和父区域、唯一控件与完整步骤计划。执行使用条件等待、整个进程的硬超时、原子报告及进度日志；中断后可区分已完成步骤和结果未知的动作，未知动作不会自动重放。

## 系统支持与验证范围

| 系统 | 可用路线 | 验证范围 |
| --- | --- | --- |
| Windows 10 x64 | CLI/HTTP、网页 DOM、Windows UIA、Python Qt 和视觉样例 | 已执行仓库记录中的样例与回归；不代表所有应用或框架均通过 |
| Windows 11 | 可按现有 Windows 路线探测目标应用 | 本次没有 Windows 11 实机结果 |
| macOS（Intel / Apple Silicon） | 提供 Mac 原生 AX 实现；也可按项目选择 CLI/HTTP、DOM 或 Qt 内部测试 | Mac 原生 ABI、辅助功能权限、真实窗口与文件系统尚未实机验证 |
| Linux | 按项目选择 CLI/HTTP、DOM、Qt 内部测试等可移植入口 | 本包没有 Linux 原生 GUI 驱动；本次没有 Linux 执行结果 |

Electron、CEF、WebView2、其他 Qt 绑定及自绘界面需要先核对实际 DOM、UIA/AX 或项目内部入口。普通网页通过不能代替真实宿主验证，控件属性正确也不能证明画面没有裁切。

## 运行前提

- **Windows 原生 UIA：** Python 3.10+ 标准库、PowerShell 7、Windows 和可交互桌面。
- **macOS 原生 AX：** macOS、64 位 Python 3.10+ 标准库、已有辅助功能授权和可交互桌面；不需要 PowerShell、PyObjC、Swift 或 Xcode。助手只检查已有授权，不修改系统权限。
- **网页与 Qt：** 使用项目已有测试工具及对应浏览器或 Qt 绑定；这些工具以及 pytest、维护解析依赖不随本包安装。

## 对应版本与已有证据

本介绍对应 **1.1.1**：补充完整概述和平台介绍；运行能力沿用 1.1.0 的 Mac AX 与按系统分发入口，保留原 Windows 入口和步骤格式。维护仓库另有跨平台 Python 安装器；维护工具与编译验收样例不属于独立运行包。

2026-11-07 在 Windows 10 的最终完整回归为 **339 通过、7 跳过**；受控安装包运行子集为 **193 通过**。跳过和 Windows 上的替身检查不算 Mac 原生通过。Mac 实机验证尚未进行，Windows 11 和 Linux 也没有本次实机执行结果。历史失败、恢复和具体覆盖范围保留在[验证记录](validation.md)中。

## 安装与使用

可从 [GitHub Release v1.1.1](https://github.com/hunxuankai/software-testing-router/releases/tag/v1.1.1) 下载独立的 software-testing-router-1.1.1.zip，核对附带的 SHA-256，并保留完整技能目录和所有被引用文件。

也可通过 skills CLI 安装固定版本：

```sh
npx skills add https://github.com/hunxuankai/software-testing-router/tree/v1.1.1/skills/software-testing-router --skill software-testing-router
```

在已安装技能的根目录检查桌面入口：

```sh
python3 scripts/run_desktop.py --help
```

Windows 可使用 python scripts/run_desktop.py --help；原 run_uia.py 入口仍可用。帮助成功只证明入口加载，原生动作还需要实际目标进程、授权、控件能力和后置结果。Linux 使用相应可移植测试入口。

例如：使用 software-testing-router 验证一个 Windows EXE 或 Mac .app 的表单填写和 JSON 导出。先核对实际窗口进程及 UIA/AX 能力，再选择最小验证流程，检查本次输出，并报告失败信息和未覆盖部分。

完整方法见 [SKILL.md](../SKILL.md)、[Windows UIA](windows-uia.md)和[macOS AX](macos-accessibility.md)。使用、修改与分发遵循 [MIT 许可](license.txt)。
