# Feature film: components, shapes and verbs

What a film does when it presents a software product **through its features**, with no presenter, built from its interfaces: what to show, in what order, and how to move it. The rules in the other guides (`principes.md`, `elements.md`) apply. This one says **how to combine them** for this kind of film.

**Basis: 2 feature launch films**, 2025 and 2026, logged at 1 and 2 frames per second and by cut list:
- **A**: 30 s, music only, black background, twelve features in twelve verbs;
- **B**: 2 min 13, voice-over, colored backgrounds, seven features, one per shot.

Two films is not much. Everything below is a **convention backed by two cases**, except where marked "(A and B)", which means "seen in both". The durations and counts from the keynotes (`principes.md`) remain the reference for the moves themselves.

---

## 1. The three materials of the film

A feature film has no wide shot of the app. It alternates three materials, and that alternation makes the rhythm:

| material | what it is | what it carries |
|---|---|---|
| **the verb** | a short centered text that names what the user does: *verb + object*, 2 to 4 words | the argument, one per feature |
| **the component** | a piece of interface **taken out of its screen**: a list row, a card, a button, a picker, a row of icons, an editing track | the proof: the feature exists, here is where you touch it |
| **the shape** | an abstract object (sphere, dot, bubble, line) that plays a person or a flow | the story: who does what, to whom it happens |

Film **A** has almost only verbs and components (black background). Film **B** adds shapes: five colored spheres play the five members of a family, and their colors are **those of the avatars in the interface**. The shape enters the screen and becomes the avatar of the row (B, 0:16 → 0:23). Keep this link when you invent shapes: they reuse a color, an icon or a state that already exists in the product.

---

## 2. Order of the film

| time | A (30 s) | B (2 min 13) |
|---|---|---|
| opening | product name in "living" lettering (letters made of objects), then the same name in clean lettering: 0 → 1.5 s | the full screen on a phone, 1 s, then the shapes alone acting out the situation: 0 → 11 s |
| promise | mosaic of all the interfaces (1.5 → 3.3 s), then the promise in two beats: "A …" / "… without end" (3.5 → 5.5 s) | the promise is spoken by the voice (0:15 → 0:28) over the shapes and a blurred screen as backdrop |
| contents | the row of tool icons (5.5 → 7 s) | — |
| features | 12 verbs, 1.0 to 3.7 s each; the last 9 average **1.05 s** (16 → 25.5 s) | 7 features, **one shot each**, 4.5 to 19.6 s (median 6.3 s), in the order a parent meets them |
| price or call | "for X / month" in one line, 26 → 27.5 s | — |
| end name | list of tools grouped by color (27.5 → 28.5 s), then the name in living → clean lettering (28.5 → 30 s) | the shapes regroup (2:04 → 2:07), end sentence, five dots, logo (2:08 → 2:13) |

What repeats (A and B):
- the film **opens and closes on the name** or logo, and the end reuses the opening image (living → clean lettering; spheres regrouped as at the start);
- **one feature = one verb (or one spoken sentence) = one component**. Never two components for one verb, never a verb without a component;
- the component **answers** the verb: it arrives during or just after it, not before;
- the **duration** of a beat is the time to read the verb, not the animation time: 1 s in A when the music carries it, 4 to 7 s in B when the voice explains.

---

## 3. The verb (text)

- **Lettering.** Sans serif, white on black (A) or black on a light background (B), title size (`elements.md` § 2). Centered. One verb on screen.
- **Entry.** By cut or in-place replacement (`mot-remplace`, `elements.md` § 6). In A, 10 verbs out of 12 **replace** the previous one in the same place, on the same black background, with no image cut. The empty background between two verbs lasts 0.1 to 0.5 s (`principes.md` P6).
- **The word carries the feature.** In A, the verb is written **in the material** of what it announces: letters made of flowers then water for "generate"; half the word pixelated for "enlarge"; one letter sliding for "move"; a handwritten word for "write"; a crumpled word falling into a trash can for "throw away"; a word replaced by a strip of video for "edit a video"; a word selected with its handles for "select". **One treated word per verb**. The rest of the sentence stays in clean lettering.
- **Duration.** 1.05 s on average when they follow each other (A, 9 cases), up to 3.7 s when a component builds up underneath (A, "make a beat": 7 → 9.7 s, tracks stacking up).
- **Don't.** More than four words. Two verbs on screen. A verb that slides or bounces (rules in `principes.md` § 13). Treating the whole text: one word is enough.

