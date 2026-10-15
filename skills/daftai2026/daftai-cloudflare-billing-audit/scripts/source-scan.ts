/**
 * [INPUT]: 依赖 候选契约与官方来源常量
 * [OUTPUT]: 提供 词法遮罩及带未知触发链的候选扫描
 * [POS]: 源码线索层；不构建调用图或确认风险
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import type { CandidateFinding } from './audit-types.ts';
import { DOCS } from './audit-types.ts';
function lineAt(source: string, offset: number): number {
  let line = 1;
  for (let i = 0; i < offset; i++) if (source.charCodeAt(i) === 10) line++;
  return line;
}

export function maskJavaScript(source: string): string {
  const chars = source.split('');
  const blank = (index: number): void => { if (chars[index] !== '\n' && chars[index] !== '\r') chars[index] = ' '; };
  let state: 'code' | 'single' | 'double' | 'template' | 'line-comment' | 'block-comment' | 'regex' = 'code';
  let escaped = false;
  let previousWord = '';
  let currentWord = '';
  let previousPunctuation = '';
  let inRegexClass = false;
  for (let i = 0; i < chars.length; i++) {
    const ch = chars[i]!;
    const next = chars[i + 1];
    if (state === 'single' || state === 'double' || state === 'template' || state === 'regex') {
      blank(i);
      if (escaped) { escaped = false; continue; }
      if (ch === '\\') { escaped = true; continue; }
      if (state === 'regex' && ch === '[') inRegexClass = true;
      else if (state === 'regex' && ch === ']') inRegexClass = false;
      if ((state === 'single' && ch === "'") || (state === 'double' && ch === '"') || (state === 'template' && ch === '`') || (state === 'regex' && ch === '/' && !inRegexClass)) {
        state = 'code'; previousWord = '__value'; previousPunctuation = '';
      }
      continue;
    }
    if (state === 'line-comment') {
      if (ch === '\n' || ch === '\r') state = 'code'; else blank(i);
      continue;
    }
    if (state === 'block-comment') {
      if (ch === '*' && next === '/') { blank(i); blank(i + 1); i++; state = 'code'; }
      else blank(i);
      continue;
    }
    if (ch === '/' && next === '/') { blank(i); blank(i + 1); i++; state = 'line-comment'; continue; }
    if (ch === '/' && next === '*') { blank(i); blank(i + 1); i++; state = 'block-comment'; continue; }
    if (ch === "'" || ch === '"' || ch === '`') {
      if (currentWord) { previousWord = currentWord; currentWord = ''; }
      previousWord = '__value'; previousPunctuation = '';
      blank(i); state = ch === "'" ? 'single' : ch === '"' ? 'double' : 'template'; escaped = false; continue;
    }
    if (/[A-Za-z0-9_$]/.test(ch)) { currentWord += ch; continue; }
    if (/\s/.test(ch)) {
      if (currentWord) { previousWord = currentWord; currentWord = ''; previousPunctuation = ''; }
      continue;
    }
    if (currentWord) { previousWord = currentWord; currentWord = ''; previousPunctuation = ''; }
    if (ch === '/' && next !== '/' && next !== '*') {
      const regexBefore = '([{=:;,!?&|+*%~^<>-)]'.includes(previousPunctuation) ||
        ['return', 'case', 'throw', 'delete', 'void', 'typeof', 'instanceof', 'in', 'of', 'yield', 'await'].includes(previousWord);
      if (regexBefore) { blank(i); state = 'regex'; escaped = false; inRegexClass = false; previousWord = ''; previousPunctuation = ''; continue; }
    }
    previousPunctuation = ch;
  }
  return chars.join('');
}

function delimiterPairs(masked: string): { pairs: Map<number, number>; malformed: boolean } {
  const pairs = new Map<number, number>();
  const stack: Array<{ char: '(' | '[' | '{'; index: number }> = [];
  const closes: Record<string, '(' | '[' | '{'> = { ')': '(', ']': '[', '}': '{' };
  let malformed = false;
  for (let i = 0; i < masked.length; i++) {
    const ch = masked[i]!;
    if (ch === '(' || ch === '[' || ch === '{') stack.push({ char: ch, index: i });
    else if (ch === ')' || ch === ']' || ch === '}') {
      const top = stack.at(-1);
      if (!top || top.char !== closes[ch]) { malformed = true; continue; }
      stack.pop(); pairs.set(top.index, i); pairs.set(i, top.index);
    }
  }
  if (stack.length) malformed = true;
  return { pairs, malformed };
}

function methodBodies(masked: string, method: string, pairs: Map<number, number>): Array<{ start: number; end: number }> {
  const bodies: Array<{ start: number; end: number }> = [];
  const matcher = new RegExp(`\\b(?:async\\s+)?${method}\\s*\\(`, 'g');
  for (const match of masked.matchAll(matcher)) {
    const paren = match.index! + match[0].lastIndexOf('(');
    const closeParen = pairs.get(paren);
    if (closeParen === undefined) continue;
    let open = closeParen + 1;
    while (/\s/.test(masked[open] ?? '')) open++;
    if (masked[open] === ':') {
      const annotation = /^:\s*(?:Promise\s*<[^{};>\n]+>|(?:void|never|unknown|any|[A-Za-z_$][\w$]*)(?:\s*<[^{};>\n]+>)?)\s*/.exec(masked.slice(open));
      if (!annotation) continue;
      open += annotation[0].length;
      while (/\s/.test(masked[open] ?? '')) open++;
    }
    if (masked[open] !== '{') continue;
    const close = pairs.get(open);
    if (close !== undefined) bodies.push({ start: open + 1, end: close });
  }
  const arrowMatcher = new RegExp(`\\b${method}\\s*[:=]\\s*(?:async\\s*)?\\(`, 'g');
  for (const match of masked.matchAll(arrowMatcher)) {
    const paren = match.index! + match[0].lastIndexOf('(');
    const closeParen = pairs.get(paren);
    if (closeParen === undefined) continue;
    let arrow = closeParen + 1;
    while (/\s/.test(masked[arrow] ?? '')) arrow++;
    if (masked[arrow] === ':') {
      const annotation = /^:\s*(?:Promise\s*<[^{};>\n]+>|(?:void|never|unknown|any|[A-Za-z_$][\w$]*)(?:\s*<[^{};>\n]+>)?)\s*/.exec(masked.slice(arrow));
      if (!annotation) continue;
      arrow += annotation[0].length;
      while (/\s/.test(masked[arrow] ?? '')) arrow++;
    }
    if (masked.slice(arrow, arrow + 2) !== '=>') continue;
    let open = arrow + 2;
    while (/\s/.test(masked[open] ?? '')) open++;
    if (masked[open] !== '{') continue;
    const close = pairs.get(open);
    if (close !== undefined) bodies.push({ start: open + 1, end: close });
  }
  return bodies;
}

