# 开通与配置

## 获取 API Key

### 个人用户

1. [正式开通](https://console.volcengine.com/search-infinity/web-search)
2. [创建 API Key](https://console.volcengine.com/search-infinity/api-key)
3. 复制 Key，在对话中发给 Agent

### Agent Plan 用户（两步）

**第 1 步 — 配置 Harness**

1. 打开 [Agent Plan 使用配置](https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement?LLM=%7B%7D&advancedActiveKey=agentPlan)（[企业版](https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement?LLM=%7B%7D&advancedActiveKey=agentEnterprise)）
2. 在流程第 2 步「**配置 Harness**」中，开通「**联网搜索**」/「**豆包搜索**」
3. 确认 Harness 卡片显示已开通（控制台可能标注 Beta 版）

**第 2 步 — 复制 API Key**

1. 打开 [Agent Plan API Key 页](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D)
2. 复制 API Key
3. 在对话中发给 Agent

> 顺序不能颠倒：须先配 Harness，再在 apiKey 页复制 Key。

## 配置方式

**优先**：拿 Key 后直接在聊天框发给我即可，无需编辑任何配置文件。

**或** 在 Claw 技能/凭证配置中填写 `WEB_SEARCH_API_KEY`：
- **OpenClaw**：编辑 `~/.openclaw/openclaw.json`，在 `skills.entries` 下添加：
  ```json
  "byted-web-search": {
    "enabled": true,
    "env": { "WEB_SEARCH_API_KEY": "您复制的Key" }
  }
  ```
- **其他 Claw**：在技能配置界面填写 `WEB_SEARCH_API_KEY` 即可

**本地使用**：skill 根目录创建 `.env`（内容 `WEB_SEARCH_API_KEY=your_key`），或 `export WEB_SEARCH_API_KEY="..."` 写入 ~/.bashrc。

**AK/SK**（可选）：`VOLCENGINE_ACCESS_KEY` + `VOLCENGINE_SECRET_KEY`。

## 常见问题

| 问题 | 解答 |
|------|------|
| Agent Plan Key 在哪复制？ | [apiKey 页](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D)，不是 Harness 页单独密钥 |
| 为什么要先配 Harness？ | 豆包搜索是 Agent Plan 的 Harness 能力，需先开通 |
| 豆包搜索 / 联网搜索 / 融合信息搜索 | 同一产品 |
| Coding Plan | 已升级为 Agent Plan |
| 10406 额度用完 | 次月 1 日重置；[充值](https://console.volcengine.com/finance/fund/recharge) |

## 官方链接

- API 文档：https://www.volcengine.com/docs/87772/2272953
- Agent Plan Harness：https://www.volcengine.com/docs/82379/2301412
