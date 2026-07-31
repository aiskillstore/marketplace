import assert from "node:assert/strict";
import { validateTrustedSearchEndpoint } from "../assets/tool/dist/utils/trusted-search-endpoint.js";

const production = "https://open.dknowc.cn/dependable/search";
const rejected = [
    "http://open.dknowc.cn/dependable/search",
    "https://open.dknowc.cn:443/dependable/search",
    "https://open.dknowc.cn/dependable/search/",
    "https://open.dknowc.cn/dependable/search?x=1",
    "https://open.dknowc.cn/dependable/search#fragment",
    "https://user@open.dknowc.cn/dependable/search",
    "https://open.dknowc.cn@evil.example/dependable/search",
    "https://open.dknowc.cn%2e.evil.example/dependable/search",
    "https://127.0.0.1:9999/dependable/search",
    "http://127.0.0.1.evil.example:9999/dependable/search",
    "http://[::1]@evil.example:9999/dependable/search",
];

assert.equal(validateTrustedSearchEndpoint(production, {}), production);
for (const endpoint of rejected) {
    assert.throws(() => validateTrustedSearchEndpoint(endpoint, {}));
}
assert.equal(
    validateTrustedSearchEndpoint("http://127.0.0.1:9999/dependable/search", { FACT_CHECK_X_TEST_MODE: "1" }),
    "http://127.0.0.1:9999/dependable/search"
);
assert.equal(
    validateTrustedSearchEndpoint("http://[::1]:9999/dependable/search", { FACT_CHECK_X_TEST_MODE: "1" }),
    "http://[::1]:9999/dependable/search"
);

console.log("PASS trusted search endpoint validator");
