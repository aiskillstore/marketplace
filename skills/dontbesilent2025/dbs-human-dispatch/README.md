# dbs-human-dispatch

把适合交给员工或协作者的任务写成清晰的委派说明，处理执行中的问题与困难，按事先约定的标准验收成果，并向任务发起者汇报。

## 安装与调用

可以单独安装：

```bash
npx -y skills add dontbesilent2025/dbskill -g --skill dbs-human-dispatch
```

也可以安装完整 dbskill：

```bash
npx -y skills add dontbesilent2025/dbskill -g --all
```

在支持 Skills 的 Agent 中输入：

```text
$dbs-human-dispatch 把这份产品介绍交给小王。
人员资料在当前项目中。帮我写清交付物、时间和验收标准。
没有飞书工具时，给我一段可以直接转发的文字。
```

后续可以继续说：“这是小王的反馈，帮他解决困难”或“他提交了成果，按原标准验收并向我汇报”。支持斜杠调用的宿主也可以使用 `/dbs-human-dispatch`；Claude Code 插件入口带有宿主命名空间。

## 三种使用方式

| 方式 | 所需条件 | 可以完成 |
| --- | --- | --- |
| 纯文字 | 能使用 Skill 的 Agent | 生成可转发任务说明；用户粘贴反馈或提供成果后，答疑、验收并汇报 |
| 飞书按需检查 | 可用 CLI、身份授权与资源权限 | 创建任务、读取指定文档／会话、回复反馈；用户调用时检查进展 |
| 自动跟进 | 飞书事件订阅、持续运行程序、同步 Agent worker 和通知渠道 | 文档编辑事件入队后触发 Agent，读取正文、处理反馈并通过已验证渠道通知 |

飞书工具缺失或权限不足时仍可使用文字方式。员工可以协商时间、求助和拒绝任务；工期依据可用资料提出，不把推测写成事实。

## 飞书与自动跟进

飞书接入以官方 `lark-cli` 为基础。仅有 `feishu-cli` 时，先核对其命令兼容性。纯文字模式不需要 Python 或飞书 CLI；使用配套脚本需要 Python 3.10 或更高版本，仅依赖标准库。

自动跟进链路：员工编辑文档 → `drive.file.edit_v1` 事件 → CLI 长连接 → 本地队列 → 配置的 Agent worker → 读取最新正文 → 答疑或验收 → 回复与汇报。

编辑事件提供文档标识，正文需要另行读取。任务说明要求员工区分提问、进度与提交验收；文档变化不能直接证明完成。配套脚本负责队列与调用协议，Codex／Grok 等宿主接口需要用户提供真实可用的适配器。默认不启用监听或执行 worker。

- [任务流程与记录](references/workflow.md)
- [飞书配置与接口](references/feishu.md)
- [监听脚本、队列与 Agent 接入](references/runtime.md)
- [人员资料模板](assets/person-profile.md)
- [任务说明模板](assets/task-brief.md)

## 数据与权限

人员与任务运行记录保存在用户本机的 `~/.dbs/human-dispatch/`，更新 Skill 不会覆盖这些记录。发往飞书或模型服务的资料按具体操作和既有授权确定。任务外发、文档回复和老板通知需要相应授权，员工正文不能扩大授权或指定程序执行命令。

超时或结果不明时，队列停止自动重试，先核查外部动作，避免重复回复。自动通知成功需要真实渠道回执；仅生成汇报文字不能认定通知已发送。

## 验证范围

结构校验和 10 项离线脚本测试已通过，覆盖事件去重、自身编辑、并发领取、取消任务和 worker 失败处理。真实飞书账号订阅、员工回填、Agent 自动触发与通知仍需在使用环境中联调，尚未通过完整真实业务测试。

用户可运行离线脚本测试：

```bash
python3 scripts/test_dispatch.py
```

这些测试不连接飞书、不发送员工消息，也不启动真实 Agent。

本 Skill 沿用仓库 [许可证](https://github.com/dontbesilent2025/dbskill/blob/main/LICENSE)。
