// Self-contained HTML report renderer — the first-class peer to the PDF,
// dispatched from --report on the path extension (.html). Input is the report
// model contract shared with lib/report.mjs: an object of { version, date,
// targets, profiles, filesCount, findings, sources }.
//
// The renderer is lane-aware: annotated findings are grouped into the five
// output lanes in lib/output.mjs order (deterministic, heuristic review,
// harmful-discriminatory, diplomacy, audit) with quoted material reported in
// its own section and counted on its own, and the audits section renders only
// when the run produced audit findings — which requires audits to have been
// requested. Every finding carries the six lane fields (lane, source, profile,
// confidence, limitation, action) beside the current-to-should-be block
// mirrored from lib/report.mjs, and the PDF's review queue is carried over
// unchanged, so nothing the PDF shows is dropped here.
//
// Contract, test-locked in tests/audit-html-report.mjs:
//   * pure — no file system, no process and no clock: identical input always
//     produces byte-identical HTML, so two runs can be diffed and hashed. The
//     scan date arrives with the input, exactly as lib/report.mjs documents;
//   * zero dependencies and no network: one file, one inline style block, no
//     scripts and no external fonts, assets or stylesheets;
//   * every piece of user text and every path passes through escapeControl
//     (lib/output.mjs) and then through HTML escaping, so a file containing
//     markup never becomes executable output;
//   * a clean scan states exactly "No findings under the enabled, documented
//     local rules." and that sentence never appears on a report carrying a
//     finding — the same rule lib/output.mjs applies to the text report.
//
// Since Phase 9 the renderer takes `opts.detail`: 'grouped' (the default)
// collapses findings that would render identically into one issue block whose
// occurrence table lists every place they were found — the groups come from
// lib/report.mjs groupIssues, so this format and the PDF agree on what one
// issue is — while 'full' is the pre-Phase-9 layout, one card per finding.
// The switch is presentation only: summary counts are computed from the
// findings before either layout runs. Two surfaces appear in both modes: the
// twelve-row category legend (lib/legend.mjs, marker code and category name
// printed together so colour is never the only signal) and the UN-style
// document furniture (lib/furniture.mjs), whose header reads EDITORIAL
// REVIEW and never UNITED NATIONS — claim row 22 promises the report never
// presents itself as United Nations endorsement.
//
// Framing wording is reused from the shipped surfaces: the three legend
// paragraphs of lib/report.mjs, the footer fragment of lib/pdf.mjs and the
// disclaimer row of docs/CLAIM-EVIDENCE-AUDIT.md, so the HTML never promises
// more than the PDF does.

import { annotate, countLanes, escapeControl, LANE_NAMES, severityCounts, summarize } from './output.mjs';
import {
  EMPTY_LANE, capLines, groupIssues, recommendations, sectionCount, sectionPlan,
} from './report.mjs';
import { categoryMarker, legendRows } from './legend.mjs';
import { categoryIcon, severityIcon, svgIcon } from './icons.mjs';
import { footerCells, headerRows, TITLE } from './furniture.mjs';
import { PALETTE } from './palette.mjs';

// Canonical clean-run sentence, restated from lib/output.mjs renderText (the
// text report prints it when no section renders; this report prints it when
// the scan produced no finding at all).
const CLEAN = 'No findings under the enabled, documented local rules.';

// A section header in the shape .feedbacks/design/build-mockup.mjs draws and
// .feedbacks/REPORT-REDESIGN-PLAN.md D5–D6 specifies: the title, the lane
// metadata and the finding count as three separate spans, so no number is
// ever part of a section's name.
function sectionHead(title, meta, count) {
  return '<h2><span class="sec-t">'
    + `${safe(title)}</span>${meta ? `<span class="sec-d">${safe(meta)}</span>` : ''}`
    + `${count ? `<span class="sec-c">${safe(count)}</span>` : ''}</h2>`;
}

