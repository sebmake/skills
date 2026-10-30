# The `film.json` format

`film.json` describes a product film and its cut-downs for social media. The engine reads it:

- `scripts/check_film.py film.json` checks the file (durations, reading time, figures, visuals, safe zones).
- `node scripts/build_film.js film.json --planche` makes the review sheet, with no video render.
- `node scripts/build_film.js film.json --rendu` builds the HyperFrames projects and renders the MP4s.

Core rules, repeated here because the format carries them:

- **No voice.** There is no "voice" field. Meaning comes through the cards and the music.
- **Provided music or none.** A local file the user has the rights to, or `null`. Never a web address, never music that was searched for or generated.
- **No invented figures.** A figure only comes in through `texte.chiffre`, with its `source`. Without a provided figure, the card shows `[TO PROVIDE]`, dimmed.
- **The grammar, never the brand.** No font, logo, device or signature from another brand.

File paths are **relative to the folder of `film.json`**. Durations are in seconds.

---

## 1. Overview

```json
{
  "version": 1,
  "meta": { ... },
  "theme": { ... },
  "musique": null,
  "plans": [ { ... }, { ... } ],
  "declinaisons": [ { ... } ]
}
```

| Block | Role |
|---|---|
| `meta` | what we are making: product, message, audience, formats, target duration |
| `theme` | the branding: colors by role, fonts with fallbacks, logo |
| `musique` | the provided track, or `null` (silent film) |
| `plans` | the long film, in order: one shot = one scene = one recipe |
| `declinaisons` | the social versions (cut-downs): format, duration, chosen shots or rule |

---

## 2. `meta`

| Field | Type | Required | Meaning |
|---|---|---|---|
| `titre` | text | yes | project name (used for file names) |
| `produit` | text | yes | the exact product name, as it is written on screen |
| `message` | text | yes | the sentence the viewer should remember (not shown as is) |
| `public` | text | yes | who the film speaks to |
| `langue` | text | no | `en` by default |
| `formats` | list | yes | requested formats: `16:9` (the film), and those of the cut-downs (`9:16`, `1:1`) |
| `duree_cible_s` | number | yes | target duration of the long film, 60 to 120 s |
| `fps` | number | no | 30 by default |

---

## 3. `theme`

```json
"theme": {
  "source": "HEX values given by the user on 10/21",
  "couleurs": {
    "fond_sombre": "#0E1013",
    "fond_clair": "#F2F1EE",
    "texte_sur_sombre": "#F4F4F2",
    "texte_sur_clair": "#16171A",
    "accent": "#E9A23B",
    "accent_2": "#C8662E"
  },
  "polices": {
    "titres": { "famille": "Inter", "repli": ["Arial", "sans-serif"], "fichier": null, "graisse": 700 },
    "texte":  { "famille": "Inter", "repli": ["Arial", "sans-serif"], "fichier": null, "graisse": 400 }
  },
  "logo": { "sur_sombre": "visuels/logo-clair.svg", "sur_clair": "visuels/logo-sombre.svg" }
}
```

| Field | Meaning |
|---|---|
| `source` | where the colors come from: a design system link, or "HEX values provided" |
| `couleurs.fond_sombre` | background of dark shots (a charcoal rather than pure black) |
| `couleurs.fond_clair` | background of light shots (never pure `#FFFFFF`: 0 light films out of 7 use it) |
| `couleurs.texte_sur_sombre`, `texte_sur_clair` | card text color, depending on the background |
| `couleurs.accent` | **a single** strong color: halo, name, detail. Required |
| `couleurs.accent_2` | optional: a second halo tint |
| `polices.titres` | name, punch words, figures. `graisse` (weight) 600 or 700 |
| `polices.texte` | card sentences. `graisse` 400 or 500 |
| `polices.*.repli` | fallback fonts, in order. The engine adds `sans-serif` at the end |
| `polices.*.fichier` | optional: a provided `.woff2`, `.woff`, `.ttf` or `.otf` file; it is embedded in the render |
| `logo` | optional. `sur_sombre` and `sur_clair` (SVG or transparent PNG). One is enough. Missing file: the end shot is made **without a logo** (never a fake logo) |

