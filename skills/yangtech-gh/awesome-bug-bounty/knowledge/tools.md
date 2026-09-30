# Tooling Notes

> Installing any tool below? Copy-paste commands live in **`knowledge/install.md`**.

## Tool choice matrix

| Need | Pick | Why |
|---|---|---|
| Manual proxy/replay (default hunting loop) | **Caido** (free tier, multi-project) or Burp Community | Caido: faster, HTTPQL, Workflows, AI plugins; Burp: extension ecosystem (Autorize, JWT Editor, Param Miner) |
| Automated active scan + OAST (blind SSRF/XXE) | Burp Pro Scanner / **ZAP** + nuclei | Burp Collaborator ≈ ZAP OAST; Caido has no Collaborator equivalent yet |
| Known-CVE / misconfig sweep at scale | **nuclei** + custom templates | Template DSL, CI-native, 11k+ community templates |
| Authz (IDOR/BFLA) replay | AutorizePro / BurpAPISecuritySuite Auth Replay / Caido plugins | Low-priv headers vs high-priv session |
| Business-logic heuristics | bizlogic + manual state machines | Heuristic crawl → 9 checks → safe exploit |
| JS-heavy / SPA rendering, agent-driven browsing | **Obscura** (CDP/MCP headless browser) | See "Obscura" section below |
| Agent-run recon/scans from chat | MCP stack (HexStrike, pd-tools-mcp, mcp-bb, BugHound-MCP) | See "MCP tool stack" |
| Autonomous end-to-end hunt w/ proof | Evidence-first hunters (VERDICT, ptai, AI Scanner…) | See "AI-native hunters" — oracle-verified only |
| Programmable interception in scripts/CI | mitmproxy (Python API) | Transform traffic as code |

Rule: **proxy (Caido/Burp/ZAP) for interactive depth → nuclei for breadth → AI hunters for orchestration/triage → always human-verify before reporting.**

## Burp Suite alternatives (2026)

### Caido — modern manual-testing default
- Rust backend + browser UI; Intercept, HTTP History, Replay, Automate (Intruder-equivalent), node-based **Workflows**, HTTPQL filtering. Free **Basic tier with multi-project** (Burp Community = single project, no extensions).
- **AI-native angle (Burp is not):** official **Client SDK + AI Skill** (`github.com/caido/skills`) lets AI agents drive replay sessions, findings, request editing programmatically with low token use; **Shift** plugin (`caido-community/shift`) adds LLM free-form request modification in-UI + micro-agent framework (XSS, WAF bypass…). Human-in-the-loop: agent artifacts appear in Replay/Findings for manual verification.
- Gaps vs Burp Pro: no full automated Scanner, no Collaborator/OAST, smaller plugin store. Migration map: `docs.caido.io/burp-suite`.
- Fit: bug bounty hunters and agents wanting a fast proxy + programmatic access over Burp's scanner depth.

### OWASP ZAP — free full DAST
- Intercepting proxy + active/passive scan, fuzzer, spider, add-on marketplace, **YAML Automation Framework** for CI/CD, REST API, Docker. Checkmarx-maintained, fully open source. Best zero-cost Burp Pro substitute for automated scanning; UI dated, FP tuning needed.

### Others
- **mitmproxy** — programmable interception (Python addons), console/web UI; ideal for scripted traffic rewriting and agent pipelines.
- **Nuclei** — not a proxy; the template-scan lane used alongside any proxy (Burp/Caido/ZAP).
- Commercial (context only): Invicti/Acunetix (proof-based), StackHawk (CI ZAP wrapper), Dastardly (PortSwigger free CI scanner).
- **When Burp still wins:** BApp ecosystem (AutorizePro, Turbo Intruder, Param Miner, JWT Editor), Scanner maturity, Collaborator OAST. Strategy: Caido/ZAP as daily driver + Burp (or extensions headless) where the ecosystem is required.

## Obscura (`h4ckf0r0day/obscura`) — where it fits

