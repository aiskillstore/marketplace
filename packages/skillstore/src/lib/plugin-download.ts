import { mkdir, writeFile, access } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import type { PluginConfig } from './plugin-config.js';
import type { ManifestSkill } from './plugin-api.js';
import { downloadSkill } from './plugin-api.js';
import { verifyContentHash } from './plugin-verify.js';
import { logger } from './plugin-logger.js';

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
	const skillPath = join(config.installDir, `${skill.slug}.md`);

	try {
		// Check if skill already exists
		if (!options.overwrite) {
			try {
				await access(skillPath);
				// File exists, skip
				return {
					slug: skill.slug,
					success: true,
					path: skillPath,
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
				path: skillPath,
				skipped: true,
			};
		}

		// Download skill content
		const content = await downloadSkill(config, skill.downloadUrl);

		// Verify content hash if enabled
		if (options.verifyHash && skill.contentHash) {
			const hashValid = verifyContentHash(content, skill.contentHash);
			if (!hashValid) {
				return {
					slug: skill.slug,
					success: false,
					error: 'Content hash verification failed',
				};
			}
		}

		// Ensure directory exists
		await mkdir(dirname(skillPath), { recursive: true });

		// Write skill file
		await writeFile(skillPath, content, 'utf-8');

		return {
			slug: skill.slug,
			success: true,
			path: skillPath,
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
