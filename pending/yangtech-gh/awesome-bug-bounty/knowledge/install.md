# Install Guide

Copy-paste install commands for every tool referenced by this skill. Conventions:

- **`go` tools** → `$GOPATH/bin` or `~/go/bin` — ensure it's on `PATH`.
- **`→ repo README`** = multi-step/uncertain build; follow the upstream quick-start rather than guessing.
- **Authorized testing only** — install ≠ permission to run against targets.
- **Respect the profile gate** (SKILL.md): if the user chose Stealth/`Don't install`/specific layers, only run the sections that match their `profile.yaml` — don't install or configure unchecked layers, and never export cloud API keys under Stealth.

Check what's installed: `command -v <tool>` or see `bb.env.check_dependencies` / `ptai tools install` / BugHound `check_tool_coverage` if using an MCP/agent harness.

## 0. Prerequisites

```bash
# Go (most recon tools) — https://go.dev/dl/
go version

# Build base (Debian/Ubuntu/Kali)
sudo apt update && sudo apt install -y git curl jq unzip python3-pip pipx nmap

# Optional: Homebrew (macOS/Linux) — https://brew.sh
# Optional: Rust (cargo installs) — https://rustup.rs
```

## 1. Recon & probing (ProjectDiscovery + classics)

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/uncover/cmd/uncover@latest
go install -v github.com/projectdiscovery/tlsx/cmd/tlsx@latest

go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/tomnomnom/waybackurls@latest
go install -v github.com/tomnomnom/gf@latest
go install -v github.com/tomnomnom/qsreplace@latest
go install -v github.com/tomnomnom/anew@latest
go install -v github.com/lc/gau/v2/cmd/gau@latest
go install -v github.com/sensepost/gowitness@latest
go install -v github.com/Josue87/gotator@latest
go install -v github.com/d3mondev/puredns/v2@latest
go install -v github.com/ffuf/ffuf/v2@latest

# Amass (large)
sudo snap install amass            # or: brew install amass

# Fuzzing / content
sudo apt install -y gobuster feroxbuster
pipx install arjun
pipx install paramspider
pipx install wafw00f
pipx install uro              # URL dedupe (non-duplicated path)
pipx install httpie   # optional manual requests

# Crawl helpers (small go scripts)
go install -v github.com/hakluke/hakrawler@latest

# Nuclei templates
nuclei -update-templates
```

**Wordlists:**

```bash
git clone --depth 1 https://github.com/danielmiessler/SecLists.git ~/wordlists/SecLists
git clone --depth 1 https://github.com/swisskyrepo/PayloadsAllTheThings.git ~/wordlists/PayloadsAllTheThings
git clone --depth 1 https://github.com/aw-junaid/bug-bounty.git ~/wordlists/aw-junaid-bug-bounty
```

## 2. Verification & secrets

```bash
# SQLi
sudo apt install -y sqlmap          # or: git clone https://github.com/sqlmapproject/sqlmap && python3 sqlmap/sqlmap.py

# XSS
go install -v github.com/hahwul/dalfox/v2@latest

# Secrets / git exposure
go install -v github.com/trufflesecurity/trufflehog/v3@latest
go install -v github.com/gitleaks/gitleaks/v8@latest
# git-dumper: pipx install git-dumper

# DNS/OAST (blind SSRF/XXE callbacks)
go install -v github.com/projectdiscovery/interactsh/cmd/interactsh@latest
```

## 3. Proxies & manual testing

| Tool | Install |
|---|---|
| **Burp Suite** | <https://portswigger.net/burp/communitydownload> (Community free; Pro paid). Extensions: Burp → Extensions → BApp Store |
| **AutorizePro / BurpAPISecuritySuite** (Python) | Install [Jython standalone](https://www.jython.org/download) JAR → Burp → Extensions → Options → Python environment → add JAR → Add extension `.py` (path without non-ASCII). No shell command. |
| **Caido** | <https://caido.io> → Download (or `brew install --cask caido` where available). AI skill: `git clone https://github.com/caido/skills` → per README (Vercel skills CLI also works) |
| **ZAP** | `docker pull ghcr.io/zaproxy/zaproxy:stable` · `sudo snap install zaproxy --classic` · <https://www.zaproxy.org/download/> |
| **mitmproxy** | `pipx install mitmproxy` · `brew install mitmproxy` · <https://mitmproxy.org> |
| **Turbo Intruder** | Burp → BApp Store (bundled script target) |

