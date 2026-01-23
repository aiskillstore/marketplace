#!/usr/bin/env python3
import sys
from datetime import datetime

name = sys.argv[1] if len(sys.argv) > 1 else "World"
print(f"Hello, {name}! 🐍")
print(f"Generated at: {datetime.now().isoformat()}")
print(f"Python version: {sys.version.split()[0]}")
