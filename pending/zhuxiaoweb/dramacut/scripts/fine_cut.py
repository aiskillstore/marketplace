"""Local-first entry point. Does not initialize desktop automation or MCP services."""
from __future__ import annotations
import argparse,hashlib,json,os,re,shutil,subprocess,sys,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
DEFAULT_CONFIG=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'state/tiktok-drama-fine-cut/backend.json'
FLAGS={'index':'--index','codec':'--codec','runtime':'--runtime','support_dir':'--support-dir','app_dir':'--app-dir','cache_dir':'--cache-dir','ffmpeg':'--ffmpeg','ffprobe':'--ffprobe'}
CAPABILITIES = {
    'locate': ('index',),
    'inspect': ('index', 'codec', 'runtime'),
    'analyze': ('support_dir', 'cache_dir', 'app_dir', 'ffmpeg'),
    'preview': ('codec', 'runtime', 'support_dir', 'cache_dir', 'app_dir'),
    'qc': ('ffmpeg', 'ffprobe'),
    'write_copy': ('index', 'codec', 'runtime'),
}
EPISODE_NUMBER = re.compile(r'(?:第\s*)?(\d{1,6})(?:\s*集)?')
EPISODE_RANGE = re.compile(r'\s*(?:第\s*)?(\d{1,6})(?:\s*集)?\s*[-–—~～至到]\s*(?:第\s*)?(\d{1,6})(?:\s*集)?\s*')

