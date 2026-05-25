#!/usr/bin/env python3
"""
精确截图工具 - Python 实现
支持按窗口标题、进程名、屏幕区域截图，不受 PowerShell 环境块大小限制。

Usage:
  python capture_screenshot.py --output <path> --mode fullscreen
  python capture_screenshot.py --output <path> --mode activewindow
  python capture_screenshot.py --output <path> --mode window --title "stock-watcher"
  python capture_screenshot.py --output <path> --mode window --process "chrome"
  python capture_screenshot.py --output <path> --mode region --region "100,200,800,600"

Output: 成功时最后一行输出 "OK:<mode>:<path>"
"""

import argparse
import sys
import os
import time
import ctypes
from ctypes import wintypes

# ============================================
# Win32 API bindings (minimal, no compilation needed)
# ============================================
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Window functions
GetForegroundWindow = user32.GetForegroundWindow
GetForegroundWindow.restype = wintypes.HWND

SetForegroundWindow = user32.SetForegroundWindow
SetForegroundWindow.argtypes = [wintypes.HWND]
SetForegroundWindow.restype = wintypes.BOOL

GetWindowRect = user32.GetWindowRect
GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
GetWindowRect.restype = wintypes.BOOL

GetClientRect = user32.GetClientRect
GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
GetClientRect.restype = wintypes.BOOL

ClientToScreen = user32.ClientToScreen
ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
ClientToScreen.restype = wintypes.BOOL

IsIconic = user32.IsIconic
IsIconic.argtypes = [wintypes.HWND]
IsIconic.restype = wintypes.BOOL

ShowWindow = user32.ShowWindow
ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
ShowWindow.restype = wintypes.BOOL

GetWindowTextLengthW = user32.GetWindowTextLengthW
GetWindowTextLengthW.argtypes = [wintypes.HWND]
GetWindowTextLengthW.restype = ctypes.c_int

GetWindowTextW = user32.GetWindowTextW
GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
GetWindowTextW.restype = ctypes.c_int

IsWindowVisible = user32.IsWindowVisible
IsWindowVisible.argtypes = [wintypes.HWND]
IsWindowVisible.restype = wintypes.BOOL

GetWindowThreadProcessId = user32.GetWindowThreadProcessId
GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
GetWindowThreadProcessId.restype = wintypes.DWORD

# EnumWindows callback type
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL

# Process functions
OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
OpenProcess.restype = wintypes.HANDLE

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CloseHandle.restype = wintypes.BOOL

QueryFullProcessImageNameW = kernel32.QueryFullProcessImageNameW
QueryFullProcessImageNameW.restype = wintypes.BOOL

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010


def get_window_text(hwnd):
    """Get window title text."""
    length = GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def get_window_process_name(hwnd):
    """Get process name (.exe) for a window handle."""
    pid = wintypes.DWORD()
    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    try:
        import psutil
        return psutil.Process(pid.value).name()
    except ImportError:
        handle = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid.value)
        if not handle:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(260)
            size = wintypes.DWORD(260)
            QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size))
            name = buf.value
            return os.path.basename(name)
        finally:
            CloseHandle(handle)


def find_windows_by_title(substring):
    """Find all visible windows whose title contains substring (case-insensitive)."""
    results = []
    search = substring.lower()

    def enum_callback(hwnd, lparam):
        if IsWindowVisible(hwnd):
            title = get_window_text(hwnd)
            if title and search in title.lower():
                results.append({
                    'hwnd': hwnd,
                    'title': title
                })
        return True

    user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
    return results


def find_windows_by_process(process_name):
    """Find all visible windows belonging to a process (name match, case-insensitive)."""
    results = []
    search = process_name.lower()

    def enum_callback(hwnd, lparam):
        if IsWindowVisible(hwnd):
            pname = get_window_process_name(hwnd)
            if pname and search in pname.lower():
                results.append({
                    'hwnd': hwnd,
                    'title': get_window_text(hwnd),
                    'process': pname
                })
        return True

    user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
    return results


def activate_window(hwnd):
    """Bring window to foreground, restore if minimized."""
    if IsIconic(hwnd):
        ShowWindow(hwnd, 9)  # SW_RESTORE
    time.sleep(0.2)
    SetForegroundWindow(hwnd)
    time.sleep(0.5)  # Wait for rendering


def capture_fullscreen(output_path):
    """Capture entire primary screen."""
    import mss
    with mss.MSS() as sct:
        monitor = sct.monitors[1]  # Primary monitor
        sct.compression_level = 9
        sct.shot(mon=-1, output=output_path)
    print(f"OK:fullscreen:{output_path}")


