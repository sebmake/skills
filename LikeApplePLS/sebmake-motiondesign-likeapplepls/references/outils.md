# Exécuter le script : After Effects et EffectCraft

Le moteur écrit un seul script, `motion.jsx`, en ExtendScript (le JavaScript des scripts After Effects). Il n'utilise que l'API objet d'After Effects, que EffectCraft reprend. Le même fichier tourne dans les deux outils.

```bash
SKILL="<dossier de ce SKILL.md>"   # souvent ~/.claude/skills/sebmake-motiondesign-likeapplepls
```

**Prérequis.** Node (pour `build_motion.mjs` ; testé avec Node 26), Python 3.9 ou plus (pour `check_motion.py` et `ec.py`, sans dépendance), ffmpeg et ffprobe (images de contrôle, vérification d'un rendu). S'il en manque un, dis-le et n'installe rien sans accord.

---

## 1. La chaîne

```bash
python3 "$SKILL/scripts/check_motion.py" motion.json      # 0 erreur avant d'aller plus loin
node "$SKILL/scripts/build_motion.mjs" motion.json        # écrit motion.jsx à côté, puis vérifie l'ES3
```

`build_motion.mjs` s'arrête avec le code 2 si le script produit contient un écart ES3 (`let`, `const`, `=>`, gabarit, `JSON`, méthode ES5…). Cela ne doit pas arriver : c'est un défaut du moteur, à signaler, pas à contourner.

Options utiles :
- `--prefixe TEST-` : même script, composition nommée `TEST-<nom>`. Pour les essais : la vraie composition n'est pas touchée.
- `--relatif` : n'écrit pas de chemins absolus vers les images. Pour donner le script à quelqu'un d'autre, avec ses images à côté.
- `--plan` : imprime le plan temporel (ce que lit le contrôle).

---

## 2. Dans After Effects

After Effects n'a pas servi aux essais de la skill (il n'était pas installé). Le script n'emploie que l'API commune et a été exécuté dans EffectCraft. Dis-le à l'utilisateur à la livraison.

**L'utilisateur lance le script lui-même.**

