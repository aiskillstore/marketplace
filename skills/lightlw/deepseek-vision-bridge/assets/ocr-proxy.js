const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const net = require('net');
const { Buffer } = require('buffer');
const Tesseract = require('tesseract.js');
const crypto = require('crypto');

// ============================================================
//  配置
// ============================================================
// ============================================================
//  上游 — 直连 DeepSeek 官网（官方原生支持 Responses API）
//  上游默认直连 DeepSeek 官网（官方原生支持 Responses API）
//  如需改回 Codex++ 网关: { host: '127.0.0.1', port: 57321, https: false }
//  可用环境变量覆盖: DEEPSEEK_BASE_URL / DEEPSEEK_BASE_PORT / DEEPSEEK_BASE_HTTPS
// ============================================================
const UPSTREAM = {
    host: process.env.DEEPSEEK_BASE_URL || 'api.deepseek.com',
    port: parseInt(process.env.DEEPSEEK_BASE_PORT || '443', 10),
    https: (process.env.DEEPSEEK_BASE_HTTPS || 'true') !== 'false'
};
const PROXY_PORT = parseInt(process.env.OCR_PROXY_PORT || '57323', 10);
const LOG_DIR = path.join(__dirname, 'outputs');
const LOG_FILE = path.join(LOG_DIR, 'proxy.log');
const LOG_MAX_SIZE = 5 * 1024 * 1024; // 5MB
const WORKER_MAX_OCR = 1000;           // worker 重建阈值

// ============================================================
//  图片处理结果缓存（LRU 淘汰）
// ============================================================
const IMAGE_CACHE_MAX = 500;           // 最大缓存条目数
const imageCache = new Map();          // hash → { text, type, ts }

function imageHash(imageData) {
    // 对 base64 data URI 取前 200 字符 + 总长度作为快速指纹（避免对 MB 级数据做完整 hash）
    if (imageData.length > 500) {
        return crypto.createHash('md5')
            .update(imageData.substring(0, 200) + '|' + imageData.length + '|' + imageData.substring(imageData.length - 100))
            .digest('hex');
    }
    return crypto.createHash('md5').update(imageData).digest('hex');
}

function cacheGet(hash) {
    const entry = imageCache.get(hash);
    if (entry) {
        // LRU: 访问时删除再重新插入（移到末尾 = 最新）
        imageCache.delete(hash);
        imageCache.set(hash, entry);
        return entry;
    }
    return null;
}

function cacheSet(hash, text, type) {
    // 超出上限时淘汰最旧条目
    if (imageCache.size >= IMAGE_CACHE_MAX) {
        const oldest = imageCache.keys().next().value;
        imageCache.delete(oldest);
    }
    imageCache.set(hash, { text, type, ts: Date.now() });
}

const TEXT_ONLY_PATTERNS = [
    'deepseek', 'ds-', 'claude', 'llama', 'mixtral',
    'qwen', 'glm', 'baichuan', 'yi-', 'minimax'
];

// ============================================================
//  SiliconFlow VL API 配置
// ============================================================
const VL_API_URL = 'https://api.siliconflow.cn/v1/chat/completions';
const VL_MODEL = 'Qwen/Qwen3-VL-8B-Instruct';

// ============================================================
//  本地视觉模型 (Ollama) 配置 — 云端不可用/离线时的兜底
// ============================================================
const OLLAMA_URL = process.env.OLLAMA_URL || 'http://127.0.0.1:11434';
const LOCAL_VL_MODEL = process.env.LOCAL_VL_MODEL || 'minicpm-v:8b';

// .env 查找顺序: 代理目录旁 .env → tools/.env → 环境变量
const LOCAL_ENV_PATH = path.join(__dirname, '.env');
const ENV_PATH = fs.existsSync(LOCAL_ENV_PATH) ? LOCAL_ENV_PATH : path.join(__dirname, '..', '..', 'tools', '.env');
const CONFIG_PATH = path.join(__dirname, '..', '..', 'tools', 'config.json');
let cachedApiKey = null;

