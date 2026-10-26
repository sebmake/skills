# motion.json : le format de l'animation

Ce fichier décrit `motion.json`, la fiche qui dit **quoi animer** et **avec quelle recette**. Le générateur en tire un script After Effects (`.jsx`) qui construit l'animation, calque par calque, clé par clé.

La chaîne :

1. écrire `motion.json` (ce fichier dit comment) ;
2. le contrôler : `python3 scripts/check_motion.py motion.json` ;
3. générer le script : `node scripts/build_motion.mjs motion.json` (écrit `motion.jsx` à côté) ;
4. l'exécuter : dans After Effects (Fichier > Scripts > Exécuter le fichier de script), ou dans EffectCraft (`python3 scripts/ec.py script motion.jsx`) ;
5. regarder : images de contrôle (`ec.py frames`), puis rendu MP4 (`ec.py render`).

Les valeurs des recettes viennent de quatre analyses image par image de 8 keynotes (2019 à 2026) : texte (145 instances), objets (122), interfaces (189), transitions (182). Chaque recette porte ses comptes. Ce qui n'est pas mesuré est marqué **convention**. La skill reprend une grammaire du mouvement, jamais une marque : aucune image, police, logo ou signature d'une entreprise.

---

## 1. Unités

| grandeur | unité | exemple |
|---|---|---|
| temps | seconde, à partir de 0 | `"debut": 3.2` |
| position | % de la largeur et % de la hauteur, centre de l'élément | `"position": [50, 50]` = centre de l'image |
| taille, distance | **u** = 1 % du petit côté de l'image | 16:9 en 1920 × 1080 : 1 u = 10,8 px (c'est le « % H » des analyses) |
| largeur d'un front ou d'un bord | % de la largeur d'image (% L) | `"bord": 2.8` |
| échelle | facteur (× 1 = taille posée) | `"depart": 4.1` |
| angle | degré | `"angle": 90` |
| couleur | HEX `#RRGGBB`, ou un rôle du thème | `"couleur": "accent"` |

- Toutes les clés sont calées sur l'image et distantes d'au moins une image : deux clés à moins d'une image fusionnent dans EffectCraft.
- Le 9:16 et le 1:1 n'existent pas dans le corpus. Les tailles et distances en u y gardent les mêmes proportions : **convention**.

---

## 2. Le bloc `comp`

```json
"comp": { "nom": "lancement", "format": "16:9", "cadence": 30, "duree": 20, "fond": "fond", "epoque": "2024-2026" }
```

| champ | valeurs | défaut | rôle |
|---|---|---|---|
| `nom` | texte | `Motion` | nom de la composition ; relancer le script remplace la composition du même nom |
| `format` | `16:9` (1920 × 1080), `9:16` (1080 × 1920), `1:1` (1080 × 1080) | `16:9` | ou `largeur` et `hauteur` en px |
| `cadence` | 24, 25, 29,97, 30, 50, 60 | 30 | images par seconde |
| `duree` | secondes | 10 | durée de la composition |
| `fond` | HEX ou rôle | `fond` | couleur de fond de la composition (sous tous les calques) |
| `epoque` | `2024-2026` ou `2019-2020` | `2024-2026` | choisit les courbes de montage (zoom, rangée, défilement, voile) ; une recette d'une autre époque est signalée |

Pourquoi l'époque : la courbe d'arrivée des zooms, glissades et rangées change d'une époque à l'autre (21 instances en 2019-2020, 56 en 2024-2026), et le chiffre dépasse de 5 % en 2020 (6 sur 6) mais jamais en 2025-2026 (18 sur 18). Choisir une époque et s'y tenir : **convention**.

---

## 3. Le bloc `theme`

```json
"theme": {
  "couleurs": { "fond": "#0E1013", "texte": "#F4F4F2", "secondaire": "#9A9CA3", "accent": "#4C8DFF", "voile": "#000000" },
  "polices": { "titre": ["Inter-SemiBold", "Inter-Bold", "Arial-BoldMT"], "texte": ["Inter-Regular", "ArialMT"],
               "chiffre": ["Inter-Bold", "Arial-BoldMT"], "surtitre": ["Inter-Medium", "ArialMT"] },
  "tailles": { "titre": 10, "phrase": 5.4 },
  "approche": { "titre": -10 }
}
```

