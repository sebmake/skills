# Format de `rushes.json` et de `montage.json`

Deux fichiers portent le montage :

- `rushes.json` décrit ce que l'utilisateur a tourné : ses rushes, sa musique s'il en a une, le nom ou le titre à écrire. C'est l'**entrée**.
- `montage.json` est la **timeline** : la liste des plans, dans l'ordre, avec leur source, leur entrée, leur sortie, leur transition et leur carton. C'est la **sortie** de `scripts/assemble.py` et l'entrée des trois sorties : `export_xml.py` (Premiere Pro, DaVinci Resolve), `export_edl.py` (CMX3600) et `filmcraft_build.py` (FilmCraft).

Règles de fond, portées par le format :

- **La grammaire, jamais la marque.** Aucun logo, aucune image ni aucun son d'une autre marque, aucune police d'Apple. Le logo est celui de l'utilisateur, ou rien ; la police est la sienne, sinon une police courante (Arial pour les titres de FilmCraft et du XML ; Inter, DejaVu Sans ou Arial pour les cartons en image).
- **Musique fournie ou aucune.** Un fichier local dont l'utilisateur a les droits, ou `null`. Jamais de musique cherchée ni générée.
- **Aucun texte inventé.** Le nom, la phrase, les répliques et les bandeaux viennent de l'utilisateur. Un texte absent reste absent ; `assemble.py` le signale dans `journal`.
- **Chemins.** Relatifs au dossier du fichier JSON, ou absolus. Les exports écrivent des chemins absolus.
- **Temps.** En secondes dans les champs `_s`, en images dans les champs `_img`. Dans `montage.json`, **les champs `_img` font foi** : les exports ne lisent qu'eux. Les champs `_s` sont là pour la lecture.

---

## 1. `rushes.json`

```json
{
  "version": 1,
  "projet": "TEST-theiere",
  "nom": "Fonte",
  "phrase": null,
  "logo": null,
  "police": { "famille": "Inter", "fichier": null },
  "couleurs": { "fond": "#000000", "texte": "#FFFFFF" },
  "musique": "musique.wav",
  "fps": null,
  "format": { "largeur": 1920, "hauteur": 1080 },
  "rushes": [
    {
      "id": "r10",
      "chemin": "r10.mp4",
      "description": "théière entière, la caméra recule",
      "valeur": "entier",
      "sujet": "objet",
      "mouvement": "lent",
      "direction": "recul",
      "role": ["revelation"],
      "note": 4,
      "prises": [[0.5, 11.5]],
      "meilleur_s": null
    }
  ]
}
```

### 1.1 Champs du projet

| Champ | Type | Sens |
|---|---|---|
| `projet` | texte | nom du projet ; sert de nom de séquence. En essai dans FilmCraft, il commence par `TEST-` |
| `nom` | texte ou `null` | le nom du produit ou le titre du film, tel qu'il s'écrit à l'écran |
| `phrase` | texte ou `null` | une phrase écrite (produit : 5 mots environ ; usage : 3 à 9 mots) |
| `these` | texte ou `null` | documentaire : une question ou une thèse d'ouverture (12 mots au plus) |
| `carton_ouverture` | texte ou `null` | ouverture, clôture : un carton de seuil (11 mots au plus) |
| `mots_chocs` | liste de textes | bande-annonce de catalogue : 2 ou 3 groupes de 1 ou 2 mots |
| `mention` | texte ou `null` | bande-annonce d'œuvre : une mention de 3 mots environ, très petite, sur noir, au début |
| `logo` | chemin ou `null` | le logo de l'utilisateur, s'il le fournit (image) |
| `police` | objet | `famille` (nom de la police installée) et `fichier` (chemin .ttf/.otf, pour les cartons en image) ; sans `famille`, les titres de FilmCraft et du XML prennent Arial |
| `couleurs` | objet | `fond` et `texte` des cartons, en `#RRGGBB` |
| `musique` | chemin ou `null` | la musique de l'utilisateur |
| `fps` | nombre ou `null` | images par seconde de la timeline ; `null` = celle de la majorité des rushes |
| `format` | objet | `largeur`, `hauteur` de la timeline ; 1920 × 1080 par défaut |

### 1.2 Ou la sortie d'`analyse_rushes.py`

