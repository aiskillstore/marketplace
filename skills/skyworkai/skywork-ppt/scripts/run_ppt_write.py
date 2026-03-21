#!/usr/bin/env python3
"""
Call the ppt_write streaming API, output progress to stdout (for skill to relay in conversation), and save to disk via download_url upon completion.
Supports multiple environments: specify Base URL via environment variables or --env.

General usage (independent of skill installation path):
  - Recommended: have the platform execute run_ppt_write.py from the skill root, e.g.: python <skill_root>/run_ppt_write.py "title" -o my.pptx
    When the user types /ppt-write title, the platform resolves the skill root and runs the above command; no need for the user to specify the path.
  - Or call this script directly: python <skill_root>/scripts/call_stream.py "title" -o my.pptx
"""
import argparse
import datetime
import json
import os
import sys
import urllib.request
import urllib.error
import uuid

from config import SKYWORK_GATEWAY_URL

from skywork_auth import get_skywork_token

def get_base_url() -> str:
    return SKYWORK_GATEWAY_URL


def write_log(log_file: str, line: str):
    """Append a plain-text line to the log file."""
    try:
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_str = f"{time_str} {line.rstrip()}\n"
        print(log_str, flush=True)
        with open(log_file, "a", encoding="utf-8") as f:            
            f.write(log_str)
            f.flush()
    except Exception:
        pass


def phase_to_message(phase: str, data: dict) -> str:
    """Convert phase to a message suitable for conversation output (consistent with SKILL progress output)"""
    if phase == "outline":
        return "Generating outline..."
    if phase == "outline_page":
        # Outline page-by-page streaming output: show page number and content (newlines collapsed to spaces for single-line console display)
        page_num = data.get("page_num") or 0
        content = (data.get("content") or "").strip()
        if isinstance(content, str):
            content = " ".join(content.split())
        else:
            content = str(content) if content else ""
        if content:
            line = f"  Page {page_num}: {content[:300]}{'...' if len(content) > 300 else ''}"
            return line
        return f"  Page {page_num}: (no body text)"
    if phase == "outline_done":
        return "Outline generated successfully!"
    if phase == "slides":
        return "Generating slides..."
    if phase == "slides_page":
        page_num = data.get("page_num") or 0
        return f"Finish generating Page {page_num} "
    if phase == "slides_page_start":
        page_num = data.get("page_num") or 0
        content = " ".join((data.get("content") or "").split())
        snippet = content[:200] + ("..." if len(content) > 200 else "")
        return f"Start generating page {page_num},content: \n{snippet}" if snippet else f"Start generating page {page_num}"
    if phase == "slides_done":
        return "Slides generated, exporting PPTX..."
    if phase == "export":
        status = data.get("status", "")
        if status == "done":
            return "Export complete."
        return "Exporting PPTX... this step takes 2-5 minutes. KEEP reading this log every 5 seconds — do NOT stop polling until you see [DONE] or [ERROR]."
    if phase == "done":
        return "Generation complete, saving file..."
    if phase == "ping":
        progress = data.get("progress", "")
        stage = data.get("stage", "")
        return f"Now {progress}% was done, and is working on {stage}" if stage else f"{progress}%"
    # --- Update/Edit PPT specific phases ---
    if phase == "parse_pptx":
        status = data.get("status", "")
        if status == "start":
            return "Parsing existing PPTX..."
        if status == "done":
            count = data.get("original_pptx_slide_count", "")
            return f"PPTX parsed, {count} slides total."
        return ""
    if phase == "gen_update_plan":
        status = data.get("status", "")
        if status == "start":
            return "Generating update plan..."
        if status == "done":
            update_count = data.get("update_pptx_slide_count", "")
            new_count = data.get("new_slide_count", 0)
            return f"Update plan ready: {update_count} slides to update, {new_count} new slides to generate."
        return ""
    if phase == "gen_new_slides":
        status = data.get("status", "")
        if status == "start":
            return "Generating updated slides..."
        if status == "done":
            count = data.get("generated_new_slide_count", "")
            return f"Updated slides generated ({count} slides)."
        page_num = data.get("page_num")
        if page_num is not None:
            return f"Slide {page_num} updated."
        return ""
    if phase == "export_update_pptx":
        status = data.get("status", "")
        if status == "start":
            return "Exporting updated PPTX..."
        if status == "done":
            count = data.get("generated_update_pptx_slide_count", "")
            return f"Export complete, {count} slides."
        return ""
    # --- Template-based generation specific phases ---
    if phase == "parse_template":
        status = data.get("status", "")
        if status == "start":
            return "Parsing template..."
        if status == "done":
            slide_count = data.get("slide_count", "")
            return f"Template parsing complete, {slide_count} pages in total."
        return ""
    if phase == "gen_outline":
        status = data.get("status", "")
        if status == "start":
            return "Generating outline..."
        if status == "done":
            page_count = data.get("page_count", "")
            return f"Outline generated, {page_count} pages in total."
        return ""
    if phase == "assign_templates":
        status = data.get("status", "")
        page_count = data.get("page_count", "")
        if status == "start":
            return "Assigning templates to each page..."
        if status == "done":
            return f"Template assignment complete, {page_count} pages in total."
        return ""
    if phase == "fill_content":
        status = data.get("status", "")
        page_count = data.get("page_count", "")
        if status == "start":
            return "Filling in content..."
        if status == "done":
            return f"Content filled, {page_count} pages in total."
        return ""
    if phase == "gen_images":
        status = data.get("status", "")
        if status == "start":
            return "Generating images..."
        if status == "done":
            return "Image generation complete."
        return ""
    if phase == "slide_image":
        page_num = data.get("page_num", "")
        return f"Page {page_num} image generated."
    if phase == "convert_html":
        status = data.get("status", "")
        if status == "start":
            return "Converting HTML..."
        if status == "done":
            page_count = data.get("page_count", "")
            return f"HTML conversion complete, {page_count} pages in total."
        return ""
    if phase:
        return f"[{phase}]"
    return "..."


