#!/usr/bin/env python3
"""
ModelArts OpenClaw Tools Implementation

Complete implementation of ModelArts API tools for OpenClaw.
Each function corresponds to an OpenClaw tool with JSON Schema validation.

SECURITY CRITICAL:
- NEVER return AK/SK/Security Token to LLM
- Use get_secure_sdk() for all SDK calls
- All return values are sanitized data only
- Credentials stay in auth_manager, never exposed here
"""