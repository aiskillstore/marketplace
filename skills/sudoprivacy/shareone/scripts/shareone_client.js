const http = require('http');
const https = require('https');
const os = require('os');
const fs = require('fs');
const path = require('path');

const DEFAULT_BASE_URL = 'https://shareone.app';
const CREDENTIALS_PATH = path.join(os.homedir(), '.shareone_credentials');
const SUDOWORK_SECRET_NAMESPACE = 'service:shareone';
const SUDOWORK_SECRET_KEY = 'X-API-Key';

function isSudowork() {
    return Boolean(process.env.SUDOWORK_AUTH_PROXY_URL && process.env.SUDOWORK_AUTH_PROXY_TOKEN);
}

function getSudoworkBaseUrl() {
    return process.env.SUDOWORK_AUTH_PROXY_BASE_URL || String(process.env.SUDOWORK_AUTH_PROXY_URL || '').replace(/\/proxy\/?$/, '');
}

function getBaseUrl() {
    return process.env.SHAREONE_BASE_URL || DEFAULT_BASE_URL;
}

function getCredentialsPath() {
    return CREDENTIALS_PATH;
}

function readLocalApiKey() {
    if (!fs.existsSync(CREDENTIALS_PATH)) return null;
    try {
        const data = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
        return data && data.api_key ? data.api_key : null;
    } catch (_) {
        return null;
    }
}

function resolveDirectApiKey(explicitApiKey) {
    return explicitApiKey || process.env.SHAREONE_API_KEY || readLocalApiKey();
}

function saveLocalApiKey(apiKey) {
    fs.writeFileSync(CREDENTIALS_PATH, JSON.stringify({ api_key: apiKey }));
}

function deleteLocalApiKey() {
    if (!fs.existsSync(CREDENTIALS_PATH)) return false;
    fs.unlinkSync(CREDENTIALS_PATH);
    return true;
}

function appendPath(baseUrl, apiPath) {
    const trimmedBase = String(baseUrl).replace(/\/+$/, '');
    const normalizedPath = apiPath.startsWith('/') ? apiPath : `/${apiPath}`;
    return `${trimmedBase}${normalizedPath}`;
}

function requestBuffer(url, options = {}, body = null) {
    return new Promise((resolve, reject) => {
        const target = new URL(url);
        const client = target.protocol === 'https:' ? https : http;
        const req = client.request(target, {
            method: options.method || 'GET',
            headers: options.headers || {},
        }, (res) => {
            const chunks = [];
            res.on('data', chunk => chunks.push(Buffer.from(chunk)));
            res.on('end', () => {
                const data = Buffer.concat(chunks);
                const text = data.toString('utf8');
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    resolve({ statusCode: res.statusCode, headers: res.headers, data, text });
                    return;
                }
                const error = new Error(`HTTP ${res.statusCode}: ${text}`);
                error.statusCode = res.statusCode;
                error.responseText = text;
                reject(error);
            });
        });

        req.on('error', reject);
        if (options.timeoutMs) {
            req.setTimeout(options.timeoutMs, () => {
                req.destroy(new Error('Request timed out'));
            });
        }
        if (body) req.write(body);
        req.end();
    });
}

function buildJsonRequestBody(payload) {
    const body = payload === null ? null : JSON.stringify(payload);
    const headers = { 'Content-Type': 'application/json' };
    if (body !== null) headers['Content-Length'] = Buffer.byteLength(body);
    return { body, headers };
}

async function requestJsonUrl(url, options = {}, payload = null) {
    const { body, headers } = buildJsonRequestBody(payload);
    const res = await requestBuffer(url, {
        ...options,
        headers: {
            ...headers,
            ...(options.headers || {}),
        },
    }, body);
    return JSON.parse(res.text);
}

async function requestPublicShareOneJson(apiPath, options = {}, payload = null) {
    return requestJsonUrl(appendPath(getBaseUrl(), apiPath), options, payload);
}

function buildSudoworkSecretsUrl(pathSuffix = '') {
    const baseUrl = getSudoworkBaseUrl();
    if (!baseUrl) {
        throw new Error('SUDOWORK_AUTH_PROXY_BASE_URL is not available');
    }
    return appendPath(baseUrl, `/secrets${pathSuffix}`);
}

async function requestSudoworkSecrets(pathSuffix = '', options = {}, payload = null) {
    if (!isSudowork()) {
        throw new Error('Sudowork environment is not available');
    }
    const { body, headers } = buildJsonRequestBody(payload);
    const res = await requestBuffer(buildSudoworkSecretsUrl(pathSuffix), {
        ...options,
        headers: {
            ...headers,
            ...(options.headers || {}),
            Authorization: `Bearer ${process.env.SUDOWORK_AUTH_PROXY_TOKEN}`,
        },
    }, body);
    return JSON.parse(res.text);
}

async function listSudoworkSecrets(namespace = SUDOWORK_SECRET_NAMESPACE) {
    const query = `?namespace=${encodeURIComponent(namespace)}`;
    const result = await requestSudoworkSecrets(query, { method: 'GET' }, null);
    return Array.isArray(result.data) ? result.data : [];
}

