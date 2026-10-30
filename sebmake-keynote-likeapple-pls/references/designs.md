# Designs: how each slide is drawn

This file says, archetype by archetype, what the slide shows: the visual content (a product in the light, an interface in a device, a full-bleed photo, an icon, a material), the possible compositions, the depth (shadow, halo, object that leaves the frame) and the visual to ask the user for. It completes `style-visuel.md`, which gives the text measures (size, weight, line spacing, colors). We point to it; we don't copy it.

Everything comes from the 8 keynotes of the corpus (2019 to 2026), watched frame by frame: about 590 frames for these cards, measured to the pixel when a value is given. The grammar, never the brand: no product, no recognizable device, no font, no logo and no on-screen text from the corpus goes into the skill. The devices the engine draws are generic: no notch, no buttons, no camera.

## Contents

1. How to read
2. Choosing a design: the method, the engine's variants, an example block
3. Rules shared by all cards
4. Text: A1 Title card · A2 Icon or logo + name · A3 Typographic agenda · A4 Thesis sentence · A7 List without bullets · A8 Checklist · A17 Quote or testimonial · A21 Name and role lower third
5. Figures and proof: A5 Big figure + label · A6 Comparison chart · A11 Diagram with a highlighted block · A15 Wall of abundance · A16 Partner logos
6. Product and image: A9 Object + text · A10 Full-bleed screenshot · A12 Inside view / exploded view · A13 Product alone · A18 Full-bleed photo · A22 Wide shot + screen · A23 Presenter in the slide · A24 Set without a screen · A25 Hands-on demo
7. Recap and conversion: A14 Bento · A19 Price · A20 Availability · Final slide · Colorway lineup · Timeline

## 1. How to read

- **N/8 counts**: the number of keynotes, out of the 8, where the variant appears at least once. v5 and v6 are live (2019); v1 and v2 (2020), v7 (2024), v8 and v3 (2025), v4 (2026) are prerecorded. A variant seen in a single keynote is still a variant, not a rule.
- **Statuses**: *measured* (to the pixel), *estimated* (by eye, within 2 %), *convention* (a choice of the skill, not observed).
- **Positions**: on a 100 × 100 canvas; x, y = top left corner; w, h = width, height; in % of the width (W) and of the height (H). 1 % W = 0.1 in; 1 % H = 0.056 in. Engine margin: 6 % W. A negative x, or an x + w past 100, means the object leaves the frame. For text, y and h bound the cap-height zone, as in `style-visuel.md`.
- **Sizes**: given for Inter (size ≈ cap in % H × 5.6). For another font, redo the calculation in `style-visuel.md` §0.
- **Eight parts per card**: 1 Role and moment · 2 Canonical composition (zones and sketch) · 3 Observed variants · 4 Visual content (type, framing, treatment, accent) · 5 Typography (only what changes from `style-visuel.md`) · 6 Build and animation · 7 Visual brief and fallback · 8 Avoid.
- **In the engine**: at the top of §3, the `slide.variante` values that `build_deck.js` draws, and what it does without a variant. The fields each variant reads are in `deck-spec.md`, “Variants”. What a card describes outside this list (a morph, a filmed shot) is done by hand in the presentation app, or in video.
- **Stage shots (A22 to A25)**: these are video shots, not slides. Their card says what a projected deck keeps of them, and what to film for a video.

## 2. Choosing a design

At the “Design slide by slide” step (`SKILL.md`), for each line of the run of show. These six rules are conventions of the skill, drawn from the cards:

1. **The archetype comes from the announcement step** (`grammaire.md` §4.1, Visual column). Change it only if the content doesn't fit: no sourced figure, no A5.
2. **The variant comes from the content and the visuals.** The user has a screenshot: a device variant. They have a photo: an image variant. They have nothing: a variant without a visual (`aplat`, `centre`), never an empty frame. The table below says what each variant needs.
3. **Vary the designs.** Never three slides in a row with the same archetype and the same variant: the check flags it. Two blocks don't open the same way. Two title cards in a row change variant.
4. **At least one strong visual moment per block**: a giant figure (A5), an object or an interface (A9, A10), the product alone (A13), the bento (A14), a full-bleed photo (A18), or an image variant (“Strong visual moment” column of the table). Put it where the block proves or reveals.
5. **Dose the depth**: an object that leaves the frame, an accent halo, or a contact shadow on a light background. Only one of these three per slide, and never a shadow on a dark background.
6. **Write the visual to prepare** in `slide.visuel` (`deck-spec.md`), from §7 of the card: type, brief, transparent background, angle, minimum resolution. `export_script.js --visuels` turns it into the list to deliver.
7. **Fetch the visuals yourself when you can**, with the user's consent. Two sources:
   - **their mockup, down to the component.** With a link to a mockup (Figma, for example), don't stop at the whole screen. Go into the frame, isolate the component that tells the feature (a card, a button, a status column, a menu, three rows of a table) and export it alone. A screen shrunk into a tile or next to text becomes unreadable; a component reads. The whole screen stays for A10 and the devices.
   - **a royalty-free photo bank**, for usage and mood photos: Unsplash or Pexels. On Unsplash, filter on “free” (the paid Unsplash+ offer is excluded) and check “Free to use” on the photo's page. On Pexels, check “Free to use”. Note the author and the link for the credits. The photo shows the audience's trade and market (places, signage, objects and people of the target country), no readable brand, and never a generated image presented as a photo.

### The engine's variants

`build_deck.js` draws every variant of these cards, under its exact name (`slide.variante`). In parentheses: the visual a variant needs. Without that visual, the engine draws the card's fallback (§7). The last column says which variants make a block's strong visual moment; the check uses it.

| Archetype | Variants (`slide.variante`) | Strong visual moment |
|---|---|---|
| A1 Title card | `aplat` · `degrade` · `sur-image` (calm photo) · `entoure` (20 to 50 words about the subject) · `matiere` (the word rendered in a material) | `sur-image`, `matiere` |
| A2 Icon or logo + name | `icone-nom` (icon) · `icone-cote` (icon) · `logo-nom` (logo) · `rangee` (three icons) · `objet-interface` · `icone-seule` (icon) | no |
| A3 Agenda | `centre` · `droite` · `ligne` · `numerote` · `suffixe` · `ligne-active` · `couleurs` (one HEX per block) | no |
| A4 Thesis sentence | `aplat` · `degrade` · `mot-accent` · `definition` · `sur-image` (dark material) · `sourdine` · `enchainee` | `sur-image` |
| A5 Big figure | `centre` · `bloc` · `a-cote` (screenshot or object) · `sur-photo` (photo of the place) · `objet-anneau` · `objet-jauge` · `contour` | all |
| A6 Chart | `barres` · `deux-axes` (series of points) · `anneaux` (two shares) · `frise` · `classement` (logos) | no |
| A7 List | `centree` · `empilement` · `a-cote-icone` (icon) · `a-cote-objet` (object or screenshot) · `deux-colonnes` (icon) · `sur-photo` (calm photo) · `filet` (screenshot) | `a-cote-objet`, `sur-photo`, `filet` |
| A8 Checks | `coche-par-ligne` · `cercles-puis-coches` · `risque-puis-reponse` · `picto-par-ligne` (pictograms) · `sur-contenu` (photo) | `sur-contenu` |
| A9 Object + text | `appareil-centre-mot` (screenshot) · `objet-coupe` (product) · `objet-liste` (icon or object) · `objet-chiffre` (product) · `annotee` (render or screenshot) · `empilee` (product) | all |
| A10 Screenshot | `telephone-centre` · `tablette-centre` · `portable-centre` · `zoom-serre` · `capture-nue` · `rangee` (three screenshots): always a bare screenshot | all |
| A11 Diagram | `legende-laterale` · `plusieurs-blocs` · `schema-chiffre` · `carte-annotee` (top view) · `carre-halo`: optional SVG diagram | `carte-annotee` |
| A12 Inside view | `macro-matiere` · `capot-ouvert` · `eclate-axial` · `flux-lumiere`: 3D render or macro | all |
| A13 Product alone | `centre-entier` · `hero-coupe` · `profil-levitation` · `coloris` (two views): cut-out product | all |
| A14 Bento | `nom-au-centre` · `produit-au-centre` (product) · `tuiles-chiffres` (product) · `mot-geant-et-produit` (product) · `theme-et-matieres` (photo) · `grille-icones` (icons) · `fragments-logiciel` (interface components, a usage photo) | all |
| A15 Wall | `vignettes` (20 to 40 images) · `icones` (40 to 100 icons) · `mots` · `nuage` · `cartes-libelles` · `forme` (images) | `vignettes`, `icones`, `forme` |
| A16 Logos | `grille` · `ligne` · `logo-seul` · `mur-dense` · `pastilles` · `soi-au-centre`: monochrome logos | no |
| A17 Quote | `courte` · `longue` · `source-accent` · `centree-signature` | no |
| A18 Photo | `usage` · `exemple-cartouche` · `diptyque` (two photos) · `photo-titre`: photo | all |
| A19 Price | `colonne` · `deux-offres` · `nom-en-haut` · `gamme-alignee` (one product per offer) · `prix-heros` · `ancrage`: cut-out product | `colonne`, `deux-offres`, `nom-en-haut`, `gamme-alignee` |
| A20 Availability | `haut-et-gamme` · `suite-de-dates` · `colonne` · `date-et-lieux` · `mot-seul`: lineup or cut-out product | all except `mot-seul` |
| A21 Lower third | `gauche` · `droite` · `double` · `sur-clair` · `carte-invite` (logo) · `carte-portrait` (portrait): photo of the speaker | all except `carte-invite` |
| A22 to A25 Stage shots | accepted, rendered as a photo of the scene (see their cards) | all |
| FIN Final slide | `signe-seul` · `signe-et-ligne` · `signe-et-evenement` · `signe-sur-photo` (calm photo) · `mot-final`: monochrome logo | `signe-sur-photo` |
| COLORIS Colorway lineup | `rangee-alignee` · `rangee-chevauchee` · `eventail` · `un-par-un` · `mur`: one cut-out render per colorway | all |
| FRISE Timeline | `rangee-datee` · `generations` · `trois-jalons` (objects) · `courbe-et-saut` · `objet-du-passe` (object) | `trois-jalons`, `objet-du-passe` |

The FIN, COLORIS and FRISE variants can be set on any archetype: `"archetype": "A1", "variante": "mot-final"`. Without a variant, the engine keeps the archetype's original rendering, which is simpler; for A1, A3, A4, A5, A7 and A17, it is the same as the first variant. So always write the variant.

The engine sets the depth: on a light background, a very soft contact shadow under a product, a device or a silhouette; on a dark background, no shadow, but a soft, neutral halo behind a product. `"profondeur": false` on the slide removes both. Objects are cut by the frame in `objet-coupe`, `objet-chiffre`, `hero-coupe`, `zoom-serre`, `filet`, `rangee-chevauchee`, `mur`, `vignettes`, `icones` and `nuage`.

### An announcement block, slide by slide

A new software feature in 8 steps, with a screenshot and a photo provided. Each line changes composition, and the block has three strong moments: the screenshot, the figure, the bento.

| Step | Design | What we see | Visual |
|---|---|---|---|
| 3 Tension | A4 · `aplat` | the gap, in one sentence | none |
| 6 Name | A1 · `sur-image` | the name, in white, on the calm photo of the place of use | photo provided |
| 7 Definition | A4 · `mot-accent` | what it does, one group of words in the accent | none |
| 9 Pillar | A10 · `telephone-centre` | the real screen, front on, in a generic phone | screenshot provided |
| 9 Pillar | A9 · `appareil-centre-mot` | the same screen in the same place; the feature name in the margin | the same screenshot |
| 9 Proof | A5 · `bloc` | the figure, its comparison base right under it | none: a sourced figure |
| 13 Safeguard | A8 · `coche-par-ligne` | three commitments, one check per click | none |
| 14 Mini recap | A14 · `nom-au-centre` | the name in the center, what was shown around it | screenshots and icons for the tiles |

Without the screenshot, the pillar becomes A9 `objet-liste` (an icon and three lines) and the strong moment stays the figure. Without the photo, the name becomes A1 `aplat`: alone on screen, it keeps its force, and the block keeps its strong moments.

## 3. Rules shared by all cards

1. **The visual takes the space** (`style-visuel.md` §1, rule 8): a device over 91 % H, an object over 56 to 62 % W, a product over 60 to 87 % H, a full-bleed photo.
2. **Generic devices only**: a rectangle with corners of 13 % of its width, a 3 % bezel, in black glass with a thin light edge (on a dark background as on a light one: the corpus shows no light gray frame); no notch, no island, no buttons, no camera (`style-visuel.md` §5.2). Always ask for a bare screenshot, without a device frame: the engine adds the frame.
3. **Depth.** No shadow on a dark background. On a light background, at most a very soft contact shadow under an object: no sharp drop shadow in the 86 frames of objects and screens reviewed (A9, A10, A12, A13), which cover 8/8 keynotes. The halo (a blurred accent glow) points to one thing only: the lit block of a diagram, the ring of a figure, the current milestone of a timeline. The object that leaves the frame tells size and closeness (A9, A13, bento tiles).
4. **The image carries the color.** Text placed next to an image stays in the text color (9 frames out of 10 in A9, in 4/8: v3, v4, v7, v8). The accent goes to a single element: the figure, the halo, the highlighted line of an interface.
5. **One background per block**: no slide changes background alone (`style-visuel.md` §4.3).
6. **A fallback doesn't lie.** A missing visual leaves room for a neutral drawing (schematic interface, silhouette, flat fill and two halos) that never carries a number, a logo, a brand name or a drawn person. The silhouette is a volume modeled like a studio object (lit top, shaded bottom, light edge, soft reflection), mid gray on a dark background (30 % of the text color), never a dark flat fill lost in the background. A cut-out PNG is placed, shadowed and cropped on its opaque part, not on the file's transparent margins. A missing figure, price, date or colorway becomes a faded `[TO PROVIDE]` in its field, never a proposed value.

## 4. Text

The slides where the text is the visual: the name, the agenda, the sentence, the lists, the quote, the lower third. Frames reviewed for these cards: 129.

### A1 · Title card

#### 1. Role and moment

- It opens a chapter, a feature or an argument, at the moment its name is said. Nothing else is on screen. Present in 8/8.
- It is the most frequent punctuation: about 40 in v7, 15 to 20 in v1, 12 to 15 in v3.
- Place in the sequence: right after the handover or the framing sentence, right before the demo, the screenshot or the figure. It also serves as the final slide (one word, larger size).
- The same card often comes back on the set's screen, with the presenter beside it (4/8: v1, v2, v7, v8). A deck keeps only the full-bleed version.

#### 2. Canonical composition

| Zone | x | y | w | h | Rule |
|---|---|---|---|---|---|
| kicker (optional) | 6 | 27 | 88 | 6 | centered; baseline 0.45 cap above the name |
| title (the name) | 6 | 40 | 88 | 20 | cap center at 50 % H and 50 % W; cap from 14.5 to 19 % H; one line |

The name takes 29 to 59 % W for one or two words (`style-visuel.md`), up to 72 % W for two long words (v3, measured). Everything else is empty.

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                       kicker (optional)                        |
|                                                                |
|    +------------------------------------------------------+    |
|    |                      N A M E .                       |    |
|    |                                                      |    |
|    +------------------------------------------------------+    |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `aplat`, `degrade`, `sur-image`, `entoure` or `matiere`. Without a variant: like `aplat`. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **aplat** (word alone, flat color) | 5/8 (v5, v1, v2, v3, v4) | The name in the text color: white on black, black on light gray. v5 sets it in the service's color. |
| **degrade** (section gradient) | 5/8 (v2, v3, v4, v7, v8) | The name in a horizontal gradient of the section's hue: darker on the left, lighter on the right, or two neighboring hues. v7 and v8 do it on all their cards. |
| **sur-image** (calm photo or blurred background) | 4/8 (v5, v2, v4, v8) | The name, white, on a full-bleed image: set wall, aerial view, sky, colored wallpaper; or a blurred light background (all of keynote v8). v4 does it about 10 times to open a sub-chapter. |
| **entoure** (ring of elements) | 2/8 (v6, v8) | The name in the center, smaller; around it, a ring of small line pictograms (v6) or of gray technical names in various sizes (v8). The central oval stays empty. |
| **matiere** (letters in a material) | 2/8 (v6, v8) | The letters are an object: a glowing outline stroke (v6), iridescent embossed glass on white (v8). The engine doesn't draw it: it comes from a provided image. |

Also seen: a small word above the name, on an image (v2, 1/8); that is the kicker the engine already supports.

#### 4. Visual content

