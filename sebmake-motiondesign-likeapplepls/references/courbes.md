# Measured curves

This file gives every curve in the engine: its shape (`cubic-bezier`), its translation into After Effects keys (`KeyframeEase`), and the use it was kept for, with counts. The engine (`scripts/motion_lib.mjs`) holds the same table, under the same names: that name is what you write in `motion.json` to force a curve.

Read `principes.md` § P2 first: the curve depends on the **role** of the move, not on the object.

---

## 1. Reading a curve

A curve says how the value moves between two keys. `cubic-bezier(x1, y1, x2, y2)`: time goes from 0 to 1 on the x axis, progress from 0 to 1 on the y axis. `(x1, y1)` is the start handle, `(x2, y2)` the end handle.

- **Linear** `(0, 0, 1, 1)`: constant speed.
- **"out" family** (`y1` = 1, or close): starts fast, brakes, settles. This is the arrival.
- **"in" family** (`y2` = 0, or close): starts gently, speeds up. This is a departure, or a light fading down to black.
- **S curve** (`in-out`): starts gently, ends gently.
- **Overshoot**: a `y` value above 1. The value passes its target, then comes back.

Four roles, four families (counts in `principes.md` § P2):

| role | family | engine curves |
|---|---|---|
| editing goes from one image to the next | linear | `lineaire` |
| a move crosses the shot | linear | `lineaire` |
| an element arrives and settles | "out" or S | `easeOutExpo`, `out-cubic`, `out-expo`, `ease`, `montage-2024`, `zoom-2024`, `glissade`, `rangee-2024`, `poussee-ecran`… |
| something lights up or goes dark | "in" or S | `easeInOutCubic`, `in-sine`, `in-out-cubic`, `in-out-sine`, `voile`, `ease-in-out`… |

---

## 2. Translating a curve into After Effects keys

For a property animated from `v0` (at time `t0`) to `v1` (at time `t1`), with `T = t1 − t0` and the average speed `m = (v1 − v0) / T`:

| key | side | influence | speed |
|---|---|---|---|
| start key | **outgoing** ease | `x1 × 100` | `(y1 / x1) × m` |
| end key | **incoming** ease | `(1 − x2) × 100` | `((1 − y2) / (1 − x2)) × m` |

```js
prop.setTemporalEaseAtKey(k0, [easeEntrantDeK0], [new KeyframeEase(vitesseSortie, influenceSortie)]);
prop.setTemporalEaseAtKey(k1, [new KeyframeEase(vitesseEntree, influenceEntree)], [easeSortantDeK1]);
```

(`easeEntrantDeK0` = the incoming ease already on k0; `vitesseSortie`, `influenceSortie` = outgoing speed and influence; `vitesseEntree`, `influenceEntree` = incoming speed and influence; `easeSortantDeK1` = the outgoing ease already on k1.)

**Special cases.**
- **Linear**: no `KeyframeEase`. Both keys in `KeyframeInterpolationType.LINEAR`.
- **Zero handle** (`x1 = y1 = 0`, or `x2 = y2 = 1`): influence 0.1 (the minimum) and the slope of the other handle. This is the case for `ease-out` and `ease-in`.
- **Influence**: between 0.1 and 100.
- **Sign**: speed follows the direction of change. It is negative when the value goes down (a scale from 400 % to 100 %, a position moving up).
- **Overshoot**: the incoming speed becomes negative (`easeOutBack`). After Effects and EffectCraft accept it.
- **Scale** (3 linked dimensions): an array of 3 `KeyframeEase`, one per dimension, each with that dimension's speed.
- **Position**: separate the dimensions (`dimensionsSeparated = true`) and animate `ADBE Position_0` (X) and `ADBE Position_1` (Y), which are one-dimensional. A linked position expects a single `KeyframeEase` whose speed is the path length; that is more fragile. The engine always separates.
- **Hold key** (a clean jump, no curve): `KeyframeInterpolationType.HOLD` on the key.

**Checked in EffectCraft on 10/21**: the gap between rendered progress and the `cubic-bezier` is 0.0002 at most, over 7 curves (including `montage-2024` and an overshoot with negative speed), on opacity, separated Y position and scale. In EffectCraft, the composition must be open in the viewer (`comp.openInViewer()`) **before** the eases are set, or they are ignored. The engine does this. After Effects is not installed here: the formula follows its keyframe model, but the result was not rendered there.

---

## 3. The table

