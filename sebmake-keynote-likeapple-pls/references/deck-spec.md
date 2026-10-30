# The deck.json file

The skill first writes a `deck.json` file. Everything else comes out of it: the .pptx, the HTML preview and the check. Never fix the content by editing the .pptx by hand. Fix `deck.json`, then render again.

- One JSON file, in UTF-8, stored in the presentation's working folder.
- Image paths are relative to this file (`images/ecran.png`).
- The output is always 16:9 (10 × 5.625 inches, `LAYOUT_16x9`).

**Contents.** Commands · Overall structure · meta · theme · intervenants · slides (`textes` fields by archetype, variants, rich text, sizes) · Markers: what the skill proposes, what it asks for · notes: the spoken script · Builds and transitions · Audience, sources and devices · Images · Visuals to prepare: `slide.visuel` · What check_deck.py checks · Full example.

The look of the slides (sizes, weights, kicker, hero figure, placeholders) is described in `style-visuel.md`, and the design of each archetype (variants, visual content, depth, brief) in `designs.md`. This file only covers the fields that drive them.

## Commands

```bash
# from the working folder; $SKILL = the skill's folder
[ -d "$SKILL/scripts/node_modules/pptxgenjs" ] || (cd "$SKILL/scripts" && npm install)   # pptxgenjs 4.0.1, once
python3 "$SKILL/scripts/check_deck.py" deck.json                 # check (exit code 1 = blocking error)
python3 "$SKILL/scripts/check_deck.py" deck.json --brouillon     # draft mode while writing: [TO PROVIDE] allowed
node "$SKILL/scripts/build_deck.js" deck.json sortie.pptx --preview apercu.html
node "$SKILL/scripts/export_script.js" deck.json --md script.md  # script; --visuels v.md: visuals to prepare;
                                                                 # --etapes: builds; --srt f.srt: subtitles
```

`build_deck.js` also accepts `--polices auto|repli`. With `auto` (the default), the .pptx always names the theme font (its exact name), whether or not it is installed on the machine that builds the deck: the deck will be presented on the user's machine. If the font is missing here, the preview uses the fallback font, the overflow check measures with the wider of the two, and the console says so in one line. `repli` writes the fallback font into the .pptx.

Open `apercu.html#qa` in a browser to outline in red any text that overflows its box. The same check is available in JavaScript with `window.__deckQA()`.

What the user receives for each `meta.format`: see `SKILL.md` (Step 6) and `formats/<format>.md`.

## Overall structure

```json
{
  "meta": { },
  "theme": { },
  "intervenants": [ ],
  "slides": [ ]
}
```

## meta

| Field | Required | Values | Role |
|---|---|---|---|
| `titre` | recommended | text | Title of the file and of the preview. |
| `langue` | yes | `fr` or `en` | Language of the slides and the script. It picks the FR or EN templates, the typography and the note labels. |
| `registre` | yes in French | `tu` or `vous` | Register toward the audience (French only). Always asked of the user. |
| `registre_intervenants` | recommended in French (several speakers) | `tu` or `vous` | Register between speakers, asked at the same time. The check applies it to `relais` (handover) segments. |
| `public` | yes | text, or `{ "type": "...", "description": "..." }` | Audience type, asked of the user (question in `references/publics.md`). `type` is a key of `references/data/publics-exigences.json` or one of its synonyms. For a mixed audience, `type` is a list (`["b2b-decideurs", "investisseurs"]`). It decides which devices are kept (see below). |
| `duree_min` | yes | number | Target length in minutes. The sum of `duree_s` must stay within ±15 % of this target. |
| `format` | yes | `keynote`, `powerpoint`, `canva`, `figma-slides`, `video` | Format asked of the user. |
| `ratio` | no | `16:9` | Always 16:9. Any other value is an error. |
| `contexte` | no | `direct` or `preenregistre` | Live (in the room or by video call) or prerecorded. Used to choose the flow. The renderer does not use it. |
| `variante` | no | `produit`, `fonctionnalite`, `service`, `technologie` | Variant of the announcement sequence (`grammaire.md` §4.3). The renderer does not use it. |
| `affichage_source` | no | `sous_le_chiffre`, `renvoi`, `carton_final`, `aucun` | Overrides the choice made by the audience. |
| `carton_sources` | no | `true` (default) or `false` | In `renvoi` or `carton_final` mode, adds a final “Sources and notes” slide. |

In English (`"langue": "en"`), leave out `registre` and `registre_intervenants`. The casual or formal tone is set in the handover phrases.

## theme

The skill does not know the user's branding. It asks for a link to their design system, or for their colors in HEX and their fonts. It then copies the values here.

```json
"theme": {
  "nom": "Clairval",
  "design_system": "https://… (optional: where the values come from)",
  "couleurs": {
    "fond_sombre": "#0F1B2A",
    "fond_clair": "#F5F7F9",
    "texte": "#14202E",
    "texte_secondaire": "#5B6776",
    "accent": "#1C9461",
    "accent2": "#E8A33D"
  },
  "polices": {
    "titre": { "nom": "Inter", "repli": "Arial" },
    "texte": { "nom": "Inter", "repli": "Arial" }
  },
  "point_accent": true,
  "finale_accent": true,
  "logo": "images/logo.png"
}
```

| Role | Required | Use |
|---|---|---|
| `fond_sombre` | yes | Background of `"fond": "sombre"` and `"image"` slides. |
| `fond_clair` | yes | Background of `"fond": "clair"` slides. Also used as the text color on a dark background if the contrast is high enough (7:1); otherwise white is used. |
| `texte` | yes | Text on a light background. |
| `texte_secondaire` | recommended | Gray labels on a light background. Computed when missing. |
| `accent` | yes | Kickers, giant figures, the highlighted bar, check marks, the bento center tile, `*accent*` words, the final period of titles, the underline of `[TO PROVIDE]` markers. |
| `accent2` | no | End of the hero figure gradient: the giant figure (A5) goes from `accent` to `accent2`. Without `accent2`, the figure is a flat `accent`. It is also the second color of the PowerPoint theme. Pick a shade close to the accent from the user's palette, never a color they have not seen. |
| `texte_sur_sombre` | no | Overrides the computed text color on a dark background. |
| `texte_secondaire_sur_sombre` | no | Overrides the computed gray on a dark background. |

