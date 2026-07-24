---
name: quantall-mcp
description: >
  QuantAll（全A解析）MCP —— 股市全市场向量化计算引擎，为 AI 提供本地 Python 计算环境。
  AI 编写向量化代码片段，数秒内完成 5000+ 股票的因子计算、策略回测、IC 分析和 GPU 可视化。
  让 AI 从"信息查询者"升级为"数据计算者"——用代码算出客观结果，而非搬运网络观点。
  触发：用户明确提到"回测""因子分析""IC分析""选股策略""QuantAll""全A解析"等量化关键词时。
  不主动在普通股市聊天中触发，仅在用户有明确量化分析需求时使用。
  能力声明：本技能需在用户电脑上创建 Python 虚拟环境（300MB+）、安装 quantall 库、
  修改 MCP 配置、启动本地 HTTP 服务（localhost:8686）、创建配置文件和启动脚本。
  所有涉及用户电脑的操作，AI 必须事先告知用户并获得同意。
  UpdateStock 为可选辅助 MCP（数据库管理，需 tushare API），非 QuantAll 必需。
agent_created: true
license: MIT
---

# QuantAll（全A解析）MCP 技能

---

## 这是什么

QuantAll 是一台运行在用户本地电脑上的**全市场向量化计算引擎**。它把 A 股 5000+ 只股票、150+ 维度的数据组织为统一矩阵，AI 只需编写简短的 Python 向量化代码片段，就能在数秒内完成全市场运算——因子计算、策略回测、IC 分析、多维可视化。

**对 AI 的意义**：不再只是"查询信息然后转述"，而是能**用代码算出客观结果**。用户问"小盘股是不是比大盘股表现好"，AI 不需要去搜索别人的观点，而是直接用全市场数据算出 IC 指标、回测收益，给出有数据支撑的结论。这是从"数据搬运工"到"数据分析师"的根本转变。

> **工具详细用法**（参数、触发场景、代码模板、核心函数）在 `scripts/data/ai_prompts.toml` 中，MCP 连接后 AI 自动获取。SKILL.md 只讲顶层定位、安装、启动、更新和 AI 行为规范。实战案例参见 `references/quantall_playbook.md`。

---

## 架构

| 组件 | 类型 | 定位 | 依赖 |
|------|------|------|------|
| **QuantAll**（全A解析） | HTTP MCP (localhost:8686) | 计算引擎：因子计算/回测/IC分析/可视化 | 本地 DuckDB 数据库 |
| **UpdateStock** | stdio MCP（可选） | 数据库管理：创建/更新/查询行情 | tushare API key |

两者共用同一个 DuckDB 数据库，路径通过 `scripts/DB_setting.json` 管理。**QuantAll 独立可运行，UpdateStock 不是必需依赖**——有自己的数据库或仅用内置测试库即可。

---

## 📦 安装（首次安装，AI 必读）

> ⚠️ **AI 行为规范**：安装前必须告知用户以下操作内容并获得同意：
> - 在 `scripts/` 下创建 Python 虚拟环境（约 45 个依赖包，300MB+ 磁盘空间）
> - 从清华 PyPI 镜像源下载安装 quantall 库
> - 修改 `~/.workbuddy/mcp.json` 添加 MCP 服务配置
> - 后续启动时会运行本地 HTTP 服务（localhost:8686）并可能弹出用户协议窗口

```
□ 1. 创建 venv：
   <Python路径> -m venv <skill-dir>/scripts/.venv
   推荐：C:/Users/<用户>/.workbuddy/binaries/python/versions/3.13.12/python.exe

□ 2. pip 安装（务必用清华源，否则 PySide6 等大包下载超时）：
   <skill-dir>/scripts/.venv/Scripts/python.exe -m pip install quantall -i https://pypi.tuna.tsinghua.edu.cn/simple

□ 3. 验证安装：
   <skill-dir>/scripts/.venv/Scripts/python.exe -c "from QuantAll import Start_main; print('OK')"

□ 4. 配置 MCP（修改 ~/.workbuddy/mcp.json）：
   见下方 MCP 配置

□ 5. 启动服务：
   <skill-dir>/scripts/.venv/Scripts/python.exe <skill-dir>/scripts/Start_QuantAll.py
   检查 8686 端口是否监听

□ 6. ⚠️ 提醒用户重连 MCP 连接器（或重启 WorkBuddy）
```

