"""The Textual application object."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from textual.app import App
from textual.binding import BindingType

from wasabi_sync.settings import Settings, SettingsStore
from wasabi_sync.ui.main_screen import MainScreen
from wasabi_sync.ui.settings_screen import SettingsScreen


class WasabiSyncApp(App):
    """wasabi-sync — synchronise multiple REAPER projects."""

    TITLE = "wasabi-sync"

    BINDINGS: ClassVar[list[BindingType]] = [
        ("ctrl+s", "settings", "Settings"),
    ]

    def __init__(self, settings_path: Path | None = None) -> None:
        super().__init__()
        self.store = SettingsStore(settings_path)
        self.settings = self.store.load()

    def get_default_screen(self) -> MainScreen:
        return MainScreen()

    async def action_settings(self) -> None:
        await self.push_screen(SettingsScreen(self.settings))

    def save_settings(self, settings: Settings) -> None:
        """Persist and apply new settings, then refresh the tabs."""
        self.store.save(settings)
        self.settings = settings
        self.notify("Settings saved.")
        for screen in self.screen_stack:
            if isinstance(screen, MainScreen):
                screen.refresh_views()
