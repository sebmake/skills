# Quoi animer, et comment : élément par élément

Pour chaque type d'élément : **quoi** animer (quelle propriété), **comment** (la recette du moteur, sa durée, sa courbe, son amplitude, son décalage), **quand** (sa place dans la séquence) et **ce qu'il ne faut pas faire**. Les noms de recettes sont ceux du moteur (`scripts/motion_lib.mjs`, liste complète : `node scripts/build_motion.mjs --liste`). La façon de les écrire dans `motion.json` est dans `motion-spec.md`.

Sommaire :
0. Lire une fiche · 1. Choisir vite · 2. Titre · 3. Phrase · 4. Surtitre · 5. Liste · 6. Mot qui change · 7. Chiffre · 8. Carton de film · 9. Logo et nom de fin · 10. Image de produit · 11. Capture d'interface · 12. Icône · 13. Forme · 14. Fond · 15. Caméra · 16. Passer d'un plan à l'autre · 17. Construire une séquence

---

## 0. Lire une fiche

- **Unité** : `u` = 1 % du petit côté de l'image. En 16:9, c'est 1 % de la hauteur (le « % H » des analyses) : 1 u = 10,8 px en 1080p.
- **Durées** : « T » = d'une clé à l'autre ; « 10–90 » = de 10 % à 90 % du mouvement ; « visible » = de 2 % à 98 %. Le moteur convertit (`courbes.md` § 5).
- **Fourchette** : chaque réglage a une valeur par défaut (la médiane mesurée) et une fourchette (le corpus). Un réglage **mesuré** hors fourchette est une erreur au contrôle. Un réglage de **convention** peut changer ; le contrôle le signale.
- **Époque** : `2024-2026` (par défaut) ou `2019-2020`. Une recette marquée d'une époque n'appartient qu'à elle ; « toutes » va partout (`principes.md` § P12).
- **Majeur** : la recette déplace l'élément de façon visible. Deux mouvements majeurs ne se chevauchent pas (`principes.md` § P5), sauf dans une cascade.
- **Sortie** : par défaut une coupe (`"sortie": "coupe"`). Le seul autre choix est un fondu lent et linéaire de 1,15 s (`"sortie": "fondu"`), vu sur 2 titres. Jamais de sortie qui bouge (0 sur 18).

---

## 1. Choisir vite

| élément | `type` | par défaut (2024-2026) | autres recettes | jamais |
|---|---|---|---|---|
| titre, nom seul | `titre` | `coupe`, ou `titre-fondu-montee` s'il doit être remarqué | `titre-fondu`, `titre-balayage`, `carton-fondu` ; 2019-2020 : `phrase-zoom-arriere`, `chute` | glisser de côté, tourner, lettre par lettre, rebondir |
| phrase | `phrase` | `coupe` | `titre-fondu-montee`, `carton-fondu`, `carton-groupes` ; 2019-2020 : `phrase-zoom-arriere`, `chute`, `phrase-par-le-bas` | mot à mot, glisser de côté |
| surtitre | `surtitre` | `avec` (son mot) | `coupe` | s'animer seul, avant son mot |
| liste | `liste` | `liste-cascade` | `liste-cascade-rapide`, `liste-au-fil` ; 2019-2020 : `liste-par-le-bas` | lignes de côté, de bas en haut |
| mot qui change | `titre`, `phrase` | `mot-remplace` | `mot-fondu-enchaine` ; 2019-2020 : `mot-glisse` | morphing de lettres, roulement |
| chiffre héros | `chiffre` | `chiffre-pose` | `nom-remonte` (prix) ; 2019-2020 : `chiffre-croissance`, `chute` | compter, fondre sur place |
| carton de film | `titre`, `phrase` | `carton-fondu` | `carton-groupes`, `coupe` | monter, zoomer |
| logo, nom de fin | `logo` | `logo-fin` | `coupe` | glisser, monter |
| image de produit | `image` | `coupe` puis `camera-poussee` | `produit-entree`, `produit-pivot`, `eclate`, `revelation-lumiere`, `balayage-lumiere`, `produit-recul`, `produit-rotation`, `produit-flotte` | flotter en boucle, faire un tour complet, rebondir |
| capture d'interface | `capture` | `coupe` puis `zoom-detail` | `panneau-pose`, `defilement`, `empilement`, `assombrir-autour` | zoom linéaire, glissade verticale, deux arrivées ensemble |
| icône | `icone` | `avec` (son mot) ou `coupe` | `assombrir-autour` (dans une grille), `produit-entree`, `revelation-lumiere` | tourner, rebondir |
| forme | `forme` | `coupe` | `panneau-pose`, `eclate`, `balayage-lumiere`, `revelation-lumiere` | boîte animée derrière un texte |
| fond | `fond` | `coupe` | transitions `bascule-lumiere`, `passage-noir`, `montee-du-noir` ; `assombrir-autour` | animer pour décorer |
| caméra | `nul-camera` | `camera-poussee` | `camera-recul`, `camera-travelling`, `camera-se-pose`, `zoom-detail` | rouler, changer de sens dans un plan |

