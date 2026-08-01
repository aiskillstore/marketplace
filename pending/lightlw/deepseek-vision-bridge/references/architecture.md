# 架构说明

## 目标

让纯文本模型（DeepSeek 等）在 Codex 对话栏中也能"看图"和"生图"：

- **看图**：在 Codex 与 DeepSeek 之间插入本地代理，拦截请求中的图片，
  交给视觉引擎转成文字描述后再转发给 DeepSeek。
- **生图**：由 `image-gen.js` 直接调用生图后端（硅基流动 API 或本地扩散模型），
  图片保存到文件，只把路径交给模型，避免 Base64 撑爆上下文。

## 请求链路（看图）

```
Codex 桌面端
  │  对话栏贴图 → 请求体含 image_url
  ▼
本地代理 ocr-proxy.js (:57323)     ← config.toml 的 base_url 指向这里
  │  检测到图片 → 三级引擎路由
  │    ① 纯文字意图(关键词) → Tesseract OCR
  │    ② 图文/纯图 → 云端 VL(硅基流动, 可选)
  │    ③ 云端失败/离线 → 本地 VLM(Ollama)
  │  图片替换为 input_text 文字描述
  ▼
DeepSeek 官网 API (api.deepseek.com, Responses API)
  ▼
纯文本回复 → 回到 Codex 对话
```

## 生图链路

```
用户要求生图
  ▼
Codex 调用 image-gen.js
  ├─ fast  → 硅基流动通义万相 API（快，需 key）
  ├─ enhanced → SDXL 本地（GPU）
  ├─ lightweight → SD 1.5 本地（CPU/GPU）
  └─ flux → Flux.1-dev 本地（最高画质，需下载模型）
  ▼
图片保存到 outputs/，返回 Markdown 路径引用（不占 token）
```

## 三级看图引擎对比（实测）

| 引擎 | 视觉理解 | 文字提取 | 速度 | 依赖 |
|---|---|---|---|---|
| OCR (Tesseract) | ❌ 只认文字 | ✅ 精确 | ~2s | 无（本地） |
| 本地 VLM (Ollama minicpm-v:8b) | ✅ 准确 | ✅ 概括性 | ~15-70s | Ollama + 模型 |
| 云端 VL (硅基流动 Qwen3-VL) | ✅ 最详细 | ✅ | ~30s | 需注册 key |

## 缓存

同一张图（按内容 hash）处理过一次即缓存，后续请求直接复用，不重复调用引擎。
缓存上限 500 条，LRU 淘汰。

## 关键文件

| 文件 | 作用 |
|---|---|
| `assets/ocr-proxy.js` | 本地看图代理（复制到用户目录） |
| `assets/image-gen.js` | 生图工具 |
| `assets/.env.template` | 配置模板（key、端口、模型名） |
| `assets/start-proxy.ps1/.sh` | 代理启动脚本 |
| `assets/install-autostart.ps1` | Windows 开机自启 |
