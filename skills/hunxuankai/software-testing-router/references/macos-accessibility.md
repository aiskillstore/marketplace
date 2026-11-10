# macOS 原生 Accessibility 测试

验收需要真实窗口的文本填写、按钮与后置状态时，探测系统 AX 属性和动作。只需 JSON 转换且已有正式 CLI 时，沿用 [CLI/API](cli-api.md)。本包 Mac 驱动已实现，但没有 Mac 实机验证；不能从 Windows 样例、模拟原生接口或帮助命令外推兼容性。

## 环境与目标身份

运行需要 **macOS、64 位 Python 3.10+ 标准库、可交互桌面和已有辅助功能授权**；预期覆盖 Intel x86_64 与 Apple Silicon arm64，两者均未实测。通过 ctypes 加载系统 Core Foundation、ApplicationServices 与 libproc，不需要 PowerShell、PyObjC、Swift 或 Xcode。Swift/AppKit 仅用于维护仓库的原生验收样例。

助手只调用 `AXIsProcessTrusted()` 检查已有权限，权限缺失返回结构化失败，不触发授权提示、不修改 TCC、不代替用户授权。需要用户处理权限时按当前会话通知/授权规则请求，等实际处理后重新核验；不要自动反复尝试。锁屏、登录界面、非交互会话与受保护目标没有本包成功证据。

由实际观察取得窗口拥有者 PID 和程序路径，`--executable` 必须指向 `.app/Contents/MacOS/...` 的真实文件，不能用 `.app` 目录。核验路径及秒/微秒启动时刻，防止 PID 重用。`--probe` 只列出**已指定并核验 PID**的窗口；与 Windows 的启动器/窗口拥有者探测不同，不寻找后代或按进程名称猜目标。

## 先检查，再执行一个完整流程

以下在独立运行包根目录使用 POSIX shell。PID、程序文件、窗口标题必须来自当前目标；示例字段名则要根据 inspect 实际结果调整。

```sh
python3 scripts/run_desktop.py --pid "$target_pid" --executable "$target_executable" --probe --timeout 15
python3 scripts/run_desktop.py --pid "$target_pid" --executable "$target_executable" --window 'Router Sample' --inspect --inspect-depth 2 --max-nodes 200 --timeout 20
```

selector 字段直接对应原始 AX 属性，不套用 Windows UIA 名称或网页 role：

| selector / 观察字段 | 原始 AX 属性 | 说明 |
|---|---|---|
| `title` | `AXTitle` | 标题；输入框不一定有标题 |
| `identifier` | `AXIdentifier` | 目标实际公开的稳定标识；可能缺失 |
| `description` | `AXDescription` | 描述；不能假定等于 title |
| `role` / `subrole` | `AXRole` / `AXSubrole` | 原始名称，例如 `AXTextField`、`AXButton` |
| `value` / `enabled` | `AXValue` / `AXEnabled` | wait 按需观察；enabled 使用 JSON 布尔值 |

组合字段全部精确匹配，目标必须唯一。inspect 默认不读取或输出文本值；密码控件的值不读取、不写入。扫描受 `--max-nodes` 和 `--inspect-depth` 限制，动作定位超出预算返回范围不足，不能把部分扫描当成唯一匹配。重名时通过 `within` 指定一个祖先 selector，或从外到内的非空数组，每一级都必须唯一；失败不会扩大到全局。窗口通过 `AXTitle` 精确匹配，可用步骤 `window` 切换到同一 PID 的其他窗口。

假设 inspect 实际确认下列标识，保存 UTF-8 `steps.json`：

```json
{"steps": [
  {"action": "set", "selector": {"identifier": "item-name", "role": "AXTextField"}, "value": "中文 样例"},
  {"action": "set", "selector": {"identifier": "quantity", "role": "AXTextField"}, "value": "3"},
  {"action": "invoke", "selector": {"identifier": "export", "role": "AXButton"}},
  {"action": "wait", "selector": {"identifier": "result", "role": "AXTextField"}, "property": "value", "equals": "Exported"}
]}
```

```sh
python3 scripts/run_desktop.py --pid "$target_pid" --executable "$target_executable" --window 'Router Sample' --steps steps.json --wait-seconds 5 --timeout 20 --report run.json --journal run.jsonl
```

也可直接调用 `scripts/run_macos.py`。每次运行用新的日志和输出目录，JSONL 已存在时停止。重新打开本次导出的 JSON，独立核对内容与预期；按钮动作返回、wait 成功和文件存在分别不足以证明业务结果。使用新的任务 ID 或空输出目录排除旧文件。

`set` 只向已启用、非密码且 AXValue 可设置的 AXTextField/AXTextArea 写入字符串；`invoke` 要求已启用并暴露 `AXPress`，只调用一次；`wait` 支持 title/value 字符串及 enabled 布尔期望，报告值来自满足条件时的同一次观察。完整计划先校验动作、selector、类型与数值，再执行；每步重新获取窗口和控件，不允许外部 PID 元素成为动作目标。

## 超时与未知结果

条件等待有有限预算，外层硬超时覆盖初始化与完整计划，终止自动化 worker 后保留被测应用。原生调用失败与属性缺失分别报告，不吞成空属性。JSON 报告原子写入；JSONL 使用 schema_version 1，动作前刷新 `action_started`，保留完成步骤供恢复判断。

若已有动作开始记录，而原生调用失败或 worker 被终止，结果为 **unknown**。先读日志、核对目标状态和本次产物，决定是否需要人工处理；助手不自动重放或扩大权限，也不执行全局键鼠、坐标回退、应用启动/关闭或提权。原生 ABI、TCC 权限归属、实际控件与不同 macOS 版本仍需具备环境后的串行实机验收，跳过不能计通过。范围见 [验证摘要](validation.md)，扩展方式见 [扩展规范](extending.md)。
