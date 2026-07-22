import { defineCommand } from 'citty';
import { randomUUID } from 'node:crypto';
import { lstat, mkdir, readFile, rename, rm, writeFile } from 'node:fs/promises';
import { basename, dirname, join } from 'node:path';
import { getPluginConfig } from '../lib/plugin-config.js';
import {
	fetchManifest,
	reportPackInstallation,
	reportSkillInstall,
	PluginApiError,
} from '../lib/plugin-api.js';
import {
	fetchSkillManifest,
	downloadSkillZip,
	formatSkillVersionIdentity,
	getSkillLockVersionIdentity,
	getSkillZipHash,
	SkillApiError,
} from '../lib/skill-api.js';
import { verifyManifest, verifySkillManifest, verifyZipHash } from '../lib/plugin-verify.js';
import {
	printDownloadSummary,
	stagePackSkillDownloads,
	stagePackTargetLinks,
	type PackSkillDownloadTransaction,
	type PackTargetLinkTransaction,
} from '../lib/plugin-download.js';
import { logger } from '../lib/plugin-logger.js';
import {
	agents,
	detectDefaultInstallAgents,
	getAgentsByIds,
	isValidAgentId,
	CANONICAL_SKILLS_DIR,
	LOCK_FILE_PATH,
	type AgentConfig,
} from '../lib/agents.js';
import { addToLock, getLockEntry } from '../lib/skill-lock.js';
import { lockVerifiedPackMembers } from '../lib/pack-lock.js';
import {
	createPackInstallReporter,
	derivePackInstallOutcome,
	readbackPackInstall,
} from '../lib/pack-install-truth.js';
import { extractSkillZip, installToAgents, getCanonicalSkillPath } from '../lib/installer.js';
import {
	buildPackOrchestration,
	stagePackOrchestration,
	type PackOrchestrationTransaction,
} from '../lib/pack-orchestration.js';

/**
 * Normalize skill/plugin slug
 * Converts "owner/name" format to "owner-name" format
 */
