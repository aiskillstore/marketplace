#!/usr/bin/env python3
"""Shared profile resolver for the STOW runtime.

This module is PACKAGED into the shipped skill. It is import-closed: it
imports only the Python standard library. It is the single runtime authority
on profile identity, aliasing, lock state, routing precedence data, and which
profile-gated lint checks are active under which profile. It does not inspect
request text or choose a profile by meaning. The data
lives in ``rules/profiles.json`` beside the packaged rule registry; this
module only loads and answers questions about it.

Check-gating semantics: a check name that appears in a profile's
``lint_checks`` map is profile-gated and runs only where the map says
``true``. A check name absent from the map is always-on and is never gated
by any profile.
"""

import json
import os
import sys

PROFILES_RELPATH = ("rules", "profiles.json")

DEFAULT_PROFILE = "stow-default"


class ProfileError(Exception):
    """Base class for profile resolution failures."""


class UnknownProfileError(ProfileError):
    """The requested profile id or alias does not exist."""


class LockedProfileError(ProfileError):
    """The requested profile exists but is locked and unavailable."""


def default_profiles_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, os.pardir, *PROFILES_RELPATH))


def load_profiles(path=None):
    """Load and index profiles.json. Raises on a missing or invalid file:
    unlike the advisory linter, profile identity is a contract surface."""
    path = path or default_profiles_path()
    with open(path, "rb") as handle:
        data = json.loads(handle.read().decode("utf-8"))
    index = {}
    for profile in data.get("profiles", []):
        index[profile["id"]] = profile
        for alias in profile.get("aliases", []):
            index[alias] = profile
    data["_index"] = index
    return data


def resolve(name, data=None):
    """Resolve a profile id or alias to its profile record.

    ``None`` resolves to the default profile. A locked profile raises
    :class:`LockedProfileError`; an unknown name raises
    :class:`UnknownProfileError`.
    """
    data = data or load_profiles()
    if name is None:
        name = DEFAULT_PROFILE
    record = data["_index"].get(name)
    if record is None:
        raise UnknownProfileError(
            "unknown profile %r; known: %s"
            % (name, ", ".join(sorted(p["id"] for p in data["profiles"]))))
    if record.get("locked"):
        raise LockedProfileError(
            "profile %r is locked and unavailable in this release"
            % record["id"])
    return record


def check_active(check, profile_record):
    """True when ``check`` runs under ``profile_record``.

    Profile-gated checks are the keys of ``lint_checks``; anything else is
    always-on.
    """
    gated = profile_record.get("lint_checks", {})
    if check in gated:
        return bool(gated[check])
    return True


def auto_order(data=None):
    """Return host/model routing precedence data, most specific first."""
    data = data or load_profiles()
    return list(data.get("auto_precedence", []))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 2 or argv[0] != "resolve":
        print("usage: profiles.py resolve <profile-id-or-alias>")
        return 1
    try:
        record = resolve(argv[1])
    except LockedProfileError as exc:
        print("locked: %s" % exc)
        return 2
    except UnknownProfileError as exc:
        print("unknown: %s" % exc)
        return 1
    print(record["id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
