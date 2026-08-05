# Output Format Template

## 输出格式

⚠️ 必须严格遵循此格式，不得修改符号或结构。

### 格式模板

```
🤖 AI 早报 | {YYYY.MM.DD}（{星期几}）
——————————————

{分类 emoji} {分类名称}

{序号}️⃣ {中文标题}
{中文摘要}（1-2句话，关键事实）
🔗 {来源链接}

{序号}️⃣ {中文标题}
{中文摘要}（1-2句话，关键事实）
🔗 {来源链接}

{分类 emoji} {分类名称}

{序号}️⃣ {中文标题}
{中文摘要}（1-2句话，关键事实）
🔗 {来源链接}

...（按分类组织，共 10-12 条）

——————————————
📌 一句话点评：{连接2-3条新闻的趋势观察，洞察行业动向}
```

## 分类标签
- 🧠 大模型 — 新模型发布、基准测试、技术突破
- 🤖 Agent — AI代理、自动化、工具使用
- 💰 融资/商业 — 融资、收购、商业合作
- 🛡️ 安全/治理 — AI安全、监管、伦理
- 🔧 应用/产品 — 新产品、功能更新
- 🔓 开源 — 开源模型、工具、框架

### 格式关键要求

1. **标题行**：`🤖 AI 早报 | 2026.03.18（星期三）`
   - 使用 🤖 emoji
   - 日期格式：YYYY.MM.DD
   - 括号内标注星期几

2. **分隔线**：`——————————————`
   - 使用 em dash（—），不是 box drawing（━）
   - 共 15 个 em dash

3. **分类标题**：`🧠 大模型`
   - 分类 emoji + 空格 + 分类名称
   - 独立成行，前后有空行

4. **序号 emoji**：`1️⃣ 2️⃣ 3️⃣ ... 1️⃣0️⃣ 1️⃣1️⃣ 1️⃣2️⃣`
   - 使用 emoji 数字，不是普通数字
   - 每条新闻一个序号

5. **新闻结构**：
   ```
   {序号}️⃣ {标题}
   {摘要}（1-2句话）
   🔗 {链接}
   ```
   - 标题：简洁有力，中文
   - 摘要：1-2句话，只包含关键事实
   - 链接：必须包含 🔗 emoji

6. **空行**：
   - 每条新闻之间有空行
   - 分类标题前后有空行

7. **结尾点评**：`📌 一句话点评：{内容}`
   - 使用 📌 emoji
   - 连接 2-3 条新闻的趋势观察
   - 洞察行业动向

### 完整示例

```
🤖 AI 早报 | 2026.03.18（星期三）
——————————————

🧠 大模型

1️⃣ Anthropic 发布全球首个"混合推理"AI 模型
在逻辑推理和创造性任务间实现动态切换，标志着大模型架构新突破。
🔗 https://www.theverge.com/2026/3/18/anthropic-hybrid-reasoning

2️⃣ Meta 自研 AI 模型"Avocado"延期至 5 月发布
性能未达预期需进一步优化，显示大模型研发难度持续增加。
🔗 https://techcrunch.com/2026/03/18/meta-avocado-delayed

🤖 Agent

3️⃣ Anthropic 升级 Claude 跨应用协作能力
可在 Excel 和 PowerPoint 间无缝切换处理数据，提升办公自动化水平。
🔗 https://www.anthropic.com/news/claude-cross-app

4️⃣ Nvidia 推出 NemoClaw 平台为 OpenClaw 添加安全保护
在隔离沙箱中运行自主 Agent，解决企业级隐私安全顾虑。
🔗 https://www.theverge.com/2026/3/18/nvidia-nemoclaw-security

💰 融资/商业

5️⃣ Ben Affleck 创立的 AI 公司被 Netflix 以约 6 亿美元收购
采用差异化生成式 AI 路线，Netflix 加速布局 AI 内容生产能力。
🔗 https://techcrunch.com/2026/03/18/netflix-acquires-affleck-ai

6️⃣ OpenAI 战略调整：削减"支线任务"聚焦核心业务
优先代码和企业用户，Sora、Atlas 浏览器等项目放缓开发节奏。
🔗 https://www.wired.com/story/openai-strategy-shift

🛡️ 安全/治理

7️⃣ Anthropic 与美国国防部关系引发关注
CEO Dario Amodei 就国家安全 AI 用途发表声明，强调透明度和安全原则。
🔗 https://www.wired.com/story/anthropic-defense-department

8️⃣ "战胜中国 AI 竞赛"策略带来潜在风险
专家呼吁审慎对待技术竞争，避免安全标准妥协。
🔗 https://www.wired.com/story/ai-race-risks

🔧 应用/产品

9️⃣ Databricks 推出新技术实现 AI 模型自我改进优化
模型可根据使用反馈自动调整参数，降低人工调优成本。
🔗 https://techcrunch.com/2026/03/18/databricks-self-improving-ai

🔟 Amazon Alexa Plus 新增"Sassy"个性风格
成人专属带幽默讽刺语气，为语音助手注入更多人格化特征。
🔗 https://techcrunch.com/2026/03/18/alexa-sassy-personality

🔓 开源

1️⃣1️⃣ Meta 扩展 AI 芯片家族发布 MTIA 300 芯片
用于 Instagram 和 Facebook 推荐系统训练，计划 2027 年前推出 400/450/500 系列。
🔗 https://www.theverge.com/2026/3/18/meta-mtia-300-chip

1️⃣2️⃣ Hugging Face 发布开源多模态模型 Idefics 3
支持图文混合输入，性能接近 GPT-4V，完全开源可商用。
🔗 https://huggingface.co/blog/idefics-3

——————————————
📌 一句话点评：本周大模型进入"混合推理"新阶段，Agent 跨应用协作和企业级安全成为行业焦点，开源社区持续推进多模态能力民主化。
```
