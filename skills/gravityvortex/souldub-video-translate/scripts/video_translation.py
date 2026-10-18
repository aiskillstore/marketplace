#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests>=2.32",
#   "pyyaml>=6.0",
#   "platformdirs>=4.3",
#   "mutagen>=1.47",
# ]
# ///
"""SoulDub original-voice video translation CLI helper."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import platformdirs
import requests
import yaml
from mutagen import File as MutagenFile

APP_NAME = ".souldub"
DEFAULT_API_BASE = "https://xxx.com/api/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CONFIG = SKILL_DIR / "config.example.yaml"
USER_CONFIG_DIR = Path.home() / ".souldub"
USER_CONFIG = USER_CONFIG_DIR / "souldub.config.yaml"
LANGUAGES_PATH = SKILL_DIR / "references" / "languages.json"
UPLOAD_PROGRESS_INTERVAL_SECONDS = 30
MAX_UPLOAD_CONCURRENCY = 4


class UserFacingError(RuntimeError):
    """Error that can be shown to the user without exposing request details."""


@dataclass
class RuntimeState:
    """Recoverable state for one run; never includes secrets or temporary signed URLs."""

    run_id:str
    state_path:Path
    progress_log_path:Path
    output_dir:Path
    source_video:str
    source_language_text:str
    target_language_text:str
    source_language:str = "auto"
    target_language:str = ""
    stage:str = "validating"
    status:str = "running"
    progress:int = 0
    message:str = ""
    task_id:str | None = None
    file_id:str | None = None
    upload_id:str | None = None
    key:str | None = None
    bucket:str | None = None
    checksum_sha256:str | None = None
    idempotency_key:str | None = None
    files:dict[str, str] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, Any]:
        """Convert to the public state.json shape.

        The state file is read by `status` and `list-runs`, so it uses
        agent/API-friendly camelCase field names and intentionally omits API
        keys, presigned URLs, and media URLs.
        """
        return {
            "runId": self.run_id,
            "stage": self.stage,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "taskId": self.task_id,
            "fileId": self.file_id,
            "uploadId": self.upload_id,
            "key": self.key,
            "bucket": self.bucket,
            "idempotencyKey": self.idempotency_key,
            "sourceVideo": self.source_video,
            "sourceLanguageText": self.source_language_text,
            "targetLanguageText": self.target_language_text,
            "sourceLanguage": self.source_language,
            "targetLanguage": self.target_language,
            "checksumSha256": self.checksum_sha256,
            "outputDir": str(self.output_dir),
            "files": self.files,
            "statePath": str(self.state_path),
            "updatedAt": now_iso(),
        }


def now_iso() -> str:
    """Return an ISO timestamp with the local timezone offset."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sanitize_stem(stem: str) -> str:
    """Sanitize a filename stem for use in output directory names.

    User video names may contain spaces, punctuation, or non-Latin characters.
    Keeping safe readable characters while replacing risky ones gives better
    cross-platform behavior without making output names opaque.
    """
    safe = re.sub(r"[^A-Za-z0-9._\-\u4e00-\u9fff]+", "-", stem).strip("-")
    return safe or "video"


def print_json(data: dict[str, Any]) -> None:
    """Print one JSON object to stdout."""
    print(json.dumps(data, ensure_ascii=False), flush=True)


