"""Central data paths and environment routing for Circit.

All persistent data (settings, logs, speech models, screenshots, reports,
temporary audio) lives under one configurable data root.  The root is
resolved in this order:

1. ``CIRCIT_DATA_DIR`` environment variable (set explicitly by the user or
   by the launch scripts).
2. ``~/Library/Application Support/Circit`` on macOS (the standard
   location; Circit is a macOS-first project).
3. ``~/.local/share/Circit`` on other POSIX systems (useful in CI).

Environment values are set before heavy libraries load so caches and
temporary files land inside the data root.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


def _default_data_dir() -> Path:
    configured = os.environ.get("CIRCIT_DATA_DIR", "").strip()
    if configured:
        return Path(configured)
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Circit"
    return Path.home() / ".local" / "share" / "Circit"


def get_data_dir() -> Path:
    """Return Circit's persistent data root (created on demand)."""
    root = _default_data_dir()
    try:
        root.mkdir(parents=True, exist_ok=True)
    except OSError:
        # A read-only or invalid data dir must not kill the process; fall back
        # to the system temp directory so diagnostics still work.
        root = Path(tempfile.gettempdir()) / "Circit_Data"
        root.mkdir(parents=True, exist_ok=True)
    return root


def sub_dir(name: str) -> Path:
    path = get_data_dir() / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_models_dir() -> Path:
    """Root folder for local speech models (faster-whisper, kokoro)."""
    return sub_dir("models")


def get_kokoro_model_dir() -> Path:
    return get_models_dir() / "kokoro"


def configure_environment() -> Path:
    """Route supported caches and temporary files into the data root.

    Call this once at startup, before importing libraries that cache files.
    """
    root = get_data_dir()
    paths = {
        "npm-cache": root / "npm-cache",
        "Temp": root / "Temp",
        "cache": root / "cache",
        "logs": root / "logs",
        "models": root / "models",
        "downloads": root / "downloads",
        "reports": root / "reports",
        "Screenshots": root / "Screenshots",
    }
    for path in paths.values():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError:
            continue

    env_paths = {
        "CIRCIT_DATA_DIR": root,
        "NPM_CONFIG_CACHE": paths["npm-cache"],
        "npm_config_cache": paths["npm-cache"],
        "CIRCIT_KOKORO_MODEL_DIR": get_kokoro_model_dir(),
    }
    for key, value in env_paths.items():
        os.environ[key] = str(value)

    try:
        # tempfile can cache its selected directory on first use; force it to
        # the data root so audio scratch files stay in one place.
        tempfile.tempdir = str(paths["Temp"])
    except Exception:
        pass
    return root


def get_logs_dir() -> Path:
    return sub_dir("logs")
