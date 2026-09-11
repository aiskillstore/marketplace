"""Target-aware local dependency checks; a passed check is not visual acceptance."""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path

MINIMUM_PYTHON=(3,10)
DEPENDENCIES={'pandas':'pandas','numpy':'numpy','openpyxl':'openpyxl','pptx':'python-pptx'}
MINIMUMS={'pandas':(2,2),'numpy':(1,26),'openpyxl':(3,1),'pptx':(1,0),
          'defusedxml':(0,7,1),'playwright':(1,40),'lxml':(4,9)}

def version_at_least(version, minimum):
    match=re.match(r'^(\d+(?:\.\d+)*)',version or '')
    if not match:return False
    parts=tuple(map(int,match[1].split('.')))
    n=max(len(parts),len(minimum))
    return parts+(0,)*(n-len(parts)) >= minimum+(0,)*(n-len(minimum))

def check_environment(target='html', *, node=None, slideviber_dir=None):
    if target not in {'html','standard','slideviber'}:raise ValueError('Unknown output target')
    required={k:v for k,v in DEPENDENCIES.items() if k!='pptx' or target!='html'}
    if target=='slideviber':required.update(defusedxml='defusedxml',playwright='playwright',lxml='lxml')
    dependencies={}
    for module,distribution in required.items():
        installed=importlib.util.find_spec(module) is not None
        try:version=metadata.version(distribution) if installed else None
        except metadata.PackageNotFoundError:version=None
        minimum=MINIMUMS[module];compatible=installed and version_at_least(version,minimum)
        dependencies[module]={'distribution':distribution,'installed':installed,'version':version,
                              'minimum':'.'.join(map(str,minimum)),'compatible':compatible}
    missing=[v['distribution'] for v in dependencies.values() if not v['installed']]
    incompatible=[v['distribution'] for v in dependencies.values() if v['installed'] and not v['compatible']]
    tools={};issues=[]
    if target!='html':
        executable=node or os.environ.get('RUNTIME_NODE') or shutil.which('node')
        good=False;version=None
        if executable:
            try:
                result=subprocess.run([str(executable),'--version'],capture_output=True,text=True,timeout=10,check=True)
                version=result.stdout.strip();good=version_at_least(version.lstrip('v'),(18,0))
            except (OSError,subprocess.SubprocessError):pass
        tools['node']={'path':str(executable) if executable else None,'version':version,'compatible':good,'minimum':'18.0'}
        if not good:issues.append('Node.js 18+ unavailable; install Node or pass --node PATH')
    if target=='slideviber':
        folder=slideviber_dir or os.environ.get('SLIDEVIBER_DIR')
        build=Path(folder)/'scripts/build.py' if folder else None
        good=bool(build and build.is_file())
        tools['slideviber']={'build':str(build) if build else None,'available':good}
        if not good:issues.append('SlideViber not located; install separately and pass --slideviber-dir PATH')
    python_ok=sys.version_info>=MINIMUM_PYTHON
    passed=python_ok and not missing and not incompatible and not issues
    next_steps=[]
    if not python_ok:
        next_steps.append('安装 Python 3.10 或更高版本，并确认当前命令使用的是该解释器')
    if missing or incompatible:
        affected=missing+incompatible
        next_steps.append(
            '安装或升级当前目标所需的 Python 包：'+', '.join(affected)
            +'；可运行 python -m pip install -r requirements.txt'
        )
    if target!='html' and not tools.get('node',{}).get('compatible'):
        next_steps.append('安装 Node.js 18 或更高版本，或通过 --node 指定可执行文件')
    if target=='slideviber' and not tools.get('slideviber',{}).get('available'):
        next_steps.append('单独安装 SlideViber，并通过 --slideviber-dir 指定其目录；不需要美化版时可跳过')
    if not next_steps:
        next_steps.append('环境依赖已通过；继续生成后仍需检查字体、排版和实际文件')
    return {'status':'passed' if passed else 'failed','target':target,
            'python':{'version':platform.python_version(),'required_major':3,'required_minor':10,'compatible':python_ok},
            'dependencies':dependencies,'missing_dependencies':missing,'incompatible_dependencies':incompatible,
            'tools':tools,'issues':issues,
            'user_summary':('环境预检通过，可以继续当前目标。' if passed else
                            '环境预检未通过；请先完成下方最小修复，再继续当前目标。'),
            'next_steps':next_steps,
            'install_command':None if not missing and not incompatible else 'python -m pip install -r requirements.txt',
            'additional_requirements':'Install the separately obtained SlideViber requirements.txt' if target=='slideviber' else None,
            'not_verified':['font_availability','actual_visual_rendering','native_app_editing']+
                (['SlideViber_browser_launch'] if target=='slideviber' else [])}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--target',choices=['html','standard','slideviber'],default='html')
    ap.add_argument('--node');ap.add_argument('--slideviber-dir',type=Path);ap.add_argument('--output',type=Path)
    a=ap.parse_args();result=check_environment(a.target,node=a.node,slideviber_dir=a.slideviber_dir)
    payload=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open('x',encoding='utf-8') as stream:stream.write(payload)
    print(payload);return 0 if result['status']=='passed' else 1

if __name__=='__main__':raise SystemExit(main())
