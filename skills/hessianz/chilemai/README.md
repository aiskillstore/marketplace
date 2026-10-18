# 吃了麦？(chilemai)

**一个帮你决定"吃什么"的 WorkBuddy Skill。**

「今天吃什么」是每天都要犯一次的难。吃了麦把这件事变成一句话：告诉它你想吃什么、有什么要求，它从麦当劳的真实菜单里配好一餐、选好离你最近的门店、把订单建好。

要营养？要减肥？要便宜？通通交给吃了麦。

---

## 它到底解决什么问题

用户的原话往往是这样的：

> "中午吃啥啊……"
> "想吃麦当劳，但我在减脂"
> "随便来点，40 块以内"
> "帮我点份早餐，送到家"

这些句子里藏着三个待办：**定目标 → 选餐品 → 下单**。吃了麦把三步都做了，而且用的是真实数据：

- **真实菜单** —— 通过麦当劳 MCP 拉取当前门店的**在售**餐品与实时价格，不是静态菜单表
- **真实营养** —— 160 条官方营养数据（热量/蛋白/脂肪/碳水/钠/钙），按你的目标筛选
- **真实门店** —— 按距离和营业状态选最近的门店
- **真实优惠** —— 自动领券、校验本店可用券、对比用券前后的价格
- **真实下单** —— 直接创建订单并给出支付入口

## 目标用户

- **选择困难的人** —— 不想在菜单前站五分钟，想有人直接给答案
- **控热量 / 增肌的人** —— 需要知道这一顿到底多少卡、多少蛋白，且不接受"猜"
- **预算敏感的人** —— 想吃好又想省钱，愿意为了便宜几块钱用张券
- **通勤 / 上班族** —— 早上赶时间、中午只有半小时，需要"最快拿到饭"的方案
- **点团餐的行政 / HR** —— 要给一群人按人均预算配餐

## 四种取餐场景

| 场景 | 适合 | 需要准备 |
| --- | --- | --- |
| **到店自取** | 门店就在楼下，拿了就走 | 城市 + 位置关键词 |
| **麦乐送外送** | 在家 / 在公司不想动 | 一个配送地址 |
| **得来速车道** | 开车路过，不熄火 | 城市 + 位置关键词 |
| **企业团餐** | 给团队按预算配餐 | 配送地址 + 预算 + 人数 |

## 安装

### 1. 拿到麦当劳 MCP Token

