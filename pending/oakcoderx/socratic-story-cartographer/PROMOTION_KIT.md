# Socratic Story Cartographer — Promotion Kit

Repository:
https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer

Install:
```bash
npx skills add https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer
```

## Core one-liner

A portable Agent Skill for novels, screenplays and series outlines that attacks its own first diagnosis with competing hypotheses, falsification and counterfactual tests before recommending the minimum-sufficient revision.

---

## 1. Registry submission — dmgrok Agent Skills Directory

**Title**
`[New Source] Socratic Story Cartographer`

**Repository URL**
`https://github.com/OakcoderX/awesome-agent-skills`

**Provider Name**
`Socratic Story Cartographer`

**Provider ID**
`socratic-story-cartographer`

**Skills location**
`socratic-story-cartographer/`

**Default branch**
`main`

**Why include it**

Socratic Story Cartographer is a portable story-development Agent Skill for novels, screenplays, scenes and multi-episode outlines. Unlike a conventional critique prompt, it keeps competing diagnoses alive, attacks the strongest diagnosis with falsification and counterfactual tests, anchors root-level claims to textual evidence, predicts regression risk, and stops when another loop no longer changes the working belief. Version 2.2 adds long-work evidence coverage and producer-facing outline review; the repository also publishes the v2.1 diagnostic benchmark and its limitations.

**Category focus**
Creative / Writing, Productivity, AI Workflow

**Quality checklist**
- Public repository
- MIT license
- Standard SKILL.md frontmatter
- No secrets or external runtime requirements
- Benchmark and first-test documentation included
- Active development in August 2026

---

## 2. Claude Skills Directory / generic registry summary

**ID**
`socratic-story-cartographer`

**Summary (<=180 chars)**
Story-development skill that falsifies its own diagnoses before proposing minimal revisions for novels, screenplays, scenes and series outlines.

**Verticals**
Writing / Productivity / AI Workflow

**Primary link**
`https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

---

## 3. r/claudeskills — Skill Share

**Title**
`I built a story skill that has to attack its own first diagnosis before editing`

**Post**

I kept running into the same problem with AI story feedback: the model makes one plausible diagnosis, then spends the rest of the conversation confidently optimizing around it.

So I turned my own fiction/script review loop into a portable Agent Skill. It keeps 2–3 competing diagnoses, requires falsification + a counterfactual test, anchors root-level claims to actual text, predicts what a fix could destroy, and stops if another loop no longer changes its belief.

I tested the design on literary fiction, a 26-episode series outline and an episode screenplay; the benchmark and its limitations are public in the repo. I’m more interested in failure cases than stars — if you have a story or script where AI critique keeps going in circles, I’d like to know where this one breaks.

Install:
`npx skills add https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

Repo:
`https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

---

## 4. r/ClaudeCode — evaluation / workflow framing

**Title**
`I benchmarked three SKILL.md designs for story diagnosis; the useful part was forcing belief updates`

**Post**

This started as a question about prompt design rather than creative writing: what happens if a skill is not allowed to protect its first diagnosis?

I tested three versions of a story-analysis SKILL.md on three different objects (literary fiction, a season outline, and an episode screenplay) with three semantically equivalent prompt variants. The final design forces concrete evidence anchors, competing diagnoses, falsification/counterfactual tests, regression checks and a “loop delta”: if another loop produces no meaningful belief update, it stops.

The experiment is same-model and not a statistical trial; I’ve published the methodology and limitations. The practical difference I cared about was prompt sensitivity and whether the skill could distinguish a root cause from a symptom.

Repo / benchmark:
`https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

Install:
`npx skills add https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

I’d be especially interested in people who already maintain their own evals for SKILL.md / AGENTS.md behavior.

---

## 5. Hacker News — Show HN

**Title**
`Show HN: Socratic Story Cartographer – a SKILL.md that falsifies its own story diagnosis`

**Post**

I write fiction/scripts and kept finding that LLM critique had a specific failure mode: once the model made a plausible first diagnosis, later turns often became elaborations of that diagnosis rather than real updates.

I made a portable Agent Skill that treats story review as a small belief-update loop: observe → competing diagnoses → falsification/counterfactual → highest-leverage intervention → blind re-check → update/stop.

The current v2.2 keeps the v2.1 evidence-anchor and loop-delta rules, so a requested “3 loops” is a maximum, not an excuse to manufacture three different opinions. It also verifies coverage before making long-work claims and compiles full-season findings into producer decisions and revision task cards. The structured same-model benchmark for the diagnostic kernel and its limitations are in the repo.

It’s just SKILL.md + documentation, no service or account required:
`npx skills add https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

