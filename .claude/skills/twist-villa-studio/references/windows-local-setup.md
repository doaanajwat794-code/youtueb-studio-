# Running Twist Villa Studio on the owner's Windows 11 PC

**Why:** the cloud session can't read files on the owner's computer, and it deletes its own files when
the session ends. Clips live on the PC, so production (import → edit → export) runs in Claude Code on
the PC. Settings, stories and prompts sync through GitHub; media never goes to GitHub.

## One-time setup (PowerShell, one command at a time)
1. `winget install --id Git.Git -e`
2. `winget install --id Python.Python.3.12 -e`
3. `irm https://claude.ai/install.ps1 | iex` (the official Claude Code installer for Windows)
4. Close and reopen PowerShell, then run `claude --version`
5. `cd $HOME\Documents`
   `git clone https://github.com/doaanajwat794-code/youtueb-studio-.git TwistVilla`
6. `cd TwistVilla` then `py -m pip install -r requirements.txt`
7. `claude` → sign in → "Continue the Twist Villa project."

## Each session on the PC
- Start: `cd $HOME\Documents\TwistVilla` then `git pull`, then `claude`.
- Files go in `media\<CODE>\incoming\` (File Explorer → Documents → TwistVilla → media → CODE → incoming).
- Commands: `py -m studio import-clips <slug>`, `py -m studio make-sfx <slug>`,
  `py -m studio assemble <slug>`, `py -m studio thumbnail <slug> --at 1.8 --text "..."`.
- The finished video is `media\<CODE>\final.mp4` (open it in the Windows Photos/Media Player app).
- End: commit and push text changes (Claude does this); copy `final.mp4` to Google Drive as a backup.

## To verify on the first local run (not yet tested on Windows)
- The ffmpeg bundled via `imageio-ffmpeg` runs; burned captions render (font fallback on Windows:
  if "DejaVu Sans" is missing, set `render.subtitles.font: Arial` in `config/providers.yaml`).
- The SessionStart hook prints the status file (it needs `cat`, which is available when Git for Windows is installed).
