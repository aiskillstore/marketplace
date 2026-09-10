#!/usr/bin/env node
// wind-mcp-skill CLI: thin JSON-envelope wrapper around Wind MCP servers
import { readFileSync, writeFileSync, existsSync, mkdirSync, copyFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, dirname, basename, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawn } from 'node:child_process';

// #region 静态：版本、7 个 MCP 地址、路径、HTTP 状态码映射。只含常量，不发网络。
const SKILL_VERSION = '2.0.4';

// 本地 registry: 工具选择可在任何网络调用前失败
const SERVERS = {
  stock_data: {
    endpoint: 'https://mcp.wind.com.cn/vserver_stock_data/mcp/',
    label: 'Wind 股票（选股筛选 + 档案/财务/股本/事件/技术/风险 + 行情/K线/分钟）',
  },
  fund_data: {
    endpoint: 'https://mcp.wind.com.cn/vserver_fund_data/mcp/',
    label: 'Wind 基金（基金筛选 + 档案/财务/持仓/业绩/持有人/公司 + 行情/K线/分钟）',
  },
  index_data: {
    endpoint: 'https://mcp.wind.com.cn/vserver_index_data/mcp/',
    label: 'Wind 指数/板块（档案/基本面/技术 + 行情/K线/分钟）',
  },
  bond_data: {
    endpoint: 'https://mcp.wind.com.cn/vserver_bond_data/mcp/',
    label: 'Wind 债券（基本档案/发债主体/行情估值/主体财务）',
  },
  financial_docs: {
    endpoint: 'https://mcp.wind.com.cn/vserver_financial_docs/mcp/',
    label: 'Wind 金融文档 RAG（公告 / 新闻）',
  },
  economic_data: {
    endpoint: 'https://mcp.wind.com.cn/vserver_economic_data/mcp/',
    label: 'Wind EDB 宏观/行业经济指标',
  },
  analytics_data: {
    endpoint: 'https://mcp.wind.com.cn/vserver_analytics_data/mcp/',
    label: 'Wind 通用分析数据（NL → Wind 数据）',
  },
};

const PORTAL_URL = 'https://aifinmarket.wind.com.cn/#/user/overview';

const SKILL_DIR = dirname(dirname(fileURLToPath(
  import.meta.url)));

const UPDATE_CHECK_PATH = join(SKILL_DIR, 'scripts', 'update-check.mjs');
const TOOL_MANIFEST_PATH = join(SKILL_DIR, 'scripts', 'tool-manifest.json');
const CALL_RULES_PATH = join(SKILL_DIR, 'scripts', 'call-rules.json');

const SKILL_NAME = basename(SKILL_DIR);

const CALL_EXAMPLES = [
  `cli.mjs call stock_data search_stocks '{"question":"筛选沪深市场市值超500亿且连续5日上涨的股票"}'`,
  `cli.mjs call stock_data search_stocks '{"question":"筛选港股中市值超1000亿港元的科技股"}'`,
  `cli.mjs call fund_data search_funds '{"question":"筛选股票型基金中近一年收益率超20%的产品"}'`,
  `cli.mjs call stock_data get_stock_basicinfo '{"question":"600519.SH公司基本档案"}'`,
  `cli.mjs call stock_data get_stock_price_indicators '{"windcode":"600519.SH","indexes":"中文简称,最新成交价,涨跌幅"}'`,
  `cli.mjs call fund_data get_fund_kline '{"windcode":"588200.SH","begin_date":"2026-04-01","end_date":"2026-04-30"}'`,
  `cli.mjs call stock_data get_stock_quote '{"windcode":"AAPL.O","begin":"2026-08-05","end":"2026-08-05","count":-30}'`,
  `cli.mjs call index_data get_index_kline '{"windcode":"000300.SH","begin_date":"2026-04-01","end_date":"2026-04-30"}'`,
  `cli.mjs call financial_docs get_financial_news '{"query":"美联储利率政策","top_k":3}'`,
  `cli.mjs call economic_data search_economic_indicator '{"question":"中国GDP相关指标有哪些"}'`,
  `cli.mjs call economic_data query_economic_indicator_data '{"question":"中国GDP","observation":"10"}'`,
  `cli.mjs call analytics_data get_financial_data '{"question":"查询中国A股市场过去一年的平均成交量"}'`,
];

const PRICE_INDICATOR_TOOLS = new Set(['get_stock_price_indicators', 'get_fund_price_indicators', 'get_index_price_indicators']);
const QUOTE_TOOLS = new Set(['get_stock_quote', 'get_fund_quote', 'get_index_quote']);

const HTTP_ERROR_MAP = {
  401: 'AUTH_ERROR',
  429: 'RATE_LIMIT_ERROR',
  500: 'NETWORK_ERROR',
  502: 'NETWORK_ERROR',
  503: 'NETWORK_ERROR',
  504: 'NETWORK_ERROR',
};
// #endregion 静态

// #region 自动更新：仅 call 成功后触发；今天已成功则跳过；detached 跑 update-check.mjs，不阻塞取数。

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

function normalizePath(value) {
  const normalized = resolve(value).replace(/\\/g, '/');
  return process.platform === 'win32' ? normalized.toLowerCase() : normalized;
}

function updateScope() {
  const globalRoot = normalizePath(join(homedir(), '.agents', 'skills'));
  const skillDir = normalizePath(SKILL_DIR);
  return skillDir.startsWith(globalRoot + '/') ? 'global' : 'project';
}