**With the engine.** `titre` + `coupe` or `mot-remplace`. The treated word is an `image` (PNG rendered separately) placed where the word goes, recipe `coupe` or `revelation-lumiere`. A component building up under the verb: `forme` or `capture` with `panneau-pose` or `empilement`, 0.25 to 0.5 s after the verb (**convention**).

---

## 4. The component taken out of the screen

This is the signature move of this kind of film, and it does not exist in the measured keynotes (where the screen stays whole, `elements.md` § 11).

**What gets taken out.** In B, in order: a list row (avatar + name + age), a settings card (title + subtitle), a "most used" card (icons + durations), a chart card (bars per day), three action buttons, a date picker (wheel), a primary button, an icon grid with checkboxes, a chat bubble with two buttons, a toggle, a day picker, a time wheel, a list of categories to check. In A: a row of icons, editing tracks, a text box with handles, a grid of pads.

**How.**
1. **The full screen first**, on its device, 1 to 3 s (B: 0:16 → 0:19; 0:29 → 0:30; 1:30 → 1:31; 1:54 → 1:55). We know where the component comes from.
2. **The component comes to the front**: it grows (×2 to ×4: the list row goes from 6 u to 20 u tall), **the screen behind blurs** and fades (B, 0:20 → 0:23: screen blurred σ ≈ 0.7 u, component sharp). The other components of the same screen can unfold in turn, offset in depth (B, 0:24 → 0:28: four cards spreading apart).
3. **It is operated**: the verb's action happens on it. The wheel turns to the right value (B, 0:36 → 0:37), the boxes get checked one by one while the grid scrolls (0:46 → 0:50), the toggle flips, the days light up (1:34 → 1:35), the time changes (1:36 → 1:37). **One action per component.**
4. **Back to the full screen**, or cut to the next one (B: 0:29, 0:43, 1:30, 1:54).

**Settings (conventions, 2 films).**
- Enlargement: ×2 to ×4; a card is no wider than 60 u.
- Background under the component: the chapter color (§ 6), or the blurred screen (σ 0.5 to 0.8 u, never sharp, never black).
- Entry: `panneau-pose` (0.36 s) when it comes from an edge; scale + position (`zoom-detail`, 0.6 to 1 s) when it comes out of the screen.
- Components keep their **real proportions, fonts and colors**: nothing is redrawn. They come from interface exports (Figma, ×2 screenshots), cut out one by one.

**Don't.** Take out two components at once (P5). Redraw a component "nicer" than in the product: the proof only counts if it is the real one. Keep a device frame recognizable as a brand's (use a rounded-corner panel). Show personal data: use demo data and made-up first names.

**With the engine.** One `capture` per component (a cut-out PNG), `zoom-detail` or `panneau-pose` on entry, `assombrir-autour` with `flou` on the background screen. The action (wheel turning, box getting checked) is **outside the recipes**: two images of the component (before, after) and a cut between them, or a small hand-written script (`courbes.md` § 7). Say so in the plan.

---

## 5. Shapes that act (film B)

