import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { isMainModule } from './main-module.mjs';
import type { ConstraintCatalog, ConstraintSource, SourceSection } from './constraint-types.mjs';

export function discoverConstraints(repository: string, { title, maxSources = 1000 }: { title?: string; maxSources?: number } = {}): ConstraintCatalog {
  if (!Number.isInteger(maxSources) || maxSources < 1) throw new Error('maxSources must be a positive integer');
  const git = (...args: string[]): string => execFileSync('git', ['--no-optional-locks', '-C', repository, ...args], {
    encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, windowsHide: true,
  }).trimEnd();
  const requestedRoot = fs.statSync(repository);
  const gitRoot = fs.statSync(git('rev-parse', '--show-toplevel'));
  if (!requestedRoot.isDirectory() || requestedRoot.dev !== gitRoot.dev || requestedRoot.ino !== gitRoot.ino) {
    throw new Error('Use the Git repository root');
  }
  const revision = git('rev-parse', 'HEAD');
  const shallow = git('rev-parse', '--is-shallow-repository') === 'true';
  const tree = git('ls-tree', '-r', '-z', revision).split('\0').filter(Boolean);
  const modes = new Map<string, string>(tree.map(entry => [entry.slice(entry.indexOf('\t') + 1), entry.slice(0, 6)]));
  const files = [...modes.keys()];
  const tracked = new Set(files);
  const entries = files.filter(file => /(^|\/)(AGENTS|CLAUDE|GEMINI|SKILL)\.md$/.test(file)
    || /^(CONTRIBUTING\.md|\.github\/copilot-instructions\.md|\.cursor\/rules\/.*\.mdc)$/.test(file));
  const excluded = new Map<string, { path: string; reason: string; target?: string }>();
  const exclusion = (file: string): string | null => {
    if (/(^|\/)(fixtures?|__fixtures__|node_modules)(\/|$)/i.test(file) || /(^|\/)snapshots\/.*\/workspace\//.test(file)) return 'fixture-or-dependency';
    if (/(^|\/)(archived?|archive)(\/|$)/i.test(file)) return 'historical';
    if (/\.zh\.md$/.test(file) && tracked.has(file.replace(/\.zh\.md$/, '.md'))) return 'translation-counterpart';
    return null;
  };
  const queue: Array<{ file: string; from: string | null }> = [];
  const seen = new Set<string>();
  const references: ConstraintCatalog['references'] = [];
  const unresolved: ConstraintCatalog['coverage']['unresolved'] = [];
  const enqueue = (file: string, from: string | null = null): void => {
    const reason = exclusion(file);
    if (reason) { excluded.set(file, { path: file, reason }); return; }
    if (!seen.has(file)) { seen.add(file); queue.push({ file, from }); }
  };
  entries.forEach(file => enqueue(file));
  const sources: ConstraintSource[] = [];
  const inspected = new Set<string>();
  for (let index = 0; index < queue.length && sources.length < maxSources; index++) {
    const { file, from } = queue[index]!;
    const text = git('show', `${revision}:${file}`);
    inspected.add(file);
    if (modes.get(file) === '120000') {
      const target = path.posix.normalize(path.posix.join(path.posix.dirname(file), text));
      excluded.set(file, { path: file, reason: 'symlink-alias', target });
      if (!text.startsWith('/') && !target.startsWith('../') && tracked.has(target)) enqueue(target, file);
      else unresolved.push({ from: file, target: text, reason: 'outside-or-missing-alias' });
      continue;
    }
    const lines = text.split(/\r?\n/);
    // Fenced examples and frontmatter stay in source text but never create headings or references.
    let fence = null;
    let frontmatter = lines[0] === '---';
    const headings: Array<{ line: number; level: number; title: string }> = [];
    const prose: string[] = [];
    for (let n = 0; n < lines.length; n++) {
      const line = lines[n];
      if (frontmatter) { if (n > 0 && line === '---') frontmatter = false; continue; }
      const marker = line!.match(/^\s*(`{3,}|~{3,})/);
      if (marker) {
        if (!fence) fence = marker[1]!;
        else if (marker[1]![0] === fence[0] && marker[1]!.length >= fence.length) fence = null;
        continue;
      }
      if (fence) continue;
      const heading = line!.match(/^(#{1,6})\s+(.+?)\s*#*$/);
      if (heading) headings.push({ line: n + 1, level: heading[1]!.length, title: heading[2]! });
      prose.push(line!);
    }
    const visible = prose.join('\n');
    const targets = [
      ...[...visible.matchAll(/\[[^\]\n]*\]\(<?([^\s)>]+)>?(?:\s+"[^"]*")?\)/g)].map(match => match[1]),
      ...[...visible.matchAll(/^\s*\[[^\]]+\]:\s*<?([^\s>]+)/gm)].map(match => match[1]),
      ...[...visible.matchAll(/`([^`\n]+\.(?:md|mdc)(?:#[^`\s]+)?)`/g)].map(match => match[1]),
    ];
    for (const target of new Set(targets.filter((value): value is string => value !== undefined))) {
      if (/^[a-z][a-z\d+.-]*:/i.test(target) || target.startsWith('#')) continue;
      let decoded;
      try { decoded = decodeURIComponent(target.split('#')[0]!); } catch { unresolved.push({ from: file, target, reason: 'invalid-url' }); continue; }
      if (!/\.(md|mdc)$/.test(decoded)) continue;
      let resolved = path.posix.normalize(path.posix.join(path.posix.dirname(file), decoded));
      if (!tracked.has(resolved) && tracked.has(decoded)) resolved = decoded;
      if (decoded.startsWith('/') || resolved.startsWith('../') || !tracked.has(resolved)) {
        unresolved.push({ from: file, target, reason: 'outside-or-missing' }); continue;
      }
      references.push({ from: file, to: resolved, target });
      enqueue(resolved, file);
    }
    const kind = /(^|\/)SKILL\.md$/.test(file) ? 'skill' : entries.includes(file) ? 'instruction' : 'reference';
    const id = 'source-' + createHash('sha256').update(file).digest('hex').slice(0, 16);
    const sections: SourceSection[] = headings.map((heading, index) => {
      const endLine = (headings[index + 1]?.line || lines.length + 1) - 1;
      return { id: `${id}-s${index + 1}`, title: heading.title, level: heading.level,
        line: heading.line, endLine, text: lines.slice(heading.line - 1, endLine).join('\n') };
    });
    if (!sections.length) sections.push({ id: `${id}-s1`, title: path.posix.basename(file), level: 1, line: 1, endLine: lines.length, text });
    sources.push({ id, path: file, kind, scope: kind === 'instruction' ? path.posix.dirname(file) : null,
      discoveredFrom: from, applicability: 'unreviewed', text, sections,
      history: { complete: !shallow, version: shallow ? null : 0, lastEdited: null, commit: null } });
  }
  // Walk history once; per-source --follow traversals are prohibitively slow on large repositories.
  // Counts describe each current path, explicitly excluding rename ancestry.
  const byPath = new Map(sources.map(source => [source.path, source]));
  const history = git('log', '--no-renames', '--format=%x1e%H|%cI', '--name-only', '-z', revision, '--', '*.md', '*.mdc');
  for (const entry of history.split('\x1e').filter(Boolean)) {
    const [header, ...changed] = entry.split(/\0|\r?\n/).filter(Boolean);
    const [commit, date] = header!.split('|');
    for (const file of new Set(changed)) {
      const source = byPath.get(file);
      if (!source) continue;
      if (!shallow) source.history.version = (source.history.version ?? 0) + 1;
      if (!source.history.commit) Object.assign(source.history, { commit: commit!, lastEdited: date! });
    }
  }
  const checked = new Set(sources.map(source => source.path));
  return { schema: 'birdview.constraint-catalog/v1', project: { name: title || path.basename(path.resolve(repository)), revision },
    coverage: { checkedAt: new Date().toISOString(), snapshot: 'committed-HEAD', shallow,
      entries, checkedPaths: [...checked], excluded: [...excluded.values()], unresolved,
      uninspectedPaths: queue.filter(item => !inspected.has(item.file)).map(item => item.file),
      semanticReview: 'pending', limitations: ['Only tracked entry files and their local Markdown references are collected.',
        'Uncommitted files, external references, implicit contracts and host/user instructions need separate inspection.',
        'Sections are source material, not automatically effective or verified rules.',
        'History counts use current file paths; rename ancestry is not followed.'] }, references, sources };
}

if (isMainModule(import.meta.url)) {
  const [repository, output, title] = process.argv.slice(2);
  if (!repository || !output) throw new Error('Usage: node scripts/discover-constraints.mjs repository catalog.json [project-name]');
  const catalog = discoverConstraints(repository, title ? { title } : {});
  fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });
  fs.writeFileSync(output, JSON.stringify(catalog, null, 2) + '\n');
  console.log(JSON.stringify({ sources: catalog.sources.length, sections: catalog.sources.reduce((n, source) => n + source.sections.length, 0),
    excluded: catalog.coverage.excluded.length, unresolved: catalog.coverage.unresolved.length, uninspected: catalog.coverage.uninspectedPaths.length }));
}
