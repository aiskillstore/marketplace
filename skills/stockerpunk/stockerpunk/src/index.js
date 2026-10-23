#!/usr/bin/env node
"use strict";
// StockerPunk CLI — reads BNB Chain + builds calldata; signing goes through `baw`. No keys held here.
const { execFileSync } = require("child_process");
const CFG = require("./config");

// ---------- helpers ----------
const out = (o) => { process.stdout.write(JSON.stringify(o, null, 2) + "\n"); };
const err = (e) => { out({ success: false, error: e }); process.exit(0); };
function flags(argv) { const f = {}; for (let i = 0; i < argv.length; i++) { if (argv[i].startsWith("--")) { const k = argv[i].slice(2); const v = (argv[i + 1] && !argv[i + 1].startsWith("--")) ? argv[++i] : true; f[k] = v; } } return f; }
const padU = (n) => BigInt(n).toString(16).padStart(64, "0");
const padA = (a) => a.toLowerCase().replace(/^0x/, "").padStart(64, "0");
const toBI = (hex) => BigInt(hex && hex !== "0x" ? hex : "0");

async function rpc(to, data) {
  const body = JSON.stringify({ jsonrpc: "2.0", id: 1, method: "eth_call", params: [{ to, data }, "latest"] });
  for (const url of CFG.RPCS) {
    try {
      const r = await fetch(url, { method: "POST", headers: { "content-type": "application/json" }, body });
      const j = await r.json(); if (j && j.result !== undefined) return j.result;
    } catch (_) {}
  }
  throw new Error("RPC unreachable");
}
function baw(args) { try { return JSON.parse(execFileSync("baw", [...args, "--json"], { encoding: "utf8" })); } catch (e) { try { return JSON.parse(e.stdout); } catch (_) { return null; } } }

function bawAddress() {
  const r = baw(["wallet", "address"]);
  const list = r && r.data && r.data.addresses;
  if (!list) return null;
  const hit = list.find((x) => String(x.binanceChainId) === String(CFG.CHAIN_ID));
  return hit ? hit.address : null;
}
async function hasAgentId(addr) {
  try { const r = await rpc(CFG.TOKENS.agentId, CFG.SEL.balanceOf + padA(addr)); return toBI(r) > 0n; } catch (_) { return null; }
}
async function bnbUsd() {
  try { const r = await fetch("https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"); const j = await r.json(); return parseFloat(j.price) || 0; } catch (_) { return 0; }
}
const live = () => !!CFG.CONTRACTS.nft;

// ---------- commands ----------
async function preflight() {
  const st = baw(["wallet", "status"]);
  if (!st || !st.data || st.data.status !== "CONNECTED")
    return out({ success: false, status: "UNCONNECTED", issues: [{ code: "NOT_SIGNED_IN", fix: "Run `baw auth signin` and confirm in the Binance App." }] });
  const addr = bawAddress();
  const set = baw(["wallet", "settings"]);
  const devMode = !!(set && set.data && set.data.devMode && set.data.devMode.enabled);
  const isAgent = addr ? await hasAgentId(addr) : null;
  let owned = 0;
  if (live() && addr) { try { owned = Number(toBI(await rpc(CFG.CONTRACTS.nft, CFG.SEL.minted + padA(addr)))); } catch (_) {} }
  const issues = [];
  if (!devMode) issues.push({ code: "DEV_MODE_OFF", fix: "Enable Developer Mode in the Binance App (needed for any contract call)." });
  if (isAgent === false) issues.push({ code: "NO_AGENT_ID", fix: "Claim a .ai Agent ID from the Agent ID banner in Binance Wallet (required to mint)." });
  out({ success: issues.length === 0, status: issues.length ? "NOT_READY" : "READY", address: addr, isAgent, devMode, owned, slotsLeft: Math.max(0, CFG.MAX_PER_WALLET - owned), live: live(), issues });
}

async function collection() {
  if (!live()) { const bu = await bnbUsd(); const pb = "0.00133"; return out({ success: true, live: false, supply: CFG.SUPPLY, priceUsd: CFG.PRICE_USD, priceBnb: pb, bnbUsd: bu || null, maxPerWallet: CFG.MAX_PER_WALLET, firstMintFree: true, note: "First mint free, then 0.00133 BNB. Opens at launch; priceBnb is a live estimate." }); }
  const minted = Number(toBI(await rpc(CFG.CONTRACTS.nft, CFG.SEL.totalMinted)));
  const supply = Number(toBI(await rpc(CFG.CONTRACTS.nft, CFG.SEL.maxSupply))) || CFG.SUPPLY;
  const priceWei = toBI(await rpc(CFG.CONTRACTS.nft, CFG.SEL.mintPriceWei));
  out({ success: true, live: true, minted, supply, priceUsd: CFG.PRICE_USD, priceBnb: (Number(priceWei) / 1e18).toFixed(6), maxPerWallet: CFG.MAX_PER_WALLET, firstMintFree: true });
}

