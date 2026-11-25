# Circit on macOS — permissions, Gatekeeper, sharing

Read this once after installing; it explains everything macOS-specific.

## The three permissions (one time each)

| Permission | Why | Grant it to |
| --- | --- | --- |
| **Accessibility** | Opening/closing apps, typing into apps, pressing shortcuts | Terminal (when launched from it) and `Circit` / `Circit.app` |
| **Microphone** | Live Mode voice input | Terminal or `Circit.app` |
| **Screen Recording** | Screenshots only | Terminal or `Circit.app` |

Open each pane from System Settings → Privacy & Security, or let the
installer open Accessibility and Microphone for you. After granting, restart
Circit once — macOS only hands the permission to a running process on next
launch.

If automation "does nothing", the missing **Accessibility** permission is
the cause 90% of the time: the executor detects it and tells you which app
to enable (the app Circit runs inside — Terminal, or `Circit.app`).

## Wake phrase

Live Mode listens continuously. Say **"Hey Circit"** and then your command;
a bare "Circit" also works and waits for a follow-up. You can rename the
assistant in Settings (the wake phrase follows the name, so "Hey Orion"
works if you rename it to Orion).

## How things work on macOS

* **Apps** are launched/focused through `NSWorkspace` and System Events;
  closing presses the real **AXCloseButton** (the red X) of each matching
  window and only falls back to a graceful AppleScript `quit` for
  non-browser apps. System processes (Finder, Dock, WindowServer, …) and
  Circit itself can never be force-killed.
* **YouTube playback** never touches coordinates: the results page opens by
  URL, video titles are read from the page, and the best match plays
  directly via its `watch?v=` link. Pause/resume/next use YouTube's own
  shortcuts (K / Shift+N) on the focused tab, or the system media key when
  no YouTube window exists. macOS cannot read the player state, so Circit
  says so honestly instead of claiming success it cannot verify.
* **Keyboard input** maps Windows-style plans to Mac reality: CTRL →
  Command, WIN → Command, ALT → Option; media keys map to pynput media keys.
* **Volume/mute, mic input** run through AppleScript; **brightness** via
  IOKit (macOS may refuse software brightness on external displays — Circit
  opens the Displays pane then); **Wi-Fi** via `networksetup`; **lock
  screen** via Ctrl+Cmd+Q; **battery report** via `pmset`.
* **Voice playback** uses macOS's built-in `afplay` for local WAV output —
  no extra audio library needed.
* **API keys** live in the macOS Keychain (services `Circit.GeminiAPI` and
  `Circit.SarvamTTS`), never in plain files.

## Building & sharing the app

1. Double-click `BUILD_APP_MAC.command` (needs the installer's `.venv`).
2. It produces `dist/Circit.app` and `dist/Circit_sharing_package.zip`
   (the zip includes a `READ_ME_FIRST.txt` for the recipient).
3. Send the zip. Your friend extracts it and double-clicks `Circit.app`.

**Gatekeeper:** because the app is unsigned, the first launch may warn
("cannot verify the developer"). Right-click `Circit.app` → **Open** →
**Open** (once). If macOS still blocks it:
System Settings → Privacy & Security → scroll down → "Open Anyway".
Your friend must also grant the Accessibility + Microphone permissions to
`Circit.app` itself.

## Optional: local Kokoro voices

Sarvam Roopa (online) and Gemini TTS are the defaults. For a fully offline
voice, install Node.js LTS and run `scripts/setup_kokoro.sh` once; the
voice model then downloads on first use into Circit's data folder.

## Data locations

* Data root: `~/Library/Application Support/Circit`
  (override with the `CIRCIT_DATA_DIR` environment variable)
* Settings: `<data root>/Circit/settings.json` — migrated once, non-
  destructively, from an earlier NOVA macOS install if one exists.
* Logs: `<data root>/logs/`, plus `install_log.txt` in the project folder.

## Testing without owning a Mac

Push this folder to a public GitHub repository — the included
`.github/workflows/macos-tests.yml` runs the complete test suite on a real
macOS runner (free for public repos). Details in `TEST_ON_CLOUD_MAC.md`.
