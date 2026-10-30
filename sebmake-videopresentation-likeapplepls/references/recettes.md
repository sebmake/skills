# Shot recipes

One shot in the film = one engine recipe = one HyperFrames scene. For each of the **12 recipes**, this file says when to use it, which visual it needs and which settings exist, and gives a sample shot for `film.json`. The names are exact: `check_film.py` rejects any other value of `recette`.

The full `film.json` format is in `film-spec.md`. The grammar (when, how many, in what order) is in `grammaire-film.md`.

Counts: "N/14" = object reveal films; "N/12" = interface films; "N/33" = texts added in the edit. "Convention" = not observed.

## Contents

1. Choosing a recipe
2. Fields shared by all shots
3. The 12 recipes: `noir`, `lisere`, `macro`, `orbite`, `eclate`, `revelation`, `panneau`, `empilement`, `carton`, `mot-sur-image`, `mur`, `fin`
4. Fallbacks when a visual is missing
5. Two standard 60 s sequences, checked
6. Observed techniques that have no recipe

---

## 1. Choosing a recipe

### 1.1 By the visual you have

| Visual provided | Possible recipes |
|---|---|
| **Cut-out** photo of the whole object (transparent PNG) | `lisere`, `orbite`, `revelation`, `macro`, `eclate` (cut into strips) |
| Several cut-out views, close angles | `orbite` (with `vues`) |
| Cut-out parts, same frame and same scale | `eclate` (with `pieces`) |
| Macro of a material or a detail | `macro` |
| Mood or in-use photo, with the rights | `mot-sur-image`, `macro` |
| Screenshot | `panneau`, `macro` (detail of a screenshot) |
| Several screenshots of modules | `empilement` |
| Icons, authorized logos, thumbnails | `mur` |
| Nothing | `carton`, `noir`, `fin` |

A screen recording (video) has no recipe in this engine. Pull still screenshots of the key moments from it (`ffmpeg -ss <time> -i recording.mp4 -frames:v 1 capture.png`).

### 1.2 By the beat of the film

| Beat | Typical recipes |
|---|---|
| Hook | `noir` (with a point of light) → `lisere` or `macro` or `panneau` without detail → `carton` (thesis) |
| Build-up | `macro`, `orbite`, `eclate`, `panneau`, `empilement`, `mur`, `mot-sur-image`, `carton` (idea, provided figure) |
| Breath between chapters | `noir`, or `transition: "noir"` on the next shot |
| Reveal | `revelation` (object); `empilement` for software (wide shot of the screens, convention) |
| Closing line | `carton` (a sentence of 3 to 9 words) |
| End | `fin` (always the last shot) |

---

## 2. Fields shared by all shots

| Field | What to know |
|---|---|
| `id` | unique; lowercase letters, digits, hyphens (`p01`, `revel`) |
| `role` | `accroche` (hook), `contexte` (context), `preuve` (proof), `revelation` (reveal), `chute` (closing line), `respiration` (breath), `fin` (end). The engine uses it to pick shots for `auto` cut-downs |
| `groupe` | shots kept or dropped together in a cut-down: a card and the shot that proves it |
| `priorite` | 1, 2 or 3; 1 = keep first in a short cut-down |
| `duree_s` | duration in the long film |
| `fond` | `sombre` (dark), `clair` (light), `accent` (rejected if no text reads on it); each recipe has its own default background |
| `transition` | how the shot **enters**: `coupe` (cut, default, 14/14), `fondu` (fade, 0.4 s; cannot be verified in the corpus: keep it for a continuous passage, `grammaire-film.md` § 5.4), `noir` (the previous shot fades out in 0.4 s, this one comes out of black in 0.5 s; 10/14 films go through black) |
| `notes` | the intent of the shot, for the review sheet; never shown in the film |

Duration rules the engine checks: each recipe has a minimum duration (from 0.5 s for `noir` to 3 s for `eclate` and `revelation`), and each text has its reading time. The checker gives the exact value, shot by shot. Follow its messages rather than computing by hand.

---

## 3. The 12 recipes

### `noir` — passing through black

