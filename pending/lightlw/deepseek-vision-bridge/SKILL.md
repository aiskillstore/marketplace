---
name: deepseek-vision-bridge
description: >-
  Deploy and maintain image understanding (OCR + local VLM + cloud VL) and image
  generation for Codex connected to text-only models like DeepSeek. Use when the
  user wants to see/read images in the conversation bar with a text-only model,
  set up automatic OCR or vision-model processing for pasted images, configure
  image generation via SiliconFlow or local Stable Diffusion/Flux, fix a broken
  vision proxy, or asks "看图/生图/贴图识别/图片理解/OCR代理" on a Codex+DeepSeek
  setup. Deploys a local proxy between Codex and the model that converts images
  to text before forwarding.
---

# DeepSeek Vision Bridge

为 Codex + 纯文本模型(DeepSeek)部署"看图 + 生图"能力。

核心机制:本地代理拦截 Codex 请求中的图片,用三级引擎(OCR / 本地VLM / 云端VL)
转成文字后再转发给 DeepSeek;生图由 image-gen.js 完成后返回文件路径。

## 部署流程

### Step 1: 环境自检

运行 `scripts/check_env.py`(需要 Python 3),得到 JSON 报告:

```bash
python scripts/check_env.py
```

关注字段:`node`、`ollama_installed`、`ollama_models`、`gpu`、
`proxy_port_open`、`codex_config`、`deepseek_key_configured`。

### Step 2: 确定部署位置与路线

选定代理目录(例如 `~/codex-vision-bridge/` 或用户偏好位置),创建:

```text
<代理目录>/
├── ocr-proxy.js          ← 从 assets/ 复制
├── image-gen.js          ← 从 assets/ 复制
├── config.json           ← 从 assets/config.json.template 复制
├── package.json          ← 从 assets/ 复制
├── .env                  ← 从 assets/.env.template 复制并填写
├── start-proxy.ps1 / .sh ← 从 assets/ 复制（按平台）
└── node_modules/         ← npm install 生成
```

按 `references/model-guide.md` 与用户确认路线:

- 注册了硅基流动 key → 云端 VL 看图 + fast 生图
- 有 GPU 且愿意装模型 → Ollama 本地 VLM + 本地 SDXL/FLUX 生图
- 都不愿意 → 仅 OCR(纯文字图可用)

### Step 3: 复制文件并填配置

复制 assets 下文件到代理目录,然后编辑 `.env`:

```bash
DEEPSEEK_API_KEY=sk-...          # 必填,DeepSeek 平台获取
SILICONFLOW_API_KEY=sk-...       # 可选,硅基流动获取
LOCAL_VL_MODEL=minicpm-v:8b      # 可选,本地 VLM 模型名
OCR_PROXY_PORT=57323             # 默认
```

若用户选本地 VLM,先安装 Ollama 并拉模型:

```bash
# Windows/macOS: https://ollama.com/download
ollama pull minicpm-v:8b
```

### Step 4: 安装依赖并启动代理

```bash
cd <代理目录>
npm install        # 安装 tesseract.js
./start-proxy.sh   # macOS/Linux
# 或 powershell -ExecutionPolicy Bypass -File start-proxy.ps1  # Windows
```

验证端口监听:57323(或自定义端口)。启动日志在 `<代理目录>/outputs/proxy.log`。

### Step 5: 配置 Codex 指向代理

修改 `~/.codex/config.toml`(Windows 为 `%USERPROFILE%\.codex\config.toml`):

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

关键:`model_provider = "custom"` + `base_url` 指向代理端口。
改配置前先备份原文件。注意 config.toml 用 UTF-8 无 BOM。

### Step 6: 设置开机自启(Windows 可选)

```powershell
powershell -ExecutionPolicy Bypass -File install-autostart.ps1
```

### Step 7: 验证

1. 重启 Codex 会话(让 config.toml 生效)
2. 对话栏贴一张图 → 应看到模型基于图片内容回答
3. 查看代理日志确认路由(OCR / 云端 VL / 本地 VLM)
4. 要求生图 → 应看到 image-gen.js 生成的图片
5. 若纯文字截图 → 提示词带"提取文字",验证走 OCR

## 故障排查

见 `references/troubleshooting.md`,按症状查:
端口未监听 / 400 / 401 / 超时 / OCR 乱码 / Ollama 连接失败 / 生图失败。

## 引擎选型与架构

- 引擎对比与组合策略:`references/model-guide.md`
- 请求链路与缓存设计:`references/architecture.md`

## 重要原则

- 图片二进制不进上下文:代理转文字、生图返回路径,禁止 Base64 内联
- 纯文字图优先 OCR;图文/纯图走 VLM;云端失败自动降级本地
- 每台机器的 key、端口、模型名不同,以用户机器的 .env / config.toml 为准
