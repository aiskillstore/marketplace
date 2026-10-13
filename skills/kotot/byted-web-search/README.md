# byted-web-search

火山引擎豆包搜索 Skill，适用于 OpenClaw、Claude Code、OpenCode 等 Agent 工具。

## 安装

```bash
npx skills add https://skills.volces.com/skills/bytedance/agentkit-samples -s byted-web-search --agent openclaw
```

或直接将本目录放入 Agent 的 skills 目录。

## 使用前准备

1. **个人用户**：[创建 API Key](https://console.volcengine.com/search-infinity/api-key)
2. **Agent Plan 用户**：先 [配置 Harness](https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement?LLM=%7B%7D&advancedActiveKey=agentPlan)，再在 [apiKey 页](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D) 复制 Key
3. 在对话中将 Key 发给 Agent，或配置环境变量 `WEB_SEARCH_API_KEY`

## 验证

```bash
python3 scripts/web_search.py "北京今日天气" --api-key "您的Key"
```

## 快速开始

1. 将本目录放入skill目录
2. 获取 API Key：[豆包搜索控制台](https://console.volcengine.com/search-infinity/api-key) 或 [Agent Plan  控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement?LLM=%7B%7D&advancedActiveKey=agentPlan)以及[Agent Plan 企业版控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/openManagement?LLM=%7B%7D&advancedActiveKey=agentEnterprise)
3. 在聊天框直接发送 Key 给 Agent 即可


## 文档

| 文件 | 说明 |
|------|------|
| `SKILL.md` | Agent 运行时指令 |
| `references/setup-guide.md` | 开通与配置 |
| `references/quick-start.md` | 快速开通与迷路兜底 |
| `references/troubleshooting.md` | 错误码说明 |

## 官方 API 文档

https://www.volcengine.com/docs/87772/2272953

## 许可证

Apache License 2.0