def load(path):return json.loads(Path(path).read_text('utf-8-sig'))
def save(path,value):
    from draft_workspace import atomic
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    atomic(path, json.dumps(value,ensure_ascii=False,indent=2).encode('utf-8'))
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(argv,timeout=210):
    return subprocess.run(list(map(str,argv)),capture_output=True,timeout=timeout,
                          creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
def version(path):return tuple(int(x) for x in re.findall(r'\d+',Path(path).name))
def unique(paths):return list(dict.fromkeys(Path(p).expanduser().resolve() for p in paths if str(p)))
def first(paths,kind='file'):
    return next((str(p) for p in unique(paths) if (p.is_file() if kind=='file' else p.is_dir())),None)

def discover(existing=None,search_roots=(),index=None):
    cfg=dict(existing or {})
    local=Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'AppData/Local')))/'JianyingPro/User Data'
    default_index = local / 'Projects/com.lveditor.draft/root_meta_info.json'
    index_path = Path(index) if index else next(
        (p for p in (Path(cfg['index']) if cfg.get('index') else default_index, default_index)
         if p.is_file()), default_index)
    roots=[Path(p) for p in search_roots]
    roots.extend([local.parent,Path.home()/'Desktop',Path(os.environ.get('ProgramFiles','C:/Program Files')),
                  Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'AppData/Local')))/'Programs'])
    if index_path.is_file():
        cfg['index']=str(index_path.resolve())
        try:
            entries = load(index_path).get('all_draft_store', [])
        except (OSError, ValueError, AttributeError):
            entries = []
        for entry in entries if isinstance(entries, list) else []:
            raw = entry.get('draft_fold_path') if isinstance(entry, dict) else None
            if raw:
                p=Path(raw)
                roots.extend(list(p.parents)[:3])
    for key in ('support_dir','app_dir','runtime','codec'):
        if cfg.get(key):roots.extend(list(Path(cfg[key]).parents)[:2])
    for name in ('JY_INSTALL_DIR','JIANYING_INSTALL_DIR','JIANYING_INSTALL_ROOT'):
        if os.environ.get(name):roots.append(Path(os.environ[name]))
    try:
        import winreg
        for hive in (winreg.HKEY_CURRENT_USER,winreg.HKEY_LOCAL_MACHINE):
            for key in (r'Software\ByteDance\JianyingPro',r'Software\JianyingPro',r'Software\Microsoft\Windows\CurrentVersion\Uninstall\JianyingPro'):
                try:
                    with winreg.OpenKey(hive,key) as k:
                        for field in ('installDir','InstallLocation'):
                            try:roots.append(Path(winreg.QueryValueEx(k,field)[0]))
                            except OSError:pass
                except OSError:pass
            for exe in ('JianyingPro.exe', 'JianyingExportAssistant.exe'):
                try:
                    with winreg.OpenKey(hive, rf'Software\Microsoft\Windows\CurrentVersion\App Paths\{exe}') as k:
                        roots.append(Path(winreg.QueryValueEx(k, None)[0].strip('"')).parent)
                except OSError:
                    pass
    except ImportError:pass
    roots=[p for p in unique(roots) if p.is_dir() and p!=Path(p.anchor)]
    support=[];apps=[];runtimes=[];codecs=[];media=[]
    # Fixed-depth, product-specific patterns. Never recursively scan a drive or user profile.
    for root in roots:
        for pat in ('jyexport/engine.py','JianyingExportAssistant/jyexport/engine.py',
                    '*/JianyingExportAssistant/jyexport/engine.py','source/jyexport/engine.py',
                    '剪映交付助手*/source/jyexport/engine.py'):
            support.extend(p.parent.parent for p in root.glob(pat) if p.is_file())
        for pat in ('JianyingPro/*/videoeditor.dll','JianyingPro/Apps/*/videoeditor.dll','Apps/*/videoeditor.dll','*/videoeditor.dll','videoeditor.dll'):
            apps.extend(p.parent for p in root.glob(pat) if p.is_file())
        for pat in ('引擎数据/*/videoeditor.dll','剪映交付助手/引擎数据/*/videoeditor.dll','*/引擎数据/*/videoeditor.dll'):
            runtimes.extend(p.parent for p in root.glob(pat) if p.is_file())
        for pat in ('runtime/ffmpeg/bin/ffmpeg.exe','*/runtime/ffmpeg/bin/ffmpeg.exe','ffmpeg/bin/ffmpeg.exe'):
            media.extend(root.glob(pat))
    for p in unique(apps):media.append(p/'ffmpeg.exe')
    support=[p for p in unique(support) if all((p/'jyexport'/f).is_file() for f in ('engine.py','processed_audio.py','encoded_audio.py'))]
    for p in support:
        codecs.append(p / 'tools/headless-engine/bin/jy-draftc.exe')
        if p.name == 'source':
            codecs.append(p.parent / 'engine/bin/jy-draftc.exe')
    codecs.extend(p for root in roots for p in
                  (root / 'jy-draftc.exe', root / 'tools/headless-engine/bin/jy-draftc.exe',
                   root / 'engine/bin/jy-draftc.exe', *root.glob('剪映交付助手*/engine/bin/jy-draftc.exe')))
    apps=sorted(unique(apps),key=version,reverse=True)
    runtimes=sorted(unique(runtimes),key=version,reverse=True)
    defaults=dict(codec=first(codecs),support_dir=first(support,'dir'),app_dir=first(apps,'dir'),
                  runtime=first(runtimes or apps,'dir'),cache_dir=str(local/'Cache'),
                  ffmpeg=first([p for p in (shutil.which('ffmpeg'),*media) if p]))
    if defaults['ffmpeg']:defaults['ffprobe']=first([Path(defaults['ffmpeg']).with_name('ffprobe.exe'),shutil.which('ffprobe') or ''])
    for key,value in defaults.items():
        old=cfg.get(key)
        if value and (not old or not Path(old).exists()):cfg[key]=value
    cfg['schema_version']=1
    cfg['runtime_candidates']=[str(p) for p in unique([*runtimes, *apps, *cfg.get('runtime_candidates', [])])
                               if (p / 'videoeditor.dll').is_file()]
    return cfg

def profile(path):
    cfg=load(path) if path.is_file() else discover()
    if not path.is_file():save(path,cfg)
    return cfg

def missing(cfg,keys):
    directories = {'runtime', 'support_dir', 'app_dir', 'cache_dir'}
    return [key for key in keys if not cfg.get(key) or
            not (Path(cfg[key]).is_dir() if key in directories else Path(cfg[key]).is_file())]


