#!/usr/bin/env node
// src/request-transit/scripts/transit.mjs: `transit index` builds the OPTIONAL contract index. Nothing indexes code unless this
// command is run on purpose (the skill asks the user first).
//   node src/request-transit/scripts/transit.mjs index [--config transit.config.json] [--cache .transit-cache/contracts]
//   node src/request-transit/scripts/transit.mjs index --print     (also print a per-service summary)
import { buildIndex } from '../contracts/indexer.mjs';
import { existsSync } from 'node:fs';
const [cmd, ...rest] = process.argv.slice(2); const opt = {};
for (let i = 0; i < rest.length; i++) if (rest[i].startsWith('--')) { const k = rest[i].slice(2); opt[k] = rest[i + 1] && !rest[i + 1].startsWith('--') ? rest[++i] : true; }
if (cmd !== 'index') { console.error('usage: node src/request-transit/scripts/transit.mjs index [--config transit.config.json] [--cache DIR] [--print]'); process.exit(1); }
const config = opt.config || 'transit.config.json';
if (!existsSync(config)) { console.error(`no config at ${config}; see references/config.md`); process.exit(1); }
const { index, latest } = buildIndex(config, { cacheDir: opt.cache || '.transit-cache/contracts', log: console.log });
if (opt.print) for (const [s, v] of Object.entries(index.services)) console.log(`  ${s.padEnd(18)} ${String(v.entries).padStart(3)} entries  ${v.files} files${v.notRead ? '  not read: ' + v.notRead.join(', ') : ''}`);
console.log(`latest index: ${latest}  (build with --contracts to use it)`);
