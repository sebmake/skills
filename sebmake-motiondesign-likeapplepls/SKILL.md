---
name: sebmake-motiondesign-likeapplepls
description: "Says what to animate and how, element by element (title, list, number, logo, product, screenshot, camera, transitions), from motion measured frame by frame in 8 Apple keynotes, then writes and runs the After Effects or EffectCraft script. It also builds a feature video, or a UI one-take taken apart into readable layers (camera, halos, cursor, voice, subtitles), reads it back and carries hand edits into the source. Use it whenever someone wants Apple-style motion design or keynote-style animation, asks to animate a title, a logo or a UI screenshot 'like Apple', wants a feature video or a narrated UI walkthrough, wants to understand or rework an animation layer by layer, wants an After Effects, EffectCraft or ExtendScript script or asks which easing or duration to use, even without the word Apple. Not for slide decks (sebmake-keynote-likeapple-pls), not for a product film rendered with HyperFrames (sebmake-videopresentation-likeapplepls)."
---

# Keynote-style motion design

This skill does three things, in this order:

1. It says **what to animate and how** for each element of a motion design video: which property, which recipe, which duration, which curve, which amplitude, at what moment, and what not to do.
2. It **writes the script** that builds the animation in After Effects or EffectCraft, and runs it when it can.
3. It **leaves a project you can understand and take over**. Each mechanism has its own layer, named by its role. The skill shows how the scene is built (layer map, screenshot of the tool, comparison). It reads it back in numbers (composition probe, render measurement). It carries hand edits back into the source. You keep working in the tool, round after round.

The values come from four frame-by-frame analyses of 8 keynotes (2019 to 2026): 145 texts, 122 object moves, 189 screen moves, 182 transitions. Each rule carries its count ("N out of M"). What is not measured is marked **convention**. The skill takes the **grammar** of the motion, never the **brand**: colors, fonts, images, logos and text belong to the user.

Scope: motion design video (moving text, products, screenshots, logos). This includes the **UI one-take** (one window, a camera that moves from one element to the next, halos, cursor, voice and subtitles: the **scene breakdown**, `references/scene-demontee.md`). It also includes the **feature video**, which presents a software product through its UI components, its verbs and shapes that play (`references/film-fonctionnalites.md`). Not slides. Not app animation (its transitions, its micro-interactions): a screenshot is animated as an image in the film.

Everything starts from one file: `motion.json` for an element animation, `scene.json` for a scene breakdown. The engine turns it into an ExtendScript (ES3) script that runs in both tools. Always fix the `.json`, never the `.jsx`: the script is rewritten on every build. A hand edit made in the tool is read back (`sonde_ec.py`) and carried into the `.json`.

```bash
SKILL="<folder of this SKILL.md>"   # often ~/.claude/skills/sebmake-motiondesign-likeapplepls
```

Requirements: Node, Python 3.9 or later, ffmpeg and ffprobe. After Effects, or EffectCraft launched with its control channel. If one is missing, say so: the skill can go as far as a checked script with no tool installed. Install nothing without consent.

## Step 1 — Intake

Reread the request and the attachments. Don't ask again for anything already said.

Ask the missing questions with the AskUserQuestion tool if it exists, otherwise in plain text, in a single message. **At most 4 questions per call**, at most 4 choices per question (plus "Other").

| Question | Choices | Why |
|---|---|---|
| What kind of video? | an element animation (titles, product, screenshots); a feature video for a software product (verbs + UI components + shapes); a UI one-take or a narrated demo (window, camera, halos, cursor, voice, subtitles); an existing animation to take apart, understand and rework | The second kind has its own guide (`film-fonctionnalites.md`, intake in § 7). The last two have theirs (`scene-demontee.md`, format in § 2). |
| Which elements should move? (multiple choice) | text (title, sentence, list, number); a product image; screenshots; an end logo (icons, shapes, background: under "Other") | Each type has its recipes (`elements.md` § 1). |
| In which tool? | After Effects; EffectCraft; both | The script is the same; only the run changes (`outils.md`). |
| Format and duration | 16:9, duration from the plan (recommended); 16:9, fixed duration (state it); 9:16 vertical; 1:1 square | The corpus is 16:9. 9:16 and 1:1 are conventions (same values in u). |
| Look | a link to my design system; my HEX colors and my fonts; neutral values for now | The skill does not know the user's identity. |

**Then the brief, in plain text**, with only the lines still unanswered:

