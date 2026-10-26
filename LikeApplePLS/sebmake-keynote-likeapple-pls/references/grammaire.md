# Grammaire condensée : présentation « à la Apple »

> La skill lit ce fichier à chaque usage. Il condense une analyse de huit keynotes (déroulé, slides, séquence d'annonce, formules) et les données de `data/`. En cas de doute sur un compte, ces fichiers font foi.
> Ici, il n'y a que des règles et des gabarits à [cases], jamais de citation.

**Comment lire.** « 8/8 » = observé dans les 8 keynotes du corpus. *Convention* = choix de la skill pour un rendu cohérent, pas une observation. Les `id` A1 à A25 sont ceux de `data/archetypes.json`.

## Direction artistique

Lis `style-visuel.md` avant d'écrire le premier texte : il montre à quoi ressemble une slide réussie, et le moteur le suit. Ce qui fait l'allure, en bref :

- **Des titres très courts et très gros**, gras, interligne serré. Un mot ou une phrase par écran, jamais un paragraphe.
- **Un surtitre d'accent** (1 à 3 mots) au-dessus du titre quand il situe le moment, et le point final du titre en accent.
- **Un moment visuel par bloc** au moins : un chiffre géant, une interface, une grille de récap. Et une slide finale forte.
- **Un design par slide** : l'archétype et sa variante, choisis dans `designs.md` d'après le contenu et les visuels disponibles. Jamais trois fois de suite la même composition.
- **Une capture manque ?** Une interface schématique dessinée prend sa place, sur le fond de la slide : des barres grises, pas des nombres. Jamais un cadre vide.
- **Un seul fond** pour le deck ; on n'en change qu'entre deux blocs.
- **Rien de l'atelier à l'écran** : ni nom d'archétype, ni numéro d'étape, ni consigne. Un `[À VALIDER]` s'affiche comme du vrai texte ; un `[À FOURNIR]` tient en 3 mots.
- **L'allure, jamais la marque** : aucune police, aucun logo, aucune image ni aucun appareil d'Apple.

## Sommaire

0. Direction artistique (ci-dessus)
1. Les règles qui ne bougent pas
2. Le conducteur type (blocs, rôles)
3. La table d'échelle par durée
4. La séquence d'annonce (16 étapes, versions courtes, variantes)
5. La construction des slides (règles, grille 16:9, étapes selon le format)
6. Le catalogue des archétypes
7. Les formules par fonction (EN, FR, tu et vous)
8. L'adaptation française
9. Le rythme

## 1. Les règles qui ne bougent pas

1. **La même personne ouvre et clôt** (8/8).
2. **Chaque bloc se ferme par un récap** (8/8).
3. **Toute annonce a un nom et un mini-récap** (8/8). Le reste de la séquence se règle selon la durée.
4. **Une idée par écran, affichée au moment où elle est dite** (8/8).
5. **Le plus gros sujet passe en dernier.**
6. **Rien n'est inventé de ce qui se vérifie.** Chiffre, prix, pourcentage, date, nom de client, logo, témoignage, capture réelle, source : l'utilisateur le fournit. Sinon, la skill écrit `[À FOURNIR : libellé]`, 3 mots au plus à l'écran, et met la consigne complète dans `a_fournir`.
   **Ce qui se rédige se propose.** Quand le brief est mince, la skill rédige elle-même la thèse, les titres, les problèmes, les descriptions de fonctions et le script, et marque chaque proposition `[À VALIDER : …]`. À l'écran, elle s'affiche comme du vrai contenu ; dans les notes, elle reste signalée ; à la livraison, l'utilisateur la valide. Une proposition ne contient jamais un chiffre, un prix, une date ni un nom : ceux-là restent `[À FOURNIR]`.
7. **La grammaire, jamais la marque.** Pas de logo, de police, d'image, d'appareil, de slogan ni de formule-signature d'Apple. Les couleurs, les polices et le produit sont ceux de l'utilisateur.

## 2. Le conducteur type

| # | Bloc | Fonction | Part du temps | Qui parle | Archétypes |
|---|---|---|---|---|---|
| 0 | Carton d'attente (option) | Faire patienter, poser le ton | 5 à 10 s | personne | A1 |
| 1 | Vidéo d'ouverture (option) | Donner le ton. Aucune annonce dedans (0/8) | 0 à 5 % (corpus : 65 à 143 s) | personne | A18, vidéo |
| 2 | Accueil | Saluer, nommer le lieu, dire le sens du jour en une phrase, donner le menu | 5 à 10 % | l'hôte | A24 ou A22, A3 |
| 3 | Aparté (option, 45 min et plus) | Une actualité hors sujet du jour : un succès récent, un chiffre de l'année | 2 à 4 % | l'hôte | A5, A18 |
| 4 | Premier relais | L'hôte passe la main | avant 15 à 20 % du temps | l'hôte | A21 |
| 5 | Blocs (1 à 6) | Annoncer, prouver, chiffrer, avec la séquence du §4 | 60 à 75 % | pivot et experts | tous |
| 6 | Dernier bloc | Le plus gros sujet, annoncé comme tel ou atteint en crescendo | 20 à 35 % du total (pris sur les blocs) | l'hôte l'ouvre | A1, A13, A5 |
| 7 | Récap global et dates | Résumer la journée, redonner toutes les dates | 3 à 5 % | l'hôte | A14, A3 repris, A20 |
| 8 | Clôture | Remercier le public, puis les équipes ; phrase finale | 1 à 3 % | l'hôte | A24 ou A22 |
| 9 | Carton final | Mentions, sources, conditions, crédits, contact | 5 à 15 s | personne | carton final (§5.1) |

**Les rôles.**

| Rôle | Chez l'utilisateur | Ce qu'il fait | Règle |
|---|---|---|---|
| Hôte | dirigeant, fondateur, responsable produit, chef de projet | ouvre, pose la thèse, annonce les plus gros noms, clôt | pas de synthé (A21) : on le connaît |
| Pivot (option, dès 30 min) | un second responsable | ouvre chaque bloc, reprend la main après chaque expert, fait les récaps de bloc | quand il existe, il parle plus longtemps que l'hôte (5/5) |
| Experts | celles et ceux qui ont fait | un ou deux passages : détail, démo | synthé au premier passage ; sa fonction dit son périmètre |
| Invités | client, partenaire | un témoignage | carton d'invité ; vrai et consenti |

- **Deux façons d'être hôte.** *Maître de cérémonie* : il revient entre chaque bloc, juge en une phrase et passe la main (choix par défaut sans pivot). *Encadrant* : il ouvre, revient pour le grand moment, puis clôt ; le pivot fait les ponts.
- **Le relais monte et descend par paliers** : expert → pivot → hôte. Le relais latéral (d'un expert à l'autre) va bien quand deux sujets s'enchaînent, surtout en vidéo.

## 3. La table d'échelle par durée

| Durée | Blocs | Écrans (indicatif) | Voix et relais | Ouverture | Séquence d'annonce | Récaps | Démo et preuves | On retire |
|---|---|---|---|---|---|---|---|---|
| 5 min | 1 | 10 à 14 | 1 voix (2 au plus), 0 ou 1 relais | 15 à 30 s, sans vidéo (carton de 5 s au plus) | courte, 6 étapes | N2 fondu dans la clôture | 1 démo de 60 s ou 1 chiffre | vidéo, aparté, sommaire, relance, preuve par des tiers (garder 1 logo ou 1 phrase) |
| 10 min | 1 ou 2 | 18 à 25 | 2 voix, 2 ou 3 relais | 30 à 60 s ; vidéo de 15 à 30 s possible | 8 étapes pour le bloc principal, 6 pour l'autre | N2 par bloc, N4 | 1 démo de 2 min, 1 preuve par des tiers | aparté, sommaire, nom raconté |
| 20 min | 2 ou 3, le dernier le plus gros | 35 à 45 | 2 à 4 voix, 5 ou 6 relais | 1 à 2 min ; vidéo de 30 à 60 s | 16 étapes pour le dernier bloc, 8 pour les autres | N2, N4 | 1 ou 2 démos, 1 témoignage | aparté |
| 30 min | 3 ou 4 | 50 à 65 | 3 à 5 voix, 8 à 10 relais ; un pivot possible | 2 à 3 min ; vidéo de 45 à 90 s ; sommaire A3 | 16 étapes pour 1 ou 2 blocs, 8 pour les autres | N1, N2, N4 (N3 si deux parties) | 2 ou 3 démos, 1 ou 2 témoignages | l'aparté, s'il ne sert pas la thèse |
| 45-60 min | 4 à 6 | 80 à 120 | 4 à 8 voix, 12 à 20 relais ; hôte et pivot | 3 à 5 min ; vidéo de 60 à 120 s ; aparté possible ; sommaire repris avant la clôture | 16 étapes par bloc majeur ; mode rafale pour les petites nouveautés | les 4 étages | 3 ou 4 démos, 2 ou 3 témoignages ; dernier bloc annoncé comme un événement | rien |

- **Écrans** = écrans distincts, pas les états d'une construction par étapes. Cadence de référence (*convention*) : environ 2 écrans par minute, jamais plus d'une minute sur le même écran hors démo et vidéo.
- **Moins de personnes que de relais ?** Changer de *mode* à la place : démo, vidéo, témoignage, question au public.
- **Fusions sous 10 min.** Ancrage et tension en une phrase. Promesse et nom ensemble. Récap, disponibilité et clôture en trois phrases.

## 4. La séquence d'annonce

### 4.1 Les 16 étapes

| n | Étape | Ce qu'elle fait | Visuel | Durée | En version courte |
|---|---|---|---|---|---|
| 1 | Ouverture de thème | Dire qu'on change de sujet, nommer le domaine | A1, A2 | 3 à 15 s | fondue dans 2 |
| 2 | Ancrage | Rappeler ce qui existe et marche : statut, héritage, chiffre d'usage | A5, A13 | 20 s à 2 min | oui, une phrase |
| 3 | Tension | Ouvrir un manque : un moment de vie, le défaut des solutions actuelles (sans les nommer), une question « et si » | A10, A8 vide | 10 à 40 s | oui, fondue dans 2 |
| 4 | Promesse | Dire que la réponse arrive, sans la nommer | orateur | 2 à 15 s | fondue dans 6 |
| 5 | Vidéo de révélation | Montrer l'objet avant de l'expliquer | vidéo, A13, A12 | 10 s à 2 min | non, sauf annonce majeure |
| 6 | Nom | Poser le mot à retenir, seul à l'écran, suivi d'un silence | A1, A2 | 1 à 5 s | **toujours** |
| 7 | Définition et verdict | Ce que ça fait pour la personne, en une phrase ; puis un jugement court | A4, A13 | 5 à 20 s | oui |
| 8 | Relais à l'expert | Passer de celui qui nomme à celui qui détaille | A21, A22 ou A24 | 5 à 40 s | non si une seule voix |
| 9 | Piliers | Pour chaque atout : titre, technique, bénéfice, chiffre, cas d'usage, commentaire bref | A1, A5, A6, A9, A11 | 1 à 20 min | 1 à 3 piliers |
| 10 | Démo | Faire voir le geste et la facilité | A10, A25 | 30 s à 5 min | 1 démo ou 1 chiffre |
| 11 | Preuve par des tiers | Faire parler d'autres : client, partenaire, presse, logos | A16, A17, vidéo | 20 s à 3 min | option |
| 12 | Relance | Ajouter un bonus quand on croit avoir fini | slide suivante | 2 à 5 s | option |
| 13 | Garde-fou | Prévenir l'objection : données, sécurité, réserves (langues, pays, bêta) | A8, A4 | 10 à 40 s | si une objection est probable |
| 14 | Mini-récap | Fermer : le nom et trois atouts | A14, A7 | 5 à 25 s | **toujours** |
| 15 | Prix et disponibilité | Combien, quand, comment l'avoir | A19, A20 | 10 s à 2 min | oui, si fournis |
| 16 | Relais retour | Rendre la main ; l'hôte juge en une phrase et enchaîne | orateur | 5 à 40 s | fondu dans la clôture |

Dans le corpus, chaque étape existe dans 8/8 keynotes, sauf la tension (7/8) et le prix (5/8 ; la disponibilité est à 8/8). Une annonce n'utilise pas les 16 : une fonction logicielle en garde une dizaine. **L'ordre est une tendance** : on peut déplacer une étape, jamais supprimer le nom ni le récap.

### 4.2 Versions courtes

**8 étapes** (10 à 20 min, ou bloc secondaire) : ① ancrage et tension (2+3) → ② promesse et nom (4+6) → ③ définition et verdict (7) → ④ 1 à 3 piliers (9) → ⑤ démo (10) → ⑥ preuve par des tiers *ou* garde-fou (11 ou 13), selon l'objection la plus probable → ⑦ mini-récap (14) → ⑧ prix, dispo et relais retour (15+16).

**6 étapes** (5 min) : ① ancrage et tension → ② nom → ③ définition → ④ une preuve (un chiffre *ou* une démo) → ⑤ récap → ⑥ disponibilité et appel à l'action.

**Placements du nom.** *En suspens* : une pause d'une à deux secondes avant le mot. *Tardif* : après la vidéo ou après quelques caractéristiques, pour un second produit du même bloc. *Catégorie d'abord* : nommer la catégorie, puis le produit. *Nom raconté* : une question sur le nom, une courte histoire, puis le nom (seulement si le nom a vraiment une histoire).

### 4.3 Les quatre variantes

| | Produit | Fonctionnalité logicielle | Service | Technologie |
|---|---|---|---|---|
| Chez l'utilisateur | un appareil, une offre packagée, une version majeure | une fonction dans un produit existant | un abonnement, une prestation | un moteur, une plateforme, une méthode, une IA |
| Durée (corpus) | 5 à 25 min | 2 à 3 min | 15 à 34 min | 5 à 37 min |
| Qui nomme | l'hôte, puis relais à l'expert | l'animateur du bloc, sans relais | l'hôte ; l'expert chiffre | l'hôte, puis l'expert technique |
| Tension | faible : le statut de l'existant suffit | courte : un moment de vie concret | forte : le manque du marché (A8 vide qui se coche d'un coup sur la promesse) | l'héritage et ce qui a changé |
| Vidéo | avant le nom | non, sauf grand chantier | vidéo d'ambiance | vidéo abstraite ou de principe |
| Preuve | chiffres contre la version précédente | démo à la première personne | chiffres de succès de l'existant, partenaires | graphique comparatif, principes annoncés en « d'abord, ensuite, enfin » |
| Prix | oui, ancré sur une base vraie | non | ancré sur la valeur totale de ce qu'il remplace | non |
| Disponibilité | date de commande, date de livraison | groupée en fin de présentation | date et zones | calendrier de transition, prérequis |
| Récap | nom, 3 atouts, A14 | nom, puis « suivant » | nom, définition, principes (A8) | 3 termes et une formule-slogan propre à l'utilisateur |
| Ordre propre | promesse, vidéo, nom, verdict, relais, piliers, options, récap, prix, dates, retour | ouverture, ancrage, tension, nom, définition, démo, relance, garde-fou, récap | ancrage long, tension, promesse, nom, relais, démo, relance, garde-fou, prix, dispo, récap | héritage, principes, nom en suspens, définition, pédagogie, preuve graphique, relance, garde-fou, récap |

