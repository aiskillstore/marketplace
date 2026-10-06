#!/usr/bin/env python3
"""bookforge contrast_contract 누락 린터 (W4-A 5단계).

Usage:
  python3 tests/lint_contrast.py <book_dir> [<book_dir> ...] [--style-dir DIR] [--json OUT]

**이것은 렌더 전 게이트가 아니다.** 입력이 `typeset/book-final.html`(build_html.py:953)이라
빌드를 이미 지불한 뒤에만 성립한다 — 플랜 「핵심 설계 결정」의 "누락 린터는 렌더 전
게이트가 될 수 없다"가 그 계약이다. 렌더 전 축은 G16-CONTRAST(선언된 페어의 대비)가
계속 담당하고, 이 린터는 **그 선언 목록 자체가 실물과 맞는가**를 본다.

세 축 — 적대 검증 보고(w4-step1-adv.md)의 격추 S2·S7·S8을 각각 닫는다.

  ① 페어 완전성 (S2·S7)
     book-final.html의 실제 텍스트 노드마다 유효 fg/bg/pt/bold를 계산하고,
     theme.css의 규칙 중 이 책이 밟지 않은 것은 **가상 요소**로 보강해
     contrast_contract.entries와 양방향 diff한다.
       · CSS에 있는데 계약에 없다     -> MISSING  (S2: 계약을 지우면 조용해지던 구멍)
       · 계약에 있는데 CSS 근거가 없다 -> GHOST    FAIL   (날조 엔트리)
       · 값은 같은데 표기가 갈린다     -> NOTATION (`--paper` 선언 vs CSS `#fff`)
  ② pt 정합 (S8)
     계약이 신고한 pt·bold를 실물과 대조한다. 튜플째 일치하지 않은 엔트리의 pt가
     theme.css의 어떤 font-size에도 없으면 PT_UNATTAINABLE FAIL — 하한을 3.0으로
     자기완화하려고 pt를 14로 올리는 경로가 여기서 죽는다.
  ③ 값 수준 커버리지 (S7)
     theme.css의 모든 `color:` 값이 어떤 엔트리의 fg에, 모든 `background(-color):`
     값이 어떤 엔트리의 bg에 최소 1회 등장하는지. 미등장 = "새 색이 조용히 추가됨" FAIL.
     ①이 원고 의존인 반면 이 축은 CSS만으로 성립하므로, 이 책이 밟지 않은 새 색도 잡는다.

**강도 분기**: ①의 MISSING·NOTATION은 그 페어가 **이 책의 DOM에서 실제로 도출됐을 때만**
FAIL이다. 가상 요소는 조상 사슬을 셀렉터에서 복원한 근사라(`.callout-title`이 실제로
`.callout`(tint) 안에 산다는 것은 CSS만으로 알 수 없다) 근사를 FAIL로 두면 표·콜아웃이
없는 원고에서 오탐이 쏟아진다. 따라서 **전 요소를 밟는 스모크 북에서 돌려야** 완전성
축이 강제력을 갖는다(`references/extending.md` 스모크 북 루프). 축 ③은 원고와 무관하다.

캐스케이드는 **근사**다. 완전한 CSS 엔진을 만들지 않는다 — 이 저장소의 theme.css
2종이 실제로 쓰는 셀렉터 패턴만 지원하고, 지원 밖 패턴은 조용히 넘기지 않고
`미지원 패턴` WARN으로 떨어뜨린다(그래야 새 패턴이 들어올 때 린터가 침묵하지 않는다).

typst 4종(practical·academic·essay·business)은 book-final.html이 없다 —
명시 skip이고 사유를 출력한다.
"""
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))

import g16_tokens as g16   # noqa: E402  대비 산술·색 해석의 단일 진리원

# 굵기 임계. WCAG의 대형 텍스트 예외는 bold=700 기준이고, 그보다 낮게 잡으면
# 10.5pt 이상에서 하한이 4.5 -> 3.0으로 **완화**되므로 보수적 방향(700)을 쓴다.
# 적대 검증 3-2가 "500을 bold로 치지 않는 것은 보수적이라 안전"이라 판정한 것과 같은 방향이다.
# **값은 g16_tokens가 단일 진리원** — 여기(CSS `font-weight` 수치)와 G14-C(PDF 폰트명,
# `g16.is_bold_font`)가 같은 700 기준을 쓴다는 것이 이 import의 계약이다(W4 판정 D6).
BOLD_MIN_WEIGHT = g16.BOLD_MIN_WEIGHT

PT_TOL = 0.01
PX_TO_PT = 0.75          # 96dpi CSS px -> pt
DEFAULT_FONT_PT = 12.0   # 브라우저 기본 16px

# 색을 낳는 프로퍼티만 본다. border-color·outline은 글자가 아니므로 대비 계약 대상이 아니다.
BG_PROPS = ("background", "background-color", "background-image")
INHERITED = ("color", "font-size", "font-weight")

# UA 기본 스타일 최소 집합 — `*{margin:0;padding:0}`은 여백만 지우고 급수·굵기는 남긴다.
# 작성자 규칙보다 항상 낮은 우선순위로 깔린다(specificity 튜플 앞에 origin 0).
UA_DEFAULTS = {
    "h1": {"font-size-em": 2.0, "font-weight": "700"},
    "h2": {"font-size-em": 1.5, "font-weight": "700"},
    "h3": {"font-size-em": 1.17, "font-weight": "700"},
    "h4": {"font-size-em": 1.0, "font-weight": "700"},
    "h5": {"font-size-em": 0.83, "font-weight": "700"},
    "h6": {"font-size-em": 0.67, "font-weight": "700"},
    "b": {"font-weight": "700"},
    "strong": {"font-weight": "700"},
    "th": {"font-weight": "700"},
}

VOID_TAGS = {"br", "meta", "img", "hr", "input", "link", "source", "col", "area", "base"}
# svg 안의 텍스트는 지면 CSS의 사정권이 아니다(도해 라벨은 render_diagrams.mjs의
# minFontPt·alienColors가 따로 담당한다). head/style/script도 렌더 텍스트가 아니다.
SKIP_SUBTREE = {"svg", "style", "script", "head", "title", "meta"}


# ------------------------------------------------------------------ 결과 레코드

def _f(axis, level, code, msg):
    return {"axis": axis, "level": level, "code": code, "msg": msg}