def capabilities(cfg, copy_open=False, codec_ready=None):
    result = {}
    for stage, keys in CAPABILITIES.items():
        absent = missing(cfg, keys)
        available = not absent and not (stage in ('inspect', 'preview', 'write_copy') and codec_ready is False)
        if stage == 'write_copy' and copy_open:
            available = False
        result[stage] = dict(paths_ready=not absent, available=available, missing=absent)
    return result
def need(cfg,keys):
    absent=missing(cfg,keys)
    if absent:raise ValueError('Missing local backend fields: '+', '.join(absent)+'. Run doctor with --search-root or explicit paths. Other available file work can continue.')

def doctor(arguments,cfg_path):
    p=argparse.ArgumentParser(description='Bounded local backend discovery; no desktop initialization.')
    p.add_argument('--search-root',action='append',default=[]);p.add_argument('--write-config')
    for key,flag in FLAGS.items():p.add_argument(flag,dest=key)
    a=p.parse_args(arguments)
    old=load(cfg_path) if cfg_path.is_file() else {}
    old.update({key:str(Path(getattr(a,key)).expanduser().resolve()) for key in FLAGS if getattr(a,key)})
    cfg=discover(old,a.search_root,a.index)
    keys=list(FLAGS);absent=missing(cfg,keys)
    facts={key:dict(path=cfg.get(key),exists=key not in absent) for key in keys}
    cfg['fingerprints']={key:dict(size=Path(cfg[key]).stat().st_size,mtime_ns=Path(cfg[key]).stat().st_mtime_ns) for key in ('codec','ffmpeg','ffprobe') if key not in absent}
    cfg['discovered_at']=time.time()
    dest=Path(a.write_config).resolve() if a.write_config else cfg_path
    save(dest,cfg)
    return dict(status='ready_to_probe' if not absent else 'partial',config=str(dest),paths=facts,missing=absent,
                capabilities=capabilities(cfg),
                compatibility='Unproven until probe and actual preview succeed',desktop_started=False)

def selected(cfg,draft,episodes):
    import draft_workspace as ds
    need(cfg,['index'])
    info=ds.named(ds.rows(Path(cfg['index'])),draft)
    return info,ds.select(info,episodes)


class StartIssue(Exception):
    def __init__(self, action, message, **details):
        super().__init__(message)
        self.next = dict(action=action, message=message, **details)


def start_selection(cfg, draft, requested):
    import draft_workspace as ds

    if missing(cfg, ('index',)):
        raise StartIssue('locate_index', 'Find the local Jianying draft index, then use start --index.')
    try:
        entries = ds.rows(Path(cfg['index']))
    except (ds.DraftError, OSError, ValueError, AttributeError) as exc:
        raise StartIssue('check_index', str(exc), index=cfg['index']) from exc
    if sum(row['draft_name'] == draft for row in entries) != 1:
        nearby = sorted({name for row in entries if isinstance(name := row['draft_name'], str)
                         and (draft.casefold() in name.casefold() or name.casefold() in draft.casefold())})
        raise StartIssue('confirm_draft_name', 'Use a uniquely registered draft name from the local index.',
                         requested=draft, candidates=nearby[:12])
    try:
        info = ds.named(entries, draft)
    except (ds.DraftError, OSError, ValueError, KeyError, TypeError) as exc:
        raise StartIssue('check_saved_draft', str(exc)) from exc
    labels = [row['name'] for row in info['timelines']]
    values = []
    for token in requested:
        token = token.strip()
        span = EPISODE_RANGE.fullmatch(token)
        if span and token not in labels:
            start, end = map(int, span.groups())
            if not 0 <= end - start < len(labels):
                raise StartIssue('confirm_episode_labels', f'Cannot map episode range {token!r}.', labels=labels)
            values.extend(str(number) for number in range(start, end + 1))
        else:
            values.append(token)
    resolved = []
    for token in values:
        number = EPISODE_NUMBER.fullmatch(token)
        if number:
            matches = [label for label in labels
                       if (match := EPISODE_NUMBER.fullmatch(label.strip()))
                       and int(match[1]) == int(number[1])]
        else:
            matches = [label for label in labels if label == token]
        if len(matches) != 1 or matches[0] in resolved:
            raise StartIssue('confirm_episode_labels', f'Expected a unique episode for {token!r}.',
                             labels=labels, matches=matches)
        resolved.append(matches[0])
    return info, ds.select(info, resolved)


