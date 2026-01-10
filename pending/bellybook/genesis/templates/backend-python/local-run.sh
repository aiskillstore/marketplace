#!/bin/bash

set -a
source .env.dev
set +a

uv run fastapi dev app/main.py --host 127.0.0.1 --port 12345
