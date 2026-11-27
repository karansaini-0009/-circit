"""Version markers used by settings migration and diagnostics."""
from __future__ import annotations

APP_NAME = "Circit"
APP_VERSION = "1.0.0"

SETTINGS_SCHEMA_VERSION = 2
# Settings files written by the original project carry no version field and
# are detected by their key set; see app/settings.py for the migration.
LEGACY_SETTINGS_SCHEMA_VERSION = 1
