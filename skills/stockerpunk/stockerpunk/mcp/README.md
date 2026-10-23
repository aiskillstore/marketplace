# StockerPunk MCP server (`spunk-mcp`)

Lets any MCP-capable AI assistant (Claude Desktop, Cursor, and others) work with StockerPunk on BNB Chain:
check the collection, run preflight, build a mint, list punks, and build a harvest. It reads the chain and
builds calldata; **signing goes through the Binance Agentic Wallet (`baw`)**, so the server never holds keys.

## Tools

| Tool | What it does |
|---|---|
| `spunk_preflight` | sign-in, Developer Mode, Agent ID, slots left |
| `spunk_collection` | supply, mint price (USD + live BNB), progress |
| `spunk_mint` | build a mint for 1-5 punks → a `baw` preview command |
| `spunk_punks` | a wallet's punks: rarity, weight, NVDA mined |
| `spunk_harvest` | build a harvest for one punk → a `baw` preview command |

`spunk_mint` and `spunk_harvest` return a `baw contract-call preview` command. The assistant runs it, shows
the parsed transaction and cost, waits for a yes, then runs `baw contract-call execute`.

## Install

```bash
npm i -g @stockerpunk/mcp           # provides: spunk-mcp
npm i -g @binance/agentic-wallet    # provides: baw (for signing)
```

## Add to Claude Desktop / Cursor

Add to your MCP config (`claude_desktop_config.json`, or Cursor's `mcp.json`):

```json
{
  "mcpServers": {
    "stockerpunk": { "command": "spunk-mcp" }
  }
}
```

Then: in the Binance App claim a `.ai` Agent ID and enable Developer Mode, run `baw auth signin` once, and
ask your assistant to "check the StockerPunk collection" or "mint a StockerPunk".

Contract addresses live in the server config and are filled at launch; before launch, mint and punks return
`NOT_LIVE` while preflight and collection still work.