```bash
# ZAP headless baseline scan (docker)
docker run --rm -v "$PWD:/zap/wrk" ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t https://target.example

# mitmproxy interactive
mitmproxy --listen-port 8080
```

## 4. Obscura (agent headless browser)

```bash
# Release archive ships `obscura` + `obscura-worker` — keep both in the same dir
# https://github.com/h4ckf0r0day/obscura/releases  (pick your OS/arch)
curl -sL https://github.com/h4ckf0r0day/obscura/releases/latest/download/obscura-linux-x86_64.tar.gz | tar -xz -C ~/.local/bin
chmod +x ~/.local/bin/obscura ~/.local/bin/obscura-worker

obscura fetch https://example.com          # one-shot render
obscura serve                              # CDP server for Playwright/Puppeteer
obscura mcp                                # MCP server for AI agents
obscura scrape https://example.com         # parallel scrape (needs worker binary)
```

Docs: repo wiki → CLI reference · `docs/Use-the-MCP-server.md`. Flags of note: `--stealth`, `--eval`, `--allow-file-access`.

## 5. Business logic

```bash
git clone https://github.com/ekomsSavior/bizlogic && cd bizlogic
pip3 install --user requests beautifulsoup4
python3 bizlogic_scanner.py           # prompts: base URL, rate, max pages
```

## 6. MCP tool stack (agent hands)

| Server | Install |
|---|---|
| **hexstrike-ai** | `git clone https://github.com/0x4m4/hexstrike-ai && cd hexstrike-ai && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` → `python3 hexstrike_server.py --port 8888` (needs `HEXSTRIKE_API_KEY` env — see README) |
| **pd-tools-mcp** | Requires §1 tools on PATH → `git clone https://github.com/intelligent-ears/pd-tools-mcp && cd pd-tools-mcp && npm install && npm run build` → register stdio cmd per README |
| **mcp-bb (mcp_bug)** | `git clone https://github.com/narkytypey/mcp_bug` → **→ repo README** (Go build + program profiles) |
| **BugHound-MCP** | `git clone https://github.com/binderlabs/BugHound-MCP` → **→ repo README** (`pip`/`uv` install; 29 techniques run with zero external tools, then add §1/§2 binaries for full 45) |
| **MoonMCP** | `git clone https://github.com/Moonwuk/MoonMCP` → **→ repo README** (stdlib-first; wraps §1 tools when present) |
| **MCPwner** | `git clone https://github.com/nedlir/mcpwner && cd mcpwner && cp .env.example .env` → `docker compose up -d` → start MCP server per README (`COMPOSE_PROFILES` gates tool categories) |
| **mcp-security-hub** | `git clone https://github.com/FuzzingLabs/mcp-security-hub && cd mcp-security-hub` → `docker compose up -d nmap-mcp nuclei-mcp` (38 servers, pick what you need) |

**Register in opencode** (`~/.config/opencode/opencode.jsonc`), example for pd-tools-mcp:

```jsonc
"mcp": {
  "pd-tools": {
    "type": "local",
    "command": ["node", "/path/to/pd-tools-mcp/dist/index.js"],
    "enabled": true
  }
}
```

## 7. AI-native hunters & autonomous agents

