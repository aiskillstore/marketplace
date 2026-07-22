#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

const SHA256 = /^[0-9a-f]{64}$/;
const ID = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function fail(message) { throw new Error(message); }

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.entries(value).filter(([, item]) => item !== undefined)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, item]) => `${JSON.stringify(key)}:${canonicalJson(item)}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function sha256(value) { return createHash('sha256').update(value).digest('hex'); }

// Keep this byte-for-byte compatible with Skillstore's canonical_entries_v1
// tree identity: JSON entries, ordered by path, separated by newlines. The
// generated orchestration Skill has exactly one logical 100644 SKILL.md file.
export function canonicalSingleFileTreeHash(content) {
  const bytes = Buffer.isBuffer(content) ? content : Buffer.from(content);
  return sha256(JSON.stringify({
    path: 'SKILL.md',
    mode: '100644',
    sha256: sha256(bytes),
    size: bytes.byteLength,
  }));
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 2) {
    const flag = argv[index];
    const value = argv[index + 1];
    if (!flag?.startsWith('--') || value == null) fail('Expected --name value arguments');
    args[flag.slice(2)] = value;
  }
  return args;
}

function required(args, name) {
  if (!args[name]) fail(`--${name} is required`);
  return resolve(args[name]);
}

export function orchestrationSlug(packSlug, bindingDigest) {
  const normalized = packSlug.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'workflow';
  const plain = `skillstore-pack-${normalized}`;
  return plain.length <= 64
    ? plain
    : `skillstore-pack-${normalized.slice(0, 39).replace(/-$/, '')}-${bindingDigest.slice(0, 8)}`;
}

export function buildRuntimeOrchestrationContent({ packName, packSlug, dag }) {
  if (!ID.test(packSlug) || !SHA256.test(dag?.bindingDigest ?? '')) fail('Invalid runtime Pack identity');
  const slug = orchestrationSlug(packSlug, dag.bindingDigest);
  const steps = dag.nodes.map((node, index) => {
    const skills = dag.skillBindings.filter((skill) => skill.slotIds.includes(node.id))
      .map((skill) => `\`${skill.canonicalId}\``).join(', ');
    return [
      `${index + 1}. **${node.id}** — ${node.instruction.trim()}`,
      `   - Use: ${skills}`,
      `   - Inputs: ${node.dependsOn.length > 0 ? node.dependsOn.map((item) => `\`${item}\``).join(', ') : 'user input'}`,
      `   - Produce: ${node.artifactIds.length > 0 ? node.artifactIds.map((item) => `\`${item}\``).join(', ') : 'validated completion evidence'}`,
    ].join('\n');
  });
  const description = `Run the verified ${packName} multi-Skill workflow and produce its required artifacts.`;
  const content = [
    '---', `name: ${slug}`, `description: ${JSON.stringify(description)}`, '---', '',
    `# ${packName}`, '', dag.usageGuideMarker, '',
    'Follow the verified stages below in order. Do not continue past a stage until its required artifacts are present and valid.',
    '', ...steps, '',
    'Use only the pinned Skills named above. Ask before any external write, destructive action, purchase, deployment, or message.',
    '',
  ].join('\n');
  return {
    slug,
    content,
    contentHash: sha256(content),
    treeHash: canonicalSingleFileTreeHash(content),
  };
}

export async function buildRuntimeStage({ evaluation, opportunity, skillsRoot, outputDir }) {
  const manifest = evaluation?.candidate?.manifest;
  const dag = manifest?.executionDag;
  if (evaluation?.outcome !== 'candidate_ready' || !manifest || !dag
    || dag.schemaVersion !== 'skillstore.pack-execution-dag/v1'
    || !Array.isArray(dag.skillBindings) || dag.skillBindings.length < 2 || dag.skillBindings.length > 3) {
    fail('Runtime stage requires one candidate_ready 2-3 Skill Pack');
  }
  const orchestration = buildRuntimeOrchestrationContent({
    packName: manifest.name,
    packSlug: manifest.slug,
    dag,
  });
  const orchestrationPath = resolve(outputDir, orchestration.slug);
  await mkdir(orchestrationPath, { recursive: false });
  await writeFile(resolve(orchestrationPath, 'SKILL.md'), orchestration.content, { mode: 0o600 });
  const candidateById = new Map(opportunity.candidateSkills.map((skill) => [skill.canonicalId, skill]));
  const members = dag.skillBindings.map((binding) => {
    const candidate = candidateById.get(binding.canonicalId);
    if (!candidate || candidate.contentHash !== binding.contentHash
      || candidate.treeHash !== binding.treeHash || candidate.version !== binding.version) {
      fail(`Runtime member differs from Opportunity Brief: ${binding.canonicalId}`);
    }
    const memberPath = resolve(skillsRoot, candidate.canonicalPath);
    if (!memberPath.startsWith(`${resolve(skillsRoot)}/`)) fail('Runtime member path escaped the Skill root');
    return {
      canonicalId: binding.canonicalId,
      contentHash: binding.contentHash,
      treeHash: binding.treeHash,
      version: binding.version,
      path: memberPath,
      slotIds: binding.slotIds,
    };
  });
  const snakeDag = {
    schema_version: dag.schemaVersion,
    workflow_digest: dag.workflowDigest,
    binding_digest: dag.bindingDigest,
    nodes: dag.nodes.map((node) => ({
      id: node.id, instruction: node.instruction, depends_on: node.dependsOn, artifact_ids: node.artifactIds,
    })),
    handoffs: dag.handoffs.map((handoff) => ({
      from: handoff.from, to: handoff.to, artifact_ids: handoff.artifactIds, contract: handoff.contract,
    })),
    skill_bindings: dag.skillBindings.map((skill) => ({
      canonical_id: skill.canonicalId, content_hash: skill.contentHash, tree_hash: skill.treeHash,
      version: skill.version, slot_ids: skill.slotIds,
    })),
    usage_guide_marker: dag.usageGuideMarker,
  };
  return {
    schemaVersion: 'skillstore.pack-runtime-identities/v1',
    orchestration: {
      canonicalId: orchestration.slug,
      contentHash: orchestration.contentHash,
      treeHash: orchestration.treeHash,
      version: evaluation.scenario.version,
      path: orchestrationPath,
      slotIds: [],
    },
    members,
    executionDag: snakeDag,
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const [evaluation, opportunity] = await Promise.all([
    readFile(required(args, 'evaluation'), 'utf8').then(JSON.parse),
    readFile(required(args, 'opportunity'), 'utf8').then(JSON.parse),
  ]);
  const output = required(args, 'output');
  const stage = await buildRuntimeStage({
    evaluation,
    opportunity,
    skillsRoot: required(args, 'skills-root'),
    outputDir: required(args, 'output-dir'),
  });
  await mkdir(dirname(output), { recursive: true });
  await writeFile(output, `${JSON.stringify(stage, null, 2)}\n`, { mode: 0o600 });
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(new URL(import.meta.url).pathname)) {
  main().catch((error) => {
    process.stderr.write(`${error.stack ?? error.message ?? String(error)}\n`);
    process.exitCode = 1;
  });
}