- HEX values can be written with or without `#`, with 3 or 6 digits. The engine strips the `#`, which the .pptx rejects.
- The colors are also written into the file's theme (the PowerPoint and Keynote palette). The title and body fonts become the theme fonts.
- A font can be written as plain text (`"texte": "Arial"`). Arial is then the fallback.
- `point_accent` (`true` by default): the final period of a title (and a `!` or `?`) takes the accent color, as a quiet signature. `false` leaves it in the text color. A title with no final punctuation gets none.
- `finale_accent` (`true` by default): a final A1 slide (one word, in last position) becomes a full accent-color page, if its text reads at 4.5:1 on it. Set `false` when the brand guidelines cap the accent area (for example a yellow limited to 10 % of the surface): the final slide then keeps its `fond` (`sombre` or `clair`), with the final period in accent. A `"fond": "accent"` written on the slide still works.
- The logo is optional. It appears at the bottom right of slides with `"logo": true`, and in the center of archetype A2 when the slide has no image.
- Forbidden: any Apple font, logo or brand image. “Apple-style” means the grammar, not the identity.

## intervenants

```json
"intervenants": [
  { "id": "claire", "nom": "Claire Duval", "role": "Chief Executive Officer" },
  { "id": "hugo", "nom": "Hugo Bernard", "role": "Head of Product" }
]
```

At least one speaker is required. The first one is the default speaker. Whoever opens the presentation closes it.

`role` is optional. If it is unknown, leave it empty: the engine writes the name alone at the top of each speaking turn. Never put a marker in it, since it would be repeated at every handover. Ask for the role once, in the delivery list.

## slides

| Field | Required | Role |
|---|---|---|
| `id` | yes | Unique identifier (`s05-nom`). |
| `bloc` | recommended | Name of the block in the run of show (`Opening`, `Clairval Direct`, `Close`). It becomes a section in PowerPoint. |
| `etape` | no | Step number in the announcement sequence (1 to 16, see `data/annonce.json`), or `null` outside the sequence. A working reference: it is shown neither on screen nor in the notes. |
| `archetype` | yes | `A1` to `A25` (see `data/archetypes.json`), `FIN`, `COLORIS`, `FRISE` (designs outside the catalog, see “Variants”), or `AF` (avoid, see the table). A working reference, never shown either. |
| `variante` | recommended | The archetype's layout, among those the engine draws (“Variants” below; the design of each is in `designs.md`). When missing: the archetype's original, simpler rendering (see “Variants”). A working reference, never shown. |
| `fond` | yes | `sombre` (dark), `clair` (light), `image` or `accent` (full accent-color page, reserved for the final slide or a single strong moment). Keep the same background from start to finish (the opening one, often `sombre`). A `sombre` ↔ `clair` change only happens between two blocks. |
| `intervenant` | recommended | `id` of the speaker who talks by default on this slide. |
| `textes` | depends on the archetype | On-screen text (table below). |
| `image` | depends on the archetype | `"chemin.png"` or `{ "chemin": "...", "attendu": "what the image must show", "ajustement": "contenir" \| "couvrir" }`. While the file is missing, the engine draws a placeholder (see Images). |
| `images` | depends on the variant | A list of images (strings or objects like `image`), for variants with several visuals: A2 and A10 `rangee`, A13 `coloris`, A18 `diptyque`, A8 `picto-par-ligne`. |
| `image_fond` | no | Background image of a `"fond": "image"` slide whose `image` is already the content. With a variant, it is the only source of the background image. |
| `appareil` | no | `telephone`, `tablette`, `portable` or `boitier`: the generic device (phone, tablet, laptop, box) that holds a screenshot. When missing: inferred from `image.attendu`. |
| `logo_invite`, `logo_systeme`, `logo_final` | no | The logo of the guest organization (A21 cards), of the system (A11), of the final slide (FIN; otherwise `image`, then `theme.logo`). |
| `profondeur` | no | `false` removes the contact shadow (light background) and the glow (dark background) that the engine places under a product or a device. |
| `visuel` | recommended whenever the slide expects an image | The brief for the visual to prepare: `{ "type", "brief", "fond_transparent", "angle", "resolution_min" }`, or a list of these objects. Never shown. `export_script.js --visuels` turns it into the list to deliver (see Visuals to prepare). |
| `voile` | no | Opacity of the black overlay on a background image, from 0 to 100 (45 by default). |
| `source` | if there is a figure | Source or conditions of a figure. Shown depending on the audience. |
| `a_fournir` | no | Text or list: the full instruction for what is missing on the slide (what, in what form, who can provide it). Never on screen. Written in the notes and in `script.md`, and listed by the check. See Markers. |
| `notes` | yes | The spoken script (see below). |
| `duree_s` | yes | Length of the slide in seconds. |
| `build` | recommended | The builds, one sentence per click. The engine turns them into the .pptx entrance animations, and the list stays in the notes for the presenter (see Builds and transitions). |
| `logo` | no | `true` to show the theme logo. |

### `textes` fields by archetype

The archetypes come from `references/data/archetypes.json`. The engine renders them with the theme colors and fonts.

**`surtitre` (kicker), in every text archetype.** One to three small words above the title or the figure: “New”, “Pilot”, “Our commitment”. It takes the accent color, in semibold, when the slide's accent is free. If the slide already carries its accent (a `*word*`, the hero figure, your own bar, the check marks, the active line), it turns gray, in regular: one accent color per slide. It names the moment without repeating it. It counts toward the 10 on-screen words. No more than one kicker per slide, and not on every slide: it loses its strength if it comes back everywhere.

