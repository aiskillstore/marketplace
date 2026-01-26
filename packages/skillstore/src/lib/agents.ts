import { homedir } from 'node:os';
import { join } from 'node:path';
import { existsSync } from 'node:fs';

/**
 * Agent Registry
 *
 * Defines supported AI coding agents and their skill installation paths.
 * Based on add-skill (skills.sh) agent definitions.
 */

/** Agent configuration */
export interface AgentConfig {
	/** Unique identifier (e.g., 'claude-code') */
	id: string;
	/** Display name (e.g., 'Claude Code') */
	name: string;
	/** Project-level skills directory (relative path) */
	projectPath: string;
	/** Global skills directory (absolute path) */
	globalPath: string;
	/** Check if this agent is installed */
	detectInstalled: () => boolean;
}

/** All supported agent IDs */
export type AgentId =
	| 'amp'
	| 'antigravity'
	| 'claude-code'
	| 'clawdbot'
	| 'cline'
	| 'codex'
	| 'command-code'
	| 'continue'
	| 'crush'
	| 'cursor'
	| 'droid'
	| 'gemini-cli'
	| 'github-copilot'
	| 'goose'
	| 'kilo'
	| 'kiro-cli'
	| 'mcpjam'
	| 'opencode'
	| 'openhands'
	| 'pi'
	| 'qoder'
	| 'qwen-code'
	| 'roo'
	| 'trae'
	| 'windsurf'
	| 'zencoder'
	| 'neovate';

const home = homedir();
const codexHome = process.env.CODEX_HOME?.trim() || join(home, '.codex');

/** Canonical skill storage location (shared across agents) */
export const CANONICAL_SKILLS_DIR = join(home, '.agents', 'skills');

/** Lock file location */
export const LOCK_FILE_PATH = join(home, '.agents', '.skill-lock.json');

