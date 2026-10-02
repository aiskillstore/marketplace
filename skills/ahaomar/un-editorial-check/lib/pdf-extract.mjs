// The PDF adapter: the only new surface the rest of the tool sees.
//
// `lib/pdf-parse.mjs` (object graph: xref, trailer, object streams, stream
// filters) and `lib/pdf-text.mjs` (content-stream tokenizer, text operators,
// font encodings, ToUnicode CMaps) recover *positioned text runs* from a PDF's
// bytes. Neither is an extractor in this tool's sense: neither knows what a
// copy span is, what a `map` is, or what a rule is allowed to see. This module
// is the boundary. It turns positioned runs into exactly the `makeUnit` shape
// every other extractor produces, and it re-exports the refusal vocabulary
// under the names the rest of the tool imports.
//
// --- the honesty contract ---------------------------------------------------
//
// A PDF is a *rendered page*, not a source. Three consequences are structural,
// not documentation, and they are enforced here rather than described:
//
//   1. `context` is always `authored`. A quotation inside a PDF is a run of
//      glyphs at an x offset; nothing in the file distinguishes it from a
//      paragraph. So a quotation is scanned as authored copy, and a rule must
//      not be able to learn that the unit came from a PDF. Every unit here is
//      `authored`, and no quote masking is applied — masking it would make the
//      rules skip copy the reader can plainly see in the document.
//
//   2. `line` is a *visual line*, reconstructed from text positioning, counted
//      continuously across the whole document in reading order: page 1's lines
//      first, then page 2's. It is not a source line, because a PDF has no
//      source lines. `file:line:column` therefore addresses the recovered text,
//      and every document that mentions PDF has to say so.
//
//   3. A refusal is never a partial result. The engine either returns the runs
//      it is certain of, or throws `PdfRefusalError`. There is no best-effort
//      path, no empty-array-means-nothing path, and no catch that returns what
//      was recovered so far. A confidently wrong line number is worse than a
//      refusal, and a silent empty result is a clean run having read nothing —
//      the shape of QA finding F1.
//
// `pdfPage` is carried on the unit and reaches the JSON and SARIF outputs. The
// text output keeps the standard `file:line:column` shape, so nothing that
// parses the text report changes shape.
//
// --- the engine seam --------------------------------------------------------
//
// The two engine modules are looked up by export name rather than imported as
// named bindings, so that the adapter degrades to one clear failure instead of
// a module-resolution error when the engine is absent. A run without the
// engine present refuses with MALFORMED — it does not scan nothing and report
// success.

import { makeUnit, unitText } from './units.mjs';
import { lineStarts } from './position.mjs';

/**
 * Refusal codes, with the reason each one states in plain words. The value is
 * the fragment that completes "cannot read <file>: …", so every message reads
 * as one sentence naming the reason and nothing else.
 */
export const PDF_REFUSAL_CODES = {
  NOT_A_PDF: 'not a PDF document',
  ENCRYPTED: 'the document is encrypted',
  SCANNED: 'no extractable text; the document appears to be scanned images',
  UNDECODABLE_FONT: 'a font in the document has no recoverable text encoding',
  MALFORMED: 'the document structure could not be read',
};

/** The engine's own class, when it exports one; otherwise this module's. */
export class PdfRefusalError extends Error {
  constructor(message, { code, detail = {} } = {}) {
    super(message);
    this.name = 'PdfRefusalError';
    this.code = code;
    this.detail = detail;
  }
}

/**
 * What to do about each refusal, where there is something to do. This is the
 * difference between a message that names a dead end and one that names the
 * next step, and it is the step the reader has not been told about yet.
 */
const REMEDY = {
  NOT_A_PDF: 'The file does not have the structure of a PDF document.',
  ENCRYPTED: 'Remove the password protection, or save an unprotected copy, and run the check on that copy.',
  SCANNED: 'The text has to be recovered by other means first, for example by exporting the document as text, because the tool reads text out of a PDF and never optical character recognition. If the text is available elsewhere, paste it into a .txt or .md file and run the check on that.',
  UNDECODABLE_FONT: 'There is no way for the tool to recover the text this font encodes, so it will not guess at it. If the same text is available elsewhere, paste it into a .txt or .md file and run the check on that.',
  MALFORMED: 'The file may be truncated or damaged. If the text is available elsewhere, paste it into a .txt or .md file and run the check on that.',
};

