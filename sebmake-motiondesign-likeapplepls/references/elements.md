# What to animate, and how: element by element

For each element type: **what** to animate (which property), **how** (the engine recipe, its duration, curve, amplitude and offset), **when** (its place in the sequence) and **what not to do**. Recipe names are the engine's (`scripts/motion_lib.mjs`; full list: `node scripts/build_motion.mjs --liste`). How to write them in `motion.json` is in `motion-spec.md`.

Contents:
0. Reading a guide · 1. Choosing fast · 2. Title · 3. Sentence · 4. Kicker · 5. List · 6. Word that changes · 7. Number · 8. Film card · 9. Logo and end name · 10. Product image · 11. Interface screenshot · 12. Icon · 13. Shape · 14. Background · 15. Camera · 16. Going from one shot to the next · 17. Building a sequence

---

## 0. Reading a guide

- **Unit**: `u` = 1% of the short side of the frame. In 16:9, that is 1% of the height (the "% H" of the analyses): 1 u = 10.8 px in 1080p.
- **Durations**: "T" = from one key to the next; "10–90" = from 10% to 90% of the move; "visible" = from 2% to 98%. The engine converts (`courbes.md` § 5).
- **Range**: each setting has a default (the measured median) and a range (the corpus). A **measured** setting outside its range is an error at check time. A **convention** setting may change; the checker flags it.
- **Era**: `2024-2026` (default) or `2019-2020`. A recipe tagged with an era belongs only to it; "toutes" (all) fits everywhere (`principes.md` § P12).
- **Major**: the recipe moves the element visibly. Two major moves don't overlap (`principes.md` § P5), except in a cascade.
- **Exit**: a cut by default (`"sortie": "coupe"`). The only other choice is a slow linear fade of 1.15 s (`"sortie": "fondu"`), seen on 2 titles. Never an exit that moves (0 out of 18).

---

## 1. Choosing fast

| element | `type` | default (2024-2026) | other recipes | never |
|---|---|---|---|---|
| title, name alone | `titre` | `coupe`, or `titre-fondu-montee` if it must be noticed | `titre-fondu`, `titre-balayage`, `carton-fondu`; 2019-2020: `phrase-zoom-arriere`, `chute` | slide from the side, rotate, letter by letter, bounce |
| sentence | `phrase` | `coupe` | `titre-fondu-montee`, `carton-fondu`, `carton-groupes`; 2019-2020: `phrase-zoom-arriere`, `chute`, `phrase-par-le-bas` | word by word, slide from the side |
| kicker | `surtitre` | `avec` (its word) | `coupe` | animate alone, before its word |
| list | `liste` | `liste-cascade` | `liste-cascade-rapide`, `liste-au-fil`; 2019-2020: `liste-par-le-bas` | lines from the side, bottom to top |
| word that changes | `titre`, `phrase` | `mot-remplace` | `mot-fondu-enchaine`; 2019-2020: `mot-glisse` | letter morphing, rolling |
| hero number | `chiffre` | `chiffre-pose` | `nom-remonte` (price); 2019-2020: `chiffre-croissance`, `chute` | counting, fading in place |
| film card | `titre`, `phrase` | `carton-fondu` | `carton-groupes`, `coupe` | rising, zooming |
| logo, end name | `logo` | `logo-fin` | `coupe` | sliding, rising |
| product image | `image` | `coupe` then `camera-poussee` | `produit-entree`, `produit-pivot`, `eclate`, `revelation-lumiere`, `balayage-lumiere`, `produit-recul`, `produit-rotation`, `produit-flotte` | floating in a loop, full turn, bounce |
| interface screenshot | `capture` | `coupe` then `zoom-detail` | `panneau-pose`, `defilement`, `empilement`, `assombrir-autour` | linear zoom, vertical slide, two arrivals together |
| icon | `icone` | `avec` (its word) or `coupe` | `assombrir-autour` (in a grid), `produit-entree`, `revelation-lumiere` | rotate, bounce |
| shape | `forme` | `coupe` | `panneau-pose`, `eclate`, `balayage-lumiere`, `revelation-lumiere` | animated box behind a text |
| background | `fond` | `coupe` | transitions `bascule-lumiere`, `passage-noir`, `montee-du-noir`; `assombrir-autour` | animate for decoration |
| camera | `nul-camera` | `camera-poussee` | `camera-recul`, `camera-travelling`, `camera-se-pose`, `zoom-detail` | roll, change direction within a shot |

