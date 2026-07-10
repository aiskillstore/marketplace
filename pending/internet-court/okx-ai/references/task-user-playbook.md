# User's User Session Playbook

> 🌐 **[Localization]** — all user-facing content must match the user's language. English users: template verbatim. Non-English: translate faithfully, preserving all field labels, data values, structure.

---

## Reading Order

1. **This file**: pre-flight, intent routing, communication boundary, decision relay — read once.
2. **[`task-user-actions-publish.md`](task-user-actions-publish.md)**: on demand — read when the user wants to publish a task or manage drafts.
3. **[`task-user-actions.md`](task-user-actions.md)**: on demand — read only the specific section needed (§2 attachment / §3 terms / §4 deliverables).
4. **[`task-cli-reference.md`](task-cli-reference.md)**: do NOT read full file. Use `grep` for the specific command you need.

⚡ Re-reading a file already in context costs 1 LLM round + thousands of tokens for zero new information.

---

## User Intent Routing

> When the user-session receives free-form text targeting a specific task and no pending decision matches, load [`task-user-intent-routing.md`](task-user-intent-routing.md) and follow its routing flow.

| Intent | Trigger examples | Route to |
|---|---|---|
| Publish task | "发布任务 / create a task / 帮我发个任务" | [`task-user-actions-publish.md`](task-user-actions-publish.md) |
| Draft operations | "save as draft / 草稿列表 / publish draft" | [`task-user-actions-publish.md`](task-user-actions-publish.md) §1.1 |
| Add attachment / image | "补充附件 / attach file to task" | [`task-user-actions.md`](task-user-actions.md) §2 |
| Switch provider / set public / stop task | "换服务商 / switch provider / 关闭任务 / stop task" | [`task-user-actions.md`](task-user-actions.md) §3 |
| View deliverables | "查看交付物 / view deliverables" | [`task-user-actions.md`](task-user-actions.md) §4 |
| Designated-provider A2A | "指定服务商 / use the service of Agent X / 购买Agent/ASP的服务 / buy service from Agent/ASP #XXXX / initiate a direct conversation with this provider" | [`task-user-actions-publish.md`](task-user-actions-publish.md) §5 |
| Designated-provider x402 | "send a request to this endpoint" | [`task-user-actions-publish.md`](task-user-actions-publish.md) §6 |
| Negotiate with provider | "negotiate with XXX" | Sub session handles automatically |
| Browse marketplace | "搜索任务 / browse marketplace" | `task-search` ([`task-cli-reference.md`](task-cli-reference.md#task-search)) |
| Re-submit / nudge | "重新提交 / 催一下" | [`task-user-intent-routing.md`](task-user-intent-routing.md) |
| Task list / status / close / decision list | "我的任务 / 查看决策 / close task" | [`task-user-intent-routing.md`](task-user-intent-routing.md) |

---