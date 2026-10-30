---
name: sebmake-videopresentation-likeapplepls
description: "Makes a voiceless 1-2 minute product film on the grammar of Apple keynote reveal films (hook, build-up, late reveal, name at the end), then cuts it to 15-60 s for social in 16:9, 9:16 and 1:1, rendered as MP4 in the user's colors, over their own music or none. Use it for any product film, launch video, teaser or reveal, anything Apple-style or keynote-style, and for reels, shorts, stories or vertical cuts of a launch, even without the word Apple. Not for slide decks (sebmake-keynote-likeapple-pls), voice-over or presenter videos, or interview edits."
---

# A product film in the style of keynotes

This skill makes two things:

1. a **product film** of 60 to 120 s, in 16:9, built like keynote reveal films: a hook, a build-up, the late reveal of the whole object, then the name as the payoff;
2. its **social cut-downs** of 15 to 60 s, in 16:9 and vertical 9:16 (square 1:1 as an option), **recomposed** for each format, never cropped.

**No voice**, no voice-over and no speech synthesis. Meaning comes from on-screen text and music. The music is a file the user provides and holds the rights to, or there is none. The skill takes the **grammar** observed in 8 keynotes (2019 to 2026), never the **brand**: colors, fonts, visuals, figures and music all belong to the user.

Everything starts from one file, `film.json`. The engine turns it into HyperFrames projects (HTML + GSAP), a review sheet and the MP4s. Always fix `film.json`, never the generated project: `build_film.js` rewrites it on every run. The HyperFrames skills are not needed; `npx hyperframes` is enough.

```bash
SKILL="<folder of this SKILL.md>"   # often ~/.claude/skills/sebmake-videopresentation-likeapplepls
```

Requirements: Node 22 or later with `npx hyperframes` (0.8), ffmpeg and ffprobe, Python 3.9 or later. If one is missing, say so: the skill can go as far as a checked `film.json`, but not to the render. Don't install anything without the user's consent.

## Step 1 — Intake

First reread the request and the attachments. Don't ask again for anything already said.

Ask the missing questions with the AskUserQuestion tool if it exists, otherwise in plain text, grouped in one message. **4 questions at most per call.** The tool only takes 4 choices per question, plus "Other". If the list is longer, offer the 4 most likely and name the others in the question text.

**Call 1: the product and the material.**

| Question | Choices | Why |
|---|---|---|
| What does the film present? | a physical object; software or an app; a service; something else (brand, event) | The film's family depends on it (`grammaire-film.md` § 4). |
| What visuals do you have? (multiple choice) | cut-out product photos (transparent PNG); mood or in-use photos; screenshots or screen recordings; logo | The shot recipes depend on it. With no visuals at all, only a text-only film is possible: say so. |
| Branding | a link to my design system; my HEX colors and my fonts | The skill doesn't know their identity. |
| Music | a file I hold the rights to; no music | There is no third option. |

**Call 2: distribution.**

| Question | Choices | Why |
|---|---|---|
| Audience | B2B decision-makers; general public; investors or partners; internal team | It sets the tone of the cards and the choice of proofs. |
| Where will it be seen? (multiple choice) | website or YouTube (16:9); Reels, Shorts, TikTok, stories (9:16); square LinkedIn or Instagram feed (1:1); trade-show or stage screen (16:9) | It decides the formats. |
| Product film length | 60 s (recommended); 75 s; 90 s; 120 s | No voiceless product film observed runs past 68.5 s. Beyond that, the film is built in chapters and needs more visuals: say so. |
| Cut-downs (multiple choice) | 15 s; 30 s; 45 s; 60 s | The templates in `declinaisons.md` § 3. |

**Then the brief, in plain text.** Give this template to fill in, with only the lines still unanswered. Say what happens to what stays empty: the wording (thesis, ideas, closing line) will be proposed and flagged "to validate"; figures, dates, the call-to-action line, logos and quotes will stay `[TO PROVIDE]`.

