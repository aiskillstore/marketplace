const http = require('http');
const https = require('https');
const os = require('os');
const fs = require('fs');
const path = require('path');

const baseUrl = process.env.SHAREONE_BASE_URL || 'https://shareone.app';
const client = baseUrl.startsWith('https') ? https : http;
const url = new URL('/api/v1/agent-guest-key', baseUrl);

const req = client.request(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
}, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        if (res.statusCode === 200) {
            const result = JSON.parse(data);
            if (result.api_key) {
                const credPath = path.join(os.homedir(), '.shareone_credentials');
                fs.writeFileSync(credPath, JSON.stringify({ api_key: result.api_key }));
                console.log(`GUEST_KEY_CREATED:${result.api_key}`);
            }
        } else if (res.statusCode === 429) {
            console.log("ERROR:RATE_LIMIT_EXCEEDED");
        } else {
            console.log(`ERROR:HTTP_${res.statusCode}`);
        }
    });
});

req.on('error', (e) => {
    console.log(`ERROR:${e.message}`);
});
req.end();