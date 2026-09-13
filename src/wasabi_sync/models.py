"""Pure data models shared across wasabi-sync.

These dataclasses carry no UI or I/O concerns so they can be used freely
from the core modules, the views, and the tests.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class EntryStatus(StrEnum):
    """Validation status of an entry or a project (LIVE tab)."""

    UNKNOWN = "unknown"
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Entry:
    """A selectable item inside a project.

    On the Export tab an entry is a track that sends audio directly to
    the master (``muted`` reflects its current state); on the LIVE tab it
    is an audio file (``path`` points at the file).
    """

    key: str
    label: str
    path: Path | None = None
    status: EntryStatus = EntryStatus.UNKNOWN
    detail: str | None = None
    muted: bool = False


@dataclass
class Project:
    """A project folder discovered in one of the configured directories."""

    key: str
    name: str
    folder: Path
    entries: list[Entry] = field(default_factory=list)
    anomaly: str | None = None
    status: EntryStatus = EntryStatus.UNKNOWN
    detail: str | None = None
    rpp_path: Path | None = None


type Selection = dict[str, set[str]]
"""Selected entry keys grouped by project key."""


def build_selection(projects: Iterable[Project], checked: set[str]) -> Selection:
    """Convert flat checked node keys into a per-project selection.

    A project key inside *checked* selects the whole project; otherwise
    only its checked entry keys are selected. Projects without any
    checked content are omitted. A project without selectable entries
    gets an empty entry set, meaning the whole folder.
    """
    selection: Selection = {}
    for project in projects:
        if project.key in checked:
            selection[project.key] = {entry.key for entry in project.entries}
            continue
        entry_keys = {entry.key for entry in project.entries if entry.key in checked}
        if entry_keys:
            selection[project.key] = entry_keys
    return selection


def selection_counts(selection: Selection) -> tuple[int, int]:
    """Return ``(projects, entries)`` counts for a selection."""
    return len(selection), sum(len(keys) for keys in selection.values())