| Archetype | Fields | Rendering |
|---|---|---|
| A1 Title card | `titre` (1 to 3 words) | A single word, very large, centered. |
| A2 Icon or logo + name | `titre` + `image` (or the theme logo) | Centered icon, name below. |
| A3 Typographic agenda | `lignes[]`, `actif` (no. from 1 to n, optional) | Centered lines, the active line in accent, the others in gray. |
| A4 Thesis sentence | `titre` (3 to 8 words; `\n` to break) | One or two centered lines. |
| A5 Big figure + label | `chiffre` (only one), `libelle` (9 words at most), optional `surtitre` | Giant hero figure, in a gradient from `accent` to `accent2` (flat without `accent2`), label below, source in small type under the label. |
| A6 Comparison chart | `titre`, `barres[]`: `{ "libelle", "valeur", "etiquette", "mise_en_avant" }`, `unite`, `axe`, `afficher_valeurs` | Horizontal bars with no numbered axis: the highlighted bar in accent, the others in gray, the tag at the end. `valeur` only sets the length. |
| A7 List without bullets | optional `titre` (above the lines), `lignes[]` (2 to 6), `actif` | Centered lines, no bullets. With `actif`, the active line is white and the others gray. |
| A8 Checklist | optional `titre`, `lignes[]` (3 to 6), `coche` (`false` = empty circles) | Check marks in the accent color, or empty circles to set up a tension. |
| A9 Object + text | `titre`, `lignes[]` (3 at most), `cote` (`droite` to put the image on the right) + `image` | Visual on one half, text on the other. |
| A10 Full-frame screenshot | `image` | Screenshot centered over almost the whole frame, with no added text. |
| A11 Diagram with a highlighted block | `titre` (name of the system), `blocs[]` with a variant (see “Variants”) | Without a variant: rendered like A9 (warning). With a variant: line diagram, one block lit up, its caption at the end of a rule. |
| A12 Inside view | `image`, optional `note` | Full-bleed image. |
| A13 Product alone | `image` | Centered product, no text. |
| A14 Bento | `titre` (center tile), `tuiles[]` (4 to 8; 10 with a “product” grid, 12 in `grille-icones`, 6 to 11 in `fragments-logiciel`): `{ "type", "chiffre", "titre", "texte", "image" }` | Center tile in accent; around it, uneven tiles of 1 to 4 words. |
| A15 Wall of abundance | `elements[]`: text or `{ "titre", "image" }` | Dense grid that runs off the frame. |
| A16 Partner logos | optional `titre`, `logos[]`: `{ "nom", "image" }` (15 at most in a grid; 30 to 80 in `mur-dense`) | Regular grid; single-color logos to provide. |
| A17 Quote or testimonial | `citation`, `auteur` | Two to four bold lines, left-aligned; quotation marks added according to the language. |
| A18 Full-bleed photo | `image`, optional `titre` and `note` | Edge-to-edge photo; caption box at the bottom right for the note. |
| A19 Price | `offres[]` (1 or 2; 4 in `gamme-alignee`): `{ "nom", "mention", "prix", "note" }` + `image` | Name, then “Starting at” in small type, then the price in large type. |
| A20 Availability | `libelle` (small, above), `titre` (date or word) + optional `image` | Small gray label, large date, product below. |
| A21 Name and role lower third | `intervenant` (id) or `nom` + `fonction`; optional `image` | Two lines at the bottom left. |
| A22 to A25 Stage shots | `image`, optional `titre` | These are video shots. As slides, they become a full-bleed photo (warning), with or without a variant. |
| FIN Final slide | depends on the variant (`titre`, `libelle`, `lieu`, `mentions[]`) | The logo alone, centered, legal notes in very small type; without a logo, the final word. |
| COLORIS Colorways | `coloris[]`: `{ "nom", "hex", "image" }` (5 at most), `afficher_noms` | One product per colorway, same angle and same scale. |
| FRISE Timeline | `titre`, `jalons[]`: `{ "titre", "date", "image" }` (7 at most) | Equal milestones on one line, the last in accent. |
| AF To provide | `attendu`, optional `archetype_prevu` | Old way to flag a whole slide that is missing. **Avoid it**: it leaves a hole in the deck. Use the planned archetype, fill it with `[TO VALIDATE]` for what can be proposed and short `[TO PROVIDE]` markers for the rest, and put the instruction in `a_fournir`. |

### Variants: the layout of each archetype

`slide.variante` picks the slide's layout. The design of each variant, its visual and its fallback are in `designs.md`. This table only gives the names, and the fields each one reads on top of the archetype's.

- **Without a variant**, the engine keeps the archetype's original rendering. It is the same as the first variant for A1 (`aplat`), A3 (`centre`), A4 (`aplat`), A5 (`centre`), A7 (`centree`) and A17 (`courte`). Elsewhere, it is simpler than the variants. Always write the variant.
- **FIN, COLORIS and FRISE**: their variants can be placed on any archetype (`"archetype": "A1", "variante": "mot-final"`), or with `"archetype": "FIN"`, `"COLORIS"` or `"FRISE"`. Without a variant, these three take their first one.
- The name is compared without accents or capitals. An unknown variant is a check error. The engine only warns and keeps the original rendering.
- A missing main field is shown as a short `[TO PROVIDE: …]`, at the size of its field. A missing image leaves room for the fallback from the design card, with no number and no brand.
- `image` background: with a variant, the background image only comes from `image_fond`, since `image` is the content. Variants that already place their photo (`sur-image`, `sur-photo`, `sur-contenu`, `capture-nue`, `macro-matiere`, A18, A21 on a photo, `signe-sur-photo`) do not add one.
- Default overlay on a photo: 30 in A1 `sur-image` and A18 `photo-titre`, 40 in A4 `sur-image`, 45 in A5 `sur-photo` and A7 `sur-photo`, 60 in A8 `sur-contenu`. `slide.voile` overrides it.

