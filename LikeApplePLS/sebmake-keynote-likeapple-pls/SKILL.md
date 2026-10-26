---
name: sebmake-keynote-likeapple-pls
description: "Builds a 16:9 deck plus the full speaker script on the grammar of Apple keynotes (run of show, announcement sequence, one idea per slide, pacing), in the user's own branding, for Keynote, PowerPoint, Figma Slides, Canva or video. Use it whenever someone wants an Apple-style or keynote-style presentation, deck or pitch, a staged product launch or demo, or a clean deck that hits hard, even if they never say Apple. Not for a plain .pptx export with no staging (that's the pptx skill), nor for Apple-style UI design."
---

# Présentation à la Apple

Cette skill produit une présentation 16:9 et le script qui va avec, construits comme une keynote Apple : un déroulé qui monte en puissance, une séquence d'annonce, une idée par écran, des relais entre intervenants, des récaps emboîtés. Elle reprend la **grammaire** observée sur 8 keynotes (2019-2026), jamais la **marque** : les couleurs, les polices, le produit et les chiffres sont ceux de l'utilisateur.

Tout part d'un seul fichier, `deck.json`. Le contrôle, le .pptx, l'aperçu HTML et le script en sortent. On corrige toujours `deck.json`, jamais le fichier rendu : sinon la correction disparaît au rendu suivant.

```bash
SKILL="<dossier de ce SKILL.md>"   # souvent ~/.claude/skills/sebmake-keynote-likeapple-pls
```

## Étape 1 — Recueil

Relis d'abord la demande et les pièces jointes, et note ce qui est déjà dit. Ne redemande rien de ce que l'utilisateur a déjà donné : il l'a écrit pour ne pas avoir à le répéter.

Pose ensuite les questions manquantes avec l'outil AskUserQuestion s'il existe, sinon en clair, groupées dans un seul message. Pas plus de 4 questions par appel. L'outil n'accepte que 4 choix par question, plus « Autre » : quand la liste est plus longue, propose les 4 plus probables d'après le brief et nomme les autres dans le texte de la question.

**Appel 1 : le cadre.**

