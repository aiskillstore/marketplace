// Release-regression suite: everything that has broken a release before, plus
// the invariants a release must never silently change — the catalogue, the
// version, the packaging and the repository's own cleanliness.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { CATALOGUE, VERSION, run as runInProcess } from '../bin/check.mjs';
import { EDITORIAL_RULES } from '../lib/rules.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cli = path.join(root, 'bin', 'check.mjs');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-release-'));
let sequence = 0;

const write = (name, value) => {
  const file = path.join(tmp, name);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, value);
  return file;
};
const unique = (ext, value = 'x') => write(`fixture-${sequence++}.${ext}`, value);
const config = write('config.json', '{}');
// A caller that passes its own `--config` must keep it: appending a second
// one would silently win and mask the configuration under test.
const run = (...args) => spawnSync(process.execPath,
  [cli, ...args, ...(args.some(arg => arg === '--config' || arg.startsWith('--config=')) ? [] : ['--config', config])],
  // The robustness fixtures below produce deliberately huge reports (the
  // long-line stress input yields tens of thousands of findings), so the
  // default 1 MB spawn buffer would truncate stdout to nothing.
  { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
const ids = result => {
  try { return [...new Set(JSON.parse(result.stdout).findings.map(f => f.ruleId))].sort(); }
  catch { return assert.fail(result.stderr || result.stdout); }
};
const textFixture = (line, ext = 'txt') => unique(ext, `${line}\n`);

// --- catalogue ---------------------------------------------------------------

const EXPECTED_IDS = [
  'UE-SP001', 'UE-SP002', 'UE-SP003', 'UE-TE001', 'UE-TE002', 'UE-TE003', 'UE-TE004', 'UE-TE005',
  'UE-NU001', 'UE-NU002', 'UE-RE001', 'UE-RE002', 'UE-RE003', 'UE-RE004', 'UE-RE005',
  'UE-DI001', 'UE-CL001', 'UE-CL002', 'UE-CL003', 'UE-DP001', 'UE-EO001', 'UE-EO002', 'UE-EO003', 'UE-EO004', 'UE-EO005',
  'UE-AX001', 'UE-AX002', 'UE-SE001', 'UE-SE002', 'UE-SE003', 'UE-SE004',
  'UE-HS001', 'UE-HS002', 'UE-HS003', 'UE-DM001', 'UE-RE006', 'UE-RE007', 'UE-RE008',
  'UE-GR001', 'UE-GR002', 'UE-GR003', 'UE-GR004',
  'UE-HR001', 'UE-HR002', 'UE-HR003', 'UE-HR004', 'UE-HR005', 'UE-HR006', 'UE-HR007', 'UE-HR008', 'UE-HR009',
  'UE-GL001', 'UE-GL002',
];
assert.equal(CATALOGUE.catalogueVersion, 1);
assert.deepEqual(CATALOGUE.rules.map(rule => rule.id), EXPECTED_IDS, 'catalogue order and membership');
for (const rule of CATALOGUE.rules) {
  for (const key of ['id', 'severity', 'category', 'confidence', 'scope', 'status', 'profile',
    'extensibility', 'guardNotes', 'summary']) {
    assert(Object.hasOwn(rule, key), `${rule.id} is missing ${key}`);
  }
  assert(!('surface' in rule), `${rule.id}: "surface" was renamed to "scope"`);
  if (rule.profile === null) {
    assert(['spelling', 'terminology', 'numerals', 'register', 'agent-review', 'diplomacy',
      'hate-speech', 'discriminatory', 'grammar'].includes(rule.category),
      `${rule.id}: editorial category ${rule.category}`);
  } else {
    assert(['publishing', 'accessibility', 'security'].includes(rule.profile), `${rule.id} profile`);
  }
}

// The engine and the catalogue must describe exactly the same editorial rules.
assert.deepEqual(Object.keys(EDITORIAL_RULES).sort(),
  CATALOGUE.rules.filter(rule => rule.profile === null).map(rule => rule.id).sort(),
  'editorial rules in lib/rules.mjs and rules/catalogue.json disagree');
for (const [id, meta] of Object.entries(EDITORIAL_RULES)) {
  const rule = CATALOGUE.rules.find(entry => entry.id === id);
  assert.equal(rule.severity, meta.severity, `${id} severity`);
  assert.equal(rule.category, meta.category, `${id} category`);
  assert.equal(rule.confidence, meta.confidence, `${id} confidence`);
}
// Judgement rules are warnings: they must never fail a build on their own.
for (const id of ['UE-RE002', 'UE-RE003', 'UE-DI001', 'UE-CL001']) {
  assert.equal(CATALOGUE.rules.find(rule => rule.id === id).category, 'agent-review', id);
}

// --- version and packaging metadata -----------------------------------------

const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const versionFile = fs.readFileSync(path.join(root, 'VERSION'), 'utf8').trim();
const changelog = fs.readFileSync(path.join(root, 'CHANGELOG.md'), 'utf8');
const skill = fs.readFileSync(path.join(root, 'SKILL.md'), 'utf8');

assert.equal(pkg.version, VERSION, 'package.json version');
assert.equal(versionFile, VERSION, 'VERSION file');
assert(new RegExp(`^## ${VERSION.replace(/\./g, '\\.')} `, 'm').test(changelog), `CHANGELOG has a ${VERSION} entry`);
assert(skill.includes(`version: "${VERSION}"`), 'SKILL.md frontmatter version');
for (const entry of ['bin', 'lib', 'config', 'rules', 'commands', 'VERSION', 'SKILL.md', 'USER-GUIDE.md']) {
  assert(pkg.files.includes(entry), `package.json files must include ${entry}`);
}
assert.equal(pkg.license, 'MIT');
assert.equal(pkg.type, 'module');
assert.equal(pkg.engines.node, '>=18');

// --- doc truth: the --fix boundary claims -----------------------------------
// The SKILL.md fix list and the UE-RE005 claim in rules/register.md both went
// stale once — prose promised behaviour the engine does not have. These locks
// pin the wording to the code's actual fixable set.
{
  const fixPara = skill.split('\n').find(line => line.startsWith('Never use `--fix`'));
  assert(fixPara, 'SKILL.md must keep its --fix boundary paragraph');
  for (const item of ['British spelling', 'per cent', 'en-dash ranges',
    'the United States', 'a doubled word', 'a space before punctuation',
    'a missing space between sentences']) {
    assert(fixPara.includes(item), `SKILL.md --fix list must mention ${item}`);
  }
  assert(!fixPara.includes('exclamation marks) in'),
    'SKILL.md must not claim exclamation marks are --fix-able');
  const registerPage = fs.readFileSync(path.join(root, 'rules', 'register.md'), 'utf8');
  const re005Line = registerPage.split('\n').find(line => line.startsWith('- **UE-RE005**'));
  assert(re005Line, 'rules/register.md must document UE-RE005');
  assert(re005Line.includes('report-only') && !re005Line.includes('fixable'),
    'rules/register.md must call UE-RE005 report-only, never fixable');
}

const version = run('--version');
assert.equal(version.status, 0, version.stderr);
assert.equal(version.stdout.trim(), `un-editorial-check ${VERSION}`);

for (const file of ['VERSION', 'config/example.un-editorial.json', '.github/workflows/ci.yml',
  'skills.sh.json', 'CONTRIBUTING.md', 'SECURITY.md', 'CODE_OF_CONDUCT.md', 'MAINTAINING.md',
  'rules/catalogue.json', 'config/profiles/un-v1.json', 'config/profiles/publishing.json',
  'config/profiles/accessibility.json', 'config/profiles/security.json', 'lib/cli.mjs']) {
  assert(fs.existsSync(path.join(root, file)), `missing ${file}`);
}

const ci = fs.readFileSync(path.join(root, '.github/workflows/ci.yml'), 'utf8');
assert(!/@v\d/.test(ci), 'GitHub Actions must be pinned to full SHAs, not version tags');
for (const command of ['npm run check:syntax', 'npm test', 'npm pack --dry-run', 'node bin/check.mjs', '--self-scan']) {
  assert(ci.includes(command), `CI must run: ${command}`);
}

// --- exit codes ---------------------------------------------------------------

{
  const clean = textFixture('The organisation reports the figure.');
  assert.equal(run(clean).status, 0, 'a clean file exits 0');
  const warning = textFixture('Coverage was 1990-2025.');
  assert.equal(run(warning).status, 0, 'warnings alone exit 0');
  const error = textFixture('The color publishes an annual report.');
  assert.equal(run(error).status, 1, 'error-severity findings exit 1');
  assert.equal(run('--format', 'xml', clean).status, 2, 'usage errors exit 2');
  // Audit findings never change the exit code.
  const audit = unique('html', '<!doctype html><html lang="en"><head><title>x</title></head><body></body></html>');
  assert.equal(run(audit, '--profile', 'publishing').status, 0, 'audits never fail the run');
}

// --- --fix: protected material ------------------------------------------------

// Bare occurrences must be fixable and protected ones untouched. The bare
// words are non-conflict map entries (color): the -ize/-ise conflict family
// is a profile choice and is never rewritten by default.
const PROTECTED_FIXES = [
  ['The color inside <cite>Cite organization</cite> and color outside.',
    'The colour inside <cite>Cite organization</cite> and colour outside.'],
  ['color <!-- organization --> color', 'Colour <!-- organization --> colour'],
  ['<script>organization</script> color', '<script>organization</script> colour'],
  ['<style>organization</style> color', '<style>organization</style> colour'],
  ['> organization\n\ncolor', '> organization\n\nColour'],
  ['`organization` and color', '`organization` and colour'],
  ['"Color" and color', '"Color" and colour'],
  ['“Color” and color', '“Color” and colour'],
  ['https://example.test/organization and color', 'https://example.test/organization and colour'],
  ['./organization and color', './organization and colour'],
];
for (const [input, expected] of PROTECTED_FIXES) {
  const file = textFixture(input);
  const before = fs.readFileSync(file, 'utf8');
  const preview = run(file, '--fix');
  assert.equal(preview.status, 1, `preview must keep reporting: ${input}\n${preview.stdout}`);
  assert.equal(fs.readFileSync(file, 'utf8'), before, `preview wrote to ${input}`);
  const applied = run(file, '--fix', '--apply');
  assert.equal(applied.status, 0, `apply: ${input}\n${applied.stdout}\n${applied.stderr}`);
  assert.equal(fs.readFileSync(file, 'utf8'), `${expected}\n`, input);
}

// --- audit rules: opt-in, context aware ---------------------------------------

{
  const sinks = [
    'el.innerHTML = "static";',
    'el.outerHTML = value;',
    'sink = "safe"; el.innerHTML =\n localValue;',
    // `//` inside a string is not a comment, so this sink is still live.
    'const u = "https://example.test/"; el.innerHTML = u;',
  ];
  for (const code of sinks) {
    const result = run(unique('mjs', code), '--format', 'json', '--profile', 'security');
    assert(ids(result).includes('UE-SE001'), `${code}\n${result.stdout}`);
  }
  // A commented-out sink is not live code.
  {
    const result = run(unique('mjs', '// el.innerHTML = value;'), '--format', 'json', '--profile', 'security');
    assert.deepEqual(ids(result), [], 'commented-out sinks must not be reported');
  }
  for (const code of ['eval(code);', 'const F = new Function("return 1");']) {
    const result = run(unique('mjs', code), '--format', 'json', '--profile', 'security');
    assert(ids(result).includes('UE-SE004'), code);
  }
}
{
  const shouldFlag = [
    ['script', '<script src="https://cdn.test/lib.js"></script>', 'UE-SE002'],
    ['stylesheet', '<link rel="stylesheet" href="https://cdn.test/a.css">', 'UE-SE002'],
    ['no opener', '<a href="https://example.test" target="_blank">Report</a>', 'UE-SE003'],
  ];
  for (const [label, html, rule] of shouldFlag) {
    const result = run(unique('html', html), '--format', 'json', '--profile', 'security');
    assert(ids(result).includes(rule), `${label} must be reported: ${result.stdout}`);
  }
  const mustStayQuiet = [
    ['commented asset', '<!-- <script src="https://cdn.test/lib.js"></script> -->'],
    ['canonical link', '<link rel="canonical" href="https://example.test/page">'],
    ['integrity present', '<script src="https://cdn.test/lib.js" integrity="sha384-abc" crossorigin></script>'],
    ['safe link', '<a href="https://example.test" target="_blank" rel="noopener">Report</a>'],
    ['same-origin asset', '<script src="/assets/app.js"></script>'],
  ];
  for (const [label, html] of mustStayQuiet) {
    const result = run(unique('html', html), '--format', 'json', '--profile', 'security');
    assert.deepEqual(ids(result).filter(id => id.startsWith('UE-SE')), [], `${label} must not be reported`);
  }
}
{
  // Position mapping survives comment masking.
  const result = run(unique('html', '\n\n<script src="https://cdn.test/lib.js"></script>'),
    '--format', 'json', '--profile', 'security');
  const finding = JSON.parse(result.stdout).findings.find(entry => entry.ruleId === 'UE-SE002');
  assert(finding, 'expected SE002');
  assert.equal(finding.line, 3, 'SE002 source mapping');
  assert.equal(finding.audit, 'security', 'audit findings are tagged');
}
{
  // Audit rules are opt-in: none of them may appear in a default run.
  const html = '<!doctype html><html lang="en"><head><title>' + 'A long title'.repeat(10)
    + '</title></head><body><canvas></canvas><script src="https://cdn.test/a.js"></script></body></html>';
  const file = unique('html', html);
  assert.deepEqual(ids(run(file, '--format', 'json')), [], 'audits must be opt-in');
  const enabled = run(file, '--format', 'json', '--profile', 'publishing', '--profile', 'accessibility',
    '--profile', 'security');
  assert(ids(enabled).length >= 3, `all requested audits must run: ${enabled.stdout}`);
  assert.equal(enabled.status, 0, 'audits never change the exit code');
}

// --- profiles: validation and isolation ---------------------------------------

{
  const file = textFixture('The organization uses a label.');
  const profile = write('profile.json', JSON.stringify({
    profileVersion: 1, name: 'Test', source: 'test',
    spelling: { organization: 'organisation' },
    // Enforce the conflict family so the severity downgrade below is what is
    // being tested (without the field the family would be accepted silently).
    spellingConflicts: [],
    terminology: { forbidden: [['old term', 'new term']] },
    register: { forbidden: ['bad'], approved: ['approved'] },
    severities: { 'UE-SP001': 'warning' },
    rules: { 'UE-RE003': { enabled: false } },
  }));
  const result = spawnSync(process.execPath, [cli, file, '--format', 'json', '--profile', profile],
    { encoding: 'utf8' });
  assert.equal(result.status, 0, 'a profile may downgrade an error to a warning');
  assert.deepEqual(ids(result), ['UE-SP001']);
}
{
  const invalidShapes = [
    {},
    { profileVersion: 1, name: '', source: 'x' },
    { profileVersion: 1, name: 'x', source: '', extra: true },
    { profileVersion: 1, name: 'x', source: 'y', spelling: { organization: '' } },
    { profileVersion: 1, name: 'x', source: 'y', spelling: { organization: ['organisation'] } },
    { profileVersion: 1, name: 'x', source: 'y', spelling: { organization: null } },
    { profileVersion: 1, name: 'x', source: 'y', spelling: { organization: { preferred: 'organisation' } } },
    { profileVersion: 1, name: 'x', source: 'y', spelling: { bogus: 'x' } },
    { profileVersion: 1, name: 'x', source: 'y', terminology: { unknown: [], forbidden: [['old', '']] } },
    { profileVersion: 1, name: 'x', source: 'y', terminology: { forbidden: [['old', 'old']] } },
    { profileVersion: 1, name: 'x', source: 'y', register: { unknown: [] } },
    { profileVersion: 1, name: 'x', source: 'y', register: { forbidden: [''] } },
    { profileVersion: 1, name: 'x', source: 'y', rules: { 'UE-RE003': { enabled: true, extra: true } } },
    { profileVersion: 1, name: 'x', source: 'y', severities: { 'UE-RE003': 'fatal' } },
    { profileVersion: 1, name: 'x', source: 'y', pageUrl: '/relative' },
    { auditVersion: 1, name: 'security', category: 'nope', rules: ['UE-SE001'] },
    { auditVersion: 1, name: 'security', category: 'security', rules: ['UE-NOPE'] },
    { auditVersion: 2, name: 'security', category: 'security', rules: ['UE-SE001'] },
  ];
  const target = textFixture('The organization reports.');
  invalidShapes.forEach((shape, index) => {
    const bad = write(`invalid-profile-${index}.json`, JSON.stringify(shape));
    const result = spawnSync(process.execPath, [cli, target, '--profile', bad, '--format', 'json'],
      { encoding: 'utf8' });
    assert.equal(result.status, 2, `${JSON.stringify(shape)}\n${result.stderr}`);
  });
}

// A profile is a read-only input: a symlinked dotfile is legitimate, but a
// named pipe must never be opened (it would block the run).
{
  const target = textFixture('The organisation reports.');
  const profile = write('link-target.json', JSON.stringify({ profileVersion: 1, name: 'x', source: 'y' }));
  const symlink = path.join(tmp, 'profile-symlink.json');
  try { fs.symlinkSync(profile, symlink); } catch { /* no symlink permission */ }
  if (fs.existsSync(symlink)) {
    const result = spawnSync(process.execPath, [cli, target, '--profile', symlink, '--format', 'json'],
      { encoding: 'utf8' });
    assert.equal(result.status, 0, `a symlinked profile is a legitimate read: ${result.stderr}`);
  }
  const fifo = path.join(tmp, 'profile-fifo.json');
  try { fs.rmSync(fifo, { force: true }); } catch { /* ignore */ }
  if (spawnSync('mkfifo', [fifo]).status === 0) {
    const profileResult = spawnSync(process.execPath, [cli, target, '--profile', fifo, '--format', 'json'],
      { encoding: 'utf8' });
    assert.equal(profileResult.status, 2, 'a named-pipe profile must be refused');
    const configResult = spawnSync(process.execPath, [cli, target, '--config', fifo], { encoding: 'utf8' });
    assert.equal(configResult.status, 2, 'a named-pipe config must be refused');
  }
}

// --- allowlists ---------------------------------------------------------------

{
  const terminology = write('terminology.json', JSON.stringify({ allowlist: { terminology: ['maternal deaths'] } }));
  const maternal = textFixture('Maternal deaths are shown.');
  assert(ids(run(maternal, '--format', 'json')).includes('UE-TE001'), 'baseline terminology must fire');
  assert(!ids(run(maternal, '--format', 'json', '--config', terminology)).includes('UE-TE001'),
    'allowlisted terminology must be quiet');
  const register = write('register.json', JSON.stringify({ allowlist: { register: ['boom'] } }));
  const boom = textFixture('A boom followed.');
  assert(ids(run(boom, '--format', 'json')).includes('UE-RE001'));
  assert(!ids(run(boom, '--format', 'json', '--config', register)).includes('UE-RE001'));
}

// --- robustness ----------------------------------------------------------------

for (const entity of ['&#x110000;', '&#999999999999;', '&#0;']) {
  const html = `<!doctype html><title>${entity}</title><meta name="description" content="ok">`
    + '<link rel="canonical" href="https://example.test/x"><h1>x</h1>'
    + '<meta property="og:title" content="x"><meta name="twitter:card" content="summary">';
  const result = run(unique('html', html), '--format', 'json', '--profile', 'publishing');
  assert.doesNotThrow(() => JSON.parse(result.stdout), `${entity}: ${result.stdout}`);
}
{
  // A very long single line must not blow the stack or the report.
  const long = textFixture(`The organisation reports ${'word '.repeat(20000)}organisation.`);
  const result = run(long, '--format', 'json');
  assert.doesNotThrow(() => JSON.parse(result.stdout));
}
{
  const dirty = write('dirty.txt', 'The US uses boom and organization.​‮');
  for (const format of ['json', 'sarif']) {
    const result = run(dirty, '--format', format);
    assert.doesNotThrow(() => JSON.parse(result.stdout));
    assert.doesNotMatch(result.stdout, /[​‮]/);
  }
}

// --- the repository checks clean ----------------------------------------------

{
  // The skill's own prose is written to pass its own rules.
  const result = run('.', '--self-scan', '--quiet');
  assert.equal(result.status, 0, `self-scan must be clean:\n${result.stdout}\n${result.stderr}`);
}

// --- installable package -------------------------------------------------------

{
  // The release/package test must never write into the protected source
  // directory: the tarball goes under this suite's own tmp directory and the
  // finally block still removes it (the tmp sweep below removes the rest).
  const packDir = path.join(tmp, 'pack');
  fs.mkdirSync(packDir, { recursive: true });
  const pack = spawnSync('npm', ['pack', '--json', '--pack-destination', packDir],
    { cwd: root, encoding: 'utf8' });
  assert.equal(pack.status, 0, pack.stderr);
  const packed = JSON.parse(pack.stdout)[0];
  const tarball = path.join(packDir, packed.filename);
  try {
    const installDir = path.join(tmp, 'install');
    fs.mkdirSync(installDir, { recursive: true });
    const install = spawnSync('npm',
      ['install', '--no-save', '--no-audit', '--no-fund', tarball],
      { cwd: installDir, encoding: 'utf8', timeout: 300000 });
    assert.equal(install.status, 0, install.stderr);
    const installed = path.join(installDir, 'node_modules', 'un-editorial-check');
    for (const file of ['bin/check.mjs', 'lib/cli.mjs', 'lib/units.mjs', 'config/default.json',
      'config/profiles/un-v1.json', 'rules/catalogue.json', 'SKILL.md', 'VERSION']) {
      assert(fs.existsSync(path.join(installed, file)), `installed package is missing ${file}`);
    }
    const version = spawnSync(process.execPath, [path.join(installed, 'bin', 'check.mjs'), '--version'],
      { encoding: 'utf8' });
    assert.equal(version.stdout.trim(), `un-editorial-check ${VERSION}`, version.stderr);
    const smoke = write('install-smoke.txt', 'The color reports.');
    const check = spawnSync(process.execPath, [path.join(installed, 'bin', 'check.mjs'), smoke],
      { cwd: installDir, encoding: 'utf8' });
    assert.equal(check.status, 1, `the installed CLI must report findings: ${check.stderr}`);
    assert.match(check.stdout, /UE-SP001/);

    // An installed package must pass its own self-scan. This is the step CI
    // runs, and it failed on every release from 1.0.0 until it was locked here:
    // the install path contains `node_modules`, and the `node_modules/**`
    // exclusion was matched against the absolute path, so a self-scan inside an
    // install either ran with no exclusions in force or with every file
    // excluded. Both are wrong. Reading its own `lib/fixtures/self-test` — the
    // deliberate violations `--self-test` asserts on — made the installed
    // package fail a scan of itself.
    const selfScan = spawnSync(process.execPath,
      [path.join(installed, 'bin', 'check.mjs'), '--self-scan', '--quiet'],
      { encoding: 'utf8' });
    assert.equal(selfScan.status, 0,
      `an installed package must pass its own self-scan:\n${selfScan.stdout}\n${selfScan.stderr}`);
    assert.doesNotMatch(selfScan.stdout, /lib\/fixtures\/self-test/,
      'a self-scan must not read the deliberate-violation fixture');
    const selfScanJson = spawnSync(process.execPath,
      [path.join(installed, 'bin', 'check.mjs'), '--self-scan', '--format', 'json'],
      { encoding: 'utf8' });
    const scanned = JSON.parse(selfScanJson.stdout).files;
    assert(scanned > 20, `a self-scan of an install must actually read the package, got ${scanned} files`);
  } finally {
    fs.rmSync(tarball, { force: true });
  }
}

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — release regressions: catalogue, version, exit codes, fixes, audits, profiles, packaging');
