// Optional, explicitly requested audits: publishing (SEO/page metadata),
// accessibility and security.
//
// These inspect raw source and markup structure, not extracted copy, which is
// exactly why they are NOT part of the editorial default. They run only when
// named on the command line (--profile publishing) or loaded from an audit
// profile file, their findings are reported in their own section, and they
// never affect the exit code.
//
// Detection lives here; metadata (severity, category, confidence, scope) comes
// from rules/catalogue.json so both sets of rules are described the same way.

import { lineStarts, posAt } from './position.mjs';
import { decodeEntities, maskHtmlComments } from './units.mjs';
import { tokenizeJS } from './tokenize.mjs';

export const AUDIT_NAMES = ['publishing', 'accessibility', 'security'];

const HTML = new Set(['.html', '.htm']);
const SCRIPTY = new Set(['.js', '.mjs', '.cjs', '.ts', '.jsx', '.tsx']);

function makeFinder(file, source) {
  const starts = lineStarts(source);
  return (offset, ruleId, message, suggestion, meta) => {
    const { line, column } = posAt(starts, Math.max(0, offset));
    return {
      file,
      line,
      column,
      ruleId,
      category: meta.category,
      severity: meta.severity,
      confidence: meta.confidence,
      scope: meta.scope,
      message,
      suggestion: suggestion || null,
    };
  };
}