| Question | Choix | Pourquoi |
|---|---|---|
| Format de sortie | Keynote, PowerPoint, Figma Slides, Canva, vidéo (vidéo via « Autre », nommée dans le texte ; ou l'inverse si le brief parle de vidéo) | Il décide du rendu. La sortie est toujours en 16:9, quel que soit le format. |
| Habillage | Un lien vers mon design system ; mes couleurs en HEX (et mes polices si j'en ai) | La skill ne connaît pas l'habillage de l'utilisateur. |
| Public | La typologie de client ou de public de `references/publics.md` §1 (B2B décideurs, B2B acheteurs, grand public, investisseurs, partenaires, équipe interne, salon, recrutement, je ne sais pas) | C'est la seule question sur le public : elle décide seule des procédés gardés (graphiques sans graduation, concurrent anonyme, sources, « jusqu'à »…). Ne pose pas de question procédé par procédé. |
| Langue et tutoiement | Français : vous au public, tu entre intervenants ; français : vous partout ; français : tu partout ; anglais | Le tu ou le vous est toujours demandé, jamais supposé. Le cas inverse (tu au public, vous entre intervenants) passe par « Autre ». En anglais, demande à l'appel 2 : ton familier (prénoms) ou formel (prénom, nom, fonction). |

**Appel 2, si ce n'est pas déjà dit** : la durée (5, 10, 20, 30 min ou plus), le contexte (en salle, en visio, vidéo enregistrée), et en anglais le ton familier ou formel.

**Habillage sans lien ni HEX** (réponse « Autre », « je n'en ai pas ») : demande-lui de décrire les couleurs qu'il veut, avec leurs HEX s'il les a. S'il décrit sans HEX (« bleu nuit et orange »), propose des HEX qui correspondent et fais-les valider. Ne choisis jamais une palette sans qu'il l'ait vue.

**Puis le brief, en clair.** Donne ce gabarit à remplir, et dis ce que deviendra ce qui reste vide : les formulations (thèse, problème, description d'une fonction) seront proposées et marquées `[À VALIDER]` ; les chiffres, prix, dates, noms de clients, logos, témoignages et captures resteront `[À FOURNIR]`. L'utilisateur peut ainsi répondre en partie sans tout bloquer. N'y laisse que les lignes encore sans réponse.

```
Habillage : [lien du design system] ou [HEX : fond sombre, fond clair, texte, accent] + [polices titre / texte]
Sujet et but : [de quoi on parle] → [ce que le public doit retenir ou faire en sortant]
Intervenants : [Prénom Nom, fonction], … · Qui ouvre et clôt : [Prénom]
Nouveauté 1 : [nom] · [problème résolu] · [bénéfice en une phrase] · [preuve + source]
              · [ce qu'on peut montrer : démo, capture, vidéo] · [prix] · [date]
Nouveauté 2 : …
Moment fort à garder pour la fin : [lequel]
Matériaux : [captures, photos, logos, vidéos : chemins ou pièces jointes]
```

**Lire l'habillage.** Avec un lien, lis-le avec les outils de la session : Figma (`get_variable_defs`, `get_screenshot`, après la skill Figma que ces outils demandent), Notion (lecture de la page), page web (WebFetch), PDF ou fichier de charte (Read). Extrais les HEX des rôles de `theme` (`fond_sombre`, `fond_clair`, `texte`, `texte_secondaire`, `accent`, `accent2`) et les polices de titre et de texte. Si le lien est illisible (outil absent, accès refusé), dis-le et demande les HEX. Si un rôle manque (pas de fond sombre, par exemple), dérive-le de sa palette et montre-le-lui. Si la charte nomme une police Apple (SF, New York), propose une linéale libre de droits à la place et dis pourquoi. Si elle plafonne la surface d'accent (« jaune ≤ 10 % »), mets `theme.finale_accent` à `false` : sinon la slide finale passe en pleine page d'accent. Une couleur que l'utilisateur n'a pas choisie ne passe jamais en silence.

**Lire le public.** Ouvre `references/publics.md` : le tableau du §3, la fiche du public (§4), et le §5 si le public est mixte ou inconnu.

## Étape 2 — Conducteur

Lis `references/grammaire.md` §1 à §4 et §9. Construis le déroulé à l'échelle de la durée avec la table du §3 : nombre de blocs, d'écrans et de voix, version de la séquence d'annonce (16, 8 ou 6 étapes). Pour une durée entre deux lignes, pars de la ligne la plus proche et ajuste le nombre d'écrans (environ 2 par minute). Choisis la variante d'annonce (§4.3 : produit, fonctionnalité, service, technologie) d'après les nouveautés.

Garde les règles du §1 : la même personne ouvre et clôt, chaque bloc finit par un récap, chaque annonce a un nom et un mini-récap, le plus gros sujet passe en dernier. Ce sont elles qui donnent l'effet « keynote », bien plus que le style des slides. Passe la main tôt (avant 15 à 20 % du temps) et change de voix ou de mode toutes les 3 à 4 minutes.

Montre le conducteur **avant** de produire quoi que ce soit, en un tableau court :

| # | Bloc | Intervenant | Durée | Slides |
|---|---|---|---|---|
| 1 | Ouverture : accueil et thèse | [hôte] | 0:45 | 2 |
| 2 | [Nouveauté 1] (6 étapes) | [hôte] → [expert] | 3:00 | 6 |
| 3 | [Nouveauté 2, le moment fort] (8 étapes) | [expert] → [hôte] | 5:00 | 11 |
| 4 | Récap, dates, clôture | [hôte] | 1:15 | 3 |
| | **Total** | 2 voix, 3 relais | **10:00** | **22** |

Ajoute dessous trois lignes au plus : le réglage retenu pour ce public (sources, graphiques, concurrents, « jusqu'à »), en une phrase, pour qu'il puisse le relâcher ; la palette et les polices retenues ; ce qui manque encore. Attends son accord et ajuste. Changer une ligne du conducteur coûte une minute ; refaire vingt slides coûte bien plus.

## Étape 3 — Design slide par slide

Lis `references/designs.md` : la partie « Choisir un design », puis la fiche de chaque archétype du conducteur. Pour chaque slide, décide :

- **l'archétype et la variante.** L'archétype vient de l'étape d'annonce (`grammaire.md` §4.1, colonne Visuel). La variante vient du contenu et des visuels que l'utilisateur a, ou peut avoir : une capture appelle un appareil, une photo une variante sur image ; sans rien, une variante sans visuel, jamais un cadre vide. La table « Les variantes du moteur » dit ce que chacune demande.
- **le rythme.** Varie les designs d'un bloc à l'autre, et jamais trois fois de suite la même composition (même archétype, même variante). Deux blocs n'ouvrent pas de la même façon.
- **un moment visuel fort par bloc**, au moins : un chiffre géant (A5), un objet ou une interface (A9, A10), le produit seul (A13), le bento (A14), une photo plein cadre (A18) ou une variante à image.
- **le récap d'un logiciel** (plateforme, outil métier en SaaS) : prends l'A14 `fragments-logiciel`. Ses tuiles suivent la démo, chacune porte un composant isolé de la maquette (pas un écran entier), avec au plus une photo d'usage (Unsplash ou Pexels) prise dans le marché du public (`designs.md`, A14, variante g).
- **le visuel à préparer**, d'après le §7 de la fiche : son type, un brief (ce qu'il montre, son cadrage, sa lumière), fond transparent ou non, l'angle, la résolution minimale. Quand tu peux le chercher toi-même, propose-le (`designs.md` §2, règle 7). Dans une maquette, ne t'arrête pas à l'écran : descends jusqu'au composant qui dit la fonction. Pour les photos d'usage ou d'ambiance, tu peux puiser dans Unsplash ou Pexels, en licence gratuite vérifiée, avec l'auteur noté et une photo prise dans le marché du public.

Montre le résultat en un tableau court, à la suite du conducteur validé, une ligne par slide :

| # | Bloc | Design | Ce qu'on voit | Visuel |
|---|---|---|---|---|
| 5 | [Nouveauté 1] | carte-titre sur photo | le nom, en blanc, sur une photo calme du lieu | photo à fournir |
| 6 | [Nouveauté 1] | capture dans un téléphone | l'écran de suivi, de face, seul | capture à fournir |

Livre ensuite la **liste des visuels à préparer** : un brief par visuel, slide par slide (type, ce qu'il montre, format, fond transparent, angle, résolution). L'utilisateur lance ainsi ses captures et ses photos pendant que tu écris le deck. N'attends pas les visuels : tant qu'il en manque un, le moteur dessine un repli neutre, sans chiffre ni logo. Après le contrôle, `export_script.js --visuels` réécrit cette liste d'après `deck.json` : c'est elle que tu livres à la fin.

## Étape 4 — Direction artistique, puis deck.json

**Direction artistique d'abord.** Lis `references/style-visuel.md` avant d'écrire le moindre texte : il montre à quoi ressemble une slide réussie. Vise l'allure d'une keynote :

- des titres très courts et très gros : un mot ou une phrase par écran, jamais un paragraphe ;
- un surtitre d'accent (`textes.surtitre`, 1 à 3 mots) là où il situe le moment, et le point final du titre en accent ;
- les designs de l'étape 3 : la variante de chaque slide, et le moment visuel fort de chaque bloc ;
- quand une capture manque, une interface schématique, que le moteur dessine d'après `image.attendu` ;
- une slide finale forte : un mot, très gros ;
- le même fond pour toutes les slides, celui du reste du deck ; on n'en change qu'entre deux blocs ;
- rien de l'atelier à l'écran ni dans les notes : ni archétype, ni étape, ni consigne.

Lis ensuite `references/deck-spec.md`. Crée un dossier de travail pour la présentation (dans le dossier courant, sauf si l'utilisateur en nomme un autre), avec `deck.json` et un sous-dossier `images/` où tu copies ses matériaux.

Remplis `meta` (titre, langue, `registre` envers le public et `registre_intervenants` entre intervenants, public, `duree_min`, format, `"ratio": "16:9"`, variante d'annonce, et `contexte` : `direct` en salle ou en visio, `preenregistre` en vidéo), `theme` (étape 1) et `intervenants`. Puis, pour chaque slide du conducteur :

- **`archetype`** et **`variante`** : ceux de l'étape 3. Écris toujours la variante : sans elle, le moteur garde un rendu plus simple. Une idée par écran. Pas de slide `AF` : prends l'archétype prévu et remplis-le.
- **`visuel`** : le brief du visuel à préparer, `{type, brief, fond_transparent, angle, resolution_min}`, sur chaque slide qui attend une image (étape 3).
- **`textes`** : 10 mots au plus, recomptés après traduction. Le nom à retenir, seul ; `*mot*` pour l'accent ; `surtitre` pour situer. Un chiffre, un prix ou une date à l'écran vient de l'utilisateur, sinon `[À FOURNIR : libellé]` en 3 mots au plus, et la consigne complète dans `a_fournir`.
- **Brief mince : propose, ne laisse pas de trou.** Rédige des propositions plausibles pour les formulations, la thèse, les problèmes vécus, les descriptions de fonctions et le script, à partir de ce que le brief dit du produit et du public, et marque chacune `[À VALIDER : …]`. À l'écran, elle s'affiche comme du vrai contenu ; dans les notes, elle reste signalée. Jamais de proposition pour un chiffre, un prix, une date, un nom de client, un logo, un témoignage ou une capture réelle : ceux-là restent `[À FOURNIR]`. Une proposition ne contient aucun nombre, même écrit en lettres.
- **`source`** : chaque chiffre porte la sienne. Le moteur l'affiche selon le public (sous le chiffre, en renvoi ou au carton final) ; `meta.affichage_source` ne sert qu'à forcer un autre choix.
- **`notes`** : le script, écrit pour être dit, **en entier** : il doit se lire à voix haute, vers 140 mots par minute, pour la durée visée (environ 1 400 mots pour 10 minutes). Phrases courtes, dans le registre choisi, qui disent ce qui est à l'écran au moment où il apparaît. Prends les gabarits de `grammaire.md` §7 (colonne FR ou EN, variante du registre) et varie-les d'un bloc à l'autre (§8). Chaque passage de parole est un segment `{"intervenant": "…", "type": "relais", "texte": "…"}` : il suit `registre_intervenants`, le reste du script suit `registre`. Un témoignage n'existe que s'il est fourni. Une fonction d'intervenant inconnue reste vide (`role` absent), jamais en marqueur.
- **`build`** : les apparitions dans l'ordre, une phrase par clic, et les indications de scène (silence après le nom, lancer la vidéo, démo). Le moteur en fait des apparitions en fondu, et chaque slide entre par un fondu. Les indications vont là, pas dans le texte à dire, puisque l'orateur lit ses notes.
- **`duree_s`** : compte environ 140 mots par minute, puis ajoute les silences et la durée réelle des démos et des vidéos. Le contrôle alerte au-dessus de 170 mots par minute sur une slide, et sous 110 ou au-dessus de 170 sur tout le deck. La somme doit rester à ±15 % de `duree_min`.
- **`image`** : un chemin relatif à `deck.json`, ou `{"chemin": "images/…", "attendu": "ce que l'image doit montrer"}` si elle manque encore : le moteur dessine une interface schématique à sa place, sans chiffre.

En anglais : `"langue": "en"`, gabarits EN, marqueurs `[TO VALIDATE: …]` et `[TO PROVIDE: …]`, pas de `registre` ; le ton familier ou formel se règle dans les formules de relais (§7.7). Tout ce que l'orateur lit est en anglais, notes comprises.

`assets/exemple-deck.json` montre un deck complet de 16 slides pour 10 minutes (fictif), avec des variantes, des `slide.visuel`, quelques `[À VALIDER]`, un `[À FOURNIR]` court et une image absente : regarde-le pour le niveau de détail du script, des briefs et des marqueurs. N'en reprends pas le contenu.

## Étape 5 — Contrôle

```bash
python3 "$SKILL/scripts/check_deck.py" deck.json --brouillon   # pendant la rédaction
python3 "$SKILL/scripts/check_deck.py" deck.json               # avant de livrer
```

Le contrôle porte les règles du public, du registre, du minutage, du débit du script, du fond, des marqueurs, des 10 mots, des variantes et du rythme des designs. Un deck qui passe tient donc ce que le conducteur a promis. Corrige `deck.json` et relance jusqu'à **zéro erreur bloquante en mode `--brouillon`**. Sa section « À VALIDER » liste les propositions : garde-la pour la livraison.

Sans `--brouillon`, les `[À FOURNIR]` restants bloquent, et c'est voulu : la skill n'invente rien pour les faire disparaître. Redemande-les à l'utilisateur, en une seule liste. S'il ne les a pas, livre en le disant : c'est un brouillon à compléter, pas une version à présenter. Pour chaque avertissement, corrige, ou garde-le en connaissance de cause et dis pourquoi à la livraison.

## Étape 6 — Rendu

Construis toujours le .pptx et l'aperçu. Ils sont le livrable pour PowerPoint, Keynote et Canva, et le contrôle pour Figma Slides et la vidéo.

```bash
[ -d "$SKILL/scripts/node_modules/pptxgenjs" ] || (cd "$SKILL/scripts" && npm install)
node "$SKILL/scripts/build_deck.js" deck.json sortie.pptx --preview apercu.html
```

Lance la commande depuis le dossier de travail. Si `node` manque, dis-le et livre `deck.json` et le script : n'installe rien à la place de l'utilisateur. Le .pptx écrit toujours les polices du thème, même absentes de cette machine : l'aperçu s'affiche alors dans la police de repli, et le moteur le signale en une ligne ; transmets-la (la police est à installer sur la machine qui présente). `--polices repli` écrit la police de repli dans le .pptx, seulement si l'utilisateur le demande. Livre un seul .pptx : pas de second fichier dans la police de repli.

Puis lis **seulement** le fichier du format choisi :

| Format | À lire | Ce que l'utilisateur reçoit |
|---|---|---|
| PowerPoint | `references/formats/powerpoint.md` | le .pptx |
| Keynote | `powerpoint.md` §1, puis `references/formats/keynote.md` | le .pptx à ouvrir dans Keynote ; le .key si Keynote est installé et qu'il est d'accord |
| Canva | `references/formats/canva.md` | le design importé par le connecteur, sinon le .pptx et la marche à suivre |
| Figma Slides | `references/formats/figma-slides.md` | un fichier Figma Slides construit avec `use_figma` (skills `figma-use` et `figma-use-slides` d'abord) ; le .pptx en secours |
| Vidéo | `references/formats/video.md` | selon la voie qu'il choisit (MP4, deck navigable, export) ; la skill écrit le script mais ne produit pas de voix |

## Étape 7 — Contrôle visuel, puis livraison

**Regarde le résultat avant de le donner.** Le contrôle ne voit pas un titre coupé en trois lignes ni un accent illisible sur une photo.

- Ouvre `apercu.html#qa` (chemin absolu en `file://`) avec l'outil de navigateur de la session. Le bandeau du haut dit « Aucun débordement détecté » ou liste les slides qui débordent ; `window.__deckQA()` rend la même liste.
- Fais une capture d'au moins quatre slides : l'ouverture, une slide-chiffre, la plus chargée et la clôture. Vérifie : une idée par écran, des titres gros qui tiennent le centre, un moment visuel par bloc, le même fond partout, aucun cadre vide, aucun mot de l'atelier (archétype, étape, consigne), des `[À FOURNIR]` courts, estompés et soulignés (entre crochets pour Canva), les couleurs du thème, rien qui rappelle Apple.
- Pour Figma Slides, Canva ou la vidéo, regarde aussi le rendu final avec les outils du format (capture Figma, relecture du design, aperçu HyperFrames).
- Sans navigateur, appuie-toi sur la liste « À vérifier » de `build_deck.js` et demande à l'utilisateur d'ouvrir l'aperçu.
- Un texte déborde : coupe des mots dans `deck.json`, puis refais les étapes 5 et 6. Ne réduis pas la taille : un texte qui ne tient pas est un texte trop long.

**Écris le script complet** dans `script.md`, slide par slide, avec intervenants, relais, minutage, apparitions, sources, propositions à valider et ce qui reste à fournir. Ajoute `--visuels visuels.md` pour la liste des visuels à préparer (d'après `slide.visuel` et `image.attendu`), `--etapes` pour la liste des apparitions (le .pptx les contient déjà ; la liste sert à les vérifier, ou à les poser dans Figma Slides et Canva), et `--srt sortie.srt` pour des sous-titres :

```bash
node "$SKILL/scripts/export_script.js" deck.json --md script.md --visuels visuels.md --etapes
```

**Livre** en un message court :

1. le fichier (chemin ou lien) et, en une ligne, comment l'ouvrir ;
2. `script.md`, le script complet (il est aussi dans les notes de chaque slide) ;
3. **à valider** : les propositions `[À VALIDER]`, slide par slide (section « À VALIDER » du contrôle), à accepter ou à corriger une à une ;
4. **à fournir** : les `[À FOURNIR]` restants et leur consigne, les images à fournir et les fonctions d'intervenants inconnues, slide par slide (lignes « Reste à fournir » et « Image à fournir » du contrôle sans `--brouillon`), ou « aucun » ;
5. **les visuels à préparer** : `visuels.md`, un brief par visuel, slide par slide, ou « aucun » ;
6. ce qui reste à faire à la main : les morphings et les apparitions hors de l'ordre de lecture (le moteur pose les fondus), les polices à installer, et le réglage du public rappelé en une phrase.

## Rappels

- **Aucun chiffre, prix, date, nom de client, logo, témoignage ou capture inventé**, pas même dans une interface schématique (des barres grises, pas des nombres). Un seul chiffre faux suffit à ruiner la confiance, et un chiffre invérifiable peut être jugé trompeur. Ce qui manque reste visible : `[À FOURNIR : libellé]`. Ce qui se rédige se propose : `[À VALIDER : …]`.
- **La grammaire, jamais la marque.** Aucun logo, aucune police (SF, New York), aucune image, aucun appareil, aucun slogan d'Apple. L'utilisateur présente son produit, avec son identité.
- **Aucune citation de keynote Apple**, ni de formule-signature. Les gabarits à [cases] de `grammaire.md` suffisent, et le script s'écrit dans les mots de l'utilisateur.
- **Des sources visibles quand le public l'exige.** Le corpus ne source rien parce qu'il vise le grand public d'une marque très connue. Devant des investisseurs, des acheteurs ou un public inconnu, la même pratique fait perdre la confiance : suis `publics.md`.
- **Toujours 16:9**, quel que soit le format.

## Fichiers de référence : quand les lire

| Fichier | Quand |
|---|---|
| `references/grammaire.md` | À chaque usage. §1 à §4 et §9 pour le conducteur (étape 2) ; §4.1 et §6 pour le design (étape 3) ; la direction artistique et §5 à §8 pendant la rédaction (étape 4). |
| `references/designs.md` | À l'étape 3 : « Choisir un design », puis la fiche de chaque archétype du conducteur (variantes, contenu visuel, profondeur, brief du visuel et repli). À l'étape 4 pour écrire `slide.variante` et `slide.visuel`. |
| `references/style-visuel.md` | À l'étape 4, avant d'écrire les textes : les mesures du texte, que le moteur suit. |
| `references/publics.md` | Dès la réponse sur le public (étape 1), puis pour régler sources, graphiques et concurrents. |
| `references/deck-spec.md` | Avant d'écrire `deck.json` (étape 4), et pour comprendre une erreur du contrôle. |
| `references/formats/<format>.md` | À l'étape 6, seulement celui du format choisi (plus `powerpoint.md` §1 pour Keynote et Canva). |
| `references/data/archetypes.json` | Quand un archétype pose question : éléments, règle de mise en page. Les variantes que le moteur dessine sont dans `designs.md`. |
| `references/data/annonce.json` | Pour le détail d'une étape d'annonce ou d'une variante. |
| `references/data/formules.json` | Pour varier les formules au-delà de `grammaire.md` §7 (gabarits EN et FR). |
| `references/data/runofshow.json` | Pour des proportions exactes de déroulé (les 8 keynotes, segment par segment). |
| `references/data/lexique.json` | Rarement : fréquence des mots du corpus anglais, pour doser un adjectif. |
| `references/data/publics-exigences.json` | Version machine de `publics.md`, lue par les scripts. À lire seulement pour comprendre une alerte. |
| `references/analyses/S1` à `S4` | Archives de l'analyse, seulement en cas de doute sur un compte. Elles contiennent des extraits de keynotes : n'en recopie rien. |
| `assets/exemple-deck.json` | Exemple fictif complet, pour le niveau de détail du script, des variantes, des briefs de visuels et des marqueurs. |
| `scripts/check_deck.py`, `scripts/build_deck.js`, `scripts/export_script.js` | Contrôle (Python 3.9 et plus, sans dépendance), rendu .pptx et aperçu (Node 18 et plus, pptxgenjs), script, visuels à préparer, apparitions et sous-titres (Node, sans dépendance). |
