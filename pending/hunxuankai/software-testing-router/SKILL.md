---
name: software-testing-router
description: Use when choosing or implementing software automation tests across CLI/API, web, or Windows/macOS desktop apps, especially when Computer Use screenshot-and-click loops are slow, only an EXE or .app is available, or the correct test interface is unclear. 适用于软件自动化测试选型、桌面回归、GUI 验收和测试入口探测。
license: MIT
metadata:
  version: "1.1.1"
---

# 软件自动化测试方法选择

按验收目标选择软件已有的测试入口，系统能力与验证边界见[完整概述](references/overview.md)。Mac 原生实现尚未实机验证，Linux 无本包原生 GUI 驱动。

选择**能证明当前验收要求、且总成本较低的稳定入口**。先探测接口和控件能力，再选择工具；开发语言不能单独决定可测性。Computer Use 是缺少合适结构化入口时的备选，不是软件测试的默认起点。

## 先确定要证明什么

从任务和仓库提取：被测版本、目标环境、源码/EXE/URL、已有测试工具、具体行为和预期结果。已有可用工具通常比换框架更省时。只为真正缺失且影响下一步的信息询问用户。

| 要证明的行为 | 优先探测的入口 | 最小有效证据 | 按需阅读 |
|---|---|---|---|
| 算法、文件转换、服务业务契约 | 已有函数测试、正式 CLI 或 API | 退出码/HTTP 状态 **及** 业务结果、实际产物 | [CLI / API](references/cli-api.md) |
| 网页按钮、表单、导航、异步弹窗 | DOM 自动化；已有框架可沿用，缺少时可选 Playwright | 真实用户事件 → 请求/界面状态 → 业务结果 | [网页](references/web.md) |
| Windows 桌面实际交互，含只有 EXE 的应用 | UIA 控件树与所需 Pattern；本包提供 PowerShell 实现 | 指定进程的控件动作、后置状态与产物 | [Windows UIA](references/windows-uia.md) |
| macOS 原生窗口实际交互，含 .app | Accessibility 属性与动作；本包提供 Python 标准库实现，需已有辅助功能授权 | 指定 PID 的唯一控件动作、后置状态与本次产物；本实现未实机验证 | [macOS Accessibility](references/macos-accessibility.md) |
| 有源码的 PySide/PyQt 控件、信号、线程、取消 | pytest-qt 的 Qt 事件循环 | 信号、状态、错误路径、应出现或不应出现的产物 | [Qt 内部测试](references/qt.md) |
| 排版、裁切、颜色、透明度、绘图外观 | 受控截图/导出图 + 有依据的视觉比较 | 固定环境下的原图、对照、差异解释 | [视觉与能力边界](references/visual-and-limits.md) |

API 成功不能证明按钮有效；控件或信号成功不能证明打包 EXE/.app 可用；DOM/UIA/AX 属性正确不能证明画面无裁切。按验收要求组合必要层次，不为每个任务运行所有路线。只验收文件转换且已确认正式 CLI 时，Mac 上也优先沿用 CLI/API。

Electron / WebView 先区分 HTML 内容与原生外壳：**已可用且获授权的**调试连接可走 DOM，原生对话框按系统探测 UIA 或 AX。普通网页测试不等于验证 Electron。没有调试端口时不能假定能附加，也不要为了测试改动用户正在使用的浏览器配置。

## 探测后执行

1. 用一句话记录：`要证明的行为 → 实际发现的入口 → 选择原因 → 成功证据 → 失败时的下一步`。先用小流程验证入口，避免先搭建大套测试框架。
2. 桌面先确认实际窗口拥有者，再用浅层检查读取区域与 Pattern/AX 属性；`scripts/run_desktop.py` 按系统选择入口，旧 Windows `run_uia.py` 仍可用。两平台支持 `--probe`、`--inspect-depth`、步骤内 `within` 和 `window`；Mac probe 仅检查已核验的指定 PID，不寻找启动器后代。网页按实际 DOM 建定位。标识必须唯一；重名时缩小作用域，缺失时检查窗口/iframe/权限/虚拟化。不要靠猜坐标或取第一个匹配掩盖问题。
3. 把确定的操作和条件等待放进同一脚本/测试，减少模型逐步往返。等待可观察状态，设置条件超时及整个进程的硬超时。动作返回后检查后置条件；有副作用的动作不因超时盲目重试。
4. 用新测试数据或可追踪任务 ID 核对真实输出，补充与本次风险相关的失败场景。保留简短日志和必要证据；修复后只重跑受影响的检查及明确要求的验证。

中断后先读本次运行的日志：区分已完成步骤、等待中的步骤、已开始但结果未知的动作。UIA/AX 助手会保留 JSONL 进度；它用于恢复判断，不自动重放动作。等待断言的记录必须来自满足条件时的同一次观测，不能用稍后的值代替。

## 何时切换路线

缺少所需 Pattern/AX 动作、辅助功能权限、控件树不可用、调试端口不可用或纯自绘内容：记录具体探测结果，再评估已有应用接口、可测性改进、平台工具或视觉操作。首次短探测失败不是“所有结构化方法均不可用”的证据；也不要在同一路线上无边界重试。Mac 助手只检查已有授权，不触发提示或修改 TCC；Linux 当前只有可移植入口，没有本包原生 GUI 驱动。

用户禁止 Computer Use 时，保留该约束。确实缺少必要能力时，清楚说明尚未验证的部分及所需帮助。现有会话的通知、授权和工具边界仍适用；本技能不扩展权限。

## 交付证据

报告被测对象/版本、实际执行的路线和命令、断言与结果、必要产物、耗时及未覆盖部分。环境缺失、跳过、动作仅已发出、未知结果分别记录，不能计为通过。对旧失败和恢复后的重跑保留原因；不要以重试次数换取“全绿”。

本包已在 Windows 10 验证 CLI、HTTP、Playwright Chromium、Windows UIA 和 pytest-qt 的具体样例；新增 Mac 原生实现与验收用例尚无 Mac 实机结果，Windows 11 与 Linux 也未实测。范围与运行方法见 [实测记录](references/validation.md)。这些局部耗时不构成工具排行榜，也未测出相对 Computer Use 的加速倍数。研究来源与现成技能比较见 [调研](references/research.md)。

增加语言、框架或平台时，按 [扩展规范](references/extending.md) 复用已有入口、补充有针对性的样例和证据，再更新验证状态。

本包版本及本地维护边界见 [维护说明](references/maintenance.md)，使用与分发遵循 [MIT 许可](references/license.txt)。