def parse_sse_stream(resp):
    """Parse SSE stream, yield (event_type, data_dict).
    The backend SendEventData wraps data as {"code":0,"message":"success","data": payload}; the data field needs to be extracted.
    """
    cur_event = None
    cur_data = None
    for line in resp:
        line = line.decode("utf-8", errors="replace").rstrip("\r\n")
        if line == "":
            if cur_event is not None and cur_data is not None:
                try:
                    raw = json.loads(cur_data) if cur_data else {}
                except json.JSONDecodeError:
                    raw = {}
                # Compatible with backend wrapper format: {"code":0,"message":"success","data": {...}}; data may also be a JSON string
                data = raw.get("data", raw) if isinstance(raw, dict) else raw
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        data = {}
                if not isinstance(data, dict):
                    data = {}
                yield cur_event, data
            cur_event = None
            cur_data = None
            continue
        if line.startswith("event:"):
            cur_event = line[6:].strip()
        elif line.startswith("data:"):
            cur_data = line[5:].strip()
    if cur_event is not None and cur_data is not None:
        try:
            raw = json.loads(cur_data) if cur_data else {}
        except json.JSONDecodeError:
            raw = {}
        data = raw.get("data", raw) if isinstance(raw, dict) else raw
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = {}
        if not isinstance(data, dict):
            data = {}
        yield cur_event, data


