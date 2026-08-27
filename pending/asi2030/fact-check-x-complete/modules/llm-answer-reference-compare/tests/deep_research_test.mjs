import assert from "node:assert/strict";
import { writeFile } from "node:fs/promises";

import {
    activateDknowcDeepResearch
} from "../assets/tool/dist/capture/generic-chat.js";
import {
    builtInPlatforms
} from "../assets/tool/dist/capture/platform-registry.js";
import { sourceDescriptor } from "../assets/tool/dist/report/source-level.js";

assert.deepEqual(
    builtInPlatforms.map((platform) => platform.name),
    [
        "doubao",
        "yuanbao",
        "deepseek",
        "qianwen",
        "dknowc-chat",
        "dknowc-deep-research",
        "generic",
    ]
);

const config = builtInPlatforms.find(
    (platform) => platform.name === "dknowc-deep-research"
);
assert.ok(config);
assert.equal(config.label, "深知晓（深度溯源）");
assert.equal(
    config.url,
    "https://poc1.dknowc.cn/wlcb/shenzhimini-test5/"
);
assert.equal(config.profile, "dknowc-chat");
assert.notEqual(config.name, "dknowc-chat");

const deepResearchSource = sourceDescriptor({
    title: "深度研究政策材料",
    url: "https://poc1.dknowc.cn/wlcb/DT_DATA/policy/1",
    snippet: "政策原文"
}, "dknowc-deep-research");
assert.equal(deepResearchSource.key, "dknow_trusted_search_official");
assert.equal(deepResearchSource.label, "官方来源");

const nonGovOrigin = sourceDescriptor({
    title: "商业法律数据库中的官方文件",
    url: "https://yun.dknowc.cn/wlcb/ShenZhi-policy/#/policyDetails?id=1",
    resourceUrl: "https://law.wkinfo.com.cn/document/1",
    originAttributionStatus: "trusted_search_official_url",
    snippet: "官方文件内容"
}, "dknowc-chat");
assert.equal(nonGovOrigin.label, "官方来源");
assert.equal(nonGovOrigin.officialOriginUrl, "https://law.wkinfo.com.cn/document/1");

const noOrigin = sourceDescriptor({
    title: "深知收录材料",
    url: "https://yun.dknowc.cn/wlcb/ShenZhi-policy/#/policyDetails?id=2",
    originAttributionStatus: "trusted_search_no_source_url",
    snippet: "官方文件内容"
}, "dknowc-chat");
assert.equal(noOrigin.label, "官方来源");
assert.equal(noOrigin.officialOriginUrl, "");
assert.match(noOrigin.note, /来源链接待补/);

let clicked = 0;
const ordinaryPage = {
    locator(selector) {
        assert.equal(selector, ".chatgpt-deepsearch.open");
        return {
            last() {
                return this;
            },
            nth() {
                return this;
            },
            async count() {
                return 1;
            },
            async isVisible() {
                return true;
            },
            async click() {
                clicked += 1;
            },
        };
    },
    async waitForTimeout() {},
};
const reportPage = {
    async waitForLoadState() {},
    url() {
        return "https://poc1.dknowc.cn/wlcb/SDSYbaogao/?uid=test";
    },
};
const context = {
    pages() {
        return [ordinaryPage];
    },
    async waitForEvent(event) {
        assert.equal(event, "page");
        return reportPage;
    },
};
assert.equal(
    await activateDknowcDeepResearch(
        ordinaryPage,
        context,
        config,
        1000
    ),
    reportPage
);
assert.equal(clicked, 1);

const wrongPage = {
    async waitForLoadState() {},
    url() {
        return "https://poc1.dknowc.cn/wlcb/shenzhimini-test5/";
    },
};
const wrongContext = {
    pages() {
        return [ordinaryPage];
    },
    async waitForEvent() {
        return wrongPage;
    },
};
await assert.rejects(
    activateDknowcDeepResearch(
        ordinaryPage,
        wrongContext,
        config,
        1000
    ),
    /打开了非预期页面/
);

if (process.env.FACT_CHECK_X_ASSERTIONS_OUTPUT) {
    await writeFile(
        process.env.FACT_CHECK_X_ASSERTIONS_OUTPUT,
        JSON.stringify({
            schemaVersion: "fact-check-x/test-assertions@1",
            actualAssertionIds: [
                "deep_research.independent_platform_registered",
                "deep_research.initial_answer_then_click",
                "deep_research.report_page_required",
                "deep_research.source_policy_official",
                "dknow.non_gov_origin_traceable",
                "dknow.missing_origin_not_downgraded",
            ],
        })
    );
}
console.log("PASS 深知晓深度研究独立平台链路");
