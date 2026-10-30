# Film de fonctionnalités : composants, formes et verbes

Ce que fait un film qui présente un produit logiciel **par ses fonctionnalités**, sans présentateur, à partir de ses interfaces : quoi montrer, dans quel ordre, et comment le faire bouger. Les règles des autres fiches (`principes.md`, `elements.md`) s'appliquent ; celle-ci dit **comment on les compose** pour ce genre de film.

**Base : 2 films** de lancement de fonctionnalités, 2025 et 2026, relevés à 1 et 2 images par seconde et par liste de coupes :
- **A** : 30 s, musique seule, fond noir, douze fonctionnalités en douze verbes ;
- **B** : 2 min 13, voix off, fonds de couleur, sept fonctionnalités, une par plan.

Deux films, c'est peu : tout ce qui suit est une **convention appuyée sur deux cas**, sauf mention « (A et B) » qui veut dire « observé dans les deux ». Les durées et les comptes des keynotes (`principes.md`) restent la référence des mouvements eux-mêmes.

---

## 1. Les trois matières du film

Un film de fonctionnalités n'a pas de plan d'ensemble de l'application. Il alterne trois matières, et c'est leur alternance qui fait le rythme :

| matière | ce que c'est | ce qu'elle porte |
|---|---|---|
| **le verbe** | un texte court, centré, qui nomme ce que l'utilisateur fait : *verbe + complément*, 2 à 4 mots | l'argument, un par fonctionnalité |
| **le composant** | un morceau d'interface **sorti de son écran** : une ligne de liste, une carte, un bouton, un sélecteur, une rangée d'icônes, une piste de montage | la preuve : la fonctionnalité existe, voilà où on la touche |
| **la forme** | un objet abstrait (sphère, pastille, bulle, trait) qui joue le rôle d'une personne ou d'un flux | l'histoire : qui fait quoi, à qui ça arrive |

Le film **A** n'a presque que des verbes et des composants (fond noir). Le film **B** ajoute les formes : cinq sphères de couleur jouent les cinq membres d'une famille, et leurs couleurs sont **celles des avatars dans l'interface** : la forme entre dans l'écran et devient l'avatar de la ligne (B, 0:16 → 0:23). C'est le lien à garder quand on invente des formes : elles reprennent une couleur, une icône ou un état qui existe déjà dans le produit.

---

## 2. L'ordre du film