**What it is:** open-source headless browser engine in Rust (V8 via deno_core, CDP server) — a drop-in for headless Chrome with Puppeteer/Playwright, plus a native **MCP server** (`obscura mcp`). ~30 MB memory, instant startup, built-in stealth (TLS ClientHello randomization, tracker blocklist), `--stealth` mode, per-page V8 watchdogs. Not a proxy and not a scanner.

**Fit in the hunt:**
1. **Recon/crawl of JS SPAs** — `obscura fetch` / `obscura scrape` for rendering routes, harvesting network requests (`browser_network_requests`), console messages, and JS-extracted endpoints where katana/gau see nothing.
2. **Agent-driven browsing via MCP** — tools like `browser_navigate`, `browser_click`, `browser_fill`, `browser_evaluate`, `browser_wait_for`: ideal for authenticated multi-step flows, wizard/workflow business-logic mapping, CSRF/state collection.
3. **DOM XSS / postMessage / iframe work** — child frames get their own V8 realm; `browser_evaluate` executes payloads in-page to confirm execution (report only on real execution).
4. **Lightweight CI/triage automation** — no Chrome/Node dependency; point existing Playwright/Puppeteer scripts at `obscura serve` (CDP WebSocket).
5. **Stealth recon** — `--stealth` for bot-check/bot-defense targets (still authorized scope only; robots-obeying flag exists).

**When to prefer Playwright/Chrome instead:** full extension ecosystem, perfect rendering parity, file-upload flows (Obscura gates file access behind `--allow-file-access`), or when the target's bot detection specifically fingerprints Obscura. Pair Obscura with a proxy (Caido/Burp) when you need to intercept/mutate requests — browser drives, proxy records.

## AI-native autonomous hunters (Burp-adjacent, evidence-first)

Selection criterion: prefer tools where **findings are oracle/execution-verified** (exploit fires, replay reproduces) over LLM self-judged verdicts.

| Tool | Model | Distinguishing property |
|---|---|---|
| **farnaboldi/ai-scanner** (Burp extension) | LLM discovery + **deterministic oracles** | "No oracle, no issue" — zero-FP by construction; works on Burp Community (own probes) or Pro; local/OpenAI-compatible LLM; SAST→DAST source-assisted mode; LLM-app testing (prompt-injection canaries) |
| **vvts-alpha/VERDICT** | Claude-led staged agent | Evidence-gated `confirmed` (failing control + ≥2 replays); behind-login (Bearer propagation + Burp audit-ext on :1338 passes *authenticated* request to Burp); OpenAPI spec-driven assessment; AI depth × Burp breadth merge |
| **0xSteph/pentest-ai (ptai)** | LLM coordinates, probes decide | 63 probes / 23 named machine oracles; findings as replayable **proof capsules**; MCP path needs no API key (drives Claude Code/Cursor); `--no-llm` deterministic mode; SARIF CI gate on verified only |
| **k3rth1/xalgorix** | BYO-LLM autonomous agent | 22-phase methodology + **independent verifier** re-exploits every finding; self-hosted; CVSS + PDF reports; free GitHub App for PR review |
| **oz9un/AOBTD** | Specialist LLM agents + verifier | MITM-proxy extraction (no LLM) → auth/injection/access/chain reasoners → black-box verifier probes; zero-LLM fallback path |
| **Christbowel/siphon** | Dual-track: local LLM + script scanners | Fully local (no API keys); cross-endpoint memory; hypothesis-driven biz-logic; findings cross-validated |
| **h4ckologic/bughunter-ai** | 20 Claude Code agents, state machine | Burp Suite MCP integration, credential vault, LLM security track |
| **Awarexone/Agentic-Bug-Hunter** | Claude Code plugin / standalone CLI | 33 commands, 9 agents; 7-Question validation gate; submission-ready reports (H1/Bugcrowd/Intigriti/Immunefi); MCP: Burp · Caido · HackerOne |
| **0x0pointer/agent-smith** | Skill-chained prompts (BYO LLM) | Augmented (human-steered) vs autonomous; Docker-sandboxed tools; adjudication gate + OOB confirmation; Burp-ready `.http` PoCs |
| **4dw1tz/Pulse** | LangGraph orchestration | Tool-per-agent (sqlmap, dalfox, semgrep, trufflehog…) → LLM attack-chain graph (MITRE-aligned) → Markdown report |

