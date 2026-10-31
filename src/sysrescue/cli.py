"""Command-line interface for SysRescueOS."""

from __future__ import annotations

import argparse
import json
from typing import Any

from . import __version__
from .collectors import collect_report


def format_bytes(value: int | None) -> str:
    if value is None:
        return "Unavailable"
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1000 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1000
    return f"{size:.1f} TB"


def format_memory(value: int | None) -> str:
    if value is None:
        return "Unavailable"
    return format_bytes(value * 1024)


def render_text(report: dict[str, Any]) -> str:
    system = report["system"]
    memory = report["memory"]
    storage = report["storage"]

    lines = [
        f"SysRescueOS Diagnostics v{__version__}",
        "=" * 36,
        "",
        "SYSTEM",
        f"  Host:           {system['hostname']}",
        f"  Distribution:   {system['distribution']}",
        f"  Kernel:         {system['kernel']}",
        f"  Architecture:   {system['architecture']}",
        f"  CPU:            {system['cpu']}",
        "",
        "MEMORY",
        f"  Total:          {format_memory(memory['total_kib'])}",
        f"  Available:      {format_memory(memory['available_kib'])}",
        f"  Used:           {format_memory(memory['used_kib'])}",
        "",
        "STORAGE",
    ]

    root = storage["root_filesystem"]
    if root:
        lines.extend(
            [
                f"  Root total:     {format_bytes(root['total_bytes'])}",
                f"  Root used:      {format_bytes(root['used_bytes'])}",
                f"  Root free:      {format_bytes(root['free_bytes'])}",
            ]
        )
    else:
        lines.append("  Root filesystem: Unavailable")

    lines.extend(["", "NETWORK"])
    if report["network"]:
        for interface in report["network"]:
            lines.append(
                f"  {interface['name']}: state={interface['state'] or 'unknown'}, "
                f"MAC={interface['mac_address'] or 'unknown'}"
            )
    else:
        lines.append("  No network interfaces found.")

    lines.extend(
        [
            "",
            "NOTE: This report is informational. No repairs or system changes were performed.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="sysrescue",
        description="Collect a read-only snapshot of basic PC diagnostics.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the report as JSON instead of formatted text.",
    )
    args = parser.parse_args()

    report = collect_report()
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_text(report))


if __name__ == "__main__":
    main()
