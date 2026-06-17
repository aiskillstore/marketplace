#!/usr/bin/env node
/**
 * Check if a newer version of the AgentCall skill is available on GitHub.
 *
 * Optional. Not required for normal skill operation. Primarily useful for users
 * who installed the skill directly from GitHub (marketplace users get updates
 * via /plugin update).
 *
 * Reads current version from ../../.claude-plugin/plugin.json, fetches the
 * latest version from GitHub's main branch, compares, and prints JSON to stdout.
 * Caches results for 7 days at ~/.agentcall/update-check.json.
 *
 * Always exits 0 (never breaks the caller).
 */

import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { dirname, join, resolve } from 'path';
import { homedir } from 'os';
import { fileURLToPath } from 'url';
import https from 'https';

const __dirname = dirname(fileURLToPath(import.meta.url));

const REPO_URL = 'https://github.com/pattern-ai-labs/agentcall';
const GITHUB_PLUGIN_URL = 'https://raw.githubusercontent.com/pattern-ai-labs/agentcall/main/.claude-plugin/plugin.json';
const CACHE_TTL_DAYS = 7;
const CACHE_VERSION = 1;
const FETCH_TIMEOUT_MS = 5000;

const UPDATE_COMMANDS = {
  marketplace: '/plugin marketplace update pattern-ai-labs-agentcall && /plugin update join-meeting',
  git: 'git pull',
  zip: `Download the latest release from ${REPO_URL}`,
};

function pluginJsonPath() {
  // scripts/node/ -> skill root -> .claude-plugin/plugin.json
  return resolve(__dirname, '..', '..', '.claude-plugin', 'plugin.json');
}

function cachePath() {
  return join(homedir(), '.agentcall', 'update-check.json');
}

function readCurrentVersion() {
  try {
    const raw = readFileSync(pluginJsonPath(), 'utf8');
    const data = JSON.parse(raw);
    return String(data.version || 'unknown');
  } catch {
    return 'unknown';
  }
}

function parseVersion(v) {
  try {
    const parts = v.split('.').slice(0, 3).map((p) => parseInt(p, 10));
    if (parts.some((n) => Number.isNaN(n))) return null;
    return parts;
  } catch {
    return null;
  }
}

function compareVersions(current, latest) {
  const c = parseVersion(current);
  const l = parseVersion(latest);
  if (!c || !l) return false;
  for (let i = 0; i < Math.max(c.length, l.length); i++) {
    const a = c[i] || 0;
    const b = l[i] || 0;
    if (b > a) return true;
    if (b < a) return false;
  }
  return false;
}

function loadCache() {
  try {
    const raw = readFileSync(cachePath(), 'utf8');
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

function saveCache(data) {
  try {
    mkdirSync(dirname(cachePath()), { recursive: true });
    writeFileSync(cachePath(), JSON.stringify(data));
  } catch {
    // ignore
  }
}

function cacheIsFresh(cache) {
  if (!cache.last_checked) return false;
  try {
    const last = new Date(cache.last_checked).getTime();
    const now = Date.now();
    return now - last < CACHE_TTL_DAYS * 24 * 60 * 60 * 1000;
  } catch {
    return false;
  }
}

function fetchLatestVersion() {
  return new Promise((resolvePromise, reject) => {
    const req = https.get(
      GITHUB_PLUGIN_URL,
      {
        headers: {
          Accept: 'application/json',
          'User-Agent': 'agentcall-skill-update-check',
        },
        timeout: FETCH_TIMEOUT_MS,
      },
      (res) => {
        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode}`));
          res.resume();
          return;
        }
        let body = '';
        res.setEncoding('utf8');
        res.on('data', (chunk) => (body += chunk));
        res.on('end', () => {
          try {
            const data = JSON.parse(body);
            resolvePromise(String(data.version || 'unknown'));
          } catch (e) {
            reject(e);
          }
        });
      }
    );
    req.on('timeout', () => {
      req.destroy(new Error('timeout'));
    });
    req.on('error', reject);
  });
}

function buildResult(current, latest) {
  return {
    current_version: current,
    latest_version: latest,
    update_available: compareVersions(current, latest),
    repo_url: REPO_URL,
    update_commands: UPDATE_COMMANDS,
    last_checked: new Date().toISOString(),
    cached: false,
  };
}

async function main() {
  const current = readCurrentVersion();
  const cache = loadCache();

  if (cacheIsFresh(cache)) {
    const result = cache.cached_result;
    if (result) {
      result.cached = true;
      console.log(JSON.stringify(result));
      return 0;
    }
  }

  try {
    const latest = await fetchLatestVersion();
    const result = buildResult(current, latest);
    saveCache({
      cache_version: CACHE_VERSION,
      last_checked: result.last_checked,
      latest_version: latest,
      cached_result: result,
    });
    console.log(JSON.stringify(result));
    return 0;
  } catch (e) {
    const stale = cache.cached_result;
    if (stale) {
      stale.stale = true;
      stale.cached = true;
      console.log(JSON.stringify(stale));
      return 0;
    }
    console.log(
      JSON.stringify({
        current_version: current,
        latest_version: 'unknown',
        update_available: false,
        repo_url: REPO_URL,
        error: 'network_failure',
        error_detail: String(e && e.message ? e.message : e),
      })
    );
    return 0;
  }
}

main().then((code) => process.exit(code));