function updateStateFile() {
  return join(SKILL_DIR, 'scripts', 'update-state.json');
}

function readUpdateState() {
  try {
    const stateFile = updateStateFile();
    if (!existsSync(stateFile)) return null;
    return JSON.parse(readFileSync(stateFile, 'utf8'));
  } catch {
    return null;
  }
}

function writeUpdateStatePatch(patch) {
  const stateFile = updateStateFile();
  mkdirSync(dirname(stateFile), { recursive: true });
  const state = { ...(readUpdateState() || {}), ...patch };
  writeFileSync(stateFile, JSON.stringify(state, null, 2) + '\n');
}

function alreadyUpdatedToday() {
  try {
    const state = readUpdateState();
    return state && state.date === todayKey() && state.status === 'success';
  } catch {
    return false;
  }
}

function markSkillUsed() {
  writeUpdateStatePatch({
    lastUsedAt: new Date().toISOString(),
    lastUsedPid: process.pid,
  });
}

function triggerUpdateCheck() {
  try {
    if (!existsSync(UPDATE_CHECK_PATH)) return;
    if (alreadyUpdatedToday()) return;
    markSkillUsed();
    const tmpDir = join(homedir(), '.cache', 'wind-aifinmarket');
    mkdirSync(tmpDir, { recursive: true });
    const runnerPath = join(tmpDir, `update-check-${SKILL_NAME}-${process.pid}.mjs`);
    copyFileSync(UPDATE_CHECK_PATH, runnerPath);
    const child = spawn('node', [runnerPath, SKILL_DIR], { detached: true, stdio: 'ignore', windowsHide: true });
    child.on('error', () => { /* ignore spawn failures; update must not block CLI */ });
    child.unref();
  } catch { }
}
// #endregion 自动更新

// #region 信封：成功写 MCP result + cli_meta；失败统一写 {ok:false,code,message}。Agent 只读 stdout。
function normalizeSuccessPayload(value, path = '$', state = { warnings: [], tables: [], invalidPaths: [] }, dataCell = false) {
  if (dataCell && value === 'INVALID') {
    state.invalidPaths.push(path);
    return null;
  }
  if (Array.isArray(value)) {
    return value.map((item, index) => normalizeSuccessPayload(item, `${path}[${index}]`, state, dataCell));
  }
  if (!value || typeof value !== 'object') return value;

  const normalized = {};
  for (const [key, item] of Object.entries(value)) {
    const isStructuredDataArray = Array.isArray(item) && (key === 'rows' || key === 'value');
    normalized[key] = normalizeSuccessPayload(item, `${path}.${key}`, state, dataCell || isStructuredDataArray);
  }
  if (Array.isArray(value.rows)) {
    state.tables.push({ path, actual_row_count: value.rows.length });
  }
  if (Object.hasOwn(value, 'excelTotalCount')) {
    state.warnings.push({
      code: 'UNRELIABLE_DECLARED_COUNT',
      path: `${path}.excelTotalCount`,
      message: 'excelTotalCount 仅保留为后端原始字段，不得据此判断结果总数或完整性。',
    });
  }
  return normalized;
}

// 保留 MCP result 外层兼容性；只清洗可解析的 JSON 文本并附加机器可读安全元数据。
function normalizeCallSuccess(result, context = {}) {
  const output = result && typeof result === 'object' ? structuredClone(result) : result;
  const state = { warnings: [], tables: [], invalidPaths: [] };
  if (output && Array.isArray(output.content)) {
    for (const item of output.content) {
      if (item?.type !== 'text' || typeof item.text !== 'string') continue;
      try {
        const parsed = JSON.parse(item.text);
        item.text = JSON.stringify(normalizeSuccessPayload(parsed, '$', state));
      } catch {
        // 非 JSON 文本按后端原文透传。
      }
    }
  }
  if (state.invalidPaths.length) {
    state.warnings.push({
      code: 'BACKEND_INVALID_AS_NULL',
      count: state.invalidPaths.length,
      paths: state.invalidPaths.slice(0, 100),
      truncated: state.invalidPaths.length > 100,
      message: '结构化数据区中的后端字符串 INVALID 已转换为 null；表示缺失或不适用，禁止按 0 参与计算。',
    });
  }
  if (output && typeof output === 'object') {
    output.cli_meta = {
      schema_version: '1.0',
      server_type: context.server_type || null,
      tool_name: context.tool_name || null,
      completeness: state.warnings.some(warning => warning.code === 'UNRELIABLE_DECLARED_COUNT') ? 'unknown' : 'not_asserted',
      tables: state.tables,
      warnings: state.warnings,
    };
  }
  return output;
}

function writeRawCallSuccess(result, context = {}) {
  process.stdout.write(JSON.stringify(normalizeCallSuccess(result, context), null, 2) + '\n');
}

function writePlainSuccess(data) {
  process.stdout.write(JSON.stringify(data, null, 2) + '\n');
}