---

## 2. Titre (un nom ou 1 à 4 mots)

**Quoi animer.** L'opacité, et la position verticale si le titre doit être remarqué. Rien d'autre.

**Comment.**

| recette | époque | ce qu'elle fait | réglages (défaut, fourchette) | comptes |
|---|---|---|---|---|
| `coupe` | toutes | plein dès la première image du plan | — | 14 titres sur 29 |
| `titre-fondu-montee` | 2024-2026 | fond en S et monte vers sa place | `T_opacite` 0,77 s (0,64–0,77), `easeInOutCubic` ; `T_position` 0,92 s (0,92–1,17), `easeOutExpo`, part `retard_position` 0,30 s (0,26–0,31) après le fondu ; `montee` 15,3 u (7,4–15,5) ; `flou` de départ 0 (convention, jusqu'à 0,4) | 4 sur 29, identiques au centième dans 3 cas sur 4 |
| `titre-fondu` | toutes | fond sur place | `d1090` 0,43 s (0,27–0,71), `ease` | 5 sur 29 |
| `titre-balayage` | 2024-2026 | se dévoile de gauche à droite derrière un front à bord flou | `T` 0,6 s (0,33–0,86), linéaire ; `bord` 2,8 % de la largeur (2,8–6,3) | 3 sur 29 |
| `phrase-zoom-arriere` | 2019-2020 | naît très grand et flou, se pose | voir § 3 | 2 phrases |
| `chute` | 2019-2020 | tombe d'en haut, sans rebond | voir § 3 | 6 chutes |

**Pourquoi la montée retarde de 0,30 s.** La montée n'est visible qu'à partir de 20 % d'opacité : le titre semble monter sur place pendant qu'il apparaît. Il ne « glisse » pas vers sa place.

**Quand.** Après une coupe sur le fond vide (0,13 à 0,23 s de vide, 135 cas). Ce vide se compte jusqu'à la première trace visible : l'opacité en S de `titre-fondu-montee` met déjà 0,09 s à atteindre 2 % (0,13 s pour une ligne de `liste-cascade`). Pose donc `debut` de 0 à 0,10 s après la coupe ; le contrôle calcule le vide visible. Puis le titre tient : 2,3 s en médiane pour un titre coupé (0,2 à 4,8), 2,0 s pour un titre en fondu + montée (1,2 à 8,2). Il sort par une coupe.

**Ne pas faire.** Glisser depuis la gauche ou la droite (0 sur 41 titres et phrases). Tourner (0 sur 145 textes). Écrire lettre par lettre (0 sur 145). Rebondir (0 sur 145). Fondre plus de 1 s (3 cas sur 91, une seule slide). Poser une boîte ou un bandeau derrière (0 sur 145).

---

## 3. Phrase (une idée, 1 ou 2 lignes)

**Quoi animer.** Rien, le plus souvent : la phrase est un plan à elle (6 sur 12). Sinon, l'opacité et la position comme un titre.

**Comment.**

| recette | époque | ce qu'elle fait | réglages | comptes |
|---|---|---|---|---|
| `coupe` | toutes | pleine dès la première image | — | 6 phrases sur 12 ; maintien 3,1 s (2,6–5,2) |
| `titre-fondu-montee` | 2024-2026 | comme un titre | § 2 | (mesuré sur les titres) |
| `carton-fondu` | toutes | fond sans bouger | § 8 | 7 cartons sur 7 |
| `carton-groupes` | toutes | se construit par groupes de 2 à 4 mots | § 8 | 3 cartons |
| `phrase-zoom-arriere` | 2019-2020 | naît ×8 et floue, se pose | `depart` ×8 (7,5–8,1) ; `T_echelle` 0,42 s (0,40–0,45), `ease` ; opacité `d1090_opacite` 0,35 s (0,33–0,37), `ease-in-out` ; `flou` σ 5 u (4,4–6,7) qui décroît avec l'échelle | 2 phrases sur 12 |
| `chute` | 2019-2020 | tombe d'en haut, accélère, s'arrête net | `T` 0,23 s (0,20–0,27), `easeInQuad` ; `hauteur` 68 u au-dessus (45–75) | 6 chutes (3 phrases, 3 chiffres) ; aucun rebond 6 sur 6 |
| `phrase-par-le-bas` | 2019-2020 | entre d'en dessous du cadre, déjà opaque | `T` 0,65 s (0,6–0,7), `ease` ; `depart` 58 u (50–60) | 1 phrase |

**Quand.** Une phrase se lit : laisse-la 2,6 à 5,2 s. Toutes les phrases animées du corpus sont de 2020 (6 sur 6) ; en 2024-2026, la phrase coupe ou fond.

**Ne pas faire.** Écrire mot à mot sur une image (0 sur 12). Fondre seule, sans autre mouvement, sur une image composée (0 sur 12 : le fondu seul est pour les cartons). Glisser de côté (0 sur 41).

---

## 4. Surtitre (la petite ligne au-dessus du mot principal)

**Quoi animer.** Rien à lui. Il suit son mot.

**Comment.** `avec`, en nommant le mot dans `"avec"`. Il reprend la recette et le début de ce mot. Réglage `ecart` : 0 s (−0,06 à +0,06). Comptes : 8 surtitres sur 11 séparables arrivent avec leur mot, à 0,06 s près.

Cas particulier : un prix. Le nom remonte pour faire place au libellé et au prix, qui entrent ensemble dessous : `nom-remonte` (§ 7).

**Ne pas faire.** L'animer seul, avant son mot (0 sur 13). Le faire glisser depuis un bord (0 sur 13).

---

## 5. Liste

**Quoi animer.** L'opacité de chaque ligne, et une petite montée. Les lignes s'allument de haut en bas (16 listes sur 16).

**Comment.**

| recette | époque | ce qu'elle fait | réglages | comptes |
|---|---|---|---|---|
| `liste-cascade` | 2024-2026 | toutes les lignes en moins d'une seconde, qui se chevauchent | `decalage` 0,10 s (0,093–0,113) ; opacité `T_opacite` 1,14 s (1,00–1,17), `easeInOutCubic`, qui part avec la montée (10–90 mesuré 0,72 s, traîne comprise) ; montée `T_position` 1,17 s (0,98–1,17), `easeInOutQuint`, `montee` 21 u (18–23) | 3 listes, 10 écarts ; montée `easeInOutQuint` 7 lignes sur 11 (`easeInOutQuart` 4) ; `easeInOutCubic` 11 lignes sur 13 ; à 25 % d'opacité, la ligne est encore 18 u sous sa place (11 lignes sur 11) |
| `liste-cascade-rapide` | 2024-2026 | la même, plus serrée | `decalage` 0,05 s (0,029–0,066) ; opacité `T_opacite` 0,75 s (0,64–0,83), `easeInOutCubic` (10–90 mesuré 0,42 s) ; `montee` 4 u (0–4,1) ; `T_position` 1,0 s, `easeInOutQuint` | 2 listes, 13 écarts |
| `liste-au-fil` | 2024-2026 | une ligne quand elle est dite ; le bloc remonte d'une demi-interligne à chaque ajout | `intervalle` 2 s (1,4–3,6), ou la liste `temps` ; opacité `T_opacite` 1,17 s, `easeInOutCubic` ; montée `T_position` 0,95 s, `easeInOutQuart`, `montee` 15 u (14–17) | 3 listes ; remontée du bloc 2 listes sur 2 |
| `liste-par-le-bas` | 2019-2020 | lignes déjà opaques qui montent du bas | `decalage` 0,37 s (0,362–0,377) ; `T` 0,65 s (0,63–0,67), `easeOutQuart` ; `depart` 31 u (27–35) | 4 listes de juin 2020 |

**Pourquoi le décalage est si court.** 0,05 à 0,10 s contre 0,42 à 0,72 s de fondu (5 listes sur 5) : on ne lit pas chaque ligne à part, on voit un bloc qui s'allume du haut vers le bas. Le décalage donne un sens de lecture, pas un rythme.

**Quand.** Cascade : en début de plan, après le temps vide. Au fil : une ligne par idée dite (avec une musique, cale-les sur les temps forts : **convention**).

**Ne pas faire.** Faire entrer une ligne de côté (0 sur 16). La faire descendre vers sa place (0 sur 13 listes où un mouvement est mesuré). Allumer de bas en haut (0 sur 16).

---

## 6. Mot qui change (même place, autre mot)

**Quoi animer.** Le moins possible. Changer un mot n'est pas un moment : 5 changements sur 14 tiennent en une image ou en moins de 0,3 s.

**Comment.**

| recette | époque | ce qu'elle fait | réglages | comptes |
|---|---|---|---|---|
| `mot-remplace` | toutes | l'ancien disparaît, le nouveau apparaît sur la même image | — | 3 sur 14 |
| `mot-fondu-enchaine` | 2024-2026 | l'ancien floute et s'efface, le nouveau apparaît | `d1090_ancien` 0,50 s ; `d1090_nouveau` 0,47 s, `easeInOutSine` ; `ecart` 0,61 s entre les deux milieux ; `flou` 1,5 u (convention) | 1 cas |
| `mot-glisse` | 2019-2020 | l'ancien monte en s'effaçant, le nouveau arrive dessous | `d1090_ancien` 0,22 s (`ease-in`) ; `d1090_nouveau` 0,20 s (`easeInCubic`) ; `ecart` 0,16 s ; `glisse` 6 u (convention) | 1 cas |

**Ne pas faire.** Transformer les lettres d'un mot en un autre (0 sur 14). Faire rouler le mot comme un compteur (0 sur 14).

---

## 7. Chiffre héros

**Quoi animer.** L'**échelle**, avec un flou qui suit l'échelle, et l'opacité. Puis le libellé, seul, en fondu sur place.

**Comment.**

| recette | époque | ce qu'elle fait | réglages | comptes |
|---|---|---|---|---|
| `chiffre-pose` | 2024-2026 | naît trop grand et flou, se pose sans dépasser | `depart` ×4,1 (1,9–8 ; ×3,4 à la première image) ; `T_echelle` 0,67 s (0,25–0,80), `easeOutExpo` ; opacité `d1090_opacite` 0,20 s (0,18–0,62), `ease-in-out` ; `flou` σ 6,7 u au départ (1,1–6,7, borne de la mesure) qui tombe à 0 avec l'échelle ; libellé `retard_libelle` +0,23 s (0,19–0,30) du milieu du fondu du chiffre au milieu du sien, `d1090_libelle` 0,27 s (0,26–0,27), `ease-in-out` | 18 chiffres sur 27 ; aucun dépassement 18 sur 18 ; libellé après 15 sur 18 ; fondu du libellé en `ease-in-out` 15 sur 15 |
| `chiffre-croissance` | 2019-2020 | grandit depuis petit, dépasse de 5 %, revient | `depart` ×0,22 (0,19–0,37) ; `T_echelle` 0,83 s (0,72–0,88), `easeOutBack` ; `d1090_opacite` 0,22 s ; libellé +0,26 s (de milieu à milieu), fondu 0,11 s | 6 sur 27 ; dépassement +5 % 6 sur 6 |
| `chute` | 2019-2020 | tombe d'en haut | § 3 | 3 chiffres |
| `nom-remonte` | toutes | un nom remonte pour faire place au libellé et au prix dessous | `T_nom` 0,50 s (0,45–0,53), `ease`, `remontee` 10 u (7,4–10,7) ; libellé + prix : `d1090_opacite` 0,30 s (0,22–0,41), `montee` 10 u (6–14) | 5 slides de prix sur 5 |

**Pourquoi l'opacité va plus vite que l'échelle.** Le chiffre est déjà lisible quand il finit de se poser (14 sur 18) : l'œil lit le nombre pendant que la taille se règle. Le flou vend la vitesse du zoom ; sans zoom, aucun flou (0 sur 27).

**Quand.** Le chiffre a son plan, sur un fond uni. Il tient 3,0 s (1,6 à 5,8). Le libellé suit : il dit ce que le chiffre compte.

**Ne pas faire.** **Compter** (0 sur 27 : le chiffre est final dès la première image visible). Fondre sur place sans échelle (0 sur 27). Flouter sans zoom (0 sur 27). Animer le libellé avec le même mouvement que le chiffre (il fond sur place, 24 sur 27).

**Aucun chiffre inventé.** Un chiffre non fourni s'écrit `[À FOURNIR]`, avec sa source à fournir.

---

## 8. Carton de film (texte plein cadre entre deux images)

**Quoi animer.** L'opacité seule.

**Comment.**

| recette | ce qu'elle fait | réglages | comptes |
|---|---|---|---|
| `carton-fondu` | fond sans bouger | `d1090` 0,45 s (0,31–0,78), linéaire | 7 fondus sur 7 sans mouvement ; linéaire 3 sur 7 |
| `carton-groupes` | la phrase se construit par groupes de sens ; la ligne se recentre à chaque ajout | `ecart` 0,75 s entre groupes (0,6–2,5) ; chaque groupe `d1090` 0,45 s ; `T_recentrage` 0,3 s, `easeOutCubic` (convention) | 3 cartons |
| `coupe` | plein à la coupe | — | 4 cartons sur 16 |

**Quand.** Un carton par idée. Il tient 2,2 s (0,2 à 4,2). Il fond plus lentement qu'un chiffre (0,45 s contre 0,20 s) : il se lit, il ne frappe pas.

**Ne pas faire.** Le faire monter ou zoomer (0 sur 7). Construire mot à mot à cadence fixe (0 sur 3).

---

## 9. Logo et nom de fin

**Quoi animer.** L'opacité, sur place. Rien d'autre.

**Comment.** `logo-fin` : `entree` `fondu` (10–90 en `d1090` 0,65 s, fourchette 0,27–2, `out-quad`) ou `coupe`. Une mention en petit dessous arrive avec lui (`avec`, 2 cartons finaux) ou après lui (0,9 s et 5 s, 2 cartons) : dans ce cas, un élément à part avec son propre `debut` et la même recette (lu sur planche, 4 cartons).

Comptes : 20 noms de fin, entrée par coupe 10, par fondu 10 ; déplacement de 1,1 u au plus dans 18 sur 20 ; centre vertical entre 47 et 51 % de la hauteur dans 15 sur 20 ; tenu 2,6 s (1,25 à 4,7). Le carton final d'une keynote tient 4 à 50 s (médiane 21,5 s).

**Quand.** En dernier, sur un plan à lui (fond uni dans 16 cas sur 20). Avant lui, un mouvement de sortie long est fréquent (7 keynotes sur 8) : la caméra s'élève, recule, ou l'objet sort du cadre.

**Ne pas faire.** Glisser ou monter en entrant (0 sur 20). Le faire tourner, rebondir ou se dessiner trait par trait (non observé). Reprendre le logo d'une autre marque.

---

## 10. Image de produit (objet détouré, rendu ou photo)

**Quoi animer.** Presque jamais l'objet lui-même. C'est la **caméra** (un nul parent) qui avance, recule ou glisse ; c'est la **lumière** qui révèle. L'objet bouge seulement pour entrer, pivoter d'un quart de tour, ou s'ouvrir en éclaté.

**Comment.**

| recette | ce qu'elle fait | réglages | comptes |
|---|---|---|---|
| `coupe` + `camera-poussee` | l'objet est là ; la caméra avance doucement tout le plan | § 15 | avancées linéaires 7 sur 11 |
| `produit-entree` | arrive par la droite sur la coupe, freine, se pose, avec flou de bougé | `T` 0,9 s (0,82–0,93), `out-cubic` ; `depuis` droite (gauche : convention) ; `obturateur` 120° (74–169) | 9 entrées ; freine 8 sur 8 ; par la droite 7 sur 7 |
| `produit-pivot` | du profil à la face, à vitesse constante (calque 3D, rotation Y) | `angle` 90° (12–90 ; avec une image plate, partir de 70° pour qu'elle reste visible) ; `T` 2 s (1,7–2,6), linéaire ; `delai` 0,25 s après la coupe | 4 pivots sur 5 linéaires ; finit de face 4 sur 4 |
| `produit-poussee` | l'objet grandit lentement (si pas de caméra) | `facteur` ×1,27 (1,02–2,58) ; `duree` 4,1 s (2,2–8,6) ou toute sa présence ; linéaire | 11 avancées |
| `produit-recul` | l'objet rétrécit en freinant | `facteur` ×0,45 (0,05–0,84) ; `duree` 5,8 s (2,7–8,5) ; `ease-out` | 6 reculs, freinent 4 sur 6 |
| `produit-rotation` | tourne dans le plan (objet vu de dessus) | `angle` 83° (19–160) ; `duree` 4,2 s (1,4–9,5), linéaire | 6 instances ; aucun tour complet 0 sur 17 |
| `produit-flotte` | lévitation : **aucun mouvement**, une ombre douce dessous | `derive` 0 u/s (convention : 1 à 10 pour un objet suspendu qui dérive en ligne droite) ; `ombre` 1 (convention) | immobile à 0,3 u près dans 10 tenues sur 13 ; 0 oscillation sur 14 |
| `eclate` | les pièces s'écartent en freinant, ou se rassemblent | `sens` ouvre (`T_ouvre` 1,9 s, `ease-out`) ou ferme (`T_ferme` 1,2 s, linéaire) ; `amplitude` ×1 (convention) ; `decalage` 0 s entre pièces (convention) | 7 ouvertures, freinent 5 sur 7 ; 9 fermetures ; 1 dépassement sur 15, dans la marge |
| `revelation-lumiere` | l'objet sort du noir, ou s'éteint | `d1090` 1,6 s (0,1–6), linéaire ; `delai` 0,3 s (0,2–0,4) ; `sens` allume ou eteint (extinction 1,0 s) ; `eclat` 0 % (jusqu'à 28 pour une puce, 3 sur 12) | 12 sorties du noir ; 7 extinctions |
| `balayage-lumiere` | un filet de lumière traverse une fois | `T` 0,28 s (0,10–1,17), linéaire ; `largeur` 31 % de l'objet (5–32) ; `sens` droite, gauche ou haut ; `intensite` 45 % et `inclinaison` 20° (conventions) | un seul passage 11 sur 11 ; vers le bas 0 sur 11 |

Les compléments s'enchaînent avec `puis` : par exemple `produit-entree`, puis `balayage-lumiere` 1,1 s après (exemple de `assets/exemple-motion.json`).

**Quand.**
- L'entrée latérale part **sur** la coupe (8 sur 8). Tout le reste attend un peu : pivot 0,2 à 0,3 s après la coupe, puce qui s'allume 0,2 à 0,4 s après.
- Après le geste, l'objet tient : 6,5 à 8 s après un pivot, 3,5 à 7,7 s après un éclaté.
- Dans un film (plans courts qui coupent), la caméra bouge encore à la coupe suivante (9 poussées sur 17).

**Ne pas faire.** Faire flotter l'objet en montant et descendant (0 sur 14). Faire un tour complet (0 sur 17) ou pivoter de plus d'un quart de tour (0 sur 7). Rebondir à l'arrivée (0 sur 8 entrées). Répéter le filet de lumière (0 sur 11) ou le faire descendre (0 sur 11). Flouter un objet immobile.

**Ce qu'il faut fournir.** Un PNG détouré, assez grand pour la poussée : pour ×1,27 en 1080p, l'objet doit garder sa netteté à 1,27 fois sa taille à l'écran. Pour un pivot : le moteur tourne le calque en 3D (`ADBE Rotate Y`) ; une image plate tourne alors comme une carte, sans volume. Un vrai volume demande un rendu 3D de l'objet ou une suite de vues (**convention**). Pour un éclaté, les pièces en fichiers séparés, de même cadre (`pieces`).

---

## 11. Capture d'interface (un écran dans le film, pas l'animation d'une application)

**Quoi animer.** Le **cadre** de la capture et la caméra qui la regarde : zoom dans un détail, défilement du contenu, arrivée d'un panneau, rangée d'écrans, voile autour. La capture reste une image : la skill ne simule pas le comportement d'une application.

**Comment.**

| recette | ce qu'elle fait | réglages | comptes |
|---|---|---|---|
| `zoom-detail` | la caméra entre dans un détail (ou en ressort) ; échelle et position, même courbe | `facteur` ×2,2 (1,45–3) ; `T` 0,95 s (0,6–1,53) ; `sens` entre ou sort ; `point` du détail en % de l'élément (convention) ; courbe `zoom-2024` (2024-2026) ou `montage-2020` | 27 zooms visibles 0,60 à 1,00 s ; 0 linéaire, 0 dépassement, 0 rotation |
| `defilement` | le contenu défile dans une fenêtre | `distance` 59,5 u (14–196) ; `T` 1,07 s (0,94–2,16) ; `mode` presentation (`defilement-2024`), geste (`geste`, lancé, 1,72 s) ou continu (linéaire, 68 u/s) ; `fenetre` 60 × 60 u (convention) | 27 défilements ; vitesse de pointe 168 u/s ; jamais plus de 196 u d'un coup |
| `panneau-pose` | un panneau arrive d'un bord et se pose | `visible` 0,36 s (0,17–0,50) ; `distance` 40 u (15,9–62) ; `depuis` bas, haut, gauche, droite ; `dans_la_page` 1 (courbe `ease`) ou bord (`out-expo`) ; `carte` 1 = dépassement ≤ 6 % (`out-back`) ; `fondu` 1 (convention) | 16 panneaux ; aucun au-delà de 0,5 s |
| `empilement` | un écran de plus entre par le côté et pousse la rangée | `intervalle` 1,67 s (0,83–10,5 ; rafale 0,85 s) ; `T` 0,79 s (0,6–1 ; 0,96 s en 2019-2020), courbe `rangee-2024` ou `montage-2020` ; `ecart` 4 u entre écrans (convention) ; un fichier par écran (`fichiers`) | 29 instances ; décalage 26,6 u ; 0 chevauchement sur 11 enchaînements ; 0 vertical sur 19 |
| `assombrir-autour` | un voile noir tombe sur tout sauf l'élément ; le fond peut se flouter | `niveau` 40 % (5–73 ; projecteur 65 à 70) ; `T` 0,53 s (0,4–0,6), courbe `voile` ; `flou` σ 0 u (0–0,78 ; 0,34 médian) | 20 voiles ; jamais jusqu'au noir 20 sur 20 ; flou avec voile 10 sur 14 |

**Quand.**
- Le zoom part après que la capture a été vue entière (convention : 0,5 s au moins). Puis on **reste** sur le détail : 7,2 s en médiane (2,5 s au quart inférieur).
- Un écran à la fois dans une rangée : le suivant part après la fin du précédent.
- Le voile et le flou du fond commencent ensemble et durent autant.
- Pour passer d'une capture à une autre : transition `glissade` ou `poussee` (§ 16).

**Ne pas faire.** Zoomer en linéaire (0 sur 27), tourner pendant un zoom (0 sur 27). Faire glisser un écran verticalement (0 sur 32). Faire arriver deux écrans ensemble (0 sur 11). Assombrir jusqu'au noir (0 sur 20). Un panneau de plus d'une demi-seconde (0 sur 16). Un flou de fond fort (au-delà de 0,78 u : 0 sur 14).

**Ce qu'il faut fournir.** Des captures à la définition native ou ×2, sans données personnelles (floutées ou de démonstration). Aucun cadre d'appareil d'une marque : un panneau flottant à coins arrondis le remplace.

---

## 12. Icône

Peu de mesures portent sur l'icône seule. Ce qui est observé :
- elle arrive **avec** son mot ou son titre, sans animation à elle (règle du surtitre, 8 sur 11 : `avec`) ;
- dans une grille d'icônes, on désigne la bonne par un projecteur : voile de 33 à 73 % sur les autres (4 cas), flou du fond jusqu'à σ 0,78 u, et l'icône choisie qui grandit d'environ ×2 en venant au centre (1 cas, lu sur planche). `assombrir-autour` avec `niveau` 65 à 70 et `flou` pose le voile et le flou ; l'agrandissement n'est pas dans la recette (à ajouter à la main, courbe `montage-2024`, 0,9 s : **convention**) ;
- dans un raccord, on coupe d'une icône à la même place dans un autre contenu (11 raccords sur 22 gardent le cadre et changent le contenu).

**Comment.** `avec` (défaut), `coupe`, `assombrir-autour`. `produit-entree` ou `revelation-lumiere` si l'icône est traitée comme un objet (**convention**).

**Ne pas faire.** Faire tourner, rebondir ou pulser une icône (aucun cas observé ; les règles générales s'appliquent : 0 rebond, 0 rotation de texte, 0 oscillation).

---

## 13. Forme (trait, cercle, jauge, panneau dessiné)

**Quoi animer.** La position ou la taille de la forme quand elle arrive ; sa lumière. Une forme ne décore pas : elle porte une information (une jauge, un tracé, un cadre).

**Comment.**
- `coupe` (défaut).
- `panneau-pose` pour un cadre ou une carte qui arrive.
- `eclate` pour des plaques qui s'écartent ou se posent.
- `balayage-lumiere` et `revelation-lumiere` pour la lumière.
- Une jauge qui se remplit : la valeur se dévoile de gauche à droite en 0,26 s (10–90), courbe proche d'une sortie douce (1 cas, mesuré). Une jauge qui glisse pour faire place : 0,2 s (1 cas). Hors recette : écris ce geste à la main (`courbes.md` § 7).
- Un tracé qui se dessine : 3 reflets suivent la pointe d'un tracé gravé à vitesse quasi constante, 12 à 19 % de la largeur par seconde, pendant 2 à 2,6 s (mesuré sur le reflet). Hors recette : la fin d'un « Trim Paths » (`ADBE Vector Trim End`) de 0 à 100 %, linéaire.

**Ne pas faire.** Une boîte ou un bandeau animé derrière un texte (0 sur 145). Une forme qui oscille, tourne en boucle ou rebondit.

---

## 14. Fond

**Quoi animer.** Rien, pour décorer. Le fond change par une coupe, une bascule de lumière, un passage par le noir ; il s'assombrit ou se floute derrière ce qu'on montre.

**Comment.**
- `coupe` : la coupe sur le fond vide de l'image suivante (135 cas), puis les éléments entrent.
- Transition `bascule-lumiere` : le fond s'éteint dans le plan, l'objet reste allumé ; `T` 2,4 s (1,2–2,6), courbe `in-out-sine` ; `niveau` 85 % (convention). Comptes : 4 bascules lentes sur 4 adoucies.
- Transitions `passage-noir`, `montee-du-noir`, `fondu-au-noir`, `fondu-depuis-noir` : § 16.
- `assombrir-autour` sur l'élément mis en avant : le voile couvre le fond.

**Fonds observés** : unis, noirs ou très sombres, gris très clairs ; en 2025, des fonds flous colorés (non mesurés en mouvement). Un fond clair vide tient 0,13 à 0,23 s après la coupe.

**Ne pas faire.** Un dégradé qui tourne, des particules, un fond qui respire en boucle (non observés : **convention** de ne pas les faire). Un fondu au blanc entre deux séquences (0 vu).

---

## 15. Caméra (un nul parent : `nul-camera`)

**Quoi animer.** L'échelle et la position d'un nul qui porte les éléments (avancée, recul, glissement). Les éléments posés en dessous gardent leurs propres recettes. Plusieurs profondeurs donnent une parallaxe (`profondeur` de chaque élément).

**Comment.**

| recette | ce qu'elle fait | réglages | comptes |
|---|---|---|---|
| `camera-poussee` | avance à vitesse constante, du début à la fin du plan | `facteur` ×1,27 (1,02–2,58) ; linéaire | 7 avancées sur 11 linéaires ; commence moins de 0,25 s après la coupe 9 sur 17 |
| `camera-recul` | recule en freinant | `facteur` ×0,45 (0,05–0,84) ; `ease-out` ; 7,4 à 8,5 s pour révéler l'objet entier depuis un détail | 6 reculs, freinent 4 sur 6 |
| `camera-travelling` | glisse à vitesse constante ; le premier plan va plus vite que le fond | `vitesse` 4,7 u/s (0,5–48) pour la profondeur 1 ; `direction` [−1, 0] (convention) ; parallaxe : premier plan 1,9 fois plus vite que le fond (0,9–12,4), jusqu'à 10 fois pour un objet devant un fond flou | 216 translations sur 309 plans qui bougent ; parallaxes linéaires 8 sur 13 |
| `camera-se-pose` | ralentit jusqu'à l'arrêt dans le plan | `d1090` 4,4 s (2,1–5,2) ; `facteur` ×0,68 (0,46–1) ; `deplacement` (convention) ; `out-cubic` | 7 sur 21 ; arrivée à vitesse nulle 7 sur 7 |
| `zoom-detail` | entrée rapide dans un détail | § 11 | 27 zooms |

**Quand.** Une seule recette de caméra par plan. Le mouvement commence avec le plan. Dans un film, il bouge encore à la coupe ; dans une image composée, il se pose puis l'image tient (`principes.md` § P10). Près de l'objet, lent : 1,4 à 5,7 % d'échelle par seconde pour un recul révélateur (4 cas).

**Ne pas faire.** Rouler (roulis médian 0,2 °/s ; aucun pendant un zoom, 0 sur 27). Changer de sens dans le plan (0 sur 17). Dépasser l'échelle finale (0 sur 17). Une poussée de moins de 1,1 s (10–90) : ce serait un zoom, pas une poussée.

---

## 16. Passer d'un plan à l'autre (`transitions`)

| transition | ce qu'elle fait | réglages | comptes | quand |
|---|---|---|---|---|
| `coupe` | rien entre les deux images | — | plus de 95 % des changements | par défaut |
| `raccord` | coupe sur la même forme, à la même place | — | 22 raccords sur 22 par coupe ; centre déplacé de 3,2 u, taille à 12 % près (21 sur 22) | passer d'un contenu à un autre dans le même cadre |
| `passage-noir` | fondu au noir, noir tenu, fondu depuis le noir, tout linéaire | `T_fondu` 0,5 s (0,33–1,27) ; `noir` 0,5 s (0,4–1,5) | fondus au noir linéaires 21 sur 21 ; noir de 0,40 s au moins 25 sur 25 | fermer une séquence |
| `fondu-au-noir` | l'image passe au noir | `T` 0,5 s (0,33–1,27), linéaire | 21 sur 21 | fin d'un film, avant le nom |
| `fondu-depuis-noir` | l'image monte du noir | `T` 0,5 s (0,34–2,71) ; au-delà de 0,68 s, la courbe freine (`out-cubic`) | 11 courts linéaires sur 16 ; 5 longs freinés sur 5 | ouvrir une séquence |
| `montee-du-noir` | coupe au noir, noir court, l'image s'allume | `noir` 0,27 s (0,1–0,5, convention) ; `d1090` 0,39 s (0,17–0,74), `in-out-cubic` | départ doux 13 sur 14 | une photo, un objet, un chiffre qui « s'allume » |
| `fondu-enchaine` | mélange court des deux images | `T` 0,54 s (0,25–0,98), linéaire | 25 vérifiés ; aucun au-delà de 1 s | rare : entre deux rendus d'objet, deux plans d'un clip |
| `glissade` | le plan entier part sur le côté, le suivant entre, avec flou de mouvement | `T` 0,89 s (0,64–0,94), courbe `glissade` ; `sens` gauche ou droite | 16 glissades, 138 u ; horizontal 32 sur 32 | d'un écran à l'autre |
| `poussee` | un contenu en pousse un autre dans un cadre fixe | `T` 0,75 s (0,6–1,02), courbe `poussee-ecran` ; `sens` | 7 instances | d'un écran à l'autre dans le même cadre |
| `bascule-lumiere` | le fond s'éteint dans le plan | § 14 | 4 sur 4 adoucies | isoler l'objet avant la révélation |

**Ne pas faire.** Un volet, un effet de page, un zoom de transition entre deux séquences (0 vu ; volet, iris et masque en forme de signe réservés aux fins : **convention**). Un fondu enchaîné de plus de 1 s (0 sur 25). Un noir de moins de 0,40 s entre deux fondus (0 sur 25). Un raccord en fondu (0 sur 22).

---

## 17. Construire une séquence

Le gabarit le plus fréquent, pour une image composée (convention qui assemble les mesures ci-dessus) :

1. **Coupe sur le fond vide** ; il tient 0,13 à 0,23 s jusqu'à la première trace visible. Le départ doux d'une opacité en S en fait partie : `debut` de 0 à 0,10 s après la coupe.
2. **L'élément principal entre** avec sa recette (titre, chiffre, objet, capture). Un seul mouvement majeur à la fois.
3. **Ce qui l'accompagne suit** : le surtitre avec lui (`avec`), le libellé 0,23 s après (de milieu de fondu à milieu de fondu), la mention après le logo.
4. **Un geste de lumière ou de caméra** s'ajoute si l'image tient longtemps : poussée lente tout le plan, filet de lumière une fois, voile autour d'un détail.
5. **L'image tient** : 2 à 3 s pour un texte, 3 s pour un chiffre, 6 à 8 s pour un objet qui pivote, plusieurs secondes sur un détail d'écran.
6. **Coupe** vers l'image suivante. Un passage par le noir pour fermer une séquence ; le nom de fin seul, en dernier.

Le rythme d'un film (plans courts, 29,7 coupes par minute) et celui d'une image composée (une image qui se pose et tient) ne se mélangent pas dans un même plan.
