# Principes du mouvement observé

Ce fichier dit **pourquoi** on anime un élément d'une certaine manière, et ce qu'on n'anime jamais. Chaque principe porte ses comptes (« N sur M ») et sa raison : ce qui se passe dans l'œil du spectateur. Les recettes et les valeurs à poser dans le script sont dans `elements.md` ; les courbes, dans `courbes.md`.

**Le corpus.** 8 keynotes, de 2019 à 2026, en vidéo 960 × 540 à 29,97 images par seconde, sans son. Deux en direct (2019), six préenregistrées (2020 à 2026). Quatre familles ont été mesurées image par image :

| famille | instances gardées | ce qu'elle couvre |
|---|---:|---|
| texte | 145 | titre, phrase, surtitre, liste, mot qui change, chiffre, carton de film, sortie |
| objets | 122 | poussée de caméra, rotation, flottement, éclaté, lumière qui balaie ou révèle, parallaxe, flou de bougé |
| interfaces | 189 | panneau, zoom dans un écran, défilement, écrans en rangée, voile, flou du fond, passage d'un écran à l'autre |
| transitions | 182 (et 8 861 coupes comptées) | coupe, fondu, passage par le noir, raccord, caméra, lumière, nom et carton de fin |

**Lire ce fichier.**
- « N sur M » : N instances sur les M de la famille.
- **Convention** : un choix de la skill, pas une mesure.
- Distances en % de la hauteur d'image (% H). 1 % H = 10,8 px en 1080p.
- « 10–90 » : temps entre 10 % et 90 % du mouvement. « Visible » ou « 0–100 » : de 2 % à 98 %. « T » : durée de clé à clé.
- On décrit une grammaire. Aucune image, police, logo ou phrase du corpus n'est reprise.

---

## 0. En bref

1. **On coupe d'abord.** On n'anime que ce qui doit être remarqué.
2. **Une courbe par rôle** : le montage est linéaire ; ce qui traverse va à vitesse constante ; ce qui arrive freine ; ce qui s'allume part doucement.
3. **Trois échelles de temps** : le geste (0,2 à 0,5 s), le déplacement qui se pose (0,6 à 1 s), le mouvement de plan (2 à 10 s).
4. **La distance règle la vitesse, pas la durée.** Le rôle règle la durée, pas la taille.
5. **Une chose à la fois entre les éléments, tout ensemble dans un élément.**
6. **Un temps vide après la coupe**, puis l'élément entre.
7. **Pas de rebond.** Rien ne dépasse sa place, sauf rares exceptions datées.
8. **Le flou vient du mouvement**, jamais seul.
9. **Ce qui est posé ne bouge plus.** On laisse regarder.
10. **Le film coupe en mouvement ; l'image composée se pose puis tient.**
11. **Rien ne tourne en entier.**
12. **Une époque à la fois** (convention).

---

## P1. On coupe d'abord

**La règle.** Le changement d'image normal est la coupe. L'animation est l'exception : on la garde pour ce que l'œil doit remarquer.

**Les comptes.**
- Plus de 95 % des changements d'image sont des coupes : 1 967 coupes contre 61 fondus dans les films (3,0 %), 6 894 coupes contre 82 fondus hors films (1,2 %).
- Les films coupent 29,7 fois par minute ; le reste de la keynote, 10,2 fois.
- Le texte est déjà plein à la première image de son plan dans 14 titres sur 29, 6 phrases sur 12, 4 cartons de film sur 16.
- Il sort par une coupe dans 15 sorties sur 18.
- Le raccord graphique (même forme, même place, autre contenu) se fait par une coupe : 22 sur 22.
- Le nom de fin arrive par une coupe dans 10 cas sur 20.

**Pourquoi ça marche.** Une coupe ne coûte rien à l'œil : l'information est là tout de suite. Une animation prend du temps et attire le regard. Si tout bouge, plus rien ne se remarque. En gardant le mouvement rare, chaque mouvement devient un signal.

**Dans le script.** Un élément qui n'a rien à annoncer entre à son `inPoint` et sort à son `outPoint`, sans aucune clé.

---

## P2. Une courbe par rôle

**La règle.** La courbe ne dépend pas de l'objet. Elle dépend de ce que fait le mouvement.

