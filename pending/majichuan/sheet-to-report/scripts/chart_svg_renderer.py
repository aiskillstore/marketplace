"""SVG presentation of a verified chart-spec/1 projection; no evidence computation."""
from __future__ import annotations

from html import escape
import math
import unicodedata

COLORS = ("#24528a", "#a46714", "#72559b", "#167565", "#527481", "#875047")
NEGATIVE = "#b94735"
INK = "#263341"
MUTED = "#596777"
GRID = "#e0e5ec"
WIDTH = 1000

CSS = """
.charts>figure.chart-spec{grid-column:1/-1;padding:26px 30px}
.chart-spec .chart-canvas{overflow-x:auto;overscroll-behavior-x:contain}
.chart-spec svg{max-height:none;width:100%;height:auto;min-width:680px;font-family:inherit}
.chart-spec .chart-axis{fill:#596777;font-size:14px}
.chart-spec .chart-label{fill:#263341;font-size:15px}
.chart-spec .chart-value{fill:#263341;font-size:14px;font-variant-numeric:tabular-nums}
.chart-spec .chart-unit{fill:#596777;font-size:14px}
.chart-spec .chart-legend{display:flex;flex-wrap:wrap;gap:10px 24px;margin:4px 0 14px;font-size:13px;color:#263341}
.chart-spec .chart-legend span{display:inline-flex;align-items:center;gap:7px}
.chart-spec .chart-legend i{width:14px;height:14px;display:inline-block;flex:none}
.chart-spec .chart-note{font-size:13px;margin-top:12px}
.chart-spec details{padding:8px 0 0;margin:10px 0 0}
.chart-spec .chart-values summary{font-size:13px;color:#24528a}
.chart-spec .chart-values th,.chart-spec .chart-values td{white-space:normal;overflow-wrap:anywhere}
@media(max-width:720px){.charts>figure.chart-spec{padding:18px 12px}}
@media print{.charts>figure.chart-spec{padding:14px;max-width:none}.chart-spec svg{min-width:0;max-height:none}.chart-spec .chart-canvas{overflow:visible}}
"""


def number(value):
    if value is None:
        return "缺期"
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def _tick(value):
    if abs(value) >= 100000000:
        return number(value / 100000000) + "亿"
    if abs(value) >= 10000:
        return number(value / 10000) + "万"
    if 0 < abs(value) < .01:
        return f"{value:.2g}"
    return number(value)


def _wrap(value, columns):
    """Wrap by approximate glyph width, retaining every character."""
    lines, line, width = [], "", 0
    for char in str(value):
        size = 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1
        if char == "\n" or width + size > columns:
            lines.append(line)
            line, width = "", 0
        if char != "\n":
            line += char
            width += size
    if line or not lines:
        lines.append(line)
    return lines


def _label_width(value, font_size=15):
    """Conservative width budget for the shipped CJK/system font stack."""
    def em(char):
        if unicodedata.east_asian_width(char) in {"W", "F"} or char in "MWmw@":
            return 1.1
        if char.isspace():
            return .5
        if char.isascii():
            return .9 if char.isupper() else .75
        return 1.1
    return sum(em(char)*font_size for char in value)


def _wrap_label(value, available_width):
    # Keep every character. Prefer a word boundary, but split long tokens safely.
    lines, line = [], ""
    for char in str(value):
        if char == "\n":
            lines.append(line)
            line = ""
            continue
        if line and _label_width(line+char) > available_width:
            cut = line.rfind(" ")+1
            if cut < len(line)/2:
                cut = len(line)
            lines.append(line[:cut])
            line = line[cut:]
        line += char
    if line or not lines:
        lines.append(line)
    return lines


def _text(x, y, value, cls="chart-axis", anchor="start", wrap=None, lines=None):
    lines = lines if lines is not None else (_wrap(value, wrap) if wrap else [str(value)])
    content = "".join(f'<tspan x="{x:.3f}" dy="{0 if i == 0 else 19}">{escape(line)}</tspan>' for i, line in enumerate(lines))
    return f'<text x="{x:.3f}" y="{y:.3f}" class="{cls}" text-anchor="{anchor}">{content}</text>'


