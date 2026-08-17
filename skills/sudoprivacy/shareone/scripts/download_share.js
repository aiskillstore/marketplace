#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const {
    CREDENTIAL_MODE_SUDOWORK_PROXY,
    detectCredentialMode,
    extractShareRef,
    requestShareOneBuffer,
    resolveDirectApiKey,
} = require('./shareone_client');

const ACTIVE_TASK_FILENAME = '.shareone_active_task';

const args = process.argv.slice(2);
let ref = null;
let password = null;
let apiKey = null;
let publicOnly = false;
let save = false;
let taskAnchor = false;

function usage() {
    console.error("Usage: node download_share.js <ref> [--password <password>] [--api-key <key>] [--public-only] [--save] [--task-anchor]");
}

function nextValue(index, flag) {
    const value = args[index + 1];
    if (value === undefined || value.startsWith('--')) {
        console.error(`ERROR:MISSING_VALUE:${flag}`);
        usage();
        process.exit(1);
    }
    return value;
}

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--ref') {
        ref = nextValue(i, args[i]);
        i += 1;
    } else if (args[i] === '--password') {
        password = nextValue(i, args[i]);
        i += 1;
    } else if (args[i] === '--api-key') {
        apiKey = nextValue(i, args[i]);
        i += 1;
    } else if (args[i] === '--public-only') {
        publicOnly = true;
    } else if (args[i] === '--save') {
        save = true;
    } else if (args[i] === '--task-anchor') {
        taskAnchor = true;
        save = true;
    } else if (!args[i].startsWith('--') && !ref) {
        ref = args[i];
    } else {
        console.error(`ERROR:UNKNOWN_ARGUMENT:${args[i]}`);
        usage();
        process.exit(1);
    }
}

if (!ref) {
    usage();
    process.exit(1);
}

async function tryOwnerDownload(credentialMode) {
    if (publicOnly) return null;
    const hasKey = credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY
        ? credentialMode.hasSudoworkKey
        : Boolean(resolveDirectApiKey(apiKey));
    if (!hasKey) return null;
    const shareRef = extractShareRef(ref);
    if (!shareRef) return null;
    try {
        return await requestShareOneBuffer(`/api/v1/shares/${encodeURIComponent(shareRef)}/download`, {
            method: 'GET',
            apiKey,
            authRequired: true,
        });
    } catch (error) {
        if ([401, 403, 404].includes(error.statusCode)) return null;
        throw error;
    }
}

async function publicDownload() {
    if (password !== null) {
        const body = JSON.stringify({ ref, password });
        return requestShareOneBuffer('/api/v1/public-download', {
            method: 'POST',
            authRequired: false,
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body),
            },
        }, body);
    }
    return requestShareOneBuffer(`/api/v1/public-download?ref=${encodeURIComponent(ref)}`, {
        method: 'GET',
        authRequired: false,
    });
}

function parseFilenameFromDisposition(disposition) {
    if (!disposition) return null;
    const utf8Match = /filename\*=utf-8''([^;]+)/i.exec(disposition);
    if (utf8Match) {
        try {
            return decodeURIComponent(utf8Match[1].trim());
        } catch (_) {
            // Fall through to the plain filename form.
        }
    }
    const plainMatch = /filename="?([^";]+)"?/i.exec(disposition);
    return plainMatch ? plainMatch[1].trim() : null;
}

function emitDownloadInfo(headers) {
    const filename = parseFilenameFromDisposition(headers['content-disposition']);
    if (filename) console.error(`INFO:FILENAME:${filename}`);
    if (headers['content-type']) console.error(`INFO:CONTENT_TYPE:${headers['content-type']}`);
}

function sanitizeFilename(name) {
    const base = path.basename(String(name || '').trim());
    const cleaned = base.replace(/[\\/:*?"<>|]/g, '_');
    return cleaned && cleaned !== '.' && cleaned !== '..' ? cleaned : null;
}

function uniqueFilename(name) {
    if (!fs.existsSync(name)) return name;
    const ext = path.extname(name);
    const stem = ext ? name.slice(0, -ext.length) : name;
    for (let i = 1; i < 1000; i++) {
        const candidate = `${stem}-${i}${ext}`;
        if (!fs.existsSync(candidate)) return candidate;
    }
    throw new Error(`Could not choose a non-conflicting filename for ${name}`);
}

function saveDownload(result) {
    const serverName = sanitizeFilename(parseFilenameFromDisposition((result.headers || {})['content-disposition']));
    const shareRef = sanitizeFilename(extractShareRef(ref)) || 'share';

    if (taskAnchor) {
        fs.writeFileSync(ACTIVE_TASK_FILENAME, `${extractShareRef(ref)}\n`);
        console.error(`ANCHOR_WRITTEN:${ACTIVE_TASK_FILENAME}`);
    }

    const preferredName = taskAnchor
        ? `shareone_${shareRef}_source${serverName ? path.extname(serverName) || '.html' : '.html'}`
        : (serverName || `shareone_${shareRef}_download`);
    const outputName = uniqueFilename(preferredName);

    fs.writeFileSync(outputName, result.data);
    console.log(`SAVED:${outputName}`);
}

(async () => {
    const credentialMode = await detectCredentialMode();
    if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY && apiKey && !publicOnly) {
        console.error("ERROR:SUDOWORK_MANAGED_KEY");
        console.error("Sudowork 模式下不要传 --api-key；请通过本 skill 的 save_api_key.js 或 create_guest_key.js 设置 ShareOne API Key。");
        process.exit(1);
    }

    const ownerResult = await tryOwnerDownload(credentialMode);
    const result = ownerResult || await publicDownload();
    emitDownloadInfo(result.headers || {});
    if (save) {
        saveDownload(result);
    } else {
        process.stdout.write(result.data);
    }
})().catch((error) => {
    let code = null;
    try {
        const parsed = JSON.parse(error.responseText || '{}');
        const detail = parsed.detail || {};
        code = typeof detail === 'string' ? detail : detail.code;
    } catch (_) {
        // Keep the original HTTP error if the response is not JSON.
    }
    if (code) {
        console.error(`ERROR:${code}`);
    } else {
        console.error(`ERROR:${error.message}`);
    }
    process.exit(1);
});
