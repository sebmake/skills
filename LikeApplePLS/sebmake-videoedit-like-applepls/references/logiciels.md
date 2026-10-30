# Les logiciels : FilmCraft piloté, Premiere Pro et DaVinci Resolve par fichier

Ce fichier dit comment `montage.json` devient une timeline dans le logiciel de l'utilisateur, et comment une timeline revient vers la critique. Le format de `montage.json` et la table complète des commandes FilmCraft sont dans `montage-spec.md`.

## Sommaire

1. Qui reçoit quoi
2. FilmCraft, piloté par son canal de contrôle
3. Premiere Pro, par XML
4. DaVinci Resolve, par XML
5. L'EDL, en secours
6. Ramener une timeline vers la critique
7. Limites connues

**Ce qui a été essayé, et ce qui ne l'a pas été.** FilmCraft était installé sur la machine où la skill a été écrite : la construction, la vérification et l'import y ont été faits. Premiere Pro et DaVinci Resolve n'y étaient pas : leurs fichiers ont été vérifiés par relecture, par une lecture indépendante (`lire_timeline.py`) et par l'importeur de FilmCraft, qui lit les mêmes formats. Les pas à pas des § 3 et 4 suivent ce que ces logiciels documentent ; ils n'ont pas été rejoués ici. Dis-le à l'utilisateur.

---

## 1. Qui reçoit quoi

| Logiciel | Ce que la skill fournit | Commande |
|---|---|---|
| FilmCraft | la séquence construite dans l'app, vérifiée, avec des titres natifs modifiables | `python3 filmcraft_build.py montage.json` |
| Premiere Pro | un XML FCP7 (« xmeml ») | `python3 export_xml.py montage.json --verifier` |
| DaVinci Resolve | le même XML FCP7 | `python3 export_xml.py montage.json --verifier` |
| Tout autre logiciel de montage | une EDL CMX3600 | `python3 export_edl.py montage.json --verifier` |

Ces quatre scripts n'utilisent que la bibliothèque standard de Python 3.9 (sauf `--cartons png`, qui demande Pillow). `--verifier` relit le fichier écrit et le compare au montage, image par image : code 0 si tout colle, 3 sinon, 1 si `montage.json` est incohérent, si un plan sort de son rush ou si un fondu enchaîné n'a pas d'images de part et d'autre de la coupe (durée du fichier lue par ffprobe ; un fichier introuvable n'est qu'un avertissement). `filmcraft_build.py` fait les mêmes refus, simulation comprise.

Les pistes sont toujours les mêmes : **V1** les plans, **V2** les cartons ; **A1** les paroles, **A2** la musique, **A3** le son des images. Chaque carton et chaque temps de la structure portent un marqueur de séquence.

Les chemins des rushes sont écrits en absolu dans le XML et l'EDL. Ne déplace pas les rushes entre l'export et l'import ; sinon, il faudra relier les médias.

---

## 2. FilmCraft, piloté par son canal de contrôle

FilmCraft est une app de montage à la manière de Premiere Pro. Elle se pilote par un canal local : TCP `127.0.0.1:9876`, une ligne JSON par requête `{"id", "method", "params"}`, une ligne JSON en réponse. Trois méthodes : `engine.commands` (la liste des commandes, 701 dans la version 0.12.0), `engine.execute` (une commande et ses paramètres), `ui.screenshot`. Les inspections (`sequence.inspect`, `project.inspect`, `state.inspect`) sont des **commandes** : elles passent par `engine.execute`. Les temps sont en « ticks », 254 016 000 000 par seconde, comme dans Premiere Pro. `scripts/fc.py` est le client.

### 2.1 Lancer et vérifier le canal

```bash
python3 "$SKILL/scripts/fc.py" etat          # projet, séquence active, sélection
```

- Réponse normale : l'app écoute. Passe à la suite.
- « aucune app à l'écoute » (code 3) : FilmCraft n'est pas lancé, ou tourne sans son canal. `filmcraft_build.py` le lance lui-même s'il est fermé (`open -a FilmCraft --args --control 9876`). S'il est **déjà ouvert sans canal**, demande à l'utilisateur de le quitter et de le relancer avec cette commande : ne le quitte jamais toi-même, son projet est peut-être ouvert.

