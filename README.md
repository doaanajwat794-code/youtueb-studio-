# Twist Villa Studio

The production studio for the YouTube channel **[Twist Villa](https://www.youtube.com/@TwistVela)**:
original **YouTube Shorts** (55–60 s, vertical 1080x1920): AI-made cinematic mystery,
psychological-thriller and sci-fi stories about identity and technology, each with a final twist.
(The earlier long-form plan is archived in `archive/longform/`.)

**How a Short gets made:** Claude writes the story and a Google Flow prompt sheet → you generate
the clips in Google Flow (your subscription) and hand them over → Claude edits, adds narration,
music, sound and captions, and exports the 1080x1920 MP4. Your step-by-step guide:
`.claude/skills/twist-villa-studio/references/flow-handoff.md`.

## How to use it (no coding needed)
Open this repository in Claude Code and say what you want, for example:
- "Continue where we left off."
- "Give me three new Short ideas."
- "What will the next Short cost?"

Claude loads the `twist-villa-studio` skill and the saved files automatically, so you
never have to re-explain the channel.

## What is where
| Folder | Contents |
|---|---|
| `config/` | Approved channel direction, story framework, tools, budget |
| `research/` | Competitor and tool research with source links |
| `state/` | Current status, next task, decisions, spending ledger |
| `projects/` | One folder per Short: idea, script, bible, storyboard, metadata |
| `archive/longform/` | Inactive long-form research and settings |
| `studio/` | The pipeline code (`python -m studio --help`) |
| `media/` | Generated video/audio (not in GitHub — copy finished files to Google Drive) |

## Safety rules built into the code
- Uses your existing subscriptions (Google Flow, ShortsFaceless); no paid API call without your recorded approval.
- Uploads are always **private**; publishing needs your explicit approval.
- Keys and tokens live in `.env` / cloud secrets, never in GitHub.

## Developer quick start
```bash
pip install -r requirements.txt
python -m studio selftest      # free offline test of editing + budget guard
python -m studio status
```
