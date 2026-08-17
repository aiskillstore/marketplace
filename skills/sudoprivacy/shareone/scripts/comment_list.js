#!/usr/bin/env node

// 读取某个 ShareOne 分享的评论，输出干净的 UTF-8 JSON（便于程序解析、规避控制台
// 非 ASCII 乱码）。评论查看走公开接口，无需凭据。用于查看/拉取/总结评论；处理评论
// （回复 + 关闭/dismiss）请用 comment_resolve.js。

const {
    extractShareRef,
    printShareOneScriptError,
    requestPublicShareOneJson,
} = require('./shareone_client');

const ALLOWED_STATUS = ['all', 'open', 'in_progress', 'resolved', 'dismissed', 'unresolved'];

function usage() {
    console.error('Usage: node comment_list.js <share_link_or_ref> [--status all|open|in_progress|resolved|dismissed|unresolved] [--json compact|pretty]');
    console.error('  默认 --status all，--json pretty。评论查看是公开操作，无需凭据。');
}

const args = process.argv.slice(2);
let ref = null;
let status = 'all';
let jsonMode = 'pretty';

for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--status') {
        status = String(args[++i] || '').trim();
    } else if (arg === '--json') {
        jsonMode = String(args[++i] || '').trim();
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

if (!ALLOWED_STATUS.includes(status)) {
    console.error(`ERROR:BAD_STATUS:${status}`);
    console.error(`--status 允许的值：${ALLOWED_STATUS.join(', ')}`);
    process.exit(1);
}

// Keep only the fields useful for triage/summarization; drop bulky anchor data
// (highlighter_data) — comment_resolve re-fetches what it needs from the parent.
function projectReply(r) {
    return {
        id: r.id,
        author_role: r.author_role,
        content: r.content,
        created_at: r.created_at,
    };
}

function projectComment(c) {
    const replies = Array.isArray(c.replies) ? c.replies.map(projectReply) : [];
    return {
        id: c.id,
        status: c.status,
        author_role: c.author_role,
        quote: c.quote,
        content: c.content,
        created_at: c.created_at,
        resolution_note: c.resolution_note || null,
        reply_count: replies.length,
        replies,
    };
}

(async () => {
    const shareRef = encodeURIComponent(extractShareRef(ref));
    const comments = await requestPublicShareOneJson(
        `/api/v1/shares/${shareRef}/comments?status=${encodeURIComponent(status)}`,
        { method: 'GET' },
    );
    const list = Array.isArray(comments) ? comments : [];
    const result = {
        share: extractShareRef(ref),
        status,
        count: list.length,
        comments: list.map(projectComment),
    };
    const out = jsonMode === 'compact'
        ? JSON.stringify(result)
        : JSON.stringify(result, null, 2);
    process.stdout.write(out + '\n');
})().catch((error) => {
    process.exit(printShareOneScriptError(error));
});
