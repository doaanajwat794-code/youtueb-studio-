# Shot-prompt guide — vertical Shorts (Veo 3.1, 9:16)

## Prompt anatomy (assembled by `studio/produce.py` in this order)
1. **Action**: one subject, one verb, one moment.
2. **Camera**: lens, move, height, and **vertical framing** ("vertical 9:16 frame, face in upper third").
3. **Character lock**: pasted from `bible.yaml` (never paraphrase it).
4. **Location lock**: pasted from `bible.yaml`.
5. **Style lock**: the Twist Villa look (`look.style_lock`).
6. **Negative prompt**: `look.negative` (text, watermarks, extra fingers …).

## Vertical composition rules
- Put the subject in the upper two-thirds; keep the bottom 25 % simple (captions and UI live there).
- Prefer close-ups and medium close-ups; wides only as tall compositions (corridors, stairwells,
  towers, doorways, elevator shafts).
- Vertical camera moves read well: tilt-up reveals, crane-downs, top-down shots.

## Continuity rules
- Same wardrobe, props, and light direction in every shot; restate them even when "obvious".
- Pass reference images (character sheet + location plate) on every shot that shows them.
- Keep screen direction consistent.
- The hook shot and the echo shot use the **same framing** (not the same footage) so the loop lands.

## Lean into AI strengths
Atmosphere, slow push-ins, light changes, reflections, screens glowing on faces, hands on
objects, silhouettes, weather, micro-expressions without speech.

## Avoid or disguise
Lip-synced dialogue, readable text or numbers (put key text in the captions or narration
instead), fast action, crowds interacting, complex hand choreography.

## Templates
- **Hook:** "Extreme close-up, vertical 9:16: {impossible detail}, {one moving element}. Camera: slow push-in. {locks}"
- **Rule:** "Medium shot, vertical: {character} {routine action} in {location}, {light}. Camera: gentle handheld. {locks}"
- **Clue insert:** "Macro shot: {object} with {subtle anomaly}. Camera: rack focus. {locks}"
- **Twist:** "Close-up, vertical: {character} {realisation expression}; {light change}. Camera: slow push to the eyes. {locks}"
- **Echo:** "Same framing as the hook: {hook image, now re-contextualised}. Camera: static, then cut to black."
