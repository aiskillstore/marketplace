const {
    CREDENTIAL_MODE_SUDOWORK_PROXY,
    detectCredentialMode,
    isSudowork,
    saveLocalApiKey,
    saveSudoworkApiKey,
} = require('./shareone_client');

const apiKey = process.argv[2];
if (!apiKey || process.argv.length > 3) {
    if (process.argv.length > 3) {
        console.error(`ERROR:UNKNOWN_ARGUMENT:${process.argv[3]}`);
    } else {
        console.error("ERROR:MISSING_VALUE:<api_key>");
    }
    console.error("Usage: node save_api_key.js <api_key>");
    process.exit(1);
}

async function saveApiKey() {
    const credentialMode = await detectCredentialMode({ refresh: true });
    if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY) {
        try {
            await saveSudoworkApiKey(apiKey);
            console.log("SUDOWORK_KEY_SAVED");
            return;
        } catch (error) {
            saveLocalApiKey(apiKey);
            console.log("SUDOWORK_FALLBACK_KEY_SAVED");
            console.log("Auth Proxy 设置 ShareOne API Key 失败，已暂时保存到 ShareOne 本地 fallback 凭证。");
            if (error && error.message) {
                console.log(`DETAIL:${error.message}`);
            }
            return;
        }
    }

    saveLocalApiKey(apiKey);
    if (isSudowork()) {
        console.log("SUDOWORK_FALLBACK_KEY_SAVED");
        return;
    }
    console.log("KEY_SAVED");
}

saveApiKey().catch((error) => {
    console.error(`ERROR:${error.message}`);
    process.exit(1);
});
