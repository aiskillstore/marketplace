// bookforge style: essay — 미니멀 에세이 (STYLE.md: 사륙판 128×188, 먹1도+포인트1색)
#import "base.typ": default-tokens, keep-words, numpad, chapter-state
#import "base.typ" as base
#let code-font = ((name: "DejaVu Sans Mono", covers: regex("[A-Za-z0-9]")), "Pretendard")

#let meta = json("meta.json")

#let theme-tokens = default-tokens + (
  trim: (w: 128mm, h: 188mm),
  margin: (top: 24mm, bottom: 26mm, left: 20mm, right: 20mm),
  brand: rgb(meta.at("brand", default: "#A2604A")),   // accent (terracotta)
  brand-light: rgb("#A2604A").transparentize(85%),
  ink: rgb("#1A1A1A"),
  ink-soft: rgb("#3A3630"),
  muted: rgb("#6E6A66"),
  rule: rgb("#DAD5CE"),
  paper: rgb("#FBFAF7"),
  body-font: ("Noto Serif KR",),
  sans-font: ("Pretendard",),
  display-font: ("Noto Serif KR",),
  body-size: 10pt,
  body-leading: 0.92em,
)

#let TT = theme-tokens

// ---- cover: 침묵대 + 타이포 존 + 아트 존 + 푸터 (세로 5존 그리드) ------------
#let make-cover(meta) = {
  let t = TT
  page(margin: 0mm, header: none, footer: none, fill: t.paper, {
    set par(justify: false, first-line-indent: 0em)
    block(width: 100%, height: 100%, inset: (left: 20mm, right: 20mm), {
      v(46mm)  // 침묵대
      text(font: t.display-font, size: 28pt, weight: "regular", fill: t.ink,
        keep-words(meta.title))
      if meta.at("subtitle", default: none) != none {
        v(8mm)
        text(font: t.sans-font, size: 12pt, weight: "light", tracking: 0.04em,
          fill: t.ink-soft, keep-words(meta.subtitle))
      }
      v(14mm)
      text(font: t.display-font, size: 11pt, fill: t.ink, meta.at("author", default: ""))
      v(1fr)
      // 아트 존: 생성 아트 1점(무텍스트), 없으면 accent 원점으로 침묵을 지킨다
      place(bottom + left, dy: -26mm, {
        let art = meta.at("_cover_art", default: none)
        if art != none {
          image(art, width: 58mm)
        } else {
          circle(radius: 1.6mm, fill: t.brand)
        }
      })
      place(bottom + left, dy: -14mm,
        text(font: t.sans-font, size: 8pt, weight: "medium", tracking: 0.08em,
          fill: t.muted, meta.at("publisher", default: "BOOKFORGE")))
      v(20mm)
    })
  })
}

// ---- 장 시작 면: 여백 낙차형 (배경·괘선·장식 금지) ---------------------------
#let essay-opener(n, title, summary, t) = {
  block(width: 100%, {
    set par(justify: false, first-line-indent: 0em, leading: 7pt, spacing: 7pt)
    v(28mm)  // 상단 낙차
    text(font: t.sans-font, size: 9pt, weight: "light", tracking: 0.18em,
      fill: t.brand, numpad(n))
    v(6mm)
    text(font: t.display-font, size: 15pt, weight: "regular", fill: t.ink,
      keep-words(title))
    if summary != none {
      v(7mm)
      text(size: 9.5pt, fill: t.ink-soft, summary)
    }
    v(15mm)
  })
}

// 여백 낙차형: 별지 도비라가 아니라 같은 면에서 본문이 흘러야 한다
#let bf-chapter(title, summary: none) = {
  pagebreak(weak: true)
  chapter-state.update(s => (num: s.num + 1, title: title))
  context {
    let n = chapter-state.get().num
    hide(block(height: 0pt, heading(level: 1, outlined: true, bookmarked: true, title)))
    v(-1.2em)
    essay-opener(n, title, summary, TT)
  }
}

// ---- 콜아웃: 박스 금지 → 전부 저자 노트(헤어라인)로 강등 ----------------------
#let bf-callout(kind: "info", title: none, body) = {
  block(breakable: false, inset: (x: 10mm), {
    line(length: 100%, stroke: 0.3pt + TT.rule)
    v(4mm)
    set text(size: 9pt, fill: TT.ink-soft)
    set par(leading: 0.8em, spacing: 0.8em, first-line-indent: 0em)
    set list(spacing: 0.7em)
    body
    v(4mm)
    line(length: 100%, stroke: 0.3pt + TT.rule)
  })
}

#let bf-stat(value, label) = bf-callout[#value #h(4pt) #text(size: 8.5pt, fill: TT.muted, label)]

#let bf-fig(path, caption: none, source: none, width: 100%) = {
  figure(
    image(path, width: width),
    caption: if caption != none {
      text(font: TT.sans-font, size: 8.5pt, fill: TT.muted, {
        caption
        if source != none [ · #source]
      })
    } else { none },
    supplement: none, numbering: none,
  )
}

// 표(에세이엔 드묾): 번호 라벨 없이 캡션·출처만 조용히
// breakable — unbreakable 블록 속 긴 표는 넘친 행이 쪽 하단에 0높이로 겹친다(issue #7)
#let bf-tbl(caption: none, source: none, body) = block(breakable: true, above: 1.3em, below: 1.3em, width: 100%, {
  if caption != none {
    text(font: TT.sans-font, size: 8.5pt, fill: TT.muted, caption)
    v(2mm)
  }
  body
  if source != none {
    v(1.5mm)
    text(font: TT.sans-font, size: 7.5pt, fill: TT.muted, [· #source])
  }
})