function normalizeSlug(slug: string): string {
	return slug.replace(/\//g, '-');
}

/**
 * Unified add command
 *
 * - `skillstore add <slug>` → Add single skill
 * - `skillstore add @<plugin>` → Add plugin (skill collection)
 */
export default defineCommand({
	meta: {
		name: 'add',
		description: 'Add skills or plugins from skillstore.io',
	},
	args: {
		target: {
			type: 'positional',
			description: 'Skill slug or @plugin to add',
			required: true,
		},
		agent: {
			type: 'string',
			alias: 'a',
			description: 'Target specific agents (comma-separated)',
		},
		global: {
			type: 'boolean',
			alias: 'g',
			description: 'Install to user-level (~/) instead of project-level',
			default: true, // Default to global for skillstore
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
		const {
			target,
			agent: agentArg,
			global: isGlobal,
			'skip-verify': skipVerify,
			'dry-run': dryRun,
			overwrite,
		} = args;

		// Detect if target is a plugin (@prefix) or skill
		const isPlugin = target.startsWith('@');
		const rawSlug = isPlugin ? target.slice(1) : target;

		// Normalize slug: convert "owner/name" format to "owner-name"
		const slug = normalizeSlug(rawSlug);

		// Determine target agents
		let targetAgents: AgentConfig[];
		let reportTargetAgents: string[] | undefined;
		if (agentArg) {
			// Parse comma-separated agent IDs
			const agentIds = agentArg.split(',').map((s) => s.trim());
			const invalidIds = agentIds.filter((id) => !isValidAgentId(id));
			if (invalidIds.length > 0) {
				logger.error(`Invalid agent ID(s): ${invalidIds.join(', ')}`);
				console.log('');
				console.log('Valid agents include: claude, codex, claude-code, cursor, windsurf, cline, continue, etc.');
				process.exit(1);
			}
			targetAgents = getAgentsByIds(agentIds);
			reportTargetAgents = targetAgents.map((agent) => agent.id);
		} else {
			// Auto-detect the default Skillstore targets only.
			targetAgents = detectDefaultInstallAgents();
			if (targetAgents.length > 0) {
				reportTargetAgents = targetAgents.map((agent) => agent.id);
			}
			if (targetAgents.length === 0) {
				logger.warn('No Codex or Claude Code folders detected. Installing to Claude Code by default.');
				targetAgents = [agents['claude-code']];
			}
		}

		if (isPlugin) {
			await addPlugin(slug, { targetAgents, reportTargetAgents, isGlobal, skipVerify, dryRun, overwrite });
		} else {
			await addSkill(slug, { targetAgents, isGlobal, skipVerify, dryRun, overwrite });
		}
	},
});

interface AddOptions {
	targetAgents: AgentConfig[];
	reportTargetAgents?: string[];
	isGlobal: boolean;
	skipVerify: boolean;
	dryRun: boolean;
	overwrite: boolean;
}

interface PluginInstallTarget {
	agent: AgentConfig;
	installDir: string;
}

function getPluginInstallTargets(targetAgents: AgentConfig[], isGlobal: boolean): PluginInstallTarget[] {
	return targetAgents.map((agent) => ({
		agent,
		installDir: isGlobal ? agent.globalPath : join(process.cwd(), agent.projectPath),
	}));
}

type LockSnapshot = Uint8Array | undefined;

async function snapshotLock(): Promise<LockSnapshot> {
	try {
		const stat = await lstat(LOCK_FILE_PATH);
		if (!stat.isFile() || stat.isSymbolicLink()) {
			throw new Error(`Refusing to replace unsafe lock path: ${LOCK_FILE_PATH}`);
		}
		return await readFile(LOCK_FILE_PATH);
	} catch (error) {
		if ((error as NodeJS.ErrnoException).code === 'ENOENT') return undefined;
		throw error;
	}
}

async function restoreLock(snapshot: LockSnapshot): Promise<void> {
	try {
		const stat = await lstat(LOCK_FILE_PATH);
		if (!stat.isFile() || stat.isSymbolicLink()) {
			throw new Error(`Refusing to restore unsafe lock path: ${LOCK_FILE_PATH}`);
		}
	} catch (error) {
		if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
	}
	if (!snapshot) {
		await rm(LOCK_FILE_PATH, { force: true });
		return;
	}
	const lockDir = dirname(LOCK_FILE_PATH);
	const stagePath = join(lockDir, `.${basename(LOCK_FILE_PATH)}.restore-${randomUUID()}`);
	await mkdir(lockDir, { recursive: true });
	try {
		await writeFile(stagePath, snapshot, { mode: 0o600 });
		await rename(stagePath, LOCK_FILE_PATH);
	} finally {
		await rm(stagePath, { force: true });
	}
}

async function linkDownloadedSkillsToAgents(
	skillSlugs: string[],
	targetAgents: AgentConfig[],
	isGlobal: boolean
): Promise<{ successCount: number; failCount: number }> {
	let successCount = 0;
	let failCount = 0;

	for (const skillSlug of skillSlugs) {
		const installResult = await installToAgents(skillSlug, targetAgents, { global: isGlobal });
		successCount += installResult.successCount;
		failCount += installResult.failCount;

		for (const result of installResult.agents) {
			if (!result.success) {
				logger.error(`  ${skillSlug} -> ${result.agentId}: ${result.error}`);
			} else if (result.symlinkFailed) {
				logger.warn(`  ${skillSlug} -> ${result.agentId}: copied (symlink failed)`);
			} else {
				logger.debug(`  ${skillSlug} -> ${result.agentId}: linked`);
			}
		}
	}

	return { successCount, failCount };
}

/**
 * Add a single skill
 */
async function addSkill(slug: string, options: AddOptions): Promise<void> {
	const { targetAgents, isGlobal, skipVerify, dryRun, overwrite } = options;

	const config = getPluginConfig({
		installDir: CANONICAL_SKILLS_DIR, // Use canonical dir for extraction
		skipVerify,
		dryRun,
	});

	logger.info(`Adding skill: ${slug}`);
	logger.info(`Target agents: ${targetAgents.map((a) => a.name).join(', ')}`);

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
		const existingLock = await getLockEntry(slug);
		if (existingLock && !overwrite) {
			if (existingLock.zipHash === zipHash) {
				const identityChanged = existingLock.version !== lockIdentity.version
					|| existingLock.authorVersion !== lockIdentity.authorVersion
					|| (existingLock.skillstoreRevision ?? null) !== lockIdentity.skillstoreRevision
					|| existingLock.versionStatus !== lockIdentity.versionStatus
					|| (existingLock.treeHash ?? null) !== lockIdentity.treeHash;
				if (identityChanged && !dryRun) {
					await addToLock({
						...existingLock,
						...lockIdentity,
						zipHash,
					});
					logger.info(`Refreshed lock metadata: ${formatSkillVersionIdentity(lockIdentity)}`);
				}
				const installedIdentity = identityChanged ? lockIdentity : existingLock;
				logger.warn(`Skill "${slug}" is already installed (${formatSkillVersionIdentity(installedIdentity)})`);
				logger.info('Use --overwrite to reinstall');
				return;
			}
			logger.info(`Updating "${slug}" from ${formatSkillVersionIdentity(existingLock)} to ${formatSkillVersionIdentity(manifest.skill)}`);
		}

		if (dryRun) {
			logger.success('Dry run complete - no files were written');
			console.log('');
			console.log(`Would install to: ${getCanonicalSkillPath(slug)}`);
			console.log(`Would symlink to: ${targetAgents.map((a) => a.name).join(', ')}`);
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

		// Step 7: Extract ZIP to canonical location
		logger.startSpinner('Extracting files...');
		const canonicalPath = getCanonicalSkillPath(slug);
		await extractSkillZip(zipBuffer, canonicalPath);
		logger.spinnerSuccess('Extracted files');

		// Step 8: Create symlinks to agents
		logger.startSpinner('Creating symlinks to agents...');
		const installResult = await installToAgents(slug, targetAgents, { global: isGlobal });
		if (installResult.successCount > 0) {
			logger.spinnerSuccess(
				`Linked to ${installResult.successCount} agent${installResult.successCount > 1 ? 's' : ''}`
			);
		} else {
			logger.spinnerError('Failed to link to any agents');
		}

		// Show symlink results
		for (const result of installResult.agents) {
			if (result.success) {
				if (result.symlinkFailed) {
					logger.warn(`  ${result.agentId}: copied (symlink failed)`);
				} else {
					logger.debug(`  ${result.agentId}: symlinked`);
				}
			} else {
				logger.error(`  ${result.agentId}: ${result.error}`);
			}
		}

		// Step 9: Update lock file
		await addToLock({
			slug,
			...lockIdentity,
			zipHash,
			source: 'skillstore',
			installedAt: new Date().toISOString(),
		});
		logger.debug('Updated lock file');

		// Step 10: Report installation (non-blocking telemetry)
		try {
			await reportSkillInstall(config, slug);
			logger.debug('Installation telemetry reported');
		} catch {
			logger.debug('Failed to report telemetry (non-critical)');
		}

		logger.success(`Skill "${manifest.skill.name}" added successfully!`);
		console.log('');
		console.log(`Installed to: ${canonicalPath}`);
		console.log(`Agents: ${installResult.agents.filter((r) => r.success).map((r) => r.agentId).join(', ')}`);
	} catch (err) {
		logger.stopSpinner();

		if (err instanceof SkillApiError) {
			if (err.statusCode === 404) {
				logger.error(`Skill "${slug}" not found`);
				console.log('');
				console.log('Tip: Use @ prefix to add a plugin, e.g.:');
				console.log(`  npx skillstore add @${slug}`);
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
 * Add a plugin (skill collection)
 */
async function addPlugin(slug: string, options: AddOptions): Promise<void> {
	const { targetAgents, reportTargetAgents, isGlobal, skipVerify, dryRun, overwrite } = options;

	const installTargets = getPluginInstallTargets(targetAgents, isGlobal);

	const config = getPluginConfig({
		installDir: CANONICAL_SKILLS_DIR,
		skipVerify,
		dryRun,
	});
	const installTruth = dryRun ? null : await createPackInstallReporter(
		(report) => reportPackInstallation(config, slug, report),
		reportTargetAgents
	);
	let expectedSkillCount = 0;
	let memberTransaction: PackSkillDownloadTransaction | undefined;
	let targetTransaction: PackTargetLinkTransaction | undefined;
	let orchestrationTransaction: PackOrchestrationTransaction | undefined;
	let lockSnapshot: LockSnapshot;
	let hasLockSnapshot = false;

	logger.info(`Adding plugin: @${slug}`);
	logger.info(`Target agents: ${targetAgents.map((a) => a.name).join(', ')}`);
	logger.info(`Canonical directory: ${CANONICAL_SKILLS_DIR}`);
	for (const target of installTargets) {
		logger.info(`Target directory (${target.agent.name}): ${target.installDir}`);
	}

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
				logger.spinnerSuccess('Manifest structure valid');
				logger.warn(verifyResult.error);
			} else {
				logger.spinnerSuccess('Manifest verified');
			}
		} else {
			logger.warn('Skipping manifest signature verification');
		}

		// Step 3: Show plugin info
		const orchestration = skipVerify ? null : buildPackOrchestration(manifest);
		logger.box(`Plugin: ${manifest.plugin.name}`, [
			`Version: ${manifest.plugin.version}`,
			`Skills: ${manifest.skills.length}`,
			...(orchestration ? [`Workflow: ${orchestration.slug}`] : []),
			`Generated: ${new Date(manifest.generatedAt).toLocaleDateString()}`,
		]);
		if (dryRun && orchestration) logger.info(`Would install verified workflow: ${orchestration.slug}`);

		// Step 4: Download skills once to the canonical skills directory.
		logger.info('');
		memberTransaction = await stagePackSkillDownloads(config, manifest.skills, {
			overwrite,
			verifyHash: !skipVerify,
		});
		const downloadResult = memberTransaction.summary;
		if (!dryRun && downloadResult.failed > 0) {
			throw new Error(`Failed to stage ${downloadResult.failed} Pack member${downloadResult.failed === 1 ? '' : 's'}`);
		}
		printDownloadSummary(downloadResult);

		// Step 5: Link canonical skills into each selected agent directory.
		const successfulSkillSlugs = downloadResult.results.filter((r) => r.success).map((r) => r.slug);
		if (!dryRun && downloadResult.failed === 0 && successfulSkillSlugs.length > 0) {
			lockSnapshot = await snapshotLock();
			hasLockSnapshot = true;
			await memberTransaction.activate();
			targetTransaction = await stagePackTargetLinks(
				successfulSkillSlugs,
				installTargets.map((target) => target.installDir),
				config.installDir
			);
			await targetTransaction.activate();
			logger.startSpinner('Linking skills to agents...');
			const linkResult = await linkDownloadedSkillsToAgents(successfulSkillSlugs, targetAgents, isGlobal);
			if (linkResult.failCount > 0) {
				logger.spinnerError(`Linked with ${linkResult.failCount} failure${linkResult.failCount > 1 ? 's' : ''}`);
				throw new Error('Pack member agent linking failed');
			} else {
				logger.spinnerSuccess(
					`Linked ${successfulSkillSlugs.length} skill${successfulSkillSlugs.length > 1 ? 's' : ''} to ${targetAgents.length} agent${targetAgents.length > 1 ? 's' : ''}`
				);
			}
			const lockResult = await lockVerifiedPackMembers(config, manifest.skills, downloadResult);
			if (lockResult.skipped > 0) {
				throw new Error(`${lockResult.skipped} Pack member${lockResult.skipped > 1 ? 's were' : ' was'} left unlocked`);
			}
			const memberReadback = await readbackPackInstall(
				manifest.skills,
				installTargets.map((target) => target.installDir)
			);
			if (!memberReadback.readbackPassed) {
				throw new Error(`Pack member readback failed for: ${memberReadback.failedSkillSlugs.join(', ') || 'unknown member state'}`);
			} else if (orchestration) {
				logger.startSpinner('Installing verified Pack workflow...');
				orchestrationTransaction = await stagePackOrchestration(orchestration, targetAgents, isGlobal);
				logger.spinnerSuccess(`Installed workflow ${orchestration.slug}`);
			}
		}

		// Step 6: Report per-skill telemetry independently of Pack truth.
		if (!dryRun && installTruth && downloadResult.success > 0) {
			// Report telemetry for each successfully installed skill
			const newlyInstalledSkillSlugs = [
				...new Set(downloadResult.results.filter((r) => r.success && !r.skipped).map((r) => r.slug)),
			];
			if (newlyInstalledSkillSlugs.length > 0) {
				// Report in parallel, non-blocking
				Promise.all(newlyInstalledSkillSlugs.map((skillSlug) => reportSkillInstall(config, skillSlug))).catch(() => {
					logger.debug('Telemetry reporting failed (non-critical)');
				});
			}
		}

		let installOutcome = derivePackInstallOutcome(expectedSkillCount, 0, false);
		if (!dryRun && downloadResult.failed === 0) {
			const readback = await readbackPackInstall(
				manifest.skills,
				installTargets.map((target) => target.installDir),
				orchestration ?? undefined
			);
			installOutcome = derivePackInstallOutcome(
				expectedSkillCount,
				readback.installedSkillCount,
				readback.readbackPassed
			);
			if (readback.failedSkillSlugs.length > 0) {
				logger.warn(`Install readback failed for: ${readback.failedSkillSlugs.join(', ')}`);
			}
			if (readback.orchestration && !readback.orchestration.readbackPassed) {
				logger.warn(`Pack workflow readback failed: ${readback.orchestration.slug}`);
			}
		}
		if (!dryRun && installOutcome.status !== 'complete') {
			throw new Error(`Pack installation readback failed: ${installOutcome.failedSkillCount} member failure${installOutcome.failedSkillCount === 1 ? '' : 's'}`);
		}
		if (!dryRun) {
			const cleanupErrors = [
				...(await memberTransaction.commit()),
				...(await targetTransaction?.commit() ?? []),
				...(await orchestrationTransaction?.commit() ?? []),
			];
			memberTransaction = undefined;
			targetTransaction = undefined;
			orchestrationTransaction = undefined;
			for (const error of cleanupErrors) logger.warn(`Pack backup cleanup failed: ${error.message}`);
		}
		if (!dryRun) {
			const reported = await installTruth?.report(installOutcome);
			if (reported === false) logger.debug('Failed to report installation truth (non-critical)');
		}

		// Final status
		if (dryRun) {
			logger.success('Dry run complete - no files were written');
		} else {
			logger.success(`Plugin "@${manifest.plugin.slug}" added successfully!`);
		}
	} catch (caught) {
		const rollbackErrors: unknown[] = [];
		if (orchestrationTransaction) {
			try {
				await orchestrationTransaction.rollback();
			} catch (error) {
				rollbackErrors.push(error);
			}
		}
		if (targetTransaction) {
			try {
				await targetTransaction.rollback();
			} catch (error) {
				rollbackErrors.push(error);
			}
		}
		if (memberTransaction) {
			try {
				await memberTransaction.rollback();
			} catch (error) {
				rollbackErrors.push(error);
			}
		}
		if (hasLockSnapshot) {
			try {
				await restoreLock(lockSnapshot);
			} catch (error) {
				rollbackErrors.push(error);
			}
		}
		const err = rollbackErrors.length > 0
			? new AggregateError([caught, ...rollbackErrors], 'Pack installation and rollback failed')
			: caught;
		logger.stopSpinner();
		await installTruth?.report(derivePackInstallOutcome(expectedSkillCount, 0, false));

		if (err instanceof PluginApiError) {
			if (err.statusCode === 404) {
				logger.error(`Plugin "@${slug}" not found`);
				console.log('');
				console.log('Tip: Without @ prefix to add a single skill, e.g.:');
				console.log(`  npx skillstore add ${slug}`);
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