function loadApiKey() {
    if (cachedApiKey) return cachedApiKey;
    try {
        if (fs.existsSync(ENV_PATH)) {
            const env = fs.readFileSync(ENV_PATH, 'utf-8');
            const m = env.match(/SILICONFLOW_API_KEY\s*=\s*(.+)/);
            if (m) { cachedApiKey = m[1].trim(); return cachedApiKey; }
        }
        if (fs.existsSync(CONFIG_PATH)) {
            const cfg = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
            if (cfg.siliconflow && cfg.siliconflow.apiKey) {
                cachedApiKey = cfg.siliconflow.apiKey; return cachedApiKey;
            }
        }
    } catch (e) { log('[Proxy] 加载 API Key 失败: ' + e.message); }
    return null;
}

// ============================================================
//  DeepSeek API Key — 转发时替换 Authorization 头
//  优先级: 环境变量 DEEPSEEK_API_KEY → tools/.env → .codex/config.toml
// ============================================================
let cachedDeepSeekKey = null;

function loadDeepSeekKey() {
    if (cachedDeepSeekKey) return cachedDeepSeekKey;
    try {
        if (process.env.DEEPSEEK_API_KEY) {
            cachedDeepSeekKey = process.env.DEEPSEEK_API_KEY.trim();
            return cachedDeepSeekKey;
        }
        if (fs.existsSync(ENV_PATH)) {
            const env = fs.readFileSync(ENV_PATH, 'utf-8');
            const m = env.match(/DEEPSEEK_API_KEY\s*=\s*(.+)/);
            if (m && m[1].trim()) { cachedDeepSeekKey = m[1].trim(); return cachedDeepSeekKey; }
        }
        const tomlPath = path.join(process.env.USERPROFILE || process.env.HOME || '', '.codex', 'config.toml');
        if (fs.existsSync(tomlPath)) {
            const toml = fs.readFileSync(tomlPath, 'utf-8');
            const m = toml.match(/experimental_bearer_token\s*=\s*"([^"]+)"/);
            if (m && m[1]) { cachedDeepSeekKey = m[1]; return cachedDeepSeekKey; }
        }
    } catch (e) {
        log('[Proxy] 加载 DeepSeek Key 失败: ' + e.message);
    }
    return null;
}

function callVLAPI(base64Image, promptText) {
    return new Promise((resolve, reject) => {
        const apiKey = loadApiKey();
        if (!apiKey) return reject(new Error('API Key 未配置'));
        const body = JSON.stringify({
            model: VL_MODEL,
            messages: [{
                role: 'user',
                content: [
                    { type: 'image_url', image_url: { url: base64Image } },
                    { type: 'text', text: promptText }
                ]
            }],
            max_tokens: 1024
        });
        const url = new URL(VL_API_URL);
        const options = {
            hostname: url.hostname,
            path: url.pathname,
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + apiKey,
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body)
            },
            timeout: 30000
        };
        const req = https.request(options, (res) => {
            const chunks = [];
            res.on('data', c => chunks.push(c));
            res.on('end', () => {
                try {
                    const data = JSON.parse(Buffer.concat(chunks).toString());
                    if (data.choices && data.choices[0]) {
                        resolve(data.choices[0].message.content);
                    } else {
                        reject(new Error(data.message || 'API 返回异常'));
                    }
                } catch (e) { reject(e); }
            });
        });
        req.on('error', reject);
        req.on('timeout', () => { req.destroy(); reject(new Error('VL API 超时')); });
        req.write(body);
        req.end();
    });
}

// ============================================================
//  本地视觉模型调用 (Ollama /api/chat，images 传 base64)
// ============================================================
function callLocalVLM(base64Image, promptText) {
    return new Promise((resolve, reject) => {
        const url = new URL(OLLAMA_URL + '/api/chat');
        const b64 = base64Image.startsWith('data:') ? base64Image.split(',')[1] : base64Image;
        const body = JSON.stringify({
            model: LOCAL_VL_MODEL,
            messages: [{
                role: 'user',
                content: promptText,
                images: [b64]
            }],
            stream: false,
            options: { num_predict: 1024 }
        });
        const options = {
            hostname: url.hostname,
            port: url.port || 11434,
            path: url.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body)
            },
            timeout: 120000
        };
        const req = http.request(options, (res) => {
            const chunks = [];
            res.on('data', c => chunks.push(c));
            res.on('end', () => {
                try {
                    const data = JSON.parse(Buffer.concat(chunks).toString());
                    if (data.message && data.message.content) {
                        resolve(data.message.content);
                    } else {
                        reject(new Error(data.error || 'Ollama 返回异常'));
                    }
                } catch (e) { reject(e); }
            });
        });
        req.on('error', reject);
        req.on('timeout', () => { req.destroy(); reject(new Error('本地 VLM 超时')); });
        req.write(body);
        req.end();
    });
}

