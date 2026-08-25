---
name: find-skills-catalog
description: 平台 skill 清单本地副本。由 npx skills update -g -y 随 wind-find-finance-skill 一起更新。
---

# Skill 目录

> 平台所有可装 skill 的清单。
> 由 `npx skills update -g -y` 随 wind-find-finance-skill 一起更新。

---

## 数据类(取数 / 查询)

> 取数 / 查询:行情、基金、股票财务、公告、新闻、宏观指标。

| 名称                  | category                              | 装好需配置     | 一句话                                                                                                                                  |
| --------------------- | ------------------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| wind-mcp-skill        | 数据-行情/基金/股票/宏观/文档         | API Key        | 访问万得 Wind 金融数据:A 股 / 港股股票(行情与财务) + ETF / 公募基金(行情与全维数据) + 公司公告 + 财经新闻 + 宏观经济指标                |
| wind-alice            | Alice 专业金融分析 Agent              | API Key        | Alice 综合分析入口,适合事实核验、公司一页纸、调研问题清单、财报点评、主题选股、基金分析、宏观/债券/信用分析、市场规模测算和可比公司分析 |
| tushare-finance-skill | 数据-行情/财务/宏观/多资产            | 依赖 + Token   | 访问 Tushare Pro 金融数据:覆盖 A 股、港股、美股、基金、期货、债券、财务报表与宏观经济指标                                               |

---

## Alice 子 Skill 索引

> 这些能力由 `wind-alice` 统一承载。用户点名中文名、英文名或提出高度匹配的问题时,推荐安装 / 调用 `wind-alice`,并把对应子 Skill 名传给 Alice。

| 中文名                 | 英文 Skill 名                            | 适合问题                                           |
| ---------------------- | ---------------------------------------- | -------------------------------------------------- |
| 通胀情景债券轮动策略   | `Inflation Bond Strategy`                | CPI/PPI 拐点驱动的债券、货基、久期轮动策略与回测   |
| 宏观数据解读           | `Macro Data Interpretation`              | CPI、PPI、PMI、GDP、社融等宏观指标的研究周报式解读 |
| 按主题选股             | `Thematic Stock Screening`               | 拆解市场主线、验证主题逻辑、筛选真实受益标的       |
| 债券利率走势研判       | `Bond Rate Outlook`                      | 从交易、策略、配置视角研判债券利率走势             |
| 信用分析               | `Credit Analysis`                        | 主体信用、财务现金流、评级对标、违约概率分析       |
| 基金对比分析           | `Fund Compare`                           | 多只基金业绩、风险、持仓、管理能力对比             |
| 基金筛选与投资建议     | `Fund Screening & Investment Advisory`   | 多维筛选基金并给出投顾式配置建议                   |
| 投资标的创意与筛选     | `Investment Idea Generation`             | 基于因子和主题扫描生成投资标的创意                 |
| 公司一页纸             | `Company One-Page Investment Memo`       | 上市公司一页纸投资报告                             |
| 上市公司调研问题清单   | `Stock DD List`                          | 买方视角调研备忘录、深度议题和管理层提问           |
| 全球上市公司季报点评   | `Global Share Quarterly Earnings Review` | 全球上市公司财报点评、beat/miss 与核心变化         |
| 市场规模测算与战略建模 | `Market Sizing & Strategic Modeling`     | Top-down / Bottom-up 市场规模测算与情景敏感性      |
| 可比公司分析           | `fsi-comps-analysis`                     | 机构级可比公司分析,含 Excel 和文字报告             |
| 事实核验               | `Fact Check`                             | 逐点核查金融数据、声明、事件和文本事实             |

---

## Avatar 思维框架索引

> 用户点名人物、要求使用对应思维框架，或问题与下表场景高度匹配时，推荐对应 Avatar skill。明确点名时将其视为必需工作流 skill；未点名的一般分析任务可将其作为可选补充 skill。

| 名称                              | category          | 装好需配置 | 适合问题                                                                 |
| --------------------------------- | ----------------- | ---------- | ------------------------------------------------------------------------ |
| avatar-charlie-munger-thinking    | 决策/认知偏误     | 无         | 查理·芒格 / 查理芒格 / Charlie Munger：逆向思考、激励分析、多学科模型、认知偏误叠加与决策失败风险 |
| avatar-nassim-taleb-risk          | 风险/不确定性     | 无         | 纳西姆·塔勒布 / 纳西姆塔勒布 / Nassim Taleb：尾部风险、出局风险、利益共担、杠铃策略与脆弱性     |
| avatar-naval-ravikant-thinking    | 职业/创业/人生决策 | 无         | 纳瓦尔·拉维坎特 / 纳瓦尔 / Naval Ravikant：职业、创业、财富、自由、特定知识、杠杆与长期复利     |
| avatar-warren-buffett-investing   | 长期投资/个股研究 | 无         | 沃伦·巴菲特 / 巴菲特 / Warren Buffett：能力圈、护城河、管理层诚信、所有者收益、估值与安全边际   |

