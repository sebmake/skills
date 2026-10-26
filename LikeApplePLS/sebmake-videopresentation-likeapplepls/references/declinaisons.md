# Les déclinaisons réseaux

Ce fichier dit comment tirer du film produit des versions courtes (15, 30, 45, 60 s) pour les réseaux, en 16:9, en vertical 9:16 et, en option, en carré 1:1. La grammaire de base est dans `grammaire-film.md`, les plans dans `recettes.md`, le format de `film.json` dans `film-spec.md`.

**Statut.** Les 51 films du corpus sont tous en 16:9 (dont 1 en format cinéma). Aucun film vertical ni carré n'est observé : **toute règle sur le 9:16 et le 1:1 est une convention.** La forme courte en 16:9 est observée : 6 films de révélation sur 8 durent de 21,5 à 34,5 s.

## Sommaire

1. Le principe : un script, plusieurs mises en page
2. Les 2 premières secondes
3. Les gabarits 15, 30, 45 et 60 s
4. Formats, zones sûres et tailles
5. Recomposer chaque élément
6. Le carton de fin
7. La musique des déclinaisons
8. Ce qui est interdit
9. Liste de contrôle

---

## 1. Le principe : un script, plusieurs mises en page

- **On recompose, on ne recadre pas.** Chaque format est sa propre composition : HyperFrames lit la largeur et la hauteur une seule fois, à la compilation. On ne rend jamais le 16:9 pour le recouper ensuite.
- **Un seul script.** Les cartons, leurs mots et l'ordre des plans sont les mêmes dans tous les formats d'une même durée. Seules la coupure des lignes et la mise en page changent.
- **Tout vient du film long.** Une déclinaison prend ses plans et ses cartons dans le film produit. Elle ne crée aucun contenu nouveau, sauf l'ordre et la coupure des lignes. Si un carton est trop long pour le format, on prend un autre carton du film, on ne le résume pas.
- **Destination → format** (d'après les skills HyperFrames) : site et YouTube → 16:9 ; Reels, Shorts, TikTok, stories → 9:16 ; fil carré (LinkedIn, Instagram, X) → 1:1, seulement si l'utilisateur le vise.
- Le film produit se fait d'abord, en 16:9. Les déclinaisons viennent après, une fois sa structure validée.

---

## 2. Les 2 premières secondes

Un fil d'actualité se joue dans sa première seconde. Les ouvertures observées font l'inverse : 5 sur 8 démarrent sur du noir, un fondu lent ou un carton fixe, et aucune (0/8) ne combine image forte, texte et mouvement dès la première seconde. C'est juste pour une salle qui attend, faux pour un fil. D'où ces conventions :

1. **Image 0 pleine**, jamais du noir. Pas de fondu depuis le noir (0,2 s au plus).
2. **Un carton lisible à 0,2 s** : 2 à 4 mots, au corps d'accroche (§ 4.3). Le fil est regardé son coupé : sans voix, c'est le texte qui accroche.
3. **Du mouvement dès la première seconde** : la lumière passe, l'objet tourne, le plan pousse.
4. **Le produit, ou son effet, visible avant 3 s.** Un détail reconnaissable suffit (macro, élément d'interface seul) ; l'objet entier peut garder sa révélation.
5. **On ouvre par la chute.** La phrase-thèse du film long passe au début. Elle dit ce que le public gagne, dans ses mots, jamais une liste de fonctions.
6. **Pas de logo en ouverture** : le nom ferme le film (observé 21 fois sur 24 textes de nom ou de logo).

Trois accroches compatibles avec la grammaire observée :

| Accroche | Ce que c'est | Observé |
|---|---|---|
| Phrase-thèse en deux temps | une proposition, puis sa chute, sur l'image la plus forte | en tête de 4 films sur 11 à cartons-message |
| Détail mystère | un gros plan qu'on ne reconnaît pas, qui s'ouvre sur l'objet | macro → objet entier dans les films de matière |
| Mot-choc | un ou deux mots, gros, sur l'image la plus forte | 5 fois, dans des bandes-annonces |

Non observés dans les films, donc à éviter : la question rhétorique, l'« avant / après » en accroche.

---

## 3. Les gabarits 15, 30, 45 et 60 s

### 3.1 Le film long découpé en rôles

Les gabarits puisent dans les rôles du film produit (convention, construite sur les temps observés) :

| Rôle | Dans le film produit |
|---|---|
| T1 Ouverture | l'accroche, et son carton-thèse s'il existe |
| T2 Contexte | le premier carton d'idée et ses images |
| T3 Révélation | le plan de l'objet entier (ou de l'ensemble des écrans) |
| T4 à T6 Preuves | un carton d'idée ou un nom de fonction, et le plan qui le prouve |
| T7 Chute | la phrase de chute, ou la thèse |
| T8 Nom et fin | le carton du nom |

### 3.2 Les gabarits

Durées en secondes. « Cartons » compte tous les textes, nom et carton de fin compris. Les budgets de mots sont des totaux (environ 62 mots par minute au plus) : tous les cartons ne peuvent pas être au maximum de 6 mots.

| Format | Déroulé | Pris dans | Cartons | Mots au plus |
|---|---|---|---|---|
| **15 s** | 0–2,5 accroche (image forte + thèse de 2 à 4 mots) · 2,5–6,5 révélation (objet 1,5 s, puis nom 2,5 s) · 6,5–11,5 une preuve (plan 2 s + carton de 6 mots au plus, 3 s) · 11,5–15 fin (3,5 s) | T7 en tête, T3, la meilleure preuve, T8 | **4** | **16** |
| **30 s** | 0–2,5 accroche · 2,5–7 contexte (1 carton) · 7–11 révélation et nom · 11–23 deux preuves (6 s chacune : plan 2 à 3 s, carton 3 s) · 23–26,5 chute courte · 26,5–30 fin | T7, T2, T3, deux preuves, T7 raccourci, T8 | **7** | **32** |
| **45 s** | 0–2,5 accroche · 2,5–8 contexte (1 ou 2 cartons) · 8–13 révélation (nom facultatif) · 13–34 trois preuves (7 s chacune) · 34–39,5 chute en deux temps · 39,5–45 fin | T1 ou T7, T2, T3, T4 à T6, T7, T8 | **9 à 10** | **45** |
| **60 s** | 0–2,5 accroche · 2,5–10 contexte (2 cartons) · 10–16 révélation (nom facultatif) · 16–46 trois ou quatre preuves (7,5 à 10 s), avec **une rupture de rythme vers 30 s** (mot seul ou passage sans texte) · 46–54 chute en deux temps · 54–60 fin | tout le film long, raccourci | **12 à 14** | **60** |

- Dans les déclinaisons, le nom peut apparaître une première fois à la révélation (convention : on ne sait pas qui regardera jusqu'au bout). Le moteur le fait d'office jusqu'à 37 s ; au-delà, c'est au choix (`avec_nom`). Il revient toujours à la fin. Jamais en ouverture.
- Repère observé pour la forme 30 s en 16:9 : accroche 3 à 6 s, montée 13 à 20 s, révélation 4 à 9 s, nom 3 s, 4 à 13 plans (6 films de révélation sur 8). Les gabarits ci-dessus la resserrent pour le fil : accroche plus courte, produit visible plus tôt.

### 3.3 Selon la famille du film

| Famille | Ce qui change dans les déclinaisons (convention) |
|---|---|
| Révélation d'objet | 30 s = un mouvement de révélation + le nom ; 60 s = deux mouvements. Préférer les plans à forme verticale : macros, rotations, lévitation. |
| Logiciel | Ouvrir sur le détail de la fonction la plus forte (`macro` sur une capture, ou `panneau` en `zoom`), avec la thèse ; puis 8 à 10 plans de 1,5 à 2,5 s, un nom de fonction sur chaque plan ; finir sur le nom. En 60 s : un court passage enchaîné en fondu (environ 12 s) et, si elles sont fournies, 2 citations entre 30 et 45 s. |
| Usage | Garder le rythme rapide du montage ; la chute et le nom tels quels. |
| Film-texte | Garder un fragment à la fois ; en 9:16, un groupe de sens par ligne. |

### 3.4 Règles de coupe

- **Plans plus courts** que dans le film long : 1,2 à 2,5 s par plan d'image, sauf sous un carton (convention ; repère observé : 1,5 à 1,6 s dans les bandes-annonces).
- **Un carton dure au moins sa durée de lecture** (`grammaire-film.md` § 6.4), même dans une déclinaison de 15 s : le moteur ne descend jamais en dessous, quitte à dépasser un peu la durée visée.
- **Les mêmes mots** que le film long.
- Garder les preuves **les plus visibles** : celles dont le plan se comprend son coupé et en petit.
- Le 9:16 et le 1:1 suivent le même déroulé que le 16:9 de même durée ; seule la mise en page change (§ 5).
- Le 1:1 est facultatif.

### 3.5 Dans `film.json`

Une déclinaison est une entrée de `declinaisons` (détail dans `film-spec.md` § 8). Deux façons de la décrire :

- **`"regle": "auto"`** : le moteur choisit les plans selon le gabarit de la durée. Il prend, dans l'ordre : l'accroche (un `mot-sur-image` de 4 mots au plus, sinon le carton-thèse de rôle `accroche`, sinon le carton de `chute` ; en 20 s et moins, le plus court des deux s'il fait 4 mots au plus ; sinon un plan d'`accroche` qui n'est pas du noir), 0 à 2 groupes de `contexte`, la `revelation` ou l'`empilement` qui en tient lieu (avec le nom si la durée fait 37 s ou moins), 1 à 4 groupes de `preuve` par `priorite` croissante, la `chute` (au-delà de 20 s, sauf si le plan d'avant est déjà un carton) et la `fin`. Jusqu'à 37 s, une preuve qui a son carton perd ses noms de fonction ; en 15 s, elle se réduit à son carton et à un plan.
- **`"plans": [...]`** : la liste voulue, dans l'ordre. Un `id`, ou `{ "id", "duree_s", "avec_nom", "sans_texte" }`. `avec_nom: true` sur un plan `revelation` fait arriver le nom à la fin du plan (4 s au moins). `sans_texte: true` retire le nom de fonction d'un plan : moins de mots, jamais d'autres mots.

Pour que `auto` choisisse bien, le film long doit être bien étiqueté :

- chaque plan a son `role` ;
- un carton et le plan qui le prouve partagent un `groupe` : ils restent ou partent ensemble ;
- les preuves les plus visibles (lisibles son coupé et en petit) ont `priorite: 1` ;
- un `mot-sur-image` de 4 mots au plus sur l'image la plus forte fait une bonne ouverture de déclinaison.

Ce que le moteur fait seul : il retire les plans `noir`, fait entrer le premier plan sans noir et son texte dès 0,2 s, pose le visuel du produit, flouté et voilé, derrière un carton d'ouverture (image 0 pleine, convention), ajuste les durées pour tomber sur `duree_cible_s` sans passer sous la lecture d'un carton ni sous le minimum d'une recette, et supprime le noir final. `musique_debut_s` choisit où le morceau commence.

Commencer par `auto`, regarder la planche, puis passer à une liste `plans` si un choix ne convient pas.

---

## 4. Formats, zones sûres et tailles

### 4.1 Les formats

| Format | Taille | Usage |
|---|---|---|
| 16:9 | 1920 × 1080 | film produit ; déclinaison pour site et YouTube |
| 9:16 | 1080 × 1920 | Reels, Shorts, TikTok, stories |
| 1:1 | 1080 × 1080 | fil carré, en option |

### 4.2 Les zones sûres

Tout le texte, le nom et le détail du produit qui porte la preuve restent dans la zone sûre. L'image (fond, objet, plan) peut déborder partout.

| Format | Zone pour le texte et le détail clé | Source |
|---|---|---|
| 16:9 | les 80 % du centre : marges de 192 px à gauche et à droite, 108 px en haut et en bas | skill HyperFrames `embedded-captions` |
| 9:16 | en hauteur, de 12 à 78 % (y de 230 à 1 498 px) : les 22 % du bas sont couverts par l'interface des réseaux ; en largeur, de 65 à 1 015 px, ligne de 800 px au plus, centrée (20 caractères à 72 px) | hauteur : skill HyperFrames ; largeur : convention (la colonne de boutons à droite, non vérifiée) |
| 1:1 | marges de 86 px (8 %) sur les 4 côtés | convention |

- **Centre optique en 9:16** : y ≈ 864 px (45 % de la hauteur, milieu de la zone sûre), au lieu de 960 px. Le carton centré se pose là (convention).
- Pas de bande vide réservée en bas : le texte est sur l'image, pas sous elle.

### 4.3 Les tailles de texte

Corps de police en px. La première valeur est celle que le moteur pose ; la fourchette entre parenthèses est la plage admise.

| Rôle | 16:9 (1920 × 1080) | 9:16 (1080 × 1920) | 1:1 (1080 × 1080) |
|---|---|---|---|
| Carton-message | 58 (52–64) | 72 (64–84) | 62 (56–72) |
| Nom, version discrète | 56 (52–64) | 76 (72–90) | 68 (64–80) |
| Nom, version héros | 124 (110–140) | 132 (120–150) | 116 (110–130) |
| Mot-choc, accroche | 150 (130–170) | 150 (130–170) | 124 (110–140) |
| Nom de fonction | 68 | 76 | 64 |
| Ligne d'action, mention | 34 (32 au moins) | 42 (40 au moins) | 38 (36 au moins) |

- 16:9 : observé (médiane 5 % de la hauteur pour un message, 9 à 14 % pour un nom héros). 9:16 et 1:1 : convention, appuyée sur les planchers des skills HyperFrames pour le vertical (corps 65 à 95 px, accroche 130 à 170 px) et le fil (corps de 32 px au moins).
- Un mot long doit tenir : corps maximal ≈ largeur utile ÷ (lettres du mot le plus long × 0,6), en regular.
- Petit et posé, même en vertical : le gros corps reste réservé au nom et à un ou deux mots-chocs.

### 4.4 Les lignes

- Au plus 42 caractères par ligne en 16:9, 22 en 9:16, 26 en 1:1 (convention).
- En 9:16, un carton tient sur 2 ou 3 lignes, coupées entre deux groupes de sens. Un carton construit met **chaque groupe sur sa propre ligne** ; les lignes s'ajoutent dessous.
- On réécrit la coupure des lignes, jamais les mots.

---

## 5. Recomposer chaque élément

| Élément | 16:9 (référence) | 9:16 | 1:1 |
|---|---|---|---|
| Carton centré sur fond uni | centré, 1 ligne | centré à 45 % de la hauteur, 2 à 3 lignes par groupes de sens | centré, 1 à 2 lignes |
| Carton construit par groupes | groupes sur la même ligne | un groupe par ligne | 2 lignes au plus |
| Objet seul sur fond uni | petit, centré, beaucoup de vide | objet à 55–75 % de la largeur, dans la bande de 25 à 65 % de la hauteur ; fond prolongé | objet à 50–65 % de la largeur |
| Objet et texte côte à côte | objet d'un côté, texte de l'autre | **empilés** : objet en haut (18 à 55 % de la hauteur), texte dessous (58 à 74 %) | côte à côte si le texte fait 3 mots au plus ; sinon empilés |
| Écran de bureau entier (panneau) | panneau à 72 % de la largeur | illisible : 1,5 s au plus, puis entrer dans un détail | panneau entier, texte dessous |
| Écran mobile et nom de fonction | écran au centre, nom à droite | nom au-dessus (vers 20 % de la hauteur), écran à 50 % de la hauteur, au-dessus de la limite des 78 % | nom dessous (vers 88 % de la hauteur), écran à environ 66 % de la hauteur |
| Image plein cadre (ambiance, photo, vidéo) | plein cadre | recadrer sur le sujet s'il tient dans 32 % de la largeur d'origine ; sinon poser l'image en bande centrale (1080 × 608) et le texte dans la zone unie au-dessus | recadrer sur le sujet (56 % de la largeur d'origine) |
| Texte posé sur image | dans une zone calme | chercher la zone calme du nouveau cadre ; sinon sortir le texte en carton sur fond uni, avant ou après le plan | idem |
| Chiffre fourni | chiffre centré, libellé dessous | même pile ; chiffre à 70 % de la largeur au plus | même pile |
| Mouvement de caméra | travelling latéral | devient vertical, ou un zoom lent | zoom lent |
| Bandes noires de cinéma | permises (observées en 2019 seulement) | supprimées : plein cadre | supprimées |
| Nom final | centré | centré à 45 % de la hauteur ; logo dessous s'il est fourni, jamais dans les 22 % du bas | centré |

Toutes ces règles de recomposition sont des conventions. Le moteur les applique recette par recette : on ne règle rien à la main, on vérifie sur la planche.

---

## 6. Le carton de fin

- Observé dans le film long : le nom seul, centré, 1,25 à 3,4 s (médiane 2,7 s), parfois précédé d'une phrase de chute à la même place ; puis noir ou logo, 1 à 2 s.
- Dans une déclinaison (convention) :
  - 2,5 à 3,5 s, immobile après un fondu d'entrée de 0,3 s au plus ;
  - **le nom**, et **une seule ligne d'action** (adresse, date, « disponible … ») **si elle est fournie** ; sinon `[À FOURNIR]` dans le storyboard, ou rien ;
  - le logo seulement s'il est fourni ;
  - tout dans la zone sûre ;
  - **pas de noir final de plus de 0,5 s** : les réseaux rejouent la vidéo en boucle, et un long noir casse la reprise.
- Le carton de fin compte dans le budget de mots.

---

## 7. La musique des déclinaisons

- Le même fichier que le film produit, fourni par l'utilisateur, ou aucune musique. Jamais une autre musique.
- On peut faire démarrer le morceau plus loin (`musique_debut_s` de la déclinaison), pour que la première seconde ait déjà de l'énergie (convention).
- Le fondu de sortie est celui de `musique.fondu_sortie_s` (2 s par défaut) ; il finit avec le carton de fin.
- Une déclinaison sans musique reste valable : le fil est souvent regardé son coupé.

---

## 8. Ce qui est interdit

Conventions, toutes :

- rendre le 16:9 et le rétrécir dans un 9:16 avec des bandes ;
- remplir les bandes avec l'image floutée et agrandie : signe de « repost » ;
- couper un mot ou une ligne de carton pour la faire tenir ;
- changer les mots d'un format à l'autre ;
- ouvrir sur du noir, sur le logo ou sur le nom ;
- inventer un chiffre, un avis, une date ou une ligne d'action.

---

## 9. Liste de contrôle d'une déclinaison

- [ ] Image 0 pleine, carton lisible à 0,2 s, mouvement dans la première seconde.
- [ ] Produit (ou son effet) visible avant 3 s ; nom à la révélation et en fin, jamais en ouverture.
- [ ] Chaque carton : 6 mots au plus d'un bloc, 12 au plus construit ; durée de lecture tenue.
- [ ] Jamais deux cartons en même temps ; un plan sans texte entre deux cartons-message.
- [ ] Budget de cartons et de mots du gabarit tenu.
- [ ] Texte, nom et détail clé dans la zone sûre du format.
- [ ] Contraste de 4,5:1 au moins partout (`npx hyperframes check`), 7:1 au moins sur une image.
- [ ] Mêmes mots que le film long ; seule la coupure des lignes change.
- [ ] Aucun chiffre, avis ou citation non fourni ; sinon `[À FOURNIR]`.
- [ ] Musique : le fichier de l'utilisateur, ou aucune.
- [ ] Carton de fin de 2,5 à 3,5 s, immobile ; pas de noir final de plus de 0,5 s.
- [ ] Le film se comprend son coupé, sur un téléphone, à bout de bras.
