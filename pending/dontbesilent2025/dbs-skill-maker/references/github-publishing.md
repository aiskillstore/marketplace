# GitHub 可选发布

只有用户明确要求发布、分享、创建 GitHub 仓库或生成 `npx skills add` 安装命令时读取本文件。

本地 Skill 已经完成时，可以提醒一次发布能力。用户未选择发布时，不创建 GitHub 配置、README、仓库、commit、tag 或 Release。

## 发布前需要确定

优先从上下文和当前 Git 状态取得：

- 使用现有仓库还是创建新仓库；
- 仓库所有者与名称；
- 公开或私有；
- 默认分支；
- 是否只提交当前 Skill；
- 是否需要版本 tag 或 GitHub Release。

只有缺少的信息会改变远端目标、公开范围或版本策略时才问 1 个问题。

## 授权边界

“帮我准备发布”只覆盖本地仓库准备和校验。“发布到 GitHub”“创建仓库并推送”等明确表达可以覆盖对应远端动作。授权不清楚时，在 push、tag 或 Release 前停止并说明将发生什么。

不得自动发布用户未审查的私密样本、测试答案、运行记录、密钥、内部路径和本机配置。

## 单 Skill 仓库结构

默认准备：

```text
repository/
├── README.md
└── skills/
    └── skill-name/
        ├── SKILL.md
        ├── agents/          存在时复制
        ├── references/      存在时复制
        ├── scripts/         存在时复制
        └── assets/          存在时复制
```

`evals/`、缓存、临时文件和本机隐藏文件默认排除。公开测试确有用户价值时，先脱敏并让用户确认具体文件。

可以使用：

```bash
python3 scripts/prepare_github_repo.py <skill-directory> <staging-directory> --owner <owner> --repo <repo>
```

脚本校验 owner 和 repo 格式，逐项比较打包前后文件，并从 `description`、`agents/openai.yaml` 和实际脚本生成 README 的用途、使用示例与依赖。它只准备本地 staging 目录，不创建远端仓库，也不 push。

## README 最小内容

- Skill 解决的问题；
- 适用条件和主要边界；
- 安装命令；
- 最短使用示例；
- 实际需要的工具或环境依赖；
- 隐私或权限说明，确有需要时加入。

单 Skill 仓库默认安装命令：

```bash
npx -y skills add <owner>/<repo> -g --all
```

## 发布门禁

发布前检查：

1. 运行 Skill 结构校验与脚本测试；
2. 检查 Git diff、未跟踪文件和暂存区；
3. 检查密钥、个人路径、私密材料和 `evals/`；
4. 只使用明确路径暂存，禁止 `git add .` 和 `git add -A`；
5. commit 信息指向实际用户收益；
6. push 前再次确认仓库、分支和提交范围；
7. tag 或 Release 只在用户要求时创建。

发现删除、覆盖、远端分叉、已有 tag、疑似密钥或额外暂存文件时停止，将异常合并说明。

## 安装验证

README 中存在命令只能证明说明已生成。发布后需要在隔离环境运行：

```bash
bash scripts/verify_npx_install.sh <owner>/<repo> <skill-name> <source-skill-directory>
```

验证至少包括：

- `npx skills add` 能发现并安装仓库中的 Skill；
- 安装目录存在 `SKILL.md`；
- frontmatter `name` 与预期一致；
- `SKILL.md`、agents、references、scripts 和 assets 与源目录逐文件一致。

网络、GitHub 权限或安装器故障时保留本地 Skill，报告失败发生在哪一步，不反复创建仓库或重复 push。
