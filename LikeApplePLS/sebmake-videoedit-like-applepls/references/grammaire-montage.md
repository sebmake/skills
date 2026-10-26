# Grammaire du montage, famille par famille

Ce fichier dit comment se monte un film à la manière des films des keynotes. Il sert deux fois :

- au **plan de montage** : choisir la famille, la forme, la place et la durée de chaque temps ;
- à la **critique** : comprendre pourquoi une mesure s'écarte, et quel geste de montage corrige.

Chaque règle porte son compte (« N sur M ») et sa raison : ce qui se passe dans l'œil ou l'oreille du spectateur. Les valeurs que lisent les scripts sont dans `cibles/` et `scripts/gabarits.json` ; le format des fichiers, dans `montage-spec.md` ; la lecture d'un rapport de critique, dans `critique.md`.

## Sommaire

1. Lire ce fichier
2. Choisir la famille
3. Le tronc commun (règles G)
4. Produit et révélation (règles P)
5. Ouverture et ambiance, avec sketches, fictions, clôtures, transitions (règles A, pour ambiance)
6. Documentaire et témoignage (règles T)
7. Bande-annonce et usage (règles BA et U)
8. Le son : voix, musique, silence
9. Durée, format, couleur
10. Ce qu'on ne reprend jamais
11. Observé ou convention : le récapitulatif

---

## 1. Lire ce fichier

**Le corpus.** Les films de 8 keynotes, de 2019 à 2026. Chaque film a été découpé plan par plan (coupes au calcul, fondus et valeurs de plan vérifiés à l'œil). La parole vient des sous-titres. La piste son n'a été mesurée que pour deux familles (ouverture, documentaire).

| Famille | Films | Ce qui a été mesuré |
|---|---|---|
| Produit et révélation | 16 : 7 révélations d'objet, 4 logiciels, 3 films de matériaux avec voix off, 2 films d'usage et de gamme | 213 plans d'image, 234 transitions, valeur de chaque plan ; pas de son |
| Ouverture et ambiance | 20 : 8 ouvertures (dont 3 sketches ou fictions), 2 seuils, 1 hommage, 3 clôtures, 6 transitions entre deux lieux | 367 changements de plan dans les ouvertures, 453 coupes comparées, piste son |
| Documentaire et témoignage | 8, plus 2 variantes sans entretien | 596 plans d'image, 606 transitions, type et valeur de 744 plans, 107 prises de parole, piste son |
| Bande-annonce et usage | 8 : 6 bandes-annonces, 2 films d'usage | 657 plans relevés à l'œil, 459 transitions, 108 répliques ; pas de son |

Un même film peut servir deux familles : une clôture faite de témoignages est comptée en ouverture et en documentaire.

**Marquage.**

- **observé N sur M** : vu dans N cas sur les M de la base indiquée ;
- **convention** : pas mesuré, ou trop peu de cas. C'est un choix de la skill, à appliquer tel quel ;
- **faible** : observé, mais sur 1 à 3 cas. À suivre, pas à imposer.

« Pourquoi » donne la raison d'une règle. C'est une lecture de ce que fait le spectateur, pas une mesure.

**Les identifiants.** Les règles de ce fichier s'écrivent G (tronc commun), P (produit), A (ouverture et ambiance), T (documentaire et témoignage), BA (bande-annonce) et U (usage). Le rapport de critique a ses propres identifiants de contrôle (C, K, O, D, B) ; `critique.md` dit à quelle règle chacun renvoie.

**Les mots.** Plan d'image : un plan qui montre une image (pas un noir, pas un carton). Plan médian : la durée du plan du milieu quand on les range du plus court au plus long. Tiers : le début, le milieu ou la fin du film, chacun un tiers de la durée. Pic : le passage où les plans sont les plus courts. Valeur de plan : détail, serré, rapproché, moyen, entier (l'objet en entier), large.

---

## 2. Choisir la famille

La famille dépend **des rushes**, pas de l'envie (convention). Sans entretiens filmés, pas de documentaire. Sans l'objet entier filmé, pas de révélation.

| Les rushes… | Famille | Forme (`schema` de `montage.json`) |
|---|---|---|
| montrent un objet nouveau : matière, pièces, détails, et un plan de l'objet entier | Produit et révélation | `revelation_tardive` |
| montrent un logiciel, un usage ou une gamme de coloris | Produit et révélation | `objet_des_le_debut` |
| installent une ambiance, un lieu, un moment ; ou jouent une petite scène | Ouverture et ambiance | `ouverture` |
| vont d'un lieu à un autre, en avançant | Ouverture et ambiance | `transition_decor` |
| font défiler des visages, des réactions, pour finir un événement | Ouverture et ambiance | `cloture` |
| des entretiens posés, peu de voix, et des plans de leur travail | Documentaire et témoignage | `pose` |
| beaucoup de voix brèves, des vidéos filmées par les gens, des réactions | Documentaire et témoignage | `choral` |
| une seule histoire, avec des répliques | Bande-annonce et usage | `oeuvre` |
| plusieurs sujets à annoncer, chacun avec un titre | Bande-annonce et usage | `catalogue_blocs` |
| plusieurs sujets, sans titres à montrer ou sans parole | Bande-annonce et usage | `catalogue_mele` |
| des gens qui se servent d'un objet, en situation | Bande-annonce et usage | `usage` |

Si deux familles conviennent, demande à l'utilisateur (convention). Un film suit une seule forme : on ne mélange pas la révélation tardive et l'objet dès le début, ni le régime posé et le régime choral.

---

## 3. Le tronc commun (règles G)

Ce que les quatre familles partagent. Une règle de famille passe avant une règle G quand elles diffèrent.

**G1. Couper franc.** La coupe franche est le changement de plan normal.
- Produit : 194 transitions sur 234 (83 %). Ouverture : 359 sur 367 (98 %). Documentaire : 594 sur 606 (98 %). Bande-annonce : 423 sur 459 (92 %). Usage : 164 sur 171 (96 %).
- *Pourquoi :* une coupe ne coûte rien à l'œil, l'image est là tout de suite. Un fondu prend du temps et se remarque. Si tout est fondu, plus rien ne se remarque.

**G2. Un fondu enchaîné au plus, à un passage choisi.**
- Produit : 7 sur 234, dont 5 douteux ; les 2 vus nettement entrent dans un plan clé (le nom, un premier visage). Ouverture : 1 net, à 94 % du film, de l'image animée vers le réel. Documentaire : 1 sur 606, jamais entre deux plans de parole. Bande-annonce : 8 sur 459, dont 6 sont un titre qui laisse place à l'image.
- Exception : un clip chanté fond 9 changements sur 16, en fondus courts de 0,17 à 0,33 s (1 film, faible).
- *Pourquoi :* le fondu dit « on passe d'un monde à l'autre ». Gardé rare, il garde ce sens.

**G3. Le noir ouvre.** On entre dans le film par le noir.
- Produit 13 sur 16 (médiane 1,1 s). Ouverture : un seuil de noir ou de carton 6 sur 8. Documentaire 6 sur 8. Bande-annonce 7 sur 7 mesurables (médiane 0,6 s).
- Ailleurs, le noir change de rôle selon la famille : rare et court dans le produit, à l'entrée seulement dans l'ouverture, au changement de chapitre dans le documentaire, en ponctuation de la fin dans la bande-annonce.
- *Pourquoi :* le noir efface ce qui précédait. L'œil se règle sur l'écran avant la première image.

