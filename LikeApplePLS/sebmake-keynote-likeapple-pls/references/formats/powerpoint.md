# Format PowerPoint (.pptx, 16:9)

Le .pptx est le format de base. Keynote, Canva et l'import Figma Slides partent aussi de lui.
Il est toujours en 16:9 : 10 × 5,625 pouces (25,4 × 14,29 cm), le format « Affichage à l'écran (16:9) » de PowerPoint.

## 1. Construire le fichier

Le moteur commun est `scripts/build_deck.js` (Node, bibliothèque pptxgenjs). Il lit `deck.json` et écrit le .pptx et un aperçu HTML.

```bash
SKILL=~/.claude/skills/sebmake-keynote-likeapple-pls
[ -d "$SKILL/scripts/node_modules/pptxgenjs" ] || (cd "$SKILL/scripts" && npm install)
node "$SKILL/scripts/build_deck.js" deck.json sortie.pptx --preview sortie.html
```

- Lancer la commande depuis le dossier de travail de l'utilisateur, pas depuis la skill.
- Si `node` manque : le dire à l'utilisateur et livrer `deck.json` et le script. Ne rien installer à sa place.
- Le script prévoit une slide par entrée de `deck.json`, les couleurs et polices du thème, et le texte à dire dans les notes.
- Le .pptx écrit toujours les polices du thème, même si elles manquent sur la machine qui le construit. La console le signale alors, et l'aperçu s'affiche dans la police de repli. Installer la police sur la machine qui présente. `--polices repli` écrit la police de repli à la place.
- Les marqueurs `[À FOURNIR]` restent visibles sur la slide, estompés pour se lire comme des emplacements. Ne jamais les remplacer par une valeur inventée.

## 2. Contrôler l'aperçu avant d'envoyer

Ouvrir `sortie.html` dans un navigateur. C'est le contrôle le plus rapide.

- Une idée par écran, 10 mots au plus hors listes.
- Les textes géants (carte-titre, gros chiffre) ne débordent pas.
- Les couleurs sont celles du thème (HEX donnés par l'utilisateur ou lus dans son design system).
- L'aperçu utilise les polices du navigateur. Le rendu dans PowerPoint peut différer : voir la section 3.

## 3. Ce que l'utilisateur vérifie à l'ouverture

**Les polices.** Le .pptx nomme les polices, il ne les contient pas.
- Si une police n'est pas installée sur l'ordinateur, PowerPoint la remplace, souvent sans prévenir.
- Pour voir les polices du fichier : Accueil > Remplacer > Remplacer les polices (Windows), ou Format > Remplacer les polices (Mac).
- Si une police manque : l'installer (fichiers du design system), puis rouvrir. Sinon, la remplacer par la police de secours choisie avec l'utilisateur.
- Jamais de police Apple (SF, New York) en secours, même si elle est installée.
- Pour un fichier qui voyage : incorporer les polices. Fichier > Options > Enregistrement > Incorporer les polices (Windows) ; PowerPoint > Préférences > Enregistrer (Mac, versions récentes). Seulement si la licence de la police le permet.

**Le reste.**
- Format : Conception > Taille des diapositives > Taille personnalisée indique 25,4 × 14,29 cm (16:9). Ne pas choisir « Écran large » : c'est aussi du 16:9, mais PowerPoint redimensionnerait tout le contenu.
- Texte qui passe à la ligne : une police de remplacement est souvent plus large. Revoir les titres.
- Couleurs : sélectionner une forme, Couleur de remplissage > Autres couleurs, comparer le code HEX.
- Marqueurs : chercher `[À FOURNIR]` (Ctrl+F ou Cmd+F). Il ne doit plus en rester à la livraison, ou l'utilisateur doit savoir lesquels restent.

## 4. Notes du présentateur

`build_deck.js` écrit le script de chaque slide dans ses notes : le texte à dire, les clics (étapes), le relais vers l'intervenant suivant et la durée cible (`duree_s`).

- Afficher les notes : bouton Notes dans la barre d'état, ou Affichage > Page de notes.
- Imprimer le script : Fichier > Imprimer > Pages de notes.
- Le tutoiement ou le vouvoiement a été choisi par l'utilisateur au départ. Vérifier qu'il est le même dans toutes les notes.

## 5. Mode présentateur

- Lancer : Diaporama > Utiliser le mode Présentateur, puis À partir du début. Raccourci Windows : Alt+F5.
- L'écran de l'orateur montre la slide en cours, la suivante, les notes et un chronomètre. Le public ne voit que la slide.
- En visio (Teams, Zoom, Meet) : partager la fenêtre du diaporama, pas l'écran entier. Sinon le public voit les notes.
- Répéter avec le minutage : Diaporama > Vérification du minutage. Comparer avec la somme des `duree_s`.

## 6. Les étapes (builds) : déjà posées, à vérifier

`build_deck.js` pose lui-même un fondu court entre chaque slide et des apparitions en fondu, au clic, dans l'ordre du champ `build` (lignes de liste, chiffre puis libellé, tuiles, prix après le nom). À l'ouverture, les vérifier dans Animations > Volet Animation, et les retoucher si besoin :

- Sélectionner l'objet > Animations > Apparaître (effet sec) ou Fondu (effet doux). Démarrage : Au clic.
- Liste : Options d'effet > Par paragraphe. Une ligne s'allume à chaque clic.
- Ordre : Animations > Volet Animation.
- Le grand mot qui change sur la même image (disponibilité) ou le chiffre qui se transforme : deux slides identiques sauf ce mot, et la transition Morphose sur la seconde (Microsoft 365, PowerPoint 2019 et suivants). Sinon, Fondu.
- Transitions entre slides : le fondu court posé par le moteur. Rien de plus.

La table archétype → étapes → effet est dans `keynote.md` (section 4). Les noms PowerPoint correspondants : Apparition = Apparaître, Dissolution = Fondu, Déplacement magique = Morphose.

Lister les apparitions prévues (champ `build` de `deck.json`), slide par slide, avec l'effet conseillé :

```bash
node "$SKILL/scripts/export_script.js" deck.json --etapes
```

## 7. Check-list avant de livrer

- [ ] Le fichier est en 16:9 (25,4 × 14,29 cm).
- [ ] L'aperçu HTML a été ouvert et relu slide par slide.
- [ ] Aucun logo, image ou police Apple ; seulement l'habillage de l'utilisateur.
- [ ] Aucun chiffre, prix, date ou témoignage inventé ; les `[À FOURNIR]` restants sont listés pour l'utilisateur.
- [ ] Les procédés gardés (graphique sans graduation, concurrent anonyme, « jusqu'à »…) sont adaptés au public déclaré.
- [ ] Chaque slide a son texte à dire dans les notes, avec le relais et la durée.
- [ ] La somme des durées tient dans le temps prévu.
- [ ] Tutoiement ou vouvoiement constant, comme choisi par l'utilisateur.
- [ ] La liste des étapes à poser à la main est donnée à l'utilisateur.
- [ ] L'utilisateur sait quelles polices installer ou incorporer.
