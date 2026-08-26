import { execFileSync } from 'node:child_process';
import { cp, lstat, mkdir } from 'node:fs/promises';
import { homedir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const PROFILE_ACCOUNT = 'profile';
export const DEFAULT_SECRET_SERVICE = 'com.vaibhavarora.job-application-agent';
export const LEGACY_SECRET_SERVICE = 'com.openai.codex.job-application-agent';
export const LINUX_PROFILE_ERROR = 'Secure profile storage requires macOS or Windows.';
export const WINDOWS_PROFILE_SCRIPT = fileURLToPath(new URL('./windows-profile-store.ps1', import.meta.url));

export function resolveSecretService(env = process.env) {
  return env.JOB_APPLICATION_AGENT_KEYCHAIN_SERVICE || DEFAULT_SECRET_SERVICE;
}

export function resolveStateDir({
  env = process.env,
  home = homedir(),
  plat = process.platform,
} = {}) {
  if (env.JOB_APPLICATION_AGENT_STATE_DIR) return env.JOB_APPLICATION_AGENT_STATE_DIR;
  if (plat === 'win32') {
    const appData = env.APPDATA || join(home, 'AppData', 'Roaming');
    return join(appData, 'job-application-agent');
  }
  if (plat === 'darwin') return join(home, 'Library', 'Application Support', 'job-application-agent');
  return join(home, '.local', 'share', 'job-application-agent');
}

export function legacyMacStateDir(home = homedir()) {
  return join(home, 'Library', 'Application Support', 'Codex', 'job-application-agent');
}

async function exists(filePath) {
  try { await lstat(filePath); return true; } catch (error) { if (error.code === 'ENOENT') return false; throw error; }
}

export async function migrateLegacyStateDir(dir, {
  env = process.env,
  home = homedir(),
  plat = process.platform,
} = {}) {
  if (env.JOB_APPLICATION_AGENT_STATE_DIR) return false;
  if (plat !== 'darwin') return false;
  const legacy = legacyMacStateDir(home);
  if (resolve(dir) === resolve(legacy)) return false;
  if (!(await exists(legacy))) return false;
  if (await exists(dir)) return false;
  await mkdir(resolve(dir, '..'), { recursive: true });
  await cp(legacy, dir, { recursive: true });
  return true;
}

function decodeSecret(value) {
  const trimmed = String(value ?? '').trim();
  return /^[0-9a-f]+$/i.test(trimmed) && trimmed.length % 2 === 0 ? Buffer.from(trimmed, 'hex').toString('utf8') : trimmed;
}

function darwinFind(exec, service, account) {
  try {
    return exec('security', ['find-generic-password', '-s', service, '-a', account, '-w'], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  } catch {
    return null;
  }
}

function darwinWrite(exec, service, account, raw) {
  try {
    exec('security', ['add-generic-password', '-a', account, '-s', service, '-U', '-w', raw], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  } catch {
    throw new Error('Keychain could not store the profile. Unlock macOS Keychain and retry; no profile data was logged.');
  }
}

function createDarwinStore({ execFileSync: exec, service, legacyService, account }) {
  return {
    readProfile() {
      const current = darwinFind(exec, service, account);
      if (current != null) return decodeSecret(current);
      if (legacyService && legacyService !== service) {
        const legacy = darwinFind(exec, legacyService, account);
        if (legacy != null) {
          const raw = decodeSecret(legacy);
          darwinWrite(exec, service, account, raw);
          return raw;
        }
      }
      throw new Error('The stored profile is missing or unreadable. Run profile set again.');
    },
    writeProfile(raw) {
      darwinWrite(exec, service, account, raw);
    },
  };
}

function windowsRequest(exec, scriptPath, payload, plaintext = '') {
  const input = `${JSON.stringify(payload)}\n${plaintext}`;
  try {
    return exec('powershell.exe', [
      '-NoProfile',
      '-NonInteractive',
      '-ExecutionPolicy', 'Bypass',
      '-File',
      scriptPath,
    ], {
      input,
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true,
      maxBuffer: 20 * 1024 * 1024,
    });
  } catch {
    throw new Error('Windows profile storage failed. Unlock Windows Credential Manager and retry; no profile data was logged.');
  }
}

function createWin32Store({
  execFileSync: exec,
  service,
  account,
  stateDir,
  scriptPath = WINDOWS_PROFILE_SCRIPT,
}) {
  const profilePath = () => join(typeof stateDir === 'function' ? stateDir() : stateDir, 'profile.dat');
  return {
    readProfile() {
      const raw = windowsRequest(exec, scriptPath, { op: 'get', service, account, path: profilePath() });
      const text = String(raw ?? '').replace(/^\uFEFF/, '');
      if (!text.trim()) throw new Error('The stored profile is missing or unreadable. Run profile set again.');
      return text;
    },
    writeProfile(raw) {
      windowsRequest(exec, scriptPath, { op: 'set', service, account, path: profilePath() }, raw);
    },
  };
}

function unsupportedStore() {
  return {
    readProfile() { throw new Error(LINUX_PROFILE_ERROR); },
    writeProfile() { throw new Error(LINUX_PROFILE_ERROR); },
  };
}

export function createSecretStore({
  platform = process.platform,
  env = process.env,
  execFileSync: exec = execFileSync,
  service = resolveSecretService(env),
  legacyService = LEGACY_SECRET_SERVICE,
  account = PROFILE_ACCOUNT,
  stateDir = () => resolveStateDir({ env, plat: platform }),
  scriptPath = WINDOWS_PROFILE_SCRIPT,
} = {}) {
  if (platform === 'darwin') return createDarwinStore({ execFileSync: exec, service, legacyService, account });
  if (platform === 'win32') return createWin32Store({ execFileSync: exec, service, account, stateDir, scriptPath });
  return unsupportedStore();
}
