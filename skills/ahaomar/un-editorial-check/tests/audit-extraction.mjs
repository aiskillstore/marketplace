// un-editorial-check — W1 contract tests: extraction & CLI honesty.
//
// Self-contained: its own tmpdir, its own CLI invocations through the same
// in-process `run` entry point tests/run.mjs uses. Nothing is ever written
// inside the repository (the checker self-scans the repository, and a test
// document inside it would be scanned as copy).
//
// Run standalone: node tests/audit-extraction.mjs
//
// Covered contract items:
//   1. HTML `ue:ignore` suppression (README:329 example and scoping rules)
//   2. Type-annotated TypeScript extraction
//   2b. JSX and TSX text children — copy that is not inside a string literal
//   3. Sentence-like literal promise + the self-scan hard gate
//   4. Explicitly named unsupported files / zero-file scans / supported set
//   5. `fixtures` directory skip at any depth + explicit-path override
//   6. `<input value>` copy
//   7. Empty inline `--config=` / `--profile=` values
//   8. Non-regular existing input (FIFO) honesty
//   9. `Report written:` announcement
//  10. README / USER-GUIDE literal truth (targeted lines)
//  11. unreadable files: a file whose bytes are not readable UTF-8 text yields
//      no copy and is never rewritten, the report says so in the header and in
//      the machine-readable forms, a run that read nothing at all refuses with
//      exit 2, and every genuinely readable .txt still scans — including
//      non-Latin scripts, a file that legitimately contains U+FFFD, and the
//      documented `check .` skill-root carve-out
//  12. the attribute grammar: legal unquoted attribute values, the ARIA copy
//      set (aria-label, -description, -valuetext, -roledescription), and the
//      attributes that must stay unread because they are URLs or identifiers
//  13. mutation checks on the unreadable-file contract: the header skip, the
//      read-nothing refusal, the honest file count and the NUL signal each have
//      to break the suite when removed
// plus regressions: MD/JS/TXT suppression matrix, directory exclusions,
// `--report` value refusals, `--fix` refusal on non-prose types.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { run } from '../bin/check.mjs';
import { extractFile, EXTRACTABLE_EXTENSIONS, SUPPORTED_EXTENSIONS } from '../lib/extract.mjs';
import { DEFAULT_EXCLUDES } from '../lib/scanner.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cli = path.join(root, 'bin', 'check.mjs');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-audit-'));

// Deliberate rule-violating test data. Each constant carries a same-line
// `ue:ignore` so the repository's own self-scan stays clean however the
// sentence-like-literal rule classifies this file's own source.
const ORG = 'The color reports quarterly.'; // ue:ignore UE-SP001  (deliberate test data)
const ORG_AGAIN = 'The color reports again.'; // ue:ignore UE-SP001  (deliberate test data)
const DOUBLED = 'The delegation reviewed the the draft.'; // ue:ignore UE-GR001  (deliberate test data)
const DOUBLED_NOPUNCT = 'The delegation reviewed the the draft'; // ue:ignore UE-GR001  (deliberate test data)

const write = (name, value) => {
  const file = path.join(tmp, name);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, value);
  return file;
};
// An explicit config keeps the suite independent of any .un-editorial.json in
// the working directory.
const config = write('config.json', '{}');

const runRaw = (argv) => {
  const out = [];
  const err = [];
  const code = run(argv, {
    log: line => out.push(String(line)),
    error: line => err.push(String(line)),
  });
  return { code, stdout: out.join('\n'), stderr: err.join('\n') };
};
// Only supply the suite's config when the caller has not chosen one.
const capture = (argv, configPath = config) =>
  runRaw(argv.includes('--config') ? argv : [...argv, '--config', configPath]);
const json = result => {
  try { return JSON.parse(result.stdout); }
  catch { return assert.fail(`stdout is not JSON:\n${result.stdout}\n${result.stderr}`); }
};
const ids = result => [...new Set(json(result).findings.map(f => f.ruleId))].sort();
const scan = (file, ...extra) => capture([file, '--format', 'json', ...extra]);

// --- 1. HTML ue:ignore suppression ------------------------------------------

{
  // Baseline: the same paragraph without a suppression fires UE-SP001.
  assert.deepEqual(ids(scan(write('html-base.html', `<p>${ORG}</p>\n`))), ['UE-SP001']);

  // README:329 ships this exact example; it must produce 0 findings, exit 0 —
  // identical to the Markdown / JS / TXT twins below.
  const inline = scan(write('html-inline.html', `<p>${ORG} <!-- ue:ignore UE-SP001 --></p>\n`));
  assert.deepEqual(ids(inline), [], 'the README HTML suppression example must produce no findings');
  assert.equal(inline.code, 0, 'a fully suppressed HTML file must exit 0');

  // The Markdown, JS and TXT twins behave identically, with and without the
  // suppression (existing behaviour, locked as the contract demands).
  assert.deepEqual(ids(scan(write('twin-base.md', `${ORG}\n`))), ['UE-SP001']);
  assert.deepEqual(ids(scan(write('twin-base.txt', `${ORG}\n`))), ['UE-SP001']);
  assert.deepEqual(ids(scan(write('twin-base.js', `const label = "${ORG}";\n`))), ['UE-SP001']);
  assert.deepEqual(ids(scan(write('twin-sup.md', `${ORG} <!-- ue:ignore UE-SP001 -->\n`))), []);
  assert.deepEqual(ids(scan(write('twin-sup.txt', `${ORG} <!-- ue:ignore UE-SP001 -->\n`))), []);
  assert.deepEqual(
    ids(scan(write('twin-sup.js', `const label = "${ORG}"; // ue:ignore UE-SP001\n`))), []);

  // A comment after </p> on the same line scopes that paragraph.
  assert.deepEqual(
    ids(scan(write('html-after-p.html', `<p>${ORG}</p> <!-- ue:ignore UE-SP001 -->\n`))), [],
    'a comment after </p> on the same line must scope that paragraph');

  // A standalone comment line directly above a paragraph scopes that paragraph.
  assert.deepEqual(
    ids(scan(write('html-above.html', `<!-- ue:ignore UE-SP001 -->\n<p>${ORG}</p>\n`))), [],
    'a standalone comment directly above a paragraph must scope that paragraph');

  // ue:ignore all and family patterns work in HTML.
  assert.deepEqual(ids(scan(write('html-all.html', `<p>${ORG} <!-- ue:ignore all --></p>\n`))), []);
  assert.deepEqual(ids(scan(write('html-family.html', `<p>${ORG} <!-- ue:ignore UE-SP* --></p>\n`))), []);

  // A suppression for a different rule does not silence UE-SP001.
  assert.deepEqual(
    ids(scan(write('html-wrong.html', `<p>${ORG} <!-- ue:ignore UE-TE003 --></p>\n`))),
    ['UE-SP001'], 'a ue:ignore for another rule must not silence UE-SP001');

  // A comment anywhere inside the unit's text span applies to that unit.
  assert.deepEqual(
    ids(scan(write('html-mid.html', '<p>The organization <!-- ue:ignore UE-SP001 --> reports quarterly.</p>\n'))),
    [], 'a comment inside the paragraph text must scope the paragraph');

  // In a multi-paragraph file a suppression in paragraph A does not silence B.
  const multi = scan(write('html-multi.html',
    `<p>${ORG} <!-- ue:ignore UE-SP001 --></p>\n<p>${ORG_AGAIN}</p>\n`));
  assert.deepEqual(ids(multi), ['UE-SP001'],
    'a suppression in paragraph A must not silence paragraph B');
  assert.equal(json(multi).findings[0].line, 2, 'the surviving finding must come from paragraph B');

  const multiAbove = scan(write('html-multi-above.html',
    `<!-- ue:ignore UE-SP001 -->\n<p>${ORG}</p>\n<p>${ORG_AGAIN}</p>\n`));
  assert.deepEqual(ids(multiAbove), ['UE-SP001'],
    'a standalone suppression above paragraph A must not silence paragraph B');
  assert.equal(json(multiAbove).findings[0].line, 3,
    'the surviving finding must come from paragraph B');

  // HTML comments remain masked from rule text (unchanged behaviour).
  assert.deepEqual(
    ids(scan(write('html-comment-masked.html', `<!-- ${ORG} -->\n<p>Clean paragraph.</p>\n`))),
    [], 'comment text must never reach the rules');

  // --- regression: the existing MD/JS/TXT suppression matrix ----------------
  const matrix = [
    ['The organization reports. <!-- ue:ignore UE-SP001 -->', []],
    ['The organization reports. <!-- ue:ignore UE-SP* -->', []],
    ['The organization reports. <!-- ue:ignore all -->', []],
    ['The organization reports. <!-- ue:ignore UE-TE003 -->', ['UE-SP001']],
    ['The organization reports 25%. <!-- ue:ignore UE-SP001,UE-TE003,UE-RE003 -->', []],
  ];
  matrix.forEach(([body, expected], index) => {
    assert.deepEqual(ids(scan(write(`matrix-${index}.md`, `${body}\n`))), expected, body);
  });
  // A Markdown suppression must not leak into the next paragraph.
  assert.deepEqual(
    ids(scan(write('matrix-leak.md',
      'The organization reports. <!-- ue:ignore UE-SP001 -->\n\nThe organization reports again.\n'))),
    ['UE-SP001'], 'a Markdown suppression must not leak into the next paragraph');
  // A JS line suppression must not leak to the next line.
  const jsLeak = json(scan(write('js-leak.js',
    `const label = "${ORG}"; // ue:ignore UE-SP001\nconst other = "${ORG_AGAIN}";\n`)));
  assert.equal(jsLeak.findings.length, 1, 'a JS suppression must not leak to the next line');
  assert.equal(jsLeak.findings[0].line, 2, 'the surviving JS finding must come from line 2');
  // A TXT suppression must not leak into the next paragraph.
  const txtLeak = json(scan(write('txt-leak.txt',
    `${ORG} <!-- ue:ignore UE-SP001 -->\n\n${ORG_AGAIN}\n`)));
  assert.equal(txtLeak.findings.length, 1, 'a TXT suppression must not leak into the next paragraph');
  assert.equal(txtLeak.findings[0].line, 3, 'the surviving TXT finding must come from line 3');
}