```
Text: [the exact text of each title, sentence, list, label]
Numbers: [value] · [what it counts] · [source]        (none if you have none)
Files: [path of each image: cut-out product, screenshots, logo]
Order: [what comes first, what closes]                 (optional)
```

For a **UI one-take**, the brief is the one in `scene-demontee.md` § 2: the window alone (screenshot or video, no camera, no larger than the composition; ×2 and the `16:9-4k` format to zoom sharply), the elements to show in order with their rectangle in the screenshot, the voice (files, or the sentences to be spoken) and the subtitles, the music and its rights. To **take apart an existing animation**, you need the window rendered alone and the trajectories (camera keys, cursor points, halo rectangles, times), read from its source.

**Voice-over.** If the user has voice files, use them. If not, the skill can make them:

```bash
python3 "$SKILL/scripts/voix.py" etat                       # is edge-tts there?
```

- **edge-tts missing**: recommend it, in a question (AskUserQuestion): "For better results, do you want to install edge-tts? Natural, free voices (Vivienne, Denise, Henri…), internet required." Choices: install edge-tts (recommended); a macOS voice, robotic, for a draft; I have my own voices; no voice. Only with consent: `python3 -m venv ~/.venv-sebmake-voix && ~/.venv-sebmake-voix/bin/pip install edge-tts`.
- **Text first**: the sentences are the user's, or proposed and marked "to validate". Nothing is spoken before they agree.
- **Audition**: `voix.py audition phrases.txt --voix Vivienne,Denise,Henri,Remy,Eloise --sortie audition/` (for English text: `--voix Ava,Andrew,Emma,Brian`); the user picks by ear.
- **Generation**: `voix.py generer phrases.txt --voix <choice> --sortie voix/` → one file per sentence and `voix/voix.json` (duration, time of each word). The durations place the sentences without overlap. The word times put a move or a click on the word that announces it.
- edge-tts goes through an online Microsoft service, free but unofficial: say so if the film leaves the company. The macOS voice gives no word times.

For a **feature video**, the brief follows `film-fonctionnalites.md` § 7: one line per point, *verb + object* and the component that proves it, then the exports (full screen, cut-out component, two states if it is manipulated), the promise, the sound, the shapes and the background color of each chapter. A point with no component does not hold in the film: say so.

Say what will happen to whatever stays empty: missing text will be proposed and marked "TO VALIDATE"; a missing number will stay `[TO PROVIDE]`; a missing image will be replaced by a neutral placeholder (a frame and its diagonals), at the right format.

**Read the look.** With a link, read it with the session's tools (Figma: `get_variable_defs` and `get_screenshot`, after the Figma skill those tools require; Notion; web page; PDF). Fill the theme roles: `fond`, `texte`, `secondaire`, `accent`, `voile`, `lumiere`. Unreadable link: say so and ask for the HEX values. Colors described without HEX: propose HEX values and have them validated. Never pick a palette the user has not seen. Fonts are written as PostScript names (`Inter-SemiBold`); EffectCraft ships Inter. A manufacturer-specific font (SF, New York…) is rejected by the checker: propose a free sans-serif and say why.

**Prepare the files.** Create a working folder (in the current folder, unless the user names another) with `images/`, and copy their files into it. Size: `ffprobe -v error -show_entries stream=width,height -of csv=p=0 <file>`. Product: cut-out PNG, large enough for the push-in (×1.27 on average). Screenshots: native resolution or ×2, no personal data (blur it or ask for a demo screenshot). Logo: theirs only. For an exploded view: one image per piece, same framing.

## Step 2 — The animation plan, before any script

Read `references/principes.md` (once per conversation). Then, in `references/elements.md`, read the guide for each requested element type, and § 17 for the order of a sequence. For a feature video, also read `references/film-fonctionnalites.md`: the film's order (§ 2), the verb (§ 3), the component lifted out of the screen (§ 4), the shapes (§ 5), the background per chapter (§ 6). Its values are conventions taken from two films: write that in the plan.

**For a film (not for a single element), three concepts first.** Propose three central ideas that differ in the image, not in the order of screens (`scene-demontee.md` § 5). For each one: the hook image, what carries from one beat to the next, what it forbids itself, and whether the film **cuts** (keynote grammar, P1) or **holds in one take**. The user chooses; the plan follows that choice.

