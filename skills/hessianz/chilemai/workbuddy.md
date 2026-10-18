# WorkBuddy 开发上下文

> 本文件记录「吃了麦？」在腾讯 WorkBuddy 中开发过程的对话上下文与关键决策，
> 用于核验本项目真实使用 WorkBuddy 开发（联动活动奖励条件）。

## 一、开发任务

用 WorkBuddy 开发一个 Skill，参加「麦当劳程序员创意开发大赛」。
Skill 目标是解决"吃什么"的选择困难：接收自然语言诉求（营养 / 减脂 / 便宜），
基于麦当劳 MCP 的真实数据推荐餐品、选择最近门店并创建订单。

## 二、开发环境

- 客户端：腾讯 WorkBuddy（macOS）
- 使用的连接器：`mcd-mcp`（麦当劳 MCP Server，streamable HTTP）
- 依赖：Python 标准库（脚本零第三方依赖）

## 三、关键决策与迭代过程

### 决策 1：先跑通真实调用链，再写文档

没有直接开写 SKILL.md，而是先用 WorkBuddy 实际调用了
`now-time-info` → `query-nearby-stores` → `query-meals` → `list-nutrition-foods`，
确认真实返回结构后再落笔。这个顺序避免了一件事：**按想象中的 API 写文档**。

实际返回值暴露了两个凭想象发现不了的问题（见决策 3、4）。

### 决策 2：确认 MCP 端点可独立调用

为验证数据的可复现性，用 WorkBuddy 的终端直接以 streamable HTTP 协议
（`initialize` + `tools/call`）访问 `https://mcp.mcd.cn`，
确认 `serverInfo.name = "mcd-mcp"`、协议版本 `2025-03-26`，
并把真实响应存成本地样本用于测试。

### 决策 3：营养数据不是 JSON

`list-nutrition-foods` 返回的 `data` 是这种自定义文本：

```
[160]{productName,nutritionDescription,energyKj,energyKcal,protein,fat,carbohydrate,sodium,calcium}:
  猪柳麦满分,null,1288,308,16,16,24,781,213
```

于是写了 `scripts/chilemai.py` 做解析，并用 160 条真实数据验证：全部解析成功，
且发现官方营养表存在**同名重复行**（如「小杯玉米杯」出现两次），加了去重。

### 决策 4：低卡筛选会返回饮料，这是错的

第一版脚本按热量升序排，`--goal low-cal` 的前四名是
「无糖可口可乐中杯 / 大杯 / 小杯 / 纯悦」——全是 0 kcal 的饮料。

**按"要低卡"推荐一杯可乐是错的。** 于是给脚本加了餐品分类
（`main` / `side` / `drink` / `dessert`，基于名称关键词），
低卡类目标默认只在主食与配餐里挑。分类结果用真实数据抽样核对过：

| 名称 | 分类 | 说明 |
| --- | --- | --- |
| 热朱古力 | drink | 是饮品 |
| 朱古力新地 | dessert | 是甜品，靠"新地"优先命中区分 |
| 德式图林根香肠 | side | 配餐 |
| 图林根香肠早安营养卷 | main | 含"卷"，是主食 |
| 柠檬拉明顿 | dessert | 靠"拉明顿"区分，不被"柠檬"误判成饮品 |

### 决策 5：套餐不能用单品的营养数值（最重要的一个修正）

`match` 子命令第一版做模糊匹配时，把「巨无霸三件套」匹配到了单品「巨无霸」（513 kcal）。
但三件套还含薯条与饮料，真实热量显著更高。

把这个数字报给正在控热量的人，是**自信地答错**。于是把匹配结果拆成三类：
`精确对齐` / `仅单品口径` / `未对齐`，并对带组合含义的项显式标注
`⚠️ 套餐：需叠加配餐+饮品`。

用真实菜单（84 项）验证后的分布：精确对齐 20 项、仅单品口径 22 项、未对齐 42 项。

### 决策 6：优惠券的可用性必须单独校验

`query-my-coupons` 返回的是用户**拥有**的券，但不做门店与下单规则校验。
要判断"这张券能不能用在当前订单"，必须走 `query-store-coupons`。
这条被写进了 `references/mcp-tools.md`，避免 Skill 做出无法兑现的承诺。

## 四、验证方式

| 环节 | 验证方法 | 结果 |
| --- | --- | --- |
| MCP 连通性 | 实际调用 `now-time-info` | 返回服务器时间，token 有效 |
| 门店查询 | 实际调用 `query-nearby-stores`（杭州·西湖） | 返回 5 家门店，最近 2545 m |
| 菜单查询 | 实际调用 `query-meals`（storeCode=3330257） | 返回 84 项在售餐品 |
| 营养解析 | 160 条真实数据跑 `parse_nutrition` | 全部解析成功，去重后 158 条 |
| 餐品分类 | 抽样核对 11 个易错名称 | 全部正确 |
| 目标筛选 | `--goal light` / `high-protein` / `low-cal` | 结果符合预期 |
| 名称对齐 | 84 项菜单 × 158 条营养 | 20 精确 / 22 单品口径 / 42 未对齐 |

## 五、产出

- `SKILL.md` —— Skill 主文件，五阶段流程
- `references/goals.md` —— 营养目标口径与真实数据锚点
- `references/mcp-tools.md` —— MCP 工具速查与参数矩阵
- `references/order-flow.md` —— 四种场景完整调用序
- `scripts/chilemai.py` —— 营养解析 / 筛选 / 菜单对齐
- `README.md`、`MCP_INTEGRATION.md`、`mcp-config.example.json`

## 六、备注

本项目全程在 WorkBuddy 中完成需求分析、MCP 调试、代码编写与验证。
真实 MCP Token 未写入仓库任何文件，示例配置仅含环境变量占位符。
