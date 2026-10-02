// un-editorial-check — documentation contract tests.
//
// Standalone: `node tests/audit-docs.mjs`. Locks what the user-facing
// documents promise:
//
//   1. banned claim phrases never appear in the README, skill instructions,
//      user guide, command template, changelog or docs/ pages;
//   2. the user guide's house style holds: no contractions, no question
//      marks outside code, British English forms, no percent signs outside
//      code (fenced blocks and inline spans are removed before checking);
//   3. the exact clean-run sentence appears on every documented surface, and
//      the CLI prints precisely that sentence on a clean run — and only then;
//   4. the changelog carries the released 1.0.0 section and no Unreleased
//      placeholder;
//   5. package.json declares no dependencies or devDependencies;
//   6. the README exit-code rows are literally true against live runs: a
//      file or sub-directory named inside the skill root is scanned, the
//      skill root itself is the documented carve-out, and the two exit-2
//      refusals still refuse.
//
// Probe prose reaches the scanner through call names that are not render
// surfaces, so the repository self-scan never extracts this file's test data
// as user-visible copy.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { run } from '../bin/check.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cli = path.join(root, 'bin', 'check.mjs');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const list = directory => fs.readdirSync(path.join(root, directory))
  .filter(name => name.endsWith('.md'))
  .map(name => path.join(directory, name));

const userFacing = ['README.md', 'SKILL.md', 'USER-GUIDE.md', 'CHANGELOG.md',
  ...list('commands'), ...list('docs')];

