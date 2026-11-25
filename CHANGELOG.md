# Changelog — Circit

Circit is the renamed, macOS-focused continuation of NOVA Assistant. This
file lists what changed at each step of that lineage.

## 1.0.0 — Circit (macOS edition) (2026-11-17)

- **Rebrand.** The project, app, bundle and every user-facing surface are
  now **Circit** (`Circit.app`, `Circit.command` Desktop launcher,
  `Circit.GeminiAPI` / `Circit.SarvamTTS` Keychain services,
  `CIRCIT_DATA_DIR`, data root `~/Library/Application Support/Circit`,
  `Circit-screenshot-…` files). The Kokoro voice id `af_nova` is a real
  engine identifier and was intentionally kept.
- **Built from the latest NOVA_OneClick codebase** (v2.0.3 reliable-YouTube
  playback + close-any-app work, with the v2.1.0 macOS backend on top) —
  not from any older snapshot.
- **Offline STT engine replaced: vosk → faster-whisper.** Dependency audit
  against PyPI (2026-11-17) proved vosk publishes **no macOS wheels at
  all** (0.3.45 ships only Linux/Windows wheels), so `pip install vosk`
  fails on every Mac. Circit now runs faster-whisper (pure Python) on
  ctranslate2 (macOS arm64 + x86_64 wheels, CPython 3.10–3.12): one
  offline multilingual model covers English + Hindi + Hinglish, with per-
  segment language detection. New Settings picker: Tiny / Base / Small /
  Medium. `tests/test_stt_regression.py` now enforces vosk-absence and
  faster-whisper presence instead of the reverse.
- **Windows-only dependencies dropped** from the manifest (pycaw, comtypes,
  pywin32, pywinauto, echoff): nothing in the Mac project installs them;
  the same features run through AppleScript/IOKit/pynput on macOS.
- **Installer hardened for this stack:** `INSTALL_CIRCUIT_MAC.command`
  requires Python 3.11/3.12 (ctranslate2 wheel coverage), explains why, and
  can install Python 3.12 via Homebrew (`brew install python@3.12`).
- **Free real-Mac testing:** `.github/workflows/macos-tests.yml` runs the
  full offline suite on a genuine GitHub Actions macOS runner (free for
  public repositories) — see TEST_ON_CLOUD_MAC.md.
- **Migration:** settings migrate one-time and non-destructively from an
  earlier NOVA macOS install (`~/Library/Application Support/NOVA`); vosk
  model keys are dropped rather than guessed into whisper equivalents.
- **Simplified for macOS-first:** the Windows legacy data-root routing
  (`D:\NOVA_DATA`) was removed from the path resolver; the Windows
  execution branches remain only as dormant, platform-guarded code that the
  shared test suite still exercises.

## 2.1.0 — NOVA macOS support (inherited)

Native macOS automation backend (`app/automation/darwin.py`) implementing
the full plan vocabulary with AppleScript + System Events + pynput; CTRL→
Command mapping; AXCloseButton-based "close any app" with system-process
protection; URL-driven YouTube playback with `watch?v=` direct links;
macOS system controls (volume/mic/brightness/Wi-Fi/lock/battery/
screenshots); `.command` installer and PyInstaller `.app` build.

## 2.0.3 — Reliable YouTube playback + close any app (inherited)

YouTube search-and-play opens the results page directly and plays the best
match by URL — zero coordinate clicks. Cursor-free UIA Invoke activation on
Windows. `close_app` / `close_active_window` / `minimize_app` /
`maximize_app` with protected system processes and deterministic
English/Hinglish close parsing before the model router.

## 2.0.2 / 2.0.1 (inherited)

Single-file `--onefile` exe default with `_MEIPASS` icon fix; one-click
Windows installer with a private venv, pip check, smoke test and desktop
launcher.
