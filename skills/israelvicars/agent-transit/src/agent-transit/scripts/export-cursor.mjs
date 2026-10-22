// export-cursor.mjs: Cursor IDE agent sessions ("composers") live in Cursor's SQLite store, not in files:
//   <Cursor user dir>/globalStorage/state.vscdb, table cursorDiskKV
//     composerData:<composerId>         fullConversationHeadersOnly = [{bubbleId, type}] in conversation order
//     bubbleId:<composerId>:<bubbleId>  type 1 = user, 2 = assistant; createdAt (ISO, Cursor builds since ~Sep 2025);
//                                       timingInfo {clientRpcSendTime, clientEndTime} on user turns (epoch ms);
//                                       toolFormerData {name, status: completed|error|cancelled, params, rawArgs, result}
//   <Cursor user dir>/workspaceStorage/<hash>/state.vscdb ItemTable 'composer.composerData' lists a workspace's composers.
// This writes ONE composer as JSON Lines in that bubble shape, metadata only: ids, type, createdAt, timing, tool name,
// status and a file basename / command word. Message text, thinking, tool params and results are never selected
// (the SQL pulls only those fields with json_extract), so they never leave the database.
// The database is opened read-only (sqlite3 CLI with argument arrays, or node:sqlite where the CLI is missing).
//
// usage: node export-cursor.mjs [--list] [--composer ID|prefix] [--workspace DIR (default: cwd)] [--all-workspaces]
//                               [--db path/to/state.vscdb] [--out session.cursor.jsonl]
//   --list            newest composers with tool calls: id, date, bubbles, tool calls, timestamps (no titles)
//   default           newest composer with tool calls in the cwd's Cursor workspace (or any, with --all-workspaces)
import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { basename, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const argv = process.argv.slice(2), opt = {};
for (let i = 0; i < argv.length; i++) if (argv[i].startsWith('--')) opt[argv[i].slice(2)] = ['list', 'all-workspaces'].includes(argv[i].slice(2)) ? true : argv[++i];
const die = (m) => { console.error(`export-cursor: ${m}`); process.exit(1); };
const userDir = process.platform === 'darwin' ? join(homedir(), 'Library/Application Support/Cursor/User')
  : process.platform === 'win32' ? join(process.env.APPDATA || join(homedir(), 'AppData/Roaming'), 'Cursor/User') : join(homedir(), '.config/Cursor/User');
const dbPath = resolve(opt.db || join(userDir, 'globalStorage/state.vscdb'));
if (!existsSync(dbPath)) die(`no Cursor database at ${dbPath} (pass --db)`);

let nodeSqlite = null;
async function query(db, sql) {
  try { return JSON.parse(execFileSync('sqlite3', ['-readonly', '-json', db, sql], { encoding: 'utf8', maxBuffer: 1 << 28, stdio: ['ignore', 'pipe', 'pipe'] }) || '[]'); }
  catch (e) {
    if (e.code !== 'ENOENT') die(`sqlite3 could not read ${db}: ${String(e.stderr || e.message).trim().split('\n')[0]}`);
    if (!nodeSqlite) {
      const emit = process.emitWarning; process.emitWarning = (w, ...a) => (/SQLite/.test(String(w)) ? undefined : emit.call(process, w, ...a));
      try { nodeSqlite = await import('node:sqlite'); } catch { die('needs the sqlite3 command or Node 22.5+ (node:sqlite)'); }
    }
    const h = new nodeSqlite.DatabaseSync(db, { readOnly: true });
    try { return h.prepare(sql).all(); } finally { h.close(); }
  }
}
const ID = /^[0-9a-f-]{4,36}$/i;   // composer ids are UUIDs; validated before they go into SQL

// composers belonging to a workspace folder, from workspaceStorage
function workspaceComposers(dir) {
  const want = pathToFileURL(resolve(dir)).href.replace(/\/$/, '');
  const root = join(userDir, 'workspaceStorage');
  let hashes = []; try { hashes = readdirSync(root); } catch { return null; }
  for (const h of hashes) {
    try { const w = JSON.parse(readFileSync(join(root, h, 'workspace.json'), 'utf8')); if (String(w.folder || '').replace(/\/$/, '') === want) return join(root, h, 'state.vscdb'); } catch {}
  }
  return null;
}

const summarySql = `select substr(c.key, 14) id, json_extract(c.value, '$.createdAt') createdAt,
  (select count(*) from cursorDiskKV b where b.key > 'bubbleId:' || substr(c.key, 14) || ':' and b.key < 'bubbleId:' || substr(c.key, 14) || ';') bubbles,
  (select count(*) from cursorDiskKV b where b.key > 'bubbleId:' || substr(c.key, 14) || ':' and b.key < 'bubbleId:' || substr(c.key, 14) || ';' and json_extract(b.value, '$.toolFormerData.name') is not null) tools,
  (select count(*) from cursorDiskKV b where b.key > 'bubbleId:' || substr(c.key, 14) || ':' and b.key < 'bubbleId:' || substr(c.key, 14) || ';' and json_extract(b.value, '$.createdAt') is not null) timed
  from cursorDiskKV c where c.key like 'composerData:%' and json_valid(c.value)`;

let scope = null;
if (!opt.composer && !opt['all-workspaces']) {
  const wdb = workspaceComposers(opt.workspace || process.cwd());
  if (wdb) {
    const rows = await query(wdb, `select value from ItemTable where key = 'composer.composerData'`);
    try { scope = new Set((JSON.parse(rows[0].value).allComposers || []).map((c) => c.composerId).filter((x) => ID.test(x))); } catch { scope = new Set(); }
  } else if (opt.list) console.error(`no Cursor workspace for ${resolve(opt.workspace || process.cwd())}; listing all workspaces`);
  else die(`no Cursor workspace for ${resolve(opt.workspace || process.cwd())}; pass --workspace DIR, --composer ID or --all-workspaces (see --list --all-workspaces)`);
}
const all = (await query(dbPath, summarySql + (scope ? ` and substr(c.key, 14) in (${[...scope].map((x) => `'${x}'`).join(',') || "''"})` : '')))
  .filter((r) => r.tools > 0).sort((a, b) => (b.createdAt || 0) - (a.createdAt || 0));

if (opt.list) {
  for (const r of all.slice(0, 25)) console.log(`${r.id}  ${r.createdAt ? new Date(r.createdAt).toISOString().slice(0, 16).replace('T', ' ') : '????-??-??'}  ${String(r.bubbles).padStart(5)} bubbles  ${String(r.tools).padStart(5)} tool calls  ${r.timed ? 'timestamps' : 'order only'}`);
  if (!all.length) console.error('no composers with tool calls' + (scope ? ' in this workspace (try --all-workspaces)' : ''));
  process.exit(0);
}
let pick;
if (opt.composer) {
  if (!ID.test(opt.composer)) die('--composer takes a composer id or an id prefix (hex)');
  const m = all.filter((r) => r.id.startsWith(opt.composer.toLowerCase()));
  if (m.length !== 1) die(m.length ? `--composer ${opt.composer} is ambiguous (${m.length} matches)` : `no composer with tool calls matches ${opt.composer}`);
  pick = m[0];
} else if (!(pick = all[0])) die('no composer with tool calls found' + (scope ? ' in this workspace (try --all-workspaces)' : ''));

const head = await query(dbPath, `select json_extract(value, '$.fullConversationHeadersOnly') h from cursorDiskKV where key = 'composerData:${pick.id}'`);
let order = []; try { order = JSON.parse(head[0].h || '[]').map((x) => x.bubbleId); } catch {}
const rows = await query(dbPath, `select substr(key, ${'bubbleId:'.length + pick.id.length + 2}) bubbleId, json_extract(value, '$.type') type, json_extract(value, '$.createdAt') createdAt,
  json_extract(value, '$.timingInfo.clientRpcSendTime') rpcSend, json_extract(value, '$.timingInfo.clientEndTime') rpcEnd,
  json_extract(value, '$.toolFormerData.name') name, json_extract(value, '$.toolFormerData.status') status,
  ${TARGET_KEYS().map((k) => `json_extract(json_extract(value, '$.toolFormerData.params'), '$.${k}') "p_${k}"`).join(', ')}
  from cursorDiskKV where key > 'bubbleId:${pick.id}:' and key < 'bubbleId:${pick.id};' and json_valid(value)`);   // key range: uses the index
function TARGET_KEYS() { return ['relativeWorkspacePath', 'targetFile', 'directoryPath', 'targetDirectory', 'path', 'command', 'searchTerm', 'globPattern', 'query']; }
const byId = new Map(rows.map((r) => [r.bubbleId, r]));
const ordered = [...order.filter((id) => byId.has(id)).map((id) => byId.get(id)), ...rows.filter((r) => !order.includes(r.bubbleId)).sort((a, b) => String(a.createdAt).localeCompare(String(b.createdAt)))];
// a target is reduced here to what the page may show: a basename, or a command's first word
const target = (r) => {
  for (const k of ['relativeWorkspacePath', 'targetFile', 'directoryPath', 'targetDirectory', 'path', 'globPattern']) if (typeof r[`p_${k}`] === 'string' && r[`p_${k}`]) return { target_file: basename(r[`p_${k}`]) };
  if (typeof r.p_command === 'string') return { command: r.p_command.trim().split(/\s+/)[0].slice(0, 40) };
  return {};
};
const lines = [{ _agentFormat: 'cursor', _comment: `Cursor composer ${pick.id} from state.vscdb; metadata only (no text, params or results)` }];
for (const r of ordered) {
  const b = { bubbleId: r.bubbleId, type: r.type };
  if (r.createdAt) b.createdAt = r.createdAt;
  if (r.rpcSend || r.rpcEnd) b.timingInfo = { clientRpcSendTime: r.rpcSend ?? undefined, clientEndTime: r.rpcEnd ?? undefined };
  if (r.name) b.toolFormerData = { name: r.name, status: r.status || undefined, params: JSON.stringify(target(r)) };
  lines.push(b);
}
const out = opt.out || `cursor-${pick.id.slice(0, 8)}.cursor.jsonl`;
writeFileSync(out, lines.map((l) => JSON.stringify(l)).join('\n') + '\n');
console.log(`wrote ${out} (${pick.tools} tool calls, ${ordered.length} bubbles, ${pick.timed ? 'with timestamps' : 'no timestamps: order only'})`);
