# Lire un rapport de critique, et corriger

Ce fichier dit comment lancer `scripts/critique_montage.py`, lire son rapport, compléter ce que le calcul ne voit pas, et passer d'une alerte à un geste de montage. Les règles citées (G, P, A, T, BA, U) sont dans `grammaire-montage.md` ; les seuils, dans `cibles/<famille>.json`.

## Sommaire

1. Deux usages, une seule mesure
2. Ce qu'il faut donner à la critique
3. La marche en trois passes
4. Lire le rapport
5. Écrire les annotations
6. Du contrôle à la règle et au geste
7. Corriger : dans quel ordre, et où
8. Ce que la critique ne voit pas
9. Rendre la critique à l'utilisateur

---

## 1. Deux usages, une seule mesure

- **Critiquer le montage de l'utilisateur** : il apporte une vidéo rendue, ou la timeline exportée de son logiciel (XML FCP7, EDL). La critique le mesure contre les films de sa famille.
- **Contrôler ce que la skill a construit** : après `assemble.py` et l'export, la même critique mesure le résultat. C'est la même mesure dans les deux cas : un montage de la skill n'a pas de passe-droit.

La critique lit les vidéos comme le corpus a été lu : 29,97 images par seconde, image réduite, mêmes seuils de coupe, de fondu et de noir. Sur un film du corpus (33,4 s), elle retrouve les 12 plans du découpage, aux mêmes durées.

**Ce que vaut un verdict.** La critique a été lancée sur 46 films du corpus eux-mêmes : 42 sortent « conformes » ; les 4 autres s'écartent à cause de leurs bornes ou d'un manque du découpage. Elle ne crie donc pas au loup sur les films qui ont servi aux cibles. Elle ne prouve pas qu'elle trouve toutes les fautes d'un montage.

---

## 2. Ce qu'il faut donner à la critique

| Entrée | Ce qu'elle apporte | Ce qui manque |
|---|---|---|
| **Vidéo rendue** (toute extension que lit ffmpeg) | plans, coupes, noirs, fondus au noir, mouvement, couleur, noir et blanc, bandes noires, cartons probables, son de la piste | les fondus enchaînés ne sont que des **candidats** ; les textes posés sur une image ne sont pas vus |
| **XML FCP7** (« xmeml », export de Premiere Pro, de DaVinci Resolve ou de FilmCraft) | plans, transitions et textes **déclarés** | mouvement et couleur : seulement avec `--mesurer-medias`, si les fichiers sources sont sur la machine |
| **EDL CMX3600** | plans, fondus, noirs | une seule piste vidéo ; aucun texte (un carton y est lu comme un noir) ; sa cadence (`--fps`) |

Le format FCPXML (Final Cut Pro récent) n'est pas lu : il faut un XML FCP7.

Et, selon la famille :

- `--famille` : `produit`, `ouverture`, `documentaire`, `bandeannonce` (alias admis : `bande_annonce`, `usage`, `produit_revelation`…).
- `--sous-famille` : produit `revelation_objet` (défaut), `logiciel`, `materiaux_voix_off`, `usage_gamme` ; ouverture `ouverture` (défaut), `sketch`, `cloture`, `hommage`, `transition_decor`, `clip` ; documentaire `pose` ou `choral` (défaut : déduit du plan médian) ; bande-annonce `oeuvre`, `catalogue_par_blocs`, `catalogue_mele` (défaut), `usage`.
- `--schema` (produit) : `tardif` ou `des_le_debut`.
- `--sous-titres F.srt|F.vtt` : la parole. Sans eux, les contrôles de parole sont « non mesurés ». Documentaire, bande-annonce, sketch : à demander.
- `--son FICHIER [--son-debut S]` : le son à mesurer si la source n'en a pas (une timeline). Sans son, les contrôles de musique sont « non mesurés ».
- `--debut S --fin S` : les bornes du film dans une vidéo plus longue.

