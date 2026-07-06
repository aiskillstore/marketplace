# wind-mcp-skill 工具契约

> 何时读：选定工具后只读对应段落 | 权威于：各工具字段 / 参数 / 示例 | 不覆盖：`indexes` 取值（见 `references/indicators.md`）

按 `SKILL.md` 完成路由判定后，只读取本文件中与所选工具相关的段落。
调用前仍需校验 `references/tool-manifest.json`；行情快照 `indexes` 仍以
`references/indicators.md` 为唯一权威清单。

## 目录

1. 工具总表
2. 参数签名
3. 行情工具
4. 领域 NL 工具
5. 文档工具
6. 宏观工具
7. 通用取数兜底
8. 调用示例

## 工具总表

**`tool_name` 必须逐字取自本表；不在表内的名字一律不存在（如 `get_fund_qa`），禁止自造或拼凑。**

| server_type | tool_name | 入参 |
| --- | --- | --- |
| `stock_data` | `search_stocks` | `question`（+`lang` / `version`） |
| `stock_data` | `get_stock_price_indicators` | `windcode` + `indexes` |
| `stock_data` | `get_stock_kline` | `windcode` + `begin_date` + `end_date`（+`period` / `count` / `aftime`…） |
| `stock_data` | `get_stock_quote` | `windcode`（+`begin` / `end`） |
| `stock_data` | `get_stock_basicinfo` / `get_stock_fundamentals` / `get_stock_equity_holders` / `get_stock_events` / `get_stock_technicals` / `get_risk_metrics` | `question`（+`lang`） |
| `fund_data` | `search_funds` | `question`（+`lang` / `version`） |
| `fund_data` | `get_fund_price_indicators` | `windcode` + `indexes` |
| `fund_data` | `get_fund_kline` | `windcode` + `begin_date` + `end_date` |
| `fund_data` | `get_fund_quote` | `windcode`（+`begin` / `end`） |
| `fund_data` | `get_fund_info` / `get_fund_financials` / `get_fund_holdings` / `get_fund_performance` / `get_fund_holders` / `get_fund_company_info` | `question`（+`lang`） |
| `index_data` | `get_index_price_indicators` | `windcode` + `indexes` |
| `index_data` | `get_index_kline` | `windcode` + `begin_date` + `end_date` |
| `index_data` | `get_index_quote` | `windcode`（+`begin` / `end`） |
| `index_data` | `get_index_basicinfo` / `get_index_fundamentals` / `get_index_technicals` | `question`（+`lang`） |
| `bond_data` | `get_bond_basicinfo` / `get_bond_issuer_info` / `get_bond_market_data` / `get_bond_financial_data` | `question`（+`lang`）；无行情快照工具 |
| `financial_docs` | `get_company_announcements` / `get_financial_news` | `query`（+`top_k`） |
| `economic_data` | `natural_language_get_edb_data` | `executionMode` + `question`（+`beginDate` / `endDate` 或 `observation`） |
| `analytics_data` | `get_financial_data` | `question`（+`lang`） |

字段级细节（`indexes` 取值、`period` 枚举、日期格式）见下方各工具段落与 `references/indicators.md`。

## 参数签名

| 工具组 | 入参 | 适用范围 |
| --- | --- | --- |
| 行情类 | `{windcode, ...}` | 股票 / 港美股 / 基金 / 指数行情工具 |
| 股票筛选 | `{question, lang?, version?}` | `stock_data.search_stocks` |
| 基金筛选 | `{question, lang?, version?}` | `fund_data.search_funds` |
| 专项 NL | `{question, lang?}` | `stock_data`、`fund_data`、`index_data`、`bond_data` NL 工具 |
| 文档 RAG | `{query, top_k?}` | `financial_docs` 工具 |
| 宏观 EDB | `{executionMode, question, ...}` | `economic_data.natural_language_get_edb_data` |
| 通用结构化取数 | `{question, lang?}` | `analytics_data.get_financial_data` |

params JSON 的 key 必须逐字复制本文件的字段名。不得把用户口语、其它 API 习惯或通用证券字段名
翻译成别名 key；例如行情类必须使用 `windcode`，不得写成 `code`、`ticker`、`symbol`、
`sec_code` 或 `stock_code`。

