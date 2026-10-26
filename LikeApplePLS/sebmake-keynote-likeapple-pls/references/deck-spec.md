# Le fichier deck.json

La skill écrit d'abord un fichier `deck.json`. Tout le reste en sort : le .pptx, l'aperçu HTML et le contrôle. On ne retouche jamais le .pptx à la main pour corriger le contenu. On corrige `deck.json`, puis on relance le rendu.

- Un seul fichier JSON, en UTF-8, rangé dans le dossier de travail de la présentation.
- Les chemins d'images sont relatifs à ce fichier (`images/ecran.png`).
- La sortie est toujours en 16:9 (10 × 5,625 pouces, `LAYOUT_16x9`).

**Sommaire.** Commandes · Structure générale · meta · theme · intervenants · slides (champs de `textes` par archétype, variantes, texte enrichi, tailles) · Marqueurs : ce que la skill propose, ce qu'elle demande · notes : le script à dire · Apparitions et transitions · Public, sources et procédés · Images · Visuels à préparer : `slide.visuel` · Ce que vérifie check_deck.py · Exemple complet.

L'allure des slides (tailles, graisses, surtitre, chiffre héros, placeholders) est décrite dans `style-visuel.md`, et le design de chaque archétype (variantes, contenu visuel, profondeur, brief) dans `designs.md`. Ce fichier-ci ne dit que les champs qui les pilotent.

## Commandes

```bash
# depuis le dossier de travail ; $SKILL = dossier de la skill
[ -d "$SKILL/scripts/node_modules/pptxgenjs" ] || (cd "$SKILL/scripts" && npm install)   # pptxgenjs 4.0.1, une fois
python3 "$SKILL/scripts/check_deck.py" deck.json                 # contrôle (code 1 = erreur bloquante)
python3 "$SKILL/scripts/check_deck.py" deck.json --brouillon     # pendant la rédaction : [À FOURNIR] toléré
node "$SKILL/scripts/build_deck.js" deck.json sortie.pptx --preview apercu.html
node "$SKILL/scripts/export_script.js" deck.json --md script.md  # script ; --visuels v.md : visuels à préparer ;
                                                                 # --etapes : apparitions ; --srt f.srt : sous-titres
```

`build_deck.js` accepte aussi `--polices auto|repli`. Avec `auto` (par défaut), le .pptx écrit toujours la police du thème (son nom exact), installée ou non sur la machine qui construit le deck : il sera présenté sur celle de l'utilisateur. Si elle manque ici, l'aperçu s'affiche dans la police de repli, la mesure anti-débordement prend la plus large des deux, et la console le dit en une ligne. `repli` écrit la police de repli dans le .pptx.

Ouvrir `apercu.html#qa` dans un navigateur entoure en rouge les textes qui débordent de leur boîte. Le même contrôle est disponible en JavaScript avec `window.__deckQA()`.

Ce que l'utilisateur reçoit selon `meta.format` : voir `SKILL.md` (étape 6) et `formats/<format>.md`.

## Structure générale

```json
{
  "meta": { },
  "theme": { },
  "intervenants": [ ],
  "slides": [ ]
}
```

## meta

| Champ | Obligatoire | Valeurs | Rôle |
|---|---|---|---|
| `titre` | conseillé | texte | Titre du fichier et de l'aperçu. |
| `langue` | oui | `fr` ou `en` | Langue des slides et du script. Elle choisit les gabarits FR ou EN, la typographie et les libellés des notes. |
| `registre` | oui en français | `tu` ou `vous` | Registre envers le public. Toujours demandé à l'utilisateur. |
| `registre_intervenants` | conseillé en français (plusieurs intervenants) | `tu` ou `vous` | Registre entre intervenants, demandé en même temps. Le contrôle le vérifie sur les segments `relais`. |
| `public` | oui | texte, ou `{ "type": "...", "description": "..." }` | Typologie du public, demandée à l'utilisateur (question de `references/publics.md`). `type` est une clé de `references/data/publics-exigences.json` ou l'un de ses synonymes. Pour un public mixte, `type` est une liste (`["b2b-decideurs", "investisseurs"]`). Elle décide des procédés gardés (voir plus bas). |
| `duree_min` | oui | nombre | Durée cible en minutes. La somme des `duree_s` doit rester à ±15 % de cette cible. |
| `format` | oui | `keynote`, `powerpoint`, `canva`, `figma-slides`, `video` | Format demandé à l'utilisateur. |
| `ratio` | non | `16:9` | Toujours 16:9. Toute autre valeur est une erreur. |
| `contexte` | non | `direct` ou `preenregistre` | Pour le choix du déroulé. Le rendu ne s'en sert pas. |
| `variante` | non | `produit`, `fonctionnalite`, `service`, `technologie` | Variante de séquence d'annonce (`grammaire.md` §4.3). Le rendu ne s'en sert pas. |
| `affichage_source` | non | `sous_le_chiffre`, `renvoi`, `carton_final`, `aucun` | Remplace le choix fait par le public. |
| `carton_sources` | non | `true` (défaut) ou `false` | En mode `renvoi` ou `carton_final`, ajoute à la fin une slide « Sources et mentions ». |

## theme

La skill ne connaît pas l'habillage de l'utilisateur. Elle demande un lien vers son design system, ou ses couleurs en HEX et ses polices. Elle reporte ensuite les valeurs ici.

```json
"theme": {
  "nom": "Clairval",
  "design_system": "https://… (facultatif : d'où viennent les valeurs)",
  "couleurs": {
    "fond_sombre": "#0F1B2A",
    "fond_clair": "#F5F7F9",
    "texte": "#14202E",
    "texte_secondaire": "#5B6776",
    "accent": "#1C9461",
    "accent2": "#E8A33D"
  },
  "polices": {
    "titre": { "nom": "Inter", "repli": "Arial" },
    "texte": { "nom": "Inter", "repli": "Arial" }
  },
  "point_accent": true,
  "finale_accent": true,
  "logo": "images/logo.png"
}
```

| Rôle | Obligatoire | Usage |
|---|---|---|
| `fond_sombre` | oui | Fond des slides `"fond": "sombre"` et `"image"`. |
| `fond_clair` | oui | Fond des slides `"fond": "clair"`. Sert aussi de texte sur fond sombre s'il contraste assez (7:1), sinon c'est du blanc. |
| `texte` | oui | Texte sur fond clair. |
| `texte_secondaire` | conseillé | Libellés gris sur fond clair. Sans valeur, il est calculé. |
| `accent` | oui | Surtitres, chiffres géants, barre mise en avant, coches, tuile centrale du bento, mots `*en accent*`, point final des titres, soulignement des `[À FOURNIR]`. |
| `accent2` | non | Fin du dégradé du chiffre héros : le chiffre géant (A5) passe de `accent` à `accent2`. Sans `accent2`, le chiffre est uni, en `accent`. C'est aussi la seconde couleur du thème PowerPoint. Prends une nuance voisine de l'accent dans la palette de l'utilisateur, jamais une couleur qu'il n'a pas vue. |
| `texte_sur_sombre` | non | Remplace la couleur calculée du texte sur fond sombre. |
| `texte_secondaire_sur_sombre` | non | Remplace le gris calculé sur fond sombre. |

