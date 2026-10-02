// un-editorial-check — W4 contract tests: extraction depth, context metadata
// and malformed-HTML recovery (remediation brief §6, Wave 4 agent C).
//
// Self-contained: its own tmpdir, its own CLI invocations through the same
// in-process `run` entry point tests/run.mjs uses. Nothing is ever written
// inside the repository (the checker self-scans the repository, and a test
// document inside it would be scanned as copy).
//
// Run standalone: node tests/audit-depth.mjs
//
// Covered contract items:
//   1. the authored / quoted / cited / code / nav / metadata context taxonomy
//      on extracted units;
//   2. heading and list-item flags on extracted units;
//   3. scan coverage: headings, lists, tables, captions, dialog content,
//      accessible labels, title / meta / og / twitter copy, blockquotes and
//      cited titles;
//   4. finding.context propagation from unit to JSON output;
//   5. malformed HTML: unclosed and mis-nested markup, entities, inline
//      scripts, an unterminated comment — extraction recovers, never throws;
//   6. locked limitations: Markdown / TXT quotations and <cite> content stay
//      out of reach (blockquote coverage is HTML-only).

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { run } from '../bin/check.mjs';
import { extractHTML } from '../lib/extract-html.mjs';
import { extractMarkdown } from '../lib/extract-markdown.mjs';
import { extractText } from '../lib/extract-text.mjs';
import { extractJS } from '../lib/extract-js.mjs';
import { lineStarts } from '../lib/position.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-depth-'));

// Deliberate rule-violating test data. This constant carries a same-line
// `ue:ignore` so the repository's own self-scan stays clean however the
// sentence-like-literal rule classifies this file's own source.
const ORG = 'The organization reports quarterly.'; // ue:ignore UE-SP001  (deliberate test data)

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
const scan = (file, ...extra) => capture([file, '--format', 'json', ...extra]);

// Extract units directly, without running any rule, so the taxonomy can be
// asserted independently of detection.
const unitsOf = (source, filePath) => {
  const starts = lineStarts(source);
  const ext = path.extname(filePath).toLowerCase();
  if (ext === '.html' || ext === '.htm') return extractHTML(source, filePath, { starts });
  if (ext === '.md' || ext === '.markdown') return extractMarkdown(source, filePath, { starts });
  if (ext === '.txt') return extractText(source, filePath, { starts });
  return extractJS(source, filePath, { starts, offsetBase: 0 });
};
const findUnit = (list, needle) => {
  const unit = list.find(entry => entry.text.includes(needle));
  assert(unit, `no unit contains "${needle}" in: ${list.map(u => u.text).join(' | ')}`);
  return unit;
};

// --- 1. context taxonomy -----------------------------------------------------

{
  const html = [
    '<p>Authored paragraph copy.</p>',
    '<nav><a href="/">Navigation label</a></nav>',
    '<aside>Sidebar navigation note.</aside>',
    '<blockquote><p>Quoted block material</p></blockquote>',
    '<q>Short inline quotation</q>',
    '<cite>Cited title text</cite>',
    '<p>Mixed <cite>cited part</cite> and authored part.</p>',
    '<nav><blockquote>Quoted wins inside navigation</blockquote></nav>',
    '<blockquote><cite>Cited wins inside quotation</cite></blockquote>',
  ].join('\n');
  const list = unitsOf(html, 'taxonomy.html');
  assert.equal(findUnit(list, 'Authored paragraph').context, 'authored');
  assert.equal(findUnit(list, 'Navigation label').context, 'nav');
  assert.equal(findUnit(list, 'Sidebar navigation').context, 'nav');
  assert.equal(findUnit(list, 'Quoted block material').context, 'quoted');
  assert.equal(findUnit(list, 'Short inline quotation').context, 'quoted');
  assert.equal(findUnit(list, 'Cited title text').context, 'cited');
  assert.equal(findUnit(list, 'cited part').context, 'cited');
  assert.equal(findUnit(list, 'authored part').context, 'authored');
  // Precedence: citation beats quotation beats navigation beats authored.
  assert.equal(findUnit(list, 'Quoted wins inside navigation').context, 'quoted');
  assert.equal(findUnit(list, 'Cited wins inside quotation').context, 'cited');

  // Copy-bearing attributes: alt is authored copy, interface labels are nav.
  const attrs = [
    '<img src="chart.png" alt="Alt text for the chart" aria-label="Accessible label copy">',
    '<input type="text" placeholder="Placeholder interface copy">',
    '<span title="Tooltip interface copy">Body</span>',
    '<button value="Button interface label"></button>',
  ].join('\n');
  const attrUnits = unitsOf(attrs, 'attributes.html');
  assert.equal(findUnit(attrUnits, 'Alt text for the chart').context, 'authored');
  assert.equal(findUnit(attrUnits, 'Accessible label copy').context, 'nav');
  assert.equal(findUnit(attrUnits, 'Placeholder interface copy').context, 'nav');
  assert.equal(findUnit(attrUnits, 'Tooltip interface copy').context, 'nav');
  assert.equal(findUnit(attrUnits, 'Button interface label').context, 'nav');

  // Title, meta description and social copy are page metadata.
  const head = [
    '<title>Page title copy</title>',
    '<meta name="description" content="Meta description copy">',
    '<meta property="og:title" content="Open graph title copy">',
    '<meta name="twitter:description" content="Twitter description copy">',
  ].join('');
  const headUnits = unitsOf(head, 'head.html');
  assert.equal(findUnit(headUnits, 'Page title copy').context, 'metadata');
  assert.equal(findUnit(headUnits, 'Meta description copy').context, 'metadata');
  assert.equal(findUnit(headUnits, 'Open graph title copy').context, 'metadata');
  assert.equal(findUnit(headUnits, 'Twitter description copy').context, 'metadata');

  // Markdown, plain text and JavaScript surfaces.
  assert.equal(unitsOf('A plain authored paragraph.\n', 'body.md')[0].context, 'authored');
  assert.equal(unitsOf('A plain authored paragraph.\n', 'body.txt')[0].context, 'authored');
  const js = unitsOf(`const label = "${ORG}";\n`, 'script.js');
  assert.equal(js[0].context, 'code');
}