- **aplat, degrade**: no visual. The emptiness makes the slide.
- **sur-image**: full-bleed photo, no frame or corners (`style-visuel.md` §4.3). The center is calm: a surface (wall, sky, sand, water). The subject and the extras stay on the edges (v4: extras left and right, bare wall in the middle). Natural, soft light. A black overlay of 20 to 45 % only if white doesn't hold 4.5:1. Blurred background: a light, defocused photo, two or three soft spots of color (v8).
- **entoure**: 20 to 50 elements over the whole frame, smaller and paler than the name (secondary gray, or a stroke in the section's color), in three sizes. None touches the central oval (60 % W × 36 % H).
- **matiere**: the image of the word alone, cut out.
- **Accent**: the name (flat accent or gradient) or the final period. Only one of the two.

#### 5. Typography

Size, floor, weight and tracking: `style-visuel.md` §3 A1. What changes here:
- 1 to 3 words, 5 at most (v7). A 4-word command or name keeps the title card, at cap ≈ 10 % H (v7: band of 11.7 % H including descenders, 45 % W).
- **sur-image**: pure white, same size, never a drop shadow (§5.1).
- **entoure**: name at 72 pt (cap ≈ 13 % H); elements from 10 to 20 pt, regular, secondary.
- Discreet subheading (v4, 1/8): cap ≈ 6 % H when the word follows the presenter's sentence. Not by default.

#### 6. Build and animation

- Slide fade (0.5 s); the name is there when it is said (8/8).
- **Wipe** from left to right that reveals the name (v3, 1/8: one frame catches the name half revealed). pptx: “Wipe” entrance from the left, 0.6 s.
- Exit by a fade to the background (v7): the next slide's fade is enough.
- **sur-image**: the image comes in with the slide, the name on click (convention).
- **entoure**: the name first, then the ring all at once (convention; v6 animates its pictograms as they appear).

#### 7. Visual brief and fallback

- **aplat, degrade**: nothing to provide, except the exact name; `accent2` for the gradient.
- **sur-image**: 16:9 photo, JPEG, 1920 × 1080 at least (3840 × 2160 recommended). No text or logo. Calm center over 60 % W × 30 % H; subject on the edges; no strong line in the 40-60 % H band. No transparency.
- **entoure**: 20 to 50 real words about the subject (modules, features, trades), or 20 to 50 monochrome line pictograms in SVG.
- **matiere**: PNG with a transparent background, the word alone, 3000 px wide at least, tightly framed, lit from the front.
- **Drawn fallback**: sur-image → a flat fill slightly lighter than the background and two very blurred neutral halos (`style-visuel.md` §5.2); entoure → a ring of round dots and gray bars with round ends (text mixed at 22-38 %), with no text or number; matiere → the name as `aplat`.

#### 8. Avoid

- More than 3 words, or a name split over two lines when it fits on one.
- A second element (logo, icon, subtitle): it is no longer A1, it is A2 or A4.
- The name at the top of the slide, empty space below.
- A busy photo in the center; an overlay that grays the whole image; a shadow on the text.
- Gradient and accent period together; two accent colors.
- Changing background for a single card in the middle of a block (§4.3).

### A2 · Icon or logo + name

#### 1. Role and moment

- It announces an app, a technology, a service or a module: “here is the subject”. Present in 7/8 (not v3).
- About 20 to 30 per software event (v1, v6, v7, v8). In v8, it opens almost every subsection.
- Moment: right after the framing, before the demo. In v8, the icon also serves as a door to the next set.

#### 2. Canonical composition

Measured on 4 full-bleed frames (v1, v2, v4).

| Zone | x | y | w | h | Rule |
|---|---|---|---|---|---|
| icon | 39 | 30.5 | 22 | 39 | square; centered on 50 % W and 50 % H; side from 30.6 to 44.2 % H (median 39.7) |
| name | 10 | 76 | 80 | 8 | centered; cap top at 77 % H; cap ≈ 5.5 % H; one line of 15 to 50 % W |

- The icon holds the center; the name drops into the bottom third. Gap between the icon and the name: 5.5 to 7.3 % H. The name's cap is about 0.14 times the icon's side.
- In inches: icon of 2.2 in, centered on 50 % H; name at 32 pt, floor 24 pt, cap top at 4.33 in.

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                         +------------+                         |
|                         |            |                         |
|                         |   ICON     |                         |
|                         |            |                         |
|                         |            |                         |
|                         |  (square)  |                         |
|                         |            |                         |
|                         +------------+                         |
|                                                                |
|                              Name                              |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `icone-nom`, `icone-cote`, `logo-nom`, `rangee`, `objet-interface` or `icone-seule`. Without a variant: the original rendering, simpler than the variants. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **icone-nom** (centered icon, name below) | 4/8 (v1, v4, v7, v8) | The canonical composition. v7 and v8 show it mostly on the set's screen, with the presenter beside it. |
| **icone-cote** (icon left, name right) | 1/8 (v6, about 25 times) | The icon and the name on the same center line; the name left-aligned after the icon. |
| **logo-nom** (brand logo + name) | 3/8 (v5, v1, v4) | No icon: the brand logo right next to the service name, on one line, at title-card size (cap of 11 to 17 % H measured). Logo 1.1 times the cap high; gap ≈ 0.3 cap. Always on black (3/3). |
| **rangee** (row, then each one alone) | 3/8 (v2, v6, v7) | Two to five icons in a row without names (trio: 3 × 22 % W, gap ≈ 2 % W, from 30 to 70 % H), then each icon alone in turn. v7 makes it a grid of 3 to 12 icons as a chapter agenda. |
| **objet-interface** (a single button) | 1/8 (v6) | The interface element alone, as a light pill with its label inside; no icon. |
| **icone-seule** (no written name) | 1/8 (v2) | The icon alone in the center; the name is only spoken. It often follows a row. |

Also seen, outside slides: icons appearing one by one next to the filmed presenter (v4, 1/8).

#### 4. Visual content

- **The icon**: a square tile with rounded corners (corner ≈ 19 to 22 % of the side, measured on 2 icons); flat fill or soft vertical gradient of a single hue; a simple pictogram in the center (50 to 65 % of the side), white or dark. Volume variant: three stacked layers seen at three-quarters (v1, 1/8).
- **Treatment**: no shadow on a dark background; no visible shadow on a light background either (v7, v8). No halo, no reflection.
- **Framing**: whole, centered, never cut by the edge.
- **Accent**: the color is in the icon; the name stays in the text color.

#### 5. Typography

- Name in semibold, cap ≈ 5.5 % H (≈ 32 pt), one line, 1 to 4 words, text color.
- **icone-cote**: same size, left-aligned at 46 % W, centered on the middle of the icon.
- **logo-nom**: title-card size (`style-visuel.md` §3 A1), reduced to fit in 60 % W.
- **objet-interface**: 28 pt label in the pill, in the slide's background color.
- No kicker seen on this archetype (0/7).

#### 6. Build and animation

- The icon and the name come in together, with a fade, when the name is said (7/7).
- **rangee**: the row comes in all at once; then one slide per icon (morph: the icon slides to the center, the others fade out).
- **Door** (v8, 1/8): zoom into the icon toward the next slide. pptx: “Zoom” transition, or a morph to a slide where the icon is enlarged to 400 %.

#### 7. Visual brief and fallback

- **Icon**: SVG, or PNG with a transparent background, square, 1024 × 1024 px at least, the pictogram without text and without a built-in shadow. If the icon has no tile, give its color: the engine adds the tile.
- **Logo**: SVG or transparent PNG, a light version and a dark one, 2000 px wide at least.
- **Button**: its exact label and its color.
- **Drawn fallback**: a square tile with 20 % corners, vertical gradient of the accent (top lightened by 20 %), white ring in the center (diameter 50 % of the side, stroke 8 %). In a row or a grid of icons, each tile takes its own hue (accent, accent 2, their mix, a gray) and its own shape (ring, square, bars, dot): three identical tiles would read as a repeated stamp. No letter, no number, no shape that recalls a brand. logo-nom without a logo → the name alone, as A1.

#### 8. Avoid

- A name larger or wider than the icon.
- An icon under 30 % H, or a centered block that pushes it up.
- A borrowed icon: a well-known app, another brand's logo.
- A black drop shadow, a frame or an outline around the icon.
- The name in the accent on top of a colored icon.
- A sentence instead of the name.

### A3 · Typographic agenda

#### 1. Role and moment

- It announces the blocks of the presentation, right after the welcome. Present in 4/8: the 4 software events (v6, v1, v7, v8); no product event (0/4).
- It comes back unchanged before the close: 2/8 (v7, v8). v7 also opens each large block with an agenda (6 in all).
- In a deck: after the opening thesis, then before the final recap.

#### 2. Canonical composition

| Zone | x | y | w | h | Rule |
|---|---|---|---|---|---|
| list, centered | 10 | 16 | 80 | 66 | 4 to 6 lines, one per block, 1 to 3 words; block center at 49 % H |
| list, right-aligned | 20 | 10 | 56 | 80 | same list, right edge at 76 % W |

- Size by number of lines, and line spacing: `style-visuel.md` §3 A3.
- Measured: a step of 12.5 % H for 6 centered lines (v7); 14.2 % H for 6 right-aligned lines, right edge at 64.8 % W, block from 9 to 91 % H (v8). The stack fills the height.

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|             +----------------------------------+               |
|             |                          block 1 |               |
|             |                                  |               |
|             |                          block 2 |               |
|             |                                  |               |
|             |                          block 3 |               |
|             |                                  |               |
|             |                          block 4 |               |
|             |                                  |               |
|             |                          block 5 |               |
|             |                                  |               |
|             |                          block 6 |               |
|             |                                  |               |
|             +----------------------------------+               |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `centre`, `droite`, `ligne`, `numerote`, `suffixe`, `ligne-active` or `couleurs`. Without a variant: like `centre`. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **centre** (centered stack) | 1/8 (v7) | The lines centered, one per block. |
| **droite** (right-aligned stack) | 2/8 (v1, v8) | Right edge at 65-78 % W; the left half stays for the presenter (v1) or empty (v8). |
| **ligne** (a single line) | 1/8 (v6) | The four names side by side, spaced, in the middle. |
| **numerote** (numbered stack) | 1/8 (v7) | An order number circled with a stroke before each line; lines left-aligned in a centered block; three lines. |
| **suffixe** (second state) | 1/8 (v8) | On click, the same word is added at the end of each line, in a lighter weight. |
| **ligne-active** (lines one by one) | 1/8 (v7) | The first line alone in the center, the next one very pale below; on each click, one more line and the block re-centers. |
| **couleurs** (one color per block) | 2/8 (v7, v8) | Each line in the color of its block. The two other keynotes stay in white (2/8: v6, v1). A gradient shared by the whole stack is seen once (v7). |

#### 4. Visual content

- No visual. The background is a flat fill (v6, v1, v7); v8 uses a blurred light background (1/8), which the skill does not reuse (`style-visuel.md` §4.3).
- **Accent**: the line of the current block (engine), or one color per block if the user has them. The agenda is one of the three exceptions to “a single accent per slide” (`style-visuel.md` §1, rule 6).

#### 5. Typography

- Measures: `style-visuel.md` §3 A3. What changes here:
- **ligne**: 40 pt on a line of 88 % W, an em space between two names.
- **numerote**: 48 pt; stroked circles 1.1 cap high, in the accent; number in regular.
- **suffixe**: same size as the name, in regular.

#### 6. Build and animation

- Whole block with the slide: 3/4 (v6, v1, v8).
- Line by line, block re-centered: v7. One slide per state, morph; fade as a fallback.
- **suffixe**: second state by morph, otherwise a fade of the added word.
- Repeat before the close: the same slide; the blocks already covered go to secondary, the last one stays full (field `actif`).

#### 7. Visual brief and fallback

- The block names, 1 to 3 words each, in running order.
- A color code per block, if one exists: the HEX values, at 3:1 at least on the background.
- **suffixe**: the exact word (year, version), never invented.
- **Fallback**: nothing to draw. Without a color code: the current line in the accent, the others in the text color. Without wanted numbers: a small solid accent circle, with no number.

#### 8. Avoid

- More than 6 lines, or sentences.
- Bullets and dashes; numbers when the order doesn't matter.
- Different sizes from one line to the next.
- A left-aligned stack without numbers (0/4).
- Six colors unrelated to the deck's blocks.

### A4 · Thesis sentence

#### 1. Role and moment

- It pins down the benefit right after a demo or a figure; it states the thesis at the opening; it shows a commitment. Present in 6/8 (v5, v6, v1, v2, v7, v3), plus a variant in v4.
- The written text is, word for word, what is said at the same moment (6/6).
- About 15 to 20 per live keynote (v5, v6), 4 to 8 when prerecorded (v2, v3).

#### 2. Canonical composition

| Zone | x | y | w | h | Rule |
|---|---|---|---|---|---|
| sentence | 12 | 36 | 76 | 25 | 1 or 2 lines, centered; block center at 48.5 % H; longest line over 66 to 74 % W; second line at 55-70 % of the first |

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|        +----------------------------------------------+        |
|        |             A sentence that fits             |        |
|        |                on two lines .                |        |
|        |                                              |        |
|        +----------------------------------------------+        |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `aplat`, `degrade`, `mot-accent`, `definition`, `sur-image`, `sourdine` or `enchainee`. Without a variant: like `aplat`. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **aplat** (flat sentence) | 4/8 (v5, v6, v1, v2) | White on black, or black on light gray; one or two lines. |
| **degrade** (hue of the product or the section) | 2/8 (v3, v7) | The sentence in a gradient: the product's hue (taupe to dark, blue-gray to light) in v3, the section's gradient over two lines in v7. |
| **mot-accent** (one group in the accent) | 3/8 (v5, v6, v3) | A group of one to three words in color (v3), in italics (v6), or the key word in color (v5). Always on black. |
| **definition** (dictionary entry) | 1/8 (v5) | The key word in accent capitals with its part of speech, then the definition over two lines, all left-aligned. |
| **sur-image** (dark material) | 2/8 (v2, v4) | The white sentence on a dark material (smoke) or a close-up of the product. |
| **sourdine** (gray sentence) | 1/8 (v2) | The sentence in secondary gray on light, to say calm or discretion. |
| **enchainee** (sentences in the same place) | 1/8 (v5) | Several short sentences replace each other, one per idea, in the same place. |

#### 4. Visual content

- No visual, except **sur-image**: full-bleed material or close-up, dark, low contrast, the detail on the edges; the sentence on the calm zone.
- **Accent**: one group of words at most, or the final period, or the gradient. Never two.

#### 5. Typography

- Size, line spacing and line breaks: `style-visuel.md` §3 A4.
- **definition**: word in 24 pt semibold capitals, in the accent; 40 pt definition, left-aligned at 14 % W.
- **sur-image**: same size, white. v4 sets its sentence on a smaller line (cap ≈ 4 % H): that is a film signature, not a default to copy.
- v6's italics go through the accent color in the skill (convention).

#### 6. Build and animation

- Fade at the moment the sentence is said (6/6).
- **enchainee**: cross-fade in the same place, or one slide per sentence with a morph.
- **sur-image**: the image with the slide, the sentence on click (convention).

#### 7. Visual brief and fallback

- The sentence (3 to 8 words) is proposed as `[TO VALIDATE]`. It contains no number.
- **sur-image**: 16:9 image, JPEG, 1920 × 1080 at least; material or product detail; dark (mean luminance under 25 %); center without detail; no text.
- **Drawn fallback**: the flat fill. sur-image → a dark flat fill and two very blurred neutral halos.

#### 8. Avoid

- More than 8 words (10 at most); three lines.
- A figure in the sentence: that is an A5. A superlative without proof in front of an audience that asks for proof (`publics.md`).
- Quotation marks, bullets, pictograms.
- Two groups in the accent; an accent and a gradient together.
- A last line of a single word.

### A7 · List without bullets

#### 1. Role and moment

- It lists benefits, or announces the plan of a sub-chapter. Present in 7/8 (not v3).
- The lines arrive one by one, at the pace of the voice, in 6/8; v8 shows them all at once.
- Moment: after a feature is announced, to say what it brings; or at the end of a block, to list what was shown.

#### 2. Canonical composition

| Zone | x | y | w | h | Rule |
|---|---|---|---|---|---|
| list | 10 | 31 | 80 | 33 | 2 to 6 lines of 2 to 5 words, centered; block center at 47 % H |

- Size and line spacing: `style-visuel.md` §3 A7.
- Measured: a step of 14.7 % H for 3 lines (v1); 20 % H for 2 lines (v2).

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|      +--------------------------------------------------+      |
|      |                   spoken line                    |      |
|      |               line to come (53 %)                |      |
|      |               line to come (53 %)                |      |
|      |                                                  |      |
|      +--------------------------------------------------+      |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `centree`, `empilement`, `a-cote-icone`, `a-cote-objet`, `deux-colonnes`, `sur-photo` or `filet`. Without a variant: like `centree`. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **centree** (stack that lights up) | 4/8 (v5, v1, v2, v4) | All lines in place; the spoken line is full, the next ones at 53 % (lighting up seen in v2 and v7). |
| **empilement** (stack that re-centers) | 3/8 (v1, v4, v7) | One line alone in the center, then two, then three: the block re-centers with each addition. |
| **a-cote-icone** (list and icon) | 3/8 (v6, v8, v4) | Icon on the left, lines left-aligned in the free column. Measured (v8): icon of 21 % W × 38 % H centered at 22 % W; lines at 45-47 % W, cap ≈ 4.2 % H, step of 7.9 % H. |
| **a-cote-objet** (list and object or screenshot) | 4/8 (v5, v6, v2, v8) | A cut-out object or a screenshot on one half; the list on the other side, aligned toward it (left when the object is on the left, right when it is on the right). |
| **deux-colonnes** (long list) | 2/8 (v4, v8) | 16 to 17 items: two columns next to an icon (v4), or one tight column in small type (v8). It is looked at more than read. |
| **sur-photo** (lines on the sky) | 1/8 (v4) | White lines on a calm photo of the place, added at the pace of the voice. |
| **filet** (list behind a rule) | 1/8 (v2) | A small left-aligned list behind a vertical rule, above a screenshot cut at the bottom; the next line still gray. |

#### 4. Visual content

- **centree, empilement**: no visual.
- **a-cote-icone**: an icon in A2 format, whole.
- **a-cote-objet**: cut-out object or screenshot, whole; an object may leave the frame on the edge side (A9); no shadow on a dark background, a very soft contact shadow on a light background.
- **sur-photo**: calm full-bleed photo (sky), the subject on the edges.
- **Accent**: none on the lines (`style-visuel.md` §3 A7). The color comes from the icon or the object.

#### 5. Typography

- **centree, empilement**: `style-visuel.md` §3 A7.
- **a-cote-icone, a-cote-objet**: 24 pt, k = 1.8, left-aligned (`style-visuel.md` §3 A9, icon variant).
- **deux-colonnes**: 20 pt, k = 1.4, two columns of 28 % W.
- **filet**: 14 pt, k = 1.4; 1 pt rule in secondary.
- Line to come: secondary at 53 %.

#### 6. Build and animation

- **Lighting up** (v2, v7): all lines in place; on each click, the next line goes from secondary to full. pptx: “Font Color” emphasis effect, or two states by morph.
- **Stacking** (v1, v4, v7): one slide per state; the new line fades in and the block re-centers (morph).
- **All at once** (v8, 1/8): for long lists (deux-colonnes).
- **a-cote**: the object or the icon first, then the lines.

#### 7. Visual brief and fallback

- The lines: 2 to 6, 5 words at most; they are proposed as `[TO VALIDATE]`.
- **a-cote-icone**: like A2 (SVG, or transparent PNG of 1024 × 1024 px at least).
- **a-cote-objet**: transparent PNG of the object, 2000 px high at least, front or three-quarter view; or a PNG screenshot at native resolution, with no personal data.
- **sur-photo**: 16:9 photo, 1920 × 1080 at least, sky or calm wall over the 25-70 % H band.
- **Drawn fallback**: icon → A2's fallback tile; screenshot → schematic interface (`style-visuel.md` §5.2); object → simple silhouette; photo → flat fill and two halos.

#### 8. Avoid

- Bullets, dashes, numbers.
- More than 6 lines, except the long list, which becomes a wall.
- A line of more than 5 words.
- The accent on a line; all lines in gray.
- Left-aligned lines in the middle of an empty slide: the corpus left-aligns them only against an object.

### A8 · Checklist

#### 1. Role and moment

- A trust argument (privacy, security), a promise, or the recap of a service. Present in 3/8 (v5, v7, v4).
- Moment: when what is missing is set against what we bring (v5, v7), or at the end of a block as a recap card already checked (v5).

#### 2. Canonical composition

| Zone | x | y | w | h | Rule |
|---|---|---|---|---|---|
| pictograms | 21 | 30 | 5.5 | 38 | one per line, 1.1 cap high, sitting on the baseline |
| lines | 28 | 30 | 52 | 38 | 3 to 6 lines, left-aligned in a centered block; block center at 47 % H |

- Size, line spacing and pictogram size: `style-visuel.md` §3 A8.
- Measured (v4): 3 lines, step of 14 % H; block from 5.5 to 88 % W when the lines are long.

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|             (v)  line 1                                        |
|                                                                |
|             (v)  line 2                                        |
|                                                                |
|             (v)  line 3                                        |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `coche-par-ligne`, `cercles-puis-coches`, `risque-puis-reponse`, `picto-par-ligne` or `sur-contenu`. Without a variant: the original rendering, simpler than the variants. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **coche-par-ligne** | 2/8 (v7, v4) | Each line arrives with its check; the last one still pale during its entrance (v4). |
| **cercles-puis-coches** | 1/8 (v5) | Empty circles before each line (what is missing), then all the checks together, on the promise sentence. |
| **risque-puis-reponse** | 1/8 (v7) | One slide of risks, each with a warning triangle; then the answers, each with its check, in the same place. Also seen: a list where each line is struck through with a cross (v7). |
| **picto-par-ligne** | 1/8 (v5) | A different pictogram per line, each in its own color; the list is a leitmotiv repeated at the end of 4 blocks. |
| **sur-contenu** | 1/8 (v5) | The checked list on a darkened content image, as a recap; or fading out over the devices. |

Seen once, as a transition: the list tilts into perspective and leaves the frame (v5). It has to be done by hand.

#### 4. Visual content

- **Pictograms** drawn with a stroke, in the accent: a thin circle with a check of the same stroke inside (3/3: v5, v7, v4); an empty stroked circle; a warning triangle (v7); a cross in a circle, in gray (v7). The corpus never uses a solid dot.
- Circle stroke ≈ 9 % of its diameter; the check has the same stroke (measured on 2 circles in v4 at 960 px). No shadow, no halo.
- **picto-par-ligne**: in the skill, all pictograms in the accent (a single color, `style-visuel.md` §4.1).
- **sur-contenu**: full-bleed image, dark overlay of 50 to 70 %.
- **Accent**: the pictograms only. The text stays in the text color.

#### 5. Typography

- Measures: `style-visuel.md` §3 A8. **picto-par-ligne**: 30 pt for 6 lines.
- v7 sets the checklist text in a gradient (1/8): not kept.

#### 6. Build and animation

- **coche-par-ligne**: one line and its check per click, with a fade.
- **cercles-puis-coches**: click 1, the lines and their empty circles; click 2, all the checks together (zoom or 0.3 s fade).
- **risque-puis-reponse**: two slides in the same place; morph of the pictograms and the text.
- **picto-par-ligne**: line by line, then the same list repeated at the end of each block.

#### 7. Visual brief and fallback

- 3 to 6 lines of 2 to 5 words. They are proposed as `[TO VALIDATE]`, except the commitments (privacy, guarantees), which the user validates personally.
- No visual to provide: the engine draws circles, checks, warnings and crosses.
- **picto-par-ligne**: 3 to 6 monochrome line pictograms in SVG; otherwise the engine's check on each line.
- **sur-contenu**: 16:9 image, 1920 × 1080 at least; otherwise the flat fill.

#### 8. Avoid

- Checks in several colors, emoji, heavy solid pictograms.
- A solid dot; a pictogram taller than 1.2 cap.
- A check before a `[TO PROVIDE]` line: the box stays empty (engine rule).
- Warnings and checks on the same slide: v7 splits them into two slides.
- The text in the accent.

### A17 · Quote or testimonial

#### 1. Role and moment

- Social proof that the presenter reads aloud: press, partner, customer. Present in 3/8 (v5, v6, v1), plus an author's quote at the opening (v3, variant).
- No press or partner quote after 2020 (0/5): proof then goes through walls, sourced rankings and films.
- Moment: opening of a section (v5, v1), or right after a launch, as a series of two (v6).

#### 2. Canonical composition

| Zone | x | y | w | h | Rule |
|---|---|---|---|---|---|
| quote | 9.2 | 33 | 76 | 24 | 2 to 4 lines in semibold, left-aligned; block centered at 50 % H |
| source | 9.2 | 62 | 76 | 6 | regular, secondary, at 0.75 times the cap; cap top 9.5 % H below the last baseline |

- Measured: left edge at 8.4-9.2 % W (v1, 2 frames). Two lines: cap ≈ 6.4 % H. Five lines: cap ≈ 5 % H, longest line at 80 % W (v1).

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|      +-----------------------------------------------+         |
|      | A quote of two                                |         |
|      | to four lines                                 |         |
|      +-----------------------------------------------+         |
|                                                                |
|      First Last, organization                                  |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `courte`, `longue`, `source-accent` or `centree-signature`. Without a variant: like `courte`. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **courte** (2 to 3 lines) | 2/8 (v1, v6) | Large size; gray source one line below. |
| **longue** (4 to 5 lines) | 3/8 (v5, v6, v1) | Reduced size (cap ≈ 5 % H), same alignment, longest line up to 80 % W. |
| **source-accent** | 1/8 (v5) | The source in small accent capitals, right under the quote. |
| **centree-signature** | v3 variant, not counted | Short centered quote, small, in quotation marks; the signature arrives below a beat later. |

Quotation marks: none on press and partner quotes (0/3 keynotes, 7 frames); only on v3's author quote.

#### 4. Visual content

- None: no portrait, no logo, no photo, no decorative quotation mark (0/3). The text is the visual.
- Background: dark flat fill (3/3, and v3).
- **Accent**: none; or the source (v5), which is then the only accent.

#### 5. Typography

- Measures: `style-visuel.md` §3 A17.
- **longue**: 28 pt (floor), 20 pt source.
- **source-accent**: 18 pt semibold capitals, in the accent.
- **centree-signature**: 24 pt centered; 20 pt source. The skill keeps the theme's text font (the only serif font in the corpus is v3's).