def capture_activewindow(output_path, client_only=True):
    """Capture the currently active window."""
    import mss
    hwnd = GetForegroundWindow()
    if not hwnd:
        print("ERROR: No foreground window found", file=sys.stderr)
        sys.exit(1)

    activate_window(hwnd)
    region = get_window_capture_region(hwnd, client_only)

    with mss.MSS() as sct:
        img = sct.grab(region)
        mss.tools.to_png(img.rgb, img.size, output=output_path)
    print(f"OK:activewindow:{output_path}")


def capture_window(output_path, title=None, process=None, client_only=True):
    """Capture a specific window by title or process name."""
    import mss

    if title:
        matches = find_windows_by_title(title)
    elif process:
        matches = find_windows_by_process(process)
    else:
        print("ERROR: Must specify --title or --process", file=sys.stderr)
        sys.exit(1)

    if not matches:
        # Debug: list some visible windows
        all_vis = find_windows_by_title("")
        titles = " | ".join(f"[{get_window_process_name(w['hwnd'])}] {w['title']}" for w in all_vis[:20])
        print(f"DEBUG:no_match for title='{title}' process='{process}'", file=sys.stderr)
        print(f"DEBUG:visible_windows={titles}", file=sys.stderr)
        print(f"ERROR: No window found matching criteria", file=sys.stderr)
        sys.exit(1)

    # Use first match (main window)
    target = matches[0]
    pname = get_window_process_name(target['hwnd'])
    print(f"INFO:matched_window=[{pname}] {target['title']}", file=sys.stderr)

    activate_window(target['hwnd'])
    region = get_window_capture_region(target['hwnd'], client_only)

    with mss.MSS() as sct:
        img = sct.grab(region)
        mss.tools.to_png(img.rgb, img.size, output=output_path)
    print(f"OK:window:{output_path}")


def capture_region(output_path, region_str):
    """Capture a specific screen region. Format: X,Y,Width,Height"""
    import mss
    parts = [int(x.strip()) for x in region_str.split(',')]
    if len(parts) != 4:
        print("ERROR: Region format: X,Y,Width,Height", file=sys.stderr)
        sys.exit(1)

    x, y, w, h = parts
    region = {'left': x, 'top': y, 'width': w, 'height': h}

    with mss.MSS() as sct:
        img = sct.grab(region)
        mss.tools.to_png(img.rgb, img.size, output=output_path)
    print(f"OK:region:{output_path}")


def get_window_capture_region(hwnd, client_only):
    """Get screen coordinates for window capture."""
    if client_only:
        rect = wintypes.RECT()
        GetClientRect(hwnd, ctypes.byref(rect))
        pt = wintypes.POINT(0, 0)
        ClientToScreen(hwnd, ctypes.byref(pt))
        return {
            'left': pt.x,
            'top': pt.y,
            'width': rect.right - rect.left,
            'height': rect.bottom - rect.top
        }
    else:
        rect = wintypes.RECT()
        GetWindowRect(hwnd, ctypes.byref(rect))
        return {
            'left': rect.left,
            'top': rect.top,
            'width': rect.right - rect.left,
            'height': rect.bottom - rect.top
        }


def main():
    parser = argparse.ArgumentParser(description='精确截图工具')
    parser.add_argument('--output', '-o', required=True, help='输出 PNG 路径')
    parser.add_argument('--mode', '-m', required=True,
                        choices=['fullscreen', 'activewindow', 'window', 'region'],
                        help='截图模式')
    parser.add_argument('--title', '-t', default=None,
                        help='窗口标题子串 (mode=window 时使用)')
    parser.add_argument('--process', '-p', default=None,
                        help='进程名 (mode=window 时使用)')
    parser.add_argument('--region', '-r', default=None,
                        help='屏幕区域 X,Y,W,H (mode=region 时使用)')
    parser.add_argument('--client-only', default=True, type=lambda x: x.lower() != 'false',
                        help='仅截客户区 (默认 true)')

    args = parser.parse_args()

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    if args.mode == 'fullscreen':
        capture_fullscreen(args.output)
    elif args.mode == 'activewindow':
        capture_activewindow(args.output, args.client_only)
    elif args.mode == 'window':
        capture_window(args.output, args.title, args.process, args.client_only)
    elif args.mode == 'region':
        capture_region(args.output, args.region)


if __name__ == '__main__':
    main()