| Archetype | Variants | Fields on top of the archetype's |
|---|---|---|
| A1 | `aplat`, `degrade`, `sur-image`, `entoure`, `matiere` | `entoure`: `couronne[]` (20 to 50 words); `sur-image`: `image` or `image_fond`; `matiere`: `image` (the word rendered in material) |
| A2 | `icone-nom`, `icone-cote`, `logo-nom`, `rangee`, `objet-interface`, `icone-seule` | `rangee`: `images[]` (3), no text; `logo-nom`: `image` or `theme.logo`; `objet-interface`: `titre` = the button label; `icone-seule`: no text |
| A3 | `centre`, `droite`, `ligne`, `numerote`, `suffixe`, `ligne-active`, `couleurs` | `numerote`: `numeros` (`false` = an accent dot); `suffixe`: `suffixe`; `couleurs`: `couleurs[]` (one HEX per line); `ligne-active`: `actif` = number of full lines, one slide per state |
| A4 | `aplat`, `degrade`, `mot-accent`, `definition`, `sur-image`, `sourdine`, `enchainee` | `definition`: `mot`, `nature`, and `titre` for the definition; `sur-image`: `image` |
| A5 | `centre`, `bloc`, `a-cote`, `sur-photo`, `objet-anneau`, `objet-jauge`, `contour` | `a-cote`: `image` (screen, phone or object, based on `attendu`); `sur-photo`: `image` (photo, already blurred); `objet-anneau`: `libelle` = the unit; `objet-jauge`: optional `libelle` |
| A6 | `barres`, `deux-axes`, `anneaux`, `frise`, `classement` | `deux-axes`: `series[]` `{ "libelle", "points", "mise_en_avant" }`, `axe_x`, `axe_y`, `sens_x`, `sens_y`; `anneaux`: `barres[]` (2), `valeur` = share from 0 to 100; `frise`: `nom`, `chiffre` (the gap), `periodes[]` (2), `generations` (3 to 6); `classement`: `rangs[]`, `colonnes[]` `{ "periode", "logos" }` |
| A7 | `centree`, `empilement`, `a-cote-icone`, `a-cote-objet`, `deux-colonnes`, `sur-photo`, `filet` | `empilement`: `actif` = lines shown; `a-cote-icone`, `deux-colonnes`: `image` (icon); `a-cote-objet`: `image` (object or screenshot); `sur-photo`: `image`; `filet`: `image` (screenshot); `deux-colonnes`: up to 18 lines |
| A8 | `coche-par-ligne`, `cercles-puis-coches`, `risque-puis-reponse`, `picto-par-ligne`, `sur-contenu` | `risque-puis-reponse`: `etat` (`risque` or `reponse`, one slide per state); `picto-par-ligne`: `pictos[]` (images) or `images[]`; `sur-contenu`: `image` |
| A9 | `appareil-centre-mot`, `objet-coupe`, `objet-liste`, `objet-chiffre`, `annotee`, `empilee` | `cote`; `objet-chiffre`: `chiffre`, `libelle` (instead of `titre`); `annotee`: `annotations[]` (5 at most) instead of `titre` |
| A10 | `telephone-centre`, `tablette-centre`, `portable-centre`, `zoom-serre`, `capture-nue`, `rangee` | no text; `rangee`: `images[]` (3) |
| A11 | `legende-laterale`, `plusieurs-blocs`, `schema-chiffre`, `carte-annotee`, `carre-halo` | `titre` (name of the system), `blocs[]` `{ "titre", "lignes", "zone": [x, y, w, h] }` in %, 3 at most in `plusieurs-blocs`, `cote`; `schema-chiffre`: `chiffre`, `libelle`; `carte-annotee`: `annotations[]` `{ "texte", "zone", "position" }`; `carre-halo`: `titre`, or `logo_systeme` |
| A12 | `macro-matiere`, `capot-ouvert`, `eclate-axial`, `flux-lumiere` | `eclate-axial`: `libelle` (the tag) |
| A13 | `centre-entier`, `hero-coupe`, `profil-levitation`, `coloris` | no text; `coloris`: `images[]` (2 views) |
| A14 | `nom-au-centre`, `produit-au-centre`, `tuiles-chiffres`, `mot-geant-et-produit`, `theme-et-matieres`, `grille-icones`, `fragments-logiciel` | `image`: the product of the center tile (the photo in `theme-et-matieres`, the light logo in `fragments-logiciel`); `mot-geant-et-produit`: `titre` of 2 to 5 letters; each tile: `type` (`capture`, `icone`, `photo`, `mot`, `chiffre`, `liste`, `matiere`, `coloris`, `halo`, and `fragment` in `fragments-logiciel`), `surtitre`, `mention`, `lignes[]`, `coloris[]`; `fragments-logiciel`: center `titre` (a name or a three-word loop, `\n` between them), optional center `texte`, 6 to 11 tiles, `fragment` = `titre` (4 words) + `texte` (5 words) + `image` (isolated component) + `echelle` (0.5 for a 2x export), `liste` = `titre` (kicker) + `lignes[]` (5 at most) |
| A15 | `vignettes`, `icones`, `mots`, `nuage`, `cartes-libelles`, `forme` | `elements[]` `{ "image", "titre" }`; `mots`: `deux_tons`; `nuage`: `titre` (the sharp name in the foreground); `forme`: `forme` (`coeur` or `cercle`) |
| A16 | `grille`, `ligne`, `logo-seul`, `mur-dense`, `pastilles`, `soi-au-centre` | `pastilles`: `logos[].couleur` (HEX); `soi-au-centre`: the theme logo in the center |
| A17 | `courte`, `longue`, `source-accent`, `centree-signature` | none |
| A18 | `usage`, `exemple-cartouche`, `diptyque`, `photo-titre` | `note` (the caption box); `diptyque`: `images[]` (2), `notes[]` (2); `photo-titre`: `titre` |
| A19 | `colonne`, `deux-offres`, `nom-en-haut`, `gamme-alignee`, `prix-heros`, `ancrage` | `gamme-alignee`: `offres[].image` (4 offers at most); `ancrage`: `libelle`, `etat` (`reference` = the reference price, in gray; one slide per state) |
| A20 | `haut-et-gamme`, `suite-de-dates`, `colonne`, `date-et-lieux`, `mot-seul` | `date-et-lieux`: `lieux[]` |
| A21 | `gauche`, `droite`, `double`, `sur-clair`, `carte-invite`, `carte-portrait` | `nom`, `fonction`, or `intervenant`; `double`: `personnes[]` `{ "nom", "fonction" }` or `intervenants[]`; `carte-invite`: `logo_invite`; `carte-portrait`: `image` (the portrait) |
| A22 to A25 | A22: `hall-ecran`, `scene-mur`, `panneau-verre` · A23: `mot-coupe`, `contenu-lisible`, `interface-geante`, `slide-floue` · A24: `large-centre`, `taille-centre`, `decor-sujet` · A25: `table-flux`, `mains-fond-uni`, `epaule`, `table-haute`, `tend-appareil` | accepted, rendered as a full-bleed photo of the scene (warning) |
| FIN | `signe-seul`, `signe-et-ligne`, `signe-et-evenement`, `signe-sur-photo`, `mot-final` | `mentions[]`; logo: `logo_final`, otherwise `image`, otherwise `theme.logo`; `signe-et-ligne`: `libelle`; `signe-et-evenement`: `titre` (the event), `lieu`; `signe-sur-photo`: `libelle` and the photo in `image_fond` or `image`; `mot-final`: `titre`, `libelle` |
| COLORIS | `rangee-alignee`, `rangee-chevauchee`, `eventail`, `un-par-un`, `mur` | `coloris[]` `{ "nom", "hex", "image" }` (5 at most), `afficher_noms`; `un-par-un`: `coloris[0]`, one slide per colorway |
| FRISE | `rangee-datee`, `generations`, `trois-jalons`, `courbe-et-saut`, `objet-du-passe` | `titre`, `jalons[]` `{ "titre", "date", "image" }` (7 at most, 3 in `trois-jalons`); `courbe-et-saut`: `nom`, `chiffre`, `periodes[]`; `objet-du-passe`: `image` |

