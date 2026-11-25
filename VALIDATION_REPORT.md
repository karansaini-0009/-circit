# Circit — Validation Report (v1.0.0, 2026-11-17)

Circit was developed without access to any Mac. This report states exactly
what was verified, how, and what still needs real hardware.

## 1. Source lineage

* Built from the **latest NOVA_Assistant_OneClick.zip** (v2.0.3 reliable
  YouTube playback + close-any-app, with the v2.1.0 macOS backend on top).
  The extraction was verified byte-identical to the delivered zip with
  `diff -rq` (clean) before assembly.
* `rrrr.zip` (the user's original flat NOVA project) was used as
  reference/history only, as instructed.

## 2. Dependency audit — the reason vosk was replaced

Every dependency was checked against the live PyPI JSON API (2026-11-17):

| Package | macOS wheels | Verdict |
| --- | --- | --- |
| vosk 0.3.45 | **NONE — Linux/Windows only** | **REPLACED** |
| faster-whisper 1.2.1 | pure Python (py3-none-any) | new STT engine |
| ctranslate2 4.9.0 | macosx_11_0 arm64 + x86_64, cp310–cp312 | backend |
| onnxruntime 1.32.0 | macosx_14_0 arm64 (VAD only) | transitive, OK |
| av 19.x / tokenizers 0.23.x | macosx arm64 + x86_64 | transitive, OK |
| PySide6 6.12 | macosx_14_0_universal2 | OK (`>=6.6` pin resolves older on macOS 13) |
| sounddevice 0.5.6 | universal2 (bundles PortAudio) | OK |
| psutil / Pillow | arm64 + x86_64 | OK |
| pynput / keyring / google-genai / sarvamai / numpy | pure Python | OK |
| pycaw / comtypes / pywin32 / pywinauto / echoff | Windows-only | **DROPPED from manifest** |

Consequences encoded in the project:

* requirements.txt ships only macOS-installable packages;
* `INSTALL_CIRCUIT_MAC.command` requires Python 3.11/3.12 (ctranslate2
  wheel ceiling) and explains why;
* `tests/test_stt_regression.py` inverted: vosk/pyaudio/pyautogui are
  forbidden everywhere (requirements lines + AST imports), faster-whisper
  must be the wired engine.

## 3. Test suite (this Linux sandbox, no GUI, no audio hardware)

`pytest -q tests` → **229 passed, 10 skipped** (skips = optional engines not
installed here: faster-whisper real-audio test, TTS/STT services). Suite
includes:

* the full inherited NOVA suite (app registry, intents, plans, darwin
  backend mocking, credentials, settings migration, kokoro, TTS, speech,
  files, UI offscreen),
* `tests/test_circit_build.py` — 13 static checks of the macOS packaging
  path (colon `--add-data`, whisper stack collect-all, pynput branches,
  icns handling, share-zip contents, installer-hint messages),
* `tests/test_stt_regression.py` — new dependency-guard tests.

`python -m compileall -q app scripts tests` → all files compile.
`bash -n` on all three shell scripts → parse OK (zsh itself is unavailable
in this sandbox; the shebang/LF/exec-bit structure is additionally asserted
by `tests/test_darwin_support.py::test_mac_command_scripts`).

## 4. Brand audit

`grep -rni "nova"` over the whole tree returns only:

* `af_nova` — the real Kokoro voice id (kept on purpose) and its label,
* documented legacy references (settings migration from an earlier NOVA
  install, rename history in README/CHANGELOG/VALIDATION_REPORT).

No NOVA strings remain in code identifiers, UI text, thread names, file
names, log names, env vars (`CIRCIT_DATA_DIR`, `CIRCIT_KOKORO_MODEL_DIR`),
service names (`Circit.GeminiAPI`), or the groundings marker
(`CIRCIT_GROUNDING_SOURCES`).

Windows-leftover audit: `.bat`/`.ps1`/`.lnk`/`.ico`/orb assets are absent;
remaining win32 mentions are only inside platform-guarded dormant branches
(lazy `win32gui` imports, Start-menu `.lnk` scan, `taskkill` semantics
comment) that the shared tests exercise.

## 5. What still needs real Mac hardware

Mocked, OS-independent tests cover command construction, window-list
parsing, matching/scoring, close-flow decisions and shortcut policy. Real
behaviour that can only be confirmed on a Mac: TCC permission prompts,
AX button pressing, `sips`/`iconutil` icns conversion, Keychain dialogs,
`afplay` audio output, real whisper transcription speed. The included
GitHub Actions workflow (`.github/workflows/macos-tests.yml`) runs the full
suite + a real `pip install` on genuine macOS runners for free — see
TEST_ON_CLOUD_MAC.md.
