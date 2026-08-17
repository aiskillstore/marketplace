const {
    CREDENTIAL_MODE_DIRECT_FALLBACK,
    CREDENTIAL_MODE_SUDOWORK_PROXY,
    detectCredentialMode,
    isAuthFailedError,
    readLocalApiKey,
    requestShareOneBuffer,
} = require('./shareone_client');

// --validate additionally hits GET /api/v1/me with the resolved credential so a
// revoked/expired key is caught here instead of failing the first real action.
const args = process.argv.slice(2);
for (const arg of args) {
    if (arg !== '--validate') {
        console.error(`ERROR:UNKNOWN_ARGUMENT:${arg}`);
        console.error('Usage: node check_api_key.js [--validate]');
        process.exit(1);
    }
}
const validate = args.includes('--validate');

async function checkApiKey() {
    const credentialMode = await detectCredentialMode({ refresh: true });
    const apiKey = process.env.SHAREONE_API_KEY || readLocalApiKey();

    let hasKey;
    if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY) {
        hasKey = credentialMode.hasSudoworkKey;
        console.log(hasKey ? 'SUDOWORK_ENV_OK_KEY_FOUND' : 'SUDOWORK_ENV_OK_KEY_NOT_FOUND');
    } else if (credentialMode.mode === CREDENTIAL_MODE_DIRECT_FALLBACK) {
        hasKey = Boolean(apiKey);
        console.log(hasKey ? `SUDOWORK_ENV_UNAVAILABLE_KEY_FOUND:${apiKey}` : 'SUDOWORK_ENV_UNAVAILABLE_KEY_NOT_FOUND');
    } else {
        hasKey = Boolean(apiKey);
        console.log(hasKey ? `KEY_FOUND:${apiKey}` : 'KEY_NOT_FOUND');
    }

    if (!validate) return;
    if (!hasKey) {
        console.log('KEY_VALIDATION_SKIPPED_NO_KEY');
        return;
    }

    try {
        await requestShareOneBuffer('/api/v1/me', { method: 'GET', authRequired: true });
        console.log('KEY_VALID');
    } catch (error) {
        console.log(isAuthFailedError(error) ? 'KEY_INVALID' : `KEY_VALIDATION_ERROR:${error.message}`);
    }
}

checkApiKey().catch((error) => {
    console.error(`ERROR:${error.message}`);
    process.exit(1);
});