// D13's cap block: the same three lines lib/report.mjs capLines builds for the
// PDF, in one bordered band so a capped section cannot be read as a section
// that simply ended. The wording is shared, not re-typed, so the two formats
// cannot promise the reader different numbers.
function capBlock(section, command) {
  const [head, promise, code] = capLines({
    shown: section.shown, total: section.total, command,
  });
  return `<div class="cap"><p class="cap-head">${safe(head)}</p>`
    + `<p>${safe(promise)}</p><pre><code>${safe(code)}</code></pre></div>`;
}

// Severity presentation, mirrored from lib/report.mjs: info and anything
// unexpected read as notes.
const SEVERITY_LABEL = { error: 'ERROR', warning: 'WARNING', info: 'NOTE' };

// Block wording, mirrored byte for byte from lib/report.mjs: a finding with no
// captured copy must not show a developer placeholder, and the fixable marker
// separates --fix-able findings from rewrites that need a human or an agent.
const NO_CONTEXT = '(not applicable)';
const MANUAL_SUFFIX = ' — manual / agent rewrite; not --fix-able';
const FIXABLE_SUFFIX = ' — --fix-able';

// The three legend paragraphs, verbatim from lib/report.mjs so the framing of
// both report formats cannot drift apart.
const LEGEND_DETERMINISTIC = 'Deterministic finding: the wording proves the defect.';
const LEGEND_HEURISTIC = 'Heuristic finding: routed to review; this report never asserts that a claim is true or false, or that any legal threshold is met.';
const LEGEND_REPORT_ONLY = 'This report changes nothing; re-run the checker to verify corrections.';
// Framing disclaimer, worded from row 22 of docs/CLAIM-EVIDENCE-AUDIT.md (the
// row states it without a closing full stop, so the sentence mark below is the
// only addition). It is the sanctioned way of saying all three of the things
// the report must not be, without ever writing one of the banned phrases.
const FRAMING = 'The report never presents itself as verification of facts, legal opinion or United Nations endorsement.';

