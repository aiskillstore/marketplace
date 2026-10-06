// bookforge style: business — 비즈니스·컨설팅 리포트 (STYLE.md: 200×280, navy 시스템)
#import "base.typ": default-tokens, keep-words, numpad, chapter-state, full-bleed
#import "base.typ" as base
#let code-font = ((name: "DejaVu Sans Mono", covers: regex("[A-Za-z0-9]")), "Pretendard")

#let meta = json("meta.json")

#let navy-900 = rgb("#0A1E38")
#let navy-700 = rgb("#123A63")
#let navy-300 = rgb("#7FB2D9")  // 다크(navy) 배경 전용 — 흰 바탕 금지(대비 2.26)
#let navy-500 = rgb("#3378AD")  // 흰 바탕용 중간톤 (4.74:1)
#let navy-100 = rgb("#D8E4EF")
#let teal-600 = rgb("#0E6E62")
#let accent   = rgb(meta.at("brand", default: "#C2662E"))
#let alert-c  = rgb("#B3261E")
#let ink      = rgb("#1A1D21")
#let ink-60   = rgb("#5A6169")
#let ink-30   = rgb("#9AA5B1")
#let rule-c   = rgb("#D5D9DE")
#let paper-alt = rgb("#F4F6F8")

// content → 평문 (목차 Executive Summary 판별용)
#let plain-text(c) = {
  if type(c) == str { c }
  else if type(c) != content { "" }
  else if c.func() == text { c.text }
  else if c.has("children") { c.children.map(plain-text).join("") }
  else if c.has("body") { plain-text(c.body) }
  else if c.func() == smartquote { "'" }
  else { " " }
}

#let theme-tokens = default-tokens + (
  trim: (w: 200mm, h: 280mm),
  // 본문 5컬럼 132.5mm + 바깥 마진 컬럼 22.5mm(+거터 5mm) 확보
  margin: (top: 28mm, bottom: 30mm, left: 20mm, right: 47.5mm),
  brand: navy-700, brand-light: navy-100,
  ink: ink, muted: ink-60, paper: white,
  body-font: ("Pretendard",), sans-font: ("Pretendard",),
  display-font: ("Pretendard",),
  // 공식 TTF판의 내부 패밀리명은 "Gmarket Sans TTF" (OTF판 "Gmarket Sans"와 다름)
  stat-font: ("Gmarket Sans TTF", "Gmarket Sans"),
  quote-font: ("Noto Serif KR",),
  body-size: 10.5pt, body-leading: 0.62em,
)

#let TT = theme-tokens

// ---- cover: navy + vector data-mesh pattern (상단 40%) -----------------------
#let cover-pattern(w, h) = {
  // 결정론적 데이터 메시: 사선 + 노드
  for i in range(12) {
    let x = w * i / 11
    place(top + left, dx: x, dy: 0mm,
      line(end: (w * 0.35, h), stroke: 0.4pt + navy-500.transparentize(72%)))
  }
  for i in range(9) {
    let x = w * (i + 1) / 10
    let y = h * calc.rem(i * 37, 83) / 83
    place(top + left, dx: x, dy: y, circle(radius: 1.1mm, fill: navy-300.transparentize(55%)))
  }
}

