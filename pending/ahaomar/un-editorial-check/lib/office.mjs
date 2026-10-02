// Word (.docx) and OpenDocument (.odt) input: recover the text, then check it
// with the same extraction-and-rules pipeline as every other format.
//
// A .docx and an .odt are ZIP containers of XML. This module carries a minimal
// ZIP reader (stored and deflate entries only, which is what Word, LibreOffice
// and every mainstream writer emit) and an XML paragraph walker, and then
// synthesises a Markdown document — one line per paragraph, headings marked —
// so the actual extraction, masking, offset mapping and position reporting
// stay in the one place that already owns them (lib/extract-markdown.mjs).
//
// What a recovered document is, and is not: the text is complete and exact for
// the body, but the visual document is not reproduced. Headers, footers, foot
// notes, endnotes, comments, tracked changes and text boxes are out of scope
// for this release and are stated as a limitation wherever the formats are
// documented. Tracked deletions (<w:delText>) are excluded from the copy: a
// deletion a reviewer still sees in tracked mode is not user-visible text, and
// including it would check wording the author already struck out.
//
// Positions: `line` addresses the recovered paragraph, counted from 1 in
// document order (a heading paragraph occupies its own line), and `column`
// addresses the character inside the recovered paragraph text. It is not a
// line of any source file, because a document container has none.
//
// Refusals mirror the PDF contract: a container that cannot be read as a
// document — not a ZIP, an encrypted document, a missing body part — refuses
// with a named reason and a remedy, and never reports a clean run.

import zlib from 'node:zlib';

import { lineStarts } from './position.mjs';
import { extractMarkdown } from './extract-markdown.mjs';

export const OFFICE_REFUSAL_CODES = {
  NOT_A_CONTAINER: 'the file does not have the structure of a ZIP document container',
  NO_BODY: 'the document body part is missing from the container',
  ENCRYPTED: 'the document is encrypted',
  MALFORMED: 'the document structure could not be read',
};

const REMEDY = {
  NOT_A_CONTAINER: 'The file may be misnamed or damaged. Export the document as plain text or Markdown and run the check on that.',
  NO_BODY: 'The file may be incomplete or damaged. Open it, save a fresh copy, and run the check on that; or export the text and check the export.',
  ENCRYPTED: 'Remove the password protection, or save an unprotected copy, and run the check on that copy.',
  MALFORMED: 'The file may be truncated or damaged. Open it, save a fresh copy, and run the check on that.',
};

export class OfficeRefusalError extends Error {
  constructor(message, { code, detail = {} } = {}) {
    super(message);
    this.name = 'OfficeRefusalError';
    this.code = code;
    this.detail = detail;
  }
}

/** A refusal message naming the file, the reason, and what to do instead. */
export function officeRefusalMessage(error, filePath) {
  const code = error && error.code;
  const reason = OFFICE_REFUSAL_CODES[code] ?? OFFICE_REFUSAL_CODES.MALFORMED;
  const stated = typeof error?.message === 'string' ? error.message.trim() : '';
  let head = `cannot read ${filePath}: ${reason}`;
  if (stated && stated !== reason && !stated.includes(reason)) {
    head += ` (${stated})`;
  }
  const remedy = REMEDY[code] ?? REMEDY.MALFORMED;
  return `${head}. ${remedy}`;
}

/** True for an office refusal, however the engine signalled it. */
export function isOfficeRefusal(error) {
  if (error instanceof OfficeRefusalError) return true;
  return Boolean(error && typeof error.code === 'string'
    && Object.hasOwn(OFFICE_REFUSAL_CODES, error.code));
}

// --- the minimal ZIP reader --------------------------------------------------
//
// Central-directory based, like every serious reader: the End of Central
// Directory record sits at the end of the file (the comment field may follow
// it, so the signature is scanned backwards), and each central entry names the
// local header whose fields size the entry's data. This ordering survives ZIP
// writers that prepend variable-sized data to local entries (streaming
// writers), which a naive "read local headers in file order" reader cannot.

