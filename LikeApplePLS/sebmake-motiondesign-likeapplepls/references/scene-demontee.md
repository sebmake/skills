# La scène démontée : un plan-séquence d'interface, lisible calque par calque

Une scène démontée montre une interface en mouvement (une fenêtre, une caméra qui va d'un élément à l'autre, des halos, un curseur, une voix et des sous-titres), construite de façon à ce que **chaque mécanique ait son calque, nommé par son rôle**. On l'ouvre dans EffectCraft ou After Effects et on comprend comment elle marche ; on la retouche à la main ; on la relit en chiffres.

Elle sert à trois choses :

- un **film de démonstration** d'un logiciel, narré, de 20 s à quelques minutes, chapitre par chapitre ;
- un **plan d'interface** dans un film de fonctionnalités (`film-fonctionnalites.md`), quand le composant doit rester dans sa fenêtre ;
- **démonter** une animation faite ailleurs (une page HTML animée, un rendu d'un autre outil) pour la comprendre et la reprendre dans l'outil : on rend la fenêtre seule, sans caméra, et on reconstruit la caméra, les halos et le reste en calques.

Rien ici n'est mesuré dans le corpus des keynotes : tout est **convention**, réglée sur deux films faits avec cette méthode (un film de lancement de 30 s et une démonstration de 7 min 39 en dix chapitres). Les valeurs mesurées des recettes (`elements.md`) restent la référence pour ce qu'elles couvrent.

---

## 1. La mécanique

```
 Fond (solide)
 Fenêtre ─────────────── la caméra est ici : ANCRAGE = le point de la fenêtre qu'on regarde
   │                                          ÉCHELLE = le zoom × 100
   │                                          POSITION = toujours le centre de l'image
   ├─ Halo 1, Halo 2 …    enfants : placés en px de la fenêtre, ils suivent la caméra sans calcul
   └─ Curseur             enfant : ses positions sont celles des éléments cliqués
 Sous-titres, textes      fixes à l'écran, au-dessus de tout
 Intertitre               par-dessus tout ; la fenêtre apparaît quand il s'efface
 Voix 1…n, Sons, Musique  chacun à son instant ; la musique décalée pour tomber au bon endroit
```

- **Il n'y a pas de calque caméra.** Déplacer l'ancrage fait glisser l'image ; augmenter l'échelle fait plonger dedans. Un repère sur la fenêtre, à chaque clé, dit l'arrivée, le zoom et ce qu'on y regarde.
- **Les enfants travaillent en px de la fenêtre.** Un halo autour d'un bouton se décrit par le rectangle du bouton dans la capture, pas par sa place à l'écran, qui change à chaque instant.
- **Ce qui ne doit pas bouger avec la caméra n'a pas de parent** : sous-titres, intertitre, textes d'écran.
- Pourquoi pas un calque nul « caméra » : EffectCraft n'applique pas l'échelle d'un nul à une image enfant (l'image reste à 100 %, vu au test) ; et il place mal les enfants d'une image plus grande que la composition. La fenêtre porte donc la caméra, et elle ne dépasse jamais la composition.

## 2. `scene.json`

Chemins relatifs au dossier du fichier. Temps en secondes. Coordonnées de la fenêtre en px **du fichier** de la fenêtre.

