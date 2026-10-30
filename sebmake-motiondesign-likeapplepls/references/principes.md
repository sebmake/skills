# Principles of the observed motion

This file says **why** an element is animated a certain way, and what is never animated. Each principle carries its counts ("N out of M") and its reason: what happens in the viewer's eye. The recipes and the values to put in the script are in `elements.md`; the curves are in `courbes.md`.

**The corpus.** 8 keynotes, from 2019 to 2026, as 960 × 540 video at 29.97 frames per second, without sound. Two were live (2019), six were prerecorded (2020 to 2026). Four families were measured frame by frame:

| family | instances kept | what it covers |
|---|---:|---|
| text | 145 | title, sentence, kicker, list, word that changes, number, film card, exit |
| objects | 122 | camera push-in, rotation, floating, exploded view, light that sweeps or reveals, parallax, motion blur |
| interfaces | 189 | panel, zoom into a screen, scrolling, screens in a row, scrim, background blur, move from one screen to the next |
| transitions | 182 (and 8,861 cuts counted) | cut, fade, dip to black, match cut, camera, light, end name and end card |

**Reading this file.**
- "N out of M": N instances out of the M in the family.
- **Convention**: a choice made by the skill, not a measurement.
- Distances in % of frame height (% H). 1 % H = 10.8 px in 1080p.
- "10–90": time between 10 % and 90 % of the move. "Visible" or "0–100": from 2 % to 98 %. "T": duration from key to key.
- This describes a grammar. No image, font, logo or sentence from the corpus is reused.

---

## 0. In short

1. **Cut first.** Only animate what must be noticed.
2. **One curve per role**: editing is linear; what crosses moves at constant speed; what arrives brakes; what lights up starts gently.
3. **Three time scales**: the gesture (0.2 to 0.5 s), the move that settles (0.6 to 1 s), the shot move (2 to 10 s).
4. **Distance sets speed, not duration.** Role sets duration, not size.
5. **One thing at a time between elements, all together within an element.**
6. **An empty beat after the cut**, then the element enters.
7. **No bounce.** Nothing overshoots its place, with rare dated exceptions.
8. **Blur comes from motion**, never on its own.
9. **What has settled stops moving.** Let people look.
10. **A film cuts while moving; a composed image settles, then holds.**
11. **Nothing spins all the way around.**
12. **One era at a time** (convention).

---

## P1. Cut first

**The rule.** The normal change of image is the cut. Animation is the exception: keep it for what the eye must notice.

**The counts.**
- Over 95 % of image changes are cuts: 1,967 cuts against 61 fades in the films (3.0 %), 6,894 cuts against 82 fades outside the films (1.2 %).
- Films cut 29.7 times per minute; the rest of the keynote, 10.2 times.
- Text is already full at the first frame of its shot in 14 titles out of 29, 6 sentences out of 12, 4 film cards out of 16.
- It exits by a cut in 15 exits out of 18.
- The graphic match cut (same shape, same place, other content) is done by a cut: 22 out of 22.
- The end name arrives by a cut in 10 cases out of 20.

**Why it works.** A cut costs the eye nothing: the information is there at once. An animation takes time and pulls the eye. If everything moves, nothing gets noticed. Keeping motion rare makes each move a signal.

**In the script.** An element with nothing to announce enters at its `inPoint` and leaves at its `outPoint`, with no keys.

---

## P2. One curve per role

**The rule.** The curve does not depend on the object. It depends on what the move does.