**Mode rafale** pour les petites nouveautés : nom, définition, suivant ; 15 à 30 s chacune.

## 5. La construction des slides

### 5.1 Les règles

1. **Fond uni dominant** (7/8), sans texture. Chez l'utilisateur : le neutre le plus sombre ou le plus clair de sa palette. Un seul fond pour le deck (*convention*) : on n'en change qu'entre deux blocs, par catégorie (sombre pour la technique, clair pour l'usage), jamais d'une slide à l'autre dans un même bloc.
2. **Une seule linéale, grasse ou demi-grasse, centrée** : celle du design system de l'utilisateur. Sans police fournie, une linéale libre de droits. Jamais une police d'Apple.
3. **Une couleur d'accent par section ou par produit** (7/8), prise dans la palette. Une notion garde sa couleur d'un bout à l'autre.
4. **10 mots au plus par écran** (7/8), hors listes, bento, murs, citations et fiches techniques. En français, compter après traduction.
5. **Une idée par écran, affichée quand elle est dite** (8/8). Seul écart admis : la date écrite en clair à l'écran, dite en relatif à l'oral.
6. **Slide-chiffre : un chiffre géant seul**, un libellé d'une ligne qui contient la base de comparaison.
7. **Graphique** : soi en couleur, l'autre en gris, étiquette au bout de chaque courbe, pas de légende séparée, l'écart écrit. Sans graduation seulement si le public le permet (`publics.md`).
8. **Pas de note sous un chiffre par défaut** (7/7) : sources et conditions vont dans le **carton final** (8/8 : logo, mentions, sources, en petit gris). Exception : le public impose une source visible (`publics.md`).
9. **Pas de puces, pas de pied de page, pas de numéro, pas de logo sur chaque slide.** Le logo vit sur le carton final, et sur la première slide si la charte l'exige.
10. **Construction par étapes** (8/8) : liste ligne par ligne, graphique en 2 à 4 temps (l'autre, puis soi, puis l'écart), prix après le nom, bento qui s'assemble autour de sa tuile centrale, mot de disponibilité qui change sur la même image. Le moteur en tire des apparitions en fondu, et chaque slide entre par un fondu (*convention*).
11. **En salle**, tout se lit du dernier rang. **En vidéo**, la slide vit en plein cadre, puis sur un écran dans le décor.

