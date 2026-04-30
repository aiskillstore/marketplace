"""Extract key points from a text file using simple sentence scoring."""

import argparse
import sys


def extract_key_points(filepath, max_points=10):
    """Read a text file and return the top N most important sentences."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: File is not valid UTF-8 text: {filepath}", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print("Error: File is empty", file=sys.stderr)
        sys.exit(1)

    # Split into sentences (simple approach)
    sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]

    # Score sentences by length and position (longer sentences earlier in doc score higher)
    scored = []
    for i, sentence in enumerate(sentences):
        position_weight = 1.0 - (i / max(len(sentences), 1)) * 0.5
        length_weight = min(len(sentence.split()) / 20.0, 1.0)
        score = position_weight * length_weight
        scored.append((score, sentence))

    scored.sort(reverse=True)
    top_points = [s for _, s in scored[:max_points]]

    for point in top_points:
        print(f"- {point}")


def main():
    parser = argparse.ArgumentParser(description="Extract key points from a text file")
    parser.add_argument("--file", required=True, help="Path to the input text file")
    parser.add_argument("--max-points", type=int, default=10, help="Maximum key points to extract")
    args = parser.parse_args()

    extract_key_points(args.file, args.max_points)


if __name__ == "__main__":
    main()
