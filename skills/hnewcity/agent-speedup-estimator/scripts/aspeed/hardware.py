from __future__ import annotations

import json
import os
import platform
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

DISK_RANK = {"unknown": 0, "hdd": 1, "sata": 2, "nvme": 3, "nvme_gen4": 4}

_WIN_SCRIPT = (
    "$c = Get-CimInstance Win32_Processor | Select-Object -First 1; "
    "$m = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory; "
    "$d = @(Get-PhysicalDisk -ErrorAction SilentlyContinue | ForEach-Object { '' + $_.BusType + '/' + $_.MediaType }); "
    "ConvertTo-Json -Compress @{name=$c.Name; cores=$c.NumberOfCores; threads=$c.NumberOfLogicalProcessors; ram=$m; disks=$d}"
)


@dataclass
class Hardware:
    cpu_name: str = ""
    cores: int = 0
    threads: int = 0
    ram_gb: float = 0.0
    disk_class: str = "unknown"
    os_name: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def _run(args: List[str], timeout: int = 25) -> str:
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout if r.returncode == 0 else ""


def _disk_from_label(label: str) -> str:
    s = label.lower()
    if "nvme" in s:
        return "nvme"
    if "hdd" in s or "unspecified/hdd" in s:
        return "hdd"
    if "sata" in s or "ssd" in s or "sas" in s:
        return "sata"
    return "unknown"


def _best_disk(classes: List[str]) -> str:
    return max(classes, key=lambda c: DISK_RANK.get(c, 0)) if classes else "unknown"


def _windows() -> Hardware:
    hw = Hardware(os_name="Windows " + platform.release())
    out = _run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", _WIN_SCRIPT])
    try:
        d = json.loads(out)
    except ValueError:
        return hw
    hw.cpu_name = str(d.get("name") or "").strip()
    hw.cores = int(d.get("cores") or 0)
    hw.threads = int(d.get("threads") or 0)
    hw.ram_gb = round(float(d.get("ram") or 0) / 1024 ** 3, 1)
    disks = d.get("disks") or []
    if isinstance(disks, str):
        disks = [disks]
    hw.disk_class = _best_disk([_disk_from_label(x) for x in disks])
    return hw


def _linux() -> Hardware:
    hw = Hardware(os_name="Linux " + platform.release(), threads=os.cpu_count() or 0)
    try:
        text = Path("/proc/cpuinfo").read_text(errors="replace")
    except OSError:
        text = ""
    m = re.search(r"^model name\s*:\s*(.+)$", text, re.M)
    hw.cpu_name = m.group(1).strip() if m else ""
    cores = {(a, b) for a, b in zip(re.findall(r"^physical id\s*:\s*(\d+)", text, re.M), re.findall(r"^core id\s*:\s*(\d+)", text, re.M))}
    hw.cores = len(cores) or hw.threads
    try:
        mem = re.search(r"MemTotal:\s*(\d+)\s*kB", Path("/proc/meminfo").read_text())
        hw.ram_gb = round(int(mem.group(1)) / 1024 ** 2, 1) if mem else 0.0
    except OSError:
        pass
    classes = []
    for p in Path("/sys/block").glob("*") if Path("/sys/block").is_dir() else []:
        n = p.name
        if n.startswith(("loop", "ram", "zram", "dm-", "sr")):
            continue
        try:
            rot = (p / "queue" / "rotational").read_text().strip()
        except OSError:
            continue
        classes.append("nvme" if n.startswith("nvme") else "hdd" if rot == "1" else "sata")
    hw.disk_class = _best_disk(classes)
    return hw


def _mac() -> Hardware:
    hw = Hardware(os_name="macOS " + platform.mac_ver()[0])
    hw.cpu_name = _run(["sysctl", "-n", "machdep.cpu.brand_string"]).strip()
    for key, attr in (("hw.physicalcpu", "cores"), ("hw.logicalcpu", "threads")):
        v = _run(["sysctl", "-n", key]).strip()
        setattr(hw, attr, int(v) if v.isdigit() else 0)
    mem = _run(["sysctl", "-n", "hw.memsize"]).strip()
    hw.ram_gb = round(int(mem) / 1024 ** 3, 1) if mem.isdigit() else 0.0
    hw.disk_class = "nvme"
    return hw


def detect() -> Hardware:
    system = platform.system()
    if system == "Windows":
        return _windows()
    if system == "Darwin":
        return _mac()
    return _linux()