- **When**: to open the product film (with the point of light); to breathe between two chapters; to hold a silence before the reveal. Observed: black 10/14, point of light 3/14; 100 blacks measured, median 0.65 s.
- **Visual**: none.
- **Settings**: `point` (true or false): a white point, a glow in the accent color and two thin crossed lines. It grows, then fades out.
- **Duration**: 0.5 to 1.5 s.
- **Cut-downs**: dropped automatically (frame 0 must be full).
- For a simple passage, `transition: "noir"` on the next shot is enough. Use the `noir` shot when you want to hold the black, or show the point of light.

```json
{ "id": "p01", "recette": "noir", "role": "accroche", "duree_s": 1.0, "mouvement": { "point": true },
  "notes": "Black. A point of light comes on, then fades out." }
```

### `lisere` — the object drawn by its lit edge

- **When**: the hook of an object film. You guess the object from its edge alone, before you see it whole. Observed 3/14.
- **Visual**: `objet`, a cut-out photo (transparent PNG), 2,400 px wide or more.
- **Settings**: `cote` (`gauche` or `droite`, left or right): the side the light comes from.
- **Background**: charcoal, lighter at the top (computed from `fond_sombre`).
- **Duration**: 3 to 5 s.
- **Pitfall**: works well on rounded shapes; on a very long shape, the edge light is uneven.

```json
{ "id": "p02", "recette": "lisere", "role": "accroche", "duree_s": 4.5,
  "visuels": { "objet": "visuels/objet-detoure.png" }, "mouvement": { "cote": "gauche" },
  "notes": "We guess the object from its edge. It stays hidden." }
```

### `macro` — an extreme close-up that slides

- **When**: the hook or the build-up: a material, a detail, a part, an area of a screenshot. Observed 12/14; a macro shot lasts 1.5 to 3 s.
- **Visual**: `image`, a high-resolution macro (at least 1.5 times the displayed size, so 2,900 px wide for an enlarged full frame), or the cut-out photo of the object, or a screenshot.
- **Settings**: `echelle` (scale, 1.2 to 3.5; capped by the engine at 1.5 times the native resolution); `sens` (`gauche`, `droite`, `haut`, `bas`: left, right, up, down): the 8% slide; `point` (`[x, y]` in % of the image): the target detail. The focus slides: a blur that clears in 1 s, then a sharp band (convention).
- **Text**: an optional `libelle` (label, 1 to 4 words).
- **Background**: black for a photo, a gradient for a cut-out object.
- **Duration**: 1.5 to 3 s.
- **Pitfall**: an image that is too small, once enlarged, gives a soft material.

```json
{ "id": "p04", "recette": "macro", "role": "contexte", "duree_s": 2.5,
  "visuels": { "image": "visuels/matiere.jpg" }, "mouvement": { "echelle": 2.2, "sens": "gauche", "point": [50, 70] },
  "notes": "The material under grazing light." }
```

### `orbite` — slow rotation and levitation

- **When**: to show the object or a part slowly turning and floating, in the build-up or just before the reveal. Observed: rotation 8/14 (30 to 90° per shot, never a full turn), levitation 9/14.
- **Visual**: `objet` (one view: rotation limited to ± 12°), or `vues`: 2 to 5 cut-out views at close angles (every 20 to 30°), same light, same scale. The engine crossfades from one to the next.
- **Settings**: `angle` (12 at most); `sens` (1 or −1).
- **Text**: an optional `libelle`.
- **Background**: light.
- **Duration**: 3 to 6 s.
- **Pitfall**: a flat photo turned past ± 15° looks like a card. Never promise a full turn.

```json
{ "id": "p10", "recette": "orbite", "role": "preuve", "groupe": "geste", "priorite": 2, "duree_s": 4.5,
  "visuels": { "vues": ["visuels/vue-face.png", "visuels/vue-34.png", "visuels/vue-profil.png"] },
  "mouvement": { "angle": 12, "sens": 1 }, "texte": { "type": "libelle", "contenu": "Adjustable head" } }
```

### `eclate` — the parts close together

