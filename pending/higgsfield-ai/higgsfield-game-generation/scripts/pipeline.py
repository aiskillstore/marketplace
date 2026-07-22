#!/usr/bin/env python3
"""Texture factory post-process: GPT output -> seamless tile + PBR maps.\n\nSeam fix modes: blend="cut" (default) hides the junction with a hard\nminimal-error cut that dodges detailed features - fully sharp; "feather"\nis the legacy cross-fade (soft band on structured materials).

Self-contained (numpy + pillow only). Steps: border trim -> exact palette
transfer back to the reference -> mathematical seam fix (Moisan periodic
decomposition + offset blend + luminance flatten) -> PBR maps computed with
wrap-around filters (basecolor / normal / roughness / height).

Usage:
  python3 pipeline.py gpt_output.png -o textures/{id} --ref textures/{id}_ref.png
  python3 pipeline.py tile.png -o textures/{id} --trim 0              # non-GPT input
  python3 pipeline.py tile.png -o textures/{id} --trim 0 --no-seam   # maps only
  python3 pipeline.py tile.png -o textures/{id} --overlap 0.08       # narrow blend
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image


# ---------------- seam fix (former seamless.py) ----------------

def periodic_component(img):
    img = img.astype(np.float64)
    h, w = img.shape[:2]
    out = np.empty_like(img)
    for c in range(img.shape[2]):
        u = img[..., c]
        v = np.zeros_like(u)
        v[0, :] += u[-1, :] - u[0, :]
        v[-1, :] += u[0, :] - u[-1, :]
        v[:, 0] += u[:, -1] - u[:, 0]
        v[:, -1] += u[:, 0] - u[:, -1]
        fy = np.cos(2 * np.pi * np.arange(h) / h)[:, None]
        fx = np.cos(2 * np.pi * np.arange(w) / w)[None, :]
        denom = 2 * fy + 2 * fx - 4
        denom[0, 0] = 1.0
        s = np.fft.fft2(v) / denom
        s[0, 0] = 0.0
        out[..., c] = u - np.real(np.fft.ifft2(s))
    return np.clip(out, 0, 255)


def offset_blend(img, overlap=0.25):
    img = img.astype(np.float64)

    def blend_seam(a, axis):
        size = a.shape[axis]
        rolled = np.roll(a, size // 2, axis=axis)
        k = max(int(size * overlap / 2), 1)
        c = size // 2
        idx = [slice(None)] * 3
        idx[axis] = slice(c - k, c + k)
        donor = np.take(a, range(c - k, c + k), axis=axis)
        w = 1 - np.abs(np.linspace(-1, 1, 2 * k))
        shape = [1, 1, 1]
        shape[axis] = 2 * k
        w = w.reshape(shape)
        rolled[tuple(idx)] = rolled[tuple(idx)] * (1 - w) + donor * w
        return np.roll(rolled, -(size // 2), axis=axis)

    return np.clip(blend_seam(blend_seam(img, 1), 0), 0, 255)


def flatten_luminance(img, sigma_frac=0.07):
    img = img.astype(np.float64)
    h, w = img.shape[:2]
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    sigma = sigma_frac * min(h, w)
    k = np.exp(-2 * (np.pi * sigma) ** 2 * (fy ** 2 + fx ** 2))
    low = np.real(np.fft.ifft2(np.fft.fft2(img.mean(axis=2)) * k))
    return np.clip(img + (low.mean() - low)[..., None], 0, 255)




# ---------------- min-cut seam (sharp default) ----------------

def _hcut_cyclic(D, tries=14):
    """Min-cost horizontal path through D (h,w), one row per column, step ±1,
    constrained to path[0] == path[-1] so the cut respects the wrap."""
    h, w = D.shape
    starts = np.argsort(D[:, 0] + D[:, -1])[:tries]
    best_cost, best_path = np.inf, None
    for s in starts:
        M = np.full((h, w), np.inf)
        M[s, 0] = D[s, 0]
        back = np.zeros((h, w), int)
        for j in range(1, w):
            prev = M[:, j - 1]
            up = np.concatenate(([np.inf], prev[:-1]))
            down = np.concatenate((prev[1:], [np.inf]))
            cand = np.stack([up, prev, down])
            M[:, j] = D[:, j] + cand.min(0)
            back[:, j] = cand.argmin(0) - 1
        if M[s, -1] >= best_cost:
            continue
        best_cost = M[s, -1]
        path = np.zeros(w, int)
        path[-1] = s
        for j in range(w - 1, 0, -1):
            path[j - 1] = path[j] + back[path[j], j]
        best_path = path
    return best_path


def _edge_energy(x):
    return (abs(np.diff(x, axis=1, prepend=x[:, :1]))
            + abs(np.diff(x, axis=0, prepend=x[:1])))


def _cut_axis(a, overlap, lam=0.6, stone_w=1.5, feather_px=3):
    """Repair the axis-0 wrap junction with a hard minimal-error cut: the seam
    is covered by a thin donor tube from the tile center, bounded by two cyclic
    min-cost paths that dodge high-detail features. No averaging except a
    feather_px-wide feather along the cut line itself."""
    n = a.shape[0]
    c = n // 2
    k = max(int(n * overlap / 2), 2)
    rolled = np.roll(a, c, axis=0)
    band = rolled[c - k:c + k].copy()
    # donor: the cleanest contiguous strip (its own middle rows must be smooth,
    # since they become the new wrap pair) that also matches the band
    cands = [int(n * f) for f in (0.25, 0.33, 0.5, 0.66, 0.75)]
    best, donor = np.inf, None
    for q in cands:
        if q - k < 0 or q + k > n:
            continue
        d = a[q - k:q + k]
        smooth = np.abs(d[k] - d[k - 1]).mean()           # future wrap pair
        fit = np.abs(band - d).mean()
        score = smooth * 3.0 + fit
        if score < best:
            best, donor = score, d
    D = np.abs(band - donor).mean(-1)
    cost = D + stone_w * (_edge_energy(band.mean(-1)) + _edge_energy(donor.mean(-1)))
    r = np.arange(k - 1)[:, None]
    up = _hcut_cyclic(cost[:k - 1] + lam * (k - 1 - r))
    lo = _hcut_cyclic(cost[k + 1:] + lam * r) + (k + 1)
    rows = np.arange(2 * k)[:, None]
    alpha = ((rows > up[None, :]) & (rows < lo[None, :])).astype(np.float64)
    if feather_px > 0:
        kern = np.ones(2 * feather_px + 1)
        kern /= kern.sum()
        alpha = np.apply_along_axis(
            lambda v: np.convolve(v, kern, mode="same"), 0, alpha)
        alpha[k - 1:k + 1] = 1.0  # the junction itself stays 100% donor
    rolled[c - k:c + k] = band * (1 - alpha[..., None]) + donor * alpha[..., None]
    return np.roll(rolled, -c, axis=0)


def make_seamless(img, overlap=0.25, flatten=True, blend="cut"):
    arr = np.asarray(img.convert("RGB")).astype(np.float64)
    if flatten:
        arr = flatten_luminance(arr)
    arr = periodic_component(arr)
    if blend == "cut":
        arr = _cut_axis(arr, overlap)
        arr = np.swapaxes(_cut_axis(np.swapaxes(arr, 0, 1), overlap), 0, 1)
        arr = np.clip(arr, 0, 255)
    else:
        arr = offset_blend(arr, overlap)
    return Image.fromarray(arr.astype(np.uint8))


def composite_cross(orig_img, gpt_img, k_in=40, k_out=110, feather_px=3):
    """Masked-inpaint emulation for the offset-inpaint pass: the model repaints
    the whole image, but only its center cross is taken - bounded by cyclic
    min-cut paths where original and repaint agree; everything else stays the
    untouched original. Returns the UNROLLED tile (the repaired cross becomes
    the wrap, the pristine original becomes the interior)."""
    O = np.asarray(orig_img.convert("RGB")).astype(np.float64)
    G = np.asarray(gpt_img.convert("RGB").resize(orig_img.size, Image.LANCZOS)
                   ).astype(np.float64)
    n = O.shape[0]
    c = n // 2
    diff = np.abs(O - G).mean(-1)

    def band_alpha(d, axis):
        if axis == 1:
            d = d.T
        up = _hcut_cyclic(d[c - k_out:c - k_in]) + (c - k_out)
        lo = _hcut_cyclic(d[c + k_in:c + k_out]) + (c + k_in)
        rows = np.arange(n)[:, None]
        a = ((rows > up[None, :]) & (rows < lo[None, :])).astype(np.float64)
        if feather_px > 0:
            kern = np.ones(2 * feather_px + 1)
            kern /= kern.sum()
            a = np.apply_along_axis(
                lambda v: np.convolve(v, kern, mode="same"), 0, a)
            a[c - k_in:c + k_in] = 1.0
        return a if axis == 0 else a.T

    alpha = np.maximum(band_alpha(diff, 0), band_alpha(diff, 1))[..., None]
    out = np.clip(O * (1 - alpha) + G * alpha, 0, 255).astype(np.uint8)
    out = np.roll(np.roll(out, -c, 0), -(O.shape[1] // 2), 1)
    return Image.fromarray(out)


# ---------------- post-process + PBR (former pipeline.py) ----------------

def trim_border(img, frac):
    if frac <= 0:
        return img
    w, h = img.size
    k = int(min(w, h) * frac)
    return img.crop((k, k, w - k, h - k))


def match_colors(img, ref):
    a = np.asarray(img.convert("RGB")).astype(np.float64)
    r = np.asarray(ref.convert("RGB")).astype(np.float64)
    out = np.empty_like(a)
    bins = np.arange(257)
    for c in range(3):
        sh, _ = np.histogram(a[..., c], bins=bins, density=True)
        rh, _ = np.histogram(r[..., c], bins=bins, density=True)
        lut = np.interp(np.cumsum(sh) / sh.sum(),
                        np.cumsum(rh) / rh.sum(), np.arange(256))
        out[..., c] = lut[a[..., c].astype(np.uint8)]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def _wrap_blur(a, sigma):
    fy = np.fft.fftfreq(a.shape[0])[:, None]
    fx = np.fft.fftfreq(a.shape[1])[None, :]
    k = np.exp(-2 * (np.pi * sigma) ** 2 * (fy ** 2 + fx ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * k))


def pbr_maps(img, strength=2.0):
    rgb = np.asarray(img.convert("RGB")).astype(np.float64)
    lum = rgb.mean(axis=2) / 255.0

    height = _wrap_blur(lum, 2.0) - _wrap_blur(lum, 48.0)
    lo, hi = np.percentile(height, [1, 99])
    height = np.clip((height - lo) / (hi - lo + 1e-9), 0, 1)

    gx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * strength * 255
    gy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * strength * 255
    nz = np.ones_like(gx) * 255.0 / strength
    norm = np.sqrt(gx ** 2 + gy ** 2 + nz ** 2)
    normal = np.stack([(-gx / norm + 1) / 2, (gy / norm + 1) / 2,
                       (nz / norm + 1) / 2], axis=-1)

    rough = 1.0 - np.clip((lum - _wrap_blur(lum, 8.0)) * 3 + 0.25, 0, 0.6)

    u8 = lambda a: Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return {"basecolor": img.convert("RGB"), "normal": u8(normal),
            "height": u8(height), "roughness": u8(rough)}


def run(inp, prefix, ref=None, trim=0.04, overlap=0.25, seam=True, blend="cut",
        inpaint=None):
    out = Path(prefix)
    out.parent.mkdir(parents=True, exist_ok=True)
    if inpaint:
        # inp = the ROLLED original (seam as a center cross), inpaint = the
        # model's repaint of it; composite takes only the cross from the model
        img = composite_cross(Image.open(inp), Image.open(inpaint))
        trim = 0
        img = trim_border(img, trim)
    else:
        img = trim_border(Image.open(inp), trim)
    if ref:
        img = match_colors(img, Image.open(ref))
    if seam:
        img = make_seamless(img, overlap, blend=blend)
    img.save(f"{prefix}_seamless.png")
    for n, m in pbr_maps(img).items():
        m.save(f"{prefix}_{n}.png")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("-o", "--prefix", required=True)
    p.add_argument("--ref", default=None)
    p.add_argument("--trim", type=float, default=0.04)
    p.add_argument("--overlap", type=float, default=0.25,
                   help="seam corridor width: cut-path room for blend=cut, "
                        "blend band for blend=feather (0.08 = narrow)")
    p.add_argument("--blend", choices=["cut", "feather"], default="cut",
                   help="cut = sharp minimal-error cut (default); "
                        "feather = legacy cross-fade (soft band at joints)")
    p.add_argument("--no-seam", action="store_true",
                   help="skip the seam fix (maps from an already-seamless tile)")
    p.add_argument("--inpaint", default=None,
                   help="offset-inpaint finish: input is the ROLLED original, "
                        "this is the model's repaint; only its center cross is "
                        "composited in (masked-inpaint emulation)")
    a = p.parse_args()
    run(a.input, a.prefix, a.ref, a.trim, a.overlap,
        seam=not a.no_seam, blend=a.blend, inpaint=a.inpaint)
