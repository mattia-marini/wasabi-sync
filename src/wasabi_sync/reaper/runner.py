"""Locating the REAPER executable on the three supported platforms."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def default_candidates(platform: str = sys.platform) -> list[Path]:
    """Well-known install locations for the REAPER binary."""
    if platform == "win32":
        return [
            Path(r"C:\Program Files\REAPER (x64)\reaper.exe"),
            Path(r"C:\Program Files\REAPER\reaper.exe"),
            Path(r"C:\Program Files (x86)\REAPER\reaper.exe"),
        ]
    if platform == "darwin":
        return [Path("/Applications/REAPER.app/Contents/MacOS/REAPER")]
    return [
        Path("/usr/bin/reaper"),
        Path("/usr/local/bin/reaper"),
        Path.home() / ".local" / "bin" / "reaper",
    ]


def locate_reaper(
    explicit: Path | None,
    candidates: list[Path] | None = None,
) -> Path | None:
    """Return the REAPER executable path, or ``None`` when not found.

    ``explicit`` (from the settings) wins when it points at a file;
    otherwise the well-known locations and ``$PATH`` are probed.
    """
    if explicit is not None:
        explicit = Path(explicit)
        if explicit.is_file():
            return explicit
    for candidate in candidates if candidates is not None else default_candidates():
        if candidate.is_file():
            return candidate
    on_path = shutil.which("reaper")
    return Path(on_path) if on_path else None