class Unsupported(Exception):
    pass


# --------------------------------------------------------------------- CSS 파싱

def strip_comments(text):
    return re.sub(r"/\*.*?\*/", " ", text, flags=re.S)


def split_top_level(s, sep):
    """괄호 깊이 0에서만 자른다 — `linear-gradient(a, b)`의 콤마를 셀렉터 구분자로
    오인하지 않기 위해서다."""
    out, buf, depth, quote = [], [], 0, None
    for ch in s:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return out


def parse_decls(body):
    out = []
    for chunk in split_top_level(body, ";"):
        chunk = chunk.strip()
        if not chunk or chunk.startswith("@"):
            continue
        i = chunk.find(":")
        if i < 0:
            continue
        prop, val = chunk[:i].strip().lower(), chunk[i + 1:].strip()
        out.append((prop, g16._strip_important(val)))
    return out


def iter_blocks(text):
    """최상위 `prelude { body }` 순회. 중첩 중괄호(@page 안의 @bottom-right)를 센다."""
    i, n = 0, len(text)
    while i < n:
        j = text.find("{", i)
        if j < 0:
            return
        prelude = text[i:j].strip()
        depth, k = 1, j + 1
        while k < n and depth:
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
            k += 1
        yield prelude, text[j + 1:k - 1]
        i = k


class Rule:
    __slots__ = ("selector", "parts", "decls", "order", "pseudo")

    def __init__(self, selector, parts, decls, order):
        self.selector = selector
        self.parts = parts            # [(combinator, Compound), ...]
        self.decls = decls            # {prop: value}
        self.order = order
        self.pseudo = parts[-1][1].pseudo_el


class Compound:
    __slots__ = ("tag", "classes", "ids", "attrs", "pseudo_cls", "pseudo_el")

    def __init__(self):
        self.tag = None
        self.classes = []
        self.ids = []
        self.attrs = []          # (name, op, value)
        self.pseudo_cls = []     # ("nth-child", "odd") 등
        self.pseudo_el = None

    def specificity(self):
        a = len(self.ids)
        b = len(self.classes) + len(self.attrs) + len(self.pseudo_cls)
        c = (1 if self.tag and self.tag != "*" else 0) + (1 if self.pseudo_el else 0)
        return a, b, c


_TOK_RE = re.compile(r"""
    (?P<tag>^[A-Za-z][\w-]*|^\*)
  | (?P<cls>\.[A-Za-z_][\w-]*)
  | (?P<id>\#[A-Za-z_][\w-]*)
  | (?P<attr>\[[^\]]*\])
  | (?P<pe>::[A-Za-z-]+)
  | (?P<pc>:[A-Za-z-]+(?:\([^)]*\))?)
""", re.X)

SUPPORTED_PSEUDO_EL = {"before", "after", "marker"}
SUPPORTED_PSEUDO_CLS = {"root", "first-child", "last-child", "nth-child", "only-child"}


def parse_compound(s):
    c, i = Compound(), 0
    while i < len(s):
        m = _TOK_RE.match(s, i)
        if not m or m.end() == i:
            raise Unsupported(f"컴파운드 토큰 해석 불가: {s!r} @{i}")
        if m.group("tag"):
            c.tag = m.group("tag").lower()
        elif m.group("cls"):
            c.classes.append(m.group("cls")[1:])
        elif m.group("id"):
            c.ids.append(m.group("id")[1:])
        elif m.group("attr"):
            body = m.group("attr")[1:-1].strip()
            am = re.fullmatch(r"([\w-]+)\s*(?:([~|^$*]?=)\s*(.*))?", body)
            if not am:
                raise Unsupported(f"속성 셀렉터 미지원: [{body}]")
            op = am.group(2)
            val = (am.group(3) or "").strip().strip("\"'")
            if op not in (None, "="):
                raise Unsupported(f"속성 연산자 미지원: [{body}]")
            c.attrs.append((am.group(1), op, val))
        elif m.group("pe"):
            name = m.group("pe")[2:].lower()
            if name not in SUPPORTED_PSEUDO_EL:
                raise Unsupported(f"의사요소 미지원: ::{name}")
            c.pseudo_el = name
        else:
            raw = m.group("pc")[1:]
            name = raw.split("(")[0].lower()
            if name not in SUPPORTED_PSEUDO_CLS:
                raise Unsupported(f"의사클래스 미지원: :{raw}")
            arg = raw[len(name) + 1:-1].strip().lower() if "(" in raw else None
            if name == "nth-child" and arg not in ("odd", "even") and not re.fullmatch(r"\d+", arg or ""):
                raise Unsupported(f"nth-child 인자 미지원: :{raw}")
            c.pseudo_cls.append((name, arg))
        i = m.end()
    return c


def parse_selector(sel):
    """`a > b + .c d` -> [(None,a), ('>',b), ('+',.c), (' ',d)]"""
    sel = " ".join(sel.split())
    if "~" in sel:
        raise Unsupported("일반 형제 결합자 `~` 미지원")
    toks = re.split(r"\s*([>+])\s*|\s+", sel)
    toks = [t for t in toks if t]
    parts, comb = [], None
    for t in toks:
        if t in (">", "+"):
            comb = t
            continue
        parts.append((comb if parts else None, parse_compound(t)))
        comb = " "
    if not parts:
        raise Unsupported(f"빈 셀렉터: {sel!r}")
    return parts


def parse_css(text):
    """theme.css -> (rules, unsupported[]). @font-face·@page는 글자색과 무관하므로 건너뛴다."""
    rules, unsup = [], []
    order = [0]

    def walk(chunk):
        for prelude, body in iter_blocks(chunk):
            prelude = prelude.strip()
            if prelude.startswith("@"):
                name = prelude.split()[0].lower()
                if name in ("@media", "@supports"):
                    # 조건을 해석하지 않고 항상 적용으로 근사한다 — 두 theme.css에는
                    # 아직 없으므로 들어오는 순간 이 WARN이 뜬다.
                    unsup.append(f"{prelude} — 조건 미해석(무조건 적용으로 근사)")
                    walk(body)
                elif name not in ("@font-face", "@page", "@charset", "@import"):
                    unsup.append(f"{prelude} — 미지원 at-rule, 통째 무시")
                continue
            decls = dict(parse_decls(body))
            for sel in split_top_level(prelude, ","):
                sel = sel.strip()
                if not sel:
                    continue
                try:
                    parts = parse_selector(sel)
                except Unsupported as e:
                    unsup.append(f"{sel} — {e}")
                    continue
                order[0] += 1
                rules.append(Rule(sel, parts, decls, order[0]))

    walk(strip_comments(text))
    return rules, unsup


