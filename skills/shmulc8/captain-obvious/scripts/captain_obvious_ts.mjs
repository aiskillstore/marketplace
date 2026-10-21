#!/usr/bin/env node
/**
 * captain-obvious — TypeScript detector
 *
 * Deterministically finds tests (Jest/Vitest style) that can never fail or
 * check nothing, and optionally deletes them.
 */
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

import { findTestFiles } from './co_ts/discovery.mjs';
import { walk } from './co_ts/ast_utils.mjs';
import { isTestBlock, analyzeTest, toReportFinding } from './co_ts/analyzer.mjs';
import { loadCoverage } from './co_ts/coverage.mjs';
import { markDuplicates } from './co_ts/duplicates.mjs';
import { decideRemovals } from './co_ts/fixer.mjs';
import { fixBlocker } from './co_ts/gitguard.mjs';

// ---------------------------------------------------------------- args
const argv = process.argv.slice(2);
const argVal = (f) => { const i = argv.indexOf(f); return i >= 0 ? argv[i + 1] : undefined; };
const projectArg = argVal('--project') ?? '.';
const fileArg = argVal('--file');
const useStdin = argv.includes('--stdin');
const doFix = argv.includes('--fix');
const jsonOut = argVal('--json');
const coverageArg = argVal('--coverage');

const force = argv.includes('--force');
const doCheck = argv.includes('--check');
const baseArg = argVal('--base');

if (doCheck && doFix) {
  console.error('captain-obvious: --check is report-only — it cannot be combined with --fix');
  process.exit(2);
}
if (doCheck && !baseArg) {
  console.error('captain-obvious: --check requires --base <ref>');
  process.exit(2);
}
if (fileArg && doFix) {
  console.error('captain-obvious: --fix is not supported with --file (single-file mode is report-only)');
  process.exit(2);
}
if (useStdin && !fileArg) {
  console.error('captain-obvious: --stdin requires --file');
  process.exit(2);
}

const projectPath = path.resolve(fileArg ? path.dirname(path.resolve(fileArg)) : projectArg);
const isFile = !fileArg && fs.existsSync(projectPath) && fs.statSync(projectPath).isFile();
const projectDir = isFile ? path.dirname(projectPath) : projectPath;

if (doFix && !force) {
  const blocker = fixBlocker(projectDir);
  if (blocker) {
    console.error(
      `captain-obvious: refusing to --fix — ${blocker}.\n` +
      '  --fix rewrites test files in place with no backup. Commit or stash\n' +
      '  first so `git checkout -- <files>` can undo it, or pass --force.');
    process.exit(2);
  }
}

// ------------------------------------------------- load project's TypeScript
let ts;
try {
  const requireShim = createRequire(path.join(projectDir, 'package.json'));
  ts = requireShim('typescript');
  if (ts && !ts.sys) {
    try { ts = requireShim('typescript/lib/typescript.js'); } catch {}
  }
} catch {
  try {
    ts = (await import('typescript')).default;
    if (ts && !ts.sys) {
      try { ts = (await import('typescript/lib/typescript.js')).default; } catch {}
    }
  } catch {
    console.error(`captain-obvious: cannot resolve "typescript" from ${projectDir}. Install it there (npm i -D typescript).`);
    process.exit(2);
  }
}

if (!ts || !ts.sys) {
  console.error(`captain-obvious: cannot load valid "typescript" from ${projectDir} (missing ts.sys).`);
  process.exit(2);
}

const tsMajor = parseInt(String(ts.version ?? '0').split('.')[0], 10);
if (!Number.isFinite(tsMajor) || tsMajor < 4) {
  console.error(`captain-obvious: unsupported typescript version ${ts.version} loaded from ${projectDir} — need >= 4.0. Upgrade the project's typescript or run with a newer one installed.`);
  process.exit(2);
}

