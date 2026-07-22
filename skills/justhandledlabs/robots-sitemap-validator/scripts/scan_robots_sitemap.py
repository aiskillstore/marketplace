#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

IGNORE_DIRS={".git","node_modules","dist","build","vendor","__pycache__"}
KNOWN={"user-agent","allow","disallow","sitemap","crawl-delay","host"}

def should_read(path: Path)->bool:
    name=path.name.lower()
    return name=="robots.txt" or (name.startswith("sitemap") and name.endswith(".xml"))

def iter_files(paths, stdin_text=None):
    if stdin_text is not None:
        yield Path("stdin"), stdin_text, None
    for raw in paths:
        p=Path(raw)
        if not p.exists(): yield p,"","missing"; continue
        if p.is_file():
            if should_read(p): yield p,p.read_text(encoding="utf-8",errors="replace"),None
            continue
        for child in p.rglob("*"):
            if child.is_file() and should_read(child) and not any(part in IGNORE_DIRS for part in child.parts):
                yield child,child.read_text(encoding="utf-8",errors="replace"),None

def add(findings,code,severity,path,line,message,excerpt):
    findings.append({"code":code,"severity":severity,"file":str(path),"line":line,"message":message,"excerpt":" ".join(str(excerpt).split())[:220]})

def scan_robots(path,text,findings):
    has_sitemap=False
    for lineno,line in enumerate(text.splitlines(),1):
        stripped=line.strip()
        if not stripped or stripped.startswith("#"): continue
        if ":" not in stripped:
            add(findings,"RSV002","medium",path,lineno,"Robots directive line is malformed.",stripped); continue
        key,value=stripped.split(":",1); low=key.strip().lower(); val=value.strip()
        if low not in KNOWN:
            add(findings,"RSV002","low",path,lineno,"Unknown robots directive.",stripped)
        if low=="disallow" and val=="/":
            add(findings,"RSV001","high",path,lineno,"robots.txt blocks the whole site.",stripped)
        if low=="sitemap":
            has_sitemap=True
            local=Path(urlparse(val).path).name
            if local and path.name!="stdin" and not (path.parent/local).exists():
                add(findings,"RSV004","low",path,lineno,"Sitemap directive points to a sibling file not present locally.",val)
    if not has_sitemap:
        add(findings,"RSV003","medium",path,1,"robots.txt has no Sitemap directive.","missing Sitemap")

def loc_texts(root):
    for node in root.iter():
        if node.tag.endswith("loc") and node.text:
            yield node.text.strip()

def scan_sitemap(path,text,findings):
    try:
        root=ET.fromstring(text)
    except ET.ParseError as exc:
        add(findings,"RSV005","high",path,getattr(exc.position,"__getitem__",lambda i:1)(0) if hasattr(exc,"position") else 1,"Sitemap XML is not well formed.",str(exc)); return
    locs=list(loc_texts(root)); schemes=set()
    for loc in locs:
        parsed=urlparse(loc)
        if not parsed.scheme or not parsed.netloc:
            add(findings,"RSV006","medium",path,1,"Sitemap loc is not an absolute URL with a scheme.",loc)
        if parsed.scheme in {"http","https"}: schemes.add(parsed.scheme)
    if len(locs)>50000 or len(text.encode("utf-8"))>50_000_000:
        add(findings,"RSV007","medium",path,1,"Sitemap exceeds common size or URL count guidance.",f"{len(locs)} URLs")
    if len(schemes)>1:
        add(findings,"RSV008","low",path,1,"Sitemap mixes http and https loc URLs.",", ".join(sorted(schemes)))

def scan(paths=None, stdin_text=None):
    paths=paths or []
    findings=[]; missing=[]; scanned=0
    for path,text,error in iter_files(paths, stdin_text):
        if error: missing.append(str(path)); continue
        scanned+=1
        if path.name.lower()=="robots.txt" or path.name=="stdin": scan_robots(path,text,findings)
        if path.name.lower().startswith("sitemap") or "<urlset" in text: scan_sitemap(path,text,findings)
    return {"scanner":"robots-sitemap-validator","files_scanned":scanned,"missing_paths":missing,"findings":findings}

def print_markdown(result):
    print("# Robots Sitemap Validator Report\n")
    print(f"Files scanned: {result['files_scanned']}\nFindings: {len(result['findings'])}\n")
    for item in result["findings"]:
        print(f"## [{item['severity'].upper()}] {item['code']} - {item['file']}:{item['line']}\n{item['message']}\n")

def main():
    ap=argparse.ArgumentParser(description="Read-only robots and sitemap validator.")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--stdin", action="store_true")
    ap.add_argument("--format", choices=["markdown","json"], default="markdown")
    args=ap.parse_args(); stdin_text=sys.stdin.read() if args.stdin else None
    result=scan(args.paths, stdin_text)
    print(json.dumps(result, indent=2) if args.format=="json" else "", end="")
    if args.format=="markdown": print_markdown(result)
if __name__=="__main__": main()