单次工具调用只查询一个标的。行情类 `windcode` 必须是单个字符串，禁止传数组、对象、
逗号分隔多代码、空格分隔多代码或把多个代码拼成一个字符串。用户要求多个指数 / 股票 /
基金对比时，必须拆成多次同工具调用后合并结果；不要把
`["000001.SH","399001.SZ"]`、`"000001.SH,399001.SZ"` 或类似形式传给 `windcode`。

`windcode` 优先传用户给出的单个标的名称、简称或代码。Wind 后端会做标的 NER，可解析中文名、简称、裸 6 位代码、裸美股 ticker 和标准代码；没有确定映射时，不得自行给名称、裸 6 位代码或裸 ticker 补交易所后缀，也不得把自然语言标的猜成代码。只有用户明确给出标准代码和市场时，才使用带后缀的 Wind 标准代码，例如：

- A股：`600519.SH`、`8XXXXX.BJ`
- 港股：`0700.HK`、`9988.HK`
- 美股：`AAPL.O`、`MSFT.O`
- 场外基金：`005827.OF`
- ETF / LOF：`588200.SH`、`159915.SZ`
- 指数：`000300.SH`、`000905.SH`、`HSI.HI`

简称或别名可能映射多个标的时先问用户，不要让后端静默选错。行情类 NER 失败后，保持同一工具，只把 `windcode` 改成更明确的单个名称或用户确认的标准代码；若原始 `windcode` 是 1-5 位纯大写英文字母，且用户问题明确是美股 / 美国上市公司语境，允许仅在 `MARKET_TARGET_NOT_FOUND` 后改为 `<ticker>.O` 重试一次；台股、日股、韩股、欧股等超出本 skill 覆盖范围的请求不得套用 `.O` 重试；除此之外禁止通过猜测 `.O`、`.N`、`.HK`、`.SH`、`.SZ` 等后缀来重试。

裸 6 位数字代码（如 `000001`）允许原样传给 Wind NER。不得在本地自动补 `.SH`、`.SZ`、`.BJ`、`.OF` 等后缀；返回结果必须以 Wind 返回的 `Wind代码` 为准。若用户要求精确市场/品类或对 Wind 返回标的有疑义，再请用户提供标的全称、市场/品类，或明确 Wind 标准代码。

带 `.HK` 的 5 位港股代码若以 0 开头，CLI 会做安全归一化：只去掉最前面的一个 0，例如 `00700.HK` -> `0700.HK`、`01211.HK` -> `1211.HK`、`03311.HK` -> `3311.HK`。裸数字不做这种处理，仍交给 Wind NER。

## 股票筛选

`stock_data.search_stocks`（股票筛选）从全市场中筛选符合条件的股票，返回股票代码列表。

触发条件：用户未指定具体股票，而是描述 选股条件，例如市值、涨跌幅、行业、上市板、
连续上涨 / 下跌、技术形态或其它筛选条件。

不要用于：已指定单只股票的行情 / 财务查询；港股、美股、基金、指数、债券筛选；需要返回字段值而非股票代码列表的取数。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `question` | 是 | 自然语言选股问句；调用前移除空白字符，不得添加用户未给出的筛选条件 |
| `lang` | | `"English"` / `"中文"`；默认 `"中文"` |
| `version` | | 后端版本参数；仅当用户或系统明确指定时传入，不得自造 |

示例：`{"question":"筛选沪深市场市值超500亿且连续5日上涨的股票"}`

## 港美股筛选

`stock_data.search_stocks`（港美股筛选）从港股 / 美股中筛选符合条件的股票，
返回港股 / 美股代码列表。

触发条件：用户未指定具体港股 / 美股，而是描述选股条件，例如市场、市值、涨跌幅、行业、
交易所、上市地或其它筛选条件。

不要用于：已指定单只港股 / 美股的行情 / 财务查询；A股、基金、指数、债券筛选；
需要返回字段值而非股票代码列表的取数。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `question` | 是 | 自然语言港美股筛选问句；调用前移除空白字符，不得添加用户未给出的筛选条件 |
| `lang` | | `"English"` / `"中文"`；默认 `"中文"` |
| `version` | | 后端版本参数；仅当用户或系统明确指定时传入，不得自造 |

示例：`{"question":"筛选港股中市值超1000亿港元的科技股"}`

## 基金筛选

`fund_data.search_funds`（基金筛选）从基金产品中筛选符合条件的基金，返回基金代码列表。

触发条件：用户未指定具体基金 / ETF / LOF，而是描述筛选条件，例如基金类型、ETF 主题、
收益率、管理规模、基金公司、投资主题、风险收益特征或其它筛选条件。