---

## 3. La marche en trois passes

Les scripts d'analyse demandent numpy et Pillow (environnement de `SKILL.md`, appelé ici `$PY`).

**Passe 1 : mesurer, et sortir une planche.**

```bash
$PY "$SKILL/scripts/critique_montage.py" film.mp4 --famille produit \
    --planche critique-planche.jpg --sortie critique.md --json critique.json
```

**Passe 2 : regarder.** Lis la planche (une vignette par plan, et 5 vignettes autour de chaque fondu candidat), puis la section « À vérifier à l'œil » du rapport. Écris les annotations (§ 5) : la valeur de chaque plan, la révélation, le nom, les textes, la décision sur chaque fondu candidat.

**Passe 3 : relancer avec les annotations.**

```bash
$PY "$SKILL/scripts/critique_montage.py" film.mp4 --famille produit \
    --annotations annotations.json --sortie critique.md --json critique.json
```

Le rapport final ne doit plus avoir de « à vérifier » importants. Code de sortie : 0 conforme, 1 s'écarte, 2 erreur.

**Pour un montage construit par la skill**, `assemble.py` écrit déjà `montage.annotations.json` (valeurs, révélation, nom, textes : ce que le montage sait) et imprime la commande exacte. Elle vaut pour l'export brut :

```bash
$PY "$SKILL/scripts/critique_montage.py" montage.xml --famille produit --sous-famille revelation_objet \
    --schema tardif --annotations montage.annotations.json --mesurer-medias \
    [--son musique.wav] [--sous-titres paroles.srt] --sortie critique.md --json critique.json
```

- `--mesurer-medias` : sans lui, le mouvement, les images fixes et le noir et blanc restent « non mesurés » (contrôle MV).
- `--son` : la musique de l'utilisateur, si elle commence à la première image de la timeline (sinon `--son-debut`).
- `--sous-titres` : si les paroles de `montage.json` ont leur texte, écris un `.srt` à partir du bloc `paroles` (début = `debut_img`, fin = `debut_img + duree_img`, à la cadence du montage). Sans texte, écris « parole » : les durées suffisent à tous les contrôles, sauf le compte de mots des répliques (B11).
- Après une retouche dans le logiciel, les annotations de `assemble.py` ne valent plus : exporte de nouveau la timeline et refais-les à l'œil.

---

## 4. Lire le rapport

### 4.1 Sa forme

