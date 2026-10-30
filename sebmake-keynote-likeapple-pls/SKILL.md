---
name: sebmake-keynote-likeapple-pls
description: "Builds a 16:9 deck plus the full speaker script on the grammar of Apple keynotes (run of show, announcement sequence, one idea per slide, pacing), in the user's own branding, for Keynote, PowerPoint, Figma Slides, Canva or video. Use it whenever someone wants an Apple-style or keynote-style presentation, deck or pitch, a staged product launch or demo, or a clean deck that hits hard, even if they never say Apple. Not for a plain .pptx export with no staging (that's the pptx skill), nor for Apple-style UI design."
---

# Apple-style presentation

This skill produces a 16:9 presentation and the script that goes with it, built like an Apple keynote: a flow that builds up, an announcement sequence, one idea per screen, handovers between speakers, nested recaps. It takes the **grammar** observed in 8 keynotes (2019-2026), never the **brand**: the colors, fonts, product and figures are the user's.

Everything comes from a single file, `deck.json`. The check, the .pptx, the HTML preview and the script all come out of it. Always fix `deck.json`, never the rendered file: otherwise the fix disappears at the next render.

```bash
SKILL="<folder of this SKILL.md>"   # often ~/.claude/skills/sebmake-keynote-likeapple-pls
```

**Language.** The deck and the script are written in the user's own language. When the user writes in French, set `"langue": "fr"` and use the French templates (`gabarit_fr`) and the `[À FOURNIR]` / `[À VALIDER]` markers. Otherwise, write in English: `"langue": "en"`, the EN templates and the `[TO PROVIDE: …]` / `[TO VALIDATE: …]` markers. The checker accepts both marker forms.

## Step 1: Intake

First reread the request and the attachments, and note what is already said. Never ask again for something the user already gave: they wrote it so they would not have to repeat it.

Then ask the missing questions with the AskUserQuestion tool if it exists, otherwise in plain text, grouped in a single message. No more than 4 questions per call. The tool accepts only 4 choices per question, plus “Other”: when the list is longer, offer the 4 most likely from the brief and name the others in the question text.

**Call 1: the frame.**