A final slide becomes a full accent-color page only if it is the last one, in A1 or FIN, with no variant or with `aplat` or `mot-final`, and if `theme.finale_accent` is not `false`.

### Rich text

- `*word*` puts the word in the accent color: `"Clairval *Direct*"`. One word per title, the one to remember.
- `\n` forces a line break. Otherwise the engine balances title lines itself to avoid a single word on the last line.
- The final period of a title takes the accent color (`theme.point_accent`, see theme).
- `[TO VALIDATE: proposed text]` and `[TO PROVIDE: short label]` mark what the skill proposes and what it asks for. They work in every field: see the next section.
- In French decks (`"langue": "fr"`), French typography is applied at render time: a non-breaking space before `: ; ! ?` and between a number and its unit (`4 h`, `89 € HT`).

## Markers: what the skill proposes, what it asks for

A thin brief must not produce a deck full of holes. The skill **proposes** what can be written, and **asks for** what must be checked.

| | `[TO VALIDATE: proposed text]` | `[TO PROVIDE: short label]` |
|---|---|---|
| For what | What the skill can write itself: thesis, wording of a title, problem people live with, description of a feature, a line of the script. | What it never invents: figure, price, percentage, date, customer name, logo, testimonial, real screenshot, source. |
| On screen | The proposed text, as real content: the marker is removed, nothing sets it apart. | The label, **3 words at most**, in its field's style (same size, same weight), **faded** (40 % of the color of the text it replaces, or the text color if it replaces the accent; never a gradient, even inside an `*accent*`) and underlined with a discreet dotted line in the accent color. |
| In the notes and `script.md` | The passage stays flagged, so the presenter knows what is not validated yet. | The label stays flagged, followed by the `a_fournir` instruction. |
| At check time | Listed in the “TO VALIDATE” section, never blocking. **Error** if it contains a figure, a price, a percentage or a date, or if it fills a testimonial (A17), logo (A16), price (A19), date (A20) or figure field (A5, A6, A14, and any `textes.chiffre`) or a `source`. | Blocking without `--brouillon`. **Error**, even in draft mode, if the on-screen label is longer than 3 words. |
| In French decks | `[À VALIDER : …]` | `[À FOURNIR : …]` |

The check accepts both the English and the French forms.

- A marker can contain a `\n`: `"[TO VALIDATE: What we build,\nand *how*.]"` is shown on two lines, without brackets. A `[TO PROVIDE]` label stays on a single line. A marker without its closing `]` would be shown as is: it is a check error.
- Canva format (`meta.format`: `canva`): the import loses the fade (the 40 % opacity). So the label keeps its brackets on screen (`[date]`, `[gain]`), so it still reads as a slot in full color. The brackets do not count toward the 3 words.
- The long instruction never goes inside the marker: `"prix": "[TO PROVIDE: price]"` on screen, and `"a_fournir": "Monthly price per site, before tax, installation included, approved by the sales team."` on the slide.
- One passage can mix both, side by side, never one inside the other: `"[TO VALIDATE: Available from] [TO PROVIDE: date]"`.
- A proposal used again elsewhere (the thesis repeated at the close) keeps its marker everywhere it appears.
- At delivery, the skill gives both lists, slide by slide: what must be validated, what must be provided.

### Sizes

Text sizes are not written in `deck.json`. Each archetype has a maximum size. The engine shrinks it until the text fits, without going below a floor. If the text still does not fit, the engine says so: cut words, do not shrink further.

## notes: the spoken script

Three forms are accepted:

```json
"notes": "Text spoken by slide.intervenant."
```

```json
"notes": [
  { "intervenant": "claire", "type": "relais", "texte": "To tell you more, here's Hugo. Hugo, over to you." },
  { "intervenant": "hugo", "texte": "Thanks, Claire. It all starts with this box…" }
]
```

```json
"notes": ["First paragraph.", "Second paragraph."]
```

- The script follows the templates in `data/formules.json` and `data/annonce.json`, adapted to the language (and, in French, to the register). It never reuses a quote from a keynote.
- **It reads in full, out loud, at about 140 words per minute for the target length**: for 10 minutes, about 1,400 words, handovers included. The check counts the words to be spoken (`[TO VALIDATE]` proposals included, without `[TO PROVIDE]` markers or cues in brackets or parentheses) and warns below 110 or above 170 words per minute over `meta.duree_min`. Stage cues go in `build`, not in the spoken text.
- `"type": "relais"` marks a handover. In French it follows `meta.registre_intervenants` (“à toi” or “à vous”), even if the audience is addressed as “vous”. The audience register check ignores these segments.
- The engine writes in the .pptx notes (and under each slide of the preview):

```
CLAIRE DUVAL · Chief Executive Officer (handover)
To tell you more, I'll hand over to Hugo…

→ HUGO BERNARD · Head of Product
Thanks, Claire. It all starts with this small box…

BUILD
1. The box appears first, alone.
2. The three lines appear one by one.

TIMING 3:50 → 4:45 (55 s)
SOURCE (shown on the slide): …
TO VALIDATE: “…”
TO PROVIDE: price. Monthly price per site, before tax, installation included…
```

The `→` arrow flags a change of speaker from the previous segment. The timing is cumulative from the first slide. Without `role`, the header line carries the name alone.

The note labels follow the deck language (in French: APPARITIONS, MINUTAGE, SOURCE, À VALIDER, À FOURNIR, and “relais” for the handover). No working term appears in them: no step number, no archetype name. The presenter reads their notes and does not need to know the grammar.

## Builds and transitions