**常见坑**：
- **Git Bash 路径**：传参给 Python 必须用 `C:/` 前缀（非 `/c/`），否则双重转义找不到文件
- **safe-delete 冲突**：WorkBuddy Python 运行时可能拦截 pip 文件覆盖，报 `SAFE_DELETE_FAIL_CLOSED`。解决：重建 venv（`rm -rf .venv && python -m venv .venv`）后重试，或用 `dangerouslyDisableSandbox: true`
- **import 大小写**：`from QuantAll import ...`（大写 Q、A），`import quantall` 会失败

### MCP 配置

```json
{
  "mcpServers": {
    "全A解析": { "url": "http://127.0.0.1:8686/mcp", "disabled": false },
    "UpdateStock": {
      "command": "<skill-dir>/scripts/.venv/Scripts/python.exe",
      "args": ["<skill-dir>/scripts/UpdateStock_skill.py"],
      "disabled": false
    }
  }
}
```

> UpdateStock 可选——不配置也能用 QuantAll。仅需要计算引擎时只配「全A解析」。

### 数据库

QuantAll 首次启动自动创建 `scripts/DB_setting.json`，默认连接 pip 包内置的 Test.duckdb（仅沪深300近两年基础行情，**仅供测试，pip 更新会覆盖**）。

正式使用需切换到自己的数据库（修改 `db_path`）：

| 方案 | 说明 |
|------|------|
| A. 内置 Test.duckdb | pip 包自带，仅沪深300近两年基础行情，仅供测试 |
| B. UpdateStock 创建 | 需 tushare：2000+ 积分全市场 / 200 积分免费精简版 |
| C. 自有数据库 | 修改 `DB_setting.json` 的 `db_path` 直连 |

> ⚠️ **AI 行为规范**：修改 `DB_setting.json` 前告知用户当前数据库路径和将要切换的目标路径。

### 桌面快捷方式（可选，AI 主动询问）

安装后 AI 应主动询问："是否需要创建桌面快捷方式？"创建 `scripts/run.bat`（后台启动，无控制台窗口），再为它创建桌面 `.lnk`。

> ⚠️ **不要在桌面创建 .bat 文件**——Windows cmd 以 GBK 读取 .bat，AI 写入的 UTF-8 中文会乱码。正确做法：先创建 `scripts/run.bat`，再创建指向它的桌面 `.lnk`。

---

## 🚀 启动

QuantAll 是独立的 HTTP 服务，**不依赖 UpdateStock 启动**。三种方式任选其一：

| 方式 | 操作 | 适用场景 |
|------|------|---------|
| AI 调用 | 通过 UpdateStock MCP 的 `Start_QuantAll` 工具 | AI 场景，可自动检测端口 |
| 双击 run.bat | 后台启动，无控制台窗口 | 手动场景最方便 |
| 命令行 | `<skill-dir>/scripts/.venv/Scripts/python.exe Start_QuantAll.py` | 调试或自定义 |

> ⚠️ **AI 行为规范**：启动服务前告知用户——QuantAll 将在本地 8686 端口启动 HTTP 服务，并可能弹出用户协议确认窗口。

**用户协议**：首次启动弹协议窗口，点击确认即"激活"（永久同意），功能无差异。未确认前除 `ping` 外所有工具被阻止（合规要求）。

**MCP 重连**：QuantAll 后于 AI 启动时，需断开重连 MCP 连接器（或重启 WorkBuddy）。首次连接需点击"信任"授权。

---

## 🔄 更新/升级

> **核心规则**：技能包文件更新后，Python 库 `quantall` 也必须同步升级，否则新接口在旧库上会报错。

```
□ 1. 升级库：
   <skill-dir>/scripts/.venv/Scripts/python.exe -m pip install --upgrade quantall -i https://pypi.tuna.tsinghua.edu.cn/simple

□ 2. 验证版本：
   <skill-dir>/scripts/.venv/Scripts/python.exe -c "import QuantAll; print(QuantAll.__version__)"
   确认 >= requirements.txt 要求的版本

□ 3. 重启 QuantAll 服务（先关旧进程再启动）

□ 4. ⚠️ 提醒用户重连 MCP
```

- safe-delete 冲突时：先 `pip uninstall quantall`，再 `pip install quantall`
- `pip install --upgrade` 是幂等的，不确定是否需要升级时直接执行
- 版本检测：对比 `_meta.json` 的 version 与已安装库 `QuantAll.__version__`

---

## ⚠️ AI 操作用户电脑的行为规范

本技能涉及多项用户电脑操作。AI 执行前**必须告知用户**将要做什么、产生什么影响：

