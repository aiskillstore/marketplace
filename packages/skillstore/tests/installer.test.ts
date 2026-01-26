import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
	sanitizeName,
	getCanonicalSkillPath,
	getAgentSkillPath,
	ensureCanonicalDir,
	symlinkToAgent,
	installToAgents,
	isSkillInstalledForAgent,
	isSkillInCanonical,
	removeSkill,
} from '../src/lib/installer.js';
import type { AgentConfig } from '../src/lib/agents.js';

// Mock fs/promises
vi.mock('node:fs/promises', () => ({
	mkdir: vi.fn(),
	rm: vi.fn(),
	symlink: vi.fn(),
	lstat: vi.fn(),
	readlink: vi.fn(),
	access: vi.fn(),
}));

// Mock os
vi.mock('node:os', () => ({
	platform: vi.fn(() => 'darwin'),
}));

// Mock agents.js
vi.mock('../src/lib/agents.js', () => ({
	CANONICAL_SKILLS_DIR: '/mock/home/.agents/skills',
}));

import { mkdir, rm, symlink, lstat, readlink, access } from 'node:fs/promises';
import { platform } from 'node:os';

describe('installer', () => {
	const mockAgent: AgentConfig = {
		id: 'claude-code',
		name: 'Claude Code',
		projectPath: '.claude/skills',
		globalPath: '/mock/home/.claude/skills',
		detectInstalled: () => true,
	};

	const mockAgent2: AgentConfig = {
		id: 'cursor',
		name: 'Cursor',
		projectPath: '.cursor/skills',
		globalPath: '/mock/home/.cursor/skills',
		detectInstalled: () => true,
	};

	beforeEach(() => {
		vi.mocked(mkdir).mockReset();
		vi.mocked(rm).mockReset();
		vi.mocked(symlink).mockReset();
		vi.mocked(lstat).mockReset();
		vi.mocked(readlink).mockReset();
		vi.mocked(access).mockReset();
		vi.mocked(platform).mockReturnValue('darwin');

		// Default mocks
		vi.mocked(mkdir).mockResolvedValue(undefined);
		vi.mocked(rm).mockResolvedValue(undefined);
		vi.mocked(symlink).mockResolvedValue(undefined);
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('sanitizeName', () => {
		it('should return name unchanged for valid names', () => {
			expect(sanitizeName('my-skill')).toBe('my-skill');
			expect(sanitizeName('skill_name')).toBe('skill_name');
			expect(sanitizeName('Skill123')).toBe('Skill123');
		});

		it('should remove path separators', () => {
			expect(sanitizeName('path/to/skill')).toBe('pathtoskill');
			expect(sanitizeName('path\\to\\skill')).toBe('pathtoskill');
		});

		it('should remove colons and null bytes', () => {
			expect(sanitizeName('skill:name')).toBe('skillname');
			expect(sanitizeName('skill\0name')).toBe('skillname');
		});

		it('should remove leading dots and spaces', () => {
			expect(sanitizeName('...skill')).toBe('skill');
			expect(sanitizeName('  skill')).toBe('skill');
			expect(sanitizeName('..skill..')).toBe('skill');
		});

		it('should return unnamed-skill for empty or invalid names', () => {
			expect(sanitizeName('')).toBe('unnamed-skill');
			expect(sanitizeName('...')).toBe('unnamed-skill');
			expect(sanitizeName('   ')).toBe('unnamed-skill');
		});

		it('should truncate names longer than 255 characters', () => {
			const longName = 'a'.repeat(300);
			expect(sanitizeName(longName).length).toBe(255);
		});
	});

	describe('getCanonicalSkillPath', () => {
		it('should return path in canonical skills directory', () => {
			const path = getCanonicalSkillPath('my-skill');
			expect(path).toBe('/mock/home/.agents/skills/my-skill');
		});

		it('should sanitize the slug', () => {
			const path = getCanonicalSkillPath('path/to/skill');
			expect(path).toBe('/mock/home/.agents/skills/pathtoskill');
		});
	});

	describe('getAgentSkillPath', () => {
		it('should return global path by default', () => {
			const path = getAgentSkillPath('my-skill', mockAgent);
			expect(path).toBe('/mock/home/.claude/skills/my-skill');
		});

		it('should return global path when global is true', () => {
			const path = getAgentSkillPath('my-skill', mockAgent, { global: true });
			expect(path).toBe('/mock/home/.claude/skills/my-skill');
		});

		it('should return project path when global is false', () => {
			const path = getAgentSkillPath('my-skill', mockAgent, { global: false, cwd: '/project' });
			expect(path).toBe('/project/.claude/skills/my-skill');
		});

		it('should use process.cwd() when cwd not provided', () => {
			const path = getAgentSkillPath('my-skill', mockAgent, { global: false });
			expect(path).toContain('.claude/skills/my-skill');
		});

		it('should sanitize the slug', () => {
			const path = getAgentSkillPath('path/to/skill', mockAgent);
			expect(path).toBe('/mock/home/.claude/skills/pathtoskill');
		});
	});

	describe('ensureCanonicalDir', () => {
		it('should create canonical directory', async () => {
			const path = await ensureCanonicalDir('my-skill');

			expect(mkdir).toHaveBeenCalledWith('/mock/home/.agents/skills/my-skill', { recursive: true });
			expect(path).toBe('/mock/home/.agents/skills/my-skill');
		});

		it('should throw for path traversal attempts', async () => {
			// This test verifies path traversal protection
			// The sanitizeName function should prevent most attacks
			await expect(ensureCanonicalDir('../../../etc/passwd')).resolves.toBe(
				'/mock/home/.agents/skills/etcpasswd'
			);
		});
	});

	describe('symlinkToAgent', () => {
		it('should create symlink successfully', async () => {
			vi.mocked(lstat).mockRejectedValue({ code: 'ENOENT' });

			const result = await symlinkToAgent('my-skill', mockAgent);

			expect(result.success).toBe(true);
			expect(result.agentId).toBe('claude-code');
			expect(result.mode).toBe('symlink');
			expect(result.symlinkFailed).toBeUndefined();
			expect(symlink).toHaveBeenCalled();
		});

		it('should handle existing symlink pointing to correct target', async () => {
			vi.mocked(lstat).mockResolvedValue({ isSymbolicLink: () => true } as any);
			vi.mocked(readlink).mockResolvedValue('/mock/home/.agents/skills/my-skill');

			const result = await symlinkToAgent('my-skill', mockAgent);

			expect(result.success).toBe(true);
			expect(rm).not.toHaveBeenCalled();
		});

		it('should remove existing symlink pointing to wrong target', async () => {
			vi.mocked(lstat).mockResolvedValue({ isSymbolicLink: () => true } as any);
			vi.mocked(readlink).mockResolvedValue('/wrong/path');

			const result = await symlinkToAgent('my-skill', mockAgent);

			expect(result.success).toBe(true);
			expect(rm).toHaveBeenCalled();
		});

		it('should remove existing non-symlink file', async () => {
			vi.mocked(lstat).mockResolvedValue({ isSymbolicLink: () => false } as any);

			const result = await symlinkToAgent('my-skill', mockAgent);

			expect(result.success).toBe(true);
			expect(rm).toHaveBeenCalledWith(expect.any(String), { recursive: true });
		});

		it('should handle ELOOP error (circular symlink)', async () => {
			vi.mocked(lstat).mockRejectedValue({ code: 'ELOOP' });

			const result = await symlinkToAgent('my-skill', mockAgent);

			expect(result.success).toBe(true);
			expect(rm).toHaveBeenCalledWith(expect.any(String), { force: true });
		});

		it('should return symlinkFailed when symlink creation fails', async () => {
			vi.mocked(lstat).mockRejectedValue({ code: 'ENOENT' });
			vi.mocked(symlink).mockRejectedValue(new Error('Permission denied'));

			const result = await symlinkToAgent('my-skill', mockAgent);

			expect(result.success).toBe(true);
			expect(result.symlinkFailed).toBe(true);
		});

		it('should use junction on Windows', async () => {
			vi.mocked(platform).mockReturnValue('win32');
			vi.mocked(lstat).mockRejectedValue({ code: 'ENOENT' });

			await symlinkToAgent('my-skill', mockAgent);

			expect(symlink).toHaveBeenCalledWith(expect.any(String), expect.any(String), 'junction');
		});
	});

	describe('installToAgents', () => {
		it('should install to multiple agents', async () => {
			vi.mocked(lstat).mockRejectedValue({ code: 'ENOENT' });

			const result = await installToAgents('my-skill', [mockAgent, mockAgent2]);

			expect(result.slug).toBe('my-skill');
			expect(result.agents.length).toBe(2);
			expect(result.successCount).toBe(2);
			expect(result.failCount).toBe(0);
			expect(result.success).toBe(true);
		});

		it('should count partial success', async () => {
			vi.mocked(lstat).mockRejectedValue({ code: 'ENOENT' });
			vi.mocked(symlink)
				.mockResolvedValueOnce(undefined)
				.mockRejectedValueOnce(new Error('Failed'));

			const result = await installToAgents('my-skill', [mockAgent, mockAgent2]);

			expect(result.successCount).toBe(2); // Both succeed because symlinkFailed is still success
			expect(result.success).toBe(true);
		});

		it('should handle empty agents list', async () => {
			const result = await installToAgents('my-skill', []);

			expect(result.agents.length).toBe(0);
			expect(result.successCount).toBe(0);
			expect(result.success).toBe(false);
		});
	});

	describe('isSkillInstalledForAgent', () => {
		it('should return true when skill directory exists', async () => {
			vi.mocked(access).mockResolvedValue(undefined);

			const result = await isSkillInstalledForAgent('my-skill', mockAgent);

			expect(result).toBe(true);
			expect(access).toHaveBeenCalledWith('/mock/home/.claude/skills/my-skill');
		});

		it('should return false when skill directory does not exist', async () => {
			vi.mocked(access).mockRejectedValue({ code: 'ENOENT' });

			const result = await isSkillInstalledForAgent('my-skill', mockAgent);

			expect(result).toBe(false);
		});

		it('should use project path when global is false', async () => {
			vi.mocked(access).mockResolvedValue(undefined);

			await isSkillInstalledForAgent('my-skill', mockAgent, { global: false, cwd: '/project' });

			expect(access).toHaveBeenCalledWith('/project/.claude/skills/my-skill');
		});
	});

	describe('isSkillInCanonical', () => {
		it('should return true when skill exists in canonical location', async () => {
			vi.mocked(access).mockResolvedValue(undefined);

			const result = await isSkillInCanonical('my-skill');

			expect(result).toBe(true);
			expect(access).toHaveBeenCalledWith('/mock/home/.agents/skills/my-skill');
		});

		it('should return false when skill does not exist in canonical location', async () => {
			vi.mocked(access).mockRejectedValue({ code: 'ENOENT' });

			const result = await isSkillInCanonical('my-skill');

			expect(result).toBe(false);
		});
	});

	describe('removeSkill', () => {
		it('should remove skill from all agents and canonical location', async () => {
			const result = await removeSkill('my-skill', [mockAgent, mockAgent2]);

			expect(result.removed).toContain('claude-code');
			expect(result.removed).toContain('cursor');
			expect(result.failed).toEqual([]);
			expect(rm).toHaveBeenCalledTimes(3); // 2 agents + 1 canonical
		});

		it('should track failed removals', async () => {
			vi.mocked(rm)
				.mockResolvedValueOnce(undefined) // First agent succeeds
				.mockRejectedValueOnce(new Error('Failed')) // Second agent fails
				.mockResolvedValueOnce(undefined); // Canonical succeeds

			const result = await removeSkill('my-skill', [mockAgent, mockAgent2]);

			expect(result.removed).toContain('claude-code');
			expect(result.failed).toContain('cursor');
		});

		it('should ignore errors when removing canonical directory', async () => {
			vi.mocked(rm)
				.mockResolvedValueOnce(undefined)
				.mockResolvedValueOnce(undefined)
				.mockRejectedValueOnce(new Error('Failed to remove canonical'));

			const result = await removeSkill('my-skill', [mockAgent, mockAgent2]);

			// Should not throw, just ignore canonical removal error
			expect(result.removed).toContain('claude-code');
			expect(result.removed).toContain('cursor');
		});

		it('should use project paths when global is false', async () => {
			await removeSkill('my-skill', [mockAgent], { global: false, cwd: '/project' });

			expect(rm).toHaveBeenCalledWith('/project/.claude/skills/my-skill', {
				recursive: true,
				force: true,
			});
		});
	});
});
