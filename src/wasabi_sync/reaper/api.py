"""Facade for driving REAPER — the implementation arrives with step 2.

Per the project constraints, REAPER is scripted through its Lua API only
(no ReaScript-Python); the reference documentation is ``REAPER API
docs.html`` at the repository root. Until the step-2 specification
lands, every entry point here raises :class:`NotImplementedError` so
accidental use fails loudly.
"""

from __future__ import annotations

from wasabi_sync.models import Selection
from wasabi_sync.settings import Settings


class ReaperApiError(RuntimeError):
    """Raised when driving REAPER fails."""


def run_export(selection: Selection, settings: Settings) -> None:
    """Execute the export pipeline inside REAPER (step 2 — TBD)."""
    raise NotImplementedError("Export pipeline awaits the step-2 specification")


def run_live_generation(selection: Selection, settings: Settings) -> None:
    """Generate the LIVE project inside REAPER (step 2 — TBD)."""
    raise NotImplementedError("LIVE pipeline awaits the step-2 specification")
