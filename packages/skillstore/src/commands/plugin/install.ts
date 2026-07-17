import { defineCommand } from 'citty';
import { getPluginConfig } from '../../lib/plugin-config.js';
import { fetchManifest, reportPackInstallation, PluginApiError } from '../../lib/plugin-api.js';
import { verifyManifest } from '../../lib/plugin-verify.js';
import { downloadAllSkills, printDownloadSummary } from '../../lib/plugin-download.js';
import { logger } from '../../lib/plugin-logger.js';
import { CANONICAL_SKILLS_DIR } from '../../lib/agents.js';
import { linkSkillToDirectory } from '../../lib/installer.js';
import { lockVerifiedPackMembers } from '../../lib/pack-lock.js';
import {
	createPackInstallReporter,
	derivePackInstallOutcome,
	readbackPackInstall,
} from '../../lib/pack-install-truth.js';

export default defineCommand({
	meta: {
		name: 'install',
		description: 'Install a plugin (collection of skills) to your project',
	},
	args: {
		slug: {
			type: 'positional',
			description: 'Plugin slug to install',
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
			description: 'Overwrite existing skill files',
			default: false,
		},
	},
	async run({ args }) {
		const { slug, dir, 'skip-verify': skipVerify, 'dry-run': dryRun, overwrite } = args;

		// Build config from args
		const config = getPluginConfig({
			installDir: CANONICAL_SKILLS_DIR,
			skipVerify,
			dryRun,
		});
		const targetConfig = getPluginConfig({ installDir: dir });
		const installTruth = dryRun ? null : await createPackInstallReporter(
			(report) => reportPackInstallation(config, slug, report)
		);
		let expectedSkillCount = 0;

		logger.info(`Installing plugin: ${slug}`);
		logger.info(`Canonical directory: ${CANONICAL_SKILLS_DIR}`);
		logger.info(`Target directory: ${targetConfig.installDir}`);

		if (dryRun) {
			logger.warn('Dry run mode - no files will be written');
		}

		try {
			// Step 1: Fetch manifest
			logger.startSpinner('Fetching plugin manifest...');
			const manifest = await fetchManifest(config, slug);
			expectedSkillCount = manifest.skills.length;
			logger.spinnerSuccess(`Fetched manifest for "${manifest.plugin.name}"`);

			// Step 2: Verify manifest
			if (!skipVerify) {
				logger.startSpinner('Verifying manifest signature...');
				const verifyResult = await verifyManifest(manifest, { skipSignature: skipVerify });

				if (!verifyResult.valid) {
					logger.spinnerError('Manifest verification failed');
					logger.error(verifyResult.error || 'Unknown verification error');
					throw new Error(verifyResult.error || 'Manifest verification failed');
				}

				if (verifyResult.error) {
					// Warning but continue
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
					await installTruth?.report(derivePackInstallOutcome(expectedSkillCount, 0, false));
					process.exit(1);
				}
				logger.spinnerSuccess(`Linked ${linkResults.length} skill${linkResults.length > 1 ? 's' : ''}`);
				const lockResult = await lockVerifiedPackMembers(config, manifest.skills, downloadResult);
				if (lockResult.skipped > 0) {
					logger.warn(`${lockResult.skipped} pack member${lockResult.skipped > 1 ? 's were' : ' was'} installed but left unlocked`);
				}
			}

			let installOutcome = derivePackInstallOutcome(expectedSkillCount, 0, false);
			if (!dryRun && downloadResult.failed === 0) {
				const readback = await readbackPackInstall(manifest.skills, [targetConfig.installDir]);
				installOutcome = derivePackInstallOutcome(
					expectedSkillCount,
					readback.installedSkillCount,
					readback.readbackPassed
				);
				if (readback.failedSkillSlugs.length > 0) {
					logger.warn(`Install readback failed for: ${readback.failedSkillSlugs.join(', ')}`);
				}
			}
			if (!dryRun) {
				const reported = await installTruth?.report(installOutcome);
				if (reported === false) logger.debug('Failed to report installation truth (non-critical)');
			}

			// Final status
			if (!dryRun && installOutcome.status !== 'complete') {
				logger.warn(`Installation did not complete: ${installOutcome.failedSkillCount} member failure${installOutcome.failedSkillCount === 1 ? '' : 's'}`);
				process.exit(1);
			} else if (dryRun) {
				logger.success('Dry run complete - no files were written');
			} else {
				logger.success(`Plugin "${manifest.plugin.name}" installed successfully!`);
			}
		} catch (err) {
			logger.stopSpinner();
			await installTruth?.report(derivePackInstallOutcome(expectedSkillCount, 0, false));

			if (err instanceof PluginApiError) {
				if (err.statusCode === 404) {
					logger.error(`Plugin "${slug}" not found`);
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
	},
});