---

**Feature film** (a software product shown through its interface components, one verb per feature, shapes that act): `film-fonctionnalites.md`. The guides below give the moves; that one says how to combine them.

## 2. Title (a name, or 1 to 4 words)

**What to animate.** Opacity, and vertical position if the title must be noticed. Nothing else.

**How.**

| recipe | era | what it does | settings (default, range) | counts |
|---|---|---|---|---|
| `coupe` | all | full from the first frame of the shot | — | 14 titles out of 29 |
| `titre-fondu-montee` | 2024-2026 | fades in on an S curve and rises to its place | `T_opacite` 0.77 s (0.64–0.77), `easeInOutCubic`; `T_position` 0.92 s (0.92–1.17), `easeOutExpo`, starts `retard_position` 0.30 s (0.26–0.31) after the fade; `montee` 15.3 u (7.4–15.5); starting `flou` 0 (convention, up to 0.4) | 4 out of 29, identical to the hundredth in 3 cases out of 4 |
| `titre-fondu` | all | fades in place | `d1090` 0.43 s (0.27–0.71), `ease` | 5 out of 29 |
| `titre-balayage` | 2024-2026 | is revealed left to right behind a soft-edged front | `T` 0.6 s (0.33–0.86), linear; `bord` 2.8% of the width (2.8–6.3) | 3 out of 29 |
| `phrase-zoom-arriere` | 2019-2020 | starts very large and blurred, settles | see § 3 | 2 sentences |
| `chute` | 2019-2020 | drops from above, no bounce | see § 3 | 6 drops |

**Why the rise is delayed by 0.30 s.** The rise only shows from 20% opacity on: the title seems to rise in place while it appears. It does not "slide" to its place.

**When.** After a cut to the empty background (0.13 to 0.23 s of emptiness, 135 cases). This emptiness counts until the first visible trace: the S-curve opacity of `titre-fondu-montee` already takes 0.09 s to reach 2% (0.13 s for a line of `liste-cascade`). So set `debut` 0 to 0.10 s after the cut; the checker computes the visible emptiness. Then the title holds: median 2.3 s for a cut-in title (0.2 to 4.8), 2.0 s for a fade + rise title (1.2 to 8.2). It leaves on a cut.

**Don't.** Slide in from the left or right (0 out of 41 titles and sentences). Rotate (0 out of 145 texts). Write letter by letter (0 out of 145). Bounce (0 out of 145). Fade longer than 1 s (3 cases out of 91, a single slide). Put a box or a banner behind it (0 out of 145).

---

## 3. Sentence (one idea, 1 or 2 lines)

**What to animate.** Usually nothing: the sentence gets a shot of its own (6 out of 12). Otherwise, opacity and position like a title.

**How.**

| recipe | era | what it does | settings | counts |
|---|---|---|---|---|
| `coupe` | all | full from the first frame | — | 6 sentences out of 12; hold 3.1 s (2.6–5.2) |
| `titre-fondu-montee` | 2024-2026 | like a title | § 2 | (measured on titles) |
| `carton-fondu` | all | fades without moving | § 8 | 7 cards out of 7 |
| `carton-groupes` | all | builds up in groups of 2 to 4 words | § 8 | 3 cards |
| `phrase-zoom-arriere` | 2019-2020 | starts at ×8 and blurred, settles | `depart` ×8 (7.5–8.1); `T_echelle` 0.42 s (0.40–0.45), `ease`; opacity `d1090_opacite` 0.35 s (0.33–0.37), `ease-in-out`; `flou` σ 5 u (4.4–6.7) that shrinks with the scale | 2 sentences out of 12 |
| `chute` | 2019-2020 | drops from above, speeds up, stops dead | `T` 0.23 s (0.20–0.27), `easeInQuad`; `hauteur` 68 u above (45–75) | 6 drops (3 sentences, 3 numbers); no bounce 6 out of 6 |
| `phrase-par-le-bas` | 2019-2020 | enters from below the frame, already opaque | `T` 0.65 s (0.6–0.7), `ease`; `depart` 58 u (50–60) | 1 sentence |

