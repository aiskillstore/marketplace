#!/usr/bin/env python3
"""Store and use API credentials through OS-backed secret stores."""

from __future__ import annotations

import argparse
import ctypes
import getpass
import os
import platform
import re
import shutil
import subprocess
import sys
from ctypes import wintypes


SERVICE_PREFIX = "api-guardian"
NAME_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")


class StoreError(RuntimeError):
    pass


def validate_name(name: str) -> str:
    if not NAME_RE.match(name):
        raise StoreError(
            "Credential names must be 1-80 chars: letters, digits, dot, underscore, colon, or hyphen."
        )
    return name


def target_name(name: str) -> str:
    return f"{SERVICE_PREFIX}:{validate_name(name)}"


def mask_secret(secret: str) -> str:
    if not secret:
        return "<empty>"
    if len(secret) <= 8:
        return "*" * len(secret)
    return f"{secret[:3]}...{secret[-4:]} ({len(secret)} chars)"


class SecretStore:
    def store(self, name: str, secret: str) -> None:
        raise NotImplementedError

    def get(self, name: str) -> str:
        raise NotImplementedError

    def delete(self, name: str) -> None:
        raise NotImplementedError

    def list(self) -> list[str]:
        return []


if platform.system() == "Windows":

    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]

    class CREDENTIALW(ctypes.Structure):
        _fields_ = [
            ("Flags", wintypes.DWORD),
            ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR),
            ("Comment", wintypes.LPWSTR),
            ("LastWritten", FILETIME),
            ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
            ("Persist", wintypes.DWORD),
            ("AttributeCount", wintypes.DWORD),
            ("Attributes", wintypes.LPVOID),
            ("TargetAlias", wintypes.LPWSTR),
            ("UserName", wintypes.LPWSTR),
        ]

    PCREDENTIALW = ctypes.POINTER(CREDENTIALW)
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    advapi32.CredWriteW.argtypes = [PCREDENTIALW, wintypes.DWORD]
    advapi32.CredWriteW.restype = wintypes.BOOL
    advapi32.CredReadW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.POINTER(PCREDENTIALW),
    ]
    advapi32.CredReadW.restype = wintypes.BOOL
    advapi32.CredDeleteW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
    advapi32.CredDeleteW.restype = wintypes.BOOL
    advapi32.CredFree.argtypes = [wintypes.LPVOID]
    advapi32.CredFree.restype = None
    advapi32.CredEnumerateW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(ctypes.POINTER(PCREDENTIALW)),
    ]
    advapi32.CredEnumerateW.restype = wintypes.BOOL

    CRED_TYPE_GENERIC = 1
    CRED_PERSIST_LOCAL_MACHINE = 2

    class WindowsCredentialStore(SecretStore):
        def store(self, name: str, secret: str) -> None:
            encoded = secret.encode("utf-16-le")
            blob = (ctypes.c_byte * len(encoded)).from_buffer_copy(encoded)
            cred = CREDENTIALW()
            cred.Type = CRED_TYPE_GENERIC
            cred.TargetName = target_name(name)
            cred.CredentialBlobSize = len(encoded)
            cred.CredentialBlob = ctypes.cast(blob, ctypes.POINTER(ctypes.c_byte))
            cred.Persist = CRED_PERSIST_LOCAL_MACHINE
            cred.UserName = getpass.getuser()
            if not advapi32.CredWriteW(ctypes.byref(cred), 0):
                raise StoreError(f"CredWriteW failed with error {ctypes.get_last_error()}.")

        def get(self, name: str) -> str:
            credential = PCREDENTIALW()
            if not advapi32.CredReadW(target_name(name), CRED_TYPE_GENERIC, 0, ctypes.byref(credential)):
                raise StoreError(f"No credential found for '{name}'.")
            try:
                size = credential.contents.CredentialBlobSize
                blob = ctypes.string_at(credential.contents.CredentialBlob, size)
                return blob.decode("utf-16-le")
            finally:
                advapi32.CredFree(credential)

        def delete(self, name: str) -> None:
            if not advapi32.CredDeleteW(target_name(name), CRED_TYPE_GENERIC, 0):
                error = ctypes.get_last_error()
                if error != 1168:
                    raise StoreError(f"CredDeleteW failed with error {error}.")

        def list(self) -> list[str]:
            count = wintypes.DWORD()
            credentials = ctypes.POINTER(PCREDENTIALW)()
            pattern = f"{SERVICE_PREFIX}:*"
            if not advapi32.CredEnumerateW(pattern, 0, ctypes.byref(count), ctypes.byref(credentials)):
                return []
            try:
                names: list[str] = []
                for idx in range(count.value):
                    target = credentials[idx].contents.TargetName
                    if target.startswith(f"{SERVICE_PREFIX}:"):
                        names.append(target.split(":", 1)[1])
                return sorted(names)
            finally:
                advapi32.CredFree(credentials)


