#!/usr/bin/env python3
"""
charset-fix helper: Test and demonstrate Windows encoding fixes.

Usage:
    python3 scripts/fix.py check        # Check current encoding status
    python3 scripts/fix.py test         # Run encoding test
"""

import subprocess
import sys
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def check():
    """Check current encoding state."""
    print("=== Encoding Check ===")
    
    # System code page
    r = subprocess.run(['powershell.exe', '-NoProfile', '-Command', 'chcp'],
                       capture_output=True, text=True, encoding='gbk')
    print(f"System code page: {r.stdout.strip()}")
    
    # Python encoding
    print(f"Python stdout encoding: {sys.stdout.encoding}")
    
    # Direct echo test
    print("\n=== Test Results ===")
    print("echo 中文测试 → 中文测试 (should be normal)")
    
    # Python test
    print("Python print('中文测试') → ", end="")
    print('中文测试')
    print("  ✅ If you see '中文测试' above, PYTHONIOENCODING is working")


def test():
    """Run full encoding test."""
    print("=== Charset Fix Test Suite ===\n")
    
    # 1. Python test
    print("1️⃣  Python test:")
    print("   ", end="")
    print('中文测试成功 ✅')
    
    # 2. PowerShell test
    print("\n2️⃣  PowerShell test:")
    r = subprocess.run([
        'powershell.exe', '-NoProfile', '-Command',
        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Write-Host '中文测试成功 ✅'"
    ], capture_output=True, text=True, encoding='utf-8')
    print(f"   {r.stdout.strip()}")
    
    # 3. System info (via cmd bridge)
    print("\n3️⃣  Windows system info (via cmd bridge):")
    r = subprocess.run(['cmd.exe', '/c', 'ver'],
                       capture_output=True, text=True, encoding='gbk')
    print(f"   {r.stdout.strip()}")
    
    print("\n✅ All tests complete")


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == 'check':
        check()
    elif sys.argv[1] == 'test':
        test()
    else:
        print(f"Usage: {sys.argv[0]} [check|test]")