| 操作 | 告知内容 |
|------|---------|
| 创建 venv | 将在 `scripts/` 下创建虚拟环境（约 300MB 磁盘空间） |
| pip install | 从清华源下载约 45 个包（含 PySide6 等大型包） |
| 修改 mcp.json | 将添加 MCP 服务配置到 `~/.workbuddy/mcp.json` |
| 启动服务 | 将在 localhost:8686 启动 HTTP 后台服务 |
| 创建文件 | 可能创建 `DB_setting.json`、`run.bat`、桌面 `.lnk` 快捷方式 |
| 修改数据库路径 | 将修改 `DB_setting.json` 的 `db_path`，影响 QuantAll 读取的数据 |

> **原则**：不在用户不知情的情况下执行任何系统操作。涉及文件创建、配置修改、服务启动等操作前，先说明意图，获得用户同意后再执行。

---

## 工具总览

安装并连接 MCP 后，AI 通过 `scripts/data/ai_prompts.toml` 自动获取每个工具的详细用法（参数、触发场景、代码模板、核心函数）。以下是概览：

| 工具 | 用途 |
|------|------|
| `ping` | 健康检查 |
| `available_data` | 查看可用数据字段 |
| `how_code` | 查看代码执行环境说明 |
| `strategy_backtest` | 策略回测（收益/夏普/回撤/胜率） |
| `factor_analysis` | 因子 IC 分析 |
| `batch_factor_analysis` | 批量因子 IC 分析 |
| `batch_factor_corr` | 因子间批量相关性计算 |
| `save_factor_result` | 保存因子分析结果到数据库 |
| `new_layer_from_code` | 创建可视化图层标记 |
| `select_by_code` | 筛选股票（集合运算） |
| `batch_select` | 批量筛选（多条件对比/交集/并集） |
| `move_by_code` | 坐标平移映射 |
| `weight_by_code` | 权重设置 |
| `batch_weight` | 批量权重对比（多权重方案） |
| `heat_map` | 热力图统计 |
| `get_user_selection` | 获取用户 GUI 交互选中 |
| `MCP_Close` | 关闭服务 ⚠️（仅不再需要时调用） |

### AI 使用前必知

- **先 ping 确认服务就绪**，未启动则引导用户启动
- **先 available_data 确认字段**，不要假设字段名（数据库字段名经 `db_translate.json` 翻译层映射为中文）
- **不支持并行调用**，所有工具串行执行（一个返回后再发下一个）
- **代码必须向量化**：禁止 import / 循环 / lambda / axis=1，最后一行设 `out = ...`
- **复权价格手动算**：`adj_close = d['close'] * d['adj_factor']`
- **每股因子必须除以 close**（非复权价），比率类/增长率类不需要
- **持仓矩阵必须用 `hold_until(buy, sell)`**，禁止手写逆序 cumsum
- **内置函数**：`hold_until`/`entry_check`（持仓）、`time_at`/`time_between`/`time_in`（时间）、`row_rank`（截面排名）、`row_top_n`/`row_bottom_n`（截面 Top/Bottom N 筛选）
- **detail 视图返回约 140 万字符**，AI 内部分析后只汇报结论，禁止直接展示

> 详细参数说明、触发场景、代码模板、核心函数参考：`scripts/data/ai_prompts.toml`
> 实战案例、模式对比、踩坑记录：`references/quantall_playbook.md`

---

## 版本历史

- **v1.0** — 首版发布。13 个工具，配套 ai_prompts.toml 和 playbook 实战手册。PyPI 在线安装。
- **v1.0.1** — 新增技能升级流程；requirements.txt 更新为 >=1.0.1；SKILL.md 精简至 500 行以内。
- **v1.0.2** — 优化 clawhub 审查问题：触发条件收窄（仅明确量化需求时触发）、能力声明透明化（venv/pip/mcp.json/HTTP 服务全部显式声明）、新增 AI 操作用户电脑的行为规范表、详细工具用法指向 ai_prompts.toml 不在 SKILL.md 展开。新增批量分析工具 `batch_weight`/`batch_select`（对应 `weight_by_code`/`select_by_code` 的批量版本）。新增 `batch_factor_corr`（因子间批量相关性计算，支持自定义基准因子）。新增 `how_code`（代码执行环境说明，帮助 AI 快速上手）。新增 exec 内置函数 `row_top_n(df,n)`/`row_bottom_n(df,n)`（截面 Top/Bottom N 筛选）。热力图/直方图统计新增 `summary` 评估参数（分布均匀度/边缘突发等）。`batch_weight` 新增 `view` 参数（summary=评估参数/heatmap=完整矩阵）及"权重未改变"提示。`batch_select` mode 重命名为描述性名称（independent_summary/independent_heatmap/intersect/union）。修复批量因子分析执行异常及 batch_select intersect/union/independent 模式 bug。requirements.txt 固定版本号。
