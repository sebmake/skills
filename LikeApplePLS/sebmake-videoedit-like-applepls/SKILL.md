---
name: sebmake-videoedit-like-applepls
description: "Montage à la manière des films de keynote Apple : monte les rushes de l'utilisateur (et sa musique) en timeline, dans FilmCraft, ou en XML FCP7 (ou EDL) pour DaVinci Resolve et Premiere Pro ; ou critique un montage existant plan par plan contre les films de sa famille (rythme, coupes, noirs, révélation, texte), avec correctifs au timecode. Quatre familles : produit et révélation, ouverture et ambiance (sketch, fiction, clôture), documentaire et témoignage, bande-annonce et usage. Use it whenever someone wants to edit their own footage like an Apple keynote film, asks for editing help, a timeline, an EDL or XML to import, or an edit critique (pacing, cuts, transitions, where the reveal or title lands), works in DaVinci Resolve, Premiere Pro or FilmCraft, even without the word Apple. Not for a product film generated in motion design (sebmake-videopresentation-likeapplepls), animating titles or logos (sebmake-motiondesign-likeapplepls), or slides (sebmake-keynote-likeapple-pls)."
---

# Montage à la manière des films de keynote

Cette skill aide à monter. Elle fait deux choses :

1. **construire une timeline** à partir des rushes de l'utilisateur, et de sa musique s'il en a une, puis la poser dans FilmCraft (pilotée) ou la remettre en fichier pour Premiere Pro et DaVinci Resolve ;
2. **critiquer un montage** : le mesurer plan par plan contre les films de sa famille, et dire quoi corriger, au timecode près.

Les règles viennent de quatre analyses des films de 8 keynotes (2019 à 2026), découpés plan par plan : 16 films produit, 20 films d'ouverture et d'ambiance, 8 documentaires, 8 bandes-annonces et films d'usage. Chaque règle porte son compte (« N sur M ») ; ce qui n'est pas mesuré est marqué **convention**. La skill reprend la **grammaire**, jamais la **marque** : ni image, ni son, ni logo, ni police d'Apple, ni phrase des films. Les images, la musique, les textes et le logo sont ceux de l'utilisateur.

La chaîne :

```
rushes ─ analyse_rushes.py ─▶ rushes.json (complété à l'œil) ─ assemble.py ─▶ montage.json
   montage.json ─▶ filmcraft_build.py (FilmCraft) | export_xml.py (Premiere, Resolve) | export_edl.py
   montage.xml, vidéo ou timeline de l'utilisateur ─ critique_montage.py ─▶ critique.md
```

Corrige toujours `rushes.json` ou `montage.json`, jamais le XML ni l'EDL : ils sont réécrits à chaque export.

```bash
SKILL="<dossier de ce SKILL.md>"   # souvent ~/.claude/skills/sebmake-videoedit-like-applepls
PY=~/.venv-videoedit/bin/python    # Python avec numpy et Pillow
```

**Prérequis.** ffmpeg et ffprobe. Python 3.9 ou plus. `analyse_rushes.py` et `critique_montage.py` demandent numpy et Pillow ; `export_xml.py --cartons png` demande Pillow (sans lui, les titres restent en texte, avec un avertissement). Mets-les dans l'environnement `~/.venv-videoedit` : `python3 -m venv ~/.venv-videoedit && ~/.venv-videoedit/bin/pip install numpy pillow`. Lancés sans numpy, `analyse_rushes.py` et `critique_montage.py` se relancent d'eux-mêmes avec son Python ; pour `--cartons png`, lance `export_xml.py` avec `$PY`. Les autres scripts n'utilisent que la bibliothèque standard. FilmCraft seulement pour le pilotage. S'il manque quelque chose, dis-le, et n'installe rien sans son accord. Sans numpy, la skill peut encore construire et exporter une timeline à partir d'un `rushes.json` rempli à la main ; elle ne peut ni analyser ni critiquer.

## Étape 1 — Recueil

Relis la demande et les pièces jointes. Ne redemande rien de ce qui est déjà dit.

Pose les questions manquantes avec l'outil AskUserQuestion s'il existe, sinon en clair, en un seul message. **4 questions au plus par appel**, 4 choix au plus par question (plus « Autre »).

| Question | Choix | Pourquoi |
|---|---|---|
| Qu'avez-vous ? | des rushes et une musique dont j'ai les droits ; des rushes, sans musique ; un montage déjà fait, à critiquer ; un montage déjà fait et ses rushes (critiquer, puis remonter) | Les deux aides. La musique : celle de l'utilisateur ou aucune. |
| Quelle famille de film ? | produit et révélation ; ouverture et ambiance (sketch, fiction, clôture compris) ; documentaire et témoignage ; bande-annonce et usage | Chaque famille a sa grammaire (`grammaire-montage.md` § 2). |
| Durée et format | la durée conseillée pour la famille, en 16:9 ; une durée précise en 16:9 (dites-la) ; vertical 9:16 ; carré 1:1 | Durées observées au § 9.1. 9:16 et 1:1 : jamais observés, convention. |
| Dans quel logiciel ? | FilmCraft (je le pilote ici) ; Premiere Pro (fichier XML) ; DaVinci Resolve (fichier XML) ; un autre (fichier EDL) | La sortie (`logiciels.md`). |

