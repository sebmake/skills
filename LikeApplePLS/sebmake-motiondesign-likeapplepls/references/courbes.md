# Courbes mesurées

Ce fichier donne toutes les courbes du moteur : leur forme (`cubic-bezier`), leur traduction en clés After Effects (`KeyframeEase`), et l'usage où elles ont été retenues, avec les comptes. Le moteur (`scripts/motion_lib.mjs`) porte la même table, sous les mêmes noms : c'est le nom qu'on écrit dans `motion.json` quand on force une courbe.

Lis d'abord `principes.md` § P2 : la courbe dépend du **rôle** du mouvement, pas de l'objet.

---

## 1. Lire une courbe

Une courbe dit comment la valeur avance entre deux clés. `cubic-bezier(x1, y1, x2, y2)` : le temps va de 0 à 1 sur l'axe x, la progression de 0 à 1 sur l'axe y. `(x1, y1)` est la poignée de départ, `(x2, y2)` celle d'arrivée.

- **Linéaire** `(0, 0, 1, 1)` : vitesse constante.
- **Famille « out »** (`y1` = 1, ou proche) : part vite, freine, se pose. C'est l'arrivée.
- **Famille « in »** (`y2` = 0, ou proche) : part doucement, accélère. C'est un départ, ou une lumière qui monte vers le noir.
- **Courbe en S** (`in-out`) : part doucement, finit doucement.
- **Dépassement** : une valeur de `y` au-dessus de 1. La valeur passe sa cible puis revient.

Quatre rôles, quatre familles (comptes dans `principes.md` § P2) :

| rôle | famille | courbes du moteur |
|---|---|---|
| le montage passe d'une image à l'autre | linéaire | `lineaire` |
| un mouvement traverse le plan | linéaire | `lineaire` |
| un élément arrive et se pose | « out » ou S | `easeOutExpo`, `out-cubic`, `out-expo`, `ease`, `montage-2024`, `zoom-2024`, `glissade`, `rangee-2024`, `poussee-ecran`… |
| quelque chose s'allume ou s'éteint | « in » ou S | `easeInOutCubic`, `in-sine`, `in-out-cubic`, `in-out-sine`, `voile`, `ease-in-out`… |

---

## 2. Traduire une courbe en clés After Effects

Pour une propriété animée de `v0` (au temps `t0`) à `v1` (au temps `t1`), avec `T = t1 − t0` et la vitesse moyenne `m = (v1 − v0) / T` :

| clé | côté | influence | vitesse |
|---|---|---|---|
| clé de départ | ease **sortant** | `x1 × 100` | `(y1 / x1) × m` |
| clé d'arrivée | ease **entrant** | `(1 − x2) × 100` | `((1 − y2) / (1 − x2)) × m` |

```js
prop.setTemporalEaseAtKey(k0, [easeEntrantDeK0], [new KeyframeEase(vitesseSortie, influenceSortie)]);
prop.setTemporalEaseAtKey(k1, [new KeyframeEase(vitesseEntree, influenceEntree)], [easeSortantDeK1]);
```

**Cas particuliers.**
- **Linéaire** : pas de `KeyframeEase`. Les deux clés en `KeyframeInterpolationType.LINEAR`.
- **Poignée nulle** (`x1 = y1 = 0`, ou `x2 = y2 = 1`) : influence 0,1 (le minimum) et la pente de l'autre poignée. C'est le cas de `ease-out` et `ease-in`.
- **Influence** : entre 0,1 et 100.
- **Signe** : la vitesse suit le sens de la variation. Elle est négative quand la valeur baisse (une échelle de 400 % à 100 %, une position qui remonte).
- **Dépassement** : la vitesse d'entrée devient négative (`easeOutBack`). After Effects et EffectCraft l'acceptent.
- **Échelle** (3 dimensions liées) : un tableau de 3 `KeyframeEase`, un par dimension, chacun avec la vitesse de sa dimension.
- **Position** : séparer les dimensions (`dimensionsSeparated = true`) et animer `ADBE Position_0` (X) et `ADBE Position_1` (Y), qui sont à une dimension. Une position liée attend un seul `KeyframeEase` dont la vitesse est la longueur du trajet ; c'est plus fragile. Le moteur sépare toujours.
- **Clé tenue** (un saut net, sans courbe) : `KeyframeInterpolationType.HOLD` sur la clé.

