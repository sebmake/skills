---
name: sebmake-videoedit-like-applepls
description: "Edits like Apple keynote films: cuts the user's footage (and their music), or assembles finished chapters with voice-over, subtitles and music ducked under the voice, in FilmCraft or as FCP7 XML (or EDL) for Resolve and Premiere; or reviews an existing edit shot by shot against the films of its family (pacing, cuts, blacks, reveal, text), with fixes at the timecode. Use it whenever someone wants to edit their own footage like an Apple keynote film, asks for editing help, a timeline, to assemble a narrated walkthrough, or an edit review (pacing, cuts, transitions, where the reveal or title lands), works in DaVinci Resolve, Premiere Pro or FilmCraft, even without the word Apple. Not for a product film generated in motion design (sebmake-videopresentation-likeapplepls), animating titles or logos (sebmake-motiondesign-likeapplepls), or slides (sebmake-keynote-likeapple-pls)."
---

# Editing like keynote films

This skill helps you edit. It does three things:

1. **build a timeline** from the user's footage, and their music if they have some, then lay it out in FilmCraft (driven from here) or hand it over as a file for Premiere Pro and DaVinci Resolve;
2. **assemble a composed edit**: finished elements (rendered chapters or scenes, one voice line per sentence, subtitles, music that ducks under the voice, one-off sound effects), each on its own track and at its own time;
3. **review an edit**: measure it shot by shot against the films of its family, and say what to fix, down to the timecode.

In FilmCraft, the edit stays **a project you can understand and pick up again**: each track is named by its role, the skill shows how the edit is built (screenshot, edit map), reads back changes made by hand and carries them into `montage.json`. You keep working in the app, round after round.

The rules come from four analyses of the films of 8 keynotes (2019 to 2026), broken down shot by shot: 16 product films, 20 opening and mood films, 8 documentaries, 8 trailers and usage films. Each rule carries its count ("N out of M"); anything not measured is marked **convention**. The skill takes the **grammar**, never the **brand**: no Apple image, sound, logo or font, and no line from the films. The images, music, text and logo are the user's.

The pipeline:

```
footage ─ analyse_rushes.py ─▶ rushes.json (completed by eye) ─ assemble.py ─▶ montage.json
   plan.json (chapters, voice, subtitles, music, sound effects) ─ compose_montage.py ─▶ montage.json   (composed edit)
   montage.json ─▶ filmcraft_build.py (FilmCraft) | export_xml.py (Premiere, Resolve) | export_edl.py
   montage.xml, video or the user's timeline ─ critique_montage.py ─▶ critique.md
```

Always fix `rushes.json` or `montage.json`, never the XML or the EDL: they are rewritten on every export.

```bash
SKILL="<folder of this SKILL.md>"   # often ~/.claude/skills/sebmake-videoedit-like-applepls
PY=~/.venv-videoedit/bin/python    # Python with numpy and Pillow
```

**Requirements.** ffmpeg and ffprobe. Python 3.9 or later. `analyse_rushes.py` and `critique_montage.py` need numpy and Pillow; `export_xml.py --cartons png` needs Pillow (without it, titles stay as text, with a warning). Put them in the `~/.venv-videoedit` environment: `python3 -m venv ~/.venv-videoedit && ~/.venv-videoedit/bin/pip install numpy pillow`. When run without numpy, `analyse_rushes.py` and `critique_montage.py` relaunch themselves with that Python; for `--cartons png`, run `export_xml.py` with `$PY`. The other scripts use only the standard library. FilmCraft is needed only for driving it. If something is missing, say so, and install nothing without the user's consent. Without numpy, the skill can still build and export a timeline from a `rushes.json` filled in by hand; it can neither analyze nor review.

## Step 1 — Intake

Reread the request and the attachments. Don't ask again for anything already said.

Ask the missing questions with the AskUserQuestion tool if it exists, otherwise in plain text, in a single message. **At most 4 questions per call**, at most 4 choices per question (plus "Other").

