#!/usr/bin/env node

// 统一发布入口：按文件类型自动分发到文本通道 (upload_page.js) 或二进制通道 (shareone_upload.js)。
// 模型不需要自行判断上传通道；误判文件类型不会再导致内容发错接口。

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const TEXT_EXTENSIONS = new Set(['.html', '.htm', '.md', '.markdown', '.txt']);

function usage() {
    console.error('Usage: node publish.js <file_path> [--filename <name>] [--password <pwd>] [--watermark <wm>] [--slug <slug>] [--share-id <id>] [--allow-comments <true|false>] [--allow-data <true|false>] [--content-type <mime>] [--base-url <url>] [--api-key <key>] [--force-new]');
}

function looksBinary(filePath) {
    const fd = fs.openSync(filePath, 'r');
    try {
        const buffer = Buffer.alloc(8192);
        const bytesRead = fs.readSync(fd, buffer, 0, buffer.length, 0);
        for (let i = 0; i < bytesRead; i++) {
            if (buffer[i] === 0) return true;
        }
        return false;
    } finally {
        fs.closeSync(fd);
    }
}

const VALUE_FLAGS = new Set([
    '--api-key', '--filename', '--password', '--watermark',
    '--share-id', '--slug', '--allow-comments', '--allow-data', '--content-type', '--base-url',
]);
const BOOL_FLAGS = new Set(['--force-new']);

const args = process.argv.slice(2);
let filePath = null;
const options = {};
const boolOptions = new Set();

for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (VALUE_FLAGS.has(arg)) {
        const value = args[i + 1];
        if (value === undefined) {
            console.error(`ERROR:MISSING_VALUE:${arg}`);
            usage();
            process.exit(1);
        }
        options[arg] = value;
        i += 1;
    } else if (BOOL_FLAGS.has(arg)) {
        boolOptions.add(arg);
    } else if (!arg.startsWith('--') && !filePath) {
        filePath = arg;
    } else {
        console.error(`ERROR:UNKNOWN_ARGUMENT:${arg}`);
        usage();
        process.exit(1);
    }
}

if (!filePath) {
    usage();
    process.exit(1);
}

if (filePath.includes('://') || /^\/?(s|md|pdf|ppt|word)\//.test(filePath)) {
    console.error('ERROR:LOOKS_LIKE_SHARE_LINK');
    console.error('本脚本的第一个参数是本地文件路径，不是 ShareOne 链接。要修改已有链接的设置请用 update_share_settings.js；要下载链接内容请用 download_share.js。');
    process.exit(1);
}

if (!fs.existsSync(filePath)) {
    console.error('ERROR:FILE_NOT_FOUND');
    console.error(`File not found: ${filePath}`);
    process.exit(1);
}

const ext = path.extname(filePath).toLowerCase();
const channel = (TEXT_EXTENSIONS.has(ext) || ext === '') && !looksBinary(filePath) ? 'text' : 'binary';
console.error(`INFO:CHANNEL:${channel}`);

const targetArgs = [filePath];

if (channel === 'text') {
    if (options['--content-type']) {
        console.error('ERROR:OPTION_NOT_SUPPORTED:--content-type');
        console.error('文本页面通道不支持 --content-type；该选项只用于二进制文件上传。');
        process.exit(1);
    }
    for (const flag of ['--filename', '--password', '--watermark', '--share-id', '--slug', '--allow-comments', '--allow-data', '--base-url', '--api-key']) {
        if (options[flag] !== undefined) targetArgs.push(flag, options[flag]);
    }
    if (boolOptions.has('--force-new')) targetArgs.push('--force-new');
} else {
    if (options['--share-id'] !== undefined) {
        console.error('ERROR:BINARY_NO_SHARE_ID');
        console.error('二进制文件不支持内容 PUT 更新；重新上传会生成新链接（去掉 --share-id 重试）。如果只是要修改已有链接的密码/水印/短链/评论开关，请用 update_share_settings.js。');
        process.exit(1);
    }
    if (options['--allow-comments'] !== undefined) {
        console.error('ERROR:BINARY_NO_ALLOW_COMMENTS');
        console.error('二进制文件上传时不支持 --allow-comments；请先上传，再用 update_share_settings.js "<share_url>" --allow-comments true 开启评论。');
        process.exit(1);
    }
    if (options['--allow-data'] !== undefined) {
        console.error('ERROR:BINARY_NO_ALLOW_DATA');
        console.error('二进制文件上传时不支持 --allow-data；请先上传，再用 update_share_settings.js "<share_url>" --allow-data true 开启数据存储。');
        process.exit(1);
    }
    for (const flag of ['--filename', '--password', '--watermark', '--slug', '--content-type', '--base-url', '--api-key']) {
        if (options[flag] !== undefined) targetArgs.push(flag, options[flag]);
    }
}

const targetScript = channel === 'text' ? 'upload_page.js' : 'shareone_upload.js';
const result = spawnSync(process.execPath, [path.join(__dirname, targetScript), ...targetArgs], {
    stdio: 'inherit',
});
process.exit(result.status === null ? 1 : result.status);