不要用于：已指定单只基金的净值 / 规模 / 档案 / 持仓 / 业绩查询；股票、指数、债券筛选；
需要返回字段值而非基金代码列表的取数。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `question` | 是 | 自然语言基金筛选问句；调用前移除空白字符，不得添加用户未给出的筛选条件 |
| `lang` | | `"English"` / `"中文"`；默认 `"中文"` |
| `version` | | 后端版本参数；仅当用户或系统明确指定时传入，不得自造 |

示例：`{"question":"筛选股票型基金中近一年收益率超20%的产品"}`

## 行情工具

### 行情快照指标

用于最新值或其它单时点行情字段。

| server_type | tool_name |
| --- | --- |
| `stock_data` | `get_stock_price_indicators` |
| `fund_data` | `get_fund_price_indicators` |
| `index_data` | `get_index_price_indicators` |

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `windcode` | 是 | 单个标的名称或代码；禁止数组、多代码字符串或逗号拼接 |
| `indexes` | 是 | 逗号分隔的精确指标名；每个值必须逐字存在于 `references/indicators.md` |

`indexes` 只能覆盖用户明确请求的指标，不得为了“更完整”追加用户未提到的字段。
`indexes` 禁止猜测、翻译、改写。不得传入未收录的英文缩写、拼音、API 字段名、
用户口语词或自行翻译词；若字段不在
`references/indicators.md`，改用合适的 NL 工具，或说明该快照字段不可用。
用户口语字段必须映射为表内精确字段后再传入，例如“今开”传 `今日开盘价`，
“昨收”传 `前收盘价`；找不到表内精确字段时不要传入快照工具。
CLI 会在调用前归一部分高频别名：`最新价` / `收盘价` / `close` -> `最新成交价`，
`昨收` -> `前收盘价`，`开盘价` / `open` -> `今日开盘价`，`市盈率TTM` / `pe_ttm` ->
`市盈率(TTM)`，`总市值` -> `总市值2`，`近一年收益率` -> `近一年净值增长率`。
若用户明确要求“流通口径总市值”，传 `总市值1`；若明确要求“含限售总市值”，传 `总市值2`。

以下仅是常用候选，用于定位用户已请求的字段；不得把候选列表当作默认字段集。
传参前仍要逐项核对 `references/indicators.md`：

- 通用：`中文简称`、`最新成交价`、`前收盘价`、`今日开盘价`、`今日最高价`、
  `今日最低价`、`成交量`、`成交额`、`涨跌`、`涨跌幅`
- 股票：`换手率`、`量比`、`委比`、`涨停价`、`跌停价`、`52周最高`、
  `52周最低`、`总市值1`、`流通市值`、`市盈率(TTM)`、`市净率`、`股息率`
- 基金：`IOPV`、`贴水率`、`基金最新份额`、`基金规模`、`最新净值`、
  `累计净值`、`七日年化收益率`
- 指数：`成分股贡献点数`、`上涨家数`、`下跌家数`、`平盘家数`

### K 线

用于历史行情序列。

| server_type | tool_name |
| --- | --- |
| `stock_data` | `get_stock_kline` |
| `fund_data` | `get_fund_kline` |
| `index_data` | `get_index_kline` |

| 字段 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `windcode` | 是 | | 单个标的名称或代码；禁止数组、多代码字符串或逗号拼接 |
| `begin_date` | 是 | | `yyyyMMdd` |
| `end_date` | 是 | | `yyyyMMdd` |
| `count` | | | 正数表示从 `begin_date` 向后取 N 条；负数表示从 `end_date` 向前取 N 条 |
| `period` | | `"10"` | `1`=1分, `3`=5分, `4`=10分, `5`=15分, `6`=30分, `7`=60分, `8`=120分, `9`=240分, `10`=日K, `11`=周K, `12`=月K, `13`=年K, `14`=季K, `15`=半年K |
| `aftime` | | `"0"` | `"0"`=前复权, `"1"`=后复权 |
| `issusp` | | `"1"` | `"0"`=不含停牌, `"1"`=含 |
| `afdate` | | | 可选复权基准日，`yyyyMMdd` |

CLI 会把 `day` / `D` / `daily` / `日线` 归一为 `period:"10"`，把 `week` / `周线`
归一为 `11`，把 `month` / `月线` 归一为 `12`。其它 `period` 值会在本地校验阶段拦截，
避免后端因 `"day"` / `"D"` 等字符串返回 500。