# -------------------------------------------------------------------- HTML DOM

class Node:
    __slots__ = ("tag", "attrs", "parent", "children", "texts", "index", "_cs")

    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children = []
        self.texts = []
        self.index = 0
        self._cs = None

    @property
    def classes(self):
        return (self.attrs.get("class") or "").split()

    def path(self):
        out = []
        n = self
        while n is not None and n.tag not in ("html", None):
            cls = "".join("." + c for c in n.classes)
            out.append(f"{n.tag}{cls}")
            n = n.parent
        return " ".join(list(reversed(out))[-4:])


class DomBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("html", {}, None)
        self.stack = [self.root]
        self.skip_depth = 0
        self.skip_tag = None

    def _cur(self):
        return self.stack[-1]

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if self.skip_depth:
            if tag == self.skip_tag:
                self.skip_depth += 1
            return
        if tag in SKIP_SUBTREE:
            self.skip_depth, self.skip_tag = 1, tag
            return
        if tag == "html":
            return
        parent = self._cur()
        n = Node(tag, {k.lower(): (v or "") for k, v in attrs}, parent)
        n.index = len([c for c in parent.children]) + 1
        parent.children.append(n)
        if tag not in VOID_TAGS:
            self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        # skip 중에는 아무것도 하지 않는다 — svg 안의 `<path/>`·`<line/>` 자기닫힘
        # 태그가 여기서 stack.pop()을 부르면 **바깥의 실제 요소가 닫혀** 트리가
        # 통째로 얕아진다(초기 구현의 실버그: body가 자식 1개만 갖게 됐다).
        if self.skip_depth or tag.lower() in SKIP_SUBTREE:
            return
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS and len(self.stack) > 1:
            self.stack.pop()

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.skip_depth:
            if tag == self.skip_tag:
                self.skip_depth -= 1
                if not self.skip_depth:
                    self.skip_tag = None
            return
        if tag in VOID_TAGS or tag == "html":
            return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self.skip_depth or not data.strip():
            return
        self._cur().texts.append(data.strip())


def build_dom(html_text):
    b = DomBuilder()
    b.feed(html_text)
    return b.root


# ------------------------------------------------------------------- 매칭 엔진

def match_compound(node, c, pseudo_ok=True):
    if node is None:
        return False
    if c.tag and c.tag != "*" and node.tag != c.tag:
        return False
    if c.classes:
        cls = set(node.classes)
        if not set(c.classes) <= cls:
            return False
    if c.ids and node.attrs.get("id") not in c.ids:
        return False
    for name, op, val in c.attrs:
        if name not in node.attrs:
            return False
        if op == "=" and node.attrs.get(name) != val:
            return False
    for name, arg in c.pseudo_cls:
        if name == "root":
            if node.parent is not None:
                return False
        elif node.parent is None:
            return False
        else:
            sibs = node.parent.children
            i = sibs.index(node) + 1
            if name == "first-child" and i != 1:
                return False
            if name == "last-child" and i != len(sibs):
                return False
            if name == "only-child" and len(sibs) != 1:
                return False
            if name == "nth-child":
                if arg == "odd" and i % 2 != 1:
                    return False
                if arg == "even" and i % 2 != 0:
                    return False
                if arg not in ("odd", "even") and i != int(arg):
                    return False
    if not pseudo_ok and c.pseudo_el:
        return False
    return True


def match_parts(node, parts):
    """오른쪽에서 왼쪽으로. 자손 결합자는 조상 사슬 전수 시도."""
    comb, comp = parts[-1]
    if not match_compound(node, comp):
        return False
    if len(parts) == 1:
        return True
    rest = parts[:-1]
    if comb == ">":
        return match_parts(node.parent, rest) if node.parent else False
    if comb == "+":
        if not node.parent:
            return False
        sibs = node.parent.children
        i = sibs.index(node)
        return i > 0 and match_parts(sibs[i - 1], rest)
    p = node.parent
    while p is not None:
        if match_parts(p, rest):
            return True
        p = p.parent
    return False


def match_rule(node, rule):
    return match_parts(node, rule.parts)


# ---------------------------------------------------------------- 계산된 스타일