**When.** A sentence is read: give it 2.6 to 5.2 s. All animated sentences in the corpus are from 2020 (6 out of 6). In 2024-2026, a sentence cuts in or fades.

**Don't.** Write word by word over an image (0 out of 12). Fade alone, with no other move, over a composed image (0 out of 12: fade alone is for cards). Slide from the side (0 out of 41).

---

## 4. Kicker (the small line above the main word)

**What to animate.** Nothing of its own. It follows its word.

**How.** `avec`, naming the word in `"avec"`. It takes that word's recipe and start. Setting `ecart`: 0 s (−0.06 to +0.06). Counts: 8 kickers out of 11 that can be told apart arrive with their word, within 0.06 s.

Special case: a price. The name moves up to make room for the label and the price, which enter together below it: `nom-remonte` (§ 7).

**Don't.** Animate it alone, before its word (0 out of 13). Slide it in from an edge (0 out of 13).

---

## 5. List

**What to animate.** The opacity of each line, and a small rise. Lines light up top to bottom (16 lists out of 16).

**How.**

| recipe | era | what it does | settings | counts |
|---|---|---|---|---|
| `liste-cascade` | 2024-2026 | all lines in under a second, overlapping | `decalage` 0.10 s (0.093–0.113); opacity `T_opacite` 1.14 s (1.00–1.17), `easeInOutCubic`, starting with the rise (10–90 measured 0.72 s, tail included); rise `T_position` 1.17 s (0.98–1.17), `easeInOutQuint`, `montee` 21 u (18–23) | 3 lists, 10 offsets; rise `easeInOutQuint` 7 lines out of 11 (`easeInOutQuart` 4); `easeInOutCubic` 11 lines out of 13; at 25% opacity, the line is still 18 u below its place (11 lines out of 11) |
| `liste-cascade-rapide` | 2024-2026 | the same, tighter | `decalage` 0.05 s (0.029–0.066); opacity `T_opacite` 0.75 s (0.64–0.83), `easeInOutCubic` (10–90 measured 0.42 s); `montee` 4 u (0–4.1); `T_position` 1.0 s, `easeInOutQuint` | 2 lists, 13 offsets |
| `liste-au-fil` | 2024-2026 | one line when it is spoken; the block moves up by half a line spacing at each addition | `intervalle` 2 s (1.4–3.6), or the `temps` list; opacity `T_opacite` 1.17 s, `easeInOutCubic`; rise `T_position` 0.95 s, `easeInOutQuart`, `montee` 15 u (14–17) | 3 lists; block moves up 2 lists out of 2 |
| `liste-par-le-bas` | 2019-2020 | already-opaque lines rising from below | `decalage` 0.37 s (0.362–0.377); `T` 0.65 s (0.63–0.67), `easeOutQuart`; `depart` 31 u (27–35) | 4 lists from June 2020 |

**Why the offset is so short.** 0.05 to 0.10 s against 0.42 to 0.72 s of fade (5 lists out of 5): you don't read each line on its own, you see a block lighting up from top to bottom. The offset gives a reading direction, not a rhythm.

**When.** Cascade: at the start of a shot, after the empty beat. One by one: one line per spoken idea (with music, sync them to the strong beats: **convention**).

**Don't.** Bring a line in from the side (0 out of 16). Move it down to its place (0 out of 13 lists where a move is measured). Light up bottom to top (0 out of 16).

---

## 6. Word that changes (same place, another word)

**What to animate.** As little as possible. Changing a word is not a moment: 5 changes out of 14 take one frame or less than 0.3 s.

**How.**

| recipe | era | what it does | settings | counts |
|---|---|---|---|---|
| `mot-remplace` | all | the old word disappears, the new one appears on the same frame | — | 3 out of 14 |
| `mot-fondu-enchaine` | 2024-2026 | the old word blurs and fades, the new one appears | `d1090_ancien` 0.50 s; `d1090_nouveau` 0.47 s, `easeInOutSine`; `ecart` 0.61 s between the two midpoints; `flou` 1.5 u (convention) | 1 case |
| `mot-glisse` | 2019-2020 | the old word rises while fading, the new one arrives below | `d1090_ancien` 0.22 s (`ease-in`); `d1090_nouveau` 0.20 s (`easeInCubic`); `ecart` 0.16 s; `glisse` 6 u (convention) | 1 case |

