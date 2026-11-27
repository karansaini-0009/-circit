"""Secure credential storage through the OS keyring (keyring package).

* macOS    — the macOS Keychain (services below)
* Windows  — Windows Credential Manager (dormant Windows code paths only)

Two independent credentials are supported:

* ``gemini`` — Google Gemini API key  (service ``Circit.GeminiAPI``)
* ``sarvam`` — Sarvam AI API key      (service ``Circit.SarvamTTS``)

Circit stores its keys under its own service names (the old NOVA install
used ``NOVA.*`` services); a fresh Circit setup asks for each key once.

Keys are never hard-coded, never written to settings JSON, and never logged.
"""
from __future__ import annotations

import logging
import sys
from typing import Dict, Tuple

try:
    import keyring
    from keyring.errors import KeyringError
except Exception:  # pragma: no cover - keyring is a hard dependency on Windows
    keyring = None
    KeyringError = Exception  # type: ignore[assignment,misc]

log = logging.getLogger(__name__)

# service name, account name — preserved from the original project.
CREDENTIAL_TARGETS: Dict[str, Tuple[str, str]] = {
    "gemini": ("Circit.GeminiAPI", "api-key"),
    "sarvam": ("Circit.SarvamTTS", "api-key"),
}

_CREDENTIAL_BACKEND = None  # test hook: None => use the real keyring module


def credential_store_name() -> str:
    """Human-readable name of the OS credential store (for error messages)."""
    if sys.platform == "win32":
        return "Windows Credential Manager"
    if sys.platform == "darwin":
        return "the macOS Keychain"
    return "the system keyring"


def _backend():
    if _CREDENTIAL_BACKEND is not None:
        return _CREDENTIAL_BACKEND
    if keyring is None:
        raise RuntimeError(
            "The keyring package is unavailable. Run the Circit installer to "
            "repair the Circit environment."
        )
    return keyring


class CredentialError(RuntimeError):
    """Raised when a credential cannot be stored or retrieved."""


def get_credential(name: str) -> str | None:
    """Return the stored secret for ``name`` or None when missing."""
    if name not in CREDENTIAL_TARGETS:
        raise KeyError(f"Unknown credential: {name}")
    service, account = CREDENTIAL_TARGETS[name]
    try:
        value = _backend().get_password(service, account)
    except Exception as exc:  # KeyringError and backend-specific errors
        log.error("Credential lookup failed for %s: %s", name, type(exc).__name__)
        raise CredentialError(
            f"{credential_store_name().capitalize()} could not provide the {name} "
            f"API key ({type(exc).__name__})."
        ) from exc
    if value is None:
        return None
    value = value.strip()
    return value or None


def set_credential(name: str, value: str) -> None:
    """Store or replace a secret; empty values are rejected."""
    if name not in CREDENTIAL_TARGETS:
        raise KeyError(f"Unknown credential: {name}")
    if not isinstance(value, str) or not value.strip():
        raise CredentialError(f"The {name} API key cannot be empty.")
    service, account = CREDENTIAL_TARGETS[name]
    try:
        _backend().set_password(service, account, value.strip())
    except Exception as exc:
        log.error("Credential write failed for %s: %s", name, type(exc).__name__)
        raise CredentialError(
            f"{credential_store_name().capitalize()} refused to store the {name} "
            f"API key ({type(exc).__name__})."
        ) from exc


def delete_credential(name: str) -> None:
    if name not in CREDENTIAL_TARGETS:
        raise KeyError(f"Unknown credential: {name}")
    service, account = CREDENTIAL_TARGETS[name]
    try:
        _backend().delete_password(service, account)
    except Exception:
        # Deleting a missing credential is not an error for our callers.
        log.debug("Credential delete for %s reported an error", name, exc_info=True)


def mask_secret(value: str | None) -> str:
    """Mask a secret for display: keep the first/last 4 characters."""
    if not value:
        return ""
    value = value.strip()
    if len(value) <= 8:
        return "•" * len(value)
    return f"{value[:4]}{'•' * (len(value) - 8)}{value[-4:]}"


# Backwards-friendly aliases used by the TTS/Gemini modules.
def get_api_key() -> str | None:
    return get_credential("gemini")


def set_api_key(value: str) -> None:
    set_credential("gemini", value)


def get_sarvam_api_key() -> str | None:
    return get_credential("sarvam")


def set_sarvam_api_key(value: str) -> None:
    set_credential("sarvam", value)
