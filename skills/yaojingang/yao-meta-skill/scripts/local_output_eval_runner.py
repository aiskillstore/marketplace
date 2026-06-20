#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Any


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, round(len(text) / 4))


def build_response(request: dict[str, Any], execution_kind: str, provider: str, model: str) -> dict[str, Any]:
    output = str(request.get("fixture_output", ""))
    prompt = str(request.get("prompt", ""))
    input_tokens = estimate_tokens(prompt)
    output_tokens = estimate_tokens(output)
    response: dict[str, Any] = {
        "output": output,
        "execution_kind": execution_kind,
        "provider": provider,
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "estimated": True,
        },
    }
    if model:
        response["model"] = model
    return response


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Local deterministic output-eval runner. It executes the runner contract "
            "without claiming provider-backed model generation."
        )
    )
    parser.add_argument("--execution-kind", choices=["command", "model"], default="command")
    parser.add_argument("--provider", default="local-output-eval-runner")
    parser.add_argument("--model", default="")
    args = parser.parse_args()

    raw = sys.stdin.read()
    if not raw.strip():
        print("runner requires a JSON request on stdin", file=sys.stderr)
        raise SystemExit(2)
    try:
        request = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"invalid JSON request: {exc}", file=sys.stderr)
        raise SystemExit(2)
    if not isinstance(request, dict):
        print("runner request must be a JSON object", file=sys.stderr)
        raise SystemExit(2)

    response = build_response(request, args.execution_kind, args.provider, args.model)
    print(json.dumps(response, ensure_ascii=False))


if __name__ == "__main__":
    main()
