#!/bin/zsh
# Circit - one-click macOS installer (v1.0.0).
#
# Double-click this file. Terminal opens and runs everything:
#   1. finds a suitable Python 3.11 or 3.12 (REQUIRED: faster-whisper's
#      backend ctranslate2 publishes macOS wheels up to Python 3.12), or
#      offers to install one with Homebrew
#   2. creates the private .venv and installs the verified dependencies
#   3. runs `pip check` and the import smoke test
#   4. pre-downloads the offline speech model (~145 MB, English + Hindi
#      + Hinglish in one multilingual model)
#   5. creates a double-clickable Circit.command launcher on the Desktop
#   6. explains and optionally opens the macOS permission panes
#
# Full technical log: install_log.txt (this folder).
# Manual fallback: see README_MAC.md.

set -o pipefail

DIR="${0:A:h}"
cd "$DIR" || exit 1
LOGFILE="$DIR/install_log.txt"
: > "$LOGFILE"

log() { print -- "$*" | tee -a "$LOGFILE"; }
run_logged() { "$@" 2>&1 | tee -a "$LOGFILE"; }

log "=============================================================="
log " Circit macOS installer - $(date)"
log " project folder: $DIR"
log "=============================================================="

# --- 1. macOS check ---------------------------------------------------------
if [[ "$(uname -s)" != "Darwin" ]]; then
  log "ERROR: this installer is for macOS only."
  exit 1
fi
log "macOS: $(sw_vers -productName 2>/dev/null) $(sw_vers -productVersion 2>/dev/null) ($(uname -m))"

# --- 2. find Python 3.11/3.12 (REQUIRED - newest usable first) ---------------
# ctranslate2 (faster-whisper's engine) ships macOS wheels for CPython
# 3.10-3.12 only.  Python 3.13/3.14 would fail `pip install` at the wheel
# stage, so they are rejected here with a clear message instead.
PY=""
for cand in python3.12 python3.11 \
            /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3.11 \
            /usr/local/bin/python3.12 /usr/local/bin/python3.11 \
            python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 \
            /usr/bin/python3; do
  if command -v "$cand" >/dev/null 2>&1; then
    if "$cand" -c 'import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] <= (3, 12) else 1)' 2>/dev/null; then
      PY="$(command -v "$cand")"
      break
    fi
  fi
done

if [[ -z "$PY" ]]; then
  # Distinguish "no Python at all" from "only unusable versions".
  BAD=""
  for cand in python3.13 python3.14 python3 /usr/bin/python3; do
    if command -v "$cand" >/dev/null 2>&1; then BAD="$($cand -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null)"; break; fi
  done
  log ""
  if [[ -n "$BAD" ]]; then
    log "Found Python $BAD, but Circit needs Python 3.11 or 3.12."
    log "(Python 3.13+ cannot install the speech engine's macOS wheels yet.)"
  else
    log "No Python 3.11/3.12 was found on this Mac."
  fi
  if command -v brew >/dev/null 2>&1; then
    printf "Homebrew detected. Install Python 3.12 now with 'brew install python@3.12'? [y/N] "
    if [[ -t 0 ]]; then read -r answer; else answer="n"; fi
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
      log "Running: brew install python@3.12"
      if run_logged brew install python@3.12; then
        for cand in python3.12 /opt/homebrew/bin/python3.12 /usr/local/bin/python3.12 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
          if command -v "$cand" >/dev/null 2>&1 && \
             "$cand" -c 'import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] <= (3, 12) else 1)' 2>/dev/null; then
            PY="$(command -v "$cand")"; break
          fi
        done
      fi
    fi
  fi
  if [[ -z "$PY" ]]; then
    log ""
    log "Please install Python 3.12 (or 3.11) and run this installer again:"
    log "  - python.org: https://www.python.org/downloads/macos/  (get the 64-bit Python 3.12 installer), or"
    log "  - Homebrew:   https://brew.sh then 'brew install python@3.12'"
    exit 1
  fi
fi
log "Python found: $PY ($($PY -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])'))"

# --- 3. virtual environment -------------------------------------------------
if [[ -x "$DIR/.venv/bin/python" ]]; then
  printf "A .venv already exists. Reuse it? [Y/n] "
  if [[ -t 0 ]]; then read -r reuse; else reuse="y"; fi
  if [[ "$reuse" == "n" || "$reuse" == "N" ]]; then
    BACKUP=".venv_backup_$(date +%Y%m%d%H%M%S)"
    log "Moving the old .venv to $BACKUP"
    mv "$DIR/.venv" "$DIR/$BACKUP"
  fi
