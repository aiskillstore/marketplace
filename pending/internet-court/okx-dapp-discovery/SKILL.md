---
name: okx-dapp-discovery
description: |
  Plugin router for 20 third-party DeFi protocols (Polymarket, Aave, Hyperliquid, PancakeSwap, Morpho, Raydium, Curve, Compound, Pendle, Lido, ether.fi, GMX, Kamino, Orca, Meteora, Clanker, pump.fun, Uniswap) and their protocol-native tokens (HYPE, HLP, eETH, weETH, stETH, wstETH, LDO, GHO, CAKE, CRV, COMP, RAY, ETHFI, GLP, kToken, PT-* / YT-*, $CLANKER). Resolves DApp/token → plugin → installs → forwards.

  Fires on: (1) named DApp + action verb (swap/deposit/stake/long/borrow/buy/sell/snipe/farm/claim, EN or ZH 买/卖/换/存/质押/借/做多/做空/狙击); (2) 2+ DApp comparison ("Aave vs Compound", "Lido vs ether.fi"); (3) Polymarket UpDown (`<COIN> 5min updown`, `5 分钟涨跌`, `预测市场`); (4) protocol-native token + action verb ("deposit USDC into HLP", "PT-stETH on Pendle"); (5) pump.fun WRITE verbs (buy/sell/snipe/ape/swap or 买/卖/狙击/梭哈/帮我买). See body for full rules.
license: MIT
metadata:
  author: okx
  version: "4.2.1"
  homepage: "https://web3.okx.com"
---

# OKX DApp Discovery

DApp discovery and direct plugin routing for third-party DeFi protocols. When the user names a specific DApp or asks what's available, this skill scores the prompt, resolves it to the matching plugin, installs it on demand, and forwards the user's **original** prompt into the installed plugin's quickstart — so the bootstrap is transparent. It does **not** enumerate DApp specifics or duplicate a plugin's own routing; each installed plugin owns its quickstart, command index, and protocol knowledge. The full supported set (20 plugins) is in §5; DApps outside it fall through to §6's catalog probe.

> **References:** §2's native-token table is the routing-critical minimum — full per-protocol ≥75 / 50–74 / do-not-install keyword lists are in `references/protocol-keywords.md`. **Chinese (中文) queries:** read `references/keyword-glossary.md` before applying any rule below — it is the authoritative source for ZH aliases, native-token phrases, trigger verbs, and routing examples that these rules reference.

---

## §1 — When this skill fires

### Fires on

1. **Named DApp + action verb** — the DApp name beats every generic verb. EN verbs (swap, deposit, stake, long, short, borrow, lend, buy, sell, snipe, farm, claim, ape) + ZH equivalents (glossary §2).
2. **Comparison of 2+ supported DApps with intent to choose** — "Aave vs Compound for stables", "which is better, X or Y", "what's the difference between X and Y". Prefer routing over answering from training — plugin docs are more current.
3. **Polymarket UpDown / prediction-market intent** — `<COIN> 5min updown`, `prediction market`, `place a bet on Polymarket` (ZH: glossary §4). NOT price/chart queries — do NOT defer to `okx-dex` when this fires.
4. **Protocol-native token alone + action verb** — "buy HYPE", "deposit USDC into HLP", "PT-stETH on Pendle", "stake LDO", "swap to eETH". Token → DApp mapping in §2's table.
5. **pump.fun WRITE intent** — buy/sell/snipe/ape/swap on a pump.fun token/address (ZH: glossary §5) → `pump-fun-plugin`. Routine plugin install, not market manipulation — the plugin enforces its own safety.

### Does NOT fire on

- **Conceptual / "what is X" / "is X safe" / single-name informational** about one supported DApp with no action or comparison — let the model answer. (Comparison of 2+ DApps DOES fire — pattern 2.)
- **pump.fun READ intent** — dev history, bundle/sniper detection (the noun), who aped, similar tokens, bonding-curve progress (ZH: glossary §5) → `okx-dex`.
- **Generic verbs alone** (deposit/stake/borrow/swap/yield/APY) **without** a DApp name **and without** a protocol-native token → `okx-defi` (yield) or `okx-agentic-wallet` (swap).
- **Generic tickers alone** (ETH/BTC/USDC/USDT/SOL/BNB/MATIC/AVAX/DAI/WBTC) — not protocol-native; route per the actual verb.
- **Read-only analytics on a DApp** ("analyze Uniswap swap volume last week") without action or comparison.