def main():
    parser = argparse.ArgumentParser(description="Call ppt_write stream API and save .pptx")
    parser.add_argument("query", nargs="?", default="", help="User query / PPT topic")
    parser.add_argument("--language", default="en", help="Language used to generate slides. e.g. English, Chinese, etc.")
    parser.add_argument("--reference", default="", help="Reference content for enriching slide content, e.g. web search results summary.")
    parser.add_argument("--reference-file", default="", dest="reference_file", help="Path to a local file whose content will be used as reference (preferred over --reference to avoid shell encoding issues).")
    parser.add_argument("-o", "--output", default="output.pptx", help="Output .pptx path")
    parser.add_argument("--session_id", default=str(uuid.uuid4()), help="session_id used for distinct ppt generate query")
    parser.add_argument("--template_urls", default="", help="Comma-separated list of template PPTX OSS URLs for style imitation")
    parser.add_argument("--files", default="", help='Reference files JSON from upload_files.py UPLOADED_FILES output, format: [{"filename":"a.pdf","url":"https://..."}]')
    parser.add_argument("--pptx-url", default="", dest="pptx_url", help="OSS URL of an existing PPTX to edit (triggers update/edit mode instead of generation).")
    parser.add_argument("--log_path", default="", dest="log_path", help="A file path to save the progress log.")
    args = parser.parse_args()
    query = args.query.strip()
    if not query:
        parser.error("query is required")
        return

    base_url = get_base_url()
    payload = {"query": query, "language": args.language}

    session_id = args.session_id.replace('-', '_')
    log_file = f"/tmp/ppt_run_{session_id}.log" if args.log_path == "" else args.log_path
    open(log_file, "w").close()  # clear previous run
    print(f"[LOG-File]: {log_file}", flush=True)

    # Determine endpoint and mode
    if args.pptx_url:
        url = f"{base_url}/update_pptx_process"
        payload["pptx_url"] = args.pptx_url
        mode = "editing"
    elif args.template_urls:
        url = f"{base_url}/chat_pptx_process"
        payload["template_urls"] = [u.strip() for u in args.template_urls.split(",") if u.strip()]
        mode = "imitation"
    else:
        url = f"{base_url}/ppt_write_stream"
        mode = "generating"

    print(f"[PID] {os.getpid()}", flush=True)
    print(f"[START] mode={mode} session={session_id} \nIS about to take 5-10minutes, please wait and check the process log every 5 seconds!", flush=True)
    write_log(log_file, f"[PID] {os.getpid()}")
    write_log(log_file, f"[START] mode={mode} session={session_id} \nIS about to take 5-10minutes, please wait and check the process log every 5 seconds!")

    reference = args.reference
    if args.reference_file:
        try:
            with open(args.reference_file, "r", encoding="utf-8") as f:
                reference = f.read()
        except Exception as e:
            print(f"[error] Failed to read reference file: {e}", file=sys.stderr)
            sys.exit(1)
    if reference:
        payload["reference"] = reference
    if args.files:
        try:
            payload["files"] = json.loads(args.files)
        except json.JSONDecodeError as e:
            print(f"--files JSON parse error: {e}", file=sys.stderr)
            sys.exit(1)
    payload["source_platform"] = "skyclaw" if os.environ.get("POD_TYPE", "") == "skyclaw" else ""
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "Session-Id": session_id,
        "Language": args.language,
    }
    token = get_skywork_token()
    if not token:
        print("[error] Failed to get token", file=sys.stderr)
        sys.exit(1)
    headers["Token"] = token

    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers=headers,
    )

    out_abs = os.path.abspath(args.output)
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            for event_type, data in parse_sse_stream(resp):
                if not isinstance(data, dict):
                    data = {}
                if event_type == "phase":
                    phase = data.get("phase", "")
                    msg = phase_to_message(phase, data)
                    if msg:
                        tag = "[PROGRESS]" if phase == "ping" else "[PHASE]"
                        write_log(log_file, f"{tag} {msg}")
                    if phase == "outline_done":
                        outline = data.get("outline", "")
                        if outline:
                            write_log(log_file, f"[OUTLINE]\n{outline}")
                elif event_type == "completionEvent":
                    phase = data.get("phase", "")
                    if phase == "done":
                        download_url = data.get("download_url")
                        write_log(log_file, "[PHASE] Generation complete, saving file to local disk. This may take 1 or 2 minutes, we are already success!")
                        if not download_url:
                            write_log(log_file, "[ERROR] No download_url in completionEvent")
                            sys.exit(1)
                        try:
                            req2 = urllib.request.Request(download_url, method="GET")
                            with urllib.request.urlopen(req2, timeout=120) as r:
                                with open(out_abs, "wb") as f:
                                    f.write(r.read())
                            write_log(log_file, f"[DONE] saved={out_abs} download_url={download_url}")
                        except Exception as e:
                            write_log(log_file, f"[ERROR] Download failed: {e}")
                            sys.exit(1)
                elif event_type == "error":
                    err_msg = data.get("message", str(data))
                    write_log(log_file, f"[ERROR] {err_msg}")
                    sys.exit(1)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        write_log(log_file, f"[ERROR] HTTP {e.code}: {body}")
        sys.exit(1)
    except Exception as e:
        write_log(log_file, f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