```
Product: [the exact name, as it is written on screen]
Message: [the sentence the viewer should remember]
Three proofs: [what the product does best] · [what we can show to prove it]
Figures: [figure] · [basis of comparison] · [source]      (none if you don't have any)
Call-to-action line: [date, address, "coming soon"]      (optional)
Visuals: [paths or attachments]
Music: [file path], and you confirm you hold the rights
```

**Reading the branding.** With a link, read it with the session's tools: Figma (`get_variable_defs`, `get_screenshot`, after the Figma skill those tools require), Notion, a web page, a PDF. Fill the roles in `theme.couleurs`: `fond_sombre` (dark background: a charcoal rather than pure black), `fond_clair` (light background: never `#FFFFFF`), `texte_sur_sombre`, `texte_sur_clair`, `accent` (a single strong color) and `accent_2` (optional). Unreadable link: say so and ask for the HEX values. Colors described without HEX: propose HEX values and have them approved. Never pick a palette the user hasn't seen. A font that belongs to a device brand (SF, New York…) is refused by the checker: propose a free sans-serif (list in `film-spec.md` § 3) and say why. The user's own font goes through `fichier`.

**Preparing the visuals.** Create a working folder (in the current folder, unless the user names another) with `visuels/` and `musique/`, and copy their files into it.

- Size: `ffprobe -v error -show_entries stream=width,height -of csv=p=0 <file>`. Cut-out object: 2,400 px wide or more; 3 to 5 close views for a rotation; parts in the same frame for an exploded view. Macro: 2,900 px for a full frame. Screenshot: native resolution or ×2.
- Object photo that isn't cut out: ask for a transparent PNG. Failing that, offer `npx hyperframes remove-background photo.jpg -o objet.png`; warn that the model is made for people and downloads on first use, and show the result.
- Sensitive data in a screenshot: blur the area (`ffmpeg -i capture.png -filter_complex "[0]crop=w:h:x:y,gblur=sigma=12[f];[0][f]overlay=x:y" capture-floue.png`) or ask for a demo screenshot.
- Screen recording: pull still frames at the key moments (`ffmpeg -ss <t> -i video.mp4 -frames:v 1 capture.png`).
- A visual is missing: don't wait. The engine puts in a neutral fallback (gray shapes, no text or brand) and the visual goes on the to-provide list.

**The music.** Copy the file into `musique/` (`.mp3`, `.m4a`, `.wav`, `.aac`). Set `droits_confirmes: true` only because the user said so. Otherwise `musique: null`.

## Step 2 — The structure, scaled to the length

Read `references/grammaire-film.md` § 2 to § 4, then `references/declinaisons.md` § 1 to § 3.

- Choose the **family** from the visuals, not from what you'd like (`grammaire-film.md` § 4).
- Count the **distinct visuals**: about 7 for 60 s, 10 for 90 s, 14 for 120 s (one visual feeds 2 to 3 shots). Below that, the film repeats itself: propose a shorter length or ask for more visuals. The checker flags it.
- Lay out the **five beats** scaled to the length with the table in § 3: hook, build-up, reveal after 60% of the length, name after 76%, end. Beyond 60 s, a build-up in 2 or 3 chapters of a single idea each (§ 3.1).
- Place the **texts**: a thesis at the end of the hook, one card per chapter, one name per feature for software, a closing line, the name (§ 3.2).
- Choose the **cut-downs** and their template (`declinaisons.md` § 3).

Show the structure **before** producing anything, in two short tables. The film, one row per beat or per chapter:

| # | Beat | From → to | What we see | Text | Visual |
|---|---|---|---|---|---|
| 1 | Hook | 0:00 → 0:09 | a glow comes out of the black; the object's outline | thesis, 5 words | cut-out photo |
| 2 | Chapter 1: [idea] | 0:09 → 0:32 | macros, slow rotation | 1 idea card | macros, 3 views |
| 3 | Reveal | 0:44 → 0:52 | the whole object, halo, slow pull-back | — | cut-out photo |
| 4 | Closing line, name, end | 0:52 → 1:00 | the closing line, the name alone, black | closing line, name | — |

The cut-downs:

| Output | Format | Length | Opening | What it keeps |
|---|---|---|---|---|
| vertical-30 | 9:16 | 30 s | 3 words over the strongest image | reveal and name, 2 proofs, closing line, end |

