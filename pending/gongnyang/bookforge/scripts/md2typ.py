#!/usr/bin/env python3
"""bookforge: deterministic Markdown(subset) -> Typst fragment converter.

Contract (chapter md):
  - first `# H1` = chapter title (opener rendered via bf-chapter; summary from outline.json)
  - `##`/`###` -> == / ===
  - paragraphs, **bold**, *em*, `code`, fenced code, > quote, lists, GFM tables, links
  - images: ![caption](path "출처: X") -> bf-fig
  - callouts (line-based, nesting depth 1):
      ::: tip 제목텍스트
      body md
      :::
    kinds: info|tip|warn|quote|stat  (stat: first line = value, second = label)
"""
import json, re, sys
from pathlib import Path
from markdown_it import MarkdownIt

MD = MarkdownIt("commonmark").enable("table").enable("strikethrough")

ESC = "\\`#$&_*@<>[]~^"

def esc(text: str) -> str:
    out = []
    for ch in text:
        if ch in ESC:
            out.append("\\" + ch)
        elif ch == "/":
            out.append("\\/")  # avoid `//` comment
        else:
            out.append(ch)
    return "".join(out)

def inline(tokens) -> str:
    """Render markdown-it inline children to typst markup."""
    out = []
    for t in tokens:
        ty = t.type
        if ty == "text":
            out.append(esc(t.content))
        elif ty == "code_inline":
            content = t.content.replace("`", "\\`")
            out.append(f"#raw(\"{content_escape(t.content)}\")")
        elif ty == "strong_open":
            out.append("#strong[")
        elif ty == "strong_close":
            out.append("];")  # ';' terminates the code expr so a following '(' or '[' is not parsed as call args
        elif ty == "em_open":
            out.append("#emph[")
        elif ty == "em_close":
            out.append("];")
        elif ty == "s_open":
            out.append("#strike[")
        elif ty == "s_close":
            out.append("];")
        elif ty == "link_open":
            href = dict(t.attrs).get("href", "")
            out.append(f'#link("{content_escape(href)}")[')
        elif ty == "link_close":
            out.append("];")
        elif ty == "softbreak":
            out.append(" ")
        elif ty == "hardbreak":
            out.append(" \\\n")
        elif ty == "image":
            # inline images are promoted to block figures by block pass; ignore here
            pass
        else:
            if t.content:
                out.append(esc(t.content))
    return "".join(out)

def content_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')

def fig_width_mm(src: str, ctx) -> float | None:
    """도해 사이드카 `bf.width` → `#bf-fig(..., width: Nmm)`에 실을 mm 수치.

    구 구현은 width를 **아예 넘기지 않았다**. 그래서 base.typ:123 `bookfig(..., width: 100%)`
    기본값이 그대로 걸리고 `bf.width: twothirds` 선언이 조판에 도달하지 못했다 — 사이드카는
    render_diagrams.mjs의 pt 환산 기준으로만 쓰이고 지면 폭은 전폭 그대로였다는 뜻이라,
    도해 글자 하한은 2/3폭 기준(예: essay 52mm)으로 재면서 실제로는 88mm로 그렸다.
    HTML 트랙이 2단계에서 없앤 것과 같은 형태의 '제2의 진리원'이며, 여기서는 그 두 번째
    값이 아예 무시되는 쪽으로 나타났다.

    `full`도 수치로 발행한다. 4종 실측에서 `100%`가 판면폭과 정확히 같아 결과는 불변이지만
    (practical 121.000 / academic 106.000 / essay 88.000 / business 132.500mm — 프로브
    PDF 벡터 실측), 그렇게 두면 판면폭이 유일 진리원이고 tokens는 그것을 **추정**하는
    제2의 값으로 남는다. 수치로 발행하면 tokens 하나가 조판과 게이트를 동시에 정하고,
    둘이 갈라지는 순간 지면에서 눈에 보인다(G16-SYNC widths 축이 정적으로도 잡는다).

    사이드카가 없는 이미지(표지 아트 등)는 `None` — 종전대로 `width: 100%`로 떨어진다.
    """
    widths, dg = ctx.get("fig_widths"), ctx.get("diagrams_dir")
    if not isinstance(widths, dict) or dg is None:
        return None
    sidecar = Path(dg) / (Path(src).stem + ".json")
    if not sidecar.exists():
        return None
    try:
        bf = json.loads(sidecar.read_text(encoding="utf-8")).get("bf") or {}
    except (ValueError, OSError):
        return None                       # 사이드카 파손은 render_diagrams가 이미 죽인다
    v = widths.get(bf.get("width") or "full")
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
        return None                       # 값 부재/비수치는 G16-SYNC widths ①이 렌더 전에 막는다
    # W7 배치 높이 상한 — render_diagrams(figFitReport)가 metrics.fit에 내린 축소 폭이
    # 있으면 그 값을 전사한다(HTML 트랙 build_html.fig의 인라인 width와 같은 소비 계약).
    # 진리원은 tokens.diagram.maxHeightMm 하나이고 여기는 결정의 배치 전사일 뿐이다.
    metrics_p = Path(dg).parent / "assets" / (Path(src).stem + ".metrics.json")
    if metrics_p.exists():
        try:
            fit = json.loads(metrics_p.read_text(encoding="utf-8")).get("fit") or {}
        except (ValueError, OSError):
            fit = {}
        fw = fit.get("widthMm")
        if (fit.get("verdict") == "shrunk"
                and isinstance(fw, (int, float)) and not isinstance(fw, bool) and fw > 0):
            return float(fw)
    return float(v)

