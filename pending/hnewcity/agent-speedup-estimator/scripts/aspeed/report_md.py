from __future__ import annotations

from .i18n import cat_name, dur, strings


def _x(v: float) -> str:
    return f"{v:.2f}x"


def _pct(part: float, whole: float) -> str:
    return f"{100.0 * part / whole:.0f}%" if whole else "-"


def _range(t: dict):
    vals = [t["scenarios"][k]["total_speedup"] for k in ("conservative", "expected", "optimistic")]
    return min(vals), t["scenarios"]["expected"]["total_speedup"], max(vals)


def render_md(r: dict, lang: str) -> str:
    S = strings(lang)
    agents = r["agents"]
    allv = agents["all"]
    names = [k for k in ("claude", "codex") if k in agents]
    col = {"claude": S["col_claude"], "codex": S["col_codex"]}
    hw, base = r["hardware"], r["baseline"]
    L = []
    L.append(f"# {S['title']}")
    L.append("")
    primary = r["targets"][r["primary"]]
    lo, ex, hi = _range(primary)
    saved = primary["scenarios"]["expected"]["saved_s"]
    L.append(f"**{S['headline'].format(name=primary['name'], x=ex, lo=lo, hi=hi, saved=dur(saved))}**")
    L.append("")
    L.append(f"- {S['scanned']}: {allv['sessions']} {S['sessions']}, {r['period']['first']} – {r['period']['last']}")
    L.append(f"- {S['this_machine']}: {hw['cpu_name']} ({hw['cores']}C/{hw['threads']}T), {hw['ram_gb']} GB RAM, disk: {hw['disk_class']}")
    L.append(f"- {S['baseline']}: {base['name']}, {base['gb6_single']} / {base['gb6_multi']}")
    L.append("")

    L.append(f"## {S['time_title']}")
    L.append("")
    head = [""] + [col[n] for n in names] + ([S["col_total"]] if len(names) > 1 else [])
    L.append("| " + " | ".join(head) + " |")
    L.append("|" + "---|" * len(head))
    rows = [
        (S["model"], "model_s"),
        (S["tools"], "tool_s"),
        (S["working"], None),
        (S["human"], "human_s"),
        (S["idle"], "idle_s"),
        (S["background"], "background_s"),
        (S["stalled"], "stalled_s"),
    ]
    for label, key in rows:
        cells = []
        for n in names + (["all"] if len(names) > 1 else []):
            a = agents[n]
            v = a["model_s"] + a["tool_s"] if key is None else a[key]
            cells.append(dur(v))
        text = f"**{label}**" if key is None else label
        L.append("| " + " | ".join([text] + cells) + " |")
    L.append("")
    working = allv["model_s"] + allv["tool_s"]
    L.append(f"**{S['sens_title']}**: {dur(r['sensitive_expected_s'])} ({_pct(r['sensitive_expected_s'], working)}){S['sep']}{S['sens_hint']}{S['end']}")
    L.append("")

    L.append(f"## {S['cat_title']}")
    L.append("")
    L.append(f"| {S['cat']} | {S['count']} | {S['time']} | {S['share']} | {S['median']} | {S['p90']} | {S['longest']} |")
    L.append("|---|---:|---:|---:|---:|---:|---:|")
    for c in allv["categories"]:
        L.append(
            f"| {cat_name(lang, c['category'])} | {c['count']} | {dur(c['seconds'])} | {_pct(c['seconds'], allv['tool_s'])} "
            f"| {c['median_s']:.1f}s | {c['p90_s']:.1f}s | {dur(c['max_s'])} |"
        )
    L.append("")
    if allv["families"]:
        fam = ", ".join(f"{k} {dur(v)}" for k, v in allv["families"][:8])
        L.append(f"{S['fam_title']}: {fam}")
        L.append("")

    L.append(f"## {S['proj_title']}")
    L.append("")
    L.append(f"| {S['target']} | {S['tier']} | {S['single_x']} | {S['multi_x']} | {S['tool_speedup']} ({S['exp']}) | {S['e2e']} ({S['exp']}) | {S['range']} | {S['saved']} |")
    L.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for t in r["targets"]:
        lo, ex, hi = _range(t)
        e = t["scenarios"]["expected"]
        flag = f" ({S['no_gain']})" if hi < 1.05 else ""
        L.append(
            f"| {t['name']} | {t['tier']} | {_x(t['cpu_x_single'])} | {_x(t['cpu_x_multi'])} | {_x(e['tool_speedup'])} "
            f"| **{_x(ex)}**{flag} | {_x(lo)} – {_x(hi)} | {dur(e['saved_s'])} |"
        )
    L.append("")

    if r.get("catalog"):
        catalog = r["catalog"]
        L.append(f"## {S['catalog_title']}")
        L.append("")
        L.append(S["catalog_count"].format(total=len(catalog["cpus"]), scored=sum(bool(c.get("gb6_single")) for c in catalog["cpus"]), targets=len(r["targets"]), date=catalog["as_of"]))
        L.append("")
        L.append(S["catalog_note"])
        L.append("")
        L.append("[" + S["catalog_title"] + "](cpu-catalog.json) · [HTML](report.html)")
        L.append("")

    L.append(f"## {S['caveat_title']}")
    L.append("")
    for n in r["notes"]:
        L.append(f"- {n}")
    L.append("")
    L.append(f"_{S['generated'].format(v=r['version'])}_")
    L.append("")
    return "\n".join(L)
