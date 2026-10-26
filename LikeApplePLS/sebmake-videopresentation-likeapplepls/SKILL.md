---
name: sebmake-videopresentation-likeapplepls
description: "Makes a voiceless 1-2 minute product film on the grammar of Apple keynote reveal films (hook, build-up, late reveal, name at the end), then cuts it to 15-60 s for social in 16:9, 9:16 and 1:1, rendered as MP4 in the user's colors, over their own music or none. Use it for any product film, launch video, teaser or reveal, anything Apple-style or keynote-style, and for reels, shorts, stories or vertical cuts of a launch, even without the word Apple. Not for slide decks (sebmake-keynote-likeapple-pls), voice-over or presenter videos, or interview edits."
---

# Film produit à la manière des keynotes

Cette skill produit deux choses :

1. un **film produit** de 60 à 120 s, en 16:9, construit comme les films de révélation des keynotes : une accroche, une montée, la révélation tardive de l'objet entier, puis le nom en chute ;
2. ses **déclinaisons réseaux** de 15 à 60 s, en 16:9 et en vertical 9:16 (le carré 1:1 en option), **recomposées** pour chaque format, jamais recadrées.

**Aucune voix**, ni voix off ni synthèse vocale : le sens passe par le texte à l'écran et la musique. La musique est un fichier fourni par l'utilisateur, dont il a les droits, ou il n'y en a pas. La skill reprend la **grammaire** observée sur 8 keynotes (2019 à 2026), jamais la **marque** : couleurs, polices, visuels, chiffres et musique sont ceux de l'utilisateur.

Tout part d'un seul fichier, `film.json`. Le moteur en tire des projets HyperFrames (HTML + GSAP), une planche de validation et les MP4. Corrige toujours `film.json`, jamais le projet produit : `build_film.js` le réécrit à chaque passage. Les skills HyperFrames ne sont pas nécessaires ; `npx hyperframes` suffit.

```bash
SKILL="<dossier de ce SKILL.md>"   # souvent ~/.claude/skills/sebmake-videopresentation-likeapplepls
```

Prérequis : Node 22 ou plus avec `npx hyperframes` (0.8), ffmpeg et ffprobe, Python 3.9 ou plus. S'il en manque un, dis-le : la skill peut aller jusqu'au `film.json` contrôlé, pas jusqu'au rendu. N'installe rien sans son accord.

## Étape 1 — Recueil

Relis d'abord la demande et les pièces jointes. Ne redemande rien de ce qui est déjà dit.

Pose les questions manquantes avec l'outil AskUserQuestion s'il existe, sinon en clair, groupées dans un seul message. **4 questions au plus par appel.** L'outil n'accepte que 4 choix par question, plus « Autre » : si la liste est plus longue, propose les 4 plus probables et nomme les autres dans le texte de la question.

**Appel 1 : le produit et la matière.**

| Question | Choix | Pourquoi |
|---|---|---|
| Que présente le film ? | un objet physique ; un logiciel ou une application ; un service ; autre chose (marque, événement) | La famille du film en dépend (`grammaire-film.md` § 4). |
| Quels visuels avez-vous ? (choix multiples) | photos détourées du produit (PNG transparent) ; photos d'ambiance ou d'usage ; captures ou enregistrements d'écran ; logo | Les recettes de plans en dépendent. Sans aucun visuel, seul un film-texte est possible : dis-le. |
| Habillage | un lien vers mon design system ; mes couleurs en HEX et mes polices | La skill ne connaît pas son identité. |
| Musique | un fichier dont j'ai les droits ; aucune musique | Il n'y a pas de troisième voie. |

**Appel 2 : la diffusion.**