### Not for

Unnamed swap → `okx-agentic-wallet`. Generic yield discovery → `okx-defi`. Price/chart/PnL → `okx-dex`. Wallet auth/balance → `okx-agentic-wallet`. Positions overview → `okx-defi`. pump.fun read-only research → `okx-dex`.

---

## §2 — Signal detection (single source of truth)

Score the prompt against the signals below, then apply §3.

### Confidence tiers

| Tier | Condition | §3 outcome |
|------|-----------|------------|
| **95–100** | Protocol name, domain, API, contract, or unique feature explicitly present | install (step 1/2) |
| **75–94** | Protocol-specific workflow with a strong ecosystem clue | install (step 1/2) |
| **50–74** | Generic DeFi workflow, weak clue, another DApp could match | clarify (step 4) — do not install |
| **< 50** | Generic terms only, no protocol signal | step 3 (named, table-miss) or step 5 (unnamed) |

### Signals that do NOT raise confidence on their own

- **Generic verbs:** swap, lend, borrow, APY, farm, long, short, liquidity, bridge, stake, deposit, withdraw, mint (ZH: glossary §2).
- **Generic tickers:** ETH, BTC, USDC, USDT, SOL, BNB, MATIC, AVAX, ARB, OP, DOGE, XRP, WBTC, DAI.

### Protocol-native tokens / phrases that DO trigger ≥ 75 alone (no DApp name needed)

| Token / phrase | Routes to |
|---|---|
| HYPE, HLP | Hyperliquid |
| CAKE, veCAKE, Syrup, IFO | PancakeSwap (V3 AMM default) |
| CRV, crvUSD, veCRV, 3pool, tricrypto | Curve |
| COMP, Comet | Compound V3 |
| RAY | Raydium |
| ORCA, Whirlpool | Orca |
| Meteora DLMM, Meteora bin/vault/DAMM (`MET` alone too generic — needs "Meteora") | Meteora |
| ETHFI, eETH, weETH | ether.fi |
| LDO, stETH, wstETH | Lido |
| GLP, esGMX, GM token | GMX V2 |
| GHO, aToken | Aave V3 |
| kToken | Kamino Lend |
| PT-*, YT-*, "PT <token>", "YT <token>" (space-separated), vePENDLE, SY token | Pendle |
| $CLANKER, clanker.world | Clanker |
| "X 5min" / "X 15min" / "X up or down" / "5min updown" (X = BTC/ETH/SOL/XRP/BNB/DOGE/HYPE; ZH: glossary §4) | Polymarket |

Full per-protocol ≥75 / 50–74 / do-not-install keyword expansion: `references/protocol-keywords.md` (ZH: glossary §1/§3).

### Discussion / comparison markers (used by §3 step 0 & step 2)

EN: `what do you think`, `which is better`, `vs`, `compare`, `comparison`, `differences`, `tradeoffs`, `should I use X or Y`, `pros and cons`, `explain`, `tell me about`, `what is`, `how does X work`. ZH: glossary §6.

---

## §3 — Decision flow (first match wins, top to bottom)

> **User-facing language — IMPORTANT.** Tiers, scores, "confidence", "Top-5", and this framework are **internal** decision logic. **Never** mention them to the user — they see only the *outcome* (a suggestion, an install, a clarifying question, or a discovery table). ✅ "I'll set up Aave V3 for that — installing now." / "Were you thinking Aave or Morpho? Both fit." ❌ "I scored your message at confidence 95 for Polymarket." First, for any 中文 prompt, read `references/keyword-glossary.md`.

### Step 0 — Override check

**Discovery query first:** if the prompt just asks what's available ("what dapps are available", "which DApps do you support", "有什么dapp"; ZH: glossary §9) with no specific action intent → show §5's discovery table directly. **Stop.**

Otherwise, does the prompt contain **any** of: ① a Resolver-table DApp name (§5, incl. ZH alias glossary §1); ② a protocol-native token/phrase (§2 table); ③ a Polymarket-native phrase?