class MacOSKeychainStore(SecretStore):
    def _run(self, args: list[str], input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, input=input_text, text=True, capture_output=True, check=False)

    def store(self, name: str, secret: str) -> None:
        result = self._run(
            [
                "/usr/bin/security",
                "add-generic-password",
                "-a",
                getpass.getuser(),
                "-s",
                target_name(name),
                "-w",
                secret,
                "-U",
            ]
        )
        if result.returncode:
            raise StoreError(result.stderr.strip() or "Failed to store credential in Keychain.")

    def get(self, name: str) -> str:
        result = self._run(
            [
                "/usr/bin/security",
                "find-generic-password",
                "-a",
                getpass.getuser(),
                "-s",
                target_name(name),
                "-w",
            ]
        )
        if result.returncode:
            raise StoreError(f"No credential found for '{name}'.")
        return result.stdout.rstrip("\n")

    def delete(self, name: str) -> None:
        result = self._run(
            [
                "/usr/bin/security",
                "delete-generic-password",
                "-a",
                getpass.getuser(),
                "-s",
                target_name(name),
            ]
        )
        if result.returncode:
            raise StoreError("Keychain did not confirm credential deletion (the item may be missing or access denied).")


class LinuxSecretToolStore(SecretStore):
    def __init__(self) -> None:
        if not shutil.which("secret-tool"):
            raise StoreError(
                "secret-tool is required on Linux. Install libsecret-tools or use an OS keyring."
            )

    def store(self, name: str, secret: str) -> None:
        result = subprocess.run(
            ["secret-tool", "store", "--label", target_name(name), "service", SERVICE_PREFIX, "name", validate_name(name)],
            input=secret,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise StoreError(result.stderr.strip() or "Failed to store credential.")

    def get(self, name: str) -> str:
        result = subprocess.run(
            ["secret-tool", "lookup", "service", SERVICE_PREFIX, "name", validate_name(name)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise StoreError(f"No credential found for '{name}'.")
        return result.stdout.rstrip("\n")

    def delete(self, name: str) -> None:
        result = subprocess.run(
            ["secret-tool", "clear", "service", SERVICE_PREFIX, "name", validate_name(name)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise StoreError("Secret Service did not confirm credential deletion (the item may be missing or access denied).")


def get_store() -> SecretStore:
    system = platform.system()
    if system == "Windows":
        return WindowsCredentialStore()
    if system == "Darwin":
        return MacOSKeychainStore()
    if system == "Linux":
        return LinuxSecretToolStore()
    raise StoreError(f"Unsupported platform: {system}")


def read_secret(args: argparse.Namespace) -> str:
    sources = [bool(args.stdin), bool(args.from_env), args.value is not None]
    if sum(sources) > 1:
        raise StoreError("Choose only one secret source: prompt, --stdin, --from-env, or --value.")
    if args.stdin:
        return sys.stdin.read().rstrip("\n")
    if args.from_env:
        value = os.environ.get(args.from_env)
        if value is None:
            raise StoreError(f"Environment variable '{args.from_env}' is not set.")
        return value
    if args.value is not None:
        return args.value
    first = getpass.getpass("Secret: ")
    second = getpass.getpass("Confirm: ")
    if first != second:
        raise StoreError("Secret confirmation did not match.")
    return first


def cmd_store(args: argparse.Namespace) -> int:
    secret = read_secret(args)
    if not secret:
        raise StoreError("Refusing to store an empty secret.")
    get_store().store(args.name, secret)
    print(f"Stored '{args.name}' in the OS secret store.")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    secret = get_store().get(args.name)
    if args.reveal:
        print(secret)
    else:
        print(f"{args.name}: {mask_secret(secret)}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    if not args.command:
        raise StoreError("Provide a command after --.")
    secret = get_store().get(args.name)
    env = os.environ.copy()
    env[args.env_var] = secret
    result = subprocess.run(args.command, env=env, check=False)
    return result.returncode


def cmd_delete(args: argparse.Namespace) -> int:
    get_store().delete(args.name)
    print(f"Deleted '{args.name}' if it existed.")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    names = get_store().list()
    if names:
        for name in names:
            print(name)
    else:
        print("No credentials listed. This platform may not support enumeration.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Securely store and use API credentials.")
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    store = subparsers.add_parser("store", help="Store or replace a credential.")
    store.add_argument("name")
    store.add_argument("--stdin", action="store_true", help="Read secret from stdin.")
    store.add_argument("--from-env", help="Read secret from an environment variable.")
    store.add_argument("--value", help="Read secret from this argument. Avoid when possible.")
    store.set_defaults(func=cmd_store)

    get = subparsers.add_parser("get", help="Retrieve a credential.")
    get.add_argument("name")
    get.add_argument("--reveal", action="store_true", help="Print the raw secret.")
    get.set_defaults(func=cmd_get)

    run = subparsers.add_parser("run", help="Run a command with a credential in its environment.")
    run.add_argument("name")
    run.add_argument("env_var")
    run.add_argument("command", nargs=argparse.REMAINDER)
    run.set_defaults(func=cmd_run)

    delete = subparsers.add_parser("delete", help="Delete a credential.")
    delete.add_argument("name")
    delete.set_defaults(func=cmd_delete)

    list_cmd = subparsers.add_parser("list", help="List known credential names when supported.")
    list_cmd.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "command") and args.command and args.command[0] == "--":
        args.command = args.command[1:]
    try:
        return args.func(args)
    except StoreError as exc:
        print(f"api_guard: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