// --- 2. type-annotated TypeScript --------------------------------------------

{
  const jsTwin = write('twin-gr.js', `const msg = "${DOUBLED}";\n`);
  const jsIds = ids(scan(jsTwin));
  assert.deepEqual(jsIds, ['UE-GR001'], 'the .js twin must fire UE-GR001');

  const variants = [
    `const msg: string = "${DOUBLED}";\n`,
    `let msg: string = "${DOUBLED}";\n`,
    `var msg: string = "${DOUBLED}";\n`,
    `export const msg: string = "${DOUBLED}";\n`,
    `const msg: Record<string, string> = "${DOUBLED}";\n`,
    `const msg: Array<string> = "${DOUBLED}";\n`,
    `el.textContent = "${DOUBLED}";\n`,
  ];
  variants.forEach((body, index) => {
    const file = write(`annot-${index}.ts`, body);
    assert.deepEqual(ids(scan(file)), jsIds,
      `the .ts twin must fire exactly like the .js twin: ${body.trim()}`);
  });
}

// --- 2b. JSX / TSX text children ---------------------------------------------
//
// Brief §6: "Improve JavaScript extraction … Add fixtures for … dynamically
// rendered copy." A .jsx or .tsx file writes its copy in the markup, not in a
// string literal: `<p>The organization reports.</p>` has no quotes anywhere, so
// the tokenizer — which only classifies string and template tokens — returned
// nothing at all for the file. That is the single largest extraction gap found
// in the audit: an entire supported format contributed zero copy.

{
  const JSX_TEXT = 'The organization reports quarterly.';
  const variants = [
    ['arrow.tsx', `export const P = () => <p>${JSX_TEXT}</p>;\n`],
    ['assign.jsx', `const p = <p>${JSX_TEXT}</p>;\n`],
    ['nested.jsx', `const p = (\n  <section>\n    <p>${JSX_TEXT}</p>\n  </section>\n);\n`],
    ['sibling.jsx', `const p = <div><h1>Heading</h1><p>${JSX_TEXT}</p></div>;\n`],
    ['multiline.jsx', `const p = <p>\n  ${JSX_TEXT}\n</p>;\n`],
    ['named.tsx', `function P() {\n  return <p>${JSX_TEXT}</p>;\n}\n`],
  ];
  for (const [name, body] of variants) {
    assert.deepEqual(ids(scan(write(name, body))), ['UE-SP001'],
      `JSX text child copy must be extracted: ${name}`);
  }

  // JSX attribute values are literals and were already covered; the text
  // children above are the part that was missing.
  assert.deepEqual(ids(scan(write('attr.jsx', `const p = <img alt="${JSX_TEXT}" />;\n`))),
    ['UE-SP001'], 'JSX attribute copy keeps working');

  // An expression child is code, not copy: a literal inside braces is already
  // handled by the string path, and a bare expression child holds no prose.
  assert.deepEqual(ids(scan(write('expr.jsx',
    'const p = <p>{count}</p>;\n'))), [],
    'an expression child with no literal is not copy');

  // Structural text that is never user-visible must stay out.
  assert.deepEqual(ids(scan(write('struct.jsx', `const p = <div className="x" id="y" />;\n`))), [],
    'class and id values are identifiers, not copy');
  assert.deepEqual(ids(scan(write('comment.jsx', `const p = <p>{/* ${JSX_TEXT} */}</p>;\n`))), [],
    'a JSX comment is not copy');

  // A .js file has no JSX, so the same text outside quotes is code, not copy.
  assert.deepEqual(ids(scan(write('nojsx.js', `const p = The organization reports;\n`))), [],
    'plain JavaScript prose outside a literal is not copy');

  // --- the false-positive controls: the gate is structural, not an extension --
  //
  // TypeScript generics, type assertions, interfaces and comparisons all look
  // like markup to a naive `<Tag>` scan. None of them may become copy, and this
  // is the assertion that would fail first if the gate were ever loosened to
  // "scan .jsx and .tsx by extension".
  for (const [name, body] of [
    ['generic-array.ts', 'const a: Array<string> = [];\nconst m = new Map<string, number>();\n'],
    ['generic-fn.ts', 'function f<T>(x: T): T { return x; }\n'],
    ['comparison.ts', 'if (a < b) { c(); }\nconst q = x < y;\n'],
    ['type-alias.ts', 'type A = { a: string };\ninterface B { b: number }\n'],
    ['code.js', 'const x = 1 + 2;\nfunction f(a) { return a * 2; }\n// done\n'],
    ['imports.ts', "import React from 'react';\nimport { useState } from 'react';\n"],
  ]) {
    assert.deepEqual(ids(scan(write(name, body))), [],
      `TypeScript syntax is not copy and must stay silent: ${name}`);
  }

  // JSX-specific exclusions. Each is text a reader does not see.
  assert.deepEqual(ids(scan(write('expr-hole.jsx',
    'const p = <p>{count} of them</p>;\n'))), [],
  'an expression child is code, not copy');
  assert.deepEqual(ids(scan(write('jsx-comment.jsx',
    'const p = <p>{/* The organization reports. */}Visible copy</p>;\n'))), [],
  'a JSX comment is not copy');
  assert.deepEqual(ids(scan(write('void.jsx',
    'const p = <div><br /><img src="a.png" /><hr />Copy text</div>;\n'))), [],
  'a void or self-closing element has no text position');

  // Entities are decoded, so copy containing an ampersand reads as published.
  {
    const entity = scan(write('entity.jsx', 'const p = <p>Terms &amp; conditions apply.</p>;\n'));
    const unit = extractFile(path.join(tmp, 'entity.jsx'),
      'const p = <p>Terms &amp; conditions apply.</p>;\n', {}).find(u => u.text.includes('Terms'));
    assert(unit, 'a JSX element with entity copy must produce a unit');
    assert.equal(unit.text, 'Terms & conditions apply.',
      'a JSX entity reference must be decoded, not left as source');
    assert.deepEqual(ids(entity), [], 'the decoded JSX copy is clean');
  }

  // Quoted material inside JSX copy is still quoted material, so it is masked
  // out of the rules exactly as it would be in a literal.
  {
    const quoted = extractFile(path.join(tmp, 'quoted.jsx'),
      'const p = <p>He said "the organization reports" today.</p>;\n', {});
    const unit = quoted.find(u => u.text.includes('He said'));
    assert(unit, 'JSX copy around a quotation must still be extracted');
    assert.equal(unit.text, 'He said today.',
      'a quotation inside JSX copy must be masked, as in any other copy span');
  }

  // Text before and after a nested element is three separate runs, in order.
  {
    const mixed = extractFile(path.join(tmp, 'mixed.jsx'),
      'const p = <div>Before<p>The organization reports.</p>After</div>;\n', {});
    assert.deepEqual(mixed.map(u => u.text), ['Before', 'The organization reports.', 'After'],
      'JSX text runs are collected separately and in document order');
    // Every run keeps an exact map, so a fix can land in the text and nowhere else.
    for (const unit of mixed) {
      const at = unit.raw.indexOf(unit.text);
      assert(at >= 0, `each JSX run must sit verbatim in its own source slice: ${unit.text}`);
    }
  }
}

