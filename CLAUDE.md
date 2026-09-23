# Twist Villa Studio — project memory

This repository is the production studio for the YouTube channel **Twist Villa**
(https://www.youtube.com/@TwistVela). It makes original, long-form (15–30 min),
English, 16:9, 1920x1080 AI-generated story videos. **No Shorts.**

The owner is not a software developer. Explain in plain language, keep answers
structured and specific, and never make them re-explain what is already saved here.

## Start of every session (mandatory)

Use the `twist-villa-studio` skill for any work in this repo. Before anything else, read:

1. `state/STATUS.md` — current phase, active video, and the **next pending task**
2. `config/channel.yaml` — channel identity and content direction
3. `config/budget.yaml` — spend limits and approval rules
4. `state/decisions.md` — permanent decisions the owner already approved

Then continue from the next pending task in `state/STATUS.md`. Read the other files
(`config/storytelling-framework.md`, `config/providers.yaml`, `research/*`) when the
task touches them.

## Hard rules

- **Money:** never call a paid API without the owner's explicit approval of a written
  cost estimate for that step. Record every approved spend in `state/spend-ledger.csv`.
  The code enforces this (`studio/budget.py`); never bypass or weaken the guard.
- **Publishing:** uploads are always `private`. Never make a video public, unlisted,
  or scheduled without explicit owner approval in the current conversation.
- **Secrets:** API keys and OAuth tokens live in `.env` / environment secrets / the
  user config dir — never in git. Never print a key into a file that is committed.
- **Media:** rendered video, audio and images go in `media/` (git-ignored) and then to
  external storage (Google Drive). Only code, config, scripts and text go in git.
- **Honesty:** do not claim an integration works until it has been run and verified.
  Mark anything untested as `UNTESTED`. Do not invent view counts or analytics.
- **Originality:** learn patterns from competitors; never copy their scripts,
  characters, footage, or distinctive storylines.
- **Permanent changes:** when the owner approves a permanent change, update the
  relevant `config/` file, add a dated line to `state/decisions.md`, and commit.

## Layout

- `.claude/skills/twist-villa-studio/` — the Skill (workflow + reference guides)
- `config/` — approved channel, storytelling, provider, and budget settings
- `research/` — competitor and tool research with source links
- `state/` — status, pending tasks, decisions log, spend ledger
- `projects/<slug>/` — per-video text assets (idea, script, bible, storyboard, metadata)
- `studio/` — Python pipeline (`python -m studio --help`)
- `media/` — large generated files (git-ignored)
