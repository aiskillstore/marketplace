import { createHash, randomUUID } from 'node:crypto';
import { lstat, mkdir, readFile, readlink, rename, rm, writeFile } from 'node:fs/promises';
import { basename, dirname, join, resolve } from 'node:path';
import type { AgentConfig } from './agents.js';
import {
	getAgentSkillPath,
	getCanonicalSkillPath,
	installToAgents,
	type MultiAgentInstallResult,
} from './installer.js';
import type {
	ManifestSkill,
	PackExecutionBinding,
	PackExecutionDag,
	PluginManifest,
} from './plugin-api.js';

const SHA256 = /^[0-9a-f]{64}$/;
const SKILL_ID = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
export const PACK_ORCHESTRATION_RECEIPT_FILE = 'skillstore-pack-orchestration.json';
const RECEIPT_SCHEMA = 'skillstore.pack-orchestration-install/v1';

export interface PackOrchestration {
	slug: string;
	packSlug: string;
	packVersion: string;
	orchestrationVersion: string;
	content: string;
	contentHash: string;
	treeHash: string;
	bindingDigest: string;
}

export interface PackOrchestrationReceipt {
	schemaVersion: typeof RECEIPT_SCHEMA;
	managedBy: 'skillstore-cli';
	slug: string;
	packSlug: string;
	packVersion: string;
	orchestrationVersion: string;
	contentHash: string;
	treeHash: string;
	bindingDigest: string;
}

export interface PackOrchestrationInstallResult {
	slug: string;
	canonicalId: string;
	version: string;
	contentHash: string;
	treeHash: string;
	bindingDigest: string;
	canonicalPath: string;
	agentPaths: string[];
}

export interface PackOrchestrationInstallDependencies {
	getCanonicalPath?: (slug: string) => string;
	install?: typeof installToAgents;
}

export interface PackOrchestrationTransaction {
	result: PackOrchestrationInstallResult;
	commit(): Promise<Error[]>;
	rollback(): Promise<void>;
}

function canonicalJson(value: unknown): string {
	if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
	if (value && typeof value === 'object') {
		return `{${Object.entries(value as Record<string, unknown>)
			.filter(([, item]) => item !== undefined)
			.sort(([left], [right]) => left.localeCompare(right))
			.map(([key, item]) => `${JSON.stringify(key)}:${canonicalJson(item)}`)
			.join(',')}}`;
	}
	return JSON.stringify(value);
}

function sha256(value: unknown): string {
	return createHash('sha256').update(canonicalJson(value)).digest('hex');
}

function contentHash(value: string): string {
	return createHash('sha256').update(value).digest('hex');
}

/**
 * The ownership receipt is installer-managed metadata, not Pack source. It is
 * excluded from the canonical tree and its own fields are verified separately.
 */
function orchestrationTreeHash(content: string): string {
	return createHash('sha256').update(JSON.stringify({
		path: 'SKILL.md',
		mode: '100644',
		sha256: contentHash(content),
		size: Buffer.byteLength(content),
	})).digest('hex');
}

function orchestrationSlug(packSlug: string, bindingDigest: string): string {
	const normalized = packSlug.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'workflow';
	const plain = `skillstore-pack-${normalized}`;
	return plain.length <= 64
		? plain
		: `skillstore-pack-${normalized.slice(0, 39).replace(/-$/, '')}-${bindingDigest.slice(0, 8)}`;
}

function assertStringArray(value: unknown, label: string): asserts value is string[] {
	if (!Array.isArray(value) || value.some((item) => typeof item !== 'string' || !item)) {
		throw new Error(`Invalid Pack execution binding: ${label}`);
	}
}

function assertUniqueStringArray(value: unknown, label: string): asserts value is string[] {
	assertStringArray(value, label);
	if (new Set(value).size !== value.length) {
		throw new Error(`Invalid Pack execution binding: duplicate ${label}`);
	}
}