For each element, choose:
- **what to animate**: the property (opacity, position, scale, Y rotation, light, parent camera); often nothing ("coupe");
- **the recipe** from the engine, for the chosen era (`2024-2026` by default, `2019-2020` for a calmer look on screens and a more playful one on numbers);
- **the moment**: cut on the empty background, entrance, what follows (`avec`, label, `puis`), hold, exit by cut;
- **what you leave out**, and why.

Show the plan **before** writing `motion.json`, as a table, one row per element or per gesture:

| # | Element | From → to | What to animate | Recipe | Duration, curve, amplitude | What carries over | Why (count) |
|---|---|---|---|---|---|---|---|
| 1 | title | 0.1 → 3.0 s | opacity, then Y position | `titre-fondu-montee` | fade 0.77 s `easeInOutCubic`; rise 15.3 u, 0.92 s `easeOutExpo`, 0.30 s later | — (cut to the product) | identical to the hundredth in 3 titles out of 4 |
| 2 | kicker | with the title | nothing of its own | `avec` | — | — | arrives with its word, 8 out of 11 |
| 3 | product | 3.0 → 6.4 s | X position; parent camera | `produit-entree` + `camera-poussee` | 0.9 s `out-cubic`, motion blur 120°; ×1.05 linear | the camera pushes in to the next detail | brakes 8 out of 8; linear push-ins 7 out of 11 |

The **what carries over** column says, at each change of beat, what survives and moves to reach the next one (the camera, the cursor, a component that becomes the next screen), or "cut". In a film that cuts, most rows say "cut": that is the grammar. In a one-take, a "cut" row is a slide and must be justified.

For a **scene breakdown**, the plan has one row per framing: time, what we look at, the camera arrival (`pose`, `suit`, `fouette`, `lineaire`, `coupe`: `scene-demontee.md` § 3), the zoom, the halo and the click, the spoken sentence, what carries over.

Add at most three lines below it: the era, the palette and fonts; the conventions taken (9:16, object drift, blur value…); what is missing (text to validate, numbers, images). Wait for agreement. Changing a row of the plan costs a minute. Redoing a script and its check frames costs much more.

A question without a script ("how do I animate this logo?") stops here: give the plan, the recipe, the values and the curve as After Effects keys (`references/courbes.md`), and offer to write the script.

## Step 3 — `motion.json` and the check

