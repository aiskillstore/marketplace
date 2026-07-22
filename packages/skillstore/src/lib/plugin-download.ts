import { createHash, randomUUID } from 'node:crypto';
import { mkdir, rm, writeFile, lstat, readFile, readdir, readlink, rename } from 'node:fs/promises';
import { basename, dirname, isAbsolute, join, normalize, relative, resolve, sep } from 'node:path';
import type { PluginConfig } from './plugin-config.js';
import type { ManifestSkill, ManifestSkillArtifactFile } from './plugin-api.js';
import { downloadSkillFile, MAX_ARTIFACT_FILE_BYTES } from './plugin-api.js';
import { verifyContentHash } from './plugin-verify.js';
import { logger } from './plugin-logger.js';
import { sanitizeName } from './installer.js';

/**
 * Plugin Skill Downloader
 *
 * Downloads skills from the Skillstore API with concurrent downloads,
 * progress tracking, and content hash verification.
 */

/** Download result for a single skill */
export interface SkillDownloadResult {
	slug: string;
	success: boolean;
	path?: string;
	error?: string;
	skipped?: boolean;
}

/** Download summary */
export interface DownloadSummary {
	total: number;
	success: number;
	failed: number;
	skipped: number;
	results: SkillDownloadResult[];
}

export const MAX_PACK_SKILLS = 100;
export const MAX_PACK_ARTIFACT_FILES = 256;
export const MAX_PACK_ARTIFACT_BYTES = 50 * 1024 * 1024;

interface StagedSkill {
	skillDir: string;
	stageDir: string;
	backupDir: string;
	hadPrevious: boolean;
	activated: boolean;
	backupCreated: boolean;
}

export interface PackSkillDownloadTransaction {
	summary: DownloadSummary;
	activate(): Promise<void>;
	commit(): Promise<Error[]>;
	rollback(): Promise<void>;
}

interface PackTarget {
	path: string;
	canonicalPath: string;
	backupPath: string;
	hadPrevious: boolean;
	activated: boolean;
	backupCreated: boolean;
}

export interface PackTargetLinkTransaction {
	activate(): Promise<void>;
	commit(): Promise<Error[]>;
	rollback(): Promise<void>;
}

function sha256Hex(bytes: Uint8Array): string {
	return createHash('sha256').update(bytes).digest('hex');
}

function verifyBytesHash(bytes: Uint8Array, expectedHash: string): boolean {
	if (!/^[0-9a-f]{64}$/.test(expectedHash)) return false;
	const actualHash = sha256Hex(bytes);
	return actualHash === expectedHash;
}

function getSkillDir(config: PluginConfig, skillSlug: string): string {
	const skillDir = join(config.installDir, sanitizeName(skillSlug));
	const installDir = resolve(config.installDir);
	if (resolve(skillDir).startsWith(`${installDir}${sep}`)) return skillDir;
	throw new Error(`Invalid skill path: ${skillSlug}`);
}

async function directoryState(path: string): Promise<'missing' | 'directory' | 'symlink' | 'other'> {
	try {
		const stat = await lstat(path);
		if (stat.isSymbolicLink()) return 'symlink';
		return stat.isDirectory() ? 'directory' : 'other';
	} catch (error) {
		if ((error as NodeJS.ErrnoException).code === 'ENOENT') return 'missing';
		throw error;
	}
}

function resolveSkillFilePath(skillDir: string, filePath: string): string {
	if (!filePath || isAbsolute(filePath)) {
		throw new Error(`Invalid artifact path: ${filePath || '<empty>'}`);
	}

	const normalizedPath = normalize(filePath);
	if (normalizedPath === '..' || normalizedPath.startsWith(`..${sep}`)) {
		throw new Error(`Invalid artifact path: ${filePath}`);
	}

	const targetPath = resolve(skillDir, normalizedPath);
	const rootPath = resolve(skillDir);
	if (targetPath !== rootPath && targetPath.startsWith(`${rootPath}${sep}`)) {
		return targetPath;
	}

	throw new Error(`Invalid artifact path: ${filePath}`);
}

function getArtifactFiles(skill: ManifestSkill): ManifestSkillArtifactFile[] {
	if (Array.isArray(skill.artifact?.files) && skill.artifact.files.length > 0) {
		const hasSkillMd = skill.artifact.files.some((file) => normalize(file.path) === 'SKILL.md');
		if (!hasSkillMd) {
			throw new Error('Skill artifact is missing SKILL.md');
		}
		return skill.artifact.files;
	}

	return [{
		path: 'SKILL.md',
		url: skill.downloadUrl,
	}];
}

