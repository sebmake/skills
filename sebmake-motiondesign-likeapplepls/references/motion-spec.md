# motion.json: the animation format

This file describes `motion.json`, the sheet that says **what to animate** and **with which recipe**. The generator turns it into an After Effects script (`.jsx`) that builds the animation, layer by layer, key by key.

The pipeline:

1. write `motion.json` (this file says how);
2. check it: `python3 scripts/check_motion.py motion.json`;
3. generate the script: `node scripts/build_motion.mjs motion.json` (writes `motion.jsx` next to it);
4. run it: in After Effects (File > Scripts > Run Script File), or in EffectCraft (`python3 scripts/ec.py script motion.jsx`);
5. look: check frames (`ec.py frames`), then an MP4 render (`ec.py render`).

The recipe values come from four frame-by-frame analyses of 8 keynotes (2019 to 2026): text (145 instances), objects (122), interfaces (189), transitions (182). Each recipe carries its counts. Anything not measured is marked **convention**. The skill borrows a grammar of motion, never a brand: no image, font, logo or signature of any company.

## French identifiers used in this file

The JSON keys and values stay in French because the scripts read them. What they mean:

| Identifier | Meaning |
|---|---|
| `comp`, `nom`, `format`, `cadence`, `duree`, `fond`, `epoque` | composition, name, format, frame rate, duration, background, era |
| `theme`, `couleurs`, `polices`, `tailles`, `approche` | theme, colors, fonts, sizes, tracking |
| color roles `fond`, `texte`, `secondaire`, `accent`, `voile`, `lumiere`, `repli`, `repli_trait` | background, text, secondary, accent, scrim, light, placeholder fill, placeholder stroke |
| `elements`, `id`, `type`, `contenu`, `fichier`, `taille`, `couleur` | elements, id, type, content (text), file, size, color |
| `recette`, `debut`, `maintien`, `fin`, `sortie`, `options`, `puis` | recipe, start, hold, end, exit, options, then (add-ons after the entrance) |
| `avec`, `parent`, `profondeur`, `camera`, `simultane` | with (arrives with another element), parent, depth, camera, simultaneous |
| `libelle`, `source`, `lignes`, `groupes`, `fichiers`, `pieces`, `alignement`, `interligne` | label, source, lines, groups, files, pieces, alignment, line spacing |
| `decalage`, `a` | offset, at (absolute time) |
| `transitions`, `temps`, `de`, `vers` | transitions, time, from, to |
| types `titre`, `phrase`, `surtitre`, `liste`, `chiffre`, `logo`, `image`, `capture`, `icone`, `forme`, `fond`, `nul-camera` | title, sentence, kicker, list, number, logo, image, screenshot, icon, shape, background, camera null |
| option values `gauche`, `droite`, `centre`, `bas`, `haut`, `ouvre`, `ferme`, `allume`, `eteint`, `entre`, `coupe`, `fondu` | left, right, center, bottom, top, opens, closes, lights up, goes dark, zooms in, cut, fade |
| statut `m` / `conv.` | measured / convention |

---

## 1. Units

| quantity | unit | example |
|---|---|---|
| time | second, from 0 | `"debut": 3.2` |
| position | % of width and % of height, center of the element | `"position": [50, 50]` = center of the frame |
| size, distance | **u** = 1 % of the short side of the frame | 16:9 at 1920 × 1080: 1 u = 10.8 px (the "% H" of the analyses) |
| width of a front or an edge | % of frame width (% W) | `"bord": 2.8` |
| scale | factor (× 1 = resting size) | `"depart": 4.1` |
| angle | degree | `"angle": 90` |
| color | HEX `#RRGGBB`, or a theme role | `"couleur": "accent"` |

- All keys are snapped to frames and at least one frame apart: two keys less than one frame apart merge in EffectCraft.
- 9:16 and 1:1 do not exist in the corpus. Sizes and distances in u keep the same proportions there: **convention**.

---

## 2. The `comp` block

```json
"comp": { "nom": "launch", "format": "16:9", "cadence": 30, "duree": 20, "fond": "fond", "epoque": "2024-2026" }
```

| field | values | default | role |
|---|---|---|---|
| `nom` | text | `Motion` | composition name; rerunning the script replaces the composition with the same name |
| `format` | `16:9` (1920 × 1080), `9:16` (1080 × 1920), `1:1` (1080 × 1080) | `16:9` | or `largeur` and `hauteur` (width and height) in px |
| `cadence` | 24, 25, 29.97, 30, 50, 60 | 30 | frames per second |
| `duree` | seconds | 10 | composition duration |
| `fond` | HEX or role | `fond` | background color of the composition (under all layers) |
| `epoque` | `2024-2026` or `2019-2020` | `2024-2026` | picks the editing curves (zoom, row, scroll, scrim); a recipe from another era is flagged |

Why the era: the arrival curve of zooms, slides and rows changes from one era to the other (21 instances in 2019-2020, 56 in 2024-2026), and the number overshoots by 5 % in 2020 (6 out of 6) but never in 2025-2026 (18 out of 18). Pick one era and stick to it: **convention**.

---

## 3. The `theme` block

