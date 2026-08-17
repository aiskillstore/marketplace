#!/usr/bin/env node

// 凭据流程编排脚本：检查 → 保存 → 复查 → 核对 的状态机全部在此执行。
// 模型只需按输出 token 行动，并把分隔线之后的话术原样转发给用户。

const {
    CREDENTIAL_MODE_SUDOWORK_PROXY,
    CREDENTIAL_MODE_DIRECT_FALLBACK,
    detectCredentialMode,
    getBaseUrl,
    isSudowork,
    readLocalApiKey,
    requestPublicShareOneJson,
    saveLocalApiKey,
    saveSudoworkApiKey,
} = require('./shareone_client');

const SEPARATOR = '--- 请将以下内容原样发给用户 ---';

function usage() {
    console.error('Usage: node ensure_credentials.js            # 检查凭据状态');
    console.error('       node ensure_credentials.js --key <用户提供的KEY>   # 保存用户已有的 API Key 并复查');
    console.error('       node ensure_credentials.js --create-guest        # 创建临时 API Key 并保存');
}

function modeName(credentialMode) {
    if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY) return 'sudowork';
    if (credentialMode.mode === CREDENTIAL_MODE_DIRECT_FALLBACK) return 'sudowork_fallback';
    return 'direct';
}

function hasDirectKey() {
    return Boolean(process.env.SHAREONE_API_KEY || readLocalApiKey());
}

function isReady(credentialMode) {
    if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY) return credentialMode.hasSudoworkKey;
    return hasDirectKey();
}

function askForKeyPrompt(credentialMode) {
    if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY) {
        return [
            '我检测到当前运行在 Sudowork 中，且 Sudowork 凭证环境可用，但还没有设置 ShareOne API Key。',
            '请问您是否已经拥有 API Key？',
            '',
            '- 如果有，请直接回复您的 API Key（例如 `sk-xxx`），我会通过 Sudowork 安全保存并继续。',
            '- 如果没有，请回复“没有”或“创建”，我会自动为您创建一个临时 API Key，并保存到 Sudowork。',
        ].join('\n');
    }
    if (credentialMode.mode === CREDENTIAL_MODE_DIRECT_FALLBACK) {
        return [
            '我检测到当前运行在 Sudowork 中，但 Sudowork Auth Proxy/secrets 当前不可用，因此会暂时回退到 ShareOne 普通凭据流程。',
            '请问您是否已经拥有 API Key？',
            '',
            '- 如果有，请直接回复您的 API Key（例如 `sk-xxx`），我将保存到 ShareOne fallback 本地凭证并继续。',
            '- 如果没有，请回复“没有”或“创建”，我可以为您创建一个临时 API Key。',
        ].join('\n');
    }
    return [
        '我没有找到您的 ShareOne API Key。',
        '请问您是否已经拥有 API Key？',
        '',
        '- 如果有，请直接回复您的 API Key（例如 `sk-xxx`），我将为您保存并继续。',
        '- 如果没有，请回复“没有”或“创建”，我可以为您创建一个临时 API Key。',
    ].join('\n');
}

function printSudoworkWriteBroken() {
    console.log('ERROR:SUDOWORK_WRITE_BROKEN');
    console.log(SEPARATOR);
    console.log('Sudowork 凭证环境当前“可读但写入失败”，API Key 无法自动保存。请在 Sudowork 密钥管理中手动配置 ShareOne API Key（namespace `service:shareone`，key `X-API-Key`），或检查 Auth Proxy 状态后再让我重试。');
}

function guestKeyNotification(apiKey) {
    return [
        `已为您自动分配临时 API Key：\`${apiKey}\``,
        `绑定账号链接：${getBaseUrl()}/?key=${apiKey}`,
        '请妥善保存此 API Key。为了方便您后续管理分享的链接，请尽快打开上面的链接绑定您的永久账号。',
    ].join('\n');
}

