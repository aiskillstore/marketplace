import { cp, mkdir, rm, symlink, lstat, readlink, access, writeFile } from 'node:fs/promises';
import { dirname, join, normalize, resolve, sep, relative } from 'node:path';
import { platform } from 'node:os';
import { type AgentConfig, type AgentId, CANONICAL_SKILLS_DIR } from './agents.js';

/**
 * Skill Installer
 *
 * Handles installation of skills to multiple agent directories
 * using symlinks for efficient storage.
 */

export type InstallMode = 'symlink' | 'copy';

export interface InstallResult {
	success: boolean;
	agentId: AgentId;
	path: string;
	canonicalPath?: string;
	mode: InstallMode;
	symlinkFailed?: boolean;
	error?: string;
}

export interface DirectoryInstallResult {
	success: boolean;
	path: string;
	canonicalPath?: string;
	mode: InstallMode;
	symlinkFailed?: boolean;
	error?: string;
}

export interface MultiAgentInstallResult {
	slug: string;
	canonicalPath: string;
	agents: InstallResult[];
	success: boolean;
	successCount: number;
	failCount: number;
}

/**
 * Sanitizes a filename/directory name to prevent path traversal attacks
 */
export function sanitizeName(name: string): string {
	let sanitized = name.replace(/[\/\\:\0]/g, '');
	sanitized = sanitized.replace(/^[.\s]+|[.\s]+$/g, '');
	sanitized = sanitized.replace(/^\.+/, '');

	if (!sanitized || sanitized.length === 0) {
		sanitized = 'unnamed-skill';
	}

	if (sanitized.length > 255) {
		sanitized = sanitized.substring(0, 255);
	}

	return sanitized;
}

/**
 * Validates that a path is within an expected base directory
 */
function isPathSafe(basePath: string, targetPath: string): boolean {
	const normalizedBase = normalize(resolve(basePath));
	const normalizedTarget = normalize(resolve(targetPath));

	return normalizedTarget.startsWith(normalizedBase + sep) || normalizedTarget === normalizedBase;
}

/**
 * Get canonical skill directory path
 */
export function getCanonicalSkillPath(slug: string): string {
	const sanitized = sanitizeName(slug);
	return join(CANONICAL_SKILLS_DIR, sanitized);
}

function normalizeZipPath(path: string): string {
	return path.replace(/\\/g, '/').replace(/^\/+/, '');
}

function getStripRootDirectory(paths: string[]): string | undefined {
	const files = paths
		.map(normalizeZipPath)
		.filter((path) => path && !path.endsWith('/'));
	const topLevelFiles = files.filter((path) => !path.includes('/'));
	if (files.length === 0 || topLevelFiles.length > 0) {
		return undefined;
	}

	const roots = new Set(files.map((path) => path.split('/')[0]));
	if (roots.size !== 1) {
		return undefined;
	}

	const [root] = roots;
	return files.includes(`${root}/SKILL.md`) ? root : undefined;
}

function getSafeZipEntryPath(rawPath: string, stripRoot?: string): string | undefined {
	let path = normalizeZipPath(rawPath);
	if (!path || path.endsWith('/')) {
		return undefined;
	}

	if (stripRoot && path.startsWith(`${stripRoot}/`)) {
		path = path.slice(stripRoot.length + 1);
	}

	const segments = path.split('/');
	if (!path || segments.some((segment) => !segment || segment === '.' || segment === '..')) {
		throw new Error(`Invalid ZIP entry path: ${rawPath}`);
	}

	return path;
}

/**
 * Extract a skill ZIP into its canonical directory.
 *
 * Skillstore ZIPs may contain either files at the archive root or a single
 * top-level skill folder. The latter is normalized so agents always see
 * `<skill>/SKILL.md` at the canonical skill root.
 */
