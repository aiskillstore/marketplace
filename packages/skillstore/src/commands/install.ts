import { defineCommand } from 'citty';
import { access } from 'node:fs/promises';
import { getPluginConfig } from '../lib/plugin-config.js';
import { fetchManifest, reportInstallation, reportSkillInstall, PluginApiError } from '../lib/plugin-api.js';
import {
	fetchSkillManifest,
	downloadSkillZip,
	formatSkillVersionIdentity,
	getSkillLockVersionIdentity,
	getSkillZipHash,
	SkillApiError,
} from '../lib/skill-api.js';
import { verifyManifest, verifySkillManifest, verifyZipHash } from '../lib/plugin-verify.js';
import { downloadAllSkills, printDownloadSummary } from '../lib/plugin-download.js';
import { logger } from '../lib/plugin-logger.js';
import { CANONICAL_SKILLS_DIR } from '../lib/agents.js';
import { extractSkillZip, getCanonicalSkillPath, linkSkillToDirectory } from '../lib/installer.js';
import { addToLock, getLockEntry } from '../lib/skill-lock.js';
import { lockVerifiedPackMembers } from '../lib/pack-lock.js';

/**
 * Normalize skill/plugin slug
 * Converts "owner/name" format to "owner-name" format
 */
function normalizeSlug(slug: string): string {
	return slug.replace(/\//g, '-');
}

/**
 * Unified install command
 *
 * - `skillstore install <slug>` → Install single skill
 * - `skillstore install @<plugin>` → Install plugin (skill collection)
 */
export default defineCommand({
	meta: {
		name: 'install',
		description: 'Install skills or plugins from skillstore.io',
	},
	args: {
		target: {
			type: 'positional',
			description: 'Skill slug or @plugin to install',
			required: true,
		},
		dir: {
			type: 'string',
			description: 'Directory to link skills into (default: ~/.agents/skills)',
			default: CANONICAL_SKILLS_DIR,
		},
		'skip-verify': {
			type: 'boolean',
			description: 'Skip manifest signature verification',
			default: false,
		},
		'dry-run': {
			type: 'boolean',
			description: 'Show what would be installed without actually installing',
			default: false,
		},
		overwrite: {
			type: 'boolean',
			description: 'Overwrite existing files',
			default: false,
		},
	},
	async run({ args }) {
		const { target, dir, 'skip-verify': skipVerify, 'dry-run': dryRun, overwrite } = args;

		// Detect if target is a plugin (@prefix) or skill
		const isPlugin = target.startsWith('@');
		const rawSlug = isPlugin ? target.slice(1) : target;

		// Normalize slug: convert "owner/name" format to "owner-name"
		const slug = normalizeSlug(rawSlug);

		if (isPlugin) {
			await installPlugin(slug, { dir, skipVerify, dryRun, overwrite });
		} else {
			await installSkill(slug, { dir, skipVerify, dryRun, overwrite });
		}
	},
});

/**
 * Install a single skill
 */
async function installSkill(
	slug: string,
	options: { dir: string; skipVerify: boolean; dryRun: boolean; overwrite: boolean }
): Promise<void> {
	const { dir, skipVerify, dryRun, overwrite } = options;

	const config = getPluginConfig({
		installDir: CANONICAL_SKILLS_DIR,
		skipVerify,
		dryRun,
	});
	const targetConfig = getPluginConfig({ installDir: dir });

	logger.info(`Installing skill: ${slug}`);
	logger.info(`Canonical directory: ${CANONICAL_SKILLS_DIR}`);
	logger.info(`Target directory: ${targetConfig.installDir}`);

	if (dryRun) {
		logger.warn('Dry run mode - no files will be written');
	}

	try {
		// Step 1: Fetch skill manifest
		logger.startSpinner('Fetching skill manifest...');
		const manifest = await fetchSkillManifest(config, slug);
		logger.spinnerSuccess(`Found skill: "${manifest.skill.name}"`);
		const zipHash = getSkillZipHash(manifest);
		const lockIdentity = getSkillLockVersionIdentity(manifest.skill);

		// Step 2: Verify manifest signature
		if (!skipVerify) {
			logger.startSpinner('Verifying manifest signature...');
			const verifyResult = await verifySkillManifest(manifest);
			if (!verifyResult.valid) {
				logger.spinnerError('Manifest verification failed');
				logger.error(verifyResult.error || 'Unknown verification error');
				process.exit(1);
			}
			logger.spinnerSuccess('Manifest verified');
		} else {
			logger.warn('Skipping signature verification');
		}

		if (!zipHash) {
			logger.error('Manifest is missing ZIP hash');
			process.exit(1);
		}

		// Step 3: Show skill info
		logger.box(`Skill: ${manifest.skill.name}`, [
			`Slug: ${manifest.skill.slug}`,
			`Version: ${formatSkillVersionIdentity(manifest.skill)}`,
			`Author: ${manifest.skill.author || 'Unknown'}`,
		]);

		// Step 4: Check if already installed
		const skillDir = getCanonicalSkillPath(slug);
		if (!overwrite) {
			try {
				await access(skillDir);
				const existingLock = await getLockEntry(slug);
				const identityChanged = existingLock && existingLock.zipHash === zipHash && (
					existingLock.version !== lockIdentity.version
					|| existingLock.authorVersion !== lockIdentity.authorVersion
					|| (existingLock.skillstoreRevision ?? null) !== lockIdentity.skillstoreRevision
					|| existingLock.versionStatus !== lockIdentity.versionStatus
					|| (existingLock.treeHash ?? null) !== lockIdentity.treeHash
				);
				if (identityChanged && !dryRun) {
					await addToLock({ ...existingLock, ...lockIdentity, zipHash });
					logger.info(`Refreshed lock metadata: ${formatSkillVersionIdentity(lockIdentity)}`);
				}
				logger.warn(`Skill "${slug}" already exists. Use --overwrite to replace.`);
				return;
			} catch {
				// Directory doesn't exist, continue
			}
		}

		if (dryRun) {
			logger.success('Dry run complete - no files were written');
			console.log('');
			console.log(`Would install to: ${skillDir}`);
			return;
		}

		// Step 5: Download skill ZIP
		logger.startSpinner('Downloading skill...');
		const zipBuffer = await downloadSkillZip(config, slug, manifest);
		logger.spinnerSuccess('Downloaded skill package');

		// Step 6: Verify ZIP hash
		if (!skipVerify) {
			logger.startSpinner('Verifying content integrity...');
			if (!verifyZipHash(zipBuffer, zipHash)) {
				logger.spinnerError('Content verification failed');
				logger.error('ZIP hash mismatch - content may be corrupted or tampered');
				process.exit(1);
			}
			logger.spinnerSuccess('Content verified');
		}

		// Step 7: Extract ZIP
		logger.startSpinner('Extracting files...');
		await extractSkillZip(zipBuffer, skillDir);
		logger.spinnerSuccess('Extracted files');

		// Step 8: Link to requested directory
		logger.startSpinner('Linking skill...');
		const linkResult = await linkSkillToDirectory(slug, targetConfig.installDir);
		if (!linkResult.success) {
			logger.spinnerError('Failed to link skill');
			logger.error(linkResult.error || 'Unknown link error');
			process.exit(1);
		}
		if (linkResult.symlinkFailed) {
			logger.spinnerSuccess('Copied skill (symlink failed)');
		} else {
			logger.spinnerSuccess('Linked skill');
		}

		// Keep install and add behavior equivalent for check/update management.
		await addToLock({
			slug,
			...lockIdentity,
			zipHash,
			source: 'skillstore',
			installedAt: new Date().toISOString(),
		});

		// Step 9: Report installation (non-blocking telemetry)
		try {
			await reportSkillInstall(config, slug);
			logger.debug('Installation telemetry reported');
		} catch {
			logger.debug('Failed to report telemetry (non-critical)');
		}

		logger.success(`Skill "${manifest.skill.name}" installed successfully!`);
		console.log('');
		console.log(`Installed to: ${skillDir}`);
		console.log(`Linked to: ${linkResult.path}`);
	} catch (err) {
		logger.stopSpinner();

		if (err instanceof SkillApiError) {
			if (err.statusCode === 404) {
				logger.error(`Skill "${slug}" not found`);
				console.log('');
				console.log('Tip: Use @ prefix to install a plugin, e.g.:');
				console.log(`  npx skillstore install @${slug}`);
			} else {
				logger.error(`API error: ${err.message}`);
			}
		} else {
			logger.error('Installation failed', err instanceof Error ? err : undefined);
		}

		process.exit(1);
	}
}

/**
 * Install a plugin (skill collection)
 */
async function installPlugin(
	slug: string,
	options: { dir: string; skipVerify: boolean; dryRun: boolean; overwrite: boolean }
): Promise<void> {
	const { dir, skipVerify, dryRun, overwrite } = options;

	const config = getPluginConfig({
		installDir: CANONICAL_SKILLS_DIR,
		skipVerify,
		dryRun,
	});
	const targetConfig = getPluginConfig({ installDir: dir });

	logger.info(`Installing plugin: @${slug}`);
	logger.info(`Canonical directory: ${CANONICAL_SKILLS_DIR}`);
	logger.info(`Target directory: ${targetConfig.installDir}`);

	if (dryRun) {
		logger.warn('Dry run mode - no files will be written');
	}

	try {
		// Step 1: Fetch manifest
		logger.startSpinner('Fetching plugin manifest...');
		const manifest = await fetchManifest(config, slug);
		logger.spinnerSuccess(`Fetched manifest for "${manifest.plugin.name}"`);

		// Step 2: Verify manifest
		if (!skipVerify) {
			logger.startSpinner('Verifying manifest signature...');
			const verifyResult = await verifyManifest(manifest, { skipSignature: skipVerify });

			if (!verifyResult.valid) {
				logger.spinnerError('Manifest verification failed');
				logger.error(verifyResult.error || 'Unknown verification error');
				process.exit(1);
			}

			if (verifyResult.error) {
				logger.spinnerSuccess('Manifest structure valid');
				logger.warn(verifyResult.error);
			} else {
				logger.spinnerSuccess('Manifest verified');
			}
		} else {
			logger.warn('Skipping manifest signature verification');
		}

		// Step 3: Show plugin info
		logger.box(`Plugin: ${manifest.plugin.name}`, [
			`Version: ${manifest.plugin.version}`,
			`Skills: ${manifest.skills.length}`,
			`Generated: ${new Date(manifest.generatedAt).toLocaleDateString()}`,
		]);

		// Step 4: Download skills
		logger.info('');
		const downloadResult = await downloadAllSkills(config, manifest.skills, {
			overwrite,
			verifyHash: !skipVerify,
		});

		// Step 5: Print summary
		printDownloadSummary(downloadResult);

		if (!dryRun && downloadResult.failed === 0) {
			logger.startSpinner('Linking skills...');
			const successfulSkillSlugs = downloadResult.results.filter((r) => r.success).map((r) => r.slug);
			const linkResults = await Promise.all(
				successfulSkillSlugs.map((skillSlug) => linkSkillToDirectory(skillSlug, targetConfig.installDir))
			);
			const failedLinks = linkResults.filter((result) => !result.success);
			if (failedLinks.length > 0) {
				logger.spinnerError(`Failed to link ${failedLinks.length} skill${failedLinks.length > 1 ? 's' : ''}`);
				for (const result of failedLinks) {
					logger.error(result.error || `Failed to link ${result.path}`);
				}
				process.exit(1);
			}
			logger.spinnerSuccess(`Linked ${linkResults.length} skill${linkResults.length > 1 ? 's' : ''}`);
			const lockResult = await lockVerifiedPackMembers(config, manifest.skills, downloadResult);
			if (lockResult.skipped > 0) {
				logger.warn(`${lockResult.skipped} pack member${lockResult.skipped > 1 ? 's were' : ' was'} installed but left unlocked`);
			}
		}

		// Step 6: Report installation (non-blocking)
		if (!dryRun && downloadResult.success > 0) {
			try {
				const reportResult = await reportInstallation(config, slug, 'cli');
				if (reportResult.duplicate) {
					logger.debug('Installation already recorded');
				} else if (reportResult.success) {
					logger.debug('Installation reported successfully');
				}
			} catch {
				logger.debug('Failed to report installation (non-critical)');
			}

			// Report telemetry for each successfully installed skill
			const successfulSkills = downloadResult.results.filter(
				(r) => r.success && !r.skipped
			);
			if (successfulSkills.length > 0) {
				// Report in parallel, non-blocking
				Promise.all(
					successfulSkills.map((r) => reportSkillInstall(config, r.slug))
				).catch(() => {
					logger.debug('Telemetry reporting failed (non-critical)');
				});
			}
		}

		// Final status
		if (downloadResult.failed > 0) {
			logger.warn(`Installation completed with ${downloadResult.failed} failures`);
			process.exit(1);
		} else if (dryRun) {
			logger.success('Dry run complete - no files were written');
		} else {
			logger.success(`Plugin "@${manifest.plugin.slug}" installed successfully!`);
		}
	} catch (err) {
		logger.stopSpinner();

		if (err instanceof PluginApiError) {
			if (err.statusCode === 404) {
				logger.error(`Plugin "@${slug}" not found`);
				console.log('');
				console.log('Tip: Without @ prefix to install a single skill, e.g.:');
				console.log(`  npx skillstore install ${slug}`);
			} else if (err.statusCode === 403) {
				logger.error('Access denied - plugin may be private or require purchase');
			} else {
				logger.error(`API error: ${err.message}`);
			}
		} else {
			logger.error('Installation failed', err instanceof Error ? err : undefined);
		}

		process.exit(1);
	}
}
