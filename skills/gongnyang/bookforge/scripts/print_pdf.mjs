// bookforge: HTML -> PDF via Playwright Chromium (preferCSSPageSize).
// Usage: NODE_PATH=$(npm root -g) node print_pdf.mjs <input.html> <output.pdf>
//
// W5 재판정 N2 메모: 도해 widths 값 축을 여기(live DOM)에 세우려 했으나 실측으로 기각했다 —
// `@page` size·margin은 실제 print 페이지네이션에서만 레이아웃에 반영되고, `page.pdf()` 호출
// 전의 `page.evaluate()`는 (emulateMedia('print') 여부와 무관하게) 뷰포트 기준 화면 레이아웃을
// 본다. `.chapter-body`를 재면 뷰포트 폭(1280px=338.667mm)이 나와 6스타일 정상 케이스까지
// 오탐으로 죽는다(실측 확인). 값 대조는 build_html.py가 ①이미 이 프로세스가 만든 pass1.pdf의
// 실제 MediaBox(진짜 물리 출력)와 ②theme.css `@page` 정적 파싱을 함께 써서 처리한다
// (typst ③'과 대칭 — 그쪽도 실제로는 정적 계산이다).
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const [html, out] = process.argv.slice(2);
if (!html || !out) { console.error("usage: print_pdf.mjs <in.html> <out.pdf>"); process.exit(2); }

const browser = await chromium.launch();
const page = await browser.newPage();
page.on("console", m => { if (m.type() === "error") console.error("[page]", m.text()); });
await page.goto("file://" + require("path").resolve(html), { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
await page.pdf({
  path: out,
  preferCSSPageSize: true,
  printBackground: true,
  displayHeaderFooter: false,
});
await browser.close();
console.log("OK pdf:", out);