// Inline style only: system font stacks, no @import, no url(), no external
// asset of any kind. Static, so it contributes nothing to run-to-run variance.
// Every colour is read from lib/palette.mjs, the single source of truth both
// renderers share: a role that appears twice here (the page ground and the
// inverted code block's type, the body ink and the code ground) stays two
// entries in the palette, because Stage E recolours them independently.
const STYLE = `
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin: 0; padding: 2rem 1rem; background: ${PALETTE.page.html}; color: ${PALETTE.body.html};
  font-family: Georgia, "Times New Roman", serif; line-height: 1.5; }
main { max-width: 54rem; margin: 0 auto; padding: 2rem; background: ${PALETTE.surface.html};
  border: 1px solid ${PALETTE.border.html}; }
h1 { margin: 0 0 1rem; font-size: 1.6rem; }
h2 { font-size: 1.2rem; margin: 2rem 0 0.5rem; padding-bottom: 0.25rem;
  border-bottom: 2px solid ${PALETTE.heading.html}; }
h2 .sec-t { margin-right: 0.5rem; }
h2 .sec-d { font-size: 0.72rem; font-weight: 400; color: ${PALETTE.meta.html}; /* ue:ignore UE-SP001 */
  font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; }
h2 .sec-c { float: right; font-size: 0.75rem; font-weight: 400; color: ${PALETTE.secondary.html}; /* ue:ignore UE-SP001 */
  font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; }
.empty { padding: 0.75rem 1rem; background: ${PALETTE.empty.html}; border: 1px dashed ${PALETTE.emptyBorder.html};
  color: ${PALETTE.secondary.html}; font-style: italic; }
.cap { margin: 1rem 0; padding: 0.9rem 1rem; background: ${PALETTE.callout.html};
  border: 1px solid ${PALETTE.calloutBorder.html}; }
.cap p { margin: 0.35rem 0; }
.cap .cap-head { font-weight: 700; }
.cap pre { margin: 0.6rem 0 0; padding: 0.5rem 0.6rem; background: ${PALETTE.codeGround.html};
  overflow-x: auto; }
.cap code { color: ${PALETTE.codeType.html}; /* ue:ignore UE-SP001 */
  font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
  font-size: 0.8rem; white-space: pre-wrap; overflow-wrap: anywhere; }
.reco ol { margin: 0.25rem 0 0; padding-left: 1.4rem; }
.reco li { margin: 0.35rem 0; }
h3 { font-size: 0.95rem; margin: 0.2rem 0 0.7rem; overflow-wrap: anywhere; }
dl { display: grid; grid-template-columns: 11rem minmax(0, 1fr);
  gap: 0.2rem 0.8rem; margin: 0 0 1rem; }
dt { font-weight: 700; }
dd { margin: 0; overflow-wrap: anywhere; }
hr { border: 0; border-top: 1px solid ${PALETTE.rule.html}; margin: 1rem 0; }
.counts, .lanes { margin: 0.25rem 0; font-size: 0.9rem;
  font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; }
.framing { margin: 1.5rem 0; padding: 0.75rem 1rem; background: ${PALETTE.panel.html};
  border-left: 4px solid ${PALETTE.heading.html}; }
.framing p { margin: 0.35rem 0; }
.disclaimer { font-weight: 700; }
.clean { padding: 1rem; background: ${PALETTE.clean.html}; border: 1px solid ${PALETTE.cleanBorder.html};
  font-weight: 700; }
article.finding { margin: 1rem 0; padding: 0.9rem 1rem; background: ${PALETTE.finding.html};
  border: 1px solid ${PALETTE.findingBorder.html}; border-left: 5px solid ${PALETTE.marker.html}; }
article.severity-error { border-left-color: ${PALETTE.severity.error.html}; } /* ue:ignore UE-SP001 */
article.severity-warning { border-left-color: ${PALETTE.severity.warning.html}; } /* ue:ignore UE-SP001 */
article.severity-note { border-left-color: ${PALETTE.severity.note.html}; } /* ue:ignore UE-SP001 */
article dl { margin-bottom: 0.6rem; }
article dl.fields { grid-template-columns: 7rem minmax(0, 1fr); margin-bottom: 0; }
.message, .heuristic { margin: 0.3rem 0 0.7rem; }
/* R7: a filled navy masthead, not a tinted panel with a navy border. Omar
   delegated the header treatment, and a rule alone was not holding four
   pieces of furniture together — the same block the PDF paints across the top
   of every page, so both formats open with one. The reversed type is white on
   the masthead's own value, which is 11.69:1 (tests/palette.mjs names the
   hexes; this file names none of them). */
.doc-header { margin: 0 0 1.5rem; padding: 0.6rem 0.9rem; background: ${PALETTE.masthead.html};
  border: 1px solid ${PALETTE.divider.html}; }
/* Each header row is two cells pushed to the edges, exactly as the plan's
   mockup draws them: the left cell reads from the left margin and the right
   cell from the right, so the boundary word sits against the tool name rather
   than wherever the text happens to run out. */
.doc-header p { display: flex; justify-content: space-between; gap: 0.5rem 1rem;
  margin: 0.15rem 0; font-size: 0.85rem; letter-spacing: 0.04em; color: ${PALETTE.onChip.html}; } /* ue:ignore UE-SP001 */
.doc-header .r { text-align: right; }
/* D11: the row's marks are vector artwork, never a glyph and never an icon
   font — the file stays self-contained, and nothing has to be fetched to draw
   a severity or a category. That paint is what the artwork draws with: the
   severity shape takes it directly, the category shape takes it unless a
   knockout inside it is meant to read as white. */
.icon { display: inline-block; width: 13px; height: 13px; margin-right: 0.35em;
  vertical-align: -2px; color: ${PALETTE.icon.html}; } /* ue:ignore UE-SP001 */
.marker { display: inline-block; min-width: 1.7em; padding: 0 0.3em; margin-right: 0.4em;
  background: ${PALETTE.marker.html}; color: ${PALETTE.onChip.html}; border-radius: 2px; vertical-align: baseline;
  font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
  font-size: 0.72rem; font-weight: 700; line-height: 1.7; text-align: center; } /* ue:ignore UE-SP001 */
.count { margin: 0.3rem 0 0.4rem; font-weight: 700; font-size: 0.9rem; }
table { border-collapse: collapse; width: 100%; margin: 0.5rem 0 0.3rem; font-size: 0.9rem; }
th, td { border: 1px solid ${PALETTE.rule.html}; padding: 0.3rem 0.45rem; text-align: left;
  vertical-align: top; overflow-wrap: anywhere; }
/* overflow-wrap: anywhere belongs to the cells, which carry user text that
   may need breaking anywhere, and not to the header labels, which are fixed
   short words. On a th it split "Location" across two lines in the
   occurrence table. */
th { background: ${PALETTE.tableHead.html}; font-size: 0.85rem; overflow-wrap: normal; }
.legend th, .legend td { font-size: 0.85rem; }
/* The footer is three columns, left, centre and right — decision D3, drawn
   from the same grid the plan's mockup uses. */
footer { max-width: 54rem; margin: 1rem auto 0; display: grid;
  grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem; color: ${PALETTE.footer.html}; /* ue:ignore UE-SP001 */
  font-size: 0.85rem; }
footer .c { text-align: center; } /* ue:ignore UE-SP001 */
footer .r { text-align: right; overflow-wrap: anywhere; }
ul { margin: 0 0 1rem; padding-left: 1.4rem; }
li { margin: 0.2rem 0; overflow-wrap: anywhere; }
`;

