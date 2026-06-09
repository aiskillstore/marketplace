const {
    hasSudoworkApiKey,
    isSudowork,
    readLocalApiKey,
} = require('./shareone_client');

async function checkApiKey() {
    if (isSudowork()) {
        try {
            const found = await hasSudoworkApiKey();
            console.log(found ? 'SUDOWORK_KEY_FOUND' : 'SUDOWORK_KEY_NOT_FOUND');
        } catch (_) {
            console.log('SUDOWORK_KEY_NOT_FOUND');
        }
        return;
    }

    let apiKey = process.env.SHAREONE_API_KEY || readLocalApiKey();
    if (apiKey) {
        console.log(`KEY_FOUND:${apiKey}`);
        return;
    }

    console.log("KEY_NOT_FOUND");
}

checkApiKey().catch((error) => {
    console.error(`ERROR:${error.message}`);
    process.exit(1);
});