### 2.2 Construire la séquence

D'abord à blanc, puis pour de bon :

```bash
python3 "$SKILL/scripts/filmcraft_build.py" montage.json --simulation          # n'envoie rien, liste les commandes
python3 "$SKILL/scripts/filmcraft_build.py" montage.json --images controle/ --rendre film.mp4 --rapport filmcraft-rapport.json
```

Ce que fait le script, une commande FilmCraft par étape :

1. un **nouveau projet** nommé comme le montage (défaut) ; ou le projet déjà ouvert avec `--projet ouvert` ;
2. un chutier « <nom> rushes », l'import des rushes, de la musique et du logo ;
3. une séquence au format du montage (3 pistes vidéo, 3 pistes son) ;
4. V1 : chaque plan à sa place, entrée et durée à l'image près ; les fonds de couleur des cartons ;
5. V2 : les cartons en **titres natifs**, modifiables, à la taille et à la place du montage ;
6. A1 paroles, A2 musique (niveau, fondu de sortie), A3 son des images ;
7. les transitions : fondus enchaînés centrés, sorties du noir, départs au noir, passage au blanc, poussée (FilmCraft les aligne seul) ;
8. les marqueurs de séquence ;
9. la vérification par `sequence.inspect` : chaque plan, chaque parole, la musique, chaque transition ;
10. avec `--images` : une image du programme au milieu de chaque plan (`file.exportFrame`, cartons compris) et une planche.