def _scale(values, start, stop, zero=True):
    values = [v for v in values if v is not None]
    if not values:
        raise ValueError("图形没有可展示数值")
    low, high = min(values), max(values)
    if zero:
        low, high = min(0, low), max(0, high)
    if low == high:
        pad = abs(low) * .1 or 1
        low, high = (0, pad) if low == 0 else (low-pad, high+pad)
    raw_step = (high-low)/5
    power = 10 ** math.floor(math.log10(raw_step))
    step = next(n for n in (1, 2, 2.5, 5, 10) if n*power >= raw_step) * power
    low, high = math.floor(low/step)*step, math.ceil(high/step)*step
    ticks = [low+i*step for i in range(round((high-low)/step)+1)]
    return lambda value: start+(value-low)/(high-low)*(stop-start), ticks


def _line(x1, y1, x2, y2, color=GRID, cls="chart-grid", dashed=False):
    return f'<line class="{cls}" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="{1.4 if cls == "zero-axis" else 1}"'+(' stroke-dasharray="4 4"' if dashed else '')+'/>'


def _rect(x, y, width, height, color, value, index, series=0, role="bar"):
    return f'<rect class="data-mark {role}" data-index="{index}" data-series="{series}" data-value="{value}" x="{x:.3f}" y="{y:.3f}" width="{max(0, width):.3f}" height="{max(0, height):.3f}" fill="{color}"/>'


def _color(view, index, value, series=0):
    if value < 0:
        return NEGATIVE
    highlights = view.get("highlight", [])
    if highlights and view["labels"][index] not in highlights:
        return "#8fa6be" if series == 0 else COLORS[series % len(COLORS)]
    return COLORS[series % len(COLORS)]


def _axis_y(scale, ticks, left, right, top, bottom):
    marks = []
    for value in ticks:
        y = scale(value)
        marks.append(_line(left, y, right, y, MUTED if value == 0 else GRID, "zero-axis" if value == 0 else "chart-grid"))
        marks.append(_text(left-12, y+5, _tick(value), anchor="end"))
    marks.append(_line(left, top, left, bottom, MUTED, "chart-axis-line"))
    return marks


def _horizontal(view):
    labels, series = view["labels"], view["series"]
    paired = view["kind"] == "paired"
    left, right = 245, 850
    label_right, label_left = left-18, 14
    label_lines = [_wrap_label(label, label_right-label_left) for label in labels]
    row_heights = [max(48, len(lines)*19+20) for lines in label_lines]
    height = 105+sum(row_heights)
    top, bottom = 58, height-46
    marks = []
    panels = [(left, 560), (650, 965)] if paired else [(left, right)]
    for j, (x0, x1) in enumerate(panels):
        s = series[j]
        scale, ticks = _scale(s["values"], x0+12, x1-48)
        marks.append(_text(x0, 19, f'{s["label"]}（{s["unit"]}）', "chart-unit"))
        for value in ticks:
            xx = scale(value)
            marks.append(_line(xx, top-8, xx, bottom+3, MUTED if value == 0 else GRID, "zero-axis" if value == 0 else "chart-grid"))
            marks.append(_text(xx, bottom+25, _tick(value), anchor="middle"))
        y = top
        for i, (label, value, row_height) in enumerate(zip(labels, s["values"], row_heights)):
            center = y+row_height/2
            if j == 0:
                lines = label_lines[i]
                marks.append(_text(label_right, center+5-(len(lines)-1)*9.5, label, "chart-label", "end", lines=lines))
            zero, end = scale(0), scale(value)
            marks.append(_rect(min(zero, end), center-13, abs(end-zero), 26, _color(view, i, value), value, i, j))
            # Values sit above the bar to remain inside each independent panel.
            marks.append(_text(max(x0, min(end, x1)), center-18, number(value), "chart-value", "end" if value < 0 else "start"))
            y += row_height
    return marks, height