const DEFAULT_ERROR_MESSAGES = Object.freeze({
  AUTH_ERROR: '认证失败，请检查 API Key',
  PARAM_TYPE_ERROR: '参数类型错误，请检查字段类型',
  USAGE_ERROR: '命令用法错误，请检查输入参数',
  PARAMS_FILE_ERROR: '参数文件读取失败，请检查文件路径和内容',
  INVALID_PARAMS_JSON: '参数格式错误，params 必须是 JSON 对象',
  ROUTE_ERROR: '工具路由失败，请检查 server_type 和 tool_name',
  PARAM_VALIDATION_ERROR: '参数校验失败，请检查字段名和取值',
  PARAM_CONFLICT_ERROR: '参数存在冲突，请检查输入组合',
  RATE_LIMIT_ERROR: '请求过于频繁，请稍后重试',
  NETWORK_ERROR: '服务暂时不可用，请稍后重试',
  TOOL_RUNTIME_ERROR: '响应解析失败，请稍后重试',
  SETUP_ERROR: '本地配置缺失或无效，请检查技能配置',
  UNKNOWN: '调用失败，请稍后重试',
});

const MAPPED_ERROR_MESSAGE_CODES = new Set(
  Object.keys(DEFAULT_ERROR_MESSAGES).filter((code) => code !== 'UNKNOWN'),
);

function normalizeErrorMessage(code, detail, metadata = {}) {
  if (!MAPPED_ERROR_MESSAGE_CODES.has(code)) {
    if (typeof metadata.error_message === 'string' && metadata.error_message.trim()) {
      return metadata.error_message.trim();
    }
    if (typeof detail === 'string' && detail.trim()) {
      return detail.trim().slice(0, 2000);
    }
    return DEFAULT_ERROR_MESSAGES.UNKNOWN;
  }
  if (typeof detail === 'string' && detail.trim()) {
    return detail.trim().slice(0, 500);
  }
  return DEFAULT_ERROR_MESSAGES[code] || DEFAULT_ERROR_MESSAGES.UNKNOWN;
}

function writeErrorEnvelope(code, detail, metadata = {}) {
  const envelope = {
    ok: false,
    code,
    message: normalizeErrorMessage(code, detail, metadata),
  };
  process.stdout.write(JSON.stringify(envelope, null, 2) + '\n');
}

function die(code, detail = null, exitCode = 1, metadata = {}) {
  writeErrorEnvelope(code, detail, metadata);
  process.exit(exitCode);
}

function exitWithUsage(usage, exitCode = 0) {
  die('USAGE_ERROR', `USAGE:\n${usage}`, exitCode);
}
// #endregion 信封

// #region 认证：Key 顺序为 ~/.wind-aifinmarket/config > skill config.json > 环境变量 WIND_API_KEY。
function maskKey(key) {
  if (!key || key.length < 8) return '***';
  return key.slice(0, 4) + '***' + key.slice(-4);
}

// dotenv 解析: 兼容注释 / 引号 / export 前缀
function parseDotenv(content) {
  const env = {};
  for (const rawLine of content.split('\n')) {
    let line = rawLine.replace(/^\uFEFF/, '').trim();
    if (!line || line.startsWith('#')) continue;
    if (line.startsWith('export ')) line = line.slice(7).trim();
    const eq = line.indexOf('=');
    if (eq <= 0) continue;
    const key = line.slice(0, eq).trim();
    let val = line.slice(eq + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    } else {
      const hashIdx = val.indexOf(' #');
      if (hashIdx >= 0) val = val.slice(0, hashIdx).trim();
    }
    env[key] = val;
  }
  return env;
}

function getApiKey() {
  const globalConfig = join(homedir(), '.wind-aifinmarket', 'config');
  if (existsSync(globalConfig)) {
    try {
      const env = parseDotenv(readFileSync(globalConfig, 'utf8'));
      const key = env.WIND_API_KEY?.trim();
      if (key) return key;
    } catch { }
  }

  const localConfig = join(SKILL_DIR, 'config.json');
  if (existsSync(localConfig)) {
    try {
      const cfg = JSON.parse(readFileSync(localConfig, 'utf8'));
      const key = typeof cfg.wind_api_key === 'string' ? cfg.wind_api_key.trim() : '';
      if (key) return key;
    } catch { }
  }

  const envKey = process.env.WIND_API_KEY?.trim();
  if (envKey) return envKey;

  die('AUTH_ERROR', 'WIND_API_KEY 未配置（CLI 已完整检查：用户全局配置 > Skill 本地配置 > 环境变量）');
}
// #endregion 认证

// #region 路由：校验 server_type、tool_name 是否在 SERVERS 与 tool-manifest.json。非法则 ROUTE_ERROR。
function getServer(server_type) {
  const server = SERVERS[server_type];
  if (!server) {
    die('ROUTE_ERROR', `未知 server_type: ${server_type}. 可用: ${Object.keys(SERVERS).join(' / ')}`);
  }
  return server;
}

function loadToolManifest() {
  try {
    // tool-manifest.json is the authority for legal server_type + tool_name combinations.
    const manifest = JSON.parse(readFileSync(TOOL_MANIFEST_PATH, 'utf8'));
    if (!manifest || typeof manifest !== 'object' || Array.isArray(manifest)) {
      throw new Error('manifest 顶层必须是对象');
    }
    for (const [serverType, tools] of Object.entries(manifest)) {
      if (!SERVERS[serverType]) {
        throw new Error(`manifest 包含未知 server_type: ${serverType}`);
      }
      if (!Array.isArray(tools) || tools.some(tool => typeof tool !== 'string' || !tool)) {
        throw new Error(`manifest 中 ${serverType} 的工具清单必须是非空字符串数组`);
      }
    }
    for (const serverType of Object.keys(SERVERS)) {
      if (!Array.isArray(manifest[serverType])) {
        throw new Error(`manifest 缺少 server_type: ${serverType}`);
      }
    }
    return manifest;
  } catch (err) {
    die('UNKNOWN', `工具清单读取失败: ${err.message}`);
  }
}

