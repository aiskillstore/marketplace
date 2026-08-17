#!/usr/bin/env node

// 强制刷新一个 remote-url auto-follow 分享的源内容（owner-only，需凭据）。
// 用于源站（GitHub 等）刚 push 后立即拉取最新内容——remote 页面的刷新是懒的、
// 只在打开渲染页时触发且有节流，`download`/`/file` 只服务缓存，不会 refetch。
// 本命令调用 POST /api/v1/pages/<ref>/refresh，绕过节流立即拉取。
// 接受完整链接、/s/<ref> 路径、裸 share_id 或 slug。

const {
    CREDENTIAL_MODE_SUDOWORK_PROXY,
    detectCredentialMode,
    extractShareRef,
    printShareOneScriptError,
    requestShareOneJson,
    resolveDirectApiKey,
} = require('./shareone_client');

function usage() {
    console.error('Usage: node refresh_share.js <share_link_or_ref> [--api-key <key>]');
    console.error('  仅对绑定了远程源 URL 的分享有效；非 remote-bound 会返回 NOT_REMOTE_BOUND。');
}


const args = process.argv.slice(2);
let ref = null;
let apiKey = null;

for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--api-key') {
        apiKey = args[++i];
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

(async () => {
    const credentialMode = await detectCredentialMode();
    if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY && apiKey) {
        console.error('ERROR:SUDOWORK_MANAGED_KEY');
        console.error('Sudowork 模式下不要传 --api-key；请通过本 skill 的 save_api_key.js 或 create_guest_key.js 设置 ShareOne API Key。');
        process.exit(1);
    }
    if (credentialMode.mode !== CREDENTIAL_MODE_SUDOWORK_PROXY && !resolveDirectApiKey(apiKey)) {
        console.error('ERROR:KEY_NOT_FOUND');
        process.exit(1);
    }

    const shareRef = encodeURIComponent(extractShareRef(ref));
    const result = await requestShareOneJson(`/api/v1/pages/${shareRef}/refresh`, {
        method: 'POST',
        apiKey,
    });
    process.stdout.write(JSON.stringify(result, null, 2) + '\n');
    console.error(`SHARE_REFRESHED:${extractShareRef(ref)}`);
})().catch((error) => {
    process.exit(printShareOneScriptError(error));
});
