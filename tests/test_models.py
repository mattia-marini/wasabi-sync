"""Tests for selection building and counting."""

from __future__ import annotations

from pathlib import Path

from wasabi_sync.models import Entry, Project, build_selection, selection_counts


def _project(name: str, entry_count: int = 2) -> Project:
    return Project(
        key=name,
        name=name,
        folder=Path(f"/library/{name}"),
        entries=[
            Entry(
                key=f"{name}/track_{index}.wav",
                label=f"track_{index}",
                path=Path(f"/library/{name}/track_{index}.wav"),
            )
            for index in range(entry_count)
        ],
    )


def test_whole_project_selection():
    project = _project("a", 2)
    selection = build_selection([project], {"a"})
    assert selection == {"a": {"a/track_0.wav", "a/track_1.wav"}}


def test_partial_selection_excludes_parent():
    project = _project("a", 2)
    selection = build_selection([project], {"a/track_0.wav"})
    assert selection == {"a": {"a/track_0.wav"}}


def test_unchecked_projects_are_omitted():
    project = _project("a", 2)
    assert build_selection([project], set()) == {}


def test_project_without_entries_selects_whole_folder():
    project = _project("a", 0)
    assert build_selection([project], {"a"}) == {"a": set()}


def test_unknown_keys_are_ignored():
    project = _project("a", 1)
    assert build_selection([project], {"b", "a/unknown.wav"}) == {}


def test_selection_counts():
    selection = {"a": {"x", "y"}, "b": set()}
    assert selection_counts(selection) == (2, 2)