// ------------------------------------------------------------- single file
// Syntactic-only scan of one file, JSON to stdout. Built for write-time
// hooks: no Program, no TypeChecker, no tsconfig — a pure (tolerant) parse,
// so the type-guaranteed family can never fire and bad syntax never throws.
if (fileArg) {
  const filePath = path.resolve(fileArg);
  const content = useStdin ? fs.readFileSync(0, 'utf8') : fs.readFileSync(filePath, 'utf8');
  const kind = /\.tsx$/.test(filePath) ? ts.ScriptKind.TSX
    : /\.jsx$/.test(filePath) ? ts.ScriptKind.JSX
    : /\.(js|mjs|cjs)$/.test(filePath) ? ts.ScriptKind.JS
    : ts.ScriptKind.TS;
  const sf = ts.createSourceFile(filePath, content, ts.ScriptTarget.Latest, true, kind);
  const printer = ts.createPrinter({ removeComments: true });
  const findings = [];
  const records = [];
  walk(ts, sf, n => {
    const t = ts.isExpressionStatement(n) ? isTestBlock(ts, n) : null;
    if (t) analyzeTest(ts, null, false, false, false, sf, t, findings, records, projectDir);
  });
  markDuplicates(ts, printer, records, findings, projectDir);
  const sum = {};
  for (const f of findings) {
    sum[f.category] = sum[f.category] ?? { proven: 0, advisory: 0 };
    sum[f.category][f.level]++;
  }
  console.log(JSON.stringify({
    tool: 'captain-obvious/ts', file: filePath, mode: 'single-file',
    typeChecksEnabled: false, testsScanned: records.length,
    findings, summary: sum,
  }, null, 2));
  process.exit(0);
}

const testFiles = findTestFiles(projectDir);
if (testFiles.length === 0) {
  if (doCheck) {
    // nothing to scan → nothing newly introduced
    console.error(`captain-obvious: --check clean — no newly-introduced proven findings vs ${baseArg}`);
    process.exit(0);
  }
  console.error(`captain-obvious: no test files (*.test.ts / *.spec.ts / __tests__) under ${projectDir}`);
  process.exit(0);
}

// ---------------------------------------------------------------- program
const tsconfigPath = isFile ? projectPath
  : ts.findConfigFile(projectDir, ts.sys.fileExists, 'tsconfig.json');

let options = {};
let configFileNames = [];
if (tsconfigPath) {
  const raw = ts.readConfigFile(tsconfigPath, ts.sys.readFile);
  const parsed = ts.parseJsonConfigFileContent(raw.config ?? {}, ts.sys, path.dirname(tsconfigPath));
  options = parsed.options;
  configFileNames = parsed.fileNames;
}
const strictNull = options.strictNullChecks ?? options.strict ?? false;
const uncheckedIndex = options.noUncheckedIndexedAccess ?? false;
const typesAvailable = !!tsconfigPath;

const program = ts.createProgram(
  [...new Set([...configFileNames, ...testFiles.map(f => path.resolve(f))])],
  { ...options, noEmit: true, allowJs: true },
);
const checker = program.getTypeChecker();
const printer = ts.createPrinter({ removeComments: true });

const allFindings = [];
const testRecords = [];

// ------------------------------------------------------------ run analysis
for (const file of testFiles) {
  const sf = program.getSourceFile(path.resolve(file));
  if (!sf) continue;
  // never trust TS's inference on plain JS: without checkJs it is not a
  // checked guarantee, so type-guaranteed must stay off for JS files
  const isJs = /\.(js|jsx|mjs|cjs)$/.test(file);
  const fileTypes = typesAvailable && !isJs;
  walk(ts, sf, n => {
    const t = ts.isExpressionStatement(n) ? isTestBlock(ts, n) : null;
    if (t) analyzeTest(ts, checker, fileTypes, strictNull, uncheckedIndex, sf, t, allFindings, testRecords, projectDir);
  });
}

// duplicate-test pass
markDuplicates(ts, printer, testRecords, allFindings, projectDir);