| Tool | Install |
|---|---|
| **ptai (pentest-ai)** | `pipx install ptai` · `ptai mcp install` (auto-wires Claude Code/Cursor/Codex) · `ptai start https://target` · local: `PENTEST_AI_LLM_PROVIDER=ollama` · no-LLM: `ptai start <url> --no-llm` · tools: `ptai tools install --tier recommended` |
| **AI Scanner (Burp ext)** | `git clone https://github.com/farnaboldi/ai-scanner && cd ai-scanner` → `./build.sh` (raw javac+jar, no Maven) → Burp → Extensions → Add → select jar. Configure LLM in the AI Scanner Settings tab (Burp AI or OpenAI-compatible/Ollama `http://localhost:11434/v1`) |
| **VERDICT** | `git clone https://github.com/vvts-alpha/VERDICT && cd VERDICT` → build CLI per README (`node packages/cli/dist/main.js …`); optional Burp audit ext: `cd tools/burp-audit-ext && gradle shadowJar` → load jar (port 1338, authenticated scans) |
| **Xalgorix** | `git clone https://github.com/k3rth1/xalgorix` → **→ repo README** (Go + TypeScript; BYO LLM key or Ollama; dashboard `127.0.0.1:9137`) |
| **AOBTD** | Releases binary: download `aobtd` → `./aobtd scan --target http://localhost:3000/ --llm ""` (zero-LLM path works). Source: `git clone https://github.com/oz9un/AOBTD` → **→ repo README** |
| **SIPHON** | `git clone https://github.com/Christbowel/siphon && cd siphon` → **→ repo README** (Docker, fully local LLM — qwen2.5-class model in RAM) |
| **Agentic-Bug-Hunter** | `git clone https://github.com/Awarexone/Agentic-Bug-Hunter && cd Agentic-Bug-Hunter` → `chmod +x install_tools.sh && ./install_tools.sh` (subfinder·httpx·nuclei·katana·ffuf) → `./install.sh` (skills→`~/.claude/`); standalone CLI: `./install.sh` then `bughunter setup`. OpenCode: `./install.sh --agent opencode` |
| **bughunter-ai** | `git clone https://github.com/h4ckologic/bughunter-ai` → **→ repo README** (Claude Code + 20 agents + Burp MCP) |
| **agent-smith** | Requires Docker Desktop + Poetry (`curl -sSL https://install.python-poetry.org \| python3 -`) → `git clone https://github.com/0x0pointer/agent-smith` → per README installer → drive from Claude Code / OpenCode / any MCP client |
| **Pulse** | `git clone https://github.com/4dw1tz/Pulse && cd Pulse` → `docker compose up` (backend + scanners) + `pnpm install && pnpm dev` (Next.js UI); Ollama on host for local LLM |
| **PentestGPT** | `pipx install pentestgpt` (suggests-only assistant) → per repo for API key setup |

## 8. Testing MCP/LLM apps (offensive)

| Tool | Install |
|---|---|
| **MCPScan** | `git clone https://github.com/sahiloj/mcpscan && cd mcpscan && npm install && npm run build` → `node dist/cli.js scan --target http://localhost:3000/mcp` (**→ repo README** for npx/global shortcut) |
| **mcpsec** | **→ repo README** (`npm`/`npx` CLI: `mcpsec scan`, `mcpsec audit --github …`, `mcpsec fuzz`) |
| **mcpwn** | `uv run mcpwn enum http://localhost:8765/mcp/` (uv pulls it) or per README install → `-x http://127.0.0.1:8080` to route through Burp; ships a vulnerable practice server under `examples/` |
| **mcpnuke** | `git clone https://github.com/babywyrm/mcpnuke` → `./scan --targets http://localhost:9090 --fast` (see `QUICKSTART.md`) |
| **MCP Server Scanner (Burp)** | Build Montoya jar per `peter-hendy/mcp-server-scanner-extension` README → load in **Burp Pro** (Scanner required; Collaborator for OAST check) |
| **Prompt-injection / LLM checks** | Use **AI Scanner** LLM-target mode (§7) or manual payloads — see `knowledge/payloads.md` + OWASP LLM/MCP Top 10 |

## 9. One-shot core stack (copy block)

