---
name: awesome-bug-bounty
description: Use when doing bug bounty hunting, vulnerability research, security report writing/analysis, payload or WAF-bypass selection, business logic / IDOR / race / API testing, recon methodology, tool choice (Burp vs Caido vs ZAP, AI pentest agents, MCP security testing, headless browsers), or looking up writeups/programs — e.g. "find XSS payload", "business logic checklist", "SSRF bypass", "HackerOne top reports", "bug bounty methodology", "which tools to install". Merges curated knowledge with source-repo fallbacks; authorized testing only.
license: MIT
---

# Awesome Bug Bounty

Distilled knowledge base for bug bounty hunting and authorized security research. **Paths below are relative to this skill's directory.** Prefer them; only fetch source repos (Fallback table) when deeper detail is needed.

## Operating rules

1. Read extended detail from `knowledge/*.md` before improvising:
   - `knowledge/vuln-types.md` — per-vuln hunt focus + example patterns
   - `knowledge/payloads.md` — payload/bypass cheat sheet by context
   - `knowledge/business-logic.md` — business logic + race condition playbooks
   - `knowledge/methodology.md` — recon/API methodology, best practices, non-duplicated engagement path, report template, wordlists
   - `knowledge/tools.md` — tool-choice matrix: proxies, AI-native hunters, Obscura, MCP stack, authz/API/bizlogic tools
   - `knowledge/install.md` — install commands + post-install setup (API keys, proxy CA, MCP registration)
2. For writeup links, full payload lists, or tool internals: fall back to source repos via registered opencode references (`@awesome-bb-writeups`, `@bug-bounty-reference`, `@payloads-all-the-things`, `@hack-skills`, `@bizlogic`, `@aw-junaid-bug-bounty`, `@hackerone-reports`, `@autorizepro`, `@burp-api-security-suite`, `@awesome-bugbounty-tools`, `@obscura`, `@caido-skills`) or the Fallback table URLs. If a reference isn't registered, use the GitHub URL.
3. **Authorized testing only.** Stay inside program scope and rules of engagement.
4. Evidence standard for reports: clear impact, minimal repro steps, PoC request-response, severity justification, fix guidance.

## Operating profile gate (ask before acting)

**When:** at the first action-taking turn of a session/engagement — **skip entirely** if the user already stated preferences/rules in this conversation, or if `engagements/<target>/profile.yaml` (or an equivalent profile the user pointed to) already exists. Never re-ask within a session after answers are given.

**How:** ask **once**, using the `question` tool, a single question:

> **"Operating profile for this engagement?"**
> - `Defaults — Stealth (Recommended)` — in-place/Ollama LLM, no cloud keys, recon + verify layers, install core, MCP: pd-tools & obscura. Applied immediately, no further prompts.
> - `Configure…` — answer the full set below (one `question` call, all items together).

Full set (only when `Configure…`):

1. **Mode** — `Stealth / no API keys (Recommended)` (local/offline tools only; `HEXSTRIKE_API_KEY` and proxy CA are local auth, allowed) · `Balanced` (in-place LLM + read-only keys like `GITHUB_TOKEN`, no paid LLM APIs) · `Full` (cloud API keys per tool)
2. **LLM backend** — `In-place (opencode session model)` · `Ollama (http://localhost:11434/v1)` · `Cloud API keys` · `None — deterministic only`
3. **Tool layers** (multiple) — `Proxy (Burp/Caido/ZAP)` · `Recon stack` · `Verify (sqlmap/dalfox/interactsh)` · `Obscura browser` · `bizlogic` · `AI hunter` · `MCP/LLM-offensive suite`
4. **Install policy** — `Install core now` · `Install only what this engagement needs` · `Don't install — report gaps only`
5. **MCP surface** (multiple) — `pd-tools` · `hexstrike` · `obscura` · `ptai` · `mcp-bb` · `none`

**After answers:** write them to `engagements/<target>/profile.yaml` (keys: `mode`, `llm`, `layers[]`, `install`, `mcp[]`; env names only, never secrets), then obey for the rest of the engagement:

| Profile choice | Enforced behavior |
|---|---|
| Mode `Stealth` | Never suggest/export cloud API keys; Caido AI plugins, Burp AI, AutorizePro AI **off** unless backend = Ollama; prefer offline/zero-dep tools (`nuclei -duc`, gau/wayback passive); hexstrike/Obscura only as **local stdio** MCP; active scanning rate-capped |
| Mode `Balanced` | In-place/Ollama only for LLM; read-only GitHub PAT allowed; no paid API suggest |
| Mode `Full` | Per-tool keys from `knowledge/install.md` §11 as needed; AI hunters may use cloud LLMs |
| LLM `In-place` | All AI features pointed at the session agent — zero key setup |
| LLM `Ollama` | Point tools at `http://localhost:11434/v1`; verify reachable before starting |
| LLM `None` | Deterministic only: `ptai --no-llm`, no AI triage steps in playbooks |
| Layer unchecked | Do not install, run, or mention that layer as a next step this engagement |
| Install `Don't install` | Health-check and report gaps (`knowledge/install.md` §10); never run install commands |
| MCP `none` / unchecked | Leave servers `enabled: false` in `opencode.jsonc`; drive tools via shell instead |

Declining the gate or saying "use defaults" = **Defaults / Stealth** above, recorded without further prompting.

## Engage flow (impact-first)

