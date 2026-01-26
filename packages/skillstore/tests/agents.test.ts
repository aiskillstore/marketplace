import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
	agents,
	getAllAgentIds,
	getAgentById,
	detectInstalledAgents,
	getAgentsByIds,
	isValidAgentId,
	CANONICAL_SKILLS_DIR,
	LOCK_FILE_PATH,
	type AgentId,
} from '../src/lib/agents.js';

// Mock fs.existsSync
vi.mock('node:fs', () => ({
	existsSync: vi.fn(() => false),
}));

import { existsSync } from 'node:fs';

describe('agents', () => {
	beforeEach(() => {
		vi.mocked(existsSync).mockReset();
	});

	describe('agent registry', () => {
		it('should have all expected agents', () => {
			const expectedAgents: AgentId[] = [
				'amp',
				'antigravity',
				'claude-code',
				'clawdbot',
				'cline',
				'codex',
				'command-code',
				'continue',
				'crush',
				'cursor',
				'droid',
				'gemini-cli',
				'github-copilot',
				'goose',
				'kilo',
				'kiro-cli',
				'mcpjam',
				'opencode',
				'openhands',
				'pi',
				'qoder',
				'qwen-code',
				'roo',
				'trae',
				'windsurf',
				'zencoder',
				'neovate',
			];

			expect(Object.keys(agents).sort()).toEqual(expectedAgents.sort());
		});

		it('should have required fields for each agent', () => {
			for (const [id, config] of Object.entries(agents)) {
				expect(config.id).toBe(id);
				expect(config.name).toBeTruthy();
				expect(config.projectPath).toBeTruthy();
				expect(config.globalPath).toBeTruthy();
				expect(typeof config.detectInstalled).toBe('function');
			}
		});

		it('should have claude-code agent configured correctly', () => {
			const claude = agents['claude-code'];

			expect(claude.id).toBe('claude-code');
			expect(claude.name).toBe('Claude Code');
			expect(claude.projectPath).toBe('.claude/skills');
			expect(claude.globalPath).toContain('.claude/skills');
		});
	});

	describe('getAllAgentIds', () => {
		it('should return all agent IDs', () => {
			const ids = getAllAgentIds();

			expect(ids).toContain('claude-code');
			expect(ids).toContain('cursor');
			expect(ids).toContain('windsurf');
			expect(ids.length).toBe(27);
		});
	});

	describe('getAgentById', () => {
		it('should return agent config by ID', () => {
			const agent = getAgentById('cursor');

			expect(agent.id).toBe('cursor');
			expect(agent.name).toBe('Cursor');
		});

		it('should return claude-code agent', () => {
			const agent = getAgentById('claude-code');

			expect(agent.id).toBe('claude-code');
			expect(agent.name).toBe('Claude Code');
		});
	});

	describe('detectInstalledAgents', () => {
		it('should return empty array when no agents installed', () => {
			vi.mocked(existsSync).mockReturnValue(false);

			const installed = detectInstalledAgents();

			expect(installed).toEqual([]);
		});

		it('should return claude-code when .claude exists', () => {
			vi.mocked(existsSync).mockImplementation((path) => {
				return String(path).includes('.claude');
			});

			const installed = detectInstalledAgents();

			expect(installed.map((a) => a.id)).toContain('claude-code');
		});

		it('should return multiple agents when multiple are installed', () => {
			vi.mocked(existsSync).mockImplementation((path) => {
				const p = String(path);
				return p.includes('.claude') || p.includes('.cursor');
			});

			const installed = detectInstalledAgents();

			expect(installed.length).toBeGreaterThanOrEqual(2);
			expect(installed.map((a) => a.id)).toContain('claude-code');
			expect(installed.map((a) => a.id)).toContain('cursor');
		});
	});

	describe('getAgentsByIds', () => {
		it('should return configs for given IDs', () => {
			const configs = getAgentsByIds(['claude-code', 'cursor']);

			expect(configs.length).toBe(2);
			expect(configs[0].id).toBe('claude-code');
			expect(configs[1].id).toBe('cursor');
		});

		it('should filter out invalid IDs', () => {
			const configs = getAgentsByIds(['claude-code', 'invalid-agent' as AgentId]);

			expect(configs.length).toBe(1);
			expect(configs[0].id).toBe('claude-code');
		});
	});

	describe('isValidAgentId', () => {
		it('should return true for valid agent IDs', () => {
			expect(isValidAgentId('claude-code')).toBe(true);
			expect(isValidAgentId('cursor')).toBe(true);
			expect(isValidAgentId('windsurf')).toBe(true);
		});

		it('should return false for invalid agent IDs', () => {
			expect(isValidAgentId('invalid')).toBe(false);
			expect(isValidAgentId('')).toBe(false);
			expect(isValidAgentId('CLAUDE-CODE')).toBe(false);
		});
	});

	describe('constants', () => {
		it('should have canonical skills dir in home', () => {
			expect(CANONICAL_SKILLS_DIR).toContain('.agents');
			expect(CANONICAL_SKILLS_DIR).toContain('skills');
		});

		it('should have lock file path in .agents', () => {
			expect(LOCK_FILE_PATH).toContain('.agents');
			expect(LOCK_FILE_PATH).toContain('.skill-lock.json');
		});
	});
});
