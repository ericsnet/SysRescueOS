# SysRescueOS

**A Linux-based rescue environment focused on PC diagnostics, hardware testing, system recovery, and repair workflows.**

SysRescueOS is an early-stage project. The first milestone is a small, read-only diagnostic toolkit that can later become part of a bootable Linux live environment.

## Current status

The repository currently contains the first diagnostic prototype:

- System identity: distribution, kernel, architecture, hostname, and CPU.
- Memory snapshot: total, available, and estimated used RAM.
- Storage overview: root filesystem usage and block-device metadata when `lsblk` is available.
- Network overview: interface names, operational state, and MAC addresses.
- Text and JSON report output.

The collectors are designed to be **read-only**. They do not format disks, change partitions, edit system configuration, or attempt automatic repairs.

## Requirements

- Linux for full diagnostic coverage.
- Python 3.10 or newer.
- Optional: `lsblk` (usually provided by `util-linux`) for block-device details.

Some fields may be unavailable when the operating system does not expose the corresponding Linux interfaces.

## Run from source

```bash
python -m pip install -e .
sysrescue
```

Generate a machine-readable report:

```bash
sysrescue --json
```

You can also run the module without installing the package:

```bash
PYTHONPATH=src python -m sysrescue.cli
```

## Development

Run the tests with:

```bash
python -m pip install pytest
python -m pytest
```

## Roadmap

- [x] Initial read-only diagnostic CLI.
- [ ] Hardware inventory and richer CPU/GPU details.
- [ ] SMART health data where supported.
- [ ] Diagnostic bundles that can be exported for troubleshooting.
- [ ] Guided recovery tools with explicit confirmation and safety checks.
- [ ] Bootable live image and hardware compatibility testing.

## Design principles

1. **Diagnose before changing anything.**
2. Never run destructive operations automatically.
3. Make privileged actions explicit and explain their impact.
4. Keep diagnostic output exportable and reproducible.
5. Prefer modular tools that can be tested independently.

## Project status

Experimental. Do not rely on this prototype as the sole recovery method for an important system.

## License

MIT. See [LICENSE](LICENSE).
