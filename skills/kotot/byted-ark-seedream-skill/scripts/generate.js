#!/usr/bin/env node

/**
 * @license MIT
 * @copyright 2026 VolcEngine / AgentPlan
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// ============================================
// 🎨 提示词优化模块
// ============================================

const STYLE_PRESETS = {
  '电影风': '好莱坞大片质感, 电影级光影, 杜比视界, 宽画幅, 极致细节',
  '二次元': '新海诚风格, 日系动漫, 精美原画, 高饱和度, 清澈光影',
  '插画风': '扁平插画风格, 莫兰迪色系, 简洁线条, 矢量感, 艺术设计',
  '写实风': '专业摄影, 索尼A7R5, f/1.8大光圈, RAW格式, 超写实, 细节锐利',
  '国潮风': '国潮插画风格, 中国传统元素, 金色点缀, 工笔画质感, 精致线条',
  '赛博朋克': '赛博朋克2077风格, 霓虹灯光, 高科技低生活, 雨天, 未来感',
  '水彩风': '水彩画风格, 透明质感, 晕染效果, 艺术纸张纹理, 清新',
  '3D渲染': 'Octane渲染, 3D立体, 光线追踪, 次表面散射, PBR材质, 极致写实',
  '暗黑风': '暗黑美学, 高对比度, 暗色调, 神秘氛围, 电影质感',
  '治愈系': '治愈系风格, 温暖明亮, 可爱, 吉卜力质感, 柔和光线'
};

const BASE_ENHANCEMENTS = '电影质感, 高分辨率, 细节丰富, 专业摄影, 构图精美, 色彩协调';

/**
 * 解析 boolean（支持 boolean 类型和字符串 'true'/'false'）
 */
function parseBoolean(val) {
  if (typeof val === 'boolean') return val;
  return val === 'true' || val === true;
}

/**
 * 🐛 Bug 10 修复：安全解析参考图 JSON，带错误处理
 */