Repo:
`https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

I’d value adversarial examples where the loop still converges on the wrong diagnosis.

---

## 6. V2EX — 中文技术版

**标题**
`做了一个给小说/剧本用的 Agent Skill：先反驳自己的判断，再给修改意见`

**正文**

我一直觉得 AI 做故事分析最大的毛病不是“不会提意见”，而是第一判断一旦错了，后面几轮经常只是围绕这个错误判断越说越完整。

所以把自己开发小说、剧本时的一套方法做成了一个通用 Agent Skill：先保留 2–3 个竞争诊断，再做证伪和反事实测试；重要判断必须给文本证据；修改前要检查会不会把原本成立的留白、人物复杂度或节奏一起修掉；如果下一轮没有 belief update，就提前停止。

支持 Claude Code、Codex、Cursor 等兼容 Agent Skills 的 Harness：
`npx skills add https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

我拿小说、26 集季纲和第一集剧本做过一个 27-condition 的对比测试，方法和局限都公开了。更想找真实失败案例：如果你正好拿 AI 做剧本/小说开发，可以拿自己的文本跑一次看看。

Repo：
`https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

---

## 7. X / Twitter — short launch post

AI story feedback has a failure mode I kept hitting: once the model makes a plausible first diagnosis, later turns often just optimize around it.

So I built Socratic Story Cartographer: competing diagnoses → falsification → counterfactual → minimum-sufficient revision → blind re-check. If the belief does not change, the loop stops.

Install:
`npx skills add https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

Benchmark + repo:
`https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

---

## 8. r/WritingWithAI — creator-first

**Title**
`I wanted AI to challenge its own editing advice, so I turned that into a reusable story skill`

**Post**

When I use AI as an editor, the frustrating part is not bad prose suggestions. It is a convincing *wrong diagnosis* that shapes every later revision.

I built a reusable Agent Skill around a different workflow: keep competing explanations alive, try to falsify the strongest one, run a counterfactual test, protect qualities that are already working, and only then suggest the smallest useful change. If the next round produces no real change in the diagnosis, it stops instead of inventing more notes.

It works on fiction, screenplays and outlines. I’m looking for people willing to test it on their own work and tell me when the diagnosis is wrong — that feedback is more useful to me than stars.

`npx skills add https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

Repo / 3-minute test:
`https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

---

## 9. 即刻 / 中文短帖

给 AI 装了一个“会反驳自己的故事编辑”。

我发现 AI 改小说/剧本最危险的不是没意见，而是第一判断错了以后，后面几轮都在给这个错误判断补论据。所以做了 Socratic Story Cartographer：竞争诊断 → 证伪 → 反事实 → 最小修改 → 回归检查；没有新的 belief update 就停。

小说、剧本、季纲都能用，Agent Skills 兼容的 Harness 基本都能装：
`npx skills add https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

Repo 里把 benchmark 和局限也公开了。想找真正拿自己文本来跑的人，最好告诉我它哪里判断错了。

---

## 10. 知乎 / 长文章定位

**建议标题**
`为什么我不再问 AI“这篇小说写得好吗”，而是让它先反驳自己的判断`

**文章结构**
1. 从苏格拉底“助产士”与 AI 未知答案的差别讲起。
2. AI 文学批评的核心失败：第一诊断锁定后形成 confirmation loop。
3. 从“能不能投《纽约客》”改造成开放式问题架构。
4. Socratic Story Cartographer 的核心：compete → falsify → counterfactual → minimal intervention → blind re-check。
5. 《菠萝鸡》《死亡剧本》季纲、第一集的对比测试设计，而不是只报分数。
6. 为什么 Evidence Anchor 和 Loop Delta 是 v2.1 最重要的两条。
7. 局限：同模型测试、文学没有 gold standard、仍需 out-of-sample 人类盲评。
8. 最后给安装命令和 3-minute test。

---

## 11. LinkedIn — professional / production framing

I’ve been experimenting with a question that matters more to me than “can AI write a story?”: **can AI diagnose a story without becoming trapped by its first plausible explanation?**

I turned that workflow into an open Agent Skill, Socratic Story Cartographer. It keeps competing diagnoses alive, requires evidence anchors, attacks the leading diagnosis with falsification and counterfactual tests, predicts regression risk, and stops when another loop no longer changes the working belief.

I tested the specification on literary fiction, a 26-episode series outline, and an episode screenplay. The comparison is not presented as a statistical benchmark — the methodology and limitations are public so other creators and producers can reproduce it on their own material.

Install:
`npx skills add https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

Repo / methodology:
`https://github.com/OakcoderX/awesome-agent-skills/tree/main/socratic-story-cartographer`

I’m looking for real failure cases, especially from writers, editors and producers already using AI in development rather than just generation.

---

## Channels intentionally not used

- r/writing — current rules prohibit generative-AI promotion/use.
- r/selfpublish — current rules prohibit AI posts and restrict self-promotion.
- r/Writers — possible, but lower priority because it is broad and self-promotion-sensitive.
- Multiple near-identical Reddit posts in a short period — avoid spam and learn from one audience before posting to the next.
