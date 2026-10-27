# ChatGPT GPT 配置

在 ChatGPT 的 “Explore GPTs → Create” 里切到 Configure 页，按下表填。创建 GPT 需要付费账号，免费用户可以使用别人分享的 GPT。

| 字段 | 填什么 |
|---|---|
| Name | 简历事实守卫 Resume Claim Guard |
| Description | 发我岗位 JD，我先问你做过什么，再写一份面试官追问也答得上来的简历。不替你编任何经历。 |
| Instructions | [PROMPT.md](../PROMPT.md) 代码块里的全文，原样粘贴 |
| Conversation starters | 这是我想投的岗位，帮我准备简历 / 我只有一份简历，帮我看看哪里经不起追问 / 这是 AI 改过的简历，和原版比哪里写过头了 |
| Knowledge | 可选：上传 [SKILL.md](../SKILL.md) 和 `references/` 里的文件，作为细则参考 |
| Capabilities | 关掉 Web Search、Image Generation；Code Interpreter 可开（读 PDF 用） |
| 分享 | 先 Only me 跑完 [测试单](../tests/web-chat.md)，通过后改为 Anyone with the link |

改了 `PROMPT.md` 之后，记得同步更新 Instructions。
