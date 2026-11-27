"""Code response extraction and safe new-file creation.

Preserved behaviour from the original project: extract the first fenced code
block from an AI answer, refuse to overwrite existing files, enforce a size
limit and require a sane file extension.
"""
from __future__ import annotations

import re
from pathlib import Path


def extract_code(text: str) -> str:
    """Return the first fenced code block, or raise ValueError."""
    text = str(text or "").strip()
    match = re.search(r"```[^\n`]*\n(.*?)```", text, re.S)
    if match:
        return match.group(1).rstrip() + "\n"
    if not text:
        raise ValueError("The AI returned an empty response; no file was created.")
    raise ValueError(
        "The AI response did not contain a fenced code block. No file was "
        "created; ask for the code again in a single fenced block."
    )


MAX_CODE_BYTES = 2_000_000


def save_new_code_file(path_text: str, code: str) -> str:
    """Write ``code`` to ``path_text`` only when the target is a new file."""
    if not isinstance(path_text, str) or not path_text.strip():
        raise ValueError("A destination path is required.")
    path = Path(path_text).expanduser().resolve()
    if path.exists() and path.is_dir():
        raise ValueError("Choose a file path, not a folder.")
    if not path.suffix or len(path.suffix) > 12:
        raise ValueError(
            "Please include a normal file extension, such as .py, .js, .java, or .cpp."
        )
    if path.exists():
        raise FileExistsError(
            "That file already exists. Choose a new filename; Circit will not overwrite it."
        )
    if len(code.encode("utf-8")) > MAX_CODE_BYTES:
        raise ValueError("Generated code exceeds the 2 MB safety limit.")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Recheck after creating parent directory to avoid accidental overwrite.
    if path.exists():
        raise FileExistsError("That file already exists. Circit will not overwrite it.")
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(code)
    return str(path)
