---
name: souldub-video-translate
description: Translate, dub, or localize local MP4 videos with SoulDub AI video translation and original-voice dubbing. Use when the user asks to translate a video into another language or Chinese dialect, AI dub an MP4, localize video content, generate translated or bilingual SRT subtitles, create a SoulDub video translation task, track long-running translation progress, or download translated video results.
license: MIT
---

# SoulDub Original-Voice Video Translation

Use this skill to translate local MP4 videos with SoulDub. Let the scripts handle upload, task creation, polling, result download, saved state, and retry behavior. The agent should understand the user's intent, collect missing parameters, call the scripts, report progress, and explain the final result.

Runtime requirements: Python 3.11+, `uv`, network access to the SoulDub API, read access to the source video, and write access to the output directory. The scripts declare dependencies with PEP 723 and must be run with `uv run`; do not call `python scripts/video_translation.py` directly.

## Parameter Collection

Always confirm these parameters from the user request:

- Source video absolute path: must be a local `.mp4` file.
- Target language: accept natural language names such as `English`, `Spanish`, `Chinese`, `Cantonese`, `日语`, `中文`, or `粤语`. Do not require the user to provide language codes such as `en` or `zh`.

Optional parameters:

- Source language: default `auto`; the user may also provide natural language names such as `English`, `Japanese`, `Chinese`, `日语`, or `中文`.
- Speaker count: default `0`; allowed range is `0..15`, where `0` means auto-detect.

The target language must not be `auto`. `references/languages.json` is the SoulDub supported-language registry. It contains only `code`, Chinese name, and English name fields; it does not maintain arbitrary aliases. The agent may understand language names in any user language, but before calling `translate` it should normalize the language to a SoulDub language code or a registered English/Chinese name, then validate it with `resolve-language`.

Language validation examples:

```bash
uv run scripts/video_translation.py resolve-language --mode target --text ja
uv run scripts/video_translation.py resolve-language --mode target --text Japanese
uv run scripts/video_translation.py resolve-language --mode target --text 日语
uv run scripts/video_translation.py resolve-language --mode source --text auto
```

If the user says a language name in another language, such as `일본어`, `japonés`, `japonais`, or `日文`, first understand it as `ja`, then validate with `--text ja`. After validation succeeds, prefer the returned `code` for `--source-language` or `--target-language`.

If language validation fails, ask the user to choose a supported language or describe the language another way. Do not force the user to provide a language code.

## Configuration

Before first use, check authentication:

```bash
uv run scripts/video_translation.py auth status
```

If no API key is configured, the script creates this user-level config file:

```text
~/.souldub/souldub.config.yaml
```

The user must create an API key at `https://www.souldub.ai/en/settings/apikeys`, set `souldub_api_key` in the config file, and save it. CI or temporary runs may use the `SOULDUB_API_KEY` environment variable.

Authentication precedence:

1. `SOULDUB_API_KEY` environment variable
2. User config at `~/.souldub/souldub.config.yaml`

User config example:

```yaml
api_base: "https://xxx.com/api/v1"
souldub_api_key: "your-agent-api-key"
```

## Translation Workflow

Agents should start long-running jobs in background mode by default, so the session remains responsive and can report progress. Run commands from the skill directory:

```bash
uv run scripts/background_translate.py start --video <absolute-mp4-path> --target-language <language-name>
```

Common optional parameters:

```bash
uv run scripts/background_translate.py start --video <absolute-mp4-path> --source-language auto --target-language English --speaker-count 0
```

When the start command succeeds, it returns JSON immediately. If the JSON includes `state_path`, remember `pid`, `state_path`, `output_dir`, `stdout_path`, and `stderr_path`, then tell the user that the job has started in the background. If the JSON status is `started_without_state_yet`, remember `pid`, `stdout_path`, and `stderr_path`, then wait briefly and read `stderr_path` until the first progress event provides `state_path`. The background process continues by calling the main script to:

