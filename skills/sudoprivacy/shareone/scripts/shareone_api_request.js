#!/usr/bin/env node

const fs = require('fs');
const {
    CREDENTIAL_MODE_SUDOWORK_PROXY,
    detectCredentialMode,
    printShareOneScriptError,
    requestShareOneBuffer,
    resolveDirectApiKey,
} = require('./shareone_client');

const args = process.argv.slice(2);
let method = 'GET';
let apiPath = null;
let data = null;
let dataFile = null;
let apiKey = null;
let publicRequest = false;

function usage() {
    console.error("Usage: node shareone_api_request.js <api_path> [--method GET|POST|PUT|DELETE] [--data '<json>' | --data-file <path|-> ] [--api-key <key>] [--public]");
    console.error("  --data-file <path>  read the request body from a file ('-' for stdin); preferred for non-ASCII or nested-JSON bodies to avoid shell quoting issues.");
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
    if (args[i] === '--method') {
        method = String(nextValue(i, args[i])).toUpperCase();
        i += 1;
    } else if (args[i] === '--data') {
        data = nextValue(i, args[i]);
        i += 1;
    } else if (args[i] === '--data-file') {
        dataFile = nextValue(i, args[i]);
        i += 1;
    } else if (args[i] === '--api-key') {
        apiKey = nextValue(i, args[i]);
        i += 1;
    } else if (args[i] === '--public') {
        publicRequest = true;
    } else if (!args[i].startsWith('--') && !apiPath) {
        apiPath = args[i];
    } else {
        console.error(`ERROR:UNKNOWN_ARGUMENT:${args[i]}`);
        usage();
        process.exit(1);
    }
}

if (!apiPath) {
    usage();
    process.exit(1);
}

// Prefer --data-file for bodies that are awkward to pass inline (CJK text,
// nested/escaped JSON): file/stdin bytes reach the request verbatim, free of
// shell quoting.
if (dataFile !== null) {
    if (data !== null) {
        console.error("ERROR:BAD_ARGS");
        console.error("Pass either --data or --data-file, not both.");
        process.exit(1);
    }
    try {
        data = fs.readFileSync(dataFile === '-' ? 0 : dataFile, 'utf8');
    } catch (error) {
        console.error(`ERROR:DATA_FILE_UNREADABLE: ${error.message}`);
        process.exit(1);
    }
}

const headers = {};
let body = null;
if (data !== null) {
    body = data;
    headers['Content-Type'] = 'application/json';
    headers['Content-Length'] = Buffer.byteLength(body);
}

(async () => {
    const credentialMode = await detectCredentialMode();
    if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY && apiKey && !publicRequest) {
        console.error("ERROR:SUDOWORK_MANAGED_KEY");
        console.error("Sudowork 模式下不要传 --api-key；请通过本 skill 的 save_api_key.js 或 create_guest_key.js 设置 ShareOne API Key。");
        process.exit(1);
    }

    if (!publicRequest && credentialMode.mode !== CREDENTIAL_MODE_SUDOWORK_PROXY && !resolveDirectApiKey(apiKey)) {
        console.error("ERROR:KEY_NOT_FOUND");
        process.exit(1);
    }

    return requestShareOneBuffer(apiPath, {
        method,
        apiKey,
        authRequired: !publicRequest,
        headers,
    }, body);
})().then((res) => {
    process.stdout.write(res.data);
}).catch((error) => {
    process.exit(printShareOneScriptError(error));
});