async function mint(f) {
  const count = Number(f.count || 1);
  if (!(count >= 1 && count <= CFG.MAX_PER_WALLET)) return err("count must be 1-" + CFG.MAX_PER_WALLET);
  if (!live()) return err("NOT_LIVE");
  const addr = f.from || bawAddress();
  if (!addr) return err("no agentic wallet address; run `baw auth signin`");
  if ((await hasAgentId(addr)) === false) return err("NO_AGENT_ID");
  const owned = Number(toBI(await rpc(CFG.CONTRACTS.nft, CFG.SEL.minted + padA(addr))));
  if (owned + count > CFG.MAX_PER_WALLET) return err("WALLET_CAP: " + (CFG.MAX_PER_WALLET - owned) + " slots left");
  const priceWei = toBI(await rpc(CFG.CONTRACTS.nft, CFG.SEL.mintPriceWei));
  const billable = count - (owned === 0 ? 1 : 0); // first mint per wallet is free
  const valueWei = (priceWei * BigInt(billable)).toString();
  const data = CFG.SEL.mint + padU(count);
  out({ success: true, count, to: CFG.CONTRACTS.nft, valueWei, valueBnb: (Number(valueWei) / 1e18).toFixed(6), data,
    bawPreview: `baw contract-call preview --binanceChainId ${CFG.CHAIN_ID} --from ${addr} --to ${CFG.CONTRACTS.nft} --value ${valueWei} --inputData ${data} --json`,
    note: "Run bawPreview, show the user, confirm, then `baw contract-call execute --requestId <id>`." });
}

function decU256Array(hex) {
  const w = hex.replace(/^0x/, ""); if (w.length < 128) return [];
  const words = w.match(/.{1,64}/g); const len = Number(BigInt("0x" + words[1]));
  return words.slice(2, 2 + len).map((x) => Number(BigInt("0x" + x)));
}
async function punks(f) {
  const addr = f.address || bawAddress();
  if (!addr) return err("no address; pass --address or run `baw auth signin`");
  if (!live()) return err("NOT_LIVE");
  const ids = decU256Array(await rpc(CFG.CONTRACTS.nft, CFG.SEL.tokensOfOwner + padA(addr)));
  const list = [];
  for (const id of ids) {
    const rar = Number(toBI(await rpc(CFG.CONTRACTS.nft, CFG.SEL.rarityOf + padU(id))));
    const t = CFG.RARITY[rar] || { name: "?", weight: 0 };
    let mined = "0"; try { mined = (Number(toBI(await rpc(CFG.CONTRACTS.vault, CFG.SEL.pendingStock + padU(id)))) / 1e18).toFixed(4); } catch (_) {}
    let acct = null; try { acct = "0x" + (await rpc(CFG.CONTRACTS.nft, CFG.SEL.accountOf + padU(id))).slice(-40); } catch (_) {}
    list.push({ id, rarity: t.name, weight: t.weight, minedNvda: mined, account: acct });
  }
  out({ success: true, address: addr, count: list.length, totalWeight: list.reduce((s, p) => s + p.weight, 0), punks: list });
}

async function harvest(f) {
  const id = f.id;
  if (id === undefined) return err("pass --id <tokenId>");
  if (!live()) return err("NOT_LIVE");
  const addr = f.from || bawAddress();
  if (!addr) return err("no agentic wallet address; run `baw auth signin`");
  const data = CFG.SEL.harvest + padU(id);
  out({ success: true, id: Number(id), to: CFG.CONTRACTS.vault, data,
    bawPreview: `baw contract-call preview --binanceChainId ${CFG.CHAIN_ID} --from ${addr} --to ${CFG.CONTRACTS.vault} --value 0 --inputData ${data} --json`,
    note: "Run bawPreview, confirm, then `baw contract-call execute --requestId <id>`." });
}

// ---------- router ----------
(async () => {
  const argv = process.argv.slice(2); const cmd = argv[0]; const f = flags(argv.slice(1));
  try {
    if (cmd === "preflight") return await preflight();
    if (cmd === "collection") return await collection();
    if (cmd === "mint") return await mint(f);
    if (cmd === "punks") return await punks(f);
    if (cmd === "punk") { f.address = f.address; return await punks(f); } // single-id filtering left to caller
    if (cmd === "harvest") return await harvest(f);
    out({ success: true, name: "spunk", commands: ["preflight", "collection", "mint", "punks", "harvest"], chain: CFG.CHAIN_NAME, supply: CFG.SUPPLY, live: live() });
  } catch (e) { err(String(e.message || e)); }
})();