| role of the move | curve | counts |
|---|---|---|
| **Editing goes from one image to the next** (fade to black, card fade) | linear | fades to black 21 out of 21; short fades from black 11 out of 16; film cards, linear 3 out of 7 (best shared curve) |
| **A move crosses the shot** (camera pushing in, parallax, pivot, streak of light, sweep) | linear, from the start to the end of the shot | push-ins 7 out of 11; slide pivots 4 out of 5; parallaxes 8 out of 13; streaks of light, straight front (median r² 0.91); title sweeps 2 out of 2 measured |
| **An element arrives and settles** (entrance, pull-back, zoom, slide, panel, number, camera that stops) | braked arrival ("out" family or S curve) | side entrances 8 out of 8; pull-backs 4 out of 6; exploded-view openings 5 out of 7; screen zooms in S or "ease" 22 out of 27; screen slides 26 out of 32; rows 17 out of 19; panels 4 out of 4 measured; number scale "expo-out" 11 out of 18; title rise "expo-out" 4 out of 4; camera that stops 7 out of 7 |
| **Something lights up or goes dark** (image rising from black, slow light, scrim, title opacity) | gentle start ("in" or "in-out") | image rising from black after a cut 13 out of 14; slow light changes 4 out of 4; opacity of "fade + rise" titles in S 4 out of 4; cascading list lines 11 out of 13; scrims in S 13 out of 18 |

**What does not exist**: a slide that starts accelerating and never brakes (0 out of 32); a linear screen zoom (0 out of 27); an eased fade to black between two sequences (0 out of 21).

**Why it works.**
- **Linear editing** is neutral: it lends no intent to the image. Nobody notices it.
- **Constant camera speed** suggests a physical move that existed before the shot and goes on after it. A camera that speeds up or brakes in a short shot reads as an effect.
- **A braked arrival** gives the object mass: it slows, settles, and the eye settles with it. An arrival without braking seems to crash into its place.
- **A gentle start** mimics a light being raised: it appears without a jolt. A harsh switch-on reads as a flash.

**An element can carry two curves.** The rising title: opacity in S (T 0.77 s) and position in "expo-out" (T 0.92 s), 4 titles out of 4. The number: its opacity ends before its scale, 14 out of 18.

---

## P3. Three time scales

| scale | durations | what belongs there | observed bounds |
|---|---|---|---|
| **the gesture** | 0.2 to 0.5 s (10–90) | number opacity 0.20 s; title fade 0.35 s; card fade 0.45 s; panel 0.36 s visible; scrim 0.45 s; streak of light 0.28 s; cross-fade 0.29 s | no panel over 0.5 s (16 out of 16); no cross-fade over 1 s (25 out of 25); text fade-in under 0.94 s in 88 cases out of 91 |
| **the move that settles** | 0.6 to 1 s visible | screen zoom ×2.2 in 0.67 s; screen slide in 0.70 s; row shifting in 0.66 s; scroll in 0.73 s; blurred side entrance in 0.88 s; rising title, T 0.92 s | zooms between 0.60 and 1.00 s, 27 out of 27 |
| **the shot move** | 2 to 10 s, or the whole shot | push-in ×1.27 in 4.1 s; pull-back ×0.45 in 5.8 s; 90° pivot in 1.7 to 2.6 s; rise from black 1.6 s (10–90); camera that settles in 2.1 to 5.2 s (10–90) | shots of 10 to 25 s in continuous motion, without a cut (3 cases) |

**Why it works.** A gesture under half a second does not delay reading: the text is readable almost at once. A move that settles in under a second can be followed without waiting. A shot move of several seconds is slow enough not to read as a move: it only gives the image life.

---

## P4. Distance sets speed; role sets duration

**Distance does not change duration.** From 27 to 138 % H, the move that settles lasts 0.66 to 0.73 s (medians of three interface families). Speed goes up instead: from 105 to 467 % H/s at its peak.

**Size does not change duration.** The hero number, very large (30 to 50 % H), fades in 0.20 s; a title in 0.35 s; a film card in 0.45 s; the end name in 0.65 s.

**The closer to the object, the slower.** Pull-back that reveals the object: 1.4 to 5.7 % scale per second (4 cases). Held image that drifts: ×1.02 to ×1.06 in 5 to 8 s (3 out of 7). Camera flights between two places: 10 to 48 % H/s (5 cases).

**Why it works.** A fixed duration keeps the film's pulse: each move takes the same time and the eye learns the rhythm. Duration follows role: the number **hits**, the card **is read**, the name **closes**. Close to the object, a fast move would lose the detail being shown.

**Reading convention.** A scroll stays readable if its peak speed stays under 250 % H/s (based on 27 scrolls: median 168, upper quartile 253).

---

## P5. One thing at a time between elements; all together within an element