#### 6. Build and animation

- Quote and source come in together and stay for the time it takes to read them (3/3).
- **centree-signature**: the quote alone, then the signature on click.

#### 7. Visual brief and fallback

- The exact text (15 to 25 words, 30 at most), the name, the role, the organization, the date and the person's consent. A testimonial is never proposed as `[TO VALIDATE]`: it is provided (deck-spec).
- No visual to provide.
- **Fallback**: the markers `[TO PROVIDE: quote]` and `[TO PROVIDE: source]`, faded, at their field's size. No fake text, no gray bars.

#### 8. Avoid

- A testimonial that is invented, reworded or shortened without its author's consent.
- Giant quotation marks, italics, portrait, the source's logo.
- A quote of more than 2 lines centered.
- More than 30 words or more than 5 lines.
- Two accents (the source and a word of the quote).

### A21 · Name and role lower third

#### 1. Role and moment

- It names a speaker on their first appearance. Present in 6/8: all the prerecorded ones (6/6), no live one (0/2). Never for the host (0/8).
- Only once per speaker, and not necessarily for all of them (v1: 17 lower thirds for 20 speakers).
- Live, an outside guest gets a card on the screen instead (v5, v6); v7 builds it into its slide.
- In a deck: on the photo slide of a speaker's first turn, or on a video. With `meta.contexte` set to `direct`, no lower third: the previous presenter says the name.

#### 2. Canonical composition

| Zone | x | y | w | h | Rule |
|---|---|---|---|---|---|
| photo | 0 | 0 | 100 | 100 | full-bleed |
| presenter (in the photo) | 40 | 15 | 32 | 85 | in the center or on the side opposite the lower third |
| name | 5.4 | 80.5 | 45 | 4.5 | baseline at 84.4 % H; cap from 2.8 to 3 % H |
| role | 5.4 | 86.4 | 45 | 4.5 | baseline at 90.3 % H; same size as the name |

```
+----------------------------------------------------------------+
|................................................................|
|................................................................|
|................................................................|
|..........................+------------------+..................|
|..........................|..................|..................|
|..........................|..................|..................|
|..........................|..................|..................|
|..........................|..................|..................|
|..........................|..................|..................|
|..........................|..................|..................|
|..........................|....PRESENTER.....|..................|
|..........................|..................|..................|
|..........................|..................|..................|
|..........................|..................|..................|
|...First Last.............|..................|..................|
|..........................|..................|..................|
|...Role...................|..................|..................|
|..........................+------------------+..................|
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `gauche`, `droite`, `double`, `sur-clair`, `carte-invite` or `carte-portrait`. Without a variant: the original rendering, simpler than the variants. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **gauche** | 6/8 (v1, v2, v7, v8, v3, v4) | Lower third at the bottom left; the person in the center or on the right. Default position. |
| **droite** | 5/8 (v2, v3, v4, v7, v8) | Lower third at the bottom right, right-aligned (right edge at 94.7 % W), when the person is on the left. |
| **double** | 1/8 (v4) | Two people in the shot, two lower thirds: one on the left, one on the right, each under its person. |
| **sur-clair** | 1/8 (v8) | On a light set, the lower third turns dark gray. |
| **carte-invite** | 2/8 (v6, v7) | On the slide: the guest organization's logo, then the name in semibold and the role in gray, centered. |
| **carte-portrait** | 1/8 (v5) | The logo on the left, a black-and-white portrait on the right, with no written name. |

#### 4. Visual content

- **The photo**: the speaker in context, in a wide shot (full length, from 1/4 to 1/2 of the height) or a waist shot, in a place linked to the subject; natural light; sharp or slightly blurred background. Full-bleed, no frame or corners.
- The person is on the side opposite the lower third; the bottom of the image is calm (floor, wall).
- No band, no background, no shadow under the text (6/6).
- **carte-invite**: monochrome logo centered on the flat fill. **carte-portrait**: black-and-white portrait, fading into black on the logo side.
- **Accent**: none.

#### 5. Typography

- Measures: `style-visuel.md` §3 A21 (name and role at the same size, in white).
- **sur-clair**: text color (dark gray), same size.
- **carte-invite**: 22 pt name in semibold, 18 pt role in secondary regular, centered under the logo (convention drawn from 2 frames).
- The role is written out in full, with no in-house abbreviation.

#### 6. Build and animation

- Fade 2 to 5 s after the person enters the frame; held 4 to 6 s; fade out (corpus analysis, A21). v7 shows the person already there and the lower third not yet.
- pptx: fade entrance “After Previous”, 2 s delay; fade exit “After Previous”, 5 s delay.
- **double**: both lower thirds come in and go out together.

#### 7. Visual brief and fallback

- **Photo**: 16:9, JPEG, 1920 × 1080 at least; wide or waist shot; the person on the right third if the lower third is on the left (the reverse otherwise), looking toward the center or the camera; the bottom of the image calm, dark enough for white text at 4.5:1 (or light enough for dark text); no text or logo in the image; signed image release.
- The exact name and role. An unknown role stays empty, never a repeated marker (deck-spec).
- **carte-invite**: the organization's logo, monochrome SVG or transparent PNG.
- **Drawn fallback**: a flat fill slightly lighter than the background and two very blurred neutral halos (`style-visuel.md` §5.2), with no silhouette or face; name and role in the text color. carte-invite without a logo → `[TO PROVIDE: logo]` in its place.

#### 8. Avoid

- A band, a caption box, a blurred background or a shadow behind the text.
- A lower third for the host, or repeated at each turn.
- The lower third on the person's side: the text falls on their body.
- Name and role at two different sizes; all capitals; the company logo in the lower third.
- A drawn or generated face to fill in for a missing photo.

## 5. Figures and proof

The slides that prove: a figure, a gap, a system in parts, abundance, adoption. Frames reviewed: 95, plus 9 extracted from the videos.

### A5 · Big figure + label

#### 1. Role and moment

- The proof of a benefit, right after it is stated (corpus analysis). In the announcement sequence, it follows the feature or the demo; the thesis sentence (A4) can come right after it.
- Presence: 7/8 (v5, v6, v1, v2, v7, v3, v4). Absent from v8, where the figures are only spoken.
- It comes in series at product events: 3/8 (v2, v3, v4), up to 9 for a single product (v2). Rare at recent software events: 3 in 1 h 44 (v7).
- The comparison base is written in the label: 2/8 as a rule (v3, v4), 2/8 in part (v2, v7).

#### 2. Canonical composition: “centre”

Measured on v1, v3, v7: figure capitals from 36.1-36.9 to 63.1-63.3 % H, label from 77-78 to 82 % H, all centered on 50 % W.

| Zone | x | y | w | h | Note |
|---|---|---|---|---|---|
| Kicker (optional) | 10 | 26.3 | 80 | 4.3 | gray, regular; baseline 0.25 cap above the figure |
| Figure | 10 | 37.1 | 80 | 25.9 | one line; cap center at 50 % H; floor 110 pt |
| Label | 8 | 77.9 | 84 | 4.3 | semibold, text color; center at 80 % H |
| Source | 8 | 85.8 | 84 | 2.0 | depending on the audience |

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                 optional kicker · 24 pt · gray                 |  baseline ≈ 30.6 % H
|                                                                |
|      ####################################################      |  cap top 37 % H
|      ############ FIGURE · 144 pt · gradient ############      |
|      ####################################################      |  center 50 % H
|      ############ one line, fitted in 80 % W ############      |
|      ####################################################      |  baseline 63 % H
|                                                                |
|                                                                |
|                   label · 24 pt · text color                   |  center 80 % H
|                         source · 11 pt                         |  ≈ 86 % H
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `centre`, `bloc`, `a-cote`, `sur-photo`, `objet-anneau`, `objet-jauge` or `contour`. Without a variant: like `centre`. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **centre** (canonical) | 5/8: v1, v3, v4, v5, v7 | figure in the middle, label far below (77-82 % H) |
| **bloc** | 2/8: v2, v6 | label right under the figure; the whole block is centered (measured v2: figure 33.9-56.4 % H, label 62.8-66.9 % H); two label lines possible |
| **a-cote** | 3/8: v2, v4, v6 | a visual takes the left half (screen cut by the edge: 0-55.8 % W × 5.6-94.2 % H in v2; whole diagram: 11-49 % W in v4); figure and label centered on 75 % W, as a block; smaller figure (cap 16 to 22 % H) |
| **sur-photo** | 2/8: v4, v5 | white figure on a very blurred full-bleed photo (v4) or on a dark map (v5); very wide figure (cap ≈ 31 % H, 84 % W in v4); label at 72-76 % H |
| **objet-anneau**, **objet-jauge** | 1/8: v4 | the figure is drawn inside an object: glowing ring with halos (33-67 % W × 20-80 % H), full gauge (36-67 % W × 37-63 % H), dimension line drawn on a screen, pictogram slipped into the sentence |
| **contour** | 1/8: v6 | figure as a glowing outline, no fill, in the chapter's color; solid label below; the figure can change in place |

Outside slides: the same figure filmed with the presenter beside it, on the set's screen (v2, v5, v6). That is a stage shot (A22, A23), not a variant.

#### 4. Visual content

- **Centre, bloc, contour**: no visual. The figure is the image. The block's solid background.
- **Figure color**: horizontal gradient in 4/8 (v2, v3, v4, v7); plain white or black in 2/8 (v1, v4); the service's color, plain, in 1/8 (v5); glowing stroke in 1/8 (v6). The skill keeps the `accent → accent2` gradient (`style-visuel.md` §4.2), except on a photo.
- **Beside**: a screenshot in a generic device, a cut-out product or a line diagram. Framing: the screen or the product **leaves through the left edge** (v2); a diagram stays whole (v4). A very soft contact shadow on a light background only; nothing on a dark background.
- **On a photo**: full-bleed photo of the place or the use, defocused until it is only a mood (v4: library, arches, beach); dark overlay so that white holds 4.5:1. White figure and label.
- **Object**: a simple shape in the accent. Ring: thick stroke, two or three blurred rings around it (halo). Gauge: solid pill, figure in `fond_sombre` inside. v4's green comes from the battery (3/8): the skill takes the user's accent.
- **Accent**: on the figure only. The label stays in the text color (`style-visuel.md` §3 A5).

#### 5. Typography

- Measures: `style-visuel.md` §3 A5.
- **bloc**: figure center at 45.5 % H, label top at 63 % H, line spacing k = 1.6 (`style-visuel.md` §3 A5, layout b).
- **a-cote**: figure 116 pt (floor 88) in a 3.2 in column; label 22 pt, one or two lines. Measured: cap 22 % H (v2), 16 % H (v4).
- **sur-photo**: figure 144 pt, plain white; label 24 pt white. Nothing under 20 pt on a photo.
- **objet**: ring, figure 72 pt and unit 34 pt inside (measured: 13 and 6 % H of cap); gauge, figure 54 pt.
- **contour**: 2.5 pt outline (convention), same size as “bloc”.

#### 6. Build and animation

- The figure arrives **blurred and zoomed**, then settles: 2/8 (v3, v4). Engine: Zoom entrance 0.4 s.
- The label arrives second: 1/8 (v1). The label arrives first, alone: 1/8 (v2).
- The figure changes in place (before / after): 1/8 (v6). Engine: two slides and Morph.
- Ring: it draws itself (wheel); gauge: it fills up (wipe). Convention, from the states seen in v4.

#### 7. Visual brief and fallback

- **Always**: the figure, its unit, the comparison base and the source. No visual for “centre”, “bloc”, “contour”, “objet”.
- **a-cote**: a PNG screenshot at least 1,600 px wide (the screen alone, without a device bezel), or a cut-out product as a PNG with a transparent background, seen at three-quarters or from the front, at least 2,000 px high.
- **sur-photo**: a 16:9 JPEG photo of at least 1,920 × 1,080 (3,840 × 2,160 preferred), with no text and a calm center; the engine blurs and darkens it.
- **Fallback**: missing figure = `[TO PROVIDE: label]` at the figure's size, faded, dotted underline. Missing screenshot = schematic interface (`style-visuel.md` §5.2). Missing photo = the “centre” variant. A fallback ring is complete: a partial arc would state a value. The gauge of a missing figure stays empty (accent edge, no fill): the gray marker reads on the background, not on the accent.

#### 8. Avoid

- Two figures on the slide: a single giant figure in 7/8, all the keynotes that have an A5.
- A gray label: it is in the text color on the measured frames.
- A note or an asterisk under the figure: no note in 7/8, all the keynotes that show a figure (the source follows the audience, `publics.md`).
- The gradient on a photo, or on anything other than the figure.
- A figure placed in the top third with empty space below, or split over two lines.
- A label of more than 9 words.

### A6 · Comparison chart

#### 1. Role and moment

- The quantified proof of a gap, in the technical part (chip, browser, performance), or the market ranking at the start of a keynote (v7, v8).
- Presence: 6/8. Charts: v6, v1, v2, v4. Ranking: v7, v8. Absent: v5, v3 (v3 puts everything through the big figure).

#### 2. Canonical composition: “barres”

Measured on v1: centered title, cap top at 12.2 % H; bars from 15 to 85 % W, 1.1 % H thick, at 51 and 65.7 % H (step of 14.5 % H); each name **above** its bar, left-aligned on its start (15.2 % W); the gap above the end of our own bar, right-aligned (84.8 % W); the other in gray at about 42 %. v4 follows the same rule with 3 bars, on a set screen.

| Zone | x | y | w | h | Note |
|---|---|---|---|---|---|
| Title | 6 | 8.9 | 88 | 5.0 | the measured quantity, centered |
| Our name | 15 | 44.5 | 45 | 4.1 | above its bar |
| Gap | 55 | 44.5 | 30 | 4.1 | right-aligned on 85 % W; the only written value |
| Our bar | 15 | 50.5 | 70 × v/max | 1.1 | plain accent, round ends |
| The other's name | 15 | 59 | 45 | 4.1 | secondary |
| The other's bar | 15 | 65 | 70 × v/max | 1.1 | gray at 45 %; bars 3 and 4 at the same step |
| Reading direction | 15 | 72 | 70 | 2.9 | optional, in words |
| Source | 6 | 92 | 88 | 2.0 | depending on the audience |

```
+----------------------------------------------------------------+
|                                                                |
|              Title: the measured quantity · 28 pt              |  cap top 8.9 % H
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|          Ours · 23 pt                     gap · 23 pt          |  44.5 % H
|          =============================================         |  our bar, accent, 1.1 % H
|          The other · 23 pt · gray                              |  59 % H
|          ------------------------------                        |  the other's bar, gray 45 %
|                                                                |
|         reading direction in words · 16 pt (optional)          |  72 % H
|                                                                |
|                                                                |
|                         source · 11 pt                         |  92 % H
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `barres`, `deux-axes`, `anneaux`, `frise` or `classement`. Without a variant: the original rendering, simpler than the variants. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **barres** (canonical) | 2/8: v1, v4 | 2 or 3 thin horizontal bars, name above, gap at the end |
| **deux-axes** | 2/8: v1, v2 | two L-shaped axes without tick marks, named in words with their reading direction; curves (v2) or position zones (v1); a name at the end of each curve; dotted accent marker (measured v2: title at 7.5 % H, vertical axis at 19.8 % W, axis names at cap 2.9 % H, dark gray) |
| **anneaux** | 1/8: v6 | two share rings side by side, value and name inside, title on the right; both values written |
| **frise** | 1/8: v2 | the generations on an almost flat line, two periods at the ends; our own tile, glowing, jumps above; arrow and gap in the accent |
| **classement** | 2/8: v7, v8 | a table of ranks (8 rows × 3 periods) filled with logos, us at rank 1; small source at the bottom right (measured v8: 97-98 % H, 87-99 % W); dark (v7) or light (v8) |

#### 4. Visual content

