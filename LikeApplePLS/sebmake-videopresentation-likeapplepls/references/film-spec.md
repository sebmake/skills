# Format de `film.json`

`film.json` décrit un film produit et ses déclinaisons pour les réseaux. Le moteur le lit :

- `scripts/check_film.py film.json` contrôle le fichier (durées, lecture, chiffres, visuels, zones sûres).
- `node scripts/build_film.js film.json --planche` fait la planche de validation, sans rendu vidéo.
- `node scripts/build_film.js film.json --rendu` fabrique les projets HyperFrames et rend les MP4.

Règles de fond, rappelées ici parce que le format les porte :

- **Aucune voix.** Il n'existe pas de champ « voix ». Le sens passe par les cartons et la musique.
- **Musique fournie ou aucune.** Un fichier local dont l'utilisateur a les droits, ou `null`. Jamais d'adresse web, jamais de musique cherchée ou générée.
- **Aucun chiffre inventé.** Un chiffre n'entre que par `texte.chiffre`, avec sa `source`. Sans chiffre fourni, le carton affiche `[À FOURNIR]` estompé.
- **La grammaire, jamais la marque.** Ni police, ni logo, ni appareil, ni signature d'une autre marque.

Les chemins de fichiers sont **relatifs au dossier de `film.json`**. Les durées sont en secondes.

---

## 1. Vue d'ensemble

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

| Bloc | Rôle |
|---|---|
| `meta` | ce que l'on fait : produit, message, public, formats, durée visée |
| `theme` | l'habillage : couleurs par rôle, polices avec repli, logo |
| `musique` | la piste fournie, ou `null` (film muet) |
| `plans` | le film long, dans l'ordre : un plan = une scène = une recette |
| `declinaisons` | les versions réseaux : format, durée, plans retenus ou règle |

---

## 2. `meta`