// ------------------------------------------------------------ coverage confirm
const coverage = coverageArg ? loadCoverage(coverageArg, projectDir) : null;
let coveragePromoted = 0, coverageSuppressed = 0;
let coverageWarning = null;
if (coverage) {
  const kept = [];
  const inertFiles = new Set();
  for (const f of allFindings) {
    if (f.category === 'conditional-assert') {
      if (!coverage.hasFile(f.file)) inertFiles.add(f.file);
      const hits = coverage.hits(f.file, f.line);
      if (hits === 0) {
        f.level = 'proven';
        f.reason += " — coverage confirms it ran 0 times: rotten (ICSE'19). Fix the guard so it fires, or remove it";
        coveragePromoted++;
      } else if (hits > 0) {
        coverageSuppressed++;
        continue;
      }
    }
    kept.push(f);
  }
  allFindings.splice(0, allFindings.length, ...kept);
  if (inertFiles.size) {
    // coverage configs usually collect only src/ — then test-file lines are
    // absent and this whole mode silently confirms nothing
    coverageWarning = `coverage data has no lines for ${inertFiles.size} test file(s) ` +
      `(${[...inertFiles].sort().slice(0, 3).join(', ')}...) — coverage mode is inert for them; ` +
      'include test files in coverage collection (e.g. collectCoverageFrom over the whole repo, not just src/)';
  }
}

// ------------------------------------------------------------ decide removals & plan
const summary = {};
for (const f of allFindings) {
  summary[f.category] = summary[f.category] ?? { proven: 0, advisory: 0 };
  summary[f.category][f.level]++;
}

const report = {
  tool: 'captain-obvious/ts',
  project: projectDir,
  tsconfig: tsconfigPath ?? null,
  typeChecksEnabled: typesAvailable,
  strictNullChecks: strictNull,
  testFilesScanned: testFiles.length,
  testsScanned: testRecords.length,
  findings: allFindings,
  summary,
  coverage: coverage
    ? { file: coverageArg, conditionalAssertsPromoted: coveragePromoted, conditionalAssertsSuppressed: coverageSuppressed, warning: coverageWarning }
    : (coverageArg ? { file: coverageArg, error: 'could not parse coverage (expected lcov / istanbul json / coverage.py json)' } : null),
  plan: null,
  fixed: null,
};

decideRemovals(ts, testRecords, doFix, report, fs, projectDir);

// ------------------------------------------------------------ output
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(report, null, 2));

const pad = (s, n) => String(s).padEnd(n);
console.log(`\ncaptain-obvious (TS) — ${testRecords.length} tests scanned in ${testFiles.length} files`);
if (!typesAvailable) console.log('  (no tsconfig.json found — type-guaranteed checks disabled, syntactic checks only)');
else if (!strictNull) console.log('  (strictNullChecks is OFF — null/undefined-related checks disabled)');
console.log('');
for (const [cat, c] of Object.entries(summary)) {
  console.log(`  ${pad(cat, 20)} proven: ${c.proven}  advisory: ${c.advisory}`);
}
if (report.plan) {
  console.log(`\n  tests fully removable: ${report.plan.testsToRemove.length}`);
  console.log(`  individual assertions removable: ${report.plan.assertionsToRemove}`);
}
if (coverage) {
  console.log(`  coverage: ${coveragePromoted} conditional-assert(s) confirmed rotten, ${coverageSuppressed} confirmed reached (dropped)`);
  if (coverageWarning) console.log(`  coverage warning: ${coverageWarning}`);
} else if (coverageArg) {
  console.log('  coverage: could not parse the coverage file (expected lcov / istanbul json / coverage.py json)');
}
if (allFindings.length) {
  console.log('\nFindings:');
  for (const f of allFindings) {
    console.log(`  [${f.level === 'proven' ? 'PROVEN  ' : 'ADVISORY'}] ${f.file}:${f.line} (${f.category}) "${f.test}"`);
    console.log(`             ${f.reason}`);
  }
}
if (report.fixed) {
  console.log(`\nFixed: removed ${report.fixed.testsRemoved} tests and ${report.fixed.assertionsRemoved} assertions across ${report.fixed.filesChanged} files.`);
  console.log('Re-run your typechecker and test suite now.');
}

