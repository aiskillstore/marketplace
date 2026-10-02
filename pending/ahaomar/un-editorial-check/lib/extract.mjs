// Extension dispatch. Only surfaces that carry user-visible copy are
// extracted; .json, .css and other implementation files are not collected by
// the scanner at all, and anything unsupported yields no units rather than
// being scanned as raw text.
//
// Binary content guard: a file whose bytes are not valid UTF-8 is not
// user-visible copy in any of these formats, and a misnamed binary — a PNG
// called notes.txt, a UTF-16 export called report.txt — is read with
// replacement characters, which the rules then read as prose. That produced
// findings invented from bytes that are not text (a "Bare US in prose" inside
// a PNG header) and, worse, let `--fix --apply` write the lossy round-trip back
// over the original bytes. extractFile therefore decodes strictly and returns
// no units for content that is not UTF-8, exactly as it returns no units for
// an unsupported extension. A readable .txt is untouched: the check is
// validity, not content, so prose with any script in it still scans.
//
// The drop is reported, never silent. `undecodableReason` is the single
// predicate, exported so the CLI can ask the same question the extractor asked
// and count the file as skipped rather than scanned: a run that never decoded a
// file must not report it as scanned, because "scanned 1 file" and the clean
// sentence are otherwise byte-identical to a run over a genuinely empty file,
// and a reader — or a CI job — cannot tell the two apart. That is the shape of
// QA finding F1, where a run printed the clean sentence having read nothing.
//
// The predicate is deliberately cheap on the common path: a file whose decode
// produced no replacement character is valid UTF-8, so the answer is no without
// touching the file system at all.

import fs from 'node:fs';
import path from 'node:path';
import { lineStarts } from './position.mjs';
import { extractHTML } from './extract-html.mjs';
import { extractMarkdown } from './extract-markdown.mjs';
import { extractText } from './extract-text.mjs';
import { extractJS } from './extract-js.mjs';
import { extractPdf } from './pdf-extract.mjs';
import { extractDocx, extractOdt } from './office.mjs';

// Ordered canonical list of every file format the checker claims to support.
// README.md and USER-GUIDE.md list these same extensions; keep them in sync.
export const SUPPORTED_EXTENSIONS = [
  '.md', '.markdown', '.txt',
  '.html', '.htm',
  '.js', '.mjs', '.cjs', '.jsx',
  '.ts', '.tsx',
  '.pdf',
  '.docx', '.odt',
];

/**
 * Formats whose bytes are not UTF-8 text, so the decode guard below does not
 * apply to them. A PDF is a binary container: it is read as a Buffer and handed
 * to the PDF adapter whole, never decoded to a string first. `.pdf` is the only
 * member; the set exists so the guard reads as a decision about *kind* of
 * input rather than a special case for one extension.
 */
export const BINARY_EXTENSIONS = new Set(['.pdf', '.docx', '.odt']);

export const EXTRACTABLE_EXTENSIONS = new Set(SUPPORTED_EXTENSIONS);

const REPLACEMENT = '\uFFFD';
const NUL = '\u0000';
const STRICT_UTF8 = new TextDecoder('utf-8', { fatal: true });

/** The reason a file yields no copy because its bytes are not readable text. */
export const UNDECODABLE_REASON = 'not valid UTF-8';

