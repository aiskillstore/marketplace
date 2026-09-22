import { execFileSync } from 'node:child_process';
import type { ConstraintRule, ReviewedConstraintCatalog, RuleHistory, TrackedRuleHistory } from './constraint-types.mjs';

export function collectRuleHistory(catalog: ReviewedConstraintCatalog, repository: string): ReviewedConstraintCatalog {
  const git = (...args: string[]): string => execFileSync('git', ['--no-optional-locks', '-C', repository, ...args], {
    encoding: 'utf8', windowsHide: true, maxBuffer: 32 * 1024 * 1024,
  }).trimEnd();
  const snapshot = catalog.project.revision;
  if (!/^[a-f0-9]{40}$/.test(snapshot)) throw new Error('History requires a full snapshot commit');
  git('cat-file', '-e', `${snapshot}^{commit}`);
  const shallow = git('rev-parse', '--is-shallow-repository') === 'true';
  const sourceCache = new Map<string, string>();
  const historyCache = new Map<string, TrackedRuleHistory | null>();
  return { ...catalog, rules: catalog.rules.map(rule => {
    const untracked = (reason: string): ConstraintRule => ({ ...rule, history: { status: 'untracked', reason, snapshot } });
    if (shallow) return untracked('shallow-history');
    const source = catalog.sources.find(item => item.path === rule.sourcePath);
    if (!source || !Number.isInteger(rule.line) || !Number.isInteger(rule.endLine)
      || rule.line < 1 || rule.endLine < rule.line || rule.endLine > source.text.split(/\r?\n/).length
      || !/^(?!\/)(?!.*(?:^|\/)\.\.(?:\/|$))[^:\r\n\\]+$/.test(rule.sourcePath)) throw new Error('Invalid rule source range');
    if (!sourceCache.has(rule.sourcePath)) sourceCache.set(rule.sourcePath, git('show', `${snapshot}:${rule.sourcePath}`));
    if (sourceCache.get(rule.sourcePath)!.replace(/\r\n/g, '\n') !== source.text.replace(/\r\n/g, '\n').trimEnd()) throw new Error('Catalog source differs from Git snapshot');
    const key = `${rule.line},${rule.endLine}:${rule.sourcePath}`;
    if (!historyCache.has(key)) {
      try {
        const log = git('log', '--format=RULE_HISTORY|%H|%cI', `-L${key}`, snapshot);
        const commits = [...log.matchAll(/^RULE_HISTORY\|([a-f0-9]{40})\|([^\r\n]+)/gm)].map(([, commit, date]) => ({ commit: commit!, date: date! }));
        historyCache.set(key, commits.length ? { status: 'tracked', method: 'git-line-history', snapshot,
          sourcePath: rule.sourcePath, line: rule.line, endLine: rule.endLine,
          version: commits.length, lastEdited: commits[0]!.date, commits } : null);
      } catch { historyCache.set(key, null); }
    }
    const history = historyCache.get(key);
    return history ? { ...rule, history } : untracked('line-history-unavailable');
  }) };
}

export function validateRuleHistory(history: RuleHistory | undefined, rule: ConstraintRule, snapshot: string): history is TrackedRuleHistory {
  if (!history || history.status === 'untracked') return false;
  if (history.status !== 'tracked' || history.method !== 'git-line-history' || history.snapshot !== snapshot
    || history.sourcePath !== rule.sourcePath || history.line !== rule.line || history.endLine !== rule.endLine
    || !Array.isArray(history.commits) || !Number.isInteger(history.version) || history.version < 1 || history.version !== history.commits.length
    || new Set(history.commits.map(item => item.commit)).size !== history.version
    || history.commits.some(item => !/^[a-f0-9]{40}$/.test(item.commit) || !Number.isFinite(Date.parse(item.date)))
    || history.lastEdited !== history.commits[0]!.date) throw new Error(`Invalid rule history: ${rule.id}`);
  return true;
}