/**
 * HTML-escape every markup character. Applied to every piece of user text and
 * every path through `safe` below, so hostile copy is displayed, never parsed.
 */
function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/** Neutralise terminal and bidi control characters, then HTML-escape. */
function safe(value) {
  return escapeHtml(escapeControl(String(value)));
}

function pushRow(parts, label, value) {
  parts.push(`<dt>${safe(label)}</dt><dd>${safe(value)}</dd>`);
}

// One card per finding, mirroring the lib/report.mjs block: severity banner,
// current text, should-be guidance with its fixable marker, the full
// explanation, the audit marker when present, the heuristic note, then the six
// lane rows (lane, source, profile, confidence, limitation, action) that close
// the block. The file position is its own row because lane sections span
// files, where the PDF has a heading per file instead.
// Report order inside a lane: files in first-appearance order, then line,
// then column — the same ordering lib/report.mjs applies inside each file
// group, restated here because lane sections span files.
function orderFindings(list) {
  const files = new Map();
  for (const finding of list) {
    if (!files.has(finding.file)) files.set(finding.file, files.size);
  }
  return [...list].sort((a, b) =>
    (files.get(a.file) - files.get(b.file))
    || (a.line - b.line)
    || (a.column - b.column));
}

// One grouped issue: the same values lib/report.mjs pushIssue puts on its
// `issue` element, built from a group lib/report.mjs groupIssues produced —
// grouping is never reimplemented here, so both formats agree on what one
// issue is and on how many occurrences it has. The banner carries a location
// only when the group holds a single occurrence, and the count is rendered
// only when it is greater than one (issueCard below): a group of one is not
// a summary.
function groupedIssue(group) {
  const { finding, occurrences } = group;
  const marker = categoryMarker(finding.category);
  const kind = finding.severity === 'error' ? 'error'
    : finding.severity === 'warning' ? 'warning' : 'note';
  const severity = SEVERITY_LABEL[finding.severity] || 'NOTE';
  const count = occurrences.length;
  const location = count === 1 ? ` · line ${finding.line}:${finding.column}` : '';
  const should = String(finding.proposed ?? finding.suggestion ?? finding.message);
  const suffix = finding._replacement == null ? MANUAL_SUFFIX : FIXABLE_SUFFIX;
  return {
    kind,
    // D11: the category name rides along for the row's artwork, exactly as
    // lib/report.mjs's issue carries it — the icon is keyed by category, and a
    // renderer that had to guess it from the marker code would be guessing.
    category: String(finding.category),
    marker: marker ? marker.code : '',
    colour: marker ? marker.colour : '',
    count,
    text: `[${severity}] ${finding.ruleId} · ${finding.category} · ${finding.confidence}${location}`,
    current: String(finding.current ?? NO_CONTEXT),
    should: should + suffix,
    message: String(finding.message),
    audit: finding.audit ? String(finding.audit) : null,
    heuristic: finding.confidence === 'heuristic',
    provenance: [
      ['Lane', String(finding.lane || 'deterministic')],
      ['Source', String(finding.source || 'rules/catalogue.json')],
      ['Profile', String(finding.profile || 'editorial baseline')],
      ['Confidence', String(finding.confidence)],
      ['Limitation', String(finding.limitation || '')],
      ['Action', String(finding.action || '')],
    ],
    // The excerpt, match marked » … « by the scanner, with the same fallback
    // lib/report.mjs uses: an audit finding or masked copy falls back to the
    // matched token, the only copy the finding can prove. No copy is ever
    // re-read from disk here — the renderer is pure.
    occurrences: occurrences.map(occurrence => ({
      file: String(occurrence.file),
      line: occurrence.line,
      column: occurrence.column,
      pdfPage: occurrence.pdfPage ?? null,
      content: occurrence.excerpt ?? String(occurrence.current ?? NO_CONTEXT),
      should: String(occurrence.proposed ?? occurrence.suggestion ?? occurrence.message),
    })),
  };
}

