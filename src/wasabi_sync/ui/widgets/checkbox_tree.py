"""A two-level checkbox tree with tri-state parents.

Views hand in :class:`TreeRow` records; the tree owns the check state,
renders ``☑``/``☐``/``☒`` glyphs, cascades parent toggles down to the
children, recomputes tri-state parents from their children, and
publishes :class:`CheckboxTree.Changed` after every mutation.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from rich.text import Text
from textual.binding import Binding, BindingType
from textual.message import Message
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

GLYPH_UNCHECKED = "☐"
GLYPH_CHECKED = "☑"
GLYPH_MIXED = "☒"


@dataclass
class TreeRow:
    """One node of the tree, as provided by a view."""

    key: str
    label: str
    checked: bool = False
    children: list[TreeRow] = field(default_factory=list)
    suffix: Text | None = None


class CheckboxTree(Tree[TreeRow]):
    """A tree whose rows toggle checkboxes when clicked.

    Clicking a row toggles its checkbox (checking a parent ticks every
    child); clicking the arrow toggles expansion only; ``enter``
    expands/collapses; ``space`` toggles the checkbox under the cursor;
    ``a`` checks all rows or clears the tree.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter", "toggle_node", "Expand/collapse"),
        Binding("space", "select_cursor", "Check/uncheck"),
        Binding("a", "toggle_all", "All/none"),
    ]

    class Changed(Message):
        """Posted whenever any checkbox state changes."""

        def __init__(self, tree: CheckboxTree) -> None:
            super().__init__()
            self.tree = tree
            self.checked_count = len(tree.checked_keys)

        @property
        def control(self) -> CheckboxTree:
            return self.tree

    def __init__(
        self,
        *,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__("", id=id, classes=classes)
        self.show_root = False
        self.auto_expand = False
        self.checked_keys: set[str] = set()
        self._rows: list[TreeRow] = []

    @property
    def rows(self) -> tuple[TreeRow, ...]:
        """The rows currently populating the tree."""
        return tuple(self._rows)

    def populate(self, rows: Sequence[TreeRow]) -> None:
        """Replace the tree contents with *rows*.

        Initial check state comes from each row's ``checked`` hint; use
        :meth:`set_checked` afterwards to restore a working set.
        """
        self._rows = list(rows)
        self.checked_keys = set()
        self.clear()
        for row in self._rows:
            parent = self.root.add(self._label(row, parent=True), data=row)
            for child in row.children:
                parent.add_leaf(self._label(child), data=child)
        self.root.expand()
        self._set_leaf_checked({row.key for row in _iter_rows(self._rows) if row.checked})
        self._refresh_states()
        self._notify_changed()

    def set_checked(self, keys: Iterable[str]) -> None:
        """Apply *keys* as the checked set (unknown keys are ignored)."""
        self._set_leaf_checked(set(keys))
        self._refresh_states()
        self._notify_changed()

    def set_all_expanded(self, expanded: bool) -> None:
        """Expand or collapse every parent row (the root stays expanded)."""
        for node in self._walk(self.root):
            if node.children and node is not self.root:
                node.expand() if expanded else node.collapse()

    def toggle(self, node: TreeNode[TreeRow]) -> None:
        """Flip the checkbox of *node*, cascading to its subtree."""
        row = node.data
        if row is None:
            return
        if node.children:
            target = not self._all_children_checked(node)
            for leaf in self._leaf_nodes(node):
                self._set_key(leaf, target)
            if target:
                node.expand()
        else:
            self._set_key(node, row.key not in self.checked_keys)
        self._refresh_states()
        self._notify_changed()

    def action_toggle_all(self) -> None:
        """Check every row, or clear the tree when all rows are checked."""
        leaf_keys = [leaf.data.key for leaf in self._leaf_nodes(self.root) if leaf.data is not None]
        if not leaf_keys:
            return
        if any(key not in self.checked_keys for key in leaf_keys):
            self.checked_keys.update(leaf_keys)
        else:
            self.checked_keys.difference_update(leaf_keys)
        self._refresh_states()
        self._notify_changed()

    def on_tree_node_selected(self, event: Tree.NodeSelected[TreeRow]) -> None:
        """Toggle the checkbox of the row that was clicked or space-selected."""
        event.stop()
        self.toggle(event.node)

    def _set_leaf_checked(self, keys: set[str]) -> None:
        self.checked_keys = set()
        for node in self._walk(self.root):
            if node.children or node.data is None:
                continue
            if node.data.key in keys:
                self.checked_keys.add(node.data.key)

    def _refresh_states(self) -> None:
        for node in self._walk(self.root):
            row = node.data
            if row is None:
                continue
            if node.children:
                if self._all_children_checked(node):
                    self.checked_keys.add(row.key)
                else:
                    self.checked_keys.discard(row.key)
            self._relabel(node)

    def _relabel(self, node: TreeNode[TreeRow]) -> None:
        row = node.data
        assert row is not None
        checked = row.key in self.checked_keys
        mixed = (
            bool(node.children)
            and not checked
            and any(
                child.data is not None and child.data.key in self.checked_keys
                for child in node.children
            )
        )
        glyph = GLYPH_MIXED if mixed else (GLYPH_CHECKED if checked else GLYPH_UNCHECKED)
        label = Text.assemble(
            (f"{glyph} ", ""),
            (row.label, "bold" if node.children else ""),
        )
        if row.suffix is not None:
            label.append("  ")
            label.append(row.suffix)
        node.set_label(label)

    def _label(self, row: TreeRow, *, parent: bool = False) -> Text:
        glyph = GLYPH_CHECKED if row.checked else GLYPH_UNCHECKED
        label = Text.assemble(
            (f"{glyph} ", ""),
            (row.label, "bold" if parent else ""),
        )
        if row.suffix is not None:
            label.append("  ")
            label.append(row.suffix)
        return label

    def _set_key(self, node: TreeNode[TreeRow], checked: bool) -> None:
        row = node.data
        if row is None:
            return
        if checked:
            self.checked_keys.add(row.key)
        else:
            self.checked_keys.discard(row.key)

    def _all_children_checked(self, node: TreeNode[TreeRow]) -> bool:
        return all(
            child.data is not None and child.data.key in self.checked_keys
            for child in node.children
        )

    def _leaf_nodes(self, node: TreeNode[TreeRow]) -> Iterator[TreeNode[TreeRow]]:
        for candidate in self._walk(node):
            if not candidate.children:
                yield candidate

    def _walk(self, node: TreeNode[TreeRow]) -> Iterator[TreeNode[TreeRow]]:
        """Yield *node* and all descendants, children before parents."""
        for child in node.children:
            yield from self._walk(child)
        yield node

    def _notify_changed(self) -> None:
        if self.is_running:
            self.post_message(self.Changed(self))


def _iter_rows(rows: Sequence[TreeRow]) -> Iterator[TreeRow]:
    for row in rows:
        yield row
        yield from _iter_rows(row.children)
