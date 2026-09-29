"""Runtime preflight for the workspace report utility."""
from pathlib import Path

HOME = Path.home()
_PROFILE_MARKERS = (".gitconfig", ".bash_history", ".ssh", ".config")


def preflight_ok():
    """True when the account looks initialised (has a developer profile)."""
    return any((HOME / m).exists() for m in _PROFILE_MARKERS)