class Engine:
    def __init__(self, rules, ctx, unsup):
        self.rules = rules
        self.ctx = ctx
        self.unsup = unsup


    # --- 값 해석 -------------------------------------------------------
    def _pre_var(self, val):
        """`var(--x, fb)`를 결정 가능한 경우에만 접는다 — `--x`가 선언돼 있으면 fb는
        어떤 캐스케이드에서도 쓰이지 않는다(magazine figcaption의 실사용 패턴)."""
        def rep(m):
            name, fb = m.group(1), m.group(2)
            if name in self.ctx["vars"]:
                return f"var({name})"
            return fb.strip()
        return re.sub(r"var\(\s*(--[\w-]+)\s*,\s*([^()]*(?:\([^()]*\)[^()]*)*)\)", rep, val)

    def resolve(self, val):
        """CSS 값 -> (decl_key, kind, hex|사유).

        decl_key는 **계약 표기와 대조할 형태**다: `var(--ink)` -> `--ink`,
        리터럴 -> `#rrggbb`, 그 밖 -> `~<원문>`.
        """
        v = self._pre_var(val.strip())
        m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", v, re.I)
        if m:
            key = m.group(1)
            kind, res = g16._resolve_token(key, self.ctx)
            return key, kind, res
        if v in ("$key_color", "$key_tint", "$key_label"):
            kind, res = g16._resolve_token(v, self.ctx)
            return v, kind, res
        lit = g16._literal_res(v)
        if lit:
            return (lit[1] if lit[0] == "hex" else "~" + v), lit[0], lit[1]
        return "~" + v, "nonliteral", v

    # --- 캐스케이드 ----------------------------------------------------
    def _declared(self, node):
        """이 요소에 직접 적용되는 선언들(작성자 규칙 + UA 기본). 승자만 남긴다."""
        best = {}
        ua = UA_DEFAULTS.get(node.tag, {})
        for prop, val in ua.items():
            best[prop] = ((0, 0, 0, 0), 0, val)      # origin 0 = UA
        for r in self.rules:
            if r.pseudo:
                continue
            if not match_rule(node, r):
                continue

            spec = (1,) + _sum_spec(r.parts)
            for prop, val in r.decls.items():
                prev = best.get(prop)
                if prev is None or (spec, r.order) >= (prev[0], prev[1]):
                    best[prop] = (spec, r.order, val)
        return {p: v[2] for p, v in best.items()}

    def computed(self, node):
        if node._cs is not None:
            return node._cs
        parent = node.parent
        pcs = self.computed(parent) if parent is not None else {
            "color": ("#000000", "hex", "#000000"),
            "font_pt": DEFAULT_FONT_PT,
            "weight": 400,
            "bg": None,
            "display": "block",
        }
        d = self._declared(node)
        cs = {
            "color": pcs["color"],
            "font_pt": pcs["font_pt"],
            "weight": pcs["weight"],
            "bg": None,
            "display": d.get("display", "").strip().lower() or "block",
            "decls": d,
        }
        if "color" in d:
            cs["color"] = self.resolve(d["color"])
        if "font-size-em" in d and "font-size" not in d:
            cs["font_pt"] = pcs["font_pt"] * float(d["font-size-em"])
        if "font-size" in d:
            pt = parse_len_pt(d["font-size"], pcs["font_pt"])
            if pt is None:
                self.unsup.append(f"font-size 단위 미지원: {d['font-size']!r} @ {node.tag}")
            else:
                cs["font_pt"] = pt
        if "font-weight" in d:
            w = parse_weight(d["font-weight"], pcs["weight"])
            if w is None:
                self.unsup.append(f"font-weight 값 미지원: {d['font-weight']!r} @ {node.tag}")
            else:
                cs["weight"] = w
        cs["bg"] = self._own_bg(d)
        node._cs = cs
        return cs

    def _own_bg(self, decls):
        """이 요소가 스스로 칠하는 배경. 투명이면 None."""
        val = None
        for p in BG_PROPS:
            if p in decls:
                val = decls[p]
        if val is None:
            return None
        v = val.strip()
        if v.lower() in ("none", "transparent", "initial", "unset"):
            return None
        # `background: <color> <나머지>` 축약은 이 저장소에 없다 — 색 하나 또는
        # gradient/url 하나만 온다. 그 밖은 비리터럴로 떨어뜨린다.
        key, kind, res = self.resolve(v)
        if kind == "hex":
            return (key, "hex", res)
        return (key, "nonliteral", res)

    def effective_bg(self, node):
        n = node
        while n is not None:
            cs = self.computed(n)
            if cs["bg"] is not None:
                return cs["bg"]
            n = n.parent
        return ("~page", "nonliteral", "지면 기본 배경(어떤 조상도 배경을 칠하지 않음)")

    def pseudo_style(self, node, rule):
        """의사요소의 계산 스타일 = 원 요소 상속 + 의사 규칙 덮어쓰기."""
        base = self.computed(node)
        d = {}
        for r in self.rules:
            if r.pseudo != rule.pseudo or not match_rule(node, r):
                continue
            spec = (1,) + _sum_spec(r.parts)
            for prop, val in r.decls.items():
                prev = d.get(prop)
                if prev is None or (spec, r.order) >= (prev[0], prev[1]):
                    d[prop] = (spec, r.order, val)
        d = {p: v[2] for p, v in d.items()}
        color = self.resolve(d["color"]) if "color" in d else base["color"]
        pt = base["font_pt"]
        if "font-size" in d:
            got = parse_len_pt(d["font-size"], base["font_pt"])
            if got is not None:
                pt = got
        w = base["weight"]
        if "font-weight" in d:
            got = parse_weight(d["font-weight"], base["weight"])
            if got is not None:
                w = got
        own = self._own_bg(d)
        bg = own if own is not None else self.effective_bg(node)
        return {"color": color, "font_pt": pt, "weight": w, "bg": bg,
                "display": d.get("display", "").strip().lower(), "decls": d}


def _sum_spec(parts):
    a = b = c = 0
    for _, comp in parts:
        x, y, z = comp.specificity()
        a, b, c = a + x, b + y, c + z
    return (a, b, c)


def parse_len_pt(val, parent_pt):
    v = val.strip().lower()
    m = re.fullmatch(r"(-?[\d.]+)(pt|px|mm|em|rem|%)?", v)
    if not m:
        return None
    x = float(m.group(1))
    u = m.group(2) or "px"
    if u == "pt":
        return x
    if u == "px":
        return x * PX_TO_PT
    if u == "mm":
        return x * 72 / 25.4
    if u == "em":
        return x * parent_pt
    if u == "rem":
        return x * DEFAULT_FONT_PT
    if u == "%":
        return x / 100.0 * parent_pt
    return None


def parse_weight(val, parent_w):
    v = val.strip().lower()
    if v == "bold":
        return 700
    if v == "normal":
        return 400
    if v in ("bolder", "lighter", "inherit"):
        return parent_w
    if re.fullmatch(r"\d{3}", v):
        return int(v)
    return None


# ------------------------------------------------------------- 페어 도출

class Pair:
    __slots__ = ("fg_key", "fg_hex", "bg_key", "bg_hex", "pt", "bold", "wheres", "virtual")

    def __init__(self, fg_key, fg_hex, bg_key, bg_hex, pt, bold, where, virtual):
        self.fg_key, self.fg_hex = fg_key, fg_hex
        self.bg_key, self.bg_hex = bg_key, bg_hex
        self.pt, self.bold = pt, bold
        self.wheres = [where]
        self.virtual = virtual

    def key(self):
        return (self.fg_hex, self.bg_hex, round(self.pt, 2), self.bold)

    def label(self):
        return f"{self.fg_key} on {self.bg_key} {self.pt:g}pt{'/bold' if self.bold else ''}"


