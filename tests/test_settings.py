"""Tests for settings persistence."""

from __future__ import annotations

from wasabi_sync.settings import Settings


def test_load_missing_file_returns_defaults(store):
    settings = store.load()
    assert settings.projects_dir is None
    assert settings.exports_dir is None
    assert settings.reaper_path is None


def test_save_and_load_round_trip(store, tmp_path):
    store.save(
        Settings(
            projects_dir=tmp_path / "projects",
            exports_dir=tmp_path / "exports",
            reaper_path=tmp_path / "reaper.exe",
        )
    )
    settings = store.load()
    assert settings.projects_dir == tmp_path / "projects"
    assert settings.exports_dir == tmp_path / "exports"
    assert settings.reaper_path == tmp_path / "reaper.exe"


def test_save_creates_parent_directory_and_is_atomic(store):
    store.save(Settings(projects_dir=None))
    assert store.path.is_file()
    assert not (store.path.parent / "settings.json.tmp").exists()


def test_corrupt_file_returns_defaults(store):
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_text("{not json", encoding="utf-8")
    settings = store.load()
    assert settings.projects_dir is None


def test_non_string_values_are_ignored(store):
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_text('{"projects_dir": 42}', encoding="utf-8")
    settings = store.load()
    assert settings.projects_dir is None