def render_tokens(tokens, ctx) -> str:
    out, i = [], 0
    while i < len(tokens):
        t = tokens[i]
        ty = t.type
        if ty == "heading_open":
            level = int(t.tag[1])
            content = inline(tokens[i + 1].children or [])
            i += 3
            if level == 1:
                if not ctx["chapter_emitted"]:
                    summary = ctx.get("summary")
                    s = f", summary: [{esc(summary)}]" if summary else ""
                    out.append(f'#bf-chapter("{content_escape(ctx["title_raw"])}"{s})\n')
                    ctx["chapter_emitted"] = True
                # extra H1s demoted
                else:
                    out.append(f"== {content}\n")
            else:
                out.append("=" * min(level, 4) + " " + content + "\n")
            continue
        if ty == "paragraph_open":
            raw_line = (tokens[i + 1].content or "").strip()
            capm = re.match(r"^\[표\]\s*(.+?)(?:\s*\|\s*자료\s*[:：]\s*(.+))?$", raw_line)
            if capm:
                ctx["pending_tbl"] = (capm.group(1).strip(), (capm.group(2) or "").strip() or None)
                i += 3
                continue
            children = tokens[i + 1].children or []
            imgs = [c for c in children if c.type == "image"]
            if imgs and all(c.type in ("image", "softbreak", "text") and (c.type != "text" or not c.content.strip()) for c in children):
                for im in imgs:
                    attrs = dict(im.attrs)
                    src = attrs.get("src", "")
                    title = attrs.get("title", "") or ""
                    cap = inline(im.children or []) or None
                    source = None
                    m = re.match(r"출처\s*[:：]\s*(.+)", title)
                    if m:
                        source = m.group(1).strip()
                    args = [f'"{content_escape(ctx["img_prefix"] + src)}"']
                    if cap:
                        args.append(f"caption: [{cap}]")
                    if source:
                        args.append(f"source: [{esc(source)}]")
                    w = fig_width_mm(src, ctx)
                    if w is not None:
                        args.append(f"width: {w:g}mm")
                    out.append(f'#bf-fig({", ".join(args)})\n')
            else:
                out.append(inline(children) + "\n")
            i += 3
            continue
        if ty == "fence":
            lang = (t.info or "").strip().split()[0] if (t.info or "").strip() else ""
            body = t.content.rstrip("\n")
            fence = "`" * max(3, max((len(m) for m in re.findall(r"`+", body)), default=0) + 1)
            out.append(f"{fence}{lang}\n{body}\n{fence}\n")
            i += 1
            continue
        if ty == "blockquote_open":
            j, depth = i + 1, 1
            while j < len(tokens) and depth:
                if tokens[j].type == "blockquote_open":
                    depth += 1
                elif tokens[j].type == "blockquote_close":
                    depth -= 1
                j += 1
            inner = render_tokens(tokens[i + 1:j - 1], ctx)
            out.append(f"#quote(block: true)[{inner.strip()}]\n")
            i = j
            continue
        if ty in ("bullet_list_open", "ordered_list_open"):
            j, depth = i + 1, 1
            opener = ty
            closer = opener.replace("open", "close")
            while j < len(tokens) and depth:
                if tokens[j].type == opener:
                    depth += 1
                elif tokens[j].type == closer:
                    depth -= 1
                j += 1
            out.append(render_list(tokens[i:j], ctx))
            i = j
            continue
        if ty == "table_open":
            j = i
            while tokens[j].type != "table_close":
                j += 1
            cap = ctx.pop("pending_tbl", None)
            out.append(render_table(tokens[i:j + 1], ctx, cap=cap))
            i = j + 1
            continue
        if ty == "hr":
            out.append("#v(0.6em)#line(length: 30%, stroke: 0.5pt + luma(170))#v(0.6em)\n")
            i += 1
            continue
        i += 1
    return "\n".join(out)

def render_list(tokens, ctx) -> str:
    ordered = tokens[0].type == "ordered_list_open"
    marker = "+" if ordered else "-"
    items, i = [], 1
    while i < len(tokens) - 1:
        if tokens[i].type == "list_item_open":
            j, depth = i + 1, 1
            while depth:
                if tokens[j].type == "list_item_open":
                    depth += 1
                elif tokens[j].type == "list_item_close":
                    depth -= 1
                j += 1
            inner = render_tokens(tokens[i + 1:j - 1], ctx).strip()
            inner = inner.replace("\n", "\n  ")
            items.append(f"{marker} {inner}")
            i = j
        else:
            i += 1
    return "\n".join(items) + "\n"

