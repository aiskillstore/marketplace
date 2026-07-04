import { createHash } from 'node:crypto';
import { mkdir, rm, writeFile, access } from 'node:fs/promises';
import { dirname, isAbsolute, join, normalize, resolve, sep } from 'node:path';
import type { PluginConfig } from './plugin-config.js';
import type { ManifestSkill, ManifestSkillArtifactFile } from './plugin-api.js';
import { downloadSkillFile } from './plugin-api.js';
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

function sha256Hex(bytes: Uint8Array): string {
	return createHash('sha256').update(bytes).digest('hex');
}

function verifyBytesHash(bytes: Uint8Array, expectedHash: string): boolean {
	const actualHash = sha256Hex(bytes);
	const compareLength = Math.min(actualHash.length, expectedHash.length);
	return actualHash.substring(0, compareLength) === expectedHash.substring(0, compareLength);
}

function getSkillDir(config: PluginConfig, skillSlug: string): string {
	return join(config.installDir, sanitizeName(skillSlug));
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
	const { overwrite = false, verifyHash = true } = options;
	const results: SkillDownloadResult[] = [];
	let success = 0;
	let failed = 0;
	let skipped = 0;

	// Start progress tracking
	logger.startProgress(skills.length, 'Downloading skills');

	// Process skills in batches for concurrency
	const batchSize = config.maxConcurrent;

	for (let i = 0; i < skills.length; i += batchSize) {
		const batch = skills.slice(i, i + batchSize);

		const batchResults = await Promise.all(
			batch.map((skill) =>
				downloadSingleSkill(config, skill, { overwrite, verifyHash })
			)
		);

		for (const result of batchResults) {
			results.push(result);
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

	return {
		total: skills.length,
		success,
		failed,
		skipped,
		results,
	};
}

/**
 * Download a single skill
 */
async function downloadSingleSkill(
	config: PluginConfig,
	skill: ManifestSkill,
	options: { overwrite: boolean; verifyHash: boolean }
): Promise<SkillDownloadResult> {
	const skillDir = getSkillDir(config, skill.slug);
	const skillPath = join(skillDir, 'SKILL.md');

	try {
		// Check if skill already exists
		if (!options.overwrite) {
			try {
				await access(skillPath);
				// File exists, skip
				return {
					slug: skill.slug,
					success: true,
					path: skillDir,
					skipped: true,
				};
			} catch {
				// File doesn't exist, continue with download
			}
		}

		// Dry run mode - don't actually download
		if (config.dryRun) {
			return {
				slug: skill.slug,
				success: true,
				path: skillDir,
				skipped: true,
			};
		}

		const artifactFiles = getArtifactFiles(skill).map((file) => ({
			file,
			targetPath: resolveSkillFilePath(skillDir, file.path),
		}));

		if (options.overwrite) {
			await rm(skillDir, { recursive: true, force: true });
		}

		for (const { file, targetPath } of artifactFiles) {
			const content = await downloadSkillFile(config, file.url);

			if (options.verifyHash) {
				const expectedHash = file.sha256 || (normalize(file.path) === 'SKILL.md' ? skill.contentHash : '');
				if (expectedHash) {
					const hashValid = normalize(file.path) === 'SKILL.md' && !file.sha256
						? verifyContentHash(new TextDecoder().decode(content), expectedHash)
						: verifyBytesHash(content, expectedHash);
					if (!hashValid) {
						return {
							slug: skill.slug,
							success: false,
							error: `Content hash verification failed for ${file.path}`,
						};
					}
				}
			}

			await mkdir(dirname(targetPath), { recursive: true });
			await writeFile(targetPath, content);
		}

		return {
			slug: skill.slug,
			success: true,
			path: skillDir,
		};
	} catch (err) {
		return {
			slug: skill.slug,
			success: false,
			error: err instanceof Error ? err.message : 'Unknown error',
		};
	}
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
