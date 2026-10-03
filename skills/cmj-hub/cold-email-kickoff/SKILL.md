---
name: cold-email-kickoff
description: Adaptive router for the cold-email skill pack. Detects the operator's current state (brand-config present? SOUL.md present? infrastructure ready? PSP defined? EVP locked? first campaign run?) and picks the next-best step. Loaded by the main cold-email skill on bare invocation ("/cold-email") or when the operator asks "where do I start" / "what's next". Inspired by coldoutboundskills' /cold-email-kickoff pattern.
user-invocable: false
allowed-tools: Read Write Grep
  - Bash
license: MIT

---

# Cold Email Kickoff — adaptive router

State-aware router. Operators don't ship cold email on day 1 — they
go through a sequence: ICP → PSP → EVP → infrastructure → first send
→ reply triage → iterate. Kickoff detects where the operator is in
that sequence and picks the right next step.

## Activation

Loaded by `cold-email` on:
- Bare `/cold-email` invocation (no other intent)
- "Where do I start"
- "What should I do next"
- "I'm new — what's the path"
- "Onboard me"

## State detection

Before recommending, kickoff checks the project state:

```python
# Pseudo-code
state = {
    "has_brand_config":   file_exists("brand-config.json"),
    "has_soul":           file_exists("SOUL.md"),
    "has_psp":            "psp" in brand_config and brand_config.psp.primary_pain != "",
    "has_evp":            "evp" in brand_config and brand_config.evp.primary != "",
    "has_infrastructure": "infrastructure" in brand_config and brand_config.infrastructure.sending_domain != "",
    "deliverability_audited_recently": days_since(brand_config.infrastructure.deliverability_last_audited) < 30,
    "first_send_logged":  has_entries(brand_config.operations.experiment_log_path),
    "reply_data_available": has_logged_replies(brand_config.operations.experiment_log_path)
}
```

Map state to the next-best step:

| State condition | Route to |
|---|---|
| `!has_brand_config OR !has_soul` | `cold-email-onboarding` |
| `has_brand_config AND !has_psp` | "Install `cmj-hub/claude-psp` first; let me know when PSP is done" |
| `has_psp AND !has_evp` | "Install `cmj-hub/claude-evp` first; let me know when EVP is done" |
| `has_evp AND !has_infrastructure` | "Let's set up infrastructure. Run `cold-email-deliverability` for a baseline audit." |
| `has_infrastructure AND !deliverability_audited_recently` | "Deliverability hasn't been re-audited in 30+ days. Run `cold-email-deliverability` first." |
| `deliverability_audited_recently AND !first_send_logged` | "Ready to ship. Want to draft your first sequence via `cold-email-craft`?" |
| `first_send_logged AND !reply_data_available` | "First sequence shipped. Set up reply routing — see `cold-email-reply-scoring`." |
| `reply_data_available` | "You've got data. Run `cold-email-audit` to score the program + `cold-email-weekly-rhythm` for the cadence going forward." |

## Welcome flow

On first invocation with no state:

```
> /cold-email

Welcome. Let's figure out where you are.

[Detected state: brand-config.json missing]

You're at step 1 of 7. The 7 steps:

1. ⬜ Set up brand-config + voice (10 min)        ← YOU ARE HERE
2. ⬜ Build a Pain Signal Profile (20-30 min)
3. ⬜ Lock the EVP for your primary tier (15 min)
4. ⬜ Set up sending infrastructure
5. ⬜ Run the 15-point pre-campaign deliverability check
6. ⬜ Draft + ship first signal-anchored sequence
7. ⬜ Score replies + iterate (weekly rhythm)

Step 1 takes ~10 minutes and is required for everything else.

Want to run it now? (y/n)
```

If yes → invoke `cold-email-onboarding`.
If no → tell the operator what minimum-mode produces, and offer to
defer.

## Status check mode

User-invocable: `/cold-email status`

Returns:

```
# Cold Email program status

Brand config:        ✓ brand-config.json (24 fields)
Voice (SOUL.md):     ✓ SOUL.md (8 phrases used, 6 banned, 5 stories)
PSP:                 ✓ Series-B SaaS pipeline-gap pain
EVP:                 ✓ Tier 3: "For Series-B SaaS, in a pipeline gap, we ship 14+ SQLs/month without hiring 2 SDRs"
Infrastructure:      ✓ outreach.acmecloud.com (Smartlead, ramped 60+d, DMARC quarantine)
Deliverability:      ✓ Last audited 2026-05-20 (3 days ago) — score 94/100
First send:          ✓ 142 sends logged (last 14d)
Reply data:          ✓ 11 replies (4 positive, 2 buy-signal, 5 neutral) — 7.7% reply rate

You're in iteration mode. Recommended next step:
→ Run `cold-email-audit` against your current program for the 30-point grade.
→ Or run `cold-email-weekly-rhythm` to set Monday's hunt + Wednesday's ship.
```

## Resume from a specific step

User-invocable: `/cold-email resume <step>`

Where step is `onboarding | psp | evp | infrastructure | deliverability | first-send | iterate`. Jumps to that step regardless of detected state.

## Why state-aware routing matters

Without it, kickoff would dump a "here are 12 sub-skills" menu and
overwhelm the operator. State-aware routing surfaces the ONE next step
that matters most given where they actually are.

The 30K+-star marketing-skills repos that work do this — orchestrator
adapts, doesn't list. Operators ship faster.

## References

- `../cold-email-onboarding/SKILL.md` — invoked on missing state
- `../cold-email-craft/SKILL.md` — invoked on "ready to ship"
- `../cold-email-audit/SKILL.md` — invoked on "have reply data"
- `../cold-email-weekly-rhythm/SKILL.md` — invoked on "in iteration mode"
