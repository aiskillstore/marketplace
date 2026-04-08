const os = require('os');
const fs = require('fs');
const path = require('path');

function checkApiKey() {
    // 1. Check environment variable
    let apiKey = process.env.SHAREONE_API_KEY;
    if (apiKey) {
        console.log(`KEY_FOUND:${apiKey}`);
        return;
    }

    // 2. Check local credentials file
    const credPath = path.join(os.homedir(), '.shareone_credentials');
    if (fs.existsSync(credPath)) {
        try {
            const data = JSON.parse(fs.readFileSync(credPath, 'utf8'));
            apiKey = data.api_key;
            if (apiKey) {
                console.log(`KEY_FOUND:${apiKey}`);
                return;
            }
        } catch (e) {
            // Ignore errors
        }
    }

    console.log("KEY_NOT_FOUND");
}

checkApiKey();