行情工具只做安全归一化：去除首尾空白、规范已带后缀代码大小写、映射少量明确指数别名
（如 `HSI` / `HSI.HK` -> `HSI.HI`）。不会也不应把裸美股 ticker 自动补为 `.O`，不会凭空补
`.N`、`.HK`、`.SH`、`.SZ` 等交易所后缀；不确定时传用户原始单标的名称，让 Wind NER 识别。仅当裸 ticker 首次 NER 返回 `MARKET_TARGET_NOT_FOUND`，且用户问题明确是美股 / 美国上市公司语境时，才允许按上文规则补 `.O` 重试一次。

### 分钟行情

用于日内走势或分钟级行情数据。

| server_type | tool_name |
| --- | --- |
| `stock_data` | `get_stock_quote` |
| `fund_data` | `get_fund_quote` |
| `index_data` | `get_index_quote` |

| 字段 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `windcode` | 是 | | 单个标的名称或代码；禁止数组、多代码字符串或逗号拼接 |
| `begin` | | `LAST` | `yyyyMMdd` 或 `LAST` |
| `end` | | `LAST` | `yyyyMMdd` 或 `LAST` |

## 领域 NL 工具

公共参数：

- `question: string` 写成标的加业务问题。
- `lang?: "English" | "中文"` 默认 `"中文"`。
- 调用前移除自然语言字段值中的空白字符。

### A股 / 港股 / 美股：`stock_data`

| 工具 | 适用场景 | `question` 示例 |
| --- | --- | --- |
| `search_stocks` | 全市场 股票筛选，返回代码列表 | `"筛选沪深市场市值超500亿且连续5日上涨的股票"` |
| `get_stock_basicinfo` | 公司档案、主营、行业、IPO、上市板 | `"600519.SH公司基本档案"` |
| `get_stock_fundamentals` | 盈利、资产负债、利润、现金流、增长率、银行业专项 | `"贵州茅台2024年ROE和净利润增速"` |
| `get_stock_equity_holders` | 股本、流通、前十大股东、实控人、限售 | `"贵州茅台前十大股东"` |
| `get_stock_events` | IPO、增发、配股、并购、ST、分红 | `"宁德时代2024年增发和并购事件"` |
| `get_stock_technicals` | MACD、KDJ、RSI、BOLL、融资融券、龙虎榜 | `"贵州茅台近60日MACD走势"` |
| `get_risk_metrics` | Beta、Jensen Alpha、波动率、Sharpe、VaR | `"贵州茅台过去1年Beta和波动率"` |

### 基金 / ETF / LOF：`fund_data`

| 工具 | 适用场景 | `question` 示例 |
| --- | --- | --- |
| `search_funds` | 全市场基金产品筛选，返回代码列表 | `"筛选股票型基金中近一年收益率超20%的产品"` |
| `get_fund_info` | 基金档案、费率、经理、风格、业绩基准 | `"易方达蓝筹精选(005827.OF)基金档案"` |
| `get_fund_financials` | 利润、净值、收入、费用、分红 | `"005827.OF2024年净利润和分红"` |
| `get_fund_holdings` | 重仓股、资产配置、行业配置 | `"005827.OF最新一期重仓股"` |
| `get_fund_performance` | 业绩、排名、ETF / 二级交易 | `"005827.OF近1年业绩排名"` |
| `get_fund_holders` | 持有人结构、申赎、规模变动 | `"005827.OF持有人结构"` |
| `get_fund_company_info` | 基金管理公司档案、经理团队 | `"易方达基金管理公司档案"` |

### 指数 / 板块：`index_data`

| 工具 | 适用场景 | `question` 示例 |
| --- | --- | --- |
| `get_index_basicinfo` | 指数档案、发布机构、基日、基点、成份数量 | `"沪深300指数档案"` |
| `get_index_fundamentals` | PE / PB / PS、营收、利润、现金流、历史分位 | `"沪深300PE/PB历史分位"` |
| `get_index_technicals` | 多周期涨跌幅、趋向、反趋向、能量、量价、波动 | `"中证500的MACD和RSI"` |

### 债券：`bond_data`

`bond_data` 没有行情快照工具。债券行情和估值请求走 NL 工具。

