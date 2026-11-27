"""Thread-safe Qt signal hub between workers and the GUI."""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal


class AssistantSignals(QObject):
    """All cross-thread notifications funnel through these queued signals."""

    voice_text = Signal(str, str)          # recognized text, language
    status = Signal(str)
    gemini_result = Signal(str, str, object)
    gemini_stream_chunk = Signal(str)
    speech_state = Signal(str)
    timing_info = Signal(object)
    automation_route = Signal(object)
    automation_finished = Signal(str, bool)
