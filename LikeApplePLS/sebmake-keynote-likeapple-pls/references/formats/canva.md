# Format Canva (présentation 16:9)

Deux voies : un connecteur Canva branché dans la session, ou l'import manuel du .pptx. Le .pptx se construit avec `build_deck.js` (voir `powerpoint.md`, section 1).

## 1. D'abord : un connecteur Canva est-il branché ?

Ne jamais supposer qu'il existe. Vérifier la liste de ses propres outils :

- chercher un outil dont le nom contient `canva` (casse ignorée) ;
- si des outils sont différés, lancer une recherche d'outils avec le mot `canva` ;
- lire la description de chaque outil trouvé avant de l'appeler. Les noms changent d'un connecteur à l'autre.

**S'il y en a un, l'utiliser plutôt que l'import manuel.**
- Préférer un outil qui importe un fichier ou une URL de fichier : on lui donne le .pptx construit par `build_deck.js`. La grammaire et le script restent ceux de la skill.
- Éviter un outil qui « génère » un design à partir d'une consigne : il impose ses propres mises en page, qui ne suivent pas la grammaire.
- Si l'outil demande une URL publique du .pptx, demander à l'utilisateur où héberger le fichier. Ne rien mettre en ligne sans son accord.
- Si le connecteur liste des kits de marque (Brand Kit), demander à l'utilisateur lequel utiliser. C'est son design system.
- Après l'import, relire le design avec les outils de lecture du connecteur s'il y en a (pages, textes) : nombre de pages, notes, marqueurs `[À FOURNIR]`.
- Donner à l'utilisateur le lien du design créé.

**S'il n'y en a pas, passer à la section 2.** Le dire en une phrase, sans proposer d'installer quoi que ce soit.

## 2. Import manuel du .pptx

1. Construire `sortie.pptx` avec `build_deck.js`.
2. Dans Canva, sur la page d'accueil : bouton Importer, ou glisser le fichier sur la page. Selon la version, l'entrée peut aussi être Créer un design > Importer un fichier.
3. Canva convertit le fichier en présentation modifiable.
4. Vérifier le format : le rapport doit être 16:9 (1920 × 1080 px pour une présentation Canva standard ; un import peut garder une autre taille de même rapport). Menu Redimensionner pour le voir.

## 3. Limites connues de l'import

**Polices.** Canva n'utilise que sa bibliothèque et les polices déposées dans le kit de marque (offres payantes).
- Une police absente est remplacée par une police Canva.
- Pour garder la sienne : la déposer dans le kit de marque (si la licence le permet), puis réimporter le .pptx.
- Sinon : choisir avec l'utilisateur la police la plus proche de son design system. Jamais une police Apple ni une imitation.
- Après un remplacement, revoir les titres : les retours à la ligne changent.

**Notes du présentateur.** Canva a des notes par page (bouton Notes sous la page).
- L'import les reprend en général, mais pas toujours. Vérifier page par page.
- Si elles manquent : les recoller depuis le script livré par la skill.

**Animations et étapes.** Le .pptx contient des fondus et des apparitions au clic, mais Canva ne les reprend pas toujours à l'import : il anime surtout l'arrivée d'une page ou d'un élément, avec peu de contrôle au clic.
- Pour une construction par étapes (liste ligne par ligne, chiffre puis libellé, nom puis prix) : une page par état (dupliquer la page, ajouter l'élément suivant), reliées par la transition Match & Move, sinon par un fondu.
- Animations Canva : garder la plus sobre (fondu). Pas d'effet spectaculaire.

**Marqueurs `[À FOURNIR]`.** L'import perd l'opacité de 40 % qui estompe les libellés : « date » ou « gain » s'afficheraient comme du vrai contenu. Avec `meta.format` à `canva`, le moteur garde donc les crochets à l'écran (`[date]`, `[gain]`). Après l'import, vérifier qu'aucun libellé n'a perdu ses crochets.

**Autres points.**
- Pas de masque de diapositive : chaque page est indépendante.
- Les graphiques natifs peuvent arriver figés ou déformés. Les refaire avec l'outil graphique de Canva, sans graduation si la grammaire n'en veut pas.
- Fichier lourd : compresser les images avant l'import.

## 4. Habillage

- Couleurs : ajouter les HEX du thème dans le kit de marque, ou les saisir dans le sélecteur de couleur.
- Ne pas laisser Canva proposer une palette « assortie » à la place de celle de l'utilisateur.

## 5. Présenter depuis Canva

- Bouton Présenter > Mode présentateur : notes, page suivante, minuteur.
- En visio : partager la fenêtre du public, pas l'écran entier.
- Présenter et enregistrer : utile pour une version vidéo (voir `video.md`).
- Exports : Partager > Télécharger, en PPTX, PDF ou MP4.

## 6. Check-list avant de livrer

- [ ] La liste des outils a été vérifiée ; connecteur utilisé s'il existe, import manuel sinon.
- [ ] Aucun fichier mis en ligne sans l'accord de l'utilisateur.
- [ ] Présentation en 16:9.
- [ ] Polices : celles du design system, ou un remplacement validé par l'utilisateur.
- [ ] Couleurs : les HEX du thème, pas une palette proposée par Canva.
- [ ] Aucun logo, image ou police Apple.
- [ ] Notes présentes sur chaque page qui a un script, avec relais et durée.
- [ ] Étapes reproduites (pages dupliquées), ou listées pour l'utilisateur.
- [ ] Aucun chiffre, prix, date ou témoignage inventé ; les `[À FOURNIR]` restants sont signalés et s'affichent entre crochets.
- [ ] Tutoiement ou vouvoiement constant, comme choisi au départ.
- [ ] Le lien Canva, ou la marche à suivre pour l'import, est remis à l'utilisateur.
