# Windows UI Automation

UIA 是 Windows 的可访问性接口。它能读取属性并调用控件提供的 Pattern，不要求被测应用使用 Python，也不必有源码。WinForms、WPF、Win32、Qt 等提供程度各不相同；**实际控件和 Pattern 的探测结果比框架名称更可靠**。

本包用 PowerShell 7 + Windows 自带 UIAutomation 程序集。Python 包装器只用标准库，为可能卡住的 UIA provider 加上进程级硬超时。已有 pywinauto/FlaUI 项目可以沿用；本次没有声称另行实测这两个封装。

## 绑定目标并读取能力

记录 PID、实际可执行文件路径、窗口名称。启动器、虚拟环境 launcher、单文件 EXE 解包父进程可能不是窗口拥有者。检查子进程/实际窗口归属后再传入窗口拥有者；不能把所有同名进程视为目标。

窗口拥有者不确定时，先从**已确认的启动器 PID 和路径**做只读探测：

```powershell
python scripts/run_uia.py --pid 1234 --executable 'D:/Apps/Launcher.exe' `
  --probe --wait-seconds 5 --timeout 15 --report '.artifacts/owners.json'
```

`target` 给出唯一窗口拥有者的 `pid`、`executable` 和启动时间；`windows` 给出窗口名称。后续命令用该目标身份。多个相关进程拥有窗口时返回 `ambiguous`，不默认选择第一个；可以用 `--window` 的精确名称缩小探测。多个窗口属于同一进程时，进程可唯一，但执行计划仍需明确窗口。

探测只查看该启动器及其仍可验证的后代，不启动、激活、输入或关闭应用。启动器已经退出、权限不足、窗口未出现或关联进程超过上限时，报告缺失信息，不能扩大到所有同名进程。

```powershell
python scripts/run_uia.py --pid 1234 --executable 'D:/Apps/Sample.exe' `
  --window 'Sample' --inspect --inspect-depth 1 --timeout 15 --report '.artifacts/uia-inspect.json'
```

这里的 PID、路径、标题必须替换为实际观察到的值。返回 name、automation_id、control_type、class_name、enabled、offscreen 和支持的 patterns；默认不读取输入框文本。Pattern 名可能是 `InvokePatternIdentifiers.Pattern`、`ValuePatternIdentifiers.Pattern`。

大窗口先用 `--inspect-depth 1` 看根与直接子区域，按需要逐步增加深度。`0` 为完整深度；`depth_limited: true` 表示这是有深度限制的观察，不能声称已看过全部控件。`--max-nodes` 限制检查输出；不要为找到一个按钮每轮输出数百个无关节点。

`AccessibleName` 通常对应可访问 Name，不应假定它等于 AutomationId。Qt `objectName` 的映射同样取决于版本和 provider。由实际 inspect 结果选择稳定标识；每次执行重新查找元素，避免沿用失效引用。

## 一次运行完整步骤

将下面内容保存为 UTF-8 `steps.json`，按实际控件修改选择器：

```json
{
  "steps": [
    {"action": "set", "selector": {"name": "Item name", "control_type": "Edit"}, "value": "中文 样例"},
    {"action": "invoke", "selector": {"name": "Export", "control_type": "Button"}},
    {"action": "wait", "selector": {"name": "Result", "control_type": "Edit"}, "property": "value", "equals": "Exported"}
  ]
}
```

```powershell
python scripts/run_uia.py --pid 1234 --executable 'D:/Apps/Sample.exe' `
  --window 'Sample' --steps steps.json --wait-seconds 5 --timeout 30 `
  --report '.artifacts/uia-run.json'
```

支持精确匹配的 selector 字段：`name`、`automation_id`、`control_type`、`class_name`，组合时全部匹配。省略步骤的 `window` 时使用命令行窗口；步骤可指定同一进程的另一个顶层窗口，包含拥有者弹窗和独立窗口。

`within` 接受一个祖先 selector 或从外到内的 selector 数组。每一级都必须唯一；缺失或歧义时失败，不退回整窗查找。示例：

```json
{
  "steps": [
    {"action": "invoke", "within": {"name": "Primary actions", "control_type": "Group"}, "selector": {"name": "Apply", "control_type": "Button"}},
    {"action": "invoke", "selector": {"name": "Open window", "control_type": "Button"}},
    {"action": "invoke", "window": "Router independent confirmation", "selector": {"name": "Confirm", "control_type": "Button"}}
  ]
}
```

示例名称来自实测程序，实际任务需使用自己的控件信息。执行动作时由 UIA 条件在目标窗口/区域内筛选匹配元素，保持唯一性检查；不会先将整棵树全部读回模型。`diagnostics.elements_returned` 统计查询返回的元素数，不代表 provider 内部访问了多少节点。

