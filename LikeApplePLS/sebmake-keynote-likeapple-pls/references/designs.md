# Designs : le dessin de chaque slide

Ce fichier dit, archétype par archétype, ce que la slide montre : le contenu visuel (produit mis en lumière, interface dans un appareil, photo à fond perdu, icône, matière), les compositions possibles, la profondeur (ombre, halo, objet qui sort du cadre) et le visuel à demander à l'utilisateur. Il complète `style-visuel.md`, qui donne les mesures du texte (corps, graisses, interlignes, couleurs) : on y renvoie, on ne les recopie pas.

Tout vient des 8 keynotes du corpus (2019 à 2026), regardées image par image : environ 590 images pour ces fiches, mesurées au pixel quand une valeur est donnée. La grammaire, jamais la marque : aucun produit, aucun appareil reconnaissable, aucune police, aucun logo et aucun texte d'écran du corpus ne passe dans la skill. Les appareils que le moteur dessine sont génériques : ni encoche, ni boutons, ni caméra.

## Sommaire

1. Comment lire
2. Choisir un design : la méthode, les variantes du moteur, un exemple de bloc
3. Règles communes à toutes les fiches
4. Textes : A1 Carte-titre · A2 Icône ou logo + nom · A3 Sommaire typographique · A4 Phrase-thèse · A7 Liste sans puces · A8 Liste à coches · A17 Citation ou témoignage · A21 Synthé nom et fonction
5. Chiffres et preuves : A5 Gros chiffre + libellé · A6 Graphique comparatif · A11 Schéma à bloc surligné · A15 Mur d'abondance · A16 Logos partenaires
6. Produit et image : A9 Objet + texte · A10 Capture plein cadre · A12 Vue intérieure / éclaté · A13 Produit seul · A18 Photo plein cadre · A22 Plan large + écran · A23 Orateur dans la slide · A24 Décor sans écran · A25 Démo manipulée
7. Récap et conversion : A14 Bento · A19 Prix · A20 Disponibilité · Slide finale · Gamme de coloris · Frise

## 1. Comment lire