function validateToolSelection(server_type, toolName) {
  getServer(server_type);
  const manifest = loadToolManifest();
  const tools = manifest[server_type];
  if (!tools.includes(toolName)) {
    die('ROUTE_ERROR', `工具名 "${toolName}" 不属于 server_type "${server_type}"。`);
  }
}
// #endregion 路由

// #region 规则加载：读 call-rules.json，得到 K 线周期映射、按域改写工具名、参数校验规则。
function readCallRules() {
  try {
    return JSON.parse(readFileSync(CALL_RULES_PATH, 'utf8'));
  } catch (err) {
    die('UNKNOWN', `调用规则读取失败: ${err.message}`);
  }
}

function prepareNormalizationRules(rules) {
  return {
    klinePeriodMap: new Map(Object.entries(rules.kline_period_map || {})),
    toolByDomain: rules.tool_by_domain || {},
  };
}

const CALL_RULES = readCallRules();
const NORMALIZATION_RULES = prepareNormalizationRules(CALL_RULES);
const KLINE_PERIOD_MAP = NORMALIZATION_RULES.klinePeriodMap;
const PUBLIC_KLINE_PERIODS = new Set(KLINE_PERIOD_MAP.keys());
const KLINE_PERIODS = new Set(KLINE_PERIOD_MAP.values());
const TOOL_BY_DOMAIN = NORMALIZATION_RULES.toolByDomain;

const TOOL_VALIDATION_RULES = {
  basic: CALL_RULES.basic || {},
  toolRules: Array.isArray(CALL_RULES.tool_rules) ? CALL_RULES.tool_rules : [],
};
const KLINE_TOOLS = new Set(TOOL_VALIDATION_RULES.toolRules.find(rule => rule.name === 'kline')?.tools || []);
// #endregion 规则加载

// #region 规范化：整理 windcode/indexes/period。不给中文名称猜交易所后缀。
function normalizeIndexes(indexes) {
  if (typeof indexes !== 'string') return indexes;
  return indexes.split(',').map((item) => item.trim()).filter(Boolean).join(',');
}

function normalizeWindcode(windcode) {
  if (typeof windcode !== 'string') return windcode;
  const raw = windcode.trim();
  const upper = raw.toUpperCase();
  // Keep natural-language names untouched. Wind's backend NER is responsible
  // for resolving names/aliases; the CLI must not guess exchange suffixes.
  if (/[\u4e00-\u9fff]/.test(raw)) return raw;
  if (/^0\d{4}\.HK$/.test(upper)) return upper.slice(1);
  if (/^\d{4}\.HK$/.test(upper)) return upper;
  if (/^\d{6}\.(SH|SZ|BJ|OF)$/.test(upper)) return upper;
  if (/^[A-Z]{1,5}\.(O|N|A|HK|SH|SZ|BJ)$/.test(upper)) return upper;
  return raw;
}

function toolFamily(toolName) {
  if (PRICE_INDICATOR_TOOLS.has(toolName)) return 'price';
  if (KLINE_TOOLS.has(toolName)) return 'kline';
  if (QUOTE_TOOLS.has(toolName)) return 'quote';
  return null;
}

function normalizeCall(server_type, toolName, args) {
  const family = toolFamily(toolName);
  if (family) toolName = TOOL_BY_DOMAIN[family]?.[server_type] || toolName;
  const normalizedArgs = { ...args };
  const normalizationErrors = [];
  if (typeof normalizedArgs.indexes === 'string') normalizedArgs.indexes = normalizeIndexes(normalizedArgs.indexes);
  if (typeof normalizedArgs.windcode === 'string') normalizedArgs.windcode = normalizeWindcode(normalizedArgs.windcode);
  // count 是整型字段：把整数字符串收敛成 number，非整数原样留给 patterns 校验拦截。
  if (typeof normalizedArgs.count === 'string' && /^-?\d+$/.test(normalizedArgs.count.trim())) {
    normalizedArgs.count = Number(normalizedArgs.count.trim());
  }
  if (KLINE_TOOLS.has(toolName) && normalizedArgs.period === undefined) normalizedArgs.period = '1d';
  if (typeof normalizedArgs.period === 'string') {
    const key = normalizedArgs.period.trim();
    const backendPeriod = KLINE_PERIOD_MAP.get(key);
    normalizedArgs.period = backendPeriod || key;
    if (!backendPeriod && KLINE_PERIODS.has(key)) {
      normalizationErrors.push({
        message: `字段 'period' 只能是 ${Array.from(PUBLIC_KLINE_PERIODS).join('/')}，日 K 请传 '1d'`,
        field: 'period',
        issue: 'invalid_enum',
        actual: key,
        allowed_values: Array.from(PUBLIC_KLINE_PERIODS),
      });
    }
  }
  return { server_type, toolName, args: normalizedArgs, normalizationErrors };
}
// #endregion 规范化

