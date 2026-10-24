"""Turn a generated sketch into clean single-colour ink like a scanned-and-traced page.

usage: python3 -I inkpost.py in.png out.png [options]

Pen variant:
  greyscale -> stretch levels (1st/99th pct) -> 2x upsample -> slight blur -> hard threshold -> downsample.
Marker variant (add --marker, or set the three numbers yourself):
  after the threshold, at 2x:  thicken the ink to a target stroke  ->  low-frequency wobble (displaces the
  strokes a little, so they look hand-drawn instead of evenly fattened)  ->  rough edge (blur + fine noise
  + threshold)  ->  downsample.
  --marker            = --stroke 7 --wobble 1.4 --rough 0.6   (values in px at a 1024 px image)
  --stroke T          measure the current typical stroke (measure.py's method) and grow the ink just enough
                      to reach T px at 1024 (bold reference pages: 7; all reference pages: 5); never thins
  --grow R            or: add exactly R px of ink on each side of every stroke (disc dilation; 0 = off)
  --wobble A          max displacement in px of the low-frequency wobble (0 = off)
  --rough S           strength of the edge roughening (0 = off)
  --seed N            noise seed (default 1)
Heavy-ink variant (速写本 · 浓墨):
  --heavy             = --stroke 7 --wobble 1.8 --rough 1.2 --dry 0.8   (add --close 1.5 only for light inputs: it fills reversed white lines)
  --close C           morphological closing by C px: dense hatching and small dark pockets fill solid
  --dry D             dry-brush skips along stroke edges (streaks at 25 degrees), 0 = off
  (the preset is not called --ink: --ink sets the ink colour)
Varied-weight variant (速写本 · 粗细对比):
  --varied            = --vgrow 2.5 --thin 0.85 --wobble 1.2   (no --rough: it breaks the thin lines)
  --vgrow G           line weight follows local busyness: strokes in calm areas (few ink edges in a ~50 px
                      window) grow by up to G px each side, strokes in busy areas grow 0; the busyness map is
                      smoothed, so weight changes gradually along a stroke
                      only strokes belonging to big forms grow (silhouettes that survive a ~40 px erosion);
                      handwriting, arrows and small isolated marks stay thin
  --thin T            in the busiest areas (busyness > T), shave 1 px off strokes that are thicker than 3 px
                      (never breaks a line: thin strokes are left alone); 0 = off
Other options: --thresh 165, --ink 2C2C2C, --paper FFFFFF (dark variant: --ink D3D3D3 --paper 000000).

Prints ink coverage inside the drawing's bounding box. Measure stroke width with measure.py.
Reference set (87 pages): stroke median 5 px at 1024 (0.49 %), bold-marker pages 7 px (0.68 %);
coverage median 0.155, bold pages 0.33."""
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageOps

a = sys.argv[1:]
src, dst = a[0], a[1]
flags = a[2:]
opt = {}
i = 0
while i < len(flags):
    if flags[i] == '--marker':
        opt.setdefault('--stroke', '7'); opt.setdefault('--wobble', '1.4'); opt.setdefault('--rough', '0.6'); i += 1
    elif flags[i] == '--varied':
        opt.setdefault('--vgrow', '2.5'); opt.setdefault('--thin', '0.85'); opt.setdefault('--wobble', '1.2'); i += 1
    elif flags[i] == '--heavy':
        opt.setdefault('--stroke', '7'); opt.setdefault('--wobble', '1.8')
        opt.setdefault('--rough', '1.2'); opt.setdefault('--dry', '0.8'); i += 1
    else:
        opt[flags[i]] = flags[i + 1]; i += 2
th = int(opt.get('--thresh', 165)); ink = opt.get('--ink', '2C2C2C'); paper = opt.get('--paper', 'FFFFFF')
grow = float(opt.get('--grow', 0)); target = float(opt.get('--stroke', 0)); wobble = float(opt.get('--wobble', 0)); rough = float(opt.get('--rough', 0))
close = float(opt.get('--close', 0)); dry = float(opt.get('--dry', 0))
vgrow = float(opt.get('--vgrow', 0)); thin = float(opt.get('--thin', 0))
rng = np.random.default_rng(int(opt.get('--seed', 1)))

im = Image.open(src).convert('L')
h = im.histogram(); n = sum(h); acc = 0; lo = 0; hi = 255
for i, c in enumerate(h):
    acc += c
    if acc < n * 0.01: lo = i
    if acc < n * 0.99: hi = i
