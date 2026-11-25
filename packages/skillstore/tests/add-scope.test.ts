import { createHash, createHmac } from 'node:crypto';
import { cp, lstat, mkdir, mkdtemp, readFile, readdir, readlink, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { zipSync } from 'fflate';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const state = vi.hoisted(() => ({ root: '', skill: {} as any, pack: {} as any, zip: new Uint8Array(), download: vi.fn(), errors: [] as unknown[][] }));
vi.mock('../src/lib/agents.js', async (original) => {
	const actual = await original<typeof import('../src/lib/agents.js')>();
	const agents = Object.fromEntries(Object.entries(actual.agents).map(([id, agent]) => [id, {
		...agent, globalPath: join(state.root, 'home', agent.projectPath),
	}]));
	return {
		...actual, agents,
		getAgentsByIds: (ids: string[]) => ids.map((id) => agents[id]),
		CANONICAL_SKILLS_DIR: join(state.root, 'home/.agents/skills'),
		LOCK_FILE_PATH: join(state.root, 'home/.agents/.skill-lock.json'),
	};
});
vi.mock('../src/lib/skill-api.js', async (original) => ({
	...await original<typeof import('../src/lib/skill-api.js')>(),
	fetchSkillManifest: async () => state.skill,
	downloadSkillZip: async () => { state.download(); return state.zip; },
}));
vi.mock('../src/lib/plugin-api.js', async (original) => ({
	...await original<typeof import('../src/lib/plugin-api.js')>(),
	fetchManifest: async () => state.pack,
	downloadSkillFile: async () => new TextEncoder().encode(content),
	reportSkillInstall: vi.fn(), reportPackInstallation: vi.fn(),
}));
vi.mock('../src/lib/plugin-logger.js', () => ({ logger: new Proxy({}, { get: (_target, name) => (...args: unknown[]) => { if (name === 'error') state.errors.push(args); } }) }));

const content = '---\nname: sample\ndescription: Local test fixture\n---\nUse local test data.\n';
const key = 'local-fixture-key';
const hash = (value: string | Uint8Array) => createHash('sha256').update(value).digest('hex');
function canonical(value: any): string {
	if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
	if (value && typeof value === 'object') return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
	return JSON.stringify(value);
}
function signed(value: any) {
	return { ...value, signature: createHmac('sha256', key).update(JSON.stringify(value)).digest('hex') };
}

let project: string;
let command: typeof import('../src/commands/add.js')['default'];
async function run(target = 'owner-sample', global = false, agent = 'codex,claude-code', dryRun = false) {
	return command.run!({ args: { target, global, agent, 'skip-verify': false, 'dry-run': dryRun, overwrite: false } } as any);
}

beforeEach(async () => {
	vi.resetModules();
	state.root = await mkdtemp(join(tmpdir(), 'skillstore-add-scope-'));
	project = join(state.root, 'project');
	await mkdir(project);
	vi.spyOn(process, 'cwd').mockImplementation(() => project);
	vi.spyOn(process, 'exit').mockImplementation((code) => { throw new Error(`exit ${code}: ${state.errors.map((args) => args.map(String).join(' ')).join('; ')}`); });
	vi.spyOn(console, 'log').mockImplementation(() => {});
	vi.stubEnv('SKILLSTORE_VERIFY_KEY', key);
	vi.stubEnv('SKILLSTORE_TELEMETRY_DISABLED', '1');
	state.download.mockClear(); state.errors = [];
	state.zip = zipSync({ 'SKILL.md': new TextEncoder().encode(content) });
	const identity = { version: '1.0.0', authorVersion: '1.0.0', skillstoreRevision: 1, versionStatus: 'valid', treeHash: hash(JSON.stringify({ path: 'SKILL.md', mode: '100644', sha256: hash(content), size: Buffer.byteLength(content) })) };
	state.skill = signed({ version: '1.0', skill: { slug: 'owner-sample', name: 'Sample', ...identity, zipHash: hash(state.zip) }, generatedAt: '2026-11-25T00:00:00Z' });
	const binding = { canonicalId: 'owner-sample', contentHash: hash(content), treeHash: identity.treeHash, version: identity.version, slotIds: ['create'] };
	const nodes = [{ id: 'create', instruction: 'Create the local result.', dependsOn: [], artifactIds: ['result'] }];
	const workflowDigest = hash(canonical({ schema_version: 'skillstore.pack-execution-dag/v1', nodes: [{ id: 'create', instruction: nodes[0].instruction, depends_on: [], artifact_ids: ['result'] }], handoffs: [] }));
	const bindingDigest = hash(canonical({ workflow_digest: workflowDigest, skill_bindings: [{ canonical_id: binding.canonicalId, content_hash: binding.contentHash, tree_hash: binding.treeHash, version: binding.version, slot_ids: binding.slotIds }] }));
	const usageGuideMarker = `<!-- skillstore-execution-binding:${bindingDigest} -->`;
	state.pack = signed({
		version: '1.0', plugin: { slug: 'sample-pack', name: 'Sample Pack', version: '1.0.0' },
		skills: [{ slug: 'owner-sample', name: 'Sample', ...identity, contentHash: hash(content), downloadUrl: '/sample', artifact: { files: [{ path: 'SKILL.md', url: '/sample', sha256: hash(content), bytes: Buffer.byteLength(content), mode: '100644' }] } }],
		executionBinding: {
			schemaVersion: 'skillstore.pack-execution-binding/v1', generationId: 'fixture', evidenceDigest: 'b'.repeat(64),
			workflowDigest, bindingDigest, usageGuideMarker, marketplaceCommitSha: 'c'.repeat(40), skills: [binding],
			executionDag: { schemaVersion: 'skillstore.pack-execution-dag/v1', workflowDigest, bindingDigest, usageGuideMarker, nodes, handoffs: [], skillBindings: [binding] },
		}, generatedAt: '2026-11-25T00:00:00Z',
	});
	command = (await import('../src/commands/add.js')).default;
});

afterEach(async () => {
	vi.restoreAllMocks(); vi.unstubAllEnvs();
	await rm(state.root, { recursive: true, force: true });
});

describe('add installation scope with verified manifests and real files', () => {
	it('keeps a global installation and two project installations independent', async () => {
		await run('owner-sample', true);
		const globalLock = await readFile(join(state.root, 'home/.agents/.skill-lock.json'), 'utf8');
		await run();
		const first = project;
		project = join(state.root, 'second'); await mkdir(project);
		await run();
		for (const root of [first, project]) {
			const canonicalPath = join(root, '.agents/skills/owner-sample');
			expect(await readFile(join(canonicalPath, 'SKILL.md'), 'utf8')).toBe(content);
			expect((await lstat(canonicalPath)).isSymbolicLink()).toBe(false);
			const link = join(root, '.claude/skills/owner-sample');
			expect(resolve(join(root, '.claude/skills'), await readlink(link))).toBe(canonicalPath);
			expect(JSON.parse(await readFile(join(root, '.agents/.skill-lock.json'), 'utf8')).skills['owner-sample']).toBeDefined();
		}
		expect(await readFile(join(state.root, 'home/.agents/.skill-lock.json'), 'utf8')).toBe(globalLock);
		expect(state.download).toHaveBeenCalledTimes(3);
	});
	it('adds a missing agent link without downloading the installed skill again', async () => {
		await run('owner-sample', false, 'codex');
		await run('owner-sample', false, 'claude-code');
		expect(await readFile(join(project, '.claude/skills/owner-sample/SKILL.md'), 'utf8')).toBe(content);
		expect(state.download).toHaveBeenCalledTimes(1);
	});
	it('keeps an unchanged copy fallback on repeated installation and rejects changed copies', async () => {
		await run('owner-sample', false, 'codex');
		const target = join(project, '.claude/skills/owner-sample');
		await cp(join(project, '.agents/skills/owner-sample'), target, { recursive: true });
		await run('owner-sample', false, 'claude-code');
		expect((await lstat(target)).isDirectory()).toBe(true);
		expect(state.download).toHaveBeenCalledTimes(1);
		await writeFile(join(target, 'extra.txt'), 'keep');
		await expect(run('owner-sample', false, 'claude-code')).rejects.toThrow('Preserve the existing project skill path');
		expect(await readFile(join(target, 'extra.txt'), 'utf8')).toBe('keep');
	});
	it('does not replace an unrelated agent directory while repairing links', async () => {
		await run('owner-sample', false, 'codex');
		const target = join(project, '.claude/skills/owner-sample');
		await mkdir(target, { recursive: true });
		await writeFile(join(target, 'SKILL.md'), 'keep custom skill');
		await expect(run('owner-sample', false, 'claude-code')).rejects.toThrow('Preserve the existing project skill path');
		expect(await readFile(join(target, 'SKILL.md'), 'utf8')).toBe('keep custom skill');
	});
	it.each(['.agents/skills', '.claude/skills'])('preserves an untracked %s directory on first install', async (directory) => {
		const target = join(project, directory, 'owner-sample');
		await mkdir(target, { recursive: true });
		await writeFile(join(target, 'keep.txt'), 'unrelated user content');
		await expect(run('owner-sample', false, 'claude-code')).rejects.toThrow('Preserve the existing project skill path');
		expect(await readFile(join(target, 'keep.txt'), 'utf8')).toBe('unrelated user content');
		expect(state.download).not.toHaveBeenCalled();
		await expect(lstat(join(project, '.agents/.skill-lock.json'))).rejects.toMatchObject({ code: 'ENOENT' });
	});
	it('previews the selected scope and actual targets without writing', async () => {
		await run('owner-sample', false, 'codex,claude-code', true);
		expect(console.log).toHaveBeenCalledWith('Scope: project-level');
		expect(console.log).toHaveBeenCalledWith(`Would install to: ${join(project, '.agents/skills/owner-sample')}`);
		expect(console.log).toHaveBeenCalledWith(`Canonical target: Codex -> ${join(project, '.agents/skills/owner-sample')}`);
		await run('owner-sample', true, 'claude-code', true);
		expect(console.log).toHaveBeenCalledWith('Scope: user-level');
		expect(await readdir(project)).toEqual([]);
		expect(state.download).not.toHaveBeenCalled();
		expect(command.args!.global.description).toContain('--no-global for project-level');
	});
	it('installs and reads back Pack members, lock and signed workflow in the project', async () => {
		await run('@sample-pack');
		expect(await readFile(join(project, '.agents/skills/owner-sample/SKILL.md'), 'utf8')).toBe(content);
		const workflow = await readFile(join(project, '.agents/skills/skillstore-pack-sample-pack/SKILL.md'), 'utf8');
		expect(workflow).toContain(state.pack.executionBinding.usageGuideMarker);
		expect(await readFile(join(project, '.claude/skills/skillstore-pack-sample-pack/SKILL.md'), 'utf8')).toBe(workflow);
		expect(JSON.parse(await readFile(join(project, '.agents/.skill-lock.json'), 'utf8')).skills['owner-sample']).toBeDefined();
		await expect(lstat(join(state.root, 'home'))).rejects.toMatchObject({ code: 'ENOENT' });
	});
	it('restores the project lock and members if an unowned workflow blocks installation', async () => {
		const workflow = join(project, '.agents/skills/skillstore-pack-sample-pack');
		await mkdir(workflow, { recursive: true });
		await writeFile(join(workflow, 'SKILL.md'), 'keep existing workflow');
		const lockPath = join(project, '.agents/.skill-lock.json');
		const lock = '{"version":1,"skills":{}}\n'; await writeFile(lockPath, lock);
		await expect(run('@sample-pack')).rejects.toThrow('exit 1');
		expect(await readFile(lockPath, 'utf8')).toBe(lock);
		expect(await readFile(join(workflow, 'SKILL.md'), 'utf8')).toBe('keep existing workflow');
		await expect(lstat(join(project, '.agents/skills/owner-sample'))).rejects.toMatchObject({ code: 'ENOENT' });
		await expect(lstat(join(state.root, 'home'))).rejects.toMatchObject({ code: 'ENOENT' });
	});
	it('preserves legacy Pack links and global content when a project migration is refused', async () => {
		const globalSkill = join(state.root, 'home/.agents/skills/owner-sample');
		await mkdir(globalSkill, { recursive: true });
		await writeFile(join(globalSkill, 'SKILL.md'), 'keep global content');
		await mkdir(join(project, '.agents/skills'), { recursive: true });
		const link = join(project, '.agents/skills/owner-sample');
		await symlink(globalSkill, link);
		await expect(run('@sample-pack')).rejects.toThrow('exit 1');
		expect(await readlink(link)).toBe(globalSkill);
		expect(await readFile(join(globalSkill, 'SKILL.md'), 'utf8')).toBe('keep global content');
	});
	it.each(['.agents', '.agents/skills', '.claude'])('rejects a project directory link at %s before writes', async (path) => {
		const outside = join(state.root, 'outside'); await mkdir(outside);
		await mkdir(join(project, '.agents'), { recursive: true });
		if (path === '.agents') await rm(join(project, '.agents'), { recursive: true });
		await symlink(outside, join(project, path));
		await expect(run()).rejects.toThrow('requires a real directory');
		expect(await readdir(outside)).toEqual([]);
	});
	it('rejects a project lock symlink without changing its target', async () => {
		await mkdir(join(project, '.agents'));
		const outside = join(state.root, 'lock'); await writeFile(outside, 'keep');
		await symlink(outside, join(project, '.agents/.skill-lock.json'));
		await expect(run()).rejects.toThrow('unsafe project lock');
		expect(await readFile(outside, 'utf8')).toBe('keep');
	});
});
