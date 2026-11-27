# 关系决策 skill（relationship-guide）

让 AI 助手照《高性价比关系指南》回答具体问题：这句话怎么说、架怎么吵、该不该道歉、怎么拒绝、一段关系有没有到红线。

它做的事只有一件：**先把相关条目从正文里查出来，再照书的排序方式回答**，每条注明出自第几章第几条。查不到就说查不到，不凭记忆编数字。规则全在 [SKILL.md](SKILL.md)。

## 装到 Claude Code

在本仓库里开 Claude Code，不用装——`.claude/skills/relationship-guide/` 已带副本。

想在任何目录下都能用，装到个人 skill 目录：

```bash
mkdir -p ~/.claude/skills/relationship-guide
curl -fsSL -o ~/.claude/skills/relationship-guide/SKILL.md "https://raw.githubusercontent.com/yuzhang-zhong/HowToGetAlong/main/skills/relationship-guide/SKILL.md"
```

之后直接问「朋友借钱不还怎么开口」「吵架吵到失控怎么办」就会触发；也可以显式说「用 relationship-guide 回答」。

## 装到 Codex

装到 Codex 的个人 skill 目录 `~/.agents/skills`：

```bash
mkdir -p ~/.agents/skills/relationship-guide
curl -fsSL -o ~/.agents/skills/relationship-guide/SKILL.md "https://raw.githubusercontent.com/yuzhang-zhong/HowToGetAlong/main/skills/relationship-guide/SKILL.md"
```

之后直接问问题就会按描述自动触发，也可以输入 `$relationship-guide` 显式调用（注意是 `$` 不是 `/`）。没出现就重启一次 Codex。

## 装到对话式助手（Muse 等）

没有文件工具的助手可以按「知识库 + 系统提示词」两层装：

1. **知识库**：把 `book/` 下的章节文件作为知识源/附件传给助手（支持上传文档的都行；只传某一章也能用，skill 会说明只读到了哪部分）。
2. **规则**：把 [SKILL.md](SKILL.md) 的全文粘贴到助手的系统提示词 / 角色设定 / 自定义指令里。

装好后问「用书里的条目回答：同事总甩锅给我，怎么开口」。如果助手连文档都不支持，可直接把[纯提示词精选版](PROMPT-ONLY.md)粘贴进系统提示词；它包含 30 条常用建议及第 4、16 章的全部安全条目。

## 正文从哪来

- 有本仓库（或本地克隆）：读 `book/`。
- 没有且环境有 shell：`git clone --depth 1 https://github.com/yuzhang-zhong/HowToGetAlong.git`，整本很小，几秒。
- 纯对话：用户上传。都取不到就如实说取不到。

## 改动须知

规则改 `skills/relationship-guide/SKILL.md`（正本），`.claude/skills/` 下是副本，**两边要同步**（用符号链接可免同步，但 Windows 克隆需开发者模式）。SKILL.md 里不留会跟着正文漂的清单：章的清单去读根 README 的「这本书想回答的问题」表，条目格式去读 `docs/写作规范.md`。增删章、改分级规则都不用动 skill。

`PROMPT-ONLY.md` 由 `node tools/build-prompt-only.mjs` 从正文生成。修改精选条目清单时改脚本里的 `CORE`，安全章自动整章收录；不要手改生成文件。
