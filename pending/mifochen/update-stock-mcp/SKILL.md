---
name: update-stock-mcp
description: >
  UpdateStock MCP 服务技能 —— 通过 stdio 模式调用 UpdateStock 脚本，
  提供 A 股 DuckDB 数据库管理功能：创建数据库、全量/增量更新股票数据、查询股票行情。
  设计的数据库方案兼容 QuantAll（全A解析）计算引擎。
  触发条件：用户提到"UpdateStock"、"创建股票数据库"、"更新股票数据"、"获取股票数据"等。
agent_created: true
license: MIT 
---

# UpdateStock MCP 技能

通过 stdio MCP 管理 A 股 DuckDB 数据库——创建、更新、查询股票行情数据。数据库方案兼容 QuantAll（全A解析）计算引擎。

> 💡 **如需使用 QuantAll**：推荐安装 `QuantAll-mcp` 技能（`pip install quantall`），其中包含 QuantAll 的详细使用文档。本技能负责为其准备兼容的数据库。

---

## 安装前准备

### 1. 填写 tushare API token

技能目录下已包含 `API_tushare.txt`（空白文件），**请先填入你自己的 tushare API token**，否则无法获取 tushare 数据。

获取方式：访问 https://tushare.pro/register 注册，登录后在个人中心复制 token，粘贴到 `API_tushare.txt` 中保存。

> 即使不填 token，脚本仍可通过 baostock（免费，无需注册）获取部分数据。

### 2. 安装 Python 依赖

建议使用虚拟环境隔离：

