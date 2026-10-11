#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy"]
# ///
"""Solve the camera position (camera resection): ≥4 points in the photo whose locations you can identify → camera lat/lon, height, heading, pitch, roll, field of view + error radius.

Suited to window views, high-rise downward shots, views across a river and other photos where "you can pick out several points on satellite imagery". Compared with a two-sight-line intersection it also uses height and pitch information, and can work out the floor.
Level shots (standing on the ground photographing a distant tower, bridge, pier) also work: fix height and give the eye height.

  solve    solve the camera position; the output includes a per-point check (leave_one_out): drop one point at a time, re-solve, and see how far off the other points' prediction of it is
  check    score discrete candidate camera positions: use when several places all fit and you must pick one; each candidate solves only the heading, then is rescored with each point dropped in turn;
           only robust Δchi2 > 9 (dropping any one point can't rescue it) counts as inconsistent with the photo
  project  with a known camera position, project a set of lat/lon points onto the photo (check whether riverbanks, roads, buildings line up);
           with --horizon <sea horizon row> it validates pitch: the target's depression angle is not the camera's pitch; a sea horizon at the frame center means pitch≈0

spec.json format:
{
  "image_size": [1476, 827],
  "points": [
    {"name": "bridgehead", "px": [212, 431], "ll": [lat, lon], "h": 470},
    {"name": "spire", "px": [1180, 120], "ll": [lat, lon], "h": 620}
  ],
  "init": {"at": [lat, lon], "height": 560, "heading": 190, "pitch": -8, "hfov": 65},
  "fix": ["hfov"]
}
- px: pixel coordinates of the point in the photo (original image, top-left is 0,0).
- h: height of the point, **on the same datum as the camera height**. Using elevation above sea level throughout is the most reliable: ground points via `terrain.py elev`, rooftop = ground elevation + building height.
- init: rough camera position and heading; if unknown, give the center of the candidate area, and --restarts will start from multiple points within --search-radius.
- fix: parameters that can be fixed (hfov, roll, height); if you know the focal length, fix hfov; more stable with few points.

Examples:
  pose.py solve spec.json --photo photo.jpg --out pose.png --search-radius 500
  pose.py check spec.json --cands cands.json        # cands.json: {"candA": [lat, lon], "candB": [lat, lon, eye_elevation]}
  pose.py project --pose pose.json --points river.json --photo photo.jpg --out check.png
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

NAMES = ["east_m", "north_m", "height", "heading", "pitch", "roll", "focal_px"]


def _frame(lat0: float):
    return 111320.0 * math.cos(math.radians(lat0)), 110540.0


def project(params: np.ndarray, pts_enu: np.ndarray, W: int, H: int) -> tuple[np.ndarray, np.ndarray]:
    e, n, u, yaw, pitch, roll, f = params
    ps, ts, rs = map(math.radians, (yaw, pitch, roll))
    fwd = np.array([math.sin(ps) * math.cos(ts), math.cos(ps) * math.cos(ts), math.sin(ts)])
    r0 = np.array([math.cos(ps), -math.sin(ps), 0.0])
    u0 = np.cross(r0, fwd)
    right = r0 * math.cos(rs) + u0 * math.sin(rs)
    up = -r0 * math.sin(rs) + u0 * math.cos(rs)
    v = pts_enu - np.array([e, n, u])
    z = v @ fwd
    x, y = v @ right, v @ up
    zz = np.where(z > 1e-3, z, np.nan)
    return np.stack([W / 2 + f * x / zz, H / 2 - f * y / zz], axis=1), z


def residuals(p, pts, obs, W, H):
    uv, z = project(p, pts, W, H)
    r = (uv - obs).ravel()
    return np.where(np.isnan(r), 5000.0, r)


def lm(p0, free, pts, obs, W, H, iters=200):
    p = p0.astype(float).copy()
    steps = np.array([0.5, 0.5, 0.5, 0.01, 0.01, 0.01, 1.0])
    lam = 1e-2
    r = residuals(p, pts, obs, W, H)
    cost = float(r @ r)
    J = None
    for _ in range(iters):
        J = np.zeros((r.size, len(free)))
        for j, k in enumerate(free):
            dp = p.copy()
            dp[k] += steps[k]
            J[:, j] = (residuals(dp, pts, obs, W, H) - r) / steps[k]
        A = J.T @ J
        g = J.T @ r
        improved = False
        for _ in range(10):
            try:
                delta = -np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-9), g)
            except np.linalg.LinAlgError:
                lam *= 10
                continue
            cand = p.copy()
            cand[free] += delta
            rc = residuals(cand, pts, obs, W, H)
            cc = float(rc @ rc)
            if cc < cost:
                p, r, cost, lam, improved = cand, rc, cc, max(lam / 3, 1e-7), True
                break
            lam *= 4
        if not improved or float(np.abs(delta).max()) < 1e-4:
            break
    return p, cost, J


def solve(spec: dict, search_radius: float, restarts: int, seed: int = 7,
          pt_sigma: float = 5.0) -> dict:
    W, H = spec["image_size"]
    init = spec.get("init", {})
    lat0, lon0 = init["at"]
    kx, ky = _frame(lat0)
    pts = np.array([[(q["ll"][1] - lon0) * kx, (q["ll"][0] - lat0) * ky, q.get("h", 0.0)] for q in spec["points"]])
    obs = np.array([q["px"] for q in spec["points"]], dtype=float)
    hfov = init.get("hfov", 65)
    f0 = (W / 2) / math.tan(math.radians(hfov / 2))
    fixed = set(spec.get("fix", []))
    free = [i for i, name in enumerate(NAMES)
            if not ((name == "focal_px" and "hfov" in fixed) or (name == "roll" and "roll" in fixed)
                    or (name == "height" and "height" in fixed))]
    n_obs, k = obs.size, len(free)
    if n_obs < k:
        raise SystemExit(f"Too few points: {len(obs)} points give only {n_obs} equations for {k} unknowns. Give at least {math.ceil(k / 2)} points, or fix hfov/roll with fix")
    base = np.array([0.0, 0.0, init.get("height", 30.0), init.get("heading", 0.0), init.get("pitch", 0.0), 0.0, f0])
    rng = np.random.default_rng(seed)
    best = None
    for t in range(max(1, restarts)):
        p0 = base.copy()
        if t:
            ang = rng.uniform(0, 2 * math.pi)
            rad = search_radius * math.sqrt(rng.uniform())
            p0[0], p0[1] = rad * math.sin(ang), rad * math.cos(ang)
            if "height" not in fixed:
                p0[2] = max(1.0, base[2] * rng.uniform(0.5, 1.5))
            p0[3] = (base[3] + rng.uniform(-90, 90)) % 360 if "heading" in init else rng.uniform(0, 360)
            p0[4] = base[4] + rng.uniform(-15, 15)
        p, cost, J = lm(p0, free, pts, obs, W, H)
        if best is None or cost < best[1]:
            best = (p, cost, J)
    p, cost, J = best
    dof = n_obs - k
    rms = math.sqrt(cost / len(obs))
    out = {"camera_ll": [round(lat0 + p[1] / ky, 7), round(lon0 + p[0] / kx, 7)], "height": round(p[2], 1),
           "heading": round(p[3] % 360, 2), "pitch": round(p[4], 2), "roll": round(p[5], 2),
           "hfov": round(2 * math.degrees(math.atan((W / 2) / p[6])), 2), "rms_px": round(rms, 2),
           "points": len(obs), "unknowns": k, "dof": dof}
    uv, _ = project(p, pts, W, H)
    out["residuals_px"] = {q.get("name", str(i)): [round(float(a), 1), round(float(b), 1)]
                           for i, (q, (a, b)) in enumerate(zip(spec["points"], uv - obs))}
    if dof > 0 and J is not None:
        sigma2 = cost / dof
        try:
            cov = sigma2 * np.linalg.inv(J.T @ J)
            idx = {v: i for i, v in enumerate(free)}
            se = [math.sqrt(max(cov[idx[i], idx[i]], 0)) if i in idx else 0.0 for i in range(len(NAMES))]
            out["sigma"] = {"east_m": round(se[0], 1), "north_m": round(se[1], 1), "height_m": round(se[2], 1),
                            "heading_deg": round(se[3], 2)}
            out["radius_px_only_m"] = round(3 * math.hypot(se[0], se[1]), 1)   # 3σ from pixel noise only; doesn't cover the ground truth, don't use it directly
        except np.linalg.LinAlgError:
            out["sigma"] = "singular: the points are too concentrated (all on one line or in one direction); add points in different directions and at different distances"
    else:
        out["sigma"] = "zero degrees of freedom, can't estimate the error; add more points"
    out["_params"] = [float(x) for x in p]
    out["_frame"] = {"lat0": lat0, "lon0": lon0, "image_size": [W, H]}
    mc = mc_radius(p, free, pts, obs, W, H, pt_sigma, rms)
    out["radius_m"] = mc["radius_m"]
    out["radius_note"] = (f"95% radius, Monte Carlo {mc['trials']} trials: control-point coordinates perturbed by ±{pt_sigma:g} m"
                          f" (--pt-sigma), pixels by ±{mc['px_sigma_used']:g} px. "
                          f"Median offset {mc['p50_m']:g} m. The old pixel-noise-only measure is in radius_px_only_m; it doesn't cover the ground truth.")
    out["pt_sigma_m"] = pt_sigma
    out["leave_one_out"] = leave_one_out(p, free, pts, obs, W, H, spec["points"])
    return out


def mc_radius(p, free, pts, obs, W, H, pt_sigma: float, rms_px: float,
              trials: int = 60, seed: int = 11, px_sigma: float | None = None) -> dict:
    """Control-point coordinate error doesn't propagate into the reprojection residuals: shift all points the same way, the camera shifts along, and the residuals don't change at all.
    So the inv(JtJ) covariance is blind in that direction: in tests, with 5 m coordinate noise the 3σ radius covers the ground truth only 67% of the time (should be 97%).
    Here the control points are perturbed by pt_sigma and the pixels by rms, re-solved from the converged solution, and the 95th percentile of the position offset is taken as the radius.
    The pixel path doesn't subtract the coordinate-error contribution: the slight double-counting happens to make up for the underestimate from "re-solving from the converged solution can't reach large offsets".
    Calibration in tests: the version that subtracts it on the pixel path covers 91%, without subtracting 95%; validated on three uncalibrated geometries, 286/300 = 95%."""
    rng = np.random.default_rng(seed)
    if px_sigma is None:
        px_sigma = max(rms_px, 1.0)
    offs = []
    for _ in range(trials):
        pts_j = pts.copy()
        if pt_sigma > 0:
            pts_j[:, :2] += rng.normal(0, pt_sigma, (len(pts_j), 2))
        q, _, _ = lm(p.copy(), free, pts_j, obs + rng.normal(0, px_sigma, obs.shape), W, H, iters=60)
        offs.append(math.hypot(q[0] - p[0], q[1] - p[1]))
    return {"radius_m": round(float(np.percentile(offs, 95)), 1),
            "p50_m": round(float(np.percentile(offs, 50)), 1),
            "q": {k: round(float(np.percentile(offs, k)), 1) for k in (50, 90, 95, 99)},
            "px_sigma_used": round(px_sigma, 1), "trials": trials}

def leave_one_out(p, free, pts, obs, W, H, spec_pts) -> dict:
    """Drop one point at a time and re-solve: where the other points "predict" this point, how many pixels off, and how far the camera position moved.
    For a misidentified point (wrong feature, wrong coordinates, inconsistent height datum), the remaining points fit very well once it is dropped, but it is itself far off."""
    if 2 * (len(obs) - 1) < len(free) + 1:
        return {"note": f"with {len(obs)} points, dropping one leaves no more equations than unknowns, so the per-point check can't be done; add another point, or fix height/roll"}
    rows, errs = {}, []
    for i in range(len(obs)):
        keep = [j for j in range(len(obs)) if j != i]
        q, cost, _ = lm(p, free, pts[keep], obs[keep], W, H)
        uv, _ = project(q, pts[i:i + 1], W, H)
        e = float(np.hypot(*(uv[0] - obs[i]))) if not np.isnan(uv[0]).any() else float("inf")
        rest = math.sqrt(cost / len(keep))
        rows[spec_pts[i].get("name", str(i))] = {"pred_err_px": round(e, 1), "rest_rms_px": round(rest, 1),
                                                  "shift_m": round(math.hypot(q[0] - p[0], q[1] - p[1]), 1)}
        errs.append((e, rest, i))
    # Flag only one: dropping it gives the lowest rms for the remaining points, clearly below the other drops (0.4× the median), and its own prediction error is more than 3× the remaining rms.
    # Measured on synthetic cases (one point injected with a 40–80 m shift): downward shot, 7 points: false positives 0–2/20, detected 12–13/20; level shot, 6 points: false positives 2–5/20, detected 6–17/20 (unstable).
    dof_after = 2 * (len(obs) - 1) - len(free)
    e, rest, i = min(errs, key=lambda t: t[1])
    med = float(np.median([t[1] for t in errs]))
    flag = [spec_pts[i].get("name", str(i))] if (dof_after >= 2 and e > 3 * max(rest, 2.0) and rest < 0.4 * med) else []
    return {"points": rows, "suspect": flag,
            "most_improved": {"name": spec_pts[i].get("name", str(i)), "rest_rms_px": round(rest, 1), "median_rest_rms_px": round(med, 1)},
            "rule": "flag only one: dropping it gives the lowest remaining rms (< 0.4× the median of the other drops) and its prediction error > 3× the remaining rms; "
                    "unreliable for level shots and few points; nothing flagged doesn't mean there is no misidentified point; most_improved is listed whether or not it passes the threshold, check it first"}


def _fit_at(e, n, h, pts, obs, W, H, free, f0, pitch0, p_start=None):
    """Camera position fixed at (e, n, h); solve only heading/pitch/roll (and the focal length if not fixed). With p_start, start from it and don't try multiple starts."""
    starts = [p_start] if p_start is not None else [np.array([e, n, h, hd, pt, 0.0, f0])
                                                    for hd in range(0, 360, 30) for pt in (pitch0 - 10, pitch0, pitch0 + 10)]
    best = None
    for p0 in starts:
        p, cost, _ = lm(np.array(p0, dtype=float), free, pts, obs, W, H)
        if abs(p[4]) > 89 or abs(p[5]) > 60:          # flipped solutions (camera facing backward, upside down) don't count
            continue
        if best is None or cost < best[1]:
            best = (p, cost)
    return best if best else (np.array(starts[0], dtype=float), float("inf"))


