// bookforge base library — shared book primitives for all Typst themes.
// A theme imports this, defines its token dict, and calls `book(...)`.
// Tokens contract (all optional, defaults below):
//   trim: (w, h) mm · margin: (top, bottom, left, right) mm
//   brand, brand-light, ink, muted, paper: colors
//   body-font, sans-font, display-font: str/array
//   body-size, body-leading, heading2-size, heading3-size
#let code-font = ((name: "DejaVu Sans Mono", covers: regex("[A-Za-z0-9]")), "Pretendard")

#let default-tokens = (
  trim: (w: 153mm, h: 225mm),
  margin: (top: 22mm, bottom: 20mm, left: 18mm, right: 16mm),
  brand: rgb("#1a5fb4"),
  brand-light: rgb("#e8f0fa"),
  ink: rgb("#1e2228"),
  muted: rgb("#6b7480"),
  paper: white,
  body-font: ("Pretendard",),
  sans-font: ("Pretendard",),
  display-font: ("Pretendard",),
  body-size: 9.5pt,
  body-leading: 0.85em,
  heading2-size: 14pt,
  heading3-size: 11pt,
)

#let merged(tokens) = {
  let t = default-tokens
  for (k, v) in tokens { t.insert(k, v) }
  t
}

// ---- word-keeping for display text (keep-all workaround) -------------------
// Wrap each space-separated word in a box so Korean titles break per word.
#let keep-words(it) = {
  let parts = if type(it) == str { it.split(" ") } else { (it,) }
  if type(it) == str {
    parts.map(w => box(w)).join([ ])
  } else { it }
}

// ---- full-bleed helper ------------------------------------------------------
// Draws content covering the whole trim, ignoring page margins.
#let full-bleed(t, body) = {
  place(top + left,
    dx: -t.margin.left, dy: -t.margin.top,
    block(width: t.trim.w, height: t.trim.h, body))
}

// ---- chapter opener (dobira) -----------------------------------------------
// Registers a level-1 heading (for outline/bookmarks/running head) and renders
// a full opener page. Theme can override via `opener` callback token.
#let chapter-state = state("bf-chapter", (num: 0, title: ""))

#let chapter(title, summary: none, t: (:), opener: none) = {
  let t = merged(t)
  pagebreak(weak: true)
  chapter-state.update(s => (num: s.num + 1, title: title))
  counter("bf-tbl-n").update(0)
  context {
    let n = chapter-state.get().num
    page(header: none, footer: none, {
      // invisible but real heading: outline + bookmarks + running-head queries
      hide(block(height: 0pt, heading(level: 1, outlined: true, bookmarked: true, title)))
      v(-1.2em)
      set par(justify: false, first-line-indent: 0em)
      if opener != none { (opener)(n, title, summary, t) }
      else {
        full-bleed(t, block(fill: t.brand, width: 100%, height: 100%, inset: (x: t.margin.left, y: t.margin.top), {
          set text(fill: white, font: t.display-font)
          v(8%)
          text(size: 64pt, weight: "black", str(n).pad(2, "0", start: true))
          v(2em)
          text(size: 24pt, weight: "bold", keep-words(title))
          if summary != none {
            v(2em)
            set text(size: 10.5pt, weight: "regular", fill: white.transparentize(15%))
            set par(leading: 0.9em)
            block(width: 78%, summary)
          }
        }))
      }
    })
  }
}

// pad helper for ints rendered as "01"
#let numpad(n) = if n < 10 { "0" + str(n) } else { str(n) }

// ---- callout boxes ----------------------------------------------------------
// kinds: info / tip / warn / quote / stat  — themes may restyle via show rules
#let callout(kind: "info", title: none, t: (:), body) = {
  let t = merged(t)
  let bg = if kind == "warn" { rgb("#fdf0ec") } else { t.brand-light }
  let bar = if kind == "warn" { rgb("#c0392b") } else { t.brand }
  block(
    width: 100%, breakable: false,
    fill: bg, radius: 4pt, inset: (x: 11pt, y: 10pt),
    stroke: (left: 2.5pt + bar),
    {
      // 박스 내부는 본문 격자(문단 간 1행 공백)를 따르지 않는다 — 밀착 리듬
      set par(spacing: 0.8em, first-line-indent: 0em)
      if title != none {
        text(font: t.sans-font, weight: "semibold", size: 9pt, fill: bar, title)
        v(4pt)
      }
      set text(size: 0.95em)
      body
    })
}

