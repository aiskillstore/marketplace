#!/usr/bin/env python3
"""Optional live model smoke test for Dittobot.

This script sends a small sample of regression cases to the OpenAI Responses
API and validates the model output with regression_100.py's deterministic
checks. It is intentionally opt-in: no API key, no network call, no failure.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from failure_taxonomy import unique_failure_buckets, unique_failure_codes
from regression_100 import Case, make_cases, validate, words


DEFAULT_MODEL = "gpt-5.2"
DEFAULT_API_URL = "https://api.openai.com/v1/responses"
PROMPT_MODES = ("any", "explicit_rewrite", "source_only")
HARD_HTTP_ERRORS = {400, 401, 403, 404}


@dataclasses.dataclass(frozen=True)
class ApiResult:
    text: str
    usage: dict


def redact_secrets(text: str) -> str:
    return re.sub(r"sk-[A-Za-z0-9_*.-]+", "sk-...REDACTED", text)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def output_text(response: dict) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"].strip()

    parts: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and "text" in content:
                parts.append(content["text"])
    return "\n".join(parts).strip()


def usage_value(usage: dict, key: str) -> int:
    value = usage.get(key)
    return value if isinstance(value, int) else 0


def open_private_jsonl(path: str):
    target = Path(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    fd = os.open(target, flags, 0o600)
    os.chmod(target, 0o600)
    return os.fdopen(fd, "a", encoding="utf-8")


def write_record(save_file, record: dict[str, Any]) -> None:
    if save_file:
        save_file.write(json.dumps(record, ensure_ascii=False) + "\n")


def user_prompt(case: Case) -> str:
    if case.prompt_mode == "source_only":
        return case.source

    lines = [
        "Use Dittobot to revise this source text.",
        f"Case: {case.id}",
        "Return only the rewritten text unless a note is explicitly allowed.",
        "",
        "Requirements:",
    ]
    if case.must:
        lines.append(f"- Preserve these required terms or ideas: {', '.join(case.must)}")
    if case.protected:
        lines.append(f"- Do not change these protected facts: {', '.join(case.protected)}")
    if case.forbid:
        lines.append(f"- Avoid these forbidden terms: {', '.join(case.forbid)}")
    if case.preserve_voice:
        lines.append(f"- Preserve these voice markers: {', '.join(case.preserve_voice)}")
    if case.exact_words is not None:
        lines.append(f"- Use exactly {case.exact_words} words.")
    if case.no_dash:
        lines.append("- Use no dashes of any kind.")
    if not case.allow_note:
        lines.append("- Do not include notes, preambles, or rationale.")

    lines.extend(["", "Source:", case.source])
    return "\n".join(lines)


def case_family(case_id: str) -> str:
    return re.sub(r"_\d+$", "", case_id)


def call_responses_api(
    *,
    api_key: str,
    api_url: str,
    model: str,
    skill_text: str,
    prompt: str,
    timeout: int,
    max_output_tokens: int,
) -> ApiResult:
    payload = {
        "model": model,
        "max_output_tokens": max_output_tokens,
        "input": [
            {"role": "developer", "content": skill_text},
            {"role": "user", "content": prompt},
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        api_url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    text = output_text(body)
    if not text:
        raise RuntimeError(f"Response did not include output text: {body}")
    usage = body.get("usage")
    return ApiResult(text=text, usage=usage if isinstance(usage, dict) else {})


def selected_cases(
    case_ids: list[str],
    limit: int,
    prompt_mode: str,
    ensure_source_only: int = 0,
) -> list[Case]:
    cases = make_cases()
    if case_ids:
        by_id = {case.id: case for case in cases}
        missing = [case_id for case_id in case_ids if case_id not in by_id]
        if missing:
            raise SystemExit(f"Unknown case id(s): {', '.join(missing)}")
        cases = [by_id[case_id] for case_id in case_ids]

    if prompt_mode != "any":
        cases = [case for case in cases if case.prompt_mode == prompt_mode]
        if not cases:
            raise SystemExit(f"No selected cases match --prompt-mode {prompt_mode}.")

    if case_ids:
        return cases
    return representative_cases(cases, limit, ensure_source_only if prompt_mode == "any" else 0)


def representative_cases(cases: list[Case], limit: int, ensure_source_only: int = 0) -> list[Case]:
    """Pick a spread across the grouped deterministic suite."""
    if limit <= 0:
        raise SystemExit("--limit must be greater than 0.")
    if limit >= len(cases):
        return cases
    step = len(cases) / limit
    selected = [cases[int(index * step)] for index in range(limit)]
    if ensure_source_only <= 0:
        return selected

    source_only = [case for case in cases if case.prompt_mode == "source_only"]
    wanted = min(ensure_source_only, limit, len(source_only))
    if wanted == 0:
        return selected
    present = {case.id for case in selected if case.prompt_mode == "source_only"}
    additions = [case for case in source_only if case.id not in present][: max(0, wanted - len(present))]
    if not additions:
        return selected

    selected_ids = {case.id for case in selected}
    replaceable = [
        index for index, case in enumerate(selected) if case.prompt_mode != "source_only"
    ]
    for case in additions:
        if case.id in selected_ids:
            continue
        if replaceable:
            index = replaceable.pop()
            selected_ids.discard(selected[index].id)
            selected[index] = case
        else:
            selected.append(case)
        selected_ids.add(case.id)
    order = {case.id: index for index, case in enumerate(cases)}
    return sorted(selected[:limit], key=lambda case: order[case.id])


def print_case_list(cases: list[Case]) -> None:
    for case in cases:
        print(
            f"{case.id}\t{case_family(case.id)}\t{case.prompt_mode}\t"
            f"source_words={len(words(case.source))}\trewrite_words={len(words(case.rewrite))}"
        )


def print_prompts(cases: list[Case]) -> None:
    for index, case in enumerate(cases, 1):
        if index > 1:
            print("\n" + "=" * 72 + "\n")
        print(f"# {case.id} ({case.prompt_mode})")
        print(user_prompt(case))


def case_by_id() -> dict[str, Case]:
    return {case.id: case for case in make_cases()}


def validate_api_url(api_url: str, allow_custom: bool) -> None:
    if api_url == DEFAULT_API_URL:
        return
    parsed = urlparse(api_url)
    if parsed.scheme != "https":
        raise SystemExit("Custom API URLs must use https.")
    if not allow_custom:
        raise SystemExit(
            "Refusing to send OPENAI_API_KEY to a custom API URL. "
            "Pass --allow-custom-api-url if you trust this endpoint."
        )


def validate_save_path(path: str | None) -> None:
    if not path:
        return
    if not path.endswith(".local.jsonl"):
        raise SystemExit("--save-jsonl path must end with .local.jsonl so git ignores it.")


def should_stop(failures: list[tuple[str, list[str]]], fail_fast: bool, max_failures: int | None) -> bool:
    if fail_fast and failures:
        return True
    return max_failures is not None and len(failures) >= max_failures


def truncated(text: str, limit: int = 600) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def result_record(
    *,
    case: Case,
    model: str,
    skill_sha256: str,
    prompt_sha256: str | None,
    source_sha256: str,
    output: str,
    usage: dict,
    errors: list[str],
) -> dict[str, Any]:
    return {
        "case": case.id,
        "family": case_family(case.id),
        "prompt_mode": case.prompt_mode,
        "model": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "skill_sha256": skill_sha256,
        "source_sha256": source_sha256,
        "prompt_sha256": prompt_sha256,
        "output_sha256": sha256_text(output),
        "output_words": len(words(output)),
        "usage": usage,
        "failure_codes": unique_failure_codes(errors),
        "failure_buckets": unique_failure_buckets(errors),
        "errors": errors,
    }


def api_error_record(
    *,
    case: Case,
    model: str,
    skill_sha256: str,
    prompt_sha256: str,
    source_sha256: str,
    errors: list[str],
    api_error_code: int | None = None,
) -> dict[str, Any]:
    record = {
        "case": case.id,
        "family": case_family(case.id),
        "prompt_mode": case.prompt_mode,
        "model": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "skill_sha256": skill_sha256,
        "source_sha256": source_sha256,
        "prompt_sha256": prompt_sha256,
        "failure_codes": unique_failure_codes(errors),
        "failure_buckets": unique_failure_buckets(errors),
        "errors": errors,
    }
    if api_error_code is not None:
        record["api_error_code"] = api_error_code
    return record


def replay_records(path: str, model: str, save_jsonl: str | None) -> int:
    transcript = Path(path)
    if not transcript.exists():
        raise SystemExit(f"Replay transcript not found: {transcript}")
    records = []
    for line_number, line in enumerate(transcript.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(record, dict):
            raise SystemExit(f"{path}:{line_number}: expected object record")
        records.append(record)

    by_id = case_by_id()
    repo = Path(__file__).resolve().parents[1]
    skill_sha256 = sha256_text((repo / "SKILL.md").read_text(encoding="utf-8"))
    save_file = open_private_jsonl(save_jsonl) if save_jsonl else None
    failures: list[tuple[str, list[str]]] = []
    attempted = 0
    passed = 0
    try:
        for index, record in enumerate(records, 1):
            case_id = str(record.get("case", ""))
            if case_id not in by_id:
                raise SystemExit(f"{path}:{index}: unknown case id {case_id!r}")
            output = record.get("output")
            record_errors = record.get("errors")
            if not isinstance(record_errors, list):
                record_errors = []
            if not isinstance(output, str) and record_errors:
                case = by_id[case_id]
                errors = [str(error) for error in record_errors]
                attempted += 1
                print(f"{case.id}: FAIL | replay record has no output")
                for error in errors:
                    print(f"  - {error}")
                write_record(
                    save_file,
                    api_error_record(
                        case=case,
                        model=str(record.get("model") or model),
                        skill_sha256=str(record.get("skill_sha256") or skill_sha256),
                        prompt_sha256=record.get("prompt_sha256")
                        if isinstance(record.get("prompt_sha256"), str)
                        else "",
                        source_sha256=str(record.get("source_sha256") or sha256_text(case.source)),
                        errors=errors,
                        api_error_code=record.get("api_error_code")
                        if isinstance(record.get("api_error_code"), int)
                        else None,
                    ),
                )
                failures.append((case.id, errors))
                continue
            if not isinstance(output, str):
                raise SystemExit(
                    f"{path}:{index}: replay records must include raw string output"
                )
            case = by_id[case_id]
            attempted += 1
            errors = validate(dataclasses.replace(case, rewrite=output))
            status = "PASS" if not errors else "FAIL"
            print(f"{case.id}: {status} | replay words={len(words(output))}")
            for error in errors:
                print(f"  - {error}")
            replay_record = result_record(
                case=case,
                model=str(record.get("model") or model),
                skill_sha256=str(record.get("skill_sha256") or skill_sha256),
                prompt_sha256=record.get("prompt_sha256")
                if isinstance(record.get("prompt_sha256"), str)
                else None,
                source_sha256=str(record.get("source_sha256") or sha256_text(case.source)),
                output=output,
                usage=record.get("usage") if isinstance(record.get("usage"), dict) else {},
                errors=errors,
            )
            if isinstance(record.get("timestamp"), str):
                replay_record["replayed_from_timestamp"] = record["timestamp"]
            write_record(save_file, replay_record)
            if errors:
                failures.append((case.id, errors))
            else:
                passed += 1
    finally:
        if save_file:
            save_file.close()

    print(f"\nREPLAY TOTAL: {passed}/{attempted} passed")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=10, help="Number of cases to run.")
    parser.add_argument("--case", action="append", default=[], help="Specific case id to run.")
    parser.add_argument(
        "--prompt-mode",
        choices=PROMPT_MODES,
        default="any",
        help="Filter cases by prompt style.",
    )
    parser.add_argument(
        "--ensure-source-only",
        type=int,
        default=1,
        help="When sampling all prompt modes, include at least this many source-only cases.",
    )
    parser.add_argument(
        "--list-cases",
        action="store_true",
        help="List matching case ids without calling the API.",
    )
    parser.add_argument(
        "--print-prompts",
        action="store_true",
        help="Print selected prompts without calling the API.",
    )
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--api-url", default=os.environ.get("OPENAI_API_URL", DEFAULT_API_URL))
    parser.add_argument(
        "--allow-custom-api-url",
        action="store_true",
        help="Allow sending the bearer token to --api-url / OPENAI_API_URL.",
    )
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--max-output-tokens", type=int, default=500)
    parser.add_argument(
        "--max-total-tokens",
        type=int,
        help="Stop before the next case once reported API usage reaches this total.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop after the first API or validation failure.",
    )
    parser.add_argument(
        "--max-failures",
        type=int,
        help="Stop after this many failures.",
    )
    parser.add_argument(
        "--show-output-on-fail",
        action="store_true",
        help="Print a truncated model output when deterministic validation fails.",
    )
    parser.add_argument("--save-jsonl", help="Optional local transcript path. Do not commit it.")
    parser.add_argument(
        "--replay-jsonl",
        help="Validate raw outputs from a saved .local.jsonl transcript without API calls.",
    )
    parser.add_argument(
        "--no-save-source",
        action="store_true",
        help="Deprecated; raw source is omitted by default.",
    )
    parser.add_argument(
        "--save-raw-source",
        action="store_true",
        help="When saving JSONL, include raw source text. Prefer redacted fixtures.",
    )
    parser.add_argument(
        "--save-raw-output",
        action="store_true",
        help="When saving JSONL, include raw model output. It may contain source text.",
    )
    parser.add_argument(
        "--require-key",
        action="store_true",
        help="Exit nonzero instead of skipping when OPENAI_API_KEY is missing.",
    )
    args = parser.parse_args()

    validate_save_path(args.save_jsonl)
    validate_save_path(args.replay_jsonl)
    if args.max_failures is not None and args.max_failures <= 0:
        raise SystemExit("--max-failures must be greater than 0.")
    if args.ensure_source_only < 0:
        raise SystemExit("--ensure-source-only cannot be negative.")
    if args.max_total_tokens is not None and args.max_total_tokens <= 0:
        raise SystemExit("--max-total-tokens must be greater than 0.")
    if args.no_save_source and args.save_raw_source:
        raise SystemExit("--no-save-source conflicts with --save-raw-source.")
    if args.replay_jsonl and (args.list_cases or args.print_prompts):
        raise SystemExit("--replay-jsonl cannot be combined with --list-cases or --print-prompts.")

    if args.replay_jsonl:
        return replay_records(args.replay_jsonl, args.model, args.save_jsonl)

    if args.list_cases:
        print_case_list(
            selected_cases(args.case, len(make_cases()), args.prompt_mode, args.ensure_source_only)
        )
        return 0

    if args.print_prompts:
        print_prompts(
            selected_cases(args.case, args.limit, args.prompt_mode, args.ensure_source_only)
        )
        return 0

    validate_api_url(args.api_url, args.allow_custom_api_url)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("SKIP: OPENAI_API_KEY is not set; live eval is optional.")
        return 1 if args.require_key else 0

    repo = Path(__file__).resolve().parents[1]
    skill_text = (repo / "SKILL.md").read_text(encoding="utf-8")
    skill_sha256 = sha256_text(skill_text)
    cases = selected_cases(args.case, args.limit, args.prompt_mode, args.ensure_source_only)

    save_file = None
    if args.save_jsonl:
        save_file = open_private_jsonl(args.save_jsonl)

    failures: list[tuple[str, list[str]]] = []
    attempted = 0
    passed = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0
    aborted = False
    try:
        for case in cases:
            if args.max_total_tokens is not None and total_tokens >= args.max_total_tokens:
                print("Stopping: token budget reached.")
                break
            prompt = user_prompt(case)
            attempted += 1
            try:
                result = call_responses_api(
                    api_key=api_key,
                    api_url=args.api_url,
                    model=args.model,
                    skill_text=skill_text,
                    prompt=prompt,
                    timeout=args.timeout,
                    max_output_tokens=args.max_output_tokens,
                )
                text = result.text
                input_tokens = usage_value(result.usage, "input_tokens")
                output_tokens = usage_value(result.usage, "output_tokens")
                case_total_tokens = usage_value(result.usage, "total_tokens")
                total_input_tokens += input_tokens
                total_output_tokens += output_tokens
                total_tokens += case_total_tokens or input_tokens + output_tokens
            except urllib.error.HTTPError as exc:
                detail = redact_secrets(exc.read().decode("utf-8", errors="replace"))
                message = f"HTTP {exc.code}: {detail or exc.reason}"
                errors = [f"API error: {message}"]
                failures.append((case.id, errors))
                print(f"{case.id}: FAIL | API error: {message}")
                write_record(
                    save_file,
                    api_error_record(
                        case=case,
                        model=args.model,
                        skill_sha256=skill_sha256,
                        prompt_sha256=sha256_text(prompt),
                        source_sha256=sha256_text(case.source),
                        errors=errors,
                        api_error_code=exc.code,
                    ),
                )
                if exc.code in HARD_HTTP_ERRORS:
                    print("Stopping: hard API setup error.")
                    aborted = True
                    break
                if should_stop(failures, args.fail_fast, args.max_failures):
                    print("Stopping: failure limit reached.")
                    break
                continue
            except (urllib.error.URLError, RuntimeError) as exc:
                errors = [f"API error: {exc}"]
                failures.append((case.id, errors))
                print(f"{case.id}: FAIL | API error: {exc}")
                write_record(
                    save_file,
                    api_error_record(
                        case=case,
                        model=args.model,
                        skill_sha256=skill_sha256,
                        prompt_sha256=sha256_text(prompt),
                        source_sha256=sha256_text(case.source),
                        errors=errors,
                    ),
                )
                if should_stop(failures, args.fail_fast, args.max_failures):
                    print("Stopping: failure limit reached.")
                    break
                continue

            live_case = dataclasses.replace(case, rewrite=text)
            errors = validate(live_case)
            status = "PASS" if not errors else "FAIL"
            print(f"{case.id}: {status} | live words={len(words(text))}")
            for error in errors:
                print(f"  - {error}")
            if errors and args.show_output_on_fail:
                print("  output:")
                for line in truncated(text).splitlines():
                    print(f"    {line}")
            if save_file:
                record = result_record(
                    case=case,
                    model=args.model,
                    skill_sha256=skill_sha256,
                    prompt_sha256=sha256_text(prompt),
                    source_sha256=sha256_text(case.source),
                    output=text,
                    usage=result.usage,
                    errors=errors,
                )
                if args.save_raw_source:
                    record["source"] = case.source
                if args.save_raw_output:
                    record["output"] = text
                write_record(save_file, record)
            if errors:
                failures.append((case.id, errors))
                if should_stop(failures, args.fail_fast, args.max_failures):
                    print("Stopping: failure limit reached.")
                    break
            else:
                passed += 1
    finally:
        if save_file:
            save_file.close()

    not_run = len(cases) - attempted
    print(f"\nLIVE TOTAL: {passed}/{attempted} attempted passed")
    if not_run:
        print(f"NOT RUN: {not_run}/{len(cases)} selected")
    if total_tokens:
        print(
            "USAGE: "
            f"input={total_input_tokens} output={total_output_tokens} total={total_tokens}"
        )
    return 1 if failures or aborted else 0


if __name__ == "__main__":
    sys.exit(main())
