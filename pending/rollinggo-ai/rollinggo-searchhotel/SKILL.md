---
name: rollinggo-searchhotel
description: 使用 RollingGo CLI 查询酒店信息、筛选结果、读取酒店标签和获取房型价格。当用户需要按目的地 / 日期 / 星级 / 预算 / 标签 / 距离搜索酒店、查看酒店详情与房型报价，或读取酒店标签库时触发本技能。触发短语——"搜索酒店"、"查酒店"、"酒店详情"、"房型价格"、"酒店标签"、"附近酒店"、"rollinggo"。
homepage: https://rollinggo.store
metadata:
  {
    "openclaw": {
      "emoji": "🏨",
      "skillKey": "rollinggo-searchhotel",
      "primaryEnv": "RollingGo_API_KEY",
      "requires": {
        "anyBins": ["rollinggo", "npx", "node", "uvx", "uv"],
        "env": ["RollingGo_API_KEY"]
      },
      "install": [
        {
          "id": "node",
          "kind": "node",
          "package": "rollinggo@latest",
          "bins": ["rollinggo"],
          "label": "Install rollinggo (npm)"
        }
      ]
    }
  }
---

# RollingGo 酒店 CLI

## 适用范围

✅ **在以下情况使用本技能：**
- **查找候选酒店：** 用户需要按城市、地标、机场或具体地址搜索附近酒店（例如：“查找东京迪士尼附近的酒店”）。
- **多条件精准筛选：** 用户需要在搜索时结合自然语言意图，并严格限制入离日期、入住人数、预算上限、星级区间或距离范围。
- **基于标签与品牌匹配：** 用户想寻找包含特定设施或属于特定品牌的酒店（如“亲子友好”、“包含早餐”、“万豪”等），技能可先查询标签库以进行精准筛选。
- **查询房型与实时报价：** 用户想深入了解某家具体酒店（通过 hotelId）的可用房型、实时价格、退款政策或具体配置。
- **酒店对比与评估：** 用户需要基于真实的结构化数据和当前报价，在多个候选酒店中进行对比分析。
- **酒店预订：** 用户选定酒店想要完成预订时。可提取并提供结果中的预订 URL 或酒店主页链接，引导用户直接点击完成购买。

❌ **以下情况不适用：**
- 用户询问非酒店类的旅游预订业务（如机票、火车票、接送机、租车等）。

## API Key

解析顺序：`--api-key` 参数 → `RollingGo_API_KEY` 环境变量。

还没有 Key？前往申请：https://mcp.agentichotel.cn/apply

## 运行环境

默认加载 [references/rollinggo-npx.md](references/rollinggo-npx.md)；用户明确使用 `uv`/`uvx`/Python 时改加载 [references/rollinggo-uv.md](references/rollinggo-uv.md)。API Key 持久化配置见 [references/claw-host-env.md](references/claw-host-env.md)。

## 版本新鲜度（始终使用最新版）

本技能默认策略：每次执行都使用最新发布版本。

- **npm/npx：** `npx --yes --package rollinggo@latest rollinggo ...`
- **uvx：** `uvx --refresh --from rollinggo@latest rollinggo ...`

如果使用已安装命令而不是临时执行，先升级再运行：

- **npm 全局：** `npm install -g rollinggo@latest`
- **uv 工具：** `uv tool upgrade rollinggo@latest`

## 主要工作流

除非用户已经把问题限定在某个具体步骤，否则按顺序执行：

1. 明确需求：目的地、日期、晚数、入住人数、预算、星级、标签、距离
2. 如果需要标签筛选 → 先执行 `hotel-tags` 获取有效标签字符串
3. 执行 `search-hotels` → 解析 JSON → 提取 `hotelId`
4. 执行 `hotel-detail --hotel-id <id>` 查询房型和价格
5. 如果结果不理想 → 放宽筛选条件后重新搜索

## 常用命令速查

```bash
# 获取标签库
rollinggo hotel-tags

# 搜索酒店（最少必填参数）
rollinggo search-hotels \
  --origin-query "<用户的自然语言描述>" \
  --place "<目的地>" \
  --place-type "<查看 --help 获取合法值>"

# 查询酒店详情与价格
rollinggo hotel-detail \
  --hotel-id <id> \
  --check-in-date YYYY-MM-DD \
  --check-out-date YYYY-MM-DD \
  --adult-count 2 --room-count 1

# 查看所有可用参数
rollinggo search-hotels --help
rollinggo hotel-detail --help
```

## 关键规则

- `--place-type` 必须使用 `rollinggo search-hotels --help` 里显示的精确值
- `--star-ratings` 格式：`最小值,最大值`，如 `4.0,5.0`
- `--format table` **只允许**用于 `search-hotels`；`hotel-detail` 和 `hotel-tags` 会拒绝该参数
- `--child-count` 的数量必须与 `--child-age` 参数的个数一致
- `--check-out-date` 必须晚于 `--check-in-date`
- 有 `hotelId` 时优先使用 `--hotel-id`，不要依赖 `--name`

## 输出说明

- stdout → 结果数据（默认 JSON）
- stderr → 仅错误信息
- 退出码 `0` 成功 · `1` HTTP/网络失败 · `2` CLI 参数校验失败
- 结果中包含预订 URL 与酒店详情页链接，可供下游直接使用

## 无结果时的放宽策略

按顺序尝试：移除 `--star-ratings` → 增大 `--size` → 增大 `--distance-in-meter` → 移除标签筛选 → 放宽日期或预算
