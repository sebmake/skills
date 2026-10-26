# Style visuel : les mesures qui font « keynote »

Ce fichier ne contient que des **mesures et des règles**, jamais une image. Il est tiré de 67 images extraites de 8 keynotes (2019-2026), regardées une à une puis mesurées au pixel (méthode en annexe A). Le moteur (`scripts/build_deck.js`) applique ces valeurs ; `deck.json` n'en porte aucune.

Chaque valeur a un statut :
- **mesuré** : relevé sur les images, avec le nombre d'images ;
- **converti** : mesure traduite pour un canevas pptx 16:9 ;
- **convention** : choix de la skill, non observé (on le dit chaque fois).

La police du corpus n'a servi que de règle graduée pour la mesure. Elle reste interdite à l'usage, comme toute marque, tout logo, toute image ou tout appareil du corpus.

---

## 0. Unités et conversions

- **Canevas** : 10 × 5,625 in, soit 720 × 405 pt. H = hauteur, L = largeur. 1 % H = 4,05 pt = 0,056 in ; 1 % L = 7,2 pt = 0,1 in.
- On mesure la **hauteur de capitale** (« cap »), jamais le corps. C'est la seule taille qui se compare d'une police à l'autre.
- **Corps (pt) = cap (% H) × 4,05 / capEm.** capEm (hauteur de capitale par em) : Inter et Inter Tight 0,728 ; Arial 0,716 ; Helvetica Neue 0,714 ; police inconnue 0,72. Règle rapide : **corps ≈ cap (% H) × 5,6**.
- **Interligne** : donné en multiple de la cap (il ne dépend pas de la police), puis en points exacts. Le moteur pose l'interligne exact (`lineSpacing` de pptxgenjs, `a:spcPts`), pas `lineSpacingMultiple` : le « 1,0 » de PowerPoint dépend des métriques de chaque police (Arial 1,12 em, Inter 1,21 em). Formule : **interligne (pt) = k × capEm × corps**. L'aperçu HTML prend `line-height = interligne / corps`.
- **Suivi** : donné en em. **charSpacing (pt, pptxgenjs) = suivi (em) × corps (pt).** Par exemple, 144 pt × −0,035 em = −5 pt.
- **Centrage vertical** : avec `valign: middle`, le centre de la boîte tombe sur le centre de la zone des capitales à 0,01 em près, pour Inter comme pour Arial. On place donc la boîte par son centre, à la hauteur visée pour les capitales.

---

## 1. Les huit mesures qui font l'allure

| # | Règle | Mesuré | Itération 1 (pour comparaison) |
|---|---|---|---|
| 1 | **Très gros.** Carte-titre : cap de 14,5 à 19 % H (100 pt environ). Phrase-thèse : 9 % H (50 pt). Chiffre héros : 22 à 26 % H (144 pt). | 4 + 2 + 6 images | titre en cap de 7,1 % H (40 pt environ) : deux fois trop petit |
| 2 | **Centré sur le milieu.** La zone des capitales du bloc est centrée entre 46,5 et 50 % H. Rien ne flotte dans le tiers haut avec un vide dessous. Seuls le graphique, le prix et la disponibilité partent du haut, parce qu'un visuel occupe le bas. | 22 images | aperçu centré à 49 % H : le vide autour vient de la taille du texte |
| 3 | **Serré.** Suivi négatif dès 28 pt. Interligne des titres de 1,55 à 1,65 cap ; citations et sommaires de 1,35 à 1,5 cap. | 19 chaînes calibrées | suivi nul |
| 4 | **Demi-gras, pas noir.** Le rapport épaisseur du fût sur cap vaut de 0,163 à 0,208 (médiane 0,18) : entre medium et demi-gras. Une graisse 800 est 40 % trop épaisse. | 17 chaînes | Arial Bold de repli : 0,21 à 0,26 |
| 5 | **Deux niveaux de texte, pas plus.** Le texte principal et un secondaire, de 0,15 à 0,45 fois sa cap, en gris à 53 %. | toutes les images à texte | trois à quatre niveaux |
| 6 | **Une seule couleur d'accent par slide**, posée sur peu d'éléments : le nom, le chiffre, la barre de soi, les pictogrammes. | 67 images (exceptions : sommaire, bento, logos) | accent rose des marqueurs + jaune |
| 7 | **Fond plein, ni bordure ni cadre autour d'un texte, ni ombre sur du texte.** | 0 cas sur 67 images | encadrés pointillés, cadres gris |
| 8 | **Le visuel prend la place.** Appareil sur 89 à 100 % H, objet sur 50 à 60 % L, produit sur 60 à 86 % H, bento jusqu'aux bords (marge de 1 %). | 15 images | cadres gris « image attendue » |

---

## 2. Typographie commune

### 2.1 Graisse

**Mesuré** sur 17 chaînes de grande taille : le rapport fût/cap observé, comparé au même texte rendu dans chaque police au même cap.