// #region 校验：按 call-rules 查必填、枚举、成对/互斥字段、日期顺序。发网络前拦住非法参数。
function validateBasicParams(params) {
  const errors = [];
  if (!params || typeof params !== 'object' || Array.isArray(params)) {
    return [{
      code: 'PARAM_TYPE_ERROR',
      message: 'params 必须是 JSON object',
      field: 'params',
      issue: 'invalid_type',
      expected_type: 'object',
      actual_type: Array.isArray(params) ? 'array' : typeof params,
    }];
  }

  const basic = TOOL_VALIDATION_RULES.basic;
  for (const key of basic.string_keys || []) {
    if (!(key in params)) continue;
    if (typeof params[key] !== 'string') {
      errors.push({ message: `字段 '${key}' 必须是字符串`, field: key, issue: 'invalid_type', expected_type: 'string', actual_type: Array.isArray(params[key]) ? 'array' : typeof params[key] });
    } else if (params[key].trim().length === 0) {
      errors.push({ message: `字段 '${key}' 不能为空或全空白`, field: key, issue: 'empty_value', expected: 'non-empty string' });
    }
  }
  return errors;
}

function hasParamValue(params, key) {
  return params[key] !== undefined && params[key] !== null && params[key] !== '';
}

function resolveValidationValues(fieldRule) {
  if (Array.isArray(fieldRule.values)) return fieldRule.values.map(String);
  if (fieldRule.values_from === 'kline_period_map') return Array.from(KLINE_PERIODS).map(String);
  return [];
}

function resolveValidationDisplayValues(fieldRule) {
  if (fieldRule.values_from === 'kline_period_map') return Array.from(PUBLIC_KLINE_PERIODS).map(String);
  return resolveValidationValues(fieldRule);
}

function renderValidationMessage(template, values) {
  return String(template || '').replace('${values}', values.join('/'));
}

function validationErrorMessage(error) {
  return typeof error === 'string' ? error : error.message;
}

function validationErrorCode(error) {
  return typeof error === 'object' && error?.code ? error.code : null;
}

function validateToolParams(toolName, params) {
  const errors = [];
  const rules = TOOL_VALIDATION_RULES.toolRules.filter(rule => Array.isArray(rule.tools) && rule.tools.includes(toolName));

  for (const rule of rules) {
    const ruleLabel = rule.label || rule.name || toolName;
    if (Array.isArray(rule.allowed)) {
      const allowedKeys = new Set(rule.allowed);
      for (const key of Object.keys(params)) {
        if (!allowedKeys.has(key)) errors.push({ message: `${ruleLabel} 工具不支持字段 '${key}'`, field: key, issue: 'unknown_field', allowed_fields: [...allowedKeys] });
      }
    }

    for (const key of rule.required || []) {
      if (!hasParamValue(params, key)) errors.push({ message: `${ruleLabel} 工具缺少必填字段 '${key}'`, field: key, issue: 'missing_required', required_fields: rule.required || [] });
    }

    for (const [field, fieldRule] of Object.entries(rule.enum_fields || {})) {
      if (!(field in params)) continue;
      const values = resolveValidationValues(fieldRule);
      if (!values.includes(String(params[field]))) {
        const displayValues = resolveValidationDisplayValues(fieldRule);
        errors.push({ message: renderValidationMessage(fieldRule.message, displayValues), field, issue: 'invalid_enum', actual: params[field], allowed_values: displayValues });
      }
    }

    for (const fields of rule.paired || []) {
      const present = fields.filter(key => hasParamValue(params, key));
      if (present.length > 0 && present.length < fields.length) {
        errors.push({ message: `字段 '${fields.join("' 和 '")}' 应成对填写`, fields, issue: 'incomplete_pair', expected_fields: fields });
      }
    }

    for (const fields of rule.mutually_exclusive || []) {
      const present = fields.filter(key => hasParamValue(params, key));
      if (present.length > 1) {
        errors.push({ message: `字段 '${fields.join('/')}' 互斥，不应同时填写`, fields, issue: 'mutually_exclusive' });
      }
    }

    for (const [startKey, endKey] of rule.ordered_dates || []) {
      if (params[startKey] && params[endKey] && params[startKey] > params[endKey]) {
        errors.push({ message: `字段 '${startKey}' 不能晚于 '${endKey}'`, fields: [startKey, endKey], issue: 'invalid_order', expected: `${startKey} <= ${endKey}` });
      }
    }

    for (const [field, patternRule] of Object.entries(rule.patterns || {})) {
      if (!(field in params)) continue;
      const pattern = new RegExp(patternRule.pattern);
      if (!pattern.test(String(params[field]))) {
        errors.push({ message: patternRule.message || `字段 '${field}' 格式不合法`, field, issue: 'invalid_format', actual: params[field], expected_pattern: patternRule.pattern });
      }
    }

    for (const conditional of rule.required_one_of_when || []) {
      if (!conditional.values?.map(String).includes(String(params[conditional.field]))) continue;
      const satisfied = conditional.one_of?.some(group => group.every(key => hasParamValue(params, key)));
      if (!satisfied) errors.push({ message: conditional.message || `字段 '${conditional.field}' 当前取值缺少配套参数`, field: conditional.field, issue: 'missing_conditional_fields', one_of: conditional.one_of });
    }

    for (const requirement of rule.required_one_of || []) {
      const satisfied = requirement.one_of?.some(group => group.every(key => hasParamValue(params, key)));
      if (!satisfied) errors.push({ message: requirement.message || `${ruleLabel} 工具缺少一组必填字段`, issue: 'missing_one_of', one_of: requirement.one_of });
    }
  }
  return errors;
}
// #endregion 校验

