#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');
const crypto = require('crypto');

function getMimeType(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    const mimeTypes = {
        '.html': 'text/html',
        '.md': 'text/markdown',
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.zip': 'application/zip'
    };
    return mimeTypes[ext] || 'application/octet-stream';
}

function request(url, options, body = null) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https') ? https : http;
        const req = client.request(url, options, (res) => {
            let data = [];
            res.on('data', (chunk) => data.push(chunk));
            res.on('end', () => {
                const buffer = Buffer.concat(data);
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    resolve({ statusCode: res.statusCode, headers: res.headers, data: buffer });
                } else {
                    reject(new Error(`HTTP Error: ${res.statusCode} ${buffer.toString()}`));
                }
            });
        });

        req.on('error', reject);

        if (body) {
            req.write(body);
        }
        req.end();
    });
}

async function uploadFile(filePath, apiKey, baseUrl = "https://shareone.app") {
    if (!fs.existsSync(filePath)) {
        console.error(`Error: File not found: ${filePath}`);
        process.exit(1);
    }

    const filename = path.basename(filePath);
    const contentType = getMimeType(filePath);

    try {
        // Step 1: Get upload credential
        const credentialUrl = `${baseUrl}/api/v1/files/credential`;
        const credentialData = JSON.stringify({
            filename: filename,
            content_type: contentType
        });

        const credRes = await request(credentialUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey,
                'Content-Length': Buffer.byteLength(credentialData)
            }
        }, credentialData);

        const cred = JSON.parse(credRes.data.toString());
        const shareId = cred.share_id;
        const uploadUrl = cred.upload_url;
        const uploadFields = cred.upload_fields;

        // Step 2: Upload to S3 directly
        const boundary = '----WebKitFormBoundary' + crypto.randomBytes(16).toString('hex');
        const bodyParts = [];

        for (const [key, value] of Object.entries(uploadFields)) {
            bodyParts.push(Buffer.from(`--${boundary}\r\n`));
            bodyParts.push(Buffer.from(`Content-Disposition: form-data; name="${key}"\r\n\r\n`));
            bodyParts.push(Buffer.from(`${value}\r\n`));
        }

        const fileData = fs.readFileSync(filePath);
        bodyParts.push(Buffer.from(`--${boundary}\r\n`));
        bodyParts.push(Buffer.from(`Content-Disposition: form-data; name="file"; filename="${filename}"\r\n`));
        bodyParts.push(Buffer.from(`Content-Type: ${contentType}\r\n\r\n`));
        bodyParts.push(fileData);
        bodyParts.push(Buffer.from('\r\n'));
        bodyParts.push(Buffer.from(`--${boundary}--\r\n`));

        const bodyBuffer = Buffer.concat(bodyParts);

        await request(uploadUrl, {
            method: 'POST',
            headers: {
                'Content-Type': `multipart/form-data; boundary=${boundary}`,
                'Content-Length': bodyBuffer.length
            }
        }, bodyBuffer);

        // Step 3: Confirm upload
        const confirmUrl = `${baseUrl}/api/v1/files/confirm`;
        const confirmData = JSON.stringify({
            share_id: shareId,
            filename: filename,
            content_type: contentType
        });

        const confirmRes = await request(confirmUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': apiKey,
                'Content-Length': Buffer.byteLength(confirmData)
            }
        }, confirmData);

        const finalRes = JSON.parse(confirmRes.data.toString());
        console.log(`Success! File deployed to: ${finalRes.share_url}`);
        return finalRes.share_url;

    } catch (error) {
        console.error(error.message);
        process.exit(1);
    }
}

// Parse arguments
const args = process.argv.slice(2);
let filePath = null;
let apiKey = null;
let baseUrl = "https://shareone.app";

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--api-key') {
        apiKey = args[++i];
    } else if (args[i] === '--base-url') {
        baseUrl = args[++i];
    } else if (!args[i].startsWith('--')) {
        filePath = args[i];
    }
}

if (!filePath || !apiKey) {
    console.error("Usage: node shareone_upload.js <file_path> --api-key <api_key> [--base-url <base_url>]");
    process.exit(1);
}

uploadFile(filePath, apiKey, baseUrl);