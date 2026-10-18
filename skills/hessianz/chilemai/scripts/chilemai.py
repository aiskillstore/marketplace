#!/usr/bin/env python3
"""吃了麦？—— 营养解析 / 筛选 / 菜单对齐

麦当劳 MCP 返回的膳食营养数据不是 JSON，而是一种自定义的定宽列文本；
`query-meals` 返回的菜单名称又与营养库存在差异（如 "纯牛奶(盒装)" vs "纯牛奶（盒装）"）。
本脚本负责把这层脏数据抹平，让上层决策只面对干净的结构化结果。

子命令
    filter   按营养目标筛选 + 排序
    match    把在售菜单与营养库做名称对齐
    plan     从可信单品组合一餐，校验整餐营养与菜单估价

用法
    cat nutrition.txt | python3 chilemai.py filter --goal low-cal --limit 8
    python3 chilemai.py match --menu menu.json --nutrition nutrition.txt

依赖：仅标准库（Python 3.8+）
"""

from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import heapq
from itertools import combinations_with_replacement
import json
import math
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple

COLUMNS = [
    "productName",
    "nutritionDescription",
    "energyKj",
    "energyKcal",
    "protein",
    "fat",
    "carbohydrate",
    "sodium",
    "calcium",
]
NUMERIC = COLUMNS[2:]

# 目标 -> (上限过滤, 下限过滤, 排序字段, 方向, 默认餐品类型)
# 数值单位：kcal / g / mg，均取自麦当劳官方营养表
#
# 为什么要 kinds：只按热量排序会得到"无糖可乐 / 锡兰红茶"这类零卡饮品——
# 它们是饮料不是饭。按"要低卡"推荐一杯可乐是错的，所以低卡类目标默认只从
# 主食和配餐里挑，饮品与甜品需要用户显式指定。
GOALS: Dict[str, Dict[str, Any]] = {
    "high-protein": {
        "min": {"protein": 20.0},
        "sort": ("protein", "desc"),
        "kinds": ["main"],
    },
    "low-cal": {
        "max": {"energyKcal": 500.0},
        "sort": ("energyKcal", "asc"),
        "kinds": ["main", "side"],
    },
    "low-fat": {
        "max": {"fat": 15.0},
        "sort": ("fat", "asc"),
        "kinds": ["main"],
    },
    "low-sodium": {
        "max": {"sodium": 600.0},
        "sort": ("sodium", "asc"),
        "kinds": ["main"],
    },
    "low-carb": {
        "max": {"carbohydrate": 30.0},
        "sort": ("carbohydrate", "asc"),
        "kinds": ["main"],
    },
    # 减脂综合：热量封顶后再看蛋白质密度，避免选到"低卡但全是糖"的东西
    "light": {
        "max": {"energyKcal": 500.0},
        "sort": ("protein_per_100kcal", "desc"),
        "kinds": ["main"],
    },
    # 未指定营养目标时保留数据源顺序，不擅自当成健身餐排序
    "any": {"kinds": ["main"]},
}

# 餐品类型关键词表。匹配顺序：甜品 -> 饮品 -> 主食 -> 配餐 -> 兜底主食。
# 顺序有讲究："热朱古力"是饮品、"朱古力新地"是甜品，靠"新地"先命中来区分。
KINDS: List[Tuple[str, Tuple[str, ...]]] = [
    (
        "dessert",
        ("新地", "麦旋风", "圆筒", "拉明顿", "冰淇淋", "阿芙佳朵", "派"),
    ),
    (
        "drink",
        (
            "可乐", "雪碧", "咖啡", "美式", "拿铁", "奶铁", "玛奇朵", "卡布奇诺",
            "红茶", "伯爵", "牛奶", "豆浆", "纯悦", "果汁", "苹果汁", "柠檬",
            "怡泉", "雪冰", "燕麦奶", "奶冻", "爆珠", "朱古力", "黑巧", "阳光橙",
            "橙橙",
        ),
    ),
    ("main", ("堡", "卷", "麦满分", "套餐", "三件套", "饭", "粥", "薄饼")),
    (
        "side",
        (
            "薯条", "薯饼", "油条", "玉米杯", "苹果片", "麦乐鸡", "鸡翅", "V翅",
            "鸡排", "鸡球", "脆汁鸡", "香肠", "多笋卷", "沙拉", "叠叠卷",
        ),
    ),
]

# 全角标点 -> 半角，便于跨数据源对名
_PUNCT = str.maketrans("（）［］【】　", "()[][] ")