def codec_fingerprint(cfg):
    if missing(cfg, ('codec', 'runtime')):
        return None
    files = [Path(cfg['codec']), Path(cfg['runtime']) / 'videoeditor.dll']
    if not files[1].is_file():
        return None
    result = {}
    for path in files:
        stat = path.stat()
        result[str(path)] = [stat.st_size, stat.st_mtime_ns]
    return result


def has_codec_probe(cfg, stamp):
    probe = cfg.get('codec_probe')
    return bool(stamp and isinstance(probe, dict) and probe.get('fingerprint') == stamp)


def inspection_workspace(root, work):
    if work.is_relative_to(root):
        raise ValueError('Inspection workspace must be outside the live draft')
    work.mkdir(parents=True, exist_ok=False)


def capture_saved(root, ep, work):
    import draft_workspace as ds

    src = ds.child_file(root, Path('Timelines') / ep['id'] / ds.CONTENT)
    raw = src.read_bytes()
    (work / f'{ep["id"]}.saved').write_bytes(raw)
    return str(src), hashlib.sha256(raw).hexdigest()


def ensure_stable(checks):
    if any(sha(path) != checksum for path, checksum in checks.items()):
        raise StartIssue('retry_latest_saved', 'Saved timelines changed during inspection. Retry in a new workspace.')


def inspect_saved(codec, ep, source, output, roundtrip=False):
    tid = ep['id']
    saved = source / f'{tid}.saved'
    out = output / f'{tid}.json'
    doc = codec.read(saved, out, tid)
    if roundtrip:
        encoded = output / f'{tid}.roundtrip.enc'
        decoded = output / f'{tid}.roundtrip.json'
        codec.run('-ec', out, encoded)
        codec.run('-dc', encoded, decoded)
        if out.read_bytes() != decoded.read_bytes():
            raise ValueError('Codec roundtrip changed JSON bytes')
    return dict(name=ep['name'], id=tid, json=str(out), seconds=doc.get('duration', 0) / 1e6,
                fps=doc.get('fps'), tracks=[dict(type=t.get('type'), name=t.get('name'),
                segments=len(t.get('segments', []))) for t in doc['tracks']])


def codec_runner(cfg, runtime=None):
    from draft_workspace import Codec

    return Codec(argparse.Namespace(codec=cfg['codec'], runtime=runtime or cfg['runtime']))


