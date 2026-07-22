import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, readFileSync, rmSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { buildRuntimeStage, canonicalSingleFileTreeHash } from '../pack-runtime-stage.mjs';

function canonicalSingleFileTreeHashIndependently(content) {
  const bytes = Buffer.from(content);
  const sha256 = (value) => createHash('sha256').update(value).digest('hex');
  return sha256(JSON.stringify({
    path: 'SKILL.md', mode: '100644', sha256: sha256(bytes), size: bytes.byteLength,
  }));
}

const bindingDigest = 'a'.repeat(64);
const bindings = [
  { canonicalId: 'spreadsheet-skill', contentHash: '1'.repeat(64), treeHash: '2'.repeat(64), version: '1.0.0', slotIds: ['workbook'] },
  { canonicalId: 'workbook-validator', contentHash: '3'.repeat(64), treeHash: '4'.repeat(64), version: '2.0.0', slotIds: ['validation'] },
];

function evaluation() {
  return {
    outcome: 'candidate_ready',
    scenario: { version: '1.0.0' },
    candidate: { manifest: {
      name: 'Monthly Sales Workbook',
      slug: 'monthly-sales-workbook',
      executionDag: {
        schemaVersion: 'skillstore.pack-execution-dag/v1',
        bindingDigest,
        nodes: [
          { id: 'workbook', instruction: 'Create the workbook.', dependsOn: [], artifactIds: ['workbook'] },
          { id: 'validation', instruction: 'Validate the workbook.', dependsOn: ['workbook'], artifactIds: ['report'] },
        ],
        handoffs: [{ from: 'workbook', to: 'validation', artifactIds: ['workbook'], contract: 'validated-artifacts-only' }],
        skillBindings: bindings,
        usageGuideMarker: `<!-- skillstore-execution-binding:${bindingDigest} -->`,
      },
    } },
  };
}

test('stages an orchestration Skill only for exact Opportunity Brief identities', async () => {
  const root = mkdtempSync(join(tmpdir(), 'pack-runtime-stage-'));
  try {
    const skillsRoot = join(root, 'skills');
    const outputDir = join(root, 'stage');
    const failedOutputDir = join(root, 'stage-fail');
    mkdirSync(skillsRoot);
    mkdirSync(outputDir);
    mkdirSync(failedOutputDir);
    const opportunity = { candidateSkills: bindings.map((binding, index) => ({
      ...binding,
      canonicalPath: `owner/skill-${index + 1}`,
    })) };
    const stage = await buildRuntimeStage({ evaluation: evaluation(), opportunity, skillsRoot, outputDir });

    assert.equal(stage.orchestration.canonicalId, 'skillstore-pack-monthly-sales-workbook');
    const orchestrationContent = readFileSync(join(stage.orchestration.path, 'SKILL.md'));
    assert.equal(stage.orchestration.treeHash, canonicalSingleFileTreeHashIndependently(orchestrationContent));
    assert.equal(stage.orchestration.treeHash, canonicalSingleFileTreeHash(orchestrationContent));
    assert.notEqual(stage.orchestration.treeHash, stage.orchestration.contentHash);
    assert.deepEqual(stage.members.map(({ canonicalId, treeHash }) => ({ canonicalId, treeHash })), [
      { canonicalId: 'spreadsheet-skill', treeHash: '2'.repeat(64) },
      { canonicalId: 'workbook-validator', treeHash: '4'.repeat(64) },
    ]);
    assert.match(orchestrationContent.toString('utf8'), /Use only the pinned Skills named above/);

    await assert.rejects(
      buildRuntimeStage({
        evaluation: evaluation(),
        opportunity: { candidateSkills: [{ ...opportunity.candidateSkills[0], treeHash: 'f'.repeat(64) }, opportunity.candidateSkills[1]] },
        skillsRoot,
        outputDir: failedOutputDir,
      }),
      /Runtime member differs from Opportunity Brief/,
    );
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
