import { defineCommand } from 'citty';
import { mkdir, writeFile, access } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { getPluginConfig } from '../lib/plugin-config.js';
import { fetchManifest, reportInstallation, reportSkillInstall, PluginApiError } from '../lib/plugin-api.js';
import { fetchSkillInfo, downloadSkillZip, SkillApiError } from '../lib/skill-api.js';
import { verifyManifest } from '../lib/plugin-verify.js';
import { downloadAllSkills, printDownloadSummary } from '../lib/plugin-download.js';
import { logger } from '../lib/plugin-logger.js';

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
			description: 'Installation directory (default: .claude/skills)',
			default: '.claude/skills',
		},
		'skip-verify': {
			type: 'boolean',
			description: 'Skip manifest signature verification (plugins only)',
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
			await installSkill(slug, { dir, dryRun, overwrite });
		}
	},
});

/**
 * Install a single skill
 */
async function installSkill(
	slug: string,
	options: { dir: string; dryRun: boolean; overwrite: boolean }
): Promise<void> {
	const { dir, dryRun, overwrite } = options;

	const config = getPluginConfig({
		installDir: dir,
		dryRun,
	});

	logger.info(`Installing skill: ${slug}`);
	logger.info(`Target directory: ${config.installDir}`);

	if (dryRun) {
		logger.warn('Dry run mode - no files will be written');
	}

	try {
		// Step 1: Fetch skill info
		logger.startSpinner('Fetching skill info...');
		const skillInfo = await fetchSkillInfo(config, slug);
		logger.spinnerSuccess(`Found skill: "${skillInfo.name}"`);

		// Step 2: Show skill info
		logger.box(`Skill: ${skillInfo.name}`, [
			`Slug: ${skillInfo.slug}`,
			`Version: ${skillInfo.version || 'N/A'}`,
			`Author: ${skillInfo.author || 'Unknown'}`,
			`Category: ${skillInfo.category || 'N/A'}`,
		]);

		// Step 3: Check if already installed
		const skillDir = join(config.installDir, slug);
		if (!overwrite) {
			try {
				await access(skillDir);
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

		// Step 4: Download skill ZIP
		logger.startSpinner('Downloading skill...');
		const zipBuffer = await downloadSkillZip(config, slug);
		logger.spinnerSuccess('Downloaded skill package');

		// Step 5: Extract ZIP
		logger.startSpinner('Extracting files...');
		await extractZip(zipBuffer, config.installDir);
		logger.spinnerSuccess('Extracted files');

		// Step 6: Report installation (non-blocking telemetry)
		try {
			await reportSkillInstall(config, slug);
			logger.debug('Installation telemetry reported');
		} catch {
			logger.debug('Failed to report telemetry (non-critical)');
		}

		logger.success(`Skill "${skillInfo.name}" installed successfully!`);
		console.log('');
		console.log(`Installed to: ${skillDir}`);
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
		installDir: dir,
		skipVerify,
		dryRun,
	});

	logger.info(`Installing plugin: @${slug}`);
	logger.info(`Target directory: ${config.installDir}`);

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

/**
 * Extract ZIP buffer to directory
 */
async function extractZip(buffer: ArrayBuffer, targetDir: string): Promise<void> {
	// Use fflate for extraction
	const { unzipSync } = await import('fflate');

	const data = new Uint8Array(buffer);
	const unzipped = unzipSync(data);

	for (const [path, content] of Object.entries(unzipped)) {
		// Skip directories (they end with /)
		if (path.endsWith('/')) continue;

		const fullPath = join(targetDir, path);
		await mkdir(dirname(fullPath), { recursive: true });
		await writeFile(fullPath, Buffer.from(content as Uint8Array));
	}
}
