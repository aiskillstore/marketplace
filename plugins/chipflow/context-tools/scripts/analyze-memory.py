#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "tree-sitter>=0.23.0",
#     "tree-sitter-cpp>=0.23.0",
#     "tree-sitter-rust>=0.23.0",
#     "psutil>=5.9.0",
# ]
# ///
"""
Analyze memory usage during repo-map parsing.
Run on a large codebase to understand memory behavior.

Usage:
    uv run analyze-memory.py /path/to/codebase
"""

import gc
import os
import sys
import time
from pathlib import Path

import psutil

# Import parsing functions from generate-repo-map.py
import importlib.util
spec = importlib.util.spec_from_file_location(
    "generate_repo_map",
    Path(__file__).parent / "generate-repo-map.py"
)
generate_repo_map = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_repo_map)

extract_symbols_from_cpp = generate_repo_map.extract_symbols_from_cpp
extract_symbols_from_python = generate_repo_map.extract_symbols_from_python
extract_symbols_from_rust = generate_repo_map.extract_symbols_from_rust
find_cpp_files = generate_repo_map.find_cpp_files
find_python_files = generate_repo_map.find_python_files
find_rust_files = generate_repo_map.find_rust_files


def get_process_memory_mb() -> float:
    """Get current process memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def analyze_files(files: list[Path], extractor, language: str, root: Path):
    """Analyze memory usage for a list of files."""
    print(f"\n{'='*60}")
    print(f"Analyzing {len(files)} {language} files")
    print(f"{'='*60}")

    if not files:
        print("  No files found")
        return

    # Sort by size to find largest files
    files_with_size = [(f, f.stat().st_size) for f in files]
    files_with_size.sort(key=lambda x: x[1], reverse=True)

    # Show top 10 largest files
    print(f"\nTop 10 largest {language} files:")
    for f, size in files_with_size[:10]:
        print(f"  {size/1024:.1f} KB - {f.relative_to(root)}")

    # Parse files and track memory
    print(f"\nParsing files and tracking memory...")

    gc.collect()
    initial_mem = get_process_memory_mb()
    print(f"Initial memory: {initial_mem:.1f} MB")

    total_symbols = 0
    max_mem = initial_mem
    max_mem_file = None

    # Parse top 50 largest files
    test_files = [f for f, _ in files_with_size[:50]]

    for i, file_path in enumerate(test_files):
        gc.collect()
        before_mem = get_process_memory_mb()

        try:
            symbols = extractor(file_path, root)
            total_symbols += len(symbols)
        except Exception as e:
            print(f"  Error parsing {file_path}: {e}")
            continue

        after_mem = get_process_memory_mb()

        if after_mem > max_mem:
            max_mem = after_mem
            max_mem_file = file_path

        # Report every 10 files or if memory spike
        if (i + 1) % 10 == 0 or (after_mem - before_mem) > 10:
            print(f"  [{i+1}/{len(test_files)}] Memory: {after_mem:.1f} MB "
                  f"(delta: {after_mem - before_mem:+.1f} MB, "
                  f"symbols: {len(symbols)})")

    gc.collect()
    final_mem = get_process_memory_mb()

    print(f"\nResults for {language}:")
    print(f"  Files parsed: {len(test_files)}")
    print(f"  Total symbols: {total_symbols}")
    print(f"  Initial memory: {initial_mem:.1f} MB")
    print(f"  Peak memory: {max_mem:.1f} MB")
    print(f"  Final memory: {final_mem:.1f} MB")
    print(f"  Memory growth: {final_mem - initial_mem:.1f} MB")
    if max_mem_file:
        print(f"  Peak at: {max_mem_file.relative_to(root)}")


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    print(f"Analyzing memory usage in: {root}")
    print(f"Process PID: {os.getpid()}")
    print(f"Initial memory: {get_process_memory_mb():.1f} MB")

    # Find all files
    print("\nFinding source files...")
    python_files = find_python_files(root)
    cpp_files = find_cpp_files(root)
    rust_files = find_rust_files(root)

    print(f"  Python: {len(python_files)} files")
    print(f"  C++: {len(cpp_files)} files")
    print(f"  Rust: {len(rust_files)} files")

    # Analyze each language
    if cpp_files:
        analyze_files(cpp_files, extract_symbols_from_cpp, "C++", root)

    if rust_files:
        analyze_files(rust_files, extract_symbols_from_rust, "Rust", root)

    if python_files:
        analyze_files(python_files, extract_symbols_from_python, "Python", root)

    # Final summary
    gc.collect()
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"Final process memory: {get_process_memory_mb():.1f} MB")


if __name__ == "__main__":
    main()
