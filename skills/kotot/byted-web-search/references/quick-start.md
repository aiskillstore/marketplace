# 快速开通

## 个人用户

```
https://console.volcengine.com/search-infinity/api-key
→ 创建 API Key → 复制 → 发给 Agent → 说「好了」
```

## Agent Plan 用户（两步）

**第 1 步：配置 Harness**

```
https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement?LLM=%7B%7D&advancedActiveKey=agentPlan
→ 进入「配置 Harness」
→ 开通「联网搜索」/「豆包搜索」（控制台可能显示 Beta 版）
```

**第 2 步：复制 API Key**

```
https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D
→ 复制 API Key → 发给 Agent → 说「好了」
```

企业版 Harness 入口：`advancedActiveKey=agentEnterprise`（Key 仍在 apiKey 页复制）。

## Key 自检

| Key 来源 | 说明 |
|---------|------|
| search-infinity/api-key | ✅ 个人用户 |
| ark apiKey 页（先配 Harness） | ✅ Agent Plan 用户 |
| 仅完成 Harness 未去 apiKey 页 | ❌ 还需第 2 步复制 Key |

## 官网迷路

| 您看到的页面 | 建议 |
|-------------|------|
| Agent Plan → 使用配置 → 配置 Harness | ✅ 第 1 步：开通联网搜索/豆包搜索 |
| Agent Plan → apiKey 页 | ✅ 第 2 步：复制 Key |
| 火山方舟其他 API 密钥页 | 不是本 skill 用的 Key，请走上方两步 |
| search-infinity/api-key | ✅ 个人用户专用 |

仍有问题可提交[工单](https://console.volcengine.com/workorder/create?step=1&SubProductID=P00001696)。