1. Mettre `motion.jsx` et ses images dans un même dossier (le script cherche d'abord chaque image à côté de lui, puis à son chemin absolu). Pour un autre poste : régénérer avec `--relatif`, puis copier le dossier entier.
2. Ouvrir un projet (neuf ou existant). Le script ajoute une composition ; il n'enregistre, n'ouvre ni ne ferme rien. Il remplace seulement une composition du même nom, et retire avec elle les solides qu'elle seule utilisait (sinon chaque relance laisserait un solide orphelin dans le projet).
3. Menu **Fichier > Scripts > Exécuter le fichier de script…** (en anglais : *File > Scripts > Run Script File…*), puis choisir `motion.jsx`.
4. Le script n'ouvre aucune boîte de dialogue : il construit la composition et s'arrête. Son rapport (calques, clés, replis) n'est affiché que dans EffectCraft. Dans After Effects, un repli (image manquante remplacée par un cadre neutre) se reconnaît à son nom de calque, `[REPLI] …`. Tout le script tient dans une seule annulation : **Édition > Annuler** retire la composition construite.
5. Rendu : **Composition > Ajouter à la file d'attente de rendu**, ou à Adobe Media Encoder. H.264, à la cadence de la composition.

**Ce qu'il faut savoir.**
- **Polices** : noms PostScript (`Inter-SemiBold`, pas « Inter SemiBold »). After Effects 24 et plus prend la première police installée de la liste du thème ; les versions plus anciennes prennent la première de la liste, installée ou non. Mets en tête une police installée sur le poste de l'utilisateur.
- **Flou de bougé** : le script active le flou de mouvement des calques rapides et de la composition, obturateur 120°, phase −60°. Le bouton « Flou de mouvement » de la timeline doit rester actif pour l'aperçu.
- **Flou gaussien** : le moteur règle « Flou » à 2 × σ, rapport mesuré dans EffectCraft. Dans After Effects, la correspondance n'est pas vérifiée : à regarder sur l'image (**convention**).
- **Une erreur** : After Effects affiche la ligne. Demande à l'utilisateur le message et le numéro de ligne, retrouve la recette dans le script (chaque bloc porte un commentaire et un repère de calque), corrige `motion.json` et régénère. Ne corrige pas le `.jsx` à la main, sauf demande : la prochaine génération l'écrase.
- **Images de contrôle** : l'utilisateur rend un MP4 et le donne ; tu en tires les images avec ffmpeg (§ 5).

---

## 3. Dans EffectCraft

EffectCraft se pilote par un canal de contrôle local (TCP `127.0.0.1:9877`, une ligne JSON par requête). `scripts/ec.py` est son client.

**Lancer l'app avec son canal**, si elle ne l'est pas :

```bash
open -a EffectCraft --args --control 9877
python3 "$SKILL/scripts/ec.py" activer        # premier plan : l'app ne traite les requêtes qu'ainsi
```

`activer` est le seul usage permis d'osascript (`tell application "EffectCraft" to activate`). N'automatise rien d'autre dans l'interface.

**Exécuter, regarder, rendre.**

```bash
python3 "$SKILL/scripts/ec.py" script motion.jsx                                  # construit la composition
python3 "$SKILL/scripts/ec.py" frames "<nom de la comp>" controle/ --pas 0.5 --max 640   # une image toutes les 0,5 s
python3 "$SKILL/scripts/ec.py" frame "<nom de la comp>" 4.3 image.png 1920       # une image précise
python3 "$SKILL/scripts/ec.py" render "<nom de la comp>" rendus/motion.mp4      # rendu H.264, attend la fin
```

- Le nom de la composition est `comp.nom` du `motion.json` (préfixé si `--prefixe`).
- `render` retire l'élément rendu de la file (sauf `--garder 1`) et attend jusqu'à 1 800 s.
- Chaque requête a un délai (`--delai`, 180 s par défaut) : une app bloquée ne bloque pas le terminal.
- Codes de sortie : 0 succès ; 1 erreur de l'app ; 2 délai dépassé ; 3 aucune app à l'écoute ; 4 refusé.

**Le projet de l'utilisateur.** `ec.py` refuse les commandes qui enregistrent, ouvrent, remplacent ou ferment le projet (`file.save`, `file.open`, `app.quit`…), sauf avec `--autoriser`. Ne l'emploie que si l'utilisateur le demande. Pour un essai, préfixe la composition (`--prefixe TEST-`). L'enregistrement du projet reste à l'utilisateur.

---

## 4. Pièges connus et parades

| symptôme | cause | parade |
|---|---|---|
| « délai dépassé », aucune réponse | la fenêtre d'EffectCraft n'est pas au premier plan | `ec.py activer`, ou `--relance` (remet au premier plan et renvoie la requête une fois) |
| « aucune app à l'écoute » | l'app tourne sans canal de contrôle, ou pas du tout | demander à l'utilisateur de la relancer avec `--args --control 9877` (ne pas la quitter soi-même : son projet est ouvert) |
| l'app à 100 % de processeur après une requête | une requête sur un masque animé a bloqué l'app | le moteur n'emploie aucun masque ; n'en ajoute pas à la main. Si l'app est bloquée, le dire à l'utilisateur, qui décide de la relancer |
| les mouvements sont tous linéaires | EffectCraft ignore interpolations et eases si la composition n'est pas active | le script appelle `comp.openInViewer()` avant toute clé ; à garder dans tout script écrit à la main |
| une courbe n'a aucun effet | une `KeyframeEase` posée sur une clé linéaire ne change rien | poser `KeyframeInterpolationType.BEZIER` avant l'ease (le moteur le fait) |
| deux clés n'en font qu'une | clés ramenées à l'image ; deux clés à moins d'une image fusionnent | temps calés sur l'image, au moins une image d'écart (le moteur le fait) |
| un masque élargi ne change rien au rendu | l'expansion de masque (`ADBE Mask Offset`) n'est pas rendue | groupes décalés ou caches (track matte) ; le moteur n'emploie aucun masque |
| une forme est décalée | un calque de forme compte ses sommets depuis son point d'ancrage | dessiner autour de l'ancre (0, 0) et placer par la position ; ou ancre = position = centre de la composition |
| un calque disparaît | un calque trop large (environ 27 000 px) n'est plus dessiné | aucun calque plus large que l'image ou que la diagonale de l'élément × 1,2 |
| une image existante devient un repli | `File.exists` répond faux dans EffectCraft | l'import est tenté quand même ; s'il échoue vraiment, vérifier le chemin absolu (régénérer sans `--relatif`) |
| une image à côté du script n'est pas trouvée dans EffectCraft | `$.fileName` vaut le nom passé à l'exécution, pas le chemin du fichier | le script garde aussi les chemins absolus de génération : régénérer sur la machine qui exécute |
| `editor.state` refusé en méthode | c'est une commande | `ec.py cmd editor.state` |
| le flou paraît deux fois trop fort ou trop faible | le réglage « Flou » du flou gaussien vaut 2 σ dans EffectCraft | le moteur convertit (`md_sigma`) ; à vérifier à l'œil dans After Effects |
| la police n'est pas la bonne | une police absente ne se signale pas | liste de polices avec repli dans le thème ; EffectCraft fournit Inter (Regular, Medium, SemiBold, Bold) |
| le rendu est retiré ou reste dans la file | la file de rendu garde les éléments rendus | `ec.py render` les retire, sauf `--garder 1` |
| le mouvement part dans le mauvais sens | la vitesse d'un ease n'a pas le signe de la variation | voir `courbes.md` § 8 |

---

## 5. Images de contrôle et vérification d'un rendu

**Une planche à partir des images de contrôle** (EffectCraft, `ec.py frames`) :

```bash
ffmpeg -v error -y -pattern_type glob -i 'controle/t*.png' -vf "scale=480:-1,tile=6x7:padding=4" -frames:v 1 planche.jpg
```

Avec un pas de 0,5 s, 6 × 7 images couvrent 21 s ; adapte la grille à la durée.

**Un MP4 rendu** (After Effects ou EffectCraft) :

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of csv=p=0 rendu.mp4
ffmpeg -v error -y -i rendu.mp4 -vf "fps=2,scale=480:-1,tile=6x7:padding=4" -frames:v 1 planche.jpg
ffmpeg -v error -y -ss 4.3 -i rendu.mp4 -frames:v 1 image-4s3.png
```

Pour juger une courbe, extrais les images d'un mouvement à pleine cadence (`-ss <début> -t <durée> -vf fps=30`) et regarde-les à la suite : le départ, le freinage, l'absence de dépassement.

**Ce qu'on regarde** (lis les images avec l'outil de lecture d'image) :
- chaque texte entier, lisible, sans boîte derrière ;
- le fond vide un instant après chaque coupe, puis l'élément ;
- un seul mouvement majeur à la fois ; le libellé après son chiffre ;
- aucun dépassement, aucun rebond, rien qui flotte en boucle ;
- les replis gris (images manquantes) et les `[À FOURNIR]` à l'écran ;
- rien qui rappelle une marque : ni appareil, ni police, ni logo, ni signature.