**Vérifié dans EffectCraft le 21/10** : l'écart entre la progression rendue et la `cubic-bezier` est de 0,0002 au plus, sur 7 courbes (dont `montage-2024` et un dépassement à vitesse négative), en opacité, position Y séparée et échelle. Dans EffectCraft, la composition doit être ouverte dans la visionneuse (`comp.openInViewer()`) **avant** de poser les eases, sinon ils sont ignorés. Le moteur le fait. After Effects n'est pas installé ici : la formule est celle de son modèle de clés, le résultat n'y a pas été rendu.

---

## 3. La table

« Sortie » = clé de départ, « entrée » = clé d'arrivée : influence en %, vitesse en multiple de la vitesse moyenne `m`. « Part 10–90 » : la part de `T` pendant laquelle la valeur va de 10 % à 90 % ; « part visible » : de 2 % à 98 %. Elles servent à passer d'une durée mesurée à l'écart des clés (§ 5).

### 3.1 Linéaire et CSS

| nom | cubic-bezier | sortie | entrée | part 10–90 | part visible | retenue pour |
|---|---|---|---|---:|---:|---|
| `lineaire` | 0, 0, 1, 1 | LINEAR | LINEAR | 0,80 | 0,96 | fondus au noir 21 sur 21 ; avancées de caméra 7 sur 11 ; pivots 4 sur 5 ; parallaxes 8 sur 13 ; filets de lumière (r² 0,91) |
| `ease` | 0.25, 0.1, 0.25, 1 | 25 ; 0,4 × | 75 ; 0 × | 0,52 | 0,78 | nom qui remonte au-dessus d'un prix 3 sur 5 ; zoom arrière d'une phrase 2 sur 2 ; titre en fondu lent 2 sur 5 ; panneau qui glisse dans la page (1 cas) |
| `ease-in` | 0.42, 0, 1, 1 | 42 ; 0 × | 0,1 ; 1,72 × | 0,68 | 0,88 | pivot qui accélère (variante) ; extinction |
| `ease-out` | 0, 0, 0.58, 1 | 0,1 ; 1,72 × | 42 ; 0 × | 0,68 | 0,88 | reculs 4 sur 6 (courbe groupée) ; ouverture d'un éclaté 5 sur 7 ; opacité du chiffre de 2020 4 sur 6 |
| `ease-in-out` | 0.42, 0, 0.58, 1 | 42 ; 0 × | 42 ; 0 × | 0,56 | 0,80 | opacité du chiffre posé (ajustement commun, 18 chiffres) ; voile d'interface |

### 3.2 Table de l'analyse « texte » (noms en camelCase)