| Question | Choices | Why |
|---|---|---|
| What do you have? | footage and music I hold the rights to; footage, no music; finished elements (rendered chapters or scenes, voice-over, subtitles, music, sound effects); a finished edit to review (with or without its footage) | The three kinds of help. Music: the user's or none. The third choice leads to step 2b. |
| Which family of film? | product and reveal; opening and mood (sketch, fiction, closing film included); documentary and testimonial; trailer and usage | Each family has its own grammar (`grammaire-montage.md` § 2). |
| Length and format | the recommended length for the family, in 16:9; a specific length in 16:9 (say it); vertical 9:16; square 1:1 | Observed lengths in § 9.1. 9:16 and 1:1: never observed, convention. |
| Which software? | FilmCraft (I drive it from here); Premiere Pro (XML file); DaVinci Resolve (XML file); another one (EDL file) | The output (`logiciels.md`). |

Recommended lengths (observed medians, then range): product 32 s (24 to 51); opening 90 s (convention, observed 65 to 143); transition between two places 24 s (11 to 31); documentary 142 s (78 to 324); trailer 89 s (50 to 119); usage 60 s (2 films: 60 and 93.5 s). An opening under 60 s is a convention: the landing tightens to keep the peak after 60%; under 30 s, use the transition between two places.

**Then the brief, in plain text**, with only the lines still unanswered:

```
Footage: [folder or files]          Music: [file], and you confirm you hold the rights
Name or title on screen: [as it is written]      Closing line: [3 to 9 words]     (optional)
People filmed: [name · role], and their consent to be named          (documentary)
Speech: [timestamped transcript or interview subtitles]              (documentary, spoken lines)
Block titles: [one per topic]                                        (catalog trailer)
Title card styling: [font] · [background and text color in HEX] · [logo]
```

Say what will happen to whatever stays empty: **no text is invented**. You may suggest a wording (a sentence, a thesis), marked "to approve"; it goes into `rushes.json` only after the user agrees. A name, a figure, a quote or a job title is never suggested: missing text stays missing, and `assemble.py` reports it.

For a review only, ask instead for: the file (rendered video, FCP7 XML or EDL), the family, and the subtitles and sound if they have them; then go to step 6.

## Step 2 — Footage analysis

```bash
$PY "$SKILL/scripts/analyse_rushes.py" rushes/ --musique musique.wav -o rushes.json
```

The script splits each video file into takes (same detector as the corpus); a still (`.png`, `.jpg`, `.tif`…) becomes a single still take. It measures motion, sharpness, light, camera (locked-off, slow, fast, handheld), zones to avoid (blur, black, shake, blown-out image), candidate strong moments (`naissance_lumiere`, `plan_tenu`, `pic_mouvement`, `mouvement_continu`, `changement_lumiere`), the sound, and for the music: tempo, strong attacks, high point, end. It writes one contact sheet per file (3 thumbnails per take) into `planches_rushes/`. It refuses to overwrite a `rushes.json` that has already been completed: to rerun the analysis (a clip added), add `--fusionner`, which keeps the fields filled in by eye for each take it finds again (same file, bounds within ± 0.1 s) and those at the root.

**Look at each contact sheet**, then complete each take in `rushes.json` (`montage-spec.md` § 1.2 and 1.3):

- `valeur` (`detail`, `serre`, `rapproche`, `moyen`, `entier`, `large`, `abstrait`) and `sujet` (`objet`, `piece` — a part of the object; a room in a house is `decor` —, `matiere`, `decor`, `lumiere`, `geste`, `ecran`, `personne`, `entretien`, `photo`…: list in § 1.3), written exactly like this, without accents: without them, `assemble.py` picks blindly, and it reports an unknown subject in `journal`;
- `role` when a take stands out (`accroche`, `revelation`, `fin`, `pic`, `arrivee`, `bouton`…), `note` from 1 to 5 (`notes` is only a free comment), `prises` to leave out a failed passage;
- documentary: `personne`, `fonction`, and `paroles` (`entree_s`, `sortie_s`, `texte`, in seconds of the file) for each interview take. The skill does not listen: take the times from the user's transcript or subtitles; `son.passages_actifs` only gives candidate bounds, voice and noise mixed;
- at the root: `nom`, `phrase`, `logo`, `police`, `couleurs`, and `format` (`{"largeur": 1080, "hauteur": 1920}` for 9:16).

