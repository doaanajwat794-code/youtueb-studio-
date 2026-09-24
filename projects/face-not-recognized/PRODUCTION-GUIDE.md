# Face Not Recognized: your production guide

Your part: **make 5 reference images and 11 clips in Google Flow, download them, rename them, and put
them in one folder.** Optional: 2 voice recordings and 2 music tracks. Claude does everything else.

The copy-paste prompts are in **`flow-prompts.md`** (same folder).
Settings for every clip: **Veo 3.1 Fast · Portrait 9:16 · 8 seconds · 1 output**. Never use Quality.

---

## 0. First, check your Flow account (5 minutes, no credits)
Claude can't see your Flow account, so please check and tell me:
1. Can you choose **Portrait / 9:16** together with **Veo 3.1 Fast**?
2. Do you see **Ingredients to Video** (add up to 3 reference images to a video prompt)?
3. Can Flow **create images** (for the reference portraits), and does that cost credits?
4. How many **credits** does one Fast 8-second clip show before you click Generate, and what's your balance?
5. When you download a clip, which sizes are offered (for example 720p / 1080p), and does 1080p cost credits?

If something is missing, tell me. I'll adapt the prompts (for example, text-only prompts instead of Ingredients).

## 1. Reference images (Step 1 in `flow-prompts.md`)
Make these 5 images and keep the best of each (generate again until the face looks right):

| File name | What it is |
|---|---|
| `FNR_REF_ELISE_YOUNG_FRONT.png` | Elise at 37, front portrait (the most important image) |
| `FNR_REF_ELISE_YOUNG_THREE-QUARTER.png` | Elise at 37, three-quarter view (backup) |
| `FNR_REF_ELISE_OLD_FRONT.png` | Elise at 67: must be the **same woman**. If you can add a reference image, add the young portrait first |
| `FNR_REF_THEO_FRONT.png` | Theo, her son, 42 |
| `FNR_REF_CORRIDOR.png` | The corridor, no people |