- **Couleurs par rôle.** Rôles reconnus : `fond`, `texte`, `secondaire` (surtitre, libellé), `accent`, `voile` (assombrissement), `lumiere` (filet de lumière), `repli` et `repli_trait` (dessin de remplacement). Un élément prend un rôle ou un HEX dans `couleur`.
- **Polices avec repli.** Chaque rôle (`titre`, `texte`, `chiffre`, `surtitre`) donne une liste de noms PostScript, du préféré au repli. After Effects 24 et plus prend le premier nom installé (`app.fonts`). Les autres versions et EffectCraft prennent le premier nom : mettre en tête une police installée. EffectCraft fournit Inter (Regular, Medium, SemiBold, Bold).
- Une police propre à une marque (famille système d'un fabricant, par exemple) est refusée par le contrôle.
- **Tailles par défaut** (u) : titre 10, phrase 5,4, surtitre 3,2, liste 4,4, chiffre 30, libellé 3,7, logo 12, image 50, capture 60, icône 10, forme 20. Le chiffre héros mesure 30 à 50 % H dans le corpus ; les autres tailles sont une **convention**.
- **Approche** (tracking, en millièmes de cadratin) par type : titre −10, chiffre −20, le reste 0 (**convention**).

---

## 4. Les éléments

`elements` est la liste des choses à l'écran, **de l'arrière vers l'avant** : le premier est dessous.

### 4.1 Champs communs

| champ | rôle |
|---|---|
| `id` | nom unique ; il sert aux liens et au nom des calques (`titre — Un objet…`) |
| `type` | `titre`, `phrase`, `surtitre`, `liste`, `chiffre`, `logo`, `image`, `capture`, `icone`, `forme`, `fond`, `nul-camera` |
| `contenu` ou `fichier` | le texte (`\n` pour aller à la ligne), ou le chemin d'une image (relatif au motion.json) |
| `position` | `[x %, y %]` du centre ; défaut `[50, 50]` |
| `taille` | en u : corps du texte, ou hauteur de l'image |
| `couleur` | HEX ou rôle du thème |
| `recette` | l'animation d'entrée (§ 5) ; défaut `coupe` |
| `debut` | instant où la recette commence |
| `maintien` | temps pendant lequel l'élément reste après la fin de son entrée |
| `fin` | instant de la sortie (prioritaire sur `maintien`) ; sans l'un ni l'autre, l'élément reste jusqu'au bout |
| `sortie` | `coupe` (défaut) ou `fondu` |
| `options` | réglages de la recette (§ 5), seulement s'il faut s'écarter des valeurs mesurées |
| `puis` | compléments joués après l'entrée : `[{ "recette": "balayage-lumiere", "decalage": 1.1, "options": {…} }]` |
| `avec` | id de l'élément principal, pour un élément qui arrive avec lui (recette `avec`) |
| `parent` | id d'un `nul-camera` : l'élément suit ses mouvements |
| `profondeur` | pour la parallaxe sous une caméra globale : 1 = premier plan (défaut), 0,5 = deux fois plus lent |
| `camera` | `false` : l'élément ne suit pas la caméra globale (un titre fixe, par exemple) |
| `simultane` | `true` : autorise un mouvement majeur en même temps qu'un autre (le contrôle l'interdit sinon) |

**La sortie.** 15 sorties de texte sur 18 sont des coupes ; les 3 autres sont des fondus (0,90 à 0,93 s de 10 à 90 %). Aucune sortie ne bouge, ne rétrécit ni ne floute (0 sur 18). Le format n'offre donc que `coupe` et `fondu` (linéaire, 1,15 s). Pour un départ animé, utiliser une transition (§ 6).

### 4.2 Champs par type

| type | champs propres | notes |
|---|---|---|
| `titre`, `phrase` | `contenu`, `police` (rôle), `alignement` (`centre`, `gauche`, `droite`), `interligne` (u) | `carton-groupes` demande `groupes` : `["Pensé pour", "durer", "longtemps."]` |
| `surtitre` | `contenu`, `avec` | le surtitre n'a pas d'animation à lui : recette `avec` |
| `liste` | `lignes` (une chaîne par ligne), `alignement` (défaut `gauche`), `interligne` (u, défaut 1,7 × corps) | le bloc est centré sur `position` ; les lignes s'alignent à gauche du bloc |
| `chiffre` | `contenu`, `libelle`, `source`, `taille_libelle`, `couleur_libelle`, `position_libelle` | une valeur inconnue s'écrit `"[À FOURNIR]"` ; un chiffre sans `source` est refusé |
| `image`, `capture`, `icone`, `logo` | `fichier`, `ratio` (largeur / hauteur du repli) | un fichier qui manque laisse un **repli neutre** : un cadre arrondi et ses deux diagonales, au bon format. Un `logo` absent avec un champ `nom` est remplacé par ce nom, en texte |
| `capture` + `empilement` | `fichiers` (deux écrans au moins) | un écran par fichier, arrivés l'un après l'autre |
| `image` + `eclate` | `pieces` : `[{ "fichier" ou "largeur", "taille", "position": [dx u, dy u], "direction": [dx u, dy u] }]` | `position` : place de la pièce assemblée, par rapport au centre ; `direction` : décalage à l'ouverture. Sans pièces : trois plaques de repli |
| `forme` | `forme` (`rect` ou `rond`), `largeur` (u), `taille` (hauteur, u), `coins` (u), `contour` | pour un panneau schématique, une carte, une pastille |
| `fond` | `couleur` ou `fichier` | une image de fond couvre tout le cadre ; le fond ne suit pas la caméra, sauf `"camera": true` |
| `nul-camera` | `position` (point d'ancrage), `recette` de caméra ou `zoom-detail` | un nul neutre (ancre = position) ; les éléments s'y rattachent par `parent` |

### 4.3 Les liens

- `avec` : l'élément prend le début, la recette, les options et la sortie de l'élément nommé. Usage : surtitre au-dessus d'un titre, mention sous un logo de fin.
- `options.nom` (recette `nom-remonte`) : le nom qui remonte quand le libellé et le prix entrent dessous.
- `options.ancien` (recettes `mot-remplace`, `mot-fondu-enchaine`, `mot-glisse`) : le mot qui s'en va.
- `parent` : un `nul-camera`.

### 4.4 Les compléments (`puis`)

Trois recettes se posent en plus de l'entrée, sur le même élément :

| complément | ce qu'il fait | quand |
|---|---|---|
| `assombrir-autour` | un voile noir tombe sur tout ce qui est sous l'élément ; option `flou` : le fond se floute en même temps | souvent après l'arrivée d'un panneau |
| `balayage-lumiere` | un filet de lumière traverse l'objet une fois, en ligne droite | quand l'objet vient de se poser |
| `revelation-lumiere` | l'objet sort du noir (ou s'éteint, `"sens": "eteint"`) ; option `eclat` : il s'allume un peu trop avant de se poser | à la coupe, 0,2 à 0,4 s après |

