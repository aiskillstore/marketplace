"""Exercise real containment and bundled suites on a provisioned Linux CI host."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from run_bounded_tests import execute


def main():
    files = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
    plan = dict(schema_version=1, source_root=str(ROOT), source_files=files,
                scratch_inputs=[], reviewed=True, network=False, wall_seconds=240,
                memory_mib=512, process_limit=64, output_bytes=1048576,
                commands=[['python3', '-B', '-S', '/source/scripts/validate_audit_contract.py'],
                          ['python3', '-B', '-S', '/source/scripts/run_self_tests.py'],
                          ['python3', '-B', '-S', '/source/scripts/run_source_tests.py']])
    result = execute(plan)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['outcome'] == 'Pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