- **Transitions.** Each slide comes in with a short fade. Nothing to write in `deck.json`.
- **Builds.** `build` lists the builds in order, one sentence per click, written for the presenter (for example: The figure comes in when it is said). The engine sets a fade-in entrance animation, on click, on the slide's elements, in the archetype's reading order: kicker and title, then figure, label, lines one by one, tiles around the center tile, the other bar then your own bar. A slide without `build` appears all at once.
- A list is written in a single text box, one paragraph per line, so that a “by paragraph” animation is enough if the user edits it.
- With a variant, the order follows its design card in `designs.md`: the visual, then the kicker and the title, then the figure and the label, then the lines, bars, tiles or logos one by one. A few words in `build` point to a group specific to a variant: “checks” (A8 `cercles-puis-coches`), “ring” and “gauge” (A5), “curves” (A6 `deux-axes`), “blocks” or “captions” (A11), “flow” or “glow” (A12 `flux-lumiere`), “tag” (A12 `eclate-axial`), “milestones” (FRISE), “colorways” (COLORIS). In French decks, the French words work too: « coches », « anneau », « jauge », « courbes », « blocs », « légendes », « flux », « halo », « étiquette », « jalons », « coloris ».
- What stays manual: a morph between two slides (Magic Move, Morph), a video to start, and any build whose order differs from the reading order. `export_script.js --etapes` gives the list.

## Audience, sources and devices

`references/publics.md` says, for each audience, which devices to keep. `references/data/publics-exigences.json` is the machine version, and `check_deck.py` and `build_deck.js` both read this file. When `publics.md` changes, update this file.

| Key | Values | Effect |
|---|---|---|
| `source_chiffre` | `exigee`, `recommandee`, `facultative` | `exigee` (required): a figure without a `source` is a blocking error. This is the setting for every audience: the skill invents no figure, and every figure comes from the user with its source. |
| `affichage_source` | `sous_le_chiffre`, `renvoi`, `carton_final`, `aucun` | `sous_le_chiffre`: the source in full, in small type under the figure. `renvoi`: “Source 1 · see the final slide” under the figure, and the full source on the final “Sources and notes” slide. `carton_final`: nothing on the slide, everything on the final slide. `aucun`: only in the notes. |
| `graduation` | `sans`, `valeurs`, `graduee` | `valeurs` and `graduee` write the values at the end of A6 bars, even without `etiquette`. `graduee` triggers a warning: A6 has no axis, so a native chart is needed if the axis matters. |
| `concurrent` | `nommes`, `nommes_si_utile`, `anonymes`, `absents` | `nommes` flags a bar with an anonymous label (“traditional solution”). `absents` flags any competitor bar. |
| `jusqua` | `avec_condition`, `valeur_typique`, `interdit` | “up to” on screen: `avec_condition` requires a `source` that gives the conditions, `valeur_typique` flags it (the maximum is said out loud, with its condition), `interdit` is a blocking error. |
| `superlatifs` | `avec_preuve`, `moderes`, `aucun` | `aucun`: every superlative on screen is flagged. `moderes`: one per block. In every case, an absolute superlative (“in the world”, “the best”) without a `source` is flagged. |
| `slide_prix` | `oui`, `non` | `non`: an A19 slide is flagged (for investors, present the business model). |
| `duree_min_conseillee` | `[min, max]` or `null` | Target length out of range: warning. |
| `registre_suggere` | text | Hint for the tu / vous question (French decks). The register is still asked of the user. |

Planned audiences, in the order of the question: `b2b-decideurs`, `b2b-acheteurs`, `grand-public`, `investisseurs`, `partenaires`, `interne-sprint`, `interne-demo`, `interne-all-hands`, `salon-conference`, `recrutement`, `defaut`. An unknown audience gets the `defaut` row, the most cautious one. For a mixed audience, each setting takes the most cautious value among the audiences present, following the file's `prudence` order.

A slide counts as having a figure if it is an A5 or an A6, an A14 with a tile that carries a figure, a slide that fills `textes.chiffre` (A9 `objet-chiffre`, A11 `schema-chiffre`, FRISE `courbe-et-saut`…), or if its text contains a %, a multiplier (“2x”, “3 times”) or “up to N”. Prices (A19) and dates (A20) do not require a source.

## Images

- Formats read: PNG, JPEG, GIF. Dimensions are read from the file, and the image is never distorted.
- `ajustement`: `contenir` (contain; the default, the whole image inside its box) or `couvrir` (cover; the box is filled and the image cropped; the default for full-frame archetypes).
- Missing or unreadable image: the engine **draws a placeholder** in the slide's style, on its background: a schematic interface (window, gray bars and blocks, one element in accent) for a screenshot, a simple silhouette for an object or a photo. No made-up figure or text inside: gray bars, not numbers. No instruction on screen: `attendu` goes into the notes, and the check repeats it (“Image to provide”). Rendering continues, and the placeholder stays in the .pptx as long as the image is missing.
- Always write `{ "chemin": "images/....png", "attendu": "…" }` for a missing image: the path says where to drop it, `attendu` says what it must show.
- For A16, provide single-color logos. The engine does not recolor images.
- A screenshot is always bare: the engine adds the generic device (corners at 13 % of its width, border at 3 %; no notch, no button, no camera, no logo), and the screenshot fills its screen.
- Images carried by an element: `tuiles[].image` (A14), `elements[].image` (A15), `logos[].image` (A16), `offres[].image` (A19 `gamme-alignee`), `coloris[].image` (COLORIS), `jalons[].image` (FRISE), `colonnes[].logos[].image` (A6 `classement`). Several visuals on one slide: `images[]`.
- The fallback depends on the variant (silhouette, schematic interface, icon tile, gray pictogram, flat color and two neutral glows): `designs.md`, §7 of each design card. It never carries a number, made-up text or a brand.

## Visuals to prepare: `slide.visuel`

`image` says where the file is and what it shows. `visuel` says how to prepare it: it is the brief that the user, their designer or their photographer receives. The skill fills it in at the “Design slide by slide” step, based on §7 of the archetype's design card in `designs.md`. It appears neither on screen nor in the notes.

```json
"image": { "chemin": "images/apercu.png", "attendu": "Notebook customization screen, preview of the cover" },
"visuel": {
  "type": "capture",
  "brief": "Notebook customization screen, preview of the cover; demo data, neutral time, no notifications.",
  "fond_transparent": false,
  "angle": "face",
  "resolution_min": "1170 × 2532"
}
```

