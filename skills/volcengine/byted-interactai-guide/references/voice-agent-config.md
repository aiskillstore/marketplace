# Voice Agent 配置路由

**Domain**: voice-agent

`{AgentConfig,Config}` 核心配置统一以 StartVoiceChat 文档为准。AibotCreate 和 AibotUpdate
分别把核心配置映射为持久智能体的创建结构和更新 patch。配置生成与字段验证按以下 references
执行：

1. 读取 `references/voice-agent-config-model.md`，把自然语言意图规范化为核心配置。
2. 涉及范围、枚举、新字段、Provider/Model/Resource/voice 兼容性等动态事实时，读取
   `references/voice-agent-config-validation.md` 并核对当前官方正文。
3. 读取 `references/voice-agent-config-output.md`，生成目标结构、最小 patch 和统一 envelope。

先确定用户想改变的效果和 target。target 决定输出投影：一次性请求使用 `start-voice-chat`；
创建或命名新智能体使用 `aibot-create`；修改现有智能体使用 `aibot-update`。三者的核心字段都
按当前 StartVoiceChat 正文生成和验证。确实无法唯一确定语义时只返回一个最小澄清问题。

Skill 中的旧范围、枚举或兼容表不构成拒绝依据。结构无法解析时可立即失败；动态事实证据不足时
返回 `valid=null`。动态限制的确定结论必须来自匹配当前产品、接口和 API 版本的官方正文或
服务端响应。