// big-number stat callout
#let stat(value, label, t: (:)) = {
  let t = merged(t)
  block(breakable: false, {
    text(font: t.display-font, weight: "extrabold", size: 30pt, fill: t.brand, value)
    h(8pt)
    box(baseline: 20%, text(font: t.sans-font, size: 9pt, fill: t.muted, label))
  })
}

// ---- figures ----------------------------------------------------------------
#let bookfig(path, caption: none, source: none, width: 100%, t: (:)) = {
  let t = merged(t)
  // placement: auto — 본문에서 가까운 상/하단으로 부동. bottom 고정은 도해가
  // 단독면으로 떨어질 때 상단 마진 아래가 통째로 비는 구멍을 만든다(시각 판정 C).
  // 인라인 배치는 도해 이월로 앞 면이 반백(G7-MID)이라 부동 자체는 유지.
  figure(
    placement: auto,
    image(path, width: width),
    caption: if caption != none {
      // 캡션·표·그림 규약: 그림 번호 없음, "▲ " + Light 7.5pt, 출처는 다음 줄 "출처 : <이름>"
      text(font: t.sans-font, size: 7.5pt, weight: "light", fill: t.ink, {
        [▲ ]
        caption
        if source != none {
          linebreak()
          text(size: 7pt, fill: t.muted)[출처 : #source]
        }
      })
    } else { none },
    numbering: none,
  )
}

// ---- tables (caption은 콘텐츠가 준다 — 필러 라벨 금지) ----------------------
#let tbl-counter = counter("bf-tbl-n")