| Field | Values | Role |
|---|---|---|
| `type` | `capture`, `photo`, `produit`, `objet`, `icone`, `logo`, `schema`, `matiere`, `pictogrammes`, `vignettes`, `video` | The kind of visual (screenshot, photo, product, object, icon, logo, diagram, material, pictograms, thumbnails, video). It sets the default format and resolution. |
| `brief` | text | What the visual must show, its framing, its light, what it must not contain. One or two sentences, written for the person who prepares it. |
| `fond_transparent` | `true` or `false` | `true` for a cut-out product, object, icon or logo (PNG or SVG). When missing: the type's value. |
| `angle` | text: `face`, `trois-quarts`, `profil`, `dessus`, `contre-plongée`… | The requested view (front, three-quarter, profile, top, low angle). When missing: free. |
| `resolution_min` | `"1920 × 1080"`, `[1920, 1080]`, or a number (pixels on the long side) | The minimum file size. When missing: the type's value. |
| `format` | optional: `PNG`, `JPEG`, `SVG`, `MP4`… | Overrides the type's format. |
| `chemin` | optional | Where to drop the file, when it is not `image.chemin` (a second visual, a tile). |

Default values for each type (those of §7 of the design cards):

| Type | Format | Transparent background | Minimum resolution |
|---|---|---|---|
| `capture` | PNG | no | native screen resolution (phone 1170 × 2532; wide screen 1920 × 1080) |
| `photo` | JPEG | no | 1920 × 1080 (3840 × 2160 recommended) |
| `produit`, `objet` | PNG | yes | 2000 px high (product) or on the long side (object) |
| `icone` | SVG or PNG | yes | 1024 × 1024 |
| `logo` | SVG or PNG | yes | 600 px wide (1000 px high for the final slide) |
| `schema` | SVG or PNG | yes | 2000 × 2000 |
| `matiere` | JPEG | no | 1920 × 1080 |
| `pictogrammes` | SVG | yes | vector, one file per pictogram |
| `vignettes` | JPEG or PNG | no | 640 px wide each, all in the same format |
| `video` | MP4 | no | 1920 × 1080 (3840 × 2160 recommended) |

- A slide that needs several visuals (two views of a product, a fan of colorways) takes a list: `"visuel": [ {…}, {…} ]`.
- Without `visuel`, `export_script.js --visuels` infers the type from the archetype and the variant, and uses `image.attendu` as the brief. Write `visuel` anyway: a precise brief avoids a second photo shoot.
- The brief contains no workshop instruction and no archetype name: it is written for someone who does not know the skill.
- The engine draws a fallback while the file is missing (see Images). The brief does not change the fallback.

```bash
node "$SKILL/scripts/export_script.js" deck.json --visuels visuels.md
```

`visuels.md` lists each visual, slide by slide: its type, its brief, its format, the transparent background, the angle, the minimum resolution, the expected file, and whether it is already provided. It is the list delivered to the user.

## What check_deck.py checks

Blocking errors (exit code 1):
- unknown archetype;
- unknown variant for the archetype, or a variant on an archetype that has none (list in the “Variants” table);
- `slide.visuel` that is neither an object nor a list of objects;
- missing required field (archetype table; some variants require others, see “Variants”);
- two figures on an A5 figure slide;
- figure without a source when the audience requires one;
- remaining `[TO PROVIDE]` marker, `a_fournir` instruction or `AF` slide (only a warning with `--brouillon`);
- `[TO PROVIDE]` label of more than 3 words on screen (`textes` or `source`), even with `--brouillon`;
- `[TO VALIDATE]` that contains a figure, a price, a percentage or a date (including in words: “two”, “free of charge”, “in January”, “in one hour”), or that fills a testimonial, a logo, a price, a date, a figure or a source;
- nested markers, or a marker without its closing `]`;
- Apple font in the theme (SF, New York);
- empty notes;
- missing `duree_s`;
- total length more than 15 % away from `duree_min`;
- in French, a script that uses “tu” more than “vous” while the register is `vous` (or the reverse);
- `meta.registre` (French), `meta.format`, `meta.public`, `meta.duree_min` or `meta.affichage_source` missing or invalid, invalid `meta.registre_intervenants`;
- “up to” on screen when the audience forbids it;
- chart without values (`afficher_valeurs: false`) when the audience expects them;
- ratio other than 16:9;
- missing required color or invalid HEX;
- unknown speaker;
- duplicate `id`.

