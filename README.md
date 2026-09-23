# Twist Villa Studio

The production studio for the YouTube channel **[Twist Villa](https://www.youtube.com/@TwistVela)**:
original long-form (15–30 min) AI-made sci-fi, mystery and psychological-thriller films.

## How to use it (no coding needed)
Open this repository in Claude Code and say what you want, for example:
- "Continue where we left off."
- "Give me three new story ideas."
- "What will the next video cost?"

Claude loads the `twist-villa-studio` skill and the saved files automatically, so you
never have to re-explain the channel.

## What is where
| Folder | Contents |
|---|---|
| `config/` | Approved channel direction, story framework, tools, budget |
| `research/` | Competitor and tool research with source links |
| `state/` | Current status, next task, decisions, spending ledger |
| `projects/` | One folder per video: idea, script, bible, storyboard, metadata |
| `studio/` | The pipeline code (`python -m studio --help`) |
| `media/` | Generated video/audio (not in GitHub — copy finished files to Google Drive) |

## Safety rules built into the code
- No paid API call without your recorded approval, and hard spending caps.
- Uploads are always **private**; publishing needs your explicit approval.
- Keys and tokens live in `.env` / cloud secrets, never in GitHub.

## Developer quick start
```bash
pip install -r requirements.txt
python -m studio selftest      # free offline test of editing + budget guard
python -m studio status
```
