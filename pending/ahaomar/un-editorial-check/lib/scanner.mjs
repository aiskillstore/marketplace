// File discovery.
//
// Defaults are deliberately conservative so a "scan the site" cannot drag in
// the skill's own source, coding-agent scratch directories, build output or
// test fixtures — the exclusions that stop self-referential findings. Hidden
// directories are skipped while walking unless the directory the user pointed
// at is itself hidden (so an explicit hidden path still works).
//
// The skill's own root carries a narrow shield: a scan whose input *is* the
// root (the bare `.` or the package directory) reads nothing and is recorded
// as the documented carve-out rather than an empty-scan refusal, and a walk
// never descends into the root. A file or a sub-directory named inside the
// root is scanned like any other input — only `--self-scan` opens the root
// itself.

import fs from 'node:fs';
import path from 'node:path';
import { EXTRACTABLE_EXTENSIONS } from './extract.mjs';

export class ScannerError extends Error {}

export const DEFAULT_EXCLUDES = [
  '.agents', '.opencode', '.claude', '.agent', 'agent', '.kilo',
  'node_modules', 'dist', 'build', 'coverage', 'fixtures', 'tests/fixtures',
];

function patternToRegex(pattern) {
  const escaped = pattern
    .replace(/[.+?^${}()|[\]\\]/g, '\\$&')
    .replace(/\*\*/g, '__DOUBLE__')
    .replace(/\*/g, '[^/]*')
    .replace(/__DOUBLE__/g, '.*');
  return new RegExp(`^${escaped}$`);
}

function isExcluded(nameOrRelPath, absPath, patterns, walkRoot = null) {
  const segments = absPath.split(path.sep);
  const absForward = absPath.split(path.sep).join('/');
  // A `dir/**` pattern is about a directory *inside* the scan, so it is matched
  // against the path relative to the walk root rather than the absolute path.
  // Absolute matching leaked the scan's own location into the decision: a skill
  // installed at `…/node_modules/un-editorial-check` matched `node_modules/**`
  // through its parent, so naming it — or self-scanning it — either read
  // everything, with no exclusion left in force, or with the correction below
  // read nothing at all. Relative to the walk root, `node_modules` is an
  // ancestor and matches nothing, while `fixtures` still matches `lib/fixtures`.
  const relSegments = walkRoot
    ? path.relative(walkRoot, absPath).split(path.sep).filter(Boolean)
    : segments;
  for (const pattern of patterns) {
    if (pattern.endsWith('/**')) {
      const prefix = pattern.slice(0, -3).split('/').filter(Boolean);
      for (let i = 0; i + prefix.length <= relSegments.length; i++) {
        if (prefix.every((part, j) => relSegments[i + j] === part)) return true;
      }
      continue;
    }
    if (pattern.includes('*')) {
      const re = patternToRegex(pattern);
      if (re.test(nameOrRelPath) || re.test(absForward)) return true;
      continue;
    }
    // Plain names match at any depth: `node_modules`, `tests/fixtures`.
    if (segments[segments.length - 1] === pattern) return true;
    if (absForward.endsWith(`/${pattern}`)) return true;
    if (nameOrRelPath === pattern || nameOrRelPath.startsWith(`${pattern}/`)) return true;
  }
  return false;
}

/**
 * Whether a pattern excludes a directory because of the directory's own name,
 * rather than because some ancestor segment matched. `fixtures` names `fixtures`
 * and lifts its own exclusion when named explicitly; `node_modules/**` does not
 * name `un-editorial-check` and must not lift anything for it.
 *
 * @param {string} named          basename of the directory named on the command line
 * @param {string[]} patterns     exclusion patterns in force
 * @returns {boolean}
 */
function excludedByOwnName(named, patterns) {
  return patterns.some((pattern) => {
    if (pattern.includes('*')) {
      // A glob names the directory only if it matches the bare basename.
      return patternToRegex(pattern).test(named);
    }
    if (pattern.endsWith('/**')) return pattern.slice(0, -3).split('/').pop() === named;
    return pattern === named;
  });
}

