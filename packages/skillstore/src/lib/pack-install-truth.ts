import { randomUUID } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { homedir, platform } from 'node:os';
import { isAbsolute, join, normalize, resolve, sep } from 'node:path';
import type { ManifestSkill } from './plugin-api.js';
import { getCanonicalSkillPath, sanitizeName } from './installer.js';
import { getLockEntry, type SkillLockEntry } from './skill-lock.js';
import { CLI_VERSION } from './version.js';

export type PackInstallStatus = 'complete' | 'partial' | 'error';
export type InstallOsPlatform = 'darwin' | 'linux' | 'win32' | 'other';

export interface PackInstallAttempt {
	attemptId: string;
	anonymousClientId: string;
}

export interface PackInstallOutcome {
	status: PackInstallStatus;
	expectedSkillCount: number;
	installedSkillCount: number;
	failedSkillCount: number;
	readbackPassed: boolean;
}

export interface PackInstallReport extends PackInstallOutcome {
	method: 'cli';
	attemptId: string;
	anonymousClientId: string;
	cliVersion: string;
	osPlatform: InstallOsPlatform;
	targetAgents?: string[];
}

export interface PackInstallReadback {
	installedSkillCount: number;
	failedSkillCount: number;
	readbackPassed: boolean;
	failedSkillSlugs: string[];
}

export interface PackInstallReportResult {
	success: boolean;
	duplicate?: boolean;
}

export interface PackInstallAttemptReporter {
	attemptId: string;
	report: (outcome: PackInstallOutcome) => Promise<boolean>;
}

const anonymousClientIds = new Map<string, string>();
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function defaultConfigDirectory(): string {
	const configured = process.env.SKILLSTORE_CONFIG_DIR?.trim();
	if (configured) return configured;
	const xdg = process.env.XDG_CONFIG_HOME?.trim();
	return join(xdg || join(homedir(), '.config'), 'skillstore');
}

function isUuid(value: string): boolean {
	return UUID_PATTERN.test(value.trim());
}

/**
 * Return a random anonymous installation identifier persisted in the user's
 * config directory. The value contains no host, account, path, or device data.
 * When the directory is not writable, it remains stable for this CLI process.
 */
export async function getAnonymousClientId(configDirectory = defaultConfigDirectory()): Promise<string> {
	const cached = anonymousClientIds.get(configDirectory);
	if (cached) return cached;

	const idPath = join(configDirectory, 'anonymous-client-id');
	try {
		const existing = (await readFile(idPath, 'utf8')).trim();
		if (isUuid(existing)) {
			anonymousClientIds.set(configDirectory, existing);
			return existing;
		}
	} catch {
		// Missing/unreadable state falls through to a new anonymous identifier.
	}

	const generated = randomUUID();
	anonymousClientIds.set(configDirectory, generated);

	try {
		await mkdir(configDirectory, { recursive: true, mode: 0o700 });
		try {
			await writeFile(idPath, `${generated}\n`, { encoding: 'utf8', flag: 'wx', mode: 0o600 });
		} catch (error) {
			if ((error as NodeJS.ErrnoException).code !== 'EEXIST') throw error;
			const concurrent = (await readFile(idPath, 'utf8')).trim();
			if (isUuid(concurrent)) {
				anonymousClientIds.set(configDirectory, concurrent);
				return concurrent;
			}
		}
	} catch {
		// Telemetry must never make installation fail. Keep the in-process ID.
	}

	return generated;
}

export async function createPackInstallAttempt(): Promise<PackInstallAttempt> {
	return {
		attemptId: randomUUID(),
		anonymousClientId: await getAnonymousClientId(),
	};
}

export function isInstallTelemetryDisabled(env: NodeJS.ProcessEnv = process.env): boolean {
	return env.DO_NOT_TRACK === '1' || env.SKILLSTORE_TELEMETRY_DISABLED === '1';
}

export function getInstallOsPlatform(value = platform()): InstallOsPlatform {
	return value === 'darwin' || value === 'linux' || value === 'win32' ? value : 'other';
}

export function derivePackInstallOutcome(
	expectedSkillCount: number,
	installedSkillCount: number,
	readbackPassed: boolean
): PackInstallOutcome {
	const expected = Math.max(0, expectedSkillCount);
	const installed = Math.max(0, Math.min(installedSkillCount, expected));
	const failed = Math.max(0, expected - installed);
	const complete = expected > 0 && installed === expected && failed === 0 && readbackPassed;
	const status: PackInstallStatus = complete ? 'complete' : installed > 0 ? 'partial' : 'error';

	return {
		status,
		expectedSkillCount: expected,
		installedSkillCount: installed,
		failedSkillCount: failed,
		readbackPassed: complete,
	};
}

export function createPackInstallReport(
	attempt: PackInstallAttempt,
	outcome: PackInstallOutcome,
	targetAgents?: string[]
): PackInstallReport {
	const normalizedAgents = targetAgents
		? [...new Set(targetAgents.map((agent) => agent.trim()).filter(Boolean))].slice(0, 32)
		: undefined;
	return {
		method: 'cli',
		attemptId: attempt.attemptId,
		anonymousClientId: attempt.anonymousClientId,
		...outcome,
		cliVersion: CLI_VERSION,
		osPlatform: getInstallOsPlatform(),
		...(normalizedAgents && normalizedAgents.length > 0
			? { targetAgents: normalizedAgents }
			: {}),
	};
}

