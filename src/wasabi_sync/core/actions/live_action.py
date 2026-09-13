"""Placeholder LIVE generation pipeline — replaced by the step-2 specification."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from wasabi_sync.core.actions.base import ActionReport
from wasabi_sync.models import Project, Selection, selection_counts
from wasabi_sync.settings import Settings

logger = logging.getLogger(__name__)


class LiveAction:
    """Stub invoked by the LIVE tab's submit button."""

    def run(
        self,
        projects: Sequence[Project],
        selection: Selection,
        settings: Settings,
    ) -> ActionReport:
        projects_count, entries = selection_counts(selection)
        logger.info(
            "LIVE generation requested (stub): projects=%d entries=%d",
            projects_count,
            entries,
        )
        details = tuple(
            f"{name}: {len(keys)} entries" if keys else f"{name}: whole folder"
            for name, keys in sorted(selection.items())
        )
        return ActionReport(
            ok=True,
            message=(
                f"[stub] LIVE project would be generated from {projects_count} "
                f"project(s) / {entries} entr(ies). The real pipeline ships "
                "with step 2."
            ),
            details=details,
        )
