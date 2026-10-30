# Format of `rushes.json` and `montage.json`

Two files carry the edit:

- `rushes.json` describes what the user shot: their footage, their music if they have some, the name or title to write. It is the **input**.
- `montage.json` is the **timeline**: the list of shots, in order, with their source, in point, out point, transition and title card. It is the **output** of `scripts/assemble.py` and the input of the three outputs: `export_xml.py` (Premiere Pro, DaVinci Resolve), `export_edl.py` (CMX3600) and `filmcraft_build.py` (FilmCraft).

The JSON keys and the values stored in these files are French identifiers. They stay as they are: the scripts read them. The glossary in § 5 says what each one means.

Ground rules, carried by the format:

- **The grammar, never the brand.** No logo, image or sound from another brand, no Apple font. The logo is the user's, or nothing; the font is theirs, otherwise a common font (Arial for FilmCraft and XML titles; Inter, DejaVu Sans or Arial for title cards rendered as images).
- **Music provided or none.** A local file the user holds the rights to, or `null`. Never music searched for or generated.
- **No invented text.** The name, the closing line, the spoken lines and the lower thirds come from the user. Missing text stays missing; `assemble.py` reports it in `journal`.
- **Paths.** Relative to the JSON file's folder, or absolute. Exports write absolute paths.
- **Times.** In seconds in the `_s` fields, in frames in the `_img` fields. In `montage.json`, **the `_img` fields are authoritative**: the exports read only them. The `_s` fields are there for reading.

---

## 1. `rushes.json`

```json
{
  "version": 1,
  "projet": "TEST-teapot",
  "nom": "Iron",
  "phrase": null,
  "logo": null,
  "police": { "famille": "Inter", "fichier": null },
  "couleurs": { "fond": "#000000", "texte": "#FFFFFF" },
  "musique": "musique.wav",
  "fps": null,
  "format": { "largeur": 1920, "hauteur": 1080 },
  "rushes": [
    {
      "id": "r10",
      "chemin": "r10.mp4",
      "description": "whole teapot, the camera pulls back",
      "valeur": "entier",
      "sujet": "objet",
      "mouvement": "lent",
      "direction": "recul",
      "role": ["revelation"],
      "note": 4,
      "prises": [[0.5, 11.5]],
      "meilleur_s": null
    }
  ]
}
```

### 1.1 Project fields

| Field | Type | Meaning |
|---|---|---|
| `projet` | text | project name; used as the sequence name. For a test in FilmCraft, it starts with `TEST-` |
| `nom` | text or `null` | the product name or film title, as written on screen |
| `phrase` | text or `null` | a written line (product: about 5 words; usage: 3 to 9 words) |
| `these` | text or `null` | documentary: an opening question or thesis (12 words at most) |
| `carton_ouverture` | text or `null` | opening, closing film: a threshold title card (11 words at most) |
| `mots_chocs` | list of texts | catalog trailer: 2 or 3 groups of 1 or 2 words |
| `mention` | text or `null` | trailer for a work: a notice of about 3 words, very small, on black, at the start |
| `logo` | path or `null` | the user's logo, if they provide it (image) |
| `police` | object | `famille` (name of the installed font) and `fichier` (.ttf/.otf path, for title cards as images); without `famille`, FilmCraft and XML titles use Arial |
| `couleurs` | object | `fond` (background) and `texte` (text) of the title cards, as `#RRGGBB` |
| `musique` | path or `null` | the user's music |
| `fps` | number or `null` | timeline frames per second; `null` = that of most of the footage |
| `format` | object | `largeur` (width), `hauteur` (height) of the timeline; 1920 × 1080 by default |

### 1.2 Or the output of `analyse_rushes.py`

`assemble.py` also reads the file written by `analyse_rushes.py` directly (`fichiers` → `prises` blocks). Each detected take becomes a clip (`id` = file name + take number). The measured motion becomes `fixe` (< 10), `lent` (10 to 50), `moyen` (50 to 200) or `fort` (200 and up), the corpus reading bounds. The `a_eviter` zones are removed from the windows. A `naissance_lumiere` moment gives the `accroche` role; the strongest `pic_mouvement` gives `meilleur_s`.