function assertDag(binding: PackExecutionBinding, members: ManifestSkill[]): PackExecutionDag {
	const dag = binding.executionDag;
	if (!dag || dag.schemaVersion !== 'skillstore.pack-execution-dag/v1') {
		throw new Error('Invalid Pack execution binding: unsupported DAG');
	}
	if (!SHA256.test(binding.bindingDigest) || !SHA256.test(binding.workflowDigest)) {
		throw new Error('Invalid Pack execution binding: malformed digest');
	}
	if (
		binding.schemaVersion !== 'skillstore.pack-execution-binding/v1'
		|| binding.bindingDigest !== dag.bindingDigest
		|| binding.workflowDigest !== dag.workflowDigest
		|| binding.usageGuideMarker !== dag.usageGuideMarker
		|| dag.usageGuideMarker !== `<!-- skillstore-execution-binding:${dag.bindingDigest} -->`
	) {
		throw new Error('Invalid Pack execution binding: inconsistent binding');
	}
	if (!Array.isArray(dag.nodes) || !Array.isArray(dag.handoffs) || !Array.isArray(dag.skillBindings)) {
		throw new Error('Invalid Pack execution binding: incomplete DAG');
	}

	const nodeIds = new Set<string>();
	const nodeById = new Map<string, PackExecutionDag['nodes'][number]>();
	const artifactProducer = new Map<string, string>();
	for (const node of dag.nodes) {
		if (!node || !SKILL_ID.test(node.id) || !node.instruction?.trim() || nodeIds.has(node.id)) {
			throw new Error('Invalid Pack execution binding: malformed DAG node');
		}
		assertUniqueStringArray(node.dependsOn, `node ${node.id} dependencies`);
		assertUniqueStringArray(node.artifactIds, `node ${node.id} artifacts`);
		if (node.dependsOn.some((dependency) => !nodeIds.has(dependency))) {
			throw new Error(`Invalid Pack execution binding: node ${node.id} is not topologically ordered`);
		}
		for (const artifactId of node.artifactIds) {
			if (artifactProducer.has(artifactId)) {
				throw new Error(`Invalid Pack execution binding: artifact ${artifactId} has multiple producers`);
			}
			artifactProducer.set(artifactId, node.id);
		}
		nodeIds.add(node.id);
		nodeById.set(node.id, node);
	}
	if (nodeIds.size === 0) throw new Error('Invalid Pack execution binding: empty DAG');
	const handoffEdges = new Set<string>();
	for (const handoff of dag.handoffs) {
		assertUniqueStringArray(handoff.artifactIds, `handoff ${handoff.from} -> ${handoff.to} artifacts`);
		const source = nodeById.get(handoff.from);
		const target = nodeById.get(handoff.to);
		const edge = `${handoff.from}->${handoff.to}`;
		if (
			!source
			|| !target
			|| handoff.from === handoff.to
			|| handoff.contract !== 'validated-artifacts-only'
			|| !target.dependsOn.includes(handoff.from)
			|| handoff.artifactIds.length === 0
			|| handoff.artifactIds.some((artifactId) => artifactProducer.get(artifactId) !== source.id)
			|| handoffEdges.has(edge)
		) {
			throw new Error('Invalid Pack execution binding: malformed handoff');
		}
		handoffEdges.add(edge);
	}
	const expectedHandoffEdges = dag.nodes
		.flatMap((node) => node.dependsOn.map((dependency) => `${dependency}->${node.id}`))
		.sort();
	if (canonicalJson([...handoffEdges].sort()) !== canonicalJson(expectedHandoffEdges)) {
		throw new Error('Invalid Pack execution binding: handoffs do not match dependencies');
	}

	if (new Set(members.map((member) => member.slug)).size !== members.length) {
		throw new Error('Invalid Pack execution binding: duplicate manifest Skill');
	}
	const memberBySlug = new Map(members.map((member) => [member.slug, member]));
	const boundSkills = new Set<string>();
	for (const skill of dag.skillBindings) {
		assertStringArray(skill.slotIds, `Skill ${skill.canonicalId} slots`);
		const member = memberBySlug.get(skill.canonicalId);
		if (
			!SKILL_ID.test(skill.canonicalId)
			|| !SHA256.test(skill.contentHash)
			|| !SHA256.test(skill.treeHash)
			|| !skill.version
			|| !member
			|| member.contentHash !== skill.contentHash
			|| member.treeHash !== skill.treeHash
			|| member.version !== skill.version
			|| skill.slotIds.length === 0
			|| skill.slotIds.some((slotId) => !nodeIds.has(slotId))
			|| boundSkills.has(skill.canonicalId)
		) {
			throw new Error(`Invalid Pack execution binding: Skill ${skill.canonicalId || '(unknown)'}`);
		}
		boundSkills.add(skill.canonicalId);
	}
	if (boundSkills.size !== members.length || dag.nodes.some((node) =>
		!dag.skillBindings.some((skill) => skill.slotIds.includes(node.id))
	)) {
		throw new Error('Invalid Pack execution binding: incomplete Skill coverage');
	}
	if (canonicalJson(binding.skills) !== canonicalJson(dag.skillBindings)) {
		throw new Error('Invalid Pack execution binding: projected Skills differ from the DAG');
	}

	const workflowDigest = sha256({
		schema_version: dag.schemaVersion,
		nodes: dag.nodes.map((node) => ({
			id: node.id,
			instruction: node.instruction,
			depends_on: node.dependsOn,
			artifact_ids: node.artifactIds,
		})),
		handoffs: dag.handoffs.map((handoff) => ({
			from: handoff.from,
			to: handoff.to,
			artifact_ids: handoff.artifactIds,
			contract: handoff.contract,
		})),
	});
	const bindingDigest = sha256({
		workflow_digest: workflowDigest,
		skill_bindings: dag.skillBindings.map((skill) => ({
			canonical_id: skill.canonicalId,
			content_hash: skill.contentHash,
			tree_hash: skill.treeHash,
			version: skill.version,
			slot_ids: skill.slotIds,
		})),
	});
	if (workflowDigest !== dag.workflowDigest || bindingDigest !== dag.bindingDigest) {
		throw new Error('Invalid Pack execution binding: digest mismatch');
	}
	return dag;
}

