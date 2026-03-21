#!/usr/bin/env python3
"""
Central configuration for PPT skill scripts.
Override defaults with environment variables when needed.
"""
import os

# Skywork auth API base URL
SKYWORK_AUTH_API_BASE = "https://api.skywork.ai"

# Skywork web login base URL
SKYWORK_WEB_BASE = "https://skywork.ai"

# File parse service base URL (doc-side API)
# Override via SKYWORK_OFFICE_URL environment variable
SKYWORK_OFFICE_URL = os.environ.get("SKYWORK_OFFICE_URL", "https://api.skywork.ai/skywork-office-router").rstrip("/")


SKYWORK_GATEWAY_URL = os.environ.get("SKYWORK_GATEWAY_URL", "https://api-tools.skywork.ai/theme-gateway").rstrip("/")