Add three lines at most below: the chosen palette and fonts; what is still missing (visuals, figures); the conventions taken (for example "90 s with no voice: never observed, done in 2 chapters"). Wait for the user's approval. Changing a row costs a minute; redoing a render costs far more.

## Step 3 — The storyboard: `film.json` and the review sheet

Read `references/recettes.md`, then `references/film-spec.md`. Look at `assets/exemple-film.json` for the level of detail: it is fictional, so don't reuse its content.

Write `film.json` in the working folder: `meta` (`formats`, `duree_cible_s`), `theme`, `musique`, `plans` in film order, `declinaisons`. For the shots:

- **One shot = one recipe** out of the 12 in `recettes.md`. Choose it from the available visual (§ 1.1) and the film's beat (§ 1.2).
- **The approved structure**: the `revelation` after 60% of the length, the `fin` last, no name before 76%. U-shaped rhythm: shots of 2.5 to 4 s in the hook, 1 to 2 s in the build-up, one long shot at the reveal.
- **Texts** (`grammaire-film.md` § 6): 6 words at most in one block, 12 at most built in groups; one idea per card; the text states the idea, the image proves it; sentence case, no exclamation mark; never two cards in a row without an image between them (except in a text-only film). The same words in every format.
- **Thin brief: propose, don't leave a gap.** Write the thesis, the ideas and the closing line in the user's words, from their brief. The proposed text goes in `texte`; `notes` then starts with "TO VALIDATE: ". A proposal contains no number, not even spelled out.
- **Figures**: `texte.chiffre` and `source` only if they were provided; otherwise `"chiffre": null`, and the screen shows `[TO PROVIDE]`, dimmed.
- **`notes`**: the intent of the shot, in one sentence. It shows on the review sheet, never in the film.
- **For the cut-downs**: a `role` on each shot, a shared `groupe` for a card and the shot that proves it, `priorite: 1` on the most visual proofs (`declinaisons.md` § 3.5). Start with `"regle": "auto"`.

Check the file (step 4), then make the review sheet:

```bash
python3 "$SKILL/scripts/check_film.py" film.json
node "$SKILL/scripts/build_film.js" film.json --planche
```

The review sheet (1 to 2 minutes of compute) writes `sortie-<title>/planches/<output>.png`, one per output: one image per shot, with its recipe, its role, its timing, its text, its intent and the checker's remarks in red. Look at each review sheet yourself before showing it (image-reading tool). Then give the user the paths, a three-line summary and the list of missing visuals. Wait for their approval before the render.

## Step 4 — The check

```bash
python3 "$SKILL/scripts/check_film.py" film.json
```

It enforces the skill's rules: no voice, local music with confirmed rights, brand fonts refused, card durations and reading time, words per card, safe zones and line length per format, figures without a source, position of the name and the reveal, text pace, contrast of the theme colors. `build_film.js` runs it again on the resolved outputs (`auto` cut-downs, adjusted durations): read what it prints too.

- **Zero errors before the render.** Fix `film.json` and run it again. A text that doesn't fit gets shorter: remove words, don't shrink the type.
- Each warning gets fixed, or is kept knowingly and mentioned at delivery. Expected and acceptable: a missing visual (fallback), a `[TO PROVIDE]`, a text share above 45% for software, a high pace for a text-only film.
- `--force` (render despite errors) only if the user asks for it.

## Step 5 — The render

The 16:9 film first, then the cut-downs. `--check` adds `npx hyperframes check` (real contrast, layout) before each render.

```bash
node "$SKILL/scripts/build_film.js" film.json --rendu --seulement film --check
node "$SKILL/scripts/build_film.js" film.json --rendu --seulement vertical-30,carre-15 --check
```

After `--seulement`, put the `id`s of your cut-downs, separated by commas.

The MP4s go into `sortie-<title>/rendus/`; the HyperFrames projects into `sortie-<title>/projets/` (they open with `npx hyperframes preview`). Compute takes about one second per second of video; run a long render in the background. `--qualite draft` gives a quick draft; `standard` is the default; `high` for the final delivery if the user asks for it.