| nom | cubic-bezier | sortie | entrée | part 10–90 | part visible | retenue pour |
|---|---|---|---|---:|---:|---|
| `easeInOutCubic` | 0.645, 0.045, 0.355, 1 | 64,5 ; 0,07 × | 64,5 ; 0 × | 0,44 | 0,74 | opacité des titres « fondu + montée » 4 sur 4 ; lignes de cascade 11 sur 13 |
| `easeOutExpo` | 0.19, 1, 0.22, 1 | 19 ; 5,26 × | 78 ; 0 × | 0,29 | 0,51 | montée des titres 4 sur 4 ; échelle du chiffre posé 11 sur 18 |
| `easeInOutQuart` | 0.77, 0, 0.175, 1 | 77 ; 0 × | 82,5 ; 0 × | 0,34 | 0,65 | montée des lignes de cascade (0,10 s), 4 lignes sur 11 ; nouvelle ligne au fil de la voix |
| `easeInOutQuint` | 0.86, 0, 0.07, 1 | 86 ; 0 × | 93 ; 0 × | 0,29 | 0,62 | montée des lignes de cascade (0,10 s), 7 lignes sur 11 ; cascade rapide (0,05 s) |
| `easeInQuad` | 0.55, 0.085, 0.68, 0.53 | 55 ; 0,15 × | 32 ; 1,47 × | 0,63 | 0,89 | chute depuis le haut 5 sur 6 (phrases et chiffres de 2020) |
| `easeOutQuart` | 0.165, 0.84, 0.44, 1 | 16,5 ; 5,09 × | 56 ; 0 × | 0,45 | 0,71 | lignes qui entrent par le bas (juin 2020), ajustement commun |
| `easeOutBack` | 0.175, 0.885, 0.32, 1.275 | 17,5 ; 5,06 × | 68 ; −0,40 × | 0,26 | 0,35 | chiffre qui grandit en 2020, 6 sur 6 (dépassement +5 %) |
| `easeInOutSine` | 0.445, 0.05, 0.55, 0.95 | 44,5 ; 0,11 × | 45 ; 0,11 × | 0,57 | 0,83 | nouveau mot dans un fondu enchaîné (1 cas) |
| `easeInCubic` | 0.55, 0.055, 0.675, 0.19 | 55 ; 0,10 × | 32,5 ; 2,49 × | 0,54 | 0,84 | mot qui glisse (1 cas) ; cascade rapide de 2024, 7 lignes sur 7 |
| `easeOutCubic` | 0.215, 0.61, 0.355, 1 | 21,5 ; 2,84 × | 64,5 ; 0 × | 0,51 | 0,76 | recentrage d'une ligne qui se construit (**convention**) |

### 3.3 Table des analyses « objets », « interfaces », « transitions » (noms en kebab)

| nom | cubic-bezier | sortie | entrée | part 10–90 | part visible | retenue pour |
|---|---|---|---|---:|---:|---|
| `out-cubic` | 0.33, 1, 0.68, 1 | 33 ; 3,03 × | 32 ; 0 × | 0,51 | 0,73 | entrée latérale floue d'un produit 8 sur 8 (courbe groupée, erreur 0,075) ; caméra qui se pose |
| `out-quad` | 0.5, 1, 0.89, 1 | 50 ; 2 × | 11 ; 0 × | 0,63 | 0,84 | logo de fin qui s'allume (3 fondus « out » sur 10) ; recul qui se pose |
| `out-quint` | 0.22, 1, 0.36, 1 | 22 ; 4,55 × | 64 ; 0 × | 0,35 | 0,57 | défilement par geste (variante) |
| `out-expo` | 0.16, 1, 0.3, 1 | 16 ; 6,25 × | 70 ; 0 × | 0,31 | 0,54 | panneau qui arrive d'un bord (1 sur 4 mesurés) ; fond qui se floute (fin en douceur 8 sur 14) |
| `out-sine` | 0.61, 1, 0.88, 1 | 61 ; 1,64 × | 12 ; 0 × | 0,66 | 0,85 | signe final qui apparaît (1 cas) |
| `out-back` | 0.34, 1.56, 0.64, 1 | 34 ; 4,59 × | 36 ; 0 × | 0,27 | 0,35 | carte qui monte avec dépassement de 6 % (1 panneau sur 4) |
| `in-quad` | 0.11, 0, 0.5, 0 | 11 ; 0 × | 50 ; 2 × | 0,63 | 0,84 | révélation et extinction qui accélèrent (variante) |
| `in-sine` | 0.12, 0, 0.39, 0 | 12 ; 0 × | 61 ; 1,64 × | 0,66 | 0,85 | image qui monte du noir après une coupe (2 keynotes) |
| `in-out-sine` | 0.37, 0, 0.63, 1 | 37 ; 0 × | 37 ; 0 × | 0,59 | 0,82 | bascule de lumière lente 2 sur 4 ; effacement d'un logo |
| `in-out-cubic` | 0.65, 0, 0.35, 1 | 65 ; 0 × | 65 ; 0 × | 0,43 | 0,71 | image qui monte du noir 4 sur 14 |
| `in-out-quart` | 0.76, 0, 0.24, 1 | 76 ; 0 × | 76 ; 0 × | 0,36 | 0,67 | bascule de lumière lente (1 cas) |