def configure_text_streams() -> None:
    """Keep JSON output UTF-8 in Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def redacted_secret(value: str) -> str:
    """Return a safely displayable secret summary."""
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def sanitize_error_message(message: str) -> str:
    """Redact temporary URLs and signature parameters from an error message.

    `requests` exceptions may include media URLs or presigned upload URLs.
    These temporary signatures must not be written to logs, state, or chat.
    """
    redacted = re.sub(r"https?://[^\s)'\"]+", "[redacted-url]", message)
    redacted = re.sub(r"/m/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+", "/m/[redacted-token]", redacted)
    redacted = re.sub(r"(?i)(signature|credential|token|X-Amz-Signature|X-Amz-Credential)=([^&\s]+)", r"\1=[redacted]", redacted)
    return redacted


def emit(state: RuntimeState, event_type: str, stage: str | None = None, progress: int | None = None, message: str = "", **extra: Any) -> None:
    """Write a progress event and refresh state.json.

    Long jobs may outlive the current terminal session. Syncing state.json on
    every event lets an agent answer later status questions without guessing.
    """
    if stage is not None:
        state.stage = stage
    if progress is not None:
        state.progress = progress
    if message:
        state.message = sanitize_error_message(message)
    event = {
        "type": event_type,
        "run_id": state.run_id,
        "stage": state.stage,
        "progress": state.progress,
        "message": state.message,
        "state_path": str(state.state_path),
        "output_dir": str(state.output_dir),
        "updated_at": now_iso(),
        **extra,
    }
    state.state_path.parent.mkdir(parents=True, exist_ok=True)
    state.progress_log_path.parent.mkdir(parents=True, exist_ok=True)
    state.state_path.write_text(json.dumps(state.to_public_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with state.progress_log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(json.dumps(event, ensure_ascii=False), file=sys.stderr, flush=True)


class UploadProgressBody:
    """Readable upload part body that emits throttled upload progress."""

    def __init__(
        self,
        handle: Any,
        part_size: int,
        state: RuntimeState,
        part_number: int,
        total_parts: int,
        bytes_before_part: int,
        total_size: int,
    ) -> None:
        self.handle = handle
        self.remaining = part_size
        self.part_size = part_size
        self.state = state
        self.part_number = part_number
        self.total_parts = total_parts
        self.bytes_before_part = bytes_before_part
        self.total_size = max(1, total_size)
        self.bytes_read = 0
        self.last_emit_at = time.monotonic()

    def __len__(self) -> int:
        return self.part_size

    def read(self, size: int = -1) -> bytes:
        if self.remaining <= 0:
            return b""
        read_size = self.remaining if size is None or size < 0 else min(size, self.remaining)
        data = self.handle.read(read_size)
        if not data:
            self.remaining = 0
            return b""
        self.remaining -= len(data)
        self.bytes_read += len(data)
        self.emit_progress_if_due()
        return data

    def emit_progress_if_due(self) -> None:
        now = time.monotonic()
        if now - self.last_emit_at < UPLOAD_PROGRESS_INTERVAL_SECONDS:
            return
        self.last_emit_at = now
        uploaded = min(self.total_size, self.bytes_before_part + self.bytes_read)
        progress = 8 + int(32 * uploaded / self.total_size)
        uploaded_mib = uploaded / 1024 / 1024
        total_mib = self.total_size / 1024 / 1024
        emit(
            self.state,
            "progress",
            "uploading",
            min(40, progress),
            f"Uploading video part: sent {uploaded_mib:.1f}/{total_mib:.1f} MiB, current part {self.part_number}/{self.total_parts}.",
        )


def load_state_from_file(state_path: Path) -> RuntimeState:
    """Restore the minimal runtime state from state.json.

    A server task may already be complete while local download failed. Restoring
    state allows fresh temporary URLs without creating another billable task.
    """
    data = json.loads(state_path.read_text(encoding="utf-8"))
    state = RuntimeState(
        run_id=data["runId"],
        state_path=state_path,
        progress_log_path=state_path.with_name("progress.log"),
        output_dir=Path(data["outputDir"]),
        source_video=data.get("sourceVideo") or "",
        source_language_text=data.get("sourceLanguageText") or "auto",
        target_language_text=data.get("targetLanguageText") or "",
    )
    state.source_language = data.get("sourceLanguage") or "auto"
    state.target_language = data.get("targetLanguage") or ""
    state.stage = data.get("stage") or "downloading"
    state.status = data.get("status") or "running"
    state.progress = int(data.get("progress") or 0)
    state.message = data.get("message") or ""
    state.task_id = data.get("taskId")
    state.file_id = data.get("fileId")
    state.upload_id = data.get("uploadId")
    state.key = data.get("key")
    state.bucket = data.get("bucket")
    state.checksum_sha256 = data.get("checksumSha256")
    state.idempotency_key = data.get("idempotencyKey")
    state.files = data.get("files") or {}
    return state


def load_yaml(path: Path) -> dict[str, Any]:
    """Read a YAML config file and return an empty dict for missing or empty files."""
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def user_config_template() -> dict[str, Any]:
    """Return the user-level config template."""
    return {"api_base": DEFAULT_API_BASE, "souldub_api_key": ""}


def ensure_user_config_template() -> bool:
    """Ensure the user config file exists and contains the API key field."""
    changed = False
    config = load_yaml(USER_CONFIG)
    if not USER_CONFIG.exists():
        config = user_config_template()
        changed = True
    else:
        if "api_base" not in config:
            config["api_base"] = DEFAULT_API_BASE
            changed = True
        if "souldub_api_key" not in config:
            config["souldub_api_key"] = ""
            changed = True
    if changed:
        write_user_config(USER_CONFIG, config)
    return changed


def load_config() -> tuple[dict[str, Any], Path]:
    """Load and merge default config with user config."""
    defaults = load_yaml(DEFAULT_CONFIG)
    user_config = load_yaml(USER_CONFIG)
    merged = {**defaults, **user_config}
    env_key = os.environ.get("SOULDUB_API_KEY", "").strip()
    if env_key:
        merged["souldub_api_key"] = env_key
        merged["_api_key_source"] = "environment"
    elif str(merged.get("souldub_api_key") or "").strip():
        merged["_api_key_source"] = "config"
    else:
        ensure_user_config_template()
        merged["_api_key_source"] = "missing"
    merged["_config_path"] = str(USER_CONFIG)
    return merged, USER_CONFIG


def write_user_config(path: Path, config: dict[str, Any]) -> None:
    """Write the user config file and restrict permissions where possible."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {key: value for key, value in config.items() if not key.startswith("_")}
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def state_root(config: dict[str, Any]) -> Path:
    """Return the root directory used for saved run state."""
    configured = str(config.get("state_dir", "auto") or "auto")
    if configured.lower() == "auto":
        return Path(platformdirs.user_state_dir(APP_NAME))
    return Path(configured).expanduser().resolve()


