#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pillow"]
# ///
"""Coordinate-system conversion + bearing/distance + camera geometry. All other scripts import this file.

Coordinate systems:
  wgs   WGS84: GPS / Google satellite imagery / OSM
  gcj   GCJ-02: Amap (Gaode) / Tencent / Google China road map
  bd    BD-09 lat/lon: Baidu
  bdmc  Baidu Mercator plane coordinates (the @x,y in Baidu Maps URLs, the x,y of the panorama API)

All lat/lon arguments are always in (lat, lon) order.

CLI examples:
  geo.py convert --from bdmc --to wgs 12697689.83 2568072.49
  geo.py bearing 22.6045,114.0520 22.6072,114.0564
  geo.py dest 22.6045,114.0520 --bearing 47 --dist 120
  geo.py range --real 55 --pixels 195 --image-width 1279 --hfov 53
  geo.py range --real 300 --pixels 420 --image-width 1080 --hfov 12:70     # zoom unknown: field-of-view range gives a distance range
  geo.py line --near 22.6060,114.0550 --far 22.6072,114.0564 --range 50:1500 --out line.json
  geo.py intersect --align1 N1lat,N1lon:F1lat,F1lon --align2 N2lat,N2lon:F2lat,F2lon --sigma 1
  geo.py bearings --at <lat,lon> --geojson buildings.geojson --target 306 --tol 8   # bearing first, then identify the structure: which building lies on that bearing
  geo.py frame --at 22.60,114.10 --anchor A:22.61,114.05:px=1000 --width 1080 --hfov 12:70 \\
               --pt B:22.62,114.06:h=300:w=60 --pt C:22.58,114.04:h=150:w=40      # compute before excluding: should B and C be in the frame
  geo.py spacing --cols '39,133,219,296,369;745,788,829' --line rail.geojson --line-name 城际 --span 32 \\
                 --center 35.4983,138.7688 --radius 1500 --grid 50 --headings 55:115 --focals 1200:1500 \\
                 --cx 640 --out spacing.json     # pixel columns of a row of bridge piers → camera position, heading, focal length (7.7)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------- coordinate-system conversion

_A = 6378245.0
_EE = 0.00669342162296594323


def _out_of_china(lat: float, lon: float) -> bool:
    return not (73.66 < lon < 135.05 and 3.86 < lat < 53.55)


def _t_lat(x: float, y: float) -> float:
    r = -100 + 2 * x + 3 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    r += (20 * math.sin(6 * x * math.pi) + 20 * math.sin(2 * x * math.pi)) * 2 / 3
    r += (20 * math.sin(y * math.pi) + 40 * math.sin(y / 3 * math.pi)) * 2 / 3
    r += (160 * math.sin(y / 12 * math.pi) + 320 * math.sin(y * math.pi / 30)) * 2 / 3
    return r


def _t_lon(x: float, y: float) -> float:
    r = 300 + x + 2 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    r += (20 * math.sin(6 * x * math.pi) + 20 * math.sin(2 * x * math.pi)) * 2 / 3
    r += (20 * math.sin(x * math.pi) + 40 * math.sin(x / 3 * math.pi)) * 2 / 3
    r += (150 * math.sin(x / 12 * math.pi) + 300 * math.sin(x / 30 * math.pi)) * 2 / 3
    return r


def _gcj_delta(lat: float, lon: float) -> tuple[float, float]:
    dlat = _t_lat(lon - 105, lat - 35)
    dlon = _t_lon(lon - 105, lat - 35)
    rad = lat / 180 * math.pi
    m = 1 - _EE * math.sin(rad) ** 2
    sm = math.sqrt(m)
    dlat = dlat * 180 / ((_A * (1 - _EE)) / (m * sm) * math.pi)
    dlon = dlon * 180 / (_A / sm * math.cos(rad) * math.pi)
    return dlat, dlon


def wgs2gcj(lat: float, lon: float) -> tuple[float, float]:
    if _out_of_china(lat, lon):
        return lat, lon
    dlat, dlon = _gcj_delta(lat, lon)
    return lat + dlat, lon + dlon


def gcj2wgs(lat: float, lon: float) -> tuple[float, float]:
    """Iterative inverse, error < 0.5 m."""
    if _out_of_china(lat, lon):
        return lat, lon
    wlat, wlon = lat, lon
    for _ in range(5):
        glat, glon = wgs2gcj(wlat, wlon)
        wlat += lat - glat
        wlon += lon - glon
    return wlat, wlon


_XPI = math.pi * 3000 / 180


def gcj2bd(lat: float, lon: float) -> tuple[float, float]:
    z = math.hypot(lon, lat) + 0.00002 * math.sin(lat * _XPI)
    th = math.atan2(lat, lon) + 0.000003 * math.cos(lon * _XPI)
    return z * math.sin(th) + 0.006, z * math.cos(th) + 0.0065


def bd2gcj(lat: float, lon: float) -> tuple[float, float]:
    x, y = lon - 0.0065, lat - 0.006
    z = math.hypot(x, y) - 0.00002 * math.sin(y * _XPI)
    th = math.atan2(y, x) - 0.000003 * math.cos(x * _XPI)
    return z * math.sin(th), z * math.cos(th)


_MCBAND = [12890594.86, 8362377.87, 5591021, 3481989.83, 1678043.12, 0]
_MC2LL = [
    [1.410526172116255e-8, 0.00000898305509648872, -1.9939833816331, 200.9824383106796, -187.2403703815547, 91.6087516669843, -23.38765649603339, 2.57121317296198, -0.03801003308653, 17337981.2],
    [-7.435856389565537e-9, 0.000008983055097726239, -0.78625201886289, 96.32687599759846, -1.85204757529826, -59.36935905485877, 47.40033549296737, -16.50741931063887, 2.28786674699375, 10260144.86],
    [-3.030883460898826e-8, 0.00000898305509983578, 0.30071316287616, 59.74293618442277, 7.357984074871, -25.38371002664745, 13.45380521110908, -3.29883767235584, 0.32710905363475, 6856817.37],
    [-1.981981304930552e-8, 0.000008983055099779535, 0.03278182852591, 40.31678527705744, 0.65659298677277, -4.44255534477492, 0.85341911805263, 0.12923347998204, -0.04625736007561, 4482777.06],
    [3.09191371068437e-9, 0.000008983055096812155, 0.00006995724062, 23.10934304144901, -0.00023663490511, -0.6321817810242, -0.00663494467273, 0.03430082397953, -0.00466043876332, 2555164.4],
    [2.890871144776878e-9, 0.000008983055095805407, -3.068298e-8, 7.47137025468032, -0.00000353937994, -0.02145144861037, -0.00001234426596, 0.00010322952773, -0.00000323890364, 826088.5],
]
_LLBAND = [75, 60, 45, 30, 15, 0]
_LL2MC = [
    [-0.0015702102444, 111320.7020616939, 1704480524535203, -10338987376042340, 26112667856603880, -35149669176653700, 26595700718403920, -10725012454188240, 1800819912950474, 82.5],
    [0.0008277824516172526, 111320.7020463578, 647795574.6671607, -4082003173.641316, 10774905663.51142, -15171875531.51559, 12053065338.62167, -5124939663.577472, 913311935.9512032, 67.5],
    [0.00337398766765, 111320.7020202162, 4481351.045890365, -23393751.19931662, 79682215.47186455, -115964993.2797253, 97236711.15602145, -43661946.33752821, 8477230.501135234, 52.5],
    [0.00220636496208, 111320.7020209128, 51751.86112841131, 3796837.749470245, 992013.7397791013, -1221952.21711287, 1340652.697009075, -620943.6990984312, 144416.9293806241, 37.5],
    [-0.0003441963504368392, 111320.7020576856, 278.2353980772752, 2485758.690035394, 6070.750963243378, 54821.18345352118, 9540.606633304236, -2710.55326746645, 1405.483844121726, 22.5],
    [-0.0003218135878613132, 111320.7020701615, 0.00369383431289, 823725.6402795718, 0.46104986909093, 2351.343141331292, 1.58060784298199, 8.77738589078284, 0.37238884252424, 7.45],
]


def _poly(x: float, y: float, c: list[float]) -> tuple[float, float]:
    fx = c[0] + c[1] * abs(x)
    t = abs(y) / c[9]
    fy = c[2] + c[3] * t + c[4] * t ** 2 + c[5] * t ** 3 + c[6] * t ** 4 + c[7] * t ** 5 + c[8] * t ** 6
    return (-fx if x < 0 else fx), (-fy if y < 0 else fy)


def bdmc2bd(x: float, y: float) -> tuple[float, float]:
    c = next(_MC2LL[i] for i, b in enumerate(_MCBAND) if abs(y) >= b)
    lon, lat = _poly(x, y, c)
    return lat, lon


def bd2bdmc(lat: float, lon: float) -> tuple[float, float]:
    lat = max(min(lat, 74), -74)
    c = next(_LL2MC[i] for i, b in enumerate(_LLBAND) if abs(lat) >= b)
    return _poly(lon, lat, c)


def convert(a: float, b: float, src: str, dst: str) -> tuple[float, float]:
    """a,b are lat,lon for the lat/lon systems; x,y for bdmc."""
    if src == dst:
        return a, b
    # normalize to wgs first
    if src == "wgs":
        lat, lon = a, b
    elif src == "gcj":
        lat, lon = gcj2wgs(a, b)
    elif src == "bd":
        lat, lon = gcj2wgs(*bd2gcj(a, b))
    elif src == "bdmc":
        lat, lon = gcj2wgs(*bd2gcj(*bdmc2bd(a, b)))
    else:
        raise ValueError(src)
    if dst == "wgs":
        return lat, lon
    g = wgs2gcj(lat, lon)
    if dst == "gcj":
        return g
    bd = gcj2bd(*g)
    if dst == "bd":
        return bd
    if dst == "bdmc":
        return bd2bdmc(*bd)
    raise ValueError(dst)


# ---------------------------------------------------------------- bearing and distance

_R = 6371008.8


def distance(p: tuple[float, float], q: tuple[float, float]) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (*p, *q))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * _R * math.asin(math.sqrt(h))


def bearing(p: tuple[float, float], q: tuple[float, float]) -> float:
    """Compass bearing from p looking at q, 0=north, clockwise."""
    la1, lo1, la2, lo2 = map(math.radians, (*p, *q))
    y = math.sin(lo2 - lo1) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(lo2 - lo1)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def dest(p: tuple[float, float], brg: float, dist_m: float) -> tuple[float, float]:
    la1, lo1 = map(math.radians, p)
    b = math.radians(brg)
    d = dist_m / _R
    la2 = math.asin(math.sin(la1) * math.cos(d) + math.cos(la1) * math.sin(d) * math.cos(b))
    lo2 = lo1 + math.atan2(math.sin(b) * math.sin(d) * math.cos(la1), math.cos(d) - math.sin(la1) * math.sin(la2))
    return math.degrees(la2), math.degrees(lo2)


# ---------------------------------------------------------------- Web Mercator tiles

def ll2px(zoom: int, lat: float, lon: float) -> tuple[float, float]:
    """lat/lon → global pixel coordinates at this zoom level (256 tiles)."""
    n = 256 * 2 ** zoom
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def px2ll(zoom: int, x: float, y: float) -> tuple[float, float]:
    n = 256 * 2 ** zoom
    lon = x / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lat, lon


def meters_per_px(zoom: int, lat: float) -> float:
    return 156543.03392 * math.cos(math.radians(lat)) / 2 ** zoom


# ---------------------------------------------------------------- camera geometry

def focal_px(image_width_px: float, hfov_deg: float) -> float:
    """Focal length in pixels under the pinhole model."""
    return (image_width_px / 2) / math.tan(math.radians(hfov_deg) / 2)


def range_from_size(real_size_m: float, size_px: float, image_width_px: float, hfov_deg: float) -> float:
    """Known real width of an object and its pixel width in the frame → depth distance (meters)."""
    return real_size_m * focal_px(image_width_px, hfov_deg) / size_px


def angle_from_center(px: float, center_px: float, image_width_px: float, hfov_deg: float) -> float:
    """Horizontal angle of a point in the frame relative to the optical axis (degrees, right positive). Same for vertical: pass vertical pixels."""
    return math.degrees(math.atan((px - center_px) / focal_px(image_width_px, hfov_deg)))


# Common phone main-camera field of view (35mm equivalent focal length → long-side/short-side field of view for a 4:3 frame)
def fov_from_equiv_focal(focal_mm: float, aspect: tuple[int, int] = (4, 3)) -> tuple[float, float]:
    diag = 43.2666
    w, h = aspect
    k = diag / math.hypot(w, h)
    long_side, short_side = w * k, h * k
    return (math.degrees(2 * math.atan(long_side / 2 / focal_mm)),
            math.degrees(2 * math.atan(short_side / 2 / focal_mm)))


# ---------------------------------------------------------------- sight-line intersection

def _enu(p: tuple[float, float], o: tuple[float, float]) -> tuple[float, float]:
    """Local plane coordinates with o as origin (meters, east, north). Error is negligible within 50 km."""
    return ((p[1] - o[1]) * math.cos(math.radians(o[0])) * 111320.0, (p[0] - o[0]) * 110540.0)


def _ll(xy: tuple[float, float], o: tuple[float, float]) -> tuple[float, float]:
    return (o[0] + xy[1] / 110540.0, o[1] + xy[0] / (math.cos(math.radians(o[0])) * 111320.0))


def ray_from_alignment(near: tuple[float, float], far: tuple[float, float]) -> tuple[tuple[float, float], float]:
    """In the frame, near is in front of far (or vertically aligned) → the camera position is on the extension of far→near, beyond near. Returns (origin, bearing)."""
    return near, bearing(far, near)


def ray_from_sighting(landmark: tuple[float, float], seen_bearing: float) -> tuple[tuple[float, float], float]:
    """The bearing from the camera position to landmark is seen_bearing → the camera position is on the ray from landmark in the opposite direction."""
    return landmark, (seen_bearing + 180) % 360


def intersect_rays(r1, r2) -> tuple[tuple[float, float], float, float, float] | None:
    """Intersect two rays. Returns (intersection, crossing angle°, distance along ray 1 in m, distance along ray 2 in m); returns None if parallel or the intersection is behind a ray."""
    (p1, b1), (p2, b2) = r1, r2
    o = p1
    x1, y1 = _enu(p1, o)
    x2, y2 = _enu(p2, o)
    d1 = (math.sin(math.radians(b1)), math.cos(math.radians(b1)))
    d2 = (math.sin(math.radians(b2)), math.cos(math.radians(b2)))
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-9:
        return None
    t1 = ((x2 - x1) * d2[1] - (y2 - y1) * d2[0]) / den
    t2 = ((x2 - x1) * d1[1] - (y2 - y1) * d1[0]) / den
    if t1 < 0 or t2 < 0:
        return None
    pt = _ll((x1 + t1 * d1[0], y1 + t1 * d1[1]), o)
    ang = abs((b1 - b2 + 180) % 360 - 180)
    return pt, min(ang, 180 - ang), t1, t2


def intersect_with_error(r1, r2, sigma_deg: float) -> dict | None:
    """Intersection of two rays, plus the maximum distance the intersection moves when each bearing is offset by ±sigma (used as the error radius)."""
    base = intersect_rays(r1, r2)
    if base is None:
        return None
    pt, ang, t1, t2 = base
    spread = 0.0
    for s1 in (-sigma_deg, sigma_deg):
        for s2 in (-sigma_deg, sigma_deg):
            q = intersect_rays((r1[0], r1[1] + s1), (r2[0], r2[1] + s2))
            spread = max(spread, math.inf if q is None else distance(pt, q[0]))
    return {"point": [round(pt[0], 7), round(pt[1], 7)], "crossing_angle_deg": round(ang, 1),
            "dist_from_ray1_origin_m": round(t1), "dist_from_ray2_origin_m": round(t2),
            "error_radius_m": None if math.isinf(spread) else round(spread)}


# ---------------------------------------------------------------- frame prediction: should a landmark appear in the frame

def _band_f(s: str) -> tuple[float, float]:
    """'65' → (65, 65); '12:70' → (12, 70)."""
    if ":" in s:
        a, b = s.split(":")
        return float(a), float(b)
    return float(s), float(s)


def _landmark(s: str) -> dict:
    """name:lat,lon[:h=height m][:w=width m][:px=pixel x] → dict."""
    parts = s.split(":")
    d = {"name": parts[0], "ll": _pair(parts[1])}
    for kv in parts[2:]:
        k, v = kv.split("=")
        d[k] = float(v)
    return d


def _drop_m(dist_m: float) -> float:
    """Height by which Earth curvature + standard atmospheric refraction (k≈0.13) make a distant object look lower."""
    return dist_m * dist_m / (2 * _R) * (1 - 0.13)


def frame_predict(cam: tuple[float, float], heading: float, hfov: float, width_px: float,
                  pts: list[dict], cam_h: float = 0.0) -> list[dict]:
    """Given camera position, heading and horizontal field of view, compute for each landmark: angle from the optical axis, pixel x, whether it is in the frame, angular height and angular width."""
    f = focal_px(width_px, hfov)
    out = []
    for p in pts:
        dist = distance(cam, p["ll"])
        rel = (bearing(cam, p["ll"]) - heading + 540) % 360 - 180
        row = {"name": p["name"], "dist_m": round(dist), "rel_deg": round(rel, 2)}
        half_w = math.degrees(math.atan2(p.get("w", 0) / 2, dist)) if dist > 0 else 0
        row["half_width_deg"] = round(half_w, 3)
        if abs(rel) < 90:
            x = width_px / 2 + f * math.tan(math.radians(rel))
            row["px"] = round(x)
            lo = width_px / 2 + f * math.tan(math.radians(rel - half_w))
            hi = width_px / 2 + f * math.tan(math.radians(rel + half_w))
            row["in_frame"] = "full" if lo >= 0 and hi <= width_px else ("partial" if hi >= 0 and lo <= width_px else "out")
        else:
            row["px"], row["in_frame"] = None, "behind"
        if "h" in p and dist > 0:
            top = p["h"] - _drop_m(dist) - cam_h
            row["top_elev_deg"] = round(math.degrees(math.atan2(top, dist)), 3)
            row["angular_height_deg"] = round(math.degrees(math.atan2(p["h"], dist)), 3)
            row["height_px"] = round(f * math.tan(math.radians(row["angular_height_deg"])))
        out.append(row)
    return out


def occluders(cam: tuple[float, float], pts: list[dict], cam_h: float = 0.0) -> list[str]:
    """Pairwise check: can a nearer landmark (with w, h given) fully block a farther one."""
    notes = []
    info = []
    for p in pts:
        d = distance(cam, p["ll"])
        info.append((p, d, bearing(cam, p["ll"])))
    for near, dn, bn in info:
        if "w" not in near or "h" not in near:
            for far, df, bf in info:
                gap = abs((bf - bn + 540) % 360 - 180)
                if far is not near and df > dn and gap < 3:
                    notes.append(f"{far['name']} may be blocked by {near['name']}: their bearings differ by only {gap:.2f}°, "
                                 f"{near['name']} has no w, h, can't compute (add them and rerun)")
            continue
        for far, df, bf in info:
            if far is near or df <= dn:
                continue
            half_n = math.degrees(math.atan2(near["w"] / 2, dn))
            half_f = math.degrees(math.atan2(far.get("w", 0) / 2, df))
            gap = abs((bf - bn + 540) % 360 - 180)
            top_n = math.degrees(math.atan2(near["h"] - _drop_m(dn) - cam_h, dn))
            top_f = math.degrees(math.atan2(far.get("h", 0) - _drop_m(df) - cam_h, df)) if "h" in far else None
            if gap + half_f <= half_n and (top_f is None or top_n >= top_f):
                notes.append(f"{far['name']} may be fully blocked by {near['name']} (bearing difference {gap:.2f}°, {near['name']} half-width {half_n:.2f}°)")
            elif gap < half_n + half_f and (top_f is None or top_n >= top_f):
                notes.append(f"{far['name']} is partly blocked by {near['name']} (bearing difference {gap:.2f}°)")
            elif gap < half_n + half_f and top_f is not None:
                notes.append(f"{far['name']} rises above {near['name']} and shows over the top ({top_f:.2f}° > {top_n:.2f}°)")
    return notes


def _ring_positions(spec: str) -> dict:
    """lat,lon:rmin:rmax:rstep:azstep → rings of candidate camera positions centered on a point."""
    ll, rmin, rmax, rstep, azstep = spec.split(":")
    c = _pair(ll)
    out = {}
    r = float(rmin)
    while r <= float(rmax) + 1e-6:
        az = 0.0
        while az < 360 - 1e-6:
            out[f"R{int(r)}m@{int(az)}"] = list(dest(c, az, r))
            az += float(azstep)
        r += float(rstep)
    return out


# ---------------------------------------------------------------- camera position from evenly spaced structures (spacing)

SPACING_DOC = """When a row of evenly spaced structures in the frame (viaduct piers, utility poles, street lights, guardrail posts) lies on a known line on the map,
solve for camera position, heading and focal length. Method in references/geometry.md 7.7.