- Les HEX s'écrivent avec ou sans `#`, en 3 ou 6 chiffres. Le moteur retire le `#`, que le .pptx refuse.
- Les couleurs sont aussi écrites dans le thème du fichier (palette de PowerPoint et de Keynote). Les polices titre et texte deviennent les polices du thème.
- Une police peut s'écrire en texte simple (`"texte": "Arial"`), et Arial sert alors de repli.
- `point_accent` (`true` par défaut) : le point final d'un titre (et le `!` ou le `?`) prend la couleur d'accent, comme une signature discrète. `false` le laisse dans la couleur du texte. Un titre sans ponctuation finale n'en reçoit pas.
- `finale_accent` (`true` par défaut) : une slide finale A1 (un mot, en dernière position) passe en pleine page d'accent, si son texte s'y lit à 4,5:1. Mets `false` quand la charte plafonne la surface d'accent (par exemple un jaune limité à 10 % de la surface) : la finale garde alors son `fond` (`sombre` ou `clair`), avec le point final en accent. Un `"fond": "accent"` écrit sur la slide reste possible.
- Le logo est facultatif. Il apparaît en bas à droite des slides qui portent `"logo": true`, et au centre de l'archétype A2 quand la slide n'a pas d'image.
- Interdit : toute police, tout logo ou toute image de la marque Apple. « À la Apple » désigne la grammaire, pas l'identité.

## intervenants

```json
"intervenants": [
  { "id": "claire", "nom": "Claire Duval", "role": "Directrice générale" },
  { "id": "hugo", "nom": "Hugo Bernard", "role": "Responsable produit" }
]
```

Il en faut au moins un. Le premier est l'intervenant par défaut. Celui qui ouvre la présentation la clôt.

`role` est facultatif. S'il est inconnu, laisse-le vide : le moteur écrit le nom seul en tête de chaque prise de parole. N'y mets jamais un marqueur, qui serait répété à chaque passage de parole ; la fonction se demande une fois, dans la liste de la livraison.

## slides

| Champ | Obligatoire | Rôle |
|---|---|---|
| `id` | oui | Identifiant unique (`s05-nom`). |
| `bloc` | conseillé | Nom du bloc du déroulé (`Ouverture`, `Clairval Direct`, `Clôture`). Il devient une section dans PowerPoint. |
| `etape` | non | Numéro de l'étape dans la séquence d'annonce (1 à 16, voir `data/annonce.json`), ou `null` hors séquence. Repère de travail : il n'est affiché ni à l'écran ni dans les notes. |
| `archetype` | oui | `A1` à `A25` (voir `data/archetypes.json`), `FIN`, `COLORIS`, `FRISE` (designs hors catalogue, voir « Variantes »), ou `AF` (à éviter, voir le tableau). Repère de travail, lui non plus jamais affiché. |
| `variante` | conseillé | La composition de l'archétype, parmi celles que le moteur dessine (« Variantes » ci-dessous ; le design de chacune est dans `designs.md`). Absente : le rendu d'origine de l'archétype, plus simple (voir « Variantes »). Repère de travail, jamais affiché. |
| `fond` | oui | `sombre`, `clair`, `image` ou `accent` (page pleine couleur d'accent, réservée à la slide finale ou à un moment fort unique). Garde le même fond d'un bout à l'autre (celui de l'ouverture, souvent `sombre`) ; un changement `sombre` ↔ `clair` ne se fait qu'entre deux blocs. |
| `intervenant` | conseillé | `id` de l'intervenant qui parle par défaut sur cette slide. |
| `textes` | selon l'archétype | Textes affichés (tableau ci-dessous). |
| `image` | selon l'archétype | `"chemin.png"` ou `{ "chemin": "...", "attendu": "ce que l'image doit montrer", "ajustement": "contenir" \| "couvrir" }`. Tant que le fichier manque, le moteur dessine un placeholder (voir Images). |
| `images` | selon la variante | Une liste d'images (chaînes ou objets comme `image`), pour les variantes à plusieurs visuels : A2 et A10 `rangee`, A13 `coloris`, A18 `diptyque`, A8 `picto-par-ligne`. |
| `image_fond` | non | Image de fond d'une slide `"fond": "image"` dont l'`image` est déjà le contenu. Avec une variante, c'est la seule source de l'image de fond. |
| `appareil` | non | `telephone`, `tablette`, `portable` ou `boitier` : l'appareil générique qui porte une capture. Absent : déduit de `image.attendu`. |
| `logo_invite`, `logo_systeme`, `logo_final` | non | Le logo de l'organisation invitée (A21 cartes), du système (A11), de la slide finale (FIN ; sinon `image`, puis `theme.logo`). |
| `profondeur` | non | `false` retire l'ombre de contact (fond clair) et le halo (fond sombre) que le moteur pose sous un produit ou un appareil. |
| `visuel` | conseillé dès que la slide attend une image | Le brief du visuel à préparer : `{ "type", "brief", "fond_transparent", "angle", "resolution_min" }`, ou une liste de ces objets. Jamais affiché ; `export_script.js --visuels` en fait la liste à livrer (voir Visuels à préparer). |
| `voile` | non | Opacité du voile noir sur une image de fond, de 0 à 100 (45 par défaut). |
| `source` | si chiffre | Source ou conditions d'un chiffre. Affichée selon le public. |
| `a_fournir` | non | Texte ou liste : la consigne complète de ce qui manque sur la slide (quoi, sous quelle forme, qui peut le donner). Jamais à l'écran ; écrite dans les notes et dans `script.md`, et listée par le contrôle. Voir Marqueurs. |
| `notes` | oui | Le script à dire (voir plus bas). |
| `duree_s` | oui | Durée de la slide en secondes. |
| `build` | conseillé | Les apparitions, une phrase par clic. Le moteur en tire les animations d'entrée du .pptx, et la liste reste dans les notes pour l'orateur (voir Apparitions et transitions). |
| `logo` | non | `true` pour afficher le logo du thème. |

### Champs de `textes` par archétype

Les archétypes viennent de `references/data/archetypes.json`. Le moteur les rend avec les couleurs et les polices du thème.

**`surtitre`, dans tous les archétypes à texte.** Un à trois mots posés au-dessus du titre ou du chiffre, en petit : « Nouveau », « Pilote », « Notre engagement ». Il prend la couleur d'accent, en demi-gras, quand l'accent de la slide est libre ; si la slide porte déjà son accent (un `*mot*`, le chiffre héros, la barre de soi, les coches, la ligne active), il passe en gris, en regular : une seule couleur d'accent par slide. Il nomme le moment sans le répéter. Il compte dans les 10 mots de l'écran. Pas plus d'un surtitre par slide, et pas sur toutes : il perd sa force s'il revient partout.