**Same-person check (young vs old Elise):** the mole above the left corner of the lip, the nose bump,
grey-green eyes, left hair parting, cream cable-knit turtleneck, silver hoops, gold ring.
Save the images in `media\FNR\incoming\` too. Claude uses them to check the clips.

**How to reuse them:** in every clip, add the images listed under "Ingredients" in `flow-prompts.md`.
Use the **same** image files every time. Don't regenerate a reference halfway through the project.

## 2. The 11 clips
| Shot | Time in the film | Ingredients to add | Save as |
|---|---|---|---|
| S01 hook | 0.0–4.5 s | ELISE_YOUNG_FRONT + CORRIDOR | `FNR_S01_v1.mp4` |
| S02 door | 4.5–10.0 s | ELISE_YOUNG_FRONT + CORRIDOR | `FNR_S02_v1.mp4` |
| S03 panel | 10.0–15.0 s | ELISE_YOUNG_FRONT + CORRIDOR | `FNR_S03_v1.mp4` |
| S04 eye | 15.0–20.0 s | ELISE_YOUNG_FRONT + CORRIDOR | `FNR_S04_v1.mp4` |
| S05 mirror | 20.0–24.0 s | ELISE_YOUNG_FRONT + CORRIDOR | `FNR_S05_v1.mp4` |
| S06 mirror flash | 24.0–25.0 s | ELISE_OLD_FRONT + CORRIDOR | `FNR_S06_v1.mp4` |
| S07 reaction | 25.0–29.0 s | ELISE_YOUNG_FRONT + CORRIDOR | `FNR_S07_v1.mp4` |
| S08 elevator | 29.0–35.0 s | ELISE_YOUNG_FRONT + THEO_FRONT + CORRIDOR | `FNR_S08_v1.mp4` |
| S09 twist | 35.0–42.5 s | ELISE_OLD_FRONT + THEO_FRONT + CORRIDOR | `FNR_S09_v1.mp4` |
| S10 realisation | 42.5–50.0 s | ELISE_OLD_FRONT + CORRIDOR | `FNR_S10_v1.mp4` |
| S11 echo | 50.0–57.6 s | ELISE_YOUNG_FRONT + CORRIDOR | `FNR_S11_v1.mp4` |

**For each shot:**
1. Choose **Ingredients to Video** (or what your account offers, see step 0) and add the ingredient images.
2. Settings: **Veo 3.1 Fast**, **Portrait 9:16**, **8 s**, **1 output**.
3. Copy the whole grey prompt box for that shot from `flow-prompts.md` and paste it.
4. Check the result against the tick-list under the prompt. If it fails, generate again (that's take `v2`).
5. **Download:** open the clip, click the download icon, choose the largest size that doesn't cost extra credits.
6. **Rename** in Windows: click the file in Downloads → press **F2** → type e.g. `FNR_S03_v2.mp4` → Enter.
   `S` = shot number (always two digits), `v` = take number. Keep all takes; Claude uses the highest
   take unless you say "use S03 v1".

Tips: generate in order (S01 → S11). If a face drifts, regenerate with the same prompt first. Change
only one thing at a time.

## 3. Voices (free Google voice first)
Claude wrote two voice scripts in this folder: **`voice-narrator.txt`** (Elise, 8 short lines) and
**`voice-theo.txt`** (Theo, 2 lines). Keep the blank lines: they become the pauses Claude uses to split the lines.

**Option A: Google Vids AI voiceover (Google voice, no API, no card).** Google Vids offers AI
voiceovers made with Gemini voices, and it can be used with a normal Google account.
*Not yet checked for your account.* If it asks you to pay or upgrade, stop and tell me.
1. Open Google Vids with your Google account and start a blank video.
2. Add an AI voiceover, paste `voice-narrator.txt`, choose a calm female voice
   (direction: warm, intimate, quietly unsettled).
3. Download the video → rename it `FNR_VOICE_NARRATOR_v1.mp4`.
4. Repeat with `voice-theo.txt` and a gentle male voice → `FNR_VOICE_THEO_v1.mp4`.

**Option B: Gemini text-to-speech, free tier** (Claude generates it). Needs a free Google AI Studio
key with **no billing**. On the free tier Google may use the text to improve its products. Rate limits apply,
and the models are in preview. Only if you say yes.

**Not free, so not used:** Google Cloud Text-to-Speech. It needs billing (a card) switched on and charges
automatically above the free monthly amount.

**Free fallbacks:** record the lines yourself on your phone (name them the same way), or use
ShortsFaceless (uses 1 of your 30 monthly videos).

## 4. Music (free)
In **YouTube Studio → Audio library**, filter *Attribution not required* and download:
- a tense, minimal, pulsing track → rename `FNR_MUSIC_M01.mp3`
- a soft, emotional piano track → rename `FNR_MUSIC_M02.mp3`

Note both titles in your message; they go in the description credits.

## 5. Where the files go (the local folder)
Everything (5 reference images, the clips, the voices, the music) goes into **one folder**:

```
TwistVilla\media\FNR\incoming\
```

### Important: why this needs Claude Code on your computer
You're using Claude Code in the cloud (web/app). The cloud computer **can't see files on your PC**,
and it deletes its own files when the session ends. So for the local-folder workflow, you run Claude
Code **on your Windows 11 computer** with a copy of this project. Your project settings, story and
prompts come along automatically, because they're saved in GitHub. Only the video files stay on your PC.

### Windows 11 setup (one time, about 15 minutes)
Open **PowerShell** (Start → type *PowerShell* → open it) and run these one at a time:

1. Install Git: `winget install --id Git.Git -e`
2. Install Python: `winget install --id Python.Python.3.12 -e`
3. Install Claude Code: `irm https://claude.ai/install.ps1 | iex`
4. **Close PowerShell and open it again** (so the new programs are found), then check: `claude --version`
5. Download the project into your Documents folder:
   `cd $HOME\Documents`
   `git clone https://github.com/doaanajwat794-code/youtueb-studio-.git TwistVilla`
   (a GitHub sign-in window may open; sign in with the account that owns the repository)
6. `cd TwistVilla`
7. Install the project's tools: `py -m pip install -r requirements.txt`
8. Start Claude Code: `claude` → sign in with your Claude account → type:
   **"Continue the Twist Villa project: import my Face Not Recognized clips."**

Then open **File Explorer → Documents → TwistVilla → media → FNR → incoming** and drag your renamed
files in. (Claude creates this folder on the first run if it isn't there yet.)

If your Claude desktop app has a built-in Claude Code ("Code") section, you can open the
`TwistVilla` folder there instead of using PowerShell. Not verified for your account.

### Cloud alternative (without your PC)
There's currently **no verified private way** to send large video files into this cloud session.
Making a Drive folder public is off the table (your rule). A private Google Drive download would need
a one-time Google sign-in set up on your computer anyway, so the local workflow above is simpler.

## 6. What Claude does when your files are in the folder
1. `py -m studio import-clips face-not-recognized` checks every clip (vertical? long enough? resolution?
   duplicates?), picks the latest takes, imports music, and splits the voices into lines.
2. Checks frames of every shot for face and clothing continuity, and tells you exactly which shot to redo, if any.
3. `py -m studio make-sfx face-not-recognized` creates the original sound effects.
4. `py -m studio assemble face-not-recognized` edits everything, adds the phone/door text, burns in
   English captions, mixes voice, music and SFX, exports **1080x1920 MP4**, and verifies 55–60 s and A/V sync.
5. Cover image + title/description/hashtags (in `metadata.yaml`) for your approval.
6. **No upload and no publishing** until you say so.

## Flow credits (estimate; your account shows the real numbers)
- 11 Fast clips × about **20 credits** each (web-reported; possibly 10 on Ultra) = about **220 credits**
- With about 30 % retakes: about **300 credits** (about 150 on Ultra)
- Reference images: check in step 0 whether they cost credits
- Claude can't read your Flow balance; please check it in Flow before you start.
