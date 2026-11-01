from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Optional, Tuple

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_NOISE = re.compile(r"\((?:r|tm)\)|\bcpu\b|\bprocessor\b|@\s*[\d.]+\s*ghz|\bwith\b.*$|\bw/\b.*$", re.I)
_SUFFIX_BLOCK = re.compile(r"^\s*(?:pro|max|ultra|plus|x\b|3d|\(\s*af\b)", re.I)


def load_json(name: str, data_dir: Optional[Path] = None) -> dict:
    with open((data_dir or DATA_DIR) / name, encoding="utf-8") as fh:
        return json.load(fh)


def normalize(name: str) -> str:
    s = _NOISE.sub(" ", name.lower())
    return re.sub(r"\s+", " ", s).strip()


def find_cpu(name: str, cpus: List[dict]) -> Optional[dict]:
    target = normalize(name)
    cpu_config = re.search(r"\b(\d+)[ -]*(?:CPU|cores?)\b", name, re.I)
    gpu_config = re.search(r"\b(\d+)[ -]*GPU\b", name, re.I)
    best_len = 0
    best = {}
    for cpu in cpus:
        if cpu["name"].startswith("Apple "):
            actual_cores = re.search(r"\b(\d+)-CPU\b", cpu["name"])
            actual_gpu = re.search(r"\b(\d+)-GPU\b", cpu["name"])
            if cpu_config and (not actual_cores or actual_cores.group(1) != cpu_config.group(1)):
                continue
            if gpu_config and (not actual_gpu or actual_gpu.group(1) != gpu_config.group(1)):
                continue
        for raw_alias in cpu.get("aliases", []) + [cpu["name"], cpu.get("id", "")]:
            alias = normalize(raw_alias)
            if not alias:
                continue
            m = re.search(r"(?<![\w-])" + re.escape(alias) + r"(?![\w-])", target)
            if not m or _SUFFIX_BLOCK.match(target[m.end():]):
                continue
            if len(alias) > best_len:
                best_len, best = len(alias), {}
            if len(alias) == best_len:
                best[cpu["name"]] = cpu
    # A family alias must never silently choose one of several core configurations.
    return next(iter(best.values())) if len(best) == 1 else None


def load_catalog(data_dir: Optional[Path] = None) -> dict:
    """Join inventory to versioned scores by stable ID; missing scores stay missing."""
    catalog = load_json("cpu_catalog.json", data_dir)
    scored = load_json("cpu_scores.json", data_dir)["cpus"]
    by_id = {c["id"]: c for c in scored}
    cpus = []
    for record in catalog["cpus"]:
        entry = dict(record)
        score = by_id.get(entry["id"])
        if score:
            entry.update(score)
            entry["score_status"] = "reference-gb6"
        cpus.append(entry)
    # Mac chart values have a version conflict. Only map a Mac to an independently
    # sourced CPU reference, retaining its identity and marking the basis explicitly.
    processors = [c for c in cpus if c["kind"] == "cpu" and c.get("gb6_single")]
    for entry in cpus:
        if entry["kind"] != "mac":
            continue
        candidates = []
        cpu_name = entry["cpu_name"]
        if cpu_name.startswith("Intel "):
            candidates = [c for c in processors if normalize(c["name"]).replace("-", " ") == normalize(cpu_name).replace("-", " ")]
        elif cpu_name.startswith("Apple "):
            cores = re.search(r"\((\d+) (?:CPU )?cores", entry["configuration"])
            gpu = re.search(r"(\d+) GPU cores", entry["configuration"])
            if cores:
                candidates = [c for c in processors if c["name"].split(" (")[0] == cpu_name
                              and c.get("cpu_cores") == int(cores.group(1))]
                if gpu:
                    exact = [c for c in candidates if re.search(r"\b" + gpu.group(1) + r"-GPU\b", c["name"])]
                    if exact:
                        candidates = exact
                    else:
                        candidates = [c for c in candidates if "-GPU" not in c["name"]]
        if candidates and len({(c["gb6_single"], c["gb6_multi"]) for c in candidates}) == 1:
            ref = candidates[0]
            entry.update({k: ref[k] for k in ("gb6_single", "gb6_multi", "benchmark", "source_url")})
            entry["cpu_reference_id"] = ref["id"]
            entry["score_status"] = "cpu-reference-gb6"
            entry["score_note"] = "Uses a CPU reference; not a benchmark measurement of this Mac. Mac chart scores with conflicting benchmark versions are excluded."
    catalog["cpus"] = cpus
    return catalog


def filter_catalog(cpus: List[dict], search: str = "", vendor: str = "", platform: str = "", generation: str = "", scored_only: bool = False) -> List[dict]:
    words = normalize(search).split()
    return [c for c in cpus
            if (not vendor or c["vendor"].lower() == vendor.lower())
            and (not platform or platform in c.get("platforms", []))
            and (not generation or generation.lower() in c.get("generation", "").lower())
            and (not scored_only or c.get("gb6_single") and c.get("gb6_multi"))
            and all(w in normalize(" ".join([c["name"], c.get("generation", ""), c.get("source_section", "")])) for w in words)]


def resolve_baseline(cpu_name: str, lang: str = "en", data_dir: Optional[Path] = None) -> Tuple[Optional[dict], str, str, float]:
    """Return (cpu_record, source, note, uncertainty). source is 'table', 'proxy' or '' when nothing matched."""
    cpus = load_json("cpu_scores.json", data_dir)["cpus"]
    exact = find_cpu(cpu_name, cpus)
    if exact:
        return exact, "table", "exact match in cpu_scores.json", 1.0
    target = normalize(cpu_name)
    for p in load_json("proxies.json", data_dir)["proxies"]:
        if p["match"] in target:
            stand_in = find_cpu(p["use"], cpus)
            if stand_in:
                return stand_in, "proxy", p["note"].get(lang) or p["note"]["en"], float(p.get("uncertainty", 1.15))
    return None, "", "", 1.0


def estimate_from_specs(threads: int, lang: str = "en", data_dir: Optional[Path] = None) -> Tuple[dict, str, float]:
    """Last resort when a CPU has no score: scale a documented anchor chip by thread count."""
    cfg = load_json("proxies.json", data_dir)["fallback"]
    anchor = find_cpu(cfg["use"], load_json("cpu_scores.json", data_dir)["cpus"])
    t = min(32, max(2, threads or cfg["threads"]))
    multi = round(anchor["gb6_multi"] * (t / cfg["threads"]) ** cfg["thread_exponent"])
    scores = {"gb6_single": anchor["gb6_single"], "gb6_multi": multi}
    return scores, cfg["note"].get(lang) or cfg["note"]["en"], float(cfg["uncertainty"])
