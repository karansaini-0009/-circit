# Circit — a local-first AI voice assistant for macOS

Circit is the renamed, macOS-focused continuation of the NOVA Assistant
project. It is a **separate, Mac-only project**: it contains no Windows
installer, no Windows launcher and no Windows-only packaging — only the code
paths macOS actually runs (the platform-dispatched Windows branches stay in
the source for the shared test suite, but nothing in this project installs
or packages them).

* Talk to it in English or Hindi (or Hinglish) — it listens offline.
* Ask it to open apps, play songs on YouTube, close apps, control volume,
  take screenshots, lock the screen and more.
* Connect a free Gemini API key for general questions, or use it fully
  locally for app/system control even without any key.

## Quick start (macOS)

1. Double-click `INSTALL_CIRCUIT_MAC.command`.
   It finds Python **3.11 or 3.12** (required — see below), creates the
   private `.venv`, installs every verified dependency, downloads the
   offline speech model (~145 MB, once), runs a smoke test and puts a
   `Circit.command` launcher on your Desktop.
2. Grant the two permissions it offers to open (Accessibility, Microphone).
3. Double-click the Desktop `Circit.command` — or the built `Circit.app` if
   you ran `BUILD_APP_MAC.command`.

**Why Python 3.11/3.12?** Circit's offline speech engine is
`faster-whisper`, whose binary backend (`ctranslate2`) publishes macOS
wheels up to CPython 3.12. The installer enforces this automatically.

## Try it first

Say (type in the box or press the mic button and speak):

* `open youtube and play ajj ki raat song` — Circit opens YouTube's result
  page directly, reads the real video titles and plays the best match
  through its `watch?v=` link. **No coordinate clicking anywhere**, so the
  cursor can never hit the wrong button.
* `close youtube` — closes only the browser windows showing YouTube.
* `open safari` / `close chrome` / `minimize vs code`
* `volume up`, `mute`, `screenshot`, `lock screen`, `battery report`
* Hinglish works too: `youtube band karo`, `gaana chalao`.

## What's inside

| Path | Purpose |
| --- | --- |
| `app/` | The assistant: GUI, speech, automation, TTS, Gemini routing |
| `app/automation/darwin.py` | Native macOS backend (AppleScript + System Events + pynput) |
| `app/speech/recognizer.py` | Offline STT — faster-whisper, one multilingual model |
| `app/local/mac_controls.py` | Volume, brightness, Wi-Fi, battery, screenshots on macOS |
| `scripts/circit_build.py` | Builds `Circit.app` with PyInstaller (macOS options) |
| `scripts/setup_models.py` | Pre-downloads the offline speech model |
| `scripts/setup_kokoro.sh` | Optional local Kokoro voices (needs Node.js) |
| `INSTALL_CIRCUIT_MAC.command` | One-click installer (double-click) |
| `BUILD_APP_MAC.command` | Builds the shareable `Circit.app` (double-click) |
| `tests/` | Full offline test suite (pytest) |

macOS specifics — permissions, Gatekeeper, voice playback (`afplay`),
sharing with friends — are in **README_MAC.md**. Problems? See
`TROUBLESHOOTING.md`, then `scripts/smoke_test.py` and `install_log.txt`.

## Dependencies — verified, with a replaced engine

Every binary dependency was checked against PyPI (2026-11-17) for real
macOS wheels. One engine was **replaced** during the port: the Windows
build used `vosk`, but vosk publishes **no macOS wheels at all** —
`pip install vosk` fails on every Mac. Circit therefore uses
`faster-whisper` (pure Python) on top of `ctranslate2` (macOS arm64 +
Intel wheels): one offline multilingual model for English, Hindi and
Hinglish, selected in Settings → Speech (Tiny / Base / Small / Medium).
`tests/test_stt_regression.py` guards this decision permanently.

## Testing on a Mac you don't own

You do not need to buy or borrow a Mac to run this project's test suite on
real macOS hardware: push the folder to a **public GitHub repository** and
GitHub Actions runs the whole suite on a genuine macOS runner for free
(`.github/workflows/macos-tests.yml` is included). See
`TEST_ON_CLOUD_MAC.md` for the 5-minute setup.
