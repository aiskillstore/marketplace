import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
	readSkillLock,
	writeSkillLock,
	addToLock,
	removeFromLock,
	getLockEntry,
	getAllLockedSkills,
	isSkillLocked,
	getLockedSkillCount,
	LOCK_VERSION,
	type SkillLock,
	type SkillLockEntry,
} from '../src/lib/skill-lock.js';

// Mock fs/promises
vi.mock('node:fs/promises', () => ({
	readFile: vi.fn(),
	writeFile: vi.fn(),
	mkdir: vi.fn(),
}));

// Mock agents.js for LOCK_FILE_PATH
vi.mock('../src/lib/agents.js', () => ({
	LOCK_FILE_PATH: '/mock/home/.agents/.skill-lock.json',
}));

import { readFile, writeFile, mkdir } from 'node:fs/promises';

describe('skill-lock', () => {
	beforeEach(() => {
		vi.mocked(readFile).mockReset();
		vi.mocked(writeFile).mockReset();
		vi.mocked(mkdir).mockReset();
		vi.mocked(mkdir).mockResolvedValue(undefined);
		vi.mocked(writeFile).mockResolvedValue(undefined);
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	const mockLockEntry: SkillLockEntry = {
		slug: 'test-skill',
		version: '1.0.0',
		zipHash: 'abc123def456',
		source: 'skillstore',
		installedAt: '2024-01-01T00:00:00Z',
		updatedAt: '2024-01-01T00:00:00Z',
	};

	const mockLock: SkillLock = {
		version: LOCK_VERSION,
		skills: {
			'test-skill': mockLockEntry,
		},
	};

	describe('LOCK_VERSION', () => {
		it('should be 1', () => {
			expect(LOCK_VERSION).toBe(1);
		});
	});

	describe('readSkillLock', () => {
		it('should return empty lock when file does not exist', async () => {
			vi.mocked(readFile).mockRejectedValue(new Error('ENOENT'));

			const lock = await readSkillLock();

			expect(lock.version).toBe(LOCK_VERSION);
			expect(lock.skills).toEqual({});
		});

		it('should return empty lock for invalid JSON', async () => {
			vi.mocked(readFile).mockResolvedValue('not valid json');

			const lock = await readSkillLock();

			expect(lock.version).toBe(LOCK_VERSION);
			expect(lock.skills).toEqual({});
		});

		it('should return empty lock for old version', async () => {
			const oldLock = { version: 0, skills: { test: mockLockEntry } };
			vi.mocked(readFile).mockResolvedValue(JSON.stringify(oldLock));

			const lock = await readSkillLock();

			expect(lock.version).toBe(LOCK_VERSION);
			expect(lock.skills).toEqual({});
		});

		it('should return parsed lock for valid file', async () => {
			vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockLock));

			const lock = await readSkillLock();

			expect(lock.version).toBe(LOCK_VERSION);
			expect(lock.skills['test-skill']).toEqual(mockLockEntry);
		});
	});

	describe('writeSkillLock', () => {
		it('should create directory and write file', async () => {
			await writeSkillLock(mockLock);

			expect(mkdir).toHaveBeenCalledWith('/mock/home/.agents', { recursive: true });
			expect(writeFile).toHaveBeenCalledWith(
				'/mock/home/.agents/.skill-lock.json',
				expect.any(String),
				'utf-8'
			);
		});

		it('should write pretty-formatted JSON', async () => {
			await writeSkillLock(mockLock);

			const writtenContent = vi.mocked(writeFile).mock.calls[0][1] as string;
			const parsed = JSON.parse(writtenContent);

			expect(parsed).toEqual(mockLock);
			expect(writtenContent).toContain('\n'); // Pretty formatted
		});
	});

	describe('addToLock', () => {
		it('should add new skill to lock', async () => {
			vi.mocked(readFile).mockResolvedValue(JSON.stringify({ version: LOCK_VERSION, skills: {} }));

			const entry = {
				slug: 'new-skill',
				version: '1.0.0',
				zipHash: 'hash123',
				source: 'skillstore' as const,
				installedAt: '2024-01-01T00:00:00Z',
			};

			await addToLock(entry);

			const writtenContent = vi.mocked(writeFile).mock.calls[0][1] as string;
			const parsed = JSON.parse(writtenContent);

			expect(parsed.skills['new-skill']).toBeDefined();
			expect(parsed.skills['new-skill'].slug).toBe('new-skill');
			expect(parsed.skills['new-skill'].updatedAt).toBeDefined();
		});

		it('should update existing skill and preserve installedAt', async () => {
			vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockLock));

			const entry = {
				slug: 'test-skill',
				version: '2.0.0',
				zipHash: 'newhash',
				source: 'skillstore' as const,
				installedAt: '2024-06-01T00:00:00Z', // Different date
			};

			await addToLock(entry);

			const writtenContent = vi.mocked(writeFile).mock.calls[0][1] as string;
			const parsed = JSON.parse(writtenContent);

			expect(parsed.skills['test-skill'].version).toBe('2.0.0');
			expect(parsed.skills['test-skill'].installedAt).toBe('2024-01-01T00:00:00Z'); // Original preserved
		});
	});

	describe('removeFromLock', () => {
		it('should remove skill from lock', async () => {
			vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockLock));

			const result = await removeFromLock('test-skill');

			expect(result).toBe(true);
			const writtenContent = vi.mocked(writeFile).mock.calls[0][1] as string;
			const parsed = JSON.parse(writtenContent);
			expect(parsed.skills['test-skill']).toBeUndefined();
		});

		it('should return false for non-existent skill', async () => {
			vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockLock));

			const result = await removeFromLock('non-existent');

			expect(result).toBe(false);
		});
	});

	describe('getLockEntry', () => {
		it('should return entry for existing skill', async () => {
			vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockLock));

			const entry = await getLockEntry('test-skill');

			expect(entry).toEqual(mockLockEntry);
		});

		it('should return undefined for non-existent skill', async () => {
			vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockLock));

			const entry = await getLockEntry('non-existent');

			expect(entry).toBeUndefined();
		});
	});

	describe('getAllLockedSkills', () => {
		it('should return all locked skills', async () => {
			const lockWithMultiple: SkillLock = {
				version: LOCK_VERSION,
				skills: {
					'skill-1': { ...mockLockEntry, slug: 'skill-1' },
					'skill-2': { ...mockLockEntry, slug: 'skill-2' },
				},
			};
			vi.mocked(readFile).mockResolvedValue(JSON.stringify(lockWithMultiple));

			const skills = await getAllLockedSkills();

			expect(skills.length).toBe(2);
			expect(skills.map((s) => s.slug).sort()).toEqual(['skill-1', 'skill-2']);
		});

		it('should return empty array when no skills', async () => {
			vi.mocked(readFile).mockResolvedValue(JSON.stringify({ version: LOCK_VERSION, skills: {} }));

			const skills = await getAllLockedSkills();

			expect(skills).toEqual([]);
		});
	});

	describe('isSkillLocked', () => {
		it('should return true for locked skill', async () => {
			vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockLock));

			const result = await isSkillLocked('test-skill');

			expect(result).toBe(true);
		});

		it('should return false for non-locked skill', async () => {
			vi.mocked(readFile).mockResolvedValue(JSON.stringify(mockLock));

			const result = await isSkillLocked('non-existent');

			expect(result).toBe(false);
		});
	});

	describe('getLockedSkillCount', () => {
		it('should return count of locked skills', async () => {
			const lockWithMultiple: SkillLock = {
				version: LOCK_VERSION,
				skills: {
					'skill-1': { ...mockLockEntry, slug: 'skill-1' },
					'skill-2': { ...mockLockEntry, slug: 'skill-2' },
					'skill-3': { ...mockLockEntry, slug: 'skill-3' },
				},
			};
			vi.mocked(readFile).mockResolvedValue(JSON.stringify(lockWithMultiple));

			const count = await getLockedSkillCount();

			expect(count).toBe(3);
		});

		it('should return 0 for empty lock', async () => {
			vi.mocked(readFile).mockResolvedValue(JSON.stringify({ version: LOCK_VERSION, skills: {} }));

			const count = await getLockedSkillCount();

			expect(count).toBe(0);
		});
	});
});