async function saveKeyAndRecheck(apiKey) {
    let credentialMode = await detectCredentialMode({ refresh: true });

    if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY) {
        let savedToSudowork = false;
        try {
            await saveSudoworkApiKey(apiKey);
            savedToSudowork = true;
        } catch (error) {
            credentialMode = await detectCredentialMode({ refresh: true });
            if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY) {
                printSudoworkWriteBroken();
                process.exit(1);
            }
            saveLocalApiKey(apiKey);
        }

        credentialMode = await detectCredentialMode({ refresh: true });
        if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY) {
            if (credentialMode.hasSudoworkKey) {
                console.log('READY');
                console.log(`MODE:${modeName(credentialMode)}`);
                return;
            }
            // 保存声称成功（或失败回退本地）但 secrets 列表里仍然没有：可读不可写。
            printSudoworkWriteBroken();
            process.exit(1);
        }
        // 复查时 proxy 已不可用，走 fallback；key 已存本地。
        console.log('READY');
        console.log(`MODE:${modeName(credentialMode)}`);
        if (!savedToSudowork) console.log('NOTE:SUDOWORK_FALLBACK_KEY_SAVED');
        return;
    }

    saveLocalApiKey(apiKey);
    console.log('READY');
    console.log(`MODE:${modeName(credentialMode)}`);
    if (isSudowork()) console.log('NOTE:SUDOWORK_FALLBACK_KEY_SAVED');
}

async function createGuestKey() {
    const credentialMode = await detectCredentialMode({ refresh: true });
    let result;
    try {
        result = await requestPublicShareOneJson('/api/v1/agent-guest-key', {
            method: 'POST',
            authRequired: false,
        });
    } catch (error) {
        if (error.statusCode === 429) {
            console.log('ERROR:RATE_LIMIT_EXCEEDED');
            console.log(SEPARATOR);
            console.log(`获取临时凭证失败：自动创建临时 API Key 触发了频率限制（每小时最多 20 次、每天最多 200 次）。请稍后再试，或前往 ${getBaseUrl()} 手动注册并获取 API Key。`);
            process.exit(1);
        }
        throw error;
    }

    if (!result || !result.api_key) {
        console.log('ERROR:INVALID_RESPONSE');
        process.exit(1);
    }

    let fallbackSaved = false;
    if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY) {
        try {
            await saveSudoworkApiKey(result.api_key);
        } catch (error) {
            const refreshedMode = await detectCredentialMode({ refresh: true });
            if (refreshedMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY) {
                printSudoworkWriteBroken();
                process.exit(1);
            }
            saveLocalApiKey(result.api_key);
            fallbackSaved = true;
        }
    } else {
        saveLocalApiKey(result.api_key);
        fallbackSaved = isSudowork();
    }

    console.log(`GUEST_KEY_CREATED:${result.api_key}`);
    if (fallbackSaved) console.log('NOTE:SUDOWORK_FALLBACK_KEY_SAVED');
    console.log(SEPARATOR);
    console.log(guestKeyNotification(result.api_key));
    if (fallbackSaved) {
        console.log('');
        console.log('另外说明：Sudowork Auth Proxy/secrets 当前不可用或保存失败，该 API Key 已暂时保存到 ShareOne skill 安装目录下的本地 fallback 凭证（`.shareone_credentials`），不是 Sudowork Secret Store。');
    }
}

(async () => {
    const args = process.argv.slice(2);

    if (args[0] === '--key') {
        const apiKey = args[1];
        if (!apiKey) {
            console.error('ERROR:MISSING_VALUE:--key');
            usage();
            process.exit(1);
        }
        await saveKeyAndRecheck(apiKey);
        return;
    }

    if (args[0] === '--create-guest') {
        await createGuestKey();
        return;
    }

    if (args.length > 0) {
        console.error(`ERROR:UNKNOWN_ARGUMENT:${args[0]}`);
        usage();
        process.exit(1);
    }

    const credentialMode = await detectCredentialMode({ refresh: true });
    if (isReady(credentialMode)) {
        console.log('READY');
        console.log(`MODE:${modeName(credentialMode)}`);
        return;
    }
    console.log('NEED_USER_INPUT');
    console.log(`MODE:${modeName(credentialMode)}`);
    console.log(SEPARATOR);
    console.log(askForKeyPrompt(credentialMode));
})().catch((error) => {
    console.error(`ERROR:${error.message}`);
    process.exit(1);
});