/** Remove fenced code blocks and inline code spans before style checks. */
const stripCode = text => text
  .replace(/```[\s\S]*?```/g, '')
  .replace(/`[^`\n]*`/g, '');

// --- 1. banned claim phrases -------------------------------------------------

{
  const banned = ['UN approved', 'fully compliant', 'finds all errors',
    'factual verification', 'legal advice'];
  for (const file of userFacing) {
    const text = read(file);
    for (const phrase of banned) {
      const pattern = new RegExp(phrase.split(/\s+/).join('\\s+'), 'i');
      const match = pattern.exec(text);
      assert(!match,
        `${file} must not carry a banned claim (${phrase.match(/\w+/)[0]} form) near offset ${match ? match.index : 0}`);
    }
  }
}

console.log('ok — banned claim phrases: absent from every user-facing document');

// --- 2. user guide house style ------------------------------------------------

{
  const prose = stripCode(read('USER-GUIDE.md'));

  const contractions = /\b\w+n't\b|\b(?:it's|that's|there's|what's|who's|here's|how's|he's|she's|it'll|that'll|there'll|they're|we're|you're|they've|we've|you've|they'll|we'll|you'll|i'm|i've|i'll|i'd|he'd|she'd|we'd|you'd|they'd|let's)\b/gi;
  const found = prose.match(contractions) || [];
  assert.equal(found.length, 0, `user guide must not use contractions: ${[...new Set(found)].join(', ')}`);

  assert(!prose.includes('?'), 'user guide must not ask questions in prose');
  assert(!prose.includes('%'), 'user guide must keep percent signs inside code');

  // British English: unambiguous American forms stay out of the prose.
  const american = ['color', 'colors', 'behavior', 'favorite', 'analyze',
    'center', 'defense', 'gray', 'fiber', 'labeled', 'traveling', 'fulfill',
    'enrollment', 'catalog'];
  const hits = [];
  for (const word of american) {
    const pattern = new RegExp(`\\b${word}\\b`, 'gi');
    if (pattern.test(prose)) hits.push(word);
  }
  assert.equal(hits.length, 0, `user guide prose must use British English: ${hits.join(', ')}`);
}

console.log('ok — user guide house style: no contractions, no questions, British English, percent in code only');

// --- 3. the clean-run sentence, on every surface and in the CLI ---------------

const CLEAN = 'No findings under the enabled, documented local rules.';

{
  for (const surface of ['README.md', 'SKILL.md', 'USER-GUIDE.md', 'commands/un-diplomatic-agent.md']) {
    assert(read(surface).includes(CLEAN),
      `${surface} must state the clean-run sentence exactly: ${CLEAN}`);
  }

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-docs-'));
  const config = path.join(tmp, 'config.json');
  fs.writeFileSync(config, '{}');
  let sequence = 0;
  const capture = (prose) => {
    const file = path.join(tmp, `probe-${sequence++}.txt`);
    fs.writeFileSync(file, prose.endsWith('\n') ? prose : `${prose}\n`);
    const out = [];
    const err = [];
    const code = run([file, '--config', config], {
      log: line => out.push(String(line)),
      error: line => err.push(String(line)),
    });
    return { code, output: out.join('\n'), stderr: err.join('\n') };
  };

  const clean = capture('The report was reviewed, and the annex follows.');
  assert.equal(clean.code, 0, `a clean scan must exit 0:\n${clean.output}\n${clean.stderr}`);
  assert(clean.output.includes(CLEAN),
    `a clean scan must print the documented sentence exactly:\n${clean.output}`);

  const dirty = capture('The report is final!');
  assert.equal(dirty.code, 1, `a scan with an error must exit 1:\n${dirty.output}\n${dirty.stderr}`);
  assert(!dirty.output.includes(CLEAN),
    `a dirty scan must not claim a clean run:\n${dirty.output}`);

  fs.rmSync(tmp, { recursive: true, force: true });
}

console.log('ok — clean-run sentence: present on every surface, printed only by a clean CLI run');

// --- 4. changelog release section ---------------------------------------------

{
  const changelog = read('CHANGELOG.md');
  assert(!/^##\s+Unreleased\s*$/mi.test(changelog),
    'changelog must not keep an Unreleased placeholder section');
  assert(/^##\s+1\.0\.0\b/m.test(changelog),
    'changelog must carry the released 1.0.0 section');
}

console.log('ok — changelog: 1.0.0 section present, no Unreleased placeholder');

// --- 5. zero npm dependencies --------------------------------------------------

{
  const manifest = JSON.parse(read('package.json'));
  assert(!('dependencies' in manifest), 'package.json must declare no dependencies');
  assert(!('devDependencies' in manifest), 'package.json must declare no devDependencies');
}

console.log('ok — package manifest: no dependencies, no devDependencies');

// --- 6. README exit-code rows, checked against live runs ----------------------

{
  // The rows and the exit-prose describe three behaviours: a named file or
  // sub-directory inside the skill root is scanned, the skill root itself is
  // the carve-out that reads nothing and exits 0, and the two exit-2
  // refusals still refuse. Each is re-run here rather than re-read (QA F1:
  // prose that described only a plain scan of the root).
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-docs-exit-'));
  const config = path.join(tmp, 'config.json');
  fs.writeFileSync(config, '{}');
  const capture = (argv) => {
    const out = [];
    const err = [];
    const code = run([...argv, '--config', config], {
      log: line => out.push(String(line)),
      error: line => err.push(String(line)),
    });
    return { code, stdout: out.join('\n'), stderr: err.join('\n') };
  };

  // A file named inside the skill root is scanned, not shielded: README's
  // own scan must read exactly one file and report what it found.
  const namedFile = capture([path.join(root, 'README.md'), '--format', 'json']);
  const parsed = JSON.parse(namedFile.stdout);
  assert.equal(parsed.files, 1,
    `README.md must be scanned as a named file, not dropped:\n${namedFile.stdout}`);
  assert.equal(namedFile.code, 0,
    `README.md must scan clean with exit 0:\n${namedFile.stdout}\n${namedFile.stderr}`);
  const namedText = capture([path.join(root, 'README.md')]).stdout;
  assert.match(namedText, /scanned 1 file\b/,
    `the report must count the named file:\n${namedText}`);
  assert.equal(namedText.includes(CLEAN), parsed.findings.length === 0,
    `the clean-run sentence appears exactly when the named-file scan found nothing:\n${namedText}`);

  // A sub-directory named inside the skill root is scanned as well.
  const subdir = capture([path.join(root, 'docs'), '--format', 'json']);
  const subdirParsed = JSON.parse(subdir.stdout);
  assert(subdirParsed.files >= 1, `docs/ must be scanned as a named sub-directory:\n${subdir.stdout}`);
  assert.equal(subdir.code, 0, `docs/ must scan without error-severity findings:\n${subdir.stderr}`);

  // The skill root itself is the documented carve-out (README's exit-2 row):
  // it reads nothing, says so, and exits 0.
  const carveOut = spawnSync(process.execPath, [cli, '.'], { cwd: root, encoding: 'utf8' });
  assert.equal(carveOut.status, 0,
    `a scan whose target is the skill root must exit 0:\n${carveOut.stdout}\n${carveOut.stderr}`);
  assert.match(carveOut.stdout, /scanned 0 files/,
    `the carve-out must be honest about reading nothing:\n${carveOut.stdout}`);

  // README's exit-2 row: an unsupported named file and an empty scan are
  // still refusals.
  const unsupported = path.join(tmp, 'doc.docx.bak');
  fs.writeFileSync(unsupported, 'copy that must never be read');
  const badExt = capture([unsupported]);
  assert.equal(badExt.code, 2, `an unsupported named file must exit 2:\n${badExt.stderr}`);
  assert.match(badExt.stderr, /unsupported file type/,
    `stderr must name the refusal:\n${badExt.stderr}`);

  const emptyDir = path.join(tmp, 'empty');
  fs.mkdirSync(emptyDir);
  const empty = capture([emptyDir]);
  assert.equal(empty.code, 2, `an empty scan must exit 2:\n${empty.stderr}`);
  assert.match(empty.stderr, /no supported files found/,
    `stderr must name the empty-scan refusal:\n${empty.stderr}`);

  fs.rmSync(tmp, { recursive: true, force: true });
}

console.log('ok — README exit-code rows: named file scanned, skill-root carve-out, exit-2 refusals');
