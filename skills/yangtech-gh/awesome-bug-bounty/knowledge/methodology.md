# Methodology, Recon & Reporting

Distilled from aw-junaid/bug-bounty methodologies/cheatsheets and hack-skills recon/api-sec routers.

## Recon pipeline

1. **Asset discovery**
   - Subdomains: subfinder, assetfinder, amass, crt.sh, DNS brute (ffuf -w wordlist).
   - Probing: httpx (status, tech detect, titles), dnsx.
   - Takeover check: nuclei subdomain-takeover templates / can-i-take-over-xyz.
2. **Content discovery**
   - URLs: katana, gau, waybackurls, hakrawler; merge + dedupe.
   - Directories/files: ffuf/gobuster with seclists/common + backup extensions (`.bak`, `.old`, `~`).
   - APIs: kiterunner, ApiHunter, OpenAPI/Swagger/GQL introspection, JS file endpoint extraction (LinkFinder/knockpy).
   - JS-rendered SPAs: render with **Obscura** (`obscura scrape` / MCP `browser_*` tools) or Playwright; harvest `browser_network_requests` + console for hidden endpoints (see `tools.md`).
3. **Secrets & exposure**
   - GitHub/gitlab secret scanning (trufflehog, gitleaks), `.git`/`.env`/`.DS_Store`, backup files, npm/pip package leaks, dependency confusion checks.
4. **Tech fingerprint**: Wappalyzer/httpx tech, framework-specific defaults (Flask debug, Spring actuators, Jenkins, Tomcat manager).
5. **Auth surface mapping**: login, SSO/SAML/OIDC providers, password reset flows, 2FA enrollment, API keys in JS.

## Prioritization (impact first)

```
RCE / SQLi (data dump) > Auth bypass / ATO > SSRF (cloud metadata) >
IDOR (PII/mass data) > Stored XSS (admin) > Business logic (money) >
Race limits > CSRF/CORS/open redirect > Info disclosure > Low-impact XSS
```

## API testing notes

- Discover: OpenAPI (`/swagger.json`, `/openapi.yaml`), GraphQL `/graphql` introspection, mobile backend certs.
- Test: BOLA (swap object IDs across roles), BFLA (function-level: admin endpoint with user token), mass assignment (send `role`, `is_admin`, `user_id`), rate limits (bomb one endpoint), pagination abuse (`limit=-1` or huge), JWT/API-key hygiene in transit + logs.
- GraphQL: introspection off? batching, depth/complexity DoS, IDOR on global IDs, mutation authz.

## Best practices

**Scope & safety**
1. Write a **scope manifest first** (in-scope hosts, exclusions, rate limits, test windows) — every tool consumes it; nothing runs unscoped (mcp-bb/MoonMCP/BugHound enforce this in-tool).
2. Passive → cheap-active → intrusive, in that order. Never open with fuzzing or sqlmap `--risk 2` against production.
3. Rate-limit everything (`nuclei -rl`, ffuf `-p`, custom sleep). Stop on destructive findings (data write, DoS, account lockout) and report privately.
4. Keys stay in env, PAT is read-only, PoCs are redacted (cookies, tokens, PII) before any share.

**Evidence-first**
5. A finding is a **candidate until reproduced**: request/response PoC + stable replay (≥2×) + impact statement. Prefer oracle-verified tooling (`tools.md` AI-native table) over LLM self-judged verdicts.
6. Deduplicate **before** writing the report (see path below) — one issue = one submission, worst-case severity path shown once.
7. Severity: program rubric first, CVSS v3.1 fallback; state *why* impact is what you claim (data class, who can act).

**Tool hygiene**
8. One engagement workspace per target (below); artifacts are regenerable — keep only inventories, findings, PoCs.
9. Minimize MCP surface: 1 recon server + Obscura default; scope-enforced servers first (`install.md` §12).
10. Human-in-the-loop: agents propose, you verify in the proxy UI (Caido Replay / Burp) before submission.
11. Platform hygiene: check recent disclosures/dupes on the program page first; respect disclosure timelines; never test across a shared backend outside scope even if DNS is in-scope.

## Non-duplicated engagement path (platform → app → site → API)

Run **one pipeline per program**, not one per tool. Every stage writes to a single workspace; each stage consumes the previous stage's deduped output — so subfinder never re-finds what crt.sh already produced, and the API fuzzer never re-fuzzes URLs katana already covered.

```
program (platform)
  └─ scope manifest            ← 1 file: hosts, wildcards, exclusions, rates, accounts
       └─ asset inventory      ← 1 file: uniq subdomains/domains (in-scope filter applied ONCE)
            └─ live hosts      ← 1 file: httpx-probed (status, tech, title)
                 ├─ site surface   ← 1 file: uniq URLs+params (gau ∪ katana ∪ wayback ∪ JS ∪ Obscura ∪ dirscan)
                 ├─ API surface    ← 1 file: endpoints+specs (OpenAPI/GQL/kiterunner ∪ JS-harvest ∪ proxy traffic)
                 └─ auth surface   ← 1 file: roles/sessions (low + high priv headers)
                      └─ test fan-out (each tool reads the SAME files, writes findings/)
                           └─ finding dedup → verify → 1 report per issue → submit once
```

