"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");

const helperPath = "../scripts/kakao-place-rating.mjs";

// Fixtures mirror the real Kakao Local keyword-search documents and the real
// m.map.kakao.com searchView item markup captured on 2026-09-15.
const KAKAO_DOCUMENTS = [
  {
    id: "1479300828",
    place_name: "명동교자 명동역점 신관 본점",
    category_name: "음식점 > 한식 > 국수 > 칼국수",
    phone: "02-776-5559",
    address_name: "서울 중구 충무로2가 64-6",
    road_address_name: "서울 중구 퇴계로 129",
    x: "126.986083137398",
    y: "37.5611814714638",
    place_url: "http://place.map.kakao.com/1479300828"
  },
  {
    id: "26567082",
    place_name: "명동교자 분점",
    category_name: "음식점 > 한식 > 국수",
    phone: "",
    address_name: "서울 중구 명동2가 29",
    road_address_name: "서울 중구 명동10길 29",
    x: "126.985",
    y: "37.563",
    place_url: "http://place.map.kakao.com/26567082"
  },
  {
    id: "1952478679",
    place_name: "명동교자 이태원점",
    category_name: "음식점 > 한식",
    phone: "",
    address_name: "서울 용산구 이태원동 1-1",
    road_address_name: "서울 용산구 이태원로 1",
    x: "126.994",
    y: "37.534",
    place_url: "http://place.map.kakao.com/1952478679"
  },
  {
    id: "1352361549",
    place_name: "명동교자 1호점",
    category_name: "음식점 > 한식",
    phone: "",
    address_name: "서울 중구 명동1가 8-1",
    road_address_name: "서울 중구 명동8길 8",
    x: "126.984",
    y: "37.562",
    place_url: "http://place.map.kakao.com/1352361549"
  }
];

function searchViewItem({ id, title, rating, reviewCount, distractorCount = null }) {
  const ratingBlock = rating === null
    ? ""
    : `<span class="ico_comm star_rate">` +
      `<span class="ico_comm inner_star" style="width:52%">평점 :</span>` +
      `<em class="num_rate">${rating}</em></span>` +
      `<span class="txt_num">(${reviewCount})</span>`;
  const distractor = distractorCount === null
    ? ""
    : `<span class="txt_num">(${distractorCount})</span>`;
  return (
    `<li class="search_item base" data-id="${id}" data-cid="${id}" data-type="place" data-title="${title}">` +
    `<a href="javascript:;" class="link_result">` +
    `<span class="info_result">` +
    `<span class="txt_tit"><strong class="tit_g">${title}</strong><span class="txt_ginfo ">칼국수</span></span>` +
    `<span class="info_detail">${distractor}${ratingBlock}` +
    `<span class="txt_addr">서울 중구 퇴계로 129</span>` +
    `</span></span></a></li>`
  );
}

// The rated item deliberately carries a distractor txt_num (an unrelated count
// span) BEFORE the star_rate block, so a naive first-match parser would read
// 999 instead of the real rating count 334 that follows num_rate.
const SEARCH_VIEW_HTML = [
  "<html><body><ul class=\"list_result\">",
  searchViewItem({ id: "1479300828", title: "명동교자 명동역점 신관 본점", rating: "2.6", reviewCount: "334", distractorCount: "999" }),
  searchViewItem({ id: "26567082", title: "명동교자 분점", rating: null, reviewCount: null }),
  searchViewItem({ id: "1952478679", title: "명동교자 이태원점", rating: "3.8", reviewCount: "236" }),
  "</ul></body></html>"
].join("\n");

function jsonResponse(status, payload) {
  return {
    ok: status >= 200 && status < 300,
    status,
    text: async () => (typeof payload === "string" ? payload : JSON.stringify(payload))
  };
}

function stubFetch({ documents = KAKAO_DOCUMENTS, html = SEARCH_VIEW_HTML, proxyStatus = 200, panelStatus = 200 }) {
  return async (url) => {
    const href = String(url);
    if (href.includes("/v1/kakao-map/search/keyword")) {
      return jsonResponse(proxyStatus, proxyStatus === 200 ? { documents } : "proxy exploded");
    }
    if (href.includes("m.map.kakao.com/actions/searchView")) {
      return jsonResponse(panelStatus, panelStatus === 200 ? html : "blocked");
    }
    throw new Error(`unexpected url: ${href}`);
  };
}

test("pickKakaoCandidate selects the unique token-superset branch that matches the address", async () => {
  const { pickKakaoCandidate } = await import(helperPath);
  const result = pickKakaoCandidate(KAKAO_DOCUMENTS, {
    name: "명동교자 본점",
    address: "서울 중구 퇴계로 129"
  });
  assert.equal(result.status, "ok");
  assert.equal(result.document.id, "1479300828");
});

