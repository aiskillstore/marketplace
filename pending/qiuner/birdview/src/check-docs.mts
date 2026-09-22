import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

// Source: src/check-docs.mts. Regenerate scripts/check-docs.mjs with npm run build.

const root = fileURLToPath(new URL('../', import.meta.url));
const files: string[] = [];
function collect(directory: string, recursive: boolean): void {
  for (const entry of fs.readdirSync(path.join(root, directory), { withFileTypes: true })) {
    const file = path.posix.join(directory, entry.name);
    if (entry.isDirectory() && recursive) collect(file, true);
    else if (entry.isFile() && entry.name.endsWith('.md')) files.push(file);
  }
}
collect('', false);
for (const directory of ['references', 'docs', 'examples', '.github']) collect(directory, true);
const hashes: Record<string, string> = {};
const errors: string[] = [];
for (const file of files.sort()) {
  const text = fs.readFileSync(path.join(root, file), 'utf8').replace(/\r\n/g, '\n');
  const counterpart = file.endsWith('.zh.md') ? file.replace(/\.zh\.md$/, '.md') : file.replace(/\.md$/, '.zh.md');
  if (!files.includes(counterpart)) errors.push(`${file}: missing ${counterpart}`);
  if (!text.includes(`](${path.posix.basename(counterpart)})`)) errors.push(`${file}: missing language link`);
  for (const match of text.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
    const target = match[1]?.split('#')[0];
    if (!target || /^[a-z]+:/i.test(target) || target.includes('<')) continue;
    if (!fs.existsSync(path.resolve(root, path.dirname(file), decodeURIComponent(target)))) errors.push(`${file}: broken link ${target}`);
  }
  hashes[file] = crypto.createHash('sha256').update(text).digest('hex');
}
const record = path.join(root, 'docs/i18n.json');
const update = process.argv.slice(2).includes('--update');
if (!update) {
  const parsed: unknown = fs.existsSync(record) ? JSON.parse(fs.readFileSync(record, 'utf8')) : {};
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) throw new Error('Documentation hash record must be an object.');
  const saved = new Map<string, unknown>(Object.entries(parsed));
  for (const file of new Set([...saved.keys(), ...Object.keys(hashes)])) {
    if (saved.get(file) !== hashes[file]) errors.push(`${file}: synchronization confirmation required`);
  }
}
if (errors.length) {
  console.error(errors.join('\n'));
  process.exitCode = 1;
} else if (update) {
  fs.writeFileSync(record, `${JSON.stringify(hashes, null, 2)}\n`);
  console.log(`Recorded ${files.length / 2} documentation pairs.`);
} else console.log(`Verified ${files.length / 2} documentation pairs and local links.`);
