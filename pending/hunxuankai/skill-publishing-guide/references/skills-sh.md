# skills.sh：安装来源与发现

核验：2026-11-07，一手 FAQ 和 Vercel skills CLI 文档。

## 发布方式

官方 FAQ 说明：用户通过 `npx skills add OWNER/REPO` 安装时的匿名遥测，会让技能出现在榜单。没有核实到“必须开 GitHub issue”或“上传 ZIP 到榜单”的要求。GitHub push、CLI 可安装、网站收录和网页内容已刷新分别核验。

本次只问方法或准备材料时，不运行安装来触发收录。明确授权该渠道发布后，可在新的隔离位置完成一次真实安装/核验。沿用已有遥测选择，不擅改禁用设置，也不通过重复安装刷计数。

## 来源与选择

先检查官方 CLI 当前帮助和项目结构。已核验的命令形状：

```text
npx skills add OWNER/REPO --list
npx skills add OWNER/REPO@REF --skill SKILL_NAME
```

多技能仓库显式选择本次 skill，核对实际安装目标，使用隔离位置避免覆盖现有副本。CLI 当前还支持 GitHub tree URL、git/local 来源及直接 SKILL.md/归档下载 URL；这些是**安装能力**，不证明每一种来源都能进入 skills.sh 榜单。

官方发现规则支持仓库根 SKILL.md、skills/、.agents/skills/、.claude/skills/ 等容器和分类路径，也支持 `skills.sh.json`。不要把 `skills/<name>/SKILL.md` 写成唯一路径。

GitHub 私有仓库可能可通过凭据安装，但这不能证明公共目录可见。Packs 的 Vercel 登录与包管理流程是另一项功能，不是普通榜单收录的必要步骤。

## 核验和更新

记录安装入口、选择的名称、解析到的 ref/提交、版本和文件哈希；再核对网页条目。若安装内容已更新而网页仍是旧快照，分别报告，不承诺固定刷新时间。源仓库新版、旧安装副本和网页快照可能暂时不同步。

更新保持项目既有版本/来源管理方式。`npx skills update` 更新使用者的安装副本，不等于作者已经向所有市场发布。未执行真实安装时说明该项未验证。

来源：[官方 FAQ](https://skills.sh/docs/faq)、[CLI 文档](https://skills.sh/docs/cli)、[完整命令](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)、[发现规则](https://github.com/vercel-labs/skills/blob/main/docs/creating-skills.md)。
