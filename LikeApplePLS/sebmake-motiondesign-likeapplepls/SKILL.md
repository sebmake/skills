---
name: sebmake-motiondesign-likeapplepls
description: "Dit quoi animer et comment, élément par élément (titre, phrase, liste, chiffre, logo, produit, capture d'écran, icône, forme, fond, caméra, transitions), selon les principes de mouvement mesurés image par image dans 8 keynotes Apple, puis écrit et exécute le script After Effects ou EffectCraft qui construit l'animation. Use it whenever someone wants Apple-style motion design or keynote-style animation, asks to animate a title, a logo, a product shot or a UI screenshot 'like Apple', wants an After Effects, EffectCraft or ExtendScript script that animates elements, or asks how to animate a given element, which easing curve, duration or stagger to use, even if they never say Apple. Not for slide decks (sebmake-keynote-likeapple-pls), not for a complete product film rendered to MP4 with HyperFrames (sebmake-videopresentation-likeapplepls), not for animating the interface of an app itself."
---

# Motion design à la manière des keynotes

Cette skill fait deux choses, dans cet ordre :

1. elle dit **quoi animer et comment**, pour chaque élément d'une vidéo de motion design : quelle propriété, quelle recette, quelle durée, quelle courbe, quelle amplitude, à quel moment, et ce qu'il ne faut pas faire ;
2. elle **écrit le script** qui construit l'animation dans After Effects ou dans EffectCraft, et l'exécute quand c'est possible.

Les valeurs viennent de quatre analyses image par image de 8 keynotes (2019 à 2026) : 145 textes, 122 mouvements d'objets, 189 mouvements d'écrans, 182 transitions. Chaque règle porte son compte (« N sur M ») ; ce qui n'est pas mesuré est marqué **convention**. La skill reprend la **grammaire** du mouvement, jamais la **marque** : couleurs, polices, images, logos et textes sont ceux de l'utilisateur.

Le champ : la vidéo de motion design (textes, produits, captures, logos qui bougent). Pas les slides, pas l'animation d'une application (ses transitions, ses micro-interactions) : une capture d'écran est animée comme une image dans le film.

Tout part d'un fichier, `motion.json`. Le moteur en tire `motion.jsx`, un script ExtendScript (ES3) qui tourne dans les deux outils. Corrige toujours `motion.json`, jamais le `.jsx` : il est réécrit à chaque génération.

```bash
SKILL="<dossier de ce SKILL.md>"   # souvent ~/.claude/skills/sebmake-motiondesign-likeapplepls
```

Prérequis : Node, Python 3.9 ou plus, ffmpeg et ffprobe. After Effects, ou EffectCraft lancé avec son canal de contrôle. S'il en manque un, dis-le : la skill peut aller jusqu'au script contrôlé sans outil installé. N'installe rien sans accord.

## Étape 1 — Recueil

Relis la demande et les pièces jointes. Ne redemande rien de ce qui est déjà dit.

Pose les questions manquantes avec l'outil AskUserQuestion s'il existe, sinon en clair, en un seul message. **4 questions au plus par appel**, 4 choix au plus par question (plus « Autre »).

| Question | Choix | Pourquoi |
|---|---|---|
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

Dis ce que deviendra ce qui reste vide : un texte manquant sera proposé et marqué « À VALIDER » ; un chiffre manquant restera `[À FOURNIR]` ; une image manquante sera remplacée par un repli neutre (un cadre et ses diagonales), au bon format.

**Lire l'habillage.** Avec un lien, lis-le avec les outils de la session (Figma : `get_variable_defs` et `get_screenshot`, après la skill Figma que ces outils demandent ; Notion ; page web ; PDF). Remplis les rôles du thème : `fond`, `texte`, `secondaire`, `accent`, `voile`, `lumiere`. Lien illisible : dis-le et demande les HEX. Couleurs décrites sans HEX : propose des HEX et fais-les valider. Ne choisis jamais une palette qu'il n'a pas vue. Les polices s'écrivent en noms PostScript (`Inter-SemiBold`) ; EffectCraft fournit Inter. Une police propre à un fabricant (SF, New York…) est refusée par le contrôle : propose une linéale libre et dis pourquoi.