| Question | Choix | Pourquoi |
|---|---|---|
| Public | décideurs B2B ; grand public ; investisseurs ou partenaires ; équipe interne | Il règle le ton des cartons et le choix des preuves. |
| Où sera-t-il vu ? (choix multiples) | site ou YouTube (16:9) ; Reels, Shorts, TikTok, stories (9:16) ; fil carré LinkedIn ou Instagram (1:1) ; écran de salon ou de scène (16:9) | Il décide des formats. |
| Durée du film produit | 60 s (conseillé) ; 75 s ; 90 s ; 120 s | Aucun film produit sans voix observé ne dépasse 68,5 s. Au-delà, le film se fait en chapitres et demande plus de visuels : dis-le. |
| Déclinaisons (choix multiples) | 15 s ; 30 s ; 45 s ; 60 s | Les gabarits de `declinaisons.md` § 3. |

**Puis le brief, en clair.** Donne ce gabarit à remplir, avec seulement les lignes encore sans réponse. Dis ce que deviendra ce qui reste vide : les formulations (thèse, idées, chute) seront proposées et signalées « à valider » ; les chiffres, les dates, la ligne d'action, les logos et les citations resteront `[À FOURNIR]`.

```
Produit : [le nom exact, tel qu'il s'écrit à l'écran]
Message : [la phrase que le spectateur doit retenir]
Trois preuves : [ce que le produit fait de mieux] · [ce qu'on peut montrer pour le prouver]
Chiffres : [chiffre] · [base de comparaison] · [source]      (aucun si vous n'en avez pas)
Ligne d'action : [date, adresse, « bientôt disponible »]      (facultatif)
Visuels : [chemins ou pièces jointes]
Musique : [chemin du fichier], et vous confirmez en avoir les droits
```

**Lire l'habillage.** Avec un lien, lis-le avec les outils de la session : Figma (`get_variable_defs`, `get_screenshot`, après la skill Figma que ces outils demandent), Notion, page web, PDF. Remplis les rôles de `theme.couleurs` : `fond_sombre` (un charbon plutôt qu'un noir pur), `fond_clair` (jamais `#FFFFFF`), `texte_sur_sombre`, `texte_sur_clair`, `accent` (une seule couleur forte) et `accent_2` (facultatif). Lien illisible : dis-le et demande les HEX. Couleurs décrites sans HEX : propose des HEX et fais-les valider. Ne choisis jamais une palette qu'il n'a pas vue. Une police propre à une marque d'appareils (SF, New York…) est refusée par le contrôle : propose une linéale libre (liste dans `film-spec.md` § 3) et dis pourquoi. Sa propre police passe par `fichier`.

