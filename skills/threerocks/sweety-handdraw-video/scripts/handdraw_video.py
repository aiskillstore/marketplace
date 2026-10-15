#!/usr/bin/env python3
"""Entry point for a job-specific narrated hand-drawn video."""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['doctor', 'build', 'render', 'verify', 'finalize'])
    parser.add_argument('job', type=Path, help='Directory containing job.json')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--start', type=float, default=0.)
    parser.add_argument('--duration', type=float)
    parser.add_argument('--assets-only', action='store_true')
    arguments = parser.parse_args()
    if arguments.command == 'doctor':
        from video_job import inspect_environment
        report = inspect_environment(arguments.job)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report['ready'] else 1
    if arguments.command == 'build':
        from video_job import FilmBuilder
        FilmBuilder(arguments.job).build()
    elif arguments.command == 'render':
        from video_renderer import render_job
        render_job(arguments.job, arguments.start, arguments.duration, arguments.preview)
    elif arguments.command == 'verify':
        from video_verifier import verify_job
        verify_job(arguments.job, arguments.assets_only)
    elif arguments.command == 'finalize':
        from video_verifier import finalize_job
        finalize_job(arguments.job)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, FileNotFoundError, KeyError, ImportError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(1)
