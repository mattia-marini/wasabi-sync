"""Shared fixtures and helpers for the wasabi-sync test suite."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from wasabi_sync.settings import SettingsStore


def make_project(
    directory: Path,
    name: str,
    audio_count: int = 5,
    extra_files: tuple[str, ...] = (),
) -> Path:
    """Create a project folder with *audio_count* audio files inside."""
    folder = directory / name
    folder.mkdir(parents=True)
    for index in range(audio_count):
        (folder / f"track_{index + 1:02d}.wav").touch()
    for extra in extra_files:
        (folder / extra).touch()
    return folder


@pytest.fixture
def library(tmp_path: Path) -> Path:
    """A directory with three projects, junk files, and hidden/empty folders."""
    root = tmp_path / "audio"
    make_project(root, "alpha")
    make_project(root, "bravo")
    make_project(root, "charlie", audio_count=3, extra_files=("notes.txt",))
    make_project(root, ".hidden")
    (root / "empty_folder").mkdir()
    (root / "stray.txt").write_text("not a folder")
    return root


def _rpp_content(tracks: list[tuple[str, bool, bool]]) -> str:
    """Render a minimal .rpp with the given ``(name, muted, sends_to_master)`` tracks."""
    lines = ['<REAPER_PROJECT 0.1 "7.0" 1710000000']
    for name, muted, sends_to_master in tracks:
        mute = "1" if muted else "0"
        main = "1" if sends_to_master else "0"
        lines.append("  <TRACK {12345678-1234-1234-1234-1234567890AB}")
        lines.append(f'    NAME "{name}"')
        lines.append(f"    MUTESOLO {mute} 0 0")
        lines.append(f"    MAINSEND {main} 0")
        lines.append("  >")
    lines.append(">")
    return "\n".join(lines) + "\n"


@pytest.fixture
def build_rpp():
    return _rpp_content


def make_rpp_project(
    directory: Path,
    name: str,
    tracks: list[tuple[str, bool, bool]],
) -> Path:
    """Create a project folder containing a single .rpp with the given tracks."""
    folder = directory / name
    folder.mkdir(parents=True)
    (folder / f"{name}.rpp").write_text(_rpp_content(tracks), encoding="utf-8")
    return folder


@pytest.fixture
def rpp_library(tmp_path: Path) -> Path:
    """Three .rpp projects (5/5/3 master tracks) plus a folder without an .rpp."""
    root = tmp_path / "rpp"
    make_rpp_project(root, "alpha", [(f"track_{i:02d}", False, True) for i in range(1, 6)])
    make_rpp_project(
        root,
        "bravo",
        [
            ("track_01", False, True),
            ("track_02", False, True),
            ("track_03", False, True),
            ("track_04", False, True),
            ("track_05", True, True),
        ],
    )
    make_rpp_project(
        root,
        "charlie",
        [
            ("track_01", False, True),
            ("track_02", False, True),
            ("track_03", False, True),
            ("bus_01", False, False),
            ("bus_02", False, False),
        ],
    )
    (root / "no_rpp").mkdir()
    (root / "stray.txt").write_text("not a folder")
    return root


@pytest.fixture
def store(tmp_path: Path) -> Iterator[SettingsStore]:
    yield SettingsStore(tmp_path / "config" / "settings.json")
