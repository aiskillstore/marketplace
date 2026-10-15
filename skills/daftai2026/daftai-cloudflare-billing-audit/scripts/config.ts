/**
 * [INPUT]: 依赖 文件适配器、发现边界、共享契约和 Bun 解析器
 * [OUTPUT]: 提供 配置解析、环境投影与辅助证据范围
 * [POS]: 配置领域层；不执行配置或推断部署状态
 * [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
 */
import path from 'node:path';
import type { AuditFs } from './audit-fs.ts';
import type { Candidate } from './discovery.ts';
import { isSensitivePath } from './discovery.ts';
import { object, isObject, isWithin, displayPath } from './fs-common.ts';
import type { Binding, MainStatus, EnvironmentInventory, ConfigInventory, UnknownItem } from './audit-types.ts';
import { SAFE_BINDING_NAME } from './audit-types.ts';
export function stripJsoncComments(input: string): string {
  let output = '';
  let inString = false;
  let escaped = false;
  for (let i = 0; i < input.length; i++) {
    const ch = input[i]!;
    const next = input[i + 1];
    if (inString) {
      output += ch;
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === '"') inString = false;
      continue;
    }
    if (ch === '"') { inString = true; output += ch; continue; }
    if (ch === '/' && next === '/') {
      output += '  '; i++;
      while (i + 1 < input.length && input[i + 1] !== '\n' && input[i + 1] !== '\r') { output += ' '; i++; }
      continue;
    }
    if (ch === '/' && next === '*') {
      output += '  '; i++;
      let closed = false;
      while (i + 1 < input.length) {
        i++;
        const commentCh = input[i]!;
        if (commentCh === '*' && input[i + 1] === '/') { output += '  '; i++; closed = true; break; }
        output += commentCh === '\n' || commentCh === '\r' ? commentCh : ' ';
      }
      if (!closed) throw new Error('unterminated-jsonc-comment');
      continue;
    }
    output += ch;
  }
  if (inString) throw new Error('unterminated-json-string');
  return output;
}