/**
 * A refusal message naming the file, the reason, and what to do instead.
 *
 * The canonical reason for the code is always stated, so a reader gets the same
 * words whatever the engine put in the message; the engine's own detail is
 * kept as a parenthetical when it adds something. The remedy, where the code has
 * one, is a separate sentence — a refusal that only names a dead end leaves the
 * reader to work out the next step themselves.
 */
export function pdfRefusalMessage(error, filePath) {
  const code = error && error.code;
  const reason = PDF_REFUSAL_CODES[code] ?? PDF_REFUSAL_CODES.MALFORMED;
  const stated = typeof error?.message === 'string' ? error.message.trim() : '';
  let head = `cannot read ${filePath}: ${reason}`;
  if (stated && stated !== reason && !stated.includes(reason)) {
    head += ` (${stated})`;
  }
  const remedy = REMEDY[code] ?? REMEDY.MALFORMED;
  return `${head}. ${remedy}`;
}

/** True for an engine refusal, however the engine chose to signal it. */
export function isPdfRefusal(error) {
  if (error instanceof PdfRefusalError) return true;
  return Boolean(error && typeof error.code === 'string'
    && Object.hasOwn(PDF_REFUSAL_CODES, error.code));
}

/**
 * Normalise anything the engine throws into *this* module's `PdfRefusalError`,
 * so a caller can rely on the class it imported rather than on whichever class
 * the engine happened to define. An error carrying no known refusal code is
 * treated as MALFORMED: an engine that fails for a reason the contract does not
 * name has still failed to prove it read the text, so it refuses.
 */
function asRefusal(error) {
  if (error instanceof PdfRefusalError) return error;
  const named = error && typeof error.code === 'string' && Object.hasOwn(PDF_REFUSAL_CODES, error.code);
  const code = named ? error.code : 'MALFORMED';
  const message = typeof error?.message === 'string' && error.message
    ? error.message
    : PDF_REFUSAL_CODES[code];
  return new PdfRefusalError(message, { code, detail: error?.detail ?? {} });
}

// --- engine seam ------------------------------------------------------------

/**
 * The engine's entry point. The roster fixes the two module names and the
 * refusal they throw but not the exported function name, so the adapter
 * accepts the conventional candidates and refuses at call time if none is
 * present. `lib/pdf-text.mjs` turns text operators, fonts and encodings into
 * positioned runs; `lib/pdf-parse.mjs` is the object graph beneath it.
 */
const ENTRY_NAMES = ['extractPdfText', 'extractText', 'extractPdf', 'readPdfText', 'parsePdfText'];

/**
 * Resolved once at module load, by a top-level await, which is what keeps
 * `extractPdf` synchronous. Every other extractor here is synchronous and
 * `extractFile` is part of that contract, so an asynchronous PDF path would have
 * changed the signature every caller already uses.
 *
 * A missing engine is recorded, not thrown. The module still loads, scans that
 * have nothing to do with PDF still run, and a PDF names the absent engine as a
 * refusal. An import that threw here would take down every run of the tool.
 */
const engine = await (async () => {
  const load = async (name) => {
    try {
      return await import(`./${name}.mjs`);
    } catch {
      return null;
    }
  };
  const [parse, text] = await Promise.all([load('pdf-parse'), load('pdf-text')]);
  const modules = [text, parse].filter(Boolean);
  const entryName = ENTRY_NAMES.find(name =>
    modules.some(mod => typeof mod[name] === 'function'));
  if (!entryName) return null;
  const owner = modules.find(mod => typeof mod[entryName] === 'function');
  return { entry: owner[entryName], entryName };
})();

// --- positioned runs to visual lines ----------------------------------------

