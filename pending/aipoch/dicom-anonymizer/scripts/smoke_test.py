#!/usr/bin/env python3
"""Deterministic smoke test for dicom-anonymizer."""

from __future__ import annotations

import json

from main import DICOMAnonymizer, HAS_PYDICOM


def main() -> None:
    anonymizer = DICOMAnonymizer(
        preserve_studies=True,
        keep_tags=["PatientAge"],
        remove_private=True,
    )
    payload = {
        "class": anonymizer.__class__.__name__,
        "has_pydicom": HAS_PYDICOM,
        "preserve_studies": anonymizer.preserve_studies,
        "remove_private": anonymizer.remove_private,
        "keep_tags": sorted(anonymizer.keep_tags),
        "phi_tag_count": len(anonymizer.PHI_TAGS),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