A photo or scan (`.png`, `.jpg`, `.tif`…) found by `analyse_rushes.py` becomes a single take, still, with no motion measurement; its contact sheet is the image itself. A file the analysis cannot read (or a photo added later) is added by hand in a `rushes` list at the root of the same file, with the fields of § 1.3 (`id`, `chemin`, `valeur`, `sujet`…): `assemble.py` then edits the analyzed takes and these clips together, and says so in `journal`. A still image is always edited from its first frame; its length is whatever the edit gives it.

If there is a single sound file in the analysis, it becomes the music, and `journal` says so; if there are several, none is taken by default: specify `--musique`.

The camera states (locked-off, slow, fast, handheld) and the zones to avoid (blur, shake) come from convention thresholds: in one test, a wall whose light changed slowly was read as "handheld", blurry and shaky. The contact sheet decides.

`analyse_rushes.py` never overwrites a file where fields have been filled in by eye: to rerun the analysis (a clip added, a clip reshot), `--fusionner` carries those fields into the new analysis, take by take (same file, start and end within ± 0.1 s), along with those at the root; an annotated take that is no longer found is kept in `annotations_non_retrouvees`, and `assemble.py` reports it.

`valeur` and `sujet` are still to be filled in by eye in this file, take by take, while looking at the contact sheet; `note` (1 to 5) too, if one take is better than another. `notes` is a free comment, added to the shot description: it does not change the rating. Without them, `assemble.py` picks blindly and says so in `journal`. The other fields of § 1.3 (`role`, `personne`, `paroles`…) are added the same way in the take. `nom`, `phrase`, `logo`, `police` are added at the root of the file.

### 1.3 Clip fields

| Field | Values | Meaning |
|---|---|---|
| `id` | short text | unique id (used as the reel in the EDL) |
| `chemin` | path | the video, audio or image file |
| `duree_s`, `fps` | number | read by `ffprobe` if missing |
| `valeur` | `detail`, `serre`, `rapproche`, `moyen`, `entier`, `large`, `abstrait` | shot size. Accepted aliases: `TG`, `tres_gros`→detail, `G`, `gros`→serre, `R`→rapproche, `M`→moyen, `L`, `ensemble`→large, and the codes 1, 2, 3, 4, A from the analyses |
| `sujet` | `objet`, `piece`, `matiere`, `decor`, `lumiere`, `geste`, `ecran`, `personne`, `entretien`, `illustration`, `oeuvre`, `photo`, `archive` | what the shot shows. `objet` + `entier` = the whole object; `piece` = a part or component of the object (a room in a house is `decor`). Accents and capitals are accepted ("Pièce", "œuvre"); any other word is reported in `journal` and counts for no rule |
| `mouvement` | `fixe`, `lent`, `moyen`, `fort` | image motion (camera and subject mixed) |
| `direction` | `avant`, `recul`, `rotation`, `lateral` | direction of the camera move, if any |
| `role` | list | wanted role: `accroche`, `revelation`, `fin`, `gamme`, `pic`, `arrivee`, `bouton`, `signature` |
| `note` | 1 to 5 | quality of the take (3 by default) |
| `prises` | list of `[start, end]` in s | usable windows in the file; by default the whole file minus 0.3 s at each end (convention) |
| `meilleur_s` | number | the moment to keep at the center of the shot |
| `personne`, `fonction` | text | documentary: who speaks, and their role (lower third) |
| `paroles` | list | interview, spoken line: `{"entree_s", "sortie_s", "texte", "ordre", "note", "chapitre"}` (`entree` and `sortie` accepted) |
| `synchro` | object | another angle of the same take: `{"avec": "e01", "decalage_s": 0.0}` |
| `bloc` | text | trailer: the topic of the block (concert, episode…) |
| `titre_bloc` | text | trailer by blocks: the title written at the head of the block |
| `scene` | number | opening, sketch, usage: scene number; the scene order is kept |

