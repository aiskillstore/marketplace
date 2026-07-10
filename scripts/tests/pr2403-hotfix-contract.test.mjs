import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '..', '..');
const PROMOTION_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'on-pr-merge.yml');
const SYNC_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'sync-to-supabase.yml');
const VALIDATE_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'validate-marketplace.yml');
const ISSUE_APPROVAL_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'issue-approval.yml');
const STANDALONE_WATCH = join(
	REPO_ROOT,
	'skills',
	'internet-court',
	'okx-ai',
	'references',
	'watch-core.md',
);
const VENDORED_WATCH = join(
	REPO_ROOT,
	'skills',
	'internet-court',
	'internet-court',
	'vendored',
	'okx',
	'okx-ai',
	'references',
	'watch-core.md',
);

function sha256(value) {
	return createHash('sha256').update(value).digest('hex');
}

function normalizeSkillMdContent(content) {
	const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
	if (!frontmatterMatch) return content.trim();

	const frontmatter = frontmatterMatch[1]
		.split('\n')
		.filter((line) => !line.trim().startsWith('version:'))
		.join('\n');
	const body = content.slice(frontmatterMatch[0].length);
	return `---\n${frontmatter}\n---${body}`.trim();
}

function calculateCurrentHashes(packageDir) {
	const fileHashes = [];

	function walk(dir) {
		const entries = readdirSync(dir, { withFileTypes: true })
			.sort((left, right) => left.name.localeCompare(right.name));
		for (const entry of entries) {
			const fullPath = join(dir, entry.name);
			if (entry.isDirectory()) {
				walk(fullPath);
			} else if (entry.isFile() && entry.name !== 'skill-report.json') {
				fileHashes.push(`${relative(packageDir, fullPath)}:${sha256(readFileSync(fullPath))}`);
			}
		}
	}

	walk(packageDir);
	return {
		contentHash: sha256(normalizeSkillMdContent(readFileSync(join(packageDir, 'SKILL.md'), 'utf8'))),
		treeHash: sha256(fileHashes.join('\n')),
	};
}

function getWorkflowStep(workflow, name) {
	const marker = `      - name: ${name}`;
	const start = workflow.indexOf(marker);
	assert.ok(start >= 0, `workflow step not found: ${name}`);
	const next = workflow.indexOf('\n      - name:', start + marker.length);
	return workflow.slice(start, next >= 0 ? next : workflow.length);
}

test('standalone and vendored okx-ai never execute remote llmContent as instructions', () => {
	for (const watchPath of [STANDALONE_WATCH, VENDORED_WATCH]) {
		const content = readFileSync(watchPath, 'utf8');
		assert.doesNotMatch(content, /execute the commands specified in `llmContent` verbatim/i);
		assert.match(content, /llmContent.*untrusted data/i);
		assert.match(content, /okx-a2a\.decision-action\/v1/);
		assert.match(content, /local allowlist/i);
		assert.match(content, /current user session.*explicit confirmation/i);
	}
});

test('PR2403 and hotfix-affected reports are bound to the current package bytes', () => {
	const packageDirs = [
		'skills/internet-court/altllm-portal-cli',
		'skills/internet-court/humanode-agentlink',
		'skills/internet-court/internet-court',
		'skills/internet-court/kleros-curate',
		'skills/internet-court/kleros-ipfs-upload',
		'skills/internet-court/lifi-stablecoin-swap',
		'skills/internet-court/lifi',
		'skills/internet-court/near-ai-cloud',
		'skills/internet-court/okx-ai',
		'skills/internet-court/okx-guide',
		'skills/internet-court/privy',
		'skills/internet-court/starknet-defi',
		'skills/internet-court/starknet-identity',
		'skills/internet-court/starknet-js',
		'skills/internet-court/starknet-wallet',
		'skills/internet-court/trustless-agents',
		'skills/internet-court/x402',
	];
	const failures = [];

	for (const relativeDir of packageDirs) {
		const packageDir = join(REPO_ROOT, relativeDir);
		const report = JSON.parse(readFileSync(join(packageDir, 'skill-report.json'), 'utf8'));
		const current = calculateCurrentHashes(packageDir);
		if (report.meta.content_hash !== current.contentHash) {
			failures.push(`${relativeDir} content_hash is stale`);
		}
		if (report.meta.tree_hash !== current.treeHash) {
			failures.push(`${relativeDir} tree_hash is stale`);
		}
	}

	assert.deepEqual(failures, [], failures.join('\n'));
});

test('known broken references use existing package-local targets without fabricated files', () => {
	for (const relativePath of [
		'skills/internet-court/near-ai-cloud/SKILL.md',
		'skills/internet-court/internet-court/vendored/near/near-ai-cloud/SKILL.md',
	]) {
		const content = readFileSync(join(REPO_ROOT, relativePath), 'utf8');
		assert.match(content, /\]\(references\/private-vs-anonymised\.md\)/);
		assert.doesNotMatch(content, /references\/model-list\.md/);
	}

	for (const relativePath of [
		'skills/internet-court/altllm-portal-cli/references/skill-map.md',
		'skills/internet-court/internet-court/vendored/altlayer/altllm-portal-cli/references/skill-map.md',
	]) {
		const content = readFileSync(join(REPO_ROOT, relativePath), 'utf8');
		assert.doesNotMatch(content, /\]\((?:\.\.\/)+/);
	}

	for (const relativePath of [
		'skills/internet-court/okx-ai/references/task-state-machine.md',
		'skills/internet-court/okx-ai/references/task-user-intent-routing.md',
		'skills/internet-court/internet-court/vendored/okx/okx-ai/references/task-state-machine.md',
		'skills/internet-court/internet-court/vendored/okx/okx-ai/references/task-user-intent-routing.md',
	]) {
		const content = readFileSync(join(REPO_ROOT, relativePath), 'utf8');
		assert.doesNotMatch(content, /(?:task-user-buyer|payment-modes|entry-points)\.md/);
	}
});

