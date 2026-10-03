# Episode 4 — THE CROWN DUEL (series finale)

**Rajan (white tiger, twin sabres) vs the masked Reigning Champion (one obsidian sword).** Rajan wins.
The mask cracks and falls: the Champion is **Kharun, an old silverback gorilla**, "The Last King".
Kharun is built as a full Flow Character so he can carry a future season.

## Format (owner 2026-10-03)
- **5 clips, not 12.** Each clip is one continuous 8 s shot (8 s is Veo's maximum, not 10) with
  timestamped beats, so the fight flows without stacked cuts. 40 s raw → edit to **32–36 s**.
- Each clip ends in the pose the next one starts from, so the joins feel like one fight.
- Credits: 5 × 20 = **100** (Veo 3.1 Fast). Images (Kharun, the reveal last frame) are free.

Mask stays on for the whole fight and comes off only after he loses (owner + Claude 2026-10-03): the
mystery is the series' hook since E03 ("WHO IS BEHIND THE MASK?"), and he removes it himself, by choice.

## Beats
| Clip | 0–8 s, one continuous shot | Line |
|---|---|---|
| C01 | Drops from the balcony, floor cracks; overhead smash caught on crossed sabres; Rajan's spin double-slash parried; elbow to the chest | Champion: "Kneel, tiger." |
| C02 | Three-strike combo (thrust sparks on the breastplate); low sweep, backflip; grabs Rajan's ankle mid-air and slams him into the snow; Rajan springs up | — |
| C03 | Sprint, spinning leap, double-sabre crash (floor cracks); six-strike flurry; back-kick | Rajan: "I kneel to no one." |
| C04 | Overhead strike misses into the stone; Rajan stamps the blade, disarms; 360° slash cracks the mask; kneel; sabres crossed at the throat; crowd silent | — |
| C05 | He rips the cracked mask off himself → silverback gorilla Kharun; looks up | Kharun: "Finally... a worthy king." |

## Steps for the owner
1. Rajan: update the Flow Character body with **Rajan BODY v2 (full armour)** from `character-prompts.md`.
2. Kharun: make portrait + body in Nano Banana 2 → new Flow Character "Kharun" (prompts in `character-prompts.md` 5b).
3. C01–C04 in Ingredients mode (Rajan + Champion + arena) from `E04_PROMPTS.txt`. Send them to Claude.
4. Claude reviews, then sends `CT_E04_C05_FIRST.png` (the last frame of C04).
5. Nano Banana 2 edit of that frame, with Kharun as the reference image:
   "Keep everything identical (pose, armour, cloak, snow, light, Rajan behind him). Replace the cracked
   obsidian mask with the face of the silverback gorilla from the reference image, looking up; the two
   halves of the black mask lie in the snow in front of him." → save as `CT_E04_C05_LAST.png`.
6. C05 in Frames to Video with FIRST + LAST frames. (UNTESTED: if Fast does not offer a last frame,
   use Ingredients: Rajan + Kharun + arena with the same prompt.)

## Edit plan (Claude)
- **Cold-open hook (1 s):** the glowing crack across the mask (C04) + text "NO ONE HAS SEEN HIS FACE…"
  → "THE CROWN DUEL".
- Clips play almost whole (pads trimmed, speed ramps on the impacts); 4 joins with transitions.
- Name cards: RAJAN · THE CRIMSON CLAW / ??? · THE REIGNING CHAMPION.
- Ending: score cuts to silence on the mask split; Kharun's line; cards "KHARUN · THE LAST KING",
  "RAJAN · KING OF AURUMVALE", then "THE END… ?" (season-2 hook).
