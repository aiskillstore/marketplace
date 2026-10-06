#!/usr/bin/env python3
"""bookforge QC gate — the ONLY path from draft/ to final/.

Usage: python3 qc_gate.py <book_dir> [--strict-pages]
Gates (pagination.md §7):
  G10 quote   : (렌더 전) ::: pull 인용·콜아웃 수치가 챕터 본문에 실재 — 날조 차단
  G0  svg     : (렌더 전) 도해 SVG 소스 — foreignObject 잔존/텍스트 부재/외부참조/
                단독문단 위반/사이드카 쌍 무결성/아이콘 탈락 차단
  G13 figtext : (렌더 후) 도해 라벨(fig-*.labels.json)이 PDF 실텍스트에 존재 —
                usvg의 조용한 텍스트 드롭 최종 포착
  G1  render  : draft/book.pdf exists; trim=tokens.trim_mm; page count WARN
                (INV-1 — hard only with --strict-pages)
  G2  fonts   : every font fully embedded
  G3  geometry: OVERFLOW(bbox가 재단 밖, tol 1.5pt) · COLLIDE(텍스트 라인 교차)
                · FIT(앞부속 텍스트가 선언 프레임 안)
  G4  toc     : bookmarks match chapter start pages
  G7  density : FRAME(판면 드리프트)·BLANK(구 G5 흡수)·TAIL·MID·DOC — reach/ink/gap
  G8  stretch : 공기 채움(gap) + 행송 편차 탐지
  G9  keep    : 면 끝 제목 고립 / widow (단일단 스타일)
  G11 roles   : pageroles.json 무결성(코드·선행조건·anchor·예산)
  G12 parity  : 장 시작 직전 필러 백면 (단면 전자책에 인쇄 관습 금지)
  G14 toc     : (tocgate.py) A 인쇄 목차 쪽번호↔폴리오 자기일관 / B 목차↔도비라
                색상(hue) 정합 / C 텍스트 배경 대비 WCAG 하한(대형 3:1, 그 외 4.5:1)
  G16-LINT    : (tests/lint_contrast.py) contrast_contract ↔ theme.css·book-final.html
                실물 대조. 축② pt 정합·축③ 값 커버리지·유령 엔트리는 fails, 축① 완전성은
                WARN. html 엔진 한정(book-final.html 부재 = 명시 skip)
  G17-FIGFIT  : (렌더 후) 도해 figure가 한 면 안 — ① 라벨 전부를 품는 본문 단일 면
                부재(면 분단) ② 도해 라벨 라인이 판면 세로 범위 밖(높이 초과) ③ 배치
                높이 정적 재산출 ≤ diagram.maxHeightMm. 근본 수리는 render_diagrams
                figFitReport(사전 축소/반려) — 이 축은 그 우회의 지면 이중 방어
Writes <book_dir>/gate-report.json. On PASS copies draft/book.pdf -> final/<slug>.pdf.
Exit 0 = PASS, 1 = FAIL. (G6 visual judgement is the agent's job on the contact sheet.)
"""
import json, math, re, shutil, sys, unicodedata
from collections import Counter
from numbers import Real
from pathlib import Path
from statistics import median

try:  # PyMuPDF 1.24+ 신 모듈명, 구버전은 fitz만 제공
    import pymupdf as fitz
except ImportError:
    import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pagemetrics import analyze  # noqa: E402
import g16_tokens  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
TOL = 1.5  # pt
MM2PT = 72 / 25.4

TAIL_HARD = {"essay": 0.35, "magazine": 0.35}          # default 0.45
TAIL_WARN = {"practical": 0.70, "insight": 0.70, "academic": 0.70,
             "business": 0.65, "essay": 0.55, "magazine": 0.50}
WARN_REPORT_ONLY = {"essay", "magazine", "insight"}    # 상용 꼬리 실측 표본 0인 스타일 — HARD만 강제
MID_HARD = 0.75
MID_ROLE_MIN = {"essay": 0.88, "insight": 0.85}       # default 0.90 — insight는 130mm 통짜 블록+H2 24mm 이월 물리
DOC_STATS_STYLES = {"practical", "academic"}  # 문서 통계는 실측 근거 있는 스타일만
ROLE_CODES = {"PART_DIVIDER", "FULL_BLEED_PLATE", "EXEC_SUMMARY",
              "ESSAY_BREATH", "MAGAZINE_WHITESPACE", "TOC_TAIL",
              "CH_CLOSE_APPROVED",   # 꼬리 미달 최종 에스컬레이션 (pagination.md §4)
              "OVERLAP_APPROVED"}    # 기계 판정 불가한 정당한 텍스트 겹침 (G3-COLLIDE)

# ---- G3-COLLIDE 임계 ----
# fo2text.mjs:89-90·:183-184의 SVG 라벨 겹침 판정을 지면으로 이식한다:
#   `const minH = Math.min(a.bottom - a.top, b.bottom - b.top);`
#   `if (oy > minH * 0.35 && ox > 2) throw ...`
# 원본 단위는 **CSS px**(DOM 라인박스의 getBoundingClientRect)다. ox는 길이라 환산이
# 필요하다: 1px = 1/96in, 1pt = 1/72in → 1px = 0.75pt → 2px = 1.5pt.
# oy는 minH에 대한 **비율**이라 단위 불변이므로 0.35를 그대로 옮긴다.
COLLIDE_OX_PT = 2 * 0.75
COLLIDE_OY_FRAC = 0.35
# OVERLAP_APPROVED가 열 수 있는 교차의 기계 상한(G11 선행조건). 면제가 면 단위라
# 사유서가 지목하지 않은 겹침까지 함께 열리므로, "승인으로 설명 가능한 교차"의 크기를
# 검출 임계의 2배로 묶는다 — 근거·실측은 G11의 해당 분기 주석.
OVERLAP_APPROVE_MAX_OX_PT = 2 * COLLIDE_OX_PT
# OVERLAP_APPROVED 승인 면의 교차 **건수** 상한(W4 재판정 R-2). 면제는 좌표가 아니라
# 면 단위라, 개별 교차가 전부 ㉢(ox <= 3.0pt) 이내라도 건수가 쌓이면 폭발 반경이 넓어진다
# — 실측(overlap_attack.py): ox 2.9pt(상한 이내) 교차 20건을 한 면에 심고 사유서 1줄로
# 승인하면 pass=True가 됐다. 사소한 물림(장식 글리프가 행 끝에 머리카락만큼 물리는 것)의
# 현실 범위는 한 면에 2~3건이고, 그 이상(특히 수십 건)은 크기가 작아도 "장식"으로 설명될
# 수 없는 조판 붕괴다. 5건은 그 현실 범위(2~3건)에 여유를 더한 상한이다.
OVERLAP_APPROVE_MAX_COUNT = 5
# 세로 박스는 line["bbox"]를 그대로 쓰지 않는다. fo2text가 재는 것은 DOM 라인박스
# (font-size × line-height ≈ 1.0~1.3em)인데 PyMuPDF의 line bbox는 **폰트 선언 bbox**라
# 서체 메트릭에 따라 1.44em까지 부푼다(실측: magazine `.pullquote`의 `::before` 큰따옴표가
# NotoSerifKR-Bold 30pt에서 43.1pt = 1.44em). 그대로 비교하면 임계가 서체에 좌우돼
# 실제로는 붙지도 않은 인용 2행이 FAIL한다(실측 오탐 2건: magazine-trend-brief p7·p13).
# → span origin(베이스라인) 기준 [-0.85em, +0.20em] 박스로 정규화하고 raw bbox로 클립한다.
#   합 1.05em은 CSS 기본 라인박스 대역이고, 한글·라틴 혼식 실잉크 대역의 [하우스] 상수다.
#   실측 여유: 이 상수에서 전 코퍼스 최근접 미검출이 임계의 0.67배(33% 헤드룸).
#
# 🚨 **검출 하한(맹점 대역)** — 이 축이 잡는 것은 "교차 전량"이 아니다.
#   정규화 박스 높이 = 0.85 + 0.20 = 1.05em, 임계 = 0.35 × minH = 0.3675em이므로
#   같은 급수 두 행의 **베이스라인 간격이 1.05 − 0.3675 = 0.6825em 이상이면 산술적으로
#   검출되지 않는다.** 한글 글리프의 실잉크 대역은 대략 1.0em이라
#   **[0.68em, 1.0em) 구간은 실잉크가 겹치는데 게이트가 침묵하는 대역**이다
#   (실측 스윕: 20pt·NotoSerifKR에서 피치 0.70em = 실잉크 949px 미검출, 0.95em = 11px 미검출.
#    W4 판정 D4-1 / `/mnt/d/bookforge-verify/adv-w4final/collide_synth2.json`).
#   상수를 키우면 이 대역은 좁아지지만 오탐(폰트 선언 bbox 1.44em 계열)이 즉시 돌아온다 —
#   현행 조판 계약의 **본문** 행송은 이 대역을 밟지 않으므로(6스타일 1.61~1.84em: insight
#   17.5/9.5 · magazine 5.4mm/9.5 · academic 17.5/10 · business 1.62em) 상수를 유지하고
#   **하한을 명시**한다. 예외는 의도적으로 조인 디스플레이 행송(magazine `.coverline`
#   line-height 0.92 등)인데, 그 대역의 실잉크 교집합은 미미하고(0.90em에서 157px,
#   0.95em에서 11px) 조판 의도 자체가 그렇다. 본문 행송을 0.95em 이하로 잡는 스타일을
#   새로 만들면 이 축은 그 스타일에서 무력하다 — pagination.md G3-COLLIDE 행 동일 문장.
COLLIDE_ASC_EM, COLLIDE_DESC_EM = 0.85, 0.20
# magazine 2단 방어: styles/magazine/theme.css:118 `column-count: 2; column-gap: 8mm`.
# 좌우 단은 y가 100% 겹치므로 x 밴드로 라인을 먼저 분류하고 같은 밴드 안에서만 비교한다.
# 밴드 경계는 판면(tokens `body_frame_mm`)과 단간에서 결정론으로 도출한다 — 실측 좌표
# 하드코딩이 아니다. 단을 걸치는 라인(`column-span: all` h2 등)은 -1로 두어 전 밴드와 비교.
BODY_COLUMNS = {"magazine": (2, 8.0)}   # {style: (단 수, 단간 mm)}
COLLIDE_BAND_TOL_PT = 2.0               # gutter 살짝 침범은 같은 밴드로 흡수


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[\s​]+", "", s)
    s = re.sub(r"[\"'‘’“”「」『』*_`~]", "", s)
    return s.replace(",", "")