Tell the user what is missing for the chosen family: for example, no shot of the whole object (no reveal possible), no wide shot (no landing), a single person for an ensemble documentary. These are shots to film, not flaws to hide.

## Step 2b — The composed edit (instead of steps 2 to 4)

When the images are already made (a demo in chapters, scenes rendered by `sebmake-motiondesign-likeapplepls`, a film cut into parts) and they need to be assembled with a voice-over, subtitles, music and sound effects, there is no footage to choose from. Write `plan.json` (format in the header of `compose_montage.py` and `montage-spec.md` § 2.8), then:

```bash
python3 "$SKILL/scripts/compose_montage.py" plan.json                 # → montage.json (+ montage.srt if "sous_titres": "auto")
python3 "$SKILL/scripts/filmcraft_build.py" montage.json --simulation
```

- **Chapters** end to end on V1, hard cut, picture only; one marker per chapter.
- **Voice-over**: one file per sentence, at the moment the picture calls for it (the time comes from the composition that made the picture, never from a time retyped by hand). `compose_montage.py` reports two voice lines that overlap and a voice line that runs past the end.
- **Subtitles**: the user's SRT, or `auto`: one subtitle per sentence, taken from the voice text.
- **Music**: `niveau_db`, `fondu_sortie_s`, `decalage_s` (where it starts in the file), and `attenuation_db`: FilmCraft ducks it by that much under the voice (Essential Sound: voice as "dialogue", music as "music", ducking generated as volume keyframes). 12 dB is a good start (convention).
- **Sound effects**: each at its own time, on A3.

**The voice-over.** If the user has voice files, use them. Otherwise, the skill can make them:

```bash
python3 "$SKILL/scripts/voix.py" etat                       # is edge-tts there?
```

- **edge-tts missing**: recommend it, in a question (AskUserQuestion): "For best results, would you like to install edge-tts? Natural, free voices, internet required." Choices: install edge-tts (recommended); a macOS voice, robotic, for a draft; I have my own voice files; no voice-over. Only with the user's consent: `python3 -m venv ~/.venv-sebmake-voix && ~/.venv-sebmake-voix/bin/pip install edge-tts`.
- **Text first**: the sentences are the user's, or suggested and marked "to approve"; nothing is spoken before the user agrees.
- **Audition**: `voix.py audition phrases.txt --voix Vivienne,Denise,Henri,Remy,Eloise --sortie audition/`; the user picks by ear. The short names are French voices; a full edge-tts name (`xx-XX-…Neural`, for example an English voice) is passed as is.
- **Generation**: `voix.py generer phrases.txt --voix <choice> --sortie voix/` → one file per sentence and `voix/voix.json` (length, time of each word). The lengths place the sentences without overlap; the word times put a motion or a click on the word that announces it.
- edge-tts goes through an online Microsoft service, free but unofficial: say so if the film leaves the company. The macOS voice does not give word times.

Show the track table (what goes where, from when to when) and what `compose_montage.py` reports before building. Then step 5.

## Step 3 — The edit plan, shown first

Read `references/grammaire-montage.md`: § 1 to 3 once per conversation, then the family's section. Choose the form from the footage (§ 2); say which one. In a documentary, choose the speech first: which takes, in what order, in which chapters (`ordre`, `chapitre` in `paroles`). Never cut speech to make it say something else.

Then run the first assembly. It sends nothing to any software:

```bash
python3 "$SKILL/scripts/assemble.py" rushes.json --famille produit [--schema revelation_tardive] \
        [--duree 32] [--musique musique.wav|aucune] [--fps 25] [--tc-debut 00:00:00:00]
```

It writes `montage.json` and `montage.annotations.json`, and prints the shot table. **Show the plan before building**, as a readable table:

| # | Beat | From → to | What we see (footage) | Text | Rule |
|---|---|---|---|---|---|
| 1 | opening | 0:00.0 → 0:01.0 | black | — | P3, observed 13 out of 16 |
| 2 | hook | 0:01.0 → 0:04.5 | the material comes out of black (`r03`) | — | P4 |

Under the table: the chosen form and why; what `journal` reports (missing footage, shortened dissolves, missing text); the `controle` measurements off target, with the reason; the conventions taken (length outside the observed range, 9:16, chapters); what will need doing by hand (black-and-white grade, widescreen format, reframing to 9:16 or 1:1, credits). **Wait for the user's approval** or changes before step 5.

