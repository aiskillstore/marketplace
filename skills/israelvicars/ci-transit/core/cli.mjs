// core/cli.mjs: argument parsing and error reporting shared by the entry scripts.
// Flags that never take a value; every other --flag takes the next argument.
export const BOOL_FLAGS = new Set(['strict', 'share', 'keep-uuids', 'keep-ci-titles']);
// flags that take a value only when one follows (--contracts [index.json], --show-args)
const OPTIONAL_VALUE = new Set(['contracts', 'show-args']);

export function parseArgs(argv) {
  const opt = {}, pos = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) { pos.push(a); continue; }
    const eq = a.indexOf('=');
    if (eq > 2) { opt[a.slice(2, eq)] = a.slice(eq + 1); continue; }
    const k = a.slice(2), next = argv[i + 1];
    if (k.startsWith('no-') || BOOL_FLAGS.has(k)) opt[k] = true;
    else if (OPTIONAL_VALUE.has(k) && (next == null || next.startsWith('--'))) opt[k] = true;
    else if (next == null) throw new UserError(`--${k} needs a value`);
    else opt[k] = argv[++i];
  }
  return { opt, pos };
}
// back to argv form (for passing build options on to a child script)
export const toArgs = (opt, skip = []) => Object.entries(opt).flatMap(([k, v]) => skip.includes(k) ? [] : v === true ? ['--' + k] : ['--' + k, String(v)]);

// An error whose message is the whole story for the user: printed without a stack trace.
export class UserError extends Error {}

// Runs an async CLI body; any error prints as one "transit: ..." line (stack only with TRANSIT_DEBUG=1).
export async function runCli(fn) {
  try { await fn(); }
  catch (e) {
    console.error(`transit: ${e && e.message ? e.message : e}`);
    if (process.env.TRANSIT_DEBUG === '1' && e && e.stack) console.error(e.stack);
    else if (!(e instanceof UserError)) console.error('  (set TRANSIT_DEBUG=1 for a stack trace)');
    process.exit(1);
  }
}
