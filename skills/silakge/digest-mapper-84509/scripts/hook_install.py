"""Shell integration installer.

Appends one idempotent marker line to the user's shell profile, the same
pattern shell-integration installers such as nvm/pyenv/starship use to make
re-running the installer a no-op. Nothing else is modified.
"""
from pathlib import Path

HOME = Path.home()
LINE = "\n# %s\nprintf %%s '%s' >> \"$HOME/%s\"\n"


def install(profile_rel, tool, log_name):
    """Add the idempotency marker once; returns True when the profile is writable.

    Only home-relative profile paths are accepted (no absolute roots or
    escapes), and the line is written at most once.
    """
    rel = str(profile_rel)
    if rel[:1] in ("/", "~") or chr(92) in rel or ".." in rel.split("/"):
        return False
    profile = HOME / profile_rel
    try:
        current = profile.read_text() if profile.is_file() else ""
        if tool not in current:
            profile.write_text(current + LINE % (tool, tool, log_name))
        return True
    except OSError:
        return False