- **When**: to show what makes up the object; often just before the reveal (in the films that have one, the assembly lands between 60 and 85%). Observed: exploded view 6/14, assembly 7/14, no bounce.
- **Visual**: `pieces`, a list of cut-out PNGs on **the same canvas** (same file size, each part in its place in the assembled object), from bottom to top; or `objet` alone, which the engine cuts into 3 to 6 strips (outer layers only: no invented insides).
- **Settings**: `axe` (`vertical`: a stack that tightens; `profondeur` (depth): a tilted 3D stack that turns back to face front); `bandes` (strips, 3 to 6, without `pieces`).
- **Text**: an optional `libelle`.
- **Background**: light.
- **Duration**: 4 to 6 s (assembly of 1.4 to 2 s, then the object holds for at least 1 s).

```json
{ "id": "p14", "recette": "eclate", "role": "contexte", "duree_s": 5.5,
  "visuels": { "pieces": ["visuels/piece-base.png", "visuels/piece-tige.png", "visuels/piece-tete.png"] },
  "mouvement": { "axe": "vertical" }, "notes": "The three parts come together." }
```

### `revelation` — the whole object, at last

- **When**: **the** reveal: the first shot of the whole object, held. Only once, after 60% of the film's duration (13/14). Observed: median shot of 5.5 s; light sweep 4/14, halo 3/14, pull-back 6/14.
- **Visual**: `objet`, the best cut-out photo (front or three-quarter).
- **Settings**: `recul` (pull-back, true by default: a slow pull-back that eases out); `halo` (true by default: a halo in the `accent` and `accent_2` colors, opacity 0.42 at most). The light sweep crosses the object once.
- **Text**: `nom`, only in a cut-down with `avec_nom` (the object fades out, the name comes in). In the long film, the name goes in `fin`.
- **Background**: dark (floor reflection); `clair` gives a soft shadow.
- **Duration**: 5 to 8 s; at least 4 s with the name.
- Often preceded by `transition: "noir"`.

```json
{ "id": "p15", "recette": "revelation", "role": "revelation", "duree_s": 8.0, "fond": "sombre",
  "visuels": { "objet": "visuels/objet-detoure.png" }, "mouvement": { "recul": true, "halo": true },
  "transition": "noir", "notes": "The whole object: halo, a sweep of light, slow pull-back." }
```

### `panneau` — the interface without a device

- **When**: the base shot of a software film. A whole screen as a floating panel, then we **go into** a detail (`zoom`) or **light it up** (`projecteur`, spotlight). One feature per shot. Observed: interface without a device 7/12, push toward a detail 6/12, no arrow or callout box 0/12.
- **Visual**: `capture`, a PNG screenshot at native resolution or ×2 (desktop or mobile, detected from the ratio). Blur or replace sensitive real data first; keep the real time shown in the screenshots. For a zoom, plan a screenshot at least twice as wide as its displayed size.
- **Settings**: `detail`: `{ "zone": [x, y, width, height] in % of the screenshot, "mode": "zoom" or "projecteur" }`. Without `detail`: a slow push.
  - `zoom`: the camera goes into the zone; the rest of the screen blurs and fades toward the background, so the feature name keeps a calm area. The zone must be clearly smaller than the screen (less than about half its width). Otherwise the engine reports "zoom limited".
  - `projecteur`: the whole frame darkens (the rest drops to about 20% of its luminance in 0.8 s: measured on 1 instance), and the isolated element rises to the center of the image area and grows. The feature name appears in light text. This is the mode to prefer in 9:16 for a desktop screen, which would be unreadable there in full.
  - After going into the detail, the camera keeps sliding slowly: never a frozen frame.
- **Text**: a `libelle`, the name of the feature (1 to 4 words), placed next to the screen: at 81% of the width in 16:9, above in 9:16, below in 1:1.
- **Background**: light.
- **Duration**: 3 to 6 s (an interface subject holds 3 to 4 s in the film, 2 to 2.5 s in a cut-down; at least 2 s).
- **Pitfall**: in 9:16, a whole desktop screen becomes unreadable; add a `detail`.

```json
{ "id": "p07", "recette": "panneau", "role": "preuve", "groupe": "planning", "priorite": 1, "duree_s": 5.5,
  "visuels": { "capture": "visuels/planning.png" },
  "texte": { "type": "libelle", "contenu": "Week view" },
  "mouvement": { "detail": { "zone": [10, 20, 40, 30], "mode": "zoom" } } }
```