def normalize(name: str) -> str:
    """把餐品名归一化，用于跨数据源匹配。"""
    s = name.strip().translate(_PUNCT)
    s = re.sub(r"\s+", "", s)
    return s.lower()


def classify(name: str) -> str:
    """按名称判断餐品类型：main / side / drink / dessert。

    营养表没有分类字段，只能靠名称关键词推断；无法判断时归为 main，
    因为"选一份吃的"比"选一杯喝的"更符合默认期待。
    """
    for kind, keywords in KINDS:
        if any(kw in name for kw in keywords):
            return kind
    return "main"


def _to_number(raw: str) -> Optional[float]:
    raw = raw.strip()
    if not raw or raw.lower() in {"null", "none", "-", ""}:
        return None
    try:
        value = float(raw)
        return value if math.isfinite(value) and value >= 0 else None
    except ValueError:
        return None


def parse_nutrition(text: str) -> List[Dict[str, Any]]:
    """解析 list-nutrition-foods 的原始返回文本。

    形如：
        [160]{productName,nutritionDescription,energyKj,...}:
          猪柳麦满分,null,1288,308,16,16,24,781,213
    """
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []

    header_idx = None
    for i, ln in enumerate(lines):
        if re.match(r"^\[\d+\]\{", ln.strip()):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError("营养表缺少 [数量]{字段,...}: 格式的表头")

    header = lines[header_idx].strip()
    inner = header[header.find("{") + 1 : header.rfind("}")]
    columns = [c.strip() for c in inner.split(",")] or COLUMNS
    if not {"productName", "energyKcal", "protein"}.issubset(columns):
        raise ValueError("营养表缺少 productName / energyKcal / protein 必要字段")

    rows: List[Dict[str, Any]] = []
    seen: set = set()
    for ln in lines[header_idx + 1 :]:
        parts = ln.strip().split(",")
        if len(parts) < len(columns):
            continue
        # 餐品名可能自带逗号，反推：尾部固定 n-1 个字段
        name = ",".join(parts[: len(parts) - len(columns) + 1]).strip()
        values = [name] + [p.strip() for p in parts[len(parts) - len(columns) + 1 :]]

        row: Dict[str, Any] = {}
        for col, val in zip(columns, values):
            row[col] = _to_number(val) if col in NUMERIC else val
        if not row.get("productName"):
            continue
        # 只合并内容相同的行；同名但数值冲突的行留给 match 标为待确认
        signature = tuple(row.get(col) for col in columns)
        if signature in seen:
            continue
        seen.add(signature)
        kcal = row.get("energyKcal") or 0.0
        protein = row.get("protein") or 0.0
        row["protein_per_100kcal"] = round(protein / kcal * 100, 1) if kcal > 0 else 0.0
        row["kind"] = classify(row["productName"])
        rows.append(row)
    return rows


def apply_goal(
    rows: Iterable[Dict[str, Any]],
    goal: Optional[str],
    overrides: Dict[str, float],
    kinds: Optional[Iterable[str]] = None,
) -> List[Dict[str, Any]]:
    """按目标与显式阈值过滤并排序。kinds 显式传入时覆盖目标默认类型。"""
    spec = GOALS.get(goal or "", {})
    max_limits = dict(spec.get("max", {}))
    min_limits = dict(spec.get("min", {}))
    for key, value in overrides.items():
        if value is None:
            continue
        if key.startswith("max_"):
            max_limits[key[4:]] = value
        elif key.startswith("min_"):
            min_limits[key[4:]] = value

    allowed = set(kinds) if kinds else set(spec.get("kinds") or [])

    kept = []
    for row in rows:
        if allowed and row.get("kind") not in allowed:
            continue
        if any(
            row.get(f) is None or row[f] > limit for f, limit in max_limits.items()
        ):
            continue
        if any(
            (row.get(f) or 0.0) < limit for f, limit in min_limits.items()
        ):
            continue
        kept.append(row)

    if "sort" in spec:
        sort_field, direction = spec["sort"]
        kept.sort(key=lambda r: r.get(sort_field) or 0.0, reverse=(direction == "desc"))
    return kept