访问[麦当劳 MCP Server 使用指南](https://github.com/M-China/mcd-mcp-server)，
用手机号登录后，在「控制台」申请 MCP Token。

### 2. 在 WorkBuddy 中配置 MCP Server

打开 WorkBuddy，左侧边栏【专家·技能·连接器】→【连接器】→ 右上角【自定义连接器】→【配置 MCP】，
填入 `mcp-config.example.json` 的内容，**把 `${MCD_MCP_TOKEN}` 换成你的真实 Token**，保存并启用。

```json
{
  "mcpServers": {
    "mcd-mcp": {
      "type": "streamablehttp",
      "url": "https://mcp.mcd.cn",
      "headers": { "Authorization": "Bearer ${MCD_MCP_TOKEN}" }
    }
  }
}
```

> 本仓库中的 `mcp-config.example.json` 只使用环境变量占位符，不含任何真实凭据。

### 3. 安装本 Skill

本仓库是公开仓库，直接 clone 即可（仓库根目录就是 Skill 根目录）：

```bash
git clone https://github.com/HessianZ/chilemai.git ~/.workbuddy/skills/chilemai
```

也可以直接用浏览器打开 <https://github.com/HessianZ/chilemai>，点右上角 `Code` → `Download ZIP`，
解压后把目录重命名为 `chilemai` 放进 `~/.workbuddy/skills/`。

## 使用示例

直接说人话就行，不需要记任何指令。
以下展示交互方式，餐品、价格、优惠和时间以当次工具结果为准。

### 例 1 · 减脂

> **你**：中午想吃麦当劳，最近在减脂，预算 40
>
> **吃了麦**：配好了 ——
> - 板烧鸡腿堡 ￥27 · 391 kcal · 23 g 蛋白
> - 无糖可口可乐（中杯）￥11 · 0 kcal
>
> 合计约 **391 kcal / 38 元**，配餐不强行凑。门店选「杭州西湖区岳庙码头餐厅」（3.6 km，营业至 22:00），
> 领券后 33 元。要下单吗？

### 例 2 · 增肌

> **你**：练完了，想吃点高蛋白的，杭州西湖附近
>
> **吃了麦**：「培根安格斯厚牛堡」34 g 蛋白 / 707 kcal，配一盒纯牛奶再补 7 g，
> 合计 **41 g 蛋白 / 836 kcal**，￥52。备选「果然多肉」蛋白密度更高（36 g / 478 kcal）。

### 例 3 · 省钱

> **你**：随便来点，别超过 25
>
> **吃了麦**：吉士汉堡包 ￥15.5（294 kcal）+ 小杯玉米杯 ￥14.5 超预算了，
> 换成锡兰红茶 ￥9 的话合计 ￥24.5，296 kcal，不超预算。要用券吗？
> 我看了下本店有一张满 20 减 5 的券，用完 ￥19.5。

### 例 4 · 送到家

> **你**：不想出门，送家里，要个早餐
>
> **吃了麦**：[读地址簿] 送到「清竹园 9 号楼 2 单元 508」——
> 猪柳蛋麦满分 ￥18.5（387 kcal / 23 g 蛋白）+ 冰美式小杯 ￥11，合计 ￥29.5，约 30 分钟送达。

## 仓库结构

```
chilemai/
├── SKILL.md                  # Skill 主文件：触发条件与五阶段流程
├── references/
│   ├── goals.md              # 营养目标口径、阈值、真实数据锚点
│   ├── mcp-tools.md          # MCP 工具速查 + beType/orderType/beCode 矩阵
│   └── order-flow.md         # 四种场景的完整调用序
├── scripts/
│   └── chilemai.py           # 营养解析 / 可信匹配 / 整餐组合（仅标准库）
├── tests/                    # 离线回归用例与合成菜单/营养样本
├── mcp-config.example.json   # 脱敏后的 MCP 配置示例
├── MCP_INTEGRATION.md        # 实际使用的 MCP Server / Tool / 调用流程 / 业务价值
├── CONTEST_DECLARATION.md    # 参赛声明（原文，未改动）
└── workbuddy.md              # 使用 WorkBuddy 开发时的对话上下文
```

## 脚本用法

`scripts/chilemai.py` 只依赖 Python 标准库，解析**自定义文本营养表**（不是 JSON），
核实菜单与营养库的名称匹配，并在整餐合计上检查营养条件。

```bash
# 按目标筛选候选（低卡默认排除饮品与甜品）
python3 scripts/chilemai.py filter --goal light --limit 8 -f nutrition.txt

# 在售菜单 × 营养库 名称对齐
python3 scripts/chilemai.py match --menu menu.json --nutrition nutrition.txt

# 组合一餐：先核实菜单价格原值单位，元用 yuan，分用 fen
python3 scripts/chilemai.py plan --menu menu.json --nutrition nutrition.txt \
  --price-unit yuan --goal light --max-kcal 500 --limit 3

# 离线回归测试（合成数据，不接入真实账号、不创建订单）
python3 -m unittest discover -s tests -v
```

`match` 输出“精确对齐 / 待确认 / 未对齐”。前缀命中、杯型不明或营养冲突的项目只返回候选名称，
不再返回可用于合计的营养值；JSON 保留 `alias` 键，其项改为 `candidates` / `reason`。
套餐即使精确同名，也需查询实际组成，不能把「巨无霸三件套」当单品的 513 kcal。

`plan` 默认枚举 **1–3 份单品、至少一份主食**，同品可多份，配餐和饮品可选。
只纳入精确匹配且热量、蛋白和价格已知的主食/配餐/饮品，套餐不自动参与。
JSON 中 `items` 可供官方算价，`nutrition` 是按份数汇总的营养，缺失值保留 `null`；
`coverage` 展示匹配与可用候选数。没有方案时退出码为 `1`，参数或数据格式错误为 `2`。

`menu_subtotal_cents` 是**菜单估价（分）**，`--budget 40` 可选地将估价限制在 40 元内。
估价不含优惠、配送或打包费；寻找券后方案时可不设 `--budget`，最后用 `calculate-price`
核对实际总额与预算。脚本没有结果不代表全菜单或优惠后无解，也不会自动放宽约束。

内置目标：`high-protein`、`low-cal`、`light`、`low-fat`、`low-sodium`、`low-carb`、`any`。

## 注意事项

- 餐品信息、价格与供应状态**以麦当劳官方渠道的实时结果为准**
- 营养数据仅供搭配参考，**不构成医疗、营养或其他专业建议**
- 下单涉及真实支付，**任何订单都会先展示方案并等待你确认**

## 许可

MIT License，详见 [LICENSE](LICENSE)。

本项目为「麦当劳程序员创意开发大赛」参赛作品，由参赛者独立开发，**非麦当劳官方产品**。