### `empilement` — windows arrive from the depth

- **When**: a workspace made of several modules; the wide shot of a software product, which can stand in for the reveal (convention). Observed: assembly 3/12, arrival in 0.5 s or less.
- **Visual**: `captures`, 2 to 5 screenshots of different modules.
- **Settings**: none. With `role: "revelation"`, the engine adds a slow pull-back that eases out over the whole shot and a soft halo in the accent colors behind the screens (convention, modeled on the object reveal).
- **Text**: an optional `libelle`. In a cut-down with `avec_nom`, the screens fade out and the name comes in (a shot of 4.5 to 5.5 s depending on the number of screenshots).
- **Background**: light.
- **Duration**: 3.5 to 5 s; up to 8 s when it stands in for the reveal.

```json
{ "id": "p12", "recette": "empilement", "role": "revelation", "duree_s": 6.0,
  "visuels": { "captures": ["visuels/accueil.png", "visuels/planning.png", "visuels/rapport.png"] },
  "transition": "noir" }
```

### `carton` — text alone on a plain background

- **When**: the thesis, an idea card (opening a chapter), a punch word, a **provided** figure, the closing line. The card is a shot of its own: 23 texts out of 33.
- **Visual**: none.
- **Text**:
  - `phrase` (sentence): 12 words at most; 6 at most in one block; from 7 to 12, built in 2 or 3 groups. `affichage` (display): `bloc`, `groupes` or `mot-a-mot` (block, groups, word by word); `groupes`: the sentence split by hand, which must give back `contenu` word for word.
  - `mot` (word): 1 or 2 words, large size, bold. One or two per film.
  - `chiffre` (figure): `chiffre` (provided, otherwise `null`), `libelle` (with the basis of comparison), `source`. Without a provided figure, the card shows `[TO PROVIDE]`, dimmed.
- **Background**: dark; `clair`; `accent` only if the text reads on it (otherwise the checker rejects it).
- **Shot duration**, entry and exit included: at least **1.8 s + 0.3 s per word**, recommended **2.1 s + 0.3 s per word** (5 words: 3.3 s at least, 3.6 s recommended). Punch word: about 2.6 s. Built in groups: count about 0.8 s per added group (0.4 s per word for word by word).
- **Pitfalls**: two cards in a row with no image between them trigger a warning (except in a text-only film, where you separate them with a `noir` of 0.5 to 1 s). Sentence case, no exclamation mark, no all caps.
- **Provided quote**: no dedicated recipe. A `phrase` in quotation marks, 12 words at most, with the author included or in the next card; only with that person's consent.

```json
{ "id": "p06", "recette": "carton", "role": "preuve", "groupe": "heure", "priorite": 1, "duree_s": 3.8, "fond": "clair",
  "texte": { "type": "phrase", "contenu": "Cool by morning. Warm by night.",
             "groupes": ["Cool by morning.", "Warm by night."], "affichage": "groupes" } }
```

```json
{ "id": "p10", "recette": "carton", "role": "preuve", "duree_s": 3.4, "fond": "sombre",
  "texte": { "type": "chiffre", "chiffre": null, "libelle": "hours of light per charge", "source": null },
  "notes": "Figure to be provided by the user, with its source." }
```

### `mot-sur-image` — a few words in the calm area of an image