| Police | Graisse | Fût rendu / fût observé | Verdict |
|---|---|---|---|
| Inter | 500 · 600 · 700 · 800 | 0,95 · 1,08 · 1,24 · 1,40 | **600** |
| Inter Display (opsz 32, proche d'Inter Tight) | 500 · 600 · 700 | 0,97 · 1,10 · 1,25 | **600** |
| Arial | 400 · 700 | 0,86 · 1,23 | **700** (pas de demi-gras) |
| Helvetica Neue | 500 · 700 | 1,02 · 1,26 | **500** |

| Rôle | Graisse |
|---|---|
| Titres, noms, chiffres, lignes de liste, citations, prix | demi-gras (600) ; Bold si la police n'a pas de demi-gras |
| Libellé sous un chiffre, texte à côté d'un objet, mot de disponibilité | demi-gras, ou medium |
| Surtitre gris, « À partir de », mention sous un prix, fonction d'un intervenant, source, mentions | regular (400) |
| Interdit | 800 et 900 |

**Poser le demi-gras dans le .pptx.** pptxgenjs ne connaît que `bold: true` (la graisse 700). Pour le 600, le moteur pose le **nom de famille hérité de la face demi-grasse** (nameID 1 du fichier de police), avec `bold: false`, quand cette face est installée : par exemple « Inter SemiBold », « Inter Tight SemiBold » ou « Inter 18pt SemiBold » pour les fichiers statiques de Google Fonts. Le moteur liste déjà les fichiers de police installés. Si la face manque, il prend la famille avec `bold: true`.

### 2.2 Suivi (charSpacing)

**Mesuré** : la largeur de 19 chaînes, comparée à leur rendu dans chaque police au même cap ; on en déduit l'écart par intervalle entre lettres. Écart d'une chaîne à l'autre : ±0,025 em environ. Les grands chiffres demandent le plus de serrage.

| Police (graisse des titres) | ≥ 50 pt | 28 à 50 pt | < 28 pt | Mesuré (médianes ≥ 50 / 28-50 / < 28) |
|---|---|---|---|---|
| Inter (600) | **−0,035 em** | **−0,035** | **−0,02** | −0,035 / −0,039 / −0,021 |
| Inter Tight (600) | **−0,02** | **−0,02** | **0** | estimé d'après Inter Display : −0,021 / −0,018 / +0,005 |
| Arial (Bold) | **−0,06** | **−0,045** | **−0,015** | −0,068 / −0,052 / −0,016 |
| Helvetica Neue (Medium) | **−0,045** | **−0,03** | **−0,01** | −0,046 / −0,026 / −0,003 |
| Police inconnue | **−0,03** | **−0,025** | **−0,01** | convention |

- Jamais au-delà de −0,07 em, et aucun serrage sous 14 pt.
- Inter Tight n'était pas installée sur la machine de mesure : sa ligne est une estimation. Refais la mesure (annexe A) dès que la police est disponible.
- **Crénage** : pptxgenjs écrit `kern="0"` dès qu'on pose un `charSpacing`, avec la mention « disable kerning » dans son code. Un titre serré sans crénage laisse des trous entre certaines paires (To, Av, Te). Le moteur remplace donc `kern="0"` par `kern="1200"` (crénage dès 12 pt) dans le XML des titres. À contrôler sur une capture après la première passe.

### 2.3 Interligne

| Usage | k (interligne / cap), mesuré | Valeur moteur | Exemple Inter |
|---|---|---|---|
| Phrase-thèse, titre sur 2 lignes | 1,55 à 1,66 (2 images) | **k = 1,6** | 50 pt → 58 pt |
| Citation | 1,48 (1 image) | **k = 1,5** | 36 pt → 39 pt |
| Sommaire empilé | 1,35 à 1,77, médiane 1,41 (3 images) | **k = 1,4** | 56 pt → 57 pt |
| Texte court à côté d'un objet | 1,50 (1 image) | **k = 1,5** | 34 pt → 37 pt |
| Liste de 3 à 6 lignes | 1,96 (1 image) ; 1,75 à 2,2 avec pictogrammes (2 images) | **k = 1,95** | 36 pt → 51 pt |
| Liste de 2 lignes | 3,1 (1 image) | **k = 3,1** | 36 pt → 81 pt |
| Liste courte à côté d'une icône, fiche de prix | 1,8 (1 image) | **k = 1,8** | 24 pt → 31 pt |
| Synthé : nom puis fonction | 2,0 (3 images) | **k = 2,0** | 16 pt → 23 pt |

### 2.4 Couleurs du texte

| Rôle | Mesuré | Valeur moteur |
|---|---|---|
| Fond clair | #F2F2F2 à #F9F9F9, jamais blanc pur (6 images) ; le blanc pur est réservé aux tuiles | `fond_clair` de l'utilisateur, tel quel |
| Fond sombre | noir pur (12 images) | `fond_sombre` de l'utilisateur, tel quel |
| Texte principal | noir ou blanc purs au cœur des lettres | `texte` (sur clair) ou blanc (sur sombre) |
| Texte secondaire | à 51-56 % du texte vers le fond (4 images, sur clair comme sur sombre) | **mélange à 53 % du texte vers le fond**, ou `texte_secondaire` s'il est fourni et lisible à 4,5:1 |
| Ligne « pas encore dite » | même valeur, 53 % (1 image) | comme le secondaire |
| L'autre, dans un graphique | gris à environ 45 % (1 image mesurée, 1 vue) | mélange à 45 % |

---

## 3. Fiches par archétype

Positions en pouces sur le canevas de 10 × 5,625 in. « centre y » est le centre visé de la zone des capitales, donc celui de la boîte posée avec `valign: middle`.

### A1 Carte-titre : un nom seul, centré

- **Mesuré (4 images)** : pour un mot, cap de 14,5, 19,0 et 19,0 % H ; pour deux mots, 11,3 % H. Largeur de 29 à 59 % L. Centre des capitales à 50 % H (±0,5) et à 50 % L. Une ligne. Fût/cap de 0,163 à 0,182. Couleur : texte, ou dégradé de la section (2 images sur 4).
- **Valeurs** :
  ```
  corps 100 pt (cap ≈ 18 % H) ; ajusté pour tenir sur une ligne dans 6.4 in, plancher 64 pt
  au-delà : 2 lignes, plancher 60 pt, interligne k = 1.6
  boîte x 0.6  w 8.8 · centre y 2.81 in (50 % H) · align center · valign middle
  suivi : classe ≥ 50 pt · graisse 600
  couleur : texte, ou accent uni (le nom porte alors l'accent de la slide)
  ```
- Le point final, s'il y en a un, prend la couleur d'accent, au même corps et à la même graisse. Le corpus n'en met pas : c'est un choix de la skill, validé sur le témoin. Il n'apparaît que sur A1, A4 et la slide finale.

### A4 Phrase-thèse : une ou deux lignes, centrées

- **Mesuré (2 images plein cadre, 1 sur un écran de scène)** : cap de 8,9 et 9,2 % H ; ligne la plus longue sur 66 à 74 % L ; deux lignes, la seconde à 55-70 % de la première ; interligne de 1,55 à 1,66 cap ; centre du bloc à 47,2 et 49,9 % H.
- **Valeurs** :
  ```
  corps 50 pt (cap ≈ 9 % H), plancher 44 pt : en dessous, le texte est trop long, on coupe des mots
  2 lignes au plus, équilibrées · interligne k = 1.6 (Inter 50 pt → 58 pt)
  boîte x 1.2  w 7.6 (76 % L) · centre y 2.73 in (48,5 % H) · align center
  suivi : classe ≥ 50 pt · graisse 600 · couleur texte ; accent sur un mot au plus
  ```
- **Coupure (convention)** : l'équilibrage des lignes évite qu'une ligne finisse sur un mot-outil (article, préposition, « ne », possessif) : « Une panne / ne prévient jamais. » plutôt que « Une panne ne / prévient jamais. ». Pénalité de 0,25 × le carré de la longueur moyenne, dans tous les textes équilibrés (titres, tuiles, colonnes A9). Un `\n` écrit dans `deck.json` reste prioritaire.

### A5 Gros chiffre + libellé : le moment héros

- **Mesuré (6 images)** : chiffre en cap de 21,6 à 26,1 % H (médiane 25,4) ; largeur de 19 % L (« 2× ») à 80 % L (nombre suivi d'un mot). Libellé en cap de 3,7 à 5,5 % H (médiane 4,2), soit 0,15 à 0,21 fois le chiffre, en demi-gras, **dans la couleur du texte** et non en gris. Deux mises en page :
  - (a) 4 images : la zone des capitales du chiffre est centrée sur le milieu (37 à 63 % H) et le libellé descend à 72-82 % H ;
  - (b) 2 images : le bloc entier est centré, le libellé collé sous le chiffre (écart de 6 % H).
  Le chiffre est en dégradé horizontal sur 4 images sur 6 (§4.2), sinon dans la couleur du texte.
- **Valeurs, mise en page (a) par défaut** :
  ```
  chiffre : corps 144 pt (cap ≈ 25,6 % H), sur une ligne, sans retour
            ajusté pour tenir dans 8.0 in, plancher 110 pt
            boîte x 1.0  w 8.0 · centre y 2.81 in (50 % H) · align center
            suivi : classe ≥ 50 pt (Inter −0.035 em, soit −5 pt) · graisse 600
            couleur : dégradé accent → accent2 (§4.2), sinon accent uni
  libellé : corps 24 pt (cap ≈ 4,3 % H) · graisse 600, ou 500 · couleur texte
            boîte x 0.8  w 8.4 · centre y 4.50 in (80 % H) · une ligne
  ```
- **Mise en page (b)**, quand le libellé tient sur deux lignes : centre du chiffre à 2.56 in (45,5 % H), haut des capitales du libellé à 3.54 in (63 % H), interligne k = 1.6.
- **Surtitre (convention)** : au corps du libellé (24 pt), ligne de base à 1.73 in, soit 0,25 cap du chiffre au-dessus de lui.
- **Chiffre manquant** : le marqueur `[À FOURNIR : …]` prend la place et le style du chiffre (§3.15). Écris son libellé en un mot (« gain », « délai ») pour qu'il reste au corps héros.

### A7 Liste sans puces : la ligne dite s'allume

- **Mesuré (2 images plein cadre)** : cap de 6,4 à 6,8 % H ; lignes centrées, larges de 18 à 85 % L ; interligne de 1,96 cap pour 3 lignes, de 3,1 cap pour 2 ; centre du bloc à 46,5-47,4 % H. La ligne dite est pleine, la suivante à 53 %.
- **Valeurs** :
  ```
  corps 36 pt (cap ≈ 6,5 % H) · graisse 600 · 5 mots par ligne au plus
  3 à 6 lignes : interligne k = 1.95 (Inter 36 pt → 51 pt) ; 2 lignes : k = 3.1 (81 pt)
  boîte x 1.0  w 8.0 · centre y 2.64 in (47 % H) · align center
  couleur : ligne dite = texte ; lignes à venir = secondaire à 53 % ; pas d'accent
  ```

### A8 Liste à coches

- **Mesuré (2 images sur scène)** : pictogramme haut de 1,1 à 1,15 cap, posé sur la ligne de base, à 0,6-0,9 cap du texte ; interligne de 1,75 à 2,2 cap ; texte aligné à gauche dans un bloc centré ; pictogrammes en accent, texte dans la couleur du texte.
- **Valeurs** :
  ```
  texte : corps 34 pt · graisse 600 · aligné à gauche · interligne k = 1.95
  pictogramme : hauteur = cap × 1.12, posé sur la ligne de base · écart 0.75 × cap · couleur accent
  bloc centré : largeur = ligne la plus longue + pictogramme ; centre y 2.64 in (47 % H)
  ```

### A9 Objet + texte

- **Mesuré (3 images)** :
  - l'objet occupe 59 % L, à fond perdu à gauche, sur toute la hauteur ; ou bien un appareil centré (25 % L × 91 % H) avec le texte à droite ;
  - l'affirmation : cap de 5,8 à 6,1 % H, en demi-gras, 1 ou 2 lignes, **centrée dans la colonne libre** (centre à 80-81 % L), interligne de 1,50 cap, centre à 50 % H ;
  - la variante avec icône : icône de 21 % L × 38 % H centrée à 22 % L ; trois lignes en cap de 4,2 % H, alignées à gauche à 45 % L, interligne de 1,8 cap.
- **Valeurs** :
  ```
  objet : x 0 → 5.6 in (fond perdu permis à gauche, en haut et en bas), h jusqu'à 5.625 in
  affirmation : corps 34 pt · graisse 600 · interligne k = 1.5
                colonne x 6.3  w 3.4 (centre 8.0 in) · align center · centre y 2.81 in
  variante icône : icône 2.1 × 2.1 in centrée en (2.2 in, 2.81 in)
                   lignes : corps 24 pt · aligné à gauche à x 4.5 in · interligne k = 1.8
  ```

### A10 Capture plein cadre, A13 Produit seul

- **Mesuré** : appareil centré sur 89 à 100 % H, à fond perdu en haut et en bas sur 1 image sur 3, sans texte ajouté (3 images). Produit seul centré sur 60 à 86 % H, posé sur un fond clair plein, sans ombre visible (3 images).
- **Valeurs** :
  ```
  capture dans un appareil générique : hauteur 5.0 à 5.35 in, centrée · aucun texte
  capture nue (convention) : 82 à 88 % H, coins arrondis 0.12 in, aucun cadre
  produit seul : hauteur 3.4 à 4.8 in, centré · aucune ombre sur fond sombre ;
                 sur fond clair, une ombre de contact très douce au plus
  ```

### A3 Sommaire typographique

- **Mesuré (3 images)** : 5 ou 6 noms empilés, en cap de 7,0 à 13,2 % H selon le nombre de lignes ; interligne de 1,35 à 1,77 cap (médiane 1,41) ; centrés, ou alignés à droite à 70-78 % L ; chaque nom dans sa couleur.
- **Valeurs** :
  ```
  corps (convention dans la fourchette mesurée) : 6 lignes → 44 pt ; 5 → 56 pt ; 4 → 68 pt ; 3 → 80 pt
  interligne k = 1.4 · graisse 600 · align center (ou align right, bord droit à 7.6 in)
  couleur : le bloc en cours en accent, les autres en texte ; à la reprise, les autres en secondaire
  ```

### A14 Bento : la grille de récap

- **Mesuré (5 images)** :
  - gouttière de 5 à 6 px sur 640, soit 0,8 à 0,95 % L ; marge extérieure du même ordre (0,6 à 1,25 % L), ou tuiles coupées par le cadre ;
  - rayon d'angle de 1,2 à 2,3 % L (médiane 2 %), **le même pour toutes les tuiles**, petites ou grandes ;
  - tuile centrale de 32 à 49 % L × 31 à 48 % H, centrée sur (50 %, 50 %), deux à trois fois plus grande que les autres ; 8 à 19 tuiles en tout ;
  - tuiles **sans bordure ni ombre**, en aplat : blanches sur fond gris clair (3 images), gris clair sur fond blanc (1 image), gris très sombre sur noir (1 image, environ 12 % de blanc) ;
  - nom dans la tuile centrale : cap de 7,4 à 10,8 % H, en blanc sur un aplat ou un dégradé de couleur ; libellés des tuiles : cap de 1,4 à 1,9 % H ; chiffres des tuiles : cap de 9 % H environ, en accent.
- **Valeurs** :
  ```
  marge extérieure 0.09 in · gouttière 0.085 in · rayon 0.20 in (et au plus 25 % du petit côté)
  tuile centrale : 3.9 × 2.25 in environ, centrée · aplat accent · nom en blanc (ou fond_sombre
                   si le contraste l'exige), corps 48 à 60 pt, graisse 600
  autres tuiles : grille de 4 ou 5 colonnes × 3 ou 4 rangées, tailles inégales
                  aplat = fond_clair éclairci vers le blanc (sur clair) ; texte mélangé à 12 % (sur sombre)
  libellé de tuile : corps 11 à 12 pt, graisse 500, secondaire, en bas de tuile
  chiffre de tuile : corps 48 pt, graisse 600, accent uni
  ```
  Le bento est la seule slide où un texte descend sous 3 % H : il se regarde, il ne se lit pas.
- **Variante `fragments-logiciel`, mesuré (5 récaps de sessions pour développeurs, hors corpus, au pixel sur 1 920 × 1 080)** :
  - marge extérieure de 46 à 60 px, soit 2,4 à 3,1 % L, et 4,1 à 5,6 % H en haut et en bas ;
  - gouttière de 12 à 20 px, soit 0,6 à 1 % L ;
  - de 5 à 16 tuiles. Les tuiles des récaps de framework sont en aplat ; ceux de plateforme portent des dégradés, que la skill ne garde pas.
- **Valeurs `fragments-logiciel`** :
  ```
  marge 0.21 in · gouttière 0.094 in · grille de 12 colonnes · rangées 300 / 352 / 312 (sur 1080)
  tuile centrale : colonnes 5 à 8, rangée du milieu · fond_sombre sur deck clair, accent sur deck sombre
                   titre 30 pt (18 au moins), graisse 600, 3 lignes au plus · texte 9 pt regular
  tuile fragment : nom 16 pt (11 au moins), graisse 600, en haut à gauche · ligne 9 pt regular, secondaire
                   composant à la taille d'interface (1 px = 1/192 in) × echelle · filet 0,5 pt, sans ombre
  tuile chiffre : 96 pt (48 au moins), graisse 600, couleur du texte (l'accent reste à la liste)
  tuile liste : surtitre 8 pt en capitales · lignes 13 pt (8 au moins), graisse 600, calées en bas · aplat accent
  ```

### A17 Citation ou témoignage

- **Mesuré (1 image plein cadre, 2 sur scène)** : 2 à 4 lignes en demi-gras, **alignées à gauche** à 9,2 % L, sur 76 % L au plus ; cap de 6,35 % H ; interligne de 1,48 cap ; source en regular secondaire, en cap de 4,7 % H (0,75 fois la citation), 9,5 % H sous la dernière ligne de base ; bloc centré à 50 % H. Sur scène, la source passe parfois en accent.
- **Valeurs** :
  ```
  citation : corps 36 pt · graisse 600 · align left · interligne k = 1.5
             boîte x 0.92  w 7.6 · bloc centré à 2.81 in
  source : corps 26 pt · regular · secondaire (ou accent, alors seul accent de la slide)
           haut des capitales à 0.53 in sous la dernière ligne de base
  ```

### A19 Prix

- **Mesuré (3 images)** : le nom et le prix ont presque le même corps (prix à 0,82-1,0 fois le nom) ; le petit « à partir de » est à 0,36-0,42 fois le nom, en regular secondaire, collé au-dessus du prix.
  - Mise en page « haut » (1 image) : nom en cap de 7,4 % H, haut des capitales à 12,8 % H ; prix en cap de 6,1 % H ; objet dessous, de 50 à 87 % H, sur 56 % L.
  - Mise en page « colonne droite » (1 image) : texte centré à 70 % L ; objet à gauche, de 12 à 39 % L, sur 91 % H ; 14 % H d'écart entre deux offres.
  - Prix héros (1 image, offre de service) : le prix est traité comme un chiffre A5 (cap de 27 % H), avec la période dessous en cap de 3,3 % H.
- **Valeurs** :
  ```
  nom : corps 40 pt, graisse 600 · petit « À partir de » : corps 16 pt, regular, secondaire
  prix : corps 36 pt, graisse 600 · précision (HT, période, capacité) : corps 16 pt, regular, secondaire
  écarts : base du nom → haut du petit : 0.48 in (« haut ») ou 0.25 in (« colonne ») ;
           base du petit → haut du prix : 0.16 in ;
           base du prix → haut de la précision : 0.16 in ; entre deux offres : 0.79 in
  « haut » : haut des capitales du nom à 0.72 in · objet de 2.7 à 4.9 in en hauteur, ≤ 6.0 in de large, centré
  « colonne droite » : texte centré à x 7.0 in · objet x 1.1 → 3.9 in, h ≤ 5.1 in
  prix seul d'un service : appliquer A5 (144 pt), période en corps 18 pt, regular
  ```

### A20 Disponibilité

- **Mesuré (4 images)** : petit libellé gris, en regular, en cap de 2,7 à 3,1 % H, au-dessus d'un mot en demi-gras en cap de 5,8 à 7,9 % H (rapport 0,38-0,46) ; 2,7 à 3,7 % H entre la base du libellé et le haut du mot ; bloc en haut (haut du libellé à 6-12 % H) ; gamme d'objets dessous, de 27-38 % à 82-90 % H, sur 61 à 92 % L, centrée.
- **Valeurs** :
  ```
  libellé : corps 16 pt · regular · secondaire · haut des capitales à 0.45 in
  mot ou date : corps 40 pt · graisse 600 · haut des capitales à 0.19 in sous la base du libellé
  visuel : de 1.6 à 5.0 in en hauteur, ≤ 9.2 in de large, centré, calé en bas à 5.0 in
  sans visuel (convention) : libellé en 24 pt et mot au corps A1 (100 pt), bloc centré à 2.81 in
  ```

### A21 Synthé nom et fonction (vidéo et plans de scène)

- **Mesuré (3 images)** : nom en gras et fonction en regular, **au même corps** (cap de 2,8 à 3 % H) ; bord gauche à 5,2-5,6 % L (bord droit à 94,7 % L dans la variante de droite) ; lignes de base à 84,4 et 90,3 % H ; en blanc sur l'image, sans fond ni ombre.
- **Valeurs** :
  ```
  nom : corps 16 pt, gras · fonction : corps 16 pt, regular · blanc · aucun fond
  x 0.54 in (variante droite : bord droit à 9.47 in, align right)
  lignes de base à 4.75 in et 5.08 in
  ```

### A6 Graphique comparatif

- **Mesuré (2 images)** : titre en cap de 4,5 à 5,5 % H, en demi-gras, centré en haut (haut des capitales à 7,5-12 % H) ; courbes et barres fines, de 1,1 % H d'épaisseur ; étiquettes en cap de 4,0 à 4,2 % H, au bout des barres ; soi en couleur, l'autre en gris à 45 % ; barres de 15 à 85 % L.
- **Valeurs** :
  ```
  titre : corps 28 pt · graisse 600 · haut des capitales à 0.5 in · centré
  zone du graphique : x 1.5 → 8.5 in, y 1.9 → 4.3 in
  barres et courbes : épaisseur 0.06 in (4,5 pt), bouts arrondis
  étiquettes : corps 23 pt, graisse 600, au départ et au bout des barres ; axes : 16 pt, regular, secondaire
  soi : accent uni (le dégradé reste au chiffre héros) · l'autre : gris à 45 %
  ```

### A16 Logos partenaires

- **Mesuré (2 images)** : logos monochromes hauts de 5 à 10 % H ; rangées tous les 17 à 22 % H ; grille sur 78 à 83 % L, centrée ; 3 à 5 logos par rangée, 4 ou 5 rangées.
- **Valeurs** :
  ```
  hauteur d'un logo 0.28 à 0.56 in · rangées tous les 1.0 à 1.2 in · grille de 8.0 in, centrée
  couleur : texte (logos monochromes) · aucun texte ajouté
  ```

### Slide finale

- **Mesuré (2 images)** : un seul signe centré, haut de 27-28 % H, centré à 47,5 % H ; dessous, au plus une ligne en cap de 4 % H, ligne de base à 89 % H ; mentions minuscules en gris en bas ; fond plein sombre, ou photo de ciel (1 image).
- **Valeurs** :
  ```
  le logo de l'utilisateur (hauteur 1.55 in) ou un mot au corps A1 (100 à 120 pt, graisse 600)
  centre y 2.67 in (47,5 % H) · point final en accent pour un mot
  une ligne dessous (facultative) : corps 22 pt, regular, ligne de base à 5.0 in
  sources et mentions : corps 9 pt, secondaire, ligne de base à 5.29 in
  fond : fond_sombre plein ; ou accent en pleine page, le seul de tout le deck, avec un texte
         en fond_sombre si le contraste atteint 4,5:1 (convention, retenue d'après le témoin)
         et si theme.finale_accent n'est pas false (charte qui plafonne la surface d'accent)
  ```

### Surtitre, dans tous les archétypes à texte

- **Mesuré (6 images)** : 0,36 à 0,46 fois la cap du titre (médiane 0,41) ; posé à 0,44-0,48 cap au-dessus du titre ; en regular, gris secondaire ; même alignement que le titre. Une seule fois en accent et en capitales grasses (une définition).
- **Valeurs** :
  ```
  corps = 0.42 × corps du titre, borné entre 16 et 28 pt
  ligne de base à 0.45 × cap du titre au-dessus du haut des capitales du titre
  graisse : regular s'il est gris ; demi-gras s'il est en accent (choix de deck-spec)
  en accent, il est l'accent de la slide avec le point final, rien d'autre
  ```

### Marqueurs à l'écran (§3.15)

| Marqueur | À l'écran |
|---|---|
| `[À VALIDER : texte proposé]` | Le texte proposé, sans crochets, dans le style normal de son champ : rien ne le distingue. |
| `[À FOURNIR : libellé]` | Le libellé seul, 3 mots au plus, **dans le style et au corps du champ** (titre, chiffre, prix, date), **estompé** à toutes les tailles (couleur du texte qu'il remplace, 40 % d'opacité, jamais de dégradé ; un chiffre ou un mot d'accent manquant passe dans la couleur du texte, car l'accent à 40 % vire au brun sur fond sombre) et souligné en pointillé d'accent : il se lit comme un emplacement, pas comme du contenu. Jamais d'encadré, de fond rose ou de cadre gris. |

- Jusqu'à 26 pt : pptx `underline: { style: 'dotted', color: ACCENT }` sur la portion du marqueur (pptxgenjs 4 écrit `u="dotted"` et `a:uFill`) ; aperçu HTML `text-decoration: underline dotted #ACCENT; text-decoration-thickness: max(2px, .05em); text-underline-offset: .12em`.
- Au-dessus de 26 pt (titre, chiffre, prix, date) : le soulignement d'une police grossit avec le corps (Arial : 0,07 em, soit une rangée de points de 10 pt sous un chiffre de 144 pt, constaté à l'itération 2). Le moteur le retire du texte et pose dessous un **filet pointillé d'épaisseur fixe** : 1,5 pt, `sysDot`, accent à 70 %, à 0,085 em sous la ligne de base (entre 3 et 12 pt), sur la largeur estimée du marqueur. Le même filet dans le .pptx (forme « Soulignement », animée avec son texte) et dans l'aperçu, chacun placé pour la police qu'il affiche : la police écrite pour le .pptx, le repli quand l'aperçu ne l'a pas (`STYLE.marqueur.chasse`, écart mesuré : 0,1 in au plus).
- Canva perd l'opacité à l'import : avec `meta.format` à `canva`, le libellé garde ses crochets (`[date]`), seul signe d'emplacement qui survit. Le filet pointillé les couvre.
- Un `[À FOURNIR]` écrit dans un `*accent*` reste un marqueur : couleur du texte à 40 %, jamais le texte en clair ni l'accent. Une ligne d'A8 qui n'est qu'un marqueur garde sa case vide, sans coche.
- Un champ principal qui manque (titre, lignes, chiffre, citation) prend un libellé tiré de la slide : le début de `textes.attendu` (sans article ni « slide de »), sinon, pour une slide AF, son identifiant (`s13-garanties` → « Garanties »). Jamais le nom du champ (« titre », « lignes », « contenu ») : ce sont des mots de l'atelier.
- Le marqueur suit l'ajustement de son champ (planchers compris). Une image qui manque est remplacée par une interface schématique (§5.2), jamais par un cadre gris.

---

## 4. Couleur

### 4.1 Une seule couleur d'accent par slide

- **Mesuré** : aucune des 67 images ne porte deux couleurs d'accent, hors sommaire, bento, murs de logos, captures et photos.
- L'accent se pose sur **un élément, deux au plus** : le nom (A1), le chiffre (A5), la barre ou la courbe de soi (A6), les pictogrammes (A8), la ligne en cours (A3), un mot de la phrase, le surtitre et le point final, la source d'une citation.
- Jamais sur le texte courant, les libellés, les lignes de liste ni les mentions.
- `accent2` ne sert qu'au dégradé du chiffre héros : ce n'est pas une seconde couleur d'accent.

### 4.2 Le dégradé, réservé au chiffre héros

- **Mesuré (4 slides-chiffre sur 6)** : le dégradé est **horizontal, de gauche à droite**, à deux arrêts. Il va d'une teinte plus profonde à gauche vers une teinte plus claire ou voisine à droite : violet vers magenta, marine vers bleu, rose vers orange, graphite vers gris. Les deux arrêts sont à moins de 65° de teinte l'un de l'autre, ou de même teinte avec 15 à 22 points de luminance d'écart.
- Le corpus l'emploie aussi sur certains noms, sur le sommaire, sur la courbe de soi et sur la tuile centrale du bento. La skill le garde **pour le chiffre A5 seul** : il reste rare, donc fort.
- Il va de `accent` à `accent2` ; sans `accent2`, le chiffre est en accent uni. Chaque arrêt doit garder un contraste d'au moins 3:1 avec le fond (texte de plus de 24 pt).
- pptx (pptxgenjs ne sait pas faire de dégradé de texte) : en post-traitement, le moteur remplace le `a:solidFill` du `a:rPr` du chiffre par
  ```xml
  <a:gradFill rotWithShape="1"><a:gsLst>
    <a:gs pos="0"><a:srgbClr val="ACCENT"/></a:gs>
    <a:gs pos="100000"><a:srgbClr val="ACCENT2"/></a:gs>
  </a:gsLst><a:lin ang="0" scaled="0"/></a:gradFill>
  ```
  Aperçu HTML : `background: linear-gradient(90deg, #ACCENT, #ACCENT2); -webkit-background-clip: text; background-clip: text; color: transparent`.
- Keynote et Canva relisent mal un dégradé de texte venu d'un .pptx. Le format `keynote` ou `canva` prend donc l'accent uni.

### 4.3 Fonds

- **Fond plein, jamais de motif, de texture ni de dégradé.** Les fonds flous et colorés du corpus (1 keynote sur 8) ne se reprennent pas : on garde l'aplat.
- Un fond par bloc. On n'en change qu'entre deux blocs, et jamais pour une seule slide au milieu d'un bloc (l'itération 1 passait au blanc pour 6 slides).
- Photo en plein cadre (A18) : à fond perdu, sans cadre ni coins arrondis.