**Don't.** Morph the letters of one word into another (0 out of 14). Roll the word like a counter (0 out of 14).

---

## 7. Hero number

**What to animate.** The **scale**, with a blur that follows the scale, and the opacity. Then the label, alone, fading in place.

**How.**

| recipe | era | what it does | settings | counts |
|---|---|---|---|---|
| `chiffre-pose` | 2024-2026 | starts too large and blurred, settles without overshoot | `depart` ×4.1 (1.9–8; ×3.4 on the first frame); `T_echelle` 0.67 s (0.25–0.80), `easeOutExpo`; opacity `d1090_opacite` 0.20 s (0.18–0.62), `ease-in-out`; `flou` σ 6.7 u at start (1.1–6.7, measurement limit) dropping to 0 with the scale; label `retard_libelle` +0.23 s (0.19–0.30) from the midpoint of the number's fade to the midpoint of its own, `d1090_libelle` 0.27 s (0.26–0.27), `ease-in-out` | 18 numbers out of 27; no overshoot 18 out of 18; label after 15 out of 18; label fade `ease-in-out` 15 out of 15 |
| `chiffre-croissance` | 2019-2020 | grows from small, overshoots by 5%, comes back | `depart` ×0.22 (0.19–0.37); `T_echelle` 0.83 s (0.72–0.88), `easeOutBack`; `d1090_opacite` 0.22 s; label +0.26 s (midpoint to midpoint), fade 0.11 s | 6 out of 27; overshoot +5% 6 out of 6 |
| `chute` | 2019-2020 | drops from above | § 3 | 3 numbers |
| `nom-remonte` | all | a name moves up to make room for the label and price below | `T_nom` 0.50 s (0.45–0.53), `ease`, `remontee` 10 u (7.4–10.7); label + price: `d1090_opacite` 0.30 s (0.22–0.41), `montee` 10 u (6–14) | 5 price slides out of 5 |

**Why opacity is faster than scale.** The number is already readable when it finishes settling (14 out of 18): the eye reads the number while the size adjusts. The blur sells the speed of the zoom. No zoom, no blur (0 out of 27).

**When.** The number gets its own shot, on a plain background. It holds 3.0 s (1.6 to 5.8). The label follows: it says what the number counts.

**Don't.** **Count up** (0 out of 27: the number is final from its first visible frame). Fade in place with no scale (0 out of 27). Blur with no zoom (0 out of 27). Animate the label with the same move as the number (it fades in place, 24 out of 27).

**No made-up numbers.** A number that was not supplied is written `[TO PROVIDE]`, with its source to be provided.

---

## 8. Film card (full-frame text between two images)

**What to animate.** Opacity only.

**How.**

| recipe | what it does | settings | counts |
|---|---|---|---|
| `carton-fondu` | fades without moving | `d1090` 0.45 s (0.31–0.78), linear | 7 fades out of 7 with no movement; linear 3 out of 7 |
| `carton-groupes` | the sentence builds up in meaning groups; the line re-centers at each addition | `ecart` 0.75 s between groups (0.6–2.5); each group `d1090` 0.45 s; `T_recentrage` 0.3 s, `easeOutCubic` (convention) | 3 cards |
| `coupe` | full at the cut | — | 4 cards out of 16 |

**When.** One card per idea. It holds 2.2 s (0.2 to 4.2). It fades slower than a number (0.45 s vs 0.20 s): it is read, it does not hit.

**Don't.** Make it rise or zoom (0 out of 7). Build it word by word at a fixed pace (0 out of 3).

---

## 9. Logo and end name

**What to animate.** Opacity, in place. Nothing else.

**How.** `logo-fin`: `entree` `fondu` (10–90 at `d1090` 0.65 s, range 0.27–2, `out-quad`) or `coupe`. A small line underneath arrives with it (`avec`, 2 end cards) or after it (0.9 s and 5 s, 2 cards). In that case, use a separate element with its own `debut` and the same recipe (read from contact sheets, 4 cards).