// #region MCP：裸 HTTP JSON-RPC + SSE。先 initialize 再 tools/call。本地/网络错误由 CLI 收口，接口错误统一 backend_error。
function parseSSE(text) {
  const trimmed = text.trim();
  // 后端正常 SSE, 部分错误场景纯 JSON
  if (trimmed.startsWith('{')) {
    try {
      return JSON.parse(trimmed);
    } catch { }
  }
  const lines = text.split(/\r?\n/);
  let last = null;
  for (const line of lines) {
    if (line.startsWith('data: ')) last = line.slice(6);
  }
  if (last) {
    try {
      return JSON.parse(last);
    } catch (e) {
      throw new Error(`SSE data 行 JSON 解析失败：${e.message}。原文前 200 字符：${text.slice(0, 200)}`);
    }
  }
  throw new Error(`响应格式无法识别（既非 SSE 也非纯 JSON）。原文前 200 字符：${text.slice(0, 200)}`);
}

async function fetchWithRetry(fetchFn, url, optionsOrFactory, {
  attempts = 3,
  delaysMs = [300, 1000],
  onAttemptError = null,
} = {}) {
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      const options = typeof optionsOrFactory === 'function'
        ? optionsOrFactory(attempt)
        : optionsOrFactory;
      return await fetchFn(url, options);
    } catch (err) {
      lastError = err;
      onAttemptError?.(err, attempt, attempts);
      const delayMs = delaysMs[Math.min(attempt - 1, delaysMs.length - 1)] || 0;
      if (attempt < attempts && delayMs > 0) {
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
  }
  throw lastError;
}

async function mcpRequest(server_type, method, params, {
  timeoutMs = 60_000,
} = {}) {
  const server = getServer(server_type);
  const apiKey = getApiKey();
  const headers = {
    Authorization: `Bearer ${apiKey}`,
    Accept: 'application/json, text/event-stream',
    'Content-Type': 'application/json',
  };

  const body = JSON.stringify({
    jsonrpc: '2.0',
    id: Date.now(),
    method,
    params
  });
  const dieInterfaceError = (message) => {
    die('backend_error', null, 1, {
      error_message: String(message ?? '').slice(0, 2000),
    });
  };
  let resp;
  try {
    resp = await fetchWithRetry(
      fetch,
      server.endpoint,
      () => ({
        method: 'POST',
        headers,
        body,
        signal: AbortSignal.timeout(timeoutMs),
      }),
      {
        attempts: 3,
        delaysMs: [300, 1000],
        onAttemptError: process.env.WIND_DEBUG === '1'
          ? (err, attempt, total) => {
            const causeCode = err?.cause?.code || err?.code || 'UNKNOWN_CAUSE';
            process.stderr.write(`[wind-mcp fetch retry ${attempt}/${total}] ${causeCode}: ${err?.message || err}\n`);
          }
          : null,
      },
    );
  } catch {
    die('NETWORK_ERROR');
  }

  if (!resp.ok) {
    await resp.text().catch(() => '');
    die(HTTP_ERROR_MAP[resp.status] || 'NETWORK_ERROR');
  }

  const text = await resp.text();
  let payload;
  try {
    payload = parseSSE(text);
  } catch (err) {
    die('TOOL_RUNTIME_ERROR', `${err.message} (server=${server_type})`);
  }

  if (payload.error) {
    const msg = typeof payload.error === 'string'
      ? payload.error
      : (payload.error.message || JSON.stringify(payload.error));
    dieInterfaceError(msg);
  }

  if (payload.result?.isError) {
    const msg = payload.result.content?.[0]?.text || JSON.stringify(payload.result);
    dieInterfaceError(msg);
  }

  // 部分工具把业务错误包在 content[0].text 的 JSON 字符串里, 必须二次解析
  const innerText = payload.result?.content?.[0]?.text;
  if (typeof innerText === 'string') {
    let inner;
    try {
      inner = JSON.parse(innerText);
    } catch {
      inner = null;
    }
    if (inner) {
      if (typeof inner.mcp_tool_error_code === 'number' && inner.mcp_tool_error_code !== 0) {
        const msg = inner.mcp_tool_error_msg || JSON.stringify(inner);
        dieInterfaceError(msg);
      }
      if (inner.error && (inner.error.code || inner.error.message)) {
        const errorMessage = inner.error.message || JSON.stringify(inner.error);
        dieInterfaceError(errorMessage);
      }
      if (inner?.data && typeof inner.data === 'object') {
        const numericCode = typeof inner.data.code === 'number'
          ? inner.data.code
          : (typeof inner.data.code === 'string' && /^\d+$/.test(inner.data.code.trim()) ? Number(inner.data.code) : null);
        const isSuccessCode = numericCode === 0
          || (numericCode !== null && numericCode >= 200 && numericCode < 300);
        if (numericCode !== null && !isSuccessCode) {
          dieInterfaceError(typeof inner.data.message === 'string' ? inner.data.message : JSON.stringify(inner.data));
        }
      }
    }
  }
  return payload.result;
}

