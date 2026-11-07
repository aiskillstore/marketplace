# Qt 内部交互测试

有 Python Qt 源码且验收涉及控件状态、信号、异步处理或取消时，可用 pytest-qt。此路线针对 Python Qt，Windows/macOS/Linux 均需该项目的源码、匹配绑定与可用环境；本包只有 Windows 10 的 PySide6 执行证据。原生交互另看 Windows UIA 或 [Mac AX](macos-accessibility.md) 实际公开的能力；新增 AX 未实机验证，Linux 暂无本包原生 GUI 驱动。C++ Qt 的 Qt Test 需要对应项目环境，不在本次实测范围内。

使用项目现有 Qt 绑定，避免混装 PySide 与 PyQt。`QT_QPA_PLATFORM=offscreen` 适合内部行为测试，不是实际桌面的显示、输入法、DPI 或打包验证。

关键做法：

- `qtbot.addWidget` 管理生命周期。
- 在触发动作之前建立 `qtbot.waitSignal`，避免错过快速信号。
- `qtbot.waitUntil` 等待实际完成条件；不靠固定睡眠猜工作完成时间。
- 验证取消时，在相关晚到事件可能出现的时间窗内检查不发信号、不继续写文件；窗口大小依据具体异步行为确定。

维护仓库的 `tests/test_qt.py` 实际运行 Qt 控件与事件循环，验证异步导出及取消；结果见本包 [验证摘要](validation.md)。下列命令仅在维护仓库根目录、准备测试依赖后执行，安装副本不包含这些样例：

```powershell
.venv/Scripts/python.exe -m pytest tests/test_qt.py -q
```

POSIX 虚拟环境使用 `.venv/bin/python -m pytest tests/test_qt.py -q`；每次设置新的外部 `--basetemp` 与 `PYTHONDONTWRITEBYTECODE=1`。Mac/Linux 需先核验该系统的 Qt wheel、插件和运行依赖，安装失败或 skipped 均不能记为测试通过。

`qtbot.assertNotEmitted(..., wait=250)` 是本样例专门观察 120ms 定时任务取消后的负向断言，不是建议给任意生产任务写死 250ms。

验收交付 EXE/.app 时，还应通过那个交付物的实际启动、界面和产物验证必要用户流程。本包 Qt 样例以解释器运行，不能冒充 PyInstaller 产物测试或 Mac 原生验收。不同层次的通过状态应分别报告。

参考：[pytest-qt 信号等待](https://pytest-qt.readthedocs.io/en/latest/signals.html)。
