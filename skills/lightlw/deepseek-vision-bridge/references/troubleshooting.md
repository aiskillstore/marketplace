# 故障排查

## 代理没生效 / 贴图后 DeepSeek 答非所问

- 检查代理是否在运行：`netstat -ano | findstr :57323`（Windows）或
  `lsof -iTCP:57323 -sTCP:LISTEN`（macOS/Linux）
- 检查 config.toml 的 `base_url` 是否指向 `http://127.0.0.1:57323/v1`，
  `model_provider` 是否为 `custom`
- 看代理日志：`<代理目录>/outputs/proxy.log` 末尾，
  应有"图片处理完成，请求已修改"

## 400 Bad Request

- 检查 .env 中 `DEEPSEEK_API_KEY` 是否正确
- 代理日志若显示"云端 VL 失败"，通常只是降级到本地 VLM，不影响请求本身

## 401 Unauthorized

- `DEEPSEEK_API_KEY` 缺失或无效；确认 .env 在 ocr-proxy.js 同目录

## 贴图后请求超时

- 云端 VL 超时 30s、本地 VLM 超时 120s 属正常（首次加载模型慢）
- 查看日志确认当前走的是哪个引擎

## OCR 输出乱码/无意义

- 正常现象：对无文字的图片（照片、绘画）OCR 无效，应走 VLM 路线
- 确认 .env 配了 SILICONFLOW_API_KEY 或本地装了 Ollama 模型

## 本地 VLM 失败（connection refused）

- Ollama 未启动：运行 `ollama serve` 或重启 Ollama 应用
- 模型未拉取：`ollama pull minicpm-v:8b`

## 代理启动失败

- 缺 Node.js：安装 LTS（https://nodejs.org）
- 缺依赖：在代理目录运行 `npm install`（tesseract.js）
- 端口被占：改 .env 的 `OCR_PROXY_PORT`

## 生图失败

- `SILICONFLOW_API_KEY` 未配 → 走本地模式（需 GPU+模型）或提示注册
- 本地模式缺模型：`--setup` 引导下载，或按显存选 SDXL/SD1.5/FLUX
