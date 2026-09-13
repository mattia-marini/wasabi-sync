"""Modal settings editor for the two source directories and REAPER path."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, cast

from textual import on
from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from wasabi_sync.settings import Settings
from wasabi_sync.ui.browser import BrowserScreen

if TYPE_CHECKING:
    from wasabi_sync.app import WasabiSyncApp


class SettingsScreen(ModalScreen[None]):
    """Edit the settings; saves through the app and dismisses."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save"),
    ]

    DEFAULT_CSS = """
    SettingsScreen {
        align: center middle;
    }
    SettingsScreen #settings-dialog {
        width: 80%;
        height: auto;
        max-height: 80%;
        border: solid $primary;
        background: $ansi-background;
        padding: 1 2;
    }
    SettingsScreen Label {
        width: 1fr;
        margin-bottom: 0;
    }
    SettingsScreen .field {
        height: 3;
        margin-bottom: 1;
    }
    SettingsScreen .field Input {
        width: 1fr;
    }
    SettingsScreen .settings-buttons {
        height: 3;
        align-horizontal: right;
        margin-top: 1;
    }
    SettingsScreen .settings-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def compose(self) -> ComposeResult:
        with Vertical(id="settings-dialog"):
            yield Label("Projects directory (Export tab)")
            with Horizontal(classes="field"):
                yield Input(_as_text(self._settings.projects_dir), id="projects-input")
                yield Button("Browse", id="projects-browse")
            yield Label("Exports directory (LIVE tab)")
            with Horizontal(classes="field"):
                yield Input(_as_text(self._settings.exports_dir), id="exports-input")
                yield Button("Browse", id="exports-browse")
            yield Label("REAPER executable (optional, used from step 2)")
            with Horizontal(classes="field"):
                yield Input(_as_text(self._settings.reaper_path), id="reaper-input")
            with Horizontal(classes="settings-buttons"):
                yield Button("Cancel", id="settings-cancel")
                yield Button("Save", id="settings-save", variant="primary")

    @on(Button.Pressed, "#projects-browse")
    async def _browse_projects(self) -> None:
        await self._browse("#projects-input")

    @on(Button.Pressed, "#exports-browse")
    async def _browse_exports(self) -> None:
        await self._browse("#exports-input")

    @on(Button.Pressed, "#settings-save")
    def _save_button(self) -> None:
        self.save()

    @on(Button.Pressed, "#settings-cancel")
    def _cancel_button(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_save(self) -> None:
        self.save()

    def save(self) -> None:
        """Validate the inputs, persist them through the app, dismiss."""
        try:
            new_settings = Settings(
                projects_dir=_dir_from_input(
                    self.query_one("#projects-input", Input).value,
                    "Projects directory",
                ),
                exports_dir=_dir_from_input(
                    self.query_one("#exports-input", Input).value,
                    "Exports directory",
                ),
                reaper_path=_file_from_input(
                    self.query_one("#reaper-input", Input).value,
                    "REAPER executable",
                ),
            )
        except ValueError as error:
            self.app.notify(str(error), title="Invalid settings", severity="error")
            return
        self.dismiss(None)
        cast("WasabiSyncApp", self.app).save_settings(new_settings)

    async def _browse(self, input_id: str) -> None:
        current = self.query_one(input_id, Input).value.strip()
        start = Path(current) if current and Path(current).is_dir() else None
        await self.app.push_screen(
            BrowserScreen(start),
            callback=lambda path: self._apply_browse(input_id, path),
        )

    def _apply_browse(self, input_id: str, path: Path | None) -> None:
        if path is not None:
            self.query_one(input_id, Input).value = str(path)


def _as_text(path: Path | None) -> str:
    return str(path) if path is not None else ""


def _dir_from_input(value: str, label: str) -> Path | None:
    value = value.strip()
    if not value:
        return None
    path = Path(value).expanduser()
    if not path.is_dir():
        raise ValueError(f"{label}: not a directory: {path}")
    return path


def _file_from_input(value: str, label: str) -> Path | None:
    value = value.strip()
    if not value:
        return None
    path = Path(value).expanduser()
    if not path.is_file():
        raise ValueError(f"{label}: not a file: {path}")
    return path