export async function extractSkillZip(buffer: ArrayBuffer, targetDir: string): Promise<void> {
	const { unzipSync } = await import('fflate');

	const data = new Uint8Array(buffer);
	const unzipped = unzipSync(data);
	const stripRoot = getStripRootDirectory(Object.keys(unzipped));

	await rm(targetDir, { recursive: true, force: true });
	await mkdir(targetDir, { recursive: true });

	for (const [rawPath, content] of Object.entries(unzipped)) {
		const path = getSafeZipEntryPath(rawPath, stripRoot);
		if (!path) continue;

		const fullPath = join(targetDir, path);
		if (!isPathSafe(targetDir, fullPath)) {
			throw new Error(`Invalid ZIP entry path: ${rawPath}`);
		}

		await mkdir(dirname(fullPath), { recursive: true });
		await writeFile(fullPath, Buffer.from(content as Uint8Array));
	}
}

/**
 * Get agent-specific skill path
 */
export function getAgentSkillPath(
	slug: string,
	agent: AgentConfig,
	options: { global?: boolean; cwd?: string } = {}
): string {
	const sanitized = sanitizeName(slug);
	const isGlobal = options.global ?? true; // Default to global for skillstore

	if (isGlobal) {
		return join(agent.globalPath, sanitized);
	} else {
		const cwd = options.cwd || process.cwd();
		return join(cwd, agent.projectPath, sanitized);
	}
}

/**
 * Creates a symlink, handling cross-platform differences
 * Returns true if symlink was created, false if fallback to copy is needed
 */
async function createSymlink(target: string, linkPath: string): Promise<boolean> {
	try {
		// Check if link already exists and points to correct target
		try {
			const stats = await lstat(linkPath);
			if (stats.isSymbolicLink()) {
				const existingTarget = await readlink(linkPath);
				if (resolve(existingTarget) === resolve(target)) {
					return true; // Already correct
				}
				await rm(linkPath);
			} else {
				await rm(linkPath, { recursive: true });
			}
		} catch (err: unknown) {
			// ELOOP = circular symlink, ENOENT = doesn't exist
			if (err && typeof err === 'object' && 'code' in err && err.code === 'ELOOP') {
				try {
					await rm(linkPath, { force: true });
				} catch {
					// If we can't remove it, symlink creation will fail
				}
			}
		}

		// Ensure parent directory exists
		const linkDir = join(linkPath, '..');
		await mkdir(linkDir, { recursive: true });

		// Create relative symlink
		const relativePath = relative(linkDir, target);
		const symlinkType = platform() === 'win32' ? 'junction' : undefined;

		await symlink(relativePath, linkPath, symlinkType);
		return true;
	} catch {
		return false;
	}
}

async function copySkillDirectory(target: string, linkPath: string): Promise<void> {
	const linkDir = join(linkPath, '..');
	await mkdir(linkDir, { recursive: true });
	await rm(linkPath, { recursive: true, force: true });
	await cp(target, linkPath, { recursive: true, force: true });
}

/**
 * Install skill to canonical location (for later symlinking)
 * This should be called AFTER extracting the ZIP to canonical path
 */
export async function ensureCanonicalDir(slug: string): Promise<string> {
	const canonicalPath = getCanonicalSkillPath(slug);

	if (!isPathSafe(CANONICAL_SKILLS_DIR, canonicalPath)) {
		throw new Error('Invalid skill name: potential path traversal detected');
	}

	await mkdir(canonicalPath, { recursive: true });
	return canonicalPath;
}

/**
 * Create symlink from agent skill directory to canonical location
 */
export async function symlinkToAgent(
	slug: string,
	agent: AgentConfig,
	options: { global?: boolean; cwd?: string } = {}
): Promise<InstallResult> {
	const canonicalPath = getCanonicalSkillPath(slug);
	const agentPath = getAgentSkillPath(slug, agent, options);

	// Validate paths
	const agentBase = options.global ?? true ? agent.globalPath : join(options.cwd || process.cwd(), agent.projectPath);

	if (!isPathSafe(agentBase, agentPath)) {
		return {
			success: false,
			agentId: agent.id as AgentId,
			path: agentPath,
			mode: 'symlink',
			error: 'Invalid skill name: potential path traversal detected',
		};
	}

	const result = await linkSkillToDirectory(slug, agentBase);
	return {
		...result,
		agentId: agent.id as AgentId,
	};
}

