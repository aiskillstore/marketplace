import { readdirSync, readFileSync, statSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, resolve } from 'node:path';

const source = process.argv[process.argv.indexOf('--source') + 1];
if (!['claude-code', 'codex', 'cursor'].includes(source)) throw new Error('usage: node find-session.mjs --source claude-code|codex|cursor');
const cwd = resolve(process.cwd()), home = homedir();
const newest = (items) => items.sort((a, b) => b.mtime - a.mtime)[0];
const mtime = (path) => { try { return statSync(path).mtimeMs; } catch { return 0; } };
const entries = (dir) => { try { return readdirSync(dir, { withFileTypes: true }); } catch { return []; } };

if (source === 'cursor') {
  const root = join(home, '.cursor', 'projects'), matches = [];
  for (const project of entries(root)) {
    if (!project.isDirectory()) continue;
    const transcripts = join(root, project.name, 'agent-transcripts');
    for (const session of entries(transcripts)) {
      if (!session.isDirectory()) continue;
      const path = join(transcripts, session.name, `${session.name}.jsonl`);
      try { if (statSync(path).isFile()) matches.push({ path, mtime: mtime(path) }); } catch {}
    }
  }
  const match = newest(matches);
  if (match) console.log(match.path);
  else console.error('no Cursor agent-transcripts found; Cursor keeps chats in its state.vscdb instead. Export one (metadata only): node <skill>/scripts/export-cursor.mjs --list, then --composer ID');
} else if (source === 'codex') {
  const root = join(home, '.codex', 'sessions'), matches = [];
  const walk = (dir) => {
    for (const entry of entries(dir)) {
      const path = join(dir, entry.name);
      if (entry.isDirectory()) walk(path);
      else if (entry.isFile() && entry.name.endsWith('.jsonl')) {
        try {
          const first = readFileSync(path, 'utf8').split(/\r?\n/, 1)[0];
          const line = JSON.parse(first);
          if (line.type === 'session_meta' && (line.payload?.cwd || line.cwd) === cwd) matches.push({ path, mtime: mtime(path) });
        } catch {}
      }
    }
  };
  walk(root); const match = newest(matches); if (match) console.log(match.path);
} else {
  const root = join(home, '.claude', 'projects'), encoded = cwd.replaceAll('/', '-'), matches = [];
  const walk = (dir) => {
    for (const entry of entries(dir)) {
      const path = join(dir, entry.name);
      if (entry.isDirectory()) walk(path);
      else if (entry.isFile() && entry.name.endsWith('.jsonl') && path.includes(encoded)) matches.push({ path, mtime: mtime(path) });
    }
  };
  walk(root); const match = newest(matches); if (match) console.log(match.path);
}