function parseReferenceImages(jsonStr) {
  if (!jsonStr) return [];
  
  // 尝试 1: JSON 字符串数组格式
  try {
    const parsed = JSON.parse(jsonStr);
    if (Array.isArray(parsed)) {
      return parsed.map(url => String(url).trim()).filter(Boolean);
    }
  } catch (e) {
    // JSON 解析失败，尝试逗号分隔格式
  }
  
  // 尝试 2: 单个 base64 data URI（必须放在逗号 split 前面，因为 data URI 自带逗号）
  if (typeof jsonStr === 'string') {
    const trimmed = jsonStr.trim().replace(/^["']|["']$/g, '');
    if (trimmed.startsWith('data:image/')) {
      return [trimmed];
    }
  }
  
  // 尝试 3: 逗号分隔的 URL 列表（兼容 CLI 简单传参）
  if (typeof jsonStr === 'string' && jsonStr.includes(',')) {
    return jsonStr.split(',').map(url => url.trim()).filter(Boolean);
  }
  
  // 尝试 4: 单个 URL（去掉引号）
  if (typeof jsonStr === 'string') {
    const trimmed = jsonStr.trim().replace(/^["']|["']$/g, '');
    if (trimmed.startsWith('http') || trimmed.startsWith('data:image/')) {
      return [trimmed];
    }
  }
  
  throw new Error(
    `参考图参数格式错误。支持两种格式：\n` +
    `  1. JSON 数组字符串: --reference_images '["https://a.png", "https://b.png"]'\n` +
    `  2. 逗号分隔: --reference_images "https://a.png,https://b.png"`
  );
}

/**
 * 检测用户输入中的风格关键词
 */
function detectStyle(prompt) {
  const lower = prompt.toLowerCase();
  for (const [style, keywords] of Object.entries({
    '电影风': ['电影', '大片', 'cinematic', '好莱坞'],
    '二次元': ['二次元', '动漫', 'anime', '漫画'],
    '插画风': ['插画', '手绘', 'illustration', '扁平'],
    '写实风': ['照片', '写实', 'photograph', '摄影'],
    '国潮风': ['国潮', '国风', '中国风', '传统'],
    '赛博朋克': ['赛博', 'cyberpunk', '朋克', '霓虹'],
    '水彩风': ['水彩', 'watercolor', '手绘'],
    '3D渲染': ['3d', 'oc', '渲染', 'octane', '三维'],
    '暗黑风': ['暗黑', '哥特', 'dark', '黑暗'],
    '治愈系': ['治愈', '温馨', '可爱', 'cute', '温暖']
  })) {
    if (keywords.some(k => lower.includes(k))) {
      return style;
    }
  }
  return null;
}

/**
 * 优化提示词（区分单张图/连贯图模式）
 */
function optimizePrompt(prompt, enable = true, isSequential = false) {
  if (!enable) {
    return {
      original: prompt,
      optimized: prompt,
      style: null,
      enabled: false,
      mode: isSequential ? 'sequential' : 'single',
      applied: []
    };
  }
  
  const detectedStyle = detectStyle(prompt);
  let optimized = prompt;
  const applied = [];
  
  if (isSequential) {
    // 🎨 连贯图模式优化策略：强调风格统一性、一致性
    optimized += ', 统一画风, 相同角色, 系列插画, 风格一致, 色彩协调';
    applied.push('连贯图：统一风格约束');
    
    if (detectedStyle) {
      optimized += `, ${STYLE_PRESETS[detectedStyle]}`;
      applied.push(`风格: ${detectedStyle}`);
    }
  } else {
    // 🖼️ 单张图模式优化策略：强调画质、细节、光影
    optimized += `, ${BASE_ENHANCEMENTS}`;
    applied.push('基础画质增强');
    
    if (detectedStyle) {
      optimized += `, ${STYLE_PRESETS[detectedStyle]}`;
      applied.push(`风格: ${detectedStyle}`);
    } else {
      optimized += ', 柔和自然光线, 构图平衡, 主体突出';
      applied.push('通用光影构图');
    }
  }
  
  return {
    original: prompt,
    optimized: optimized,
    style: detectedStyle,
    enabled: true,
    mode: isSequential ? 'sequential' : 'single',
    applied: applied
  };
}

// ============================================
// 🔑 API Key 自动检测模块
// ============================================

const os = require('os');
const homedir = os.homedir();

/**
 * 有效性校验：必须Agent Plan 专属
 */
function validateArkKey(key) {
  if (!key || typeof key !== 'string') {
    return { valid: false, reason: 'API Key 为空' };
  }
  
  const trimmed = key.trim();
  
  // 核心校验：必须Agent Plan 专属
  if (!trimmed.startsWith('ark-')) {
    return { 
      valid: false, 
      reason: `API Key 必须以 \"ark-\" 开头（火山方舟 Agent Plan 专属格式）` 
    };
  }
  
  return { valid: true, trimmed };
}

/**
 * 检测当前运行平台
 */
function detectPlatform() {
  if (fs.existsSync(path.join(homedir, '.openclaw'))) {
    return 'openclaw';
  }
  if (fs.existsSync(path.join(homedir, '.hermes'))) {
    return 'hermes';
  }
  if (fs.existsSync(path.join(homedir, '.claude')) || process.env.ANTHROPIC_AUTH_TOKEN) {
    return 'claude-code';
  }
  return 'unknown';
}

/**
 * 从 OpenClaw 配置中查找 Agent Plan 专属的 Key
 */
function findOpenClawArkKey() {
  const configPath = path.join(homedir, '.openclaw', 'openclaw.json');
  if (!fs.existsSync(configPath)) return null;
  
  try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    const providers = config.models?.providers || {};
    
    for (const [providerName, provider] of Object.entries(providers)) {
      if (provider.apiKey) {
        const validation = validateArkKey(provider.apiKey);
        if (validation.valid) {
          return validation.trimmed;
        }
      }
    }
  } catch (e) {
    return null;
  }
  return null;
}

/**
 * 从 Hermes 配置中查找 model.api_key
 */
function findHermesArkKey() {
  const configPath = path.join(homedir, '.hermes', 'config.yaml');
  if (!fs.existsSync(configPath)) return null;
  
  try {
    const content = fs.readFileSync(configPath, 'utf8');
    // 简单正则匹配：model.api_key: "ark-xxx"
    const match = content.match(/^model:\s*(?:\n.*)*?api_key:\s*[\"']?(ark-[^\"'\\s]+)[\"']?/m);
    if (match && match[1]) {
      const validation = validateArkKey(match[1]);
      if (validation.valid) {
        return validation.trimmed;
      }
    }
    return null;
  } catch (e) {
    return null;
  }
  return null;
}

/**
 * 智能兜底扫描：在特定环境变量和常见配置文件中找 Agent Plan 专属的 Key
 * ⚠️ 只扫描 API Key 字段的常见命名变体，避免误扫其他业务配置
 */
function smartScanForArkKey() {
  const found = [];
  
  // 只扫描通用环境变量的常见命名变体
  // 不扫描配置文件，避免误扫其他业务 Key
  const commonEnvNames = [
    'ANTHROPIC_AUTH_TOKEN',  // Claude Code 标准
    'API_KEY',
    'API_Key',
    'API_Keys',
    'api_key',
    'apiKey',
  ];
  
  for (const envName of commonEnvNames) {
    const value = process.env[envName];
    if (typeof value === 'string') {
      const validation = validateArkKey(value);
      if (validation.valid && !found.includes(validation.trimmed)) {
        found.push(validation.trimmed);
      }
    }
  }
  
  return found;
}

// 部分宿主平台（如 OpenClaw）通过一份 dotenv 文件下发工具凭证，而非直接暴露成真实
// env var。/root/.openclaw/.env 用绝对路径优先检查（不依赖脚本实际运行时 $HOME 解析到
// 哪个用户），再检查 ~/.openclaw/.env。已存在的真实 env var 不会被覆盖（setdefault 语义）。
const OPENCLAW_ENV_PATHS = ['/root/.openclaw/.env', path.join(os.homedir(), '.openclaw', '.env')];

function loadOpenClawEnv() {
  const seen = new Set();
  for (const rawPath of OPENCLAW_ENV_PATHS) {
    let content;
    try {
      if (seen.has(rawPath) || !fs.existsSync(rawPath)) continue;
      seen.add(rawPath);
      content = fs.readFileSync(rawPath, 'utf8');
    } catch (e) {
      continue;
    }
    for (let line of content.split('\n')) {
      line = line.trim();
      if (!line || line.startsWith('#')) continue;
      if (line.startsWith('export ')) line = line.slice('export '.length).trim();
      const eq = line.indexOf('=');
      if (eq < 0) continue;
      const key = line.slice(0, eq).trim();
      let value = line.slice(eq + 1).trim();
      if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      if (key && !(key in process.env)) {
        process.env[key] = value;
      }
    }
  }
}

/**
 * 自动检测 API Key（完整流程）
 */
function autoDetectApiKey() {
  loadOpenClawEnv();

  // 优先级 1: 显式环境变量（宿主平台通过 skill 级 env 下发的专属 key，或上面 loadOpenClawEnv()
  // 从 dotenv 文件补齐），与其余 ARK_SEEDREAM_* 覆盖项同一套命名约定，跳过平台探测直接生效。
  if (process.env.ARK_SEEDREAM_API_KEY) {
    const raw = process.env.ARK_SEEDREAM_API_KEY.trim();
    const validation = validateArkKey(raw);
    if (validation.valid) {
      return { key: validation.trimmed, source: 'env-override', found: true };
    }
    // base URL 被覆盖时请求发往宿主代理网关，凭证是代理签发的不透明 token
    // （不一定是 ark- 前缀），格式校验交给代理侧，这里原样放行。
    if (raw && (process.env.ARK_SEEDREAM_API_BASE_URL || process.env.ARK_API_BASE_URL)) {
      return { key: raw, source: 'env-override', found: true };
    }
  }

  const platform = detectPlatform();

  // 优先级 2: 根据当前平台读取对应配置
  if (platform === 'claude-code') {
    // 1. 先读环境变量（会话级，优先级最高）
    if (process.env.ANTHROPIC_AUTH_TOKEN) {
      const validation = validateArkKey(process.env.ANTHROPIC_AUTH_TOKEN);
      if (validation.valid) {
        return { key: validation.trimmed, source: 'claude-code', found: true };
      }
    }
    // 2. 再读配置文件（持久化配置）
    const claudeConfigPath = path.join(homedir, '.claude', 'settings.json');
    if (fs.existsSync(claudeConfigPath)) {
      try {
        const claudeConfig = JSON.parse(fs.readFileSync(claudeConfigPath, 'utf8'));
        if (claudeConfig.env?.ANTHROPIC_AUTH_TOKEN) {
          const validation = validateArkKey(claudeConfig.env.ANTHROPIC_AUTH_TOKEN);
          if (validation.valid) {
            return { key: validation.trimmed, source: 'claude-code', found: true };
          }
        }
      } catch (e) {
        // 配置文件有问题，静默跳过
      }
    }
  } else if (platform === 'openclaw') {
    // OpenClaw: 配置文件中的 apiKey
    const openClawKey = findOpenClawArkKey();
    if (openClawKey) {
      return { key: openClawKey, source: 'openclaw', found: true };
    }
  } else if (platform === 'hermes') {
    // Hermes: 配置文件中的 api_key
    const hermesKey = findHermesArkKey();
    if (hermesKey) {
      return { key: hermesKey, source: 'hermes', found: true };
    }
  }
  
  // 优先级 3: 兜底 - 扫描通用环境变量和配置文件
  // 平台特定检测没找到，或者是 unknown 平台
  const scanned = smartScanForArkKey();
  if (scanned.length > 0) {
    return { key: scanned[0], source: 'auto-scan', found: true };
  }
  
  return { key: null, source: null, found: false };
}

/**
 * 保存 API Key 到当前平台的全局配置文件
 * 
 * ⚠️ 安全原则：仅当用户明确确认保存，或显式传入 --save-api-key 时才调用此函数
 * 
 * ✅ 这是 Agent Plan 全局配置，保存后：
 *    - 不仅 Seedance / Seedream 可以自动检测使用
 *    - 整个平台所有 Agent Plan 能力（语言模型、生图、生视频、Embedding 等）都能直接复用
 */
// 🛡️ 递归脱敏对象中的 API Key 字段
function sanitizeApiKeys(obj) {
  if (!obj || typeof obj !== 'object') return obj;
  const result = Array.isArray(obj) ? [] : {};
  for (const [key, value] of Object.entries(obj)) {
    if (key.toLowerCase().includes('apikey') || key.toLowerCase() === 'api_key' || key.toLowerCase() === 'api-key') {
      result[key] = '***REDACTED***';
    } else if (typeof value === 'object') {
      result[key] = sanitizeApiKeys(value);
    } else {
      result[key] = value;
    }
  }
  return result;
}

async function autoSaveApiKey(apiKey) {
  const os = require('os');
  const path = require('path');
  const fs = require('fs');
  const homedir = os.homedir();
  
  const platform = detectPlatform();
  
  try {
    switch (platform) {
      case 'openclaw': {
        const configPath = path.join(homedir, '.openclaw', 'openclaw.json');
        if (!fs.existsSync(configPath)) {
          console.error(`ℹ️  未找到 OpenClaw 配置文件，跳过保存`);
          return false;
        }
        // 🛡️ 脱敏后备份，不泄漏已有密钥
        const backupPath = configPath + '.backup.before_agentplan';
        const originalConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        const sanitizedBackup = sanitizeApiKeys(originalConfig);
        fs.writeFileSync(backupPath, JSON.stringify(sanitizedBackup, null, 2));
        
        originalConfig.models = originalConfig.models || {};
        originalConfig.models.providers = originalConfig.models.providers || {};
        originalConfig.models.providers['volcengine-plan'] = originalConfig.models.providers['volcengine-plan'] || {};
        originalConfig.models.providers['volcengine-plan'].apiKey = apiKey;
        fs.writeFileSync(configPath, JSON.stringify(originalConfig, null, 2));
        // 🛡️ 设置严格的文件权限（仅所有者可读写）
        fs.chmodSync(configPath, 0o600);
        
        console.error(`✅ API Key 已保存到 OpenClaw 全局配置！`);
        console.error(`   文件: ~/.openclaw/openclaw.json (权限 0600)`);
        console.error(`   备份: ~/.openclaw/openclaw.json.backup.before_agentplan (API Key 已脱敏)`);
        console.error(`   🎯 此 Key 将用于所有 Agent Plan 能力：语言模型、生图、生视频、Embedding 等`);
        return true;
      }
      
      case 'hermes': {
        const configPath = path.join(homedir, '.hermes', 'config.yaml');
        if (!fs.existsSync(configPath)) {
          console.error(`ℹ️  未找到 Hermes 配置文件，跳过保存`);
          return false;
        }
        // 🛡️ 脱敏后备份，不泄漏已有密钥
        const backupPath = configPath + '.backup.before_agentplan';
        let originalContent = fs.readFileSync(configPath, 'utf8');
        const sanitizedContent = originalContent.replace(
          /(api_key:\s*)["']?[^"'\s]+["']?/mg,
          '$1"***REDACTED***"'
        );
        fs.writeFileSync(backupPath, sanitizedContent);
        
        let content = originalContent;
        const regex = /^(model:\s*(?:\n.*)*?api_key:\s*)["']?[^"'\s]+["']?/m;
        if (regex.test(content)) {
          content = content.replace(regex, `$1"${apiKey}"`);
        } else {
          content = content.replace(
            /^(model:)/m,
            `$1\n  api_key: "${apiKey}"`
          );
        }
        fs.writeFileSync(configPath, content);
        // 🛡️ 设置严格的文件权限（仅所有者可读写）
        fs.chmodSync(configPath, 0o600);
        
        console.error(`✅ API Key 已保存到 Hermes 全局配置！`);
        console.error(`   文件: ~/.hermes/config.yaml (权限 0600)`);
        console.error(`   备份: ~/.hermes/config.yaml.backup.before_agentplan (API Key 已脱敏)`);
        console.error(`   🎯 此 Key 将用于所有 Agent Plan 能力：语言模型、生图、生视频、Embedding 等`);
        return true;
      }
      
      case 'claude-code': {
        const claudeDir = path.join(homedir, '.claude');
        const configPath = path.join(claudeDir, 'settings.json');
        
        // 确保目录存在
        if (!fs.existsSync(claudeDir)) {
          fs.mkdirSync(claudeDir, { recursive: true });
        }
        
        let config = {};
        let existingKey = null;
        
        // 读取现有配置
        if (fs.existsSync(configPath)) {
          const backupPath = configPath + '.backup.before_agentplan';
          const originalConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
          // 🛡️ 脱敏后备份，不泄漏已有密钥
          const sanitizedBackup = sanitizeApiKeys(originalConfig);
          fs.writeFileSync(backupPath, JSON.stringify(sanitizedBackup, null, 2));
          try {
            config = originalConfig;
            config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
            existingKey = config.env?.ANTHROPIC_AUTH_TOKEN;
          } catch (e) {
            // 配置文件损坏，直接覆盖
          }
        }
        
        if (existingKey) {
          // 已有 Key，不覆盖，提示用户
          console.error(`ℹ️  Claude Code 已配置 ANTHROPIC_AUTH_TOKEN`);
          console.error(`   为避免覆盖您的原有配置，本次仅临时使用新 Key`);
          console.error(`   如需永久更新，请手动修改 ~/.claude/settings.json`);
          return false;
        } else {
          // 没有 Key，写入配置
          if (!config.env) config.env = {};
          config.env.ANTHROPIC_AUTH_TOKEN = apiKey;
          fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
          // 🛡️ 设置严格的文件权限（仅所有者可读写）
          fs.chmodSync(configPath, 0o600);
          
          console.error(`✅ API Key 已保存到 Claude Code 全局配置！`);
          console.error(`   文件: ~/.claude/settings.json (权限 0600)`);
          if (fs.existsSync(configPath + '.backup.before_agentplan')) {
            console.error(`   备份: ~/.claude/settings.json.backup.before_agentplan (API Key 已脱敏)`);
          }
          console.error(`   🎯 此 Key 将用于所有 Agent Plan 能力：语言模型、生图、生视频、Embedding 等`);
          return true;
        }
      }
      
      default:
        console.error(`ℹ️  当前平台为 ${platform}，API Key 仅本次临时使用`);
        return false;
    }
  } catch (e) {
    console.error(`⚠️  保存配置失败: ${e.message}，不影响本次使用`);
    return false;
  }
}

/**
 * 展开路径中的 ~ 为用户主目录
 */
function expandHome(inputPath) {
  if (!inputPath || typeof inputPath !== 'string') return inputPath;
  const os = require('os');
  const path = require('path');
  const homedir = os.homedir();
  if (inputPath === '~') return homedir;
  if (inputPath.startsWith('~/')) {
    return path.join(homedir, inputPath.slice(2));
  }
  return inputPath;
}

/**
 * 获取默认保存路径
 * 优先级: 环境变量配置 > Claude 启动目录（脚本运行时的当前工作目录）
 *
 * ⚠️ 默认保存到 process.cwd()，即调用脚本时所在的目录（Claude 启动目录）。
 *    因此请用脚本的【绝对路径】调用，且不要 cd 进入 skill 安装目录，
 *    否则 process.cwd() 会变成 skill 目录，图片就会存到 skill 里而不是启动目录。
 */
function getDefaultSavePath() {
  const path = require('path');

  // 1. 优先使用环境变量配置（用户显式指定固定保存路径时）
  if (process.env.ARK_SEEDREAM_SAVE_PATH) {
    return expandHome(process.env.ARK_SEEDREAM_SAVE_PATH);
  }
  if (process.env.ARK_SAVE_PATH) {
    return expandHome(process.env.ARK_SAVE_PATH);
  }

  // 2. 默认保存到 Claude 启动目录（当前工作目录）下的 Seedream-Images
  return path.join(process.cwd(), 'Seedream-Images');
}

// ============================================
// ⚙️ 配置
// ============================================

// 自动检测 API Key
const detected = autoDetectApiKey();

const CONFIG = {
  // Agent Plan 专属版本 - 使用 Agent Plan 统一 baseurl /api/plan/v3
  apiBaseUrl: process.env.ARK_SEEDREAM_API_BASE_URL || process.env.ARK_API_BASE_URL || 'https://ark.cn-beijing.volces.com/api/plan/v3',
  // Agent Plan Seedream 5.0 lite 模型（可通过环境变量扩展其他模型）
  model: process.env.ARK_SEEDREAM_MODEL || process.env.ARK_MODEL || 'doubao-seedream-5.0-lite',
  // API Key：自动检测结果
  apiKey: detected.found ? detected.key : '',
  savePath: getDefaultSavePath()
};

/**
 * 验证必需配置检查
 * @returns {Object} { valid: boolean, errors: string[], warnings: string[] }
 */
function validateConfig() {
  const errors = [];
  const warnings = [];

  if (!CONFIG.apiKey) {
    errors.push('❌ 未检测到有效的 Agent Plan API Key');
    errors.push('');
    errors.push('💡 请直接在对话中发送 Agent Plan 专属 API Key（必须以 \"ark-\" 开头）');
    errors.push('   本次会临时使用；如需保存为全局配置，请明确说明「保存这个 API Key」。');
    errors.push('');
    errors.push('📍 如果已经配置了但检测不到，请确认：');
    errors.push('   - OpenClaw: models.providers.*.apiKey');
    errors.push('   - Hermes: model.api_key');
    errors.push('   - Claude Code: ANTHROPIC_AUTH_TOKEN 环境变量');
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * 🔒 安全校验：所有输入参数合法性校验
 * @param {Object} params - 输入参数
 * @returns {string[]} 错误列表，空数组表示校验通过
 */
function validateParams(params) {
  const errors = [];

  // 1. prompt 必填且长度限制
  if (!params.prompt || params.prompt.trim() === '') {
    errors.push('prompt 不能为空');
  } else if (params.prompt.length > 3000) {
    errors.push(`prompt 长度不能超过 3000 字符（当前: ${params.prompt.length}）`);
  }

  // 2. size 校验：支持 K 值枚举或像素值格式
  if (params.size) {
    const validSizes = ['2K', '3K', '2k', '3k'];
    const pixelRegex = /^\d+x\d+$/i;
    
    if (!validSizes.includes(params.size) && !pixelRegex.test(params.size)) {
      errors.push(`size 参数无效（\"${params.size}\"），支持：2K/3K 或具体像素值如 2048x2048`);
    }
  }

  // 3. count 范围校验（连贯图时）
  if (params.count !== undefined) {
    const count = parseInt(params.count);
    if (isNaN(count) || count < 1 || count > 15) {
      errors.push('count 参数必须是 1-15 之间的整数');
    }
  }

  // 4. mode 枚举校验
  if (params.mode && !['text-to-image', 'image-to-image'].includes(params.mode)) {
    errors.push(`mode 参数无效（\"${params.mode}\"），支持：text-to-image / image-to-image`);
  }

  // 5. 参考图校验
  if (params.reference_images) {
    try {
      const refs = parseReferenceImages(params.reference_images);
      if (refs.length === 0) {
        errors.push('参考图数组不能为空');
      } else if (refs.length > 14) {
        errors.push(`参考图数量不能超过 14 张（当前: ${refs.length}）`);
      }
      // 🐛 Bug 修复：校验参考图数量 + 生成图片数量 <= 15
      const outputCount = params.sequential ? Number(params.count || 4) : 1;
      if (refs.length + outputCount > 15) {
        errors.push(`参考图数量 + 生成图片数量不能超过 15（当前: ${refs.length} + ${outputCount} = ${refs.length + outputCount}）`);
      }
      // 简单格式校验：URL 或 Base64
      refs.forEach((ref, idx) => {
        const isUrl = ref.startsWith('http://') || ref.startsWith('https://');
        const isBase64 = ref.startsWith('data:image/');
        if (!isUrl && !isBase64) {
          errors.push(`第 ${idx + 1} 张参考图格式无效，必须是 HTTP URL 或 Base64 编码（data:image/xxx;base64,...）`);
        }
      });
    } catch (e) {
      errors.push('reference_images 格式无效，必须是 JSON 数组格式');
    }
  }

  // 6. response_format 枚举校验
  if (params.response_format && !['png', 'jpeg'].includes(params.response_format)) {
    errors.push(`response_format 参数无效（\"${params.response_format}\"），支持：png / jpeg`);
  }

  // 7. 布尔类型参数校验
  const booleanParams = ['sequential', 'watermark', 'stream', 'optimize', 'enable_web_search'];
  booleanParams.forEach(key => {
    if (params[key] !== undefined && typeof params[key] !== 'boolean') {
      errors.push(`${key} 参数必须是布尔值（true/false）`);
    }
  });

  // 8. user_id 长度限制
  if (params.user_id && params.user_id.length > 128) {
    errors.push('user_id 长度不能超过 128 字符');
  }

  // 9. model 长度校验（不做白名单限制，让 API 负责模型有效性）
  if (params.model && params.model.length > 128) {
    errors.push('model 参数长度不能超过 128 字符');
  }
  // reference_strength 参数校验（0~1）
  if (params.reference_strength !== undefined) {
    const strength = parseFloat(params.reference_strength);
    if (isNaN(strength) || strength < 0 || strength > 1) {
      errors.push('reference_strength 参数必须是 0 到 1 之间的数字');
    }
  }


  return errors;
}

// 全局状态
let startTime = Date.now();
let generatedImages = [];
// 流式下载状态管理
let pendingDownloads = 0;
let streamCompleted = false;
let streamResolveFn = null;  // 流式完成回调
let nextImageIndex = 1;      // 🐛 Bug 5 修复：原子计数器，不依赖数组长度

// ============================================
// 🌐 HTTP 请求
// ============================================

function request(url, options, data = null) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const isHttps = parsedUrl.protocol === 'https:';
    const lib = isHttps ? https : http;
    
    const API_TIMEOUT_MS = Number(process.env.ARK_SEEDREAM_TIMEOUT_MS || 120000);
    
    const req = lib.request(url, options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        // 🔒 安全掩码：隐藏 Authorization 头，防止意外打印时泄漏
        const safeHeaders = { ...res.headers };
        if (safeHeaders.authorization) {
          safeHeaders.authorization = 'Bearer ***masked***';
        }
        
        try {
          resolve({
            statusCode: res.statusCode,
            headers: safeHeaders,
            body: body ? JSON.parse(body) : null
          });
        } catch (e) {
          resolve({
            statusCode: res.statusCode,
            headers: safeHeaders,
            body: body
          });
        }
      });
    });
    
    req.setTimeout(API_TIMEOUT_MS, () => {
      req.destroy(new Error(`API 请求超时（${API_TIMEOUT_MS / 1000}s）`));
    });
    
    req.on('error', reject);
    
    if (data) {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
}

function requestStream(url, options, data, onChunk, onDone) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const isHttps = parsedUrl.protocol === 'https:';
    const lib = isHttps ? https : http;
    
    const req = lib.request(url, options, (res) => {
      let buffer = '';
      let currentEvent = null;
      
      if (res.statusCode !== 200) {
        let errorBody = '';
        res.on('data', (chunk) => errorBody += chunk);
        res.on('end', () => {
          reject(new Error(`HTTP ${res.statusCode}: ${errorBody}`));
        });
        return;
      }
      
      res.on('data', (chunk) => {
        buffer += chunk.toString('utf-8');
        const lines = buffer.split(/\r?\n/);
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;
          
          // 处理 event: 前缀
          if (trimmed.startsWith('event:')) {
            currentEvent = trimmed.slice(6).trim();
            continue;
          }
          
          // 处理 data: 前缀
          if (trimmed.startsWith('data:')) {
            const dataStr = trimmed.slice(5).trim();
            if (dataStr === '[DONE]') {
              onDone && onDone();
              return;
            }
            try {
              const json = JSON.parse(dataStr);
              json._event = currentEvent;  // 把 event 附上去
              onChunk && onChunk(json);
            } catch (e) {
              // SSE 解析失败不中断流程，仅打印日志方便调试
              console.error(`⚠️  SSE data 行解析失败: ${e.message}`);
              console.error(`   data: ${dataStr.substring(0, 100)}${dataStr.length > 100 ? '...' : ''}`);
            }
          }
        }
      });
      
      res.on('end', () => {
        resolve();
      });
    });

    const API_TIMEOUT_MS = Number(process.env.ARK_SEEDREAM_TIMEOUT_MS || 120000);
    req.setTimeout(API_TIMEOUT_MS, () => {
      req.destroy(new Error(`API 请求超时（${API_TIMEOUT_MS / 1000}s）`));
    });

    req.on('error', reject);
    
    if (data) {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
}

// ============================================
// 📂 文件工具
// ============================================

/**
 * 下载文件（带超时机制 + 错误清理）
 */
function downloadFile(url, savePath, timeoutMs = 30000, redirectCount = 0) {
  return new Promise((resolve, reject) => {
    const MAX_REDIRECTS = 5;
    
    if (redirectCount > MAX_REDIRECTS) {
      reject(new Error(`重定向次数超过限制（${MAX_REDIRECTS}次）`));
      return;
    }
    
    const parsedUrl = new URL(url);
    const isHttps = parsedUrl.protocol === 'https:';
    const lib = isHttps ? https : http;
    
    let file = null;
    let request = null;
    
    // 超时机制
    const timeout = setTimeout(() => {
      reject(new Error(`下载超时（${timeoutMs/1000}s）`));
      if (file) file.destroy();
      if (request) request.destroy();
      fs.unlink(savePath, () => {});
    }, timeoutMs);
    
    request = lib.get(url, (response) => {
      // 处理重定向
      if ([301, 302, 307, 308].includes(response.statusCode) && response.headers.location) {
        clearTimeout(timeout);
        if (file) file.destroy();
        const redirectUrl = new URL(response.headers.location, url).href;
        resolve(downloadFile(redirectUrl, savePath, timeoutMs, redirectCount + 1));
        return;
      }
      
      // 校验 HTTP 状态码
      if (response.statusCode !== 200) {
        clearTimeout(timeout);
        if (file) file.destroy();
        fs.unlink(savePath, () => {});
        reject(new Error(`HTTP ${response.statusCode} / content-type: ${response.headers['content-type'] || 'unknown'}`));
        return;
      }
      
      // 校验 Content-Type
      const contentType = response.headers['content-type'] || '';
      if (!contentType.startsWith('image/') && !contentType.startsWith('video/') && !contentType.startsWith('application/octet-stream')) {
        clearTimeout(timeout);
        if (file) file.destroy();
        fs.unlink(savePath, () => {});
        reject(new Error(`无效资源类型: ${contentType}（不是图片/视频）`));
        return;
      }
      
      // 开始下载
      file = fs.createWriteStream(savePath);
      response.pipe(file);
      
      file.on('finish', () => {
        clearTimeout(timeout);
        file.close();
        
        // 校验文件大小 > 0
        try {
          const stats = fs.statSync(savePath);
          if (stats.size === 0) {
            fs.unlink(savePath, () => {});
            reject(new Error('下载文件大小为 0'));
            return;
          }
          resolve(savePath);
        } catch (e) {
          fs.unlink(savePath, () => {});
          reject(new Error(`文件校验失败: ${e.message}`));
        }
      });
      
      file.on('error', (err) => {
        clearTimeout(timeout);
        file.destroy();
        fs.unlink(savePath, () => {});
        reject(err);
      });
    });
    
    request.on('error', (err) => {
      clearTimeout(timeout);
      if (file) file.destroy();
      fs.unlink(savePath, () => {});
      reject(err);
    });
  });
}

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
  return dirPath;
}

function renderProgress(current, total, prefix = '生成中') {
  const percent = Math.round((current / total) * 100);
  const barLength = 20;
  const filled = Math.round((current / total) * barLength);
  const empty = barLength - filled;
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  
  const bar = '█'.repeat(filled) + '░'.repeat(empty);
  console.error(`[${prefix}] ${bar} ${percent}% (${current}/${total}) · ${elapsed}s`);
}

// 检查流式是否全部完成（API 完成 + 所有图片下载完成）
async function checkStreamComplete() {
  if (streamCompleted && pendingDownloads === 0) {
    console.error('');
    console.error('📥 所有图片接收并下载完毕');
    // 真正 resolve 流式 Promise
    if (streamResolveFn) {
      streamResolveFn();
      streamResolveFn = null;
    }
  }
}

async function handleStreamChunk(chunk, saveDir, timestamp, totalImages, params) {
  // Seedream 流式格式: event: image_generation.partial_succeeded + data: {url}
  // 🐛 Bug 修复：兼容多种 API 返回格式，从多个可能位置提取 URL
  const imageUrl = 
    chunk.url || 
    chunk.data?.url || 
    chunk.image?.url || 
    chunk.output?.url || 
    chunk.result?.url;
    
  if (chunk._event === 'image_generation.partial_succeeded' && imageUrl) {
    const index = nextImageIndex++;  // 🐛 Bug 5 修复：原子计数器
    
    console.error('');
    console.error(`🖼️  第 ${index} 张图已生成！`);
    
    // 🐛 Bug 修复：按实际输出格式决定文件扩展名
    const ext = (params.response_format || 'jpeg') === 'png' ? 'png' : 'jpg';
    const fileName = `seedream_${timestamp}_${index}.${ext}`;
    const localPath = path.join(saveDir, fileName);
    
    console.error(`   正在下载...`);
    pendingDownloads++;
    
    try {
      await downloadFile(imageUrl, localPath);
      console.error(`   ✅ 已保存: ${fileName}`);
      
      generatedImages.push({
        url: imageUrl,
        local_path: localPath,
        prompt: params.prompt,
        index: index,
        download_success: true
      });
    } catch (e) {
      // 🐛 Bug 6 修复：下载失败不中断整个流程，记录结构化错误
      console.error(`   ❌ 下载失败: ${e.message}`);
      
      generatedImages.push({
        url: imageUrl,
        local_path: null,
        prompt: params.prompt,
        index: index,
        download_success: false,
        download_error: e.message
      });
    }
    
    pendingDownloads--;  // 无论成功失败都--
    
    if (totalImages) {
      renderProgress(index, totalImages);
    }
    
    // 检查是否所有都完成了
    checkStreamComplete();
  }
  
  // completed 事件：标记 API 完成，但等所有图片下载完再输出结束
  if (chunk._event === 'image_generation.completed') {
    streamCompleted = true;
    checkStreamComplete();
  }
}

// ============================================
// 🚀 API 调用
// ============================================

async function callSeedreamApi(params, saveDir, timestamp) {
  const body = {
    model: CONFIG.model,
    prompt: params.prompt,
    sequential_image_generation: params.sequential ? 'auto' : 'disabled',
    response_format: 'url',
    size: params.size || '2k',
    stream: params.stream,
    watermark: params.watermark !== false,
    output_format: params.response_format || 'jpeg'  // 图片输出格式：png/jpeg（5.0 lite 默认 jpeg）
  };

  // 联网搜索开关
  if (params.enable_web_search === true) {
    body.tools = [{ type: 'web_search' }];
  }
  
  // ⚠️ Bug 修复：Seedream Agent Plan API 不支持 sequential_image_generation_options.max_images
  // 传了这个参数会导致 400 错误。只保留 sequential 开关即可，API 会自动根据 prompt 生成对应张数
  // 注意：--count 不会透传为 API 数量字段，真正控制张数靠 prompt 中的"生成 X 张一组"语义
  // --count 仅用于本地校验、进度展示和 metadata 记录
  // 参考：Agent Plan 视频生成也有类似行为，无需传多余的 options
  
  if (params.mode === 'image-to-image' && params.reference_images) {
    const refs = parseReferenceImages(params.reference_images);
    // 支持两种参考图格式（官方 API 支持）：
    // 1. HTTP URL 字符串：https://xxx.com/yyy.png
    // 2. Base64 字符串：data:image/png;base64,xxx（png/jpeg/webp/bmp/tiff/gif 均可）
    // 传参规则：
    // - 长度为1时传字符串（Seedream API 约定）
    // - 长度>1时传数组，支持最多 14 张参考图
    // 总张数限制：输入参考图数量 + 生成图片数量 ≤ 15 张
    body.image = refs.length === 1 ? refs[0] : refs;
  }
  
  // 参考图影响强度
  if (params.reference_strength !== undefined) {
    body.reference_strength = Number(params.reference_strength);
  }
  
  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${CONFIG.apiKey}`
    }
  };
  
  // Agent Plan 统一架构：图片生成 API 路径为 /api/plan/v3/images/generations
  // 调用 Agent Plan 原生图片生成接口
  const url = `${CONFIG.apiBaseUrl}/images/generations`;
  const totalImages = params.sequential ? (params.count || 4) : 1;

  if (params.stream) {
    console.error('🌊 启用流式输出模式，生成一张返回一张');
    console.error('');
    
    return await new Promise((resolve, reject) => {
      streamResolveFn = () => resolve({ stream: true, images: [...generatedImages] });
      requestStream(url, options, body, 
        (chunk) => handleStreamChunk(chunk, saveDir, timestamp, totalImages, params),
        () => { streamCompleted = true; checkStreamComplete(); }
      )
      .then(() => {
        // 兜底：连接正常结束但未收到 completed 事件时也标记完成
        if (!streamCompleted) {
          streamCompleted = true;
          checkStreamComplete();
        }
      })
      .catch(reject);
    });
  } else {
    console.error('📦 使用非流式模式，等待全部生成完毕');
    
    const response = await request(url, options, body);
    if (response.statusCode !== 200) {
      throw new Error(`HTTP ${response.statusCode}: ${JSON.stringify(response.body)}`);
    }
    
    return { response: response.body, generationTime: (Date.now() - startTime) / 1000 };
  }
}

// ============================================
// 🏁 主函数
// ============================================

// 🛡️ 增强参数解析：支持 --key=value、无值 boolean 参数
function parseArgv(argv) {
  const params = {};
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (!token.startsWith('--')) continue;
    
    // 处理 --key=value 格式
    const eqIndex = token.indexOf('=');
    if (eqIndex >= 0) {
      const key = token.slice(2, eqIndex);
      const value = token.slice(eqIndex + 1);
      params[key] = value;
      continue;
    }
    
    // 处理 --key value 格式（或无值 boolean）
    const key = token.slice(2);
    const nextToken = argv[i + 1];
    if (nextToken && !nextToken.startsWith('--')) {
      // 有值：--key value
      params[key] = nextToken;
      i++; // 跳过下一个 token（已作为值处理）
    } else {
      // 无值 boolean：--stream → 设为 true
      params[key] = 'true';
    }
  }
  return params;
}

async function main() {
  try {
    // 先解析命令行参数（必须在 validateConfig 之前，因为 --api-key 会修改 CONFIG）
    const args = process.argv.slice(2);
    const params = parseArgv(args);
    
    // 🔑 优先处理用户传入的 API Key（支持三种写法：--api-key / --api_key / --apiKey）
    const apiKeyParam = params['api-key'] || params.api_key || params.apiKey;
    // 🔒 仅当显式传入 --save-api-key 时才保存到全局配置
    const shouldSaveKey = params['save-api-key'] !== undefined || params.save_api_key !== undefined || params.saveApiKey !== undefined;
    
    if (apiKeyParam) {
      const validation = validateArkKey(apiKeyParam);
      if (!validation.valid) {
        console.error(`❌ ${validation.reason}`);
        process.exit(1);
      }
      CONFIG.apiKey = validation.trimmed;
      
      if (shouldSaveKey) {
        // 显式要求保存才写入全局配置
        await autoSaveApiKey(CONFIG.apiKey);
      } else {
        // 🛡️ 默认仅临时使用，不保存
        console.error(`ℹ️  已使用本次提供的 API Key（默认仅本次临时使用，不保存到全局配置）`);
        console.error(`   💡 提示：Agent Plan API Key 是全局配置，影响语言模型、生图、生视频、Embedding 等所有能力`);
        console.error(`   如需以后自动使用，请明确说「保存这个 API Key 到全局配置」`);
      }
      console.error('');
    }

    // 配置验证
    const { valid, errors, warnings } = validateConfig();
    if (warnings.length > 0) {
      console.error(warnings.join('\n'));
      console.error('');
    }
    if (!valid) {
      console.error(errors.join('\n'));
      process.exit(1);
    }
    
    // 解析参数类型
    if (params.sequential !== undefined) params.sequential = parseBoolean(params.sequential);
    // 🐛 Bug 9 修复：count 参数边界检查
    if (params.count !== undefined) {
      const count = parseInt(params.count);
      if (isNaN(count)) {
        console.error(`ℹ️  count 参数格式错误，已自动设为默认值 4`);
        params.count = 4;  // 默认值
      } else if (count < 1 || count > 15) {
        const clamped = Math.max(1, Math.min(15, count));
        console.error(`ℹ️  count 超出有效范围 1-15，已自动调整为 ${clamped}`);
        console.error(`   （API 限制：参考图 + 生成图总数 ≤ 15）`);
        params.count = clamped;
      }
    }
    if (params.watermark !== undefined) params.watermark = parseBoolean(params.watermark);
    if (params.stream !== undefined) params.stream = parseBoolean(params.stream);
    if (params.optimize !== undefined) params.optimize = parseBoolean(params.optimize);
    if (params.enable_web_search !== undefined) params.enable_web_search = parseBoolean(params.enable_web_search);
    
    // 🐛 Bug 修复：传了 reference_images 但没传 mode 时，自动推断为 image-to-image
    if (params.reference_images && !params.mode) {
      params.mode = 'image-to-image';
    }
    
    // 🔒 安全校验：所有参数合法性校验
    const validationErrors = validateParams(params);
    if (validationErrors.length > 0) {
      console.error('❌ 参数校验失败：');
      validationErrors.forEach(err => console.error(`   - ${err}`));
      process.exit(1);
    }
    
    // 🐛 Bug 12 修复：无论 optimize 是否开启，都要保存原始提示词
    params.originalPrompt = params.prompt;
    
    // 提示词优化：先判断是不是连贯图模式，再应用对应优化策略
    if (params.optimize !== false) {
      const isSequential = params.sequential === true;
      const promptResult = optimizePrompt(params.prompt, params.optimize !== false, isSequential);
      params.prompt = promptResult.optimized;
      params.promptInfo = promptResult;
    }
    
    // 自动判断流式输出
    if (params.stream === undefined) {
      params.stream = params.sequential || false;
    }
    
    // 自动检测联网搜索：提示词包含相关关键词时自动开启
    if (params.enable_web_search === undefined) {
      const lowerPrompt = params.originalPrompt.toLowerCase();
      if (/联网|搜索|实时|最新|新闻|赛事|今天|今日|现在|当前|刚|最新消息/i.test(lowerPrompt)) {
        params.enable_web_search = true;
      }
    }
    
    // 🐛 Bug 7 修复：完整重置所有全局状态
    startTime = Date.now();
    generatedImages = [];
    pendingDownloads = 0;
    streamCompleted = false;
    streamResolveFn = null;
    nextImageIndex = 1;
    
    // 检查 API Key
    if (!CONFIG.apiKey) {
      throw new Error(`API Key 未配置。

请使用以下任一方式配置：

方式 1: 直接在对话中发送你的 API Key（Agent Plan 专属）
方式 2: 设置环境变量 export API_KEY="ark-xxx"
方式 3: 在平台配置文件中配置
`);
    }
    
    // 检查必填参数
    if (!params.prompt) {
      throw new Error('缺少 prompt 参数');
    }
    
    // 准备保存目录
    const today = new Date().toISOString().split('T')[0];
    const saveDir = ensureDir(path.join(CONFIG.savePath, today));
    const timestamp = Math.floor(Date.now() / 1000);
    
    // 打印开始信息
    console.error('\n' + '='.repeat(50));
    console.error('🎨 Ark Seedream 图片生成');
    console.error('='.repeat(50));
    
    if (params.promptInfo && params.promptInfo.enabled) {
      console.error(`✅ 提示词优化: 已开启`);
      if (params.promptInfo.style) {
        console.error(`🎨 检测风格: ${params.promptInfo.style}`);
      }
      console.error(`📝 原提示词: ${params.promptInfo.original}`);
      console.error(`✨ 优化后: ${params.prompt}`);
    } else {
      console.error(`📝 提示词: ${params.prompt}`);
    }
    
    console.error(`📐 尺寸: ${params.size || '2k'}`);
    console.error(`🎬 模式: ${params.mode || 'text-to-image'} ${params.stream ? '(流式)' : '(非流式)'}`);
    if (params.sequential) {
      console.error(`🖼️  连贯图: ${params.count || 4} 张`);
    }
    if (params.mode === 'image-to-image' && params.reference_images) {
      const refs = parseReferenceImages(params.reference_images);
      console.error(`🖼️  参考图: ${refs.length} 张`);
    }
    console.error('='.repeat(50));
    console.error('');
    
    // 调用 API
    const result = await callSeedreamApi(params, saveDir, timestamp);
    
    // 非流式模式：手动下载所有图片
    if (!params.stream && result.response && result.response.data) {
      console.error('');
      // 🐛 Bug 修复：按实际输出格式决定文件扩展名
      const ext = (params.response_format || 'jpeg') === 'png' ? 'png' : 'jpg';
      for (let i = 0; i < result.response.data.length; i++) {
        const imageData = result.response.data[i];
        const fileName = `seedream_${timestamp}_${i + 1}.${ext}`;
        const localPath = path.join(saveDir, fileName);
        
        console.error(`🖼️  正在下载第 ${i + 1}/${result.response.data.length} 张...`);
        
        // 🐛 Bug 11 修复：单张下载失败不影响其他图片，记录结构化错误
        try {
          await downloadFile(imageData.url, localPath);
          console.error(`   ✅ 已保存: ${fileName}`);
          
          generatedImages.push({
            url: imageData.url,
            local_path: localPath,
            prompt: params.prompt,
            index: i + 1,
            download_success: true
          });
        } catch (e) {
          console.error(`   ❌ 下载失败: ${e.message}`);
          
          generatedImages.push({
            url: imageData.url,
            local_path: null,
            prompt: params.prompt,
            index: i + 1,
            download_success: false,
            download_error: e.message
          });
        }
      }
    }
    
    // 保存 metadata
    const metadata = {
      prompt: params.prompt,
      original_prompt: params.originalPrompt,
      mode: params.mode || 'text-to-image',
      size: params.size || '2k',
      sequential: params.sequential,
      count: params.count || (params.sequential ? 4 : 1),
      stream: params.stream,
      watermark: params.watermark,
      generation_time: (Date.now() - startTime) / 1000,
      image_count: generatedImages.length,
      optimize: params.optimize,
      detected_style: params.promptInfo?.style || null,
      images: generatedImages.map(img => ({
        url: img.url,
        file_name: img.local_path ? path.basename(img.local_path) : null,
        download_success: img.download_success,
        download_error: img.download_error || null,
        index: img.index
      }))
    };
    
    const metadataPath = path.join(saveDir, `seedream_${timestamp}_metadata.json`);
    // 🐛 Bug 13 修复：metadata 写入失败不崩溃
    try {
      fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2), 'utf-8');
    } catch (e) {
      console.error(`⚠️  metadata 写入失败: ${e.message}`);
    }
    
    // 返回结果
    const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
    
    // 🛡️ 统一兜底校验：无论流式还是非流式，0 张图都报错
    if (generatedImages.length === 0) {
      console.error('❌ 生成失败：API 未返回任何可用图片');
      console.error('   可能原因：API 返回格式变化、网络异常、或参数错误');
      process.exit(1);
    }
    
    const output = {
      success: true,
      images: [...generatedImages],  // 返回副本防止后续意外修改
      error: null,
      metadata: {
        generation_time: parseFloat(totalTime),
        size: params.size || '2k',
        mode: params.mode || 'text-to-image',
        stream: params.stream,
        image_count: generatedImages.length,
        style: params.promptInfo?.style || null,
        save_dir: saveDir,                    // 图片保存目录，方便 Agent 直接读取文件夹
        metadata_path: metadataPath           // metadata.json 完整路径
      }
    };
    
    console.error('\n' + '='.repeat(50));
    console.error('✅ 全部生成完成！');
    console.error(`⏱️  总耗时: ${totalTime}s`);
    console.error(`📂 保存目录: ${saveDir}`);
    console.error(`🖼️  生成数量: ${generatedImages.length} 张`);
    console.error('');
    console.error('💡 提示：图片已成功保存到本地目录');
    console.error('   如果没有看到图片，可以直接去保存目录查看文件');
    console.error('='.repeat(50));
    console.error('');
    
    // 明确列出本地路径和原始资源地址，优先使用本地文件
    if (generatedImages.length > 0) {
      console.error('📄 生成结果：');
      generatedImages.forEach((img, idx) => {
        if (img.download_success) {
          console.error(`   ${idx + 1}. ✅ 下载成功:`);
          console.error(`      💾 本地保存路径: ${img.local_path}`);
          console.error(`      🔗 原始资源地址（不要截断 URL）:`);
          console.error(`      \`\`\``);
          console.error(`      ${img.url}`);
          console.error(`      \`\`\``);
        } else {
          console.error(`   ${idx + 1}. ❌ 下载失败:`);
          console.error(`      错误信息: ${img.download_error}`);
          console.error(`      🔗 原始资源地址: ${img.url}`);
        }
      });
      console.error('');
    }
    
    console.log(JSON.stringify(output, null, 2));
    
  } catch (error) {
    console.error('\n❌ 生成失败:');
    console.error(error.message);
    
    const output = {
      success: false,
      images: generatedImages,
      error: error.message,
      metadata: null
    };
    
    console.log(JSON.stringify(output, null, 2));
    process.exit(1);
  }
}

main();
