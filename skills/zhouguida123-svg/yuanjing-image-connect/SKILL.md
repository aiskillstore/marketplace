---
name: yuanjing-image-connect
description: Connect a compatible desktop agent to Yuanjing AI for image generation, image editing, and product visuals. Use when the user asks to connect Yuanjing AI, check an existing connection, or create images with Yuanjing AI (源景AI).
---

# 源景 AI 作图连接器

本入口引导 Agent 安装和连接官网的 `yuanjing-ai` 技能。只问用法、写提示词或做视觉策划时，直接回答。用户明确要求连接或使用源景作图时，再开始连接检查。

## 安装与连接

1. 读取 [官方实时清单](https://yuanjing-ai.com/.well-known/yuanjing-agent-skill.json) 和 [官方安装细则](https://yuanjing-ai.com/.well-known/yuanjing-agent-install.md)。检查宿主能否执行本地连接程序、保护凭据并安装技能。网页端或托管 Agent 缺少这些能力时，给出官方安装细则，引导用户在支持本地安装的桌面 Agent 完成。
2. 有有效的本机源景凭据时，沿用现有凭据。首次连接时，按官方细则从清单的 `bootstrap.connect_url` 获取认证脚本，先校验 `bootstrap.connect_sha256`，再在本机运行 `node <本地连接脚本> --wait-for-connection`。用户只在官方程序的本机交互提示中输入自己的授权码。切勿在聊天、命令参数、日志或 URL 中收集、传递或回显授权码。遇到凭据问题按官网细则排查。
3. 按清单 `current_version` 和 `sha256` 验证官方包。需要安装或升级时，认证后拉取官网授权包并验证 SHA-256，以宿主原生方式安装为 `yuanjing-ai`。保留已有凭据和用户资料，遵守服务端下载权限。官网清单与细则提供最新操作方法。
4. 从已验证的正式技能目录执行官方 `scripts/yuanjing-agent-connect.cjs --wait-for-connection`，只读检查版本、认证和开放能力。分别确认连接、完整版安装和宿主工具加载状态。出现 `awaiting_interactive_terminal` 时，提示用户完成本机窗口操作，再检查同一次连接。

## 使用源景作图

- 把用户提供的素材、目标、数量和约束交给已连接的 `yuanjing-ai`。实时读取账户开放的模型及功能。
- 上传素材前确认用户授权和必要用途。生成消耗源景账户算力，按实时精确报价及用户确认的预算执行。连接与只读检查不发起生成。
- 超时后先查同一任务并恢复原产物，避免重复扣费。只有实际拿到结果才报告完成。