---

## 工作流类(决策 / 分析)

> 决策 / 工作流:估值、复盘、选股、回测、个股研究、市场主线。

| 名称                                 | category                 | 装好需配置 | 一句话                                                                                                                                  |
| ------------------------------------ | ------------------------ | ---------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| dcf-model                            | 估值                     | 无         | DCF 估值建模(WACC + 敏感性分析)                                                                                                         |
| earnings-analysis                    | 估值-季报                | 无         | 季报点评(beat/miss + 估值更新)                                                                                                          |
| valuation-pricing-framework          | 估值                     | 无         | 估值与定价框架(重估空间判断)                                                                                                            |
| equity-investment-thesis             | 个股研究                 | 无         | 个股投资逻辑深度研究(券商研究员风格)                                                                                                    |
| a-share-primary-theme-identification | 市场主线                 | 无         | A 股市场主线识别(题材周期 / 资金行为)                                                                                                   |
| market-environment-analysis          | 市场主线                 | 无         | 全球市场环境分析(risk-on / risk-off)                                                                                                    |
| theme-detector                       | 市场主线                 | 无         | 跨板块主题检测(FINVIZ + 生命周期)                                                                                                       |
| post-market-debrief                  | 复盘                     | 无         | 盘后复盘(市场全景 / 主线轮动)                                                                                                           |
| position-sizer                       | 仓位                     | 无         | 仓位管理(风险 / Kelly / ATR)                                                                                                            |
| backtest-expert                      | 回测                     | 无         | 量化策略系统化回测(压力测试)                                                                                                            |
| valuation_snapshot_skill             | 估值                     | 无         | 快速判断个股估值高低、所处分位与重估触发条件                                                                                            |
| bull_bear_case_builder_skill         | 个股研究                 | 无         | 同步搭建看多与看空逻辑，压缩确认偏误并找出核心分歧                                                                                      |
| peer_comparison_decision_skill       | 个股研究                 | 无         | 横向比较候选公司质量、成长、估值与催化，辅助二选一                                                                                      |
| moat_strength_review_skill           | 个股研究                 | 无         | 评估公司竞争优势是否真实、可持续且能转化为回报                                                                                          |
| business_model_decoder_skill         | 个股研究                 | 无         | 把公司如何获客、赚钱、扩张和受限讲清楚                                                                                                  |
| major_announcement_impact_skill      | 事件/公告/财报文档       | 无         | 分析并购、减持、定增等重大公告的核心影响，服务突发事件判断                                                                              |
| conference_call_takeaway_skill       | 事件/公告/财报文档       | 无         | 提炼业绩会关键信息、管理层表态和警讯，服务会后快速吸收要点                                                                              |
| guidance_change_impact_skill         | 事件/公告/财报文档       | 无         | 解释业绩指引上修下修的含义、可信度与后续影响                                                                                            |
| sec_filing_question_answer_skill     | 事件/公告/财报文档       | 无         | 从 10-K、10-Q、招股书等长文档中精准答疑，服务监管文件快读                                                                               |
| sector_rotation_radar_skill          | 市场主线                 | 无         | 识别板块强弱切换、资金迁移与风格变化，服务市场主线判断                                                                                  |
| market_regime_switch_skill           | 市场主线                 | 无         | 判断市场处于进攻、防守、震荡或切换阶段，服务总仓位与风格判断                                                                            |
| institutional_position_shift_skill   | 市场主线                 | 无         | 识别机构持仓变化与共识迁移，服务季报持仓研究                                                                                            |
| theme_leader_identification_skill    | 市场主线/选股            | 无         | 识别热门题材中的龙头、中军和跟随股，判断谁最值得跟踪                                                                                    |
| breakout_candidate_finder_skill      | 选股                     | 无         | 筛选形态成熟、放量待发的突破候选股，并给出触发条件                                                                                      |
| pullback_opportunity_finder_skill    | 选股                     | 无         | 寻找回调充分但趋势未破坏的候选股，定位低吸观察区                                                                                        |
| high_quality_compounder_finder_skill | 选股                     | 无         | 筛选高 ROE、高护城河、可长期复利的核心候选股                                                                                            |
| trade_plan_builder_skill             | 交易执行                 | 无         | 下单前生成包含入场、仓位、止损止盈的完整计划                                                                                            |
| position_sizing_decision_skill       | 交易执行/仓位            | 无         | 按风险预算和波动水平给出单笔仓位与分批建议                                                                                              |
| stop_loss_discipline_skill           | 交易执行                 | 无         | 设计价格、逻辑、时间三类止损规则与执行动作                                                                                              |
| take_profit_ladder_skill             | 交易执行                 | 无         | 为盈利仓设计分层兑现、保本上移与尾仓持有规则                                                                                            |
| add_to_winner_decision_skill         | 交易执行/仓位                  | 无          | 判断盈利仓是否适合继续加仓，并给出加仓前提、节奏安排、保护规则与停止扩张边界 |
| after_close_watchlist_recap_skill    | 复盘/自选股                   | 无          | 收盘后总结自选股当日表现、驱动因素、强弱分化与次日观察点 |
| breakout_trade_execution_skill       | 交易执行                     | 无          | 围绕突破交易制定从观察、触发、跟进到失效处理的落地执行方案 |
| buyback_program_reviewer_skill       | 事件/公告/财报文档               | 无          | 判断回购计划的规模、动机、执行约束与真实利好程度 |
| canslim_growth_scan_skill            | 选股                       | 无          | 依据 CANSLIM 成长股框架批量筛选业绩、预期、相对强度与供需结构共振的强势标的 |
| daily_watchlist_morning_brief_skill  | 复盘/自选股                   | 无          | 为自选股生成盘前简报，汇总隔夜公告、新闻、价格变化、事件日程与今日观察重点 |
| dip_buy_decision_skill               | 交易执行                     | 无          | 判断下跌或回调中的个股是否值得承接，并给出观察区、试错条件、分批节奏与放弃标准 |
| dividend_change_explainer_skill      | 事件/公告/财报文档               | 无          | 解读分红提升、削减、暂停或恢复背后的原因、持续性与投资含义 |
| dividend_growth_entry_skill          | 选股                       | 无          | 寻找股息持续增长、经营质量稳定且估值回落到合理区间的候选股 |
| earnings_calendar_planner_skill      | 事件/公告/财报文档               | 无          | 按时间轴组织财报季中的重点公司、前后任务、优先级与提醒 |
| earnings_momentum_setup_skill        | 选股                       | 无          | 寻找财报发布后业绩与指引共同强化、量价表现积极、具备继续上行动能的机会股 |
| earnings_preview_skill               | 事件/公告/财报文档               | 无          | 财报前梳理市场预期、关键看点、验证指标、情景推演与风险点 |
| earnings_reaction_interpreter_skill  | 事件/公告/财报文档               | 无          | 解读财报发布后的涨跌反应、超预期来源、市场真实分歧与后续观察点 |
| failed_breakout_exit_skill           | 交易执行                     | 无          | 识别突破失败、冲高回落与关键位失守后的撤退信号，并给出减仓、止损与重新观察顺序 |
| gap_open_interpreter_skill           | 盘中异动/交易判断                | 无          | 解读高开、低开、跳空缺口背后的预期差、事件含义与日内风险点 |
| growth_quality_check_skill           | 个股研究                     | 无          | 拆解公司增长来源，检查盈利含量、现金含量、可持续性与失速风险 |
| hot_stock_quick_read_skill           | 个股研究                     | 无          | 在极短时间内解释热门股的业务、催化、市场预期、资金关注点与主要风险 |
| industry_chain_signal_skill          | 市场主线                     | 无          | 从产业链上下游景气、价格、订单、库存与盈利变化中识别机会与风险 |
| intraday_abnormal_move_alert_skill   | 盘中异动/交易判断                | 无          | 识别盘中急拉、急跌、放量、换手突变等异常波动，并解释可能驱动与持续性 |
| macro_event_market_impact_skill      | 市场主线                     | 无          | 解读利率、通胀、就业、增长等宏观事件对股市、风格和行业的影响路径 |
| management_quality_check_skill       | 个股研究                     | 无          | 检查管理层背景、激励机制、资本配置、治理质量与潜在红旗信号 |
| market_breadth_health_skill          | 市场主线                     | 无          | 判断指数涨跌背后是否有足够市场广度支撑，识别健康扩散、局部抱团或虚弱反弹 |
| market_sentiment_temperature_skill   | 市场主线                     | 无          | 量化市场情绪冷热、风险偏好与交易拥挤度，辅助仓位和节奏判断 |
| northbound_capital_flow_skill        | 市场主线                     | 无          | 追踪北向资金或外资偏好的变化、行业流向与风格迁移 |
| pead_opportunity_skill               | 选股                       | 无          | 识别财报后漂移行情中值得跟踪的中短线机会，判断预期修正、价格延续与失效边界 |
| policy_headline_interpreter_skill    | 市场主线                     | 无          | 解读政策新闻对行业、题材和个股的影响路径、受益方向与执行不确定性 |
| premarket_trade_checklist_skill      | 交易执行                     | 无          | 开盘前核查候选交易的催化剂、流动性、计划完整性、环境适配与风险暴露 |
| price_target_reach_alert_skill       | 交易执行                     | 无          | 当股价接近、触达或穿越目标价时，生成分批处理、继续持有或重新评估建议 |
| shareholder_letter_digest_skill      | 事件/公告/财报文档               | 无          | 总结股东信中的长期战略、经营变化、资本配置与管理层信号 |
| stock_first_look_skill               | 个股研究                     | 无          | 首次接触个股时，快速建立业务、市场关注点、关键指标、估值位置与主要风险认知 |
| stock_research_memo_writer_skill     | 个股研究                     | 无          | 生成结构化、可分享的个股研究备忘录，沉淀投资逻辑、核心分歧、估值判断与风险 |
| support_break_warning_skill          | 交易执行                     | 无          | 围绕支撑位、压力位、前高前低、趋势线等关键价格位置生成预警与应对提示 |
| theme_heat_tracker_skill             | 市场主线                     | 无          | 跟踪主题题材热度变化、扩散层级、拥挤程度与持续性 |
| trading_halt_resume_tracker_skill    | 事件/公告/财报文档               | 无          | 跟踪停牌、临停、复牌事件的原因、进展、潜在影响与复牌后观察框架 |
| trim_or_hold_decision_skill          | 交易执行                     | 无          | 在持仓明显盈利或短期大涨后，判断应部分兑现还是继续持有 |
| turnaround_story_validation_skill    | 个股研究                     | 无          | 验证困境公司是否真的出现反转证据，拆解修复路径、时间窗口、失败边界与赔率条件 |
| value_dividend_candidate_skill       | 选股                       | 无          | 筛选估值具备安全边际、股息有吸引力且分红可持续的收益型股票 |
| vcp_breakout_scan_skill              | 选股                       | 无          | 筛选波动逐级收缩、抛压减弱、结构趋于成熟的突破预备股 |
| volume_spike_reasoning_skill         | 盘中异动/交易判断                | 无          | 对股票盘中或日内放量异动进行归因，判断消息驱动、资金行为、情绪扩散或技术性放量 |
| watchlist_news_impact_digest_skill   | 复盘/自选股                   | 无          | 汇总自选股在指定时间窗口内的重要新闻、公告与舆情变化，并判断影响方向 |
| wind-alice                           | Alice 专业金融分析 Agent | API Key    | Alice 综合分析入口,适合事实核验、公司一页纸、调研问题清单、财报点评、主题选股、基金分析、宏观/债券/信用分析、市场规模测算和可比公司分析 |