Read `references/motion-spec.md`, then look at `assets/exemple-motion.json` for the level of detail (it is fictional: don't reuse its content).

Write `motion.json` in the working folder: `comp` (name, format, frame rate, duration, era), `theme`, `elements` from back to front, `transitions`. Keep the recipes' default values. Put in `options` only what the validated plan changes. Proposed text carries "TO VALIDATE" in your reply, not in the image. A number not provided is written `"[TO PROVIDE]"`, with `"source": "[TO PROVIDE]"`.

```bash
python3 "$SKILL/scripts/check_motion.py" motion.json
```

- **Zero errors before building.** A measured option outside its range, two major moves that overlap, an animated exit, a downward sweep, a scrim that goes to black, a vertical slide, a number without a source: fix `motion.json` and run again. Text that does not fit in its time gets shorter or stays longer; it is not shrunk.
- Each warning is fixed, or kept knowingly and stated at delivery. Expected and acceptable: a `[TO PROVIDE]`, a missing image (placeholder), a convention chosen in the plan.
- `"simultane": true` lifts the ban on two major moves at once: only if the validated plan asks for it, and say so.

## Step 4 — The script

```bash
node "$SKILL/scripts/build_motion.mjs" motion.json                  # writes motion.jsx and checks ES3
node "$SKILL/scripts/build_motion.mjs" motion.json --prefixe TEST-  # for a test run in EffectCraft
```

The script is ExtendScript ES3 (no `let`, no `const`, no arrow function, no template literal, no `JSON`) and uses only the After Effects object API. The generator checks it. An ES3 issue (exit code 2) is an engine bug: report it. At the top of the script: the recipes, the curves and their translation into keys. Each recipe sets a layer marker that states its recipe, curve and duration. To share with another machine: `--relatif`, and the images next to the script.

A gesture no recipe covers (a path that draws itself, an icon that grows under a spotlight): propose it in the plan as a convention, then write it in a second short script, with the function in `references/courbes.md` § 7. Don't modify the engine.

## Step 4b — The scene breakdown (instead of steps 3 and 4)

For a UI one-take or an animation to take apart, instead of steps 3 and 4: read `references/scene-demontee.md`, write `scene.json`, then

```bash
python3 "$SKILL/scripts/scene_ec.py" scene.json --prefixe TEST-          # writes scene.jsx and runs it in EffectCraft
python3 "$SKILL/scripts/scene_ec.py" scene.json --jsx-seul               # for After Effects: the script only
```

The script rejects a window larger than the composition, camera keys out of order, and a missing file. A long demo is made as one scene per chapter, edited together afterwards (step 6).

## Step 5 — Run and check frames

Read `references/outils.md`.

**EffectCraft** (on this machine):

```bash
python3 "$SKILL/scripts/ec.py" activer                     # the app only answers when in front
python3 "$SKILL/scripts/ec.py" script motion.jsx
python3 "$SKILL/scripts/ec.py" frames "<comp.nom>" controle/ --pas 0.5 --max 640
ffmpeg -v error -y -pattern_type glob -i 'controle/t*.png' -vf "scale=480:-1,tile=6x7:padding=4" -frames:v 1 planche.jpg
python3 "$SKILL/scripts/ec.py" render "<comp.nom>" rendus/motion.mp4     # if a render is requested
```

Launch EffectCraft with `open -a EffectCraft --args --control 9877` if it is not listening (exit code 3). Never save, open or close its project: `ec.py` refuses without `--autoriser`, and only the user can ask for it. A test run happens in a `TEST-` composition.

**After Effects**: the user runs the script (**File > Scripts > Run Script File…**). Give them the steps in `outils.md` § 2. To see the result, ask them for an MP4 and make a contact sheet from it (`outils.md` § 5). After Effects was not used to test the skill: say so, and ask for the message and line of any error. If EffectCraft is installed, offer a test pass in a `TEST-` composition for the check frames, with their consent.

**Read the composition and the render back in numbers** (`scene-demontee.md` § 6), for a scene breakdown as for a film:

```bash
python3 "$SKILL/scripts/sonde_ec.py" "<comp.nom>" --cadre "Cursor,Halo" --carte carte.md   # map, boundaries, speed, frame
python3 "$SKILL/scripts/mesure_rendu.py" rendus/motion.mp4 [--ref reference.mp4]          # energy, rest, cuts, sound
```

Each issue is fixed in the `.json` or kept and stated: a watched layer out of frame, travel over 80 px per frame without motion blur (`camera.flou_de_bouge`, or the recipe's motion blur), a carry-over score under 0.5 in a one-take, no rest.

**Look at the frames yourself** before showing them (image reading tool). Check:
- each text whole, readable, with no box behind it; the background empty for a moment after each cut;
- only one major move at a time; the label after its number; a camera that does not roll;
- no overshoot, no bounce, nothing floating in a loop, no number counting up;
- placeholders and `[TO PROVIDE]` visible; nothing that recalls a brand (no device, font, logo or signature).

To judge a curve, extract the move at full frame rate and look at the frames in sequence (`outils.md` § 5). A defect: fix `motion.json`, then redo steps 3 to 5.

## Step 6 — Show the mechanics, then keep going

The user must be able to **understand how the scene is built** and take it over. Show them, in this order:

1. the **tool screenshot**, composition open (`ec.py capture capture.png "<comp.nom>"`);
2. the **map** from `sonde_ec.py`: each layer, its role, its parent, what is animated. Then explain the mechanics in a few lines (for a scene breakdown: the window's anchor and scale are the camera; halos and cursor are its children; subtitles and title card stay fixed; each voice sits at its time);
3. a **comparison**: a frame of the render next to a frame of the reference (or of the intent) at the same time, and the gaps that remain.

Then **the loop goes on** (`scene-demontee.md` § 7): the user edits by hand in the tool or asks for a change; you run `sonde_ec.py` again, say what changed, carry the edit into the `.json`, rebuild, and measure again. Nothing the user did by hand may be lost on the next pass.

**Keep the project**, only when asked: `python3 "$SKILL/scripts/ec.py" --autoriser garder <folder>/<name>.ecproj` (a new file, never over an existing one). Rendered scenes are then edited into a film with `sebmake-videoedit-like-applepls` (composed edit: picture, voice, music ducked under the voice, subtitles, sounds).

## Step 7 — Delivery

Deliver in one short message:

1. **the files**: the `.jsx` script (path), the MP4 render if any (path, duration, format), the source `.json`, the contact sheet, the map and the tool screenshot, the saved project if asked for;
2. **how to run it**: the `ec.py` command, or the After Effects menu, in one line;
3. **to validate**: the proposed text, one item at a time;
4. **to provide**: the `[TO PROVIDE]` items (numbers with their source), the images replaced by a placeholder, with what they must show and their format (cut-out PNG, native screenshot ×2, one image per piece);
5. in one line: the conventions taken and the warnings kept; "not tested in After Effects" if that is the tool;
6. for what comes next: edit `motion.json` and rebuild. A hand edit in the `.jsx` or in the composition is lost on the next script run.

## Reminders

- **The principles are measured.** Only state a duration, curve or amplitude if it is in the references, with its count. What is not measured is called "convention".
- **No invented numbers**, dates, reviews, quotes or client logos. What is missing stays visible: `[TO PROVIDE]`.
- **The grammar, never the brand.** No Apple image, font, logo or signature, no recognizable device (a floating panel with rounded corners replaces a device frame), no keynote quote, even translated.
- **What does not exist in the corpus is not animated**: counting numbers, bounce, typewriter, word by word, rotating text, full spin, sine-wave floating, animated exit, vertical screen slide, box behind text (counts in `principes.md` § 13).
- **ES3 for After Effects**: `var` and `function` only. A hand-written script follows the same rule.
- **The user's project belongs to them**: the script adds or replaces one composition (with the solids only it used), nothing else; no open or close. A save only when asked, in a new file (`ec.py garder`).
- **Sound.** The corpus is silent: syncing a move to music is a convention. The scene breakdown places the user's voices, sounds and music (which they hold the rights to) at their times. A synthetic voice only with agreement on the engine, the text and the voice (`voix.py`); no music searched for or made.
- **A hand edit is never lost**: read by the probe, carried into the `.json`, told to the user.

## Reference files: when to read them

| File | When |
|---|---|
| `references/principes.md` | Step 2, once: the 12 principles, their counts and their reason; § 13 before refusing a gesture ("what is never animated"); § 14 for conventions. |
| `references/elements.md` | Step 2: the guide for each requested element type (§ 2 to § 16), the quick choice (§ 1), the order of a sequence (§ 17). Also to answer "how do I animate this element". |
| `references/film-fonctionnalites.md` | Step 1 (§ 7: its own intake) and step 2, for a film that presents a software product through its features: three materials (verb, component, shape), film order, component lifted out of the screen, background per chapter; two films studied, values are conventions. |
| `references/scene-demontee.md` | Step 1 (one-take or animation to take apart: brief in § 2); step 2 (three concepts and what carries over, § 5; camera, § 3; readability, § 4); step 4b (format); steps 5 and 6 (benchmarks § 6, ongoing loop § 7, pitfalls § 8). |
| `references/courbes.md` | Step 2, to give a curve as After Effects keys; step 4, for a gesture outside the recipes (§ 7); when in doubt about a curve name (§ 3.3). |
| `references/motion-spec.md` | Step 3, before writing `motion.json`; to understand a checker error (§ 7) or the shape of the script (§ 9). |
| `references/outils.md` | Step 5: run in After Effects (§ 2) or EffectCraft (§ 3); a symptom and its fix (§ 4); contact sheet and render check (§ 5). |
| `assets/exemple-motion.json`, `assets/exemple-motion.jsx` | Step 3: a complete 20 s animation (fictional) and the script it produces; neutral images in `assets/exemple/`. |
| `scripts/check_motion.py` | Step 3: the check (Python 3.9, no dependencies). |
| `scripts/build_motion.mjs`, `scripts/motion_lib.mjs` | Step 4: script generation; `--liste` lists the recipes and their counts. |
| `scripts/ec.py` | Step 5: client for EffectCraft's control channel (Python 3.9, no dependencies); `capture` (step 6), `garder` (on request). |
| `scripts/scene_ec.py` | Step 4b: `scene.json` → scene breakdown, run in EffectCraft. |
| `scripts/sonde_ec.py` | Steps 5 and 6: reads the open composition → layer map, boundaries and carry-over score, speeds, frame. |
| `scripts/voix.py` | Step 1: synthetic voice-over (edge-tts recommended, macOS `say` as fallback): status, audition, generation with word times. |
| `scripts/mesure_rendu.py` | Step 5: reads an MP4 → energy map, rest, cuts, bursts, shots, sound; `--ref` for a reference. |