| Question | Choices | Why |
|---|---|---|
| Output format | Keynote, PowerPoint, Figma Slides, Canva, video (video through “Other”, named in the text; or the reverse if the brief talks about video) | It decides the render. The output is always 16:9, whatever the format. |
| Branding | A link to my design system; my colors in HEX (and my fonts if I have some) | The skill does not know the user's branding. |
| Audience | The client or audience type from `references/publics.md` §1 (B2B decision makers, B2B buyers, general public, investors, partners, internal team, trade show, recruiting, I don't know) | This is the only question about the audience: it alone decides which devices are kept (charts without axis ticks, anonymous competitor, sources, “up to”…). Do not ask device by device. |
| Language and register | English; French: vous to the audience, tu between speakers; French: vous everywhere; French: tu everywhere | In French, tu or vous is always asked, never assumed. The reverse case (tu to the audience, vous between speakers) goes through “Other”. In English, ask in call 2: casual tone (first names) or formal (first name, last name, role). |

**Call 2, if not already said**: the length (5, 10, 20, 30 min or more), the context (in the room, video call, recorded video), and in English the casual or formal tone.

**Branding with no link and no HEX** (answer “Other”, “I don't have any”): ask them to describe the colors they want, with their HEX if they have them. If they describe without HEX (“midnight blue and orange”), propose matching HEX values and have them approved. Never pick a palette they have not seen.

**Then the brief, in plain text.** Give this template to fill in, and say what will happen to what stays empty: the wording (thesis, problem, description of a feature) will be proposed and marked `[TO VALIDATE]`; figures, prices, dates, client names, logos, testimonials and screenshots will stay `[TO PROVIDE]`. The user can then answer in part without blocking everything. Leave in it only the lines that still have no answer.

```
Branding: [design system link] or [HEX: dark background, light background, text, accent] + [title / body fonts]
Topic and goal: [what this is about] → [what the audience must remember or do when they leave]
Speakers: [First Last, role], … · Who opens and closes: [First name]
New thing 1: [name] · [problem solved] · [benefit in one sentence] · [proof + source]
             · [what can be shown: demo, screenshot, video] · [price] · [date]
New thing 2: …
Big moment to keep for the end: [which one]
Materials: [screenshots, photos, logos, videos: paths or attachments]
```

**Read the branding.** With a link, read it with the session's tools: Figma (`get_variable_defs`, `get_screenshot`, after the Figma skill these tools require), Notion (read the page), web page (WebFetch), PDF or brand guide file (Read). Extract the HEX for the `theme` roles (`fond_sombre`, `fond_clair`, `texte`, `texte_secondaire`, `accent`, `accent2`) and the title and body fonts. If the link cannot be read (tool missing, access denied), say so and ask for the HEX. If a role is missing (no dark background, for example), derive it from their palette and show it to them. If the guide names an Apple font (SF, New York), propose a free sans-serif instead and say why. If it caps the accent area (“yellow ≤ 10 %”), set `theme.finale_accent` to `false`: otherwise the final slide becomes a full accent page. A color the user did not choose never goes by in silence.

**Read the audience.** Open `references/publics.md`: the table in §3, the audience card (§4), and §5 if the audience is mixed or unknown.

## Step 2: Run of show

Read `references/grammaire.md` §1 to §4 and §9. Build the flow to the scale of the length with the table in §3: number of blocks, screens and voices, version of the announcement sequence (16, 8 or 6 steps). For a length between two rows, start from the closest row and adjust the number of screens (about 2 per minute). Pick the announcement variant (§4.3: product, feature, service, technology) from the new things.

Keep the rules of §1: the same person opens and closes, every block ends with a recap, every announcement has a name and a mini-recap, the biggest topic goes last. These rules give the “keynote” effect, far more than the slide style. Hand over early (before 15 to 20 % of the time) and change voice or mode every 3 to 4 minutes.

Show the run of show **before** producing anything, as a short table:

| # | Block | Speaker | Length | Slides |
|---|---|---|---|---|
| 1 | Opening: welcome and thesis | [host] | 0:45 | 2 |
| 2 | [New thing 1] (6 steps) | [host] → [expert] | 3:00 | 6 |
| 3 | [New thing 2, the big moment] (8 steps) | [expert] → [host] | 5:00 | 11 |
| 4 | Recap, dates, close | [host] | 1:15 | 3 |
| | **Total** | 2 voices, 3 handovers | **10:00** | **22** |

Add three lines at most below it: the setting chosen for this audience (sources, charts, competitors, “up to”), in one sentence, so they can relax it; the palette and fonts chosen; what is still missing. Wait for their approval and adjust. Changing a row of the run of show costs a minute; redoing twenty slides costs far more.

## Step 3: Design slide by slide

Read `references/designs.md`: the “Choosing a design” part, then the card of each archetype in the run of show. For each slide, decide:

- **the archetype and the variant.** The archetype comes from the announcement step (`grammaire.md` §4.1, Visual column). The variant comes from the content and the visuals the user has, or can get: a screenshot calls for a device, a photo for an on-image variant; with nothing, a variant with no visual, never an empty frame. The table “The engine's variants” says what each one needs.
- **the rhythm.** Vary the designs from one block to the next, and never the same composition (same archetype, same variant) three times in a row. Two blocks do not open the same way.
- **one strong visual moment per block**, at least: a giant figure (A5), an object or an interface (A9, A10), the product alone (A13), the bento (A14), a full-bleed photo (A18) or an image variant.
- **the recap of a software product** (platform, SaaS business tool): use A14 `fragments-logiciel`. Its tiles follow the demo, each one carries an isolated component from the mockup (not a whole screen), with at most one photo of the product in use (Unsplash or Pexels) taken in the audience's market (`designs.md`, A14, variant g).
- **the visual to prepare**, from §7 of the card: its type, a brief (what it shows, its framing, its light), transparent background or not, the angle, the minimum resolution. When you can look for it yourself, propose it (`designs.md` §2, rule 7). In a mockup, don't stop at the screen: go down to the component that says what the feature does. For photos of use or mood, you can draw on Unsplash or Pexels, with a verified free license, the author noted and a photo taken in the audience's market.

Show the result as a short table, after the approved run of show, one row per slide:

| # | Block | Design | What you see | Visual |
|---|---|---|---|---|
| 5 | [New thing 1] | title card on photo | the name, in white, on a calm photo of the place | photo to provide |
| 6 | [New thing 1] | screenshot in a phone | the tracking screen, from the front, alone | screenshot to provide |

Then deliver the **list of visuals to prepare**: one brief per visual, slide by slide (type, what it shows, format, transparent background, angle, resolution). The user can start their screenshots and photos while you write the deck. Don't wait for the visuals: as long as one is missing, the engine draws a neutral fallback, with no figure and no logo. After the check, `export_script.js --visuels` rewrites this list from `deck.json`: that is the one you deliver at the end.

## Step 4: Art direction, then deck.json

**Art direction first.** Read `references/style-visuel.md` before writing any text: it shows what a good slide looks like. Aim for the look of a keynote:

- very short, very large titles: one word or one sentence per screen, never a paragraph;
- an accent kicker (`textes.surtitre`, 1 to 3 words) where it places the moment, and the title's final period in accent;
- the designs from step 3: the variant of each slide, and the strong visual moment of each block;
- when a screenshot is missing, a schematic interface, which the engine draws from `image.attendu`;
- a strong final slide: one word, very large;
- the same background on every slide, the one of the rest of the deck; change it only between two blocks;
- nothing from the workshop on screen or in the notes: no archetype, no step, no instruction.

Then read `references/deck-spec.md`. Create a working folder for the presentation (in the current folder, unless the user names another one), with `deck.json` and an `images/` subfolder where you copy their materials.

Fill in `meta` (title, language, `registre` toward the audience and `registre_intervenants` between speakers, audience, `duree_min`, format, `"ratio": "16:9"`, announcement variant, and `contexte`: `direct` in the room or on a video call, `preenregistre` for video), `theme` (step 1) and `intervenants`. Then, for each slide of the run of show:

- **`archetype`** and **`variante`**: those from step 3. Always write the variant: without it, the engine keeps a simpler render. One idea per screen. No `AF` slide: take the planned archetype and fill it in.
- **`visuel`**: the brief of the visual to prepare, `{type, brief, fond_transparent, angle, resolution_min}`, on every slide that expects an image (step 3).
- **`textes`**: 10 words at most, recounted after translation. The name to remember, alone; `*word*` for the accent; `surtitre` to place the moment. A figure, a price or a date on screen comes from the user, otherwise `[TO PROVIDE: label]` in 3 words at most, with the full instruction in `a_fournir`.
- **Thin brief: propose, don't leave a hole.** Write plausible proposals for the wording, the thesis, the problems people live with, the feature descriptions and the script, from what the brief says about the product and the audience, and mark each one `[TO VALIDATE: …]`. On screen, it shows as real content; in the notes, it stays flagged. Never a proposal for a figure, a price, a date, a client name, a logo, a testimonial or a real screenshot: those stay `[TO PROVIDE]`. A proposal contains no number, not even spelled out.
- **`source`**: every figure carries its own. The engine shows it according to the audience (under the figure, as a numbered note or on the final card); `meta.affichage_source` only forces another choice.
- **`notes`**: the script, written to be spoken, **in full**: it must read aloud at about 140 words per minute for the target length (about 1,400 words for 10 minutes). Short sentences, in the chosen register, that say what is on screen at the moment it appears. Use the templates in `grammaire.md` §7 (EN or FR column, register variant) and vary them from one block to the next (§8). Each change of voice is a segment `{"intervenant": "…", "type": "relais", "texte": "…"}`: it follows `registre_intervenants`, the rest of the script follows `registre`. A testimonial exists only if it is provided. An unknown speaker role stays empty (`role` absent), never a marker.
- **`build`**: the builds in order, one sentence per click, and the stage directions (silence after the name, start the video, demo). The engine turns them into fade-in builds, and each slide enters with a fade. Directions go there, not in the spoken text, since the presenter reads their notes.
- **`duree_s`**: count about 140 words per minute, then add the silences and the real length of demos and videos. The check warns above 170 words per minute on a slide, and below 110 or above 170 over the whole deck. The sum must stay within ±15 % of `duree_min`.
- **`image`**: a path relative to `deck.json`, or `{"chemin": "images/…", "attendu": "what the image must show"}` if it is still missing: the engine draws a schematic interface in its place, with no figures.

In English: `"langue": "en"`, EN templates, `[TO VALIDATE: …]` and `[TO PROVIDE: …]` markers, no `registre`; the casual or formal tone is set in the handover phrases (§7.7). Everything the presenter reads is in English, notes included. In French: `"langue": "fr"`, FR templates, `[À VALIDER : …]` and `[À FOURNIR : …]` markers, and `registre` set to `tu` or `vous`.

`assets/exemple-deck.json` shows a complete 16-slide deck for 10 minutes (fictional), with variants, `slide.visuel` briefs, a few `[TO VALIDATE]`, one short `[TO PROVIDE]` and a missing image: look at it for the level of detail of the script, the briefs and the markers. Don't reuse its content.

## Step 5: Check

```bash
python3 "$SKILL/scripts/check_deck.py" deck.json --brouillon   # while writing (draft mode)
python3 "$SKILL/scripts/check_deck.py" deck.json               # before delivering
```

The check covers the rules for the audience, the register, the timing, the speaking rate of the script, the background, the markers, the 10 words, the variants and the rhythm of the designs. A deck that passes therefore keeps what the run of show promised. Fix `deck.json` and run it again until there are **zero blocking errors in `--brouillon` mode**. Its “TO VALIDATE” section lists the proposals: keep it for the delivery.

Without `--brouillon`, the remaining `[TO PROVIDE]` markers block, and that is on purpose: the skill invents nothing to make them go away. Ask the user for them again, in a single list. If they don't have them, deliver and say so: it is a draft to complete, not a version to present. For each warning, fix it, or keep it knowingly and say why at delivery.

## Step 6: Render

Always build the .pptx and the preview. They are the deliverable for PowerPoint, Keynote and Canva, and the check for Figma Slides and video.

```bash
[ -d "$SKILL/scripts/node_modules/pptxgenjs" ] || (cd "$SKILL/scripts" && npm install)
node "$SKILL/scripts/build_deck.js" deck.json sortie.pptx --preview apercu.html
```

Run the command from the working folder. If `node` is missing, say so and deliver `deck.json` and the script: don't install anything in the user's place. The .pptx always writes the theme fonts, even when they are missing on this machine: the preview then shows in the fallback font, and the engine says so in one line; pass it on (the font must be installed on the machine that presents). `--polices repli` writes the fallback font into the .pptx, only if the user asks. Deliver a single .pptx: no second file in the fallback font.

Then read **only** the file for the chosen format:

| Format | Read | What the user gets |
|---|---|---|
| PowerPoint | `references/formats/powerpoint.md` | the .pptx |
| Keynote | `powerpoint.md` §1, then `references/formats/keynote.md` | the .pptx to open in Keynote; the .key if Keynote is installed and they agree |
| Canva | `references/formats/canva.md` | the design imported by the connector, otherwise the .pptx and the steps to follow |
| Figma Slides | `references/formats/figma-slides.md` | a Figma Slides file built with `use_figma` (skills `figma-use` and `figma-use-slides` first); the .pptx as a backup |
| Video | `references/formats/video.md` | depending on the path they choose (MP4, clickable deck, export); the skill writes the script but produces no voice |

## Step 7: Visual check, then delivery

**Look at the result before handing it over.** The check does not see a title broken over three lines or an accent that can't be read on a photo.

- Open `apercu.html#qa` (absolute path as `file://`) with the session's browser tool. The top banner says no overflow was detected, or lists the slides that overflow; `window.__deckQA()` returns the same list.
- Take a screenshot of at least four slides: the opening, a figure slide, the busiest one and the close. Check: one idea per screen, large titles that hold the center, one visual moment per block, the same background everywhere, no empty frame, no workshop word (archetype, step, instruction), short `[TO PROVIDE]` markers, faded and underlined (in brackets for Canva), the theme colors, nothing that recalls Apple.
- For Figma Slides, Canva or video, also look at the final render with the format's tools (Figma screenshot, review of the design, HyperFrames preview).
- Without a browser, rely on the “to check” list from `build_deck.js` and ask the user to open the preview.
- A text overflows: cut words in `deck.json`, then redo steps 5 and 6. Don't reduce the size: a text that doesn't fit is a text that is too long.

**Write the full script** in `script.md`, slide by slide, with speakers, handovers, timing, builds, sources, proposals to validate and what is still to provide. Add `--visuels visuels.md` for the list of visuals to prepare (from `slide.visuel` and `image.attendu`), `--etapes` for the list of builds (the .pptx already contains them; the list is there to check them, or to set them in Figma Slides and Canva), and `--srt sortie.srt` for subtitles:

```bash
node "$SKILL/scripts/export_script.js" deck.json --md script.md --visuels visuels.md --etapes
```

**Deliver** in a short message:

1. the file (path or link) and, in one line, how to open it;
2. `script.md`, the full script (it is also in the notes of each slide);
3. **to validate**: the `[TO VALIDATE]` proposals, slide by slide (the check's “TO VALIDATE” section), to accept or correct one by one;
4. **to provide**: the remaining `[TO PROVIDE]` markers and their instruction, the images to provide and the unknown speaker roles, slide by slide (the check's still-to-provide and image-to-provide lines without `--brouillon`), or “none”;
5. **the visuals to prepare**: `visuels.md`, one brief per visual, slide by slide, or “none”;
6. what is left to do by hand: morphs and builds outside reading order (the engine sets the fades), the fonts to install, and the audience setting recalled in one sentence.

## Reminders

- **No invented figure, price, date, client name, logo, testimonial or screenshot**, not even in a schematic interface (gray bars, not numbers). A single wrong figure is enough to ruin trust, and a figure that can't be checked can be judged misleading. What is missing stays visible: `[TO PROVIDE: label]`. What can be written is proposed: `[TO VALIDATE: …]`.
- **The grammar, never the brand.** No Apple logo, font (SF, New York), image, device or slogan. The user presents their product, with their identity.
- **No quote from an Apple keynote**, and no signature phrase. The [slot] templates in `grammaire.md` are enough, and the script is written in the user's words.
- **Visible sources when the audience requires them.** The corpus sources nothing because it targets the general public of a very well-known brand. In front of investors, buyers or an unknown audience, the same practice loses trust: follow `publics.md`.
- **Always 16:9**, whatever the format.
- **The user's language.** English by default; French decks (`"langue": "fr"`) use the French templates and markers.

## Reference files: when to read them

| File | When |
|---|---|
| `references/grammaire.md` | Every time. §1 to §4 and §9 for the run of show (step 2); §4.1 and §6 for the design (step 3); the art direction and §5 to §8 while writing (step 4). |
| `references/designs.md` | At step 3: “Choosing a design”, then the card of each archetype in the run of show (variants, visual content, depth, visual brief and fallback). At step 4 to write `slide.variante` and `slide.visuel`. |
| `references/style-visuel.md` | At step 4, before writing the texts: the text measurements, which the engine follows. |
| `references/publics.md` | As soon as the audience is answered (step 1), then to set sources, charts and competitors. |
| `references/deck-spec.md` | Before writing `deck.json` (step 4), and to understand an error from the check. |
| `references/formats/<format>.md` | At step 6, only the one for the chosen format (plus `powerpoint.md` §1 for Keynote and Canva). |
| `references/data/archetypes.json` | When an archetype raises a question: elements, layout rule. The variants the engine draws are in `designs.md`. |
| `references/data/annonce.json` | For the detail of an announcement step or a variant. |
| `references/data/formules.json` | To vary the phrases beyond `grammaire.md` §7 (EN and FR templates). |
| `references/data/runofshow.json` | For exact run-of-show proportions (the 8 keynotes, segment by segment). |
| `references/data/lexique.json` | Rarely: word frequency in the English corpus, to dose an adjective. |
| `references/data/publics-exigences.json` | Machine version of `publics.md`, read by the scripts. Read it only to understand a warning. |
| `references/analyses/S1` to `S4` | Analysis archives, only when in doubt about a count. They contain keynote excerpts: copy nothing from them. |
| `assets/exemple-deck.json` | Complete fictional example, for the level of detail of the script, variants, visual briefs and markers. |
| `scripts/check_deck.py`, `scripts/build_deck.js`, `scripts/export_script.js` | Check (Python 3.9 and later, no dependency), .pptx render and preview (Node 18 and later, pptxgenjs), script, visuals to prepare, builds and subtitles (Node, no dependency). |