Durées conseillées (médianes observées, puis bornes) : produit 32 s (24 à 51) ; ouverture 90 s (convention, observé 65 à 143) ; transition entre deux lieux 24 s (11 à 31) ; documentaire 142 s (78 à 324) ; bande-annonce 89 s (50 à 119) ; usage 60 s (2 films : 60 et 93,5 s). Une ouverture de moins de 60 s est une convention : l'atterrissage se resserre pour garder le pic après 60 % ; sous 30 s, prends la transition entre deux lieux.

**Puis le brief, en clair**, avec seulement les lignes encore sans réponse :

```
Rushes : [dossier ou fichiers]          Musique : [fichier], et vous confirmez en avoir les droits
Nom ou titre à l'écran : [tel qu'il s'écrit]      Phrase de fin : [3 à 9 mots]     (facultatif)
Personnes filmées : [nom · fonction], et leur accord pour être nommées          (documentaire)
Paroles : [transcription horodatée ou sous-titres des entretiens]              (documentaire, répliques)
Titres de blocs : [un par sujet]                                                (bande-annonce de catalogue)
Habillage des cartons : [police] · [couleur de fond et de texte en HEX] · [logo]
```

Dis ce que deviendra ce qui reste vide : **aucun texte n'est inventé**. Tu peux proposer une formulation (une phrase, une thèse), marquée « à valider » ; elle n'entre dans `rushes.json` qu'après son accord. Un nom, un chiffre, une citation, une fonction ne se proposent jamais : un texte absent reste absent, et `assemble.py` le signale.

Pour une critique seule, demande plutôt : le fichier (vidéo rendue, XML FCP7 ou EDL), la famille, et les sous-titres et le son s'il les a ; puis va à l'étape 6.

## Étape 2 — Analyse des rushes

```bash
$PY "$SKILL/scripts/analyse_rushes.py" rushes/ --musique musique.wav -o rushes.json
```

Le script découpe chaque fichier vidéo en prises (même détecteur que le corpus) ; une photo (`.png`, `.jpg`, `.tif`…) devient une prise fixe unique, mesure mouvement, netteté, lumière, caméra (fixe, lente, rapide, à la main), zones à éviter (flou, noir, tremblement, image brûlée), moments forts candidats (`naissance_lumiere`, `plan_tenu`, `pic_mouvement`, `mouvement_continu`, `changement_lumiere`), le son, et pour la musique : tempo, attaques fortes, sommet, fin. Il écrit une planche par fichier (3 vignettes par prise) dans `planches_rushes/`. Il refuse d'écrire par-dessus un `rushes.json` déjà complété : pour relancer l'analyse (un rush ajouté), ajoute `--fusionner`, qui reprend les champs remplis à l'œil de chaque prise retrouvée (même fichier, bornes à ± 0,1 s) et ceux de la racine.

**Regarde chaque planche**, puis complète chaque prise dans `rushes.json` (`montage-spec.md` § 1.2 et 1.3) :