def render_table(tokens, ctx, cap=None) -> str:
    rows, cur = [], None
    for t in tokens:
        if t.type == "tr_open":
            cur = []
        elif t.type == "tr_close":
            rows.append(cur)
        elif t.type == "inline" and cur is not None:
            cur.append(inline(t.children or []))
    if not rows:
        return ""
    ncol = max(len(r) for r in rows)
    padded = [r + [""] * (ncol - len(r)) for r in rows]
    # 헤더 행은 table.header로 — 긴 표가 쪽을 넘을 때 매 쪽 상단에 반복된다(issue #7)
    head = ", ".join(f"[{c}]" for c in padded[0])
    cells = [f"[{c}]" for r in padded[1:] for c in r]
    # (1fr,)*n — 표 폭 = 판면 폭 100% 강제 (auto 컬럼은 내용 폭만큼만 차지해 우측이 빈다)
    tbl = f"table(columns: (1fr,) * {ncol}, table.header({head})" \
          + ("".join(", " + c for c in cells)) + ")"
    if cap:
        title, source = cap
        args = [f"caption: [{esc(title)}]"]
        if source:
            args.append(f"source: [{esc(source)}]")
        return f"#bf-tbl({', '.join(args)}, {tbl})\n"
    return f"#bf-tbl({tbl})\n"

# statrow는 stat보다 먼저 — 대안 순서가 뒤면 "::: statrow"가 stat(title="row")로 오탐된다
CALLOUT_RE = re.compile(r"^:::\s*(info|tip|warn|quote|statrow|stat|pull|lead|cols)\s*(.*)$")

def split_callouts(md: str):
    """Yield ('md', text) and ('callout', kind, title, body) segments."""
    lines = md.split("\n")
    buf, i = [], 0
    while i < len(lines):
        m = CALLOUT_RE.match(lines[i].strip())
        if m:
            if buf:
                yield ("md", "\n".join(buf))
                buf = []
            kind, title = m.group(1), m.group(2).strip() or None
            body, i = [], i + 1
            while i < len(lines) and lines[i].strip() != ":::":
                body.append(lines[i])
                i += 1
            i += 1
            yield ("callout", kind, title, "\n".join(body))
        else:
            buf.append(lines[i])
            i += 1
    if buf:
        yield ("md", "\n".join(buf))

def convert_chapter(md_path: Path, out_path: Path, title: str, summary: str | None,
                    img_prefix: str = "../../assets/",
                    diagrams_dir: Path | None = None, fig_widths: dict | None = None) -> None:
    """`diagrams_dir`+`fig_widths`(= tokens.diagram.widths)가 주어지면 도해 사이드카의
    `bf.width`를 `#bf-fig(..., width: Nmm)`로 발행한다. 둘 중 하나라도 없으면 종전대로
    width 인자를 생략해 base.typ 기본 `100%`로 떨어진다(단독 CLI 실행 경로)."""
    md = md_path.read_text(encoding="utf-8")
    ctx = {"chapter_emitted": False, "title_raw": title, "summary": summary,
           "img_prefix": img_prefix, "diagrams_dir": diagrams_dir, "fig_widths": fig_widths}
    parts = ['#import "../_style/theme.typ": *\n']
    for seg in split_callouts(md):
        if seg[0] == "md":
            parts.append(render_tokens(MD.parse(seg[1]), ctx))
        else:
            _, kind, title_c, body = seg
            if kind == "stat":
                ls = [l.strip() for l in body.strip().split("\n") if l.strip()]
                value = ls[0] if ls else ""
                label = ls[1] if len(ls) > 1 else ""
                parts.append(f'#bf-stat("{content_escape(value)}", "{content_escape(label)}")\n')
            elif kind == "statrow":
                # 각 행 = "값 | 라벨" — T1 하단 키 스탯 스트립 (business 팩 전용)
                cells = []
                for l in body.strip().split("\n"):
                    if not l.strip():
                        continue
                    value, _, label = l.partition("|")
                    cells.append(f'("{content_escape(value.strip())}", "{content_escape(label.strip())}")')
                parts.append(f'#bf-statrow({", ".join(cells)})\n')
            elif kind in ("lead", "cols"):
                inner = render_tokens(MD.parse(body), ctx).strip()
                parts.append(f'#bf-{kind}[{inner}]\n')
            else:
                if kind == "pull":  # 풀퀘트는 HTML 전용 — Typst 트랙에선 인용으로 강등
                    kind = "quote"
                inner = render_tokens(MD.parse(body), ctx).strip()
                targ = f"title: [{esc(title_c)}], " if title_c else ""
                parts.append(f'#bf-callout(kind: "{kind}", {targ})[{inner}]\n'.replace(", )", ")"))
    if not ctx["chapter_emitted"]:
        s = f", summary: [{esc(summary)}]" if summary else ""
        parts.insert(1, f'#bf-chapter("{content_escape(title)}"{s})\n')
    out_path.write_text("\n".join(parts), encoding="utf-8")

if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    title = sys.argv[3] if len(sys.argv) > 3 else src.stem
    summary = sys.argv[4] if len(sys.argv) > 4 else None
    convert_chapter(src, dst, title, summary)
    print(f"OK {dst}")