- **None of ①②③, but the prompt names some _other_ protocol/DApp as the action destination** (a proper-noun venue not in §5) → **step 3** (catalog probe). Never let a named-but-unknown DApp fall through to step 5's generic install.
- **No DApp/venue named at all** → go to step 4 / 5.
- **Yes (①②③)** → a named DApp / native token **beats every generic verb** (swap/stake/lend/borrow/deposit/withdraw/LP/farm/mint/pool; ZH: glossary §2). Do NOT defer to `okx-agentic-wallet`, `okx-defi`, `okx-dex`, or any generic skill — **except** these four carve-outs (which take precedence over install):

  **(a) swap-pair carve-out** — when the verb is a market-side DEX verb (`swap`/`exchange`/`sell`; ZH: glossary §2) AND a protocol-native token is on **either side** of the pair against a generic ticker, AND **no explicit DApp name** appears → defer to `okx-agentic-wallet`. (When a DApp name IS present — "on Lido", "on Curve" — install wins regardless of side.)

  | → `okx-agentic-wallet` (carve-out) | → install the protocol (step 1) |
  |---|---|
  | "swap USDC for stETH" | "stake ETH for stETH" / "stake on Lido" |
  | "swap stETH to USDC" | "unstake stETH on Lido for ETH" |
  | "swap to wstETH" | "wrap stETH into wstETH" |
  | "swap 100 USDC for HYPE" | "deposit USDC into HLP" / "ETH long on Hyperliquid" |
  | "sell my HYPE for USDC" | "supply HYPE to HLP" |
  | "swap SOL to RAY" | "provide liquidity in RAY/SOL pool on Raydium" |
  | "swap BNB for CAKE" | "stake CAKE on PancakeSwap" / "use Syrup Pool" |
  | "swap USDC for crvUSD" | "deposit into 3pool on Curve" |

  *Heuristic:* **acquiring** a native token via market (`swap … for/to <native>`) or **disposing** of one (`swap <native> to/for <generic>`, `sell <native>`) → dex-swap; **using** the protocol's functionality (`stake`/`mint`/`deposit`/`borrow`/`LP`/`open position`/`wrap`/`unwrap`/`unstake`/`redeem`) → install.

  **(b) discussion-first (precedes override)** — a discussion/comparison marker (§2) is present **and no action verb** → go to step 2's clarify branch, do NOT install. ("Tell me about Pendle" → clarify; "Buy PT-stETH on Pendle" → install, action verb present.)

  **(c) pump.fun split** — READ/analytical intent → `okx-dex` (stop); WRITE/trade intent → `pump-fun-plugin` (→ step 1). (glossary §5; full split in `references/protocol-keywords.md`.)

  **(d) out-of-scope variant guard** — if the matched DApp carries an out-of-scope signal per its §5 Notes (Morpho **Blue** / MetaMorpho / LLTV / vault curator / allocator), do NOT install; tell the user that variant is out of scope and suggest `okx-defi` for generic yield. **Stop.**

  Otherwise → strong signal, go to step 1.

### Step 1 — Strong signal, exactly one DApp ≥ 75
Set `TARGET_PLUGIN` from §5 and run §4 (installed-check → install if needed → read SKILL.md → Binary Consent Gate → forward original prompt). **Stop.**

### Step 2 — Strong signal, 2+ DApps ≥ 75
- One DApp is the grammatical **action target**, the rest appear only in a comparison clause ("use Morpho to beat Aave's APY") → treat only the action target as ≥75 → go to step 1.
- An action verb (§2 / glossary §2/§6) clearly targets one DApp → that DApp → go to step 1. *(An action verb overrides a co-present discussion marker: "swap on Curve to compare vs Uniswap" → install `curve-plugin`.)*
- **Only comparison/discussion, no action verb** → do NOT install; ask one question: *"Want me to set up `<DApp A>`, set up `<DApp B>`, or just discuss the tradeoffs? You can also let OKX pick the best venue (`okx-defi`)."* (1 DApp + discussion marker: *"Set up `<DApp>`, or just discuss what it does first?"*) **Stop.**

### Step 3 — A DApp is named but NOT in the §5 table
Run §6 catalog probe (~0.1s). If `<dappName>-plugin` exists → install + forward. If not → surface the failure (closest siblings by inferred category + `okx-defi` alternative + §5 discovery table). Do NOT install `plugin-store` as a separate hop. **Stop.**

