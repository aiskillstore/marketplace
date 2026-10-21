import fs from 'node:fs';
import path from 'node:path';

export const SKIP_DIRS = new Set(['node_modules', '.git', 'dist', 'build', 'out', 'coverage', '.next', '.turbo']);
export const TEST_RE = /\.(test|spec)\.(ts|tsx|mts|cts|js|jsx|mjs|cjs)$/;

export function findTestFiles(root) {
  const found = [];
  (function walk(dir) {
    let entries;
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (e.isDirectory()) {
        if (!SKIP_DIRS.has(e.name) && !e.name.startsWith('.')) walk(path.join(dir, e.name));
      } else if (TEST_RE.test(e.name) ||
                 (/\.(ts|tsx|js|jsx)$/.test(e.name) && path.basename(dir) === '__tests__')) {
        found.push(path.join(dir, e.name));
      }
    }
  })(root);
  return found.sort();
}
