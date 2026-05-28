#!/usr/bin/env python3
"""Medical Unit Converter - Lab value unit conversions."""

import argparse
import json
import sys

# CONVERSIONS keyed by (analyte, from_unit, to_unit)
# Units normalised: mg/dL → mg_dl, mmol/L → mmol_l, umol/L → umol_l, mEq/L → meq_l
CONVERSIONS = {
    # Cholesterol
    ("cholesterol", "mg_dl", "mmol_l"): {
        "factor": 1 / 38.67,
        "reference_range": "< 5.18 mmol/L (desirable)",
    },
    ("cholesterol", "mmol_l", "mg_dl"): {
        "factor": 38.67,
        "reference_range": "< 200 mg/dL (desirable)",
    },
    # Creatinine
    ("creatinine", "mg_dl", "umol_l"): {
        "factor": 88.42,
        "reference_range": "44–97 umol/L (female), 62–115 umol/L (male)",
    },
    ("creatinine", "umol_l", "mg_dl"): {
        "factor": 1 / 88.42,
        "reference_range": "0.5–1.1 mg/dL (female), 0.7–1.3 mg/dL (male)",
    },
    # Hemoglobin
    ("hemoglobin", "g_dl", "mmol_l"): {
        "factor": 1 / 1.611,
        "reference_range": "7.4–9.9 mmol/L (female), 8.7–11.2 mmol/L (male)",
    },
    ("hemoglobin", "mmol_l", "g_dl"): {
        "factor": 1.611,
        "reference_range": "12.0–16.0 g/dL (female), 14.0–18.0 g/dL (male)",
    },
    # Glucose
    ("glucose", "mg_dl", "mmol_l"): {
        "factor": 1 / 18.02,
        "reference_range": "3.9–5.6 mmol/L (fasting)",
    },
    ("glucose", "mmol_l", "mg_dl"): {
        "factor": 18.02,
        "reference_range": "70–100 mg/dL (fasting)",
    },
    # Triglycerides
    ("triglycerides", "mg_dl", "mmol_l"): {
        "factor": 1 / 88.57,
        "reference_range": "< 1.70 mmol/L (desirable)",
    },
    ("triglycerides", "mmol_l", "mg_dl"): {
        "factor": 88.57,
        "reference_range": "< 150 mg/dL (desirable)",
    },
    # Urea
    ("urea", "mg_dl", "mmol_l"): {
        "factor": 1 / 2.801,
        "reference_range": "2.5–7.1 mmol/L",
    },
    ("urea", "mmol_l", "mg_dl"): {
        "factor": 2.801,
        "reference_range": "7–20 mg/dL",
    },
    # Calcium
    ("calcium", "mg_dl", "mmol_l"): {
        "factor": 1 / 4.008,
        "reference_range": "2.15–2.55 mmol/L",
    },
    ("calcium", "mmol_l", "mg_dl"): {
        "factor": 4.008,
        "reference_range": "8.6–10.2 mg/dL",
    },
    # Sodium (1:1 mEq/L ↔ mmol/L)
    ("sodium", "meq_l", "mmol_l"): {
        "factor": 1.0,
        "reference_range": "136–145 mmol/L",
    },
    ("sodium", "mmol_l", "meq_l"): {
        "factor": 1.0,
        "reference_range": "136–145 mEq/L",
    },
    # Potassium (1:1 mEq/L ↔ mmol/L)
    ("potassium", "meq_l", "mmol_l"): {
        "factor": 1.0,
        "reference_range": "3.5–5.0 mmol/L",
    },
    ("potassium", "mmol_l", "meq_l"): {
        "factor": 1.0,
        "reference_range": "3.5–5.0 mEq/L",
    },
}

SUPPORTED_ANALYTES = sorted({k[0] for k in CONVERSIONS})


def normalise_unit(unit: str) -> str:
    """Normalise unit string to internal key format."""
    return (
        unit.lower()
        .replace("/", "_")
        .replace(" ", "_")
        .replace("-", "_")
    )


def convert(value: float, analyte: str, from_unit: str, to_unit: str) -> dict:
    """Perform the conversion and return a result dict."""
    analyte_key = analyte.lower()
    from_key = normalise_unit(from_unit)
    to_key = normalise_unit(to_unit)

    lookup = (analyte_key, from_key, to_key)
    if lookup not in CONVERSIONS:
        supported = ", ".join(SUPPORTED_ANALYTES)
        print(
            f"Error: unsupported conversion '{from_unit}' → '{to_unit}' for analyte '{analyte}'.\n"
            f"Supported analytes: {supported}",
            file=sys.stderr,
        )
        sys.exit(1)

    conv = CONVERSIONS[lookup]
    output_value = round(value * conv["factor"], 4)

    return {
        "analyte": analyte,
        "input_value": value,
        "input_unit": from_unit,
        "output_value": output_value,
        "output_unit": to_unit,
        "reference_range": conv["reference_range"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Convert medical lab values between units.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py --analyte glucose --value 100 --from-unit mg/dL --to-unit mmol/L\n"
            "  python main.py --analyte cholesterol --value 5.2 --from-unit mmol/L --to-unit mg/dL\n"
            f"\nSupported analytes: {', '.join(SUPPORTED_ANALYTES)}"
        ),
    )
    parser.add_argument("--value", type=float, required=True, help="Numeric value to convert")
    parser.add_argument("--from-unit", required=True, help="Source unit (e.g. mg/dL)")
    parser.add_argument("--to-unit", required=True, help="Target unit (e.g. mmol/L)")
    parser.add_argument(
        "--analyte",
        required=True,
        help=f"Analyte name. Supported: {', '.join(SUPPORTED_ANALYTES)}",
    )

    args = parser.parse_args()

    result = convert(
        value=args.value,
        analyte=args.analyte,
        from_unit=args.from_unit,
        to_unit=args.to_unit,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
