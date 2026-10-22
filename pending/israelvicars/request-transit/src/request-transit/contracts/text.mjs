// contracts/text.mjs: tiny source helpers for the regex-and-brackets extractors (no compiler dependency).
// Comments are blanked to spaces so offsets and line numbers still point at the original file.
export function blankComments(src) {
  let out = '', i = 0;
  while (i < src.length) {
    const c = src[i], n = src[i + 1];
    if (c === '/' && n === '/') { while (i < src.length && src[i] !== '\n') { out += ' '; i++; } continue; }
    if (c === '/' && n === '*') { while (i < src.length && !(src[i] === '*' && src[i + 1] === '/')) { out += src[i] === '\n' ? '\n' : ' '; i++; } out += '  '; i += 2; continue; }
    if (c === '"' || c === "'" || c === '`') { const q = c; out += c; i++; while (i < src.length && src[i] !== q) { if (src[i] === '\\') { out += src[i++]; } out += src[i++]; } out += src[i++] || ''; continue; }
    out += c; i++;
  }
  return out;
}
const OPEN = { '(': ')', '[': ']', '{': '}', '<': '>' };
// index of the bracket closing the one at `at` (strings skipped). '<' only balances against '>'.
export function closeOf(s, at) {
  const stack = [OPEN[s[at]]];
  for (let i = at + 1; i < s.length; i++) {
    const c = s[i];
    if (c === '"' || c === "'" || c === '`') { const q = c; i++; while (i < s.length && s[i] !== q) { if (s[i] === '\\') i++; i++; } continue; }
    if (c === '=' && s[i + 1] === '>') { i++; continue; }      // arrow, not a closing angle
    if (OPEN[c] && (c !== '<' || stack[stack.length - 1] === '>' || /\w/.test(s[i - 1] || ''))) { stack.push(OPEN[c]); continue; }
    if (c === stack[stack.length - 1]) { stack.pop(); if (!stack.length) return i; continue; }
    if (c === '>' ) continue;
  }
  return -1;
}
// split at top-level separators (outside (), [], {}, <> and strings)
export function splitTop(s, sep) {
  const out = []; let depth = 0, cur = '';
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (c === '"' || c === "'" || c === '`') { const q = c; let j = i + 1; while (j < s.length && s[j] !== q) { if (s[j] === '\\') j++; j++; } cur += s.slice(i, j + 1); i = j; continue; }
    if (c === '=' && s[i + 1] === '>') { cur += '=>'; i++; continue; }
    if ('([{'.includes(c) || (c === '<' && /\w/.test(s[i - 1] || ''))) depth++;
    else if (')]}'.includes(c) || (c === '>' && depth > 0)) depth--;
    if (depth === 0 && sep.includes(c)) { out.push(cur); cur = ''; continue; }
    cur += c;
  }
  out.push(cur);
  return out.map((x) => x.trim()).filter(Boolean);
}
export const lineOf = (s, idx) => { let n = 1; for (let i = 0; i < idx && i < s.length; i++) if (s[i] === '\n') n++; return n; };
// end of a `const x = ...` initializer: the first ';' or blank-line/newline at depth 0 after balanced brackets
export function exprEnd(s, start) {
  let depth = 0;
  for (let i = start; i < s.length; i++) {
    const c = s[i];
    if (c === '"' || c === "'" || c === '`') { const q = c; i++; while (i < s.length && s[i] !== q) { if (s[i] === '\\') i++; i++; } continue; }
    if ('([{'.includes(c)) depth++;
    else if (')]}'.includes(c)) depth--;
    else if (depth === 0 && (c === ';' || (c === '\n' && !/^\s*[.)]/.test(s.slice(i + 1, i + 40))))) return i;
  }
  return s.length;
}
export const unquote = (k) => k.replace(/^['"`]|['"`]$/g, '');
// a.b(c).d() -> [{name:'a'}, {name:'b', args:'c'}, {name:'d', args:''}]
export function chain(expr) {
  return splitTop(expr.trim(), '.').map((p) => {
    const i = p.indexOf('(');
    if (i < 0) return { name: p.trim() };
    const j = closeOf(p, i);
    return { name: p.slice(0, i).trim(), args: p.slice(i + 1, j < 0 ? p.length : j).trim() };
  });
}