Counts: 20 end names, entry by cut 10, by fade 10; movement of 1.1 u at most in 18 out of 20; vertical center between 47 and 51% of the height in 15 out of 20; held 2.6 s (1.25 to 4.7). The final card of a keynote holds 4 to 50 s (median 21.5 s).

**When.** Last, in a shot of its own (plain background in 16 cases out of 20). Before it, a long exit move is common (7 keynotes out of 8): the camera rises, pulls back, or the object leaves the frame.

**Don't.** Slide or rise on entry (0 out of 20). Make it spin, bounce or draw itself stroke by stroke (not observed). Reuse another brand's logo.

---

## 10. Product image (cut-out object, render or photo)

**What to animate.** Almost never the object itself. The **camera** (a parent null) moves in, pulls back or slides; the **light** reveals. The object only moves to enter, turn a quarter turn, or open into an exploded view.

**How.**

| recipe | what it does | settings | counts |
|---|---|---|---|
| `coupe` + `camera-poussee` | the object is there; the camera moves in gently for the whole shot | § 15 | linear push-ins 7 out of 11 |
| `produit-entree` | enters from the right on the cut, brakes, settles, with motion blur | `T` 0.9 s (0.82–0.93), `out-cubic`; `depuis` right (left: convention); `obturateur` 120° (74–169) | 9 entries; brakes 8 out of 8; from the right 7 out of 7 |
| `produit-pivot` | from profile to front, at constant speed (3D layer, Y rotation) | `angle` 90° (12–90; with a flat image, start at 70° so it stays visible); `T` 2 s (1.7–2.6), linear; `delai` 0.25 s after the cut | 4 pivots out of 5 linear; ends facing front 4 out of 4 |
| `produit-poussee` | the object grows slowly (if there is no camera) | `facteur` ×1.27 (1.02–2.58); `duree` 4.1 s (2.2–8.6) or its whole presence; linear | 11 push-ins |
| `produit-recul` | the object shrinks while braking | `facteur` ×0.45 (0.05–0.84); `duree` 5.8 s (2.7–8.5); `ease-out` | 6 pull-backs, brake 4 out of 6 |
| `produit-rotation` | turns in the plane (object seen from above) | `angle` 83° (19–160); `duree` 4.2 s (1.4–9.5), linear | 6 instances; no full turn 0 out of 17 |
| `produit-flotte` | levitation: **no movement**, a soft shadow underneath | `derive` 0 u/s (convention: 1 to 10 for a suspended object drifting in a straight line); `ombre` 1 (convention) | still within 0.3 u in 10 holds out of 13; 0 oscillation out of 14 |
| `eclate` | the parts spread apart while braking, or come together | `sens` ouvre (`T_ouvre` 1.9 s, `ease-out`) or ferme (`T_ferme` 1.2 s, linear); `amplitude` ×1 (convention); `decalage` 0 s between parts (convention) | 7 openings, brake 5 out of 7; 9 closings; 1 overshoot out of 15, within the margin |
| `revelation-lumiere` | the object comes out of the dark, or goes dark | `d1090` 1.6 s (0.1–6), linear; `delai` 0.3 s (0.2–0.4); `sens` allume or eteint (going dark 1.0 s); `eclat` 0% (up to 28 for a chip, 3 out of 12) | 12 reveals from dark; 7 go-darks |
| `balayage-lumiere` | a streak of light crosses once | `T` 0.28 s (0.10–1.17), linear; `largeur` 31% of the object (5–32); `sens` droite, gauche or haut; `intensite` 45% and `inclinaison` 20° (conventions) | a single pass 11 out of 11; downward 0 out of 11 |

Extras chain with `puis`: for example `produit-entree`, then `balayage-lumiere` 1.1 s later (example in `assets/exemple-motion.json`).

**When.**
- The side entry starts **on** the cut (8 out of 8). Everything else waits a little: pivot 0.2 to 0.3 s after the cut, a chip lighting up 0.2 to 0.4 s after.
- After the gesture, the object holds: 6.5 to 8 s after a pivot, 3.5 to 7.7 s after an exploded view.
- In a film (short shots with cuts), the camera is still moving at the next cut (9 push-ins out of 17).

