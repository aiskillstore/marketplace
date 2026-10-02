// Report model: the pure data layer between scan findings and the renderer.
//
// `buildReport` turns a scan result (contract: .feedbacks/PHASE3-CONTRACT.md §2)
// into the flat element union that lib/pdf.mjs consumes. The module is pure by
// contract: no file system, no process access and no clock — the date arrives
// with the input, so identical input always produces identical, deeply equal
// output. Input findings are never mutated: grouping happens in a Map and every
// sort runs on a copy, so a frozen input renders exactly like a fresh one.
// Since Wave 3 each finding is annotated with its lane and metadata before
// rendering; that annotation resolves once, at first use, from the shipped
// rules/catalogue.json through lib/output.mjs — buildReport itself performs no
// I/O, and for a fixed catalogue its output still depends only on input data.

import { summarize, annotate, countLanes, LANE_NAMES, severityCounts } from './output.mjs';
import { categoryMarker } from './legend.mjs';
import { TITLE } from './furniture.mjs';

const ELEMENT_TYPES = new Set([
  'banner', 'heading', 'paragraph', 'kv', 'bullets', 'spacer', 'rule', 'issue',
  'cap',
]);

/**
 * Check every element against the union above. A renderer switches on `type`,
 * so an unknown type must fail loudly instead of vanishing from the report.
 */
export function assertElements(elements) {
  for (const element of elements) {
    const type = element !== null && typeof element === 'object' ? element.type : undefined;
    if (!ELEMENT_TYPES.has(type)) {
      throw new Error(`unknown element type: ${String(type)}`);
    }
  }
  return elements;
}

// Severity presentation: `info` and anything unexpected read as notes.
const SEVERITY_LABEL = { error: 'ERROR', warning: 'WARNING', info: 'NOTE' };

function severityLabel(severity) {
  return SEVERITY_LABEL[severity] || 'NOTE';
}

function severityKind(severity) {
  if (severity === 'error') return 'error';
  if (severity === 'warning') return 'warning';
  return 'note';
}

// A finding with no captured copy (audits, hate-speech review) must not show a
// developer placeholder in the director-facing PDF — "(not applicable)" reads
// as an editorial statement, not as missing plumbing.
const NO_CONTEXT = '(not applicable)';
const MANUAL_SUFFIX = ' — manual / agent rewrite; not --fix-able';
const FIXABLE_SUFFIX = ' — --fix-able';

// One block per finding: severity banner, current text, should-be guidance,
// the full explanation, an audit marker when present, the heuristic note that
// keeps judgement questions out of definitive language, and the five lane
// rows (lane, source, profile, limitation, action) that close the block.
function pushFinding(elements, finding) {
  // D12 (.feedbacks/REPORT-REDESIGN-PLAN.md): one row shape for every section
  // and every severity. The uncapped layout draws *the same row the capped
  // layout draws*, with a group of one — so `full` cannot grow a second
  // implementation of the finding block and quietly lose a field from it.
  // That is exactly what this function did before this line: five provenance
  // rows where `grouped` printed six, the defect D12 names and §10 item 4
  // forbids. One builder, so the two layouts cannot disagree again.
  pushIssue(elements, { finding, occurrences: [finding] });
}

// --- grouping ---------------------------------------------------------------
//
// A report issue is a group of findings that would render identically except
// for where they were found. The key is built from what the issue block
// actually prints, which is a stronger guarantee than any hand-picked list of
// columns: two findings may only share a block if every value the reader will
// see for that block is the same for both. Different advice, a different
// explanation or a different severity all keep findings apart, because a group
// that printed one of them for two occurrences that disagree would be the
// silent merging of unlike things the plan names as the failure mode.
//
// `file` is deliberately not a key part — the same defect in two files is one
// issue, and the occurrence table carries each file. Grouping is presentation:
// no count anywhere is derived from it.

