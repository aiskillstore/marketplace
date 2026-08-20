# OKX.AI Trading Hackathon — FAQ

> **Precondition (BLOCKING):** [`hackathon-core.md`](hackathon-core.md) must already be loaded — it holds the Output Rules and Pre-Delivery Checklist these answers assume and do not restate. If you reached this file first, stop and read it now, then come back.
>
> Scope: common questions about `hackathon register` outside an active registration walkthrough (that flow is `hackathon-registration.md`). Answers stay short and point at `hackathon-registration.md` for the mechanics — that file is the single source for flags, templates, and error handling. If a question is answered in none of these files, say so and defer to the error message the command itself returned rather than guessing.

**Q: What does my Trading ASP agent need to qualify?**
A: Three preconditions: (1) a trading-type ASP, (2) offers a subscription service, (3) offers a 3-day free trial. All three are checked at registration and it is refused if any is not met — so they cannot be self-declared. `hackathon-registration.md` Step 1 covers when and how the flow pre-confirms them.

**Q: Which chain does this register against?**
A: X Layer, fixed by the CLI/MCP tool — no flag sets or returns it, and neither does the hackathon's internal activity id. Refer to the hackathon by name, never by that id (`hackathon-core.md` §Output Rules).

**Q: Do I need to fund my account before I register?**
A: No. `hackathon register` does not check or gate on balance. The 300 USDT-equivalent requirement is checked later, by a balance snapshot taken across all entrants before the competition starts.

**Q: What's the difference between the `web3` and `cefi` account types?**
A: `web3` registers with your current wallet's X Layer address and needs no UID; `cefi` additionally requires your OKX UID. `hackathon-registration.md` Step 2 covers how each is collected and submitted.

**Q: What happens to my OKX UID?**
A: It is submitted with the registration and nothing else — not returned in the result, not printed to the terminal, and fully redacted in the local audit log.

**Q: Can I skip providing my wallet address?**
A: Yes, for both account types — it auto-resolves from your currently selected wallet account's X Layer (EVM) address. Pass it explicitly only to override.

**Q: My registration failed — what should I do?**
A: Branch on `errorCode`, never on the wording of the message — the wording changes without notice, the code is the contract. The authoritative table (rejection / service unavailable / CLI-side validation, and what to say for each) is `hackathon-registration.md` Step 4 — read it before replying, and note the rule that a service-unavailable failure must **never** be reported as an eligibility problem.

**Q: The registration keeps getting rejected and the message mentions the activity, not my ASP.**
A: This CLI build is pinned to one specific hackathon, so that means the hackathon is over rather than anything being wrong with the ASP. `hackathon-registration.md` Step 4 has the exact handling; there is no flag to point the command at a different activity.

**Q: I have no ASP — can I still register?**
A: No. Registration needs an ASP that already exists; this activity never creates one — creating an agent identity is `okx-ai`. `hackathon-registration.md` Step 1 has the fixed no-ASP message — use it verbatim (translated) rather than improvising alternatives.

**Q: Can I register more than one agent, or list/update a registration afterward?**
A: `hackathon register` submits exactly one `--agent-id` per call, and there is no list/update/status subcommand in the current CLI or MCP surface. If asked, say it isn't supported today rather than guessing at a flow that doesn't exist.

**Q: What happens if I run `hackathon register` again for the same agent?**
A: The CLI does not track prior registration state client-side — it submits again, and the response (success or a rejection message) is authoritative on whether a duplicate is allowed.

**Q: I asked to join a competition/trading cup — is this the right skill?**
A: No. The hackathon activity only enters an existing Trading ASP in the OKX.AI hackathon; joining a standard trading competition or cup is `competition join` in `okx-growth-competition`.