| temps | A (30 s) | B (2 min 13) |
|---|---|---|
| ouverture | nom du produit en graphie « vivante » (lettres faites d'objets), puis le même nom en graphie propre : 0 → 1,5 s | l'écran complet sur un téléphone, 1 s, puis les formes seules qui jouent la situation : 0 → 11 s |
| promesse | mosaïque de toutes les interfaces (1,5 → 3,3 s), puis la promesse en deux temps : « Un(e) … » / « … sans fin » (3,5 → 5,5 s) | la promesse est dite par la voix (0:15 → 0:28) sur les formes et un écran flouté en décor |
| sommaire | la rangée des icônes des outils (5,5 → 7 s) | — |
| fonctionnalités | 12 verbes, 1,0 à 3,7 s chacun ; les 9 derniers à **1,05 s** de moyenne (16 → 25,5 s) | 7 fonctionnalités, **un plan chacune**, 4,5 à 19,6 s (médiane 6,3 s), dans l'ordre où un parent les rencontre |
| prix ou appel | « pour X / mois » en une ligne, 26 → 27,5 s | — |
| nom de fin | liste des outils groupés par couleur (27,5 → 28,5 s), puis le nom en graphie vivante → propre (28,5 → 30 s) | les formes se regroupent (2:04 → 2:07), phrase de fin, cinq pastilles, logo (2:08 → 2:13) |

Ce qui se répète (A et B) :
- le film **ouvre et ferme sur le nom** ou le logo, et la fin reprend l'image de l'ouverture (graphie vivante → propre ; sphères regroupées comme au début) ;
- **une fonctionnalité = un verbe (ou une phrase dite) = un composant**. Jamais deux composants pour un verbe, jamais un verbe sans composant ;
- le composant **répond** au verbe : il arrive pendant ou juste après lui, pas avant ;
- la **durée** d'un temps est celle de la lecture du verbe, pas celle de l'animation : 1 s en A quand la musique porte, 4 à 7 s en B quand la voix explique.

---

## 3. Le verbe (texte)

- **Graphie.** Linéale, blanc sur noir (A) ou noir sur fond clair (B), corps d'un titre (`elements.md` § 2). Centré. Un seul verbe à l'écran.
- **Entrée.** Par coupe ou remplacement sur place (`mot-remplace`, `elements.md` § 6) : en A, 10 verbes sur 12 **remplacent** le précédent au même endroit, sur le même fond noir, sans coupe d'image ; le fond vide entre deux verbes dure 0,1 à 0,5 s (`principes.md` P6).
- **Le mot porte la fonctionnalité.** En A, le verbe est écrit **dans la matière** de ce qu'il annonce : lettres en fleurs puis en eau pour « générer » ; moitié du mot pixelisée pour « agrandir » ; une lettre qui glisse pour « déplacer » ; mot écrit à la main pour « écrire » ; mot froissé qui tombe dans une corbeille pour « jeter » ; un mot remplacé par une bande de vidéo pour « monter une vidéo » ; mot sélectionné avec ses poignées pour « sélectionner ». **Un seul mot traité par verbe**, le reste de la phrase reste en graphie propre.
- **Durée.** 1,05 s en moyenne quand ils s'enchaînent (A, 9 cas), jusqu'à 3,7 s quand un composant se construit dessous (A, « faire un rythme » : 7 → 9,7 s, pistes qui s'empilent).
- **Ne pas faire.** Plus de quatre mots. Deux verbes à l'écran. Un verbe qui glisse ou rebondit (règles de `principes.md` § 13). Traiter tout le texte : un mot suffit.

**Avec le moteur.** `titre` + `coupe` ou `mot-remplace` ; le mot traité est une `image` (PNG rendu à part) posée à la place du mot, recette `coupe` ou `revelation-lumiere`. La construction d'un composant sous le verbe : `forme` ou `capture` avec `panneau-pose` ou `empilement`, 0,25 à 0,5 s après le verbe (**convention**).

---

## 4. Le composant sorti de l'écran

C'est le geste propre à ce genre de film, et il n'existe pas dans les keynotes mesurées (où l'écran reste entier, `elements.md` § 11).

**Ce qu'on sort.** En B, dans l'ordre : une ligne de liste (avatar + nom + âge), une carte de réglage (titre + sous-titre), une carte « plus utilisés » (icônes + durées), une carte graphique (barres par jour), trois boutons d'action, un sélecteur de date (roue), un bouton principal, une grille d'icônes avec cases à cocher, une bulle de conversation avec deux boutons, un interrupteur, un sélecteur de jours, une roue d'heure, une liste de catégories à cocher. En A : une rangée d'icônes, des pistes de montage, un cadre de texte avec poignées, une grille de pads.

**Comment.**
1. **L'écran entier d'abord**, sur son appareil, 1 à 3 s (B : 0:16 → 0:19 ; 0:29 → 0:30 ; 1:30 → 1:31 ; 1:54 → 1:55). On sait d'où vient le composant.
2. **Le composant monte au premier plan** : il grandit (×2 à ×4 : la ligne de liste passe de 6 u à 20 u de haut), **l'écran derrière se floute** et s'efface (B, 0:20 → 0:23 : écran flou σ ≈ 0,7 u, composant net). Les autres composants du même écran peuvent se déplier à leur tour, décalés dans la profondeur (B, 0:24 → 0:28 : quatre cartes qui s'écartent).
3. **Il est manipulé** : on y fait l'action du verbe. La roue tourne jusqu'à la bonne valeur (B, 0:36 → 0:37), les cases se cochent une à une pendant que la grille défile (0:46 → 0:50), l'interrupteur bascule, les jours s'allument (1:34 → 1:35), l'heure change (1:36 → 1:37). **Une manipulation par composant.**
4. **Retour à l'écran entier** ou coupe au suivant (B : 0:29, 0:43, 1:30, 1:54).

**Réglages (conventions, 2 films).**
- Agrandissement : ×2 à ×4 ; une carte ne dépasse pas 60 u de large.
- Fond sous le composant : la couleur du chapitre (§ 6), ou l'écran flouté (σ 0,5 à 0,8 u, jamais net, jamais noir).
- Entrée : `panneau-pose` (0,36 s) quand il vient d'un bord ; échelle + position (`zoom-detail`, 0,6 à 1 s) quand il sort de l'écran.
- Les composants gardent leurs **vraies proportions, polices et couleurs** : rien n'est redessiné. Ils viennent d'exports de l'interface (Figma, captures ×2), découpés un par un.

**Ne pas faire.** Sortir deux composants en même temps (P5). Redessiner un composant « plus beau » que dans le produit : la preuve ne vaut que si c'est le vrai. Garder un cadre d'appareil reconnaissable d'une marque (panneau à coins arrondis). Montrer des données personnelles : données de démonstration, prénoms fictifs.

**Avec le moteur.** `capture` par composant (un PNG découpé), `zoom-detail` ou `panneau-pose` à l'entrée, `assombrir-autour` avec `flou` sur l'écran de fond. La manipulation (roue qui tourne, case qui se coche) est **hors recette** : deux images du composant (avant, après) et une coupe entre les deux, ou un petit script à la main (`courbes.md` § 7) ; dis-le dans le plan.

---

## 5. Les formes qui jouent (film B)

- **Une forme = une personne** (ou un objet qui circule : bulle de message, fenêtre, bloc). Sphères dégradées, 8 à 25 u, cinq couleurs du produit. Elles se **déplacent** (glissent, roulent, se cachent derrière un écran, se regroupent), elles ne se déforment pas, sauf un aplatissement bref quand l'une d'elles est bloquée (2:01 → 2:03 : la sphère devient un demi-dôme).
- **Elles entrent dans l'interface** : la sphère devient l'avatar de la ligne (0:21), se cache derrière l'écran flou (0:40 → 0:42), revient devant le composant (1:05 → 1:08).
- **Elles donnent le ton** : bulles qui dansent pour « discuter » (0:05), traînées rapides pour « jouer » (0:06 → 0:07), défilement derrière une fenêtre pour « faire défiler » (0:08 → 0:10), flocons qui tombent pour « tomber de sommeil » (1:56 → 1:57).
- **Durée** : 1,5 à 3 s par situation en ouverture (coupes à 4,8 ; 6,4 ; 8,0 ; 11,0 s), 5 à 12 s quand elles accompagnent la voix.

**Ne pas faire.** Des personnages dessinés (visages, corps) : la forme suffit, elle n'a pas d'âge ni de genre. Une forme qui rebondit en boucle ou flotte (P7, P9). Des formes d'une couleur absente du produit.

**Avec le moteur.** `forme` ronde avec un dégradé (deux couleurs du thème), `nul-camera` parent pour les déplacements, `camera-travelling` ; les regroupements de fin par `coupe` ou `produit-entree`. Les déformations ne sont pas dans le moteur : convention à écrire à la main, ou à éviter.

---

## 6. Le fond change à chaque chapitre (film B)

Le fond n'est pas neutre : il **dit le chapitre**. Relevé sur B (couleur médiane des bords) :

| temps | fond | chapitre |
|---|---|---|
| 0:00, 0:16, 1:54 | gris clair `#dddce1` | l'application, les écrans entiers |
| 0:05, 1:56 | violet nuit `#140048` | la conversation, la nuit |
| 0:06, 1:05, 1:43 | vert sombre `#08473f` | le jeu, les applis, le soir |
| 0:08, 1:39 | vert pâle `#cfdcd2` | l'école, le planning |
| 1:17 | indigo `#2e077e` | les contacts |
| 1:24 → 1:28 | lavande → rouge `#c44851` | l'alerte sur une image |
| 1:47 → 1:51 | bleu pâle → bleu `#86bcd6` | la pause, la pluie |
| 2:08 | noir | la fin, le nom |

- **23 changements de fond en 2 min 13**, tous **par coupe** ou par **balayage de couleur** qui traverse l'image (1:24 → 1:28 : le rouge monte depuis le bas en 2 s). Jamais de fondu enchaîné entre deux fonds.
- Les composants gardent leur fond clair : c'est le fond du film qui change, pas l'interface.
- Le film A ne change jamais de fond (noir, 30 s) : avec la musique seule, le rythme vient des verbes.

**Avec le moteur.** `fond` avec `couleur` du thème, recette `coupe` à chaque chapitre ; le balayage de couleur est hors recette (convention : `forme` rect qui monte, `phrase-par-le-bas` détourné, ou une coupe).

---

## 7. Ce qu'il faut recueillir pour un film de ce genre

En plus du recueil de `SKILL.md` § 1 :

1. **La liste des arguments**, dans l'ordre du business, un par ligne : *verbe + complément* (ce que l'utilisateur fait), et la **preuve** (le composant qui le montre). Sans composant, l'argument n'entre pas dans le film : il va dans la phrase de fin, ou il saute.
2. **Les composants**, un fichier par composant, découpés à partir des écrans (Figma : un export par cadre, ×2 ; capture : découpe), avec l'écran entier dont chacun vient, en données de démonstration.
3. **Deux états par composant manipulé** (avant, après) : case vide et cochée, interrupteur éteint et allumé, roue sur l'ancienne et la nouvelle valeur.
4. **La promesse** en une ligne (6 mots au plus), et la **phrase de fin** si elle diffère ; le **prix** ou l'appel à l'action, s'il y en a un.
5. **Les couleurs** : celles du produit (thème), et pour chaque chapitre la couleur de fond qu'il prend (ou « le même fond partout »).
6. **Le son** : musique fournie (le rythme des verbes suit ses temps : convention) ou voix off (texte dit, et alors un plan par phrase), ou rien.
7. **Les formes** : voulues ou non ; si oui, ce qu'elles représentent (une personne, un flux), et de quelle couleur du produit elles héritent.

Ce qui manque reste visible : un argument sans composant est marqué `[COMPOSANT À FOURNIR]` et montré en repli neutre ; une promesse non fournie est proposée et marquée « À VALIDER ».

---

## 8. Limites de cette fiche

- Deux films, un par registre (musique seule ; voix off). Les comptes « N sur M » des autres fiches n'existent pas ici : tout est convention appuyée sur ces deux cas, et se dit comme tel dans le plan.
- Les manipulations de composants (roue, case, interrupteur) et les déformations de formes **ne sont pas dans le moteur** : elles se font à la main ou par deux images et une coupe.
- Les durées des temps en A dépendent d'une musique précise ; sur une autre musique, caler les verbes sur ses temps est une convention.
- Les deux films sont en 16:9 ; en 9:16, les composants sortis de l'écran prennent toute la largeur (convention).