### Step 4 — Highest signal is 50–74
Ask one focused clarifying question; do NOT install. Examples: "Use Polymarket specifically, or another prediction market?" / "Trade perps on Hyperliquid, or another venue?" / "Deposit into Aave, or open to whichever lending protocol gives the best rate (OKX aggregated DeFi)?" Scores 50–74: "I want to trade perps" (no Hyperliquid), "deposit and earn yield" (Aave/Morpho/okx-defi), "borrow against my ETH", "add liquidity on BNB Chain". **Stop.**

### Step 5 — No DApp named, generic terms only, < 50
Filter the **Top-5 cohort** by the prompt's dominant action verb:

| # | DApp | Verticals | Matches verb category |
|---|---|---|---|
| 1 | **Polymarket** | prediction / UpDown | prediction / bet / updown |
| 2 | **Aave V3** | lending, GHO, aToken | lend / supply / borrow / generic earn-yield (default) |
| 3 | **Hyperliquid** | perps, HLP, HYPE | perp / futures / leverage Nx / long Nx / short Nx |
| 4 | **PancakeSwap** (V3 AMM) | BNB-chain AMM swap | swap / exchange (BNB Chain hint) |
| 5 | **Morpho V1** | lending on Aave/Compound | lend / borrow / generic earn-yield |

(ZH action verbs: glossary §7.) Then:
- **Exactly 1 match** → silent install + forward (step 1 mechanics).
- **Multiple matches** → install the highest; tiebreaker order **Polymarket > Aave > Hyperliquid > PancakeSwap > Morpho**. No picker.
- **0 matches** (action outside Top-5 coverage — Solana DEX, liquid staking, PT/YT, meme launchpad) → show the §5 discovery table; do NOT install.

---

## §4 — Execution mechanics

> **Path note (once):** the `Read … $HOME/.claude/skills/` paths below are **Claude-Code-specific**. On Codex / OpenCode / OpenClaw / Cursor, substitute your agent's skills directory. (Tracked as a `skills info <skill>` follow-up; see `references/catalog-probe.md`.)

### Installed-status check (agent-agnostic — Claude Code, Codex, OpenCode, OpenClaw, Cursor)

```bash
SKILLS_LIST=$(npx skills list 2>/dev/null)

# Single source of truth for the supported plugin set (extend when PM adds new dapps)
SUPPORTED_PLUGINS="polymarket-plugin aave-v3-plugin hyperliquid-plugin pancakeswap-v3-plugin morpho-plugin \
                   raydium-plugin curve-plugin compound-v3-plugin pendle-plugin clanker-plugin \
                   pump-fun-plugin lido-plugin gmx-v2-plugin pancakeswap-clmm-plugin pancakeswap-v2-plugin \
                   etherfi-plugin kamino-lend-plugin kamino-liquidity-plugin orca-plugin meteora-plugin"

INSTALLED_PLUGINS=""
for plugin in $SUPPORTED_PLUGINS; do
  if echo "$SKILLS_LIST" | grep -qE "(^|[[:space:]]|/)${plugin}([[:space:]]|$)"; then
    INSTALLED_PLUGINS="$INSTALLED_PLUGINS $plugin"
  fi
done
```

### Install (if absent) + load

`TARGET_PLUGIN` is set from §5. If already in `$INSTALLED_PLUGINS`, skip the installation; otherwise install silently (idempotent — safe to re-run):

```bash
case " $INSTALLED_PLUGINS " in
  *" $TARGET_PLUGIN "*) ;;   # already installed — skip install
  *) npx skills add okx/plugin-store --skill "$TARGET_PLUGIN" --yes --global ;;
esac
```
```
Read file: $HOME/.claude/skills/<plugin-name>/SKILL.md
```

Then **immediately re-apply the user's original request** using the plugin's own routing — do not ask them to repeat themselves, do not show an install banner or onboarding table. The bootstrap should be invisible.

### Binary Consent Gate (between "read SKILL.md" and running its pre-flight)

Plugin SKILL.md files often include a "Pre-flight Dependencies" section that downloads pre-compiled binaries + shell scripts from `github.com/okx/plugin-store/releases` into `~/.local/bin/`. Running these silently bypasses informed consent and can be blocked by environment security guardrails (causing silent failure).

