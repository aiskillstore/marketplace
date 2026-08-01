# 看图引擎选型指南

按用户环境从优到劣选择，把选择理由讲给用户，让用户确认。

## 路线一：云端 VL（硅基流动）— 推荐新手

- 优点：无需 GPU、模型质量最高、安装最简单
- 缺点：需注册 [cloud.siliconflow.cn](https://cloud.siliconflow.cn) 拿 key（有免费额度）
- 模型：`Qwen/Qwen3-VL-8B-Instruct`（代理内置默认）
- 适用：任何配置的电脑；不想折腾本地模型

## 路线二：本地 VLM（Ollama）— 推荐离线/隐私优先

- 优点：免费、离线可用、图片不出本机
- 缺点：需下载模型（2-6GB），8B 模型首张图约 1 分钟；无 GPU 会慢
- 安装：
  ```
  # 安装 Ollama: https://ollama.com/download
  ollama pull minicpm-v:8b        # 或 qwen2.5-vl:7b / llama3.2-vision:11b
  ```
- 配置：`LOCAL_VL_MODEL=minicpm-v:8b` 写入 .env
- 适用：有 NVIDIA GPU（≥6GB 显存）；或能接受 CPU 慢速

## 路线三：仅 OCR — 兜底

- 纯文字截图/扫描件时最快最准；对无文字图片无效
- 无需任何模型或 key，代理内置

## 组合策略（代理自动执行）

1. 用户提示词含"提取/识别/转录文字"等意图 → 直接 OCR
2. 否则图文/纯图 → 云端 VL（配了 key 时）
3. 云端失败/离线/超时 → 本地 VLM（装了 Ollama 时）
4. 全部不可用 → 返回明确错误，提示用户补配置

云端连续失败 2 次进入 5 分钟冷却，期间直接走本地 VLM，避免干等超时。

## 生图后端选型

| 模式 | 速度 | 质量 | 依赖 |
|---|---|---|---|
| fast（硅基流动 API） | ~4-10s | 好 | key |
| enhanced（SDXL） | ~30s+ | 好 | GPU ≥8GB |
| lightweight（SD 1.5） | ~30-60s | 一般 | CPU 也行 |
| flux（Flux.1-dev） | ~3min | 最高 | GPU ≥12GB + 模型 |