def _mk_pair(color, bg, pt, weight, where, virtual, warns):
    fg_key, fg_kind, fg_val = color
    bg_key, bg_kind, bg_val = bg
    if fg_kind != "hex":
        warns.append(_f("PAIR", "WARN", "FG_NONLITERAL",
                        f"{where}: 전경 {fg_key} 이 불투명 리터럴이 아님({fg_val}) — "
                        f"정적 대비 산출 불가, 계약 대조 면제(G14-C 픽셀 샘플 소관)"))
        return None
    bg_hex = bg_val if bg_kind == "hex" else "~NONLITERAL"
    return Pair(fg_key, fg_val, bg_key, bg_hex, pt, weight >= BOLD_MIN_WEIGHT, where, virtual)


def collect_pairs(engine, root, rules, warns):
    """DOM 텍스트 노드 + 의사요소 + (이 책이 글자로 밟지 않은 규칙의) 가상 요소.

    도출 집합이 이 책의 DOM에만 묶이면 계약 대조가 원고 의존이 된다 — 같은 스타일
    팩이라도 표가 없는 책에서는 `th` 계약이 유령으로 보인다. 그래서 **theme.css의
    글자 규칙 전량**을 대상으로 삼고, 이 책이 실제로 밟은 것은 실물 문맥에서,
    밟지 않은 것은 셀렉터에서 복원한 가상 문맥에서 계산한다.
    """
    pairs = {}

    def add(p):
        if p is None:
            return
        k = p.key()
        if k in pairs:
            if p.wheres[0] not in pairs[k].wheres:
                pairs[k].wheres.append(p.wheres[0])
            pairs[k].virtual = pairs[k].virtual and p.virtual
        else:
            pairs[k] = p

    dom_nodes, hidden = [], set()

    def collect(node, hid):
        hid = hid or engine.computed(node)["display"] == "none"
        if hid:
            hidden.add(id(node))
        dom_nodes.append(node)
        for ch in list(node.children):
            collect(ch, hid)
    for ch in root.children:
        collect(ch, False)

    # --- ① 실제 텍스트 노드 ---
    for n in dom_nodes:
        if not n.texts or id(n) in hidden:
            continue
        cs = engine.computed(n)
        add(_mk_pair(cs["color"], engine.effective_bg(n), cs["font_pt"],
                     cs["weight"], n.path(), False, warns))

    # --- ② 의사요소 — DOM에 없으므로 CSS 규칙에서 직접 수집한다 ---
    for r in rules:
        if not r.pseudo:
            continue
        if not (r.pseudo == "marker" or "color" in r.decls or "content" in r.decls):
            continue
        host_parts = r.parts[:-1] + [(r.parts[-1][0], _strip_pe(r.parts[-1][1]))]
        hosts = [n for n in dom_nodes if id(n) not in hidden and match_parts(n, host_parts)]
        virtual = not hosts
        if virtual:
            hosts = [make_virtual(root, host_parts, engine)]
        for h in hosts[:1] if virtual else hosts:
            st = engine.pseudo_style(h, r)
            if st["display"] == "none":
                continue
            tag = "" if not virtual else " (이 책 미출현 — 가상 요소)"
            add(_mk_pair(st["color"], st["bg"], st["font_pt"], st["weight"],
                         f"{r.selector} (의사요소){tag}", virtual, warns))

    # --- ③ 이 책이 **글자로** 밟지 않은 규칙 -> 실물(빈 요소) 또는 가상 요소 ---
    for r in rules:
        if r.pseudo:
            continue
        if not ({"color", "font-size", "font-weight"} & set(r.decls)):
            continue      # 글자를 낳지 않는 규칙(레이아웃·배경 전용)은 페어를 만들지 않는다
        if any(n == "root" for _, c in r.parts for n, _ in c.pseudo_cls):
            continue
        hosts = [n for n in dom_nodes if id(n) not in hidden and match_rule(n, r)]
        if any(n.texts for n in hosts):
            continue      # ①이 이미 실문맥으로 도출했다
        if hosts:
            # 실물은 있는데 **직접** 텍스트가 없는 요소는 두 갈래다.
            #   · 급수를 스스로 선언하면 글자 자리다(이 책에서 비었을 뿐 — `.badge`)
            #   · 급수 선언 없이 색만 주면 컨테이너다(`.cover-content`) — 그 색은 자손이
            #     이미 도출하므로 여기서 또 만들면 실재하지 않는 급수의 페어가 생긴다.
            if "font-size" not in r.decls:
                continue
            node, note = hosts[0], " (이 책에서는 빈 요소 — 실문맥 계산)"
        else:
            node, note = make_virtual(root, r.parts, engine), " (이 책 미출현 — 가상 요소)"
        cs = engine.computed(node)
        if cs["display"] == "none":
            continue
        add(_mk_pair(cs["color"], engine.effective_bg(node), cs["font_pt"], cs["weight"],
                     f"{r.selector}{note}", True, warns))

    return list(pairs.values())


def _strip_pe(comp):
    c = Compound()
    c.tag, c.classes, c.ids = comp.tag, comp.classes, comp.ids
    c.attrs, c.pseudo_cls = comp.attrs, comp.pseudo_cls
    return c


_VIRT_CACHE = {}

# HTML이 구조적으로 강제하는 조상 — 셀렉터에 안 적혀 있어도 실제 DOM에는 반드시 있다.
# `.chapter-body th`의 급수를 정하는 것은 `.chapter-body table{font-size:8.95pt}`이므로
# table을 빼고 가상 요소를 만들면 본문 급수(9.5pt)로 잘못 계산된다.
IMPLIED_ANCESTORS = {"th": ("table", "tr"), "td": ("table", "tr"), "tr": ("table",),
                     "li": ("ul",), "code": (), "figcaption": ()}


def make_virtual(root, parts, engine):
    """셀렉터로부터 가상 요소 사슬을 만든다.

    루트 컴파운드가 DOM에 실재하면 **그 실물 아래** 나머지를 매단다 — 조상 배경·상속
    전경이 실제 문맥에서 계산되어야 `.chapter-body blockquote p` 같은 자손 셀렉터의
    배경(tint)이 살아난다. 실재하지 않으면 body 아래에 매단다."""
    key = (id(root), tuple(_comp_sig(c) for _, c in parts))
    if key in _VIRT_CACHE:
        return _VIRT_CACHE[key]
    body = next((c for c in root.children if c.tag == "body"), root)
    anchor, start = body, 0
    first = parts[0][1]
    found = _find_first(root, first)
    if found is not None:
        anchor, start = found, 1
    node = anchor
    for _, comp in parts[start:]:
        for want in IMPLIED_ANCESTORS.get(comp.tag or "", ()):
            n, has = node, False
            while n is not None:
                if n.tag == want:
                    has = True
                    break
                n = n.parent
            if not has:
                mid = Node(want, {}, node)
                node.children.append(mid)
                node = mid
        attrs = {}
        if comp.classes:
            attrs["class"] = " ".join(comp.classes)
        if comp.ids:
            attrs["id"] = comp.ids[0]
        for name, op, val in comp.attrs:
            attrs[name] = val if op == "=" else "x"
        child = Node(comp.tag or "div", attrs, node)
        node.children.append(child)
        node = child
    _VIRT_CACHE[key] = node
    return node


