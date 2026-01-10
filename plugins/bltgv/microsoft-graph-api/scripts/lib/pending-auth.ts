/**
 * Pending Auth State Management
 *
 * Stores in-progress device code flow state on disk so authentication
 * can be resumed without conversation context.
 */

import { homedir } from "os";
import { join } from "path";
import { mkdir, readFile, writeFile, unlink } from "fs/promises";

export interface PendingAuth {
  deviceCode: string;
  userCode: string;
  verificationUri: string;
  expiresAt: string;
  clientId: string;
  tenantId: string;
  scopes: string[];
  profile: string;
}

interface PendingAuthStore {
  [service: string]: {
    [profile: string]: PendingAuth;
  };
}

const PENDING_AUTH_PATH = join(
  homedir(),
  ".config",
  "api-skills",
  "pending-auth.json"
);

async function ensureDir(): Promise<void> {
  const dir = join(homedir(), ".config", "api-skills");
  await mkdir(dir, { recursive: true });
}

async function loadStore(): Promise<PendingAuthStore> {
  try {
    const data = await readFile(PENDING_AUTH_PATH, "utf-8");
    const parsed = JSON.parse(data);
    return typeof parsed === "object" && parsed !== null ? parsed : {};
  } catch {
    return {};
  }
}

async function saveStore(store: PendingAuthStore): Promise<void> {
  await ensureDir();
  await writeFile(PENDING_AUTH_PATH, JSON.stringify(store, null, 2));
}

export async function getPendingAuth(
  service: string,
  profile: string
): Promise<PendingAuth | null> {
  const store = await loadStore();
  return store[service]?.[profile] ?? null;
}

export async function setPendingAuth(
  service: string,
  profile: string,
  pending: PendingAuth
): Promise<void> {
  const store = await loadStore();
  if (!store[service]) {
    store[service] = {};
  }
  store[service][profile] = pending;
  await saveStore(store);
}

export async function deletePendingAuth(
  service: string,
  profile: string
): Promise<void> {
  const store = await loadStore();
  if (store[service]?.[profile]) {
    delete store[service][profile];
    if (Object.keys(store[service]).length === 0) {
      delete store[service];
    }
    await saveStore(store);
  }
}

export function isPendingExpired(pending: PendingAuth): boolean {
  const expiresAt = new Date(pending.expiresAt);
  return expiresAt.getTime() <= Date.now();
}
