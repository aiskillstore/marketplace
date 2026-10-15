/**
 * [INPUT]: 依赖 node:path、node:process、node:url 和 audit-engine 的受控入口
 * [OUTPUT]: 提供 兼容导出、CLI 与退出码
 * [POS]: 脚本层的唯一命令入口；领域模块不反向依赖它
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import { auditProject, readReviewEvidenceFile } from './audit-engine.ts';
export { auditProject, readReviewEvidenceFile } from './audit-engine.ts';
export type { UnknownItem, Binding, MainStatus, EnvironmentInventory, ConfigInventory, CandidateFinding, AuditReport, ReviewEvidenceFile, AuditOptions } from './audit-types.ts';
export { stripJsoncComments, parseJsoncStrict } from './config.ts';
export { maskJavaScript, scanSource } from './source-scan.ts';
export type { SourceScanResult } from './source-scan.ts';
function parseArgs(args: string[]): { project?: string; outputDir?: string; inventory?: string; readFile?: string; help: boolean } {
  let project: string | undefined;
  let outputDir: string | undefined;
  let inventory: string | undefined;
  let readFile: string | undefined;
  let help = false;
  for (let i = 0; i < args.length; i++) {
    const arg = args[i]!;
    if (arg === '--help' || arg === '-h') { help = true; continue; }
    if (arg === '--project') { project = args[++i]; if (!project) throw new Error('missing-project-path'); continue; }
    if (arg === '--output-dir') { outputDir = args[++i]; if (!outputDir) throw new Error('missing-output-directory'); continue; }
    if (arg === '--inventory') { inventory = args[++i]; if (!inventory) throw new Error('missing-inventory-path'); continue; }
    if (arg === '--read-file') { readFile = args[++i]; if (!readFile) throw new Error('missing-review-path'); continue; }
    throw new Error('unknown-cli-option');
  }
  return { project, outputDir, inventory, readFile, help };
}

export function runCli(args = process.argv.slice(2)): number {
  try {
    const parsed = parseArgs(args);
    if (parsed.help) {
      console.log('Usage: bun scripts/audit.ts --project <path> [--output-dir <audit-workdir>] | --project <path> --inventory <inventory.json> --read-file <listed-relative-path>');
      return 0;
    }
    if (!parsed.project) throw new Error('explicit-project-required');
    if (parsed.inventory || parsed.readFile) {
      if (!parsed.inventory || !parsed.readFile || parsed.outputDir) throw new Error('invalid-reader-arguments');
      const source = readReviewEvidenceFile(parsed.project, parsed.inventory, parsed.readFile);
      process.stdout.write(source);
      return 0;
    }
    const result = auditProject(parsed.project, { outputDir: parsed.outputDir });
    console.log(JSON.stringify({ status: result.report.status, workspaces: result.report.workspaces.length, configs: result.report.configs.length, sourceFilesScanned: result.report.sourceFilesScanned, candidateFindings: result.report.findings.length, outputDirectory: result.outputDirectory }));
    return 0;
  } catch (error) {
    const message = error instanceof Error ? error.message : 'audit-failed';
    const publicMessages: Record<string, string> = {
      'explicit-project-required': 'Error: pass an explicit --project <path>.',
      'project-path-not-found': 'Error: the project path does not exist or cannot be resolved.',
      'project-path-through-symlink': 'Error: the project path contains a symlink component; symlink paths are not followed.',
      'project-path-not-directory': 'Error: --project must point to a directory.',
      'output-inside-project': 'Error: output directory must be outside the target project.',
      'missing-project-path': 'Error: --project requires a path.',
      'missing-output-directory': 'Error: --output-dir requires a path.',
      'inventory-too-large': 'Error: inventory metadata exceeds 16 MiB; choose a narrower explicit project scope.',
      'secure-path-access-unsupported': 'Error: required secure filesystem access is unavailable on this host.',
      'unsafe-windows-path': 'Error: use an ordinary local Windows drive path without reserved or ambiguous components.',
      'unknown-cli-option': 'Error: unsupported command-line option.',
    };
    console.error(publicMessages[message] ?? 'Error: audit could not complete safely.');
    return /stale|inventory|review-evidence-not-allowlisted/.test(message) ? 3 : 2;
  }
}

const entryArg = process.argv[1] ? path.resolve(process.argv[1]) : '';
if (entryArg && entryArg === path.resolve(fileURLToPath(import.meta.url))) process.exitCode = runCli();
