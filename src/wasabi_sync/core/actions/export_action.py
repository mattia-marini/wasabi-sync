"""Placeholder export pipeline — replaced by the step-2 specification."""

from __future__ import annotations

import logging

from wasabi_sync.core.actions.base import ActionReport
from wasabi_sync.models import Selection, selection_counts
from wasabi_sync.settings import Settings

logger = logging.getLogger(__name__)


class ExportAction:
    """Stub invoked by the Export tab's submit button."""

    def run(self, selection: Selection, settings: Settings) -> ActionReport:
        projects, entries = selection_counts(selection)
        logger.info("Export requested (stub): projects=%d entries=%d", projects, entries)
        details = tuple(
            f"{name}: {len(keys)} entries" if keys else f"{name}: whole folder"
            for name, keys in sorted(selection.items())
        )
        return ActionReport(
            ok=True,
            message=(
                f"[stub] Export would run for {projects} project(s) / "
                f"{entries} entr(ies). The real pipeline ships with step 2."
            ),
            details=details,
        )