hi = max(hi, lo + 10)
im = im.point(lambda v: max(0, min(255, (v - lo) * 255 // (hi - lo))))
big = im.resize((im.width * 2, im.height * 2), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))
mask = big.point(lambda v: 0 if v < th else 255)  # 0 = ink

if grow or target or wobble or rough or close or dry or vgrow or thin:
    S = 2 * im.width / 1024.0            # px at this working scale per px at 1024
    m = np.asarray(mask) < 128           # True = ink
    H, W = m.shape
    if target and not grow:
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from measure import measure_mask
        ys, xs = np.nonzero(m)
        # measure_mask reports px with the drawing's long side scaled to 1024, like the reference numbers
        cur = (measure_mask(m) or {}).get('stroke', 0.0)
        unit = (max(int(xs.max() - xs.min()), int(ys.max() - ys.min())) + 1) / 1024.0 if len(xs) else S
        r = max(0.0, min(4.0 * S, (target - cur) / 2 * unit))   # working px per side
        print(f"stroke {cur:.1f}px -> target {target:g}px: grow {r / unit:.2f}px each side", file=sys.stderr)
    elif grow:
        r = grow * S
    else:
        r = 0
    if r > 0:
        # disc dilation via a blurred mask: everything within ~r of ink becomes ink
        blur = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r * 0.75))
        m = np.asarray(blur) > 255 * 0.12
    if vgrow or thin:
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from measure import erode, dilate, box_mean
        edges = m & ~erode(m)
        busy = box_mean(edges, max(4, int(24 * S)))
        bi = busy[m]
        if bi.size:
            lo_b, hi_b = np.quantile(bi, [0.30, 0.85])
            b01 = np.clip((busy - lo_b) / max(1e-6, hi_b - lo_b), 0, 1)
            # smooth so the weight never jumps along one stroke
            b01 = np.asarray(Image.fromarray((b01 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10 * S)), dtype=np.float32) / 255.0
            if thin:
                # busiest areas: shave one px off strokes that are >= 5 px wide there (they stay >= 3 px);
                # thinner strokes are untouched, so nothing breaks
                e1 = erode(m)
                wide = dilate(dilate(erode(e1)))
                m = np.where((b01 > thin) & wide, e1, m)
            if vgrow:
                g = vgrow * S * (1.0 - b01)                     # growth radius per pixel, working px
                # only big forms get thick: fill each silhouette (flood the outside paper from the border),
                # erode it by ~40 px; words, arrows and stray marks don't survive, so they stay thin
                from PIL import ImageDraw
                Rb = 40 * S
                sil = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3 * S))
                sil = Image.fromarray(((np.asarray(sil) > 30) * 255).astype(np.uint8))
                sil = ImageOps.expand(sil, 2, fill=0); ImageDraw.floodfill(sil, (0, 0), 128)
                sil = np.asarray(sil)[2:-2, 2:-2] != 128
                core = np.asarray(Image.fromarray((sil * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(Rb * 0.75))) > 255 * 0.88
                near = np.asarray(Image.fromarray((core * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur((Rb + 8 * S) * 0.75))) > 255 * 0.08
                g = g * near
                K = int(np.ceil(g.max()))
                dist = np.full(m.shape, 255, np.uint8); dist[m] = 0
                cur = m.copy()
                for k in range(1, K + 1):
                    nxt = dilate(cur) if k % 2 else (cur | np.pad(cur, 1)[2:, 1:-1] | np.pad(cur, 1)[:-2, 1:-1] | np.pad(cur, 1)[1:-1, 2:] | np.pad(cur, 1)[1:-1, :-2])
                    dist[nxt & ~cur] = k; cur = nxt
                m = m | (dist <= g)
                print(f"varied: busyness q30/q85 {lo_b:.3f}/{hi_b:.3f}, grow up to {vgrow:g}px in calm areas", file=sys.stderr)
    if close:
        # closing (dilate, then erode by the same radius): gaps narrower than ~2*close px fill in, so dense
        # hatching and small enclosed dark pockets become solid black; open white areas keep their shape
        rc = close * S
        b = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rc * 0.75))
        b = Image.fromarray(((np.asarray(b) > 255 * 0.12) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rc * 0.75))
        m = np.asarray(b) > 255 * 0.88
    if wobble:
        # smooth random displacement field, wavelength ~ 6 % of the image
        cell = max(8, int(W * 0.06))
        gw, gh = W // cell + 3, H // cell + 3
        def field():
            f = Image.fromarray(((rng.random((gh, gw)) * 255)).astype(np.uint8)).resize((W + 2 * cell, H + 2 * cell), Image.BICUBIC)
            f = np.asarray(f, dtype=np.float32)[cell:cell + H, cell:cell + W] / 255.0 - 0.5
            return f * 2 * wobble * S
        dx, dy = field(), field()
        yy, xx = np.mgrid[0:H, 0:W]
        sx = np.clip((xx + dx).round().astype(int), 0, W - 1)
        sy = np.clip((yy + dy).round().astype(int), 0, H - 1)
        m = m[sy, sx]
    if rough:
        # ragged marker edge: blur the mask, add fine noise, threshold again
        b = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1 * S)), dtype=np.float32) / 255.0
        noise = Image.fromarray((rng.random((H // 3 + 1, W // 3 + 1)) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        noise = np.asarray(noise, dtype=np.float32) / 255.0 - 0.5
        m = (b + noise * 0.35 * rough) > 0.5
    if dry:
        # dry-brush / worn-marker skips: streaky noise at ~25 degrees removes ink only in a band along the
        # edges (never in the middle of a black mass), so strokes look dragged and broken at their sides
        band = max(2, int(2.5 * S))
        core = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(band * 0.75))) > 255 * 0.88
        edge = m & ~core
        st = Image.fromarray((rng.random((H // 2 + 1, max(2, W // 40))) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        st = np.asarray(st.rotate(25, resample=Image.BILINEAR, fillcolor=128), dtype=np.float32) / 255.0
        m = m & ~(edge & (st < 0.38 * dry))
    mask = Image.fromarray(np.where(m, 0, 255).astype(np.uint8))

bw = mask.resize(im.size, Image.LANCZOS)
rgb = lambda s: tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
out = ImageOps.colorize(bw, rgb(ink), rgb(paper))
out.save(dst)
bb = ImageOps.invert(bw).getbbox()
crop = bw.crop(bb) if bb else bw
cov = sum(crop.histogram()[:128]) / (crop.width * crop.height)
print(f"{dst} ink coverage {cov:.3f}")
