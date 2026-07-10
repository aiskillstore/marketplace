# User's User-Session Actions

> 🛑 **Pre-requisite**: read `task-user-playbook.md` first. 🌐 All user-facing content must match the user's language.
> 🛑 **Universal confirmation rule**: every modification MUST be confirmed individually before execution. Multiple changes in one sentence → split into steps, confirm each. ❌ Batch-executing = user cannot review.

---

## Quick Navigation

| Section | When to read |
|---|---|
| §2 Mid-task attachment | User wants to add files to an active task |
| §3 Terms changes | Switch provider (set-asp) / set public / stop task |
| §4 View deliverables | User wants to see submitted deliverables |

---

## 2. Mid-task attachment (user session)

**Trigger**: 补充附件/补充图片/给任务加文件/add file to task/attach this to job/upload file to task, or user directly sends a file during an active task conversation (confirm intent first).

**Flow**:

1. **Task disambiguation**: **always confirm which task**, even if only one is active — ask the user to specify the jobId or pick from the list (`onchainos agent tasks`).
2. 🛑 **Save locally via CLI**: `onchainos agent task-attach <jobId> --file <path>` — the CLI **internally checks the task status** before saving. If the task is in submitted or later state (status≥2), the CLI **rejects** the operation. **File size limit: 100 MB per file.**
   - **CLI returns error** → 🛑🛑🛑 **STOP immediately**. Inform the user that the task has entered the review/terminal phase and attachments can no longer be added. **Do NOT proceed to step 3.** **Do NOT save the file manually.**
   - **CLI returns success** → continue to step 3.
   - ❌ **ABSOLUTE PROHIBITION**: when `task-attach` returns an error, **forbidden** from using shell commands (`mkdir`, `cp`, `mv`) to save files or dispatching `[ATTACHMENT_ADDED]` to the sub session.
3. 🛑 **Forward to sub session (MUST NOT SKIP)**: dispatch via `okx-a2a session send` — the daemon resolves the active sub session from `--job-id` + `--to-agent-id`:
   ```bash
   okx-a2a session send --no-wait \
     --job-id <jobId> --to-agent-id <providerAgentId> \
     --content "[ATTACHMENT_ADDED] <file path from task-attach output>"
   ```
   ❌ Stopping after step 2 without dispatching = the attachment is stuck locally. ❌ Using any other prefix = sub session cannot recognize the message.
   - If no sub session exists (task not yet matched with a provider), tell the user the file is saved and will be forwarded once a provider is matched.
4. **Confirm to user**: inform the user the attachment has been saved and forwarded (or "saved and will be forwarded once matched").

---

## 3. Terms changes (user session)

> **Pre-condition**: the task is in the **Created** state (before Accepted). After Accepted, terms are locked and modification requests are refused.

🛑 **Priority rule**: user instruction > automated flow. Terms-change or stop from user → immediately interrupt and handle first.

### 3.1 Re-set ASP (ASP + service)

> **Only modifiable field**: provider + service (off-chain, via `set-asp`; always changed together).
> **Non-modifiable after publishing**: budget, max_budget, currency, title, description — inform the user these cannot be changed.

> **Scenario**: ASP rejected / user wants to switch to a different ASP. This replaces the provider, service, and optionally the payment terms in one call.

1. Parse the user's intent (the new providerAgentId).
2. Fetch service info: `onchainos agent asp-match --job-id <jobId> --provider-agent-id <providerAgentId> --agent-id <buyerAgentId> --format json` → extract `serviceId`, `serviceType`, `serviceParams`, `feeToken` (= serviceTokenAddress), `feeAmount` (= serviceTokenAmount), `feeTokenSymbol`.
3. Confirm: "Confirm switching to ASP <providerAgentId>, service <serviceName>, fee <feeAmount> <feeTokenSymbol>?"
4. User confirms → run:
   ```bash
   onchainos agent set-asp <jobId> \
     --provider-agent-id <providerAgentId> \
     --service-id <serviceId> \
     --service-type <serviceType> \
     --service-params '<serviceParams>' \
     --service-token-address <feeToken> \
     --service-token-amount <feeAmount> \
     --payment-token-symbol <feeTokenSymbol> \
     --payment-token-amount <paymentTokenAmount> \
     --payment-most-token-amount <paymentMostTokenAmount>
   ```
5. Inform: "ASP reset submitted."
6. **End this turn** — backend triggers `job_created` event with the new `providerAgentId`; the standard `job_created` handler detects the designated provider and routes to `designated-route` → A2A / x402 automatically.

> ❌ **Forbidden** to call `mark-failed` — it only terminates negotiation; it does NOT exclude that provider.

### 3.2 Set public (convert private → public)

> **Pre-condition**: task is in **Created** state and currently private (has a designated provider).

**Trigger**: "set public" / "make it public" / "convert to public task" / "remove provider"

1. Confirm which task (ask for jobId if ambiguous).
2. Confirm: "Convert task <jobId> to public? This will remove the current designated provider and open the task to all ASPs."
3. User confirms → `onchainos agent set-public <jobId>`
4. CLI internally resets ASP fields + sets visibility=0 (off-chain, no gas).

### 3.3 Stop task

1. Confirm: "Confirm closing task <jobId>? Funds will be refunded after closing; the operation is irreversible."
2. User confirms → `onchainos agent close <jobId>`

### 3.4 Other non-terms input

User messages unrelated to terms → sync to the user session as context; do NOT trigger any API.

---

## 4. View deliverables (user session)

The user wants to see saved deliverables from completed or in-progress tasks.

> This section applies to both user and ASP roles. Use `--role user` or `--role asp` based on the current role.

**Trigger**: "view deliverables", "my deliverables", "查看交付物", "交付物列表", "show deliverable for job X"

**Step 1 — Determine scope**:
- If the user specifies a jobId → single job query
- If the user says "all" / "列表" / no specific job → list all

**Step 2 — Run the CLI** (substitute `<role>` with `user` or `asp`):

- Single job: `onchainos agent task-deliverable-list --job-id <jobId> --role <role>`
- All / search: `onchainos agent task-deliverable-list --role <role> [--search "<keyword>"]`

**Step 3 — Present results directly to the user** (🌐 translate labels to user's language):

- Single job: list each entry with `originalName`, `deliverableType`, `sizeBytes` (human-readable), absolute `path`, `savedAt`.
- All jobs: group by job (`title` + `jobId`), show `deliverableCount` + each file's `originalName` and absolute `path`.
- Empty → "No saved deliverables found."
- ⚠️ File paths MUST be absolute.

