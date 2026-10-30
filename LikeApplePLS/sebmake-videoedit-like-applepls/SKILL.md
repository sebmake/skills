---
name: sebmake-videoedit-like-applepls
description: "Montage à la manière des films de keynote Apple : monte les rushes de l'utilisateur (et sa musique), ou assemble des chapitres déjà faits avec voix, sous-titres et musique atténuée sous la voix, dans FilmCraft ou en XML FCP7 (ou EDL) pour Resolve et Premiere ; ou critique un montage existant plan par plan contre les films de sa famille (rythme, coupes, noirs, révélation, texte), avec correctifs au timecode. Use it whenever someone wants to edit their own footage like an Apple keynote film, asks for editing help, a timeline, to assemble a narrated walkthrough, or an edit critique (pacing, cuts, transitions, where the reveal or title lands), works in DaVinci Resolve, Premiere Pro or FilmCraft, even without the word Apple. Not for a product film generated in motion design (sebmake-videopresentation-likeapplepls), animating titles or logos (sebmake-motiondesign-likeapplepls), or slides (sebmake-keynote-likeapple-pls)."
---

# Montage à la manière des films de keynote

Cette skill aide à monter. Elle fait trois choses :

1. **construire une timeline** à partir des rushes de l'utilisateur, et de sa musique s'il en a une, puis la poser dans FilmCraft (pilotée) ou la remettre en fichier pour Premiere Pro et DaVinci Resolve ;
2. **assembler un montage composé** : des éléments déjà faits (chapitres ou scènes rendus, une voix par phrase, des sous-titres, une musique qui s'efface sous la voix, des sons ponctuels), chacun sur sa piste et à son instant ;
3. **critiquer un montage** : le mesurer plan par plan contre les films de sa famille, et dire quoi corriger, au timecode près.

Dans FilmCraft, le montage reste **un projet qu'on comprend et qu'on reprend** : chaque piste est nommée par son rôle, la skill montre comment il est fait (capture, carte des pistes), relit les retouches faites à la main et les reporte dans `montage.json`. On continue ainsi à travailler dans l'outil, tour après tour.

Les règles viennent de quatre analyses des films de 8 keynotes (2019 à 2026), découpés plan par plan : 16 films produit, 20 films d'ouverture et d'ambiance, 8 documentaires, 8 bandes-annonces et films d'usage. Chaque règle porte son compte (« N sur M ») ; ce qui n'est pas mesuré est marqué **convention**. La skill reprend la **grammaire**, jamais la **marque** : ni image, ni son, ni logo, ni police d'Apple, ni phrase des films. Les images, la musique, les textes et le logo sont ceux de l'utilisateur.

La chaîne :

```
rushes ─ analyse_rushes.py ─▶ rushes.json (complété à l'œil) ─ assemble.py ─▶ montage.json
   plan.json (chapitres, voix, sous-titres, musique, sons) ─ compose_montage.py ─▶ montage.json   (montage composé)
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
| Qu'avez-vous ? | des rushes et une musique dont j'ai les droits ; des rushes, sans musique ; des éléments déjà composés (chapitres ou scènes rendus, voix, sous-titres, musique, sons) ; un montage déjà fait, à critiquer (avec ou sans ses rushes) | Les trois aides. La musique : celle de l'utilisateur ou aucune. Le troisième choix mène à l'étape 2 bis. |
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

## Étape 2 bis — Le montage composé (à la place des étapes 2 à 4)

Quand les images sont déjà faites (une démonstration en chapitres, des scènes rendues par `sebmake-motiondesign-likeapplepls`, un film découpé en parties) et qu'il faut les assembler avec une voix, des sous-titres, une musique et des sons, il n'y a pas de rushes à choisir. Écris `plan.json` (format dans l'en-tête de `compose_montage.py` et `montage-spec.md` § 2.8), puis :

```bash
python3 "$SKILL/scripts/compose_montage.py" plan.json                 # → montage.json (+ montage.srt si « sous_titres »: « auto »)
python3 "$SKILL/scripts/filmcraft_build.py" montage.json --simulation
```

- **Chapitres** bout à bout sur V1, coupe franche, image seule ; un marqueur par chapitre.
- **Voix** : un fichier par phrase, à l'instant où l'image la demande (le temps vient de la composition qui a fait l'image, jamais d'un temps retapé à la main). `compose_montage.py` signale deux voix qui se chevauchent et une voix qui dépasse la fin.
- **Sous-titres** : le SRT de l'utilisateur, ou `auto` : un sous-titre par phrase, tiré du texte des voix.
- **Musique** : `niveau_db`, `fondu_sortie_s`, `decalage_s` (où elle commence dans le fichier), et `attenuation_db` : FilmCraft l'efface d'autant sous les voix (son essentiel : voix en « dialogue », musique en « music », atténuation générée en images clés de volume). 12 dB est un bon départ (convention).
- **Sons** : chacun à son instant, sur A3.

**La voix off.** Si l'utilisateur a ses fichiers de voix, on les prend. Sinon, la skill peut les fabriquer :

```bash
python3 "$SKILL/scripts/voix.py" etat                       # edge-tts est-il là ?
```

- **edge-tts absent** : recommande-le, dans une question (AskUserQuestion) : « Pour de meilleurs résultats, voulez-vous installer edge-tts ? Voix naturelles et gratuites (Vivienne, Denise, Henri…), internet requis. » Choix : installer edge-tts (conseillé) ; une voix de macOS, robotique, pour un brouillon ; j'ai mes propres voix ; pas de voix. Sur son accord seulement : `python3 -m venv ~/.venv-sebmake-voix && ~/.venv-sebmake-voix/bin/pip install edge-tts`.
- **Le texte d'abord** : les phrases sont les siennes, ou proposées et marquées « à valider » ; rien n'est dit avant son accord.
- **L'audition** : `voix.py audition phrases.txt --voix Vivienne,Denise,Henri,Remy,Eloise --sortie audition/` ; il choisit à l'oreille.
- **La génération** : `voix.py generer phrases.txt --voix <choix> --sortie voix/` → un fichier par phrase et `voix/voix.json` (durée, instant de chaque mot). Les durées placent les phrases sans chevauchement ; l'instant des mots pose un mouvement ou un clic sur le mot qui l'annonce.
- edge-tts passe par un service en ligne de Microsoft, gratuit mais non officiel : dis-le si le film sort de l'entreprise. La voix de macOS ne donne pas l'instant des mots.

Montre le tableau des pistes (ce qui va où, de quand à quand) et ce que signale `compose_montage.py` avant de construire. Puis étape 5.

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
python3 "$SKILL/scripts/filmcraft_build.py" montage.json --images controle/ --carte carte-montage.md --capture capture-filmcraft.png \
        --rendre film.mp4 --rapport filmcraft-rapport.json
```

Un nouveau projet est créé, rien n'est enregistré (`--enregistrer` seulement vers un fichier qui n'existe pas, et seulement s'il le demande). Les pistes sont nommées par leur rôle (Image, Cartons et textes, Paroles et voix, Musique, Son des images et gestes), les sous-titres vont sur C1. `--carte` écrit la carte du montage (chaque piste, son rôle, ses éléments, l'atténuation générée) ; `--capture` la fenêtre de FilmCraft, séquence ouverte (l'écran doit être allumé). Les sous-titres de C1 ne sont pas incrustés dans la vidéo rendue. Ne quitte jamais l'app. Code 0 = séquence construite et relue sans écart. `--rendre` exporte la vidéo sur toute la durée du montage : un noir final est un trou sur V1, et un export de la séquence entière s'arrête au dernier élément, sans lui. Regarde la planche de `controle/` avant d'aller plus loin.

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

## Étape 6 bis — Montrer le montage, puis continuer

L'utilisateur doit pouvoir **comprendre comment le montage est fait** et le reprendre lui-même dans FilmCraft. Montre-lui la capture de FilmCraft et la carte du montage, puis explique en quelques lignes : V1 porte l'image, chapitre par chapitre ; A1 chaque phrase à son instant ; A2 la musique et la courbe de volume qui la creuse sous la voix ; A3 les gestes ; C1 les sous-titres ; les marqueurs, la structure.

Puis **la boucle continue** : il retouche à la main dans FilmCraft (un plan raccourci, une phrase déplacée, la musique plus basse) ou demande une modification. Relis la séquence (`python3 "$SKILL/scripts/fc.py" inspecter`, ou un export XML relu par `lire_timeline.py`), dis ce qui a changé, reporte-le dans `montage.json` (ou `plan.json`), reconstruis dans un projet `TEST-`, remesure et recritique. Rien de ce qu'il a fait à la main ne doit se perdre au passage suivant.

**Garder le projet**, sur sa demande seulement : `--enregistrer <dossier>/<nom>.fcproj`, un fichier neuf, jamais par-dessus.

## Étape 7 — La remise

Remets le travail en un message court :

1. **les fichiers** : `montage.json` (et `plan.json` pour un montage composé), `montage.xml` (et `.edl`), ou le nom du projet et de la séquence FilmCraft ; la planche de contrôle ; la carte du montage et la capture ; `critique.md` ;
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
- **Voix fournies ou synthétisées avec accord.** Les fichiers de voix de l'utilisateur ; sinon `voix.py` (edge-tts recommandé, installé seulement s'il le veut), après son accord sur le texte et sur la voix.
- **Une retouche à la main ne se perd jamais** : relue (`fc.py inspecter`, `lire_timeline.py`), reportée dans `montage.json` ou `plan.json`, dite à l'utilisateur.
- **Aucun texte, aucun chiffre, aucun témoignage inventés.** Les noms et fonctions des personnes filmées, avec leur accord. Un chiffre à l'écran seulement s'il est dit dans les rushes ou fourni avec sa source.
- **Couper franc par défaut** : le fondu enchaîné reste une exception choisie (G1, G2).
- **Vitesse normale** : aucun ralenti, aucun accéléré pour atteindre une durée.
- **Le projet de l'utilisateur** : rien n'est enregistré, fermé ni quitté sans sa demande ; un enregistrement va dans un fichier neuf ; dans FilmCraft, un essai porte le préfixe `TEST-`.
- **Dire les limites** : ce qui est convention, ce qui n'est pas mesuré, ce qui n'a pas été essayé.

