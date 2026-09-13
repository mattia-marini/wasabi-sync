"""wasabi-sync — a Textual TUI wrapper for REAPER project synchronisation."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from importlib import metadata

from wasabi_sync.logging_setup import configure_logging

__version__ = "0.1.0"

_APP_DESCRIPTION = "Synchronise multiple REAPER projects from the terminal."


def get_version() -> str:
    """Return the installed version when available, else the source one."""
    try:
        return metadata.version("wasabi-sync")
    except metadata.PackageNotFoundError:
        return __version__


def main(argv: Sequence[str] | None = None) -> None:
    """Parse arguments and run the TUI."""
    parser = argparse.ArgumentParser(
        prog="wasabi-sync",
        description=_APP_DESCRIPTION,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
    )
    parser.parse_args(argv)
    configure_logging()
    from wasabi_sync.app import WasabiSyncApp

    WasabiSyncApp().run()