/**
 * The fallback shape this adapter reads: positioned runs, one entry per visual
 * line of recovered text — the runs on it, in left-to-right order, and the page
 * they sit on.
 *
 *   { page: 1, runs: [{ text, x, y }] }
 *
 * `x` and `y` are the run's horizontal and vertical origin in PDF user space
 * (x grows rightwards, y grows upwards). Only `text` and `page` are required;
 * without positioning the adapter still reads the text correctly, but it
 * cannot order two columns and does not merge lines into blocks, so it produces
 * one unit per line rather than guessing a paragraph structure.
 *
 * An engine that emits the contract's units instead never reaches this
 * function: `isEngineUnits` passes those through with their own `line`,
 * `column` and `pdfPage` intact, because rebuilding them here would discard
 * exactly the geometry the contract asks for.
 */
function normaliseRuns(records) {
  const lines = [];
  for (const record of records ?? []) {
    if (!record || typeof record !== 'object') continue;
    if (Array.isArray(record.lines)) {
      // A page given as its lines. Each line is either a string or a run list.
      let index = 0;
      for (const line of record.lines) {
        const page = record.page ?? index + 1;
        if (typeof line === 'string') {
          lines.push({ page, runs: [{ text: line, x: null, y: null }] });
        } else if (line && typeof line === 'object') {
          lines.push({ page, runs: [normaliseRun(line)] });
        }
        index++;
      }
      continue;
    }
    const page = record.page ?? 1;
    if (Array.isArray(record.runs)) {
      const runs = record.runs.map(normaliseRun).filter(Boolean);
      if (runs.length) lines.push({ page, runs });
    } else if (typeof record.text === 'string') {
      lines.push({ page, runs: [normaliseRun(record)] });
    }
  }
  return lines;
}

function normaliseRun(run) {
  if (typeof run === 'string') return { text: run, x: null, y: null };
  if (!run || typeof run.text !== 'string') return null;
  const num = value => (typeof value === 'number' && Number.isFinite(value) ? value : null);
  return { text: run.text, x: num(run.x) ?? num(run.column), y: num(run.y) ?? num(run.baseline) };
}

/**
 * Reading order: pages ascending, and within a page the lines from the top
 * down. PDF y grows upwards, so "top down" is the larger y first. A document
 * that does not position its text keeps the order the engine emitted, which is
 * the order the engine had to have used to reconstruct the lines.
 */
function inReadingOrder(lines) {
  const positioned = lines.filter(line => line.runs.some(run => run.y !== null));
  if (positioned.length < lines.length) return lines; // not all positioned: engine order stands
  return lines
    .map((line, index) => ({ line, index }))
    .sort((a, b) => {
      const pageDiff = (a.line.page ?? 0) - (b.line.page ?? 0);
      if (pageDiff !== 0) return pageDiff;
      const ay = topY(a.line);
      const by = topY(b.line);
      if (ay !== null && by !== null && ay !== by) return by - ay; // higher on the page first
      return a.index - b.index; // same baseline: engine order, which is left to right
    })
    .map(entry => entry.line);
}

function topY(line) {
  let best = null;
  for (const run of line.runs) if (run.y !== null && (best === null || run.y > best)) best = run.y;
  return best;
}

function leftX(line) {
  let best = null;
  for (const run of line.runs) if (run.x !== null && (best === null || run.x < best)) best = run.x;
  return best;
}

/** One line's runs, left to right, joined with a single space. */
function joinRuns(line) {
  const positioned = line.runs.every(run => run.x !== null);
  const ordered = positioned
    ? line.runs
      .map((run, index) => ({ run, index }))
      .sort((a, b) => (a.run.x === b.run.x ? a.index - b.index : a.run.x - b.run.x))
      .map(entry => entry.run)
    : line.runs;
  return ordered
    .map(run => run.text.replace(/\s+/g, ' ').trim())
    .filter(Boolean)
    .join(' ');
}

