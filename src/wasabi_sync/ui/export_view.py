"""The Export projects tab."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from rich.text import Text

from wasabi_sync.core.actions import Action, ExportAction
from wasabi_sync.core.discovery import scan_projects
from wasabi_sync.models import Project
from wasabi_sync.settings import Settings
from wasabi_sync.ui.project_view import ProjectView
from wasabi_sync.ui.widgets.checkbox_tree import TreeRow

ANOMALY_STYLE = "yellow"


class ExportView(ProjectView):
    """Lists the projects stored in the configured projects directory."""

    def __init__(self) -> None:
        super().__init__(prefix="export", submit_label="Export selection")

    def source_dir(self, settings: Settings) -> Path | None:
        return settings.projects_dir

    def fetch_projects(self, settings: Settings) -> list[Project]:
        return scan_projects(settings.projects_dir)

    def build_rows(self, projects: Sequence[Project]) -> list[TreeRow]:
        return [
            TreeRow(
                key=project.key,
                label=project.name,
                children=[TreeRow(key=entry.key, label=entry.label) for entry in project.entries],
                suffix=_anomaly_suffix(project),
            )
            for project in projects
        ]

    def make_action(self) -> Action:
        return ExportAction()


def _anomaly_suffix(project: Project) -> Text | None:
    if project.anomaly is None:
        return None
    return Text(f"⚠ {project.anomaly}", style=ANOMALY_STYLE)