Warnings:
- more than 10 words on screen (except lists, quotes, bento, walls and logos);
- title card of more than three words, figure label of more than nine words;
- list too long (6 lines, 18 in A7 `deux-colonnes`), bento outside 4 to 8 tiles (4 to 10 in a “product” grid, 3 to 12 in `grille-icones`), more than 2 offers (4 in `gamme-alignee`);
- in French, an isolated “tu” or “vous”; a handover that does not follow `registre_intervenants`, or `registre_intervenants` missing with several speakers;
- unknown `meta.variante` or `meta.contexte`;
- speaking rate above 170 words per minute on a slide;
- script too short or too long for the target length: below 110 or above 170 words per minute over `meta.duree_min` (words to be spoken, without `[TO PROVIDE]` markers and cues);
- two consecutive slides in the same block that switch from `sombre` to `clair` (or the reverse);
- kicker of more than 3 words;
- speaker role written as a marker;
- `theme.point_accent` or `theme.finale_accent` that is not `true` or `false`;
- missing image (“Image to provide”, with its `attendu`);
- image variant with no image at all (`image`, `images`, `image_fond`, element image or `slide.visuel`): the fallback will be drawn;
- images in `images[]`, element images (`offres`, `coloris`, `jalons`, `elements`, `pictos`, `colonnes`) or extra logos not found; logos without an image (their name is written as text);
- `slide.visuel` without `type` or `brief`, unknown type, `fond_transparent` that is not `true` or `false`, unreadable `resolution_min`, unknown field;
- `slide.profondeur` that is not `true` or `false`, unknown `slide.appareil`;
- three slides in a row with the same archetype and the same variant (a missing variant counts as the engine's);
- a block of two or more slides with no visual moment: no A5, A9, A10, A13, A14 or A18, and no image variant (the “Strong visual moment” column of the “The engine's variants” table, `designs.md`);
- low contrast (`accent2` included);
- “up to”, superlatives, competitors, a chart that needs an axis, a price slide and a length out of range, depending on the audience;
- stage shots A22 to A25 (with or without a variant), and A11 without a variant, rendered differently.

A separate section, never blocking: **TO VALIDATE**, the list of proposals, slide by slide (key `a_valider` with `--json`). The delivery repeats it as is.

## Full example

Here is a short but complete deck: a two-minute slot at a trade show, with two voices. Each slide has its variant. The price of a service with no physical object uses `prix-heros`, and the missing screenshot has its brief in `visuel`. A 16-slide version is in `assets/exemple-deck.json`, with its images in `assets/exemple-images/`. Everything in it is fictional.

```json
{
  "meta": {
    "titre": "Atelier Brume: new offer",
    "langue": "en",
    "public": { "type": "salon-conference", "description": "Visitors at a trade show, 2-minute slot" },
    "duree_min": 2,
    "format": "powerpoint",
    "ratio": "16:9"
  },
  "theme": {
    "nom": "Atelier Brume",
    "couleurs": {
      "fond_sombre": "#1A1F24", "fond_clair": "#FFFFFF", "texte": "#1A1F24",
      "texte_secondaire": "#5E6670", "accent": "#E8622C", "accent2": "#F59E5B"
    },
    "polices": { "titre": { "nom": "Arial", "repli": "Arial" }, "texte": "Arial" },
    "point_accent": true
  },
  "intervenants": [
    { "id": "lea", "nom": "Léa Morin", "role": "Founder" },
    { "id": "tom", "nom": "Tom Girard" }
  ],
  "slides": [
    {
      "id": "s1", "bloc": "Opening", "archetype": "A1", "variante": "aplat", "fond": "sombre", "intervenant": "lea",
      "textes": { "titre": "Hello." },
      "notes": "Hello, everyone, and thank you for stopping by our booth. I'm Léa, and I run Atelier Brume, the stationery workshop that many of you already know. We have two minutes, and something new to show you.",
      "duree_s": 20, "build": ["The word is on screen before anyone speaks."]
    },
    {
      "id": "s2", "bloc": "Brume Custom", "etape": 3, "archetype": "A5", "variante": "centre", "fond": "sombre", "intervenant": "lea",
      "textes": { "surtitre": "Today", "chiffre": "[TO PROVIDE: current wait]", "libelle": "average wait for a custom notebook" },
      "source": "[TO PROVIDE: source]",
      "a_fournir": "Current average time to make a custom notebook, with its source (internal log, study) and its period.",
      "notes": "Today, when you order a custom notebook from us, you wait [TO PROVIDE: current wait] on average. It's the feedback we hear from you most often, and we hear it. A notebook that runs late means a customer who waits, or an empty shop window. We wanted to change that.",
      "duree_s": 25, "build": ["The kicker first.", "The figure comes in when it is said, then the label."]
    },
    {
      "id": "s3", "bloc": "Brume Custom", "etape": 6, "archetype": "A1", "variante": "aplat", "fond": "sombre", "intervenant": "lea",
      "textes": { "surtitre": "New", "titre": "Brume *Custom*" },
      "notes": [
        { "intervenant": "lea", "texte": "This is Brume Custom." },
        { "intervenant": "lea", "type": "relais", "texte": "Tom designed it with our bindery team. He'll tell you more. Tom, over to you." }
      ],
      "duree_s": 15, "build": ["The name appears alone, the moment it is said. Two seconds of silence."]
    },
    {
      "id": "s4", "bloc": "Brume Custom", "etape": 9, "archetype": "A9", "variante": "objet-liste", "fond": "sombre", "intervenant": "tom",
      "textes": {
        "titre": "[TO VALIDATE: Designed in the morning, bound by night.]",
        "lignes": ["[TO VALIDATE: Your cover, your paper]", "No minimum", "Live preview"]
      },
      "image": { "chemin": "images/apercu.png", "attendu": "Notebook customization screen on a phone, preview of the cover" },
      "visuel": { "type": "capture", "brief": "Notebook customization screen, preview of the cover; demo data, neutral time, no notifications.", "fond_transparent": false, "angle": "face", "resolution_min": "1170 × 2532" },
      "notes": "Thanks, Léa. [TO VALIDATE: You design your notebook in the morning, and we bind it by night.] There's no minimum order: one copy or fifty, it's the same service. And you watch your notebook take shape live, from your phone, with every choice of paper or cover. You always know what it will look like, and so does your customer, if you send them the link.",
      "duree_s": 30, "build": ["The screen first.", "The title, then the three lines one by one."]
    },
    {
      "id": "s5", "bloc": "Brume Custom", "etape": 15, "archetype": "A19", "variante": "prix-heros", "fond": "sombre", "intervenant": "tom",
      "textes": { "offres": [{ "nom": "Brume Custom", "mention": "Starting at", "prix": "[TO PROVIDE: price]", "note": "per notebook" }] },
      "a_fournir": "Price of a Custom notebook before tax, approved by Léa.",
      "notes": [
        { "intervenant": "tom", "texte": "Brume Custom starts at [TO PROVIDE: price] before tax per notebook, with no subscription. You can try it today: design your first notebook right here, at the booth, with me." },
        { "intervenant": "tom", "type": "relais", "texte": "Léa, back to you." }
      ],
      "duree_s": 25, "build": ["The name, then the price."]
    },
    {
      "id": "s6", "bloc": "Close", "archetype": "A1", "variante": "mot-final", "fond": "sombre", "intervenant": "lea",
      "textes": { "titre": "Thank you." },
      "notes": "Thanks, Tom. And thank you all. [TO VALIDATE: Brume Custom means designing your notebook in the morning and holding it in your hands by night.] Come and see us before you leave: we have samples for you, and Tom will show you the preview on his phone. Enjoy the rest of the show!",
      "duree_s": 20
    }
  ]
}
```

With `check_deck.py --brouillon`, this example passes with no error and three intended warnings: the wait and its source, the price, and the missing image. The “TO VALIDATE” section lists the four proposals: the title, the line and the sentence on slide 4, and the sentence repeated at the close. Without `--brouillon`, the `[TO PROVIDE]` markers and the `a_fournir` instructions block it until the user has given the wait time, the source and the price. The skill asks the user for them before delivering, and has them validate the proposals.