Principle: each structure's pixel column x → offset angle from the frame center atan((x-cx)/f) → a ray; intersect the ray with the GeoJSON polyline
to get that structure's chainage (distance along the line). When camera position/heading/focal length are all right, the chainage difference between neighbors is constant and equals the standard span (--span).
Score pier = dispersion CV of the chainage differences + |log(mean chainage difference / span)| (plus --mono-penalty if the chainage is not monotonic).

With spacing alone, the solution is a band along the sight-line direction (in practice scattered within about 800 m). Give --ridge to score jointly with the skyline
(as in joint.py: tot = skyline rms + --flat-weight × flat-horizon penalty + --ridge-weight × spacing score),
which in practice narrows it to about 300 m. The skyline part downloads elevation tiles (the AWS Terrain Tiles used by terrain.py, cached in --cache).

Grouping in --cols: when the foreground breaks the structures into segments, group them with ';'; neighbor differences are only computed within a group (the difference across a break is not one span).
The monotonicity check still runs across all columns: the chainage of the whole row along the line must increase all the way or decrease all the way.

Output JSON:
  {"line": {…the selected line…},
   "params": {…all parameters of this run…},
   "best": <candidates[0]>,
   "candidates": [{"tot": total score, "rms": skyline rms (null without --ridge),
                   "pier": spacing score, "cam": [lat, lon], "f": focal length px, "H": heading°,
                   "cc": skyline pitch correction° (null without --ridge),
                   "span_m": mean solved span m, "d_first": distance to the first structure m,
                   "d_last": distance to the last structure m}, …top --top sorted by tot ascending]}
  The field names cam/f/H/cc follow the output of the script written on the spot in that real case (joint.py), so results from both can be compared directly."""


def _spacing_col_val(v) -> float:
    """One pixel column: a number, [x, …], or {"col": x, "prominence": …} as from imgprep.py piers."""
    if isinstance(v, dict):
        if "col" not in v:
            sys.exit(f"Structure record in the JSON has no col field: {v}")
        return float(v["col"])
    if isinstance(v, (list, tuple)):
        return float(v[0])
    return float(v)


def _spacing_cols(spec: str) -> list[list[float]]:
    """Pixel-column groups: '39,133,219;745,788' → [[39,133,219],[745,788]].

    Also accepts a JSON file ('@path' or ending in .json): list, list[list], list[{"col": …}],
    {"piers": [{"col": …}, …]} (output of imgprep.py piers), {"groups": [[…]]}, {"cols": […]} are all recognized.
    Key priority is piers > groups > cols: "cols" in the imgprep.py piers output is the column search range [x0, x1], not structure columns.
    Each group is sorted ascending; groups are ordered by their first column."""
    raw = spec
    if raw.startswith("@") or raw.lower().endswith(".json"):
        with open(raw[1:] if raw.startswith("@") else raw, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            for key in ("piers", "groups", "cols"):
                if key in data:
                    data = data[key]
                    break
            else:
                sys.exit("No piers / groups / cols found in the JSON")
        if data is None:
            sys.exit("piers / groups / cols in the JSON is empty")
        groups = data if (data and isinstance(data[0], (list, tuple))) else [data]
        groups = [[_spacing_col_val(v) for v in g] for g in groups]
    else:
        groups = [[float(v) for v in part.split(",") if v.strip() != ""] for part in raw.split(";")]
    groups = [sorted(g) for g in groups if g]
    groups.sort(key=lambda g: g[0])
    if not groups:
        sys.exit("--cols is empty")
    return groups


def _spacing_focals(spec: str, step: float) -> list[float]:
    """'1200,1281,1350' → list; '1200:1500' → arithmetic sequence with step. That real case used the list 1200,1281,1350,1430,1500."""
    if ":" in spec:
        parts = [float(v) for v in spec.split(":")]
        lo, hi = parts[0], parts[1]
        st = parts[2] if len(parts) > 2 else step
        n = int(round((hi - lo) / st))
        return [lo + st * k for k in range(n + 1)]
    return [float(v) for v in spec.split(",") if v.strip() != ""]


def _spacing_band(spec: str) -> tuple[float, float]:
    a, b = spec.split(":")
    return float(a), float(b)


def _spacing_line(path: str, name: str | None, index: int):
    """Take one polyline from a GeoJSON, return (Nx2 [lon,lat] list, info dict).

    --line-name matches a substring of properties.name; for features with the same name (two tracks, one per direction) use --line-index to pick which one.
    Without a name: if there is only one line use it; if there are several use the longest and print a note."""
    with open(path, encoding="utf-8") as fh:
        g = json.load(fh)
    feats = g.get("features") if isinstance(g, dict) and g.get("type") == "FeatureCollection" else None
    if feats is None:
        feats = [g] if isinstance(g, dict) else list(g)
    cands = []
    for f in feats:
        geom = f.get("geometry", f) or {}
        props = f.get("properties") or {}
        parts = []
        if geom.get("type") == "LineString":
            parts = [geom["coordinates"]]
        elif geom.get("type") == "MultiLineString":
            parts = list(geom["coordinates"])
        for c in parts:
            if len(c) < 2:
                continue
            ln = sum(math.dist(c[k], c[k + 1]) for k in range(len(c) - 1)) * 111000
            cands.append({"name": str(props.get("name") or ""), "coords": c, "length_m": ln})
    if not cands:
        sys.exit(f"No LineString in {path}")
    if name:
        hit = [c for c in cands if name in c["name"]]
        if not hit:
            names = sorted({c["name"] for c in cands if c["name"]})
            sys.exit(f"No line whose name contains {name!r}; names in the file: {names}")
        if index >= len(hit):
            sys.exit(f"{len(hit)} lines have a name containing {name!r}; --line-index can go up to {len(hit) - 1} only")
        pick = hit[index]
        note = f"line {index} of the {len(hit)} whose name contains {name!r}"
    elif len(cands) == 1:
        pick = cands[0]
        note = "this is the only line in the file"
    else:
        pick = max(cands, key=lambda c: c["length_m"])
        note = f"the file has {len(cands)} lines and no --line-name was given, so the longest was used; for another line give --line-name / --line-index"
    info = {"name": pick["name"], "note": note, "points": len(pick["coords"]),
            "length_m": round(pick["length_m"]),
            "ends": [[round(pick["coords"][0][1], 6), round(pick["coords"][0][0], 6)],
                     [round(pick["coords"][-1][1], 6), round(pick["coords"][-1][0], 6)]]}
    return pick["coords"], info


def _spacing_ridge(path: str) -> dict:
    """Read the output of terrain.py ridge {"ridge": [[x,y]…], "flat": [x0,x1], "hrow":…, "f0":…}.

    Also recognizes two handwritten formats: {"760": 826, …} (column → ridgeline row) and a bare [[x,y]…]."""
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    out = {"flat": None, "hrow": None, "f0": None}
    if isinstance(d, list):
        pts = d
    else:
        pts = d.get("ridge")
        out["flat"] = d.get("flat")
        out["hrow"] = d.get("hrow")
        out["f0"] = d.get("f0")
        if pts is None:
            pts = [[float(k), float(v)] for k, v in d.items() if str(k).lstrip("-").replace(".", "", 1).isdigit()]
    if isinstance(pts, dict):
        pts = [[float(k), float(v)] for k, v in pts.items()]
    pts = [[float(p[0]), float(p[1])] for p in pts]
    if len(pts) < 4:
        sys.exit(f"Too few ridgeline points in {path} ({len(pts)}), need at least 4")
    out["pts"] = sorted(pts)
    return out


def _spacing_run(args) -> dict:
    """Grid search over camera position × heading × focal length, computing the spacing score for each (optionally joint with the skyline). Returns the dict written to --out."""
    import numpy as np

    groups = _spacing_cols(args.cols)
    cols = [c for g in groups for c in g]
    if len(cols) < 3:
        sys.exit(f"--cols has only {len(cols)} columns, need at least 3 (geometry.md 7.7 recommends ≥6). "
                 "If you passed a JSON file: in imgprep.py piers output the structure columns are in the piers field; the cols field is the search range")
    pier = np.array(cols, float)

    pair_a, pair_b, off = [], [], 0                      # neighbor pairs within a group: only neighbors in the same segment are one span
    for g in groups:
        pair_a += list(range(off, off + len(g) - 1))
        pair_b += list(range(off + 1, off + len(g)))
        off += len(g)
    if not pair_a:
        sys.exit("Every --cols group has only one column; can't compute neighbor spacing")
    pair_a, pair_b = np.array(pair_a), np.array(pair_b)

    lat0, lon0 = args.center
    kx = 111320 * math.cos(math.radians(lat0))
    ky = 110540.0

    coords, line_info = _spacing_line(args.line, args.line_name, args.line_index)
    ll = np.array(coords, float)
    P = np.c_[(ll[:, 0] - lon0) * kx, (ll[:, 1] - lat0) * ky]     # local meter coordinates (x east, y north)
    seg_a, seg_b = P[:-1], P[1:]
    e = seg_b - seg_a
    seg_len = np.hypot(*e.T)
    chain0 = np.r_[0, np.cumsum(seg_len)][:-1]                    # chainage at the start of each segment

    hs = np.arange(args.headings[0], args.headings[1] + 1e-9, args.heading_step)
    focals = _spacing_focals(args.focals, args.focal_step)
    xs = np.arange(-args.radius, args.radius + 1e-9, args.grid)
    print(f"Line: {line_info['name'] or '(unnamed)'} {line_info['points']} points {line_info['length_m']} m ({line_info['note']})")
    print(f"Camera positions {len(xs)}×{len(xs)} cells × headings {len(hs)} × focal lengths {len(focals)}; {len(cols)} pixel columns in {len(groups)} groups, "
          f"standard span {args.span} m")

    dem = ridge = None
    if args.ridge:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import terrain                                            # noqa: PLC0415 — only needed for the joint skyline; don't make other subcommands wait for it
        ridge = _spacing_ridge(args.ridge)
        hrow = args.hrow if args.hrow is not None else ridge["hrow"]
        if hrow is None:
            sys.exit("The --ridge file has no hrow (the image row of the horizon in the photo); give one with --hrow")
        rp = np.array(ridge["pts"], float)
        rx, ry = rp[:, 0], rp[:, 1]
        flat = args.flat if args.flat is not None else (tuple(ridge["flat"]) if ridge["flat"] else None)
        flx = np.arange(flat[0], flat[1] + 1e-9, args.flat_step) if flat else None
        az = np.arange(0, 360, args.az_step)
        dist = args.sky_near * (args.sky_range / args.sky_near) ** (np.arange(args.sky_samples) / (args.sky_samples - 1))
        drop = dist ** 2 / (2 * terrain.R_EARTH) * (1 - terrain.K_REFRACTION)   # Earth curvature + atmospheric refraction
        dem = terrain.DEM((lat0, lon0), args.dem_range, args.dem_zoom, args.cache, args.proxy)
        print(f"Joint skyline: ridgeline {len(rx)} points, horizon row {hrow}, "
              f"flat-horizon columns {f'{flat[0]:g}–{flat[1]:g}' if flat else 'not used'}, DEM z{args.dem_zoom} radius {args.dem_range} m")

    res, nfit, t0 = [], 0, time.time()
    for iy, yy in enumerate(xs):
        for xx in xs:
            w = seg_a - np.array([xx, yy])
            hor = None
            for f in focals:
                offs = np.degrees(np.arctan((pier - args.cx) / f))            # offset angle of each structure from the frame center
                a = np.radians(hs[:, None] + offs[None, :])
                dx, dy = np.sin(a)[..., None], np.cos(a)[..., None]           # (heading, structure, 1)
                den = dx * e[:, 1] - dy * e[:, 0]
                with np.errstate(divide="ignore", invalid="ignore"):
                    t = (w[:, 0] * e[:, 1] - w[:, 1] * e[:, 0]) / den         # ray parameter = distance m
                    u = (w[:, 0] * dy - w[:, 1] * dx) / den                   # segment parameter 0–1
                ok = (t > args.min_dist) & (u >= 0) & (u <= 1)
                tt = np.where(ok, t, np.inf)
                i = np.argmin(tt, axis=2)                                     # take the nearest intersection
                tmin = np.take_along_axis(tt, i[..., None], 2)[..., 0]
                valid = np.all(np.isfinite(tmin), axis=1)
                if not valid.any():
                    continue
                uu = np.take_along_axis(u, i[..., None], 2)[..., 0]
                ch = chain0[i] + uu * seg_len[i]                              # chainage of each structure
                sp = np.abs(ch[:, pair_b] - ch[:, pair_a])
                m = sp.mean(axis=1)
                cv = sp.std(axis=1) / np.maximum(m, 1e-6)
                dch = np.diff(ch, axis=1)
                mono = np.all(dch > 0, axis=1) | np.all(dch < 0, axis=1)
                ps = cv + np.abs(np.log(np.maximum(m, 1e-3) / args.span)) + (~mono) * args.mono_penalty
                ps[~valid] = np.inf
                k = int(np.argmin(ps))
                if not np.isfinite(ps[k]) or ps[k] > args.pier_max:
                    continue
                nfit += 1
                H = float(hs[k])
                clat, clon = lat0 + yy / ky, lon0 + xx / kx
                rms = cc = None
                tot = float(ps[k])
                if dem is not None:
                    if hor is None:                                           # compute the horizon once per camera position, shared by all focal lengths
                        g0 = float(dem.sample(np.array([clat]), np.array([clon]))[0])
                        la, lo = terrain._dest_np(clat, clon, az, dist)
                        hh = dem.sample(la, lo)
                        hor = np.degrees(np.arctan2(hh - drop[None, :] - g0 - args.eye, dist[None, :])).max(axis=1)
                    r_off = np.degrees(np.arctan((rx - args.cx) / f))         # ridgeline points: pixel column → bearing offset
                    r_el = np.degrees(np.arctan((hrow - ry) / f))             #                   pixel row → elevation angle
                    mr = np.interp((H + r_off) % 360, az, hor, period=360)
                    diff = mr - r_el
                    cc = float(np.clip(np.median(diff), -args.cc_max, args.cc_max))   # pitch correction (horizon row estimate was off)
                    rms = float(np.sqrt(np.mean((diff - cc) ** 2)))
                    fpen = 0.0
                    if flx is not None:
                        mf = np.interp((H + np.degrees(np.arctan((flx - args.cx) / f))) % 360, az, hor, period=360)
                        fpen = float(np.mean(np.clip(mf - cc - args.flat_margin, 0, None)))  # the stretch that should be flat must not show mountains
                    tot = rms + args.flat_weight * fpen + args.ridge_weight * float(ps[k])
                res.append({"tot": tot, "rms": rms, "pier": float(ps[k]), "cam": [round(clat, 5), round(clon, 5)],
                            "f": int(f) if float(f).is_integer() else f, "H": H, "cc": cc, "span_m": round(float(m[k]), 1),
                            "d_first": round(float(tmin[k, 0])), "d_last": round(float(tmin[k, -1]))})
        if args.progress and (iy + 1) % args.progress == 0:
            print(f"  {iy + 1}/{len(xs)} rows, hits {nfit}, {time.time() - t0:.0f}s", file=sys.stderr)

    res.sort(key=lambda r: r["tot"])
    top = res[:args.top]
    return {"line": line_info,
            "params": {"cols": [[int(c) if float(c).is_integer() else c for c in g] for g in groups],
                       "span": args.span, "cx": args.cx, "center": [lat0, lon0], "radius": args.radius,
                       "grid": args.grid, "headings": list(args.headings), "heading_step": args.heading_step,
                       "focals": focals, "pier_max": args.pier_max, "min_dist": args.min_dist,
                       "ridge": args.ridge, "ridge_weight": args.ridge_weight if args.ridge else None,
                       "hrow": (args.hrow if args.hrow is not None else (ridge["hrow"] if ridge else None)),
                       "dem_zoom": args.dem_zoom if args.ridge else None},
            "n_fit": nfit, "best": top[0] if top else None, "candidates": top}


# ---------------------------------------------------------------- CLI

def _pair(s: str) -> tuple[float, float]:
    a, b = s.split(",")
    return float(a), float(b)



def _neg_coords(argv: list[str]) -> list[str]:
    """argparse treats negative coordinates like -1.45,-48.5 as option names; prefixing a space makes them plain values (float ignores the space). Needed for any photo in the southern or western hemisphere."""
    return [" " + a if re.match(r"^-\d[\d.]*(,-?[\d.]+)+$", a) else a for a in argv]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("convert", help="coordinate-system conversion")
    c.add_argument("--from", dest="src", required=True, choices=["wgs", "gcj", "bd", "bdmc"])
    c.add_argument("--to", dest="dst", required=True, choices=["wgs", "gcj", "bd", "bdmc"])
    c.add_argument("a", type=float)
    c.add_argument("b", type=float)

    b = sub.add_parser("bearing", help="bearing and distance between two points (wgs)")
    b.add_argument("p", type=_pair)
    b.add_argument("q", type=_pair)

    d = sub.add_parser("dest", help="walk a given number of meters from a point along a bearing (wgs)")
    d.add_argument("p", type=_pair)
    d.add_argument("--bearing", type=float, required=True)
    d.add_argument("--dist", type=float, required=True)

    r = sub.add_parser("range", help="estimate distance from an object's real size and pixel size")
    r.add_argument("--real", type=float, required=True, help="real size, meters")
    r.add_argument("--pixels", type=float, required=True, help="pixel size in the frame")
    r.add_argument("--image-width", type=float, required=True, help="pixel count of the side that hfov refers to")
    r.add_argument("--hfov", help="field of view of that side (degrees); if the zoom is unknown give a range, e.g. 12:70, to output a distance range")
    r.add_argument("--equiv-focal", type=float, help="35mm equivalent focal length; if given, the field of view is computed automatically")
    r.add_argument("--side", choices=["long", "short"], default="short", help="whether image-width is the long side or the short side")

    f = sub.add_parser("fov", help="equivalent focal length → field of view")
    f.add_argument("focal", type=float)

    ln = sub.add_parser("line", help="alignment line: near is in front of far → the extension line the camera position is on; outputs sample points along it")
    ln.add_argument("--near", type=_pair, required=True, help="lat,lon of the nearer object in the frame")
    ln.add_argument("--far", type=_pair, required=True, help="lat,lon of the farther object in the frame, aligned with near")
    ln.add_argument("--range", default="0:2000", help="distance range extending outward from near (meters), e.g. 50:1500")
    ln.add_argument("--step", type=float, default=100)
    ln.add_argument("--out", help="write {name:[lat,lon]}, can be passed to tiles.py mark")

    it = sub.add_parser("intersect", help="intersect two sight lines (with error radius)")
    it.add_argument("--align1", help="near_lat,near_lon:far_lat,far_lon (first aligned pair)")
    it.add_argument("--align2", help="second aligned pair, same format")
    it.add_argument("--sight1", help="lat,lon@bearing: compass bearing from the camera position to this landmark")
    it.add_argument("--sight2", help="same as above")
    it.add_argument("--sigma", type=float, default=1.0, help="bearing error of each sight line (degrees), default 1")

    fr = sub.add_parser("frame", help="frame check before excluding: from a candidate camera position, should a landmark appear in the frame, and would it be blocked",
                        formatter_class=argparse.RawDescriptionHelpFormatter, description=(
        "Purpose: before you use \"X is not in the frame\" to exclude a candidate camera position or a whole direction, first compute whether X falls in the frame at all.\n"
        "Heading can be given two ways: --heading directly; or --anchor with an identified landmark and its pixel x in the frame,\n"
        "and the script back-computes the heading for each field of view (the smaller the field of view, the narrower the frame, the easier nearby landmarks fall out of it).\n"
        "If the field of view is unknown (video screenshot, crop, zoom), give a range; the script sweeps it and reports over which field-of-view range each landmark enters the frame.\n"
        "Only a landmark that is \"fully in the frame over the whole field-of-view range and not blocked\" can have its absence used to exclude."))
    pos = fr.add_mutually_exclusive_group(required=True)
    pos.add_argument("--at", action="append", type=_pair, help="candidate camera position lat,lon, repeatable")
    pos.add_argument("--points", help="candidate camera positions JSON {name:[lat,lon]}")
    pos.add_argument("--ring", help="lat,lon:min_radius:max_radius:radius_step:bearing_step — place candidate camera positions in rings around a landmark")
    fr.add_argument("--heading", type=float, help="camera heading (compass angle)")
    fr.add_argument("--anchor", help="name:lat,lon:px=pixel_x — an identified landmark and its horizontal pixel position in the frame")
    fr.add_argument("--width", type=float, required=True, help="frame width in pixels (same side as hfov)")
    fr.add_argument("--hfov", default="65", help="horizontal field of view, single value or range 12:70 (default 65)")
    fr.add_argument("--pt", action="append", default=[], type=_landmark,
                    help="landmark to check name:lat,lon[:h=height_m][:w=width_m], repeatable; h, w are used for angular height and occlusion")
    fr.add_argument("--cam-h", type=float, default=0.0, help="camera height, same datum as landmark h (both height above ground or both elevation above sea level)")
    fr.add_argument("--min-px", type=float, default=12, help="minimum pixel height of a landmark in the frame to count as \"should be visible\"")
    fr.add_argument("--out", help="write the full result as JSON")

    bg = sub.add_parser("bearings", help="bearing, angular width and distance of each GeoJSON feature from the camera position; with --target, sorted by bearing difference (bearing first, then identify the structure)")
    bg.add_argument("--at", type=_pair, required=True, help="camera position lat,lon")
    bg.add_argument("--geojson", required=True, help="output of osm.py geom (building footprints, lines, points)")
    bg.add_argument("--target", type=float, help="true bearing of the target (the bearing of that tower in the photo, computed by sun.py compass)")
    bg.add_argument("--tol", type=float, default=8, help="mark as candidates those within this many degrees of bearing difference")
    bg.add_argument("--max-dist", type=float, default=3000, help="only consider features within this distance (meters)")
    bg.add_argument("--out", help="write {name: [lat, lon]}, can be passed to tiles.py mark")

    sp = sub.add_parser("spacing", help="camera position from a row of evenly spaced structures (bridge piers, utility poles): pixel columns → rays → intersect with the line → neighbor chainage differences should be constant",
                        formatter_class=argparse.RawDescriptionHelpFormatter, description=SPACING_DOC)
    sp.add_argument("--cols", required=True,
                    help="pixel columns of the structures, comma-separated; when blocked into segments, group with ';' (remember the quotes), e.g. '39,133,219,296,369;745,788,829'. "
                         "Can also be a JSON file (@cols.json); the output of imgprep.py piers (piers field) works directly. "
                         "First check the piers --sheet to remove peaks that aren't structures and split into segments by foreground occlusion; these two are the top reasons for getting no solution")
    sp.add_argument("--line", required=True, help="the line the structures are on, GeoJSON (railway/power line fetched by osm.py)")
    sp.add_argument("--line-name", help="pick a line by substring of properties.name; if not given, use the longest line in the file")
    sp.add_argument("--line-index", type=int, default=0, help="which one to pick when several lines share the name (one track per direction), default 0")
    sp.add_argument("--span", type=float, required=True, help="standard span m (high-speed rail simply supported box girder 32, utility poles per local standard); if unsure, run once with each of several values")
    sp.add_argument("--center", type=_pair, required=True, help="center of the candidate area lat,lon (also the origin of the local plane coordinates)")
    sp.add_argument("--radius", type=float, default=1500, help="half side length of the candidate area m, default 1500 (searches a ±radius square)")
    sp.add_argument("--grid", type=float, default=50, help="camera-position grid spacing m, default 50")
    sp.add_argument("--headings", type=_spacing_band, default=(0.0, 360.0), help="heading search range lo:hi (degrees), default 0:360; narrow it if you know the rough heading, much faster")
    sp.add_argument("--heading-step", type=float, default=0.25, help="heading step (degrees), default 0.25")
    sp.add_argument("--focals", required=True, help="focal lengths (pixels), list 1200,1281,1350,1430,1500 or range 1200:1500[:step]")
    sp.add_argument("--focal-step", type=float, default=50, help="step when --focals is a range, default 50")
    sp.add_argument("--cx", type=float, default=640, help="horizontal center pixel of the frame, default 640 (photo 1280 wide); for a cropped photo compute it from the crop")
    sp.add_argument("--min-dist", type=float, default=100, help="minimum distance for an intersection to count m, default 100 (filters out false intersections at the camera's feet)")
    sp.add_argument("--pier-max", type=float, default=0.08, help="solutions with a spacing score above this are dropped, default 0.08")
    sp.add_argument("--mono-penalty", type=float, default=1.0, help="penalty for non-monotonic chainage (rays hitting both sides of the line), default 1.0")
    sp.add_argument("--top", type=int, default=25, help="number of top results to output, default 25")
    sp.add_argument("--progress", type=int, default=10, help="report progress to stderr every this many grid rows, 0=off")
    sp.add_argument("--out", help="write the result as JSON (structure above)")
    sp.add_argument("--ridge", help="ridgeline pixel points JSON (output of terrain.py ridge); if given, score jointly with the skyline, downloads elevation tiles")
    sp.add_argument("--hrow", type=float, help="pixel row of the horizon in the photo; not needed if the --ridge file has hrow")
    sp.add_argument("--flat", type=_spacing_band, help="column range in the frame that should be a flat horizon x0:x1 (e.g. 0:280); defaults to flat from the --ridge file")
    sp.add_argument("--flat-step", type=float, default=20, help="sampling step for flat-horizon columns px, default 20")
    sp.add_argument("--flat-margin", type=float, default=1.0, help="how many degrees the flat horizon may rise above the corrected horizon, default 1.0")
    sp.add_argument("--flat-weight", type=float, default=1.5, help="weight of the flat-horizon penalty, default 1.5")
    sp.add_argument("--ridge-weight", "--pier-weight", dest="ridge_weight", type=float, default=2.0,
                    help="weight of the spacing score in joint scoring, default 2.0 (tot = skyline rms + flat-weight×flat-horizon penalty + this weight×spacing score)")
    sp.add_argument("--cc-max", type=float, default=0.8, help="maximum absolute pitch correction (degrees), default 0.8")
    sp.add_argument("--eye", type=float, default=1.6, help="camera height above ground m, default 1.6")
    sp.add_argument("--dem-zoom", type=int, default=13, help="elevation tile zoom level, default 13")
    sp.add_argument("--dem-range", type=float, default=18000, help="DEM mosaic radius m, default 18000 (must cover the candidate area + the visible mountains)")
    sp.add_argument("--sky-range", type=float, default=16000, help="how far out the skyline looks m, default 16000")
    sp.add_argument("--sky-near", type=float, default=100, help="how near the skyline sampling starts m, default 100")
    sp.add_argument("--sky-samples", type=int, default=400, help="number of distances sampled per bearing, default 400 (dense near, sparse far)")
    sp.add_argument("--az-step", type=float, default=0.1, help="step of the horizon bearing table (degrees), default 0.1")
    sp.add_argument("--cache", type=Path, default=Path(".geo-cache/dem"), help="elevation tile cache directory, default .geo-cache/dem (same as terrain.py)")
    sp.add_argument("--proxy", default=os.environ.get("GEO_PROXY"), help="proxy URL or 'direct'")

    args = ap.parse_args(_neg_coords(sys.argv[1:]))
    if args.cmd == "convert":
        x, y = convert(args.a, args.b, args.src, args.dst)
        print(f"{x:.7f},{y:.7f}")
    elif args.cmd == "bearing":
        print(f"bearing={bearing(args.p, args.q):.1f}deg distance={distance(args.p, args.q):.1f}m")
    elif args.cmd == "dest":
        la, lo = dest(args.p, args.bearing, args.dist)
        print(f"{la:.7f},{lo:.7f}")
    elif args.cmd == "range":
        if args.hfov is None:
            if args.equiv_focal is None:
                ap.error("--hfov or --equiv-focal is required")
            lf, sf = fov_from_equiv_focal(args.equiv_focal)
            lo = hi = lf if args.side == "long" else sf
        else:
            lo, hi = _band_f(args.hfov)
        if lo == hi:
            dist = range_from_size(args.real, args.pixels, args.image_width, lo)
            print(f"fov={lo:.1f}deg focal={focal_px(args.image_width, lo):.0f}px range={dist:.0f}m")
        else:
            steps = 6
            for k in range(steps + 1):
                hf = lo * (hi / lo) ** (k / steps)          # geometric sampling over zoom
                dist = range_from_size(args.real, args.pixels, args.image_width, hf)
                print(f"fov={hf:5.1f}deg focal={focal_px(args.image_width, hf):6.0f}px range={dist:7.0f}m")
            print(f"Field of view {lo:g}–{hi:g}° → distance {range_from_size(args.real, args.pixels, args.image_width, hi):.0f}–"
                  f"{range_from_size(args.real, args.pixels, args.image_width, lo):.0f} m. Until the zoom is pinned down, look for candidates over the whole range")
    elif args.cmd == "frame":
        if args.heading is None and not args.anchor:
            ap.error("--heading or --anchor is required")
        if args.at:
            cams = {f"P{i + 1}": list(p) for i, p in enumerate(args.at)}
        elif args.points:
            with open(args.points, encoding="utf-8") as fh:
                cams = {k: v[:2] for k, v in json.load(fh).items()}
        else:
            cams = _ring_positions(args.ring)
        anchor = _landmark(args.anchor) if args.anchor else None
        lo, hi = _band_f(args.hfov)
        hfovs = [lo] if lo == hi else [lo * (hi / lo) ** (k / 40) for k in range(41)]
        pts = args.pt + ([anchor] if anchor else [])
        W = args.width
        full: dict = {}
        summary_rows = []
        for cname, cll in cams.items():
            cam = tuple(cll)
            per_hfov = []
            status: dict[str, list[float]] = {p["name"]: [] for p in args.pt}
            min_px: dict[str, float] = {}
            for hf in hfovs:
                if anchor:
                    f = focal_px(W, hf)
                    off = math.degrees(math.atan((anchor["px"] - W / 2) / f))
                    hd = (bearing(cam, anchor["ll"]) - off) % 360
                else:
                    hd = args.heading
                rows = frame_predict(cam, hd, hf, W, pts, args.cam_h)
                per_hfov.append({"hfov": round(hf, 2), "heading": round(hd, 2), "points": rows})
                for r in rows:
                    if r["name"] in status and r["in_frame"] == "full":
                        status[r["name"]].append(hf)
                        if "height_px" in r:
                            min_px[r["name"]] = min(min_px.get(r["name"], 1e9), r["height_px"])
            occ = occluders(cam, pts, args.cam_h)
            full[cname] = {"ll": cll, "frames": per_hfov, "occlusion": occ}
            verdict = {}
            for p in args.pt:
                inside = status[p["name"]]
                hidden = any(o.startswith(p["name"] + " may be ") for o in occ)
                whole_range = False
                if len(hfovs) == 1:
                    v = "fully in frame" if inside else "not fully in frame"
                elif len(inside) == len(hfovs):
                    v = "in frame over the whole field-of-view range"
                    whole_range = True
                elif inside:
                    v = f"in frame at field of view {min(inside):.0f}–{max(inside):.0f}°, out of frame otherwise"
                else:
                    v = "not in frame over the whole field-of-view range"
                if hidden:
                    v += "; may be blocked"
                small = False
                if inside and "h" not in p:
                    v += "; no height h given, not checked whether it is big enough or shows above the foreground"
                    small = True
                elif inside and min_px.get(p["name"], 0) < args.min_px:
                    v += f"; only {min_px.get(p['name'], 0):.0f} px tall at minimum, may not be visible"
                    small = True
                can_exclude = (whole_range or (len(hfovs) == 1 and bool(inside))) \
                    and not hidden and not small
                verdict[p["name"]] = {"verdict": v, "absence_excludes": can_exclude}
            full[cname]["verdict"] = verdict
            summary_rows.append((cname, cll, verdict))
        for cname, cll, verdict in summary_rows[:60]:
            print(f"{cname} {cll[0]:.5f},{cll[1]:.5f}")
            frames = full[cname]["frames"]
            for n, v in verdict.items():
                print(f"   {n}: {v['verdict']} → absence {'can' if v['absence_excludes'] else 'cannot'} exclude")
            if len(hfovs) == 1:
                f0 = frames[0]
                print(f"   heading {f0['heading']}°: " + "; ".join(
                    f"{r['name']} x={r['px']} {r['in_frame']}" + (f" height {r['height_px']}px" if "height_px" in r else "")
                    for r in f0["points"]))
            else:
                a, b = frames[0], frames[-1]
                print(f"   as field of view goes {a['hfov']}°→{b['hfov']}°, heading is between {a['heading']}°→{b['heading']}°")
            for o in full[cname]["occlusion"]:
                print(f"   occlusion: {o}")
        if len(summary_rows) > 60:
            print(f"  …{len(summary_rows)} camera positions in total, see --out for the full result")
        excl = [c for c, _, v in summary_rows if any(x["absence_excludes"] for x in v.values())]
        print(f"\nOf {len(summary_rows)} candidate camera positions, {len(excl)} can be excluded by \"a landmark is not in the frame\""
              " (provided the landmark really is absent from the photo, and no unlisted nearby building blocks that direction)")
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                json.dump(full, fh, ensure_ascii=False, indent=1)
            excl_pts = {c: cams[c] for c in excl}
            keep_pts = {c: cams[c] for c in cams if c not in excl}
            base = args.out.rsplit(".", 1)[0]
            with open(base + "_keep.json", "w", encoding="utf-8") as fh:
                json.dump(keep_pts, fh, indent=1)
            with open(base + "_excluded.json", "w", encoding="utf-8") as fh:
                json.dump(excl_pts, fh, indent=1)
            print(f"-> {args.out} (kept camera positions {base}_keep.json, excludable ones {base}_excluded.json, both can go straight to tiles.py mark)")
    elif args.cmd == "bearings":
        with open(args.geojson, encoding="utf-8") as fh:
            gj = json.load(fh)
        rows = []
        for f in gj.get("features", []):
            g = f.get("geometry") or {}
            t = g.get("type")
            if t == "Polygon":
                coords = [(c[1], c[0]) for c in g["coordinates"][0]]
            elif t == "MultiPolygon":
                coords = [(c[1], c[0]) for poly in g["coordinates"] for c in poly[0]]
            elif t == "LineString":
                coords = [(c[1], c[0]) for c in g["coordinates"]]
            elif t == "Point":
                coords = [(g["coordinates"][1], g["coordinates"][0])]
            else:
                continue
            dists = [distance(args.at, c) for c in coords]
            if min(dists) > args.max_dist:
                continue
            brgs = [bearing(args.at, c) for c in coords]
            mx = sum(math.cos(math.radians(b)) for b in brgs)
            my = sum(math.sin(math.radians(b)) for b in brgs)
            center = math.degrees(math.atan2(my, mx)) % 360
            rel = [((b - center + 180) % 360) - 180 for b in brgs]
            props = f.get("properties") or {}
            tags = props.get("tags") or props
            name = tags.get("name") or f.get("id") or ""
            rows.append({"name": str(name), "bearing": round(center, 1), "span_deg": round(max(rel) - min(rel), 1),
                         "dist_m": round(min(dists)), "height": tags.get("height") or tags.get("building:height") or "",
                         "levels": tags.get("building:levels") or "", "kind": tags.get("building") or tags.get("man_made") or tags.get("power") or "",
                         "center": [round(sum(c[0] for c in coords) / len(coords), 6), round(sum(c[1] for c in coords) / len(coords), 6)]})
        if args.target is not None:
            for r in rows:
                r["d_bearing"] = round(((r["bearing"] - args.target + 180) % 360) - 180, 1)
            rows.sort(key=lambda r: abs(r["d_bearing"]))
        else:
            rows.sort(key=lambda r: r["bearing"])
        print(f"{len(rows)} features (within {args.max_dist:.0f} m)" + (f", target bearing {args.target}°, those within ±{args.tol}° marked *" if args.target is not None else ""))
        print(f"{'':1} {'brg':>6} {'span':>5} {'dist':>6} {'h/lvl':>7}  name/kind")
        for r in rows[:60]:
            star = "*" if args.target is not None and abs(r["d_bearing"]) <= args.tol else " "
            print(f"{star} {r['bearing']:>6.1f} {r['span_deg']:>5.1f} {r['dist_m']:>6} {str(r['height'] or r['levels']):>7}  {r['name'][:28]} {r['kind']}")
        if args.target is not None:
            hits = [r for r in rows if abs(r["d_bearing"]) <= args.tol]
            print(f"{len(hits)} match the bearing" + ("; when nothing matches, first suspect the heading and zoom, then suspect OSM hasn't mapped it" if not hits else ". Nearby buildings with a large angular width block those behind; only tall ones can show above"))
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                json.dump({(f"{'*' if args.target is not None and abs(r['d_bearing']) <= args.tol else ''}{r['bearing']:.0f}° {r['name'][:12]}"): r["center"] for r in rows}, fh, ensure_ascii=False, indent=1)
            print(f"-> {args.out}")
    elif args.cmd == "spacing":
        out = _spacing_run(args)
        cands = out["candidates"]
        if not cands:
            print(f"No solution: {out['n_fit']} combinations passed --pier-max {args.pier_max}. Check in this order: "
                  "① --cols contains peaks that aren't structures (foreground highlights, railings, trees); clean them out against the imgprep.py piers --sheet; "
                  "② structures broken by the foreground weren't split into segments with ';' (the difference across a break is not one span, so the whole group is ruined); "
                  "③ loosen --pier-max; ④ check that --span, --cx, --cols were measured on the same image; "
                  "⑤ only then suspect that --center/--radius encloses the wrong area")
        else:
            print(f"{out['n_fit']} passed --pier-max; top {len(cands)} by tot:")
            print(f"{'tot':>6} {'rms':>6} {'pier':>6} {'span':>6}  {'camera':^17} {'f':>6} {'H':>7} {'cc':>6} {'d_1st':>6} {'d_last':>6}")
            for r in cands:
                rms = "     -" if r["rms"] is None else format(r["rms"], "6.3f")
                cc = "     -" if r["cc"] is None else format(r["cc"], "6.2f")
                print(f"{r['tot']:6.3f} {rms} {r['pier']:6.3f} {r['span_m']:6.1f}  "
                      f"{r['cam'][0]:.5f},{r['cam'][1]:.5f} {r['f']:6.0f} {r['H']:7.2f} {cc} "
                      f"{r['d_first']:6.0f} {r['d_last']:6.0f}")
            b = cands[0]
            spread = max(distance(b["cam"], r["cam"]) for r in cands)
            print(f"Best solution: {b['cam'][0]:.5f},{b['cam'][1]:.5f} heading {b['H']:.2f}° focal length {b['f']:.0f}px "
                  f"mean span {b['span_m']:.1f} m (nominal {args.span:g})")
            print(f"Top {len(cands)} scattered within {spread:.0f} m" + (
                ". With spacing alone the solution is a band along the sight line; giving --ridge for joint scoring with the skyline narrows it (geometry.md 7.7)"
                if not args.ridge else ". Check the pier positions of the best solution on satellite imagery; don't rely on the score alone"))
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                json.dump(out, fh, ensure_ascii=False, indent=1)
            print(f"-> {args.out}")
    elif args.cmd == "fov":
        lf, sf = fov_from_equiv_focal(args.focal)
        print(f"4:3 long_side={lf:.1f}deg short_side={sf:.1f}deg")
    elif args.cmd == "line":
        origin, brg = ray_from_alignment(args.near, args.far)
        a, b = (float(x) for x in args.range.split(":"))
        pts, k, dcur = {}, 0, a
        while dcur <= b + 1e-6:
            pts[f"L{int(dcur)}m"] = [round(v, 7) for v in dest(origin, brg, dcur)]
            dcur += args.step
            k += 1
        print(f"Camera position is on the ray beyond near at bearing {brg:.1f}°; {k} sample points")
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                json.dump(pts, fh, indent=1)
            print(f"-> {args.out}")
        else:
            for name, ll in pts.items():
                print(f"  {name}: {ll[0]},{ll[1]}")
    elif args.cmd == "intersect":
        def ray(align, sight):
            if align:
                n, fr = align.split(":")
                return ray_from_alignment(_pair(n), _pair(fr))
            if sight:
                ll, brg = sight.split("@")
                return ray_from_sighting(_pair(ll), float(brg))
            ap.error("each line needs --alignN or --sightN")
        r1, r2 = ray(args.align1, args.sight1), ray(args.align2, args.sight2)
        res = intersect_with_error(r1, r2, args.sigma)
        if res is None:
            print("The two lines are parallel, or the intersection is behind the objects (check whether near/far are swapped)")
        else:
            print(json.dumps(res, ensure_ascii=False))
            if res["crossing_angle_deg"] < 15:
                print("Note: the lines cross at less than 15°, so the intersection is very sensitive to bearing error; find another line with a larger crossing angle")


if __name__ == "__main__":
    # Chinese-locale Windows outputs GBK by default: it crashes on m², ñ, and the Chinese the agent reads is garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
