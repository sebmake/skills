---
name: sebmake-motiondesign-likeapplepls
description: "Dit quoi animer et comment, élément par élément (titre, liste, chiffre, logo, produit, capture, caméra, transitions), selon le mouvement mesuré image par image dans 8 keynotes Apple, puis écrit et exécute le script After Effects ou EffectCraft ; compose aussi un film de fonctionnalités, ou un plan-séquence d'interface démonté en calques lisibles (caméra, halos, curseur, voix, sous-titres), le relit et reporte les retouches faites à la main. Use it whenever someone wants Apple-style motion design or keynote-style animation, asks to animate a title, a logo or a UI screenshot 'like Apple', wants a feature video or a narrated UI walkthrough, wants to understand or rework an animation layer by layer, wants an After Effects, EffectCraft or ExtendScript script or asks which easing or duration to use, even without the word Apple. Not for slide decks (sebmake-keynote-likeapple-pls), not for a product film rendered with HyperFrames (sebmake-videopresentation-likeapplepls)."
---

# Motion design à la manière des keynotes

Cette skill fait trois choses, dans cet ordre :

1. elle dit **quoi animer et comment**, pour chaque élément d'une vidéo de motion design : quelle propriété, quelle recette, quelle durée, quelle courbe, quelle amplitude, à quel moment, et ce qu'il ne faut pas faire ;
2. elle **écrit le script** qui construit l'animation dans After Effects ou dans EffectCraft, et l'exécute quand c'est possible ;
3. elle **laisse un projet qu'on comprend et qu'on reprend** : chaque mécanique a son calque nommé par son rôle, la skill montre comment la scène est faite (carte des calques, capture de l'outil, comparaison), la relit en chiffres (sonde de la composition, mesure du rendu), et reporte dans sa source les retouches faites à la main. On continue ainsi à travailler dans l'outil, tour après tour.

Les valeurs viennent de quatre analyses image par image de 8 keynotes (2019 à 2026) : 145 textes, 122 mouvements d'objets, 189 mouvements d'écrans, 182 transitions. Chaque règle porte son compte (« N sur M ») ; ce qui n'est pas mesuré est marqué **convention**. La skill reprend la **grammaire** du mouvement, jamais la **marque** : couleurs, polices, images, logos et textes sont ceux de l'utilisateur.

Le champ : la vidéo de motion design (textes, produits, captures, logos qui bougent), y compris le **plan-séquence d'interface** (une fenêtre, une caméra qui va d'un élément à l'autre, halos, curseur, voix et sous-titres : la **scène démontée**, `references/scene-demontee.md`) et le **film de fonctionnalités** qui présente un produit logiciel par ses composants d'interface, ses verbes et des formes qui jouent (`references/film-fonctionnalites.md`). Pas les slides, pas l'animation d'une application (ses transitions, ses micro-interactions) : une capture d'écran est animée comme une image dans le film.

Tout part d'un fichier : `motion.json` pour une animation d'éléments, `scene.json` pour une scène démontée. Le moteur en tire un script ExtendScript (ES3) qui tourne dans les deux outils. Corrige toujours le `.json`, jamais le `.jsx` : il est réécrit à chaque génération. Une retouche faite à la main dans l'outil se relit (`sonde_ec.py`) et se reporte dans le `.json`.

```bash
SKILL="<dossier de ce SKILL.md>"   # souvent ~/.claude/skills/sebmake-motiondesign-likeapplepls
```

Prérequis : Node, Python 3.9 ou plus, ffmpeg et ffprobe. After Effects, ou EffectCraft lancé avec son canal de contrôle. S'il en manque un, dis-le : la skill peut aller jusqu'au script contrôlé sans outil installé. N'installe rien sans accord.

## Étape 1 — Recueil

Relis la demande et les pièces jointes. Ne redemande rien de ce qui est déjà dit.

Pose les questions manquantes avec l'outil AskUserQuestion s'il existe, sinon en clair, en un seul message. **4 questions au plus par appel**, 4 choix au plus par question (plus « Autre »).

| Question | Choix | Pourquoi |
|---|---|---|
| Quel genre de vidéo ? | une animation d'éléments (titres, produit, captures) ; un film de fonctionnalités d'un produit logiciel (verbes + composants d'interface + formes) ; un plan-séquence d'interface ou une démonstration narrée (fenêtre, caméra, halos, curseur, voix, sous-titres) ; une animation existante à démonter pour la comprendre et la reprendre | Le deuxième genre a sa fiche (`film-fonctionnalites.md`, recueil au § 7) ; les deux derniers ont la leur (`scene-demontee.md`, format au § 2). |
| Quels éléments faut-il animer ? (choix multiples) | des textes (titre, phrase, liste, chiffre) ; une image de produit ; des captures d'écran ; un logo de fin (icônes, formes, fond : dans « Autre ») | Chaque type a ses recettes (`elements.md` § 1). |
| Dans quel outil ? | After Effects ; EffectCraft ; les deux | Le script est le même ; seule l'exécution change (`outils.md`). |
| Format et durée | 16:9, durée selon le plan (conseillé) ; 16:9, durée fixe (dites-la) ; 9:16 vertical ; 1:1 carré | Le corpus est en 16:9 ; 9:16 et 1:1 sont des conventions (mêmes valeurs en u). |
| Habillage | un lien vers mon design system ; mes couleurs en HEX et mes polices ; valeurs neutres pour l'instant | La skill ne connaît pas son identité. |

**Puis le brief, en clair**, avec seulement les lignes encore sans réponse :

```
Textes : [le texte exact de chaque titre, phrase, liste, libellé]
Chiffres : [valeur] · [ce qu'elle compte] · [source]        (aucun si vous n'en avez pas)
Fichiers : [chemin de chaque image : produit détouré, captures, logo]
Ordre : [ce qui vient d'abord, ce qui ferme]                 (facultatif)
```

Pour un **plan-séquence d'interface**, le brief est celui de `scene-demontee.md` § 2 : la fenêtre seule (capture ou vidéo, sans caméra, pas plus grande que la composition ; ×2 et format `16:9-4k` pour zoomer net), les éléments à montrer dans l'ordre avec leur rectangle dans la capture, la voix (fichiers, ou les phrases à faire dire) et les sous-titres, la musique et ses droits. Pour **démonter une animation existante**, il faut la fenêtre rendue seule et les trajectoires (clés de caméra, points du curseur, rectangles des halos, instants), lues dans sa source.

**La voix off.** Si l'utilisateur a ses fichiers de voix, on les prend. Sinon, la skill peut les fabriquer :

```bash
python3 "$SKILL/scripts/voix.py" etat                       # edge-tts est-il là ?
```

- **edge-tts absent** : recommande-le, dans une question (AskUserQuestion) : « Pour de meilleurs résultats, voulez-vous installer edge-tts ? Voix naturelles et gratuites (Vivienne, Denise, Henri…), internet requis. » Choix : installer edge-tts (conseillé) ; une voix de macOS, robotique, pour un brouillon ; j'ai mes propres voix ; pas de voix. Sur son accord seulement : `python3 -m venv ~/.venv-sebmake-voix && ~/.venv-sebmake-voix/bin/pip install edge-tts`.
- **Le texte d'abord** : les phrases sont les siennes, ou proposées et marquées « à valider » ; rien n'est dit avant son accord.
- **L'audition** : `voix.py audition phrases.txt --voix Vivienne,Denise,Henri,Remy,Eloise --sortie audition/` ; il choisit à l'oreille.
- **La génération** : `voix.py generer phrases.txt --voix <choix> --sortie voix/` → un fichier par phrase et `voix/voix.json` (durée, instant de chaque mot). Les durées placent les phrases sans chevauchement ; l'instant des mots pose un mouvement ou un clic sur le mot qui l'annonce.
- edge-tts passe par un service en ligne de Microsoft, gratuit mais non officiel : dis-le si le film sort de l'entreprise. La voix de macOS ne donne pas l'instant des mots.

Pour un **film de fonctionnalités**, le brief prend la forme de `film-fonctionnalites.md` § 7 : une ligne par argument, *verbe + complément* et le composant qui le prouve, puis les exports (écran entier, composant découpé, deux états si on le manipule), la promesse, le son, les formes et la couleur de fond de chaque chapitre. Un argument sans composant ne tient pas dans le film : dis-le.

Dis ce que deviendra ce qui reste vide : un texte manquant sera proposé et marqué « À VALIDER » ; un chiffre manquant restera `[À FOURNIR]` ; une image manquante sera remplacée par un repli neutre (un cadre et ses diagonales), au bon format.

**Lire l'habillage.** Avec un lien, lis-le avec les outils de la session (Figma : `get_variable_defs` et `get_screenshot`, après la skill Figma que ces outils demandent ; Notion ; page web ; PDF). Remplis les rôles du thème : `fond`, `texte`, `secondaire`, `accent`, `voile`, `lumiere`. Lien illisible : dis-le et demande les HEX. Couleurs décrites sans HEX : propose des HEX et fais-les valider. Ne choisis jamais une palette qu'il n'a pas vue. Les polices s'écrivent en noms PostScript (`Inter-SemiBold`) ; EffectCraft fournit Inter. Une police propre à un fabricant (SF, New York…) est refusée par le contrôle : propose une linéale libre et dis pourquoi.

**Préparer les fichiers.** Crée un dossier de travail (dans le dossier courant, sauf s'il en nomme un autre) avec `images/`, et copies-y ses fichiers. Taille : `ffprobe -v error -show_entries stream=width,height -of csv=p=0 <fichier>`. Produit : PNG détouré, assez grand pour la poussée (×1,27 en moyenne). Captures : définition native ou ×2, sans données personnelles (floute-les ou demande une capture de démonstration). Logo : le sien seulement. Pour un éclaté : une image par pièce, de même cadre.

## Étape 2 — Le plan d'animation, avant tout script

Lis `references/principes.md` (une fois par conversation), puis, dans `references/elements.md`, la fiche de chaque type d'élément demandé, et § 17 pour l'ordre d'une séquence. Pour un film de fonctionnalités, lis aussi `references/film-fonctionnalites.md` : l'ordre du film (§ 2), le verbe (§ 3), le composant sorti de l'écran (§ 4), les formes (§ 5), le fond par chapitre (§ 6). Ses valeurs sont des conventions tirées de deux films : écris-le dans le plan.

**Pour un film (pas pour un élément isolé), d'abord trois concepts.** Propose trois idées centrales qui diffèrent par l'image, pas par l'ordre des écrans (`scene-demontee.md` § 5) : pour chacune, l'image d'accroche, ce qui passe d'un temps à l'autre, ce qu'elle s'interdit, et si le film **coupe** (la grammaire des keynotes, P1) ou **se tient en un plan**. L'utilisateur choisit ; le plan suit son choix.

Pour chaque élément, choisis :
- **quoi animer** : la propriété (opacité, position, échelle, rotation Y, lumière, caméra parente) ; souvent rien (« coupe ») ;
- **la recette** du moteur, de l'époque choisie (`2024-2026` par défaut, `2019-2020` pour un rendu plus calme sur les écrans et plus joueur sur les chiffres) ;
- **le moment** : coupe sur le fond vide, entrée, ce qui suit (`avec`, libellé, `puis`), maintien, sortie par coupe ;
- **ce qu'on écarte**, et pourquoi.

Montre le plan **avant** d'écrire `motion.json`, en un tableau, une ligne par élément ou par geste :

| # | Élément | De → à | Quoi animer | Recette | Durée, courbe, amplitude | Ce qui traverse | Pourquoi (compte) |
|---|---|---|---|---|---|---|---|
| 1 | titre | 0,1 → 3,0 s | opacité, puis position Y | `titre-fondu-montee` | fondu 0,77 s `easeInOutCubic` ; montée 15,3 u, 0,92 s `easeOutExpo`, 0,30 s après | — (coupe vers le produit) | identique au centième dans 3 titres sur 4 |
| 2 | surtitre | avec le titre | rien à lui | `avec` | — | — | arrive avec son mot, 8 sur 11 |
| 3 | produit | 3,0 → 6,4 s | position X ; caméra parente | `produit-entree` + `camera-poussee` | 0,9 s `out-cubic`, flou de bougé 120° ; ×1,05 linéaire | la caméra pousse jusqu'au détail suivant | freine 8 sur 8 ; avancées linéaires 7 sur 11 |

La colonne **ce qui traverse** dit, à chaque changement de temps, ce qui survit et bouge pour passer au suivant (la caméra, le curseur, un composant qui devient l'écran suivant), ou « coupe ». Dans un film qui coupe, la plupart des lignes disent « coupe » : c'est la grammaire. Dans un plan-séquence, une ligne « coupe » est une diapositive, à justifier.

Pour une **scène démontée**, le plan est une ligne par cadrage : instant, ce qu'on regarde, l'arrivée de la caméra (`pose`, `suit`, `fouette`, `lineaire`, `coupe` : `scene-demontee.md` § 3), le zoom, le halo et le clic, la phrase dite, ce qui traverse.

Ajoute dessous trois lignes au plus : l'époque, la palette et les polices ; les conventions prises (9:16, dérive d'un objet, valeur de flou…) ; ce qui manque (textes à valider, chiffres, images). Attends son accord. Changer une ligne du plan coûte une minute ; refaire un script et ses images de contrôle coûte bien plus.

Une question sans script (« comment animer ce logo ? ») s'arrête ici : donne le plan, la recette, les valeurs et la courbe en clés After Effects (`references/courbes.md`), et propose d'écrire le script.

## Étape 3 — `motion.json` et le contrôle

Lis `references/motion-spec.md`, puis regarde `assets/exemple-motion.json` pour le niveau de détail (il est fictif : n'en reprends pas le contenu).

Écris `motion.json` dans le dossier de travail : `comp` (nom, format, cadence, durée, époque), `theme`, `elements` de l'arrière vers l'avant, `transitions`. Garde les valeurs par défaut des recettes ; ne mets dans `options` que ce que le plan validé change. Un texte proposé porte « À VALIDER » dans ta réponse, pas dans l'image. Un chiffre non fourni s'écrit `"[À FOURNIR]"`, avec `"source": "[À FOURNIR]"`.

```bash
python3 "$SKILL/scripts/check_motion.py" motion.json
```

- **Zéro erreur avant de générer.** Une option mesurée hors de sa fourchette, deux mouvements majeurs qui se chevauchent, une sortie animée, un balayage vers le bas, un voile qui va au noir, une glissade verticale, un chiffre sans source : corrige `motion.json` et relance. Un texte qui ne tient pas dans son temps se raccourcit ou reste plus longtemps ; on ne le réduit pas.
- Chaque avertissement se corrige, ou se garde en connaissance de cause et se dit à la livraison. Attendus et acceptables : un `[À FOURNIR]`, une image absente (repli), une convention choisie dans le plan.
- `"simultane": true` lève l'interdit de deux mouvements majeurs ensemble : seulement si le plan validé le demande, et dis-le.

## Étape 4 — Le script

```bash
node "$SKILL/scripts/build_motion.mjs" motion.json                  # écrit motion.jsx et vérifie l'ES3
node "$SKILL/scripts/build_motion.mjs" motion.json --prefixe TEST-  # pour un essai dans EffectCraft
```

Le script est en ExtendScript ES3 (ni `let`, ni `const`, ni fonction fléchée, ni gabarit, ni `JSON`) et n'emploie que l'API objet d'After Effects. Le générateur le vérifie ; un écart ES3 (code 2) est un défaut du moteur : signale-le. En tête du script : les recettes, les courbes et leur traduction en clés. Chaque recette pose un repère de calque qui dit sa recette, sa courbe et sa durée. Pour un partage sur un autre poste : `--relatif`, et les images à côté du script.

Un geste qu'aucune recette ne couvre (un tracé qui se dessine, une icône qui grandit sous un projecteur) : propose-le dans le plan comme convention, puis écris-le dans un second script court, avec la fonction de `references/courbes.md` § 7. Ne modifie pas le moteur.

## Étape 4 bis — La scène démontée (à la place des étapes 3 et 4)

Pour un plan-séquence d'interface ou une animation à démonter, à la place des étapes 3 et 4 : lis `references/scene-demontee.md`, écris `scene.json`, puis

```bash
python3 "$SKILL/scripts/scene_ec.py" scene.json --prefixe TEST-          # écrit scene.jsx et l'exécute dans EffectCraft
python3 "$SKILL/scripts/scene_ec.py" scene.json --jsx-seul               # pour After Effects : le script seul
```

Le script refuse une fenêtre plus grande que la composition, des clés de caméra dans le désordre, un fichier absent. Une longue démonstration se fait en une scène par chapitre, montées ensuite (étape 6).

## Étape 5 — Exécution et images de contrôle

Lis `references/outils.md`.

**EffectCraft** (sur cette machine) :

```bash
python3 "$SKILL/scripts/ec.py" activer                     # l'app ne répond qu'au premier plan
python3 "$SKILL/scripts/ec.py" script motion.jsx
python3 "$SKILL/scripts/ec.py" frames "<comp.nom>" controle/ --pas 0.5 --max 640
ffmpeg -v error -y -pattern_type glob -i 'controle/t*.png' -vf "scale=480:-1,tile=6x7:padding=4" -frames:v 1 planche.jpg
python3 "$SKILL/scripts/ec.py" render "<comp.nom>" rendus/motion.mp4     # si un rendu est demandé
```

Lance EffectCraft avec `open -a EffectCraft --args --control 9877` s'il n'écoute pas (code 3). N'enregistre, n'ouvre ni ne ferme jamais son projet : `ec.py` le refuse sans `--autoriser`, et seul l'utilisateur peut le demander. Un essai se fait dans une composition `TEST-`.

**After Effects** : l'utilisateur lance le script (**Fichier > Scripts > Exécuter le fichier de script…**). Donne-lui les étapes de `outils.md` § 2. Pour voir le résultat, demande-lui un MP4 et tires-en une planche (`outils.md` § 5). After Effects n'a pas servi aux essais de la skill : dis-le, et demande le message et la ligne de toute erreur. Si EffectCraft est installé, propose une passe d'essai dans une composition `TEST-` pour les images de contrôle, avec son accord.

**Relis la composition et le rendu en chiffres** (`scene-demontee.md` § 6), pour une scène démontée comme pour un film :

```bash
python3 "$SKILL/scripts/sonde_ec.py" "<comp.nom>" --cadre "Curseur,Halo" --carte carte.md   # carte, frontières, vitesse, cadre
python3 "$SKILL/scripts/mesure_rendu.py" rendus/motion.mp4 [--ref reference.mp4]             # énergie, repos, coupes, son
```

Chaque écart se corrige dans le `.json` ou se garde en le disant : un calque surveillé hors du cadre, une course de plus de 80 px par image sans flou de bougé (`camera.flou_de_bouge`, ou le flou de bougé de la recette), une note de transport sous 0,5 dans un plan-séquence, aucun repos.

**Regarde les images toi-même** avant de les montrer (outil de lecture d'image). Vérifie :
- chaque texte entier, lisible, sans boîte derrière ; le fond vide un instant après chaque coupe ;
- un seul mouvement majeur à la fois ; le libellé après son chiffre ; la caméra qui ne roule pas ;
- aucun dépassement, aucun rebond, rien qui flotte en boucle, aucun chiffre qui compte ;
- les replis et les `[À FOURNIR]` visibles ; rien qui rappelle une marque (ni appareil, ni police, ni logo, ni signature).

Pour juger une courbe, extrais le mouvement à pleine cadence et regarde les images à la suite (`outils.md` § 5). Un défaut : corrige `motion.json`, puis refais les étapes 3 à 5.

## Étape 6 — Montrer la mécanique, puis continuer

L'utilisateur doit pouvoir **comprendre comment la scène est faite** et la reprendre lui-même. Montre-lui, dans cet ordre :

1. la **capture de l'outil**, composition ouverte (`ec.py capture capture.png "<comp.nom>"`) ;
2. la **carte** de `sonde_ec.py` : chaque calque, son rôle, son parent, ce qui est animé ; puis explique la mécanique en quelques lignes (pour une scène démontée : l'ancrage et l'échelle de la fenêtre font la caméra ; halos et curseur sont ses enfants ; sous-titres et intertitre restent fixes ; chaque voix est à son instant) ;
3. une **comparaison** : une image du rendu à côté d'une image de la référence (ou de l'intention) au même instant, et les écarts qui restent.

Puis **la boucle continue** (`scene-demontee.md` § 7) : il retouche à la main dans l'outil ou demande une modification ; tu relances `sonde_ec.py`, tu dis ce qui a changé, tu reportes la retouche dans le `.json`, tu régénères, tu remesures. Rien de ce qu'il a fait à la main ne doit se perdre au passage suivant.

**Garder le projet**, sur sa demande seulement : `python3 "$SKILL/scripts/ec.py" --autoriser garder <dossier>/<nom>.ecproj` (un fichier neuf, jamais par-dessus). Les scènes rendues se montent ensuite en film avec `sebmake-videoedit-like-applepls` (montage composé : image, voix, musique atténuée sous la voix, sous-titres, sons).

## Étape 7 — Livraison

Livre en un message court :

1. **les fichiers** : le script `.jsx` (chemin), le rendu MP4 s'il y en a un (chemin, durée, format), le `.json` source, la planche de contrôle, la carte et la capture de l'outil, le projet gardé s'il l'a demandé ;
2. **comment l'exécuter** : la commande `ec.py`, ou le menu After Effects, en une ligne ;
3. **à valider** : les textes proposés, un par un ;
4. **à fournir** : les `[À FOURNIR]` (chiffres avec leur source), les images remplacées par un repli, avec ce qu'elles doivent montrer et leur format (PNG détouré, capture native ×2, une image par pièce) ;
5. en une ligne : les conventions prises et les avertissements gardés ; « non testé dans After Effects » si c'est l'outil ;
6. pour la suite : on modifie `motion.json` et on régénère ; une retouche faite à la main dans le `.jsx` ou dans la composition est perdue au prochain passage du script.

## Rappels

- **Les principes sont mesurés.** N'avance une durée, une courbe ou une amplitude que si elle est dans les références, avec son compte. Ce qui n'est pas mesuré se dit « convention ».
- **Aucun chiffre inventé**, ni date, ni avis, ni citation, ni logo de client. Ce qui manque reste visible : `[À FOURNIR]`.
- **La grammaire, jamais la marque.** Aucune image, police, logo ou signature d'Apple, aucun appareil reconnaissable (un panneau flottant à coins arrondis remplace un cadre d'appareil), aucune citation de keynote, même traduite.
- **Ce qui n'existe pas dans le corpus ne s'anime pas** : chiffre qui compte, rebond, machine à écrire, mot à mot, rotation de texte, tour complet, flottement sinusoïdal, sortie animée, glissade verticale d'écran, boîte derrière un texte (comptes dans `principes.md` § 13).
- **ES3 pour After Effects** : `var` et `function` seulement. Un script écrit à la main suit la même règle.
- **Le projet de l'utilisateur est à lui** : le script ajoute ou remplace une composition (avec les solides qu'elle seule utilisait), rien d'autre ; aucune ouverture ni fermeture. Un enregistrement seulement à sa demande, dans un fichier neuf (`ec.py garder`).
- **Le son.** Le corpus est muet : caler un mouvement sur la musique est une convention. La scène démontée pose les voix, les sons et la musique de l'utilisateur (dont il a les droits) à leur instant. Une voix de synthèse seulement avec son accord sur le moteur, le texte et la voix (`voix.py`) ; aucune musique cherchée ni fabriquée.
- **Une retouche à la main ne se perd jamais** : relue par la sonde, reportée dans le `.json`, dite à l'utilisateur.

## Fichiers de référence : quand les lire

| Fichier | Quand |
|---|---|
| `references/principes.md` | Étape 2, une fois : les 12 principes, leurs comptes et leur raison ; § 13 avant de refuser un geste (« ce qu'on n'anime jamais ») ; § 14 pour les conventions. |
| `references/elements.md` | Étape 2 : la fiche de chaque type d'élément demandé (§ 2 à § 16), le choix rapide (§ 1), l'ordre d'une séquence (§ 17). Aussi pour répondre à « comment animer tel élément ». |
| `references/film-fonctionnalites.md` | Étape 1 (§ 7 : le recueil propre) et étape 2, pour un film qui présente un produit logiciel par ses fonctionnalités : trois matières (verbe, composant, forme), ordre du film, composant sorti de l'écran, fond par chapitre ; deux films relevés, valeurs en convention. |
| `references/scene-demontee.md` | Étape 1 (genre plan-séquence ou animation à démonter : brief au § 2) ; étape 2 (trois concepts et ce qui traverse, § 5 ; caméra, § 3 ; lisibilité, § 4) ; étape 4 bis (format) ; étapes 5 et 6 (repères § 6, boucle continue § 7, pièges § 8). |
| `references/courbes.md` | Étape 2, pour donner une courbe en clés After Effects ; étape 4, pour un geste hors recette (§ 7) ; en cas de doute sur un nom de courbe (§ 3.3). |
| `references/motion-spec.md` | Étape 3, avant d'écrire `motion.json` ; pour comprendre une erreur du contrôle (§ 7) ou la forme du script (§ 9). |
| `references/outils.md` | Étape 5 : exécuter dans After Effects (§ 2) ou EffectCraft (§ 3) ; un symptôme et sa parade (§ 4) ; planche et vérification d'un rendu (§ 5). |
| `assets/exemple-motion.json`, `assets/exemple-motion.jsx` | Étape 3 : une animation complète de 20 s (fictive) et le script qu'elle donne ; images neutres dans `assets/exemple/`. |
| `scripts/check_motion.py` | Étape 3 : contrôle (Python 3.9, sans dépendance). |
| `scripts/build_motion.mjs`, `scripts/motion_lib.mjs` | Étape 4 : génération du script ; `--liste` donne les recettes et leurs comptes. |
| `scripts/ec.py` | Étape 5 : client du canal de contrôle d'EffectCraft (Python 3.9, sans dépendance) ; `capture` (étape 6), `garder` (sur demande). |
| `scripts/scene_ec.py` | Étape 4 bis : `scene.json` → scène démontée, exécutée dans EffectCraft. |
| `scripts/sonde_ec.py` | Étapes 5 et 6 : lit la composition ouverte → carte des calques, frontières et note de transport, vitesses, cadre. |
| `scripts/voix.py` | Étape 1 : voix off de synthèse (edge-tts conseillé, `say` de macOS en repli) : état, audition, génération avec l'instant des mots. |
| `scripts/mesure_rendu.py` | Étape 5 : lit un MP4 → carte d'énergie, repos, coupes, rafales, plans, son ; `--ref` pour une référence. |