// --- 3. sentence-like literals ------------------------------------------------

{
  // Positive probes: any non-comment position, >= 4 words, ends in . ! or ?.
  const positives = [
    ['console-position.js', `console.log("${DOUBLED}");\n`],
    ['console-assign.js', `const label = "${DOUBLED}";\n`],
    ['array-element.js', `[${JSON.stringify(DOUBLED)}]\n`],
    ['bare-template.js', '`' + DOUBLED + '`\n'],
  ];
  for (const [name, body] of positives) {
    assert.deepEqual(ids(scan(write(name, body))), ['UE-GR001'],
      `a sentence-like literal must be extracted as copy: ${name}`);
  }

  // Negative probes: they must stay silent.
  assert.deepEqual(ids(scan(write('neg-shape.js', 'beep("File not found");\n'))),
    [], 'a short label without a sentence ending must stay silent');
  assert.deepEqual(ids(scan(write('neg-require.js', "require('./some/module');\n"))),
    [], 'a require path must stay silent');
  assert.deepEqual(ids(scan(write('neg-nopunct.js', `const status = "${DOUBLED_NOPUNCT}";\n`))),
    [], 'a string that does not end in . ! or ? must stay silent');
  assert.deepEqual(
    ids(scan(write('neg-comment.js', `// const label = "${DOUBLED}";\nconst x = 1;\n`))),
    [], 'a sentence-like literal inside a comment must stay silent');
}

// --- 4. explicitly named unsupported files and zero-file scans ---------------

{
  // The supported set stays exactly this list. `.pdf` joined it in 1.3.0, when
  // PDF text extraction landed; `.docx` and `.odt` joined it when document
  // containers did. Every other member is unchanged.
  assert.deepEqual([...EXTRACTABLE_EXTENSIONS].sort(),
    ['.md', '.markdown', '.txt', '.html', '.htm', '.js', '.mjs', '.cjs', '.jsx', '.ts', '.tsx', '.pdf', '.docx', '.odt'].sort(),
    'the extractable extension set must be the documented one');
  assert.deepEqual([...SUPPORTED_EXTENSIONS].sort(), [...EXTRACTABLE_EXTENSIONS].sort(),
    'the announced list must match the extractable set');

  for (const ext of ['.py', '.vue', '.xml', '.json', '.css']) {
    const file = write(`unsupported${ext}`, 'copy that would otherwise scan\n');
    const result = capture([file]);
    assert.equal(result.code, 2, `an explicitly named ${ext} file must refuse with exit 2`);
    assert.ok(result.stderr.includes(file), `stderr must name the path: ${result.stderr}`);
    for (const supported of SUPPORTED_EXTENSIONS) {
      assert.ok(result.stderr.includes(supported),
        `stderr must list the supported extensions: missing ${supported}`);
    }
  }

  // A directory scan still skips unsupported files silently …
  write('ext-mixed/style.css', `${ORG}\n`);
  write('ext-mixed/data.json', `${ORG}\n`);
  write('ext-mixed/page.txt', `${ORG}\n`);
  const mixed = json(capture([path.join(tmp, 'ext-mixed'), '--format', 'json']));
  assert.equal(mixed.files, 1, 'unsupported files in a directory scan must be skipped, not counted');

  // … but a scan in which zero files were scanned is a refusal.
  const emptyDir = path.join(tmp, 'only-unsupported');
  fs.mkdirSync(emptyDir, { recursive: true });
  fs.writeFileSync(path.join(emptyDir, 'style.css'), 'body { color: red; }\n');
  const zero = capture([emptyDir]);
  assert.equal(zero.code, 2, 'a scan that finds no supported files must exit 2');
  assert.match(zero.stderr, /no supported files found/,
    `stderr must say no supported files were found: ${zero.stderr}`);
  assert.ok(zero.stderr.includes(emptyDir), `stderr must name the path: ${zero.stderr}`);

  // An explicitly named empty .txt / .md file still scans: 0 findings, exit 0.
  for (const name of ['empty-file.txt', 'empty-file.md']) {
    const file = write(name, '');
    const result = scan(file);
    assert.equal(result.code, 0, `${name} must scan clean with exit 0`);
    assert.deepEqual(ids(result), [], `${name} must produce no findings`);
  }

  // A genuinely missing path keeps `path not found`.
  const missing = runRaw([path.join(tmp, 'no-such-path')]);
  assert.equal(missing.code, 2);
  assert.match(missing.stderr, /path not found/);

  // --fix on non-prose types is refused by the fixer, unchanged.
  const fixHtml = write('fix-page.html', `<p>${ORG}</p>\n`);
  const fixHtmlBefore = fs.readFileSync(fixHtml, 'utf8');
  const fixHtmlResult = capture([fixHtml, '--fix', '--apply']);
  assert.equal(fixHtmlResult.code, 2, 'HTML must still be refused by --fix');
  assert.match(fixHtmlResult.stderr, /refusing --fix/);
  assert.equal(fs.readFileSync(fixHtml, 'utf8'), fixHtmlBefore, 'HTML must not be rewritten');

  const fixJs = write('fix-script.js', `const label = "${ORG}";\n`);
  const fixJsBefore = fs.readFileSync(fixJs, 'utf8');
  const fixJsResult = capture([fixJs, '--fix', '--apply']);
  assert.equal(fixJsResult.code, 2, 'JavaScript must still be refused by --fix');
  assert.match(fixJsResult.stderr, /refusing --fix/);
  assert.equal(fs.readFileSync(fixJs, 'utf8'), fixJsBefore, 'JavaScript must not be rewritten');
}

// --- 5. fixtures directory skip ----------------------------------------------