// ---- 판권면 ------------------------------------------------------------------
#let colophon(meta, t) = {
  pagebreak(weak: true)
  page(header: none, footer: none, {
    set text(font: t.sans-font, size: 8pt, weight: "light", fill: t.ink-soft)
    set par(leading: 5pt, spacing: 5pt, first-line-indent: 0em)
    v(1fr)
    meta.title
    if meta.at("subtitle", default: none) != none [ — #meta.subtitle]
    linebreak()
    [초판 1쇄 발행 #meta.at("date", default: "")]
    linebreak()
    [지은이 #meta.at("author", default: "bookforge") · 펴낸곳 bookforge]
    linebreak()
    [조판 bookforge · 본문 Noto Serif KR · 표지·라벨 Pretendard]
  })
}

// ---- 마스터 래퍼 (base.book 대체 — 에세이 전용 지면 규칙) ---------------------
#let book(meta: (:), tokens: (:), cover: none, toc: true, toc-title: "차례", body) = {
  let t = TT
  set document(title: meta.at("title", default: "무제"), author: meta.at("author", default: "bookforge"))
  set page(
    width: t.trim.w, height: t.trim.h,
    margin: (top: t.margin.top, bottom: t.margin.bottom, left: t.margin.left, right: t.margin.right),
    fill: t.paper,
    header: none,
    footer: context {
      // 장 시작 면·판권면은 쪽번호 숨김
      let starts = query(heading.where(level: 1)).map(h => h.location().page())
      if not starts.contains(here().page()) {
        align(right, text(font: t.sans-font, size: 9pt, fill: t.muted,
          str(counter(page).get().first())))
      }
    },
  )
  // 행송 19pt 고정(사륙판 20행 격자): edge 고정 + leading=spacing=9pt
  set text(font: t.body-font, size: t.body-size, fill: t.ink, lang: "ko", region: "KR",
    top-edge: 0.8em, bottom-edge: -0.2em)
  set text(costs: (orphan: 100%, widow: 100%, runt: 200%))
  set par(justify: true, leading: 9pt, spacing: 9pt,
    first-line-indent: (amount: 1em, all: false))

  // 글 제목(h2) / 소제목(h3)
  show heading.where(level: 2): it => {
    v(38pt, weak: true)
    block(sticky: true, text(font: t.display-font, size: 12pt, weight: "regular", fill: t.ink, it.body))
    v(19pt, weak: true)
  }
  show heading.where(level: 3): it => {
    v(28.5pt, weak: true)
    block(sticky: true, text(font: t.sans-font, size: 10pt, weight: "medium", tracking: 0.04em, fill: t.ink, it.body))
    v(9.5pt, weak: true)
  }
  set heading(numbering: none)

  // 인용문: 블록 인용, 배경 없음, accent-tint 헤어라인
  show quote.where(block: true): it => {
    v(7mm, weak: true)
    block(inset: (left: 6mm, right: 4mm),
      stroke: (left: 0.4pt + t.brand.transparentize(70%)),
      {
        set text(size: 9.5pt, fill: t.ink-soft)
        set par(leading: 0.78em, spacing: 0.7em, first-line-indent: 0em)
        it.body
      })
    v(7mm, weak: true)
  }
  set list(marker: ([·],), indent: 0.5em, spacing: 0.75em)
  set enum(indent: 0.5em, spacing: 0.75em)
  show list: set block(above: 0.9em, below: 0.9em)
  show enum: set block(above: 0.9em, below: 0.9em)
  show figure: set block(above: 1.2em, below: 1.2em)
  show raw.where(block: true): it => block(
    width: 100%, inset: (x: 6mm, y: 4mm),
    stroke: (top: 0.3pt + t.rule, bottom: 0.3pt + t.rule),
    text(font: t.sans-font, size: 8pt, it))
  set table(stroke: none, inset: (x: 5pt, y: 5pt))
  show table: it => { set text(size: 8.5pt, font: t.sans-font); it }
  show table.cell.where(y: 0): it => text(weight: "medium", it)
  set table(fill: none, stroke: (x, y) => if y == 0 { (bottom: 0.4pt + t.ink) } else { (bottom: 0.3pt + t.rule) })
  show link: it => text(fill: t.ink, it)

  if cover != none { cover }

  // 속표지 (표지 타이포 그리드 80% 축소판)
  page(header: none, footer: none, {
    v(40mm)
    text(font: t.display-font, size: 22pt, keep-words(meta.title))
    if meta.at("subtitle", default: none) != none {
      v(6mm)
      text(font: t.sans-font, size: 10pt, weight: "light", fill: t.ink-soft, meta.subtitle)
    }
    v(11mm)
    text(font: t.display-font, size: 10pt, meta.at("author", default: ""))
  })

  // 차례: 리더선 금지, 좌측 정렬 + 우측 쪽번호
  if toc {
    page(header: none, footer: none, {
      v(24mm)
      text(font: t.display-font, size: 13pt, tracking: 0.12em, toc-title)
      v(14mm)
      set text(size: 10pt)
      show outline.entry: it => {
        set par(leading: 0.6em)
        v(14pt, weak: true)
        link(it.element.location(), {
          it.body()
          h(1fr)
          text(font: t.sans-font, size: 9pt, fill: t.muted, it.page())
        })
      }
      outline(title: none, depth: 1)
    })
  }
  counter(page).update(1)
  body
}
