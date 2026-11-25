# Test Circit on real macOS hardware — for free

You do not own a Mac and nobody you know owns one. You can still run this
project's **entire test suite on a genuine macOS machine** using GitHub
Actions: public repositories get free macOS runners (Apple Silicon), and
the workflow file is already included in this project.

What this gives you (all on real macOS):

* the complete offline pytest suite (~230 tests, including the macOS
  build-path, darwin-backend and engine tests),
* `compileall` syntax compilation of every Python file,
* a real `pip install -r requirements.txt` on macOS — this is the big one:
  it proves every dependency (faster-whisper, ctranslate2, PySide6, …)
  actually installs on a Mac,
* `zsh -n` syntax checks of the `.command` scripts.

What it cannot give you: GUI interaction, microphone input and TCC
permission prompts. Those need a physical Mac in front of you; everything
else is covered.

## Setup (about 5 minutes)

1. Create a free account at <https://github.com> (if you don't have one)
   and create a **new public repository** (public = free macOS runners).
2. Upload this whole project folder to the repository
   (drag-and-drop upload in the browser works; keep the folder structure,
   including `.github/`).
3. Open the repository → **Actions** tab → enable workflows if asked.
4. Click the **"Circit macOS test suite"** workflow → **Run workflow** →
   **Run workflow**.

Within a few minutes you get a green (or red!) run on real macOS hardware.
Open any job to see the pip install log, the test output and the smoke
 test — every line is a real Mac answering your question "does it work on
macOS?".

If a test fails there, the log tells you exactly which one; that is a real
macOS bug report you can act on (or paste back to your AI assistant).

## Why not a virtual Mac on a PC?

Running macOS on non-Apple hardware violates Apple's EULA (macOS is only
licensed for Apple hardware), so there is no legitimate free macOS VM for
a Windows PC, and Docker cannot run macOS at all. Paid cloud Macs
(MacStadium, AWS EC2 Mac) work but are not free. Free GitHub Actions
macOS runners are the one genuinely free, legitimate way to test on real
macOS — that is what this project ships with.

## Tip: keep the suite green locally too

The same tests run on Linux (they skip macOS-only hardware paths), so you
can iterate locally with `pytest` and use the macOS runner as the final
gate before sharing the project.
