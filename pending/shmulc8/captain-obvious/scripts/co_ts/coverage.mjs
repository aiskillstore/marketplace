import fs from 'node:fs';
import path from 'node:path';

export function loadCoverage(file, projectDir) {
  let raw;
  try { raw = fs.readFileSync(file, 'utf8'); } catch { return null; }
  const map = new Map();
  const norm = (p) => path.relative(projectDir, path.isAbsolute(p) ? p : path.resolve(projectDir, p))
    .split(path.sep).join('/');
  const put = (p, line, hits) => {
    const rel = norm(p);
    let m = map.get(rel);
    if (!m) { m = new Map(); map.set(rel, m); }
    m.set(line, Math.max(m.get(line) ?? 0, hits));
  };
  const trimmed = raw.trimStart();
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
    let json;
    try { json = JSON.parse(raw); } catch { return null; }
    if (json && json.files && typeof json.files === 'object') {
      for (const [p, d] of Object.entries(json.files)) {
        for (const ln of d.executed_lines ?? []) put(p, ln, 1);
        for (const ln of d.missing_lines ?? []) put(p, ln, 0);
      }
    } else if (json && typeof json === 'object') {
      for (const [p, d] of Object.entries(json)) {
        if (!d || !d.statementMap || !d.s) continue;
        for (const [id, loc] of Object.entries(d.statementMap)) {
          const line = loc?.start?.line;
          if (line == null) continue;
          put(d.path ?? p, line, d.s[id] ?? 0);
        }
      }
    }
  } else {
    let cur = null;
    for (const line of raw.split(/\r?\n/)) {
      if (line.startsWith('SF:')) cur = line.slice(3).trim();
      else if (line.startsWith('DA:') && cur) {
        const [ln, hits] = line.slice(3).split(',');
        put(cur, parseInt(ln, 10), parseInt(hits, 10) || 0);
      } else if (line.startsWith('end_of_record')) cur = null;
    }
  }
  if (map.size === 0) return null;
  return {
    hits(relFile, line) {
      const m = map.get(String(relFile).split(path.sep).join('/'));
      if (!m) return undefined;
      return m.has(line) ? m.get(line) : undefined;
    },
    hasFile(relFile) {
      return map.has(String(relFile).split(path.sep).join('/'));
    },
  };
}
