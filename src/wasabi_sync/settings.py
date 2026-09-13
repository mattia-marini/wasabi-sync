"""Application settings, persisted as JSON in the user config directory."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_config_dir

logger = logging.getLogger(__name__)

APP_NAME = "wasabi-sync"
SETTINGS_FILENAME = "settings.json"


@dataclass
class Settings:
    """User-configurable directories used by the two tabs."""

    projects_dir: Path | None = None
    exports_dir: Path | None = None
    reaper_path: Path | None = None


class SettingsStore:
    """Load and save :class:`Settings` in a JSON file."""

    def __init__(self, path: Path | None = None) -> None:
        if path is not None:
            self.path = path
        else:
            self.path = Path(user_config_dir(APP_NAME)) / SETTINGS_FILENAME

    def load(self) -> Settings:
        """Return the stored settings, or defaults when unreadable."""
        if not self.path.is_file():
            return Settings()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except OSError, json.JSONDecodeError:
            logger.warning("Unreadable settings file %s; using defaults", self.path)
            return Settings()
        if not isinstance(data, dict):
            logger.warning("Malformed settings file %s; using defaults", self.path)
            return Settings()
        return Settings(
            projects_dir=_optional_path(data.get("projects_dir")),
            exports_dir=_optional_path(data.get("exports_dir")),
            reaper_path=_optional_path(data.get("reaper_path")),
        )

    def save(self, settings: Settings) -> None:
        """Persist *settings* atomically (write to a temp file, then rename)."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {
                "projects_dir": _optional_str(settings.projects_dir),
                "exports_dir": _optional_str(settings.exports_dir),
                "reaper_path": _optional_str(settings.reaper_path),
            },
            indent=2,
        )
        tmp_path = self.path.with_name(self.path.name + ".tmp")
        tmp_path.write_text(payload + "\n", encoding="utf-8")
        tmp_path.replace(self.path)


def _optional_path(value: object) -> Path | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        return None
    return Path(value).expanduser()


def _optional_str(value: Path | None) -> str | None:
    return str(value) if value is not None else None
