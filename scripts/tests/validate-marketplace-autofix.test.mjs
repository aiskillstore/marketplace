import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';

const workflow = readFileSync('.github/workflows/validate-marketplace.yml', 'utf8');

function runBlock(stepName) {
  const marker = `      - name: ${stepName}\n`;
  const start = workflow.indexOf(marker);
  assert.ok(start >= 0, `missing step ${stepName}`);
  const run = workflow.indexOf('        run: |\n', start);
  assert.ok(run >= 0, `missing run block for ${stepName}`);
  const end = workflow.indexOf('\n      - name:', run + 1);
  const lines = workflow.slice(run + '        run: |\n'.length, end < 0 ? undefined : end).split('\n');
  return lines.map((line) => line.startsWith('          ') ? line.slice(10) : line).join('\n');
}

const rebind = runBlock('Rebind reports to auto-fixed SKILL.md artifacts');
const commitSkill = runBlock('Commit auto-fixed SKILL.md artifacts locally');
const commitReport = runBlock('Commit auto-fixed skill-report.json files locally');
const publish = runBlock('Publish validated auto-fixes');

test('auto-fix binds final artifact hashes before creating local commits', () => {
  assert.match(rebind, /git diff --name-only -z --diff-filter=ACMRT HEAD/);
  assert.match(rebind, /scripts\/rebind-skill-report-hashes\.mjs/);
  assert.match(rebind, /--skill-paths-file/);
  assert.doesNotMatch(commitSkill, /git push|gh pr create/);
  assert.doesNotMatch(commitReport, /git push|git pull|git reset|git cherry-pick/);
});

test('publishing updates only the original trusted PR head and fails closed on races', () => {
  assert.match(publish, /test "\$HEAD_REPOSITORY" = "\$REPOSITORY"/);
  assert.match(publish, /test "\$HEAD_REF" = "\$BRANCH"/);
  assert.match(publish, /git check-ref-format --branch "\$BRANCH"/);
  assert.match(publish, /test "\$REMOTE_SHA" = "\$AUTO_FIX_BASE_SHA"/);
  assert.match(publish, /git push origin "HEAD:refs\/heads\/\$BRANCH"/);
  assert.doesNotMatch(publish, /git pull|git rebase|git reset|git cherry-pick|\|\| true/);
  assert.match(publish, /if \[ "\$EVENT_NAME" = "pull_request" \]; then[\s\S]*else[\s\S]*gh pr create/);
});

function executePullRequestPublish({ headRepository = 'aiskillstore/marketplace', pushStatus = 0 } = {}) {
  const root = mkdtempSync(join(tmpdir(), 'validate-autofix-publish-'));
  const log = join(root, 'commands.log');
  const script = `${publish.replace('FIX_BRANCH="fix/validated-marketplace-artifacts-${{ github.run_id }}"', 'FIX_BRANCH="fix/test"')}\n`;
  const harness = `
git() {
  printf 'git %s\\n' "$*" >> "$FAKE_LOG"
  if [ "$1" = rev-parse ] && [ "$2" = HEAD ]; then printf '%s\\n' final; return 0; fi
  if [ "$1" = ls-remote ]; then printf '%s\\trefs/heads/%s\\n' "$AUTO_FIX_BASE_SHA" "$BRANCH"; return 0; fi
  if [ "$1" = push ]; then return "$FAKE_PUSH_STATUS"; fi
  return 0
}
gh() { printf 'gh %s\\n' "$*" >> "$FAKE_LOG"; return 0; }
${script}`;
  writeFileSync(join(root, 'run.sh'), harness);
  const result = spawnSync('bash', [join(root, 'run.sh')], {
    encoding: 'utf8',
    env: {
      ...process.env,
      APP_TOKEN: 'fixture-token',
      AUTO_FIX_BASE_SHA: 'base',
      BRANCH: 'submission/fixture',
      EVENT_NAME: 'pull_request',
      FAKE_LOG: log,
      FAKE_PUSH_STATUS: String(pushStatus),
      GH_TOKEN: 'fixture-token',
      HEAD_REF: 'submission/fixture',
      HEAD_REPOSITORY: headRepository,
      REPOSITORY: 'aiskillstore/marketplace',
    },
  });
  const commands = readFileSync(log, 'utf8');
  rmSync(root, { recursive: true, force: true });
  return { result, commands };
}

test('same-repository PR publishes the final commit to its original head', () => {
  const { result, commands } = executePullRequestPublish();
  assert.equal(result.status, 0, result.stderr);
  assert.match(commands, /git push origin HEAD:refs\/heads\/submission\/fixture/);
  assert.doesNotMatch(commands, /gh pr create/);
});

test('fork PR and write-permission failure are terminal and never create a superset PR', () => {
  const fork = executePullRequestPublish({ headRepository: 'external/fork' });
  assert.notEqual(fork.result.status, 0);
  assert.doesNotMatch(fork.commands, /git push|gh pr create/);

  const denied = executePullRequestPublish({ pushStatus: 1 });
  assert.notEqual(denied.result.status, 0);
  assert.match(denied.commands, /git push origin HEAD:refs\/heads\/submission\/fixture/);
  assert.doesNotMatch(denied.commands, /gh pr create/);
});
