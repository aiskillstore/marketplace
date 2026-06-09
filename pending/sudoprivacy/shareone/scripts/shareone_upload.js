#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const {
    isSudowork,
    printShareOneScriptError,
    requestBuffer,
    requestShareOneBuffer,
    requestShareOneJson,
    resolveDirectApiKey,
} = require('./shareone_client');

function getMimeType(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    const mimeTypes = {
        '.html': 'text/html',
        '.htm': 'text/html',
        '.md': 'text/markdown',
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.zip': 'application/zip'
    };
    return mimeTypes[ext] || 'application/octet-stream';
}

function buildMultipartBody(fields, filePath, filename, contentType) {
    const boundary = '----ShareOneBoundary' + crypto.randomBytes(16).toString('hex');
    const fileData = fs.readFileSync(filePath);
    const bodyParts = [];

    for (const [key, value] of Object.entries(fields || {})) {
        if (value === undefined || value === null) continue;
        bodyParts.push(Buffer.from(`--${boundary}\r\n`));
        bodyParts.push(Buffer.from(`Content-Disposition: form-data; name="${key}"\r\n\r\n`));
        bodyParts.push(Buffer.from(`${value}\r\n`));
    }

    bodyParts.push(Buffer.from(`--${boundary}\r\n`));
    bodyParts.push(Buffer.from(`Content-Disposition: form-data; name="file"; filename="${filename}"\r\n`));
    bodyParts.push(Buffer.from(`Content-Type: ${contentType}\r\n\r\n`));
    bodyParts.push(fileData);
    bodyParts.push(Buffer.from('\r\n'));
    bodyParts.push(Buffer.from(`--${boundary}--\r\n`));

    return { body: Buffer.concat(bodyParts), boundary };
}

async function uploadToAzure(uploadUrl, filePath, contentType) {
    const fileData = fs.readFileSync(filePath);
    await requestBuffer(uploadUrl, {
        method: 'PUT',
        headers: {
            'x-ms-blob-type': 'BlockBlob',
            'Content-Type': contentType,
            'Content-Length': fileData.length
        }
    }, fileData);
}

async function uploadToS3(uploadUrl, uploadFields, filePath, filename, contentType) {
    const { body, boundary } = buildMultipartBody(uploadFields, filePath, filename, contentType);
    await requestBuffer(uploadUrl, {
        method: 'POST',
        headers: {
            'Content-Type': `multipart/form-data; boundary=${boundary}`,
            'Content-Length': body.length
        }
    }, body);
}

async function uploadMultipartFallback(filePath, filename, contentType, options) {
    const fields = {};
    if (options.password) fields.password = options.password;
    if (options.watermark) fields.watermark = options.watermark;
    if (options.slug) fields.custom_slug = options.slug;
    const { body, boundary } = buildMultipartBody(fields, filePath, filename, contentType);
    const res = await requestShareOneBuffer('/api/v1/files', {
        method: 'POST',
        apiKey: options.apiKey,
        headers: {
            'Content-Type': `multipart/form-data; boundary=${boundary}`,
            'Content-Length': body.length
        }
    }, body);
    return JSON.parse(res.text);
}

function shouldFallbackToMultipart(error) {
    const detail = String(error.responseText || error.message || '');
    return error.statusCode === 400 && detail.includes('Direct upload is only supported');
}

async function uploadFile(filePath, options) {
    if (!fs.existsSync(filePath)) {
        console.error(`Error: File not found: ${filePath}`);
        process.exit(1);
    }

    if (isSudowork() && options.apiKey) {
        console.error("ERROR:SUDOWORK_MANAGED_KEY");
        console.error("Sudowork 模式下不要传 --api-key；请通过本 skill 的 save_api_key.js 或 create_guest_key.js 设置 ShareOne API Key。");
        process.exit(1);
    }

    if (!isSudowork() && !resolveDirectApiKey(options.apiKey)) {
        console.error("ERROR:KEY_NOT_FOUND");
        process.exit(1);
    }

    const filename = options.filename || path.basename(filePath);
    const contentType = options.contentType || getMimeType(filePath);

    try {
        const credential = await requestShareOneJson('/api/v1/files/credential', {
            method: 'POST',
            apiKey: options.apiKey,
        }, {
            filename: filename,
            content_type: contentType,
            custom_slug: options.slug || undefined
        });

        if (credential.upload_type === 'azure') {
            await uploadToAzure(credential.upload_url, filePath, contentType);
        } else {
            await uploadToS3(credential.upload_url, credential.upload_fields || {}, filePath, filename, contentType);
        }

        const confirmPayload = {
            share_id: credential.share_id,
            filename: filename,
            content_type: contentType
        };
        if (options.password) confirmPayload.password = options.password;
        if (options.watermark) confirmPayload.watermark = options.watermark;
        if (options.slug) confirmPayload.custom_slug = options.slug;

        const finalRes = await requestShareOneJson('/api/v1/files/confirm', {
            method: 'POST',
            apiKey: options.apiKey,
        }, confirmPayload);

        console.log(JSON.stringify(finalRes));
        return finalRes.share_url;
    } catch (error) {
        if (shouldFallbackToMultipart(error)) {
            const finalRes = await uploadMultipartFallback(filePath, filename, contentType, options);
            console.log(JSON.stringify(finalRes));
            return finalRes.share_url;
        }
        throw error;
    }
}

const args = process.argv.slice(2);
let filePath = null;
const options = {
    apiKey: null,
    filename: null,
    contentType: null,
    password: null,
    watermark: null,
    slug: null,
};

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--api-key') {
        options.apiKey = args[++i];
    } else if (args[i] === '--base-url') {
        process.env.SHAREONE_BASE_URL = args[++i];
    } else if (args[i] === '--filename') {
        options.filename = args[++i];
    } else if (args[i] === '--content-type') {
        options.contentType = args[++i];
    } else if (args[i] === '--password') {
        options.password = args[++i];
    } else if (args[i] === '--watermark') {
        options.watermark = args[++i];
    } else if (args[i] === '--slug') {
        options.slug = args[++i];
    } else if (!args[i].startsWith('--')) {
        filePath = args[i];
    }
}

if (!filePath) {
    console.error("Usage: node shareone_upload.js <file_path> [--api-key <api_key>] [--base-url <base_url>] [--filename <name>] [--content-type <mime>] [--password <password>] [--watermark <watermark>] [--slug <slug>]");
    process.exit(1);
}

uploadFile(filePath, options).catch((error) => {
    printShareOneScriptError(error);
    process.exit(1);
});