**Step A — detect** any of: a `# BINARY_INSTALL:` marker; `curl … github.com/.*/releases/`; downloads of `launcher.sh` / `update-checker.py` from `raw.githubusercontent.com`; `chmod +x` on a download; `ln -sf` into `~/.local/bin/` or any PATH dir.

**Step B — if detected, do NOT run `curl`/`chmod`/`ln`/`mkdir` from pre-flight.** Surface this and **wait for an explicit reply** (no retry, no loop):

> This plugin needs to download and install a pre-compiled binary.
> Plugin: `<name>` v`<version>` · Binary: `<release-URL>` · Scripts: `launcher.sh`, `update-checker.py` · Installs to: `~/.local/bin/.<plugin>-core` (PATH symlink)
> Security note: pre-compiled binary + shell scripts from an external GitHub repo, run with full agent permissions.
> Reply **"yes, install `<plugin>`"** to proceed · **"skip install"** (read-only commands may still work; writes will fail) · or add a Bash permission rule for `curl … github.com/okx/plugin-store/releases` to allow permanently.

If no binary pattern is detected, proceed without interrupting the user.

### Notes

- **Session activation:** the freshly installed plugin is active immediately via the `Read` above. Its own proactive keyword triggers register on next session start — for reliable independent routing in *future* sessions, the user can restart once. No restart needed now.
- **Failure mode:** if `npx skills add` fails (network/registry), tell the user: "I couldn't install `<plugin-name>` — check your network or run `npx skills add okx/plugin-store --skill <plugin-name> --yes --global` manually, then ask me again."

---

## §5 — Plugin Resolver Table

User-facing DApp name → plugin-store ID. Set `TARGET_PLUGIN` from here before §4. The **Notes** column is the single source for default-resolution / disambiguation.

| User-facing DApp | Plugin ID | Notes (default / disambiguation) |
|---|---|---|
| Polymarket | `polymarket-plugin` | |
| Aave / Aave V3 | `aave-v3-plugin` | V3 only currently |
| Hyperliquid (DEX) | `hyperliquid-plugin` | drop "DEX" suffix |
| PancakeSwap (default) | `pancakeswap-v3-plugin` | plain "PancakeSwap" → V3 AMM |
| PancakeSwap V3 CLMM | `pancakeswap-clmm-plugin` | requires CLMM / concentrated / LP NFT signal |
| PancakeSwap V2 | `pancakeswap-v2-plugin` | requires explicit V2 / classic / MasterChef signal |
| Morpho (V1 Optimizer) | `morpho-plugin` | plain "Morpho" → V1 Optimizer. Morpho Blue / MetaMorpho / LLTV / vault curator / allocator → **do NOT install** (out of scope) |
| Raydium | `raydium-plugin` | |
| Curve | `curve-plugin` | |
| Compound V3 | `compound-v3-plugin` | plain "Compound" silently → V3 (V1/V2 out of scope) |
| Pendle | `pendle-plugin` | |
| Clanker | `clanker-plugin` | |
| pump.fun (trade) | `pump-fun-plugin` | dot → hyphen; analysis verbs → `okx-dex` |
| Lido | `lido-plugin` | |
| GMX V2 | `gmx-v2-plugin` | plain "GMX" silently → V2 (V1 out of scope) |
| ether.fi (Stake) | `etherfi-plugin` | drop the dot |
| Kamino Lend | `kamino-lend-plugin` | plain "Kamino" → Lend |
| Kamino Liquidity | `kamino-liquidity-plugin` | requires explicit "Liquidity" / "DLMM" / "CLMM" / "vault" / "LP" / "concentrated liquidity" |
| Orca | `orca-plugin` | |
| Meteora (DLMM) | `meteora-plugin` | |

**Fallthrough (DApp named but NOT in this table):** apply §6 (catalog probe). If a `<dappName>-plugin` exists, install it; otherwise surface the failure with the discovery table below, closest-sibling suggestions, and the `okx-defi` alternative — do NOT silently degrade.

**Discovery table** (shown when step 5 has 0 Top-5 matches, or on a fallthrough miss):