function isOnline() {
    return new Promise((resolve) => {
        const apiKey = loadApiKey();
        if (!apiKey) return resolve(false);
        const req = https.get('https://api.siliconflow.cn/v1/models', {
            headers: { 'Authorization': 'Bearer ' + apiKey },
            timeout: 5000
        }, (res) => {
            resolve(res.statusCode === 200);
        });
        req.on('error', () => resolve(false));
        req.on('timeout', () => { req.destroy(); resolve(false); });
    });
}

// ============================================================
//  日志
// ============================================================
function log(msg) {
    const ts = new Date().toISOString().replace('T', ' ').substring(0, 19);
    const line = `[${ts}] ${msg}`;
    console.log(line);
    try {
        fs.appendFileSync(LOG_FILE, line + '\n');
    } catch (_) {}
}

function rotateLog() {
    try {
        if (fs.existsSync(LOG_FILE) && fs.statSync(LOG_FILE).size > LOG_MAX_SIZE) {
            const bak = LOG_FILE + '.1';
            if (fs.existsSync(bak)) fs.unlinkSync(bak);
            fs.renameSync(LOG_FILE, bak);
            log('[Proxy] 日志轮转完成');
        }
    } catch (_) {}
}

// ============================================================
//  OCR Worker（单例 + 自动重建）
// ============================================================
let ocrWorker = null;
let ocrCount = 0;

async function getWorker() {
    if (!ocrWorker || ocrCount >= WORKER_MAX_OCR) {
        if (ocrWorker) {
            log('[Proxy] 重建 worker（已达 ' + WORKER_MAX_OCR + ' 次 OCR 上限）');
            try { await ocrWorker.terminate(); } catch (_) {}
            ocrWorker = null;
        }
        log('[Proxy] 初始化 tesseract worker (chi_sim+eng)...');
        try {
            ocrWorker = await Tesseract.createWorker('chi_sim+eng');
            ocrCount = 0;
        } catch (e) {
            log('[Proxy] Worker 初始化失败: ' + e.message);
            throw e;
        }
    }
    return ocrWorker;
}

async function ocrImage(imageData) {
    let buffer;
    if (imageData.startsWith('data:')) {
        const base64 = imageData.split(',')[1];
        buffer = Buffer.from(base64, 'base64');
    } else if (imageData.startsWith('http://') || imageData.startsWith('https://')) {
        const resp = await fetch(imageData);
        buffer = Buffer.from(await resp.arrayBuffer());
    } else {
        buffer = Buffer.from(imageData, 'base64');
    }

    const worker = await getWorker();
    const { data } = await worker.recognize(buffer);
    ocrCount++;
    return data.text;
}

// ============================================================
//  Body 解析
// ============================================================
function parseBody(req) {
    return new Promise((resolve, reject) => {
        const chunks = [];
        req.on('data', c => chunks.push(c));
        req.on('end', () => resolve(Buffer.concat(chunks)));
        req.on('error', reject);
    });
}

// ============================================================
//  预处理 — 替换 image_url 为 OCR 文本
// ============================================================
// 纯文字意图关键词 — 命中则直接走 OCR（快、准，不浪费 VLM）
// 纯文字意图正则 — 命中则直接走 OCR（快、准，不浪费 VLM）
const OCR_INTENT_PATTERNS = [
    /提取.{0,12}文字/,
    /识别.{0,12}文字/,
    /读取.{0,12}文字/,
    /转录/,
    /转文字/,
    /文字内容/,
    /图中.{0,6}文字/,
    /图里.{0,6}文字/,
    /把.{0,6}文字/,
    /翻译.{0,8}文字/,
    /\bOCR\b/i,
    /extract.{0,12}text/i,
    /read.{0,12}text/i,
    /transcribe/i
];