Safe fonts that need no file: Inter, Roboto, Open Sans, Lato, Nunito, Montserrat, Poppins, Outfit, Oswald, League Gothic, Archivo Black, Playfair Display, EB Garamond, Space Mono, IBM Plex Mono, JetBrains Mono, Source Code Pro. HyperFrames 0.8.181 fetches them from Google Fonts on the first build, then caches them (`~/.cache/hyperframes/fonts/`): it needs the network once. A user's own font goes through `fichier` (embedded, no network).

Fonts the checker rejects (fonts tied to a device brand): `SF Pro`, `SF Pro Display`, `SF Pro Text`, `SF Compact`, `SF Mono`, `New York`, `San Francisco`, `-apple-system`, `BlinkMacSystemFont`, `system-ui`, `ui-sans-serif`, `Myriad`.

---

## 4. `musique`

`null`: the film is silent. Otherwise:

```json
"musique": {
  "fichier": "musique/piste.mp3",
  "droits_confirmes": true,
  "debut_s": 0,
  "volume": 0.9,
  "fondu_sortie_s": 2,
  "caler_coupes": false,
  "temps_s": [],
  "bpm": null,
  "premier_temps_s": 0
}
```

| Field | Meaning |
|---|---|
| `fichier` | local path (`.mp3`, `.m4a`, `.wav`, `.aac`). An `http…` address is rejected |
| `droits_confirmes` | must be `true`: the user said they have the rights |
| `debut_s` | where to start in the track |
| `volume` | 0 to 1 |
| `fondu_sortie_s` | fade-out at the end, 2 s by default |
| `caler_coupes` | `true`: each shot start is moved to the nearest beat (±0.25 s at most). **Convention**: cutting on the music is not shown in the corpus (16 cuts out of 62 land on a strong attack, 16.4 expected by chance) |
| `temps_s` | optional: list of strong beats, in seconds into the track |
| `bpm`, `premier_temps_s` | optional: a regular grid, if `temps_s` is empty |

If `caler_coupes` is `true` with no `temps_s` and no `bpm`, the engine runs `npx hyperframes beats` on the track and reads the grid it produces.

Each cut-down can have its own `musique_debut_s` (for example, to start at the chorus).

---

## 5. `plans`

One shot = one HyperFrames scene = one recipe. The order of the list is the order of the film.

```json
{
  "id": "p07",
  "recette": "panneau",
  "role": "preuve",
  "groupe": "preuve-heure",
  "priorite": 1,
  "duree_s": 5,
  "fond": "clair",
  "visuels": { "capture": "visuels/appli-planning.png" },
  "texte": { "type": "libelle", "contenu": "Daylight" },
  "mouvement": { "detail": { "zone": [52, 30, 40, 42], "mode": "zoom" } },
  "transition": "coupe",
  "notes": "The curve of the day, then we go into the late afternoon."
}
```

| Field | Type | Meaning |
|---|---|---|
| `id` | text | unique, lowercase letters, digits and hyphens (`p01`, `revel`) |
| `recette` | text | one of the 12 recipes in § 6 |
| `role` | text | place in the story: `accroche` (hook), `contexte` (context), `preuve` (proof), `revelation` (reveal), `chute` (closing line), `respiration` (breath), `fin` (end). Used by the checker and by the `auto` rule of cut-downs |
| `groupe` | text | optional: shots in the same group are kept or dropped together (a card and the shot that proves it) |
| `priorite` | 1, 2 or 3 | optional: 1 = keep first in a short cut-down |
| `duree_s` | number | duration of the shot in the long film |
| `fond` | text | `sombre` (dark), `clair` (light) or `accent`. Each recipe has a default background |
| `visuels` | object | the shot's files, by "slot" (see the recipe). A missing file is replaced by a **neutral drawn fallback** (gray shapes, no brand, no text) and reported |
| `texte` | object or `null` | the on-screen text (§ 5.1) |
| `mouvement` | object | motion settings specific to the recipe (§ 6). All optional |
| `transition` | text | how the shot **enters**: `coupe` (cut, default, 14/14 films), `fondu` (crossfade 0.4 s; cannot be verified in the corpus, keep it rare), `noir` (the previous shot fades out in 0.4 s, this one comes out of black in 0.5 s; 10/14 films go through black at least once) |
| `notes` | text | intent, for the review sheet. Never shown in the film |