def _vertical(view):
    labels, series, kind = view["labels"], view["series"], view["kind"]
    grouped, stacked, waterfall, histogram = kind == "grouped", kind == "stacked", kind == "waterfall", kind == "histogram"
    left, right, top, bottom = 100, 960, 52, 355
    label_columns = max(5, min(24, int((right-left)/max(1, len(labels))/8)))
    label_rows = max(len(_wrap(label, label_columns)) for label in labels)
    height = bottom+60+label_rows*19
    values = [v for s in series for v in s["values"]]
    if stacked:
        values = [v for s in series for v in s["bases"]+s["ends"]]
    elif waterfall:
        values = view["bases"]+view["ends"]
    scale, ticks = _scale(values, bottom, top)
    marks = _axis_y(scale, ticks, left, right, top, bottom)
    value_labels = []
    axis_title = (f'单位：{series[0]["unit"]}' if series[0]["unit"] else "数值") if grouped or stacked else f'{series[0]["label"]}（{series[0]["unit"]}）'
    marks.append(_text(left, 22, axis_title, "chart-unit"))
    band = (right-left)/len(labels)
    time_positions = None
    if view["axes"]["x"]["scale"] == "time":
        xs = view["x_values"]
        gap = min((b-a for a,b in zip(xs,xs[1:])), default=1)
        span = xs[-1]-xs[0]+gap
        time_positions = [left+(x-xs[0]+gap/2)/span*(right-left) for x in xs]
        band = gap/span*(right-left)
    xbin = None
    if histogram:
        lower, upper = view["bin_lower"][0], view["bin_upper"][-1]
        xbin = lambda v: left+(v-lower)/(upper-lower)*(right-left)
    for i, label in enumerate(labels):
        cx = left+band*(i+.5)
        if time_positions is not None:
            cx = time_positions[i]
        if histogram:
            x0, x1 = xbin(view["bin_lower"][i]), xbin(view["bin_upper"][i])
            cx = (x0+x1)/2
        if not histogram:
            marks.append(_text(cx, bottom+45, label, "chart-axis", "middle", label_columns))
        if waterfall and i < len(labels)-1:
            marks.append(_line(cx+band*.31, scale(view["ends"][i]), cx+band*.69, scale(view["ends"][i]), MUTED, "waterfall-connector", True))
        for j, s in enumerate(series):
            value = s["values"][i]
            if value is None:
                if j == 0:
                    marks.append(_text(cx, bottom-10, "缺期", "chart-axis", "middle"))
                continue
            base, end = 0, value
            if stacked:
                base, end = s["bases"][i], s["ends"][i]
            elif waterfall:
                base, end = view["bases"][i], view["ends"][i]
            bar_width = min(100, band*.62)
            xx = cx-bar_width/2
            if grouped:
                bar_width = min(50, band*.76/len(series))
                xx = cx-len(series)*bar_width/2+j*bar_width+1
                bar_width -= 2
            elif histogram:
                xx, bar_width = x0+1, x1-x0-2
            y0, y1 = scale(base), scale(end)
            color = _color(view, i, value, j)
            role = view["roles"][i] if waterfall else "bar"
            if waterfall and role == "delta" and value > 0:
                color = COLORS[3]
            marks.append(_rect(xx, min(y0, y1), bar_width, abs(y0-y1), color, value, i, j, role))
            if stacked:
                if abs(y0-y1) >= 28:
                    marks.append(_text(xx+bar_width/2, (y0+y1)/2+5, number(value), "chart-value", "middle").replace('class="chart-value"', 'class="chart-value" style="fill:white"'))
            else:
                offset_y = min(y0, y1)-9 if value >= 0 else max(y0, y1)+20
                if waterfall and role == "delta":
                    offset_y = min(y0, y1)-9
                # Compact display only; exact values remain in data marks and the table.
                label = (f'{value/100000000:.1f}亿' if abs(value)>=100000000 else
                         f'{value/10000:.1f}万' if abs(value)>=10000 else number(value))
                text = ("+" if waterfall and role == "delta" and value > 0 else "")+label
                value_labels.append(_text(xx+bar_width/2, offset_y, text, "chart-value", "middle"))
    # Later series must never paint over an earlier series' label.
    marks.extend(value_labels)
    if histogram:
        for boundary in [*view["bin_lower"], view["bin_upper"][-1]]:
            xx = xbin(boundary)
            marks.append(_line(xx,bottom,xx,bottom+6,MUTED,"chart-axis-tick"))
            marks.append(_text(xx,bottom+30,number(boundary),anchor="middle"))
    axis = view["axes"]["x"]
    marks.append(_text((left+right)/2, height-9, axis["label"]+(f'（{axis["unit"]}）' if axis["unit"] else ""), "chart-unit", "middle"))
    return marks, height


