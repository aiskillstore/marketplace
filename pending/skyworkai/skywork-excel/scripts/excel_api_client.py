#!/usr/bin/env python3
"""
Excel Agent API Client

A helper module for interacting with the Excel Agent backend service.
Handles SSE streaming, file upload/download, and progress display.

Usage:
    from excel_api_client import ExcelAgentClient

    # Auto-login (recommended) - will prompt browser login if needed
    client = ExcelAgentClient()

    # Or with environment variable
    # export SKYBOT_TOKEN="your-token"
    # client = ExcelAgentClient()

    # Or with explicit token
    # client = ExcelAgentClient(token="your-token")

    if not client.health_check():
        raise RuntimeError("Service not available or token invalid")

    file_ids = [client.upload_file("data.xlsx")]
    outputs = client.run_agent("Create a summary report", file_ids=file_ids)

    for f in outputs:
        client.download_file(f["file_id"], f"./{f['name']}")
"""

import datetime
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from typing import Optional

from skywork_auth import get_skywork_token as _auth_get_token


# ---------------------------------------------------------------------------
# Log file support (for OpenClaw progress polling)
# ---------------------------------------------------------------------------

_LOG_FILE: Optional[str] = None


def _init_log_file(session_id: str = "", log_path: str = "") -> str:
    """Initialize log file for this session."""
    global _LOG_FILE
    if log_path:
        _LOG_FILE = log_path
    else:
        if not session_id:
            session_id = str(uuid.uuid4()).replace('-', '_')
        _LOG_FILE = f"/tmp/excel_run_{session_id}.log"
    # Clear previous run
    open(_LOG_FILE, "w").close()
    return _LOG_FILE


def write_log(line: str) -> None:
    """
    Append a timestamped line to both stdout and log file.
    This keeps OpenClaw informed of progress during long-running tasks.
    """
    global _LOG_FILE
    try:
        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_str = f"{time_str} {line.rstrip()}\n"
        print(log_str, end="", flush=True)
        if _LOG_FILE:
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_str)
                f.flush()
    except Exception:
        pass


class HeartbeatThread(threading.Thread):
    """
    Background thread that outputs heartbeat messages every N seconds.
    This keeps OpenClaw informed that the process is still alive,
    even when the main thread is blocked waiting for SSE data.
    """
    def __init__(self, interval: int = 30):
        super().__init__(daemon=True)
        self.interval = interval
        self.start_time = time.time()
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.wait(self.interval):
            elapsed_min = (time.time() - self.start_time) / 60
            write_log(f"[HEARTBEAT] Still processing... ({elapsed_min:.1f} minutes elapsed)")

    def stop(self):
        self._stop_event.set()

SKYWORK_GATEWAY_URL = os.environ.get("SKYWORK_GATEWAY_URL", "https://api-tools.skywork.ai/theme-gateway").rstrip("/")


def _get_token_auto() -> str:
    """
    Get Skywork token via auth module.

    Returns:
        str: Valid token, or empty string on failure
    """
    try:
        return _auth_get_token()
    except Exception:
        return ""