### 5.1 `texte`

| `type` | Fields | Recipes | Rules |
|---|---|---|---|
| `phrase` | `contenu`, `groupes` (optional), `affichage` | `carton`, `mot-sur-image` | 12 words at most. Up to 6 words: shown as one block. From 7 to 12: built in 2 or 3 groups of meaning |
| `mot` | `contenu` | `carton`, `mot-sur-image` | 1 or 2 "punch" words, large size. One or two per film |
| `chiffre` | `chiffre`, `libelle`, `source` | `carton` | `chiffre` is `null` until the user gives it: the card shows `[TO PROVIDE]`, dimmed. `libelle` holds the basis of comparison |
| `libelle` | `contenu` | `panneau`, `empilement`, `mur`, `orbite`, `eclate`, `macro` | feature name, 1 to 4 words, placed next to the image |
| `nom` | `contenu`, `ligne` (optional) | `fin`, `revelation` | the product name; `ligne` = a provided call-to-action line ("Coming soon", an address, a provided date) |

- `groupes`: the sentence split by the author, for example `["Cool by morning.", "Warm by night."]`. Joined together, they must give back `contenu`. Without `groupes`, the engine splits at punctuation, otherwise in the middle.
- `affichage` (display): `bloc`, `groupes` or `mot-a-mot` (block, groups, word by word). Default: `bloc` up to 6 words, `groupes` beyond.
- The words never change from one format to another. Only the line breaks change.
- Sentence case, no exclamation mark, no all caps for a sentence.

---

## 6. The 12 recipes

Each recipe is an engine function (`RECETTES` in `build_film.js`). "Slots" = keys of `visuels`. Counts come from the corpus analyses; "convention" = not observed.