/** Best-effort reporting must never replace the install command's exit result. */
export async function reportPackInstallBestEffort(
	report: PackInstallReport,
	reporter: (report: PackInstallReport) => Promise<PackInstallReportResult>
): Promise<boolean> {
	try {
		const result = await reporter(report);
		return result.success || result.duplicate === true;
	} catch {
		return false;
	}
}

/**
 * Create one reporter per real CLI invocation. Repeated finalization calls use
 * the same attempt ID and never emit a second request from this process.
 */
export async function createPackInstallReporter(
	reporter: (report: PackInstallReport) => Promise<PackInstallReportResult>,
	targetAgents?: string[]
): Promise<PackInstallAttemptReporter | null> {
	if (isInstallTelemetryDisabled()) return null;
	const attempt = await createPackInstallAttempt();
	let result: Promise<boolean> | undefined;
	return {
		attemptId: attempt.attemptId,
		report(outcome) {
			result ??= reportPackInstallBestEffort(
				createPackInstallReport(attempt, outcome, targetAgents),
				reporter
			);
			return result;
		},
	};
}

function hasOwn(value: object, key: PropertyKey): boolean {
	return Object.prototype.hasOwnProperty.call(value, key);
}

function lockMatchesMember(lock: SkillLockEntry | undefined, member: ManifestSkill): boolean {
	if (!lock) return false;
	const authorVersion = hasOwn(member, 'authorVersion')
		? member.authorVersion ?? null
		: member.version ?? null;
	const version = member.version ?? authorVersion;
	const versionStatus = member.versionStatus || (authorVersion ? 'legacy_unknown' : 'missing');

	return lock.slug === member.slug
		&& lock.version === version
		&& (lock.authorVersion ?? null) === authorVersion
		&& (lock.skillstoreRevision ?? null) === (member.skillstoreRevision ?? null)
		&& lock.versionStatus === versionStatus
		&& (lock.treeHash ?? null) === (member.treeHash ?? null)
		&& !!lock.zipHash;
}

interface ReadbackDependencies {
	readPath: (path: string) => Promise<Uint8Array>;
	readLockEntry: (slug: string) => Promise<SkillLockEntry | undefined>;
}

const defaultReadbackDependencies: ReadbackDependencies = {
	readPath: async (path) => readFile(path),
	readLockEntry: getLockEntry,
};

function getMemberArtifactPaths(member: ManifestSkill): string[] {
	const paths = member.artifact?.files?.length
		? member.artifact.files.map((file) => file.path)
		: ['SKILL.md'];
	return [...new Set(paths)];
}

function resolveReadbackPath(root: string, filePath: string): string {
	if (!filePath || isAbsolute(filePath)) throw new Error('Invalid artifact path');
	const normalizedPath = normalize(filePath);
	if (normalizedPath === '..' || normalizedPath.startsWith(`..${sep}`)) {
		throw new Error('Invalid artifact path');
	}
	const resolvedRoot = resolve(root);
	const resolvedPath = resolve(resolvedRoot, normalizedPath);
	if (resolvedPath !== resolvedRoot && resolvedPath.startsWith(`${resolvedRoot}${sep}`)) {
		return resolvedPath;
	}
	throw new Error('Invalid artifact path');
}

/**
 * Verify the durable post-install state. A member counts only when its
 * canonical SKILL.md, every requested target link/copy, and matching lock entry
 * can all be read back after writes finish.
 */
export async function readbackPackInstall(
	members: ManifestSkill[],
	targetDirectories: string[],
	dependencies: ReadbackDependencies = defaultReadbackDependencies
): Promise<PackInstallReadback> {
	const uniqueTargetDirectories = [...new Set(targetDirectories)];
	const failedSkillSlugs: string[] = [];

	for (const member of members) {
		try {
			const canonicalRoot = getCanonicalSkillPath(member.slug);
			for (const artifactPath of getMemberArtifactPaths(member)) {
				const canonicalBytes = await dependencies.readPath(resolveReadbackPath(canonicalRoot, artifactPath));
				for (const targetDirectory of uniqueTargetDirectories) {
					const targetRoot = join(targetDirectory, sanitizeName(member.slug));
					const targetBytes = await dependencies.readPath(resolveReadbackPath(targetRoot, artifactPath));
					if (!Buffer.from(targetBytes).equals(Buffer.from(canonicalBytes))) {
						throw new Error('Target content mismatch');
					}
				}
			}
			const lock = await dependencies.readLockEntry(member.slug);
			if (!lockMatchesMember(lock, member)) throw new Error('Lock identity mismatch');
		} catch {
			failedSkillSlugs.push(member.slug);
		}
	}

	const installedSkillCount = members.length - failedSkillSlugs.length;
	return {
		installedSkillCount,
		failedSkillCount: failedSkillSlugs.length,
		readbackPassed: members.length > 0 && failedSkillSlugs.length === 0,
		failedSkillSlugs,
	};
}