```bash
mkdir -p ~/go/bin && export PATH="$PATH:$HOME/go/bin"
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/tomnomnom/waybackurls@latest
go install -v github.com/tomnomnom/gf@latest
go install -v github.com/tomnomnom/qsreplace@latest
go install -v github.com/tomnomnom/anew@latest
go install -v github.com/lc/gau/v2/cmd/gau@latest
go install -v github.com/ffuf/ffuf/v2@latest
go install -v github.com/hahwul/dalfox/v2@latest
go install -v github.com/gitleaks/gitleaks/v8@latest
go install -v github.com/trufflesecurity/trufflehog/v3@latest
sudo apt install -y nmap sqlmap feroxbuster gobuster
pipx install wafw00f arjun uro
nuclei -update-templates
git clone --depth 1 https://github.com/danielmiessler/SecLists.git ~/wordlists/SecLists
echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
```

Then install the layer you need: proxy (§3) · Obscura (§4) · MCP server (§6) · AI hunter (§7).

## 10. Quick health check

```bash
for t in subfinder httpx dnsx naabu katana nuclei gau ffuf sqlmap dalfox nmap gitleaks; do
  printf '%-12s %s\n' "$t" "$(command -v $t >/dev/null && echo OK || echo missing)"
done
nuclei -version
```

## 11. Post-install setup (API keys, config, auth)

Install ≠ ready. Configure each layer once:

### API keys / env (shell profile or `~/.config/<tool>`)

| Key / config | Used by | Get it |
|---|---|---|
| `PDCP_API_KEY` | nuclei (limited), chaos dataset, PD cloud features | <https://cloud.projectdiscovery.io> |
| `CHAOS_API_KEY` | BugHound / chaos subdomain corpus | same PD cloud |
| `GITHUB_TOKEN` / `GH_TOKEN` | GitHub dork recon, gitleaks CI, secret hunting | GitHub → Settings → Developer settings → PAT (repo read scope only) |
| `SHODAN_API_KEY` | shodan wrappers, MoonMCP, mcp-security-hub | shodan.io |
| `URLSCAN_API_KEY` | urlscan recon modules | urlscan.io |
| `HEXSTRIKE_API_KEY` | hexstrike-ai server auth | you generate it; export before `hexstrike_server.py` |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `OLLAMA_HOST` | AI hunters (ptai CLI, VERDICT, Xalgorix, Pulse, agent-smith) | provider dashboards — or skip keys entirely: MCP paths (ptai) and `--no-llm` modes need none |
| `PTAI_PRICE_LIMIT` | ptai spend cap (default `$10`/engagement) | set low for first runs |
| `BURP_AUDIT_API` + `BURP_AUDIT_TOKEN` | VERDICT → Burp audit-ext (:1338) | start the extension, set token |

```bash
# ~/.profile or ~/.bashrc — scope keys to tools that need them
export PDCP_API_KEY=...
export CHAOS_API_KEY=...
export GITHUB_TOKEN=ghp_...        # read-only PAT
export HEXSTRIKE_API_KEY=...
```

Config files worth touching:

- **subfinder**: `~/.config/subfinder/provider-config.yaml` — add GitHub/rapid7/etc. tokens to unlock more passive sources.
- **nuclei**: `nuclei -update-templates` first run; custom templates dir via `-t ~/nuclei-templates/custom`; headless browser checks need Chrome/Chromium installed.
- **httpx/gau**: gau reads `~/.gau.toml` for alienvault/wayback keys (BugHound shares this file).
- **sqlmap**: no config needed; use `--batch` + `--answers` for automation; keep `~/.sqlmap` for sessions/resume.
- **mitmproxy/ZAP/Burp/Caido**: install/trust the tool's CA cert into the OS/browser store **only on your testing machine**; set browser proxy `127.0.0.1:8080` (Burp/Caido/ZAP) or `8080` (mitmproxy).
- **Caido**: create a project per engagement (scope isolation); configure AI plugins with your model provider key (or OpenRouter) — see `caido/skills`.
- **Burp**: set Target → Scope to the program scope before browsing; AutorizePro → paste low-priv headers + set Interception Filters (scope!) (see `tools.md`).
- **Obscura MCP**: when exposing HTTP transport beyond loopback set `OBSCURA_MCP_ALLOWED_ORIGINS` (see repo `docs/Use-the-MCP-server.md`); file access gated behind `--allow-file-access`.
- **ptai**: `ptai mcp install` auto-detects clients; standalone CLI needs one LLM key **or** `PENTEST_AI_LLM_PROVIDER=ollama` **or** `--no-llm`.
- **Ollama (local LLM)**: `ollama pull qwen2.5-coder:7b` (or similar) → endpoints `http://localhost:11434/v1` (OpenAI-compatible) for AutorizePro AI, AI Scanner, ptai, Pulse. Docker-based tools need host reachability (`host.docker.internal` / bridge IP).

