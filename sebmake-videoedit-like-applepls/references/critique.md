# Reading a review report, and fixing

This file says how to run `scripts/critique_montage.py`, read its report, fill in what the calculation does not see, and go from an alert to an editing move. The rules cited (G, P, A, T, BA, U) are in `grammaire-montage.md`; the thresholds, in `cibles/<famille>.json`.

## Contents

1. Two uses, one measure
2. What to give the review
3. The three-pass method
4. Reading the report
5. Writing the annotations
6. From check to rule to move
7. Fixing: in what order, and where
8. What the review does not see
9. Giving the review to the user

---

## 1. Two uses, one measure

- **Review the user's edit**: they bring a rendered video, or the timeline exported from their software (FCP7 XML, EDL). The review measures it against the films of its family.
- **Check what the skill built**: after `assemble.py` and the export, the same review measures the result. It is the same measure in both cases: an edit made by the skill gets no free pass.

The review reads videos the way the corpus was read: 29.97 frames per second, reduced image, same thresholds for cuts, dissolves and blacks. On one corpus film (33.4 s), it finds the 12 shots of the breakdown, at the same lengths.

**What a verdict is worth.** The review was run on 46 of the corpus films themselves: 42 come out "on target"; the other 4 deviate because of their bounds or a gap in the breakdown. So it does not cry wolf on the films that set the targets. It does not prove that it finds every flaw in an edit.

---

## 2. What to give the review

| Input | What it brings | What is missing |
|---|---|---|
| **Rendered video** (any extension ffmpeg reads) | shots, cuts, blacks, fades to black, motion, color, black and white, black bars, likely title cards, track sound | cross dissolves are only **candidates**; text placed over a picture is not seen |
| **FCP7 XML** ("xmeml", exported from Premiere Pro, DaVinci Resolve or FilmCraft) | **declared** shots, transitions and text | motion and color: only with `--mesurer-medias`, if the source files are on the machine |
| **CMX3600 EDL** | shots, dissolves, blacks | a single video track; no text (a title card is read as a black); its frame rate (`--fps`) |

The FCPXML format (recent Final Cut Pro) is not read: an FCP7 XML is needed.

And, depending on the family:

- `--famille`: `produit`, `ouverture`, `documentaire`, `bandeannonce` (accepted aliases: `bande_annonce`, `usage`, `produit_revelation`…).
- `--sous-famille`: product `revelation_objet` (default), `logiciel`, `materiaux_voix_off`, `usage_gamme`; opening `ouverture` (default), `sketch`, `cloture`, `hommage`, `transition_decor`, `clip`; documentary `pose` or `choral` (default: deduced from the median shot); trailer `oeuvre`, `catalogue_par_blocs`, `catalogue_mele` (default), `usage`.
- `--schema` (product): `tardif` (late reveal) or `des_le_debut` (object from the start).
- `--sous-titres F.srt|F.vtt`: the speech. Without them, the speech checks are "not measured". Documentary, trailer, sketch: ask for them.
- `--son FILE [--son-debut S]`: the sound to measure if the source has none (a timeline). Without sound, the music checks are "not measured".
- `--debut S --fin S`: the bounds of the film inside a longer video.

---

## 3. The three-pass method

The analysis scripts need numpy and Pillow (the environment from `SKILL.md`, called `$PY` here).

**Pass 1: measure, and output a contact sheet.**

```bash
$PY "$SKILL/scripts/critique_montage.py" film.mp4 --famille produit \
    --planche critique-planche.jpg --sortie critique.md --json critique.json
```

**Pass 2: look.** Read the contact sheet (one thumbnail per shot, and 5 thumbnails around each candidate dissolve), then the "To check by eye" section of the report. Write the annotations (§ 5): the size of each shot, the reveal, the name, the text, the decision on each candidate dissolve.

**Pass 3: rerun with the annotations.**

```bash
$PY "$SKILL/scripts/critique_montage.py" film.mp4 --famille produit \
    --annotations annotations.json --sortie critique.md --json critique.json
```

The final report should no longer have important "to check" items. Exit code: 0 on target, 1 deviates, 2 error.

**For an edit built by the skill**, `assemble.py` already writes `montage.annotations.json` (shot sizes, reveal, name, text: what the edit knows) and prints the exact command. It applies to the raw export:

```bash
$PY "$SKILL/scripts/critique_montage.py" montage.xml --famille produit --sous-famille revelation_objet \
    --schema tardif --annotations montage.annotations.json --mesurer-medias \
    [--son musique.wav] [--sous-titres paroles.srt] --sortie critique.md --json critique.json
```