**G4. Tout bouge, sauf ce qu'on doit regarder longtemps.**
- Plans fixes (mouvement sous le seuil du corpus) : produit 14 sur 197 (7 %), ouverture 30 sur 351 (9 %), bande-annonce 29 sur 384 (7,6 %), transitions entre deux lieux 0 sur 33.
- Deux exceptions nettes : l'entretien, caméra fixe dans 18 plans sur 20 regardés ; les photos d'un hommage, immobiles dans 22 sur 22.
- *Pourquoi :* le mouvement garde l'œil actif. Un visage qui parle, une photo, se lisent mieux immobiles : le sens est dans ce qu'on voit, pas dans la caméra.

**G5. Un plan long tient le film**, sauf dans la bande-annonce.
- Un plan d'au moins 5 s : produit 14 sur 16 ; ouvertures montées 7 sur 7 ; documentaire posé 5 sur 5, dans le dernier cinquième.
- Bande-annonce : le plus long plan va de 1,8 à 5,1 s selon le film. Son temps long est le titre final (§ 7).
- *Pourquoi :* après des plans courts, un plan long laisse le temps de comprendre. Il marque la révélation, l'arrivée, la fin.

**G6. Le texte est rare, petit, centré, sans boîte, et seul.**
- Produit : 0 carton explicatif et 0 chiffre sur 16 films ; une seule phrase dans tout le corpus de la famille (5 mots).
- Jamais deux textes à l'écran en même temps : 0 sur 16 films produit ; un seul bloc à la fois dans 8 bandes-annonces et films d'usage sur 8.
- Cartons-message du documentaire : centrés 6 sur 6, d'une hauteur de 5,2 à 5,7 % de l'image (5 sur 6). Bandeaux de nom : sans boîte (8 personnes vues de près).
- Ouverture : texte au seuil ou à la fin, jamais au milieu (0 sur 7).
- *Pourquoi :* le texte arrête l'image. Peu de mots, posés dans un vide, se lisent sans quitter le film.

**G7. Le carton reste assez longtemps pour être lu.**
- Ouverture : environ 0,5 s par mot (médiane de 7 cartons ; de 0,32 à 2,09 s par mot).
- La skill sœur `sebmake-videopresentation-likeapplepls` pose le plancher : **1,2 s + 0,3 s par mot** (convention calée sur 109 cartons). Une phrase de 6 mots tient donc au moins 3,0 s, ce qui rejoint les 0,5 s par mot de l'ouverture.
- Cas courts observés : titre de bloc d'une bande-annonce 1,0 s en médiane ; mot-choc de 1 ou 2 mots, 1,0 à 2,3 s ; bandeau de nom 2,1 s en médiane.
- *Pourquoi :* un carton qu'on n'a pas fini de lire laisse une gêne qui couvre le plan suivant.

**G8. La musique porte les grands changements, pas chaque coupe.**
- Coupe sur une attaque du son : non démontré. Film produit (skill sœur) : 16 coupes sur 62 à ± 70 ms d'une attaque, pour 16,4 attendues au hasard. Documentaire : 363 coupes sur 597, pour 361,5 au hasard. Ouverture : net dans 1 film sur 11 (un montage de photos), faible dans 2, absent dans 8.
- Ce que la musique fait : elle part du calme (ouverture 4 sur 8 partent du silence ; documentaire 8 sur 8 ouvrent plus bas que leur niveau médian) et culmine après 60 % de la durée (ouverture 7 sur 8).
- *Pourquoi :* couper sur chaque temps se sent comme une machine. Les films suivent la musique par la sortie du noir, le pic, la révélation, le nom.

**G9. Le raccord se place, il ne se répète pas.**
- Sur 453 coupes d'ouverture, la composition d'un plan ressemble au suivant autant qu'à un plan pris au hasard (médiane 0,05 contre 0,06).
- Les raccords existent, mais à des endroits choisis : sur le mouvement dans 12 films produit sur 16 ; de forme dans 3 films produit sur 16 ; aucun raccord d'image dans 17 coupes documentaires sur 48 (la voix fait le lien).
- *Pourquoi :* un raccord se remarque. À chaque coupe, il devient un tic.

