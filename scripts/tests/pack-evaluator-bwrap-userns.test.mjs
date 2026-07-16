import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const HELPER_PATH = join(REPO_ROOT, 'scripts/configure-pack-evaluator-bwrap.sh');
const HELPER = readFileSync(HELPER_PATH, 'utf8');
const PROFILE = readFileSync(
  join(REPO_ROOT, 'scripts/pack-evaluator-bwrap.apparmor'),
  'utf8',
);
const PRODUCTION = readFileSync(join(REPO_ROOT, '.github/workflows/generate-packs.yml'), 'utf8');
const HOSTED_CI = readFileSync(
  join(REPO_ROOT, '.github/workflows/test-pack-evaluator-bwrap.yml'),
  'utf8',
);

function workflowSection(source, start, end) {
  const startIndex = source.indexOf(start);
  assert.notEqual(startIndex, -1, `missing workflow section ${start}`);
  const endIndex = source.indexOf(end, startIndex + start.length);
  assert.notEqual(endIndex, -1, `missing workflow boundary ${end}`);
  return source.slice(startIndex, endIndex);
}

test('AppArmor policy grants userns only to the root-owned bwrap path', () => {
  assert.match(PROFILE, /profile pack-production-bwrap \/usr\/bin\/bwrap flags=\(unconfined\) \{/);
  assert.match(PROFILE, /^\s*userns,\s*$/m);
  assert.doesNotMatch(PROFILE, /capability|network|mount|ptrace|signal|\/\*\*/);
});

test('root helper keeps the global restriction and loads only the scoped profile', () => {
  const syntax = spawnSync('bash', ['-n', HELPER_PATH], { encoding: 'utf8' });
  assert.equal(syntax.status, 0, syntax.stderr);
  assert.match(HELPER, /EUID[\s\S]*-ne 0/);
  assert.match(HELPER, /ubuntu:24\.04/);
  assert.match(HELPER, /bubblewrap 0\.9\.0/);
  assert.match(HELPER, /kernel\.apparmor_restrict_unprivileged_userns/);
  assert.match(HELPER, /test "\$RESTRICTED_USERNS_BEFORE" = '1'/);
  assert.match(HELPER, /test "\$\(sysctl -n kernel\.apparmor_restrict_unprivileged_userns\)" = '1'/);
  assert.match(HELPER, /test "\$MAX_USER_NAMESPACES" -gt 0/);
  assert.match(HELPER, /install -o root -g root -m 0644/);
  assert.match(HELPER, /"\$APPARMOR_PARSER" -Q/);
  assert.match(HELPER, /"\$APPARMOR_PARSER" -r/);
  assert.match(HELPER, /Unprofiled user namespace creation unexpectedly succeeded/);
  assert.doesNotMatch(HELPER, /sysctl\s+(?:-w\s+)?kernel\.apparmor_restrict_unprivileged_userns=0/);
  assert.doesNotMatch(HELPER, /apparmor_restrict_unprivileged_userns\s*=\s*0/);
});

test('real probe matches the executor namespace contract and verifies its closure', () => {
  assert.match(
    HELPER,
    /--unshare-all\s+\\\n\s+--share-net\s+\\\n\s+--unshare-user\s+\\\n\s+--disable-userns\s+\\\n\s+--cap-drop ALL/,
  );
  for (const required of ['--tmpfs /', '--proc /proc', '--dev /dev', '--tmpfs /run']) {
    assert.match(HELPER, new RegExp(required.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  }
  assert.match(HELPER, /\/proc\/self\/uid_map/);
  assert.match(HELPER, /\^Cap\(Inh\|Prm\|Eff\|Bnd\|Amb\):\$/);
  assert.match(HELPER, /test -x \/opt\/pack-evaluator\/runtime\/bin\/node/);
  assert.match(HELPER, /\/opt\/pack-evaluator\/runtime\/bin\/node --version/);
  assert.match(HELPER, /! test -w \/opt\/pack-evaluator\/runtime/);
  assert.match(HELPER, /! test -e \/opt\/pack-evaluator\/(?:bin|lib|input|results)/);
  assert.match(HELPER, /! test -e "\$OUTER_WORKSPACE"/);
  assert.match(HELPER, /! test -e "\/proc\/\$OUTER_PID"/);
  assert.match(HELPER, /! env \| grep -Eq/);
  assert.match(HELPER, /if \/usr\/bin\/unshare --user \/usr\/bin\/true/);
  assert.doesNotMatch(HELPER, /--(?:ro-)?bind \/ \/|--dev-bind \/ \/|--cap-add/);
});

test('production configures and proves bwrap before the only Helm secret step', () => {
  const evaluate = workflowSection(PRODUCTION, '  evaluate:', '  persist:');
  const helperIndex = evaluate.indexOf('scripts/configure-pack-evaluator-bwrap.sh');
  const helperInputIndex = evaluate.indexOf('PACK_EVALUATOR_OUTER_WORKSPACE="$GITHUB_WORKSPACE"');
  const userIndex = evaluate.indexOf('useradd --create-home --home-dir /home/packeval');
  const secretStepIndex = evaluate.indexOf('PACK_EVALUATOR_HELM_API_KEY: ${{ secrets.PACK_EVALUATOR_HELM_API_KEY }}');

  assert.match(evaluate, /runs-on: ubuntu-24\.04/);
  assert.ok(userIndex >= 0);
  assert.ok(helperInputIndex > userIndex);
  assert.ok(helperIndex > userIndex);
  assert.ok(secretStepIndex > helperIndex);
  assert.ok(helperIndex > helperInputIndex);
  assert.doesNotMatch(evaluate.slice(0, secretStepIndex), /secrets\./);
});

test('hosted proof is pinned, secret-free, and invokes the production helper', () => {
  assert.match(HOSTED_CI, /runs-on: ubuntu-24\.04/);
  assert.match(HOSTED_CI, /timeout-minutes: 10/);
  assert.match(HOSTED_CI, /permissions:\n  contents: read/);
  assert.match(HOSTED_CI, /persist-credentials: false/);
  assert.match(HOSTED_CI, /apt-get install --yes --no-install-recommends apparmor bubblewrap util-linux/);
  assert.match(HOSTED_CI, /useradd --create-home --home-dir \/home\/packeval/);
  assert.match(HOSTED_CI, /\/opt\/pack-evaluator\/runtime\/bin\/node/);
  assert.match(HOSTED_CI, /scripts\/configure-pack-evaluator-bwrap\.sh/);
  assert.doesNotMatch(HOSTED_CI, /secrets\.|pull_request_target|self-hosted/);
});
