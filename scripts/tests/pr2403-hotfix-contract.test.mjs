import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '..', '..');
const PROMOTION_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'on-pr-merge.yml');
const SYNC_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'sync-to-supabase.yml');
const VALIDATE_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'validate-marketplace.yml');
const ISSUE_APPROVAL_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'issue-approval.yml');
const APPROVE_SUBMISSION_WORKFLOW = join(
	REPO_ROOT,
	'.github',
	'workflows',
	'approve-submission.yml',
);
const REUSABLE_PROCESS_WORKFLOW = join(
	REPO_ROOT,
	'.github',
	'workflows',
	'reusable-process-skills.yml',
);
const OKX_PACKAGE_ROOTS = [
	join(REPO_ROOT, 'skills', 'internet-court', 'okx-ai'),
	join(
		REPO_ROOT,
		'skills',
		'internet-court',
		'internet-court',
		'vendored',
		'okx',
		'okx-ai',
	),
];
const FOCUSED_SAFETY_TESTS = [
	'scripts/tests/publication-gate.test.mjs',
	'scripts/tests/pr2403-hotfix-contract.test.mjs',
	'scripts/tests/bind-skill-report-hashes.test.mjs',
	'scripts/tests/changed-package-selection.test.mjs',
	'scripts/tests/empty-skill-cleanup.test.mjs',
	'scripts/tests/approval-record.test.mjs',
	'scripts/tests/approval-cas.test.mjs',
];

async function loadGate() {
	const gatePath = join(REPO_ROOT, 'scripts', 'validate-skill-publication.mjs');
	return import(`${pathToFileURL(gatePath).href}?test=${Date.now()}-${Math.random()}`);
}

function getWorkflowStep(workflow, name) {
	const marker = `      - name: ${name}`;
	const start = workflow.indexOf(marker);
	assert.ok(start >= 0, `workflow step not found: ${name}`);
	const next = workflow.indexOf('\n      - name:', start + marker.length);
	return workflow.slice(start, next >= 0 ? next : workflow.length);
}

function getWorkflowJob(workflow, name) {
	const marker = `  ${name}:`;
	const start = workflow.indexOf(marker);
	assert.ok(start >= 0, `workflow job not found: ${name}`);
	const remainder = workflow.slice(start + marker.length);
	const nextMatch = remainder.match(/\n  [a-zA-Z0-9_-]+:\n/);
	const end = nextMatch ? start + marker.length + nextMatch.index : workflow.length;
	return workflow.slice(start, end);
}

function assertLockedInstall(step) {
	assert.match(step, /\brun: npm ci\s*(?:\n|$)/);
	assert.doesNotMatch(step, /\bnpm install\b/);
}

function assertFocusedSafetyCommand(step) {
	const commandIndex = step.indexOf('node --test \\');
	assert.ok(commandIndex >= 0, 'safety step must execute node --test');
	let previousIndex = commandIndex;
	for (const testPath of FOCUSED_SAFETY_TESTS) {
		const testIndex = step.indexOf(testPath, commandIndex);
		assert.ok(testIndex > previousIndex, `${testPath} must run in the focused safety command`);
		previousIndex = testIndex;
	}
	return commandIndex;
}

function markdownFiles(root) {
	const files = [];
	for (const entry of readdirSync(root, { withFileTypes: true })) {
		const fullPath = join(root, entry.name);
		if (entry.isDirectory()) {
			files.push(...markdownFiles(fullPath));
		} else if (entry.isFile() && entry.name.toLowerCase().endsWith('.md')) {
			files.push(fullPath);
		}
	}
	return files;
}

function unsafeLlmContentClauses(content) {
	const clauses = content
		.replace(/`{3,}[\s\S]*?`{3,}/g, '')
		.split(/(?<=[.!?])\s+|\n+/)
		.map((clause) => clause.trim())
		.filter((clause) => /llmContent/i.test(clause));
	const directPatterns = [
		/\b(?:execute|run|invoke|follow|perform)\b.{0,80}\b(?:its\s+)?`?llmContent`?\b/i,
		/\b(?:execute|run|invoke|follow|perform)\b.{0,80}\b(?:whatever|any|all)\b.{0,80}\b(?:commands?|instructions?|actions?|tools?)\b.{0,80}\b`?llmContent`?\b/i,
		/\b(?:commands?|instructions?|actions?|tools?)\b.{0,80}\b`?llmContent`?\b.{0,80}\b(?:specifies|provides|contains|requests)\b/i,
	];
	const explicitDenial = /\b(?:do not|don't|must not|never|cannot|can't|not authorized to)\b.{0,60}\b(?:execute|run|invoke|follow|perform|instruction)/i;

	return clauses.filter((clause) => (
		directPatterns.some((pattern) => pattern.test(clause))
		&& !explicitDenial.test(clause)
	));
}

