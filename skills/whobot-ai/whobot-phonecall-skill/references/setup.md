# 安装、自检与排障

## 用户会这样说

- 怎么安装这个 Skill？
- 命令找不到怎么办？
- 帮我看看为什么用不了。
- 我要反馈问题。
- CLI 要不要更新？
- 装不上，提示原来的程序不在。

## 先弄清楚

确认宿主和问题（安装、版本、服务或登录）；一次问完，优先运行自检。

## 标准流程

1. 检查 Node.js 20+、npm、npx；缺少时先安装。
2. Skill 三步安装：克隆仓库、复制 `skills/whobot-phonecall-skill`、重启宿主。
3. 命令不存在时执行 `npx --yes @whobot/cli@latest install`，再运行 `whobot status --skill 2.0.0`。
4. 自检运行 `whobot doctor`（需要人读时可加 `--pretty`）；需要反馈时运行 `whobot support`，把 `data.report` 原样放进代码块交给客服；输出带 `data.contactUrl` 时用图片展示客服二维码：`![联系客服](https://…)`（括号里放 `data.contactUrl` 的值），下一行再附这个链接（有的宿主不显示图片），`data.contactTitle`、`data.contactNote` 只转述。用户问官网、后台或管理平台：官网 https://whobot.com ，管理平台 https://work.whobot.com/ ；`data.consoleUrl` 存在时以它为准。

网页通话状态只由服务端保存；CLI 被宿主回收或更换对话后，继续运行 `next.command` 中的 `whobot call wait` / `whobot call show` 查询同一通话，不读取或清理本地网页通话状态文件。

## 话术

安装完成后告诉用户可说“呼波特能做什么”。自检进行中只说明正在检查。排障把 `data.report` 放进代码块并说可直接发给客服；协议 2 日常升级先运行 `whobot update` 展示当前版本与目标版本确认卡，再且仅再运行确认卡 `next.command` 中带 `--yes` 的命令。有活动网页通话时，更新会由服务端拒绝并提示先结束通话，不静默挂断。宿主工具的调用超时应至少设置 130 秒。

## 常见岔路

最低 CLI 和 Skill 版本由服务端分别校验，不自行比较或推导配套版本。预检的 `data.upgrades` 给出具体目标：CLI 用 `installCommand`，Skill 用 `packageUrl` 和 `instructionsUrl`；取得更新同意后操作，不把命令当作用户文案。按预检要求升级对应组件至渠道最新稳定版；Skill 用原平台更新入口或官方完整包安装，不自动覆盖宿主目录。Skill 更新后重载或新建任务，重新预检后才继续业务。失败重试或用户明确要求时也可重查；无 Skill 参数的状态查询只作诊断，不代表 Skill 已通过。

安装输出含 `PREVIOUS_CLI_MISSING` 或 `CREDENTIAL_ORIGIN_MISMATCH`：原来的程序被宿主清理了（或服务地址已变），本机登录核对不了，重试不会好。用选择卡说明并征求同意，推荐“清掉本机登录后重装”：员工和数据都在服务端不受影响，装好后要重新登录一次。同意后运行安装输出给出的恢复命令（即第 3 步的安装命令末尾加 `--reset-local`），成功后按 [account](account.md) 重新登录；不同意就停下，不重试、不手动删文件、不换别的办法。

协议 v1 或 `status` 未知时停止业务，不运行旧自升级器：先用 `whobot version` 查看 channel，再用 `npm view @whobot/cli dist-tags --json` 取得同渠道最新具体版本；展示目标并取得同意后，将该版本代入 `npx --yes @whobot/cli@<具体版本> install`。仅 Skill 更新而 CLI 仍旧版也走此流程，完成后重新预检。PATH 没有入口就用安装结果给出的实际入口。宿主命令预算不足时按宿主设置调整，不给 CLI 传超时参数。

## 绝不

- 不静默更新或删除本机身份。
- 不把内部错误码念给用户。
- 不把安装成功说成登录成功。
- 不上传排障报告之外的秘密。