`assemble.py` lit aussi directement le fichier écrit par `analyse_rushes.py` (blocs `fichiers` → `prises`). Chaque prise détectée devient un rush (`id` = nom du fichier + numéro de prise). Le mouvement mesuré devient `fixe` (< 10), `lent` (10 à 50), `moyen` (50 à 200) ou `fort` (200 et plus), les bornes de lecture du corpus. Les zones `a_eviter` sont retirées des fenêtres. Un moment `naissance_lumiere` donne le rôle `accroche` ; le plus fort `pic_mouvement` donne `meilleur_s`.

Une photo ou un scan (`.png`, `.jpg`, `.tif`…) trouvé par `analyse_rushes.py` devient une prise unique, fixe, sans mesure de mouvement ; sa planche est l'image elle-même. Un fichier que l'analyse ne lit pas (ou une photo ajoutée après coup) s'ajoute à la main dans une liste `rushes` à la racine du même fichier, avec les champs du § 1.3 (`id`, `chemin`, `valeur`, `sujet`…) : `assemble.py` monte alors ensemble les prises analysées et ces rushes, et le dit au `journal`. Une image fixe se monte toujours depuis sa première image ; sa durée est celle que le montage lui donne.

S'il y a un seul fichier son dans l'analyse, il devient la musique, et le `journal` le dit ; s'il y en a plusieurs, aucun n'est pris d'office : préciser `--musique`.

Les états de caméra (fixe, lente, rapide, à la main) et les zones à éviter (flou, tremblement) viennent de seuils de convention : sur un essai, un mur dont la lumière varie lentement a été lu « à la main », flou et tremblant. La planche tranche.

`analyse_rushes.py` n'écrit jamais par-dessus un fichier où des champs ont été remplis à l'œil : pour relancer l'analyse (un rush ajouté, un rush retourné), `--fusionner` reprend ces champs dans la nouvelle analyse, prise par prise (même fichier, début et fin à ± 0,1 s), avec ceux de la racine ; une prise annotée qui n'est plus retrouvée est gardée dans `annotations_non_retrouvees`, et `assemble.py` le signale.

`valeur` et `sujet` restent à remplir à l'œil dans ce fichier, prise par prise, en regardant la planche ; `note` (1 à 5) aussi, si une prise vaut mieux qu'une autre. `notes` est un commentaire libre, ajouté à la description du plan : il ne change pas la note. Sans eux, `assemble.py` choisit à l'aveugle et le dit dans `journal`. Les autres champs du § 1.3 (`role`, `personne`, `paroles`…) s'ajoutent de la même façon dans la prise. `nom`, `phrase`, `logo`, `police` s'ajoutent à la racine du fichier.

### 1.3 Champs d'un rush

