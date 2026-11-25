# Circit — Troubleshooting (macOS)

Work top to bottom; the first three items cover most reports.

## 1. Automation does nothing (apps don't open / keys not typed)

**Cause: the Accessibility permission is missing.** Enable it for the app
Circit runs inside (Terminal, or `Circit.app` after building it):
System Settings → Privacy & Security → Accessibility → toggle the app on.
Then quit Circit fully (`pkill -f "app/main.py"` from Terminal) and start
it again — permissions are only read at launch.

Circit detects this state and prints exactly which app needs the toggle;
the same message appears in `install_log.txt` / the log file.

## 2. Live Mode says the microphone is silent / never hears me

* Grant Microphone: System Settings → Privacy & Security → Microphone.
* macOS may also show a per-app mic icon in the menu bar; click it to see
  which app holds the mic.
* First use downloads the speech model (~145 MB for `base`). If the
  download was interrupted, delete
  `~/Library/Application Support/Circit/models/whisper/` and press the mic
  button again, or run `.venv/bin/python scripts/setup_models.py`.
* Pick a smaller model (Settings → Speech model → Tiny) on older Macs.

## 3. "faster-whisper is not installed" / engine errors

* The speech engine needs **Python 3.11 or 3.12** — on 3.13+ the binary
  backend has no macOS wheels and `pip install` fails. Re-run
  `INSTALL_CIRCUIT_MAC.command`; it checks the version and explains.
* Repair the venv: delete the `.venv` folder and re-run the installer.

## 4. Circit says a key/service is missing

* Gemini key: Settings → API keys, or run
  `.venv/bin/python setup_sarvam_key.py` style helpers are not needed —
  settings → save. Keys go into the macOS Keychain under
  `Circit.GeminiAPI` / `Circit.SarvamTTS`. If Keychain prompts to allow
  access, click "Always Allow".
* Local control (volume, apps, close, YouTube playback) works **without**
  any key.

## 5. "Circit is already running"

A previous instance is still alive (or a stale lock file exists):

    pkill -f "app/main.py"
    rm -f ~/Library/Application\ Support/Circit/circit_assistant.lock

## 6. YouTube plays the wrong song / does not play

* Circit plays the best title match from the results page — be more
  specific in the request (add the movie/artist name).
* If playback starts muted, unmute with `unmute` or the tab's own controls.
* Pause/resume/next work on the **focused** tab — click the YouTube tab
  once, then say it again.

## 7. Voice output too quiet / delayed

* Sarvam TTS needs internet; Gemini TTS needs a key; for fully offline
  speech run `scripts/setup_kokoro.sh` (needs Node.js) and pick Kokoro in
  Settings. Local WAV playback uses macOS `afplay`.
* Gemini TTS playback streams through `afplay` — if a firewall prompt
  appears, allow it.

## 8. Screenshots don't appear

Screen Recording permission is missing: System Settings → Privacy &
Security → Screen Recording → enable the app Circit runs inside, then
restart Circit. Files land in `~/Library/Application Support/Circit/Screenshots`
named `Circit-screenshot-<timestamp>.png`.

## 9. Brightness / Wi-Fi / Bluetooth refuse

* Brightness: macOS restricts software brightness on some external
  displays; Circit opens the Displays pane and says so honestly.
* Wi-Fi toggle: `networksetup` may ask for the admin password once.
* Bluetooth: macOS has no user-level toggle API; Circit opens the pane and
  explains.

## 10. Built Circit.app is blocked by Gatekeeper

Right-click `Circit.app` → Open → Open (first launch only), or System
Settings → Privacy & Security → "Open Anyway". The app is unsigned; this
is expected for personally built apps.

## 11. Everything else

Run the diagnostics and read the logs:

    .venv/bin/python scripts/smoke_test.py
    .venv/bin/python app/main.py --diagnostic

* App log: `~/Library/Application Support/Circit/logs/circit_assistant.log`
  (secrets are never logged)
* Installer log: `install_log.txt` in the project folder
* Model/bridge cache: `~/Library/Application Support/Circit/models/`

Move the whole project folder elsewhere? Fine — nothing outside the folder
and the data root is touched; the data root can be moved with
`CIRCIT_DATA_DIR=/new/path` before launch.
