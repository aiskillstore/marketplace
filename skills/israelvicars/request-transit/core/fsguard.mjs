// core/fsguard.mjs: the only way Transit clears output. No recursive deletes: a frames folder is emptied
// by removing just the files Transit writes there (NNNN.png and the .transit-frames marker), then the folder
// itself if that left it empty. Filesystem roots, the home directory, the repo root, the working directory
// and any of their ancestors are refused outright, whatever --frames / --out / --out-dir say.
import { existsSync, lstatSync, readdirSync, rmdirSync, unlinkSync, writeFileSync, mkdirSync, realpathSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, parse, resolve, relative, isAbsolute, sep } from 'node:path';
import { ROOT } from './tools.mjs';
import { UserError } from './cli.mjs';

export const FRAME_FILE = /^\d{4}\.png$/;
export const FRAMES_MARKER = '.transit-frames';
const real = (p) => { try { return realpathSync(p); } catch { return resolve(p); } };
const isInside = (child, parent) => { const r = relative(parent, child); return r === '' || (!r.startsWith('..') && !isAbsolute(r)); };

// throws when `dir` is a place no Transit output folder may be
export function assertSafeOutputDir(dir, what = 'output folder') {
  const d = real(resolve(dir));
  const protectedDirs = [parse(d).root, homedir(), ROOT, process.cwd()].map(real);
  for (const p of protectedDirs) if (isInside(p, d)) throw new UserError(`refusing to use ${dir} as the ${what}: it is ${p === d ? '' : 'an ancestor of '}${p === parse(d).root ? 'the filesystem root' : p === real(homedir()) ? 'your home directory' : p === real(ROOT) ? 'the Transit repo root' : 'the current directory'}. Pick a dedicated folder, e.g. out/frames.`);
  return d;
}

// empties a frames folder of Transit's own files only; returns the number of files removed
export function clearFrames(dir) {
  const d = assertSafeOutputDir(dir, 'frames folder');
  if (!existsSync(d)) return 0;
  if (!lstatSync(d).isDirectory()) throw new UserError(`${dir} exists and is not a folder`);
  let n = 0;
  for (const f of readdirSync(d)) if (FRAME_FILE.test(f) || f === FRAMES_MARKER) { const p = join(d, f); if (lstatSync(p).isFile()) { unlinkSync(p); n++; } }
  return n;
}
// clears, then removes the folder only if nothing else is left in it
export function removeFramesDir(dir) {
  const n = clearFrames(dir);
  const d = resolve(dir);
  if (existsSync(d) && readdirSync(d).length === 0) rmdirSync(d);
  return n;
}
export function prepareFramesDir(dir) {
  const d = assertSafeOutputDir(dir, 'frames folder');
  mkdirSync(d, { recursive: true });
  writeFileSync(join(d, FRAMES_MARKER), 'frames written by Transit; safe to delete\n');
  return d;
}
// a --name becomes a folder under out/: one path segment, no separators or dot-dot
export function safeName(name) {
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/.test(name) || name.includes('..') || name.includes(sep)) throw new UserError(`--name must be a simple folder name (letters, digits, . _ -), got ${JSON.stringify(name)}`);
  return name;
}
