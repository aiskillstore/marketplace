#!/usr/bin/env python3
"""
Research Conflict Detection Script.

Detect duplicates and conflicts between research findings.

Usage:
    python detect_conflicts.py FILE1 FILE2 [FILE3...] [--mode MODE]

Output:
    JSON object with detected conflicts/duplicates
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


def tokenize(text: str) -> Set[str]:
    """Tokenize text into word set."""
    words = re.findall(r'\b\w+\b', text.lower())
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'could', 'should', 'may', 'might', 'must', 'can',
                  'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                  'as', 'into', 'through', 'during', 'before', 'after', 'above',
                  'below', 'between', 'under', 'again', 'further', 'then', 'once',
                  'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either',
                  'neither', 'not', 'only', 'own', 'same', 'than', 'too', 'very',
                  'just', 'also', 'now', 'here', 'there', 'when', 'where', 'why',
                  'how', 'all', 'each', 'every', 'some', 'any', 'few', 'more',
                  'most', 'other', 'no', 'this', 'that', 'these', 'those', 'it'}
    return set(words) - stop_words


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def extract_statements(content: str) -> List[Dict[str, Any]]:
    """Extract statements/claims from content."""
    statements = []

    # Extract bullet points
    for match in re.finditer(r'^[\-\*]\s+(.+)$', content, re.MULTILINE):
        statements.append({
            "text": match.group(1).strip(),
            "type": "bullet"
        })

    # Extract sentences from paragraphs (simplified)
    paragraphs = re.split(r'\n\n+', content)
    for para in paragraphs:
        if para.strip() and not para.strip().startswith('#'):
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sent in sentences:
                if len(sent) > 20:  # Skip very short sentences
                    statements.append({
                        "text": sent.strip(),
                        "type": "sentence"
                    })

    return statements


def find_duplicates(files: List[Path], threshold: float = 0.7) -> List[Dict[str, Any]]:
    """Find duplicate content across files."""
    duplicates = []
    file_statements = {}

    # Extract statements from each file
    for file_path in files:
        if file_path.exists():
            content = file_path.read_text()
            file_statements[str(file_path)] = extract_statements(content)

    # Compare statements between files
    file_paths = list(file_statements.keys())
    for i, file1 in enumerate(file_paths):
        for file2 in file_paths[i+1:]:
            for stmt1 in file_statements[file1]:
                tokens1 = tokenize(stmt1["text"])
                for stmt2 in file_statements[file2]:
                    tokens2 = tokenize(stmt2["text"])
                    similarity = jaccard_similarity(tokens1, tokens2)

                    if similarity >= threshold:
                        duplicates.append({
                            "file1": file1,
                            "statement1": stmt1["text"][:100],
                            "file2": file2,
                            "statement2": stmt2["text"][:100],
                            "similarity": round(similarity, 2)
                        })

    return duplicates


def find_conflicts(files: List[Path]) -> List[Dict[str, Any]]:
    """Find potentially conflicting statements."""
    conflicts = []

    # Patterns that might indicate conflicting statements
    contradiction_pairs = [
        (r'\bshould\b', r'\bshould not\b'),
        (r'\bmust\b', r'\bmust not\b'),
        (r'\balways\b', r'\bnever\b'),
        (r'\brecommended\b', r'\bnot recommended\b'),
        (r'\bbest practice\b', r'\banti-pattern\b'),
        (r'\bincrease\b', r'\bdecrease\b'),
        (r'\bfaster\b', r'\bslower\b'),
        (r'\bbetter\b', r'\bworse\b'),
    ]

    file_statements = {}
    for file_path in files:
        if file_path.exists():
            content = file_path.read_text()
            file_statements[str(file_path)] = extract_statements(content)

    # Look for contradictions
    file_paths = list(file_statements.keys())
    for i, file1 in enumerate(file_paths):
        for file2 in file_paths[i+1:]:
            for stmt1 in file_statements[file1]:
                text1 = stmt1["text"].lower()
                for stmt2 in file_statements[file2]:
                    text2 = stmt2["text"].lower()

                    # Check for contradiction patterns
                    for pattern1, pattern2 in contradiction_pairs:
                        if (re.search(pattern1, text1) and re.search(pattern2, text2)) or \
                           (re.search(pattern2, text1) and re.search(pattern1, text2)):
                            # Check if they're about the same topic
                            tokens1 = tokenize(text1)
                            tokens2 = tokenize(text2)
                            topic_overlap = jaccard_similarity(tokens1, tokens2)

                            if topic_overlap > 0.3:  # Same topic
                                conflicts.append({
                                    "file1": file1,
                                    "statement1": stmt1["text"][:100],
                                    "file2": file2,
                                    "statement2": stmt2["text"][:100],
                                    "topic_overlap": round(topic_overlap, 2),
                                    "type": "potential_contradiction"
                                })

    return conflicts


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Detect research conflicts")
    parser.add_argument("files", nargs="+", help="Research files to analyze")
    parser.add_argument("--mode", choices=["duplicates", "conflicts", "all"], default="all",
                        help="Detection mode")
    parser.add_argument("--threshold", type=float, default=0.7,
                        help="Similarity threshold for duplicates")
    args = parser.parse_args()

    files = [Path(f) for f in args.files]

    # Validate files exist
    missing = [f for f in files if not f.exists()]
    if missing:
        print(json.dumps({
            "success": False,
            "error": f"Files not found: {[str(f) for f in missing]}"
        }, indent=2))
        return 1

    result = {
        "operation": "detect_conflicts",
        "files_analyzed": len(files),
        "mode": args.mode
    }

    if args.mode in ["duplicates", "all"]:
        duplicates = find_duplicates(files, args.threshold)
        result["duplicates"] = {
            "count": len(duplicates),
            "items": duplicates[:20]  # Limit output
        }

    if args.mode in ["conflicts", "all"]:
        conflicts = find_conflicts(files)
        result["conflicts"] = {
            "count": len(conflicts),
            "items": conflicts[:20]  # Limit output
        }

    result["success"] = True

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
