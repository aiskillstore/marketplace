const https = require('https');
const fs = require('fs');

const args = process.argv.slice(2);
let filePath = null;
let apiKey = process.env.SHAREONE_API_KEY || "";
let filename = "shared_content.html";
let password = null;
let watermark = null;
let shareId = null;

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--api-key') {
        apiKey = args[++i];
    } else if (args[i] === '--filename') {
        filename = args[++i];
    } else if (args[i] === '--password') {
        password = args[++i];
    } else if (args[i] === '--watermark') {
        watermark = args[++i];
    } else if (args[i] === '--share-id') {
        shareId = args[++i];
    } else if (!args[i].startsWith('--')) {
        filePath = args[i];
    }
}

if (!filePath) {
    console.error("Usage: node upload_page.js <file_path> [--api-key <key>] [--filename <name>] [--password <pwd>] [--watermark <wm>] [--share-id <id>]");
    process.exit(1);
}

const content = fs.readFileSync(filePath, "utf-8");

const payload = {
    filename: filename,
    html_content: content
};

if (!shareId) {
    if (password) payload.password = password;
    if (watermark) payload.watermark = watermark;
}

const data = JSON.stringify(payload);

const url = shareId
    ? `https://shareone.sudoprivacy.com/api/v1/pages/${shareId}`
    : 'https://shareone.sudoprivacy.com/api/v1/pages';

const method = shareId ? 'PUT' : 'POST';

const req = https.request(url, {
    method: method,
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
        'Content-Length': Buffer.byteLength(data)
    }
}, (res) => {
    let responseData = '';
    res.on('data', chunk => responseData += chunk);
    res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
            console.log(responseData);
        } else {
            console.log(`Error: ${res.statusCode}`, responseData);
        }
    });
});

req.on('error', (e) => console.error(e));
req.write(data);
req.end();