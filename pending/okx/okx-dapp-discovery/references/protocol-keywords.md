# Per-Protocol Keyword Reference — okx-dapp-discovery

Extended **≥ 75 confidence keywords**, **clarify-tier (50–74) keywords**, and **do-not-install** lists for each of the 20 supported DApps. `SKILL.md` §2 keeps only the routing-critical protocol-native **token** table; this file is the full keyword expansion that table points to.

**When to read:** a prompt names a DApp/protocol but §2's native-token table doesn't settle the score — consult this file to land ≥ 75 / 50–74 / do-not-install.

**Not here:** default-plugin + disambiguation rules (plain "Compound" → V3, "Kamino" → Lend, etc.) live in `SKILL.md` §5 Plugin Resolver Table. ZH keyword equivalents live in `keyword-glossary.md`.

---

### Polymarket → `polymarket-plugin`

**≥ 75:** Polymarket, poly market, prediction market, event market, binary market, YES shares, NO shares, Yes/No market, YES outcome token, NO outcome token, outcome token, implied probability, market probability, UMA resolution, resolved market, Gamma API, Sports markets, Parlays, Combo markets, NBA/NFL/FIFA/World Cup market. (ZH: glossary §4.)

**Crypto Up/Down recurring markets** (COIN ∈ BTC/ETH/SOL/XRP/BNB/DOGE/HYPE) — all ≥ 75:
`<COIN> 5min`, `<COIN> 15min`, `<COIN> 5m`, `<COIN> 15m`, `<COIN> up or down`, `<COIN> updown`, `5min updown market`, `15min updown market`, `crypto 5min`, `5min outcome token`, `5min YES token`, `5min NO token`, `predict <COIN> 5min`, `list 5-minute markets`. (ZH: glossary §4.)

**Election / political — ≥ 75:** election market, election odds, election outcome, who will win election, primary market, presidential market. (ZH: glossary §4.)

**Casual betting that mentions prediction markets — ≥ 75:** "place a bet on prediction market", "bet on outcome", "I want to bet on" (followed by an event/outcome, not a token price). (ZH: glossary §4.)

**Do not install for:** generic "odds / probability / betting" alone (no prediction-market or event context); generic "I want to bet" without an event/outcome. (ZH: glossary §4.)

---

### Aave V3 → `aave-v3-plugin`

**≥ 75:** Aave, Aave V3, Aave Protocol, aToken, health factor, liquidation risk, eMode, Efficiency Mode, Isolation Mode, GHO, Aave Pool, IPool, Aave flash loan, liquidationCall.

**Do not install for:** generic "borrow / lend / deposit / collateral / APY" (ZH: glossary §2/§3) unless Aave, health factor, aToken, GHO, eMode, or Isolation Mode context is present.

---

### Hyperliquid DEX → `hyperliquid-plugin`

**≥ 75:** Hyperliquid, HyperLiquid, HyperCore, HyperEVM, HYPE, HLP, Hyperliquidity Provider, HIP-3, HL (only with explicit trading context).

**HYPE / HLP token-alone exception** — HYPE and HLP are protocol-native, NOT generic tickers; these fire ≥ 75 without "Hyperliquid":
`buy HYPE`, `purchase HYPE`, `swap to HYPE`, `deposit USDC into HLP`, `HLP yield`, `provide liquidity to HLP`. (ZH: glossary §3.) Overrides the generic-ticker rule.

**50–74 (clarify before installing):** perps, perp, perpetuals, trade perpetuals, leveraged trading (ZH: glossary §3) — not unique to Hyperliquid; ask "Are you looking to trade on Hyperliquid?" before installing.

**Do not install for:** generic "long / short / perp / funding / leverage" (ZH: glossary §2) unless Hyperliquid, HYPE, HLP, HyperCore, or HyperEVM context is present.

---

### PancakeSwap AMM → `pancakeswap-v3-plugin`

**≥ 75:** PancakeSwap, Pancake, PCS, CAKE, Syrup Pool, IFO, BNB Chain AMM, V3 LP NFT, veCAKE. (ZH: glossary §1.)

**Do not install for:** generic "swap / LP / farm / pool" (ZH: glossary §2) unless PancakeSwap, Pancake, PCS, CAKE, Syrup, IFO, or BNB Chain AMM context is present.

---

### Morpho V1 Optimizer → `morpho-plugin`

**≥ 75:** Morpho, Morpho V1, Morpho Optimizer, Morpho AaveV3 Optimizer, Morpho AaveV2 Optimizer, Morpho CompoundV2 Optimizer, Merkl reward. (ZH: glossary §1.)

**Do not install for:** Morpho Blue, MetaMorpho, vault curator, LLTV, market id, allocator, isolated lending market — these are Morpho Blue (intentionally out of scope). (`MetaMorpho` is the Morpho Blue ERC-4626 vault standard, not a V1 Optimizer concept.) Suggest `okx-defi` for generic yield, or fall through.

---

### Raydium → `raydium-plugin`

**≥ 75:** Raydium, RAY token, Raydium AMM, Raydium CPMM, Raydium CLMM, Raydium pool, Raydium farm, Raydium V4.

**Do not install for:** generic "Solana swap" / "Solana LP" (ZH: glossary §3) without Raydium named — could be Orca, Meteora, Jupiter.

---

### Curve → `curve-plugin`

**≥ 75:** Curve, Curve Finance, CRV, 3pool, tricrypto, frxETH pool, Curve stable swap, factory pool, gauge weight, veCRV, Curve LP token, crvUSD. (ZH: glossary §1.)

