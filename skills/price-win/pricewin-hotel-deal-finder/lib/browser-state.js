// ----------------------------------------------------------------------------
// browser-state.js
//
// Persists the running Chromium's CDP endpoint to a state file so that
// subsequent CLI invocations can re-attach to the same browser. Without this
// every CLI call would spawn a fresh browser and lose its tab + cookies.
//
// State layout (~/.cache/pricewin-hotel-deal-finder/session-<id>.json):
//   {
//     "port": 51234,
//     "pid": 12345,
//     "token": "<64-hex auth token for the daemon's localhost API>",
//     "createdAt": "2026-05-18T10:00:00Z"
//   }
//
// The file carries the daemon's auth token, so it is created 0600 inside a 0700
// directory: on a shared machine another local user must not be able to read it
// and drive the browser.
// ----------------------------------------------------------------------------

import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { existsSync, mkdirSync, chmodSync } from 'node:fs';

const STATE_DIR = path.join(os.homedir(), '.cache', 'pricewin-hotel-deal-finder');
const DEFAULT_SESSION = 'default';

function ensureDir() {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true, mode: 0o700 });
  // Tighten a directory an older version created 0755.
  else chmodSync(STATE_DIR, 0o700);
}

function statePath(sessionId = DEFAULT_SESSION) {
  return path.join(STATE_DIR, `session-${sessionId}.json`);
}

export async function saveState(state, sessionId = DEFAULT_SESSION) {
  ensureDir();
  const file = statePath(sessionId);
  await fs.writeFile(file, JSON.stringify(state, null, 2), { mode: 0o600 });
  // writeFile's `mode` only applies when it creates the file — chmod covers the
  // case where a previous run left a world-readable state file behind.
  await fs.chmod(file, 0o600).catch(() => {});
}

export async function loadState(sessionId = DEFAULT_SESSION) {
  try {
    const raw = await fs.readFile(statePath(sessionId), 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    if (err.code === 'ENOENT') return null;
    throw err;
  }
}

export async function clearState(sessionId = DEFAULT_SESSION) {
  await fs.unlink(statePath(sessionId)).catch(() => {});
}

export function isProcessAlive(pid) {
  if (!pid) return false;
  try {
    // Signal 0 = test without actually signalling. Throws if process gone.
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}