## Step 4 — `montage.json`

Apply the changes at the source: in `rushes.json` (`role`, `note`, `prises`, `meilleur_s`), or through the `assemble.py` options (`--schema`, `--duree`, `--musique aucune`), then rerun. Edit `montage.json` by hand only for fine tuning: the `_img` fields are authoritative, each shot starts where the previous one ends, and `sortie_img − entree_img = duree_img`. The three outputs (`export_xml.py`, `export_edl.py`, `filmcraft_build.py`) refuse an inconsistent edit, a shot that runs past its clip, or a cross dissolve without frames on both sides of the cut.

`assemble.py` exit code: 0 = on target; 2 = timeline produced with deviations (read `journal`, one line per deviation); 1 = unreadable input or invalid command, nothing is written.

## Step 5 — Building

Read `references/logiciels.md` (the section for the chosen software).

**FilmCraft, driven:**

```bash
python3 "$SKILL/scripts/fc.py" etat
python3 "$SKILL/scripts/filmcraft_build.py" montage.json --simulation
python3 "$SKILL/scripts/filmcraft_build.py" montage.json --images controle/ --carte carte-montage.md --capture capture-filmcraft.png \
        --rendre film.mp4 --rapport filmcraft-rapport.json
```

A new project is created, nothing is saved (`--enregistrer` only to a file that does not exist, and only if the user asks). Tracks are named by their role (Picture, Titles and text, Speech and voice, Music, Picture sound and gestures); subtitles go on C1. `--carte` writes the edit map (each track, its role, its items, the generated ducking); `--capture` captures the FilmCraft window with the sequence open (the screen must be on). The C1 subtitles are not burned into the rendered video. Never quit the app. Code 0 = sequence built and read back with no deviation. `--rendre` exports the video over the full length of the edit: a final black is a gap on V1, and an export of the whole sequence stops at the last item, without it. Look at the contact sheet in `controle/` before going further.

**Premiere Pro or DaVinci Resolve:**

```bash
python3 "$SKILL/scripts/export_xml.py" montage.json -o montage.xml --verifier
$PY "$SKILL/scripts/export_xml.py" montage.json -o montage-png.xml --cartons png --verifier   # all text as images
python3 "$SKILL/scripts/export_edl.py" montage.json -o montage.edl --verifier                 # as a fallback
```

Get code 0 from `--verifier` before handing over a file. Give the user the import steps from `logiciels.md` § 3 or § 4, and say that these two programs were not tried when the skill was written.

Export `montage.xml` in every case, even for FilmCraft: it is the input of the review.

## Step 6 — The review, with the same measure

Read `references/critique.md`. The same measure applies to the skill's edit and to the user's.

**The skill's edit.** `assemble.py` printed the exact command. It looks like:

```bash
$PY "$SKILL/scripts/critique_montage.py" montage.xml --famille produit --sous-famille revelation_objet \
    --schema tardif --annotations montage.annotations.json --mesurer-medias [--son musique.wav] \
    [--sous-titres paroles.srt] --sortie critique.md --json critique.json
```

**The user's edit.** In three passes: measure, with `--planche` for a video; look at the contact sheet and write the annotations (shot sizes, reveal, name, text, candidate dissolves); rerun with `--annotations` (`critique.md` § 3 and § 5).

Read the report: verdict, then "What deviates", "Notes", "To check by eye", "Not measured". For each alert, `critique.md` § 6 gives the rule and the move that fixes it. Fix in this order: form, then pacing, then transitions and blacks, then text and sound; rerun the review after each step. Go back to step 4 for a skill edit; give timecoded fixes for the user's edit. Stop at zero alerts, or when each remaining alert has a stated reason (a missing clip, a deliberate choice).

Also watch the film, or at least the whole contact sheet: the review sees neither a good match cut, nor the meaning of a sentence, nor the emotion on a face.

## Step 6b — Show the edit, then keep going