**Don't.** Float the object up and down (0 out of 14). Do a full turn (0 out of 17) or pivot more than a quarter turn (0 out of 7). Bounce on arrival (0 out of 8 entries). Repeat the light streak (0 out of 11) or send it downward (0 out of 11). Blur a still object.

**What to provide.** A cut-out PNG, large enough for the push-in: for ×1.27 in 1080p, the object must stay sharp at 1.27 times its on-screen size. For a pivot: the engine turns the layer in 3D (`ADBE Rotate Y`); a flat image then turns like a card, with no volume. Real volume needs a 3D render of the object or a series of views (**convention**). For an exploded view, the parts as separate files with the same frame (`pieces`).

---

## 11. Interface screenshot (a screen in the film, not an app animation)

**What to animate.** The screenshot's **frame** and the camera looking at it: zoom into a detail, content scrolling, a panel arriving, a row of screens, a scrim around it. The screenshot stays an image: the skill does not simulate an app's behavior.

**How.**

| recipe | what it does | settings | counts |
|---|---|---|---|
| `zoom-detail` | the camera goes into a detail (or comes back out); scale and position, same curve | `facteur` ×2.2 (1.45–3); `T` 0.95 s (0.6–1.53); `sens` entre or sort; `point` of the detail in % of the element (convention); curve `zoom-2024` (2024-2026) or `montage-2020` | 27 zooms visible 0.60 to 1.00 s; 0 linear, 0 overshoot, 0 rotation |
| `defilement` | the content scrolls inside a window | `distance` 59.5 u (14–196); `T` 1.07 s (0.94–2.16); `mode` presentation (`defilement-2024`), geste (`geste`, flung, 1.72 s) or continu (linear, 68 u/s); `fenetre` 60 × 60 u (convention) | 27 scrolls; peak speed 168 u/s; never more than 196 u at once |
| `panneau-pose` | a panel arrives from an edge and settles | `visible` 0.36 s (0.17–0.50); `distance` 40 u (15.9–62); `depuis` bas, haut, gauche, droite; `dans_la_page` 1 (curve `ease`) or edge (`out-expo`); `carte` 1 = overshoot ≤ 6% (`out-back`); `fondu` 1 (convention) | 16 panels; none beyond 0.5 s |
| `empilement` | one more screen enters from the side and pushes the row | `intervalle` 1.67 s (0.83–10.5; burst 0.85 s); `T` 0.79 s (0.6–1; 0.96 s in 2019-2020), curve `rangee-2024` or `montage-2020`; `ecart` 4 u between screens (convention); one file per screen (`fichiers`) | 29 instances; offset 26.6 u; 0 overlap out of 11 sequences; 0 vertical out of 19 |
| `assombrir-autour` | a black scrim falls on everything except the element; the background may blur | `niveau` 40% (5–73; spotlight 65 to 70); `T` 0.53 s (0.4–0.6), curve `voile`; `flou` σ 0 u (0–0.78; median 0.34) | 20 scrims; never all the way to black 20 out of 20; blur with scrim 10 out of 14 |

**When.**
- The zoom starts after the whole screenshot has been seen (convention: at least 0.5 s). Then we **stay** on the detail: median 7.2 s (2.5 s at the lower quartile).
- One screen at a time in a row: the next one starts after the previous one ends.
- The scrim and the background blur start together and last the same time.
- To go from one screenshot to another: transition `glissade` or `poussee` (§ 16).

**Don't.** Zoom linearly (0 out of 27), rotate during a zoom (0 out of 27). Slide a screen vertically (0 out of 32). Bring in two screens together (0 out of 11). Darken all the way to black (0 out of 20). A panel longer than half a second (0 out of 16). A strong background blur (above 0.78 u: 0 out of 14).

**What to provide.** Screenshots at native resolution or ×2, with no personal data (blurred or demo data). No brand device frame: a floating rounded-corner panel replaces it.

---

## 12. Icon

