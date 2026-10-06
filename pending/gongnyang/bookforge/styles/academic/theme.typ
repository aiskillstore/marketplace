// bookforge style: academic — 학술·논문형 (STYLE.md: 신국판 153×225, 1도+먹)
#import "base.typ": default-tokens, keep-words, chapter-state
#import "base.typ" as base
#let code-font = ((name: "DejaVu Sans Mono", covers: regex("[A-Za-z0-9]")), "Pretendard")

#let meta = json("meta.json")

#let accent = rgb(meta.at("brand", default: "#12395F"))
#let accent-tint = rgb("#E8EDF3")
#let ink = rgb("#1A1A1A")
#let muted = rgb("#6E6E6E")
#let rule-c = rgb("#2E2E2E")

#let theme-tokens = default-tokens + (
  trim: (w: 153mm, h: 225mm),
  margin: (top: 26mm, bottom: 34.9mm, left: 25mm, right: 22mm),
  brand: accent, brand-light: accent-tint,
  ink: ink, muted: muted, paper: white,
  // Libertinus는 라틴 영숫자만 — covers 없이 1순위로 두면 한국어 문장의
  // 공백·쉼표·마침표까지 라틴 세리프로 빠진다 (code-font와 동일 클래스 버그)
  body-font: ((name: "Libertinus Serif", covers: regex("[A-Za-z0-9]")), "Noto Serif KR"),
  sans-font: ("Pretendard",),
  display-font: ("Pretendard",),
  body-size: 10pt,
)

#let TT = theme-tokens

// ---- 표지: 이중 룰 표제 블록, 타이포 전용 ------------------------------------
#let make-cover(meta) = {
  page(header: none, footer: none, {
    set par(justify: false, first-line-indent: 0em)
    v(48mm - 26mm)
    line(length: 100%, stroke: 1.2pt + accent)
    v(9mm)
    align(center, {
      text(font: TT.display-font, weight: "semibold", size: 28pt, tracking: -0.02em,
        fill: ink, keep-words(meta.title))
    })
    v(9mm)
    line(length: 100%, stroke: 0.4pt + rule-c)
    if meta.at("subtitle", default: none) != none {
      v(7mm)
      align(center, text(font: ("Noto Serif KR",), size: 13pt, fill: ink, keep-words(meta.subtitle)))
    }
    v(16mm)
    align(center, text(font: TT.display-font, weight: "medium", size: 11.5pt, fill: ink,
      meta.at("author", default: "bookforge")))
    v(1fr)
    align(center, text(font: TT.display-font, weight: "medium", size: 9.5pt, fill: ink,
      meta.at("publisher", default: "bookforge")))
  })
}

#let fig-counter = counter("bf-fig")
#let tbl-counter = counter("bf-tbl")

// ---- 장 헤더: 도비라 별면 금지 — 같은 면에서 본문 시작 ------------------------
#let bf-chapter(title, summary: none) = {
  pagebreak(weak: true)
  chapter-state.update(s => (num: s.num + 1, title: title))
  counter(heading).step(level: 1)
  tbl-counter.update(0)
  fig-counter.update(0)
  context {
    let n = chapter-state.get().num
    v(12mm)
    hide(block(height: 0pt, heading(level: 1, outlined: true, bookmarked: true, numbering: none, title)))
    v(-1.2em)
    text(font: TT.display-font, weight: "medium", size: 10pt, tracking: 0.15em,
      fill: accent, "제" + str(n) + "장")
    v(4mm)
    line(length: 18mm, stroke: 1pt + accent)
    v(7mm)
    text(font: TT.display-font, weight: "semibold", size: 20pt, fill: ink, keep-words(title))
    v(8mm)
    line(length: 100%, stroke: 1pt + ink)
    if summary != none {
      v(9mm)
      block({
        set text(font: ("Noto Serif KR",), size: 9.5pt, fill: muted)
        set par(leading: 6.5pt, first-line-indent: 0em, justify: true)
        summary
      })
    }
    v(12mm)
  }
}

// ---- 정의·정리 박스 ----------------------------------------------------------
#let bf-callout(kind: "info", title: none, body) = {
  let label = if title != none { title } else if kind == "warn" { "유의" } else { "정리" }
  block(
    width: 100%, breakable: false,
    fill: accent-tint, stroke: (left: 1.5pt + accent),
    inset: (x: 8pt, y: 6pt), above: 5mm, below: 5mm,
    {
      set text(size: 9.5pt)
      set par(leading: 6.5pt, first-line-indent: 0em)
      text(font: TT.sans-font, weight: "semibold", size: 9.5pt, fill: accent, label)
      h(1em)
      body
    })
}