function loopBodies(masked: string, pairs: Map<number, number>): Array<{ start: number; end: number }> {
  const bodies: Array<{ start: number; end: number }> = [];
  const matcher = /\b(?:for|while)\s*\(/g;
  for (const match of masked.matchAll(matcher)) {
    const parenStart = match.index! + match[0].lastIndexOf('(');
    const closeParen = pairs.get(parenStart);
    if (closeParen === undefined) continue;
    let bodyStart = closeParen + 1;
    while (/\s/.test(masked[bodyStart] ?? '')) bodyStart++;
    if (masked[bodyStart] === '{') {
      const close = pairs.get(bodyStart);
      if (close !== undefined) bodies.push({ start: bodyStart + 1, end: close });
    } else if (bodyStart < masked.length) {
      let parens = 0;
      let brackets = 0;
      let braces = 0;
      let end = bodyStart;
      for (; end < masked.length; end++) {
        const ch = masked[end]!;
        if (ch === '(') parens++;
        else if (ch === ')') { if (parens === 0) break; parens--; }
        else if (ch === '[') brackets++;
        else if (ch === ']') brackets--;
        else if (ch === '{') braces++;
        else if (ch === '}') { if (braces === 0) break; braces--; }
        else if (ch === ';' && parens === 0 && brackets === 0 && braces === 0) { end++; break; }
        else if ((ch === '\n' || ch === '\r') && parens === 0 && brackets === 0 && braces === 0) break;
      }
      if (end > bodyStart) bodies.push({ start: bodyStart, end });
    }
  }
  const doMatcher = /\bdo\s*\{/g;
  for (const match of masked.matchAll(doMatcher)) {
    const open = match.index! + match[0].lastIndexOf('{');
    const close = pairs.get(open);
    if (close !== undefined) bodies.push({ start: open + 1, end: close });
  }
  return bodies;
}

export type SourceScanResult = { findings: CandidateFinding[]; truncated: boolean; unsupported: string[] };

function lineLookup(source: string): (offset: number) => number {
  const starts = [0];
  for (let i = 0; i < source.length; i++) if (source.charCodeAt(i) === 10) starts.push(i + 1);
  return (offset: number): number => {
    let low = 0;
    let high = starts.length;
    while (low + 1 < high) {
      const middle = (low + high) >>> 1;
      if (starts[middle]! <= offset) low = middle; else high = middle;
    }
    return low + 1;
  };
}

function hasLikelyJsx(source: string, file: string): boolean {
  if (/\.(?:jsx|tsx)$/i.test(file)) return true;
  const masked = maskJavaScript(source);
  return /(?<![A-Za-z0-9_$])<\/?[A-Za-z][\w.:-]*(?:\s|\/?>)/.test(masked);
}

export function scanSource(source: string, file: string, configuredMainPaths: Set<string> = new Set(), maxFindings = 200): SourceScanResult {
  const unsupported: string[] = [];
  if (hasLikelyJsx(source, file)) return { findings: [], truncated: false, unsupported: ['jsx-or-tsx'] };
  if (source.includes('`')) unsupported.push('template-interpolation-not-analyzed');
  if (/\)\s*\/\s*\S/.test(source)) unsupported.push('ambiguous-regex-or-division');
  const masked = maskJavaScript(source);
  if (masked.includes('/')) unsupported.push('ambiguous-regex-or-division');
  const loopCount = (masked.match(/\b(?:for|while|do)\b/g) ?? []).length;
  const handlerCount = (masked.match(/\b(?:alarm|queue)\b/g) ?? []).length;
  // Bounds repeated overlapping scans in nested loops/handlers. Files remain safe-read evidence for manual review.
  if (loopCount * masked.length + handlerCount * masked.length > 8 * 1024 * 1024) {
    return { findings: [], truncated: false, unsupported: [...new Set([...unsupported, 'source-work-budget-exceeded'])] };
  }
  const { pairs, malformed } = delimiterPairs(masked);
  if (malformed) unsupported.push('unbalanced-or-unsupported-delimiters');
  const findings: CandidateFinding[] = [];
  const keys = new Set<string>();
  let truncated = false;
  const getLine = lineLookup(masked);
  const record = (finding: CandidateFinding): void => {
    const key = `${finding.ruleId}\0${finding.file}\0${finding.line}`;
    if (keys.has(key)) return;
    if (findings.length >= maxFindings) { truncated = true; return; }
    keys.add(key); findings.push(finding);
  };
  const alarmBodies = methodBodies(masked, 'alarm', pairs);
  if (/\b(?:async\s+)?alarm\s*\(/.test(masked) && alarmBodies.length === 0) unsupported.push('alarm-handler-syntax-not-recognized');
  if (/\balarm\s*[:=]\s*/.test(masked) && methodBodies(masked, 'alarm', pairs).length === 0) unsupported.push('alarm-arrow-syntax-not-recognized');
  for (const body of alarmBodies) {
    const calls = /\b(?:[A-Za-z_$][\w$]*\s*\.\s*)?setAlarm\s*\(/g;
    for (const match of masked.slice(body.start, body.end).matchAll(calls)) {
      if (truncated) break;
      const offset = body.start + match.index!;
      record({
        ruleId: 'CFBA-DO-ALARM-SELF-REARM-CANDIDATE', matchesRuleId: 'CF-DO-ALARM-LOOP', product: 'Durable Objects', file, line: getLine(offset),
        triggerChain: 'unknown', evidence: 'setAlarm token is lexically inside a method named alarm; no reachability or control-flow proof',
        condition: 'Only material if this is a deployed Durable Object alarm handler that re-schedules itself without an effective stop/guard.',
        possibleConsequence: 'Repeated alarm wakeups may add Worker runtime and Durable Object storage operations; actual billing impact depends on plan, frequency, and guards.',
        recommendation: 'Trace the exported Durable Object class, alarm schedule, and stop conditions; verify recurrence is intentional and bounded.', sources: [DOCS.alarms],
      });
    }
    if (truncated) break;
  }

  const queueBodies = methodBodies(masked, 'queue', pairs);
  if (/\b(?:async\s+)?queue\s*\(/.test(masked) && queueBodies.length === 0) unsupported.push('queue-handler-syntax-not-recognized');
  if (/\bqueue\s*[:=]\s*/.test(masked) && methodBodies(masked, 'queue', pairs).length === 0) unsupported.push('queue-arrow-syntax-not-recognized');
  for (const body of queueBodies) {
    const bodyText = masked.slice(body.start, body.end);
    for (const match of bodyText.matchAll(/\b(?:[A-Za-z_$][\w$]*\s*\.\s*)?retry\s*\(/g)) {
      if (truncated) break;
      const offset = body.start + match.index!;
      record({
        ruleId: 'CFBA-QUEUE-RETRY-CANDIDATE', matchesRuleId: 'CF-QUEUES-RETRY-FANOUT', product: 'Cloudflare Queues', file, line: getLine(offset), triggerChain: 'unknown',
        evidence: 'retry token is lexically inside a method named queue; target message and call reachability are not resolved',
        condition: 'Only material if this method is a deployed queue consumer and retries recur or handle failing messages.',
        possibleConsequence: 'Repeated deliveries can consume queue operations and consumer Worker runtime; retry intent and limits are unknown.',
        recommendation: 'Trace the consumer binding and retry branch; check retry delays, maximum attempts, and dead-letter behavior.', sources: [DOCS.queueApi, DOCS.queues],
      });
    }
    if (truncated) break;
    for (const match of bodyText.matchAll(/\b(?:[A-Za-z_$][\w$]*\s*\.\s*)?(?:send|sendBatch)\s*\(/g)) {
      if (truncated) break;
      const offset = body.start + match.index!;
      record({
        ruleId: 'CFBA-QUEUE-CONSUMER-SEND-CANDIDATE', matchesRuleId: 'CF-QUEUES-SELF-REENQUEUE-LOOP', product: 'Cloudflare Queues', file, line: getLine(offset), triggerChain: 'unknown',
        evidence: 'send token is lexically inside a method named queue; destination and message-flow relation are unknown',
        condition: 'Only material if this is a deployed consumer and it sends work back into the same queue or a repeating queue cycle.',
        possibleConsequence: 'A queue feedback cycle may multiply deliveries, sends, and Worker runtime; this scan cannot establish a cycle.',
        recommendation: 'Trace producer destinations and message-derived routing end to end; add idempotency, cycle guards, and bounded retries where needed.', sources: [DOCS.queueApi, DOCS.queues],
      });
    }
    if (truncated) break;
  }

  const loops = loopBodies(masked, pairs);
  for (const body of loops) {
    for (const match of masked.slice(body.start, body.end).matchAll(/\b(?:[A-Za-z_$][\w$]*\s*\.\s*)?(?:send|sendBatch|setAlarm)\s*\(/g)) {
      if (truncated) break;
      const offset = body.start + match.index!;
      const token = /setAlarm/.test(match[0]) ? 'setAlarm' : 'queue send';
      const isAlarm = token === 'setAlarm';
      record({
        ruleId: isAlarm ? 'CFBA-DO-LOOP-ALARM-CANDIDATE' : 'CFBA-QUEUE-LOOP-SEND-CANDIDATE',
        matchesRuleId: isAlarm ? 'CF-DO-ALARM-LOOP' : 'CF-QUEUES-SELF-REENQUEUE-LOOP',
        product: isAlarm ? 'Durable Objects' : 'Cloudflare Queues', file, line: getLine(offset), triggerChain: 'unknown',
        evidence: `${token} token is lexically inside a loop block; alias, guard, target, and invocation flow are unresolved`,
        condition: isAlarm ? 'Only material if repeated loop iterations schedule billable Durable Object alarms.' : 'Only material if each iteration sends a message to a billable queue and the loop is reachable with material iteration counts.',
        possibleConsequence: isAlarm ? 'Repeated scheduling may create avoidable alarm/storage activity; billing impact is unverified.' : 'Looped sends may increase queue operations and downstream Worker invocations; billing impact is unverified.',
        recommendation: isAlarm ? 'Inspect loop bounds and alarm scheduling intent; avoid duplicate or unbounded scheduling.' : 'Inspect loop bounds, batch APIs, and downstream consumer flow; batch or cap sends when appropriate.',
        sources: isAlarm ? [DOCS.alarms] : [DOCS.queueApi, DOCS.queues],
      });
    }
    if (truncated) break;
  }
  return { findings: findings.map((finding) => ({ ...finding, evidence: configuredMainPaths.has(file) ? `${finding.evidence}; file is a configured main path, but call reachability remains unknown` : finding.evidence })), truncated, unsupported };
}