Few measurements cover the icon alone. What is observed:
- it arrives **with** its word or title, with no animation of its own (kicker rule, 8 out of 11: `avec`);
- in an icon grid, the right one is pointed out with a spotlight: a scrim of 33 to 73% on the others (4 cases), background blur up to σ 0.78 u, and the chosen icon growing about ×2 as it moves to the center (1 case, read from a contact sheet). `assombrir-autour` with `niveau` 65 to 70 and `flou` sets the scrim and the blur. The enlargement is not in the recipe (add it by hand, curve `montage-2024`, 0.9 s: **convention**);
- in a match cut, you cut from an icon to the same place in another content (11 match cuts out of 22 keep the frame and change the content).

**How.** `avec` (default), `coupe`, `assombrir-autour`. `produit-entree` or `revelation-lumiere` if the icon is treated as an object (**convention**).

**Don't.** Spin, bounce or pulse an icon (no case observed; the general rules apply: 0 bounce, 0 text rotation, 0 oscillation).

---

## 13. Shape (line, circle, gauge, drawn panel)

**What to animate.** The shape's position or size when it arrives; its light. A shape does not decorate: it carries information (a gauge, a path, a frame).

**How.**
- `coupe` (default).
- `panneau-pose` for a frame or a card that arrives.
- `eclate` for plates that spread apart or settle.
- `balayage-lumiere` and `revelation-lumiere` for light.
- A gauge that fills: the value is revealed left to right in 0.26 s (10–90), a curve close to a soft ease-out (1 case, measured). A gauge that slides to make room: 0.2 s (1 case). Outside the recipes: write this gesture by hand (`courbes.md` § 7).
- A path drawing itself: 3 highlights follow the tip of an engraved path at near-constant speed, 12 to 19% of the width per second, for 2 to 2.6 s (measured on the highlight). Outside the recipes: the end of a "Trim Paths" (`ADBE Vector Trim End`) from 0 to 100%, linear.

**Don't.** An animated box or banner behind a text (0 out of 145). A shape that oscillates, spins in a loop or bounces.

---

## 14. Background

**What to animate.** Nothing, for decoration. The background changes by a cut, a light switch, a pass through black. It darkens or blurs behind what is shown.

**How.**
- `coupe`: the cut to the empty background of the next image (135 cases), then the elements enter.
- Transition `bascule-lumiere`: the background goes dark within the shot, the object stays lit; `T` 2.4 s (1.2–2.6), curve `in-out-sine`; `niveau` 85% (convention). Counts: 4 slow switches out of 4 eased.
- Transitions `passage-noir`, `montee-du-noir`, `fondu-au-noir`, `fondu-depuis-noir`: § 16.
- `assombrir-autour` on the featured element: the scrim covers the background.

**Observed backgrounds**: plain, black or very dark, very light gray; in 2025, blurred colored backgrounds (not measured in motion). An empty light background holds 0.13 to 0.23 s after the cut.

**Don't.** A rotating gradient, particles, a background that breathes in a loop (not observed: **convention** not to do them). A fade to white between two sequences (0 seen).

---

## 15. Camera (a parent null: `nul-camera`)

