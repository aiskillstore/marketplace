#!/usr/bin/env python3
"""Horizontal value comparison for liuzi-kitchen social-intel research."""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass
class Option:
    name: str
    price: float
    servings: float
    minutes: float
    reuse: float
    risk: float
    sources: float

    @property
    def cost_per_serving(self) -> float:
        return self.price / self.servings if self.servings else self.price

    @property
    def score(self) -> float:
        cost_score = max(0.0, 5.0 - self.cost_per_serving)
        time_score = max(0.0, 5.0 - (self.minutes / 20.0))
        reuse_score = min(5.0, self.reuse)
        safety_score = max(0.0, 5.0 - self.risk)
        source_score = min(5.0, 1.5 + self.sources)
        return (
            cost_score * 0.34
            + time_score * 0.16
            + reuse_score * 0.20
            + safety_score * 0.18
            + source_score * 0.12
        )


def parse_option(raw: str) -> Option:
    parts = [part.strip() for part in raw.split("|")]
    if len(parts) != 7:
        raise argparse.ArgumentTypeError(
            "--option must use: name|price|servings|minutes|reuse_1to5|risk_0to5|source_count"
        )
    name, price, servings, minutes, reuse, risk, sources = parts
    return Option(
        name=name,
        price=float(price),
        servings=float(servings),
        minutes=float(minutes),
        reuse=float(reuse),
        risk=float(risk),
        sources=float(sources),
    )


def text(zh: str, en: str, lang: str) -> str:
    if lang == "zh":
        return zh
    if lang == "en":
        return en
    return f"{zh} / {en}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare grocery, recipe, or meal-prep options by true student-kitchen value."
    )
    parser.add_argument(
        "--option",
        action="append",
        type=parse_option,
        required=True,
        help="Repeatable. Format: name|price|servings|minutes|reuse_1to5|risk_0to5|source_count",
    )
    parser.add_argument("--lang", choices=("zh", "en", "zh-en"), default="zh-en")
    args = parser.parse_args()

    ranked = sorted(args.option, key=lambda item: item.score, reverse=True)

    print(text("横向性价比对比", "Horizontal Value Comparison", args.lang))
    print("=" * 78)
    header = text(
        "选项 | 每份成本 | 时间 | 复用 | 风险 | 来源数 | 总分",
        "Option | Cost/serving | Time | Reuse | Risk | Sources | Score",
        args.lang,
    )
    print(header)
    print("-" * 78)
    for item in ranked:
        print(
            f"{item.name} | ${item.cost_per_serving:.2f} | "
            f"{item.minutes:.0f} min | {item.reuse:.1f}/5 | {item.risk:.1f}/5 | "
            f"{item.sources:.0f} | {item.score:.2f}/5"
        )

    winner = ranked[0]
    print()
    print(text("推荐", "Recommendation", args.lang))
    print("- " + text(
        f"{winner.name} 综合胜出：每份约 ${winner.cost_per_serving:.2f}，复用 {winner.reuse:.1f}/5，风险 {winner.risk:.1f}/5。",
        f"{winner.name} wins overall: about ${winner.cost_per_serving:.2f}/serving, reuse {winner.reuse:.1f}/5, risk {winner.risk:.1f}/5.",
        args.lang,
    ))
    print("- " + text(
        "如果本地价格、会员费、交通时间、冰箱空间不同，请重新填入参数再比较。",
        "If local price, membership cost, travel time, or fridge/freezer space differs, rerun with updated inputs.",
        args.lang,
    ))
    print("- " + text(
        "风险分越高代表越不确定或越麻烦，例如易坏、要处理生肉、储存困难、攻略来源少。",
        "Higher risk means more uncertainty or friction, such as spoilage, raw-meat handling, storage trouble, or weak source evidence.",
        args.lang,
    ))


if __name__ == "__main__":
    main()