---

## 2. `montage.json`

```json
{
  "version": 1,
  "titre": "TEST-teapot",
  "famille": "produit",
  "schema": "revelation_tardive",
  "duree_cible_s": 32.0,
  "duree_s": 32.0,
  "duree_img": 800,
  "format": { "largeur": 1920, "hauteur": 1080, "fps": 25, "tc_debut": "00:00:00:00" },
  "police": { "famille": "Inter", "fichier": null },
  "couleurs": { "fond": "#000000", "texte": "#FFFFFF" },
  "musique": { ... },
  "plans": [ { ... } ],
  "paroles": [ { ... } ],
  "marqueurs": [ { ... } ],
  "controle": [ { ... } ],
  "journal": [ "..." ]
}
```

| Field | Meaning |
|---|---|
| `famille` | `produit`, `ouverture`, `documentaire`, `bande_annonce` |
| `schema` | the form chosen within the family (§ 2.6) |
| `duree_cible_s` | the requested length; `duree_s` and `duree_img` the length obtained |
| `format.fps` | 23.976, 24, 25, 29.97, 30, 50, 59.94 or 60. 23.976, 29.97 and 59.94 are read as 24000/1001, 30000/1001, 60000/1001 |
| `format.tc_debut` | timecode of the first frame of the timeline; `00:00:00:00` by default, `01:00:00:00` for those who edit in Resolve by habit |
| `controle` | the measurements of the resulting edit, each with its target and status (§ 2.7) |
| `critique` | the `critique_montage.py` arguments that match this edit: `famille`, `sous_famille`, `schema` |
| `journal` | what `assemble.py` chose, what is missing, what to check by eye |

Next to `montage.json`, `assemble.py` writes `montage.annotations.json`: the "by eye" annotations for `critique_montage.py --annotations` (size and type of each shot, reveal, name, closing, text), drawn from what the edit already knows. They apply to the raw export; after a change in the software, redo them by eye.

### 2.1 A shot

Shots follow one another on track V1, with no gap: each shot starts where the previous one ends. A black is a shot.

```json
{
  "n": 3,
  "type": "image",
  "temps": "montee",
  "debut_img": 110, "duree_img": 55,
  "debut_s": 4.4, "duree_s": 2.2,
  "source": "r04",
  "chemin": "/absolute/path/r04.mp4",
  "entree_img": 60, "sortie_img": 115,
  "entree_s": 2.4, "sortie_s": 4.6,
  "transition": { "type": "coupe" },
  "carton": null,
  "valeur": "serre", "sujet": "piece", "mouvement": "moyen",
  "son_image": false,
  "notes": "build-up: tighten on the parts (65 to 70% tight shots, observed)"
}
```

| Field | Meaning |
|---|---|
| `n` | order number, from 1 to N |
| `type` | `image` (a clip), `noir` (nothing on screen), `carton` (text on a solid background) |
| `temps` | the beat in the structure: `ouverture`, `accroche`, `montee`, `pic`, `revelation`, `nom`, `fin`, `seuil`, `premier_plan`, `corps`, `atterrissage`, `voix`, `respiration`, `annonce`, `bloc`, `fermeture`, `bouton`, `titre`… |
| `debut_img`, `duree_img` | position and length on the timeline, in frames. `debut_img` of shot n+1 = `debut_img + duree_img` of shot n |
| `source`, `chemin` | the clip (`type: image`) |
| `entree_img`, `sortie_img` | in and out points in the source file, in timeline frames. `sortie_img − entree_img = duree_img` (normal speed only) |
| `transition` | how this shot **starts** (§ 2.2) |
| `carton` | a text placed on this shot (§ 2.3), or `null` |
| `son_image` | `true`: keep the clip's sound under this shot (track A3) |
| `mouvement_mesure` | motion of the edited passage (mean gray difference per second), read from the `analyse_rushes.py` curve; under 10.5, the shot counts as still in `controle`: the review counts still under 10, on its own measurement, close to this one but not equal to it, hence the margin. Absent for a clip described by hand: the `mouvement` label is used instead |
| `personne` | the person in the clip, if any (documentary, closing film) |
| `sync` | `true`: interview shot synced to the speech running under it |
| `notes` | the rule applied, with its count or "convention" |

