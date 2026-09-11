#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mutation-kill.py -- 变异杀伤检验器 / Mutation-kill checker.

用途：验证「一份产物自带的检查」到底有没有鉴别力。
把产物自检当被测对象，注入若干**单点变异体**（各改一处的合理错误），逐个跑产物自带的自检，
再与**基线（未变异）**的判定比对。两个指标，别混：

- **区分率（主指标）** = 判定与基线不同的变异体数 / 该类**有效**变异体数。
  含义：这份自检**看得出**这类改动吗？区分率 0% 表示该类错误的验证证据为零（不是证据较弱）。
  ERROR（未测成）不计入分母。
- **命中期望（次指标）** = 判定 == 该变异体声明的 `expect` 的个数 / 声明了 `expect` 的个数。
  含义：变异体的设计意图有没有被兑现（例如"把已发现的缺陷改回正确"应当改变判定）。

两者不同，不是同一个数：一个变异体可以同时"命中期望"且"零区分"（例如基线本身就判 FAIL）。

原则（与本仓库纪律一致）：
- **原产物只读**：只读其文本，变异体一律写在 workdir；前后比对 sha256，被改动即报错退出。
- **永不自动判 PASS**：本工具输出的是「产物自检自己的判定」，加上"是否符合期望"的比对；
  自检说 PASS 不等于产物正确，自检说 FAIL 也不等于产物错误。
- **静默替换即伪造**：每处 `find` 的命中数必须等于 `count`（默认 1），否则该变异体记 ERROR 而不是"通过"。
- **必须有且只有一个基线**：清单里没有基线变异体时，任何"区分率"都无从计算——工具直接报错退出，
  而不是把所有类别报成 0%（那是把"没算"说成"看不见"，恰好是本工具要防的那类错误）。
- **未测成不等于没抓住**：ERROR（find 命中数不符 / 注入点不存在 / 取不到结果 / 超时）单列，
  不进区分率分母，也不进"零区分力"告警。

用法：
    python scripts/mutation-kill.py --help
    python scripts/mutation-kill.py run <manifest.json>

可运行的示例（与文档同仓）：
    python scripts/mutation-kill.py run scripts/examples/mutation-kill-demo.manifest.json
示例里 `artifact` / `workdir` 用相对路径，按 manifest 自身所在目录解析。

manifest.json 结构（必须的字段：artifact、mutants；且 mutants 里恰好一个基线）：
{
  "artifact": "产物路径（只读）；相对路径按 manifest 所在目录解析",
  "workdir":  "可选，变异体与 profile 的落盘目录，默认系统临时目录",
  "chrome":   "可选，Chrome 可执行文件路径；不填则按常见路径探测",
  "budget_ms": 6000,
  "marker":   "自检结果标记串（须在 inject 源码里以拼接形式出现，否则会匹配到源码本身）",
  "inject":   "一段 <script>：调用产物自带的自检，把结果写成 marker + JSON 追加进 DOM",
  "inject_target": "可选，注入锚点，默认 \"</body>\"；产物没有它时该变异体记 ERROR（可用 </html>）",
  "mutants": [
    {"name": "m00-orig", "desc": "基线：原样不变异", "edits": []},
    {"name": "m01-fix",  "category": "render",   "desc": "把符号改回正确", "expect": "FAIL",
     "edits": [{"find": "旧串", "replace": "新串", "count": 1}]}
  ]
}