// One grouped issue block: severity banner (marker code beside the text —
// the category name is already in the banner, so colour is never the only
// signal), the count when the group is larger than one, Current and Should
// be, the explanation, the audit marker and heuristic note, the six
// provenance fields, and finally the occurrence table — a real <table> with
// File / Location / Content / Should be. Every cell carries user text through
// safe(), so an excerpt or a path containing markup is displayed, never
// parsed. The table comes last so the provenance rows still close the block,
// exactly as the finding card does.
function issueCard(issue) {
  const parts = [];
  parts.push(`<article class="finding issue severity-${issue.kind}">`);
  // D11: the row's marks are drawn, not written. Severity artwork first, then
  // the category's own artwork, then the coloured chip carrying the category's
  // short code — D12's order, and the reason colour is never the only signal:
  // two shapes and a code all say what the row is before a word is read.
  // `svgIcon` hides them from assistive technology by default, so the headline
  // text below is still the only thing announced. A category with no icon in
  // the catalogue has none; its code and name still say what it is.
  const sevShapes = severityIcon(issue.kind);
  const sev = sevShapes ? svgIcon(sevShapes, { size: 13, className: 'icon sev' }) : '';
  const catShapes = issue.category ? categoryIcon(issue.category) : null;
  const cat = catShapes ? svgIcon(catShapes, { size: 13, className: 'icon cat' }) : '';
  const badge = issue.marker
    ? `<span class="marker" style="background:${safe(issue.colour)}">${safe(issue.marker)}</span>`
    : '';
  const marks = sev + cat + badge;
  parts.push(`<h3>${marks}${marks ? ' ' : ''}${safe(issue.text)}</h3>`);
  // A count is shown only when it is greater than one — "1 occurrence" next
  // to a lone finding reads as though something was counted that was not.
  if (issue.count > 1) parts.push(`<p class="count">${issue.count} occurrences</p>`);
  parts.push('<dl>');
  pushRow(parts, 'Current', issue.current);
  pushRow(parts, 'Should be', issue.should);
  parts.push('</dl>');
  parts.push(`<p class="message">${safe(issue.message)}</p>`);
  if (issue.audit) {
    parts.push(`<dl class="audit"><dt>Audit</dt><dd>${safe(issue.audit)}</dd></dl>`);
  }
  if (issue.heuristic) {
    parts.push('<p class="heuristic">Heuristic finding — routed to review.</p>');
  }
  parts.push('<dl class="fields">');
  for (const [label, value] of issue.provenance) pushRow(parts, label, value);
  parts.push('</dl>');
  parts.push('<table class="occurrences">');
  parts.push('<thead><tr><th scope="col">File</th><th scope="col">Location</th>'
    + '<th scope="col">Content</th><th scope="col">Should be</th></tr></thead>');
  parts.push('<tbody>');
  for (const occurrence of issue.occurrences) {
    const location = Number.isInteger(occurrence.pdfPage)
      ? `${occurrence.line}:${occurrence.column} · page ${occurrence.pdfPage}`
      : `${occurrence.line}:${occurrence.column}`;
    parts.push(`<tr><td>${safe(occurrence.file)}</td><td>${safe(location)}</td>`
      + `<td>${safe(occurrence.content)}</td><td>${safe(occurrence.should)}</td></tr>`);
  }
  parts.push('</tbody>');
  parts.push('</table>');
  parts.push('</article>');
  return parts.join('\n');
}