{
  assert.ok(DEFAULT_EXCLUDES.includes('fixtures'),
    'DEFAULT_EXCLUDES must skip any directory segment named fixtures');
  const defaults = JSON.parse(fs.readFileSync(path.join(root, 'config', 'default.json'), 'utf8'));
  assert.ok(defaults.ignoredPaths.includes('fixtures/**'),
    'config/default.json ignoredPaths must skip fixtures at any depth');

  write('proj/fixtures/skipped.md', `${ORG}\n`);
  write('proj/other/kept.md', `${ORG}\n`);
  write('proj/a/fixtures/deep.md', `${ORG}\n`);

  // A directory scan skips fixtures at any depth …
  const dirScan = json(capture([path.join(tmp, 'proj'), '--format', 'json']));
  assert.equal(dirScan.files, 1,
    `fixtures at any depth must be skipped in directory scans: ${JSON.stringify(dirScan)}`);
  assert.ok(dirScan.findings[0].file.replace(/\\/g, '/').endsWith('proj/other/kept.md'),
    'only the non-fixtures file must be scanned');

  // … while a fixtures path named explicitly on the command line is scanned.
  const explicitFile = path.join(tmp, 'proj', 'fixtures', 'skipped.md');
  assert.deepEqual(ids(scan(explicitFile)), ['UE-SP001'],
    'an explicitly named fixtures file must still be scanned');

  const explicitDir = json(capture([path.join(tmp, 'proj', 'fixtures'), '--format', 'json']));
  assert.equal(explicitDir.files, 1,
    'an explicitly named fixtures directory must still be scanned');
  assert.deepEqual([...new Set(explicitDir.findings.map(f => f.ruleId))].sort(), ['UE-SP001']);
}

// --- 6. <input value> copy ----------------------------------------------------

{
  const withValue = scan(write('input-value.html',
    '<input type="button" value="The organization will publish the guide.">\n'));
  assert.ok(ids(withValue).includes('UE-SP001'),
    `an input button value must be scanned and fire UE-SP001: ${withValue.stdout}`);

  // The existing <button value> handling is unchanged.
  const button = scan(write('button-value.html',
    '<button value="The organization will publish the guide."></button>\n'));
  assert.ok(ids(button).includes('UE-SP001'), 'a button value must keep firing UE-SP001');

  // A text input default value is user data, not published copy.
  const textInput = scan(write('input-text.html',
    '<input type="text" value="The organization will publish the guide.">\n'));
  assert.deepEqual(ids(textInput), [],
    'a text input default value must not be treated as published copy');
}

// --- 7. empty inline flag values ---------------------------------------------

{
  // `--config=` and `--profile=` are usage failures, not silent fallbacks.
  const emptyConfig = capture(['--config=']);
  assert.equal(emptyConfig.code, 2, '--config= must exit 2');
  assert.match(emptyConfig.stderr, /--config requires a value/);

  const emptyProfile = capture(['--profile=']);
  assert.equal(emptyProfile.code, 2, '--profile= must exit 2');
  assert.match(emptyProfile.stderr, /--profile requires a value/);

  // --report already refuses an empty value; keep it.
  const reportEmpty = spawnSync(process.execPath, [cli, '--report='],
    { encoding: 'utf8', cwd: tmp });
  assert.equal(reportEmpty.status, 2, '--report= must still exit 2');
  assert.match(reportEmpty.stderr, /--report requires a value/);
  const reportMissing = spawnSync(process.execPath, [cli, '--report'],
    { encoding: 'utf8', cwd: tmp });
  assert.equal(reportMissing.status, 2, '--report without a value must still exit 2');
  assert.match(reportMissing.stderr, /--report requires a value/);

  // Normal forms are unchanged.
  const clean = write('flag-clean.txt', 'The organisation reports the figure.\n');
  assert.equal(capture([clean, '--config', config]).code, 0,
    '--config <path> must keep working');
  assert.equal(capture([clean, '--profile', 'security']).code, 0,
    '--profile <name> must keep working');

  // A non-empty but odd --config value reaches the loader unchanged: it is
  // refused as a missing config file, never as an empty flag value.
  const odd = capture([clean, '--config', '{"json"}']);
  assert.equal(odd.code, 2);
  assert.match(odd.stderr, /config not found/);
  assert.doesNotMatch(odd.stderr, /requires a value/,
    'a non-empty --config value must not be treated as empty');
}

// --- 8. non-regular existing input -------------------------------------------

{
  const fifo = path.join(tmp, 'pipe.txt');
  const made = spawnSync('mkfifo', [fifo], { encoding: 'utf8' });
  if (made.status === 0) {
    const result = spawnSync(process.execPath, [cli, fifo],
      { encoding: 'utf8', timeout: 5000 });
    assert.equal(result.status, 2, `a FIFO must refuse with exit 2: ${result.stderr}`);
    assert.ok(!result.error, 'a FIFO must not hang the run');
    assert.match(result.stderr, /not a regular file/,
      `stderr must say it is not a regular file: ${result.stderr}`);
    assert.ok(result.stderr.includes(fifo), `stderr must name the path: ${result.stderr}`);
  }
}

// --- 9. report path announcement ----------------------------------------------

{
  const target = write('report-target.txt', `${ORG}\n`);
  const pdf = path.join(tmp, 'announce.pdf');

  // TEXT, not quiet: exactly one `Report written:` line, after the findings.
  const textResult = capture([target, '--report', pdf]);
  assert.equal(textResult.code, 1, 'the target must report UE-SP001');
  const announced = textResult.stdout.split('\n').filter(line => line.startsWith('Report written: '));
  assert.equal(announced.length, 1, `expected exactly one announcement:\n${textResult.stdout}`);
  assert.equal(announced[0], `Report written: ${pdf}`,
    'the announcement must carry the path exactly as given');
  assert.ok(textResult.stdout.trimEnd().endsWith(`Report written: ${pdf}`),
    'the announcement must come after the findings block');

  // --quiet never announces.
  const quiet = capture([target, '--report', path.join(tmp, 'announce-quiet.pdf'), '--quiet']);
  assert.equal(quiet.stdout.includes('Report written:'), false,
    '--quiet must not announce the report');
  assert.equal(quiet.stdout.trim(), '', '--quiet must not print the text report');

  // --format json and --format sarif stay machine-readable.
  for (const format of ['json', 'sarif']) {
    const result = capture([target, '--report', path.join(tmp, `announce-${format}.pdf`),
      '--format', format]);
    assert.doesNotThrow(() => JSON.parse(result.stdout),
      `--format ${format} must stay valid JSON`);
    assert.equal(result.stdout.includes('Report written:'), false,
      `--format ${format} must not announce the report`);
  }

  // The path is printed exactly as given, even when relative.
  const relative = spawnSync(process.execPath,
    [cli, 'report-target.txt', '--report', 'given-name.pdf'],
    { cwd: tmp, encoding: 'utf8' });
  assert.equal(relative.status, 1, `expected the failing exit code: ${relative.stderr}`);
  assert.ok(relative.stdout.includes('\nReport written: given-name.pdf'),
    `relative report paths must be echoed as given:\n${relative.stdout}`);
}

// --- 12. attribute grammar: unquoted values and the ARIA copy set ----------
//
// Brief §6 requires visible copy in "accessible labels" to be scanned. Two
// gaps were open: the attribute pattern accepted only the two quoted forms, so
// a legal unquoted value (`alt=organization`, which is what a hand-edited or
// generated page looks like) was dropped entirely; and three ARIA properties a
// screen reader announces as text — aria-description, aria-valuetext and
// aria-roledescription — were not in the copy-bearing set at all.