function shouldUseOCR(promptText) {
    if (!promptText) return false;
    return OCR_INTENT_PATTERNS.some(re => re.test(promptText));
}

// 云端熔断：连续失败 N 次后，短时间内直接走本地 VLM，避免每次干等超时
let cloudFailCount = 0;
let cloudCooldownUntil = 0;
const CLOUD_FAIL_THRESHOLD = 2;
const CLOUD_COOLDOWN_MS = 5 * 60 * 1000;

function cloudOnCooldown() {
    if (Date.now() < cloudCooldownUntil) {
        return cloudFailCount >= CLOUD_FAIL_THRESHOLD;
    }
    cloudFailCount = 0;
    return false;
}

function recordCloudSuccess() {
    cloudFailCount = 0;
    cloudCooldownUntil = 0;
}

function recordCloudFailure() {
    cloudFailCount++;
    if (cloudFailCount >= CLOUD_FAIL_THRESHOLD) {
        cloudCooldownUntil = Date.now() + CLOUD_COOLDOWN_MS;
        log('[Proxy] 云端 VL 连续失败 ' + cloudFailCount + ' 次，进入 ' + (CLOUD_COOLDOWN_MS / 60000) + ' 分钟冷却，改用本地 VLM');
    }
}

function hasImages(parts) {
    return Array.isArray(parts) && parts.some(p =>
        p.type === 'image_url' || p.type === 'image' ||
        p.type === 'input_image' || p.type === 'image_file'
    );
}


// ============================================================
//  响应过滤 -- 去除 tool result 中的 base64 图片数据
// ============================================================
function stripImageBase64(jsonStr) {
    // 格式1: Responses API -- image_url 直接是字符串
    jsonStr = jsonStr.replace(
        /("image_url"\s*:\s*)"data:image\/[^;]+;base64,[^"]+"/g,
        (m, prefix) => prefix + '"[base64 omitted ' + Math.round((m.length - prefix.length - 2) * 0.75 / 1024) + 'KB]"'
    );
    // 格式2: Chat Completions -- image_url 是对象 {url: "data:..."}
    jsonStr = jsonStr.replace(
        /("url"\s*:\s*)"data:image\/[^;]+;base64,[^"]+"/g,
        (m, prefix) => prefix + '"[base64 omitted ' + Math.round((m.length - prefix.length - 2) * 0.75 / 1024) + 'KB]"'
    );
    return jsonStr;
}