- **One shape = one person** (or a moving object: message bubble, window, block). Gradient spheres, 8 to 25 u, five product colors. They **move** (slide, roll, hide behind a screen, regroup). They don't deform, except for a brief squash when one of them is blocked (2:01 → 2:03: the sphere becomes a half dome).
- **They enter the interface**: the sphere becomes the row's avatar (0:21), hides behind the blurred screen (0:40 → 0:42), comes back in front of the component (1:05 → 1:08).
- **They set the tone**: bubbles dancing for "chat" (0:05), fast trails for "play" (0:06 → 0:07), scrolling behind a window for "scroll" (0:08 → 0:10), falling snowflakes for "fall asleep" (1:56 → 1:57).
- **Duration**: 1.5 to 3 s per situation in the opening (cuts at 4.8, 6.4, 8.0, 11.0 s), 5 to 12 s when they go with the voice.

**Don't.** Drawn characters (faces, bodies): the shape is enough, it has no age and no gender. A shape that bounces in a loop or floats (P7, P9). Shapes in a color the product doesn't have.

**With the engine.** A round `forme` with a gradient (two theme colors), a `nul-camera` parent for the moves, `camera-travelling`; end regroupings with `coupe` or `produit-entree`. Deformations are not in the engine: a convention to write by hand, or to avoid.

---

## 6. The background changes with each chapter (film B)

The background is not neutral: it **names the chapter**. Logged on B (median color of the edges):

| time | background | chapter |
|---|---|---|
| 0:00, 0:16, 1:54 | light gray `#dddce1` | the app, full screens |
| 0:05, 1:56 | night purple `#140048` | the conversation, the night |
| 0:06, 1:05, 1:43 | dark green `#08473f` | games, apps, the evening |
| 0:08, 1:39 | pale green `#cfdcd2` | school, the schedule |
| 1:17 | indigo `#2e077e` | contacts |
| 1:24 → 1:28 | lavender → red `#c44851` | the alert on an image |
| 1:47 → 1:51 | pale blue → blue `#86bcd6` | the break, the rain |
| 2:08 | black | the end, the name |

- **23 background changes in 2 min 13**, all **by cut** or by a **color wipe** crossing the frame (1:24 → 1:28: the red rises from the bottom in 2 s). Never a cross-dissolve between two backgrounds.
- Components keep their light background: the film's background changes, not the interface.
- Film A never changes background (black, 30 s): with music only, the rhythm comes from the verbs.

**With the engine.** `fond` with a theme `couleur`, recipe `coupe` at each chapter. The color wipe is outside the recipes (convention: a rect `forme` rising, a repurposed `phrase-par-le-bas`, or a cut).

---

## 7. What to collect for this kind of film

On top of the intake in `SKILL.md` § 1:

1. **The list of arguments**, in business order, one per line: *verb + object* (what the user does), and the **proof** (the component that shows it). Without a component, the argument does not go into the film: it goes into the end sentence, or it is dropped.
2. **The components**, one file per component, cut out from the screens (Figma: one export per frame, ×2; screenshot: cut-out), with the full screen each one comes from, in demo data.
3. **Two states per operated component** (before, after): box empty and checked, toggle off and on, wheel on the old and the new value.
4. **The promise** in one line (6 words at most), and the **end sentence** if it differs; the **price** or the call to action, if there is one.
5. **The colors**: the product's (theme), and for each chapter the background color it takes (or "the same background throughout").
6. **The sound**: supplied music (the verb rhythm follows its beats: convention) or voice-over (spoken text, and then one shot per sentence), or nothing.
7. **The shapes**: wanted or not; if so, what they stand for (a person, a flow), and which product color they inherit.

What is missing stays visible: an argument with no component is marked `[COMPONENT TO PROVIDE]` and shown as a neutral placeholder; a promise that was not supplied is proposed and marked "TO VALIDATE".

---

## 8. Limits of this guide

- Two films, one per register (music only; voice-over). The "N out of M" counts of the other guides don't exist here: everything is a convention backed by these two cases, and is stated as such in the plan.
- Component actions (wheel, checkbox, toggle) and shape deformations **are not in the engine**: do them by hand, or with two images and a cut.
- The beat durations in A depend on a specific piece of music. On other music, syncing the verbs to its beats is a convention.
- Both films are 16:9. In 9:16, components taken out of the screen fill the full width (convention).