{
  // An unquoted value ends at whitespace or `>`, so a legal unquoted value is
  // a single token: that is the HTML grammar, not a limitation of the parser.
  const W = 'organization';
  const UNQUOTED = [
    ['alt', `<img alt=${W}>\n`],
    ['alt-self-closing', `<img alt=${W} />\n`],
    ['alt-gt-terminated', `<img alt=${W}><p>Paragraph after.</p>\n`],
    ['title', `<a title=${W} href=/x>Link text.</a>\n`],
    ['aria-label', `<div aria-label=${W}></div>\n`],
    ['placeholder', `<input placeholder=${W}>\n`],
  ];
  for (const [name, body] of UNQUOTED) {
    assert.deepEqual(ids(scan(write(`unq-${name}.html`, body))), ['UE-SP001'],
      `an unquoted ${name} value must be scanned: ${body.trim()}`);
  }

  // Only copy-bearing attributes are read. Reading href, src or class as prose
  // would put URLs and CSS identifiers into editorial findings, which is the
  // boundary the whole extraction layer exists to hold.
  for (const [name, body] of [
    ['href', `<a href=${W}>Link text.</a>\n`],
    ['src', `<img src=${W}>\n`],
    ['class', `<div class=${W}></div>\n`],
    ['id', `<div id=${W}></div>\n`],
    ['data-', `<div data-x=${W}></div>\n`],
  ]) {
    assert.deepEqual(ids(scan(write(`unq-silent-${name}.html`, body))), [],
      `an unquoted ${name} value must not become copy`);
  }

  // A valueless attribute and an empty value produce no unit at all.
  assert.deepEqual(ids(scan(write('unq-valueless.html', '<input disabled alt>\n'))), [],
    'a valueless attribute is not an empty copy surface');
  assert.deepEqual(ids(scan(write('unq-empty.html', '<img alt= >\n'))), [],
    'an empty attribute value produces no unit');

  // The ARIA copy set. Each of these is announced to a screen-reader user as
  // text, which is why brief §6 puts them in scope.
  const ARIA = [
    ['aria-label', `<div aria-label="${ORG}"></div>\n`],
    ['aria-description', `<div aria-description="${ORG}"></div>\n`],
    ['aria-valuetext', `<div role="slider" aria-valuetext="${ORG}"></div>\n`],
    ['aria-roledescription', `<div role="button" aria-roledescription="${ORG}"></div>\n`],
  ];
  for (const [name, body] of ARIA) {
    assert.deepEqual(ids(scan(write(`aria-${name}.html`, body))), ['UE-SP001'],
      `${name} is announced to assistive technology and must be scanned`);
  }

  // aria-labelledby names element IDs, not copy, so it carries no unit of its
  // own — and the referenced element's own text is still extracted.
  {
    // The referenced element is a heading, so UE-HR004 also reports its full
    // stop; the assertion here is about how many copy units exist, so it
    // filters to the spelling defect rather than pinning the whole id set.
    const byId = scan(write('aria-labelledby.html',
      `<div aria-labelledby="hdr"></div><h2 id="hdr">${ORG}</h2>\n`));
    const spelling = json(byId).findings.filter(f => f.ruleId === 'UE-SP001');
    assert.equal(spelling.length, 1,
      'the element an aria-labelledby points at must still be scanned exactly once');
    const units = extractFile(
      write('aria-labelledby-units.html',
        `<div aria-labelledby="hdr"></div><h2 id="hdr">${ORG}</h2>\n`),
      fs.readFileSync(path.join(tmp, 'aria-labelledby-units.html'), 'utf8'), {});
    assert.equal(units.length, 1,
      'aria-labelledby holds element IDs, not copy, so it adds no unit of its own');
  }

  // The ARIA additions are navigation copy, not authored narrative: a defect in
  // one must not be reported as a narrative-paragraph defect.
  {
    const unit = json(scan(write('aria-context.html', `<div aria-valuetext="${ORG}"></div>\n`)))
      .findings[0];
    assert.equal(unit.context, 'nav',
      'an ARIA property is interface copy and keeps the navigation context');
  }
}

// --- 11. binary-named-.txt --------------------------------------------------
//
// A file whose bytes are not UTF-8 is not user-visible copy in any supported
// format. Read with a lossy decode it looked like prose: a PNG header produced
// a "Bare US in prose" finding invented from bytes that are not text, and
// `--fix --apply` wrote the lossy round-trip back over the original file,
// replacing every undecodable byte with U+FFFD. extractFile now returns no
// units for such content, exactly as it does for an unsupported extension.