export function buildPackOrchestration(manifest: PluginManifest): PackOrchestration | null {
	const binding = manifest.executionBinding;
	if (!binding) return null;
	const packVersion = manifest.pack?.version ?? manifest.plugin?.version;
	if (typeof packVersion !== 'string' || !packVersion.trim()) {
		throw new Error('Invalid Pack execution binding: missing Pack version');
	}
	const dag = assertDag(binding, manifest.skills);
	const slug = orchestrationSlug(manifest.plugin.slug, binding.bindingDigest);
	if (manifest.skills.some((skill) => skill.slug === slug)) {
		throw new Error('Invalid Pack execution binding: orchestration slug collides with a member Skill');
	}
	const steps = dag.nodes.map((node, index) => {
		const skills = dag.skillBindings
			.filter((skill) => skill.slotIds.includes(node.id))
			.map((skill) => `\`${skill.canonicalId}\``)
			.join(', ');
		return [
			`${index + 1}. **${node.id}** — ${node.instruction.trim()}`,
			`   - Use: ${skills}`,
			`   - Inputs: ${node.dependsOn.length > 0 ? node.dependsOn.map((item) => `\`${item}\``).join(', ') : 'user input'}`,
			`   - Produce: ${node.artifactIds.length > 0 ? node.artifactIds.map((item) => `\`${item}\``).join(', ') : 'validated completion evidence'}`,
		].join('\n');
	});
	const description = `Run the verified ${manifest.plugin.name} multi-Skill workflow and produce its required artifacts.`;
	const content = [
			'---',
			`name: ${slug}`,
			`description: ${JSON.stringify(description)}`,
			'---',
			'',
			`# ${manifest.plugin.name}`,
			'',
			dag.usageGuideMarker,
			'',
			'Follow the verified stages below in order. Do not continue past a stage until its required artifacts are present and valid.',
			'',
			...steps,
			'',
			'Use only the pinned Skills named above. Ask before any external write, destructive action, purchase, deployment, or message.',
			'',
		].join('\n');
	return {
		slug,
		packSlug: manifest.plugin.slug,
		packVersion,
		orchestrationVersion: packVersion,
		bindingDigest: binding.bindingDigest,
		content,
		contentHash: contentHash(content),
		treeHash: orchestrationTreeHash(content),
	};
}

