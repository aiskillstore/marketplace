import { existsSync } from 'node:fs';
import { chmod, mkdir, open, readFile, rename, stat, unlink, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';

import { SKILL_VERSION } from './telemetry-client.mjs';
import {
  createCommunityJobContributionEnvelope,
  createSourceContributionEnvelope,
  normalizeCommunityJob,
  normalizeCommunitySource,
  validateCommunityJobList,
  validateCommunitySourceList,
} from './source-community-schema.mjs';

export const DEFAULT_SOURCE_COMMUNITY_ENDPOINT = process.env.JOB_APPLICATION_AGENT_SOURCE_COMMUNITY_URL ?? process.env.JOB_APPLICATION_AGENT_TELEMETRY_URL ?? 'https://job-application-agent-telemetry.varora1406.workers.dev';
export const SOURCE_SHARING_NOTICE = 'Community sharing is enabled by default. Confirmed public job links are logged privately and enter maintainer review before publication, as do repeatable job boards and hiring feeds. Personal, answer, resume, score, referral, and candidate timing data are never sent. Run `sources sharing disable` to opt out.\n';

const CONFIG_FILE = 'source-sharing.json';
const CONFIG_LOCK_FILE = '.source-sharing.lock';
const CONFIG_LOCK_TIMEOUT_MS = 15_000;
const CONFIG_LOCK_STALE_MS = 60_000;

function defaultConfig({ jobSharingGraceConsumed = true } = {}) {
  return { version: 1, enabled: true, disclosed: false, jobSharingDisclosed: false, jobSharingGraceConsumed, installationId: null, token: null, tokenExpiresAt: null };
}

function sameCredentialState(left, right) {
  return left.enabled === right.enabled
    && left.installationId === right.installationId
    && left.token === right.token
    && left.tokenExpiresAt === right.tokenExpiresAt;
}

function processIsAlive(pid) {
  if (!Number.isSafeInteger(pid) || pid <= 0) return false;
  if (pid === process.pid) return true;
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    if (error.code === 'ESRCH') return false;
    return true;
  }
}

