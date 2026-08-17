#!/usr/bin/env node

// 评论闭环的“回复 + 关闭”一体脚本：自动从父评论继承 quote/highlighter_data，
// 先 POST 一条 author_role=agent 的回复，再把父评论状态置为 resolved 或 dismissed。
// 模型不需要手工拼接含 highlighter_data 的多层转义 JSON。

const {
    CREDENTIAL_MODE_SUDOWORK_PROXY,
    detectCredentialMode,
    extractShareRef,
    printShareOneScriptError,
    requestShareOneJson,
    resolveDirectApiKey,
} = require('./shareone_client');

function usage() {
    console.error('Usage: node comment_resolve.js <share_link_or_ref> <comment_id> --reply "<回复内容>" [--note "<处理说明>"] [--api-key <key>]');
    console.error('       node comment_resolve.js <share_link_or_ref> <comment_id> --dismiss --note "<原因>" [--reply "<回复内容>"] [--api-key <key>]');
}

const args = process.argv.slice(2);
let ref = null;
let commentId = null;
let reply = null;
let note = null;
let dismiss = false;
let apiKey = null;

for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--reply') {
        reply = args[++i];
    } else if (arg === '--note') {
        note = args[++i];
    } else if (arg === '--dismiss') {
        dismiss = true;
    } else if (arg === '--api-key') {
        apiKey = args[++i];
    } else if (!arg.startsWith('--') && !ref) {
        ref = arg;
    } else if (!arg.startsWith('--') && !commentId) {
        commentId = arg;
    } else {
        console.error(`ERROR:UNKNOWN_ARGUMENT:${arg}`);
        usage();
        process.exit(1);
    }
}

if (!ref || !commentId) {
    usage();
    process.exit(1);
}

if (!dismiss && !reply) {
    console.error('ERROR:REPLY_REQUIRED');
    console.error('resolved 闭环要求先给访问者一条回复。请用 --reply 说明改了什么；如果这条评论无法处理或与页面无关，请改用 --dismiss --note "<原因>"。');
    process.exit(1);
}

if (dismiss && !note) {
    console.error('ERROR:NOTE_REQUIRED');
    console.error('dismissed 闭环要求用 --note 说明无法处理或无需处理的原因。');
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
    const comments = await requestShareOneJson(`/api/v1/shares/${shareRef}/comments?status=all`, {
        method: 'GET',
        apiKey,
    });

    const wantedId = String(commentId);
    const parent = (comments || []).find(c => String(c.id) === wantedId);
    if (!parent) {
        for (const c of comments || []) {
            const asReply = (c.replies || []).find(r => String(r.id) === wantedId);
            if (asReply) {
                console.error(`ERROR:IS_REPLY:${c.id}`);
                console.error(`评论 ${wantedId} 是一条回复，状态只能对父评论操作。请改用父评论 ID ${c.id} 重新执行。`);
                process.exit(1);
            }
        }
        console.error('ERROR:COMMENT_NOT_FOUND');
        console.error(`在该 share 下没有找到 ID 为 ${wantedId} 的评论。`);
        process.exit(1);
    }

    if (reply) {
        const posted = await requestShareOneJson(`/api/v1/shares/${shareRef}/comments`, {
            method: 'POST',
            apiKey,
        }, {
            parent_id: parent.id,
            quote: parent.quote,
            highlighter_data: parent.highlighter_data,
            content: reply,
            author_role: 'agent',
            // Agent replies now require an explicit state (server-enforced). This
            // legacy resolve/dismiss script maps to the closest state; the status
            // PUT below still finalizes to resolved/dismissed. For nuanced replies
            // (esp. disagreement that should stay open) prefer comment_reply.js.
            state: dismiss ? 'open-disagree' : 'resolved-agree',
        });
        console.log(`REPLY_POSTED:${posted && posted.id !== undefined ? posted.id : ''}`);
    }

    const status = dismiss ? 'dismissed' : 'resolved';
    const payload = { status };
    if (note !== null) payload.note = note;
    await requestShareOneJson(`/api/v1/shares/${shareRef}/comments/${encodeURIComponent(wantedId)}/status`, {
        method: 'PUT',
        apiKey,
    }, payload);
    console.log(dismiss ? `COMMENT_DISMISSED:${wantedId}` : `COMMENT_RESOLVED:${wantedId}`);
})().catch((error) => {
    process.exit(printShareOneScriptError(error));
});