#let make-cover(meta) = {
  page(margin: 0mm, header: none, footer: none, fill: navy-900, {
    set par(justify: false, first-line-indent: 0em)
    block(width: 100%, height: 40%, clip: true, cover-pattern(200mm, 112mm))
    place(top + left, dx: 20mm, dy: 20mm, rect(width: 24mm, height: 4mm, fill: accent))
    // 시리즈 라벨: 제목 블록 위 6mm
    place(top + left, dx: 20mm, dy: 114mm,
      text(fill: navy-300, font: TT.display-font, size: 8pt, tracking: 0.06em,
        upper(meta.at("series", default: "BOOKFORGE INSIGHT REPORT"))))
    // 제목 블록 상단 = 판면 상단(28mm) + 96mm = 페이지 상단 124mm 고정 (STYLE 표지 문법)
    place(top + left, dx: 20mm, dy: 124mm, block(width: 160mm, {
      set text(fill: white, font: TT.display-font)
      context {
        // 48pt ExtraBold 기본, 3행(3×52pt) 초과 시에만 하향
        let title-at(sz) = text(size: sz, weight: "extrabold", tracking: -0.025em,
          keep-words(meta.title))
        let sz = 48pt
        while sz > 30pt and measure(block(width: 160mm, title-at(sz))).height > 3 * 52pt {
          sz = sz - 4pt
        }
        title-at(sz)
      }
      if meta.at("subtitle", default: none) != none {
        v(6mm)
        text(size: 16pt, weight: "regular", fill: navy-100, keep-words(meta.subtitle))
      }
      v(12mm)
      line(length: 100%, stroke: 0.6pt + navy-500.transparentize(40%))
    }))
    place(bottom + left, dx: 20mm, dy: -18mm, {
      set text(size: 8pt, fill: navy-100, font: TT.sans-font)
      [#meta.at("author", default: "bookforge") · #meta.at("date", default: "") · #meta.at("series_no", default: "REPORT 01")]
    })
  })
}

// ---- 도비라: navy 풀블리드 + 96pt 장번호 + accent 룰 + 하단 절 목록 ----------
#let biz-opener(n, title, summary, t) = {
  full-bleed(t, block(fill: navy-900, width: 100%, height: 100%, inset: (x: 20mm, y: 28mm), {
    set text(fill: white, font: t.display-font)
    set par(justify: false, first-line-indent: 0em)
    // 표지 계통 벡터 패턴: 우측 하단 60% 영역, 30% 불투명도 (STYLE 도비라 문법)
    place(bottom + right, dx: 20mm, dy: 28mm,
      block(width: 120mm, height: 168mm, clip: true, cover-pattern(120mm, 168mm)))
    v(6mm)
    text(size: 96pt, weight: "extrabold", tracking: -0.03em, fill: navy-300, numpad(n))
    v(6mm)
    text(size: 30pt, weight: "extrabold", tracking: -0.02em, keep-words(title))
    v(12mm)
    rect(width: 40mm, height: 3pt, fill: accent)
    if summary != none {
      v(6mm)
      set text(size: 11pt, weight: "regular", fill: navy-100)
      set par(leading: 0.7em, justify: false)
      block(width: 82%, summary)
    }
    // 하단 좌측: 해당 장 수록 절 목록 8pt/+6% navy-300
    context {
      let h1s = query(heading.where(level: 1).after(here()))
      let secs = query(heading.where(level: 2).after(here()))
      if h1s.len() > 0 {
        let lim = h1s.first().location().page()
        secs = secs.filter(h => h.location().page() < lim)
      }
      if secs.len() > 0 {
        place(bottom + left, {
          set text(font: t.sans-font, size: 8pt, tracking: 0.06em, fill: navy-300)
          set par(leading: 0.5em, spacing: 0.5em)
          stack(dir: ttb, spacing: 2.8mm, ..secs.map(h => h.body))
        })
      }
    }
  }))
}

#let biz-tbl = counter("biz-tbl")
#let biz-fig = counter("biz-fig")

// T1 — Executive Summary: 도비라 없이 라벨 + 결론 액션 타이틀(22pt)로 여는 지면.
// 장 카운터(chapter-state)를 건드리지 않아 본장 번호·표/그림 채번이 밀리지 않는다.
#let bf-exec-open(title, summary) = {
  pagebreak(weak: true)
  hide(block(height: 0pt, heading(level: 1, outlined: true, bookmarked: true, title)))
  v(-1.2em)
  block({
    set par(justify: false, first-line-indent: 0em)
    // 라벨색은 토큰만 사용 — accent(#C2662E)는 흰 바탕 4.01로 4.5:1 미달(G14-C).
    // W4 7단계 전에는 10.5pt Bold로 올려 구(舊) 완화 하한의 "대형 3:1" 대역에 넣어
    // 통과시켰으나, 하한이 WCAG(≥18pt 또는 ≥14pt Bold)로 교정되면서 그 회피가 무효화됐다.
    // 급수를 14pt Bold로 더 올리는 길은 STYLE.md 타입 스케일에 없다(라벨은 8/12/+6이
    // 유일한 급수이고, 14pt는 리드문 13pt·항 15pt 사이라 라벨이 액션 타이틀과 경합한다).
    // 그래서 색을 바꾼다 — CONTENTS 라벨(아래 toc-head)이 같은 이유로 이미 택한
    // navy-700(11.60:1)을 그대로 쓰고, 급수는 STYLE.md T1 규정값 8pt/+6%로 되돌린다.
    text(font: TT.sans-font, size: 8pt, tracking: 0.06em, weight: "bold", fill: navy-700, title)
    if summary != none {
      v(4mm)
      text(font: TT.display-font, size: 22pt, weight: "bold", tracking: -0.015em,
        fill: navy-900, keep-words(summary))
    }
    v(3mm)
    line(length: 100%, stroke: 0.8pt + navy-700)
  })
  v(4mm)
}