def check(spec: dict, cands: dict, px_sigma: float) -> dict:
    """Score discrete candidate camera positions: each candidate frees only heading, pitch, roll (and the focal length if not fixed); compare reprojection errors.
    Suited to cases where "two or three places fit geometrically and you must pick one", e.g. the viewing platform marked on the map vs another stretch of shore on satellite imagery, or several buildings on the same alignment line.
    A single misidentified point can flip the ranking (synthetic cases: in downward shots, ground truth ranked first dropped from 15/15 to 1/15), so each point is also dropped in turn and rescored:
    robust_delta_chi2 takes the smallest over all drops; only candidates where that is also large count as inconsistent."""
    W, H = spec["image_size"]
    init = spec.get("init", {})
    lat0, lon0 = init["at"]
    kx, ky = _frame(lat0)
    pts = np.array([[(q["ll"][1] - lon0) * kx, (q["ll"][0] - lat0) * ky, q.get("h", 0.0)] for q in spec["points"]])
    obs = np.array([q["px"] for q in spec["points"]], dtype=float)
    names = [q.get("name", str(i)) for i, q in enumerate(spec["points"])]
    fixed = set(spec.get("fix", []))
    f0 = (W / 2) / math.tan(math.radians(init.get("hfov", 65) / 2))
    free = [3, 4, 5] + ([] if "hfov" in fixed else [6])
    subsets = [("all_points", list(range(len(obs))))]
    if 2 * (len(obs) - 1) >= len(free) + 1:
        subsets += [(f"drop {names[i]}", [j for j in range(len(obs)) if j != i]) for i in range(len(obs))]
    res, costs = {}, {}
    for name, c in cands.items():
        ll, h = (c[:2], c[2]) if len(c) > 2 else (c, init.get("height", 30.0))
        e, n = (ll[1] - lon0) * kx, (ll[0] - lat0) * ky
        p, cost = _fit_at(e, n, h, pts, obs, W, H, free, f0, init.get("pitch", 0.0))
        costs[name] = {"all_points": cost}
        for sname, keep in subsets[1:]:
            costs[name][sname] = _fit_at(e, n, h, pts[keep], obs[keep], W, H, free, f0, 0, p_start=p)[1]
        uv, _ = project(p, pts, W, H)
        res[name] = {"rms_px": round(math.sqrt(cost / len(obs)), 1),
                     "heading": round(p[3] % 360, 1), "pitch": round(p[4], 1), "roll": round(p[5], 1),
                     "hfov": round(2 * math.degrees(math.atan((W / 2) / p[6])), 1),
                     "residuals_px": {nm: [round(float(a), 1), round(float(b), 1)] for nm, (a, b) in zip(names, uv - obs)}}
    for sname, keep in subsets:
        best = min(costs[c][sname] for c in cands)
        sig2 = max(px_sigma ** 2, best / len(keep))           # when even the best candidate can't fit to px_sigma, loosen to its rms
        for c in cands:
            costs[c][sname] = (costs[c][sname] - best) / sig2
    for c in cands:
        d = costs[c]
        res[c]["delta_chi2"] = round(d["all_points"], 1)
        worst_drop = min(d, key=d.get)
        res[c]["robust_delta_chi2"] = round(d[worst_drop], 1)
        res[c]["robust_by"] = worst_drop
    return dict(sorted(res.items(), key=lambda kv: (kv[1]["robust_delta_chi2"], kv[1]["delta_chi2"])))


