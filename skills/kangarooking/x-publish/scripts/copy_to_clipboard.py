#!/usr/bin/env python3
"""
Copy text to system clipboard for X tweet publishing.

Usage:
    # Copy text directly
    python copy_to_clipboard.py text "Tweet content here"

    # Copy text from file
    python copy_to_clipboard.py text --file /tmp/tweet.txt

Requirements:
    macOS: pip install pyobjc-framework-Cocoa
    Windows: pip install pyperclip
"""

import argparse
import os
import sys


def copy_text_to_clipboard_macos(text: str) -> bool:
    """Copy text to macOS clipboard using AppKit."""
    try:
        from AppKit import NSPasteboard, NSPasteboardTypeString

        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        pasteboard.setString_forType_(text, NSPasteboardTypeString)
        return True

    except ImportError as e:
        print(f"Error: Missing dependency: {e}", file=sys.stderr)
        print("Install with: pip install pyobjc-framework-Cocoa", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error copying text: {e}", file=sys.stderr)
        return False


def copy_text_to_clipboard_windows(text: str) -> bool:
    """Copy text to Windows clipboard."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        # Fallback to win32clipboard
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            finally:
                win32clipboard.CloseClipboard()
            return True
        except ImportError as e:
            print(f"Error: Missing dependency: {e}", file=sys.stderr)
            print("Install with: pip install pyperclip", file=sys.stderr)
            return False
    except Exception as e:
        print(f"Error copying text: {e}", file=sys.stderr)
        return False


def copy_text_to_clipboard_linux(text: str) -> bool:
    """Copy text to Linux clipboard using xclip or xsel."""
    try:
        import subprocess

        # Try xclip first
        try:
            process = subprocess.Popen(
                ['xclip', '-selection', 'clipboard'],
                stdin=subprocess.PIPE
            )
            process.communicate(text.encode('utf-8'))
            return process.returncode == 0
        except FileNotFoundError:
            pass

        # Try xsel
        try:
            process = subprocess.Popen(
                ['xsel', '--clipboard', '--input'],
                stdin=subprocess.PIPE
            )
            process.communicate(text.encode('utf-8'))
            return process.returncode == 0
        except FileNotFoundError:
            print("Error: Neither xclip nor xsel found. Install one of them.", file=sys.stderr)
            return False

    except Exception as e:
        print(f"Error copying text: {e}", file=sys.stderr)
        return False


def copy_text_to_clipboard(text: str) -> bool:
    """Copy text to clipboard (cross-platform)."""
    if sys.platform == 'darwin':
        return copy_text_to_clipboard_macos(text)
    elif sys.platform == 'win32':
        return copy_text_to_clipboard_windows(text)
    elif sys.platform.startswith('linux'):
        return copy_text_to_clipboard_linux(text)
    else:
        print(f"Error: Unsupported platform: {sys.platform}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description='Copy text to clipboard for X publishing')
    subparsers = parser.add_subparsers(dest='type', required=True)

    # Text subcommand
    text_parser = subparsers.add_parser('text', help='Copy text to clipboard')
    text_parser.add_argument('content', nargs='?', help='Text content')
    text_parser.add_argument('--file', '-f', help='Read text from file')

    args = parser.parse_args()

    if args.type == 'text':
        if args.file:
            if not os.path.exists(args.file):
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                sys.exit(1)
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        elif args.content:
            text = args.content
        else:
            # Read from stdin
            text = sys.stdin.read()

        success = copy_text_to_clipboard(text)
        if success:
            char_count = len(text)
            preview = text[:50] + '...' if len(text) > 50 else text
            preview = preview.replace('\n', ' ')
            print(f"Text copied to clipboard ({char_count} chars)")
            print(f"Preview: {preview}")
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
