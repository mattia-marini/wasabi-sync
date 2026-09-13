"""Unmute the master-sending tracks of the selected REAPER projects."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from wasabi_sync.core.actions.base import ActionReport
from wasabi_sync.models import Project, Selection
from wasabi_sync.reaper.rpp import unmute_master_tracks
from wasabi_sync.settings import Settings

logger = logging.getLogger(__name__)


class ExportAction:
    """Ensure every master-sending track is unmuted, editing the .rpp in place.

    Only tracks that send audio directly to the master are considered
    (mirroring the Export tab). Any that are muted are unmuted and the
    project file is rewritten. The unmute applies to *all* master-sending
    tracks of each selected project — the per-track checkboxes select the
    projects to process and will scope the next step's export.
    """

    def run(
        self,
        projects: Sequence[Project],
        selection: Selection,
        settings: Settings,
    ) -> ActionReport:
        selected = [project for project in projects if project.key in selection]
        total_unmuted = 0
        details: list[str] = []
        errors: list[str] = []
        for project in selected:
            if project.rpp_path is None:
                errors.append(f"{project.name}: no .rpp file")
                continue
            try:
                text = project.rpp_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as error:
                logger.warning("Cannot read %s: %s", project.rpp_path, error)
                errors.append(f"{project.name}: cannot read project file")
                continue
            new_text, unmuted = unmute_master_tracks(text)
            if not unmuted:
                details.append(f"{project.name}: no muted master tracks")
                continue
            try:
                project.rpp_path.write_text(new_text, encoding="utf-8")
            except OSError as error:
                logger.warning("Cannot write %s: %s", project.rpp_path, error)
                errors.append(f"{project.name}: cannot write project file")
                continue
            total_unmuted += len(unmuted)
            details.append(f"{project.name}: unmuted {', '.join(unmuted)}")
        if errors:
            return ActionReport(
                ok=False,
                message=(f"Unmuted {total_unmuted} track(s); {len(errors)} project(s) failed."),
                details=tuple([*details, *errors]),
            )
        return ActionReport(
            ok=True,
            message=f"Unmuted {total_unmuted} track(s) across {len(selected)} project(s).",
            details=tuple(details),
        )