---

## category 索引(用户问“探索”时使用)

| category                      | 含 skill 数 | 代表 skill                           |
| ----------------------------- | ----------- | ------------------------------------ |
| 数据-行情/基金/股票/宏观/文档 | 4           | wind-mcp-skill                       |
| Alice 专业金融分析 Agent      | 1           | wind-alice                           |
| 估值                          | 4           | dcf-model                            |
| 个股研究                      | 11          | stock_first_look_skill               |
| 事件/公告/财报文档            | 11          | earnings_preview_skill               |
| 市场主线                      | 14          | market_breadth_health_skill          |
| 选股                          | 10          | canslim_growth_scan_skill            |
| 复盘/自选股                   | 4           | after_close_watchlist_recap_skill    |
| 仓位                          | 3           | position_sizing_decision_skill       |
| 交易执行                      | 12          | premarket_trade_checklist_skill      |
| 盘中异动/交易判断             | 3           | intraday_abnormal_move_alert_skill   |
| 回测                          | 1           | backtest-expert                      |
| Avatar 思维框架               | 4           | avatar-charlie-munger-thinking       |


---

## 安装公式

把命令里的 `<name>` 换成上表"名称"列的值:

```bash
# 全局安装(推荐 — 跨项目 + 跨 AI agent 共享)
# 国外(GitHub)
npx skills add Wind-Information-Co-Ltd/wind-skills --skill <name> -g -y
# 国内(Gitee 镜像)
npx skills add https://gitee.com/wind_info/wind-skills.git --skill <name> -g -y
```

> 想限制在当前项目内用,把上面命令的 `-g` 去掉即可。

参数说明:

- `-g`:全局安装 — 跨项目 + 自动 symlink 到机器上所有已识别 AI agent(Claude Code / Cursor / OpenClaw / Hermes 等)。金融机构内网推荐。
- 去掉 `-g`:仅当前项目 — 装到当前目录,不影响其它项目 / agent。
- `-y`:**必加**,跳过交互菜单(不加会卡)

---

## 升级所有已装 skill

```bash
npx skills update -g -y
```

含义:`update` 重拉所有已装 skill 最新版,`-g` 只升级全局,`-y` 跳过 scope 提示。