**Between elements: one after another.**
- Two screens in a row never arrive at the same time: 11 sequences out of 11. Median gap 1.67 s.
- A number's label arrives after it: the middle of its fade comes +0.23 s after the number's (15 out of 18, from 0.19 to 0.30 s); it fades in 0.27 s (10–90, ease-in-out, 15 out of 15).
- The end name has a shot of its own (plain background) in 16 cases out of 20.
- A camera push never changes direction within its shot (0 out of 17): one shot, one move.

**The exception: the cascade.** The lines of a list start every 0.05 or 0.10 s, while each one fades in 0.42 to 0.72 s. They overlap a lot (5 lists out of 5). The kicker arrives with its word: 8 cases out of 11, within 0.06 s.

**Within an element: the properties move together**, each with its own duration. Opacity and position for a title; opacity, scale and blur for a number; scrim, background blur and highlight for a spotlight; push and drift for a camera (median translation of 25 % H during a push-in).

**Why it works.** The eye follows one point at a time. The gap between two elements sets the reading order: first the number, then what it counts. The cascade reads as one block lighting up from top to bottom: the gap is too short to read each line separately; it only gives a direction. Within an element, properties split in time would look like several moves.

---

## P6. An empty beat after the cut

**The rule.** Cut to the empty background, then the element enters.

**The counts.**
- The empty background holds 0.13 to 0.23 s before the elements enter (medians of 6 keynotes, 135 cases). It is counted up to the first visible trace: the gentle start of an S-curve opacity (0.04 to 0.13 s before 2 %) is part of it.
- An object pivot starts 0.2 to 0.3 s after the cut (2 out of 2).
- A chip lights up 0.2 to 0.4 s after the cut (4 out of 4).
- In a film, light arrives 0.9 to 4.6 s after the cut (4 out of 4).
- **Only exception**: the blurred side entrance of a product starts on the cut (8 out of 8). It is fast enough to make the cut on its own.

**Why it works.** After a cut, the eye has to find the frame again. If the element is already moving, part of the move is lost. The empty beat clears the space; the element enters a frame that has already been read.

---

## P7. No bounce

**The rule.** Nothing overshoots its final place. Nothing oscillates around it.

**The counts.**
- No oscillation: 0 out of 145 texts, 0 out of 14 floats, 0 out of 56 screen transitions, 0 out of 18 scrims, 0 out of 37 dip-to-black fades.
- No overshoot over 3 %: 0 out of 17 push-ins, 0 out of 17 rotations, 0 out of 8 side entrances, 0 out of 13 parallaxes, 0 out of 19 rows, 0 out of 27 screen zooms (1.1 % at most).
- Simple overshoots (one way out, one way back), rare:
  - +5 % scale for the 2020 numbers (6 out of 6), absent in 2025-2026 (0 out of 18);
  - a card that rises: +6 % (1 panel out of 4);
  - a scroll: +7.4 % (1 out of 27);
  - an exploded view at +3.9 % (1 out of 15, within the measurement margin).
- The only clear overshoot is **in light**: a chip lights up above its final value, then drops back (3 reveals out of 12, +11 to +28 % luminance).

**Why it works.** A bounce adds a second move after the information has arrived: the eye waits for it to stop. It also gives a toy-like, elastic tone that makes the object feel light. A clean, braked stop says the object is sure of its place.

**In the script.** By default, no key goes past its final value. The 2020 overshoot stays possible if the user picks that era; it is set with a third key (see `courbes.md` § 4).

---

## P8. Blur comes from motion, never on its own

**The counts.**
- **Motion blur**: on fast side entrances, the trail matches a shutter of about 120° (median 118°, from 74 to 169°, 9 entrances). Also visible on screen slides (10 out of 16 examined).
- **Scale blur**: the number that starts too large is blurred (over 6.7 % H in 12 cases out of 18), and the blur clears as it settles. No number is blurred without a zoom (0 out of 27).
- **Depth blur**: the background is slightly blurred (median σ 0.34 % H, 14 cases), almost always with a dark scrim (10 out of 14). At this level, the background stays recognizable.
- Never: a "style" blur on a still object, or blur on a slow move.