Also known (reference): PentestGPT (suggests, no execution), CAI, PentAGI, Strix, Shannon, HexStrike (broad tool-wrapper MCP, weaker verification). Benchmarks vs ptai/HexStrike/ZAP/Nuclei are public — treat vendor numbers as directional.

## MCP tool stack (agent-executable recon & scanning)

Wire one into opencode as an MCP server to give the agent hands:

| Server | Scope | Notes |
|---|---|---|
| **0x4m4/hexstrike-ai** | 150+ tools, 12+ agents | Network/web/binary/cloud; FastMCP; broadest wrapper layer |
| **intelligent-ears/pd-tools-mcp** | subfinder, dnsx, naabu, httpx, katana, nuclei | Clean ProjectDiscovery-only surface; `bug_hunting_workflow` |
| **narkytypey/mcp_bug (mcp-bb)** | 60+ tools in Go | **Strict scope enforcement** (program profiles), rate limits, audit JSONL — safest default for bounty work |
| **binderlabs/BugHound-MCP** | 7-stage pipeline, 45 techniques | 29 pure-Python (zero external deps); auth-aware JWT propagation; HTML reports; Black Hat Arsenal Asia 2026 |
| **Moonwuk/MoonMCP** | 166 tools, stdlib-first | Works with zero binaries installed; scope guard on every active tool; SARIF export; persistent knowledge-graph memory |
| **nedlir/mcpwner** | 55+ containerized tools | Findings ledger, PoC sandbox with deterministic oracles ("no exploit, no report"); SAST+SCA+DAST+fuzz |
| **FuzzingLabs/mcp-security-hub** | 38 Dockerized MCP servers | 300+ tools incl. nmap, nuclei, sqlmap, ghidra; compose orchestration |
| **akinabudu/bug-bounty-mcp** | 28+ tools | H1/Bugcrowd/Intigriti/YesWeHack scope validation, caching, audit trail |

## Testing MCP/LLM apps — new bounty surface

Programs increasingly scope **AI features, MCP servers, and LLM integrations**. Tooling:

| Tool | Use |
|---|---|
| **sahiloj/MCPScan** | Offensive auditor: tool poisoning, credential leak, overprivilege, SSRF, RCE vectors, supply chain; SARIF; CVE-2025-6514 etc. |
| **mcpsec** | Live protocol fuzzer + static audit (3,450 sink patterns, 149 Semgrep rules); proves runtime exploitability (past CVEs in radare2-mcp, mobile-mcp) |
| **D0rs4n/mcpwn** | Enum/call MCP servers over stdio/HTTP/SSE; route through Burp; sqlmap bridge for injectable tool args |
| **babywyrm/mcpnuke** | Static + behavioral probing, 100 checks; `--no-invoke` safe mode; DVMCP walkthrough |
| **peter-hendy/mcp-server-scanner-extension** | Burp Pro extension: MCP discovery → active/passive audits (auth bypass, path traversal, OAuth SSRF, Collaborator RCE) |
| **AI Scanner (above)** | Prompt-injection / system-prompt disclosure / tool-abuse canaries over multi-step agent flows |

Hunt classes: prompt injection (direct/indirect), system-prompt leak, tool poisoning/over-permission, MCP auth bypass, SSRF via resource URIs, excessive agency (side-effect chains), model DoS. Payloads: `knowledge/payloads.md` + OWASP LLM Top 10 / OWASP MCP guidance.

## AutorizePro (WuliRuler/AutorizePro)

Burp extension for **authorization enforcement** testing with optional AI triage.

- **Setup**: Burp → Extender → Python env → Jython standalone JAR → Add extension `AutorizePro.py` (no non-ASCII in path).
- **Use**:
  1. Configuration tab → paste low-privilege (2nd account) auth headers into "Insert injected header here".
  2. Optional: uncheck "Check unauthenticated" to skip cookieless tests.
  3. Optional AI: default API or custom OpenAI-compatible endpoint (e.g. Ollama `http://localhost:11434/v1/chat/completions`) + "Enable AI".
  4. Toggle AutorizePro on; browse target with high-priv session.