### 5.2 La grille 16:9

Les tailles ci-dessous viennent du corpus et de conventions. Pour le rendu, `style-visuel.md` prévaut en cas d'écart.

- Référence 1920 × 1080 px ; H = hauteur, L = largeur. Marges : 6 % de L sur les côtés, 8 % de H en haut et en bas (*convention*).
- Tailles **observées** : mot de carte-titre 10 à 17 % de H (110 à 180 px) ; chiffre géant 30 à 40 % de H (325 à 430 px) ; nom du synthé environ 4 % de H.
- Tailles de **convention** : phrase-thèse 6 à 9 % de H ; libellé et lignes de liste 4 à 6 % ; prix et grand mot de disponibilité 12 à 18 % ; mentions du carton final 1,5 à 2 %. Rien sous 3 % de H, hors carton final.
- Graisse grasse pour titres et chiffres, regular pour les libellés gris ; interligne serré (1,05 à 1,15) pour les titres. Contraste du texte : au moins 4,5:1. Le gris « pas encore dit » ou « l'autre » : 35 à 45 % d'opacité.

### 5.3 Les étapes selon le format

- **Keynote, PowerPoint** : apparitions ligne par ligne ; ou une slide par état, reliées par un morphing (Magic Move, Morphose).
- **Figma Slides, Canva** : une slide par état, reliées par Smart Animate ou Match & Move, sinon par un fondu.
- **Vidéo** : chaque état devient un plan ; A21 devient une incrustation ; A22 à A25 deviennent des plans de tournage. Entre deux décors, pas de coupe sèche : fondu, raccord, déplacement.