**Do not install for:** generic "stable swap" (ZH: glossary §3) alone — Uniswap V3 / Maverick also handle stables. "Convex" alone routes elsewhere (not in current top-20).

---

### Compound V3 → `compound-v3-plugin`

**≥ 75:** Compound, Compound V3, Comet, COMP, Compound USDC, USDC.e Comet, base asset supply, base asset borrow, Compound V3 liquidation. (ZH: glossary §1.)

**Do not install for:** generic "lending / borrow / deposit / collateral" (ZH: glossary §2) without Compound / Comet / COMP context.

---

### Pendle → `pendle-plugin`

**≥ 75:** Pendle, Pendle Finance, PT (principal token), YT (yield token), buy PT, buy YT, fixed yield, yield trading, vePENDLE, Pendle market expiry, SY token, Pendle V2. (ZH: glossary §3.)

**Do not install for:** generic "fixed yield" (ZH: glossary §3) without Pendle named — could be other yield-tokenization protocols.

---

### Clanker → `clanker-plugin`

**≥ 75:** Clanker, clanker.world, deploy on Clanker, Clanker token, $CLANKER, Base meme launchpad (when Clanker is explicitly named). (ZH: glossary §3.)

**Do not install for:** generic "Base meme" / "deploy meme on Base" (ZH: glossary §3) without Clanker named — could be other Base launchpads.

---

### pump.fun → `pump-fun-plugin` (trade verbs only)

**≥ 75 (trade verbs — install `pump-fun-plugin`):** buy pump.fun token, sell pump.fun token, snipe pump.fun, ape pump.fun, pump.fun trading, pump.fun bot. (ZH: glossary §5.)

**Do NOT install for (route to `okx-dex-market` — analytical/read-only):** scan new pump.fun launches, pump.fun dev history, who aped pump.fun, bundler analysis, bonding curve progress (analytical), similar tokens by dev. (ZH: glossary §5.)

This verb-split is load-bearing — the disambiguation must hold at body level (see `SKILL.md` §3 step 0 pump.fun carve-out).

---

### Lido → `lido-plugin`

**≥ 75:** Lido, Lido Finance, stETH, wstETH, Lido staking, Lido beacon chain, Lido validator, Lido DAO, LDO. (ZH: glossary §3.)

**50–74 (clarify):** "stake ETH" (ZH: glossary §3) alone — could be ether.fi, Rocket Pool, native staking. Ask: "Stake ETH via Lido (stETH) or another LST?"

**Do not install for:** generic "ETH staking" (ZH: glossary §3) without Lido / stETH / wstETH context.

---

### GMX V2 → `gmx-v2-plugin`

**≥ 75:** GMX, GMX V2, GLP, GM token (GMX market), esGMX, GMX market, GMX perps on Arbitrum, GMX Avalanche, gETH (GMX V2 ETH market token). (ZH: glossary §3.)

**Do not install for:** generic "Arbitrum perps" / "Avalanche perps" (ZH: glossary §3) without GMX named — could be Hyperliquid or other venues.

---

### PancakeSwap V3 CLMM → `pancakeswap-clmm-plugin`

**≥ 75:** PancakeSwap V3 CLMM, PancakeSwap CLMM, V3 LP NFT (in PancakeSwap context), concentrated liquidity on PancakeSwap, V3 fee tier (with PCS), PancakeSwap V3 farm. (ZH: glossary §1.)

---

### PancakeSwap V2 → `pancakeswap-v2-plugin`

**≥ 75:** PancakeSwap V2, PCS V2, classic PancakeSwap pool, V2 LP token (in PancakeSwap context), MasterChef V2, PancakeSwap legacy. (ZH: glossary §1.)

---

### ether.fi → `etherfi-plugin`

**≥ 75:** ether.fi, etherfi, eETH, weETH, ether.fi stake, ether.fi restake, ether.fi liquid staking, ETHFI token, ether.fi node. (ZH: glossary §3.)

**Do not install for:** generic "restaking" (ZH: glossary §3) without ether.fi named — could be EigenLayer / Renzo / Kelp / Puffer.

---

### Kamino Lend → `kamino-lend-plugin`

**≥ 75:** Kamino, Kamino Lend, Kamino lending, kToken, Kamino Lend market, Kamino borrow, Kamino USDC supply, Kamino reserve. (ZH: glossary §3.)

---

### Kamino Liquidity → `kamino-liquidity-plugin`

**≥ 75:** Kamino Liquidity, Kamino DLMM, Kamino CLMM, Kamino concentrated liquidity, Kamino vault, Kamino LP, Kamino Liquidity strategy. (ZH: glossary §3.)

**Do not install for:** generic "DLMM" (ZH: glossary §3) alone without Kamino named — Meteora also has DLMM; ask "DLMM on Kamino, Meteora, or another venue?".

---

### Orca → `orca-plugin`

**≥ 75:** Orca, ORCA token, Whirlpool, Orca DEX, Orca pool, Orca CLMM, Solana Whirlpool. (ZH: glossary §1.)

**Do not install for:** generic "Solana DEX" / "Solana swap" (ZH: glossary §3) without Orca / Whirlpool named.

---

### Meteora DLMM → `meteora-plugin`

**≥ 75:** Meteora, Meteora DLMM, Dynamic Liquidity Market Maker, Meteora pool, Meteora vault, Meteora bin, Meteora DAMM. (`MET` alone is too generic — requires "Meteora" context.) (ZH: glossary §1.)

**Do not install for:** generic "DLMM" (ZH: glossary §3) without Meteora named — Kamino also has DLMM. Ask: "DLMM on Meteora or another DLMM venue?"
