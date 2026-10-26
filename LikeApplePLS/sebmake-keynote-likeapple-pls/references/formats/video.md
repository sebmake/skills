# Format vidéo (MP4 16:9, ou deck HyperFrames)

Toujours 1920 × 1080. Demander d'abord à l'utilisateur ce qu'il veut :
- **A. Une vidéo montée (MP4)** : regardée sans orateur, une scène par slide.
- **B. Un deck HyperFrames navigable** : présenté en direct dans le navigateur, pas de MP4.
- **C. Un Artifact « Motion »** : seulement si la session le propose.
- **D. Un export depuis Keynote, PowerPoint ou Canva** : sans code, avec sa propre voix.

## 1. La voix : le dire clairement

La skill écrit le script. Elle ne produit pas de voix. Trois cas :
- l'utilisateur enregistre sa voix (voie D, ou un fichier audio qu'on place dans la voie A) ;
- un outil de synthèse vocale est présent dans la session (par exemple celui de la skill `media-use` de HyperFrames) et l'utilisateur accepte de l'utiliser. Ne jamais imiter la voix d'une personne réelle ;
- sinon : pas de voix, le script passe en sous-titres.

Fichier de sous-titres (.srt) depuis le champ `notes` de `deck.json` : deux lignes de 42 signes au plus par sous-titre, temps répartis selon la longueur dans la `duree_s` de chaque slide.

```bash
node "$SKILL/scripts/export_script.js" deck.json --srt sortie.srt
```

Relire les coupures. Si la voix réelle est enregistrée, recaler les temps sur elle.

## 2. Voie A : vidéo montée avec HyperFrames

1. Lire la skill `hyperframes` d'abord : c'est le point d'entrée obligatoire. Une vidéo linéaire faite de slides va vers la voie `general-video`, pas vers `slideshow` (qui ne sait pas faire de MP4).
2. HyperFrames pose ses propres questions et écrit un `BRIEF.md`. Lui donner ce que la skill sait déjà (message, public, 16:9, durée, habillage) pour ne pas redemander à l'utilisateur.
3. Mise à jour de la voie, avec l'accord de l'utilisateur : `npx hyperframes skills update general-video`.
4. Correspondance avec `deck.json` :
   - une scène par slide : `data-composition-id` = `id` de la slide, `data-duration` = `duree_s`, `data-width="1920"`, `data-height="1080"` ;
   - `data-start` = somme des durées des scènes précédentes ;
   - les apparitions (`build`) deviennent des entrées minutées dans la scène, au moment où le script (`notes`) les dit ;
   - les couleurs et polices viennent du thème de `deck.json`.
5. Si la voix dure plus que `duree_s`, allonger la scène. Ne pas accélérer la voix.
6. Entre les scènes : fondu court ou raccord, pas de coupe sèche entre deux décors. Pas d'effet spectaculaire. A21 (synthé) devient une incrustation ; A22 à A25 sont des plans à tourner, pas des scènes à inventer.
7. Vérifier puis rendre, après accord de l'utilisateur sur l'aperçu :

```bash
npx hyperframes check
npx hyperframes render --quality draft                       # essais
npx hyperframes render --quality high --output sortie.mp4    # livraison
```

Le rendu MP4 exige **Node 22 ou plus** et **FFmpeg** (`node -v`, `ffmpeg -version`). S'ils manquent, le dire. Un rendu hébergé existe (`npx hyperframes cloud render`), mais il demande un compte : c'est à l'utilisateur de choisir.

## 3. Voie B : deck HyperFrames navigable

1. Lire `hyperframes`, puis `slideshow` et `hyperframes-core`.
2. La skill `slideshow` demande une confirmation oui / non avant d'écrire le deck. Poser la question. Ne pas la sauter.
3. Correspondance avec `deck.json` :
   - une scène par slide (`data-composition-id`, `data-duration` = `duree_s`) ;
   - dans le bloc JSON `application/hyperframes-slideshow+json` : `slides[]` avec `sceneId`, `notes` = script de la slide (relais et durée compris), `fragments` = temps des étapes dans la scène.
4. Valider : `npx hyperframes lint` (0 erreur), puis `npx hyperframes check`.
5. Présenter : `npx hyperframes present <dossier>`, puis bouton Present ou touche P. L'onglet de l'orateur montre les notes, la slide suivante et le chronomètre. En visio : partager l'onglet du public (Meet) ou sa fenêtre (Zoom).
6. Pas de MP4 depuis un deck : `render` ne garde que la première slide, sans prévenir. Pour un MP4, prendre la voie A.

## 4. Voie C : Artifact « Motion »

Seulement si l'outil Artifact de la session liste un type « Motion » (vérifier avec la liste des types, ne pas le supposer). Il fait une animation écrite en code, qu'on peut faire défiler, commenter, et exporter en MP4. Lui donner `deck.json` comme découpage : une scène par slide, durées `duree_s`, script en sous-titres. Pour la voix, mêmes règles qu'à la section 1.

## 5. Voie D : export sans code

À partir du .pptx (`powerpoint.md`) ou du .key (`keynote.md`) :
- **PowerPoint** : Diaporama > Enregistrer (voix et minutage), puis Fichier > Exporter > Créer une vidéo, en 1080p.
- **Keynote** : Lecture > Enregistrer le diaporama (voix), puis Fichier > Exporter vers > Vidéo, en 1080p.
- **Canva** : Présenter et enregistrer, ou Partager > Télécharger en MP4.

L'orateur lit le script des notes. Les étapes posées à la main sont gardées dans la vidéo.

## 6. Check-list avant de livrer

- [ ] La voie a été choisie par l'utilisateur.
- [ ] Vidéo ou deck en 1920 × 1080 (16:9).
- [ ] Une scène par slide ; chaque scène dure au moins `duree_s` ; durée totale annoncée.
- [ ] Voix : enregistrée par l'utilisateur, ou synthèse acceptée par lui, ou sous-titres. C'est dit clairement.
- [ ] Sous-titres relus : coupures, orthographe, pas de texte sur les gros titres.
- [ ] Aucun logo, image, police ou musique Apple ; seulement l'habillage de l'utilisateur.
- [ ] Aucun chiffre, prix, date ou témoignage inventé ; aucun `[À FOURNIR]` à l'image dans un MP4 livré.
- [ ] Tutoiement ou vouvoiement constant, comme choisi au départ.
- [ ] Voie A : `check` passé, aperçu approuvé avant le rendu final. Voie B : `lint` à 0 erreur.
- [ ] Le fichier ou l'URL de présentation est remis à l'utilisateur.