def clamped_int(value: Any, default: int, minimum: int, maximum: int | None = None) -> int:
    """Parse an integer config value and clamp it to a safe range."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    parsed = max(minimum, parsed)
    if maximum is not None:
        parsed = min(maximum, parsed)
    return parsed


def output_root(config: dict[str, Any], video_path: Path) -> Path:
    """Return the root directory used for translated outputs."""
    configured = str(config.get("output_dir", "auto") or "auto")
    if configured.lower() == "auto":
        return video_path.parent / "souldub_outputs"
    return Path(configured).expanduser().resolve()


def make_run_state(config: dict[str, Any], video_path: Path, source_text: str, target_text: str) -> RuntimeState:
    """Create the runtime state object for one translation run."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = f"{timestamp}-{sanitize_stem(video_path.stem)}"
    out_dir = unique_dir(output_root(config, video_path) / run_id)
    run_dir = state_root(config) / "runs" / run_id
    return RuntimeState(
        run_id=run_id,
        state_path=run_dir / "state.json",
        progress_log_path=run_dir / "progress.log",
        output_dir=out_dir,
        source_video=str(video_path),
        source_language_text=source_text,
        target_language_text=target_text,
    )


def unique_dir(path: Path) -> Path:
    """Return a directory path that will not overwrite existing output."""
    if not path.exists():
        return path
    for index in range(1, 1000):
        candidate = path.with_name(f"{path.name}-{index}")
        if not candidate.exists():
            return candidate
    raise UserFacingError(f"Could not create a unique output directory: {path}")


def unique_file(path: Path) -> Path:
    """Return a file path that will not overwrite existing output."""
    if not path.exists():
        return path
    for index in range(1, 1000):
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise UserFacingError(f"Could not create a unique output file: {path}")


def validate_api_key(config: dict[str, Any]) -> str:
    """Read and validate the Agent API key."""
    key = str(config.get("souldub_api_key") or "").strip()
    if not key:
        raise UserFacingError(f"Missing souldub_api_key. Create an API key at souldub.ai, set souldub_api_key in {USER_CONFIG}, save the file, or set the SOULDUB_API_KEY environment variable.")
    return key


def load_languages() -> dict[str, Any]:
    """Read the generated supported-language registry."""
    if not LANGUAGES_PATH.exists():
        raise UserFacingError(f"Missing language registry file: {LANGUAGES_PATH}")
    return json.loads(LANGUAGES_PATH.read_text(encoding="utf-8"))


def normalize_language_text(text: str) -> str:
    """Normalize language text for deterministic matching."""
    return re.sub(r"[\s_（(].*?[）)]", "", text.strip().lower())


def language_candidates(entry: dict[str, Any]) -> list[tuple[str, str]]:
    """Return deterministic match candidates for one language registry entry."""
    return [
        ("code", str(entry["code"])),
        ("zh", str(entry["zh"])),
        ("en", str(entry["en"])),
    ]