## 6. Le catalogue des archétypes

| id | Nom | Quand | Mise en page (16:9) | Mots max |
|---|---|---|---|---|
| A1 | Carte-titre | ouvrir un chapitre ; poser un nom à l'instant où il est dit | 1 à 3 mots centrés, 10 à 17 % de H ; rien d'autre ; fond uni ou teinte de la section | 3 (5 au plus) |
| A2 | Icône ou logo + nom | annoncer une app, un module, un service | icône à 30-45 % de H, centrée ou dans le tiers gauche ; nom dessous ou à droite, nettement plus petit | 3 |
| A3 | Sommaire typographique | dès 3 blocs : juste après l'accueil, repris tel quel avant la clôture | 3 à 6 noms de blocs, un par ligne, 8 à 12 % de H, alignés à droite ou centrés, chacun dans sa couleur ; en reprise, la ligne en cours en couleur, les autres grisées | 3 par ligne |
| A4 | Phrase-thèse | après une démo ou un chiffre, pour fixer le bénéfice | 1 ou 2 lignes centrées, 6 à 9 % de H, texte seul, sans pictogramme | 8 (10 au plus) |
| A5 | Gros chiffre + libellé | prouver un bénéfice juste après l'avoir dit | chiffre centré à 30-40 % de H avec son unité (×, %, h) ; libellé d'une ligne dessous, 4 à 6 % de H, base de comparaison comprise | le chiffre + 9 |
| A6 | Graphique comparatif | partie technique : performance contre une base | titre en haut (5 à 7 % de H) ; graphique au centre sur 60 à 70 % de L ; soi en accent, l'autre en gris ; étiquette au bout de chaque courbe ou barre ; écart écrit | titre de 5 + étiquettes de 1 à 3 |
| A7 | Liste sans puces | énumérer des bénéfices ; plan d'un sous-chapitre | 2 à 6 lignes centrées ou à gauche, 4 à 6 % de H ; la ligne dite pleine, les suivantes grisées | 5 par ligne |
| A8 | Liste à coches | confiance, sécurité, conformité ; récap d'un service | 3 à 6 lignes, chacune précédée d'un pictogramme de couleur ; ou des cercles vides qui se cochent sur la promesse | 4 par ligne |
| A9 | Objet + texte | détailler une fonction ou une caractéristique | objet ou capture sur 50 à 60 % de L ; de l'autre côté un mot, une affirmation ou 3-4 lignes ; variante annotée avec des filets vers l'objet | 4 lignes de 4 |
| A10 | Capture plein cadre | toute explication de fonction logicielle | capture nue ou appareil générique sans marque, centré, 80 à 95 % de H ; aucun texte ajouté ; barre d'état propre, données de démo neutres | 0 ajouté |
| A11 | Schéma à bloc surligné | architecture, composant, processus | schéma au trait sur 40 à 60 % de L ; un bloc allumé à la fois, relié par un filet à une légende latérale (un titre, 5 lignes grises au plus) | titre + 5 lignes courtes |
| A12 | Vue intérieure | montrer ce qu'il y a dedans : couches, composants | rendu sombre plein cadre, éléments séparés, mouvement lent | 1 étiquette |
| A13 | Produit seul | révélation, puis appui de chaque caractéristique | objet centré à 50-70 % de H, ombre douce, fond selon la catégorie ; aucun texte | 0 |
| A14 | Bento | fin de bloc, pendant la phrase de récap | tuile centrale 2 à 3 fois plus grande (nom ou objet) ; autour, 8 à 20 tuiles arrondies de tailles inégales, chacune un visuel et 1 à 4 mots ou un chiffre | 4 par tuile |
| A15 | Mur d'abondance | dire « il y en a beaucoup » sans détailler | grille dense qui déborde du cadre : intégrations, écrans, fonctions, logos autorisés ; texte volontairement trop petit | 0 à lire |
| A16 | Logos partenaires | preuve d'adoption juste après l'annonce | logos monochromes en ligne ou en grille régulière (5 rangées au plus), sans texte ; seulement ceux que l'utilisateur a le droit d'afficher | 0 |
| A17 | Citation ou témoignage | preuve sociale, en ouverture de section ou après un lancement | 2 à 4 lignes grasses alignées à gauche, 5 à 7 % de H ; source sur une ligne dessous, en gris ; citation réelle et autorisée | 25 + la source |
| A18 | Photo plein cadre | émotion avant l'argument ; preuve de qualité | photo sur tout le cadre ; cartouche translucide en bas à droite si c'est un exemple produit | 0 (+ cartouche) |
| A19 | Prix | fin du bloc, juste avant la disponibilité | objet à gauche (40 à 50 % de L) ; à droite : nom en gras, « À partir de » en petit gris, prix en gros, précision en gris (HT ou TTC, période) ; 2 offres au plus, 4 pour une gamme | 6 par offre |
| A20 | Disponibilité | dernière étape d'une annonce, ou groupée en fin | petit libellé gris (« Disponible », « Dès le ») au-dessus d'un grand mot ou d'une date ; objet dessous ou à côté ; le grand mot change sur la même image | 4 |
| A21 | Synthé nom et fonction | première apparition d'un intervenant, jamais l'hôte | deux lignes sans fond en bas à gauche (à droite si l'orateur est à gauche) : nom en gras, fonction en regular ; tenu 4 à 6 s | nom + fonction |
| A22 | Plan large + écran | scène ou vidéo : respiration, entrée d'un intervenant | orateur en pied sur un côté, 1/10 à 1/4 de H ; écran avec la slide sur 50 à 70 % de L | — |
| A23 | Orateur dans la slide | vidéo : plan de parole par défaut | orateur en plan taille sur un tiers ; la slide remplit le fond, coupée par le bord | — |
| A24 | Décor sans écran | vidéo : accueil, relais, cadrage | orateur centré dans un lieu lié au sujet, en pied puis en plan taille | — |
| A25 | Démo manipulée | juste après l'annonce d'une fonction | mains qui tiennent l'appareil devant un fond uni, ou orateur au poste de démo avec l'écran en grand ; alterner plan large, mains, plein cadre | — |

A21 à A25 sont des plans, pas des slides : en salle, ils deviennent des indications de mise en scène dans le script ; en vidéo, des plans à tourner.

Ce tableau dit quand prendre chaque archétype. Comment le dessiner (variantes de composition, contenu visuel, profondeur, visuel à préparer et repli) : `designs.md`, une fiche par archétype.

## 7. Les formules par fonction

### 7.1 Tu ou vous : deux réglages distincts

- **Envers le public (P).** La skill le demande. Le vouvoiement est la règle du corpus français (4/4). Le tutoiement va bien en vidéo ou à l'écrit, quand une seule personne regarde. Devant une salle, le pluriel de « tu » est « vous » : on garde « vous », mais le ton devient familier (« on » au lieu de « nous », pas de « nous avons le plaisir »).
- **Entre intervenants (I).** La skill le demande aussi. Le corpus tutoie entre collègues et vouvoie le public. Le vouvoiement entre intervenants convient à une équipe qui se vouvoie au quotidien, ou face à un invité extérieur.
- Les deux se combinent. Le cas le plus courant : tu entre collègues, vous au public.
- **En anglais**, pas de tu ni de vous. Le réglage équivalent : prénom seul (familier) ou prénom, nom et fonction (formel).

Dans les tables : une seule forme = elle vaut pour tous les registres. « P-tu » = public tutoyé ; « I-vous » = intervenants qui se vouvoient.

### 7.2 Ouverture et cadrage

| EN | FR | Variante | Note |
|---|---|---|---|
| Good [morning], and welcome to [lieu / événement]. | Bonjour, et bienvenue à [lieu / événement]. | — | salut + lieu (7/8) |
| Today is a [big] day for [X]. | Aujourd'hui est un [grand] jour pour [X]. | — | le sens du jour en une phrase |
| We have [a lot] to [show you] today. | Nous avons [beaucoup] à vous [montrer] aujourd'hui. | P-tu : On a [plein de choses] à te [montrer]. | annonce le menu (A3) |
| At [entreprise], [valeur] [is / has always been] [X]. | Chez [entreprise], [valeur] fait partie de [X]. | — | thèse ; une seule par présentation |
| This year, we're [verbe] [X]. | Cette année, nous [verbe] [X]. | familier : Cette année, on [verbe] [X]. | marqueur de temps (8/8) |
| Our goal was simple: [verbe] [X]. | Notre objectif était simple : [verbe] [X]. | — | cadrage d'un bloc |
| Today, [X] [fait A]. But [obstacle]. | Aujourd'hui, [X] [fait A]. Mais [obstacle]. | — | tension |
| What if you could [X]? | Et si vous pouviez [X] ? | P-tu : Et si tu pouvais [X] ? | tension ; rare hors logiciel |

### 7.3 Annonce du nom et verdict

| EN | FR | Variante | Note |
|---|---|---|---|
| Introducing [Nom]. | Voici [Nom]. | — | forme sèche, posée sur le nom seul (A1) |
| Today we're [launching / introducing] [X]. | Aujourd'hui, nous lançons [X]. | familier : Aujourd'hui, on lance [X]. | forme pleine (8/8) |
| And we call it… [Nom]. | Et nous l'avons appelé… [Nom]. | familier : On l'a appelé… [Nom]. | nom en suspens : 1 à 2 s de pause |
| We're [proud] to [introduce] [X]. | Nous avons [le plaisir] de [vous présenter] [X]. | P-tu : On est [fiers] de te [présenter] [X]. | FR : le plaisir plutôt que l'excitation |
| [Nom] is the [simple] way to [bénéfice] without [douleur]. | [Nom] est le moyen [simple] de [bénéfice] sans [douleur]. | — | définition (étape 7) |
| [Nom] is [truly] [adj]. | [Nom] est [vraiment] [adj]. | — | verdict de l'hôte ; FR sans « je pense » |

### 7.4 Superlatifs (le registre ne change rien)

| Niveau | EN | FR | Condition |
|---|---|---|---|
| 1. relatif à soi | our most [adj] [X] yet | notre [X] le plus [adj] à ce jour | vrai par rapport à ses propres versions |
| 1 | the [adj-est] [X] we've ever [made] | le [X] le plus [adj] que nous ayons jamais [conçu] | idem ; plutôt pour un produit |
| 1 | [adj-er] than ever | plus [adj] que jamais | idem |
| 2. première | for the first time, [X] | pour la première fois, [X] | doit être vrai ; « chez nous » si le doute existe |
| 3. absolu | the world's [first / fastest] [X] | le [premier / plus rapide] [X] au monde | preuve externe, citée |
| 3 | [industry-leading / best-in-class] [X] | la meilleure [X] du marché | preuve externe, citée |
| 3 | [X], by far | [X], et de loin | preuve externe, citée |

Un superlatif par annonce, au plus. Le dosage par public est dans `publics.md`.

### 7.5 Chiffres et comparaisons

| EN | FR | Note |
|---|---|---|
| [N] times [more adj] than [base] | [N] fois plus [adj] que [base] | la base est dite **et** écrite dans le libellé A5 |
| up to [N] [unité] | jusqu'à [N] [unité] | toujours avec sa condition (`publics.md`) |
| [N] more [unité] than [base] | [N] [unité] de plus que [base] | base : la version précédente, de préférence |
| [N]% [faster] than [base] | [N] % plus [adj] que [base] | espace insécable avant « % » |
| That's enough to [équivalent concret]. | De quoi [équivalent concret]. | traduit le chiffre en vie réelle |
| over [N] [millions] [objets] every [période] | plus de [N] [millions] de [objets] chaque [période] | chiffre d'usage, dans l'ancrage |

### 7.6 Relance et transitions

| EN | FR | Note |
|---|---|---|
| Now, let's talk about [X]. | Parlons maintenant de [X]. | connecteur universel (8/8) |
| Next, let's turn to [X]. | Passons à [X]. | changement de bloc |
| And that's not all: [bonus]. | [Et] ce n'est pas tout : [bonus]. | ouvre souvent le meilleur argument |
| [Before we close], one last [announcement]: [X]. | [Avant de terminer], une dernière [annonce] : [X]. | une seule fois, pour le plus gros sujet ; jamais la formule-signature d'Apple ni sa traduction |

### 7.7 Relais aller et retour

| Sens | EN | FR | Variante |
|---|---|---|---|
| Aller | Here's [Prénom] to tell you [more]. | Voici [Prénom], qui va vous [en dire plus]. | P-tu : … qui va t'[en dire plus]. |
| Aller | To tell you [more] about [X], here's [Prénom]. | Pour vous [en dire plus] sur [X], voici [Prénom]. | P-tu : Pour t'[en dire plus]… |
| Aller formel | Please welcome [Prénom Nom], [fonction]. | J'invite [Prénom Nom], [fonction], à me rejoindre. | — |
| Aller direct | [Prénom], over to you. | I-tu : [Prénom], je te [laisse] la parole. | I-vous : [Prénom], je vous [laisse] la parole. |
| Latéral | Now, over to [Prénom] to tell you about [X]. | Je [passe] la parole à [Prénom], qui va vous [parler] de [X]. | — |
| Réception | Thanks, [Prénom]. | Merci, [Prénom]. | en vidéo, l'arrivant commence plutôt par une thèse |
| Retour | Back to you, [Prénom]. | I-tu : À toi, [Prénom]. / Je te [rends] la parole. | I-vous : À vous, [Prénom]. / Je vous [rends] la parole. |
| Retour neutre | Now, back to [Prénom]. | Retour à [Prénom]. / Je [repasse] la parole à [Prénom]. | — |
| Reprise de l'hôte | Thank you, [Prénom]. [Verdict]. | Merci, [Prénom]. [Verdict d'une phrase]. | — |