---

## 5. Images, formes et interfaces

### 5.1 Règles

- **Jamais de cadre ni de bordure autour d'un texte** (0 cas sur 67). Les tuiles se détachent par leur aplat, sans trait.
- **Aucune ombre sur un texte.** Aucune ombre portée sur fond sombre. Sur fond clair, une ombre de contact très douce au plus, sous un objet.
- Les objets peuvent sortir du cadre (A9, A10 : 2 cas sur 6). Un objet entier, centré, flottant au milieu d'une zone vide, fait moins keynote qu'un objet coupé par le bord.
- Coins arrondis : 0,20 in pour les tuiles, 0,12 in pour une capture nue (convention), 0 pour une photo plein cadre.

### 5.2 Interface schématique, quand une capture manque (convention)

Le moteur la dessine d'après `image.attendu`. Elle dit « un écran est là », sans rien inventer.

```
carte : un écran en mode clair, quel que soit le fond de la slide
        sur fond sombre : fond_clair (blanc s'il ne contraste pas à 7:1) ; aplats intérieurs gris à 4,5 %
        sur fond clair : blanche ; sur fond blanc pur : grise à 5 %, aplats intérieurs blancs
        rayon 0.12 in · aucun trait
contenu : barres grises (texte mélangé à 22-38 %), hauteur 0.08 in, bouts ronds,
          longueurs 100 / 72 / 48 % de la largeur utile, une tous les 0.16 in
une seule chose en accent (la chose dont on parle) : la ligne mise en avant, teintée d'accent à 22 %,
          avec sa pastille d'état en accent ; une barre d'accent, ou une pastille pleine avec un trait
          sombre si l'accent est trop clair sur la carte (sous 1,8:1 : jaune sur blanc)
aucun texte, aucun chiffre, aucun montant, aucune date, aucun nom de client, aucun logo
ombre : aucune sur sombre ; sur clair : flou 0.3 in, décalage 0.08 in, 12 % de noir
appareil générique (si besoin) : rectangle à coins de 13 % de la largeur, bord de 3 %, verre noir
          et liseré clair de 0,75 à 1,75 pt, ni encoche ni boutons : rien qui évoque un appareil réel
photo : aplat un peu plus clair que le fond, deux halos neutres ; aucun reflet d'accent (il virait au kaki)
tuile d'image (mur, bento) : aplat voisin des tuiles, jamais un écran clair au milieu du mur
```

