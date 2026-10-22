// core/gaps.mjs: shorten idle stretches (no non-root span running) so long agent sessions and CI runs
// don't animate as dead air. The time map is monotone, so order and overlaps are kept; only idle time
// between activity is squeezed down to maxGapMs. Not applied to request traces.
export const DEFAULT_MAX_GAP_MS = { agent: 3000, ci: 20000 };
const r3 = (x) => Math.round(x * 1000) / 1000;

export function compressGaps(trace, maxGapMs) {
  if (!(maxGapMs > 0)) return null;
  const spans = trace.spans;
  const root = spans.find((s) => !s.parentId);
  const iv = spans.filter((s) => s !== root).map((s) => [s.start, s.start + s.duration]).sort((a, b) => a[0] - b[0]);
  if (!iv.length) return null;
  const merged = [];
  for (const [a, b] of iv) { const m = merged[merged.length - 1]; if (m && a <= m[1]) m[1] = Math.max(m[1], b); else merged.push([a, b]); }
  const end = Math.max(...spans.map((s) => s.start + s.duration));
  const idle = [];
  let prev = Math.min(0, ...spans.map((s) => s.start));
  for (const [a, b] of merged) { if (a - prev > maxGapMs) idle.push([prev, a]); prev = Math.max(prev, b); }
  if (end - prev > maxGapMs) idle.push([prev, end]);
  if (!idle.length) return null;
  const map = (t) => {
    let cut = 0;
    for (const [a, b] of idle) {
      if (t >= b) { cut += (b - a) - maxGapMs; continue; }
      if (t > a) return r3(a - cut + (t - a) * maxGapMs / (b - a));
      break;
    }
    return r3(t - cut);
  };
  const wall = end;
  for (const s of spans) { const a = map(s.start), b = map(s.start + s.duration); s.start = a; s.duration = r3(b - a); }
  const removedMs = r3(idle.reduce((n, [a, b]) => n + (b - a) - maxGapMs, 0));
  if (root) root.attrs = Object.assign({}, root.attrs, { 'transit.wall_ms': r3(wall), 'transit.idle_gaps_shortened': idle.length });
  return { count: idle.length, maxGapMs, removedMs };
}
