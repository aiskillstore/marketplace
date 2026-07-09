import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '..', '..');
const AUDIT_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'audit-skills.yml');

test('audit workflow wires risk-level filtering from dispatch input to CLI shards', () => {
	const workflow = readFileSync(AUDIT_WORKFLOW, 'utf8');

	assert.match(workflow, /risk_level:\n\s+description: 'Only audit skills whose existing report risk level matches this comma-separated list'/);
	assert.match(workflow, /RISK_LEVEL: \$\{\{ inputs\.risk_level \}\}/);
	assert.match(workflow, /const filter = \(process\.env\.RISK_LEVEL \|\| ''\)/);
	assert.match(workflow, /const risk = report\?\.security_audit\?\.risk_level \|\| report\?\.skill\?\.risk_level/);
	assert.match(workflow, /RISK_LEVEL_FLAG="--risk-level \$\{\{ inputs\.risk_level \}\}"/);
	assert.match(workflow, /\$RISK_LEVEL_FLAG \\\n\s+--offset \$\{\{ matrix\.offset \}\}/);
	assert.match(workflow, /\| Risk Filter \| \\\`\$\{RISK_LEVEL:-all\}\\\` \|/);
});

test('audit workflow skips PR creation when no skills were successfully updated', () => {
	const workflow = readFileSync(AUDIT_WORKFLOW, 'utf8');

	assert.match(workflow, /if \[ "\$TOTAL_UPDATED" -eq 0 \]; then/);
	assert.match(workflow, /No successfully updated skills; skipping audit PR to avoid timestamp-only failed-analysis churn/);
	assert.match(workflow, /echo "has_changes=false" >> \$GITHUB_OUTPUT/);
});