export function buildPackOrchestrationReceipt(
	orchestration: PackOrchestration
): PackOrchestrationReceipt {
	return {
		schemaVersion: RECEIPT_SCHEMA,
		managedBy: 'skillstore-cli',
		slug: orchestration.slug,
		packSlug: orchestration.packSlug,
		packVersion: orchestration.packVersion,
		orchestrationVersion: orchestration.orchestrationVersion,
		contentHash: orchestration.contentHash,
		treeHash: orchestration.treeHash,
		bindingDigest: orchestration.bindingDigest,
	};
}

function receiptJson(orchestration: PackOrchestration): string {
	return `${JSON.stringify(buildPackOrchestrationReceipt(orchestration), null, 2)}\n`;
}

function parseReceipt(value: string): PackOrchestrationReceipt | null {
	try {
		const receipt = JSON.parse(value) as Partial<PackOrchestrationReceipt>;
		return receipt.schemaVersion === RECEIPT_SCHEMA
			&& receipt.managedBy === 'skillstore-cli'
			&& typeof receipt.slug === 'string'
			&& typeof receipt.packSlug === 'string'
			&& typeof receipt.packVersion === 'string'
			&& receipt.packVersion.length > 0
			&& typeof receipt.orchestrationVersion === 'string'
			&& receipt.orchestrationVersion.length > 0
			&& typeof receipt.contentHash === 'string'
			&& SHA256.test(receipt.contentHash)
			&& typeof receipt.treeHash === 'string'
			&& SHA256.test(receipt.treeHash)
			&& typeof receipt.bindingDigest === 'string'
			&& SHA256.test(receipt.bindingDigest)
			? receipt as PackOrchestrationReceipt
			: null;
	} catch {
		return null;
	}
}

async function pathState(path: string): Promise<'missing' | 'directory' | 'symlink' | 'other'> {
	try {
		const stat = await lstat(path);
		if (stat.isSymbolicLink()) return 'symlink';
		if (stat.isDirectory()) return 'directory';
		return 'other';
	} catch (error) {
		if ((error as NodeJS.ErrnoException).code === 'ENOENT') return 'missing';
		throw error;
	}
}

async function verifyOwnedDirectory(
	path: string,
	orchestration: Pick<PackOrchestration, 'slug' | 'packSlug'>,
	exact?: Pick<PackOrchestration, 'packVersion' | 'orchestrationVersion' | 'contentHash' | 'treeHash' | 'bindingDigest'>
): Promise<PackOrchestrationReceipt> {
	if (await pathState(path) !== 'directory') {
		throw new Error(`Refusing to replace unowned Pack workflow path: ${path}`);
	}
	let skillContent: string;
	let receipt: PackOrchestrationReceipt | null;
	try {
		[skillContent, receipt] = await Promise.all([
			readFile(join(path, 'SKILL.md'), 'utf8'),
			readFile(join(path, PACK_ORCHESTRATION_RECEIPT_FILE), 'utf8').then(parseReceipt),
		]);
	} catch {
		throw new Error(`Refusing to replace Pack workflow without an ownership receipt: ${path}`);
	}
	if (
		!receipt
		|| receipt.slug !== orchestration.slug
		|| receipt.packSlug !== orchestration.packSlug
		|| receipt.contentHash !== contentHash(skillContent)
		|| receipt.treeHash !== orchestrationTreeHash(skillContent)
		|| (exact && (
			receipt.packVersion !== exact.packVersion
			|| receipt.orchestrationVersion !== exact.orchestrationVersion
			|| receipt.contentHash !== exact.contentHash
			|| receipt.treeHash !== exact.treeHash
			|| receipt.bindingDigest !== exact.bindingDigest
		))
	) {
		throw new Error(`Refusing to replace modified or unowned Pack workflow: ${path}`);
	}
	return receipt;
}