0. **Profile gate** — once per engagement as above; persist `profile.yaml`; all later steps obey it.
1. **Scope** — write the scope manifest (`knowledge/methodology.md` → non-duplicated path): in-scope hosts, exclusions, rate limits, test windows. Every tool consumes this one file.
2. **Recon / attack-surface map** — single deduped workspace: assets → live hosts → site/API/auth surfaces (union + `uro`/`sort -u`, no per-tool re-enumeration); render SPAs with Obscura/Playwright; note in-scope MCP/LLM features.
3. **Route by surface** — highest-impact path first (auth bypass > ATO > RCE > SSRF/IDOR > XSS > info leaks).
4. **Deep playbooks** — read matching `knowledge/*.md` section; escalate to fallback repos only if uncovered. Fan-out tools **read** the shared surfaces, never re-scan them.
5. **Report** — dedupe findings by `METHOD+host+path+param+class`; impact-first writeup per template; one submission per issue.

## Category router (symptom → knowledge → fallback)

| Symptom / surface | Knowledge | Primary fallback |
|---|---|---|
| XSS, SQLi, SSTI, RCE, LFI/upload, SSRF, CSRF/CORS, smuggling, takeover, cache, host header, 401/403, SAML, most vuln classes | `knowledge/vuln-types.md` (+ `knowledge/payloads.md` for injection/WAF contexts) | PayloadsAllTheThings, Awesome-Bugbounty-Writeups, bug-bounty-reference, hackerone-reports `docs/tops_*` |
| IDOR/BOLA, API recon, GraphQL, mass assignment | `knowledge/vuln-types.md`, `knowledge/methodology.md`, `knowledge/tools.md` | AutorizePro, BurpAPISecuritySuite, hack-skills api-sec |
| Auth bypass, 2FA/MFA, OAuth/JWT, ATO | `knowledge/vuln-types.md` | bug-bounty-reference, hack-skills auth-sec |
| Business logic, race conditions | `knowledge/business-logic.md` | hack-skills, bizlogic, PayloadsAllTheThings, hackerone-reports TOPRACECONDITION |
| Recon, wordlists, engagement workspace, report template, SPA browsing | `knowledge/methodology.md` + `knowledge/tools.md` (Obscura) | aw-junaid/bug-bounty, obscura |
| Proxy / scanner / AI hunter / MCP tool choice, agent orchestration | `knowledge/tools.md` | awesome-bugbounty-tools, caido-skills, hexstrike-ai, pd-tools-mcp |
| Install commands, API keys, proxy CA, MCP registration | `knowledge/install.md` | upstream repo README |
| Mode / LLM / layers / MCP enablement | Operating profile gate → `profile.yaml` | `knowledge/install.md` §11–12 |
| MCP server or LLM app testing (prompt injection, tool poisoning) | `knowledge/tools.md`, `knowledge/payloads.md` | MCPScan, mcpsec, mcpwn, AI Scanner |

Covered classes are indexed in `knowledge/vuln-types.md` (XSS → MCP abuse).

## Fallback repositories

| Reference alias | Repository | Role |
|---|---|---|
| `@awesome-bb-writeups` | [devanshbatham/Awesome-Bugbounty-Writeups](https://github.com/devanshbatham/Awesome-Bugbounty-Writeups) | Writeups indexed by bug type |
| `@bug-bounty-reference` | [ngalongc/bug-bounty-reference](https://github.com/ngalongc/bug-bounty-reference) | Writeups by bug nature (XSSI, OAuth, money, business logic) |
| `@payloads-all-the-things` | [swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) | 64+ vuln categories: payloads, bypasses, methodology |
| `@hack-skills` | [yaklang/hack-skills](https://github.com/yaklang/hack-skills) | 100+ agent skills; master/category routers |
| `@bizlogic` | [ekomsSavior/bizlogic](https://github.com/ekomsSavior/bizlogic) | Business-logic heuristic scanner (9 checks) |
| `@aw-junaid-bug-bounty` | [aw-junaid/bug-bounty](https://github.com/aw-junaid/bug-bounty) | Methodologies, cheatsheets, wordlists, report templates |
| `@hackerone-reports` | [reddelexc/hackerone-reports](https://github.com/reddelexc/hackerone-reports) | Top disclosed HackerOne reports by bug type + program |
| `@autorizepro` | [WuliRuler/AutorizePro](https://github.com/WuliRuler/AutorizePro) | Burp authz-enforcement tester + AI FP reduction |
| `@burp-api-security-suite` | [Teycir/BurpAPISecuritySuite](https://github.com/Teycir/BurpAPISecuritySuite) | Burp API suite: recon, 15 attack types, BOLA/IDOR |
| `@awesome-bugbounty-tools` | [vavkamil/awesome-bugbounty-tools](https://github.com/vavkamil/awesome-bugbounty-tools) | Curated tool index by phase (incl. AI Agents) |
| `@obscura` | [h4ckf0r0day/obscura](https://github.com/h4ckf0r0day/obscura) | Rust headless browser for AI agents: CDP + MCP, stealth, SPA rendering |
| `@caido-skills` | [caido/skills](https://github.com/caido/skills) | Caido Client SDK + AI skill (AI-native Burp alternative) |

Deep research: fetch the corresponding reference path (e.g. `@payloads-all-the-things` → `SQL Injection/README.md`) rather than guessing payloads.