def _xy(view):
    labels, s, kind = view["labels"], view["series"][0], view["kind"]
    left, right, top, bottom, height = 100, 950, 52, 350, 430
    axis = view["axes"]["x"]
    if axis["scale"] != "linear":
        height = max(height, bottom+60+max(len(_wrap(label,14)) for label in labels)*19)
    values, xs = s["values"], view["x_values"]
    scale_y, ticks = _scale(values, bottom, top)
    marks = _axis_y(scale_y, ticks, left, right, top, bottom)
    marks.append(_text(left, 22, f'{s["label"]}（{s["unit"]}）', "chart-unit"))
    if axis["scale"] == "category":
        x_positions = [left+(right-left)*i/max(1,len(xs)-1) for i in range(len(xs))]
    else:
        low, high = min(xs), max(xs)
        if kind == 'scatter' and low == high:
            pad = max(1, abs(low)*.05)
            low, high = low-pad, high+pad
        span = high-low or 1
        x_positions = [left+(v-low)/span*(right-left) for v in xs]
    if axis["scale"] == "linear":
        # Keep the same expanded domain for equal-x points and printed ticks.
        for i in range(6):
            value = low+(high-low)*i/5
            xx = left+(right-left)*i/5
            marks.append(_line(xx, top, xx, bottom))
            marks.append(_text(xx, bottom+28, _tick(value), anchor="middle"))
    else:
        every = max(1, math.ceil(len(labels)/8))
        for i, (label, xx) in enumerate(zip(labels, x_positions)):
            if i % every == 0 or i == len(labels)-1:
                marks.append(_text(xx, bottom+28, label, anchor="middle", wrap=14))
    marks.append(_text((left+right)/2, height-9, axis["label"]+(f'（{axis["unit"]}）' if axis["unit"] else ""), "chart-unit", "middle"))
    points, segments = [], []
    valid = [i for i,v in enumerate(values) if v is not None]
    annotated = set(valid if len(valid) <= 8 else [valid[0], valid[-1]])
    annotated |= {i for i, label in enumerate(labels) if label in view.get("highlight", [])}
    for i, (label, xx, value) in enumerate(zip(labels, x_positions, values)):
        if value is None:
            if points:
                segments.append(points)
            points = []
            marks.append(_text(xx, bottom-10, "缺期", "chart-axis", "middle"))
            continue
        yy = scale_y(value)
        points.append(f'{xx:.3f},{yy:.3f}')
        color = _color(view, i, value)
        marks.append(f'<circle class="data-mark" data-index="{i}" data-value="{value}" data-x="{xs[i]}" cx="{xx:.3f}" cy="{yy:.3f}" r="{5 if kind == "scatter" else 4}" fill="{color}"><title>{escape(label)}：{escape(number(value))}{escape(s["unit"])}</title></circle>')
        if i in annotated:
            text = (label+" · " if kind == "scatter" else "")+number(value)
            anchor = "start" if i == valid[0] else ("end" if i == valid[-1] else "middle")
            label_y = yy+25 if kind == 'scatter' and yy < top+40 else yy-12-(19 if kind == 'scatter' else 0)
            marks.append(_text(xx, label_y, text, "chart-value", anchor, 22 if kind == "scatter" else None))
    if points:
        segments.append(points)
    if kind == "line":
        paths = [f'<polyline class="data-line" points="{" ".join(segment)}" fill="none" stroke="{COLORS[0]}" stroke-width="3"/>' for segment in segments if len(segment)>1]
        # Marks and value labels stay above the lines.
        marks = paths+marks
    return marks, height


def _donut(view):
    labels, s = view["labels"], view["series"][0]
    cx, cy, radius, start = 260, 190, 122, -math.pi/2
    marks = []
    # Values are already validated percentage shares; division maps them to angles.
    for i, (label, value) in enumerate(zip(labels, s["values"])):
        angle = value/100*2*math.pi
        end = start+angle
        if value == 100:
            marks.append(f'<circle class="data-mark donut-segment" data-index="{i}" data-value="{value}" cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{COLORS[i]}" stroke-width="55"/>')
        elif value > 0:
            x0,y0,x1,y1 = cx+radius*math.cos(start),cy+radius*math.sin(start),cx+radius*math.cos(end),cy+radius*math.sin(end)
            marks.append(f'<path class="data-mark donut-segment" data-index="{i}" data-value="{value}" d="M{x0:.3f},{y0:.3f} A{radius},{radius} 0 {int(angle>math.pi)} 1 {x1:.3f},{y1:.3f}" fill="none" stroke="{COLORS[i]}" stroke-width="55"/>')
        start = end
    marks.append(_text(cx, cy+2, "构成占比", "chart-label", "middle"))
    marks.append(_text(cx, cy+28, "合计 100%", "chart-value", "middle"))
    y = 62
    for i,(label,value) in enumerate(zip(labels,s["values"])):
        marks.append(_rect(500, y-12, 14, 14, COLORS[i], value, i, role="legend-swatch"))
        marks.append(_text(530, y, label, "chart-label", wrap=40))
        marks.append(_text(950, y, number(value)+"%", "chart-value", "end"))
        y += max(43,len(_wrap(label,40))*19+18)
    return marks, max(385,y+20)


