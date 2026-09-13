"""Tests for directory scanning."""

from __future__ import annotations

import pytest

from wasabi_sync.core.discovery import EXPECTED_ENTRY_COUNT, DiscoveryError, scan_projects


def test_scan_finds_projects_sorted(library):
    projects = scan_projects(library)
    assert [project.name for project in projects] == ["alpha", "bravo", "charlie"]


def test_entries_and_keys(library):
    projects = scan_projects(library)
    alpha = projects[0]
    assert len(alpha.entries) == EXPECTED_ENTRY_COUNT
    assert [entry.label for entry in alpha.entries] == [
        f"track_{index:02d}" for index in range(1, 6)
    ]
    assert alpha.entries[0].key == "alpha/track_01.wav"
    assert alpha.entries[0].path == alpha.folder / "track_01.wav"


def test_anomaly_flagged_for_wrong_count(library):
    projects = scan_projects(library)
    assert projects[0].anomaly is None
    assert projects[2].anomaly == "3/5 audio files"


def test_non_audio_files_are_not_entries(library):
    projects = scan_projects(library)
    charlie = projects[2]
    assert all(entry.path.suffix == ".wav" for entry in charlie.entries)


def test_hidden_and_empty_folders_are_skipped(library):
    names = [project.name for project in scan_projects(library)]
    assert ".hidden" not in names
    assert "empty_folder" not in names


def test_none_directory_returns_empty():
    assert scan_projects(None) == []


def test_missing_directory_raises(tmp_path):
    with pytest.raises(DiscoveryError):
        scan_projects(tmp_path / "missing")


def test_file_instead_of_directory_raises(tmp_path):
    target = tmp_path / "file.txt"
    target.touch()
    with pytest.raises(DiscoveryError):
        scan_projects(target)


def test_uppercase_extension_is_audio(tmp_path):
    folder = tmp_path / "caps"
    folder.mkdir()
    (folder / "STEM.WAV").touch()
    (folder / "notes.txt").touch()
    projects = scan_projects(tmp_path)
    assert [entry.path.name for entry in projects[0].entries] == ["STEM.WAV"]