function issueKey(finding) {
  const should = String(finding.proposed ?? finding.suggestion ?? finding.message);
  return JSON.stringify([
    finding.ruleId,
    finding.lane,
    finding.severity,
    finding.confidence,
    finding.category,
    finding.current ?? null,
    should,
    String(finding.message),
    finding.audit ?? null,
  ]);
}

/**
 * Group an ordered list of findings into issues, in the order each group's
 * first occurrence appears. Occurrences inside a group keep the list's own
 * order, so a report reads in position order and never jumps around.
 *
 * @param {object[]} findings annotated findings, in rendering order
 * @returns {object[]} one issue per distinct group
 */
export function groupIssues(findings) {
  const order = [];
  const byKey = new Map();
  for (const finding of findings) {
    const key = issueKey(finding);
    let issue = byKey.get(key);
    if (!issue) {
      issue = { finding, occurrences: [] };
      byKey.set(key, issue);
      order.push(issue);
    }
    issue.occurrences.push(finding);
  }
  return order;
}

/**
 * One grouped issue: the same block a single finding draws, plus the count and
 * the occurrence table behind it.
 *
 * The six provenance fields are laid out explicitly rather than left to fall
 * out of the banner, because the requirement is that every issue carries them
 * — including when the group has a hundred occurrences and nobody is going to
 * cross-check the banner against the catalogue to work out what was asserted.
 */
function pushIssue(elements, issue) {
  const { finding, occurrences } = issue;
  const marker = categoryMarker(finding.category);
  const kind = severityKind(finding.severity);
  const count = occurrences.length;
  // A count is shown only when it is more than one: a group of one is not a
  // summary, and printing "1 occurrence" next to a lone finding reads as
  // though something was counted that was not there.
  const location = count === 1
    ? ` · line ${finding.line}:${finding.column}`
    : '';
  elements.push({
    type: 'issue',
    kind,
    ruleId: String(finding.ruleId),
    category: String(finding.category),
    confidence: String(finding.confidence),
    severity: String(finding.severity),
    lane: String(finding.lane || 'deterministic'),
    marker: marker ? marker.code : '',
    colour: marker ? marker.colour : '',
    count,
    text: `[${severityLabel(finding.severity)}] ${finding.ruleId} · ${finding.category} · ${finding.confidence}${location}`,
    current: String(finding.current ?? NO_CONTEXT),
    should: String(finding.proposed ?? finding.suggestion ?? finding.message) + (finding._replacement == null ? MANUAL_SUFFIX : FIXABLE_SUFFIX),
    message: String(finding.message),
    audit: finding.audit ? String(finding.audit) : null,
    heuristic: finding.confidence === 'heuristic',
    provenance: [
      { label: 'Lane', value: String(finding.lane || 'deterministic') },
      { label: 'Source', value: String(finding.source || 'rules/catalogue.json') },
      { label: 'Profile', value: String(finding.profile || 'editorial baseline') },
      { label: 'Confidence', value: String(finding.confidence) },
      { label: 'Limitation', value: String(finding.limitation || '') },
      { label: 'Action', value: String(finding.action || '') },
    ],
    occurrences: occurrences.map(occurrence => ({
      file: String(occurrence.file),
      line: occurrence.line,
      column: occurrence.column,
      pdfPage: occurrence.pdfPage ?? null,
      // The line of copy the finding sits on, with the match marked. Built at
      // scan time and never by re-reading the file, so a document that changed
      // after the scan cannot put words in a report that were never scanned.
      // A finding that carries no excerpt (an audit rule, or copy that was
      // masked away from its match) falls back to the matched token, which is
      // the only copy the finding can prove.
      content: occurrence.excerpt ?? String(occurrence.current ?? NO_CONTEXT),
      should: String(occurrence.proposed ?? occurrence.suggestion ?? occurrence.message),
      fixable: occurrence._replacement != null,
    })),
  });
}