- `valeur` (`detail`, `serre`, `rapproche`, `moyen`, `entier`, `large`, `abstrait`) et `sujet` (`objet`, `piece` — une pièce de l'objet ; une pièce d'habitation, c'est `decor` —, `matiere`, `decor`, `lumiere`, `geste`, `ecran`, `personne`, `entretien`, `photo`… : liste au § 1.3), écrits ainsi, sans accents : sans eux, `assemble.py` choisit à l'aveugle, et il signale au `journal` un sujet qu'il ne connaît pas ;
- `role` quand une prise s'impose (`accroche`, `revelation`, `fin`, `pic`, `arrivee`, `bouton`…), `note` de 1 à 5 (`notes` n'est qu'un commentaire libre), `prises` pour écarter un passage raté ;
- documentaire : `personne`, `fonction`, et `paroles` (`entree_s`, `sortie_s`, `texte`, en secondes du fichier) de chaque prise d'entretien. La skill n'écoute pas : prends les temps dans la transcription ou les sous-titres de l'utilisateur ; `son.passages_actifs` ne donne que des bornes candidates, voix et bruit mêlés ;
- à la racine : `nom`, `phrase`, `logo`, `police`, `couleurs`, et `format` (`{"largeur": 1080, "hauteur": 1920}` pour du 9:16).

Dis à l'utilisateur ce qui manque pour la famille choisie : par exemple, pas de plan de l'objet entier (pas de révélation possible), pas de plan large (pas d'atterrissage), une seule personne pour un documentaire choral. Ce sont des plans à tourner, pas des défauts à cacher.

## Étape 3 — Le plan de montage, montré avant

Lis `references/grammaire-montage.md` : les § 1 à 3 une fois par conversation, puis la section de la famille. Choisis la forme d'après les rushes (§ 2) ; dis-la. En documentaire, choisis d'abord la parole : quelles prises, dans quel ordre, en quels chapitres (`ordre`, `chapitre` dans `paroles`). Ne coupe jamais une parole pour lui faire dire autre chose.

Puis lance le premier assemblage. Il n'envoie rien à aucun logiciel :

```bash
python3 "$SKILL/scripts/assemble.py" rushes.json --famille produit [--schema revelation_tardive] \
        [--duree 32] [--musique musique.wav|aucune] [--fps 25] [--tc-debut 00:00:00:00]
```

Il écrit `montage.json`, `montage.annotations.json`, et imprime le tableau du plan. **Montre le plan avant de construire**, en une table lisible :

| # | Temps | De → à | Ce qu'on voit (rushes) | Texte | Règle |
|---|---|---|---|---|---|
| 1 | ouverture | 0:00,0 → 0:01,0 | noir | — | P3, observé 13 sur 16 |
| 2 | accroche | 0:01,0 → 0:04,5 | la matière sort du noir (`r03`) | — | P4 |

Sous la table : la forme choisie et pourquoi ; ce que `journal` signale (rushes manquants, fondus raccourcis, textes absents) ; les mesures de `controle` hors cible, avec la raison ; les conventions prises (durée hors des bornes observées, 9:16, chapitres) ; ce qui sera à faire à la main (étalonnage noir et blanc, format large, recadrage en 9:16 ou 1:1, crédits). **Attends son accord** ou ses changements avant l'étape 5.

## Étape 4 — `montage.json`

Applique ses changements à la source : dans `rushes.json` (`role`, `note`, `prises`, `meilleur_s`), ou par les options d'`assemble.py` (`--schema`, `--duree`, `--musique aucune`), puis relance. Édite `montage.json` à la main seulement pour un réglage fin : les champs `_img` font foi, chaque plan commence où finit le précédent, et `sortie_img − entree_img = duree_img`. Les trois sorties (`export_xml.py`, `export_edl.py`, `filmcraft_build.py`) refusent un montage incohérent, un plan qui sort de son rush, ou un fondu enchaîné sans images de part et d'autre de la coupe.

Code d'`assemble.py` : 0 = conforme aux cibles ; 2 = timeline produite avec des écarts (lis `journal`, une ligne par écart) ; 1 = entrée illisible ou commande invalide, rien n'est écrit.

## Étape 5 — Construction

Lis `references/logiciels.md` (la section du logiciel choisi).

**FilmCraft, piloté :**

```bash
python3 "$SKILL/scripts/fc.py" etat
python3 "$SKILL/scripts/filmcraft_build.py" montage.json --simulation
python3 "$SKILL/scripts/filmcraft_build.py" montage.json --images controle/ --rendre film.mp4 --rapport filmcraft-rapport.json
```

Un nouveau projet est créé, rien n'est enregistré (`--enregistrer` seulement vers un fichier qui n'existe pas, et seulement s'il le demande). Ne quitte jamais l'app. Code 0 = séquence construite et relue sans écart. `--rendre` exporte la vidéo sur toute la durée du montage : un noir final est un trou sur V1, et un export de la séquence entière s'arrête au dernier élément, sans lui. Regarde la planche de `controle/` avant d'aller plus loin.

**Premiere Pro ou DaVinci Resolve :**

```bash
python3 "$SKILL/scripts/export_xml.py" montage.json -o montage.xml --verifier
$PY "$SKILL/scripts/export_xml.py" montage.json -o montage-png.xml --cartons png --verifier   # tous les textes en images
python3 "$SKILL/scripts/export_edl.py" montage.json -o montage.edl --verifier                 # en secours
```

Code 0 de `--verifier` avant de remettre un fichier. Donne-lui le pas à pas d'import de `logiciels.md` § 3 ou § 4, et dis que ces deux logiciels n'ont pas été essayés à l'écriture de la skill.

Exporte `montage.xml` dans tous les cas, même pour FilmCraft : c'est l'entrée de la critique.

## Étape 6 — La critique, avec la même mesure

Lis `references/critique.md`. La même mesure sert au montage de la skill et à celui de l'utilisateur.

**Le montage de la skill.** `assemble.py` a imprimé la commande exacte. Elle ressemble à :

```bash
$PY "$SKILL/scripts/critique_montage.py" montage.xml --famille produit --sous-famille revelation_objet \
    --schema tardif --annotations montage.annotations.json --mesurer-medias [--son musique.wav] \
    [--sous-titres paroles.srt] --sortie critique.md --json critique.json
```

**Le montage de l'utilisateur.** En trois passes : mesurer, avec `--planche` pour une vidéo ; regarder la planche et écrire les annotations (valeurs, révélation, nom, textes, fondus candidats) ; relancer avec `--annotations` (`critique.md` § 3 et § 5).

Lis le rapport : verdict, puis « Ce qui s'écarte », « Notes », « À vérifier à l'œil », « Non mesuré ». Pour chaque alerte, `critique.md` § 6 donne la règle et le geste qui corrige. Corrige dans l'ordre : la forme, puis le rythme, puis les transitions et les noirs, puis le texte et le son ; relance la critique après chaque étape. Reviens à l'étape 4 pour un montage de la skill ; donne des correctifs au timecode pour celui de l'utilisateur. Arrête-toi à zéro alerte, ou quand chaque alerte restante a une raison dite (un rush manque, un choix voulu).

Regarde aussi le film, ou au moins la planche, en entier : la critique ne voit ni un raccord réussi, ni le sens d'une phrase, ni l'émotion d'un visage.

## Étape 7 — La remise

Remets le travail en un message court :

1. **les fichiers** : `montage.json`, `montage.xml` (et `.edl`), ou le nom du projet et de la séquence FilmCraft ; la planche de contrôle ; `critique.md` ;
2. **le film en une phrase** : famille, forme, durée, nombre de plans ;
3. **le verdict de la critique** et les écarts gardés, chacun avec sa raison ;
4. **à faire à la main** : textes à poser (marqueurs), étalonnage, format large, recadrage en 9:16 ou 1:1 (aucun export ne recadre), médias à relier, niveau de la musique ;
5. **à fournir pour une meilleure version** : les plans à tourner, les textes absents ;
6. en une ligne : les conventions prises, et que Premiere Pro et DaVinci Resolve n'ont pas été essayés ici ;
7. pour la suite : on modifie `rushes.json` ou `montage.json` et on relance ; une retouche faite dans le XML est perdue au prochain export.

Pour une critique seule : le verdict, les 3 à 5 écarts qui comptent avec leur geste et leur timecode, ce qui colle, ce qui n'a pas pu être mesuré (`critique.md` § 9).

## Rappels

- **La grammaire, jamais la marque.** Aucune image, aucun son, aucun logo, aucune police d'Apple ; aucune phrase des films, même traduite ; aucune signature (ni mention de l'appareil ou du logiciel de tournage). Ne cite jamais un film du corpus par son titre : dis « les films de révélation d'objet ».
- **Musique fournie ou aucune.** Un fichier de l'utilisateur, dont il a les droits. Jamais une musique cherchée, téléchargée, générée ou prise dans une bibliothèque.
- **Aucun texte, aucun chiffre, aucun témoignage inventés.** Les noms et fonctions des personnes filmées, avec leur accord. Un chiffre à l'écran seulement s'il est dit dans les rushes ou fourni avec sa source.
- **Couper franc par défaut** : le fondu enchaîné reste une exception choisie (G1, G2).
- **Vitesse normale** : aucun ralenti, aucun accéléré pour atteindre une durée.
- **Le projet de l'utilisateur** : rien n'est enregistré, fermé ni quitté sans sa demande ; dans FilmCraft, un essai porte le préfixe `TEST-`.
- **Dire les limites** : ce qui est convention, ce qui n'est pas mesuré, ce qui n'a pas été essayé.

## Fichiers de référence : quand les lire

| Fichier | Quand |
|---|---|
| `references/grammaire-montage.md` | Étape 3 : § 1 à 3 une fois, puis la section de la famille (§ 4 à 7), le son (§ 8), la durée et le format (§ 9). Étape 6 : pour comprendre une règle citée par la critique. |
| `references/critique.md` | Étape 6 : lancer la critique, écrire les annotations, passer d'un contrôle à un geste (§ 6), rendre la critique (§ 9). |
| `references/logiciels.md` | Étape 5 : FilmCraft (§ 2), Premiere Pro (§ 3), DaVinci Resolve (§ 4), EDL (§ 5). Étape 6 : exporter une timeline retouchée (§ 6). |
| `references/montage-spec.md` | Étapes 2 et 4 : les champs de `rushes.json` et de `montage.json`, les familles et schémas, la table des commandes FilmCraft. |
| `references/cibles/<famille>.json` | Les mesures du corpus, avec leurs comptes. Lues par la critique ; à ouvrir pour une valeur précise. |
| `scripts/gabarits.json` | Les cibles de construction d'`assemble.py`, chacune avec sa base ou « convention ». |