| 工具 | 适用场景 | `question` 示例 |
| --- | --- | --- |
| `get_bond_basicinfo` | 债券档案、发行、规模、价格、票面利率、期限、兑付 | `"国债2601基本信息"` |
| `get_bond_issuer_info` | 发债主体名称、注册地、行业、股权结构、企业背景 | `"国债2601发债主体"` |
| `get_bond_market_data` | 报价、估价、溢价、久期、凸性、利差 | `"国债2601久期和凸性"` |
| `get_bond_financial_data` | 发债主体营收、利润、资产、负债 | `"国债2601主体2024年营收"` |

## 文档工具

用户询问文档内容或新闻时，优先使用 `financial_docs`。

| 工具 | 适用场景 |
| --- | --- |
| `get_company_announcements` | 官方公告、监管披露、年报、半年报、季报、招股书 |
| `get_financial_news` | 第三方财经新闻、市场报道、政策和政经动态 |

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `query` | 是 | 调用时不含空白字符的自然语言查询 |
| `top_k` | | 返回文档数量 |

## 宏观工具

宏观和行业 EDB 指标使用 `economic_data.natural_language_get_edb_data`。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `executionMode` | 是 | 执行模式：`search`/`fetch`/`searchFetch`；也可用中文枚举 `仅搜索`/`仅提数`/`搜索并提数` |
| `question` | 是 | `search` / `searchFetch` 时填自然语言指标描述，如 `中国GDP`；`fetch` 时填一个或多个 EDB 指标代码，多个代码用英文逗号分隔 |
| `beginDate` / `endDate` | | 数据提取时间范围，`yyyyMMdd`；与 `observation` 互斥 |
| `observation` | | 近 N 期数据填数字字符串，如 `10`；全量数据填 `all`；与 `beginDate` / `endDate` 互斥 |

调用约束：`fetch` 或 `searchFetch` 需要返回具体数值数据时，必须显式提供 `beginDate` / `endDate` 或 `observation`。不要只把时间范围写入 `question`。

## 通用取数兜底

只有专项路由无法覆盖的结构化取数任务，才使用 `analytics_data.get_financial_data`。

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `question` | 是 | 简洁的自然语言取数问题 |
| `lang` | | `CNS`=中文默认，`ENS`=英文 |

规则：

1. 首次调用必须将用户原始问题去除所有空格后传入，不得改写、概括、翻译或增加用户未给出的筛选条件。
2. 只有首次调用失败、返回空数据或明显不匹配请求后，才可改写或拆分 `question`。
3. 一个 analytics 问题只聚焦一个取数动作；复杂分析先拆成简单取数步骤，再综合结果。
4. 若任务需要先发现范围，再对范围内成员二次取数，必须显式分步执行。无法得到可靠范围或后端没有可用排名口径时，停止并说明限制。

## 调用示例

以下示例都要求先 `cd` 到 skill 目录，即本 `SKILL.md` 所在目录、不是当前项目目录，再用相对路径执行 `node scripts/cli.mjs ...`。不 `cd` 会找不到脚本。

```bash
node scripts/cli.mjs call stock_data search_stocks '{"question":"筛选沪深市场市值超500亿且连续5日上涨的股票"}'
node scripts/cli.mjs call stock_data search_stocks '{"question":"筛选港股中市值超1000亿港元的科技股"}'
node scripts/cli.mjs call fund_data search_funds '{"question":"筛选股票型基金中近一年收益率超20%的产品"}'
node scripts/cli.mjs call stock_data get_stock_price_indicators '{"windcode":"600519.SH","indexes":"中文简称,最新成交价,涨跌幅,成交量"}'   # indexes 逐字抄 indicators.md
node scripts/cli.mjs call stock_data get_stock_kline '{"windcode":"600519.SH","begin_date":"20260401","end_date":"20260430"}'   # 日期 yyyyMMdd，不带 -
node scripts/cli.mjs call stock_data get_stock_kline '{"windcode":"0700.HK","begin_date":"20260401","end_date":"20260430"}'
node scripts/cli.mjs call fund_data get_fund_price_indicators '{"windcode":"588200.SH","indexes":"中文简称,最新成交价,IOPV,贴水率"}'
node scripts/cli.mjs call financial_docs get_financial_news '{"query":"美联储利率政策","top_k":5}'   # query 无空格
node scripts/cli.mjs call economic_data natural_language_get_edb_data '{"executionMode":"searchFetch","question":"中国CPI同比","beginDate":"20240101","endDate":"20261231"}'   # 宏观提数显式传时间范围
```
