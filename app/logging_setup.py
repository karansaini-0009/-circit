"""Application logging with rotating files and console output.

Secrets (API keys, audio payloads, prompts) are never logged by Circit code;
this module only configures handlers and levels.
"""
from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

from .paths import get_logs_dir

_CONFIGURED = False
_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging(level: int = logging.INFO, console: bool = True) -> Path:
    """Configure the root logger once; return the active log file path."""
    global _CONFIGURED
    log_dir = get_logs_dir()
    log_file = log_dir / "circit_assistant.log"

    root = logging.getLogger()
    root.setLevel(level)
    if _CONFIGURED:
        return log_file

    formatter = logging.Formatter(_FORMAT)
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=2_000_000, backupCount=4, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    except OSError:
        # Logging must never prevent startup.
        pass
    if console or not sys.stdout:
        console_handler = logging.StreamHandler(sys.stderr if not sys.stdout else sys.stdout)
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)

    # Quieten chatty third-party loggers.
    for name in ("urllib3", "httpx", "google_genai", "comtypes", "pywinauto"):
        logging.getLogger(name).setLevel(logging.WARNING)
    _CONFIGURED = True
    return log_file


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