def g10_quote_check(book_dir, outline):
    """렌더 전 md 검사: pull 인용 분절(≥12자)과 stat/콜아웃 수치의 본문 실재."""
    problems = []
    for ch in outline["chapters"]:
        p = book_dir / "chapters" / ch["file"]
        if not p.exists():
            continue
        raw = p.read_text(encoding="utf-8")
        callouts = re.findall(r"^:::\s*(pull|statrow|stat|quote|info|tip|warn)[^\n]*\n(.*?)^:::\s*$",
                              raw, re.S | re.M)
        body = re.sub(r"^:::.*?^:::\s*$", "", raw, flags=re.S | re.M)
        nbody = norm(body)
        body_nums = set(re.findall(r"\d[\d,.]*", body.replace(",", "")))
        for kind, ctext in callouts:
            if kind == "pull":
                # build_html 계약과 동일: 1행 = 인용문, 2행 = 화자 라벨(검사 제외)
                ls = [l.strip() for l in ctext.split("\n") if l.strip()]
                quote_line = ls[0] if ls else ""
                frags = [f for f in re.split(r"[…⋯]|\.\.\.|[—–~]", quote_line) if len(norm(f)) >= 12]
                for f in frags:
                    if norm(f) not in nbody:
                        problems.append(f"{ch['file']}: pull 인용이 본문에 없음 — '{f.strip()[:40]}'")
            if kind in ("stat", "statrow"):
                for tok in re.findall(r"\d[\d,.]*", ctext.replace(",", "")):
                    if len(tok) < 2:  # 한 자리 토큰(5G·3nm류)은 오탐 — 검사 제외
                        continue
                    if tok in body_nums:
                        continue
                    ctx = ctext[max(0, ctext.find(tok) - 8):ctext.find(tok)]
                    approx = any(w in ctx for w in ("약", "가량", "내외", "여"))
                    if approx:
                        try:
                            v = float(tok)
                            if any(abs(float(b) - v) <= 0.05 * max(v, 1e-9)
                                   for b in body_nums if _isnum(b)):
                                continue
                        except ValueError:
                            pass
                    problems.append(f"{ch['file']}: stat 수치 '{tok}'가 본문에 없음")
    return problems


