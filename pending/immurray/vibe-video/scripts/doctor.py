#!/usr/bin/env python3
"""Read-only local dependency check; no installs and no model requests."""
import argparse,importlib.util,json,os,shutil,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--project',default='.');a=p.parse_args();project=Path(a.project).resolve()
checks={'python':{'ok':sys.version_info>=(3,9),'version':sys.version.split()[0]}}
for mod in ['numpy','scipy','PIL']:checks[mod]={'ok':importlib.util.find_spec(mod)is not None}
for binary in ['node','ffmpeg','ffprobe']:
 path=shutil.which(binary);checks[binary]={'ok':bool(path)}
 if path:
  r=subprocess.run([path,'--version'if binary=='node'else '-version'],capture_output=True,text=True)
  checks[binary]['version']=(r.stdout or r.stderr).splitlines()[0]
  if binary=='node':checks[binary]['ok']=int(checks[binary]['version'].lstrip('v').split('.')[0])>=20
node=shutil.which('node')
if node and project.is_dir():
 code="""const path=require('path');const m=require(require.resolve('@napi-rs/canvas',{paths:[process.argv[1]]}));const f=process.env.VIBE_FONT_PATH;const registered=f?m.GlobalFonts.registerFromPath(f,'VibeCJK'):null;const cn=registered?'VibeCJK':['Noto Sans CJK SC','Noto Sans SC','Source Han Sans SC','Hiragino Sans GB','PingFang SC','Microsoft YaHei'].find(x=>m.GlobalFonts.has(x));console.log(JSON.stringify({canvas:true,cjk_font:cn||null}));if(!cn)process.exitCode=2;"""
 r=subprocess.run([node,'-e',code,str(project)],capture_output=True,text=True)
 try:detail=json.loads(r.stdout.strip())
 except ValueError:detail={'canvas':False,'cjk_font':None}
 checks['canvas_and_cjk']={'ok':r.returncode==0,**detail}
else:checks['canvas_and_cjk']={'ok':False}
ok=all(v['ok']for v in checks.values());print(json.dumps({'passed':ok,'checks':checks,'agent_capabilities_not_tested':['research','image inspection','model tool use']},ensure_ascii=False,indent=2));sys.exit(0 if ok else 1)