- **Comptes N/8** : le nombre de keynotes, sur les 8, où l'on voit la variante, au moins une fois. v5 et v6 sont en direct (2019) ; v1 et v2 (2020), v7 (2024), v8 et v3 (2025), v4 (2026) sont préenregistrées. Une variante vue dans une seule keynote reste une variante, pas une règle.
- **Statuts** : *mesuré* (au pixel), *estimé* (à l'œil, à 2 % près), *convention* (choix de la skill, non observé).
- **Positions** : sur un canevas 100 × 100 ; x, y = coin haut gauche ; l, h = largeur, hauteur ; en % de la largeur (L) et de la hauteur (H). 1 % L = 0,1 in ; 1 % H = 0,056 in. Marge du moteur : 6 % L. Un x négatif, ou un x + l au-delà de 100, veut dire que l'objet sort du cadre. Pour un texte, y et h bornent la zone des capitales, comme dans `style-visuel.md`.
- **Corps** : donnés pour Inter (corps ≈ cap en % H × 5,6). Pour une autre police, refais le calcul de `style-visuel.md` §0.
- **Huit parties par fiche** : 1 Rôle et moment · 2 Composition canonique (zones et croquis) · 3 Variantes observées · 4 Contenu visuel (type, cadrage, traitement, accent) · 5 Typographie (seulement ce qui change par rapport à `style-visuel.md`) · 6 Apparition et animation · 7 Brief du visuel et repli · 8 À éviter.
- **Dans le moteur** : en tête du §3, les valeurs de `slide.variante` que `build_deck.js` dessine, et ce qu'il fait sans variante. Les champs que lit chaque variante sont dans `deck-spec.md`, « Variantes ». Ce que la fiche décrit hors de cette liste (un morphing, un plan tourné) se fait à la main dans le logiciel, ou en vidéo.
- **Plans de scène (A22 à A25)** : ce sont des plans vidéo, pas des slides. Leur fiche dit ce qu'on en garde dans un deck projeté, et ce qu'on tourne pour une vidéo.

## 2. Choisir un design

À l'étape « Design slide par slide » (`SKILL.md`), pour chaque ligne du conducteur. Ces six règles sont des conventions de la skill, tirées des fiches :

1. **L'archétype vient de l'étape d'annonce** (`grammaire.md` §4.1, colonne Visuel). Change-le seulement si le contenu ne s'y prête pas : pas de chiffre sourcé, pas d'A5.
2. **La variante vient du contenu et des visuels.** L'utilisateur a une capture : une variante à appareil. Il a une photo : une variante sur image. Il n'a rien : une variante sans visuel (aplat, centre), jamais un cadre vide. La table ci-dessous dit ce que chaque variante demande.
3. **Varie les designs.** Jamais trois slides de suite avec le même archétype et la même variante : le contrôle le signale. Deux blocs n'ouvrent pas de la même façon. Deux cartes-titres qui se suivent changent de variante.
4. **Au moins un moment visuel fort par bloc** : un chiffre géant (A5), un objet ou une interface (A9, A10), le produit seul (A13), le bento (A14), une photo plein cadre (A18), ou une variante à image (colonne « Moment visuel fort » de la table). Place-le là où le bloc prouve ou révèle.
5. **Dose la profondeur** : un objet qui sort du cadre, un halo d'accent, ou une ombre de contact sur fond clair. Une seule de ces trois choses par slide, et jamais d'ombre sur fond sombre.
6. **Écris le visuel à préparer** dans `slide.visuel` (`deck-spec.md`), d'après le §7 de la fiche : type, brief, fond transparent, angle, résolution minimale. `export_script.js --visuels` en tire la liste à livrer.
7. **Va chercher les visuels toi-même quand tu le peux**, avec l'accord de l'utilisateur. Deux sources :
   - **sa maquette, jusqu'au composant.** Avec le lien d'une maquette (Figma, par exemple), ne t'arrête pas à l'écran entier. Entre dans la frame, isole le composant qui dit la fonction (une carte, un bouton, une colonne de statuts, un menu, trois lignes d'un tableau) et exporte-le seul. Un écran réduit dans une tuile ou à côté d'un texte devient illisible ; un composant se lit. L'écran entier reste pour l'A10 et les appareils.
   - **une banque de photos libre de droits**, pour les photos d'usage et d'ambiance : Unsplash ou Pexels. Sur Unsplash, filtre sur « gratuit » (l'offre payante Unsplash+ est exclue) et vérifie « Photo gratuite » sur la page de la photo. Sur Pexels, vérifie « Free to use ». Note l'auteur et le lien pour les crédits. La photo montre le métier et le marché du public (lieux, signalétique, objets et gens du pays visé), aucune marque lisible et jamais une image générée présentée comme une photo.

### Les variantes du moteur

`build_deck.js` dessine toutes les variantes de ces fiches, sous leur nom exact (`slide.variante`). Entre parenthèses : le visuel qu'une variante demande. Sans ce visuel, le moteur dessine le repli de la fiche (§7). La dernière colonne dit quelles variantes font le moment visuel fort d'un bloc ; le contrôle s'en sert.

| Archétype | Variantes (`slide.variante`) | Moment visuel fort |
|---|---|---|
| A1 Carte-titre | `aplat` · `degrade` · `sur-image` (photo calme) · `entoure` (20 à 50 mots du sujet) · `matiere` (le mot rendu en matière) | `sur-image`, `matiere` |
| A2 Icône ou logo + nom | `icone-nom` (icône) · `icone-cote` (icône) · `logo-nom` (logo) · `rangee` (trois icônes) · `objet-interface` · `icone-seule` (icône) | non |
| A3 Sommaire | `centre` · `droite` · `ligne` · `numerote` · `suffixe` · `ligne-active` · `couleurs` (un HEX par bloc) | non |
| A4 Phrase-thèse | `aplat` · `degrade` · `mot-accent` · `definition` · `sur-image` (matière sombre) · `sourdine` · `enchainee` | `sur-image` |
| A5 Gros chiffre | `centre` · `bloc` · `a-cote` (capture ou objet) · `sur-photo` (photo du lieu) · `objet-anneau` · `objet-jauge` · `contour` | toutes |
| A6 Graphique | `barres` · `deux-axes` (des séries de points) · `anneaux` (deux parts) · `frise` · `classement` (des logos) | non |
| A7 Liste | `centree` · `empilement` · `a-cote-icone` (icône) · `a-cote-objet` (objet ou capture) · `deux-colonnes` (icône) · `sur-photo` (photo calme) · `filet` (capture) | `a-cote-objet`, `sur-photo`, `filet` |
| A8 Coches | `coche-par-ligne` · `cercles-puis-coches` · `risque-puis-reponse` · `picto-par-ligne` (pictogrammes) · `sur-contenu` (photo) | `sur-contenu` |
| A9 Objet + texte | `appareil-centre-mot` (capture) · `objet-coupe` (produit) · `objet-liste` (icône ou objet) · `objet-chiffre` (produit) · `annotee` (rendu ou capture) · `empilee` (produit) | toutes |
| A10 Capture | `telephone-centre` · `tablette-centre` · `portable-centre` · `zoom-serre` · `capture-nue` · `rangee` (trois captures) : toujours une capture nue | toutes |
| A11 Schéma | `legende-laterale` · `plusieurs-blocs` · `schema-chiffre` · `carte-annotee` (vue de dessus) · `carre-halo` : schéma SVG facultatif | `carte-annotee` |
| A12 Vue intérieure | `macro-matiere` · `capot-ouvert` · `eclate-axial` · `flux-lumiere` : rendu 3D ou macro | toutes |
| A13 Produit seul | `centre-entier` · `hero-coupe` · `profil-levitation` · `coloris` (deux vues) : produit détouré | toutes |
| A14 Bento | `nom-au-centre` · `produit-au-centre` (produit) · `tuiles-chiffres` (produit) · `mot-geant-et-produit` (produit) · `theme-et-matieres` (photo) · `grille-icones` (icônes) · `fragments-logiciel` (composants d'interface, une photo d'usage) | toutes |
| A15 Mur | `vignettes` (20 à 40 images) · `icones` (40 à 100 icônes) · `mots` · `nuage` · `cartes-libelles` · `forme` (images) | `vignettes`, `icones`, `forme` |
| A16 Logos | `grille` · `ligne` · `logo-seul` · `mur-dense` · `pastilles` · `soi-au-centre` : logos monochromes | non |
| A17 Citation | `courte` · `longue` · `source-accent` · `centree-signature` | non |
| A18 Photo | `usage` · `exemple-cartouche` · `diptyque` (deux photos) · `photo-titre` : photo | toutes |
| A19 Prix | `colonne` · `deux-offres` · `nom-en-haut` · `gamme-alignee` (un produit par offre) · `prix-heros` · `ancrage` : produit détouré | `colonne`, `deux-offres`, `nom-en-haut`, `gamme-alignee` |
| A20 Disponibilité | `haut-et-gamme` · `suite-de-dates` · `colonne` · `date-et-lieux` · `mot-seul` : gamme ou produit détouré | toutes sauf `mot-seul` |
| A21 Synthé | `gauche` · `droite` · `double` · `sur-clair` · `carte-invite` (logo) · `carte-portrait` (portrait) : photo de l'intervenant | toutes sauf `carte-invite` |
| A22 à A25 Plans de scène | acceptées, rendues en photo de la scène (voir leurs fiches) | toutes |
| FIN Slide finale | `signe-seul` · `signe-et-ligne` · `signe-et-evenement` · `signe-sur-photo` (photo calme) · `mot-final` : logo monochrome | `signe-sur-photo` |
| COLORIS Gamme de coloris | `rangee-alignee` · `rangee-chevauchee` · `eventail` · `un-par-un` · `mur` : un rendu détouré par coloris | toutes |
| FRISE Frise | `rangee-datee` · `generations` · `trois-jalons` (objets) · `courbe-et-saut` · `objet-du-passe` (objet) | `trois-jalons`, `objet-du-passe` |

Les variantes de FIN, COLORIS et FRISE se posent sur n'importe quel archétype : `"archetype": "A1", "variante": "mot-final"`. Sans variante, le moteur garde le rendu d'origine de l'archétype, plus simple ; pour A1, A3, A4, A5, A7 et A17, c'est le même que la première variante. Écris donc toujours la variante.

La profondeur est réglée par le moteur : sur fond clair, une ombre de contact très douce sous un produit, un appareil ou une silhouette ; sur fond sombre, aucune ombre, mais un halo doux et neutre derrière un produit. `"profondeur": false` sur la slide retire les deux. Les objets coupés par le cadre le sont dans `objet-coupe`, `objet-chiffre`, `hero-coupe`, `zoom-serre`, `filet`, `rangee-chevauchee`, `mur`, `vignettes`, `icones` et `nuage`.

### Un bloc d'annonce, slide par slide

Une nouveauté de logiciel en 8 étapes, avec une capture et une photo fournies. Chaque ligne change de composition, et le bloc a trois moments forts : la capture, le chiffre, le bento.

| Étape | Design | Ce qu'on voit | Visuel |
|---|---|---|---|
| 3 Tension | A4 · `aplat` | le manque, en une phrase | aucun |
| 6 Nom | A1 · `sur-image` | le nom, en blanc, sur la photo calme du lieu d'usage | photo fournie |
| 7 Définition | A4 · `mot-accent` | ce que ça fait, un groupe de mots en accent | aucun |
| 9 Pilier | A10 · `telephone-centre` | l'écran réel, de face, dans un téléphone générique | capture fournie |
| 9 Pilier | A9 · `appareil-centre-mot` | le même écran à la même place ; le nom de la fonction dans la marge | la même capture |
| 9 Preuve | A5 · `bloc` | le chiffre, sa base de comparaison collée dessous | aucun : un chiffre sourcé |
| 13 Garde-fou | A8 · `coche-par-ligne` | trois engagements, une coche par clic | aucun |
| 14 Mini-récap | A14 · `nom-au-centre` | le nom au centre, ce qui a été montré autour | captures et icônes des tuiles |

Sans la capture, le pilier passe en A9 `objet-liste` (une icône et trois lignes) et le moment fort reste le chiffre. Sans la photo, le nom passe en A1 `aplat` : seul à l'écran, il garde sa force, et le bloc garde ses moments forts.

## 3. Règles communes à toutes les fiches

1. **Le visuel prend la place** (`style-visuel.md` §1, règle 8) : un appareil sur 91 % H, un objet sur 56 à 62 % L, un produit sur 60 à 87 % H, une photo à fond perdu.
2. **Appareil générique seulement** : un rectangle à coins de 13 % de sa largeur, avec un bord de 3 %, en verre noir cerné d'un fin liseré clair (sur fond sombre comme sur fond clair : le corpus ne montre aucun cadre gris clair) ; ni encoche, ni îlot, ni boutons, ni caméra (`style-visuel.md` §5.2). On demande toujours une capture nue, sans cadre d'appareil : le moteur pose le cadre.
3. **Profondeur.** Aucune ombre sur fond sombre. Sur fond clair, une ombre de contact très douce sous un objet, au plus : aucune ombre portée nette sur les 86 images d'objets et d'écrans regardées (A9, A10, A12, A13), qui couvrent 8/8 keynotes. Le halo (une lueur d'accent floue) désigne une seule chose : le bloc allumé d'un schéma, l'anneau d'un chiffre, le jalon actuel d'une frise. L'objet qui sort du cadre dit la taille et la proximité (A9, A13, tuiles du bento).
4. **L'image porte la couleur.** Le texte posé à côté d'une image reste dans la couleur du texte (9 images sur 10 en A9, dans 4/8 : v3, v4, v7, v8). L'accent va à un seul élément : le chiffre, le halo, la ligne mise en avant d'une interface.
5. **Un fond par bloc** : aucune slide ne change de fond seule (`style-visuel.md` §4.3).
6. **Un repli ne ment pas.** Un visuel qui manque laisse place à un dessin neutre (interface schématique, silhouette, aplat et deux halos) qui ne porte jamais de nombre, de logo, de nom de marque ni de personne dessinée. La silhouette est un volume modelé comme un objet de studio (haut éclairé, bas dans l'ombre, arête claire, reflet doux), gris moyen sur fond sombre (30 % du texte), jamais un aplat sombre qui se perd dans le fond. Un PNG détouré se cale, s'ombre et se coupe sur sa partie opaque, pas sur les marges transparentes du fichier. Un chiffre, un prix, une date ou un coloris qui manque devient un `[À FOURNIR]` estompé dans son champ, jamais une valeur proposée.

## 4. Textes

Les slides où le texte est le visuel : le nom, le sommaire, la phrase, les listes, la citation, le synthé. Images regardées pour ces fiches : 129.

### A1 · Carte-titre

#### 1. Rôle et moment

- Elle ouvre un chapitre, une fonction ou un argument, à l'instant où son nom est dit. Rien d'autre n'est à l'écran. Présente dans 8/8.
- C'est la ponctuation la plus fréquente : environ 40 dans v7, 15 à 20 dans v1, 12 à 15 dans v3.
- Place dans la séquence : juste après le relais ou la phrase de cadrage, juste avant la démo, la capture ou le chiffre. Elle sert aussi de slide finale (un mot, corps plus gros).
- La même carte repasse souvent sur l'écran du décor, l'orateur à côté (4/8 : v1, v2, v7, v8). Un deck n'en garde que la version plein cadre.

#### 2. Composition canonique

| Zone | x | y | l | h | Règle |
|---|---|---|---|---|---|
| surtitre (facultatif) | 6 | 27 | 88 | 6 | centré ; ligne de base à 0,45 cap au-dessus du nom |
| titre (le nom) | 6 | 40 | 88 | 20 | centre des capitales à 50 % H et 50 % L ; cap de 14,5 à 19 % H ; une ligne |

Le nom occupe de 29 à 59 % L pour un ou deux mots (`style-visuel.md`), jusqu'à 72 % L pour deux mots longs (v3, mesuré). Tout le reste est vide.

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                     surtitre (facultatif)                      |
|                                                                |
|    +------------------------------------------------------+    |
|    |                       N O M .                        |    |
|    |                                                      |    |
|    +------------------------------------------------------+    |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `aplat`, `degrade`, `sur-image`, `entoure` ou `matiere`. Sans variante : comme `aplat`. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **aplat** (mot seul en aplat) | 5/8 (v5, v1, v2, v3, v4) | Le nom dans la couleur du texte : blanc sur noir, noir sur gris clair. v5 le pose dans la couleur du service. |
| **degrade** (dégradé de section) | 5/8 (v2, v3, v4, v7, v8) | Le nom en dégradé horizontal de la teinte de la section : plus sombre à gauche, plus clair à droite, ou deux teintes voisines. v7 et v8 le font sur toutes leurs cartes. |
| **sur-image** (photo calme ou fond flou) | 4/8 (v5, v2, v4, v8) | Le nom, blanc, posé sur une image plein cadre : mur du décor, vue aérienne, ciel, fond d'écran coloré ; ou un fond clair flou (toute la keynote v8). v4 le fait environ 10 fois pour ouvrir un sous-chapitre. |
| **entoure** (couronne d'éléments) | 2/8 (v6, v8) | Le nom au centre, plus petit ; autour, une couronne de petits pictogrammes au trait (v6) ou de noms techniques gris de tailles variées (v8). L'ovale central reste vide. |
| **matiere** (lettres en matière) | 2/8 (v6, v8) | Les lettres sont un objet : trait lumineux en contour (v6), verre en relief irisé sur blanc (v8). Le moteur ne la dessine pas : elle vient d'une image fournie. |

Vu aussi : un petit mot au-dessus du nom, sur une image (v2, 1/8) ; c'est le surtitre déjà prévu par le moteur.

#### 4. Contenu visuel

- **aplat, degrade** : aucun visuel. Le vide fait la slide.
- **sur-image** : photo à fond perdu, sans cadre ni coins (`style-visuel.md` §4.3). Le centre est calme : une surface (mur, ciel, sable, eau). Le sujet et les figurants restent sur les bords (v4 : figurants à gauche et à droite, mur nu au milieu). Lumière naturelle et douce. Voile noir de 20 à 45 % seulement si le blanc ne tient pas 4,5:1. Fond flou : photo claire défocalisée, deux ou trois taches de couleur douces (v8).
- **entoure** : 20 à 50 éléments sur toute l'image, plus petits et plus pâles que le nom (gris secondaire, ou trait de la couleur de la section), de trois tailles. Aucun ne touche l'ovale central (60 % L × 36 % H).
- **matiere** : l'image du mot seul, détourée.
- **Accent** : le nom (aplat d'accent ou dégradé) ou le point final. Un seul des deux.

#### 5. Typographie

Corps, plancher, graisse et suivi : `style-visuel.md` §3 A1. Ce qui change ici :
- 1 à 3 mots, 5 au plus (v7). Une commande ou un nom de 4 mots garde la carte-titre, en cap ≈ 10 % H (v7 : bande de 11,7 % H jambages compris, 45 % L).
- **sur-image** : blanc pur, même corps, jamais d'ombre portée (§5.1).
- **entoure** : nom à 72 pt (cap ≈ 13 % H) ; éléments de 10 à 20 pt, regular, secondaire.
- Intertitre discret (v4, 1/8) : cap ≈ 6 % H quand le mot suit la phrase de l'orateur. Pas en défaut.

#### 6. Apparition et animation

- Fondu de la slide (0,5 s) ; le nom est là quand il est dit (8/8).
- **Balayage** de gauche à droite qui révèle le nom (v3, 1/8 : une image saisit le nom à moitié révélé). pptx : entrée « Balayer » depuis la gauche, 0,6 s.
- Sortie par un fondu vers le fond (v7) : le fondu de la slide suivante suffit.
- **sur-image** : l'image entre avec la slide, le nom au clic (convention).
- **entoure** : le nom d'abord, puis la couronne d'un bloc (convention ; v6 anime ses pictogrammes à l'apparition).

#### 7. Brief du visuel et repli

- **aplat, degrade** : rien à fournir, sauf le nom exact ; `accent2` pour le dégradé.
- **sur-image** : photo 16:9, JPEG, 1920 × 1080 au moins (3840 × 2160 conseillé). Sans texte ni logo. Centre calme sur 60 % L × 30 % H ; sujet sur les bords ; aucune ligne forte dans la bande 40-60 % H. Pas de transparence.
- **entoure** : 20 à 50 mots réels du sujet (modules, fonctions, métiers), ou 20 à 50 pictogrammes SVG monochromes au trait.
- **matiere** : PNG à fond transparent, le mot seul, 3000 px de large au moins, cadré serré, éclairé de face.
- **Repli dessiné** : sur-image → aplat un peu plus clair que le fond et deux halos neutres très flous (`style-visuel.md` §5.2) ; entoure → couronne de pastilles rondes et de barres grises à bouts ronds (texte mélangé à 22-38 %), sans texte ni nombre ; matiere → le nom en aplat.

#### 8. À éviter

- Plus de 3 mots, ou un nom coupé en deux lignes alors qu'il tient sur une.
- Un second élément (logo, icône, sous-titre) : ce n'est plus A1, c'est A2 ou A4.
- Le nom en haut de la slide, du vide dessous.
- Une photo chargée au centre ; un voile qui grise toute l'image ; une ombre sur le texte.
- Dégradé et point d'accent ensemble ; deux couleurs d'accent.
- Changer de fond pour une seule carte au milieu d'un bloc (§4.3).

### A2 · Icône ou logo + nom

#### 1. Rôle et moment

- Elle annonce une app, une technologie, un service ou un module : « voici le sujet ». Présente dans 7/8 (pas v3).
- Environ 20 à 30 par conférence logicielle (v1, v6, v7, v8). Dans v8, elle ouvre presque chaque sous-section.
- Moment : juste après le cadrage, avant la démo. Dans v8, l'icône sert aussi de porte vers le décor suivant.

#### 2. Composition canonique

Mesurée sur 4 images plein cadre (v1, v2, v4).

| Zone | x | y | l | h | Règle |
|---|---|---|---|---|---|
| icône | 39 | 30,5 | 22 | 39 | carrée ; centrée sur 50 % L et 50 % H ; côté de 30,6 à 44,2 % H (médiane 39,7) |
| nom | 10 | 76 | 80 | 8 | centré ; haut des capitales à 77 % H ; cap ≈ 5,5 % H ; une ligne de 15 à 50 % L |

- L'icône tient le centre ; le nom descend dans le tiers bas. Écart entre l'icône et le nom : 5,5 à 7,3 % H. La cap du nom vaut environ 0,14 fois le côté de l'icône.
- En pouces : icône de 2,2 in, centrée sur 50 % H ; nom de 32 pt, plancher 24 pt, haut des capitales à 4,33 in.

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                         +------------+                         |
|                         |            |                         |
|                         |   ICONE    |                         |
|                         |            |                         |
|                         |            |                         |
|                         |  (carre)   |                         |
|                         |            |                         |
|                         +------------+                         |
|                                                                |
|                              Nom                               |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `icone-nom`, `icone-cote`, `logo-nom`, `rangee`, `objet-interface` ou `icone-seule`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **icone-nom** (icône centrée, nom dessous) | 4/8 (v1, v4, v7, v8) | La composition canonique. v7 et v8 la montrent surtout sur l'écran du décor, l'orateur à côté. |
| **icone-cote** (icône à gauche, nom à droite) | 1/8 (v6, environ 25 fois) | L'icône et le nom sur la même ligne médiane ; le nom aligné à gauche après l'icône. |
| **logo-nom** (logo de la marque + nom) | 3/8 (v5, v1, v4) | Pas d'icône : le logo de la marque collé au nom du service, sur une ligne, au corps d'une carte-titre (cap de 11 à 17 % H mesurée). Logo haut de 1,1 fois la cap ; écart ≈ 0,3 cap. Toujours sur noir (3/3). |
| **rangee** (rangée, puis chacune seule) | 3/8 (v2, v6, v7) | Deux à cinq icônes alignées sans nom (trio : 3 × 22 % L, écart ≈ 2 % L, de 30 à 70 % H), puis chaque icône seule à son tour. v7 en fait une grille de 3 à 12 icônes en sommaire de chapitre. |
| **objet-interface** (un bouton seul) | 1/8 (v6) | L'élément d'interface seul, en pilule claire, son libellé dedans ; pas d'icône. |
| **icone-seule** (sans nom écrit) | 1/8 (v2) | L'icône seule au centre ; le nom n'est que dit. Elle suit souvent une rangée. |

Vu aussi, hors slide : des icônes qui apparaissent une à une à côté de l'orateur filmé (v4, 1/8).

#### 4. Contenu visuel

- **L'icône** : tuile carrée à coins arrondis (coin ≈ 19 à 22 % du côté, mesuré sur 2 icônes) ; aplat ou dégradé vertical doux d'une seule teinte ; un pictogramme simple au centre (50 à 65 % du côté), blanc ou sombre. Variante en volume : trois couches empilées vues de trois quarts (v1, 1/8).
- **Traitement** : aucune ombre sur fond sombre ; aucune ombre visible sur fond clair non plus (v7, v8). Ni halo, ni reflet.
- **Cadrage** : entière, centrée, jamais coupée par le bord.
- **Accent** : la couleur est dans l'icône ; le nom reste dans la couleur du texte.

#### 5. Typographie

- Nom en demi-gras, cap ≈ 5,5 % H (≈ 32 pt), une ligne, 1 à 4 mots, couleur du texte.
- **icone-cote** : même corps, aligné à gauche à 46 % L, centré sur le milieu de l'icône.
- **logo-nom** : corps d'une carte-titre (`style-visuel.md` §3 A1), réduit pour tenir dans 60 % L.
- **objet-interface** : libellé de 28 pt dans la pilule, couleur du fond de la slide.
- Aucun surtitre vu sur cet archétype (0/7).

#### 6. Apparition et animation

- L'icône et le nom entrent ensemble, en fondu, quand le nom est dit (7/7).
- **rangee** : la rangée entre d'un bloc ; puis une slide par icône (morphose : l'icône glisse au centre, les autres s'effacent).
- **Porte** (v8, 1/8) : zoom avant dans l'icône vers la slide suivante. pptx : transition « Zoom », ou morphose vers une slide où l'icône est agrandie à 400 %.

#### 7. Brief du visuel et repli

- **Icône** : SVG, ou PNG à fond transparent, carrée, 1024 × 1024 px au moins, le pictogramme sans texte et sans ombre intégrée. Si l'icône n'a pas de tuile, donner sa couleur : le moteur pose la tuile.
- **Logo** : SVG ou PNG transparent, une version claire et une sombre, 2000 px de large au moins.
- **Bouton** : son libellé exact et sa couleur.
- **Repli dessiné** : tuile carrée à coins de 20 %, dégradé vertical de l'accent (haut éclairci de 20 %), anneau blanc au centre (diamètre 50 % du côté, trait 8 %). Dans une rangée ou une grille d'icônes, chaque tuile prend sa teinte (accent, accent 2, leur mélange, un gris) et sa forme (anneau, carré, barres, point) : trois tuiles identiques se liraient comme un tampon répété. Ni lettre, ni nombre, ni forme qui rappelle une marque. logo-nom sans logo → le nom seul, en A1.

#### 8. À éviter

- Un nom plus gros ou plus large que l'icône.
- Une icône sous 30 % H, ou un bloc centré qui la fait remonter vers le haut.
- Une icône empruntée : app connue, logo d'une autre marque.
- Une ombre portée noire, un cadre ou un contour autour de l'icône.
- Le nom en accent en plus d'une icône colorée.
- Une phrase à la place du nom.

### A3 · Sommaire typographique

#### 1. Rôle et moment

- Il annonce les blocs de la présentation, juste après l'accueil. Présent dans 4/8 : les 4 conférences logicielles (v6, v1, v7, v8) ; aucun événement produit (0/4).
- Il revient à l'identique avant la clôture : 2/8 (v7, v8). v7 ouvre aussi chaque grand bloc par un sommaire (6 en tout).
- Dans un deck : après la thèse d'ouverture, puis avant le récap final.

#### 2. Composition canonique

| Zone | x | y | l | h | Règle |
|---|---|---|---|---|---|
| liste, centrée | 10 | 16 | 80 | 66 | 4 à 6 lignes, une par bloc, 1 à 3 mots ; centre du bloc à 49 % H |
| liste, alignée à droite | 20 | 10 | 56 | 80 | même liste, bord droit à 76 % L |

- Corps selon le nombre de lignes, et interligne : `style-visuel.md` §3 A3.
- Mesuré : pas de 12,5 % H pour 6 lignes centrées (v7) ; 14,2 % H pour 6 lignes à droite, bord droit à 64,8 % L, bloc de 9 à 91 % H (v8). La pile remplit la hauteur.

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|             +----------------------------------+               |
|             |                           bloc 1 |               |
|             |                                  |               |
|             |                           bloc 2 |               |
|             |                                  |               |
|             |                           bloc 3 |               |
|             |                                  |               |
|             |                           bloc 4 |               |
|             |                                  |               |
|             |                           bloc 5 |               |
|             |                                  |               |
|             |                           bloc 6 |               |
|             |                                  |               |
|             +----------------------------------+               |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `centre`, `droite`, `ligne`, `numerote`, `suffixe`, `ligne-active` ou `couleurs`. Sans variante : comme `centre`. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **centre** (pile centrée) | 1/8 (v7) | Les lignes centrées, une par bloc. |
| **droite** (pile alignée à droite) | 2/8 (v1, v8) | Bord droit à 65-78 % L ; la moitié gauche reste à l'orateur (v1) ou au vide (v8). |
| **ligne** (une seule ligne) | 1/8 (v6) | Les quatre noms côte à côte, espacés, au milieu. |
| **numerote** (pile numérotée) | 1/8 (v7) | Un numéro d'ordre cerclé au trait devant chaque ligne ; lignes alignées à gauche dans un bloc centré ; trois lignes. |
| **suffixe** (second état) | 1/8 (v8) | Au clic, un même mot s'ajoute au bout de chaque ligne, en graisse plus légère. |
| **ligne-active** (lignes une à une) | 1/8 (v7) | La première ligne seule au centre, la suivante très pâle dessous ; à chaque clic, une ligne de plus et le bloc se recentre. |
| **couleurs** (une couleur par bloc) | 2/8 (v7, v8) | Chaque ligne dans la couleur de son bloc. Les deux autres keynotes restent en blanc (2/8 : v6, v1). Un dégradé commun à toute la pile se voit une fois (v7). |

#### 4. Contenu visuel

- Aucun visuel. Le fond est un aplat (v6, v1, v7) ; v8 pose un fond clair flou (1/8), que la skill ne reprend pas (`style-visuel.md` §4.3).
- **Accent** : la ligne du bloc en cours (moteur), ou une couleur par bloc si l'utilisateur en a. Le sommaire est une des trois exceptions à « un seul accent par slide » (`style-visuel.md` §1, règle 6).

#### 5. Typographie

- Mesures : `style-visuel.md` §3 A3. Ce qui change ici :
- **ligne** : 40 pt sur une ligne de 88 % L, un cadratin entre deux noms.
- **numerote** : 48 pt ; cercles au trait hauts de 1,1 cap, en accent ; numéro en regular.
- **suffixe** : même corps que le nom, en regular.

#### 6. Apparition et animation

- Bloc entier avec la slide : 3/4 (v6, v1, v8).
- Ligne à ligne, bloc recentré : v7. Une slide par état, morphose ; repli en fondu.
- **suffixe** : second état par morphose, sinon fondu du mot ajouté.
- Reprise avant la clôture : la même slide ; les blocs traités passent au secondaire, le dernier reste plein (champ `actif`).

#### 7. Brief du visuel et repli

- Les noms des blocs, 1 à 3 mots chacun, dans l'ordre du déroulé.
- Un code couleur par bloc, s'il existe : les HEX, à 3:1 au moins sur le fond.
- **suffixe** : le mot exact (année, version), jamais inventé.
- **Repli** : rien à dessiner. Sans code couleur : la ligne en cours en accent, les autres dans la couleur du texte. Sans numéros voulus : un petit cercle plein d'accent, sans chiffre.

#### 8. À éviter

- Plus de 6 lignes, ou des phrases.
- Puces et tirets ; numéros quand l'ordre ne compte pas.
- Des tailles différentes d'une ligne à l'autre.
- Une pile alignée à gauche sans numéros (0/4).
- Six couleurs sans lien avec les blocs du deck.

### A4 · Phrase-thèse

#### 1. Rôle et moment

- Elle fixe le bénéfice juste après une démo ou un chiffre ; elle pose la thèse à l'ouverture ; elle affiche un engagement. Présente dans 6/8 (v5, v6, v1, v2, v7, v3), plus une variante dans v4.
- Le texte écrit est, mot pour mot, ce qui est dit au même moment (6/6).
- Environ 15 à 20 par keynote en direct (v5, v6), 4 à 8 en préenregistré (v2, v3).

#### 2. Composition canonique

| Zone | x | y | l | h | Règle |
|---|---|---|---|---|---|
| phrase | 12 | 36 | 76 | 25 | 1 ou 2 lignes, centrées ; centre du bloc à 48,5 % H ; ligne la plus longue sur 66 à 74 % L ; seconde ligne à 55-70 % de la première |

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|        +----------------------------------------------+        |
|        |             Une phrase qui tient             |        |
|        |              sur deux lignes .               |        |
|        |                                              |        |
|        +----------------------------------------------+        |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `aplat`, `degrade`, `mot-accent`, `definition`, `sur-image`, `sourdine` ou `enchainee`. Sans variante : comme `aplat`. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **aplat** (phrase en aplat) | 4/8 (v5, v6, v1, v2) | Blanc sur noir, ou noir sur gris clair ; une ou deux lignes. |
| **degrade** (teinte du produit ou de la section) | 2/8 (v3, v7) | La phrase en dégradé : teinte du produit (taupe vers sombre, gris-bleu vers clair) dans v3, dégradé de la section sur deux lignes dans v7. |
| **mot-accent** (un groupe en accent) | 3/8 (v5, v6, v3) | Un groupe de un à trois mots en couleur (v3), en italique (v6), ou le mot-vedette en couleur (v5). Toujours sur noir. |
| **definition** (article de dictionnaire) | 1/8 (v5) | Le mot-vedette en capitales d'accent avec sa nature, puis la définition sur deux lignes, le tout aligné à gauche. |
| **sur-image** (matière sombre) | 2/8 (v2, v4) | La phrase blanche posée sur une matière sombre (fumée) ou un gros plan du produit. |
| **sourdine** (phrase grise) | 1/8 (v2) | La phrase en gris secondaire sur clair, pour dire le calme ou la discrétion. |
| **enchainee** (phrases à la même place) | 1/8 (v5) | Plusieurs phrases courtes se remplacent, une par idée, à la même place. |

#### 4. Contenu visuel

- Aucun visuel, sauf **sur-image** : matière ou gros plan à fond perdu, sombre, peu contrasté, le détail sur les bords ; la phrase sur la zone calme.
- **Accent** : un groupe de mots au plus, ou le point final, ou le dégradé. Jamais deux.

#### 5. Typographie

- Corps, interligne et coupure des lignes : `style-visuel.md` §3 A4.
- **definition** : mot en capitales demi-grasses de 24 pt, en accent ; définition de 40 pt, alignée à gauche à 14 % L.
- **sur-image** : même corps, blanc. v4 pose sa phrase sur une ligne plus petite (cap ≈ 4 % H) : c'est une signature de film, pas un défaut à reprendre.
- L'italique de v6 passe, dans la skill, par la couleur d'accent (convention).

#### 6. Apparition et animation

- Fondu au moment où la phrase est dite (6/6).
- **enchainee** : fondu enchaîné à la même place, ou une slide par phrase avec morphose.
- **sur-image** : l'image avec la slide, la phrase au clic (convention).

#### 7. Brief du visuel et repli

- La phrase (3 à 8 mots) se propose en `[À VALIDER]`. Elle ne contient aucun nombre.
- **sur-image** : image 16:9, JPEG, 1920 × 1080 au moins ; matière ou détail du produit ; sombre (luminance moyenne sous 25 %) ; centre sans détail ; sans texte.
- **Repli dessiné** : l'aplat. sur-image → aplat sombre et deux halos neutres très flous.

#### 8. À éviter

- Plus de 8 mots (10 au plus) ; trois lignes.
- Un chiffre dans la phrase : c'est un A5. Un superlatif sans preuve devant un public qui en demande (`publics.md`).
- Guillemets, puces, pictogrammes.
- Deux groupes en accent ; un accent et un dégradé ensemble.
- Une dernière ligne d'un seul mot.

### A7 · Liste sans puces

#### 1. Rôle et moment

- Elle énumère des bénéfices, ou annonce le plan d'un sous-chapitre. Présente dans 7/8 (pas v3).
- Les lignes arrivent une à une, au rythme de la voix, dans 6/8 ; v8 les affiche en bloc.
- Moment : après l'annonce d'une fonction, pour dire ce qu'elle apporte ; ou en fin de bloc, pour lister ce qui a été montré.

#### 2. Composition canonique

| Zone | x | y | l | h | Règle |
|---|---|---|---|---|---|
| liste | 10 | 31 | 80 | 33 | 2 à 6 lignes de 2 à 5 mots, centrées ; centre du bloc à 47 % H |

- Corps et interlignes : `style-visuel.md` §3 A7.
- Mesuré : pas de 14,7 % H pour 3 lignes (v1) ; 20 % H pour 2 lignes (v2).

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|      +--------------------------------------------------+      |
|      |                    ligne dite                    |      |
|      |               ligne a venir (53 %)               |      |
|      |               ligne a venir (53 %)               |      |
|      |                                                  |      |
|      +--------------------------------------------------+      |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `centree`, `empilement`, `a-cote-icone`, `a-cote-objet`, `deux-colonnes`, `sur-photo` ou `filet`. Sans variante : comme `centree`. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **centree** (pile qui s'allume) | 4/8 (v5, v1, v2, v4) | Toutes les lignes en place ; la ligne dite est pleine, les suivantes à 53 % (allumage vu dans v2 et v7). |
| **empilement** (pile qui se recentre) | 3/8 (v1, v4, v7) | Une ligne seule au centre, puis deux, puis trois : le bloc se recentre à chaque ajout. |
| **a-cote-icone** (liste et icône) | 3/8 (v6, v8, v4) | Icône à gauche, lignes alignées à gauche dans la colonne libre. Mesuré (v8) : icône de 21 % L × 38 % H centrée à 22 % L ; lignes à 45-47 % L, cap ≈ 4,2 % H, pas de 7,9 % H. |
| **a-cote-objet** (liste et objet ou capture) | 4/8 (v5, v6, v2, v8) | Un objet détouré ou une capture sur une moitié ; la liste de l'autre côté, alignée vers lui (à gauche quand l'objet est à gauche, à droite quand il est à droite). |
| **deux-colonnes** (liste longue) | 2/8 (v4, v8) | 16 à 17 éléments : deux colonnes à côté d'une icône (v4), ou une colonne serrée en petit (v8). Elle se regarde plus qu'elle ne se lit. |
| **sur-photo** (lignes sur le ciel) | 1/8 (v4) | Lignes blanches sur une photo calme du lieu, ajoutées au rythme de la voix. |
| **filet** (liste derrière un filet) | 1/8 (v2) | Petite liste alignée à gauche derrière un filet vertical, au-dessus d'une capture coupée par le bas ; la ligne suivante encore grise. |

#### 4. Contenu visuel

- **centree, empilement** : aucun visuel.
- **a-cote-icone** : une icône au format A2, entière.
- **a-cote-objet** : objet détouré ou capture, entier ; un objet peut sortir du cadre côté bord (A9) ; aucune ombre sur fond sombre, ombre de contact très douce sur fond clair.
- **sur-photo** : photo calme à fond perdu (ciel), le sujet sur les bords.
- **Accent** : aucun sur les lignes (`style-visuel.md` §3 A7). La couleur vient de l'icône ou de l'objet.

#### 5. Typographie

- **centree, empilement** : `style-visuel.md` §3 A7.
- **a-cote-icone, a-cote-objet** : 24 pt, k = 1,8, aligné à gauche (`style-visuel.md` §3 A9, variante icône).
- **deux-colonnes** : 20 pt, k = 1,4, deux colonnes de 28 % L.
- **filet** : 14 pt, k = 1,4 ; filet de 1 pt en secondaire.
- Ligne à venir : secondaire à 53 %.

#### 6. Apparition et animation

- **Allumage** (v2, v7) : toutes les lignes posées ; à chaque clic, la ligne suivante passe du secondaire au plein. pptx : effet d'accentuation « Couleur du texte », ou deux états par morphose.
- **Empilement** (v1, v4, v7) : une slide par état ; la nouvelle ligne entre en fondu et le bloc se recentre (morphose).
- **En bloc** (v8, 1/8) : pour les longues listes (deux-colonnes).
- **a-cote** : l'objet ou l'icône d'abord, puis les lignes.

#### 7. Brief du visuel et repli

- Les lignes : 2 à 6, 5 mots au plus ; elles se proposent en `[À VALIDER]`.
- **a-cote-icone** : comme A2 (SVG, ou PNG transparent de 1024 × 1024 px au moins).
- **a-cote-objet** : PNG transparent de l'objet, 2000 px de haut au moins, vue de face ou de trois quarts ; ou capture PNG à la résolution native, sans donnée personnelle.
- **sur-photo** : photo 16:9, 1920 × 1080 au moins, ciel ou mur calme sur la bande 25-70 % H.
- **Repli dessiné** : icône → tuile de repli d'A2 ; capture → interface schématique (`style-visuel.md` §5.2) ; objet → silhouette simple ; photo → aplat et deux halos.

#### 8. À éviter

- Puces, tirets, numéros.
- Plus de 6 lignes, sauf la liste longue, qui devient un mur.
- Une ligne de plus de 5 mots.
- L'accent sur une ligne ; toutes les lignes en gris.
- Des lignes alignées à gauche au milieu d'une slide vide : le corpus ne les aligne à gauche que contre un objet.

### A8 · Liste à coches

#### 1. Rôle et moment

- Argument de confiance (vie privée, sécurité), promesse, ou récap d'un service. Présente dans 3/8 (v5, v7, v4).
- Moment : quand on oppose ce qui manque à ce qu'on apporte (v5, v7), ou en fin de bloc comme fiche récap déjà cochée (v5).

#### 2. Composition canonique

| Zone | x | y | l | h | Règle |
|---|---|---|---|---|---|
| pictogrammes | 21 | 30 | 5,5 | 38 | un par ligne, haut de 1,1 cap, posé sur la ligne de base |
| lignes | 28 | 30 | 52 | 38 | 3 à 6 lignes, alignées à gauche dans un bloc centré ; centre du bloc à 47 % H |

- Corps, interligne et taille du pictogramme : `style-visuel.md` §3 A8.
- Mesuré (v4) : 3 lignes, pas de 14 % H ; bloc de 5,5 à 88 % L quand les lignes sont longues.

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|             (v)  ligne 1                                       |
|                                                                |
|             (v)  ligne 2                                       |
|                                                                |
|             (v)  ligne 3                                       |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `coche-par-ligne`, `cercles-puis-coches`, `risque-puis-reponse`, `picto-par-ligne` ou `sur-contenu`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **coche-par-ligne** | 2/8 (v7, v4) | Chaque ligne arrive avec sa coche ; la dernière encore pâle pendant son entrée (v4). |
| **cercles-puis-coches** | 1/8 (v5) | Des cercles vides devant chaque ligne (ce qui manque), puis toutes les coches ensemble, sur la phrase de promesse. |
| **risque-puis-reponse** | 1/8 (v7) | Une slide de risques, chacun avec un triangle d'alerte ; puis les réponses, chacune avec sa coche, à la même place. Vu aussi : une liste dont chaque ligne est barrée d'une croix (v7). |
| **picto-par-ligne** | 1/8 (v5) | Un pictogramme différent par ligne, chacun dans sa couleur ; la liste est un leitmotiv repris à la fin de 4 blocs. |
| **sur-contenu** | 1/8 (v5) | La liste cochée posée sur une image de contenu assombrie, en récap ; ou qui s'efface sur les appareils. |

Vu une fois, en transition : la liste bascule en perspective et sort du cadre (v5). Elle reste à faire à la main.

#### 4. Contenu visuel

- **Pictogrammes** dessinés au trait, dans l'accent : un cercle fin avec une coche du même trait dedans (3/3 : v5, v7, v4) ; un cercle vide au trait ; un triangle d'alerte (v7) ; une croix dans un cercle, en gris (v7). Le corpus ne pose jamais de pastille pleine.
- Trait du cercle ≈ 9 % de son diamètre ; la coche a le même trait (mesuré sur 2 cercles de v4 à 960 px). Pas d'ombre, pas de halo.
- **picto-par-ligne** : dans la skill, tous les pictogrammes dans l'accent (une seule couleur, `style-visuel.md` §4.1).
- **sur-contenu** : image à fond perdu, voile sombre de 50 à 70 %.
- **Accent** : les pictogrammes seuls. Le texte reste dans la couleur du texte.

#### 5. Typographie

- Mesures : `style-visuel.md` §3 A8. **picto-par-ligne** : 30 pt pour 6 lignes.
- v7 passe le texte des coches en dégradé (1/8) : non retenu.

#### 6. Apparition et animation

- **coche-par-ligne** : une ligne et sa coche par clic, en fondu.
- **cercles-puis-coches** : clic 1, les lignes et leurs cercles vides ; clic 2, toutes les coches ensemble (zoom ou fondu de 0,3 s).
- **risque-puis-reponse** : deux slides à la même place ; morphose des pictogrammes et du texte.
- **picto-par-ligne** : ligne par ligne, puis la même liste en reprise à la fin de chaque bloc.

#### 7. Brief du visuel et repli

- 3 à 6 lignes de 2 à 5 mots. Elles se proposent en `[À VALIDER]`, sauf les engagements (vie privée, garanties), que l'utilisateur valide lui-même.
- Aucun visuel à fournir : le moteur dessine cercles, coches, alertes et croix.
- **picto-par-ligne** : 3 à 6 pictogrammes SVG monochromes au trait ; sinon la coche du moteur sur chaque ligne.
- **sur-contenu** : image 16:9, 1920 × 1080 au moins ; sinon l'aplat.

#### 8. À éviter

- Coches de plusieurs couleurs, emoji, pictogrammes pleins et lourds.
- Une pastille pleine ; un pictogramme plus haut que 1,2 cap.
- Une coche devant une ligne `[À FOURNIR]` : la case reste vide (règle du moteur).
- Alertes et coches sur la même slide : v7 les sépare en deux slides.
- Le texte en accent.

### A17 · Citation ou témoignage

#### 1. Rôle et moment

- Une preuve sociale que l'orateur lit à voix haute : presse, partenaire, client. Présente dans 3/8 (v5, v6, v1), plus une citation d'auteur en ouverture (v3, variante).
- Aucune citation de presse ou de partenaire après 2020 (0/5) : la preuve passe ensuite par les murs, les classements sourcés et les films.
- Moment : ouverture de section (v5, v1), ou juste après un lancement, en série de deux (v6).

#### 2. Composition canonique

| Zone | x | y | l | h | Règle |
|---|---|---|---|---|---|
| citation | 9,2 | 33 | 76 | 24 | 2 à 4 lignes en demi-gras, alignées à gauche ; bloc centré à 50 % H |
| source | 9,2 | 62 | 76 | 6 | regular, secondaire, à 0,75 fois la cap ; haut des capitales 9,5 % H sous la dernière ligne de base |

- Mesuré : bord gauche à 8,4-9,2 % L (v1, 2 images). Deux lignes : cap ≈ 6,4 % H. Cinq lignes : cap ≈ 5 % H, ligne la plus longue à 80 % L (v1).

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|      +-----------------------------------------------+         |
|      | Citation de deux                              |         |
|      | a quatre lignes                               |         |
|      +-----------------------------------------------+         |
|                                                                |
|      Prenom Nom, organisation                                  |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `courte`, `longue`, `source-accent` ou `centree-signature`. Sans variante : comme `courte`. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **courte** (2 à 3 lignes) | 2/8 (v1, v6) | Grand corps ; source grise une ligne dessous. |
| **longue** (4 à 5 lignes) | 3/8 (v5, v6, v1) | Corps réduit (cap ≈ 5 % H), même alignement, ligne la plus longue jusqu'à 80 % L. |
| **source-accent** | 1/8 (v5) | La source en petites capitales d'accent, collée sous la citation. |
| **centree-signature** | variante v3, non comptée | Citation courte centrée, en petit, entre guillemets ; la signature arrive dessous un temps après. |

Guillemets : aucun sur les citations de presse et de partenaire (0/3 keynotes, 7 images) ; seulement sur la citation d'auteur de v3.

#### 4. Contenu visuel

- Aucun : ni portrait, ni logo, ni photo, ni guillemet décoratif (0/3). Le texte est le visuel.
- Fond : aplat sombre (3/3, et v3).
- **Accent** : aucun ; ou la source (v5), qui est alors le seul accent.

#### 5. Typographie

- Mesures : `style-visuel.md` §3 A17.
- **longue** : 28 pt (plancher), source de 20 pt.
- **source-accent** : capitales demi-grasses de 18 pt, en accent.
- **centree-signature** : 24 pt centré ; source de 20 pt. La skill garde la police de texte du thème (la seule police à empattements du corpus est celle de v3).

#### 6. Apparition et animation

- Citation et source entrent ensemble et restent le temps de la lecture (3/3).
- **centree-signature** : la citation seule, puis la signature au clic.

#### 7. Brief du visuel et repli

- Le texte exact (15 à 25 mots, 30 au plus), le nom, la fonction, l'organisation, la date et l'accord de la personne. Un témoignage ne se propose jamais en `[À VALIDER]` : il se fournit (deck-spec).
- Aucun visuel à fournir.
- **Repli** : les marqueurs `[À FOURNIR : citation]` et `[À FOURNIR : source]`, estompés, au corps de leur champ. Ni faux texte, ni barres grises.

#### 8. À éviter

- Un témoignage inventé, reformulé ou raccourci sans l'accord de son auteur.
- Guillemets géants, italique, portrait, logo de la source.
- Une citation de plus de 2 lignes centrée.
- Plus de 30 mots ou plus de 5 lignes.
- Deux accents (la source et un mot de la citation).

### A21 · Synthé nom et fonction

#### 1. Rôle et moment

- Il nomme un intervenant à sa première apparition. Présent dans 6/8 : tous les préenregistrés (6/6), aucun direct (0/2). Jamais pour l'hôte (0/8).
- Une seule fois par intervenant, et pas forcément pour tous (v1 : 17 synthés pour 20 intervenants).
- En direct, un invité extérieur reçoit une carte sur l'écran à la place (v5, v6) ; v7 l'intègre à sa slide.
- Dans un deck : sur la slide-photo de la première prise de parole d'un intervenant, ou sur une vidéo. Avec `meta.contexte` à `direct`, pas de synthé : l'orateur précédent dit le nom.

#### 2. Composition canonique

| Zone | x | y | l | h | Règle |
|---|---|---|---|---|---|
| photo | 0 | 0 | 100 | 100 | à fond perdu |
| orateur (dans la photo) | 40 | 15 | 32 | 85 | au centre ou du côté opposé au synthé |
| nom | 5,4 | 80,5 | 45 | 4,5 | ligne de base à 84,4 % H ; cap de 2,8 à 3 % H |
| fonction | 5,4 | 86,4 | 45 | 4,5 | ligne de base à 90,3 % H ; même corps que le nom |

```
+----------------------------------------------------------------+
|................................................................|
|................................................................|
|................................................................|
|..........................+------------------+..................|
|..........................|..................|..................|
|..........................|..................|..................|
|..........................|..................|..................|
|..........................|..................|..................|
|..........................|..................|..................|
|..........................|..................|..................|
|..........................|.....ORATEUR......|..................|
|..........................|..................|..................|
|..........................|..................|..................|
|..........................|..................|..................|
|...Prenom Nom.............|..................|..................|
|..........................|..................|..................|
|...Fonction...............|..................|..................|
|..........................+------------------+..................|
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `gauche`, `droite`, `double`, `sur-clair`, `carte-invite` ou `carte-portrait`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **gauche** | 6/8 (v1, v2, v7, v8, v3, v4) | Synthé en bas à gauche ; la personne au centre ou à droite. Position par défaut. |
| **droite** | 5/8 (v2, v3, v4, v7, v8) | Synthé en bas à droite, aligné à droite (bord droit à 94,7 % L), quand la personne est à gauche. |
| **double** | 1/8 (v4) | Deux personnes dans le plan, deux synthés : un à gauche, un à droite, chacun sous sa personne. |
| **sur-clair** | 1/8 (v8) | Sur un décor clair, le synthé passe en gris foncé. |
| **carte-invite** | 2/8 (v6, v7) | Sur la slide : le logo de l'organisation invitée, puis le nom en demi-gras et la fonction en gris, centrés. |
| **carte-portrait** | 1/8 (v5) | Le logo à gauche, un portrait noir et blanc à droite, sans nom écrit. |

#### 4. Contenu visuel

- **La photo** : l'intervenant en situation, en plan large (en pied, de 1/4 à 1/2 de la hauteur) ou en plan taille, dans un lieu lié au sujet ; lumière naturelle ; décor net ou légèrement flou derrière. Plein cadre, sans cadre ni coins.
- La personne est du côté opposé au synthé ; le bas de l'image est calme (sol, mur).
- Aucun bandeau, aucun fond, aucune ombre sous le texte (6/6).
- **carte-invite** : logo monochrome centré sur l'aplat. **carte-portrait** : portrait noir et blanc, fondu dans le noir du côté du logo.
- **Accent** : aucun.

#### 5. Typographie

- Mesures : `style-visuel.md` §3 A21 (nom et fonction au même corps, en blanc).
- **sur-clair** : couleur du texte (gris foncé), même corps.
- **carte-invite** : nom de 22 pt en demi-gras, fonction de 18 pt en regular secondaire, centrés sous le logo (convention tirée de 2 images).
- La fonction s'écrit en clair, sans abréviation maison.

#### 6. Apparition et animation

- Fondu 2 à 5 s après l'entrée de la personne dans le champ ; tenu 4 à 6 s ; sortie en fondu (l'analyse du corpus, A21). v7 montre la personne déjà là et le synthé pas encore.
- pptx : entrée en fondu « après la précédente », délai de 2 s ; sortie en fondu « après la précédente », délai de 5 s.
- **double** : les deux synthés entrent et sortent ensemble.

#### 7. Brief du visuel et repli

- **Photo** : 16:9, JPEG, 1920 × 1080 au moins ; plan large ou plan taille ; la personne sur le tiers droit si le synthé est à gauche (l'inverse sinon), regard vers le centre ou la caméra ; le bas de l'image calme, assez sombre pour un texte blanc à 4,5:1 (ou assez clair pour un texte sombre) ; aucun texte ni logo dans l'image ; droit à l'image signé.
- Le nom et la fonction exacts. Une fonction inconnue reste vide, jamais un marqueur répété (deck-spec).
- **carte-invite** : le logo de l'organisation, SVG ou PNG transparent monochrome.
- **Repli dessiné** : aplat un peu plus clair que le fond et deux halos neutres très flous (`style-visuel.md` §5.2), sans silhouette ni visage ; nom et fonction dans la couleur du texte. carte-invite sans logo → `[À FOURNIR : logo]` à sa place.

#### 8. À éviter

- Bandeau, cartouche, fond flou ou ombre derrière le texte.
- Un synthé pour l'hôte, ou répété à chaque passage.
- Le synthé du côté de la personne : le texte tombe sur son corps.
- Nom et fonction à deux corps différents ; tout en capitales ; logo de l'entreprise dans le synthé.
- Un visage dessiné ou généré pour combler une photo qui manque.

## 5. Chiffres et preuves

Les slides qui prouvent : un chiffre, un écart, un système en parties, l'abondance, l'adoption. Images regardées : 95, plus 9 extraites des vidéos.

### A5 · Gros chiffre + libellé

#### 1. Rôle et moment

- La preuve d'un bénéfice, juste après son énoncé (l'analyse du corpus). Dans la séquence d'annonce, il suit la fonction ou la démo ; la phrase-thèse (A4) peut venir juste après lui.
- Présence : 7/8 (v5, v6, v1, v2, v7, v3, v4). Absent de v8, où les chiffres sont seulement dits.
- Il vient en série dans les événements produits : 3/8 (v2, v3, v4), jusqu'à 9 pour un seul produit (v2). Rare aux conférences logicielles récentes : 3 en 1 h 44 (v7).
- La base de comparaison est écrite dans le libellé : 2/8 en règle (v3, v4), 2/8 en partie (v2, v7).

#### 2. Composition canonique : « centre »

Mesuré sur v1, v3, v7 : capitales du chiffre de 36,1-36,9 à 63,1-63,3 % H, libellé de 77-78 à 82 % H, tout centré sur 50 % L.

| Zone | x | y | l | h | Note |
|---|---|---|---|---|---|
| Surtitre (facultatif) | 10 | 26,3 | 80 | 4,3 | gris, regular ; base à 0,25 cap au-dessus du chiffre |
| Chiffre | 10 | 37,1 | 80 | 25,9 | une ligne ; centre des capitales à 50 % H ; plancher 110 pt |
| Libellé | 8 | 77,9 | 84 | 4,3 | demi-gras, couleur du texte ; centre à 80 % H |
| Source | 8 | 85,8 | 84 | 2,0 | selon le public |

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|               surtitre facultatif · 24 pt · gris               |  base ≈ 30,6 % H
|                                                                |
|      ####################################################      |  haut des capitales 37 % H
|      ############ CHIFFRE · 144 pt · dégradé ############      |
|      ####################################################      |  centre 50 % H
|      ########## une ligne, ajusté dans 80 % L ###########      |
|      ####################################################      |  base 63 % H
|                                                                |
|                                                                |
|               libellé · 24 pt · couleur du texte               |  centre 80 % H
|                         source · 11 pt                         |  ≈ 86 % H
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `centre`, `bloc`, `a-cote`, `sur-photo`, `objet-anneau`, `objet-jauge` ou `contour`. Sans variante : comme `centre`. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **centre** (canonique) | 5/8 : v1, v3, v4, v5, v7 | chiffre au milieu, libellé loin dessous (77-82 % H) |
| **bloc** | 2/8 : v2, v6 | libellé collé sous le chiffre ; le bloc entier se centre (mesuré v2 : chiffre 33,9-56,4 % H, libellé 62,8-66,9 % H) ; deux lignes de libellé possibles |
| **a-cote** | 3/8 : v2, v4, v6 | un visuel occupe la moitié gauche (écran coupé par le bord : 0-55,8 % L × 5,6-94,2 % H en v2 ; schéma entier : 11-49 % L en v4) ; chiffre et libellé centrés sur 75 % L, en bloc ; chiffre plus petit (cap 16 à 22 % H) |
| **sur-photo** | 2/8 : v4, v5 | chiffre blanc sur une photo plein cadre très floutée (v4) ou sur une carte sombre (v5) ; chiffre très large (cap ≈ 31 % H, 84 % L en v4) ; libellé à 72-76 % H |
| **objet-anneau**, **objet-jauge** | 1/8 : v4 | le chiffre est dessiné dans un objet : anneau lumineux avec halos (33-67 % L × 20-80 % H), jauge pleine (36-67 % L × 37-63 % H), cote tracée sur un écran, pictogramme glissé dans la phrase |
| **contour** | 1/8 : v6 | chiffre au trait lumineux, sans remplissage, dans la couleur du chapitre ; libellé plein dessous ; le chiffre peut changer sur place |

Hors slide : le même chiffre filmé avec l'orateur à côté, sur l'écran du décor (v2, v5, v6). C'est un plan de scène (A22, A23), pas une variante.

#### 4. Contenu visuel

- **Centre, bloc, contour** : aucun visuel. Le chiffre est l'image. Fond plein du bloc.
- **Couleur du chiffre** : dégradé horizontal dans 4/8 (v2, v3, v4, v7) ; blanc ou noir uni dans 2/8 (v1, v4) ; couleur du service, unie, dans 1/8 (v5) ; trait lumineux dans 1/8 (v6). La skill garde le dégradé `accent → accent2` (`style-visuel.md` §4.2), sauf sur photo.
- **A côté** : capture dans un appareil générique, produit détouré ou schéma au trait. Cadrage : l'écran ou le produit **sort par le bord gauche** (v2) ; un schéma reste entier (v4). Ombre de contact très douce sur fond clair seulement ; rien sur fond sombre.
- **Sur photo** : photo à fond perdu, du lieu ou de l'usage, défocalisée au point de n'être qu'une ambiance (v4 : bibliothèque, arches, plage) ; voile sombre pour que le blanc tienne 4,5:1. Chiffre et libellé blancs.
- **Objet** : forme simple en accent. Anneau : trait épais, deux ou trois anneaux flous autour (halo). Jauge : pilule pleine, chiffre en `fond_sombre` dedans. Le vert de v4 vient de la batterie (3/8) : la skill prend l'accent de l'utilisateur.
- **Accent** : sur le chiffre seul. Le libellé reste dans la couleur du texte (`style-visuel.md` §3 A5).

#### 5. Typographie

- Mesures : `style-visuel.md` §3 A5.
- **bloc** : centre du chiffre à 45,5 % H, haut du libellé à 63 % H, interligne k = 1,6 (`style-visuel.md` §3 A5, mise en page b).
- **a-cote** : chiffre 116 pt (plancher 88) dans une colonne de 3,2 in ; libellé 22 pt, une ou deux lignes. Mesuré : cap 22 % H (v2), 16 % H (v4).
- **sur-photo** : chiffre 144 pt, blanc uni ; libellé 24 pt blanc. Rien sous 20 pt sur une photo.
- **objet** : anneau, chiffre 72 pt et unité 34 pt dedans (mesuré : 13 et 6 % H de cap) ; jauge, chiffre 54 pt.
- **contour** : contour 2,5 pt (convention), même corps que « bloc ».

#### 6. Apparition et animation

- Le chiffre arrive **flou et zoomé**, puis se pose : 2/8 (v3, v4). Moteur : entrée Zoom 0,4 s.
- Le libellé arrive en second : 1/8 (v1). Le libellé arrive d'abord, seul : 1/8 (v2).
- Le chiffre change sur place (avant / après) : 1/8 (v6). Moteur : deux slides et Morphose.
- Anneau : il se trace (roue) ; jauge : elle se remplit (balayage). Convention, d'après les états vus en v4.

#### 7. Brief du visuel et repli

- **Toujours** : le chiffre, son unité, la base de comparaison et la source. Aucun visuel pour « centre », « bloc », « contour », « objet ».
- **a-cote** : une capture PNG d'au moins 1 600 px de large (l'écran seul, sans bord d'appareil), ou un produit détouré en PNG à fond transparent, vu de trois quarts ou de face, d'au moins 2 000 px de haut.
- **sur-photo** : une photo JPEG 16:9 d'au moins 1 920 × 1 080 (3 840 × 2 160 de préférence), sans texte, avec un centre calme ; le moteur la floute et l'assombrit.
- **Repli** : chiffre manquant = `[À FOURNIR : libellé]` au corps du chiffre, estompé, filet pointillé. Capture manquante = interface schématique (`style-visuel.md` §5.2). Photo manquante = variante « centre ». L'anneau d'un repli est complet : un arc partiel dirait une valeur. La jauge d'un chiffre manquant reste vide (liseré d'accent, sans remplissage) : le marqueur gris se lit sur le fond, pas sur l'accent.

#### 8. À éviter

- Deux chiffres sur la slide : un seul chiffre géant dans 7/8, toutes les keynotes qui ont un A5.
- Un libellé gris : il est dans la couleur du texte sur les images mesurées.
- Une note ou un astérisque sous le chiffre : aucune note dans 7/8, toutes les keynotes qui affichent un chiffre (la source suit le public, `publics.md`).
- Le dégradé sur une photo, ou sur autre chose que le chiffre.
- Un chiffre posé dans le tiers haut avec du vide dessous, ou coupé sur deux lignes.
- Un libellé de plus de 9 mots.

### A6 · Graphique comparatif

#### 1. Rôle et moment

- La preuve chiffrée d'un écart, dans la partie technique (puce, navigateur, performance), ou le classement de marché au début d'une keynote (v7, v8).
- Présence : 6/8. Graphiques : v6, v1, v2, v4. Classement : v7, v8. Absent : v5, v3 (v3 passe tout par le gros chiffre).

#### 2. Composition canonique : « barres »

Mesuré sur v1 : titre centré, haut des capitales à 12,2 % H ; barres de 15 à 85 % L, épaisses de 1,1 % H, à 51 et 65,7 % H (pas de 14,5 % H) ; chaque nom **au-dessus** de sa barre, calé à gauche sur son départ (15,2 % L) ; l'écart au-dessus du bout de la barre de soi, calé à droite (84,8 % L) ; l'autre en gris à 42 % environ. v4 suit la même règle avec 3 barres, sur un écran du décor.

| Zone | x | y | l | h | Note |
|---|---|---|---|---|---|
| Titre | 6 | 8,9 | 88 | 5,0 | la grandeur mesurée, centrée |
| Nom de soi | 15 | 44,5 | 45 | 4,1 | au-dessus de sa barre |
| Écart | 55 | 44,5 | 30 | 4,1 | calé à droite sur 85 % L ; seule valeur écrite |
| Barre de soi | 15 | 50,5 | 70 × v/max | 1,1 | accent uni, bouts ronds |
| Nom de l'autre | 15 | 59 | 45 | 4,1 | secondaire |
| Barre de l'autre | 15 | 65 | 70 × v/max | 1,1 | gris à 45 % ; barres 3 et 4 au même pas |
| Sens de lecture | 15 | 72 | 70 | 2,9 | facultatif, en mots |
| Source | 6 | 92 | 88 | 2,0 | selon le public |

```
+----------------------------------------------------------------+
|                                                                |
|              Titre : la grandeur mesurée · 28 pt               |  haut des capitales 8,9 % H
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|          Soi · 23 pt                    écart · 23 pt          |  44,5 % H
|          =============================================         |  barre de soi, accent, 1,1 % H
|          L'autre · 23 pt · gris                                |  59 % H
|          ------------------------------                        |  barre de l'autre, gris 45 %
|                                                                |
|          sens de lecture en mots · 16 pt (facultatif)          |  72 % H
|                                                                |
|                                                                |
|                         source · 11 pt                         |  92 % H
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `barres`, `deux-axes`, `anneaux`, `frise` ou `classement`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **barres** (canonique) | 2/8 : v1, v4 | 2 ou 3 barres horizontales fines, nom au-dessus, écart au bout |
| **deux-axes** | 2/8 : v1, v2 | deux axes en L sans graduation, nommés en mots avec leur sens de lecture ; courbes (v2) ou zones de position (v1) ; nom au bout de chaque courbe ; repère pointillé d'accent (mesuré v2 : titre à 7,5 % H, axe vertical à 19,8 % L, noms d'axes en cap 2,9 % H, gris sombre) |
| **anneaux** | 1/8 : v6 | deux anneaux de part côte à côte, valeur et nom dedans, titre à droite ; les deux valeurs écrites |
| **frise** | 1/8 : v2 | les générations sur une ligne presque plate, deux périodes aux bouts ; la tuile de soi, lumineuse, saute au-dessus ; flèche et écart en accent |
| **classement** | 2/8 : v7, v8 | tableau de rangs (8 rangées × 3 périodes) rempli de logos, soi au rang 1 ; source en petit en bas à droite (mesuré v8 : 97-98 % H, 87-99 % L) ; sombre (v7) ou clair (v8) |

#### 4. Contenu visuel

- Tout se dessine : filets, barres, courbes, anneaux. Aucune image, sauf les logos du classement et la tuile de soi de la frise.
- **Soi en couleur, l'autre en gris** : 3/8 (v1, v2, v4) ; l'autre dans une teinte pâle : 1/8 (v6). Le corpus met parfois un dégradé sur soi (v1, v2) ; la skill garde l'accent uni et le gris à 45 % (`style-visuel.md` §4.2).
- Aucune graduation chiffrée : 4/8 (les 4 keynotes à graphique). Les axes portent des mots.
- Profondeur : aucune, sauf la **frise** : la tuile de soi a un liseré lumineux qui déborde en halo (v2). Pas d'ombre, pas de 3D, pas de quadrillage (une seule grille, très sombre, sous les zones de v1).
- Fond : sombre dans 5/8 (v6, v1, v2, v4, v7), clair dans 1/8 (v8).
- Accent : la barre, la courbe ou l'anneau de soi, et l'écart. Rien d'autre.

#### 5. Typographie

- Mesures : `style-visuel.md` §3 A6.
- Titre : il **nomme la grandeur** ou le classement, il ne conclut pas : 6/8 (v6, v1, v2, v4, v7, v8). La conclusion est l'écart.
- **deux-axes** : noms d'axes 16 pt, sens de lecture 10 pt dessous (mesuré : cap 2,9 et 1,6 % H). Noms des courbes 16 pt.
- **anneaux** : valeur 40 pt, nom 14 pt, titre 40 pt à droite (convention, d'après une mesure sur la scène).
- **classement** : titre 32 pt (mesuré : cap ≈ 5,8 % H), rangs 16 pt, périodes 14 pt, source 9 pt.

#### 6. Apparition et animation

- Construction en 2 à 4 temps : 3/8 (v6, v1, v2). v4 n'est vu que dans son état final.
- Ordre : l'autre d'abord, puis soi, puis les repères : 1/8 (v2). Soi d'abord, puis l'autre : 1/8 (v6). Par défaut, la skill garde « l'autre, puis soi ».
- Barres : la barre pousse depuis la gauche (balayage, 0,6 s, convention).
- Classement : d'un bloc, l'orateur lit la première rangée (v7, v8).

#### 7. Brief du visuel et repli

- **À fournir** : chaque valeur (pour la longueur), l'écart à écrire, la source, le nom de l'autre (nommé ou anonyme selon le public, `publics.md`).
- **classement** : les rangs, les périodes, et un logo monochrome par service (SVG, ou PNG transparent d'au moins 600 px de large).
- **frise** : les périodes et l'écart ; un logo ou un nom pour la tuile de soi.
- **Repli** (sans nombre, sans marque) : barres en filet pointillé gris de même longueur, écart `[À FOURNIR : écart]` ; courbes absentes, remplacées par `[À FOURNIR : courbes]` entre les axes ; anneau vide ; frise sans saut ; classement en noms de texte, rangs et périodes en `[À FOURNIR]`.

#### 8. À éviter

- Une graduation, une légende à part, un quadrillage, une 3D.
- Plus de 4 barres : le corpus en montre 2 ou 3.
- Deux couleurs d'accent, ou un dégradé sur la barre.
- Un titre qui dit la conclusion.
- Une longueur de barre ou une hauteur de saut qui ne vient pas d'une valeur fournie.
- Le nom du concurrent quand le public ne le veut pas (`publics.md`).

### A11 · Schéma à bloc surligné

#### 1. Rôle et moment

- Expliquer de quoi est fait le système avant de chiffrer ses gains : la section « dedans » d'un produit. Un bloc à la fois.
- Présence : 3/8 (v2, v3, v4), les 3 événements produits. Dans le corpus, c'est toujours une puce ; la skill l'étend à tout système en parties (architecture, plateforme, machine, organisation).
- Il précède les chiffres de performance : 3/8 (v2, v3, v4). Il peut porter le chiffre lui-même (variante « schema-chiffre », 1/8).

#### 2. Composition canonique : « legende-laterale »

Mesuré : schéma carré de 31 à 69 % L et de 16,5 à 83,5 % H, centré (v3, v4, ; v2 un peu plus petit : 33-67 % L). Légende : titre en cap 2,4 % H, sous-lignes en cap 1,8 % H, pas de 3,7 % H ; à gauche à 4,4-5 % L (v3, v4) ou 10 % L (v2), à droite calée sur 95 % L ; un filet de 0,6 % H sous le titre, du bord de la légende au bord du schéma.

| Zone | x | y | l | h | Corps | Note |
|---|---|---|---|---|---|---|
| Schéma | 31 | 16,5 | 38 | 67 | — | carré, trait fin gris ; liseré 1,5 pt |
| Nom du système | 32 | 18 | 15 | 4,7 | 26 pt | dans la case du coin haut gauche |
| Bloc allumé | 31,5 | 55 | 18,5 | 28 | — | contour clair, intérieur éclairci, lueur |
| Titre de légende | 4,5 | 53,5 | 24 | 3,2 | 18 pt | au niveau du haut du bloc |
| Filet | 4,5 | 58 | 26,5 | 0,3 | — | 0,75 pt, gris à 45 % |
| Sous-lignes (1 à 5) | 4,5 | 60,5 | 24 | 11 | 14 pt | secondaire ; à droite, alignées à droite sur 95,5 % L |

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                    +---------+-------------+                   |  schéma 31-69 % L × 16,5-83,5 % H
|                    | Nom     |             |                   |  nom dans la case du coin
|                    +---------+             |                   |
|                    |          +---+---+---+|                   |
|                    | +--+     |   |   |   ||                   |
|                    |          +---+---+---+|                   |
|   Titre · 18 pt    |                       |                   |  titre de légende 53,5 % H
|   _________________+----------+            |                   |  filet jusqu'au bord du schéma
|   ligne · 14 pt    |          |            |                   |
|   ligne · 14 pt    |   bloc   |            |                   |  sous-lignes, pas 3,7 % H
|   ligne · 14 pt    |  allumé  |            |                   |
|                    |          |            |                   |
|                    +----------+------------+                   |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `legende-laterale`, `plusieurs-blocs`, `schema-chiffre`, `carte-annotee` ou `carre-halo`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **legende-laterale** (canonique) | 3/8 : v2, v3, v4 | un bloc allumé, sa légende du côté du bloc |
| **plusieurs-blocs** | 3/8 : v2, v3, v4 | 2 ou 3 blocs allumés, une légende par bloc, des deux côtés (v4) ou empilées (v3) ; en v2, les noms sont écrits dans les blocs |
| **schema-chiffre** | 1/8 : v4 | schéma décalé à gauche (centre à 30 % L), chiffre héros à droite (centre à 74,5 % L, cap ≈ 16 % H) avec son libellé |
| **carte-annotee** | 1/8 : v2 | vue de dessus d'un objet réel ; cadres fins autour des composants ; étiquettes au bout de filets verticaux, en haut ou en bas |
| **carre-halo** | 2/8 : v2, v7 | le système réduit à un carré sombre et son nom, entouré d'un halo lumineux ; en v7, une rangée de carrés pour les générations (sur clair). Variante d'introduction : elle n'entre pas dans les 3/8 d'A11 |

#### 4. Contenu visuel

- **Le schéma** : un dessin au trait, monochrome, gris à 30-40 % sur fond sombre, carré, plein de cases de tailles inégales. Fond sombre : 3/8 (les 3 cas).
- **Liseré** : dégradé dans 2/8 (v2, v3), gris dans 1/8 (v4). La skill prend l'accent uni ou le gris : le dégradé reste au chiffre héros.
- **Le bloc allumé** : contour plus clair, intérieur un peu éclairci, légère lueur (halo). C'est l'accent de la slide.
- **Le nom** : dans la case du coin haut gauche, dans le schéma : 3/8 (les 3 cas). Le logo de l'utilisateur peut l'accompagner, jamais un autre.
- **carte-annotee** : une vraie vue de dessus, détourée, sombre, sans ombre ; cadres blancs de 1 pt.
- **carre-halo** : carré presque noir, coins presque vifs (5 % du côté : un composant, pas une icône d'app) ; halo qui déborde de 8 % L autour ; nom au centre.

#### 5. Typographie

- Pas de fiche A11 dans `style-visuel.md`. Mesuré : titre de légende cap 2,4 % H, sous-lignes 1,8 % H, demi-gras puis regular, secondaire pour les sous-lignes.
- **Convention** : 18 pt et 14 pt (cap 3,2 et 2,5 % H). C'est un peu plus gros que le corpus, fait pour la vidéo : en salle, le texte reste au-dessus de 2,5 % H.
- Nom du système : 26 pt demi-gras (mesuré : cap 4 à 5 % H).
- **schema-chiffre** : chiffre 90 pt, libellé 20 pt (règles A5).
- 5 sous-lignes au plus, 4 mots chacune.

#### 6. Apparition et animation

- Le bloc s'allume avec sa légende, au même moment : 3/8 (v2, v3, v4). Le schéma seul d'abord : vu dans 1/8 (v4).
- Le surlignage passe d'un bloc au suivant sur la même image : 3/8 (v2, v3, v4). Moteur : une slide par bloc, Morphose ; repli en fondu.
- **carte-annotee** : une étiquette par clic, avec son cadre et son filet (v2).

#### 7. Brief du visuel et repli

- **À fournir** : le schéma de l'utilisateur en SVG, ou en PNG transparent d'au moins 2 000 × 2 000 px, au trait, d'une seule couleur ; la liste des blocs, chacun avec un titre et 1 à 5 lignes ; le nom du système.
- **carte-annotee** : une photo de dessus (à 90°), détourée, PNG transparent d'au moins 2 400 px de large, et la position des composants à annoter.
- **Repli** : le moteur dessine un plan de blocs au trait (une grille subdivisée de 8 à 12 cases inégales), allume une case et pose la légende ; aucune inscription dans les cases, aucun nombre ; nom en `[À FOURNIR : nom]` s'il manque.

#### 8. À éviter

- La photo ou le rendu d'une vraie puce de marque.
- Des blocs remplis de couleurs différentes.
- Plus d'un bloc allumé par clic, sauf « plusieurs-blocs » (3 au plus).
- Une légende sans filet, un filet en diagonale, une légende de plus de 5 lignes.
- Du texte dans le schéma, hors le nom du coin.

### A15 · Mur d'abondance

#### 1. Rôle et moment

- Dire « il y en a beaucoup » sans détailler. Juste après le bento : 1/8 (v8, le mur de fin de section). À la place d'un nombre dit à l'oral : 1/8 (v7, le mur d'icônes).
- Présence : 6/8 (v5, v6, v1, v7, v8, v3). Absent : v2, v4.
- Il se regarde, il ne se lit pas : c'est voulu.

#### 2. Composition canonique : « vignettes »

Vu sur v1 : vignettes 16:9 d'environ 21 % L × 21,5 % H, gouttière de 1,25 % L et 2,2 % H, coins arrondis, rangées décalées, coupées par les bords. Mesuré sur v8 (cartes) : gouttière 1,25 % L et 2,1 % H.

| Zone | x | y | l | h | Note |
|---|---|---|---|---|---|
| Grille | −4 | −3 | 108 | 106 | 4 rangées, décalées d'un tiers de vignette ; 20 à 24 vignettes visibles |
| Une vignette | 1 | 1 | 21 | 21,5 | image fournie en « couvrir », rayon 1,2 % L, sans texte ajouté |

Les coordonnées négatives ou au-delà de 100 sont voulues : le mur déborde.

```
+----------------------------------------------------------------+
|:::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::|  vignette 16:9 : 21 % L × 21,5 % H
|:::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::|
|                                                                |  gouttière 1,25 % L · 2,2 % H
|::::::::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::|
|::::::::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::|
|::::::::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::|  rangées décalées d'un tiers
|                                                                |
| ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::::::|
| ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::::::|
| ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::::::|  coupées par les 4 bords
|                                                                |
|::::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: ::|
|::::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: ::|
|::::: ::::::::::::: ::::::::::::: ::::::::::::: ::::::::::::: ::|  rayon 1,2 % L, sans ombre
|                                                                |
|:::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::::::::::|
|:::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::::::::::|  aucun texte lisible
|:::::::::: ::::::::::::: ::::::::::::: ::::::::::::: :::::::::::|
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `vignettes`, `icones`, `mots`, `nuage`, `cartes-libelles` ou `forme`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **vignettes** (canonique) | 3/8 : v1, v5, v8 | affiches, couvertures ou jaquettes au format du contenu (16:9, 3:4, 2:3) |
| **icones** | 3/8 : v5, v6, v7 | des dizaines de pastilles identiques (carré arrondi ou cercle, ≈ 7,5 % L), très serrées, rangées décalées d'une demi-pastille ; en v5, des visages |
| **mots** | 3/8 : v6, v7, v8 | lignes justifiées de libellés, petits et gris (v6 : cap 1,8 % H, 5 lignes) ou moyens (v8 : cap 2,9 % H, pas 10,3 % H ; v7 : cap 4,2 % H, deux tons, déborde des bords) |
| **nuage** | 3/8 : v3, v7, v8 | mots épars sur trois plans de profondeur (taille et opacité), coupés par les bords ; en v8, un nom net au premier plan |
| **cartes-libelles** | 1/8 : v8 | 6 × 6 petites cartes blanches (mesuré : 15,2 % L × 14,2 % H), icône en haut à gauche, libellé de 2 lignes en bas |
| **forme** | 1/8 : v5 | la mosaïque découpée en forme simple (un cœur), à côté de l'orateur |

#### 4. Contenu visuel

- **Le contenu de l'utilisateur, en nombre** : vignettes de ses contenus, icônes de ses intégrations, noms de ses fonctions.
- **Cadrage** : le mur d'images touche ou dépasse les bords : 5/8 (v1, v5, v6, v7, v8), toutes les keynotes qui ont un mur d'images, hors variante « forme ». Le mur de mots garde une marge de 3,6 à 6 % L : 2/8 (v6, v8) ; il déborde : 1/8 (v7).
- **Traitement** : coins arrondis, ni bordure, ni ombre, ni reflet ; gouttière fine et régulière. Profondeur seulement dans le **nuage** : trois tailles et trois opacités (plein, environ 70 %, environ 30 %), vues sur v3.
- **Accent** : aucun dans les murs d'images (exception admise à la règle d'un seul accent : les images gardent leurs couleurs, `style-visuel.md` §4.1). Mots : couleur secondaire, ou deux tons alternés (v7). Nuage : une seule teinte.
- Fond : celui du bloc (sombre ou clair).

#### 5. Typographie

- `style-visuel.md` n'a pas de fiche A15. Avec le bento, c'est l'endroit où le texte peut descendre sous 3 % H : il se regarde.
- **mots** : 16 pt (cap 2,9 % H), regular ou demi-gras, pas de 10,3 % H, 3 ou 4 libellés par ligne (mesuré v8). Plancher : 10 pt (v6 mesuré à 1,8 % H).
- **nuage** : 36 / 22 / 13 pt pour les trois plans (convention, d'après v3) ; le nom au premier plan au corps A1 réduit (52 pt).
- **cartes-libelles** : libellé 9 pt, 2 lignes.

#### 6. Apparition et animation

- Défilement lent : 2/8 (v8 cartes qui montent, v7 nuage qui traverse l'écran ). Moteur : deux slides et Morphose sur une grille décalée d'une rangée (8 s), ou une trajectoire lente ; repli : entrée en fondu.
- Ailleurs, le mur est vu fixe, d'un bloc. Une entrée élément par élément : 0/8 sur les images regardées.

#### 7. Brief du visuel et repli

- **vignettes** : 20 à 40 images au même format, d'au moins 640 px de large chacune, sans texte ajouté (JPEG ou PNG).
- **icones** : 40 à 100 icônes carrées PNG d'au moins 256 × 256, sur fond plein ou transparent, toutes au même gabarit.
- **mots, nuage, cartes** : 24 à 40 libellés de 2 à 5 mots (et une icône par carte). Des libellés tirés du brief peuvent se proposer `[À VALIDER]`, sans nombre.
- **Repli** : vignettes et icônes absentes = aplats de quelques nuances voisines du fond, une barre grise par vignette, un pictogramme géométrique par pastille d'icône (une sur neuf teintée d'accent), jamais un écran clair au milieu du mur (`style-visuel.md` §5.2) ; libellés absents = barres arrondies de longueurs variées. Le nuage n'a pas de repli : il passe en « mots » à barres.

#### 8. À éviter

- Une grille qui flotte au centre avec des marges : elle devient un catalogue, ou un bento.
- Un élément lisible, plus gros ou en accent au milieu du mur (sauf le nom du nuage).
- Moins d'une vingtaine d'éléments : le mur ne dit plus « beaucoup ».
- Des formats mélangés, des ombres, des cadres.
- Un nombre écrit sur le mur : il se dit, ou il passe en A5.

### A16 · Logos partenaires

#### 1. Rôle et moment

- La preuve d'adoption, juste après l'annonce d'un standard, d'un service ou d'un partenariat. Une seconde grille plus dense peut suivre pour « encore plus » : 1/8 (v8).
- Présence : 5/8 (v5, v6, v1, v8, v4). Variante dans v7 : un logo seul en plein cadre. Absent : v2, v3.

#### 2. Composition canonique : « grille »

Mesuré sur v8 (5 × 4) : centres des colonnes à 14,5 / 32,3 / 50 / 67,7 / 85,3 % L (pas 17,7 % L), centres des rangées à 17 / 39 / 61 / 82,7 % H (pas 21,9 % H). Les mots-logos font 7 à 11 % L sur 1,4 à 3,3 % H ; les emblèmes 2,8 à 5,2 % L sur 5 à 8 % H : le poids optique est égal, pas la hauteur.

| Zone | x | y | l | h | Note |
|---|---|---|---|---|---|
| Grille | 8,5 | 6 | 83 | 88 | 3 à 5 colonnes ; 2 rangées : centres 38 / 62 ; 3 : 28 / 50 / 72 ; 4 : 17 / 39 / 61 / 82,7 |
| Une case | 9 | 13 | 11 | 8 | boîte du logo au plus ; logo à aire égale (aire cible 0,15 in², convention) |

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                    @@@                   @@@                   |
|      =======       @@@      =======      @@@       =======     |  rangée 1 · centre 17 % H
|                                                                |
|                                                                |
|                               @@@        @@@                   |
|      =======     =======      @@@        @@@       =======     |  rangée 2 · 39 % H
|                                                                |
|                                                                |
|                               @@@                              |
|      =======     =======      @@@      =======     =======     |  rangée 3 · 61 % H
|                                                                |
|                                                                |
|                               @@@        @@@                   |
|      =======     =======      @@@        @@@       =======     |  rangée 4 · 82,7 % H
|                                                                |
|                                                                |  colonnes 14,5 / 32,3 / 50 / 67,7 / 85,3 % L
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `grille`, `ligne`, `logo-seul`, `mur-dense`, `pastilles` ou `soi-au-centre`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

| Variante | N/8 | Ce qui change |
|---|---|---|
| **grille** (canonique) | 4/8 : v1, v5, v6, v8 | 3 à 5 logos par rangée, 2 à 5 rangées, centrés |
| **ligne** | 4/8 : v1, v4, v5, v8 | 2 à 4 logos sur une ligne, plus gros (v8 : 16 à 22 % L × 7,5 à 9,4 % H, centres 18 / 48 / 80 % L) |
| **logo-seul** | 3/8 : v1, v5, v7 | un partenaire en plein cadre, centré, jusqu'à 46 % L |
| **mur-dense** | 3/8 : v5, v6, v8 | 30 à 80 logos serrés ; en v8, la grille de 20 se resserre en 33 |
| **pastilles** | 1/8 : v5 | chaque logo blanc dans une pastille ronde de sa couleur, 3 rangées en quinconce |
| **soi-au-centre** | 1/8 : v1 | son propre logo au centre de l'alliance, rangées en quinconce 3 / 4 / 3 / 4 / 3 ; il arrive d'abord entre deux partenaires |

#### 4. Contenu visuel

- **Logos monochromes** dans la couleur du texte (blanc sur sombre, noir sur clair) : 5/8 (v1, v4, v5, v6, v8), sur toutes les images vues. Seule exception : « pastilles » (1/8, v5).
- **Aucun texte ajouté** : ni titre, ni légende, sur toutes les grilles vues (5/8 : v1, v4, v5, v6, v8).
- **Taille** : elle suit le nombre. 3 logos : 16 à 22 % L de large (v8) ; 6 logos : 10 à 20 % L (v5) ; 20 logos : 7 à 11 % L (v8) ; 60 logos : quelques % (v6).
- **Profondeur** : aucune. Pas d'ombre, pas de tuile, pas de cadre. Fond du bloc, ou fond flou clair (v8).
- **Accent** : aucun.

#### 5. Typographie

- Pas de texte. Mesures de grille : `style-visuel.md` §3 A16 ; la taille des logos suit leur poids optique (§2 ci-dessus).
- Un logo manquant s'écrit en nom : 20 pt demi-gras, secondaire.
- Un surtitre court reste permis par la skill (convention) ; le corpus n'en montre aucun.

#### 6. Apparition et animation

- La grille arrive d'un bloc : 5/8 (v5, v6, v1, v8, v4).
- Une grille plus dense suit pour « encore plus » : 1/8 (v8). Moteur : Morphose de la grille de 20 vers celle de 33.
- Un logo seul, puis une paire séparée par un filet : 1/8 (v5). Son logo entre deux partenaires, puis l'alliance autour : 1/8 (v1).

#### 7. Brief du visuel et repli

- **À fournir** : chaque logo en version monochrome (blanche pour fond sombre, noire pour fond clair), en SVG ou en PNG transparent d'au moins 600 px de large, recadré au ras du dessin ; l'accord des partenaires pour les montrer.
- **soi-au-centre** : le logo de l'utilisateur, dans la même couleur que les autres.
- **Repli** : le nom du partenaire en texte, demi-gras, secondaire, centré dans sa case. Jamais un logo imité ou redessiné. Sans nom ni logo, la case reste vide et l'emplacement passe en `[À FOURNIR : logo]` dans les notes.

#### 8. À éviter

- Des logos en couleurs mélangées (hors « pastilles »).
- Tous les logos à la même hauteur : les mots-logos deviennent énormes, les emblèmes minuscules.
- Un titre du type « ils nous font confiance » au-dessus de la grille : 0/8.
- Plus de 5 logos par rangée en grille standard (au-delà, c'est un « mur-dense »).
- Un cadre, une tuile ou une ombre derrière chaque logo.
- Un logo de client ou de partenaire sans son accord, ou un concurrent présenté comme partenaire.

## 6. Produit et image

Les slides où l'image prend toute la place : l'objet, l'écran, l'intérieur, le produit, la photo ; puis les plans de scène, qui sont de la vidéo. Images regardées : 186.

### A9 · Objet + texte

#### 1. Rôle et moment

- Le détail d'une fonction ou d'une caractéristique : l'objet ou l'écran montre, une à quatre lignes nomment.
- Il vient après le nom de la fonction (A1, A2) ou après l'écran plein cadre (A10) de la même fonction. Il précède la preuve chiffrée (A5) ou le récap (A14).
- Présent dans 7/8 (v5, v6, v2, v7, v8, v3, v4). v1 n'a que la version empilée (variante f).
- Il sert aussi de légende minimale : un nom de fonction ou d'app posé à côté d'un écran (v4, v7, v8).

#### 2. Composition canonique

Objet coupé à gauche, affirmation centrée dans la colonne libre à droite.

| Zone | x | y | l | h | D'où vient la valeur |
|---|---|---|---|---|---|
| Objet (image, fond perdu) | 0 | 0 | 58 à 62 | 100 | mesuré : 0–58 % L (v2), 0–62 % L (v3), fond perdu sur 2 ou 3 bords |
| Affirmation (1 ou 2 lignes) | 66 | 38 | 28 | 24 | mesuré : centre à 79,6–81,1 % L et 49,9–50,6 % H sur 6 images (v3, v4, v7, v8) ; cap 5,8 à 6,1 % H |
| Miroir (objet à droite) | — | — | — | — | mesuré : texte centré à 20,0–20,5 % L (v3, v7) |

```
+------------------------------------------------------------+
|####################################                        |
|####################################                        |
|####################################                        |
|####################################                        |
|####################################                        |
|####################################                        |
|####################################  +------------------+  |
|####################################  |    Affirmation   |  |
|##### OBJET coupe par le cadre #####  |    1-2 lignes    |  |
|######## x 0  l 56-62  h 100 #######  |    centre 80 %   |  |
|####################################  |                  |  |
|####################################  +------------------+  |
|####################################                        |
|####################################                        |
|####################################                        |
|####################################                        |
|####################################                        |
|####################################                        |
+------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `appareil-centre-mot`, `objet-coupe`, `objet-liste`, `objet-chiffre`, `annotee` ou `empilee`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

**a. Appareil centré + mot (`appareil-centre-mot`)** — 3/8 (v4, v7, v8).
- L'appareil reste à sa place d'A10 : 37,5–62,3 % L × 4,4–95,3 % H, centré sur (50, 50) (mesuré, 4 images). Le mot, ou 2 à 3 lignes courtes, se centre dans la marge à 81 % L, cap 5,8 % H (mesuré, 4 images). Le mot est un nom de fonction ou d'app.
- Fond clair (v7, v8) ou noir (v4).

**b. Objet coupé + affirmation (`objet-coupe`)** — 2/8 (v3, v7).
- Le produit en gros plan, ou un portable, sort du cadre par 2 ou 3 bords et couvre 58 à 62 % L. L'affirmation tient en 2 à 4 mots, sur 2 lignes.
- Sur noir, le texte peut prendre un dégradé de la teinte du produit (v3, 1 image) : la skill garde la couleur du texte.

**c. Icône ou objet + liste (`objet-liste`)** — 4/8 (v2, v5, v6, v8).
- Une icône ou un objet entier à gauche ; 3 à 5 lignes alignées à gauche dans un bloc qui part de 45 % L.
- Icône : 21 % L × 37,5 % H, centrée sur (22 %, 50 %) (mesuré, v8). Lignes : cap d'environ 4,2 % H (`style-visuel.md`), une tous les 8 % H (mesuré, v8).
- Sur scène (v5, v6), l'objet est au centre du mur et la liste à sa droite. v2 pose la liste au-dessus d'un portable coupé, séparée par un filet vertical.

**d. Objet + chiffre (`objet-chiffre`)** — 2/8 (v2, v4).
- L'objet coupé sur 0–58 % L (v2) ou entier sur 11–49 % L (v4). Un chiffre au style A5, centré à 74,5–75,4 % L, cap de 16 à 22 % H, avec son libellé dessous (mesuré, 2 images).
- Le chiffre est en dégradé (2/2). C'est le seul cas d'A9 où le texte porte l'accent.

**e. Objet annoté (`annotee`)** — 3/8 (v2, v5, v6).
- L'objet ou l'écran au centre ; 2 à 5 libellés courts autour, reliés à leur point par un filet fin (v2), une flèche courbe (v5) ou un chevron (v6).
- v5 donne une couleur par flèche : la skill ne le reprend pas (une seule couleur d'accent).

**f. Empilée (`empilee`)** — 1/8 (v1).
- L'objet en haut (23–37 % H), le nom dessous (cap d'environ 5,3 % H, centre à 48 % H), puis 3 lignes centrées (cap d'environ 4,2 % H, une tous les 8,6 % H) (mesuré, 1 image). C'est la fiche technique ; la slide de prix reprend ce cadre.

#### 4. Contenu visuel

- **Type** : produit détouré ou photo macro (b, d) ; capture dans l'appareil générique (a) ; icône (c) ; rendu ou capture nette, de face ou de dessus (e) ; produit détouré (f).
- **Cadrage** : en b et d, l'objet sort du cadre par 2 ou 3 bords (5 images sur 5, v2, v3, v7). En a, l'appareil est entier, à la place exacte d'A10. En c, e et f, l'objet est entier.
- **Traitement** : fond plein du bloc ; lumière douce de studio, avec une arête claire sur le bord de l'objet ; aucune ombre (0 sur 26 images). Une capture reste entière : une interface coupée se lit comme une erreur de cadrage (`style-visuel.md` §5.2).
- **Accent** : le texte reste dans la couleur du texte (9 images sur 10, v3, v4, v7, v8). La couleur vient de l'image. L'accent va au chiffre (d), ou à un seul filet ou chevron (e), ou à la ligne mise en avant d'une interface schématique.

#### 5. Typographie

- Base : `style-visuel.md` §3 A9. Affirmation en 34 pt, demi-gras, interligne k = 1,5, centrée dans la colonne ; variante icône : lignes en 24 pt alignées à gauche, k = 1,8.
- (a) Le mot en 34 pt aussi (cap mesurée 5,8 % H, soit environ 32 pt), une ligne, trois au plus. Pas de surtitre : le mot est déjà la légende.
- (d) Chiffre en 110 pt (plancher 80 pt), au style et au dégradé d'A5 ; libellé en 20 pt demi-gras, couleur du texte.
- (e) Libellés en 20 pt demi-gras, 2 à 4 mots chacun ; filet de 1 pt en texte secondaire.
- (f) Nom en 32 pt ; lignes en 24 pt centrées, k = 1,95.

#### 6. Apparition et animation

- En slide : l'objet d'abord, puis le texte au clic (l'analyse du corpus). Une liste vient ligne par ligne (v6) ou d'un bloc (v8).
- En vidéo préenregistrée, la slide arrive entière sur une coupe depuis l'orateur (v8, vérifié image par image).
- Enchaînement A10 → A9 (a) : même appareil, même place ; le mot entre seul en fondu. Avec deux objets de même nom, la Morphose le fait sans saut (convention déduite des mesures).
- (e) Les libellés entrent un par un, chacun avec son filet.

#### 7. Brief du visuel et repli

| Variante | À demander à l'utilisateur | Repli dessiné si l'image manque |
|---|---|---|
| a | Capture d'écran nue, PNG, au format natif de l'écran (portrait), 1170 px de large au moins, sans cadre d'appareil ; l'état exact à montrer ; données réelles ou anonymisées par lui. | Appareil générique et interface schématique du moteur, à la place mesurée (37,5 / 4,4 / 25 / 91). |
| b, d | Photo ou rendu du produit en gros plan, PNG détouré (fond transparent) ou sur un fond uni proche du fond du deck ; angle 3/4 ou profil ; le détail dont on parle au centre de l'image ; 2400 px au moins sur le côté long. | Silhouette d'objet modelée (règle 6), arête claire de 2 % de sa largeur, visible de 0 à 58 % L et poussée hors du cadre à gauche et en bas ; ombre de contact sur fond clair seulement. |
| c | Icône ou logo de la fonction, SVG ou PNG transparent, carré, 1024 px au moins. | Carré arrondi (rayon 22 % du côté, convention) en aplat d'accent, avec une forme géométrique blanche simple (cercle ou trait). |
| e | Rendu ou capture de face ou de dessus, 2400 px au moins ; la liste des 2 à 5 points à désigner, avec leur position sur l'image. | Silhouette ou interface schématique ; libellés proposés en `[À VALIDER]`, sans nombre ; filets en texte secondaire. |
| f | Produit détouré, PNG transparent, 1600 px de large au moins. | Silhouette d'objet centrée en haut. |

Dans tous les cas, `image.attendu` dit ce que l'image doit montrer, et le repli ne porte ni chiffre, ni logo, ni nom de marque.

#### 8. À éviter

- Un objet entier qui flotte au milieu de sa moitié : il fait moins keynote qu'un objet coupé par le bord (b, d).
- Le texte collé à l'objet, ou en haut de la colonne : il se centre dans la colonne libre, à 50 % H.
- Plus de quatre lignes.
- Une ombre portée sur fond sombre, un cadre autour de l'objet ou du texte.
- Une capture d'écran coupée par le bord du cadre.
- Un appareil reconnaissable (encoche, îlot, boutons, caméra) : on demande une capture nue.
- Des flèches de plusieurs couleurs, ou un mot en accent sur un objet déjà coloré.

### A10 · Capture plein cadre

#### 1. Rôle et moment

- Toute explication de fonction : l'écran montre, la voix explique, aucun texte n'est ajouté. Le texte vient de l'interface.
- C'est le plan le plus fréquent hors orateur : environ 27 % des images de v1, la moitié des plans sans intervenant de v8 (v1 et v8).
- Présent dans 8/8. Il suit le nom de la fonction (A1, A2) et précède la légende (A9) ou la démo (A25).

#### 2. Composition canonique

Appareil vertical, de face, centré.

| Zone | x | y | l | h | D'où vient la valeur |
|---|---|---|---|---|---|
| Appareil (portrait) | 37,5 | 4,4 | 25 | 91 | mesuré sur 7 images de 5 keynotes (v1, v3, v4, v6, v8) : 36,2–62,7 % L × 2,5–97,2 % H, centre (49,5–49,9 ; 49,7–49,9) |
| Écran dans l'appareil | 38,3 | 5,8 | 23,4 | 88,3 | convention moteur : bord de 3 % de la largeur de l'appareil |
| Tablette (paysage) | 14 | 4,4 | 72 | 91 | mesuré, 3 images (v1, v4, v8) : 67 à 77 % L |
| Portable (paysage) | 7 | 4,5 | 86 | 91 | mesuré, 2 images (v2, v8) |

```
+------------------------------------------------------------+
|                                                            |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::: APPAREIL :::                      |
|                      :::: x 37,5 ::::                      |
|                      ::::: l 25 :::::                      |
|                      ::::: h 91 :::::                      |
|                      :::: centre ::::                      |
|                      :::: 50 / 50 :::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                      ::::::::::::::::                      |
|                                                            |
+------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `telephone-centre`, `tablette-centre`, `portable-centre`, `zoom-serre`, `capture-nue` ou `rangee`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

**a. Téléphone centré (`telephone-centre`)** — 5/8 (v1, v3, v4, v6, v8), 7 images mesurées.
- La boîte ne bouge pas d'une keynote à l'autre (écart de 1,5 % L au plus). Fond noir (v1, v3, v6) ou clair (v4, v8).

**b. Tablette centrée (`tablette-centre`)** — 3/8 (v1, v4, v8).
- Paysage, 67 à 77 % L × 91 % H, de face. Le haut et le bas restent à 4,4 et 95,3 % H, comme le téléphone.

**c. Portable centré (`portable-centre`)** — 2/8 (v2, v8) ; v7 en a aussi, vu seulement avec un mot (A9).
- 86 % L × 91 % H ; le clavier n'est qu'une fine base sous l'écran.
- Écart vu une fois (v2) : un grand écran posé sur pied, le petit boîtier au pied.

**d. Zoom serré (`zoom-serre`)** — 3/8 (v3, v6, v7).
- Un petit appareil (montre) cadré au plus près : le boîtier couvre 28–74 % L, le bracelet sort du cadre en haut et en bas (mesuré, 3 images). L'écran devient presque une slide.

**e. Capture nue plein cadre (`capture-nue`)** — 3/8 (v1, v2, v6).
- Le bureau d'un ordinateur ou une app, sans appareil, à fond perdu (0–100 %). C'est le régime du logiciel de bureau.
- Une capture fournie à fond perdu seulement si elle est en 16:9 (à 4 % près) ; sinon elle reste entière, contenue sur 92 % H, coins de 0,12 in (une interface coupée se lit comme une erreur de cadrage). Sans capture : carte schématique sur 85 % H.

**f. Rangée d'appareils (`rangee`)** — 3/8 (v5 d'après l'analyse de la vidéo, v6, v7).
- Deux à cinq appareils côte à côte, de même taille : trois téléphones de 24 % L chacun, 3,5 % L d'écart, sur 94 % H (estimé, v7). Ils montrent trois états ou trois thèmes du même écran.

#### 4. Contenu visuel

- **Type** : la vraie interface de l'utilisateur, en capture nue, placée par le moteur dans l'appareil générique.
- **Cadrage** : de face, sans perspective (0 vue inclinée sur 24 images) ; l'appareil entier (a, b, c, f) ou coupé haut et bas (d) ; la capture nue à fond perdu (e).
- **Traitement** : aucune ombre, aucun reflet (24 images). Fond plein du bloc : noir ou clair. Le fond flou et coloré de v8 (1/8) ne se reprend pas (`style-visuel.md` §4.3).
- **État de l'écran** : un état réel et figé, l'heure et la date neutres, sans notification parasite.
- **Accent** : dans l'interface seulement. Si elle est schématique, une seule ligne en accent (§5.2).

#### 5. Typographie

Aucun texte ajouté (`style-visuel.md` §3 A10). Si un mot est nécessaire, c'est A9 a : même appareil, même place, le mot dans la marge.

#### 6. Apparition et animation

- En vidéo, l'interface s'anime ; on coupe franchement vers l'orateur et depuis lui (l'analyse du corpus). Entre deux plein cadre, un fondu par le fond du bloc (v7, plus de 30 fondus au gris).
- En slide : fondu d'entrée de 0,5 s. Plusieurs états de l'écran = plusieurs slides au même cadrage, chaque clic montre l'état suivant (Morphose, sinon fondu).
- Rangée : les appareils entrent ensemble (convention).

#### 7. Brief du visuel et repli

- **À demander** : des captures nues, PNG, à la résolution native. Téléphone en portrait : 1170 × 2532 px au moins. Tablette : 2360 × 1640 px au moins. Portable : 2560 × 1600 px au moins. Capture plein cadre : 16:9, 1920 × 1080 au moins (3840 × 2160 conseillé). Si l'écran bouge, un enregistrement MP4 en plus, à poser à la main.
- Jamais de maquette avec le cadre d'un appareil du commerce : le moteur dessine l'appareil générique.
- **Repli** : appareil générique et interface schématique du moteur (`style-visuel.md` §5.2) : barres grises, une ligne en accent, aucun texte, aucun chiffre. Pour une capture nue : carte schématique sur 85 % H, centrée, coins de 0,12 in.

#### 8. À éviter

- Un texte ajouté sur ou à côté de l'écran (c'est alors A9).
- Un appareil incliné, en perspective, ou plus petit que 85 % H.
- Un cadre d'appareil reconnaissable.
- Une capture floue, agrandie au-delà de sa résolution, ou d'un autre ratio étirée.
- Des données réelles de clients à l'écran.
- Un fond flou ou en dégradé.

### A12 · Vue intérieure / éclaté

#### 1. Rôle et moment

- Montrer ce qu'on ne voit pas : l'intérieur, la fabrication, la matière. C'est la partie « ingénierie » d'un produit.
- Présent dans 4/8 (v6, v2, v3, v4) : les 4 keynotes qui lancent un appareil. v5 montre une macro de fabrication, sans éclaté (non comptée).
- Il vient après le nom de la caractéristique et avant le chiffre qui la mesure (A5). Sans texte, ou avec une seule étiquette.

#### 2. Composition canonique

Objet ouvert ou éclaté, centré, sur fond sombre ; une étiquette au plus.

| Zone | x | y | l | h | D'où vient la valeur |
|---|---|---|---|---|---|
| Objet ouvert ou éclaté | 20 | 6 | 60 | 88 | mesuré sur 3 images (v2, v4) : 43 à 71 % L × 79 à 99 % H, centré sur (50, 50) |
| Étiquette (0 ou 1) | 48 | 9 | 14 | 5 | estimé (v4) : en haut, cap d'environ 3 % H, filet vertical de 1 pt jusqu'à la pièce |

```
+------------------------------------------------------------+
|                          +------------+                    |
|                          |  etiquette |                    |
|                          +------------+                    |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|            ########### OBJET OUVERT ###########            |
|            ############# ou ECLATE ############            |
|            ######### x 20  l 60  h 88 #########            |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|            ####################################            |
|                                                            |
+------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `macro-matiere`, `capot-ouvert`, `eclate-axial` ou `flux-lumiere`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

**a. Macro de matière (`macro-matiere`)** — 2/8 (v2, v3) ; v5 montre la même grammaire hors A12.
- Un détail en très gros plan, à fond perdu, en lumière rasante, avec une faible profondeur de champ ; ou un outil en action, des projections, des pièces posées. Aucun texte.

**b. Capot ouvert ou transparence (`capot-ouvert`)** — 3/8 (v2, v4, v6).
- L'objet entier, de face ou de dessus, le capot retiré ou rendu translucide. Centré, 44 à 72 % L × 79 à 91 % H (mesuré, 2 images). Fond sombre (v6) ou clair (v2, v4).

**c. Éclaté le long d'un axe (`eclate-axial`)** — 2/8 vus (v2, v4) ; 3/8 avec v6, où l'analyse décrit les composants qui sortent un à un.
- Les pièces flottent, séparées le long d'un axe (horizontal en v4, vertical en v2), sur 44 % L et toute la hauteur (mesuré, v4), ou en tranches empilées qui sortent du cadre (v4). Une étiquette au plus.

**d. Flux et lumière (`flux-lumiere`)** — 3/8 (v2, v4, v6).
- Ce qui circule est dessiné : air en traînées (v6), chaleur en arcs (v2), faisceau de lumière (v4) ; ou un halo coloré autour de la pièce dont on parle (v2). L'objet reste au centre ; les flux s'étendent sur 60 à 80 % L.

#### 4. Contenu visuel

- **Type** : rendu 3D ou photo macro ; matières : métal, verre, circuit, tissu technique.
- **Cadrage** : la macro est à fond perdu et sort du cadre (a) ; l'objet ouvert ou éclaté est entier et centré (b, c).
- **Traitement** : lumière rasante qui fait briller les arêtes ; fond sombre (v3, v4, v6) ou gris clair (v2, v4) : la skill prend le fond du bloc. Profondeur : profondeur de champ courte (a), écartement des pièces (c), halo (d).
- **Accent** : le halo ou le flux, et rien d'autre. Le corpus met deux couleurs au flux (froid et chaud, v6) ; la skill garde l'accent pour ce dont on parle et le gris secondaire pour l'autre (convention).

#### 5. Typographie

- Étiquette : 16 pt demi-gras, couleur du texte, 1 à 2 mots, filet de 1 pt en texte secondaire (cap estimée à 3 % H, v4).
- Aucune autre ligne. Le nom de la caractéristique passe sur une carte-titre (A1) avant ou après.

#### 6. Apparition et animation

- En vidéo : mouvement de caméra lent ; les couches se séparent (l'analyse du corpus).
- En slide : deux slides au même cadrage, l'objet assemblé puis éclaté, avec des objets de même nom : la Morphose fait la séparation ; sinon un fondu.
- L'étiquette arrive au clic, après la séparation. Le flux arrive après l'objet (deux temps).

#### 7. Brief du visuel et repli

- **À demander** : un rendu 3D ou une photo macro. Plein cadre (a) : 16:9, 3840 × 2160 px au moins. Objet ouvert ou éclaté (b, c) : PNG détouré, 2400 px au moins sur le côté long. Pour l'éclaté : deux fichiers au même cadrage et à la même échelle, l'un assemblé, l'autre éclaté. Le nom exact de la pièce à étiqueter.
- **Repli** : un éclaté schématique : 3 à 5 plaques à coins arrondis, empilées en léger décalage, en aplats modelés du texte mélangé de 9 à 16 % vers le fond, nettement séparées (l'éclaté se lit à l'écart des pièces) ; une seule pièce mise en avant, au liseré et à la lueur d'accent (jamais un aplat d'accent atténué, qui vire au brun sur fond sombre) ; l'étiquette à droite de cette pièce, son filet ne traverse aucune autre ; sans chiffre, sans étiquette inventée.

#### 8. À éviter

- Plusieurs étiquettes, ou des spécifications chiffrées qui n'ont pas de source.
- Deux couleurs d'accent dans les flux.
- Un éclairage plat, une vue de plan technique coté.
- Un fond texturé ou dégradé.
- Une macro floue sur toute sa surface : la zone nette doit montrer la pièce dont on parle.

### A13 · Produit seul

#### 1. Rôle et moment

- La révélation du produit, puis l'appui de chaque caractéristique : le produit tourne pendant que la voix décrit.
- Présent dans 6/8 (v5, v6, v1, v2, v3, v4). Absent des deux dernières conférences logicielles (v7, v8), sans matériel.
- Il suit le film de révélation ou la carte-titre du nom. Aucun texte.

#### 2. Composition canonique

Produit entier, centré, sur le fond plein du bloc.

| Zone | x | y | l | h | D'où vient la valeur |
|---|---|---|---|---|---|
| Produit | 36 | 14 | 28 | 72 | mesuré sur 5 images (v1, v3, v4) : hauteur 60 à 87 % H, centre à 45–50,5 % L et 49–53 % H |

La largeur suit la forme du produit ; seule la hauteur est fixée. Aucune ombre visible (5 images sur 5).

```
+------------------------------------------------------------+
|                                                            |
|                                                            |
|                                                            |
|                      ################                      |
|                      ################                      |
|                      ################                      |
|                      #### PRODUIT ###                      |
|                      #### entier ####                      |
|                      ### h 60-87 % ##                      |
|                      #### centre ####                      |
|                      #### 50 / 50 ###                      |
|                      ################                      |
|                      ################                      |
|                      ################                      |
|                      ################                      |
|                                                            |
|                                                            |
|                                                            |
+------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `centre-entier`, `hero-coupe`, `profil-levitation` ou `coloris`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

**a. Centré entier (`centre-entier`)** — 3/8 (v1, v3, v4).
- De face ou de 3/4, sur clair (v3, v4) ou sur noir (v1).

**b. Héros coupé (`hero-coupe`)** — 4/8 (v2, v3, v4, v5).
- Gros plan en légère contre-plongée ou sur un détail (objectif, molette, arête) ; le produit sort du cadre par 1 à 4 bords (mesuré : 12,5–99,4 % H en v3, 1–99 % L en v4).

**c. Profil en lévitation (`profil-levitation`)** — 2/8 (v2, v3).
- L'objet vu de profil, à plat ou entrouvert, flotte au milieu : 71 % L × 20 % H en v3 (mesuré), dans le décor en v2. Il dit la finesse.

**d. Coloris (`coloris`)** — 2/8 (v3, v4).
- Un éventail des coloris autour d'un axe (v3, 63 % L × 69 % H, mesuré), ou deux vues côte à côte, avant et arrière (v4, 52 à 77 % L × 70 à 80 % H, mesuré).

**Hors slide — vrai produit sur un socle** — 1/8 (v6). En direct, le vrai produit est posé sur un socle noir, côté cour, et l'orateur se tient à côté :. C'est une mise en scène de salle : le moteur ne la dessine pas.

#### 4. Contenu visuel

- **Type** : rendu détouré ou photo de studio du produit de l'utilisateur.
- **Cadrage** : entier et centré (a, c, d) ; coupé par le bord (b).
- **Traitement** : lumière douce de studio, arêtes claires ; aucune ombre visible (5/5 en a) ; fond plein du bloc. Le corpus change de fond selon la catégorie (3/8, v2, v3, v4) ; la skill garde le fond du bloc et n'en change qu'entre deux blocs.
- **Accent** : aucun. Le produit porte sa propre couleur.

#### 5. Typographie

Aucun texte (`style-visuel.md` §3 A13). Le nom passe avant, sur une carte-titre (A1).

#### 6. Apparition et animation

- En vidéo : rotation lente (v3, v4), entrée en lévitation (v2), ou un détail en macro puis un recul jusqu'à l'objet entier (v2, vérifié image par image).
- En slide : le recul se refait avec deux slides, le détail (b) puis l'objet entier (a), objets de même nom, en Morphose ; sinon un fondu de 0,5 s.

#### 7. Brief du visuel et repli

- **À demander** : PNG détouré à fond transparent ; angle de face ou de 3/4 face, en légère contre-plongée pour le héros ; lumière douce, sans ombre ni reflet intégrés ; 2000 px de haut au moins. Un fichier par coloris, même angle et même échelle. Pour le profil, une vue de côté exacte.
- **Repli** : la silhouette d'objet du moteur (volume modelé, arête claire, reflet doux), centrée sur 72 % H ; ombre de contact sur fond clair seulement ; aucun détail qui imite un produit réel.

#### 8. À éviter

- Un produit trop petit (moins de 50 % H), ou du texte à côté.
- Une ombre portée sur fond sombre, un reflet au sol.
- Un détourage sale (liseré blanc autour de l'objet).
- Un fond dégradé ou texturé.
- Plusieurs produits différents : c'est alors une gamme (A20).

### A18 · Photo plein cadre

#### 1. Rôle et moment

- Deux emplois. **L'usage** : l'émotion avant l'argument, une personne qui vit avec le produit. **L'exemple** : une photo prise avec le produit, comme preuve de qualité.
- Présent dans 5/8 (v5, v6, v2, v3, v4).
- L'usage vient juste après la carte-titre, en 2ᵉ position (v2 : 3 fiches produit sur 3). L'exemple vit dans le chapitre « image » (v3, v4).

#### 2. Composition canonique

Photo à fond perdu, sans cadre ni coins arrondis (`style-visuel.md` §4.3) ; un cartouche facultatif en bas à droite.

| Zone | x | y | l | h | D'où vient la valeur |
|---|---|---|---|---|---|
| Photo | 0 | 0 | 100 | 100 | observé : fond perdu sur l'écran ou le mur, 19 images sur 19 |
| Cartouche (exemple) | 77 | 82 | 18 | 12 | estimé sur 2 images (v3, v4) : 81–95 % L × 76–94 % H ; la skill le réduit à 3 lignes |

```
+------------------------------------------------------------+
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|.................... PHOTO a fond perdu ....................|
|.................... sujet sur un tiers ....................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|..............................................+---------+...|
|.............................................. cartouche ...|
|..............................................+---------+...|
|............................................................|
+------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `usage`, `exemple-cartouche`, `diptyque` ou `photo-titre`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

**a. Usage (`usage`)** — 3/8 (v2, v5, v6).
- Une scène de vie : une personne utilise le produit dans un lieu réel, sujet sur un tiers, produit net et visible. En direct, la photo couvre tout le mur et l'orateur s'y tient à l'échelle d'une figurine.

**b. Exemple + cartouche (`exemple-cartouche`)** — 2/8 (v3, v4).
- Une photo forte (portrait, paysage, animal) prise avec le produit. En bas à droite, un cartouche gris translucide à coins arrondis : 3 lignes en accent (appareil, auteur, lieu), puis les réglages en blanc, en petites capitales (vu à pleine résolution, 2/2).

**c. Diptyque (`diptyque`)** — 2/8 (v3, v4).
- Deux photos côte à côte, chacune sur une moitié, bord à bord ; un cartouche par photo, dans les coins bas extérieurs.

**d. Photo + titre (`photo-titre`)** — 2/8 (v2, v4).
- Un plan calme du lieu ou d'une matière (mur, sable vu du ciel, bois, fumée), avec une grande zone unie au centre. Un mot ou une phrase en blanc, centré à 47,4–48,6 % H, cap de 11 à 14 % H (mesuré, 3 images v4). Pas de voile (4/4).

#### 4. Contenu visuel

- **Type** : photo réelle. Usage : personne et produit en situation. Exemple : photo prise avec le produit. Photo + titre : lieu ou matière calme.
- **Cadrage** : à fond perdu ; sujet décentré, sur un tiers (6 images d'usage sur 10) ; centre libre pour le titre (photo + titre, 4/4).
- **Traitement** : lumière naturelle, chaude ou du soir ; profondeur de champ courte (usage) ; aucune retouche visible, aucun filtre. Le cartouche : aplat gris translucide (environ 55 % d'opacité, estimé), coins arrondis d'environ 1 % L, sans trait.
- **Accent** : la photo porte la couleur. Seules les premières lignes du cartouche passent en accent (2/2). Le titre reste en blanc (4/4).

#### 5. Typographie

- Photo + titre : 72 pt demi-gras, blanc, centré à 47,5 % H (cap mesurée de 11 à 14 % H, soit 62 à 80 pt) ; 2 lignes au plus, alors 56 pt, interligne k = 1,6. C'est l'échelle d'A1 : le corpus ne montre ni titre en bas, ni voile (4/4).
- Cartouche : 10 pt (plancher 9), regular, 3 lignes au plus ; les deux premières en accent demi-gras.
- Aucune ombre sur le texte (`style-visuel.md` §1, règle 7). Si le contraste du titre tombe sous 3:1, on change de photo ; à défaut, un voile radial très doux de 20 à 30 % au centre (convention).

#### 6. Apparition et animation

- Fondu (l'analyse du corpus). Le cartouche entre avec la photo (convention). Les deux photos du diptyque sont là ensemble (2/2 images).
- Photo + titre : la photo d'abord, le titre en fondu à l'instant où il est dit.
- Pas de zoom lent sur la photo (aucun vu).

#### 7. Brief du visuel et repli

- **À demander** : une photo 16:9, 3840 × 2160 px conseillé, 1920 × 1080 au moins, JPEG de qualité 85 ou plus, avec les droits d'usage et l'accord des personnes. Usage : une vraie personne avec le produit, sujet sur un tiers. Exemple : l'appareil, l'auteur et le lieu, réels ; les réglages seulement s'ils sont exacts. Diptyque : deux photos 8:9, 1920 × 2160 px au moins. Photo + titre : un centre calme sur 60 % L × 30 % H.
- **Repli** : aplat un peu plus clair que le fond et deux halos neutres (moteur, §5.2). Jamais de personne dessinée. Pas de cartouche dans le repli : son contenu est un fait. Photo + titre : le titre sur cet aplat.

#### 8. À éviter

- Un voile noir sur toute la photo, un bandeau en bas, une ombre sous le titre.
- Un cadre, une bordure, des coins arrondis.
- Un titre posé sur une zone chargée.
- Un cartouche avec des réglages inventés.
- Une photo de banque d'images reconnaissable, un filtre, une photo étirée.
- Une photo où le produit ne se voit pas (usage).

### A22 · Plan large + écran

#### 1. Rôle et moment

- La respiration entre deux slides plein cadre, et le plan d'entrée de chaque intervenant.
- Présent dans 7/8 (v5, v6, v1, v2, v7, v8, v4) ; absent de v3, qui n'a aucun écran dans le décor.
- **Ce qu'on garde dans un deck projeté** : ce n'est pas une slide, c'est la salle. On garde les conditions de lecture : l'orateur ne couvre jamais le texte ; il se tient à côté de l'écran (v1, v2, v7, v8) ou devant le bas d'un mur géant, sous le texte (v4, v5, v6), soit 7/7 ; en salle sombre, le fond sombre fond l'écran dans la salle (2/2 en direct) ; rien d'essentiel dans le bas de la slide, que les têtes et l'orateur cachent (convention). Le moteur ne produit pas de slide A22.
- **Ce qu'on garde dans une vidéo** : un plan à tourner ou à composer. L'orateur en pied, à côté d'un écran qui montre la slide en cours ; ce plan alterne avec la même slide en plein cadre (4/8 : v1, v2, v7, v8).

#### 2. Composition canonique (vidéo)

| Zone | x | y | l | h | D'où vient la valeur |
|---|---|---|---|---|---|
| Écran : la slide en cours | 36 | 16 | 56 | 58 | estimé sur 8 images : écran de 40 à 71 % L, haut à 3–36 % H, bas à 72–83 % H |
| Orateur, en pied | 25 | 48 | 8 | 38 | estimé : 15 à 53 % H de haut, à côté de l'écran (centre à 16–36 % L, ou à 82 % L) ; pieds à 73–95 % H |
| Sol | 0 | 86 | 100 | 14 | sol qui reflète la slide (v1, v2, v7) |

```
+------------------------------------------------------------+
|                                                            |
|                                                            |
|                                                            |
|                      :::::::::::::::::::::::::::::::::     |
|                      :::::::::::::::::::::::::::::::::     |
|                      :::::::::::::::::::::::::::::::::     |
|                      ::::::::::::: ECRAN :::::::::::::     |
|                      ::::::: la slide en cours :::::::     |
|                      ::::::: x 36  l 56  h 58 ::::::::     |
|               ooooo  :::::::::::::::::::::::::::::::::     |
|               ooooo  :::::::::::::::::::::::::::::::::     |
|               o O o  :::::::::::::::::::::::::::::::::     |
|               ooooo  :::::::::::::::::::::::::::::::::     |
|               ooooo                                        |
|               ooooo                                        |
|____________________________________________________________|
|______________________ sol qui reflete _____________________|
|____________________________________________________________|
+------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `hall-ecran`, `scene-mur` ou `panneau-verre` sont acceptées, mais la slide devient la photo de la scène à fond perdu, avec un avertissement. Ce sont des plans à tourner, pas des slides.

**a. Hall et écran autoportant (`hall-ecran`)** — 3/8 (v1, v2, v7).
- Un hall clair, un écran posé au sol, l'orateur à côté ; plafond et sol miroir visibles ; plan symétrique.

**b. Scène et mur sombre (`scene-mur`)** — 4/8 (v2, v4, v5, v6).
- Un plateau sombre, un mur sur toute la largeur, l'orateur au pied ; en direct, une rangée de projecteurs au-dessus (v5, v6).

**c. Panneau incrusté (`panneau-verre`)** — 1/8 (v8).
- Une dalle translucide à coins arrondis, sans cadre, flotte à côté de l'orateur dans un lieu réel et floute le décor derrière elle ; elle porte la slide ; elle entre et sort en glissant.

#### 4. Contenu visuel

- **Type** : un rush de l'orateur ; la slide en cours, exportée en image ; le décor.
- **Cadrage** : plan fixe, large, symétrique ; l'écran entier et de face.
- **Traitement** : sol qui reflète (v1, v2, v7) ; panneau : aplat blanc translucide à 70–80 % (convention), flou du décor derrière, ombre douce au sol (v8).
- **Accent** : celui de la slide affichée, rien d'autre.

#### 5. Typographie

Celle de la slide affichée, inchangée. Le synthé (A21) apparaît au premier passage de l'intervenant, du côté opposé à lui (5/6 cadrages décentrés, l'analyse du corpus).

#### 6. Apparition et animation

- Coupe depuis le plein cadre ; l'orateur entre souvent en marchant (l'analyse du corpus).
- Le panneau entre en glissant et sort hors du champ (v8).

#### 7. Brief du visuel et repli

- **À demander (vidéo)** : un rush 3840 × 2160 (1920 × 1080 au moins), 25 ou 30 images par seconde, plan fixe large, orateur en pied, du côté laissé libre par la slide. Pour un plan composé : l'orateur filmé en pied sur fond uni (vert ou gris), lumière douce, et chaque slide exportée en PNG 1920 × 1080.
- **Repli** : sans rush, la slide en plein cadre, dans son propre archétype. On ne dessine jamais de personne.

#### 8. À éviter

- Un écran trop petit pour lire la slide (moins de 40 % L).
- L'orateur devant le texte.
- Un écran en forte perspective.
- Un synthé posé sur l'écran.

### A23 · Orateur dans la slide

#### 1. Rôle et moment

- Le plan de parole par défaut. Le plan large donne le texte ; le plan serré donne l'expression.
- Présent dans 6/8 (v5, v6, v1, v2, v7, v4) ; variante dans v8 (panneau coupé par le bord) ; absent de v3.
- **Ce qu'on garde dans un deck projeté** : pas de slide à part. La slide derrière l'orateur doit supporter d'être coupée : le mot-clé assez gros pour se reconnaître à moitié (A1, 100 pt), et le visuel tenu dans les deux tiers du haut (convention).
- **Ce qu'on garde dans une vidéo** : un plan taille de l'orateur sur un tiers ; derrière lui, la slide agrandie de 1,3 à 1,7 fois et coupée par le bord.

#### 2. Composition canonique (vidéo)

| Zone | x | y | l | h | D'où vient la valeur |
|---|---|---|---|---|---|
| Orateur, plan taille | 58 | 10 | 32 | 90 | estimé sur 8 images : tiers droit (centre à 67–74 % L : v2, v7), tiers gauche (27–33 % L : v4, v7, v8), ou centre quand le mot passe derrière la tête (50–57 % L : v1, v5) ; tête à 1–22 % H ; coupé à la taille ou aux hanches |
| Contenu de la slide derrière | 4 | 4 | 62 | 26 | mesuré sur 2 images (v2, v7) : cap de 24,7 % H, centre à 31–35 % L, dans la moitié haute |

```
+------------------------------------------------------------+
|............................................................|
|..######################################....................|
|..########### MOT GEANT coupe #####ooooooooooooooooooo......|
|..############# cap 25 % H ########ooooooooooooooooooo......|
|..#################################ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooo ORATEUR ooooo......|
|...................................ooo plan taille ooo......|
|...................................ooo centre 74 % ooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
|...................................ooooooooooooooooooo......|
+------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `mot-coupe`, `contenu-lisible`, `interface-geante` ou `slide-floue` sont acceptées, mais la slide devient la photo de la scène à fond perdu, avec un avertissement. Ce sont des plans à tourner, pas des slides.

**a. Mot coupé (`mot-coupe`)** — 3/8 (v1, v5, v7).
- Le mot géant de la slide dépasse le cadre ou passe derrière la tête ; on n'en lit qu'une partie.

**b. Contenu lisible (`contenu-lisible`)** — 2/8 (v2, v7).
- Moitié orateur, moitié contenu entier et lisible : un chiffre et son libellé, ou une icône et son nom.

**c. Interface géante (`interface-geante`)** — 3/8 (v2, v4, v8).
- Un écran d'appareil énorme, coupé par le bord, sur un côté ; l'orateur sur l'autre tiers.

**d. Slide floue (`slide-floue`)** — 1/8 (v6).
- Derrière l'orateur, la slide hors de la zone nette : il n'en reste que des formes et des couleurs.

#### 4. Contenu visuel

- **Type** : rush de l'orateur en plan taille ; la slide en cours, en grande résolution.
- **Cadrage** : l'orateur sur un tiers latéral, regard caméra ; la slide occupe tout le fond et dépasse le cadre.
- **Traitement** : l'écran réel est filmé (le bord de l'écran se voit parfois, v7) ; en plan composé, la slide agrandie sans flou (a, b, c) ou floutée fortement (d).
- **Accent** : celui de la slide, rien d'autre.

#### 5. Typographie

Celle de la slide, agrandie : le mot ou le chiffre atteint une cap de 25 % H (mesuré, 2 images). Le synthé (A21), s'il y en a un, se place du côté opposé à l'orateur.

#### 6. Apparition et animation

- Coupe depuis le plan large (l'analyse du corpus). Le fond change quand la slide change, sans mouvement de caméra.

#### 7. Brief du visuel et repli

- **À demander (vidéo)** : un rush plan taille en 3840 × 2160 (pour pouvoir recadrer), l'orateur décalé sur un tiers, le regard vers la caméra. Pour un plan composé : l'orateur détouré ou sur fond uni, et chaque slide en PNG 3840 × 2160, pour l'agrandir 1,7 fois sans flou.
- **Repli** : la slide plein cadre. Jamais de personne dessinée.

#### 8. À éviter

- L'orateur au centre, qui cache le mot.
- Un mot coupé au point de ne plus se reconnaître (convention : au moins 60 % du mot visible).
- Une slide réduite derrière l'orateur, au lieu d'agrandie.
- Un flou partiel, qui fait croire à une erreur de mise au point.

### A24 · Décor sans écran

#### 1. Rôle et moment

- L'accueil, un relais, le cadrage d'une section. Le lieu remplace la slide et porte le sujet.
- Présent dans 6/8 : tous les préenregistrés (v1, v2, v7, v8, v3, v4) ; aucun en direct (0/2).
- **Ce qu'on garde dans un deck projeté** : un moment sans slide. Pendant l'accueil ou un relais, l'écran reste au fond du bloc, vide, et l'orateur seul porte le moment (convention, puisque le direct n'en a pas). Si le lieu dit quelque chose du sujet, une photo du lieu (A18 usage) le remplace.
- **Ce qu'on garde dans une vidéo** : tourner l'orateur dans un vrai lieu lié au sujet, en plan large puis en plan taille.

#### 2. Composition canonique (vidéo)

| Zone | x | y | l | h | D'où vient la valeur |
|---|---|---|---|---|---|
| Décor réel | 0 | 0 | 100 | 100 | observé : lieu à fond perdu, souvent symétrique |
| Orateur, en pied, centré | 45 | 38 | 10 | 52 | estimé sur 6 images (v2, v3, v8) : centre à 49–51 % L, hauteur 39 à 61 % H, pieds à 83–96 % H ; 2 autres images le décalent à 36–40 % L (v7, v8) |

```
+------------------------------------------------------------+
|............................................................|
|................... DECOR REEL symetrique ..................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|............................................................|
|...........................oooooo...........................|
|...........................oooooo...........................|
|...........................oooooo...........................|
|...........................oo O o...........................|
|...........................o en o...........................|
|........................... pied ...........................|
|...........................oooooo...........................|
|...........................oooooo...........................|
|...........................oooooo...........................|
|............................................................|
|............................................................|
+------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `large-centre`, `taille-centre` ou `decor-sujet` sont acceptées, mais la slide devient la photo de la scène à fond perdu, avec un avertissement. Ce sont des plans à tourner, pas des slides.

**a. Plan large centré (`large-centre`)** — 5/8 (v2, v3, v4, v7, v8).
- L'orateur en pied au centre d'une architecture, les lignes de fuite convergent vers lui (6 images sur 8) ; il entre souvent en marchant.

**b. Plan taille centré (`taille-centre`)** — 4/8 vus (v1, v3, v4, v7) ; 5/8 avec v8, où l'analyse décrit le plan moyen qui suit le plan large.
- Cadré à la taille, centre à 42–56 % L, tête à 3–15 % H (estimé) ; mains jointes au repos (vu dans v3, v4, v7, v8) ; le décor reste lisible derrière.

**c. Décor qui montre le sujet (`decor-sujet`)** — 3/8 (v1, v2, v4).
- L'objet du sujet est dans le champ (une voiture, une paillasse, une salle de sport, une plage avec des passants) ; l'orateur se décale sur un côté pour lui laisser la place ; le synthé passe de l'autre côté.

#### 4. Contenu visuel

- **Type** : un rush dans un lieu réel, lié au sujet (6/6 décors thématiques, l'analyse du corpus).
- **Cadrage** : large et symétrique, puis taille ; l'orateur au centre, sauf quand l'objet du sujet partage le champ (c).
- **Traitement** : lumière naturelle ; la journée peut avancer du jour à la nuit au fil de la keynote (2/6 : v3, v4) ; figurants actifs au fond (v4).
- **Accent** : aucun. Le lieu porte la couleur.

#### 5. Typographie

Aucun texte, sauf le synthé (A21) au premier passage, du côté opposé à l'orateur. Jamais pour l'hôte (0/8).

#### 6. Apparition et animation

- Entrée en marchant (6/6) ; deux caméras, large puis taille (l'analyse du corpus).
- Liaison entre deux décors par un plan aérien ou un drone (5/6), jamais par une coupe sèche (v1, v2, v7, v8).

#### 7. Brief du visuel et repli

- **À demander (vidéo)** : un rush 3840 × 2160 dans un lieu lié au sujet : un plan large et un plan taille, ou un seul plan 4K recadré ; lumière naturelle ; orateur au centre, regard caméra ; son propre (micro-cravate).
- **Repli** : en deck, l'écran au fond du bloc, vide, ou la carte-titre du bloc (A1). En vidéo, une photo du lieu (A18) sous la voix ; à défaut, l'aplat et les deux halos du moteur. Jamais de personne dessinée.

#### 8. À éviter

- Un décor sans lien avec le sujet, ou un fond de bureau neutre.
- Un orateur décentré sans raison en plan large.
- Un texte incrusté autre que le synthé, un synthé pour l'hôte.
- Une coupe sèche entre deux décors.

### A25 · Démo manipulée

#### 1. Rôle et moment

- Après l'annonce d'une fonction, avant la phrase-bilan. L'orateur montre que ça marche et commente à la première personne.
- Présent dans 5/8 (v5, v6, v1, v7, v8). Les événements produits la remplacent par des saynètes jouées (v3, v4).
- **Ce qu'on garde dans un deck projeté** : en salle, la démo passe par le flux de l'appareil, en grand, dans le cadre générique (A10), pendant que l'orateur manipule à une table (v6) ou debout à côté (v5). Le deck garde une slide avant la démo (A10 au même cadrage) et, en secours, la même démo en captures si l'appareil lâche (convention).
- **Ce qu'on garde dans une vidéo** : alterner plan large de l'orateur, mains en gros plan et flux plein cadre (l'analyse du corpus).

#### 2. Composition canonique (vidéo : les mains sur fond uni)

| Zone | x | y | l | h | D'où vient la valeur |
|---|---|---|---|---|---|
| Appareil tenu en main | 34 | 10 | 28 | 80 | estimé sur 5 images (v7, v8) : appareil incliné de 10 à 20°, centre à 48–52 % L |
| Mains | 28 | 30 | 45 | 70 | estimé : une main tient par le bas et sort du cadre en bas ; l'autre touche l'écran |
| Fond uni gris clair | 0 | 0 | 100 | 100 | observé (v7, v8) ; table noire en direct (v6) |

```
+------------------------------------------------------------+
|                                                            |
|  fond uni                                                  |
|                    :::::::::::::::::                       |
|                    :::::::::::::::::                       |
|                    :::::::::::::::::                       |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooo::: APPAREIL ::::ooooooo                |
|                 ooo::::: tenu ::::::ooooooo                |
|                 ooo:::: incline ::::ooooooo                |
|                 ooo::: 10-20 deg :::ooooooo                |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooo:::::::::::::::::ooooooo                |
|                 ooooooooooooooooooooooooooo                |
|                 ooooooooooooooooooooooooooo                |
+------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `table-flux`, `mains-fond-uni`, `epaule`, `table-haute` ou `tend-appareil` sont acceptées, mais la slide devient la photo de la scène à fond perdu, avec un avertissement. Ce sont des plans à tourner, pas des slides.

**a. Table et flux au mur (`table-flux`)** — 2/8 (v5, v6), en direct.
- L'orateur à une table noire (v6) ou debout (v5), petit, sur le tiers gauche ; le flux de l'appareil sur toute la hauteur du mur, à droite, coupé en haut.

**b. Mains sur fond uni (`mains-fond-uni`)** — 3/8 (v6, v7, v8).
- Une ou deux mains, l'appareil incliné, des gestes réels, devant un gris clair uni (v7, v8) ou en plongée sur la table noire (v6).

**c. Par-dessus l'épaule (`epaule`)** — 2/8 vus (v1, v6) ; 3/8 avec v7, où l'analyse décrit ce plan dans les démos en situation.
- L'épaule floue au premier plan, l'écran en grand, incliné, coupé par le bord.

**d. Table haute (`table-haute`)** — 2/8 (v7, v8).
- L'orateur debout derrière une table ronde, l'ordinateur ou la tablette posé devant lui, en plan moyen ; le montage alterne avec la capture plein cadre.

**e. L'orateur tend l'appareil (`tend-appareil`)** — 1/8 (v1) ; v4 le fait une fois avec son produit vedette (compté à part dans l'analyse du corpus).
- L'orateur, en plan taille, tient l'appareil vers la caméra, à hauteur de poitrine ; l'écran se voit, petit.

#### 4. Contenu visuel

- **Type** : rushes des mains et de l'orateur ; enregistrement d'écran pour le flux plein cadre.
- **Cadrage** : appareil incliné (b, c), jamais de face comme en A10 ; mains qui sortent du cadre en bas.
- **Traitement** : fond gris clair uni (v7, v8) ou table noire (v6) ; lumière douce, sans reflet sur l'écran ; l'écran reste lisible.
- **Accent** : celui de l'interface. L'appareil de l'utilisateur ou un appareil sans signe distinctif.

#### 5. Typographie

Aucun texte ajouté : le texte vient de l'interface. Synthé (A21) au premier passage d'un nouvel intervenant.

#### 6. Apparition et animation

- Alternance plan large, mains, flux plein cadre, en coupes franches (l'analyse du corpus).
- Une démo longue dure de 2 à 4 minutes (v7).

#### 7. Brief du visuel et repli

- **À demander** : l'enregistrement d'écran de la démo (MP4, résolution native, 60 images par seconde si l'interface s'anime) ; en vidéo, les rushes des mains sur fond gris uni, en 3840 × 2160, lumière douce, et un plan large de l'orateur. Le déroulé de la démo en 3 à 5 gestes.
- **Repli** : A10 avec l'appareil générique et l'interface schématique, un état par clic. Jamais de mains dessinées.

#### 8. À éviter

- Une démo sans flux plein cadre : l'écran reste illisible.
- Des mains qui cachent la zone dont on parle.
- Un fond chargé derrière les mains, un reflet sur l'écran.
- Une démo en direct sans captures de secours.
- Des notifications réelles ou des données privées à l'écran.

## 7. Récap et conversion

Les slides qui ferment une annonce : le récap, le prix, la date, la fin. Puis deux designs hors du catalogue des archétypes, que le moteur dessine aussi : la gamme de coloris et la frise. Images regardées : 180.

### A14 · Bento

#### 1. Rôle et moment

- Il ferme une section, pendant la phrase de récap (étape 14 « Mini-récap », `grammaire.md` §4.1). Il ne présente rien de neuf : chaque tuile rappelle une chose déjà dite.
- Présent dans **6/8** (v1, v2, v7, v8, v3, v4) : tous les préenregistrés (6/6), aucun direct (0/2). En direct, le récap passe par une grille d'icônes (v6) ou par la liste des principes (v5).
- Un par section : 5 grilles en v1, 7 en v2, 7 en v3, 6 (plus 2) en v4, 7 en v7, 6 en v8.
- Dans un bloc produit, il vient juste avant le prix et la disponibilité (v2, v3, v4 : 3/3). Dans un bloc logiciel, il clôt chaque plateforme (v1, v7, v8 : 3/3).

#### 2. Composition canonique

Une grille de 3 × 3 cellules. La cellule centrale est deux à trois fois plus grande que les autres. Chaque cellule extérieure porte une tuile, ou deux tuiles côte à côte.

Mesuré :
- marge extérieure de 0,8 à 1,1 % L (v1, v3, v4, v7, v8) ; gouttière de 0,6 à 1,25 % L ;
- le même rayon pour toutes les tuiles (`style-visuel.md` §5.1) ;
- tuile centrale « nom » : 39 % L × 31,4 % H, en (30,5 ; 34,3) (v7 et v8, identiques au pixel ; 32 × 31 en v1) ;
- tuile centrale « produit » : 48,2 % L × 47,4 % H, en (25,9 ; 26,3) (une image de v3 et une de v4, identiques au pixel). Elle varie de 39 à 48 % L et de 47 à 64 % H selon la forme du produit (39 × 47 en v2, 39 × 56 en v3, 39 × 64 en v4).

Valeurs retenues : marge 1,0 % L et 1,7 % H ; gouttière 0,9 % L, soit 1,6 % H (0,09 in dans les deux sens).

| Zone (grille « nom ») | x | y | l | h | En pouces |
|---|---|---|---|---|---|
| Colonnes | 1,0 · 30,5 · 70,4 | | 28,6 · 39,0 · 28,6 | | 0,10 · 3,05 · 7,04 in |
| Rangées | | 1,7 · 34,3 · 67,3 | | 31,0 · 31,4 · 31,0 | 0,10 · 1,93 · 3,79 in |
| Tuile centrale (nom) | 30,5 | 34,3 | 39,0 | 31,4 | 3,9 × 1,77 in |

| Zone (grille « produit ») | x | y | l | h | En pouces |
|---|---|---|---|---|---|
| Colonnes | 1,0 · 25,9 · 75,0 | | 24,0 · 48,2 · 24,0 | | |
| Rangées | | 1,7 · 26,3 · 75,3 | | 23,0 · 47,4 · 23,0 | |
| Tuile centrale (produit) | 25,9 | 26,3 | 48,2 | 47,4 | 4,82 × 2,67 in |

Intérieur d'une tuile (règle commune, vue sur les 6 keynotes à bento) : le visuel occupe le haut, le libellé est centré dans une bande en bas (de 79 à 93 % de la hauteur de la tuile), marge intérieure de 6 % de la tuile. Le libellé est centré sous le visuel dans la plupart des tuiles des 6/6 bentos ; seules quelques tuiles mettent le texte à côté de l'icône.

Grille « nom » (8 tuiles autour du nom) :

```
+----------------------------------------------------------------+
| +----------------+ +----------------------+ +----------------+ |
| |                | |                      | |                | |
| |    capture     | |        icone         | |     photo      | |
| |                | |                      | |                | |
| |                | |                      | |                | |
| +----------------+ +----------------------+ +----------------+ |
| +----------------+ +----------------------+ +----------------+ |
| |                | |                      | |                | |
| |    capture     | |     NOM (accent)     | |      mot       | |
| |                | |                      | |                | |
| |                | |                      | |                | |
| +----------------+ +----------------------+ +----------------+ |
| +----------------+ +----------------------+ +----------------+ |
| |                | |                      | |                | |
| |     icone      | |       capture        | |     icone      | |
| |                | |                      | |                | |
| |                | |                      | |                | |
| +----------------+ +----------------------+ +----------------+ |
+----------------------------------------------------------------+
```

Grille « produit » (10 tuiles autour du produit) :

```
+----------------------------------------------------------------+
| +-------------+ +-------------++-------------+ +-------------+ |
| |    icone    | |   chiffre   ||   capture   | |    photo    | |
| |             | |             ||             | |             | |
| +-------------+ +-------------++-------------+ +-------------+ |
|                                                                |
| +-------------+ +----------------------------+ +-------------+ |
| |             | |                            | |             | |
| |             | |                            | |             | |
| |   capture   | |          PRODUIT           | |     mot     | |
| |             | |                            | |             | |
| |             | |                            | |             | |
| |             | |                            | |             | |
| +-------------+ +----------------------------+ +-------------+ |
|                                                                |
| +-------------+ +-------------++-------------+ +-------------+ |
| |     mot     | |   chiffre   ||    icone    | |    icone    | |
| |             | |             ||             | |             | |
| +-------------+ +-------------++-------------+ +-------------+ |
+----------------------------------------------------------------+
```

La grille « nom » tient en 8 tuiles. La grille « produit » en demande 10, ou 8 si l'on fusionne les deux tuiles du haut et les deux du bas. Le corpus en montre de 8 à 19.

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `nom-au-centre`, `produit-au-centre`, `tuiles-chiffres`, `mot-geant-et-produit`, `theme-et-matieres`, `grille-icones` ou `fragments-logiciel` (variante g, ci-dessous). Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

**a. Nom au centre (`nom-au-centre`)** — 3/8 (v1, v7, v8), les trois conférences logicielles préenregistrées.
Le nom de la plateforme, en blanc, sur la tuile centrale large et basse. Autour : captures, icônes, une photo, un mot. Aucun chiffre (0/3).

**b. Produit au centre (`produit-au-centre`)** — 3/8 (v2, v3, v4), les trois événements produits.
La tuile centrale est plus haute et ne porte aucun texte : le rendu détouré du produit seul (4 tuiles centrales sur 4 regardées). Autour, 10 à 18 tuiles plus petites.

**c. Mot géant traversé par le produit (`mot-geant-et-produit`)** — 2/8 (v3, v4), le modèle haut de gamme.
La tuile centrale porte un mot de trois lettres, géant ; le produit passe devant le bas du mot et sort par le bas de la tuile. Fond sombre (2/2).

**d. Tuiles-chiffres (`tuiles-chiffres`)** — 3/8 (v2, v3, v4). Avec un symbole à halo : 1/8 (v2).
Une partie des tuiles porte un chiffre en grand, un petit mot au-dessus (« jusqu'à ») et un libellé dessous. En v2, jusqu'à 7 tuiles-chiffres et une tuile où le symbole du produit brille d'un halo coloré.

**e. Thème en mots et matières (`theme-et-matieres`)** — 2/8 (v2, v4).
Un récap transversal (environnement, santé), pas un produit. Les tuiles portent surtout des mots et des matières en fond (circuit, granulés, gros plan). La tuile centrale associe une image et une phrase.

**f. Grille d'icônes (récap du direct) (`grille-icones`)** — 1/8 (v6).
Pas de tuile centrale : deux ou trois rangées d'icônes égales, une par nouveauté, sans texte. C'est le récap des keynotes en direct, qui n'ont pas de bento (0/2).

**g. Logiciel en fragments (`fragments-logiciel`)** — hors corpus : 7 slides de récap de sessions pour développeurs (WWDC 2023 à 2025 : deux récaps de plateforme, cinq récaps d'un framework d'interface), relevées sur une galerie publique de slides de récap ; géométrie mesurée au pixel sur 5 d'entre elles (`style-visuel.md` §3 A14), le reste relevé à l'œil.
C'est le récap d'un logiciel : une plateforme, ou un outil métier vendu en SaaS. Il n'y a pas de produit à photographier ; ce qu'on montre, ce sont les fonctions.
- Pas de grille 3 × 3 : de 5 à 16 tuiles de tailles très inégales. La tuile qui ancre porte le nom de la plateforme ou son logo, au centre ou presque.
- Chaque tuile associe un nom de fonction (2 ou 3 mots) et un fragment de l'interface : une fenêtre, un menu, une carte, un réglage, trois lignes de code. Jamais un écran entier réduit.
- Le fragment sort le plus souvent par un bord de la tuile (une fenêtre coupée à droite ou en bas). Sinon il flotte entier : un petit panneau posé sur la tuile.
- Le nom se pose en haut à gauche, au-dessus ou à côté du fragment ; il n'est centré sous le visuel que dans les tuiles-icônes.
- Une tuile-photo d'usage au plus : une personne qui se sert de la plateforme, titre en blanc en bas à gauche.
- Une tuile-liste en aplat de couleur, avec quatre ou cinq mots empilés (les qualités du langage, par exemple), dans un récap sur sept.
- Les marges extérieures sont deux à trois fois plus larges que dans les bentos de keynote.

Ce que la skill en garde (convention de la skill, éprouvée sur un cas réel) :
- **les tuiles suivent la démo.** Trois zones de gauche à droite, dans l'ordre où la démo a montré les choses : ce que l'utilisateur configure, ce que son client fait, ce qu'il en tire. Une tuile par parcours montré, rien de neuf.
- **la tuile centrale est sombre** sur un deck clair (aplat `fond_sombre`) et en accent sur un deck sombre. Elle porte le logo clair (`image`, facultatif), puis le nom ou la boucle de la démo en trois mots, un par ligne (« Configurer. Vendre. Encaisser. »), et une phrase à droite au plus (`texte`).
- **une tuile `fragment`** se compose d'un nom de 4 mots au plus, en haut à gauche, d'une ligne de 5 mots au plus qui le situe, et d'un composant isolé de son écran. Le composant est posé à sa taille d'interface : 1 px de l'export vaut 1 px d'un écran de 1 920 px (`echelle` 0,5 pour un export 2x). S'il tient, ou s'il dépasse de moins de moitié, il est montré entier, réduit au besoin et calé en bas. Au-delà, il garde sa taille et sort par la droite et par le bas. Un composant haut (une colonne de statuts, un panneau) se place à droite du nom. Un filet de 0,5 pt le détache d'une tuile de même couleur. Pas d'ombre : la skill garde la règle du §4.
- **une seule tuile d'accent**, la tuile-liste (`liste` : un surtitre, puis 4 ou 5 lignes de 2 à 4 mots), sur un deck clair. Sur un deck sombre, l'accent passe à la tuile centrale.
- **au plus une tuile-photo et une tuile-chiffre.** La photo montre le métier du public. Le chiffre est sourcé, comme partout.
- de 6 à 11 tuiles. En dessous de 11, des cases fusionnent deux à deux ; il n'y a jamais de trou.

**Non retenue pour le moteur : le bento sur l'écran du décor** — 3/8 (v1, v7, v8). La même grille repasse sur le mur ou sur le panneau, l'orateur à côté ou incrusté devant. C'est un plan de scène (A22), pas une slide.

**Contenus de tuile** (on les combine dans toutes les variantes) :

| Contenu | N/8 | Keynotes |
|---|---|---|
| Icône ou pictogramme + libellé | 6/8 | v1, v2, v7, v8, v3, v4 |
| Capture ou appareil coupé par le bord de la tuile | 4/8 | v7, v8, v3, v4 |
| Photo d'usage à fond perdu dans la tuile | 4/8 | v7, v8, v3, v4 |
| Mot seul en couleur | 4/8 | v2, v8, v3, v4 |
| Chiffre + libellé | 3/8 | v2, v3, v4 |
| Jauge dessinée (batterie pleine, durée dedans) | 3/8 | v2, v3, v4 |
| Matière ou texture en fond de tuile | 3/8 | v2, v3, v4 |
| Tuile en aplat de couleur (au lieu du gris) | 3/8 | v2, v8, v4 |
| Rangée de coloris | 2/8 | v3, v4 |

#### 4. Contenu visuel

- **Types d'images** : captures de l'interface réelle, rendu détouré du produit (tuile centrale), icônes au format app (carré arrondi), photos d'usage, matières en gros plan, chiffres.
- **Cadrage** :
 - un appareil ou une capture est coupé par le bord haut ou latéral de sa tuile : il « sort de la tuile » (4/8 : v7, v8, v3, v4) ;
 - une photo remplit sa tuile à fond perdu, coins de la tuile compris (4/8) ;
 - le produit central est entier et centré, sur environ 76 % de la largeur et 86 % de la hauteur de sa tuile ;
 - dans la variante c, le produit coupe le bas du mot et sort par le bas de la tuile (2/2).
- **Traitement** :
 - tuiles en aplat, sans bordure ni ombre, même rayon (`style-visuel.md` §3 A14, 5 images ; revu sur 24 bentos) ;
 - sur fond clair, tuiles blanches sur un gris très clair (5/8 : v2, v7, v8, v3, v4) ; sur fond sombre, tuiles gris très sombre, vers 11 à 12 % de blanc (4/8 : v1, v2, v3, v4) ;
 - tuiles translucides sur un fond flou : 1/8 (v7, une plateforme). Non retenu : la skill garde l'aplat ;
 - halo : seulement autour du symbole de la puce en v2 (1/8). Aucun reflet ;
 - le produit central n'a aucune ombre visible (4 tuiles-produit sur 4 : v2, v3, v4) ; la skill tolère une ombre de contact très douce sur fond clair.
- **Accent** : le corpus colore la tuile centrale « nom » d'un dégradé (3/3) et pose une couleur par tuile (3/8 : v2, v3, v4). La skill garde une seule couleur d'accent : l'aplat d'accent de la tuile centrale, les chiffres de tuile et les mots-couleur. Le dégradé reste réservé au chiffre A5 (`style-visuel.md` §4.2).

#### 5. Typographie

Mesures : `style-visuel.md` §3 A14. Le bento est la seule slide où un texte descend sous 3 % H.

Ce qui change selon la variante :
- **produit au centre** : aucun texte dans la tuile centrale (4/4). Le nom est dit, ou posé dans une tuile « mot ».
- **mot géant** : le mot fait de 62 à 106 pt (cap de 11 à 19 % H, mesuré sur v3 et v4), en accent ; 84 pt par défaut. Il ne fait que 2 à 5 lettres.
- **tuile-chiffre** : petit mot au-dessus en 11 pt regular, chiffre en 48 pt, libellé en 11 pt.
- **tuile-photo** : un titre de 18 à 22 pt, en blanc, posé en bas à gauche sur la photo (v8, v4).
- **tuile-mot** : 22 à 26 pt, graisse 600, centré, en accent (v2, v8, v4).

#### 6. Apparition et animation

- La tuile centrale est là avant les autres (v1, v7, v4 : 3/8) ; en v7, on la voit entrer seule, en fondu.
- Les autres tuiles arrivent ensuite autour d'elle, du centre vers les bords : en v1, elles apparaissent par vagues ; en v4, on les voit glisser vers leur place, encore translucides.
- Variante : la grille complète se révèle par un dézoom depuis un recadrage serré (1/8 : v2).
- Moteur : la centrale au clic, toutes les autres en un seul clic après elle, en fondu avec un glissement de 2 % vers leur place, 0,4 s, décalées de 0,05 s (convention). Jamais un clic par tuile : le bento se regarde pendant une phrase.

#### 7. Brief du visuel et repli

Une ligne par tuile : « tuile n : type, ce qu'elle montre ». Puis, selon le type :
- **produit (tuile centrale)** : rendu détouré, PNG sur fond transparent, vue de face ou de trois-quarts, lumière douce, sans ombre intégrée, au moins 1 000 px de haut (le produit fait environ 440 px de haut sur une slide de 1 920 × 1 080 ; on double pour la netteté).
- **capture** : PNG de l'écran réel, au moins 1 200 px sur le grand côté. Elle sera coupée par le haut de la tuile : garder l'essentiel dans les deux tiers bas.
- **icône** : SVG, ou PNG transparent carré d'au moins 512 px.
- **photo** : JPG d'au moins 1 600 px de large, sujet au centre ; elle sera recadrée à la forme de la tuile.
- **matière** : JPG d'au moins 1 200 px, sans texte ni logo.
- **chiffre** : le chiffre, son libellé et sa source.
- **fragment** (variante g) : un composant isolé de son écran, jamais une capture pleine page. Ce peut être une carte, une colonne de statuts, un bouton, trois lignes d'un tableau ou un menu. On entre dans la maquette (dans Figma, la frame, puis le calque du composant) et on l'exporte seul, en PNG à 2x (`echelle: 0.5`) ou à 1x, avec les données de démonstration de la maquette. Le serveur MCP de Figma ne rend un nœud qu'à 1x au plus : à cette taille, on l'affiche à l'échelle 1 ou en dessous, sinon le texte devient flou. On garde la partie qui dit la fonction : la colonne des statuts plutôt que le tableau entier. Une maquette gelée ne se retouche pas pour la slide.
- **photo d'usage** (variante g) : une banque d'images libre de droits convient, Unsplash ou Pexels (§2, règle 7). Sur Unsplash, filtrer sur « gratuit » et vérifier « Photo gratuite » sur la page de la photo. Sur Pexels, vérifier « Free to use ». Noter l'auteur pour les crédits. La photo montre le métier du public et son marché : les lieux, la signalétique, les objets et les gens du pays visé. Un public ne se reconnaît pas dans le décor d'un autre pays. Aucune marque lisible.

**Repli dessiné** (rien n'est inventé) : la tuile centrale « nom » en aplat d'accent avec le nom ; la tuile centrale « produit » avec une silhouette générique (volume arrondi, sans détail) ; les captures en interface schématique claire coupée par le bord de la tuile (`style-visuel.md` §5.2) ; les icônes en pictogramme géométrique gris (cercle, carré arrondi, trait) ; les photos en aplat voisin avec deux halos neutres ; les matières en aplat un peu plus sombre, sans motif ; les chiffres en marqueur estompé. Aucun nombre, aucun logo.

#### 8. À éviter

- Une bordure, une ombre ou un rayon différent d'une tuile à l'autre.
- Une grille de cases toutes égales : c'est un tableau, pas un bento. La tuile centrale doit faire deux à trois fois les autres.
- Une tuile qui présente une chose qu'on n'a pas encore dite.
- Plus de 4 mots dans une tuile.
- Un écran clair entier posé au milieu d'une tuile sombre (`style-visuel.md` §5.2) ; un appareil flottant, entier et petit, au milieu de sa tuile.
- Une tuile vide ou un cadre gris « image attendue ».
- Un dégradé de fond, ou plusieurs couleurs d'accent.
- Un logo de partenaire ou un nombre dans le repli.
- (variante g) Un écran entier réduit dans une tuile, illisible : prendre un composant.
- (variante g) Un composant agrandi au-delà de sa taille d'export : il devient flou.
- (variante g) Une tuile d'impacts ou de gains présentée comme un résultat alors que c'est une promesse : la passer en `[À VALIDER]`, ou citer la mesure.
- (variante g) Une photo hors du marché du public, ou qui montre une marque.

### A19 · Prix

#### 1. Rôle et moment

- Fin du bloc produit, juste avant la disponibilité (étape 15, `grammaire.md` §4.1).
- Présent dans **5/8** (v5, v6, v2, v3, v4). En conférence logicielle : 1/4 (v6, matériel pro seulement).
- Le nom arrive avant le prix : 5/5 keynotes à prix.
- Un prix de référence plus élevé le précède parfois : 2/8 (v5, v6).
- Toujours sur le fond du bloc (v4 : sur ses quelque 8 slides de prix).
- Pour des investisseurs, `publics.md` déconseille cette slide (`slide_prix: non`).

#### 2. Composition canonique : « colonne »

Le produit d'un côté, la pile de texte de l'autre. 3/8 (v6, v3, v4).

| Zone | x | y | l | h | Mesure ou règle |
|---|---|---|---|---|---|
| Produit | 11 | 5 | 29 | 90 | objet de 12 à 39 % L sur 91 % H (`style-visuel.md`) ; v4 : 4,7 à 90,8 % H |
| Nom | 47 | 37 | 46 | 10 | centré à 70 % L (7,0 in) |
| « À partir de » | 47 | 49 | 46 | 4,5 | collé au-dessus du prix |
| Prix | 47 | 53,5 | 46 | 9,5 | |
| Précision (HT, période, capacité) | 47 | 63,5 | 46 | 4,5 | |

Le bloc de texte est centré vers 50 à 53 % H (v3 et v4, 2 images mesurées). Le produit peut passer à droite et le texte à gauche (1 cas, v3).

```
+----------------------------------------------------------------+
|                                                                |
|       +-----------------+                                      |
|       |                 |                                      |
|       |                 |                                      |
|       |                 |                                      |
|       |                 |                                      |
|       |                 |                                      |
|       |                 |             Nom (40 pt)              |
|       |     PRODUIT     |                                      |
|       |                 |         a partir de (16 pt)          |
|       |                 |             PRIX (36 pt)             |
|       |                 |          precision (16 pt)           |
|       |                 |                                      |
|       |                 |                                      |
|       |                 |                                      |
|       |                 |                                      |
|       +-----------------+                                      |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `colonne`, `deux-offres`, `nom-en-haut`, `gamme-alignee`, `prix-heros` ou `ancrage`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

**a. Colonne (`colonne`)** — 3/8 (v6, v3, v4). La composition canonique.

**b. Deux offres (`deux-offres`)** — 3/8 (v6, v3, v4).
Deux piles l'une sous l'autre (v3, v4) ou côte à côte (v6). Le produit montre les deux modèles, le grand derrière. Mesuré sur v4 : première offre de 18 à 44 % H, seconde de 59 à 86 % H, centrées à 70 % L.

**c. Nom en haut, produit dessous (`nom-en-haut`)** — 1/8 (v2), sur fond clair.
Le nom en haut (capitales entre 12,5 et 20 % H), le prix dessous, le produit entier posé de 50 à 87 % H sur 55 % L.

**d. Gamme alignée (`gamme-alignee`)** — 1/8 (v3).
Quatre produits côte à côte, de 14 à 65 % H. Sous chacun, son nom, puis « à partir de » et son prix (72 à 86 % H). Les prix arrivent tous ensemble.

**e. Prix héros (`prix-heros`)** — 1/8 (v5), pour un service sans objet.
Le prix traité comme un chiffre A5, la période dessous.

**f. Ancrage (`ancrage`)** — 2/8 (v5, v6).
D'abord un prix de référence plus élevé (la valeur totale en v5, la machine d'en face en v6), puis le vrai prix. En v5, cinq secondes séparent les deux ; en v6, sept minutes.

**Non retenues** : les pastilles de taux en couleur (1/8 : v5) et la remise avec condition (1/8 : v4). Elles portent plusieurs nombres et des conditions : mieux vaut une slide A5 par taux, sourcée.

#### 4. Contenu visuel

- **Type** : rendu détouré du produit, éclairage de studio, sur le fond plein du bloc. Pour un service, aucun objet (variante e).
- **Cadrage** : le produit est très grand, de 86 à 91 % H (v3, v4). Il montre souvent deux vues qui se chevauchent, de dos et de face (2/8 : v3, v4). Il touche ou franchit un bord dans 2/8 (bracelet coupé en haut en v3, main coupée en bas en v4) : c'est permis.
- **Traitement** : aucune ombre visible sur noir (v6, v3, v4 : 3/3) ; sur fond clair, une ombre de contact très douce au plus (v2). Aucun halo, aucun reflet.
- **Accent** : le prix est dans la couleur du texte dans 4/5 keynotes à prix (v6, v2, v3, v4). Seul v5 met un prix en couleur. La skill garde le prix dans la couleur du texte (le surtitre ou le point peuvent porter l'accent), sauf pour la variante « prix héros », qui suit le chiffre A5.
- **Devise** : le symbole est en exposant dans 4/8 (v6, v2, v3, v4). En français, la skill garde la norme typographique (« 89 € HT », symbole après le nombre, espace insécable, même corps).

#### 5. Typographie

Corps, graisses et écarts : `style-visuel.md` §3 A19.

Ce qui change :
- **gamme alignée** : nom 20 pt, petit 11 pt, prix 24 pt (cap de 3 à 3,6 % H, mesuré sur v3).
- **prix héros** : prix à 144 pt (cap de 27 % H), période 18 pt regular, comme A5.
- **ancrage** : le prix de référence est au même corps que le vrai prix, en gris secondaire ; le vrai prix prend sa place.

#### 6. Apparition et animation

- Le produit et le nom d'abord, puis le prix en fondu, puis la seconde offre (v4 : trois images à 3 s d'intervalle ; v3 : prix saisi en plein fondu).
- Le prix peut changer en place pour une seconde offre (1/8 : v2) : Morphose entre deux slides identiques.
- L'ancrage se joue en deux slides : le prix de référence, un silence, puis le vrai prix au même endroit.

#### 7. Brief du visuel et repli

- Le rendu détouré du produit (ou des deux modèles), PNG sur fond transparent, vue de face et de dos si possible, même lumière pour les deux, au moins 2 000 px de haut (le produit occupe 90 % de la hauteur).
- Le prix exact, HT ou TTC, la période ou la capacité, la mention « à partir de » si elle s'applique.
- Pour l'ancrage : le prix de référence, ce qu'il recouvre, et sa source.

**Repli dessiné** : une silhouette générique à la place du produit (volume modelé, règle 6 du §3 ; sans bouton, caméra ni logo), dans la même zone ; dans la gamme alignée, toutes à la même échelle sur la même ligne ; le prix en marqueur estompé au corps du prix. Jamais de prix proposé, jamais de prix de référence inventé.

#### 8. À éviter

- Le prix avant le nom.
- Plus de deux offres sur la slide, sauf la gamme alignée de quatre.
- Un astérisque, un prix barré ou une note sous le prix : les réserves vont au carton final (7/7 keynotes chiffrées).
- Un dégradé sur le prix, ou le prix et le nom tous deux en accent.
- Un tableau comparatif des offres.
- « À partir de » plus gros que 0,45 fois le nom.
- Un petit produit qui flotte au milieu d'un grand vide.

### A20 · Disponibilité

#### 1. Rôle et moment

- La toute dernière étape d'une annonce, juste après le prix quand il y en a un (étape 15). Présente dans **8/8**.
- En conférence logicielle, les dates sont groupées à la fin de la keynote (4/4 : v6, v1, v7, v8) ; en v8, dans les 30 dernières secondes de parole.
- Elle précède le relais retour ou la clôture.

#### 2. Composition canonique : « haut et gamme »

Le petit libellé et la date en haut, la gamme dessous, calée en bas. 6/8 (v1, v2, v3, v4, v7, v8).

| Zone | x | y | l | h | Mesuré |
|---|---|---|---|---|---|
| Libellé | 30 | 7 | 40 | 4,5 | haut des capitales de 5,6 à 11,9 % H (v2, v3, v4, v8) |
| Date ou mot | 10 | 12,5 | 80 | 11 | capitales de 12 à 28 % H, descendantes comprises |
| Gamme | 4 | 30 | 92 | 59 | de 28-38 % H à 88-90 % H ; 4 à 96 % L pour une gamme, 20 à 80 % L pour trois objets |

Les mêmes positions en pouces : `style-visuel.md` §3 A20.

```
+----------------------------------------------------------------+
|                                                                |
|                        libelle (16 pt)                         |
|                                                                |
|                          DATE (40 pt)                          |
|                                                                |
|   +--------------------------------------------------------+   |
|   |                                                        |   |
|   |                                                        |   |
|   |                                                        |   |
|   |                                                        |   |
|   |                   GAMME calee en bas                   |   |
|   |                                                        |   |
|   |                                                        |   |
|   |                                                        |   |
|   |                                                        |   |
|   +--------------------------------------------------------+   |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `slide.variante` = `haut-et-gamme`, `suite-de-dates`, `colonne`, `date-et-lieux` ou `mot-seul`. Sans variante : le rendu d'origine, plus simple que les variantes. Champs de chaque variante : `deck-spec.md`, « Variantes ».

**a. Haut et gamme (`haut-et-gamme`)** — 6/8 (v1, v2, v3, v4, v7, v8). La composition canonique.

**b. Colonne (`colonne`)** — 5/8 (v5, v6, v3, v4, v7).
Le même cadre que la slide de prix : le produit à gauche (de 5 à 58 % L selon l'objet), la date à droite, centrée vers 73-74 % L ; libellé de 39 à 42 % H, date de 46 à 54 % H (v3, v4).

**c. Suite de dates sur la même image (`suite-de-dates`)** — 7/8 (v1, v2, v3, v4, v6, v7, v8).
Le visuel ne bouge pas ; le libellé et la date changent en place, deux à trois fois en une dizaine de secondes (11 s en v7). C'est un déroulé de a ou b.

**d. Date et lieux (`date-et-lieux`)** — 3/8 (v1, v5, v7) pour une disponibilité par pays ; sous forme de liste de noms : 1/8 (v7).
Le produit à gauche ; à droite, la date puis la liste des pays, un par ligne. v1 et v5 montrent des drapeaux ronds : non retenu (on ne dessine pas de drapeau).

**e. Mot seul (`mot-seul`)** — convention de la skill pour une slide sans visuel. Le plus proche observé : la date seule sur une image plein cadre (1/8 : v2). Une seule image proche, pas de second exemple.

**Non retenues** : le libellé en capitales d'accent (1/8 : v5) et le texte incliné en perspective sur le mur de scène (1/8 : v6).

#### 4. Contenu visuel

- **Type** : la gamme des appareils ou produits concernés, de face, chacun avec son écran allumé ; ou le produit seul, repris de la slide de prix (variante b).
- **Cadrage** : la gamme est alignée par le bas, à l'échelle réelle des objets les uns par rapport aux autres, les petits devant les grands (4/8 : v1, v2, v7, v8). Elle prend presque toute la largeur.
- **Traitement** : même image sur tous les écrans de la gamme (v2, v8 : 2/8). Aucune ombre visible sur noir ; sur clair, une ombre de contact très douce au plus. Le fond clair irisé de v8 (1/8) n'est pas repris : fond plein.
- **Accent** : aucun dans 7/8. Le libellé est gris, la date dans la couleur du texte. Seul v5 met le libellé en couleur.

#### 5. Typographie

Mesures, version sans visuel comprise : `style-visuel.md` §3 A20.

Ce qui change :
- **colonne** : mêmes corps ; bloc centré vers 46 % H et 73 % L (7,3 in).
- **date et lieux** : la liste en 18 pt, centrée, interligne k = 1,8, 3 à 6 lieux.

#### 6. Apparition et animation

- La gamme et le libellé, puis la date quand elle est dite.
- Puis la date change sur la même image (7/8) : Morphose entre deux slides de même mise en page, ou fondu. La gamme ne bouge pas.
- Le libellé peut changer avec la date (v2, v3, v4 : de la précommande à la disponibilité).

#### 7. Brief du visuel et repli

- Un PNG détouré par produit, tous de face, même lumière, écrans allumés avec la même image, au moins 1 500 px de haut pour le plus grand ; indiquer la taille réelle de chacun pour respecter l'échelle. Ou un visuel déjà composé, PNG transparent d'au moins 3 600 × 1 500 px.
- La date exacte (jour ou mois), le libellé (disponible, précommande, bêta…), et les lieux s'il y en a.

**Repli dessiné** : trois ou quatre silhouettes génériques de tailles différentes (écran large, tablette, téléphone, boîtier), alignées en bas, chacune avec une interface schématique claire ; aucun logo, aucun drapeau. La date en marqueur estompé au corps de la date.

#### 8. À éviter

- Une date relative à l'écran (« dans quinze jours ») : on l'écrit en clair et on la dit en relatif (4/8).
- Une phrase entière ; plus de quatre mots en tout.
- Deux dates sur la même image : on fait une suite de dates.
- Un libellé plus gros que 0,46 fois la date.
- Des produits à des échelles fausses, ou un appareil reconnaissable dans le repli.
- Des drapeaux dessinés, ou un texte incliné en perspective.

### FIN · Slide finale

Dans un deck, c'est la dernière slide : `"archetype": "FIN"`, ou un A1 avec une variante ci-dessous. Elle passe en pleine page d'accent seulement en A1 ou FIN, sans variante ou avec `aplat` ou `mot-final`, et si `theme.finale_accent` n'est pas `false`.

#### 1. Rôle et moment

- Le dernier écran, après le remerciement de l'hôte. Le carton final existe dans **8/8** : il porte aussi tout le juridique et, selon le public, les sources (`publics.md`).
- Juste avant lui, l'hôte fait un récap global : le sommaire repris (2/8 : v7, v8), la gamme entière à l'écran (2/8 : v4, v6), une photo de groupe (1/8 : v5). Exemples : ,.
- Il reste longtemps : jusqu'à deux minutes de logo fixe en fin de vidéo (v2).

#### 2. Composition canonique : « signe seul »

Un seul signe, centré, et les mentions en très petit en bas. 6/8 (v1, v2, v3, v4, v7, v8).

| Zone | x | y | l | h | Mesuré |
|---|---|---|---|---|---|
| Signe (logo) | 40 | 34 | 20 | 27,5 | de 34,2 à 61,1 % H, centre à 47,7 % H, 12 % L de large (v2, v3, v4, v8, à 1 % près) |
| Mentions | 10 | 86 | 80 | 8 | en bas dans 7/8 (v1 les met sur un carton à part) ; cap de 1,4 à 1,9 % H, de 76 à 94 % H selon la longueur, 80 % L au plus |

Les mêmes positions en pouces : `style-visuel.md` §3, slide finale.

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                          +----------+                          |
|                          |          |                          |
|                          |  SIGNE   |                          |
|                          |          |                          |
|                          +----------+                          |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                        mentions (9 pt)                         |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `"archetype": "FIN"`, ou la variante posée sur n'importe quel archétype (souvent A1). `slide.variante` = `signe-seul`, `signe-et-ligne`, `signe-et-evenement`, `signe-sur-photo` ou `mot-final` ; sans variante, `signe-seul`. Champs de chaque variante : `deck-spec.md`, « Variantes ».

**a. Signe seul (`signe-seul`)** — 6/8 (v1, v2, v3, v4, v7, v8). La composition canonique.

**b. Signe et une ligne (`signe-et-ligne`)** — 3/8 (v3, v7, v8).
Une phrase courte sous le signe, sur la fabrication de l'événement (cap de 3 à 4 % H, ligne de base vers 89 à 93 % H). Les mentions viennent sur le carton suivant.

**c. Signe, nom de l'événement et lieu (`signe-et-evenement`)** — 3/8 (v2, v5, v6).
Deux lignes sous le signe : le nom de l'événement en demi-gras (entre 67 et 82 % H selon la keynote ; 70 à 75 % H en v2), le lieu en gris juste dessous, puis les mentions. v5 éclaire le signe d'un faisceau venu du haut (1/8) ; v6 remplace le signe par l'illustration de l'événement (1/8).

**d. Signe sur une photo calme (`signe-sur-photo`)** — 1/8 (v7).
Le signe et la ligne en blanc sur une photo de ciel à fond perdu.

**e. Mot final (`mot-final`)** — convention de la skill, non observée en carton de texte seul (0/8). Un mot au corps A1, point final en accent ; il peut passer en pleine page d'accent (convention, `style-visuel.md` §3, slide finale). Pas d'image d'exemple : c'est une convention.

#### 4. Contenu visuel

- **Type** : le logo de l'utilisateur, monochrome, sans effet. Blanc sur noir dans 7/8 ; blanc sur ciel en v7.
- **Cadrage** : centré, entier, petit (12 % L), avec beaucoup de vide autour.
- **Traitement** : une fois posé, le signe est net et sans effet dans 7/8 ; seul v5 l'éclaire d'un faisceau venu du haut. Un flou ou une lueur ne se voient qu'à son arrivée (v1, v3). La skill ne pose aucun effet.
- **Accent** : aucun sur le logo. Pour un mot final, l'accent ne va que sur le point final.

#### 5. Typographie

Mesures : `style-visuel.md` §3, slide finale.

Ce qui change :
- **signe et ligne** : ligne en 22 pt (cap de 3 à 4 % H, mesuré sur v3 et v7) ; sous-ligne facultative en 9 pt.
- **signe et événement** : nom en 24 pt, graisse 600 (cap de 3,6 à 5 % H, v2, v5, v6) ; lieu en 16 pt regular secondaire (cap de 2,2 à 3 % H).

#### 6. Apparition et animation

- Le signe entre seul, en fondu (v3), ou arrive grand et flou puis se pose (1/8 : v1).
- La ligne ou les mentions viennent après le signe, sur un second carton identique, dans 4/8 (v1, v3, v7, v8).
- Rien ne boucle. En salle, la slide reste pendant les applaudissements ou les questions.

#### 7. Brief du visuel et repli

- Le logo en SVG, ou en PNG transparent d'au moins 1 000 px de haut, en version monochrome claire et foncée.
- La ligne finale, si l'utilisateur en veut une ; le nom de l'événement, le lieu et la date pour la variante c.
- Les mentions et les sources du carton.
- Pour la variante d : une photo 16:9 d'au moins 1 920 × 1 080 px, sans sujet net, avec du calme au centre.

**Repli dessiné** : sans logo, la variante « mot final » (un mot très gros, point final en accent). Jamais de logo dessiné ni de monogramme inventé. Sans photo, le fond plein.

#### 8. À éviter

- « Des questions ? », une adresse, un paragraphe.
- Un logo en couleur sur un fond de couleur ; un logo plus haut que 30 % H.
- Des mentions au-dessus de 12 pt, ou en blanc plein.
- Plusieurs logos (partenaires) sur la finale.
- Une phrase de fabrication qu'on ne peut pas tenir.
- Un fond qui change pour la seule finale, sauf la pleine page d'accent prévue par la skill.

### COLORIS · Gamme de coloris

Dans un deck, la gamme passe par `"variante": "rangee-alignee"` (ou une autre variante ci-dessous) sur la slide produit, souvent un A13. La tuile de coloris du bento (variante f) se pose dans A14, avec une tuile `"type": "coloris"`.

#### 1. Rôle et moment

- Dans un bloc produit, après les piliers et avant le récap : « piliers, coloris et accessoires, récap, prix, dates » (l'analyse du corpus, variante produit).
- Présente dans **3/8** (v6, v3, v4). Dans les événements produits : 2/3 (v3, v4 ; pas en v2). En v1, une rangée de montres aux bracelets de couleurs accompagne un récap de cadrans : variante (x), non comptée.
- Les noms des coloris sont dits, jamais écrits : aucun libellé sur les plans de coloris regardés (3/3 keynotes).
- La gamme revient en petit dans une tuile du bento (2/8 : v3, v4).

#### 2. Composition canonique : « rangée alignée »

De deux à cinq produits côte à côte, un par coloris, même angle, même échelle, entiers, centrés.

| Zone | x | y | l | h | Mesuré |
|---|---|---|---|---|---|
| Rangée (4 coloris) | 5 → 95 | 18 | 4 × 20,5, écart 2,5 | 62 | v3 : 3-98 % L × 21-79 % H ; v4 : 11-88 % L × 14-85 % H et 17-84 % L × 20-80 % H |

Maximum observé : 5 coloris sur une rangée (v3, 2 fois). Aucun ordre constant des couleurs (0/5 rangées).

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|   +-----------+  +-----------+  +-----------+  +-----------+   |
|   |           |  |           |  |           |  |           |   |
|   |           |  |           |  |           |  |           |   |
|   |           |  |           |  |           |  |           |   |
|   |           |  |           |  |           |  |           |   |
|   | coloris 1 |  | coloris 2 |  | coloris 3 |  | coloris 4 |   |
|   |           |  |           |  |           |  |           |   |
|   |           |  |           |  |           |  |           |   |
|   |           |  |           |  |           |  |           |   |
|   |           |  |           |  |           |  |           |   |
|   +-----------+  +-----------+  +-----------+  +-----------+   |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `"archetype": "COLORIS"`, ou la variante posée sur n'importe quel archétype (souvent A13). `slide.variante` = `rangee-alignee`, `rangee-chevauchee`, `eventail`, `un-par-un` ou `mur` ; sans variante, `rangee-alignee`. Champs de chaque variante : `deck-spec.md`, « Variantes ».

**a. Rangée alignée (`rangee-alignee`)** — 2/8 (v3, v4). La composition canonique, sur fond clair ou sombre.

**b. Rangée en escalier, coupée par le cadre (`rangee-chevauchee`)** — 1/8 (v3).
Les produits se chevauchent, chacun devant le précédent, et sortent par le bas du cadre (ou par le haut et le bas, vus de profil). Fond sombre.

**c. Éventail (`eventail`)** — 1/8 (v3).
Un produit à plat devant ; les autres coloris pivotent derrière lui autour d'un même bout. Fond clair.

**d. Un par un, même cadre (`un-par-un`)** — 1/8 (v4).
Le produit reste à la même place ; seule sa couleur change, d'une image à l'autre. Variante proche : un gros plan par coloris, en plans successifs.

**e. Mur de coloris (`mur`)** — 1/8 (v6).
Des dizaines de produits en quinconce, qui débordent du cadre de tous les côtés. Pour dire « il y en a beaucoup ».

**f. Tuile de coloris dans le bento** — 2/8 (v3, v4). Trois ou quatre produits en rangée dans une tuile, un libellé dessous. Voir A14.

#### 4. Contenu visuel

- **Type** : rendus détourés identiques, un par coloris, même lumière.
- **Cadrage** : entiers et centrés (a, c, d) ; coupés par le cadre (b, e). Même angle pour tous (5 rangées sur 5).
- **Traitement** : fond plein, clair (v3, v4) ou sombre (v6, v3, v4). Aucune ombre visible sur noir ; sur clair, ombre de contact très douce au plus. En d, une lumière douce venue du haut éclaire le produit (halo très doux sur le fond).
- **Accent** : aucun. Les coloris sont la couleur de la slide ; on n'en ajoute pas (0 accent vu sur les plans de coloris).

#### 5. Typographie

Aucun texte (3/3 keynotes). Option, par convention : le nom de chaque coloris en 16 pt regular secondaire, centré sous son produit vers 86 % H, quand le public regarde sans le son (salon, vidéo muette). Pas de surtitre.

#### 6. Apparition et animation

- Rangée : en un fondu, pendant que les coloris sont nommés.
- Escalier : les produits glissent un par un depuis le bas.
- Éventail : le produit de devant, puis l'éventail s'ouvre derrière lui.
- Un par un : une slide par coloris, en Morphose, au rythme où chaque couleur est nommée.

#### 7. Brief du visuel et repli

- Un PNG sur fond transparent par coloris, tous au même angle, au même cadrage et sur un canevas de même taille (pour qu'ils s'alignent), au moins 2 000 px de haut.
- La liste des coloris : nom et HEX de chacun.
- Pour l'éventail, une vue de dos ou de profil ; pour la variante d, un gros plan par coloris (JPG d'au moins 1 920 px de large).

**Repli dessiné** : des silhouettes génériques identiques, remplies des HEX de coloris fournis par l'utilisateur et modelées par la même lumière (haut éclairci, bas assombri, arête claire), pour se lire comme des objets et non comme des nuanciers. Sans HEX, des paliers de gris tirés du fond, et l'image passe en « Image à fournir » : aucune couleur n'est inventée. Aucun texte, aucun nombre.

#### 8. À éviter

- Des pastilles de couleur à la place du produit (un nuancier n'est pas un produit).
- Les noms des coloris écrits en gros.
- Des angles, des échelles ou des lumières différents d'un coloris à l'autre.
- Des produits qui flottent sans ligne de base commune.
- Plus de cinq coloris sur une rangée : au-delà, un mur.
- Une couleur de coloris que l'utilisateur n'a pas validée.

### FRISE · Frise ou chronologie

Dans un deck, la frise passe par `"variante": "rangee-datee"` (ou une autre variante ci-dessous), souvent sur un A6 à l'étape d'ancrage.

#### 1. Rôle et moment

- À l'étape 2 « Ancrage », pour rappeler l'héritage (`grammaire.md` §4.1, colonne Visuel : « frise ; produit ancien seul »).
- En slide : **3/8** (v1, v2, v7), toujours pour une technologie maison (la puce, 3/3). À côté : un objet du passé montré seul, 2/8 (v1, v8, variante e) ; un film de générations en plans successifs, (x) v4.
- Elle prépare une preuve : la frise de v1 se resserre sur le dernier jalon, puis laisse place à un chiffre héros ; celle de v2 se termine par l'écart chiffré ; les trois jalons de v1 mènent à une phrase-thèse.

#### 2. Composition canonique : « rangée de jalons »

De 5 à 10 tuiles carrées égales, en ligne sur toute la largeur, la date sous chacune. 2/8 partagent cette structure (v1 avec dates, v7 sans dates).

| Zone | x | y | l | h | Mesuré |
|---|---|---|---|---|---|
| Rangée de 6 jalons | 4 → 96 | 30 | 13 chacun, écart 2,8 | 23 | v1 : 10 tuiles de 2 à 96 % L, de 41 à 51 % H ; v7 : 5 tuiles de 4,7 à 95 % L, de 35 à 65 % H |
| Dates | sous chaque tuile | 57 | 13 | 5 | v1 : de 58 à 61 % H (cap de 2,7 % H) |
| Jalon actuel | le dernier, à droite | | | | seul en accent (convention) |

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|   +------+  +------+  +------+  +------+  +------+  +------+   |
|   |      |  |      |  |      |  |      |  |      |  |      |   |
|   |jalon |  |jalon |  |jalon |  |jalon |  |jalon |  |actuel|   |
|   |      |  |      |  |      |  |      |  |      |  |      |   |
|   +------+  +------+  +------+  +------+  +------+  +------+   |
|     date      date      date      date      date      date     |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
```

#### 3. Variantes observées

**Dans le moteur** : `"archetype": "FRISE"`, ou la variante posée sur n'importe quel archétype (souvent A6). `slide.variante` = `rangee-datee`, `generations`, `trois-jalons`, `courbe-et-saut` ou `objet-du-passe` ; sans variante, `rangee-datee`. Champs de chaque variante : `deck-spec.md`, « Variantes ».

**a. Rangée datée (`rangee-datee`)** — 1/8 (v1). Dix tuiles égales, une date sous chacune.

**b. Générations sans date (`generations`)** — 1/8 (v7). Cinq tuiles carrées plus grandes, le nom dans chaque tuile ; les tuiles passent d'une image (le plan de la puce) à leur nom.

**c. Trois jalons en objets (`trois-jalons`)** — 1/8 (v1). Trois objets historiques côte à côte (de 28 à 72 % H, de 8 à 92 % L), sans date, qui arrivent un par un.

**d. Ligne plate, puis le saut (`courbe-et-saut`)** — 1/8 (v2). Un titre en haut, un axe du temps avec une date à chaque bout (86 à 89 % H), des pastilles sur une ligne presque plate, puis la nouveauté qui saute au-dessus avec une flèche et l'écart en accent. Aucune graduation.

**e. Un objet du passé, seul (`objet-du-passe`)** — 2/8 (v1, v8). L'ancien produit ou l'ancien écran, petit, centré, sans texte, juste avant le présent.

**Non retenue : le film de générations** — (x) v4. Un plan par génération, en macro. C'est un film, pas une slide.

#### 4. Contenu visuel

- **Type** : tuiles en aplat portant le nom ou le pictogramme de chaque jalon (a, b) ; objets historiques détourés (c, e) ; ligne et pastilles dessinées (d).
- **Cadrage** : la frise occupe toute la largeur, en une seule ligne (3/3). Aucune frise verticale (0/8).
- **Traitement** : tuiles sans bordure ni ombre, en gris très sombre sur noir (v1) ou en noir sur gris clair (v7). Le jalon nouveau se détache dans 2/3 : halo d'accent et saut (v2), seul resté à l'écran (v1).
- **Accent** : seulement sur le jalon actuel (et l'écart, s'il est écrit).

#### 5. Typographie

- Dates : 16 pt regular secondaire (cap de 2,7 à 2,8 % H, mesuré sur v1 et v2).
- Nom dans une tuile : 28 pt, graisse 600 (cap d'environ 5 % H, v7).
- Titre de la variante d : 28 pt, graisse 600, comme le titre d'un graphique A6.
- Écart de la variante d : 48 pt en accent, une seule valeur, sourcée.

#### 6. Apparition et animation

- De gauche à droite : un objet par clic (v1), ou la ligne qui se trace et les pastilles qui s'y posent (v2).
- La nouveauté arrive en dernier, au-dessus ou à part (v2).
- Les tuiles peuvent passer de l'image au nom (Morphose, v7).
- La frise peut se resserrer sur le dernier jalon, qui ouvre la slide suivante (v1).

#### 7. Brief du visuel et repli

- La liste ordonnée des jalons : nom et date de chacun.
- Une image ou un pictogramme par jalon, tous dans le même style : PNG transparent d'au moins 800 px.
- L'écart chiffré, s'il y en a un, avec sa source.
- Pour la variante e : une photo détourée de l'ancien produit, ou une capture de l'ancien écran.

**Repli dessiné** : tuiles en aplat avec un pictogramme géométrique gris, la dernière en accent ; dates en marqueurs estompés ; ligne et pastilles grises pour la variante d. Aucune date, aucune valeur proposée.

#### 8. À éviter

- Un axe gradué avec des valeurs.
- Plus de 10 jalons, ou des jalons de tailles inégales.
- Plus d'un mot ou d'une date sous un jalon.
- Des flèches décoratives entre les jalons.
- La chronologie d'un concurrent.
- Une date inventée pour combler un trou.
