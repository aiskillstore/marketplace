import { test, type TestContext } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const cli = fileURLToPath(new URL('../scripts/birdview.mjs', import.meta.url));
function project(t: TestContext) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'birdview-mode-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  return root;
}
function run(root: string, ...args: string[]) {
  return spawnSync(process.execPath, [cli, 'mode', ...args, '--project', root], { encoding: 'utf8' });
}

test('Claude mode preserves its rules and leaves AGENTS.md untouched; DeepSeek uses AGENTS.md', (t) => {
  const root = project(t);
  const agents = path.join(root, 'AGENTS.md');
  const claude = path.join(root, 'CLAUDE.md');
  fs.writeFileSync(agents, 'Existing agent rules\n');
  fs.writeFileSync(claude, '\uFEFF# Claude rules\r\n');
  assert.equal(run(root, 'on-demand', '--agent', 'claude-code').status, 0);
  assert.equal(fs.readFileSync(agents, 'utf8'), 'Existing agent rules\n');
  const original = fs.readFileSync(claude, 'utf8');
  assert.ok(original.startsWith('\uFEFF# Claude rules\r\n'));
  assert.match(run(root, '--agent', 'claude-code').stdout, /^on-demand/);
  assert.equal(run(root, 'on-demand', '--agent', 'claude-code').status, 0);
  assert.equal(fs.readFileSync(claude, 'utf8'), original);
  assert.equal(run(root, 'on-demand', '--agent', 'deepseek').status, 0);
  assert.match(fs.readFileSync(agents, 'utf8'), /Birdview mode: on-demand/);
  assert.equal(run(root, 'on-demand', '--agent', 'unknown').status, 1);
  fs.writeFileSync(claude, '<!-- birdview:mode:start -->');
  assert.equal(run(root, 'on-demand', '--agent', 'claude-code').status, 1);
  assert.equal(fs.readFileSync(claude, 'utf8'), '<!-- birdview:mode:start -->');
});