```bash
# 在 scripts 目录下创建虚拟环境
<你的Python路径> -m venv scripts/.venv

# 用清华镜像源安装依赖
scripts/.venv/Scripts/python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

所需依赖（见 `requirements.txt`）：
- `mcp` — MCP Python SDK（提供 FastMCP）
- `pydantic` — 参数校验
- `pandas` — 数据处理
- `numpy` — 数值计算
- `duckdb` — DuckDB 数据库引擎
- `tushare` — A 股数据接口（需注册获取 API token）
- `baostock` — 备用数据源（免费，无需 token）

### 3. 配置 MCP（stdio 模式）

在 `~/.workbuddy/mcp.json` 的 `mcpServers` 中添加：

```json
"UpdateStock": {
  "command": "C:/Users/<用户>/.workbuddy/skills/update-stock-mcp/scripts/.venv/Scripts/python.exe",
  "args": ["C:/Users/<用户>/.workbuddy/skills/update-stock-mcp/scripts/UpdateStock_skill.py"],
  "disabled": false
}
```

> 路径使用正斜杠 `/`，避免反斜杠转义问题。
> 配置完成后需在 WorkBuddy 连接器管理中断开重连（或重启智能体），首次连接需点击「信任」。

### 4. DB_setting.json（自动创建）

技能包**不携带** `DB_setting.json`。UpdateStock 首次启动时检测到缺失会自动创建默认配置文件，默认连接同目录下的 `Test.duckdb`。

> ⚠️ **Test.duckdb 仅供测试**：首次调用 `Creat_DB` 留空路径时自动创建，仅含基础表结构（无数据）。正式使用时请通过 `Creat_DB` 指定独立路径创建数据库。

`DB_setting.json` 结构：

```json
{
  "db_path": "./Test.duckdb",
  "days": 730,
  "stock": "stock",
  "map_stock": { "trade_date": "trade_date", "symbol": "symbol", ... },
  "stock_index": "stock_index",
  "map_stock_index": { ... },
  ...
}
```

每个 `map_*` 字段定义了对应表的列名映射，用户使用自有数据库时修改这些映射即可适配实际字段名。

---

## 可用工具

### mcp__UpdateStock__ping — 连接检测

无参数。返回 `Pong` 表示服务正常。

```
DeferExecuteTool(toolName="mcp__UpdateStock__ping", params={})
```

### mcp__UpdateStock__Creat_DB — 创建数据库

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| DB_path | string | `""` | 数据库路径，留空则使用同目录下 `Test.duckdb` |

创建的表：stock、stock_index、stock_basic、stock_factor、stock_forecast、stock_dividend、stock_report

```
DeferExecuteTool(toolName="mcp__UpdateStock__Creat_DB", params={"DB_path": ""})
```

### mcp__UpdateStock__Update_Stock_Data — 全量更新

> ⚠️ **首次从 0 开始更新数据库耗时非常长（可能需数小时）**，请在空闲时运行，避免中途中断。
> 需要 tushare 积分 2000+。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| ignore_check | boolean | `false` | 是否跳过部分检查 |

数据库路径和 API key 自动从 `DB_setting.json` 和 `API_tushare.txt` 读取，无需手动传入。

**7 个更新阶段**（每阶段持续发送 MCP 进度通知）：
1. 指数数据（上证指数、深证成指）
2. 股票行情（全市场日线）
3. 基础数据（股票列表、公司信息）
4. 行情因子（PE/PB/换手率/市值等每日指标）
5. 业绩预告
6. 分红
7. 财报 / 财务指标

> **阶段 7 特殊情况**：2000 积分接口不支持按日期批量获取财务指标，需先通过 `disclosure_date` 收集发布财报的股票清单，再逐只调用 `fina_indicator` 拉取。
> - **非财报披露窗口**（如 5~7 月）清单可能为空，属正常现象——没有公司在这些月份披露新财报。
> - **披露窗口**（3~4 月年报季、8 月中报季、10 月三季报季）可能涉及数千只股票，逐只拉取耗时数十分钟。
> - v2.2 起内置**心跳机制**：每更新 10 只或超过 30 秒无输出，强制发送进度（含 ETA），防止 AI 因长时间无响应而误判 MCP 断连。

```
DeferExecuteTool(toolName="mcp__UpdateStock__Update_Stock_Data", params={
  "ignore_check": false
})
```

### mcp__UpdateStock__Update_Stock_Data_easy — 增量更新（精简版）

> 适合 tushare 积分 120-200 的用户，仅更新指数行情和股票行情两张表。
> 通过 baostock 获取指数数据 + tushare 获取股票日线。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| ignore_check | boolean | `false` | 是否跳过部分检查 |

数据库路径和 API key 自动从 `DB_setting.json` 和 `API_tushare.txt` 读取。

```
DeferExecuteTool(toolName="mcp__UpdateStock__Update_Stock_Data_easy", params={
  "ignore_check": false
})
```

### mcp__UpdateStock__get_stock — 获取非复权股票行情

从数据库查询指定股票、指定时间范围的非复权行情数据。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| symbol | string | `"000001"` | 股票代码（6位数字） |
| start_date | string | `""` | 开始日期，格式 `YYYY-MM-DD` |
| end_date | string | `""` | 截止日期，格式 `YYYY-MM-DD` |

返回字段：trade_date, symbol, open, high, low, close, pre_close, vol, voe

```
DeferExecuteTool(toolName="mcp__UpdateStock__get_stock", params={
  "symbol": "000001",
  "start_date": "2026-05-01",
  "end_date": "2026-07-03"
})
```

### mcp__UpdateStock__get_adj_stock — 获取前复权股票行情

从数据库查询指定股票、指定时间范围的前复权行情数据（已自动处理分红送股除权）。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| symbol | string | `"000001"` | 股票代码（6位数字） |
| start_date | string | `""` | 开始日期，格式 `YYYY-MM-DD` |
| end_date | string | `""` | 截止日期，格式 `YYYY-MM-DD` |

返回字段：trade_date, symbol, open, high, low, close, vol, voe

```
DeferExecuteTool(toolName="mcp__UpdateStock__get_adj_stock", params={
  "symbol": "000001",
  "start_date": "2026-05-01",
  "end_date": "2026-07-03"
})
```

### mcp__UpdateStock__Start_QuantAll — 启动 QuantAll

无参数。在 localhost:8686 启动 QuantAll HTTP MCP 服务。内置端口检测，防止重复启动。

> 启动时会在 `scripts/` 目录下动态生成 `Start_QuantAll.py` 启动脚本，然后通过 subprocess 启动子进程。

> ⚠️ **用户协议**：QuantAll 首次启动会弹出用户协议确认窗口。**在用户点击确认之前，除 `ping` 外的所有 QuantAll 工具都将被阻止**——这是金融技能的法律合规要求。启动后请尽快到桌面找到弹窗并点击确认。

> ⚠️ **MCP 重连**：QuantAll 启动后，全A解析 MCP 连接需要断开重连才能生效。两种方式：①连接器管理页面手动重连（专家→连接器→自定义连接器→全A解析→断开→连接）；②重启智能体（推荐，自动重连所有 MCP）。

```
DeferExecuteTool(toolName="mcp__UpdateStock__Start_QuantAll", params={})
```

### mcp__UpdateStock__Set_QuantAll_DataBase — 设置数据库

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| path | string | `""` | 数据库路径 |
| days | int | `730` | 加载天数（默认两年） |

将数据库路径写入 `DB_setting.json`，QuantAll 下次启动时生效。

```
DeferExecuteTool(toolName="mcp__UpdateStock__Set_QuantAll_DataBase", params={
  "path": "D:/你的数据库路径/your_db.duckdb",
  "days": 730
})
```

---

## QuantAll 集成

本技能管理的 DuckDB 数据库可直接作为 QuantAll 的数据源。如需使用 QuantAll：

1. **安装 QuantAll**：推荐安装 `QuantAll-mcp` 技能（`pip install quantall`），该技能包含详细的 QuantAll 使用文档
2. **准备数据库**：通过本技能的 `Creat_DB` + `Update_Stock_Data`（或 `Update_Stock_Data_easy`）创建并填充数据库
3. **设置数据库路径**：调用 `Set_QuantAll_DataBase` 将数据库路径写入配置
4. **启动 QuantAll**：调用 `Start_QuantAll` 启动服务（首次启动需确认用户协议弹窗）
5. **配置 MCP**：在 `mcp.json` 中添加全A解析 HTTP MCP 配置：

```json
"全A解析": {
  "url": "http://127.0.0.1:8686/mcp",
  "disabled": false
}
```

6. 重连全A解析 MCP（连接器页面或重启智能体），首次连接需点击「信任」

---

## 数据库方案

### 方案 A：使用默认测试数据库（仅供功能验证）

调用 `Creat_DB` 留空路径时自动创建 `Test.duckdb`，仅含 7 张空表结构。用于验证数据库连接和工具可用性。

> ⚠️ **Test.duckdb 仅用于测试**，正式使用请通过方案 B/C 创建独立数据库。

### 方案 B：通过 UpdateStock 创建完整数据库

| 方案 | tushare积分 | 数据范围 | 调用工具 | 耗时 |
|------|------------|----------|----------|------|
| 完整版 | **2000+** | 全市场 5500+ 股票，全部表（行情/财务/因子/预告/分红/财报） | `Update_Stock_Data` | 首次数小时 |
| 精简版 | **120-200**（免费认证即可获得） | 指数行情 + 股票行情（仅 OHLCV） | `Update_Stock_Data_easy` | 较快 |

> **更新速度说明**：即使是增量更新也不快——部分数据需从最新缺失日期开始逐天确认是否有新数据，且 tushare 部分接口本身响应较慢。
>
> **心跳机制（v2.2+）**：阶段 7（财务指标）逐只拉取时，内置计数+时间双触发心跳——每 10 只或 30 秒无输出即发送进度。进度格式为 `财报拉取进度 1523/5530（27%）已耗时 5m12s 预计剩余 13m40s`，确保 AI 不会因长时间无响应而误判 MCP 断连或进程崩溃。

操作步骤：
1. 调用 `Creat_DB` 创建独立数据库（指定新路径，**不要覆盖 Test.duckdb**）
2. 调用 `Set_QuantAll_DataBase` 将新数据库路径写入设置
3. 调用 `Update_Stock_Data` 或 `Update_Stock_Data_easy` 填充数据
4. 重启 QuantAll 服务使新数据库生效

### 方案 C：使用用户自有数据库

如果用户已有 DuckDB 股票数据库，直接修改 `DB_setting.json` 中的 `db_path` 指向该数据库，并调整各表的 `map_*` 字段映射以匹配实际列名即可。

---

## 工作流程

### 数据库创建与更新流程
1. 调用 `ping` 确认 MCP 服务已连接
2. 首次使用先调用 `Creat_DB` 创建独立数据库（不要用 Test.duckdb）
3. 调用 `Set_QuantAll_DataBase` 设置数据库路径
4. 根据 tushare 积分选择 `Update_Stock_Data`（2000+）或 `Update_Stock_Data_easy`（120-200）
   - **首次全量更新耗时极长，请在空闲时段运行，避免中途中断**
5. 检查返回信息确认操作结果

### 数据查询流程
1. 调用 `get_stock`（非复权）或 `get_adj_stock`（前复权）获取行情数据
2. 指定股票代码和时间范围
3. AI 可直接使用返回的 JSON 数据进行绘图、分析等操作

### QuantAll 启动流程
1. 确认 QuantAll 已安装（`pip install quantall`，推荐通过 `QuantAll-mcp` 技能安装）
2. 确认 `mcp.json` 中已配置全A解析 HTTP MCP
3. 调用 `Start_QuantAll` 启动服务
4. 重连全A解析 MCP（连接器页面或重启智能体）
5. 首次启动需确认用户协议弹窗
6. 调用 `mcp__全A解析__ping` 验证

---

## 注意事项

- 数据库路径和 API key 分别由 `DB_setting.json` 和 `API_tushare.txt` 管理，工具调用时无需手动传入
- `DB_setting.json` 首次运行自动创建，默认连接同目录 `Test.duckdb`
- tushare API token 放入 `API_tushare.txt`（纯文本，一行），避免每次输入
- 查询无结果时返回友好提示字符串，而非报错
- 返回的 trade_date 格式为 `YYYY-MM-DD` 字符串，方便 AI 直接解析
- **pandas 3.x 兼容性**：pandas 3.0+ 中 `str` 类型不再是 `object`，日期处理代码需在 `pd.to_datetime()` 前先 `.astype(object)` 转换
- Test.duckdb 仅供测试，正式使用务必创建独立数据库

## 版本历史

- **v2.2** — 阶段 7（财务指标）心跳优化：计数+时间双触发进度机制（每 10 只 / 30 秒），带 ETA 预估；修正 `disclosure_date` 按 `actual_date` 查询在非披露窗口返回 0 的说明（非 bug，正常行为）；修正频率限速逻辑
- **v2.1** — 移除已废弃的 `Install_QuantAll` / `Uninstall_QuantAll` 工具（QuantAll 现通过 `pip install quantall` 安装）；精简 QuantAll 相关描述（推荐安装 `QuantAll-mcp` 技能）；修正依赖列表（移除不在 requirements.txt 中的 PySide6/PyOpenGL）；修正 Test.duckdb 说明（运行时创建，非技能包自带）；修正字段映射说明（`DB_setting.json` 的 `map_*` 替代 `db_translate.json`）
- **v2.0** — 重写文档：以数据库管理为核心定位；更新工具签名匹配 async 新版本（`Update_Stock_Data` / `Update_Stock_Data_easy` 不再接收 `DB_path`/`API` 参数，改为自动读取配置文件）；新增进度通知说明；新增 MCP 重连和用户协议注意事项
- **v1.1** — 新增 `get_stock` 和 `get_adj_stock` 工具，支持查询股票行情数据（支持时间范围过滤）
- **v1.0** — 初始版本，支持数据库创建和全量/增量更新