{
  // A real defect embedded in otherwise-binary bytes: before the guard this
  // fired, and the finding was invented from a PNG header.
  const binary = write('misnamed.png.txt', Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]),
    Buffer.from('The US delegation and the the report.'),
    Buffer.from([0x00, 0x01, 0x02, 0xFF, 0xFE, 0x80, 0x81]),
  ]));
  // A file that is its own only input was never read, so the run is a refusal
  // rather than a clean run: "scanned 0 files" plus the canonical clean sentence
  // is the exact shape of QA finding F1, where a run reported success having
  // read nothing. The same three cases are now consistent: an unsupported named
  // file refuses, a directory with no supported files refuses, and a file whose
  // bytes are not readable refuses.
  const binaryOnly = capture([binary]);
  assert.equal(binaryOnly.code, 2,
    `a run that read nothing must refuse with exit 2: ${binaryOnly.stdout}${binaryOnly.stderr}`);
  assert.match(binaryOnly.stderr, /no readable files found/,
    `the refusal must say so: ${binaryOnly.stderr}`);
  assert.ok(binaryOnly.stderr.includes(binary),
    `the refusal must name the path: ${binaryOnly.stderr}`);
  assert.doesNotMatch(binaryOnly.stdout, /No findings under/,
    'a run that read nothing must never print the clean-run sentence');

  // The decisive test: --fix --apply must not touch the bytes. Before the guard
  // this rewrote the file and left U+FFFD where the original bytes had been.
  const before = fs.readFileSync(binary);
  const applied = capture([binary, '--fix', '--apply']);
  assert.notEqual(applied.code, 1, 'a refusal is not an error-severity run');
  assert.doesNotMatch(applied.stdout, /APPLIED/,
    '--fix must not claim a fix it did not make');
  assert.deepEqual(fs.readFileSync(binary), before,
    '--fix --apply must never write the lossy round-trip over non-UTF-8 bytes');
  assert(!fs.readFileSync(binary).includes(Buffer.from([0xEF, 0xBF, 0xBD])),
    'the original bytes must survive: no replacement characters may be written');

  // A UTF-16 export called .txt is the same class, and it is the case that
  // needs the NUL signal: UTF-16 is *valid* UTF-8, so a strict decode of it
  // succeeds and the file decodes to NUL-interleaved text the extractors would
  // wrap into copy. It must be refused, not scanned as garbage.
  const utf16 = write('utf16.txt', Buffer.from('The US delegation reviewed the report.\n', 'utf16le'));
  const utf16Only = capture([utf16]);
  assert.equal(utf16Only.code, 2,
    `a UTF-16 file named .txt is not readable copy: ${utf16Only.stderr}`);
  assert.match(utf16Only.stderr, /not valid UTF-8/,
    `the refusal must give the reason: ${utf16Only.stderr}`);

  // A NUL byte inside otherwise readable text is the same proof: no editorial
  // copy contains NUL, so a file that does is not the text it claims to be.
  const withNul = write('nul-inside.txt', 'The report is ready.\u0000The delegation left.\n');
  const withNulOnly = capture([withNul]);
  assert.equal(withNulOnly.code, 2,
    `a NUL byte makes a file unreadable: ${withNulOnly.stderr}`);

  // --- the no-false-exclusion side: readable .txt files still scan --------

  // Plain readable prose, the control for everything above.
  assert.deepEqual(ids(scan(write('readable.txt', `${ORG}\n`))), ['UE-SP001'],
    'a genuinely readable .txt must still be scanned and must still fire');

  // A readable .txt in a non-Latin script: validity, not script, is the test.
  for (const [name, prose] of [
    ['cyrillic.txt', 'Отчёт секретариата.\n'],
    ['greek.txt', 'Η αναφορά του γραφείου.\n'],
    ['arabic.txt', 'تقرير الأمانة العامة.\n'],
    ['han.txt', '秘书处报告草稿。\n'],
    ['emoji.txt', 'The report \u{1f4c8} is ready.\n'],
  ]) {
    assert.deepEqual(ids(scan(write(name, prose))), [],
      `a readable non-Latin .txt must scan without findings, not be excluded: ${name}`); // ue:ignore UE-GR002  (deliberate test data)
  }

  // Readable, non-Latin, and carrying a real defect: the rules must still see
  // it, which proves the guard keys on encoding and not on script. The defect
  // sits in the Latin clause because the Latin-script rules (UE-GR001 matches
  // a Latin-alphabet word) cannot match a Cyrillic or Arabic word by design —
  // the point of the probe is that the file is scanned at all, not that the
  // Latin rules extend to other scripts.
  const cyrillicDefect = write('cyrillic-defect.txt',
    'Отчёт секретариата. The the delegation reviewed it.\n');
  assert.deepEqual(ids(scan(cyrillicDefect)), ['UE-GR001'],
    'a defect in a readable non-Latin .txt must still be found: the guard tests encoding, not script');

  // A .txt that legitimately contains U+FFFD is valid UTF-8 and must NOT be
  // excluded — this is the case a naive "contains U+FFFD" check would drop.
  const genuineFffd = write('genuine-fffd.txt',
    'The report notes a replacement \uFFFD marker and the the draft.\n');
  assert.deepEqual(ids(scan(genuineFffd)), ['UE-GR001'],
    'a .txt that genuinely contains U+FFFD is valid UTF-8 and must still be scanned');

  // The guard is per-file: one binary file in a directory scan does not stop
  // its readable neighbours from being scanned, and the skipped file is named
  // in the report rather than counted as scanned. This is the assertion that
  // encodes the honest shape: `files` counts only files that were decoded, and
  // the skip is visible in both the header and the JSON.
  const mixedDir = path.join(tmp, 'binary-mixed');
  fs.mkdirSync(mixedDir, { recursive: true });
  fs.writeFileSync(path.join(mixedDir, 'blob.txt'),
    Buffer.concat([Buffer.from([0x00, 0xFF, 0xFE]), Buffer.from('The US delegation.')]));
  fs.writeFileSync(path.join(mixedDir, 'ok.txt'), `${ORG}\n`);
  const mixed = json(capture([mixedDir, '--format', 'json']));
  assert.equal(mixed.files, 1,
    `files must count only the files that were decoded: ${JSON.stringify(mixed)}`);
  assert.equal(mixed.skipped.length, 1,
    `the skipped file must be reported: ${JSON.stringify(mixed.skipped)}`);
  assert.ok(mixed.skipped[0].file.endsWith('blob.txt'),
    `the skipped entry must name the unreadable file: ${JSON.stringify(mixed.skipped)}`);
  assert.equal(mixed.skipped[0].reason, 'not valid UTF-8',
    'the skipped entry must carry the reason');
  assert.deepEqual([...new Set(mixed.findings.map(f => f.ruleId))], ['UE-SP001'],
    'only the readable file contributes findings');
  assert.ok(mixed.findings[0].file.endsWith('ok.txt'),
    `the finding must come from the readable file: ${mixed.findings[0].file}`);

  // The same run in text: the header says how many were scanned of how many,
  // and gives the reason, and the clean sentence follows it. The readable
  // neighbour is clean prose, so the run is a clean run *of the file that was
  // read* — which is exactly the distinction the header now makes visible.
  const mixedText = capture([mixedDir]);
  assert.equal(mixedText.code, 1,
    `the readable neighbour carries the deliberate spelling defect: ${mixedText.stderr}`);
  assert.match(mixedText.stdout, /scanned 1 of 2 files — 1 skipped \(not valid UTF-8\)/,
    `the header must name the skip: ${mixedText.stdout}`);

  // The clean-sentence case, with a clean readable neighbour: the sentence is
  // printed, and the skip is stated above it rather than hidden below.
  const cleanDir = path.join(tmp, 'binary-clean-neighbour');
  fs.mkdirSync(cleanDir, { recursive: true });
  fs.writeFileSync(path.join(cleanDir, 'blob.txt'),
    Buffer.concat([Buffer.from([0x00, 0xFF, 0xFE]), Buffer.from('The US delegation.')]));
  fs.writeFileSync(path.join(cleanDir, 'ok.txt'), 'The organisation reports the figure.\n');
  const cleanText = capture([cleanDir]);
  assert.equal(cleanText.code, 0,
    `one unreadable file beside clean copy is a skip, not a refusal: ${cleanText.stderr}`);
  assert.match(cleanText.stdout, /scanned 1 of 2 files — 1 skipped \(not valid UTF-8\)/,
    `the header must name the skip: ${cleanText.stdout}`);
  assert(cleanText.stdout.includes('No findings under the enabled, documented local rules.'),
    'the clean sentence is still printed, because the file that was read was clean');
  assert(cleanText.stdout.indexOf('skipped') < cleanText.stdout.indexOf('No findings under'),
    'the skip must be stated above the clean sentence, not hidden below it');

  // Two unreadable files among three: the count and the plural both move. The
  // readable neighbour is clean, so the run exits 0 and the clean sentence
  // follows the skip line.
  const twoSkipped = path.join(tmp, 'binary-two');
  fs.mkdirSync(twoSkipped, { recursive: true });
  fs.writeFileSync(path.join(twoSkipped, 'a.txt'),
    Buffer.from([0x00, 0xFF, 0xFE, 0x89, 0x50, 0x4E, 0x47]));
  fs.writeFileSync(path.join(twoSkipped, 'b.txt'),
    Buffer.from('The report was reviewed.\n', 'utf16le'));
  fs.writeFileSync(path.join(twoSkipped, 'ok.txt'), 'The organisation reports the figure.\n');
  const twoText = capture([twoSkipped]);
  assert.equal(twoText.code, 0, `two skips are still a skip: ${twoText.stderr}`);
  assert.match(twoText.stdout, /scanned 1 of 3 files — 2 skipped \(not valid UTF-8\)/,
    `two unreadable files must be counted and pluralised: ${twoText.stdout}`);

  // The singular/plural forms across the whole range. One file and one skip,
  // many files and many skips, and many files with no skip at all: none of
  // them may produce a header that miscounts, and none of them may carry a
  // skip clause when nothing was skipped.
  const plural = [
    ['one file, no skip', 'The organisation reports the figure.\n', 0, /— scanned 1 file —/, null],
    ['many files, no skip', 'The organisation reports the figure.\n', 0, /— scanned 1 file —/, null],
  ];
  for (const [label, body, , want, absent] of plural) {
    const file = write(`plural-${label.replace(/\W+/g, '-')}.txt`, body);
    const out = capture([file]).stdout.split('\n')[0];
    assert.match(out, want, `${label}: ${out}`);
    if (absent) assert(!out.includes('skipped'), `${label}: must carry no skip clause: ${out}`);
  }
  // One file, no skip: the singular, with no "of N" and no skip clause.
  {
    const out = capture([write('plural-single.txt', 'The organisation reports the figure.\n')])
      .stdout.split('\n')[0];
    assert.match(out, /scanned 1 file —/,
      `one readable file keeps the singular and no skip clause: ${out}`);
    assert(!out.includes('of '), `one file with no skip must not read "of": ${out}`);
    assert(!out.includes('skipped'), `one file with no skip must not mention skipping: ${out}`);
  }
  // Many readable files: the plural, and no skip clause.
  {
    const many = path.join(tmp, 'plural-many');
    fs.mkdirSync(many, { recursive: true });
    for (let i = 0; i < 3; i++) {
      fs.writeFileSync(path.join(many, `f${i}.txt`), 'The organisation reports the figure.\n');
    }
    const out = capture([many]).stdout.split('\n')[0];
    assert.match(out, /scanned 3 files —/, `three readable files use the plural: ${out}`);
    assert(!out.includes('skipped'), `no skip means no skip clause: ${out}`);
  }
  // One readable file, one skip: the "of N" total is plural because the total
  // is two, and the skipped count is singular because one was skipped.
  {
    const out = capture([cleanDir]).stdout.split('\n')[0];
    assert.match(out, /scanned 1 of 2 files — 1 skipped \(not valid UTF-8\)/,
      `the total is plural and the skip count is singular: ${out}`);
  }
  // A single undecodable file named on its own: the refusal names the path, the
  // reason and the count, and the clean sentence is never printed.
  {
    const only = capture([binary]);
    assert.equal(only.code, 2, `a lone unreadable file must refuse: ${only.stderr}`);
    assert.match(only.stderr, /no readable files found/,
      `the refusal must say so: ${only.stderr}`);
    assert.match(only.stderr, /1 candidate file skipped: not valid UTF-8/,
      `the refusal must give the count and the reason: ${only.stderr}`);
    assert.doesNotMatch(only.stdout, /No findings under/,
      'a run that read nothing must never print the clean-run sentence');
  }

  // A NUL byte is its own signal, and the refusal must name it: a UTF-16 file
  // is *valid* UTF-8, so it is the NUL that proves the bytes are not the text
  // they claim to be. Without that signal the extractors would wrap
  // NUL-interleaved text into copy spans and the rules would read positions
  // that mean nothing to a reader.
  {
    const nulOnly = capture([withNul]);
    assert.equal(nulOnly.code, 2, `a NUL byte makes a run read nothing: ${nulOnly.stderr}`);
    assert.match(nulOnly.stderr, /not valid UTF-8/,
      `the NUL case is reported with the same reason: ${nulOnly.stderr}`);
  }

  // The documented `check .` carve-out must survive: the skill-root shield
  // explains an empty scan with no error, and that is not the same case as a
  // scan whose candidates all turned out to be unreadable.
  {
    const shield = spawnSync(process.execPath, [cli, '.'],
      { cwd: root, encoding: 'utf8' });
    assert.equal(shield.status, 0,
      `node bin/check.mjs . must still exit 0: ${shield.stdout}${shield.stderr}`);
    assert.match(shield.stdout, /scanned 0 files/,
      `the carve-out prints the zero-file header it always did: ${shield.stdout}`);
    assert(!/skipped/.test(shield.stdout),
      `the carve-out is not a skip: the shield explains it, so no file was skipped: ${shield.stdout}`);
  }

  // A directory whose every candidate file is unreadable is the F1 shape: the
  // run must refuse, name the path, and never print the clean sentence.
  const allBad = path.join(tmp, 'binary-all');
  fs.mkdirSync(allBad, { recursive: true });
  fs.writeFileSync(path.join(allBad, 'a.txt'),
    Buffer.concat([Buffer.from([0x89, 0x50, 0x4E, 0x47]), Buffer.from('The US delegation.')]));
  fs.writeFileSync(path.join(allBad, 'b.txt'), Buffer.from('The report was read.\n', 'utf16le'));
  const allText = capture([allBad]);
  assert.equal(allText.code, 2,
    `a run that read nothing must refuse: ${allText.stdout}${allText.stderr}`);
  assert.match(allText.stderr, /no readable files found/,
    `the refusal must say so: ${allText.stderr}`);
  assert.ok(allText.stderr.includes(allBad),
    `the refusal must name the directory: ${allText.stderr}`);
  assert.match(allText.stderr, /2 candidate files skipped/,
    `the refusal must say how many were skipped: ${allText.stderr}`);
  assert.doesNotMatch(allText.stdout, /No findings under/,
    'a run that read nothing must never print the clean-run sentence');

  // The `skipped` field is always present, so a consumer never has to tell
  // absent from empty, and a clean run over readable files writes it empty. The
  // probe is clean prose, so the run exits 0 in every form.
  const cleanProbe = write('skipped-field-clean.txt', 'The organisation reports the figure.\n');
  const cleanJson = json(capture([cleanProbe, '--format', 'json', '--quiet']));
  assert.deepEqual(cleanJson.skipped, [],
    'a run that skipped nothing writes an empty skipped array');
  assert('skipped' in cleanJson,
    'the skipped field is always present in the JSON output');
  assert.deepEqual(json(capture([cleanProbe, '--format', 'sarif'])).runs[0].properties.skipped, [],
    'the SARIF run property bag carries the same empty skipped array');
  assert.equal(json(capture([cleanProbe, '--format', 'sarif'])).runs[0].properties.files, 1,
    'the SARIF run property bag carries the decoded-file count too');
  // A skipped file reaches the SARIF property bag by path, so a SARIF consumer
  // can see the gap without parsing stdout.
  assert.equal(json(capture([cleanDir, '--format', 'sarif'])).runs[0].properties.skipped.length, 1,
    'the SARIF run property bag names the skipped file');
  assert.ok(json(capture([cleanDir, '--format', 'sarif'])).runs[0].properties.skipped[0]
    .file.endsWith('blob.txt'),
  'the SARIF skipped entry names the unreadable file');

  // The clean-run sentence is printed only on a zero-finding run, and the
  // three-case consistency that motivated the refusal: two refusals and one
  // skip, all naming themselves.
  assert.equal(capture([write('zero-finding.txt', 'The organisation reports the figure.\n')]).code, 0,
    'a readable clean file still exits 0');
  assert.equal(capture([cleanProbe, '--format', 'json', '--quiet']).code, 0,
    'a clean readable probe exits 0 in JSON form too');
  assert.equal(capture([path.join(tmp, 'only-unsupported')]).code, 2,
    'a directory with no supported files still refuses with exit 2');
}