**G10. Finir : tenir, ou fermer net.**
- Tenir : le produit finit sur l'objet entier tenu (13 sur 16, médiane 7,4 s) ; l'ouverture sur un plan large qui atterrit (6 sur 8 d'au moins 5 s) ; le documentaire posé sur un plan tenu (5 sur 5).
- Fermer net : la bande-annonce accélère puis s'arrête sur son titre (8 sur 8) ; le documentaire choral finit par une rafale puis un logo (3 sur 3).
- *Pourquoi :* la fin est ce qu'on emporte. Un plan tenu laisse l'image se poser ; un arrêt net fait tomber le titre.

---

## 4. Produit et révélation (règles P)

**Base : 16 films** (24 à 128 s). Sans voix off : 13 films de 24 à 51 s, médiane 31,9 s. Avec voix off : 3 films de matériaux, 54 à 128 s.

### 4.1 Deux formes

| Forme | Films | Ce qui se passe |
|---|---|---|
| **Révélation tardive** (`revelation_tardive`) | 10 sur 16 | un monde ou une matière, puis des détails, puis l'objet entier vers 77 % de la durée |
| **Objet dès le début** (`objet_des_le_debut`) | 5 sur 16 | l'objet entier entre 1 et 18 % de la durée, puis ses usages ou ses fonctions, puis une gamme ou le nom |
| Objet jamais entier | 1 sur 16 | un logiciel montré par des gestes sur l'écran ; le nom ferme |

### 4.2 Les temps de la révélation tardive (10 films)

| Temps | Ce qu'on voit | Mesure |
|---|---|---|
| Ouverture | noir, puis une image naît | noir d'ouverture 7 sur 10 |
| Accroche | un décor ou un paysage (6 sur 10) ; une matière, une pièce, un liseré de lumière (4 sur 10) | premier plan d'image 3,3 s en médiane (quartiles 2,3 et 7,9 s, 16 films) |
| Montée | détails, pièces, fabrication, usages, en plans courts | plans de 1,25 à 3,5 s (quartiles), médiane 2,4 s |
| Révélation | l'objet entier, tenu | entre 69 et 82 % de la durée (médiane 77 %) ; plan tenu 4,9 à 9,0 s (médiane 8,0 s) |
| Nom | écrit sur un carton, s'il est écrit | entre 83 et 96 % (médiane 94 %), 1,3 à 4,5 s (médiane 2,4 s) |
| Fin | l'objet entier tenu, puis rien, un noir ou le nom | dernier plan d'image 7,4 s en médiane |

### 4.3 Les règles

**P1. Choisir la forme selon ce qu'on montre.** Un objet nouveau se garde pour la fin (révélation tardive, 10 sur 16). Un logiciel, un usage, une gamme se montrent tout de suite (5 sur 16).
*Pourquoi :* la révélation vit de la curiosité. Quand le sujet est ce qu'on fait avec l'objet, le cacher n'apporte rien.

**P2. Durée : court.** Sans voix, 24 à 51 s (médiane 31,9 s, 13 films). Avec une voix off de matériaux, 54 à 128 s (3 films). La skill sœur compte jusqu'à 68,5 s avec d'autres bornes : même conclusion, un film produit sans voix reste court. Au-delà de 60 s sans voix : des chapitres d'une idée chacun (convention).
*Pourquoi :* sans voix, le film tient sur une seule attente. Elle s'use vite.

**P3. Ouvrir sur le noir, puis faire naître l'image.** Noir d'ouverture 13 sur 16, de 0,3 à 1,6 s pour 9 sur 13. L'image sort du noir par un fondu (0,7 à 1,3 s) ou par la lumière dans 8 sur 16.
*Pourquoi :* l'image qui naît pose le calme. Le spectateur entre avant que quelque chose se passe.

**P4. Premier plan : un monde ou une matière, jamais l'objet entier** en révélation tardive (0 sur 10).
*Pourquoi :* montrer l'entier d'abord, c'est donner la fin.

**P5. Serrer dans la montée.** Détails et plans serrés : 70 % des plans au premier tiers, 65 % au milieu, 48 % au dernier (201 plans).
*Pourquoi :* l'objet vu par morceaux crée l'envie de le voir en entier.

**P6. Rythme : des plans de 2 s, un passage rapide tôt.** Plan d'image médian 2,17 s (213 plans ; p10 0,73 s, p90 7,16 s). Un passage d'environ 5 plans à 1,2 s, dans la première moitié pour 8 films sur 11. Pas de règle d'accélération jusqu'à la fin : 9 films accélèrent en seconde moitié, 5 ralentissent, 2 restent stables. Pas de pic juste avant la révélation (les 3 plans qui la précèdent sont plus courts que la médiane dans 6 sur 10 seulement).
*Pourquoi :* l'énergie vient pendant qu'on découvre les pièces. Ensuite le film ralentit pour laisser voir l'entier.

**P7. Couper franc ; les fondus vont au noir.** 83 % de coupes. Fondus au noir et depuis le noir : 9 % ensemble. Aucun fondu depuis le noir dans le dernier tiers (0 sur 10) : le noir qui s'ouvre appartient au début.

**P8. Lier les plans par le mouvement.** Un geste, une rotation, une descente qui continue d'un plan au suivant : 12 films sur 16. Le raccord de forme reste rare (3 sur 16), gardé pour un moment.
*Pourquoi :* l'œil suit le mouvement et ne voit pas la coupe.

**P9. Un logiciel : entrer dans l'écran**, ou reculer pour montrer que l'image était l'écran (3 logiciels sur 4). Le logiciel coupe plus vite : 24,3 plans par minute en médiane (5,3 à 32,4), contre 16,1 pour la révélation d'objet.

**P10. Faire bouger presque tout.** Images fixes : 7 % des plans. Les garder pour une image qui sort du noir, un tableau large, une photo.

**P11. Révéler aux trois quarts.** L'objet entier, seul, entre 69 et 82 % de la durée (médiane 77 %, 10 films), dans un plan tenu de 4,9 à 9,0 s. Le plan est en recul dans 5 cas sur 10, en rotation dans 3.
*Pourquoi :* assez tard pour que l'attente pèse, assez tôt pour laisser le temps de regarder.

**P12. Élargir à la fin.** Le dernier plan d'image montre l'objet entier : 13 sur 16. Il dure 6,0 à 8,5 s (quartiles), au moins 4 s dans 13 sur 16. Les 3 autres finissent sur le carton du nom, qui tient alors le rôle du plan final.

**P13. Un plan d'au moins 5 s** dans le film : 14 sur 16. Le plus long dure 8,1 s en médiane.

**P14. Noirs internes rares et courts.** 4 films sur 16, de 0,3 à 0,9 s. Un noir long avant la révélation : 1 film sur 16, un effet rare.

**P15. Le nom ferme le film.** Écrit dans 7 films sur 16, entre 83 et 96 % de la durée (médiane 94 %), 1,3 à 4,5 s (médiane 2,4 s), seul, centré, sur fond uni (5 cartons sur 5).
*Pourquoi :* le nom est la chute. Écrit plus tôt, il devient un titre et vide la révélation.

**P16. Sans orateur, toujours écrire le nom** (convention). 9 films sur 16 ne l'écrivent pas : dans 8, l'orateur le dit dans la seconde qui suit le film ; dans le neuvième, une voix off. Ici, personne ne le dira.

**P17. La taille du nom.** Discrète pour un objet (4 à 5 % de la hauteur de l'image) ; héros pour un logiciel (9 à 12 %). 2 et 2 mesures : faible.
*Pourquoi :* l'objet reste le héros de son film ; un logiciel n'a pas d'objet, son nom prend la place.

**P18. La fin : rien, un noir, ou le nom puis un noir.** Après le dernier plan d'image : rien (5 sur 16), un noir (4), le nom (3), le nom puis un noir (4). Noir final de 0,1 à 2,8 s (médiane 0,95 s). Logo seul en fin : 0 sur 16. Date ou slogan sous le nom : 0 sur 16.

**P19. Pas de carton explicatif, pas de chiffre.** 0 sur 16. Au plus une phrase d'environ 5 mots, au centre d'une zone calme (1 sur 16).
*Pourquoi :* le film montre, il n'explique pas. Un chiffre à l'écran transforme le film en slide.

**P20. La voix off, seulement pour un film de matériaux** (3 sur 16, tous de matériaux). Elle couvre 61 à 69 % du temps, se tait les 3,9 à 4,6 premières secondes et les 2,3 à 3,6 dernières (3 sur 3). L'image de l'étape arrive avant ou avec la phrase qui la nomme : 7 sur 10, dans 1 film (faible).
*Pourquoi :* l'œil voit, puis l'oreille confirme. La phrase qui précède l'image se lit comme un commentaire.

**P21. Film de fabrication : suivre l'ordre de la fabrication**, de la matière brute à l'objet fini, un plan par étape (2 sur 16, faible).

**P22. La musique porte la sortie du noir, la révélation et le nom**, pas chaque coupe (convention : le corpus de cette famille n'a pas de son ; voir G8 et § 8).

**P23. Formats 9:16 et 1:1, chapitres au-delà de 60 s sans voix** : convention (aucun film observé ; voir § 9).

### 4.4 Gabarits (convention, à partir des médianes)

Révélation tardive, 33 s :

| De → à | Temps | Contenu | Plans |
|---|---|---|---|
| 0,0 → 1,0 | ouverture | noir | 1 |
| 1,0 → 4,5 | accroche | un monde ou une matière qui sort du noir (fondu de 0,9 s) | 1 ou 2 |
| 4,5 → 24,5 | montée | détails et pièces, 1,2 à 3,5 s ; un passage de 5 plans d'environ 1,2 s vers 25 à 45 % | 9 à 11 |
| 24,5 → 30,5 | révélation | l'objet entier, recul lent, tenu | 1 |
| 30,5 → 32,9 | nom | carton seul, centré, fond uni | 1 |
| 32,9 → 33,5 | fin | noir | 1 |

Objet dès le début, 30 s : noir 0,5 à 1 s ; l'objet entier vers 1,5 s (5 %) ; 10 à 13 plans d'usage ou de fonction de 1,3 à 2,5 s, l'objet entier ou en main ; un dernier plan tenu (gamme ou usage) de 5 à 7 s ; le nom 2,4 s.

---

## 5. Ouverture et ambiance (règles A)

**Base : 20 films.** 8 ouvertures de 65 à 143 s (médiane 99 s), dont 3 sketches ou fictions ; 2 seuils ; 1 hommage ; 3 clôtures ; 6 transitions entre deux lieux.

### 5.1 Les cinq temps d'une ouverture

| Temps | Ce qu'on voit | Mesure | Compte |
|---|---|---|---|
| 1. Seuil | noir, ou carton sur noir | noir seul environ 1 s ; carton + noir 5,7 à 9,8 s | 6 sur 8 ont un seuil |
| 2. Premier plan | un plan long qui installe : lumière, détail, ou plan de situation | médiane 6,8 s | au moins 5 s : 5 sur 8 |
| 3. Corps | montage court et régulier | plan médian 1,33 s (p10 0,65 s ; p90 3,17 s ; 337 plans, 7 films) | — |
| 4. Pic | les 5 plans les plus rapides | 0,40 à 0,73 s | entre 61 et 79 % de la durée : 5 sur 7 |
| 5. Atterrissage | un plan long, souvent large, qui mène au lieu ou à la personne qui va parler | médiane 7,1 s (4,3 à 18 s) | au moins 5 s : 6 sur 8 ; au moins 3,5 fois le plan médian : 7 sur 7 |

### 5.2 Les règles

**A1. Le seuil : 0,5 à 1,5 s de noir et de silence** (convention, sur 6 seuils sur 8). Un carton de seuil, s'il y en a un : court, 5 mots ou moins de préférence (observés : 6 mots tenus 1,9 s ; un carton d'événement 4,0 s ; une citation de 16 mots 8,0 s), puis 0,8 à 4,3 s de noir. Le son part du silence dans 4 ouvertures sur 8.
*Pourquoi :* le seuil sépare le film de ce qui précède. Le silence rend la première note audible.

**A2. Un premier plan long, 5 à 10 s.** Serré (un détail, une lumière : 4 sur 7) ou large (un plan de situation : 3 sur 7), selon les rushes.
*Pourquoi :* le spectateur a besoin de temps pour entrer avant que le montage s'emballe.

**A3. Le corps coupe vite et régulier.** Plans de 0,9 à 2,1 s (quartiles), médiane 1,3 à 1,5 s. 25 à 40 changements par minute (5 ouvertures sur 7). Au plus 1 plan sur 10 au-delà de 3,2 s ; un plan long au milieu ouvre une scène ou un chapitre (6 sur 9). Le corps ne ralentit pas avant l'atterrissage : 1,60 s au premier tiers, 1,30 s au milieu, 1,24 s au dernier ; le premier tiers est le plus lent ou égal dans 6 sur 7.
*Pourquoi :* le corps donne l'énergie. S'il ralentit avant la fin, le film s'essouffle avant d'arriver.

**A4. Dans chaque scène, ouvrir large puis serrer.** 8 scènes sur 11 relevées. Les gestes et les objets en très gros plans de 0,5 à 1,3 s.

**A5. Un pic entre 60 et 80 %** : 5 plans de 0,4 à 0,7 s (5 ouvertures sur 7), sur le moment le plus fort de la musique (le son culmine après 60 % dans 7 ouvertures sur 8, médiane 68 %). Le pic n'est jamais le dernier plan.
*Pourquoi :* le film a besoin d'un sommet. Placé aux deux tiers, il laisse le temps d'atterrir.

**A6. Atterrir.** 3 à 5 plans qui s'allongent (par exemple 0,9 → 1,2 → 1,5 → 2,5 → 2,5 → 5,0 s), puis un dernier plan de 5 à 11 s, large, sur le lieu ou la personne qui va parler. Il finit sur le lieu ou la personne dans 6 ouvertures sur 8. S'il y a une personne qui parle ensuite, elle commence à parler dans ce plan (observé 3 sur 8 ; convention : continuer le plan 2 à 5 s sous ses premiers mots).
*Pourquoi :* l'atterrissage ramène au monde réel sans choc et passe la main.

**A7. Du serré vers le large sur tout le film.** Dernier plan large 5 sur 7, jamais serré (0 sur 7). Le large revient au dernier tiers dans 2 films entiers sur 3.
*Pourquoi :* on part d'un détail, on arrive au lieu. C'est l'inverse du plan de situation classique, à l'échelle du film.

**A8. Coupe franche partout.** 359 sur 367. Les fondus avec le noir sont à l'entrée (6 sur 6 dans les 10 premiers % du film). Un fondu enchaîné de 1 à 1,5 s seulement pour passer de l'animation au réel (1 cas net).

**A9. Le noir sert à entrer.** 15 noirs sur 17 sont dans les 11 premiers % du film. Exception : une ouverture « à froid » découpe son début par deux noirs de 1,5 et 1,0 s.
*Pourquoi :* un noir au milieu du corps casse l'élan.

**A10. Texte : 0 à 2, au seuil ou à la fin, jamais au milieu** (0 sur 7). Environ 0,5 s par mot (G7). Sur noir (4 sur 7) ou dans une zone calme et sombre de l'image (3 sur 7).

**A11. Peu de parole, et une fin sans parole.** 0 % de parole dans 4 ouvertures sur 8, au plus 28 % dans 3 (la fiction narrée monte à 63 %). Les films parlés finissent sur 15 à 33 s de musique seule (3 sur 3, hors fiction narrée).

**A12. Le raccord est local** (G9). Le sens du mouvement : le garder d'un plan à l'autre quand c'est la même action (convention : non démontré sur 34 coupes).

**A13. Noir et blanc pour des gens et une ambiance** : 3 films sur 20, tous montrent des gens au travail ou des portraits. La couleur pour un sommet : 1 cas (faible).

**A14. Un seul format par film** (2 sur 2). Le format large (2,35:1 ou plus) dit « cinéma » : seulement si les rushes le supportent (convention).

### 5.3 Sketch ou fiction (3 films, faible)

- Une scène dialoguée au début, puis action et musique. Dans un sketch de 85 s, le dialogue tient de 7 à 28 s, puis 33 s sans parole finissent le film. Convention : la scène parlée au plus 40 % du film.
- Ouverture à froid (1 sur 8) : un très gros plan de 2 à 3 s, puis 1 à 1,5 s de noir.
- Montage alterné entre deux lieux (1 film) : le second lieu revient toutes les 7 à 20 s (médiane 12,8 s), pour 0,7 à 2,3 s (médiane 1,5 s).
- Fiction narrée (1 film) : 6 chapitres de 14 à 29 s (médiane 26 s), chacun ouvert par une phrase de la voix off, puis l'image la montre. 25 coupes sur 62 tombent pendant une phrase.

### 5.4 Clôture et hommage (`cloture`)

- Un carton d'ouverture court (observé : 11 mots, 4,7 s), puis les visages.
- Les voix des gens couvrent la moitié à deux tiers du temps (clôture 66 %, hommage 51 %). On coupe pendant qu'ils parlent : 33 coupes sur 68.
- Bandeaux de nom petits, en bas à gauche, **après** la première apparition : tous entre 29 et 77 % du film (7 sur 7, 1 film). 2,9 s par personne en médiane, sur 1 à 3 plans. *Pourquoi :* on montre d'abord, on nomme ensuite.
- Accélérer au dernier tiers (plan médian 0,98 s), un pic vers 90 % (0,20 s en médiane glissante), puis un plan-signature de 1,7 à 8,3 s (3 films sur 4). Le logo de l'utilisateur s'il le fournit, sinon son nom (convention).
- Photos : immobiles, sur noir, dans leur format (25 sur 27), une par mesure de musique : 19 photos sur 26 durent environ 4 temps, 23 sur 26 tombent à un quart de temps près sur un nombre entier de temps (1 film). C'est le seul cas où les coupes suivent la grille de la musique.
- Clip chanté (1 film) : changer de plan au début d'un vers (9 sur 16, contre 2,5 au hasard) ; fondus courts permis ; finir en silence sur le signe final.

### 5.5 Transition entre deux lieux (`transition_decor`, 6 films)

| Mesure | Valeur | Compte |
|---|---|---|
| Durée | 11 à 31 s (médiane 23,9 s) | 6 |
| Mouvement | la caméra ou le sujet avance d'un lieu vers l'autre, sans arrêt | 6 sur 6 |
| Coupes cachées | dans un passage sombre ou flou (porte, mur, feuillage, filé) | 4 transitions sur 6 (14 coupes sur 30) |
| Plans fixes, texte | aucun | 0 sur 33 plans ; 0 sur 6 |
| Rythme | départ vif (0,1 à 2,4 s, souvent dans le sombre), arrivée lente (4 à 14 s) | — |
| Arrivée | le dernier plan est le plus long | 4 sur 5 (la sixième est un seul plan) |
| Avant la parole | l'arrivée est tenue 6,7 à 11,5 s (médiane 9,3 s) avant que la personne suivante parle, puis continue sous ses premiers mots | 5 ; 6 sur 6 |
| Musique | une même phrase musicale pour les transitions d'un film ; elle s'arrête 1,2 à 1,3 s avant la parole | 2 sur 2, faible |

*Pourquoi :* le mouvement vers l'avant dit « on y va ». Les coupes cachées donnent l'illusion d'un seul voyage.

### 5.6 Gabarit d'ouverture, 90 s (convention, à partir des médianes)

| De → à | Temps | Contenu |
|---|---|---|
| 0:00 → 0:01 | seuil | noir et silence ; ou un carton court puis 1 s de noir |
| 0:01 → 0:08 | premier plan | un détail, une lumière ou un plan de situation, 7 s |
| 0:08 → 0:56 | corps | scènes ouvertes large puis serrées ; plans de 1,3 à 1,5 s ; un plan long par scène au plus |
| 0:56 → 1:08 | pic | 5 plans de 0,4 à 0,7 s vers 62 à 70 %, sur le sommet de la musique ; puis le corps reprend |
| 1:08 → 1:22 | atterrissage | 3 à 5 plans qui s'allongent |
| 1:22 → 1:30 | dernier plan | large, sur le lieu ou la personne, 8 s ; le texte de fin ici s'il y en a un |

---

## 6. Documentaire et témoignage (règles T)

**Base : 8 films** de 78 à 324 s (médiane 142 s), plus 2 variantes sans entretien. Types de plan : entretien (la personne parle, cadrée pour ça), personne en situation, illustration (lieu, objet, archive, écran, œuvre).

### 6.1 Deux régimes

| Régime | Films | Plan médian | p10 à p90 | Coupes par minute |
|---|---|---|---|---|
| **Posé** (`pose`) : entretiens filmés, une ou quelques voix qui développent | 5 | 2,0 s | 1,0 à 4,5 s | 19,9 à 27,3 |
| **Choral** (`choral`) : beaucoup de gens, images courtes, phrases qui se répondent | 3 | 1,2 s | 0,47 à 2,6 s | 32,6 à 45,1 |

### 6.2 La structure

| Partie | Ce qui s'y passe | Repère |
|---|---|---|
| Ouverture | noir, son calme ; un texte, une voix dans le noir, ou des images sans parole | noir d'abord 6 sur 8 ; première parole à 6,0 s (2,9 à 16,5 s) |
| Entrée des voix | la voix d'abord, sur une illustration ; le visage ensuite ; le bandeau sur ce visage | 13 sur 20 ; visage 3,0 s après (1,5 à 4,7 s) |
| Corps en chapitres | une idée, une personne ou une étape par chapitre | chapitres de 19 à 35 s dans un film |
| Respirations | musique seule, 3 à 9 s, sur des images | 6 films sur 8 ; environ 0,6 par minute |
| Changement de chapitre | un noir de 0,4 à 1 s, ou un blanc, ou un carton | au plus 1 noir par film |
| Montée | posé : par le propos ; choral : des rafales | rafale finale 4 sur 8 |
| Résolution | les dernières phrases, des plans plus longs | posé : un plan d'au moins 5 s dans le dernier cinquième, 5 sur 5 |
| Fin | posé : un plan tenu ; choral : une rafale puis le logo | dernière parole 4,2 s avant la fin (0,9 à 9,5 s) |

### 6.3 Les règles

**T1. Choisir le régime d'après les rushes** et le dire à l'utilisateur avant de monter.

**T2. Monter la parole d'abord** (convention) : une piste de voix seule, faite de prises de 2 à 20 s (médiane observée 5,9 s ; p10 1,9 s ; p90 19,8 s ; 107 prises). Une prise porte une idée (convention).
*Pourquoi :* dans un documentaire, la parole est la colonne. L'image se choisit ensuite, pour elle.

**T3. Laisser respirer.** La parole couvre 77 % du film en médiane (51 à 88 %, 8 films). Dans un film posé, une respiration de 3 à 9 s sans parole, environ une par minute et demie (6 films sur 8 en ont ; 0,6 par minute en médiane).
*Pourquoi :* sans silence, le spectateur n'a jamais le temps de penser à ce qu'il vient d'entendre.

**T4. Couvrir la voix.** On voit la personne parler pendant un tiers de ce qu'elle dit (médiane 33 % ; sous 55 % dans 6 films sur 8). Les deux exceptions sont des films de réactions et de webcam, où le visage est l'image.
*Pourquoi :* la voix porte le sens ; l'image montre ce dont elle parle. Un visage qui parle tout le temps devient une radio filmée.

**T5. Faire entrer chaque personne par la voix.** On l'entend avant de la voir dans 13 cas sur 20. Le visage arrive 1,5 à 4,7 s après (médiane 3,0 s).
*Pourquoi :* la voix éveille la curiosité ; le visage y répond.

**T6. Nommer au premier visage, discrètement.** Nom et fonction, en bas à gauche ou à droite, hors du visage, petit (2,5 à 3,3 % de la hauteur pour le nom), sans boîte, 2,1 s en médiane (0,9 à 3,5 s ; 27 bandeaux), apparu en fondu après la coupe (2 sur 2). 4 films sur 8 nomment ainsi ; 3 sur 8 ne nomment personne (voix nombreuses et brèves).

**T7. Cadrer l'entretien serré, jamais large.** Sur 162 plans d'entretien : rapproché 53 %, moyen 26 %, gros plan 15 %, très gros plan 6 %, large 0. Deux plans de suite de la même personne : le second plus serré, 9 fois sur 10.
*Pourquoi :* le visage porte l'émotion. Changer de valeur entre deux plans de la même personne évite la saute à l'image.

**T8. Caméra fixe sur l'entretien** (18 sur 20) ; le mouvement va aux illustrations et aux personnes en situation.

**T9. Couper sous la voix.** 414 coupes sur 594 (70 %) tombent pendant que quelqu'un parle. Les coupes ne cherchent pas les silences (172 dans un silence, pour 162 au hasard). Le changement de voix et le changement d'image sont décalés : ils coïncident à une demi-seconde près dans 23 cas sur 57 seulement.
*Pourquoi :* une coupe qui tombe pile au changement de voix se voit. Décalée, la voix tire l'image ou la prolonge, et le fil ne casse pas.

**T10. Coupe franche partout** (98 %). Aucun fondu enchaîné entre deux plans de parole. Un seul passage au noir (0,4 à 1 s) ou au blanc, pour changer de chapitre (3 passages sur 3 sont des changements de chapitre).

**T11. La forme du rythme.** Posé : la fin n'accélère jamais (0 sur 5 de plus de 15 %) ; les plans les plus longs sont à la fin (p90 du dernier tiers 6,2 s, contre 3,4 à 3,7 s avant). Choral : la fin est plus rapide que le début (3 sur 3).

**T12. Un plan d'entretien court.** 1,77 s en médiane (p90 3,16 s, 162 plans). Au-delà de 5 s, seulement dans le dernier cinquième du film (4 sur 4).

**T13. Ouvrir par le noir et le calme.** Les 3 premières secondes sont plus basses que le niveau médian du film dans 8 sur 8 (de 9,7 à 47,8 dB, médiane 16,7 dB). Première parole entre 3 et 17 s (cible 6 s).

**T14. Finir.** Posé : les dernières phrases, puis un plan tenu de 5,7 à 8,1 s, large de préférence (5 sur 5). Choral : une rafale de 3 à 5 plans de 0,3 à 0,4 s qui montre les œuvres ou le produit, **jamais les visages** (4 sur 4), puis le logo de l'utilisateur s'il le fournit (5 films sur 8 ont un logo, 2,2 à 4,2 s). La dernière parole tombe 1 à 10 s avant la fin.

**T15. Rafales au milieu permises** (4 films sur 8) : salutations qui s'enchaînent, la même personne à plusieurs âges, des réactions. Là, les visages sont permis.

**T16. Le raccord, c'est la voix.** 17 coupes sur 48 n'ont aucun raccord d'image : la voix qui continue fait le lien. Place ou forme reprise : 10 sur 48. Image qui montre le mot entendu : 4 sur 48 ; l'illustration suit le **thème** de la phrase plus que le mot exact (1 film lu en entier).

**T17. Cartons : aucun par défaut** (3 films sur 8 n'en ont aucun). Au plus une question ou une thèse en ouverture (2 sur 8), ou 1 à 3 cartons de conclusion alternés avec l'image (1 sur 8). Petits (5,2 à 5,7 % de la hauteur, 5 sur 6), centrés (6 sur 6), 3 à 12 mots. Mots-échos (un mot que la personne vient de dire, repris en grand à l'écran) : en régime choral seulement (1 film, 10 mots sur 10 reprennent un mot entendu). Lettre tapée à l'écran : seulement si le film parle d'un écrit (1 sur 8).

**T18. Noir et blanc pour un portrait.** Les 4 films en noir et blanc, variantes comprises, sont des portraits de gens et de métiers. Mélange permis : les personnes en noir et blanc, les écrans et les œuvres en couleur (2 sur 8). Letterbox 2,39:1 seulement pour un film tout en noir et blanc (1 sur 8, convention).

**T19. Aucun chiffre à l'écran qui ne soit dit par une personne dans les rushes.** Aucun témoignage, aucun nom, aucune fonction inventés.

### 6.4 Gabarit posé, 2 min (convention, à partir des médianes)

| De → à | Partie | Contenu |
|---|---|---|
| 0:00 → 0:06 | ouverture | noir, son calme ; images sans parole, ou une question de 12 mots au plus |
| 0:06 → 0:09 | entrée | la première voix sur une illustration |
| 0:09 → 0:40 | chapitre 1 | le visage (bandeau 2,1 s) ; la voix passe aux deux tiers sur les illustrations ; plans de 1 à 4,5 s |
| 0:40 → 0:46 | respiration | musique seule sur des images, 6 s |
| 0:46 → 1:28 | chapitre 2 | ouvert par un noir de 0,5 s ou par la voix d'une deuxième personne |
| 1:28 → 1:46 | résolution | les dernières phrases ; plans plus longs |
| 1:46 → 2:00 | fin | dernière parole 4 s avant la fin ; un plan large tenu 7 s |

Choral, 90 s : même ouverture ; voix brèves de 1,9 s environ, phrases qui passent d'une personne à l'autre ; plans de 1,2 s, plus courts à la fin ; rafale finale de 3 à 5 œuvres à 0,3 ou 0,4 s vers 90 à 97 % ; logo 3,5 s.

---

## 7. Bande-annonce et usage (règles BA et U)

**Base : 6 bandes-annonces** de 50 à 119 s (médiane 89,2 s) : 2 d'une œuvre, 2 catalogues par blocs, 2 catalogues mêlés. **2 films d'usage** (60,0 et 93,5 s) : les règles d'usage reposent sur 2 cas, elles sont fragiles.

### 7.1 Les six temps d'une bande-annonce

| Temps | Place | Ce qui s'y passe | Compte |
|---|---|---|---|
| Noir d'ouverture | 0 à 1 % | 0,13 à 4,2 s (médiane 0,6 s) | 7 sur 7 mesurables |
| Accroche | 0 à 20 % | une réplique dès les premières secondes, des images de situation, beaucoup de plans larges | réplique 4 sur 5 parlées ; plans larges 6 sur 6 |
| Annonce | 15 à 25 % (catalogue) ; 29 à 45 % (œuvre) | catalogue : mots-chocs, phrase ou logo ; œuvre : un ou deux cartons de crédit | 3 sur 3 ; 2 sur 2 |
| Corps | 25 à 78 % | catalogue : blocs ouverts par leur titre ; œuvre : l'histoire en répliques | — |
| Pic | 78 à 88 % | plans les plus courts, moins de parole | 6 sur 6 |
| Fermeture | 83 à 100 % | noir, une dernière réplique (le « bouton »), noir, titre ou logo | 8 sur 8 ; bouton 4 sur 6 |

### 7.2 Les règles de la bande-annonce

**BA1. Choisir la sous-forme** (§ 2) : une histoire = œuvre ; plusieurs sujets avec titres = catalogue par blocs ; plusieurs sujets sans titres ou sans parole = catalogue mêlé.

**BA2. Raccourcir les plans jusqu'au pic, puis s'arrêter net.** Plan médian 1,20 s au premier tiers, 0,90 s au milieu, 0,77 s au dernier (384 plans). Dernier tiers plus rapide que le premier : 6 sur 6 ; chaque tiers plus rapide que le précédent : 4 sur 6. Plan d'image médian du film : 0,73 à 1,65 s.
*Pourquoi :* la vitesse monte l'envie. L'arrêt net fait tomber le titre. Ce n'est pas la forme du film produit : la bande-annonce ne révèle rien à la fin, elle s'arrête.

**BA3. Le pic entre 78 et 88 %** (6 sur 6) : les 10 secondes les plus rapides, plans de 0,62 s en médiane (0,41 à 1,46 s). Il parle peu : 21 % du temps en parole, contre 48 % sur tout le film (4 sur 5).
*Pourquoi :* au pic, les images vont trop vite pour écouter. La musique prend la place.

**BA4. Coupe franche : au moins 90 %** (observé 92 %). Le fondu enchaîné est réservé au texte qui laisse place à l'image (6 sur 8). Le fondu depuis le noir, au bouton (4 sur 4) et au titre final (4 sur 6). Aucun passage au blanc (0 sur 459).

**BA5. Le noir ponctue.** 40 noirs, médiane 0,42 s ; 21 sur 40 dans les 20 derniers %. Courts (0,1 à 0,5 s) au pic et autour du bouton. Longs (1 à 2,5 s) seulement entre les chapitres d'une œuvre (les 6 noirs longs sont tous dans les 2 bandes-annonces d'œuvre).

**BA6. Ouvrir large, puis se rapprocher.** Plans larges : 44 % au premier tiers, 28 % au milieu, 26 % au dernier ; la part baisse dans 6 films sur 6 (39 à 56 % au premier tiers). Ce qui monte au milieu, c'est le plan moyen : les personnages en situation.
*Pourquoi :* on montre d'abord où l'on est, puis qui agit.

**BA7. La voix passe par-dessus la coupe.** 94 répliques sur 108 durent pendant au moins une coupe. Une réplique dure 1,7 s en médiane (p90 3,1 s) et compte 6 mots (p90 10).
*Pourquoi :* la voix tient le fil pendant que l'image saute. C'est le procédé central de la famille.

**BA8. Parler la moitié du temps.** Parole : 48 % en médiane (28 à 58 %, borne haute). Première réplique dans les 5 premiers % (4 sur 5). Dernière réplique entre 83 et 94 % (5 sur 5).

**BA9. Le bouton.** Après le pic : un noir, puis une seule réplique sur 1 ou 2 plans (2,3 à 3,4 s), qui sort du noir par un fondu (4 sur 4), puis un noir et le titre. 4 bandes-annonces sur 6. La musique tombe juste avant : le bouton se joue presque à sec (convention).
*Pourquoi :* après la vitesse, une phrase seule fait sourire ou frissonner. Le contraste fixe le souvenir.

**BA10. Finir sur le titre ou le logo, jamais sur une image** (8 sur 8). Il commence entre 90 et 96 % de la durée et reste 3,5 s en médiane (2,5 à 4,8 s pour 7 films sur 8). Il sort du noir par un fondu, souvent dans une lueur (4 sur 6). La fermeture entière dure 8,0 s en médiane, 6 à 17 % du film.

**BA11. Catalogue par blocs : un sujet par bloc.** Un bloc dure 4,5 s en médiane (1,9 à 7,8 s ; 21 blocs) et compte 3 à 6 plans. Le titre **ouvre** son bloc (20 sur 21) et reste environ 1,0 s (0,73 à 2,27 s). 9 à 12 blocs, puis un mélange final de 12 à 13 s sans titres. À l'intérieur d'un bloc, les coupes restent dans le même sujet (29 sur 32).

**BA12. Catalogue mêlé : les sujets alternent plan par plan.** 28 coupes sur 32 changent de sujet. Le lien graphique y sert (une couleur, la place d'un visage : 8 sur 32). Une seule phrase d'annonce, ou aucun texte avant le logo.

**BA13. Œuvre : une mise en place lente.** Une mention courte sur noir ouvre le film (3 mots, 2,2 s, 2 sur 2). Les crédits (8 à 12 mots) arrivent entre 29 et 45 %. Le titre de l'œuvre à 91 et 94 %. Des noirs de chapitre longs permis.

**BA14. Le texte : un bloc à la fois** (8 sur 8). Mot-choc de 1 ou 2 mots, 1,0 à 2,3 s, sur noir, puis l'image monte dessous (3 sur 5). Part du temps avec texte : œuvre 8 à 17 %, catalogue par blocs 27 à 28 %, catalogue mêlé 10 à 14 %.

**BA15. L'image bouge de plus en plus.** Le mouvement médian monte du premier au dernier tiers dans 6 films sur 6. Plans fixes : 7,6 %.

**BA16. Garder la couleur.** Aucun film ne passe en noir et blanc, sauf 2 plans d'archive pour dire « c'est le passé ». Format large (2,0 à 2,39:1) pour une fiction : 4 sur 4 ; plein cadre 16:9 pour l'usage et les jeux : 3 sur 3.

### 7.3 Les règles du film d'usage (2 films, faible)

**U1. Quatre temps.** Ouverture (0 à 5 %) : noir, puis un plan qui découvre la situation, ou la lumière de l'objet qui bat sur le noir (2 sur 2). Scènes de vie (5 à 78 %) : des scènes de 4 à 7 plans, la situation, la personne, l'objet, ce que fait l'objet. Pic (78 à 90 %) : scènes alternées, plans de 0,37 s (1 sur 2 ; l'autre finit sur un plan de 7,4 s). Fin : une phrase de 3 à 9 mots, puis le nom ou le logo (2 sur 2).

**U2. L'objet un plan sur trois.** 10 plans sur 29 et 23 sur 73. Les coupes directes passent de la personne à l'objet ou l'inverse (8 sur 8). Le regard fait un bon raccord : la personne regarde son poignet, le plan suivant montre le cadran (1 cas).
*Pourquoi :* l'objet présent sans cesse transforme le film en démonstration ; absent, on l'oublie.

**U3. Le texte à la fin seulement** (dans les 10 derniers %, 2 sur 2). Pas de bouton (0 sur 2).

**U4. Plan médian 1,0 à 1,7 s** (2 films). Une scène s'ouvre souvent sur un plan large (3 scènes sur 5 dans un film).

**U5. La pulsation image et noir, si le sujet la motive.** Un film enchaîne 49 noirs de 0,1 à 0,6 s pour imiter un battement (1 sur 2).

**U6. La voix off est permise** (1 sur 2 : 18 phrases de 5 mots, 45 % du temps). Elle se tait au pic, puis revient pour deux phrases avant la fin.

### 7.4 Gabarits (convention : la structure observée, ramenée à la durée)

Catalogue par blocs, 90 s. Exemple : la saison d'un festival de musique, 10 concerts.

| # | Temps | De → à | Contenu | Plans |
|---|---|---|---|---|
| 1 | Noir | 0:00,0 → 0:00,6 | noir | 1 |
| 2 | Accroche | 0:00,6 → 0:15 | un plan par concert, une phrase de musicien dès 2 s ; plans larges d'abord | 10 à 12, de 1,2 s |
| 3 | Annonce | 0:15 → 0:20 | 2 ou 3 mots-chocs de 2 mots, sur noir ; l'image monte sous chacun | 3 cartons de 1 à 2 s |
| 4 | Corps | 0:20 → 1:10 | 10 blocs de 4,5 s : le titre du concert (1 s), puis 3 à 6 plans ; une réplique à cheval sur les coupes | 40 à 50, de 0,7 à 0,9 s |
| 5 | Pic | 1:10 → 1:20 | tous les concerts mêlés, sans titre, presque sans parole | 15 à 20, de 0,5 à 0,6 s |
| 6 | Fermeture | 1:20 → 1:30 | noir 0,4 s ; bouton 2,5 à 3 s ; noir 0,2 s ; titre ou logo qui sort du noir, 3,5 s | 4 à 5 |

Œuvre, 90 s. Exemple : un documentaire sur une ascension en haute montagne.

| # | Temps | De → à | Contenu |
|---|---|---|---|
| 1 | Noir et mention | 0:00 → 0:05 | noir 2 s, puis une mention de 2 ou 3 mots, très petite, sur noir (2 s) |
| 2 | Mise en place | 0:05 → 0:30 | plans larges de 1,5 à 3,5 s ; la première réplique peut attendre 20 % |
| 3 | Crédit | vers 0:27 et 0:40 | 1 ou 2 cartons de 8 à 12 mots, 2 à 3 s, sur noir ; le texte reste sur le plan suivant |
| 4 | Montée | 0:30 → 1:12 | plans de 1,5 s qui descendent à 0,7 s ; noirs de chapitre de 1 à 2,5 s permis |
| 5 | Pic | 1:12 → 1:17 | plans de 0,5 à 0,6 s ; noirs de 0,2 à 0,4 s entre les images permis |
| 6 | Fermeture | 1:17 → 1:30 | noir 1 à 2,5 s ; bouton (1 plan, 3 à 3,5 s, la réplique commence sur le noir) ; noir ; titre qui sort d'une lueur (3,5 à 7 s) ; noir |

Usage, 60 s. Exemple : une lampe frontale de course en montagne, la nuit.

| # | Temps | De → à | Contenu |
|---|---|---|---|
| 1 | Ouverture | 0:00 → 0:05 | noir 0,4 s, puis un plan qui découvre la scène, ou la lumière de la lampe qui s'allume sur le noir |
| 2 | Scènes de vie | 0:05 → 0:47 | 4 ou 5 scènes de 8 à 10 s : situation (large), personne, objet en gros plan, ce que fait l'objet ; un plan sur trois montre l'objet |
| 3 | Pic | 0:47 → 0:54 | scènes alternées, plans de 0,4 à 0,8 s ; la voix off se tait s'il y en a une |
| 4 | Fin | 0:54 → 1:00 | une phrase de 3 à 9 mots, construite par groupes sur noir ou posée sous l'objet ; puis le nom 3,5 s |

---

## 8. Le son : voix, musique, silence

**La musique est celle de l'utilisateur, dont il a les droits, ou il n'y en a pas.** Jamais une musique cherchée, téléchargée, générée ou prise dans une bibliothèque, même « libre de droits ».

| Famille | Ce que fait le son | Statut |
|---|---|---|
| Produit | pas de son mesurable dans le corpus ; la musique porte la sortie du noir, la révélation et le nom ; le film finit sur une résolution, puis un noir court | convention |
| Ouverture | part du silence (4 sur 8), monte, culmine après 60 % (7 sur 8, médiane 68 %) ; la vitesse de coupe ne suit pas le volume (3 films sur 7 seulement) | observé |
| Documentaire | fond continu sous et entre les voix (8 sur 8 : dans les silences de parole, 5,5 dB sous la voix en médiane) ; niveau stable d'un tiers à l'autre (8 sur 8) ; finit avec du son (6 sur 8) | observé |
| Bande-annonce | la musique seule porte l'accroche, le pic et le logo ; elle tombe avant le bouton ; le titre arrive sur un accent | convention (pas de son dans le corpus mesuré) |

Les règles qui en découlent :

- **Caler les grands changements, pas les coupes** (G8) : la sortie du noir, le pic, la révélation, l'atterrissage, le nom ou le titre se posent sur une attaque ou un changement de la musique, s'il y en a un à moins de 0,6 s (convention). Les coupes ordinaires suivent l'action et la parole.
- **Deux exceptions où la coupe suit la grille** : des photos fixes, une par mesure (1 film) ; un clip chanté, au début d'un vers (1 film). Au pic d'une bande-annonce, couper sur les temps forts est permis (convention).
- **La voix et l'image n'entrent pas ensemble.** Documentaire : la voix d'une personne avant son visage (13 sur 20). Voix off de matériaux : l'image de l'étape avant ou avec le mot (7 sur 10, 1 film). Ce n'est pas contradictoire : la personne s'annonce par sa voix ; la chose montrée s'annonce par son image.
- **Pas de silence numérique entre deux phrases** dans un documentaire (8 sur 8) : la musique ou le son du lieu reste dessous.
- **Un son peut précéder l'image** de 0,5 à 1,5 s pour entrer dans un nouveau lieu (convention, 1 cas lu dans les sous-titres).
- **Sans musique** (convention) : couper sur l'action et la parole ; garder les noirs d'entrée et de fin ; garder le son des rushes sous les plans qui en ont (piste A3).

---

## 9. Durée, format, couleur

### 9.1 Durées observées

| Famille, forme | Durée observée |
|---|---|
| Produit sans voix | 24 à 51 s (médiane 31,9 s, 13 films) |
| Produit avec voix off de matériaux | 54 à 128 s (3 films) |
| Ouverture | 65 à 143 s (médiane 99 s, 8 films) |
| Transition entre deux lieux | 11 à 31 s (médiane 23,9 s, 6 films) |
| Documentaire | 78 à 324 s (médiane 142 s, 8 films) |
| Bande-annonce | 50 à 119 s (médiane 89,2 s, 6 films) |
| Usage | 60,0 et 93,5 s (2 films) |

Une durée demandée hors de ces bornes est permise. Elle est marquée **convention** dans le plan de montage, et la structure s'étire ou se resserre en gardant les places relatives (révélation vers 77 %, pic entre 60 et 88 % selon la famille, nom ou titre à la fin).

### 9.2 Formats

- 16:9 plein cadre : la règle dans toutes les familles (produit 13 sur 16 ; documentaire 6 sur 7 ; usage 3 sur 3).
- Format large (2,0 à 2,39:1) : bandes-annonces de fiction (4 sur 4), 2 ouvertures sur 8, 1 documentaire tout en noir et blanc. Un seul format par film.
- 9:16 et 1:1 : **0 film observé**. Convention : mêmes règles de rythme et de structure ; chaque plan est recadré sur son sujet, jamais réduit avec des bandes ; les textes dans la zone sûre.

### 9.3 Couleur

| Famille | Noir et blanc |
|---|---|
| Produit | jamais une scène désaturée (0 sur 16) |
| Ouverture | 3 films sur 20, tous des gens au travail ou des portraits |
| Documentaire | portraits en noir et blanc (4 sur 4) ; personnes en noir et blanc, écrans en couleur (2 sur 8) |
| Bande-annonce et usage | jamais, sauf une archive (8 sur 8) |

Un étalonnage noir et blanc se fait dans le logiciel de montage. La skill le signale dans le plan de montage ; elle ne le règle pas dans les fichiers de timeline.

---

## 10. Ce qu'on ne reprend jamais

La grammaire, jamais la marque. Même « à la manière de » :

- aucune image, aucun son, aucun extrait des films mesurés ;
- aucun logo, aucune police, aucune icône d'Apple ; le logo est celui de l'utilisateur, ou rien ; la police est la sienne, sinon une police courante (Arial, Inter ou DejaVu Sans) ;
- aucune signature : ni légende qui nomme l'appareil ou le logiciel de tournage, ni logo d'une autre marque en fin de film ;
- aucune phrase des films, même traduite, ni sa forme exacte ;
- aucun chiffre, aucun avis, aucun témoignage, aucun nom inventé : ce qui manque reste visible et se demande ;
- aucune musique sans droits.

---

## 11. Observé ou convention : le récapitulatif

| Règle | Statut |
|---|---|
| Coupe franche : 83 à 98 % des changements selon la famille | observé (234, 367, 606, 459 transitions) |
| Un fondu enchaîné au plus, sur un passage choisi | observé (7 sur 234 ; 2 sur 367 ; 1 sur 606 ; 8 sur 459) |
| Le noir ouvre | observé 13 sur 16, 6 sur 8, 6 sur 8, 7 sur 7 |
| Couper sur chaque temps de la musique | non démontré (1 film sur 11 ; 16 sur 62 contre 16,4 ; 363 sur 597 contre 361,5) |
| Durée d'un carton : 1,2 s + 0,3 s par mot au moins | convention (skill sœur), rejointe par l'ouverture (0,5 s par mot, 7 cartons) |
| Produit : révélation entre 69 et 82 % | observé 10 films |
| Produit : jamais l'objet entier au premier plan d'une révélation | observé 0 sur 10 |
| Produit : nom entre 83 et 96 % | observé 7 films |
| Produit : toujours écrire le nom sans orateur | convention |
| Produit : au-delà de 60 s sans voix, en chapitres | convention |
| Ouverture : pic entre 61 et 79 % | observé 5 sur 7 |
| Ouverture : dernier plan d'au moins 5 s, large | observé 6 sur 8 ; 5 sur 7 |
| Ouverture : texte jamais au milieu | observé 0 sur 7 |
| Ouverture : continuer le dernier plan sous les premiers mots | observé 3 sur 8 ; durée de 2 à 5 s : convention |
| Documentaire : parole 51 à 88 % du film | observé 8 sur 8 |
| Documentaire : visage à l'écran pendant un tiers de la parole | observé, médiane 33 %, 6 sur 8 sous 55 % |
| Documentaire : la voix avant le visage | observé 13 sur 20 |
| Documentaire : entretien jamais large | observé 0 sur 162 |
| Documentaire : monter la parole d'abord | convention |
| Bande-annonce : dernier tiers plus rapide que le premier | observé 6 sur 6 |
| Bande-annonce : pic entre 78 et 88 % | observé 6 sur 6 |
| Bande-annonce : réplique à cheval sur une coupe | observé 94 sur 108 |
| Bande-annonce : titre ou logo final | observé 8 sur 8 |
| Usage : l'objet un plan sur trois | observé 2 sur 2, faible |
| Musique : ce qu'elle porte dans le produit et la bande-annonce | convention (pas de son dans ces corpus) |
| Formats 9:16 et 1:1 | convention (0 film observé) |
| Durée hors des bornes observées | convention |