async function processOneImage(part, promptText) {
    const url = part.image_url?.url || part.image_url || part.source?.data || part.file_id || '';
    if (!url || typeof url !== 'string' || url.length < 10) {
        log('[Proxy] 跳过无法解析的图片: type=' + part.type);
        return { result: part, cached: false };
    }

    // 1) 查缓存
    const hash = imageHash(url);
    const cached = cacheGet(hash);
    if (cached) {
        log('[Proxy] 缓存命中 (' + hash.substring(0, 8) + '): ' + cached.text.length + ' 字符');
        return { result: { type: 'input_text', text: cached.text }, cached: true };
    }

    const vlPrompt = '请用中文完整描述这张图片的视觉内容和所有文字信息。要求准确提取图中所有文字，同时详细描述图片中的物体、人物、场景、颜色和构图。';

    // 2) 预判断：纯文字意图 → 直接 OCR（快、准）
    if (shouldUseOCR(promptText)) {
        log('[Proxy] 检测到纯文字意图，直接 OCR (' + hash.substring(0, 8) + ')...');
        try {
            const ocrText = await ocrImage(url);
            const text = '[OCR提取内容]:\n' + ocrText;
            log('[Proxy] OCR 完成 (' + hash.substring(0, 8) + '): ' + ocrText.length + ' 字符');
            cacheSet(hash, text, 'ocr');
            return { result: { type: 'input_text', text }, cached: false };
        } catch (e) {
            log('[Proxy] OCR 失败 (' + hash.substring(0, 8) + '): ' + e.message);
            return { result: { type: 'input_text', text: '[OCR失败: ' + e.message + ']' }, cached: false };
        }
    }

    // 3) VLM 链路：云端优先，本地 Ollama 兜底
    if (!cloudOnCooldown()) {
        log('[Proxy] 尝试云端 VL API (' + hash.substring(0, 8) + ')...');
        try {
            const vlText = await callVLAPI(url, vlPrompt);
            if (vlText && vlText.length > 10) {
                const text = '[图片描述]:\n' + vlText;
                log('[Proxy] 云端 VL 完成 (' + hash.substring(0, 8) + '): ' + vlText.length + ' 字符');
                recordCloudSuccess();
                cacheSet(hash, text, 'vl');
                return { result: { type: 'input_text', text }, cached: false };
            }
        } catch (vlErr) {
            recordCloudFailure();
            log('[Proxy] 云端 VL 失败 (' + hash.substring(0, 8) + '): ' + vlErr.message + '，回退本地 VLM');
        }
    } else {
        log('[Proxy] 云端 VL 处于冷却期，直接使用本地 VLM (' + hash.substring(0, 8) + ')...');
    }

    // 4) 本地 VLM (Ollama) 兜底
    log('[Proxy] 尝试本地 VLM ' + LOCAL_VL_MODEL + ' (' + hash.substring(0, 8) + ')...');
    try {
        const localText = await callLocalVLM(url, vlPrompt);
        if (localText && localText.length > 10) {
            const text = '[图片描述]:\n' + localText;
            log('[Proxy] 本地 VLM 完成 (' + hash.substring(0, 8) + '): ' + localText.length + ' 字符');
            cacheSet(hash, text, 'local');
            return { result: { type: 'input_text', text }, cached: false };
        }
    } catch (localErr) {
        log('[Proxy] 本地 VLM 失败 (' + hash.substring(0, 8) + '): ' + localErr.message);
        return { result: { type: 'input_text', text: '[图片理解失败: ' + localErr.message + ']' }, cached: false };
    }
}

async function preprocessContent(parts) {
    if (!Array.isArray(parts)) return parts;

    // 收集同一消息中的文本部分，用于纯文字意图预判断
    const promptText = parts
        .filter(p => p.type === 'text' || p.type === 'input_text' || p.type === 'output_text')
        .map(p => (typeof p.text === 'string' ? p.text : ''))
        .join(' ');

    // 分离：标记每个 part 是图片还是透传
    const imageIndices = [];
    for (let i = 0; i < parts.length; i++) {
        const p = parts[i];
        const isImage = p.type === 'image_url' || p.type === 'image' ||
                        p.type === 'input_image' || p.type === 'image_file';
        if (isImage) imageIndices.push(i);
    }

    if (imageIndices.length === 0) return parts;

    // 并行处理所有图片
    const imageParts = imageIndices.map(i => parts[i]);
    const processed = await Promise.all(imageParts.map(p => processOneImage(p, promptText)));

    // 统计
    const cachedCount = processed.filter(p => p.cached).length;
    const newCount = processed.length - cachedCount;
    if (cachedCount > 0) {
        log('[Proxy] 图片处理: ' + processed.length + ' 张 (' + cachedCount + ' 缓存命中, ' + newCount + ' 新处理)');
    }

    // 重建结果数组（保持原始顺序）
    const results = [...parts];
    for (let j = 0; j < imageIndices.length; j++) {
        results[imageIndices[j]] = processed[j].result;
    }
    return results;
}

// ============================================================
//  模型判断
// ============================================================
function needsOCR(model) {
    if (!model) return true;
    const m = model.toLowerCase();
    return TEXT_ONLY_PATTERNS.some(p => m.includes(p));
}

// ============================================================
//  端口去重
// ============================================================
async function portAvailable(port) {
    return new Promise(resolve => {
        const s = net.createServer();
        s.once('error', () => resolve(false));
        s.once('listening', () => { s.close(); resolve(true); });
        // 与 server.listen 保持一致（0.0.0.0），否则端口占用检测失效
        s.listen(port);
    });
}