**Deux noms proches, deux courbes.** `easeOutExpo` (0.19, 1, 0.22, 1) et `out-expo` (0.16, 1, 0.3, 1) ne sont pas la même courbe ; de même `easeOutCubic` et `out-cubic`, `easeInOutCubic` et `in-out-cubic`. Les analyses n'ont pas ajusté les mêmes tables. Garde la courbe que la recette donne : c'est celle qui a été retenue sur ses instances.

### 3.4 Courbes de famille (ajustées en commun sur toutes les instances d'une famille)

Ce sont les plus sûres : une seule courbe colle à des dizaines d'instances.

| nom | cubic-bezier | sortie | entrée | part 10–90 | part visible | retenue pour |
|---|---|---|---|---:|---:|---|
| `montage-2020` | 0.36, 0, 0.25, 1 | 36 ; 0 × | 75 ; 0 × | 0,48 | 0,75 | zooms, glissades et rangées de 2019-2020 : 21 instances, erreur 0,018 |
| `montage-2024` | 0.6, 0.4, 0.17, 0.95 | 60 ; 0,67 × | 83 ; 0,06 × | 0,48 | 0,80 | zooms, glissades et rangées de 2024-2026 : 56 instances, erreur 0,026 |
| `zoom-2024` | 0.56, 0.32, 0.19, 0.98 | 56 ; 0,57 × | 81 ; 0,02 × | 0,47 | 0,78 | zoom dans un détail, 2024-2026 : 18 instances, erreur 0,028 |
| `zoom-sortie` | 0.64, 0.47, 0.15, 0.94 | 64 ; 0,73 × | 85 ; 0,07 × | 0,48 | 0,81 | zoom qui ressort du détail : 10 instances, erreur 0,019 |
| `rangee-2024` | 0.67, 0.49, 0.09, 0.88 | 67 ; 0,73 × | 91 ; 0,13 × | 0,49 | 0,85 | écrans qui s'empilent, 2024-2026 : 14 instances, erreur 0,014 |
| `glissade` | 0.65, 0.5, 0.15, 0.93 | 65 ; 0,77 × | 85 ; 0,08 × | 0,48 | 0,81 | plan entier qui glisse vers le suivant : 16 instances, erreur 0,030 |
| `poussee-ecran` | 0.43, 0.08, 0.21, 1 | 43 ; 0,19 × | 79 ; 0 × | 0,46 | 0,75 | un contenu en pousse un autre, cadre fixe : 7 instances, erreur 0,019 |
| `voile` | 0.44, 0.21, 0.29, 1 | 44 ; 0,48 × | 71 ; 0 × | 0,50 | 0,78 | fond qui s'assombrit : 18 instances, erreur 0,021 |
| `voile-2024` | 0.52, 0.42, 0.34, 1 | 52 ; 0,81 × | 66 ; 0 × | 0,53 | 0,79 | fond qui s'assombrit, 2024-2026 : 9 instances, erreur 0,021 |
| `defilement` | 0.36, 0, 0.25, 1 | 36 ; 0 × | 75 ; 0 × | 0,48 | 0,75 | défilement : 27 instances, erreur 0,033 |
| `defilement-2024` | 0.39, 0.06, 0.25, 1 | 39 ; 0,15 × | 75 ; 0 × | 0,48 | 0,76 | défilement de présentation, 2024-2026 : 12 instances, erreur 0,020 |
| `geste` | 0.43, 0, 0.06, 0.82 | 43 ; 0 × | 94 ; 0,19 × | 0,51 | 0,81 | défilement lancé d'un coup de doigt : 4 instances, erreur 0,019 |