**Préparer les visuels.** Crée un dossier de travail (dans le dossier courant, sauf s'il en nomme un autre) avec `visuels/` et `musique/`, et copies-y ses fichiers.

- Taille : `ffprobe -v error -show_entries stream=width,height -of csv=p=0 <fichier>`. Objet détouré : 2 400 px de large ou plus ; 3 à 5 vues proches pour une rotation ; pièces de même cadre pour un éclaté. Macro : 2 900 px pour un plein cadre. Capture : définition native ou ×2.
- Photo d'objet non détourée : demande un PNG transparent. À défaut, propose `npx hyperframes remove-background photo.jpg -o objet.png` ; préviens que le modèle est fait pour des personnes et se télécharge au premier usage, et montre le résultat.
- Données sensibles dans une capture : floute la zone (`ffmpeg -i capture.png -filter_complex "[0]crop=w:h:x:y,gblur=sigma=12[f];[0][f]overlay=x:y" capture-floue.png`) ou demande une capture de démonstration.
- Enregistrement d'écran : tires-en des images fixes aux moments clés (`ffmpeg -ss <t> -i video.mp4 -frames:v 1 capture.png`).
- Un visuel manque : n'attends pas. Le moteur pose un repli neutre (formes grises, sans texte ni marque) et le visuel entre dans la liste à fournir.

**La musique.** Copie le fichier dans `musique/` (`.mp3`, `.m4a`, `.wav`, `.aac`). `droits_confirmes: true` seulement parce qu'il l'a dit. Sinon `musique: null`.

## Étape 2 — La structure, à l'échelle de la durée

Lis `references/grammaire-film.md` § 2 à § 4, puis `references/declinaisons.md` § 1 à § 3.

- Choisis la **famille** d'après les visuels, pas d'après l'envie (`grammaire-film.md` § 4).
- Compte les **visuels distincts** : environ 7 pour 60 s, 10 pour 90 s, 14 pour 120 s (un visuel nourrit 2 à 3 plans). En dessous, le film se répète : propose une durée plus courte ou demande d'autres visuels. Le contrôle le signale.
- Pose les **cinq temps** à l'échelle de la durée avec la table du § 3 : accroche, montée, révélation après 60 % de la durée, nom après 76 %, fin. Au-delà de 60 s, une montée en 2 ou 3 chapitres d'une seule idée chacun (§ 3.1).
- Place les **textes** : une thèse en fin d'accroche, un carton par chapitre, un nom par fonction pour un logiciel, une chute, le nom (§ 3.2).
- Choisis les **déclinaisons** et leur gabarit (`declinaisons.md` § 3).

Montre la structure **avant** de produire quoi que ce soit, en deux tableaux courts. Le film, une ligne par temps ou par chapitre :

| # | Temps | De → à | Ce qu'on voit | Texte | Visuel |
|---|---|---|---|---|---|
| 1 | Accroche | 0:00 → 0:09 | une lueur sort du noir ; le contour de l'objet | thèse, 5 mots | photo détourée |
| 2 | Chapitre 1 : [idée] | 0:09 → 0:32 | macros, rotation lente | 1 carton d'idée | macros, 3 vues |
| 3 | Révélation | 0:44 → 0:52 | l'objet entier, halo, recul lent | — | photo détourée |
| 4 | Chute, nom, fin | 0:52 → 1:00 | la chute, le nom seul, noir | chute, nom | — |

Les déclinaisons :

| Sortie | Format | Durée | Ouverture | Ce qu'elle garde |
|---|---|---|---|---|
| vertical-30 | 9:16 | 30 s | 3 mots sur l'image la plus forte | révélation et nom, 2 preuves, chute, fin |

Ajoute dessous trois lignes au plus : la palette et les polices retenues ; ce qui manque encore (visuels, chiffres) ; les conventions prises (par exemple « 90 s sans voix : jamais observé, fait en 2 chapitres »). Attends son accord. Changer une ligne coûte une minute ; refaire un rendu coûte bien plus.

## Étape 3 — Le storyboard : `film.json` et la planche

Lis `references/recettes.md`, puis `references/film-spec.md`. Regarde `assets/exemple-film.json` pour le niveau de détail : il est fictif, n'en reprends pas le contenu.

Écris `film.json` dans le dossier de travail : `meta` (`formats`, `duree_cible_s`), `theme`, `musique`, `plans` dans l'ordre du film, `declinaisons`. Pour les plans :

- **Un plan = une recette** parmi les 12 de `recettes.md`. Choisis-la d'après le visuel disponible (§ 1.1) et le temps du film (§ 1.2).
- **La structure validée** : la `revelation` après 60 % de la durée, la `fin` en dernier, aucun nom avant 76 %. Rythme en U : plans de 2,5 à 4 s dans l'accroche, de 1 à 2 s dans la montée, un plan long à la révélation.
- **Les textes** (`grammaire-film.md` § 6) : 6 mots au plus d'un bloc, 12 au plus construits en groupes ; une idée par carton ; le texte dit l'idée, l'image la prouve ; casse de phrase, sans point d'exclamation ; jamais deux cartons de suite sans image entre eux (sauf film-texte). Les mêmes mots dans tous les formats.
- **Brief mince : propose, ne laisse pas de trou.** Rédige la thèse, les idées et la chute dans les mots de l'utilisateur, à partir de son brief. Le texte proposé va dans `texte` ; `notes` commence alors par « À VALIDER : ». Une proposition ne contient aucun nombre, même écrit en lettres.
- **Les chiffres** : `texte.chiffre` et `source` seulement s'ils sont fournis ; sinon `"chiffre": null`, et l'écran affiche `[À FOURNIR]` estompé.
- **`notes`** : l'intention du plan, en une phrase. Elle s'affiche sur la planche, jamais dans le film.
- **Pour les déclinaisons** : un `role` sur chaque plan, un `groupe` commun pour un carton et le plan qui le prouve, `priorite: 1` sur les preuves les plus visibles (`declinaisons.md` § 3.5). Commence par `"regle": "auto"`.

Contrôle le fichier (étape 4), puis fais la planche :

```bash
python3 "$SKILL/scripts/check_film.py" film.json
node "$SKILL/scripts/build_film.js" film.json --planche
```

La planche (1 à 2 minutes de calcul) écrit `sortie-<titre>/planches/<sortie>.png`, une par sortie : une image par plan, avec sa recette, son rôle, son temps, son texte, son intention et les remarques du contrôle en rouge. Regarde chaque planche toi-même avant de la montrer (outil de lecture d'image). Donne ensuite à l'utilisateur les chemins, un résumé en trois lignes et la liste des visuels manquants. Attends sa validation avant le rendu.

## Étape 4 — Le contrôle

```bash
python3 "$SKILL/scripts/check_film.py" film.json
```

Il porte les règles de la skill : aucune voix, musique locale aux droits confirmés, polices de marque refusées, durées et lecture des cartons, mots par carton, zones sûres et longueur des lignes par format, chiffres sans source, place du nom et de la révélation, cadence des textes, contraste des couleurs du thème. `build_film.js` le relance sur les sorties résolues (déclinaisons `auto`, durées ajustées) : lis aussi ce qu'il affiche.

- **Zéro erreur avant le rendu.** Corrige `film.json` et relance. Un texte qui ne tient pas se raccourcit : on retire des mots, on ne réduit pas la taille.
- Chaque avertissement se corrige, ou se garde en connaissance de cause et se dit à la livraison. Attendus et acceptables : un visuel absent (repli), un `[À FOURNIR]`, une part de texte au-dessus de 45 % pour un logiciel, une cadence haute pour un film-texte.
- `--force` (rendu malgré les erreurs) seulement si l'utilisateur le demande.

## Étape 5 — Le rendu

Le film 16:9 d'abord, puis les déclinaisons. `--check` ajoute `npx hyperframes check` (contraste réel, mise en page) avant chaque rendu.

```bash
node "$SKILL/scripts/build_film.js" film.json --rendu --seulement film --check
node "$SKILL/scripts/build_film.js" film.json --rendu --seulement vertical-30,carre-15 --check
```

Après `--seulement`, mets les `id` de tes déclinaisons, séparés par des virgules.

Les MP4 vont dans `sortie-<titre>/rendus/` ; les projets HyperFrames dans `sortie-<titre>/projets/` (ouvrables avec `npx hyperframes preview`). Le calcul prend environ une seconde par seconde de vidéo ; lance un long rendu en arrière-plan. `--qualite draft` donne un brouillon rapide ; `standard` est le défaut ; `high` pour la livraison finale s'il la demande.

## Étape 6 — Le contrôle visuel

Regarde le résultat avant de le donner : le contrôle ne voit pas tout. Pour chaque MP4 :

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type -of csv=p=0 <video>.mp4
ffmpeg -v error -y -i <video>.mp4 -vf "fps=30/<durée en s>,scale=480:-1,tile=6x5" -frames:v 1 verif-<sortie>.jpg
ffmpeg -v error -y -ss 0.2 -i <video>.mp4 -frames:v 1 verif-<sortie>-debut.png
```

La planche-contact montre 30 images réparties sur toute la vidéo. Lis les images, puis vérifie :

- la durée attendue ; une piste son seulement s'il y a une musique ;
- chaque texte entier, lisible, centré, dans la zone sûre, sans boîte derrière, un seul à la fois ;
- aucune bande noire au bord d'un plan, aucune image figée plus de 2 s (hors carton et nom) ;
- la révélation tenue, le nom seul en dernier ;
- en déclinaison : image 0 pleine, texte lisible à 0,2 s, aucun noir final (liste de contrôle de `declinaisons.md` § 9) ;
- les `[À FOURNIR]` visibles et estompés ; les replis gris, acceptables dans un brouillon seulement ;
- rien qui rappelle Apple : ni appareil, ni police, ni signature.

Un défaut : corrige `film.json`, puis refais les étapes 4 et 5.

## Étape 7 — La livraison

Livre en un message court :

1. **les fichiers** : chaque MP4 (chemin, format, durée), `film.json` et les planches ;
2. **à valider** : les textes proposés (plans dont `notes` commence par « À VALIDER »), un par un ;
3. **à fournir** : les `[À FOURNIR]` restants (chiffres avec leur source, ligne d'action, logo), plan par plan, ou « aucun » ;
4. **les visuels à fournir pour une meilleure version** : chaque repli du contrôle, avec ce que le visuel doit montrer et son format (PNG détouré de 2 400 px, 3 à 5 vues, capture native ×2…) ;
5. en une ligne : les conventions prises (durée sans voix au-delà de 68,5 s, formats 9:16 et 1:1 jamais observés…) et les avertissements gardés ;
6. pour la suite : on modifie `film.json` et on relance le rendu ; une retouche faite à la main dans un projet est effacée au prochain passage du moteur.

## Rappels

- **Aucune voix.** Ni voix off, ni synthèse vocale, ni sous-titres de narration. Ignore les étapes de voix des skills HyperFrames (`product-launch-video`, `media-use`, `npx hyperframes tts`).
- **Aucune musique sans droits.** Le fichier de l'utilisateur, ou `musique: null`. Jamais une musique cherchée, téléchargée, générée ou prise dans une bibliothèque, même « libre de droits », même si une skill HyperFrames le propose par défaut.
- **Aucun chiffre inventé**, ni date, ni avis, ni citation, ni logo de client. Ce qui manque reste visible : `[À FOURNIR]`. Un chiffre faux suffit à ruiner la confiance.
- **La grammaire, jamais la marque.** Aucune image, aucun son, aucun appareil reconnaissable (un panneau flottant sans contour d'appareil le remplace), aucune police ni aucun logo d'Apple, aucune signature (« tourné avec… », logo seul sur noir, heure figée des écrans de démo).
- **Aucune citation de keynote**, même traduite. Les textes s'écrivent dans les mots de l'utilisateur.
- **Recomposer, jamais recadrer** : chaque format est sa propre composition ; les mots ne changent pas d'un format à l'autre.

## Fichiers de référence : quand les lire

| Fichier | Quand |
|---|---|
| `references/grammaire-film.md` | Étape 2 (§ 2 à § 4 : les temps, la structure, les familles). Étape 3 (§ 5 à § 8 : rythme, texte, nom, image). En cas de doute sur un compte ou une convention (§ 11). |
| `references/declinaisons.md` | Étape 2 (§ 1 à § 3 : principe et gabarits). Étape 3 (§ 3.5 : la déclinaison dans `film.json` ; § 4 et § 5 : zones sûres et recomposition). Étape 6 (§ 9 : liste de contrôle). |
| `references/recettes.md` | Étape 3, avant d'écrire les plans : choisir la recette, ses visuels, ses réglages ; § 4 quand un visuel manque ; § 5 pour deux enchaînements de 60 s déjà contrôlés. |
| `references/film-spec.md` | Étape 3, avant d'écrire `film.json` ; et pour comprendre une erreur du contrôle ou du moteur. |
| `assets/exemple-film.json` | Étape 3 : un film complet (fictif) avec déclinaisons, pour le niveau de détail. Ses visuels neutres sont dans `assets/exemple-visuels/`. |
| `scripts/check_film.py` | Étapes 3 et 4 : contrôle (Python 3.9, sans dépendance). |
| `scripts/build_film.js` | Étape 3 (`--planche`) et étape 5 (`--rendu`) : Node, ffmpeg, `npx hyperframes`, sans dépendance npm. |
