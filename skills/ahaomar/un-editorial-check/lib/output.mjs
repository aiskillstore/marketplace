// Report rendering: text (default), JSON and SARIF 2.1.0.
//
// Every finding carries file, line, column, rule id, category, severity,
// confidence and scope; since Wave 3 it also carries its lane and per-finding
// metadata (source, profile, limitation, action) through `annotate`, and the
// text report groups findings into five lanes — deterministic, heuristic
// review, harmful-discriminatory, diplomacy and audit — plus a separate
// quoted-material section, so a reader can never mistake a security finding
// for an editorial one or a diplomatic sensitivity for a factual falsehood.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { categoryMarker, legendRows } from './legend.mjs';

// Findings carry fields the report renders but JSON and SARIF must not: the
// unit it came from, the excerpt, the plan's internals. `publicFinding` strips
// these, which is also what keeps the JSON and SARIF shape byte-identical to
// what it was before `excerpt` existed.
const INTERNAL = new Set(['_unit', '_index', '_matched', '_offset', '_replacement', 'excerpt']);

// The five output lanes, in report order. Quoted material is a context, not
// a lane: a quoted finding keeps its lane and renders in its own section.
export const LANE_NAMES = ['deterministic', 'heuristic-review', 'harmful-discriminatory', 'diplomacy', 'audit'];

// "1 error", "2 errors". Every surface that prints a severity count takes its
// words from here — the terminal, the HTML document and the PDF — so the three
// cannot drift. They did: the terminal pluralised correctly while both report
// renderers wrote the plural unconditionally, so a scan with a single error
// printed "1 errors" on the document and "1 error" on the console. The locks
// that pinned the old wording moved with the fix (report-model, audit-lanes,
// audit-report-fix), and the singular case is now asserted directly.
export const countWord = (n, singular) => `${n} ${singular}${n === 1 ? '' : 's'}`;

/**
 * The three severity counts as one string. `joinWith` selects the surface:
 * the console joins with ", ", both report formats with " · ".
 */
export const severityCounts = (summary, joinWith = ', ') => [
  countWord(summary.errors, 'error'),
  countWord(summary.warnings, 'warning'),
  countWord(summary.info, 'note'),
].join(joinWith);

/** Lane precedence: audit, then safety categories, then confidence. */
export function laneOf(finding) {
  if (finding.audit) return 'audit';
  if (finding.category === 'hate-speech' || finding.category === 'discriminatory') {
    return 'harmful-discriminatory';
  }
  if (finding.category === 'diplomacy') return 'diplomacy';
  if (finding.confidence === 'heuristic') return 'heuristic-review';
  return 'deterministic';
}