A source at a frame rate other than the timeline's is played at normal speed: its in and out points are converted to timeline frames.

### 2.2 The transition

The transition is carried by the shot that **starts**. It is read together with the shot before.

| `type` | Shot before | Effect | In the software |
|---|---|---|---|
| `coupe` | any | hard cut | — |
| `fondu` | a picture | cross dissolve, centered on the cut | Cross Dissolve; needs `duree/2` of handle in both clips |
| `fondu` | a black, or nothing | the picture comes out of black, over its first frames | Cross Dissolve at the head (`start-black` alignment) |
| `fondu` | (this shot is a black) | the picture before fades to black, over its last frames | Cross Dissolve at the tail (`end-black` alignment) |
| `blanc` | a picture | dip to white, centered | Dip to White |
| `poussee` | a picture | the next shot pushes the first out, centered | Push |

`duree` is in seconds, `duree_img` in frames. `assemble.py` checks the clip handles; without enough handle, it shortens the dissolve or replaces it with a cut and says so in `journal`. The three outputs redo the check on a `montage.json` edited by hand: a cross dissolve of `d` frames needs `d // 2` frames before the in point of the incoming shot and the rest after the out point of the outgoing shot; otherwise they refuse the edit (code 1) and name the shot.

### 2.3 The title card

```json
"carton": {
  "role": "nom",
  "texte": "Iron",
  "debut_img": 0, "duree_img": 60,
  "place": "centre",
  "taille_pct": 4.5,
  "fond": "noir"
}
```