- `--mesurer-medias`: without it, motion, still images and black and white stay "not measured" (check MV).
- `--son`: the user's music, if it starts on the first frame of the timeline (otherwise `--son-debut`).
- `--sous-titres`: if the speech in `montage.json` has its text, write an `.srt` from the `paroles` block (start = `debut_img`, end = `debut_img + duree_img`, at the edit's frame rate). Without text, write "speech": the lengths are enough for every check except the word count of spoken lines (B11).
- After a change in the software, the `assemble.py` annotations no longer hold: export the timeline again and redo them by eye.

---

## 4. Reading the report

### 4.1 Its shape

1. The title, then one line: family, context (subfamily, schema or regime), source (video, XML, EDL), **verdict** ("on target" = no alert; otherwise "deviates (N alerts)").
2. The "Measured" line: length, picture shots, blacks, title cards, median shot (p10, p90), shots per minute, share of hard cuts, opening black.
3. The counts: matching, alerts, notes, to check, not measured.
4. The sections, in this order: **What deviates**, **Notes**, **To check by eye**, **What matches**, **Not measured**, **Not applicable**. Each check gives its ID, the measurement, the target, the corpus basis (N out of M), the source, and often a **fix with timecode** (`HH:MM:SS:FF` at the edit's frame rate, plus seconds).
5. The "Measured timeline": no., in point, length, what (picture, black, title card, solid color), incoming transition ("candidate" if a dissolve was found by calculation), motion, annotation.

### 4.2 The levels

| Level | What it means | What to do |
|---|---|---|
| **alert** | no corpus film does this (rule seen N out of N, or value outside the observed range) | fix it, or say why it is deliberate |
| **note** | possible, but only a minority of the corpus does it, or a convention threshold | say so; fix it if it is a flaw and not a choice |
| **to check** | the measurement depends on an uncertain calculation or a missing annotation | look, then annotate (§ 5) |
| **not measured** | a source is missing (subtitles, sound, annotations, source files); the report says which | provide it, or tell the user |
| **not applicable** | the check does not apply (a oner, a name spoken by a speaker…) | nothing |

An alert is not a lapse of taste: it is a gap from what all the measured films do. A deliberate choice (a reveal film in black and white on purpose) is kept, and stated.

### 4.3 The sources, from most to least reliable

| Source | From | Confidence |
|---|---|---|
| eye | annotations written after looking | always wins over calculation |
| declared | transitions, blacks and text written in the XML or EDL | reliable, except text in an EDL (absent) |
| subtitles | speech | upper bounds: a subtitle often runs past the voice |
| sound | level, attacks, tempo | voice and music mixed |
| calculation | breakdown of the video | shots and blacks almost certain (on very flat images, a cut can still be missed: the contact sheet shows it); cross dissolves and title cards to confirm |

In the corpus, the calculation proposed 225 candidate dissolves (cross, to black or to white) for 54 real ones: a dissolve found by calculation stays "to check" until an annotation confirms it. Check **V1** lists the shots whose first and last frames no longer have anything in common: a dissolve or a wipe may have been missed there.

---

## 5. Writing the annotations

A JSON file, every key optional. Example for a film about a cast-iron teapot:

```json
{
  "sous_famille": "revelation_objet",
  "schema": "tardif",
  "revelation": 24.5,
  "nom": [30.0, 32.4],
  "codes": "N1211222213",
  "plans": {"7": {"valeur": "serre", "type": "objet"}},
  "plans_par_temps": [{"t": 12.3, "valeur": "detail", "type": "objet", "objet": true, "visage": false}],
  "textes": [{"type": "nom", "debut": 30.0, "fin": 32.4, "mots": 1, "place": "centre", "boite": false}],
  "transitions": {"18.52": "F"},
  "ajouts": [{"t": 6.75, "type": "fondu_enchaine"}]
}
```

| Key | What it says |
|---|---|
| `revelation` | start, in s, of the shot that shows the whole object for the first time |
| `nom` | `[start, end]` of the written name, or `{"type": "dit_par_orateur"}` (spoken by a speaker) |
| `fermeture` | trailer: start of the closing (s) |
| `ouverture_a_froid`, `fiction_narree` | opening: `true` if deliberate (cold open, narrated fiction; the entry check and the speech share adapt) |
| `codes` | one value per shot, in report order: product `1` detail, `2` tight, `3` whole, `4` wide, `A` abstract, `N` black, `T` text; documentary `D TG G R M L`; trailer `S R M L T N A X`; opening `S M E L T N` |
| `plans` | by shot number in the report: `valeur` and `type` |
| `plans_par_temps` | the shot that contains time `t`: `valeur`, `type`, `personne`, `objet`, `visage`. Safer than numbers when the breakdown changes between passes |
| `textes` | each text seen: `type` (`nom`, `phrase`, `question`, `these`, `chiffre`, `explicatif`, `slogan`, `date`, `logo`, `titre_bloc`, `bandeau`, `mot`, `carton`), `debut`, `fin`, `mots`, `place` (`centre`, `visage`, `fin_de_bloc`), `boite` |
| `transitions` | decision on a candidate dissolve (within ± 0.35 s of the transition): `T` true, `F` false, `C` a cut, `U` unsure, `B` dip to white |
| `ajouts` | a transition seen by eye that the calculation did not find: `fondu_enchaine`, `volet`, `fondu_au_noir`… |

Accepted shot sizes: `detail`, `tres_gros`, `gros`, `serre`, `rapproche`, `moyen`, `ensemble`, `entier`, `large`, `abstrait`, `noir`, `texte`. Types: `image`, `entretien`, `personne`, `illustration`, `objet`, `carton`, `titre`, `nom`, `logo`, `noir`. (Meanings in the glossary of `montage-spec.md`.)

Once `textes` is given, only those texts count for the name and for excess text (K6, K11, K12, K13): an untyped title card is no longer taken for the name.

---

## 6. From check to rule to move

The report IDs are not the rule IDs. These tables bridge them: for each check, the rule in `grammaire-montage.md` that explains it, and the move that fixes an alert or a note.

### 6.1 Product and reveal (C, K)

| Check | Rule | Fixing move |
|---|---|---|
| C2 length | P2 | shorten the build-up; past 60 s without voice, split into chapters of one idea each |
| C3 open on black | P3 | add 0.5 to 1.5 s of black; bring the first image out of black with a 0.7 to 1.3 s fade |
| C4 first shot length | P4, § 4.2 | lengthen the first shot toward 3 s (2.3 to 7.9 s) |
| K1 reveal position | P11 | move the first whole-object shot to between 69 and 82%; remove the whole shots before it |
| K2 first shot whole | P4 | open on a setting, a material or a detail |
| K3 median shot, K4 shots per minute | P6, P9 | shorten (or lengthen) the build-up shots toward 2 s; software can cut faster |
| K5 one shot of at least 5 s | P13 | hold the reveal or the last shot |
| K6 last shot held | P12 | hold the last picture shot 6 to 8.5 s, or end on the name title card |
| K7 cross dissolves | G2, P7 | replace with cuts; keep at most one, on a key shot |
| K8 dissolve from black in the last third | P7 | hard cut |
| K9 details and tight shots | P5 | replace wide shots in the build-up with details and parts |
| K10 last shot whole | P12 | end on the whole object, alone |
| K11 name position and length | P15 | place the name between 83 and 96% of the length, 1.3 to 4.5 s |
| C16 write the name | P16 | add the name title card (text provided by the user) |
| K12 excess text | P19, G6 | remove explanatory or numeric title cards; one text at a time |
| K13 logo, date or slogan at the end | P18 | end on the object, or the name then a black |
| K14 inner blacks | P14 | remove the blacks in the middle, or bring them down to 0.3 to 0.9 s |
| K15 still images | P10, G4 | replace still shots with slow-moving shots |
| K16 voice-over | P20 | leave 4 silent seconds at the start, 2 to 3.5 s at the end; voice over two thirds of the time at most |
| K18 film without voice over 60 s | P2, P23 | shorten, or use chapters |
| K19 black and white | § 9.3 | restore color (the product is never desaturated: 0 out of 16) |
| K20 cuts on every beat | G8, P22 | shift the ordinary cuts; only lock the exit from black, the reveal and the name to the beat |

### 6.2 Documentary and testimonial (D)

| Check | Rule | Fixing move |
|---|---|---|
| D1 median shot, D2 cuts per minute | § 6.1, T11 | calm: shots around 2 s; ensemble: around 1.2 s. First check the regime (`--sous-famille`) |
| D3 pacing shape | T11 | calm: slow down the end, longest shots at the end; ensemble: speed up the end |
| D4 shot of at least 5 s in the last fifth | T14 | hold a wide shot at the end |
| D5 transitions other than cuts, chapter blacks | T10 | hard cut; a single black (0.4 to 1 s) to change chapter |
| D5b dissolve between two people shots, D5c cross dissolves | G2, T10 | replace with a cut |
| D6 speech share | T3 | too much: leave silences and a breathing space; too little: tighten the takes |
| D7 breathing spaces | T3 | add 3 to 9 s of music alone over pictures, about one every minute and a half |
| D8 speech on the face | T4 | cover two thirds of the voice with illustration shots |
| D9 entry through the voice | T5 | let the first person be heard over an illustration, face 1.5 to 4.7 s later |
| D10 long interview before the end | T12 | cut the interview, cover with an illustration; keep shots over 5 s for the end |
| D11 interview in a wide shot | T7 | use a tighter shot size |
| D12 same person twice | T7 | the second shot tighter, or an illustration between the two |
| D13 camera on the interview | T8 | choose a locked-off take |
| D15 lower thirds | T6 | at the bottom, on the empty side, small, no box, 2 to 3.5 s, on the first face |
| D16 message title cards | T17 | at most 3, small, centered, 12 words at most, no box |
| D17 first speech, D17b opening black, D17c calm sound | T13 | open with black and calm; first speech between 3 and 17 s |
| D18 last speech, D18b shot held at the end | T14 | end the speech 1 to 10 s before the end; hold the last shot 5.7 to 8.1 s |
| D19 final burst of faces | T14 | put the works or the product in the final burst, not the faces |
| D20 sound between sentences | § 8 | leave the music or the room sound under the speech silences |
| D21 black and white | T18 | the whole film, or the people in black and white and the screens in color |

### 6.3 Trailer and usage (B)

| Check | Rule | Fixing move |
|---|---|---|
| B1 median shot | BA2 | tighten toward 0.9 s |
| B2 last third faster | BA2 | shorten the shots up to the peak |
| B3 peak position, B4 peak shots | BA3 | cut 10 s of shots at 0.6 s around 80% of the length |
| B5 closing | BA10 | closing of 6 to 17% of the length: black, button, black, title |
| B6 last item | BA10 | end on the title or the logo, 2.5 to 4.8 s, out of black |
| B7 hard cuts, B8 cross dissolves | BA4 | replace effects with cuts; keep the dissolve for a title that gives way to the picture |
| B9 wide shots in the first third | BA6 | open on wide shots (at least 35%) |
| B10 still shots | BA15 | shots that move, more and more |
| B11 long spoken lines | BA7 | cut lines to 3 s and 10 words |
| B12 speech at the peak | BA3 | silence the peak; the music carries it |
| B13 opening in black | G3, § 7.1 | add a black of about 0.6 s |
| B14 block titles | BA11 | the title at the head of the block, about 1 s |
| B15 text in a usage film | U3 | move the text into the last 10% |
| B16 object on screen | U2 | the object in one shot out of three or four |
| B17 cuts on the beat | G8 | allowed at the peak only; elsewhere, cut on speech and action |

### 6.4 Opening and mood (O)

| Check | Rule | Fixing move |
|---|---|---|
| O0 length | § 9.1 | 60 to 120 s (convention; observed 65 to 143 s) |
| O1 entry, O1b threshold | A1, A2 | a threshold of black and silence, then a first shot of 5 to 10 s (unless a deliberate cold open: annotate it) |
| O2 median body shot, O3 body pacing | A3 | body around 1.3 to 1.5 s, without slowing down before the landing |
| O4 speed peak | A5 | 5 shots of 0.4 to 0.7 s between 60 and 80% |
| O5 landing | A6 | 3 to 5 shots that get longer, then a last shot of 5 to 11 s |
| O6 tight ending | A7 | end wide, on the place or the person |
| O7 cross dissolves | A8 | cuts; a dissolve only from animation to live action |
| O8 black in the middle | A9 | keep black for the entry |
| O9 text in the middle or more than 2, O10 title card too short | A10, G7 | text at the threshold or at the end; about 0.5 s per word |
| O11 cuts on the beat | G8 | lock the peak, the landing and the final black to the music, not every cut |
| O12 sound high point | A5, § 8 | let the music build until after 60% |
| O13 ending without speech, O13b speech share | A11 | end on 15 to 30 s without speech; 30% speech at most |
| O15 lower thirds | § 5.4 | name people after the first third |
| O16a length, O16 still shots, O17 held arrival | § 5.5 | 15 to 30 s, continuous motion, arrival held 7 to 11.5 s |

### 6.5 Common

| Check | Move |
|---|---|
| V1 transitions possibly missed | look at those shots; write the dissolve or the wipe in `ajouts`, or nothing |
| MV motion not measured | rerun with `--mesurer-medias`, or review the rendered video; "source timecode outside the file": the timeline points to other files than the ones edited |

---

## 7. Fixing: in what order, and where

**The order.** Fix first what carries the film, then the pacing, then the details:

1. **the form**: right family and schema, position of the reveal, of the peak, of the name or title, the ending (K1, K2, K6, K11, B3, B5, B6, O5, D18…);
2. **the pacing**: median shot, cutting rate, pacing shape, long shot (K3, K4, K5, D1 to D4, B1, B2, O2, O3…);
3. **transitions and blacks** (K7, K8, K14, D5, B7, B8, O7, O8…);
4. **text and sound** (K12, K13, D15, D16, B11, B12, O9, O13…).

A fix to the form often moves everything else: rerun the review after each step rather than at the end.

**Where to fix.**

- **An edit made by the skill**: fix the input and rebuild. In `rushes.json`, change `role` (for example `revelation`, `fin`, `pic`), `note`, `prises` or `meilleur_s`; or rerun `assemble.py` with another `--schema` or another `--duree`. Edit `montage.json` by hand only for fine tuning, keeping the `_img` fields consistent (each shot starts where the previous one ends; `sortie_img − entree_img = duree_img`): the exports refuse an inconsistent edit, or a shot that runs past its clip (code 1). Then export again with `--verifier`.
- **The user's edit**: give the fixes in editor's words, with the report's timecode: "lengthen shot 14 (00:00:24:12) to 7 s", "replace the dissolve at 00:00:18:13 with a cut", "move the name to 00:00:30:00". The user makes them in their software, exports, and the review runs again.

**What you never do to pass a check**: invent a text, a name, a figure or a testimonial; add music; stretch a shot in slow motion to reach a length; add a logo that is not the user's. If a clip is missing (no whole object filmed, no wide shot), say so: it is a shot to film, not a flaw to hide.

---

## 8. What the review does not see

- **Cross dissolves**: lower bound, only candidates by calculation; wipes are not calculated (declared or annotated). In one test, 3 dissolves between 0.5 s shots were not found from the video alone.
- **Title cards**: found by a heuristic (flat background, thin strokes). A white screen can pass for a title card; text placed over a picture is not seen. Small light text on black can be read as a black, and a streak of light on black as a title card: in pass 1, C4, C16 and O1 need confirming on the contact sheet. Always to confirm.
- **Shot sizes, subject, reveal**: by eye only. The whole object is only looked for in the first shot (K2) and at the annotated reveal time (K1): a wide shot where it appears whole, even small, before its reveal is seen only by eye (in one test, the whole lamp at 21% of the length, revealed at 76%, raised no alert).
- **The reveal position (K1)** has a convention tolerance around the corpus's 69 to 82%: under 60%, alert; 60 to 66%, note; 66 to 87%, no remark; above 87%, note.
- **The opening black of a video**: a very dark first shot (a streak of light coming out of black) lengthens the black that is read (1.8 s read for 1.1 s placed in one test, C3); the contact sheet shows it.
- **Speech**: only through subtitles; the sound does not separate voice and music.
- **A silent audio track** (a render without music often carries one): read as no sound; the sound checks stay "not measured".
- **The camera**: only its slides. A zoom or a rotation comes out as "locked-off", on a video as on an XML whose footage is measured.
- **What cannot be counted**: a good match cut on action, the meaning of a sentence, the story of a sketch, the emotion on a face, whether a piece of music is right. Watch the whole film before delivering the review.

---

## 9. Giving the review to the user

Don't paste the raw report. Give, in simple sentences:

1. **the verdict** in one line: on target, or deviates, with the number of alerts;
2. **the 3 to 5 deviations that matter**, in the order of § 7: what is measured, what the films of the family do (with the N out of M count), the move and its timecode;
3. **what matches**, in one line;
4. **what is left to check or was not measured**, and what should be provided (subtitles, sound, source files);
5. the path of the full report (`critique.md`) and of the contact sheet.

A note is not a fault: say "possible, but rare" and leave the choice. Never name a corpus film by its title or its brand: say "the object reveal films", "the catalog trailers".