async function mcpInitializeAndCall(server_type, method, params) {
  await mcpRequest(server_type, 'initialize', {
    protocolVersion: '2025-03-26',
    capabilities: {},
    clientInfo: {
      name: SKILL_NAME,
      version: SKILL_VERSION
    },
  }, {
    timeoutMs: 30_000
  });

  return mcpRequest(server_type, method, params, {
    timeoutMs: 600_000,
  });
}
// #endregion MCP

// #region 命令：call 取数；list-tools 拉 schema；setup-key / open-portal 配 Key；diagnose 看更新状态。
function loadParamsInput(paramsInput) {
  if (!paramsInput.startsWith('@')) {
    return { jsonText: paramsInput, source: 'inline' };
  }

  const fileArg = paramsInput.slice(1);
  if (!fileArg) {
    const error = new Error('@file 缺少文件路径');
    error.code = 'PARAMS_FILE_ERROR';
    error.file = fileArg;
    throw error;
  }

  const filePath = resolve(process.cwd(), fileArg);
  try {
    const jsonText = readFileSync(filePath, 'utf8').replace(/^\uFEFF/, '');
    return { jsonText, source: 'file', filePath };
  } catch (cause) {
    const error = new Error(`无法读取 params 文件：${filePath} (${cause.code || cause.message})`);
    error.code = 'PARAMS_FILE_ERROR';
    error.file = filePath;
    error.cause = cause;
    throw error;
  }
}

async function cmdCall(server_type, toolName, paramsInput) {
  if (!server_type || !toolName || !paramsInput) {
    exitWithUsage(
      `用法：call <server_type> <tool_name> '<params_json>|@params_file'\n` +
      `可用 server_type: ${Object.keys(SERVERS).join(' / ')}\n` +
      `典型：\n  ${CALL_EXAMPLES.join('\n  ')}`,
      1,
    );
  }

  let paramsSource;
  try {
    paramsSource = loadParamsInput(paramsInput);
  } catch (e) {
    die('PARAMS_FILE_ERROR', e.message);
  }

  let args;
  try {
    args = JSON.parse(paramsSource.jsonText);
  } catch (e) {
    const sourceDetail = paramsSource.source === 'file'
      ? `文件：${paramsSource.filePath}`
      : `原文：${paramsSource.jsonText.slice(0, 200)}`;
    die('INVALID_PARAMS_JSON', `params JSON 解析失败：${e.message} | ${sourceDetail}`);
  }

  if (!args || typeof args !== 'object' || Array.isArray(args)) {
    die('PARAM_TYPE_ERROR', 'params 必须是 JSON object');
  }

  let normalizationErrors;
  ({ server_type, toolName, args, normalizationErrors } = normalizeCall(server_type, toolName, args));
  validateToolSelection(server_type, toolName);

  const validationErrors = [...normalizationErrors, ...validateBasicParams(args)];
  const paramsShapeInvalid = validationErrors.some(error => validationErrorCode(error) === 'PARAM_TYPE_ERROR' && error.field === 'params');
  if (!paramsShapeInvalid) validationErrors.push(...validateToolParams(toolName, args));
  if (validationErrors.length > 0) {
    const explicitCode = validationErrors.map(validationErrorCode).find(Boolean);
    const messages = validationErrors.map(validationErrorMessage);
    const hasTypeError = validationErrors.some(error => typeof error === 'object' && error?.issue === 'invalid_type');
    die(explicitCode || (hasTypeError ? 'PARAM_TYPE_ERROR' : 'PARAM_VALIDATION_ERROR'), messages.join('；'));
  }

  const result = await mcpInitializeAndCall(server_type, 'tools/call', {
    name: toolName,
    arguments: args,
    _meta: { clientVersion: SKILL_VERSION },
  });
  return {
    server_type,
    tool: toolName,
    result,
  };
}

async function cmdListTools(server_type) {
  if (!server_type) {
    exitWithUsage(
      `用法：list-tools <server_type>\n` +
      `可用 server_type: ${Object.keys(SERVERS).join(' / ')}`,
      1,
    );
  }
  getServer(server_type);
  const result = await mcpInitializeAndCall(server_type, 'tools/list', {});
  return { server_type, ...result };
}

async function cmdSetupKey(...rawArgs) {
  const key = rawArgs[0];

  if (!key || key.startsWith('--')) {
    exitWithUsage(
      `用法：cli.mjs setup-key <KEY> --scope <global|skill>\n\n` +
      `scope: global=全局共享；skill=仅当前 skill。调用前先让用户选择。`,
      1,
    );
  }

  let scope = null;
  for (let i = 1; i < rawArgs.length; i++) {
    const a = rawArgs[i];
    if (a === '--scope' && rawArgs[i + 1]) {
      scope = rawArgs[i + 1];
      break;
    }
    if (a.startsWith('--scope=')) {
      scope = a.slice(8);
      break;
    }
  }

  if (!scope) {
    exitWithUsage(
      `setup-key 缺 --scope 参数。\n\n` +
      `先让用户选择 global 或 skill，再重试：cli.mjs setup-key ${maskKey(key)} --scope <global|skill>`,
      1,
    );
  }

  if (!['global', 'skill'].includes(scope)) {
    die('SETUP_ERROR', `setup-key 未知 scope: ${scope} (可选: global / skill)`);
  }

  let file;
  try {
    if (scope === 'global') {
      const dir = join(homedir(), '.wind-aifinmarket');
      if (!existsSync(dir)) mkdirSync(dir, {
        recursive: true
      });
      file = join(dir, 'config');
      let lines = [];
      if (existsSync(file)) {
        lines = readFileSync(file, 'utf8').split('\n')
          .filter(l => l.length > 0 && !/^\s*(export\s+)?WIND_API_KEY\s*=/.test(l));
      }
      lines.push(`WIND_API_KEY=${key}`);
      writeFileSync(file, lines.join('\n') + '\n', {
        mode: 0o600
      });
    } else {
      file = join(SKILL_DIR, 'config.json');
      writeFileSync(file, JSON.stringify({ wind_api_key: key }, null, 2) + '\n', { mode: 0o600 });
    }
  } catch (err) {
    die('SETUP_ERROR', `配置写入失败 (scope=${scope}, path=${file || 'n/a'}): ${err.message}`);
  }

  return {
    scope,
    path: file,
    key_masked: maskKey(key),
    next: '现在可以重试原 Wind 调用',
  };
}