// Deterministic quote detection for the report layer: an explicit `context`
// from extraction is authoritative, otherwise a copy span that opens with a
// quotation mark or a blockquote marker — or is wrapped in quotation marks —
// is treated as quoted and routed to the quoted-material section. Nothing is
// ever skipped: quoted findings are reported, just separately.
//
// Detection runs only over prose units (Markdown, plain text, HTML prose),
// where an opening quotation mark is content. Syntax quotes — a JavaScript
// string token, an HTML attribute value — always open with a quote and are
// authored copy, never quotation, so those contexts are never auto-detected.
function detectedContext(finding) {
  if (finding.context !== undefined) return finding.context;
  const unit = finding._unit;
  const raw = unit && unit.raw;
  if (typeof raw !== 'string') return 'authored';
  const unitContext = unit.context;
  if (unitContext !== undefined && !PROSE_CONTEXTS.has(unitContext)) return 'authored';
  const text = raw.trim();
  if (/^(?:["“'‘]|>\s?)/.test(text)) return 'quoted';
  if (/^(?:["“][\s\S]*["”]|['‘][\s\S]*['’])$/.test(text)) return 'quoted';
  return 'authored';
}

const PROSE_CONTEXTS = new Set(['md-prose', 'text-prose', 'html-prose']);

// Catalogue lookups are cached lazily: the shipped rules/catalogue.json is
// the source for per-rule source, profile, limitation and action wording.
let catalogueCache = null;
function catalogueRule(ruleId) {
  if (catalogueCache === null) {
    catalogueCache = new Map();
    try {
      const file = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'rules', 'catalogue.json');
      const parsed = JSON.parse(fs.readFileSync(file, 'utf8'));
      for (const rule of parsed.rules) catalogueCache.set(rule.id, rule);
    } catch { /* defaults below keep the renderer usable without the file */ }
  }
  return catalogueCache.get(ruleId);
}

const CATEGORY_SOURCE = {
  spelling: 'rules/spelling.md',
  terminology: 'rules/terminology.md',
  numerals: 'rules/numerals.md',
  register: 'rules/register.md',
  'agent-review': 'rules/register.md',
  grammar: 'rules/grammar.md',
  diplomacy: 'rules/diplomacy.md',
  'hate-speech': 'rules/hate-speech.md',
  discriminatory: 'rules/hate-speech.md',
};

const LANE_LIMITATION = {
  audit: 'Audit finding: declaration and presence checks only; audits never change the exit code.',
  'harmful-discriminatory': 'Wording flagged for high-severity human review; not a legal judgement and never rewritten automatically.',
  diplomacy: 'Requires diplomatic review; the checker never decides whose claim is correct.',
  'heuristic-review': 'Heuristic signal: routed to review, never proof of a defect.',
  deterministic: 'Deterministic match on extracted copy; quoted, cited and code spans are outside the scan.',
};

const LANE_ACTION = {
  audit: 'Review under the audit profile; audits never fail the run.',
  'harmful-discriminatory': 'High-severity human review; never auto-rewritten.',
  diplomacy: 'Requires diplomatic review; attribute the claim to the party advancing it or use the neutral wording.',
  'heuristic-review': 'Human or agent review before any change.',
  deterministic: 'Editorial correction; verify in context before applying.',
};

/**
 * Annotate a finding with its lane and per-finding metadata. Returns a new
 * object; the input finding is never mutated. Quoted routing honours an
 * explicit `context` from extraction and otherwise applies deterministic
 * quote detection to the raw copy span.
 */
export function annotate(finding) {
  const context = detectedContext(finding);
  const lane = laneOf(finding);
  const rule = catalogueRule(finding.ruleId);
  return {
    ...finding,
    lane,
    context,
    source: (rule && rule.source) || finding._sourceOverride || (finding.audit ? `config/profiles/${finding.audit}.json` : CATEGORY_SOURCE[finding.category]) || 'rules/catalogue.json',
    profile: (rule && rule.profile) || (finding.audit || 'editorial baseline'),
    confidence: finding.confidence,
    limitation: (rule && rule.limitation) || LANE_LIMITATION[lane],
    action: (rule && rule.action) || LANE_ACTION[lane],
  };
}

/** Lane counts over an annotated list; quoted findings count separately. */
export function countLanes(findings) {
  const counts = Object.fromEntries([...LANE_NAMES, 'quoted'].map(name => [name, 0]));
  for (const finding of findings) {
    if (finding.context === 'quoted') counts.quoted++;
    else counts[finding.lane]++;
  }
  return counts;
}

// C0/C1 controls, bidi overrides and isolate markers: none of them may reach a
// terminal inside a file name, a message or a copy excerpt, because a terminal
// escape sequence inside a scanned file could redraw or hide a finding. JSON
// and SARIF need no help: JSON.stringify escapes on its way out.
const CONTROL_RE = new RegExp('[\\u0000-\\u001f\\u007f-\\u009f\\u202a-\\u202e\\u2066-\\u2069]', 'g');

export function escapeControl(text) {
  return String(text).replace(CONTROL_RE, char =>
    `\\u${char.charCodeAt(0).toString(16).padStart(4, '0')}`);
}

export function publicFinding(finding) {
  const out = {};
  for (const [key, value] of Object.entries(finding)) {
    if (INTERNAL.has(key)) continue;
    out[key] = value;
  }
  return out;
}

export function summarize(findings) {
  const summary = { errors: 0, warnings: 0, info: 0, audits: {} };
  for (const finding of findings) {
    if (finding.audit) {
      summary.audits[finding.audit] = (summary.audits[finding.audit] || 0) + 1;
      continue;
    }
    if (finding.severity === 'error') summary.errors++;
    else if (finding.severity === 'warning') summary.warnings++;
    else summary.info++;
  }
  return summary;
}

/** Exit code input: error-severity editorial findings only. */
export function editorialErrors(findings) {
  return findings.filter(f => !f.audit && f.severity === 'error');
}

function line(finding) {
  const position = `${escapeControl(finding.file)}:${finding.line}:${finding.column}`;
  const suggestion = finding.suggestion ? `  → ${escapeControl(finding.suggestion)}` : '';
  // The category marker and its text label travel together on every surface
  // (PHASE-9-PLAN §5): the short code is the marker the legend explains, the
  // category name is the label that keeps it from being the only signal, and
  // neither is ever omitted on the strength of the other.
  const marker = categoryMarker(finding.category);
  const category = marker
    ? `${marker.code} ${marker.category}`
    : (finding.category ? escapeControl(finding.category) : '');
  const label = category ? `  ${category}` : '';
  return `  ${position}  ${finding.ruleId}${label}  [${finding.confidence}]  ${escapeControl(finding.message)}${suggestion}`;
}

/**
 * The distinct reasons a file was skipped, in first-seen order, joined for the
 * header. One reason is the norm (`not valid UTF-8`); the join exists so a
 * future reason cannot be silently folded into another, and so the order is
 * deterministic rather than dependent on object key iteration.
 */
function skippedReasons(skipped) {
  const reasons = [];
  for (const entry of skipped) {
    if (!reasons.includes(entry.reason)) reasons.push(entry.reason);
  }
  return reasons.join('; ');
}

export function renderText({ findings, files, skipped = [], version, fixes = [], applied = false }) {
  const annotated = findings.map(f => annotate(f));
  const editorial = annotated.filter(f => !f.audit);
  const sections = [];

  const push = (title, list) => {
    if (!list.length) return;
    sections.push(`${title} (${list.length})\n${list.map(line).join('\n')}`);
  };

  // Five lanes, each with its own section, plus quoted material reported
  // separately — never skipped, never mixed into a lane it does not belong
  // to. The deterministic lane keeps the editorial severity ladder; the
  // safety, diplomacy and heuristic lanes never masquerade as editorial
  // errors, and a heuristic judgement question cannot fail a build here.
  const inLane = (lane) => editorial.filter(f => f.lane === lane && f.context !== 'quoted');
  const deterministic = inLane('deterministic');
  const quoted = annotated.filter(f => f.context === 'quoted');

  push('EDITORIAL ERRORS', deterministic.filter(f => f.severity === 'error'));
  push('EDITORIAL WARNINGS', deterministic.filter(f => f.severity === 'warning'));
  push('EDITORIAL NOTES', deterministic.filter(f => f.severity !== 'warning' && f.severity !== 'error'));
  push('AGENT REVIEW REQUIRED', inLane('heuristic-review'));
  push('HARMFUL-DISCRIMINATORY REVIEW', inLane('harmful-discriminatory'));
  push('DIPLOMATIC SENSITIVITY', inLane('diplomacy'));

  const byAudit = new Map();
  for (const finding of annotated) {
    if (!finding.audit || finding.context === 'quoted') continue;
    if (!byAudit.has(finding.audit)) byAudit.set(finding.audit, []);
    byAudit.get(finding.audit).push(finding);
  }
  for (const [name, list] of [...byAudit].sort((a, b) => a[0].localeCompare(b[0]))) {
    push(`OPTIONAL AUDIT — ${name}`, list);
  }
  push('QUOTED MATERIAL', quoted);

  const summary = summarize(annotated);
  // "scanned N files" counts only files that were actually decoded. When a file
  // was skipped, the count is stated as "N of M" and the reason is named, so a
  // clean sentence can never be read as a statement about a file nobody opened —
  // the shape of QA finding F1, where the run reported success having read
  // nothing. The pluralisation is on the scanned count, which is the one the
  // sentence is about.
  const scanned = skipped.length
    ? `scanned ${files} of ${files + skipped.length} file${files + skipped.length === 1 ? '' : 's'}`
      + ` — ${skipped.length} skipped (${skippedReasons(skipped)})`
    : `scanned ${files} file${files === 1 ? '' : 's'}`;
  const header = [
    `un-editorial-check ${version}`,
    scanned,
    `editorial: ${severityCounts(summary)}`
      + (annotated.some(f => f.audit) ? `, audits: ${Object.entries(summary.audits).map(([k, v]) => `${k} ${v}`).join(', ')}` : ''),
  ].join(' — ');

  const out = [header];
  // The lane line appears only when there is something to route: all five
  // lane names with their counts, and quoted material counted separately —
  // the counts exclude quoted findings so the lanes sum to the non-quoted
  // total and quoted is reported on top of them.
  if (annotated.length) {
    const laneCounts = countLanes(annotated);
    const lanes = LANE_NAMES.map(name => `${name} ${laneCounts[name]}`)
      .concat(`quoted ${laneCounts.quoted}`);
    out.push(`lanes: ${lanes.join(' · ')}`);
    // The category legend on the terminal, matching the one the PDF and the
    // HTML draw: exactly the catalogue's twelve categories, in catalogue
    // order, with this scan's count against each. Categories that did not fire
    // are still listed — a legend that drops part of its own vocabulary reads
    // as though those categories do not exist — and it is gated on there being
    // findings, so a clean run still prints the clean sentence and nothing
    // else. The count is read from the findings in hand, never from a report.
    out.push(`categories: ${legendRows(annotated)
      .map(row => `${row.code} ${row.category} ${row.count}`).join(' · ')}`);
  }
  out.push('');
  if (sections.length) out.push(sections.join('\n\n'), '');
  else out.push('No findings under the enabled, documented local rules.', '');

  const replacements = fixes.reduce((n, plan) => n + plan.edits.length, 0);
  if (fixes.length) {
    out.push(`${applied ? 'APPLIED' : 'FIXABLE'} — ${replacements} replacement${replacements === 1 ? '' : 's'} in ${fixes.length} file${fixes.length === 1 ? '' : 's'}`, '');
  }
  return out.join('\n');
}

export function renderJSON({ findings, files, skipped = [], version, fixes = [] }) {
  const annotated = findings.map(f => annotate(f));
  return `${JSON.stringify({
    version,
    // `files` counts only the files that were decoded. `skipped` names the ones
    // that were not, so a consumer asserting `files > 0` and
    // `findings.length === 0` is asserting about copy that was actually read.
    // The field is always present, empty on a run that skipped nothing, so a
    // consumer never has to distinguish absent from empty.
    files,
    skipped: skipped.map(entry => ({ file: entry.file, reason: entry.reason })),
    summary: summarize(annotated),
    lanes: countLanes(annotated),
    findings: annotated.map(publicFinding),
    fixes: fixes.map(plan => ({
      file: plan.file,
      edits: plan.edits.map(edit => ({
        line: edit.line,
        column: edit.column,
        ruleId: edit.ruleId,
        from: edit.from,
        to: edit.to,
        message: edit.message,
      })),
    })),
  }, null, 2)}\n`;
}

const SARIF_LEVEL = { error: 'error', warning: 'warning', info: 'note' };

export function renderSARIF({ findings, files, skipped = [], version, informationUri }) {
  const ruleIndex = new Map();
  const rules = [];
  for (const finding of findings) {
    if (ruleIndex.has(finding.ruleId)) continue;
    ruleIndex.set(finding.ruleId, rules.length);
    // Lane metadata is stable per rule id (it derives from audit flag,
    // category and confidence), so the rule descriptor carries the same
    // source, profile, limitation and action as its results.
    const annotated = annotate(finding);
    rules.push({
      id: finding.ruleId,
      name: finding.ruleId.replace(/-/g, '_'),
      shortDescription: { text: finding.message },
      properties: {
        category: finding.category,
        confidence: finding.confidence,
        scope: finding.scope,
        audit: finding.audit || null,
        lane: annotated.lane,
        source: annotated.source,
        profile: annotated.profile,
        limitation: annotated.limitation,
        action: annotated.action,
      },
    });
  }
  const results = findings.map(raw => {
    const finding = annotate(raw);
    return {
      ruleId: finding.ruleId,
      ruleIndex: ruleIndex.get(finding.ruleId),
      level: SARIF_LEVEL[finding.severity] || 'warning',
      message: { text: finding.suggestion ? `${finding.message} ${finding.suggestion}` : finding.message },
      locations: [{
        physicalLocation: {
          artifactLocation: { uri: finding.file.split('/').join('/') },
          region: { startLine: finding.line, startColumn: finding.column },
        },
      }],
      properties: {
        category: finding.category,
        confidence: finding.confidence,
        scope: finding.scope,
        audit: finding.audit || null,
        lane: finding.lane,
        context: finding.context,
        source: finding.source,
        profile: finding.profile,
        limitation: finding.limitation,
        action: finding.action,
        // The page a PDF finding sits on. Added only when the finding has one,
        // so a run over any other format emits byte-identical properties to the
        // 1.2.1 shape: a consumer reading this bag is not handed a new key it has
        // to learn to ignore on every finding but only on PDFs.
        ...(Number.isInteger(finding.pdfPage) ? { pdfPage: finding.pdfPage } : {}),
      },
    };
  });

  return `${JSON.stringify({
    $schema: 'https://json.schemastore.org/sarif-2.1.0.json',
    version: '2.1.0',
    runs: [{
      tool: {
        driver: {
          name: 'un-editorial-check',
          version,
          informationUri,
          rules,
        },
      },
      // SARIF has no field for "a file was not read", so the count and the
      // skips go in the run property bag, which is where a consumer looks for
      // run-level facts. An empty `skipped` array is written on every clean run
      // so the field is never absent, and a run that skipped a file therefore
      // cannot be mistaken for a run that read it.
      properties: {
        files,
        skipped: skipped.map(entry => ({ file: entry.file, reason: entry.reason })),
      },
      results,
    }],
  }, null, 2)}\n`;
}