#let bf-chapter(title, summary: none) = {
  if lower(title).contains("executive summary") {
    bf-exec-open(title, summary)
  } else {
    biz-tbl.update(0)
    biz-fig.update(0)
    base.chapter(title, summary: summary, t: TT, opener: biz-opener)
  }
}

// ---- 키 스탯: accent 상단 룰 + Gmarket 숫자 40pt (STYLE 타입 스케일) ----------
// 주의: 본문 par spacing(1em)은 급수에 비례해 커진다 — 40pt 문단이 그대로 상속하면
// 룰과 숫자 사이 20mm대 공기가 생긴다(실측). 블록 내부는 스페이싱을 0으로 재설정.
#let bf-stat-cell(value, label, width: 100%) = {
  set par(spacing: 0em, leading: 0.35em, justify: false, first-line-indent: 0em)
  set block(spacing: 0em)
  rect(width: width, height: 2pt, fill: accent)
  v(2.5mm)
  block(text(font: TT.stat-font, weight: "bold", size: 40pt, tracking: -0.03em,
    fill: navy-900, top-edge: "cap-height", bottom-edge: "baseline", value))
  v(2.5mm)
  block(width: width, text(font: TT.sans-font, size: 9pt, fill: ink-60, label))
}

#let bf-stat(value, label) = {
  block(breakable: false, width: 50mm, above: 5mm, below: 5mm,
    bf-stat-cell(value, label))
}

// ---- Exec Summary 리드문 13/21pt ---------------------------------------------
#let bf-lead(body) = block(width: 100%, above: 4mm, below: 5mm, {
  set text(size: 13pt, fill: ink)
  set par(leading: 0.62em, spacing: 1.0em, justify: true, first-line-indent: 0em)
  body
})

// ---- 2단(3+3 컬럼) 배치 — Exec Summary 키 메시지용 (2단 본문 9.5/15.5) -------
// columns()는 무한 플로우에서 남은 지면 전체를 차지한다(실측 — 뒤따르는 스탯
// 스트립이 다음 면으로 밀림). 단일 컬럼 실측 높이의 절반 + 여유로 높이를 고정.
#let bf-cols(body) = {
  let styled = {
    set text(size: 9.5pt)
    set par(leading: 0.63em, spacing: 0.9em)
    body
  }
  block(width: 100%, above: 4mm, below: 4mm, layout(size => context {
    let col-w = (size.width - 5mm) / 2
    let h-full = measure(block(width: col-w, styled)).height
    let h = h-full / 2 + 30pt  // 헤딩 keep 경계의 불균형 분할 여유
    block(width: 100%, height: h, columns(2, gutter: 5mm, styled))
  }))
}

// ---- 키 스탯 3연 스트립 (T1 하단, paper-alt 바탕) ----------------------------
// items: "값 | 라벨" 행들의 배열
// T1 하단 고정 스트립 — 흐름이 아니라 지면 하단에 앉힌다 (STYLE T1 "하단 고정 스트립")
#let bf-statrow(..items) = place(bottom + left,
  block(breakable: false, width: 100%, fill: paper-alt, inset: 6mm,
    // align: top — place(bottom)의 정렬 컨텍스트가 셀에 상속되면 설명이 2행인 셀만
    // 숫자가 위로 밀려 3연 숫자 기준선이 어긋난다(실측 9.5pt). 셀 상단 정렬로
    // 룰·숫자 기준선을 통일하고, 행 수 차이는 라벨 아래쪽으로만 흡수한다.
    grid(columns: (1fr,) * items.pos().len(), column-gutter: 6mm, align: top,
      ..items.pos().map(it => bf-stat-cell(it.at(0), it.at(1))))))