Options : `--nom NOM` (nom du projet et de la séquence ; préfixe `TEST-` pour un essai), `--rendre FICHIER.mp4` (la vidéo H.264, vers un fichier qui n'existe pas encore), `--port`, `--rapport`. Codes de sortie : 0 séquence construite et conforme ; 1 erreur ; 2 FilmCraft injoignable ; 3 écarts à la vérification.

Sur les essais faits à l'écriture de la skill, trois séquences (25 et 23,976 images par seconde, avec musique, paroles, bandeaux, dix cartons) ont été construites et relues par `sequence.inspect` sans écart, et chaque plan d'entretien est retombé sur sa parole à l'image près.

### 2.2 bis Le montage composé, et la carte

`compose_montage.py plan.json` puis `filmcraft_build.py montage.json` posent les chapitres sur V1, une voix par phrase sur A1, la musique sur A2 (atténuée sous les voix si `attenuation_db` : son essentiel de FilmCraft), les sons sur A3 et les sous-titres sur C1 ; les pistes portent le nom de leur rôle. `--carte carte-montage.md` décrit chaque piste et ce qu'elle porte ; `--capture capture.png` prend la fenêtre de FilmCraft (l'app passe au premier plan ; l'écran doit être allumé, sinon « no frame was presented »). Ce sont les deux pièces à montrer pour expliquer le montage avant qu'on le retouche à la main.

### 2.3 Regarder le résultat

La vérification compare des nombres. Regarde aussi les images : ouvre la planche du dossier `--images`, et vérifie que chaque carton est lisible, que rien de noir ne cache une image, que la révélation et la fin tombent où le plan le dit.

```bash
python3 "$SKILL/scripts/fc.py" inspecter                           # résumé lisible de la séquence active
python3 "$SKILL/scripts/fc.py" image 24.5 verif-24s.png            # une image du programme à 24,5 s
python3 "$SKILL/scripts/fc.py" capture fenetre.png                 # la fenêtre de l'app
```

### 2.4 Le projet de l'utilisateur

- **Rien n'est enregistré**, sauf `--enregistrer CHEMIN.fcproj`, vers un fichier **qui n'existe pas encore**. Jamais par-dessus un fichier. L'enregistrement reste à l'utilisateur.
- `fc.py` refuse les commandes qui ouvrent, enregistrent, ferment, suppriment ou quittent (`file.save`, `file.open`, `file.closeProject`, `app.quit`…), sauf avec `--autoriser`. Ne l'emploie que si l'utilisateur le demande.
- `--projet ouvert` ajoute un chutier et une séquence au projet de l'utilisateur, sans enregistrer. Préfère le nouveau projet (défaut), sauf s'il demande l'inverse.
- Ne quitte jamais l'app. Ne touche à aucune séquence qui n'est pas la tienne.

### 2.5 Retoucher, puis critiquer de nouveau

L'utilisateur retouche à la main dans FilmCraft : les titres sont natifs, les plans sont de vrais plans. Pour mesurer le résultat retouché, exporte la séquence active en XML FCP7, puis lance la critique dessus (§ 6) :

```bash
python3 "$SKILL/scripts/fc.py" cmd sequence.open '{"item": "<id de la séquence>"}'
python3 "$SKILL/scripts/fc.py" cmd file.exportFcp7Xml '{"path": "/chemin/absolu/retouche.xml"}'
```

L'identifiant de la séquence se lit dans `fc.py etat` ou `fc.py inspecter`. Dans un essai, un titre de FilmCraft est sorti de cet export comme un plan d'image portant son texte pour nom : la critique le lit comme une image. Annote-le dans `textes` (voir `critique.md` § 5).

**La vidéo.** `--rendre film.mp4` passe par `file.exportMedia` (H.264), de 0 à la durée du montage (`range: "custom"`). Essayé à la relecture : 45 s rendues en 1 125 images, noir final compris, en une dizaine de secondes. Sans ces bornes, l'export de la séquence entière s'arrête au dernier élément : le noir final, qui est un trou sur V1, disparaît (44,04 s au lieu de 45,00 s au même essai). C'est l'entrée la plus complète de la critique : mouvement, couleur et son y sont mesurés. Un rendu sans musique porte une piste son muette : la critique la lit comme une absence de son.

### 2.6 Quand ça ne répond pas

| Ce qu'on voit | Pourquoi | Que faire |
|---|---|---|
| « aucune app à l'écoute » (code 3) | FilmCraft fermé, ou ouvert sans `--control 9876` | § 2.1 |
| « délai dépassé » (code 2) | l'app est occupée (import, rendu) ou attend au second plan | `fc.py activer` (met l'app au premier plan), puis relancer ; ou `--relance` |
| « unknown method » | une inspection appelée comme méthode | `fc.py cmd sequence.inspect` |
| « refusé » (code 4) | commande protégée | seulement à la demande de l'utilisateur : `--autoriser` |
| écarts à la vérification (code 3 de `filmcraft_build.py`) | un plan, une parole ou une transition n'est pas où le montage le dit | lire le rapport (`--rapport`), comparer à `montage.json`, reconstruire dans un nouveau projet |
| une commande inconnue | la version de l'app a changé | `fc.py commandes <filtre>` donne la liste et les paramètres |

---

## 3. Premiere Pro, par XML