async function writePrivate(file, value) {
  const temporary = `${file}.${process.pid}.tmp`;
  await writeFile(temporary, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
  await rename(temporary, file);
  await chmod(file, 0o600);
}

export class SourceCommunityClient {
  constructor({ stateDir, endpoint = DEFAULT_SOURCE_COMMUNITY_ENDPOINT, fetch: fetchFn = globalThis.fetch, stderr = (value) => process.stderr.write(value), now = () => new Date(), timeoutMs = Number(process.env.JOB_APPLICATION_AGENT_SOURCE_COMMUNITY_TIMEOUT_MS ?? 3000), historicalApplicationsAtStart = null }) {
    this.stateDir = stateDir;
    this.endpoint = endpoint.replace(/\/$/, '');
    this.fetch = fetchFn;
    this.stderr = stderr;
    this.now = now;
    this.timeoutMs = timeoutMs;
    this.historicalApplicationsAtStart = historicalApplicationsAtStart ?? existsSync(join(stateDir, 'applications.ndjson'));
  }

  initialConfig() { return defaultConfig({ jobSharingGraceConsumed: !this.historicalApplicationsAtStart }); }

  get configPath() { return join(this.stateDir, CONFIG_FILE); }
  get configLockPath() { return join(this.stateDir, CONFIG_LOCK_FILE); }

  async ensureDirectory() {
    await mkdir(this.stateDir, { recursive: true, mode: 0o700 });
    await chmod(this.stateDir, 0o700);
  }

  async readConfig() {
    try {
      const value = JSON.parse(await readFile(this.configPath, 'utf8'));
      return { version: 1, enabled: value.enabled !== false, disclosed: value.disclosed === true, jobSharingDisclosed: value.jobSharingDisclosed === true, jobSharingGraceConsumed: value.jobSharingGraceConsumed === true, installationId: value.installationId ?? null, token: value.token ?? null, tokenExpiresAt: value.tokenExpiresAt ?? null };
    } catch (error) {
      if (error.code === 'ENOENT') return null;
      return { version: 1, enabled: false, disclosed: true, jobSharingDisclosed: true, jobSharingGraceConsumed: true, installationId: null, token: null, tokenExpiresAt: null };
    }
  }

  async saveConfigUnlocked(config) {
    await this.ensureDirectory();
    await writePrivate(this.configPath, config);
  }

  async removeStaleConfigLock() {
    let contents;
    let metadata;
    try {
      [contents, metadata] = await Promise.all([
        readFile(this.configLockPath, 'utf8'),
        stat(this.configLockPath),
      ]);
    } catch (error) {
      if (error.code === 'ENOENT') return true;
      throw error;
    }
    const trimmed = contents.trim();
    const pid = /^\d+$/.test(trimmed) ? Number(trimmed) : null;
    const ownerIsDead = pid !== null && !processIsAlive(pid);
    const lockExpired = Date.now() - metadata.mtimeMs >= CONFIG_LOCK_STALE_MS;
    if (!ownerIsDead && !lockExpired) return false;
    try {
      if (await readFile(this.configLockPath, 'utf8') !== contents) return false;
      await unlink(this.configLockPath);
      return true;
    } catch (error) {
      if (error.code === 'ENOENT') return true;
      throw error;
    }
  }

  async withConfigLock(operation) {
    await this.ensureDirectory();
    const startedAt = Date.now();
    let handle;
    while (!handle) {
      try {
        handle = await open(this.configLockPath, 'wx', 0o600);
      } catch (error) {
        if (error.code !== 'EEXIST') throw error;
        if (await this.removeStaleConfigLock()) continue;
        if (Date.now() - startedAt >= CONFIG_LOCK_TIMEOUT_MS) throw new Error('Could not acquire source-sharing config lock.');
        await delay(20);
      }
    }
    try {
      await handle.writeFile(`${process.pid}\n`);
    } catch (error) {
      await handle.close();
      await unlink(this.configLockPath).catch(() => {});
      throw error;
    }
    try {
      return await operation();
    } finally {
      await handle.close();
      await unlink(this.configLockPath).catch((error) => { if (error.code !== 'ENOENT') throw error; });
    }
  }

  async updateConfig(transform) {
    return this.withConfigLock(async () => {
      const current = await this.readConfig() ?? this.initialConfig();
      const next = transform(current);
      await this.saveConfigUnlocked(next);
      return next;
    });
  }

  async config() {
    return this.withConfigLock(async () => {
      const existing = await this.readConfig();
      if (existing) return existing;
      const config = this.initialConfig();
      await this.saveConfigUnlocked(config);
      return config;
    });
  }

  async status() {
    const config = await this.readConfig();
    return { enabled: config?.enabled ?? true, disclosed: config?.disclosed ?? false, jobSharingDisclosed: config?.jobSharingDisclosed ?? false, hasInstallationId: Boolean(config?.installationId), endpoint: this.endpoint, schemaVersion: 1 };
  }

  async configure(action) {
    if (action === 'status') return this.status();
    let discloseJobSharing = false;
    await this.updateConfig((config) => {
      if (action === 'enable') {
        config.enabled = true;
        if (!config.jobSharingDisclosed) discloseJobSharing = true;
        config.jobSharingDisclosed = true;
        config.jobSharingGraceConsumed = true;
      }
      else if (action === 'disable') config.enabled = false;
      else if (action === 'reset') Object.assign(config, { enabled: false, disclosed: true, jobSharingDisclosed: false, jobSharingGraceConsumed: false, installationId: null, token: null, tokenExpiresAt: null });
      else throw new Error('Source sharing action must be status, enable, disable, or reset.');
      config.disclosed = true;
      return config;
    });
    if (discloseJobSharing) this.stderr(SOURCE_SHARING_NOTICE);
    return this.status();
  }

  async credentials(config) {
    if (config.installationId && config.token && config.tokenExpiresAt && Date.parse(config.tokenExpiresAt) > this.now().getTime() + 60_000) return config;
    let expectedState = config;
    let body = config.installationId && config.token ? { installationId: config.installationId, token: config.token } : {};
    let response = await this.fetch(`${this.endpoint}/v1/install`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body), signal: AbortSignal.timeout(this.timeoutMs) });
    if (response.status === 401 && body.installationId) {
      config = await this.updateConfig((current) => {
        if (current.installationId === body.installationId) Object.assign(current, { installationId: null, token: null, tokenExpiresAt: null });
        return current;
      });
      expectedState = config;
      body = {};
      response = await this.fetch(`${this.endpoint}/v1/install`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body), signal: AbortSignal.timeout(this.timeoutMs) });
    }
    if (!response.ok) throw new Error('community relay unavailable');
    const identity = await response.json();
    return this.updateConfig((current) => sameCredentialState(current, expectedState)
      ? { ...current, installationId: identity.installationId, token: identity.token, tokenExpiresAt: identity.expiresAt }
      : current);
  }

  async preview(input) {
    return normalizeCommunitySource(input);
  }

  async contribute(input) {
    const source = normalizeCommunitySource(input);
    try {
      let config = await this.config();
      if (!config.enabled) return { shared: false, reason: 'disabled' };
      if (!config.disclosed) {
        this.stderr(SOURCE_SHARING_NOTICE);
        config = await this.updateConfig((current) => ({ ...current, disclosed: true, jobSharingDisclosed: true, jobSharingGraceConsumed: true }));
        if (!config.enabled) return { shared: false, reason: 'disabled' };
      }
      config = await this.credentials(config);
      let sent = await this.sendContribution(config, source);
      if (sent.disabled) return { shared: false, reason: 'disabled' };
      let response = sent.response;
      if (response.status === 401) {
        config = await this.updateConfig((current) => ({ ...current, tokenExpiresAt: null }));
        config = await this.credentials(config);
        sent = await this.sendContribution(config, source);
        if (sent.disabled) return { shared: false, reason: 'disabled' };
        response = sent.response;
      }
      if (!response.ok) {
        return { shared: false, reason: 'unavailable' };
      }
      const result = await response.json();
      const allowed = new Set(['accepted', 'sourceId', 'publicationStatus', 'uniqueContributors']);
      if (!result || typeof result !== 'object' || Array.isArray(result) || Object.keys(result).some((key) => !allowed.has(key))) return { shared: false, reason: 'unavailable' };
      if (result.accepted !== true || !/^community-[0-9a-f]{16}$/.test(result.sourceId)) return { shared: false, reason: 'unavailable' };
      if (!['pending', 'published', 'rejected'].includes(result.publicationStatus)) return { shared: false, reason: 'unavailable' };
      if (!Number.isSafeInteger(result.uniqueContributors) || result.uniqueContributors < 1 || result.uniqueContributors > 1_000_000_000) return { shared: false, reason: 'unavailable' };
      return { shared: true, sourceId: result.sourceId, publicationStatus: result.publicationStatus, uniqueContributors: result.uniqueContributors };
    } catch {
      return { shared: false, reason: 'unavailable' };
    }
  }

  async sendContribution(config, source) {
    return this.withConfigLock(async () => {
      const current = await this.readConfig() ?? config;
      if (!current.enabled) return { disabled: true };
      const envelope = createSourceContributionEnvelope({ installationId: current.installationId, token: current.token, source, skillVersion: SKILL_VERSION });
      const response = await this.fetch(`${this.endpoint}/v1/sources`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(envelope), signal: AbortSignal.timeout(this.timeoutMs) });
      return { disabled: false, response };
    });
  }

  async contributeJob(input) {
    const job = normalizeCommunityJob(input);
    try {
      let config = await this.config();
      if (!config.enabled) return { shared: false, reason: 'disabled' };
      if (!config.jobSharingDisclosed) {
        this.stderr(SOURCE_SHARING_NOTICE);
        const grace = !config.jobSharingGraceConsumed;
        config = await this.updateConfig((current) => ({ ...current, disclosed: true, jobSharingDisclosed: true, jobSharingGraceConsumed: true }));
        if (!config.enabled) return { shared: false, reason: 'disabled' };
        if (grace) return { shared: false, reason: 'grace' };
      } else if (!config.jobSharingGraceConsumed) {
        config = await this.updateConfig((current) => ({ ...current, jobSharingGraceConsumed: true }));
        if (!config.enabled) return { shared: false, reason: 'disabled' };
        return { shared: false, reason: 'grace' };
      }
      config = await this.credentials(config);
      let sent = await this.sendJobContribution(config, job);
      if (sent.disabled) return { shared: false, reason: 'disabled' };
      let response = sent.response;
      if (response.status === 401) {
        config = await this.updateConfig((current) => ({ ...current, tokenExpiresAt: null }));
        config = await this.credentials(config);
        sent = await this.sendJobContribution(config, job);
        if (sent.disabled) return { shared: false, reason: 'disabled' };
        response = sent.response;
      }
      if (!response.ok) return { shared: false, reason: 'unavailable' };
      const result = await response.json();
      const allowed = new Set(['accepted', 'jobId', 'publicationStatus', 'contributionCount']);
      if (!result || typeof result !== 'object' || Array.isArray(result) || Object.keys(result).some((key) => !allowed.has(key))) return { shared: false, reason: 'unavailable' };
      if (result.accepted !== true || !/^community-job-[0-9a-f]{16}$/.test(result.jobId)) return { shared: false, reason: 'unavailable' };
      if (!['pending', 'published', 'rejected'].includes(result.publicationStatus)) return { shared: false, reason: 'unavailable' };
      if (!Number.isSafeInteger(result.contributionCount) || result.contributionCount < 1 || result.contributionCount > 1_000_000_000) return { shared: false, reason: 'unavailable' };
      return { shared: true, jobId: result.jobId, publicationStatus: result.publicationStatus, contributionCount: result.contributionCount };
    } catch {
      return { shared: false, reason: 'unavailable' };
    }
  }

  async sendJobContribution(config, job) {
    return this.withConfigLock(async () => {
      const current = await this.readConfig() ?? config;
      if (!current.enabled) return { disabled: true };
      const envelope = createCommunityJobContributionEnvelope({ installationId: current.installationId, token: current.token, job, skillVersion: SKILL_VERSION });
      const response = await this.fetch(`${this.endpoint}/v1/jobs`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(envelope), signal: AbortSignal.timeout(this.timeoutMs) });
      return { disabled: false, response };
    });
  }

  async list() {
    if (this.sourceReadUnavailable) return [];
    try {
      const response = await this.fetch(`${this.endpoint}/v1/sources`, { headers: { accept: 'application/json' }, signal: AbortSignal.timeout(this.timeoutMs) });
      if (!response.ok) return [];
      return validateCommunitySourceList(await response.json());
    } catch {
      this.sourceReadUnavailable = true;
      return [];
    }
  }

  async listJobs({ limit = 50, cursor = null } = {}) {
    if (this.jobReadUnavailable) return { version: 1, jobs: [], nextCursor: null };
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > 100) throw new Error('Community job limit must be between 1 and 100.');
    if (cursor !== null && (typeof cursor !== 'string' || !cursor || cursor.length > 1024)) throw new Error('Community job cursor is invalid.');
    try {
      const query = new URLSearchParams({ limit: String(limit) });
      if (cursor !== null) query.set('cursor', cursor);
      const response = await this.fetch(`${this.endpoint}/v1/jobs?${query}`, { headers: { accept: 'application/json' }, signal: AbortSignal.timeout(this.timeoutMs) });
      if (!response.ok) return { version: 1, jobs: [], nextCursor: null };
      return validateCommunityJobList(await response.json());
    } catch {
      this.jobReadUnavailable = true;
      return { version: 1, jobs: [], nextCursor: null };
    }
  }
}