// ---- 콜아웃: 인사이트 박스 / 인용 박스 / alert ------------------------------
#let bf-callout(kind: "info", title: none, body) = {
  if kind == "quote" {
    block(breakable: false, inset: (left: 6mm),
      stroke: (left: 3pt + navy-500), {
        set text(font: TT.quote-font, size: 13pt, fill: navy-900)
        set par(leading: 0.62em, first-line-indent: 0em)
        body
      })
  } else {
    let label = if title != none { title } else if kind == "warn" { "유의" } else { "시사점" }
    let lc = if kind == "warn" { alert-c } else { navy-700 }
    block(
      width: 100%, breakable: false,
      fill: paper-alt, stroke: 0.5pt + navy-100, inset: 6mm,
      {
        text(font: TT.sans-font, size: 8pt, tracking: 0.06em, weight: "bold", fill: lc, upper(label))
        v(2.5mm)
        set text(size: 9.5pt)
        set par(leading: 0.6em, spacing: 0.8em)
        body
      })
  }
}

// 그림: 표와 동일한 장-순번 채번 — [그림 2-1] 9pt Bold navy-700 + 제목 11pt SemiBold
#let bf-fig(path, caption: none, source: none, width: 100%) = {
  block(breakable: false, {
    if caption != none {
      context {
        biz-fig.step()
        let n = chapter-state.get().num
        let m = biz-fig.get().first() + 1
        text(font: TT.sans-font, size: 9pt, weight: "bold", fill: navy-700,
          "[그림 " + str(n) + "-" + str(m) + "]")
        h(0.5em)
        text(font: TT.sans-font, size: 11pt, weight: "semibold", fill: ink, caption)
      }
      v(2.5mm)
    }
    image(path, width: width)
    if source != none {
      v(3mm)
      text(font: TT.sans-font, size: 7.5pt, fill: ink-60, [자료: #source])
    }
  })
}

// 표: 콘텐츠 [표] 캡션 계약 — 캡션이 실재할 때만 <표 n-m> 라벨, 출처는 콘텐츠가 준 것만
// breakable — 판면보다 긴 표를 unbreakable 블록에 넣으면 Typst가 넘친 행을
// 쪽 하단 한 줄에 0높이로 겹쳐 찍는다(issue #7). 쪽넘김 + table.header 반복이 정답.
#let bf-tbl(caption: none, source: none, body) = block(breakable: true, above: 6mm, below: 6mm, width: 100%, {
  if caption != none {
    context {
      biz-tbl.step()
      let n = chapter-state.get().num
      let m = biz-tbl.get().first() + 1
      text(font: TT.sans-font, size: 9pt, weight: "bold", fill: navy-700,
        "<표 " + str(n) + "-" + str(m) + ">")
      h(0.5em)
      text(font: TT.sans-font, size: 9.5pt, weight: "semibold", fill: ink, caption)
    }
    v(2mm)
  }
  body
  if source != none {
    v(2mm)
    text(font: TT.sans-font, size: 7.5pt, fill: ink-60, [자료: #source])
  }
})

#let colophon(meta, t) = {
  pagebreak(weak: true)
  page(header: none, footer: none, background: none, {  // 판권면: 러닝·섹션 탭 생략
    set text(size: 8pt, fill: ink-60)
    set par(first-line-indent: 0em)
    v(1fr)
    line(length: 40%, stroke: 0.4pt + rule-c)
    v(4pt)
    [#meta.title · #meta.at("author", default: "bookforge") · #meta.at("date", default: "") 발행 · bookforge로 조판]
    linebreak()
    [본 보고서의 수치·인용은 본문 표기 출처를 따르며, 무단 전재를 금합니다.]
  })
}

// ---- 마스터 래퍼 -------------------------------------------------------------
#let book(meta: (:), tokens: (:), cover: none, toc: true, toc-title: "차례", body) = {
  let t = TT
  set document(title: meta.at("title", default: "무제"), author: meta.at("author", default: "bookforge"))
  set page(
    width: t.trim.w, height: t.trim.h,
    margin: (top: t.margin.top, bottom: t.margin.bottom, left: t.margin.left, right: t.margin.right),
    // 러닝헤드 하단(헤어라인) = 판면 상단 위 6mm → 텍스트 베이스라인 ≈ 8mm (STYLE 러닝 시스템)
    header-ascent: 6mm,
    header: context {
      let prev = query(heading.where(level: 1).before(here()))
      if prev.len() > 0 {
        set text(font: t.sans-font, size: 8pt, tracking: 0.06em, fill: ink-60)
        let n = chapter-state.get().num
        if n > 0 { numpad(n); h(0.6em) }  // 좌측 = {장번호} {장 제목}
        prev.last().body
        h(1fr)
        meta.at("title", default: "")
        v(1.2mm)  // 베이스라인(판면 -8mm)과 헤어라인(-6mm) 간격 2mm — 디센트 0.6mm 감안
        line(length: 100%, stroke: 0.4pt + rule-c)
      }
    },
    footer: context {
      // H1이 실린 면(도비라·Exec Summary 첫 면)은 쪽번호 미표기 (러닝 시스템 규약)
      let pg = here().page()
      let h1-here = query(heading.where(level: 1)).filter(h => h.location().page() == pg)
      if h1-here.len() == 0 {
        align(right, text(font: t.sans-font, size: 9pt, weight: "medium", fill: navy-700,
          str(counter(page).get().first())))
      }
    },
    background: context {
      // 섹션 탭: 재단선 안쪽 8mm(x0=186mm), 도비라·ES 면에는 그리지 않는다(유령 탭 방지)
      let n = chapter-state.get().num
      let pg = here().page()
      let h1-here = query(heading.where(level: 1)).filter(h => h.location().page() == pg)
      if n > 0 and h1-here.len() == 0 {
        place(top + right, dx: -8mm, dy: 28mm + (n - 1) * 26mm,
          rect(width: 6mm, height: 24mm, fill: navy-500, {
            align(center + horizon, text(font: t.sans-font, size: 8pt, weight: "bold",
              fill: white, numpad(n)))
          }))
      }
    },
  )
  set text(font: t.body-font, size: t.body-size, fill: ink, lang: "ko", region: "KR")
  set text(costs: (orphan: 100%, widow: 100%, runt: 200%))
  set par(justify: true, leading: t.body-leading, spacing: 1.0em, first-line-indent: 0em)

  // 절/항: 액션 타이틀 문법 — 강제 개면 금지(흐름 배치), 개면은 H1만
  show heading.where(level: 2): it => {
    v(1.8em, weak: true)
    block(sticky: true, {
      text(font: t.sans-font, size: 16pt, weight: "bold", tracking: -0.01em, fill: navy-900, it.body)
      v(2.2mm)
      line(length: 100%, stroke: 0.8pt + navy-700)
    })
    v(1.1em, weak: true)
  }
  show heading.where(level: 3): it => {
    v(1.5em, weak: true)
    block(sticky: true, text(font: t.sans-font, size: 12pt, weight: "semibold", fill: navy-700, it.body))
    v(0.6em, weak: true)
  }
  set heading(numbering: none)

  show quote.where(block: true): it => bf-callout(kind: "quote")[#it.body]
  set list(marker: ([•], [–]), indent: 5mm, spacing: 0.7em, body-indent: 3mm)
  set enum(indent: 5mm, spacing: 0.7em, body-indent: 3mm)
  show list: set block(above: 1em, below: 1em)
  show enum: set block(above: 1em, below: 1em)
  set text(number-type: "lining", number-width: "tabular")
  show raw.where(block: true): it => block(
    width: 100%, fill: paper-alt, inset: 5mm, stroke: 0.5pt + navy-100,
    text(font: code-font, size: 8.5pt, it))

  // 표: 세로 괘선·얼룩말 금지, navy 상하 굵은 룰
  set table(stroke: none, inset: (x: 3mm, y: 2.6mm), fill: none)
  show table: it => {
    set text(size: 9pt, font: t.sans-font)
    // breakable — bf-tbl과 같은 이유(issue #7). 여기가 unbreakable이면 bf-tbl을
    // 고쳐도 이 래퍼가 다시 표를 한 판면에 눌러 담아 행이 겹친다.
    block(breakable: true, {
      it
    })
  }
  set table(stroke: (x, y) => (
    top: if y == 0 { 1.2pt + navy-900 } else if y == 1 { 0.6pt + navy-700 } else { 0.4pt + rule-c },
    bottom: 1.2pt + navy-900,
  ))
  show table.cell.where(y: 0): it => text(weight: "semibold", fill: navy-900, it)
  show table.cell: set align(left + horizon)
  show link: it => text(fill: navy-500, it)
  show figure.caption: it => text(font: t.sans-font, size: 8pt, fill: ink-60, it)

  if cover != none { cover }
  // 리포트형: 속표지 생략, 목차 1면 완결 (STYLE.md「목차 문법」)
  //  - 좌측 22.5mm 컬럼 장번호 / 우측 5컬럼 장제목 + 절제목 리스트
  //  - 점선 리더 금지, 쪽번호 우측 정렬 tabular, 위계는 장·절 2단계까지
  //  - 최상단 Executive Summary는 장번호 없이 별도 행
  if toc {
    // 한 행 = 제목(1fr) + 쪽번호(우측 정렬). 리더 없음.
    let toc-row(body, pnum, t-size, p-size, t-fill, p-fill, t-weight, t-font) = grid(
      columns: (1fr, 11mm), column-gutter: 3mm,
      align: (left + top, right + top),
      text(font: t-font, size: t-size, weight: t-weight, tracking: -0.01em, fill: t-fill, body),
      {
        // 쪽번호를 제목 베이스라인에 맞춰 내림(급수 차 보정)
        v((t-size - p-size) * 0.88)
        text(font: t.sans-font, size: p-size, weight: "medium", fill: p-fill, str(pnum))
      },
    )

    // 항목 전체 렌더 — 간격/급수는 tier로 주입(1면 완결을 위한 적응 축소)
    let toc-body(entries, ch-gap, sec-gap, ch-size, sec-size, num-size) = {
      // 간격은 오직 v()로만 — 블록 자동 간격 제거(1면 예산 계산의 전제)
      set par(justify: false, first-line-indent: 0em, leading: 0.42em, spacing: 0em)
      set block(spacing: 0em)
      for (i, e) in entries.enumerate() {
        if i > 0 { v(ch-gap) }
        block(breakable: false, width: 100%, grid(
          columns: (22.5mm, 1fr),
          {
            // 장번호 01 / ES는 번호 없이 accent 마커
            if e.num == none {
              v(ch-size * 0.5)
              rect(width: 12mm, height: 2pt, fill: accent)
            } else {
              text(font: t.display-font, size: num-size, weight: "extrabold",
                tracking: -0.02em, fill: navy-500, numpad(e.num))
            }
          },
          {
            link(e.loc, toc-row(e.title, e.page, ch-size, ch-size * 0.7,
              navy-900, navy-700, "semibold", t.sans-font))
            if e.secs.len() > 0 {
              v(sec-gap * 0.9)
              for (j, s) in e.secs.enumerate() {
                if j > 0 { v(sec-gap) }
                link(s.loc, toc-row(s.title, s.page, sec-size, sec-size,
                  ink-60, ink-60, "regular", t.body-font))
              }
            }
          },
        ))
        // ES 블록은 본장과 헤어라인으로 분리
        if e.num == none {
          v(ch-gap * 0.6)
          line(length: 100%, stroke: 0.4pt + rule-c)
        }
      }
    }

    let toc-head = {
      set par(spacing: 0em)
      set block(spacing: 0em)
      // 라벨색은 토큰만 사용 — accent(#C2662E)는 8pt에서 배경 대비 4.5:1 미달(G14-C)이라
      // 그림/표 라벨과 같은 navy-700을 쓴다 (임의 중간색 #AF5C2A 제거)
      text(font: t.sans-font, size: 8pt, tracking: 0.06em, weight: "bold", fill: navy-700, "CONTENTS")
      v(3mm)
      text(font: t.display-font, size: 20pt, weight: "extrabold", tracking: -0.02em,
        fill: navy-900, toc-title)
      v(4mm)
      line(length: 100%, stroke: 1.2pt + navy-900)
      v(8mm)
    }

    // 넉넉한 사양치부터 시도해 1면에 들어가는 첫 tier 채택
    let tiers = (
      (ch: 12mm,  sec: 6mm,   chs: 15pt,   secs: 10.5pt, num: 24pt),
      (ch: 10mm,  sec: 5mm,   chs: 14.5pt, secs: 10pt,   num: 22pt),
      (ch: 8mm,   sec: 4.2mm, chs: 14pt,   secs: 9.5pt,  num: 21pt),
      (ch: 6.5mm, sec: 3.4mm, chs: 13pt,   secs: 9pt,    num: 19pt),
      (ch: 6.0mm, sec: 3.1mm, chs: 12.5pt, secs: 8.8pt,  num: 18pt),
      (ch: 5.2mm, sec: 2.8mm, chs: 12pt,   secs: 8.5pt,  num: 17pt),
      (ch: 4.2mm, sec: 2.2mm, chs: 11.5pt, secs: 8.2pt,  num: 16pt),
      (ch: 3.4mm, sec: 1.7mm, chs: 11pt,   secs: 8pt,    num: 15pt),
      (ch: 2.8mm, sec: 1.2mm, chs: 10.5pt, secs: 7.6pt,  num: 14pt),
    )

    // 목차 면은 6컬럼 전폭(160mm)을 쓴다 — 바깥 마진 컬럼 해제
    page(
      margin: (top: t.margin.top, bottom: t.margin.bottom,
        left: t.margin.left, right: t.margin.left),
      header: none, footer: none, background: none,
      context {
        let w = t.trim.w - t.margin.left * 2
        let avail = t.trim.h - t.margin.top - t.margin.bottom

        // 장·절 수집 (2단계까지, 항 제외)
        let hs = query(heading).filter(h => h.level <= 2 and h.outlined)
        let entries = ()
        for h in hs {
          let p = counter(page).at(h.location()).first()
          if h.level == 1 {
            entries.push((
              num: entries.len() + 1, title: h.body,
              page: p, loc: h.location(), secs: (),
            ))
          } else if entries.len() > 0 {
            let last = entries.pop()
            last.secs.push((title: h.body, page: p, loc: h.location()))
            entries.push(last)
          }
        }
        // 1장이 Executive Summary면 번호 없는 별도 행으로 — 뒤 장들은 01부터 다시 채번
        // (본문 도비라·표/그림 번호는 chapter-state 기준이라 ES를 세지 않는다)
        if entries.len() > 0 {
          let head-title = lower(plain-text(entries.first().title))
          if head-title.contains("executive summary") or head-title.contains("요약") {
            let first = entries.first()
            first.num = none
            entries.at(0) = first
            for i in range(1, entries.len()) {
              let e = entries.at(i)
              e.num = e.num - 1
              entries.at(i) = e
            }
          }
        }

        let hh = measure(block(width: w, toc-head)).height
        let budget = avail - hh - 4mm
        let fits(tier) = measure(block(width: w,
          toc-body(entries, tier.ch, tier.sec, tier.chs, tier.secs, tier.num))).height
        let pick = tiers.last()
        for tier in tiers {
          if fits(tier) <= budget { pick = tier; break }
        }
        // 남은 여백은 장 사이 간격으로 되돌린다(사양치 12mm 상한)
        let slack = budget - fits(pick)
        let gaps = calc.max(entries.len() - 1, 1)
        let ch-gap = calc.min(pick.ch + slack / gaps, 12mm)

        toc-head
        toc-body(entries, ch-gap, pick.sec, pick.chs, pick.secs, pick.num)
      },
    )
  }
  counter(page).update(1)
  body
}