def _isnum(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def classify_bbox(raw_bbox, clip):
    """Return (status, normalized bbox) for a raw PyMuPDF block bbox."""
    if (not isinstance(raw_bbox, (list, tuple)) or len(raw_bbox) != 4
            or any(isinstance(v, bool) or not isinstance(v, Real) for v in raw_bbox)):
        return "invalid", None
    try:
        coords = [float(v) for v in raw_bbox]
    except (TypeError, ValueError, OverflowError):
        return "invalid", None
    if not all(math.isfinite(v) for v in coords):
        return "invalid", None
    bbox = fitz.Rect(coords)
    bbox.normalize()
    if bbox.is_empty:
        return "empty", list(bbox)
    return ("inside" if clip.contains(bbox) else "overflow"), list(bbox)


def g3_new_acc():
    return {"overflows": [], "invalid_bboxes": [], "empty_count": 0}


def g3_scan_page(pno, clip, blocks, acc):
    """한 면의 블록 bbox를 분류해 acc에 누적한다. main()의 공유 루프(면당 `get_text`
    1회 계약 — G3 세 축이 같은 blocks를 소비)가 면마다 호출하고, 단독 실행은
    g3_check()가 문서 전체를 이 함수로 돈다."""
    for block in blocks:
        raw_bbox = block.get("bbox")
        status, bbox = classify_bbox(raw_bbox, clip)
        item = {"page": pno + 1,
                "kind": "text" if block.get("type") == 0 else "image"}
        if status == "overflow":
            acc["overflows"].append({**item, "bbox": bbox})
        elif status == "empty":
            acc["empty_count"] += 1
        elif status == "invalid":
            acc["invalid_bboxes"].append({**item, "bbox": repr(raw_bbox)[:200]})


def g3_report(acc):
    overflows, invalid_bboxes = acc["overflows"], acc["invalid_bboxes"]
    return {"overflows": overflows[:20], "count": len(overflows),
            "invalid_bboxes": invalid_bboxes[:20], "invalid_count": len(invalid_bboxes),
            "empty_count": acc["empty_count"],
            "ok": not overflows and not invalid_bboxes}


def g3_check(doc):
    acc = g3_new_acc()
    for pno in range(doc.page_count):
        page = doc[pno]
        pr = page.rect
        clip = fitz.Rect(pr.x0 - TOL, pr.y0 - TOL, pr.x1 + TOL, pr.y1 + TOL)
        g3_scan_page(pno, clip, page.get_text("dict").get("blocks", []), acc)
    return g3_report(acc)


IMG_REF_RE = re.compile(r'!\[[^\]]*\]\((\.\./assets/[^)"\s]+\.svg)(?:\s+"[^"]*")?\)')

# ---- G15 지면 리듬 (스타일별 실측 근거 있는 곳만 강제) ----
# PARA: 단락 최대 행수 (business STYLE.md T2 "단락 최대 8행") — 렌더 전 md 추정 검사
# RHYTHM: 시각 요소 없는 연속 본문 면 상한 (T2 "면당 시각 요소 1~2개"의 최소 방어선)
G15_PARA_CFG = {"business": {"max_lines": 8, "cpl": 36, "tol": 0.6}}
G15_DROUGHT_MAX = {"business": 3}


def _eff_chars(s):
    """행 길이 추정용 유효 글자수 — CJK 전각 1.0, 그 외 0.55."""
    return sum(1.0 if ord(c) > 0x2E7F else 0.55 for c in s)


SCALE_TOL_PT = 0.3  # 실측: 정상 8권 |측정-선언| <= 0.01pt(float 표현차), 축소본 1.87pt


def body_pt_mode(doc):
    """본문 최빈 pt — 글자 수 가중(행 수 기준이면 표·리스트가 본문을 이긴다).
    앞부속 대형 활자는 글자 수가 적어 최빈값을 흔들지 못한다(실측 확인)."""
    sz = Counter()
    for pno in range(doc.page_count):
        for blk in doc[pno].get_text("dict").get("blocks", []):
            for ln in blk.get("lines", []):
                for sp in ln["spans"]:
                    if sp["text"].strip():
                        sz[round(sp["size"], 2)] += len(sp["text"].strip())
    return sz.most_common(1)[0][0] if sz else None


def g1_scale_check(doc, decl_pt, tol=SCALE_TOL_PT):
    """G1-SCALE: 선언 본문 급수 대조. (측정값, problems) 반환.
    뮤테이션 스위트가 이 함수를 직접 호출해 감도를 고정한다."""
    meas = body_pt_mode(doc)
    if meas is None or decl_pt is None or abs(meas - decl_pt) <= tol:
        return meas, []
    return meas, [
        f"본문 최빈 {meas:.2f}pt vs tokens body_pt {decl_pt}pt (비 {meas / decl_pt:.4f}) — "
        "전역 축소/확대. Chromium shrink-to-fit 의심: 목차·표·도해 중 판면을 넘긴 요소를 "
        "찾아 원고/조판에서 줄일 것(폰트 크기 조정으로 대응 금지)"]


def g15_para_check(book_dir, outline, style):
    cfg = G15_PARA_CFG.get(style)
    if not cfg:
        return []
    problems = []
    for ch in outline["chapters"]:
        p = book_dir / "chapters" / ch["file"]
        if not p.exists():
            continue
        raw = re.sub(r"^:::.*?^:::\s*$", "", p.read_text(encoding="utf-8"), flags=re.S | re.M)
        for para in re.split(r"\n\s*\n", raw):
            para = para.strip()
            if not para or para[0] in "#!|>-+`[":
                continue  # 제목·이미지·표·인용·리스트·펜스는 비대상
            if re.match(r"\d+\.\s", para):
                continue  # 순번 리스트
            est = _eff_chars(para.replace("\n", "")) / cfg["cpl"]
            if est > cfg["max_lines"] + cfg["tol"]:
                problems.append(f"{ch['file']}: 단락 추정 {est:.1f}행 > {cfg['max_lines']}행 "
                                f"— '{para[:28]}…' 분할 필요")
    return problems


def g15_drought_check(pages, page_texts, first_ch, structural, style):
    """시각 요소(도해·표·박스·키 스탯 디스플레이) 없는 연속 본문 면 상한."""
    limit = G15_DROUGHT_MAX.get(style)
    if not limit:
        return []
    problems, run = [], []
    for p in pages:
        pg = p["page"]
        if pg < first_ch or pg in structural:
            if len(run) > limit:
                problems.append(f"연속 순텍스트 본문 {len(run)}면 {run} > {limit}면")
            run = []
            continue
        txt = page_texts[pg - 1]
        visual = (p["imgarea"] >= 0.02 or p.get("vecarea", 0) >= 0.02
                  or any(l["size"] >= 20 for l in p["_lines"])
                  or "<표" in txt or "[그림" in txt)
        if visual:
            if len(run) > limit:
                problems.append(f"연속 순텍스트 본문 {len(run)}면 {run} > {limit}면")
            run = []
        else:
            run.append(pg)
    if len(run) > limit:
        problems.append(f"연속 순텍스트 본문 {len(run)}면 {run} > {limit}면")
    return problems


def g0_svg_check(book_dir, outline):
    """렌더 전 도해 SVG 소스 검사 — Typst(usvg)는 foreignObject를 에러 없이 드롭하므로
    조용한 텍스트 전멸을 빌드 전에 차단한다."""
    problems = []
    referenced = []
    for ch in outline["chapters"]:
        p = book_dir / "chapters" / ch["file"]
        if not p.exists():
            continue
        paragraphs = re.split(r"\n\s*\n", p.read_text(encoding="utf-8"))
        for para in paragraphs:
            refs = IMG_REF_RE.findall(para)
            if not refs:
                continue
            # md2typ 승격 조건: 이미지 단독 문단이 아니면 이미지가 조용히 증발한다
            rest = IMG_REF_RE.sub("", para).strip()
            if rest:
                problems.append(f"{ch['file']}: SVG 이미지 문단에 다른 텍스트 혼합 — "
                                f"단독 문단이어야 승격됨: '{para.strip()[:50]}…'")
            referenced.extend(refs)
    for ref in referenced:
        name = ref[len("../assets/"):]
        svg_path = book_dir / "assets" / name
        if not svg_path.exists():
            problems.append(f"G0: 참조된 {name} 부재 (프리렌더 미실행?)")
            continue
        svg = svg_path.read_text(encoding="utf-8")
        if "<foreignObject" in svg:
            problems.append(f"{name}: foreignObject 잔존 — Typst에서 텍스트 전멸")
        if "xml-stylesheet" in svg or re.search(r'(?:href|src)="https?://', svg):
            problems.append(f"{name}: 외부 참조(CDN 폰트/미인라인 자원) 잔존")
        stem = name[:-len(".svg")]
        sidecar = book_dir / "diagrams" / f"{stem}.json"
        labels_path = book_dir / "assets" / f"{stem}.labels.json"
        if sidecar.exists():
            sc = json.loads(sidecar.read_text(encoding="utf-8"))
            bf = sc.get("bf", {})
            kind = sc.get("kind", "antv")
            if kind not in ("antv", "authored"):
                problems.append(f"{stem}.json: kind '{kind}'는 antv|authored만")
            if kind == "authored" and not (book_dir / "diagrams" / f"{stem}.svg").exists():
                problems.append(f"{stem}: kind=authored인데 diagrams/{stem}.svg 소스 부재")
            if not labels_path.exists():
                problems.append(f"{name}: labels.json 부재 — 프리렌더 산출물 불완전")
            elif json.loads(labels_path.read_text(encoding="utf-8")) and "<text" not in svg:
                problems.append(f"{name}: 라벨이 있는데 SVG에 <text> 0개")
            if bf.get("icons") is True and "<symbol" not in svg:
                problems.append(f"{name}: icons:true인데 <symbol> 0개 — 아이콘 조용한 탈락")
        elif "<text" not in svg and "<foreignObject" not in svg:
            # 수동 SVG(사이드카 없음)는 외부참조/foreignObject 검사만 — 텍스트 없는 순수 도형 허용
            pass
    return problems


def g13_figtext_check(book_dir, outline, page_texts):
    """렌더 후: 프리렌더 라벨(렌더된 줄 단위)이 PDF 실텍스트에 존재하는지 대조."""
    problems = []
    all_norm = norm("".join(page_texts))
    referenced = set()
    for ch in outline["chapters"]:
        p = book_dir / "chapters" / ch["file"]
        if p.exists():
            referenced.update(IMG_REF_RE.findall(p.read_text(encoding="utf-8")))
    for ref in sorted(referenced):
        stem = ref[len("../assets/"):-len(".svg")]
        labels_path = book_dir / "assets" / f"{stem}.labels.json"
        if not labels_path.exists():
            continue  # 수동 SVG — G13 비대상 (G0에서 소스 검사만)
        for label in json.loads(labels_path.read_text(encoding="utf-8")):
            if len(norm(label)) >= 2 and norm(label) not in all_norm:
                problems.append(f"{stem}: 라벨 '{label[:30]}'이 PDF 텍스트에 없음")
    return problems


def g17_figfit_check(book_dir, outline, page_texts, line_recs, page_size, tokens, first_ch):
    """G17-FIGFIT (W7 신설): 도해 figure(도해+캡션)가 한 면 안에 들어갔는가 — 최종 PDF 기준.

    실증 사고: insight 세로 셰브런 도해(폭 130mm × 종횡비 1.96 = 배치 높이 254.8mm)가
    판면 높이(190mm)를 넘어 Chromium print가 break-inside:avoid를 지키지 못하고
    p5(단계 01~03)/p6(단계 04+캡션)으로 **면을 넘겨 쪼갰다** — 기존 전 축이 통과했다
    (G13은 라벨 실재만, G3-OVERFLOW는 페이지 밖 bbox만 본다). 근본 수리는
    render_diagrams.figFitReport(배치 높이 사전 산출 → 폭 비례 축소/반려)이고, 이 축은
    그 수리를 우회한 산출물(산출 SVG 수동 변조·빌더의 fit 폭 전사 누락 회귀)을 최종
    지면에서 잡는 이중 방어다.

    세 술어(labels.json이 있는 사이드카 도해만 — 수동 SVG는 G0 계약 그대로 비대상):
      ① 분단: 그 도해의 유효 라벨(정규화 2자 이상) 전부를 품는 **본문 단일 면이 없다**
         → HTML 트랙의 면 분단. 본문 산문에 라벨과 같은 구절이 우연히 더 있어도
         "전부를 품는 면의 존재"는 흔들리지 않는다(도해 면 자체가 그 면이다).
      ② 판면 초과: 라벨 전부를 품는 면에서 라벨과 정규화 일치하는 텍스트 라인의 세로
         범위가 body_frame_mm 밖 → typst 트랙의 지면 증거(이미지를 쪼개는 대신 판면
         아래로 넘친다). 숫자-only 라벨(배지 01/02)과 회전 라인(세로 러닝헤드)은 대조에서
         제외하고, 대상 면을 본문(first_ch 이후)으로 한정해 목차·앞부속 오탐을 차단한다.
      ③ 정적 재산출: 산출 SVG viewBox 종횡비 × 배치 폭(metrics.fit.widthMm 우선, 없으면
         tokens.diagram.widths[bf.width]) ≤ diagram.maxHeightMm + 0.5 — 렌더 판정과 지면
         배치가 같은 값을 말하는지의 대조."""
    problems = []
    dg = tokens.get("diagram") or {}
    widths = dg.get("widths") if isinstance(dg.get("widths"), dict) else {}
    max_h = dg.get("maxHeightMm")
    frame = tokens.get("body_frame_mm")
    pages_norm = [norm(t) for t in page_texts]
    referenced = set()
    for ch in outline["chapters"]:
        p = book_dir / "chapters" / ch["file"]
        if p.exists():
            referenced.update(IMG_REF_RE.findall(p.read_text(encoding="utf-8")))
    for ref in sorted(referenced):
        stem = ref[len("../assets/"):-len(".svg")]
        labels_path = book_dir / "assets" / f"{stem}.labels.json"
        svg_path = book_dir / "assets" / f"{stem}.svg"
        # ---- ③ 정적 재산출 (라벨 유무와 무관) ----
        if svg_path.exists() and isinstance(max_h, (int, float)) and not isinstance(max_h, bool):
            svg_text = svg_path.read_text(encoding="utf-8")
            vb = re.search(r'viewBox="[-\d. ]*?([\d.]+) ([\d.]+)"', svg_text)
            placed_w = None
            sidecar = book_dir / "diagrams" / f"{stem}.json"
            if sidecar.exists():
                try:
                    bf = json.loads(sidecar.read_text(encoding="utf-8")).get("bf") or {}
                    placed_w = widths.get(bf.get("width") or "full")
                except ValueError:
                    placed_w = None
            metrics_path = book_dir / "assets" / f"{stem}.metrics.json"
            if metrics_path.exists():
                try:
                    fit = json.loads(metrics_path.read_text(encoding="utf-8")).get("fit") or {}
                    if fit.get("verdict") == "shrunk" and isinstance(fit.get("widthMm"), (int, float)):
                        placed_w = fit["widthMm"]
                except ValueError:
                    pass
            if vb and isinstance(placed_w, (int, float)) and not isinstance(placed_w, bool) and placed_w > 0:
                vb_w, vb_h = float(vb.group(1)), float(vb.group(2))
                if vb_w > 0:
                    placed_h = placed_w * vb_h / vb_w
                    if placed_h > max_h + 0.5:
                        problems.append(
                            f"{stem}: 배치 높이 {placed_h:.1f}mm > 상한 {max_h}mm "
                            f"(폭 {placed_w:g}mm × viewBox {vb_w:g}:{vb_h:g}) — "
                            f"figure가 한 면에 들어갈 수 없다(렌더 fit 판정 우회 의심)")
        # ---- ①·② 지면 술어 ----
        if not labels_path.exists():
            continue  # 수동 SVG — G13과 같은 비대상 계약
        labels = [l for l in json.loads(labels_path.read_text(encoding="utf-8"))
                  if len(norm(l)) >= 2]
        if not labels:
            continue
        host = [i + 1 for i, pn in enumerate(pages_norm)
                if i + 1 >= first_ch and all(norm(l) in pn for l in labels)]
        if not host:
            problems.append(f"{stem}: 도해 면 분단 — 라벨 {len(labels)}건 전부를 품는 "
                            f"본문 단일 면 없음(figure가 면 경계에서 쪼개짐)")
            continue
        if not frame:
            continue
        top, _right, bottom, _left = frame
        lab_norms = {norm(l) for l in labels if not norm(l).isdigit()}
        for pg in host:
            _w_pt, h_pt = page_size.get(pg, (None, None))
            if h_pt is None:
                continue
            y0f, y1f = top * MM2PT - TOL, h_pt - bottom * MM2PT + TOL
            for rec in line_recs.get(pg, []):
                if rec["rot"] or norm(rec["text"]) not in lab_norms:
                    continue
                ry0, ry1 = rec["raw"][1], rec["raw"][3]
                if ry0 < y0f or ry1 > y1f:
                    problems.append(
                        f"{stem}: p{pg} 도해 라벨 '{rec['text'][:16]}' 판면 세로 범위 밖 "
                        f"(y {ry0 / MM2PT:.1f}~{ry1 / MM2PT:.1f}mm vs 판면 {top}~"
                        f"{(h_pt - bottom * MM2PT) / MM2PT:.1f}mm) — 배치 높이 판면 초과")
    return problems


def _column_bands(style, frame_mm, page_rect):
    """판면 x 구간을 단 수·단간으로 결정론 분할. 1단 스타일은 None(=전면 단일 밴드)."""
    ncol, gap_mm = BODY_COLUMNS.get(style, (1, 0.0))
    if ncol < 2 or not frame_mm:
        return None
    _t, right, _b, left = frame_mm
    fl = left * MM2PT
    fr = page_rect.width - right * MM2PT
    gap = gap_mm * MM2PT
    w = (fr - fl - gap * (ncol - 1)) / ncol
    return [(fl + i * (w + gap), fl + i * (w + gap) + w) for i in range(ncol)]


def _band_of(bands, x0, x1):
    """한 밴드에 온전히 들어가면 그 인덱스, 아니면 -1(단 걸침 → 전 밴드와 비교)."""
    if bands is None:
        return 0
    for i, (a, b) in enumerate(bands):
        if x0 >= a - COLLIDE_BAND_TOL_PT and x1 <= b + COLLIDE_BAND_TOL_PT:
            return i
    return -1


def line_records(blocks, bands):
    """면의 텍스트 라인 레코드. `get_text("dict")` 1회 결과를 G3 세 축이 공유한다.
    raw = PyMuPDF line bbox(프레임 적합 판정용) / box = 베이스라인 정규화 박스(교차 판정용)."""
    recs = []
    for bi, blk in enumerate(blocks):
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            spans = [s for s in ln.get("spans", []) if s.get("text", "").strip()]
            if not spans:
                continue
            rx0, ry0, rx1, ry1 = ln["bbox"]
            # ── 정규화의 전제: 라인이 **수평 정립**(dir == (1,0))일 것 ──
            # 정규화는 span origin(베이스라인)에서 세로로만 [-0.85em, +0.20em]를 잡는다.
            # 회전 라인에서 origin은 회전 **전** 기준점이므로 이 계산은 라인이 실제로
            # 점유한 세로 대역과 무관해진다: 90°/270° 라벨(raw 높이 101.8pt)의 정규화
            # 박스가 2.8~11.9pt로 붕괴해 실잉크가 겹치는데도 교차 0건이 됐다(W4 판정 D4-2).
            # 회전 라인은 서체 메트릭 부풀림(정규화의 도입 사유)보다 좌표 붕괴가 훨씬
            # 큰 오차이므로 **raw bbox로 판정**한다 — 검출 방향으로 보수적이다.
            dr = tuple(round(v, 3) for v in (ln.get("dir") or (1.0, 0.0)))
            if dr != (1.0, 0.0):
                by0, by1 = ry0, ry1
            else:
                by0 = max(min(s["origin"][1] - COLLIDE_ASC_EM * s["size"] for s in spans), ry0)
                by1 = min(max(s["origin"][1] + COLLIDE_DESC_EM * s["size"] for s in spans), ry1)
            if rx1 - rx0 <= 0 or by1 - by0 <= 0:
                continue
            recs.append({"blk": bi, "raw": (rx0, ry0, rx1, ry1), "box": (rx0, by0, rx1, by1),
                         "rot": dr != (1.0, 0.0),
                         "text": "".join(s["text"] for s in spans).strip(),
                         "band": _band_of(bands, rx0, rx1)})
    return recs


def front_frame_for(decl, page_no):
    """tokens `front_frame_mm`에서 이 앞부속 면에 적용할 [top,right,bottom,left]를 고른다.
    리스트면 앞부속 전 면 공통, 객체면 1면=`cover` / 나머지=`toc`(표지는 1면 고정 계약)."""
    if isinstance(decl, dict):
        return decl.get("cover" if page_no == 1 else "toc")
    return decl


# ---- G16-LINT (tests/lint_contrast.py 배선) ----
# 린터의 세 축 중 **CSS만으로 증명되는 것**만 qc_gate의 fails로 올린다. 축① 완전성
# (MISSING = CSS에 있는데 계약에 없다)은 이 책의 원고가 그 요소를 밟았는지에 의존하므로
# WARN이다 — 린터 §5의 설계(전 요소를 밟는 스모크 북에서만 강제력을 갖는다)를 그대로 둔다.
#  · PT_UNATTAINABLE (축②) — 계약이 신고한 pt가 theme.css의 어떤 font-size에도 없다.
#    pt는 contrast_floor의 입력이라 위조하면 계약이 스스로 하한을 4.5 -> 3.0으로 낮춘다.
#  · FG/BG_UNCOVERED (축③) — theme.css의 색이 어떤 엔트리에도 없다. 원고와 무관하다.
#  · GHOST — 엔트리의 성분(색·급수)이 theme.css 어디에도 없다. 계약 쪽 날조라 CSS만으로 증명된다.
#  · NO_CONTRACT / STAMP 3종 — 계약 자체의 부재, decorate.py 상수와의 모순. 파일 대조라 증명 가능.
LINT_HARD_CODES = {"PT_UNATTAINABLE", "FG_UNCOVERED", "BG_UNCOVERED", "GHOST",
                   "NO_CONTRACT", "NO_DECORATE", "NO_CONST", "CONST_MISMATCH"}


def g16_lint_check(book_dir, style):
    """contrast_contract 실물 대조 린터를 출하 경로에서 돌린다.

    이 린터는 `typeset/book-final.html`을 입력으로 하므로 **렌더 전 게이트가 될 수 없고**
    (그래서 build.py의 G16이 아니라 여기 있다), typst 4종에는 그 파일 자체가 없다.
    배선 전에는 코드·CI·문서 어디에도 호출 지점이 없어서 세 축이 전부 무효였고,
    계약 엔트리 절삭·pt 위조·미등재 저대비 규칙 신설이 출하 파이프라인을 통과했다
    (W4 판정 D1). 반환 dict는 그대로 report["gates"]["G16-LINT"]가 된다.

    **중단 지점이 아니다** — FAIL은 fails에 누적만 하고 뒤 게이트를 계속 판정한다.
    린터 자체가 터져도(경로·의존성 문제·**`sys.exit()`이 던지는 `SystemExit` 포함**) 게이트를
    죽이지 않는다: WARN으로 강등한다. `SystemExit`은 `BaseException` 계열이라 평범한
    `except Exception`으로는 못 잡는다 — 아래 호출부는 `(Exception, SystemExit)`을 명시로
    잡는다(단 `KeyboardInterrupt`는 사용자 중단이라 그대로 전파한다). 또한 이 경로에서
    죽더라도 `main()` 진입 시 이미 낡은 `gate-report.json`을 지운 뒤이므로, 죽은 뒤 디스크에
    남는 리포트가 "직전 실행의 오래된 PASS"일 수 없다(W4 재판정 E1).
    """
    res = {"ok": True, "problems": [], "warns": [], "skipped": None}
    html = book_dir / "typeset" / "book-final.html"
    if not html.exists():
        res["skipped"] = (f"typeset/book-final.html 부재 — 이 린터는 HTML DOM에서 실 페어를 "
                          f"도출하므로 typst 엔진 스타일({style})에는 원리적으로 적용 불가")
        return res
    lint_py = SKILL / "tests" / "lint_contrast.py"
    if not lint_py.exists():
        res["skipped"] = f"{lint_py} 부재 — 배포본에서 tests/가 빠졌는지 확인할 것"
        res["warns"].append(res["skipped"])
        return res
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("bf_lint_contrast", lint_py)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod._VIRT_CACHE.clear()
        r = mod.lint_book(book_dir)
    except (Exception, SystemExit) as exc:  # 린터의 사고가 게이트 전체를 죽이지 않게 한다.
        # SystemExit은 BaseException 계열이라 `except Exception`만으로는 못 잡는다 —
        # 린터가 `sys.exit(...)`으로 죽으면 이 함수를 그대로 빠져나가 qc_gate.py 프로세스
        # 전체가 죽었고, 그 시점에 gate-report.json이 갱신되지 않아 **직전 실행의 낡은
        # PASS 리포트가 디스크에 그대로 남았다**(W4 재판정 E1). KeyboardInterrupt는
        # BaseException 계열이지만 여기 안 넣는다 — 사용자 중단은 강등하지 않고 전파한다.
        res["warns"].append(f"린터 실행 실패({type(exc).__name__}: {exc}) — 이 축은 미판정. "
                            f"직접 실행: python3 {lint_py} {book_dir}")
        return res
    if r.get("skipped"):
        res["skipped"] = r["skipped"]
        return res
    res["pairs"], res["entries"] = r.get("pairs"), r.get("entries")
    for x in r.get("findings", []):
        line = f"[{x['code']}] {x['msg']}"
        if x["level"] == "FAIL" and x["code"] in LINT_HARD_CODES:
            res["problems"].append(line)
        else:
            res["warns"].append(f"({x['level']}) {line}")
    res["ok"] = not res["problems"]
    return res


def collide_exempt_pages(fullbleed, overlap_ok, ch_starts, first_ch):
    """G3-COLLIDE 면제 면 집합. **도비라·앞부속은 어떤 경우에도 빠진다.**

    면제는 새 집합을 만들지 않고 기존 것을 재사용한다:
      · `fullbleed`(imgarea|vecarea ≥ 0.60) — 전면 도판 위 활자 배치는 조판 문법이다
      · `OVERLAP_APPROVED` — 기계 판정 불가한 정당한 겹침에 이름을 준다(INV-3)
    거기서 도비라(`ch_starts`)와 앞부속(`range(1, first_ch)`)을 뺀다. 뮤테이션 스위트가
    이 함수를 직접 호출해 차감을 회귀로 고정한다(M9c)."""
    return ((set(fullbleed) | set(overlap_ok)) - set(ch_starts)
            - set(range(1, first_ch)))


def g3_collide_page(recs):
    """같은 밴드 안 라인 쌍의 박스 교차 — fo2text와 같은 임계(위 상수 주석)."""
    hits = []
    for i in range(len(recs)):
        for j in range(i + 1, len(recs)):
            a, b = recs[i], recs[j]
            if not (a["band"] == b["band"] or a["band"] == -1 or b["band"] == -1):
                continue
            ax0, ay0, ax1, ay1 = a["box"]
            bx0, by0, bx1, by1 = b["box"]
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox <= COLLIDE_OX_PT or oy <= 0:
                continue
            if oy > COLLIDE_OY_FRAC * min(ay1 - ay0, by1 - by0):
                hits.append({"ox": round(ox, 2), "oy": round(oy, 2),
                             "a": a["text"][:24], "b": b["text"][:24],
                             "box_a": [round(v, 1) for v in a["box"]],
                             "box_b": [round(v, 1) for v in b["box"]]})
    return hits


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python3 scripts/qc_gate.py <book_dir> [--strict-pages]")
    book_dir = Path(sys.argv[1]).resolve()
    # 크래시 안전판(W4 재판정 E1): main() 진입 시 이전 실행의 gate-report.json을 무조건
    # 지운다. 이 시점 이후 어떤 코드 경로가 잡히지 않은 예외로 죽더라도(린터의 SystemExit
    # 포함, 또는 이 함수 자체의 다른 미래 실수) 디스크에는 "직전 실행의 낡은 PASS"가 남을
    # 수 없다 — 크래시 후에는 gate-report.json이 아예 없거나 이번 실행이 끝까지 써낸 값뿐이다.
    stale_report = book_dir / "gate-report.json"
    if stale_report.exists():
        stale_report.unlink()
    book = json.loads((book_dir / "book.json").read_text(encoding="utf-8"))
    outline = json.loads((book_dir / "outline.json").read_text(encoding="utf-8"))
    style = book["style"]
    tokens = json.loads((SKILL / "styles" / style / "tokens.json").read_text(encoding="utf-8"))
    # metrics는 조기 실패에서도 항상 존재 (소비자가 키 존재를 가정할 수 있게)
    report = {"gates": {}, "warns": [], "pass": False, "metrics": {}}
    fails = []

    # ---- G16-TOKENS (기록만 — 중단은 build.py 몫) ----
    # build.py가 이미 같은 순수 함수로 렌더 전에 판정하고 die()했다. 여기서는 리포트
    # 일관성을 위해 재호출해 등록만 한다 — FAIL이어도 fails에 넣지 않으므로 qc_gate의
    # 중단 지점 수는 늘지 않는다(pagination.md 게이트 표의 중단 지점 계수가 유효).
    _css = SKILL / "styles" / style / "theme.css"
    for _axis, _fs in g16_tokens.run(
            style, tokens, _css.read_text(encoding="utf-8") if _css.exists() else None,
            book.get("brand"), SKILL / "styles" / style).items():
        _probs = [f["msg"] for f in _fs if f["level"] == "FAIL"]
        report["gates"][_axis] = {
            "problems": _probs,
            "warns": [f["msg"] for f in _fs if f["level"] == "WARN"],
            "ok": not _probs,
            "enforced_by": "build.py",
        }
        # 여기 FAIL이 남아 있다는 건 build.py가 --g16-warn-only로 강등됐다는 뜻이다
        # (아니면 빌드가 die()해서 이 지점에 못 온다). 탈출구 사용 흔적이 gates 블록
        # 안에만 있으면 report만 보는 하류 소비자가 놓치므로 warns에도 한 줄씩 싣는다.
        # fails에는 여전히 넣지 않는다 — 중단 지점은 build.py 단일이라는 설계 불변.
        for _p in _probs:
            report["warns"].append(f"{_axis} FAIL(build.py --g16-warn-only로 강등됨): {_p}")

    # ---- G10 (렌더 전 — 날조는 빌드보다 먼저 잡는다) ----
    g10 = g10_quote_check(book_dir, outline)
    report["gates"]["G10"] = {"problems": g10, "ok": not g10}
    if g10:
        finish(book_dir, report, ["G10: " + p for p in g10])

    # ---- G0 (렌더 전 — 도해 SVG 소스: usvg의 조용한 드롭은 빌드보다 먼저 잡는다) ----
    g0 = g0_svg_check(book_dir, outline)
    report["gates"]["G0"] = {"problems": g0, "ok": not g0}
    if g0:
        finish(book_dir, report, ["G0: " + p for p in g0])

    # ---- G15-PARA (렌더 전 — 단락 8행 초과는 원고 문제, 빌드보다 먼저 잡는다) ----
    g15p = g15_para_check(book_dir, outline, style)
    report["gates"]["G15-PARA"] = {"problems": g15p, "ok": not g15p}
    if g15p:
        finish(book_dir, report, ["G15-PARA: " + p for p in g15p])

    # ---- G16-LINT (contrast_contract ↔ theme.css·DOM 실물 대조) ----
    # G16-TOKENS(build.py)가 "선언된 페어의 대비"를 보는 축이라면 이 린터는 **그 선언
    # 목록 자체가 실물과 맞는가**를 본다. 위 세 개(G10·G0·G15-PARA)와 달리 즉시 종료하지
    # 않는다 — fails에 누적만 하므로 중단 지점 수가 늘지 않는다.
    g16l = g16_lint_check(book_dir, style)
    report["gates"]["G16-LINT"] = g16l
    report["warns"] += [f"G16-LINT: {w}" for w in g16l["warns"]]
    if g16l["skipped"]:
        report["warns"].append(f"G16-LINT: skip — {g16l['skipped']}")
    for p in g16l["problems"]:
        fails.append(f"G16-LINT: {p}")

    pdf = book_dir / "draft" / "book.pdf"

    # ---- G1 render + page count ----
    g1 = {"exists": pdf.exists()}
    if not pdf.exists():
        finish(book_dir, report, fails + ["G1: draft/book.pdf missing"])
    doc = fitz.open(pdf)
    n = doc.page_count
    lo, hi = tokens.get("length_pages", {}).get(book.get("length", "short"), [10, 400])
    in_range = lo <= n <= hi
    # trim_mm(tokens) ↔ PDF 물리 크기 대조 — 테마 하드코딩이 tokens와 어긋나면 즉시 검출
    trim = tokens.get("trim_mm")
    trim_ok = True
    if trim:
        pr = doc[0].rect
        w_mm, h_mm = pr.width * 25.4 / 72, pr.height * 25.4 / 72
        trim_ok = abs(w_mm - trim[0]) <= 0.5 and abs(h_mm - trim[1]) <= 0.5
        if not trim_ok:
            fails.append(f"G1: 판형 불일치 — PDF {w_mm:.1f}×{h_mm:.1f}mm vs tokens trim_mm {trim} "
                         "(테마 하드코딩과 tokens가 갈라짐)")
        g1["trim_mm_measured"] = [round(w_mm, 1), round(h_mm, 1)]
        g1["trim_mm_expected"] = list(trim)
    g1["trim_ok"] = trim_ok
    # ---- G1-SCALE 전역 축소/확대 (스케일 불변 게이트들의 사각지대) ----
    # 🚨 Chromium print는 조판 요소가 판면을 넘기면 **문서 전체**를 shrink-to-fit으로 축소한다
    #    (styles/insight/theme.css의 목차 주석이 경고하는 그 메커니즘). 실측 사고: 목차 24행이
    #    판면을 2.11mm 넘긴 책이 전권 0.804배로 축소돼 출하됐고 **기존 15개 게이트가 전부 통과**했다
    #    — body_size(:589)·reach·gap·pitch가 모두 문서 자신을 기준으로 하는 상대 지표이고, G1은
    #    판형만, G7-FRAME은 6pt 임계(실측 드리프트 2.7pt)라서다. 절대 급수를 선언값과 대조하는
    #    축이 없으면 이 사고 계열은 원리적으로 검출되지 않는다.
    # 축은 본문 pt 하나다 — 행송(pitch)은 선언값 대비 -1.4~-2% 편차가 정상 권에도 있어
    #    (insight 17.25 vs 17.5, magazine 15.00 vs 15.31 실측) 게이트 축으로 쓰면 오탐이 난다.
    # tokens에 body_pt가 없는 스타일 팩은 WARN으로 넘긴다 — 중단 지점을 늘리지 않는다
    #    (pagination.md의 "중단 지점" 불변식 유지).
    scale_ok = True
    decl_pt = tokens.get("body_pt")
    if decl_pt:
        meas, probs = g1_scale_check(doc, decl_pt)
        g1["body_pt_declared"] = decl_pt
        g1["body_pt_measured"] = meas
        if probs:
            fails.extend("G1-SCALE: " + p for p in probs)
            scale_ok = False
    else:
        report["warns"].append(
            f"G1-SCALE: tokens.json에 body_pt 미선언 — 전역 축소 검출 불가 (styles/{style}/tokens.json)")
    # INV-1(pagination.md): 목표 쪽수는 조판의 입력이 아니다 — 산출물 쪽수는 기본
    # WARN. 하드 FAIL은 --strict-pages 명시 opt-in에서만 (강제 채움/개면 유인 차단).
    # ok는 이 게이트가 fails에 넣은 모든 사유(판형 포함)를 반영해야 진단이 안 갈라진다.
    strict_pages = "--strict-pages" in sys.argv[2:]
    g1.update({"pages": n, "range": [lo, hi],
               "ok": trim_ok and scale_ok and (in_range or not strict_pages),
               "strict": strict_pages})
    report["gates"]["G1"] = g1
    if not in_range:
        msg = f"G1: page count {n} outside [{lo},{hi}]"
        if strict_pages:
            fails.append(msg)
        else:
            report["warns"].append(msg + " (WARN — 쪽수는 조판을 압박하지 않는다, INV-1)")

    # ---- G2 font embedding ----
    # Type3 = Chromium이 글리프를 외부 폰트 없이 페이지별 벡터로 그린 것. 실측된 유입
    # 경로는 두 갈래다: ① CFF(.otf) @font-face(서브셋 실패), ② <img src=*.svg> 안의
    # <text>(SVG-as-image 모드는 문서 @font-face를 차단해 폴백 폰트로 렌더 — w7-b3:
    # magazine $tocmap이 도해 SVG를 썸네일로 참조하던 경로가 이것이었다).
    # 어느 쪽이든 텍스트 추출·검색·접근성이 깨진 상태이므로 FAIL.
    # 대응: ①은 TTF로 교체(scripts/convert_fonts.py), ②는 SVG 인라인 또는 래스터 참조.
    not_embedded = set()
    type3_pages = []
    for pno in range(n):
        for f in doc.get_page_fonts(pno, full=True):
            xref, ext, ftype, basefont = f[0], f[1], f[2], f[3]
            if ftype == "Type3":
                type3_pages.append(pno + 1)
                continue
            if ext in ("n/a", ""):
                extracted = doc.extract_font(xref)
                if not extracted or not extracted[-1]:
                    not_embedded.add(basefont)
    type3_pages = sorted(set(type3_pages))
    report["gates"]["G2"] = {"not_embedded": sorted(not_embedded),
                             "type3_pages": type3_pages,
                             "ok": not not_embedded and not type3_pages}
    if not_embedded:
        fails.append(f"G2: fonts not embedded: {sorted(not_embedded)}")
    if type3_pages:
        fails.append(f"G2: Type3 글리프 페이지 {type3_pages[:8]}{'…' if len(type3_pages) > 8 else ''} "
                     f"— 원인 후보: CFF(.otf) @font-face(→ TTF 교체, convert_fonts.py) 또는 "
                     f"<img src=*.svg> 안의 <text>(→ SVG 인라인 또는 래스터 참조)")

    # ---- G3-OVERFLOW / G3-COLLIDE 수집 ----
    # 같은 루프에서 `get_text("dict")` 1회 호출을 공유한다. 겹침의 **면제**는 구조 파생
    # 집합(fullbleed)과 pageroles가 확정된 뒤에야 걸 수 있으므로 여기서는 원시 교차만
    # 모으고, 등록은 G11 뒤에서 한다(G7-FRAME 선례로 별도 축 등록).
    # OVERFLOW 판정은 classify_bbox 경유 — PyMuPDF가 역전 bbox(x0>x1·y0>y1)를 반환하면
    # 정규화 없는 clip.contains가 오탐하므로 정규화 뒤 판정한다. 좌표 불능(NaN·inf·
    # 타입 오류)은 침묵 통과 대신 invalid로 하드 FAIL, 0면적은 진단 카운트만(#4).
    g3acc = g3_new_acc()
    collide_raw = {}    # page -> [hit, ...]  면제 적용 전
    line_recs = {}      # page -> [rec, ...]  G3-FIT이 재사용(get_text 재호출 금지)
    page_size = {}      # page -> (w, h) pt   doc.close() 후에도 프레임을 계산하려면 필요
    _frame_mm = tokens.get("body_frame_mm")
    for pno in range(n):
        page = doc[pno]
        pr = page.rect
        page_size[pno + 1] = (pr.width, pr.height)
        clip = fitz.Rect(pr.x0 - TOL, pr.y0 - TOL, pr.x1 + TOL, pr.y1 + TOL)
        blocks = page.get_text("dict").get("blocks", [])
        g3_scan_page(pno, clip, blocks, g3acc)
        recs = line_records(blocks, _column_bands(style, _frame_mm, pr))
        line_recs[pno + 1] = recs
        hits = g3_collide_page(recs)
        if hits:
            collide_raw[pno + 1] = hits
    g3 = g3_report(g3acc)
    report["gates"]["G3-OVERFLOW"] = g3
    if g3["count"]:
        fails.append(f"G3-OVERFLOW: {g3['count']} bbox overflow(s), "
                     f"first on page {g3['overflows'][0]['page']}")
    if g3["invalid_count"]:
        fails.append(f"G3-OVERFLOW: {g3['invalid_count']} invalid bbox(es), "
                     f"first on page {g3['invalid_bboxes'][0]['page']}")

    # ---- G4 TOC / bookmarks ----
    toc_entries = doc.get_toc(simple=True)
    lvl1 = [(t.strip(), p) for (l, t, p) in toc_entries if l == 1]
    lvl2 = [(t.strip(), p) for (l, t, p) in toc_entries if l == 2]
    g4 = {"bookmarks": len(lvl1), "bookmarks_lvl2": len(lvl2), "mismatches": [], "ok": True}
    want = [ch["title"].strip() for ch in outline["chapters"]]
    # 레벨 2(절) 북마크. 두 축을 본다.
    #  ㉠ 수 대조: 기대값은 빌더가 발행한 절 마커 수(typeset/tocplan.json). 이 축은 항등식에
    #     가까워(적대검토 D5) set_toc/saveIncr의 북마크 소실과 파일 변조만 잡는다.
    #  ㉡ **대상 면 대조**: 각 절 북마크가 가리키는 면에 그 절 제목이 실재하는가. 레벨 1엔
    #     이미 있던 대조가 레벨 2엔 없어서, 마커 오배정(D3/V1)이 개수만 맞으면 통과했다.
    plan_p = book_dir / "typeset" / "tocplan.json"
    plan = None       # G14-E(차례 쪽번호 축)도 소비 — 아래 g14_run에 tocplan으로 전달
    if plan_p.exists():
        plan = json.loads(plan_p.read_text(encoding="utf-8"))
        g4["sections_declared"] = plan.get("section_markers")
        g4["toc_pages"] = plan.get("toc_pages")
        g4["replanned"] = plan.get("replanned")
        g4["measured_bottom_mm"] = plan.get("measured_bottom_mm")
        for w in plan.get("warnings", []):
            report["warns"].append("build: " + w)
        if plan.get("section_markers") != len(lvl2):
            g4["ok"] = False
            g4["mismatches"].append(
                f"레벨 2 북마크 {len(lvl2)} != 발행 절 마커 {plan.get('section_markers')} "
                f"(toc_levels={plan.get('toc_levels')})")
    elif tokens.get("engine") == "html":
        # 계획 파일 부재는 그 자체가 실패다 — 구 구현은 WARN으로 강등해 HARD 축을 통째로
        # 껐고, 스테일 산출물에 qc_gate만 재실행하면 조용히 통과했다.
        g4["ok"] = False
        g4["mismatches"].append(
            "typeset/tocplan.json 부재 — html 엔진 빌드는 이 파일을 반드시 남긴다"
            "(구 빌드 산출물이면 현행 코드로 재빌드할 것)")
    lvl2_bad = []
    for title, page in lvl2:
        if page < 1 or page > n:
            lvl2_bad.append(f"절 '{title[:16]}' -> bad page {page}")
        elif norm(title) not in norm(doc[page - 1].get_text()):
            lvl2_bad.append(f"절 '{title[:16]}'이 북마크 대상 면 {page}에 없음")
    if lvl2_bad:
        g4["ok"] = False
        g4["mismatches"] += lvl2_bad[:5]
    if len(lvl1) < len(want):
        g4["ok"] = False
        g4["mismatches"].append(f"bookmark count {len(lvl1)} < chapters {len(want)}")
    else:
        for title, page in lvl1:
            if page < 1 or page > n:
                g4["ok"] = False
                g4["mismatches"].append(f"'{title}' -> bad page {page}")
            else:
                text = doc[page - 1].get_text()
                if norm(title) not in norm(text):
                    g4["ok"] = False
                    g4["mismatches"].append(f"'{title}' not found on its page {page}")
    report["gates"]["G4"] = g4
    if not g4["ok"]:
        fails.append("G4: " + "; ".join(g4["mismatches"][:3]))

    page_texts = [doc[i].get_text() for i in range(n)]
    doc.close()

    # ---- G13 figtext (도해 라벨의 PDF 실텍스트 실재 — G11 anchor와 동일 패턴) ----
    g13 = g13_figtext_check(book_dir, outline, page_texts)
    report["gates"]["G13"] = {"problems": g13, "ok": not g13}
    if g13:
        fails.append("G13: " + "; ".join(g13[:3]) + (f" 외 {len(g13)-3}건" if len(g13) > 3 else ""))

    # ---- 밀도 전처리 (pagination.md §7) ----
    frame_mm = tokens.get("body_frame_mm")
    if not frame_mm:
        finish(book_dir, report, fails + [f"G7: styles/{style}/tokens.json에 body_frame_mm 없음"])
    m = analyze(pdf, frame_mm)
    pages = m["pages"]
    N = m["n_grid"] or 1

    ch_starts = sorted({p for (_, p) in lvl1 if 1 <= p <= n})
    first_ch = ch_starts[0] if ch_starts else 1
    if not ch_starts:
        # 북마크·장 마커가 0건이면 first_ch가 조용히 1로 폴백하고, range(1, first_ch)가
        # 빈 집합이 되어 앞부속 보호가 통째로 정지한다: G3-COLLIDE의 앞부속 차감
        # (collide_exempt_pages)과 G3-FIT의 검사 대상(front_pages)이 둘 다 비게 된다
        # (W4 재판정 E3). 같은 원인으로 G4(북마크 정합)가 별도로 FAIL해 단독 우회는
        # 성립하지 않지만, 이 축들이 왜 침묵했는지는 리포트에 남겨야 한다.
        report["warns"].append(
            "앞부속 보호 정지: 북마크(장 마커) 0건 → first_ch=1 폴백 → "
            "G3-COLLIDE 앞부속 면제 차감과 G3-FIT 검사 대상이 둘 다 빈 집합. "
            "(같은 원인으로 G4가 별도 FAIL한다)")

    # ---- G17-FIGFIT (도해 면 분단·판면 초과 — W7 신설, 렌더 fit 판정의 지면 이중 방어) ----
    g17 = g17_figfit_check(book_dir, outline, page_texts, line_recs, page_size,
                           tokens, first_ch)
    report["gates"]["G17-FIGFIT"] = {"problems": g17, "ok": not g17}
    if g17:
        fails.append("G17-FIGFIT: " + "; ".join(g17[:3])
                     + (f" 외 {len(g17) - 3}건" if len(g17) > 3 else ""))

    # ---- G14 목차·디자인 정합 (tocgate.py) ----
    from tocgate import run as g14_run
    g14_doc = fitz.open(pdf)  # 본 doc은 page_texts 추출 후 닫혔음
    g14 = g14_run(g14_doc, outline, ch_starts, book, tokens, tocplan=plan)
    g14_doc.close()
    report["gates"]["G14-A"] = g14["A"]
    report["gates"]["G14-B"] = g14["B"]
    report["gates"]["G14-C"] = g14["C"]
    report["gates"]["G14-D"] = g14["D"]
    report["gates"]["G14-E"] = g14["E"]
    for axis in ("A", "B", "C", "D", "E"):
        for p in g14[axis]["problems"]:
            fails.append(f"G14-{axis}: {p}")
    report["warns"] += g14["D"].get("warns", []) + g14["E"].get("warns", [])
    colophon_pages = {i + 1 for i, t in enumerate(page_texts)
                      if "bookforge" in t and "조판" in t and i + 1 >= (ch_starts[-1] if ch_starts else 1)}
    fullbleed = {p["page"] for p in pages
                 if p["imgarea"] >= 0.60 or p.get("vecarea", 0) >= 0.60}
    # float 밀림 면제(구조 파생): 다음 면 첫 블록(통짜 표·그림)이 이 면 잔여 공간보다 크면
    # 이 면의 미달은 결속 규칙의 정당한 대가다 — 중간면 판정에서 제외.
    float_pushed = set()
    pitch_ref = m["book_pitch"] or 12
    for i, p in enumerate(pages[:-1]):
        nxt = pages[i + 1]
        fl, ft, fr, fb = nxt["frame"]
        # 텍스트는 나눠 흐를 수 있으므로 면제 사유가 못 된다 — 객체(표 괘선·그림·박스)만 본다.
        segs = sorted(nxt["_objs"])
        if not segs or segs[0][0] > ft + 2 * pitch_ref:
            continue  # 다음 면이 객체로 시작하지 않으면 밀림이 아니다
        top0, cur1 = segs[0]
        for a, b in segs[1:]:
            if a - cur1 > pitch_ref * 3:  # 표는 모든 행에 괘선이 있지 않다 — 행 건너뜀 허용
                break
            cur1 = max(cur1, b)
        first_block_h = cur1 - top0
        remaining = (1 - p["reach"]) * (p["frame"][3] - p["frame"][1])
        # 블록은 CSS/Typst 마진을 데리고 다닌다 — 3행송 슬랙 인정
        if first_block_h + pitch_ref * 3 > remaining:
            float_pushed.add(p["page"])
    body_last = max((p["page"] for p in pages
                     if p["lines"] > 0 and p["page"] not in colophon_pages), default=n)
    # 마지막 본문 면은 구조 파생 면제(pagination.md §7 — 책의 끝은 자연 꼬리)
    tails = {p - 1 for p in ch_starts if p - 1 >= first_ch}
    structural = (set(range(1, first_ch)) | set(ch_starts) | colophon_pages | fullbleed
                  | {body_last})  # 마지막 본문 면 면제 (pagination.md §7)

    # ---- G15-RHYTHM 시각 요소 없는 연속 본문 면 (스타일별 상한) ----
    g15r = g15_drought_check(pages, page_texts, first_ch, structural, style)
    report["gates"]["G15-RHYTHM"] = {"problems": g15r, "ok": not g15r}
    if g15r:
        fails.append("G15-RHYTHM: " + "; ".join(g15r[:3]))

    # ---- G11 pageroles.json ----
    roles_p = book_dir / "pageroles.json"
    roles = []
    g11 = {"declared": 0, "problems": [], "ok": True}
    if roles_p.exists():
        roles = json.loads(roles_p.read_text(encoding="utf-8")).get("roles", [])
        g11["declared"] = len(roles)
        budget = max(3, int(0.08 * n))
        if len(roles) > budget:
            g11["problems"].append(f"선언 면 {len(roles)} > 예산 {budget}")
        breaths = 0
        for r in roles:
            pg, code = r.get("page"), r.get("code")
            why, anchor = (r.get("why") or "").strip(), r.get("anchor")
            pm = next((p for p in pages if p["page"] == pg), None)
            if code not in ROLE_CODES:
                g11["problems"].append(f"p{pg}: 코드 '{code}' 화이트리스트 밖"); continue
            if not why:
                g11["problems"].append(f"p{pg}: why 비어 있음")
            if pm is None or not (1 <= pg <= n):
                g11["problems"].append(f"p{pg}: 존재하지 않는 면"); continue
            # 기계 선행조건 — 불충족 시 코드 자체가 FAIL (도장 방지)
            if code == "FULL_BLEED_PLATE" and pm["imgarea"] < 0.60:
                g11["problems"].append(f"p{pg}: FULL_BLEED_PLATE인데 imgarea {pm['imgarea']} < 0.60")
            if code == "PART_DIVIDER" and pm["lines"] > 3:
                g11["problems"].append(f"p{pg}: PART_DIVIDER인데 텍스트 {pm['lines']}행 > 3")
            if code == "EXEC_SUMMARY":
                if style != "business" or not (0.35 <= pm["ink"] <= 0.70):
                    g11["problems"].append(f"p{pg}: EXEC_SUMMARY 선행조건 위반 (style={style}, ink={pm['ink']})")
            if code == "ESSAY_BREATH":
                breaths += 1
                if style != "essay" or pg not in tails or pm["lines"] < 6:
                    g11["problems"].append(f"p{pg}: ESSAY_BREATH 선행조건 위반 (꼬리 면·6행 이상·essay 한정)")
            if code == "MAGAZINE_WHITESPACE" and style != "magazine":
                g11["problems"].append(f"p{pg}: MAGAZINE_WHITESPACE는 magazine 한정")
            if code == "TOC_TAIL" and pg >= first_ch:
                g11["problems"].append(f"p{pg}: TOC_TAIL은 본문 시작 전 한정")
            if code == "OVERLAP_APPROVED":
                # 도비라·앞부속은 어떤 경우에도 면제하지 않는다 — 이번 사이클의 원 사고
                # (목차 넘침이 도비라 면으로 흘러 기존 행과 겹친 채 출하)의 **발생 지점과
                # 착지 지점**이 정확히 그 둘이다. 계약 문장(pagination.md)이 원래 그렇게
                # 적혀 있었고 코드만 도비라를 뺐다 — 코드를 문장에 맞춘다(W4 판정 D2).
                if pg in ch_starts:
                    g11["problems"].append(
                        f"p{pg}: OVERLAP_APPROVED는 도비라(장 오프너)에 쓸 수 없다 "
                        "— 목차↔도비라 겹침 사고 계열이 통째로 면제된다")
                elif pg < first_ch:
                    g11["problems"].append(
                        f"p{pg}: OVERLAP_APPROVED는 앞부속(표지·목차·판권, 1~{first_ch - 1}면)에 "
                        "쓸 수 없다 — 표지는 G14-C가 원리적으로 스캔하지 않는 유일한 면이고"
                        "(tocgate.py: `range(1, page_count)`), 목차는 넘침 사고의 발생 면이다")
                elif pg not in collide_raw:
                    g11["problems"].append(
                        f"p{pg}: OVERLAP_APPROVED인데 그 면에 교차 라인이 실재하지 않는다 (도장 방지)")
                else:
                    # 면제는 **면 단위**다(교차 1건을 지목하지 못한다). 그래서 사소한 교차
                    # 하나로 선행조건을 제조한 뒤 같은 면의 중대한 겹침까지 함께 면제하는
                    # 경로가 열려 있었다(W4 판정 D5 — 실측: 장식 불릿 ox 2.02pt로 승인을
                    # 정당화하고 본문 행 통째 겹침 ox 38.85pt를 함께 통과시킴).
                    # 폭발 반경을 기계 상한 둘로 묶는다:
                    #  ㉢ 크기 — 승인 면의 **모든** 교차가 검출 임계의 2배(ox <= 3.0pt ≈ 1mm)
                    #    이내여야 한다. 이 코드가 존재하는 사유(장식 글리프가 행 끝에
                    #    머리카락만큼 물리는 정당한 조판)는 전부 이 대역 안이고, 그보다 큰
                    #    교차는 "설명 가능한 조판"이 아니라 결함이다.
                    #  ㉣ 건수 — 개별 크기가 ㉢ 이내라도 건수가 쌓이면 폭발 반경이 넓어진다
                    #    (W4 재판정 R-2 — ox 2.9pt 교차 20건을 사유서 1줄로 승인해 통과시킴).
                    #    사소한 물림의 현실 범위는 면당 2~3건이고, 그 이상은 개별 크기가
                    #    작아도 조판 붕괴다.
                    big = [h for h in collide_raw[pg] if h["ox"] > OVERLAP_APPROVE_MAX_OX_PT]
                    if big:
                        h0 = big[0]
                        g11["problems"].append(
                            f"p{pg}: OVERLAP_APPROVED 면에 상한 초과 교차 {len(big)}건 — "
                            f"'{h0['a']}' ↔ '{h0['b']}' (ox {h0['ox']}pt > "
                            f"{OVERLAP_APPROVE_MAX_OX_PT}pt = 검출 임계 {COLLIDE_OX_PT}pt의 2배). "
                            "면 단위 면제라 사유서에 없는 겹침까지 함께 열리므로, 이 크기의 "
                            "겹침은 승인 대상이 아니라 수리 대상이다")
                    n_ovl = len(collide_raw[pg])
                    if n_ovl > OVERLAP_APPROVE_MAX_COUNT:
                        g11["problems"].append(
                            f"p{pg}: OVERLAP_APPROVED 면에 교차 {n_ovl}건 > 상한 "
                            f"{OVERLAP_APPROVE_MAX_COUNT}건 — 개별 크기가 ㉢ 이내라도 이 건수는 "
                            "사소한 물림의 현실 범위(면당 2~3건)를 넘는 조판 붕괴다(W4 재판정 R-2)")
            if code == "CH_CLOSE_APPROVED" and pg not in tails:
                g11["problems"].append(f"p{pg}: CH_CLOSE_APPROVED는 장 끝 면 한정 "
                                       "(레버 소진 후 최종 에스컬레이션)")
            if anchor:
                if norm(anchor) not in norm(page_texts[pg - 1]):
                    g11["problems"].append(f"p{pg}: anchor 불일치(stale — 리빌드로 면 밀림 의심)")
            elif code not in ("FULL_BLEED_PLATE", "PART_DIVIDER"):
                g11["problems"].append(f"p{pg}: anchor 필수(텍스트 면)")
        if breaths > max(1, len(ch_starts)):
            g11["problems"].append(f"ESSAY_BREATH {breaths}회 > 장당 1회 한도")
    g11["ok"] = not g11["problems"]
    report["gates"]["G11"] = g11
    if not g11["ok"]:
        fails.append("G11: " + "; ".join(g11["problems"][:3]))
    role_by_page = {r.get("page"): r.get("code") for r in roles}

    # ---- G3-COLLIDE 면제 적용·등록 ----
    # 면제는 **새 집합을 만들지 않고** 기존 것을 재사용한다.
    #  · `fullbleed`(imgarea|vecarea ≥ 0.60) — 전면 도판 위 활자 배치는 조판 문법이지 겹침이 아니다
    #  · `role_by_page`의 `OVERLAP_APPROVED` — 기계 판정 불가한 정당한 겹침에 이름을 준다(INV-3)
    # `structural`의 나머지 성분(판권·마지막 본문 면)과 도비라·앞부속은 **면제하지 않는다**:
    # 밀도(비움) 면제와 겹침 면제는 다른 관심사이고, 앞부속·도비라를 면제하면 이번 사이클의
    # 원 사고(목차 넘침 → 도비라 겹침)가 발생 지점에서 통째로 열린다.
    #
    # 🚨 앞부속 차감은 **fullbleed 자동 면제에도** 걸린다. 표지는 imgarea 1.0인 전면
    # 도판이라 fullbleed 집합에 자동으로 들어가는데(실측: magazine-trend-brief p1),
    # 동시에 **G14-C가 원리적으로 스캔하지 않는 유일한 면**이다(tocgate.py의 대비 루프가
    # `range(1, page_count)`로 표지를 건너뛴다 — 아트 배경 때문). 즉 표지에서 제목 위에
    # 다른 행이 통째로 얹혀도 사람 판단 0·사유 코드 0으로 전 게이트를 통과했다(W4 판정 D2).
    # 계약 문장(pagination.md 「도비라·앞부속은 어떤 경우에도 면제하지 않는다」)이 옳았고
    # 코드가 `ch_starts`만 뺐다 — 코드를 문장에 맞춘다.
    overlap_ok = {pg for pg, c in role_by_page.items() if c == "OVERLAP_APPROVED"}
    collide_exempt = collide_exempt_pages(fullbleed, overlap_ok, ch_starts, first_ch)
    collisions = [dict(page=pg, **h) for pg in sorted(collide_raw)
                  if pg not in collide_exempt for h in collide_raw[pg]]
    report["gates"]["G3-COLLIDE"] = {
        "collisions": collisions[:20], "count": len(collisions),
        "exempt_pages": sorted(collide_exempt & set(collide_raw)),
        "ok": not collisions}
    if collisions:
        f0 = collisions[0]
        fails.append(f"G3-COLLIDE: 텍스트 라인 교차 {len(collisions)}건, 첫 건 p{f0['page']} "
                     f"'{f0['a']}' ↔ '{f0['b']}' (ox {f0['ox']}pt · oy {f0['oy']}pt) "
                     "— 넘친 요소를 줄이거나 배치를 고칠 것(정당한 겹침이면 pageroles.json "
                     "OVERLAP_APPROVED, 단 도비라는 불가)")

    # ---- G3-FIT 앞부속 프레임 적합 ----
    # 대상은 앞부속 `range(1, first_ch)`. 표지·목차면은 `body_frame_mm`이 아니라 자체
    # padding을 쓰므로(styles/*/theme.css) body_frame을 들이대면 전량 FAIL한다 — tokens에
    # `front_frame_mm`이 선언된 스타일에서만 프레임 축을 돌리고, 미선언 스타일은 WARN으로
    # 남긴다(오탐 0이 합격선). **양성 조건**(앞부속 면은 텍스트 ≥1행 또는 선언된 역할)은
    # 선언 유무와 무관하게 항상 돈다 — 빈 면이 구조적 면제에 삼켜지는 구멍을 봉쇄한다.
    # 라인은 G3 루프가 이미 모은 `line_recs`를 재사용한다(pagemetrics도 get_text 재호출 없음).
    front_pages = list(range(1, first_ch))
    front_frame = tokens.get("front_frame_mm")
    g3fit = {"problems": [], "front_pages": front_pages, "declared": bool(front_frame),
             "ok": True}
    for pg in front_pages:
        if not line_recs.get(pg) and pg not in role_by_page:
            g3fit["problems"].append(
                f"p{pg}: 앞부속인데 텍스트 0행이고 pageroles 선언도 없다 "
                "— 빈 면이 구조적 면제에 삼켜져 전 게이트를 통과하는 구멍")
    if front_frame:
        # 선언값의 **형식·물리 타당성**은 G16-SYNC가 렌더 전에 판정한다
        # (g16_tokens.front_frame_findings — 4원소 수치·비음수·프레임<판형·객체형 두 키).
        # 여기서는 그 선언이 이 책에서 **실제로 축으로 작동했는가**만 본다: 선언은 있는데
        # 검사한 면이 0이거나 프레임이 지면과 사실상 같으면 축이 조용히 항등이 된 것이고,
        # 그 상태가 리포트에서 "declared:true · 결함 0"으로만 보이면 위조가 미선언보다
        # 조용해진다(W4 판정 D3).
        checked = 0
        trim_mm = tokens.get("trim_mm")
        for pg in front_pages:
            fr_mm = front_frame_for(front_frame, pg)
            if not fr_mm:
                continue
            checked += 1
            ratio = g16_tokens.front_frame_area_ratio(fr_mm, trim_mm)
            if ratio is not None and ratio >= g16_tokens.FRONT_FRAME_AREA_WARN:
                report["warns"].append(
                    f"G3-FIT: p{pg} 선언 프레임 {fr_mm}가 지면의 {ratio:.1%} — 봉투가 판형과 "
                    f"사실상 같아 이 면의 프레임 축은 항등이다(축 무력화 의심)")
            top, right, bottom, left = fr_mm
            pw, ph = page_size[pg]
            box = fitz.Rect(left * MM2PT - TOL, top * MM2PT - TOL,
                            pw - right * MM2PT + TOL, ph - bottom * MM2PT + TOL)
            for rec in line_recs.get(pg, []):
                if not box.contains(fitz.Rect(rec["raw"])):
                    g3fit["problems"].append(
                        f"p{pg}: 앞부속 텍스트가 선언 프레임 밖 — '{rec['text'][:20]}' "
                        f"bbox {[round(v, 1) for v in rec['raw']]} "
                        f"vs front_frame {[round(v, 1) for v in box]}")
        g3fit["checked_pages"] = checked
        if front_pages and not checked:
            report["warns"].append(
                f"G3-FIT: styles/{style}/tokens.json에 front_frame_mm 선언은 있으나 "
                f"검사한 앞부속 면이 0개다(앞부속 {front_pages}) — 선언 형태가 이 책의 면에 "
                f"적용되지 않는다(객체형 키 누락·null 등). 축이 조용히 꺼진 상태다")
    else:
        report["warns"].append(
            f"G3-FIT: styles/{style}/tokens.json에 front_frame_mm 미선언 — 앞부속 프레임 축 생략"
            "(표지·목차의 자체 padding 계약이 확보되지 않은 스타일). 양성 조건만 검사함")
    g3fit["ok"] = not g3fit["problems"]
    g3fit["problems"] = g3fit["problems"][:20]
    report["gates"]["G3-FIT"] = g3fit
    if not g3fit["ok"]:
        fails.append("G3-FIT: " + "; ".join(g3fit["problems"][:3]))

    # ---- G7-FRAME 판면 드리프트 ----
    ft_pt = frame_mm[0] * MM2PT
    d_top = m["derived_frame"][0]
    g7f = {"token_top_pt": round(ft_pt, 1), "derived_top_pt": d_top,
           "book_pitch": m["book_pitch"], "n_grid": N, "ok": True}
    if d_top is not None and abs(d_top - ft_pt) > 6:
        g7f["ok"] = False
        fails.append(f"G7-FRAME: tokens 판면 상단 {ft_pt:.1f}pt vs 실측 {d_top}pt — 드리프트 >6pt")
    report["gates"]["G7-FRAME"] = g7f

    # ---- G7-BLANK (구 G5 흡수) + G12 ----
    blanks, parity = [], []
    for p in pages:
        pg = p["page"]
        if p["ink"] >= 0.03 or pg in structural or pg in role_by_page:
            continue
        if pg + 1 in ch_starts:
            parity.append(pg)  # 장 시작 직전 필러 백면 — 인쇄 관습 이식
        else:
            blanks.append(pg)
    report["gates"]["G7-BLANK"] = {"blank_pages": blanks, "ok": not blanks}
    report["gates"]["G12"] = {"parity_filler": parity, "ok": not parity}
    if blanks:
        fails.append(f"G7-BLANK: 의도 없는 백면 {blanks}")
    if parity:
        fails.append(f"G12: 장 시작 직전 필러 백면 {parity} (단면 전자책에 recto 맞춤 금지)")

    # ---- G7-TAIL / G7-MID ----
    tail_hard = TAIL_HARD.get(style, 0.45)
    tail_warn = TAIL_WARN.get(style, 0.70)
    mid_role_min = MID_ROLE_MIN.get(style, 0.90)
    g7t = {"tails": [], "ok": True}
    g7m = {"underfull": [], "ok": True}
    tail_reaches = []
    for p in pages:
        pg = p["page"]
        if (pg < first_ch or pg in colophon_pages or pg in fullbleed or pg in ch_starts
                or pg == body_last):  # 마지막 본문 면 면제 (pagination.md §7)
            continue
        code = role_by_page.get(pg)
        if pg in tails:
            tail_reaches.append(p["reach"])
            entry = {"page": pg, "reach": p["reach"], "lines": p["lines"], "role": code}
            g7t["tails"].append(entry)
            if p["lines"] < 6:
                g7t["ok"] = False
                fails.append(f"G7-TAIL: p{pg} 꼬리 {p['lines']}행 < 6 (HARD — 사유 코드 불가)")
            elif p["reach"] < tail_hard:
                g7t["ok"] = False
                fails.append(f"G7-TAIL: p{pg} reach {p['reach']} < HARD {tail_hard}")
            elif p["reach"] < tail_warn and not code:
                if style in WARN_REPORT_ONLY:
                    report["warns"].append(f"G7-TAIL: p{pg} reach {p['reach']} < {tail_warn} (report-only)")
                else:
                    g7t["ok"] = False
                    fails.append(f"G7-TAIL: p{pg} reach {p['reach']} < {tail_warn}, 사유 코드 없음")
        else:
            if pg in float_pushed:
                report["warns"].append(f"G7-MID: p{pg} reach {p['reach']} — float 밀림 면제(다음 면 통짜 블록)")
                continue
            if p["reach"] < MID_HARD:
                g7m["underfull"].append({"page": pg, "reach": p["reach"]})
                g7m["ok"] = False
                fails.append(f"G7-MID: p{pg} reach {p['reach']} < {MID_HARD} (HARD)")
            elif p["reach"] < mid_role_min and not code:
                if style in WARN_REPORT_ONLY:
                    report["warns"].append(f"G7-MID: p{pg} reach {p['reach']} < {mid_role_min} (report-only)")
                else:
                    g7m["underfull"].append({"page": pg, "reach": p["reach"]})
                    g7m["ok"] = False
                    fails.append(f"G7-MID: p{pg} reach {p['reach']} < {mid_role_min}, 사유 코드 없음")
    report["gates"]["G7-TAIL"] = g7t
    report["gates"]["G7-MID"] = g7m

    # ---- G7-DOC 문서 통계 (실측 근거 있는 스타일만) ----
    if style in DOC_STATS_STYLES and tail_reaches:
        med = round(median(tail_reaches), 3)
        p10 = round(sorted(tail_reaches)[max(0, int(0.1 * len(tail_reaches)) - 0)], 3) \
            if len(tail_reaches) >= 3 else min(tail_reaches)
        ok = med >= 0.80 and p10 >= 0.55
        report["gates"]["G7-DOC"] = {"median": med, "p10": p10, "ok": ok}
        if not ok:
            fails.append(f"G7-DOC: 꼬리 reach 중앙값 {med}/p10 {p10} < 0.80/0.55 — 원고 분량 설계 반환")

    # 본문 크기 = 글자 수 가중 최빈값(행 수 기준이면 리스트·표 9pt가 본문 10.5pt를 이길 수 있다)
    sizes = Counter()
    for p in pages:
        for l in p["_lines"]:
            sizes[round(l["size"] * 2) / 2] += len(l["text"])
    body_size = sizes.most_common(1)[0][0] if sizes else 10.0

    # ---- G8-STRETCH 공기 채움 ----
    g8 = {"stretched": [], "ok": True}
    for p in pages:
        pg = p["page"]
        if pg < first_ch or pg in structural or pg in tails or pg in role_by_page \
                or pg in float_pushed:
            continue
        # insight는 H2 위 여백 24mm(STYLE.md 정본)+와이드 콜아웃이 구조적 공기를 만든다 — 임계 완화.
        # 한 면에 섹션 전환이 2회 이상이면 여백이 배로 쌓이므로 디스플레이 행 수 비례 가산.
        gap_thr = 0.18
        if style == "insight":
            heads = sum(1 for l in p["_lines"] if l["size"] >= 1.3 * body_size)
            gap_thr = 0.28 + 0.10 * max(0, heads - 1)
        elif style == "business":
            # 액션 타이틀(16pt + 전폭 룰 + 전후 v1.8/1.1em)과 키 스탯 디스플레이가
            # 면당 ~10mm(≈0.045)의 구조적 공기를 만든다(실측 — p13 홀 스캔). 디스플레이
            # 행 수에 비례해 가산, 디스플레이 없는 순본문 면은 0.18 그대로.
            heads = sum(1 for l in p["_lines"] if l["size"] >= 1.3 * body_size)
            gap_thr = 0.18 + 0.05 * heads
        if p["gap"] > gap_thr and p["lines"] < 0.8 * N:
            g8["stretched"].append({"page": pg, "gap": p["gap"], "lines": p["lines"]})
        # 행송 편차는 WARN만 — 두 엔진 모두 페이지 단위로 행송을 벌릴 능력이 없다(실측).
        # 리스트·코드·콜아웃 혼합 면의 자연 편차가 대부분이라 FAIL로 쓰면 오탐.
        if p["pitch"] and m["book_pitch"] and p["lines"] >= 10 and \
                abs(p["pitch"] - m["book_pitch"]) / m["book_pitch"] > 0.03:
            report["warns"].append(f"G8: p{pg} 행송 편차 {p['pitch']} vs {m['book_pitch']} (혼합 콘텐츠 추정)")
    g8["ok"] = not g8["stretched"]
    report["gates"]["G8"] = g8
    if g8["stretched"]:
        first = g8["stretched"][0]
        fails.append(f"G8-STRETCH: 공기 채움/행송 이탈 {len(g8['stretched'])}면, 첫 면 p{first['page']}")

    # ---- G9-KEEP 제목 고립·widow ----
    g9 = {"violations": [], "ok": True}
    single_col = style in ("practical", "academic", "essay", "business")
    for i, p in enumerate(pages):
        pg = p["page"]
        if pg < first_ch or pg in structural or not p["_lines"]:
            continue
        last = p["_lines"][-1]
        if last["size"] >= 1.3 * body_size and pg not in tails:  # 1.1~1.3 대역은 스탯 라벨·덱 오탐(폰트 판별은 백로그)
            g9["violations"].append(f"p{pg}: 면 끝 제목 고립('{last['text'][:20]}')")
        if single_col and i > 0 and pages[i - 1]["_lines"] and pg - 1 >= first_ch \
                and pg - 1 not in ch_starts:
            fl_, _, fr_, _ = p["frame"]
            first_l, prev_last = p["_lines"][0], pages[i - 1]["_lines"][-1]
            w = fr_ - fl_
            if abs(first_l["size"] - body_size) <= 0.5 and \
                    first_l["x1"] < fr_ - 0.15 * w and prev_last["x1"] >= fr_ - 0.05 * w and \
                    len(p["_lines"]) >= 2 and abs(p["_lines"][1]["size"] - body_size) <= 0.5 and \
                    p["_lines"][1]["y0"] - first_l["y0"] > (m["book_pitch"] or 12) * 1.5:
                g9["violations"].append(f"p{pg}: widow 의심(면 첫 행이 앞 문단 끝줄)")
    g9["ok"] = not g9["violations"]
    report["gates"]["G9"] = g9
    if g9["violations"]:
        fails.append("G9-KEEP: " + "; ".join(g9["violations"][:3]))

    # metrics 요약을 리포트에 (디버그·refit 입력)
    report["metrics"] = {"book_pitch": m["book_pitch"], "n_grid": N,
                         "pages": [{k: p[k] for k in ("page", "lines", "reach", "ink", "gap", "imgarea")}
                                   for p in pages],
                         "chapter_starts": ch_starts, "tails": sorted(tails),
                         "structural_exempt": sorted(structural)}

    if fails:
        finish(book_dir, report, fails)

    report["pass"] = True
    final_dir = book_dir / "final"
    final_dir.mkdir(exist_ok=True)
    dst = final_dir / f"{book_dir.name}.pdf"
    shutil.copy(pdf, dst)
    report["final"] = str(dst)
    (book_dir / "gate-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for w in report["warns"]:
        print("WARN", w)
    print(f"PASS -> {dst}")
    sys.exit(0)


def finish(book_dir, report, fails):
    report["fails"] = fails
    # FAIL이면 이전 회차의 final/을 무효화한다 — 게이트를 통과하지 못한 시점의
    # 스테일 PDF가 final/에 남아 "완료"로 오판되는 것을 차단 (SKILL.md의 final 계약).
    stale = book_dir / "final" / f"{book_dir.name}.pdf"
    if stale.exists():
        stale.unlink()
        print(f"FAIL -> 스테일 final 제거: {stale}", file=sys.stderr)
    (book_dir / "gate-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for w in report.get("warns", []):
        print("WARN", w, file=sys.stderr)
    for f in fails:
        print("FAIL", f, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
