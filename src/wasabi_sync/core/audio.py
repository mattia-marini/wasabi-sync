"""Audio file classification used by the project scanners."""

from __future__ import annotations

from pathlib import Path

AUDIO_EXTENSIONS = frozenset(
    {
        ".aac",
        ".aif",
        ".aifc",
        ".aiff",
        ".flac",
        ".m4a",
        ".mp3",
        ".ogg",
        ".opus",
        ".w64",
        ".wav",
        ".wma",
    }
)


def is_audio_file(path: Path) -> bool:
    """True when *path* looks like an audio file REAPER could import."""
    return path.suffix.lower() in AUDIO_EXTENSIONS