#let bf-stat(value, label) = bf-callout(title: "수치")[#strong(value) — #label]

#let bf-fig(path, caption: none, source: none, width: 100%) = {
  // placement: bottom — 도해를 면 하단으로 부동시켜 본문이 면을 계속 채우게 한다.
  // 인라인 블록이면 도해+후속 제목이 통째로 이월해 앞 면이 반백이 되고(G7-MID),
  // top 부동이면 꼬리면 reach가 도해 높이에서 캡되어 G7-TAIL에 걸린다.
  figure(placement: bottom, kind: image, supplement: none, numbering: none, gap: 0mm,
    block(breakable: false, above: 5mm, below: 5mm, {
    align(center, image(path, width: width))
    context {
      fig-counter.step()
      let n = chapter-state.get().num
      let f = fig-counter.get().first() + 1
      if caption != none {
        v(2mm)
        align(center, {
          set text(font: TT.sans-font, size: 8.5pt)
          text(weight: "semibold", fill: accent, "[그림 " + str(n) + "-" + str(f) + "] ")
          text(fill: ink, caption)
          if source != none { text(fill: muted)[ (자료: #source)] }
        })
      }
    }
  }))
}

// 표: 콘텐츠가 [표] 캡션을 준 경우에만 번호 라벨. 캡션 없으면 표만 렌더.
// breakable — unbreakable 블록 속 긴 표는 넘친 행이 쪽 하단에 0높이로 겹친다(issue #7)
#let bf-tbl(caption: none, source: none, body) = block(breakable: true, above: 6mm, below: 6mm, width: 100%, {
  if caption != none {
    context {
      tbl-counter.step()
      let n = chapter-state.get().num
      let m = tbl-counter.get().first() + 1
      align(center, {
        text(font: TT.sans-font, size: 8.5pt, weight: "semibold", fill: accent,
          "표 " + str(n) + "-" + str(m) + ".")
        h(0.5em)
        text(font: TT.sans-font, size: 8.5pt, fill: ink, caption)
      })
    }
    v(2mm)
  }
  align(center, block(stroke: (bottom: 1pt + ink), inset: 0pt, body))  // booktabs bottomrule
  if source != none {
    v(1.5mm)
    align(center, text(font: TT.sans-font, size: 7.5pt, fill: muted, [자료: #source]))
  }
})

// ---- 목차 보조: 제목에 이미 박힌 번호를 뽑아낸다(중복 표기 방지) --------------
#let bf-plain(c) = {
  if c == none { "" }
  else if type(c) == str { c }
  else if type(c) == content {
    if c.has("text") { c.text }
    else if c.has("children") { c.children.map(bf-plain).fold("", (a, b) => a + b) }
    else if c.has("body") { bf-plain(c.body) }
    else { "" }
  } else { "" }
}

// "1.2 제목" → ("1.2", "제목") / 번호가 없으면 (none, 원문)
#let bf-split-num(s) = {
  let m = s.match(regex("^\s*([0-9]+(?:[.\-][0-9]+)*)[.)]?[ \t]+(.+)$"))
  if m == none { (none, s) } else { (m.captures.at(0), m.captures.at(1)) }
}

#let colophon(meta, t) = {
  pagebreak(weak: true)
  page(header: none, footer: none, {  // 판권면: 러닝헤드·쪽번호 생략(러닝 시스템 규약)
    set text(font: TT.display-font, size: 8.5pt, fill: ink)
    set par(leading: 4.5pt, first-line-indent: 0em)
    v(1fr)
    meta.title
    if meta.at("subtitle", default: none) != none [ — #meta.subtitle]
    linebreak()
    [#meta.at("date", default: "") 발행 · 지은이 #meta.at("author", default: "bookforge")]
    linebreak()
    [조판 bookforge · 본문 Noto Serif KR·Libertinus Serif · 표제 Pretendard]
  })
}

// ---- 마스터 래퍼 -------------------------------------------------------------
#let book(meta: (:), tokens: (:), cover: none, toc: true, toc-title: "차 례", body) = {
  let t = TT
  set document(title: meta.at("title", default: "무제"), author: meta.at("author", default: "bookforge"))
  set page(
    width: t.trim.w, height: t.trim.h,
    margin: (top: t.margin.top, bottom: t.margin.bottom, left: t.margin.left, right: t.margin.right),
    header: context {
      let prev = query(heading.where(level: 1).before(here()))
      // 장 시작 면(도비라)은 러닝헤드 생략
      let starts = query(heading.where(level: 1)).map(h => h.location().page())
      if prev.len() > 0 and not starts.contains(here().page()) {
        set text(font: t.sans-font, size: 8.5pt, weight: "medium", fill: ink)
        // 폭 초과 시 좌측 클립 금지 — 번호는 항상 보존, 제목 꼬리만 말줄임
        let trunc(s, n) = {
          let cs = s.clusters()
          if cs.len() > n { cs.slice(0, n).join("") + "…" } else { s }
        }
        text(fill: accent, "제" + str(prev.len()) + "장")
        h(2em)
        trunc(bf-plain(prev.last().body), 18)
        h(1fr)
        // 우측: 현재 장 안에서 진행 중인 절만 (경계 오류 방지 — 이전 장 절 참조 금지,
        // 현재 면에서 시작한 절 포함, 절이 없으면 항목 생략)
        let ch-pg = prev.last().location().page()
        let secs = query(heading.where(level: 2)).filter(s => {
          let sp = s.location().page()
          sp >= ch-pg and sp <= here().page()
        })
        if secs.len() > 0 {
          text(fill: muted, str(prev.len()) + "." + str(secs.len()) + " " +
            trunc(bf-plain(secs.last().body), 14))
        }
        v(1.5mm)
        line(length: 100%, stroke: 0.4pt + rule-c)
      }
    },
    footer: context align(center,
      text(font: t.sans-font, size: 9pt, fill: ink, str(counter(page).get().first()))),
  )
  // 행송 17.5pt 고정: top/bottom-edge 고정 + leading 7.5pt
  set text(font: t.body-font, size: 10pt, fill: ink, lang: "ko", region: "KR",
    top-edge: 0.8em, bottom-edge: -0.2em, hyphenate: false,
    number-type: "lining", number-width: "tabular")
  set text(costs: (orphan: 100%, widow: 100%, runt: 200%))
  set par(justify: true, leading: 7.5pt, spacing: 7.5pt,
    first-line-indent: (amount: 1em, all: true))

  set heading(numbering: (..n) => {
    let p = n.pos()
    if p.len() >= 2 { p.slice(1).map(str).join(".") } else { none }
  })
  show heading.where(level: 2): it => {
    v(26.25pt, weak: true)
    block(sticky: true, text(font: t.sans-font, size: 11.5pt, weight: "semibold", fill: ink, {
      counter(heading).display((..n) => str(chapter-state.get().num) + "." + str(n.pos().at(1, default: 1)))
      h(1.5em)
      it.body
    }))
    v(8.75pt, weak: true)
  }
  show heading.where(level: 3): it => {
    v(17.5pt, weak: true)
    block(sticky: true, text(font: t.sans-font, size: 10.5pt, weight: "medium", fill: ink, it.body))
    v(5pt, weak: true)
  }

  show quote.where(block: true): it => block(
    inset: (left: 2em, right: 1em), above: 6mm, below: 6mm, {
      set text(size: 9.5pt)
      set par(leading: 6.5pt, first-line-indent: 0em)
      it.body
    })
  set list(indent: 1em, spacing: 7.5pt)
  set enum(indent: 1em, spacing: 7.5pt)
  show raw.where(block: true): it => block(
    width: 100%, fill: luma(248), inset: 8pt, above: 5mm, below: 5mm,
    text(font: code-font, size: 8.5pt, it))

  // 3선표(booktabs): 상하 1.0pt 먹, 헤더 아래 0.4pt. 캡션은 콘텐츠 [표] 계약(bf-tbl)만
  set table(stroke: none, inset: (x: 8pt, y: 5pt))
  show table: it => { set text(size: 9pt, font: t.sans-font); it }
  // booktabs 3선: top 1.0 / 헤더 아래 0.4 / bottom 1.0 (bottom은 bf-tbl 래퍼가 긋는다)
  set table(stroke: (x, y) => (
    top: if y == 0 { 1pt + ink } else if y == 1 { 0.4pt + rule-c } else { none },
    bottom: none,
  ))
  show table.cell.where(y: 0): it => text(weight: "semibold", it)
  show table.cell: set par(justify: false)  // 셀 양끝맞춤 파열 방지
  show table.cell: set align(left + horizon)  // 왼끝맞춤(가운데 정렬 금지)
  show link: it => text(fill: accent, it)

  if cover != none { cover }
  // 속표지
  page(header: none, footer: none, {
    v(44mm)
    line(length: 100%, stroke: 0.4pt + rule-c)
    v(7mm)
    align(center, text(font: t.display-font, weight: "semibold", size: 20pt, keep-words(meta.title)))
    if meta.at("subtitle", default: none) != none {
      v(5mm)
      align(center, text(font: ("Noto Serif KR",), size: 11pt, meta.subtitle))
    }
    v(10mm)
    align(center, text(font: t.display-font, weight: "medium", size: 10pt, meta.at("author", default: "")))
  })
  if toc {
    // 앞붙이 쪽번호(i, ii, iii…) · 러닝헤드 없음
    counter(page).update(1)
    // 목차 1행 = 번호칼럼 14mm + 제목 + flex 공백 + 쪽번호 9mm(우측). 리더 점선 없음.
    // 행송 16pt: em 박스가 1em으로 고정(top-edge .8em / bottom-edge -.2em)돼 있으므로
    // 블록 간격 6pt + 본문 10pt = 16pt, 되돌이 줄도 leading 6pt로 같은 행송을 쓴다.
    // bottom-edge: "baseline" — 칼럼 박스의 아래끝을 베이스라인에 맞춘다.
    // (전역 em 박스 고정(bottom-edge -0.2em) 탓에 그냥 두면 박스가 2pt 떠서
    //  번호·쪽번호 베이스라인이 제목과 어긋나고 행송도 16 → 18pt로 벌어진다.)
    // fill을 text()로 직접 박는 이유: 전역 `show link: 별색` 규칙을 안쪽에서 덮기 위함.
    let toc-row(loc, indent: 0mm, num: none, num-font: none, num-fill: ink,
                title: none, page-no: none,
                size: 10pt, weight: "regular", above: 6pt, sticky: false) = block(
      width: 100%, above: above, below: 0pt, sticky: sticky,
      {
        set par(first-line-indent: 0em, hanging-indent: indent + 14mm,
          leading: 16pt - size, spacing: 0pt, justify: false)
        if indent > 0mm { h(indent) }
        link(loc, box(width: 14mm, text(font: num-font, size: size, fill: num-fill,
          weight: weight, bottom-edge: "baseline",
          number-type: "lining", number-width: "tabular", num)))
        link(loc, text(font: t.sans-font, size: size, weight: weight, fill: ink, title))
        h(1fr)
        link(loc, box(width: 9mm, align(right,
          text(font: t.body-font, size: size - 0.5pt, fill: ink, bottom-edge: "baseline",
            number-type: "lining", number-width: "tabular", page-no))))
      })
    page(
      header: none,
      numbering: "i",
      footer: context align(center, text(font: t.sans-font, size: 9pt, fill: ink,
        counter(page).display("i"))),
      {
        v(24mm)
        text(font: t.display-font, weight: "semibold", size: 16pt, tracking: 1em,
          fill: ink, toc-title)
        // 표제 아래 정확히 10mm. 룰을 그냥 놓으면 문단 어센트(0.8em)가 얹혀
        // 실측 12.6mm가 되므로 높이 0 블록에 place로 앉힌다.
        v(10mm)
        block(width: 100%, height: 0pt, above: 0pt, below: 0pt,
          place(top + left, line(length: 100%, stroke: 0.4pt + rule-c)))
        v(6mm)

        // 장: 10.5pt Medium, 번호 칼럼 `제N장`, 장과 장 사이 2.5mm
        show outline.entry.where(level: 1): it => context {
          let loc = it.element.location()
          let n = query(heading.where(level: 1).before(loc, inclusive: true)).len()
          let (embedded, rest) = bf-split-num(bf-plain(it.element.body))
          toc-row(loc,
            num: if embedded == none { "제" + str(n) + "장" } else { embedded },
            num-font: t.sans-font, num-fill: accent,
            title: if embedded == none { it.element.body } else { rest },
            page-no: it.page(),
            size: 10.5pt, weight: "medium", above: 6pt + 2.5mm, sticky: true)
        }

        // 절: 10pt Regular, 14mm 추가 들여쓰기, 번호 `N.M`
        show outline.entry.where(level: 2): it => context {
          let loc = it.element.location()
          let ch = query(heading.where(level: 1).before(loc))
          let cn = ch.len()
          let sn = if cn == 0 {
            query(heading.where(level: 2).before(loc, inclusive: true)).len()
          } else {
            query(heading.where(level: 2)
              .after(ch.last().location()).before(loc, inclusive: true)).len()
          }
          let (embedded, rest) = bf-split-num(bf-plain(it.element.body))
          toc-row(loc,
            indent: 14mm,
            num: if embedded == none { str(cn) + "." + str(sn) } else { embedded },
            num-font: t.body-font, num-fill: ink,
            title: if embedded == none { it.element.body } else { rest },
            page-no: it.page(),
            size: 10pt, weight: "regular", above: 6pt)
        }

        outline(title: none, depth: 2, indent: 0pt)
      })
  }
  counter(page).update(1)
  body
}