动作：

| 动作 | 行为 |
|---|---|
| `set` | 对唯一可用、非密码且非只读控件调用 ValuePattern.SetValue |
| `invoke` | 对唯一可用控件调用 InvokePattern.Invoke，一次发出，不自动重复 |
| `wait` | 等待唯一控件的 `name` / `value` / `enabled` 等于 `equals` |

选择器字段不能为空；多匹配立即失败；无匹配/未就绪限时等待。默认完整检查最多返回 400 节点；动作的条件查询不因无关子树超过此数而失败。每次动作核对 PID、进程启动时间与 EXE 路径。外层超时终止自动化 PowerShell worker，保留目标应用，返回码 124。

`enabled` 的 `equals` 必须是 JSON 布尔值 `true` / `false`，不能写成字符串 `"false"`；`name` / `value` 的期望则必须是字符串。本助手先检查这些类型，避免 PowerShell 隐式转换造成错误通过。

`ok: true` 表示计划中的动作/断言完成。如果计划只包含 `invoke`，只证明调用已发出。仍需核验实际结果，例如重新打开本次导出的文件；本包测试在 UIA 成功之后独立检查内容。

## 超时与进度证据

每次调用分配 `run_id` 并创建独立 JSONL 日志。指定 `--report` 时日志默认放在报告旁；否则放在系统临时目录的 `software-testing-router` 下。返回的 `journal_path` 指向本次日志，也可用 `--journal` 指定**不存在的新文件**。已有日志不覆盖，创建失败时不执行动作。

步骤开始、动作开始、步骤完成都会刷新到磁盘。硬超时后，报告保留有效日志前缀里的 `steps` 和 `incomplete_step`：

| 字段/值 | 含义 |
|---|---|
| `steps[].status = dispatched` | 该调用已返回，业务结果仍需验证 |
| `steps[].status = asserted` | 同一次观测满足了条件；`observed_at` 是记录时间 |
| `incomplete_step.phase = locating` | 等待目标/状态中；没有记录该步动作开始 |
| `incomplete_step.phase = acting`、`outcome = unknown` | 动作已开始，未获得可确认的完成记录 |
| `may_have_side_effects = true` | 本次至少有一次变更动作已开始；不意味着业务成功 |
| `journal_incomplete = true` | 日志缺失、损坏或尾行不完整，只使用有效前缀 |

恢复时先核对目标当前状态和实际产物。日志不是续跑或自动重试指令，也不能保证崩溃前最后一个操作没有执行。正常完成的报告用临时文件替换，避免读到半写 JSON。

总硬超时包含 worker 初始化、所有定位、所有条件等待和动作执行；它不是“每个步骤的超时”。根据已观察的定位耗时和计划长度设置总预算，超时后先读日志而不是直接放大预算重放。实际模型使用验证中保留了 20 秒预算不足的失败及在新进程、新输出目录中重新验证的记录。

`--wait-seconds` 是条件轮询的软预算：进行中的原生 UIA 调用无法由该循环抢断，返回时可能已超过这个值。严格限制整个调用使用外层 `--timeout`。大窗口样例里确实出现过这种差异，不能将“设置了 5 秒”等同于每次调用必在 5 秒内返回。

本机另实测到一个兼容性要求：Windows UIA 在直接 `FromHandle` 之前先执行一次限定 PID 的桌面 `FindAll`，才能正确初始化所需的客户端代理；否则部分 WinForms 控件可能只显示成没有 Pattern 的 Pane。助手已处理这个初始化顺序，无需额外扫描整台桌面。

## 常见不通原因

- **没有窗口**：先查 PID 是否属于启动器、窗口是否未就绪、窗口标题是否正确、会话是否可交互。
- **没有所需 Pattern**：记录实际支持列表。选择、展开、文本编辑等 Pattern 不能互相替代；当前小助手只实现表内三种动作。
- **虚拟化列表**：项目可能尚未生成对应元素，应使用现有框架的滚动/实现化能力再定位。
- **权限/桌面隔离**：完整性级别、UAC 安全桌面、锁屏、RDP 断连、系统服务会话都可能阻止访问。不要将失败包装成通过或自动提权。
- **调用成功但无业务结果**：检查状态、路径、错误提示和文件，不直接回放 Invoke。Qt 某些选择 Pattern 改变“选中”不一定触发业务监听的“当前项变化”。

本助手不注入全局键鼠，也不提供盲目坐标回退。若必须测试焦点、键盘快捷键、拖拽或原生菜单，应为相应用户事件选择合适驱动并单独验证；Pattern 调用不能证明所有物理输入路径。

参考：[Microsoft UIA Pattern 概览](https://learn.microsoft.com/en-us/dotnet/framework/ui-automation/ui-automation-control-patterns-overview)。
