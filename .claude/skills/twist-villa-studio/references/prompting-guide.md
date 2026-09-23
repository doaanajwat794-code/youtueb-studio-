# Shot-prompt guide (Veo 3.1 / image models)

## Prompt anatomy (the pipeline assembles it in this order)
1. **Action** — one subject, one verb, one moment: "Mara lowers the flashlight as the
   corridor lights flicker on one by one."
2. **Camera** — lens + move + height: "slow dolly-in, 35mm, eye level".
3. **Character lock** — pasted from `bible.yaml` (never paraphrase it).
4. **Location lock** — pasted from `bible.yaml`.
5. **Style lock** — the Twist Villa look from `bible.yaml` → `look.style_lock`.
6. **Negative prompt** — `look.negative`.

## Continuity rules
- Same wardrobe/props/light direction within a scene; state them in the prompt
  even if "obvious".
- Pass reference images (character sheet + location plate) on every shot that shows
  them — max 3 per shot.
- Keep screen direction consistent (who is left/right; which way they walk).
- For a cut within a continuous action, generate the second shot from the last frame
  of the first (first-frame image) when possible.

## What AI video does well (lean in)
Atmosphere, slow camera moves, environments, silhouettes, hands on objects, screens,
reflections, weather, light changes, crowds at distance, close-ups without speech.

## What to avoid or disguise
Long lip-synced dialogue, fast fights, complex hand choreography, readable text,
many characters interacting, exact repeated props across many shots.
→ Use V.O., over-the-shoulder, cutaways, inserts, and screens instead.

## Templates
- **Establishing:** "Wide establishing shot of {location}, {time/weather}, {one moving
  element}. Camera: slow crane down."
- **Emotional close-up (hero):** "Close-up of {character}, {micro-expression}, {light
  change on face}. Camera: static, 85mm, shallow focus."
- **Clue insert:** "Extreme close-up of {object detail}, {subtle anomaly}. Camera: slow
  rack focus from foreground to detail."
- **Reveal:** "{character} turns toward {thing}; {light/sound motivated change}.
  Camera: slow push-in ending on the eyes."