/**
 * Group consecutive lines that belong to the same block of text.
 *
 * A PDF carries no paragraph structure, so a block boundary is inferred: two
 * consecutive lines on the same page belong together when the vertical gap
 * between them is no more than 1.8 times the tightest gap on that page (the
 * tightest gap is the intra-paragraph one) and their left edges are within two
 * characters of each other. A larger gap, a different left edge, a page change
 * or any line without a vertical position ends the block.
 *
 * This is a reconstruction, and it is documented as one. It affects only which
 * lines share a unit — never the recovered text, and never a position: a finding
 * is placed through the unit's offset map, so it still points at the exact
 * visual line the character sits on. Where the engine supplies no positions,
 * no grouping is attempted and every line stands alone.
 */
function groupIntoBlocks(lines) {
  const blocks = [];
  let current = null;

  const leadingFor = page => {
    const ys = [];
    for (const line of lines) {
      if ((line.page ?? 0) !== page) continue;
      const y = topY(line);
      if (y !== null) ys.push(y);
    }
    if (ys.length < 2) return null;
    const gaps = [];
    for (let i = 1; i < ys.length; i++) {
      const gap = ys[i - 1] - ys[i];
      if (gap > 0) gaps.push(gap);
    }
    return gaps.length ? Math.min(...gaps) : null;
  };

  for (const line of lines) {
    const y = topY(line);
    const x = leftX(line);
    const last = current ? current.lines[current.lines.length - 1] : null;
    const lastY = last ? topY(last) : null;
    const lastX = last ? leftX(last) : null;
    const leading = leadingFor(line.page ?? 0);

    const continues = Boolean(
      current && last && y !== null && lastY !== null
      && (last.page ?? 0) === (line.page ?? 0)
      && leading !== null
      && (lastY - y) <= leading * 1.8
      && x !== null && lastX !== null
      && Math.abs(x - lastX) <= 2,
    );

    if (continues) current.lines.push(line);
    else {
      current = { page: line.page ?? 1, lines: [line] };
      blocks.push(current);
    }
  }
  return blocks;
}

/**
 * Build the units for a set of positioned lines.
 *
 * The positions address a *synthetic source* built here: one entry per visual
 * line, joined with newlines, so that `posAt` and the `map` work exactly as
 * they do for a real file. Every offset, line and column is an offset into
 * that recovered text, which is why the documents call the line a visual line.
 */
function unitsFromLines(lines, filePath, starts) {
  const blocks = groupIntoBlocks(lines);

  // The synthetic source: the text of every visual line, in reading order,
  // with internal whitespace already collapsed so a unit's map survives
  // `makeUnit`'s equality check.
  const visual = blocks.flatMap(block => block.lines.map(line => joinRuns(line)));
  const source = visual.join('\n');
  const sourceStarts = starts ?? lineStarts(source);

  // Which slice of the synthetic source each visual line occupies. A block that
  // covers several lines starts at its first line and ends after its last.
  const slices = [];
  let cursor = 0;
  for (const text of visual) {
    slices.push({ start: cursor, end: cursor + text.length });
    cursor += text.length + 1;
  }

  const units = [];
  let lineIndex = 0;
  for (const block of blocks) {
    const first = slices[lineIndex];
    const last = slices[lineIndex + block.lines.length - 1];
    lineIndex += block.lines.length;
    if (!first || !last) continue;

    const raw = source.slice(first.start, last.end);
    if (!raw.trim()) continue;

    // `quotes: false` on purpose: quoted material in a PDF is scanned as
    // authored copy, because the file cannot tell a quotation from a paragraph.
    // URLs are masked exactly as they are in every other extractor, so the
    // rules never read a link target as copy.
    const { text, map } = unitText(raw, { base: first.start, quotes: false });
    const unit = makeUnit({
      file: filePath,
      starts: sourceStarts,
      offset: first.start,
      raw,
      text,
      map,
      context: 'authored',
    });
    if (!unit) continue;
    // Carried, not consumed: the rule layer never reads it, and the JSON and
    // SARIF outputs copy it out. The text report keeps `file:line:column`.
    unit.pdfPage = block.page;
    units.push(unit);
  }
  return units;
}