test("pickKakaoCandidate refuses to guess when several branches share the name tokens", async () => {
  const { pickKakaoCandidate } = await import(helperPath);
  const result = pickKakaoCandidate(KAKAO_DOCUMENTS, { name: "명동교자", address: "" });
  assert.equal(result.status, "ambiguous");
});

test("pickKakaoCandidate reports no_match when nothing fits the name", async () => {
  const { pickKakaoCandidate } = await import(helperPath);
  const result = pickKakaoCandidate(KAKAO_DOCUMENTS, { name: "없는가게 본점", address: "서울 중구" });
  assert.equal(result.status, "no_match");
});

test("pickKakaoCandidate rejects a name-only hit whose address is incompatible", async () => {
  const { pickKakaoCandidate } = await import(helperPath);
  const result = pickKakaoCandidate(KAKAO_DOCUMENTS, {
    name: "명동교자 본점",
    address: "부산 해운대구 센텀중앙로 1"
  });
  assert.equal(result.status, "no_match");
});

test("parseSearchViewItems extracts id, title, rating, and the count that follows the rating", async () => {
  const { parseSearchViewItems } = await import(helperPath);
  const items = parseSearchViewItems(SEARCH_VIEW_HTML);
  const rated = items.find((item) => item.id === "1479300828");
  assert.ok(rated, "rated item is parsed");
  assert.equal(rated.title, "명동교자 명동역점 신관 본점");
  assert.equal(rated.rating, 2.6);
  assert.equal(rated.reviewCount, 334);
  const unrated = items.find((item) => item.id === "26567082");
  assert.equal(unrated.rating, null);
  assert.equal(unrated.reviewCount, null);
});

test("parseSearchViewItems returns an empty list for malformed HTML instead of throwing", async () => {
  const { parseSearchViewItems } = await import(helperPath);
  assert.deepEqual(parseSearchViewItems("<div>garbage without items"), []);
  assert.deepEqual(parseSearchViewItems(""), []);
});

test("lookupKakaoPlaceRating returns the aggregate rating for a resolved merchant", async () => {
  const { lookupKakaoPlaceRating } = await import(helperPath);
  const result = await lookupKakaoPlaceRating({
    name: "명동교자 본점",
    address: "서울 중구 퇴계로 129",
    fetchImpl: stubFetch({})
  });
  assert.equal(result.status, "ok");
  assert.equal(result.rating, 2.6);
  assert.equal(result.reviewCount, 334);
  assert.equal(result.kakaoPlaceId, "1479300828");
  assert.equal(result.kakaoPlaceUrl, "http://place.map.kakao.com/1479300828");
});

test("lookupKakaoPlaceRating never guesses on ambiguous merchant names", async () => {
  const { lookupKakaoPlaceRating } = await import(helperPath);
  const result = await lookupKakaoPlaceRating({
    name: "명동교자",
    address: "",
    fetchImpl: stubFetch({})
  });
  assert.equal(result.status, "ambiguous");
  assert.equal(result.rating, null);
});

test("lookupKakaoPlaceRating reports no_match when Kakao has no candidate", async () => {
  const { lookupKakaoPlaceRating } = await import(helperPath);
  const result = await lookupKakaoPlaceRating({
    name: "없는가게 본점",
    address: "서울 중구",
    fetchImpl: stubFetch({ documents: [] })
  });
  assert.equal(result.status, "no_match");
  assert.equal(result.rating, null);
});

test("lookupKakaoPlaceRating reports no_rating when the matched place exposes no score", async () => {
  const { lookupKakaoPlaceRating } = await import(helperPath);
  const result = await lookupKakaoPlaceRating({
    name: "명동교자 분점",
    address: "서울 중구 명동10길 29",
    fetchImpl: stubFetch({})
  });
  assert.equal(result.status, "no_rating");
  assert.equal(result.kakaoPlaceId, "26567082");
  assert.equal(result.rating, null);
});

test("lookupKakaoPlaceRating converts upstream failures into status error without throwing", async () => {
  const { lookupKakaoPlaceRating } = await import(helperPath);
  const proxyDown = await lookupKakaoPlaceRating({
    name: "명동교자 본점",
    address: "서울 중구 퇴계로 129",
    fetchImpl: stubFetch({ proxyStatus: 500 })
  });
  assert.equal(proxyDown.status, "error");
  assert.equal(proxyDown.rating, null);

  const malformed = await lookupKakaoPlaceRating({
    name: "명동교자 본점",
    address: "서울 중구 퇴계로 129",
    fetchImpl: async () => jsonResponse(200, "not json at all")
  });
  assert.equal(malformed.status, "error");
  assert.equal(malformed.rating, null);
});
