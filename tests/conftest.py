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
    make_project(tmp_path, "alpha")
    make_project(tmp_path, "bravo")
    make_project(tmp_path, "charlie", audio_count=3, extra_files=("notes.txt",))
    make_project(tmp_path, ".hidden")
    (tmp_path / "empty_folder").mkdir()
    (tmp_path / "stray.txt").write_text("not a folder")
    return tmp_path


@pytest.fixture
def store(tmp_path: Path) -> Iterator[SettingsStore]:
    yield SettingsStore(tmp_path / "config" / "settings.json")