#let bf-tbl-base(caption: none, source: none, t: (:), label-fmt: none, body) = {
  let t = merged(t)
  // breakable — unbreakable 블록 속 긴 표는 넘친 행이 쪽 하단에 0높이로 겹친다(issue #7)
  block(breakable: true, above: 1.3em, below: 1.3em, width: 100%, {
    if caption != none {
      context {
        tbl-counter.step()
        let n = chapter-state.get().num
        let m = tbl-counter.get().first() + 1
        let lab = if label-fmt != none { (label-fmt)(n, m) } else { "표 " + str(n) + "-" + str(m) }
        text(font: t.sans-font, size: 8.5pt, weight: "semibold", fill: t.brand, lab)
        h(0.6em)
        text(font: t.sans-font, size: 8.5pt, fill: t.ink, caption)
      }
      v(2mm)
    }
    body
    if source != none {
      v(1.5mm)
      text(font: t.sans-font, size: 7.5pt, fill: t.muted, [자료: #source])
    }
  })
}

// ---- front matter -----------------------------------------------------------
#let title-page(meta, t) = {
  page(header: none, footer: none, {
    set par(justify: false, first-line-indent: 0em)
    v(28%)
    set text(font: t.display-font)
    text(size: 26pt, weight: "bold", fill: t.ink, keep-words(meta.title))
    if "subtitle" in meta and meta.subtitle != none {
      v(1.2em)
      text(size: 12pt, fill: t.muted, keep-words(meta.subtitle))
    }
    v(1fr)
    set text(size: 9pt, fill: t.muted)
    if "author" in meta [#meta.author\ ]
    if "date" in meta [#meta.date]
    v(6%)
  })
}

#let colophon(meta, t) = {
  pagebreak(weak: true)
  page(header: none, footer: none, {  // 판권면: 러닝헤드·쪽번호 생략(러닝 시스템 규약)
    set text(size: 8pt, fill: t.muted)
    set par(first-line-indent: 0em)
    v(1fr)
    line(length: 30%, stroke: 0.5pt + t.muted)
    v(6pt)
    text(size: 9.5pt, fill: t.ink, weight: "semibold", meta.title)
    if "subtitle" in meta and meta.subtitle != none [ — #meta.subtitle]
    linebreak()
    if "author" in meta [지은이 #meta.author]
    linebreak()
    if "date" in meta [초판 1쇄 발행 #meta.date]
    linebreak()
    [펴낸곳 bookforge · 조판 bookforge 자동 조판 파이프라인]
    linebreak()
    [본문 서체 #merged((:)).body-font.at(0) · 표제 서체 #merged((:)).display-font.at(0)]
    linebreak()
    [이 책의 내용은 조사 시점 기준이며, 인용·수치는 본문 표기 출처를 따릅니다.]
  })
}

// ---- table of contents ------------------------------------------------------
#let book-toc(t, depth: 2, title: "차례", cols: 1) = {
  page(header: none, footer: none, {
    text(font: t.display-font, size: 20pt, weight: "bold", fill: t.ink, title)
    v(1.8em)
    set text(size: 9.2pt)
    show outline.entry.where(level: 1): it => {
      v(0.9em, weak: true)
      strong(text(font: t.sans-font, size: 10pt, fill: t.brand, it))
    }
    show outline.entry.where(level: 2): it => {
      v(0.45em, weak: true)
      text(size: 8.8pt, it)
    }
    if cols > 1 {
      columns(cols, gutter: 8mm, outline(title: none, depth: depth))
    } else {
      outline(title: none, depth: depth)
    }
  })
}

// ---- master wrapper ---------------------------------------------------------
// theme.typ calls: #show: book.with(meta: (...), tokens: theme-tokens, cover: ..)
#let book(meta: (:), tokens: (:), cover: none, toc: true, toc-title: "차례", toc-cols: 1, body) = {
  let t = merged(tokens)

  set document(title: meta.at("title", default: "무제"), author: meta.at("author", default: "bookforge"))
  set page(
    width: t.trim.w, height: t.trim.h,
    margin: (top: t.margin.top, bottom: t.margin.bottom, left: t.margin.left, right: t.margin.right),
    fill: t.paper,
    footer: context {
      let pn = counter(page).get().first()
      align(center, text(font: t.sans-font, size: 8pt, fill: t.muted, str(pn)))
    },
    header: context {
      let sel = heading.where(level: 1)
      let prev = query(sel.before(here()))
      if prev.len() > 0 {
        set text(font: t.sans-font, size: 7.5pt, fill: t.muted, tracking: 0.06em)
        prev.last().body
        h(1fr)
        text(fill: t.brand, meta.at("title", default: ""))
      }
    },
  )
  set text(font: t.body-font, size: t.body-size, fill: t.ink, lang: "ko", region: "KR")
  // 고아/과부 2행 계약(pagination.md §3) — 기본값과 같아도 명시로 고정
  set text(costs: (orphan: 100%, widow: 100%, runt: 200%))
  set par(justify: true, leading: t.body-leading, spacing: 1.15em, first-line-indent: (amount: 1em, all: false))

  // headings 2/3 (level 1 is consumed by chapter())
  show heading.where(level: 2): it => {
    v(1.6em, weak: true)
    block(sticky: true, text(font: t.sans-font, size: t.heading2-size, weight: "bold", fill: t.ink, it.body))
    v(0.7em, weak: true)
  }
  show heading.where(level: 3): it => {
    v(1.2em, weak: true)
    block(sticky: true, {
      box(baseline: -0.12em, circle(radius: 2.2pt, fill: t.brand))
      h(6pt)
      text(font: t.sans-font, size: t.heading3-size, weight: "semibold", fill: t.ink, it.body)
    })
    v(0.5em, weak: true)
  }
  set heading(numbering: none)

  // quotes / lists / code / tables
  show quote.where(block: true): it => block(
    inset: (left: 1.2em, y: 0.3em),
    stroke: (left: 2pt + t.brand.transparentize(50%)),
    text(fill: t.ink.transparentize(15%), it.body))
  set list(marker: ([•], [–]), indent: 0.5em)
  set enum(indent: 0.5em)
  show raw.where(block: true): it => block(
    width: 100%, fill: luma(247), radius: 4pt, inset: 9pt, breakable: true,
    text(font: code-font, size: 8pt, it))
  show raw.where(block: false): it => box(fill: luma(243), radius: 2pt, inset: (x: 3pt, y: 1pt), text(font: code-font, size: 0.92em, it))
  set table(stroke: none, inset: (x: 7pt, y: 6pt))
  show table: it => {
    set text(size: 8.7pt, font: t.sans-font)
    it
  }
  show table.cell.where(y: 0): it => text(weight: "semibold", fill: white, it)
  set table(fill: (x, y) => if y == 0 { t.brand } else if calc.odd(y) { t.brand-light.transparentize(45%) } else { none })
  show figure.where(kind: table): set figure.caption(position: top)
  show figure.caption: it => text(font: t.sans-font, size: 8.5pt, fill: t.muted, it)
  show link: it => text(fill: t.brand, it)

  // front matter
  if cover != none { cover }
  title-page(meta, t)
  if toc { book-toc(t, title: toc-title, cols: toc-cols) }
  counter(page).update(1)

  body
}
