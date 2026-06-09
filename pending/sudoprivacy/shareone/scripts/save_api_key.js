const { isSudowork, saveLocalApiKey, saveSudoworkApiKey } = require('./shareone_client');

const apiKey = process.argv[2];
if (!apiKey) {
    console.error("Please provide an API key.");
    process.exit(1);
}

async function saveApiKey() {
    if (isSudowork()) {
        await saveSudoworkApiKey(apiKey);
        console.log("SUDOWORK_KEY_SAVED");
        return;
    }

    saveLocalApiKey(apiKey);
    console.log("KEY_SAVED");
}

saveApiKey().catch((error) => {
    if (isSudowork()) {
        console.error("ERROR:SUDOWORK_AUTH_PROXY_SAVE_FAILED");
        console.error("Auth Proxy 设置 ShareOne API Key 失败。请前往 Sudowork 的密钥管理手动添加 API Key，操作路径：【远程连接】-【密钥管理】。");
        if (error && error.message) {
            console.error(`DETAIL:${error.message}`);
        }
        process.exit(1);
    }
    console.error(`ERROR:${error.message}`);
    process.exit(1);
});
