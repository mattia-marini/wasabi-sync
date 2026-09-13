"""Shared behaviour for the Export projects and Generate LIVE tabs."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, cast

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Static

from wasabi_sync.core.actions import Action, ActionReport
from wasabi_sync.core.discovery import DiscoveryError
from wasabi_sync.models import Project, Selection, build_selection, selection_counts
from wasabi_sync.settings import Settings
from wasabi_sync.ui.widgets.checkbox_tree import CheckboxTree, TreeRow

if TYPE_CHECKING:
    from wasabi_sync.app import WasabiSyncApp

logger = logging.getLogger(__name__)


class ProjectView(Vertical):
    """Toolbar + checkbox tree + status row + submit button.

    Subclasses provide the source directory, the scan/validation
    behaviour, the row presentation, and the submit action.
    """

    DEFAULT_CSS = """
    ProjectView {
        height: 1fr;
    }
    ProjectView .toolbar {
        height: 3;
        align-horizontal: left;
    }
    ProjectView .toolbar Button {
        margin: 0 1 0 0;
    }
    ProjectView CheckboxTree {
        height: 1fr;
        border: round $primary;
    }
    ProjectView .status-row {
        height: 3;
    }
    ProjectView .status-row Static {
        width: 1fr;
        content-align: left middle;
    }
    """

    def __init__(self, prefix: str, submit_label: str) -> None:
        super().__init__()
        self._prefix = prefix
        self._submit_label = submit_label
        self._projects: list[Project] = []
        self._expanded = False
        self._notice: str | None = None

    def compose(self) -> ComposeResult:
        with Horizontal(classes="toolbar"):
            yield Button("Refresh", id=f"{self._prefix}-refresh")
            yield Button("Select all", id=f"{self._prefix}-all")
            yield Button("Expand", id=f"{self._prefix}-expand")
        yield CheckboxTree(id=f"{self._prefix}-tree")
        with Horizontal(classes="status-row"):
            yield Static("", id=f"{self._prefix}-status")
            yield Button(
                self._submit_label,
                id=f"{self._prefix}-submit",
                variant="success",
                disabled=True,
            )

    def source_dir(self, settings: Settings) -> Path | None:
        raise NotImplementedError

    def fetch_projects(self, settings: Settings) -> list[Project]:
        raise NotImplementedError

    def build_rows(self, projects: Sequence[Project]) -> list[TreeRow]:
        raise NotImplementedError

    def make_action(self) -> Action:
        raise NotImplementedError

    @property
    def project_tree(self) -> CheckboxTree:
        return self.query_one(f"#{self._prefix}-tree", CheckboxTree)

    @property
    def app_settings(self) -> Settings:
        return cast("WasabiSyncApp", self.app).settings

    def on_mount(self) -> None:
        self.refresh_projects()

    def refresh_projects(self) -> None:
        """Rescan the source directory and rebuild the tree."""
        previous = set(self.project_tree.checked_keys)
        settings = self.app_settings
        if self.source_dir(settings) is None:
            self._projects = []
            self._notice = "Source directory not set — press ctrl+s to open settings."
            self.project_tree.populate([])
            self._sync_controls()
            return
        try:
            projects = self.fetch_projects(settings)
        except DiscoveryError as error:
            self._projects = []
            self._notice = str(error)
            self.project_tree.populate([])
            self._sync_controls()
            self.app.notify(str(error), title="Scan failed", severity="error")
            return
        self._projects = projects
        self._notice = None
        self.project_tree.populate(self.build_rows(projects))
        self.project_tree.set_checked(previous)
        self._sync_controls()

    def current_selection(self) -> Selection:
        """The selection implied by the tree's current checkbox state."""
        return build_selection(self._projects, self.project_tree.checked_keys)

    def _set_status(self, text: str) -> None:
        self.query_one(f"#{self._prefix}-status", Static).update(text)

    def _sync_controls(self) -> None:
        projects, entries = selection_counts(self.current_selection())
        self.query_one(f"#{self._prefix}-submit", Button).disabled = projects == 0
        if self._notice is not None:
            self._set_status(self._notice)
            return
        self._set_status(
            f"{len(self._projects)} project(s) · {projects} selected · {entries} entr(ies)"
        )

    @on(CheckboxTree.Changed)
    def _on_tree_changed(self, event: CheckboxTree.Changed) -> None:
        self._sync_controls()

    @on(Button.Pressed)
    def _on_button(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id == f"{self._prefix}-refresh":
            self.refresh_projects()
        elif button_id == f"{self._prefix}-all":
            self.project_tree.action_toggle_all()
        elif button_id == f"{self._prefix}-expand":
            self._expanded = not self._expanded
            self.project_tree.set_all_expanded(self._expanded)
            event.button.label = "Collapse" if self._expanded else "Expand"
        elif button_id == f"{self._prefix}-submit":
            self._submit()

    def _submit(self) -> None:
        selection = self.current_selection()
        if not selection:
            self.app.notify("Nothing selected.", severity="warning")
            return
        self._run_action(self.make_action(), selection, self.app_settings)

    @work(thread=True, exclusive=True, group="submit")
    def _run_action(self, action: Action, selection: Selection, settings: Settings) -> None:
        try:
            report = action.run(selection, settings)
        except Exception:
            logger.exception("Submit action failed")
            report = ActionReport(
                ok=False,
                message="Action failed — see the log for details.",
            )
        self.app.call_from_thread(self._show_report, report)

    def _show_report(self, report: ActionReport) -> None:
        message = report.message
        if report.details:
            message = "\n".join((message, *report.details))
        self.app.notify(
            message,
            severity="information" if report.ok else "error",
            timeout=10,
        )
        self._set_status(report.message)