```json
{
  "comp":    { "nom": "Démo · chapitre 1", "format": "16:9", "fps": 30, "duree": 19.5 },
  "theme":   { "fond": "#1B2420", "texte": "#F4F3EE", "secondaire": "#C9CFC9", "accent": "#E8B44C",
               "voile": "#0E1311", "police": "Inter-Medium", "police_titre": "Inter-Bold" },
  "fenetre": { "fichier": "fenetre.png", "largeur": 1440, "hauteur": 960, "apparition": [2.2, 2.8] },
  "camera":  { "flou_de_bouge": true, "cles": [
      { "t": 0,   "x": 720, "y": 480, "zoom": 1.05 },
      { "t": 3.6, "x": 720, "y": 480, "zoom": 1.05, "arrivee": "coupe", "note": "repos" },
      { "t": 5.0, "x": 160, "y": 60,  "zoom": 2.2,  "arrivee": "fouette", "note": "le bouton Nouveau" } ] },
  "enfants": {
    "halos":   [ { "nom": "Nouveau", "rect": [24, 28, 232, 44], "t0": 5.2, "t1": 7.8 } ],
    "curseur": { "points": [ { "t": 3.6, "x": 900, "y": 600 }, { "t": 4.9, "x": 150, "y": 52 } ], "clics": [7.0] } },
  "ecran": {
    "sous_titres": "voix.srt",
    "intertitre": { "t1": 2.6, "titre": "Le produit", "sous_titre": "Une phrase de promesse", "etiquette": "Démo" },
    "textes": [ { "texte": "…", "x": 960, "y": 120, "corps": 48, "t0": 3, "t1": 6 } ] },
  "son": {
    "voix":    [ { "t": 3.0, "fichier": "voix/v1.mp3", "texte": "début de la phrase" } ],
    "sons":    [ { "t": 7.0, "fichier": "clic.wav", "nom": "clic" } ],
    "musique": { "fichier": "musique.wav", "decalage": 0 } }
}
```