"Out" = start key, "in" = end key: influence in %, speed as a multiple of the average speed `m`. "Share 10–90": the share of `T` during which the value goes from 10 % to 90 %; "share visible": from 2 % to 98 %. They convert a measured duration into the key spacing (§ 5).

### 3.1 Linear and CSS

| name | cubic-bezier | out | in | share 10–90 | share visible | kept for |
|---|---|---|---|---:|---:|---|
| `lineaire` | 0, 0, 1, 1 | LINEAR | LINEAR | 0.80 | 0.96 | fades to black 21 out of 21; camera push-ins 7 out of 11; pivots 4 out of 5; parallaxes 8 out of 13; streaks of light (r² 0.91) |
| `ease` | 0.25, 0.1, 0.25, 1 | 25; 0.4 × | 75; 0 × | 0.52 | 0.78 | name rising above a price 3 out of 5; zoom out of a sentence 2 out of 2; title in slow fade 2 out of 5; panel sliding into the page (1 case) |
| `ease-in` | 0.42, 0, 1, 1 | 42; 0 × | 0.1; 1.72 × | 0.68 | 0.88 | pivot that speeds up (variant); fade-out |
| `ease-out` | 0, 0, 0.58, 1 | 0.1; 1.72 × | 42; 0 × | 0.68 | 0.88 | pull-backs 4 out of 6 (grouped curve); exploded view opening 5 out of 7; 2020 number opacity 4 out of 6 |
| `ease-in-out` | 0.42, 0, 0.58, 1 | 42; 0 × | 42; 0 × | 0.56 | 0.80 | opacity of the settling number (shared fit, 18 numbers); interface scrim |

### 3.2 Table from the "text" analysis (camelCase names)

| name | cubic-bezier | out | in | share 10–90 | share visible | kept for |
|---|---|---|---|---:|---:|---|
| `easeInOutCubic` | 0.645, 0.045, 0.355, 1 | 64.5; 0.07 × | 64.5; 0 × | 0.44 | 0.74 | opacity of "fade + rise" titles 4 out of 4; cascade lines 11 out of 13 |
| `easeOutExpo` | 0.19, 1, 0.22, 1 | 19; 5.26 × | 78; 0 × | 0.29 | 0.51 | title rise 4 out of 4; scale of the settling number 11 out of 18 |
| `easeInOutQuart` | 0.77, 0, 0.175, 1 | 77; 0 × | 82.5; 0 × | 0.34 | 0.65 | rise of cascade lines (0.10 s), 4 lines out of 11; new line following the voice |
| `easeInOutQuint` | 0.86, 0, 0.07, 1 | 86; 0 × | 93; 0 × | 0.29 | 0.62 | rise of cascade lines (0.10 s), 7 lines out of 11; fast cascade (0.05 s) |
| `easeInQuad` | 0.55, 0.085, 0.68, 0.53 | 55; 0.15 × | 32; 1.47 × | 0.63 | 0.89 | drop from above 5 out of 6 (2020 sentences and numbers) |
| `easeOutQuart` | 0.165, 0.84, 0.44, 1 | 16.5; 5.09 × | 56; 0 × | 0.45 | 0.71 | lines entering from below (June 2020), shared fit |
| `easeOutBack` | 0.175, 0.885, 0.32, 1.275 | 17.5; 5.06 × | 68; −0.40 × | 0.26 | 0.35 | number growing in 2020, 6 out of 6 (overshoot +5 %) |
| `easeInOutSine` | 0.445, 0.05, 0.55, 0.95 | 44.5; 0.11 × | 45; 0.11 × | 0.57 | 0.83 | new word in a cross-fade (1 case) |
| `easeInCubic` | 0.55, 0.055, 0.675, 0.19 | 55; 0.10 × | 32.5; 2.49 × | 0.54 | 0.84 | sliding word (1 case); 2024 fast cascade, 7 lines out of 7 |
| `easeOutCubic` | 0.215, 0.61, 0.355, 1 | 21.5; 2.84 × | 64.5; 0 × | 0.51 | 0.76 | recentering a line that builds up (**convention**) |

### 3.3 Table from the "objects", "interfaces" and "transitions" analyses (kebab-case names)

