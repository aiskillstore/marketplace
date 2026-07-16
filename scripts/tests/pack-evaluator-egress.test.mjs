import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const HELPER_PATH = join(REPO_ROOT, 'scripts/configure-pack-evaluator-egress.sh');
const HELPER = readFileSync(HELPER_PATH, 'utf8');
const PRODUCTION = readFileSync(join(REPO_ROOT, '.github/workflows/generate-packs.yml'), 'utf8');
const HOSTED = readFileSync(join(REPO_ROOT, '.github/workflows/test-pack-evaluator-bwrap.yml'), 'utf8');

test('egress helper is bounded to one UID, one IPv4 address, and one TCP port', () => {
  const syntax = spawnSync('bash', ['-n', HELPER_PATH], { encoding: 'utf8' });
  assert.equal(syntax.status, 0, syntax.stderr);
  assert.match(HELPER, /EVALUATOR_USER=packeval/);
  assert.match(HELPER, /PROXY_ADDRESS=127\.0\.0\.1/);
  assert.match(HELPER, /PROXY_PORT=18765/);
  assert.match(HELPER, /-m owner --uid-owner "\$EVALUATOR_UID"/);
  assert.match(HELPER, /prepare_guard iptables "\$IPV4_GUARD_CHAIN"/);
  assert.match(HELPER, /prepare_guard ip6tables "\$IPV6_GUARD_CHAIN"/);
  assert.match(HELPER, /-p tcp -d "\$PROXY_ADDRESS\/32" --dport "\$PROXY_PORT" -j ACCEPT/);
  assert.match(HELPER, /iptables .* -j REJECT --reject-with icmp-admin-prohibited/);
  assert.match(HELPER, /ip6tables .* -j REJECT --reject-with icmp6-adm-prohibited/);
  assert.doesNotMatch(HELPER, /-P OUTPUT|--flush|\s-F OUTPUT|ACCEPT.*0\.0\.0\.0|ACCEPT.*::\/0/);
  const guardIndex = HELPER.indexOf('prepare_guard iptables');
  const flushIndex = HELPER.indexOf('iptables -w 5 -F "$IPV4_CHAIN"');
  const policyJumpIndex = HELPER.indexOf('iptables -w 5 -I OUTPUT 1');
  const guardRemovalIndex = HELPER.indexOf('finish_guard iptables');
  assert.ok(guardIndex > 0 && guardIndex < flushIndex);
  assert.ok(flushIndex < policyJumpIndex && policyJumpIndex < guardRemovalIndex);
});

test('production installs and proves egress restrictions before the only Helm secret step', () => {
  const evaluateStart = PRODUCTION.indexOf('  evaluate:');
  const persistStart = PRODUCTION.indexOf('  persist:', evaluateStart);
  const evaluate = PRODUCTION.slice(evaluateStart, persistStart);
  const helperIndex = evaluate.indexOf('configure-pack-evaluator-egress.sh');
  const secretIndex = evaluate.indexOf('PACK_EVALUATOR_HELM_API_KEY: ${{ secrets.PACK_EVALUATOR_HELM_API_KEY }}');
  assert.match(evaluate, /apparmor bubblewrap ffmpeg iptables poppler-utils ripgrep util-linux/);
  assert.ok(helperIndex > 0 && helperIndex < secretIndex);
  assert.match(evaluate, /169\.254\.169\.254/);
  assert.match(evaluate, /127\.0\.0\.1:18764/);
  assert.match(evaluate, /\[::1\]:18765/);
  assert.match(evaluate, /IPV4_REJECT_AFTER.*-gt.*IPV4_REJECT_BEFORE/);
  assert.match(evaluate, /IPV6_REJECT_AFTER.*-gt.*IPV6_REJECT_BEFORE/);
});

test('hosted proof applies the same helper before real pinned CLI preflight', () => {
  const helperIndex = HOSTED.indexOf('configure-pack-evaluator-egress.sh');
  const preflightIndex = HOSTED.indexOf('bash "$GITHUB_WORKSPACE/scripts/pack-evaluator-preflight.sh"');
  assert.ok(helperIndex > 0 && helperIndex < preflightIndex);
  assert.match(HOSTED, /169\.254\.169\.254/);
  assert.match(HOSTED, /127\.0\.0\.1:18764/);
  assert.match(HOSTED, /\[::1\]:18765/);
  assert.match(HOSTED, /IPV4_ACCEPT_AFTER.*-gt.*IPV4_ACCEPT_BEFORE/);
  assert.equal((HOSTED.match(/configure-pack-evaluator-egress\.sh"/g) ?? []).length >= 2, true);
  assert.match(HOSTED, /\/v1\/messages/);
  assert.match(HOSTED, /\/v1\/responses/);
});
