"""Circit — a local-first AI voice assistant for Windows and macOS.

Redesigned implementation of the original Circit project.  The package layout
separates concerns so that GUI, speech, TTS, AI, automation and persistence
never share a thread or an import cycle.  Windows runs the Win32 automation
stack; macOS uses the native backend in ``app/automation/darwin.py`` and
``app/local/mac_controls.py``.
"""

__app_name__ = "Circit"
# Semantic version of the new project (independent from the legacy build).
__version__ = "2.1.0"