判定口径：
- 基线认定：`edits` 缺失/为空，**或** `"category": "baseline"`。数量不等于 1 直接报错退出（exit 2）。
- 基线必须取到 PASS/FAIL；基线本身 ERROR（含注入点不存在、Chrome 超时）=> 整轮作废（exit 2）。
- `expect` 默认 "FAIL"，但只有**显式写了** `expect` 的变异体才计入"命中期望"统计。
- `same_as_baseline` 只在两侧都取到 PASS/FAIL 时计算；ERROR 行不进统计、不进告警。
- 基线自身判 FAIL 时显式告警：产物未变异就不过自检，此时的"区分率"参照的是一个已失败的基线。
- 退出码：0 = 跑完且无 ERROR；1 = 有 ERROR 行（未测成）；2 = manifest/环境不合法（含基线问题）。
"""
import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def find_chrome(explicit=None):
    if explicit and os.path.isfile(explicit):
        return explicit
    for c in CHROME_CANDIDATES:
        if os.path.isfile(c):
            return c
    return shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")


def apply_edits(text, edits):
    """返回 (新文本, 问题列表)。命中数不符即记问题——静默替换等于伪造。"""
    problems = []
    out = text
    for i, e in enumerate(edits):
        find = e["find"]
        repl = e["replace"]
        want = int(e.get("count", 1))
        got = out.count(find)
        if want <= 0:                      # count<=0 表示"全部替换"，但必须命中至少一次
            if got == 0:
                problems.append("edit[%d] 命中 0 次（期望至少 1 次）：%s" % (i, find[:60]))
                continue
            out = out.replace(find, repl)
        else:
            if got != want:
                problems.append("edit[%d] 命中 %d 次，期望 %d 次：%s" % (i, got, want, find[:60]))
                continue
            out = out.replace(find, repl, want)
    return out, problems


def run_mutant(chrome, workdir, name, html, budget_ms, marker, inject, inject_target="</body>"):
    path = os.path.join(workdir, name + ".html")
    if inject:
        # 注入点必须真实存在：早先这里是 `if "</body>" in html`，锚点缺失就静默不注入，
        # 于是基线也取不到结果、最后被误读成"自检零区分力"。现在显式失败。
        if inject_target not in html:
            return "ERROR", ("注入点 %r 不在产物里（产物可能没有它；用 manifest 的 "
                             "inject_target 指定其它锚点，例如 </html>）" % inject_target)
        html = html.replace(inject_target, inject + "\n" + inject_target, 1)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    profile = os.path.join(workdir, "profile_" + name)
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--user-data-dir=" + profile,
           "--virtual-time-budget=" + str(budget_ms),
           "--dump-dom", "file:///" + path.replace("\\", "/")]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=180)
        dom = p.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return "ERROR", "chrome 超时"
    m = re.search(re.escape(marker) + r"(\{[^\n<]*\}|ERROR[^\n<]*)", dom)
    if not m:
        return "ERROR", "未取到自检结果（marker 不对 / 注入脚本报错 / 自检未在 load 前挂上？）"
    payload = m.group(1)
    if payload.startswith("ERROR"):
        return "ERROR", payload
    try:
        data = json.loads(payload)
    except ValueError as exc:
        return "ERROR", "结果 JSON 解析失败：%s" % exc
    return ("PASS" if data.get("pass") else "FAIL"), data.get("fails", data)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="mutation-kill.py",
        description="变异杀伤检验器：验证一份产物自带的自检有没有鉴别力。主指标＝区分率"
                    "（判定与基线不同的变异体 / 该类有效变异体），原产物只读。")
    sub = ap.add_subparsers(dest="cmd")
    rp = sub.add_parser("run", help="按 manifest 执行变异杀伤实验")
    rp.add_argument("manifest", help="manifest.json 路径")
    args = ap.parse_args(argv)

    if args.cmd != "run":
        ap.print_help()
        return 0

    # 结构化失败（2026-09-11 batch 44）：此前 manifest 缺字段/坏 JSON 直接抛 KeyError
    # 轨迹并以 exit 1 退出，而 docstring 声明「2 = manifest/环境不合法」——文档与行为不符，
    # 且 CI 只看 exit 0/1 会把"用法错误"误读成"跑完有未测成项"。
    try:
        with open(args.manifest, encoding="utf-8") as f:
            man = json.load(f)
    except FileNotFoundError:
        print("ERROR: manifest 不存在：%s" % args.manifest, file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print("ERROR: manifest 不是合法 JSON（%s）：line %d col %d: %s"
              % (args.manifest, exc.lineno, exc.colno, exc.msg), file=sys.stderr)
        return 2
    except OSError as exc:
        print("ERROR: 无法读取 manifest：%s" % exc, file=sys.stderr)
        return 2
    if not isinstance(man, dict):
        print("ERROR: manifest 顶层必须是 JSON 对象，实际为 %s" % type(man).__name__,
              file=sys.stderr)
        return 2
    man_dir = os.path.dirname(os.path.abspath(args.manifest))
    if not man.get("artifact"):
        print("ERROR: manifest 缺少必需字段 artifact（产物路径）", file=sys.stderr)
        return 2
    artifact = man["artifact"]
    if not os.path.isabs(artifact):                      # 相对路径按 manifest 所在目录解析
        artifact = os.path.normpath(os.path.join(man_dir, artifact))
    mutants = man.get("mutants") or []
    if not isinstance(mutants, list):
        print("ERROR: manifest 的 mutants 必须是数组，实际为 %s" % type(mutants).__name__,
              file=sys.stderr)
        return 2
    if not mutants:
        print("ERROR: manifest 里没有任何 mutants，无事可做", file=sys.stderr)
        return 2
    # 基线唯一性是硬前提：没有基线就没有"区分"的参照，区分率无从计算。
    # 这里以前不校验，缺基线时每个类别都被算成 0% —— 把"没算"说成"看不见"，
    # 恰好是本工具要防的那类错误。现在直接拒绝输出。
    baselines = [m for m in mutants
                 if not (m.get("edits") or []) or m.get("category") == "baseline"]
    if len(baselines) != 1:
        print("ERROR: 需要且只需要 1 个基线变异体（无 edits，或 category=baseline），"
              "manifest 里找到 %d 个。缺基线时区分率无法计算，拒绝输出。" % len(baselines),
              file=sys.stderr)
        return 2
    contradictory = [m.get("name") or "?" for m in mutants
                     if m.get("category") == "baseline" and (m.get("edits") or [])]
    if contradictory:
        print("ERROR: 以下变异体 category=baseline 却带了 edits（基线必须原样不变异）："
              + ", ".join(contradictory), file=sys.stderr)
        return 2
    marker = man.get("marker", "MUTRESULT:")
    inject = man.get("inject", "")
    inject_target = man.get("inject_target", "</body>")
    try:
        budget = int(man.get("budget_ms", 6000))
    except (TypeError, ValueError):
        print("ERROR: manifest 的 budget_ms 必须是整数（毫秒），实际为 %r"
              % (man.get("budget_ms"),), file=sys.stderr)
        return 2
    workdir = man.get("workdir") or os.path.join(tempfile.gettempdir(), "mutation-kill")
    if not os.path.isabs(workdir):                       # 同上
        workdir = os.path.normpath(os.path.join(man_dir, workdir))
    os.makedirs(workdir, exist_ok=True)

    chrome = find_chrome(man.get("chrome"))
    if not chrome:
        print("ERROR: 找不到 Chrome；请用 manifest 的 chrome 字段指定可执行文件路径", file=sys.stderr)
        return 2

    with open(artifact, encoding="utf-8") as f:
        src = f.read()
    before = sha256_text(src)

    rows = []
    base_verdict = None
    for mu in mutants:
        name = mu.get("name") or ("mutant%d" % (len(rows) + 1))
        cat = mu.get("category", "uncategorized")
        expect = mu.get("expect", "FAIL")
        is_base = not (mu.get("edits") or []) or cat == "baseline"
        html, problems = apply_edits(src, [] if is_base else (mu.get("edits") or []))
        declare_expect = "expect" in mu
        shown_cat = "baseline" if is_base else cat
        if problems:
            rows.append({"name": name, "category": shown_cat, "expect": expect,
                         "expect_declared": declare_expect,
                         "verdict": "ERROR", "detail": "; ".join(problems),
                         "hit": False, "same_as_baseline": None})
            print("[ERROR] %-22s cat=%-12s %s" % (name, shown_cat, "; ".join(problems)))
            continue
        verdict, detail = run_mutant(chrome, workdir, name, html, budget, marker,
                                     inject, inject_target)
        if is_base and verdict not in ("PASS", "FAIL"):
            # 基线没测成 => 后续所有"与基线比较"都没有意义，不许继续算区分率。
            print("[ERROR] 基线未测成（%s）—— 没有有效参照，整轮作废。" % detail, file=sys.stderr)
            return 2
        row = {"name": name, "category": shown_cat, "expect": expect,
               "expect_declared": declare_expect,
               "verdict": verdict, "detail": detail,
               "hit": verdict == expect, "same_as_baseline": None}
        if is_base:
            base_verdict = verdict
        elif verdict in ("PASS", "FAIL"):        # 只在两侧都取到 PASS/FAIL 时才比较
            row["same_as_baseline"] = (verdict == base_verdict)
        rows.append(row)
        print("[%-5s] %-22s cat=%-12s%s" % (
            verdict, name, row["category"],
            ("   <-- 与基线判定相同：零区分力" if row["same_as_baseline"] else "")))

    with open(artifact, encoding="utf-8") as f:          # 只读复核（句柄一并关闭）
        after = sha256_text(f.read())
    print("")
    print("原产物只读校验：%s -> %s  %s" % (
        before[:16], after[:16], "OK" if before == after else "!!! 原产物被改动，结果作废"))
    if base_verdict == "FAIL":
        print("")
        print("⚠ 基线（未变异产物）自身判 FAIL —— 产物未改动就不过自己的自检。"
              "下面\"区分率\"的参照是一个已经失败的基线，读数需谨慎。")

    cats = {}
    errored = []
    for r in rows:
        if r["category"] == "baseline":
            continue
        if r["verdict"] == "ERROR":
            errored.append(r["name"])            # ERROR 不计入分母：它不是"没被抓住"，是根本没测成
            continue
        d = cats.setdefault(r["category"], {"n": 0, "distinguished": 0, "hit": 0, "exp": 0})
        d["n"] += 1
        d["distinguished"] += 1 if r["same_as_baseline"] is False else 0
        if r.get("expect_declared"):
            d["exp"] += 1
            d["hit"] += 1 if r["hit"] else 0
    print("")
    print("区分率 = 判定与基线不同的变异体 / 该类有效变异体总数（主指标）")
    if not cats:
        print("  （没有可统计的有效变异体：除基线外没有变异体，或全部未测成）")
    for c in sorted(cats):
        d = cats[c]
        line = "  %-14s 区分 %d/%d = %5.1f%%" % (c, d["distinguished"], d["n"],
                                               100.0 * d["distinguished"] / d["n"])
        if d["exp"]:
            line += "   命中期望 %d/%d" % (d["hit"], d["exp"])
        print(line)
    # 零区分力告警：判定与基线相同、且这一行确实测成了（ERROR 行不算 —— 它测都没测成）
    zero = [r["name"] for r in rows if r["same_as_baseline"] and r["verdict"] != "ERROR"]
    if zero:
        print("")
        print("零区分力告警（变异后判定与基线完全相同，即这份自检没看出差别）：")
        for n in zero:
            print("  - " + n)
    if errored:
        print("")
        print("未测成（ERROR，不计入区分率，需先修 manifest/环境）：")
        for n in errored:
            print("  - " + n)

    out = os.path.join(workdir, "mutation-kill-report.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"artifact": artifact, "sha256_before": before, "sha256_after": after,
                   "baseline_verdict": base_verdict, "mutants": rows,
                   "per_category": cats,
                   "errored": errored,
                   "metric_definitions": {
                       "distinguished_rate": "判定与基线不同的变异体数 / 该类有效变异体数（主指标）",
                       "expect_hit": "判定 == 声明的 expect 的个数 / 显式声明了 expect 的个数（次指标）",
                       "excluded": "verdict == ERROR 的行不进任何分母；它不是没被抓住，是根本没测成",
                       "baseline": "未变异产物自身的判定，是所有比较的参照；必须唯一且取到 PASS/FAIL",
                   }}, f, ensure_ascii=False, indent=1, default=str)
    print("")
    print("报告：" + out)
    err = [r for r in rows if r["verdict"] == "ERROR"]
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