def find_language(text: str, languages: dict[str, Any], mode: str) -> dict[str, Any]:
    """Find a language entry and return match details."""
    raw = text.strip()
    if mode == "source" and raw.lower() == "auto":
        return {"code": "auto", "zh": "自动识别", "en": "Auto Detect", "matched": "auto"}
    if mode == "target" and raw.lower() == "auto":
        raise UserFacingError("Target language cannot be auto. Provide a specific target language such as English, Japanese, Chinese, 日语, 中文, or 粤语.")
    entries = languages["source" if mode == "source" else "target"]
    normalized = normalize_language_text(raw)
    for entry in entries:
        for matched, candidate in language_candidates(entry):
            if normalize_language_text(candidate) == normalized:
                return {
                    "code": str(entry["code"]),
                    "zh": str(entry["zh"]),
                    "en": str(entry["en"]),
                    "matched": matched,
                }
    examples = ", ".join(str(item["en"]) for item in entries[:20])
    role = "source" if mode == "source" else "target"
    raise UserFacingError(f"Unsupported or unrecognized {role} language: {text}. Try one of: {examples}.")


def resolve_language(text: str, languages: dict[str, Any], mode: str) -> str:
    """Map user or agent-normalized language text to a SoulDub language code."""
    return str(find_language(text, languages, mode)["code"])


def language_examples(languages: dict[str, Any], mode: str, limit: int = 20) -> list[dict[str, str]]:
    """Return a few supported-language examples for resolve-language failures."""
    entries = languages["source" if mode == "source" else "target"]
    examples: list[dict[str, str]] = []
    for entry in entries[:limit]:
        examples.append({"code": str(entry["code"]), "zh": str(entry["zh"]), "en": str(entry["en"])})
    return examples


def validate_video(path_text: str) -> Path:
    """Validate the local source video file."""
    path = Path(path_text).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise UserFacingError(f"Video file does not exist: {path}")
    if path.suffix.lower() != ".mp4":
        raise UserFacingError("The current SoulDub Agent API only supports .mp4 files.")
    size_bytes = path.stat().st_size
    max_size_bytes = 5 * 1024 * 1024 * 1024
    if size_bytes <= 0:
        raise UserFacingError("Video file size must be greater than 0.")
    if size_bytes > max_size_bytes:
        raise UserFacingError(
            f"Video file size must not exceed 5 GiB; "
            f"current size is {size_bytes / (1024 ** 3):.3f} GiB."
        )
    return path


def video_duration_seconds(video_path: Path) -> int:
    """Read video duration and convert it to the seconds required by the API."""
    media = MutagenFile(video_path)
    if media is None or not getattr(media, "info", None) or not getattr(media.info, "length", None):
        raise UserFacingError("Could not read video duration. Confirm the file is a valid MP4.")
    duration = round(float(media.info.length))
    if duration < 1 or duration > 1800:
        raise UserFacingError(f"Video duration must be within 1..1800 seconds; current value is {duration} seconds.")
    return duration


def sha256_file(video_path: Path) -> str:
    """Calculate the file SHA-256."""
    digest = hashlib.sha256()
    with video_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_ascii_idempotency_key(state: RuntimeState) -> str:
    """Generate an HTTP-header-safe idempotency key."""
    raw = f"{state.run_id}:{state.file_id}:{state.source_language}:{state.target_language}:{state.checksum_sha256}"
    key_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"agent:{key_hash[:48]}"