function removeTrailingCommas(input: string): string {
  let output = '';
  let inString = false;
  let escaped = false;
  for (let i = 0; i < input.length; i++) {
    const ch = input[i]!;
    if (inString) {
      output += ch;
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === '"') inString = false;
      continue;
    }
    if (ch === '"') { inString = true; output += ch; continue; }
    if (ch === ',') {
      let j = i + 1;
      while (/\s/.test(input[j] ?? '') && j < input.length) j++;
      const previous = output.trimEnd().at(-1) ?? '';
      if ((input[j] === '}' || input[j] === ']') && /["}\]0-9A-Za-z]/.test(previous)) continue;
    }
    output += ch;
  }
  return output;
}

function parseJsonStringAt(source: string, start: number): { value: string; end: number } {
  let escaped = false;
  for (let i = start + 1; i < source.length; i++) {
    const ch = source[i]!;
    if (escaped) { escaped = false; continue; }
    if (ch === '\\') { escaped = true; continue; }
    if (ch === '"') {
      return { value: JSON.parse(source.slice(start, i + 1)) as string, end: i + 1 };
    }
  }
  throw new Error('invalid-json-string');
}

function parseStrictJsonWithDuplicateGuard(source: string): unknown {
  let i = 0;
  let depth = 0;
  const whitespace = (): void => { while (/\s/.test(source[i] ?? '') && i < source.length) i++; };
  const parseValue = (): unknown => {
    whitespace();
    if (++depth > 128) throw new Error('json-depth-limit');
    const ch = source[i];
    let value: unknown;
    if (ch === '"') {
      const parsed = parseJsonStringAt(source, i); i = parsed.end; value = parsed.value;
    } else if (ch === '{') {
      i++; whitespace();
      const object: Record<string, unknown> = Object.create(null) as Record<string, unknown>;
      const keys = new Set<string>();
      if (source[i] === '}') i++;
      else {
        while (true) {
          whitespace();
          if (source[i] !== '"') throw new Error('invalid-json-object-key');
          const key = parseJsonStringAt(source, i); i = key.end;
          if (keys.has(key.value)) throw new Error('duplicate-json-object-key');
          keys.add(key.value); whitespace();
          if (source[i] !== ':') throw new Error('invalid-json-object-colon');
          i++; object[key.value] = parseValue(); whitespace();
          if (source[i] === '}') { i++; break; }
          if (source[i] !== ',') throw new Error('invalid-json-object-separator');
          i++; whitespace();
        }
      }
      value = object;
    } else if (ch === '[') {
      i++; whitespace();
      const array: unknown[] = [];
      if (source[i] === ']') i++;
      else {
        while (true) {
          array.push(parseValue()); whitespace();
          if (source[i] === ']') { i++; break; }
          if (source[i] !== ',') throw new Error('invalid-json-array-separator');
          i++; whitespace();
        }
      }
      value = array;
    } else {
      const rest = source.slice(i);
      const match = /^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/.exec(rest);
      if (!match) throw new Error('invalid-json-value');
      value = JSON.parse(match[0]) as unknown; i += match[0].length;
      if (typeof value === 'number' && !Number.isFinite(value)) throw new Error('non-finite-json-number');
    }
    depth--;
    return value;
  };
  const value = parseValue(); whitespace();
  if (i !== source.length) throw new Error('trailing-json-content');
  return value;
}

export function parseJsoncStrict(source: string): unknown {
  const cleaned = removeTrailingCommas(stripJsoncComments(source));
  const guarded = parseStrictJsonWithDuplicateGuard(cleaned);
  const bun = (globalThis as typeof globalThis & { Bun?: { JSONC?: { parse?: (text: string) => unknown } } }).Bun;
  if (typeof bun?.JSONC?.parse === 'function') {
    // Bun's native JSONC parser owns the parse; the bounded guard above rejects duplicate keys first.
    return bun.JSONC.parse(cleaned);
  }
  return guarded;
}

export function parseConfig(format: ConfigInventory['format'], text: string): { value?: unknown; status: string } {
  if (format !== 'toml') {
    try { return { value: parseJsoncStrict(text), status: 'supported-jsonc' }; }
    catch { return { status: 'invalid-json-or-jsonc' }; }
  }
  const bun = (globalThis as typeof globalThis & { Bun?: { TOML?: { parse?: (text: string) => unknown } } }).Bun;
  if (typeof bun?.TOML?.parse !== 'function') return { status: 'unsupported-no-bun-toml-parser' };
  try { return { value: bun.TOML.parse(text), status: 'supported-bun-toml' }; }
  catch { return { status: 'invalid-toml' }; }
}

function safeIdentifier(value: unknown, fallback: string): string {
  if (typeof value !== 'string') return fallback;
  return SAFE_BINDING_NAME.test(value) ? value : fallback;
}

const BINDING_FIELDS: Record<string, { product: string; type: string }> = {
  kv_namespaces: { product: 'Workers KV', type: 'kv_namespace' },
  r2_buckets: { product: 'R2', type: 'r2_bucket' },
  d1_databases: { product: 'D1', type: 'd1_database' },
  services: { product: 'Workers Service Bindings', type: 'service_binding' },
  workflows: { product: 'Workflows', type: 'workflow' },
  analytics_engine_datasets: { product: 'Analytics Engine', type: 'analytics_engine_dataset' },
  vectorize: { product: 'Vectorize', type: 'vectorize_index' },
  hyperdrive: { product: 'Hyperdrive', type: 'hyperdrive_config' },
  pipelines: { product: 'Pipelines', type: 'pipeline' },
  send_email: { product: 'Email Routing', type: 'send_email' },
  secrets_store_secrets: { product: 'Secrets Store', type: 'secret_store_binding' },
};

const SINGLE_BINDING_FIELDS: Record<string, { product: string; type: string }> = {
  ai: { product: 'Workers AI', type: 'ai_binding' },
  browser: { product: 'Browser Rendering', type: 'browser' },
  assets: { product: 'Workers Static Assets', type: 'assets' },
  images: { product: 'Images', type: 'images' },
};

function collectBindings(config: Record<string, unknown>): { bindings: Binding[]; varsCount: number; unknownBindingCount: number } {
  const bindings: Binding[] = [];
  let unknownBindingCount = 0;
  for (const [field, metadata] of Object.entries(BINDING_FIELDS)) {
    const entries = config[field];
    if (entries === undefined) continue;
    if (!Array.isArray(entries)) { unknownBindingCount++; continue; }
    entries.forEach((entry, index) => {
      if (!isObject(entry)) { unknownBindingCount++; return; }
      const label = safeIdentifier(entry.binding, `binding-${index + 1}`);
      bindings.push({ product: metadata.product, type: metadata.type, binding: label });
    });
  }
  for (const [field, metadata] of Object.entries(SINGLE_BINDING_FIELDS)) {
    if (config[field] === undefined) continue;
    const entry = object(config[field]);
    if (!entry) { unknownBindingCount++; continue; }
    bindings.push({ product: metadata.product, type: metadata.type, binding: safeIdentifier(entry.binding, 'binding-1') });
  }
  if (config.containers !== undefined) {
    if (!Array.isArray(config.containers)) unknownBindingCount++;
    else config.containers.forEach((entry) => {
      if (!isObject(entry)) { unknownBindingCount++; return; }
      bindings.push({ product: 'Cloudflare Containers', type: 'container', binding: safeIdentifier(entry.class_name, 'container') });
    });
  }
  const doConfig = object(config.durable_objects);
  if (config.durable_objects !== undefined && !doConfig) unknownBindingCount++;
  const doBindings = doConfig?.bindings;
  if (doBindings !== undefined && !Array.isArray(doBindings)) unknownBindingCount++;
  if (Array.isArray(doBindings)) doBindings.forEach((entry, index) => {
    if (!isObject(entry)) { unknownBindingCount++; return; }
    bindings.push({ product: 'Durable Objects', type: 'durable_object_namespace', binding: safeIdentifier(entry.name, `binding-${index + 1}`) });
  });
  const queue = object(config.queues);
  if (config.queues !== undefined && !queue) unknownBindingCount++;
  if (queue) {
    for (const role of ['producers', 'consumers'] as const) {
      const entries = queue[role];
      if (entries === undefined) continue;
      if (!Array.isArray(entries)) { unknownBindingCount++; continue; }
      entries.forEach((entry, index) => {
        if (!isObject(entry)) { unknownBindingCount++; return; }
        bindings.push({ product: 'Cloudflare Queues', type: `queue_${role.slice(0, -1)}`, binding: safeIdentifier(entry.binding, `${role.slice(0, -1)}-${index + 1}`), role });
      });
    }
  }
  const unsafeBindings = object(config.unsafe)?.bindings;
  if (unsafeBindings !== undefined) unknownBindingCount += Array.isArray(unsafeBindings) ? Math.max(1, unsafeBindings.length) : 1;
  const vars = object(config.vars);
  if (config.vars !== undefined && !vars) unknownBindingCount++;
  return { bindings, varsCount: vars ? Object.keys(vars).length : 0, unknownBindingCount };
}

function collectExecutionMetadata(config: Record<string, unknown>): { triggers: { cronCount: number }; routeCount: number; limits: { cpuMs?: number }; unknownCount: number } {
  let unknownCount = 0;
  let cronCount = 0;
  if (config.triggers !== undefined) {
    const triggers = object(config.triggers);
    if (!triggers) unknownCount++;
    else if (triggers.crons !== undefined) {
      if (Array.isArray(triggers.crons)) cronCount = triggers.crons.length;
      else unknownCount++;
    }
  }
  let routeCount = 0;
  if (config.routes !== undefined) {
    if (Array.isArray(config.routes)) routeCount += config.routes.length;
    else if (typeof config.routes === 'string') routeCount++;
    else unknownCount++;
  }
  if (config.route !== undefined) {
    if (typeof config.route === 'string') routeCount++;
    else unknownCount++;
  }
  const limitsObject = object(config.limits);
  const limits: { cpuMs?: number } = {};
  if (config.limits !== undefined && !limitsObject) unknownCount++;
  if (limitsObject?.cpu_ms !== undefined) {
    if (typeof limitsObject.cpu_ms === 'number' && Number.isSafeInteger(limitsObject.cpu_ms) && limitsObject.cpu_ms >= 0) limits.cpuMs = limitsObject.cpu_ms;
    else unknownCount++;
  }
  return { triggers: { cronCount }, routeCount, limits, unknownCount };
}

function safeMain(tree: AuditFs, workspace: string, configured: unknown, source: string): MainStatus {
  if (configured === undefined) return { configured: false, source, status: 'not-declared' };
  if (typeof configured !== 'string' || configured.length === 0 || configured.includes('\0') || /^[A-Za-z]:[\\/]/.test(configured)) {
    return { configured: true, source, status: 'invalid-or-non-string' };
  }
  const root = tree.rootPath;
  const target = path.resolve(workspace, configured);
  if (!isWithin(root, target)) return { configured: true, source, status: 'outside-project' };
  const relative = displayPath(root, target);
  if (relative.split('/').some(isSensitivePath)) return { configured: true, source, status: 'excluded-sensitive-path', path: relative };
  const check = tree.inspectFile(relative);
  if (check.status === 'file') return { configured: true, source, status: 'exists', path: relative };
  if (check.status === 'missing') return { configured: true, source, status: 'missing', path: relative };
  if (check.status === 'symlink') return { configured: true, source, status: 'symlink-not-followed', path: relative };
  return { configured: true, source, status: 'not-regular-file', path: relative };
}

function environmentInventory(tree: AuditFs, workspace: string, config: Record<string, unknown>, envName: string, source: string, inheritedMain?: unknown): EnvironmentInventory {
  const mainConfigured = Object.prototype.hasOwnProperty.call(config, 'main') ? config.main : inheritedMain;
  const mainSource = Object.prototype.hasOwnProperty.call(config, 'main') ? source : inheritedMain !== undefined ? 'base (inherited)' : source;
  const { bindings, varsCount } = collectBindings(config);
  const execution = collectExecutionMetadata(config);
  return {
    name: envName,
    declarations: 'local-only',
    main: safeMain(tree, workspace, mainConfigured, mainSource),
    varsCount,
    bindings,
    triggers: execution.triggers,
    routeCount: execution.routeCount,
    limits: execution.limits,
  };
}

export function parseWranglerEnvironments(tree: AuditFs, candidate: Candidate, raw: unknown, format: ConfigInventory['format'], parserStatus: string, unknowns: UnknownItem[]): ConfigInventory {
  const root = tree.rootPath;
  const workspace = path.resolve(root, path.dirname(candidate.relative));
  const workspacePath = path.posix.dirname(candidate.relative) || '.';
  const config = object(raw) ?? Object.create(null) as Record<string, unknown>;
  if (!isObject(raw)) unknowns.push({ code: 'invalid-wrangler-root', detail: `${candidate.relative} did not contain a top-level object; no config fields were normalized.` });
  const environments: EnvironmentInventory[] = [];
  environments.push(environmentInventory(tree, workspace, config, 'base', 'base config'));
  const envs = object(config.env);
  if (config.env !== undefined && !envs) unknowns.push({ code: 'invalid-env-config', detail: `Environment declaration in ${candidate.relative} is not an object; environment coverage is unknown.` });
  if (envs) {
    let index = 0;
    for (const [key, value] of Object.entries(envs)) {
      index++;
      const env = object(value);
      const label = /^[A-Za-z0-9_.-]{1,64}$/.test(key) ? key : `environment-${index}`;
      if (!env) { unknowns.push({ code: 'invalid-env-entry', detail: `An environment in ${candidate.relative} is not an object; its bindings are unknown.` }); continue; }
      const inventory = environmentInventory(tree, workspace, env, label, `env.${label}`, config.main);
      // Wrangler non-inheritable keys are intentionally not shallow-merged; declarations are reported per scope.
      if (Object.prototype.hasOwnProperty.call(env, 'main') && env.main !== undefined) inventory.main = safeMain(tree, workspace, env.main, `env.${label}`);
      environments.push(inventory);
      if (collectBindings(env).unknownBindingCount) unknowns.push({ code: 'unclassified-binding', detail: `Some binding declarations in ${candidate.relative} (env.${label}) could not be normalized.` });
      if (collectExecutionMetadata(env).unknownCount) unknowns.push({ code: 'unclassified-trigger-route-limit', detail: `Some trigger, route, or limit declarations in ${candidate.relative} (env.${label}) were not understood.` });
    }
  }
  if (collectBindings(config).unknownBindingCount) unknowns.push({ code: 'unclassified-binding', detail: `Some binding declarations in ${candidate.relative} (base) could not be normalized.` });
  if (collectExecutionMetadata(config).unknownCount) unknowns.push({ code: 'unclassified-trigger-route-limit', detail: `Some trigger, route, or limit declarations in ${candidate.relative} (base) were not understood.` });
  if (config.main === undefined) unknowns.push({ code: 'main-not-declared', detail: `No main entry point is declared in ${candidate.relative}; source reachability is unknown.` });
  return { path: candidate.relative, workspace: workspacePath, format, parserStatus, environments };
}

export function hasD1Declaration(raw: unknown): boolean {
  const config = object(raw);
  if (!config) return false;
  if (Array.isArray(config.d1_databases) && config.d1_databases.some((entry) => isObject(entry))) return true;
  const envs = object(config.env);
  return !!envs && Object.values(envs).some((entry) => {
    const env = object(entry);
    return !!env && Array.isArray(env.d1_databases) && env.d1_databases.some((binding) => isObject(binding));
  });
}

export function validAuxiliaryConfig(configPath: string, raw: unknown): boolean {
  const config = object(raw);
  if (!config) return false;
  const validScope = (scope: Record<string, unknown>): boolean =>
    (scope.main === undefined || typeof scope.main === 'string') &&
    collectBindings(scope).unknownBindingCount === 0 && collectExecutionMetadata(scope).unknownCount === 0;
  if (!validScope(config) || migrationDirectories(configPath, config).some((selection) => selection.invalid)) return false;
  if (config.env === undefined) return true;
  const envs = object(config.env);
  if (!envs) return false;
  return Object.values(envs).every((value) => {
    const env = object(value);
    return !!env && validScope(env) && migrationDirectories(configPath, { env: { preview: env } }).every((selection) => !selection.invalid);
  });
}

export function migrationDirectories(configPath: string, raw: unknown): Array<{ directory?: string; invalid: boolean }> {
  const config = object(raw);
  if (!config) return [];
  const workspace = path.posix.dirname(configPath);
  const bindings: unknown[] = [];
  if (Array.isArray(config.d1_databases)) bindings.push(...config.d1_databases);
  const envs = object(config.env);
  if (envs) for (const value of Object.values(envs)) {
    const env = object(value);
    if (Array.isArray(env?.d1_databases)) bindings.push(...env.d1_databases);
  }
  const selections: Array<{ directory?: string; invalid: boolean }> = [];
  for (const item of bindings) {
    const binding = object(item);
    if (!binding) continue;
    const value = binding.migrations_dir;
    if (typeof value === 'string' && (value.includes('\0') || path.posix.isAbsolute(value.replaceAll('\\', '/')) || /^[A-Za-z]:[\\/]/.test(value))) {
      selections.push({ invalid: true });
      continue;
    }
    const joined = value === undefined ? path.posix.join(workspace, 'migrations') :
      typeof value === 'string' && value.length > 0 ? path.posix.join(workspace, value.replaceAll('\\', '/')) : undefined;
    if (!joined || joined.startsWith('/') || joined.split('/').some((part) => part === '..' || isSensitivePath(part))) selections.push({ invalid: true });
    else selections.push({ directory: joined.replace(/^\.\//, ''), invalid: false });
  }
  return selections;
}