**Workspace layout**

```
engagements/<program>/
├── scope.yaml                 # manifest: include/exclude, rate, notes, accounts
├── assets/subs.txt            # sorted uniq, in-scope only
├── assets/live.txt            # httpx output
├── surfaces/urls.txt          # merged, normalized, uniq URL+param corpus
├── surfaces/api.txt           # API endpoints / spec paths
├── surfaces/auth.json         # low-priv + high-priv sessions, roles
├── findings/raw/              # per-tool output (nuclei, sqlmap, …) — kept, not submitted
├── findings/deduped.md        # canonical list, one entry per real issue
└── reports/                   # final submissions
```

**Dedup mechanics (copy-paste)**

```bash
# 1) Assets: merge sources, normalize, keep only scope
cat from_pd.txt from_crtsh.txt from_wayback.txt | sed 's/^\*\.//' | sort -u > assets/all.txt
# filter to scope (wildcard + excludes) — example with grep; or use httpx -ild
grep -E '^(.*\.)?target\.com$' assets/all.txt | sort -u > assets/subs.txt

# 2) Live hosts once — every later stage reads live.txt
httpx -l assets/subs.txt -sc -title -tech-detect -o assets/live.txt

# 3) Site surface: union all URL sources, normalize, dedupe
gau --subs target.com > surfaces/gau.txt &
katana -l assets/live.txt -o surfaces/katana.txt &
waybackurls target.com > surfaces/wb.txt &
wait
cat surfaces/gau.txt surfaces/katana.txt surfaces/wb.txt surfaces/js.txt surfaces/obscura.txt \
  | uro | sort -u > surfaces/urls.txt        # uro dedupes paths; grep -vE exclusions after

# 4) API surface: specs + harvested paths (already unique by construction)
cat surfaces/openapi_paths.txt surfaces/gql_fields.txt surfaces/kiterunner.txt surfaces/js_endpoints.txt \
  | sort -u > surfaces/api.txt

# 5) Test fan-out — tools READ surfaces, never re-enumerate
nuclei -l surfaces/urls.txt -severity critical,high -rl 100 -o findings/raw/nuclei.txt
dalfox file surfaces/urls.txt -o findings/raw/dalfox.txt          # only param'd URLs
ffuf -u https://host/FUZZ -w seclists/... -of json                # only paths NOT already in urls.txt

# 6) Finding dedup key before reporting: METHOD + host + path + param + vuln-class
#    (normalize: strip query values, lowercase host, collapse ids → :id)
sort -u findings/raw/* | ... > findings/deduped.md   # or use nuclei JSON → jq group_by(.info.name)
```

**Cross-platform rule (site/app/API overlap):** many programs share backends (app + API + marketing site on one org). Build the inventory **once per program**, tag each asset with `surface: web|api|app`, and test each asset once — don't re-run the pipeline per platform listing (HackerOne/Bugcrowd scope files can be merged into one `scope.yaml` when the legal entity and rules match; keep separate workspaces when ROE differs).

**Skip-lists to avoid re-work:** persist `surfaces/urls.txt` + `findings/deduped.md`; before any new scan session, subtract already-tested paths (`grep -v -F -f findings/tested_paths.txt`). Re-run only **delta** (new subs, new URLs) on subsequent days: `comm -13 old/urls.txt new/urls.txt`.

## Report template

```markdown
# Title: [Vuln type] in [endpoint/feature] leading to [impact]

## Summary
One paragraph: what, where, impact.

## Severity
[CVSS or program rubric] — justification.

## Affected endpoint(s)
- METHOD https://host/path (param names)

## Steps to reproduce
1. ...
2. ...

## Proof of concept
Request/response (redact secrets). Screenshots if UI.

## Impact
Who/what is affected; data or action demonstrated (minimal).

## Remediation
Server-side check, authz fix, rate limit, etc.

## References
OWASP/CWE/writeup links.
```

## Cheatsheet command anchors

- ffuf dir: `ffuf -u https://t/FUZZ -w seclists/Discovery/Web-Content/common.txt -mc 200,301,403,500`
- ffuf vhosts: `ffuf -u https://t -H "Host: FUZZ.t" -w subdomains.txt`
- nuclei: `nuclei -u https://t -severity critical,high -rl 100`
- httpx: `cat subs.txt | httpx -sc -title -tech-detect`
- sqlmap: `sqlmap -u 'https://t/?id=1' --batch --level 3 --risk 2`
- dalfox: `dalfox url 'https://t/?q=x' --pipe`
- cookie auth replay: copy low-priv session → Burp Autorize / Suite Auth Replay.

## Wordlists (in aw-junaid/bug-bounty resources)

- `custom-subdomains.txt` — curated subdomains for asset discovery.
- `directories-small.txt` — compact directory fuzz list.
- `xss-payloads.txt` — XSS collection for filter bypass.

## Safety

Only test assets in program scope. Respect rate limits and ROE. Stop on destructive findings and report privately.
