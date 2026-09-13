"""Action contracts: the report every action returns and the action protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from wasabi_sync.models import Selection
from wasabi_sync.settings import Settings


@dataclass(frozen=True)
class ActionReport:
    """Outcome of a submit action."""

    ok: bool
    message: str
    details: tuple[str, ...] = ()


class Action(Protocol):
    """Behaviour triggered by a tab's submit button."""

    def run(self, selection: Selection, settings: Settings) -> ActionReport: ...
