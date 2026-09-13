"""Tests for REAPER executable discovery."""

from __future__ import annotations

from wasabi_sync.reaper.runner import default_candidates, locate_reaper


def test_explicit_path_wins(tmp_path):
    exe = tmp_path / "reaper.exe"
    exe.touch()
    other = tmp_path / "other"
    other.touch()
    assert locate_reaper(exe, candidates=[other]) == exe


def test_falls_back_to_candidates(tmp_path, monkeypatch):
    monkeypatch.setattr("wasabi_sync.reaper.runner.shutil.which", lambda _: None)
    exe = tmp_path / "found"
    exe.touch()
    assert locate_reaper(None, candidates=[tmp_path / "missing", exe]) == exe


def test_missing_explicit_path_falls_through(tmp_path, monkeypatch):
    monkeypatch.setattr("wasabi_sync.reaper.runner.shutil.which", lambda _: None)
    exe = tmp_path / "found"
    exe.touch()
    assert locate_reaper(tmp_path / "nope", candidates=[exe]) == exe


def test_returns_none_when_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr("wasabi_sync.reaper.runner.shutil.which", lambda _: None)
    assert locate_reaper(None, candidates=[]) is None


def test_path_lookup_fallback(tmp_path, monkeypatch):
    exe = tmp_path / "on-path"
    exe.touch()
    monkeypatch.setattr("wasabi_sync.reaper.runner.shutil.which", lambda _: str(exe))
    assert locate_reaper(None, candidates=[]) == exe


def test_default_candidates_cover_all_platforms():
    assert all("reaper" in str(path).lower() for path in default_candidates("win32"))
    assert all("REAPER" in str(path) for path in default_candidates("darwin"))
    assert all("reaper" in str(path) for path in default_candidates("linux"))