// --- the section plan (D5, D7, D8, D10, D13) --------------------------------
//
// One table, imported by lib/pdf.mjs (through buildReport below) and by
// lib/html.mjs, so the two formats cannot order the sections differently, cap
// one of them and not the other, or disagree about what a section's title is.
// This is the only place the section list exists.
//
// The order is the reader's: harmful and discriminatory content first because
// it carries the most serious weight, then diplomatic sensitivity, then the
// editorial lanes from errors down to warnings, then the agent review queue,
// then the audit findings the reader opted into.

/**
 * The body cap. Warnings may be capped; errors and the critical lanes are
 * never capped, and a group is never split at the boundary, which is why a
 * capped section can read `Showing 18 of 41`.
 */
export const CAP = 20;

/**
 * D10's wording: an empty lane says it was checked, so a reader can tell a
 * clean lane from a lane that never ran.
 */
export const EMPTY_LANE = 'No findings under this lane in this scan. The lane was checked.';

/**
 * The six sections, in D5 order. `severity` narrows a lane that carries more
 * than one: `'error'` keeps errors, `'non-error'` keeps everything else. A
 * deterministic note has no section of its own in the design, and dropping a
 * finding the scan really made would be a lie, so notes ride in Editorial
 * Warnings — the alternative is a section that silently omits them.
 *
 * `cap` marks the two sections whose body may be truncated. Nothing else can
 * ever be capped, and `full` never is (§4).
 */
export const SECTIONS = [
  { title: 'Harmful / Discriminatory Content', lane: 'harmful-discriminatory', severity: null, cap: false },
  { title: 'Diplomatic Sensitivity', lane: 'diplomacy', severity: null, cap: false },
  { title: 'Editorial Errors', lane: 'deterministic', severity: 'error', cap: false },
  { title: 'Editorial Warnings', lane: 'deterministic', severity: 'non-error', cap: true },
  { title: 'Agent Review Required', lane: 'heuristic-review', severity: null, cap: true },
  { title: 'Audit Findings', lane: 'audit', severity: null, cap: false },
];

const SEVERITY_RANK = { error: 0, warning: 1, info: 2 };

/** The lane metadata printed beside a section title (D6: never a number). */
function sectionMeta(section, findings) {
  let meta = section.lane;
  if (section.severity === 'error') return `${meta} · error only`;
  if (section.severity === 'non-error') {
    const notes = findings.some(finding => finding.severity !== 'warning');
    return notes ? `${meta} · warning and note` : `${meta} · warning only`;
  }
  return meta;
}

/** The count printed on the right of a section title: findings, not groups. */
export function sectionCount(n) {
  return `${n} finding${n === 1 ? '' : 's'}`;
}

/**
 * Build every section of the body against the plan, capped where the plan
 * says so.
 *
 * Quoted material is a context, not a lane, so it is excluded here and carried
 * in its own section after the lane sections — reported separately, never
 * skipped, never mixed into the authored copy.
 *
 * @param {object[]} findings annotated findings
 * @param {object} [opts] `{ detail }` — only `grouped` bodies are capped (§4)
 * @returns {object[]} one descriptor per section, in D5 order
 */
export function sectionPlan(findings, opts = {}) {
  const detail = opts.detail === 'full' ? 'full' : 'grouped';
  const authored = findings.filter(finding => finding.context !== 'quoted');
  return SECTIONS.map((section) => {
    const inSection = authored.filter((finding) => finding.lane === section.lane
      && (section.severity === null
        || (section.severity === 'error'
          ? finding.severity === 'error'
          : finding.severity !== 'error')));
    const ordered = [...inSection]
      .sort((a, b) => (SEVERITY_RANK[a.severity] ?? 3) - (SEVERITY_RANK[b.severity] ?? 3));
    const groups = groupIssues(ordered);
    let kept = groups;
    let shown = ordered.length;
    let capped = false;
    if (section.cap && detail === 'grouped' && ordered.length > CAP) {
      // Never split a group: take whole groups until the next one would take
      // the body past the cap, and always take at least one so the section is
      // never rendered empty by its own cap.
      kept = [];
      shown = 0;
      for (const group of groups) {
        const size = group.occurrences.length;
        if (shown + size > CAP && kept.length) break;
        kept.push(group);
        shown += size;
      }
      // A section that drew everything — one group, too large to split, and
      // therefore taken whole — withheld nothing, so it is not capped and
      // prints no cap block. D13 asks the block to state what the body is not
      // showing; a block announcing "0 not listed above" states no such thing.
      capped = shown < ordered.length;
    }
    return {
      title: section.title,
      lane: section.lane,
      meta: sectionMeta(section, ordered),
      cap: section.cap,
      total: ordered.length,
      shown,
      capped,
      findings: ordered,
      groups,
      kept,
      empty: ordered.length === 0,
    };
  });
}