Itération 2, première version : une carte sombre à 8 % et des barres à 25-35 % se lisaient comme un écran de chargement, et la barre d'accent jaune disparaissait sur fond blanc. Le témoin sans skill, jugé plus « keynote », posait des écrans clairs sur fond sombre.

Place et taille : celles de l'image qu'elle remplace (A9 : la zone de l'objet, mais l'écran reste entier, à 0,5 in du bord, alors qu'un objet peut sortir du cadre ; A10 : 82 à 88 % H, centrée).

---

## 6. Mouvement

Les durées ne se mesurent pas sur des images fixes : elles sont de convention. Les manières, elles, sont observées (l'analyse du corpus).

| Moment | Observé | Valeur moteur |
|---|---|---|
| Entre deux slides | fondu (cartes-titres, phrases) | transition fondu, 0,5 s (convention) |
| Le même écran qui change (mot de disponibilité, ligne suivante, chiffre qui se transforme) | changement sur la même image | Morphose (PowerPoint) entre deux slides aux objets de même nom ; repli en fondu |
| Chiffre héros | il arrive flou et zoomé, puis se pose ; ou le libellé d'abord | entrée Zoom ou Fondu, 0,4 s, au clic |
| Liste | ligne par ligne | une entrée Fondu par paragraphe |
| Bento | la tuile centrale d'abord, puis les autres | centrale au clic, les autres après elle |
| Prix | le nom, puis le prix | deux temps |

pptx : pptxgenjs ne pose ni transition ni animation. En post-traitement, le moteur insère `<p:transition spd="med"><p:fade/></p:transition>` après `</p:clrMapOvr>` de chaque slide. La Morphose passe par un `mc:AlternateContent` qui contient `p159:morph` et un repli `p:fade`. Valide le fichier avec `validate.py` après ce post-traitement.

---

## 7. Contrôle visuel : à vérifier sur les captures

1. Le texte principal atteint sa taille : cap ≥ 14 % H en A1, ≥ 8 % en A4, ≥ 20 % pour le chiffre A5.
2. Le centre du bloc tombe entre 44 et 56 % H, sauf pour A6, A19, A20 et A21.
3. Deux niveaux de texte au plus. Rien sous 3 % H de cap, hors bento et mentions.
4. Une seule couleur d'accent ; un dégradé seulement sur un chiffre A5.
5. Aucun cadre, aucune bordure, aucun encadré pointillé, aucun fond rose, aucun cadre gris.
6. Les titres ne sont pas plus gras que du demi-gras (sauf Arial Bold, faute de mieux).
7. Le même fond d'un bout à l'autre du bloc.
8. Rien de l'atelier à l'écran : ni archétype, ni étape, ni consigne.

---

## Annexe A. Méthode de mesure (pour la refaire)

1. Chaque image (640 × 360, ou 960 × 540 ramenée à 640) est convertie en luminance avec ffmpeg. Le fond est la médiane du pourtour. Un pixel est de l'« encre » s'il s'écarte du fond de plus de 30 à 60 niveaux (ou par seuil absolu, pour un texte blanc sur photo).
2. Les lignes de texte sont les bandes de rangées qui contiennent de l'encre. Pour chaque bande : le haut (première rangée encrée), la ligne de base (dernière rangée encrée à au moins 25 % du maximum, ce qui écarte les jambages), la largeur et le centre.
3. La hauteur ainsi mesurée dépasse la vraie cap de 5,5 % (anticrénelage et hampes). Le facteur a été étalonné sur 19 rendus de cap connue ; toutes les caps de ce fichier sont corrigées.
4. Fût : la médiane des plages d'encre horizontales dans la zone médiane des lettres, divisée par la cap.
5. Graisse et suivi : le même texte est rendu dans chaque police candidate, au même cap et à la même échelle, avec Playwright, puis mesuré par le même script. Le rapport des fûts donne la graisse. L'écart de largeur, divisé par le nombre d'intervalles entre lettres, donne le suivi en em. Un second rendu, à 1,5 fois puis réduit comme les images du corpus, redonne les mêmes valeurs à ±0,005 em au-dessus de 28 pt. Sous 28 pt, l'écart atteint 0,025 em (deux chaînes seulement) : c'est la colonne la moins sûre du §2.2.
6. Bento : les gouttières sont les plages de fond entre deux aplats de tuile (classées au seuil médian entre fond et tuile) ; le rayon se déduit du nombre de rangées où le bord de la tuile rentre dans l'angle (r − √r = n).
7. Limites : 1 px vaut 0,28 % H ; les images sur scène ne servent qu'aux rapports (graisse, couleur, alignement), pas aux tailles.

## Annexe B. Images mesurées, par archétype

Chemins relatifs au dossier des images de l'analyse (`fr/vN/…`, comme dans `data/archetypes.json`). On ne les recopie pas dans la skill.

| Archétype | Images |
|---|---|
| A1 | v1 frame_0321 · v3 frame_0075 · v7 frame_0162 · v8 frame_0339 |
| A4 | v3 frame_0543 · v2 t1641 · v2 t1562 (scène) · v4 t3120 |
| A5 | v1 t3420 · v3 t355 · v2 t1940 · v2 t738 · v7 t420 · v4 t556 · v6 t1751 (scène) · v2 t2310 (scène) |
| A7, A8 | v2 t995 · v4 t472 · v7 t4420 (scène) · v5 t1605 (scène) |
| A9 | v3 t1325 · v8 t262 · v8 frame_0132 · v5 t2270 (scène) |
| A10, A13 | v1 frame_0054 · v2 frame_0328 · v3 frame_0282 · v3 frame_0134 · v4 frame_0354 · v2 t1420 |
| A3 | v7 t320 · v8 t785 · v1 t338 |
| A14 | v1 t1900 · v2 t1735 · v3 t1372 · v7 t2550 · v8 t2924 |
| A17 | v1 t1505 · v6 t6960 (scène) · v5 t435 (scène) |
| A19 | v2 t1721 · v4 t1753 · v5 t1296 (scène) · v6 t6080 (scène) |
| A20 | v2 t2493 · v3 t1750 · v7 t3852 · v8 t5344 · v6 t8105 (scène) |
| A21 | v2 t330 · v3 t304 · v7 frame_0232 |
| A6 | v2 t606 · v1 t4795 · v2 t683 |
| A16 | v1 t3660 · v8 t1990 · v5 t3255 (scène) |
| Finale | v7 t6200 · v8 t5539 |
| A2 (vu, non chiffré) | v7 frame_0791 · v8 t1097 · v6 t2450 |
