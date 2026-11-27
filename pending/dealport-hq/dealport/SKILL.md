---
name: dealport
description: Use when the user wants to find, size, research, score, or contact off-market US small and mid-sized businesses (28M+ private companies), commercial buildings, or the human principals behind them; match a CSV of company names or domains; monitor target companies in a Project; or request double-opt-in owner introductions through Avery.
version: 0.1.3
---

# Dealport: The SMB Knowledge Layer for Agents and Humans

Dealport holds cited **Records** on 28M+ US private companies, the commercial buildings they own, and the human principals behind them (corporate registries, UCC filings, Medicare & CMS cost reports, state health and trade licenses, SEC Form ADV, property & mortgage deeds, and cached company websites). Every fact carries its primary source and basis (`filed`, `observed`, or `estimate`).

## 1. Check Your Connection First

Use whichever Dealport interface is available in your runtime:

1. **MCP Tools (`https://app.dealport.com/api/mcp`):** If you see `preview_companies`, `search_companies`, `get_record`, `annotate_companies`, and `find_owner`, Dealport MCP is already connected. Use those tools directly.
2. **CLI (`npx dealport`):** Zero-dependency Node 20+ CLI wrapping `/api/v1/*`:
   ```bash
   npx dealport balance --json
   ```
   If unauthenticated, guide the user to create an API key in **Connect your AI -> API keys** (`https://app.dealport.com/connect?tab=keys`) and run:
   ```bash
   npx dealport login --key dp_live_...
   ```
   Or connect MCP in one command:
   ```bash
   claude mcp add --transport http dealport https://app.dealport.com/api/mcp
   ```

## 2. Follow the 5-Step Dealport V4 Workflow

Always execute sourcing and origination mandates in this order so the user gets fast, cited results without wasted spend:

### Step 1: Size the Market Free (`preview`, `$0.00`)
Start every mandate with a free preview to check the total matching universe and review 5 sample companies with the user before opening paid records:
```bash
npx dealport preview --state OH --naics 238220 --min-employees 15 --independent --json
```
*(MCP equivalent: `preview_companies`)*

### Step 2: Pull Cited `Record`s & Website `pages` (`$0.01`/record, `$0.00` 30-day repeat)
Fetch candidate companies or buildings and inspect primary filing citations and website Markdown:
```bash
npx dealport search --state OH --naics 238220 --independent --limit 25 --json
npx dealport record <company_id> --evidence --json
npx dealport pages <company_id_or_domain> --paths /,/about,/services --json
```
Starting from a user's CSV of accounts or territory targets? Match up to 250 rows at `$0.00`:
```bash
npx dealport match targets.csv --project "Ohio HVAC Mandate" --json
```
Searching NYC commercial/multifamily buildings?
```bash
npx dealport buildings --borough BK --min-units 20 --loan-due-by 2027 --json
```
*(MCP equivalents: `search_companies`, `get_record`, `fetch_company_pages`, `match_company_list`, `search_buildings`)*

Always state whether revenue, headcount, and ownership facts are `filed`, `observed`, or `estimate`.

### Step 3: Persist Ranked Scores & Monitor in a Dealport `Project` (`annotate`, `$0.00`)
Whenever you evaluate or rank candidate companies against a Playbook or buy-box rubric, **always write scores back into Dealport** so the human user can inspect the living Project in their workspace UI:
```bash
npx dealport annotate \
  --company <company_id> \
  --project "Ohio Commercial HVAC" \
  --score 92 \
  --verdict priority \
  --rationale "32-year operating history, commercial service mix, filed state license" \
  --field commercial_b2b=true \
  --json
```
- `score`: integer `0` to `100`
- `verdict`: `priority` | `qualified` | `watch` | `pass`
- Cost: `$0.00` *(MCP equivalents: `annotate_companies`, `get_annotations`, `list_playbooks`, `save_playbook`, `list_projects`, `project_leads`, `create_project`, `save_project_search`, `run_project`, `project_run_status`; CLI: `npx dealport playbooks [list | get <id> | save]` and `npx dealport projects [list | leads <id> | create | source <id> | run <id> | run-status <id> <batch>]`)*