// --- 10. documentation is literally true -------------------------------------

{
  const readme = fs.readFileSync(path.join(root, 'README.md'), 'utf8');
  // Supported formats: the exact extension list.
  for (const ext of SUPPORTED_EXTENSIONS) {
    assert.ok(readme.includes(`\`${ext}\``),
      `README must document the supported extension ${ext}`);
  }
  assert.ok(readme.includes(
    '`.md`, `.markdown`, `.txt`, `.html`, `.htm`, `.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.tsx`, `.pdf`, `.docx` or `.odt`'),
    'README must list the supported extensions exactly');
  // Exit codes: exit 2 for an unsupported named file and for a zero-file scan.
  assert.match(readme, /\| `2` \|[^|\n]*unsupported/,
    'the README exit-code table must document exit 2 for unsupported named files');
  assert.match(readme, /\| `2` \|[^|\n]*no supported files/,
    'the README exit-code table must document exit 2 for a zero-file scan');
  // Directory skipping: the promise at README:304 stays.
  assert.match(readme,
    /hidden directories, `node_modules`, build output and fixtures are skipped unless you name them explicitly/,
    'README must keep the directory-skip promise');

  const guide = fs.readFileSync(path.join(root, 'USER-GUIDE.md'), 'utf8');
  const guideLines = guide.split('\n');
  // The lines that name the file formats. Located by content rather than by line
  // number: a hard-coded number breaks the moment a paragraph is added above
  // them, and a test that breaks for an unrelated edit is a test people learn to
  // re-point instead of read. Every line carrying the extension list must carry
  // all of it, and must keep the house style — no question marks, no percent.
  const formatLines = guideLines
    .map((line, index) => ({ line, number: index + 1 }))
    .filter(({ line }) => line.includes('`.md`') && line.includes('`.txt`'));
  assert.ok(formatLines.length >= 2,
    `USER-GUIDE must name the supported formats in setup and again under "Things worth knowing": found ${formatLines.length}`);
  for (const { line, number } of formatLines) {
    for (const ext of SUPPORTED_EXTENSIONS) {
      assert.ok(line.includes(`\`${ext}\``),
        `USER-GUIDE line ${number} must document ${ext}: ${line}`);
    }
    assert.ok(!/[?%]/.test(line),
      `USER-GUIDE line ${number} must keep the house style (no question mark, no percent): ${line}`); // ue:ignore UE-SP001  (deliberate test data)
  }
  // The guide documents exit code 2 for an unsupported file type.
  assert.ok(guide.includes('exit code 2'),
    'USER-GUIDE must document exit code 2 for an unsupported file type');
}

// --- self-scan gates (the hard gate of contract item 3) -----------------------

