#!/usr/bin/env node
// StockerPunk MCP server — read BNB Chain + build calldata. Signing goes through the Agentic Wallet (baw).
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { execFile } from "node:child_process";

const CFG = {
  CHAIN_ID: 56,
  RPCS: ["https://bsc-rpc.publicnode.com", "https://binance.llamarpc.com", "https://bsc-dataseed.binance.org"],
  CONTRACTS: { nft: "0xfD81e3e5853553D43e4BD3D0bCDE98c69E86c98c", vault: "0x50F03C2034942f1C032a466F5dBb3a1fc9477504", spunk: "0x5d392B52868077b9Ba5391eeF734820865CD0de6" }, // LIVE on BSC
  TOKENS: { agentId: "0x60b9262456de011f7d15a54cdd8c48baaa8b022f", nvda: "0x02fca66c1d1afb4e2a7884261eb00f63598a7436" },
  SUPPLY: 5000, PRICE_USD: 1, MAX_PER_WALLET: 5,
  RARITY: [["Retail", 1.0], ["Day Trader", 1.6], ["Broker", 2.5], ["Quant", 4.0], ["Whale", 8.0]],
  SEL: { mint: "0xa0712d68", harvest: "0xddc63262", totalMinted: "0xa2309ff8", mintPriceWei: "0xcb2c9722",
    tokensOfOwner: "0x8462151c", rarityOf: "0xdd3b5f9a", pendingStock: "0x5d9fd0ea", balanceOf: "0x70a08231", minted: "0x1e7269c5" },
};
const live = () => !!CFG.CONTRACTS.nft;
const padU = (n) => BigInt(n).toString(16).padStart(64, "0");
const padA = (a) => a.toLowerCase().replace(/^0x/, "").padStart(64, "0");
const toBI = (h) => BigInt(h && h !== "0x" ? h : "0");
async function call(to, data) {
  const body = JSON.stringify({ jsonrpc: "2.0", id: 1, method: "eth_call", params: [{ to, data }, "latest"] });
  for (const url of CFG.RPCS) { try { const r = await fetch(url, { method: "POST", headers: { "content-type": "application/json" }, body }); const j = await r.json(); if (j && j.result !== undefined) return j.result; } catch {} }
  throw new Error("rpc unreachable");
}
const baw = (args) => new Promise((res) => execFile("baw", [...args, "--json"], (e, so) => { try { res(JSON.parse(so || (e && e.stdout) || "null")); } catch { res(null); } }));
async function bawAddr() { const r = await baw(["wallet", "address"]); const l = r?.data?.addresses; const h = l?.find((x) => String(x.binanceChainId) === "56"); return h?.address || null; }
async function hasAgent(a) { try { return toBI(await call(CFG.TOKENS.agentId, CFG.SEL.balanceOf + padA(a))) > 0n; } catch { return null; } }
async function bnbUsd() { try { const r = await fetch("https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"); return parseFloat((await r.json()).price) || 0; } catch { return 0; } }
const ok = (o) => ({ content: [{ type: "text", text: JSON.stringify(o, null, 2) }] });

const server = new McpServer({ name: "stockerpunk", version: "0.1.0" });

server.registerTool("spunk_preflight",
  { title: "Preflight", description: "Check sign-in, Developer Mode, Agent ID and remaining mint slots. Never spends gas." },
  async () => {
    const st = await baw(["wallet", "status"]);
    if (st?.data?.status !== "CONNECTED") return ok({ status: "UNCONNECTED", fix: "Run `baw auth signin` and confirm in the Binance App." });
    const addr = await bawAddr(); const set = await baw(["wallet", "settings"]);
    const devMode = !!set?.data?.devMode?.enabled; const isAgent = addr ? await hasAgent(addr) : null;
    let owned = 0; if (live() && addr) { try { owned = Number(toBI(await call(CFG.CONTRACTS.nft, CFG.SEL.minted + padA(addr)))); } catch {} }
    const issues = [];
    if (!devMode) issues.push({ code: "DEV_MODE_OFF", fix: "Enable Developer Mode in the Binance App." });
    if (isAgent === false) issues.push({ code: "NO_AGENT_ID", fix: "Claim a .ai Agent ID in Binance Wallet." });
    return ok({ status: issues.length ? "NOT_READY" : "READY", address: addr, isAgent, devMode, owned, slotsLeft: Math.max(0, CFG.MAX_PER_WALLET - owned), live: live(), issues });
  });