| name | cubic-bezier | out | in | share 10–90 | share visible | kept for |
|---|---|---|---|---:|---:|---|
| `out-cubic` | 0.33, 1, 0.68, 1 | 33; 3.03 × | 32; 0 × | 0.51 | 0.73 | blurred side entrance of a product 8 out of 8 (grouped curve, error 0.075); camera that settles |
| `out-quad` | 0.5, 1, 0.89, 1 | 50; 2 × | 11; 0 × | 0.63 | 0.84 | end logo lighting up (3 "out" fades out of 10); pull-back that settles |
| `out-quint` | 0.22, 1, 0.36, 1 | 22; 4.55 × | 64; 0 × | 0.35 | 0.57 | swipe scroll (variant) |
| `out-expo` | 0.16, 1, 0.3, 1 | 16; 6.25 × | 70; 0 × | 0.31 | 0.54 | panel arriving from an edge (1 out of 4 measured); background blurring (gentle end 8 out of 14) |
| `out-sine` | 0.61, 1, 0.88, 1 | 61; 1.64 × | 12; 0 × | 0.66 | 0.85 | final sign appearing (1 case) |
| `out-back` | 0.34, 1.56, 0.64, 1 | 34; 4.59 × | 36; 0 × | 0.27 | 0.35 | card rising with a 6 % overshoot (1 panel out of 4) |
| `in-quad` | 0.11, 0, 0.5, 0 | 11; 0 × | 50; 2 × | 0.63 | 0.84 | reveal and fade-out that speed up (variant) |
| `in-sine` | 0.12, 0, 0.39, 0 | 12; 0 × | 61; 1.64 × | 0.66 | 0.85 | image rising from black after a cut (2 keynotes) |
| `in-out-sine` | 0.37, 0, 0.63, 1 | 37; 0 × | 37; 0 × | 0.59 | 0.82 | slow light change 2 out of 4; logo fading out |
| `in-out-cubic` | 0.65, 0, 0.35, 1 | 65; 0 × | 65; 0 × | 0.43 | 0.71 | image rising from black 4 out of 14 |
| `in-out-quart` | 0.76, 0, 0.24, 1 | 76; 0 × | 76; 0 × | 0.36 | 0.67 | slow light change (1 case) |

**Two similar names, two curves.** `easeOutExpo` (0.19, 1, 0.22, 1) and `out-expo` (0.16, 1, 0.3, 1) are not the same curve; nor are `easeOutCubic` and `out-cubic`, or `easeInOutCubic` and `in-out-cubic`. The analyses did not fit the same tables. Keep the curve the recipe gives: it is the one kept for its instances.

### 3.4 Family curves (fit jointly on all instances of a family)

These are the safest: one curve fits dozens of instances.

| name | cubic-bezier | out | in | share 10–90 | share visible | kept for |
|---|---|---|---|---:|---:|---|
| `montage-2020` | 0.36, 0, 0.25, 1 | 36; 0 × | 75; 0 × | 0.48 | 0.75 | zooms, slides and rows from 2019-2020: 21 instances, error 0.018 |
| `montage-2024` | 0.6, 0.4, 0.17, 0.95 | 60; 0.67 × | 83; 0.06 × | 0.48 | 0.80 | zooms, slides and rows from 2024-2026: 56 instances, error 0.026 |
| `zoom-2024` | 0.56, 0.32, 0.19, 0.98 | 56; 0.57 × | 81; 0.02 × | 0.47 | 0.78 | zoom into a detail, 2024-2026: 18 instances, error 0.028 |
| `zoom-sortie` | 0.64, 0.47, 0.15, 0.94 | 64; 0.73 × | 85; 0.07 × | 0.48 | 0.81 | zoom back out of the detail: 10 instances, error 0.019 |
| `rangee-2024` | 0.67, 0.49, 0.09, 0.88 | 67; 0.73 × | 91; 0.13 × | 0.49 | 0.85 | screens stacking up, 2024-2026: 14 instances, error 0.014 |
| `glissade` | 0.65, 0.5, 0.15, 0.93 | 65; 0.77 × | 85; 0.08 × | 0.48 | 0.81 | whole shot sliding to the next: 16 instances, error 0.030 |
| `poussee-ecran` | 0.43, 0.08, 0.21, 1 | 43; 0.19 × | 79; 0 × | 0.46 | 0.75 | one content pushes another out, fixed frame: 7 instances, error 0.019 |
| `voile` | 0.44, 0.21, 0.29, 1 | 44; 0.48 × | 71; 0 × | 0.50 | 0.78 | background darkening: 18 instances, error 0.021 |
| `voile-2024` | 0.52, 0.42, 0.34, 1 | 52; 0.81 × | 66; 0 × | 0.53 | 0.79 | background darkening, 2024-2026: 9 instances, error 0.021 |
| `defilement` | 0.36, 0, 0.25, 1 | 36; 0 × | 75; 0 × | 0.48 | 0.75 | scroll: 27 instances, error 0.033 |
| `defilement-2024` | 0.39, 0.06, 0.25, 1 | 39; 0.15 × | 75; 0 × | 0.48 | 0.76 | presentation scroll, 2024-2026: 12 instances, error 0.020 |
| `geste` | 0.43, 0, 0.06, 0.82 | 43; 0 × | 94; 0.19 × | 0.51 | 0.81 | scroll flicked by a finger: 4 instances, error 0.019 |