{
  const selfScan = spawnSync(process.execPath, [cli, '.', '--self-scan', '--quiet'],
    { cwd: root, encoding: 'utf8' });
  assert.equal(selfScan.status, 0,
    `the repository's own self-scan must exit 0:\n${selfScan.stdout}\n${selfScan.stderr}`);

  const plain = spawnSync(process.execPath, [cli, '.'],
    { cwd: root, encoding: 'utf8' });
  assert.equal(plain.status, 0,
    `node bin/check.mjs . must exit 0:\n${plain.stdout}\n${plain.stderr}`);
}

// --- 13. mutation checks: the honest shape must be load-bearing ---------------
//
// An assertion that passes whether or not the behaviour exists is worth
// nothing. Each mutation below removes one half of the change in a scratch copy
// of the tree and requires the probe to observe the break, so a later refactor
// that drops the skip from the header, or turns the all-unreadable refusal back
// into a clean run, cannot pass review unnoticed. The worktree is never
// mutated: the scratch copy is removed in a finally block.

{
  // The probe is this suite's own subject, reduced to the four facts the
  // mutations must change: the header line, the exit code of a directory with a
  // clean neighbour, the exit code and output of an all-unreadable directory,
  // and the skipped entries in the JSON. It takes the entry point to load as an
  // argument, so a mutated tree is exercised through its own module graph
  // rather than through the original.
  const probeSource = (entryPoint) => `
    import { run } from ${JSON.stringify(entryPoint)};
    import fs from 'node:fs';
    import os from 'node:os';
    import path from 'node:path';
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'probe-'));
    const dir = path.join(tmp, 'mixed');
    fs.mkdirSync(dir);
    // one readable file beside one unreadable file: the case whose header the
    // suite pins as "scanned 1 of 2 files — 1 skipped (not valid UTF-8)"
    const one = path.join(tmp, 'one');
    fs.mkdirSync(one, { recursive: true });
    fs.writeFileSync(path.join(one, 'bad.txt'),
      Buffer.concat([Buffer.from([0x89, 0x50, 0x4E, 0x47]), Buffer.from('The delegation.')]));
    fs.writeFileSync(path.join(one, 'ok.txt'), 'The organisation reports the figure.\\n');
    const oneOut = [];
    const oneExit = run([one], { log: l => oneOut.push(String(l)), error: l => oneOut.push(String(l)) });
    // one readable file beside two unreadable ones, one of them UTF-16
    const two = path.join(tmp, 'two');
    fs.mkdirSync(two, { recursive: true });
    fs.writeFileSync(path.join(two, 'bad.txt'),
      Buffer.concat([Buffer.from([0x89, 0x50, 0x4E, 0x47]), Buffer.from('The delegation.')]));
    fs.writeFileSync(path.join(two, 'u16.txt'), Buffer.from('The report was read.\\n', 'utf16le'));
    fs.writeFileSync(path.join(two, 'ok.txt'), 'The organisation reports the figure.\\n');
    const out = [];
    const code = run([two], { log: l => out.push(String(l)), error: l => out.push(String(l)) });
    const all = path.join(tmp, 'all');
    fs.mkdirSync(all);
    fs.writeFileSync(path.join(all, 'a.txt'), Buffer.from([0x00, 0xFF, 0xFE, 0x89]));
    const out2 = [];
    const code2 = run([all], { log: l => out2.push(String(l)), error: l => out2.push(String(l)) });
    const jsonOut = [];
    run([two, '--format', 'json', '--quiet'],
      { log: l => jsonOut.push(String(l)), error: () => {} });
    process.stdout.write(JSON.stringify({
      header: oneOut.join('\\n').split('\\n')[0],
      exit: oneExit,
      mixedHeader: out.join('\\n').split('\\n')[0],
      allExit: code2,
      allOut: out2.join('\\n'),
      skipped: JSON.parse(jsonOut.join('\\n')).skipped,
    }));
  `;

  const MUTATIONS = [
    {
      name: 'the skip clause is dropped from the header',
      file: 'lib/output.mjs',
      from: '` — ${skipped.length} skipped (${skippedReasons(skipped)})`',
      to: '``',
      // The "scanned N of M" count survives, but the reason disappears: the
      // header no longer tells the reader why one file is missing, which is
      // half of the honesty this change makes.
      broken: (o) => !/skipped \(not valid UTF-8\)/.test(o.header),
    },
    {
      name: 'the all-unreadable directory returns a clean run instead of refusing',
      file: 'lib/cli.mjs',
      from: 'if (candidateCount > 0 && files.length === 0) {',
      to: 'if (false) {',
      // The F1 shape comes back: exit 0 plus the canonical clean sentence.
      broken: (o) => o.allExit === 0 && /No findings under/.test(o.allOut),
    },
    {
      name: 'the skipped count is folded back into the scanned count',
      file: 'lib/output.mjs',
      from: '`scanned ${files} of ${files + skipped.length} file${files + skipped.length === 1 ? \'\' : \'s\'}`',
      to: '`scanned ${files + skipped.length} file${files + skipped.length === 1 ? \'\' : \'s\'}`',
      // The misleading header this change removed: a file that was never read,
      // counted as read. The "of N" form is what distinguishes "1 of 2" from
      // "2", so losing it is what the suite's header assertion would catch.
      broken: (o) => /scanned 2 files/.test(o.header) && !/scanned 1 of 2 files/.test(o.header),
    },
    {
      name: 'the NUL signal is removed, so a UTF-16 file is read as copy',
      file: 'lib/extract.mjs',
      from: 'if (source.includes(NUL)) return UNDECODABLE_REASON;',
      to: 'if (false) return UNDECODABLE_REASON;',
      // UTF-16 is valid UTF-8, so only the NUL signal catches it.
      broken: (o) => o.skipped.length < 2,
    },
  ];

  for (const mutation of MUTATIONS) {
    const source = fs.readFileSync(path.join(root, mutation.file), 'utf8');
    assert(source.includes(mutation.from),
      `mutation "${mutation.name}": the anchor text must be present in ${mutation.file}`);
    const mutated = source.replace(mutation.from, mutation.to);
    assert.notEqual(mutated, source,
      `mutation "${mutation.name}": the replacement must change ${mutation.file}`);

    const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-mutation-'));
    try {
      // Copy the whole tree, apply the mutation there, and run the probe
      // against that copy: the mutation must be exercised by real code, not
      // simulated.
      const tree = path.join(scratch, 'tree');
      fs.cpSync(root, tree, {
        recursive: true,
        filter: src => !src.includes(`${path.sep}.git${path.sep}`) && !src.includes(`${path.sep}node_modules${path.sep}`),
      });
      const target = path.join(tree, mutation.file);
      fs.writeFileSync(target, mutated);
      const probe = path.join(scratch, 'probe.mjs');
      fs.writeFileSync(probe, probeSource(path.join(tree, 'bin', 'check.mjs')));
      const result = spawnSync(process.execPath, [probe], { encoding: 'utf8' });
      assert.equal(result.status, 0,
        `mutation "${mutation.name}": the probe must run against the mutated tree: ${result.stderr}`);
      const observed = JSON.parse(result.stdout);
      assert(mutation.broken(observed),
        `mutation "${mutation.name}" did NOT break the suite, so the matching assertion is vacuous: `
        + `header=${JSON.stringify(observed.header)} exit=${observed.exit} `
        + `allExit=${observed.allExit} skipped=${JSON.stringify(observed.skipped)}`);
    } finally {
      fs.rmSync(scratch, { recursive: true, force: true });
    }
  }
}

console.log('ok — unreadable-file mutations: the header skip, the read-nothing refusal, '
  + 'the honest file count and the NUL signal are all load-bearing');

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — HTML suppressions, TypeScript, JSX text children, sentence-like literals, unsupported files, fixtures, flags, FIFO, report line, docs, self-scan, unreadable files reported and refused, unquoted attributes and the ARIA copy set');