1. Le titre, puis une ligne : famille, contexte (sous-famille, schéma ou régime), source (vidéo, XML, EDL), **verdict** (« conforme » = aucune alerte ; sinon « s'écarte (N alertes) »).
2. La ligne « Mesuré » : durée, plans d'image, noirs, cartons, plan médian (p10, p90), plans par minute, part de coupes franches, noir d'ouverture.
3. Les comptes : qui collent, alertes, notes, à vérifier, non mesurés.
4. Les sections, dans cet ordre : **Ce qui s'écarte**, **Notes**, **À vérifier à l'œil**, **Ce qui colle**, **Non mesuré**, **Sans objet**. Chaque contrôle donne son identifiant, la mesure, la cible, la base du corpus (N sur M), la source, et souvent un **correctif avec timecode** (`HH:MM:SS:FF` à la cadence du montage, plus les secondes).
5. La « Timeline mesurée » : n°, entrée, durée, quoi (image, noir, carton, uni), transition d'entrée (« candidat » si fondu trouvé au calcul), mouvement, annotation.

### 4.2 Les niveaux

| Niveau | Ce qu'il veut dire | Que faire |
|---|---|---|
| **alerte** | aucun film du corpus ne fait cela (règle vue N sur N, ou valeur hors de la plage observée) | corriger, ou dire pourquoi c'est voulu |
| **note** | possible, mais seule une minorité du corpus le fait, ou seuil de convention | le dire ; corriger si c'est un défaut et pas un choix |
| **à vérifier** | la mesure dépend d'un calcul incertain ou d'une annotation absente | regarder, puis annoter (§ 5) |
| **non mesuré** | il manque une source (sous-titres, son, annotations, fichiers sources) ; le rapport dit laquelle | la fournir, ou le dire à l'utilisateur |
| **sans objet** | le contrôle ne s'applique pas (plan-séquence, nom dit par un orateur…) | rien |

Une alerte n'est pas une faute de goût : c'est un écart à ce que font tous les films mesurés. Un choix voulu (un film de révélation volontairement en noir et blanc) se garde, et se dit.

### 4.3 Les sources, de la plus sûre à la moins sûre

| Source | D'où | Confiance |
|---|---|---|
| œil | annotations écrites après avoir regardé | l'emporte toujours sur le calcul |
| déclaré | transitions, noirs et textes écrits dans le XML ou l'EDL | sûre, sauf les textes d'une EDL (absents) |
| sous-titres | parole | bornes hautes : un sous-titre déborde souvent la voix |
| son | niveau, attaques, tempo | voix et musique mêlées |
| calcul | découpage de la vidéo | plans et noirs presque sûrs (sur des images très unies, une coupe peut encore manquer : la planche le montre) ; fondus enchaînés et cartons à confirmer |

Dans le corpus, le calcul a proposé 225 fondus candidats (enchaînés, au noir ou au blanc) pour 54 vrais : un fondu trouvé au calcul reste « à vérifier » tant qu'une annotation ne le confirme pas. Le contrôle **V1** liste les plans dont l'image du début et celle de la fin n'ont plus rien en commun : un fondu ou un volet a pu y être manqué.

---

## 5. Écrire les annotations

Un fichier JSON, toutes les clés facultatives. Exemple pour un film d'une théière en fonte :

```json
{
  "sous_famille": "revelation_objet",
  "schema": "tardif",
  "revelation": 24.5,
  "nom": [30.0, 32.4],
  "codes": "N1211222213",
  "plans": {"7": {"valeur": "serre", "type": "objet"}},
  "plans_par_temps": [{"t": 12.3, "valeur": "detail", "type": "objet", "objet": true, "visage": false}],
  "textes": [{"type": "nom", "debut": 30.0, "fin": 32.4, "mots": 1, "place": "centre", "boite": false}],
  "transitions": {"18.52": "F"},
  "ajouts": [{"t": 6.75, "type": "fondu_enchaine"}]
}
```

| Clé | Ce qu'elle dit |
|---|---|
| `revelation` | début, en s, du plan qui montre l'objet entier pour la première fois |
| `nom` | `[début, fin]` du nom écrit, ou `{"type": "dit_par_orateur"}` |
| `fermeture` | bande-annonce : début de la fermeture (s) |
| `ouverture_a_froid`, `fiction_narree` | ouverture : `true` si c'est voulu (le contrôle d'entrée et la part de parole s'adaptent) |
| `codes` | une valeur par plan, dans l'ordre du rapport : produit `1` détail, `2` serré, `3` entier, `4` large, `A` abstrait, `N` noir, `T` texte ; documentaire `D TG G R M L` ; bande-annonce `S R M L T N A X` ; ouverture `S M E L T N` |
| `plans` | par numéro de plan du rapport : `valeur` et `type` |
| `plans_par_temps` | le plan qui contient l'instant `t` : `valeur`, `type`, `personne`, `objet`, `visage`. Plus sûr que les numéros quand le découpage change d'une passe à l'autre |
| `textes` | chaque texte vu : `type` (`nom`, `phrase`, `question`, `these`, `chiffre`, `explicatif`, `slogan`, `date`, `logo`, `titre_bloc`, `bandeau`, `mot`, `carton`), `debut`, `fin`, `mots`, `place` (`centre`, `visage`, `fin_de_bloc`), `boite` |
| `transitions` | décision sur un fondu candidat (à ± 0,35 s du passage) : `T` vrai, `F` faux, `C` une coupe, `U` douteux, `B` passage au blanc |
| `ajouts` | une transition vue à l'œil que le calcul n'a pas trouvée : `fondu_enchaine`, `volet`, `fondu_au_noir`… |

Valeurs admises : `detail`, `tres_gros`, `gros`, `serre`, `rapproche`, `moyen`, `ensemble`, `entier`, `large`, `abstrait`, `noir`, `texte`. Types : `image`, `entretien`, `personne`, `illustration`, `objet`, `carton`, `titre`, `nom`, `logo`, `noir`.

Dès que `textes` est donné, seuls ces textes comptent pour le nom et le texte en trop (K6, K11, K12, K13) : un carton non typé n'est plus pris pour le nom.

---

## 6. Du contrôle à la règle et au geste

Les identifiants du rapport ne sont pas ceux des règles. Ces tables font le pont : pour chaque contrôle, la règle de `grammaire-montage.md` qui l'explique, et le geste qui corrige une alerte ou une note.

### 6.1 Produit et révélation (C, K)

| Contrôle | Règle | Geste qui corrige |
|---|---|---|
| C2 durée | P2 | raccourcir la montée ; au-delà de 60 s sans voix, découper en chapitres d'une idée |
| C3 ouvrir sur le noir | P3 | ajouter 0,5 à 1,5 s de noir ; faire sortir la première image du noir par un fondu de 0,7 à 1,3 s |
| C4 durée du premier plan | P4, § 4.2 | allonger le premier plan vers 3 s (2,3 à 7,9 s) |
| K1 place de la révélation | P11 | déplacer le premier plan de l'objet entier entre 69 et 82 % ; retirer les plans entiers qui le précèdent |
| K2 premier plan entier | P4 | ouvrir sur un décor, une matière ou un détail |
| K3 plan médian, K4 plans par minute | P6, P9 | raccourcir (ou allonger) les plans de la montée vers 2 s ; un logiciel peut couper plus vite |
| K5 un plan d'au moins 5 s | P13 | tenir la révélation ou le dernier plan |
| K6 dernier plan tenu | P12 | tenir le dernier plan d'image 6 à 8,5 s, ou finir sur le carton du nom |
| K7 fondus enchaînés | G2, P7 | remplacer par des coupes ; en garder un au plus, sur un plan clé |
| K8 fondu depuis le noir au dernier tiers | P7 | couper franc |
| K9 détails et plans serrés | P5 | remplacer des plans larges de la montée par des détails et des pièces |
| K10 dernier plan entier | P12 | finir sur l'objet entier, seul |
| K11 place et durée du nom | P15 | poser le nom entre 83 et 96 % de la durée, 1,3 à 4,5 s |
| C16 écrire le nom | P16 | ajouter le carton du nom (texte fourni par l'utilisateur) |
| K12 texte en trop | P19, G6 | retirer les cartons explicatifs ou chiffrés ; un seul texte à la fois |
| K13 logo, date ou slogan en fin | P18 | finir sur l'objet, ou le nom puis un noir |
| K14 noirs internes | P14 | retirer les noirs du milieu, ou les ramener à 0,3 à 0,9 s |
| K15 images fixes | P10, G4 | remplacer des plans fixes par des plans en mouvement lent |
| K16 voix off | P20 | laisser 4 s muettes au début, 2 à 3,5 s à la fin ; la voix sur deux tiers du temps au plus |
| K18 film sans voix de plus de 60 s | P2, P23 | raccourcir, ou des chapitres |
| K19 noir et blanc | § 9.3 | rendre la couleur (le produit n'est jamais désaturé : 0 sur 16) |
| K20 coupes calées sur chaque temps | G8, P22 | décaler les coupes ordinaires ; ne caler que la sortie du noir, la révélation et le nom |

### 6.2 Documentaire et témoignage (D)

| Contrôle | Règle | Geste qui corrige |
|---|---|---|
| D1 plan médian, D2 coupes par minute | § 6.1, T11 | posé : plans vers 2 s ; choral : vers 1,2 s. Vérifier d'abord le régime (`--sous-famille`) |
| D3 forme du rythme | T11 | posé : ralentir la fin, plans les plus longs à la fin ; choral : accélérer la fin |
| D4 plan d'au moins 5 s au dernier cinquième | T14 | tenir un plan large à la fin |
| D5 transitions autres que la coupe, noirs de chapitre | T10 | couper franc ; un seul noir (0,4 à 1 s) pour changer de chapitre |
| D5b fondu entre deux plans de personne, D5c fondus enchaînés | G2, T10 | remplacer par une coupe |
| D6 part de parole | T3 | trop : laisser des silences et une respiration ; trop peu : resserrer les prises |
| D7 respirations | T3 | ajouter 3 à 9 s de musique seule sur des images, environ une par minute et demie |
| D8 parole sur le visage | T4 | couvrir les deux tiers de la voix par des illustrations |
| D9 entrée par la voix | T5 | faire entendre la première personne sur une illustration, visage 1,5 à 4,7 s après |
| D10 entretien long avant la fin | T12 | couper l'entretien, couvrir par une illustration ; garder les plans de plus de 5 s pour la fin |
| D11 entretien en plan large | T7 | prendre une valeur plus serrée |
| D12 même personne deux fois | T7 | le second plan plus serré, ou une illustration entre les deux |
| D13 caméra sur l'entretien | T8 | choisir une prise fixe |
| D15 bandeaux | T6 | en bas, côté vide, petit, sans boîte, 2 à 3,5 s, au premier visage |
| D16 cartons-message | T17 | au plus 3, petits, centrés, 12 mots au plus, sans boîte |
| D17 première parole, D17b noir d'ouverture, D17c son calme | T13 | ouvrir par le noir et le calme ; première parole entre 3 et 17 s |
| D18 dernière parole, D18b plan tenu à la fin | T14 | finir la parole 1 à 10 s avant la fin ; tenir le dernier plan 5,7 à 8,1 s |
| D19 rafale finale de visages | T14 | mettre les œuvres ou le produit dans la rafale finale, pas les visages |
| D20 son entre les phrases | § 8 | laisser la musique ou le son du lieu sous les silences de parole |
| D21 noir et blanc | T18 | tout le film, ou les personnes en noir et blanc et les écrans en couleur |

### 6.3 Bande-annonce et usage (B)

| Contrôle | Règle | Geste qui corrige |
|---|---|---|
| B1 plan médian | BA2 | resserrer vers 0,9 s |
| B2 dernier tiers plus rapide | BA2 | raccourcir les plans jusqu'au pic |
| B3 place du pic, B4 plans du pic | BA3 | monter 10 s de plans à 0,6 s vers 80 % de la durée |
| B5 fermeture | BA10 | fermeture de 6 à 17 % de la durée : noir, bouton, noir, titre |
| B6 dernier élément | BA10 | finir sur le titre ou le logo, 2,5 à 4,8 s, sorti du noir |
| B7 coupes franches, B8 fondus enchaînés | BA4 | remplacer les effets par des coupes ; garder le fondu pour un titre qui laisse place à l'image |
| B9 plans larges au premier tiers | BA6 | ouvrir sur des plans larges (35 % au moins) |
| B10 plans fixes | BA15 | des plans qui bougent, de plus en plus |
| B11 répliques longues | BA7 | couper les répliques à 3 s et 10 mots |
| B12 parole au pic | BA3 | faire taire le pic ; la musique porte |
| B13 ouverture dans le noir | G3, § 7.1 | ajouter un noir de 0,6 s environ |
| B14 titres de bloc | BA11 | le titre en tête du bloc, environ 1 s |
| B15 texte dans un film d'usage | U3 | déplacer le texte dans les 10 derniers % |
| B16 objet à l'image | U2 | l'objet un plan sur trois ou sur quatre |
| B17 coupes sur les temps | G8 | permis au pic seulement ; ailleurs, couper sur la parole et l'action |

### 6.4 Ouverture et ambiance (O)

| Contrôle | Règle | Geste qui corrige |
|---|---|---|
| O0 durée | § 9.1 | 60 à 120 s (convention ; observé 65 à 143 s) |
| O1 entrée, O1b seuil | A1, A2 | un seuil de noir et de silence, puis un premier plan de 5 à 10 s (sauf ouverture à froid voulue : l'annoter) |
| O2 plan médian du corps, O3 rythme du corps | A3 | corps vers 1,3 à 1,5 s, sans ralentir avant l'atterrissage |
| O4 pic de vitesse | A5 | 5 plans de 0,4 à 0,7 s entre 60 et 80 % |
| O5 atterrissage | A6 | 3 à 5 plans qui s'allongent, puis un dernier plan de 5 à 11 s |
| O6 fin serrée | A7 | finir large, sur le lieu ou la personne |
| O7 fondus enchaînés | A8 | des coupes ; un fondu seulement de l'animation au réel |
| O8 noir au milieu | A9 | garder le noir pour l'entrée |
| O9 texte au milieu ou plus de 2, O10 carton trop court | A10, G7 | texte au seuil ou à la fin ; environ 0,5 s par mot |
| O11 coupes sur les temps | G8 | caler le pic, l'atterrissage et le noir final sur la musique, pas chaque coupe |
| O12 sommet du son | A5, § 8 | faire monter la musique jusqu'après 60 % |
| O13 fin sans parole, O13b part de parole | A11 | finir sur 15 à 30 s sans parole ; 30 % de parole au plus |
| O15 bandeaux | § 5.4 | nommer après le premier tiers |
| O16a durée, O16 plans fixes, O17 arrivée tenue | § 5.5 | 15 à 30 s, mouvement continu, arrivée tenue 7 à 11,5 s |

### 6.5 Communs

| Contrôle | Geste |
|---|---|
| V1 transitions possiblement manquées | regarder ces plans ; écrire le fondu ou le volet dans `ajouts`, ou rien |
| MV mouvement non mesuré | relancer avec `--mesurer-medias`, ou critiquer la vidéo rendue ; « timecode source hors du fichier » : la timeline pointe sur d'autres fichiers que ceux montés |

---

## 7. Corriger : dans quel ordre, et où

**L'ordre.** Corrige d'abord ce qui porte le film, puis le rythme, puis les détails :

1. **la forme** : famille et schéma justes, place de la révélation, du pic, du nom ou du titre, la fin (K1, K2, K6, K11, B3, B5, B6, O5, D18…) ;
2. **le rythme** : plan médian, cadence, forme du rythme, plan long (K3, K4, K5, D1 à D4, B1, B2, O2, O3…) ;
3. **les transitions et les noirs** (K7, K8, K14, D5, B7, B8, O7, O8…) ;
4. **le texte et le son** (K12, K13, D15, D16, B11, B12, O9, O13…).

Une correction de forme déplace souvent tout le reste : relance la critique après chaque étape plutôt qu'à la fin.

**Où corriger.**

- **Un montage de la skill** : corrige l'entrée et reconstruis. Dans `rushes.json`, change `role` (par exemple `revelation`, `fin`, `pic`), `note`, `prises` ou `meilleur_s` ; ou relance `assemble.py` avec un autre `--schema` ou une autre `--duree`. Édite `montage.json` à la main seulement pour un réglage fin, en gardant les `_img` cohérents (chaque plan commence où finit le précédent ; `sortie_img − entree_img = duree_img`) : les exports refusent un montage incohérent, ou un plan qui sort de son rush (code 1). Puis exporte de nouveau avec `--verifier`.
- **Le montage de l'utilisateur** : donne les correctifs dans ses mots de monteur, avec le timecode du rapport : « allonge le plan 14 (00:00:24:12) jusqu'à 7 s », « remplace le fondu à 00:00:18:13 par une coupe », « déplace le nom à 00:00:30:00 ». Il les fait dans son logiciel, exporte, et la critique repasse.

**Ce qu'on ne fait jamais pour faire passer un contrôle** : inventer un texte, un nom, un chiffre ou un témoignage ; ajouter une musique ; étirer un plan au ralenti pour atteindre une durée ; mettre un logo qui n'est pas le sien. S'il manque un rush (pas d'objet entier filmé, pas de plan large), le dire : c'est un plan à tourner, pas un défaut à cacher.

---

## 8. Ce que la critique ne voit pas

- **Les fondus enchaînés** : borne basse, candidats seulement au calcul ; les volets ne se calculent pas (déclarés ou annotés). Sur un test, 3 fondus entre des plans de 0,5 s n'ont pas été trouvés sur la vidéo seule.
- **Les cartons** : trouvés par une heuristique (fond uni, traits fins). Un écran blanc peut passer pour un carton ; un texte posé sur une image n'est pas vu. Un petit texte clair sur noir peut être lu comme un noir, et un trait de lumière sur noir comme un carton : en passe 1, C4, C16 et O1 sont à confirmer sur la planche. Toujours à confirmer.
- **Les valeurs de plan, le sujet, la révélation** : seulement à l'œil. L'objet entier n'est cherché qu'au premier plan (K2) et au temps de la révélation annoté (K1) : un plan large où il paraît en entier, même en petit, avant sa révélation n'est vu que par l'œil (sur un essai, la lampe entière à 21 % de la durée, révélée à 76 %, n'a levé aucune alerte).
- **La place de la révélation (K1)** a une tolérance de convention autour des 69 à 82 % du corpus : sous 60 %, alerte ; de 60 à 66 %, note ; de 66 à 87 %, aucune remarque ; au-delà de 87 %, note.
- **Le noir d'ouverture d'une vidéo** : un premier plan très sombre (un trait de lumière qui sort du noir) allonge le noir lu (1,8 s lues pour 1,1 s posées sur un essai, C3) ; la planche le montre.
- **La parole** : seulement par les sous-titres ; le son ne sépare pas voix et musique.
- **Une piste son muette** (un rendu sans musique en porte souvent une) : lue comme une absence de son ; les contrôles du son restent « non mesurés ».
- **La caméra** : seulement ses glissements. Un zoom ou une rotation sortent « fixes », sur une vidéo comme sur un XML dont les rushes sont mesurés.
- **Ce qui ne se compte pas** : un raccord sur le mouvement réussi, le sens d'une phrase, le récit d'un sketch, l'émotion d'un visage, la justesse d'une musique. Regarde le film en entier avant de rendre la critique.

---

## 9. Rendre la critique à l'utilisateur

Ne colle pas le rapport brut. Donne, en phrases simples :

1. **le verdict** en une ligne : conforme, ou s'écarte, avec le nombre d'alertes ;
2. **les 3 à 5 écarts qui comptent**, dans l'ordre du § 7 : ce qui est mesuré, ce que font les films de la famille (avec le compte N sur M), le geste et son timecode ;
3. **ce qui colle**, en une ligne ;
4. **ce qui reste à vérifier ou n'a pas été mesuré**, et ce qu'il faudrait fournir (sous-titres, son, fichiers sources) ;
5. le chemin du rapport complet (`critique.md`) et de la planche.

Une note n'est pas une faute : dis « possible, mais rare » et laisse le choix. Ne cite jamais un film du corpus par son titre ou sa marque : dis « les films de révélation d'objet », « les bandes-annonces de catalogue ».