**The 2024-2026 curve** (`montage-2024`) starts already moving: speed peaks at 39 % of `T`, at 3 times the average speed, then a long tail. The 2019-2020 curve (`montage-2020`) starts and ends at zero speed; its peak is at 30 % of `T`, at 2.4 times the average. **Convention**: one era for the whole film (`principes.md` § P12).

---

## 4. Which curve for which gesture

The engine's recipes choose the curve. This table is for reviewing an animation plan or writing a gesture outside the recipes.

| gesture | property | curve | duration (key to key) | counts |
|---|---|---|---|---|
| fade to black, short fade from black | opacity of a black solid | `lineaire` | 0.50 s | 21 out of 21; 11 out of 16 |
| image rising from black after a cut | opacity | `in-sine` or `in-out-cubic` | 10–90 in 0.39 s | gentle start 13 out of 14 |
| cross-fade | opacity | `lineaire` (no dominant curve) | 0.54 s | 25 checked |
| title that fades and rises | opacity; Y position | `easeInOutCubic`; `easeOutExpo` | 0.77 s; 0.92 s, starting 0.30 s later | 4 out of 4 |
| cascading list line | opacity; Y position | `easeInOutCubic`; `easeInOutQuint` | 1.14 s; 1.17 s, starting together | 11 out of 13; 7 out of 11 |
| number that settles | scale (and blur); opacity | `easeOutExpo`; `ease-in-out` | 0.67 s; 0.36 s | 11 out of 18; shared fit |
| film card, end name | opacity | `lineaire` (card); `out-quad` (name) | 0.56 s; 10–90 in 0.65 s | 3 out of 7; 3 "out" fades out of 10 |
| product entering from the side | X position | `out-cubic` | 0.9 s, on the cut | 8 out of 8 |
| camera push-in | scale of a parent null | `lineaire` | the whole shot | 7 out of 11 |
| camera pull-back | scale of a parent null | `ease-out` | 5.8 s | 4 out of 6 |
| camera settling in the shot | scale, position | `out-cubic` | 10–90 in 4.4 s | arrives at zero speed 7 out of 7 |
| pivot from profile to front | Y rotation (or width) | `lineaire` | 2 s | 4 out of 5 |
| streak of light | position of the band | `lineaire` | 0.28 s | straight front, r² 0.91 |
| object rising from black | opacity of a scrim, exposure | `lineaire` | 10–90 in 1.6 s | linear or speeding up 8 out of 12 |
| exploded view opening; settling | position of the pieces | `ease-out`; `lineaire` | 1.9 s; 1.2 s | 5 out of 7; 3 settles out of 3 |
| zoom into a screen detail | scale and position, same curve | `zoom-2024` (or `montage-2020`) | 0.95 s | 18; 9 instances |
| slide from one screen to the next | X position of both shots | `glissade` | 0.89 s | 16 instances |
| screen joining a row | X position of the row | `rangee-2024` (or `montage-2020`) | 0.79 s (0.96 s) | 14; 5 instances |
| scroll | Y position of the content | `defilement-2024`; `geste`; `lineaire` (continuous) | 1.07 s; 2.16 s | 12; 4; 1 instance |
| panel arriving | position | `out-expo` (from an edge); `ease` (within the page) | 0.36 s visible | 4 curves measured |
| dark scrim around an element | opacity of a black solid | `voile` (or `voile-2024`) | 0.53 s | 18 instances |
| background blurring | Gaussian blur | `out-expo` | same start and same duration as the scrim | gentle end 8 out of 14 |
| slow light change | opacity of a scrim | `in-out-sine` | 2.4 s | 4 out of 4 eased |

---

## 5. From a measured duration to key spacing

The analyses give three durations: 10–90, visible (2–98) and key to key (`T`). In the script, you set `T`. To convert:

`T = 10–90 duration ÷ share 10–90`; `T = visible duration ÷ share visible`.

