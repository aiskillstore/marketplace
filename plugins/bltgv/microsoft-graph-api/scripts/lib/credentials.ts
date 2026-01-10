import { homedir } from "os";
import { join } from "path";
import { readFile, writeFile, mkdir } from "fs/promises";
import type { Credential, CredentialStore } from "./types";

const CONFIG_DIR = join(homedir(), ".config", "api-skills");
const CREDENTIALS_FILE = join(CONFIG_DIR, "credentials.json");

export async function ensureConfigDir(): Promise<void> {
  await mkdir(CONFIG_DIR, { recursive: true });
}

export async function loadCredentials(): Promise<CredentialStore> {
  try {
    const content = await readFile(CREDENTIALS_FILE, "utf-8");
    return JSON.parse(content);
  } catch {
    return {};
  }
}

export async function saveCredentials(store: CredentialStore): Promise<void> {
  await ensureConfigDir();
  await writeFile(CREDENTIALS_FILE, JSON.stringify(store, null, 2));
}

export async function getCredential(
  service: string,
  profile: string = "default"
): Promise<Credential | null> {
  const store = await loadCredentials();
  return store[service]?.[profile] ?? null;
}

export async function setCredential(
  service: string,
  profile: string,
  credential: Credential
): Promise<void> {
  const store = await loadCredentials();
  if (!store[service]) {
    store[service] = {};
  }
  store[service][profile] = credential;
  await saveCredentials(store);
}

export async function listProfiles(service: string): Promise<string[]> {
  const store = await loadCredentials();
  return Object.keys(store[service] ?? {});
}

export async function deleteCredential(
  service: string,
  profile: string
): Promise<boolean> {
  const store = await loadCredentials();
  if (store[service]?.[profile]) {
    delete store[service][profile];
    if (Object.keys(store[service]).length === 0) {
      delete store[service];
    }
    await saveCredentials(store);
    return true;
  }
  return false;
}

export function isTokenExpired(credential: Credential): boolean {
  const expiresAt = new Date(credential.expiresAt);
  const now = new Date();
  // Consider expired if less than 5 minutes remaining
  return expiresAt.getTime() - now.getTime() < 5 * 60 * 1000;
}
