#!/usr/bin/env python3
"""estimate_recurring.py -- estimate a recurring AI job's spend BEFORE you build it.

Stdlib only. Multiplies runs/day x tokens/run and compares the result with a
weekly allowance. The result is a FLOOR, not a ceiling: retries, growing
inputs and overlapping jobs only push real spend above it.

That is exactly what happened in anthropics/claude-code#110395: the straight
maths said about 15.6 days to empty a 361.6M weekly allowance; the job
emptied it in 3.83 days because a failure loop ran 39 times in a row and
other automations stacked on top.

Usage:
  estimate_recurring.py --interval-min 5 --tokens-per-run 40000 --weekly-allowance 361600000
  estimate_recurring.py --interval-min 10 --tokens-per-run 40000 --weekly-allowance 361600000 --price-per-mtok 3
"""

import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="estimate_recurring.py",
        description="Estimate a recurring AI job's spend before you build it.",
    )
    parser.add_argument("--interval-min", type=float, required=True,
                        help="minutes between runs")
    parser.add_argument("--tokens-per-run", type=int, required=True,
                        help="tokens used per run (input + output)")
    parser.add_argument("--weekly-allowance", type=int, default=0,
                        help="weekly token allowance, 0 = no allowance to check")
    parser.add_argument("--retry-factor", type=float, default=1.0,
                        help="multiplier for retries (default 1.0 = no retries)")
    parser.add_argument("--active-hours", type=float, default=24.0,
                        help="hours per day the job runs (default 24)")
    parser.add_argument("--price-per-mtok", type=float, default=0.0,
                        help="blended USD price per 1M tokens, 0 = skip cost")
    args = parser.parse_args(argv)

    if args.interval_min <= 0:
        parser.error("--interval-min must be above 0")
    if args.tokens_per_run < 0:
        parser.error("--tokens-per-run must be 0 or more")
    if not 0 < args.active_hours <= 24:
        parser.error("--active-hours must be between 0 and 24")
    if args.retry_factor < 1:
        parser.error("--retry-factor must be 1 or more")
    if args.weekly_allowance < 0:
        parser.error("--weekly-allowance must be 0 or more")

    runs_per_day = args.active_hours * 60.0 / args.interval_min
    tokens_per_day = runs_per_day * args.tokens_per_run * args.retry_factor
    print(f"runs per day: {runs_per_day:.1f}")
    print(f"tokens per day: {tokens_per_day:,.0f}")
    if args.weekly_allowance > 0:
        days = args.weekly_allowance / tokens_per_day if tokens_per_day else float("inf")
        print(f"days to empty weekly allowance: {days:.2f}")
        if days >= 7:
            print("fits in a week: yes -- on paper")
        else:
            print("fits in a week: NO -- allowance runs out in under 7 days")
    if args.price_per_mtok > 0:
        print(f"estimated cost per day: ${tokens_per_day / 1_000_000 * args.price_per_mtok:.2f}")
    print("WARNING: this is a floor, not a ceiling. Retries, failure loops and")
    print("overlapping jobs push real spend higher. Add a cap before you ship it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