/**
 * Null when `source` is scannable copy, or the reason it is not.
 *
 * Two independent signals, because a misnamed binary reaches this function by
 * two different routes and each needs its own test.
 *
 * 1. **A NUL byte.** A UTF-16 export is *valid* UTF-8 — every character is
 *    followed by a zero byte — so a strict decode succeeds and the file decodes
 *    to NUL-interleaved text. The extractors wrap that into copy spans whose
 *    characters do not correspond to anything a reader would see, and the rules
 *    then read positions that mean nothing. No editorial copy contains NUL, in
 *    any script, so its presence is proof the bytes are not the text they claim
 *    to be. This is the same signal version control uses to tell text from
 *    binary, and it is what makes a misnamed UTF-16 `.txt` a skip rather than a
 *    scan of garbage.
 *
 * 2. **A replacement character.** Node's decoder substitutes U+FFFD for a byte
 *    it cannot decode. A file that legitimately contains U+FFFD must not be
 *    excluded, so the ambiguous case is settled against the file's actual
 *    bytes: a strict decode that throws is proof the bytes are not UTF-8.
 *
 * Any failure to read the bytes back (a caller that passed text not on disk)
 * leaves the source scannable, so this guard can never exclude a file it
 * cannot prove.
 *
 * @param {string} source  the decoded file content
 * @param {string} filePath
 * @returns {string|null} UNDECODABLE_REASON, or null
 */
export function undecodableReason(source, filePath) {
  if (source.includes(NUL)) return UNDECODABLE_REASON;
  if (!source.includes(REPLACEMENT)) return null;
  let bytes;
  try {
    bytes = fs.readFileSync(filePath);
  } catch {
    return null;
  }
  try {
    STRICT_UTF8.decode(bytes);
    return null; // valid UTF-8 that genuinely contains U+FFFD
  } catch {
    return UNDECODABLE_REASON;
  }
}

/**
 * True when `source` is a raw binary buffer for a binary format, rather than
 * decoded text. `lib/cli.mjs` reads a `.pdf` as a Buffer precisely so the
 * adapter receives the bytes; this predicate is how `extractFile` knows the
 * difference without being told which branch the caller took.
 */
export function isBinarySource(source) {
  return Buffer.isBuffer(source) || source instanceof Uint8Array;
}

export function extractFile(filePath, source, { renderTargets = [], extraExtensions = {}, ext: extOverride = null } = {}) {
  // A record may carry its own extension (a URL has no path suffix, a
  // synthetic name carries one); the override wins over the file name.
  const ext = (extOverride || path.extname(filePath).toLowerCase()).toLowerCase();
  // A project-configured extension is read under an existing extractor's
  // contract (.mdx as Markdown, .vue/.twig as HTML, a custom suffix as plain
  // text). The mapping never changes the masking rules, only which parser
  // walks the bytes.
  const mappedKind = extraExtensions[ext];

  // Binary dispatch comes first, and deliberately so. The UTF-8 guard below
  // reasons about decoded text: a PDF is not decoded text, so running the guard
  // on it would either reject every real PDF (its bytes are not valid UTF-8)
  // or, worse, let it through after a lossy decode and scan garbage. The Buffer
  // has to reach `extractPdf` intact, and the only way to guarantee that is for
  // the binary branch to precede the guard. A caller that passes a PDF as a
  // string is refused rather than parsed, because a lossy decode cannot be
  // undone and the adapter's contract is bytes in.
  if (BINARY_EXTENSIONS.has(ext)) {
    if (!isBinarySource(source)) return [];
    if (ext === '.docx') return extractDocx(source, filePath);
    if (ext === '.odt') return extractOdt(source, filePath);
    return extractPdf(source, filePath);
  }

  if (isBinarySource(source)) return [];
  if (undecodableReason(source, filePath)) return [];
  const starts = lineStarts(source);
  const options = { starts, renderTargets };

  switch (ext) {
    case '.html':
    case '.htm':
      return extractHTML(source, filePath, options);
    case '.md':
    case '.markdown':
      return extractMarkdown(source, filePath, options);
    case '.txt':
      return extractText(source, filePath, options);
    case '.js':
    case '.mjs':
    case '.cjs':
    case '.jsx':
    case '.ts':
    case '.tsx':
      return extractJS(source, filePath, { starts, offsetBase: 0, renderTargets });
    default:
      if (mappedKind === 'markdown') return extractMarkdown(source, filePath, options);
      if (mappedKind === 'html') return extractHTML(source, filePath, options);
      if (mappedKind === 'text') return extractText(source, filePath, options);
      return [];
  }
}
