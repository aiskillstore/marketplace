import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { LOCK_FILE_PATH } from './agents.js';

/**
 * Skill Lock File Management
 *
 * Tracks installed skills with version and hash information
 * for update detection and management.
 */

/** Lock file version - increment when schema changes */
export const LOCK_VERSION = 1;

/** Entry for a single installed skill */
export interface SkillLockEntry {
	/** Skill slug */
	slug: string;
	/** Skill version */
	version: string;
	/** ZIP file SHA256 hash */
	zipHash: string;
	/** Source (always 'skillstore' for now) */
	source: 'skillstore';
	/** ISO timestamp when installed */
	installedAt: string;
	/** ISO timestamp when last updated */
	updatedAt: string;
}

/** Lock file structure */
export interface SkillLock {
	/** Lock file version */
	version: number;
	/** Map of slug to lock entry */
	skills: Record<string, SkillLockEntry>;
}

/** Create empty lock file */
function createEmptyLock(): SkillLock {
	return {
		version: LOCK_VERSION,
		skills: {},
	};
}

/**
 * Read skill lock file
 * Returns empty lock if file doesn't exist or is invalid
 */
export async function readSkillLock(): Promise<SkillLock> {
	try {
		const content = await readFile(LOCK_FILE_PATH, 'utf-8');
		const lock = JSON.parse(content) as SkillLock;

		// Check version - wipe if outdated
		if (lock.version !== LOCK_VERSION) {
			return createEmptyLock();
		}

		return lock;
	} catch {
		// File doesn't exist or invalid JSON
		return createEmptyLock();
	}
}

/**
 * Write skill lock file
 */
export async function writeSkillLock(lock: SkillLock): Promise<void> {
	// Ensure directory exists
	await mkdir(dirname(LOCK_FILE_PATH), { recursive: true });

	// Write with pretty formatting
	await writeFile(LOCK_FILE_PATH, JSON.stringify(lock, null, 2), 'utf-8');
}

/**
 * Add or update a skill in the lock file
 */
export async function addToLock(entry: Omit<SkillLockEntry, 'updatedAt'>): Promise<void> {
	const lock = await readSkillLock();
	const now = new Date().toISOString();

	const existing = lock.skills[entry.slug];

	lock.skills[entry.slug] = {
		...entry,
		installedAt: existing?.installedAt || entry.installedAt,
		updatedAt: now,
	};

	await writeSkillLock(lock);
}

/**
 * Remove a skill from the lock file
 */
export async function removeFromLock(slug: string): Promise<boolean> {
	const lock = await readSkillLock();

	if (!(slug in lock.skills)) {
		return false;
	}

	delete lock.skills[slug];
	await writeSkillLock(lock);
	return true;
}

/**
 * Get a single lock entry
 */
export async function getLockEntry(slug: string): Promise<SkillLockEntry | undefined> {
	const lock = await readSkillLock();
	return lock.skills[slug];
}

/**
 * Get all locked skills
 */
export async function getAllLockedSkills(): Promise<SkillLockEntry[]> {
	const lock = await readSkillLock();
	return Object.values(lock.skills);
}

/**
 * Check if a skill is in the lock file
 */
export async function isSkillLocked(slug: string): Promise<boolean> {
	const lock = await readSkillLock();
	return slug in lock.skills;
}

/**
 * Get count of locked skills
 */
export async function getLockedSkillCount(): Promise<number> {
	const lock = await readSkillLock();
	return Object.keys(lock.skills).length;
}
