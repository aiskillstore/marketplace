---
name: cold-email-list-quality
description: Score a cold-email prospect list 0-100 across dedup, role-fit (vs brand-config.icp), signal freshness, email-validity heuristics, exclusion-criteria match, and company-stage match. Returns the score, list of rows to remove, and a fix recommendation. Loaded by cold-email-weekly-rhythm on Monday's list refresh. Operates on CSV or JSONL; no external services.
user-invocable: false
allowed-tools: Read Bash Write
  - Grep
license: MIT

---

# Cold Email List Quality — list scoring + dedup

Run before any campaign. Bad lists kill reply rates more than bad
copy. This sub-skill scores the list across 6 axes, returns the rows
to remove, and surfaces fix recommendations.

## Activation

Loaded by:
- `cold-email-weekly-rhythm` — Monday's list refresh
- User invocation: "Score my list", "Check list quality", "Clean my prospect list"

## Inputs

The skill accepts:

- **CSV** with at minimum: `email`, optional `first_name`, `last_name`,
  `role`, `company`, `signal`, `signal_date`, `linkedin_url`
- **JSONL** with same fields

If `brand-config.json` is loaded, the skill cross-references
`icp.segment`, `icp.role_targets`, `icp.exclusion_criteria`, and
`psp.signal_anchors` for scoring.

## Scoring (6 axes, 100 total)

| Axis | Max | What it catches |
|---|---|---|
| Dedup | 20 | Exact-match emails, near-duplicate same-company-same-person rows |
| Role-fit | 25 | Role title matches `brand-config.icp.role_targets` or known equivalents |
| Signal freshness | 20 | Signal age — fresh (≤14d) > recent (15-30d) > stale (>30d) |
| Email validity | 15 | Heuristic checks — RFC-shaped, no plus-extensions for B2B, no free-email domains, no role-account emails (info@, sales@) |
| Exclusion match | 10 | Row matches any `brand-config.icp.exclusion_criteria` → fail |
| Company-stage match | 10 | Company stage (from signal or heuristic) matches ICP segment |

## Output

```markdown
# List Quality Score — <file>

## Overall: <0-100>/100

| Axis | Score | Issues |
|---|---|---|
| Dedup | <0-20>/20 | <N> duplicate rows |
| Role-fit | <0-25>/25 | <N> rows outside ICP role targets |
| Signal freshness | <0-20>/20 | <N> stale signals (>30d) |
| Email validity | <0-15>/15 | <N> invalid / free-email / role-account |
| Exclusion match | <0-10>/10 | <N> rows hit exclusion criteria |
| Company-stage match | <0-10>/10 | <N> wrong-stage companies |

## Rows to remove (<N> total)

| Row | Email | Reason |
|---|---|---|
| 12 | sarah@gmail.com | Free-email domain (B2B) |
| 14 | info@acme.com | Role-account email |
| 22 | mike@acme.com (Engineering Manager) | Role outside ICP (target: VP+) |
| 27 | jane@beta.com | Signal stale (45 days) |
| ... |

## Fix recommendations (in order)

1. Remove the 12 free-email + role-account rows (immediate)
2. Re-pull signals for the 8 stale rows (today)
3. Tighten role-fit list — 14 rows are "Engineering Manager" / "Director"
   while ICP targets VP+. Consider adding "Director" if the ICP has
   shifted, or excluding these rows.
4. Run `cold-email-deliverability` on the sending domain before this
   list ships.

## Send-volume recommendation

With cleaning, the deliverable list is: <N - removed> rows.

Given warm-up state (`<warm_up_status>`), recommended weekly send
volume: <X> per day across <M> mailboxes = <X*M> per day = <X*M*5>
per week.

## Send the cleaned list

The skill writes `<file>.cleaned.csv` and `<file>.removed.csv` to the
project root. Operator can review before importing into Smartlead /
Instantly / etc.
```

## What gets flagged automatically

### Dedup
- Same email → duplicate (remove all but oldest)
- Same `linkedin_url` → duplicate (remove all but most-recent signal)
- Same `first_name + last_name + company` → near-duplicate (warn,
  don't auto-remove — might be father/son etc.)

### Role-fit
- Compare each `role` against `brand-config.icp.role_targets`
- Apply role-equivalent map (built-in):
  - "Demand Gen Lead" ↔ "Head of Demand Generation" ↔ "VP Demand Gen"
  - "CRO" ↔ "Chief Revenue Officer" ↔ "VP Revenue"
  - etc.
- Rows where role doesn't match any target → flag with severity

### Signal freshness
- Compare `signal_date` to today
- Score:
  - 0-7 days = full score
  - 8-14 days = full score
  - 15-30 days = half score + warn
  - >30 days = zero score + recommend removal

### Email validity heuristics
- RFC-shape (`@`, `.`, no spaces)
- Free-email domains (gmail.com, yahoo.com, outlook.com, hotmail.com,
  proton.me, icloud.com, aol.com, gmx.com)
- Role-account patterns (info@, sales@, support@, hello@, contact@,
  marketing@, hr@, jobs@, careers@, admin@)
- Plus-extension addresses (alex+marketing@acme.com) — flag as warn

### Exclusion match
- Each row scored against each `exclusion_criteria` entry
- Examples: "Pre-PMF (<$2M ARR)", "Enterprise-only ACV >$100k",
  "Government/regulated industries"
- Uses heuristic + (optional) external enrichment data if present in row

### Company-stage match
- Derive stage from signal (e.g., "Series B announced" → stage = Series B)
- Match against ICP segment description
- Out-of-stage rows flagged

## Implementation

Backed by `scripts/score_list.py` (Python 3.8+, no external deps —
uses csv stdlib).

```bash
python3 ../../scripts/score_list.py \
    --input prospects.csv \
    --brand-config ../../brand-config.json \
    --format text
```

(Note: `score_list.py` ships in the next release — for v0.2.0 this
skill describes the contract; the deterministic script ships Wave 2.)

## References

- `brand-config.json` — ICP, exclusion, role targets, PSP signal anchors
- `../cold-email-weekly-rhythm/SKILL.md` — Monday's caller
- Send-volume math: `warm_up_status` table in
  `cold-email-deliverability/SKILL.md`