fi
if [[ ! -x "$DIR/.venv/bin/python" ]]; then
  log "Creating virtual environment (.venv) ..."
  if ! run_logged "$PY" -m venv "$DIR/.venv"; then
    log "ERROR: could not create the venv (see install_log.txt)."
    exit 1
  fi
fi
VENV_PY="$DIR/.venv/bin/python"
log "Upgrading pip ..."
run_logged "$VENV_PY" -m pip install --upgrade pip --quiet

# --- 4. dependencies ---------------------------------------------------------
log "Installing dependencies from requirements.txt ..."
if ! run_logged "$VENV_PY" -m pip install -r "$DIR/requirements.txt"; then
  log "ERROR: pip could not install every dependency (see install_log.txt)."
  exit 1
fi
log "Verifying package metadata (pip check) ..."
if ! run_logged "$VENV_PY" -m pip check; then
  log "ERROR: pip check failed (see install_log.txt)."
  exit 1
fi

# --- 5. smoke test ------------------------------------------------------------
log "Running the import smoke test ..."
if ! run_logged "$VENV_PY" "$DIR/scripts/smoke_test.py"; then
  log "ERROR: the smoke test failed (see install_log.txt)."
  exit 1
fi

# --- 6. offline speech model ----------------------------------------------------
log "Downloading the offline speech model (~145 MB, English + Hindi + Hinglish) ..."
run_logged "$VENV_PY" "$DIR/scripts/setup_models.py" || \
  log "WARNING: model download failed; Live Mode will retry it automatically later."

# --- 7. Desktop launcher --------------------------------------------------------
DESKTOP="$HOME/Desktop"
[[ -d "$DESKTOP" ]] || DESKTOP="$HOME"
LAUNCHER="$DESKTOP/Circit.command"
cat > "$LAUNCHER" <<LAUNCHER_EOF
#!/bin/zsh
# Circit launcher (created by INSTALL_CIRCUIT_MAC.command)
cd "$DIR" || exit 1
exec "$DIR/.venv/bin/python" app/main.py
LAUNCHER_EOF
chmod 755 "$LAUNCHER"
log "Created the launcher: $LAUNCHER  (double-click it to start Circit)"

# --- 8. macOS permissions -------------------------------------------------------
log ""
log "macOS permissions - Circit needs these once:"
log "  1. Accessibility   -> lets Circit open/close apps and type for you."
log "     Enable it for Terminal (you are running Circit from a terminal)"
log "     and later also for Circit if you build the .app."
log "  2. Microphone      -> needed for voice (Live Mode)."
log "  3. Screen Recording -> only needed for screenshots."
printf "Open the Accessibility settings pane now? [Y/n] "
if [[ -t 0 ]]; then read -r open_acc; else open_acc="y"; fi
if [[ "$open_acc" != "n" && "$open_acc" != "N" ]]; then
  open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility" || true
fi
printf "Open the Microphone settings pane now? [Y/n] "
if [[ -t 0 ]]; then read -r open_mic; else open_mic="y"; fi
if [[ "$open_mic" != "n" && "$open_mic" != "N" ]]; then
  open "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone" || true
fi

# --- 9. launch ------------------------------------------------------------------
printf "Start Circit now? [Y/n] "
if [[ -t 0 ]]; then read -r start; else start="y"; fi
if [[ "$start" != "n" && "$start" != "N" ]]; then
  nohup "$VENV_PY" app/main.py >/dev/null 2>&1 &
  log "Circit started (window opens in a few seconds)."
fi

log ""
log "=============================================================="
log " INSTALLATION COMPLETE"
log "  - Start Circit:    double-click Circit.command on the Desktop"
log "  - Build a .app:    double-click BUILD_APP_MAC.command"
log "  - First steps:     README_MAC.md (permissions, sharing, notes)"
log "  - Optional voice:  scripts/setup_kokoro.sh (local Kokoro voices)"
log "  - Full log:        $LOGFILE"
log "=============================================================="
log "Waiting 10 seconds before closing (press Ctrl+C to keep it open) ..."
sleep 10
exit 0