test('standalone and vendored okx-ai recursively reject remote llmContent execution semantics', () => {
	const failures = [];

	for (const packageRoot of OKX_PACKAGE_ROOTS) {
		const relativeRoot = relative(REPO_ROOT, packageRoot);
		const files = markdownFiles(packageRoot);
		assert.ok(files.length > 2, `${relativeRoot} must be scanned recursively`);

		for (const markdownPath of files) {
			const content = readFileSync(markdownPath, 'utf8');
			for (const clause of unsafeLlmContentClauses(content)) {
				failures.push(`${relative(REPO_ROOT, markdownPath)}: ${clause}`);
			}
		}

		const watchCore = readFileSync(join(packageRoot, 'references', 'watch-core.md'), 'utf8');
		const outstandingDecision = readFileSync(
			join(packageRoot, 'references', 'watch-outdated-list.md'),
			'utf8',
		);
		for (const content of [watchCore, outstandingDecision]) {
			assert.match(content, /llmContent.*untrusted data/i);
			assert.match(content, /okx-a2a\.decision-action\/v1/);
			assert.match(content, /local allowlist/i);
			assert.match(content, /current user session.*explicit confirmation/i);
		}
	}

	assert.deepEqual(failures, [], failures.join('\n'));
});

test('PR2403 and hotfix-affected reports have authentic bindings to the current package tree', async () => {
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
	const { validatePackage } = await loadGate();

	for (const relativeDir of packageDirs) {
		const packageDir = join(REPO_ROOT, relativeDir);
		const attestationPath = join(packageDir, 'skill-report.attestation.json');
		if (!existsSync(attestationPath)) {
			failures.push(`${relativeDir} audit attestation is missing`);
			continue;
		}
		const result = await validatePackage(packageDir, {
			enforcePublicationPolicy: false,
			requireAuditAttestation: true,
		});
		if (!result.ok) {
			failures.push(...result.errors.map((error) => `${relativeDir}: ${error}`));
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

test('promotion installs locked dependencies and runs focused safety tests before writes', () => {
	const workflow = readFileSync(PROMOTION_WORKFLOW, 'utf8');
	const promotionStep = getWorkflowStep(
		workflow,
		'Find pending skills and commit to skills directory',
	);
	const installIndex = promotionStep.indexOf('npm ci');
	const testIndex = assertFocusedSafetyCommand(promotionStep);
	const gateIndex = promotionStep.indexOf('node scripts/validate-skill-publication.mjs');
	const writeCommands = [
		'mv "$PENDING_DIR" "$TARGET_DIR"',
		'git commit -m "Approve skills:$SKILL_NAMES$SUBMISSION_TAG"',
		'git push origin main',
	];

	assert.ok(installIndex >= 0 && installIndex < testIndex, 'npm ci must precede safety tests');
	assert.ok(gateIndex > testIndex, 'publication gate must run after focused safety tests');
	for (const command of writeCommands) {
		const writeIndex = promotionStep.indexOf(command);
		assert.ok(writeIndex > testIndex, `${command} must occur after focused safety tests`);
		assert.ok(writeIndex > gateIndex, `${command} must occur after publication validation`);
	}
	assert.doesNotMatch(promotionStep, /\bnpm install\b/);
});

test('sync installs locked dependencies and runs focused safety tests before Supabase writes', () => {
	const workflow = readFileSync(SYNC_WORKFLOW, 'utf8');
	const installStep = getWorkflowStep(workflow, 'Install dependencies');
	const safetyStep = getWorkflowStep(workflow, 'Run publication safety regression tests');
	const validationStep = getWorkflowStep(workflow, 'Validate publication safety before sync');
	const syncStep = getWorkflowStep(workflow, 'Sync skills to Supabase');
	const installIndex = workflow.indexOf('      - name: Install dependencies');
	const safetyIndex = workflow.indexOf('      - name: Run publication safety regression tests');
	const validationIndex = workflow.indexOf('      - name: Validate publication safety before sync');
	const syncIndex = workflow.indexOf('      - name: Sync skills to Supabase');

	assertLockedInstall(installStep);
	assertFocusedSafetyCommand(safetyStep);
	assert.match(validationStep, /node scripts\/validate-skill-publication\.mjs/);
	assert.match(syncStep, /"\$GITHUB_WORKSPACE\/skillstore-cli" skill sync/);
	assert.ok(installIndex < safetyIndex, 'locked install must precede sync safety tests');
	assert.ok(safetyIndex < validationIndex, 'focused tests must precede sync publication validation');
	assert.ok(validationIndex < syncIndex, 'publication validation must precede Supabase writes');
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

test('ordinary /approve remains the generic submission path and never forges an override', () => {
	const workflow = readFileSync(ISSUE_APPROVAL_WORKFLOW, 'utf8');
	const approveWorkflow = readFileSync(APPROVE_SUBMISSION_WORKFLOW, 'utf8');
	const reusableWorkflow = readFileSync(REUSABLE_PROCESS_WORKFLOW, 'utf8');
	const checkJob = getWorkflowJob(workflow, 'check-approval');
	const triggerJob = getWorkflowJob(workflow, 'trigger-processing');

	assert.match(workflow, /issue_comment:\s*\n\s+types: \[created\]/);
	assert.match(checkJob, /github\.event\.issue\.pull_request == null/);
	assert.match(checkJob, /startsWith\(github\.event\.comment\.body, '\/approve'\)/);
	assert.match(
		checkJob,
		/!startsWith\(github\.event\.comment\.body, '\/approve safe-to-publish'\)/,
	);
	assert.match(checkJob, /github\.event\.comment\.user\.type == 'User'/);
	assert.match(triggerJob, /gh workflow run "Approve & Process Submission"/);
	assert.match(triggerJob, /approval_actor=.*github\.event\.comment\.user\.login/);
	assert.match(approveWorkflow, /approval_comment_id:/);
	assert.match(approveWorkflow, /approval_actor:/);
	assert.match(reusableWorkflow, /is_manual_approval:/);
	assert.doesNotMatch(reusableWorkflow, /update-skill-publish-approval\.mjs/);
});

test('pre-audit safe-to-publish comments cannot trigger submission processing', () => {
	const workflow = readFileSync(ISSUE_APPROVAL_WORKFLOW, 'utf8');
	const checkJob = getWorkflowJob(workflow, 'check-approval');
	const safeJob = getWorkflowJob(workflow, 'record-publication-approval');

	assert.match(checkJob, /github\.event\.issue\.pull_request == null/);
	assert.match(
		checkJob,
		/!startsWith\(github\.event\.comment\.body, '\/approve safe-to-publish'\)/,
	);
	assert.match(safeJob, /github\.event\.comment\.user\.type == 'User'/);
	assert.match(safeJob, /startsWith\(github\.event\.comment\.body, '\/approve safe-to-publish'\)/);
	assert.match(safeJob, /record-skill-publish-approval\.mjs/);
	assert.doesNotMatch(safeJob, /gh workflow run "Approve & Process Submission"/);
});

test('safe-to-publish PR comments validate current audited head before the only branch write', () => {
	const workflow = readFileSync(ISSUE_APPROVAL_WORKFLOW, 'utf8');
	const safeJob = getWorkflowJob(workflow, 'record-publication-approval');
	const permissionIndex = safeJob.indexOf('      - name: Check safe approval commenter permission');
	const tokenIndex = safeJob.indexOf('      - name: Generate GitHub App Token');
	const checkoutIndex = safeJob.indexOf('      - name: Checkout trusted approval tooling');
	const installIndex = safeJob.indexOf('      - name: Install trusted tooling dependencies');
	const recordIndex = safeJob.indexOf('      - name: Record publication approval with CAS retry');

	assert.match(safeJob, /startsWith\(github\.event\.comment\.body, '\/approve safe-to-publish'\)/);
	assert.match(safeJob, /github\.event\.comment\.user\.type == 'User'/);
	assert.match(safeJob, /github\.event\.issue\.pull_request != null/);
	assert.match(safeJob, /github\.event\.issue\.state == 'open'/);
	assert.match(safeJob, /contains\(github\.event\.issue\.labels\.\*\.name, 'pending-review'\)/);
	assert.match(safeJob, /collaborators\/.*\/permission/);
	assert.match(safeJob, /write.*maintain.*admin|admin.*maintain.*write/s);
	assert.ok(permissionIndex >= 0 && permissionIndex < tokenIndex);
	assert.ok(tokenIndex < checkoutIndex);
	assert.ok(checkoutIndex < installIndex);
	assert.ok(installIndex < recordIndex);
	const checkoutStep = getWorkflowStep(workflow, 'Checkout trusted approval tooling');
	assert.match(checkoutStep, /ref: \$\{\{ github\.workflow_sha \}\}/);
	assert.match(checkoutStep, /path: trusted-approval-tooling/);
	assert.match(checkoutStep, /persist-credentials: false/);
	assert.doesNotMatch(checkoutStep, /steps\.app-token\.outputs\.token/);
	const installStep = getWorkflowStep(workflow, 'Install trusted tooling dependencies');
	assert.match(installStep, /working-directory: trusted-approval-tooling/);
	assert.match(installStep, /\bnpm ci --ignore-scripts\b/);
	const recordStep = getWorkflowStep(workflow, 'Record publication approval with CAS retry');
	assert.match(recordStep, /working-directory: trusted-approval-tooling/);
	assert.match(recordStep, /node scripts\/record-skill-publish-approval\.mjs/);
	assert.match(recordStep, /--max-attempts 5/);
	assert.match(recordStep, /--comment-id "\$\{\{ github\.event\.comment\.id \}\}"/);
	assert.match(recordStep, /--pr-number "\$\{\{ github\.event\.issue\.number \}\}"/);
	assert.doesNotMatch(safeJob, /Checkout current PR head/);
	assert.doesNotMatch(safeJob, /\bnpm ci\b(?! --ignore-scripts)/);
	assert.doesNotMatch(safeJob, /git (?:reset|clean|stash)|rm -rf/);
	assert.doesNotMatch(safeJob, /gh workflow run|gh issue edit|gh pr edit|reactions|curl|supabase/i);
	assert.doesNotMatch(safeJob, /production|sync|promot/i);
	assert.doesNotMatch(workflow, /record-publication-approval:[\s\S]*cancel-in-progress:\s*true/);
});

test('promotion and sync pass exact current PR identity to unsafe publication validation', () => {
	const promotionWorkflow = readFileSync(PROMOTION_WORKFLOW, 'utf8');
	const syncWorkflow = readFileSync(SYNC_WORKFLOW, 'utf8');
	const promotionStep = getWorkflowStep(
		promotionWorkflow,
		'Find pending skills and commit to skills directory',
	);
	const syncResolveStep = getWorkflowStep(syncWorkflow, 'Resolve exact merged PR for push');
	const syncValidationStep = getWorkflowStep(
		syncWorkflow,
		'Validate publication safety before sync',
	);

	assert.match(
		promotionStep,
		/--current-pr-number "\$\{\{ github\.event\.pull_request\.number \}\}"/,
	);
	assert.match(
		promotionStep,
		/--current-pr-head-sha "\$\{\{ github\.event\.pull_request\.head\.sha \}\}"/,
	);
	assert.match(syncResolveStep, /commits\/\$GITHUB_SHA\/pulls/);
	assert.match(syncResolveStep, /merge_commit_sha.*GITHUB_SHA|GITHUB_SHA.*merge_commit_sha/s);
	assert.match(syncResolveStep, /base\.ref.*main|main.*base\.ref/s);
	assert.match(syncResolveStep, /merged_at/);
	assert.match(syncValidationStep, /--current-pr-number/);
	assert.match(syncValidationStep, /--current-pr-head-sha/);
});

test('CI runs every publication safety regression before auto-fix writes', () => {
	const workflow = readFileSync(VALIDATE_WORKFLOW, 'utf8');
	const installStep = getWorkflowStep(workflow, 'Install dependencies');
	const safetyStep = getWorkflowStep(workflow, 'Run publication safety regression tests');
	const installIndex = workflow.indexOf('      - name: Install dependencies');
	const safetyIndex = workflow.indexOf('      - name: Run publication safety regression tests');
	const integrityIndex = workflow.indexOf('      - name: Validate changed package report integrity');
	const cliDownloadIndex = workflow.indexOf('      - name: Download skillstore CLI for auto-fix');
	const autoFixIndex = workflow.indexOf('      - name: Auto-fix SKILL.md validation errors');

	assert.match(workflow, /validate-skill-publication\.mjs.*--integrity-only.*--changed-since/s);
	assert.match(workflow, /skills\/\*\*\/\*\.md/);
	assert.match(workflow, /pending\/\*\*\/\*\.md/);
	assert.match(workflow, /\.github\/workflows\/issue-approval\.yml/);
	assert.match(workflow, /npm-shrinkwrap\.json/);
	assertLockedInstall(installStep);
	assertFocusedSafetyCommand(safetyStep);
	assert.ok(installIndex < safetyIndex, 'locked install must precede validation safety tests');
	assert.ok(cliDownloadIndex >= 0, 'auto-fix CLI download step must exist');
	assert.ok(autoFixIndex >= 0, 'auto-fix step must exist');
	assert.ok(safetyIndex < cliDownloadIndex);
	assert.ok(safetyIndex < autoFixIndex);
	assert.ok(integrityIndex < cliDownloadIndex);
	assert.ok(integrityIndex < autoFixIndex);
	assert.match(
		workflow,
		/name: Validate changed package report integrity\s+if: \$\{\{ !cancelled\(\) \}\}/,
	);
	assert.match(workflow, /remove-empty-skill-files\.mjs/);
	assert.doesNotMatch(
		getWorkflowStep(workflow, 'Auto-fix SKILL.md validation errors'),
		/rm -rf "\$PARENT_DIR"/,
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
