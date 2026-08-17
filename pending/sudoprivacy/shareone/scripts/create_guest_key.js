const {
    CREDENTIAL_MODE_SUDOWORK_PROXY,
    detectCredentialMode,
    isSudowork,
    requestPublicShareOneJson,
    saveLocalApiKey,
    saveSudoworkApiKey,
} = require('./shareone_client');

if (process.argv.length > 2) {
    console.error(`ERROR:UNKNOWN_ARGUMENT:${process.argv[2]}`);
    console.error('Usage: node create_guest_key.js');
    process.exit(1);
}

async function createGuestKey() {
    try {
        const credentialMode = await detectCredentialMode({ refresh: true });
        const result = await requestPublicShareOneJson('/api/v1/agent-guest-key', {
            method: 'POST',
            authRequired: false,
        });
        if (result.api_key) {
            if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY) {
                try {
                    await saveSudoworkApiKey(result.api_key);
                } catch (error) {
                    saveLocalApiKey(result.api_key);
                    console.log(`GUEST_KEY_CREATED:${result.api_key}`);
                    console.log("SUDOWORK_FALLBACK_KEY_SAVED");
                    console.log("Auth Proxy 设置 ShareOne API Key 失败，已暂时保存到 ShareOne 本地 fallback 凭证。");
                    if (error && error.message) {
                        console.log(`DETAIL:${error.message}`);
                    }
                    return;
                }
            } else {
                saveLocalApiKey(result.api_key);
            }
            console.log(`GUEST_KEY_CREATED:${result.api_key}`);
            if (isSudowork() && credentialMode.mode !== CREDENTIAL_MODE_SUDOWORK_PROXY) {
                console.log("SUDOWORK_FALLBACK_KEY_SAVED");
                console.log("Sudowork Auth Proxy 当前不可用，已保存到 ShareOne 本地 fallback 凭证。");
            }
            return;
        }
        console.log("ERROR:INVALID_RESPONSE");
    } catch (error) {
        if (error.statusCode === 429) {
            console.log("ERROR:RATE_LIMIT_EXCEEDED");
        } else {
            console.log(`ERROR:${error.message}`);
        }
    }
}

createGuestKey();