function normalizedArtifactPath(filePath: string): string {
	return resolveSkillFilePath('/skill-root', filePath).slice('/skill-root/'.length).split(sep).join('/');
}

function treeHash(entries: Array<{ path: string; mode: string; sha256: string; size: number }>): string {
	return createHash('sha256').update(entries
		.sort((left, right) => left.path.localeCompare(right.path, 'en', { sensitivity: 'variant' }))
		.map((entry) => JSON.stringify(entry))
		.join('\n')).digest('hex');
}

/**
 * A pre-existing member may be reused only after its complete on-disk tree
 * matches the signed artifact inventory and immutable Pack identity.
 */
export async function verifyInstalledPackMember(skillDir: string, skill: ManifestSkill): Promise<void> {
	if (!skill.artifact?.files?.length || !/^[0-9a-f]{64}$/.test(skill.treeHash ?? '')) {
		throw new Error(`Existing skill cannot be reused without a signed artifact tree: ${skill.slug}`);
	}

	const expected = new Map<string, ManifestSkillArtifactFile>();
	for (const file of getArtifactFiles(skill)) {
		const path = normalizedArtifactPath(file.path);
		if (!/^[0-9a-f]{64}$/.test(file.sha256 ?? '') || !Number.isSafeInteger(file.bytes) || file.bytes! < 0) {
			throw new Error(`Existing skill cannot be reused without signed file hashes: ${skill.slug}`);
		}
		if (expected.has(path)) throw new Error(`Existing skill has duplicate signed artifact path: ${skill.slug}`);
		expected.set(path, file);
	}
	if (skill.contentHash !== expected.get('SKILL.md')?.sha256) {
		throw new Error(`Existing skill content identity does not match signed manifest: ${skill.slug}`);
	}

	const entries: Array<{ path: string; mode: string; sha256: string; size: number }> = [];
	const root = resolve(skillDir);
	const walk = async (directory: string): Promise<void> => {
		const children = await readdir(directory, { withFileTypes: true });
		for (const child of children) {
			const path = join(directory, child.name);
			const relativePath = relative(root, path).split('\\').join('/');
			const stat = await lstat(path);
			if (stat.isSymbolicLink() || (!stat.isDirectory() && !stat.isFile())) {
				throw new Error(`Unsupported existing skill entry: ${relativePath}`);
			}
			if (stat.isDirectory()) {
				await walk(path);
				continue;
			}
			const bytes = await readFile(path);
			entries.push({
				path: relativePath,
				mode: (stat.mode & 0o111) === 0 ? '100644' : '100755',
				sha256: sha256Hex(bytes),
				size: bytes.byteLength,
			});
		}
	};
	await walk(root);

	if (entries.length !== expected.size || entries.some((entry) => {
		const signed = expected.get(entry.path);
		return !signed || signed.sha256 !== entry.sha256 || signed.bytes !== entry.size;
	})) {
		throw new Error(`Existing skill does not match signed artifact files: ${skill.slug}`);
	}
	if (treeHash(entries) !== skill.treeHash) {
		throw new Error(`Existing skill tree hash does not match signed manifest: ${skill.slug}`);
	}
}

function validatePackManifest(skills: ManifestSkill[]): void {
	if (skills.length > MAX_PACK_SKILLS) {
		throw new Error(`Pack has too many Skills (maximum ${MAX_PACK_SKILLS})`);
	}
	if (new Set(skills.map((skill) => skill.slug)).size !== skills.length) {
		throw new Error('Pack has duplicate Skill slugs');
	}
	let fileCount = 0;
	let declaredBytes = 0;
	for (const skill of skills) {
		const files = getArtifactFiles(skill);
		const paths = new Set<string>();
		fileCount += files.length;
		if (fileCount > MAX_PACK_ARTIFACT_FILES) {
			throw new Error(`Pack has too many artifact files (maximum ${MAX_PACK_ARTIFACT_FILES})`);
		}
		if (!skill.artifact) continue;
		for (const file of files) {
			const path = normalizedArtifactPath(file.path);
			if (paths.has(path)) throw new Error(`Pack has duplicate artifact path: ${file.path}`);
			paths.add(path);
			if (!/^[0-9a-f]{64}$/.test(file.sha256 ?? '')) {
				throw new Error(`Missing exact SHA-256 for artifact file ${file.path}`);
			}
			if (!Number.isSafeInteger(file.bytes) || file.bytes! < 0 || file.bytes! > MAX_ARTIFACT_FILE_BYTES) {
				throw new Error(`Invalid signed byte count for artifact file ${file.path}`);
			}
			declaredBytes += file.bytes!;
			if (declaredBytes > MAX_PACK_ARTIFACT_BYTES) {
				throw new Error(`Pack artifacts exceed ${MAX_PACK_ARTIFACT_BYTES} byte limit`);
			}
		}
	}
}