async function writeAndVerifyStage(path: string, orchestration: PackOrchestration): Promise<void> {
	await mkdir(path, { recursive: false, mode: 0o700 });
	await Promise.all([
		writeFile(join(path, 'SKILL.md'), orchestration.content, { encoding: 'utf8', mode: 0o600 }),
		writeFile(join(path, PACK_ORCHESTRATION_RECEIPT_FILE), receiptJson(orchestration), {
			encoding: 'utf8',
			mode: 0o600,
		}),
	]);
	await verifyOwnedDirectory(path, orchestration, orchestration);
}

interface TargetState {
	path: string;
	existed: boolean;
}

async function preflightTargets(
	orchestration: PackOrchestration,
	canonicalPath: string,
	targetAgents: AgentConfig[],
	isGlobal: boolean
): Promise<TargetState[]> {
	const targets: TargetState[] = [];
	for (const agent of targetAgents) {
		const path = getAgentSkillPath(orchestration.slug, agent, { global: isGlobal });
		if (resolve(path) === resolve(canonicalPath)) {
			targets.push({ path, existed: await pathState(path) !== 'missing' });
			continue;
		}
		const state = await pathState(path);
		if (state === 'missing') {
			targets.push({ path, existed: false });
			continue;
		}
		if (state === 'symlink') {
			const target = await readlink(path);
			if (resolve(dirname(path), target) !== resolve(canonicalPath)) {
				throw new Error(`Refusing to replace unowned Pack workflow link: ${path}`);
			}
		} else {
			await verifyOwnedDirectory(path, orchestration);
		}
		targets.push({ path, existed: true });
	}
	return targets;
}

async function verifyActiveInstall(
	orchestration: PackOrchestration,
	canonicalPath: string,
	links: MultiAgentInstallResult
): Promise<PackOrchestrationInstallResult> {
	await verifyOwnedDirectory(canonicalPath, orchestration, orchestration);
	if (!links.success || links.failCount > 0) {
		throw new Error('Pack workflow agent linking failed');
	}
	for (const result of links.agents) {
		if (!result.success) throw new Error(`Pack workflow agent linking failed: ${result.path}`);
		if (resolve(result.path) === resolve(canonicalPath)) continue;
		const state = await pathState(result.path);
		if (state === 'symlink') {
			const target = await readlink(result.path);
			if (resolve(dirname(result.path), target) !== resolve(canonicalPath)) {
				throw new Error(`Pack workflow link readback failed: ${result.path}`);
			}
			await verifyOwnedDirectory(canonicalPath, orchestration, orchestration);
		} else {
			await verifyOwnedDirectory(result.path, orchestration, orchestration);
		}
	}
	return {
		slug: orchestration.slug,
		canonicalId: orchestration.slug,
		version: orchestration.orchestrationVersion,
		contentHash: orchestration.contentHash,
		treeHash: orchestration.treeHash,
		bindingDigest: orchestration.bindingDigest,
		canonicalPath,
		agentPaths: links.agents.map((result) => result.path),
	};
}

async function removeActivatedPath(path: string, orchestration: PackOrchestration): Promise<void> {
	const state = await pathState(path);
	if (state === 'missing') return;
	if (state === 'symlink') {
		await rm(path, { force: true });
		return;
	}
	await verifyOwnedDirectory(path, orchestration, orchestration);
	await rm(path, { recursive: true, force: true });
}

