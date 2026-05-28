---
name: emerging-topic-scout
description: A real-time monitoring system for identifying "incubation period" research hotspots in biological and medical sciences before they are defined by mainstream journals.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Emerging Topic Scout

A real-time monitoring system for identifying "incubation period" research hotspots in biological and medical sciences before they are defined by mainstream journals.

## When to Use

- Use this skill when the task needs A real-time monitoring system for identifying "incubation period" research hotspots in biological and medical sciences before they are defined by mainstream journals.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: A real-time monitoring system for identifying "incubation period" research hotspots in biological and medical sciences before they are defined by mainstream journals.
- Packaged executable path(s): `scripts/main.py` plus 1 additional script(s).
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `feedparser`: `unspecified`. Declared in `requirements.txt`.
- `requests`: `unspecified`. Declared in `requirements.txt`.
- `textblob`: `unspecified`. Declared in `requirements.txt`.
- `requests`: `>=2.28.0`. Declared in `scripts/requirements.txt`.
- `feedparser`: `>=6.0.10`. Declared in `scripts/requirements.txt`.
- `pandas`: `>=1.5.0`. Declared in `scripts/requirements.txt`.
- `scikit-learn`: `>=1.1.0`. Declared in `scripts/requirements.txt`.
- `numpy`: `>=1.23.0`. Declared in `scripts/requirements.txt`.
- `textblob`: `>=0.17.1`. Declared in `scripts/requirements.txt`.
- `pyyaml`: `>=6.0`. Declared in `scripts/requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/emerging-topic-scout"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/main.py` with additional helper scripts under `scripts/`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Quick Check

Use this command to verify that the packaged script entry point can be parsed before deeper execution.

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

Use these concrete commands for validation. They are intentionally self-contained and avoid placeholder paths.

```bash
python -m py_compile scripts/main.py
python scripts/smoke_test.py
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Audit Note

The primary script depends on optional external packages such as `textblob` and live-source access. Audit validation therefore uses `scripts/smoke_test.py` as the deterministic fallback command for structural verification in constrained environments.

## Overview

This skill continuously monitors:
- **bioRxiv**: Biology preprints via RSS/API ⚠️ *Currently blocked by Cloudflare*
- **medRxiv**: Medicine preprints via RSS/API ⚠️ *Currently blocked by Cloudflare*
- **arXiv**: Quantitative Biology preprints via RSS ✅ *Recommended alternative*
- **Academic discussions**: Social media and forum mentions

It uses trend analysis algorithms to detect sudden spikes in topic frequency, cross-platform mentions, and emerging keyword clusters.

### ⚠️ Network Access Notice

**bioRxiv and medRxiv** are currently protected by Cloudflare JavaScript Challenge, which prevents programmatic RSS access. As a workaround, this skill now supports **arXiv q-bio** (Quantitative Biology) as an alternative data source.

**Recommended usage:**
```text

# Use arXiv for reliable data fetching
python scripts/main.py --sources arxiv --days 30

# bioRxiv/medRxiv may return 0 results due to Cloudflare protection
python scripts/main.py --sources biorxiv medrxiv --days 30  # May not work
```

## Installation

```text
cd /Users/z04030865/.openclaw/workspace/skills/emerging-topic-scout
pip install -r scripts/requirements.txt
```

## Usage

### Basic Scan (Recommended: Use arXiv)

```text
python scripts/main.py --sources arxiv --days 7 --output json
```

### Legacy bioRxiv/medRxiv (May not work due to Cloudflare)

```text
python scripts/main.py --sources biorxiv medrxiv --days 7 --output json
```

### Advanced Configuration (arXiv Recommended)

```text
python scripts/main.py \
  --sources arxiv \
  --keywords "CRISPR,gene editing,machine learning" \
  --days 14 \
  --min-score 0.7 \
  --output markdown \
  --notify
```

### Legacy Configuration (bioRxiv/medRxiv - May not work)

```text
python scripts/main.py \
  --sources biorxiv medrxiv \
  --keywords "CRISPR,gene editing,long COVID" \
  --days 14 \
  --min-score 0.7 \
  --output markdown \
  --notify

# Note: bioRxiv/medRxiv may return 0 results due to Cloudflare protection

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--sources` | list | `arxiv` | Data sources to monitor (arxiv recommended due to Cloudflare issues with biorxiv/medrxiv) |
| `--keywords` | string | (auto-detect) | Comma-separated keywords to track |
| `--days` | int | `7` | Lookback period in days |
| `--min-score` | float | `0.6` | Minimum trending score (0-1) |
| `--max-topics` | int | `20` | Maximum topics to return |
| `--output` | string | `markdown` | Output format: `json`, `markdown`, `csv` |
| `--notify` | flag | `false` | Send notification for high-priority topics |
| `--config` | path | `config.yaml` | Path to configuration file |

## Output Format

### JSON Output

```json
{
  "scan_date": "2026-02-06T05:57:00Z",
  "sources": ["biorxiv", "medrxiv"],
  "hot_topics": [
    {
      "topic": "gene editing therapy",
      "keywords": ["CRISPR", "base editing", "prime editing"],
      "trending_score": 0.89,
      "velocity": "rapid",
      "preprint_count": 34,
      "cross_platform_mentions": 127,
      "related_papers": [
        {
          "title": "New CRISPR variant shows promise",
          "authors": ["Smith J.", "Lee K."],
          "doi": "10.1101/2026.01.15.xxxxx",
          "source": "biorxiv",
          "published": "2026-01-15",
          "abstract_summary": "..."
        }
      ],
      "emerging_since": "2026-01-20"
    }
  ],
  "summary": {
    "total_papers_analyzed": 1247,
    "new_topics_detected": 8,
    "high_priority_alerts": 2
  }
}
```

### Markdown Output

```markdown