/**
 * Download all skills from a manifest with concurrent downloads
 */
export async function downloadAllSkills(
	config: PluginConfig,
	skills: ManifestSkill[],
	options: {
		overwrite?: boolean;
		verifyHash?: boolean;
	} = {}
): Promise<DownloadSummary> {
	const transaction = await stagePackSkillDownloads(config, skills, options);
	if (transaction.summary.failed === 0) {
		try {
			await transaction.activate();
			await transaction.commit();
		} catch (error) {
			await transaction.rollback();
			throw error;
		}
	} else {
		await transaction.rollback();
		for (const result of transaction.summary.results) {
			if (result.success && !result.skipped) {
				result.success = false;
				result.error = 'Pack download aborted because another member failed';
				transaction.summary.success--;
				transaction.summary.failed++;
			}
		}
	}
	return transaction.summary;
}

/**
 * Stage every Pack member before changing a live directory. The caller keeps
 * the transaction open until linking, locking, and readback have succeeded.
 */
export async function stagePackSkillDownloads(
	config: PluginConfig,
	skills: ManifestSkill[],
	options: {
		overwrite?: boolean;
		verifyHash?: boolean;
	} = {}
): Promise<PackSkillDownloadTransaction> {
	const { overwrite = false, verifyHash = true } = options;
	validatePackManifest(skills);
	const results: SkillDownloadResult[] = [];
	const staged: StagedSkill[] = [];
	let success = 0;
	let failed = 0;
	let skipped = 0;
	let downloadedBytes = 0;
	const consumeBytes = (bytes: number) => {
		if (downloadedBytes + bytes > MAX_PACK_ARTIFACT_BYTES) {
			throw new Error(`Pack artifacts exceed ${MAX_PACK_ARTIFACT_BYTES} byte limit`);
		}
		downloadedBytes += bytes;
	};

	// Start progress tracking
	logger.startProgress(skills.length, 'Downloading skills');

	// Process skills in batches for concurrency
	const batchSize = config.maxConcurrent;

	for (let i = 0; i < skills.length; i += batchSize) {
		const batch = skills.slice(i, i + batchSize);

		const batchResults = await Promise.all(
			batch.map((skill) =>
				stageSingleSkill(config, skill, { overwrite, verifyHash }, consumeBytes)
			)
		);

		for (const { result, stagedSkill } of batchResults) {
			results.push(result);
			if (stagedSkill) staged.push(stagedSkill);
			if (result.success) {
				if (result.skipped) {
					skipped++;
				} else {
					success++;
				}
			} else {
				failed++;
			}
			logger.incrementProgress();
		}
	}

	logger.completeProgress();

	const summary = {
		total: skills.length,
		success,
		failed,
		skipped,
		results,
	};

	let closed = false;
	return {
		summary,
		async activate() {
			if (closed) throw new Error('Pack download transaction is closed');
			if (summary.failed > 0) throw new Error('Cannot activate failed Pack download');
			for (const entry of staged) {
				if (entry.activated) continue;
				const liveState = await directoryState(entry.skillDir);
				if (entry.hadPrevious) {
					if (liveState !== 'directory') {
						throw new Error(`Refusing to replace changed skill path: ${entry.skillDir}`);
					}
					await rename(entry.skillDir, entry.backupDir);
					entry.backupCreated = true;
				} else if (liveState !== 'missing') {
					throw new Error(`Refusing to replace changed skill path: ${entry.skillDir}`);
				}
				await rename(entry.stageDir, entry.skillDir);
				entry.activated = true;
			}
		},
		async commit() {
			if (closed) return [];
			const cleanupErrors: Error[] = [];
			for (const entry of staged) {
				if (!entry.backupCreated) continue;
				try {
					await rm(entry.backupDir, { recursive: true, force: true });
				} catch (error) {
					cleanupErrors.push(error instanceof Error ? error : new Error(String(error)));
				}
			}
			closed = true;
			return cleanupErrors;
		},
		async rollback() {
			if (closed) return;
			const rollbackErrors: unknown[] = [];
			for (const entry of [...staged].reverse()) {
				try {
					if (entry.activated) {
						if (await directoryState(entry.skillDir) !== 'directory') {
							throw new Error(`Refusing to remove changed skill path: ${entry.skillDir}`);
						}
						await rm(entry.skillDir, { recursive: true, force: true });
					}
					if (entry.backupCreated) await rename(entry.backupDir, entry.skillDir);
				} catch (error) {
					rollbackErrors.push(error);
				} finally {
					await rm(entry.stageDir, { recursive: true, force: true }).catch((error) => rollbackErrors.push(error));
				}
			}
			closed = true;
			if (rollbackErrors.length > 0) {
				throw new AggregateError(rollbackErrors, 'Pack member rollback failed');
			}
		},
	};
}

