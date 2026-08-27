const OFFICIAL_MEDIA = ["people.com.cn", "xinhuanet.com", "qstheory.cn", "gmw.cn"];
const DKNOW_OFFICIAL_PLATFORMS = new Set(["dknowc-chat", "dknowc-deep-research"]);
const OFFICIAL_ORIGIN_KEYS = [
    "originUrl",
    "origin_url",
    "resourceUrl",
    "resource_url",
    "officialUrl",
    "official_url",
    "sourceUrl",
    "source_url"
];

function hostname(value) {
    try {
        return new URL(String(value || "")).hostname.toLowerCase();
    }
    catch {
        return "";
    }
}

function isOfficialUrl(value) {
    const host = hostname(value);
    return host === "gov.cn"
        || host.endsWith(".gov.cn")
        || OFFICIAL_MEDIA.some((domain) => host === domain || host.endsWith(`.${domain}`));
}

function isHttpUrl(value) {
    try {
        const url = new URL(String(value || ""));
        return url.protocol === "http:" || url.protocol === "https:";
    }
    catch {
        return false;
    }
}

function officialOrigin(reference, platformId) {
    if (reference?.originAttributionStatus === "trusted_search_no_source_url") {
        return "";
    }
    const candidates = OFFICIAL_ORIGIN_KEYS.map((key) => reference?.[key])
        .map((value) => String(value || "").trim())
        .filter(Boolean);
    for (const candidate of candidates) {
        if (isOfficialUrl(candidate)
            || (DKNOW_OFFICIAL_PLATFORMS.has(platformId)
                && reference?.originAttributionStatus === "trusted_search_official_url"
                && isHttpUrl(candidate))) {
            return candidate;
        }
    }
    const primary = String(reference?.url || "").trim();
    return isOfficialUrl(primary) ? primary : "";
}

function isDknowTrustedReference(reference, platformId) {
    if (!DKNOW_OFFICIAL_PLATFORMS.has(platformId)) {
        return false;
    }
    return Boolean(reference?.url
        || reference?.title
        || reference?.snippet
        || reference?.text
        || reference?.content);
}

export function sourceDescriptor(reference, platformId = "") {
    const url = String(reference?.url || "");
    if (isDknowTrustedReference(reference, platformId)) {
        const hasOfficialSourceUrl = reference?.originAttributionStatus === "trusted_search_official_url";
        return {
            key: "dknow_trusted_search_official",
            label: "官方来源",
            officialOriginUrl: officialOrigin(reference, platformId),
            note: hasOfficialSourceUrl
                ? "由深知可信搜索提供，统一按官方来源处理；已返回来源链接"
                : "由深知可信搜索提供，统一按官方来源处理；来源链接待补"
        };
    }
    if (isOfficialUrl(url)) {
        return { key: "official_site", label: "官方来源", officialOriginUrl: url };
    }
    return { key: "non_official", label: "非官方来源", officialOriginUrl: "" };
}