- **When**: 1 to 4 words on a strong, calm image; the hook of a cut-down, or a proof on an in-use photo. Observed once, in an appendix: it is almost a convention. The card on a plain background stays the rule.
- **Visual**: `image`, a photo the user has the rights to, with a calm area (sky, night, wall, blur).
- **Settings**: `zone` (`centre`, `haut`, `bas`, `gauche`, `droite`: center, top, bottom, left, right): where to place the text; `point` (`[x, y]` in %): the subject to keep when the engine recomposes for 9:16 and 1:1.
- **Text**: `phrase` (4 words at most recommended) or `mot`.
- **Background**: the image, with a slow push and a soft local veil behind the text (never a box).
- **Duration**: 2.5 to 4 s.
- **Pitfall**: the real contrast depends on the image. Aim for 7:1; check it with `npx hyperframes check` (the engine's `--check` option).

```json
{ "id": "p09", "recette": "mot-sur-image", "role": "preuve", "duree_s": 3.4,
  "visuels": { "image": "visuels/bureau-le-soir.jpg" },
  "texte": { "type": "phrase", "contenu": "Just one gesture." }, "mouvement": { "zone": "gauche", "point": [70, 50] } }
```

### `mur` — a grid or a parade of items

- **When**: integrations, compatible tools, customers, a product range. `grille` (grid): the grid fills up, then a spotlight lights one item; `defile` (parade): one item at a time, every 0.5 s, on a background that alternates dark and light. Observed: parade 1/12 (0.5 s measured), spotlight measured on 1 instance.
- **Visual**: `elements`, a list of PNGs (icons, logos, thumbnails); 6 to 12 for a parade. **Logos only if they are provided and authorized.**
- **Settings**: `mode` (`grille` or `defile`); `focus`: the position of the lit item, starting at 1.
- **Text**: an optional `libelle`.
- **Background**: dark.
- **Duration**: 3 to 6 s; in a parade, 0.5 s per item plus 1 s.

```json
{ "id": "p13", "recette": "mur", "role": "preuve", "duree_s": 4.5,
  "visuels": { "elements": ["visuels/scene-1.png", "visuels/scene-2.png", "visuels/scene-3.png", "visuels/scene-4.png", "visuels/scene-5.png", "visuels/scene-6.png"] },
  "mouvement": { "mode": "grille", "focus": 3 } }
```

### `fin` — the name, alone

- **When**: the last shot of every output, film and cut-downs. The name closes the film (21 times out of 24). Never at the opening: the checker rejects it.
- **Visual**: none; the logo comes from `theme.logo`, only if it is provided.
- **Text**: `nom`, with `contenu` (the exact name) and an optional `ligne`: a **provided** call-to-action line (a date, an address, "coming soon"). No slogan and no invented date under the name (0/14).
- **Settings**: `taille` (size): `heros` (hero, default; 124 px in 16:9) or `discret` (discreet, 56 px). `discret` for an object, which stays the hero (observed 2/2 object films); `heros` for software or a service (observed 2/2 interface films). This split is a convention.
- **Background**: dark.
- **Duration**: 3 to 4.5 s in the film (final fade to black of 0.6 s); 2.5 to 3.5 s in a cut-down, with no final black.

```json
{ "id": "p17", "recette": "fin", "role": "fin", "duree_s": 4.5, "fond": "sombre",
  "texte": { "type": "nom", "contenu": "Clarity", "ligne": "Coming soon" }, "mouvement": { "taille": "discret" } }
```

---

## 4. Fallbacks when a visual is missing

A missing visual does not block the work. The engine draws a **neutral fallback**, with no text, no figure and no brand, and reports it in the console and on the review sheet.

| Missing slot | Fallback drawn |
|---|---|
| `objet`, `pieces`, `vues` | a gray pebble |
| `capture`, `captures` | a gray interface skeleton |
| `image` | a dark gradient |
| `image` of a `macro` | gray brushed metal |
| `elements` | rounded tiles |

A film full of fallbacks is a draft. Each fallback goes on the list of visuals to provide, at delivery.

---

## 5. Two standard 60 s sequences, checked

These two sequences pass `check_film.py` with no errors. The remaining warnings are expected: missing visuals, rotation on a single view, a figure not provided, real contrast on an image to verify, automatic selection for a cut-down and, for software, the share of text. They are a starting point, not a model to copy: the shots come from the user's visuals.

### 5.1 Object, 60 s (reveal at 73%, name at 93%)

| # | Recipe | Role | Duration | Text |
|---|---|---|---|---|
| 1 | `noir` (point) | accroche | 1.0 | — |
| 2 | `lisere` | accroche | 4.5 | — |
| 3 | `carton` | accroche | 3.6 | thesis, 5 words |
| 4 | `macro` | contexte | 3.0 | — |
| 5 | `macro` | contexte | 2.0 | — |
| 6 | `orbite` (one view) | preuve | 4.0 | label, 2 words |
| 7 | `carton` (light background) | preuve | 3.6 | idea, 5 words |
| 8 | `macro` | preuve | 2.2 | — |
| 9 | `mot-sur-image` | preuve | 3.4 | 3 words |
| 10 | `orbite` (3 views) | preuve | 4.5 | — |
| 11 | `noir` | respiration | 0.8 | — |
| 12 | `carton` | contexte | 3.6 | idea, 5 words |
| 13 | `macro` | contexte | 2.5 | — |
| 14 | `eclate` (3 parts) | contexte | 5.5 | — |
| 15 | `revelation` (`transition: noir`) | revelation | 8.0 | — |
| 16 | `carton` | chute | 3.6 | 5 words |
| 17 | `fin` (discreet) | fin | 4.5 | the name |

Total 60.3 s; 17 shots; 7 texts, so 7 per minute.

### 5.2 Software, 60 s (wide shot at 76%, name at 92%)

| # | Recipe | Role | Duration | Text |
|---|---|---|---|---|
| 1 | `noir` (point) | accroche | 1.2 | — |
| 2 | `panneau` without detail | accroche | 4.3 | — |
| 3 | `carton` | accroche | 3.6 | thesis, 5 words |
| 4 | `panneau` (`zoom`) | preuve | 5.5 | feature name |
| 5 | `panneau` (`projecteur`) | preuve | 5.5 | feature name |
| 6 | `carton` | contexte | 3.3 | idea, 4 words |
| 7 | `mur` (grid, focus) | preuve | 5.0 | — |
| 8 | `panneau` (`zoom`) | preuve | 5.5 | feature name |
| 9 | `carton` (figure `null`) | preuve | 3.4 | `[TO PROVIDE]` + label |
| 10 | `panneau` without text | preuve | 5.0 | — |
| 11 | `macro` on a screenshot | preuve | 2.5 | — |
| 12 | `noir` | respiration | 0.8 | — |
| 13 | `empilement` (`transition: noir`) | revelation | 6.0 | — |
| 14 | `carton` | chute | 3.9 | 6 words |
| 15 | `fin` (hero) | fin | 4.5 | the name |

Total 60.0 s; 15 shots. Feature names stay on screen for their whole shot. A software film often goes over 45% text on screen, and the checker reports it. This warning is expected. Keep it knowingly, or remove one feature name.

### 5.3 Text-only film

A series of `carton` shots (some of them `mot-a-mot`), separated by `noir` shots of 0.8 s, on two or three backgrounds that change by section, then `fin`. About 13 fragments for 60 s. The checker reports a pace and a share of text above the conventions of an image film. This is expected for this family (the observed text-only film shows text 85% of the time).

---

## 6. Observed techniques that have no recipe

| Technique | Observed | Why no recipe | Instead |
|---|---|---|---|
| The image was the screen (a pull-back reveals that a full-frame image is the object's screen) | 3/14 | needs a device frame: risk of a recognizable device | `panneau` with `zoom` |
| A line of light, an engraving that draws itself | 2 films | needs an SVG from the user | `lisere` or `macro` |
| Backlight and silhouettes | 3/14 | needs cut-out people and their consent | don't do it |
| Top-down plunge, parade of colorways, shape match cut | 4/14, 4/14, 7/14 | not written yet | colorways: `mur` in `defile` if the photos share the same framing; otherwise `orbite` |
| Parallax flyover, technical view, hands and motion blur | 1/14, 2/14, 7/14 | rare materials, risk of invented dimensions | don't do it |
| Same frame, new state; scrolling; match cut on content; typing; cursor | 2 to 4/12 | not written yet | two `panneau` shots in a row on two screenshots; `macro` on a long screenshot |
| The word does what it says | 5 cases in 3 films | not written | don't imitate it with a generic effect |

A missing technique can be added by hand in the generated HyperFrames project (`sortie-…/projets/<name>/compositions/<shot>.html`, following the `hyperframes-core` skill), then rendered with `npx hyperframes render`. Warning: running `build_film.js` again rewrites the project and erases the edit. Tell the user, and note it at delivery.
