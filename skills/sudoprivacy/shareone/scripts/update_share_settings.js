#!/usr/bin/env node

const {
    getBaseUrl,
    isSudowork,
    printShareOneScriptError,
    requestShareOneBuffer,
    resolveDirectApiKey,
} = require('./shareone_client');

const args = process.argv.slice(2);
let ref = null;
let apiKey = null;
let dryRun = false;
let explicitBaseUrl = null;
const payload = {};

function usage() {
    console.error('Usage: node update_share_settings.js <share_link_or_id> [--api-key <key>] [--base-url <url>] [--watermark <text>] [--password <pwd>] [--slug <slug>] [--allow-comments <true|false>] [--dry-run]');
}

function nextValue(index, flag) {
    const value = args[index + 1];
    if (value === undefined) {
        console.error(`ERROR:MISSING_VALUE:${flag}`);
        usage();
        process.exit(1);
    }
    return value;
}

function parseBoolean(value, flag) {
    if (value === 'true') return true;
    if (value === 'false') return false;
    console.error(`ERROR:INVALID_BOOLEAN:${flag}`);
    console.error(`${flag} must be true or false.`);
    process.exit(1);
}

for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--api-key') {
        apiKey = nextValue(i, arg);
        i += 1;
    } else if (arg === '--base-url') {
        explicitBaseUrl = nextValue(i, arg);
        process.env.SHAREONE_BASE_URL = explicitBaseUrl;
        i += 1;
    } else if (arg === '--watermark') {
        payload.watermark = nextValue(i, arg);
        i += 1;
    } else if (arg === '--password') {
        payload.password = nextValue(i, arg);
        i += 1;
    } else if (arg === '--slug' || arg === '--custom-slug') {
        payload.custom_slug = nextValue(i, arg);
        i += 1;
    } else if (arg === '--allow-comments') {
        payload.allow_comments = parseBoolean(nextValue(i, arg), arg);
        i += 1;
    } else if (arg === '--dry-run') {
        dryRun = true;
    } else if (!arg.startsWith('--') && !ref) {
        ref = arg;
    } else {
        console.error(`ERROR:UNKNOWN_ARGUMENT:${arg}`);
        usage();
        process.exit(1);
    }
}

if (!ref) {
    usage();
    process.exit(1);
}

if (Object.keys(payload).length === 0) {
    console.error('ERROR:NO_SETTINGS_PROVIDED');
    console.error('Provide at least one of --watermark, --password, --slug, or --allow-comments.');
    process.exit(1);
}

if (isSudowork() && apiKey && !dryRun) {
    console.error('ERROR:SUDOWORK_MANAGED_KEY');
    console.error('Sudowork 模式下不要传 --api-key；请通过本 skill 的 save_api_key.js 或 create_guest_key.js 设置 ShareOne API Key。');
    process.exit(1);
}

if (!dryRun && !isSudowork() && !resolveDirectApiKey(apiKey)) {
    console.error('ERROR:KEY_NOT_FOUND');
    process.exit(1);
}

function parseRef(input) {
    const raw = String(input || '').trim();
    let path = raw.split('?')[0].split('#')[0];

    try {
        if (raw.includes('://')) {
            const parsed = new URL(raw);
            if (!explicitBaseUrl) {
                process.env.SHAREONE_BASE_URL = `${parsed.protocol}//${parsed.host}`;
            }
            path = parsed.pathname;
        }
    } catch (_) {
        path = raw.split('?')[0].split('#')[0];
    }

    const parts = path.split('/').filter(Boolean);
    const knownPrefixes = new Set(['s', 'md', 'pdf', 'ppt', 'word']);

    if (parts.length >= 2 && knownPrefixes.has(parts[0])) {
        return { prefix: parts[0], shareRef: parts[1] };
    }

    return { prefix: null, shareRef: parts[parts.length - 1] || raw };
}

function endpointForPrefix(prefix, shareRef) {
    const encodedRef = encodeURIComponent(shareRef);
    if (prefix === 's' || prefix === 'md') {
        return `/api/v1/pages/${encodedRef}`;
    }
    if (prefix === 'pdf' || prefix === 'ppt' || prefix === 'word') {
        return `/api/v1/files/${encodedRef}`;
    }
    return null;
}

function buildRequestBody() {
    const body = JSON.stringify(payload);
    return {
        body,
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(body),
        },
    };
}

function shouldRetryAsFile(error) {
    const text = `${error && error.message ? error.message : ''}\n${error && error.responseText ? error.responseText : ''}`;
    return error && error.statusCode === 400 && /only for HTML\/Markdown|Use \/api\/v1\/files|HTML\/Markdown pages/i.test(text);
}

async function putSettings(apiPath) {
    const { body, headers } = buildRequestBody();
    return requestShareOneBuffer(apiPath, {
        method: 'PUT',
        apiKey,
        headers,
    }, body);
}

(async () => {
    const parsed = parseRef(ref);
    const explicitApiPath = endpointForPrefix(parsed.prefix, parsed.shareRef);
    const pageApiPath = `/api/v1/pages/${encodeURIComponent(parsed.shareRef)}`;
    const fileApiPath = `/api/v1/files/${encodeURIComponent(parsed.shareRef)}`;

    if (dryRun) {
        const result = {
            method: 'PUT',
            api_path: explicitApiPath || pageApiPath,
            payload,
            base_url: getBaseUrl(),
        };
        if (!explicitApiPath) {
            result.fallback_api_path = fileApiPath;
        }
        console.log(JSON.stringify(result, null, 2));
        return;
    }

    if (explicitApiPath) {
        const res = await putSettings(explicitApiPath);
        process.stdout.write(res.data);
        return;
    }

    try {
        const res = await putSettings(pageApiPath);
        process.stdout.write(res.data);
    } catch (error) {
        if (!shouldRetryAsFile(error)) {
            throw error;
        }
        const res = await putSettings(fileApiPath);
        process.stdout.write(res.data);
    }
})().catch((error) => {
    printShareOneScriptError(error);
    process.exit(1);
});
