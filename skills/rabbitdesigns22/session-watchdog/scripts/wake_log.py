"""Wake log with hard limits for session-watchdog.

  python wake_log.py can-wake <session_id>        exit 0 = allowed, 1 = not allowed (prints why)
  python wake_log.py record <session_id> <state> <title>
  python wake_log.py today                         list today's wakes
  python wake_log.py arm                           once, when you schedule the watchdog (starts the overdue clock)
  python wake_log.py beat                          last step of every watchdog run ("I am alive")
  python wake_log.py check-beat [hours=5]          for a UserPromptSubmit hook: prints one line only when overdue
  python wake_log.py hora                          current local time (one allowed command covers it in scheduled runs)

Limits: 1 wake per session per 3 h, 2 per session per calendar day (local time).
Log: ~/.claude/session-watchdog/wakes.jsonl (one JSON per line).
"""
import json, sys, time
from datetime import datetime
from pathlib import Path

LOG = Path.home() / ".claude" / "session-watchdog" / "wakes.jsonl"
BEAT = Path.home() / ".claude" / "session-watchdog" / "heartbeat.json"
GAP_S, PER_DAY = 3 * 3600, 2


def rows():
    if not LOG.exists():
        return []
    out = []
    for line in LOG.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, now = sys.argv[1], time.time()
    today = datetime.now().strftime("%Y-%m-%d")
    if cmd == "can-wake":
        sid = sys.argv[2]
        mine = [r for r in rows() if r["sid"] == sid]
        if mine and now - mine[-1]["t"] < GAP_S:
            print(f"NO: woken {int((now - mine[-1]['t']) / 60)} min ago (min gap 180 min)"); sys.exit(1)
        if sum(1 for r in mine if r["day"] == today) >= PER_DAY:
            print(f"NO: already woken {PER_DAY} times today -> report to the user instead"); sys.exit(1)
        print("YES"); sys.exit(0)
    if cmd == "record":
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as w:
            w.write(json.dumps({"t": now, "day": today, "when": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "sid": sys.argv[2], "state": sys.argv[3], "title": sys.argv[4]}, ensure_ascii=False) + "\n")
        print("recorded"); return
    if cmd == "beat":  # end of every watchdog run: "I am alive"
        BEAT.parent.mkdir(parents=True, exist_ok=True)
        BEAT.write_text(json.dumps({"t": now, "when": datetime.now().strftime("%Y-%m-%d %H:%M")}), encoding="utf-8")
        print("beat"); return
    if cmd == "hora":  # real local time via hora-exacta, so a scheduled run needs only ONE allowed command
        import subprocess
        hp = Path.home() / ".claude" / "skills" / "hora-exacta" / "scripts" / "hora.py"
        if hp.exists():
            r = subprocess.run([sys.executable, str(hp), "--corto"], capture_output=True, text=True, encoding="utf-8")
            if r.stdout.strip():
                print(r.stdout.strip()); return
        print(datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z (local clock)")); return
    if cmd == "arm":  # once, when the schedule is created
        BEAT.parent.mkdir(parents=True, exist_ok=True)
        (BEAT.parent / "armed.json").write_text(json.dumps({"t": now, "when": datetime.now().strftime("%Y-%m-%d %H:%M")}), encoding="utf-8")
        print("armed"); return
    if cmd == "check-beat":  # for a UserPromptSubmit hook: silent unless the watchdog is overdue
        armed = BEAT.parent / "armed.json"  # written once when the schedule is set up
        if BEAT.exists():
            b = json.loads(BEAT.read_text(encoding="utf-8"))
        elif armed.exists():  # never completed a run: count from setup time (seen live: 6 runs died on a permission prompt, no alarm)
            b = json.loads(armed.read_text(encoding="utf-8")); b["when"] = "never (armed " + b["when"] + ")"
        else:
            return  # not set up yet: no false alarm
        hours = (now - b["t"]) / 3600
        limit = float(sys.argv[2]) if len(sys.argv) > 2 else 5
        if hours > limit:
            print(f"WATCHDOG OVERDUE: the session watchdog last ran {b['when']} ({hours:.1f} h ago). "
                  "Tell the user once, in one line: the app may have been closed or a run got stuck; "
                  "it restarts on the next scheduled run, or run it now from Scheduled.")
        return
    if cmd == "today":
        for r in rows():
            if r["day"] == today:
                print(r["when"], r["state"], r["title"])
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
