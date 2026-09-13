"""Tests for the submit actions."""

from __future__ import annotations

from wasabi_sync.core.actions import ExportAction, LiveAction
from wasabi_sync.models import Project, Selection
from wasabi_sync.reaper.rpp import parse_rpp
from wasabi_sync.settings import Settings


def _project(name: str, rpp_path) -> Project:
    return Project(key=name, name=name, folder=rpp_path.parent, rpp_path=rpp_path)


def test_export_action_unmutes_muted_master_tracks(tmp_path, build_rpp):
    rpp = tmp_path / "song" / "song.rpp"
    rpp.parent.mkdir()
    rpp.write_text(
        build_rpp(
            [
                ("Drums", False, True),
                ("Bass", True, True),  # muted master → should be unmuted
                ("Keys", True, False),  # muted, not master → untouched
            ]
        ),
        encoding="utf-8",
    )
    projects = [_project("song", rpp)]
    selection: Selection = {"song": set()}
    report = ExportAction().run(projects, selection, Settings())

    assert report.ok is True
    assert "1 track(s)" in report.message
    tracks = {track.name: track for track in parse_rpp(rpp.read_text()).tracks}
    assert tracks["Bass"].muted is False
    assert tracks["Drums"].muted is False
    assert tracks["Keys"].muted is True


def test_export_action_skips_unselected_projects(tmp_path, build_rpp):
    a = tmp_path / "a" / "a.rpp"
    b = tmp_path / "b" / "b.rpp"
    a.parent.mkdir()
    b.parent.mkdir()
    a.write_text(build_rpp([("t", True, True)]), encoding="utf-8")
    b.write_text(build_rpp([("t", True, True)]), encoding="utf-8")

    projects = [_project("a", a), _project("b", b)]
    report = ExportAction().run(projects, {"a": set()}, Settings())

    assert report.ok is True
    assert parse_rpp(a.read_text()).tracks[0].muted is False
    assert parse_rpp(b.read_text()).tracks[0].muted is True  # untouched


def test_export_action_reports_already_unmuted(tmp_path, build_rpp):
    rpp = tmp_path / "x" / "x.rpp"
    rpp.parent.mkdir()
    rpp.write_text(build_rpp([("t", False, True)]), encoding="utf-8")

    report = ExportAction().run([_project("x", rpp)], {"x": set()}, Settings())
    assert report.ok is True
    assert "0 track(s)" in report.message
    assert any("no muted master tracks" in detail for detail in report.details)


def test_export_action_flags_missing_rpp(tmp_path):
    project = Project(key="x", name="x", folder=tmp_path / "x")
    report = ExportAction().run([project], {"x": set()}, Settings())
    assert report.ok is False
    assert "failed" in report.message


def test_live_stub_report():
    selection: Selection = {
        "alpha": {"alpha/track_0.wav", "alpha/track_1.wav"},
        "bravo": set(),
    }
    report = LiveAction().run([], selection, Settings())
    assert report.ok is True
    assert "2 project(s)" in report.message
    assert "step 2" in report.message
