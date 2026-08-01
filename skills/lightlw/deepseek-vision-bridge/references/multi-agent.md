# 多 Agent 适配指南

`ocr-proxy.js` 是一个本地 HTTP 代理,不是 Codex 专属。任何通过
OpenAI 兼容 API(Responses / Chat Completions)或 Anthropic Messages API
连接 DeepSeek 的 agent,只要把 API 地址指向代理端口,即可获得看图能力;
生图则可直接调用 `image-gen.js`。

## 核心原理

```
任意 agent ──API请求──▶ 本地代理(:57323) ──文字──▶ DeepSeek API
                              │
                              └─ 图片转文字(OCR / 本地VLM / 云端VL)
```

代理会拦截请求体中的图片,替换为文字描述后转发;同时把 Authorization
头替换为 `.env` 中的 `DEEPSEEK_API_KEY`。因此客户端侧的 API key 可以
随便填占位符。

## 接入清单

### 1. Codex(Responses API)

修改 `~/.codex/config.toml`:

```toml
model = "deepseek-v4-flash"
model_provider = "custom"

[model_providers.custom]
name = "custom"
wire_api = "responses"
requires_openai_auth = true
base_url = "http://127.0.0.1:57323/v1"
approvals_reviewer = "user"
```

### 2. Claude Code(Anthropic Messages API)

设置环境变量:

```bash
export ANTHROPIC_BASE_URL="http://127.0.0.1:57323/v1"
export ANTHROPIC_AUTH_TOKEN="任意占位符"
export ANTHROPIC_MODEL="deepseek-v4-flash"
```

注:代理已兼容 Anthropic 风格的图片格式(`source.data` base64)。
建议首次使用前用一张图实测。

### 3. Cherry Studio / Chatbox 等桌面客户端

在模型的 API 设置里:

- API 地址:`http://127.0.0.1:57323/v1`
- API Key:任意占位符(代理会替换为 DeepSeek key)
- 模型名:`deepseek-v4-flash`

### 4. Dify / FastGPT 等平台

自定义模型接入时,OpenAI 兼容配置:

- API Endpoint:`http://127.0.0.1:57323/v1`
- API Key:占位符
- Model:`deepseek-v4-flash`

### 5. OpenAI SDK / LangChain / AutoGen 等

```python
from openai import OpenAI
client = OpenAI(
    base_url="http://127.0.0.1:57323/v1",
    api_key="placeholder",
)
```

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="http://127.0.0.1:57323/v1",
    api_key="placeholder",
)
```

## 协议兼容矩阵

| 协议 | 状态 |
|---|---|
| OpenAI Responses API(Codex) | ✅ 完整支持 |
| OpenAI Chat Completions(Cherry Studio/Dify/SDK) | ✅ 完整支持 |
| Anthropic Messages API(Claude Code) | ⚠️ 图片格式已兼容,建议实测 |

## 生图供任意 agent 使用

`image-gen.js` 是独立 CLI,任何 agent 都能在终端调用:

```bash
node image-gen.js "提示词" --mode fast
node image-gen.js "提示词" --mode flux
```

输出为 Markdown 图片路径引用,不占用模型上下文。
