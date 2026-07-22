#!/usr/bin/env python3
"""Make a texture seamless: Moisan periodic decomposition + offset blend."""
import argparse

import numpy as np
from PIL import Image


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


def make_seamless(img, overlap=0.25, flatten=True):
    arr = np.asarray(img.convert("RGB")).astype(np.float64)
    if flatten:
        arr = flatten_luminance(arr)
    arr = periodic_component(arr)
    arr = offset_blend(arr, overlap)
    return Image.fromarray(arr.astype(np.uint8))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("-o", "--output", required=True)
    p.add_argument("--overlap", type=float, default=0.25)
    a = p.parse_args()
    make_seamless(Image.open(a.input), a.overlap).save(a.output)
