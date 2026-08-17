#!/usr/bin/env node

const {
    CREDENTIAL_MODE_SUDOWORK_PROXY,
    deleteLocalApiKey,
    deleteSudoworkApiKey,
    detectCredentialMode,
    isSudowork,
} = require('./shareone_client');

if (process.argv.length > 2) {
    console.error(`ERROR:UNKNOWN_ARGUMENT:${process.argv[2]}`);
    console.error('Usage: node delete_api_key.js');
    process.exit(1);
}

async function deleteApiKey() {
    const credentialMode = await detectCredentialMode({ refresh: true });
    if (credentialMode.mode === CREDENTIAL_MODE_SUDOWORK_PROXY) {
        let sudoworkDeleted = true;
        try {
            await deleteSudoworkApiKey();
        } catch (error) {
            if (error.statusCode !== 404) throw error;
            sudoworkDeleted = false;
        }
        const localDeleted = deleteLocalApiKey();
        console.log(sudoworkDeleted || localDeleted ? "SUDOWORK_KEY_DELETED" : "KEY_NOT_FOUND");
        return;
    }

    const deleted = deleteLocalApiKey();
    if (isSudowork()) {
        console.log(deleted ? "SUDOWORK_FALLBACK_KEY_DELETED" : "KEY_NOT_FOUND");
        return;
    }
    console.log(deleted ? "KEY_DELETED" : "KEY_NOT_FOUND");
}

deleteApiKey().catch((error) => {
    console.error(`ERROR:${error.message}`);
    process.exit(1);
});