Non testé dans Premiere Pro (voir l'encadré du début).

**Avant l'import.**

```bash
python3 "$SKILL/scripts/export_xml.py" montage.json -o montage.xml --verifier
python3 "$SKILL/scripts/export_xml.py" montage.json -o montage-png.xml --cartons png --verifier   # cartons en images
```

Choisis le mode des cartons :

| `--cartons` | Ce que reçoit le logiciel | Quand |
|---|---|---|
| `texte` (défaut) | un générateur « Text » pour un carton sur fond noir ; un texte posé sur une image ou sur une couleur n'est qu'un **marqueur**, à poser à la main | l'utilisateur veut des titres modifiables et posera les bandeaux lui-même |
| `png` | une image PNG par carton (texte et fond déjà dessinés), sur V2 ; demande Pillow et le fichier de la police de l'utilisateur (`police.fichier`). L'export imprime la police employée ; sans fichier, il prévient et se replie sur Inter, DejaVu Sans ou Arial | il veut voir tous les textes dès l'import |
| `generateurs` | le générateur « Text » partout | à ses risques : un importeur qui ne lit pas ce générateur met de la vidéo noire à la place, et cache l'image dessous (vu dans FilmCraft) |

**Pas à pas** (menus de Premiere Pro en français, puis en anglais) :

1. **Fichier > Importer…** (File > Import…), choisis `montage.xml`. Premiere crée un chutier au nom du fichier, avec la séquence et les médias.
2. Ouvre la séquence. Vérifie sa cadence et sa taille dans **Séquence > Paramètres de la séquence** : ce sont celles de `montage.json` (`format`).
3. Médias hors ligne (rouges) : clic droit sur eux, **Lier le média…** (Link Media…), et montre le dossier des rushes.
4. Vérifie les pistes (V1, V2, A1 à A3) et les transitions. Le fondu enchaîné est un Cross Dissolve. Le passage au blanc et la poussée sont écrits « Dip to White » et « Push » : vérifie qu'ils sont arrivés, sinon pose-les à la main au marqueur.
5. Cartons en mode `texte` : ouvre le panneau **Marqueurs** ; chaque marqueur porte le texte et sa place. Pose le titre avec l'outil Texte, dans la police de l'utilisateur, petit et centré (voir `grammaire-montage.md` G6).
6. Écoute la musique : le niveau et les respirations du documentaire se règlent à l'oreille (aucune courbe de volume n'est écrite).
7. Ce que le XML ne porte pas : l'étalonnage noir et blanc, le format large (bandes), le recadrage en 9:16 ou 1:1 (chaque plan sur son sujet, sans bandes : les plans entrent à leur taille), les crédits d'une bande-annonce d'œuvre. Ils se font dans Premiere.

---

## 4. DaVinci Resolve, par XML