/**
 * Download and verify a single skill into its sibling staging directory.
 */
async function stageSingleSkill(
	config: PluginConfig,
	skill: ManifestSkill,
	options: { overwrite: boolean; verifyHash: boolean },
	consumeBytes: (bytes: number) => void
): Promise<{ result: SkillDownloadResult; stagedSkill?: StagedSkill }> {
	const skillDir = getSkillDir(config, skill.slug);
	const parent = dirname(skillDir);
	const suffix = randomUUID();
	const stageDir = join(parent, `.${basename(skillDir)}.stage-${suffix}`);
	const backupDir = join(parent, `.${basename(skillDir)}.backup-${suffix}`);

	try {
		// Dry run mode - don't actually download
		if (config.dryRun) {
			return { result: { slug: skill.slug, success: true, path: skillDir, skipped: true } };
		}

		const artifactFiles = getArtifactFiles(skill).map((file) => ({
			file,
			targetPath: resolveSkillFilePath(stageDir, file.path),
		}));
		const currentState = await directoryState(skillDir);
		if (currentState !== 'missing' && currentState !== 'directory') {
			throw new Error(`Refusing to replace non-directory skill path: ${skillDir}`);
		}
		if (currentState === 'directory' && !options.overwrite) {
			await verifyInstalledPackMember(skillDir, skill);
			return { result: { slug: skill.slug, success: true, path: skillDir, skipped: true } };
		}
		await mkdir(parent, { recursive: true });
		await mkdir(stageDir, { recursive: false, mode: 0o700 });

		for (const { file, targetPath } of artifactFiles) {
			const expectedBytes = skill.artifact ? file.bytes : undefined;
			const content = await downloadSkillFile(config, file.url, {
				maxBytes: expectedBytes ?? MAX_ARTIFACT_FILE_BYTES,
				expectedBytes,
				onBytes: consumeBytes,
			});

			if (options.verifyHash) {
				const expectedHash = file.sha256 || (normalize(file.path) === 'SKILL.md' ? skill.contentHash : '');
				if (expectedHash) {
					const hashValid = normalize(file.path) === 'SKILL.md' && !file.sha256
						? verifyContentHash(new TextDecoder().decode(content), expectedHash)
						: verifyBytesHash(content, expectedHash);
					if (!hashValid) {
						throw new Error(`Content hash verification failed for ${file.path}`);
					}
				}
			}

			await mkdir(dirname(targetPath), { recursive: true });
			await writeFile(targetPath, content);
		}

		return {
			result: { slug: skill.slug, success: true, path: skillDir },
			stagedSkill: {
				skillDir,
				stageDir,
				backupDir,
				hadPrevious: currentState === 'directory',
				activated: false,
				backupCreated: false,
			},
		};
	} catch (err) {
		await rm(stageDir, { recursive: true, force: true });
		return { result: {
			slug: skill.slug,
			success: false,
			error: err instanceof Error ? err.message : 'Unknown error',
		} };
	}
}

function targetState(path: string): Promise<'missing' | 'directory' | 'symlink' | 'other'> {
	return directoryState(path);
}