```json
"theme": {
  "couleurs": { "fond": "#0E1013", "texte": "#F4F4F2", "secondaire": "#9A9CA3", "accent": "#4C8DFF", "voile": "#000000" },
  "polices": { "titre": ["Inter-SemiBold", "Inter-Bold", "Arial-BoldMT"], "texte": ["Inter-Regular", "ArialMT"],
               "chiffre": ["Inter-Bold", "Arial-BoldMT"], "surtitre": ["Inter-Medium", "ArialMT"] },
  "tailles": { "titre": 10, "phrase": 5.4 },
  "approche": { "titre": -10 }
}
```

- **Colors by role.** Known roles: `fond`, `texte`, `secondaire` (kicker, label), `accent`, `voile` (darkening scrim), `lumiere` (light streak), `repli` and `repli_trait` (placeholder drawing). An element takes a role or a HEX in `couleur`.
- **Fonts with fallback.** Each role (`titre`, `texte`, `chiffre`, `surtitre`) gives a list of PostScript names, from preferred to fallback. After Effects 24 and later takes the first installed name (`app.fonts`). Other versions and EffectCraft take the first name: put an installed font first. EffectCraft ships Inter (Regular, Medium, SemiBold, Bold).
- A brand-specific font (a manufacturer's system family, for example) is refused by the check.
- **Default sizes** (u): title 10, sentence 5.4, kicker 3.2, list 4.4, number 30, label 3.7, logo 12, image 50, screenshot 60, icon 10, shape 20. The hero number measures 30 to 50 % H in the corpus; the other sizes are a **convention**.
- **Tracking** (`approche`, in thousandths of an em) by type: title −10, number −20, everything else 0 (**convention**).

---

## 4. Elements

`elements` is the list of things on screen, **from back to front**: the first one is at the bottom.

### 4.1 Common fields

| field | role |
|---|---|
| `id` | unique name; used for links and for layer names (`titre — One object…`) |
| `type` | `titre`, `phrase`, `surtitre`, `liste`, `chiffre`, `logo`, `image`, `capture`, `icone`, `forme`, `fond`, `nul-camera` |
| `contenu` or `fichier` | the text (`\n` for a line break), or the path of an image (relative to motion.json) |
| `position` | `[x %, y %]` of the center; default `[50, 50]` |
| `taille` | in u: text size, or image height |
| `couleur` | HEX or theme role |
| `recette` | the entrance animation (§ 5); default `coupe` |
| `debut` | moment the recipe starts |
| `maintien` | how long the element stays after its entrance ends |
| `fin` | moment of the exit (takes priority over `maintien`); with neither, the element stays to the end |
| `sortie` | `coupe` (default) or `fondu` |
| `options` | recipe settings (§ 5), only when you must depart from the measured values |
| `puis` | add-ons played after the entrance: `[{ "recette": "balayage-lumiere", "decalage": 1.1, "options": {…} }]` |
| `avec` | id of the main element, for an element that arrives with it (recipe `avec`) |
| `parent` | id of a `nul-camera`: the element follows its moves |
| `profondeur` | for parallax under a global camera: 1 = foreground (default), 0.5 = twice as slow |
| `camera` | `false`: the element does not follow the global camera (a fixed title, for example) |
| `simultane` | `true`: allows a major move at the same time as another one (the check forbids it otherwise) |

**The exit.** 15 text exits out of 18 are cuts; the other 3 are fades (0.90 to 0.93 s from 10 to 90 %). No exit moves, shrinks or blurs (0 out of 18). So the format offers only `coupe` and `fondu` (linear, 1.15 s). For an animated departure, use a transition (§ 6).

### 4.2 Fields by type

| type | own fields | notes |
|---|---|---|
| `titre`, `phrase` | `contenu`, `police` (role), `alignement` (`centre`, `gauche`, `droite`), `interligne` (u) | `carton-groupes` needs `groupes`: `["Built to", "last", "a long time."]` |
| `surtitre` | `contenu`, `avec` | the kicker has no animation of its own: recipe `avec` |
| `liste` | `lignes` (one string per line), `alignement` (default `gauche`), `interligne` (u, default 1.7 × size) | the block is centered on `position`; lines align to the left of the block |
| `chiffre` | `contenu`, `libelle`, `source`, `taille_libelle`, `couleur_libelle`, `position_libelle` | an unknown value is written `"[TO PROVIDE]"`; a number without `source` is refused |
| `image`, `capture`, `icone`, `logo` | `fichier`, `ratio` (width / height of the placeholder) | a missing file leaves a **neutral placeholder**: a rounded frame and its two diagonals, at the right aspect ratio. A missing `logo` with a `nom` field is replaced by that name, as text |
| `capture` + `empilement` | `fichiers` (at least two screens) | one screen per file, arriving one after the other |
| `image` + `eclate` | `pieces`: `[{ "fichier" or "largeur", "taille", "position": [dx u, dy u], "direction": [dx u, dy u] }]` | `position`: place of the assembled piece, relative to the center; `direction`: offset when opened. Without pieces: three placeholder plates |
| `forme` | `forme` (`rect` or `rond`), `largeur` (u), `taille` (height, u), `coins` (u), `contour` | for a schematic panel, a card, a pill |
| `fond` | `couleur` or `fichier` | a background image covers the whole frame; the background does not follow the camera, unless `"camera": true` |
| `nul-camera` | `position` (anchor point), a camera `recette` or `zoom-detail` | a neutral null (anchor = position); elements attach to it through `parent` |

### 4.3 Links

- `avec`: the element takes the start, recipe, options and exit of the named element. Use: a kicker above a title, a tagline under an end logo.
- `options.nom` (recipe `nom-remonte`): the name that moves up when the label and price come in below it.
- `options.ancien` (recipes `mot-remplace`, `mot-fondu-enchaine`, `mot-glisse`): the word that leaves.
- `parent`: a `nul-camera`.

### 4.4 Add-ons (`puis`)

Three recipes sit on top of the entrance, on the same element:

| add-on | what it does | when |
|---|---|---|
| `assombrir-autour` | a black scrim falls over everything under the element; option `flou`: the background blurs at the same time | often after a panel arrives |
| `balayage-lumiere` | a light streak crosses the object once, in a straight line | when the object has just settled |
| `revelation-lumiere` | the object comes out of black (or goes dark, `"sens": "eteint"`); option `eclat`: it lights up a bit too much before settling | on the cut, 0.2 to 0.4 s after |

Timing: `"a": 4.1` (absolute), or `"decalage": 1.1` (after the element's `debut`). With neither, the add-on starts at the end of the entrance.

---

## 5. Recipes

A recipe = a measured animation. Its options have a **default** (the median or common value of the corpus), a **range** and a **status**: `m` (measured: a setting outside the range is an error in the check) or `conv.` (convention: a different setting is allowed, and flagged). "Major": the recipe moves or enlarges the element; two major moves do not overlap (§ 7).

Durations: `T` = time from one key to the next; `d1090` = measured time between 10 and 90 % of progress (the generator derives `T` from the curve); `visible` = between 2 and 98 %.

#### Common

| recipe | types | major | era | options: default · range · status |
|---|---|---|---|---|
| `coupe` | all | no | all | — |

#### Text

| recipe | types | major | era | options: default · range · status |
|---|---|---|---|---|
| `avec` | surtitre, phrase, titre, icone | no | all | `ecart` 0 · -0.06–0.06 s · m |
| `titre-fondu-montee` | titre, phrase, chiffre | yes | 2024-2026 | `T_opacite` 0.77 · 0.64–0.77 s · m<br>`T_position` 0.92 · 0.92–1.17 s · m<br>`retard_position` 0.3 · 0.26–0.31 s · m<br>`montee` 15.3 · 7.4–15.5 u · m<br>`flou` 0 · 0–0.4 u · conv. |
| `titre-fondu` | titre, phrase, surtitre | no | all | `d1090` 0.43 · 0.27–0.71 s · m |
| `titre-balayage` | titre, phrase | no | 2024-2026 | `T` 0.6 · 0.33–0.86 s · m<br>`bord` 2.8 · 2.8–6.3 % W · m |
| `phrase-zoom-arriere` | phrase, titre | yes | 2019-2020 | `depart` 8 · 7.5–8.1 × · m<br>`T_echelle` 0.42 · 0.4–0.45 s · m<br>`d1090_opacite` 0.35 · 0.33–0.37 s · m<br>`flou` 5 · 4.4–6.7 u · m |
| `chute` | phrase, chiffre, titre | yes | 2019-2020 | `T` 0.23 · 0.2–0.27 s · m<br>`hauteur` 68 · 45–75 u · m |
| `phrase-par-le-bas` | phrase | yes | 2019-2020 | `T` 0.65 · 0.6–0.7 s · m<br>`depart` 58 · 50–60 u · m |
| `liste-cascade` | liste | yes | 2024-2026 | `decalage` 0.1 · 0.093–0.113 s · m<br>`T_opacite` 1.14 · 1–1.17 s · m<br>`T_position` 1.17 · 0.98–1.17 s · m<br>`montee` 21 · 18–23 u · m |
| `liste-cascade-rapide` | liste | yes | 2024-2026 | `decalage` 0.05 · 0.029–0.066 s · m<br>`T_opacite` 0.75 · 0.64–0.83 s · m<br>`montee` 4 · 0–4.1 u · m<br>`T_position` 1 · 1–1.02 s · m |
| `liste-par-le-bas` | liste | yes | 2019-2020 | `decalage` 0.37 · 0.362–0.377 s · m<br>`T` 0.65 · 0.63–0.67 s · m<br>`depart` 31 · 27–35 u · m |
| `liste-au-fil` | liste | yes | 2024-2026 | `intervalle` 2 · 1.4–3.6 s · m<br>`T_opacite` 1.17 · 1.1–1.2 s · m<br>`T_position` 0.95 · 0.9–1 s · m<br>`montee` 15 · 14–17 u · m |
| `nom-remonte` | phrase, chiffre | yes | all | `T_nom` 0.5 · 0.45–0.53 s · m<br>`remontee` 10 · 7.4–10.7 u · m<br>`d1090_opacite` 0.3 · 0.22–0.41 s · m<br>`montee` 10 · 6–14 u · m |
| `mot-remplace` | titre, phrase, surtitre | no | all | — |
| `mot-fondu-enchaine` | titre, phrase, surtitre | no | 2024-2026 | `d1090_ancien` 0.5 · 0.45–0.55 s · m<br>`d1090_nouveau` 0.47 · 0.42–0.52 s · m<br>`ecart` 0.61 · 0.55–0.65 s · m<br>`flou` 1.5 · 0–3 u · conv. |
| `mot-glisse` | titre, phrase, surtitre | no | 2019-2020 | `d1090_ancien` 0.22 · 0.2–0.25 s · m<br>`d1090_nouveau` 0.2 · 0.18–0.23 s · m<br>`ecart` 0.16 · 0.14–0.18 s · m<br>`glisse` 6 · 3–10 u · conv. |
| `chiffre-pose` | chiffre, titre | yes | 2024-2026 | `depart` 4.1 · 1.9–8 × · m<br>`T_echelle` 0.67 · 0.25–0.8 s · m<br>`d1090_opacite` 0.2 · 0.18–0.62 s · m<br>`flou` 6.7 · 1.1–6.7 u · m<br>`retard_libelle` 0.23 · 0.19–0.3 s · m<br>`d1090_libelle` 0.27 · 0.26–0.27 s · m |
| `chiffre-croissance` | chiffre | yes | 2019-2020 | `depart` 0.22 · 0.19–0.37 × · m<br>`T_echelle` 0.83 · 0.72–0.88 s · m<br>`d1090_opacite` 0.22 · 0.2–0.24 s · m<br>`retard_libelle` 0.26 · 0.16–0.29 s · m<br>`d1090_libelle` 0.11 · 0.1–0.15 s · m |
| `carton-fondu` | titre, phrase | no | all | `d1090` 0.45 · 0.31–0.78 s · m |
| `carton-groupes` | phrase | no | all | `ecart` 0.75 · 0.6–2.5 s · m<br>`d1090` 0.45 · 0.31–0.78 s · m<br>`T_recentrage` 0.3 · 0.2–0.5 s · conv. |

#### Objects and products

| recipe | types | major | era | options: default · range · status |
|---|---|---|---|---|
| `produit-entree` | image, capture, icone, logo, forme | yes | 2024-2026 | `T` 0.9 · 0.82–0.93 s · m<br>`depuis` droite  · m<br>`obturateur` 120 · 74–169 ° · m |
| `produit-poussee` | image, capture, icone, logo, forme, nul-camera | no | all | `facteur` 1.27 · 1.02–2.58 × · m<br>`duree` 4.1 · 2.2–8.6 s · m |
| `produit-recul` | image, capture, icone, logo, forme, nul-camera | no | all | `facteur` 0.45 · 0.05–0.84 × · m<br>`duree` 5.8 · 2.7–8.5 s · m |
| `produit-pivot` | image, capture, icone, logo, forme | yes | all | `angle` 90 · 12–90 ° · m<br>`T` 2 · 1.7–2.6 s · m<br>`delai` 0.25 · 0.2–0.3 s · m |
| `produit-rotation` | image, capture, icone, logo, forme | no | all | `angle` 83 · 19–160 ° · m<br>`duree` 4.2 · 1.4–9.5 s · m |
| `produit-flotte` | image, capture, icone, logo, forme | no | all | `derive` 0 · 0–10 u/s · conv.<br>`ombre` 1 · 0–1  · conv. |
| `eclate` | image, forme | yes | all | `sens` ouvre  · m<br>`T_ouvre` 1.9 · 0.2–18.8 s · m<br>`T_ferme` 1.2 · 1.1–2.8 s · m<br>`amplitude` 1 · 0.5–3 × · conv.<br>`decalage` 0 · 0–3.15 s · conv. |
| `balayage-lumiere` | image, capture, icone, logo, forme, titre | no | 2024-2026 | `T` 0.28 · 0.1–1.17 s · m<br>`largeur` 31 · 5–32 % of object · m<br>`sens` droite  · m<br>`intensite` 45 · 20–80 % · conv.<br>`inclinaison` 20 · 0–35 ° · conv. |
| `revelation-lumiere` | image, capture, icone, logo, forme | no | all | `d1090` 1.6 · 0.1–6 s · m<br>`delai` 0.3 · 0.2–0.4 s · m<br>`sens` allume  · m<br>`eclat` 0 · 0–28 % · m |

#### Screens and interfaces

| recipe | types | major | era | options: default · range · status |
|---|---|---|---|---|
| `panneau-pose` | capture, forme, image, icone | yes | all | `visible` 0.36 · 0.17–0.5 s · m<br>`distance` 40 · 15.9–62 u · m<br>`depuis` bas  · m<br>`dans_la_page` 0 · 0–1  · m<br>`carte` 0 · 0–1  · m<br>`fondu` 1 · 0–1  · conv. |
| `zoom-detail` | capture, image, nul-camera | yes | all | `facteur` 2.2 · 1.45–3 × · m<br>`T` 0.95 · 0.6–1.53 s · m<br>`sens` entre  · m<br>`point` [50, 50] % · conv. |
| `defilement` | capture | yes | all | `distance` 59.5 · 14–196 u · m<br>`T` 1.07 · 0.94–2.16 s · m<br>`mode` presentation  · m<br>`fenetre` [60, 60] u · conv. |
| `empilement` | capture | yes | all | `intervalle` 1.67 · 0.83–10.5 s · m<br>`T` 0.79 · 0.6–1 s · m<br>`ecart` 4 · 2–8 u · conv. |
| `assombrir-autour` | image, capture, icone, logo, forme, titre, phrase, surtitre, chiffre, liste | no | all | `niveau` 40 · 5–73 % · m<br>`T` 0.53 · 0.4–0.6 s · m<br>`flou` 0 · 0–0.78 u · m |

#### Camera (nul-camera or camera block)

| recipe | types | major | era | options: default · range · status |
|---|---|---|---|---|
| `camera-poussee` | nul-camera | no | all | `facteur` 1.27 · 1.02–2.58 × · m |
| `camera-recul` | nul-camera | no | all | `facteur` 0.45 · 0.05–0.84 × · m |
| `camera-travelling` | nul-camera | no | all | `vitesse` 4.7 · 0.5–48 u/s · m<br>`direction` [-1, 0]  · conv. |
| `camera-se-pose` | nul-camera | no | all | `d1090` 4.4 · 2.1–5.2 s · m<br>`facteur` 0.68 · 0.46–1 × · m<br>`deplacement` [0, 0] u · conv. |

#### End

| recipe | types | major | era | options: default · range · status |
|---|---|---|---|---|
| `logo-fin` | logo, titre, image | no | all | `entree` fondu  · m<br>`d1090` 0.65 · 0.27–2 s · m |

#### Transitions

| transition | options: default · range · status |
|---|---|
| `coupe` | — |
| `raccord` | — |
| `fondu-enchaine` | `T` 0.54 · 0.25–0.98 s · m |
| `passage-noir` | `T_fondu` 0.5 · 0.33–1.27 s · m<br>`noir` 0.5 · 0.4–1.5 s · m |
| `fondu-au-noir` | `T` 0.5 · 0.33–1.27 s · m |
| `fondu-depuis-noir` | `T` 0.5 · 0.34–2.71 s · m |
| `montee-du-noir` | `noir` 0.27 · 0.1–0.5 s · conv.<br>`d1090` 0.39 · 0.17–0.74 s · m |
| `glissade` | `T` 0.89 · 0.64–0.94 s · m<br>`sens` gauche  · m |
| `poussee` | `T` 0.75 · 0.6–1.02 s · m<br>`sens` gauche  · m |
| `bascule-lumiere` | `T` 2.4 · 1.2–2.6 s · m<br>`niveau` 85 · 30–100 % · conv. |

The counts for each recipe are in `scripts/recettes.json` (field `mesure`) and in `node scripts/build_motion.mjs --liste`.

### 5.1 What the recipes do, in one line

**Text**
- `coupe`: the element is there, fully visible, on the first frame. This is the most common case (14 titles out of 29).
- `avec`: arrives with the named element (the kicker with its word: 8 out of 11).
- `titre-fondu-montee`: the title fades in (easeInOutCubic, 0.77 s) and rises 15 u (easeOutExpo, 0.92 s); the rise starts 0.30 s after the fade.
- `titre-fondu`: fade in place, ease curve.
- `titre-balayage`: the word is revealed from left to right behind a soft front (blurred rectangular matte, linear).
- `phrase-zoom-arriere`: the sentence starts eight times too large and blurred, then settles (ease, 0.42 s).
- `chute`: drops from above, accelerating (easeInQuad, 0.23 s), with no bounce.
- `phrase-par-le-bas`: enters from below, already opaque.
- `liste-cascade`: one line every 0.10 s; each fades and rises at the same time (opacity starts with the rise, so you see the line rise); lines overlap.
- `liste-cascade-rapide`: one line every 0.05 s, small rise.
- `liste-par-le-bas`: opaque lines rising from the bottom, every 0.37 s (June 2020).
- `liste-au-fil`: one line when it is spoken (`intervalle`, or `options.temps`: the list of times); the block moves up half a line at each addition.
- `nom-remonte`: the name (`options.nom`) rises 10 u; the label and price fade and rise below it.
- `mot-remplace`: the old word disappears on the frame where the new one appears.
- `mot-fondu-enchaine`: the old word blurs and fades, the new one appears (1 case).
- `mot-glisse`: the old word rises as it fades, the new one arrives below (1 case).
- `chiffre-pose`: the number starts at ×4 and blurred, settles with no overshoot; the label follows: the middle of its fade (0.27 s) comes 0.23 s after the number's. The number never counts up (0 out of 27).
- `chiffre-croissance`: the number grows from ×0.22, overshoots by 5 % and comes back (June 2020).
- `carton-fondu`: film card, linear fade, no movement (7 out of 7).
- `carton-groupes`: the sentence builds up in groups of meaning; the line recenters at each addition.

**Objects**
- `produit-entree`: arrives from the right on the cut, brakes (out-cubic, 0.9 s), with 120° shutter motion blur.
- `produit-poussee`: the object grows slowly, at constant speed, for its whole presence.
- `produit-recul`: the object shrinks while braking (ease-out).
- `produit-pivot`: a 3D layer that turns from profile (90°) to front, at constant speed, 0.25 s after the cut. With a flat image, start at 70° so the object stays visible.
- `produit-rotation`: in-plane rotation, slow and partial (no full turn out of 17).
- `produit-flotte`: **no key on position** (the levitating product does not move: 10 holds out of 13); a soft shadow on the floor; option `derive`: a slow linear drift (**convention**). A floating bob does not exist in the corpus (0 out of 14).
- `eclate`: the pieces spread apart while braking (ease-out, 1.9 s) or close at constant speed (1.2 s).
- `balayage-lumiere`, `revelation-lumiere`: see § 4.4.

**Interfaces**
- `panneau-pose`: a panel arrives from an edge (out-expo) or slides within the page (ease), visible in 0.36 s; none beyond 0.5 s.
- `zoom-detail`: scale and position move together toward a point (`options.point`) with the era's curve, in 0.95 s. On a screenshot, `point` is in % of the image; on a `nul-camera`, in % of the composition. Then stay 2.5 to 7 s on the detail (**convention** drawn from the measured holds).
- `defilement`: the screenshot scrolls behind a fixed window (`options.fenetre`: width and height in u); `mode`: `presentation` (S-curve), `geste` (flick, long braking), `continu` (linear, 68 u/s).
- `empilement`: screens arrive one by one from the right and the row recenters; never two arrivals at once.
- `assombrir-autour`: see § 4.4.

**Camera** (on a `nul-camera`, or in the `camera` block)
- `camera-poussee`: linear push-in from start to end.
- `camera-recul`: pull-back that brakes.
- `camera-travelling`: translation at constant speed; the elements' `profondeur` creates the parallax.
- `camera-se-pose`: the move slows down to a stop (out-cubic).

**End**
- `logo-fin`: the name or logo arrives on a cut or a fade (out-quad, 0.65 s from 10 to 90 %), without moving.

---

## 6. Transitions

```json
"transitions": [
  { "type": "passage-noir", "temps": 16.4, "de": ["panneau"], "vers": ["logo", "mention"] }
]
```

| field | role |
|---|---|
| `type` | a transition from the table in § 5 |
| `temps` | start of the transition |
| `de` | elements that leave; their exit is set by the transition |
| `vers` | elements that arrive; their entrance is moved earlier or later by the transition (their recipe is usually `coupe`) |
| `options` | settings (§ 5, transitions table) |

| transition | what it does |
|---|---|
| `coupe` | the `de` elements stop at `temps`. This is the general case: more than 95 % of picture changes |
| `raccord` | a cut where the shape keeps its place and size (22 match cuts out of 22 are cuts) |
| `fondu-enchaine` | the `de` fade to 0 and the `vers` to their opacity, linear, 0.54 s; never more than 1 s |
| `passage-noir` | linear fade to black 0.5 s, black 0.5 s (never less than 0.40 s), fade from black 0.5 s |
| `fondu-au-noir` | linear fade to black until the end |
| `fondu-depuis-noir` | the image rises from black; linear if short, braked (out-cubic) beyond 0.68 s |
| `montee-du-noir` | cut to black, short black (0.27 s), then the image rises gently from black (in-out-cubic) |
| `glissade` | the `de` leave by one frame width to the side, the `vers` arrive from the other side, with motion blur; horizontal only |
| `poussee` | same gesture inside a fixed frame, shorter (0.75 s) |
| `bascule-lumiere` | the background slowly goes dark (in-out-sine) under the elements; `options.fond`: the `fond` element above which the scrim sits |

---

## 7. Rules the check enforces

`check_motion.py` reads motion.json, asks the generator for the exact timeline (`build_motion.mjs --plan`) and returns a report. An **error** blocks (exit code 1); a **warning** and an **info** do not.

| rule | level | basis |
|---|---|---|
| unknown recipe, transition, type or link; duplicate id | error | — |
| option outside the measured range | error | the corpus range (§ 5) |
| option outside a convention | warning | — |
| two major moves that overlap, except linked elements (`avec`, `options.nom`, `options.ancien`, `parent`, `de`/`vers` of the same transition) and `simultane` | error | rows: 0 overlaps out of 11; the label follows its number (15 out of 18) |
| two transitions that overlap | error | 25 out of 25 |
| arrivals in a row, or lines timed to the voice, that overlap | error | 11 out of 11 |
| exit other than `coupe` or `fondu` | error | 0 animated exits out of 18 |
| downward sweep, or two sweeps on the same element | error | 0 out of 11; a single pass, 11 out of 11 |
| scrim at 75 % or more | error | never all the way to black, 20 out of 20 |
| vertical slide | error | horizontal 32 out of 32 |
| number without `source` | error | no number without a source |
| `[TO PROVIDE]` left over | warning | to fill in before release |
| text visible less than 1.2 s + 0.3 s per word | warning; error below 60 % of that time | reading **convention** |
| too many words (title 6, sentence 12, kicker 4, line 6, label 5); line too wide (estimate 0.55 × size per character) | warning | **convention**; no measured instance above 12 words |
| kicker animated on its own | warning | 8 out of 11 arrive with their word |
| recipe from an era other than `comp.epoque` | warning | **convention** |
| less than 2.5 s on a detail after a zoom; end name held less than 1.25 s | warning | median hold 7.2 s; 2.6 s (17 names) |
| missing file | warning | a neutral placeholder will be drawn |
| text / background contrast below 4.5:1 | warning | readability **convention** |
| empty background visible (from the cut to 2 % opacity: `debut` plus the curve's soft start) under 0.10 s | info | the empty background holds 0.13 to 0.23 s (135 cases); only the side entrance starts on the cut (8 out of 8) |
| empty background visible beyond 0.30 s before a text or logo that fades in | warning | same basis; 0.30 s tolerance: **convention** |
| end name outside 47 to 51 % of the height | info | 15 out of 20 |

---

## 8. Full example

`assets/exemple-motion.json`: 20 s, 16:9, neutral and fictional. The generated script sits next to it (`assets/exemple-motion.jsx`), the images in `assets/exemple/`.

| time | what happens | recipe |
|---|---|---|
| 0.1 – 3.0 s | a kicker and a title fade and rise together | `avec` + `titre-fondu-montee` |
| 3.0 – 6.4 s | cut; the object enters from the right, with motion blur; the camera pushes in ×1.05; a light streak crosses it at 4.1 s | `produit-entree`, `camera-poussee`, `balayage-lumiere` |
| 6.45 – 9.6 s | three lines in cascade | `liste-cascade` |
| 9.8 – 12.4 s | the [TO PROVIDE] number starts large and blurred and settles; its label follows | `chiffre-pose` |
| 12.6 – 16.9 s | a schematic UI panel rises from the bottom; ×2 zoom on the toggle | `panneau-pose`, `zoom-detail` |
| 16.4 – 17.9 s | dip to black | `passage-noir` |
| 17.4 – 20.0 s | the fictional logo and its tagline, set on the cut, still | `logo-fin` + `avec` |

```json
{
  "version": 1,
  "comp": { "nom": "exemple-motion", "format": "16:9", "cadence": 30, "duree": 20, "fond": "fond", "epoque": "2024-2026" },
  "theme": {
    "couleurs": { "fond": "#0E1013", "texte": "#F4F4F2", "secondaire": "#9A9CA3", "accent": "#4C8DFF", "voile": "#000000" },
    "polices": { "titre": ["Inter-SemiBold", "Inter-Bold", "Arial-BoldMT"], "texte": ["Inter-Regular", "ArialMT"], "chiffre": ["Inter-Bold", "Arial-BoldMT"], "surtitre": ["Inter-Medium", "ArialMT"] }
  },
  "elements": [
    { "id": "fond", "type": "fond", "couleur": "fond", "recette": "coupe", "debut": 0 },
    { "id": "surtitre", "type": "surtitre", "contenu": "New", "position": [50, 41], "taille": 3.2, "couleur": "accent", "recette": "avec", "avec": "titre" },
    { "id": "titre", "type": "titre", "contenu": "One object. Nothing more.", "position": [50, 50], "taille": 9, "recette": "titre-fondu-montee", "debut": 0.1, "fin": 3.0 },
    { "id": "cam-produit", "type": "nul-camera", "position": [50, 50], "recette": "camera-poussee", "debut": 3.0, "fin": 6.4, "options": { "facteur": 1.05 } },
    { "id": "produit", "type": "image", "fichier": "exemple/produit.png", "position": [50, 52], "taille": 72, "ratio": 0.64, "parent": "cam-produit",
      "recette": "produit-entree", "debut": 3.0, "fin": 6.4,
      "puis": [ { "recette": "balayage-lumiere", "decalage": 1.1, "options": { "T": 0.5, "sens": "gauche" } } ] },
    { "id": "liste", "type": "liste", "lignes": ["Light.", "Quiet.", "Built to last."], "position": [50, 50], "taille": 6, "alignement": "gauche",
      "recette": "liste-cascade", "debut": 6.45, "fin": 9.6 },
    { "id": "chiffre", "type": "chiffre", "contenu": "[TO PROVIDE]", "libelle": "hours unplugged", "source": "[TO PROVIDE]", "position": [50, 46], "taille": 14,
      "recette": "chiffre-pose", "debut": 9.8, "fin": 12.4 },
    { "id": "cam-panneau", "type": "nul-camera", "position": [50, 50], "recette": "zoom-detail", "debut": 13.3, "options": { "facteur": 2.0, "point": [64.2, 60.1] } },
    { "id": "panneau", "type": "capture", "fichier": "exemple/panneau.png", "position": [50, 52], "taille": 56, "ratio": 1.5, "parent": "cam-panneau",
      "recette": "panneau-pose", "debut": 12.6, "fin": 16.9, "options": { "depuis": "bas" } },
    { "id": "logo", "type": "logo", "fichier": "exemple/logo.png", "nom": "exemple", "position": [50, 49], "taille": 9, "ratio": 4.2,
      "recette": "logo-fin", "debut": 17.4, "fin": 20, "options": { "entree": "coupe" } },
    { "id": "mention", "type": "phrase", "contenu": "Coming soon.", "position": [50, 59], "taille": 2.8, "couleur": "secondaire", "recette": "avec", "avec": "logo", "fin": 20 }
  ],
  "transitions": [
    { "type": "passage-noir", "temps": 16.4, "de": ["panneau"], "vers": ["logo", "mention"] }
  ]
}
```

The check of this example returns 0 errors and 1 warning (the number is still to be provided).

---

## 9. The generated script

### 9.1 Its shape

- **ExtendScript ES3**: `var` and `function` only; no `let`, `const`, arrow function, template literal, native JSON or ES5 array method. It uses only the After Effects object API (`app.project.items.addComp`, `layers.addText/addShape/addSolid/addNull`, internal "ADBE …" match names, `setValueAtTime`, `KeyframeEase`, `setTemporalEaseAtKey`, `ImportOptions`…). The generator checks the syntax and these bans on every run.
- **Header**: the list of recipes, and the table of curves used with their translation (influence and speed of each key) and their counts.
- **The engine** (`md_…`): about twenty short functions. `md_anime(property, t0, v0, t1, v1, curve)` sets two keys and computes the `KeyframeEase` from the cubic-bezier: you can change a curve or a value by hand in the script.
- **Seven phases**, commented: layers from back to front; parenting; animations; layer presence (entrance, exit); transitions; lights (they copy the animated element, hence their place at the end); camera.
- **Clean names**: each layer is named `id — role` (`produit — light sweep`, `[PLACEHOLDER] panneau …` for a placeholder). Each recipe sets a **layer marker** at the start of its animation, giving the recipe, the curve and the duration: it names the keys.
- **Report**: the script returns "N layers, M keys" and the list of placeholders.
- **Files**: each image is looked for first next to the script (After Effects knows the script's folder), then at its absolute path at generation time (EffectCraft). `--relatif` writes no absolute path, to share a script; on another machine, regenerate the script.

### 9.2 Pitfalls handled

| pitfall | fix in the script |
|---|---|
| EffectCraft ignores interpolations and eases on a composition that is not active (found on 21/10) | the composition is opened in the viewer (`comp.openInViewer()`) before any key |
| new keys are linear; a `KeyframeEase` alone changes nothing | the BEZIER type is set before the eases |
| two keys less than one frame apart merge | times snapped to frames, at least one frame apart |
| a multi-dimensional property expects one `KeyframeEase` per dimension (Scale: 3) | `md_anime` counts the property's dimensions |
| spatial position mixes the axes | position with separate dimensions: X and Y are two one-dimensional properties |
| parenting compensates for the parent's transform | camera nulls set neutral (anchor = position) and parented before their keys: nothing moves |
| a shape layer counts its vertices from its anchor point | shapes drawn around the anchor (0, 0), placed by position |
| mask expansion is not rendered; a query on an animated mask froze the app | no masks: a title's sweep, a scroll's window and the lights use track mattes |
| a layer that is too wide (~27,000 px) is no longer drawn | no layer wider than the element's diagonal × 1.2 or than the frame |
| `File.exists` returns false in EffectCraft even when the file exists | the import is attempted; if it fails, a neutral placeholder is drawn |
| missing fonts are not reported | font list with fallback; After Effects 24 and later picks the first installed |
| the "Blurriness" setting of Gaussian blur | measured in EffectCraft: setting = 2 × σ (2.00, 1.98, 1.97 for 10, 20, 40). In After Effects: check by eye (**convention**) |
| the user's project | no file commands: the script does not save, open or close anything; it only replaces the composition with the same name |

---

## 10. Commands

```bash
python3 scripts/check_motion.py motion.json                 # check (exit code 1 if there is an error)
node scripts/build_motion.mjs motion.json                   # writes motion.jsx
node scripts/build_motion.mjs motion.json --prefixe TEST-   # same script, prefixed composition (trials)
node scripts/build_motion.mjs --liste                       # recipes and transitions, with their counts
node scripts/build_motion.mjs --recettes                    # regenerates scripts/recettes.json (read by the check)

# EffectCraft (launch the app with: open -a EffectCraft --args --control 9877)
python3 scripts/ec.py activer                               # bring to front: the app only answers then
python3 scripts/ec.py script motion.jsx                     # runs the script
python3 scripts/ec.py frames "launch" controle/ --pas 0.5 --max 640   # one frame every 0.5 s
python3 scripts/ec.py frame "launch" 4.3 image.png 1920     # one frame
python3 scripts/ec.py render "launch" rendu.mp4             # H.264 render (waits for the end)
```

`ec.py` refuses commands that save, open or close the project, unless given `--autoriser`. Each request has a timeout (`--delai`, 180 s; 1,800 s for a render): a frozen app does not freeze the terminal. `--relance` brings the app back to the front and resends the request once.

---

## 11. What this format does not do (conventions and limits)

- No sound: the corpus is silent; no link between motion and music is measured.
- No counter, repeated bounce, typewriter, text rotation or full turn: none of these exist in the corpus (0 out of 145 texts; 0 out of 17 rotations).
- A sinusoidal float does not exist either (0 out of 14): `produit-flotte` does not animate the object.
- Smoke on a drop, a sliding focus pull, the offset between pieces of an exploded view, the blur intensity of slides: not measured, not reproduced, or set by **convention**.
- 9:16 and 1:1: none observed; same values in u (**convention**).
- After Effects was not used for testing: the script uses only the shared object API and was run in EffectCraft. The example and six test compositions cover the 39 recipes and the 10 transitions; check frames and MP4 renders were reviewed.
