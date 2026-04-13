---
name: seedance-prompt
description: |
  为 Seedance 2.0 视频生成模型撰写产品宣传动画提示词（Motion Graphics Prompt）。
  生成 15 秒一镜到底的动态影像提示词，支持 4 种美学风格（Apple/Microsoft/Bauhaus/Vercel）。
  支持垫图（参考图）模式，自动标注图片占位符。
  生成提示词后可通过即梦 Dreamina CLI 直接生成视频（自动检测安装状态）。
  TRIGGER when: 用户需要生成 Seedance 视频提示词、产品宣传动画提示词、motion graphics prompt，
  或提到 "Seedance"、"视频提示词"、"产品动画"、"宣传视频提示词"、"video prompt"。
  Keywords: Seedance, 视频提示词, video prompt, motion graphics, 产品动画, 宣传动画, 垫图, Dreamina
---

# Seedance 2.0 产品宣传动画提示词生成器

## 交互流程

### Step 1: 收集信息

使用 AskUserQuestion 向用户询问以下信息（一次性问完）：

1. **产品信息**：你的产品叫什么名字？请简要描述产品定位和核心功能。
2. **具体需求**：你希望视频重点展示什么？（如某个功能、品牌调性、技术特点）
3. **图片素材**：是否有图片素材可以提供？（产品图、Logo 图、界面截图等）
   - 如果有，请用户直接发送图片或提供图片路径
4. **口播需求**：是否需要口播（Voiceover）？如果需要，请说明语言和大致内容方向

### Step 2: 分析素材

- 读取用户提供的产品描述，提取核心特征
- 如果用户提供了图片，使用 Read 工具查看图片内容，分析 Logo 结构、产品界面布局、品牌色彩等
- 根据产品定位，从美学风格矩阵中选择最合适的风格（A/B/C/D）

### Step 3: 生成提示词

读取 [references/prompt-system.md](references/prompt-system.md) 获取完整的提示词系统规则，包括：
- 美学风格矩阵详细描述
- 严格撰写规则（字数限制、镜头约束、形变过渡等）
- 时间戳结构和输出模板

按照 prompt-system.md 中的规则和模板生成最终提示词。

### Step 4: 垫图引导（如涉及参考图）

Seedance 2.0 支持"垫图"（参考图）功能。如果生成的提示词需要用到用户提供的图片作为参考：

1. 告知用户在 Seedance 2.0 中选择 **"全能参考"** 模式
2. 明确标注每张图片的占位符和用途，例如：
   - `[图片一]` → Logo 图，用于 9-12s 的 Logo 形态参考
   - `[图片二]` → 产品界面截图，用于 2-5s 的界面形态参考
3. 说明用户需要在 Seedance 界面中将对应图片拖入对应位置

### Step 5: 输出与检查

- 输出纯英文提示词
- 确认字符数在 1000-2000 之间（用 `wc -c` 验证）
- 如果超出 2000 字符，精简后重新输出
- 提示词中应包含 Music 和 Sound Design 描述；如果用户需要口播，还需包含 Voiceover 脚本
- 附上中文说明：选用的风格、每个时间段的设计意图、垫图位置说明

### Step 6: 即梦 Dreamina CLI 视频生成

提示词输出完成后，检测用户是否已安装即梦 Dreamina CLI：

1. **检测安装状态**：运行 `which dreamina` 或 `dreamina --version` 检查是否已安装
2. **根据结果引导**：
   - **未安装**：使用 AskUserQuestion 询问用户是否要安装即梦 Dreamina CLI 来直接生成视频。如果用户同意，执行安装命令：
     ```
     curl -fsSL https://jimeng.jianying.com/cli | bash
     ```
     安装完成后，引导用户使用 CLI 生成视频。
   - **已安装**：使用 AskUserQuestion 询问用户是否要直接用即梦 CLI 生成这个视频。如果用户同意，使用 dreamina CLI 配合刚生成的提示词来生成视频。

注意：如果提示词涉及垫图，需要将用户提供的图片路径作为参数传入 CLI。
