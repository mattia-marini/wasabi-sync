"""Tests for the stub submit actions."""

from __future__ import annotations

from wasabi_sync.core.actions import ExportAction, LiveAction
from wasabi_sync.settings import Settings

SELECTION = {
    "alpha": {"alpha/track_0.wav", "alpha/track_1.wav"},
    "bravo": set(),
}


def test_export_stub_report():
    report = ExportAction().run(SELECTION, Settings())
    assert report.ok is True
    assert "2 project(s) / 2 entr(ies)" in report.message
    assert "step 2" in report.message
    assert report.details == ("alpha: 2 entries", "bravo: whole folder")


def test_live_stub_report():
    report = LiveAction().run(SELECTION, Settings())
    assert report.ok is True
    assert "2 project(s)" in report.message
    assert "step 2" in report.message


def test_empty_selection_reports_zero():
    report = ExportAction().run({}, Settings())
    assert "0 project(s) / 0 entr(ies)" in report.message
    assert report.details == ()