// ------------------------------------------------------------ --check CI gate
// Report-only (plan 011): exit 1 iff a proven syntactic finding is newly
// introduced vs --base in a changed file; every git failure other than
// 'file absent in base' fails OPEN (note + exit 0). Base-vs-current findings
// are keyed on (category, test) — the exact key hooks/prevent.py uses (line
// numbers shift across edits); shared BY CONVENTION, change both if it changes.
function checkGate(base, projectDir, findings) {
  const failOpen = (msg) => {
    console.error(`captain-obvious: --check could not compare against ${base} (${msg}) — treating as clean (fail-open)`);
    return 0;
  };
  const clean = () => {
    console.error(`captain-obvious: --check clean — no newly-introduced proven findings vs ${base}`);
    return 0;
  };
  const top = spawnSync('git', ['rev-parse', '--show-toplevel'], { cwd: projectDir, encoding: 'utf8' });
  if (top.status !== 0) return failOpen(String(top.stderr).trim().split('\n')[0] || 'not a git repository');
  const repo = fs.realpathSync(top.stdout.trim());

  // invalid ref → fail open; a valid ref with a file merely absent means NEW
  if (spawnSync('git', ['cat-file', '-e', base], { cwd: repo }).status !== 0)
    return failOpen(`no such ref ${base}`);

  const diff = spawnSync('git', ['diff', '--name-only', `${base}...HEAD`], { cwd: repo, encoding: 'utf8' });
  if (diff.status !== 0) return failOpen(String(diff.stderr).trim().split('\n')[0] || 'git diff failed');
  // realpath both sides to match abs(f): a symlinked directory component below
  // repo would otherwise diverge and silently empty the intersection. Fall back
  // to the plain resolved path on ENOENT (a deleted file's realpath throws).
  const changed = new Set(diff.stdout.split('\n').filter(Boolean).map(p => {
    const resolved = path.resolve(repo, p);
    try { return fs.realpathSync(resolved); } catch { return resolved; }
  }));

  const abs = (f) => fs.realpathSync(path.resolve(projectDir, f.file));  // findings exist on disk
  const key = (f) => `${f.category} ${f.test}`;

  // syntactic proven only: the base scan is single-file (no tsc, no coverage),
  // so categories whose proven status depends on either — type-guaranteed (tsc)
  // and coverage-promoted conditional-assert — can never appear proven on the
  // base side and would over-fire the gate
  const candidates = findings.filter(f =>
    f.level === 'proven' &&
    f.category !== 'type-guaranteed' && f.category !== 'conditional-assert' &&
    changed.has(abs(f)));
  if (candidates.length === 0) return clean();

  const seenByFile = new Map();
  for (const absfile of new Set(candidates.map(abs))) {
    const rel = path.relative(repo, absfile).split(path.sep).join('/');
    const show = spawnSync('git', ['show', `${base}:${rel}`], { cwd: repo, maxBuffer: 1 << 28 });
    if (show.status !== 0) { seenByFile.set(absfile, new Set()); continue; }  // absent in base → NEW
    const scan = spawnSync(process.execPath, [process.argv[1], '--file', absfile, '--stdin'],
      { input: show.stdout, encoding: 'utf8', maxBuffer: 1 << 28 });
    let baseFindings;
    try { baseFindings = JSON.parse(scan.stdout).findings; }
    catch { return failOpen(`base scan of ${rel} failed`); }
    if (!Array.isArray(baseFindings)) return failOpen(`base scan of ${rel} produced no findings array`);
    seenByFile.set(absfile, new Set(baseFindings.filter(f => f.level === 'proven').map(key)));
  }

  const fresh = candidates.filter(f => !seenByFile.get(abs(f)).has(key(f)));
  if (fresh.length === 0) return clean();
  for (const f of fresh)
    console.error(`captain-obvious: NEW proven finding: ${f.file}:${f.line} (${f.category}) "${f.test}" — ${f.reason}`);
  return 1;
}

if (doCheck) {
  let code;
  try {
    code = checkGate(baseArg, projectDir, allFindings);
  } catch (e) {
    // any unexpected throw (e.g. realpathSync ENOENT) fails OPEN — a gate must
    // never invent a CI failure
    console.error(`captain-obvious: --check could not compare against ${baseArg} (${(e && e.message) || e}) — treating as clean (fail-open)`);
    code = 0;
  }
  process.exit(code);
}
