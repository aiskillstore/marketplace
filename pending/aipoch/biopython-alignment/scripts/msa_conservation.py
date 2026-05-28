from __future__ import annotations

import json
from io import StringIO
from typing import Dict, List

from Bio import AlignIO

CONFIG_PATH = "config/task_config.json"


def load_config(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def compute_conservation(fasta_text: str, gap_chars: List[str]) -> Dict:
    alignment = AlignIO.read(StringIO(fasta_text), "fasta")
    alignment_length = alignment.get_alignment_length()
    sequence_count = len(alignment)

    columns = []
    for idx in range(alignment_length):
        column = alignment[:, idx]
        counts: Dict[str, int] = {}
        non_gap = 0
        for char in column:
            if char in gap_chars:
                continue
            non_gap += 1
            counts[char] = counts.get(char, 0) + 1

        if non_gap == 0:
            consensus = "-"
            conservation = 0.0
        else:
            consensus = max(counts.items(), key=lambda item: (item[1], item[0]))[0]
            conservation = counts[consensus] / non_gap

        columns.append(
            {
                "index": idx + 1,
                "consensus": consensus,
                "conservation": round(conservation, 4),
                "non_gap": non_gap,
                "counts": counts,
            }
        )

    return {
        "sequence_count": sequence_count,
        "alignment_length": alignment_length,
        "columns": columns,
    }


def main() -> None:
    config = load_config(CONFIG_PATH)
    fasta_text = config["fasta_text"]
    gap_chars = config.get("gap_chars", ["-", "."])
    min_conservation = float(config.get("min_conservation", 1.0))
    output_path = config.get("output_path", "config/msa_conservation.json")

    result = compute_conservation(fasta_text, gap_chars)
    conserved_positions = [
        col["index"]
        for col in result["columns"]
        if col["conservation"] >= min_conservation
    ]

    result["min_conservation"] = min_conservation
    result["conserved_positions"] = conserved_positions

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    print("MSA conservative statistics completed")
    print(f"Number of sequences: {result['sequence_count']}")
    print(f"Alignment length: {result['alignment_length']}")
    print(f"conservative threshold: {min_conservation}")
    print(f"Number of conserved sites: {len(conserved_positions)}")
    print(f"English(1-based): {conserved_positions}")
    print(f"The result has been written: {output_path}")


if __name__ == "__main__":
    main()