def start_draft(arguments, cfg_path):
    from draft_workspace import DraftError

    parser = argparse.ArgumentParser(description='Resolve and inspect saved episodes without starting Jianying or desktop tools.')
    parser.add_argument('--draft', required=True)
    parser.add_argument('--episodes', nargs='+', required=True, help='Exact episode labels or a numeric range such as 9-16.')
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--search-root', action='append', default=[])
    parser.add_argument('--index')
    a = parser.parse_args(arguments)
    work = Path(a.workspace).expanduser().resolve()
    result = dict(status='needs_local_action', workspace=str(work), config=str(cfg_path),
                  desktop_started=False, next=[])
    try:
        try:
            cfg = load(cfg_path) if cfg_path.is_file() else {}
            if not isinstance(cfg, dict):
                raise ValueError('Expected a configuration object')
        except (OSError, ValueError) as exc:
            result['previous_config_error'] = str(exc)
            cfg = {}
        fingerprint = codec_fingerprint(cfg)
        validated = has_codec_probe(cfg, fingerprint)
        if a.index or a.search_root or not validated or missing(cfg, FLAGS):
            cfg = discover(cfg, a.search_root, a.index)
            if a.index:
                cfg['index'] = str(Path(a.index).expanduser().resolve())
            # Preserve a valid stored profile when an explicit index is mistyped.
            if not a.index or not missing(cfg, ('index',)):
                save(cfg_path, cfg)
        result['capabilities'] = capabilities(cfg)
        info, episodes = start_selection(cfg, a.draft, a.episodes)
        root = Path(info['path'])
        result.update(draft=info, episodes=episodes, copy_open=os.path.lexists(root / '.locked'))
        result['capabilities'] = capabilities(cfg, result['copy_open'])
        if missing(cfg, ('codec', 'runtime')):
            raise StartIssue('locate_codec_runtime', 'Supply the missing compatible codec/runtime via doctor or start --search-root.',
                             missing=missing(cfg, ('codec', 'runtime')))
        try:
            inspection_workspace(root, work)
        except FileExistsError as exc:
            raise StartIssue('use_new_workspace', 'Use a new isolated inspection directory.') from exc
        except (OSError, ValueError) as exc:
            raise StartIssue('check_saved_files', str(exc)) from exc
        captured = []
        episode_errors = []
        for ep in episodes:
            try:
                path, checksum = capture_saved(root, ep, work)
                captured.append((ep, path, checksum))
            except (DraftError, OSError) as exc:
                episode_errors.append(dict(name=ep['name'], id=ep['id'], error=str(exc)))
        result['episode_errors'] = episode_errors
        if not captured:
            raise StartIssue('check_saved_files', 'None of the requested saved timeline files could be read.')

        runtimes = unique([cfg['runtime'], *cfg.get('runtime_candidates', [])])[:3]
        attempts = []
        for i, runtime in enumerate(runtimes, 1):
            candidate = dict(cfg, runtime=str(runtime))
            stamp = codec_fingerprint(candidate)
            cached = has_codec_probe(cfg, stamp)
            attempt = work / f'codec-{i}'
            attempt.mkdir()
            try:
                codec = codec_runner(cfg, runtime)
                if not cached:
                    first_summary = inspect_saved(codec, captured[0][0], work, attempt, roundtrip=True)
            except (DraftError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
                attempts.append(dict(runtime=str(runtime), error=str(exc)))
                continue
            decoded = []
            checks = {}
            decode_errors = []
            for j, (ep, path, checksum) in enumerate(captured):
                try:
                    if j == 0 and not cached:
                        summary = first_summary
                    else:
                        summary = inspect_saved(codec, ep, work, attempt)
                except (DraftError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
                    decode_errors.append(dict(name=ep['name'], id=ep['id'], error=str(exc)))
                    continue
                decoded.append((summary, path, checksum))
            if not decoded:
                if cached:
                    attempts.append(dict(runtime=str(runtime), error='No selected saved timeline could be read.',
                                         episode_errors=decode_errors))
                    continue
                result['episode_errors'].extend(decode_errors)
                raise StartIssue('check_saved_files', 'No stable saved timeline was available from this selection.')
            summaries = []
            for summary, path, checksum in decoded:
                try:
                    ensure_stable({path: checksum})
                except (OSError, StartIssue) as exc:
                    decode_errors.append(dict(name=summary['name'], id=summary['id'], error=str(exc)))
                    continue
                summaries.append(summary)
                checks[path] = checksum
            result['episode_errors'].extend(decode_errors)
            if not summaries:
                raise StartIssue('retry_latest_saved', 'Saved timelines changed during inspection. Retry in a new workspace.')
            cfg['runtime'] = str(runtime)
            if not cached:
                cfg['codec_probe'] = dict(fingerprint=stamp, codec=cfg['codec'], runtime=str(runtime),
                                          roundtrip=True, at=time.time())
                save(cfg_path, cfg)
            result.update(status='ready', episodes=summaries, source_hashes=checks, analysis_only=True,
                          copy_open=os.path.lexists(root / '.locked'), runtime=str(runtime),
                          codec_roundtrip='cached' if cached else 'passed', codec_attempts=attempts)
            result['capabilities'] = capabilities(cfg, result['copy_open'], True)
            result['next'].append(dict(action='analyze_saved', message='Use the isolated episode JSON for read-only analysis.'))
            if result['episode_errors']:
                result['status'] = 'partial'
                result['next'].append(dict(action='check_saved_files',
                                           message='Continue the ready episodes. Retry the affected episodes from a stable save.'))
            for stage in ('analyze', 'preview', 'qc'):
                absent = result['capabilities'][stage]['missing']
                if absent:
                    result['next'].append(dict(action='locate_local_dependencies', stage=stage, missing=absent))
            if result['copy_open']:
                result['next'].append(dict(action='save_and_close_before_write', stage='write_copy',
                                           message='Continue analysis now. Save and return home before snapshot/commit.'))
            save(work / 'inspection.json', result)
            return result
        result.update(codec_attempts=attempts, capabilities=capabilities(cfg, result['copy_open'], False))
        raise StartIssue('check_codec_compatibility', 'No tested local codec/runtime could open the saved timeline. Check the recorded errors and the compatible runtime.')
    except StartIssue as exc:
        result['next'].append(exc.next)
        return result

def inspect_draft(arguments,cfg,cfg_path,probe=False):
    p=argparse.ArgumentParser(description='Decode stable saved files into an isolated read-only analysis workspace.')
    p.add_argument('--draft',required=True);p.add_argument('--episodes',nargs='+',required=True);p.add_argument('--workspace',required=True)
    a=p.parse_args(arguments);need(cfg,['codec','runtime','index'])
    info,episodes=selected(cfg,a.draft,a.episodes)
    root=Path(info['path']);work=Path(a.workspace).resolve()
    inspection_workspace(root,work)
    checks=dict(capture_saved(root, ep, work) for ep in episodes)
    codec=codec_runner(cfg)
    summaries=[inspect_saved(codec,ep,work,work,roundtrip=probe) for ep in episodes]
    ensure_stable(checks)
    result=dict(draft=info,episodes=summaries,source_hashes=checks,analysis_only=True,copy_open=os.path.lexists(root/'.locked'),desktop_started=False)
    save(work/'inspection.json',result)
    if probe:
        cfg['codec_probe']=dict(codec=cfg['codec'],runtime=cfg['runtime'],at=time.time(),workspace=str(work),
                                roundtrip=True,fingerprint=codec_fingerprint(cfg))
        save(cfg_path,cfg)
    return result

def append_defaults(arguments,cfg,keys):
    result=list(arguments)
    for key in keys:
        flag=FLAGS[key]
        if flag not in result and not any(x.startswith(flag+'=') for x in result):
            need(cfg,[key]);result.extend([flag,cfg[key]])
    return result

def execute(a):
    cfg_path=Path(a.config).expanduser().resolve()
    if a.command=='doctor':return doctor(a.arguments,cfg_path)
    if a.command=='start':return start_draft(a.arguments,cfg_path)
    help_only=any(x in ('--help','-h') for x in a.arguments)
    cfg={} if help_only else profile(cfg_path)
    if a.command in ('probe','inspect'):return inspect_draft(a.arguments,cfg,cfg_path,a.command=='probe')
    if a.command in ('list','clone','snapshot','commit','verify','readback','recover'):
        keys=['index'] if a.command in ('list','clone','snapshot') else []
        if a.command not in ('list','recover'):keys+=['codec','runtime']
        script=HERE/'draft_workspace.py';arguments=[a.command,*(a.arguments if help_only else append_defaults(a.arguments,cfg,keys))]
    elif a.command in ('apply','validate','inspect-json'):
        script=HERE/'timeline_ops.py';arguments=['inspect' if a.command=='inspect-json' else a.command,*a.arguments]
    elif a.command=='analyze':
        script=HERE/'analyze_draft.py';arguments=list(a.arguments) if help_only else append_defaults(a.arguments,cfg,['support_dir','cache_dir','app_dir','ffmpeg'])
    elif a.command in ('propose','approve-plan'):
        script=HERE/'plan_candidates.py';arguments=['approve' if a.command=='approve-plan' else a.command,*a.arguments]
    elif a.command=='transcribe':
        script=HERE/'transcribe.py';arguments=list(a.arguments)
    elif a.command in ('sfx-library', 'seam-review', 'audio-audition', 'review-check', 'feedback-review', 'automated-review'):
        script=HERE/({'sfx-library':'sfx_library.py','seam-review':'seam_review.py',
                      'audio-audition':'audio_audition.py','review-check':'review_check.py',
                      'feedback-review':'feedback_review.py','automated-review':'automated_review.py'}[a.command])
        keys = []
        if a.command == 'seam-review' and a.arguments and a.arguments[0] in ('scan', 'inspect-range'):
            keys = ['ffmpeg', 'ffprobe']
        elif a.command == 'sfx-library' and a.arguments and a.arguments[0] in ('index','measure','prepare'):
            keys = ['ffmpeg']
        elif a.command == 'audio-audition':
            keys = ['ffmpeg', 'codec', 'runtime']
        elif a.command == 'automated-review' and a.arguments and a.arguments[0] == 'build':
            keys = ['ffmpeg', 'ffprobe']
        arguments=list(a.arguments) if help_only else append_defaults(a.arguments,cfg,keys)
    elif a.command=='run':
        script=HERE/'run_workflow.py';arguments=list(a.arguments) if help_only else [*a.arguments,'--config',str(cfg_path)]
    elif a.command=='preview':
        script=HERE/'preview_draft.py';arguments=list(a.arguments) if help_only else append_defaults(a.arguments,cfg,['codec','runtime','support_dir','cache_dir','app_dir'])
        if '--fps' not in arguments and not any(s.startswith('--fps=') for s in arguments):
            inputs=[arguments[i+1] for i,x in enumerate(arguments[:-1]) if x=='--input']
            inputs.extend(x.split('=',1)[1] for x in arguments if x.startswith('--input='))
            if inputs:arguments.extend(['--fps',str(load(inputs[0]).get('fps',30))])
    else:
        script=HERE/'media_qc.py';arguments=list(a.arguments) if help_only else append_defaults(a.arguments,cfg,['ffmpeg','ffprobe'])
    proc=run([sys.executable,'-B',script,*arguments],86400 if a.command=='run' else 1200)
    if proc.returncode:
        diagnostics = (proc.stderr or proc.stdout).decode('utf-8','replace').strip()
        raise ValueError(diagnostics[-2000:] or f'{script.name} failed ({proc.returncode})')
    text=proc.stdout.decode('utf-8','replace')
    try:return json.loads(text)
    except ValueError:return dict(status='completed',output=text.strip())

def main():
    sys.dont_write_bytecode=True
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',default=str(DEFAULT_CONFIG));p.add_argument('--metrics',help='Optional local JSONL stage timing log')
    p.add_argument('command',choices=['start','doctor','probe','inspect','list','clone','snapshot','inspect-json','analyze','transcribe','propose','approve-plan','apply','validate','preview','qc','commit','verify','readback','recover','run','sfx-library','seam-review','audio-audition','review-check','feedback-review','automated-review'])
    p.add_argument('arguments',nargs=argparse.REMAINDER)
    a=p.parse_args();started=time.monotonic();status='failed'
    try:
        result=execute(a)
        status = result.get('status', 'completed') if isinstance(result, dict) else 'completed'
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except Exception as exc:
        p.exit(1,json.dumps(dict(status='local_command_failed',step=a.command,error=str(exc),desktop_started=False),ensure_ascii=False)+'\n')
    finally:
        if a.metrics:
            path=Path(a.metrics);path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('a',encoding='utf-8') as f:f.write(json.dumps(dict(step=a.command,status=status,elapsed_seconds=round(time.monotonic()-started,3),desktop_started=False))+'\n')

if __name__=='__main__':main()
