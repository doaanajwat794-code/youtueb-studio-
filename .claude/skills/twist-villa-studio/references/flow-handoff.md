# Owner guide: Google Flow → Twist Villa hand-off

This is the owner's part of every Short: about 45–90 minutes in Flow. Claude does everything else.

## 1. Before you start
- Open `projects/<slug>/flow-prompts.md` (Claude sends it or shows it in the chat).
- In Flow, create a project named after the Short, e.g. `FNR - Face Not Recognized`.
- Check your credit balance. The prompt sheet shows the estimated credits for this Short.

## 2. Reference images (once per Short, about 5 minutes)
- In Flow, generate each image under **Step 1** of the prompt sheet (the character from the
  front, three-quarter view and full body; each location).
- Keep the best one of each and **rename it exactly** as shown, e.g. `FNR_REF_ELISE_FRONT.png`.
- These become the *Ingredients* for the clips: the same face and clothes every time.

## 3. Clips (in order)
For each shot in **Step 2**:
1. Mode: as listed (usually **Ingredients to Video**). Add the listed ingredient images.
2. Settings: **Portrait 9:16**, **8 seconds**, **1 output**, model as listed (⭐ = Quality, otherwise Fast).
3. Paste the prompt from the grey box **exactly as written**.
4. Watch the result. Tick the checklist: same face and clothes? vertical? no warped hands or
   text? real movement? If not, generate again. That's a new take: `v2`, `v3` …
5. **Download** at the highest resolution Flow offers (1080p if available).
6. **Rename**: `CODE_SNN_vN.mp4`, e.g. `FNR_S03_v2.mp4`. (S = shot number, v = take number.)

Tip: you can send several takes of the same shot. Claude uses the highest take number unless
you say "use S03 v1".

## 4. Hand the clips to Claude (choose one)
| Option | How | Notes |
|---|---|---|
| **A. Local folder (owner's approved method)** | Claude Code on your Windows PC; drop files in `media/<CODE>/incoming/` (see `windows-local-setup.md`). | Most reliable: no upload, no key, nothing public. |
| B. Google Drive folder (**not used**: the owner declined public sharing) | Upload all clips to a Drive folder, e.g. `Twist Villa/FNR/clips` → Share → *Anyone with the link: Viewer* → paste the folder link in the chat. Claude runs `fetch-drive`. | Needs a free `GOOGLE_API_KEY` with the Drive API enabled (one-time setup). Set the folder back to *Restricted* afterwards. **UNTESTED until the first real hand-off.** |
| C. Attach in the chat | Drag the files into the message. | Works only if the app accepts video attachments; large clips may fail. |

## 5. Narration (Google voice only if free)
- **Option 0: Google Vids AI voiceover (preferred).** Paste `voice-<speaker>.txt`, download,
  name it `CODE_VOICE_<SPEAKER>_v1.mp4`, and put it in `incoming/`. It's imported automatically.
- **Option 1: ShortsFaceless voice.** Paste the text from `projects/<slug>/voice-<speaker>.txt` as a
  Custom Script, choose the voice, **turn off background music if possible**, download, and
  hand it over like the clips. Name it `CODE_VOICE_<SPEAKER>_v1.mp4`. (Uses 1 of your 30 monthly videos.)
- **Option 2: Gemini free tier.** Needs a free Google AI Studio key (no billing) and the owner's OK; Claude generates it.
- **Option 3: your own voice.** Record the text on your phone, with a short pause between lines.

Claude then splits the recording into lines and syncs it to the shots (`import-voice`).

## 6. What Claude does next
Import and check the clips → narration → music and sound effects → captions → export
1080x1920 MP4 → title, description, hashtags, cover → private upload (only after your OK).