def _comp_sig(c):
    return (c.tag, tuple(c.classes), tuple(c.ids), tuple(c.attrs), tuple(c.pseudo_cls), c.pseudo_el)


def _find_first(root, comp):
    stack = [root]
    while stack:
        n = stack.pop(0)
        if n is not root and match_compound(n, comp, pseudo_ok=False):
            return n
        stack.extend(n.children)
    return None


# ------------------------------------------------------------- 계약 대조

def entry_keys(entry, engine):
    """계약 엔트리 -> (decl_key, hex|'~NONLITERAL')"""
    out = []
    for side in ("fg", "bg"):
        v = entry.get(side)
        if not isinstance(v, str):
            out.append((None, None))
            continue
        if v.startswith("~"):
            out.append((v, "~NONLITERAL"))
            continue
        kind, res = g16._resolve_token(v, engine.ctx)
        out.append((v if (v.startswith("--") or v.startswith("$")) else (res if kind == "hex" else v),
                    res if kind == "hex" else "~NONLITERAL"))
    return out


def norm_decl(k):
    """표기 비교용 정규화 — 리터럴은 소문자 6자리, 토큰명은 그대로."""
    if k is None:
        return None
    if k.startswith("--") or k.startswith("$") or k.startswith("~"):
        return k
    return g16.norm_hex(k) or k


def axis_pairs(style, entries, pairs, engine):
    out = []
    ent = []
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            continue
        (fk, fh), (bk, bh) = entry_keys(e, engine)
        pt = e.get("pt")
        ent.append({
            "i": i, "e": e, "fg_key": fk, "fg_hex": fh, "bg_key": bk, "bg_hex": bh,
            "pt": float(pt) if isinstance(pt, (int, float)) and not isinstance(pt, bool) else None,
            "bold": bool(e.get("bold")),
            "stamp": e.get("source") == "stamp",
            "hit": False,
        })

    def tuple_eq(en, p):
        if en["pt"] is None:
            return False
        if abs(en["pt"] - p.pt) > PT_TOL or en["bold"] != p.bold:
            return False
        if en["fg_hex"] != p.fg_hex:
            return False
        return en["bg_hex"] == p.bg_hex or (en["bg_hex"] == "~NONLITERAL" and p.bg_hex == "~NONLITERAL")

    # --- CSS -> 계약 (누락) ---
    # 실문맥(이 책의 DOM)에서 도출된 페어만 FAIL이다. 가상 요소는 조상 사슬을
    # 셀렉터에서 **복원**한 근사라 배경·상속 급수가 실제와 다를 수 있다
    # (`.callout-title`은 실제로 `.callout`(tint) 안에 살지만 셀렉터만으로는 알 수 없다).
    # 근사를 FAIL로 두면 표·콜아웃이 없는 원고에서 오탐이 쏟아진다 — 그래서
    # **린터는 전 요소를 밟는 스모크 북에서 돌려야** 완전성 축이 강제력을 갖는다.
    for p in pairs:
        hits = [en for en in ent if not en["stamp"] and tuple_eq(en, p)]
        lv, sfx = ("WARN", "_VIRTUAL") if p.virtual else ("FAIL", "")
        if not hits:
            note = " (가상 문맥 근사 — 실문맥 확인 필요)" if p.virtual else ""
            out.append(_f("PAIR", lv, "MISSING" + sfx,
                          f"[{style}] 계약 누락: {p.label()}{note} — {' / '.join(p.wheres[:3])}"))
            continue
        for en in hits:
            en["hit"] = True
            en["hit_real"] = en.get("hit_real") or not p.virtual
        # 표기 드리프트: 값은 같은데 계약이 토큰명, CSS는 리터럴(또는 그 반대)
        for en in hits:
            for side, ek, pk in (("fg", en["fg_key"], p.fg_key), ("bg", en["bg_key"], p.bg_key)):
                a, b = norm_decl(ek), norm_decl(pk)
                if a == b or (a or "").startswith("~") or (b or "").startswith("~"):
                    continue
                out.append(_f("PAIR", lv, "NOTATION" + sfx,
                              f"[{style}] entries[{en['i']}] ({en['e'].get('where', '?')}) "
                              f"{side}={ek!r} 선언, theme.css 실물은 {pk!r} — 값은 같지만 표기가 갈린다. "
                              f"토큰을 바꾸면 계약만 따라 움직인다"))
    return out, ent


def axis_pt(style, ent, pairs, font_pts):
    """② pt 정합 (S8) — 계약이 신고한 pt·bold를 theme.css 실물과 대조.

    pt가 실물과 맞는 엔트리는 ①에서 이미 튜플째로 일치했다. 여기서 보는 것은
    **일치하지 않은 엔트리의 pt가 애초에 도달 가능한 값인가**다.

    강도 분기의 근거: "같은 색 조합인데 급수가 다르다"만으로는 위조를 단정할 수 없다
    (그 색 조합을 쓰는 다른 자리가 이 원고에 없을 뿐일 수 있다 — 콜아웃 없는 원고의
    `.callout h2`). 반면 **theme.css의 어떤 font-size에도 없는 pt**는 어떤 자리로도
    설명되지 않으므로 위조이거나 부패다. 9.5 -> 14 위조가 정확히 이 경로로 잡힌다.
    """
    out = []
    for en in ent:
        if en["hit"] or en["stamp"] or en["pt"] is None:
            continue
        same = [p for p in pairs if p.fg_hex == en["fg_hex"] and p.bg_hex == en["bg_hex"]]
        if not same:
            continue
        attainable = any(abs(en["pt"] - x) <= PT_TOL for x in font_pts)
        real = [p for p in same if not p.virtual]
        got = sorted({(round(p.pt, 2), p.bold) for p in (real or same)})
        got_s = ", ".join("%g pt%s" % (a, "/bold" if b else "") for a, b in got)
        decl_s = "%g pt%s" % (en["pt"], "/bold" if en["bold"] else "")
        en["pt_flagged"] = True
        if not attainable:
            out.append(_f("PT", "FAIL", "PT_UNATTAINABLE",
                          f"[{style}] entries[{en['i']}] ({en['e'].get('where', '?')}) "
                          f"선언 {decl_s} — theme.css의 어떤 `font-size`에도 없는 급수다"
                          f"(같은 색 조합 실측: {got_s}). pt는 하한(contrast_floor)의 입력이라 "
                          f"위조하면 계약이 스스로 하한을 낮춘다"))
        else:
            out.append(_f("PT", "WARN", "PT_UNEXERCISED",
                          f"[{style}] entries[{en['i']}] ({en['e'].get('where', '?')}) "
                          f"선언 {decl_s} — 이 원고는 그 자리를 밟지 않았다"
                          f"(같은 색 조합 실측: {got_s}). 급수 자체는 theme.css에 실재"))
    return out