def render_chart(view, title, emphasis=None):
    """Return a figure from a frozen, verified projection; unsupported kinds fail."""
    if view.get("version") != "chart-spec/1":
        raise ValueError("不支持的图表投影版本")
    kind = view["kind"]
    if kind == "paired" and view["axes"]["x"]["scale"] == "time":
        marks, height = [], 0
        for s in view["series"]:
            panel = {**view, "kind": "line", "series": [s]}
            drawing, panel_height = _xy(panel)
            marks.append(f'<g class="paired-time-panel" transform="translate(0,{height})">'+"".join(drawing)+'</g>')
            height += panel_height+22
    elif kind in {"bar", "paired"}:
        marks, height = _horizontal(view)
    elif kind in {"column", "grouped", "stacked", "waterfall", "histogram"}:
        marks, height = _vertical(view)
    elif kind in {"line", "scatter"}:
        marks, height = _xy(view)
    elif kind == "donut":
        marks, height = _donut(view)
    else:
        raise ValueError(f"图形尚不支持 {kind}")
    legend = ""
    if kind in {"grouped", "stacked"}:
        legend = '<div class="chart-legend">'+"".join(f'<span><i style="background:{COLORS[j]}"></i>{escape(s["label"])}（{escape(s["unit"])}）</span>' for j,s in enumerate(view["series"]))+'</div>'
    notes = []
    if kind == "paired":
        notes.append("两幅图时间轴对齐，纵轴分别标尺，不直接比较曲线高度。" if view["axes"]["x"]["scale"] == "time" else "同一行对应同一对象，两幅图分别标尺；跨图柱长不直接比较。")
    if kind == "waterfall":
        notes.append("首尾柱为总额，中间悬浮柱为增减贡献；虚线连接每一步累计位置。")
    if kind == "scatter":
        notes.append("每个点对应一个对象；图中关系不代表因果。")
    if kind == "histogram":
        notes.append("柱宽对应真实分箱区间；区间左闭右开，最后一箱包含右端点。")
    if kind == "donut":
        notes.append("各部分互斥且覆盖完整总体。")
    if any(v is not None and v < 0 for s in view["series"] for v in s["values"]):
        notes.append("红色负贡献柱表示该分量降低累计值。" if kind == "waterfall" else "红色表示负值，方向由零轴区分。")
    if view.get("tail_note"):
        notes.append(view["tail_note"])
    notes.extend(view.get("warnings", []))
    if view.get("gap_indices"):
        notes.append("缺失周期留空；折线在缺期处断开，未填作零。" if kind in {"line", "paired"} else "缺失周期留空，不绘制柱形，未填作零。")
    denominators = [f'{s["label"]}分母：{s["denominator"]}' for s in view["series"] if s.get("denominator")]
    notes.extend(denominators)
    note_html = "".join(f'<p class="chart-note">{escape(note)}</p>' for note in notes)
    heads = '<th scope="col">'+escape(view["axes"]["x"]["label"])+'</th>'+"".join(f'<th scope="col">{escape(s["label"])}（{escape(s["unit"])}）</th>' for s in view["series"])
    rows = "".join('<tr><th scope="row">'+escape(label)+'</th>'+"".join(f'<td>{escape(number(s["values"][i]))}</td>' for s in view["series"])+'</tr>' for i,label in enumerate(view["labels"]))
    if kind == "scatter":
        heads = '<th scope="col">对象</th><th scope="col">'+escape(view["axes"]["x"]["label"])+f'（{escape(view["axes"]["x"]["unit"])}）</th>'+"".join(f'<th scope="col">{escape(s["label"])}（{escape(s["unit"])}）</th>' for s in view["series"])
        rows = "".join('<tr><th scope="row">'+escape(label)+f'</th><td>{escape(number(view["x_values"][i]))}</td>'+"".join(f'<td>{escape(number(s["values"][i]))}</td>' for s in view["series"])+'</tr>' for i,label in enumerate(view["labels"]))
    table = f'<details class="chart-values"><summary>查看完整图表读数</summary><div class="table-scroll"><table><thead><tr>{heads}</tr></thead><tbody>{rows}</tbody></table></div></details>'
    return f'<figure class="chart-spec {escape(emphasis or view.get("emphasis", "supporting"))} chart-{kind}" data-chart-id="{escape(view["id"])}"><figcaption>{escape(title)}</figcaption>{legend}<div class="chart-canvas"><svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{escape(title)}" viewBox="0 0 {WIDTH} {height}"><title>{escape(title)}</title>'+"".join(marks)+f'</svg></div>{note_html}{table}</figure>'