// The category legend: all twelve catalogue categories in catalogue order,
// zero-count rows included, each row printing the marker code and the
// category's own name side by side — colour and shape are never the only
// signal, so a greyscale printout and a screen reader get the same twelve
// rows. Rows come from lib/legend.mjs legendRows, so the counts are exactly
// the findings this report already holds.
function legendSection(findings) {
  const parts = [];
  // D5's second section, named from the same string lib/report.mjs pushes for
  // the PDF, so the two formats cannot call the vocabulary section something
  // different. The count is the report's finding count, which is what the
  // twelve rows below add up to.
  parts.push('<section class="category-legend" id="categories">');
  parts.push(sectionHead('Categories', 'thirteen checked categories',
    sectionCount(findings.length)));
  parts.push('<table class="legend">');
  parts.push('<thead><tr><th scope="col">Marker</th><th scope="col">Category</th>'
    + '<th scope="col">What it covers</th><th scope="col">Findings</th></tr></thead>');
  parts.push('<tbody>');
  for (const row of legendRows(findings)) {
    // D11: the legend teaches a mark the report actually draws — the same
    // category artwork, in the same place, as the finding rows put it. A
    // category the catalogue has no icon for prints its code and name alone
    // rather than borrowing a neighbour's artwork.
    const shapes = categoryIcon(row.category);
    const icon = shapes ? svgIcon(shapes, { size: 13, className: 'icon cat' }) : '';
    parts.push(`<tr><td>${icon}<span class="marker" style="background:${safe(row.colour)}">`
      + `${safe(row.code)}</span></td><td>${safe(row.category)}</td>`
      + `<td>${safe(row.intent)}</td><td>${row.count}</td></tr>`);
  }
  parts.push('</tbody>');
  parts.push('</table>');
  parts.push('</section>');
  return parts.join('\n');
}

/**
 * Render the report model into one self-contained HTML document.
 *
 * @param {object} input  { version, date, targets, profiles, filesCount, findings, sources }
 * @param {object} [opts] `{ version }` — stamped into the footer, as in lib/pdf.mjs;
 *                         `{ detail }` — 'grouped' (default) renders issue blocks
 *                         with an occurrence table, 'full' the pre-Phase-9
 *                         one-card-per-finding layout. Presentation only: counts,
 *                         lanes and the clean-run sentence are computed from the
 *                         findings before either layout runs.
 * @returns {string} the whole file; deterministic for identical input
 */