| Recipe | What you see | Slots | `mouvement` | Default background | Recommended duration |
|---|---|---|---|---|---|
| `noir` | passing through black, optional point of light (black 10/14 films; point of light 3/14) | none | `point` (boolean) | black | 0.5 to 1.5 s |
| `lisere` | the object drawn only by its lit edge, on charcoal (3/14) | `objet` (cut-out PNG) | `cote` (`gauche`, `droite`) | dark | 3 to 5 s |
| `macro` | an extreme close-up that slides, with a sliding focus (macro 12/14; sliding focus: convention) | `image` (macro or cut-out object) | `echelle` (1.2 to 3.5; 2.6 by default; capped at 1.5 × a photo's resolution), `sens` (`gauche`, `droite`, `haut`, `bas`), `point` ([x, y] in % of the image) | dark | 1.5 to 3 s |
| `orbite` | slow simulated 3D rotation, ±12° at most, a sliding reflection, levitation (rotation 8/14; levitation 9/14) | `objet`, or `vues` (list of 2 to 5 close views) | `angle` (≤ 12), `sens` (1 or -1) | light | 3 to 6 s |
| `eclate` | an exploded view in layers that closes up (exploded view 6/14; assembly 7/14) | `pieces` (list of PNGs of the same size, bottom to top), or `objet` alone (cut into strips) | `axe` (`vertical`, `profondeur`), `bandes` (3 to 6) | light | 4 to 6 s |
| `revelation` | the whole object, alone: comes out of black, halo, levitation, a light sweep that crosses once, slow pull-back (sweep 4/14; halo 3/14; pull-back 6/14) | `objet` | `recul` (boolean), `halo` (boolean) | dark | 5 to 8 s |
| `panneau` | interface without a device, as a floating panel, then we go into a detail (zoom: the rest blurs and fades) or light it up (spotlight: the whole frame darkens, the element grows in the center) (no device 7/12; push toward a detail 6/12) | `capture` | `detail`: `{ "zone": [x, y, w, h] in % of the screenshot, "mode": "zoom" or "projecteur" }` | light | 3 to 6 s |
| `empilement` | 2 to 5 windows that arrive from the depth and stack up (assembly 3/12); as a reveal: slow pull-back and accent halo (convention); name possible in a cut-down (`avec_nom`) | `captures` (list) | none | light | 3.5 to 5 s |
| `carton` | typographic card on a plain background: sentence, word or figure (the card is a shot of its own: 23/33) | none | none | dark | depends on the words (§ 7) |
| `mot-sur-image` | 1 to 4 words placed in the calm area of an image (1 case in an appendix; convention) | `image` | `zone` (`centre`, `haut`, `bas`, `gauche`, `droite`), `point` ([x, y] %: subject to keep in 9:16 and 1:1) | image | 2.5 to 4 s |
| `mur` | a wall of icons or visuals: a grid that fills up, spotlight on one (`grille`), or a parade one by one every 0.5 s (`defile`) (parade 1/12; spotlight measured on 1 instance) | `elements` (list) | `mode` (`grille`, `defile`), `focus` (position of the lit item, starting at 1) | dark | 3 to 6 s |
| `fin` | the name alone, centered, then the logo and a call-to-action line if provided (name at the end: 21/24 segments) | none (the logo comes from `theme.logo`) | `taille` (`heros` or `discret`) | dark | 3 to 4.5 s |

The checker rejects any other value of `recette`.

Framing of cut-out PNGs: the engine measures the useful box (non-transparent pixels) and frames that box, not the whole canvas. `pieces` must share the same canvas (same size, each part in its place): the exploded view spreads them apart, then puts them back.

Text of `revelation`: only `{ "type": "nom" }`, used when a cut-down asks for `avec_nom` (otherwise the name from `meta.produit`). `avec_nom` also works on an `empilement` (reveal of a software product).

---

## 7. What the engine computes (and `check_film.py` checks)

- **Card duration** (`grammaire-film.md` § 6.4, a convention tuned to what was observed): at least `1.2 s + 0.3 s × words`; at least 1.5 s for a sentence, 1.0 s for a single word, 2.5 s for the name. A card built in groups counts from the last group that appears, then holds for at least `1.0 + 0.1 × words`.
- **Words**: 12 at most per card (106 cards out of 109). Beyond 6, built in groups.
- **Characters per line**: 42 in 16:9, 22 in 9:16, 26 in 1:1 (a convention that leaves room for languages longer than English), and never more than the allowed line width: the engine breaks earlier rather than shrinking the type size (about 20 characters at 72 px in 9:16, on an 800 px line). The break falls between two groups, otherwise after punctuation, otherwise at the most balanced point.
- **Sizes** (px): card 58 / 72 / 62; punch word 150 / 150 / 124; hero name 124 / 132 / 116; discreet name 56 / 76 / 68 (16:9 / 9:16 / 1:1).
- **Safe zones**: 9:16: text between y = 230 and 1,498 px, x from 65 to 1,015 px, optical center y = 864; 1:1: 86 px margins; 16:9: the central 80%.
- **The name** comes last: never before 76% of the film (0 product films out of 20 show it earlier).
- **The reveal** of the whole object: after 60% of the film (13 films out of 14).

---

## 8. `declinaisons`

```json
"declinaisons": [
  {
    "id": "vertical-30",
    "format": "9:16",
    "duree_cible_s": 30,
    "plans": [
      "p09",
      { "id": "p03", "duree_s": 3 },
      { "id": "p16", "duree_s": 5, "avec_nom": true },
      "p06", "p07", "p13", "p17", "p18"
    ]
  },
  { "id": "carre-15", "format": "1:1", "duree_cible_s": 15, "regle": "auto" }
]
```

| Field | Meaning |
|---|---|
| `id` | name of the cut-down (used for the file name) |
| `format` | `16:9`, `9:16` or `1:1` |
| `duree_cible_s` | 15 to 60 s |
| `plans` | the chosen shots, in the wanted order: an `id`, or `{ "id", "duree_s", "avec_nom", "sans_texte" }`. `avec_nom` (recipe `revelation` or `empilement`): the object or the screens, then the name alone (≥ 2.5 s; a shot of at least 4 s, 4.5 to 5.5 s for an `empilement`). `sans_texte`: removes a shot's label (fewer words, never different words) |
| `regle` | `auto` instead of `plans`: the engine chooses according to the 15 / 30 / 45 / 60 s template in `declinaisons.md` § 3.2. Hook: a `mot-sur-image` of 4 words at most, otherwise the thesis card (`role` `accroche`), otherwise the card with `role` `chute`; at 20 s and under, the shortest one if it has 4 words at most. An opening card gets the product visual behind it, blurred and veiled (frame 0 full). Then 0 to 2 `contexte` groups, the `revelation` or the `empilement` that stands in for it (with the name up to 37 s), 1 to 4 `preuve` groups (`priorite` 1 first, film order kept), the `chute` (beyond 20 s, except after a card) and the `fin`. Up to 37 s, a proof that has its own card loses its labels; at 15 s, it shrinks to its card and one shot |
| `musique_debut_s` | optional: where to start in the track |

Rules the engine applies (conventions from `declinaisons.md`, § 3):

- **Recompose, don't crop.** Each format is its own HyperFrames composition (`data-width`, `data-height`). The recipes recompute their layout: object enlarged in 9:16, text above the image, one line per group, and so on.
- Durations that are not given are adjusted to land on `duree_cible_s`, without going under a card's minimum reading time or the recipe's minimum.
- `noir` shots are removed. Frame 0 is full: the first shot does not enter through black, and the first card is readable at 0.2 s.
- End: no final black longer than 0.5 s (platforms replay in a loop).
- The real duration can go over the target when the reading minimums require it; the checker blocks beyond ±10%.

---

## 9. Full example

The file `assets/exemple-film.json` is the reference example: a fictional desk lamp ("Clarity"), silent, a 65.3 s 16:9 film (17 shots), a 30 s 9:16 cut-down (explicit list) and a 15.4 s 1:1 one (`regle: auto`). The figure in `p10` is not provided: it shows as `[TO PROVIDE]`, dimmed. Its neutral visuals are in `assets/exemple-visuels/`. Here is its full text:

```json
{
  "version": 1,
  "meta": {
    "titre": "Clarity",
    "produit": "Clarity",
    "message": "A desk lamp that adjusts its own light as the day goes on.",
    "public": "People who work at their desk all day",
    "langue": "en",
    "formats": ["16:9", "9:16", "1:1"],
    "duree_cible_s": 65,
    "fps": 30
  },
  "theme": {
    "source": "Example HEX values (fictional product)",
    "couleurs": {
      "fond_sombre": "#0E1013",
      "fond_clair": "#F2F1EE",
      "texte_sur_sombre": "#F4F4F2",
      "texte_sur_clair": "#16171A",
      "accent": "#E9A23B",
      "accent_2": "#B8642A"
    },
    "polices": {
      "titres": { "famille": "Inter", "repli": ["Arial", "sans-serif"], "fichier": null, "graisse": 700 },
      "texte": { "famille": "Inter", "repli": ["Arial", "sans-serif"], "fichier": null, "graisse": 400 }
    },
    "logo": { "sur_sombre": "exemple-visuels/logo-clair.svg", "sur_clair": "exemple-visuels/logo-sombre.svg" }
  },
  "musique": null,
  "plans": [
    {
      "id": "p01", "recette": "noir", "role": "accroche", "duree_s": 1.2,
      "mouvement": { "point": true },
      "notes": "Black. A point of light comes on, then fades out."
    },
    {
      "id": "p02", "recette": "lisere", "role": "accroche", "duree_s": 4.3,
      "visuels": { "objet": "exemple-visuels/lampe.png" },
      "notes": "We guess the lamp from its lit edge alone. The whole object stays hidden."
    },
    {
      "id": "p03", "recette": "carton", "role": "accroche", "duree_s": 3.8, "fond": "sombre",
      "texte": { "type": "phrase", "contenu": "A lamp that follows your day." },
      "notes": "The thesis sentence, up front."
    },
    {
      "id": "p04", "recette": "macro", "role": "contexte", "duree_s": 3.0,
      "visuels": { "image": "exemple-visuels/matiere.jpg" },
      "mouvement": { "echelle": 1.6, "sens": "gauche", "point": [50, 70] },
      "notes": "Brushed metal and a line of light; the focus slides."
    },
    {
      "id": "p05", "recette": "macro", "role": "contexte", "duree_s": 2.5,
      "visuels": { "image": "exemple-visuels/lampe.png" },
      "mouvement": { "echelle": 2.6, "sens": "droite", "point": [57, 5] },
      "notes": "The joint and the light bar, up close."
    },
    {
      "id": "p06", "recette": "carton", "role": "preuve", "groupe": "preuve-heure", "priorite": 1, "duree_s": 4.0, "fond": "clair",
      "texte": { "type": "phrase", "contenu": "Cool by morning. Warm by night.", "groupes": ["Cool by morning.", "Warm by night."], "affichage": "groupes" },
      "notes": "A statement, then its payoff."
    },
    {
      "id": "p07", "recette": "panneau", "role": "preuve", "groupe": "preuve-heure", "priorite": 1, "duree_s": 5.0, "fond": "clair",
      "visuels": { "capture": "exemple-visuels/appli-planning.png" },
      "texte": { "type": "libelle", "contenu": "Daylight" },
      "mouvement": { "detail": { "zone": [52, 18, 40, 46], "mode": "zoom" } },
      "notes": "The curve of the day, then we go into the late afternoon."
    },
    {
      "id": "p08", "recette": "orbite", "role": "preuve", "groupe": "preuve-geste", "priorite": 2, "duree_s": 4.0, "fond": "clair",
      "visuels": { "objet": "exemple-visuels/piece-tete.png" },
      "mouvement": { "angle": 12 },
      "notes": "The lamp head alone, turning slowly."
    },
    {
      "id": "p09", "recette": "mot-sur-image", "role": "preuve", "groupe": "preuve-geste", "priorite": 2, "duree_s": 3.2,
      "visuels": { "image": "exemple-visuels/photo-bureau.jpg" },
      "texte": { "type": "phrase", "contenu": "Just one gesture." },
      "mouvement": { "zone": "gauche", "point": [70, 50] },
      "notes": "The desk at night; the sentence on the dark wall."
    },
    {
      "id": "p10", "recette": "carton", "role": "preuve", "groupe": "preuve-charge", "priorite": 3, "duree_s": 3.6, "fond": "sombre",
      "texte": { "type": "chiffre", "chiffre": null, "libelle": "hours of light per charge", "source": null },
      "notes": "Figure to be provided by the user: nothing is invented."
    },
    {
      "id": "p11", "recette": "noir", "role": "respiration", "duree_s": 0.8,
      "notes": "A breath before the app chapter."
    },
    {
      "id": "p12", "recette": "empilement", "role": "preuve", "groupe": "preuve-appli", "priorite": 2, "duree_s": 4.5, "fond": "clair",
      "visuels": { "captures": ["exemple-visuels/fenetre-1.png", "exemple-visuels/fenetre-2.png", "exemple-visuels/fenetre-3.png"] },
      "texte": { "type": "libelle", "contenu": "Your scenes" },
      "transition": "coupe",
      "notes": "The app windows arrive from the depth."
    },
    {
      "id": "p13", "recette": "mur", "role": "preuve", "groupe": "preuve-appli", "priorite": 2, "duree_s": 4.5, "fond": "sombre",
      "visuels": { "elements": ["exemple-visuels/scene-1.png", "exemple-visuels/scene-2.png", "exemple-visuels/scene-3.png", "exemple-visuels/scene-4.png", "exemple-visuels/scene-5.png", "exemple-visuels/scene-6.png", "exemple-visuels/scene-7.png", "exemple-visuels/scene-8.png"] },
      "mouvement": { "mode": "grille", "focus": 3 },
      "notes": "The light scenes; the \"reading\" scene lights up."
    },
    {
      "id": "p14", "recette": "eclate", "role": "contexte", "duree_s": 5.2, "fond": "clair",
      "visuels": { "pieces": ["exemple-visuels/piece-base.png", "exemple-visuels/piece-tige.png", "exemple-visuels/piece-tete.png"] },
      "mouvement": { "axe": "vertical" },
      "transition": "noir",
      "notes": "The three parts come together."
    },
    {
      "id": "p15", "recette": "revelation", "role": "revelation", "duree_s": 7.6, "fond": "sombre",
      "visuels": { "objet": "exemple-visuels/lampe.png" },
      "mouvement": { "recul": true, "halo": true },
      "transition": "noir",
      "notes": "The whole object, at last: halo, a sweep of light, slow pull-back."
    },
    {
      "id": "p16", "recette": "carton", "role": "chute", "duree_s": 3.6, "fond": "sombre",
      "texte": { "type": "phrase", "contenu": "Your desk, finally well lit." },
      "notes": "The closing line, just before the name."
    },
    {
      "id": "p17", "recette": "fin", "role": "fin", "duree_s": 4.5, "fond": "sombre",
      "texte": { "type": "nom", "contenu": "Clarity", "ligne": "Coming soon" },
      "mouvement": { "taille": "heros" },
      "notes": "The name alone, then the call-to-action line and the logo."
    }
  ],
  "declinaisons": [
    {
      "id": "vertical-30",
      "format": "9:16",
      "duree_cible_s": 30,
      "plans": [
        { "id": "p09", "duree_s": 2.6 },
        "p03",
        { "id": "p15", "duree_s": 5.0, "avec_nom": true },
        "p06",
        "p07",
        "p13",
        "p16",
        { "id": "p17", "duree_s": 3.2 }
      ]
    },
    { "id": "carre-15", "format": "1:1", "duree_cible_s": 15, "regle": "auto" }
  ]
}
```

---

## 10. Commands

```bash
# 1. check
python3 scripts/check_film.py film.json            # exit code 0 = nothing blocking; 1 = errors

# 2. review sheet (one image per shot, with duration and text), no render
node scripts/build_film.js film.json --planche --sortie ./sortie

# 3. render (after the review sheet is approved)
node scripts/build_film.js film.json --rendu --sortie ./sortie            # film + cut-downs
node scripts/build_film.js film.json --rendu --seulement vertical-30      # a single output
node scripts/build_film.js film.json --rendu --qualite draft              # quick draft
node scripts/build_film.js film.json --rendu --check                      # + npx hyperframes check (WCAG contrast, overflow)
```

- The engine runs `check_film.py` again on the resolved outputs (adjusted durations, real lines). An error stops the render; `--force` overrides it.
- The engine also runs `npx hyperframes lint` on each project. HyperFrames calls run without telemetry (`HYPERFRAMES_NO_TELEMETRY=1`), and `snapshot` runs without description by an external service (`--describe false`).
- Benchmarks measured on the example (Mac, `standard` quality, 30 fps): 33 s of compute for 65 s of 16:9 film, 17 s for 30 s in 9:16, 12 s for 15 s in 1:1; review sheet: a few seconds per output.

Outputs: `sortie/projets/<name>/` (HyperFrames projects, which open in `npx hyperframes preview`), `sortie/planches/<name>.png`, `sortie/rendus/<name>.mp4`.
