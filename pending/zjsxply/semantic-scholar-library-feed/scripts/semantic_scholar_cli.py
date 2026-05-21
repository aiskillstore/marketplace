#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from ss_store import (
    DEFAULT_COOKIE_PATH,
    DEFAULT_USER_AGENT,
    GRAPH_API_ORIGIN,
    SEMANTIC_SCHOLAR_ORIGIN,
    build_cookie_bundle,
    count_papers,
    decode_ssr_data_from_html,
    fetch_html,
    fetch_json,
    find_snapshot,
    list_snapshot_names,
    load_cookie_bundle,
    mask_secret,
    missing_required_cookies,
    parse_cookie_header,
    parse_folder_ids,
    parse_window_utc,
    save_cookie_bundle,
)


def write_json(path: str | Path, payload: Any) -> Path:
    output = Path(path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return output


def load_bundle(cookie_path: str | Path | None) -> dict[str, Any]:
    try:
        return load_cookie_bundle(cookie_path)
    except FileNotFoundError as exc:
        raise SystemExit(
            f"{exc}. Import cookies with `import-curl` or `import-header` first."
        ) from exc
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def split_csv(values: list[str] | None) -> list[str]:
    results: list[str] = []
    for value in values or []:
        for item in value.split(","):
            normalized = item.strip()
            if normalized:
                results.append(normalized)
    return results


def require_cookie_health(bundle: dict[str, Any], *, allow_partial: bool) -> None:
    missing = missing_required_cookies(bundle)
    if missing and not allow_partial:
        raise SystemExit(
            "Missing required cookies: "
            + ", ".join(missing)
            + ". Refresh the Cookie Store or import cookies from a browser curl/header."
        )


def persist_imported_cookie_header(
    raw_header: str,
    *,
    source: str,
    user_agent: str,
    note: str,
    cookie_path: str | Path | None,
    allow_partial: bool,
    extra_fields: dict[str, Any] | None = None,
) -> None:
    cookies = parse_cookie_header(raw_header)
    bundle = build_cookie_bundle(
        cookies,
        source=source,
        user_agent=user_agent,
        note=note,
    )
    bundle["cookieHeader"] = raw_header
    if extra_fields:
        bundle.update(extra_fields)
    require_cookie_health(bundle, allow_partial=allow_partial)
    saved_cookie_path, header_path = save_cookie_bundle(bundle, cookie_path)
    print(f"Saved cookies to {saved_cookie_path}")
    print(f"Saved Cookie header to {header_path}")
    print(f"Cookie names: {', '.join(bundle['cookieNames'])}")


def extract_recommendation_bootstrap(decoded_data: Any) -> dict[str, Any]:
    snapshot = find_snapshot(decoded_data, "GET_LIBRARY_FOLDERS_RECOMMENDATIONS")
    if snapshot is None:
        raise RuntimeError("Could not find GET_LIBRARY_FOLDERS_RECOMMENDATIONS in SSR data.")
    result_data = snapshot.get("resultData") or {}
    if not isinstance(result_data, dict):
        raise RuntimeError("Recommendation snapshot does not contain a JSON object resultData.")
    path = str(snapshot.get("path", ""))
    return {
        "path": path,
        "folderIds": parse_folder_ids(path),
        "windowUTC": parse_window_utc(path),
        "nextWindowUTC": result_data.get("nextWindowUTC"),
        "days": result_data.get("days") or [],
    }


def build_feed_url(folder_ids: list[str], window_utc: str) -> str:
    query = urlencode(
        [*[( "folderIds", folder_id) for folder_id in folder_ids], ("windowUTC", str(window_utc))],
        doseq=True,
    )
    return f"{SEMANTIC_SCHOLAR_ORIGIN}/api/1/library/folders/recommendations?{query}"


def summarize_crawl(windows: list[dict[str, Any]]) -> dict[str, Any]:
    unique_ids: set[str] = set()
    unique_titles: set[str] = set()
    total_papers = 0
    for window in windows:
        for day in window.get("days", []):
            for paper_wrapper in day.get("papers", []):
                paper = paper_wrapper.get("paper") or {}
                paper_id = str(paper.get("id", "")).strip()
                title_obj = paper.get("title") or {}
                title = str(title_obj.get("text", "")).strip()
                if paper_id:
                    unique_ids.add(paper_id)
                if title:
                    unique_titles.add(title)
                total_papers += 1
    return {
        "windowCount": len(windows),
        "paperCount": total_papers,
        "uniquePaperIds": len(unique_ids),
        "uniqueTitles": len(unique_titles),
    }


def cmd_import_header(args: argparse.Namespace) -> None:
    if bool(args.header) == bool(args.header_file):
        raise SystemExit("Provide exactly one of --header or --header-file.")
    if args.header:
        raw_header = args.header.strip()
    else:
        raw_header = Path(args.header_file).expanduser().read_text().strip()
    if not raw_header:
        raise SystemExit("Cookie header is empty.")
    persist_imported_cookie_header(
        raw_header,
        source="manual-cookie-header",
        user_agent=args.user_agent,
        note="Imported from raw Cookie header.",
        cookie_path=args.cookie_path,
        allow_partial=args.allow_partial,
    )


def extract_cookie_artifacts_from_curl(curl_command: str) -> dict[str, str]:
    normalized = curl_command.replace("\\\r\n", " ").replace("\\\n", " ").strip()
    if not normalized:
        raise SystemExit("curl command is empty.")
    try:
        tokens = shlex.split(normalized, posix=True)
    except ValueError as exc:
        raise SystemExit(f"Could not parse curl command: {exc}") from exc

    cookie_header = ""
    user_agent = ""
    referer = ""
    url = ""
    i = 0
    while i < len(tokens):
        token = tokens[i]
        next_token = tokens[i + 1] if i + 1 < len(tokens) else ""
        lower_token = token.lower()

        if token in {"-b", "--cookie"} and next_token:
            cookie_header = next_token.strip()
            i += 2
            continue
        if token in {"-A", "--user-agent"} and next_token:
            user_agent = next_token.strip()
            i += 2
            continue
        if token in {"-H", "--header"} and next_token:
            header = next_token.strip()
            lower_header = header.lower()
            if lower_header.startswith("cookie:"):
                cookie_header = header.split(":", 1)[1].strip()
            elif lower_header.startswith("user-agent:"):
                user_agent = header.split(":", 1)[1].strip()
            elif lower_header.startswith("referer:"):
                referer = header.split(":", 1)[1].strip()
            i += 2
            continue
        if lower_token.startswith("http://") or lower_token.startswith("https://"):
            url = token
        i += 1

    if not cookie_header:
        raise SystemExit("Could not find a Cookie header or -b/--cookie value in the curl command.")

    return {
        "cookieHeader": cookie_header,
        "userAgent": user_agent,
        "referer": referer,
        "url": url,
    }


def cmd_import_curl(args: argparse.Namespace) -> None:
    if bool(args.curl) == bool(args.curl_file):
        raise SystemExit("Provide exactly one of --curl or --curl-file.")
    if args.curl:
        raw_curl = args.curl
    else:
        raw_curl = Path(args.curl_file).expanduser().read_text()

    artifacts = extract_cookie_artifacts_from_curl(raw_curl)
    raw_header = artifacts["cookieHeader"]
    effective_user_agent = args.user_agent or artifacts["userAgent"] or DEFAULT_USER_AGENT
    extra_fields: dict[str, Any] = {}
    if artifacts["referer"]:
        extra_fields["referer"] = artifacts["referer"]
    if artifacts["url"]:
        extra_fields["sourceUrl"] = artifacts["url"]
    persist_imported_cookie_header(
        raw_header,
        source="browser-curl",
        user_agent=effective_user_agent,
        note=(
            "Imported from a browser-copied curl command."
            + (f" URL: {artifacts['url']}" if artifacts["url"] else "")
        ),
        cookie_path=args.cookie_path,
        allow_partial=args.allow_partial,
        extra_fields=extra_fields,
    )


def cmd_cookie_summary(args: argparse.Namespace) -> None:
    cookie_path = Path(args.cookie_path or DEFAULT_COOKIE_PATH).expanduser().resolve()
    try:
        bundle = load_cookie_bundle(cookie_path)
    except FileNotFoundError:
        summary = {
            "cookiePath": str(cookie_path),
            "exists": False,
            "missingRequired": ["sid", "s2"],
            "nextStep": "Import cookies with `import-curl` or `import-header`.",
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    names = bundle.get("cookieNames") or []
    header = str(bundle.get("cookieHeader", "")).strip()
    summary = {
        "cookiePath": str(cookie_path),
        "exists": True,
        "updatedAt": bundle.get("updatedAt"),
        "source": bundle.get("source"),
        "cookieNames": names,
        "missingRequired": missing_required_cookies(bundle),
        "maskedCookieHeader": mask_secret(header, keep=12) if header else "",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def cmd_ssr_dump(args: argparse.Namespace) -> None:
    bundle = load_bundle(args.cookie_path)
    require_cookie_health(bundle, allow_partial=args.allow_partial)
    html = fetch_html(args.page_url, bundle, referer=args.page_url)
    decoded = decode_ssr_data_from_html(html)

    if args.list_names:
        for name in list_snapshot_names(decoded):
            print(name)
        return

    output: Any = decoded
    if args.snapshot:
        snapshot = find_snapshot(decoded, *args.snapshot)
        if snapshot is None:
            raise SystemExit("Requested snapshot not found in SSR data.")
        output = snapshot

    if args.output:
        target = write_json(args.output, output)
        print(f"Wrote SSR data to {target}")
        return

    print(json.dumps(output, ensure_ascii=False, indent=2))


def load_resume_state(output_path: Path) -> dict[str, Any]:
    if not output_path.exists():
        raise SystemExit(f"Resume file does not exist: {output_path}")
    payload = json.loads(output_path.read_text())
    if not isinstance(payload, dict):
        raise SystemExit("Resume file must contain a JSON object.")
    return payload


def cmd_feed_crawl(args: argparse.Namespace) -> None:
    bundle = load_bundle(args.cookie_path)
    require_cookie_health(bundle, allow_partial=args.allow_partial)

    output_path = Path(args.output).expanduser().resolve() if args.output else None
    state: dict[str, Any]
    if args.resume:
        if output_path is None:
            raise SystemExit("--resume requires --output.")
        state = load_resume_state(output_path)
        folder_ids = split_csv(args.folder_ids) or state.get("folderIds") or []
        current_window = str(
            args.window_utc
            or state.get("state", {}).get("nextWindowUTC")
            or state.get("state", {}).get("lastWindowUTC")
            or ""
        ).strip()
        windows = state.get("windows") or []
    else:
        html = fetch_html(args.page_url, bundle, referer=args.page_url)
        decoded = decode_ssr_data_from_html(html)
        bootstrap = extract_recommendation_bootstrap(decoded)
        folder_ids = split_csv(args.folder_ids) or bootstrap["folderIds"]
        current_window = str(args.window_utc or bootstrap["windowUTC"] or "").strip()
        windows = []
        state = {
            "source": "semantic-scholar-feed-crawl",
            "pageUrl": args.page_url,
            "bootstrap": bootstrap,
            "folderIds": folder_ids,
            "windows": windows,
            "state": {},
        }

    if not folder_ids:
        raise SystemExit("No folderIds available. Pass --folder-ids or bootstrap from SSR.")
    if not current_window:
        raise SystemExit("No starting windowUTC available. Pass --window-utc or bootstrap from SSR.")

    seen_windows = {str(window.get("windowUTC", "")).strip() for window in windows}
    stop_reason = "max-windows"
    while len(windows) < args.max_windows:
        if current_window in seen_windows:
            stop_reason = "duplicate-window"
            break

        api_url = build_feed_url(folder_ids, current_window)
        payload = fetch_json(api_url, bundle, referer=args.page_url)
        days = payload.get("days") or []
        next_window = payload.get("nextWindowUTC")

        record = {
            "windowUTC": current_window,
            "nextWindowUTC": next_window,
            "paperCount": count_papers(days),
            "days": days,
            "responseMeta": {
                key: value
                for key, value in payload.items()
                if key not in {"days", "nextWindowUTC"}
            },
        }
        windows.append(record)
        seen_windows.add(current_window)

        state["folderIds"] = folder_ids
        state["windows"] = windows
        state["summary"] = summarize_crawl(windows)
        state["state"] = {
            "lastWindowUTC": current_window,
            "nextWindowUTC": next_window,
            "stopReason": None,
            "finished": False,
        }
        if output_path is not None:
            write_json(output_path, state)

        if not days:
            stop_reason = "empty-days"
            break
        if next_window in (None, ""):
            stop_reason = "no-next-window"
            break
        current_window = str(next_window)

    state["summary"] = summarize_crawl(windows)
    state["state"] = {
        "lastWindowUTC": windows[-1]["windowUTC"] if windows else None,
        "nextWindowUTC": windows[-1]["nextWindowUTC"] if windows else current_window,
        "stopReason": stop_reason,
        "finished": stop_reason in {"empty-days", "no-next-window", "duplicate-window"},
    }

    if output_path is not None:
        target = write_json(output_path, state)
        print(f"Wrote crawl state to {target}")

    print(json.dumps(state["summary"], ensure_ascii=False, indent=2))
    print(f"Stop reason: {stop_reason}")


def cmd_folder_entries(args: argparse.Namespace) -> None:
    if args.page_size > 100:
        raise SystemExit("Semantic Scholar folder entries pageSize must be <= 100.")
    bundle = load_bundle(args.cookie_path)
    require_cookie_health(bundle, allow_partial=args.allow_partial)

    page = args.page
    combined: list[Any] = []
    last_payload: dict[str, Any] | None = None
    filters = args.entry_source_type_filter or [
        "AuthorLibraryFolder",
        "Library",
        "Feed",
    ]

    while True:
        query = urlencode(
            [
                *[("entrySourceTypeFilter", value) for value in filters],
                ("q", args.query),
                ("page", str(page)),
                ("pageSize", str(args.page_size)),
                ("sort", args.sort),
            ],
            doseq=True,
        )
        url = (
            f"{SEMANTIC_SCHOLAR_ORIGIN}/api/1/library/folders/"
            f"{args.folder_id}/entries?{query}"
        )
        referer = f"{SEMANTIC_SCHOLAR_ORIGIN}/me/library/folder/{args.folder_id}"
        payload = fetch_json(url, bundle, referer=referer)
        last_payload = payload
        combined.extend(payload.get("entries") or [])
        if not args.all_pages:
            break
        total_pages = int(payload.get("totalPages") or 1)
        if page >= total_pages:
            break
        page += 1

    if args.all_pages:
        output = {
            "folderId": args.folder_id,
            "pageSize": args.page_size,
            "query": args.query,
            "sort": args.sort,
            "entrySourceTypeFilter": filters,
            "totalHits": last_payload.get("totalHits") if last_payload else None,
            "totalPages": last_payload.get("totalPages") if last_payload else None,
            "entries": combined,
        }
    else:
        output = last_payload

    if args.output:
        target = write_json(args.output, output)
        print(f"Wrote folder entries to {target}")
        return

    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_folder_add(args: argparse.Namespace) -> None:
    folder_ids = [int(item) for item in split_csv(args.folder_ids)]
    body = {
        "paperId": args.paper_id,
        "paperTitle": args.paper_title,
        "folderIds": folder_ids,
        "annotationState": None,
        "sourceType": "Library",
    }
    if args.dry_run:
        print(json.dumps(body, ensure_ascii=False, indent=2))
        return

    bundle = load_bundle(args.cookie_path)
    require_cookie_health(bundle, allow_partial=args.allow_partial)
    url = f"{SEMANTIC_SCHOLAR_ORIGIN}/api/1/library/folders/entries/bulk"
    payload = fetch_json(
        url,
        bundle,
        method="POST",
        referer=f"{SEMANTIC_SCHOLAR_ORIGIN}/paper/{args.paper_id}",
        json_body=body,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_graph_batch(args: argparse.Namespace) -> None:
    ids = split_csv(args.ids)
    if args.ids_file:
        ids.extend(
            [
                line.strip()
                for line in Path(args.ids_file).expanduser().read_text().splitlines()
                if line.strip()
            ]
        )
    deduped: list[str] = []
    seen: set[str] = set()
    for identifier in ids:
        if identifier not in seen:
            deduped.append(identifier)
            seen.add(identifier)
    if not deduped:
        raise SystemExit("Provide at least one identifier with --ids or --ids-file.")

    query = urlencode({"fields": args.fields})
    url = f"{GRAPH_API_ORIGIN}/graph/v1/paper/batch?{query}"
    payload = fetch_json(
        url,
        None,
        method="POST",
        referer=GRAPH_API_ORIGIN,
        json_body={"ids": deduped},
    )
    if args.output:
        target = write_json(args.output, payload)
        print(f"Wrote Graph batch results to {target}")
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Authenticated Semantic Scholar helper for Library and Research Feeds."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    import_header = subparsers.add_parser(
        "import-header",
        help="Import a raw Cookie header and save it in the fixed cookie store.",
    )
    import_header.add_argument("--cookie-path", default=str(DEFAULT_COOKIE_PATH))
    import_header.add_argument("--header")
    import_header.add_argument("--header-file")
    import_header.add_argument("--allow-partial", action="store_true")
    import_header.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    import_header.set_defaults(func=cmd_import_header)

    import_curl = subparsers.add_parser(
        "import-curl",
        help="Import cookies from a browser-copied curl command.",
    )
    import_curl.add_argument("--cookie-path", default=str(DEFAULT_COOKIE_PATH))
    import_curl.add_argument("--curl")
    import_curl.add_argument("--curl-file")
    import_curl.add_argument("--allow-partial", action="store_true")
    import_curl.add_argument("--user-agent", default="")
    import_curl.set_defaults(func=cmd_import_curl)

    cookie_summary = subparsers.add_parser("cookie-summary", help="Print cookie store summary.")
    cookie_summary.add_argument("--cookie-path", default=str(DEFAULT_COOKIE_PATH))
    cookie_summary.set_defaults(func=cmd_cookie_summary)

    ssr_dump = subparsers.add_parser(
        "ssr-dump",
        help="Fetch a private Semantic Scholar page, decode `var DATA`, and print or save it.",
    )
    ssr_dump.add_argument("--cookie-path", default=str(DEFAULT_COOKIE_PATH))
    ssr_dump.add_argument("--page-url", default=f"{SEMANTIC_SCHOLAR_ORIGIN}/me/recommendations")
    ssr_dump.add_argument("--snapshot", action="append")
    ssr_dump.add_argument("--list-names", action="store_true")
    ssr_dump.add_argument("--allow-partial", action="store_true")
    ssr_dump.add_argument("--output")
    ssr_dump.set_defaults(func=cmd_ssr_dump)

    feed_crawl = subparsers.add_parser(
        "feed-crawl",
        help="Bootstrap from SSR and paginate Research Feeds through /api/1.",
    )
    feed_crawl.add_argument("--cookie-path", default=str(DEFAULT_COOKIE_PATH))
    feed_crawl.add_argument("--page-url", default=f"{SEMANTIC_SCHOLAR_ORIGIN}/me/recommendations")
    feed_crawl.add_argument("--folder-ids", action="append")
    feed_crawl.add_argument("--window-utc")
    feed_crawl.add_argument("--max-windows", type=int, default=200)
    feed_crawl.add_argument("--output")
    feed_crawl.add_argument("--resume", action="store_true")
    feed_crawl.add_argument("--allow-partial", action="store_true")
    feed_crawl.set_defaults(func=cmd_feed_crawl)

    folder_entries = subparsers.add_parser(
        "folder-entries",
        help="List items in a private Library folder via /api/1/library/folders/<id>/entries.",
    )
    folder_entries.add_argument("--cookie-path", default=str(DEFAULT_COOKIE_PATH))
    folder_entries.add_argument("--folder-id", required=True)
    folder_entries.add_argument("--page", type=int, default=1)
    folder_entries.add_argument("--page-size", type=int, default=100)
    folder_entries.add_argument("--query", default="")
    folder_entries.add_argument("--sort", default="date_added_to_library")
    folder_entries.add_argument("--entry-source-type-filter", action="append")
    folder_entries.add_argument("--all-pages", action="store_true")
    folder_entries.add_argument("--allow-partial", action="store_true")
    folder_entries.add_argument("--output")
    folder_entries.set_defaults(func=cmd_folder_entries)

    folder_add = subparsers.add_parser(
        "folder-add",
        help="Add a paper to one or more Library folders through entries/bulk.",
    )
    folder_add.add_argument("--cookie-path", default=str(DEFAULT_COOKIE_PATH))
    folder_add.add_argument("--paper-id", required=True)
    folder_add.add_argument("--paper-title", required=True)
    folder_add.add_argument("--folder-ids", action="append", required=True)
    folder_add.add_argument("--dry-run", action="store_true")
    folder_add.add_argument("--allow-partial", action="store_true")
    folder_add.set_defaults(func=cmd_folder_add)

    graph_batch = subparsers.add_parser(
        "graph-batch",
        help="Resolve ARXIV:/DOI:/Corpus identifiers through the Graph paper/batch API.",
    )
    graph_batch.add_argument("--ids", action="append")
    graph_batch.add_argument("--ids-file")
    graph_batch.add_argument("--fields", default="paperId,title,year,url,externalIds")
    graph_batch.add_argument("--output")
    graph_batch.set_defaults(func=cmd_graph_batch)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
