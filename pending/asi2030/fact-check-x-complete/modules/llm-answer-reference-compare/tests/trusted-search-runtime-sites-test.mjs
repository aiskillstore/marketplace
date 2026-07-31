import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const distRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "assets", "tool", "dist");
const sites = [
    join(distRoot, "capture", "generic-chat.js"),
    join(distRoot, "trusted-search-onboarding.js"),
];
for (const site of sites) {
    const source = await readFile(site, "utf8");
    const credentialedFetch = /fetch\(endpoint,\s*\{[\s\S]{0,600}?"api-key"/.exec(source);
    assert.ok(credentialedFetch, `${site} must contain credentialed fetch`);
    assert.match(source.slice(0, credentialedFetch.index), /validateTrustedSearchEndpoint\(/);
    assert.match(credentialedFetch[0], /redirect:\s*"error"/);
}
console.log("PASS credentialed runtime fetches validate endpoint before fetch and reject redirects");