const EOCD_SIG = 0x06054b50;
const CEN_SIG = 0x02014b50;
const LOC_SIG = 0x04034b50;

function u16(buffer, at) { return buffer.readUInt16LE(at); }
function u32(buffer, at) { return buffer.readUInt32LE(at); }

/**
 * Read every entry of a ZIP container into a Map of name -> Buffer.
 * Only stored (0) and deflate (8) entries are supported — the methods every
 * mainstream document writer emits. Anything else refuses rather than guesses.
 */
export function readZipEntries(bytes) {
  if (!Buffer.isBuffer(bytes) || bytes.length < 22) {
    throw new OfficeRefusalError('too small to be a ZIP container', { code: 'NOT_A_CONTAINER' });
  }
  // Scan backwards for the EOCD signature: up to the 65 535-byte maximum
  // comment plus the fixed record size.
  const scanFloor = Math.max(0, bytes.length - (22 + 0xffff));
  let eocd = -1;
  for (let i = bytes.length - 22; i >= scanFloor; i--) {
    if (u32(bytes, i) === EOCD_SIG) { eocd = i; break; }
  }
  if (eocd < 0) {
    throw new OfficeRefusalError('no End of Central Directory record', { code: 'NOT_A_CONTAINER' });
  }
  const entryCount = u16(bytes, eocd + 10);
  const centralOffset = u32(bytes, eocd + 16);

  const entries = new Map();
  let at = centralOffset;
  for (let n = 0; n < entryCount; n += 1) {
    if (at + 46 > bytes.length || u32(bytes, at) !== CEN_SIG) {
      throw new OfficeRefusalError(`central directory entry ${n} is unreadable`, { code: 'NOT_A_CONTAINER' });
    }
    const method = u16(bytes, at + 10);
    const compressedSize = u32(bytes, at + 20);
    const nameLength = u16(bytes, at + 28);
    const extraLength = u16(bytes, at + 30);
    const commentLength = u16(bytes, at + 32);
    const localOffset = u32(bytes, at + 42);
    const name = bytes.toString('utf8', at + 46, at + 46 + nameLength);

    // The local header repeats the name and extra-field lengths; a writer may
    // put a different extra-field size in the local record, so the data start
    // must come from the local header itself.
    if (localOffset + 30 > bytes.length || u32(bytes, localOffset) !== LOC_SIG) {
      throw new OfficeRefusalError(`local header for "${name}" is unreadable`, { code: 'NOT_A_CONTAINER' });
    }
    const localNameLength = u16(bytes, localOffset + 26);
    const localExtraLength = u16(bytes, localOffset + 28);
    const dataStart = localOffset + 30 + localNameLength + localExtraLength;
    const dataEnd = dataStart + compressedSize;
    if (dataEnd > bytes.length) {
      throw new OfficeRefusalError(`entry "${name}" is truncated`, { code: 'NOT_A_CONTAINER' });
    }
    const stored = bytes.subarray(dataStart, dataEnd);
    if (method === 0) {
      entries.set(name, Buffer.from(stored));
    } else if (method === 8) {
      try {
        entries.set(name, zlib.inflateRawSync(stored));
      } catch (err) {
        throw new OfficeRefusalError(`entry "${name}" could not be inflated`, { code: 'NOT_A_CONTAINER' });
      }
    } else {
      throw new OfficeRefusalError(`entry "${name}" uses compression method ${method}`, { code: 'NOT_A_CONTAINER' });
    }
    at += 46 + nameLength + extraLength + commentLength;
  }
  return entries;
}

// --- XML paragraph recovery --------------------------------------------------
//
// The walker is deliberately regex-shaped, like every other extraction surface
// in this tool: it recovers the paragraphs a reader sees, and it refuses to be
// clever about anything else.