### 7.8 Démo

| EN | FR | Variante |
|---|---|---|
| Let's [take a look] at [X]. | Voyons [X] ensemble. | P-tu : Regarde [X]. |
| Let me show you [how X works]. | Je vais vous montrer [comment ça marche]. | P-tu : Je te montre [comment ça marche]. |
| I just [geste], and [résultat]. | Il suffit de [geste], et [résultat]. | — |
| Check this out: [X]. | Et regardez : [X]. | P-tu : Et regarde : [X]. |
| As you just saw, [X]. | Comme vous [venez de le voir], [X]. | P-tu : Comme tu [viens de le voir], [X]. |
| [Prénom] will show you [X] live. | [Prénom] va vous faire [une démonstration] en direct. | P-tu : … va te faire [une démo] en direct. |

### 7.9 Témoignage et invité

| EN | FR | Note |
|---|---|---|
| We've been working with [partenaire] to [X]. | Nous travaillons avec [partenaire] pour [X]. | partenaire réel, accord obtenu |
| Let's hear from [qui]. | Écoutons [qui]. | avant une vidéo de témoignage |
| It's [remarkable] to see how [produit] helps [qui] [X]. | C'est [remarquable] de voir comment [produit] aide [qui] à [X]. | phrase de l'hôte après le témoignage |
| Here's what [client / média] says about [X]. | Voici ce qu'en dit [client / média]. | avant A17 ; texte réel et autorisé |

