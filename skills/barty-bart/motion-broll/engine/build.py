"""Assemble clip fragments + engine + fonts into self-contained HTML files.
usage: python3 build.py <out_dir> clips/01-name.html [clips/02-name.html ...]"""
import base64, re, sys, pathlib
E = pathlib.Path(__file__).resolve().parent
b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
CURSOR = '<svg id="cursor" viewBox="0 0 40 56"><path d="M3 3 L3 41 L12.5 32 L19 47 L25.5 44.2 L19.2 29.8 L32 29.8 Z" fill="#0B0B0B" stroke="#fff" stroke-width="2.6" stroke-linejoin="round"/></svg>'
def build(src, dst):
    frag = open(src, encoding='utf-8').read()
    m = re.search(r'<title>(.*?)</title>', frag); title = m.group(1) if m else pathlib.Path(src).stem
    css = ''.join(re.findall(r'<style>(.*?)</style>', frag, re.S))
    slot = lambda n: (re.search(rf'<div data-slot="{n}">(.*?)</div><!--/{n}-->', frag, re.S) or [None, ''])[1]
    js = ''.join(re.findall(r'<script>(.*?)</script>', frag, re.S))
    base = open(E/'base.css').read().replace('__GEIST__', b64(E/'fonts/Geist-Variable.woff2')).replace('__GEISTMONO__', b64(E/'fonts/GeistMono-Medium.woff2'))
    html = (f'<!doctype html><html><head><meta charset="utf-8"><title>{title}</title><style>{base}{css}</style></head><body>\n'
            f'<div id="wrap"><div id="stage"><div id="world">{slot("world")}<div id="shape">{slot("shape")}</div>{slot("over")}</div>{CURSOR}</div></div>\n'
            f'<script>{open(E/"motion.js").read()}</script><script>{js}</script></body></html>')
    open(dst, 'w', encoding='utf-8').write(html)
if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for s in sys.argv[2:]:
        d = out/(pathlib.Path(s).stem + '.html'); build(s, d); print('built', d)
