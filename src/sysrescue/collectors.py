"""Read-only collectors for basic Linux system diagnostics."""

from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
from pathlib import Path
from typing import Any


def read_text(path: str | Path) -> str | None:
    """Read a text file without raising when it is unavailable."""
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").strip()
    except (OSError, UnicodeError):
        return None


def run_read_only(command: list[str], timeout: float = 3.0) -> str | None:
    """Run a fixed, read-only system command without invoking a shell."""
    if not command or not isinstance(command, list):
        return None

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            shell=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None
    return result.stdout.strip()


def parse_meminfo(content: str) -> dict[str, int]:
    """Parse Linux /proc/meminfo values into KiB."""
    values: dict[str, int] = {}
    for line in content.splitlines():
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        parts = raw_value.strip().split()
        if not parts:
            continue
        try:
            values[key] = int(parts[0])
        except ValueError:
            continue
    return values


def collect_system() -> dict[str, Any]:
    distro = "Unknown"
    os_release = read_text("/etc/os-release")
    if os_release:
        for line in os_release.splitlines():
            if line.startswith("PRETTY_NAME="):
                distro = line.partition("=")[2].strip().strip('"')
                break

    cpu_name = None
    cpuinfo = read_text("/proc/cpuinfo")
    if cpuinfo:
        for line in cpuinfo.splitlines():
            if line.lower().startswith(("model name", "hardware")) and ":" in line:
                cpu_name = line.split(":", 1)[1].strip()
                break

    return {
        "hostname": socket.gethostname(),
        "distribution": distro,
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "cpu": cpu_name or platform.processor() or "Unknown",
        "python": platform.python_version(),
    }


def collect_memory() -> dict[str, int | None]:
    raw = read_text("/proc/meminfo")
    if not raw:
        return {"total_kib": None, "available_kib": None, "used_kib": None}

    values = parse_meminfo(raw)
    total = values.get("MemTotal")
    available = values.get("MemAvailable")
    used = total - available if total is not None and available is not None else None
    return {
        "total_kib": total,
        "available_kib": available,
        "used_kib": used,
    }


def collect_storage() -> dict[str, Any]:
    root_usage = None
    try:
        usage = shutil.disk_usage("/")
        root_usage = {
            "total_bytes": usage.total,
            "used_bytes": usage.used,
            "free_bytes": usage.free,
        }
    except OSError:
        pass

    raw_disks = run_read_only(
        ["lsblk", "--json", "--bytes", "--output", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL"]
    )
    disks: list[dict[str, Any]] = []
    if raw_disks:
        try:
            parsed = json.loads(raw_disks)
            disks = parsed.get("blockdevices", [])
        except (json.JSONDecodeError, AttributeError):
            disks = []

    return {"root_filesystem": root_usage, "devices": disks}


def collect_network() -> list[dict[str, str | None]]:
    interfaces: list[dict[str, str | None]] = []
    net_root = Path("/sys/class/net")
    try:
        names = sorted(item.name for item in net_root.iterdir() if item.name != "lo")
    except OSError:
        return interfaces

    for name in names:
        interfaces.append(
            {
                "name": name,
                "state": read_text(net_root / name / "operstate"),
                "mac_address": read_text(net_root / name / "address"),
            }
        )
    return interfaces


def collect_report() -> dict[str, Any]:
    """Collect a compact diagnostic snapshot. No system changes are made."""
    return {
        "schema_version": 1,
        "system": collect_system(),
        "memory": collect_memory(),
        "storage": collect_storage(),
        "network": collect_network(),
    }