Non testé dans DaVinci Resolve (voir l'encadré du début).

**Avant l'export.** Resolve fait commencer ses timelines à `01:00:00:00` par habitude. Pour s'y tenir, construis le montage avec `assemble.py … --tc-debut 01:00:00:00`, puis exporte comme pour Premiere. Le mode `--cartons png` est le plus sûr : la conversion du générateur « Text » par Resolve n'a pas été vérifiée.

**Pas à pas** (menus de Resolve en français, puis en anglais) :

1. Dans un projet neuf, règle d'abord la cadence de la timeline sur celle de `montage.json` : **Fichier > Paramètres du projet > Master Settings** (File > Project Settings). Resolve fige souvent cette cadence dès que des médias sont importés.
2. **Fichier > Importer > Timeline…** (File > Import > Timeline…), choisis `montage.xml`. Dans la fenêtre qui suit, laisse cochée l'option qui importe automatiquement les clips sources dans le Media Pool.
3. Médias hors ligne : sélectionne-les dans le Media Pool, clic droit, **Relier les clips sélectionnés** (Relink Selected Clips), et montre le dossier des rushes.
4. Ouvre la timeline dans la page Edit. Vérifie pistes, transitions, marqueurs, comme au § 3 (étapes 4 à 6).
5. Étalonnage noir et blanc, format large, recadrage en 9:16 ou 1:1 (chaque plan sur son sujet, sans bandes), niveau de la musique : dans Resolve.

---

## 5. L'EDL, en secours

L'EDL CMX3600 est le format le plus ancien et le plus lu. Elle sert quand le XML ne passe pas.

```bash
python3 "$SKILL/scripts/export_edl.py" montage.json -o montage.edl --verifier
```

- Ce qu'elle porte : une seule piste vidéo, les noirs (bobine `BL`), les fondus (`D` et leur durée en images), le passage au blanc (`D` et un commentaire), les paroles (`A`), la musique (`A2`), le son des images (`A3`).
- Ce qu'elle ne porte pas : les cartons (commentaires `* CARTON`), la poussée (une coupe et un commentaire), le niveau de la musique, les marqueurs (commentaires `* MARQUEUR`).
- Chaque événement nomme son rush (bobine = identifiant du rush, 8 caractères au plus) et son fichier (`* FROM CLIP NAME`, `* SOURCE FILE`). Le logiciel retrouve les clips par ce nom : importe d'abord les rushes (dans Resolve, dans le Media Pool), puis l'EDL.
- Cadences NTSC (23,976 et 29,97) : timecode non drop-frame, compté à 24 ou 30 images.
- FilmCraft lit l'EDL à 24 images par seconde, sans réglage : pour FilmCraft, préfère `filmcraft_build.py` ou le XML.
- Rushes à une autre cadence que la timeline (le `journal` dit « cadences mêlées ») : leurs entrées source sont écrites en timecode à la cadence de la timeline. Un logiciel qui conforme l'EDL par le timecode du clip peut les lire autrement (non essayé, faute de Premiere Pro et de Resolve) : préfère le XML, ou vérifie ces plans à l'import.

---

## 6. Ramener une timeline vers la critique

La critique lit une vidéo rendue, un XML FCP7 ou une EDL (`critique.md` § 2).

| Logiciel | Exporter | Attention |
|---|---|---|
| Premiere Pro | **Fichier > Exporter > Final Cut Pro XML…** (File > Export > Final Cut Pro XML…) | pas le FCPXML : la critique ne le lit pas |
| DaVinci Resolve | **Fichier > Exporter > Timeline…** (File > Export > Timeline…), format « FCP 7 XML » | idem |
| FilmCraft | `fc.py cmd file.exportFcp7Xml '{"path": "…"}'` sur la séquence active (§ 2.5) | les titres peuvent sortir comme des plans d'image : les annoter |
| Les trois | une vidéo rendue (H.264 suffit) | la vidéo donne le mouvement, la couleur et le son ; les textes posés sur une image n'y sont pas vus |

Avec un XML, ajoute `--mesurer-medias` si les rushes sont sur la machine : sinon le mouvement et la couleur ne sont pas mesurés. Avec une EDL, donne `--fps` ; ses entrées sont en timecode source, et la critique en retranche le timecode inscrit dans chaque fichier (10:00:00:00 sur bien des caméras) avant de mesurer. Pour la parole, demande les sous-titres (`.srt` ou `.vtt`) que le logiciel sait exporter, ou écris-les depuis `montage.json` (`critique.md` § 3).

---

## 7. Limites connues

| Limite | Où | Que faire |
|---|---|---|
| Premiere Pro et DaVinci Resolve non installés à l'écriture | XML, EDL | les fichiers sont vérifiés par relecture, par `lire_timeline.py` et par l'import dans FilmCraft (chaque plan, chaque entrée source et chaque parole retrouvés à l'image près) ; vérifier à l'import chez l'utilisateur |
| Le générateur « Text » du format FCP7 n'est pas lu partout | XML | défaut : générateur sur fond noir seulement ; `--cartons png` pour tout voir |
| Taille et place exactes du texte | XML | à vérifier à l'œil après l'import |
| « Dip to White » et « Push » | XML | noms écrits à la manière de Premiere ; leur conversion n'est pas vérifiée |
| Une seule piste vidéo, pas de texte ni de niveau | EDL | préférer le XML |
| Pas de courbe de volume | toutes les sorties | respirations et sommets marqués par des marqueurs ; régler à l'oreille |
| Vitesse normale seulement | `montage.json` | aucun ralenti ni accéléré n'est écrit |
| Un noir final est un trou sur V1 | FilmCraft, XML, EDL | un export « séquence entière » s'arrête au dernier élément (vu dans FilmCraft) ; exporter de 0 à la durée du montage (`--rendre`, ou des points d'entrée et de sortie) |
| Noir et blanc, format large, étalonnage, recadrage en 9:16 ou 1:1 | toutes les sorties | signalés dans le plan de montage (le recadrage dans `journal`), faits dans le logiciel |
| Crédits d'une bande-annonce d'œuvre, chapitres titrés d'un documentaire, fiction narrée | `assemble.py` | à poser à la main |
| Raccord sur le mouvement, coupe cachée dans le sombre, sens des phrases, récit d'un sketch | `assemble.py` | le script ne les décide pas : notes « à vérifier à l'œil » dans `journal` |
