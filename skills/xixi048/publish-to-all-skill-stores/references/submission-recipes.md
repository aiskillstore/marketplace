# 提交配方

每个渠道的"提交动作"其实只有几种形状。先认清形状，再抄对应配方。

## 配方 0 · 把仓库改成"可被索引"的样子

爬取型目录站（skills.sh / SkillsMP / claude-plugins.dev）**不看你提交，只看仓库**。前置清单：

```
<repo>/
├── .claude-plugin/
│   └── marketplace.json        # 让仓库本身成为插件市场
├── skills/
│   └── <name>/
│       ├── SKILL.md            # 必须在这个路径
│       ├── references/         # 可选
│       └── scripts/            # 可选
├── LICENSE                     # MIT / Apache-2.0 / MPL-2.0
└── README.md                   # 含一行安装命令
```

`marketplace.json` 最小可用形状（取自 anthropics/skills）：

```json
{
  "name": "<repo-slug>",
  "owner": { "name": "<作者>", "url": "https://github.com/<作者>" },
  "metadata": { "description": "...", "version": "1.0.0" },
  "plugins": [
    {
      "name": "<skill-name>",
      "description": "...",
      "version": "1.0.0",
      "source": "./",
      "strict": false,
      "skills": ["./skills/<name>"]
    }
  ]
}
```

同时补上 GitHub 元数据（影响爬取与搜索排序）：

```bash
gh api -X PUT repos/<owner>/<repo>/topics -f names[]=agent-skills -f names[]=claude-skills
```

README 里写 `npx skills add <owner>/<repo>` 与 `/plugin marketplace add <owner>/<repo>`，
前者是 skills.sh 的安装入口，也是它唯一能观测到的"活跃度"来源。

## 配方 1 · 服务端拉取型 API

服务端自己 clone 仓库、跑审计、开 PR。你只需要一个能公网访问的 GitHub URL。

```bash
python scripts/submit_all.py --channel skillstore \
    --repo https://github.com/<owner>/<repo> \
    --notes-file notes.txt
```

`notes` 是给**人工审核**看的，写三件事就够了：这次改了什么、凭什么安全（零依赖/无网络/
无 eval/写入有备份）、以及在什么真实场景下验证过。

## 配方 2 · multipart 快速提交

少数渠道要文件本体而不只是 URL：

```bash
python scripts/submit_all.py --channel skillbay \
    --skill-md skills/<name>/SKILL.md --name <联系人> --email <邮箱>
```

这类渠道常要求 **before/after 实证**（同一 prompt：没装技能的回答 vs 装了的回答）。
提前准备好，没有实证的付费 listing 基本过不了审。

## 配方 3 · GitHub PR 型

```bash
# 1. fork（用 API 或 gh）
gh repo fork <owner>/<repo> --clone=false
# 2. 本地加文件，按对方 CONTRIBUTING 的路径
# 3. push 到 fork，然后开 PR（head 写 <me>:<branch>）
gh pr create --repo <owner>/<repo> --head <me>:main --title ... --body ...
```

细节：

- 先读 `CONTRIBUTING.md`，它决定的不是格式而是**能不能被合并**
- 先看 `pull_request_creation_policy`：`collaborators_only` 的仓库外部开不了 PR，直接跳过
- PR 正文按对方模板写（Component Details / Testing），比长篇自我介绍有用

## 配方 4 · 登录式 CLI

浏览器里登录过 ≠ CLI 登录过，两套凭据。先探登录态，没登录就走 device-code：

```bash
npx -y clawhub@latest whoami          # 未登录会提示 clawhub login
(nohup npx -y clawhub@latest login >/tmp/clawlogin.log 2>&1 &); sleep 12
cat /tmp/clawlogin.log                # 拿到 https://clawhub.ai/cli/device?user_code=XXXX-XXXX
# 把这个 URL 丢给用户浏览器确认，**别 kill 进程**，确认后日志会出现 Authorized

npx -y clawhub@latest skill publish skills/<name>     --slug <slug> --name "<名称>" --version 1.2.0     --tags "a,b,c" --changelog "..."     --source-repo https://github.com/<owner>/<repo>     --source-commit $(git rev-parse HEAD) --source-ref main --source-path skills/<name>     --dry-run          # 先看 Would publish <slug>@<version>
```

发布成功返回 `pending security scans`，**不是**“已上架”。

```bash
npm i -g @tankpkg/cli && tank login && tank init && tank scan && tank publish --dry-run
# 2026-10 实测：tank login 报 Failed to start auth session: Invalid request body（CLI/服务端版本不匹配）
```