## Step 6 — The visual check

Look at the result before handing it over: the checker doesn't see everything. For each MP4:

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type -of csv=p=0 <video>.mp4
ffmpeg -v error -y -i <video>.mp4 -vf "fps=30/<duration in s>,scale=480:-1,tile=6x5" -frames:v 1 verif-<output>.jpg
ffmpeg -v error -y -ss 0.2 -i <video>.mp4 -frames:v 1 verif-<output>-debut.png
```

The contact sheet shows 30 frames spread over the whole video. Read the images, then check:

- the expected length; an audio track only if there is music;
- every text whole, readable, centered, inside the safe zone, with no box behind it, one at a time;
- no black band at the edge of a shot, no frozen image longer than 2 s (except cards and the name);
- the reveal held, the name alone at the end;
- in a cut-down: frame 0 full, text readable at 0.2 s, no black at the end (checklist in `declinaisons.md` § 9);
- the `[TO PROVIDE]` items visible and dimmed; the gray fallbacks, acceptable in a draft only;
- nothing that recalls Apple: no device, no font, no signature.

A defect: fix `film.json`, then redo steps 4 and 5.

## Step 7 — Delivery

Deliver in one short message:

1. **the files**: each MP4 (path, format, length), `film.json` and the review sheets;
2. **to validate**: the proposed texts (shots whose `notes` start with "TO VALIDATE"), one by one;
3. **to provide**: the remaining `[TO PROVIDE]` items (figures with their source, call-to-action line, logo), shot by shot, or "none";
4. **the visuals to provide for a better version**: each fallback from the checker, with what the visual should show and its format (cut-out PNG of 2,400 px, 3 to 5 views, native screenshot ×2…);
5. in one line: the conventions taken (voiceless length beyond 68.5 s, 9:16 and 1:1 formats never observed…) and the warnings kept;
6. for what comes next: edit `film.json` and run the render again; a manual edit made in a project is erased the next time the engine runs.

## Reminders

- **No voice.** No voice-over, no speech synthesis, no narration subtitles. Skip the voice steps of the HyperFrames skills (`product-launch-video`, `media-use`, `npx hyperframes tts`).
- **No music without rights.** The user's file, or `musique: null`. Never music that was searched for, downloaded, generated or taken from a library, even "royalty-free", even if a HyperFrames skill offers it by default.
- **No invented figures**, and no invented dates, reviews, quotes or client logos. What is missing stays visible: `[TO PROVIDE]`. One wrong figure is enough to ruin trust.
- **The grammar, never the brand.** No recognizable image, sound or device (a floating panel with no device outline replaces it), no Apple font or logo, no signature ("shot on…", a lone logo on black, the frozen clock of demo screens).
- **No keynote quotes**, not even translated. Texts are written in the user's words.
- **Recompose, never crop**: each format is its own composition; the words don't change from one format to another.

## Reference files: when to read them

| File | When |
|---|---|
| `references/grammaire-film.md` | Step 2 (§ 2 to § 4: the beats, the structure, the families). Step 3 (§ 5 to § 8: rhythm, text, name, image). When in doubt about a count or a convention (§ 11). |
| `references/declinaisons.md` | Step 2 (§ 1 to § 3: principle and templates). Step 3 (§ 3.5: the cut-down in `film.json`; § 4 and § 5: safe zones and recomposition). Step 6 (§ 9: checklist). |
| `references/recettes.md` | Step 3, before writing the shots: choose the recipe, its visuals, its settings; § 4 when a visual is missing; § 5 for two 60 s sequences already checked. |
| `references/film-spec.md` | Step 3, before writing `film.json`; and to understand an error from the checker or the engine. |
| `assets/exemple-film.json` | Step 3: a complete (fictional) film with cut-downs, for the level of detail. Its neutral visuals are in `assets/exemple-visuels/`. |
| `scripts/check_film.py` | Steps 3 and 4: the checker (Python 3.9, no dependencies). |
| `scripts/build_film.js` | Step 3 (`--planche`) and step 5 (`--rendu`): Node, ffmpeg, `npx hyperframes`, no npm dependencies. |
