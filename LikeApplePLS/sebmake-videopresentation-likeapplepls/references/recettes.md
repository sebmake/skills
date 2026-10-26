# Les recettes de plans

Un plan du film = une recette du moteur = une scène HyperFrames. Ce fichier dit, pour chacune des **12 recettes**, quand l'utiliser, quel visuel il faut, quels réglages existent, et donne un plan d'exemple pour `film.json`. Les noms sont exacts : `check_film.py` refuse toute autre valeur de `recette`.

Le format complet de `film.json` est dans `film-spec.md`. La grammaire (quand, combien, dans quel ordre) est dans `grammaire-film.md`.

Comptes : « N/14 » = films de révélation d'objet ; « N/12 » = films d'interface ; « N/33 » = textes ajoutés au montage. « Convention » = pas observé.

## Sommaire

1. Choisir une recette
2. Les champs communs à tous les plans
3. Les 12 recettes : `noir`, `lisere`, `macro`, `orbite`, `eclate`, `revelation`, `panneau`, `empilement`, `carton`, `mot-sur-image`, `mur`, `fin`
4. Les replis quand un visuel manque
5. Deux enchaînements types de 60 s, contrôlés
6. Les procédés observés qui n'ont pas de recette

---

## 1. Choisir une recette

### 1.1 Selon le visuel disponible

| Visuel fourni | Recettes possibles |
|---|---|
| Photo **détourée** de l'objet entier (PNG transparent) | `lisere`, `orbite`, `revelation`, `macro`, `eclate` (découpé en bandes) |
| Plusieurs vues détourées, angles proches | `orbite` (avec `vues`) |
| Pièces détourées, même cadre et même échelle | `eclate` (avec `pieces`) |
| Macro de matière ou de détail | `macro` |
| Photo d'ambiance ou d'usage, avec les droits | `mot-sur-image`, `macro` |
| Capture d'écran | `panneau`, `macro` (détail d'une capture) |
| Plusieurs captures de modules | `empilement` |
| Icônes, logos autorisés, vignettes | `mur` |
| Rien | `carton`, `noir`, `fin` |

Un enregistrement d'écran (vidéo) n'a pas de recette dans ce moteur : en tirer des captures fixes des moments clés (`ffmpeg -ss <temps> -i enregistrement.mp4 -frames:v 1 capture.png`).

### 1.2 Selon le temps du film

