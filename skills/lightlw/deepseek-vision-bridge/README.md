# DeepSeek Vision Bridge

为 DeepSeek(及任何纯文本模型)提供**看图**和**生图**能力的一站式部署 skill。
适配 Codex、Claude Code、Cherry Studio、Dify 等所有走 OpenAI/Anthropic 兼容
接口连接 DeepSeek 的 agent。

安装后,在对话栏直接粘贴图片即可自动"看懂";说出生图需求即可自动生成图片。

## 特性

- **看图三级引擎**:纯文字图走 OCR(快/准),图文与纯图走视觉大模型,
  云端不可用时自动降级本地 VLM(Ollama),全程不需要图片二进制进入上下文
- **生图多后端**:硅基流动 API(fast)或本地 SDXL / SD 1.5 / FLUX
- **零注册可选**:只装 Ollama + 开源视觉模型即可离线看图;硅基流动注册只是可选的"更快"路线
- **一键环境自检**:`scripts/check_env.py` 自动检测 Node / Ollama / GPU / 端口 / 现有配置
- **自动开机自启**(Windows)与跨平台启动脚本
- **多 agent 适配**:不只 Codex,Claude Code / Cherry Studio / Dify 等都能接

## 安装

### 方式一:Codex 中直接使用

将本仓库 `SKILL.md` 所在目录复制到 `~/.codex/skills/codex-vision-bridge/`
(Windows 为 `%USERPROFILE%\.codex\skills\codex-vision-bridge\`),
然后在对话中告诉 Codex:"配置看图生图能力"。

### 方式二:手动部署

1. 复制 `assets/` 下全部文件到你的代理目录(如 `~/codex-vision-bridge/`)
2. 把 `assets/.env.template` 重命名为 `.env` 并填写:
   - `DEEPSEEK_API_KEY`(必填):[DeepSeek 平台](https://platform.deepseek.com)获取
   - `SILICONFLOW_API_KEY`(可选):[硅基流动](https://cloud.siliconflow.cn)获取
   - `LOCAL_VL_MODEL`(可选):本地视觉模型名,如 `minicpm-v:8b`
3. 安装依赖并启动:
   ```bash
   cd <代理目录>
   npm install
   ./start-proxy.sh          # macOS / Linux
   # Windows: powershell -ExecutionPolicy Bypass -File start-proxy.ps1
   ```
4. 修改 `~/.codex/config.toml`,让 Codex 走代理(详见 `SKILL.md` 或
   `references/architecture.md`)
5. (Windows 可选)设置开机自启:
   ```powershell
   powershell -ExecutionPolicy Bypass -File install-autostart.ps1
   ```

> 使用 Claude Code、Cherry Studio 等其他 agent?见
> [references/multi-agent.md](references/multi-agent.md) 的接入配置。

## 工作原理

```
Codex ──贴图──▶ 本地代理(:57323) ──文字──▶ DeepSeek API
                    │
                    ├─ 纯文字图 → OCR (Tesseract)
                    ├─ 图文/纯图 → 云端 VL (硅基流动 Qwen3-VL)
                    └─ 云端失败/离线 → 本地 VLM (Ollama)
```

图片经代理转为文字描述后才发给 DeepSeek,既不依赖 DeepSeek 的多模态能力,
也不会因 Base64 图片撑爆上下文。

## 文档

- 架构与缓存:`references/architecture.md`
- 引擎选型(本地/云端/OCR 对比):`references/model-guide.md`
- 其他 agent 接入(Claude Code / Cherry Studio / Dify 等):`references/multi-agent.md`
- 故障排查:`references/troubleshooting.md`

## 许可

MIT License