- Read config and obtain the API key by authentication precedence.
- Validate the MP4 file and calculate `videoDurationSeconds`.
- Calculate SHA-256 and send it as `checksumSha256` when creating the task.
- Upload the video, create the translation task, and use a stable `Idempotency-Key` for safe retry.
- Poll with `2s -> 5s -> 10s -> 20s -> 30s` backoff.
- Download `result.mp4`, `translated.srt`, and `bilingual.srt`.
- Append a numeric suffix if a destination file already exists, avoiding silent overwrite.

If the current agent environment is not suitable for background processes, or if manual debugging is needed, run the main script in the foreground:

```bash
uv run scripts/video_translation.py translate --video <absolute-mp4-path> --source-language auto --target-language English --speaker-count 0
```

Default output directory:

```text
<source-video-directory>/souldub_outputs/<timestamp>-<filename-stem>/
```

Default state directory:

```text
platformdirs.user_state_dir(".souldub")/runs/<run-id>/
```

The state directory stores only `state.json` and `progress.log`. It must not store API keys, upload presigned URLs, media download URLs, or temporary signature parameters.

## Progress Reporting

Script stdout prints only the final JSON result. Script stderr prints JSONL progress events. The agent should not repeat every JSONL event to the user.

Reporting rules:

- Report once immediately after the background start succeeds, and remember `run_id`, `state_path`, `output_dir`, and `pid`.
- Report concise updates when the stage changes.
- During `uploading`, run `status --state <state-json-path>` about every 10 seconds, but report only when the stage or progress changes.
- During `task_processing`, run `status --state <state-json-path>` about every 60 seconds, but report only when the stage, status, or progress changes.
- Report immediately when the job completes or fails.
- For rate limits or concurrency limits, explain that the script is waiting for service-side limits to clear. Do not describe it as stuck.

Stages:

```text
validating
reading_config
uploading
upload_completed
task_created
task_processing
downloading
completed
failed
```

## User Status Follow-Up

If the user asks for status, whether the translation is done, or where the job is:

1. If the current session has `state_path`, run:

```bash
uv run scripts/video_translation.py status --state <state-json-path>
```

2. If `state_path` is unknown, run:

```bash
uv run scripts/video_translation.py list-runs
```

Then choose the most likely run by source video path, target language, update time, or `run_id`, and run `status --state <state-json-path>`. If multiple candidates remain and there is no reliable choice, ask the user to confirm.

3. If `status` cannot read the state file but the current session has `stderr_path`, read the most recent JSONL progress events and summarize the stage, progress, and output directory.

If the task completed but local download failed, continue downloading with the same `state_path`. Do not upload again or create another task:

```bash
uv run scripts/video_translation.py download --state <state-json-path>
```

The continuation command refreshes temporary media URLs and saves subtitle files first. If the media gateway is temporarily unreachable, explain the video download failure and still report any subtitle paths that were saved successfully.

## Results and Failures

On success, tell the user the local file paths, especially:

- Translated video: `result.mp4`
- Target-language subtitles: `translated.srt`
- Bilingual subtitles: `bilingual.srt`
- Output directory: `output_dir`

Additionally, notify the user that they can visit https://www.souldub.ai/en/dashboard/projects and open the video dubbing editor to further edit subtitle segments, audio segments.

Common failure handling:

- `UNAUTHORIZED`, `API_KEY_INVALID`, `API_KEY_EXPIRED`, `API_KEY_REVOKED`: ask the user to check the API key.
- `INSUFFICIENT_CREDITS`: explain that credits are insufficient; do not retry automatically.
- `INVALID_LANGUAGE`: ask the user to choose a supported language.
- `INVALID_SPEAKER_COUNT`: explain that speaker count must be `0..15`.
- `RATE_LIMITED`: the script waits according to `Retry-After`.
- `CONCURRENCY_LIMIT_REACHED`: the script backs off and waits; do not retry aggressively.

Read `references/agent-api.md` for detailed API behavior when needed. Read `references/languages.json` for the supported-language registry.