**Préparer les fichiers.** Crée un dossier de travail (dans le dossier courant, sauf s'il en nomme un autre) avec `images/`, et copies-y ses fichiers. Taille : `ffprobe -v error -show_entries stream=width,height -of csv=p=0 <fichier>`. Produit : PNG détouré, assez grand pour la poussée (×1,27 en moyenne). Captures : définition native ou ×2, sans données personnelles (floute-les ou demande une capture de démonstration). Logo : le sien seulement. Pour un éclaté : une image par pièce, de même cadre.

## Étape 2 — Le plan d'animation, avant tout script

Lis `references/principes.md` (une fois par conversation), puis, dans `references/elements.md`, la fiche de chaque type d'élément demandé, et § 17 pour l'ordre d'une séquence.

Pour chaque élément, choisis :
- **quoi animer** : la propriété (opacité, position, échelle, rotation Y, lumière, caméra parente) ; souvent rien (« coupe ») ;
- **la recette** du moteur, de l'époque choisie (`2024-2026` par défaut, `2019-2020` pour un rendu plus calme sur les écrans et plus joueur sur les chiffres) ;
- **le moment** : coupe sur le fond vide, entrée, ce qui suit (`avec`, libellé, `puis`), maintien, sortie par coupe ;
- **ce qu'on écarte**, et pourquoi.

Montre le plan **avant** d'écrire `motion.json`, en un tableau, une ligne par élément ou par geste :

| # | Élément | De → à | Quoi animer | Recette | Durée, courbe, amplitude | Pourquoi (compte) |
|---|---|---|---|---|---|---|
| 1 | titre | 0,1 → 3,0 s | opacité, puis position Y | `titre-fondu-montee` | fondu 0,77 s `easeInOutCubic` ; montée 15,3 u, 0,92 s `easeOutExpo`, 0,30 s après | identique au centième dans 3 titres sur 4 |
| 2 | surtitre | avec le titre | rien à lui | `avec` | — | arrive avec son mot, 8 sur 11 |
| 3 | produit | 3,0 → 6,4 s | position X ; caméra parente | `produit-entree` + `camera-poussee` | 0,9 s `out-cubic`, flou de bougé 120° ; ×1,05 linéaire | freine 8 sur 8 ; avancées linéaires 7 sur 11 |

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

**Regarde les images toi-même** avant de les montrer (outil de lecture d'image). Vérifie :
- chaque texte entier, lisible, sans boîte derrière ; le fond vide un instant après chaque coupe ;
- un seul mouvement majeur à la fois ; le libellé après son chiffre ; la caméra qui ne roule pas ;
- aucun dépassement, aucun rebond, rien qui flotte en boucle, aucun chiffre qui compte ;
- les replis et les `[À FOURNIR]` visibles ; rien qui rappelle une marque (ni appareil, ni police, ni logo, ni signature).

Pour juger une courbe, extrais le mouvement à pleine cadence et regarde les images à la suite (`outils.md` § 5). Un défaut : corrige `motion.json`, puis refais les étapes 3 à 5.

## Étape 6 — Livraison

Livre en un message court :

1. **les fichiers** : `motion.jsx` (chemin), le rendu MP4 s'il y en a un (chemin, durée, format), `motion.json`, la planche de contrôle ;
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
- **Le projet de l'utilisateur est à lui** : le script ajoute ou remplace une composition (avec les solides qu'elle seule utilisait), rien d'autre ; aucune commande d'enregistrement, d'ouverture ou de fermeture.
- **Pas de son.** Le corpus est muet : caler un mouvement sur la musique est une convention.

## Fichiers de référence : quand les lire

| Fichier | Quand |
|---|---|
| `references/principes.md` | Étape 2, une fois : les 12 principes, leurs comptes et leur raison ; § 13 avant de refuser un geste (« ce qu'on n'anime jamais ») ; § 14 pour les conventions. |
| `references/elements.md` | Étape 2 : la fiche de chaque type d'élément demandé (§ 2 à § 16), le choix rapide (§ 1), l'ordre d'une séquence (§ 17). Aussi pour répondre à « comment animer tel élément ». |
| `references/courbes.md` | Étape 2, pour donner une courbe en clés After Effects ; étape 4, pour un geste hors recette (§ 7) ; en cas de doute sur un nom de courbe (§ 3.3). |
| `references/motion-spec.md` | Étape 3, avant d'écrire `motion.json` ; pour comprendre une erreur du contrôle (§ 7) ou la forme du script (§ 9). |
| `references/outils.md` | Étape 5 : exécuter dans After Effects (§ 2) ou EffectCraft (§ 3) ; un symptôme et sa parade (§ 4) ; planche et vérification d'un rendu (§ 5). |
| `assets/exemple-motion.json`, `assets/exemple-motion.jsx` | Étape 3 : une animation complète de 20 s (fictive) et le script qu'elle donne ; images neutres dans `assets/exemple/`. |
| `scripts/check_motion.py` | Étape 3 : contrôle (Python 3.9, sans dépendance). |
| `scripts/build_motion.mjs`, `scripts/motion_lib.mjs` | Étape 4 : génération du script ; `--liste` donne les recettes et leurs comptes. |
| `scripts/ec.py` | Étape 5 : client du canal de contrôle d'EffectCraft (Python 3.9, sans dépendance). |
