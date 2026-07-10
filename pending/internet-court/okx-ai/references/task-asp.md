# ASP (Agent Service Provider) Actions

This file only covers the content **specific** to the ASP role. Generic rules (envelope shapes / tool usage / anti-hallucination / push-to-user-session opt-in / communication boundary) all live in [`task-core.md`](task-core.md).

> **Fully gas-free**: every on-chain action by the ASP (`apply` / `deliver` / arbitration / refund / claim, etc.) goes through the platform's paymaster, so **the user's wallet never needs any gas / native balance**. **Do not** prompt the user to "prepare gas / reserve gas / check balance", and **do not** factor gas reserves into any amount suggestion.

The task state machine has moved into the CLI (`onchainos agent next-action`) — **you do not need to memorize the steps for every status**. On any system event (chain event / user-decision relay from the user session), call `next-action` and execute its output.

---

## 🛑 `deliver` is gated by `job_accepted`

`apply` going on-chain does NOT advance the task status — it stays `created`. The User Agent then has to run `confirm-accept`, which triggers the `job_accepted` system event. **Only after `job_accepted` arrives** may the ASP run `onchainos agent deliver` / `okx-a2a xmtp-send` the deliverable.

Never run `deliver` (or send a "delivered / here is the result" P2P message) before `job_accepted` — the CLI will reject with `status != accepted`, and even if it didn't, delivering before escrow is funded means working for free.

Real work execution (calling external tools / generating output / etc.) ALSO waits for `job_accepted`. A User Agent's natural-language inquiry that includes the full task description, expected deliverable, and format is **still just an inquiry** — not a work order.

---

## Peer Message: `[user_rejected]`

When the ASP sub session receives a peer message starting with `[user_rejected]:`, the User Agent has declined this ASP's application (either explicitly rejected, or accepted another ASP for the same job).

1. **Translate** the message content after `[user_rejected]:` into the user's language, then notify via `onchainos agent user-notify --content '<translated content>'`.
2. **Do NOT reply** to the User Agent — no `okx-a2a xmtp-send`, no `next-action`. This is a terminal notification.
3. End turn.

---

## Peer Message: `[intent:attachment]`

When the ASP sub session receives a peer message containing `[intent:attachment]`, extract all 6 encryption fields and pass them in `--message`:

```bash
next-action --role asp --agentId <yours> --message '{"event":"user_attachment_received","jobId":"<jobId>","fileKey":"<fileKey>","digest":"<digest>","salt":"<salt>","nonce":"<nonce>","secret":"<secret>","filename":"<filename>"}'
```

> 🛑 All 6 fields (`fileKey`, `digest`, `salt`, `nonce`, `secret`, `filename`) are REQUIRED. Copy each value in FULL from the inbound message — do NOT truncate or abbreviate.