| Champ | Valeurs | Sens |
|---|---|---|
| `id` | texte court | identifiant unique (sert de bobine dans l'EDL) |
| `chemin` | chemin | le fichier vidéo, audio ou image |
| `duree_s`, `fps` | nombre | lus par `ffprobe` s'ils manquent |
| `valeur` | `detail`, `serre`, `rapproche`, `moyen`, `entier`, `large`, `abstrait` | valeur de plan. Alias admis : `TG`, `tres_gros`→detail, `G`, `gros`→serre, `R`→rapproche, `M`→moyen, `L`, `ensemble`→large, et les codes 1, 2, 3, 4, A des analyses |
| `sujet` | `objet`, `piece`, `matiere`, `decor`, `lumiere`, `geste`, `ecran`, `personne`, `entretien`, `illustration`, `oeuvre`, `photo`, `archive` | ce que montre le plan. `objet` + `entier` = l'objet en entier ; `piece` = une pièce ou un composant de l'objet (une pièce d'habitation, c'est `decor`). Les accents et les majuscules sont admis (« Pièce », « œuvre ») ; un autre mot est signalé au `journal` et ne compte pour aucune règle |
| `mouvement` | `fixe`, `lent`, `moyen`, `fort` | mouvement de l'image (caméra et sujet mêlés) |
| `direction` | `avant`, `recul`, `rotation`, `lateral` | sens du mouvement de caméra, s'il y en a un |
| `role` | liste | rôle souhaité : `accroche`, `revelation`, `fin`, `gamme`, `pic`, `arrivee`, `bouton`, `signature` |
| `note` | 1 à 5 | qualité de la prise (3 par défaut) |
| `prises` | liste de `[début, fin]` en s | fenêtres utilisables dans le fichier ; par défaut tout le fichier moins 0,3 s à chaque bout (convention) |
| `meilleur_s` | nombre | l'instant à garder au centre du plan |
| `personne`, `fonction` | texte | documentaire : qui parle, et sa fonction (bandeau) |
| `paroles` | liste | entretien, réplique : `{"entree_s", "sortie_s", "texte", "ordre", "note", "chapitre"}` (`entree` et `sortie` admis) |
| `synchro` | objet | autre angle de la même prise : `{"avec": "e01", "decalage_s": 0.0}` |
| `bloc` | texte | bande-annonce : le sujet du bloc (concert, épisode…) |
| `titre_bloc` | texte | bande-annonce par blocs : le titre écrit en tête du bloc |
| `scene` | nombre | ouverture, sketch, usage : numéro de scène ; l'ordre des scènes est gardé |

---

## 2. `montage.json`

```json
{
  "version": 1,
  "titre": "TEST-theiere",
  "famille": "produit",
  "schema": "revelation_tardive",
  "duree_cible_s": 32.0,
  "duree_s": 32.0,
  "duree_img": 800,
  "format": { "largeur": 1920, "hauteur": 1080, "fps": 25, "tc_debut": "00:00:00:00" },
  "police": { "famille": "Inter", "fichier": null },
  "couleurs": { "fond": "#000000", "texte": "#FFFFFF" },
  "musique": { ... },
  "plans": [ { ... } ],
  "paroles": [ { ... } ],
  "marqueurs": [ { ... } ],
  "controle": [ { ... } ],
  "journal": [ "..." ]
}
```

| Champ | Sens |
|---|---|
| `famille` | `produit`, `ouverture`, `documentaire`, `bande_annonce` |
| `schema` | la forme retenue dans la famille (§ 2.6) |
| `duree_cible_s` | la durée demandée ; `duree_s` et `duree_img` la durée obtenue |
| `format.fps` | 23.976, 24, 25, 29.97, 30, 50, 59.94 ou 60. 23.976, 29.97 et 59.94 sont lus 24000/1001, 30000/1001, 60000/1001 |
| `format.tc_debut` | timecode de la première image de la timeline ; `00:00:00:00` par défaut, `01:00:00:00` pour qui monte dans Resolve à l'habitude |
| `controle` | les mesures du montage obtenu, chacune avec sa cible et son statut (§ 2.7) |
| `critique` | les arguments de `critique_montage.py` qui correspondent à ce montage : `famille`, `sous_famille`, `schema` |
| `journal` | ce qu'`assemble.py` a choisi, ce qui manque, ce qu'il faut vérifier à l'œil |

À côté de `montage.json`, `assemble.py` écrit `montage.annotations.json` : les annotations « à l'œil » de `critique_montage.py --annotations` (valeur et type de chaque plan, révélation, nom, fermeture, textes), tirées de ce que le montage sait déjà. Elles valent pour l'export brut ; après retouche dans le logiciel, les refaire à l'œil.

### 2.1 Un plan

Les plans se suivent sur la piste V1, sans trou : chaque plan commence où finit le précédent. Un noir est un plan.

```json
{
  "n": 3,
  "type": "image",
  "temps": "montee",
  "debut_img": 110, "duree_img": 55,
  "debut_s": 4.4, "duree_s": 2.2,
  "source": "r04",
  "chemin": "/chemin/absolu/r04.mp4",
  "entree_img": 60, "sortie_img": 115,
  "entree_s": 2.4, "sortie_s": 4.6,
  "transition": { "type": "coupe" },
  "carton": null,
  "valeur": "serre", "sujet": "piece", "mouvement": "moyen",
  "son_image": false,
  "notes": "montée : on serre sur les pièces (65 à 70 % de plans serrés, observé)"
}
```

| Champ | Sens |
|---|---|
| `n` | numéro d'ordre, de 1 à N |
| `type` | `image` (un rush), `noir` (rien à l'image), `carton` (un texte sur fond uni) |
| `temps` | le moment de la structure : `ouverture`, `accroche`, `montee`, `pic`, `revelation`, `nom`, `fin`, `seuil`, `premier_plan`, `corps`, `atterrissage`, `voix`, `respiration`, `annonce`, `bloc`, `fermeture`, `bouton`, `titre`… |
| `debut_img`, `duree_img` | place et durée sur la timeline, en images. `debut_img` du plan n+1 = `debut_img + duree_img` du plan n |
| `source`, `chemin` | le rush (`type: image`) |
| `entree_img`, `sortie_img` | entrée et sortie dans le fichier source, en images de la timeline. `sortie_img − entree_img = duree_img` (vitesse normale seulement) |
| `transition` | comment ce plan **commence** (§ 2.2) |
| `carton` | un texte posé sur ce plan (§ 2.3), ou `null` |
| `son_image` | `true` : garder le son du rush sous ce plan (piste A3) |
| `mouvement_mesure` | mouvement du passage monté (écart moyen de gris par seconde), lu dans la courbe d'`analyse_rushes.py` ; sous 10,5, le plan compte comme fixe dans `controle` : la critique compte fixe sous 10, sur sa propre mesure, proche de celle-ci sans lui être égale, d'où la marge. Absent pour un rush décrit à la main : l'étiquette `mouvement` sert alors |
| `personne` | la personne du rush, s'il y en a une (documentaire, clôture) |
| `sync` | `true` : plan d'entretien calé sur la parole qui passe dessous |
| `notes` | la règle appliquée, avec son compte ou « convention » |

Une source à une autre cadence que la timeline est lue à vitesse normale : ses entrées et sorties sont converties en images de la timeline.

### 2.2 La transition

La transition est portée par le plan qui **commence**. Elle se lit avec le plan d'avant.

| `type` | Plan d'avant | Effet | Dans les logiciels |
|---|---|---|---|
| `coupe` | tout | coupe franche | — |
| `fondu` | une image | fondu enchaîné, centré sur la coupe | Cross Dissolve ; il faut `duree/2` de marge dans les deux rushes |
| `fondu` | un noir, ou rien | l'image sort du noir, dans ses premières images | Cross Dissolve en tête (alignement `start-black`) |
| `fondu` | (ce plan est un noir) | l'image d'avant part au noir, dans ses dernières images | Cross Dissolve en queue (alignement `end-black`) |
| `blanc` | une image | passage par le blanc, centré | Dip to White |
| `poussee` | une image | le plan suivant pousse le premier, centré | Push |

`duree` est en secondes, `duree_img` en images. `assemble.py` vérifie la marge des rushes ; sans marge, il raccourcit le fondu ou le remplace par une coupe et le dit dans `journal`. Les trois sorties refont la vérification sur un `montage.json` retouché à la main : un fondu enchaîné de `d` images demande `d // 2` images avant l'entrée du plan qui arrive et le reste après la sortie du plan qui part ; sinon elles refusent le montage (code 1) et nomment le plan.

### 2.3 Le carton

```json
"carton": {
  "role": "nom",
  "texte": "Fonte",
  "debut_img": 0, "duree_img": 60,
  "place": "centre",
  "taille_pct": 4.5,
  "fond": "noir"
}
```

| Champ | Sens |
|---|---|
| `role` | `nom`, `titre`, `phrase`, `these`, `bandeau`, `titre_bloc`, `mot_choc`, `credit`, `mention`, `logo` |
| `texte` | le texte, ou `null` pour un logo (`logo` = chemin de l'image) |
| `debut_img`, `duree_img` | place **dans le plan** (0 = la première image du plan) et durée |
| `place` | `centre`, `bas_gauche`, `bas_droite`, `haut_gauche` |
| `taille_pct` | hauteur des capitales en % de la hauteur de l'image |
| `fond` | `image` (le texte est posé sur le plan), `noir`, `blanc` ou `#RRGGBB` (plan de type `carton`) |
| `deuxieme_ligne` | bandeau : la fonction, sous le nom |

Sur un plan `image`, le carton va sur la piste V2, au-dessus de l'image. Un plan `carton` est un texte sur fond uni : rien sur V1 (noir) ou une couleur unie, et le texte sur V2.

### 2.4 Les paroles

Les paroles sont des morceaux de son posés sur la piste A1 : entretiens, répliques, voix off. L'image qui passe dessus est choisie à part (voix sur illustration, visage ensuite).

```json
{
  "n": 1,
  "source": "e01",
  "chemin": "/chemin/absolu/e01.mp4",
  "debut_img": 143, "duree_img": 139,
  "entree_img": 288, "sortie_img": 427,
  "personne": "Ana",
  "texte": "On commence toujours par le papier.",
  "piste": "A1"
}
```

### 2.5 La musique et les marqueurs

```json
"musique": {
  "chemin": "/chemin/absolu/musique.wav",
  "debut_img": 0, "entree_img": 0, "duree_img": 800,
  "fondu_sortie_img": 25,
  "reperes": { "debut_son_s": 0.6, "sommet_s": 22.1, "attaques_s": [1.0, 8.0, 16.0, 24.5, 29.0] },
  "piste": "A2"
}
```

- Pistes : paroles en A1, musique en A2, son des images en A3. Toujours les mêmes.
- `reperes` : ce qu'`assemble.py` a mesuré dans la musique (méthode et seuils dans l'en-tête du script ; `assemble.py --musique F --reperes` les affiche seuls). Les grands changements y sont calés ; les coupes ordinaires, non (convention).
- `marqueurs` : `{"debut_img", "duree_img", "nom", "texte"}`. Chaque carton et chaque temps de la structure en reçoit un. Les trois sorties les écrivent.

### 2.6 Familles et schémas

| `famille` | `schema` | Pour quoi |
|---|---|---|
| `produit` | `revelation_tardive` | un objet nouveau : un monde ou une matière, des détails, l'objet entier vers 77 %, le nom |
| `produit` | `objet_des_le_debut` | un logiciel, un usage, une gamme : l'objet tout de suite, puis ses usages, puis le nom |
| `ouverture` | `ouverture` | film d'ouverture ou d'ambiance, sketch (l'ordre des scènes est gardé) |
| `ouverture` | `transition_decor` | passage d'un lieu à un autre, 15 à 30 s, sans texte |
| `ouverture` | `cloture` | film de clôture : carton, visages, dernier tiers plus rapide, plan-signature |
| `documentaire` | `pose` | peu de voix, longues prises, fin plus lente |
| `documentaire` | `choral` | beaucoup de voix brèves, fin plus rapide, rafale finale |
| `bande_annonce` | `catalogue_blocs` | plusieurs sujets, un bloc et un titre par sujet |
| `bande_annonce` | `catalogue_mele` | plusieurs sujets mêlés plan par plan, sans titres |
| `bande_annonce` | `oeuvre` | une seule histoire, avec des répliques |
| `bande_annonce` | `usage` | un objet utilisé par des gens |

Les cibles de chaque schéma sont dans `scripts/gabarits.json`, chacune avec son compte (N sur M) ou la mention « convention », et sa source dans `references/cibles/`. `python3 assemble.py --verifier-gabarits` compare les deux.

Noms admis aussi : familles `bandeannonce`, `produit_revelation`, `ouverture_ambiance`, `documentaire_temoignage` ; schémas `tardif`, `des_le_debut`, `catalogue_par_blocs`, `sketch` (= ouverture), `hommage` (= clôture). Ce sont les noms de `critique_montage.py`.

### 2.7 Le contrôle

`controle` est une liste de mesures faites sur la timeline obtenue :

```json
{ "id": "plan_median", "mesure": 2.2, "cible": [1.0, 3.6], "statut": "observe", "base": "14 films qui coupent : 1,0 à 3,6 s", "ok": true }
```

`ok` vaut `true`, `false`, ou `null` quand la mesure n'est qu'un repère (un seul film mesuré). Une mesure hors cible ne bloque rien : elle dit où le montage s'écarte des films mesurés, et `journal` dit pourquoi (souvent : pas assez de rushes du bon type). Les plans fixes se comptent avec une marge sur la critique (`mouvement_mesure` sous 10,5, quand la critique compte sous 10 sur sa propre mesure, proche mais pas identique) : `part_plans_fixes` (produit, bande-annonce, au plus 25 %) et `plans_fixes` (transition entre deux lieux, aucun) sortent en écart là où la critique lèverait une alerte. Sans plan de l'objet entier, une révélation tardive n'a pas de plan : `revelation_objet_entier` sort en écart, et rien n'est annoncé comme révélation à la critique.

Le `journal` dit aussi chaque repli : une exigence levée faute de rush qui la remplisse, des images déjà montées rejouées faute de place libre ailleurs, un noir posé « faute d'images ».

---

## 3. Ce que les sorties savent faire

| Élément | XML FCP7 (Premiere, Resolve) | EDL CMX3600 | FilmCraft |
|---|---|---|---|
| plans image, entrées, sorties | oui | oui (une piste vidéo) | oui |
| noirs | trous sur V1 | événements `BL` | trous sur V1 |
| fondus, passage au blanc, poussée | oui | fondus et blanc : dissolve `D` ; poussée : coupe + commentaire | oui |
| cartons sur fond noir | générateur « Text » sur V2 + marqueur | commentaire `* CARTON` | titre natif, modifiable |
| textes posés sur une image (bandeau, titre dans le décor), fonds de couleur | marqueur seulement (`--cartons texte`, défaut), ou image PNG sur V2 (`--cartons png`, demande Pillow) | commentaire `* CARTON` | titre natif ; fond de couleur en cache couleur sur V1 |
| paroles, musique | A1, A2 | événements `A`, `A2` | A1, A2 |
| marqueurs | oui | commentaires | oui |

Pourquoi le texte posé sur une image n'est pas un générateur par défaut : l'importeur de FilmCraft ne lit pas le générateur « Text » du format FCP7 et le remplace par de la vidéo noire, qui cachait le visage sous le bandeau (vu au test). Sur un fond noir, cela ne se voit pas ; sur une image, si. `--cartons generateurs` le force partout, à ses risques.

Premiere Pro et DaVinci Resolve ne sont pas installés sur la machine où la skill a été écrite : le XML et l'EDL y sont vérifiés par relecture (`--verifier`), par la lecture indépendante de `lire_timeline.py`, et par import dans FilmCraft (qui lit les deux formats et a reconstruit chaque plan à l'image près), pas dans ces deux logiciels.

## 4. FilmCraft

`filmcraft_build.py montage.json` construit la séquence par le canal de contrôle (`fc.py`), puis la relit par `sequence.inspect`. Commandes employées, toutes passées par `engine.execute` :

| Étape | Commande | Paramètres utiles |
|---|---|---|
| projet | `file.newProject` (défaut) ou `project.inspect` (`--projet ouvert`) | `name` |
| chutier, import | `file.newBin`, `file.import` | `name` ; `paths`, `bin` |
| séquence | `file.newSequence`, `sequence.open` | `name`, `width`, `height`, `fps`, `video: 3`, `audio: 3` |
| plans, paroles, musique | `timeline.place` | `item`, `track` (`V1`, `V2`, `A1`, `A2`, `A3`), `time`, `sourceIn`, `duration` en ticks, `insert: false`, `video`, `audio` |
| fond de couleur | `file.newColorMatte` puis `timeline.place` | `color`, `seconds` |
| cartons | `graphics.newText`, `graphics.set`, `graphics.align` | `text`, `size`, `font`, `seconds`, `track: 1` (= V2), `time` ; `props.align`, `props.position`, `props.fill_color` |
| niveau de la musique | `effects.setParam` | `clip`, `effect: 0` (volume), `param: "level"`, `value` en dB |
| transitions | `sequence.applyVideoTransition`, `sequence.applyAudioTransition` | `clip`, `effect` (`cross_dissolve`, `dip_to_white`, `push`, `constant_power`), `frames`, `edge` (`in`, `out`) : FilmCraft aligne seul (centré entre deux plans, au début après un trou, à la fin avant un trou) |
| marqueurs | `markers.add` | `target: "program"`, `time`, `name`, `comment`, `durationFrames` |
| vérification | `sequence.inspect` | `item` |
| images de contrôle | `file.exportFrame` | `path`, `format: "png"`, `target: "program"`, `time`, `sequence` |
| vidéo (`--rendre`) | `file.exportMedia` | `path`, `format: "h264"`, `sequence`, `range: "custom"`, `startSeconds: 0`, `endSeconds` = durée du montage, `wait: true` |
| enregistrement (sur demande) | `file.saveAs` | vers un chemin qui n'existe pas encore, jamais par-dessus |

Temps en ticks : 254 016 000 000 par seconde. `--simulation` imprime la liste des commandes, paramètres abrégés, sans rien envoyer ; `--rapport` en garde les paramètres complets.
