"""Set up to force formulas to be recalculated when Excel is opened."""

from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook


CONFIG = {
    "input_file": "input.xlsx",
    "output_file": "output_recalc.xlsx",
}


def main() -> None:
    workbook = load_workbook(CONFIG["input_file"])
    workbook.calcProperties.fullCalcOnLoad = True
    workbook.calcProperties.calcMode = "auto"

    output_path = Path(CONFIG["output_file"])
    workbook.save(output_path)
    print(f"Recalculation flag set: {output_path}")


if __name__ == "__main__":
    main()