Le moment : `"a": 4.1` (absolu), ou `"decalage": 1.1` (après le `debut` de l'élément). Sans l'un ni l'autre, le complément part à la fin de l'entrée.

---

## 5. Les recettes

Une recette = une animation mesurée. Ses options ont un **défaut** (la médiane ou la valeur commune du corpus), une **fourchette** et un **statut** : `m` (mesuré : un réglage hors fourchette est une erreur au contrôle) ou `conv.` (convention : un réglage différent est permis, signalé). « Majeur » : la recette déplace ou agrandit l'élément ; deux mouvements majeurs ne se chevauchent pas (§ 7).

Les durées : `T` = durée d'une clé à l'autre ; `d1090` = durée mesurée entre 10 et 90 % de la progression (le générateur en déduit `T` par la courbe) ; `visible` = entre 2 et 98 %.

#### Commun

| recette | types | majeur | époque | options : défaut · fourchette · statut |
|---|---|---|---|---|
| `coupe` | tous | non | toutes | — |

#### Texte

| recette | types | majeur | époque | options : défaut · fourchette · statut |
|---|---|---|---|---|
| `avec` | surtitre, phrase, titre, icone | non | toutes | `ecart` 0 · -0,06–0,06 s · m |
| `titre-fondu-montee` | titre, phrase, chiffre | oui | 2024-2026 | `T_opacite` 0,77 · 0,64–0,77 s · m<br>`T_position` 0,92 · 0,92–1,17 s · m<br>`retard_position` 0,3 · 0,26–0,31 s · m<br>`montee` 15,3 · 7,4–15,5 u · m<br>`flou` 0 · 0–0,4 u · conv. |
| `titre-fondu` | titre, phrase, surtitre | non | toutes | `d1090` 0,43 · 0,27–0,71 s · m |
| `titre-balayage` | titre, phrase | non | 2024-2026 | `T` 0,6 · 0,33–0,86 s · m<br>`bord` 2,8 · 2,8–6,3 % L · m |
| `phrase-zoom-arriere` | phrase, titre | oui | 2019-2020 | `depart` 8 · 7,5–8,1 × · m<br>`T_echelle` 0,42 · 0,4–0,45 s · m<br>`d1090_opacite` 0,35 · 0,33–0,37 s · m<br>`flou` 5 · 4,4–6,7 u · m |
| `chute` | phrase, chiffre, titre | oui | 2019-2020 | `T` 0,23 · 0,2–0,27 s · m<br>`hauteur` 68 · 45–75 u · m |
| `phrase-par-le-bas` | phrase | oui | 2019-2020 | `T` 0,65 · 0,6–0,7 s · m<br>`depart` 58 · 50–60 u · m |
| `liste-cascade` | liste | oui | 2024-2026 | `decalage` 0,1 · 0,093–0,113 s · m<br>`T_opacite` 1,14 · 1–1,17 s · m<br>`T_position` 1,17 · 0,98–1,17 s · m<br>`montee` 21 · 18–23 u · m |
| `liste-cascade-rapide` | liste | oui | 2024-2026 | `decalage` 0,05 · 0,029–0,066 s · m<br>`T_opacite` 0,75 · 0,64–0,83 s · m<br>`montee` 4 · 0–4,1 u · m<br>`T_position` 1 · 1–1,02 s · m |
| `liste-par-le-bas` | liste | oui | 2019-2020 | `decalage` 0,37 · 0,362–0,377 s · m<br>`T` 0,65 · 0,63–0,67 s · m<br>`depart` 31 · 27–35 u · m |
| `liste-au-fil` | liste | oui | 2024-2026 | `intervalle` 2 · 1,4–3,6 s · m<br>`T_opacite` 1,17 · 1,1–1,2 s · m<br>`T_position` 0,95 · 0,9–1 s · m<br>`montee` 15 · 14–17 u · m |
| `nom-remonte` | phrase, chiffre | oui | toutes | `T_nom` 0,5 · 0,45–0,53 s · m<br>`remontee` 10 · 7,4–10,7 u · m<br>`d1090_opacite` 0,3 · 0,22–0,41 s · m<br>`montee` 10 · 6–14 u · m |
| `mot-remplace` | titre, phrase, surtitre | non | toutes | — |
| `mot-fondu-enchaine` | titre, phrase, surtitre | non | 2024-2026 | `d1090_ancien` 0,5 · 0,45–0,55 s · m<br>`d1090_nouveau` 0,47 · 0,42–0,52 s · m<br>`ecart` 0,61 · 0,55–0,65 s · m<br>`flou` 1,5 · 0–3 u · conv. |
| `mot-glisse` | titre, phrase, surtitre | non | 2019-2020 | `d1090_ancien` 0,22 · 0,2–0,25 s · m<br>`d1090_nouveau` 0,2 · 0,18–0,23 s · m<br>`ecart` 0,16 · 0,14–0,18 s · m<br>`glisse` 6 · 3–10 u · conv. |
| `chiffre-pose` | chiffre, titre | oui | 2024-2026 | `depart` 4,1 · 1,9–8 × · m<br>`T_echelle` 0,67 · 0,25–0,8 s · m<br>`d1090_opacite` 0,2 · 0,18–0,62 s · m<br>`flou` 6,7 · 1,1–6,7 u · m<br>`retard_libelle` 0,23 · 0,19–0,3 s · m<br>`d1090_libelle` 0,27 · 0,26–0,27 s · m |
| `chiffre-croissance` | chiffre | oui | 2019-2020 | `depart` 0,22 · 0,19–0,37 × · m<br>`T_echelle` 0,83 · 0,72–0,88 s · m<br>`d1090_opacite` 0,22 · 0,2–0,24 s · m<br>`retard_libelle` 0,26 · 0,16–0,29 s · m<br>`d1090_libelle` 0,11 · 0,1–0,15 s · m |
| `carton-fondu` | titre, phrase | non | toutes | `d1090` 0,45 · 0,31–0,78 s · m |
| `carton-groupes` | phrase | non | toutes | `ecart` 0,75 · 0,6–2,5 s · m<br>`d1090` 0,45 · 0,31–0,78 s · m<br>`T_recentrage` 0,3 · 0,2–0,5 s · conv. |

#### Objets et produits

| recette | types | majeur | époque | options : défaut · fourchette · statut |
|---|---|---|---|---|
| `produit-entree` | image, capture, icone, logo, forme | oui | 2024-2026 | `T` 0,9 · 0,82–0,93 s · m<br>`depuis` droite  · m<br>`obturateur` 120 · 74–169 ° · m |
| `produit-poussee` | image, capture, icone, logo, forme, nul-camera | non | toutes | `facteur` 1,27 · 1,02–2,58 × · m<br>`duree` 4,1 · 2,2–8,6 s · m |
| `produit-recul` | image, capture, icone, logo, forme, nul-camera | non | toutes | `facteur` 0,45 · 0,05–0,84 × · m<br>`duree` 5,8 · 2,7–8,5 s · m |
| `produit-pivot` | image, capture, icone, logo, forme | oui | toutes | `angle` 90 · 12–90 ° · m<br>`T` 2 · 1,7–2,6 s · m<br>`delai` 0,25 · 0,2–0,3 s · m |
| `produit-rotation` | image, capture, icone, logo, forme | non | toutes | `angle` 83 · 19–160 ° · m<br>`duree` 4,2 · 1,4–9,5 s · m |
| `produit-flotte` | image, capture, icone, logo, forme | non | toutes | `derive` 0 · 0–10 u/s · conv.<br>`ombre` 1 · 0–1  · conv. |
| `eclate` | image, forme | oui | toutes | `sens` ouvre  · m<br>`T_ouvre` 1,9 · 0,2–18,8 s · m<br>`T_ferme` 1,2 · 1,1–2,8 s · m<br>`amplitude` 1 · 0,5–3 × · conv.<br>`decalage` 0 · 0–3,15 s · conv. |
| `balayage-lumiere` | image, capture, icone, logo, forme, titre | non | 2024-2026 | `T` 0,28 · 0,1–1,17 s · m<br>`largeur` 31 · 5–32 % objet · m<br>`sens` droite  · m<br>`intensite` 45 · 20–80 % · conv.<br>`inclinaison` 20 · 0–35 ° · conv. |
| `revelation-lumiere` | image, capture, icone, logo, forme | non | toutes | `d1090` 1,6 · 0,1–6 s · m<br>`delai` 0,3 · 0,2–0,4 s · m<br>`sens` allume  · m<br>`eclat` 0 · 0–28 % · m |

#### Écrans et interfaces

| recette | types | majeur | époque | options : défaut · fourchette · statut |
|---|---|---|---|---|
| `panneau-pose` | capture, forme, image, icone | oui | toutes | `visible` 0,36 · 0,17–0,5 s · m<br>`distance` 40 · 15,9–62 u · m<br>`depuis` bas  · m<br>`dans_la_page` 0 · 0–1  · m<br>`carte` 0 · 0–1  · m<br>`fondu` 1 · 0–1  · conv. |
| `zoom-detail` | capture, image, nul-camera | oui | toutes | `facteur` 2,2 · 1,45–3 × · m<br>`T` 0,95 · 0,6–1,53 s · m<br>`sens` entre  · m<br>`point` [50, 50] % · conv. |
| `defilement` | capture | oui | toutes | `distance` 59,5 · 14–196 u · m<br>`T` 1,07 · 0,94–2,16 s · m<br>`mode` presentation  · m<br>`fenetre` [60, 60] u · conv. |
| `empilement` | capture | oui | toutes | `intervalle` 1,67 · 0,83–10,5 s · m<br>`T` 0,79 · 0,6–1 s · m<br>`ecart` 4 · 2–8 u · conv. |
| `assombrir-autour` | image, capture, icone, logo, forme, titre, phrase, surtitre, chiffre, liste | non | toutes | `niveau` 40 · 5–73 % · m<br>`T` 0,53 · 0,4–0,6 s · m<br>`flou` 0 · 0–0,78 u · m |

#### Caméra (nul-camera ou bloc camera)

| recette | types | majeur | époque | options : défaut · fourchette · statut |
|---|---|---|---|---|
| `camera-poussee` | nul-camera | non | toutes | `facteur` 1,27 · 1,02–2,58 × · m |
| `camera-recul` | nul-camera | non | toutes | `facteur` 0,45 · 0,05–0,84 × · m |
| `camera-travelling` | nul-camera | non | toutes | `vitesse` 4,7 · 0,5–48 u/s · m<br>`direction` [-1, 0]  · conv. |
| `camera-se-pose` | nul-camera | non | toutes | `d1090` 4,4 · 2,1–5,2 s · m<br>`facteur` 0,68 · 0,46–1 × · m<br>`deplacement` [0, 0] u · conv. |

#### Fin

| recette | types | majeur | époque | options : défaut · fourchette · statut |
|---|---|---|---|---|
| `logo-fin` | logo, titre, image | non | toutes | `entree` fondu  · m<br>`d1090` 0,65 · 0,27–2 s · m |

#### Transitions

| transition | options : défaut · fourchette · statut |
|---|---|
| `coupe` | — |
| `raccord` | — |
| `fondu-enchaine` | `T` 0,54 · 0,25–0,98 s · m |
| `passage-noir` | `T_fondu` 0,5 · 0,33–1,27 s · m<br>`noir` 0,5 · 0,4–1,5 s · m |
| `fondu-au-noir` | `T` 0,5 · 0,33–1,27 s · m |
| `fondu-depuis-noir` | `T` 0,5 · 0,34–2,71 s · m |
| `montee-du-noir` | `noir` 0,27 · 0,1–0,5 s · conv.<br>`d1090` 0,39 · 0,17–0,74 s · m |
| `glissade` | `T` 0,89 · 0,64–0,94 s · m<br>`sens` gauche  · m |
| `poussee` | `T` 0,75 · 0,6–1,02 s · m<br>`sens` gauche  · m |
| `bascule-lumiere` | `T` 2,4 · 1,2–2,6 s · m<br>`niveau` 85 · 30–100 % · conv. |

Les comptes de chaque recette sont dans `scripts/recettes.json` (champ `mesure`) et dans `node scripts/build_motion.mjs --liste`.

### 5.1 Ce que font les recettes, en une ligne

**Texte**
- `coupe` : l'élément est là, plein, à la première image. C'est le cas le plus fréquent (14 titres sur 29).
- `avec` : arrive avec l'élément nommé (le surtitre avec son mot : 8 sur 11).
- `titre-fondu-montee` : le titre fond (easeInOutCubic, 0,77 s) et monte de 15 u (easeOutExpo, 0,92 s), la montée 0,30 s après le début du fondu.
- `titre-fondu` : fondu sur place, courbe ease.
- `titre-balayage` : le mot se dévoile de gauche à droite derrière un front flou (cache rectangulaire flouté, linéaire).
- `phrase-zoom-arriere` : la phrase naît huit fois trop grande et floue, puis se pose (ease, 0,42 s).
- `chute` : tombe d'en haut en accélérant (easeInQuad, 0,23 s), sans rebond.
- `phrase-par-le-bas` : entre d'en dessous, déjà opaque.
- `liste-cascade` : une ligne toutes les 0,10 s, chacune fond et monte en même temps (l'opacité part avec la montée : la ligne se voit monter) ; les lignes se chevauchent.
- `liste-cascade-rapide` : une ligne toutes les 0,05 s, petite montée.
- `liste-par-le-bas` : lignes opaques qui montent depuis le bas, toutes les 0,37 s (juin 2020).
- `liste-au-fil` : une ligne quand elle est dite (`intervalle`, ou `options.temps` : la liste des instants) ; le bloc remonte d'une demi-interligne à chaque ajout.
- `nom-remonte` : le nom (`options.nom`) remonte de 10 u ; le libellé et le prix fondent et montent dessous.
- `mot-remplace` : l'ancien mot disparaît sur l'image où le nouveau apparaît.
- `mot-fondu-enchaine` : l'ancien floute et s'efface, le nouveau apparaît (1 cas).
- `mot-glisse` : l'ancien monte en s'effaçant, le nouveau arrive dessous (1 cas).
- `chiffre-pose` : le chiffre naît ×4 et flou, se pose sans dépasser ; le libellé suit : le milieu de son fondu (0,27 s) vient 0,23 s après celui du chiffre. Le chiffre ne compte jamais (0 sur 27).
- `chiffre-croissance` : le chiffre grandit depuis ×0,22, dépasse de 5 % et revient (juin 2020).
- `carton-fondu` : carton de film, fondu linéaire, sans mouvement (7 sur 7).
- `carton-groupes` : la phrase se construit par groupes de sens ; la ligne se recentre à chaque ajout.

**Objets**
- `produit-entree` : arrive par la droite sur la coupe, freine (out-cubic, 0,9 s), avec un flou de bougé d'obturateur 120°.
- `produit-poussee` : l'objet grandit lentement, à vitesse constante, pendant toute sa présence.
- `produit-recul` : l'objet rapetisse en freinant (ease-out).
- `produit-pivot` : calque 3D qui tourne du profil (90°) à la face, à vitesse constante, 0,25 s après la coupe. Avec une image plate, partir de 70° pour que l'objet reste visible.
- `produit-rotation` : rotation dans le plan, lente et partielle (aucun tour complet sur 17).
- `produit-flotte` : **aucune clé sur la position** (le produit en lévitation ne bouge pas : 10 tenues sur 13) ; une ombre douce au sol ; option `derive` : une dérive linéaire lente (**convention**). L'oscillation de flottement n'existe pas dans le corpus (0 sur 14).
- `eclate` : les pièces s'écartent en freinant (ease-out, 1,9 s) ou se referment à vitesse constante (1,2 s).
- `balayage-lumiere`, `revelation-lumiere` : voir § 4.4.

**Interfaces**
- `panneau-pose` : un panneau arrive d'un bord (out-expo) ou glisse dans la page (ease), en 0,36 s visibles ; aucun au-delà de 0,5 s.
- `zoom-detail` : l'échelle et la position vont ensemble vers un point (`options.point`) avec la courbe de l'époque, en 0,95 s. Sur une capture, `point` est en % de l'image ; sur un `nul-camera`, en % de la composition. Rester ensuite 2,5 à 7 s sur le détail (**convention** tirée des maintiens mesurés).
- `defilement` : la capture défile derrière une fenêtre fixe (`options.fenetre` : largeur et hauteur en u) ; `mode` : `presentation` (en S), `geste` (lancé, long freinage), `continu` (linéaire, 68 u/s).
- `empilement` : les écrans arrivent un par un par la droite et la rangée se recentre ; jamais deux arrivées à la fois.
- `assombrir-autour` : voir § 4.4.

**Caméra** (sur un `nul-camera`, ou dans le bloc `camera`)
- `camera-poussee` : avancée linéaire du début à la fin.
- `camera-recul` : recul qui freine.
- `camera-travelling` : translation à vitesse constante ; la `profondeur` des éléments fait la parallaxe.
- `camera-se-pose` : le mouvement ralentit jusqu'à l'arrêt (out-cubic).

**Fin**
- `logo-fin` : le nom ou le logo arrive par une coupe ou par un fondu (out-quad, 0,65 s de 10 à 90 %), sans bouger.

---

## 6. Les transitions

```json
"transitions": [
  { "type": "passage-noir", "temps": 16.4, "de": ["panneau"], "vers": ["logo", "mention"] }
]
```

| champ | rôle |
|---|---|
| `type` | une transition du tableau du § 5 |
| `temps` | début de la transition |
| `de` | éléments qui s'en vont ; leur sortie est réglée par la transition |
| `vers` | éléments qui arrivent ; leur entrée est avancée ou retardée par la transition (leur recette est en général `coupe`) |
| `options` | réglages (§ 5, tableau des transitions) |

| transition | ce qu'elle fait |
|---|---|
| `coupe` | les `de` s'arrêtent à `temps`. C'est le cas général : plus de 95 % des changements d'image |
| `raccord` | une coupe où la forme garde sa place et sa taille (22 raccords sur 22 sont des coupes) |
| `fondu-enchaine` | les `de` fondent à 0 et les `vers` à leur opacité, linéaire, 0,54 s ; jamais plus d'1 s |
| `passage-noir` | fondu au noir linéaire 0,5 s, noir 0,5 s (jamais moins de 0,40 s), fondu depuis le noir 0,5 s |
| `fondu-au-noir` | fondu au noir linéaire jusqu'à la fin |
| `fondu-depuis-noir` | l'image monte du noir ; linéaire si court, freinée (out-cubic) au-delà de 0,68 s |
| `montee-du-noir` | coupe au noir, noir court (0,27 s), puis l'image monte du noir en douceur (in-out-cubic) |
| `glissade` | les `de` partent d'une largeur d'image sur le côté, les `vers` arrivent de l'autre côté, avec flou de bougé ; horizontal seulement |
| `poussee` | même geste dans un cadre fixe, plus court (0,75 s) |
| `bascule-lumiere` | le fond s'éteint lentement (in-out-sine) sous les éléments ; `options.fond` : l'élément `fond` au-dessus duquel poser le voile |

---

## 7. Les règles que le contrôle fait respecter

`check_motion.py` lit le motion.json, demande le plan temporel exact au générateur (`build_motion.mjs --plan`) et rend un rapport. Une **erreur** bloque (code de sortie 1) ; un **avertissement** et une **info** non.

| règle | niveau | appui |
|---|---|---|
| recette, transition, type, lien inconnus ; id en double | erreur | — |
| option hors de la fourchette mesurée | erreur | la fourchette du corpus (§ 5) |
| option hors d'une convention | avertissement | — |
| deux mouvements majeurs qui se chevauchent, hors éléments liés (`avec`, `options.nom`, `options.ancien`, `parent`, `de`/`vers` d'une même transition) et hors `simultane` | erreur | rangées : 0 recouvrement sur 11 ; le libellé suit son chiffre (15 sur 18) |
| deux transitions qui se chevauchent | erreur | 25 sur 25 |
| arrivées d'une rangée, ou lignes au fil de la voix, qui se recouvrent | erreur | 11 sur 11 |
| sortie autre que `coupe` ou `fondu` | erreur | 0 sortie animée sur 18 |
| balayage vers le bas, ou deux balayages sur un même élément | erreur | 0 sur 11 ; un seul passage, 11 sur 11 |
| voile à 75 % ou plus | erreur | jamais jusqu'au noir, 20 sur 20 |
| glissade verticale | erreur | horizontal 32 sur 32 |
| chiffre sans `source` | erreur | aucun chiffre sans source |
| `[À FOURNIR]` restant | avertissement | à remplir avant diffusion |
| texte visible moins de 1,2 s + 0,3 s par mot | avertissement ; erreur sous 60 % de ce temps | **convention** de lecture |
| trop de mots (titre 6, phrase 12, surtitre 4, ligne 6, libellé 5) ; ligne trop large (estimation 0,55 × corps par signe) | avertissement | **convention** ; aucune instance mesurée au-delà de 12 mots |
| surtitre animé seul | avertissement | 8 sur 11 arrivent avec leur mot |
| recette d'une autre époque que `comp.epoque` | avertissement | **convention** |
| moins de 2,5 s sur un détail après un zoom ; nom de fin tenu moins de 1,25 s | avertissement | maintien médian 7,2 s ; 2,6 s (17 noms) |
| fichier absent | avertissement | un repli neutre sera dessiné |
| contraste texte / fond sous 4,5:1 | avertissement | **convention** de lisibilité |
| fond vide visible (de la coupe à 2 % d'opacité : `debut` plus le départ doux de la courbe) sous 0,10 s | info | le fond vide tient 0,13 à 0,23 s (135 cas) ; seule l'entrée latérale part sur la coupe (8 sur 8) |
| fond vide visible au-delà de 0,30 s avant un texte ou un logo qui fond | avertissement | même appui ; tolérance de 0,30 s : **convention** |
| nom de fin hors de 47 à 51 % de la hauteur | info | 15 sur 20 |

---

## 8. Exemple complet

`assets/exemple-motion.json` : 20 s, 16:9, neutre et fictif. Le script généré est à côté (`assets/exemple-motion.jsx`), les images dans `assets/exemple/`.

| temps | ce qui se passe | recette |
|---|---|---|
| 0,1 – 3,0 s | un surtitre et un titre fondent et montent ensemble | `avec` + `titre-fondu-montee` |
| 3,0 – 6,4 s | coupe ; l'objet entre par la droite, flou de bougé ; la caméra avance de ×1,05 ; un filet de lumière le traverse à 4,1 s | `produit-entree`, `camera-poussee`, `balayage-lumiere` |
| 6,45 – 9,6 s | trois lignes en cascade | `liste-cascade` |
| 9,8 – 12,4 s | le chiffre [À FOURNIR] naît grand et flou et se pose ; son libellé suit | `chiffre-pose` |
| 12,6 – 16,9 s | un panneau d'interface schématique monte du bas ; zoom ×2 sur l'interrupteur | `panneau-pose`, `zoom-detail` |
| 16,4 – 17,9 s | passage par le noir | `passage-noir` |
| 17,4 – 20,0 s | le logo fictif et sa mention, posés à la coupe, immobiles | `logo-fin` + `avec` |

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
    { "id": "surtitre", "type": "surtitre", "contenu": "Nouveau", "position": [50, 41], "taille": 3.2, "couleur": "accent", "recette": "avec", "avec": "titre" },
    { "id": "titre", "type": "titre", "contenu": "Un objet, rien de plus.", "position": [50, 50], "taille": 9, "recette": "titre-fondu-montee", "debut": 0.1, "fin": 3.0 },
    { "id": "cam-produit", "type": "nul-camera", "position": [50, 50], "recette": "camera-poussee", "debut": 3.0, "fin": 6.4, "options": { "facteur": 1.05 } },
    { "id": "produit", "type": "image", "fichier": "exemple/produit.png", "position": [50, 52], "taille": 72, "ratio": 0.64, "parent": "cam-produit",
      "recette": "produit-entree", "debut": 3.0, "fin": 6.4,
      "puis": [ { "recette": "balayage-lumiere", "decalage": 1.1, "options": { "T": 0.5, "sens": "gauche" } } ] },
    { "id": "liste", "type": "liste", "lignes": ["Léger.", "Silencieux.", "Fait pour durer."], "position": [50, 50], "taille": 6, "alignement": "gauche",
      "recette": "liste-cascade", "debut": 6.45, "fin": 9.6 },
    { "id": "chiffre", "type": "chiffre", "contenu": "[À FOURNIR]", "libelle": "heures d'autonomie", "source": "[À FOURNIR]", "position": [50, 46], "taille": 14,
      "recette": "chiffre-pose", "debut": 9.8, "fin": 12.4 },
    { "id": "cam-panneau", "type": "nul-camera", "position": [50, 50], "recette": "zoom-detail", "debut": 13.3, "options": { "facteur": 2.0, "point": [64.2, 60.1] } },
    { "id": "panneau", "type": "capture", "fichier": "exemple/panneau.png", "position": [50, 52], "taille": 56, "ratio": 1.5, "parent": "cam-panneau",
      "recette": "panneau-pose", "debut": 12.6, "fin": 16.9, "options": { "depuis": "bas" } },
    { "id": "logo", "type": "logo", "fichier": "exemple/logo.png", "nom": "exemple", "position": [50, 49], "taille": 9, "ratio": 4.2,
      "recette": "logo-fin", "debut": 17.4, "fin": 20, "options": { "entree": "coupe" } },
    { "id": "mention", "type": "phrase", "contenu": "Bientôt disponible.", "position": [50, 59], "taille": 2.8, "couleur": "secondaire", "recette": "avec", "avec": "logo", "fin": 20 }
  ],
  "transitions": [
    { "type": "passage-noir", "temps": 16.4, "de": ["panneau"], "vers": ["logo", "mention"] }
  ]
}
```

Le contrôle de cet exemple rend 0 erreur et 1 avertissement (le chiffre est encore à fournir).

---

## 9. Le script généré

### 9.1 Sa forme

- **ExtendScript ES3** : `var` et `function` seulement ; ni `let`, `const`, fonction fléchée, gabarit, ni JSON natif ni méthode de tableau ES5. Il n'utilise que l'API objet d'After Effects (`app.project.items.addComp`, `layers.addText/addShape/addSolid/addNull`, noms internes « ADBE … », `setValueAtTime`, `KeyframeEase`, `setTemporalEaseAtKey`, `ImportOptions`…). Le générateur vérifie la syntaxe et ces interdits à chaque génération.
- **En tête** : la liste des recettes, et la table des courbes utilisées avec leur traduction (influence et vitesse de chaque clé) et leurs comptes.
- **Le moteur** (`md_…`) : une vingtaine de fonctions courtes. `md_anime(propriété, t0, v0, t1, v1, courbe)` pose deux clés et calcule les `KeyframeEase` depuis la cubic-bezier : on peut changer une courbe ou une valeur à la main dans le script.
- **Sept phases**, commentées : calques de l'arrière vers l'avant ; parentage ; animations ; présence des calques (entrée, sortie) ; transitions ; lumières (elles copient l'élément animé, d'où leur place à la fin) ; caméra.
- **Noms propres** : chaque calque porte `id — rôle` (`produit — filet de lumière`, `[REPLI] panneau …` pour un repli). Chaque recette pose un **repère de calque** au début de son animation, qui dit la recette, la courbe et la durée : c'est le nom des clés.
- **Rapport** : le script rend « N calques, M clés » et la liste des replis.
- **Fichiers** : chaque image est cherchée d'abord à côté du script (After Effects connaît le dossier du script), puis à son chemin absolu au moment de la génération (EffectCraft). `--relatif` n'écrit pas de chemin absolu, pour partager un script ; sur une autre machine, régénérer le script.

### 9.2 Pièges respectés

| piège | parade dans le script |
|---|---|
| EffectCraft ignore interpolations et eases sur une composition qui n'est pas active (constaté le 21/10) | la composition est ouverte dans la visionneuse (`comp.openInViewer()`) avant toute clé |
| les clés neuves sont linéaires ; une `KeyframeEase` seule ne change rien | le type BEZIER est posé avant les eases |
| deux clés à moins d'une image fusionnent | temps calés sur l'image, au moins une image d'écart |
| une propriété à plusieurs dimensions attend un `KeyframeEase` par dimension (Échelle : 3) | `md_anime` compte les dimensions de la propriété |
| la position spatiale mêle les axes | position en dimensions séparées : X et Y sont deux propriétés à une dimension |
| parenter compense la transformation du parent | nuls de caméra posés neutres (ancre = position) et parentés avant leurs clés : rien ne bouge |
| un calque de forme compte ses sommets depuis son point d'ancrage | formes dessinées autour de l'ancre (0, 0), placées par la position |
| l'expansion de masque n'est pas rendue ; une requête sur un masque animé a bloqué l'app | aucun masque : le balayage d'un titre, la fenêtre d'un défilement et les lumières passent par des caches (track matte) |
| un calque trop large (~27 000 px) n'est plus dessiné | aucun calque plus large que la diagonale de l'élément × 1,2 ou que l'image |
| `File.exists` répond faux dans EffectCraft même quand le fichier existe | l'import est tenté ; s'il échoue, un repli neutre est dessiné |
| les polices manquantes ne se signalent pas | liste de polices avec repli ; After Effects 24 et plus choisit la première installée |
| le réglage « Flou » du flou gaussien | mesuré dans EffectCraft : réglage = 2 × σ (2,00 ; 1,98 ; 1,97 pour 10, 20, 40). Dans After Effects : à vérifier à l'œil (**convention**) |
| projet de l'utilisateur | aucune commande de fichier : le script n'enregistre, n'ouvre ni ne ferme rien ; il remplace seulement la composition de même nom |

---

## 10. Commandes

```bash
python3 scripts/check_motion.py motion.json                 # contrôle (code 1 s'il y a une erreur)
node scripts/build_motion.mjs motion.json                   # écrit motion.jsx
node scripts/build_motion.mjs motion.json --prefixe TEST-   # même script, composition préfixée (essais)
node scripts/build_motion.mjs --liste                       # recettes et transitions, avec leurs comptes
node scripts/build_motion.mjs --recettes                    # régénère scripts/recettes.json (lu par le contrôle)

# EffectCraft (lancer l'app avec : open -a EffectCraft --args --control 9877)
python3 scripts/ec.py activer                               # premier plan : l'app ne répond qu'ainsi
python3 scripts/ec.py script motion.jsx                     # exécute le script
python3 scripts/ec.py frames "lancement" controle/ --pas 0.5 --max 640   # une image toutes les 0,5 s
python3 scripts/ec.py frame "lancement" 4.3 image.png 1920  # une image
python3 scripts/ec.py render "lancement" rendu.mp4          # rendu H.264 (attend la fin)
```

`ec.py` refuse les commandes qui enregistrent, ouvrent ou ferment le projet, sauf avec `--autoriser`. Chaque requête a un délai (`--delai`, 180 s ; 1 800 s pour un rendu) : une app bloquée ne bloque pas le terminal. `--relance` remet l'app au premier plan et renvoie la requête une fois.

---

## 11. Ce que ce format ne fait pas (conventions et limites)

- Pas de son : le corpus est muet ; aucun lien entre le mouvement et la musique n'est mesuré.
- Pas de compteur, de rebond répété, de machine à écrire, de rotation de texte, de tour complet : rien de cela n'existe dans le corpus (0 sur 145 textes ; 0 sur 17 rotations).
- Le flottement sinusoïdal n'existe pas non plus (0 sur 14) : `produit-flotte` n'anime pas l'objet.
- La fumée d'une chute, la mise au point qui glisse, le décalage entre pièces d'un éclaté, l'intensité du flou des glissades : non mesurés, non reproduits ou posés par **convention**.
- Le 9:16 et le 1:1 : aucun observé ; mêmes valeurs en u (**convention**).
- After Effects n'a pas servi aux essais : le script n'utilise que l'API objet commune et a été exécuté dans EffectCraft : l'exemple et six compositions d'essai couvrent les 39 recettes et les 10 transitions, images de contrôle et rendu MP4 regardés.
