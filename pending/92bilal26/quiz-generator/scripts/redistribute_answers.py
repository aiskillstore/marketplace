#!/usr/bin/env python3
"""
Quiz Answer Redistributor - Programmatic answer key normalization

This script reads a quiz .md file, parses the questions array, and redistributes
the correctOption indices to match one of 8 pre-made, non-biased sequences (A-H).

Usage:
    python redistribute_answers.py <quiz_file_path> <sequence_letter>

Example:
    python redistribute_answers.py chapter_02_quiz.md C
"""

import re
import sys
from pathlib import Path


# Pre-made distribution sequences (50 items each)
SEQUENCES = {
    'A': [2,0,3,1,2,0,1,3,2,0,1,3,0,2,1,3,2,0,1,3,0,2,3,1,0,2,3,1,2,0,3,1,2,0,1,3,0,2,3,1,2,0,3,1,0,2,1,3,0,2],
    'B': [1,3,0,2,1,3,0,2,3,1,0,2,3,1,2,0,1,3,2,0,3,1,2,0,1,3,0,2,1,3,2,0,3,1,0,2,3,1,2,0,1,3,0,2,1,0,3,2,1,3],
    'C': [3,2,1,0,3,2,1,0,2,3,0,1,3,2,0,1,2,3,1,0,3,2,0,1,2,3,1,0,3,2,1,0,2,3,0,1,3,2,1,0,2,3,0,1,3,2,0,1,3,2],
    'D': [0,3,2,1,0,3,2,1,3,0,2,1,0,3,1,2,0,3,2,1,0,3,1,2,3,0,1,2,0,3,2,1,3,0,1,2,0,3,1,2,3,0,2,1,0,3,1,2,3,0],
    'E': [1,2,3,0,1,2,3,0,2,1,3,0,1,2,0,3,1,2,3,0,1,2,0,3,2,1,3,0,1,2,3,0,2,1,0,3,1,2,3,0,2,1,0,3,2,1,3,0,1,2],
    'F': [2,3,0,1,2,3,0,1,3,2,1,0,2,3,0,1,3,2,0,1,2,3,1,0,3,2,1,0,2,3,0,1,3,2,1,0,2,3,1,0,3,2,0,1,2,3,1,0,3,2],
    'G': [0,1,2,3,0,1,2,3,1,0,3,2,0,1,3,2,0,1,2,3,1,0,2,3,0,1,3,2,1,0,2,3,0,1,2,3,1,0,3,2,1,0,2,3,1,0,3,2,0,1],
    'H': [3,0,1,2,3,0,1,2,0,3,2,1,3,0,2,1,3,0,1,2,3,0,2,1,0,3,2,1,3,0,1,2,0,3,1,2,3,0,2,1,0,3,1,2,3,0,2,1,3,0],
}


def extract_field(text, field_name):
    """
    Extract a field value from question object string.
    Handles escaped quotes and special characters safely.
    """
    pattern = field_name + ': "'
    start_idx = text.find(pattern)
    if start_idx < 0:
        return ""

    start_idx += len(pattern)
    value = ""
    i = start_idx

    while i < len(text):
        if text[i] == '"' and (i == 0 or text[i-1] != chr(92)):  # unescaped quote
            return value
        elif text[i] == chr(92):  # backslash
            value += text[i:i+2]
            i += 2
            continue
        else:
            value += text[i]
        i += 1

    return value


def parse_question(q_block):
    """Parse a single question object string into a dict."""
    q_text = extract_field(q_block, "question")

    # Extract options from options array
    opts_start = q_block.find('options: [')
    opts_end = q_block.find(']', opts_start)
    opts_raw = q_block[opts_start+len('options: ['):opts_end] if opts_start >= 0 else ""

    opts = []
    i = 0
    while i < len(opts_raw):
        if opts_raw[i] == '"':
            i += 1
            opt = ""
            while i < len(opts_raw):
                if opts_raw[i] == '"' and opts_raw[i-1] != chr(92):
                    opts.append(opt)
                    break
                elif opts_raw[i] == chr(92):
                    opt += opts_raw[i:i+2]
                    i += 2
                    continue
                else:
                    opt += opts_raw[i]
                i += 1
            i += 1
        else:
            i += 1

    # Extract correctOption
    corr_match = re.search(r'correctOption:\s*(\d+)', q_block)
    correct = int(corr_match.group(1)) if corr_match else 0

    exp_text = extract_field(q_block, "explanation")
    src_text = extract_field(q_block, "source")

    return {
        'question': q_text,
        'options': opts,
        'correctOption': correct,
        'explanation': exp_text,
        'source': src_text
    }


