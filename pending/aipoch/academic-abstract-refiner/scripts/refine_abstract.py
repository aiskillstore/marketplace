#!/usr/bin/env python3
import argparse
import os


def read_abstracts(args):
    if not args.abstract_zh or not args.abstract_en:
        raise SystemExit("Provide both --abstract-zh and --abstract-en")
    return args.abstract_zh, args.abstract_en


def render_report(abstract_zh, abstract_en):
    lines = ["# Summary Report", "", "## Chinese Abstract", abstract_zh.strip(), ""]
    lines += ["## English Abstract", abstract_en.strip(), ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Render bilingual abstracts into Summary_Report.md"
    )
    parser.add_argument("--abstract-zh", help="Chinese abstract text")
    parser.add_argument("--abstract-en", help="English abstract text")
    parser.add_argument("--output", "-o", default="Summary_Report.md")
    args = parser.parse_args()

    abstract_zh, abstract_en = read_abstracts(args)

    report = render_report(abstract_zh, abstract_en)
    output_path = args.output
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
