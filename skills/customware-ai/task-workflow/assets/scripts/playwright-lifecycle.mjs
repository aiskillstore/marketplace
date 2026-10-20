#!/usr/bin/env node
import { spawn, spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { createWriteStream, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';

function printUsage() {
	console.log(`Usage:
  node task-workflow/scripts/playwright-lifecycle.mjs \\
    --server "PORT=4444 node build/server/start.js" \\
    --ready-url "http://127.0.0.1:4444/health" \\
    --run "node task-workflow/playwright/verify-flow.mjs"

Common options:
  --setup "command"              Run bounded setup before server startup; repeatable.
  --run "command"                Run bounded verification command after readiness; repeatable.
  --env NAME=value               Add an environment variable; repeatable. Database path variables are rejected.
  --ready-text "text"            Require response body text during readiness polling.
  --ready-timeout-ms 30000       Startup readiness timeout.
  --command-timeout-ms 300000    Per-run command timeout.
  --force-restart                Ignore an already healthy ready URL and start this run's server.
  --keep-server                  Leave this run's captured server process running.

Use this helper for custom Playwright scripts, browser probes, and repo E2E
commands. Put "pnpm exec playwright test ..." inside --run by default. Use repo
Playwright webServer ownership only when this helper cannot own the server for
that exact command and the artifact records the reason before running it.`);
}

function parseArgs(argv) {
	const args = {
		runs: [],
		setups: [],
		env: [],
		cwd: process.cwd(),
		runtimeDir: 'task-workflow/runtime',
		setupTimeoutMs: 120000,
		readyTimeoutMs: 120000,
		commandTimeoutMs: 300000,
		keepServer: false,
		forceRestart: false
	};

	for (let index = 0; index < argv.length; index += 1) {
		const arg = argv[index];
		const next = () => {
			index += 1;
			if (index >= argv.length) {
				throw new Error(`${arg} requires a value`);
			}
			return argv[index];
		};

		if (arg === '--cwd') {
			args.cwd = next();
		} else if (arg === '--server') {
			args.server = next();
		} else if (arg === '--ready-url') {
			args.readyUrl = next();
		} else if (arg === '--ready-text') {
			args.readyText = next();
		} else if (arg === '--run') {
			args.runs.push(next());
		} else if (arg === '--setup') {
			args.setups.push(next());
		} else if (arg === '--env') {
			args.env.push(next());
		} else if (arg === '--runtime-dir') {
			args.runtimeDir = next();
		} else if (arg === '--setup-timeout-ms') {
			args.setupTimeoutMs = Number(next());
		} else if (arg === '--ready-timeout-ms') {
			args.readyTimeoutMs = Number(next());
		} else if (arg === '--command-timeout-ms') {
			args.commandTimeoutMs = Number(next());
		} else if (arg === '--keep-server') {
			args.keepServer = true;
		} else if (arg === '--force-restart') {
			args.forceRestart = true;
		} else if (arg === '--help' || arg === '-h') {
			args.help = true;
		} else {
			throw new Error(`Unknown argument: ${arg}`);
		}
	}

	return args;
}

// E2E/end-to-end database paths are owned by the target repo's checked-in test config.
// Agents must never override them here, and must never point test runs at the
// live workspace/production database `.dbs/database.db`.
const BLOCKED_DATABASE_ENV_KEYS = new Set([
	'DATABASE_PATH',
	'DATABASE_FILE_PATH',
	'DATABASE_FILENAME',
	'E2E_DATABASE_FILE_PATH',
	'PLAYWRIGHT_DATABASE_FILE_PATH',
	'TEST_DATABASE_PATH',
	'TEST_DATABASE_FILE_PATH',
	'SQLITE_DATABASE_PATH',
	'SQLITE_DB_PATH',
	'DB_PATH',
	'DB_FILE',
	'DB_FILENAME'
]);

function isDatabasePathOverrideKey(key) {
	const normalized = key.toUpperCase();
	const looksLikeDatabaseFilePathKey =
		/(DATABASE|SQLITE|DB)/.test(normalized) && /(PATH|FILE|FILENAME)/.test(normalized);

	return BLOCKED_DATABASE_ENV_KEYS.has(normalized) || looksLikeDatabaseFilePathKey;
}

function isWorkspaceDatabasePath(value) {
	const normalized = value.replaceAll('\\', '/');
	return normalized === '.dbs/database.db' || normalized.endsWith('/.dbs/database.db');
}

function assertAllowedEnvOverride(key, value) {
	if (isDatabasePathOverrideKey(key) || (/(DATABASE|DB|SQLITE)/i.test(key) && isWorkspaceDatabasePath(value))) {
		throw new Error(
			`Refusing --env ${key}=... Database file paths are owned by the repo/test config and must not be changed through playwright-lifecycle. Never point verification at .dbs/database.db; that is the live workspace database.`
		);
	}
}

function buildEnv(args) {
	const env = { ...process.env };

	if (!env.PLAYWRIGHT_BROWSERS_PATH && existsSync('/ms-playwright')) {
		env.PLAYWRIGHT_BROWSERS_PATH = '/ms-playwright';
	}

	if (args.readyUrl && !env.TARGET_URL) {
		const url = new URL(args.readyUrl);
		env.TARGET_URL = `${url.protocol}//${url.host}`;
	}

	for (const entry of args.env) {
		const separatorIndex = entry.indexOf('=');
		if (separatorIndex <= 0) {
			throw new Error(`Invalid --env value: ${entry}`);
		}

		const key = entry.slice(0, separatorIndex);
		const value = entry.slice(separatorIndex + 1);
		assertAllowedEnvOverride(key, value);
		env[key] = value;
	}

	return env;
}

function browserDirectoryName(name, revision) {
	return name === 'chromium-headless-shell' ? `chromium_headless_shell-${revision}` : `${name}-${revision}`;
}

function findBrowsersJson(cwd) {
	const require = createRequire(resolve(cwd, 'package.json'));
	for (const packageName of ['playwright-core/package.json', 'playwright/package.json', '@playwright/test/package.json']) {
		try {
			const packagePath = require.resolve(packageName);
			const candidate = packageName.startsWith('playwright-core/') ? join(dirname(packagePath), 'browsers.json') : null;
			if (candidate && existsSync(candidate)) {
				return candidate;
			}
		} catch {
			// Fall through to the pnpm workspace search below.
		}
	}

	const nodeModulesPath = join(cwd, 'node_modules');
	const found = spawnSync(
		'bash',
		[
			'-lc',
			`find ${JSON.stringify(nodeModulesPath)} -name browsers.json -print 2>/dev/null | grep '/playwright-core/browsers.json$' | head -1`
		],
		{ encoding: 'utf8' }
	);
	const path = found.stdout.trim();
	return path && existsSync(path) ? path : null;
}

function preflightPlaywrightBrowsers(cwd, env, commands) {
	if (!commands.some((command) => /\bplaywright\b/.test(command))) {
		return;
	}

	if (!env.PLAYWRIGHT_BROWSERS_PATH) {
		return;
	}

	const browsersJsonPath = findBrowsersJson(cwd);
	if (!browsersJsonPath) {
		console.log('[lifecycle] Playwright browsers.json not found; skipping browser preflight');
		return;
	}

	const data = JSON.parse(readFileSync(browsersJsonPath, 'utf8'));
	const required = data.browsers.filter(
		(browser) => browser.name === 'chromium' || browser.name === 'chromium-headless-shell'
	);
	const missing = [];
	for (const browser of required) {
		const dir = join(env.PLAYWRIGHT_BROWSERS_PATH, browserDirectoryName(browser.name, browser.revision));
		if (!existsSync(dir)) {
			missing.push(dir);
		}
	}

	if (missing.length > 0) {
		throw new Error(
			[
				`Playwright browser preflight failed for PLAYWRIGHT_BROWSERS_PATH=${env.PLAYWRIGHT_BROWSERS_PATH}.`,
				`Expected browser directories from ${browsersJsonPath}:`,
				...missing.map((item) => `- ${item}`),
				'Do not run playwright install in this workflow. Use the project-pinned Playwright version that matches the sandbox image, or update the image/browser cache intentionally.'
			].join('\n')
		);
	}

	console.log(`[lifecycle] Playwright browser preflight passed at ${env.PLAYWRIGHT_BROWSERS_PATH}`);
}

async function probeReady(url, readyText) {
	const controller = new AbortController();
	const timer = setTimeout(() => controller.abort(), 2500);
	try {
		const response = await fetch(url, { signal: controller.signal });
		if (!response.ok) {
			return false;
		}
		if (!readyText) {
			return true;
		}
		const text = await response.text();
		return text.includes(readyText);
	} catch {
		return false;
	} finally {
		clearTimeout(timer);
	}
}

function killProcessGroup(pid, signal) {
	try {
		process.kill(-pid, signal);
		return true;
	} catch {
		try {
			process.kill(pid, signal);
			return true;
		} catch {
			return false;
		}
	}
}

function spawnLogged(command, options) {
	mkdirSync(dirname(options.logPath), { recursive: true });
	const log = createWriteStream(options.logPath, { flags: 'w' });
	const child = spawn('bash', ['-lc', command], {
		cwd: options.cwd,
		env: options.env,
		detached: true,
		stdio: ['ignore', 'pipe', 'pipe']
	});
	child.stdout.pipe(log, { end: false });
	child.stderr.pipe(log, { end: false });
	child.stdout.pipe(process.stdout, { end: false });
	child.stderr.pipe(process.stderr, { end: false });
	child.once('close', () => log.end());
	return child;
}

async function runCommand(command, options) {
	const child = spawnLogged(command, options);
	let timedOut = false;
	const timeout = setTimeout(() => {
		timedOut = true;
		killProcessGroup(child.pid, 'SIGTERM');
		setTimeout(() => killProcessGroup(child.pid, 'SIGKILL'), 2000).unref();
	}, options.timeoutMs);

	const exitCode = await new Promise((resolve) => {
		child.once('close', (code, signal) => resolve(code ?? (signal ? 128 : 1)));
	});
	clearTimeout(timeout);

	if (timedOut) {
		throw new Error(`Command timed out after ${options.timeoutMs}ms; output preserved at ${options.logPath}`);
	}
	if (exitCode !== 0) {
		throw new Error(`Command failed with exit ${exitCode}; output preserved at ${options.logPath}`);
	}
}

async function startServer(args, env, runtimeDir) {
	if (!args.server) {
		return null;
	}

	if (!args.readyUrl) {
		throw new Error('--ready-url is required with --server');
	}

	if (!args.forceRestart && (await probeReady(args.readyUrl, args.readyText))) {
		console.log(`[lifecycle] Reusing healthy server at ${args.readyUrl}`);
		return null;
	}

	const logPath = resolve(runtimeDir, 'server.log');
	const pidPath = resolve(runtimeDir, 'server.pid');
	const child = spawnLogged(args.server, { cwd: args.cwd, env, logPath });
	writeFileSync(pidPath, `${child.pid}\n`);

	const deadline = Date.now() + args.readyTimeoutMs;
	while (Date.now() < deadline) {
		if (await probeReady(args.readyUrl, args.readyText)) {
			console.log(`[lifecycle] Server ready at ${args.readyUrl}; pid=${child.pid}; log=${logPath}`);
			return child.pid;
		}

		if (child.exitCode !== null) {
			throw new Error(`Server exited before readiness; log preserved at ${logPath}`);
		}

		await delay(250);
	}

	killProcessGroup(child.pid, 'SIGTERM');
	throw new Error(`Server was not ready within ${args.readyTimeoutMs}ms; log preserved at ${logPath}`);
}

const args = parseArgs(process.argv.slice(2));
if (args.help) {
	printUsage();
	process.exit(0);
}
const cwd = resolve(args.cwd);
const runtimeDir = resolve(cwd, args.runtimeDir);
mkdirSync(runtimeDir, { recursive: true });
const env = buildEnv(args);

preflightPlaywrightBrowsers(cwd, env, args.runs);

let startedPid = null;
try {
	let setupIndex = 0;
	for (const command of args.setups) {
		setupIndex += 1;
		const logPath = resolve(runtimeDir, `setup-${String(setupIndex).padStart(2, '0')}.log`);
		console.log(`[lifecycle] Running setup ${setupIndex}: ${command}`);
		await runCommand(command, { cwd, env, logPath, timeoutMs: args.setupTimeoutMs });
	}
	startedPid = await startServer({ ...args, cwd }, env, runtimeDir);
	let index = 0;
	for (const command of args.runs) {
		index += 1;
		const logPath = resolve(runtimeDir, `run-${String(index).padStart(2, '0')}.log`);
		console.log(`[lifecycle] Running command ${index}: ${command}`);
		await runCommand(command, { cwd, env, logPath, timeoutMs: args.commandTimeoutMs });
	}
	console.log('[lifecycle] Completed successfully');
} finally {
	if (startedPid && !args.keepServer) {
		killProcessGroup(startedPid, 'SIGTERM');
		await delay(500);
		killProcessGroup(startedPid, 'SIGKILL');
		console.log(`[lifecycle] Stopped server pid=${startedPid}`);
	}
}
