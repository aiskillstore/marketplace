#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qryma Direct Run Version
Simplified version that directly accepts command line arguments and outputs results
"""
import argparse
import sys
import os

# Add scripts directory to Python path to ensure modules can be imported correctly
script_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(script_dir, 'scripts')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

try:
    from adapters.adapter import QrymaAdapter
except ImportError:
    # Fallback import method
    print("Warning: Using fallback import method", file=sys.stderr)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "adapter",
        os.path.join(scripts_dir, 'adapters', 'adapter.py')
    )
    adapter_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter_module)
    QrymaAdapter = adapter_module.QrymaAdapter


def main():
    parser = QrymaAdapter.create_parser()
    args = parser.parse_args()
    adapter = QrymaAdapter(api_key=getattr(args, "api_key", None))
    adapter.run(args)


def handler(event, context=None):
    """Handler function for platform integration"""
    api_key = event.get("api_key") if isinstance(event, dict) else None
    adapter = QrymaAdapter(api_key=api_key)
    return adapter.run(event)


if __name__ == "__main__":
    main()