| Champ | Type | Obligatoire | Sens |
|---|---|---|---|
| `titre` | texte | oui | nom du projet (sert aux noms de fichiers) |
| `produit` | texte | oui | le nom exact du produit, tel qu'il s'écrit à l'écran |
| `message` | texte | oui | la phrase que le spectateur doit retenir (n'est pas affichée telle quelle) |
| `public` | texte | oui | à qui parle le film |
| `langue` | texte | non | `fr` par défaut |
| `formats` | liste | oui | formats demandés : `16:9` (le film), et ceux des déclinaisons (`9:16`, `1:1`) |
| `duree_cible_s` | nombre | oui | durée visée du film long, 60 à 120 s |
| `fps` | nombre | non | 30 par défaut |

---

## 3. `theme`

```json
"theme": {
  "source": "HEX donnés par l'utilisateur le 21/10",
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

| Champ | Sens |
|---|---|
| `source` | d'où viennent les couleurs : lien du design system, ou « HEX fournis » |
| `couleurs.fond_sombre` | fond des plans sombres (un charbon plutôt qu'un noir pur) |
| `couleurs.fond_clair` | fond des plans clairs (jamais `#FFFFFF` pur : 0 film clair sur 7 l'utilise) |
| `couleurs.texte_sur_sombre`, `texte_sur_clair` | couleur des cartons selon le fond |
| `couleurs.accent` | **une seule** couleur forte : halo, nom, détail. Obligatoire |
| `couleurs.accent_2` | facultatif : seconde teinte du halo |
| `polices.titres` | nom, mots-chocs, chiffres. `graisse` 600 ou 700 |
| `polices.texte` | phrases des cartons. `graisse` 400 ou 500 |
| `polices.*.repli` | polices de secours, dans l'ordre. Le moteur ajoute `sans-serif` à la fin |
| `polices.*.fichier` | facultatif : fichier `.woff2`, `.woff`, `.ttf` ou `.otf` fourni ; il est embarqué dans le rendu |
| `logo` | facultatif. `sur_sombre` et `sur_clair` (SVG ou PNG transparent). Un seul suffit. Fichier absent : la fin se fait **sans logo** (jamais de faux logo) |

Polices sûres sans fichier : Inter, Roboto, Open Sans, Lato, Nunito, Montserrat, Poppins, Outfit, Oswald, League Gothic, Archivo Black, Playfair Display, EB Garamond, Space Mono, IBM Plex Mono, JetBrains Mono, Source Code Pro. HyperFrames 0.8.181 les récupère sur Google Fonts à la première compilation, puis les garde en cache (`~/.cache/hyperframes/fonts/`) : il faut le réseau une fois. Une police de l'utilisateur passe par `fichier` (embarquée, sans réseau).

Polices refusées par le contrôle (polices propres à une marque d'appareils) : `SF Pro`, `SF Pro Display`, `SF Pro Text`, `SF Compact`, `SF Mono`, `New York`, `San Francisco`, `-apple-system`, `BlinkMacSystemFont`, `system-ui`, `ui-sans-serif`, `Myriad`.

---

## 4. `musique`

`null` : le film est muet. Sinon :

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

| Champ | Sens |
|---|---|
| `fichier` | chemin local (`.mp3`, `.m4a`, `.wav`, `.aac`). Une adresse `http…` est refusée |
| `droits_confirmes` | doit valoir `true` : l'utilisateur a dit qu'il a les droits |
| `debut_s` | où commencer dans la piste |
| `volume` | 0 à 1 |
| `fondu_sortie_s` | fondu de fin, 2 s par défaut |
| `caler_coupes` | `true` : chaque début de plan est déplacé sur le temps le plus proche (±0,25 s au plus). **Convention** : le calage des coupes sur la musique n'est pas démontré dans le corpus (16 coupes sur 62 tombent sur une attaque forte, 16,4 attendues au hasard) |
| `temps_s` | facultatif : liste des temps forts, en secondes dans la piste |
| `bpm`, `premier_temps_s` | facultatif : grille régulière, si `temps_s` est vide |

Si `caler_coupes` vaut `true` sans `temps_s` ni `bpm`, le moteur lance `npx hyperframes beats` sur la piste et lit la grille produite.

Chaque déclinaison peut avoir son propre `musique_debut_s` (par exemple pour partir du refrain).

---

## 5. `plans`

Un plan = une scène HyperFrames = une recette. L'ordre de la liste est l'ordre du film.

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
  "texte": { "type": "libelle", "contenu": "Lumière du jour" },
  "mouvement": { "detail": { "zone": [52, 30, 40, 42], "mode": "zoom" } },
  "transition": "coupe",
  "notes": "La courbe de la journée, puis on entre dans la fin d'après-midi."
}
```

| Champ | Type | Sens |
|---|---|---|
| `id` | texte | unique, lettres minuscules, chiffres et tirets (`p01`, `revel`) |
| `recette` | texte | une des 12 recettes du § 6 |
| `role` | texte | place dans le récit : `accroche`, `contexte`, `preuve`, `revelation`, `chute`, `respiration`, `fin`. Sert au contrôle et à la règle `auto` des déclinaisons |
| `groupe` | texte | facultatif : des plans de même groupe sont gardés ou retirés ensemble (un carton et le plan qui le prouve) |
| `priorite` | 1, 2 ou 3 | facultatif : 1 = à garder en premier dans une déclinaison courte |
| `duree_s` | nombre | durée du plan dans le film long |
| `fond` | texte | `sombre`, `clair` ou `accent`. Chaque recette a un fond par défaut |
| `visuels` | objet | les fichiers du plan, par « emplacement » (voir la recette). Un fichier absent est remplacé par un **repli dessiné neutre** (formes grises, sans marque ni texte) et signalé |
| `texte` | objet ou `null` | le texte à l'écran (§ 5.1) |
| `mouvement` | objet | réglages de mouvement propres à la recette (§ 6). Tous facultatifs |
| `transition` | texte | comment le plan **entre** : `coupe` (défaut, 14/14 films), `fondu` (fondu enchaîné 0,4 s ; non vérifiable dans le corpus, à garder rare), `noir` (le plan précédent s'éteint en 0,4 s, celui-ci sort du noir en 0,5 s ; 10/14 films passent au moins une fois par le noir) |
| `notes` | texte | intention, pour la planche. Jamais affiché dans le film |

### 5.1 `texte`

| `type` | Champs | Recettes | Règles |
|---|---|---|---|
| `phrase` | `contenu`, `groupes` (facultatif), `affichage` | `carton`, `mot-sur-image` | 12 mots au plus. Jusqu'à 6 mots : affiché d'un bloc. De 7 à 12 : construit en 2 ou 3 groupes de sens |
| `mot` | `contenu` | `carton`, `mot-sur-image` | 1 ou 2 mots « coup de poing », gros corps. Un ou deux par film |
| `chiffre` | `chiffre`, `libelle`, `source` | `carton` | `chiffre` vaut `null` tant que l'utilisateur ne l'a pas donné : le carton affiche `[À FOURNIR]` estompé. `libelle` contient la base de comparaison |
| `libelle` | `contenu` | `panneau`, `empilement`, `mur`, `orbite`, `eclate`, `macro` | nom de fonction, 1 à 4 mots, posé à côté de l'image |
| `nom` | `contenu`, `ligne` (facultatif) | `fin`, `revelation` | le nom du produit ; `ligne` = une ligne d'action fournie (« Bientôt disponible », une adresse, une date fournie) |

- `groupes` : la phrase découpée par l'auteur, par exemple `["Froide le matin.", "Chaude le soir."]`. La concaténation doit redonner `contenu`. Sans `groupes`, le moteur coupe à la ponctuation, sinon au milieu.
- `affichage` : `bloc`, `groupes` ou `mot-a-mot`. Par défaut : `bloc` jusqu'à 6 mots, `groupes` au-delà.
- Les mots ne changent jamais d'un format à l'autre. Seule la coupure des lignes change.
- Casse de phrase, pas de point d'exclamation, pas de capitales pour une phrase.

---

## 6. Les 12 recettes

Chaque recette est une fonction du moteur (`RECETTES` dans `build_film.js`). « Emplacements » = clés de `visuels`. Les comptes viennent des analyses du corpus ; « convention » = non observé.

| Recette | Ce qu'on voit | Emplacements | `mouvement` | Fond par défaut | Durée conseillée |
|---|---|---|---|---|---|
| `noir` | passage par le noir, point lumineux en option (noir 10/14 films ; point lumineux 3/14) | aucun | `point` (booléen) | noir | 0,5 à 1,5 s |
| `lisere` | l'objet dessiné par son seul contour éclairé, sur charbon (3/14) | `objet` (PNG détouré) | `cote` (`gauche`, `droite`) | sombre | 3 à 5 s |
| `macro` | très gros plan qui glisse, mise au point qui glisse (macro 12/14 ; glissement de mise au point : convention) | `image` (macro ou objet détouré) | `echelle` (1,2 à 3,5 ; 2,6 par défaut ; plafonnée à 1,5 × la définition d'une photo), `sens` (`gauche`, `droite`, `haut`, `bas`), `point` ([x, y] en % de l'image) | sombre | 1,5 à 3 s |
| `orbite` | rotation lente simulée en 3D, ±12° au plus, reflet qui glisse, lévitation (rotation 8/14 ; lévitation 9/14) | `objet`, ou `vues` (liste de 2 à 5 vues proches) | `angle` (≤ 12), `sens` (1 ou -1) | clair | 3 à 6 s |
| `eclate` | éclaté en couches qui se referme (éclaté 6/14 ; assemblage 7/14) | `pieces` (liste de PNG de même taille, du bas vers le haut), ou `objet` seul (découpé en bandes) | `axe` (`vertical`, `profondeur`), `bandes` (3 à 6) | clair | 4 à 6 s |
| `revelation` | l'objet entier, seul : sort du noir, halo, lévitation, filet de lumière qui balaie une fois, recul lent (filet 4/14 ; halo 3/14 ; recul 6/14) | `objet` | `recul` (booléen), `halo` (booléen) | sombre | 5 à 8 s |
| `panneau` | interface sans appareil, en panneau flottant, puis on entre dans un détail (zoom : le reste se floute et s'efface) ou on l'éclaire (projecteur : tout le cadre s'assombrit, l'élément grossit au centre) (sans appareil 7/12 ; poussée vers un détail 6/12) | `capture` | `detail` : `{ "zone": [x, y, l, h] en % de la capture, "mode": "zoom" ou "projecteur" }` | clair | 3 à 6 s |
| `empilement` | 2 à 5 fenêtres qui arrivent de la profondeur et s'empilent (assemblage 3/12) ; en révélation : recul lent et halo d'accent (convention) ; nom possible en déclinaison (`avec_nom`) | `captures` (liste) | aucun | clair | 3,5 à 5 s |
| `carton` | carton typographique sur fond uni : phrase, mot ou chiffre (carton = plan à lui : 23/33) | aucun | aucun | sombre | selon les mots (§ 7) |
| `mot-sur-image` | 1 à 4 mots posés dans la zone calme d'une image (1 cas en annexe ; convention) | `image` | `zone` (`centre`, `haut`, `bas`, `gauche`, `droite`), `point` ([x, y] % : sujet à garder en 9:16 et 1:1) | image | 2,5 à 4 s |
| `mur` | mur d'icônes ou de visuels : grille qui se remplit, projecteur sur l'un (`grille`), ou défilé un par un à 0,5 s (`defile`) (défilé 1/12 ; projecteur mesuré sur 1 passage) | `elements` (liste) | `mode` (`grille`, `defile`), `focus` (rang de l'élément éclairé, à partir de 1) | sombre | 3 à 6 s |
| `fin` | le nom seul, centré, puis le logo et une ligne d'action s'ils sont fournis (nom en fin : 21/24 segments) | aucun (le logo vient de `theme.logo`) | `taille` (`heros` ou `discret`) | sombre | 3 à 4,5 s |

Le contrôle refuse toute autre valeur de `recette`.

Cadrage des PNG détourés : le moteur mesure la boîte utile (pixels non transparents) et cadre cette boîte, pas la toile entière. Des `pieces` doivent partager la même toile (même taille, chaque pièce à sa place) : l'éclaté les écarte puis les remet en place.

Texte de `revelation` : seulement `{ "type": "nom" }`, utilisé quand une déclinaison demande `avec_nom` (sinon le nom de `meta.produit`). `avec_nom` marche aussi sur un `empilement` (révélation d'un logiciel).

---

## 7. Ce que le moteur calcule (et que `check_film.py` vérifie)

- **Durée d'un carton** (`grammaire-film.md` § 6.4, convention calée sur l'observé) : au moins `1,2 s + 0,3 s × mots` ; 1,5 s au moins pour une phrase, 1,0 s pour un mot seul, 2,5 s pour le nom. Un carton construit compte à partir du dernier groupe apparu, puis tient au moins `1,0 + 0,1 × mots`.
- **Mots** : 12 au plus par carton (106 cartons sur 109). Au-delà de 6, construction en groupes.
- **Caractères par ligne** : 42 en 16:9, 22 en 9:16, 26 en 1:1 (convention pour le français), et jamais plus que la largeur de ligne permise : le moteur coupe plus tôt plutôt que de réduire le corps (environ 20 caractères à 72 px en 9:16, ligne de 800 px). La coupure tombe entre deux groupes, sinon après une ponctuation, sinon au plus équilibré.
- **Tailles** (px) : carton 58 / 72 / 62 ; mot-choc 150 / 150 / 124 ; nom héros 124 / 132 / 116 ; nom discret 56 / 76 / 68 (16:9 / 9:16 / 1:1).
- **Zones sûres** : 9:16 : texte entre y = 230 et 1 498 px, x de 65 à 1 015 px, centre optique y = 864 ; 1:1 : marges de 86 px ; 16:9 : 80 % central.
- **Le nom** arrive en dernier : jamais avant 76 % du film (0 film produit sur 20 ne le montre avant).
- **La révélation** de l'objet entier : après 60 % du film (13 films sur 14).

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

| Champ | Sens |
|---|---|
| `id` | nom de la déclinaison (sert au nom du fichier) |
| `format` | `16:9`, `9:16` ou `1:1` |
| `duree_cible_s` | 15 à 60 s |
| `plans` | les plans retenus, dans l'ordre voulu : un `id`, ou `{ "id", "duree_s", "avec_nom", "sans_texte" }`. `avec_nom` (recette `revelation` ou `empilement`) : l'objet ou les écrans, puis le nom seul (≥ 2,5 s ; plan d'au moins 4 s, 4,5 à 5,5 s pour un empilement). `sans_texte` : retire le libellé d'un plan (moins de mots, jamais d'autres mots) |
| `regle` | `auto` à la place de `plans` : le moteur choisit selon le gabarit 15 / 30 / 45 / 60 s de `declinaisons.md` § 3.2. Accroche : un `mot-sur-image` de 4 mots au plus, sinon le carton-thèse (`role` `accroche`), sinon le carton de `role` `chute` ; en 20 s et moins, le plus court s'il fait 4 mots au plus. Un carton d'ouverture reçoit derrière lui le visuel du produit, flouté et voilé (image 0 pleine). Puis 0 à 2 groupes `contexte`, la `revelation` ou l'`empilement` qui en tient lieu (avec le nom jusqu'à 37 s), 1 à 4 groupes `preuve` (`priorite` 1 d'abord, ordre du film gardé), la `chute` (au-delà de 20 s, sauf après un carton) et la `fin`. Jusqu'à 37 s, une preuve qui a son carton perd ses libellés ; à 15 s, elle se réduit à son carton et à un plan |
| `musique_debut_s` | facultatif : où commencer dans la piste |

Règles appliquées par le moteur (conventions de `declinaisons.md`, § 3) :

- **Recomposer, pas recadrer.** Chaque format est sa propre composition HyperFrames (`data-width`, `data-height`). Les recettes recalculent leur mise en page : objet agrandi en 9:16, texte au-dessus de l'image, une ligne par groupe, etc.
- Les durées non données sont ajustées pour tomber sur `duree_cible_s`, sans passer sous le minimum de lecture d'un carton ni sous le minimum de la recette.
- Les plans `noir` sont retirés. Image 0 pleine : le premier plan n'entre pas par le noir, le premier carton est lisible à 0,2 s.
- Fin : pas de noir final de plus de 0,5 s (les plateformes rejouent en boucle).
- La durée réelle peut dépasser la cible quand les minimums de lecture l'imposent ; le contrôle bloque au-delà de ±10 %.

---

## 9. Exemple complet

Le fichier `assets/exemple-film.json` est l'exemple de référence : une lampe de bureau fictive (« Clarté »), muette, 16:9 de 65,3 s (17 plans), une déclinaison 9:16 de 30 s (liste explicite) et une 1:1 de 15,4 s (`regle: auto`). Le chiffre de `p10` n'est pas fourni : il s'affiche `[À FOURNIR]`, estompé. Ses visuels neutres sont dans `assets/exemple-visuels/`. En voici le texte intégral :

```json
{
  "version": 1,
  "meta": {
    "titre": "Clarté",
    "produit": "Clarté",
    "message": "Une lampe de bureau qui règle sa lumière toute seule, au fil de la journée.",
    "public": "Personnes qui travaillent à leur bureau toute la journée",
    "langue": "fr",
    "formats": ["16:9", "9:16", "1:1"],
    "duree_cible_s": 65,
    "fps": 30
  },
  "theme": {
    "source": "HEX d'exemple (produit fictif)",
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
      "notes": "Noir, un point de lumière s'allume puis s'éteint."
    },
    {
      "id": "p02", "recette": "lisere", "role": "accroche", "duree_s": 4.3,
      "visuels": { "objet": "exemple-visuels/lampe.png" },
      "notes": "On devine la lampe par son seul contour éclairé. L'objet entier reste caché."
    },
    {
      "id": "p03", "recette": "carton", "role": "accroche", "duree_s": 3.8, "fond": "sombre",
      "texte": { "type": "phrase", "contenu": "Une lampe qui suit votre journée." },
      "notes": "La phrase-thèse, en tête."
    },
    {
      "id": "p04", "recette": "macro", "role": "contexte", "duree_s": 3.0,
      "visuels": { "image": "exemple-visuels/matiere.jpg" },
      "mouvement": { "echelle": 1.6, "sens": "gauche", "point": [50, 70] },
      "notes": "Métal brossé et filet de lumière, la mise au point glisse."
    },
    {
      "id": "p05", "recette": "macro", "role": "contexte", "duree_s": 2.5,
      "visuels": { "image": "exemple-visuels/lampe.png" },
      "mouvement": { "echelle": 2.6, "sens": "droite", "point": [57, 5] },
      "notes": "L'articulation et la barre de lumière, de très près."
    },
    {
      "id": "p06", "recette": "carton", "role": "preuve", "groupe": "preuve-heure", "priorite": 1, "duree_s": 4.0, "fond": "clair",
      "texte": { "type": "phrase", "contenu": "Froide le matin. Chaude le soir.", "groupes": ["Froide le matin.", "Chaude le soir."], "affichage": "groupes" },
      "notes": "Proposition, puis sa chute."
    },
    {
      "id": "p07", "recette": "panneau", "role": "preuve", "groupe": "preuve-heure", "priorite": 1, "duree_s": 5.0, "fond": "clair",
      "visuels": { "capture": "exemple-visuels/appli-planning.png" },
      "texte": { "type": "libelle", "contenu": "Lumière du jour" },
      "mouvement": { "detail": { "zone": [52, 18, 40, 46], "mode": "zoom" } },
      "notes": "La courbe de la journée, puis on entre dans la fin d'après-midi."
    },
    {
      "id": "p08", "recette": "orbite", "role": "preuve", "groupe": "preuve-geste", "priorite": 2, "duree_s": 4.0, "fond": "clair",
      "visuels": { "objet": "exemple-visuels/piece-tete.png" },
      "mouvement": { "angle": 12 },
      "notes": "La tête de la lampe seule, qui tourne lentement."
    },
    {
      "id": "p09", "recette": "mot-sur-image", "role": "preuve", "groupe": "preuve-geste", "priorite": 2, "duree_s": 3.2,
      "visuels": { "image": "exemple-visuels/photo-bureau.jpg" },
      "texte": { "type": "phrase", "contenu": "Un seul geste." },
      "mouvement": { "zone": "gauche", "point": [70, 50] },
      "notes": "Le bureau le soir ; la phrase dans le mur sombre."
    },
    {
      "id": "p10", "recette": "carton", "role": "preuve", "groupe": "preuve-charge", "priorite": 3, "duree_s": 3.6, "fond": "sombre",
      "texte": { "type": "chiffre", "chiffre": null, "libelle": "heures de lumière par charge", "source": null },
      "notes": "Chiffre à fournir par l'utilisateur : rien n'est inventé."
    },
    {
      "id": "p11", "recette": "noir", "role": "respiration", "duree_s": 0.8,
      "notes": "Respiration avant le chapitre de l'application."
    },
    {
      "id": "p12", "recette": "empilement", "role": "preuve", "groupe": "preuve-appli", "priorite": 2, "duree_s": 4.5, "fond": "clair",
      "visuels": { "captures": ["exemple-visuels/fenetre-1.png", "exemple-visuels/fenetre-2.png", "exemple-visuels/fenetre-3.png"] },
      "texte": { "type": "libelle", "contenu": "Vos scènes" },
      "transition": "coupe",
      "notes": "Les fenêtres de l'application arrivent de la profondeur."
    },
    {
      "id": "p13", "recette": "mur", "role": "preuve", "groupe": "preuve-appli", "priorite": 2, "duree_s": 4.5, "fond": "sombre",
      "visuels": { "elements": ["exemple-visuels/scene-1.png", "exemple-visuels/scene-2.png", "exemple-visuels/scene-3.png", "exemple-visuels/scene-4.png", "exemple-visuels/scene-5.png", "exemple-visuels/scene-6.png", "exemple-visuels/scene-7.png", "exemple-visuels/scene-8.png"] },
      "mouvement": { "mode": "grille", "focus": 3 },
      "notes": "Les scènes de lumière ; la scène « lecture » s'allume."
    },
    {
      "id": "p14", "recette": "eclate", "role": "contexte", "duree_s": 5.2, "fond": "clair",
      "visuels": { "pieces": ["exemple-visuels/piece-base.png", "exemple-visuels/piece-tige.png", "exemple-visuels/piece-tete.png"] },
      "mouvement": { "axe": "vertical" },
      "transition": "noir",
      "notes": "Les trois pièces se rejoignent."
    },
    {
      "id": "p15", "recette": "revelation", "role": "revelation", "duree_s": 7.6, "fond": "sombre",
      "visuels": { "objet": "exemple-visuels/lampe.png" },
      "mouvement": { "recul": true, "halo": true },
      "transition": "noir",
      "notes": "L'objet entier, enfin : halo, lumière qui balaie, recul lent."
    },
    {
      "id": "p16", "recette": "carton", "role": "chute", "duree_s": 3.6, "fond": "sombre",
      "texte": { "type": "phrase", "contenu": "Votre bureau, enfin bien éclairé." },
      "notes": "La chute, juste avant le nom."
    },
    {
      "id": "p17", "recette": "fin", "role": "fin", "duree_s": 4.5, "fond": "sombre",
      "texte": { "type": "nom", "contenu": "Clarté", "ligne": "Bientôt disponible" },
      "mouvement": { "taille": "heros" },
      "notes": "Le nom seul, puis la ligne d'action et le logo."
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

## 10. Commandes

```bash
# 1. contrôler
python3 scripts/check_film.py film.json            # code 0 = aucun blocage ; 1 = erreurs

# 2. planche de validation (une image par plan, durée et texte), sans rendu
node scripts/build_film.js film.json --planche --sortie ./sortie

# 3. rendu (après validation de la planche)
node scripts/build_film.js film.json --rendu --sortie ./sortie            # film + déclinaisons
node scripts/build_film.js film.json --rendu --seulement vertical-30      # une seule sortie
node scripts/build_film.js film.json --rendu --qualite draft              # brouillon rapide
node scripts/build_film.js film.json --rendu --check                      # + npx hyperframes check (contraste WCAG, débordements)
```

- `check_film.py` est relancé par le moteur sur les sorties résolues (durées ajustées, lignes réelles). Une erreur arrête le rendu ; `--force` passe outre.
- Le moteur lance aussi `npx hyperframes lint` sur chaque projet. Les appels à HyperFrames se font sans télémétrie (`HYPERFRAMES_NO_TELEMETRY=1`) et `snapshot` sans description par un service externe (`--describe false`).
- Repères mesurés sur l'exemple (Mac, qualité `standard`, 30 i/s) : 33 s de calcul pour 65 s de film 16:9, 17 s pour 30 s en 9:16, 12 s pour 15 s en 1:1 ; planche : quelques secondes par sortie.

Sorties : `sortie/projets/<nom>/` (projets HyperFrames, ouvrables dans `npx hyperframes preview`), `sortie/planches/<nom>.png`, `sortie/rendus/<nom>.mp4`.