def redistribute_quiz(file_path, sequence_letter):
    """
    Main function: Read quiz file, parse questions, apply sequence, and write back.
    """
    if sequence_letter.upper() not in SEQUENCES:
        print(f"ERROR: Sequence '{sequence_letter}' not found. Available: A-H")
        return False

    sequence = SEQUENCES[sequence_letter.upper()]

    # Read file
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find questions array boundaries
    q_start = content.find('questions={[')
    q_end = content.find('  ]}', q_start)

    if q_start < 0 or q_end < 0:
        print("ERROR: Could not find questions array in file")
        return False

    # Extract array content
    array_content = content[q_start + len('questions={['):q_end]

    # Parse all question blocks
    questions_raw = []
    depth = 0
    current = ""

    for i, char in enumerate(array_content):
        if char == '{':
            depth += 1
            current += char
        elif char == '}':
            depth -= 1
            current += char
            if depth == 0 and current.strip():
                questions_raw.append(current.strip().rstrip(',').strip())
                current = ""
        elif depth > 0:
            current += char

    print(f"Extracted {len(questions_raw)} question blocks")

    # Parse each question
    parsed = [parse_question(q) for q in questions_raw]

    # Count original distribution
    orig_dist = {}
    for q in parsed:
        idx = q['correctOption']
        orig_dist[idx] = orig_dist.get(idx, 0) + 1

    print(f"Original distribution: {orig_dist}")

    # Apply sequence: swap options and update correctOption
    swaps = 0
    for i in range(len(parsed)):
        if i >= len(sequence):
            break

        curr_idx = parsed[i]['correctOption']
        targ_idx = sequence[i]

        if curr_idx != targ_idx and len(parsed[i]['options']) > max(curr_idx, targ_idx):
            # Swap option texts
            parsed[i]['options'][curr_idx], parsed[i]['options'][targ_idx] = \
                parsed[i]['options'][targ_idx], parsed[i]['options'][curr_idx]

            # Update correctOption index
            parsed[i]['correctOption'] = targ_idx
            swaps += 1

    print(f"Applied {swaps} swaps")

    # Count new distribution
    new_dist = {}
    for q in parsed:
        idx = q['correctOption']
        new_dist[idx] = new_dist.get(idx, 0) + 1

    print(f"New distribution: {new_dist}")

    # Rebuild the array
    new_array = ""
    for i, q in enumerate(parsed):
        new_array += "    {\n"
        new_array += f'      question: "{q["question"]}",\n'
        new_array += "      options: [\n"
        for j, opt in enumerate(q['options']):
            new_array += f'        "{opt}"'
            if j < len(q['options']) - 1:
                new_array += ","
            new_array += "\n"
        new_array += "      ],\n"
        new_array += f"      correctOption: {q['correctOption']},\n"
        new_array += f'      explanation: "{q["explanation"]}",\n'
        new_array += f'      source: "{q["source"]}"\n'
        new_array += "    }"
        if i < len(parsed) - 1:
            new_array += ","
        new_array += "\n"

    # Replace in file content
    new_content = content[:q_start + len('questions={[')] + new_array + content[q_end:]

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    # Verification
    print(f"\nVerification:")
    print(f"* Total Questions: {len(parsed)}")
    for idx in sorted(new_dist.keys()):
        print(f"* Index {idx}: {new_dist[idx]}")
    print(f"* Total: {sum(new_dist.values())}")

    print(f"\nSuccess! Applied Sequence {sequence_letter.upper()} to {file_path.name}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python redistribute_answers.py <quiz_file_path> <sequence_letter>")
        print("Example: python redistribute_answers.py chapter_02_quiz.md C")
        print("Available sequences: A, B, C, D, E, F, G, H")
        sys.exit(1)

    file_path = sys.argv[1]
    sequence_letter = sys.argv[2]

    success = redistribute_quiz(file_path, sequence_letter)
    sys.exit(0 if success else 1)