## Fichiers de référence : quand les lire

| Fichier | Quand |
|---|---|
| `references/grammaire-montage.md` | Étape 3 : § 1 à 3 une fois, puis la section de la famille (§ 4 à 7), le son (§ 8), la durée et le format (§ 9). Étape 6 : pour comprendre une règle citée par la critique. |
| `references/critique.md` | Étape 6 : lancer la critique, écrire les annotations, passer d'un contrôle à un geste (§ 6), rendre la critique (§ 9). |
| `references/logiciels.md` | Étape 5 : FilmCraft (§ 2), Premiere Pro (§ 3), DaVinci Resolve (§ 4), EDL (§ 5). Étape 6 : exporter une timeline retouchée (§ 6). |
| `references/montage-spec.md` | Étapes 2 et 4 : les champs de `rushes.json` et de `montage.json`, les familles et schémas, la table des commandes FilmCraft. Étape 2 bis : le montage composé (§ 2.8). |
| `scripts/voix.py` | Étape 2 bis : voix off de synthèse (edge-tts conseillé, `say` de macOS en repli) : état, audition, génération avec l'instant des mots. |
| `scripts/compose_montage.py` | Étape 2 bis : `plan.json` (chapitres, voix, sous-titres, musique, sons) → `montage.json`. |
| `references/cibles/<famille>.json` | Les mesures du corpus, avec leurs comptes. Lues par la critique ; à ouvrir pour une valeur précise. |
| `scripts/gabarits.json` | Les cibles de construction d'`assemble.py`, chacune avec sa base ou « convention ». |