**Why it works.** Blur is what a camera sees of a fast object. It makes motion believable and soft. Without motion, blur reads as a focus error. The blurred background mimics focus on the foreground element: it stays light so people still know where they are.

**In the script.** Motion blur: turn on layer and composition motion blur, 120° shutter. Scale blur: a Gaussian blur that follows the scale. Background blur: small, and always with the scrim.

---

## P9. What has settled stops moving; let people look

**What does not move.**
- **The levitating product**: it moves less than 0.3 % H in 2 to 18 s (10 holds out of 13), less than 1.6 % H in 12 out of 13. No floating oscillation (0 out of 14). The levitation comes from the shadow, the reflection and the camera moving around, not from the object.
- **Exiting text**: no exit moves, shrinks, grows or blurs (0 out of 18).
- **The end name, the film card, a number's label**: they fade in place. Name: less than 1.1 % H of movement in 18 cases out of 20. Cards: 7 out of 7. Labels: no movement measured, 24 cases out of 27 after the number.
- **The final card**: held still for 4 to 50 s (median 21.5 s, 7 keynotes).

**Time to look, after the move.**

| after | median hold |
|---|---|
| a zoom into a screen detail | 7.2 s (lower quartile 2.5 s) |
| an object pivot | 6.5 to 8 s |
| an open exploded view | 3.5 to 7.7 s |
| a hero number | 3.0 s |
| a title or a sentence | 2.0 to 3.1 s |
| the end name | 2.6 s |
| a scrim | 2.3 s |
| a scroll | 0.9 s |

**Why it works.** Motion announces; stillness lets people read. A still object in the center says it is the subject. An object floating in a loop reads like a screensaver and pulls attention away.

---

## P10. A film cuts while moving; a composed image settles, then holds

- **In a film**, motion fills the shot. It starts less than 0.25 s after the cut (9 push-ins out of 17, 12 parallaxes out of 13) and is still moving at the next cut (9 push-ins out of 17, 11 parallaxes out of 13).
- **In a composed image** (a slide, a built full frame), the move settles, then the image holds: pivot held 6.5 to 8 s; exploded view held 3.5 to 7.7 s; screen detail held 7.2 s.
- **Between two sequences**, dip to black: 0.5 s linear fade, black held 0.4 to 0.5 s, 0.5 s fade (6 sequences out of 7 in the keynote that uses it most). Or cut to the empty background of the next image (135 cases).

**Why it works.** A move that continues through the cut links the shots: the film flows. A move that settles invites reading. Pick one or the other based on what the image must do: carry along or show.

---

## P11. Nothing spins all the way around

**The counts.**
- No full turn: 0 out of 17 rotations. Largest angle: 160°.
- An object pivot goes from profile to front, a quarter turn (90°), in 1.7 to 2.6 s, at constant speed (30 to 42 °/s, 3 clean cases). It ends facing front (4 out of 4). No pivot beyond a quarter turn (0 out of 7).
- No text rotates (0 out of 145).
- The camera barely rolls: 0.2 °/s median over 309 moving shots. No rotation during a screen zoom (27 out of 27).

**Why it works.** A full turn shows off the 3D, not the object. A quarter turn that ends facing front presents the object the way you hand something to someone. Rotating text can no longer be read.

---

## P12. One era at a time (convention)

Two styles follow each other in the corpus.

| | 2019-2020 | 2024-2026 |
|---|---|---|
| screen curve (zoom, slide, row) | `cubic-bezier(0.36, 0, 0.25, 1)`: starts gently, settles gently (21 instances) | `cubic-bezier(0.60, 0.40, 0.17, 0.95)`: starts already moving, brakes hard, long tail (56 instances) |
| hero number | grows from 0.2 of its size, overshoots by 5 % (6 out of 6), or drops from above | starts 2 to 8 times too large and blurred, settles without overshoot (18 out of 18) |
| list | lines rising from below, already opaque, every 0.37 s (4 out of 4, 2020 only) | fade + rise cascade, every 0.05 or 0.10 s (5 lists) |
| title | cut, or growth from a point | cut, or fade + rise identical to the hundredth (3 titles out of 4) |