- Everything is drawn: rules, bars, curves, rings. No image, except the ranking's logos and the timeline's own tile.
- **Us in color, the other in gray**: 3/8 (v1, v2, v4); the other in a pale hue: 1/8 (v6). The corpus sometimes puts a gradient on us (v1, v2); the skill keeps the plain accent and the gray at 45 % (`style-visuel.md` §4.2).
- No numbered tick marks: 4/8 (the 4 keynotes with a chart). The axes carry words.
- Depth: none, except the **frise**: our own tile has a glowing edge that spills into a halo (v2). No shadow, no 3D, no gridlines (a single grid, very dark, under v1's zones).
- Background: dark in 5/8 (v6, v1, v2, v4, v7), light in 1/8 (v8).
- Accent: our bar, curve or ring, and the gap. Nothing else.

#### 5. Typography

- Measures: `style-visuel.md` §3 A6.
- Title: it **names the quantity** or the ranking, it doesn't conclude: 6/8 (v6, v1, v2, v4, v7, v8). The conclusion is the gap.
- **deux-axes**: axis names 16 pt, reading direction 10 pt below (measured: cap 2.9 and 1.6 % H). Curve names 16 pt.
- **anneaux**: value 40 pt, name 14 pt, title 40 pt on the right (convention, from one measure on stage).
- **classement**: title 32 pt (measured: cap ≈ 5.8 % H), ranks 16 pt, periods 14 pt, source 9 pt.

#### 6. Build and animation

- Built in 2 to 4 steps: 3/8 (v6, v1, v2). v4 is only seen in its final state.
- Order: the other first, then us, then the markers: 1/8 (v2). Us first, then the other: 1/8 (v6). By default, the skill keeps “the other, then us”.
- Bars: the bar grows from the left (wipe, 0.6 s, convention).
- Ranking: all at once, the presenter reads the first row (v7, v8).

#### 7. Visual brief and fallback

- **To provide**: each value (for the length), the gap to write, the source, the other's name (named or anonymous depending on the audience, `publics.md`).
- **classement**: the ranks, the periods, and one monochrome logo per service (SVG, or transparent PNG at least 600 px wide).
- **frise**: the periods and the gap; a logo or a name for our own tile.
- **Fallback** (no number, no brand): bars as gray dotted rules of the same length, gap `[TO PROVIDE: gap]`; curves absent, replaced by `[TO PROVIDE: curves]` between the axes; empty ring; timeline without a jump; ranking as text names, ranks and periods as `[TO PROVIDE]`.

#### 8. Avoid

- Tick marks, a separate legend, gridlines, 3D.
- More than 4 bars: the corpus shows 2 or 3.
- Two accent colors, or a gradient on the bar.
- A title that states the conclusion.
- A bar length or a jump height that doesn't come from a provided value.
- The competitor's name when the audience doesn't want it (`publics.md`).

### A11 · Diagram with a highlighted block

#### 1. Role and moment

- Explain what the system is made of before putting numbers on its gains: the “inside” section of a product. One block at a time.
- Presence: 3/8 (v2, v3, v4), the 3 product events. In the corpus, it is always a chip; the skill extends it to any system in parts (architecture, platform, machine, organization).
- It comes before the performance figures: 3/8 (v2, v3, v4). It can carry the figure itself (“schema-chiffre” variant, 1/8).

#### 2. Canonical composition: “legende-laterale”

Measured: a square diagram from 31 to 69 % W and from 16.5 to 83.5 % H, centered (v3, v4; v2 a little smaller: 33-67 % W). Legend: title at cap 2.4 % H, sub-lines at cap 1.8 % H, step of 3.7 % H; on the left at 4.4-5 % W (v3, v4) or 10 % W (v2), on the right aligned on 95 % W; a 0.6 % H rule under the title, from the edge of the legend to the edge of the diagram.

| Zone | x | y | w | h | Size | Note |
|---|---|---|---|---|---|---|
| Diagram | 31 | 16.5 | 38 | 67 | — | square, thin gray stroke; 1.5 pt edge |
| System name | 32 | 18 | 15 | 4.7 | 26 pt | in the top left corner cell |
| Lit block | 31.5 | 55 | 18.5 | 28 | — | light outline, lightened inside, glow |
| Legend title | 4.5 | 53.5 | 24 | 3.2 | 18 pt | level with the top of the block |
| Rule | 4.5 | 58 | 26.5 | 0.3 | — | 0.75 pt, gray at 45 % |
| Sub-lines (1 to 5) | 4.5 | 60.5 | 24 | 11 | 14 pt | secondary; on the right, right-aligned on 95.5 % W |

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                    +---------+-------------+                   |  diagram 31-69 % W × 16.5-83.5 % H
|                    | Name    |             |                   |  name in the corner cell
|                    +---------+             |                   |
|                    |          +---+---+---+|                   |
|                    | +--+     |   |   |   ||                   |
|                    |          +---+---+---+|                   |
|   Title · 18 pt    |                       |                   |  legend title 53.5 % H
|   _________________+----------+            |                   |  rule up to the diagram's edge
|   line · 14 pt     |          |            |                   |
|   line · 14 pt     |  block   |            |                   |  sub-lines, step 3.7 % H
|   line · 14 pt     |   lit    |            |                   |
|                    |          |            |                   |
|                    +----------+------------+                   |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `legende-laterale`, `plusieurs-blocs`, `schema-chiffre`, `carte-annotee` or `carre-halo`. Without a variant: the original rendering, simpler than the variants. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **legende-laterale** (canonical) | 3/8: v2, v3, v4 | one lit block, its legend on the block's side |
| **plusieurs-blocs** | 3/8: v2, v3, v4 | 2 or 3 lit blocks, one legend per block, on both sides (v4) or stacked (v3); in v2, the names are written in the blocks |
| **schema-chiffre** | 1/8: v4 | diagram shifted left (center at 30 % W), hero figure on the right (center at 74.5 % W, cap ≈ 16 % H) with its label |
| **carte-annotee** | 1/8: v2 | top view of a real object; thin frames around the components; labels at the end of vertical rules, at the top or the bottom |
| **carre-halo** | 2/8: v2, v7 | the system reduced to a dark square and its name, surrounded by a glowing halo; in v7, a row of squares for the generations (on light). Introduction variant: it does not count in A11's 3/8 |

#### 4. Visual content

- **The diagram**: a line drawing, monochrome, gray at 30-40 % on a dark background, square, full of cells of unequal sizes. Dark background: 3/8 (all 3 cases).
- **Edge**: gradient in 2/8 (v2, v3), gray in 1/8 (v4). The skill takes the plain accent or the gray: the gradient stays on the hero figure.
- **The lit block**: lighter outline, slightly lightened inside, a soft glow (halo). It is the slide's accent.
- **The name**: in the top left corner cell, inside the diagram: 3/8 (all 3 cases). The user's logo can go with it, never another one.
- **carte-annotee**: a real top view, cut out, dark, with no shadow; 1 pt white frames.
- **carre-halo**: an almost black square, almost sharp corners (5 % of the side: a component, not an app icon); halo spilling 8 % W around it; name in the center.

#### 5. Typography

- No A11 card in `style-visuel.md`. Measured: legend title cap 2.4 % H, sub-lines 1.8 % H, semibold then regular, secondary for the sub-lines.
- **Convention**: 18 pt and 14 pt (cap 3.2 and 2.5 % H). That is a little larger than the corpus, which is made for video: in a room, text stays above 2.5 % H.
- System name: 26 pt semibold (measured: cap 4 to 5 % H).
- **schema-chiffre**: figure 90 pt, label 20 pt (A5 rules).
- 5 sub-lines at most, 4 words each.

#### 6. Build and animation

- The block lights up with its legend, at the same moment: 3/8 (v2, v3, v4). The diagram alone first: seen in 1/8 (v4).
- The highlight moves from one block to the next on the same image: 3/8 (v2, v3, v4). Engine: one slide per block, Morph; fade as a fallback.
- **carte-annotee**: one label per click, with its frame and its rule (v2).

#### 7. Visual brief and fallback

- **To provide**: the user's diagram in SVG, or as a transparent PNG of at least 2,000 × 2,000 px, line drawing, a single color; the list of blocks, each with a title and 1 to 5 lines; the system's name.
- **carte-annotee**: a top-down photo (at 90°), cut out, transparent PNG at least 2,400 px wide, and the position of the components to annotate.
- **Fallback**: the engine draws a plan of blocks in line art (a subdivided grid of 8 to 12 unequal cells), lights one cell and places the legend; no writing in the cells, no number; name as `[TO PROVIDE: name]` if it is missing.

#### 8. Avoid

- The photo or render of a real branded chip.
- Blocks filled with different colors.
- More than one lit block per click, except “plusieurs-blocs” (3 at most).
- A legend without a rule, a diagonal rule, a legend of more than 5 lines.
- Text in the diagram, other than the corner name.

### A15 · Wall of abundance

#### 1. Role and moment

- Say “there are many” without detailing them. Right after the bento: 1/8 (v8, the wall at the end of a section). Instead of a number said aloud: 1/8 (v7, the wall of icons).
- Presence: 6/8 (v5, v6, v1, v7, v8, v3). Absent: v2, v4.
- It is looked at, not read: that is the point.

#### 2. Canonical composition: “vignettes”

Seen on v1: 16:9 thumbnails of about 21 % W × 21.5 % H, gutter of 1.25 % W and 2.2 % H, rounded corners, offset rows, cut by the edges. Measured on v8 (cards): gutter 1.25 % W and 2.1 % H.

| Zone | x | y | w | h | Note |
|---|---|---|---|---|---|
| Grid | −4 | −3 | 108 | 106 | 4 rows, offset by a third of a thumbnail; 20 to 24 thumbnails visible |
| A thumbnail | 1 | 1 | 21 | 21.5 | provided image in “cover” mode, radius 1.2 % W, no added text |

The negative coordinates, or those past 100, are intended: the wall spills over.

```
+----------------------------------------------------------------+
|:::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::|  16:9 thumbnail: 21 % W × 21.5 % H
|:::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::|
|                                                                |  gutter 1.25 % W · 2.2 % H
|::::::::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::|
|::::::::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::|
|::::::::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::|  rows offset by a third
|                                                                |
| ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::::::|
| ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::::::|
| ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::::::|  cut by all 4 edges
|                                                                |
|::::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: ::|
|::::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: ::|
|::::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: ::|  radius 1.2 % W, no shadow
|                                                                |
|:::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::::::::::|
|:::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::::::::::|  no readable text
|:::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::::::::::|
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `vignettes`, `icones`, `mots`, `nuage`, `cartes-libelles` or `forme`. Without a variant: the original rendering, simpler than the variants. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **vignettes** (canonical) | 3/8: v1, v5, v8 | posters, covers or sleeves in the content's format (16:9, 3:4, 2:3) |
| **icones** | 3/8: v5, v6, v7 | dozens of identical badges (rounded square or circle, ≈ 7.5 % W), packed tight, rows offset by half a badge; in v5, faces |
| **mots** | 3/8: v6, v7, v8 | justified lines of labels, small and gray (v6: cap 1.8 % H, 5 lines) or medium (v8: cap 2.9 % H, step 10.3 % H; v7: cap 4.2 % H, two tones, spills past the edges) |
| **nuage** | 3/8: v3, v7, v8 | scattered words on three depth planes (size and opacity), cut by the edges; in v8, a sharp name in the foreground |
| **cartes-libelles** | 1/8: v8 | 6 × 6 small white cards (measured: 15.2 % W × 14.2 % H), icon at the top left, 2-line label at the bottom |
| **forme** | 1/8: v5 | the mosaic cut into a simple shape (a heart), next to the presenter |

#### 4. Visual content

- **The user's content, in numbers**: thumbnails of their content, icons of their integrations, names of their features.
- **Framing**: the wall of images touches or passes the edges: 5/8 (v1, v5, v6, v7, v8), all the keynotes with a wall of images, except the “forme” variant. The wall of words keeps a margin of 3.6 to 6 % W: 2/8 (v6, v8); it spills over: 1/8 (v7).
- **Treatment**: rounded corners, no border, no shadow, no reflection; a thin, regular gutter. Depth only in the **nuage**: three sizes and three opacities (full, about 70 %, about 30 %), seen on v3.
- **Accent**: none in the walls of images (an accepted exception to the single-accent rule: the images keep their colors, `style-visuel.md` §4.1). Words: secondary color, or two alternating tones (v7). Cloud: a single hue.
- Background: the block's (dark or light).

#### 5. Typography

- `style-visuel.md` has no A15 card. With the bento, this is the place where text can go below 3 % H: it is looked at.
- **mots**: 16 pt (cap 2.9 % H), regular or semibold, step of 10.3 % H, 3 or 4 labels per line (measured v8). Floor: 10 pt (v6 measured at 1.8 % H).
- **nuage**: 36 / 22 / 13 pt for the three planes (convention, from v3); the foreground name at a reduced A1 size (52 pt).
- **cartes-libelles**: 9 pt label, 2 lines.

#### 6. Build and animation

- Slow scroll: 2/8 (v8 cards that rise, v7 cloud that crosses the screen). Engine: two slides and Morph on a grid offset by one row (8 s), or a slow motion path; fallback: fade entrance.
- Elsewhere, the wall is seen still, all at once. An entrance item by item: 0/8 on the frames reviewed.

#### 7. Visual brief and fallback

- **vignettes**: 20 to 40 images in the same format, at least 640 px wide each, with no added text (JPEG or PNG).
- **icones**: 40 to 100 square PNG icons of at least 256 × 256, on a solid or transparent background, all on the same template.
- **mots, nuage, cartes**: 24 to 40 labels of 2 to 5 words (and one icon per card). Labels drawn from the brief can be proposed as `[TO VALIDATE]`, with no number.
- **Fallback**: missing thumbnails and icons = flat fills in a few shades close to the background, one gray bar per thumbnail, one geometric pictogram per icon badge (one in nine tinted with the accent), never a light screen in the middle of the wall (`style-visuel.md` §5.2); missing labels = rounded bars of varied lengths. The cloud has no fallback: it becomes “mots” with bars.

#### 8. Avoid

- A grid floating in the center with margins: it becomes a catalog, or a bento.
- A readable, larger or accented item in the middle of the wall (except the cloud's name).
- Fewer than about twenty items: the wall no longer says “many”.
- Mixed formats, shadows, frames.
- A number written on the wall: it is spoken, or it becomes an A5.

### A16 · Partner logos

#### 1. Role and moment

- The proof of adoption, right after a standard, a service or a partnership is announced. A second, denser grid can follow for “even more”: 1/8 (v8).
- Presence: 5/8 (v5, v6, v1, v8, v4). Variant in v7: a single logo, full frame. Absent: v2, v3.

#### 2. Canonical composition: “grille”

Measured on v8 (5 × 4): column centers at 14.5 / 32.3 / 50 / 67.7 / 85.3 % W (step 17.7 % W), row centers at 17 / 39 / 61 / 82.7 % H (step 21.9 % H). Wordmarks are 7 to 11 % W by 1.4 to 3.3 % H; emblems 2.8 to 5.2 % W by 5 to 8 % H: the optical weight is equal, not the height.

| Zone | x | y | w | h | Note |
|---|---|---|---|---|---|
| Grid | 8.5 | 6 | 83 | 88 | 3 to 5 columns; 2 rows: centers 38 / 62; 3: 28 / 50 / 72; 4: 17 / 39 / 61 / 82.7 |
| A cell | 9 | 13 | 11 | 8 | the logo's box at most; logo at equal area (target area 0.15 in², convention) |

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                    @@@                   @@@                   |
|      =======       @@@      =======      @@@       =======     |  row 1 · center 17 % H
|                                                                |
|                                                                |
|                               @@@        @@@                   |
|      =======     =======      @@@        @@@       =======     |  row 2 · 39 % H
|                                                                |
|                                                                |
|                               @@@                              |
|      =======     =======      @@@      =======     =======     |  row 3 · 61 % H
|                                                                |
|                                                                |
|                               @@@        @@@                   |
|      =======     =======      @@@        @@@       =======     |  row 4 · 82.7 % H
|                                                                |
|                                                                |  columns 14.5 / 32.3 / 50 / 67.7 / 85.3 % W
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `grille`, `ligne`, `logo-seul`, `mur-dense`, `pastilles` or `soi-au-centre`. Without a variant: the original rendering, simpler than the variants. Fields for each variant: `deck-spec.md`, “Variants”.

| Variant | N/8 | What changes |
|---|---|---|
| **grille** (canonical) | 4/8: v1, v5, v6, v8 | 3 to 5 logos per row, 2 to 5 rows, centered |
| **ligne** | 4/8: v1, v4, v5, v8 | 2 to 4 logos on one line, larger (v8: 16 to 22 % W × 7.5 to 9.4 % H, centers 18 / 48 / 80 % W) |
| **logo-seul** | 3/8: v1, v5, v7 | one partner full frame, centered, up to 46 % W |
| **mur-dense** | 3/8: v5, v6, v8 | 30 to 80 logos packed tight; in v8, the grid of 20 tightens into 33 |
| **pastilles** | 1/8: v5 | each white logo in a round badge of its own color, 3 staggered rows |
| **soi-au-centre** | 1/8: v1 | your own logo at the center of the alliance, staggered rows 3 / 4 / 3 / 4 / 3; it arrives first between two partners |

#### 4. Visual content

- **Monochrome logos** in the text color (white on dark, black on light): 5/8 (v1, v4, v5, v6, v8), on every frame seen. Only exception: “pastilles” (1/8, v5).
- **No added text**: no title, no caption, on every grid seen (5/8: v1, v4, v5, v6, v8).
- **Size**: it follows the count. 3 logos: 16 to 22 % W wide (v8); 6 logos: 10 to 20 % W (v5); 20 logos: 7 to 11 % W (v8); 60 logos: a few % (v6).
- **Depth**: none. No shadow, no tile, no frame. The block's background, or a blurred light background (v8).
- **Accent**: none.

#### 5. Typography

- No text. Grid measures: `style-visuel.md` §3 A16; logo size follows their optical weight (§2 above).
- A missing logo is written as a name: 20 pt semibold, secondary.
- The skill still allows a short kicker (convention); the corpus shows none.

#### 6. Build and animation

- The grid arrives all at once: 5/8 (v5, v6, v1, v8, v4).
- A denser grid follows for “even more”: 1/8 (v8). Engine: Morph from the grid of 20 to the grid of 33.
- A single logo, then a pair split by a rule: 1/8 (v5). Your logo between two partners, then the alliance around it: 1/8 (v1).

#### 7. Visual brief and fallback

- **To provide**: each logo in a monochrome version (white for a dark background, black for a light one), in SVG or as a transparent PNG at least 600 px wide, cropped tight to the drawing; the partners' consent to show them.
- **soi-au-centre**: the user's logo, in the same color as the others.
- **Fallback**: the partner's name as text, semibold, secondary, centered in its cell. Never an imitated or redrawn logo. With neither a name nor a logo, the cell stays empty and the slot becomes `[TO PROVIDE: logo]` in the notes.

#### 8. Avoid

- Logos in mixed colors (except “pastilles”).
- All logos at the same height: wordmarks become huge, emblems tiny.
- A title like “they trust us” above the grid: 0/8.
- More than 5 logos per row in a standard grid (beyond that, it is a “mur-dense”).
- A frame, a tile or a shadow behind each logo.
- A customer's or partner's logo without their consent, or a competitor presented as a partner.

## 6. Product and image

The slides where the image takes all the room: the object, the screen, the inside, the product, the photo; then the stage shots, which are video. Images reviewed: 186.

### A9 · Object + text

#### 1. Role and moment

- The detail of a feature or a property: the object or the screen shows, one to four lines name.
- It comes after the feature name (A1, A2) or after the full-bleed screen (A10) of the same feature. It comes before the figure that proves it (A5) or the recap (A14).
- Present in 7/8 (v5, v6, v2, v7, v8, v3, v4). v1 only has the stacked version (variant f).
- It also works as a minimal caption: a feature or app name set next to a screen (v4, v7, v8).

#### 2. Canonical layout

Object cut by the frame on the left, statement centered in the free column on the right.

| Zone | x | y | w | h | Where the value comes from |
|---|---|---|---|---|---|
| Object (image, bleeding off) | 0 | 0 | 58 to 62 | 100 | measured: 0–58 % W (v2), 0–62 % W (v3), bleeds off 2 or 3 edges |
| Statement (1 or 2 lines) | 66 | 38 | 28 | 24 | measured: center at 79.6–81.1 % W and 49.9–50.6 % H on 6 images (v3, v4, v7, v8); cap 5.8 to 6.1 % H |
| Mirror (object on the right) | — | — | — | — | measured: text centered at 20.0–20.5 % W (v3, v7) |

```
+------------------------------------------------------------+
|####################################                        |
|####################################                        |
|####################################                        |
|####################################                        |
|####################################                        |
|####################################                        |
|####################################  +------------------+  |
|####################################  |    Statement     |  |
|##### OBJECT cut by the frame ######  |    1-2 lines     |  |
|######## x 0  w 56-62  h 100 #######  |    center 80 %   |  |
|####################################  |                  |  |
|####################################  +------------------+  |
|####################################                        |
|####################################                        |
|####################################                        |
|####################################                        |
|####################################                        |
|####################################                        |
+------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `appareil-centre-mot`, `objet-coupe`, `objet-liste`, `objet-chiffre`, `annotee` or `empilee`. With no variant: the original rendering, simpler than the variants. Fields of each variant: `deck-spec.md`, “Variants”.

**a. Centered device + word (`appareil-centre-mot`)**: 3/8 (v4, v7, v8).
- The device stays where it sits in A10: 37.5–62.3 % W × 4.4–95.3 % H, centered on (50, 50) (measured, 4 images). The word, or 2 to 3 short lines, is centered in the margin at 81 % W, cap 5.8 % H (measured, 4 images). The word is a feature or app name.
- Light background (v7, v8) or black (v4).

**b. Cut object + statement (`objet-coupe`)**: 2/8 (v3, v7).
- The product in close-up, or a laptop, runs off the frame by 2 or 3 edges and covers 58 to 62 % W. The statement fits in 2 to 4 words, on 2 lines.
- On black, the text can take a gradient in the product's hue (v3, 1 image): the skill keeps the text color.

**c. Icon or object + list (`objet-liste`)**: 4/8 (v2, v5, v6, v8).
- An icon or a whole object on the left; 3 to 5 left-aligned lines in a block that starts at 45 % W.
- Icon: 21 % W × 37.5 % H, centered on (22 %, 50 %) (measured, v8). Lines: cap of about 4.2 % H (`style-visuel.md`), one every 8 % H (measured, v8).
- On stage (v5, v6), the object is in the middle of the wall and the list to its right. v2 puts the list above a cut laptop, separated by a vertical rule.

**d. Object + figure (`objet-chiffre`)**: 2/8 (v2, v4).
- The object cut on 0–58 % W (v2) or whole on 11–49 % W (v4). A figure in A5 style, centered at 74.5–75.4 % W, cap of 16 to 22 % H, with its label below (measured, 2 images).
- The figure is in a gradient (2/2). It is the only A9 case where the text carries the accent.

**e. Annotated object (`annotee`)**: 3/8 (v2, v5, v6).
- The object or the screen in the center; 2 to 5 short labels around it, tied to their point by a thin rule (v2), a curved arrow (v5) or a chevron (v6).
- v5 gives each arrow its own color: the skill does not copy this (one accent color only).

**f. Stacked (`empilee`)**: 1/8 (v1).
- The object at the top (23–37 % H), the name below (cap of about 5.3 % H, center at 48 % H), then 3 centered lines (cap of about 4.2 % H, one every 8.6 % H) (measured, 1 image). This is the spec sheet; the price slide reuses this frame.

#### 4. Visual content

- **Type**: cut-out product or macro photo (b, d); screenshot inside the generic device (a); icon (c); clean render or screenshot, from the front or from above (e); cut-out product (f).
- **Framing**: in b and d, the object runs off the frame by 2 or 3 edges (5 images out of 5, v2, v3, v7). In a, the device is whole, at the exact A10 position. In c, e and f, the object is whole.
- **Treatment**: solid background of the block; soft studio light, with a light edge along the object's outline; no shadow (0 out of 26 images). A screenshot stays whole: a cut interface reads as a framing error (`style-visuel.md` §5.2).
- **Accent**: the text stays in the text color (9 images out of 10, v3, v4, v7, v8). The color comes from the image. The accent goes to the figure (d), or to a single rule or chevron (e), or to the highlighted line of a schematic interface.

#### 5. Typography

- Base: `style-visuel.md` §3 A9. Statement in 34 pt, semibold, line spacing k = 1.5, centered in the column; icon variant: lines in 24 pt, left-aligned, k = 1.8.
- (a) The word in 34 pt too (measured cap 5.8 % H, about 32 pt), one line, three at most. No kicker: the word is already the caption.
- (d) Figure in 110 pt (floor 80 pt), in A5 style and gradient; label in 20 pt semibold, text color.
- (e) Labels in 20 pt semibold, 2 to 4 words each; 1 pt rule in secondary text color.
- (f) Name in 32 pt; lines in 24 pt centered, k = 1.95.

#### 6. Build and animation

- On a slide: the object first, then the text on click (corpus analysis). A list comes line by line (v6) or as one block (v8).
- In a prerecorded video, the slide arrives whole on a cut from the presenter (v8, checked frame by frame).
- A10 → A9 sequence (a): same device, same place; the word fades in alone. With two objects of the same name, Morph does it without a jump (convention inferred from the measurements).
- (e) The labels come in one by one, each with its rule.

#### 7. Visual brief and fallback

| Variant | What to ask the user for | Fallback drawn if the image is missing |
|---|---|---|
| a | Bare screenshot, PNG, at the screen's native format (portrait), at least 1170 px wide, with no device frame; the exact state to show; real data or data the user has anonymized. | Generic device and the engine's schematic interface, at the measured position (37.5 / 4.4 / 25 / 91). |
| b, d | Photo or render of the product in close-up, cut-out PNG (transparent background) or on a plain background close to the deck background; 3/4 or side angle; the detail being discussed in the center of the image; at least 2400 px on the long side. | Shaded object silhouette (rule 6), light edge at 2 % of its width, visible from 0 to 58 % W and pushed off the frame on the left and at the bottom; contact shadow on a light background only. |
| c | Icon or logo of the feature, SVG or transparent PNG, square, at least 1024 px. | Rounded square (radius 22 % of the side, convention) in solid accent, with a simple white geometric shape (circle or stroke). |
| e | Render or screenshot from the front or from above, at least 2400 px; the list of the 2 to 5 points to call out, with their position on the image. | Silhouette or schematic interface; labels proposed as `[TO VALIDATE]`, with no number; rules in secondary text color. |
| f | Cut-out product, transparent PNG, at least 1600 px wide. | Object silhouette centered at the top. |

In every case, `image.attendu` says what the image must show, and the fallback carries no figure, no logo and no brand name.

#### 8. Avoid

- A whole object floating in the middle of its half: it looks less like a keynote than an object cut by the edge (b, d).
- Text stuck to the object, or at the top of the column: it is centered in the free column, at 50 % H.
- More than four lines.
- A drop shadow on a dark background, a frame around the object or the text.
- A screenshot cut by the edge of the frame.
- A recognizable device (notch, island, buttons, camera): ask for a bare screenshot.
- Arrows in several colors, or an accented word on an object that already has color.

### A10 · Full-bleed screenshot

#### 1. Role and moment

- Any feature explanation: the screen shows, the voice explains, no text is added. The text comes from the interface.
- It is the most frequent shot apart from the presenter: about 27 % of the images in v1, half of the shots with no speaker in v8 (v1 and v8).
- Present in 8/8. It follows the feature name (A1, A2) and comes before the caption (A9) or the demo (A25).

#### 2. Canonical layout

Vertical device, from the front, centered.

| Zone | x | y | w | h | Where the value comes from |
|---|---|---|---|---|---|
| Device (portrait) | 37.5 | 4.4 | 25 | 91 | measured on 7 images from 5 keynotes (v1, v3, v4, v6, v8): 36.2–62.7 % W × 2.5–97.2 % H, center (49.5–49.9; 49.7–49.9) |
| Screen inside the device | 38.3 | 5.8 | 23.4 | 88.3 | engine convention: bezel of 3 % of the device width |
| Tablet (landscape) | 14 | 4.4 | 72 | 91 | measured, 3 images (v1, v4, v8): 67 to 77 % W |
| Laptop (landscape) | 7 | 4.5 | 86 | 91 | measured, 2 images (v2, v8) |

```
+------------------------------------------------------------+
|                                                            |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      :::: DEVICE ::::                      |
|                      :::: x 37.5 ::::                      |
|                      ::::: w 25 :::::                      |
|                      ::::: h 91 :::::                      |
|                      :::: center ::::                      |
|                      :::: 50 / 50 :::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                                                            |
+------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `telephone-centre`, `tablette-centre`, `portable-centre`, `zoom-serre`, `capture-nue` or `rangee`. With no variant: the original rendering, simpler than the variants. Fields of each variant: `deck-spec.md`, “Variants”.

**a. Centered phone (`telephone-centre`)**: 5/8 (v1, v3, v4, v6, v8), 7 images measured.
- The box does not move from one keynote to the next (gap of 1.5 % W at most). Black background (v1, v3, v6) or light (v4, v8).

**b. Centered tablet (`tablette-centre`)**: 3/8 (v1, v4, v8).
- Landscape, 67 to 77 % W × 91 % H, from the front. Top and bottom stay at 4.4 and 95.3 % H, like the phone.

**c. Centered laptop (`portable-centre`)**: 2/8 (v2, v8); v7 has one too, seen only with a word (A9).
- 86 % W × 91 % H; the keyboard is only a thin base under the screen.
- Deviation seen once (v2): a large screen on a stand, the small box at its foot.

**d. Tight zoom (`zoom-serre`)**: 3/8 (v3, v6, v7).
- A small device (a watch) framed as tight as possible: the case covers 28–74 % W, the band runs off the frame at the top and bottom (measured, 3 images). The screen almost becomes a slide.

**e. Bare full-bleed screenshot (`capture-nue`)**: 3/8 (v1, v2, v6).
- A computer desktop or an app, with no device, bleeding off (0–100 %). This is the mode for desktop software.
- A supplied screenshot bleeds off only if it is 16:9 (within 4 %); otherwise it stays whole, contained in 92 % H, with 0.12 in corners (a cut interface reads as a framing error). With no screenshot: schematic card on 85 % H.

**f. Row of devices (`rangee`)**: 3/8 (v5 from the video analysis, v6, v7).
- Two to five devices side by side, all the same size: three phones of 24 % W each, 3.5 % W apart, on 94 % H (estimated, v7). They show three states or three themes of the same screen.

#### 4. Visual content

- **Type**: the user's real interface, as a bare screenshot, placed by the engine inside the generic device.
- **Framing**: from the front, with no perspective (0 tilted views out of 24 images); the whole device (a, b, c, f) or cut at top and bottom (d); the bare screenshot bleeding off (e).
- **Treatment**: no shadow, no reflection (24 images). Solid background of the block: black or light. The blurred, colored background of v8 (1/8) is not reused (`style-visuel.md` §4.3).
- **Screen state**: a real, frozen state, with a neutral time and date, and no stray notification.
- **Accent**: in the interface only. If it is schematic, a single line in accent (§5.2).

#### 5. Typography

No added text (`style-visuel.md` §3 A10). If a word is needed, it is A9 a: same device, same place, the word in the margin.

#### 6. Build and animation

- In video, the interface moves; cut hard to and from the presenter (corpus analysis). Between two full-bleed shots, a fade through the block's background (v7, more than 30 fades through gray).
- On a slide: 0.5 s fade in. Several screen states = several slides with the same framing, each click shows the next state (Morph, otherwise a fade).
- Row: the devices come in together (convention).

#### 7. Visual brief and fallback

- **To ask for**: bare screenshots, PNG, at native resolution. Phone in portrait: at least 1170 × 2532 px. Tablet: at least 2360 × 1640 px. Laptop: at least 2560 × 1600 px. Full-bleed screenshot: 16:9, at least 1920 × 1080 (3840 × 2160 recommended). If the screen moves, an MP4 recording too, to be placed by hand.
- Never a mockup with the frame of a retail device: the engine draws the generic device.
- **Fallback**: the engine's generic device and schematic interface (`style-visuel.md` §5.2): gray bars, one line in accent, no text, no figure. For a bare screenshot: schematic card on 85 % H, centered, 0.12 in corners.

#### 8. Avoid

- Text added on or next to the screen (that makes it A9).
- A tilted device, in perspective, or smaller than 85 % H.
- A recognizable device frame.
- A blurry screenshot, one enlarged beyond its resolution, or one from another ratio stretched to fit.
- Real customer data on screen.
- A blurred or gradient background.

### A12 · Inside view / exploded view

#### 1. Role and moment

- Show what cannot be seen: the inside, the making, the material. It is the “engineering” part of a product.
- Present in 4/8 (v6, v2, v3, v4): the 4 keynotes that launch a device. v5 shows a macro of the making, with no exploded view (not counted).
- It comes after the name of the property and before the figure that measures it (A5). With no text, or with a single tag.

#### 2. Canonical layout

Open or exploded object, centered, on a dark background; one tag at most.

| Zone | x | y | w | h | Where the value comes from |
|---|---|---|---|---|---|
| Open or exploded object | 20 | 6 | 60 | 88 | measured on 3 images (v2, v4): 43 to 71 % W × 79 to 99 % H, centered on (50, 50) |
| Tag (0 or 1) | 48 | 9 | 14 | 5 | estimated (v4): at the top, cap of about 3 % H, 1 pt vertical rule down to the part |

```
+------------------------------------------------------------+
|                          +------------+                    |
|                          |    tag     |                    |
|                          +------------+                    |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|            ########### OPEN OBJECT ############            |
|            ########### or EXPLODED ############            |
|            ######### x 20  w 60  h 88 #########            |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|                                                            |
+------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `macro-matiere`, `capot-ouvert`, `eclate-axial` or `flux-lumiere`. With no variant: the original rendering, simpler than the variants. Fields of each variant: `deck-spec.md`, “Variants”.

**a. Material macro (`macro-matiere`)**: 2/8 (v2, v3); v5 shows the same grammar outside A12.
- A detail in extreme close-up, bleeding off, in raking light, with a shallow depth of field; or a tool at work, sparks, parts laid out. No text.

**b. Open cover or transparency (`capot-ouvert`)**: 3/8 (v2, v4, v6).
- The whole object, from the front or from above, with the cover removed or made translucent. Centered, 44 to 72 % W × 79 to 91 % H (measured, 2 images). Dark background (v6) or light (v2, v4).

**c. Exploded along an axis (`eclate-axial`)**: 2/8 seen (v2, v4); 3/8 with v6, where the analysis describes the parts coming out one by one.
- The parts float, separated along one axis (horizontal in v4, vertical in v2), on 44 % W and the full height (measured, v4), or in stacked slices that run off the frame (v4). One tag at most.

**d. Flow and light (`flux-lumiere`)**: 3/8 (v2, v4, v6).
- What flows is drawn: air as streaks (v6), heat as arcs (v2), a beam of light (v4); or a colored halo around the part being discussed (v2). The object stays in the center; the flows spread over 60 to 80 % W.

#### 4. Visual content

- **Type**: 3D render or macro photo; materials: metal, glass, circuit, technical fabric.
- **Framing**: the macro bleeds off and runs off the frame (a); the open or exploded object is whole and centered (b, c).
- **Treatment**: raking light that makes the edges shine; dark background (v3, v4, v6) or light gray (v2, v4): the skill uses the block's background. Depth: shallow depth of field (a), spacing between parts (c), halo (d).
- **Accent**: the halo or the flow, and nothing else. The corpus gives the flow two colors (cold and warm, v6); the skill keeps the accent for what is being discussed and the secondary gray for the rest (convention).

#### 5. Typography

- Tag: 16 pt semibold, text color, 1 to 2 words, 1 pt rule in secondary text color (cap estimated at 3 % H, v4).
- No other line. The name of the property goes on a title card (A1) before or after.

#### 6. Build and animation

- In video: slow camera move; the layers separate (corpus analysis).
- On a slide: two slides with the same framing, the object assembled then exploded, with objects of the same name: Morph does the separation; otherwise a fade.
- The tag arrives on click, after the separation. The flow arrives after the object (two beats).

#### 7. Visual brief and fallback

- **To ask for**: a 3D render or a macro photo. Full-bleed (a): 16:9, at least 3840 × 2160 px. Open or exploded object (b, c): cut-out PNG, at least 2400 px on the long side. For the exploded view: two files with the same framing and the same scale, one assembled, the other exploded. The exact name of the part to tag.
- **Fallback**: a schematic exploded view: 3 to 5 plates with rounded corners, stacked with a slight offset, in shaded fills of the text color mixed 9 to 16 % toward the background, clearly apart (an exploded view reads through the spacing between parts); a single highlighted part, with an accent outline and glow (never a faded accent fill, which turns brown on a dark background); the tag to the right of that part, its rule crossing no other part; no figure, no invented tag.

#### 8. Avoid

- Several tags, or numeric specs with no source.
- Two accent colors in the flows.
- Flat lighting, a dimensioned technical drawing.
- A textured or gradient background.
- A macro blurry across its whole surface: the sharp area must show the part being discussed.

### A13 · Product alone

#### 1. Role and moment

- The product reveal, then the support for each property: the product turns while the voice describes it.
- Present in 6/8 (v5, v6, v1, v2, v3, v4). Absent from the last two software events (v7, v8), which have no hardware.
- It follows the reveal film or the title card with the name. No text.

#### 2. Canonical layout

Whole product, centered, on the block's solid background.

| Zone | x | y | w | h | Where the value comes from |
|---|---|---|---|---|---|
| Product | 36 | 14 | 28 | 72 | measured on 5 images (v1, v3, v4): height 60 to 87 % H, center at 45–50.5 % W and 49–53 % H |

The width follows the product's shape; only the height is fixed. No visible shadow (5 images out of 5).

```
+------------------------------------------------------------+
|                                                            |
|                                                            |
|                                                            |
|                      ################                      |
|                      ################                      |
|                      ################                      |
|                      ### PRODUCT ####                      |
|                      ##### whole ####                      |
|                      ### h 60-87 % ##                      |
|                      #### center ####                      |
|                      #### 50 / 50 ###                      |
|                      ################                      |
|                      ################                      |
|                      ################                      |
|                      ################                      |
|                                                            |
|                                                            |
|                                                            |
+------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `centre-entier`, `hero-coupe`, `profil-levitation` or `coloris`. With no variant: the original rendering, simpler than the variants. Fields of each variant: `deck-spec.md`, “Variants”.

**a. Whole and centered (`centre-entier`)**: 3/8 (v1, v3, v4).
- From the front or at 3/4, on light (v3, v4) or on black (v1).

**b. Cropped hero (`hero-coupe`)**: 4/8 (v2, v3, v4, v5).
- Close-up from a slightly low angle or on a detail (lens, dial, edge); the product runs off the frame by 1 to 4 edges (measured: 12.5–99.4 % H in v3, 1–99 % W in v4).

**c. Floating profile (`profil-levitation`)**: 2/8 (v2, v3).
- The object seen from the side, flat or half open, floats in the middle: 71 % W × 20 % H in v3 (measured), inside the set in v2. It says thinness.

**d. Colorways (`coloris`)**: 2/8 (v3, v4).
- A fan of the colorways around an axis (v3, 63 % W × 69 % H, measured), or two views side by side, front and back (v4, 52 to 77 % W × 70 to 80 % H, measured).

**Off slide: the real product on a stand**: 1/8 (v6). Live, the real product sits on a black stand at stage side, and the presenter stands next to it. This is room staging: the engine does not draw it.

#### 4. Visual content

- **Type**: cut-out render or studio photo of the user's product.
- **Framing**: whole and centered (a, c, d); cut by the edge (b).
- **Treatment**: soft studio light, light edges; no visible shadow (5/5 in a); solid background of the block. The corpus changes background by category (3/8, v2, v3, v4); the skill keeps the block's background and only changes it between two blocks.
- **Accent**: none. The product carries its own color.

#### 5. Typography

No text (`style-visuel.md` §3 A13). The name comes first, on a title card (A1).

#### 6. Build and animation

- In video: slow rotation (v3, v4), floating entrance (v2), or a macro detail then a pull back to the whole object (v2, checked frame by frame).
- On a slide: the pull back is rebuilt with two slides, the detail (b) then the whole object (a), objects of the same name, with Morph; otherwise a 0.5 s fade.

#### 7. Visual brief and fallback

- **To ask for**: cut-out PNG with a transparent background; front or 3/4 front angle, from a slightly low angle for the hero; soft light, with no baked-in shadow or reflection; at least 2000 px tall. One file per colorway, same angle and same scale. For the profile, an exact side view.
- **Fallback**: the engine's object silhouette (shaded volume, light edge, soft highlight), centered on 72 % H; contact shadow on a light background only; no detail that imitates a real product.

#### 8. Avoid

- A product too small (under 50 % H), or text next to it.
- A drop shadow on a dark background, a floor reflection.
- A dirty cut-out (white fringe around the object).
- A gradient or textured background.
- Several different products: that makes it a lineup (A20).

### A18 · Full-bleed photo

#### 1. Role and moment

- Two uses. **Use**: emotion before the argument, a person living with the product. **Example**: a photo taken with the product, as proof of quality.
- Present in 5/8 (v5, v6, v2, v3, v4).
- The use shot comes right after the title card, in 2nd position (v2: 3 product cards out of 3). The example lives in the “image” chapter (v3, v4).

#### 2. Canonical layout

Bleeding photo, with no frame and no rounded corners (`style-visuel.md` §4.3); an optional caption box at the bottom right.

| Zone | x | y | w | h | Where the value comes from |
|---|---|---|---|---|---|
| Photo | 0 | 0 | 100 | 100 | observed: bleeds off the screen or the wall, 19 images out of 19 |
| Caption box (example) | 77 | 82 | 18 | 12 | estimated on 2 images (v3, v4): 81–95 % W × 76–94 % H; the skill cuts it to 3 lines |

```
+------------------------------------------------------------+
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|................... PHOTO bleeding off .....................|
|.................. subject on a third ......................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|..............................................+---------+...|
|.............................................. caption .....|
|..............................................+---------+...|
|............................................................|
+------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `usage`, `exemple-cartouche`, `diptyque` or `photo-titre`. With no variant: the original rendering, simpler than the variants. Fields of each variant: `deck-spec.md`, “Variants”.

**a. Use (`usage`)**: 3/8 (v2, v5, v6).
- A scene from life: a person uses the product in a real place, subject on a third, product sharp and visible. Live, the photo covers the whole wall and the presenter stands in it at the scale of a figurine.

**b. Example + caption box (`exemple-cartouche`)**: 2/8 (v3, v4).
- A strong photo (portrait, landscape, animal) taken with the product. At the bottom right, a translucent gray caption box with rounded corners: 3 lines in accent (device, author, place), then the settings in white, in small caps (seen at full resolution, 2/2).

**c. Diptych (`diptyque`)**: 2/8 (v3, v4).
- Two photos side by side, each on one half, edge to edge; one caption box per photo, in the outer bottom corners.

**d. Photo + title (`photo-titre`)**: 2/8 (v2, v4).
- A calm shot of the place or of a material (wall, sand seen from the air, wood, smoke), with a large plain area in the center. A word or a sentence in white, centered at 47.4–48.6 % H, cap of 11 to 14 % H (measured, 3 images v4). No scrim (4/4).

#### 4. Visual content

- **Type**: real photo. Use: person and product in context. Example: photo taken with the product. Photo + title: calm place or material.
- **Framing**: bleeding off; subject off-center, on a third (6 use images out of 10); center left free for the title (photo + title, 4/4).
- **Treatment**: natural light, warm or evening; shallow depth of field (use); no visible retouching, no filter. The caption box: translucent gray fill (about 55 % opacity, estimated), corners rounded at about 1 % W, no stroke.
- **Accent**: the photo carries the color. Only the first lines of the caption box go to accent (2/2). The title stays white (4/4).

#### 5. Typography

- Photo + title: 72 pt semibold, white, centered at 47.5 % H (measured cap 11 to 14 % H, so 62 to 80 pt); 2 lines at most, then 56 pt, line spacing k = 1.6. This is the A1 scale: the corpus shows no title at the bottom and no scrim (4/4).
- Caption box: 10 pt (floor 9), regular, 3 lines at most; the first two in semibold accent.
- No shadow on the text (`style-visuel.md` §1, rule 7). If the title contrast falls below 3:1, change the photo; failing that, a very soft radial scrim of 20 to 30 % in the center (convention).

#### 6. Build and animation

- Fade (corpus analysis). The caption box comes in with the photo (convention). Both photos of the diptych are there together (2/2 images).
- Photo + title: the photo first, the title fades in the moment it is said.
- No slow zoom on the photo (none seen).

#### 7. Visual brief and fallback

- **To ask for**: a 16:9 photo, 3840 × 2160 px recommended, at least 1920 × 1080, JPEG quality 85 or higher, with usage rights and the consent of the people shown. Use: a real person with the product, subject on a third. Example: the device, the author and the place, all real; the settings only if they are exact. Diptych: two 8:9 photos, at least 1920 × 2160 px. Photo + title: a calm center over 60 % W × 30 % H.
- **Fallback**: a fill slightly lighter than the background and two neutral halos (engine, §5.2). Never a drawn person. No caption box in the fallback: its content is a fact. Photo + title: the title on that fill.

#### 8. Avoid

- A black scrim over the whole photo, a band at the bottom, a shadow under the title.
- A frame, a border, rounded corners.
- A title set on a busy area.
- A caption box with invented settings.
- A recognizable stock photo, a filter, a stretched photo.
- A photo where the product cannot be seen (use).

### A22 · Wide shot + screen

#### 1. Role and moment

- The breather between two full-bleed slides, and the entrance shot of each speaker.
- Present in 7/8 (v5, v6, v1, v2, v7, v8, v4); absent from v3, which has no screen in the set.
- **What to keep in a projected deck**: this is not a slide, it is the room. Keep the reading conditions: the presenter never covers the text; they stand next to the screen (v1, v2, v7, v8) or in front of the bottom of a giant wall, under the text (v4, v5, v6), so 7/7; in a dark room, the dark background blends the screen into the room (2/2 live); nothing essential at the bottom of the slide, which heads and the presenter hide (convention). The engine does not produce an A22 slide.
- **What to keep in a video**: a shot to film or to composite. The presenter full length, next to a screen that shows the current slide; this shot alternates with the same slide full-bleed (4/8: v1, v2, v7, v8).

#### 2. Canonical layout (video)

| Zone | x | y | w | h | Where the value comes from |
|---|---|---|---|---|---|
| Screen: the current slide | 36 | 16 | 56 | 58 | estimated on 8 images: screen of 40 to 71 % W, top at 3–36 % H, bottom at 72–83 % H |
| Presenter, full length | 25 | 48 | 8 | 38 | estimated: 15 to 53 % H tall, next to the screen (center at 16–36 % W, or at 82 % W); feet at 73–95 % H |
| Floor | 0 | 86 | 100 | 14 | floor that reflects the slide (v1, v2, v7) |

```
+------------------------------------------------------------+
|                                                            |
|                                                            |
|                                                            |
|                      :::::::::::::::::::::::::::::::::     |
|                      :::::::::::::::::::::::::::::::::     |
|                      :::::::::::::::::::::::::::::::::     |
|                      ::::::::::::: SCREEN ::::::::::::     |
|                      :::::::: the current slide ::::::     |
|                      ::::::: x 36  w 56  h 58 ::::::::     |
|               ooooo  :::::::::::::::::::::::::::::::::     |
|               ooooo  :::::::::::::::::::::::::::::::::     |
|               o O o  :::::::::::::::::::::::::::::::::     |
|               ooooo  :::::::::::::::::::::::::::::::::     |
|               ooooo                                        |
|               ooooo                                        |
|____________________________________________________________|
|_____________________ reflective floor _____________________|
|____________________________________________________________|
+------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `hall-ecran`, `scene-mur` or `panneau-verre` are accepted, but the slide becomes the full-bleed photo of the scene, with a warning. These are shots to film, not slides.

**a. Hall and freestanding screen (`hall-ecran`)**: 3/8 (v1, v2, v7).
- A bright hall, a screen standing on the floor, the presenter next to it; ceiling and mirror floor visible; symmetrical shot.

**b. Stage and dark wall (`scene-mur`)**: 4/8 (v2, v4, v5, v6).
- A dark stage, a wall across the full width, the presenter at its foot; live, a row of spotlights above (v5, v6).

**c. Inset panel (`panneau-verre`)**: 1/8 (v8).
- A translucent slab with rounded corners, with no frame, floats next to the presenter in a real place and blurs the set behind it; it carries the slide; it slides in and out.

#### 4. Visual content

- **Type**: raw footage of the presenter; the current slide, exported as an image; the set.
- **Framing**: fixed, wide, symmetrical shot; the whole screen, from the front.
- **Treatment**: reflective floor (v1, v2, v7); panel: translucent white fill at 70–80 % (convention), blur of the set behind, soft shadow on the floor (v8).
- **Accent**: the one on the displayed slide, nothing else.

#### 5. Typography

That of the displayed slide, unchanged. The lower third (A21) appears the first time the speaker shows up, on the side opposite them (5/6 off-center framings, corpus analysis).

#### 6. Build and animation

- Cut from the full-bleed shot; the presenter often walks in (corpus analysis).
- The panel slides in and slides out of frame (v8).

#### 7. Visual brief and fallback

- **To ask for (video)**: raw footage at 3840 × 2160 (at least 1920 × 1080), 25 or 30 frames per second, fixed wide shot, presenter full length, on the side the slide leaves free. For a composited shot: the presenter filmed full length on a plain background (green or gray), soft light, and each slide exported as a 1920 × 1080 PNG.
- **Fallback**: with no footage, the slide full-bleed, in its own archetype. Never draw a person.

#### 8. Avoid

- A screen too small to read the slide (under 40 % W).
- The presenter in front of the text.
- A screen in strong perspective.
- A lower third set on the screen.

### A23 · Presenter inside the slide

#### 1. Role and moment

- The default talking shot. The wide shot gives the text; the medium shot gives the expression.
- Present in 6/8 (v5, v6, v1, v2, v7, v4); a variant in v8 (panel cut by the edge); absent from v3.
- **What to keep in a projected deck**: no separate slide. The slide behind the presenter must survive being cut: the keyword large enough to be recognized when half hidden (A1, 100 pt), and the visual kept in the top two thirds (convention).
- **What to keep in a video**: a medium shot of the presenter on one third; behind them, the slide enlarged 1.3 to 1.7 times and cut by the edge.

#### 2. Canonical layout (video)

| Zone | x | y | w | h | Where the value comes from |
|---|---|---|---|---|---|
| Presenter, medium shot | 58 | 10 | 32 | 90 | estimated on 8 images: right third (center at 67–74 % W: v2, v7), left third (27–33 % W: v4, v7, v8), or center when the word passes behind the head (50–57 % W: v1, v5); head at 1–22 % H; cut at the waist or the hips |
| Slide content behind | 4 | 4 | 62 | 26 | measured on 2 images (v2, v7): cap of 24.7 % H, center at 31–35 % W, in the top half |

```
+------------------------------------------------------------+
|............................................................|
|..######################################....................|
|..########### GIANT WORD, cut #####ooooooooooooooooooo......|
|..############# cap 25 % H ########ooooooooooooooooooo......|
|..#################################ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................oooo PRESENTER oooo......|
|...................................oo medium shot oooo......|
|...................................ooo center 74 % ooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
+------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `mot-coupe`, `contenu-lisible`, `interface-geante` or `slide-floue` are accepted, but the slide becomes the full-bleed photo of the scene, with a warning. These are shots to film, not slides.

**a. Cut word (`mot-coupe`)**: 3/8 (v1, v5, v7).
- The giant word of the slide runs past the frame or passes behind the head; only part of it can be read.

**b. Readable content (`contenu-lisible`)**: 2/8 (v2, v7).
- Half presenter, half content, whole and readable: a figure and its label, or an icon and its name.

**c. Giant interface (`interface-geante`)**: 3/8 (v2, v4, v8).
- A huge device screen, cut by the edge, on one side; the presenter on the other third.

**d. Blurred slide (`slide-floue`)**: 1/8 (v6).
- Behind the presenter, the slide is out of the focus zone: only shapes and colors remain.

#### 4. Visual content

- **Type**: raw footage of the presenter in a medium shot; the current slide, at high resolution.
- **Framing**: the presenter on a side third, looking at the camera; the slide fills the whole background and runs past the frame.
- **Treatment**: the real screen is filmed (its edge is sometimes visible, v7); in a composited shot, the slide is enlarged without blur (a, b, c) or heavily blurred (d).
- **Accent**: the one on the slide, nothing else.

#### 5. Typography

That of the slide, enlarged: the word or the figure reaches a cap of 25 % H (measured, 2 images). The lower third (A21), if there is one, goes on the side opposite the presenter.

#### 6. Build and animation

- Cut from the wide shot (corpus analysis). The background changes when the slide changes, with no camera move.

#### 7. Visual brief and fallback

- **To ask for (video)**: medium-shot footage at 3840 × 2160 (so it can be reframed), the presenter offset to one third, looking toward the camera. For a composited shot: the presenter cut out or on a plain background, and each slide as a 3840 × 2160 PNG, so it can be enlarged 1.7 times without blur.
- **Fallback**: the slide full-bleed. Never a drawn person.

#### 8. Avoid

- The presenter in the center, hiding the word.
- A word cut so much it can no longer be recognized (convention: at least 60 % of the word visible).
- A slide shrunk behind the presenter, instead of enlarged.
- Partial blur, which looks like a focus error.

### A24 · Set with no screen

#### 1. Role and moment

- The welcome, a handover, the framing of a section. The place replaces the slide and carries the subject.
- Present in 6/8: all the prerecorded ones (v1, v2, v7, v8, v3, v4); none live (0/2).
- **What to keep in a projected deck**: a moment with no slide. During the welcome or a handover, the screen stays on the block's background, empty, and the presenter alone carries the moment (convention, since live events have none). If the place says something about the subject, a photo of the place (A18 use) replaces it.
- **What to keep in a video**: film the presenter in a real place tied to the subject, in a wide shot then a medium shot.

#### 2. Canonical layout (video)

| Zone | x | y | w | h | Where the value comes from |
|---|---|---|---|---|---|
| Real set | 0 | 0 | 100 | 100 | observed: place bleeding off, often symmetrical |
| Presenter, full length, centered | 45 | 38 | 10 | 52 | estimated on 6 images (v2, v3, v8): center at 49–51 % W, height 39 to 61 % H, feet at 83–96 % H; 2 other images offset them to 36–40 % W (v7, v8) |

```
+------------------------------------------------------------+
|............................................................|
|................. REAL SET, symmetrical ....................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|...........................oooooo...........................|
|...........................oooooo...........................|
|...........................oooooo...........................|
|...........................oo O o...........................|
|...........................o full...........................|
|...........................length...........................|
|...........................oooooo...........................|
|...........................oooooo...........................|
|...........................oooooo...........................|
|............................................................|
|............................................................|
+------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `large-centre`, `taille-centre` or `decor-sujet` are accepted, but the slide becomes the full-bleed photo of the scene, with a warning. These are shots to film, not slides.

**a. Centered wide shot (`large-centre`)**: 5/8 (v2, v3, v4, v7, v8).
- The presenter full length in the center of an architecture, the vanishing lines converge on them (6 images out of 8); they often walk in.

**b. Centered medium shot (`taille-centre`)**: 4/8 seen (v1, v3, v4, v7); 5/8 with v8, where the analysis describes the medium shot that follows the wide shot.
- Framed at the waist, center at 42–56 % W, head at 3–15 % H (estimated); hands joined at rest (seen in v3, v4, v7, v8); the set stays readable behind.

**c. Set that shows the subject (`decor-sujet`)**: 3/8 (v1, v2, v4).
- The subject's object is in the frame (a car, a lab bench, a gym, a beach with passers-by); the presenter moves to one side to make room for it; the lower third goes on the other side.

#### 4. Visual content

- **Type**: raw footage in a real place tied to the subject (6/6 themed sets, corpus analysis).
- **Framing**: wide and symmetrical, then medium; the presenter in the center, except when the subject's object shares the frame (c).
- **Treatment**: natural light; the day can move from daytime to night over the keynote (2/6: v3, v4); active extras in the background (v4).
- **Accent**: none. The place carries the color.

#### 5. Typography

No text, except the lower third (A21) on first appearance, on the side opposite the presenter. Never for the host (0/8).

#### 6. Build and animation

- Walking entrance (6/6); two cameras, wide then medium (corpus analysis).
- Link between two sets through an aerial or drone shot (5/6), never through a hard cut (v1, v2, v7, v8).

#### 7. Visual brief and fallback

- **To ask for (video)**: raw footage at 3840 × 2160 in a place tied to the subject: a wide shot and a medium shot, or a single 4K shot reframed; natural light; presenter in the center, looking at the camera; clean sound (lavalier mic).
- **Fallback**: in a deck, the screen on the block's background, empty, or the block's title card (A1). In video, a photo of the place (A18) under the voice; failing that, the engine's fill and two halos. Never a drawn person.

#### 8. Avoid

- A set with no link to the subject, or a neutral office background.
- A presenter off-center for no reason in a wide shot.
- Any overlaid text other than the lower third, a lower third for the host.
- A hard cut between two sets.

### A25 · Hands-on demo

#### 1. Role and moment

- After a feature announcement, before the wrap-up sentence. The presenter shows that it works and comments in the first person.
- Present in 5/8 (v5, v6, v1, v7, v8). Product events replace it with acted vignettes (v3, v4).
- **What to keep in a projected deck**: in the room, the demo runs through the device's feed, large, in the generic frame (A10), while the presenter works at a table (v6) or stands next to it (v5). The deck keeps one slide before the demo (A10 with the same framing) and, as a backup, the same demo in screenshots in case the device fails (convention).
- **What to keep in a video**: alternate a wide shot of the presenter, hands in close-up and the full-bleed feed (corpus analysis).

#### 2. Canonical layout (video: hands on a plain background)

| Zone | x | y | w | h | Where the value comes from |
|---|---|---|---|---|---|
| Device held in hand | 34 | 10 | 28 | 80 | estimated on 5 images (v7, v8): device tilted 10 to 20°, center at 48–52 % W |
| Hands | 28 | 30 | 45 | 70 | estimated: one hand holds from below and runs off the frame at the bottom; the other touches the screen |
| Plain light-gray background | 0 | 0 | 100 | 100 | observed (v7, v8); black table live (v6) |

```
+------------------------------------------------------------+
|                                                            |
|  plain background                                          |
|                    :::::::::::::::::                       |
|                    :::::::::::::::::                       |
|                    :::::::::::::::::                       |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooo:::: DEVICE :::::ooooooo                |
|                 ooo::::: held ::::::ooooooo                |
|                 ooo:::: tilted :::::ooooooo                |
|                 ooo::: 10-20 deg :::ooooooo                |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooooooooooooooooooooooooooo                |
|                 ooooooooooooooooooooooooooo                |
+------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `table-flux`, `mains-fond-uni`, `epaule`, `table-haute` or `tend-appareil` are accepted, but the slide becomes the full-bleed photo of the scene, with a warning. These are shots to film, not slides.

**a. Table and feed on the wall (`table-flux`)**: 2/8 (v5, v6), live.
- The presenter at a black table (v6) or standing (v5), small, on the left third; the device feed over the full height of the wall, on the right, cut at the top.

**b. Hands on a plain background (`mains-fond-uni`)**: 3/8 (v6, v7, v8).
- One or two hands, the device tilted, real gestures, in front of a plain light gray (v7, v8) or seen from above on the black table (v6).

**c. Over the shoulder (`epaule`)**: 2/8 seen (v1, v6); 3/8 with v7, where the analysis describes this shot in the in-context demos.
- The blurred shoulder in the foreground, the screen large, tilted, cut by the edge.

**d. High table (`table-haute`)**: 2/8 (v7, v8).
- The presenter standing behind a round table, the computer or tablet set in front of them, in a medium-wide shot; the edit alternates with the full-bleed screenshot.

**e. The presenter holds out the device (`tend-appareil`)**: 1/8 (v1); v4 does it once with its flagship product (counted separately in the corpus analysis).
- The presenter, in a medium shot, holds the device toward the camera, at chest height; the screen is visible, small.

#### 4. Visual content

- **Type**: raw footage of the hands and the presenter; screen recording for the full-bleed feed.
- **Framing**: device tilted (b, c), never from the front as in A10; hands running off the frame at the bottom.
- **Treatment**: plain light-gray background (v7, v8) or black table (v6); soft light, with no reflection on the screen; the screen stays readable.
- **Accent**: the interface's own. The user's device, or a device with no distinctive marks.

#### 5. Typography

No added text: the text comes from the interface. Lower third (A21) on the first appearance of a new speaker.

#### 6. Build and animation

- Alternation of wide shot, hands and full-bleed feed, with hard cuts (corpus analysis).
- A long demo lasts 2 to 4 minutes (v7).

#### 7. Visual brief and fallback

- **To ask for**: the screen recording of the demo (MP4, native resolution, 60 frames per second if the interface animates); in video, footage of the hands on a plain gray background, at 3840 × 2160, soft light, and a wide shot of the presenter. The demo flow in 3 to 5 gestures.
- **Fallback**: A10 with the generic device and the schematic interface, one state per click. Never drawn hands.

#### 8. Avoid

- A demo with no full-bleed feed: the screen stays unreadable.
- Hands that hide the area being discussed.
- A busy background behind the hands, a reflection on the screen.
- A live demo with no backup screenshots.
- Real notifications or private data on screen.

## 7. Recap and conversion

The slides that close an announcement: the recap, the price, the date, the end. Then two designs outside the archetype catalog, which the engine also draws: the colorways lineup and the timeline. Images reviewed: 180.

### A14 · Bento

#### 1. Role and moment

- It closes a section, during the recap sentence (step 14 “Mini-recap”, `grammaire.md` §4.1). It presents nothing new: each tile recalls something already said.
- Present in **6/8** (v1, v2, v7, v8, v3, v4): all the prerecorded ones (6/6), no live one (0/2). Live, the recap goes through an icon grid (v6) or through the list of principles (v5).
- One per section: 5 grids in v1, 7 in v2, 7 in v3, 6 (plus 2) in v4, 7 in v7, 6 in v8.
- In a product block, it comes right before the price and availability (v2, v3, v4: 3/3). In a software block, it closes each platform (v1, v7, v8: 3/3).

#### 2. Canonical layout

A grid of 3 × 3 cells. The center cell is two to three times larger than the others. Each outer cell holds one tile, or two tiles side by side.

Measured:
- outer margin of 0.8 to 1.1 % W (v1, v3, v4, v7, v8); gutter of 0.6 to 1.25 % W;
- the same radius for every tile (`style-visuel.md` §5.1);
- center “name” tile: 39 % W × 31.4 % H, at (30.5; 34.3) (v7 and v8, identical to the pixel; 32 × 31 in v1);
- center “product” tile: 48.2 % W × 47.4 % H, at (25.9; 26.3) (one image from v3 and one from v4, identical to the pixel). It ranges from 39 to 48 % W and from 47 to 64 % H depending on the product's shape (39 × 47 in v2, 39 × 56 in v3, 39 × 64 in v4).

Values kept: margin 1.0 % W and 1.7 % H; gutter 0.9 % W, which is 1.6 % H (0.09 in both ways).

| Zone (“name” grid) | x | y | w | h | In inches |
|---|---|---|---|---|---|
| Columns | 1.0 · 30.5 · 70.4 | | 28.6 · 39.0 · 28.6 | | 0.10 · 3.05 · 7.04 in |
| Rows | | 1.7 · 34.3 · 67.3 | | 31.0 · 31.4 · 31.0 | 0.10 · 1.93 · 3.79 in |
| Center tile (name) | 30.5 | 34.3 | 39.0 | 31.4 | 3.9 × 1.77 in |

| Zone (“product” grid) | x | y | w | h | In inches |
|---|---|---|---|---|---|
| Columns | 1.0 · 25.9 · 75.0 | | 24.0 · 48.2 · 24.0 | | |
| Rows | | 1.7 · 26.3 · 75.3 | | 23.0 · 47.4 · 23.0 | |
| Center tile (product) | 25.9 | 26.3 | 48.2 | 47.4 | 4.82 × 2.67 in |

Inside a tile (shared rule, seen in the 6 keynotes with a bento): the visual takes the top, the label is centered in a band at the bottom (from 79 to 93 % of the tile height), inner margin of 6 % of the tile. The label is centered under the visual in most tiles of the 6/6 bentos; only a few tiles put the text next to the icon.

“Name” grid (8 tiles around the name):

```
+----------------------------------------------------------------+
| +----------------+ +----------------------+ +----------------+ |
| |                | |                      | |                | |
| |   screenshot   | |         icon         | |     photo      | |
| |                | |                      | |                | |
| |                | |                      | |                | |
| +----------------+ +----------------------+ +----------------+ |
| +----------------+ +----------------------+ +----------------+ |
| |                | |                      | |                | |
| |   screenshot   | |    NAME (accent)     | |      word      | |
| |                | |                      | |                | |
| |                | |                      | |                | |
| +----------------+ +----------------------+ +----------------+ |
| +----------------+ +----------------------+ +----------------+ |
| |                | |                      | |                | |
| |      icon      | |      screenshot      | |      icon      | |
| |                | |                      | |                | |
| |                | |                      | |                | |
| +----------------+ +----------------------+ +----------------+ |
+----------------------------------------------------------------+
```

“Product” grid (10 tiles around the product):

```
+----------------------------------------------------------------+
| +-------------+ +-------------++-------------+ +-------------+ |
| |    icon     | |   figure    ||  screenshot | |    photo    | |
| |             | |             ||             | |             | |
| +-------------+ +-------------++-------------+ +-------------+ |
|                                                                |
| +-------------+ +----------------------------+ +-------------+ |
| |             | |                            | |             | |
| |             | |                            | |             | |
| |  screenshot | |          PRODUCT           | |     word    | |
| |             | |                            | |             | |
| |             | |                            | |             | |
| |             | |                            | |             | |
| +-------------+ +----------------------------+ +-------------+ |
|                                                                |
| +-------------+ +-------------++-------------+ +-------------+ |
| |     word    | |   figure    ||    icon     | |    icon     | |
| |             | |             ||             | |             | |
| +-------------+ +-------------++-------------+ +-------------+ |
+----------------------------------------------------------------+
```

The “name” grid fits in 8 tiles. The “product” grid needs 10, or 8 if the two top tiles and the two bottom tiles are merged. The corpus shows from 8 to 19.

#### 3. Observed variants

**In the engine**: `slide.variante` = `nom-au-centre`, `produit-au-centre`, `tuiles-chiffres`, `mot-geant-et-produit`, `theme-et-matieres`, `grille-icones` or `fragments-logiciel` (variant g, below). With no variant: the original rendering, simpler than the variants. Fields of each variant: `deck-spec.md`, “Variants”.

**a. Name in the center (`nom-au-centre`)**: 3/8 (v1, v7, v8), the three prerecorded software events.
The platform name, in white, on the wide, low center tile. Around it: screenshots, icons, a photo, a word. No figure (0/3).

**b. Product in the center (`produit-au-centre`)**: 3/8 (v2, v3, v4), the three product events.
The center tile is taller and carries no text: the cut-out render of the product alone (4 center tiles out of 4 reviewed). Around it, 10 to 18 smaller tiles.

**c. Giant word crossed by the product (`mot-geant-et-produit`)**: 2/8 (v3, v4), the high-end model.
The center tile carries a giant three-letter word; the product passes in front of the bottom of the word and runs out the bottom of the tile. Dark background (2/2).

**d. Figure tiles (`tuiles-chiffres`)**: 3/8 (v2, v3, v4). With a haloed symbol: 1/8 (v2).
Some tiles carry a large figure, a small word above (“up to”) and a label below. In v2, up to 7 figure tiles and one tile where the product's symbol glows with a colored halo.

**e. Theme in words and materials (`theme-et-matieres`)**: 2/8 (v2, v4).
A cross-cutting recap (environment, health), not a product. The tiles mostly carry words and materials as backgrounds (circuit, pellets, close-up). The center tile pairs an image and a sentence.

**f. Icon grid (live recap) (`grille-icones`)**: 1/8 (v6).
No center tile: two or three rows of equal icons, one per new item, with no text. This is the recap of live keynotes, which have no bento (0/2).

**g. Software in fragments (`fragments-logiciel`)**: outside the corpus: 7 recap slides from developer sessions (WWDC 2023 to 2025: two platform recaps, five recaps of an interface framework), collected from a public gallery of recap slides; geometry measured to the pixel on 5 of them (`style-visuel.md` §3 A14), the rest noted by eye.
This is the recap of software: a platform, or a business tool sold as SaaS. There is no product to photograph; what is shown is the features.
- No 3 × 3 grid: from 5 to 16 tiles of very unequal sizes. The anchor tile carries the platform's name or logo, in the center or close to it.
- Each tile pairs a feature name (2 or 3 words) with a fragment of the interface: a window, a menu, a card, a setting, three lines of code. Never a whole screen shrunk down.
- The fragment most often runs out through one edge of the tile (a window cut on the right or at the bottom). Otherwise it floats whole: a small panel set on the tile.
- The name sits at the top left, above or next to the fragment; it is centered under the visual only in icon tiles.
- One use-photo tile at most: a person using the platform, title in white at the bottom left.
- A list tile in solid color, with four or five stacked words (the qualities of the language, for example), in one recap out of seven.
- The outer margins are two to three times wider than in keynote bentos.

What the skill keeps from it (skill convention, tested on a real case):
- **the tiles follow the demo.** Three zones from left to right, in the order the demo showed things: what the user sets up, what their customer does, what they get out of it. One tile per journey shown, nothing new.
- **the center tile is dark** on a light deck (`fond_sombre` fill) and in accent on a dark deck. It carries the light logo (`image`, optional), then the name or the demo loop in three words, one per line (“Set up. Sell. Get paid.”), and one sentence on the right at most (`texte`).
- **a `fragment` tile** is made of a name of 4 words at most, at the top left, a line of 5 words at most that places it, and a component isolated from its screen. The component is set at its interface size: 1 px of the export equals 1 px of a 1,920 px screen (`echelle` 0.5 for a 2x export). If it fits, or overflows by less than half, it is shown whole, shrunk if needed and set at the bottom. Beyond that, it keeps its size and runs out on the right and at the bottom. A tall component (a status column, a panel) goes to the right of the name. A 0.5 pt rule separates it from a tile of the same color. No shadow: the skill keeps the rule from §4.
- **a single accent tile**, the list tile (`liste`: a kicker, then 4 or 5 lines of 2 to 4 words), on a light deck. On a dark deck, the accent moves to the center tile.
- **one photo tile and one figure tile at most.** The photo shows the audience's trade. The figure has a source, as everywhere.
- from 6 to 11 tiles. Below 11, cells merge in pairs; there is never a hole.

**Not kept for the engine: the bento on the set's screen**: 3/8 (v1, v7, v8). The same grid shows again on the wall or on the panel, the presenter next to it or composited in front. That is a stage shot (A22), not a slide.

**Tile contents** (combined in every variant):

| Content | N/8 | Keynotes |
|---|---|---|
| Icon or pictogram + label | 6/8 | v1, v2, v7, v8, v3, v4 |
| Screenshot or device cut by the tile edge | 4/8 | v7, v8, v3, v4 |
| Use photo bleeding off inside the tile | 4/8 | v7, v8, v3, v4 |
| Single word in color | 4/8 | v2, v8, v3, v4 |
| Figure + label | 3/8 | v2, v3, v4 |
| Drawn gauge (full battery, duration inside) | 3/8 | v2, v3, v4 |
| Material or texture as tile background | 3/8 | v2, v3, v4 |
| Tile in solid color (instead of gray) | 3/8 | v2, v8, v4 |
| Row of colorways | 2/8 | v3, v4 |

#### 4. Visual content

- **Image types**: screenshots of the real interface, cut-out render of the product (center tile), app-format icons (rounded square), use photos, close-ups of materials, figures.
- **Framing**:
 - a device or a screenshot is cut by the top or side edge of its tile: it “comes out of the tile” (4/8: v7, v8, v3, v4);
 - a photo fills its tile, bleeding off, tile corners included (4/8);
 - the center product is whole and centered, over about 76 % of the width and 86 % of the height of its tile;
 - in variant c, the product cuts the bottom of the word and runs out the bottom of the tile (2/2).
- **Treatment**:
 - solid tiles, with no border or shadow, same radius (`style-visuel.md` §3 A14, 5 images; reviewed on 24 bentos);
 - on a light background, white tiles on a very light gray (5/8: v2, v7, v8, v3, v4); on a dark background, very dark gray tiles, around 11 to 12 % white (4/8: v1, v2, v3, v4);
 - translucent tiles on a blurred background: 1/8 (v7, one platform). Not kept: the skill keeps the solid fill;
 - halo: only around the chip symbol in v2 (1/8). No reflection;
 - the center product has no visible shadow (4 product tiles out of 4: v2, v3, v4); the skill allows a very soft contact shadow on a light background.
- **Accent**: the corpus colors the center “name” tile with a gradient (3/3) and gives each tile a color (3/8: v2, v3, v4). The skill keeps a single accent color: the accent fill of the center tile, the tile figures and the color words. The gradient stays reserved for the A5 figure (`style-visuel.md` §4.2).

#### 5. Typography

Measurements: `style-visuel.md` §3 A14. The bento is the only slide where text goes below 3 % H.

What changes by variant:
- **product in the center**: no text in the center tile (4/4). The name is said, or set in a “word” tile.
- **giant word**: the word is 62 to 106 pt (cap of 11 to 19 % H, measured on v3 and v4), in accent; 84 pt by default. It is only 2 to 5 letters long.
- **figure tile**: small word above in 11 pt regular, figure in 48 pt, label in 11 pt.
- **photo tile**: a title of 18 to 22 pt, in white, set at the bottom left on the photo (v8, v4).
- **word tile**: 22 to 26 pt, weight 600, centered, in accent (v2, v8, v4).

#### 6. Build and animation

- The center tile is there before the others (v1, v7, v4: 3/8); in v7, it can be seen fading in alone.
- The other tiles then arrive around it, from the center out to the edges: in v1, they appear in waves; in v4, they can be seen sliding into place, still translucent.
- Variant: the full grid is revealed by a zoom out from a tight crop (1/8: v2).
- Engine: the center tile on click, all the others in a single click after it, fading in with a 2 % slide toward their place, 0.4 s, staggered by 0.05 s (convention). Never one click per tile: the bento is watched during one sentence.

#### 7. Visual brief and fallback

One line per tile: “tile n: type, what it shows”. Then, by type:
- **product (center tile)**: cut-out render, PNG on a transparent background, front or three-quarter view, soft light, no baked-in shadow, at least 1,000 px tall (the product is about 440 px tall on a 1,920 × 1,080 slide; double it for sharpness).
- **screenshot**: PNG of the real screen, at least 1,200 px on the long side. It will be cut by the top of the tile: keep what matters in the bottom two thirds.
- **icon**: SVG, or a square transparent PNG of at least 512 px.
- **photo**: JPG at least 1,600 px wide, subject in the center; it will be cropped to the tile's shape.
- **material**: JPG of at least 1,200 px, with no text or logo.
- **figure**: the figure, its label and its source.
- **fragment** (variant g): a component isolated from its screen, never a full-page screenshot. It can be a card, a status column, a button, three rows of a table or a menu. Go into the mockup (in Figma, the frame, then the component's layer) and export it alone, as a PNG at 2x (`echelle: 0.5`) or at 1x, with the mockup's demo data. The Figma MCP server renders a node at 1x at most: at that size, show it at scale 1 or below, otherwise the text gets blurry. Keep the part that says the feature: the status column rather than the whole table. A frozen mockup is not retouched for the slide.
- **use photo** (variant g): a royalty-free stock library works, Unsplash or Pexels (§2, rule 7). On Unsplash, filter on “Free” and check on the photo's page that it is free to use. On Pexels, check “Free to use”. Note the author for the credits. The photo shows the audience's trade and market: the places, signage, objects and people of the target country. An audience does not recognize itself in another country's setting. No readable brand.

**Drawn fallback** (nothing is invented): the center “name” tile in accent fill with the name; the center “product” tile with a generic silhouette (rounded volume, no detail); screenshots as a light schematic interface cut by the tile edge (`style-visuel.md` §5.2); icons as a gray geometric pictogram (circle, rounded square, stroke); photos as a nearby fill with two neutral halos; materials as a slightly darker fill, with no pattern; figures as a faded marker. No number, no logo.

#### 8. Avoid

- A border, a shadow or a radius that differs from one tile to the next.
- A grid of cells that are all equal: that is a table, not a bento. The center tile must be two to three times the others.
- A tile that presents something not yet said.
- More than 4 words in a tile.
- A whole light screen set in the middle of a dark tile (`style-visuel.md` §5.2); a floating device, whole and small, in the middle of its tile.
- An empty tile or a gray “image expected” frame.
- A gradient background, or several accent colors.
- A partner logo or a number in the fallback.
- (variant g) A whole screen shrunk into a tile, unreadable: take a component.
- (variant g) A component enlarged beyond its export size: it gets blurry.
- (variant g) An impact or gains tile presented as a result when it is a promise: switch it to `[TO VALIDATE]`, or cite the measurement.
- (variant g) A photo from outside the audience's market, or one that shows a brand.

### A19 · Price

#### 1. Role and moment

- End of the product block, right before availability (step 15, `grammaire.md` §4.1).
- Present in **5/8** (v5, v6, v2, v3, v4). In software events: 1/4 (v6, pro hardware only).
- The name comes before the price: 5/5 keynotes with a price.
- A higher reference price sometimes comes first: 2/8 (v5, v6).
- Always on the block's background (v4: across its 8 or so price slides).
- For investors, `publics.md` advises against this slide (`slide_prix: non`).

#### 2. Canonical layout: “column”

The product on one side, the text stack on the other. 3/8 (v6, v3, v4).

| Zone | x | y | w | h | Measurement or rule |
|---|---|---|---|---|---|
| Product | 11 | 5 | 29 | 90 | object from 12 to 39 % W over 91 % H (`style-visuel.md`); v4: 4.7 to 90.8 % H |
| Name | 47 | 37 | 46 | 10 | centered at 70 % W (7.0 in) |
| “From” | 47 | 49 | 46 | 4.5 | set right above the price |
| Price | 47 | 53.5 | 46 | 9.5 | |
| Detail (excl. tax, period, capacity) | 47 | 63.5 | 46 | 4.5 | |

The text block is centered around 50 to 53 % H (v3 and v4, 2 images measured). The product can move to the right and the text to the left (1 case, v3).

```
+----------------------------------------------------------------+
|                                                                |
|       +-----------------+                                      |
|       |                 |                                      |
|       |                 |                                      |
|       |                 |                                      |
|       |                 |                                      |
|       |                 |                                      |
|       |                 |             Name (40 pt)             |
|       |     PRODUCT     |                                      |
|       |                 |              from (16 pt)            |
|       |                 |             PRICE (36 pt)            |
|       |                 |             detail (16 pt)           |
|       |                 |                                      |
|       |                 |                                      |
|       |                 |                                      |
|       |                 |                                      |
|       +-----------------+                                      |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `colonne`, `deux-offres`, `nom-en-haut`, `gamme-alignee`, `prix-heros` or `ancrage`. With no variant: the original rendering, simpler than the variants. Fields of each variant: `deck-spec.md`, “Variants”.

**a. Column (`colonne`)**: 3/8 (v6, v3, v4). The canonical layout.

**b. Two offers (`deux-offres`)**: 3/8 (v6, v3, v4).
Two stacks one above the other (v3, v4) or side by side (v6). The product shows both models, the large one behind. Measured on v4: first offer from 18 to 44 % H, second from 59 to 86 % H, centered at 70 % W.

**c. Name on top, product below (`nom-en-haut`)**: 1/8 (v2), on a light background.
The name at the top (caps between 12.5 and 20 % H), the price below, the whole product set from 50 to 87 % H over 55 % W.

**d. Aligned lineup (`gamme-alignee`)**: 1/8 (v3).
Four products side by side, from 14 to 65 % H. Under each, its name, then “from” and its price (72 to 86 % H). The prices all arrive together.

**e. Hero price (`prix-heros`)**: 1/8 (v5), for a service with no object.
The price treated as an A5 figure, the period below.

**f. Anchor (`ancrage`)**: 2/8 (v5, v6).
First a higher reference price (the total value in v5, the competing machine in v6), then the real price. In v5, five seconds separate the two; in v6, seven minutes.

**Not kept**: the colored rate badges (1/8: v5) and the discount with a condition (1/8: v4). They carry several numbers and conditions: one A5 slide per rate, with its source, works better.

#### 4. Visual content

- **Type**: cut-out render of the product, studio lighting, on the block's solid background. For a service, no object (variant e).
- **Framing**: the product is very large, from 86 to 91 % H (v3, v4). It often shows two overlapping views, back and front (2/8: v3, v4). It touches or crosses an edge in 2/8 (band cut at the top in v3, hand cut at the bottom in v4): this is allowed.
- **Treatment**: no visible shadow on black (v6, v3, v4: 3/3); on a light background, a very soft contact shadow at most (v2). No halo, no reflection.
- **Accent**: the price is in the text color in 4/5 keynotes with a price (v6, v2, v3, v4). Only v5 puts a price in color. The skill keeps the price in the text color (the kicker or the dot can carry the accent), except for the “hero price” variant, which follows the A5 figure.
- **Currency**: the symbol is superscript in 4/8 (v6, v2, v3, v4). The skill keeps the typographic norm of the deck's language, at the same size: in English the symbol goes before the number (“$89”); in French it goes after, with a non-breaking space (“89 € HT”).

#### 5. Typography

Sizes, weights and spacing: `style-visuel.md` §3 A19.

What changes:
- **aligned lineup**: name 20 pt, small word 11 pt, price 24 pt (cap of 3 to 3.6 % H, measured on v3).
- **hero price**: price at 144 pt (cap of 27 % H), period 18 pt regular, like A5.
- **anchor**: the reference price is at the same size as the real price, in secondary gray; the real price takes its place.

#### 6. Build and animation

- The product and the name first, then the price fades in, then the second offer (v4: three images 3 s apart; v3: price caught mid-fade).
- The price can change in place for a second offer (1/8: v2): Morph between two identical slides.
- The anchor plays out over two slides: the reference price, a silence, then the real price in the same place.

#### 7. Visual brief and fallback

- The cut-out render of the product (or of both models), PNG on a transparent background, front and back view if possible, same light for both, at least 2,000 px tall (the product takes 90 % of the height).
- The exact price, excluding or including tax, the period or the capacity, the word “from” if it applies.
- For the anchor: the reference price, what it covers, and its source.

**Drawn fallback**: a generic silhouette in place of the product (shaded volume, rule 6 of §3; no button, camera or logo), in the same zone; in the aligned lineup, all at the same scale on the same line; the price as a faded marker at the price size. Never a proposed price, never an invented reference price.

#### 8. Avoid

- The price before the name.
- More than two offers on the slide, except the aligned lineup of four.
- An asterisk, a struck-through price or a note under the price: the caveats go to the final card (7/7 keynotes with figures).
- A gradient on the price, or both price and name in accent.
- A comparison table of the offers.
- “From” larger than 0.45 times the name.
- A small product floating in the middle of a large empty space.

### A20 · Availability

#### 1. Role and moment

- The very last step of an announcement, right after the price when there is one (step 15). Present in **8/8**.
- In software events, the dates are grouped at the end of the keynote (4/4: v6, v1, v7, v8); in v8, in the last 30 seconds of speech.
- It comes before the handover back or the close.

#### 2. Canonical layout: “top and lineup”

The small label and the date at the top, the lineup below, set at the bottom. 6/8 (v1, v2, v3, v4, v7, v8).

| Zone | x | y | w | h | Measured |
|---|---|---|---|---|---|
| Label | 30 | 7 | 40 | 4.5 | top of the caps from 5.6 to 11.9 % H (v2, v3, v4, v8) |
| Date or word | 10 | 12.5 | 80 | 11 | caps from 12 to 28 % H, descenders included |
| Lineup | 4 | 30 | 92 | 59 | from 28-38 % H to 88-90 % H; 4 to 96 % W for a lineup, 20 to 80 % W for three objects |

The same positions in inches: `style-visuel.md` §3 A20.

```
+----------------------------------------------------------------+
|                                                                |
|                         label (16 pt)                          |
|                                                                |
|                          DATE (40 pt)                          |
|                                                                |
|   +--------------------------------------------------------+   |
|   |                                                        |   |
|   |                                                        |   |
|   |                                                        |   |
|   |                                                        |   |
|   |              LINEUP set at the bottom                  |   |
|   |                                                        |   |
|   |                                                        |   |
|   |                                                        |   |
|   |                                                        |   |
|   +--------------------------------------------------------+   |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `slide.variante` = `haut-et-gamme`, `suite-de-dates`, `colonne`, `date-et-lieux` or `mot-seul`. With no variant: the original rendering, simpler than the variants. Fields of each variant: `deck-spec.md`, “Variants”.

**a. Top and lineup (`haut-et-gamme`)**: 6/8 (v1, v2, v3, v4, v7, v8). The canonical layout.

**b. Column (`colonne`)**: 5/8 (v5, v6, v3, v4, v7).
The same frame as the price slide: the product on the left (from 5 to 58 % W depending on the object), the date on the right, centered around 73-74 % W; label from 39 to 42 % H, date from 46 to 54 % H (v3, v4).

**c. Series of dates on the same image (`suite-de-dates`)**: 7/8 (v1, v2, v3, v4, v6, v7, v8).
The visual does not move; the label and the date change in place, two or three times in about ten seconds (11 s in v7). It is a sequence of a or b.

**d. Date and places (`date-et-lieux`)**: 3/8 (v1, v5, v7) for availability by country; as a list of names: 1/8 (v7).
The product on the left; on the right, the date then the list of countries, one per line. v1 and v5 show round flags: not kept (no flags are drawn).

**e. Single word (`mot-seul`)**: skill convention for a slide with no visual. The closest observed: the date alone on a full-bleed image (1/8: v2). A single close image, no second example.

**Not kept**: the label in accent caps (1/8: v5) and the text tilted in perspective on the stage wall (1/8: v6).

#### 4. Visual content

- **Type**: the lineup of the devices or products concerned, from the front, each with its screen on; or the product alone, taken from the price slide (variant b).
- **Framing**: the lineup is aligned along the bottom, at the objects' real scale relative to one another, the small ones in front of the large ones (4/8: v1, v2, v7, v8). It takes almost the full width.
- **Treatment**: the same image on every screen of the lineup (v2, v8: 2/8). No visible shadow on black; on light, a very soft contact shadow at most. The iridescent light background of v8 (1/8) is not reused: solid background.
- **Accent**: none in 7/8. The label is gray, the date in the text color. Only v5 puts the label in color.

#### 5. Typography

Measurements, version with no visual included: `style-visuel.md` §3 A20.

What changes:
- **column**: same sizes; block centered around 46 % H and 73 % W (7.3 in).
- **date and places**: the list in 18 pt, centered, line spacing k = 1.8, 3 to 6 places.

#### 6. Build and animation

- The lineup and the label, then the date when it is said.
- Then the date changes on the same image (7/8): Morph between two slides with the same layout, or a fade. The lineup does not move.
- The label can change along with the date (v2, v3, v4: from preorder to availability).

#### 7. Visual brief and fallback

- One cut-out PNG per product, all from the front, same light, screens on with the same image, at least 1,500 px tall for the largest; give the real size of each to respect the scale. Or a visual already composed, transparent PNG of at least 3,600 × 1,500 px.
- The exact date (day or month), the label (available, preorder, beta…), and the places if any.

**Drawn fallback**: three or four generic silhouettes of different sizes (wide screen, tablet, phone, box), aligned at the bottom, each with a light schematic interface; no logo, no flag. The date as a faded marker at the date size.

#### 8. Avoid

- A relative date on screen (“in two weeks”): write it out and say it in relative terms (4/8).
- A whole sentence; more than four words in all.
- Two dates on the same image: make a series of dates.
- A label larger than 0.46 times the date.
- Products at wrong scales, or a recognizable device in the fallback.
- Drawn flags, or text tilted in perspective.

### FIN · Final slide

In a deck, it is the last slide: `"archetype": "FIN"`, or an A1 with one of the variants below. It turns into a full accent page only in A1 or FIN, with no variant or with `aplat` or `mot-final`, and if `theme.finale_accent` is not `false`.

#### 1. Role and moment

- The last screen, after the host's thanks. The final card exists in **8/8**: it also carries all the legal text and, depending on the audience, the sources (`publics.md`).
- Right before it, the host gives an overall recap: the agenda shown again (2/8: v7, v8), the whole lineup on screen (2/8: v4, v6), a group photo (1/8: v5).
- It stays up a long time: up to two minutes of still logo at the end of the video (v2).

#### 2. Canonical layout: “sign alone”

A single sign, centered, and the legal notes very small at the bottom. 6/8 (v1, v2, v3, v4, v7, v8).

| Zone | x | y | w | h | Measured |
|---|---|---|---|---|---|
| Sign (logo) | 40 | 34 | 20 | 27.5 | from 34.2 to 61.1 % H, center at 47.7 % H, 12 % W wide (v2, v3, v4, v8, within 1 %) |
| Notes | 10 | 86 | 80 | 8 | at the bottom in 7/8 (v1 puts them on a separate card); cap of 1.4 to 1.9 % H, from 76 to 94 % H depending on length, 80 % W at most |

The same positions in inches: `style-visuel.md` §3, final slide.

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                          +----------+                          |
|                          |          |                          |
|                          |   SIGN   |                          |
|                          |          |                          |
|                          +----------+                          |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                          notes (9 pt)                          |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `"archetype": "FIN"`, or the variant set on any archetype (often A1). `slide.variante` = `signe-seul`, `signe-et-ligne`, `signe-et-evenement`, `signe-sur-photo` or `mot-final`; with no variant, `signe-seul`. Fields of each variant: `deck-spec.md`, “Variants”.

**a. Sign alone (`signe-seul`)**: 6/8 (v1, v2, v3, v4, v7, v8). The canonical layout.

**b. Sign and one line (`signe-et-ligne`)**: 3/8 (v3, v7, v8).
A short sentence under the sign, about how the event was made (cap of 3 to 4 % H, baseline around 89 to 93 % H). The notes come on the next card.

**c. Sign, event name and place (`signe-et-evenement`)**: 3/8 (v2, v5, v6).
Two lines under the sign: the event name in semibold (between 67 and 82 % H depending on the keynote; 70 to 75 % H in v2), the place in gray right below, then the notes. v5 lights the sign with a beam from above (1/8); v6 replaces the sign with the event's illustration (1/8).

**d. Sign on a calm photo (`signe-sur-photo`)**: 1/8 (v7).
The sign and the line in white on a full-bleed sky photo.

**e. Final word (`mot-final`)**: skill convention, not observed as a text-only card (0/8). One word at A1 size, final period in accent; it can turn into a full accent page (convention, `style-visuel.md` §3, final slide). No example image: it is a convention.

#### 4. Visual content

- **Type**: the user's logo, monochrome, with no effect. White on black in 7/8; white on sky in v7.
- **Framing**: centered, whole, small (12 % W), with a lot of empty space around it.
- **Treatment**: once set, the sign is sharp and with no effect in 7/8; only v5 lights it with a beam from above. A blur or a glow is seen only as it arrives (v1, v3). The skill applies no effect.
- **Accent**: none on the logo. For a final word, the accent goes only on the final period.

#### 5. Typography

Measurements: `style-visuel.md` §3, final slide.

What changes:
- **sign and line**: line in 22 pt (cap of 3 to 4 % H, measured on v3 and v7); optional sub-line in 9 pt.
- **sign and event**: name in 24 pt, weight 600 (cap of 3.6 to 5 % H, v2, v5, v6); place in 16 pt regular secondary (cap of 2.2 to 3 % H).

#### 6. Build and animation

- The sign comes in alone, fading in (v3), or arrives large and blurred then settles (1/8: v1).
- The line or the notes come after the sign, on a second identical card, in 4/8 (v1, v3, v7, v8).
- Nothing loops. In the room, the slide stays up during the applause or the questions.

#### 7. Visual brief and fallback

- The logo as SVG, or as a transparent PNG of at least 1,000 px tall, in light and dark monochrome versions.
- The final line, if the user wants one; the event name, place and date for variant c.
- The legal notes and the sources for the card.
- For variant d: a 16:9 photo of at least 1,920 × 1,080 px, with no sharp subject, with calm in the center.

**Drawn fallback**: with no logo, the “final word” variant (one very large word, final period in accent). Never a drawn logo or an invented monogram. With no photo, the solid background.

#### 8. Avoid

- “Any questions?”, an address, a paragraph.
- A color logo on a colored background; a logo taller than 30 % H.
- Notes above 12 pt, or in full white.
- Several logos (partners) on the final slide.
- A sentence about how the event was made that cannot be backed up.
- A background that changes just for the final slide, except the full accent page the skill plans for.

### COLORIS · Colorways lineup

In a deck, the lineup goes through `"variante": "rangee-alignee"` (or another variant below) on the product slide, often an A13. The colorways tile of the bento (variant f) goes in A14, with a `"type": "coloris"` tile.

#### 1. Role and moment

- In a product block, after the pillars and before the recap: “pillars, colorways and accessories, recap, price, dates” (corpus analysis, product variant).
- Present in **3/8** (v6, v3, v4). In product events: 2/3 (v3, v4; not in v2). In v1, a row of watches with colored bands goes with a recap of watch faces: variant (x), not counted.
- The colorway names are said, never written: no label on the colorway shots reviewed (3/3 keynotes).
- The lineup comes back small in a bento tile (2/8: v3, v4).

#### 2. Canonical layout: “aligned row”

From two to five products side by side, one per colorway, same angle, same scale, whole, centered.

| Zone | x | y | w | h | Measured |
|---|---|---|---|---|---|
| Row (4 colorways) | 5 → 95 | 18 | 4 × 20.5, gap 2.5 | 62 | v3: 3-98 % W × 21-79 % H; v4: 11-88 % W × 14-85 % H and 17-84 % W × 20-80 % H |

Maximum observed: 5 colorways in a row (v3, 2 times). No constant order of colors (0/5 rows).

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|   +-----------+  +-----------+  +-----------+  +-----------+   |
|   |           |  |           |  |           |  |           |   |
|   |           |  |           |  |           |  |           |   |
|   |           |  |           |  |           |  |           |   |
|   |           |  |           |  |           |  |           |   |
|   | colorway 1|  | colorway 2|  | colorway 3|  | colorway 4|   |
|   |           |  |           |  |           |  |           |   |
|   |           |  |           |  |           |  |           |   |
|   |           |  |           |  |           |  |           |   |
|   |           |  |           |  |           |  |           |   |
|   +-----------+  +-----------+  +-----------+  +-----------+   |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `"archetype": "COLORIS"`, or the variant set on any archetype (often A13). `slide.variante` = `rangee-alignee`, `rangee-chevauchee`, `eventail`, `un-par-un` or `mur`; with no variant, `rangee-alignee`. Fields of each variant: `deck-spec.md`, “Variants”.

**a. Aligned row (`rangee-alignee`)**: 2/8 (v3, v4). The canonical layout, on a light or dark background.

**b. Staggered row, cut by the frame (`rangee-chevauchee`)**: 1/8 (v3).
The products overlap, each in front of the previous one, and run out the bottom of the frame (or out the top and bottom, seen from the side). Dark background.

**c. Fan (`eventail`)**: 1/8 (v3).
One product lying flat in front; the other colorways pivot behind it around a shared end. Light background.

**d. One by one, same frame (`un-par-un`)**: 1/8 (v4).
The product stays in the same place; only its color changes, from one image to the next. Close variant: one close-up per colorway, in successive shots.

**e. Colorway wall (`mur`)**: 1/8 (v6).
Dozens of products in a staggered grid, overflowing the frame on every side. To say “there are lots of them”.

**f. Colorways tile in the bento**: 2/8 (v3, v4). Three or four products in a row inside a tile, a label below. See A14.

#### 4. Visual content

- **Type**: identical cut-out renders, one per colorway, same light.
- **Framing**: whole and centered (a, c, d); cut by the frame (b, e). Same angle for all (5 rows out of 5).
- **Treatment**: solid background, light (v3, v4) or dark (v6, v3, v4). No visible shadow on black; on light, a very soft contact shadow at most. In d, a soft light from above lights the product (very soft halo on the background).
- **Accent**: none. The colorways are the slide's color; none is added (0 accent seen on the colorway shots).

#### 5. Typography

No text (3/3 keynotes). Option, by convention: the name of each colorway in 16 pt regular secondary, centered under its product around 86 % H, when the audience watches with no sound (trade show, silent video). No kicker.

#### 6. Build and animation

- Row: in one fade, while the colorways are named.
- Staggered: the products slide in one by one from the bottom.
- Fan: the front product, then the fan opens behind it.
- One by one: one slide per colorway, with Morph, at the pace each color is named.

#### 7. Visual brief and fallback

- One PNG on a transparent background per colorway, all at the same angle, with the same framing and on a canvas of the same size (so they line up), at least 2,000 px tall.
- The list of colorways: name and HEX of each.
- For the fan, a back or side view; for variant d, one close-up per colorway (JPG at least 1,920 px wide).

**Drawn fallback**: identical generic silhouettes, filled with the colorway HEX values supplied by the user and shaded by the same light (lighter top, darker bottom, light edge), so they read as objects and not as swatches. With no HEX, steps of gray taken from the background, and the image becomes “Image to provide”: no color is invented. No text, no number.

#### 8. Avoid

- Color dots in place of the product (a swatch card is not a product).
- Colorway names written large.
- Different angles, scales or lights from one colorway to the next.
- Products floating with no shared baseline.
- More than five colorways in a row: beyond that, a wall.
- A colorway color that the user has not validated.

### FRISE · Timeline or chronology

In a deck, the timeline goes through `"variante": "rangee-datee"` (or another variant below), often on an A6 at the anchor step.

#### 1. Role and moment

- At step 2 “Anchor”, to recall the heritage (`grammaire.md` §4.1, Visual column: “timeline; old product alone”).
- On a slide: **3/8** (v1, v2, v7), always for an in-house technology (the chip, 3/3). Alongside: an object from the past shown alone, 2/8 (v1, v8, variant e); a film of generations in successive shots, (x) v4.
- It sets up a proof: the v1 timeline closes in on the last milestone, then gives way to a hero figure; the v2 one ends on the measured gap; the three milestones of v1 lead to a thesis sentence.

#### 2. Canonical layout: “row of milestones”

From 5 to 10 equal square tiles, in a line across the full width, the date under each. 2/8 share this structure (v1 with dates, v7 with no dates).

| Zone | x | y | w | h | Measured |
|---|---|---|---|---|---|
| Row of 6 milestones | 4 → 96 | 30 | 13 each, gap 2.8 | 23 | v1: 10 tiles from 2 to 96 % W, from 41 to 51 % H; v7: 5 tiles from 4.7 to 95 % W, from 35 to 65 % H |
| Dates | under each tile | 57 | 13 | 5 | v1: from 58 to 61 % H (cap of 2.7 % H) |
| Current milestone | the last one, on the right | | | | alone in accent (convention) |

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|   +------+  +------+  +------+  +------+  +------+  +------+   |
|   |      |  |      |  |      |  |      |  |      |  |      |   |
|   |milest|  |milest|  |milest|  |milest|  |milest|  | now  |   |
|   |      |  |      |  |      |  |      |  |      |  |      |   |
|   +------+  +------+  +------+  +------+  +------+  +------+   |
|     date      date      date      date      date      date     |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Observed variants

**In the engine**: `"archetype": "FRISE"`, or the variant set on any archetype (often A6). `slide.variante` = `rangee-datee`, `generations`, `trois-jalons`, `courbe-et-saut` or `objet-du-passe`; with no variant, `rangee-datee`. Fields of each variant: `deck-spec.md`, “Variants”.

**a. Dated row (`rangee-datee`)**: 1/8 (v1). Ten equal tiles, a date under each.

**b. Generations with no dates (`generations`)**: 1/8 (v7). Five larger square tiles, the name inside each tile; the tiles go from an image (the chip layout) to their name.

**c. Three milestones as objects (`trois-jalons`)**: 1/8 (v1). Three historical objects side by side (from 28 to 72 % H, from 8 to 92 % W), with no dates, arriving one by one.

**d. Flat line, then the jump (`courbe-et-saut`)**: 1/8 (v2). A title at the top, a time axis with a date at each end (86 to 89 % H), dots on an almost flat line, then the new item jumping above it with an arrow and the gap in accent. No tick marks.

**e. One object from the past, alone (`objet-du-passe`)**: 2/8 (v1, v8). The old product or the old screen, small, centered, with no text, right before the present.

**Not kept: the film of generations**: (x) v4. One shot per generation, in macro. That is a film, not a slide.

#### 4. Visual content

- **Type**: solid tiles carrying the name or the pictogram of each milestone (a, b); cut-out historical objects (c, e); drawn line and dots (d).
- **Framing**: the timeline takes the full width, on a single line (3/3). No vertical timeline (0/8).
- **Treatment**: tiles with no border or shadow, in very dark gray on black (v1) or in black on light gray (v7). The new milestone stands out in 2/3: accent halo and jump (v2), the only one left on screen (v1).
- **Accent**: only on the current milestone (and the gap, if it is written).

#### 5. Typography

- Dates: 16 pt regular secondary (cap of 2.7 to 2.8 % H, measured on v1 and v2).
- Name inside a tile: 28 pt, weight 600 (cap of about 5 % H, v7).
- Title of variant d: 28 pt, weight 600, like the title of an A6 chart.
- Gap in variant d: 48 pt in accent, a single value, with a source.

#### 6. Build and animation

- From left to right: one object per click (v1), or the line drawing itself and the dots landing on it (v2).
- The new item arrives last, above or apart (v2).
- The tiles can go from the image to the name (Morph, v7).
- The timeline can close in on the last milestone, which opens the next slide (v1).

#### 7. Visual brief and fallback

- The ordered list of milestones: name and date of each.
- One image or pictogram per milestone, all in the same style: transparent PNG of at least 800 px.
- The measured gap, if there is one, with its source.
- For variant e: a cut-out photo of the old product, or a screenshot of the old screen.

**Drawn fallback**: solid tiles with a gray geometric pictogram, the last one in accent; dates as faded markers; gray line and dots for variant d. No date, no value proposed.

#### 8. Avoid

- A graduated axis with values.
- More than 10 milestones, or milestones of unequal sizes.
- More than one word or one date under a milestone.
- Decorative arrows between milestones.
- A competitor's chronology.
- A date invented to fill a gap.