def extract_menu_items(payload: Any) -> List[Dict[str, Any]]:
    """从 query-meals 的返回中抽出 [{code, name, price}]，兼容多种包装。"""
    data = payload.get("data", payload) if isinstance(payload, dict) else payload
    items: List[Dict[str, Any]] = []

    if isinstance(data, dict) and isinstance(data.get("meals"), dict):
        for code, meal in data["meals"].items():
            if isinstance(meal, dict) and meal.get("name"):
                items.append(
                    {
                        "code": str(code),
                        "name": meal["name"],
                        "price": meal.get("currentPrice"),
                    }
                )
        return items

    if isinstance(data, dict) and isinstance(data.get("items"), list):
        for it in data["items"]:
            if isinstance(it, dict) and it.get("name"):
                items.append(
                    {
                        "code": str(it.get("code", "")),
                        "name": it["name"],
                        "price": it.get("price"),
                    }
                )
        return items

    if isinstance(data, list):
        for it in data:
            if isinstance(it, dict) and it.get("name"):
                items.append(
                    {
                        "code": str(it.get("code", "")),
                        "name": it["name"],
                        "price": it.get("price"),
                    }
                )
    return items


# 出现这些词说明菜单项是"组合"，营养库里的单品数值不能代表它
COMBO_HINTS = ("套餐", "三件套", "双人餐", "精选", "随心拼", "四宫格", "拼")