/**
 * D13's cap block, as the three lines both renderers print verbatim: the count
 * withheld, the promise that nothing was discarded, and a genuinely runnable
 * command rather than an abbreviation.
 *
 * @param {{shown: number, total: number, command: string}} info
 * @returns {string[]}
 */
export function capLines({ shown, total, command }) {
  return [
    `Showing ${shown} of ${total} · ${total - shown} not listed above.`,
    `Nothing is discarded. All ${total} are in this run's JSON and SARIF output,`
      + ' and every one of them can be listed here by re-running the same scan with:',
    command,
  ];
}

/**
 * Priority Recommendations: derived only from counts that are in this report,
 * so the section cannot advise a reader about something the scan did not find.
 *
 * @param {object[]} findings every finding of the scan
 * @returns {string[]} ordered recommendation sentences
 */
export function recommendations(findings) {
  const list = findings.filter(finding => finding.context !== 'quoted');
  const items = [];
  const harmful = list.filter(finding => finding.lane === 'harmful-discriminatory').length;
  const diplomatic = list.filter(finding => finding.lane === 'diplomacy').length;
  if (harmful) {
    items.push(`Address the ${harmful} harmful or discriminatory finding${harmful === 1 ? '' : 's'} first.`
      + ' They carry the most serious weight of anything in this scan.');
  }
  if (diplomatic) {
    items.push(`Review the ${diplomatic} diplomatic claim${diplomatic === 1 ? '' : 's'}.`
      + ' Attribute it to the party advancing it rather than stating it as fact.');
  }
  const byRule = new Map();
  for (const finding of list) {
    byRule.set(finding.ruleId, (byRule.get(finding.ruleId) || 0) + 1);
  }
  const ranked = [...byRule.entries()].sort((a, b) => (b[1] - a[1]) || String(a[0]).localeCompare(String(b[0])));
  for (const [ruleId, count] of ranked.slice(0, 6)) {
    const sample = list.find(finding => finding.ruleId === ruleId);
    const message = String(sample.message);
    const text = message.length > 120 ? `${message.slice(0, 120)}...` : message;
    items.push(`${ruleId} fires ${count} time${count === 1 ? '' : 's'} — ${text}`);
  }
  return items;
}

/**
 * @param {object} input  { version, date, targets, profiles, filesCount, findings, sources }
 * @param {object} [opts] { detail: 'grouped' | 'full', command?: string }
 * @returns {object[]}    renderable elements in contract order
 *
 * `detail: 'full'` is the pre-Phase-9 layout — one block per finding, exactly
 * as it always rendered, and never capped. `grouped` is the default: it draws
 * the sections of the D5 plan, collapsing findings that would render
 * identically into a single issue carrying an occurrence table, and capping
 * only the two sections the plan marks as cappable. A capped body needs
 * `command`, the genuinely runnable command that lists everything it withheld;
 * without one the build refuses rather than print a cap that promises a way
 * back that does not exist.
 *
 * The switch changes presentation only: counts, lanes and the clean-run
 * sentence are computed from the findings before either layout runs, so the
 * two modes cannot disagree about what was found.
 */