没登录态就不要硬试。**明确告诉用户这一步需要他登录**，比自己造一个 token 强。

## 配方 4.5 · 有「从 GitHub 导入」就不要本地上传

腾讯 SkillHub、部分国内 Skill 广场、agentskill.sh 都提供「从 GitHub 导入」。
优先选它，理由不是省事，而是**单一真源**：平台直接读 `<owner>/<repo>/skills/<name>/`，
以后 push 就是更新，永远不会出现"商店版本落后于仓库"。

实操（腾讯 SkillHub，实测）：

1. `发布 Skill` → 选「发布 Skill」（最快上架），不要选 `发布 Pay Skill`（需支付改造）
2. 类型页切到 **「从 GitHub 导入」** 标签（默认是「本地上传」）
3. 绑定过 GitHub 后，它会自动列出你仓库里所有 `skills/<name>/`，勾选要发布的
4. 「下一步：确认信息」→ 核对 slug / 显示名 / 版本号 / 描述 → 点「发布 (1)」
5. 落在 `/dashboard`「我的 Skills」，状态 `安全审核中`

注意：点首页的「发布 Skill」按钮可能先跳 `/dashboard/verify`（实名+人脸）；
直接进 `/dashboard/publish` 可以绕开那个引导页。
实名认证与绑定 GitHub 必须用户本人做，不要代填身份信息。

## 配方 6 · 讯飞 Astron SkillHub（skill.xfyun.cn）

真注册中心，走「上传 ZIP → 建草稿 → 质量评测 → 发布」四步，产出正式版本号（形如 `v20261025.230752`）。

1. 登录：`passport.xfyun.cn`（微信扫码 / 手机号 / 密码），未登录时 `/publish` 直接 404
2. 正确入口是 **`/dashboard/publish`**（导航里的「发布」也是它）；`/publish` 是 404
3. 上传 zip（`build_package.py` 打的 skillroot 包，≤5 MB 级别没问题），选 **命名空间**（个人号只有 `Global (@global)`）
4. 「创建草稿并继续」→ 步骤 1 填 **简介（中文）** → 保存 → 「继续质量评测」
5. 步骤 2 用默认 Auto 快速评测（发布后异步跑，不阻断）→ 「继续发布」
6. 步骤 3 点「发布」→ 状态变 `ACTIVE · 审核中`，后台「我的技能」可见

坑：
- 命名空间下拉是异步渲染的，`click()` 之后要**另一次调用**再点 `[role=option]`，否则选不上、建草稿按钮无效
- 「继续质量评测 / 继续发布」按钮点完页面不跳转时，先点一次「保存」再点
- 简介字段是 `#candidate-summary`，是 React 受控组件，要用原生 value setter + `input` 事件写入

## 配方 5 · 把网页表单当 SPA 逆向（找不到接口时）

1. `curl` 提交页，grep 静态 `<form>` → 拿到 multipart 字段名
2. 试 `/openapi.json`、`/api/docs` → 拿到完整协议（skillbay.sh 就是这么拿到的，115 KB OpenAPI）
3. 框架线索：SvelteKit 看 `__sveltekit_*` 与 `_app/immutable/entry/app.js` 里的
   `import("../nodes/N.*.js")` 路由映射；Next.js 看 `_next/static/chunks`
4. 在 chunk 里 grep `/api/`，打印每个命中位置前后 900 字符 → 请求体结构全暴露

挖到的接口立刻写成注册表条目（`scripts/submit_all.py` 的 `CHANNELS`），下次直接用。

## 本机网络坑（Windows / 中国网络环境）

- 全局 git 配置里常有 `url.https://ghfast.top/https://github.com/.insteadof`，
  于是 `git remote -v` 永远显示镜像地址，`git push` 也会走镜像。
  镜像通常只读，会报 `Password authentication is not supported`。
- 直连 `github.com` 可能被 reset，所以正确解法是**走镜像 + 自带认证头**：

```bash
TOK=$(gh auth token)
B64=$(printf 'x-access-token:%s' "$TOK" | base64 -w0)
git -c credential.helper='' \
    -c http.extraheader="Authorization: Basic $B64" \
    push https://ghfast.top/https://github.com/<owner>/<repo>.git main
```

- 提交商店时永远用**原始** `https://github.com/<owner>/<repo>`，镜像地址他人拉不到。
- Git Bash 的 `/tmp` 与 Windows 的 `C:\tmp` 不是同一个目录；临时文件统一写到固定目录。