async function removeOwnedPath(
	path: string,
	orchestration: Pick<PackOrchestration, 'slug' | 'packSlug'>,
	canonicalPath: string
): Promise<void> {
	const state = await pathState(path);
	if (state === 'missing') return;
	if (state === 'symlink') {
		const target = await readlink(path);
		if (resolve(dirname(path), target) !== resolve(canonicalPath)) {
			throw new Error(`Refusing to remove unowned Pack workflow link: ${path}`);
		}
		await rm(path, { force: true });
		return;
	}
	await verifyOwnedDirectory(path, orchestration);
	await rm(path, { recursive: true, force: true });
}

export async function stagePackOrchestration(
	orchestration: PackOrchestration,
	targetAgents: AgentConfig[],
	isGlobal: boolean,
	dependencies: PackOrchestrationInstallDependencies = {}
): Promise<PackOrchestrationTransaction> {
	const canonicalPath = (dependencies.getCanonicalPath ?? getCanonicalSkillPath)(orchestration.slug);
	const install = dependencies.install ?? installToAgents;
	const parent = dirname(canonicalPath);
	const suffix = randomUUID();
	const stagePath = join(parent, `.${basename(canonicalPath)}.stage-${suffix}`);
	const backupPath = join(parent, `.${basename(canonicalPath)}.backup-${suffix}`);
	await mkdir(parent, { recursive: true });
	const targetStates = await preflightTargets(orchestration, canonicalPath, targetAgents, isGlobal);
	const canonicalState = await pathState(canonicalPath);
	const hadPrevious = canonicalState !== 'missing';
	if (hadPrevious) await verifyOwnedDirectory(canonicalPath, orchestration);

	let links: MultiAgentInstallResult | undefined;
	let backupCreated = false;
	let activated = false;
	let closed = false;
	const rollback = async () => {
		if (closed) return;
		const rollbackErrors: unknown[] = [];
		if (activated) {
			try {
				await removeActivatedPath(canonicalPath, orchestration);
			} catch (rollbackError) {
				rollbackErrors.push(rollbackError);
			}
		}
		if (backupCreated) {
			try {
				await rename(backupPath, canonicalPath);
				backupCreated = false;
				await install(orchestration.slug, targetAgents, { global: isGlobal });
			} catch (rollbackError) {
				rollbackErrors.push(rollbackError);
			}
		}
		for (const target of targetStates.filter((item) => !item.existed)) {
			if (resolve(target.path) === resolve(canonicalPath)) continue;
			try {
				await removeOwnedPath(target.path, orchestration, canonicalPath);
			} catch (rollbackError) {
				rollbackErrors.push(rollbackError);
			}
		}
		closed = true;
		if (rollbackErrors.length > 0) {
			throw new AggregateError(rollbackErrors, 'Pack workflow rollback failed');
		}
	};
	try {
		await writeAndVerifyStage(stagePath, orchestration);
		if (hadPrevious) {
			await rename(canonicalPath, backupPath);
			backupCreated = true;
		}
		await rename(stagePath, canonicalPath);
		activated = true;
		links = await install(orchestration.slug, targetAgents, { global: isGlobal });
		const result = await verifyActiveInstall(orchestration, canonicalPath, links);
		return {
			result,
			async commit() {
				if (closed) return [];
				const cleanupErrors: Error[] = [];
				if (backupCreated) {
					try {
						await rm(backupPath, { recursive: true, force: true });
					} catch (error) {
						cleanupErrors.push(error instanceof Error ? error : new Error(String(error)));
					}
				}
				closed = true;
				return cleanupErrors;
			},
			rollback,
		};
	} catch (error) {
		try {
			await rollback();
		} catch (rollbackError) {
			throw new AggregateError([error, rollbackError], 'Pack workflow activation and rollback failed');
		}
		throw error;
	} finally {
		await rm(stagePath, { recursive: true, force: true });
	}
}

export async function installPackOrchestration(
	orchestration: PackOrchestration,
	targetAgents: AgentConfig[],
	isGlobal: boolean,
	dependencies: PackOrchestrationInstallDependencies = {}
): Promise<PackOrchestrationInstallResult> {
	const transaction = await stagePackOrchestration(orchestration, targetAgents, isGlobal, dependencies);
	await transaction.commit();
	return transaction.result;
}