export function renderHtml(input, opts = {}) {
  const version = typeof opts.version === 'string'
    ? opts.version
    : String(input.version == null ? '' : input.version);
  // Same switch lib/report.mjs applies: anything that is not 'full' groups.
  const detail = opts.detail === 'full' ? 'full' : 'grouped';
  const findings = (input.findings || []).map(finding => annotate(finding));
  const targets = input.targets || [];
  const profiles = input.profiles || [];
  const sources = input.sources || [];
  const summary = summarize(findings);
  const laneCounts = countLanes(findings);

  // Quoted material is a context, not a lane: a quoted finding keeps its lane
  // metadata but renders in its own section — reported separately, never
  // skipped, never mixed into the authored copy. Everything else is sectioned
  // by lib/report.mjs sectionPlan, the one table both formats read, so this
  // renderer cannot reorder the sections, cap one of them or name one of them
  // differently from the PDF.
  const quoted = findings.filter(finding => finding.context === 'quoted');
  const plan = sectionPlan(findings, { detail });
  // The command a capped section prints so a reader can list what the body
  // withheld. lib/cli.mjs builds it from the real argv; without it a cap
  // would promise a way back that does not exist, so the build refuses.
  const command = typeof opts.command === 'string' ? opts.command : '';
  // One row shape (D12): the uncapped layout is the capped row with a group of
  // one, built by the same `groupedIssue`/`issueCard` pair. Two card builders
  // is how `full` came to print a `File` row the grouped layout never had and
  // differ from it field by field — there is now one.
  const rowOf = finding => issueCard(groupedIssue({ finding, occurrences: [finding] }));
  // Quoted material renders in the same two shapes as the lane sections.
  const blocks = (list) => (detail === 'full'
    ? list.map(rowOf)
    : groupIssues(list).map(group => issueCard(groupedIssue(group))));

  const parts = [];
  parts.push('<!DOCTYPE html>');
  parts.push('<html lang="en">');
  parts.push('<head>');
  parts.push('<meta charset="utf-8">');
  parts.push('<meta name="viewport" content="width=device-width, initial-scale=1">');
  parts.push(`<title>${safe(TITLE)} - un-editorial-check ${safe(version)}</title>`);
  parts.push(`<style>${STYLE}</style>`);
  parts.push('</head>');
  parts.push('<body>');
  parts.push('<main>');

  // 1. Document header (lib/furniture.mjs headerRows): two rows of two cells,
  // drawn on the cover and on every continuation page alike, so the same block
  // frames every page of the document. EDITORIAL REVIEW sits opposite the tool
  // and its version — never UNITED NATIONS — so no masthead can imply the tool
  // speaks for the United Nations. The title is deliberately not part of the
  // repeating header; it is the <h1> below, and the cover block that follows
  // carries the scan's vital statistics in the order lib/report.mjs renders
  // them.
  parts.push('<header class="doc-header">');
  for (const row of headerRows(input, version)) {
    parts.push(`<p><span class="l">${safe(row.left)}</span>`
      + `<span class="r">${safe(row.right)}</span></p>`);
  }
  parts.push('</header>');
  parts.push(`<h1>${safe(TITLE)}</h1>`);
  parts.push('<dl class="cover">');
  pushRow(parts, 'Version', version);
  pushRow(parts, 'Date', input.date);
  pushRow(parts, 'Targets', targets.join(' '));
  if (profiles.length) pushRow(parts, 'Profiles', profiles.join(', '));
  pushRow(parts, 'Files scanned', input.filesCount);
  parts.push('</dl>');
  parts.push('<hr>');

  // 2. Summary (D5, first): the counts, the lane routing, the audit row and
  // the three promises, all under the one heading both formats use, so the
  // numbers are read before any finding is.
  parts.push('<section class="summary" id="summary">');
  parts.push(sectionHead('Summary', '', sectionCount(findings.length)));
  parts.push(`<p class="counts">${severityCounts(summary, ' · ')}</p>`);
  if (findings.length) {
    const lanes = LANE_NAMES.map(name => `${name} ${laneCounts[name]}`)
      .concat(`quoted ${laneCounts.quoted}`);
    parts.push(`<p class="lanes">lanes: ${safe(lanes.join(' · '))}</p>`);
    // D9's other half, in the same section and the same place as the PDF's:
    // every path below is relative, and this row says what to. Stated only
    // when there are paths to resolve — a clean scan prints no file at all.
    if (input.root) {
      parts.push('<dl class="root">');
      pushRow(parts, 'Root', input.root);
      parts.push('</dl>');
    }
  }
  const auditNames = Object.keys(summary.audits).sort();
  if (auditNames.length) {
    parts.push('<dl class="audits">');
    pushRow(parts, 'Audits',
      auditNames.map(name => `${name} ${summary.audits[name]}`).join(', '));
    parts.push('</dl>');
  }

  // 3. Framing: the three promises of the PDF report, then the disclaimer.
  // Both formats now say exactly the same thing. The framing block still
  // leads everything a reader could mistake for a finding.
  parts.push('<section class="framing">');
  parts.push(`<p>${safe(LEGEND_DETERMINISTIC)}</p>`);
  parts.push(`<p>${safe(LEGEND_HEURISTIC)}</p>`);
  parts.push(`<p>${safe(LEGEND_REPORT_ONLY)}</p>`);
  parts.push(`<p class="disclaimer">${safe(FRAMING)}</p>`);
  parts.push('</section>');
  parts.push('</section>');

  // 3b. Categories (D5, second): all twelve categories in both detail modes,
  // drawn from lib/legend.mjs so the vocabulary and its counts cannot drift
  // from the catalogue or from the other report formats.
  parts.push(legendSection(findings));

  // 4. Findings: the clean sentence when the scan found nothing, otherwise
  // every section of the plan — including the ones with nothing in them, so a
  // reader can tell a lane that was checked from a lane that never ran (D10).
  // The count on each header is the section's finding count in both modes:
  // grouping is presentation, so what the `lanes:` line above states is what
  // each header states. Inside a section, `grouped` renders one issue per
  // group from the plan's own groups — capped where the plan says so (D7–D8),
  // never splitting a group — and `full` renders one card per finding,
  // ordered here the way this renderer always has ordered it.
  if (!findings.length) {
    parts.push(`<p class="clean">${safe(CLEAN)}</p>`);
  } else {
    for (const section of plan) {
      parts.push(`<section class="lane" id="lane-${safe(section.lane)}">`);
      parts.push(sectionHead(section.title, section.meta, sectionCount(section.total)));
      if (section.empty) {
        parts.push(`<p class="empty">${safe(EMPTY_LANE)}</p>`);
      } else if (detail === 'full') {
        for (const finding of orderFindings(section.findings)) parts.push(rowOf(finding));
      } else {
        for (const group of section.kept) parts.push(issueCard(groupedIssue(group)));
        if (section.capped) {
          // Refuse rather than guess: a cap with no runnable command would
          // promise the reader a way back that does not exist (D13).
          if (!command) {
            throw new Error('a capped report body needs the re-run command: pass opts.command');
          }
          parts.push(capBlock(section, command));
        }
      }
      parts.push('</section>');
    }
    if (quoted.length) {
      parts.push('<section class="quoted" id="quoted-material">');
      parts.push(sectionHead('Quoted material', 'context, not a lane',
        sectionCount(quoted.length)));
      for (const block of blocks(quoted)) parts.push(block);
      parts.push('</section>');
    }
  }

  // 5. Priority Recommendations: derived only from counts that are in this
  // report, so the section cannot advise a reader about anything the scan did
  // not find.
  const recs = recommendations(findings);
  if (recs.length) {
    parts.push('<section class="reco" id="priority-recommendations">');
    parts.push(sectionHead('Priority Recommendations', 'derived from the findings above', ''));
    parts.push('<ol>');
    for (const item of recs) parts.push(`<li>${safe(item)}</li>`);
    parts.push('</ol>');
    parts.push('</section>');
  }

  // 6. Sources appendix.
  if (sources.length) {
    parts.push('<section class="sources" id="sources">');
    parts.push('<h2>Sources</h2>');
    parts.push('<ul>');
    for (const source of sources) parts.push(`<li>${safe(source)}</li>`);
    parts.push('</ul>');
    parts.push('</section>');
  }

  parts.push('</main>');
  // Footer (lib/furniture.mjs footerCells): three cells — the page position,
  // the copyright with its year read from the scan's date, and the repository
  // address — placed left, centre and right so both formats state the same
  // three things in the same order.
  const footer = footerCells({ date: input.date, page: 1, pages: 1 });
  parts.push('<footer>');
  parts.push(`<span class="l">${safe(footer.left)}</span>`);
  parts.push(`<span class="c">${safe(footer.centre)}</span>`);
  parts.push(`<span class="r">${safe(footer.right)}</span>`);
  parts.push('</footer>');
  parts.push('</body>');
  parts.push('</html>');
  return parts.join('\n');
}