console.log('ok — context taxonomy: authored, quoted, cited, code, nav, metadata');

// --- 2. heading and list-item flags ------------------------------------------

{
  const html = '<h2>Section heading</h2><ul><li>List item copy</li></ul><p>Plain paragraph</p>';
  const list = unitsOf(html, 'flags.html');
  assert.equal(findUnit(list, 'Section heading').heading, true, 'an h2 must be flagged as a heading');
  assert.equal(findUnit(list, 'Section heading').listItem, undefined);
  assert.equal(findUnit(list, 'List item copy').listItem, true, 'an li must be flagged as a list item');
  assert.equal(findUnit(list, 'List item copy').heading, undefined);
  assert.equal(findUnit(list, 'Plain paragraph').heading, undefined);
  assert.equal(findUnit(list, 'Plain paragraph').listItem, undefined);

  // Definition lists count as list items too.
  const dl = unitsOf('<dl><dt>Term label</dt><dd>Definition copy</dd></dl>', 'dl.html');
  assert.equal(findUnit(dl, 'Term label').listItem, true);
  assert.equal(findUnit(dl, 'Definition copy').listItem, true);

  // Markdown ATX headings and list markers.
  const md = ['# Report heading', '', '- Item copy', '', 'Plain paragraph', ''].join('\n');
  const mdUnits = unitsOf(md, 'flags.md');
  assert.equal(findUnit(mdUnits, 'Report heading').heading, true);
  assert.equal(findUnit(mdUnits, 'Item copy').listItem, true);
  assert.equal(findUnit(mdUnits, 'Plain paragraph').heading, undefined);
  assert.equal(findUnit(mdUnits, 'Plain paragraph').listItem, undefined);

  // Plain text carries no structural flags at all.
  const txt = unitsOf('A plain paragraph.\n', 'flags.txt');
  assert.equal(txt[0].heading, undefined);
  assert.equal(txt[0].listItem, undefined);
}

console.log('ok — heading and list-item flags on HTML and Markdown units');

// --- 3. scan coverage: every surface brief §6 names produces a unit ----------

{
  const surfaces = [
    '<h1>Heading surface marker</h1>',
    '<ul><li>List surface marker</li></ul>',
    '<table><caption>Caption surface marker</caption><tr><th>Header cell marker</th></tr><tr><td>Body cell marker</td></tr></table>',
    '<figure><img src="x.png" alt="Image alt marker"><figcaption>Figure caption marker</figcaption></figure>',
    '<dialog><p>Panel content marker</p></dialog>',
    '<button aria-label="Accessible button marker">OK</button>',
    '<title>Title surface marker</title>',
    '<meta name="description" content="Meta surface marker">',
    '<blockquote><p>Blockquote surface marker</p></blockquote>',
    '<cite>Cited surface marker</cite>',
  ].join('\n');
  const list = unitsOf(surfaces, 'surfaces.html');
  for (const marker of [
    'Heading surface marker', 'List surface marker', 'Caption surface marker',
    'Header cell marker', 'Body cell marker', 'Image alt marker',
    'Figure caption marker', 'Panel content marker', 'Accessible button marker',
    'Title surface marker', 'Meta surface marker', 'Blockquote surface marker',
    'Cited surface marker',
  ]) {
    assert(list.some(unit => unit.text.includes(marker)),
      `the ${marker} surface must produce a unit`);
  }

  // Technical surfaces still never become units.
  const technical = unitsOf(
    '<code>code() copy</code><pre>pre() copy</pre><template>template() copy</template>',
    'technical.html');
  assert.deepEqual(technical.map(unit => unit.text), [],
    'code, pre and template content must stay out of the units');
}