async function cmdOpenPortal() {
  const platform = process.platform;
  let bin, args;
  if (platform === 'darwin') {
    bin = 'open';
    args = [PORTAL_URL];
  } else if (platform === 'win32') {
    bin = 'cmd';
    args = ['/c', 'start', '', PORTAL_URL];
  } else {
    bin = 'xdg-open';
    args = [PORTAL_URL];
  }

  let spawnError = null;
  try {
    const child = spawn(bin, args, {
      stdio: 'ignore',
      detached: true,
      windowsHide: true
    });
    child.unref();
    spawnError = await new Promise((resolve) => {
      child.once('error', resolve);
      setTimeout(() => resolve(null), 300);
    });
  } catch (err) {
    spawnError = err;
  }

  const data = {
    url: PORTAL_URL,
    platform,
    spawn_command: `${bin} ${args.join(' ')}`,
    flow_note: '未登录时会自动跳转到登录页（/#/login）；登录完成后回到 overview 页面即可获取 API Key。',
    fallback_message: `如果浏览器没有自动弹出，请手动访问：${PORTAL_URL}`,
  };
  if (spawnError) {
    die('SETUP_ERROR', `本地无法启动浏览器: ${spawnError.message} | 用户应手动打开 ${data.url}`);
  }
  return data;
}

// 诊断: 输出自动更新状态
async function cmdDiagnose() {
  let updateState = null;
  try {
    const stateFile = updateStateFile();
    if (existsSync(stateFile)) {
      updateState = JSON.parse(readFileSync(stateFile, 'utf8'));
    }
  } catch {
    updateState = { status: 'unreadable' };
  }
  return {
    platform: process.platform,
    node_pid: process.pid,
    update_scope: updateScope(),
    update_state_file: updateStateFile(),
    update_state: updateState,
    next_update_needed: !alreadyUpdatedToday(),
  };
}
// #endregion 命令

// #region 主入口：IS_MAIN 避免测试 import 时跑副作用。无参打 USAGE；仅 call 成功才触发更新检查。
const IS_MAIN = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;

if (IS_MAIN) runMain();

function runMain() {
  const [cmd, ...args] = process.argv.slice(2);

  const USAGE =
    `wind-mcp-skill\n` +
    `访问万得 Wind 金融数据（按数据域分类调用）\n\n` +
    `用法:\n` +
    `  cli.mjs call <server_type> <tool_name> '<params_json>|@params_file'\n` +
    `  cli.mjs list-tools <server_type>                    # 获取后端官方工具描述和 inputSchema\n` +
    `  cli.mjs open-portal                                # 打开万得开发者中心拿 API Key\n` +
    `  cli.mjs setup-key <KEY> --scope <global|skill>     # 配置 API Key（先问用户存放位置）\n\n` +
    `可用 server_type:\n` +
    Object.entries(SERVERS).map(([k, v]) => `  ${k.padEnd(20)}${v.label}`).join('\n') + '\n\n' +
    `典型:\n` +
    `  ${CALL_EXAMPLES.join('\n  ')}`;

  const commands = {
    call: () => cmdCall(args[0], args[1], args[2]),
    'list-tools': () => cmdListTools(args[0]),
    'open-portal': () => cmdOpenPortal(),
    'setup-key': () => cmdSetupKey(...args),
    diagnose: () => cmdDiagnose(),
  };

  if (!cmd) {
    // help: 直接输出 USAGE 纯文本
    process.stdout.write(USAGE + '\n');
    process.exit(0);
  }

  if (!commands[cmd]) {
    die('USAGE_ERROR', `未知命令: ${cmd}\nUSAGE:\n${USAGE}`);
  }

  commands[cmd]()
    .then((data) => {
      if (cmd === 'call') {
        // call: 透传 result 内容 (parse JSON if applicable, else raw text)
        writeRawCallSuccess(data?.result, { server_type: data?.server_type, tool_name: data?.tool });
        setTimeout(triggerUpdateCheck, 0);
      } else {
        // open-portal / setup-key: 直接输出结构化数据 (无 envelope 包裹)
        writePlainSuccess(data);
      }
    })
    .catch((err) => {
      die('UNKNOWN', `执行失败: ${err.message || err}${err.stack ? ' | stack: ' + err.stack.slice(0, 300) : ''}`);
    });
}
// #endregion 主入口
