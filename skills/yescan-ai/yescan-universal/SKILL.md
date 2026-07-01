---
name: yescan-universal
description: 当用户需要对图片进行文字识别（OCR）、图片翻译、画质增强（去除水印/阴影/手写/底色/屏纹等瑕疵，矫正，高清增强，素描/线稿转换等）、格式转换（转 Word/Excel/PDF）或 AI 生成（证件照）时使用此技能。即使用户没有明确提到具体功能名称，只要涉及图片处理、文字提取、文档转换、图像优化或证件照生成，都应触发此技能。不适用于视频处理、纯文本编辑或非图片输入的任务。夸克扫描王图片处理能力中心。
license: MIT
compatibility: Requires pip3 install yescan and SCAN_WEBSERVICE_KEY configuration. Performs network calls to scan-business.quark.cn.
metadata:
  author: yescan-ai
  version: "1.0.5"
  homepage: https://scan.quark.cn/business
---

## 执行流程

每次执行严格按 **Plan → Execute → Verify** 顺序进行，不得跳过或乱序。

### Plan — 理解意图，发现能力

1. 确认环境就绪（每次执行，不得跳过）：
   - **安装 & 升级**：
     1. `yescan --version` — 未安装则执行 `pip3 install yescan`；若版本 < 1.0.5，执行 `pip3 install yescan --upgrade`，升级完成后才继续
     2. `pip3 index versions yescan` — 若 INSTALLED < LATEST，告知用户有新版本可用并提供升级命令：`pip3 install yescan --upgrade`，由用户决定是否升级
   - **密钥检查**：`yescan config get SCAN_WEBSERVICE_KEY`，未配置则引导用户配置
     - 设置命令：`yescan config set SCAN_WEBSERVICE_KEY <your_api_key>`
     > Key 获取方式：https://scan.quark.cn/business → 开发者后台 → API Key

   > **Checkpoint**：版本 < 1.0.5 → 必须升级后才能继续。版本 ≥ 1.0.5 但不是最新 → 提示用户后可继续。密钥未配置则引导配置后再继续。

2. 发现能力：
   ```bash
   yescan --list-scenes              # 获取全部场景及意图描述
   yescan --list-scenes <scene>      # 获取该场景的 --set 参数
   ```
   从输出中匹配用户意图到具体场景
3. 多步处理时，向用户展示完整步骤计划

**Gate**：
- 「确认环境就绪」每一步均为硬性前置，不得跳过任何一步，未全部通过 → 禁止进入 Execute：
  1. 未执行 `yescan --version` 确认安装状态 → 禁止继续
  2. 版本 < 1.0.5 且未完成升级 → 禁止继续
  3. 未执行 `pip3 index versions yescan` 确认最新版本状态 → 禁止继续
  4. 未执行 `yescan config get SCAN_WEBSERVICE_KEY` 确认密钥已配置 → 禁止继续
- 只执行用户明确需要的场景，不主动添加额外步骤。为提升当前任务效果的辅助操作不受此限
- 文档转换（Word/Excel/PDF）直接处理图片，不依赖 OCR 结果。两者输入都是图片，是独立操作
- 场景名和 `--set` 参数必须来自本次会话的 CLI 输出
- 未执行过 `--list-scenes` 则不得进入 Execute
- 场景有 `--set` 参数且用户未明确指定时，须向用户展示可选参数并确认后再执行

### Execute — 执行场景

```bash
yescan --scene <SCENE> --path <FILE> --platform "${AGENT_NAME}" [--output <DIR>] [--set key=value]
yescan --scene <SCENE> --url  <URL>  --platform "${AGENT_NAME}" [--output <DIR>] [--set key=value]
```
> `--path` 传本地文件路径，`--url` 传 http/https 链接。

> 把 `${AGENT_NAME}` 替换为当前 Agent 平台名称（如 openclaw、hermes、qoderWork、wukong、coze、claudecode 等），无法确定时填 `community`，禁止猜测或自造。

- 单步：直接执行
- 多步处理为逐步 Execute → Verify 循环：step N+1 的命令在 step N Verify 通过后才构造，`--path` 取自 step N 响应中的 `data.path`

**Gate**：
- 多步处理时向用户说明步骤计划
- 每步命令不得预先构造
- `--set` 参数不跨场景沿用

### Verify — 验证并交付

每步执行后检查响应中的 `code` 字段：

- **成功**（`code` 为 `"00000"` 或 `0`）→ 进入交付
- **失败** → 不继续下一步，根据错误信息处理（详见 Gate）

交付标准 — 以下条件满足才算完成：

- **OCR 识别**：识别内容已以可读文本呈现给用户
- **图片翻译 / 图像增强 / AIGC**：输出文件路径已告知用户
- **文档转换**：输出文档路径和格式已告知用户

**Gate**：
- code 非成功 → 不得继续下一步，不得报告成功
- 根据错误信息自行修复（如场景名无效 → 重新 `--list-scenes`）或将错误原因告知用户
- 用户未看到结果 → 未完成

---

## 约束

- **输入方式**：`--path` 或 `--url`，二选一。不支持 base64（如需则先写入临时文件）
- **URL 引号**：`--url` 参数须用单引号包裹，避免 shell 对 `!` `$` 等特殊字符的解析
- **文件大小**：≤ 5MB
- **图片来源**：仅限用户当次请求中明确指定的文件或 URL
- **禁止伪造**：不得编造或模拟 yescan CLI 的请求参数或响应输出；所有场景名、参数值和执行结果必须来自实际运行的 CLI 命令

---

## 参考文档

- [references/privacy.md](./references/privacy.md) — 隐私、数据流向与密钥安全
- [references/troubleshooting.md](./references/troubleshooting.md) — 错误码与排错
- [references/implementation.md](./references/implementation.md) — 实现细节：CLI 行为与响应字段
- [SECURITY.md](./SECURITY.md) — 安全策略与数据流声明