// bookforge fo2text — AntV SSR SVG의 <foreignObject><span> 텍스트를 Chromium 실측
// 좌표의 네이티브 <text>로 재구성한다. Typst(usvg)는 foreignObject를 조용히 드롭하므로
// 이 변환 없이는 도해 텍스트가 전멸한다 (A0 실측: 변환 후 pixelmatch ≤2%, PDF 텍스트 실재).
//
// 좌표 계약: 클라이언트 좌표 → SVG 유저 좌표는 반드시 getScreenCTM().inverse() 경유.
// (AntV 루트는 viewBox 원점이 음수 — 예: "-20 -20 462 261" — 단순 빼기는 오프셋 오류.)
// 렌더된 줄이 대조 단위: 방출한 줄 텍스트 목록(labels)이 그대로 G13 게이트의 정본이 된다.
import { readdirSync, readFileSync, writeFileSync } from "node:fs";

const PRETENDARD_WEIGHTS = {
  "Pretendard-Regular.ttf": 400,
  "Pretendard-Medium.ttf": 500,
  "Pretendard-SemiBold.ttf": 600,
  "Pretendard-Bold.ttf": 700,
};

export function fontFaceCss(fontDir) {
  return readdirSync(fontDir)
    .filter((f) => f in PRETENDARD_WEIGHTS)
    .map((f) => `@font-face{font-family:'Pretendard';src:url('file://${fontDir}/${f}');font-weight:${PRETENDARD_WEIGHTS[f]};}`)
    .join("\n");
}

function harnessHtml(svg, fontDir) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
${fontFaceCss(fontDir)}
html,body{margin:0;padding:0;background:#fff;}
#stage foreignObject, #stage foreignObject * { font-family:'Pretendard' !important; }
#stage svg text, #stage svg tspan { font-family:'Pretendard' !important; }
</style></head><body><div id="stage">${svg}</div></body></html>`;
}

// authored SVG(에이전트가 직접 그린 네이티브 <text> 도해) 정규화 — antv 경로와 같은
// 산출 계약 {svg, labels}를 지킨다: Pretendard·실측 font-size를 속성으로 베이크(독립
// 파일화), 라벨 수집(G13 정본), 회전 금지, 텍스트 겹침 즉시 실패.
export async function normalizeAuthoredSvg(page, rawSvg, fontDir) {
  await page.setContent(harnessHtml(rawSvg, fontDir), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  return page.evaluate(() => {
    // computed font-size(user unit)를 속성으로 굽는다. SVG에서 font-size의 computed 값은
    // 유저 좌표계의 px = user unit이므로 scanLabelPt의 환산계(pt/u)와 같은 계다.
    const bakeFontSize = (el, cs) => {
      const px = parseFloat(cs.fontSize);
      if (isFinite(px) && px > 0) el.setAttribute("font-size", px.toFixed(2));
    };
    const svg = document.querySelector("#stage svg");
    if (!svg) throw new Error("no <svg> in input");
    if (svg.querySelector("foreignObject")) {
      throw new Error("authored SVG에 foreignObject 금지 — 네이티브 <text>로 그릴 것");
    }
    const texts = [...svg.querySelectorAll("text")];
    if (!texts.length) throw new Error("authored SVG에 <text> 0개 — 라벨 없는 도해는 수동 SVG 경로(사이드카 없이)로");
    const labels = [];
    const boxes = [];
    texts.forEach((el, idx) => {
      const cs = getComputedStyle(el);
      // 가시성 가드: 인쇄에 실재하지 않는 숨김 텍스트는 라벨 수집·검사 대상에서 제외
      // (antv 트랙 convertForeignObjectText의 0크기 스킵과 같은 기준).
      if (cs.display === "none" || cs.visibility === "hidden") return;
      const m = el.getCTM();
      // 회전·전단 성분 검사 (스케일 허용): b/c가 스케일 대비 유의하면 회전
      if (m && (Math.abs(m.b) > 0.01 * Math.abs(m.a) || Math.abs(m.c) > 0.01 * Math.abs(m.d))) {
        throw new Error(`회전 라벨 금지 — <text> #${idx + 1} '${el.textContent.slice(0, 15)}'`);
      }
      el.setAttribute("font-family", "Pretendard");
      // 급수는 **DOM 실측(computed)을 언제나 굽는다.** 종전엔 속성이 없을 때만 구웠고
      // `<tspan>`은 아예 굽지 않아서, `<style>.big{font-size:34px}` + `<tspan class="big">`가
      // 급수 축의 사각지대였다(W5 판정 K6). 그 결과 같은 metrics 안에서 `sizesPt`는
      // 9.974pt를, `labelPaint`는 30.83pt를 기록하는 **이중 진리**가 생겼다 —
      // scanLabelPt(정규식)와 measureLabelPaint(DOM)가 다른 것을 보고 있었다.
      // computed를 속성으로 구우면 두 축이 같은 숫자를 본다. 렌더 외형은 불변이다:
      // 표현 속성은 CSS 선언보다 우선순위가 낮아 `<style>` 규칙이 그대로 이긴다
      // (pixelSelfCheck가 이 불변을 회차마다 어서션한다).
      bakeFontSize(el, cs);
      for (const sp of el.querySelectorAll("tspan")) {
        const spcs = getComputedStyle(sp);
        if (spcs.display === "none" || spcs.visibility === "hidden") continue;
        sp.setAttribute("font-family", "Pretendard");
        bakeFontSize(sp, spcs);
      }
      // <text> 하위 '모든' 텍스트 노드를 단위로 순회 — tspan에 감싸이지 않은 형제
      // 텍스트 노드(<text>Label: <tspan>42</tspan></text>의 'Label: ')도 라벨 수집(G13
      // 정본)과 겹침 bbox 검사에 포함한다.
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        const t = node.textContent.replace(/\s+/g, " ").trim();
        if (!t) continue;
        const pcs = node.parentElement === el ? cs : getComputedStyle(node.parentElement);
        if (pcs.display === "none" || pcs.visibility === "hidden") continue;
        const range = document.createRange();
        range.selectNodeContents(node);
        const r = range.getBoundingClientRect();
        if (r.width === 0 && r.height === 0) continue; // 0크기 스킵 (antv 트랙과 동일)
        labels.push(t);
        boxes.push({ idx, text: t, left: r.left, right: r.right, top: r.top, bottom: r.bottom });
      }
    });
    // 텍스트 요소 간 겹침 감지 (fo2text와 동일 임계)
    for (let i = 0; i < boxes.length; i++) {
      for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i], b = boxes[j];
        if (a.idx === b.idx) continue;
        const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (ox <= 0 || oy <= 0) continue;
        const minH = Math.min(a.bottom - a.top, b.bottom - b.top);
        if (oy > minH * 0.35 && ox > 2) {
          throw new Error(`text overlap: '${a.text.slice(0, 15)}' ↔ '${b.text.slice(0, 15)}' — 라벨 축약·재배치 필요`);
        }
      }
    }
    return { svg: new XMLSerializer().serializeToString(svg), labels };
  });
}