/** All supported agents */
export const agents: Record<AgentId, AgentConfig> = {
	amp: {
		id: 'amp',
		name: 'Amp',
		projectPath: '.agents/skills',
		globalPath: join(home, '.config/agents/skills'),
		detectInstalled: () => existsSync(join(home, '.config/amp')),
	},
	antigravity: {
		id: 'antigravity',
		name: 'Antigravity',
		projectPath: '.agent/skills',
		globalPath: join(home, '.gemini/antigravity/global_skills'),
		detectInstalled: () =>
			existsSync(join(process.cwd(), '.agent')) ||
			existsSync(join(home, '.gemini/antigravity')),
	},
	'claude-code': {
		id: 'claude-code',
		name: 'Claude Code',
		projectPath: '.claude/skills',
		globalPath: join(home, '.claude/skills'),
		detectInstalled: () => existsSync(join(home, '.claude')),
	},
	clawdbot: {
		id: 'clawdbot',
		name: 'Clawdbot',
		projectPath: 'skills',
		globalPath: join(home, '.clawdbot/skills'),
		detectInstalled: () => existsSync(join(home, '.clawdbot')),
	},
	cline: {
		id: 'cline',
		name: 'Cline',
		projectPath: '.cline/skills',
		globalPath: join(home, '.cline/skills'),
		detectInstalled: () => existsSync(join(home, '.cline')),
	},
	codex: {
		id: 'codex',
		name: 'Codex',
		projectPath: '.codex/skills',
		globalPath: join(codexHome, 'skills'),
		detectInstalled: () => existsSync(codexHome) || existsSync('/etc/codex'),
	},
	'command-code': {
		id: 'command-code',
		name: 'Command Code',
		projectPath: '.commandcode/skills',
		globalPath: join(home, '.commandcode/skills'),
		detectInstalled: () => existsSync(join(home, '.commandcode')),
	},
	continue: {
		id: 'continue',
		name: 'Continue',
		projectPath: '.continue/skills',
		globalPath: join(home, '.continue/skills'),
		detectInstalled: () =>
			existsSync(join(process.cwd(), '.continue')) || existsSync(join(home, '.continue')),
	},
	crush: {
		id: 'crush',
		name: 'Crush',
		projectPath: '.crush/skills',
		globalPath: join(home, '.config/crush/skills'),
		detectInstalled: () => existsSync(join(home, '.config/crush')),
	},
	cursor: {
		id: 'cursor',
		name: 'Cursor',
		projectPath: '.cursor/skills',
		globalPath: join(home, '.cursor/skills'),
		detectInstalled: () => existsSync(join(home, '.cursor')),
	},
	droid: {
		id: 'droid',
		name: 'Droid',
		projectPath: '.factory/skills',
		globalPath: join(home, '.factory/skills'),
		detectInstalled: () => existsSync(join(home, '.factory')),
	},
	'gemini-cli': {
		id: 'gemini-cli',
		name: 'Gemini CLI',
		projectPath: '.gemini/skills',
		globalPath: join(home, '.gemini/skills'),
		detectInstalled: () => existsSync(join(home, '.gemini')),
	},
	'github-copilot': {
		id: 'github-copilot',
		name: 'GitHub Copilot',
		projectPath: '.github/skills',
		globalPath: join(home, '.copilot/skills'),
		detectInstalled: () =>
			existsSync(join(process.cwd(), '.github')) || existsSync(join(home, '.copilot')),
	},
	goose: {
		id: 'goose',
		name: 'Goose',
		projectPath: '.goose/skills',
		globalPath: join(home, '.config/goose/skills'),
		detectInstalled: () => existsSync(join(home, '.config/goose')),
	},
	kilo: {
		id: 'kilo',
		name: 'Kilo Code',
		projectPath: '.kilocode/skills',
		globalPath: join(home, '.kilocode/skills'),
		detectInstalled: () => existsSync(join(home, '.kilocode')),
	},
	'kiro-cli': {
		id: 'kiro-cli',
		name: 'Kiro CLI',
		projectPath: '.kiro/skills',
		globalPath: join(home, '.kiro/skills'),
		detectInstalled: () => existsSync(join(home, '.kiro')),
	},
	mcpjam: {
		id: 'mcpjam',
		name: 'MCPJam',
		projectPath: '.mcpjam/skills',
		globalPath: join(home, '.mcpjam/skills'),
		detectInstalled: () => existsSync(join(home, '.mcpjam')),
	},
	opencode: {
		id: 'opencode',
		name: 'OpenCode',
		projectPath: '.opencode/skills',
		globalPath: join(home, '.config/opencode/skills'),
		detectInstalled: () =>
			existsSync(join(home, '.config/opencode')) || existsSync(join(home, '.claude/skills')),
	},
	openhands: {
		id: 'openhands',
		name: 'OpenHands',
		projectPath: '.openhands/skills',
		globalPath: join(home, '.openhands/skills'),
		detectInstalled: () => existsSync(join(home, '.openhands')),
	},
	pi: {
		id: 'pi',
		name: 'Pi',
		projectPath: '.pi/skills',
		globalPath: join(home, '.pi/agent/skills'),
		detectInstalled: () => existsSync(join(home, '.pi/agent')),
	},
	qoder: {
		id: 'qoder',
		name: 'Qoder',
		projectPath: '.qoder/skills',
		globalPath: join(home, '.qoder/skills'),
		detectInstalled: () => existsSync(join(home, '.qoder')),
	},
	'qwen-code': {
		id: 'qwen-code',
		name: 'Qwen Code',
		projectPath: '.qwen/skills',
		globalPath: join(home, '.qwen/skills'),
		detectInstalled: () => existsSync(join(home, '.qwen')),
	},
	roo: {
		id: 'roo',
		name: 'Roo Code',
		projectPath: '.roo/skills',
		globalPath: join(home, '.roo/skills'),
		detectInstalled: () => existsSync(join(home, '.roo')),
	},
	trae: {
		id: 'trae',
		name: 'Trae',
		projectPath: '.trae/skills',
		globalPath: join(home, '.trae/skills'),
		detectInstalled: () => existsSync(join(home, '.trae')),
	},
	windsurf: {
		id: 'windsurf',
		name: 'Windsurf',
		projectPath: '.windsurf/skills',
		globalPath: join(home, '.codeium/windsurf/skills'),
		detectInstalled: () => existsSync(join(home, '.codeium/windsurf')),
	},
	zencoder: {
		id: 'zencoder',
		name: 'Zencoder',
		projectPath: '.zencoder/skills',
		globalPath: join(home, '.zencoder/skills'),
		detectInstalled: () => existsSync(join(home, '.zencoder')),
	},
	neovate: {
		id: 'neovate',
		name: 'Neovate',
		projectPath: '.neovate/skills',
		globalPath: join(home, '.neovate/skills'),
		detectInstalled: () => existsSync(join(home, '.neovate')),
	},
};

/** Get all agent IDs */
export function getAllAgentIds(): AgentId[] {
	return Object.keys(agents) as AgentId[];
}

/** Get agent config by ID */
export function getAgentById(id: AgentId): AgentConfig {
	return agents[id];
}

/** Detect which agents are installed on this system */
export function detectInstalledAgents(): AgentConfig[] {
	return Object.values(agents).filter((agent) => agent.detectInstalled());
}

/** Get agent configs by IDs */
export function getAgentsByIds(ids: AgentId[]): AgentConfig[] {
	return ids.map((id) => agents[id]).filter(Boolean);
}

/** Check if an agent ID is valid */
export function isValidAgentId(id: string): id is AgentId {
	return id in agents;
}
