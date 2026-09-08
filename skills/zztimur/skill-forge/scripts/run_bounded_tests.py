#!/usr/bin/env python3
"""Capability-checked execution of explicitly reviewed, declarative test plans.

Linux requires a local Docker daemon and the pinned image already installed.
macOS probes basic isolation but refuses targets without verified aggregate
resource limits and whole-tree containment. No backend installs dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
import uuid

from inspect_skill_package import PublicArgumentParser

IMAGE = 'docker.io/library/python@sha256:933b46a028fd786c9c3d426ebabc237e29a15912231ea8de576e95f0e4f41a4c'
MAX_FILES = 5000
MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_SOURCE_BYTES = 100 * 1024 * 1024
KEYS = {'schema_version', 'source_root', 'source_files', 'scratch_inputs', 'commands',
        'reviewed', 'network', 'wall_seconds', 'memory_mib', 'process_limit', 'output_bytes'}


def relative_file(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or '\x00' in value:
        raise ValueError('Invalid relative input path.')
    path = PurePosixPath(value)
    if path.is_absolute() or any(x in ('', '.', '..') for x in value.split('/')):
        raise ValueError('Input paths must stay within the declared source.')
    if any(x.startswith('.env') or x in ('.git', '.ssh', '.aws', '.codex') for x in path.parts):
        raise ValueError('Credential/configuration paths cannot be test inputs.')
    return value


def validate_plan(plan):
    if not isinstance(plan, dict) or set(plan) != KEYS or type(plan['schema_version']) is not int or plan['schema_version'] != 1:
        raise ValueError('Invalid test-plan schema or fields.')
    if plan['reviewed'] is not True or plan['network'] is not False:
        raise ValueError('Static review and default-deny network are required.')
    if not isinstance(plan['source_root'], str) or not Path(plan['source_root']).is_absolute():
        raise ValueError('source_root must be absolute.')
    for key, lower, upper in [('wall_seconds', 1, 300), ('memory_mib', 64, 2048),
                              ('process_limit', 8, 128), ('output_bytes', 1024, 1048576)]:
        if type(plan[key]) is not int or not lower <= plan[key] <= upper:
            raise ValueError('Invalid numeric limit: ' + key)
    files = plan['source_files']
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_FILES:
        raise ValueError('Explicit bounded source_files are required.')
    for value in files: relative_file(value)
    if len(set(files)) != len(files): raise ValueError('Duplicate source file.')
    inputs = plan['scratch_inputs']
    if not isinstance(inputs, list) or len(inputs) > MAX_FILES: raise ValueError('Invalid scratch inputs.')
    destinations = set()
    for item in inputs:
        if not isinstance(item, dict) or set(item) != {'source', 'destination'}:
            raise ValueError('Invalid scratch input record.')
        if relative_file(item['source']) not in files: raise ValueError('Scratch input not selected.')
        dest = relative_file(item['destination'])
        if dest in destinations: raise ValueError('Duplicate scratch destination.')
        destinations.add(dest)
    commands = plan['commands']
    if not isinstance(commands, list) or not 1 <= len(commands) <= 20: raise ValueError('Invalid command list.')
    for argv in commands:
        if not isinstance(argv, list) or not 1 <= len(argv) <= 100 or any(not isinstance(x, str) or not x or '\x00' in x or len(x) > 4096 for x in argv):
            raise ValueError('Commands must be bounded argv arrays, never shell strings.')
        if Path(argv[0]).name in ('sh', 'bash', 'zsh', 'dash', 'fish', 'cmd', 'powershell', 'pwsh'):
            raise ValueError('Shell entrypoints are not supported.')
    return plan


def copy_sources(plan, destination):
    """Read only selected regular files, walking each component without symlinks."""
    root = Path(plan['source_root'])
    if root.resolve() != root: raise ValueError('Source root must use its canonical path.')
    total, records = 0, {}
    for name in plan['source_files']:
        descriptors = []
        try:
            descriptor = os.open(str(root), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            descriptors.append(descriptor)
            parts = PurePosixPath(name).parts
            for part in parts[:-1]:
                descriptor = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
                descriptors.append(descriptor)
            file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
            descriptors.append(file_fd)
            info = os.fstat(file_fd)
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_FILE_BYTES:
                raise ValueError('Source input is not a bounded regular file.')
            chunks, size = [], 0
            while True:
                chunk = os.read(file_fd, 65536)
                if not chunk: break
                size += len(chunk)
                if size > MAX_FILE_BYTES or total + size > MAX_SOURCE_BYTES:
                    raise ValueError('Source copy limit exceeded.')
                chunks.append(chunk)
            data = b''.join(chunks)
            after = os.fstat(file_fd)
            if (info.st_size, info.st_mtime_ns, info.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise ValueError('Source input changed during copy.')
            total += size
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(0o444)
            records[name] = hashlib.sha256(data).hexdigest()
        finally:
            for descriptor in reversed(descriptors): os.close(descriptor)
    # The unprivileged container must be able to traverse the copied tree.
    for directory, _, _ in os.walk(destination): Path(directory).chmod(0o755)
    return records


def invoke(argv, timeout=15, output_limit=1048576):
    """Bound output while reading, rather than after communicate allocates it."""
    env = {'PATH': '/usr/local/bin:/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C'}
    process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, env=env, start_new_session=True)
    output, overflow = bytearray(), threading.Event()
    def consume():
        while True:
            block = process.stdout.read(4096)
            if not block: break
            room = output_limit - len(output)
            output.extend(block[:max(room, 0)])
            if len(block) > room:
                overflow.set()
                break
    reader = threading.Thread(target=consume, daemon=True)
    reader.start()
    end = time.monotonic() + timeout
    timed_out = False
    while process.poll() is None:
        if overflow.is_set() or time.monotonic() >= end:
            timed_out = not overflow.is_set()
            try: os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            break
        time.sleep(0.02)
    process.wait(timeout=5)
    reader.join(timeout=2)
    if reader.is_alive():
        process.stdout.close()
        raise RuntimeError('Controller output stream did not close.')
    process.stdout.close()
    captured = bytes(output)
    return dict(code=process.returncode, text=captured.decode('utf-8', 'replace'),
                captured_bytes=len(captured), captured_sha256=hashlib.sha256(captured).hexdigest(),
                timed_out=timed_out, output_limited=overflow.is_set())


def container_options(name, source, plan):
    return ['create', '--name=' + name, '--pull=never', '--network=none', '--read-only',
            '--cap-drop=ALL', '--security-opt=no-new-privileges', '--cgroupns=private',
            '--user=65534:65534', '--log-driver=none', '--stop-timeout=1',
            '--pids-limit=' + str(plan['process_limit']), '--memory=' + str(plan['memory_mib']) + 'm',
            '--memory-swap=' + str(plan['memory_mib']) + 'm', '--cpus=1',
            '--mount=type=bind,src=' + str(source) + ',dst=/source,readonly',
            '--tmpfs=/scratch:rw,nosuid,nodev,size=268435456,mode=1777',
            '--tmpfs=/dev/shm:ro,nosuid,nodev,size=4096,mode=0555',
            '--workdir=/scratch', '--entrypoint=/usr/local/bin/python3', IMAGE]


def docker_prefix(config):
    binary = next((p for p in ('/usr/bin/docker', '/usr/local/bin/docker') if os.path.isfile(p) and os.access(p, os.X_OK)), None)
    if binary is None: raise RuntimeError('Docker CLI unavailable; install is outside this runner.')
    return [binary, '--config', str(config), '--host', 'unix:///var/run/docker.sock']


def container_run(prefix, source, plan, program, arguments=(), timeout=None):
    name = 'skill-forge-test-' + uuid.uuid4().hex
    cleanup = False
    result = None
    try:
        created = invoke(prefix + container_options(name, source, plan) + ['-I', '-c', program, *arguments])
        if created['code'] or created['timed_out'] or created['output_limited']:
            raise RuntimeError('Container creation failed; pinned image/daemon may be unavailable.')
        result = invoke(prefix + ['start', '--attach', name], timeout or plan['wall_seconds'], plan['output_bytes'])
        if result['timed_out'] or result['output_limited']:
            killed = invoke(prefix + ['kill', name])
            if killed['code']: raise RuntimeError('Container kill could not be confirmed.')
        state_result = invoke(prefix + ['inspect', '--format', '{{json .State}}', name])
        state = json.loads(state_result['text'])
        started = state.get('StartedAt')
        if (state_result['code'] or state.get('Running') or state.get('Error')
                or state.get('Status') != 'exited' or not isinstance(started, str)
                or not started or started.startswith('0001-')
                or type(state.get('ExitCode')) is not int):
            raise RuntimeError('Container termination state is unverified.')
        if not result['timed_out'] and not result['output_limited'] and result['code'] != state['ExitCode']:
            raise RuntimeError('Docker attach status does not match the verified target exit.')
        result.update(code=state['ExitCode'], oom_killed=state.get('OOMKilled', False))
    finally:
        # Daemon-side removal destroys the entire container PID namespace,
        # including descendants that called setsid; killing the CLI is insufficient.
        removed = invoke(prefix + ['rm', '--force', name])
        checked = invoke(prefix + ['container', 'ls', '--all', '--quiet', '--filter', 'name=^/' + name + '$'])
        cleanup = removed['code'] == 0 and checked['code'] == 0 and not checked['text'].strip()
        if not cleanup: raise RuntimeError('Container cleanup could not be verified; stop all target execution.')
    result['cleanup_verified'] = cleanup
    return result


BASIC_PROBE = r'''
import errno,json,os,pathlib,socket,subprocess,sys
def denied(path):
    try: pathlib.Path(path).write_text('synthetic')
    except PermissionError: return True
    except OSError as e: return e.errno == errno.EROFS
    return False
p=pathlib.Path('/scratch/check');p.write_text('synthetic')
network=False
try:
    s=socket.socket();s.settimeout(1);s.connect(('1.1.1.1',443))
except OSError as e: network=e.errno in (errno.EPERM,errno.EACCES,errno.ENETUNREACH)
c=pathlib.Path('/sys/fs/cgroup')
env=set(os.environ).issubset({'PATH','LANG','LC_ALL','TMPDIR','TMP','TEMP'})
children=[];limited=False
try:
    for i in range(int(sys.argv[2])+2): children.append(subprocess.Popen([sys.executable,'-I','-c','import time;time.sleep(10)']))
except OSError as e: limited=e.errno==errno.EAGAIN
finally:
    for p in children:p.kill()
    for p in children:p.wait()
status=pathlib.Path('/proc/self/status').read_text()
print(json.dumps(dict(source_read=pathlib.Path('/source/canary').read_text()=='synthetic',source_write_denied=denied('/source/canary'),root_write_denied=denied('/tmp/outside'),scratch_write=True,network_denied=network,credentials_absent=env,memory_kernel=(c/'memory.max').read_text().strip()==sys.argv[1],swap_disabled=(c/'memory.swap.max').read_text().strip()=='0',process_kernel=(c/'pids.max').read_text().strip()==sys.argv[2],process_stress=limited,capabilities_dropped=int(next(line.split()[1] for line in status.splitlines() if line.startswith('CapEff:')),16)==0,no_new_privileges='NoNewPrivs:\t1' in status)))
'''

BOOTSTRAP = r'''
import json,os,pathlib,shutil,sys
os.environ.clear();os.environ.update(PATH='/usr/local/bin:/usr/bin:/bin',LANG='C',LC_ALL='C',TMPDIR='/scratch',TMP='/scratch',TEMP='/scratch')
for item in json.loads(sys.argv[1]):
    dest=pathlib.Path('/scratch')/item['destination'];dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(pathlib.Path('/source')/item['source'],dest)
argv=json.loads(sys.argv[2]);os.execvpe(argv[0],argv,os.environ)
'''


def mac_probe():
    controls = {'aggregate_memory_limit': 'Not Assessed', 'aggregate_process_limit': 'Not Assessed',
                'whole_process_tree_termination': 'Not Assessed'}
    if not Path('/usr/bin/sandbox-exec').exists(): return controls
    with tempfile.TemporaryDirectory(prefix='skill-forge-capability-') as directory:
        root = Path(directory).resolve(); scratch = root / 'scratch'; scratch.mkdir()
        source = root / 'source'; source.write_text('synthetic', encoding="utf-8")
        profile = root / 'policy.sb'
        profile.write_text('(version 1) (allow default) (deny network*) (deny file-read* (subpath "/Users")) (deny file-write*) (allow file-write* (subpath ' + json.dumps(str(scratch)) + ') (literal "/dev/null"))', encoding="utf-8")
        code = "import json,pathlib,socket,sys\nr={}\ntry: pathlib.Path(sys.argv[1]).write_text('x');r['source_write_denied']=False\nexcept PermissionError:r['source_write_denied']=True\npathlib.Path(sys.argv[2]).write_text('x');r['scratch_write']=True\ntry: socket.socket().connect(('1.1.1.1',443));r['network_denied']=False\nexcept PermissionError:r['network_denied']=True\nprint(json.dumps(r))"
        try:
            result = invoke(['/usr/bin/sandbox-exec', '-f', str(profile), str(Path(sys.executable).resolve()), '-I', '-c', code, str(source), str(scratch / 'allowed')], timeout=5, output_limit=4096)
            if result['code'] == 0:
                controls.update({k: 'Verified' if v is True else 'Failed' for k, v in json.loads(result['text']).items()})
            else: controls['basic_sandbox_probe'] = 'Not Assessed'
        except (OSError, ValueError, RuntimeError): controls['basic_sandbox_probe'] = 'Not Assessed'
    return controls


def probe(requested_plan=None):
    host = platform.system()
    result = dict(schema_version=1, backend=host, image=IMAGE, supported=False,
                  outcome='Not Assessed', controls={}, reasons=[])
    if host == 'Darwin':
        result['controls'] = mac_probe()
        result['reasons'] = ['macOS aggregate memory/process bounds and whole-tree containment are unverified; sampled group watchdogs are insufficient.']
        return result
    if host != 'Linux':
        result['reasons'] = ['No supported execution backend for this host.']
        return result
    try:
        with tempfile.TemporaryDirectory(prefix='skill-forge-probe-') as directory:
            root = Path(directory); config = root / 'config'; config.mkdir()
            source = root / 'source'; source.mkdir(); source.chmod(0o777)
            (source / 'canary').write_text('synthetic', encoding="utf-8"); (source / 'canary').chmod(0o666)
            prefix = docker_prefix(config)
            plan = dict(memory_mib=64, process_limit=16, wall_seconds=15, output_bytes=65536)
            if requested_plan is not None:
                plan.update(memory_mib=requested_plan['memory_mib'], process_limit=requested_plan['process_limit'])
            result['probe_limits'] = dict(plan)
            # Clear image defaults before the probe, just as for target execution.
            program = 'import os;os.environ.clear();os.environ.update(PATH="/usr/local/bin:/usr/bin:/bin",LANG="C",LC_ALL="C");\n' + BASIC_PROBE
            basic = container_run(prefix, source, plan, program, [str(plan['memory_mib']*1024*1024), str(plan['process_limit'])])
            controls = json.loads(basic['text']) if basic['code'] == 0 else {}
            if len(controls) != 12 or not all(v is True for v in controls.values()):
                raise RuntimeError('Basic filesystem/network/environment/cgroup stress probe failed.')
            memory = container_run(prefix, source, plan, 'x=[]\nwhile True:x.append(bytearray(4*1024*1024))')
            controls['memory_stress'] = memory['oom_killed'] is True and memory['code'] == 137
            timeout = container_run(prefix, source, plan, 'import os,time\nif os.fork()==0:os.setsid()\nwhile True:time.sleep(1)', timeout=1)
            controls['timeout_and_tree_cleanup'] = timeout['timed_out'] and timeout['cleanup_verified']
            result['controls'] = {k: 'Verified' if v else 'Failed' for k,v in controls.items()}
            result['supported'] = all(controls.values())
            result['outcome'] = 'Pass' if result['supported'] else 'Not Assessed'
            if not result['supported']: result['reasons'] = ['Resource or cleanup stress probe failed.']
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError):
        result['reasons'] = ['Local Docker, pinned image, cgroup-v2 controls, or probe cleanup unavailable/unverified. No target launched.']
    return result


def classify(code, execution_error):
    return 'Execution Error' if execution_error else 'Pass' if code == 0 else 'Artifact Fail'


def execute(plan):
    validate_plan(plan)
    capability = probe(plan)
    result = dict(schema_version=1, outcome='Not Assessed', target_launched=False, capability=capability, commands=[])
    result['requested_limits'] = {key: plan[key] for key in ('wall_seconds', 'memory_mib', 'process_limit', 'output_bytes')}
    if not capability['supported']: return result
    try:
        with tempfile.TemporaryDirectory(prefix='skill-forge-run-') as directory:
            root = Path(directory); source = root / 'source'; source.mkdir(); config = root / 'config'; config.mkdir()
            records = copy_sources(plan, source)
            # Hash records without exposing potentially sensitive source names.
            result['source_snapshot_sha256'] = hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()
            prefix = docker_prefix(config)
            for number, argv in enumerate(plan['commands'], 1):
                result['target_launch_attempted'] = True
                result['target_launched'] = None
                observed = container_run(prefix, source, plan, BOOTSTRAP, [json.dumps(plan['scratch_inputs']), json.dumps(argv)])
                result['target_launched'] = True
                status = classify(observed['code'], observed['timed_out'] or observed['output_limited'] or observed['oom_killed'])
                result['commands'].append(dict(number=number, outcome=status, exit_code=observed['code'],
                    timed_out=observed['timed_out'], output_limited=observed['output_limited'],
                    output_sha256=observed['captured_sha256'],
                    output_bytes=observed['captured_bytes'], cleanup_verified=observed['cleanup_verified']))
                if status == 'Execution Error': break
            outcomes = [x['outcome'] for x in result['commands']]
            result['outcome'] = 'Execution Error' if 'Execution Error' in outcomes else 'Artifact Fail' if 'Artifact Fail' in outcomes else 'Pass'
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.SubprocessError):
        result['outcome'] = 'Execution Error'
        result['reason'] = 'Source copy, container execution, or cleanup could not be verified.'
    return result


def main():
    parser = PublicArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--probe', action='store_true')
    modes.add_argument('--plan', type=Path)
    parser.add_argument('--json', action='store_true', help='Emit structured evidence (also the default).')
    args = parser.parse_args()
    try:
        if args.probe: result = probe()
        else:
            if args.plan.stat().st_size > 1048576: raise ValueError('Plan exceeds 1 MiB.')
            result = execute(json.loads(args.plan.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        result = dict(schema_version=1, outcome='Execution Error', target_launched=False, reason='Invalid or unavailable reviewed test plan.')
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['outcome'] == 'Pass' else 1 if result['outcome'] == 'Artifact Fail' else 2


if __name__ == '__main__':
    raise SystemExit(main())
