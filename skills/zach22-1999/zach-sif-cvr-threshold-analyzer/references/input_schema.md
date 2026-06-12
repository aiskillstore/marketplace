# 输入字段说明

## 业务报告

优先使用领星 ASIN 360 导出的日级 ASIN 业务报表。脚本也兼容常见 CSV / XLSX / XLSM 文件，只要字段能映射到下面的标准字段。

脚本默认读取第一个工作表或 CSV 表头。

## 最低必需字段

| 标准字段 | 支持别名 | 说明 |
|---|---|---|
| 日期 | `时间`, `日期`, `date`, `day`, `report date` | 日级数据，必须连续 |
| ASIN | `ASIN`, `asin`, `子ASIN`, `商品ASIN` | 如果存在该列，会过滤目标 ASIN |
| Session | `Sessions-Total`, `Sessions Total`, `sessions`, `会话数`, `总会话数`, `访客数`, `父体访客数` | 用于判断流量放大 |
| 整体 CVR | `CVR`, `Conversion Rate`, `转化率`, `整体CVR`, `买家转化率` | 主监控候选 |

## 推荐字段

| 标准字段 | 支持别名 | 用途 |
|---|---|---|
| 广告 CVR | `广告CVR`, `Ad CVR`, `Advertising CVR`, `PPC CVR`, `广告转化率` | 广告 CVR 确认线 |
| 自然 CVR | `自然CVR`, `Organic CVR`, `Natural CVR`, `自然转化率` | 辅助判断 |
| 点击 | `点击`, `clicks`, `广告点击`, `广告点击量` | 转化拆解 |
| 广告订单 | `广告订单量`, `Ad Orders`, `Advertising Orders`, `广告订单` | 广告承接 |
| 自然点击 | `自然点击量`, `Organic Clicks`, `自然点击` | 自然承接 |
| 自然订单 | `自然订单量`, `Organic Orders`, `自然订单` | 标记负订单调整日 |
| 销量 | `销量`, `units`, `Units`, `Units Ordered`, `商品销量` | 业务背景 |
| 订单量 | `订单量`, `orders`, `Orders`, `Total Orders`, `订单` | 业务背景 |

## CVR 解析规则

脚本会把以下值统一转为小数：

| 原始值 | 解析结果 |
|---|---:|
| `2.78%` | `0.0278` |
| `2.78` | `0.0278` |
| `0.0278` | `0.0278` |

## SIF JSON 缓存

公开版脚本只读取用户自己保存的本地 JSON。建议结构：

```json
{
  "source": "user-provided SIF cache",
  "daily": {
    "2026-01-01": {
      "details": [
        {
          "keyword": "example keyword",
          "scoreRatio": 0.02,
          "score": 100,
          "pchangeReason": {
            "nfInfo": {"change": "10_16"},
            "spInfo": {"change": "1_2"}
          }
        }
      ]
    }
  }
}
```

其中：

- `daily` 必须是按日期分组的对象。
- 每天可以使用 `details`、`records` 或 `list` 作为关键词明细列表。
- 自然位变化优先读取 `pchangeReason.nfInfo.change`，格式为 `before_after`。
- 广告位变化优先读取 `pchangeReason.spInfo.change`，格式为 `before_after`。
- `scoreRatio` / `score` 可选，但有助于自动筛选核心词和稳定词。

## 数据质量规则

- 日期不连续时直接报错，不继续生成阈值。
- 业务报告没有目标 ASIN 行时直接报错。
- SIF 缓存缺失或没有可用关键词记录时直接报错。
- 自然订单量为负，或自然 CVR 为负的日期，会被标记为 `organic_negative_adjustment`。
- 负自然订单调整日不参与自然 CVR 主阈值选择。
- 样本窗口少于 21 天时，报告可以生成，但必须标记为小样本风险。