class ExcelAgentClient:
    """Client for the Excel Agent backend service."""

    def __init__(
        self,
        base_url: str = SKYWORK_GATEWAY_URL,
        token: str = None,
        timeout: int = 900
    ):
        """
        Initialize the client.

        Args:
            base_url: Backend service URL (default: test environment)
            token: User authentication token. If not provided, will try:
                   1. Environment variable SKYBOT_TOKEN
                   2. Global token file ~/.skywork_token
            timeout: Request timeout in seconds (default: 900, suitable for complex tasks)
        """
        self.base_url = base_url.rstrip("/")
        
        # Get token: explicit > env var > auto-login
        if token is not None:
            self.token = token
        else:
            self.token = _get_token_auto()
        
        self.timeout = timeout
        self._headers = {"token": self.token} if self.token else {}
        self._source_platform = "skyclaw" if os.environ.get("POD_TYPE", "") == "skyclaw" else ""

        # Note: Token logging removed to avoid OpenClaw treating stderr as error

    def _build_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[dict] = None,
        data: Optional[bytes] = None
    ) -> urllib.request.Request:
        """Build a urllib request with merged headers."""
        request_headers = {**self._headers}
        if headers:
            request_headers.update(headers)
        return urllib.request.Request(url=url, data=data, headers=request_headers, method=method)

    def _urlopen(
        self,
        request: urllib.request.Request,
        timeout: Optional[int] = None
    ):
        """Open a URL request with configured timeout."""
        return urllib.request.urlopen(request, timeout=timeout or self.timeout)

    def health_check(self, retries: int = 3, retry_delay: float = 2.0) -> bool:
        """
        Check if the backend service is healthy and ready.

        Args:
            retries: Number of retry attempts (default: 3, for ECI allocation instability)
            retry_delay: Delay between retries in seconds (default: 2.0)

        Returns:
            True if service is operational, False otherwise
        """
        last_error = None
        for attempt in range(retries):
            try:
                req = self._build_request(f"{self.base_url}/api/sse/excel-agent/health")
                with self._urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data.get("status") == "ok" and data.get("initialised", False):
                        return True
                    # Service responded but not ready, retry
                    last_error = f"Service not ready: {data}"
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    print("❌ Authentication failed: invalid or expired token", file=sys.stderr)
                    return False  # Don't retry auth failures
                elif e.code == 503:
                    # No backend available - ECI pool issue, worth retrying
                    last_error = "No backend available (ECI pool may be allocating)"
                else:
                    last_error = f"HTTP {e.code}: {e.reason}"
            except Exception as e:
                last_error = str(e)

            if attempt < retries - 1:
                time.sleep(retry_delay)

        if last_error:
            print(f"❌ Health check failed after {retries} attempts: {last_error}", file=sys.stderr)
        return False

    def upload_file(self, file_path: str) -> str:
        """
        Upload a file to the backend.

        Args:
            file_path: Path to the file to upload

        Returns:
            file_id: Unique identifier for the uploaded file

        Raises:
            urllib.error.HTTPError: If upload fails
        """
        with open(file_path, "rb") as f:
            file_content = f.read()

        filename = os.path.basename(file_path)
        boundary = f"----SkyworkBoundary{int(time.time() * 1000)}"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            "Content-Type: application/octet-stream\r\n\r\n"
        ).encode("utf-8") + file_content + f"\r\n--{boundary}--\r\n".encode("utf-8")

        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        req = self._build_request(
            url=f"{self.base_url}/api/upload",
            method="POST",
            headers=headers,
            data=body
        )
        with self._urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        file_id = payload["file_id"]
        print(f"✅ Uploaded: {file_path} → file_id={file_id}")
        return file_id

    def upload_files(self, file_paths: list[str], delay_between: float = 1.0) -> list[str]:
        """
        Upload multiple files with appropriate delays.

        Args:
            file_paths: List of file paths to upload
            delay_between: Delay between uploads in seconds (default: 1.0)

        Returns:
            List of file_ids for all uploaded files

        Raises:
            Exception: If any upload fails
        """
        file_ids = []
        total = len(file_paths)
        for i, file_path in enumerate(file_paths):
            file_id = self.upload_file(file_path)
            file_ids.append(file_id)
            # Add delay between uploads (except after the last one)
            if i < total - 1 and delay_between > 0:
                time.sleep(delay_between)
        return file_ids

    def run_agent(
        self,
        message: str,
        file_ids: Optional[list[str]] = None,
        session_id: str = "",
        language: str = "zh-CN",
        verbose: bool = True,
        new_session: bool = False,
        log_path: str = ""
    ) -> tuple[list[dict], str]:
        """
        Run the Excel Agent with streaming progress display.

        Args:
            message: User's task description
            file_ids: List of uploaded file IDs (optional)
            session_id: Session ID for multi-turn conversations (optional)
            language: "zh-CN" (Chinese) or "en-US" (English)
            verbose: Whether to print progress to stdout
            log_path: Custom log file path (optional, auto-generated if empty)

        Returns:
            tuple of (output_files, session_id):
                - output_files: List of generated file metadata dicts with keys:
                    - file_id: Unique identifier
                    - name: Filename
                    - size: File size in bytes
                    - mime_type: MIME type
                    - path: Server-side path
                    - oss_url: OSS download URL (if available)
                - session_id: The session ID used (useful if auto-generated)

        Raises:
            urllib.error.HTTPError: If request fails
        """
        # Initialize log file for progress tracking
        run_session_id = session_id if session_id else str(uuid.uuid4()).replace('-', '_')
        if log_path:
            global _LOG_FILE
            _LOG_FILE = log_path
            open(_LOG_FILE, "w").close()
        else:
            _init_log_file(run_session_id)
        
        write_log(f"[PID] {os.getpid()}")
        write_log(f"[LOG-File]: {_LOG_FILE}")
        write_log(f"[START] Excel Agent task starting. This may take 5-25 minutes, please wait and check the progress log!")

        payload = {
            "message": message,
            "file_ids": file_ids or [],
            "session_id": session_id,
            "language": language,
            "new_session": new_session,
            "source_platform": self._source_platform,
        }

        output_files = []
        actual_session_id = session_id  # Will be updated from session_start event

        if verbose:
            write_log(f"🚀 Starting Excel Agent...")
            write_log(f"⏱️  Timeout: {self.timeout}s (complex tasks may take 5-25 minutes)")
            write_log("=" * 60)

        headers = {"Content-Type": "application/json"}
        start_time = time.time()
        connected = False

        # Start heartbeat thread to output progress every 30 seconds
        # This runs in background so it works even when main thread is blocked on SSE
        heartbeat = HeartbeatThread(interval=30)
        heartbeat.start_time = start_time
        heartbeat.start()

        req = self._build_request(
            url=f"{self.base_url}/api/sse/excel-agent/chat",
            method="POST",
            headers=headers,
            data=json.dumps(payload).encode("utf-8")
        )
        try:
            with self._urlopen(req) as resp:
                for raw_line in resp:
                    line = raw_line.decode("utf-8", errors="ignore").strip()
                    # Show connection success on first data
                    if not connected and verbose:
                        elapsed = time.time() - start_time
                        write_log(f"📡 Connected to backend ({elapsed:.1f}s)")
                        write_log("🤖 Agent is working...")
                        connected = True

                    if not line.startswith("data: "):
                        continue

                    try:
                        event = json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue

                    event_type = event.get("type")

                    if event_type == "session_start":
                        # Capture the actual session_id from server
                        actual_session_id = event.get("session_id", session_id)
                        if verbose and not session_id:
                            write_log(f"📋 Session ID: {actual_session_id}")

                    elif event_type == "progress":
                        # Stream LLM output - write to log but keep it concise
                        content = event.get("content", "")
                        if verbose and content:
                            # For progress, just print without timestamp to avoid clutter
                            print(content, end="", flush=True)
                            # Write to log file periodically (every 500 chars)
                            if len(content) > 100:
                                write_log(f"[PROGRESS] LLM generating... ({len(content)} chars)")

                    elif event_type == "tool_start":
                        # Tool execution starting
                        if verbose:
                            tool_name = event["name"]
                            brief = event.get("brief", "")
                            write_log(f"\n🔧 Tool: [{tool_name}] {brief}")

                    elif event_type == "tool_result":
                        # Tool execution completed
                        if verbose:
                            tool_name = event.get("name", "")
                            success = event.get("success", True)
                            summary = event.get("summary", "")
                            if isinstance(summary, str):
                                summary = summary[:300]
                            else:
                                summary = str(summary)[:300]
                            icon = "✅" if success else "❌"
                            
                            # Special handling for todo_write - output clear progress summary
                            if tool_name == "todo_write":
                                write_log(f"\n{'='*60}")
                                write_log(f"📋 [TASK PROGRESS UPDATE]")
                                # Parse todo items from summary
                                try:
                                    for line in summary.split('\n'):
                                        line = line.strip()
                                        if line:
                                            write_log(f"   {line}")
                                except Exception as e:
                                    write_log(f"   {summary}")
                                write_log(f"{'='*60}")
                            else:
                                write_log(f"   {icon} {summary}")

                    elif event_type == "clarification_needed":
                        # Agent needs user input
                        if verbose:
                            card = event.get("card", {})
                            question = card.get("question", "")
                            options = card.get("options", [])
                            write_log(f"\n❓ Clarification needed: {question}")
                            for opt in options:
                                write_log(f"   - {opt}")

                    elif event_type == "output_files":
                        # Final output files
                        output_files = event["files"]
                        if verbose:
                            write_log(f"\n📁 Output files ({len(output_files)}):")
                            for f in output_files:
                                oss_url = f.get('oss_url')
                                if oss_url:
                                    write_log(f"   - {f['name']}  ({f['size']:,} bytes)")
                                    write_log(f"     ☁️ OSS: {oss_url}")
                                else:
                                    write_log(f"   - {f['name']}  ({f['size']:,} bytes)  id={f['file_id']}")

                    elif event_type == "usage":
                        # Token usage info (optional display)
                        pass

                    elif event_type == "usage_summary":
                        # Final cumulative usage
                        if verbose:
                            usage = event.get("usage", {})
                            total_tokens = usage.get("total_tokens", 0)
                            iterations = event.get("iterations", 0)
                            write_log(f"\n📊 Total tokens: {total_tokens:,} ({iterations} iterations)")

                    elif event_type == "done":
                        # Agent completed
                        if verbose:
                            stop_reason = event.get("stop_reason", "unknown")
                            total_time = time.time() - start_time
                            write_log(f"\n[DONE] stop_reason={stop_reason}")
                            write_log(f"⏱️  Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
                        break

                    elif event_type == "error":
                        # Error occurred
                        error_msg = event.get("message", "Unknown error")
                        write_log(f"\n[ERROR] {error_msg}")
                        break
        finally:
            # Stop heartbeat thread when done
            heartbeat.stop()

        return output_files, actual_session_id

    def download_file(self, file_id: str, save_path: str) -> None:
        """
        Download a file from the backend.

        Args:
            file_id: File identifier (from output_files)
            save_path: Local path to save the file

        Raises:
            urllib.error.HTTPError: If download fails
        """
        req = self._build_request(f"{self.base_url}/api/download/{file_id}")
        with self._urlopen(req, timeout=60) as resp:
            content = resp.read()

        with open(save_path, "wb") as f:
            f.write(content)

        print(f"💾 Downloaded: {save_path} ({len(content):,} bytes)")


def main():
    """Simple CLI for testing the Excel Agent."""
    import argparse

    parser = argparse.ArgumentParser(description="Excel Agent CLI")
    parser.add_argument("message", help="Task description for the agent")
    parser.add_argument("--token", default=None, help="User authentication token (auto-login if not provided)")
    parser.add_argument("--files", nargs="*", help="Files to upload")
    parser.add_argument("--session", help="Session ID for multi-turn (use same value across calls)")
    parser.add_argument("--new-session", action="store_true",
                        help="Clear existing session history before running")
    parser.add_argument("--lang", "--language", dest="lang", default="zh-CN", 
                        help="Language: zh-CN (Chinese) or en-US (English)")
    parser.add_argument("--output-dir", default=".", help="Download directory")
    parser.add_argument("--base-url", default=SKYWORK_GATEWAY_URL,
                        help="Backend service URL")
    parser.add_argument("--timeout", type=int, default=900,
                        help="Request timeout in seconds (default: 900)")
    parser.add_argument("--log-path", default="",
                        help="Path to save progress log (default: /tmp/excel_run_<session>.log)")

    args = parser.parse_args()

    client = ExcelAgentClient(base_url=args.base_url, token=args.token, timeout=args.timeout)

    # Health check
    print("Checking service health...")
    if not client.health_check():
        print("\n❌ Backend service is not available or token is invalid.")
        print("\nPlease check:")
        print("  1. Your token is valid and not expired")
        print("  2. The service URL is correct")
        sys.exit(1)

    print("✅ Service is healthy\n")

    # Upload files
    file_ids = []
    if args.files:
        write_log(f"📤 Uploading {len(args.files)} file(s):")
        for file_path in args.files:
            write_log(f"   - {file_path}")
        for file_path in args.files:
            try:
                file_id = client.upload_file(file_path)
                file_ids.append(file_id)
                write_log(f"   ✅ {os.path.basename(file_path)} -> file_id={file_id}")
            except Exception as e:
                write_log(f"   ❌ Failed to upload {file_path}: {e}")
                sys.exit(1)
        print()

    # Run agent
    try:
        output_files, actual_session_id = client.run_agent(
            message=args.message,
            file_ids=file_ids,
            session_id=args.session or "",
            language=args.lang,
            new_session=args.new_session,
            log_path=args.log_path
        )
    except Exception as e:
        print(f"\n❌ Agent failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Show session_id for multi-turn reference
    if actual_session_id and not args.session:
        print(f"\n💡 To continue this conversation, use: --session {actual_session_id}")

    # Download outputs
    if output_files:
        write_log(f"\n📥 Downloading {len(output_files)} output file(s)...")
        
        # Post-validation: prioritize /home/skywork/workspace if it exists
        final_output_dir = args.output_dir
        if os.path.isdir("/home/skywork/workspace"):
            final_output_dir = "/home/skywork/workspace"

        
        for f in output_files:
            save_path = os.path.abspath(f"{final_output_dir}/{f['name']}")
            oss_url = f.get('oss_url', '')
            try:
                client.download_file(f["file_id"], save_path)
                write_log(f"   ✅ {f['name']}")
                write_log(f"      📁 Local: {save_path}")
                if oss_url:
                    write_log(f"      ☁️  OSS: {oss_url}")
            except Exception as e:
                write_log(f"   ❌ Failed to download {f['name']}: {e}")

        write_log(f"\n✅ All done!")
        if actual_session_id:
            write_log(f"💡 To continue this conversation, use: --session {actual_session_id}")
    else:
        write_log("\n⚠️  No output files generated.")
        if actual_session_id:
            write_log(f"💡 To continue this conversation, use: --session {actual_session_id}")


if __name__ == "__main__":
    main()
