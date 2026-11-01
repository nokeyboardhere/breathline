
"""Breathline settings persistence."""

import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".breathline.json"

DEFAULT_SETTINGS = {
    "regulation": 0.0,
    "tempo": 0.0,
    "inhale_color": "#55B8E8",
    "exhale_color": "#E6A15C",
    "duration": 3600,
    "theme": "Dark",
    "window_geometry": "600x750",
}


def load_settings():
    """Load saved settings, falling back to defaults."""

    if not CONFIG_FILE.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as file:
            saved = json.load(file)

        # Migrate the old rhythm setting to tempo.
        if "tempo" not in saved and "rhythm" in saved:
            saved["tempo"] = saved["rhythm"]

        saved.pop("rhythm", None)

        settings = DEFAULT_SETTINGS.copy()
        settings.update(saved)
        return settings

    except (json.JSONDecodeError, OSError, TypeError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """Save settings to disk."""

    try:
        with CONFIG_FILE.open("w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4)

    except OSError:
        pass

