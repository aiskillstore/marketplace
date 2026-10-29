#!/usr/bin/env python3
"""Probe Resolve, or import XML only into an explicitly named empty project."""
import argparse
import importlib
import json
import sys
from pathlib import Path


def connect(modules=None):
    if modules:
        sys.path.insert(0, str(Path(modules).resolve()))
    elif sys.platform == 'darwin':
        sys.path.append('/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules')
    bmd = importlib.import_module('DaVinciResolveScript')
    resolve = bmd.scriptapp('Resolve')
    if not resolve:
        raise RuntimeError('No Resolve connection. Open Resolve and check local scripting access.')
    return resolve


def guarded_import(resolve, xml, expected):
    manager = resolve.GetProjectManager()
    project = manager.GetCurrentProject()
    if not project or project.GetName() != expected:
        raise RuntimeError('Open the explicitly named empty demo project first. No project was changed.')
    pool = project.GetMediaPool(); folder = pool.GetRootFolder()
    if project.GetTimelineCount() or folder.GetClipList() or folder.GetSubFolderList():
        raise RuntimeError('Refusing import into a populated project. No project was changed.')
    timeline = pool.ImportTimelineFromFile(str(Path(xml).resolve()))
    if not timeline:
        raise RuntimeError('Import failed. Inspect the demo project; rollback is not claimed.')
    if not manager.SaveProject():
        raise RuntimeError('Timeline imported but project save failed.')
    return {'project': expected, 'timeline': timeline.GetName(), 'saved': True,
            'verification': 'Import only; media relinking, frames and rendered playback still need review.'}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--modules')
    sub = p.add_subparsers(dest='command', required=True); sub.add_parser('probe')
    imp = sub.add_parser('import-xml'); imp.add_argument('xml', type=Path); imp.add_argument('--project', required=True)
    a = p.parse_args()
    try:
        if a.command == 'import-xml' and not a.xml.is_file():
            raise FileNotFoundError(a.xml)
        resolve = connect(a.modules)
        if a.command == 'probe':
            current = resolve.GetProjectManager().GetCurrentProject()
            result = {'connected': True, 'version': resolve.GetVersionString(),
                      'current_project': current.GetName() if current else None, 'modified': False}
        else:
            result = guarded_import(resolve, a.xml, a.project)
        print(json.dumps(result, indent=2))
    except Exception as error:
        p.exit(1, f'Unavailable or refused: {error}\n')


if __name__ == '__main__':
    main()