**What to animate.** The scale and position of a null that carries the elements (push-in, pull-back, slide). The elements below it keep their own recipes. Several depths give parallax (each element's `profondeur`).

**How.**

| recipe | what it does | settings | counts |
|---|---|---|---|
| `camera-poussee` | moves in at constant speed, from the start to the end of the shot | `facteur` ×1.27 (1.02–2.58); linear | 7 push-ins out of 11 linear; starts less than 0.25 s after the cut 9 out of 17 |
| `camera-recul` | pulls back while braking | `facteur` ×0.45 (0.05–0.84); `ease-out`; 7.4 to 8.5 s to reveal the whole object from a detail | 6 pull-backs, brake 4 out of 6 |
| `camera-travelling` | slides at constant speed; the foreground moves faster than the background | `vitesse` 4.7 u/s (0.5–48) for depth 1; `direction` [−1, 0] (convention); parallax: foreground 1.9 times faster than background (0.9–12.4), up to 10 times for an object in front of a blurred background | 216 translations out of 309 moving shots; linear parallaxes 8 out of 13 |
| `camera-se-pose` | slows to a stop within the shot | `d1090` 4.4 s (2.1–5.2); `facteur` ×0.68 (0.46–1); `deplacement` (convention); `out-cubic` | 7 out of 21; arrives at zero speed 7 out of 7 |
| `zoom-detail` | fast move into a detail | § 11 | 27 zooms |

**When.** One camera recipe per shot. The move starts with the shot. In a film, it is still moving at the cut; in a composed image, it settles and then the image holds (`principes.md` § P10). Close to the object, slow: 1.4 to 5.7% scale per second for a revealing pull-back (4 cases).

**Don't.** Roll (median roll 0.2 °/s; none during a zoom, 0 out of 27). Change direction within a shot (0 out of 17). Overshoot the final scale (0 out of 17). A push-in shorter than 1.1 s (10–90): that would be a zoom, not a push-in.

---

## 16. Going from one shot to the next (`transitions`)

| transition | what it does | settings | counts | when |
|---|---|---|---|---|
| `coupe` | nothing between the two images | — | more than 95% of changes | default |
| `raccord` | cut on the same shape, in the same place | — | 22 match cuts out of 22 by cut; center moved by 3.2 u, size within 12% (21 out of 22) | going from one content to another in the same frame |
| `passage-noir` | fade to black, black held, fade from black, all linear | `T_fondu` 0.5 s (0.33–1.27); `noir` 0.5 s (0.4–1.5) | linear fades to black 21 out of 21; black of at least 0.40 s 25 out of 25 | closing a sequence |
| `fondu-au-noir` | the image goes to black | `T` 0.5 s (0.33–1.27), linear | 21 out of 21 | end of a film, before the name |
| `fondu-depuis-noir` | the image comes up from black | `T` 0.5 s (0.34–2.71); beyond 0.68 s, the curve brakes (`out-cubic`) | 11 short linear out of 16; 5 long braked out of 5 | opening a sequence |
| `montee-du-noir` | cut to black, short black, the image lights up | `noir` 0.27 s (0.1–0.5, convention); `d1090` 0.39 s (0.17–0.74), `in-out-cubic` | soft start 13 out of 14 | a photo, an object, a number that "lights up" |
| `fondu-enchaine` | short blend of the two images | `T` 0.54 s (0.25–0.98), linear | 25 checked; none beyond 1 s | rare: between two object renders, two shots of a clip |
| `glissade` | the whole shot leaves to the side, the next enters, with motion blur | `T` 0.89 s (0.64–0.94), curve `glissade`; `sens` gauche or droite | 16 slides, 138 u; horizontal 32 out of 32 | from one screen to another |
| `poussee` | one content pushes another inside a fixed frame | `T` 0.75 s (0.6–1.02), curve `poussee-ecran`; `sens` | 7 instances | from one screen to another in the same frame |
| `bascule-lumiere` | the background goes dark within the shot | § 14 | 4 out of 4 eased | isolating the object before the reveal |

**Don't.** A wipe, a page effect, a transition zoom between two sequences (0 seen; wipe, iris and sign-shaped mask reserved for endings: **convention**). A cross-dissolve longer than 1 s (0 out of 25). A black shorter than 0.40 s between two fades (0 out of 25). A match cut done as a fade (0 out of 22).

---

## 17. Building a sequence

The most common template, for a composed image (a convention that assembles the measurements above):

1. **Cut to the empty background**; it holds 0.13 to 0.23 s until the first visible trace. The soft start of an S-curve opacity is part of it: `debut` 0 to 0.10 s after the cut.
2. **The main element enters** with its recipe (title, number, object, screenshot). One major move at a time.
3. **What goes with it follows**: the kicker with it (`avec`), the label 0.23 s after (fade midpoint to fade midpoint), the small line after the logo.
4. **A light or camera gesture** is added if the image holds a long time: slow push-in for the whole shot, one light streak, a scrim around a detail.
5. **The image holds**: 2 to 3 s for a text, 3 s for a number, 6 to 8 s for a pivoting object, several seconds on a screen detail.
6. **Cut** to the next image. A pass through black to close a sequence; the end name alone, last.

The rhythm of a film (short shots, 29.7 cuts per minute) and that of a composed image (an image that settles and holds) don't mix within one shot.
