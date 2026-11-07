# 验证覆盖、历史证据与限制

本包的小型能力校准在 Windows 10 实际执行了 CLI/HTTP、Playwright Chromium、Windows UIA、pytest-qt 和图像证据检查。它证明记录中的具体样例、断言和失败处理可运行，不是对任意生产软件的完整验收，也未证明相对 Computer Use 的加速倍数或统计性选型收益。1.1.0 新增 [macOS AX](macos-accessibility.md) 实现，但本次没有 Mac 硬件，原生 ABI、权限与 GUI **未实机验证**。

## 2026-11-07 整合验证

最终已审查运行版本 `35c727db6ca1c907bbc713470ff04387549373b1` 的 Windows 10 干净全套为 **339 通过、7 跳过、0 失败/错误，191.28 秒**；受控安装副本运行子集 **193 通过、0 跳过，18.28 秒**。7 项跳过类别仍为 3 项 Mac 原生、2 项原生 POSIX 大小写不敏感文件系统、2 项 OS symlink 权限检查。受控更新验证旧副本的完整备份及清单，安装包为 **40 文件/48 本地引用**；fixtures 来自维护仓库。

中间一次全套为 **336 通过、3 失败、7 跳过，160.19 秒**：一次 help-only GREEN 未设置 `PYTHONDONTWRITEBYTECODE`，产生 3 个被忽略的源 `.pyc`，使既有原始载荷比较失败。代码及 40 项清单文件字节未变；将确切 3 个缓存文件移到外部证据留存后，定向恢复 **3 通过，12.57 秒**，再完成上述干净全套。缓存未删除，失败与恢复均保留，没有调整实现或超时。最终审查另修正动作开始状态转移缺口并增加 15 项真实子进程用例，针对性审查通过。

Mac ABI、TCC、Swift/AppKit GUI、Intel/Apple Silicon 与真实 Mac 文件系统仍未实机验证。以下首轮整合与开发失败记录仍有效，不被最终通过覆盖；发行不扩展这些验证结论。

### 首轮整合记录

Windows 10 源码全套 **324 通过、7 跳过、0 失败/错误，176.90 秒**；受控安装副本的运行子集 **178 通过、0 跳过，14.23 秒**，运行模块来自安装副本，fixtures 来自维护仓库。7 项跳过是 3 项 Mac 原生、2 项原生 POSIX 大小写不敏感文件系统、2 项 OS symlink 权限/支持检查，不计通过。

干净提交 `14ce17bf2a70a78ee52817ac183c861e3c8ac17d` 的候选 ZIP 恰有一层 `software-testing-router/`，包校验 **40 文件/48 本地引用**，清单与提交源码一致；受控安装预览、安装及安装后清单核对通过。这是公开发行前的整合候选记录，文档隔离阶段的 36/48 不代表整合包，也不能代替包含最终文档的发行包。完整日志与清单留在维护仓库之外的新证据目录，不进入运行包。

以上包括真实既有 Windows GUI 路线和 Windows 宿主的 Mac 函数边界、策略与受控子进程检查，不能证明 Mac 系统 API 或窗口已运行。Mac ABI、TCC、Swift/AppKit GUI、Intel/Apple Silicon 与真实 Mac 文件系统仍未实机验证。

保留开发失败与恢复：安装检查首轮 6 项 fixture 失败经明确字节写入/导入路径修正后恢复；安装审查修正大小写别名重叠、普通 CLI bytecode 写入和 dash 路径转发；worker/runner 审查修正短/畸形成功、缺终止记录和 stdin Latin-1 mojibake。各项 RED/GREEN、早期自审和重跑记录由维护者保存；最终通过不覆盖旧失败，不增加超时掩盖问题。

## 2026-11-07 Mac 适配前基线与边界

适配前 Windows 10 完整回归为 **103 通过、1 跳过，166.27 秒**。跳过项是 `test_validator_rejects_file_symlink_if_supported`，原因是当前 Windows 缺少文件 symlink 权限或支持；跳过不算通过。这是开发前基线，不能代替新版本的整合回归。

独立检索 1.0.2 时，Mac 原生填写/导出场景缺少可调用驱动与步骤说明；CLI-only JSON 转换场景已正确沿用 CLI/API。1.1.0 补充入口、AX 字段、权限、范围与恢复 recipe，不把检索结果当真实 GUI 执行。

维护仓库提供 `RUN_MACOS_NATIVE_TESTS=1` 的串行原生验收：实际设置文本、调用 AXPress、等待状态并独立读取新 JSON，还检查重复控件的祖先范围及默认 inspect 不读值。非 Mac、未 opt-in、缺少交互桌面/Swift 编译器/已有授权时明确 skipped；不会修改 TCC。Swift/AppKit 仅用于构建测试样例，不是运行依赖。Windows 上的替身测试不证明 Mac 真实 ABI 或 GUI 可用；当前没有 Intel 或 Apple Silicon 的 native 成功记录。完整命令和本地新证据由维护仓库保存，不把机器路径写入本包。

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

UIA Python 包装器仅用标准库；Windows provider 需要 Windows、PowerShell 7 和可交互桌面。测试样例由系统 .NET Framework 4.x `csc.exe` 编译。新增 AX 使用 macOS 系统框架和 Python 标准库。安装包保留原四个相邻 Windows 运行脚本与历史证据，另含 Mac 运行模块和平台入口，不包含 tests、fixtures、安装工具、测试依赖、浏览器 trace 或大型运行目录。

完整测试与基准复现命令位于维护仓库 `docs/validation.md`，须在仓库根目录准备开发依赖后执行；`scripts/run_desktop.py --help` 及旧 Windows `scripts/run_uia.py --help` 可在本运行包中独立启动。帮助命令通过只证明入口可加载，不代表桌面交互完成验证。

Windows 11、其他浏览器、macOS/Linux 原生界面、移动端、C++ Qt、真实 Electron/WebView2、pywinauto/FlaUI 封装、UAC/锁屏/RDP、完整 PyInstaller 打包、真实视觉设计验收未在本包执行。Mac/Linux 的 CLI/API、DOM、Qt 路线仍依赖目标环境，未获得本包在这些系统的执行证据；Linux 暂无本包原生 GUI 驱动。非 Windows 的 skipped 不能算 Windows 通过，非 Mac 的 skipped 不能算 Mac 通过；Qt offscreen 或 DOM/UIA/AX 属性也不能冒充真实画面/EXE/.app 验收。版本和维护边界见 [维护说明](maintenance.md)。