**La courbe de 2024-2026** (`montage-2024`) part déjà lancée : la vitesse culmine à 39 % de `T`, à 3 fois la vitesse moyenne, puis une longue traîne. Celle de 2019-2020 (`montage-2020`) part et finit à vitesse nulle ; son pic est à 30 % de `T`, à 2,4 fois la moyenne. **Convention** : une époque pour tout le film (`principes.md` § P12).

---

## 4. Quelle courbe pour quel geste

Les recettes du moteur choisissent la courbe. Ce tableau sert à relire un plan d'animation ou à écrire un geste hors recette.

| geste | propriété | courbe | durée (clé à clé) | comptes |
|---|---|---|---|---|
| fondu au noir, fondu depuis le noir court | opacité d'un solide noir | `lineaire` | 0,50 s | 21 sur 21 ; 11 sur 16 |
| image qui monte du noir après une coupe | opacité | `in-sine` ou `in-out-cubic` | 10–90 en 0,39 s | départ doux 13 sur 14 |
| fondu enchaîné | opacité | `lineaire` (aucune courbe dominante) | 0,54 s | 25 vérifiés |
| titre qui fond et monte | opacité ; position Y | `easeInOutCubic` ; `easeOutExpo` | 0,77 s ; 0,92 s, départ 0,30 s plus tard | 4 sur 4 |
| ligne de liste en cascade | opacité ; position Y | `easeInOutCubic` ; `easeInOutQuint` | 1,14 s ; 1,17 s, parties ensemble | 11 sur 13 ; 7 sur 11 |
| chiffre qui se pose | échelle (et flou) ; opacité | `easeOutExpo` ; `ease-in-out` | 0,67 s ; 0,36 s | 11 sur 18 ; ajustement commun |
| carton de film, nom de fin | opacité | `lineaire` (carton) ; `out-quad` (nom) | 0,56 s ; 10–90 en 0,65 s | 3 sur 7 ; 3 fondus « out » sur 10 |
| produit qui entre de côté | position X | `out-cubic` | 0,9 s, sur la coupe | 8 sur 8 |
| avancée de caméra | échelle d'un nul parent | `lineaire` | tout le plan | 7 sur 11 |
| recul de caméra | échelle d'un nul parent | `ease-out` | 5,8 s | 4 sur 6 |
| caméra qui se pose dans le plan | échelle, position | `out-cubic` | 10–90 en 4,4 s | arrivée à vitesse nulle 7 sur 7 |
| pivot du profil à la face | rotation Y (ou largeur) | `lineaire` | 2 s | 4 sur 5 |
| filet de lumière | position de la bande | `lineaire` | 0,28 s | front rectiligne, r² 0,91 |
| sortie du noir d'un objet | opacité d'un voile, exposition | `lineaire` | 10–90 en 1,6 s | linéaire ou qui accélère 8 sur 12 |
| éclaté qui s'ouvre ; qui se pose | position des pièces | `ease-out` ; `lineaire` | 1,9 s ; 1,2 s | 5 sur 7 ; 3 poses sur 3 |
| zoom dans un détail d'écran | échelle et position, même courbe | `zoom-2024` (ou `montage-2020`) | 0,95 s | 18 ; 9 instances |
| glissade d'un écran au suivant | position X des deux plans | `glissade` | 0,89 s | 16 instances |
| écran qui rejoint une rangée | position X de la rangée | `rangee-2024` (ou `montage-2020`) | 0,79 s (0,96 s) | 14 ; 5 instances |
| défilement | position Y du contenu | `defilement-2024` ; `geste` ; `lineaire` (continu) | 1,07 s ; 2,16 s | 12 ; 4 ; 1 instance |
| panneau qui arrive | position | `out-expo` (d'un bord) ; `ease` (dans la page) | 0,36 s visibles | 4 courbes mesurées |
| voile sombre autour d'un élément | opacité d'un solide noir | `voile` (ou `voile-2024`) | 0,53 s | 18 instances |
| fond qui se floute | flou gaussien | `out-expo` | même début et même durée que le voile | fin en douceur 8 sur 14 |
| bascule de lumière lente | opacité d'un voile | `in-out-sine` | 2,4 s | 4 sur 4 adoucies |

---

## 5. D'une durée mesurée à l'écart des clés

Les analyses donnent trois durées : 10–90, visible (2–98) et clé à clé (`T`). Dans le script, on pose `T`. Pour passer de l'une à l'autre :

`T = durée 10–90 ÷ part 10–90` ; `T = durée visible ÷ part visible`.

Exemples :
- Un fondu `easeInOutCubic` de 0,34 s entre 10 et 90 % : `T = 0,34 / 0,44 = 0,77 s`.
- Un panneau `out-expo` visible 0,36 s : `T = 0,36 / 0,54 = 0,67 s`. La fin de la courbe est une longue traîne presque immobile.
- Un fondu au noir `lineaire` de 0,40 s entre 10 et 90 % : `T = 0,40 / 0,80 = 0,50 s`.

Le moteur fait ce calcul (`T_depuis` dans `motion_lib.mjs`) : dans `motion.json`, chaque paramètre porte son unité et dit s'il est une durée 10–90 (`d1090…`), visible (`visible`) ou clé à clé (`T…`).

**À l'image près.** Les clés sont ramenées à l'image. Deux clés à moins d'une image fusionnent. À 30 images par seconde, le plus court mouvement mesuré (un filet de lumière de 0,10 s) fait 3 images : il passe. Un panneau de 0,17 s n'a que 5 images : la forme de sa courbe ne se voit plus.

---

## 6. Dépassement

Par défaut, aucune clé ne dépasse sa valeur finale (`principes.md` § P7). Trois exceptions mesurées existent, chacune limitée :

| geste | dépassement | comment le poser |
|---|---|---|
| chiffre qui grandit (manière 2019-2020) | +5 % d'échelle, 6 sur 6 | `easeOutBack`, deux clés, vitesse d'entrée négative ; ou **convention** : trois clés, 20 % → 105 % à 0,6 s (`easeOutCubic`) → 100 % à 1,3 s (`easeInOutSine`) |
| carte qui monte | +6 %, 1 panneau sur 4 | `out-back`, deux clés |
| éclat d'une puce qui s'allume | +11 à +28 % de luminance, 3 sur 12 | trois clés (**convention** appuyée sur 3 cas) : 0 → 115 à 130 % de la valeur finale en 0,5 à 0,7 s, puis retour à 100 % en 0,6 s |

Les deux manières (vitesse négative ou troisième clé) marchent dans les deux outils. La troisième clé se relit plus facilement dans l'éditeur de graphes.

---

## 7. Écrire une courbe à la main (ES3)

Le script produit par le moteur contient déjà ces fonctions (`md_anime`, `md_ease`, `md_saut`). Pour un geste hors recette, dans un script écrit à la main, voici l'équivalent minimal. Il reste en ES3 : `var`, `function`, ni `let`, ni `const`, ni fonction fléchée, ni gabarit, ni `JSON`.

```js
// Pose (t0, v0) -> (t1, v1) sur une propriété à une dimension, avec la courbe b = [x1, y1, x2, y2].
// b = null : linéaire. Temps ramenés à l'image de la composition.
function poserCourbe(comp, prop, t0, v0, t1, v1, b) {
    var fd = comp.frameDuration;
    t0 = Math.round(t0 / fd) * fd; t1 = Math.round(t1 / fd) * fd;
    if (t1 < t0 + fd) t1 = t0 + fd;                      // au moins une image d'écart
    prop.setValueAtTime(t0, v0); prop.setValueAtTime(t1, v1);
    var k0 = prop.nearestKeyIndex(t0), k1 = prop.nearestKeyIndex(t1);
    var KI = KeyframeInterpolationType;
    if (!b) {
        prop.setInterpolationTypeAtKey(k0, KI.LINEAR, KI.LINEAR);
        prop.setInterpolationTypeAtKey(k1, KI.LINEAR, KI.LINEAR);
        return;
    }
    var m = (v1 - v0) / (t1 - t0);
    var x1 = b[0], y1 = b[1], x2 = b[2], y2 = b[3], inS, peS, inE, peE;
    if (x1 <= 0.000001 && y1 <= 0.000001) { inS = 0.1; peS = y2 / x2; } else { inS = x1 * 100; peS = y1 / x1; }
    if (x2 >= 0.999999 && y2 >= 0.999999) { inE = 0.1; peE = (1 - y1) / (1 - x1); } else { inE = (1 - x2) * 100; peE = (1 - y2) / (1 - x2); }
    var neutre = new KeyframeEase(0, 33.333);
    prop.setInterpolationTypeAtKey(k0, KI.BEZIER, KI.BEZIER);
    prop.setInterpolationTypeAtKey(k1, KI.BEZIER, KI.BEZIER);
    prop.setTemporalEaseAtKey(k0, [neutre], [new KeyframeEase(peS * m, Math.max(0.1, Math.min(100, inS)))]);
    prop.setTemporalEaseAtKey(k1, [new KeyframeEase(peE * m, Math.max(0.1, Math.min(100, inE)))], [neutre]);
}

// Exemple : un titre fond (easeInOutCubic, 0,77 s) puis monte de 15,3 % H (easeOutExpo, 0,92 s, 0,30 s plus tard).
// var tg = titre.property("ADBE Transform Group");
// tg.property("ADBE Position").dimensionsSeparated = true;
// poserCourbe(comp, tg.property("ADBE Opacity"), 1.0, 0, 1.77, 100, [0.645, 0.045, 0.355, 1]);
// poserCourbe(comp, tg.property("ADBE Position_1"), 1.30, 540 + 0.153 * 1080, 2.22, 540, [0.19, 1, 0.22, 1]);
```

Cette version écrase l'ease des côtés extérieurs (`neutre`). Pour enchaîner plusieurs segments sur la même propriété, garde l'ease existant de ces côtés, comme le fait `md_anime` (fonction `md_garde`).

Pour l'échelle, passe un tableau de 3 `KeyframeEase` (un par dimension) au lieu d'un seul.

---

## 8. Pièges

- **Courbe ignorée dans EffectCraft** : la composition n'était pas ouverte dans la visionneuse. Appelle `comp.openInViewer()` avant de poser les eases.
- **Deux clés fusionnent** : elles tombent sur la même image. Garde au moins une image d'écart ; un fondu de 10 images ou plus montre sa courbe.
- **Le mouvement part dans le mauvais sens ou dépasse** : la vitesse n'a pas le signe de la variation. Elle vaut `pente × (v1 − v0) / T`, avec le signe de `v1 − v0`.
- **Le dépassement disparaît** : l'influence a été bornée à 100, ou la vitesse négative a été remise à 0 par une autre fonction. Relis la clé dans l'éditeur de graphes.
- **Position liée** : la vitesse d'un `KeyframeEase` spatial est une longueur de trajet, pas un écart en X ou en Y. Sépare les dimensions.
- **Échelle** : 3 eases, pas 1. Sinon l'appel lève une erreur.
- **Ne pas reconstruire une courbe d'après un nom** : `easeOutExpo` et `out-expo` diffèrent (§ 3.3). Prends la bezier de la table.