- **Statuses**: `Bypassed!` (authz fail — red), `Enforced!` (ok — green), `Is enforced???` (configure enforcement detector rules).
- **Filters**: Interception Filters (blacklist/whitelist/regex/Burp scope) — **always scope to target** to avoid cookie leakage and AI cost.
- **Safety**: AI only runs on status-equal JSON responses (length 50–6000); export HTML/CSV reports; logs show AI reasoning per request.
- **Caido path:** Caido's SDK/skill + plugins cover equivalent auth-replay workflows when you've left Burp.

## BurpAPISecuritySuite (Teycir/BurpAPISecuritySuite)

All-in-one Burp suite for **API recon, fuzzing, and AI-assisted triage** (15 attack types, 108+ payloads).

- **Install**: Burp → Extensions → Add → Python → `BurpAPISecuritySuite.py` (Community or Pro + Jython).
- **Workflow**: capture traffic (Recon auto-capture) → review normalized endpoints → optional Passive Discovery (differentials, token lineage, parity drift, abuse chains) → Export AI Bundle → LLM triage.
- **Key tabs**:
  - **Recon**: smart endpoint grouping, noise filter, Export AI Bundle, Refresh Invariants.
  - **Auth Replay**: guest/user/admin header profiles → replay + severity ranking (BOLA triage).
  - **Fuzzer**: 15 attack types (BOLA, IDOR, SQLi, XSS, SSTI, JWT, GraphQL, race, business logic, WAF bypass…) → Intruder/Turbo/cURL/JSON export.
  - **Discovery**: Version Scanner (v1/v2/dev/legacy), Param Miner (admin/debug params), Wayback, Katana, HTTPX, FFUF, Kiterunner, ApiHunter.
  - **Verify**: SQLMap verify, Dalfox verify for candidates.
  - **Sensitive Data**: regex packs for secrets/PII/credentials/infra exposure.
- **Integrations**: Nuclei (with GraphQL templates), subfinder/dnsx, export to Intruder positions, Postman, Insomnia.

## bizlogic (ekomsSavior/bizlogic)

Heuristic **business-logic scanner** (Python, no heavy deps: `requests` + `beautifulsoup4`).

```bash
git clone https://github.com/ekomsSavior/bizlogic && cd bizlogic
pip install requests beautifulsoup4
python bizlogic_scanner.py
# prompts: base URL, rate (default 0.5s), max pages (default 50)
```

- Phases: discovery (crawl, robots/sitemaps/OpenAPI) → auth detection → 9 heuristic checks → optional controlled exploitation (max 5 attempts/finding, 1.0s rate, non-destructive).
- Outputs: `reports/scan_[domain]_[timestamp]/` with text, JSON, HTML, Nuclei templates.
- Detection categories: ownership/transfer, alternate-channel authz, user-controlled keys, weak recovery, wrong ownership, unlimited allocation, premature release, single-action flaws, client-side workflow.

## Complementary stack (from PayloadsAllTheThings / aw-junaid)

| Phase | Tools |
|---|---|
| Subdomains | subfinder, amass, assetfinder, crt.sh |
| Probe | httpx, dnsx |
| Crawl/URLs | katana, gau, waybackurls, hakrawler · **Obscura** for JS-rendered surface |
| Content fuzz | ffuf, gobuster, feroxbuster |
| API routes | kiterunner, ApiHunter, LinkFinder |
| Vuln scan | nuclei (custom templates) |
| SQLi/XSS verify | sqlmap, dalfox |
| Race | Turbo Intruder, Burp Suite concurrent tab, Caido Automate |
| Authz | AutorizePro, BurpAPISecuritySuite Auth Replay |
| Secrets | trufflehog, gitleaks, git-dumper |
| Logic | bizlogic + manual state-machine mapping |
| Orchestration | MCP servers above · evidence-first AI hunters |
| MCP/LLM targets | MCPScan, mcpsec, mcpwn, AI Scanner |
| Tool indexes | vavkamil/awesome-bugbounty-tools (incl. AI Agents section) |