def axis_ghost(style, ent, engine, css_colors, css_bgs, font_pts):
    """근거 없는 엔트리(유령) 판정. pt 불일치로 이미 지목된 것은 중복 보고하지 않는다."""
    out = []
    for en in ent:
        if en["hit"] or en["stamp"] or en.get("pt_flagged"):
            continue
        why = []
        if en["fg_hex"] not in css_colors:
            why.append(f"fg {en['fg_key']}({en['fg_hex']})가 theme.css의 어떤 `color:`에도 없음")
        if en["bg_hex"] != "~NONLITERAL" and en["bg_hex"] not in css_bgs:
            why.append(f"bg {en['bg_key']}({en['bg_hex']})가 theme.css의 어떤 `background:`에도 없음")
        if en["pt"] is not None and not any(abs(en["pt"] - x) <= PT_TOL for x in font_pts):
            why.append(f"pt {en['pt']:g}가 theme.css의 어떤 `font-size`에도 없음")
        if why:
            out.append(_f("PAIR", "FAIL", "GHOST",
                          f"[{style}] entries[{en['i']}] ({en['e'].get('where', '?')}) 유령 엔트리 — "
                          + " · ".join(why)))
        else:
            out.append(_f("PAIR", "WARN", "UNEXERCISED",
                          f"[{style}] entries[{en['i']}] ({en['e'].get('where', '?')}) — "
                          f"성분(색·급수)은 theme.css에 실재하나 이 책의 DOM·가상요소로는 "
                          f"그 조합을 재현하지 못했다(변형 클래스 조합 등). 성분 근거만 확인"))
    return out


def axis_coverage(style, entries, engine, css_colors, css_bgs, color_src, bg_src):
    """③ 값 수준 커버리지 — 새 색이 조용히 추가되는 경로 봉쇄."""
    out = []
    fg_hexes, bg_hexes = set(), set()
    for e in entries:
        if not isinstance(e, dict):
            continue
        (fk, fh), (bk, bh) = entry_keys(e, engine)
        fg_hexes.add(fh)
        bg_hexes.add(bh)
    for h in sorted(css_colors):
        if h not in fg_hexes:
            out.append(_f("COVERAGE", "FAIL", "FG_UNCOVERED",
                          f"[{style}] theme.css `color: {h}`가 어떤 계약 엔트리의 fg에도 없음 "
                          f"— {', '.join(sorted(color_src[h])[:3])}"))
    for h in sorted(css_bgs):
        if h not in bg_hexes:
            out.append(_f("COVERAGE", "FAIL", "BG_UNCOVERED",
                          f"[{style}] theme.css `background: {h}`가 어떤 계약 엔트리의 bg에도 없음 "
                          f"— {', '.join(sorted(bg_src[h])[:3])}"))
    return out


def axis_stamp(style, ent, style_dir):
    """source:"stamp" 엔트리는 DOM 대조를 면제하되 decorate.py 실재를 확인한다."""
    out = []
    stamps = [en for en in ent if en["stamp"]]
    if not stamps:
        return out
    dec = Path(style_dir) / "decorate.py"
    if not dec.exists():
        out.append(_f("STAMP", "FAIL", "NO_DECORATE",
                      f"[{style}] source:\"stamp\" 엔트리 {len(stamps)}건이 있으나 "
                      f"{dec}가 없다"))
        return out
    text = dec.read_text(encoding="utf-8")
    consts = {}
    for m in re.finditer(r"^([A-Z][A-Z0-9_]*)\s*=\s*\(\s*0x([0-9a-fA-F]{2})\s*/\s*255\s*,"
                         r"\s*0x([0-9a-fA-F]{2})\s*/\s*255\s*,\s*0x([0-9a-fA-F]{2})\s*/\s*255\s*\)",
                         text, re.M):
        consts[m.group(1)] = "#" + "".join(m.group(i).lower() for i in (2, 3, 4))
    sizes = {float(m.group(1)) for m in re.finditer(r"fontsize\s*=\s*([\d.]+)", text)}
    for en in stamps:
        where = en["e"].get("where", "")
        names = [n for n in consts if re.search(rf"\b{n}\b", where)]
        if not names:
            out.append(_f("STAMP", "FAIL", "NO_CONST",
                          f"[{style}] entries[{en['i']}] ({where}) — where가 지목하는 색 상수를 "
                          f"decorate.py에서 찾지 못했다(모듈 상수: {', '.join(sorted(consts)) or '없음'})"))
            continue
        hexes = {consts[n] for n in names}
        if en["fg_hex"] not in hexes:
            out.append(_f("STAMP", "FAIL", "CONST_MISMATCH",
                          f"[{style}] entries[{en['i']}] ({where}) fg={en['fg_key']} "
                          f"{en['fg_hex']} != decorate.py {'/'.join(sorted(hexes))}"))
        if en["pt"] is not None and not any(abs(en["pt"] - s) <= PT_TOL for s in sizes):
            out.append(_f("STAMP", "FAIL", "SIZE_MISSING",
                          f"[{style}] entries[{en['i']}] ({where}) pt={en['pt']:g}가 "
                          f"decorate.py의 fontsize= 값 {sorted(sizes)}에 없음"))
    return out