async function hasSudoworkApiKey() {
    const secrets = await listSudoworkSecrets(SUDOWORK_SECRET_NAMESPACE);
    return secrets.some(secret => secret && secret.namespace === SUDOWORK_SECRET_NAMESPACE && secret.key === SUDOWORK_SECRET_KEY);
}

async function saveSudoworkApiKey(apiKey) {
    const pathSuffix = `/${encodeURIComponent(SUDOWORK_SECRET_NAMESPACE)}/${encodeURIComponent(SUDOWORK_SECRET_KEY)}`;
    return requestSudoworkSecrets(pathSuffix, { method: 'PUT' }, {
        value: apiKey,
        description: 'ShareOne API Key',
    });
}

async function deleteSudoworkApiKey() {
    const pathSuffix = `/${encodeURIComponent(SUDOWORK_SECRET_NAMESPACE)}/${encodeURIComponent(SUDOWORK_SECRET_KEY)}`;
    return requestSudoworkSecrets(pathSuffix, { method: 'DELETE' }, null);
}

function buildShareOneRequest(apiPath, options = {}) {
    const targetUrl = appendPath(getBaseUrl(), apiPath);
    const headers = { ...(options.headers || {}) };

    if (isSudowork() && options.authRequired !== false) {
        delete headers['X-API-Key'];
        delete headers['x-api-key'];
        return {
            url: process.env.SUDOWORK_AUTH_PROXY_URL,
            options: {
                ...options,
                headers: {
                    ...headers,
                    Authorization: `Bearer ${process.env.SUDOWORK_AUTH_PROXY_TOKEN}`,
                    'X-Secret-Namespace': 'service:shareone',
                    'X-Remote-URL': targetUrl,
                    'X-Auth-Scheme': 'header',
                    'X-Auth-Header': 'X-API-Key',
                    'X-Secret-Key': 'X-API-Key'
                },
            },
        };
    }

    if (options.authRequired !== false) {
        const apiKey = resolveDirectApiKey(options.apiKey);
        if (apiKey) headers['X-API-Key'] = apiKey;
    }

    return {
        url: targetUrl,
        options: {
            ...options,
            headers,
        },
    };
}

async function requestShareOneBuffer(apiPath, options = {}, body = null) {
    const built = buildShareOneRequest(apiPath, options);
    return requestBuffer(built.url, built.options, body);
}

async function requestShareOneJson(apiPath, options = {}, payload = null) {
    const { body, headers } = buildJsonRequestBody(payload);

    const res = await requestShareOneBuffer(apiPath, {
        ...options,
        headers: {
            ...headers,
            ...(options.headers || {}),
        },
    }, body);
    return JSON.parse(res.text);
}

function getErrorDetail(error) {
    const text = String(error && error.responseText ? error.responseText : '');
    if (!text) return '';
    try {
        const parsed = JSON.parse(text);
        return String(parsed.detail || parsed.message || text);
    } catch (_) {
        return text;
    }
}

function isSudoworkMissingKeyError(error) {
    if (!error) return false;
    const detail = getErrorDetail(error);

    if (error.statusCode === 502) {
        return /secret|key|credential|not found|missing|未配置|不存在|缺少/i.test(detail || error.message || '');
    }

    if (error.statusCode !== 401) return false;
    return /Missing API Key/i.test(detail);
}

function isAuthFailedError(error) {
    if (!error) return false;
    if (error.statusCode === 401 || error.statusCode === 403) return true;
    const detail = getErrorDetail(error);
    return /Invalid API Key|Inactive user|unauthorized|forbidden|权限不足|无效/i.test(detail || error.message || '');
}

function printShareOneScriptError(error) {
    if (isSudowork() && isSudoworkMissingKeyError(error)) {
        console.error("ERROR:SUDOWORK_KEY_NOT_FOUND");
        console.error("请先运行 check_api_key.js，并按提示通过 save_api_key.js 或 create_guest_key.js 设置 ShareOne API Key。");
        return;
    }

    if (isAuthFailedError(error)) {
        console.error("ERROR:AUTH_FAILED");
        console.error("API Key 无效或权限不足。");
        return;
    }

    console.error(`ERROR:${error.message}`);
}

module.exports = {
    DEFAULT_BASE_URL,
    SUDOWORK_SECRET_KEY,
    SUDOWORK_SECRET_NAMESPACE,
    appendPath,
    deleteLocalApiKey,
    deleteSudoworkApiKey,
    getBaseUrl,
    getCredentialsPath,
    hasSudoworkApiKey,
    isSudowork,
    isAuthFailedError,
    isSudoworkMissingKeyError,
    listSudoworkSecrets,
    printShareOneScriptError,
    readLocalApiKey,
    requestBuffer,
    requestPublicShareOneJson,
    requestShareOneBuffer,
    requestShareOneJson,
    resolveDirectApiKey,
    saveLocalApiKey,
    saveSudoworkApiKey,
};
