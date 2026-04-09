const https = require('https');
const os = require('os');
const fs = require('fs');
const path = require('path');

const req = https.request('https://shareone.sudoprivacy.com/api/v1/agent-guest-key', {
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