# Emerging Topics Report - 2026-02-06

## 🔥 High Priority Topics

### 1. Gene Editing Therapy (Score: 0.89)
- **Keywords**: CRISPR, base editing, prime editing
- **Growth Rate**: Rapid (+145% vs last week)
- **Preprints**: 34 papers
- **Cross-platform mentions**: 127

#### Key Papers
1. "New CRISPR variant shows promise" - Smith J. et al.
   - DOI: 10.1101/2026.01.15.xxxxx
   - Source: bioRxiv
```

## Configuration File

Create `config.yaml` for persistent settings:

```yaml
sources:
  arxiv:
    enabled: true
    rss_url: "https://export.arxiv.org/rss/q-bio"
    description: "arXiv Quantitative Biology - Recommended (no Cloudflare)"
  biorxiv:
    enabled: false  # Disabled due to Cloudflare protection
    rss_url: "https://www.biorxiv.org/rss/recent.rss"
    api_endpoint: "https://api.biorxiv.org/details/"
    note: "Currently blocked by Cloudflare JavaScript Challenge"
  medrxiv:
    enabled: false  # Disabled due to Cloudflare protection
    rss_url: "https://www.medrxiv.org/rss/recent.rss"
    api_endpoint: "https://api.medrxiv.org/details/"
    note: "Currently blocked by Cloudflare JavaScript Challenge"

trending:
  min_papers_threshold: 5
  velocity_window_days: 3
  novelty_weight: 0.4
  momentum_weight: 0.6

keywords:
  auto_detect: true
  custom_trackers:
    - "artificial intelligence"
    - "machine learning"
    - "single cell"
    - "spatial transcriptomics"

output:
  default_format: markdown
  save_history: true
  history_path: "./data/history.json"

notifications:
  enabled: false
  high_score_threshold: 0.8
```

## Trending Score Algorithm

The trending score (0-1) is calculated using:

```
Score = (Novelty × 0.4) + (Momentum × 0.4) + (CrossRef × 0.2)

Where:
- Novelty: Inverse frequency of topic in historical data
- Momentum: Rate of increase in mentions over velocity window
- CrossRef: Mentions across multiple platforms
```

## API Endpoints

### bioRxiv API
- Base: `https://api.biorxiv.org/`
- Details: `/details/[server]/[DOI]/[format]`
- Publication: `/pub/[DOI]/[format]`

### medRxiv API
- Same structure as bioRxiv

## Data Storage

Historical data is stored in `data/history.json` for:
- Trend comparison
- Velocity calculation
- Duplicate detection

## Examples

### Example 1: Quick Daily Scan (arXiv - Recommended)

```text
python scripts/main.py --sources arxiv --days 1 --output markdown
```

### Example 2: Daily Scan with bioRxiv (May not work)

```text
python scripts/main.py --sources biorxiv --days 1 --output markdown

# Note: May return 0 results due to Cloudflare protection

### Example 2: Weekly Deep Analysis

```text
python scripts/main.py \
  --days 7 \
  --min-score 0.7 \
  --max-topics 50 \
  --output json \
  > weekly_report.json
```

### Example 3: Track Specific Research Area

```text
python scripts/main.py \
  --keywords "Alzheimer,neurodegeneration,amyloid" \
  --days 30 \
  --min-score 0.5
```

## Known Issues

### bioRxiv/medRxiv Cloudflare Protection
**Status:** ❌ Blocked  
**Issue:** bioRxiv and medRxiv RSS feeds are protected by Cloudflare JavaScript Challenge, which prevents programmatic access. The site returns an HTML page requiring JavaScript execution and cookie validation.

**Attempted Solutions:**
1. ✅ Added browser User-Agent headers → **Failed** (Cloudflare detects bot)
2. ✅ Added complete browser headers (Accept, Accept-Language, etc.) → **Failed** 
3. ❌ Browser automation (Selenium/Playwright) → **Not implemented** (complex, heavy dependency)

**Workaround:** ✅ **Use arXiv instead**
- arXiv q-bio (Quantitative Biology) RSS is accessible without protection
- Contains computational biology, bioinformatics, and quantitative biology papers
- Successfully tested: 35+ papers fetched in 30-day window

**Usage:**
```text

# Recommended: Use arXiv
python scripts/main.py --sources arxiv --days 30

# Not working: bioRxiv/medRxiv
python scripts/main.py --sources biorxiv medrxiv --days 30  # Returns 0 papers
```

## References

See `references/README.md` for:
- API documentation links
- Research papers on trend detection
- Related tools and resources

## License

MIT License - Part of OpenClaw Skills Collection

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `emerging-topic-scout` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `emerging-topic-scout` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.
