---
name: psp-signal-hunt
description: Surface 5-10 public, recent, verifiable signals worth hunting for a given ICP segment. Catalogs signal types (hiring, funding, leadership, product, pivot, content) and proposes operational sources + cadence to track each. Loaded by the main psp skill when the user wants to find what signals to hunt.
user-invocable: false
allowed-tools: Read WebFetch
  - Grep
license: MIT

---

# PSP Signal Hunt — sub-skill

Loaded by `psp` when the user wants to identify what signals to track
for a specific ICP segment.

## Activation

The main `psp` skill routes here on:
- "What signals should we hunt for <ICP>"
- "Find signals for <segment>"
- "Signal hunt"

## Signal taxonomy

The skill produces signal candidates across 6 categories:

| Category | Examples |
|---|---|
| **Hiring** | Specific role open ≤30 days; team size jump; first-of-kind hire (first SDR, first VP) |
| **Funding** | Round announced ≤30 days; secondary; bridge; ARR milestone |
| **Leadership** | New C-level / VP ≤60 days; departure; board change |
| **Product** | New tier / pricing change / feature launch / public roadmap ≤45 days |
| **Pivot** | Website hero rewrite; positioning shift; rebrand; new ICP language |
| **Content** | Podcast / panel / public talk on the relevant pain ≤30 days |

## Workflow

### 1. Take the ICP segment

The user provides a specific ICP (e.g. "Series-B SaaS, $20-50M ARR,
PLG motion"). If they're vague, ask for precision before continuing.

### 2. Generate 5-10 candidate signals

For each candidate, output:

- **Signal type** (from the 6 categories)
- **What to look for** (specific shape — e.g. "Demand Gen Lead role posted ≤14 days")
- **Where to find it** (LinkedIn / Crunchbase / RSS / podcast feeds / their own blog)
- **Cadence** (daily / weekly / event-driven)
- **Why this signal implies operational pain for this ICP**

### 3. Rank by hunting feasibility

Rank the 5-10 candidates by:
- **Volume**: how many target companies show this signal monthly
- **Specificity**: how directly it implies actionable pain
- **Effort**: how hard to operationalize the hunt

### 4. Output

```markdown
# Signal hunt — <ICP segment>

| # | Signal | Where | Cadence | Pain implied | Volume |
|---|---|---|---|---|---|
| 1 | Demand Gen Lead role posted ≤14d | LinkedIn job search + RSS | Daily | Pipeline gap | ~15-30/mo |
| 2 | Series B announced ≤30d | Crunchbase API + CB Insights newsletter | Weekly | 3x revenue mandate | ~5-10/mo |
| 3 | New CMO ≤60d | LinkedIn search + The Org | Weekly | 90-day GTM stack review | ~3-8/mo |
| 4 | ... | ... | ... | ... | ... |

## Recommended hunt stack
1. **Daily**: LinkedIn job posts (manual or via Phantombuster)
2. **Weekly**: Crunchbase + The Org
3. **Event-driven**: Podcast RSS for relevant shows

## Operational notes
- Capture signal date so freshness is enforced
- Tag each signal with the implied pain at capture time
- Stale signals (>45 days for hiring, >30 days for funding) drop from outreach queue
```

### 5. Hand off

Once signals are picked, hand to:
- **claude-cold-email** → first-line opener uses Signal verbatim
- **claude-psp psp-construct** → map each signal to a felt pain