export function buildReport(input, opts = {}) {
  const detail = opts.detail === 'full' ? 'full' : 'grouped';
  const targets = input.targets || [];
  const profiles = input.profiles || [];
  // Annotate before any grouping: every consumer (counts, blocks, queue,
  // quoted section) works on the lane-annotated copy. annotate() returns a
  // new object, so input findings are never mutated and a frozen input
  // renders exactly like a fresh one.
  const findings = (input.findings || []).map(f => annotate(f));
  const sources = input.sources || [];

  const elements = [];

  // 1. Cover block: title banner plus the scan's vital statistics. The title
  // is one constant (D1) shared with the HTML `<h1>` and `<title>`, so the two
  // formats cannot name the document differently.
  elements.push({ type: 'banner', kind: 'title', text: TITLE });
  elements.push({ type: 'kv', label: 'Version', value: String(input.version) });
  elements.push({ type: 'kv', label: 'Date', value: String(input.date) });
  elements.push({ type: 'kv', label: 'Targets', value: targets.join(' ') });
  if (profiles.length) {
    elements.push({ type: 'kv', label: 'Profiles', value: profiles.join(', ') });
  }
  elements.push({ type: 'kv', label: 'Files scanned', value: String(input.filesCount) });
  elements.push({ type: 'rule' });

  // 2. Summary: the section that carries the counts (D5, first section).
  //
  // A clean scan gets no section at all — the clean-run sentence already
  // states that every enabled, documented rule ran, which is a stronger
  // guarantee than a lane saying "the lane was checked". Where the scan did
  // find things, Summary opens the body so the counts are read before any
  // finding is.
  const summary = summarize(findings);
  const auditNames = Object.keys(summary.audits).sort();
  // Summary is always the first section — a clean scan reports its zero count
  // in the same shape as a dirty one, so a reader never has to guess whether
  // the counts were omitted because there were none.
  elements.push({ type: 'spacer' });
  elements.push({
    type: 'heading', level: 1, text: 'Summary', meta: '', count: sectionCount(findings.length),
  });
  // Counts: editorial findings only; audits get their own row. The lane
  // line follows the severity counts (skipped on an empty scan) so routing
  // and quoted material are visible before any finding is read.
  elements.push({
    type: 'paragraph',
    text: severityCounts(summary, ' · '),
  });
  if (findings.length) {
    const laneCounts = countLanes(findings);
    const lanes = LANE_NAMES.map(name => `${name} ${laneCounts[name]}`)
      .concat(`quoted ${laneCounts.quoted}`);
    elements.push({ type: 'paragraph', text: `lanes: ${lanes.join(' · ')}` });
    // D9's other half. Every path in this body is relative, and this row is
    // the one place that says what to — so a printed copy can still resolve
    // `docs/page.md` back to the file the scan actually read. Stated only
    // when there are paths to resolve: a clean scan prints no file at all.
    if (input.root) elements.push({ type: 'kv', label: 'Root', value: String(input.root) });
  }
  if (auditNames.length) {
    elements.push({
      type: 'kv',
      label: 'Audits',
      value: auditNames.map(name => `${name} ${summary.audits[name]}`).join(', '),
    });
  }

  // 3. Legend: what deterministic and heuristic confidence each promise, and
  // the report-only guarantee that nothing here changes the scan.
  elements.push({ type: 'paragraph', text: 'Deterministic finding: the wording proves the defect.' });
  elements.push({
    type: 'paragraph',
    text: 'Heuristic finding: routed to review; this report never asserts that a claim is true or false, or that any legal threshold is met.',
  });
  elements.push({
    type: 'paragraph',
    text: 'This report changes nothing; re-run the checker to verify corrections.',
  });

  // 5. Categories: the legend's own section (D5, second). The rows are
  // spliced in by lib/pdf.mjs and rendered by lib/html.mjs; both hang them
  // from this heading so the two formats name the section identically.
  elements.push({ type: 'spacer' });
  elements.push({
    type: 'heading', level: 1, text: 'Categories',
    meta: 'thirteen checked categories', count: sectionCount(findings.length),
  });

  // 6. The body.
  //
  // `grouped` — the default — draws the sections in D5 order through
  // sectionPlan, capped where the plan says so. Grouping happens inside a
  // section, so a section's findings can only ever merge with each other, and
  // `file` is not part of an issue's identity, so one defect in three files is
  // one issue with three places and the occurrence table carries each file.
  //
  // `full` keeps the layout it has always had: one heading per file,
  // findings in line then column order inside it. It is never capped (§4) —
  // it is the reader explicitly asking for everything.
  const authored = findings.filter(finding => finding.context !== 'quoted');
  const quoted = findings.filter(finding => finding.context === 'quoted');
  if (!findings.length) {
    elements.push({ type: 'paragraph', text: 'No findings.' });
  } else if (detail === 'full') {
    const byFile = new Map();
    for (const finding of authored) {
      if (!byFile.has(finding.file)) byFile.set(finding.file, []);
      byFile.get(finding.file).push(finding);
    }
    elements.push({ type: 'spacer' });
    elements.push({
      type: 'heading', level: 1, text: 'Findings by file',
      meta: 'full detail · every finding', count: sectionCount(authored.length),
    });
    for (const [file, group] of byFile) {
      elements.push({
        type: 'heading', level: 2, text: String(file), meta: '',
        count: sectionCount(group.length),
      });
      const ordered = [...group].sort((a, b) => (a.line - b.line) || (a.column - b.column));
      for (const finding of ordered) pushFinding(elements, finding);
    }
  } else {
    for (const section of sectionPlan(findings, { detail })) {
      elements.push({ type: 'spacer' });
      elements.push({
        type: 'heading', level: 1, text: section.title,
        meta: section.meta, count: sectionCount(section.total),
      });
      if (section.empty) {
        // D10: a lane with nothing in it still says it was checked, so a
        // reader can tell a clean lane from a lane that never ran.
        elements.push({ type: 'paragraph', text: EMPTY_LANE });
        continue;
      }
      for (const group of section.kept) pushIssue(elements, group);
      if (section.capped) {
        // Refuse rather than guess: a cap that cannot print a runnable
        // command would promise the reader a way back that does not exist.
        if (!opts.command) {
          throw new Error('a capped report body needs the re-run command: pass opts.command');
        }
        elements.push({
          type: 'cap', shown: section.shown, total: section.total,
          command: String(opts.command),
        });
      }
    }
  }

  // Quoted material is a context, not a lane: a quoted finding keeps its lane
  // metadata but renders in its own section — reported separately, never
  // skipped, never mixed into the authored copy, and outside the lane sections
  // so it is never summarised into one of them.
  if (quoted.length) {
    elements.push({ type: 'spacer' });
    elements.push({
      type: 'heading', level: 1, text: 'Quoted material', meta: 'context, not a lane',
      count: sectionCount(quoted.length),
    });
    if (detail === 'full') {
      for (const finding of quoted) pushFinding(elements, finding);
    } else {
      for (const issue of groupIssues(quoted)) pushIssue(elements, issue);
    }
  }

  // 7. Priority Recommendations: derived only from counts that are in this
  // report, so the section cannot advise a reader about anything the scan did
  // not find.
  const recs = recommendations(findings);
  if (recs.length) {
    elements.push({ type: 'spacer' });
    elements.push({
      type: 'heading', level: 1, text: 'Priority Recommendations',
      meta: 'derived from the findings above', count: '',
    });
    elements.push({ type: 'bullets', items: recs });
  }

  // 8. Sources appendix.
  if (sources.length) {
    elements.push({ type: 'spacer' });
    elements.push({ type: 'heading', level: 1, text: 'Sources', meta: '', count: '' });
    elements.push({ type: 'bullets', items: sources.map(source => String(source)) });
  }

  return assertElements(elements);
}