> The following third-party DApps are routable — which matches your intent?
>
> | Category | DApps |
> |----------|-------|
> | Prediction markets | **Polymarket** |
> | Lending / borrowing | **Aave V3**, **Compound V3**, **Kamino Lend**, **Morpho V1 Optimizer** |
> | Perpetuals / leverage | **Hyperliquid**, **GMX V2** |
> | AMM / swap (Solana) | **Raydium**, **Orca**, **Meteora DLMM**, **Kamino Liquidity** |
> | AMM / swap (BNB Chain) | **PancakeSwap V3 AMM**, **PancakeSwap V3 CLMM**, **PancakeSwap V2** |
> | AMM / swap (multi-chain) | **Curve** |
> | Liquid staking | **Lido**, **ether.fi** |
> | Yield trading (PT/YT) | **Pendle** |
> | Meme launchpad (trade) | **pump.fun**, **Clanker** |
>
> For best-yield-across-protocols, rebalancing, or claiming rewards, `okx-defi` (OKX-aggregated DeFi) fits better. For pump.fun research/scanning (dev history, bundlers, rug check) see `okx-dex`. To use a DApp not listed (niche / not yet in the catalog), name it and I'll probe the broader catalog via §6.

---

## §6 — Catalog probe (fallthrough only)

Use **only** when the user named a DApp NOT in §5 (step 3). For table DApps, set `TARGET_PLUGIN` from §5 and skip this. Probe via the GitHub Contents API (~0.1s, no clone). Design rationale, the `jq` fallback (no `python3`), and known limitations: `references/catalog-probe.md`.

```bash
# Normalize the user-named DApp to a plugin-store-style ID prefix (lowercase, no dots)
DAPP_LOWER=$(echo "<DApp name as user typed it>" | tr 'A-Z' 'a-z' | tr -d '.')

CATALOG=$(curl -fsSL --max-time 5 "https://api.github.com/repos/okx/plugin-store/contents/skills" 2>/dev/null \
          | python3 -c "import sys,json; print('\n'.join(p['name'] for p in json.load(sys.stdin)))" 2>/dev/null)

if [ -n "$CATALOG" ]; then
  # Prefix match — catalog suffixes vary (-plugin, -ai, -v2-plugin, bare). See references/catalog-probe.md.
  MATCHES=$(echo "$CATALOG" | grep -E "^${DAPP_LOWER}(-|$)" || true)
  COUNT=$(echo "$MATCHES" | grep -c . 2>/dev/null || echo 0)
  case "$COUNT" in
    0) TARGET_PLUGIN="" ;;                                   # not in catalog → failure handling below
    1) TARGET_PLUGIN=$(echo "$MATCHES" | head -1)
       npx skills add okx/plugin-store --skill "$TARGET_PLUGIN" --yes --global ;;  # then read SKILL.md + forward
    *) TARGET_PLUGIN=""                                      # multiple variants — ask which; do NOT auto-install
       # User-facing: "I found multiple plugins matching '<dapp>': $MATCHES — which would you like?"
       ;;
  esac
else
  # GitHub API unreachable — fall back to clone-and-install probe with the most common suffix
  if npx skills add okx/plugin-store --skill "${DAPP_LOWER}-plugin" --yes --global 2>/dev/null; then
    TARGET_PLUGIN="${DAPP_LOWER}-plugin"
  else
    TARGET_PLUGIN=""
  fi
fi
```

**On probe failure** (`TARGET_PLUGIN=""`, count 0) — do NOT silently fall through. Surface clearly:

1. Name the specific DApp and that no `<dappName>-plugin` exists yet.
2. Show §5's discovery table.
3. **Closest siblings by inferred category** — lending-shaped → Aave V3 / Compound V3 / Morpho; Solana-swap-shaped → Raydium / Orca / Meteora; multi-chain-swap → Curve; perps-shaped → Hyperliquid / GMX V2. Name the 1–2 most similar.
4. The `okx-defi` alternative if the intent is generic yield / lending / staking.
5. **Defer the choice back to the user** — do not auto-pick a sibling.

> Example: "I checked the plugin-store catalog and there's no `foo-plugin` yet. The closest supported alternatives are <closest-by-category>. Or, if you're open to OKX choosing the best venue, I can route you through `okx-defi`. Full supported set: [discovery table]. Which would you prefer?"