// --- the exported surface ----------------------------------------------------

/**
 * Recover the user-visible copy of a PDF as ordinary units.
 *
 * @param {Buffer|Uint8Array} bytes  the raw file
 * @param {string} filePath          the path to name in every unit
 * @param {object} [options]         `{ starts }` — a precomputed `lineStarts`
 *   for the recovered text; computed here when absent
 * @returns {Promise<object[]>} units, exactly the `makeUnit` shape
 * @throws {PdfRefusalError} when the text cannot be recovered with certainty
 */
/** The PDF file signature: `%PDF-`, within the leading bytes a reader may omit. */
const PDF_MAGIC = Buffer.from('%PDF-', 'latin1');

/**
 * True when the bytes carry the PDF signature. Checked here, before the engine,
 * because it is a fact about the first bytes that needs no parsing at all — and
 * because a file named `.pdf` that is not one should be told so plainly rather
 * than reported as a structural failure inside a document that does not exist.
 * The signature is required to appear within the first 1024 bytes, which is the
 * tolerance the format itself allows for a leading comment.
 */
export function hasPdfSignature(bytes) {
  if (!bytes || bytes.length < PDF_MAGIC.length) return false;
  const window = bytes.subarray(0, Math.min(bytes.length, 1024));
  return window.includes(PDF_MAGIC);
}

export function extractPdf(bytes, filePath, { starts = null } = {}) {
  if (!bytes || typeof bytes.length !== 'number' || bytes.length === 0) {
    throw new PdfRefusalError('the file is empty', { code: 'NOT_A_PDF' });
  }
  if (!hasPdfSignature(bytes)) {
    throw new PdfRefusalError('the file carries no PDF signature', { code: 'NOT_A_PDF' });
  }
  if (!engine) {
    throw new PdfRefusalError(
      'the PDF text engine is not present in this build', { code: 'MALFORMED' });
  }
  let records;
  try {
    records = engine.entry(bytes, filePath);
  } catch (error) {
    // A refusal is re-thrown as this module's class so that a caller which
    // imported the class from here can rely on `instanceof`, and so that an
    // engine error with no code in the contract still refuses rather than
    // escaping as an unhandled failure.
    throw asRefusal(error);
  }
  // An engine that emits the contract's units passes through with them. Those
  // units are already ordered, already split at a gutter, and already carry
  // `line`, `column`, `offset` and `pdfPage` computed from the geometry of the
  // page. Rebuilding them as positioned runs would lose that twice: the
  // synthetic source would be rebuilt without the horizontal indent that makes
  // `column` mean something, collapsing every `column` to 1, and units carry
  // `pdfPage` rather than `page`, so every page would collapse to 1 as well.
  if (isEngineUnits(records)) return records.map(redressUnit);
  return unitsFromLines(inReadingOrder(normaliseRuns(records)), filePath, starts);
}

/**
 * True when the entry returned the contract's units rather than positioned
 * runs. A unit is the only shape here carrying `file` alongside the integer
 * `line`, `column` and `offset` that `makeUnit` computes; a run record carries
 * `text` and, where the engine positioned it, `x` and `y`.
 */
function isEngineUnits(records) {
  if (!Array.isArray(records) || records.length === 0) return false;
  return records.every((record) => record && typeof record === 'object'
    && typeof record.file === 'string'
    && Number.isInteger(record.line)
    && Number.isInteger(record.column)
    && Number.isInteger(record.offset));
}

/**
 * The adapter's whole treatment of a unit the engine already built: mask the
 * copy hazards every other extractor masks, so a rule never reads a link
 * target as copy, and rebuild the offset map so it points at the characters
 * the rule layer will read. `line`, `column`, `offset` and `pdfPage` are the
 * engine's own and are left alone — they were computed from a geometry this
 * adapter never sees.
 */
function redressUnit(unit) {
  if (typeof unit.raw !== 'string') return unit;
  const { text, map } = unitText(unit.raw, { base: unit.offset, quotes: false });
  return { ...unit, text, map };
}
