// core/scrub.mjs: value-based scrubbing, run on every trace before anything is rendered.
// Key-based redaction (build.mjs DEFAULT_REDACT) drops whole attributes by name; this pass rewrites the
// strings that are always drawn or inlined: service and span names, peers, operations, status messages,
// attribute values, the source note and warnings. The default level is meant to be safe to share.
//
// levels (build/render flags):
//   default         emails, bearer/basic credentials, JWTs, known token prefixes (GitHub, Slack, AWS keys,
//                   Stripe, OpenAI, GitLab, npm, PostHog...), key=value secrets (password=, token:, api_key=...),
//                   URL userinfo and query strings, long hex (>= 32) and long base64-like runs, UUIDs,
//                   home directories (/Users/<name>, /home/<name>, C:\Users\<name>), AWS account ids in ARNs;
//                   CI runs lose the PR/commit title and the branch name
//   --strict        (alias --share) also IPv4/IPv6 addresses, internal host names (.internal .local .lan .corp
//                   .intranet .svc .cluster.local and hosts inside URLs), long numeric ids (>= 6 digits), and keeps
//                   only a minimal attribute allowlist
//   --keep-uuids    keep UUIDs (default level only)      --keep-ci-titles   keep CI run titles and branch names
//   --no-scrub      off (local debugging only; the page is NOT safe to share)
// Placeholders are bracketed, e.g. [email], so a reader can see something was removed.

