#!/usr/bin/env node

const {
    deleteLocalApiKey,
    deleteSudoworkApiKey,
    isSudowork,
} = require('./shareone_client');

async function deleteApiKey() {
    if (isSudowork()) {
        await deleteSudoworkApiKey();
        console.log("SUDOWORK_KEY_DELETED");
        return;
    }

    const deleted = deleteLocalApiKey();
    console.log(deleted ? "KEY_DELETED" : "KEY_NOT_FOUND");
}

deleteApiKey().catch((error) => {
    console.error(`ERROR:${error.message}`);
    process.exit(1);
});