| Archétype | Champs | Rendu |
|---|---|---|
| A1 Carte-titre | `titre` (1 à 3 mots) | Mot seul, très gros, centré. |
| A2 Icône ou logo + nom | `titre` + `image` (ou logo du thème) | Icône centrée, nom dessous. |
| A3 Sommaire typographique | `lignes[]`, `actif` (n° de 1 à n, facultatif) | Lignes centrées, la ligne active en accent, les autres en gris. |
| A4 Phrase-thèse | `titre` (3 à 8 mots ; `\n` pour couper) | Une ou deux lignes centrées. |
| A5 Gros chiffre + libellé | `chiffre` (un seul), `libelle` (9 mots au plus), `surtitre` facultatif | Chiffre héros géant, en dégradé de `accent` à `accent2` (uni sans `accent2`), libellé dessous, source en petit sous le libellé. |
| A6 Graphique comparatif | `titre`, `barres[]` : `{ "libelle", "valeur", "etiquette", "mise_en_avant" }`, `unite`, `axe`, `afficher_valeurs` | Barres horizontales sans axe chiffré : la barre mise en avant en accent, les autres en gris, l'étiquette au bout. `valeur` ne sert qu'à la longueur. |
| A7 Liste sans puces | `titre` facultatif (au-dessus des lignes), `lignes[]` (2 à 6), `actif` | Lignes centrées, sans puces. Avec `actif`, la ligne active est en blanc et les autres en gris. |
| A8 Liste à coches | `titre` facultatif, `lignes[]` (3 à 6), `coche` (`false` = cercles vides) | Coches en couleur d'accent, ou cercles vides pour poser une tension. |
| A9 Objet + texte | `titre`, `lignes[]` (3 au plus), `cote` (`droite` pour mettre l'image à droite) + `image` | Visuel sur une moitié, texte sur l'autre. |
| A10 Capture plein cadre | `image` | Capture centrée sur presque tout le cadre, sans texte ajouté. |
| A11 Schéma à bloc surligné | `titre` (nom du système), `blocs[]` avec une variante (voir « Variantes ») | Sans variante : rendu comme A9 (avertissement). Avec une variante : schéma au trait, un bloc allumé, sa légende au bout d'un filet. |
| A12 Vue intérieure | `image`, `note` facultative | Image plein cadre. |
| A13 Produit seul | `image` | Produit centré, sans texte. |
| A14 Bento | `titre` (tuile centrale), `tuiles[]` (4 à 8 ; 10 avec une grille « produit », 12 en `grille-icones`, 6 à 11 en `fragments-logiciel`) : `{ "type", "chiffre", "titre", "texte", "image" }` | Tuile centrale en accent ; autour, des tuiles inégales de 1 à 4 mots. |
| A15 Mur d'abondance | `elements[]` : textes ou `{ "titre", "image" }` | Grille dense qui déborde du cadre. |
| A16 Logos partenaires | `titre` facultatif, `logos[]` : `{ "nom", "image" }` (15 au plus en grille ; 30 à 80 en `mur-dense`) | Grille régulière ; logos monochromes à fournir. |
| A17 Citation ou témoignage | `citation`, `auteur` | Deux à quatre lignes en gras, alignées à gauche ; guillemets ajoutés selon la langue. |
| A18 Photo plein cadre | `image`, `titre` et `note` facultatifs | Photo bord à bord ; cartouche en bas à droite pour la note. |
| A19 Prix | `offres[]` (1 ou 2 ; 4 en `gamme-alignee`) : `{ "nom", "mention", "prix", "note" }` + `image` | Nom, puis « À partir de » en petit, puis le prix en gros. |
| A20 Disponibilité | `libelle` (petit, au-dessus), `titre` (date ou mot) + `image` facultative | Petit libellé gris, grande date, produit dessous. |
| A21 Synthé nom et fonction | `intervenant` (id) ou `nom` + `fonction` ; `image` facultative | Deux lignes en bas à gauche. |
| A22 à A25 Plans de scène | `image`, `titre` facultatif | Ce sont des plans vidéo. En slide, ils deviennent une photo plein cadre (avertissement), avec ou sans variante. |
| FIN Slide finale | selon la variante (`titre`, `libelle`, `lieu`, `mentions[]`) | Le logo seul, centré, mentions en très petit ; sans logo, le mot final. |
| COLORIS Gamme de coloris | `coloris[]` : `{ "nom", "hex", "image" }` (5 au plus), `afficher_noms` | Un produit par coloris, même angle et même échelle. |
| FRISE Frise | `titre`, `jalons[]` : `{ "titre", "date", "image" }` (7 au plus) | Jalons égaux sur une ligne, le dernier en accent. |
| AF À fournir | `attendu`, `archetype_prevu` facultatif | Ancien moyen de signaler une slide entière qui manque. **À éviter** : il fait un trou dans le deck. Prends l'archétype prévu, remplis-le avec des `[À VALIDER]` pour ce qui se propose et des `[À FOURNIR]` courts pour le reste, et mets la consigne dans `a_fournir`. |

### Variantes : la composition de chaque archétype

`slide.variante` choisit la composition de la slide. Le design de chaque variante, son visuel et son repli sont dans `designs.md` ; ce tableau-ci ne donne que les noms, et les champs que chacune lit en plus de ceux de l'archétype.

- **Sans variante**, le moteur garde le rendu d'origine de l'archétype. C'est le même que la première variante pour A1 (`aplat`), A3 (`centre`), A4 (`aplat`), A5 (`centre`), A7 (`centree`) et A17 (`courte`) ; ailleurs, il est plus simple que les variantes. Écris toujours la variante.
- **FIN, COLORIS et FRISE** : leurs variantes se posent sur n'importe quel archétype (`"archetype": "A1", "variante": "mot-final"`), ou avec `"archetype": "FIN"`, `"COLORIS"` ou `"FRISE"`. Sans variante, ces trois-là prennent leur première.
- Le nom se compare sans accents ni majuscules. Une variante inconnue est une erreur du contrôle ; le moteur, lui, avertit et garde le rendu d'origine.
- Un champ principal absent s'affiche en `[À FOURNIR : …]` court, au corps de son champ. Une image absente laisse place au repli de la fiche, sans nombre ni marque.
- Fond `image` : avec une variante, l'image de fond ne vient que de `image_fond`, puisque `image` est le contenu. Les variantes qui posent déjà leur photo (`sur-image`, `sur-photo`, `sur-contenu`, `capture-nue`, `macro-matiere`, A18, A21 sur photo, `signe-sur-photo`) n'en ajoutent pas.
- Voile sur photo, par défaut : 30 en A1 `sur-image` et A18 `photo-titre`, 40 en A4 `sur-image`, 45 en A5 `sur-photo` et A7 `sur-photo`, 60 en A8 `sur-contenu`. `slide.voile` le remplace.

| Archétype | Variantes | Champs en plus de ceux de l'archétype |
|---|---|---|
| A1 | `aplat`, `degrade`, `sur-image`, `entoure`, `matiere` | `entoure` : `couronne[]` (20 à 50 mots) ; `sur-image` : `image` ou `image_fond` ; `matiere` : `image` (le mot rendu en matière) |
| A2 | `icone-nom`, `icone-cote`, `logo-nom`, `rangee`, `objet-interface`, `icone-seule` | `rangee` : `images[]` (3), sans texte ; `logo-nom` : `image` ou `theme.logo` ; `objet-interface` : `titre` = le libellé du bouton ; `icone-seule` : sans texte |
| A3 | `centre`, `droite`, `ligne`, `numerote`, `suffixe`, `ligne-active`, `couleurs` | `numerote` : `numeros` (`false` = un point d'accent) ; `suffixe` : `suffixe` ; `couleurs` : `couleurs[]` (un HEX par ligne) ; `ligne-active` : `actif` = nombre de lignes pleines, une slide par état |
| A4 | `aplat`, `degrade`, `mot-accent`, `definition`, `sur-image`, `sourdine`, `enchainee` | `definition` : `mot`, `nature`, et `titre` pour la définition ; `sur-image` : `image` |
| A5 | `centre`, `bloc`, `a-cote`, `sur-photo`, `objet-anneau`, `objet-jauge`, `contour` | `a-cote` : `image` (écran, téléphone ou objet, d'après `attendu`) ; `sur-photo` : `image` (photo, déjà floutée) ; `objet-anneau` : `libelle` = l'unité ; `objet-jauge` : `libelle` facultatif |
| A6 | `barres`, `deux-axes`, `anneaux`, `frise`, `classement` | `deux-axes` : `series[]` `{ "libelle", "points", "mise_en_avant" }`, `axe_x`, `axe_y`, `sens_x`, `sens_y` ; `anneaux` : `barres[]` (2), `valeur` = part de 0 à 100 ; `frise` : `nom`, `chiffre` (l'écart), `periodes[]` (2), `generations` (3 à 6) ; `classement` : `rangs[]`, `colonnes[]` `{ "periode", "logos" }` |
| A7 | `centree`, `empilement`, `a-cote-icone`, `a-cote-objet`, `deux-colonnes`, `sur-photo`, `filet` | `empilement` : `actif` = lignes affichées ; `a-cote-icone`, `deux-colonnes` : `image` (icône) ; `a-cote-objet` : `image` (objet ou capture) ; `sur-photo` : `image` ; `filet` : `image` (capture) ; `deux-colonnes` : jusqu'à 18 lignes |
| A8 | `coche-par-ligne`, `cercles-puis-coches`, `risque-puis-reponse`, `picto-par-ligne`, `sur-contenu` | `risque-puis-reponse` : `etat` (`risque` ou `reponse`, une slide par état) ; `picto-par-ligne` : `pictos[]` (images) ou `images[]` ; `sur-contenu` : `image` |
| A9 | `appareil-centre-mot`, `objet-coupe`, `objet-liste`, `objet-chiffre`, `annotee`, `empilee` | `cote` ; `objet-chiffre` : `chiffre`, `libelle` (au lieu de `titre`) ; `annotee` : `annotations[]` (5 au plus) au lieu de `titre` |
| A10 | `telephone-centre`, `tablette-centre`, `portable-centre`, `zoom-serre`, `capture-nue`, `rangee` | sans texte ; `rangee` : `images[]` (3) |
| A11 | `legende-laterale`, `plusieurs-blocs`, `schema-chiffre`, `carte-annotee`, `carre-halo` | `titre` (nom du système), `blocs[]` `{ "titre", "lignes", "zone": [x, y, l, h] }` en %, 3 au plus en `plusieurs-blocs`, `cote` ; `schema-chiffre` : `chiffre`, `libelle` ; `carte-annotee` : `annotations[]` `{ "texte", "zone", "position" }` ; `carre-halo` : `titre`, ou `logo_systeme` |
| A12 | `macro-matiere`, `capot-ouvert`, `eclate-axial`, `flux-lumiere` | `eclate-axial` : `libelle` (l'étiquette) |
| A13 | `centre-entier`, `hero-coupe`, `profil-levitation`, `coloris` | sans texte ; `coloris` : `images[]` (2 vues) |
| A14 | `nom-au-centre`, `produit-au-centre`, `tuiles-chiffres`, `mot-geant-et-produit`, `theme-et-matieres`, `grille-icones`, `fragments-logiciel` | `image` : le produit (la photo en `theme-et-matieres`, le logo clair en `fragments-logiciel`) de la tuile centrale ; `mot-geant-et-produit` : `titre` de 2 à 5 lettres ; chaque tuile : `type` (`capture`, `icone`, `photo`, `mot`, `chiffre`, `liste`, `matiere`, `coloris`, `halo`, et `fragment` en `fragments-logiciel`), `surtitre`, `mention`, `lignes[]`, `coloris[]` ; `fragments-logiciel` : `titre` central (nom ou boucle en trois mots, `\n` entre eux), `texte` central facultatif, 6 à 11 tuiles, `fragment` = `titre` (4 mots) + `texte` (5 mots) + `image` (composant isolé) + `echelle` (0,5 pour un export 2x), `liste` = `titre` (surtitre) + `lignes[]` (5 au plus) |
| A15 | `vignettes`, `icones`, `mots`, `nuage`, `cartes-libelles`, `forme` | `elements[]` `{ "image", "titre" }` ; `mots` : `deux_tons` ; `nuage` : `titre` (le nom net au premier plan) ; `forme` : `forme` (`coeur` ou `cercle`) |
| A16 | `grille`, `ligne`, `logo-seul`, `mur-dense`, `pastilles`, `soi-au-centre` | `pastilles` : `logos[].couleur` (HEX) ; `soi-au-centre` : le logo du thème au centre |
| A17 | `courte`, `longue`, `source-accent`, `centree-signature` | aucun |
| A18 | `usage`, `exemple-cartouche`, `diptyque`, `photo-titre` | `note` (le cartouche) ; `diptyque` : `images[]` (2), `notes[]` (2) ; `photo-titre` : `titre` |
| A19 | `colonne`, `deux-offres`, `nom-en-haut`, `gamme-alignee`, `prix-heros`, `ancrage` | `gamme-alignee` : `offres[].image` (4 offres au plus) ; `ancrage` : `libelle`, `etat` (`reference` = le prix de référence, en gris ; une slide par état) |
| A20 | `haut-et-gamme`, `suite-de-dates`, `colonne`, `date-et-lieux`, `mot-seul` | `date-et-lieux` : `lieux[]` |
| A21 | `gauche`, `droite`, `double`, `sur-clair`, `carte-invite`, `carte-portrait` | `nom`, `fonction`, ou `intervenant` ; `double` : `personnes[]` `{ "nom", "fonction" }` ou `intervenants[]` ; `carte-invite` : `logo_invite` ; `carte-portrait` : `image` (le portrait) |
| A22 à A25 | A22 : `hall-ecran`, `scene-mur`, `panneau-verre` · A23 : `mot-coupe`, `contenu-lisible`, `interface-geante`, `slide-floue` · A24 : `large-centre`, `taille-centre`, `decor-sujet` · A25 : `table-flux`, `mains-fond-uni`, `epaule`, `table-haute`, `tend-appareil` | acceptées, rendues en photo de la scène à fond perdu (avertissement) |
| FIN | `signe-seul`, `signe-et-ligne`, `signe-et-evenement`, `signe-sur-photo`, `mot-final` | `mentions[]` ; logo : `logo_final`, sinon `image`, sinon `theme.logo` ; `signe-et-ligne` : `libelle` ; `signe-et-evenement` : `titre` (l'événement), `lieu` ; `signe-sur-photo` : `libelle` et la photo en `image_fond` ou `image` ; `mot-final` : `titre`, `libelle` |
| COLORIS | `rangee-alignee`, `rangee-chevauchee`, `eventail`, `un-par-un`, `mur` | `coloris[]` `{ "nom", "hex", "image" }` (5 au plus), `afficher_noms` ; `un-par-un` : `coloris[0]`, une slide par coloris |
| FRISE | `rangee-datee`, `generations`, `trois-jalons`, `courbe-et-saut`, `objet-du-passe` | `titre`, `jalons[]` `{ "titre", "date", "image" }` (7 au plus, 3 en `trois-jalons`) ; `courbe-et-saut` : `nom`, `chiffre`, `periodes[]` ; `objet-du-passe` : `image` |

Une slide finale passe en pleine page d'accent seulement si c'est la dernière, en A1 ou FIN, sans variante ou avec `aplat` ou `mot-final`, et si `theme.finale_accent` n'est pas `false`.

### Texte enrichi

- `*mot*` met le mot en couleur d'accent : `"Clairval *Direct*"`. Un mot par titre, celui qu'on doit retenir.
- `\n` force un retour à la ligne. Sinon, le moteur répartit lui-même les lignes des titres pour éviter un mot seul en dernière ligne.
- Le point final d'un titre passe en couleur d'accent (`theme.point_accent`, voir theme).
- `[À VALIDER : texte proposé]` et `[À FOURNIR : libellé court]` marquent ce que la skill propose et ce qu'elle demande. Ils valent dans tous les champs : voir la section suivante.
- La typographie française est appliquée au rendu : espace insécable avant `: ; ! ?` et entre un nombre et son unité (`4 h`, `89 € HT`).

## Marqueurs : ce que la skill propose, ce qu'elle demande

Un brief mince ne doit pas donner un deck à trous. La skill **propose** ce qui se rédige, et **demande** ce qui se vérifie.

| | `[À VALIDER : texte proposé]` | `[À FOURNIR : libellé court]` |
|---|---|---|
| Pour quoi | Ce que la skill peut rédiger elle-même : thèse, formulation d'un titre, problème vécu, description d'une fonction, phrase du script. | Ce qu'elle n'invente jamais : chiffre, prix, pourcentage, date, nom de client, logo, témoignage, capture réelle, source. |
| À l'écran | Le texte proposé, comme du vrai contenu : le marqueur est retiré, rien ne le distingue. | Le libellé, **3 mots au plus**, dans le style de son champ (même taille, même graisse), **estompé** (couleur du texte qu'il remplace à 40 %, ou la couleur du texte s'il remplace l'accent ; jamais de dégradé, même dans un `*accent*`) et souligné en pointillé discret de la couleur d'accent. |
| Dans les notes et `script.md` | Le passage reste signalé, pour que l'orateur sache ce qui n'est pas encore validé. | Le libellé reste signalé, suivi de la consigne de `a_fournir`. |
| Au contrôle | Listé dans la section « À VALIDER », jamais bloquant. **Erreur** s'il contient un chiffre, un prix, un pourcentage ou une date, ou s'il occupe un champ de témoignage (A17), de logo (A16), de prix (A19), de date (A20), de chiffre (A5, A6, A14, et tout `textes.chiffre`) ou une `source`. | Bloquant sans `--brouillon`. **Erreur**, même en brouillon, si le libellé à l'écran dépasse 3 mots. |
| En anglais | `[TO VALIDATE: …]` | `[TO PROVIDE: …]` |

- Un marqueur peut contenir un `\n` : `"[À VALIDER : Ce qu'on construit,\net *comment*.]"` s'affiche sur deux lignes, sans crochets. Un libellé `[À FOURNIR]` revient sur une seule ligne. Un marqueur sans `]` final s'afficherait tel quel : c'est une erreur du contrôle.
- Format Canva (`meta.format`: `canva`) : l'import perd l'estompé (l'opacité de 40 %). Le libellé garde donc ses crochets à l'écran (`[date]`, `[gain]`), pour se lire comme un emplacement même en couleur pleine. Les crochets ne comptent pas dans les 3 mots.
- La consigne longue ne s'écrit jamais dans le marqueur : `"prix": "[À FOURNIR : prix HT]"` à l'écran, et `"a_fournir": "Prix mensuel HT par site, pose comprise, validé par la direction commerciale."` sur la slide.
- Un même passage peut mêler les deux, côte à côte, jamais l'un dans l'autre : `"[À VALIDER : Disponible dès le] [À FOURNIR : date]"`.
- Une proposition reprise ailleurs (la thèse redite à la clôture) garde son marqueur partout où elle revient.
- À la livraison, la skill donne les deux listes, slide par slide : ce qu'il faut valider, ce qu'il faut fournir.

### Les tailles

Les tailles de texte ne s'écrivent pas dans `deck.json`. Chaque archétype a une taille maximale. Le moteur la réduit jusqu'à ce que le texte tienne, sans descendre sous un plancher. Si le texte ne tient toujours pas, le moteur le signale : il faut couper des mots, pas réduire encore.

## notes : le script à dire

Trois formes sont acceptées :

```json
"notes": "Texte dit par slide.intervenant."
```

```json
"notes": [
  { "intervenant": "claire", "type": "relais", "texte": "Pour vous en dire plus, voici Hugo. Hugo, à toi." },
  { "intervenant": "hugo", "texte": "Merci Claire. Tout commence par ce boîtier…" }
]
```

```json
"notes": ["Premier paragraphe.", "Deuxième paragraphe."]
```

- Le script suit les gabarits de `data/formules.json` et `data/annonce.json`, adaptés au registre et à la langue. On n'y reprend aucune citation de keynote.
- **Il se lit en entier, à voix haute, vers 140 mots par minute pour la durée visée** : pour 10 minutes, environ 1 400 mots, relais compris. Le contrôle compte les mots à dire (propositions `[À VALIDER]` comprises, sans les `[À FOURNIR]` ni les indications entre crochets ou parenthèses) et alerte sous 110 ou au-dessus de 170 mots par minute sur `meta.duree_min`. Les indications de scène vont dans `build`, pas dans le texte à dire.
- `"type": "relais"` marque un passage de parole. Il suit `meta.registre_intervenants` (« à toi » ou « à vous »), même si le public est vouvoyé. Le contrôle du registre du public ignore ces segments.
- Le moteur écrit dans les notes du .pptx (et sous chaque slide de l'aperçu) :

```
CLAIRE DUVAL · Directrice générale (relais)
Pour vous en dire plus, je passe la parole à Hugo…

→ HUGO BERNARD · Responsable produit
Merci Claire. Tout commence par ce petit boîtier…

APPARITIONS
1. Le boîtier apparaît d'abord, seul.
2. Les trois lignes s'affichent une à une.

MINUTAGE 3:50 → 4:45 (55 s)
SOURCE (affichée sur la slide) : …
À VALIDER : « … »
À FOURNIR : prix HT. Prix mensuel HT par site, pose comprise…
```

La flèche `→` signale un changement d'intervenant par rapport à ce qui précède. Le minutage est cumulé depuis la première slide. Sans `role`, la ligne d'en-tête porte le nom seul.

Les libellés des notes suivent la langue du deck (en anglais : HANDOVER, BUILD, TIMING, SOURCE, TO VALIDATE, TO PROVIDE). Aucun terme de travail n'y figure : ni numéro d'étape, ni nom d'archétype. L'orateur lit ses notes, il n'a pas à connaître la grammaire.

## Apparitions et transitions

- **Transitions.** Chaque slide entre par un fondu court. Rien à écrire dans `deck.json`.
- **Apparitions.** `build` liste les apparitions dans l'ordre, une phrase par clic, écrite pour l'orateur (par exemple : Le chiffre arrive quand il est dit). Le moteur pose une animation d'entrée en fondu, au clic, sur les éléments de la slide, dans l'ordre de lecture de l'archétype : surtitre et titre, puis chiffre, libellé, lignes une à une, tuiles autour de la tuile centrale, barre de l'autre puis barre de soi. Une slide sans `build` s'affiche d'un bloc.
- Une liste est écrite dans une seule zone de texte, un paragraphe par ligne, pour qu'une animation « par paragraphe » suffise si l'utilisateur la retouche.
- Avec une variante, l'ordre suit celui de sa fiche dans `designs.md` : le visuel, puis le surtitre et le titre, puis le chiffre et le libellé, puis les lignes, barres, tuiles ou logos un à un. Quelques mots de `build` désignent un groupe propre à une variante : « coches » (A8 `cercles-puis-coches`), « anneau » et « jauge » (A5), « courbes » (A6 `deux-axes`), « blocs » ou « légendes » (A11), « flux » ou « halo » (A12 `flux-lumiere`), « étiquette » (A12 `eclate-axial`), « jalons » (FRISE), « coloris » (COLORIS).
- Ce qui reste à la main : un morphing entre deux slides (Magic Move, Morphose), une vidéo à lancer, et toute apparition dont l'ordre diffère de l'ordre de lecture. `export_script.js --etapes` en donne la liste.

## Public, sources et procédés

`references/publics.md` dit, pour chaque public, quels procédés garder. `references/data/publics-exigences.json` en est la version machine, et `check_deck.py` et `build_deck.js` lisent tous les deux ce fichier. Quand `publics.md` change, on met ce fichier à jour.

| Clé | Valeurs | Effet |
|---|---|---|
| `source_chiffre` | `exigee`, `recommandee`, `facultative` | `exigee` : un chiffre sans `source` est une erreur bloquante. C'est le réglage de tous les publics : la skill n'invente aucun chiffre, et chaque chiffre vient de l'utilisateur avec sa source. |
| `affichage_source` | `sous_le_chiffre`, `renvoi`, `carton_final`, `aucun` | `sous_le_chiffre` : la source en clair, en petit sous le chiffre. `renvoi` : « Source 1 · en fin de présentation » sous le chiffre, et la source complète sur la slide finale « Sources et mentions ». `carton_final` : rien sur la slide, tout sur la slide finale. `aucun` : seulement dans les notes. |
| `graduation` | `sans`, `valeurs`, `graduee` | `valeurs` et `graduee` écrivent les valeurs au bout des barres A6, même sans `etiquette`. `graduee` déclenche un avertissement : A6 n'a pas d'axe, il faut un graphique natif si l'axe compte. |
| `concurrent` | `nommes`, `nommes_si_utile`, `anonymes`, `absents` | `nommes` signale une barre au libellé anonyme (« solution classique »). `absents` signale toute barre de concurrent. |
| `jusqua` | `avec_condition`, `valeur_typique`, `interdit` | « jusqu'à » à l'écran : `avec_condition` demande une `source` qui donne les conditions, `valeur_typique` le signale (le maximum se dit à l'oral, avec sa condition), `interdit` est une erreur bloquante. |
| `superlatifs` | `avec_preuve`, `moderes`, `aucun` | `aucun` : tout superlatif à l'écran est signalé. `moderes` : un seul par bloc. Dans tous les cas, un superlatif absolu (« au monde », « le meilleur ») sans `source` est signalé. |
| `slide_prix` | `oui`, `non` | `non` : une slide A19 est signalée (pour les investisseurs, on présente le modèle économique). |
| `duree_min_conseillee` | `[min, max]` ou `null` | Durée cible hors fourchette : avertissement. |
| `registre_suggere` | texte | Indication pour la question tu / vous. Le registre reste demandé à l'utilisateur. |

Publics prévus, dans l'ordre de la question : `b2b-decideurs`, `b2b-acheteurs`, `grand-public`, `investisseurs`, `partenaires`, `interne-sprint`, `interne-demo`, `interne-all-hands`, `salon-conference`, `recrutement`, `defaut`. Un public inconnu reçoit la ligne `defaut`, la plus prudente. Pour un public mixte, chaque réglage prend la valeur la plus prudente des publics présents, selon l'ordre `prudence` du fichier.

Une slide est considérée comme chiffrée si c'est une A5 ou une A6, une A14 dont une tuile porte un chiffre, une slide qui remplit `textes.chiffre` (A9 `objet-chiffre`, A11 `schema-chiffre`, FRISE `courbe-et-saut`…), ou si son texte contient un %, un multiplicateur (« 2x », « 3 fois ») ou « jusqu'à N ». Les prix (A19) et les dates (A20) ne demandent pas de source.

## Images

- Formats lus : PNG, JPEG, GIF. Les dimensions sont lues dans le fichier, et l'image n'est jamais déformée.
- `ajustement` : `contenir` (par défaut, l'image entière dans sa boîte) ou `couvrir` (la boîte est remplie et l'image recadrée ; par défaut pour les archétypes plein cadre).
- Image absente ou illisible : le moteur **dessine un placeholder** dans le style de la slide, sur son fond : une interface schématique (fenêtre, barres et blocs gris, un élément en accent) pour une capture, une silhouette simple pour un objet ou une photo. Aucun chiffre ni texte inventé dedans : des barres grises, pas des nombres. Aucune consigne à l'écran : `attendu` part dans les notes, et le contrôle le reprend (« Image à fournir »). Le rendu continue, et le placeholder reste dans le .pptx tant que l'image manque.
- Écris toujours `{ "chemin": "images/....png", "attendu": "…" }` pour une image qui manque : le chemin dit où la déposer, `attendu` dit ce qu'elle doit montrer.
- Pour A16, fournir des logos d'une seule couleur. Le moteur ne recolore pas les images.
- Une capture est toujours nue : le moteur pose l'appareil générique (coins de 13 % de sa largeur, bord de 3 % ; ni encoche, ni bouton, ni caméra, ni logo), et la capture couvre son écran.
- Images portées par un élément : `tuiles[].image` (A14), `elements[].image` (A15), `logos[].image` (A16), `offres[].image` (A19 `gamme-alignee`), `coloris[].image` (COLORIS), `jalons[].image` (FRISE), `colonnes[].logos[].image` (A6 `classement`). Plusieurs visuels sur une slide : `images[]`.
- Le repli dépend de la variante (silhouette, interface schématique, tuile d'icône, pictogramme gris, aplat et deux halos neutres) : `designs.md`, §7 de chaque fiche. Il ne porte jamais de nombre, de texte inventé ni de marque.

## Visuels à préparer : `slide.visuel`

`image` dit où est le fichier et ce qu'il montre. `visuel` dit comment le préparer : c'est le brief que l'utilisateur, son graphiste ou son photographe reçoit. La skill le remplit à l'étape « Design slide par slide », d'après le §7 de la fiche de l'archétype dans `designs.md`. Il n'apparaît ni à l'écran ni dans les notes.

```json
"image": { "chemin": "images/apercu.png", "attendu": "Écran de personnalisation d'un carnet, aperçu de la couverture" },
"visuel": {
  "type": "capture",
  "brief": "Écran de personnalisation d'un carnet, aperçu de la couverture ; données de démonstration, heure neutre, sans notification.",
  "fond_transparent": false,
  "angle": "face",
  "resolution_min": "1170 × 2532"
}
```

| Champ | Valeurs | Rôle |
|---|---|---|
| `type` | `capture`, `photo`, `produit`, `objet`, `icone`, `logo`, `schema`, `matiere`, `pictogrammes`, `vignettes`, `video` | La nature du visuel. Il donne le format et la résolution par défaut. |
| `brief` | texte | Ce que le visuel doit montrer, son cadrage, sa lumière, ce qu'il ne doit pas contenir. Une ou deux phrases, écrites pour la personne qui le prépare. |
| `fond_transparent` | `true` ou `false` | `true` pour un produit, un objet, une icône ou un logo détourés (PNG ou SVG). Absent : la valeur du type. |
| `angle` | texte : `face`, `trois-quarts`, `profil`, `dessus`, `contre-plongée`… | La vue demandée. Absent : libre. |
| `resolution_min` | `"1920 × 1080"`, `[1920, 1080]`, ou un nombre (pixels sur le grand côté) | La taille minimale du fichier. Absent : la valeur du type. |
| `format` | facultatif : `PNG`, `JPEG`, `SVG`, `MP4`… | Remplace le format du type. |
| `chemin` | facultatif | Où déposer le fichier, quand ce n'est pas `image.chemin` (un second visuel, une tuile). |

Valeurs par défaut de chaque type (celles du §7 des fiches) :

| Type | Format | Fond transparent | Résolution minimale |
|---|---|---|---|
| `capture` | PNG | non | résolution native de l'écran (téléphone 1170 × 2532 ; écran large 1920 × 1080) |
| `photo` | JPEG | non | 1920 × 1080 (3840 × 2160 conseillé) |
| `produit`, `objet` | PNG | oui | 2000 px de haut (produit) ou sur le grand côté (objet) |
| `icone` | SVG ou PNG | oui | 1024 × 1024 |
| `logo` | SVG ou PNG | oui | 600 px de large (1000 px de haut pour la slide finale) |
| `schema` | SVG ou PNG | oui | 2000 × 2000 |
| `matiere` | JPEG | non | 1920 × 1080 |
| `pictogrammes` | SVG | oui | vectoriel, un fichier par pictogramme |
| `vignettes` | JPEG ou PNG | non | 640 px de large chacune, toutes au même format |
| `video` | MP4 | non | 1920 × 1080 (3840 × 2160 conseillé) |

- Une slide qui demande plusieurs visuels (deux vues d'un produit, un éventail de coloris) prend une liste : `"visuel": [ {…}, {…} ]`.
- Sans `visuel`, `export_script.js --visuels` déduit le type de l'archétype et de la variante, et prend `image.attendu` comme brief. Écris quand même `visuel` : un brief précis évite une seconde séance photo.
- Le brief ne contient ni consigne d'atelier ni nom d'archétype : il s'adresse à quelqu'un qui ne connaît pas la skill.
- Le moteur dessine un repli tant que le fichier manque (voir Images). Le brief ne change rien au repli.

```bash
node "$SKILL/scripts/export_script.js" deck.json --visuels visuels.md
```

`visuels.md` liste, slide par slide, chaque visuel : son type, son brief, son format, le fond transparent, l'angle, la résolution minimale, le fichier attendu, et s'il est déjà fourni. C'est la liste livrée à l'utilisateur.

## Ce que vérifie check_deck.py

Erreurs bloquantes (code de sortie 1) :
- archétype inconnu ;
- variante inconnue pour l'archétype, ou variante sur un archétype qui n'en a pas (liste du tableau « Variantes ») ;
- `slide.visuel` qui n'est ni un objet ni une liste d'objets ;
- champ obligatoire manquant (tableau des archétypes ; certaines variantes en demandent d'autres, voir « Variantes ») ;
- deux chiffres sur une slide-chiffre A5 ;
- chiffre sans source quand le public l'exige ;
- marqueur `[À FOURNIR]` restant, consigne `a_fournir` ou slide `AF` (avertissement seulement avec `--brouillon`) ;
- libellé `[À FOURNIR]` de plus de 3 mots à l'écran (`textes` ou `source`), même avec `--brouillon` ;
- `[À VALIDER]` qui contient un chiffre, un prix, un pourcentage ou une date (y compris en lettres : « deux », « gratuit », « en janvier », « en une heure »), ou qui occupe un témoignage, un logo, un prix, une date, un chiffre ou une source ;
- marqueurs imbriqués, ou marqueur sans `]` final ;
- police d'Apple dans le thème (SF, New York) ;
- notes vides ;
- `duree_s` absente ;
- durée totale à plus de 15 % de `duree_min` ;
- script qui tutoie plus qu'il ne vouvoie alors que le registre est `vous` (ou l'inverse) ;
- `meta.registre`, `meta.format`, `meta.public`, `meta.duree_min` ou `meta.affichage_source` absents ou invalides, `meta.registre_intervenants` invalide ;
- « jusqu'à » à l'écran quand le public l'interdit ;
- graphique sans valeurs (`afficher_valeurs: false`) quand le public les attend ;
- ratio autre que 16:9 ;
- couleur obligatoire absente ou HEX invalide ;
- intervenant inconnu ;
- `id` en double.

Avertissements :
- plus de 10 mots à l'écran (hors listes, citations, bento, murs et logos) ;
- carte-titre de plus de trois mots, libellé de chiffre de plus de neuf mots ;
- liste trop longue (6 lignes, 18 en A7 `deux-colonnes`), bento hors 4 à 8 tuiles (4 à 10 en grille « produit », 3 à 12 en `grille-icones`), plus de 2 offres (4 en `gamme-alignee`) ;
- tutoiement ou vouvoiement isolé ; relais qui ne suit pas `registre_intervenants`, ou `registre_intervenants` absent avec plusieurs intervenants ;
- `meta.variante` ou `meta.contexte` inconnus ;
- débit supérieur à 170 mots par minute sur une slide ;
- script trop court ou trop long pour la durée visée : moins de 110 ou plus de 170 mots par minute sur `meta.duree_min` (mots à dire, hors `[À FOURNIR]` et indications) ;
- deux slides consécutives du même bloc qui passent de `sombre` à `clair` (ou l'inverse) ;
- surtitre de plus de 3 mots ;
- rôle d'intervenant écrit en marqueur ;
- `theme.point_accent` ou `theme.finale_accent` qui n'est pas `true` ou `false` ;
- image manquante (« Image à fournir », avec son `attendu`) ;
- variante à image sans aucune image (`image`, `images`, `image_fond`, image d'élément ou `slide.visuel`) : le repli sera dessiné ;
- images de `images[]`, d'éléments (`offres`, `coloris`, `jalons`, `elements`, `pictos`, `colonnes`) ou logos annexes introuvables ; logos sans image (leur nom s'écrit en texte) ;
- `slide.visuel` sans `type` ou sans `brief`, type inconnu, `fond_transparent` qui n'est pas `true` ou `false`, `resolution_min` illisible, champ inconnu ;
- `slide.profondeur` qui n'est pas `true` ou `false`, `slide.appareil` inconnu ;
- trois slides de suite avec le même archétype et la même variante (la variante absente compte pour celle du moteur) ;
- bloc de deux slides ou plus sans moment visuel : ni A5, A9, A10, A13, A14 ou A18, ni variante à image (colonne « Moment visuel fort » de la table « Les variantes du moteur », `designs.md`) ;
- contraste faible (`accent2` compris) ;
- « jusqu'à », superlatifs, concurrents, graphique à graduer, slide de prix et durée hors fourchette, selon le public ;
- plans de scène A22 à A25 (avec ou sans variante), et A11 sans variante, rendus autrement.

Section à part, jamais bloquante : **À VALIDER**, la liste des propositions, slide par slide (clé `a_valider` avec `--json`). La livraison la reprend telle quelle.

## Exemple complet

Voici un deck court mais complet : un créneau de deux minutes sur un salon, avec deux voix. Chaque slide a sa variante ; le prix d'un service sans objet prend `prix-heros`, et la capture qui manque a son brief dans `visuel`. Une version de 16 slides se trouve dans `assets/exemple-deck.json`, avec ses images dans `assets/exemple-images/`. Tout y est fictif.

```json
{
  "meta": {
    "titre": "Atelier Brume : nouvelle offre",
    "langue": "fr",
    "registre": "vous",
    "registre_intervenants": "tu",
    "public": { "type": "salon-conference", "description": "Visiteurs d'un salon professionnel, créneau de 2 minutes" },
    "duree_min": 2,
    "format": "powerpoint",
    "ratio": "16:9"
  },
  "theme": {
    "nom": "Atelier Brume",
    "couleurs": {
      "fond_sombre": "#1A1F24", "fond_clair": "#FFFFFF", "texte": "#1A1F24",
      "texte_secondaire": "#5E6670", "accent": "#E8622C", "accent2": "#F59E5B"
    },
    "polices": { "titre": { "nom": "Arial", "repli": "Arial" }, "texte": "Arial" },
    "point_accent": true
  },
  "intervenants": [
    { "id": "lea", "nom": "Léa Morin", "role": "Fondatrice" },
    { "id": "tom", "nom": "Tom Girard" }
  ],
  "slides": [
    {
      "id": "s1", "bloc": "Ouverture", "archetype": "A1", "variante": "aplat", "fond": "sombre", "intervenant": "lea",
      "textes": { "titre": "Bonjour." },
      "notes": "Bonjour à toutes et à tous, et merci d'être passés sur notre stand. Je suis Léa, je dirige Atelier Brume, l'atelier de papeterie que beaucoup d'entre vous connaissent déjà. Nous avons deux minutes, et une nouveauté à vous montrer.",
      "duree_s": 20, "build": ["Le mot est à l'écran avant la prise de parole."]
    },
    {
      "id": "s2", "bloc": "Brume Sur-mesure", "etape": 3, "archetype": "A5", "variante": "centre", "fond": "sombre", "intervenant": "lea",
      "textes": { "surtitre": "Aujourd'hui", "chiffre": "[À FOURNIR : délai actuel]", "libelle": "d'attente moyenne pour un carnet personnalisé" },
      "source": "[À FOURNIR : source]",
      "a_fournir": "Délai moyen actuel pour fabriquer un carnet personnalisé, avec sa source (relevé interne, étude) et sa période.",
      "notes": "Aujourd'hui, quand vous nous commandez un carnet personnalisé, vous attendez en moyenne [À FOURNIR : délai actuel]. C'est le retour que vous nous faites le plus souvent, et nous l'entendons. Un carnet qui tarde, c'est un client qui attend, ou une vitrine vide. Nous avons voulu changer cela.",
      "duree_s": 25, "build": ["Le surtitre d'abord.", "Le chiffre arrive quand il est dit, puis le libellé."]
    },
    {
      "id": "s3", "bloc": "Brume Sur-mesure", "etape": 6, "archetype": "A1", "variante": "aplat", "fond": "sombre", "intervenant": "lea",
      "textes": { "surtitre": "Nouveau", "titre": "Brume *Sur-mesure*" },
      "notes": [
        { "intervenant": "lea", "texte": "Voici Brume Sur-mesure." },
        { "intervenant": "lea", "type": "relais", "texte": "Tom l'a conçu avec notre atelier de reliure. Il va vous en dire plus. Tom, à toi." }
      ],
      "duree_s": 15, "build": ["Le nom apparaît seul, au moment où il est dit. Deux secondes de silence."]
    },
    {
      "id": "s4", "bloc": "Brume Sur-mesure", "etape": 9, "archetype": "A9", "variante": "objet-liste", "fond": "sombre", "intervenant": "tom",
      "textes": {
        "titre": "[À VALIDER : Composé le matin, relié le soir.]",
        "lignes": ["[À VALIDER : Votre couverture, votre papier]", "Sans minimum", "Aperçu en direct"]
      },
      "image": { "chemin": "images/apercu.png", "attendu": "Écran de personnalisation d'un carnet sur téléphone, aperçu de la couverture" },
      "visuel": { "type": "capture", "brief": "Écran de personnalisation d'un carnet, aperçu de la couverture ; données de démonstration, heure neutre, sans notification.", "fond_transparent": false, "angle": "face", "resolution_min": "1170 × 2532" },
      "notes": "Merci Léa. [À VALIDER : Vous composez votre carnet le matin, nous le relions le soir.] Il n'y a pas de minimum de commande : un exemplaire ou cinquante, c'est le même service. Et vous voyez votre carnet prendre forme en direct, depuis votre téléphone, à chaque choix de papier ou de couverture. Vous savez toujours à quoi il ressemblera, et votre client aussi, si vous lui transférez le lien.",
      "duree_s": 30, "build": ["L'écran d'abord.", "Le titre, puis les trois lignes une à une."]
    },
    {
      "id": "s5", "bloc": "Brume Sur-mesure", "etape": 15, "archetype": "A19", "variante": "prix-heros", "fond": "sombre", "intervenant": "tom",
      "textes": { "offres": [{ "nom": "Brume Sur-mesure", "mention": "À partir de", "prix": "[À FOURNIR : prix HT]", "note": "par carnet" }] },
      "a_fournir": "Prix HT d'un carnet Sur-mesure, validé par Léa.",
      "notes": [
        { "intervenant": "tom", "texte": "Brume Sur-mesure est proposé à partir de [À FOURNIR : prix] hors taxes par carnet, sans abonnement. Vous pouvez l'essayer dès aujourd'hui : composez votre premier carnet ici, sur le stand, avec moi." },
        { "intervenant": "tom", "type": "relais", "texte": "Léa, je te rends la parole." }
      ],
      "duree_s": 25, "build": ["Le nom, puis le prix."]
    },
    {
      "id": "s6", "bloc": "Clôture", "archetype": "A1", "variante": "mot-final", "fond": "sombre", "intervenant": "lea",
      "textes": { "titre": "Merci." },
      "notes": "Merci Tom. Et merci à vous. [À VALIDER : Brume Sur-mesure, c'est composer son carnet le matin et le tenir en main le soir.] Passez nous voir avant de partir : nous avons des échantillons pour vous, et Tom vous montrera l'aperçu sur son téléphone. Très bonne fin de salon !",
      "duree_s": 20
    }
  ]
}
```

Avec `check_deck.py --brouillon`, cet exemple passe sans erreur, avec trois avertissements voulus : le délai et sa source, le prix, et l'image qui manque. La section « À VALIDER » liste les quatre propositions : le titre, la ligne et la phrase de la slide 4, la phrase reprise à la clôture. Sans `--brouillon`, les `[À FOURNIR]` et les `a_fournir` le bloquent tant que l'utilisateur n'a pas donné le délai, la source et le prix. La skill les lui demande avant de livrer, et lui fait valider les propositions.
