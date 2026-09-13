"""Validation framework for exported projects (LIVE tab).

The framework is final; the concrete rules arrive with the step-2
specification. Rules inspect a :class:`~wasabi_sync.models.Project` and
return :class:`Finding` records, which the LIVE view renders as
per-entry and per-project markers.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from wasabi_sync.core.discovery import EXPECTED_ENTRY_COUNT
from wasabi_sync.models import EntryStatus, Project

_SEVERITY = {
    EntryStatus.UNKNOWN: 0,
    EntryStatus.OK: 1,
    EntryStatus.WARNING: 2,
    EntryStatus.ERROR: 3,
}


@dataclass(frozen=True)
class Finding:
    """A single validation result.

    ``entry_key`` is ``None`` for project-level findings, otherwise the
    key of the entry the finding applies to.
    """

    entry_key: str | None
    status: EntryStatus
    detail: str


@runtime_checkable
class ValidationRule(Protocol):
    """A named check applied to every scanned project."""

    name: str

    def check(self, project: Project) -> list[Finding]: ...


class EntryCountRule:
    """Built-in structural check: each project must carry 5 audio files."""

    name = "entry-count"

    def check(self, project: Project) -> list[Finding]:
        count = len(project.entries)
        if count == EXPECTED_ENTRY_COUNT:
            return [
                Finding(
                    entry_key=None,
                    status=EntryStatus.OK,
                    detail=f"{count} audio files",
                )
            ]
        return [
            Finding(
                entry_key=None,
                status=EntryStatus.WARNING,
                detail=f"{count}/{EXPECTED_ENTRY_COUNT} audio files",
            )
        ]


def default_rules() -> list[ValidationRule]:
    """The rules applied by the LIVE tab until the step-2 registry lands."""
    return [EntryCountRule()]


def run_validations(projects: Sequence[Project], rules: Sequence[ValidationRule]) -> None:
    """Apply *rules* to every project, writing results onto the models."""
    for project in projects:
        findings: list[Finding] = []
        for rule in rules:
            findings.extend(rule.check(project))
        apply_findings(project, findings)


def apply_findings(project: Project, findings: Sequence[Finding]) -> None:
    """Store *findings* on the project and its entries."""
    project.status = EntryStatus.UNKNOWN
    project.detail = None
    for entry in project.entries:
        entry.status = EntryStatus.UNKNOWN
        entry.detail = None
    project_findings = [finding for finding in findings if finding.entry_key is None]
    if project_findings:
        project.status = max(
            (finding.status for finding in project_findings),
            key=lambda status: _SEVERITY[status],
        )
        project.detail = "; ".join(finding.detail for finding in project_findings if finding.detail)
    for finding in findings:
        if finding.entry_key is None:
            continue
        for entry in project.entries:
            if entry.key == finding.entry_key:
                entry.status = finding.status
                entry.detail = finding.detail