| rôle du mouvement | courbe | comptes |
|---|---|---|
| **Le montage passe d'une image à l'autre** (fondu au noir, fondu de carton) | linéaire | fondus au noir 21 sur 21 ; fondus courts depuis le noir 11 sur 16 ; cartons de film, linéaire 3 sur 7 (meilleure courbe commune) |
| **Un mouvement traverse le plan** (caméra qui avance, parallaxe, pivot, filet de lumière, balayage) | linéaire, du début à la fin du plan | avancées 7 sur 11 ; pivots de slide 4 sur 5 ; parallaxes 8 sur 13 ; filets de lumière, front rectiligne (r² médian 0,91) ; balayages de titre 2 sur 2 mesurés |
| **Un élément arrive et se pose** (entrée, recul, zoom, glissade, panneau, chiffre, caméra qui s'arrête) | arrivée freinée (famille « out » ou courbe en S) | entrées latérales 8 sur 8 ; reculs 4 sur 6 ; ouvertures d'éclaté 5 sur 7 ; zooms d'écran en S ou « ease » 22 sur 27 ; glissades d'écran 26 sur 32 ; rangées 17 sur 19 ; panneaux 4 sur 4 mesurés ; échelle du chiffre « expo-out » 11 sur 18 ; montée d'un titre « expo-out » 4 sur 4 ; caméra qui s'arrête 7 sur 7 |
| **Quelque chose s'allume ou s'éteint** (image qui monte du noir, lumière lente, voile, opacité d'un titre) | départ doux (« in » ou « in-out ») | image qui monte du noir après une coupe 13 sur 14 ; bascules de lumière lentes 4 sur 4 ; opacité des titres « fondu + montée » en S 4 sur 4 ; lignes de liste en cascade 11 sur 13 ; voiles en S 13 sur 18 |

**Ce qui n'existe pas** : une glissade qui part en accélérant sans freiner (0 sur 32) ; un zoom d'écran linéaire (0 sur 27) ; un fondu au noir adouci entre deux séquences (0 sur 21).

**Pourquoi ça marche.**
- Le **montage linéaire** est neutre : il ne prête aucune intention à l'image. On ne le remarque pas.
- La **vitesse constante** d'une caméra fait croire à un mouvement physique qui existait avant le plan et continue après. Une caméra qui accélère ou freine dans un plan court se remarque comme un effet.
- L'**arrivée freinée** donne une masse à l'objet : il ralentit, se pose, et l'œil se pose avec lui. Une arrivée lancée (sans freinage) semble heurter sa place.
- Le **départ doux** imite une lumière qu'on monte : elle naît sans à-coup. Un allumage brutal se lit comme un flash.

**Un élément peut porter deux courbes.** Le titre qui monte : opacité en S (T 0,77 s) et position en « expo-out » (T 0,92 s), 4 titres sur 4. Le chiffre : son opacité finit avant son échelle, 14 sur 18.

---

## P3. Trois échelles de temps

| échelle | durées | ce qui s'y range | bornes observées |
|---|---|---|---|
| **le geste** | 0,2 à 0,5 s (10–90) | opacité d'un chiffre 0,20 s ; fondu de titre 0,35 s ; fondu de carton 0,45 s ; panneau 0,36 s visibles ; voile 0,45 s ; filet de lumière 0,28 s ; fondu enchaîné 0,29 s | aucun panneau au-delà de 0,5 s (16 sur 16) ; aucun fondu enchaîné au-delà de 1 s (25 sur 25) ; fondu d'entrée d'un texte sous 0,94 s dans 88 cas sur 91 |
| **le déplacement qui se pose** | 0,6 à 1 s visibles | zoom d'écran ×2,2 en 0,67 s ; glissade d'écran en 0,70 s ; rangée qui se décale en 0,66 s ; défilement en 0,73 s ; entrée latérale floue en 0,88 s ; titre qui monte, T 0,92 s | zooms entre 0,60 et 1,00 s, 27 sur 27 |
| **le mouvement de plan** | 2 à 10 s, ou tout le plan | avancée ×1,27 en 4,1 s ; recul ×0,45 en 5,8 s ; pivot de 90° en 1,7 à 2,6 s ; sortie du noir 1,6 s (10–90) ; caméra qui se pose en 2,1 à 5,2 s (10–90) | plans de 10 à 25 s en mouvement continu, sans coupe (3 cas) |

**Pourquoi ça marche.** Un geste sous une demi-seconde ne retarde pas la lecture : le texte est lisible presque aussitôt. Un déplacement qui se pose en moins d'une seconde se suit des yeux sans attendre. Un mouvement de plan de plusieurs secondes est assez lent pour ne pas se voir comme un mouvement : il donne seulement de la vie à l'image.

---

## P4. La distance règle la vitesse ; le rôle règle la durée

**La distance ne change pas la durée.** De 27 à 138 % H, le déplacement qui se pose dure 0,66 à 0,73 s (médianes de trois familles d'interface). C'est la vitesse qui monte : de 105 à 467 % H/s au plus fort.

**La taille ne change pas la durée.** Le chiffre héros, très grand (30 à 50 % H), fond en 0,20 s ; un titre en 0,35 s ; un carton de film en 0,45 s ; le nom de fin en 0,65 s.

**Plus c'est près de l'objet, plus c'est lent.** Recul qui révèle l'objet : 1,4 à 5,7 % d'échelle par seconde (4 cas). Image tenue qui dérive : ×1,02 à ×1,06 en 5 à 8 s (3 sur 7). Vols de caméra entre deux lieux : 10 à 48 % H/s (5 cas).

**Pourquoi ça marche.** Une durée fixe garde le pouls du film : chaque déplacement prend le même temps, l'œil apprend le rythme. La durée suit le rôle : le chiffre **frappe**, le carton **se lit**, le nom **ferme**. Près de l'objet, un mouvement rapide ferait perdre le détail qu'on montre.

**Convention de lecture.** Un défilement reste lisible si sa vitesse de pointe reste sous 250 % H/s (appuyé sur 27 défilements : médiane 168, quart supérieur 253).

---

## P5. Une chose à la fois entre les éléments ; tout ensemble dans un élément

**Entre les éléments : l'un après l'autre.**
- Deux écrans d'une rangée n'arrivent jamais en même temps : 11 enchaînements sur 11. Écart médian 1,67 s.
- Le libellé d'un chiffre arrive après lui : le milieu de son fondu vient +0,23 s après celui du chiffre (15 sur 18, de 0,19 à 0,30 s) ; il fond en 0,27 s (10–90, ease-in-out, 15 sur 15).
- Le nom de fin a un plan à lui (fond uni) dans 16 cas sur 20.
- Une poussée de caméra ne change jamais de sens dans son plan (0 sur 17) : un plan, un mouvement.

**L'exception : la cascade.** Les lignes d'une liste partent toutes les 0,05 ou 0,10 s, alors que chacune fond en 0,42 à 0,72 s. Elles se chevauchent beaucoup (5 listes sur 5). Le surtitre arrive avec son mot : 8 cas sur 11, à 0,06 s près.

**Dans un élément : les propriétés bougent ensemble**, chacune avec sa durée. Opacité et position pour un titre ; opacité, échelle et flou pour un chiffre ; voile, flou du fond et mise en avant pour un projecteur ; poussée et glissement pour une caméra (translation médiane de 25 % H pendant une poussée).

**Pourquoi ça marche.** L'œil suit un seul point à la fois. Le décalage entre deux éléments dit l'ordre de lecture : d'abord le chiffre, puis ce qu'il compte. La cascade, elle, se lit comme un seul bloc qui s'allume du haut vers le bas : le décalage est trop court pour qu'on lise chaque ligne à part, il donne seulement un sens. Dans un élément, les propriétés séparées en temps feraient croire à plusieurs mouvements.

---

## P6. Un temps vide après la coupe

**La règle.** On coupe sur le fond vide, puis l'élément entre.

**Les comptes.**
- Le fond vide tient 0,13 à 0,23 s avant que les éléments n'entrent (médianes de 6 keynotes, 135 cas). Il se compte jusqu'à la première trace visible : le départ doux d'une opacité en S (0,04 à 0,13 s avant 2 %) en fait partie.
- Un pivot d'objet part 0,2 à 0,3 s après la coupe (2 sur 2).
- Une puce s'allume 0,2 à 0,4 s après la coupe (4 sur 4).
- Dans un film, la lumière arrive 0,9 à 4,6 s après la coupe (4 sur 4).
- **Seule exception** : l'entrée latérale floue d'un produit part sur la coupe (8 sur 8). Elle est assez rapide pour faire la coupe à elle seule.

**Pourquoi ça marche.** Après une coupe, l'œil doit retrouver le cadre. Si l'élément bouge déjà, une partie du mouvement est perdue. Le temps vide prépare la place ; l'élément entre dans un cadre déjà lu.

---

## P7. Pas de rebond

**La règle.** Rien ne dépasse sa place finale. Rien n'oscille autour d'elle.

**Les comptes.**
- Aucune oscillation : 0 sur 145 textes, 0 sur 14 flottements, 0 sur 56 passages d'écran, 0 sur 18 voiles, 0 sur 37 fondus de passage par le noir.
- Aucun dépassement de plus de 3 % : 0 sur 17 poussées, 0 sur 17 rotations, 0 sur 8 entrées latérales, 0 sur 13 parallaxes, 0 sur 19 rangées, 0 sur 27 zooms d'écran (1,1 % au plus).
- Dépassements simples (un seul aller, un seul retour), rares :
  - +5 % d'échelle pour les chiffres de 2020 (6 sur 6), absent en 2025-2026 (0 sur 18) ;
  - une carte qui monte : +6 % (1 panneau sur 4) ;
  - un défilement : +7,4 % (1 sur 27) ;
  - un éclaté à +3,9 % (1 sur 15, dans la marge de mesure).
- Le seul dépassement franc est **lumineux** : une puce s'allume au-dessus de sa valeur finale puis retombe (3 révélations sur 12, +11 à +28 % de luminance).

**Pourquoi ça marche.** Un rebond ajoute un second mouvement après que l'information est arrivée : l'œil attend que ça s'arrête. Il donne aussi un ton de jouet, élastique, qui rend l'objet léger. Un arrêt net et freiné dit que l'objet est sûr de sa place.

**Dans le script.** Aucune clé ne dépasse sa valeur finale, par défaut. Le dépassement de 2020 reste possible si l'utilisateur choisit cette époque ; il se pose avec une troisième clé (voir `courbes.md` § 4).

---

## P8. Le flou vient du mouvement, jamais seul

**Les comptes.**
- **Flou de bougé** : sur les entrées latérales rapides, la traînée vaut celle d'un obturateur d'environ 120° (médiane 118°, de 74 à 169°, 9 entrées). Visible aussi sur les glissades d'écran (10 sur 16 regardées).
- **Flou d'échelle** : le chiffre qui naît trop grand est flou (au-delà de 6,7 % H dans 12 cas sur 18), et le flou disparaît pendant qu'il se pose. Aucun chiffre n'est flou sans zoom (0 sur 27).
- **Flou de profondeur** : le fond se floute légèrement (σ médian 0,34 % H, 14 cas), presque toujours avec un voile sombre (10 sur 14). À ce niveau, le fond reste reconnaissable.
- Jamais : un flou « de style » sur un objet immobile, ni un flou sur un mouvement lent.

**Pourquoi ça marche.** Le flou est ce qu'une caméra voit d'un objet rapide. Il rend le mouvement crédible et doux. Sans mouvement, le flou se lit comme une erreur de mise au point. Le fond flou, lui, imite une mise au point sur l'élément du premier plan : il reste léger pour que l'on sache encore où l'on est.

**Dans le script.** Flou de bougé : activer le flou de mouvement du calque et de la composition, obturateur 120°. Flou d'échelle : un flou gaussien qui suit l'échelle. Flou de fond : petit, et toujours avec le voile.

---

## P9. Ce qui est posé ne bouge plus ; on laisse regarder

**Ce qui ne bouge pas.**
- **Le produit en lévitation** : il bouge de moins de 0,3 % H en 2 à 18 s (10 tenues sur 13), de moins de 1,6 % H dans 12 sur 13. Aucune oscillation de flottement (0 sur 14). La lévitation vient de l'ombre, du reflet et de la caméra qui bouge autour, pas de l'objet.
- **Le texte qui sort** : aucune sortie ne bouge, ne rétrécit, ne grossit ni ne floute (0 sur 18).
- **Le nom de fin, le carton de film, le libellé d'un chiffre** : ils fondent sur place. Nom : moins de 1,1 % H de déplacement dans 18 cas sur 20. Cartons : 7 sur 7. Libellés : aucun mouvement mesuré, 24 cas sur 27 après le chiffre.
- **Le carton final** : tenu immobile 4 à 50 s (médiane 21,5 s, 7 keynotes).

**Le temps de regarder, après le mouvement.**

| après | maintien médian |
|---|---|
| un zoom dans un détail d'écran | 7,2 s (quart inférieur 2,5 s) |
| un pivot d'objet | 6,5 à 8 s |
| un éclaté ouvert | 3,5 à 7,7 s |
| un chiffre héros | 3,0 s |
| un titre ou une phrase | 2,0 à 3,1 s |
| le nom de fin | 2,6 s |
| un voile | 2,3 s |
| un défilement | 0,9 s |

**Pourquoi ça marche.** Le mouvement annonce, l'immobilité fait lire. Un objet immobile au centre dit qu'il est le sujet. Un objet qui flotte en boucle se lit comme un économiseur d'écran et détourne l'attention.

---

## P10. Le film coupe en mouvement ; l'image composée se pose puis tient

- **Dans un film**, le mouvement remplit le plan. Il commence moins de 0,25 s après la coupe (9 poussées sur 17, 12 parallaxes sur 13) et bouge encore à la coupe suivante (9 poussées sur 17, 11 parallaxes sur 13).
- **Dans une image composée** (une slide, un plein cadre construit), le mouvement se pose, puis l'image tient : pivot tenu 6,5 à 8 s ; éclaté tenu 3,5 à 7,7 s ; détail d'écran tenu 7,2 s.
- **Entre deux séquences**, on passe par le noir : fondu linéaire de 0,5 s, noir tenu 0,4 à 0,5 s, fondu de 0,5 s (6 séquences sur 7 dans la keynote qui l'utilise le plus). Ou on coupe sur le fond vide de l'image suivante (135 cas).

**Pourquoi ça marche.** Un mouvement qui continue à travers la coupe relie les plans : le film coule. Un mouvement qui se pose invite à lire. On choisit l'un ou l'autre selon ce que l'image doit faire : emmener ou montrer.

---

## P11. Rien ne tourne en entier

**Les comptes.**
- Aucun tour complet : 0 sur 17 rotations. Plus grand angle : 160°.
- Le pivot d'un objet va du profil à la face, un quart de tour (90°), en 1,7 à 2,6 s, à vitesse constante (30 à 42 °/s, 3 cas nets). Il finit de face (4 sur 4). Aucun pivot au-delà d'un quart de tour (0 sur 7).
- Aucun texte ne tourne (0 sur 145).
- La caméra roule à peine : 0,2 °/s en médiane sur 309 plans qui bougent. Aucune rotation pendant un zoom d'écran (27 sur 27).

**Pourquoi ça marche.** Un tour complet montre la 3D, pas l'objet. Un quart de tour qui finit de face présente l'objet comme on tend une chose à quelqu'un. Un texte qui tourne ne se lit plus.

---

## P12. Une époque à la fois (convention)

Deux manières se succèdent dans le corpus.

| | 2019-2020 | 2024-2026 |
|---|---|---|
| courbe des écrans (zoom, glissade, rangée) | `cubic-bezier(0.36, 0, 0.25, 1)` : part doucement, se pose doucement (21 instances) | `cubic-bezier(0.60, 0.40, 0.17, 0.95)` : part déjà lancé, freine fort, longue traîne (56 instances) |
| chiffre héros | grandit depuis 0,2 de sa taille, dépasse de 5 % (6 sur 6), ou tombe d'en haut | naît 2 à 8 fois trop grand et flou, se pose sans dépasser (18 sur 18) |
| liste | lignes qui montent du bas, déjà opaques, toutes les 0,37 s (4 sur 4, 2020 seulement) | cascade en fondu + montée, toutes les 0,05 ou 0,10 s (5 listes) |
| titre | coupe ou croissance depuis un point | coupe, ou fondu + montée identique au centième (3 titres sur 4) |

**Convention.** Choisir une époque pour tout le film et s'y tenir. Par défaut : 2024-2026. La manière 2019-2020 donne un rendu plus calme pour les écrans, plus joueur pour les chiffres.

---

## 13. Ce qu'on n'anime jamais

| geste | vu | base |
|---|---:|---|
| chiffre qui compte (compteur, roulement) | 0 | 27 chiffres + 2 chiffres qui changent |
| rebond, oscillation autour de la place finale | 0 | 145 textes, 14 flottements, 56 passages d'écran, 18 voiles |
| texte qui tourne | 0 | 145 textes |
| machine à écrire, lettre par lettre à cadence fixe | 0 | 145 textes (les lettres ne se dévoilent que par un balayage à bord flou : 3 titres et 1 valeur) |
| mot par mot à cadence fixe | 0 | 3 cartons construits, tous par groupes de sens, à 0,6 à 2,5 s d'écart |
| titre ou phrase qui entre en glissant de côté | 0 | 41 titres et phrases |
| sortie de texte animée (mouvement, échelle, flou) | 0 | 18 sorties |
| surtitre animé seul, avant son mot | 0 | 13 surtitres (un seul en avance, poussé par la mise en page) |
| boîte ou bandeau créé pour porter un texte | 0 | 145 textes |
| fondu d'entrée d'un texte au-delà de 1 s (10–90) | 3 | 91 fondus mesurés ; les 3 viennent d'une seule slide |
| mot qui se transforme en un autre (morphing de lettres) | 0 | 14 mots qui changent |
| produit qui flotte en montant et descendant | 0 | 14 flottements |
| tour complet ; pivot au-delà de 90° | 0 ; 0 | 17 rotations ; 7 pivots |
| poussée de caméra qui dépasse ou change de sens | 0 | 17 poussées |
| filet de lumière qui repasse, ou qui descend | 0 ; 0 | 11 fronts |
| flou sans mouvement | 0 | 27 chiffres ; aucun objet immobile flou |
| zoom d'écran linéaire, ou avec rotation | 0 ; 0 | 27 zooms |
| glissade d'écran verticale ; glissade qui part en accélérant sans freiner | 0 ; 0 | 32 glissades |
| deux écrans qui arrivent en même temps dans une rangée | 0 | 11 enchaînements |
| voile qui va jusqu'au noir | 0 | 20 voiles (73 % au plus) |
| panneau qui met plus d'une demi-seconde | 0 | 16 panneaux |
| fondu enchaîné de plus de 1 s | 0 | 25 fondus enchaînés |
| noir de moins de 0,40 s entre deux fondus | 0 | 25 noirs |
| raccord graphique par fondu | 0 | 22 raccords |
| nom de fin qui glisse ou monte en entrant | 0 | 20 noms |
| fondu au noir adouci entre deux séquences | 0 | 21 fondus au noir (tous linéaires) |
| fondu au blanc entre deux séquences | 0 | toute la régie (l'éclat blanc existe, dans les films seulement) |
| volet, effet de page, zoom de transition entre deux séquences | 0 | 181 candidats mesurés ; un volet, un iris et un masque en forme de signe existent, en ouverture ou en fin seulement (**convention** : les réserver aux fins) |

---

## 14. Ce que ces principes ne disent pas (conventions)

- **La musique.** Les vidéos sont sans son : aucun lien entre un mouvement et un temps musical n'est mesuré. Caler les entrées sur la musique est une convention.
- **Les formats 9:16 et 1:1.** Aucun n'est observé. Les distances en % H se transposent par convention en u, 1 % du petit côté : 10,8 px en 1920 × 1080 comme en 1080 × 1920 ou en 1080 × 1080. Sur un même téléphone, un texte garde ainsi sa taille quand on tourne l'image.
- **L'intensité du flou de bougé des glissades d'écran**, la mise au point qui glisse, le décalage entre les pièces d'un même éclaté : non mesurés.
- **Les films de pur motion design** (fenêtres en vol, éventails) : plusieurs mouvements s'y superposent ; 15 tentatives de mesure sur 16 ont été écartées.
- **Les valeurs de départ cachées** : un mouvement qui démarre sous un fondu n'est pas visible avant 20 % d'opacité ; son départ est extrapolé.
- **Le flou de départ du chiffre** au-delà de 6,7 % H : c'est la borne de la mesure, pas une valeur.

## 15. Limites du corpus

- Vidéo compressée en 960 × 540 : les mouvements de moins de 0,1 % H se confondent avec le bruit.
- Les deux keynotes de 2019 montrent les slides sur l'écran de scène, filmé par une caméra : moins d'instances, mesures plus bruitées.
- Beaucoup de mouvements sont coupés en cours par le montage : leur durée totale n'est pas observable, seule la partie visible l'est.
- Les « maintiens » des démonstrations suivent la parole du présentateur : ce sont des ordres de grandeur.
