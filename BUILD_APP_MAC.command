#!/bin/zsh
# Circit - build a standalone Circit.app on macOS.
#
# Double-click this file (it needs the project .venv, so run
# INSTALL_CIRCUIT_MAC.command first). It calls scripts/circit_build.py, which:
#   - converts circit_icon.png to circit_icon.icns (sips/iconutil)
#   - runs PyInstaller with the verified macOS options
#   - produces dist/Circit.app and a ready-to-send
#     dist/Circit_sharing_package.zip (with a READ_ME_FIRST.txt)
#
# After a successful build the dist folder is revealed in Finder.

DIR="${0:A:h}"
cd "$DIR" || exit 1

if [[ ! -x "$DIR/.venv/bin/python" ]]; then
  print "No project venv found (.venv/bin/python)."
  print "Run INSTALL_CIRCUIT_MAC.command first - it creates the venv that"
  print "contains PyInstaller - then double-click this file again."
  print "Press Enter to close this window."
  [[ -t 0 ]] && read -r
  exit 1
fi

"$DIR/.venv/bin/python" scripts/circit_build.py "$@"
status=$?
print ""
if [[ $status -eq 0 ]]; then
  print "Build finished - revealing the dist folder in Finder."
  open -R "$DIR/dist" 2>/dev/null || open "$DIR/dist" 2>/dev/null || true
else
  print "BUILD FAILED - scroll up for the PyInstaller output."
fi
print "Press Enter to close this window."
[[ -t 0 ]] && read -r
exit $status
