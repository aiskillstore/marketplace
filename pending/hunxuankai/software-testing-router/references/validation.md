# 验证覆盖、历史证据与限制

本包的小型能力校准实际执行了 CLI/HTTP、Playwright Chromium、Windows UIA、pytest-qt 和图像证据检查。它证明记录中的具体样例、断言和失败处理可运行，不是对任意生产软件的完整验收，也未证明相对 Computer Use 的加速倍数或统计性选型收益。

## 已执行的范围

2026-11-05 初版 `f958d20`：**19 项通过，0 失败、0 错误、0 跳过，pytest 23.06 秒**。包括 CLI/HTTP 4 项、DOM 2 项、Qt 内部事件循环 2 项、Windows UIA 9 项、透明像素证据 2 项。

同日优化版：**37 项通过，0 失败、0 错误、0 跳过，86.33 秒**。保留全部初版项目，增加 13 项桌面/探测检查及 5 项日志恢复与一致性检查：父区域消歧、独立/模态窗口、无关大子树、浅层检查、启动器与实际窗口拥有者、条件观测一致性、硬超时保留已完成步骤、阻塞动作结果未知、损坏或不一致日志拒绝成功。

- 初版 [结构化结果](evidence/results.json)、[JUnit](evidence/junit.xml)、[执行日志](evidence/calibration.txt)、[WinForms UIA](evidence/uia-winforms.json)、[Qt UIA](evidence/uia-qt.json)、[模型基线](evidence/agent-baseline.json)。
- 优化版 [完整结果与环境](evidence/optimization-20261105/results.json)、[JUnit](evidence/optimization-20261105/junit.xml)、[执行日志](evidence/optimization-20261105/calibration.txt)、[旧失败复现](evidence/optimization-20261105/before-regressions.json)。
- [性能样本](evidence/optimization-20261105/benchmark.json)、[代理实际使用](evidence/optimization-20261105/agent-use.json)、[未采用实验](evidence/optimization-20261105/rejected-experiment.json)、[研究来源](evidence/sources.json)。

600 个无关标签的同一 WinForms 样例，旧版/优化版各三个交替样本的中位耗时为 9796.88/8004.51ms，约减少 18.3%；均含新 worker 启动成本。provider 内部访问量没有测出，单一样例不能外推为通用速度比。代理样例也未证明模型调用数减少；候选版曾硬超时，再用新进程和新输出目录验证通过，原失败保留在证据中。

2026-11-06 搬迁前完整回归为 **36 通过、1 失败，153.22 秒**；600 标签用例在 `Ready` 断言及 `run_finished` 后触及 20 秒硬超时，未改代码的单项重跑 **13.58 秒**通过。这个环境时间波动不覆盖上述历史记录，也不以增加超时预算处理。更完整的本机日志及当前复现方法由维护仓库保存，不作为安装运行依赖。

## 验证环境与复现边界

`1.0.1` 的三份历史执行 JSON 是公开脱敏派生文件，仅替换 `/journal_path_at_execution` 中的本机目录，步骤、结果、时间和数值均保留。详见 [字段与哈希清单](evidence/public-redactions-1.0.1.md)；不能把其中的占位目录当成实际执行路径。

历史环境为 Windows 10 x64 10.0.19045、PowerShell 7.6.9、CPython 3.11.13、PySide6 Essentials / Qt 6.12.0、pytest 9.2.0、pytest-qt 4.5.0、Python Playwright 1.61.0、Chromium 149.0.7827.55 revision 1228（headless）、Pillow 13.0.0。

UIA Python 包装器仅用标准库；Windows provider 需要 Windows、PowerShell 7 和可交互桌面。测试样例由系统 .NET Framework 4.x `csc.exe` 编译。安装包包含四个相邻运行脚本和 17 个历史证据文件，不包含 tests、fixtures、测试依赖、浏览器 trace 或大型运行目录。

完整测试与基准复现命令位于维护仓库 `docs/validation.md`，须在仓库根目录准备开发依赖后执行；`scripts/run_uia.py --help` 可在本运行包中独立启动。帮助命令通过只证明入口可加载，不代表桌面交互完成验证。

Windows 11、其他浏览器、macOS/Linux 原生界面、移动端、C++ Qt、真实 Electron/WebView2、pywinauto/FlaUI 封装、UAC/锁屏/RDP、完整 PyInstaller 打包、真实视觉设计验收未在本包执行。非 Windows 的 skipped 不能算 Windows 通过；Qt offscreen 或 DOM/UIA 属性也不能冒充真实画面/EXE 验收。版本和维护边界见 [维护说明](maintenance.md)。