| Field | Meaning |
|---|---|
| `role` | `nom`, `titre`, `phrase`, `these`, `bandeau`, `titre_bloc`, `mot_choc`, `credit`, `mention`, `logo` |
| `texte` | the text, or `null` for a logo (`logo` = image path) |
| `debut_img`, `duree_img` | position **within the shot** (0 = the shot's first frame) and length |
| `place` | `centre`, `bas_gauche`, `bas_droite`, `haut_gauche` |
| `taille_pct` | cap height as a % of the image height |
| `fond` | `image` (the text is placed over the shot), `noir`, `blanc` or `#RRGGBB` (shot of type `carton`) |
| `deuxieme_ligne` | lower third: the person's role, under the name |

On an `image` shot, the title card goes on track V2, above the picture. A `carton` shot is text on a solid background: nothing on V1 (black) or a solid color, and the text on V2.

### 2.4 Speech

Speech clips are pieces of sound placed on track A1: interviews, spoken lines, voice-over. The picture running over them is chosen separately (voice over an illustration, face afterward).

```json
{
  "n": 1,
  "source": "e01",
  "chemin": "/absolute/path/e01.mp4",
  "debut_img": 143, "duree_img": 139,
  "entree_img": 288, "sortie_img": 427,
  "personne": "Ana",
  "texte": "We always start with paper.",
  "piste": "A1"
}
```

### 2.5 Music and markers

```json
"musique": {
  "chemin": "/absolute/path/musique.wav",
  "debut_img": 0, "entree_img": 0, "duree_img": 800,
  "fondu_sortie_img": 25,
  "reperes": { "debut_son_s": 0.6, "sommet_s": 22.1, "attaques_s": [1.0, 8.0, 16.0, 24.5, 29.0] },
  "piste": "A2"
}
```

- Tracks: speech on A1, music on A2, picture sound on A3. Always the same.
- `reperes`: what `assemble.py` measured in the music (method and thresholds in the script header; `assemble.py --musique F --reperes` shows them alone). The big changes are locked to them; ordinary cuts are not (convention).
- `marqueurs`: `{"debut_img", "duree_img", "nom", "texte"}`. Each title card and each structure beat gets one. The three outputs write them.

### 2.6 Families and schemas

| `famille` | `schema` | For what |
|---|---|---|
| `produit` | `revelation_tardive` | a new object: a world or a material, details, the whole object around 77%, the name |
| `produit` | `objet_des_le_debut` | software, a use, a product range: the object right away, then its uses, then the name |
| `ouverture` | `ouverture` | opening or mood film, sketch (the scene order is kept) |
| `ouverture` | `transition_decor` | passage from one place to another, 15 to 30 s, no text |
| `ouverture` | `cloture` | closing film: title card, faces, faster last third, signature shot |
| `documentaire` | `pose` | little voice, long takes, slower ending |
| `documentaire` | `choral` | many short voices, faster ending, final burst |
| `bande_annonce` | `catalogue_blocs` | several topics, one block and one title per topic |
| `bande_annonce` | `catalogue_mele` | several topics mixed shot by shot, no titles |
| `bande_annonce` | `oeuvre` | a single story, with spoken lines |
| `bande_annonce` | `usage` | an object used by people |

The targets of each schema are in `scripts/gabarits.json`, each with its count (N out of M) or the word "convention", and its source in `references/cibles/`. `python3 assemble.py --verifier-gabarits` compares the two.

Also accepted: families `bandeannonce`, `produit_revelation`, `ouverture_ambiance`, `documentaire_temoignage`; schemas `tardif`, `des_le_debut`, `catalogue_par_blocs`, `sketch` (= ouverture), `hommage` (= cloture). These are the `critique_montage.py` names.

### 2.7 The check

`controle` is a list of measurements made on the resulting timeline:

```json
{ "id": "plan_median", "mesure": 2.2, "cible": [1.0, 3.6], "statut": "observe", "base": "14 films that cut: 1.0 to 3.6 s", "ok": true }
```

`ok` is `true`, `false`, or `null` when the measurement is only a reference point (a single film measured). A measurement off target blocks nothing: it says where the edit deviates from the measured films, and `journal` says why (often: not enough clips of the right kind). Still shots are counted with a margin over the review (`mouvement_mesure` under 10.5, while the review counts under 10 on its own measurement, close but not identical): `part_plans_fixes` (product, trailer, at most 25%) and `plans_fixes` (transition between two places, none) come out as deviations where the review would raise an alert. Without a shot of the whole object, a late reveal has no shot: `revelation_objet_entier` comes out as a deviation, and nothing is announced to the review as a reveal.

`journal` also states each fallback: a requirement dropped for lack of a clip that fills it, already-edited frames replayed for lack of free room elsewhere, a black placed "for lack of footage".

---

### 2.8 The composed edit

`compose_montage.py plan.json` writes an ordinary `montage.json` (one `image` shot per chapter, hard cut; one speech clip per sentence; one marker per chapter; `schema: "compose"`), plus three fields that only `filmcraft_build.py` reads:

```json
"musique": { "chemin": "…/musique.wav", "debut_img": 0, "entree_img": 0, "duree_img": 600, "fondu_sortie_img": 60,
             "niveau_db": -6, "attenuation_db": 12, "piste": "A2" },
"sons": [ { "n": 1, "nom": "clic", "chemin": "…/clic.wav", "debut_img": 210, "entree_img": 0, "duree_img": 2, "piste": "A3" } ],
"sous_titres": "…/montage.srt"
```

| Field | Meaning |
|---|---|
| `musique.attenuation_db` | how much the music ducks under the speech. FilmCraft: speech as "dialogue", music as "music" (Essential Sound), `ducking.reduceDb`, then `generateDucking` places the volume keyframes |
| `sons` | one-off sound effects on A3, each at its time (as "sfx" when ducking is requested) |
| `sous_titres` | an SRT imported onto the C1 subtitle track; it is not burned into the rendered video |

The `plan.json` input (format in the header of `compose_montage.py`):

```json
{"titre": "TEST-demo", "famille": "bande_annonce", "format": {"largeur": 1920, "hauteur": 1080, "fps": 30},
 "chapitres": [{"fichier": "chapitres/1.mp4", "nom": "Opening"}],
 "voix": [{"t": 3.0, "fichier": "voix/v1.mp3", "texte": "The spoken sentence."}],
 "sous_titres": "auto",
 "musique": {"fichier": "musique.wav", "niveau_db": -8, "attenuation_db": 12, "fondu_sortie_s": 2, "decalage_s": 0},
 "sons": [{"t": 7.0, "fichier": "clic.wav", "nom": "clic"}]}
```

The FCP7 XML and the EDL carry neither the one-off sound effects, nor the ducking, nor the subtitles: redo them in Premiere or Resolve (import the SRT, lower the music under the voice).

## 3. What the outputs can do

| Element | FCP7 XML (Premiere, Resolve) | CMX3600 EDL | FilmCraft |
|---|---|---|---|
| picture shots, in points, out points | yes | yes (one video track) | yes |
| blacks | gaps on V1 | `BL` events | gaps on V1 |
| dissolves, dip to white, push | yes | dissolves and white: dissolve `D`; push: cut + comment | yes |
| title cards on black | "Text" generator on V2 + marker | comment line | native title, editable |
| text placed over a picture (lower third, title over a setting), color backgrounds | marker only (`--cartons texte`, default), or PNG image on V2 (`--cartons png`, needs Pillow) | comment line | native title; color background as a color matte on V1 |
| speech, music | A1, A2 | `A`, `A2` events | A1, A2 |
| markers | yes | comments | yes |

Why text over a picture is not a generator by default: the FilmCraft importer does not read the FCP7 "Text" generator and replaces it with black video, which hid the face under the lower third (seen in testing). On a black background this does not show; over a picture, it does. `--cartons generateurs` forces it everywhere, at your own risk.

Premiere Pro and DaVinci Resolve are not installed on the machine where the skill was written: the XML and the EDL are checked there by reading back (`--verifier`), by the independent reader `lire_timeline.py`, and by import into FilmCraft (which reads both formats and rebuilt each shot to the frame), not in those two programs.

## 4. FilmCraft

`filmcraft_build.py montage.json` builds the sequence through the control channel (`fc.py`), then reads it back through `sequence.inspect`. Commands used, all sent through `engine.execute`:

| Step | Command | Useful parameters |
|---|---|---|
| project | `file.newProject` (default) or `project.inspect` (`--projet ouvert`) | `name` |
| bin, import | `file.newBin`, `file.import` | `name`; `paths`, `bin` |
| sequence | `file.newSequence`, `sequence.open` | `name`, `width`, `height`, `fps`, `video: 3`, `audio: 3` |
| shots, speech, music | `timeline.place` | `item`, `track` (`V1`, `V2`, `A1`, `A2`, `A3`), `time`, `sourceIn`, `duration` in ticks, `insert: false`, `video`, `audio` |
| color background | `file.newColorMatte` then `timeline.place` | `color`, `seconds` |
| title cards | `graphics.newText`, `graphics.set`, `graphics.align` | `text`, `size`, `font`, `seconds`, `track: 1` (= V2), `time`; `props.align`, `props.position`, `props.fill_color` |
| music level | `effects.setParam` | `clip`, `effect: 0` (volume), `param: "level"`, `value` in dB |
| transitions | `sequence.applyVideoTransition`, `sequence.applyAudioTransition` | `clip`, `effect` (`cross_dissolve`, `dip_to_white`, `push`, `constant_power`), `frames`, `edge` (`in`, `out`): FilmCraft aligns them itself (centered between two shots, at the start after a gap, at the end before a gap) |
| named tracks | `timeline.setTrack` | `track`, `name` (V1 "Picture", V2 "Titles and text", A1 "Speech and voice", A2 "Music", A3 "Picture sound and gestures") |
| subtitles | `captions.import` | `path`, `name` ("Subtitles") |
| ducking under the voice | `essentialSound.setType`, `essentialSound.set`, `essentialSound.generateDucking` | `clips`, `type` (`dialogue`, `music`, `sfx`); `key: "ducking.reduceDb"`, `value` |
| screenshot (`--capture`) | `ui.screenshot` (a method, not a command) | `path`; window in front, screen on |
| markers | `markers.add` | `target: "program"`, `time`, `name`, `comment`, `durationFrames` |
| check | `sequence.inspect` | `item` |
| check frames | `file.exportFrame` | `path`, `format: "png"`, `target: "program"`, `time`, `sequence` |
| video (`--rendre`) | `file.exportMedia` | `path`, `format: "h264"`, `sequence`, `range: "custom"`, `startSeconds: 0`, `endSeconds` = length of the edit, `wait: true` |
| save (on request) | `file.saveAs` | to a path that does not exist yet, never over an existing file |

Times in ticks: 254,016,000,000 per second. `--simulation` prints the command list, with shortened parameters, without sending anything; `--rapport` keeps the full parameters.

## 5. Glossary of French identifiers

The keys and stored values in `rushes.json`, `montage.json`, `plan.json` and the annotation files are French. They never change: the scripts read them as written (without accents). This table says what each one means.

**Files and top-level keys**

| Identifier | Meaning |
|---|---|
| `rushes`, `rushes.json` | footage, the clips the user shot |
| `montage`, `montage.json` | the edit (the timeline) |
| `plan.json` | the plan of a composed edit (input of `compose_montage.py`) |
| `plans` | shots (list) |
| `paroles` | speech clips (interviews, spoken lines, voice-over) |
| `musique` | music |
| `sons` | one-off sound effects |
| `voix` | voice-over lines (one file per sentence) |
| `chapitres` | chapters (finished videos laid end to end) |
| `sous_titres` | subtitles (SRT path, or `auto`) |
| `marqueurs` | markers |
| `controle` | measurements of the resulting edit against targets |
| `journal` | log: choices, gaps, things to check |
| `critique` | review (`critique_montage.py` arguments) |
| `titre` | title |
| `projet` | project name |
| `nom` | name (product name, chapter name, marker name, sound name) |
| `texte` | text |
| `phrase` | a written line (closing line) |
| `these` | thesis or opening question |
| `fichier` | file |
| `chemin` | path |
| `famille` | film family (see below); in `police`, the font family |
| `sous_famille` | subfamily |
| `schema` | form within the family |
| `format`, `largeur`, `hauteur` | format, width, height |
| `police` | font |
| `couleurs`, `fond` | colors, background |
| `t` | time in the film, in seconds (`plan.json`) |

**Times and levels**

| Identifier | Meaning |
|---|---|
| `_s` suffix, `_img` suffix | in seconds, in frames |
| `debut_img`, `debut_s` | start on the timeline |
| `duree_img`, `duree_s` | length |
| `entree_img`, `entree_s` | in point in the source file |
| `sortie_img`, `sortie_s` | out point in the source file |
| `duree_cible_s` | requested length |
| `tc_debut` | start timecode |
| `niveau_db` | music level, in dB |
| `attenuation_db` | ducking: how many dB the music drops under the voice |
| `fondu_sortie_s`, `fondu_sortie_img` | fade-out length |
| `decalage_s` | offset: where the music starts in its file |
| `reperes`, `debut_son_s`, `sommet_s`, `attaques_s` | music landmarks: sound start, high point, strong attacks |
| `meilleur_s` | best moment to keep at the center of the shot |
| `piste` | track (`V1`, `V2`, `A1`, `A2`, `A3`) |

**Shot, title card and clip fields**

| Identifier | Meaning |
|---|---|
| `type` | shot type: `image` (picture), `noir` (black), `carton` (title card) |
| `temps` | structure beat (see below) |
| `source` | clip id |
| `transition` | how the shot starts |
| `carton` | title card |
| `son_image` | keep the clip's own sound |
| `mouvement`, `mouvement_mesure` | motion label, measured motion |
| `valeur` | shot size |
| `sujet` | subject of the shot |
| `role` | wanted role of a clip, or role of a title card |
| `note` | rating 1 to 5 (`notes` = free comment) |
| `prises` | usable windows, or takes |
| `personne`, `fonction` | person, their role or job title |
| `ordre`, `chapitre` | order, chapter (of a speech clip) |
| `synchro`, `avec`, `decalage_s` | other angle of the same take: with which clip, offset |
| `bloc`, `titre_bloc` | trailer block, block title |
| `scene` | scene number |
| `place`, `taille_pct`, `deuxieme_ligne` | text position, cap height %, second line of a lower third |
| `direction` | camera direction |
| `statut`, `cible`, `mesure`, `base` | status, target, measurement, basis (corpus count) |

**Stored values**

| Identifier | Meaning |
|---|---|
| `produit`, `ouverture`, `documentaire`, `bande_annonce` (`bandeannonce`) | families: product and reveal; opening and mood; documentary and testimonial; trailer and usage |
| `revelation_tardive` / `tardif` | late reveal |
| `objet_des_le_debut` / `des_le_debut` | object from the start |
| `transition_decor`, `cloture`, `sketch`, `hommage` | transition between two places, closing film, sketch, tribute |
| `pose`, `choral` | calm (few long voices), ensemble (many short voices) |
| `catalogue_blocs` / `catalogue_par_blocs`, `catalogue_mele`, `oeuvre`, `usage` | catalog by blocks, mixed catalog, trailer for a single work, usage film |
| `compose` | composed edit |
| `coupe`, `fondu`, `blanc`, `poussee` | transitions: cut, dissolve (or fade from/to black), dip to white, push |
| `fondu_enchaine`, `fondu_au_noir`, `volet` | cross dissolve, fade to black, wipe (annotations) |
| `image`, `noir`, `carton` | picture, black, title card |
| `detail`, `tres_gros`, `gros`, `serre`, `rapproche`, `moyen`, `ensemble`, `entier`, `large`, `abstrait` | shot sizes: detail, extreme close-up, close-up, tight, medium close, medium, full group, whole object, wide, abstract |
| `objet`, `piece`, `matiere`, `decor`, `lumiere`, `geste`, `ecran`, `personne`, `entretien`, `illustration`, `oeuvre`, `photo`, `archive` | subjects: object, part, material, setting, light, gesture, screen, person, interview, illustration (cutaway), work, photo, archive |
| `fixe`, `lent`, `moyen`, `fort` | motion: still, slow, medium, strong |
| `avant`, `recul`, `rotation`, `lateral` | camera direction: forward, pull back, rotation, sideways |
| `accroche`, `revelation`, `fin`, `gamme`, `pic`, `arrivee`, `bouton`, `signature` | roles: hook, reveal, ending, product range, peak, arrival, button (the beat after the climax), signature shot |
| `ouverture`, `montee`, `nom`, `seuil`, `premier_plan`, `corps`, `atterrissage`, `respiration`, `annonce`, `fermeture`, `titre` | beats: opening, build-up, name, threshold, first shot, body, landing, breathing space, announcement, closing, title |
| `nom`, `titre`, `phrase`, `these`, `bandeau`, `titre_bloc`, `mot_choc`, `credit`, `mention`, `logo` | title card roles: name, title, line, thesis, lower third, block title, punch word, credit, notice, logo |
| `centre`, `bas_gauche`, `bas_droite`, `haut_gauche` | positions: center, bottom left, bottom right, top left |
| `naissance_lumiere`, `plan_tenu`, `pic_mouvement`, `mouvement_continu`, `changement_lumiere` | strong moments from the analysis: light appearing, held shot, motion peak, continuous motion, light change |
| `a_eviter` | zones to avoid |
| `ok`, `alerte`, `note`, `a_verifier`, `non_mesure`, `sans_objet` | review statuses: matches, alert, note, to check, not measured, not applicable |
| `observe` | observed in the corpus (as opposed to convention) |
