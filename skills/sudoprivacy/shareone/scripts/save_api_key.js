const os = require('os');
const fs = require('fs');
const path = require('path');

const apiKey = process.argv[2];
if (!apiKey) {
    console.error("Please provide an API key.");
    process.exit(1);
}

const credPath = path.join(os.homedir(), '.shareone_credentials');
fs.writeFileSync(credPath, JSON.stringify({ api_key: apiKey }));
console.log("KEY_SAVED");