/** Decode the five named entities and numeric references the writers emit. */
function decodeXml(text) {
  return text
    .replace(/&#x([0-9a-fA-F]+);/g, (_, hex) => safeCodePoint(parseInt(hex, 16)))
    .replace(/&#(\d+);/g, (_, dec) => safeCodePoint(parseInt(dec, 10)))
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&apos;/g, "'")
    .replace(/&amp;/g, '&');
}

function safeCodePoint(code) {
  if (!Number.isSafeInteger(code) || code < 0 || code > 0x10ffff) return '';
  if (code >= 0xd800 && code <= 0xdfff) return '';
  if (code === 0) return '';
  return String.fromCodePoint(code);
}

/**
 * Recover one paragraph's visible text from a DOCX `<w:p>` element.
 * `<w:t>` carries text; `<w:tab/>` and `<w:br/>` are spacing a reader sees;
 * `<w:delText>` is a tracked deletion (struck copy, never user-visible);
 * `<w:instrText>` is a field instruction. Returns '' for a paragraph with no
 * visible run text (an image-only paragraph, for instance).
 */
function docxParagraphText(paragraph) {
  let out = '';
  const re = /<w:(t|tab|br|delText|instrText)\b([^>]*)>([\s\S]*?)<\/w:\1>|<w:(tab|br|cr)\b[^>]*\/>/g;
  let m;
  while ((m = re.exec(paragraph))) {
    if (m[1] === 't') out += m[3];
    else if (m[1] === 'tab' || m[4] === 'tab') out += ' ';
    else if (m[1] === 'br' || m[4] === 'br' || m[4] === 'cr') out += ' ';
    // delText and instrText contribute nothing: struck or invisible.
  }
  return decodeXml(out).replace(/\s+/g, ' ').trim();
}

/** The heading level of a DOCX paragraph, or 0. */
function docxHeadingLevel(paragraph) {
  const style = paragraph.match(/<w:pStyle\s+w:val="(?:Heading|heading)\s*(\d)"/);
  if (style) return Math.min(6, Math.max(1, parseInt(style[1], 10)));
  // Title style is a level-1 heading in editorial terms.
  if (/<w:pStyle\s+w:val="Title"/.test(paragraph)) return 1;
  return 0;
}

/**
 * Recover one paragraph's visible text from an ODT `<text:p>`/`<text:h>`
 * element. Spans and links carry text inline; `<text:s/>`, `<text:tab/>` and
 * `<text:line-break/>` are spacing.
 */
function odtParagraphText(paragraph) {
  let out = paragraph
    .replace(/<text:s\b[^>]*\/>/g, ' ')
    .replace(/<text:tab\b[^>]*\/>/g, ' ')
    .replace(/<text:line-break\b[^>]*\/>/g, ' ')
    .replace(/<text:change\b[^>]*\/>/g, '')
    .replace(/<text:(deletion|change-start)\b[\s\S]*?<\/text:\1>/g, '')
    .replace(/<office:annotation[\s\S]*?<\/office:annotation>/g, '');
  // Every remaining element tag opens or closes a span, a link or a bookmark:
  // the text between them is the copy.
  out = out.replace(/<[^>]+>/g, '');
  return decodeXml(out).replace(/\s+/g, ' ').trim();
}

/** The heading level of an ODT `<text:h>` element, or 0 for `<text:p>`. */
function odtHeadingLevel(paragraph, isOpenHeading) {
  if (!isOpenHeading) return 0;
  const level = paragraph.match(/text:outline-level="(\d)"/);
  return level ? Math.min(6, Math.max(1, parseInt(level[1], 10))) : 1;
}

/**
 * Split an XML body into paragraph elements of the given tag names, returning
 * { text, headingLevel } records in document order. Nested same-name elements
 * are not a DOCX/ODT body reality (paragraphs do not nest), so a single
 * non-greedy close-tag scan is exact for the bodies mainstream writers emit.
 */
function bodyParagraphs(xml, openTags) {
  const out = [];
  const re = new RegExp(`<(${openTags})\\b[^>]*(/>|>[\\s\\S]*?</\\1>)`, 'g');
  let m;
  while ((m = re.exec(xml))) {
    out.push({ element: m[0], isOpenHeading: /^text:h$/.test(m[1]) });
  }
  return out;
}

/**
 * The synthesised Markdown source: one line per paragraph, headings marked
 * with the ATX form the Markdown extractor already understands. Empty
 * paragraphs produce an empty line, so paragraph numbering is stable whether
 * or not a paragraph carried visible copy.
 */
function synthesise(paragraphs) {
  const lines = [];
  for (const { text, headingLevel } of paragraphs) {
    if (!text) { lines.push(''); continue; }
    lines.push(headingLevel ? `${'#'.repeat(headingLevel)} ${text}` : text);
  }
  return lines.join('\n');
}

function extractContainer(entries, filePath, kind) {
  let body;
  if (kind === 'docx') {
    // An encrypted DOCX (the ODF-CFIF wrap) carries no word/document.xml at
    // all; an OLE-embedded encrypted package shows up as an unencrypted ZIP
    // whose only content is the encrypted payload. Either way the body part is
    // absent, and that is the honest refusal.
    if (entries.has('EncryptionInfo') || entries.has('EncryptedPackage')) {
      throw new OfficeRefusalError('the container carries an encrypted package', { code: 'ENCRYPTED' });
    }
    body = entries.get('word/document.xml');
    if (body === undefined) {
      throw new OfficeRefusalError('no word/document.xml in the container', { code: 'NO_BODY' });
    }
  } else if (entries.has('mimetype') && entries.get('mimetype').toString('utf8').includes('opendocument.text')) {
    body = entries.get('content.xml');
    if (body === undefined) {
      throw new OfficeRefusalError('no content.xml in the container', { code: 'NO_BODY' });
    }
  } else {
    throw new OfficeRefusalError('no content.xml in the container', { code: 'NO_BODY' });
  }

  const xml = body.toString('utf8');
  const openTags = kind === 'docx' ? 'w:p' : 'text:p|text:h';
  const paragraphs = bodyParagraphs(xml, openTags).map(({ element, isOpenHeading }) => ({
    text: kind === 'docx'
      ? docxParagraphText(element)
      : odtParagraphText(element),
    headingLevel: kind === 'docx'
      ? docxHeadingLevel(element)
      : odtHeadingLevel(element, isOpenHeading),
  }));

  const source = synthesise(paragraphs);
  if (!source.trim()) {
    // An empty document is a refusal, not a clean run: nothing was read to
    // judge, and the clean sentence must never print for an unread document.
    throw new OfficeRefusalError('the document body carries no recoverable text', { code: 'MALFORMED' });
  }
  // The Markdown pipeline owns masking, offset maps, contexts and positions;
  // this module only decides what copy exists and what kind of paragraph it is.
  return extractMarkdown(source, filePath, { starts: lineStarts(source) });
}

/**
 * Public entry points. Each verifies the container is the kind the extension
 * claims before walking it, so a misnamed file refuses rather than misparses.
 */
export function extractDocx(bytes, filePath) {
  const entries = readZipEntries(bytes);
  // An encrypted DOCX is a ZIP whose payload is the encrypted package; the
  // body part is absent by design, so the encryption check comes first and the
  // refusal names the real reason rather than a missing part.
  if (entries.has('EncryptionInfo') || entries.has('EncryptedPackage')) {
    throw new OfficeRefusalError('the container carries an encrypted package', { code: 'ENCRYPTED' });
  }
  if (!entries.has('[Content_Types].xml') || !entries.has('word/document.xml')) {
    throw new OfficeRefusalError('no word/document.xml in the container', { code: 'NO_BODY' });
  }
  return extractContainer(entries, filePath, 'docx');
}

export function extractOdt(bytes, filePath) {
  const entries = readZipEntries(bytes);
  const mime = entries.get('mimetype');
  if (!mime || !mime.toString('utf8').includes('opendocument.text')) {
    throw new OfficeRefusalError('the container is not an OpenDocument text document', { code: 'NO_BODY' });
  }
  return extractContainer(entries, filePath, 'odt');
}

// Re-exported for the suite that proves the reader against its specification.
export { readZipEntries as _readZipEntries, synthesise as _synthesise,
  docxParagraphText as _docxParagraphText, odtParagraphText as _odtParagraphText };
