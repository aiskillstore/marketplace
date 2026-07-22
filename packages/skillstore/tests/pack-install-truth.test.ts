import { createHash } from 'node:crypto';
import { mkdtemp, readFile, stat, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { ManifestSkill } from '../src/lib/plugin-api.js';
import {
	buildPackOrchestrationReceipt,
	PACK_ORCHESTRATION_RECEIPT_FILE,
	type PackOrchestration,
} from '../src/lib/pack-orchestration.js';
import type { SkillLockEntry } from '../src/lib/skill-lock.js';
import { CLI_VERSION } from '../src/lib/version.js';
import {
	createPackInstallReporter,
	derivePackInstallOutcome,
	getAnonymousClientId,
	isInstallTelemetryDisabled,
	readbackPackInstall,
	type PackInstallReport,
} from '../src/lib/pack-install-truth.js';

const originalDoNotTrack = process.env.DO_NOT_TRACK;
const originalTelemetryDisabled = process.env.SKILLSTORE_TELEMETRY_DISABLED;
const originalConfigDir = process.env.SKILLSTORE_CONFIG_DIR;

afterEach(() => {
	if (originalDoNotTrack === undefined) delete process.env.DO_NOT_TRACK;
	else process.env.DO_NOT_TRACK = originalDoNotTrack;
	if (originalTelemetryDisabled === undefined) delete process.env.SKILLSTORE_TELEMETRY_DISABLED;
	else process.env.SKILLSTORE_TELEMETRY_DISABLED = originalTelemetryDisabled;
	if (originalConfigDir === undefined) delete process.env.SKILLSTORE_CONFIG_DIR;
	else process.env.SKILLSTORE_CONFIG_DIR = originalConfigDir;
});

describe('Pack install outcomes', () => {
	it('keeps the reported CLI version aligned with the package version', async () => {
		const packageJson = JSON.parse(
			await readFile(new URL('../package.json', import.meta.url), 'utf8')
		) as { version: string };
		expect(CLI_VERSION).toBe(packageJson.version);
	});

	it('classifies only full durable readback as complete', () => {
		expect(derivePackInstallOutcome(3, 3, true)).toEqual({
			status: 'complete',
			expectedSkillCount: 3,
			installedSkillCount: 3,
			failedSkillCount: 0,
			readbackPassed: true,
		});
	});

	it('classifies a final partial readback as partial', () => {
		expect(derivePackInstallOutcome(3, 2, false)).toEqual({
			status: 'partial',
			expectedSkillCount: 3,
			installedSkillCount: 2,
			failedSkillCount: 1,
			readbackPassed: false,
		});
	});

	it('classifies zero installed members and empty Packs as error', () => {
		expect(derivePackInstallOutcome(3, 0, false).status).toBe('error');
		expect(derivePackInstallOutcome(0, 0, true)).toEqual({
			status: 'error',
			expectedSkillCount: 0,
			installedSkillCount: 0,
			failedSkillCount: 0,
			readbackPassed: false,
		});
	});
});

describe('anonymous client identity and privacy', () => {
	it('persists a stable random UUID without device-derived data', async () => {
		const directory = await mkdtemp(join(tmpdir(), 'skillstore-client-id-'));
		const first = await getAnonymousClientId(directory);
		const second = await getAnonymousClientId(directory);

		expect(second).toBe(first);
		expect(first).toMatch(/^[0-9a-f-]{36}$/i);
		expect((await readFile(join(directory, 'anonymous-client-id'), 'utf8')).trim()).toBe(first);
	});

	it('uses a stable in-process fallback when the config directory is not writable', async () => {
		const directory = await mkdtemp(join(tmpdir(), 'skillstore-client-id-blocked-'));
		const blocker = join(directory, 'file-not-directory');
		await writeFile(blocker, 'blocked');
		const impossibleDirectory = join(blocker, 'skillstore');

		const first = await getAnonymousClientId(impossibleDirectory);
		const second = await getAnonymousClientId(impossibleDirectory);

		expect(second).toBe(first);
		await expect(stat(join(impossibleDirectory, 'anonymous-client-id'))).rejects.toBeDefined();
	});

	it.each([
		[{ DO_NOT_TRACK: '1' }, true],
		[{ SKILLSTORE_TELEMETRY_DISABLED: '1' }, true],
		[{}, false],
	] as const)('applies the telemetry opt-out gate', (env, expected) => {
		expect(isInstallTelemetryDisabled(env)).toBe(expected);
	});

	it('does not create an ID or reporter when telemetry is disabled', async () => {
		const parent = await mkdtemp(join(tmpdir(), 'skillstore-dnt-'));
		const configDirectory = join(parent, 'must-not-exist');
		process.env.DO_NOT_TRACK = '1';
		process.env.SKILLSTORE_CONFIG_DIR = configDirectory;
		const reporter = vi.fn();

		await expect(createPackInstallReporter(reporter)).resolves.toBeNull();
		expect(reporter).not.toHaveBeenCalled();
		await expect(stat(configDirectory)).rejects.toBeDefined();
	});
});

describe('Pack install reporting', () => {
	it('reports an attempt at most once with a stable idempotency key', async () => {
		delete process.env.DO_NOT_TRACK;
		delete process.env.SKILLSTORE_TELEMETRY_DISABLED;
		process.env.SKILLSTORE_CONFIG_DIR = await mkdtemp(join(tmpdir(), 'skillstore-report-'));
		const reports: PackInstallReport[] = [];
		const reporter = vi.fn(async (report: PackInstallReport) => {
			reports.push(report);
			return { success: true };
		});
		const attempt = await createPackInstallReporter(reporter, ['codex', 'codex']);
		const outcome = derivePackInstallOutcome(2, 2, true);

		await expect(attempt?.report(outcome)).resolves.toBe(true);
		await expect(attempt?.report(derivePackInstallOutcome(2, 0, false))).resolves.toBe(true);

		expect(reporter).toHaveBeenCalledOnce();
		expect(reports[0]).toMatchObject({
			method: 'cli',
			attemptId: attempt?.attemptId,
			status: 'complete',
			targetAgents: ['codex'],
			cliVersion: '0.1.10',
		});
	});

	it('contains reporting failures so they cannot replace the install result', async () => {
		delete process.env.DO_NOT_TRACK;
		delete process.env.SKILLSTORE_TELEMETRY_DISABLED;
		process.env.SKILLSTORE_CONFIG_DIR = await mkdtemp(join(tmpdir(), 'skillstore-report-failure-'));
		const attempt = await createPackInstallReporter(async () => {
			throw new Error('network unavailable');
		});

		await expect(attempt?.report(derivePackInstallOutcome(1, 1, true))).resolves.toBe(false);
	});
});

describe('Pack install readback', () => {
	const members: ManifestSkill[] = [
		{
			slug: 'owner-one',
			name: 'One',
			version: '1.0.0',
			authorVersion: '1.0.0',
			skillstoreRevision: 2,
			versionStatus: 'valid',
			treeHash: 'a'.repeat(64),
			contentHash: 'content-one',
			downloadUrl: '/one',
			artifact: {
				files: [
					{ path: 'SKILL.md', url: '/one/SKILL.md' },
					{ path: 'references/guide.md', url: '/one/references/guide.md' },
				],
			},
		},
		{
			slug: 'owner-two',
			name: 'Two',
			version: '2.0.0',
			authorVersion: '2.0.0',
			skillstoreRevision: 3,
			versionStatus: 'valid',
			treeHash: 'b'.repeat(64),
			contentHash: 'content-two',
			downloadUrl: '/two',
		},
	];

	function lockFor(member: ManifestSkill): SkillLockEntry {
		return {
			slug: member.slug,
			version: member.version ?? null,
			authorVersion: member.authorVersion,
			skillstoreRevision: member.skillstoreRevision,
			versionStatus: member.versionStatus,
			treeHash: member.treeHash,
			zipHash: `zip-${member.slug}`,
			source: 'skillstore',
			installedAt: '2026-07-17T00:00:00.000Z',
			updatedAt: '2026-07-17T00:00:00.000Z',
		};
	}

	it('requires canonical files, every actual target directory, and matching locks', async () => {
		const readPath = vi.fn(async () => new Uint8Array([1, 2, 3]));
		const result = await readbackPackInstall(members, ['/targets/codex', '/targets/claude'], undefined, {
			readPath,
			readLockEntry: async (slug) => lockFor(members.find((member) => member.slug === slug)!),
		});

		expect(result).toEqual({
			installedSkillCount: 2,
			failedSkillCount: 0,
			readbackPassed: true,
			failedSkillSlugs: [],
		});
		expect(readPath.mock.calls.map(([path]) => path)).toEqual(expect.arrayContaining([
			'/targets/codex/owner-one/SKILL.md',
			'/targets/claude/owner-one/SKILL.md',
			'/targets/codex/owner-one/references/guide.md',
			'/targets/claude/owner-one/references/guide.md',
			'/targets/codex/owner-two/SKILL.md',
			'/targets/claude/owner-two/SKILL.md',
		]));
	});

	it('counts only members whose final lock and filesystem state read back', async () => {
		const result = await readbackPackInstall(members, ['/targets/codex'], undefined, {
			readPath: async () => new Uint8Array([1, 2, 3]),
			readLockEntry: async (slug) => slug === members[0].slug ? lockFor(members[0]) : undefined,
		});

		expect(result).toEqual({
			installedSkillCount: 1,
			failedSkillCount: 1,
			readbackPassed: false,
			failedSkillSlugs: ['owner-two'],
		});
	});

	it('binds formal Pack readback to orchestration content, digest, receipt, and agent paths', async () => {
		const content = '# Verified workflow\n';
		const orchestration: PackOrchestration = {
			slug: 'skillstore-pack-business-review',
			packSlug: 'business-review',
			packVersion: '1.0.0',
			orchestrationVersion: '1.0.0',
		content,
		contentHash: createHash('sha256').update(content).digest('hex'),
		treeHash: createHash('sha256').update(JSON.stringify({
			path: 'SKILL.md', mode: '100644',
			sha256: createHash('sha256').update(content).digest('hex'), size: Buffer.byteLength(content),
		})).digest('hex'),
		bindingDigest: 'c'.repeat(64),
		};
		const receipt = Buffer.from(JSON.stringify(buildPackOrchestrationReceipt(orchestration)));
		const result = await readbackPackInstall(
			members,
			['/targets/codex', '/targets/claude'],
			orchestration,
			{
				readPath: async (path) => {
					if (path.endsWith(PACK_ORCHESTRATION_RECEIPT_FILE)) return receipt;
					if (path.includes(orchestration.slug)) return Buffer.from(content);
					return new Uint8Array([1, 2, 3]);
				},
				readLockEntry: async (slug) => lockFor(members.find((member) => member.slug === slug)!),
			}
		);

		expect(result).toMatchObject({
			installedSkillCount: 2,
			failedSkillCount: 0,
			readbackPassed: true,
			orchestration: {
				slug: orchestration.slug,
				canonicalId: orchestration.slug,
				version: orchestration.orchestrationVersion,
				contentHash: orchestration.contentHash,
				bindingDigest: orchestration.bindingDigest,
				agentPaths: [
					'/targets/codex/skillstore-pack-business-review',
					'/targets/claude/skillstore-pack-business-review',
				],
				readbackPassed: true,
			},
		});
	});

	it('fails formal Pack readback when one agent orchestration receipt differs', async () => {
		const content = '# Verified workflow\n';
		const orchestration: PackOrchestration = {
			slug: 'skillstore-pack-business-review',
			packSlug: 'business-review',
			packVersion: '1.0.0',
			orchestrationVersion: '1.0.0',
		content,
		contentHash: createHash('sha256').update(content).digest('hex'),
		treeHash: createHash('sha256').update(JSON.stringify({
			path: 'SKILL.md', mode: '100644',
			sha256: createHash('sha256').update(content).digest('hex'), size: Buffer.byteLength(content),
		})).digest('hex'),
		bindingDigest: 'c'.repeat(64),
		};
		const receipt = buildPackOrchestrationReceipt(orchestration);
		const result = await readbackPackInstall(
			members,
			['/targets/codex', '/targets/claude'],
			orchestration,
			{
				readPath: async (path) => {
					if (path.endsWith(PACK_ORCHESTRATION_RECEIPT_FILE)) {
						return Buffer.from(JSON.stringify(
							path.includes('/targets/claude/')
								? { ...receipt, orchestrationVersion: '2.0.0' }
								: receipt
						));
					}
					if (path.includes(orchestration.slug)) return Buffer.from(content);
					return new Uint8Array([1, 2, 3]);
				},
				readLockEntry: async (slug) => lockFor(members.find((member) => member.slug === slug)!),
			}
		);

		expect(result).toMatchObject({
			installedSkillCount: 2,
			failedSkillCount: 0,
			readbackPassed: false,
			orchestration: {
				canonicalId: orchestration.slug,
				version: orchestration.orchestrationVersion,
				readbackPassed: false,
			},
		});
	});
});