**Convention.** Pick one era for the whole film and stick to it. Default: 2024-2026. The 2019-2020 style gives a calmer look on screens and a more playful one on numbers.

---

## 13. What is never animated

| gesture | seen | base |
|---|---:|---|
| counting number (counter, rolling digits) | 0 | 27 numbers + 2 numbers that change |
| bounce, oscillation around the final place | 0 | 145 texts, 14 floats, 56 screen transitions, 18 scrims |
| rotating text | 0 | 145 texts |
| typewriter, letter by letter at a fixed rate | 0 | 145 texts (letters are only revealed by a soft-edged sweep: 3 titles and 1 value) |
| word by word at a fixed rate | 0 | 3 built cards, all by meaning groups, 0.6 to 2.5 s apart |
| title or sentence that slides in from the side | 0 | 41 titles and sentences |
| animated text exit (motion, scale, blur) | 0 | 18 exits |
| kicker animated alone, before its word | 0 | 13 kickers (only one early, pushed by the layout) |
| box or banner created to hold text | 0 | 145 texts |
| text fade-in longer than 1 s (10–90) | 3 | 91 fades measured; all 3 come from a single slide |
| word that morphs into another (letter morphing) | 0 | 14 words that change |
| product floating up and down | 0 | 14 floats |
| full turn; pivot beyond 90° | 0; 0 | 17 rotations; 7 pivots |
| camera push that overshoots or changes direction | 0 | 17 push-ins |
| streak of light that passes again, or goes down | 0; 0 | 11 fronts |
| blur without motion | 0 | 27 numbers; no still object blurred |
| linear screen zoom, or with rotation | 0; 0 | 27 zooms |
| vertical screen slide; slide that starts accelerating and never brakes | 0; 0 | 32 slides |
| two screens arriving at the same time in a row | 0 | 11 sequences |
| scrim that goes all the way to black | 0 | 20 scrims (73 % at most) |
| panel that takes more than half a second | 0 | 16 panels |
| cross-fade longer than 1 s | 0 | 25 cross-fades |
| black shorter than 0.40 s between two fades | 0 | 25 blacks |
| graphic match cut done by a fade | 0 | 22 match cuts |
| end name that slides or rises as it enters | 0 | 20 names |
| eased fade to black between two sequences | 0 | 21 fades to black (all linear) |
| fade to white between two sequences | 0 | all of the show control (the white flash exists, in films only) |
| wipe, page effect, transition zoom between two sequences | 0 | 181 candidates measured; one wipe, one iris and one sign-shaped mask exist, at the opening or the end only (**convention**: keep them for endings) |

---

## 14. What these principles do not say (conventions)

- **Music.** The videos have no sound: no link between a move and a musical beat is measured. Syncing entrances to music is a convention.
- **9:16 and 1:1 formats.** Neither is observed. Distances in % H carry over by convention into u, 1 % of the short side: 10.8 px in 1920 × 1080 as in 1080 × 1920 or 1080 × 1080. On the same phone, text then keeps its size when the image is rotated.
- **How strong the motion blur of screen slides is**, focus that shifts, the gap between the pieces of one exploded view: not measured.
- **Pure motion design films** (flying windows, fans): several moves stack up; 15 measurement attempts out of 16 were discarded.
- **Hidden start values**: a move that starts under a fade is not visible before 20 % opacity; its start is extrapolated.
- **The number's starting blur** beyond 6.7 % H: that is the measurement limit, not a value.

- **Feature videos** (component lifted out of the screen, shapes that play, background per chapter): two films studied in 2025-2026, no "N out of M" counts; see `film-fonctionnalites.md`, everything there is convention.

## 15. Limits of the corpus

- Compressed 960 × 540 video: moves under 0.1 % H blend into noise.
- The two 2019 keynotes show the slides on the stage screen, filmed by a camera: fewer instances, noisier measurements.
- Many moves are cut mid-way by the edit: their full duration cannot be observed, only the visible part.
- The "holds" in demos follow the presenter's speech: they are orders of magnitude.
