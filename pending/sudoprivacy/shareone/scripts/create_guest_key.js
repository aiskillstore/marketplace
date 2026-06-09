const {
    isSudowork,
    requestPublicShareOneJson,
    requestShareOneJson,
    saveLocalApiKey,
    saveSudoworkApiKey,
} = require('./shareone_client');

async function createGuestKey() {
    try {
        const requestJson = isSudowork() ? requestPublicShareOneJson : requestShareOneJson;
        const result = await requestJson('/api/v1/agent-guest-key', {
            method: 'POST',
            authRequired: false,
        });
        if (result.api_key) {
            if (isSudowork()) {
                try {
                    await saveSudoworkApiKey(result.api_key);
                } catch (error) {
                    console.log(`ERROR:SUDOWORK_AUTH_PROXY_SAVE_FAILED:${result.api_key}`);
                    console.log("Auth Proxy 设置 ShareOne API Key 失败。请前往 Sudowork 的密钥管理手动添加 API Key，操作路径：【远程连接】-【密钥管理】。");
                    if (error && error.message) {
                        console.log(`DETAIL:${error.message}`);
                    }
                    return;
                }
            } else {
                saveLocalApiKey(result.api_key);
            }
            console.log(`GUEST_KEY_CREATED:${result.api_key}`);
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