def match_menu(
    menu: List[Dict[str, Any]], nutrition: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """在售菜单 x 营养库 名称对齐。

    返回 (exact, alias, unmatched)：
      exact  —— 名称归一化后唯一匹配；套餐仍需确认组成
      alias  —— 名称/规格未确认或营养行冲突，仅返回候选名称，不返回营养数值
      unmatched —— 营养库没有对应项，不参与严格营养目标计算
    """
    index: Dict[str, List[Dict[str, Any]]] = {}
    for row in nutrition:
        index.setdefault(normalize(row["productName"]), []).append(row)

    exact: List[Dict[str, Any]] = []
    alias: List[Dict[str, Any]] = []
    unmatched: List[Dict[str, Any]] = []
    for item in menu:
        key = normalize(item["name"])
        combo = any(hint in item["name"] for hint in COMBO_HINTS)
        matches = index.get(key, [])
        if len(matches) == 1:
            exact.append({**item, "nutrition": matches[0], "combo": combo})
            continue
        # 前缀只能产生待核实候选，不能用第一条记录决定杯型、份量或套餐热量
        candidates = matches or [
            nrow for nkey, nrows in index.items()
            if key and (nkey.startswith(key) or key.startswith(nkey))
            for nrow in nrows
        ]
        if candidates:
            alias.append(
                {
                    **item,
                    "candidates": sorted({row["productName"] for row in candidates}),
                    "combo": combo,
                    "reason": "同名营养数据冲突" if matches else "名称或规格未确认",
                }
            )
        else:
            unmatched.append(item)
    return exact, alias, unmatched


def _price_cents(value: Any, unit: str) -> Optional[int]:
    """按显式单位转成整数分；未知或不足一分的价格不能用于预算估算。"""
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        return None
    if not amount.is_finite() or amount < 0:
        return None
    cents = amount * (100 if unit == "yuan" else 1)
    return int(cents) if cents == cents.to_integral_value() else None


def plan_meals(
    menu: List[Dict[str, Any]], nutrition: List[Dict[str, Any]],
    goal: str, overrides: Dict[str, float], price_unit: str,
    budget_cents: Optional[int] = None, limit: int = 3,
) -> Dict[str, Any]:
    """枚举 1–3 份单品（可重复），在整餐合计上应用营养约束。

    价格只用于菜单估算，不含券、配送费或打包费，不能替代 calculate-price。
    未确认匹配、套餐、未知价格和热量/蛋白缺失的餐品不参与组合。
    """
    exact, uncertain, unmatched = match_menu(menu, nutrition)
    candidates = []
    for item in exact:
        row = item["nutrition"]
        cents = _price_cents(item.get("price"), price_unit)
        if (item["combo"] or not item.get("code") or cents is None
                or row.get("energyKcal") is None or row.get("protein") is None
                or row.get("kind") not in {"main", "side", "drink"}):
            continue
        candidates.append({**item, "cents": cents})

    def meals():
        for count in range(1, 4):
            for indices in combinations_with_replacement(range(len(candidates)), count):
                selected = [candidates[i] for i in indices]
                if not any(item["nutrition"]["kind"] == "main" for item in selected):
                    continue
                subtotal = sum(item["cents"] for item in selected)
                if budget_cents is not None and subtotal > budget_cents:
                    continue
                totals = {}
                for field in NUMERIC:
                    values = [item["nutrition"].get(field) for item in selected]
                    totals[field] = (
                        round(sum(values), 4) if all(v is not None for v in values) else None
                    )
                kcal = totals["energyKcal"]
                totals["protein_per_100kcal"] = (
                    round(totals["protein"] / kcal * 100, 1) if kcal > 0 else 0.0
                )
                # 用整餐的虚拟行复用阈值校验；不先按单品门槛筛选
                if not apply_goal([{**totals, "kind": "main"}], goal, overrides):
                    continue
                quantities = Counter(item["code"] for item in selected)
                yield {
                    "items": [{"productCode": code, "quantity": qty}
                              for code, qty in quantities.items()],
                    "names": list(dict.fromkeys(item["name"] for item in selected)),
                    "nutrition": totals,
                    "menu_subtotal_cents": subtotal,
                }

    def rank(meal):
        field, direction = GOALS[goal].get("sort", ("energyKcal", "asc"))
        score = meal["nutrition"].get(field) or 0.0
        if direction == "desc":
            score = -score
        # 未指定营养目标时按估价排序，不默认追求高蛋白
        return (score if goal != "any" else 0, meal["menu_subtotal_cents"],
                sum(item["quantity"] for item in meal["items"]))

    return {
        "plans": heapq.nsmallest(limit, meals(), key=rank),
        "pricing": "menu_estimate",
        "budget_cents": budget_cents,
        "max_items": 3,
        "coverage": {"menu_items": len(menu), "exact": len(exact),
                     "uncertain": len(uncertain), "unmatched": len(unmatched),
                     "eligible": len(candidates)},
    }


def _read(path: Optional[str]) -> str:
    if path and path != "-":
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    return sys.stdin.read()


def _fmt(value: Optional[float]) -> str:
    if value is None:
        return "-"
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


def cmd_filter(args: argparse.Namespace) -> int:
    rows = parse_nutrition(_read(args.input))
    overrides = {
        "max_energyKcal": args.max_kcal,
        "max_fat": args.max_fat,
        "max_sodium": args.max_sodium,
        "max_carbohydrate": args.max_carb,
        "min_protein": args.min_protein,
    }
    kinds = [k.strip() for k in args.kind.split(",")] if args.kind else None
    picked = apply_goal(rows, args.goal, overrides, kinds)
    if args.limit:
        picked = picked[: args.limit]

    if args.json:
        print(json.dumps(picked, ensure_ascii=False, indent=2))
        return 0

    if not picked:
        print("没有餐品满足当前营养条件，建议放宽阈值或调整 --kind。", file=sys.stderr)
        return 1

    print(f"# 吃了麦？· 共 {len(rows)} 条营养数据，命中 {len(picked)} 条")
    if args.goal:
        print(f"# 目标：{args.goal}")
    print()
    print("| 餐品 | 类型 | 热量(kcal) | 蛋白(g) | 脂肪(g) | 碳水(g) | 钠(mg) | 蛋白/100kcal |")
    print("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in picked:
        print(
            "| {name} | {kind} | {kcal} | {protein} | {fat} | {carb} | {sodium} | {density} |".format(
                name=row["productName"],
                kind=row.get("kind", "-"),
                kcal=_fmt(row.get("energyKcal")),
                protein=_fmt(row.get("protein")),
                fat=_fmt(row.get("fat")),
                carb=_fmt(row.get("carbohydrate")),
                sodium=_fmt(row.get("sodium")),
                density=_fmt(row.get("protein_per_100kcal")),
            )
        )
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    budget = _price_cents(args.budget, "yuan") if args.budget is not None else None
    if args.budget is not None and budget is None:
        raise ValueError("--budget 必须是非负金额，最多两位小数（元）")
    if args.limit < 1:
        raise ValueError("--limit 必须大于 0")
    overrides = {"max_energyKcal": args.max_kcal, "max_fat": args.max_fat,
                 "max_sodium": args.max_sodium, "max_carbohydrate": args.max_carb,
                 "min_protein": args.min_protein}
    if any(v is not None and (not math.isfinite(v) or v < 0) for v in overrides.values()):
        raise ValueError("营养阈值必须是非负有限数值")
    with open(args.menu, encoding="utf-8") as fh:
        menu = extract_menu_items(json.load(fh))
    result = plan_meals(menu, parse_nutrition(_read(args.nutrition)), args.goal,
                        overrides, args.price_unit, budget, args.limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["plans"]:
        print("可信单品的 1–3 份组合无匹配方案；请检查数据覆盖与约束。"
              "菜单估价不含优惠及配送费，不能据此断言实际预算无解。", file=sys.stderr)
        return 1
    return 0


def _row(item: Dict[str, Any], n: Dict[str, Any], note: str) -> str:
    return "| {code} | {name} | {price} | {nname} | {kcal} | {protein} | {fat} | {sodium} | {note} |".format(
        code=item["code"],
        name=item["name"],
        price=item["price"] if item.get("price") is not None else "-",
        nname=n["productName"],
        kcal=_fmt(n.get("energyKcal")),
        protein=_fmt(n.get("protein")),
        fat=_fmt(n.get("fat")),
        sodium=_fmt(n.get("sodium")),
        note=note,
    )


_HEADER = (
    "| 编码 | 在售名称 | 价格(菜单原值) | 营养库名称 | 热量(kcal) | 蛋白(g) | 脂肪(g) | 钠(mg) | 说明 |",
    "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |",
)


def cmd_match(args: argparse.Namespace) -> int:
    nutrition = parse_nutrition(_read(args.nutrition))
    with open(args.menu, encoding="utf-8") as fh:
        menu = extract_menu_items(json.load(fh))

    exact, alias, unmatched = match_menu(menu, nutrition)
    if args.json:
        print(
            json.dumps(
                {"exact": exact, "alias": alias, "unmatched": unmatched},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print(
        f"# 在售 {len(menu)} 项：精确对齐 {len(exact)}，待确认 {len(alias)}，"
        f"未对齐 {len(unmatched)}"
    )
    print()
    print("## 精确对齐（套餐仍需核实组成，缺失数值不代表零）")
    print()
    print(*_HEADER, sep="\n")
    for item in exact:
        print(_row(item, item["nutrition"], "套餐：需核实组成" if item["combo"] else "-"))

    if alias:
        print()
        print("## 待确认（不提供可用于合计的营养数值）")
        print()
        for item in alias:
            note = "；套餐需核实组成" if item["combo"] else ""
            print(f"- {item['code']} {item['name']} → {' / '.join(item['candidates'])}"
                  f"（{item['reason']}{note}）")

    if unmatched:
        print()
        print("## 未对齐（营养未知，不参与严格营养目标计算）")
        for item in unmatched:
            print(f"- {item['code']} {item['name']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="吃了麦？营养解析/筛选/菜单对齐")
    sub = parser.add_subparsers(dest="command", required=True)

    # 兼容 `--goal low-cal` 与位置式 `low-cal` 两种写法
    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("goal_pos", nargs="?", choices=sorted(GOALS), default=None,
                        help=argparse.SUPPRESS)

    f = sub.add_parser("filter", parents=[shared], help="按营养目标筛选")
    f.add_argument("--goal", choices=sorted(GOALS), default=None)
    f.add_argument("-f", "--input", default=None, help="营养原始文本，默认 stdin")
    f.add_argument("--max-kcal", type=float, default=None)
    f.add_argument("--max-fat", type=float, default=None)
    f.add_argument("--max-sodium", type=float, default=None)
    f.add_argument("--max-carb", type=float, default=None)
    f.add_argument("--min-protein", type=float, default=None)
    f.add_argument(
        "--kind",
        default=None,
        help="只保留指定类型，逗号分隔：main,side,drink,dessert",
    )
    f.add_argument("--limit", type=int, default=None)
    f.add_argument("--json", action="store_true")
    f.set_defaults(func=cmd_filter)

    m = sub.add_parser("match", help="在售菜单与营养库对齐")
    m.add_argument("--menu", required=True, help="query-meals 返回的 JSON 文件")
    m.add_argument("--nutrition", default=None, help="营养原始文本，默认 stdin")
    m.add_argument("--json", action="store_true")
    m.set_defaults(func=cmd_match)

    p = sub.add_parser("plan", help="按整餐营养组合 1–3 份可信单品，输出 JSON")
    p.add_argument("--menu", required=True, help="query-meals 返回的 JSON 文件")
    p.add_argument("--nutrition", default=None, help="营养原始文本，默认 stdin")
    p.add_argument("--price-unit", required=True, choices=["yuan", "fen"],
                   help="菜单价格原值单位，必须先核实；不代表官方实付金额")
    p.add_argument("--goal", choices=sorted(GOALS), default="any")
    p.add_argument("--budget", default=None, help="可选的菜单估价上限（元），不含优惠及配送费")
    p.add_argument("--max-kcal", type=float, default=None)
    p.add_argument("--max-fat", type=float, default=None)
    p.add_argument("--max-sodium", type=float, default=None)
    p.add_argument("--max-carb", type=float, default=None)
    p.add_argument("--min-protein", type=float, default=None)
    p.add_argument("--limit", type=int, default=3)
    p.set_defaults(func=cmd_plan)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "goal", None) is None and getattr(args, "goal_pos", None):
        args.goal = args.goal_pos
    try:
        return args.func(args)
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
