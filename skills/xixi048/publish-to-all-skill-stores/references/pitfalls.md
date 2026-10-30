# 踩坑清单

每条都是真实发生过的。按"症状 → 原因 → 正确做法"记，便于下次 10 秒内认出来。

## 收录相关

**提交了却永远搜不到**
原因：技能在仓库根目录 `{name}/SKILL.md`，不是 `skills/<name>/SKILL.md`。
爬虫只认后一种，而且**不报错**——它只是安静地不收录。
做法：迁移到 `skills/<name>/`，同步改 README 里所有相对路径，然后重新提交。
> 曾经有过一次反向结论（"`{name}/` 也命中扫描路径"），是错的。以
> `anthropics/skills` 的实际布局与 skills.sh 官方文档为准：`skills/<name>/`。

**SkillsMP 一直收不到**
原因：它要求仓库 **≥2 stars** 才抓。0 star 的新仓库进不去。
做法：先在 skillstore / skills.sh 拿到曝光，再等；不要把"没被收录"当成接口问题。

**skills.sh 排行榜上没动静**
原因：它用**匿名安装量**排序，不是看提交。
做法：README 写清 `npx skills add <owner>/<repo>`，让人真的安装一次，telemetry 就会播种。

## 提交接口相关

**skillstore.io 返回 409**
原因：同一仓库 **1 小时内重复提交**被限流。
做法：等窗口过去再提；或把 `notes` 写清"上次提交针对旧路径"，让审核知道是改版不是刷量。

**skillsmd.dev 返回 `404 GitHub repo not found`**
原因：它的索引没跟上新建/刚改名的仓库，或它按 stars 过滤。
做法：过一阵重试；不要反复打同一个接口。

**skillbay 快速提交成功，但设不了价**
原因：快速提交只登记"作者想要上架"，`price` 字段在 seller listing 接口上，
必须有 seller 账号 + Stripe onboarding。
做法：先用快速提交占位，把 `SkillForm` 全字段（含 `examples`）备好，等邀请到位再发。

**`notify_via_github: true` 之后提交卡住**
原因：它会弹 GitHub 登录框，纯脚本流程断在这里。
做法：一律传 `false`。

**agentskill.sh 找不到提交接口**
原因：`/submit` 是 SPA，走服务端 action，没有可直接 POST 的公开端点（探过
`/api/submit`、`/api/skills/analyze`、`/openapi.json`，均无）。
做法：当表单渠道处理，交给用户点；别在它身上耗时间。

## 宿主 / 工具相关

**`publish_skill` 报 `INVALID_PARAMS`（cindy_helper）**
原因：带 `display_name` / `summary` / `tags` 时被判参数不合法；
**只传 `path` + `name` + `mode` + `visibility` 才能过**。
做法：先最简参数创建成功，再用 `mode: "update"` 补 `changelog`；要改展示名就先确认服务端是否接受。

**`publish_skill` 报 `NAME_TAKEN`，而且无法自救**
原因：先做过一次 `visibility: "private"` 的测试上传，名称被自己占住了；
update **不能**改 visibility（"Updates preserve visibility, ownership and tags"）。
做法：**create 之前就想清楚 visibility**（要公开就一次到位）。
已占名时只能去 Skills 页删除那条私有记录，再重新 create。

**以为已经在浏览器登录了，CLI 还是说 Not logged in**
原因：浏览器里的登录态和 CLI 的 token 是两套。ClawHub / Tank / skilld 都有自己的 device-code 流程。
做法：`clawhub login` 会打印一行 URL（带 `user_code`），**直接把这个 URL 丢给浏览器打开**让用户确认，
然后把进程留在后台等（别 kill，kill 掉这次码就废了）：

```bash
(nohup npx -y clawhub@latest login >/tmp/clawlogin.log 2>&1 &); sleep 12; cat /tmp/clawlogin.log
# → https://clawhub.ai/cli/device?user_code=XXXX-XXXX
```

**`clawhub skill publish` 报 `--source-repo and --source-commit must be provided together`**
原因：想声明来源仓库就必须同时给 commit，只给 repo 不行。
做法：`--source-commit $(git rev-parse HEAD)`；先 `--dry-run` 看 `Would publish <slug>@<version>` 再真发。
发布成功返回的不是“已上架”，而是 `pending security scans`。

**`tank login` 报 `Failed to start auth session: Invalid request body`**
原因：CLI（v0.16.5）与 registry 的 auth 接口版本不匹配，不是用户操作问题。
做法：记下来当“当前不可用处理”，别反复试；等官方修或改走网页端。

**想删掉自己发错的 SkillHub 发布，但找不到接口**
原因：宿主 SkillHub 的工具只有 `search_skills` / `list_my_published_skills` / `publish_skill` /
`get_skill_publish_status` / `start_skill_learning`，**没有删除**。
做法：明确告诉用户到“技能”页手动删；不要承诺自己能删，也不要为绕开它去换名字重发
（会造成两条同名不同 slug 的重复记录）。

**上传被拒，但报错只给 "upload did not complete"**
原因：目录里有 `__pycache__/*.pyc` 之类的垃圾文件。
做法：打包/上传前 `find . -name __pycache__ -prune -exec rm -rf {} +`。

## 仓库与 git 相关

**`git push` 报 `Password authentication is not supported`**
原因：全局 `url.https://ghfast.top/https://github.com/.insteadof` 把 github.com 改写成镜像，
而镜像地址没有可用凭据；直连 github.com 又被网络重置。
做法：走镜像 + 显式认证头：

```bash
TOK=$(gh auth token); B64=$(printf 'x-access-token:%s' "$TOK" | base64 -w0)
git -c credential.helper='' -c http.extraheader="Authorization: Basic $B64" \
    push https://ghfast.top/https://github.com/<owner>/<repo>.git main
```

**`preflight.py` 误报"缺少 LICENSE"**
原因：它用 `skill_dir.parent` 当仓库根；改成 `skills/<name>/` 布局后 parent 是 `skills/`。
做法：已修——向上找 `.git`，再退化为找 `LICENSE` / `README.md`。

**PR 打不开**
原因：目标仓库 `pull_request_creation_policy` 是 `collaborators_only`。
做法：先查这条策略，别写完文件才发现开不了 PR。

## 文案相关

**简介里写了会变的固定数量，后来数据一扩就对不上了**
典型：`762 feeling words / 598 styles`、`3000+ entries`、`supports 50 formats`。
这些数字是**当前快照**，词库 / 数据集 / 规则一扩就失真，而文案已经散落在十几处
（README、`package.json`、`server.json`、SKILL.md frontmatter、marketplace.json、各商店后台），
改一次要全链路同步，而且必然漏。

做法：对外只写**能力与作用**，不写数量。「Turn one sentence into the closest visual style
(backed by an art-reference chart)」比「598 styles」信息量更大，也不会过期。
确实需要精确数字时放进详情页的**数据说明**，并标注统计时间。

已经写进多个渠道时：先改仓库（一处），再发新版本让元数据同步；没有自助编辑入口的商店
（mcpservers.org 一类）只能等审核通过后改或重新提交。
**这就是为什么这条必须在第一次提交前定死。**

## 流程相关

- **先修仓库再提交**。布局/许可证错的时候提交，等于把一次审核机会烧掉。
- **每次提交都留回执**（submission id / PR 号 / 版本号）。没有回执的人工确认不算完成。
- **别轮询审核状态**。pending 就是 pending，反复查询只会让结果看起来更不确定。
- 交付时必须把「已提交 / 待登录 / 需移植 / 已排除」分开写，
  否则用户会以为"全量推送"= 全部上线了。