/**
 * Move every existing Pack target aside before linking, so a failed Pack can
 * restore the prior symlink or copied directory exactly.
 */
export async function stagePackTargetLinks(
	skillSlugs: string[],
	targetDirs: string[],
	canonicalDir: string
): Promise<PackTargetLinkTransaction> {
	const targets: PackTarget[] = [];
	const seen = new Set<string>();
	for (const targetDir of targetDirs) {
		const resolvedTargetDir = resolve(targetDir);
		for (const slug of skillSlugs) {
			const name = sanitizeName(slug);
			const path = join(targetDir, name);
			const canonicalPath = join(canonicalDir, name);
			if (!resolve(path).startsWith(`${resolvedTargetDir}${sep}`)) {
				throw new Error(`Invalid Pack target path: ${path}`);
			}
			if (resolve(path) === resolve(canonicalPath) || seen.has(resolve(path))) continue;
			seen.add(resolve(path));
			const state = await targetState(path);
			if (state === 'symlink') {
				const target = await readlink(path);
				if (resolve(dirname(path), target) !== resolve(canonicalPath)) {
					throw new Error(`Refusing to replace unowned Pack target link: ${path}`);
				}
			} else if (state !== 'missing' && state !== 'directory') {
				throw new Error(`Refusing to replace non-directory Pack target path: ${path}`);
			}
			const suffix = randomUUID();
			targets.push({
				path,
				canonicalPath,
				backupPath: join(dirname(path), `.${basename(path)}.pack-backup-${suffix}`),
				hadPrevious: state !== 'missing',
				activated: false,
				backupCreated: false,
			});
		}
	}

	let closed = false;
	return {
		async activate() {
			if (closed) throw new Error('Pack target transaction is closed');
			for (const target of targets) {
				if (target.activated) continue;
				if (!target.hadPrevious) {
					if (await targetState(target.path) !== 'missing') {
						throw new Error(`Refusing to replace changed Pack target path: ${target.path}`);
					}
					target.activated = true;
					continue;
				}
				const state = await targetState(target.path);
				if (state !== 'directory' && state !== 'symlink') {
					throw new Error(`Refusing to replace changed Pack target path: ${target.path}`);
				}
				await rename(target.path, target.backupPath);
				target.backupCreated = true;
				target.activated = true;
			}
		},
		async commit() {
			if (closed) return [];
			const cleanupErrors: Error[] = [];
			for (const target of targets) {
				if (!target.backupCreated) continue;
				try {
					await rm(target.backupPath, { recursive: true, force: true });
				} catch (error) {
					cleanupErrors.push(error instanceof Error ? error : new Error(String(error)));
				}
			}
			closed = true;
			return cleanupErrors;
		},
		async rollback() {
			if (closed) return;
			const rollbackErrors: unknown[] = [];
			for (const target of [...targets].reverse()) {
				try {
					if (target.activated) {
						const state = await targetState(target.path);
						if (state === 'symlink') {
							const link = await readlink(target.path);
							if (resolve(dirname(target.path), link) !== resolve(target.canonicalPath)) {
								throw new Error(`Refusing to remove changed Pack target link: ${target.path}`);
							}
						} else if (state !== 'missing' && state !== 'directory') {
							throw new Error(`Refusing to remove changed Pack target path: ${target.path}`);
						}
						if (state !== 'missing') await rm(target.path, { recursive: true, force: true });
					}
					if (target.backupCreated) await rename(target.backupPath, target.path);
				} catch (error) {
					rollbackErrors.push(error);
				}
			}
			closed = true;
			if (rollbackErrors.length > 0) throw new AggregateError(rollbackErrors, 'Pack target rollback failed');
		},
	};
}

/**
 * Print download summary
 */
export function printDownloadSummary(summary: DownloadSummary): void {
	console.log('');
	console.log('Download Summary:');

	for (const result of summary.results) {
		if (result.success) {
			if (result.skipped) {
				logger.skillSummary(result.slug, 'skipped');
			} else {
				logger.skillSummary(result.slug, 'installed');
			}
		} else {
			logger.skillSummary(result.slug, 'failed');
			if (result.error) {
				console.log(`    Error: ${result.error}`);
			}
		}
	}

	console.log('');
	console.log(
		`Total: ${summary.total} | Installed: ${summary.success} | Skipped: ${summary.skipped} | Failed: ${summary.failed}`
	);
}