def sanity(pose: dict, pts: list[dict], horizon_row: float | None = None) -> list[str]:
    """Self-consistency check before reporting a camera position. Mistakes made before: putting the depression angle of some target in the frame into pitch as the camera's pitch,
    and reporting a camera position whose elevation doesn't match the depression angle in the frame (a 4 m height difference with a 7.6° depression angle, off by a factor of four)."""
    H = pose["_frame"]["image_size"][1]
    e0, n0, h_cam, _yaw, pitch, _roll, f = pose["_params"]
    lat0, lon0 = pose["_frame"]["lat0"], pose["_frame"]["lon0"]
    kx, ky = _frame(lat0)
    out = [(f"Self-check pitch={pitch:.1f}°: the true horizon (sea horizon / distant flat horizon) should fall on row "
            f"{H / 2 - f * math.tan(math.radians(pitch)):.0f} of the frame ({H} rows, frame center {H // 2}). "
            f"If the sea horizon in the photo is not near this row, pitch was filled in wrong: the target's depression angle ≠ the camera's pitch.")]
    if horizon_row is not None:
        pitch_h = math.degrees(math.atan2(H / 2 - float(horizon_row), f))
        d = abs(pitch_h - pitch)
        out.append(f"  Sea horizon in the photo is on row {float(horizon_row):.0f} → pitch should be {pitch_h:.1f}° (current {pitch:.1f}°, off by {d:.1f}°)")
        if d > 2.0:
            out.append(f"  !! pitch contradicts the sea horizon by {d:.1f}° > 2°: calibrate pitch from the sea horizon first, then project/solve")
    out.append(f"Self-check camera height {h_cam:.1f} (same datum as each point's h); the \"expected row\" in the table below must match the actual row of that feature in the photo:")
    for q in pts:
        e = (q["ll"][1] - lon0) * kx - e0
        n = (q["ll"][0] - lat0) * ky - n0
        dist = math.hypot(e, n)
        if dist < 1.0:
            continue
        dh = h_cam - q.get("h", 0.0)
        dep = math.degrees(math.atan2(dh, dist))
        row = H / 2 + f * math.tan(math.radians(dep + pitch))
        note = ""
        if "px" in q and len(q["px"]) > 1:
            note = f"  actual row {q['px'][1]:.0f}, off by {abs(row - q['px'][1]):.0f} px"
        out.append(f"  {q.get('name', '?'):<14} horizontal {dist:6.0f} m  height diff {dh:6.1f} m  geometric depression {dep:5.1f}°  expected row {row:6.0f}{note}")
    return out


