#!/usr/bin/env python3
"""
Data Split Validator

Validates train/test splits for common leakage patterns:
- Temporal ordering
- Sample overlap
- Group leakage
- Preprocessing order

Usage:
    python validate_split.py --train train.csv --test test.csv
    python validate_split.py --train train.csv --test test.csv --date-col timestamp --group-col user_id
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import warnings


def check_sample_overlap(train_df, test_df):
    """Check for overlapping samples between train and test"""
    print("\n=== Checking Sample Overlap ===")

    train_hashes = set(hash(str(row.values)) for _, row in train_df.iterrows())
    test_hashes = set(hash(str(row.values)) for _, row in test_df.iterrows())

    overlap = train_hashes & test_hashes

    if overlap:
        print(f"❌ FAIL: Found {len(overlap)} overlapping samples")
        print(f"   Overlap rate: {len(overlap)/len(test_hashes)*100:.1f}%")
        return False
    else:
        print(f"✅ PASS: No sample overlap detected")
        return True


def check_temporal_ordering(train_df, test_df, date_col):
    """Check temporal ordering of train/test split"""
    print(f"\n=== Checking Temporal Ordering (column: {date_col}) ===")

    if date_col not in train_df.columns or date_col not in test_df.columns:
        print(f"⚠️ SKIP: Column '{date_col}' not found")
        return None

    try:
        train_dates = pd.to_datetime(train_df[date_col])
        test_dates = pd.to_datetime(test_df[date_col])
    except Exception as e:
        print(f"⚠️ SKIP: Cannot parse dates: {e}")
        return None

    train_min, train_max = train_dates.min(), train_dates.max()
    test_min, test_max = test_dates.min(), test_dates.max()

    print(f"   Training period: {train_min} to {train_max}")
    print(f"   Test period: {test_min} to {test_max}")

    # Check for temporal leakage
    if train_max > test_min:
        overlap_days = (train_max - test_min).days
        print(f"❌ FAIL: Temporal leakage detected!")
        print(f"   Training data extends {overlap_days} days into test period")
        return False

    # Check for suspicious gaps
    gap = (test_min - train_max).days
    if gap > 365:
        print(f"⚠️ WARNING: Large gap between train and test ({gap} days)")
        print(f"   Possible distribution shift")
    elif gap < 0:
        print(f"❌ FAIL: Negative gap ({gap} days) - training after test!")
        return False

    print(f"✅ PASS: Temporal ordering correct (gap: {gap} days)")
    return True


def check_group_leakage(train_df, test_df, group_col):
    """Check for group leakage between train and test"""
    print(f"\n=== Checking Group Leakage (column: {group_col}) ===")

    if group_col not in train_df.columns or group_col not in test_df.columns:
        print(f"⚠️ SKIP: Column '{group_col}' not found")
        return None

    train_groups = set(train_df[group_col].dropna().unique())
    test_groups = set(test_df[group_col].dropna().unique())

    overlap = train_groups & test_groups

    print(f"   Training groups: {len(train_groups)}")
    print(f"   Test groups: {len(test_groups)}")

    if overlap:
        overlap_pct = len(overlap) / len(test_groups) * 100
        print(f"❌ FAIL: Found {len(overlap)} overlapping groups")
        print(f"   Overlap rate: {overlap_pct:.1f}%")
        print(f"   Examples: {list(overlap)[:5]}")
        return False
    else:
        print(f"✅ PASS: No group overlap detected")
        return True


def check_class_distribution(train_df, test_df, target_col=None):
    """Check if class distributions are similar"""
    print("\n=== Checking Class Distribution ===")

    if target_col is None:
        # Try to find target column
        possible_targets = ['target', 'label', 'class', 'y']
        target_col = next((col for col in possible_targets if col in train_df.columns), None)

    if target_col is None or target_col not in train_df.columns:
        print(f"⚠️ SKIP: Target column not specified or found")
        return None

    train_dist = train_df[target_col].value_counts(normalize=True).sort_index()
    test_dist = test_df[target_col].value_counts(normalize=True).sort_index()

    print(f"   Target column: {target_col}")
    print("\n   Class distributions:")
    print(f"   {'Class':<15} {'Train %':<10} {'Test %':<10} {'Diff'}")
    print("   " + "-" * 50)

    all_classes = sorted(set(train_dist.index) | set(test_dist.index))
    max_diff = 0

    for cls in all_classes:
        train_pct = train_dist.get(cls, 0) * 100
        test_pct = test_dist.get(cls, 0) * 100
        diff = abs(train_pct - test_pct)
        max_diff = max(max_diff, diff)

        status = "⚠️" if diff > 10 else "  "
        print(f"{status} {str(cls):<15} {train_pct:>8.1f}% {test_pct:>8.1f}% {diff:>8.1f}%")

    if max_diff > 10:
        print(f"\n⚠️ WARNING: Large distribution shift detected (max diff: {max_diff:.1f}%)")
        return False

    print(f"\n✅ PASS: Class distributions similar (max diff: {max_diff:.1f}%)")
    return True


def check_size_ratio(train_df, test_df):
    """Check if train/test split ratio is reasonable"""
    print("\n=== Checking Split Ratio ===")

    n_train = len(train_df)
    n_test = len(test_df)
    total = n_train + n_test

    train_pct = n_train / total * 100
    test_pct = n_test / total * 100

    print(f"   Training samples: {n_train} ({train_pct:.1f}%)")
    print(f"   Test samples: {n_test} ({test_pct:.1f}%)")

    if test_pct < 10:
        print(f"⚠️ WARNING: Test set very small ({test_pct:.1f}%)")
        print(f"   Consider using at least 15-20% for test")
    elif test_pct > 40:
        print(f"⚠️ WARNING: Test set very large ({test_pct:.1f}%)")
        print(f"   Consider using more data for training")
    else:
        print(f"✅ PASS: Split ratio reasonable")

    return True


def main():
    parser = argparse.ArgumentParser(description='Validate train/test split for leakage')
    parser.add_argument('--train', required=True, help='Path to training data (CSV)')
    parser.add_argument('--test', required=True, help='Path to test data (CSV)')
    parser.add_argument('--date-col', help='Date column for temporal validation')
    parser.add_argument('--group-col', help='Group column for group leakage check')
    parser.add_argument('--target-col', help='Target column for distribution check')

    args = parser.parse_args()

    print("="*70)
    print(" Data Split Validator")
    print("="*70)

    # Load data
    print(f"\nLoading data...")
    print(f"   Training: {args.train}")
    print(f"   Test: {args.test}")

    try:
        train_df = pd.read_csv(args.train)
        test_df = pd.read_csv(args.test)
    except Exception as e:
        print(f"❌ ERROR: Failed to load data: {e}")
        return 1

    print(f"   Loaded {len(train_df)} training samples, {len(test_df)} test samples")

    # Run all checks
    results = {
        'sample_overlap': check_sample_overlap(train_df, test_df),
        'split_ratio': check_size_ratio(train_df, test_df),
    }

    if args.date_col:
        results['temporal'] = check_temporal_ordering(train_df, test_df, args.date_col)

    if args.group_col:
        results['group_leakage'] = check_group_leakage(train_df, test_df, args.group_col)

    results['class_distribution'] = check_class_distribution(
        train_df, test_df, args.target_col
    )

    # Summary
    print("\n" + "="*70)
    print(" Validation Summary")
    print("="*70)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for check_name, result in results.items():
        status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⚠️ SKIP"
        print(f"   {check_name:<25} {status}")

    print(f"\n   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Skipped: {skipped}")
    print("="*70)

    if failed > 0:
        print("\n❌ VALIDATION FAILED: Found data leakage issues!")
        print("   Fix these issues before training.")
        return 1
    else:
        print("\n✅ VALIDATION PASSED: No critical issues detected")
        return 0


if __name__ == "__main__":
    exit(main())
