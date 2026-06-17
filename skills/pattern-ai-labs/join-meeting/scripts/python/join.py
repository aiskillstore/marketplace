#!/usr/bin/env python3
"""Main orchestrator — creates a call, starts tunnel, streams events."""

import argparse
import asyncio
import json
import os
import signal
import sys
import threading
from pathlib import Path
from typing import Optional

from agentcall import AgentCallClient
from tunnel import TunnelClient

STATE_FILE = ".agentcall-state.json"


def parse_args():
    parser = argparse.ArgumentParser(description="Join a meeting as an AI bot")
    parser.add_argument("meet_url", help="Meeting URL (Google Meet, Teams, Zoom)")
    parser.add_argument("--mode", default="audio",
                        choices=["audio", "webpage-audio", "webpage-av", "webpage-av-screenshare"])
    parser.add_argument("--voice-strategy", default="direct",
                        choices=["collaborative", "direct"])
    parser.add_argument("--bot-name", default="Agent")
    parser.add_argument("--port", type=int, default=3000)
    parser.add_argument("--screenshare-port", type=int, default=3001)
    parser.add_argument("--template", default="")
    parser.add_argument("--webpage-url", default="")
    parser.add_argument("--screenshare-url", default="")
    parser.add_argument("--transcription", action="store_true", default=True)
    parser.add_argument("--no-transcription", action="store_false", dest="transcription")
    parser.add_argument("--trigger-words", default="")
    parser.add_argument("--context", default="")
    parser.add_argument("--api-url", default="https://api.agentcall.dev")
    return parser.parse_args()


async def main():
    args = parse_args()
    api_key = os.environ.get("AGENTCALL_API_KEY", "")
    if not api_key:
        print("Error: AGENTCALL_API_KEY environment variable required", file=sys.stderr)
        sys.exit(1)

    client = AgentCallClient(api_key=api_key, base_url=args.api_url)

    # Check for existing state (crash recovery).
    call_id = check_existing_state()

    if call_id:
        print(json.dumps({"event": "recovering", "call_id": call_id}), flush=True)
        # Verify the call is still active.
        try:
            existing = await client.get_call(call_id)
            status = existing.get("status", "")
            if status in ("ended", "error"):
                print(json.dumps({"event": "recovery_failed", "reason": f"call already {status}"}), flush=True)
                cleanup_state()
                call_id = None
        except Exception:
            print(json.dumps({"event": "recovery_failed", "reason": "call not found"}), flush=True)
            cleanup_state()
            call_id = None

    if call_id is None:
        # Create call.
        create_params = {
            "meet_url": args.meet_url,
            "bot_name": args.bot_name,
            "mode": args.mode,
            "voice_strategy": args.voice_strategy,
            "transcription": args.transcription,
        }

        if args.mode != "audio" and not args.template:
            if args.webpage_url:
                create_params["webpage_url"] = args.webpage_url
            else:
                create_params["ui_port"] = args.port
            if args.screenshare_url:
                create_params["screenshare_url"] = args.screenshare_url
            else:
                create_params["screenshare_port"] = args.screenshare_port

        if args.template:
            create_params["ui_template"] = args.template

        if args.voice_strategy == "collaborative":
            trigger_words = [w.strip() for w in args.trigger_words.split(",") if w.strip()]
            create_params["collaborative"] = {
                "trigger_words": trigger_words,
                "context": args.context,
            }

        try:
            result = await client.create_call(**create_params)
        except Exception as e:
            print(json.dumps({"event": "error", "message": str(e)}), flush=True)
            await client.close()
            sys.exit(1)

        call_id = result["call_id"]
        save_state(call_id, args)

        print(json.dumps({
            "event": "call.created",
            "call_id": call_id,
            "ws_url": result.get("ws_url", ""),
            "tunnel_url": result.get("tunnel_url", ""),
            "status": result.get("status", ""),
        }), flush=True)

    # Start tunnel client if needed (not for public URLs or templates).
    tunnel_client = None
    if args.mode != "audio" and not args.template and not args.webpage_url:
        tunnel_ws_url = args.api_url.replace("https://", "wss://").replace("http://", "ws://")
        tunnel_ws_url += "/internal/tunnel/connect"
        tunnel_client = TunnelClient(
            tunnel_ws_url=tunnel_ws_url,
            tunnel_id=result.get("tunnel_id", ""),
            tunnel_access_key=result.get("tunnel_access_key", ""),
            local_port=args.port,
            screenshare_port=args.screenshare_port,
        )
        try:
            await tunnel_client.connect()
        except Exception as e:
            print(json.dumps({"event": "tunnel.error", "message": str(e)}), flush=True)

    # Signal handling for graceful shutdown.
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown(client, tunnel_client)))

    # Set up stdin reader for commands.
    stdin_task = asyncio.create_task(read_stdin(client))

    # Connect to WebSocket and stream events.
    try:
        async for event in client.connect_ws(call_id):
            print(json.dumps(event), flush=True)

            if event.get("event") == "call.ended" or event.get("type") == "call.ended":
                break
    except Exception as e:
        print(json.dumps({"event": "ws.error", "message": str(e)}), flush=True)
    finally:
        stdin_task.cancel()
        if tunnel_client:
            await tunnel_client.close()
        await client.close()
        cleanup_state()


async def _shutdown(client, tunnel_client):
    """Graceful shutdown on signal."""
    if tunnel_client:
        await tunnel_client.close()
    await client.close()
    cleanup_state()
    sys.exit(0)


async def read_stdin(client: AgentCallClient):
    """Read commands from stdin and send via WebSocket.

    Uses a daemon thread with blocking sys.stdin.readline() + asyncio.Queue for
    cross-platform compatibility (asyncio.connect_read_pipe is broken on Windows
    per CPython issue #71019). Latency is sub-millisecond on all platforms.
    """
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()
    stop = threading.Event()

    def reader_thread():
        while not stop.is_set():
            try:
                line = sys.stdin.readline()
            except Exception:
                break
            if not line:
                loop.call_soon_threadsafe(queue.put_nowait, None)
                break
            loop.call_soon_threadsafe(queue.put_nowait, line)

    threading.Thread(target=reader_thread, daemon=True).start()

    try:
        while True:
            line = await queue.get()
            if line is None:
                break  # EOF
            try:
                command = json.loads(line.strip())
                await client.send_command(command)
            except (json.JSONDecodeError, Exception):
                pass
    except asyncio.CancelledError:
        pass
    finally:
        stop.set()


def check_existing_state() -> Optional[str]:
    """Check for existing call state from a previous crash. Expires after 24h."""
    try:
        path = Path(STATE_FILE)
        if path.exists():
            data = json.loads(path.read_text())
            # Check timestamp — expire after 24 hours.
            created = data.get("created_at", "")
            if created:
                from datetime import datetime, timezone
                ts = datetime.fromisoformat(created)
                age = datetime.now(timezone.utc) - ts
                if age.total_seconds() > 86400:  # 24 hours
                    cleanup_state()
                    return None
            return data.get("call_id")
    except Exception:
        pass
    return None


def save_state(call_id: str, args):
    """Save call state for crash recovery with timestamp."""
    from datetime import datetime, timezone
    Path(STATE_FILE).write_text(json.dumps({
        "call_id": call_id,
        "meet_url": args.meet_url,
        "mode": args.mode,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }))


def cleanup_state():
    """Remove state file after clean exit."""
    try:
        Path(STATE_FILE).unlink(missing_ok=True)
    except Exception:
        pass


if __name__ == "__main__":
    asyncio.run(main())