// ============================================================
//  预热
// ============================================================
async function warmup() {
    log('[Proxy] 预热 tesseract 语言数据...');
    try {
        const worker = await getWorker();
        const minPng = Buffer.from(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            'base64'
        );
        await worker.recognize(minPng);
        log('[Proxy] 预热完成');
    } catch (e) {
        log('[Proxy] 预热失败（不影响使用，首次 OCR 稍慢）: ' + e.message);
    }
}

// ============================================================
//  优雅关闭
// ============================================================
async function gracefulShutdown(signal) {
    log('[Proxy] 收到 ' + signal + '，优雅关闭...');
    server.close();
    if (ocrWorker) {
        try { await ocrWorker.terminate(); } catch (_) {}
        ocrWorker = null;
    }
    log('[Proxy] 已关闭');
    process.exit(0);
}

// ============================================================
//  HTTP 服务器
// ============================================================
const server = http.createServer(async (clientReq, clientRes) => {
    try {
        const body = await parseBody(clientReq);
        const ct = clientReq.headers['content-type'] || '';
        let modifiedBody = body;

        if (ct.includes('application/json') && body.length > 0) {
            const reqJson = JSON.parse(body.toString('utf-8'));
            const model = reqJson.model || '';
            let modified = false;

            if (needsOCR(model)) {
                // Responses API 格式
                if (reqJson.input && Array.isArray(reqJson.input)) {
                    for (let i = 0; i < reqJson.input.length; i++) {
                        const msg = reqJson.input[i];
                        if (msg.content && hasImages(msg.content)) {
                            reqJson.input[i].content = await preprocessContent(msg.content);
                            modified = true;
                        }
                        // 处理 function_call_output 中的 output 数组（tool result 中的图片）
                        if (msg.output && Array.isArray(msg.output) && hasImages(msg.output)) {
                            reqJson.input[i].output = await preprocessContent(msg.output);
                            modified = true;
                        }
                    }
                }
                // Chat Completions API 格式
                if (reqJson.messages && Array.isArray(reqJson.messages)) {
                    for (let i = 0; i < reqJson.messages.length; i++) {
                        const msg = reqJson.messages[i];
                        if (msg.content && hasImages(msg.content)) {
                            reqJson.messages[i].content = await preprocessContent(msg.content);
                            modified = true;
                        }
                    }
                }
                if (modified) log('[Proxy] [OK] 图片处理完成，请求已修改');
            }

            modifiedBody = Buffer.from(JSON.stringify(reqJson), 'utf-8');
        }

        // ========== 关键：SSE 流式转发修复（不得删除） ==========
        // 1. 请求转发前去除 hop-by-hop 头部
        const fwdHeaders = { ...clientReq.headers };
        delete fwdHeaders['host'];
        delete fwdHeaders['connection'];
        delete fwdHeaders['keep-alive'];
        delete fwdHeaders['transfer-encoding'];
        fwdHeaders['content-length'] = String(modifiedBody.length);

        const options = {
            hostname: UPSTREAM.host,
            port: UPSTREAM.port,
            path: clientReq.url,
            method: clientReq.method,
            headers: fwdHeaders
        };

        // 直连 DeepSeek 官网：替换 Authorization 为 DeepSeek API Key
        const dsKey = loadDeepSeekKey();
        if (dsKey) {
            options.headers['authorization'] = 'Bearer ' + dsKey;
        } else {
            log('[Proxy] 警告: 未配置 DeepSeek API Key，上游可能拒绝认证');
        }

        const transport = UPSTREAM.https ? https : http;
        const upstreamReq = transport.request(options, (upstreamRes) => {
            // 2. 响应转发前去除 Content-Length（SSE 流式响应关键）
            const resHeaders = { ...upstreamRes.headers };
            delete resHeaders['content-length'];
            delete resHeaders['connection'];
            delete resHeaders['keep-alive'];
            delete resHeaders['transfer-encoding'];
            const isSSE = (upstreamRes.headers['content-type'] || '').includes('text/event-stream');

            if (isSSE) {
                // SSE 流式响应：快速透传 + 按需过滤
                clientRes.writeHead(upstreamRes.statusCode, resHeaders);
                let filteredBytes = 0;
                upstreamRes.on('data', (chunk) => {
                    // 快速预检：chunk 不含 data:image 则直接透传原始 Buffer
                    if (chunk.indexOf('data:image') === -1) {
                        clientRes.write(chunk);
                        return;
                    }
                    // 仅在检测到 base64 特征时才做字符串转换和正则过滤
                    let str = chunk.toString('utf-8');
                    const before = str.length;
                    str = stripImageBase64(str);
                    if (str.length !== before) {
                        filteredBytes += (before - str.length);
                    }
                    clientRes.write(str);
                });
                upstreamRes.on('end', () => {
                    if (filteredBytes > 0) {
                        log('[Proxy] \u2713 SSE 响应 base64 过滤完成: 节省 ' + filteredBytes + ' bytes');
                    }
                    clientRes.end();
                });
            } else {
                // JSON 响应：collect + filter + forward
                const chunks = [];
                upstreamRes.on('data', (c) => chunks.push(c));
                upstreamRes.on('end', () => {
                    let body = Buffer.concat(chunks).toString('utf-8');

                    if ((upstreamRes.headers['content-type'] || '').includes('application/json')) {
                        try {
                            const before = body.length;
                            body = stripImageBase64(body);
                            if (body.length !== before) {
                                log('[Proxy] \u2713 响应 base64 过滤完成: ' + before + ' -> ' + body.length + ' bytes');
                            }
                        } catch (e) {
                            log('[Proxy] 过滤 base64 异常: ' + e.message);
                        }
                    }

                    clientRes.writeHead(upstreamRes.statusCode, resHeaders);
                    clientRes.end(body);
                });
            }
        });

        // 3. 客户端断连时销毁上游请求
        clientReq.on('close', () => {
            if (!upstreamReq.destroyed) upstreamReq.destroy();
        });
        // ======================================================

        upstreamReq.on('error', e => {
            log('[Proxy] 上游请求错误: ' + e.message);
            if (!clientRes.headersSent) {
                clientRes.writeHead(502, { 'Content-Type': 'text/plain' });
            }
            clientRes.end('Proxy upstream error: ' + e.message);
        });

        upstreamReq.write(modifiedBody);
        upstreamReq.end();

    } catch (err) {
        log('[Proxy] 处理请求异常: ' + err.message);
        if (!clientRes.headersSent) {
            clientRes.writeHead(500, { 'Content-Type': 'text/plain' });
        }
        clientRes.end('Proxy error: ' + err.message);
    }
});

