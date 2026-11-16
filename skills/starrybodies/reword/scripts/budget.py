#!/usr/bin/env python3
"""Measure and bound editing guidance locally, without model or network calls."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
import json
from pathlib import Path
import sys

DEFAULT_GUIDANCE_CHARS = 4000
DEFAULT_GUIDANCE_TOKENS = 1000
DEFAULT_EXAMPLE_CHARS = 900
DEFAULT_MAX_EXAMPLES = 2
SEPARATOR = "\n\n"


class GuidanceBudgetError(ValueError):
    """Required material does not fit; the caller must not silently remove it."""

    def __init__(self, message: str, measurement: dict):
        super().__init__(message)
        self.measurement = measurement


def _nonnegative_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer.")


def _parts(values: Sequence[str], name: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise ValueError(f"{name} must be a sequence of strings.")
    result = tuple(values)
    if any(not isinstance(value, str) for value in result):
        raise ValueError(f"{name} must contain only strings.")
    return result


def measure_guidance(
    text: str,
    encoding: str = "o200k_base",
    *,
    token_counter: Callable[[str], int] | None = None,
) -> dict:
    """Count this exact text; accept an exact local tokenizer only when supplied.

    The default byte/4 heuristic is explicitly an estimate, not a token bound.
    ``encoding`` labels the intended encoding; it is not a model identifier.
    An exact counter must tokenize all text, including special-token-looking text.
    """
    if not isinstance(text, str):
        raise ValueError("text must be a string.")
    if not isinstance(encoding, str) or not encoding.strip():
        raise ValueError("encoding must be a nonempty string.")
    byte_count = len(text.encode("utf-8"))
    report = {
        "characters": len(text),
        "utf8_bytes": byte_count,
        "encoding": encoding,
        "scope": "provided_text_only",
        "tokens": None,
        "estimated_tokens": None,
        "token_measurement": "estimate",
    }
    if token_counter is None:
        report["estimated_tokens"] = (byte_count + 3) // 4
        report["estimation_method"] = "ceil(utf8_bytes / 4); heuristic, not a bound"
    else:
        if not callable(token_counter):
            raise ValueError("token_counter must be callable.")
        count = token_counter(text)
        _nonnegative_int(count, "token count")
        report["tokens"] = count
        report["token_measurement"] = "exact"
    return report


def fit_examples(
    examples: Sequence[str],
    *,
    remaining_chars: int,
    max_examples: int = DEFAULT_MAX_EXAMPLES,
    max_chars: int = DEFAULT_EXAMPLE_CHARS,
    separator: str = SEPARATOR,
) -> list[str]:
    """Keep whole optional examples in priority order; never truncate an example.

    Count internal separators. The caller reserves any separator before examples.
    Skip an example that cannot fit, allowing a later, smaller example to fit.
    """
    examples = _parts(examples, "examples")
    for value, name in ((remaining_chars, "remaining_chars"),
                        (max_examples, "max_examples"), (max_chars, "max_chars")):
        _nonnegative_int(value, name)
    if not isinstance(separator, str):
        raise ValueError("separator must be a string.")
    allowance = min(remaining_chars, max_chars)
    selected: list[str] = []
    used = 0
    for example in examples:
        if len(selected) >= max_examples:
            break
        if not example:
            continue
        size = len(example) + (len(separator) if selected else 0)
        if used + size <= allowance:
            selected.append(example)
            used += size
    return selected


def assemble_guidance(
    required_parts: Sequence[str],
    examples: Sequence[str] = (),
    *,
    max_chars: int = DEFAULT_GUIDANCE_CHARS,
    target_tokens: int | None = DEFAULT_GUIDANCE_TOKENS,
    max_examples: int = DEFAULT_MAX_EXAMPLES,
    max_example_chars: int = DEFAULT_EXAMPLE_CHARS,
    separator: str = SEPARATOR,
    encoding: str = "o200k_base",
    token_counter: Callable[[str], int] | None = None,
) -> dict:
    """Keep required text verbatim and remove optional examples before overflow.

    Required parts include the kernel, destination, explicit author preferences,
    and any locks placed in guidance. Source/data should be carried separately;
    if supplied as required text, it is also kept verbatim or rejected intact.
    The token target is enforced only with an exact counter. The character cap
    is always enforced, including every separator.
    """
    required_parts = _parts(required_parts, "required_parts")
    examples = _parts(examples, "examples")
    _nonnegative_int(max_chars, "max_chars")
    if target_tokens is not None:
        _nonnegative_int(target_tokens, "target_tokens")
    if not isinstance(separator, str):
        raise ValueError("separator must be a string.")
    required = separator.join(required_parts)
    measurement = measure_guidance(required, encoding, token_counter=token_counter)
    required_measurement = measurement
    if measurement["characters"] > max_chars:
        raise GuidanceBudgetError(
            f"Required guidance exceeds the {max_chars}-character budget; nothing was removed.",
            measurement,
        )
    if token_counter is not None and target_tokens is not None and measurement["tokens"] > target_tokens:
        raise GuidanceBudgetError(
            f"Required guidance exceeds the {target_tokens}-token budget; nothing was removed.",
            measurement,
        )
    prefix = separator if required else ""
    selected = fit_examples(
        examples,
        remaining_chars=max(0, max_chars - len(required) - len(prefix)),
        max_examples=max_examples,
        max_chars=max_example_chars,
        separator=separator,
    )
    while True:
        text = required + (prefix + separator.join(selected) if selected else "")
        measurement = (measure_guidance(text, encoding, token_counter=token_counter)
                       if selected else required_measurement)
        if token_counter is None or target_tokens is None or measurement["tokens"] <= target_tokens:
            break
        selected.pop()
    return {
        "text": text,
        "measurement": measurement,
        "examples_used": len(selected),
        "examples_omitted": len(examples) - len(selected),
        "limits": {
            "characters": max_chars,
            "target_tokens": target_tokens,
            "token_target_enforced": token_counter is not None and target_tokens is not None,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", default="-", help="UTF-8 guidance file, or - for stdin")
    parser.add_argument("--encoding", default="o200k_base", help="label the intended token encoding")
    parser.add_argument("--max-chars", type=int, default=DEFAULT_GUIDANCE_CHARS)
    args = parser.parse_args(argv)
    try:
        _nonnegative_int(args.max_chars, "max_chars")
        if args.file == "-":
            text = sys.stdin.read()
        else:
            with Path(args.file).open(encoding="utf-8", newline="") as stream:
                text = stream.read()
        report = measure_guidance(text, args.encoding)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    report["character_budget"] = args.max_chars
    report["within_character_budget"] = report["characters"] <= args.max_chars
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["within_character_budget"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
