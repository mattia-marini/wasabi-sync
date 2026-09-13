"""Headless integration tests driven through Textual's pilot."""

from __future__ import annotations

from pathlib import Path

from textual.widgets import Button, Input, Static, TabbedContent

from wasabi_sync.app import WasabiSyncApp
from wasabi_sync.settings import Settings
from wasabi_sync.ui.browser import BrowserScreen
from wasabi_sync.ui.export_view import ExportView
from wasabi_sync.ui.live_view import LiveView
from wasabi_sync.ui.main_screen import MainScreen
from wasabi_sync.ui.settings_screen import SettingsScreen


def make_app(settings: Settings, tmp_path: Path) -> WasabiSyncApp:
    app = WasabiSyncApp(settings_path=tmp_path / "settings.json")
    app.settings = settings
    return app


async def test_app_boots_and_switches_tabs(library, tmp_path):
    app = make_app(Settings(), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        tabbed = app.query_one(TabbedContent)
        assert tabbed.active_pane is not None
        assert tabbed.active_pane.id == "tab-export"
        await pilot.press("f2")
        await pilot.pause()
        assert tabbed.active_pane.id == "tab-live"
        await pilot.press("f1")
        await pilot.pause()
        assert tabbed.active_pane.id == "tab-export"


async def test_export_view_populates_from_settings(library, tmp_path):
    app = make_app(Settings(projects_dir=library), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        view = app.query_one(ExportView)
        tree = view.project_tree
        assert len(tree.root.children) == 3
        alpha = tree.root.children[0]
        assert alpha.data is not None and alpha.data.key == "alpha"
        assert len(alpha.children) == 5
        assert view.current_selection() == {}
        assert app.query_one("#export-submit").disabled is True
        status = app.query_one("#export-status", Static)
        assert "3 project(s)" in str(status.content)


async def test_unconfigured_view_shows_hint(tmp_path):
    app = make_app(Settings(), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        status = app.query_one("#export-status", Static)
        assert "Source directory not set" in str(status.content)
        assert len(app.query_one(ExportView).project_tree.root.children) == 0


async def test_checking_parent_ticks_children(library, tmp_path):
    app = make_app(Settings(projects_dir=library), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        view = app.query_one(ExportView)
        tree = view.project_tree
        alpha = tree.root.children[0]
        tree.toggle(alpha)
        await pilot.pause()
        assert alpha.is_expanded is True
        selection = view.current_selection()
        assert set(selection) == {"alpha"}
        assert len(selection["alpha"]) == 5
        assert "alpha" in tree.checked_keys
        assert app.query_one("#export-submit").disabled is False


async def test_unchecking_child_flips_parent_to_mixed(library, tmp_path):
    app = make_app(Settings(projects_dir=library), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        view = app.query_one(ExportView)
        tree = view.project_tree
        alpha = tree.root.children[0]
        tree.toggle(alpha)
        await pilot.pause()
        tree.toggle(alpha.children[0])
        await pilot.pause()
        assert "alpha" not in tree.checked_keys
        selection = view.current_selection()
        assert len(selection["alpha"]) == 4
        assert alpha._label.plain.startswith("☒")


async def test_toggle_all_round_trip(library, tmp_path):
    app = make_app(Settings(projects_dir=library), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        view = app.query_one(ExportView)
        tree = view.project_tree
        tree.focus()
        await pilot.press("a")
        await pilot.pause()
        projects, entries = (
            len(view.current_selection()),
            sum(len(keys) for keys in view.current_selection().values()),
        )
        assert (projects, entries) == (3, 13)
        await pilot.press("a")
        await pilot.pause()
        assert view.current_selection() == {}


async def test_space_toggles_cursor_row(library, tmp_path):
    app = make_app(Settings(projects_dir=library), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        view = app.query_one(ExportView)
        tree = view.project_tree
        tree.focus()
        await pilot.press("down")
        await pilot.press("space")
        await pilot.pause()
        selection = view.current_selection()
        assert set(selection) == {"alpha"}
        assert len(selection["alpha"]) == 5


async def test_refresh_preserves_checked_state(library, tmp_path):
    app = make_app(Settings(projects_dir=library), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        view = app.query_one(ExportView)
        tree = view.project_tree
        tree.toggle(tree.root.children[1])
        await pilot.pause()
        await pilot.click("#export-refresh")
        await pilot.pause()
        selection = view.current_selection()
        assert set(selection) == {"bravo"}
        assert len(selection["bravo"]) == 5


async def test_live_view_shows_validation(library, tmp_path):
    app = make_app(Settings(exports_dir=library), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        tree = app.query_one(LiveView).project_tree
        rows = tree.rows
        assert rows[0].suffix is not None
        assert "5 audio files" in rows[0].suffix.plain
        assert rows[2].suffix is not None
        assert "3/5 audio files" in rows[2].suffix.plain


async def test_submit_reports_stub(library, tmp_path):
    app = make_app(Settings(projects_dir=library), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        app.query_one(ExportView).project_tree.focus()
        await pilot.press("a")
        await pilot.pause()
        await pilot.click("#export-submit")
        await pilot.pause()
        notifications = list(app._notifications._notifications.values())
        assert notifications
        assert "stub" in notifications[-1].message
        status = app.query_one("#export-status", Static)
        assert "[stub]" in str(status.content)


async def test_settings_flow_saves_and_refreshes(library, tmp_path):
    app = make_app(Settings(), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("ctrl+s")
        await pilot.pause()
        assert isinstance(app.screen, SettingsScreen)
        screen = app.screen
        screen.query_one("#projects-input", Input).value = str(library)
        screen.query_one("#exports-input", Input).value = str(library)
        screen.query_one("#settings-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, MainScreen)
        assert app.settings.projects_dir == library
        assert app.settings.exports_dir == library
        assert app.store.load().projects_dir == library
        assert len(app.query_one(ExportView).project_tree.root.children) == 3
        assert len(app.query_one(LiveView).project_tree.root.children) == 3


async def test_settings_invalid_path_is_rejected(library, tmp_path):
    app = make_app(Settings(), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("ctrl+s")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, SettingsScreen)
        screen.query_one("#projects-input", Input).value = str(tmp_path / "nope")
        screen.query_one("#settings-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, SettingsScreen)
        assert app.settings.projects_dir is None


async def test_settings_browse_opens_directory_browser(library, tmp_path):
    app = make_app(Settings(), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("ctrl+s")
        await pilot.pause()
        settings_screen = app.screen
        assert isinstance(settings_screen, SettingsScreen)
        settings_screen.query_one("#projects-input", Input).value = str(library)
        settings_screen.query_one("#projects-browse", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, BrowserScreen)
        app.screen.query_one("#browser-choose", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, SettingsScreen)
        assert settings_screen.query_one("#projects-input", Input).value == str(library)


async def test_settings_escape_cancels(library, tmp_path):
    app = make_app(Settings(projects_dir=library), tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("ctrl+s")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, MainScreen)
        assert app.settings.projects_dir == library


async def test_browser_screen_returns_chosen_directory(library, tmp_path):
    app = make_app(Settings(), tmp_path)
    results: list[Path | None] = []
    async with app.run_test() as pilot:
        await app.push_screen(BrowserScreen(library), callback=results.append)
        await pilot.pause()
        app.screen.query_one("#browser-choose", Button).press()
        await pilot.pause()
    assert results == [Path(library)]
