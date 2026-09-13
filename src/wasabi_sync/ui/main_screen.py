"""The main screen hosting the two tabs."""

from __future__ import annotations

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import BindingType
from textual.screen import Screen
from textual.widgets import Footer, Header, TabbedContent, TabPane

from wasabi_sync.ui.export_view import ExportView
from wasabi_sync.ui.live_view import LiveView

TAB_EXPORT = "tab-export"
TAB_LIVE = "tab-live"


class MainScreen(Screen):
    """Export projects / Generate LIVE."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("f1", "show_export", "Export tab"),
        ("f2", "show_live", "LIVE tab"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with TabbedContent():
            with TabPane("Export projects", id=TAB_EXPORT):
                yield ExportView()
            with TabPane("Generate LIVE", id=TAB_LIVE):
                yield LiveView()
        yield Footer()

    def action_show_export(self) -> None:
        self.query_one(TabbedContent).active = TAB_EXPORT

    def action_show_live(self) -> None:
        self.query_one(TabbedContent).active = TAB_LIVE

    def refresh_views(self) -> None:
        """Rescan both tabs (called after settings change)."""
        self.query_one(ExportView).refresh_projects()
        self.query_one(LiveView).refresh_projects()