Examples:
- An `easeInOutCubic` fade of 0.34 s between 10 and 90 %: `T = 0.34 / 0.44 = 0.77 s`.
- An `out-expo` panel visible for 0.36 s: `T = 0.36 / 0.54 = 0.67 s`. The end of the curve is a long, almost still tail.
- A `lineaire` fade to black of 0.40 s between 10 and 90 %: `T = 0.40 / 0.80 = 0.50 s`.

The engine does this math (`T_depuis` in `motion_lib.mjs`): in `motion.json`, each parameter carries its unit and says whether it is a 10–90 duration (`d1090…`), visible (`visible`) or key to key (`T…`).

**To the frame.** Keys are snapped to the frame. Two keys less than one frame apart merge. At 30 frames per second, the shortest measured move (a 0.10 s streak of light) is 3 frames: it works. A 0.17 s panel has only 5 frames: the shape of its curve is no longer visible.

---

## 6. Overshoot

By default, no key goes past its final value (`principes.md` § P7). Three measured exceptions exist, each limited:

| gesture | overshoot | how to set it |
|---|---|---|
| number that grows (2019-2020 style) | +5 % scale, 6 out of 6 | `easeOutBack`, two keys, negative incoming speed; or **convention**: three keys, 20 % → 105 % at 0.6 s (`easeOutCubic`) → 100 % at 1.3 s (`easeInOutSine`) |
| card that rises | +6 %, 1 panel out of 4 | `out-back`, two keys |
| flash of a chip lighting up | +11 to +28 % luminance, 3 out of 12 | three keys (**convention** based on 3 cases): 0 → 115 to 130 % of the final value in 0.5 to 0.7 s, then back to 100 % in 0.6 s |

Both methods (negative speed or third key) work in both tools. The third key is easier to read in the graph editor.

---

## 7. Writing a curve by hand (ES3)

The script the engine produces already contains these functions (`md_anime`, `md_ease`, `md_saut`). For a gesture outside the recipes, in a hand-written script, here is the minimal equivalent. It stays ES3: `var`, `function`, no `let`, no `const`, no arrow function, no template literal, no `JSON`.

```js
// Sets (t0, v0) -> (t1, v1) on a one-dimensional property, with the curve b = [x1, y1, x2, y2].
// b = null: linear. Times are snapped to the composition's frame.
function poserCourbe(comp, prop, t0, v0, t1, v1, b) {
    var fd = comp.frameDuration;
    t0 = Math.round(t0 / fd) * fd; t1 = Math.round(t1 / fd) * fd;
    if (t1 < t0 + fd) t1 = t0 + fd;                      // at least one frame apart
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

// Example: a title fades in (easeInOutCubic, 0.77 s), then rises 15.3 % H (easeOutExpo, 0.92 s, 0.30 s later).
// var tg = titre.property("ADBE Transform Group");
// tg.property("ADBE Position").dimensionsSeparated = true;
// poserCourbe(comp, tg.property("ADBE Opacity"), 1.0, 0, 1.77, 100, [0.645, 0.045, 0.355, 1]);
// poserCourbe(comp, tg.property("ADBE Position_1"), 1.30, 540 + 0.153 * 1080, 2.22, 540, [0.19, 1, 0.22, 1]);
```

(`poserCourbe` = "set curve"; `neutre` = neutral ease.) This version overwrites the ease on the outer sides (`neutre`). To chain several segments on the same property, keep the existing ease on those sides, as `md_anime` does (function `md_garde`).

For scale, pass an array of 3 `KeyframeEase` (one per dimension) instead of one.

---

## 8. Pitfalls

- **Curve ignored in EffectCraft**: the composition was not open in the viewer. Call `comp.openInViewer()` before setting the eases.
- **Two keys merge**: they land on the same frame. Keep at least one frame apart; a fade of 10 frames or more shows its curve.
- **The move goes the wrong way or overshoots**: the speed does not have the sign of the change. It equals `slope × (v1 − v0) / T`, with the sign of `v1 − v0`.
- **The overshoot disappears**: influence was capped at 100, or the negative speed was reset to 0 by another function. Check the key in the graph editor.
- **Linked position**: the speed of a spatial `KeyframeEase` is a path length, not a gap in X or Y. Separate the dimensions.
- **Scale**: 3 eases, not 1. Otherwise the call throws an error.
- **Don't rebuild a curve from its name**: `easeOutExpo` and `out-expo` differ (§ 3.3). Take the bezier from the table.
