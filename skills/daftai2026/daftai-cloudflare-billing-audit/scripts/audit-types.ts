/**
 * [INPUT]: 依赖 TypeScript 类型系统
 * [OUTPUT]: 提供 审计契约、额度和静态集合
 * [POS]: 脚本层的无副作用共享契约
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
export type UnknownItem = { code: string; detail: string; count?: number };
export type Binding = { product: string; type: string; binding: string; role?: string };
export type MainStatus = {
  configured: boolean;
  source: string;
  status: string;
  path?: string;
};
export type EnvironmentInventory = {
  name: string;
  declarations: 'local-only';
  main: MainStatus;
  varsCount: number;
  bindings: Binding[];
  triggers: { cronCount: number };
  routeCount: number;
  limits: { cpuMs?: number };
};
export type ConfigInventory = {
  path: string;
  workspace: string;
  format: 'json' | 'jsonc' | 'toml';
  parserStatus: string;
  environments: EnvironmentInventory[];
};
export type CandidateFinding = {
  ruleId: string;
  matchesRuleId: string;
  product: string;
  file: string;
  line: number;
  triggerChain: 'unknown';
  evidence: string;
  condition: string;
  possibleConsequence: string;
  recommendation: string;
  sources: string[];
};
export type AuditReport = {
  schemaVersion: '1.1';
  generatedAt: string;
  projectLabel: string;
  runtimePlatform: string;
  secureReadMode: 'descriptor-anchored' | 'portable-stable-tree';
  projectRootFingerprint: string;
  status: 'partial' | 'inventory-only' | 'scanned';
  coverage: string[];
  limits: { maxDepth: number; maxFiles: number; maxEntries: number; maxTotalBytes: number; maxFileBytes: number; maxCandidates: number };
  workspaces: string[];
  configs: ConfigInventory[];
  packageWorkspaces: Array<{ manifest: string; patternCount: number; patterns: string[] }>;
  readSourceFiles: string[];
  readAuxiliaryFiles: string[];
  reviewEvidenceFiles: ReviewEvidenceFile[];
  sourceFilesScanned: number;
  scannedSourceFiles: string[];
  findings: CandidateFinding[];
  unknowns: UnknownItem[];
  skipped: { symlinks: number; excludedPaths: number; unreadableOrOversize: number; nonRegularFiles: number };
};

export type ReviewEvidenceFile = {
  path: string;
  kind: 'source-js-ts' | 'd1-migration-sql' | 'github-workflow-yaml';
  bytes: number;
  sha256: string;
  statFingerprint: string;
};

export type AuditOptions = {
  accessMode?: 'portable-stable-tree';
  outputDir?: string;
  now?: Date;
  limits?: Partial<AuditReport['limits']>;
  writeReports?: boolean;
};

export const DEFAULT_LIMITS: AuditReport['limits'] = {
  maxDepth: 8,
  maxFiles: 500,
  maxEntries: 4000,
  maxTotalBytes: 2 * 1024 * 1024,
  maxFileBytes: 256 * 1024,
  maxCandidates: 200,
};

export const CONFIG_NAMES = new Set(['wrangler.json', 'wrangler.jsonc', 'wrangler.toml']);
export const SOURCE_EXTENSIONS = new Set(['.js', '.jsx', '.mjs', '.cjs', '.ts', '.tsx', '.mts', '.cts']);
export const AUXILIARY_EXTENSIONS = new Set(['.sql', '.yml', '.yaml']);
export const EXCLUDED_DIRS = new Set([
  '.git', '.hg', '.svn', 'node_modules', 'build', 'dist', 'out', 'target', 'coverage',
  '.wrangler', '.next', '.nuxt', '.vercel', '.turbo', 'vendor', 'secrets', '.secrets',
  'credentials',
]);
export const SAFE_BINDING_NAME = /^[A-Za-z_$][A-Za-z0-9_$]{0,63}$/;
export const DOCS = {
  alarms: 'https://developers.cloudflare.com/durable-objects/api/alarms/',
  queueApi: 'https://developers.cloudflare.com/queues/configuration/javascript-apis/',
  queues: 'https://developers.cloudflare.com/workers/configuration/queues/',
};

// 库存元数据有独立上限；它不扩大目标源码的读取额度。
export const MAX_INVENTORY_BYTES = 16 * 1024 * 1024;