test('doctor executes the installed validator and renders in memory without writing', (t) => {
  const root = project(t);
  const result = spawnSync(process.execPath, [cli, 'doctor'], { cwd: root, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /OK: example validation/);
  assert.deepEqual(fs.readdirSync(root), []);
  assert.equal(spawnSync(process.execPath, [cli, 'doctor', '--unknown']).status, 1);
});

test('doctor rejects silent, malformed and failed installed CLI responses', t => {
  const root = project(t);
  const scripts = path.join(root, 'scripts');
  fs.mkdirSync(scripts);
  fs.mkdirSync(path.join(root, 'examples'));
  fs.copyFileSync(cli, path.join(scripts, 'birdview.mjs'));
  fs.writeFileSync(path.join(root, 'examples/architecture.json'), '{}');
  fs.writeFileSync(path.join(scripts, 'render.mjs'), "export const renderArchitecture = () => '<html></html>';\n");
  const cases = [
    ['', /no valid JSON report/],
    ["console.log('not-json')", /no valid JSON report/],
    ['console.log(JSON.stringify({ok:true}))', /did not confirm/],
    ["process.stderr.write('broken entry'); process.exitCode = 1", /broken entry/],
  ] as const;
  for (const [source, expected] of cases) {
    fs.writeFileSync(path.join(scripts, 'validate.mjs'), source);
    const result = spawnSync(process.execPath, [path.join(scripts, 'birdview.mjs'), 'doctor'], { encoding: 'utf8' });
    assert.equal(result.status, 1);
    assert.match(result.stderr, expected);
    assert.doesNotMatch(result.stdout, /OK:/);
  }
});

test('default mode is read-only; explicit selection creates a project rule', (t) => {
  const root = project(t);
  assert.match(run(root).stdout, /on-demand.*default/);
  assert.equal(fs.existsSync(path.join(root, 'AGENTS.md')), false);
  assert.equal(run(root, 'on-demand').status, 0);
  assert.match(run(root).stdout, /^on-demand\n/);
});

test('foundation survives mode switches; setup upgrades legacy on-demand without enabling maps', (t) => {
  const root = project(t);
  const file = path.join(root, 'AGENTS.md');
  fs.writeFileSync(file, '# User rules\n<!-- birdview:mode:start -->\nBirdview mode: on-demand\nlegacy\n<!-- birdview:mode:end -->\nKeep this.');
  assert.match(run(root).stdout, /Foundation: not installed/);
  const setup = () => spawnSync(process.execPath, [cli, 'setup', '--project', root], { encoding: 'utf8' });
  assert.equal(setup().status, 0);
  const installed = fs.readFileSync(file, 'utf8');
  assert.match(installed, /Birdview mode: on-demand/);
  assert.match(installed, /even when the Birdview skill is not activated/);
  assert.match(installed, /do not require reading the skill/);
  assert.match(run(root).stdout, /Foundation: on/);
  assert.equal(setup().status, 0);
  assert.equal(fs.readFileSync(file, 'utf8'), installed);
  assert.equal(run(root, 'on-demand').status, 0);
  assert.match(run(root).stdout, /Foundation: on/);
  assert.equal(run(root, 'off').status, 0);
  assert.match(run(root).stdout, /Foundation: off/);
  assert.doesNotMatch(fs.readFileSync(file, 'utf8'), /For every authorized coding task/);
  assert.equal(setup().status, 0);
  assert.match(run(root).stdout, /^off/);
  const before = fs.readFileSync(file, 'utf8');
  const uninstall = () => spawnSync(process.execPath, [cli, 'uninstall', '--project', root], { encoding: 'utf8' });
  assert.equal(uninstall().status, 0);
  assert.equal(fs.readFileSync(file, 'utf8'), before.replace(/<!-- birdview:mode:start -->[\s\S]*?<!-- birdview:mode:end -->/, ''));
  assert.equal(uninstall().status, 0);
  assert.match(run(root).stdout, /Foundation: not installed/);
});

test('setup and uninstall preserve host boundaries and reject damaged files', (t) => {
  const root = project(t);
  const agents = path.join(root, 'AGENTS.md');
  fs.writeFileSync(agents, 'User rules');
  const invoke = (command: string, agent: string) => spawnSync(process.execPath, [cli, command, '--project', root, '--agent', agent], { encoding: 'utf8' });
  assert.equal(invoke('setup', 'claude-code').status, 0);
  assert.match(run(root, '--agent', 'claude-code').stdout, /Foundation: on/);
  assert.equal(fs.readFileSync(agents, 'utf8'), 'User rules');
  assert.equal(invoke('uninstall', 'claude-code').status, 0);
  assert.equal(invoke('setup', 'deepseek').status, 0);
  assert.match(run(root).stdout, /Foundation: on/);
  fs.writeFileSync(agents, '<!-- birdview:mode:start -->');
  for (const command of ['setup', 'uninstall']) {
    assert.equal(invoke(command, 'codex').status, 1);
    assert.equal(fs.readFileSync(agents, 'utf8'), '<!-- birdview:mode:start -->');
  }
});

test('switching preserves surrounding UTF-8 text, BOM and CRLF; repeat is idempotent', (t) => {
  const root = project(t);
  const file = path.join(root, 'AGENTS.md');
  const prefix = '\uFEFF# 用户规则\r\n不得覆盖。\r\n';
  fs.writeFileSync(file, prefix);
  assert.equal(run(root, 'on-demand').status, 0);
  const automatic = fs.readFileSync(file, 'utf8');
  assert.ok(automatic.startsWith(prefix));
  assert.equal(automatic.replaceAll('\r\n', '').includes('\n'), false);
  fs.appendFileSync(file, '\r\n其他规则保持原样。');
  assert.equal(run(root, 'on-demand').status, 0);
  const manual = fs.readFileSync(file, 'utf8');
  assert.ok(manual.startsWith(prefix));
  assert.ok(manual.endsWith('\r\n其他规则保持原样。'));
  assert.match(run(root).stdout, /^on-demand\n/);
  assert.equal(run(root, 'on-demand').status, 0);
  assert.equal(fs.readFileSync(file, 'utf8'), manual);
  assert.equal(manual.split('<!-- birdview:mode:start -->').length, 2);
  const local = spawnSync(process.execPath, [cli, 'mode'], { cwd: root, encoding: 'utf8' });
  assert.equal(local.status, 0);
  assert.match(local.stdout, /^on-demand\n/);
});

test('malformed, duplicate blocks and invalid arguments fail without writing', (t) => {
  const root = project(t);
  const file = path.join(root, 'AGENTS.md');
  for (const original of ['user\n<!-- birdview:mode:start -->', '<!-- birdview:mode:end -->\n<!-- birdview:mode:start -->', '<!-- birdview:mode:start -->\nunknown\n<!-- birdview:mode:end -->']) {
    fs.writeFileSync(file, original);
    assert.equal(run(root, 'on-demand').status, 1);
    assert.equal(fs.readFileSync(file, 'utf8'), original);
  }
  fs.writeFileSync(file, 'keep');
  assert.equal(run(root, 'invalid').status, 1);
  assert.equal(fs.readFileSync(file, 'utf8'), 'keep');
  assert.equal(run(root, 'on-demand').status, 0);
  const duplicate = fs.readFileSync(file, 'utf8').repeat(2);
  fs.writeFileSync(file, duplicate);
  assert.equal(run(root, 'on-demand').status, 1);
  assert.equal(fs.readFileSync(file, 'utf8'), duplicate);
  fs.unlinkSync(file);
  fs.mkdirSync(file);
  assert.equal(run(root, 'on-demand').status, 1);
  assert.ok(fs.statSync(file).isDirectory());
});

test('auto is opt-in; setup preserves it and switching back stops automatic instructions', (t) => {
  const root = project(t);
  const file = path.join(root, 'AGENTS.md');
  fs.writeFileSync(file, '# Keep\n');
  const setup = () => spawnSync(process.execPath, [cli, 'setup', '--project', root], { encoding: 'utf8' });
  assert.equal(setup().status, 0);
  assert.match(run(root).stdout, /^on-demand/);
  assert.equal(run(root, 'auto').status, 0);
  assert.match(fs.readFileSync(file, 'utf8'), /before every code-changing task/);
  assert.equal(setup().status, 0);
  assert.match(run(root).stdout, /^auto/);
  assert.equal(run(root, 'on-demand').status, 0);
  assert.doesNotMatch(fs.readFileSync(file, 'utf8'), /before every code-changing task/);
  assert.ok(fs.readFileSync(file, 'utf8').startsWith('# Keep\n'));
  assert.equal(setup().status, 0);
  assert.match(run(root).stdout, /^on-demand/);
});