// ============================================================
//  启动
// ============================================================
async function main() {
    // 确保日志目录存在
    try { fs.mkdirSync(LOG_DIR, { recursive: true }); } catch (_) {}

    rotateLog();
    log('========================================');
    log('  Codex 图片理解代理 v5（云端VL + 本地VLM + OCR 三级路由）');
    log('  端口: ' + PROXY_PORT + '  上游: ' + (UPSTREAM.https ? 'https://' : 'http://') + UPSTREAM.host + ':' + UPSTREAM.port);
    log('  缓存上限: ' + IMAGE_CACHE_MAX + ' 条 | 云端 VL 超时: 30s | 本地 VLM 超时: 120s');
    log('  本地 VLM: ' + OLLAMA_URL + ' 模型 ' + LOCAL_VL_MODEL);
    log('  日志: ' + LOG_FILE);
    log('========================================');

    // 端口去重
    const avail = await portAvailable(PROXY_PORT);
    if (!avail) {
        log('[Proxy] 端口 ' + PROXY_PORT + ' 已被占用，代理已在运行');
        process.exit(0);
    }

    // 启动服务器
    server.listen(PROXY_PORT, () => {
        log('[Proxy] HTTP 服务器已启动');
    });

    // 后台预热（不阻塞）
    warmup();
}

// 注册优雅关闭
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

main().catch(e => {
    log('[Proxy] 启动失败: ' + e.message);
    process.exit(1);
});
