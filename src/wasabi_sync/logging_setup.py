"""File-based logging setup.

The TUI owns the terminal, so logs never go to the console; they are
written to a rotating file inside the user config directory.
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from platformdirs import user_config_dir

from wasabi_sync.settings import APP_NAME

LOG_FILENAME = "wasabi-sync.log"
MAX_BYTES = 1_000_000
BACKUP_COUNT = 3


def configure_logging() -> Path | None:
    """Route INFO+ logs to a rotating file; return its path or ``None``."""
    try:
        log_dir = Path(user_config_dir(APP_NAME))
        log_dir.mkdir(parents=True, exist_ok=True)
        handler: logging.Handler = logging.handlers.RotatingFileHandler(
            log_dir / LOG_FILENAME,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
    except OSError:
        return None
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    return log_dir / LOG_FILENAME