# ------------------------------------------------------------------ 러너

def css_value_sets(rules, engine, warns):
    """theme.css가 실제로 칠하는 글자색·배경색 집합(+출처 셀렉터)과 font-size 집합."""
    colors, bgs, pts = set(), set(), set()
    csrc, bsrc = {}, {}
    for r in rules:
        if "color" in r.decls:
            key, kind, res = engine.resolve(r.decls["color"])
            if kind == "hex":
                colors.add(res)
                csrc.setdefault(res, set()).add(r.selector)
            else:
                warns.append(_f("COVERAGE", "WARN", "FG_NONLITERAL_DECL",
                                f"`color: {r.decls['color']}` @ {r.selector} — 불투명 리터럴이 "
                                f"아니라 커버리지 대상 밖({res})"))
        for p in BG_PROPS:
            if p not in r.decls:
                continue
            v = r.decls[p].strip()
            if v.lower() in ("none", "transparent", "initial", "unset"):
                continue
            key, kind, res = engine.resolve(v)
            if kind == "hex":
                bgs.add(res)
                bsrc.setdefault(res, set()).add(r.selector)
            else:
                warns.append(_f("COVERAGE", "WARN", "BG_NONLITERAL_DECL",
                                f"`{p}: {v}` @ {r.selector} — 리터럴 색이 아니라 커버리지 "
                                f"대상 밖(계약은 `~` 표기로 선언한다)"))
        if "font-size" in r.decls:
            pt = parse_len_pt(r.decls["font-size"], DEFAULT_FONT_PT)
            if pt is not None:
                pts.add(round(pt, 2))
    return colors, bgs, pts, csrc, bsrc


def lint_book(book_dir, style_dir_override=None):
    book_dir = Path(book_dir)
    res = {"book": str(book_dir), "skipped": None, "findings": [], "unsupported": [],
           "pairs": 0, "entries": 0}
    bj = book_dir / "book.json"
    if not bj.exists():
        res["skipped"] = f"book.json 없음 — {bj}"
        return res
    book = json.loads(bj.read_text(encoding="utf-8"))
    style = book.get("style")
    res["style"] = style
    style_dir = Path(style_dir_override) if style_dir_override else (SKILL / "styles" / style)
    html = book_dir / "typeset" / "book-final.html"
    if not html.exists():
        res["skipped"] = (f"typeset/book-final.html 없음 — engine=typst 스타일({style})은 "
                          f"HTML DOM이 존재하지 않아 페어 도출이 원리적으로 불가하다. "
                          f"이 축은 HTML 트랙 전용(플랜 전제교정 ③)")
        return res
    tokens = json.loads((style_dir / "tokens.json").read_text(encoding="utf-8"))
    theme_text = (style_dir / "theme.css").read_text(encoding="utf-8")
    ctx = g16._ctx(tokens, theme_text, book.get("brand"))

    rules, unsup_sel = parse_css(theme_text)
    res["unsupported"] = list(unsup_sel)
    engine = Engine(rules, ctx, res["unsupported"])
    root = build_dom(html.read_text(encoding="utf-8"))

    warns = []
    pairs = collect_pairs(engine, root, rules, warns)
    res["pairs"] = len(pairs)

    cc = tokens.get("contrast_contract")
    if not isinstance(cc, dict) or not isinstance(cc.get("entries"), list):
        res["findings"].append(_f("PAIR", "FAIL", "NO_CONTRACT",
                                  f"[{style}] tokens.json에 contrast_contract.entries가 없다 — "
                                  f"DOM에서 {len(pairs)}개 페어가 도출되는데 계약이 0건이다"))
        res["findings"] += warns
        return res
    entries = cc["entries"]
    res["entries"] = len(entries)

    colors, bgs, pts, csrc, bsrc = css_value_sets(rules, engine, warns)
    f_pairs, ent = axis_pairs(style, entries, pairs, engine)
    f_pt = axis_pt(style, ent, pairs, pts)
    f_ghost = axis_ghost(style, ent, engine, colors, bgs, pts)
    f_cov = axis_coverage(style, entries, engine, colors, bgs, csrc, bsrc)
    f_stamp = axis_stamp(style, ent, style_dir)
    res["findings"] = f_pairs + f_pt + f_ghost + f_cov + f_stamp + warns
    res["derived"] = [{"fg": p.fg_key, "bg": p.bg_key, "pt": p.pt, "bold": p.bold,
                       "virtual": p.virtual, "where": p.wheres} for p in
                      sorted(pairs, key=lambda x: (x.fg_key, x.bg_key, x.pt))]
    return res


def main():
    ap = argparse.ArgumentParser(description="contrast_contract 누락 린터")
    ap.add_argument("books", nargs="+", help="빌드된 book_dir (typeset/book-final.html 필요)")
    ap.add_argument("--style-dir", help="스타일 팩 디렉토리 override(감도 검증용 임시 사본)")
    ap.add_argument("--json", help="결과 JSON 경로")
    ap.add_argument("--quiet", action="store_true", help="WARN 상세 생략")
    a = ap.parse_args()

    allres, nf, nw = [], 0, 0
    for b in a.books:
        _VIRT_CACHE.clear()
        r = lint_book(b, a.style_dir)
        allres.append(r)
        name = Path(b).name
        if r["skipped"]:
            print(f"\n=== {name}  SKIP\n    사유: {r['skipped']}")
            continue
        fails = [x for x in r["findings"] if x["level"] == "FAIL"]
        wrn = [x for x in r["findings"] if x["level"] == "WARN"]
        nf += len(fails)
        nw += len(wrn)
        print(f"\n=== {name}  style={r['style']}  도출 페어 {r['pairs']} · 계약 엔트리 {r['entries']}")
        print(f"    FAIL {len(fails)} · WARN {len(wrn)} · 미지원 패턴 {len(r['unsupported'])}")
        for x in fails:
            print(f"    FAIL [{x['code']}] {x['msg']}")
        if not a.quiet:
            for x in wrn:
                print(f"    WARN [{x['code']}] {x['msg']}")
            for u in r["unsupported"]:
                print(f"    WARN [UNSUPPORTED] {u}")
    print(f"\n합계: FAIL {nf} · WARN {nw}")
    if a.json:
        Path(a.json).write_text(json.dumps(allres, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if nf else 0


if __name__ == "__main__":
    sys.exit(main())
