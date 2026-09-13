"""Tests for the validation framework."""

from __future__ import annotations

from pathlib import Path

from wasabi_sync.core.validation import (
    EntryCountRule,
    Finding,
    apply_findings,
    default_rules,
    run_validations,
)
from wasabi_sync.models import Entry, EntryStatus, Project


def _project(entry_count: int = 5) -> Project:
    return Project(
        key="p",
        name="p",
        folder=Path("/library/p"),
        entries=[
            Entry(
                key=f"p/track_{index}.wav",
                label=f"track_{index}",
                path=Path(f"/library/p/track_{index}.wav"),
            )
            for index in range(entry_count)
        ],
    )


def test_entry_count_rule_ok():
    findings = EntryCountRule().check(_project(5))
    assert findings == [Finding(entry_key=None, status=EntryStatus.OK, detail="5 audio files")]


def test_entry_count_rule_warns_on_wrong_count():
    finding = EntryCountRule().check(_project(3))[0]
    assert finding.status is EntryStatus.WARNING
    assert "3/5 audio files" in finding.detail


def test_default_rules_apply_to_project_status():
    project = _project(5)
    run_validations([project], default_rules())
    assert project.status is EntryStatus.OK
    assert project.detail == "5 audio files"


def test_apply_findings_maps_entry_findings():
    project = _project(2)
    apply_findings(
        project,
        [
            Finding(entry_key="p/track_0.wav", status=EntryStatus.ERROR, detail="missing"),
            Finding(entry_key=None, status=EntryStatus.WARNING, detail="project-level"),
        ],
    )
    assert project.entries[0].status is EntryStatus.ERROR
    assert project.entries[0].detail == "missing"
    assert project.entries[1].status is EntryStatus.UNKNOWN
    assert project.status is EntryStatus.WARNING
    assert project.detail == "project-level"


def test_apply_findings_keeps_worst_project_status():
    project = _project(1)
    apply_findings(
        project,
        [
            Finding(entry_key=None, status=EntryStatus.OK, detail="a"),
            Finding(entry_key=None, status=EntryStatus.ERROR, detail="b"),
        ],
    )
    assert project.status is EntryStatus.ERROR
    assert project.detail == "a; b"


def test_apply_findings_resets_previous_state():
    project = _project(1)
    project.status = EntryStatus.ERROR
    project.entries[0].status = EntryStatus.ERROR
    apply_findings(project, [])
    assert project.status is EntryStatus.UNKNOWN
    assert project.entries[0].status is EntryStatus.UNKNOWN