/**
 * Link a canonical skill directory into an arbitrary skills directory.
 */
export async function linkSkillToDirectory(
	slug: string,
	targetSkillsDir: string
): Promise<DirectoryInstallResult> {
	const canonicalPath = getCanonicalSkillPath(slug);
	const agentPath = join(targetSkillsDir, sanitizeName(slug));

	if (!isPathSafe(targetSkillsDir, agentPath)) {
		return {
			success: false,
			path: agentPath,
			mode: 'symlink',
			error: 'Invalid skill name: potential path traversal detected',
		};
	}

	try {
		if (resolve(canonicalPath) === resolve(agentPath)) {
			return {
				success: true,
				path: agentPath,
				canonicalPath,
				mode: 'symlink',
			};
		}

		const symlinkCreated = await createSymlink(canonicalPath, agentPath);

		if (!symlinkCreated) {
			await copySkillDirectory(canonicalPath, agentPath);
			return {
				success: true,
				path: agentPath,
				canonicalPath,
				mode: 'copy',
				symlinkFailed: true,
			};
		}

		return {
			success: true,
			path: agentPath,
			canonicalPath,
			mode: 'symlink',
		};
	} catch (error) {
		return {
			success: false,
			path: agentPath,
			mode: 'symlink',
			error: error instanceof Error ? error.message : 'Unknown error',
		};
	}
}

/**
 * Install skill to multiple agents
 * Assumes ZIP has already been extracted to canonical location
 */
export async function installToAgents(
	slug: string,
	agents: AgentConfig[],
	options: { global?: boolean; cwd?: string } = {}
): Promise<MultiAgentInstallResult> {
	const canonicalPath = getCanonicalSkillPath(slug);
	const results: InstallResult[] = [];

	for (const agent of agents) {
		const result = await symlinkToAgent(slug, agent, options);
		results.push(result);
	}

	const successCount = results.filter((r) => r.success).length;

	return {
		slug,
		canonicalPath,
		agents: results,
		success: successCount > 0,
		successCount,
		failCount: results.length - successCount,
	};
}

/**
 * Check if skill is installed for an agent
 */
export async function isSkillInstalledForAgent(
	slug: string,
	agent: AgentConfig,
	options: { global?: boolean; cwd?: string } = {}
): Promise<boolean> {
	const agentPath = getAgentSkillPath(slug, agent, options);

	try {
		await access(agentPath);
		return true;
	} catch {
		return false;
	}
}

/**
 * Check if skill exists in canonical location
 */
export async function isSkillInCanonical(slug: string): Promise<boolean> {
	const canonicalPath = getCanonicalSkillPath(slug);

	try {
		await access(canonicalPath);
		return true;
	} catch {
		return false;
	}
}

/**
 * Remove skill from canonical location and all agent symlinks
 */
export async function removeSkill(
	slug: string,
	agents: AgentConfig[],
	options: { global?: boolean; cwd?: string } = {}
): Promise<{ removed: AgentId[]; failed: AgentId[] }> {
	const removed: AgentId[] = [];
	const failed: AgentId[] = [];

	// Remove symlinks from agents
	for (const agent of agents) {
		const agentPath = getAgentSkillPath(slug, agent, options);
		try {
			await rm(agentPath, { recursive: true, force: true });
			removed.push(agent.id as AgentId);
		} catch {
			failed.push(agent.id as AgentId);
		}
	}

	// Remove canonical directory
	const canonicalPath = getCanonicalSkillPath(slug);
	try {
		await rm(canonicalPath, { recursive: true, force: true });
	} catch {
		// Ignore errors removing canonical
	}

	return { removed, failed };
}
