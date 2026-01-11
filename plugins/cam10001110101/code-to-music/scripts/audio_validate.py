#!/usr/bin/env python3
"""
Validate audio quality and detect issues in MP3/WAV files.

This script performs quality control checks on any audio file:
- Audio clipping detection (peaks > 0dB)
- Silence detection (empty sections)
- Duration verification
- Abrupt volume changes
- Dynamic range analysis

Usage:
    python audio_validate.py output.mp3 [--expected-duration 90]
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from pydub import AudioSegment
from pydub.utils import db_to_float


class ValidationResult:
    def __init__(self):
        self.passed = True
        self.errors = []
        self.warnings = []

    def add_error(self, message: str):
        self.errors.append(message)
        self.passed = False

    def add_warning(self, message: str):
        self.warnings.append(message)

    def print_results(self):
        if self.passed and not self.warnings:
            print("\n✓ VALIDATION PASSED - No issues detected")
            return

        if self.errors:
            print("\n✗ VALIDATION FAILED")
            print("\nErrors (must fix):")
            for error in self.errors:
                print(f"  ✗ {error}")

        if self.warnings:
            print("\nWarnings (should review):")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")

        if not self.errors:
            print("\n⚠ VALIDATION PASSED WITH WARNINGS")


def validate_audio(audio_path: Path, expected_duration: float = None) -> ValidationResult:
    """Perform comprehensive audio validation."""
    result = ValidationResult()

    try:
        audio = AudioSegment.from_file(str(audio_path))
    except Exception as e:
        result.add_error(f"Failed to load audio file: {e}")
        return result

    actual_duration = len(audio) / 1000.0

    if expected_duration:
        duration_diff = abs(actual_duration - expected_duration)
        if duration_diff > 2.0:
            result.add_error(
                f"Duration mismatch: expected {expected_duration:.1f}s, got {actual_duration:.1f}s "
                f"(diff: {duration_diff:.1f}s)"
            )
        elif duration_diff > 0.5:
            result.add_warning(
                f"Duration slightly off: expected {expected_duration:.1f}s, got {actual_duration:.1f}s "
                f"(diff: {duration_diff:.1f}s)"
            )

    max_db = audio.max_dBFS
    if max_db > -0.1:
        result.add_error(
            f"Audio clipping detected: peak level is {max_db:.1f} dBFS "
            f"(should be below -0.1 dBFS to avoid distortion)"
        )
    elif max_db > -1.0:
        result.add_warning(
            f"Audio very loud: peak level is {max_db:.1f} dBFS "
            f"(recommended: -3 to -6 dBFS for headroom)"
        )

    rms_db = audio.dBFS
    if rms_db < -40.0:
        result.add_warning(
            f"Audio very quiet: RMS level is {rms_db:.1f} dBFS "
            f"(recommended: -15 to -20 dBFS)"
        )

    silent_threshold = -50.0
    chunk_length = 1000
    silent_chunks = 0
    total_chunks = len(audio) // chunk_length

    for i in range(0, len(audio), chunk_length):
        chunk = audio[i:i + chunk_length]
        if chunk.dBFS < silent_threshold:
            silent_chunks += 1

    silence_percent = (silent_chunks / total_chunks) * 100 if total_chunks > 0 else 0

    if silence_percent > 50:
        result.add_error(
            f"Excessive silence detected: {silence_percent:.1f}% of audio is silent "
            f"(threshold: {silent_threshold} dBFS)"
        )
    elif silence_percent > 20:
        result.add_warning(
            f"Significant silence: {silence_percent:.1f}% of audio is silent"
        )

    window_size = 2000
    volumes = []
    for i in range(0, len(audio) - window_size, window_size // 2):
        chunk = audio[i:i + window_size]
        volumes.append(chunk.dBFS)

    if len(volumes) > 1:
        volume_changes = [abs(volumes[i+1] - volumes[i]) for i in range(len(volumes)-1)]
        max_change = max(volume_changes) if volume_changes else 0

        if max_change > 20:
            result.add_warning(
                f"Abrupt volume change detected: {max_change:.1f} dB jump "
                f"(may sound jarring to listeners)"
            )

    dynamic_range = max_db - rms_db
    if dynamic_range < 3:
        result.add_warning(
            f"Limited dynamic range: {dynamic_range:.1f} dB "
            f"(audio may sound compressed or lifeless)"
        )

    print(f"\nAudio Analysis:")
    print(f"  Duration: {actual_duration:.2f}s")
    print(f"  Peak level: {max_db:.1f} dBFS")
    print(f"  RMS level: {rms_db:.1f} dBFS")
    print(f"  Dynamic range: {dynamic_range:.1f} dB")
    print(f"  Silence: {silence_percent:.1f}%")
    print(f"  Channels: {audio.channels}")
    print(f"  Sample rate: {audio.frame_rate} Hz")
    print(f"  Bit depth: {audio.sample_width * 8} bit")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Validate audio quality and detect issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python audio_validate.py output.mp3
    Check audio file for quality issues

  python audio_validate.py output.mp3 --expected-duration 90
    Verify duration matches expected 90 seconds

  python audio_validate.py output.wav --expected-duration 60
    Validate WAV file with expected duration

Checks performed:
  - Audio clipping (peaks > 0dB)
  - Excessive silence
  - Duration accuracy
  - Abrupt volume changes
  - Dynamic range
  - Overall loudness levels
        """
    )

    parser.add_argument("input", help="Input audio file (MP3, WAV, etc.)")
    parser.add_argument(
        "--expected-duration",
        type=float,
        help="Expected duration in seconds (for verification)"
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    print(f"Validating: {args.input}")

    result = validate_audio(input_path, args.expected_duration)
    result.print_results()

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()