function walk(dir, options) {
  const { patterns, out, skillRoot, selfScan, allowHidden, allowed } = options;
  const walkRoot = options.walkRoot || dir;
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return; // unreadable directory: skip quietly rather than abort the run
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    // While walking, the skill root itself is a plain directory exclusion
    // (like `node_modules`): never descend into it without --self-scan. This
    // only ever matches the root as a discovered sub-directory — a file or
    // sub-directory named on the command line never passes through here —
    // so nothing the user named explicitly is dropped by this check.
    if (skillRoot && !selfScan && full === skillRoot) continue;

    if (entry.isDirectory()) {
      if (entry.name.startsWith('.') && !allowHidden) continue;
      if (isExcluded(entry.name, full, patterns, walkRoot)) continue;
      walk(full, { ...options, walkRoot });
      continue;
    }
    if (!entry.isFile()) continue; // symlinks are not followed while walking
    const ext = path.extname(entry.name).toLowerCase();
    if (!allowed.has(ext)) continue;
    if (isExcluded(entry.name, full, patterns, walkRoot)) continue;
    out.add(full);
  }
}

/**
 * @param {string[]} inputs   files or directories (resolved from cwd)
 * @param {object} options
 * @param {string|null} options.skillRoot   installed skill directory: skipped
 *                                          when named as input, never descended
 *                                          into while walking, unless --self-scan
 * @param {boolean} options.selfScan        scan the skill root itself
 * @param {string[]} options.excludes       extra patterns (config ignoredPaths)
 * @param {boolean} options.fixMode         an unsupported named file is left to
 *                                          the fixer's own `refusing --fix` error
 * @returns {string[]} absolute file paths, sorted
 */
export function collectFiles(inputs, {
  skillRoot = null, selfScan = false, excludes = [], fixMode = false, extensions = null,
} = {}) {
  // The configured extra extensions widen collection without touching the
  // extraction rules: a mapped suffix is collected exactly like a built-in one.
  const allowed = new Set([...EXTRACTABLE_EXTENSIONS, ...Object.keys(extensions || {})]);
  const patterns = [...DEFAULT_EXCLUDES, ...excludes];
  const out = new Set();
  // An input that *is* the skill root (the bare `.` or the package
  // directory) is the documented carve-out: it is skipped, and an empty
  // result the skip explains is not an empty-scan refusal — that is the
  // `node bin/check.mjs .` behaviour. No other input is dropped: a file or
  // sub-directory named inside the root is scanned, so an empty result from
  // it is a refusal like any other.
  const shield = { skippedBySkillRoot: false };

  for (const input of inputs) {
    const full = path.resolve(input);
    if (!fs.existsSync(full)) throw new ScannerError(`path not found: ${input}`);
    const stat = fs.statSync(full); // explicit inputs may be symlinks; --fix refuses them later
    if (stat.isFile()) {
      const ext = path.extname(full).toLowerCase();
      if (!allowed.has(ext) && !fixMode) {
        const supported = [...allowed].join(' ');
        throw new ScannerError(
          `unsupported file type: ${input} (supported extensions: ${supported})`);
      }
      out.add(full);
      continue;
    }
    if (!stat.isDirectory()) {
      throw new ScannerError(`not a regular file: ${input}`);
    }
    // The skill root named as a directory input: skip it and record why.
    if (skillRoot && !selfScan && full === skillRoot) {
      shield.skippedBySkillRoot = true;
      continue;
    }
    // A directory named on the command line overrides its own exclusion
    // (README: `fixtures` are skipped "unless you name them explicitly"):
    // only that directory's walk drops the patterns, everything inside it is
    // still filtered by the file-extension check alone.
    //
    // "Its own exclusion" means a match on the directory's *name*. Dropping the
    // pattern list for any directory that happened to be excluded was too
    // broad: a skill installed at `…/node_modules/un-editorial-check` is
    // excluded by `node_modules/**` through its ancestor, not by its own name,
    // so `--self-scan` inside an install used to run with no exclusions at all
    // and read the package's own `lib/fixtures/self-test` — the file holding
    // deliberate violations for `--self-test` to assert on. The installed
    // package then failed its own self-scan, which is the last thing a
    // self-scan is for, and CI caught it on every release from 1.0.0.
    const named = path.basename(full);
    const rootExcluded = excludedByOwnName(named, patterns);
    walk(full, {
      patterns: rootExcluded ? [] : patterns,
      out,
      skillRoot,
      selfScan,
      allowed,
      allowHidden: named.startsWith('.'),
    });
  }

  if (out.size === 0 && !shield.skippedBySkillRoot) {
    throw new ScannerError(`no supported files found: ${inputs.join(' ')}`);
  }

  // A symlinked file is never scanned: the target can change between the read
  // and any later write, and the v0.3.0 fix path already refused them.
  for (const file of out) {
    const stat = fs.lstatSync(file);
    if (stat.isSymbolicLink()) throw new ScannerError(`refusing symbolic link: ${file}`);
    if (!stat.isFile()) throw new ScannerError(`not a regular file: ${file}`);
  }
  return [...out].sort();
}
