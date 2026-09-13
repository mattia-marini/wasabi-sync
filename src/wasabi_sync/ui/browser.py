"""A modal directory picker built on :class:`~textual.widgets.DirectoryTree`."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import BindingType
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Input, Label


class FoldersOnlyTree(DirectoryTree):
    """A :class:`DirectoryTree` that hides everything except folders."""

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.is_dir()]


class BrowserScreen(ModalScreen[Path | None]):
    """Pick a directory; dismisses with the chosen path or ``None``."""

    BINDINGS: ClassVar[list[BindingType]] = [("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    BrowserScreen {
        align: center middle;
    }
    BrowserScreen #browser-dialog {
        width: 70%;
        height: 70%;
        border: round $primary;
        background: $surface;
        padding: 1;
    }
    BrowserScreen #browser-input {
        margin-bottom: 1;
    }
    BrowserScreen FoldersOnlyTree {
        height: 1fr;
    }
    BrowserScreen .browser-buttons {
        height: 3;
        align-horizontal: right;
    }
    BrowserScreen .browser-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, start: Path | None = None, *, title: str = "Choose directory") -> None:
        super().__init__()
        self._start = Path(start) if start is not None else Path.home()
        self._title = title

    def compose(self) -> ComposeResult:
        with Vertical(id="browser-dialog"):
            yield Label(self._title)
            yield Input(str(self._start), id="browser-input")
            yield FoldersOnlyTree(str(self._start), id="browser-tree")
            with Horizontal(classes="browser-buttons"):
                yield Button("Up", id="browser-up")
                yield Button("Choose this folder", id="browser-choose", variant="primary")
                yield Button("Cancel", id="browser-cancel")

    @on(Input.Submitted, "#browser-input")
    def _retarget(self, event: Input.Submitted) -> None:
        target = Path(event.value).expanduser()
        if target.is_dir():
            tree = self.query_one("#browser-tree", FoldersOnlyTree)
            tree.path = target
            event.input.value = str(target)
        else:
            self.app.notify(f"Not a directory: {target}", severity="warning")

    @on(Button.Pressed, "#browser-up")
    def _go_up(self) -> None:
        tree = self.query_one("#browser-tree", FoldersOnlyTree)
        current = Path(tree.path)
        if current.parent != current:
            tree.path = current.parent

    @on(Button.Pressed, "#browser-choose")
    def _choose(self) -> None:
        self.dismiss(Path(self.query_one("#browser-tree", FoldersOnlyTree).path))

    @on(Button.Pressed, "#browser-cancel")
    def _cancel(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
