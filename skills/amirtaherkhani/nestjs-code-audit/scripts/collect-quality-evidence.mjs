#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import {
  existsSync,
  lstatSync,
  readFileSync,
  readdirSync,
  realpathSync,
  statSync,
} from 'node:fs';
import { basename, dirname, isAbsolute, join, relative, resolve, sep } from 'node:path';
import process from 'node:process';

const DEFAULT_TIMEOUT_MS = 120_000;
const MAX_SOURCE_FILES = 5_000;
const MAX_FILE_BYTES = 1_000_000;
const MAX_OUTPUT_CHARS = 200_000;
const SOURCE_EXTENSIONS = new Set(['.ts', '.tsx', '.mts', '.cts']);
const IGNORED_DIRECTORIES = new Set([
  '.git',
  '.next',
  '.nuxt',
  '.output',
  'build',
  'coverage',
  'dist',
  'node_modules',
  'out',
  'tmp',
]);

const REVIEW_SIGNALS = [
  {
    id: 'forward-ref',
    owner: 'architecture',
    pattern: /\bforwardRef\s*\(/,
    review: 'Verify whether this is a temporary compatibility measure or evidence of unclear module/provider ownership.',
  },
  {
    id: 'module-ref-lookup',
    owner: 'oop-design',
    pattern: /\b(?:this\.)?moduleRef\s*\.\s*(?:get|resolve|create)\s*\(/i,
    review: 'Verify whether runtime lookup is required by a real plugin/lifecycle need or hides a constructor dependency.',
  },
  {
    id: 'global-module',
    owner: 'architecture',
    pattern: /@Global\s*\(/,
    review: 'Verify that global visibility is narrow, intentional, and does not hide feature dependencies.',
  },
  {
    id: 'request-scope',
    owner: 'runtime',
    pattern: /\bScope\.REQUEST\b/,
    review: 'Verify that request scope is required and that its transitive allocation/runtime cost is understood.',
  },
  {
    id: 'http-exception-import',
    owner: 'runtime',
    pattern: /import[\s\S]*\b(?:HttpException|BadRequestException|InternalServerErrorException)\b[\s\S]*from\s+['"]@nestjs\/common['"]/,
    review: 'Verify that transport-specific errors stay at HTTP/Nest boundaries rather than leaking into reusable application or domain policy.',
  },
  {
    id: 'fatal-process-handler',
    owner: 'runtime',
    pattern: /process\.(?:on|once)\s*\(\s*['"](?:uncaughtException|unhandledRejection)['"]/,
    review: 'Verify that the handler performs bounded diagnostics and exits instead of continuing in potentially inconsistent state.',
  },
  {
    id: 'typeorm-synchronize',
    owner: 'architecture',
    pattern: /\bsynchronize\s*:\s*true\b/,
    review: 'Verify that automatic schema synchronization cannot run in production and that reviewed migrations own schema change.',
  },
];

function fail(message) {
  process.stderr.write(`${message}\n`);
  process.exit(2);
}

function parseArguments(argv) {
  const options = {
    root: process.cwd(),
    scope: '.',
    run: false,
    timeoutMs: DEFAULT_TIMEOUT_MS,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--run') {
      options.run = true;
    } else if (argument === '--root' || argument === '--scope' || argument === '--timeout-ms') {
      const value = argv[index + 1];
      if (!value) fail(`Missing value for ${argument}.`);
      index += 1;
      if (argument === '--root') options.root = value;
      if (argument === '--scope') options.scope = value;
      if (argument === '--timeout-ms') {
        options.timeoutMs = Number(value);
        if (!Number.isInteger(options.timeoutMs) || options.timeoutMs < 1_000) {
          fail('--timeout-ms must be an integer of at least 1000.');
        }
      }
    } else if (argument === '--help' || argument === '-h') {
      process.stdout.write([
        'Usage: collect-quality-evidence.mjs [options]',
        '',
        'Options:',
        '  --root <path>        NestJS repository root (default: current directory)',
        '  --scope <path>       Relative file or directory scope (default: .)',
        '  --run                Run allow-listed local ESLint and TypeScript checks',
        '  --timeout-ms <ms>    Per-check timeout (default: 120000)',
        '  --help               Show this help',
        '',
      ].join('\n'));
      process.exit(0);
    } else {
      fail(`Unknown argument: ${argument}`);
    }
  }

  return options;
}

function insideRoot(root, candidate) {
  return candidate === root || candidate.startsWith(`${root}${sep}`);
}

function readJson(path, label) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    fail(`Cannot parse ${label} at ${path}: ${error.message}`);
  }
}

function packageManager(root, manifest) {
  const declared = typeof manifest.packageManager === 'string'
    ? manifest.packageManager.split('@')[0]
    : undefined;
  if (declared) return declared;
  if (existsSync(join(root, 'pnpm-lock.yaml'))) return 'pnpm';
  if (existsSync(join(root, 'yarn.lock'))) return 'yarn';
  if (existsSync(join(root, 'bun.lock')) || existsSync(join(root, 'bun.lockb'))) return 'bun';
  if (existsSync(join(root, 'package-lock.json'))) return 'npm';
  return 'unknown';
}

function sourceExtension(path) {
  const match = path.match(/(\.d)?\.(?:ts|tsx|mts|cts)$/);
  return match ? match[0].replace(/^\.d/, '') : '';
}

function collectSourceFiles(scopePath) {
  const files = [];
  let truncated = false;

  function visit(path) {
    if (files.length >= MAX_SOURCE_FILES) {
      truncated = true;
      return;
    }

    const entry = lstatSync(path);
    if (entry.isSymbolicLink()) return;
    if (entry.isDirectory()) {
      for (const name of readdirSync(path).sort()) {
        if (IGNORED_DIRECTORIES.has(name)) continue;
        visit(join(path, name));
        if (truncated) return;
      }
      return;
    }

    if (!entry.isFile()) return;
    const extension = sourceExtension(path);
    if (!SOURCE_EXTENSIONS.has(extension)) return;
    if (entry.size > MAX_FILE_BYTES) return;
    files.push(path);
  }

  visit(scopePath);
  return { files, truncated };
}

function reviewCandidates(root, files) {
  const candidates = [];
  for (const file of files) {
    const lines = readFileSync(file, 'utf8').split(/\r?\n/);
    for (let index = 0; index < lines.length; index += 1) {
      const line = lines[index];
      for (const signal of REVIEW_SIGNALS) {
        if (!signal.pattern.test(line)) continue;
        candidates.push({
          signal: signal.id,
          owner: signal.owner,
          file: relative(root, file) || basename(file),
          line: index + 1,
          review: signal.review,
        });
        if (candidates.length >= 500) return { candidates, truncated: true };
      }
    }
  }
  return { candidates, truncated: false };
}

function localBinary(root, name) {
  const suffix = process.platform === 'win32' ? '.cmd' : '';
  const path = join(root, 'node_modules', '.bin', `${name}${suffix}`);
  return existsSync(path) ? path : undefined;
}

function trimOutput(value) {
  if (!value) return '';
  const normalized = value.toString().replace(/\u001b\[[0-9;]*m/g, '').trim();
  if (normalized.length <= MAX_OUTPUT_CHARS) return normalized;
  return `${normalized.slice(0, MAX_OUTPUT_CHARS)}\n[output truncated]`;
}

function runCheck({ id, command, args, cwd, timeoutMs, scope }) {
  if (!command) {
    return {
      id,
      status: 'not-run',
      scope,
      reason: `Local ${id === 'lint' ? 'ESLint' : 'TypeScript'} executable is unavailable; dependencies were not installed by the audit.`,
    };
  }

  const result = spawnSync(command, args, {
    cwd,
    encoding: 'utf8',
    env: { ...process.env, CI: '1', FORCE_COLOR: '0', NO_COLOR: '1' },
    maxBuffer: MAX_OUTPUT_CHARS * 2,
    timeout: timeoutMs,
  });

  const displayCommand = [relative(cwd, command) || basename(command), ...args].join(' ');
  if (result.error?.code === 'ETIMEDOUT' || result.signal === 'SIGTERM') {
    return {
      id,
      status: 'not-run',
      scope,
      command: displayCommand,
      reason: `Timed out after ${timeoutMs} ms.`,
      stdout: trimOutput(result.stdout),
      stderr: trimOutput(result.stderr),
    };
  }

  if (result.error) {
    return {
      id,
      status: 'not-run',
      scope,
      command: displayCommand,
      reason: result.error.message,
      stdout: trimOutput(result.stdout),
      stderr: trimOutput(result.stderr),
    };
  }

  const stdout = trimOutput(result.stdout);
  const stderr = trimOutput(result.stderr);
  const safeTypecheckUnsupported = id === 'typescript'
    && /TS(?:6310|6379)|may not disable incremental compilation|Referenced project .* may not disable emit/i.test(`${stdout}\n${stderr}`);
  if (safeTypecheckUnsupported) {
    return {
      id,
      status: 'not-run',
      scope,
      command: displayCommand,
      reason: 'The repository uses project-reference/composite settings incompatible with the collector\'s read-only no-emit command.',
      stdout,
      stderr,
    };
  }

  return {
    id,
    status: result.status === 0 ? 'pass' : 'fail',
    scope,
    command: displayCommand,
    exitCode: result.status,
    stdout,
    stderr,
  };
}

function gitEvidence(root) {
  const branch = spawnSync('git', ['branch', '--show-current'], { cwd: root, encoding: 'utf8' });
  const revision = spawnSync('git', ['rev-parse', '--short', 'HEAD'], { cwd: root, encoding: 'utf8' });
  const status = spawnSync('git', ['status', '--short'], { cwd: root, encoding: 'utf8' });
  if (branch.status !== 0 || revision.status !== 0 || status.status !== 0) {
    return { available: false };
  }
  const changes = status.stdout.split(/\r?\n/).filter(Boolean);
  return {
    available: true,
    branch: branch.stdout.trim(),
    revision: revision.stdout.trim(),
    dirty: changes.length > 0,
    changedPaths: changes.slice(0, 200),
    changedPathsTruncated: changes.length > 200,
  };
}

const options = parseArguments(process.argv.slice(2));
const requestedRoot = resolve(options.root);
if (!existsSync(requestedRoot) || !statSync(requestedRoot).isDirectory()) {
  fail(`Repository root does not exist or is not a directory: ${requestedRoot}`);
}
const root = realpathSync(requestedRoot);
const manifestPath = join(root, 'package.json');
if (!existsSync(manifestPath)) fail(`No package.json found at repository root: ${root}`);
const manifest = readJson(manifestPath, 'package.json');

const unresolvedScope = isAbsolute(options.scope) ? resolve(options.scope) : resolve(root, options.scope);
if (!insideRoot(root, unresolvedScope)) fail(`Scope escapes repository root: ${options.scope}`);
if (!existsSync(unresolvedScope)) fail(`Scope does not exist: ${options.scope}`);
const scopePath = realpathSync(unresolvedScope);
if (!insideRoot(root, scopePath)) fail(`Scope resolves outside repository root: ${options.scope}`);
const scope = relative(root, scopePath) || '.';

const dependencies = {
  ...(manifest.dependencies ?? {}),
  ...(manifest.devDependencies ?? {}),
  ...(manifest.peerDependencies ?? {}),
};
const source = collectSourceFiles(scopePath);
const signals = reviewCandidates(root, source.files);
const manager = packageManager(root, manifest);
const scriptNames = Object.keys(manifest.scripts ?? {}).sort();

const checks = [];
if (options.run) {
  const eslint = localBinary(root, 'eslint');
  checks.push(runCheck({
    id: 'lint',
    command: eslint,
    args: [scope, '--no-fix', '--no-cache'],
    cwd: root,
    timeoutMs: options.timeoutMs,
    scope,
  }));

  const tsc = localBinary(root, 'tsc');
  checks.push(runCheck({
    id: 'typescript',
    command: tsc,
    args: ['--noEmit', '--pretty', 'false', '--incremental', 'false'],
    cwd: root,
    timeoutMs: options.timeoutMs,
    scope: '.',
  }));
} else {
  checks.push(
    { id: 'lint', status: 'not-run', scope, reason: 'Collector was invoked without --run.' },
    { id: 'typescript', status: 'not-run', scope: '.', reason: 'Collector was invoked without --run.' },
  );
}

const output = {
  schemaVersion: 1,
  generatedAt: new Date().toISOString(),
  readOnlyContract: true,
  root,
  scope,
  project: {
    name: manifest.name ?? null,
    packageManager: manager,
    nestjs: Boolean(dependencies['@nestjs/core']),
    nestVersion: dependencies['@nestjs/core'] ?? null,
    typescriptVersion: dependencies.typescript ?? null,
    scripts: scriptNames,
  },
  git: gitEvidence(root),
  inventory: {
    sourceFiles: source.files.length,
    sourceFilesTruncated: source.truncated,
  },
  checks,
  reviewCandidates: signals.candidates,
  reviewCandidatesTruncated: signals.truncated,
  notes: [
    'Review candidates are heuristic signals, not confirmed findings.',
    'The collector does not install dependencies, execute package scripts, run tests/builds, or modify source files.',
    scope === '.'
      ? 'TypeScript and lint scopes cover the repository root.'
      : 'TypeScript checks the repository configuration as a whole; lint and source review use the requested scope.',
  ],
};

process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
