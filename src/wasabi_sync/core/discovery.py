"""Scan a directory into project listings."""

from __future__ import annotations

import logging
from pathlib import Path

from wasabi_sync.core.audio import is_audio_file
from wasabi_sync.models import Entry, Project

logger = logging.getLogger(__name__)

EXPECTED_ENTRY_COUNT = 5
"""Documented number of audio entries inside every project folder."""


class DiscoveryError(RuntimeError):
    """A directory scan failed (missing or unreadable directory)."""


def scan_projects(directory: Path | None) -> list[Project]:
    """List the project folders inside *directory*.

    A folder qualifies as a project when it contains at least one audio
    file. Folders whose audio count differs from
    :data:`EXPECTED_ENTRY_COUNT` are still returned, but flagged with an
    anomaly message for the views to display.
    """
    if directory is None:
        return []
    directory = Path(directory)
    if not directory.exists():
        raise DiscoveryError(f"Directory does not exist: {directory}")
    if not directory.is_dir():
        raise DiscoveryError(f"Not a directory: {directory}")
    try:
        children = list(directory.iterdir())
    except OSError as error:
        raise DiscoveryError(f"Cannot read directory {directory}: {error}") from error
    projects: list[Project] = []
    for folder in sorted(children, key=lambda path: path.name.lower()):
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        entries = _audio_entries(folder)
        if not entries:
            logger.debug("Skipping folder without audio files: %s", folder)
            continue
        anomaly = None
        if len(entries) != EXPECTED_ENTRY_COUNT:
            anomaly = f"{len(entries)}/{EXPECTED_ENTRY_COUNT} audio files"
        projects.append(
            Project(
                key=folder.name,
                name=folder.name,
                folder=folder,
                entries=entries,
                anomaly=anomaly,
            )
        )
    return projects


def _audio_entries(folder: Path) -> list[Entry]:
    entries: list[Entry] = []
    for item in sorted(folder.iterdir(), key=lambda path: path.name.lower()):
        if item.name.startswith(".") or not is_audio_file(item):
            continue
        entries.append(
            Entry(
                key=f"{folder.name}/{item.name}",
                label=item.stem,
                path=item,
            )
        )
    return entries