server.registerTool("spunk_collection",
  { title: "Collection", description: "Supply, mint price (USD + live BNB), and progress. Works before launch." },
  async () => {
    if (!live()) { const bu = await bnbUsd(); return ok({ live: false, supply: CFG.SUPPLY, priceUsd: CFG.PRICE_USD, priceBnb: "0.00133", maxPerWallet: CFG.MAX_PER_WALLET, firstMintFree: true, note: "First mint free, then 0.00133 BNB. Opens at launch." }); }
    const minted = Number(toBI(await call(CFG.CONTRACTS.nft, CFG.SEL.totalMinted)));
    const price = toBI(await call(CFG.CONTRACTS.nft, CFG.SEL.mintPriceWei));
    return ok({ live: true, minted, supply: CFG.SUPPLY, priceUsd: CFG.PRICE_USD, priceBnb: (Number(price) / 1e18).toFixed(6), maxPerWallet: CFG.MAX_PER_WALLET, firstMintFree: true });
  });

server.registerTool("spunk_mint",
  { title: "Build mint", description: "Build a mint transaction for 1-5 punks. Returns a `baw contract-call preview` command to run, confirm, then execute. Does not sign.", inputSchema: { count: z.number().int().min(1).max(5).default(1) } },
  async ({ count }) => {
    if (!live()) return ok({ success: false, error: "NOT_LIVE", note: "Minting opens at launch." });
    const addr = await bawAddr(); if (!addr) return ok({ success: false, error: "run `baw auth signin`" });
    if ((await hasAgent(addr)) === false) return ok({ success: false, error: "NO_AGENT_ID" });
    const owned = Number(toBI(await call(CFG.CONTRACTS.nft, CFG.SEL.minted + padA(addr))));
    if (owned + count > CFG.MAX_PER_WALLET) return ok({ success: false, error: `WALLET_CAP: ${CFG.MAX_PER_WALLET - owned} slots left` });
    const price = toBI(await call(CFG.CONTRACTS.nft, CFG.SEL.mintPriceWei)); const billable = count - (owned === 0 ? 1 : 0); const value = (price * BigInt(billable)).toString();
    const data = CFG.SEL.mint + padU(count);
    return ok({ success: true, count, to: CFG.CONTRACTS.nft, valueWei: value, data,
      bawPreview: `baw contract-call preview --binanceChainId 56 --from ${addr} --to ${CFG.CONTRACTS.nft} --value ${value} --inputData ${data} --json`,
      next: "Run bawPreview, show the user the parsed tx + cost, confirm, then `baw contract-call execute --requestId <id>`." });
  });

server.registerTool("spunk_punks",
  { title: "List punks", description: "List a wallet's punks with rarity, mining weight and NVDA mined.", inputSchema: { address: z.string().optional() } },
  async ({ address }) => {
    if (!live()) return ok({ success: false, error: "NOT_LIVE" });
    const addr = address || await bawAddr(); if (!addr) return ok({ success: false, error: "no address" });
    const hex = await call(CFG.CONTRACTS.nft, CFG.SEL.tokensOfOwner + padA(addr));
    const w = hex.replace(/^0x/, ""); const words = w.match(/.{1,64}/g) || []; const len = words[1] ? Number(toBI("0x" + words[1])) : 0;
    const ids = words.slice(2, 2 + len).map((x) => Number(toBI("0x" + x)));
    const punks = [];
    for (const id of ids) { const r = Number(toBI(await call(CFG.CONTRACTS.nft, CFG.SEL.rarityOf + padU(id)))); const t = CFG.RARITY[r] || CFG.RARITY[0];
      let mined = "0"; try { mined = (Number(toBI(await call(CFG.CONTRACTS.vault, CFG.SEL.pendingStock + padU(id)))) / 1e18).toFixed(4); } catch {}
      punks.push({ id, rarity: t[0], weight: t[1], minedNvda: mined }); }
    return ok({ success: true, address: addr, count: punks.length, punks });
  });

server.registerTool("spunk_harvest",
  { title: "Build harvest", description: "Build a harvest transaction for one punk. Returns a `baw contract-call preview` command. Does not sign.", inputSchema: { id: z.number().int() } },
  async ({ id }) => {
    if (!live()) return ok({ success: false, error: "NOT_LIVE" });
    const addr = await bawAddr(); if (!addr) return ok({ success: false, error: "run `baw auth signin`" }); const data = CFG.SEL.harvest + padU(id);
    return ok({ success: true, id, to: CFG.CONTRACTS.vault, data,
      bawPreview: `baw contract-call preview --binanceChainId 56 --from ${addr} --to ${CFG.CONTRACTS.vault} --value 0 --inputData ${data} --json`,
      next: "Run bawPreview, confirm, then `baw contract-call execute --requestId <id>`." });
  });

await server.connect(new StdioServerTransport());