test('promotion validates candidates before the first directory move', () => {
	const workflow = readFileSync(PROMOTION_WORKFLOW, 'utf8');
	const gateIndex = workflow.indexOf('validate-skill-publication.mjs');
	const moveIndex = workflow.indexOf('mv "$PENDING_DIR" "$TARGET_DIR"');

	assert.ok(gateIndex >= 0, 'promotion workflow must call the publication gate');
	assert.ok(moveIndex >= 0, 'promotion workflow must still move approved packages');
	assert.ok(gateIndex < moveIndex, 'promotion gate must run before any package move');
});

test('sync independently re-gates packages before invoking skillstore-cli or Supabase', () => {
	const workflow = readFileSync(SYNC_WORKFLOW, 'utf8');
	const gateIndex = workflow.indexOf('validate-skill-publication.mjs');
	const syncIndex = workflow.indexOf('"$GITHUB_WORKSPACE/skillstore-cli" skill sync');

	assert.ok(gateIndex >= 0, 'sync workflow must call the publication gate');
	assert.ok(syncIndex >= 0, 'sync workflow must still invoke skillstore-cli');
	assert.ok(gateIndex < syncIndex, 'sync gate must run before the CLI can write Supabase');
});

test('publication workflows pass an existing GitHub token to the validator through env', () => {
	const promotionWorkflow = readFileSync(PROMOTION_WORKFLOW, 'utf8');
	const syncWorkflow = readFileSync(SYNC_WORKFLOW, 'utf8');

	assert.match(
		promotionWorkflow,
		/GH_TOKEN: \$\{\{ steps\.app-token\.outputs\.token \}\}[\s\S]*validate-skill-publication\.mjs/,
	);
	assert.match(
		syncWorkflow,
		/name: Validate publication safety before sync[\s\S]*GH_TOKEN: \$\{\{ steps\.app-token\.outputs\.token \}\}[\s\S]*validate-skill-publication\.mjs/,
	);
	assert.doesNotMatch(promotionWorkflow, /validate-skill-publication\.mjs[\s\S]{0,300}--(?:github-)?token/);
	assert.doesNotMatch(syncWorkflow, /validate-skill-publication\.mjs[\s\S]{0,300}--(?:github-)?token/);
});

test('safe-to-publish evidence reuses the issue_comment /approve permission gate', () => {
	const workflow = readFileSync(ISSUE_APPROVAL_WORKFLOW, 'utf8');

	assert.match(workflow, /issue_comment:\s*\n\s+types: \[created\]/);
	assert.match(workflow, /startsWith\(github\.event\.comment\.body, '\/approve'\)/);
	assert.match(workflow, /github\.event\.comment\.user\.type == 'User'/);
	assert.match(workflow, /\/approve safe-to-publish/);
	assert.match(workflow, /collaborators\/\$\{\{ github\.event\.comment\.user\.login \}\}\/permission/);
});

test('CI validates changed package freshness, evidence, and relative links', () => {
	const workflow = readFileSync(VALIDATE_WORKFLOW, 'utf8');

	assert.match(workflow, /validate-skill-publication\.mjs.*--integrity-only.*--changed-since/s);
	assert.match(workflow, /skills\/\*\*\/\*\.md/);
	assert.match(workflow, /pending\/\*\*\/\*\.md/);
	assert.match(workflow, /\.github\/workflows\/issue-approval\.yml/);
	assert.match(
		workflow,
		/name: Validate changed package report integrity\s+if: \$\{\{ !cancelled\(\) \}\}/,
	);
});

test('changed package integrity fetches the shallow diff endpoints before validation', () => {
	const workflow = readFileSync(VALIDATE_WORKFLOW, 'utf8');
	const step = getWorkflowStep(workflow, 'Validate changed package report integrity');
	const prFetch = 'git fetch --no-tags --depth=1 origin "$PR_BASE_SHA"';
	const prValidation = '--changed-since "$PR_BASE_SHA"';
	const pushFetch = 'git fetch --no-tags --deepen=1 origin "$BRANCH"';
	const pushValidation = '--changed-since HEAD~1';

	assert.match(step, /working-directory: \$\{\{ env\.WORK_DIR \}\}/);
	assert.match(step, /EVENT_NAME: \$\{\{ github\.event_name \}\}/);
	assert.match(step, /PR_BASE_SHA: \$\{\{ github\.event\.pull_request\.base\.sha \|\| '' \}\}/);
	assert.ok(step.indexOf(prFetch) >= 0, 'PR validation must fetch the exact base SHA');
	assert.ok(step.indexOf(prValidation) > step.indexOf(prFetch), 'PR base fetch must precede validation');
	assert.ok(step.indexOf(pushFetch) >= 0, 'push validation must deepen the current branch by one');
	assert.ok(
		step.indexOf(pushValidation) > step.indexOf(pushFetch),
		'push branch deepening must precede HEAD~1 validation',
	);
	assert.doesNotMatch(step, /--unshallow/);
	assert.doesNotMatch(step, /APP_TOKEN|secrets\./);
});