To monitor companies weekly in a Project (`$0.05`/company/month, `$0.00` weekly `what_changed` diffs) or configure signed `X-Dealport-Signature` HTTPS Project webhooks (`$0.00`), use `watch_companies`, `what_changed`, and the separated webhook tools (`list_watch_webhooks`, `create_watch_webhook`, `toggle_watch_webhook`, `test_watch_webhook`, `delete_watch_webhook`), or CLI `npx dealport webhooks [list | create | test | delete]`. Ask explicit human confirmation before `delete_watch_webhook`.

### Step 4: Check `blocklist` & Resolve Human Principals (`owner`, `$0.09` hit / `$0.00` miss)
Before unlocking contacts or outreach, check workspace exclusions (NDAs, portfolio companies, CRM accounts, passed deals) and resolve the verified human founder/owner (corporate registered agents and generic `info@`/`sales@` role inboxes are filtered out):
```bash
npx dealport blocklist list --json
npx dealport owner <company_id> --json
```
*(MCP equivalents: `list_blocklist`, `add_blocklist`, `remove_blocklist`, `find_owner`, `find_contact`, `research_building_owners` at `$0.05`/NYC building owner, `research_company` at `$0.50` + `get_research` at `$0.00`)*

If no verified human phone or email is found, the call costs `$0.00`. Ask explicit human confirmation before `remove_blocklist`.

### Step 5: Ask Explicit Human Permission Before `avery`
**Avery** is Dealport's AI outreach specialist for double-opt-in owner introductions. She writes privately to business owners, always discloses she is an AI, and brings back owners who opt in to talk. Always refer to Avery as **Dealport's AI outreach specialist** (never imply a human is writing or describe her as a customer-owned bot).

- **Hard rule:** Never run `avery reach-out` / `avery_reach_out` (`$0.02` per email Avery sends, up to 150 owners/month self-serve) or `avery accept-intro` / `avery_accept_intro` (`$25.00`/accepted Warm Yes introduction) without **explicit human confirmation** naming the target company, human principal, and USD cost.
- The CLI enforces this with a required `--yes` flag on mutations:
  ```bash
  npx dealport avery status --json
  npx dealport avery reach-out --company <company_id> --intent acquisition --yes --json
  npx dealport avery accept-intro --conversation <conversation_id> --yes --json
  ```

## 3. Plain-USD Rate Card (API Pro - Pay as You Go)

New accounts start with a **$5.00 free USD balance** and no subscription. HTTP `402` (CLI exit code `2`) indicates the USD balance or monthly key spend cap was reached.

| Action | CLI / SDK / MCP | Rate (USD) |
| --- | --- | --- |
| Market sizing, CSV matching, Playbooks, Projects, annotations, blocklist, flags, webhooks, diffs | `preview_companies`, `match_company_list`, `list_playbooks`, `save_playbook`, `list_projects`, `create_project`, `annotate_companies`, `list_blocklist`, `what_changed`, `list_watch_webhooks`, `create_watch_webhook`, `toggle_watch_webhook`, `test_watch_webhook`, `delete_watch_webhook` | `$0.00` |
| Repeat reads within 30 days in the same workspace | `search_companies`, `search_buildings`, `get_record`, `find_owner`, `research_company` | `$0.00` |
| Search row or full cited `Record` (company or building) | `search_companies`, `search_buildings`, `get_record` | `$0.01` |
| Website Markdown reader (`pages`) | `fetch_company_pages` | `$0.00` cached / `$0.01` live |
| Monthly company monitoring in a `Project`, Playbook check, or NYC building owner lookup | `watch_companies`, `run_project`, `research_building_owners` | `$0.05` |
| Verified human company owner / contact phone & email hit (`$0.00` on miss or 30-day repeat) | `find_owner`, `find_contact` | `$0.09` |
| Deep cited company investigation (`$0.00` polling) | `research_company`, `get_research` | `$0.50` |
| Outreach by Avery (up to 150 owners/month self-serve) | `avery_reach_out` / `avery reach-out --yes` | `$0.02` / email |
| Accepted double-opt-in Warm Yes owner introduction | `avery_accept_intro` / `avery accept-intro --yes` | `$25.00` |

**Enterprise:** Want Dealport's team to run origination end-to-end (searches, Playbooks, custom domains, campaigns, pipeline, and CRM sync)? Talk to Dealport at `https://dealport.com`.