const KEYS = 'password|passwd|pwd|pass|secret|client[_-]?secret|token|access[_-]?token|refresh[_-]?token|id[_-]?token|api[_-]?key|apikey|x-api-key|access[_-]?key|private[_-]?key|auth|authorization|credentials?|session(?:[_-]?id)?|sid|sig|signature|key|cookie';
// base64/base64url secrets vs kebab-case names and paths: a secret has one long unbroken run (>= 24) that mixes
// upper, lower and digits with high character entropy; "feature/jira-1234-big-customer" has only short words
const entropy = (x) => { const f = {}; for (const ch of x) f[ch] = (f[ch] || 0) + 1; return Object.values(f).reduce((h, c) => h - (c / x.length) * Math.log2(c / x.length), 0); };
function looksSecret(m) {
  const run = m.split(/[-_/+.=]/).reduce((a, b) => (b.length > a.length ? b : a), '');
  return run.length >= 24 && /[a-z]/.test(run) && /[A-Z]/.test(run) && /\d/.test(run) && entropy(run) >= 4;
}
// key=value always counts; with a colon ("session: tool calls" is prose) only a strong secret key or a value that looks
// like a secret (has a digit or symbol, or is a long unbroken run) is redacted
const STRONG = /^(password|passwd|pwd|secret|client[_-]?secret|api[_-]?key|apikey|x-api-key|access[_-]?key|private[_-]?key|access[_-]?token|refresh[_-]?token|id[_-]?token|authorization|credentials?)$/i;
function kvReplace(m, k, sep, v) {
  if (/^\[[a-z-]+\]$/.test(v) || /^(bearer|basic|token)$/i.test(v)) return m;
  const bare = v.replace(/^["']|["']$/g, '');
  if (sep.includes(':') && !STRONG.test(k) && !/[\d!@#$%^&*+/=_~-]/.test(bare) && bare.length < 16) return m;
  return `${k}${sep}[redacted]`;
}
const RULES = [
  // URL userinfo first, then query strings, so the URL rules see whole URLs
  ['userinfo', /\b([a-z][a-z0-9+.-]*:\/\/)[^\s/@:]+(?::[^\s/@]*)?@/gi, '$1[credentials]@'],
  ['query', /((?:\b[a-z][a-z0-9+.-]*:\/\/[^\s?#"'<>]+|(?:^|(?<=[\s"'(=]))\/[^\s?#"'<>]*))\?[^\s#"'<>]+/gi, '$1?[query]'],
  ['jwt', /\beyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}/g, '[jwt]'],
  ['bearer', /\b(bearer|basic|token)\s+[A-Za-z0-9._~+/=-]{8,}/gi, '$1 [token]'],
  ['token', /\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[abprs]-[A-Za-z0-9-]{10,}|(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{10,}|sk-[A-Za-z0-9_-]{20,}|glpat-[A-Za-z0-9_-]{20,}|npm_[A-Za-z0-9]{30,}|ph[cxs]_[A-Za-z0-9]{20,}|(?:AKIA|ASIA)[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{30,})\b/g, '[token]'],
  ['kv', new RegExp(`\\b(${KEYS})(\\s*[=:]\\s*)("[^"]*"|'[^']*'|[^\\s&,;)"'\\]}]+)`, 'gi'), kvReplace],
  ['email', /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, '[email]'],
  ['arn', /(\barn:aws[a-z-]*:[a-z0-9-]*:[a-z0-9-]*:)\d{12}(?=:)/g, '$1[account]'],
  ['home', /(\/Users\/|\/home\/|[A-Za-z]:\\Users\\)[^\s/\\:"']+/g, (m, p) => (p.includes('\\') ? 'C:\\Users\\[user]' : `${p}[user]`)],
  ['uuid', /\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, '[uuid]', 'uuids'],
  ['hex', /\b[0-9a-f]{32,}\b/gi, '[hex]'],
  ['b64', /(?<![A-Za-z0-9+/_-])[A-Za-z0-9+/_-]{32,}={0,2}(?![A-Za-z0-9+/_-])/g, (m) => (looksSecret(m) ? '[secret]' : m)],
];
const STRICT_RULES = [
  ['ipv4', /\b(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}\b/g, '[ip]'],
  // full 8-group form, or a compressed form with "::" and at least one group (clock times like 10:30:00 never match)
  ['ipv6', /(?<![\w:])(?:(?:[0-9a-f]{1,4}:){7}[0-9a-f]{1,4}|(?:[0-9a-f]{1,4}(?::[0-9a-f]{1,4})*)?::(?:[0-9a-f]{1,4}(?::[0-9a-f]{1,4})*)?)(?![\w:])/gi, (m) => (/[0-9a-f]/i.test(m) ? '[ip]' : m)],
  ['url-host', /\b([a-z][a-z0-9+.-]*:\/\/)(?!\[)[^\s/?#"'<>]+/gi, '$1[host]'],
  ['internal-host', /\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:internal|local|lan|corp|intranet|svc|cluster\.local|home\.arpa)\b/gi, '[internal-host]'],
  ['long-id', /(?<![\w.])\d{6,}(?![\w.])/g, '[id]'],
];
// attributes kept in --strict (values are still scrubbed); ci.step.* and ci.needs.from are structural: CI steps are stations only with them
const STRICT_ATTRS = /^(http\.(request\.method|method|response\.status_code|status_code|route)|rpc\.(system|service|method|grpc\.status_code)|db\.system|messaging\.(system|operation)|ci\.(job|conclusion|needs|needs\.from|attempt|event|step\.number|step\.name)|agent\.source|component)$/;

export function scrubLevel(opt = {}) {
  if (opt['no-scrub'] || opt.scrub === 'off') return { level: 'off' };
  const strict = !!(opt.strict || opt.share || opt.scrub === 'strict');
  return { level: strict ? 'strict' : 'default', uuids: strict || !opt['keep-uuids'], ciTitles: !opt['keep-ci-titles'] };
}

export function scrubString(value, cfg = { level: 'default', uuids: true }, counts = {}) {
  if (typeof value !== 'string' || !value || cfg.level === 'off') return value;
  let s = value;
  for (const [name, re, rep, flag] of cfg.level === 'strict' ? [...RULES, ...STRICT_RULES] : RULES) {
    if (flag && !cfg[flag]) continue;
    s = s.replace(re, (...m) => {
      const out = typeof rep === 'function' ? rep(...m) : rep.replace(/\$(\d)/g, (_, i) => (typeof m[i] === 'string' ? m[i] : ''));
      if (out !== m[0]) counts[name] = (counts[name] || 0) + 1;
      return out;
    });
  }
  return s;
}

const scrubValue = (v, cfg, counts) => typeof v === 'string' ? scrubString(v, cfg, counts) : Array.isArray(v) ? v.map((x) => scrubValue(x, cfg, counts)) : v;

// rewrites the trace in place; returns {level, values} (values = number of replacements)
export function scrubTrace(trace, cfg = scrubLevel(), format) {
  if (cfg.level === 'off') { trace.meta.scrub = { level: 'off', values: 0 }; trace.meta.warnings.push('value scrubbing is off (--no-scrub): names, messages and URLs are unredacted; do not share this page'); return trace.meta.scrub; }
  const counts = {};
  const str = (v) => scrubString(v, cfg, counts);
  if (format === 'gh-actions' && cfg.ciTitles) {
    const root = trace.spans.find((s) => !s.parentId);
    // the run title is the PR or commit title; the branch name can carry ticket ids or customer names
    if (root && root.name !== root.service) { root.name = root.service; counts['ci-title'] = 1; }
    for (const s of trace.spans) if (s.attrs) for (const k of ['ci.branch', 'ci.title', 'ci.head_sha', 'ci.actor']) if (k in s.attrs) { delete s.attrs[k]; counts['ci-meta'] = (counts['ci-meta'] || 0) + 1; }
  }
  for (const s of trace.spans) {
    // CI step stations are named by their own span id (job-<id>-step-<n>), which the page keeps anyway;
    // scrubbing the id out of the name alone would merge every job's steps into one station
    const stepStation = format === 'gh-actions' && s.service === s.spanId && /^job-\d+-step-\d+$/.test(s.service);
    for (const k of ['service', 'name', 'peer', 'operation', 'statusMessage']) if (typeof s[k] === 'string' && !(k === 'service' && stepStation)) s[k] = str(s[k]);
    if (s.attrs) {
      for (const k of Object.keys(s.attrs)) {
        if (cfg.level === 'strict' && !STRICT_ATTRS.test(k)) { delete s.attrs[k]; counts['strict-attr'] = (counts['strict-attr'] || 0) + 1; continue; }
        s.attrs[k] = scrubValue(s.attrs[k], cfg, counts);
      }
    }
    if (s.events) s.events = scrubValue(s.events, cfg, counts);
  }
  if (trace.meta.source) trace.meta.source = str(String(trace.meta.source));
  trace.meta.warnings = trace.meta.warnings.map(str);
  const values = Object.values(counts).reduce((a, b) => a + b, 0);
  trace.meta.scrub = { level: cfg.level, values, kinds: counts };
  return trace.meta.scrub;
}