class SoulDubClient:
    """Agent API client with centralized auth, rate-limit, and error handling."""

    def __init__(self, api_base: str, api_key: str, state: RuntimeState):
        """Initialize the API client."""
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.state = state
        self.session = requests.Session()

    def headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        """Build Agent API request headers."""
        request_hash = hashlib.sha1(self.state.run_id.encode("utf-8")).hexdigest()[:24]
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Request-Id": f"agent-{request_hash}",
        }
        if extra:
            headers.update(extra)
        return headers

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Send an Agent API request with bounded retry for transient failures."""
        url = f"{self.api_base}{path}"
        extra_headers = kwargs.pop("headers", None)
        for attempt in range(1, 6):
            response = self.session.request(method, url, headers=self.headers(extra_headers), timeout=60, **kwargs)
            if response.status_code == 429:
                wait = retry_after_seconds(response, default=min(30, 2 * attempt))
                emit(self.state, "warning", message="Service rate limit reached; waiting before retry.", retry_after_seconds=wait)
                time.sleep(wait)
                continue
            if 500 <= response.status_code < 600:
                wait = min(30, 2**attempt)
                emit(self.state, "warning", message="Service temporarily unavailable; waiting before retry.", retry_after_seconds=wait)
                time.sleep(wait)
                continue
            return parse_response(response)
        raise UserFacingError("Service returned rate-limit or temporary errors repeatedly; stopped retrying.")

    def initiate_upload(self, video_path: Path) -> dict[str, Any]:
        """Initiate an upload session."""
        return self.request(
            "POST",
            "/video-uploads/initiate",
            json={"filename": video_path.name, "contentType": "video/mp4", "fileSizeBytes": video_path.stat().st_size},
        )

    def presign_part(self, upload_id: str, key: str, part_number: int) -> dict[str, Any]:
        """Get a presigned upload URL for one part."""
        return self.request(
            "POST",
            "/video-uploads/presign-part",
            json={"uploadId": upload_id, "key": key, "partNumber": part_number, "expiresInSeconds": 900},
        )

    def complete_upload(self, upload_id: str, key: str) -> dict[str, Any]:
        """Tell the server the multipart upload is complete."""
        return self.request("POST", "/video-uploads/complete", json={"uploadId": upload_id, "key": key})

    def create_task(self, body: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        """Create a SoulDub translation task."""
        return self.request("POST", "/video-translations", headers={"Idempotency-Key": idempotency_key}, json=body)

    def get_task(self, task_id: str) -> dict[str, Any]:
        """Query translation task status."""
        return self.request("GET", f"/video-translations/{task_id}")

    def get_file(self, task_id: str, variant: str) -> dict[str, Any]:
        """Get temporary download info for one media result."""
        return self.request("GET", f"/video-translations/{task_id}/results/files/{variant}?expiresIn=600")

    def subtitle_response(self, task_id: str, variant: str) -> requests.Response:
        """Download a subtitle response whose body is plain SRT text."""
        url = f"{self.api_base}/video-translations/{task_id}/results/subtitles/{variant}?download=1"
        response = self.session.get(url, headers=self.headers(), timeout=60)
        if response.status_code >= 400:
            parse_response(response)
        return response


def retry_after_seconds(response: requests.Response, default: int) -> int:
    """Parse Retry-After seconds and clamp to a practical range."""
    raw = response.headers.get("Retry-After")
    if raw and raw.isdigit():
        return max(1, min(300, int(raw)))
    return default


def parse_response(response: requests.Response) -> Any:
    """Parse an Agent API response envelope."""
    try:
        payload = response.json()
    except ValueError:
        if response.ok:
            return response.text
        raise UserFacingError(f"HTTP {response.status_code}: service returned a non-JSON error.")
    if response.ok and payload.get("code") == 0:
        return payload.get("data")
    error = payload.get("error") or {}
    code = error.get("code") or payload.get("message") or f"HTTP_{response.status_code}"
    details = error.get("details") or {}
    if code == "LANGUAGE_PAIR_TASK_EXISTS" and details.get("existingTaskId"):
        return {"existingTaskId": details["existingTaskId"], "_existingTask": True}
    if code in {"RATE_LIMITED", "CONCURRENCY_LIMIT_REACHED", "IDEMPOTENCY_REQUEST_IN_PROGRESS"}:
        raise TransientApiError(code, str(error.get("message") or code))
    raise UserFacingError(f"{code}: {error.get('message') or payload.get('message') or 'request failed'}")


class TransientApiError(UserFacingError):
    """Service-side state that can be retried by a higher-level workflow."""

    def __init__(self, code: str, message: str):
        """Store the transient API error code and message."""
        super().__init__(message)
        self.code = code


def upload_part(
    client: SoulDubClient,
    state: RuntimeState,
    video_path: Path,
    part_number: int,
    offset: int,
    part_size: int,
    presign_lock: threading.Lock,
) -> int:
    """Upload one multipart part and return its part number."""
    with presign_lock:
        presign = client.presign_part(state.upload_id or "", state.key or "", part_number)
    with video_path.open("rb") as handle:
        handle.seek(offset)
        data = handle.read(part_size)
    # PUT goes directly to the presigned storage URL without an Agent API key.
    put_response = requests.put(presign["presignedUrl"], data=data, headers={"Content-Type": "video/mp4"}, timeout=300)
    if not 200 <= put_response.status_code < 300:
        raise UserFacingError(f"Failed to upload part {part_number}: HTTP {put_response.status_code}")
    return part_number


def upload_video(client: SoulDubClient, state: RuntimeState, video_path: Path, part_size_mib: int, concurrency: int) -> None:
    """Upload a local video file."""
    init = client.initiate_upload(video_path)
    state.file_id = init["fileId"]
    state.upload_id = init["uploadId"]
    state.key = init["key"]
    state.bucket = init.get("bucket")

    part_size = max(5, int(part_size_mib)) * 1024 * 1024
    upload_concurrency = clamped_int(concurrency, default=1, minimum=1, maximum=MAX_UPLOAD_CONCURRENCY)
    total_size = video_path.stat().st_size
    total_parts = max(1, math.ceil(total_size / part_size))
    upload_concurrency = min(upload_concurrency, total_parts)
    emit(state, "progress", "uploading", 8, f"Upload initialized; starting video part upload with concurrency {upload_concurrency}.")

    if upload_concurrency > 1:
        completed_parts = 0
        presign_lock = threading.Lock()
        with ThreadPoolExecutor(max_workers=upload_concurrency) as executor:
            futures = []
            for part_number in range(1, total_parts + 1):
                offset = (part_number - 1) * part_size
                current_part_size = min(part_size, total_size - offset)
                futures.append(executor.submit(upload_part, client, state, video_path, part_number, offset, current_part_size, presign_lock))
            for future in as_completed(futures):
                part_number = future.result()
                completed_parts += 1
                progress = 8 + int(32 * completed_parts / total_parts)
                emit(state, "progress", "uploading", progress, f"Uploaded {completed_parts}/{total_parts} parts; latest completed part {part_number}.")
    else:
        with video_path.open("rb") as handle:
            for part_number in range(1, total_parts + 1):
                bytes_before_part = (part_number - 1) * part_size
                current_part_size = min(part_size, total_size - bytes_before_part)
                presign = client.presign_part(state.upload_id, state.key, part_number)
                body = UploadProgressBody(handle, current_part_size, state, part_number, total_parts, bytes_before_part, total_size)
                # PUT goes directly to the presigned storage URL without an Agent API key.
                put_response = requests.put(presign["presignedUrl"], data=body, headers={"Content-Type": "video/mp4"}, timeout=300)
                if not 200 <= put_response.status_code < 300:
                    raise UserFacingError(f"Failed to upload part {part_number}: HTTP {put_response.status_code}")
                progress = 8 + int(32 * part_number / total_parts)
                emit(state, "progress", "uploading", progress, f"Uploaded {part_number}/{total_parts} parts.")

    complete = client.complete_upload(state.upload_id, state.key)
    if not complete.get("success") or complete.get("status") != "completed":
        raise UserFacingError("Server did not confirm upload completion.")
    emit(state, "progress", "upload_completed", 42, "Video upload completed.")


def create_or_reuse_task(client: SoulDubClient, state: RuntimeState, config: dict[str, Any], duration: int, speaker_count: int) -> None:
    """Create a translation task or reuse an existing same-language task."""
    # Bind the idempotency key to this create intent and keep it ASCII-safe for HTTP headers.
    state.idempotency_key = stable_ascii_idempotency_key(state)
    body = {
        "fileId": state.file_id,
        "videoDurationSeconds": duration,
        "checksumSha256": state.checksum_sha256,
        "sourceLanguage": state.source_language,
        "targetLanguage": state.target_language,
        "speakerCount": speaker_count,
        "allowDynamicDuration": bool(config.get("allow_dynamic_duration", True)),
    }
    try:
        data = client.create_task(body, state.idempotency_key)
    except TransientApiError as exc:
        if exc.code == "CONCURRENCY_LIMIT_REACHED":
            emit(state, "warning", "task_created", 45, "Account concurrency limit reached; retrying later.", retry_after_seconds=30)
            time.sleep(30)
            data = client.create_task(body, state.idempotency_key)
        else:
            raise
    if data.get("_existingTask"):
        state.task_id = data["existingTaskId"]
        emit(state, "warning", "task_created", 48, "Existing task detected for the same language pair; tracking that task instead.")
    else:
        state.task_id = data["taskId"]
        emit(state, "progress", "task_created", 48, "Translation task created.", credits_consumed=data.get("creditsConsumed"))


def poll_task(client: SoulDubClient, state: RuntimeState, max_interval: int) -> None:
    """Poll the translation task until a terminal status."""
    intervals = [2, 5, 10, 20, max(1, min(30, max_interval))]
    attempt = 0
    while True:
        time.sleep(intervals[min(attempt, len(intervals) - 1)])
        attempt += 1
        data = client.get_task(state.task_id or "")
        status = data.get("status")
        progress = int(data.get("progress") or 0)
        state.status = status or "unknown"
        emit(state, "progress", "task_processing", max(50, min(90, progress)), f"Video translation is processing; current status: {status}.", task_status=status)
        if status == "completed":
            emit(state, "progress", "downloading", 92, "Translation completed; starting result download.")
            return
        if status in {"failed", "cancelled"}:
            raise UserFacingError(data.get("errorMessage") or f"Task status is {status}.")


def download_results(client: SoulDubClient, state: RuntimeState, config: dict[str, Any]) -> None:
    """Download translated result files."""
    state.output_dir.mkdir(parents=True, exist_ok=True)

    variants = config.get("download_subtitles") or ["translated", "bilingual"]
    for variant in variants:
        response = client.subtitle_response(state.task_id or "", str(variant))
        subtitle_path = unique_file(state.output_dir / f"{variant}.srt")
        subtitle_path.write_bytes(response.content)
        state.files[f"{variant}_srt"] = str(subtitle_path)
    emit(state, "progress", "downloading", 94, "Subtitle files downloaded.")

    video_path = unique_file(state.output_dir / "result.mp4")
    last_error:Exception | None = None
    max_api_retries = clamped_int(config.get("max_api_retries"), default=5, minimum=1)
    for attempt in range(1, max_api_retries + 1):
        try:
            # Media URLs may expire or fail once; fetch a fresh URL on every retry.
            video_info = client.get_file(state.task_id or "", "video")
            with requests.get(video_info["url"], stream=True, timeout=(30, 300)) as response:
                if response.status_code >= 400:
                    raise UserFacingError(f"Failed to download result video: HTTP {response.status_code}")
                with video_path.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            handle.write(chunk)
            last_error = None
            break
        except Exception as exc:
            last_error = exc
            wait = min(30, 2**attempt)
            emit(state, "warning", "downloading", 92, f"Result video download failed; waiting before retry: {exc}", retry_after_seconds=wait, attempt=attempt)
            time.sleep(wait)
    if last_error is not None:
        raise UserFacingError(f"Result video download failed repeatedly: {sanitize_error_message(str(last_error))}")
    state.files["video"] = str(video_path)
    emit(state, "progress", "downloading", 98, "Translated video downloaded.")


def cmd_translate(args: argparse.Namespace) -> int:
    """Run the full video translation command."""
    config, _ = load_config()
    video_path = validate_video(args.video)
    state = make_run_state(config, video_path, args.source_language, args.target_language)
    try:
        emit(state, "started", "validating", 0, "Starting SoulDub video translation task.")
        api_key = validate_api_key(config)
        speaker_count = int(args.speaker_count)
        if speaker_count < 0 or speaker_count > 15:
            raise UserFacingError("speaker-count must be between 0 and 15; 0 means auto-detect.")
        emit(state, "progress", "reading_config", 2, "Config loaded; validating video and languages.")
        languages = load_languages()
        state.source_language = resolve_language(args.source_language, languages, "source")
        state.target_language = resolve_language(args.target_language, languages, "target")
        duration = video_duration_seconds(video_path)
        state.checksum_sha256 = sha256_file(video_path)
        emit(state, "progress", "validating", 6, "Video and language parameters validated.", video_duration_seconds=duration)

        client = SoulDubClient(str(config.get("api_base") or DEFAULT_API_BASE), api_key, state)
        upload_video(client, state, video_path, int(config.get("upload_part_size_mib") or 8), config.get("upload_concurrency"))
        create_or_reuse_task(client, state, config, duration, speaker_count)
        poll_task(client, state, int(config.get("max_poll_interval_seconds") or 30))
        download_results(client, state, config)
        state.status = "completed"
        emit(state, "completed", "completed", 100, "SoulDub video translation completed.")
        print_json({"ok": True, "run_id": state.run_id, "output_dir": str(state.output_dir), "files": state.files, "state_path": str(state.state_path)})
        return 0
    except Exception as exc:
        state.status = "failed"
        error_message = sanitize_error_message(str(exc))
        emit(state, "error", "failed", state.progress, error_message)
        print_json({"ok": False, "run_id": state.run_id, "error": error_message, "state_path": str(state.state_path), "output_dir": str(state.output_dir)})
        return 1


def cmd_download(args: argparse.Namespace) -> int:
    """Continue downloading results from an existing state.json file."""
    config, _ = load_config()
    state = load_state_from_file(Path(args.state).expanduser().resolve())
    try:
        api_key = validate_api_key(config)
        if not state.task_id:
            raise UserFacingError("state.json is missing taskId; cannot continue download.")
        client = SoulDubClient(str(config.get("api_base") or DEFAULT_API_BASE), api_key, state)
        emit(state, "progress", "downloading", max(state.progress, 92), "Continuing result download for the completed task.")
        download_results(client, state, config)
        state.status = "completed"
        emit(state, "completed", "completed", 100, "SoulDub video translation results downloaded.")
        print_json({"ok": True, "run_id": state.run_id, "output_dir": str(state.output_dir), "files": state.files, "state_path": str(state.state_path)})
        return 0
    except Exception as exc:
        state.status = "failed"
        error_message = sanitize_error_message(str(exc))
        emit(state, "error", "failed", state.progress, error_message)
        print_json({"ok": False, "run_id": state.run_id, "error": error_message, "state_path": str(state.state_path), "output_dir": str(state.output_dir)})
        return 1


def cmd_auth_status(args: argparse.Namespace) -> int:
    """Print current authentication status without exposing the full API key."""
    config, config_path = load_config()
    api_key = str(config.get("souldub_api_key") or "").strip()
    source = str(config.get("_api_key_source") or "missing")
    payload: dict[str, Any] = {
        "ok": True,
        "authenticated": bool(api_key),
        "source": source,
        "config_path": str(config_path),
    }
    if api_key:
        payload["api_key"] = redacted_secret(api_key)
    else:
        payload["next_step"] = f"Open {USER_CONFIG}, set souldub_api_key, save the file, then retry."
    print_json(payload)
    return 0


def cmd_resolve_language(args: argparse.Namespace) -> int:
    """Resolve and validate a SoulDub language code or registered name."""
    languages = load_languages()
    try:
        match = find_language(args.text, languages, args.mode)
        print_json({"ok": True, "mode": args.mode, "input": args.text, **match})
        return 0
    except UserFacingError as exc:
        print_json(
            {
                "ok": False,
                "mode": args.mode,
                "input": args.text,
                "error": str(exc),
                "examples": language_examples(languages, args.mode),
            }
        )
        return 1


def cmd_status(args: argparse.Namespace) -> int:
    """Read state.json and return the current status."""
    state_path = Path(args.state).expanduser().resolve()
    if not state_path.exists():
        raise UserFacingError(f"State file does not exist: {state_path}")
    print_json(json.loads(state_path.read_text(encoding="utf-8")))
    return 0


def cmd_list_runs(args: argparse.Namespace) -> int:
    """List recent saved runs."""
    config, _ = load_config()
    runs_dir = state_root(config) / "runs"
    runs:list[dict[str, Any]] = []
    for state_file in sorted(runs_dir.glob("*/state.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        runs.append(
            {
                "run_id": data.get("runId"),
                "state_path": str(state_file),
                "source_video": data.get("sourceVideo"),
                "target_language": data.get("targetLanguageText") or data.get("targetLanguage"),
                "stage": data.get("stage"),
                "progress": data.get("progress"),
                "updated_at": data.get("updatedAt"),
                "output_dir": data.get("outputDir"),
            }
        )
    print_json({"ok": True, "runs_dir": str(runs_dir), "runs": runs[:20]})
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description="SoulDub video translation helper.")
    sub = parser.add_subparsers(dest="command", required=True)

    auth = sub.add_parser("auth", help="Manage SoulDub API authentication.")
    auth_sub = auth.add_subparsers(dest="auth_command", required=True)

    auth_status = auth_sub.add_parser("status", help="Show current authentication status without printing the full API Key.")
    auth_status.set_defaults(func=cmd_auth_status)

    translate = sub.add_parser("translate", help="Upload a local MP4, create a SoulDub translation task, and download results.")
    translate.add_argument("--video", required=True, help="Absolute path to local MP4 file.")
    translate.add_argument("--source-language", default="auto", help="Source language text, default auto.")
    translate.add_argument("--target-language", required=True, help="Target language text, such as English, Japanese, Chinese, 日语, 中文, or 粤语.")
    translate.add_argument("--speaker-count", type=int, default=0, help="Speaker count 0..15; 0 means auto detect.")
    translate.set_defaults(func=cmd_translate)

    resolve = sub.add_parser("resolve-language", help="Resolve and validate a SoulDub language code or name.")
    resolve.add_argument("--mode", required=True, choices=["source", "target"], help="Resolve against source or target language list.")
    resolve.add_argument("--text", required=True, help="Language code or name to resolve, such as ja, 日语, Japanese.")
    resolve.set_defaults(func=cmd_resolve_language)

    status = sub.add_parser("status", help="Read a saved state.json file.")
    status.add_argument("--state", required=True, help="Path to state.json.")
    status.set_defaults(func=cmd_status)

    list_runs = sub.add_parser("list-runs", help="List recent runs from configured state directory.")
    list_runs.set_defaults(func=cmd_list_runs)

    download = sub.add_parser("download", help="Download results for an existing completed task from state.json.")
    download.add_argument("--state", required=True, help="Path to state.json.")
    download.set_defaults(func=cmd_download)
    return parser


def main() -> int:
    """Script entrypoint."""
    configure_text_streams()
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except UserFacingError as exc:
        print_json({"ok": False, "error": sanitize_error_message(str(exc))})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
