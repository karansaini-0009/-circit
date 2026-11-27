"""Application entry point and lifecycle.

Responsibilities kept deliberately small: environment routing, logging,
single-instance protection, Qt application creation and clean shutdown.

Command line:
* ``main.py``            — normal start (run it via the Desktop
  ``Circit.command`` launcher created by INSTALL_CIRCUIT_MAC.command).
* ``main.py --no-orb``   — do not start the floating desktop launcher
  (Windows-only concept; macOS always runs without the orb).
* ``main.py --diagnostic`` — keep console logging verbose and pause on exit
  so errors remain visible when troubleshooting.
"""
from __future__ import annotations

import argparse
import ctypes
import os
import sys
from pathlib import Path

# Route caches/temp into the data root before any heavy library imports.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.paths import configure_environment, get_data_dir  # noqa: E402

configure_environment()

from app.logging_setup import setup_logging  # noqa: E402
from app.settings import load_settings  # noqa: E402

APP_MUTEX_NAME = "Circit_SingleInstance_Mutex"


def acquire_single_instance() -> bool:
    """Prevent duplicate assistant instances (mutex on Windows, lockfile else)."""
    if sys.platform == "win32":
        try:
            handle = ctypes.windll.kernel32.CreateMutexW(None, False, APP_MUTEX_NAME)
            # ERROR_ALREADY_EXISTS == 183
            return not (handle and ctypes.windll.kernel32.GetLastError() == 183)
        except Exception:
            return True  # never block startup on a guard failure
    lock_path = get_data_dir() / "circit_assistant.lock"
    try:
        if lock_path.exists():
            try:
                os.kill(int(lock_path.read_text().strip() or 0), 0)
                return False  # process still alive
            except (OSError, ValueError):
                pass  # stale lock
        lock_path.write_text(str(os.getpid()), encoding="utf-8")
        return True
    except OSError:
        return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Circit")
    parser.add_argument("--no-orb", action="store_true",
                        help="Do not start the floating desktop launcher")
    parser.add_argument("--diagnostic", action="store_true",
                        help="Verbose console logging for troubleshooting")
    args = parser.parse_args()

    setup_logging(
        level="DEBUG" if args.diagnostic else "INFO",
        console=args.diagnostic or sys.stdout is not None,
    )

    if not acquire_single_instance():
        print("Circit is already running. Check the system tray/taskbar "
              "or the floating orb.")
        return 0

    from PySide6.QtWidgets import QApplication

    from app.ui.main_window import MainWindow

    settings = load_settings()

    app = QApplication(sys.argv)
    app.setApplicationName(settings.get("assistant_name", "Circit"))
    # Frozen exe builds keep bundled data files in sys._MEIPASS (one-file:
    # a temp unpack folder; one-folder: the _internal folder). Source runs
    # use the project root two levels above this file.
    icon_base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    icon_path = icon_base / "circit_icon.png"
    if icon_path.exists():
        try:
            from PySide6.QtGui import QIcon
            app.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass

    window = MainWindow(settings)
    window.show()

    if not args.no_orb and not getattr(sys, "frozen", False) and sys.platform != "darwin":
        # The launcher is a separate process so a launcher crash can never
        # take the assistant down and vice versa. In a frozen (PyInstaller)
        # build there is no separate interpreter to spawn it with — spawning
        # would just re-run this exe — so the exe build starts without the
        # floating orb launcher. On macOS, Tk offers no per-pixel window
        # transparency ("-transparentcolor" is Windows-only), so the orb
        # would render as an opaque square window and is skipped too.
        try:
            launcher_main = Path(__file__).resolve().parents[1] / "launcher" / "circit_orb.py"
            if launcher_main.exists():
                import subprocess
                python = sys.executable
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                subprocess.Popen(
                    [python, "-W", "ignore", str(launcher_main)],
                    cwd=str(PROJECT_ROOT := launcher_main.parents[1]),
                    creationflags=creationflags,
                    close_fds=True,
                )
        except Exception:
            # An unavailable launcher must not prevent the assistant from running.
            pass

    exit_code = app.exec()

    try:  # clean lock-file shutdown on non-Windows
        if sys.platform != "win32":
            lock_path = get_data_dir() / "circit_assistant.lock"
            if lock_path.exists():
                try:
                    if lock_path.read_text().strip() == str(os.getpid()):
                        lock_path.unlink()
                except OSError:
                    pass
    except Exception:
        pass
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