Sans témoignage fourni : `[À FOURNIR : témoignage client]` à l'écran, et la consigne (qui, sur quoi, accord obtenu) dans `a_fournir`. La skill n'en écrit jamais, pas même en `[À VALIDER]`.

### 7.10 Prix et disponibilité

| EN | FR | Variante |
|---|---|---|
| [Produit] starts at [prix]. | [Produit] est [disponible] à partir de [prix]. | — |
| [Produit] starts at [prix], [the same price as / less than] [base]. | [Produit] est [proposé] à partir de [prix], [au même prix que / moins cher que] [base]. | l'ancre doit être vraie |
| [X] will be available [date]. | [X] sera disponible le [date]. | — |
| You can [order / sign up] today; [X] ships [date]. | Vous pouvez [commander] dès aujourd'hui ; [X] arrive le [date]. | P-tu : Tu peux [commander]… ; à l'écran : [Commandez / Commande] dès aujourd'hui. |
| [X] is coming [later this year / next month]. | [X] arrive [plus tard dans l'année / le mois prochain]. | — |
| [X] is available [at no extra cost] [with Y]. | [X] est disponible [sans surcoût] [avec Y]. | — |
| Pricing and details [on date]. | Tarifs et détails [le date]. | quand le prix n'est pas encore fixé |

### 7.11 Récap

| Étage | EN | FR |
|---|---|---|
| N1 fonction | So that's [X]. | Voilà pour [X]. |
| N2 produit ou bloc | So that's [Nom]: [A], [B] and [C]. | Voilà pour [Nom] : [A], [B] et [C]. |
| N2 | And that's [Nom], [définition en une ligne]. | Voilà pour [Nom], [définition]. |
| N3 partie ou gamme | Our [all-new] [X] lineup. | Notre [toute nouvelle] gamme de [X]. |
| N4 événement | What a [big] day for [X]. | Quelle journée pour [X] ! |

### 7.12 Clôture

| EN | FR | Variante |
|---|---|---|
| We can't wait [for you] to [verbe]. | Nous avons [hâte] que vous [verbe]. | familier : On a [hâte] que vous [verbe]. P-tu : On a [hâte] que tu [verbe]. |
| [Mission dite dans les mots de l'utilisateur]. | [Mission]. | reprend la thèse de l'accueil |
| I'm [proud] of the teams who [made] [X] possible. | Je suis [fier / fière] des équipes qui [ont rendu] [X] possible. | merci aux équipes : nommer ce qu'elles ont fait |
| Thank you for [your time / being here]. | Merci [de votre attention / d'être venus]. | P-tu (vidéo) : Merci d'avoir regardé [X]. |
| Have a great [day / event]. | Excellente [journée / fin de salon] ! | P-tu : Passe une excellente journée ! |

## 8. L'adaptation française

1. **« Voici »** rend trois formules anglaises : l'annonce du nom, la révélation et l'aller du relais. Varier ensuite : « [Prénom] va vous [en dire plus] », « Je [passe] la parole à [Prénom] ».
2. **« ever »** devient « à ce jour » pour un produit, « depuis sa création » ou « sans précédent » pour un logiciel ou un service.
3. **À l'écran, l'impératif** pour l'appel à l'action (« Essayez », « Réservez » ; P-tu : « Essaie »). **À l'oral**, « vous pouvez » reste naturel.
4. **Prix** dans la devise du public, au format français : chiffre avant le symbole, espace insécable pour les milliers (1 099 €). Préciser HT ou TTC, et la période (/mois, /an). « Starts at » devient « à partir de ».
5. **Dates** à la française : « le 19 mars », jamais d'ordinal sauf « le 1er ». À l'écran la date en clair ; à l'oral, « jeudi », « le mois prochain ».
6. **Unités** converties en métrique (km, kg, °C) ; les tailles d'écran restent en pouces.
7. **L'avis personnel s'efface** : « je pense que [X] est incroyable » devient « [X] est vraiment remarquable ». « We're excited to » devient « Nous avons [le plaisir] de » (vous) ou « On est [fiers] de » (familier).
8. **Le français varie là où l'anglais répète** : alterner les formules de relais et de transition d'un bloc à l'autre.
9. **Les publics nommés à l'oral** suivent la charte de l'utilisateur. Par défaut : doublets à l'oral (« celles et ceux qui… »), mot épicène à l'écran plutôt qu'un point médian (place et lisibilité).
10. **Typographie** : espace insécable avant « : ; ! ? » et « % », guillemets « », virgule décimale (1,5).
11. **Le français est plus long** que l'anglais : recompter les 10 mots par écran après traduction ; couper plutôt que réduire la taille. Le texte à l'écran se traduit aussi, mot pour mot comme le script.

## 9. Le rythme

1. **Changer de voix toutes les 3 à 4 minutes** (6/6 en préenregistré), et passer la main tôt (avant 15 à 20 % du temps). Avec une seule voix, changer de mode au même rythme : démo, vidéo, témoignage.
2. **Ouvrir et fermer avec la même personne** (8/8). La clôture reprend les mots de la thèse d'ouverture ; le sommaire A3 est réaffiché tel quel.
3. **Garder le plus gros pour la fin.** Les blocs montent en puissance, du plus simple au plus fort. Le dernier est le plus long (20 à 35 % du total) ; on peut l'annoncer dès le sommaire.
4. **Les récaps s'emboîtent**, et chaque étage reprend les mots du dessous :
   - N1 fonction, toutes les 4 à 7 min, par l'expert ;
   - N2 produit ou bloc, toutes les 6 à 16 min, avec A14 ;
   - N3 partie ou gamme, 1 à 3 par présentation, par le pivot ;
   - N4 événement, une fois, par l'hôte, juste avant la clôture.
5. **Un récap avant le relais retour**, le plus souvent (2 fois sur 3) ; sinon une phrase-bilan.
6. **Un silence après le nom** : 1 à 2 s en salle ; en vidéo, un coup de musique ou un silence. Ne pas meubler.
7. **Une phrase-bilan d'une ligne** à la fin de chaque bloc, par l'hôte ou le pivot.
8. **En salle**, la vidéo se lance depuis la scène, sur un noir. **En vidéo**, aucune pause pour des applaudissements : l'orateur dit lui-même l'effet en une phrase courte.