### One-time verifier setup

```bash
nuclei -update-templates
subfinder -version && httpx -version && nuclei -version
# optional API sanity: pd httpx -resp-header ... ; gau example.com | head
```

## 12. MCP registration cookbook (opencode)

`~/.config/opencode/opencode.jsonc` — add only the servers you'll use; disable the rest (`"enabled": false`). Pattern: `"type": "local"` + `command` array (never a string).

```jsonc
"mcp": {
  // Recon hands (needs §1 binaries on PATH)
  "pd-tools":   { "type": "local", "command": ["node", "/opt/pd-tools-mcp/dist/index.js"], "enabled": true },
  // Broad tool wrapper (argv per its README; Railway-style setups use hexstrike_mcp.py over stdio)
  "hexstrike":  { "type": "local", "command": ["python3", "/opt/hexstrike-ai/hexstrike_mcp.py"], "enabled": false,
                  "environment": { "HEXSTRIKE_API_KEY": "${env:HEXSTRIKE_API_KEY}" } },
  // Agent browser (SPA render, DOM XSS confirm)
  "obscura":    { "type": "local", "command": ["obscura", "mcp", "--stealth"], "enabled": true },
  // Evidence-first scanner (MCP path needs no API key — exact argv per README, e.g. `ptai mcp serve`)
  "ptai":       { "type": "local", "command": ["ptai", "mcp"], "enabled": false },
  // Scope-enforced bounty workflows
  "mcp-bb":     { "type": "local", "command": ["mcp-bb", "serve"], "enabled": false },  // per repo README for exact argv
  // Dockerized suite (start only what you need)
  "nuclei-mcp": { "type": "local", "command": ["docker", "run", "-i", "--rm", "nuclei-mcp:latest"], "enabled": false }
}
```

Rules of thumb:

1. **One recon MCP + Obscura** is enough for most sessions — enabling everything floods context and multiplies scope risk.
2. Put **scope-enforced servers first** (mcp-bb, MoonMCP, BugHound): they refuse out-of-scope targets by construction.
3. Prefer **stdio** over HTTP transports; if HTTP, bind `127.0.0.1` and set origin allowlists (Obscura `OBSCURA_MCP_ALLOWED_ORIGINS`).
4. Restart opencode after editing `opencode.jsonc` (no hot reload).
5. Verify with the MCP section in opencode's TUI; run `external_tools` / `check_tool_coverage` / `ptai tools install --tier core` from the server itself to confirm binaries resolve.

## 13. Setup done when…

- [ ] **Profile gate answered** (or defaults accepted) → `engagements/<target>/profile.yaml` written; mode/LLM/layers/install/MCP honored below
- [ ] §10 health check all `OK`, `nuclei -update-templates` run
- [ ] Proxy CA trusted + browser proxy set; program scope configured in proxy
- [ ] API keys in env only (never committed); PAT is read-only — **skipped entirely under Stealth**
- [ ] Approved MCP servers registered and enabled deliberately (per profile)
- [ ] Local LLM endpoint reachable (if Ollama chosen); otherwise in-place/none
- [ ] Engagement workspace created (see `methodology.md` → non-duplicated path)

