/**
 * [INPUT]: 依赖 文件适配器、发现、配置解析和词法候选模块
 * [OUTPUT]: 提供 auditProject 与 readReviewEvidenceFile
 * [POS]: 审计编排层；统一额度、外置报告和证据复核
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import type { AuditReport, AuditOptions, ReviewEvidenceFile, UnknownItem, ConfigInventory, CandidateFinding } from './audit-types.ts';
import { DEFAULT_LIMITS, SOURCE_EXTENSIONS, MAX_INVENTORY_BYTES } from './audit-types.ts';
import { isWithin, object, isObject, statFingerprint } from './fs-common.ts';
import { openAuditFs, resolveAuditPath } from './audit-fs.ts';
import type { AuditFs } from './audit-fs.ts';
import { isSensitivePath, discoverProject, readBounded } from './discovery.ts';
import type { Candidate } from './discovery.ts';
import { parseConfig, parseJsoncStrict, parseWranglerEnvironments, hasD1Declaration, validAuxiliaryConfig, migrationDirectories } from './config.ts';
import { scanSource } from './source-scan.ts';
const skillDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
function createOutputDirectory(base: AuditFs, now: Date): { tree: AuditFs; path: string } {
  const stamp = now.toISOString().replace(/[:.]/g, '-');
  const prefix = `cloudflare-billing-audit-${stamp}`;
  for (let suffix = 0; suffix < 1000; suffix++) {
    const name = suffix === 0 ? prefix : `${prefix}-${suffix + 1}`;
    try { return { tree: base.createChildDirectory(name), path: path.join(base.rootPath, name) }; }
    catch (error) { if (error instanceof Error && error.message === 'output-collision') continue; throw new Error('cannot-create-audit-output'); }
  }
  throw new Error('cannot-create-unique-audit-output');
}

function markdownSafe(value: string): string {
  return value.replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\\/g, '\\\\').replace(/([`*_{}\[\]()#+.!|<>])/g, '\\$1');
}

function workspacePatternsFromPackage(raw: unknown): string[] | undefined {
  const packageJson = object(raw);
  if (!packageJson || packageJson.workspaces === undefined) return undefined;
  const workspaces = Array.isArray(packageJson.workspaces) ? packageJson.workspaces : object(packageJson.workspaces)?.packages;
  if (!Array.isArray(workspaces)) return [];
  return workspaces.filter((item): item is string => typeof item === 'string').map((pattern) => /^[A-Za-z0-9_./*{}!@+-]{1,120}$/.test(pattern) ? pattern : '[redacted-pattern]');
}

function renderMarkdown(report: AuditReport): string {
  const out: string[] = [
    '# Cloudflare billing audit inventory', '',
    `- Project: ${markdownSafe(report.projectLabel)}`, `- Generated: ${markdownSafe(report.generatedAt)}`, `- Status: ${report.status}`, '',
    `- Runtime platform: ${markdownSafe(report.runtimePlatform)}`, `- Secure read mode: ${report.secureReadMode}`, `- Project-root fingerprint: ${report.projectRootFingerprint}`, '',
    'This is a bounded, offline inventory and candidate scan. A missing finding is not evidence of safety or zero billing risk.', '',
    '## Coverage', ...report.coverage.map((item) => `- ${item}`), '',
    '## Workspaces and Wrangler configs',
  ];
  if (!report.configs.length) out.push('- No Wrangler config was found within the scan limits. Deployment configuration and billing exposure are unknown.');
  for (const config of report.configs) {
    out.push(`- ${markdownSafe(config.path)} (workspace ${markdownSafe(config.workspace)}; ${config.format}; parser ${config.parserStatus})`);
    for (const env of config.environments) {
      out.push(`  - ${markdownSafe(env.name)}: main ${env.main.status}${env.main.path ? ` (${markdownSafe(env.main.path)})` : ''}; vars count ${env.varsCount}; declared bindings ${env.bindings.length}; crons ${env.triggers.cronCount}; routes ${env.routeCount}; cpu_ms ${env.limits.cpuMs ?? 'unknown'}`);
      for (const binding of env.bindings) out.push(`    - ${binding.product}: ${markdownSafe(binding.binding)} (${binding.type}${binding.role ? `, ${binding.role}` : ''})`);
    }
  }
  if (report.packageWorkspaces.length) {
    out.push('', '## Package workspace metadata');
    for (const workspace of report.packageWorkspaces) out.push(`- ${markdownSafe(workspace.manifest)}: ${workspace.patternCount} workspace pattern(s)${workspace.patterns.length ? ` (${workspace.patterns.map(markdownSafe).join(', ')})` : ''}`);
  }
  if (report.scannedSourceFiles.length) {
    out.push('', '## Scanned source paths');
    for (const file of report.scannedSourceFiles) out.push(`- ${markdownSafe(file)}`);
  }
  if (report.readSourceFiles.some((file) => !report.scannedSourceFiles.includes(file))) {
    out.push('', '## Read source paths with unsupported lexical syntax');
    for (const file of report.readSourceFiles.filter((item) => !report.scannedSourceFiles.includes(item))) out.push(`- ${markdownSafe(file)}`);
  }
  out.push('', '## Auxiliary review evidence');
  if (!report.readAuxiliaryFiles.length) out.push('- No selected D1 migration SQL or Workers workflow YAML was read.');
  for (const file of report.reviewEvidenceFiles.filter((item) => item.kind !== 'source-js-ts')) {
    out.push(`- ${markdownSafe(file.path)} (${file.kind}; ${file.bytes} bytes; SHA-256 fingerprint recorded in JSON)`);
  }
  out.push(`- Review evidence files: ${report.reviewEvidenceFiles.length}; safe-read source files: ${report.readSourceFiles.length}; auxiliary files: ${report.readAuxiliaryFiles.length}.`);
  out.push('', '## Candidate signals');
  if (!report.findings.length) out.push('- No supported lexical candidate signal was found in the scanned source subset. This is not a safety proof.');
  for (const f of report.findings) {
    out.push(`- ${f.ruleId} (${f.matchesRuleId}) — ${f.product} — ${markdownSafe(f.file)}:${f.line}`);
    out.push(`  - Trigger chain: unknown. ${f.evidence}.`);
    out.push(`  - Condition: ${f.condition}`);
    out.push(`  - Possible consequence: ${f.possibleConsequence}`);
    out.push(`  - Suggested check: ${f.recommendation}`);
    out.push(`  - Sources: ${f.sources.join(', ')}`);
  }
  out.push('', '## Unknowns and limits');
  if (!report.unknowns.length) out.push('- Static coverage remains incomplete: imports, aliases, dynamic dispatch, framework-generated wiring, external triggers, and runtime behavior are not resolved.');
  for (const item of report.unknowns) out.push(`- ${item.code}: ${markdownSafe(item.detail)}${item.count !== undefined ? ` (count ${item.count})` : ''}`);
  out.push(`- Scanned source files: ${report.sourceFilesScanned}; skipped symlinks: ${report.skipped.symlinks}; excluded paths: ${report.skipped.excludedPaths}; non-regular files: ${report.skipped.nonRegularFiles}; unreadable/oversize: ${report.skipped.unreadableOrOversize}.`);
  out.push(`- Limits: depth ${report.limits.maxDepth}, entries ${report.limits.maxEntries}, candidate files ${report.limits.maxFiles}, total bytes ${report.limits.maxTotalBytes}, per file ${report.limits.maxFileBytes}, candidates ${report.limits.maxCandidates}.`);
  out.push('', '## Binding inventory', 'Binding declarations are not findings by themselves. Values, resource IDs, secret values, config vars, and source snippets are omitted.');
  out.push('');
  return out.join('\n');
}

function normalizedLimits(input?: Partial<AuditReport['limits']>): AuditReport['limits'] {
  const result = { ...DEFAULT_LIMITS };
  if (!input) return result;
  for (const key of Object.keys(DEFAULT_LIMITS) as Array<keyof AuditReport['limits']>) {
    const value = input[key];
    if (typeof value === 'number' && Number.isSafeInteger(value) && value >= 0) result[key] = Math.min(DEFAULT_LIMITS[key], value);
  }
  return result;
}

function reportError(unknowns: UnknownItem[], code: string, detail: string, count?: number): void {
  if (unknowns.some((item) => item.code === code && item.detail === detail)) return;
  unknowns.push({ code, detail, ...(count === undefined ? {} : { count }) });
}

function readCandidate(tree: AuditFs, candidate: Candidate, limits: AuditReport['limits'], totalBytes: number): ReturnType<typeof readBounded> {
  return readBounded(tree, candidate, limits.maxFileBytes, Math.max(0, limits.maxTotalBytes - totalBytes));
}

function auditOnTree(tree: AuditFs, projectPath: string, options: AuditOptions = {}): AuditReport {
  const limits = normalizedLimits(options.limits);
  const now = options.now ?? new Date();
  const discovery = discoverProject(tree, limits);
  const unknowns: UnknownItem[] = [];
  const evidence: ReviewEvidenceFile[] = [];
  for (const code of discovery.limitsHit) reportError(unknowns, `scan-limit-${code}`, `The ${code} limit was reached; files outside the observed subset are unknown.`);
  if (discovery.symlinks) reportError(unknowns, 'symlink-content-not-followed', 'Symlink paths and their targets were intentionally not read; any project content reachable only through them is unknown.', discovery.symlinks);
  if (discovery.nonRegularFiles) reportError(unknowns, 'nonregular-content-not-read', 'FIFO, socket, device, and other non-regular paths were not opened.', discovery.nonRegularFiles);
  if (discovery.unreadableDirectories) reportError(unknowns, 'directory-not-read', 'One or more directories could not be safely enumerated; their contents are unknown.', discovery.unreadableDirectories);
  if (discovery.changedEntries) reportError(unknowns, 'entry-changed-during-discovery', 'One or more entries disappeared or changed type during bounded discovery; that content is unknown.', discovery.changedEntries);

  const configs: ConfigInventory[] = [];
  const packageWorkspaces: AuditReport['packageWorkspaces'] = [];
  const configRaw: Array<{ candidate: Candidate; raw: unknown; valid: boolean }> = [];
  const configCandidates = discovery.candidates.filter((candidate) => candidate.kind === 'config');
  const packageCandidates = discovery.candidates.filter((candidate) => candidate.kind === 'metadata');
  let totalBytes = 0;
  let filesRead = 0;
  let unreadableOrOversize = 0;
  const limitFiles = (remaining: number): boolean => {
    if (filesRead < limits.maxFiles) { filesRead++; return true; }
    reportError(unknowns, 'scan-limit-max-files', 'The maximum inspected file count was reached; files outside the inspected subset are unknown.', remaining);
    return false;
  };
  const readStatusUnknown = (candidate: Candidate, what: string, error?: string): void => {
    unreadableOrOversize++;
    const detail = `${candidate.relative} could not be safely read${error === 'file-too-large' || error === 'total-byte-limit' ? ' within configured byte limits' : ''}; ${what} is unknown.`;
    const code = what === 'configuration' ? 'config-not-read' : what === 'workspace metadata' ? 'workspace-metadata-not-read' : what === 'source signals' ? 'source-not-scanned' : 'review-evidence-not-read';
    reportError(unknowns, code, detail);
  };

  for (let i = 0; i < configCandidates.length; i++) {
    const candidate = configCandidates[i]!;
    if (!limitFiles(configCandidates.length - i + packageCandidates.length)) break;
    const format = path.extname(candidate.relative).toLowerCase() === '.toml' ? 'toml' : path.extname(candidate.relative).toLowerCase() === '.jsonc' ? 'jsonc' : 'json';
    const read = readCandidate(tree, candidate, limits, totalBytes);
    if (read.text === undefined) { readStatusUnknown(candidate, 'configuration', read.error); continue; }
    totalBytes += read.bytes ?? 0;
    const parsed = parseConfig(format, read.text);
    const config = parseWranglerEnvironments(tree, candidate, parsed.value, format, parsed.status, unknowns);
    configs.push(config);
    const auxiliaryValid = validAuxiliaryConfig(candidate.relative, parsed.value) && (parsed.status === 'supported-jsonc' || parsed.status === 'supported-bun-toml');
    configRaw.push({ candidate, raw: parsed.value, valid: auxiliaryValid });
    if (isObject(parsed.value) && (parsed.status === 'supported-jsonc' || parsed.status === 'supported-bun-toml') && !auxiliaryValid)
      reportError(unknowns, 'config-shape-unsupported-for-auxiliary-review', `Known config shapes in ${candidate.relative} are incomplete or unsafe; auxiliary review was not authorized from this config.`);
    if (parsed.status !== 'supported-jsonc' && parsed.status !== 'supported-bun-toml') reportError(unknowns, `config-${parsed.status}`, `${candidate.relative} was not fully parsed; declared billing bindings and environments are unknown.`);
    if (format === 'toml' && parsed.status === 'unsupported-no-bun-toml-parser') reportError(unknowns, 'toml-coverage-unsupported', `${candidate.relative} was not parsed because Bun.TOML.parse is unavailable; no TOML coverage is claimed.`);
  }
  for (let i = 0; i < packageCandidates.length; i++) {
    const candidate = packageCandidates[i]!;
    if (!limitFiles(packageCandidates.length - i)) break;
    const read = readCandidate(tree, candidate, limits, totalBytes);
    if (read.text === undefined) { readStatusUnknown(candidate, 'workspace metadata', read.error); continue; }
    totalBytes += read.bytes ?? 0;
    try {
      const patterns = workspacePatternsFromPackage(parseJsoncStrict(read.text));
      if (patterns !== undefined) packageWorkspaces.push({ manifest: candidate.relative, patternCount: patterns.length, patterns });
    } catch { reportError(unknowns, 'workspace-metadata-invalid', `${candidate.relative} could not be parsed for workspace metadata; package scripts were not inspected.`); }
  }
  if (!configCandidates.length) reportError(unknowns, 'no-wrangler-config', 'No supported Wrangler config was found within the bounded inventory; deployment bindings and entry points are unknown.');

  const mainPaths = new Set<string>();
  for (const config of configs) for (const env of config.environments) if (env.main.status === 'exists' && env.main.path) mainPaths.add(env.main.path);
  const sourceCandidates = discovery.candidates.filter((candidate) => candidate.kind === 'source');
  sourceCandidates.sort((a, b) => Number(mainPaths.has(b.relative)) - Number(mainPaths.has(a.relative)) || a.relative.localeCompare(b.relative));
  const sourceFiles: string[] = [];
  const scannedSourceFiles: string[] = [];
  const findings: CandidateFinding[] = [];
  let sourceFilesScanned = 0;
  for (let i = 0; i < sourceCandidates.length; i++) {
    const candidate = sourceCandidates[i]!;
    if (filesRead >= limits.maxFiles) {
      reportError(unknowns, 'scan-limit-max-files', 'The maximum inspected file count was reached; remaining source files are unknown.', sourceCandidates.length - i);
      break;
    }
    filesRead++;
    const read = readCandidate(tree, candidate, limits, totalBytes);
    if (read.text === undefined) { readStatusUnknown(candidate, 'source signals', read.error); continue; }
    totalBytes += read.bytes ?? 0;
    sourceFiles.push(candidate.relative);
    evidence.push({ path: candidate.relative, kind: 'source-js-ts', bytes: read.bytes ?? 0, sha256: read.sha256!, statFingerprint: read.statFingerprint! });
    const scan = scanSource(read.text, candidate.relative, mainPaths, Math.max(0, limits.maxCandidates - findings.length));
    if (scan.unsupported.length) {
      reportError(unknowns, 'source-syntax-unsupported', `${candidate.relative} was not lexically scanned because ${scan.unsupported.join(', ')}; it remains available for controlled manual review.`);
      continue;
    }
    sourceFilesScanned++;
    scannedSourceFiles.push(candidate.relative);
    findings.push(...scan.findings);
    if (scan.truncated) reportError(unknowns, 'scan-limit-max-candidates', `Candidate findings in ${candidate.relative} were truncated at the configured cap.`);
  }
  for (const main of mainPaths) {
    if (!sourceFiles.includes(main)) reportError(unknowns, 'configured-main-not-reviewed', `Configured main ${main} was not safely included in the source review set.`);
  }

  const sqlCandidates = discovery.candidates.filter((candidate) => candidate.kind === 'sql');
  const auxiliaryToRead: Candidate[] = [];
  for (const item of configRaw) {
    if (!item.valid || !hasD1Declaration(item.raw)) continue;
    const selections = migrationDirectories(item.candidate.relative, item.raw);
    if (selections.length > 1) reportError(unknowns, 'd1-migration-binding-attribution-unknown', `Multiple D1 bindings are configured in ${item.candidate.relative}; the bounded SQL evidence paths are not attributed to individual bindings.`);
    for (const selection of selections) {
      if (selection.invalid || !selection.directory) {
        reportError(unknowns, 'd1-migration-directory-invalid', `A D1 migrations_dir in ${item.candidate.relative} is invalid or unsafe; migration coverage is unknown.`);
        continue;
      }
      const selected = sqlCandidates.filter((candidate) => candidate.relative.startsWith(`${selection.directory}/`) && !candidate.relative.slice(selection.directory!.length + 1).includes('/'));
      auxiliaryToRead.push(...selected);
      if (!selected.length) reportError(unknowns, 'd1-migrations-not-found', `No safe direct-child .sql migration files were found under ${selection.directory}; migration coverage is unknown.`);
      if (sqlCandidates.some((candidate) => candidate.relative.startsWith(`${selection.directory}/`) && candidate.relative.slice(selection.directory!.length + 1).includes('/')))
        reportError(unknowns, 'd1-migration-nested-files-not-included', `Nested .sql paths under ${selection.directory} are not included in the migration evidence set.`);
    }
  }
  const workflows = discovery.candidates.filter((candidate) => candidate.kind === 'workflow' && /^\.github\/workflows\/[^/]+\.(?:yml|yaml)$/i.test(candidate.relative));
  if (configRaw.some((item) => item.valid)) auxiliaryToRead.push(...workflows);
  const uniqueAux = [...new Map(auxiliaryToRead.map((candidate) => [candidate.relative, candidate])).values()].sort((a, b) => a.relative.localeCompare(b.relative));
  const readAuxiliaryFiles: string[] = [];
  for (let i = 0; i < uniqueAux.length; i++) {
    const candidate = uniqueAux[i]!;
    if (filesRead >= limits.maxFiles) {
      reportError(unknowns, 'scan-limit-max-files', 'The maximum inspected file count was reached; remaining auxiliary evidence files are unknown.', uniqueAux.length - i);
      break;
    }
    filesRead++;
    const read = readCandidate(tree, candidate, limits, totalBytes);
    if (read.text === undefined) { readStatusUnknown(candidate, 'auxiliary evidence', read.error); continue; }
    totalBytes += read.bytes ?? 0;
    const kind = candidate.kind === 'sql' ? 'd1-migration-sql' : 'github-workflow-yaml';
    evidence.push({ path: candidate.relative, kind, bytes: read.bytes ?? 0, sha256: read.sha256!, statFingerprint: read.statFingerprint! });
    readAuxiliaryFiles.push(candidate.relative);
  }
  if (sourceFilesScanned === 0) reportError(unknowns, 'no-source-files-scanned', 'No supported source files were scanned; code-path and billing-cycle signals are unknown.');
  unknowns.push({ code: 'static-analysis-scope', detail: 'No call graph, import resolution, alias analysis, dynamic dispatch, generated code, framework wiring, external triggers, or runtime behavior is resolved; trigger chains remain unknown.' });
  const status: AuditReport['status'] = unknowns.some((item) => item.code !== 'static-analysis-scope') || configs.some((config) => config.parserStatus.startsWith('unsupported') || config.parserStatus.startsWith('invalid')) || configs.length === 0 ? 'partial' : sourceFilesScanned ? 'scanned' : 'inventory-only';
  return {
    schemaVersion: '1.1', generatedAt: now.toISOString(), projectLabel: path.basename(projectPath) || 'project', runtimePlatform: process.platform,
    secureReadMode: tree.mode, projectRootFingerprint: tree.rootFingerprint(), status,
    coverage: [
      'Offline read-only scan; no network, project script, import, package hook, or target-code execution.',
      'Wrangler JSON/JSONC and supported Bun TOML configs are inventoried without outputting config values.',
      'Source candidate signals are lexical only; trigger chains, aliases, external entrances, and runtime behavior remain unknown.',
      'D1 migration SQL and GitHub workflow YAML may be listed as bounded, fingerprinted manual-review evidence; neither format is executed or fully parsed.',
      tree.mode === 'descriptor-anchored' ? 'Never reads .env-prefixed/secrets/credentials paths; never follows symlinks; excludes generated/dependency trees.' : 'Excludes secret-like and generated/dependency paths; rejects observed symlink, junction and path redirection in a stable tree. Concurrent path replacement can defeat portable checks.',
      tree.mode === 'descriptor-anchored' ? 'Descriptor-pinned reads detect path identity changes but do not provide an atomic filesystem snapshot against an arbitrary same-privilege concurrent actor.' : 'Portable stable-tree access requires unchanged input and output ancestry throughout scan/review. Pre/post identity and realpath checks are best effort, not atomic no-follow traversal or protection against malicious same-user races.',
    ],
    limits, workspaces: [...new Set(configs.map((config) => config.workspace))].sort(), configs, packageWorkspaces,
    readSourceFiles: sourceFiles, readAuxiliaryFiles, reviewEvidenceFiles: evidence.sort((a, b) => a.path.localeCompare(b.path)),
    sourceFilesScanned, scannedSourceFiles, findings, unknowns,
    skipped: { symlinks: discovery.symlinks, excludedPaths: discovery.excludedPaths, unreadableOrOversize, nonRegularFiles: discovery.nonRegularFiles },
  };
}

export function auditProject(projectPath: string, options: AuditOptions = {}): { report: AuditReport; outputDirectory?: string } {
  const requestedRoot = resolveAuditPath(projectPath);
  const tree = openAuditFs(requestedRoot, false, options.accessMode);
  try {
    const report = auditOnTree(tree, requestedRoot, options);
    if (options.writeReports === false) return { report };
    const inventoryText = `${JSON.stringify(report, null, 2)}\n`;
    if (Buffer.byteLength(inventoryText) > MAX_INVENTORY_BYTES) throw new Error('inventory-too-large');
    const outputBasePath = resolveAuditPath(options.outputDir ?? path.join(skillDir, 'audit-results'));
    if (isWithin(requestedRoot, outputBasePath)) throw new Error('output-inside-project');
    let outputBase: AuditFs;
    try { outputBase = openAuditFs(outputBasePath, true, options.accessMode); }
    catch (error) {
      if (error instanceof Error && error.message === 'project-path-through-symlink') throw new Error('output-symlink-component');
      if (error instanceof Error && error.message === 'project-path-not-directory') throw new Error('invalid-output-directory');
      throw error;
    }
    try {
      const output = createOutputDirectory(outputBase, options.now ?? new Date());
      try {
        output.tree.writeNewFile('inventory.json', inventoryText);
        output.tree.writeNewFile('inventory.md', renderMarkdown(report));
      } finally { output.tree.close(); }
      return { report, outputDirectory: output.path };
    } finally { outputBase.close(); }
  } finally { tree.close(); }
}

function isSafeEvidencePath(relative: string): boolean {
  if (!relative || path.posix.isAbsolute(relative) || relative.includes('\\') || relative.split('/').some((part) => !part || part === '.' || part === '..' || isSensitivePath(part))) return false;
  return true;
}

export function readReviewEvidenceFile(projectPath: string, inventoryPath: string, relative: string, options: Pick<AuditOptions, 'accessMode'> = {}): string {
  if (!isSafeEvidencePath(relative)) throw new Error('review-evidence-not-allowlisted');
  const absoluteInventory = resolveAuditPath(inventoryPath);
  if (path.basename(absoluteInventory) !== 'inventory.json' || absoluteInventory.split(path.sep).some(isSensitivePath)) throw new Error('unsafe-inventory-path');
  const requestedRoot = resolveAuditPath(projectPath);
  if (isWithin(requestedRoot, absoluteInventory)) throw new Error('unsafe-inventory-path');
  const inventoryTree = openAuditFs(path.dirname(absoluteInventory), false, options.accessMode);
  let inventory: unknown;
  try {
    const read = inventoryTree.readFile('inventory.json', MAX_INVENTORY_BYTES);
    if (read.text === undefined) throw new Error('invalid-inventory');
    try { inventory = JSON.parse(read.text); } catch { throw new Error('invalid-inventory'); }
  } finally { inventoryTree.close(); }
  const report = object(inventory) as unknown as AuditReport | undefined;
  if (!report || report.schemaVersion !== '1.1' || !Array.isArray(report.reviewEvidenceFiles) || !report.limits || JSON.stringify(report.limits) !== JSON.stringify(DEFAULT_LIMITS)) throw new Error('stale-inventory');
  const snapshot = report.reviewEvidenceFiles.find((item) => object(item)?.path === relative) as ReviewEvidenceFile | undefined;
  if (!snapshot || !['source-js-ts', 'd1-migration-sql', 'github-workflow-yaml'].includes(snapshot.kind) || !Number.isSafeInteger(snapshot.bytes) || snapshot.bytes < 0 || !/^[0-9a-f]{64}$/.test(snapshot.sha256) || !/^[0-9a-f]{64}$/.test(snapshot.statFingerprint)) throw new Error('review-evidence-not-allowlisted');
  if ((snapshot.kind === 'source-js-ts' && !SOURCE_EXTENSIONS.has(path.extname(relative).toLowerCase())) || (snapshot.kind === 'd1-migration-sql' && path.extname(relative).toLowerCase() !== '.sql') || (snapshot.kind === 'github-workflow-yaml' && !/^\.github\/workflows\/[^/]+\.(?:yml|yaml)$/i.test(relative))) throw new Error('review-evidence-not-allowlisted');

  const fresh = auditProject(requestedRoot, { writeReports: false, accessMode: options.accessMode }).report;
  if (fresh.secureReadMode !== report.secureReadMode || fresh.projectRootFingerprint !== report.projectRootFingerprint) throw new Error('stale-inventory');
  const current = fresh.reviewEvidenceFiles.find((item) => item.path === relative);
  if (!current || current.kind !== snapshot.kind || current.bytes !== snapshot.bytes || current.sha256 !== snapshot.sha256 || current.statFingerprint !== snapshot.statFingerprint) throw new Error('stale-review-evidence');
  const tree = openAuditFs(requestedRoot, false, options.accessMode);
  try {
    if (tree.rootFingerprint() !== report.projectRootFingerprint) throw new Error('stale-inventory');
    const info = tree.inspectFile(relative);
    if (info.status !== 'file' || !info.stat || !info.parentFingerprint) throw new Error('stale-review-evidence');
    const read = tree.readFile(relative, DEFAULT_LIMITS.maxFileBytes, { stat: info.stat, statFingerprint: statFingerprint(info.stat, info.parentFingerprint) });
    if (read.text === undefined || read.sha256 !== snapshot.sha256 || read.bytes !== snapshot.bytes || read.statFingerprint !== snapshot.statFingerprint) throw new Error('stale-review-evidence');
    return read.text;
  } finally { tree.close(); }
}
