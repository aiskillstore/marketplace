#!/usr/bin/env node

const {
    hasSudoworkApiKey,
    isSudowork,
    requestShareOneBuffer,
    resolveDirectApiKey,
} = require('./shareone_client');

const args = process.argv.slice(2);
let ref = null;
let password = null;
let apiKey = null;
let publicOnly = false;

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--ref') {
        ref = args[++i];
    } else if (args[i] === '--password') {
        password = args[++i];
    } else if (args[i] === '--api-key') {
        apiKey = args[++i];
    } else if (args[i] === '--public-only') {
        publicOnly = true;
    } else if (!args[i].startsWith('--') && !ref) {
        ref = args[i];
    }
}

if (!ref) {
    console.error("Usage: node download_share.js <ref> [--password <password>] [--api-key <key>] [--public-only]");
    process.exit(1);
}

if (isSudowork() && apiKey && !publicOnly) {
    console.error("ERROR:SUDOWORK_MANAGED_KEY");
    console.error("Sudowork 模式下不要传 --api-key；请通过本 skill 的 save_api_key.js 或 create_guest_key.js 设置 ShareOne API Key。");
    process.exit(1);
}

function extractShareRef(value) {
    const raw = String(value || '').trim();
    if (!raw) return null;
    try {
        const parsed = raw.includes('://') ? new URL(raw) : null;
        const path = parsed ? parsed.pathname : raw.split('?')[0].split('#')[0];
        const parts = path.split('/').filter(Boolean);
        if (parts.length === 0) return raw;
        if (parts[0] === 'file' && parts.length >= 2) return parts[1];
        if (parts[0] === 'api' && parts.includes('shares')) {
            const index = parts.indexOf('shares');
            return parts[index + 1] || raw;
        }
        return parts[parts.length - 1] || raw;
    } catch (_) {
        return raw;
    }
}

async function tryOwnerDownload() {
    if (publicOnly) return null;
    let hasKey = Boolean(resolveDirectApiKey(apiKey));
    if (isSudowork()) {
        try {
            hasKey = await hasSudoworkApiKey();
        } catch (_) {
            hasKey = false;
        }
    }
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

(async () => {
    const ownerResult = await tryOwnerDownload();
    const result = ownerResult || await publicDownload();
    process.stdout.write(result.data);
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
