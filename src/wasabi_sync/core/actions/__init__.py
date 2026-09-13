"""Submit actions for the two tabs.

Actions run inside worker threads (never on the UI thread) and return an
:class:`ActionReport` that the view turns into a notification. The
concrete pipelines arrive with the step-2 specification; the stubs below
record the request and report what is still missing.
"""

from __future__ import annotations

from wasabi_sync.core.actions.base import Action, ActionReport
from wasabi_sync.core.actions.export_action import ExportAction
from wasabi_sync.core.actions.live_action import LiveAction

__all__ = ["Action", "ActionReport", "ExportAction", "LiveAction"]
