"""The Textual application object."""

from __future__ import annotations

import os
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

    CSS = """
    /* Flat, modern look using the terminal's own palette (ansi theme). */

    /* Buttons: flat, no bevel or border. */
    Button {
        border: none;
        background: transparent;
        padding: 0 2;
        height: 1;
        text-style: none;
    }
    Button:hover {
        background: $ansi-background;
        text-style: bold;
    }
    Button:focus {
        text-style: bold;
    }
    Button:disabled {
        color: $foreground 40%;
        background: transparent;
        text-style: none;
    }
    Button.-primary {
        color: $primary;
        text-style: bold;
    }
    Button.-primary:hover {
        background: $primary;
        color: $ansi-background;
    }
    Button.-success {
        color: $success;
    }
    Button.-success:hover {
        background: $success;
        color: $ansi-background;
    }

    /* Tabs: flat, single row, no sliding underline animation. */
    TabbedContent {
        height: 1fr;
    }
    TabbedContent > ContentTabs {
        height: 1;
    }
    Underline {
        display: none;
    }
    Tab.-active {
        text-style: bold;
    }
    """

    def __init__(self, settings_path: Path | None = None) -> None:
        super().__init__()
        self.theme = os.environ.get("TEXTUAL_THEME", "ansi-dark")
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
