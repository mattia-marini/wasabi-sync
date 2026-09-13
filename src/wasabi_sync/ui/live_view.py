"""The Generate LIVE tab."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from rich.text import Text

from wasabi_sync.core.actions import Action, LiveAction
from wasabi_sync.core.discovery import scan_projects
from wasabi_sync.core.validation import default_rules, run_validations
from wasabi_sync.models import EntryStatus, Project
from wasabi_sync.settings import Settings
from wasabi_sync.ui.project_view import ProjectView
from wasabi_sync.ui.widgets.checkbox_tree import TreeRow

STATUS_SUFFIXES: dict[EntryStatus, tuple[str, str]] = {
    EntryStatus.OK: ("✓", "green"),
    EntryStatus.WARNING: ("⚠", "yellow"),
    EntryStatus.ERROR: ("✗", "red"),
}


class LiveView(ProjectView):
    """Lists exported projects, validating them for LIVE generation."""

    def __init__(self) -> None:
        super().__init__(prefix="live", submit_label="Generate LIVE")

    def source_dir(self, settings: Settings) -> Path | None:
        return settings.exports_dir

    def fetch_projects(self, settings: Settings) -> list[Project]:
        projects = scan_projects(settings.exports_dir)
        run_validations(projects, default_rules())
        return projects

    def build_rows(self, projects: Sequence[Project]) -> list[TreeRow]:
        return [
            TreeRow(
                key=project.key,
                label=project.name,
                children=[
                    TreeRow(
                        key=entry.key,
                        label=entry.label,
                        suffix=_status_suffix(entry.status, entry.detail),
                    )
                    for entry in project.entries
                ],
                suffix=_status_suffix(project.status, project.detail),
            )
            for project in projects
        ]

    def make_action(self) -> Action:
        return LiveAction()


def _status_suffix(status: EntryStatus, detail: str | None) -> Text | None:
    if status is EntryStatus.UNKNOWN:
        return None
    glyph, style = STATUS_SUFFIXES[status]
    text = Text(glyph, style=style)
    if detail:
        text.append(f" {detail}", style=style)
    return text