function attrsOf(tag) {
  const attrs = new Map();
  const re = /([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(?:"([^"]*)"|'([^']*)')/g;
  let m;
  while ((m = re.exec(tag))) attrs.set(m[1].toLowerCase(), m[2] !== undefined ? m[2] : m[3]);
  return attrs;
}

// --- publishing -------------------------------------------------------------

function runPublishing(files, ctx) {
  const out = [];
  for (const { file, source, ext } of files) {
    if (!HTML.has(ext)) continue;
    const emit = makeFinder(file, source);

    const title = source.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
    if (!title) {
      out.push(emit(0, 'UE-EO001', 'No <title> element found.', 'Add a page title of at most 60 characters.', ctx.meta['UE-EO001']));
    } else {
      // Length limits apply to what a reader and a search engine see, so
      // `&amp;` counts as one character, not five.
      const length = decodeEntities(title[1]).trim().length;
      if (length === 0) {
        out.push(emit(title.index, 'UE-EO001', 'Empty <title>.', 'Add a page title of at most 60 characters.', ctx.meta['UE-EO001']));
      } else if (length > 60) {
        out.push(emit(title.index, 'UE-EO001', `<title> is ${length} characters (recommended maximum 60).`, 'Shorten the title.', ctx.meta['UE-EO001']));
      }
    }

    const description = source.match(/<meta[^>]+name=["']description["'][^>]*content=["']([^"']*)["'][^>]*>/i)
      || source.match(/<meta[^>]+content=["']([^"']*)["'][^>]*name=["']description["'][^>]*>/i);
    if (!description) {
      out.push(emit(0, 'UE-EO002', 'No meta description found.', 'Add a description of at most 160 characters.', ctx.meta['UE-EO002']));
    } else {
      const length = decodeEntities(description[1]).trim().length;
      if (length === 0) {
        out.push(emit(description.index, 'UE-EO002', 'Empty meta description.', 'Add a description of at most 160 characters.', ctx.meta['UE-EO002']));
      } else if (length > 160) {
        out.push(emit(description.index, 'UE-EO002', `Meta description is ${length} characters (recommended maximum 160).`, 'Shorten the description.', ctx.meta['UE-EO002']));
      }
    }

    const canonical = source.match(/<link[^>]+rel=["']canonical["'][^>]*href=["']([^"']*)["'][^>]*>/i)
      || source.match(/<link[^>]+href=["']([^"']*)["'][^>]*rel=["']canonical["'][^>]*>/i);
    if (!canonical) {
      out.push(emit(0, 'UE-EO003', 'No canonical link found.', 'Add <link rel="canonical"> pointing at the page URL.', ctx.meta['UE-EO003']));
    } else if (!/^https?:\/\//i.test(canonical[1])) {
      out.push(emit(canonical.index, 'UE-EO003', 'Canonical link is not an absolute URL.', 'Use an absolute http(s) URL.', ctx.meta['UE-EO003']));
    } else if (ctx.cfg.baseOrigin) {
      try {
        const origin = new URL(canonical[1]).origin;
        const expected = new URL(ctx.cfg.baseOrigin).origin;
        if (origin !== expected) {
          out.push(emit(canonical.index, 'UE-EO003', `Canonical origin "${origin}" does not match the configured origin "${expected}".`, 'Point the canonical link at the deployment origin.', ctx.meta['UE-EO003']));
        }
      } catch { /* validated above; keep the audit quiet on odd input */ }
    }

    const h1Count = (source.match(/<h1[\s>]/gi) || []).length;
    if (h1Count !== 1) {
      const at = source.search(/<h1[\s>]/i);
      out.push(emit(at < 0 ? 0 : at, 'UE-EO004', `Page has ${h1Count} <h1> elements; exactly one is expected.`, 'Keep exactly one first-level heading.', ctx.meta['UE-EO004']));
    }

    const hasOpenGraph = /<meta[^>]+property=["']og:/i.test(source);
    const hasTwitter = /<meta[^>]+name=["']twitter:/i.test(source);
    if (!hasOpenGraph || !hasTwitter) {
      out.push(emit(0, 'UE-EO005', `Page is missing ${!hasOpenGraph && !hasTwitter ? 'Open Graph and Twitter' : !hasOpenGraph ? 'Open Graph' : 'Twitter'} metadata.`, 'Add og:* and twitter:* meta tags for shared links.', ctx.meta['UE-EO005']));
    }
  }
  return out;
}

// --- accessibility ----------------------------------------------------------

function runAccessibility(files, ctx) {
  const out = [];
  for (const { file, source, ext } of files) {
    if (!HTML.has(ext)) continue;
    const emit = makeFinder(file, source);

    let m;
    const canvasRe = /<canvas\b([^>]*)>/gi;
    while ((m = canvasRe.exec(source))) {
      if (!/aria-label=|aria-labelledby=|role=["']img["']/i.test(m[1])) {
        out.push(emit(m.index, 'UE-AX001', 'Canvas has no accessible name.', 'Add aria-label or role="img" with a label.', ctx.meta['UE-AX001']));
      }
    }

    const imgRe = /<img\b([^>]*)>/gi;
    while ((m = imgRe.exec(source))) {
      if (!/\balt=/i.test(m[1])) {
        out.push(emit(m.index, 'UE-AX001', 'Image has no alt attribute.', 'Add alt text, or alt="" for decorative images.', ctx.meta['UE-AX001']));
      }
    }

    const controlRe = /<(input|select|textarea)\b([^>]*)>/gi;
    while ((m = controlRe.exec(source))) {
      const attrs = attrsOf(m[0]);
      if (/type=["'](hidden|submit|button|image)["']/i.test(m[2])) continue;
      const id = attrs.get('id');
      const labelled = /aria-label=|aria-labelledby=/i.test(m[2])
        || (id && new RegExp(`<label[^>]+for=["']${id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}["']`, 'i').test(source));
      if (!labelled) {
        out.push(emit(m.index, 'UE-AX002', `<${m[1]}> has no associated <label> or aria-label.`, 'Associate a label with the control.', ctx.meta['UE-AX002']));
      }
    }
  }
  return out;
}

// --- security ---------------------------------------------------------------

/**
 * Blank JavaScript comments in place. Commented-out sinks are not live code,
 * and the tokenizer — unlike a naive `//` regex — knows that `http://` inside a
 * string literal is not a comment. Length and line breaks are preserved so the
 * reported position still points at the real source.
 */
function maskScriptComments(source) {
  let out = source;
  for (const token of tokenizeJS(source)) {
    if (token.type !== 'comment') continue;
    out = out.slice(0, token.start) + token.text.replace(/[^\n]/g, ' ') + out.slice(token.end);
  }
  return out;
}

/** The value of a tag's rel attribute, whatever quoting style it uses. */
function relValue(tag) {
  const match = tag.match(/\brel=(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i);
  if (!match) return '';
  return match[1] ?? match[2] ?? match[3] ?? '';
}

function runSecurity(files, ctx) {
  const out = [];
  for (const { file, source, ext } of files) {
    const emit = makeFinder(file, source);
    const isHtml = HTML.has(ext);
    const isScript = SCRIPTY.has(ext);
    if (!isHtml && !isScript) continue;

    // Commented-out code is not live code. Blanking comments in place keeps
    // every offset valid, so a finding still points at the real source.
    const live = isHtml ? maskHtmlComments(source) : maskScriptComments(source);

    if (isScript) {
      let m;
      const sinkRe = /\.(innerHTML|outerHTML)\s*=/g;
      while ((m = sinkRe.exec(live))) {
        out.push(emit(m.index, 'UE-SE001',
          `Assignment to ${m[1]} — a DOM XSS sink if the value includes unsanitised input.`,
          'Prefer textContent, an auto-escaping template, or a sanitiser.', ctx.meta['UE-SE001']));
      }
      const dangerousRe = /\beval\s*\(|new\s+Function\s*\(/g;
      while ((m = dangerousRe.exec(live))) {
        out.push(emit(m.index, 'UE-SE004', 'Dynamic code execution (eval or Function constructor).', 'Remove dynamic code evaluation.', ctx.meta['UE-SE004']));
      }
    }

    if (isHtml) {
      let m;
      // Subresource Integrity is meaningful for scripts and stylesheets only:
      // a canonical, alternate or preload link must never be reported for
      // missing it.
      const assetRe = /<(script|link)\b[^>]+(?:src|href)=["']https?:\/\/[^"']+["'][^>]*>/gi;
      while ((m = assetRe.exec(live))) {
        const tag = m[0];
        if (m[1] === 'link' && !/\bstylesheet\b/i.test(relValue(tag))) continue;
        if (/\bintegrity=/i.test(tag)) continue;
        out.push(emit(m.index, 'UE-SE002',
          'External script or stylesheet has no Subresource Integrity attribute.',
          'Add integrity="sha384-…" (and crossorigin) or serve the asset yourself.', ctx.meta['UE-SE002']));
      }
      const blankRe = /<a\b[^>]*target=["']_blank["'][^>]*>/gi;
      while ((m = blankRe.exec(live))) {
        if (!/rel=["'][^"']*\bnoopener\b/i.test(m[0]) && !/rel=["'][^"']*\bnoreferrer\b/i.test(m[0])) {
          out.push(emit(m.index, 'UE-SE003', 'target="_blank" without rel="noopener".', 'Add rel="noopener" (or "noreferrer").', ctx.meta['UE-SE003']));
        }
      }
    }
  }
  return out;
}

const RUNNERS = {
  publishing: runPublishing,
  accessibility: runAccessibility,
  security: runSecurity,
};

/**
 * @param {Map<string,Set<string>>|string[]} audits  audit name -> allowed rule ids
 *                                                   (a bare name means every rule)
 * @param {Array} files       [{ file, source, ext }]
 * @param {object} ctx        { meta, cfg } where cfg.rules may disable or re-grade audit rules
 */
export function runAudits(audits, files, ctx) {
  const requested = audits instanceof Map
    ? [...audits].map(([name, rules]) => ({ name, rules }))
    : [...new Set(audits)].map(name => ({ name, rules: null }));

  const findings = [];
  for (const { name, rules } of requested) {
    const run = RUNNERS[name];
    if (!run) throw new Error(`unknown audit "${name}"`);
    for (const finding of run(files, ctx)) {
      if (rules && !rules.has(finding.ruleId)) continue;
      const setting = ctx.cfg.rules[finding.ruleId];
      if (setting && setting.enabled === false) continue;
      if (setting && setting.severity) finding.severity = setting.severity;
      finding.audit = name;
      findings.push(finding);
    }
  }
  findings.sort((a, b) =>
    a.file.localeCompare(b.file) || a.line - b.line || a.column - b.column ||
    a.ruleId.localeCompare(b.ruleId));
  return findings;
}
