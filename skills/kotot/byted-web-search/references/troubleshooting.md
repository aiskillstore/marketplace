# 故障排查

## 错误码

| Code | 含义 | 处理 |
|------|------|------|
| `未找到凭证` | 未配置 Key | 见 setup-guide 获取 Key |
| `invalid_api_key` / `10403` | Key 无效 | 个人用 api-key 页；Agent Plan 先 Harness 再 apiKey 页 |
| `401 InvalidAccessKey` | AK/SK 失效 | 改用 API Key |
| `429` / `FlowLimitExceeded` / `100018` | 限流 | 降频，并发 ≤ 5 |
| `700429` | 免费链路限流 | 降频重试 |
| `10400` | 参数错误 | 检查搜索词长度、条数、时间范围 |
| `10402` | 类型非法 | 仅 web/image |
| `10406` | 额度耗尽 | 次月 1 日重置；[充值](https://console.volcengine.com/finance/fund/recharge) |
| `10407` | 无免费策略 | 检查 [开通](https://console.volcengine.com/search-infinity/web-search) |
| `10408` / `FunctionUnavailable` | 欠费 | [充值](https://console.volcengine.com/finance/fund/recharge) |
| `10409` | 套餐不支持 | 换 web/image |
| `10412` | 套餐额度不足 | 充值或联系管理员 |
| `10500` | 内部错误 | 2–3 秒后重试 |
| `100013` | 子账号无权限 | 授权 `TorchlightApiFullAccess` |

## 额度

- 免费：主账号 500 次/月，次月 1 日重置
- 查询：[数据管理](https://console.volcengine.com/search-infinity/web-search-interface)
- 充值：https://console.volcengine.com/finance/fund/recharge