console.log('ok — headings, lists, tables, captions, dialog, labels, title/meta, quotes');

// --- 4. finding.context reaches JSON output ----------------------------------

{
  const authored = json(scan(write('ctx-p.html', `<p>${ORG}</p>`)));
  assert.equal(authored.findings[0].context, 'authored',
    'a finding in an authored paragraph must say so');

  const quoted = json(scan(write('ctx-q.html', `<blockquote><p>${ORG}</p></blockquote>`)));
  const quotedFinding = quoted.findings.find(f => f.ruleId === 'UE-SP001');
  assert(quotedFinding, `a blockquote must still be scanned: ${quoted.stdout}`);
  assert.equal(quotedFinding.context, 'quoted',
    'a finding inside a blockquote must carry the quoted context for the review lanes');

  const cited = json(scan(write('ctx-c.html', `<cite>${ORG}</cite>`)));
  const citedFinding = cited.findings.find(f => f.ruleId === 'UE-SP001');
  assert(citedFinding, `a cited title must still be scanned: ${cited.stdout}`);
  assert.equal(citedFinding.context, 'cited');

  const nav = json(scan(write('ctx-n.html', `<nav aria-label="${ORG}">Home</nav>`)));
  const navFinding = nav.findings.find(f => f.ruleId === 'UE-SP001');
  assert(navFinding, `an aria-label must still be scanned: ${nav.stdout}`);
  assert.equal(navFinding.context, 'nav');

  const meta = json(scan(write('ctx-m.html', `<title>${ORG}</title>`)));
  const metaFinding = meta.findings.find(f => f.ruleId === 'UE-SP001');
  assert(metaFinding, `the page title must still be scanned: ${meta.stdout}`);
  assert.equal(metaFinding.context, 'metadata');

  const js = json(scan(write('ctx.js', `const label = "${ORG}";`)));
  assert.equal(js.findings[0].context, 'code');

  const md = json(scan(write('ctx.md', `${ORG}\n`)));
  assert.equal(md.findings[0].context, 'authored');
}

console.log('ok — finding.context propagates from unit to JSON output');

// --- 5. malformed HTML recovers ----------------------------------------------

{
  // An unclosed paragraph does not swallow the copy that follows it.
  const unclosed = unitsOf('<p>First paragraph text\n<p>Second paragraph text', 'unclosed.html');
  assert(unclosed.some(u => u.text.includes('First paragraph text')));
  assert(unclosed.some(u => u.text.includes('Second paragraph text')));

  // Mis-nested inline markup: every text node is still reached exactly once.
  const nested = unitsOf('<p>Before <b>bold <i>both</b> tail</i> after</p>', 'nested.html');
  const texts = nested.map(u => u.text);
  assert(texts.some(t => t.includes('both')));
  assert(texts.some(t => t.includes('Before')));
  assert(texts.some(t => t.includes('after')));

  // Entities decode without disturbing the surviving characters.
  const entity = unitsOf('<p>A &amp; B &lt;tag&gt; organisation</p>', 'entity.html');
  const entityUnit = findUnit(entity, 'A & B');
  assert.equal(entityUnit.context, 'authored');
  assert(!entityUnit.text.includes('&amp;'), 'entities must be decoded in unit text');

  // Inline <script> payloads are still delegated to the JS extractor.
  const script = unitsOf('<p>Intro paragraph</p><script>const label = "' + ORG + '";</script>',
    'inline.html');
  const scriptUnit = findUnit(script, 'organization');
  assert.equal(scriptUnit.context, 'code', 'inline script copy must keep the code context');

  // An unterminated comment hides everything after it, without throwing.
  const comment = unitsOf('<p>Before comment</p><!-- never closed', 'comment.html');
  assert(comment.some(u => u.text.includes('Before comment')));

  // A tag soup fragment with a stray bracket never throws.
  assert.doesNotThrow(() => unitsOf('<p <p>broken</p attr>', 'soup.html'));
}

console.log('ok — malformed HTML: unclosed, mis-nested, entities, inline scripts, comment');

// --- 6. locked limitations: MD/TXT quotations and <cite> stay out of reach ----

{
  // Blockquote coverage is HTML-only: Markdown and plain-text quotation lines
  // are masked before any unit exists (locked by tests/run.mjs quotation and
  // cite locks, which must keep passing unchanged).
  assert.deepEqual(unitsOf('> The organization reports.\n', 'quote.md'), []);
  assert.deepEqual(unitsOf('> The organization reports.\n', 'quote.txt'), []);
  for (const file of ['cite.md', 'cite.txt']) {
    const list = unitsOf('See <cite>Organization of African Unity</cite> here.\n', file);
    assert(!list.some(u => u.text.includes('Organization of African Unity')),
      `${file}: cited title content must never become a unit`);
  }
}

console.log('ok — extraction depth, context metadata, malformed HTML, locked limitations');

fs.rmSync(tmp, { recursive: true, force: true });
