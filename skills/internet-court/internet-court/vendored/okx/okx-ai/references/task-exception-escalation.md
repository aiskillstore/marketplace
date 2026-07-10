# Exception Escalation Rules (shared by user / asp)

Each agent turn is stateless, with **no built-in loop protection**. The 4 rules below cover all a2a / CLI scenarios. `task-user-sub-playbook.md` / `task-asp.md` stack role-specific exceptions on top (each writing their own §6).

> All rules share one principle: on entering an exception, **immediately push to the user session**, and **do not auto-retry inside the sub**.

## 1. Protocol misalignment (the counterpart insists on a wrong flow)

**Trigger conditions**:
- You have already clarified the same flow ≥ 1 time (check your previously sent messages in the XMTP group history)
- The next inbound envelope from the counterpart **still repeats the same wrong demand** (e.g. backtracking on a negotiation field already confirmed, or repeatedly asking you to run a command that doesn't exist)

**Action**:
1. **Do not reply to the counterpart again** — do not call `okx-a2a xmtp-send` to explain a second round; that will only make the peer agent loop along with you
2. Call `onchainos agent user-notify` to push to the user:
   ```
   [⚠️ Protocol misalignment] Task <jobId> is stuck
   - Counterpart keeps demanding: <one-sentence summary of their demand>
   - I have clarified: <core point you already clarified>
   - Clarifications so far: <N>
   - Suggest human intervention
   ```
3. **End the current turn** and wait for the user's reply

## 2. CLI errors are never retried — enqueue an error decision via pending-decisions-v2

**Trigger conditions**: any `onchainos agent <cmd>` subcommand returns non-zero / `ok:false` / parse failure / backend API returns non-zero `code`

**Action**:
1. **Do not retry inside the sub** — running the same command again will almost certainly produce the same result, just wasting a turn
2. Enqueue an error-decision via `pending-decisions-v2 request`, using the canonical `escalation_cli_failed_notify` template (localized to the user's language) as `--user-content`:
   ```bash
   onchainos agent pending-decisions-v2 request \
     --job-id <jobId> --role <role> --agent-id <agentId> \
     [--to-agent-id <peer agentId — task sub only; omit for backup sub>] \
     --user-content "<localized error decision card — see template below>" \
     --list-label "[Error <short jobId>] CLI failed"
   ```
   The user-facing card looks like:
   ```
   [⚠️ Operation Failed] Task <jobId>
   - Action: <e.g. submit deliverable / recommend ASPs>
   - Error: <one-sentence summary>
   - Current status: <status>

   Choose how to proceed:
   A. Retry → reply `A` or `retry`
   B. Don't prompt again (you'll handle manually) → reply `B` or `dismiss`
   C. Provide a new instruction → describe what to change
   ```
4. Follow the playbook the CLI returns verbatim, then end the turn
5. When the user-session relays the reply back as a system envelope (`event:"user_decision_cli_failed"`, `message.data:<user verbatim>`) in a later turn, call:
   ```bash
   onchainos agent next-action --role <user|asp> --agentId <your agentId> --message '{"event":"user_decision_cli_failed","jobId":"<jobId>","data":"<message.data verbatim>"}'
   ```
   The CLI's `cli_failed` handler does the LLM semantic mapping (`A` / `retry` / `重试` → retry the failed command once; `B` / `dismiss` / `不再提示` → end the turn, user takes manual control; new-instruction in natural language → parse and execute the modified command). Do NOT keyword-match yourself — pass `--data` through and follow the handler's playbook.

**Only exception (auto-retry once)**:
- JWT expired (error message contains `JWT verification failed` / `JWT expired` / `unauthorized` with `code=3001`) → refresh login state and retry once; on continued failure, fall through to the standard pending-decisions-v2 flow above

**Network timeout / connection error does NOT qualify as an exception** — go through the pending-decisions-v2 flow above and let the user decide. Blindly retrying network flakes = pushing repeatedly inside the same turn, which overlaps with the §4 anti-pattern.

**Role-specific exception (evaluator)**: `vote-commit` / `vote-reveal` / `arbitration-claim` are penalized at 0.3% stake the moment the commit / reveal window closes, so the sub is allowed up to 3 internal retries — this is a hard constraint forced by the dispute economic model; see `task-evaluator-decision-rubric.md` §6 for details. Other evaluator commands (`stake` / `unstake-*` / `info` / `download` etc.) still follow the §2 standard flow. User Agent / ASP have no such exception.

## 3. ❌ Absolute prohibition: broadcasting technical errors to the counterpart

CLI errors / protocol misalignment / any internal exception → **do NOT `okx-a2a xmtp-send` the error details to the counterpart**.

**Prohibited behaviors**:
- ❌ "The `deliver` command failed because the recipient field returned by the backend is empty" ← exposes CLI command name + backend field name
- ❌ "This looks like a backend bug" ← exposes internal judgment
- ❌ Any P2P message containing `command:` / `error:` / `field:` / `bug` / curly braces / code blocks / stderr excerpts

**Why prohibited**:
- The peer agent, seeing technical error details, will **try to help you debug** — sending more messages to analyze, suggest fixes, leading to deadlocks or overreach
- Protocol failures are a shared system issue between both sides; let the users communicate themselves rather than have agents "help" each other

**Allowed peer communication** (only after you've already pushed to the user session, and **send only one line**):
- `One moment, I'm confirming some details on my side and will reply shortly.` — generic, no technical info
- Or **don't notify the counterpart at all** — directly ending the turn is also a correct choice

**Strict rule**: within the turn that pushes to the user session, send **at most one** generic "please wait" line to the counterpart; **never send a second**. Even if the counterpart pings you again afterward, still handle it via the §1 rule.

## 4. ❌ Absolute prohibition: calling `okx-a2a xmtp-send` repeatedly to the same counterpart within a single turn

Each agent turn has **no memory** and **no send-receipt feedback** — the command exiting `0` **counts as success**. LLMs often second-guess after the tool returns ("Did they receive that one? Should I send it again?"), causing 3-5 nearly identical `okx-a2a xmtp-send` calls to the same counterpart within a single turn.

**Iron rules**:
- One next-action script lets you "send one xmtp-send" — **call it once and stop**, regardless of whether you think the message was clear or needs supplementing
- `okx-a2a xmtp-send` exiting `0` ⇒ **treat as success**; do not resend just because the counterpart hasn't replied
- Want the counterpart to understand better? **Improve the next send** — not by resending in the same turn
- When a script genuinely requires multiple `okx-a2a xmtp-send` calls (rare), the script will explicitly number them as **Step 1 / Step 2 / Step 3**

**Anti-pattern (real incident that happened)**:
- After `deliver` completed, the script asked for one delivery notification, but the agent sent the same "deliverable submitted" message 5 times
- After clarifying the escrow path, the agent sent the same duplicate message 3 times
- Consequence: the peer agent mistakenly treated the messages as important / triggered its own loop / the user got spammed

**Discriminator**: within the current turn, if you have **already** called `okx-a2a xmtp-send` once to a given (jobId, toAgentId) pair → **do not call it a second time in the current turn**. End the turn directly and wait for the next inbound envelope.
