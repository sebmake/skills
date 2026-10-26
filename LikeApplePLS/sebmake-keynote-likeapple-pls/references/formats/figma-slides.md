# Format Figma Slides (16:9)

Ici, on ne passe pas par le .pptx : on construit le deck directement dans Figma Slides avec l'outil `use_figma` (serveur MCP Figma). Une slide Figma Slides fait 1920 × 1080 : c'est déjà du 16:9.

## 1. Prérequis

**Les outils.** Vérifier que la session a les outils Figma : `use_figma`, `create_new_file`, `whoami`, `get_screenshot`, et pour lire un design system `get_design_context`, `get_variable_defs`, `search_design_system`. S'ils sont différés, charger leurs schémas en une seule recherche d'outils. S'ils manquent : le dire à l'utilisateur (le connecteur Figma doit être branché), et proposer la voie de secours de la section 6.

**Les skills Figma, à charger avant tout appel `use_figma`.** Dans cet ordre :
1. `figma-use` : les règles de l'API Plugin (obligatoire avant chaque `use_figma`) ;
2. `figma-use-slides` : les règles propres à Slides ;
3. `figma-create-new-file` : avant l'appel à `create_new_file`.

Les trouver si le nom exact n'est pas dans la liste des skills :

```bash
find ~/.claude/plugins "$HOME/Library/Application Support/Claude" -name SKILL.md -path "*figma-use*" 2>/dev/null
```

Elles peuvent aussi venir du serveur MCP Figma (ressource `skill://figma/figma-use/SKILL.md`). Dans chaque appel `use_figma`, passer `skillNames: "figma-use,figma-use-slides"` (préfixe `resource:` si elles viennent d'une ressource MCP).

## 2. Lire l'habillage

- **Lien Figma vers un fichier Design** (`figma.com/design/...`) : `get_design_context` et `get_variable_defs` pour les couleurs, les polices et les styles ; `get_screenshot` pour l'aspect.
- **Lien vers un fichier Slides** (`figma.com/slides/...`) : `get_metadata` ne marche pas sur Slides. Utiliser `use_figma` en lecture seule sur ce fichier, plus `get_screenshot`.
- **Bibliothèque publiée** : `search_design_system` pour trouver les variables et styles, puis les importer par clé.
- **Pas de lien, seulement des HEX** : on crée les variables (section 3, étape 3).
- Ne jamais inventer une couleur ou une police que l'utilisateur n'a pas donnée sans le lui dire.

## 3. La recette

1. **Plan d'abord** (phase 1 de `figma-use-slides`). Pour chaque entrée de `deck.json` : archétype, disposition décrite en mots, fond. Puis un préambule de code commun : palette `C`, chargement des polices, fonctions `addFrame` / `addText` / `addRect` de `references/slide-gotchas.md` (dans la skill `figma-use-slides`).
2. **Créer le fichier.** `whoami` pour le `planKey` (demander à l'utilisateur s'il a plusieurs équipes), puis `create_new_file` avec le type Slides. Garder le `file_key` rendu. Le fichier neuf est vide : la première `figma.createSlide()` crée la première rangée.
3. **Variables de couleur depuis le thème.** Un fichier Slides neuf a un thème clair par défaut : ne pas s'en inspirer. Lire d'abord les collections locales (`await figma.variables.getLocalVariableCollectionsAsync()`). Écraser leurs valeurs avec le thème de `deck.json` ; sinon créer une collection « Thème présentation » avec `fond`, `texte`, `texte-secondaire`, `accent`. Valeur de variable : `{r, g, b, a}` en 0–1 (le HEX divisé par 255). Fixer les `scopes` (FRAME_FILL et SHAPE_FILL pour les fonds, TEXT_FILL pour le texte). Lier chaque remplissage avec `setBoundVariableForPaint`, qui rend une nouvelle peinture à réaffecter.
4. **Une slide par entrée de `deck.json`**, dans l'ordre, 3 à 5 slides par appel `use_figma`. Toujours `appendChild` avant de fixer `x` / `y`. Charger chaque police avant d'écrire (`listAvailableFontsAsync` si le style exact est incertain ; ne jamais deviner « SemiBold » ou « Semi Bold »).
5. **Sections.** Chaque rangée de la grille est une section. Nommer les rangées (`SLIDE_ROW.name`) d'après les blocs du déroulé : ouverture, chaque bloc, récap, clôture.
6. **Notes du présentateur.** `slide.speakerNotes = "..."` (texte en markdown). Y mettre le texte à dire en entier (champ `notes`, chaque segment précédé du nom de l'intervenant, relais compris), puis les apparitions en liste (`- clic : …`, champ `build`) et la durée (`duree_s`). Formats acceptés : listes, gras, italique. Pas de titres `#`, pas de liens, pas de code : ils s'affichent tels quels.
7. **Valider chaque lot** avec le script de validation de `slide-gotchas.md` (chevauchements, texte coupé, objets hors cadre). Capture d'écran après le premier lot et après le dernier seulement.
8. **Rendre les identifiants** créés à chaque appel, et le lien du fichier à l'utilisateur.

## 4. Les étapes (builds)

L'API ne pose ni transition ni animation (`setSlideTransition` lève « not implemented »). Deux options :
- une slide par état (on duplique la slide et on ajoute l'élément suivant), construite par l'API ;
- puis l'utilisateur relie ces slides dans l'interface par la transition Smart Animate, sinon par un fondu. Lui donner la liste des apparitions : `node "$SKILL/scripts/export_script.js" deck.json --etapes`.

## 5. Limites à signaler

- Pas de transitions ni d'animations par l'API (voir section 4).
- Le thème de slide n'est que lisible (`slideThemeId`) ; on passe par les variables.
- Tableaux et médias (`createTable`, `createGif`) bloqués dans Slides par l'API : les ajouter dans l'interface.
- `get_metadata` ne marche pas sur un fichier Slides.
- `figma.createPage()` n'existe pas dans Slides.
- Sur un deck existant : modifier en place, ne jamais supprimer des slides pour les refaire.
- Si la session propose aussi `generate_deck` : ne pas l'utiliser en plus. Ses gabarits ne suivent ni l'habillage de l'utilisateur ni la grammaire.

## 6. Voie de secours sans connecteur

Construire le .pptx avec `build_deck.js` (voir `powerpoint.md`), puis l'importer dans Figma Slides depuis l'interface, si l'espace de l'utilisateur propose l'import PowerPoint. Mêmes contrôles qu'à la section 7 : polices, notes, 16:9.

## 7. Check-list avant de livrer

- [ ] `figma-use` puis `figma-use-slides` chargées avant le premier `use_figma`.
- [ ] Une slide par entrée de `deck.json`, toutes en 1920 × 1080.
- [ ] Couleurs liées aux variables du thème, pas codées en dur.
- [ ] Polices du design system chargées ; jamais de police Apple.
- [ ] Aucun logo ni image Apple.
- [ ] Validation de lot passée ; captures de contrôle regardées.
- [ ] Notes de chaque slide : texte à dire, clics, relais, durée.
- [ ] Sections nommées d'après le déroulé.
- [ ] Aucun chiffre, prix, date ou témoignage inventé ; les `[À FOURNIR]` restants sont signalés.
- [ ] Tutoiement ou vouvoiement constant, comme choisi au départ.
- [ ] Les limites (animations, tableaux, médias) sont dites à l'utilisateur, avec la liste des étapes.