The user must be able to **understand how the edit is built** and pick it up in FilmCraft. Show them the FilmCraft screenshot and the edit map, then explain in a few lines: V1 carries the picture, chapter by chapter; A1 each sentence at its time; A2 the music and the volume curve that ducks it under the voice; A3 the gestures; C1 the subtitles; the markers, the structure.

Then **the loop goes on**: the user changes things by hand in FilmCraft (a shortened shot, a moved sentence, quieter music) or asks for a change. Read the sequence back (`python3 "$SKILL/scripts/fc.py" inspecter`, or an XML export read by `lire_timeline.py`), say what changed, carry it into `montage.json` (or `plan.json`), rebuild in a `TEST-` project, measure and review again. Nothing the user did by hand may be lost on the next pass.

**Keeping the project**, only when asked: `--enregistrer <folder>/<name>.fcproj`, a new file, never over an existing one.

## Step 7 — Handover

Hand over the work in a short message:

1. **the files**: `montage.json` (and `plan.json` for a composed edit), `montage.xml` (and `.edl`), or the name of the FilmCraft project and sequence; the check contact sheet; the edit map and the screenshot; `critique.md`;
2. **the film in one sentence**: family, form, length, number of shots;
3. **the review verdict** and the deviations kept, each with its reason;
4. **to do by hand**: text to place (markers), grading, widescreen format, reframing to 9:16 or 1:1 (no export reframes), media to relink, music level;
5. **to provide for a better version**: the shots to film, the missing text;
6. in one line: the conventions taken, and that Premiere Pro and DaVinci Resolve were not tried here;
7. for what comes next: edit `rushes.json` or `montage.json` and rerun; a change made in the XML is lost on the next export.

For a review only: the verdict, the 3 to 5 deviations that matter with their move and timecode, what matches, what could not be measured (`critique.md` § 9).

## Reminders

- **The grammar, never the brand.** No Apple image, sound, logo or font; no line from the films, even translated; no signature (no mention of the camera or software used to shoot). Never name a film from the corpus by its title: say "the object reveal films".
- **Music provided or none.** A file from the user, who holds the rights. Never music searched for, downloaded, generated or taken from a library.
- **Voice provided, or synthesized with consent.** The user's voice files; otherwise `voix.py` (edge-tts recommended, installed only if the user wants it), after the user approves the text and the voice.
- **A change made by hand is never lost**: read back (`fc.py inspecter`, `lire_timeline.py`), carried into `montage.json` or `plan.json`, told to the user.
- **No invented text, figure or testimonial.** Names and roles of the people filmed, with their consent. A figure on screen only if it is said in the footage or provided with its source.
- **Hard cut by default**: the cross dissolve stays a chosen exception (G1, G2).
- **Normal speed**: no slow motion, no speed-up to hit a length.
- **The user's project**: nothing is saved, closed or quit without the user asking; a save goes to a new file; in FilmCraft, a test carries the `TEST-` prefix.
- **State the limits**: what is convention, what is not measured, what was not tried.

## Reference files: when to read them

| File | When |
|---|---|
| `references/grammaire-montage.md` | Step 3: § 1 to 3 once, then the family's section (§ 4 to 7), sound (§ 8), length and format (§ 9). Step 6: to understand a rule cited by the review. |
| `references/critique.md` | Step 6: run the review, write the annotations, go from a check to a move (§ 6), deliver the review (§ 9). |
| `references/logiciels.md` | Step 5: FilmCraft (§ 2), Premiere Pro (§ 3), DaVinci Resolve (§ 4), EDL (§ 5). Step 6: export a retouched timeline (§ 6). |
| `references/montage-spec.md` | Steps 2 and 4: the fields of `rushes.json` and `montage.json`, the families and schemas, the FilmCraft command table, the glossary of French identifiers. Step 2b: the composed edit (§ 2.8). |
| `scripts/voix.py` | Step 2b: synthesized voice-over (edge-tts recommended, macOS `say` as a fallback): status, audition, generation with word times. |
| `scripts/compose_montage.py` | Step 2b: `plan.json` (chapters, voice-over, subtitles, music, sound effects) → `montage.json`. |
| `references/cibles/<famille>.json` | The corpus measurements, with their counts. Read by the review; open one for a precise value. |
| `scripts/gabarits.json` | The `assemble.py` build targets, each with its basis or "convention". |