// page: 재사용되는 Playwright Page. 반환 { svg, labels }
export async function convertForeignObjectText(page, rawSvg, fontDir) {
  await page.setContent(harnessHtml(rawSvg, fontDir), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  return page.evaluate(() => {
    const svg = document.querySelector("#stage svg");
    if (!svg) throw new Error("no <svg> in input");
    const ctm = svg.getScreenCTM().inverse();
    const toUser = (x, y) => { const p = new DOMPoint(x, y).matrixTransform(ctm); return [p.x, p.y]; };
    const scale = ctm.a;
    const lines = [];
    const lineBoxes = []; // 노드 간 겹침 감지용 (클라이언트 좌표)
    let nodeIdx = 0;
    const foList = [...svg.querySelectorAll("foreignObject")];
    for (const fo of foList) {
      const walker = document.createTreeWalker(fo, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        nodeIdx++;
        const raw = node.textContent;
        if (!raw.trim()) continue;
        const cs = getComputedStyle(node.parentElement);
        const writing = cs.writingMode || "horizontal-tb";
        if (!writing.startsWith("horizontal")) {
          throw new Error(`vertical/rotated text unsupported (writing-mode=${writing}) — DSL에서 회전 라벨 금지`);
        }
        const charBoxes = [];
        for (let i = 0; i < raw.length; i++) {
          const r = document.createRange();
          r.setStart(node, i); r.setEnd(node, i + 1);
          const b = r.getBoundingClientRect();
          if (b.width === 0 && b.height === 0) continue;
          if (b.height > 0 && b.width > b.height * 3 && raw[i].trim()) {
            throw new Error("rotated glyph box detected — DSL에서 회전 라벨 금지");
          }
          charBoxes.push({ ch: raw[i], left: b.left, right: b.right, top: b.top, bottom: b.bottom });
        }
        if (!charBoxes.length) continue;
        let cur = null;
        const nodeLines = [];
        for (const cb of charBoxes) {
          if (!cur || Math.abs(cb.top - cur.top) > 1.5) {
            cur = { text: "", left: cb.left, right: cb.right, top: cb.top, bottom: cb.bottom };
            nodeLines.push(cur);
          }
          cur.text += cb.ch;
          cur.left = Math.min(cur.left, cb.left);
          cur.right = Math.max(cur.right, cb.right);
          cur.bottom = Math.max(cur.bottom, cb.bottom);
        }
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        const fontSize = parseFloat(cs.fontSize);
        ctx.font = `${cs.fontWeight} ${fontSize}px Pretendard`;
        const m = ctx.measureText("한Ag");
        const ascent = m.fontBoundingBoxAscent;
        const fontBox = m.fontBoundingBoxAscent + m.fontBoundingBoxDescent;
        for (const ln of nodeLines) {
          const boxH = ln.bottom - ln.top;
          const leading = boxH > fontSize * 1.05 ? Math.max(0, (boxH - fontBox) / 2) : 0;
          const [ux, uy] = toUser(ln.left, ln.top + leading + ascent);
          lineBoxes.push({ nodeIdx, text: ln.text, left: ln.left, right: ln.right, top: ln.top, bottom: ln.bottom });
          lines.push({
            text: ln.text.replace(/\s+$/, ""),
            x: +ux.toFixed(2),
            y: +uy.toFixed(2),
            fontSize: +(fontSize * scale).toFixed(2),
            fontWeight: cs.fontWeight,
            fill: cs.color,
            letterSpacing: cs.letterSpacing === "normal" ? null : cs.letterSpacing,
          });
        }
      }
    }
    // 노드 간 줄 겹침 감지 — SSR의 자체 폰트 메트릭이 Pretendard보다 좁아 라벨이
    // 박스를 넘쳐 다른 텍스트를 덮는 경우가 있다(조용한 시각 결함). 겹치면 즉시 실패
    // → 대응은 라벨 축약 또는 템플릿 교체 (references/diagrams.md).
    for (let i = 0; i < lineBoxes.length; i++) {
      for (let j = i + 1; j < lineBoxes.length; j++) {
        const a = lineBoxes[i], b = lineBoxes[j];
        if (a.nodeIdx === b.nodeIdx) continue;
        const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (ox <= 0 || oy <= 0) continue;
        const minH = Math.min(a.bottom - a.top, b.bottom - b.top);
        if (oy > minH * 0.35 && ox > 2) {
          throw new Error(`text overlap: '${a.text.slice(0, 15)}' ↔ '${b.text.slice(0, 15)}' — 라벨 축약 필요`);
        }
      }
    }
    const NS = "http://www.w3.org/2000/svg";
    const g = document.createElementNS(NS, "g");
    g.setAttribute("class", "bf-textlayer");
    for (const ln of lines) {
      const t = document.createElementNS(NS, "text");
      t.setAttribute("x", ln.x); t.setAttribute("y", ln.y);
      t.setAttribute("font-family", "Pretendard");
      t.setAttribute("font-size", ln.fontSize);
      t.setAttribute("font-weight", ln.fontWeight);
      t.setAttribute("fill", ln.fill);
      if (ln.letterSpacing) t.setAttribute("letter-spacing", ln.letterSpacing);
      t.textContent = ln.text;
      g.appendChild(t);
    }
    foList.forEach((fo) => fo.remove());
    svg.appendChild(g);
    return {
      svg: new XMLSerializer().serializeToString(svg),
      labels: lines.map((l) => l.text),
    };
  });
}

// 자기검증: 원본/변환 SVG를 같은 하네스에서 스크린샷 → 픽셀 상이율 반환.
export async function pixelSelfCheck(browser, rawSvg, convertedSvg, fontDir, tmpPrefix) {
  // 1순위 벤더 번들(pixelmatch·pngjs 동봉), 폴백 node_modules
  let pixelmatch, PNG;
  try {
    ({ pixelmatch, PNG } = await import(new URL("../vendor/antv-ssr.bundle.mjs", import.meta.url).href));
  } catch {
    ({ default: pixelmatch } = await import("pixelmatch"));
    ({ PNG } = await import("pngjs"));
  }
  const shots = [];
  for (const [markup, tag] of [[rawSvg, "orig"], [convertedSvg, "conv"]]) {
    const p = await browser.newPage({ viewport: { width: 1600, height: 1200 }, deviceScaleFactor: 2 });
    await p.setContent(harnessHtml(markup, fontDir), { waitUntil: "networkidle" });
    await p.evaluate(() => document.fonts.ready);
    const file = `${tmpPrefix}.${tag}.png`;
    await p.locator("#stage svg").screenshot({ path: file });
    await p.close();
    shots.push(file);
  }
  const a = PNG.sync.read(readFileSync(shots[0]));
  const b = PNG.sync.read(readFileSync(shots[1]));
  if (a.width !== b.width || a.height !== b.height) return { ratio: 1, note: "size mismatch" };
  const diff = new PNG({ width: a.width, height: a.height });
  const n = pixelmatch(a.data, b.data, diff.data, a.width, a.height, { threshold: 0.1 });
  writeFileSync(`${tmpPrefix}.diff.png`, PNG.sync.write(diff));
  return { ratio: n / (a.width * a.height) };
}