| Temps | Recettes typiques |
|---|---|
| Accroche | `noir` (avec point lumineux) → `lisere` ou `macro` ou `panneau` sans détail → `carton` (thèse) |
| Montée | `macro`, `orbite`, `eclate`, `panneau`, `empilement`, `mur`, `mot-sur-image`, `carton` (idée, chiffre fourni) |
| Respiration entre chapitres | `noir`, ou `transition: "noir"` sur le plan suivant |
| Révélation | `revelation` (objet) ; `empilement` pour un logiciel (plan d'ensemble des écrans, convention) |
| Chute | `carton` (phrase de 3 à 9 mots) |
| Fin | `fin` (toujours le dernier plan) |

---

## 2. Les champs communs à tous les plans

| Champ | Ce qu'il faut savoir |
|---|---|
| `id` | unique ; minuscules, chiffres, tirets (`p01`, `revel`) |
| `role` | `accroche`, `contexte`, `preuve`, `revelation`, `chute`, `respiration`, `fin`. Le moteur s'en sert pour choisir les plans des déclinaisons `auto` |
| `groupe` | des plans gardés ou retirés ensemble dans une déclinaison : un carton et le plan qui le prouve |
| `priorite` | 1, 2 ou 3 ; 1 = garder en premier dans une déclinaison courte |
| `duree_s` | durée dans le film long |
| `fond` | `sombre`, `clair`, `accent` (refusé si aucun texte ne s'y lit) ; chaque recette a son fond par défaut |
| `transition` | comment le plan **entre** : `coupe` (défaut, 14/14), `fondu` (0,4 s ; non vérifiable dans le corpus : à garder pour un passage continu, `grammaire-film.md` § 5.4), `noir` (le plan d'avant s'éteint en 0,4 s, celui-ci sort du noir en 0,5 s ; 10/14 films passent par le noir) |
| `notes` | l'intention du plan, pour la planche ; jamais affiché |

Règles de durée vérifiées par le moteur : chaque recette a une durée minimale (de 0,5 s pour `noir` à 3 s pour `eclate` et `revelation`), et chaque texte a sa durée de lecture. Le contrôle donne la valeur exacte, plan par plan : suivre ses messages plutôt que calculer à la main.

---

## 3. Les 12 recettes

### `noir` — passage par le noir

- **Quand** : ouvrir le film produit (avec le point lumineux) ; respirer entre deux chapitres ; poser un silence avant la révélation. Observé : noir 10/14, point lumineux 3/14 ; 100 noirs mesurés, médiane 0,65 s.
- **Visuel** : aucun.
- **Réglages** : `point` (vrai ou faux) : un point blanc, une lueur de la couleur d'accent et deux traits fins croisés, qui grandit puis s'éteint.
- **Durée** : 0,5 à 1,5 s.
- **Déclinaisons** : retiré automatiquement (l'image 0 doit être pleine).
- Pour un simple passage, `transition: "noir"` sur le plan suivant suffit. Le plan `noir` sert quand on veut tenir le noir, ou le point lumineux.

```json
{ "id": "p01", "recette": "noir", "role": "accroche", "duree_s": 1.0, "mouvement": { "point": true },
  "notes": "Noir, un point de lumière s'allume puis s'éteint." }
```

### `lisere` — l'objet dessiné par son contour éclairé

- **Quand** : l'accroche d'un film d'objet. On devine l'objet par son seul contour, avant de le montrer entier. Observé 3/14.
- **Visuel** : `objet`, une photo détourée (PNG transparent), 2 400 px de large ou plus.
- **Réglages** : `cote` (`gauche` ou `droite`) : le côté d'où vient la lumière.
- **Fond** : charbon, plus clair en haut (calculé depuis `fond_sombre`).
- **Durée** : 3 à 5 s.
- **Piège** : marche bien sur des formes arrondies ; sur une forme très longue, le liseré est inégal.

```json
{ "id": "p02", "recette": "lisere", "role": "accroche", "duree_s": 4.5,
  "visuels": { "objet": "visuels/objet-detoure.png" }, "mouvement": { "cote": "gauche" },
  "notes": "On devine l'objet par son contour. Il reste caché." }
```

### `macro` — très gros plan qui glisse

- **Quand** : l'accroche ou la montée : une matière, un détail, une pièce, une zone d'une capture. Observé 12/14 ; un plan macro dure 1,5 à 3 s.
- **Visuel** : `image`, une macro en haute définition (au moins 1,5 fois la taille affichée, soit 2 900 px de large pour un plein cadre agrandi), ou la photo détourée de l'objet, ou une capture.
- **Réglages** : `echelle` (1,2 à 3,5 ; plafonnée par le moteur à 1,5 fois la définition native) ; `sens` (`gauche`, `droite`, `haut`, `bas`) : le glissement de 8 % ; `point` (`[x, y]` en % de l'image) : le détail visé. La mise au point glisse : flou qui se retire en 1 s, puis bande nette (convention).
- **Texte** : un `libelle` (1 à 4 mots) possible.
- **Fond** : noir pour une photo, dégradé pour un objet détouré.
- **Durée** : 1,5 à 3 s.
- **Piège** : une image trop petite agrandie donne une matière molle.

```json
{ "id": "p04", "recette": "macro", "role": "contexte", "duree_s": 2.5,
  "visuels": { "image": "visuels/matiere.jpg" }, "mouvement": { "echelle": 2.2, "sens": "gauche", "point": [50, 70] },
  "notes": "La matière en lumière rasante." }
```

### `orbite` — rotation lente et lévitation

- **Quand** : montrer l'objet ou une pièce qui tourne lentement et flotte, dans la montée ou juste avant la révélation. Observé : rotation 8/14 (30 à 90° par plan, jamais un tour complet), lévitation 9/14.
- **Visuel** : `objet` (une vue : rotation limitée à ± 12°), ou `vues` : 2 à 5 vues détourées sous des angles proches (tous les 20 à 30°), même lumière, même échelle ; le moteur passe de l'une à l'autre en fondu.
- **Réglages** : `angle` (12 au plus) ; `sens` (1 ou −1).
- **Texte** : un `libelle` possible.
- **Fond** : clair.
- **Durée** : 3 à 6 s.
- **Piège** : une photo à plat tournée au-delà de ± 15° se voit comme une carte. Ne jamais promettre un tour complet.

```json
{ "id": "p10", "recette": "orbite", "role": "preuve", "groupe": "geste", "priorite": 2, "duree_s": 4.5,
  "visuels": { "vues": ["visuels/vue-face.png", "visuels/vue-34.png", "visuels/vue-profil.png"] },
  "mouvement": { "angle": 12, "sens": 1 }, "texte": { "type": "libelle", "contenu": "Tête orientable" } }
```

### `eclate` — les pièces se referment

- **Quand** : montrer ce qui compose l'objet ; souvent juste avant la révélation (l'assemblage tombe entre 60 et 85 % des films qui en ont un). Observé : éclaté 6/14, assemblage 7/14, sans rebond.
- **Visuel** : `pieces`, une liste de PNG détourés sur **la même toile** (même taille de fichier, chaque pièce à sa place dans l'objet assemblé), du bas vers le haut ; ou `objet` seul, que le moteur découpe en 3 à 6 bandes (couches extérieures seulement : aucun intérieur inventé).
- **Réglages** : `axe` (`vertical` : pile qui se resserre ; `profondeur` : pile 3D inclinée qui se remet de face) ; `bandes` (3 à 6, sans `pieces`).
- **Texte** : un `libelle` possible.
- **Fond** : clair.
- **Durée** : 4 à 6 s (assemblage de 1,4 à 2 s, puis l'objet tient au moins 1 s).

```json
{ "id": "p14", "recette": "eclate", "role": "contexte", "duree_s": 5.5,
  "visuels": { "pieces": ["visuels/piece-base.png", "visuels/piece-tige.png", "visuels/piece-tete.png"] },
  "mouvement": { "axe": "vertical" }, "notes": "Les trois pièces se rejoignent." }
```

### `revelation` — l'objet entier, enfin

- **Quand** : **la** révélation : le premier plan de l'objet entier, tenu. Une seule fois, après 60 % de la durée du film (13/14). Observé : plan médian de 5,5 s ; filet de lumière 4/14, halo 3/14, recul 6/14.
- **Visuel** : `objet`, la meilleure photo détourée (face ou trois-quarts).
- **Réglages** : `recul` (vrai par défaut : recul lent qui freine) ; `halo` (vrai par défaut : halo aux couleurs `accent` et `accent_2`, opacité 0,42 au plus). Le filet de lumière balaie l'objet une fois.
- **Texte** : `nom`, seulement dans une déclinaison avec `avec_nom` (l'objet s'efface, le nom arrive). Dans le film long, le nom va dans `fin`.
- **Fond** : sombre (reflet au sol) ; `clair` donne une ombre douce.
- **Durée** : 5 à 8 s ; 4 s au moins avec le nom.
- Souvent précédée de `transition: "noir"`.

```json
{ "id": "p15", "recette": "revelation", "role": "revelation", "duree_s": 8.0, "fond": "sombre",
  "visuels": { "objet": "visuels/objet-detoure.png" }, "mouvement": { "recul": true, "halo": true },
  "transition": "noir", "notes": "L'objet entier : halo, lumière qui balaie, recul lent." }
```

### `panneau` — l'interface sans appareil

- **Quand** : le plan de base d'un film de logiciel. Un écran entier en panneau flottant, puis on **entre** dans un détail (`zoom`) ou on l'**éclaire** (`projecteur`). Une fonction par plan. Observé : interface sans appareil 7/12, poussée vers un détail 6/12, aucune flèche ni encadré 0/12.
- **Visuel** : `capture`, une capture PNG à la définition native ou ×2 (bureau ou mobile, reconnu par le ratio). Flouter ou remplacer les données réelles sensibles avant ; garder l'heure réelle des captures. Pour un zoom, prévoir une capture au moins deux fois plus large que sa taille affichée.
- **Réglages** : `detail` : `{ "zone": [x, y, largeur, hauteur] en % de la capture, "mode": "zoom" ou "projecteur" }`. Sans `detail` : poussée lente.
  - `zoom` : la caméra entre dans la zone ; le reste de l'écran se floute et s'efface vers le fond, pour que le nom de fonction garde une zone calme. La zone doit être nettement plus petite que l'écran (moins de la moitié de sa largeur environ) : sinon le moteur signale « zoom limité ».
  - `projecteur` : tout le cadre s'assombrit (le reste tombe vers 20 % de sa luminance en 0,8 s : mesuré sur 1 passage), et l'élément isolé monte au centre de la zone image et grossit. Le nom de fonction passe en clair. C'est le mode à préférer en 9:16 pour un écran de bureau, qui y serait illisible en entier.
  - Après l'entrée dans le détail, la caméra continue de glisser lentement : jamais d'image figée.
- **Texte** : un `libelle`, le nom de la fonction (1 à 4 mots), posé à côté de l'écran : à 81 % de la largeur en 16:9, au-dessus en 9:16, dessous en 1:1.
- **Fond** : clair.
- **Durée** : 3 à 6 s (un sujet d'interface tient 3 à 4 s dans le film, 2 à 2,5 s dans une déclinaison ; 2 s au moins).
- **Piège** : en 9:16, un écran de bureau entier devient illisible ; mettre un `detail`.

```json
{ "id": "p07", "recette": "panneau", "role": "preuve", "groupe": "planning", "priorite": 1, "duree_s": 5.5,
  "visuels": { "capture": "visuels/planning.png" },
  "texte": { "type": "libelle", "contenu": "Vue de la semaine" },
  "mouvement": { "detail": { "zone": [10, 20, 40, 30], "mode": "zoom" } } }
```

### `empilement` — les fenêtres arrivent de la profondeur

- **Quand** : un espace de travail fait de plusieurs modules ; le plan d'ensemble d'un logiciel, qui peut tenir lieu de révélation (convention). Observé : assemblage 3/12, arrivée en 0,5 s ou moins.
- **Visuel** : `captures`, 2 à 5 captures de modules différents.
- **Réglages** : aucun. Avec `role: "revelation"`, le moteur ajoute un recul lent qui freine pendant tout le plan et un halo doux aux couleurs d'accent derrière les écrans (convention, sur le modèle de la révélation d'objet).
- **Texte** : un `libelle` possible. En déclinaison avec `avec_nom`, les écrans s'effacent et le nom arrive (plan de 4,5 à 5,5 s selon le nombre de captures).
- **Fond** : clair.
- **Durée** : 3,5 à 5 s ; jusqu'à 8 s quand il tient lieu de révélation.

```json
{ "id": "p12", "recette": "empilement", "role": "revelation", "duree_s": 6.0,
  "visuels": { "captures": ["visuels/accueil.png", "visuels/planning.png", "visuels/rapport.png"] },
  "transition": "noir" }
```

### `carton` — le texte seul sur fond uni

- **Quand** : la thèse, un carton d'idée (ouverture de chapitre), un mot-choc, un chiffre **fourni**, la chute. Le carton est un plan à lui : 23 textes sur 33.
- **Visuel** : aucun.
- **Texte** :
  - `phrase` : 12 mots au plus ; 6 au plus d'un bloc ; de 7 à 12, construite en 2 ou 3 groupes. `affichage` : `bloc`, `groupes` ou `mot-a-mot` ; `groupes` : la phrase découpée à la main, qui doit redonner `contenu` mot pour mot.
  - `mot` : 1 ou 2 mots, gros corps, gras. Un ou deux par film.
  - `chiffre` : `chiffre` (fourni, sinon `null`), `libelle` (avec la base de comparaison), `source`. Sans chiffre fourni, le carton affiche `[À FOURNIR]` estompé.
- **Fond** : sombre ; `clair` ; `accent` seulement si le texte s'y lit (le contrôle refuse sinon).
- **Durée du plan**, entrée et sortie comprises : au moins **1,8 s + 0,3 s par mot**, conseillé **2,1 s + 0,3 s par mot** (5 mots : 3,3 s au moins, 3,6 s conseillé). Mot-choc : environ 2,6 s. Construit : compter environ 0,8 s par groupe ajouté (0,4 s par mot en mot à mot).
- **Pièges** : deux cartons de suite sans image entre eux font un avertissement (sauf en film-texte, où on les sépare par un `noir` de 0,5 à 1 s). Casse de phrase, pas de point d'exclamation, pas de capitales.
- **Citation fournie** : pas de recette dédiée. Une `phrase` entre guillemets, 12 mots au plus, l'auteur compris ou dans le carton suivant ; seulement avec l'accord de la personne.

```json
{ "id": "p06", "recette": "carton", "role": "preuve", "groupe": "heure", "priorite": 1, "duree_s": 3.8, "fond": "clair",
  "texte": { "type": "phrase", "contenu": "Froide le matin. Chaude le soir.",
             "groupes": ["Froide le matin.", "Chaude le soir."], "affichage": "groupes" } }
```

```json
{ "id": "p10", "recette": "carton", "role": "preuve", "duree_s": 3.4, "fond": "sombre",
  "texte": { "type": "chiffre", "chiffre": null, "libelle": "heures de lumière par charge", "source": null },
  "notes": "Chiffre à fournir par l'utilisateur, avec sa source." }
```

### `mot-sur-image` — quelques mots dans la zone calme d'une image

- **Quand** : 1 à 4 mots sur une image forte et calme ; l'accroche d'une déclinaison, ou une preuve sur une photo d'usage. Observé 1 fois, en annexe : c'est presque une convention. Le carton sur fond uni reste la règle.
- **Visuel** : `image`, une photo dont l'utilisateur a les droits, avec une zone calme (ciel, nuit, mur, flou).
- **Réglages** : `zone` (`centre`, `haut`, `bas`, `gauche`, `droite`) : où poser le texte ; `point` (`[x, y]` en %) : le sujet à garder quand le moteur recompose en 9:16 et en 1:1.
- **Texte** : `phrase` (4 mots au plus conseillés) ou `mot`.
- **Fond** : l'image, en poussée lente, avec un voile local doux derrière le texte (jamais de boîte).
- **Durée** : 2,5 à 4 s.
- **Piège** : le contraste réel dépend de l'image. Viser 7:1 ; le vérifier avec `npx hyperframes check` (option `--check` du moteur).

```json
{ "id": "p09", "recette": "mot-sur-image", "role": "preuve", "duree_s": 3.4,
  "visuels": { "image": "visuels/bureau-le-soir.jpg" },
  "texte": { "type": "phrase", "contenu": "Un seul geste." }, "mouvement": { "zone": "gauche", "point": [70, 50] } }
```

### `mur` — une grille ou un défilé d'éléments

- **Quand** : des intégrations, des outils compatibles, des clients, une gamme. `grille` : la grille se remplit, puis un projecteur éclaire un élément ; `defile` : un élément à la fois, toutes les 0,5 s, fond alterné sombre et clair. Observé : défilé 1/12 (0,5 s mesuré), projecteur mesuré sur 1 passage.
- **Visuel** : `elements`, une liste de PNG (icônes, logos, vignettes) ; 6 à 12 pour un défilé. **Logos seulement s'ils sont fournis et autorisés.**
- **Réglages** : `mode` (`grille` ou `defile`) ; `focus` : le rang de l'élément éclairé, à partir de 1.
- **Texte** : un `libelle` possible.
- **Fond** : sombre.
- **Durée** : 3 à 6 s ; en défilé, 0,5 s par élément plus 1 s.

```json
{ "id": "p13", "recette": "mur", "role": "preuve", "duree_s": 4.5,
  "visuels": { "elements": ["visuels/scene-1.png", "visuels/scene-2.png", "visuels/scene-3.png", "visuels/scene-4.png", "visuels/scene-5.png", "visuels/scene-6.png"] },
  "mouvement": { "mode": "grille", "focus": 3 } }
```

### `fin` — le nom, seul

- **Quand** : le dernier plan de chaque sortie, film et déclinaisons. Le nom ferme le film (21 fois sur 24). Jamais en ouverture : le contrôle le refuse.
- **Visuel** : aucun ; le logo vient de `theme.logo`, seulement s'il est fourni.
- **Texte** : `nom`, avec `contenu` (le nom exact) et `ligne` facultative : une ligne d'action **fournie** (date, adresse, « bientôt disponible »). Ni slogan ni date inventés sous le nom (0/14).
- **Réglages** : `taille` : `heros` (par défaut ; 124 px en 16:9) ou `discret` (56 px). `discret` pour un objet, qui reste le héros (observé 2/2 films d'objet) ; `heros` pour un logiciel ou un service (observé 2/2 films d'interface). Ce partage est une convention.
- **Fond** : sombre.
- **Durée** : 3 à 4,5 s dans le film (fondu au noir final de 0,6 s) ; 2,5 à 3,5 s dans une déclinaison, sans noir final.

```json
{ "id": "p17", "recette": "fin", "role": "fin", "duree_s": 4.5, "fond": "sombre",
  "texte": { "type": "nom", "contenu": "Clarté", "ligne": "Bientôt disponible" }, "mouvement": { "taille": "discret" } }
```

---

## 4. Les replis quand un visuel manque

Un visuel absent ne bloque pas le travail : le moteur dessine un **repli neutre**, sans texte, sans chiffre et sans marque, et le signale dans la console et sur la planche.

| Emplacement manquant | Repli dessiné |
|---|---|
| `objet`, `pieces`, `vues` | un galet gris |
| `capture`, `captures` | un squelette d'interface gris |
| `image` | un dégradé sombre |
| `image` d'une `macro` | un métal brossé gris |
| `elements` | des tuiles arrondies |

Un film plein de replis est un brouillon. Chaque repli entre dans la liste des visuels à fournir, à la livraison.

---

## 5. Deux enchaînements types de 60 s, contrôlés

Ces deux suites passent `check_film.py` sans erreur. Les avertissements restants sont attendus : visuels absents, rotation sur une seule vue, chiffre non fourni, contraste réel sur image à vérifier, sélection automatique d'une déclinaison et, pour le logiciel, la part de texte. Elles servent de point de départ, pas de modèle à recopier : les plans viennent des visuels de l'utilisateur.

### 5.1 Objet, 60 s (révélation à 73 %, nom à 93 %)

| # | Recette | Rôle | Durée | Texte |
|---|---|---|---|---|
| 1 | `noir` (point) | accroche | 1,0 | — |
| 2 | `lisere` | accroche | 4,5 | — |
| 3 | `carton` | accroche | 3,6 | thèse, 5 mots |
| 4 | `macro` | contexte | 3,0 | — |
| 5 | `macro` | contexte | 2,0 | — |
| 6 | `orbite` (une vue) | preuve | 4,0 | libellé, 2 mots |
| 7 | `carton` (fond clair) | preuve | 3,6 | idée, 5 mots |
| 8 | `macro` | preuve | 2,2 | — |
| 9 | `mot-sur-image` | preuve | 3,4 | 3 mots |
| 10 | `orbite` (3 vues) | preuve | 4,5 | — |
| 11 | `noir` | respiration | 0,8 | — |
| 12 | `carton` | contexte | 3,6 | idée, 5 mots |
| 13 | `macro` | contexte | 2,5 | — |
| 14 | `eclate` (3 pièces) | contexte | 5,5 | — |
| 15 | `revelation` (`transition: noir`) | revelation | 8,0 | — |
| 16 | `carton` | chute | 3,6 | 5 mots |
| 17 | `fin` (discret) | fin | 4,5 | le nom |

Total 60,3 s ; 17 plans ; 7 textes, soit 7 par minute.

### 5.2 Logiciel, 60 s (ensemble à 76 %, nom à 92 %)

| # | Recette | Rôle | Durée | Texte |
|---|---|---|---|---|
| 1 | `noir` (point) | accroche | 1,2 | — |
| 2 | `panneau` sans détail | accroche | 4,3 | — |
| 3 | `carton` | accroche | 3,6 | thèse, 5 mots |
| 4 | `panneau` (`zoom`) | preuve | 5,5 | nom de fonction |
| 5 | `panneau` (`projecteur`) | preuve | 5,5 | nom de fonction |
| 6 | `carton` | contexte | 3,3 | idée, 4 mots |
| 7 | `mur` (grille, focus) | preuve | 5,0 | — |
| 8 | `panneau` (`zoom`) | preuve | 5,5 | nom de fonction |
| 9 | `carton` (chiffre `null`) | preuve | 3,4 | `[À FOURNIR]` + libellé |
| 10 | `panneau` sans texte | preuve | 5,0 | — |
| 11 | `macro` sur une capture | preuve | 2,5 | — |
| 12 | `noir` | respiration | 0,8 | — |
| 13 | `empilement` (`transition: noir`) | revelation | 6,0 | — |
| 14 | `carton` | chute | 3,9 | 6 mots |
| 15 | `fin` (héros) | fin | 4,5 | le nom |

Total 60,0 s ; 15 plans. Les noms de fonction restent à l'écran tout leur plan : un film de logiciel dépasse souvent 45 % de texte à l'écran, et le contrôle le signale. C'est un avertissement attendu ; le garder en connaissance de cause, ou retirer un nom de fonction.

### 5.3 Film-texte

Suite de `carton` (dont quelques-uns en `mot-a-mot`), séparés par des `noir` de 0,8 s, sur deux ou trois fonds qui changent par section, puis `fin`. Environ 13 fragments pour 60 s. Le contrôle signale une cadence et une part de texte au-dessus des conventions du film d'images : c'est attendu pour cette famille (le film-texte observé montre du texte 85 % du temps).

---

## 6. Les procédés observés qui n'ont pas de recette

| Procédé | Observé | Pourquoi pas de recette | À la place |
|---|---|---|---|
| L'image était l'écran (recul qui révèle qu'une image plein cadre est l'écran de l'objet) | 3/14 | demande un cadre d'appareil : risque d'appareil reconnaissable | `panneau` avec `zoom` |
| Tracé lumineux, gravure qui se dessine | 2 films | demande un SVG de l'utilisateur | `lisere` ou `macro` |
| Contre-jour et silhouettes | 3/14 | demande des personnes détourées et leur accord | ne pas faire |
| Plongée verticale, défilé des coloris, raccord de forme | 4/14, 4/14, 7/14 | pas encore écrits | coloris : `mur` en `defile` si les photos ont le même cadrage ; sinon `orbite` |
| Survol en parallaxe, vue technique, mains et filé | 1/14, 2/14, 7/14 | matériaux rares, risque de cotes inventées | ne pas faire |
| Même cadre, nouvel état ; défilement ; raccord par le contenu ; saisie ; curseur | 2 à 4/12 | pas encore écrits | deux `panneau` de suite sur deux captures ; `macro` sur une capture longue |
| Le mot fait ce qu'il dit | 5 cas dans 3 films | pas écrit | ne pas l'imiter avec un effet générique |

Un procédé absent peut s'ajouter à la main dans le projet HyperFrames produit (`sortie-…/projets/<nom>/compositions/<plan>.html`, en suivant la skill `hyperframes-core`), puis se rendre avec `npx hyperframes render`. Attention : relancer `build_film.js` réécrit le projet et efface la retouche. Le dire à l'utilisateur, et le noter à la livraison.