| Champ | Sens |
|---|---|
| `comp.format` | `16:9`, `16:9-4k` (3 840 × 2 160 : pour zoomer net sur une fenêtre ×2), `9:16`, `1:1` |
| `fenetre.fichier` | une image ou une vidéo de l'interface **seule**, sans caméra ni décor. Jamais plus grande que la composition (le script refuse) |
| `fenetre.apparition` | `[t0, t1]` : fondu d'entrée de la fenêtre (par exemple quand l'intertitre s'efface) |
| `camera.cles[].arrivee` | comment la caméra **arrive** sur cette clé (§ 3) ; la première clé n'en a pas |
| `camera.cles[].note` | ce qu'on regarde : écrit dans le repère de la clé, lu dans l'outil et par la sonde |
| `camera.flou_de_bouge` | flou de bougé de la composition, de la fenêtre et de ses enfants (EffectCraft le rend) |
| `enfants.halos[]` | `rect` [x, y, largeur, hauteur] de l'élément, `t0` (le contour se dessine en 0,45 s), `t1` (il s'efface en 0,3 s) ; `marge` 8, `epaisseur` 3, `arrondi` 12, `couleur` (l'accent) |
| `enfants.curseur` | `points` [{t, x, y}] (le curseur glisse d'un point à l'autre), `clics` [t] (il se creuse à 84 % pendant 0,14 s) |
| `ecran.sous_titres` | un fichier `.srt` ou une liste `[début, fin, texte]` ; coupé en deux lignes au-delà de 64 caractères (`caracteres_par_ligne`) |
| `son.musique.decalage` | où commence la musique dans le film entier : une scène qui est le chapitre 3 d'un film reprend la musique à son instant |

## 3. La caméra : poser, suivre, fouetter, couper

| `arrivee` | Interpolation | Quand |
|---|---|---|
| `pose` (défaut) | Bézier, influence 66 % de part et d'autre | un mouvement de plan qui part doucement et se pose |
| `suit` | Bézier, influence 33 % | accompagner un sujet qui bouge, sans à-coup |
| `fouette` | Bézier, influence 88 % | aller vite d'un point à un autre : presque tout le trajet au milieu |
| `lineaire` | linéaire | un travelling à vitesse constante |
| `coupe` | maintien | l'image ne bouge pas jusqu'à cette clé (un repos), ou saute à elle |

Comment poser les clés :

- **Un repos est deux clés identiques**, la seconde en `coupe` ; une clé sans `x`, `y` ou `zoom` garde ceux de la clé d'avant, donc un repos s'écrit `{"t": 6.4, "arrivee": "coupe"}`. Pendant un repos, rien ne bouge : c'est ce qui donne leur poids aux gestes. Une poussée lente pendant qu'on écoute la voix n'est pas un repos.
- **Suivre** : posez la clé là où sera le sujet un dixième de seconde plus tard ; la caméra paraît le tenir.
- **Fouetter** : posez la clé d'arrivée avant que le sujet y soit ; la caméra paraît l'attendre. Un fouetté va vite (300 px par image et plus) : mettez `flou_de_bouge`, sinon il se dédouble.
- **Une opération, un cadrage.** Chaque geste montré (ouvrir, choisir, envoyer) a son cadrage serré ; le plan large sert à situer et à finir.
- **Le curseur arrive avant la caméra, ou avec elle**, jamais après : sinon il sort du cadre pendant le mouvement (la sonde le voit).
- **Le halo s'efface avant que la caméra parte**, ou il sort du cadre en s'effaçant (vu sur la démonstration de 7 min 39, la sonde l'a relevé).

## 4. Lisibilité

- La taille d'un texte de l'interface à l'écran = son corps dans la capture × le zoom. Tout ce que la voix nomme doit faire **au moins 26 px à l'écran** en 1080p : un libellé de 13 px demande un zoom de 2.
- Une fenêtre qu'on doit lire occupe 70 à 80 % de la largeur de l'image ; le plan large ne sert pas à lire.
- **Netteté** : la fenêtre est une image ; zoomer ×2 sur une capture à 1:1 la rend douce. Pour des zooms forts, faites la capture ×2 et prenez le format `16:9-4k`.
- **La fenêtre vient d'une page web animée ?** Rendez-la comme une image (une vidéo de la fenêtre seule, sans caméra), pas comme du HTML filmé de près : le navigateur cale le texte sur la grille des pixels et il tremble pendant les zooms.

## 5. Trois concepts, et ce qui traverse chaque frontière

Avant le plan, pour un film (pas pour un élément isolé), proposez **trois idées centrales** qui diffèrent par l'image, pas par l'ordre des écrans : un seul plan qui se promène dans la fenêtre ; un composant qui sort de la fenêtre et devient le suivant ; un avant/après côte à côte ; une plongée d'un écran entier jusqu'à un bouton… Pour chacune : l'image d'accroche, ce qui passe d'un temps à l'autre, ce qu'elle s'interdit. L'utilisateur choisit.

Puis, dans le plan, une colonne **« ce qui traverse »** : à chaque changement de temps, ce qui survit et bouge pour passer au suivant. Dans une scène démontée, ce peut être :

- la **caméra** elle-même (la fenêtre reste, on change de cadrage) : la frontière est portée ;
- le **curseur**, qui va d'un élément à l'autre ;
- un **halo** qui glisse d'un élément au suivant plutôt que de disparaître ;
- un **composant** qui grandit jusqu'à devenir l'écran suivant (deux calques, le second enfant du premier le temps du passage).

Un changement où rien ne survit est une diapositive. C'est juste à la manière des keynotes, qui coupent d'abord (P1) ; ce n'est pas juste dans un plan-séquence. Choisissez l'un ou l'autre et dites-le dans le plan.

## 6. Relire en chiffres : la sonde et la mesure

**`sonde_ec.py`** lit la composition ouverte (les calques eux-mêmes, pas les pixels) :

- la **carte** : chaque calque, son genre, son parent, sa présence, ce qui est animé et combien de clés, ses repères. C'est la page à montrer pour expliquer la scène ;
- les **frontières** : instants où l'essentiel de ce qu'on voit change d'identité en 0,4 s ; chacune portée, ancrée ou nue, et une note de transport ;
- la **vitesse** : la plus grande course de chaque calque, en px par image ;
- le **cadre** : les calques surveillés (`--cadre "Curseur,Halo"`) qui sortent de l'image, et quand.

**`mesure_rendu.py`** lit le MP4 : carte d'énergie (un caractère par 1/12 s), part d'images immobiles, plus long calme, coupes, rafales, durées des plans et leur variation, son (crête, saturation, silence, intensité). `--ref` lit une référence à côté.

Repères (conventions : seuils d'usage du motion design de lancement, non mesurés sur le corpus) :

| Repère | Valeur | Ce qu'il dit |
|---|---|---|
| note de transport | < 0,5 : une suite de diapositives ; ≥ 0,7 : un plan qui se tient | ne se lit que pour un plan-séquence |
| vitesse | > 80 px par image sans flou de bougé | le mouvement se dédouble en copies nettes |
| cadre | un calque surveillé hors de l'image | le sujet est perdu pendant un mouvement |
| cadence | variation des plans (écart-type / moyenne) ≥ 0,25 | sinon le film coupe sur un métronome |
| repos | ≥ 25 % d'images immobiles et un calme d'au moins 1 s | sinon tout bouge et rien ne pèse |
| son | crête ≤ −3 dBFS, aucun échantillon saturé | une voix continue donne peu de silence : c'est normal |

Aucun repère ne bloque. Chacun se corrige, ou se garde en le disant.

## 7. La boucle de travail continue

1. **Écrire** `scene.json` (une scène par chapitre pour un long film), puis `scene_ec.py scene.json --prefixe TEST-`.
2. **Regarder** : planche d'images (`ec.py frames`), puis `sonde_ec.py` (carte, frontières, vitesse, cadre).
3. **Montrer la mécanique** : la capture de l'outil (`ec.py capture`), la carte, et une image du rendu à côté d'une image de référence au même instant. On explique calque par calque : ce que fait l'ancrage, ce que fait l'échelle, pourquoi les halos suivent seuls.
4. **Rendre** (`ec.py render`), puis `mesure_rendu.py`.
5. **Retoucher**, de deux façons :
   - dans `scene.json`, puis on régénère (la voie sûre : rien ne se perd) ;
   - **à la main dans l'outil** (une clé déplacée, un halo élargi) : on relance `sonde_ec.py`, dont la carte dit ce qui a changé (clés, présences, repères), et on reporte la retouche dans `scene.json` pour qu'elle survive à la prochaine génération. Le dire à l'utilisateur à chaque fois.
6. **Garder** : sur sa demande seulement, `ec.py --autoriser garder <nouveau fichier>.ecproj` enregistre le projet dans un fichier neuf, jamais par-dessus un autre. Le projet devient alors un objet de travail qu'on rouvre, qu'on lit et qu'on fait évoluer.
7. **Monter** : les scènes rendues deviennent les chapitres d'un montage (skill `sebmake-videoedit-like-applepls`, montage composé : image, voix, musique atténuée sous la voix, sous-titres, sons).

## 8. Pièges payés

| Symptôme | Cause | Parade |
|---|---|---|
| halos et curseur deux fois trop grands, décalés | fenêtre plus grande que la composition | fenêtre ≤ composition (le script refuse) ; format `16:9-4k` pour une capture ×2 |
| la fenêtre ignore le zoom | elle était l'enfant d'un calque nul : EffectCraft n'applique pas l'échelle du nul à une image | la fenêtre porte elle-même la caméra |
| mouvements tous linéaires | la composition n'était pas ouverte dans la visionneuse | le script l'ouvre avant toute clé |
| un halo sort du cadre en s'effaçant | la caméra part avant la fin du halo | `t1` du halo avant la clé de départ |
| le curseur sort du cadre pendant un fouetté | il arrive après la caméra | point du curseur sur l'élément avant la clé d'arrivée |
| `ec.py capture` : « no frame was presented » | fenêtre de l'app cachée ou écran en veille | la commande met l'app au premier plan ; écran allumé |
| image plus douce que l'original | la fenêtre est une image agrandie par le zoom | capture ×2 et format `16:9-4k` |
