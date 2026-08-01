const PRODUCTION_ENDPOINT = "https://open.dknowc.cn/dependable/search";
const TEST_ENDPOINT = /^(?:https?):\/\/(?:127\.0\.0\.1|\[::1\])(?::[0-9]+)?\/dependable\/search$/;

export function validateTrustedSearchEndpoint(value, environment = process.env) {
    const endpoint = String(value || "").trim();
    if (endpoint === PRODUCTION_ENDPOINT) {
        return endpoint;
    }
    if (environment.FACT_CHECK_X_TEST_MODE !== "1" || !TEST_ENDPOINT.test(endpoint)) {
        throw new Error("Trusted search endpoint is not allowed.");
    }
    return endpoint;
}
