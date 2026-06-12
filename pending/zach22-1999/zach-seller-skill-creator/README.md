# zach-seller-skill-creator

> **作者**：Zach ｜ 公众号「Zach的进化笔记」
>
> Learn in public！把亚马逊卖家的实战流程做成可安装、可评测、可迭代的 AI skill。

中文版卖家 Skill 创建器，基于 Anthropic 官方 `skill-creator` 的思路重构，面向亚马逊运营、自媒体和日常工作流场景。

## 推荐安装方式：让 AI 帮你装

推荐在以下 IDE 中直接用自然语言安装：

- Claude Code
- Codex
- Cursor

把下面这句话直接发给你的 AI：

```text
帮我安装 `zach-seller-skill-creator` 这个 skill，来源仓库是 `amazon-skills`。直接装到当前工作区，并把依赖一起检查好。
```

手动安装仍然保留，但只作为降级方案：
[../../docs/manual-install.md](../../docs/manual-install.md)

## 它解决什么问题

很多卖家想把自己的经验沉淀成 skill，但一开始只能说出“帮我做关键词分析”“帮我自动化广告优化”这类很宽的需求。结果写出来的 skill 往往像说明书，缺少真实业务判断。

这个 Skill 在写 `SKILL.md` 之前，先用 6 个问题把业务上下文问清楚：

1. 业务目标是什么
2. 过去人工怎么做
3. 具体步骤怎么走
4. 背后方法论是什么
5. 用户以后会怎么调用
6. 期望输出长什么样

只有这些答案足够具体，才进入 skill 草稿、测试用例、评测、打分和迭代。

## 核心能力

- 用中文引导卖家把模糊需求拆成可执行工作流
- 自动把 6 问结果映射到 `SKILL.md` 的关键段落
- 生成 2-3 个真实用户提示词作为测试用例
- 支持 with-skill 与 baseline 对照评测
- 聚合 benchmark，并生成 HTML 可视化评审页
- 根据评审反馈迭代优化 skill

## 使用方法

直接对 AI 说：

```text
我想做一个专门检查 Listing 差评机会点的 skill，你用 zach-seller-skill-creator 帮我一步步梳理。
```

或者使用 skill 命令：

```text
/zach-seller-skill-creator
```

## 文件结构

- `SKILL.md`：主流程与执行规则
- `references/`：6 问流程、模板、schema 和 skill 写作指南
- `agents/`：分析、对比、评分子任务提示
- `scripts/`：校验、评测、打包和报告脚本
- `eval-viewer/`：HTML 评审页生成器

## 前置条件

- Python 3.10+
- 使用评测脚本时，需要当前 IDE/agent 支持本地命令执行

## 如果安装或运行出错，直接让 AI 帮你排查

把下面这段直接发给你的 AI，并把报错信息、截图或终端输出一起贴上：

```text
我已经安装了 `zach-seller-skill-creator`，但现在遇到了问题。请你直接帮我排查并尽量修复：

1. 先判断是 skill 文件缺失、依赖缺失、路径错误，还是当前 IDE 没有正确加载
2. 自动检查当前工作区里和 `zach-seller-skill-creator` 相关的文件、配置、脚本和依赖
3. 如果可以自动修复，就直接修复
4. 修复后告诉我还需要重启 IDE、重新加载工作区，还是重新运行哪个命令
5. 最后给我一个最短的验证步骤，确认这个 skill 已经能用了
```

## 关于作者

关注「**Zach的进化笔记**」，获取 AI x 跨境电商的实战经验、工具和方法论：

<img src="../../assets/traffic/wechat-official-account.jpg" width="200" alt="公众号二维码" />

扫码加入交流群，一起交流 AI + 跨境电商的实战玩法：

<img src="../../assets/traffic/wechat-group.jpeg" width="200" alt="交流群二维码" />