def draw(photo: Path, pose: dict, pts: list[dict], out: Path, observed: bool) -> None:
    im = Image.open(photo).convert("RGB")
    W, H = pose["_frame"]["image_size"]
    sx, sy = im.width / W, im.height / H
    lat0, lon0 = pose["_frame"]["lat0"], pose["_frame"]["lon0"]
    kx, ky = _frame(lat0)
    enu = np.array([[(q["ll"][1] - lon0) * kx, (q["ll"][0] - lat0) * ky, q.get("h", 0.0)] for q in pts])
    uv, z = project(np.array(pose["_params"]), enu, W, H)
    d = ImageDraw.Draw(im)
    for q, (u, v), zz in zip(pts, uv, z):
        if observed and "px" in q:
            ox, oy = q["px"][0] * sx, q["px"][1] * sy
            d.line([ox - 9, oy, ox + 9, oy], fill="lime", width=3)
            d.line([ox, oy - 9, ox, oy + 9], fill="lime", width=3)
        if zz > 0 and not math.isnan(u):
            cx, cy = u * sx, v * sy
            d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline="red", width=3)
            d.text((cx + 9, cy - 8), q.get("name", ""), fill="yellow")
    im.save(out, quality=90)



def _neg_coords(argv: list[str]) -> list[str]:
    """argparse treats negative coordinates like -1.45,-48.5 as option names; prefixing a space makes them plain values (float ignores the space). Needed for any photo in the southern or western hemisphere."""
    return [" " + a if re.match(r"^-\d[\d.]*(,-?[\d.]+)+$", a) else a for a in argv]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("solve")
    s.add_argument("spec", type=Path)
    s.add_argument("--search-radius", type=float, default=300, help="radius of uncertainty of the initial position m")
    s.add_argument("--restarts", type=int, default=40)
    s.add_argument("--photo", type=Path, help="draw observed points (green crosses) and reprojected points (red circles)")
    s.add_argument("--out", type=Path, help="overlay output")
    s.add_argument("--save", type=Path, default=Path("pose.json"))
    s.add_argument("--pt-sigma", type=float, default=5.0,
                   help="coordinate error of the control points themselves m (clicking a building corner on satellite imagery: typically 5–15 m). The error radius uses it for Monte Carlo; set 0 to fall back to pixel noise only")
    ck = sub.add_parser("check", help="score discrete candidate camera positions: each candidate solves only the heading; compare reprojection errors")
    ck.add_argument("spec", type=Path)
    ck.add_argument("--cands", type=Path, required=True, help='{"cand_name": [lat, lon] or [lat, lon, height]}; without height, init.height is used')
    ck.add_argument("--px-sigma", type=float, default=5.0, help="pixel measurement error, used to convert to chi2")
    ck.add_argument("--save", type=Path, default=Path("pose_check.json"))
    pr = sub.add_parser("project")
    pr.add_argument("--pose", type=Path, required=True)
    pr.add_argument("--points", type=Path, required=True, help='[{"name":…,"ll":[lat,lon],"h":…}] or {name:[lat,lon,h]}')
    pr.add_argument("--photo", type=Path, required=True)
    pr.add_argument("--out", type=Path, required=True)
    pr.add_argument("--horizon", type=float, help="row of the sea horizon / distant flat horizon in the photo (original image pixels): used to calibrate and validate pitch")
    args = ap.parse_args(_neg_coords(sys.argv[1:]))

    if args.cmd == "solve":
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        pose = solve(spec, args.search_radius, args.restarts, pt_sigma=args.pt_sigma)
        args.save.write_text(json.dumps(pose, ensure_ascii=False, indent=1), encoding="utf-8")
        show = {k: v for k, v in pose.items() if not k.startswith("_")}
        print(json.dumps(show, ensure_ascii=False, indent=1))
        if pose["rms_px"] > 15:
            print("Note: reprojection error is high; a point may be mismatched, the height datum inconsistent, or the initial value too far off (increase --search-radius / --restarts)")
        loo = pose["leave_one_out"]
        if loo.get("suspect"):
            print(f"Note: the per-point check flagged a suspected misidentified point {loo['suspect']}: go back and verify its feature and coordinates first, then decide whether to keep it")
        elif loo.get("most_improved"):
            m = loo["most_improved"]
            print(f"Per-point check: after dropping \"{m['name']}\" the remaining rms is {m['rest_rms_px']} px (median of other drops {m['median_rest_rms_px']} px); below the suspect threshold, but if the gap is large, still check it first")
        for line in sanity(pose, spec["points"]):
            print(line)
        if args.photo and args.out:
            draw(args.photo, pose, spec["points"], args.out, observed=True)
            print(f"overlay -> {args.out}")
    elif args.cmd == "check":
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        cands = json.loads(args.cands.read_text(encoding="utf-8"))
        out = check(spec, cands, args.px_sigma)
        args.save.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        for name, v in out.items():
            print(f"{name:24s} rms {v['rms_px']:6.1f} px  Δchi2 {v['delta_chi2']:8.1f}  robust Δchi2 {v['robust_delta_chi2']:8.1f} ({v['robust_by']})"
                  f"  heading {v['heading']:6.1f}  pitch {v['pitch']:5.1f}")
        print(f"-> {args.save} (only robust Δchi2 > 9 counts as inconsistent: dropping any one point can't rescue it; when two candidates differ only on one point, verify that point first)")
    else:
        pose = json.loads(args.pose.read_text(encoding="utf-8"))
        raw = json.loads(args.points.read_text(encoding="utf-8"))
        pts = raw if isinstance(raw, list) else [{"name": k, "ll": v[:2], "h": (v[2] if len(v) > 2 else 0.0)} for k, v in raw.items()]
        draw(args.photo, pose, pts, args.out, observed=False)
        for line in sanity(pose, pts, args.horizon):
            print(line)
        print(args.out)


if __name__ == "__main__":
    # Chinese-locale Windows outputs GBK by default: it crashes on m², ñ, and the Chinese the agent reads is garbled
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    main()
