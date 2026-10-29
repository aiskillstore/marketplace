#!/usr/bin/env python3
"""SoulBoard MCP server — expose the agentic launchpad to any MCP host (Claude Desktop, Cursor, …).

Read tools (board/token/config) return live on-chain data. The prepare_* tools are NON-CUSTODIAL:
they return a `sign_this` {to, data, value} (plus any approve steps) that the host then signs with
the user's own agentic wallet via `baw contract-call` — this server never holds keys or signs.

Run:  SOULBOARD_BACKEND=https://soulboard.fun  python3 soulboard_mcp.py
Deps: pip install "mcp"
"""
import json
import os
import urllib.error
import urllib.request

from mcp.server.fastmcp import FastMCP

BACKEND = os.environ.get("SOULBOARD_BACKEND", "https://soulboard.fun").rstrip("/")
mcp = FastMCP("soulboard")


def _get(path):
    req = urllib.request.Request(BACKEND + path, headers={"user-agent": "SoulBoard-Skill/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def _post(path, body):
    req = urllib.request.Request(
        BACKEND + path, data=json.dumps(body).encode(),
        headers={"content-type": "application/json", "user-agent": "SoulBoard-Skill/1.0"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read())
        except Exception:
            return {"error": f"HTTP {e.code}"}


@mcp.tool()
def board() -> dict:
    """List live launches on the SoulBoard agent-gated launchpad (Robinhood Chain, chainId 4663)."""
    return _get("/api/board")


@mcp.tool()
def token(ca: str) -> dict:
    """Get details for one token by its contract address (supply, mint price, progress, holders)."""
    return _get(f"/api/token/{ca}")


@mcp.tool()
def config() -> dict:
    """SoulBoard chain config + deployed contract addresses (factory, market, $SoulBoard, signer)."""
    return _get("/config")


@mcp.tool()
def prepare_mint(asset: str, wallet: str, value_wei: str = "0") -> dict:
    """Prepare an agent-gated mint of a fair-mint token. Returns sign_this {to,data,value} to sign
    with the user's agentic wallet (baw contract-call). The wallet MUST hold a soulbound Agent-ID on
    BNB Chain, or the backend refuses. First mint per wallet is free (value 0)."""
    return _post("/prepare/mint", {"asset": asset, "wallet": wallet, "value_wei": value_wei})


@mcp.tool()
def prepare_buy(wallet: str, listing_id: int, value_wei: str = "0") -> dict:
    """Prepare buying a sell-order on the agent-gated market. Returns sign_this to sign with baw."""
    return _post("/prepare/buy", {"wallet": wallet, "listingId": listing_id, "value_wei": value_wei})


@mcp.tool()
def prepare_sell(wallet: str, asset: str, amount: str, price_wei: str) -> dict:
    """Prepare listing `amount` of `asset` for sale at `price_wei`. Returns approve + list steps."""
    return _post("/prepare/sell", {"wallet": wallet, "asset": asset, "amount": amount, "priceWei": price_wei})


@mcp.tool()
def prepare_cancel(listing_id: int) -> dict:
    """Prepare cancelling one of your open listings (no voucher needed)."""
    return _post("/prepare/cancel", {"listingId": listing_id})


@mcp.tool()
def prepare_launch(wallet: str, name: str, symbol: str, max_supply: str, amount_per_mint: str,
                   mint_price_wei: str, quote_token: str = "0x0000000000000000000000000000000000000000",
                   creator_fee_bps: int = 100, free_mints_per_wallet: int = 1,
                   max_mints_per_wallet: int = 0) -> dict:
    """Prepare launching a fair-mint token (burns 1,000 $BOARD). Returns approve + launch steps.

    Units: max_supply and amount_per_mint are WHOLE TOKENS (e.g. "21000000", "1000") — the backend
    scales them to 18 decimals, so do NOT pass base units/wei. mint_price_wei is in WEI of the pair
    asset (e.g. "200000000000000" = 0.0002 ETH)."""
    return _post("/prepare/launch", {
        "wallet": wallet, "name": name, "symbol": symbol, "maxSupply": max_supply,
        "amountPerMint": amount_per_mint, "mintPriceWei": mint_price_wei, "quoteToken": quote_token,
        "creatorFeeBps": creator_fee_bps, "freeMintsPerWallet": free_mints_per_wallet,
        "maxMintsPerWallet": max_mints_per_wallet})


@mcp.tool()
def prepare_transfer(to: str, value_wei: str) -> dict:
    """Prepare a native Robinhood-Chain ETH transfer (fund/withdraw an agentic wallet). Your own
    funds, no voucher — sign with baw."""
    return _post("/prepare/transfer", {"to": to, "value_wei": value_wei})


if __name__ == "__main__":
    mcp.run()
