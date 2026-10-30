# Editing grammar, family by family

This file says how to edit a film the way keynote films are edited. It is used twice:

- for the **edit plan**: choose the family, the form, the position and length of each beat;
- for the **review**: understand why a measurement deviates, and which editing move fixes it.

Each rule carries its count ("N out of M") and its reason: what happens in the viewer's eye or ear. The values the scripts read are in `cibles/` and `scripts/gabarits.json`; the file format, in `montage-spec.md`; how to read a review report, in `critique.md`.

## Contents

1. Reading this file
2. Choosing the family
3. The common core (G rules)
4. Product and reveal (P rules)
5. Opening and mood, with sketches, fictions, closing films, transitions (A rules, for ambiance)
6. Documentary and testimonial (T rules)
7. Trailer and usage (BA and U rules)
8. Sound: voice, music, silence
9. Length, format, color
10. What is never taken
11. Observed or convention: the summary

---

## 1. Reading this file

**The corpus.** The films of 8 keynotes, from 2019 to 2026. Each film was broken down shot by shot (cuts by calculation, dissolves and shot sizes checked by eye). Speech comes from the subtitles. The sound track was measured for only two families (opening, documentary).

| Family | Films | What was measured |
|---|---|---|
| Product and reveal | 16: 7 object reveals, 4 software films, 3 materials films with voice-over, 2 usage and product range films | 213 picture shots, 234 transitions, size of each shot; no sound |
| Opening and mood | 20: 8 openings (3 of them sketches or fictions), 2 thresholds, 1 tribute, 3 closing films, 6 transitions between two places | 367 shot changes in the openings, 453 cuts compared, sound track |
| Documentary and testimonial | 8, plus 2 variants without interviews | 596 picture shots, 606 transitions, type and size of 744 shots, 107 speech turns, sound track |
| Trailer and usage | 8: 6 trailers, 2 usage films | 657 shots logged by eye, 459 transitions, 108 spoken lines; no sound |

The same film can serve two families: a closing film made of testimonials is counted in opening and in documentary.

**Marking.**

- **observed N out of M**: seen in N cases out of the M of the stated basis;
- **convention**: not measured, or too few cases. It is a choice made by the skill, to apply as is;
- **weak**: observed, but in 1 to 3 cases. Worth following, not imposing.

"Why" gives the reason for a rule. It is a reading of what the viewer does, not a measurement.

**The IDs.** The rules in this file are written G (common core), P (product), A (opening and mood), T (documentary and testimonial), BA (trailer) and U (usage). The review report has its own check IDs (C, K, O, D, B); `critique.md` says which rule each one points to.

**The words.** Picture shot: a shot that shows a picture (not a black, not a title card). Median shot: the length of the middle shot when they are sorted from shortest to longest. Third: the beginning, middle or end of the film, each one third of the length. Peak: the passage where the shots are shortest. Shot size: detail, tight, medium close, medium, whole (the whole object), wide.

---

## 2. Choosing the family

The family depends on **the footage**, not on what you'd like (convention). No filmed interviews, no documentary. No whole object filmed, no reveal.

| The footage… | Family | Form (`schema` in `montage.json`) |
|---|---|---|
| shows a new object: material, parts, details, and a shot of the whole object | Product and reveal | `revelation_tardive` |
| shows software, a use or a range of colors | Product and reveal | `objet_des_le_debut` |
| sets a mood, a place, a moment; or plays a short scene | Opening and mood | `ouverture` |
| goes from one place to another, moving forward | Opening and mood | `transition_decor` |
| runs through faces and reactions, to close an event | Opening and mood | `cloture` |
| calm interviews, few voices, and shots of their work | Documentary and testimonial | `pose` |
| many short voices, videos filmed by people, reactions | Documentary and testimonial | `choral` |
| a single story, with spoken lines | Trailer and usage | `oeuvre` |
| several topics to announce, each with a title | Trailer and usage | `catalogue_blocs` |
| several topics, with no titles to show or no speech | Trailer and usage | `catalogue_mele` |
| people using an object, in context | Trailer and usage | `usage` |

If two families fit, ask the user (convention). A film follows a single form: don't mix the late reveal and the object from the start, or the calm regime and the ensemble regime.

---

## 3. The common core (G rules)

What the four families share. A family rule wins over a G rule when they differ.

**G1. Hard cut.** The hard cut is the normal shot change.
- Product: 194 transitions out of 234 (83%). Opening: 359 out of 367 (98%). Documentary: 594 out of 606 (98%). Trailer: 423 out of 459 (92%). Usage: 164 out of 171 (96%).
- *Why:* a cut costs the eye nothing, the picture is there at once. A dissolve takes time and gets noticed. If everything dissolves, nothing gets noticed anymore.

**G2. One cross dissolve at most, at a chosen moment.**
- Product: 7 out of 234, 5 of them doubtful; the 2 seen clearly lead into a key shot (the name, a first face). Opening: 1 clear one, at 94% of the film, from animation to live action. Documentary: 1 out of 606, never between two speech shots. Trailer: 8 out of 459, 6 of them a title giving way to the picture.
- Exception: a sung music video dissolves 9 changes out of 16, in short dissolves of 0.17 to 0.33 s (1 film, weak).
- *Why:* the dissolve says "we're moving from one world to another". Kept rare, it keeps that meaning.

**G3. Black opens.** You enter the film through black.
- Product 13 out of 16 (median 1.1 s). Opening: a threshold of black or a title card 6 out of 8. Documentary 6 out of 8. Trailer 7 out of 7 measurable (median 0.6 s).
- Elsewhere, black changes role by family: rare and short in product, at the entry only in opening, at chapter changes in documentary, as punctuation at the end in trailer.
- *Why:* black wipes out what came before. The eye adjusts to the screen before the first picture.

**G4. Everything moves, except what has to be looked at for a long time.**
- Still shots (motion under the corpus threshold): product 14 out of 197 (7%), opening 30 out of 351 (9%), trailer 29 out of 384 (7.6%), transitions between two places 0 out of 33.
- Two clear exceptions: the interview, locked-off camera in 18 of the 20 shots looked at; the photos of a tribute, still in 22 out of 22.
- *Why:* motion keeps the eye active. A talking face or a photo reads better when still: the meaning is in what you see, not in the camera.

**G5. One long shot holds the film**, except in the trailer.
- A shot of at least 5 s: product 14 out of 16; edited openings 7 out of 7; calm documentary 5 out of 5, in the last fifth.
- Trailer: the longest shot runs from 1.8 to 5.1 s depending on the film. Its long beat is the final title (§ 7).
- *Why:* after short shots, a long shot leaves time to understand. It marks the reveal, the arrival, the ending.

**G6. Text is rare, small, centered, with no box, and alone.**
- Product: 0 explanatory title cards and 0 figures in 16 films; a single line in the whole corpus of the family (5 words).
- Never two texts on screen at once: 0 out of 16 product films; one block at a time in 8 out of 8 trailers and usage films.
- Documentary message title cards: centered 6 out of 6, 5.2 to 5.7% of the image height (5 out of 6). Name lower thirds: no box (8 people seen up close).
- Opening: text at the threshold or at the end, never in the middle (0 out of 7).
- *Why:* text stops the picture. A few words, placed in empty space, can be read without leaving the film.

**G7. The title card stays long enough to be read.**
- Opening: about 0.5 s per word (median of 7 title cards; 0.32 to 2.09 s per word).
- The sister skill `sebmake-videopresentation-likeapplepls` sets the floor: **1.2 s + 0.3 s per word** (convention fitted on 109 title cards). A 6-word line therefore holds at least 3.0 s, which matches the opening's 0.5 s per word.
- Short cases observed: trailer block title 1.0 s median; punch word of 1 or 2 words, 1.0 to 2.3 s; name lower third 2.1 s median.
- *Why:* a title card you haven't finished reading leaves an unease that spills over the next shot.

**G8. Music carries the big changes, not every cut.**
- Cutting on a sound attack: not shown. Product film (sister skill): 16 cuts out of 62 within ± 70 ms of an attack, against 16.4 expected by chance. Documentary: 363 cuts out of 597, against 361.5 by chance. Opening: clear in 1 film out of 11 (a photo montage), weak in 2, absent in 8.
- What music does: it starts from calm (opening 4 out of 8 start from silence; documentary 8 out of 8 open below their median level) and peaks after 60% of the length (opening 7 out of 8).
- *Why:* cutting on every beat feels mechanical. The films follow the music through the exit from black, the peak, the reveal, the name.

**G9. A match cut is placed, not repeated.**
- Across 453 opening cuts, a shot's composition resembles the next shot's as much as a random shot's (median 0.05 against 0.06).
- Match cuts exist, but at chosen places: on action in 12 product films out of 16; on shape in 3 product films out of 16; no visual match in 17 documentary cuts out of 48 (the voice makes the link).
- *Why:* a match cut gets noticed. At every cut, it becomes a tic.

**G10. Ending: hold, or close sharply.**
- Hold: product ends on the whole object held (13 out of 16, median 7.4 s); opening on a wide shot that lands (6 out of 8 of at least 5 s); calm documentary on a held shot (5 out of 5).
- Close sharply: the trailer speeds up then stops on its title (8 out of 8); the ensemble documentary ends with a burst then a logo (3 out of 3).
- *Why:* the ending is what you take away. A held shot lets the picture settle; a sharp stop makes the title land.

---

## 4. Product and reveal (P rules)

**Basis: 16 films** (24 to 128 s). Without voice-over: 13 films of 24 to 51 s, median 31.9 s. With voice-over: 3 materials films, 54 to 128 s.

### 4.1 Two forms

| Form | Films | What happens |
|---|---|---|
| **Late reveal** (`revelation_tardive`) | 10 out of 16 | a world or a material, then details, then the whole object around 77% of the length |
| **Object from the start** (`objet_des_le_debut`) | 5 out of 16 | the whole object between 1 and 18% of the length, then its uses or features, then a range or the name |
| Object never whole | 1 out of 16 | software shown through gestures on the screen; the name closes |

### 4.2 The beats of the late reveal (10 films)

| Beat | What we see | Measurement |
|---|---|---|
| Opening | black, then a picture is born | opening black 7 out of 10 |
| Hook | a setting or a landscape (6 out of 10); a material, a part, an edge of light (4 out of 10) | first picture shot 3.3 s median (quartiles 2.3 and 7.9 s, 16 films) |
| Build-up | details, parts, making, uses, in short shots | shots of 1.25 to 3.5 s (quartiles), median 2.4 s |
| Reveal | the whole object, held | between 69 and 82% of the length (median 77%); shot held 4.9 to 9.0 s (median 8.0 s) |
| Name | written on a title card, if it is written | between 83 and 96% (median 94%), 1.3 to 4.5 s (median 2.4 s) |
| Ending | the whole object held, then nothing, a black or the name | last picture shot 7.4 s median |

### 4.3 The rules

**P1. Choose the form by what you show.** A new object is kept for the end (late reveal, 10 out of 16). Software, a use, a range are shown right away (5 out of 16).
*Why:* the reveal lives on curiosity. When the subject is what you do with the object, hiding it brings nothing.

**P2. Length: short.** Without voice, 24 to 51 s (median 31.9 s, 13 films). With a materials voice-over, 54 to 128 s (3 films). The sister skill counts up to 68.5 s with other bounds: same conclusion, a product film without voice stays short. Past 60 s without voice: chapters of one idea each (convention).
*Why:* without voice, the film rests on a single expectation. It wears out fast.

**P3. Open on black, then let the picture be born.** Opening black 13 out of 16, 0.3 to 1.6 s for 9 out of 13. The picture comes out of black through a fade (0.7 to 1.3 s) or through light in 8 out of 16.
*Why:* a picture being born sets the calm. The viewer is in before anything happens.

**P4. First shot: a world or a material, never the whole object** in a late reveal (0 out of 10).
*Why:* showing the whole first gives away the ending.

**P5. Go tight in the build-up.** Details and tight shots: 70% of shots in the first third, 65% in the middle, 48% in the last (201 shots).
*Why:* the object seen in pieces makes you want to see it whole.

**P6. Pacing: 2 s shots, a fast passage early.** Median picture shot 2.17 s (213 shots; p10 0.73 s, p90 7.16 s). A passage of about 5 shots at 1.2 s, in the first half for 8 films out of 11. No rule of speeding up to the end: 9 films speed up in the second half, 5 slow down, 2 stay steady. No peak just before the reveal (the 3 shots before it are shorter than the median in only 6 out of 10).
*Why:* the energy comes while you discover the parts. Then the film slows down to let you see the whole.

**P7. Hard cut; the dissolves go to black.** 83% cuts. Fades to and from black: 9% together. No fade from black in the last third (0 out of 10): black that opens belongs to the start.

**P8. Link the shots through motion.** A gesture, a rotation, a descent that carries on from one shot to the next: 12 films out of 16. The shape match stays rare (3 out of 16), kept for a moment.
*Why:* the eye follows the motion and does not see the cut.

**P9. Software: go into the screen**, or pull back to show that the image was the screen (3 software films out of 4). Software cuts faster: 24.3 shots per minute median (5.3 to 32.4), against 16.1 for the object reveal.

**P10. Make almost everything move.** Still images: 7% of shots. Keep them for a picture coming out of black, a wide tableau, a photo.

**P11. Reveal at three quarters.** The whole object, alone, between 69 and 82% of the length (median 77%, 10 films), in a shot held 4.9 to 9.0 s. The shot pulls back in 5 cases out of 10, rotates in 3.
*Why:* late enough for the wait to weigh, early enough to leave time to look.

**P12. Widen at the end.** The last picture shot shows the whole object: 13 out of 16. It lasts 6.0 to 8.5 s (quartiles), at least 4 s in 13 out of 16. The other 3 end on the name title card, which then plays the role of the final shot.

**P13. One shot of at least 5 s** in the film: 14 out of 16. The longest lasts 8.1 s median.

**P14. Inner blacks rare and short.** 4 films out of 16, 0.3 to 0.9 s. A long black before the reveal: 1 film out of 16, a rare effect.

**P15. The name closes the film.** Written in 7 films out of 16, between 83 and 96% of the length (median 94%), 1.3 to 4.5 s (median 2.4 s), alone, centered, on a solid background (5 title cards out of 5).
*Why:* the name is the punchline. Written earlier, it becomes a title and empties the reveal.

**P16. With no presenter, always write the name** (convention). 9 films out of 16 don't write it: in 8, the presenter says it in the second after the film; in the ninth, a voice-over. Here, nobody will say it.

**P17. Name size.** Discreet for an object (4 to 5% of the image height); hero for software (9 to 12%). 2 and 2 measurements: weak.
*Why:* the object stays the hero of its film; software has no object, so its name takes the place.

**P18. The ending: nothing, a black, or the name then a black.** After the last picture shot: nothing (5 out of 16), a black (4), the name (3), the name then a black (4). Final black of 0.1 to 2.8 s (median 0.95 s). Logo alone at the end: 0 out of 16. Date or slogan under the name: 0 out of 16.

**P19. No explanatory title card, no figure.** 0 out of 16. At most one line of about 5 words, in the center of a calm area (1 out of 16).
*Why:* the film shows, it does not explain. A figure on screen turns the film into a slide.

**P20. Voice-over only for a materials film** (3 out of 16, all materials films). It covers 61 to 69% of the time, stays silent for the first 3.9 to 4.6 seconds and the last 2.3 to 3.6 (3 out of 3). The picture of a step arrives before or with the sentence that names it: 7 out of 10, in 1 film (weak).
*Why:* the eye sees, then the ear confirms. A sentence that comes before the picture reads as a commentary.

**P21. Making-of film: follow the order of making**, from raw material to finished object, one shot per step (2 out of 16, weak).

**P22. The music carries the exit from black, the reveal and the name**, not every cut (convention: this family's corpus has no sound; see G8 and § 8).

**P23. 9:16 and 1:1 formats, chapters past 60 s without voice**: convention (no film observed; see § 9).

### 4.4 Templates (convention, from the medians)

Late reveal, 33 s:

| From → to | Beat | Content | Shots |
|---|---|---|---|
| 0.0 → 1.0 | opening | black | 1 |
| 1.0 → 4.5 | hook | a world or a material coming out of black (0.9 s fade) | 1 or 2 |
| 4.5 → 24.5 | build-up | details and parts, 1.2 to 3.5 s; a passage of 5 shots of about 1.2 s around 25 to 45% | 9 to 11 |
| 24.5 → 30.5 | reveal | the whole object, slow pull-back, held | 1 |
| 30.5 → 32.9 | name | title card alone, centered, solid background | 1 |
| 32.9 → 33.5 | ending | black | 1 |

Object from the start, 30 s: black 0.5 to 1 s; the whole object around 1.5 s (5%); 10 to 13 use or feature shots of 1.3 to 2.5 s, the object whole or in hand; a last held shot (range or use) of 5 to 7 s; the name 2.4 s.

---

## 5. Opening and mood (A rules)

**Basis: 20 films.** 8 openings of 65 to 143 s (median 99 s), 3 of them sketches or fictions; 2 thresholds; 1 tribute; 3 closing films; 6 transitions between two places.

### 5.1 The five beats of an opening

| Beat | What we see | Measurement | Count |
|---|---|---|---|
| 1. Threshold | black, or a title card on black | black alone about 1 s; title card + black 5.7 to 9.8 s | 6 out of 8 have a threshold |
| 2. First shot | a long shot that sets things up: light, detail, or establishing shot | median 6.8 s | at least 5 s: 5 out of 8 |
| 3. Body | short, steady cutting | median shot 1.33 s (p10 0.65 s; p90 3.17 s; 337 shots, 7 films) | — |
| 4. Peak | the 5 fastest shots | 0.40 to 0.73 s | between 61 and 79% of the length: 5 out of 7 |
| 5. Landing | a long shot, often wide, that leads to the place or to the person who will speak | median 7.1 s (4.3 to 18 s) | at least 5 s: 6 out of 8; at least 3.5 times the median shot: 7 out of 7 |

### 5.2 The rules

**A1. The threshold: 0.5 to 1.5 s of black and silence** (convention, on 6 thresholds out of 8). A threshold title card, if there is one: short, preferably 5 words or fewer (observed: 6 words held 1.9 s; an event title card 4.0 s; a 16-word quote 8.0 s), then 0.8 to 4.3 s of black. The sound starts from silence in 4 openings out of 8.
*Why:* the threshold separates the film from what came before. Silence makes the first note audible.

**A2. A long first shot, 5 to 10 s.** Tight (a detail, a light: 4 out of 7) or wide (an establishing shot: 3 out of 7), depending on the footage.
*Why:* the viewer needs time to get in before the cutting takes off.

**A3. The body cuts fast and steady.** Shots of 0.9 to 2.1 s (quartiles), median 1.3 to 1.5 s. 25 to 40 changes per minute (5 openings out of 7). At most 1 shot in 10 over 3.2 s; a long shot in the middle opens a scene or a chapter (6 out of 9). The body does not slow down before the landing: 1.60 s in the first third, 1.30 s in the middle, 1.24 s in the last; the first third is the slowest or equal in 6 out of 7.
*Why:* the body gives the energy. If it slows down before the end, the film runs out of breath before it arrives.

**A4. In each scene, open wide then go tight.** 8 scenes out of 11 logged. Gestures and objects in extreme close-ups of 0.5 to 1.3 s.

**A5. A peak between 60 and 80%**: 5 shots of 0.4 to 0.7 s (5 openings out of 7), on the strongest moment of the music (the sound peaks after 60% in 7 openings out of 8, median 68%). The peak is never the last shot.
*Why:* the film needs a high point. Placed at two thirds, it leaves time to land.

**A6. Land.** 3 to 5 shots that get longer (for example 0.9 → 1.2 → 1.5 → 2.5 → 2.5 → 5.0 s), then a last shot of 5 to 11 s, wide, on the place or the person who will speak. It ends on the place or the person in 6 openings out of 8. If a person speaks next, they start speaking in this shot (observed 3 out of 8; convention: continue the shot 2 to 5 s under their first words).
*Why:* the landing brings you back to the real world without a jolt and hands over.

**A7. From tight to wide over the whole film.** Last shot wide 5 out of 7, never tight (0 out of 7). Wide shots come back in the last third in 2 full films out of 3.
*Why:* you start from a detail and arrive at the place. It is the reverse of the classic establishing shot, at the scale of the film.

**A8. Hard cuts everywhere.** 359 out of 367. Dissolves with black are at the entry (6 out of 6 in the first 10% of the film). A cross dissolve of 1 to 1.5 s only to go from animation to live action (1 clear case).

**A9. Black is for entering.** 15 blacks out of 17 are in the first 11% of the film. Exception: a "cold" opening cuts up its start with two blacks of 1.5 and 1.0 s.
*Why:* a black in the middle of the body breaks the momentum.

**A10. Text: 0 to 2, at the threshold or at the end, never in the middle** (0 out of 7). About 0.5 s per word (G7). On black (4 out of 7) or in a calm, dark area of the picture (3 out of 7).

**A11. Little speech, and an ending without speech.** 0% speech in 4 openings out of 8, at most 28% in 3 (the narrated fiction goes up to 63%). The films with speech end on 15 to 33 s of music alone (3 out of 3, narrated fiction aside).

**A12. Match cuts are local** (G9). Direction of motion: keep it from one shot to the next when it is the same action (convention: not shown on 34 cuts).

**A13. Black and white for people and a mood**: 3 films out of 20, all showing people at work or portraits. Color for a high point: 1 case (weak).

**A14. One format per film** (2 out of 2). Widescreen (2.35:1 or more) says "cinema": only if the footage supports it (convention).

### 5.3 Sketch or fiction (3 films, weak)

- A scene with dialogue at the start, then action and music. In an 85 s sketch, the dialogue runs from 7 to 28 s, then 33 s without speech end the film. Convention: the spoken scene at most 40% of the film.
- Cold open (1 out of 8): an extreme close-up of 2 to 3 s, then 1 to 1.5 s of black.
- Cross-cutting between two places (1 film): the second place comes back every 7 to 20 s (median 12.8 s), for 0.7 to 2.3 s (median 1.5 s).
- Narrated fiction (1 film): 6 chapters of 14 to 29 s (median 26 s), each opened by a voice-over sentence, then the picture shows it. 25 cuts out of 62 fall during a sentence.

### 5.4 Closing film and tribute (`cloture`)

- A short opening title card (observed: 11 words, 4.7 s), then the faces.
- People's voices cover half to two thirds of the time (closing film 66%, tribute 51%). You cut while they speak: 33 cuts out of 68.
- Small name lower thirds, bottom left, **after** the first appearance: all between 29 and 77% of the film (7 out of 7, 1 film). 2.9 s per person median, over 1 to 3 shots. *Why:* show first, name afterward.
- Speed up in the last third (median shot 0.98 s), a peak around 90% (0.20 s rolling median), then a signature shot of 1.7 to 8.3 s (3 films out of 4). The user's logo if they provide it, otherwise their name (convention).
- Photos: still, on black, in their own format (25 out of 27), one per bar of music: 19 photos out of 26 last about 4 beats, 23 out of 26 fall within a quarter beat of a whole number of beats (1 film). It is the only case where the cuts follow the music's grid.
- Sung music video (1 film): change shot at the start of a line (9 out of 16, against 2.5 by chance); short dissolves allowed; end in silence on the final sign.

### 5.5 Transition between two places (`transition_decor`, 6 films)

| Measurement | Value | Count |
|---|---|---|
| Length | 11 to 31 s (median 23.9 s) | 6 |
| Motion | the camera or the subject moves forward from one place to the other, without stopping | 6 out of 6 |
| Hidden cuts | in a dark or blurred passage (door, wall, foliage, whip pan) | 4 transitions out of 6 (14 cuts out of 30) |
| Still shots, text | none | 0 out of 33 shots; 0 out of 6 |
| Pacing | lively start (0.1 to 2.4 s, often in the dark), slow arrival (4 to 14 s) | — |
| Arrival | the last shot is the longest | 4 out of 5 (the sixth is a single shot) |
| Before speech | the arrival is held 6.7 to 11.5 s (median 9.3 s) before the next person speaks, then continues under their first words | 5; 6 out of 6 |
| Music | one musical phrase for all the transitions of a film; it stops 1.2 to 1.3 s before the speech | 2 out of 2, weak |

*Why:* forward motion says "here we go". Hidden cuts give the illusion of a single journey.

### 5.6 Opening template, 90 s (convention, from the medians)

| From → to | Beat | Content |
|---|---|---|
| 0:00 → 0:01 | threshold | black and silence; or a short title card then 1 s of black |
| 0:01 → 0:08 | first shot | a detail, a light or an establishing shot, 7 s |
| 0:08 → 0:56 | body | scenes opened wide then tight; shots of 1.3 to 1.5 s; one long shot per scene at most |
| 0:56 → 1:08 | peak | 5 shots of 0.4 to 0.7 s around 62 to 70%, on the music's high point; then the body resumes |
| 1:08 → 1:22 | landing | 3 to 5 shots that get longer |
| 1:22 → 1:30 | last shot | wide, on the place or the person, 8 s; the closing text here if there is one |

---

## 6. Documentary and testimonial (T rules)

**Basis: 8 films** of 78 to 324 s (median 142 s), plus 2 variants without interviews. Shot types: interview (the person speaks, framed for it), person in context, illustration (place, object, archive, screen, work).

### 6.1 Two regimes

| Regime | Films | Median shot | p10 to p90 | Cuts per minute |
|---|---|---|---|---|
| **Calm** (`pose`): filmed interviews, one or a few voices that develop an idea | 5 | 2.0 s | 1.0 to 4.5 s | 19.9 to 27.3 |
| **Ensemble** (`choral`): many people, short images, sentences that answer one another | 3 | 1.2 s | 0.47 to 2.6 s | 32.6 to 45.1 |

### 6.2 The structure

| Part | What happens | Landmark |
|---|---|---|
| Opening | black, calm sound; a text, a voice in the dark, or images without speech | black first 6 out of 8; first speech at 6.0 s (2.9 to 16.5 s) |
| Voices come in | the voice first, over an illustration; the face afterward; the lower third on that face | 13 out of 20; face 3.0 s later (1.5 to 4.7 s) |
| Body in chapters | one idea, one person or one step per chapter | chapters of 19 to 35 s in one film |
| Breathing spaces | music alone, 3 to 9 s, over pictures | 6 films out of 8; about 0.6 per minute |
| Chapter change | a black of 0.4 to 1 s, or a white, or a title card | at most 1 black per film |
| Build | calm: through what is said; ensemble: bursts | final burst 4 out of 8 |
| Resolution | the last sentences, longer shots | calm: a shot of at least 5 s in the last fifth, 5 out of 5 |
| Ending | calm: a held shot; ensemble: a burst then the logo | last speech 4.2 s before the end (0.9 to 9.5 s) |

### 6.3 The rules

**T1. Choose the regime from the footage** and tell the user before editing.

**T2. Edit the speech first** (convention): a voice-only track, made of takes of 2 to 20 s (observed median 5.9 s; p10 1.9 s; p90 19.8 s; 107 takes). One take carries one idea (convention).
*Why:* in a documentary, speech is the spine. The picture is chosen afterward, for it.

**T3. Let it breathe.** Speech covers 77% of the film median (51 to 88%, 8 films). In a calm film, a breathing space of 3 to 9 s without speech, about one every minute and a half (6 films out of 8 have them; 0.6 per minute median).
*Why:* without silence, the viewer never has time to think about what they just heard.

**T4. Cover the voice.** You see the person speaking for a third of what they say (median 33%; under 55% in 6 films out of 8). The two exceptions are reaction and webcam films, where the face is the picture.
*Why:* the voice carries the meaning; the picture shows what it talks about. A face that talks all the time becomes filmed radio.

**T5. Bring each person in through their voice.** You hear them before you see them in 13 cases out of 20. The face arrives 1.5 to 4.7 s later (median 3.0 s).
*Why:* the voice sparks curiosity; the face answers it.

**T6. Name at the first face, discreetly.** Name and role, bottom left or right, off the face, small (2.5 to 3.3% of the height for the name), no box, 2.1 s median (0.9 to 3.5 s; 27 lower thirds), faded in after the cut (2 out of 2). 4 films out of 8 name people this way; 3 out of 8 name nobody (many short voices).

**T7. Frame the interview tight, never wide.** Across 162 interview shots: medium close 53%, medium 26%, close-up 15%, extreme close-up 6%, wide 0. Two shots in a row of the same person: the second tighter, 9 times out of 10.
*Why:* the face carries the emotion. Changing shot size between two shots of the same person avoids a jump cut.

**T8. Locked-off camera on the interview** (18 out of 20); motion goes to the illustrations and to people in context.

**T9. Cut under the voice.** 414 cuts out of 594 (70%) fall while someone is speaking. The cuts don't look for silences (172 in a silence, against 162 by chance). The voice change and the picture change are offset: they coincide within half a second in only 23 cases out of 57.
*Why:* a cut that falls right on the voice change shows. Offset, the voice pulls the picture or extends it, and the thread does not break.

**T10. Hard cuts everywhere** (98%). No cross dissolve between two speech shots. A single dip to black (0.4 to 1 s) or to white, to change chapter (3 transitions out of 3 are chapter changes).

**T11. The pacing shape.** Calm: the ending never speeds up (0 out of 5 by more than 15%); the longest shots are at the end (p90 of the last third 6.2 s, against 3.4 to 3.7 s before). Ensemble: the ending is faster than the start (3 out of 3).

**T12. A short interview shot.** 1.77 s median (p90 3.16 s, 162 shots). Over 5 s, only in the last fifth of the film (4 out of 4).

**T13. Open with black and calm.** The first 3 seconds are quieter than the film's median level in 8 out of 8 (by 9.7 to 47.8 dB, median 16.7 dB). First speech between 3 and 17 s (target 6 s).

**T14. Ending.** Calm: the last sentences, then a shot held 5.7 to 8.1 s, preferably wide (5 out of 5). Ensemble: a burst of 3 to 5 shots of 0.3 to 0.4 s showing the works or the product, **never the faces** (4 out of 4), then the user's logo if they provide it (5 films out of 8 have a logo, 2.2 to 4.2 s). The last speech falls 1 to 10 s before the end.

**T15. Bursts in the middle are allowed** (4 films out of 8): greetings in a row, the same person at several ages, reactions. There, faces are allowed.

**T16. The voice is the match.** 17 cuts out of 48 have no visual match: the voice carrying on makes the link. Place or shape repeated: 10 out of 48. Picture showing the word just heard: 4 out of 48; the illustration follows the **theme** of the sentence more than the exact word (1 film read in full).

**T17. Title cards: none by default** (3 films out of 8 have none). At most one question or thesis at the opening (2 out of 8), or 1 to 3 closing title cards alternating with the picture (1 out of 8). Small (5.2 to 5.7% of the height, 5 out of 6), centered (6 out of 6), 3 to 12 words. Echo words (a word the person just said, shown large on screen): in the ensemble regime only (1 film, 10 words out of 10 repeat a word heard). A letter typed on screen: only if the film is about something written (1 out of 8).

**T18. Black and white for a portrait.** The 4 black-and-white films, variants included, are portraits of people and trades. Mixing allowed: people in black and white, screens and works in color (2 out of 8). 2.39:1 letterbox only for a film entirely in black and white (1 out of 8, convention).

**T19. No figure on screen that is not said by a person in the footage.** No invented testimonial, name or role.

### 6.4 Calm template, 2 min (convention, from the medians)

| From → to | Part | Content |
|---|---|---|
| 0:00 → 0:06 | opening | black, calm sound; images without speech, or a question of 12 words at most |
| 0:06 → 0:09 | entry | the first voice over an illustration |
| 0:09 → 0:40 | chapter 1 | the face (lower third 2.1 s); the voice moves to the illustrations two thirds of the time; shots of 1 to 4.5 s |
| 0:40 → 0:46 | breathing space | music alone over pictures, 6 s |
| 0:46 → 1:28 | chapter 2 | opened by a 0.5 s black or by a second person's voice |
| 1:28 → 1:46 | resolution | the last sentences; longer shots |
| 1:46 → 2:00 | ending | last speech 4 s before the end; a wide shot held 7 s |

Ensemble, 90 s: same opening; short voices of about 1.9 s, sentences passed from one person to the next; 1.2 s shots, shorter at the end; final burst of 3 to 5 works at 0.3 or 0.4 s around 90 to 97%; logo 3.5 s.

---

## 7. Trailer and usage (BA and U rules)

**Basis: 6 trailers** of 50 to 119 s (median 89.2 s): 2 for a single work, 2 catalogs by blocks, 2 mixed catalogs. **2 usage films** (60.0 and 93.5 s): the usage rules rest on 2 cases, they are fragile.

### 7.1 The six beats of a trailer

| Beat | Position | What happens | Count |
|---|---|---|---|
| Opening black | 0 to 1% | 0.13 to 4.2 s (median 0.6 s) | 7 out of 7 measurable |
| Hook | 0 to 20% | a spoken line in the first seconds, situation shots, many wide shots | spoken line 4 out of 5 with speech; wide shots 6 out of 6 |
| Announcement | 15 to 25% (catalog); 29 to 45% (work) | catalog: punch words, a line or a logo; work: one or two credit title cards | 3 out of 3; 2 out of 2 |
| Body | 25 to 78% | catalog: blocks opened by their title; work: the story in spoken lines | — |
| Peak | 78 to 88% | shortest shots, less speech | 6 out of 6 |
| Closing | 83 to 100% | black, a last spoken line (the "button"), black, title or logo | 8 out of 8; button 4 out of 6 |

### 7.2 The trailer rules

**BA1. Choose the subform** (§ 2): one story = work; several topics with titles = catalog by blocks; several topics without titles or without speech = mixed catalog.

**BA2. Shorten the shots up to the peak, then stop sharply.** Median shot 1.20 s in the first third, 0.90 s in the middle, 0.77 s in the last (384 shots). Last third faster than the first: 6 out of 6; each third faster than the one before: 4 out of 6. Median picture shot of the film: 0.73 to 1.65 s.
*Why:* speed builds desire. The sharp stop makes the title land. This is not the product film's shape: the trailer reveals nothing at the end, it stops.

**BA3. The peak between 78 and 88%** (6 out of 6): the fastest 10 seconds, shots of 0.62 s median (0.41 to 1.46 s). It has little speech: 21% of the time in speech, against 48% over the whole film (4 out of 5).
*Why:* at the peak, the images go too fast to listen. The music takes over.

**BA4. Hard cuts: at least 90%** (observed 92%). The cross dissolve is reserved for text giving way to the picture (6 out of 8). The fade from black, for the button (4 out of 4) and the final title (4 out of 6). No dip to white (0 out of 459).

**BA5. Black punctuates.** 40 blacks, median 0.42 s; 21 out of 40 in the last 20%. Short (0.1 to 0.5 s) at the peak and around the button. Long (1 to 2.5 s) only between the chapters of a work (the 6 long blacks are all in the 2 trailers for a work).

**BA6. Open wide, then move closer.** Wide shots: 44% in the first third, 28% in the middle, 26% in the last; the share drops in 6 films out of 6 (39 to 56% in the first third). What rises in the middle is the medium shot: the characters in context.
*Why:* you first show where you are, then who acts.

**BA7. The voice runs over the cut.** 94 spoken lines out of 108 last through at least one cut. A line lasts 1.7 s median (p90 3.1 s) and has 6 words (p90 10).
*Why:* the voice holds the thread while the picture jumps. It is the family's central device.

**BA8. Speak half the time.** Speech: 48% median (28 to 58%, upper bound). First spoken line in the first 5% (4 out of 5). Last spoken line between 83 and 94% (5 out of 5).

**BA9. The button.** After the peak: a black, then a single spoken line over 1 or 2 shots (2.3 to 3.4 s), which comes out of black through a fade (4 out of 4), then a black and the title. 4 trailers out of 6. The music drops just before: the button plays almost dry (convention).
*Why:* after the speed, a single line makes you smile or shiver. The contrast fixes the memory.

**BA10. End on the title or the logo, never on a picture** (8 out of 8). It starts between 90 and 96% of the length and stays 3.5 s median (2.5 to 4.8 s for 7 films out of 8). It comes out of black through a fade, often into a glow (4 out of 6). The whole closing lasts 8.0 s median, 6 to 17% of the film.

**BA11. Catalog by blocks: one topic per block.** A block lasts 4.5 s median (1.9 to 7.8 s; 21 blocks) and has 3 to 6 shots. The title **opens** its block (20 out of 21) and stays about 1.0 s (0.73 to 2.27 s). 9 to 12 blocks, then a final mix of 12 to 13 s without titles. Inside a block, the cuts stay on the same topic (29 out of 32).

**BA12. Mixed catalog: topics alternate shot by shot.** 28 cuts out of 32 change topic. A graphic link helps there (a color, the position of a face: 8 out of 32). A single announcement line, or no text before the logo.

**BA13. Work: a slow setup.** A short notice on black opens the film (3 words, 2.2 s, 2 out of 2). The credits (8 to 12 words) arrive between 29 and 45%. The title of the work at 91 and 94%. Long chapter blacks allowed.

**BA14. Text: one block at a time** (8 out of 8). Punch word of 1 or 2 words, 1.0 to 2.3 s, on black, then the picture rises underneath (3 out of 5). Share of time with text: work 8 to 17%, catalog by blocks 27 to 28%, mixed catalog 10 to 14%.

**BA15. The picture moves more and more.** Median motion rises from the first to the last third in 6 films out of 6. Still shots: 7.6%.

**BA16. Keep color.** No film goes to black and white, except 2 archive shots to say "this is the past". Widescreen (2.0 to 2.39:1) for fiction: 4 out of 4; full-frame 16:9 for usage and games: 3 out of 3.

### 7.3 The usage film rules (2 films, weak)

**U1. Four beats.** Opening (0 to 5%): black, then a shot that reveals the situation, or the object's light pulsing on black (2 out of 2). Scenes of life (5 to 78%): scenes of 4 to 7 shots, the situation, the person, the object, what the object does. Peak (78 to 90%): alternating scenes, shots of 0.37 s (1 out of 2; the other ends on a 7.4 s shot). Ending: a line of 3 to 9 words, then the name or the logo (2 out of 2).

**U2. The object in one shot out of three.** 10 shots out of 29 and 23 out of 73. Direct cuts go from the person to the object or the reverse (8 out of 8). A look makes a good match: the person looks at their wrist, the next shot shows the watch face (1 case).
*Why:* an object present all the time turns the film into a demo; absent, it is forgotten.

**U3. Text at the end only** (in the last 10%, 2 out of 2). No button (0 out of 2).

**U4. Median shot 1.0 to 1.7 s** (2 films). A scene often opens on a wide shot (3 scenes out of 5 in one film).

**U5. A picture-and-black pulse, if the subject calls for it.** One film strings together 49 blacks of 0.1 to 0.6 s to mimic a heartbeat (1 out of 2).

**U6. Voice-over is allowed** (1 out of 2: 18 sentences of 5 words, 45% of the time). It goes silent at the peak, then comes back for two sentences before the end.

### 7.4 Templates (convention: the observed structure, scaled to the length)

Catalog by blocks, 90 s. Example: the season of a music festival, 10 concerts.

| # | Beat | From → to | Content | Shots |
|---|---|---|---|---|
| 1 | Black | 0:00.0 → 0:00.6 | black | 1 |
| 2 | Hook | 0:00.6 → 0:15 | one shot per concert, a line from a musician from 2 s; wide shots first | 10 to 12, of 1.2 s |
| 3 | Announcement | 0:15 → 0:20 | 2 or 3 punch words of 2 words, on black; the picture rises under each | 3 title cards of 1 to 2 s |
| 4 | Body | 0:20 → 1:10 | 10 blocks of 4.5 s: the concert title (1 s), then 3 to 6 shots; a spoken line running over the cuts | 40 to 50, of 0.7 to 0.9 s |
| 5 | Peak | 1:10 → 1:20 | all the concerts mixed, no title, almost no speech | 15 to 20, of 0.5 to 0.6 s |
| 6 | Closing | 1:20 → 1:30 | black 0.4 s; button 2.5 to 3 s; black 0.2 s; title or logo coming out of black, 3.5 s | 4 to 5 |

Work, 90 s. Example: a documentary about a high-mountain climb.

| # | Beat | From → to | Content |
|---|---|---|---|
| 1 | Black and notice | 0:00 → 0:05 | black 2 s, then a notice of 2 or 3 words, very small, on black (2 s) |
| 2 | Setup | 0:05 → 0:30 | wide shots of 1.5 to 3.5 s; the first spoken line can wait until 20% |
| 3 | Credit | around 0:27 and 0:40 | 1 or 2 title cards of 8 to 12 words, 2 to 3 s, on black; the text stays over the next shot |
| 4 | Build-up | 0:30 → 1:12 | 1.5 s shots coming down to 0.7 s; chapter blacks of 1 to 2.5 s allowed |
| 5 | Peak | 1:12 → 1:17 | shots of 0.5 to 0.6 s; blacks of 0.2 to 0.4 s between images allowed |
| 6 | Closing | 1:17 → 1:30 | black 1 to 2.5 s; button (1 shot, 3 to 3.5 s, the line starts on the black); black; title coming out of a glow (3.5 to 7 s); black |

Usage, 60 s. Example: a headlamp for mountain running, at night.

| # | Beat | From → to | Content |
|---|---|---|---|
| 1 | Opening | 0:00 → 0:05 | black 0.4 s, then a shot that reveals the scene, or the lamp's light turning on in the dark |
| 2 | Scenes of life | 0:05 → 0:47 | 4 or 5 scenes of 8 to 10 s: situation (wide), person, object in close-up, what the object does; one shot in three shows the object |
| 3 | Peak | 0:47 → 0:54 | alternating scenes, shots of 0.4 to 0.8 s; the voice-over goes silent if there is one |
| 4 | Ending | 0:54 → 1:00 | a line of 3 to 9 words, built up in groups on black or placed under the object; then the name 3.5 s |

---

## 8. Sound: voice, music, silence

**The music is the user's, and they hold the rights, or there is none.** Never music searched for, downloaded, generated or taken from a library, even "royalty-free".

| Family | What the sound does | Status |
|---|---|---|
| Product | no measurable sound in the corpus; the music carries the exit from black, the reveal and the name; the film ends on a resolution, then a short black | convention |
| Opening | starts from silence (4 out of 8), rises, peaks after 60% (7 out of 8, median 68%); the cutting speed does not follow the volume (only 3 films out of 7) | observed |
| Documentary | continuous bed under and between the voices (8 out of 8: in speech silences, 5.5 dB below the voice median); steady level from one third to the next (8 out of 8); ends with sound (6 out of 8) | observed |
| Trailer | the music alone carries the hook, the peak and the logo; it drops before the button; the title lands on an accent | convention (no sound in the measured corpus) |

The rules that follow:

- **Lock the big changes, not the cuts** (G8): the exit from black, the peak, the reveal, the landing, the name or the title sit on an attack or a change in the music, if there is one within 0.6 s (convention). Ordinary cuts follow action and speech.
- **Two exceptions where the cut follows the grid**: still photos, one per bar (1 film); a sung music video, at the start of a line (1 film). At a trailer's peak, cutting on strong beats is allowed (convention).
- **Voice and picture don't come in together.** Documentary: a person's voice before their face (13 out of 20). Materials voice-over: the picture of the step before or with the word (7 out of 10, 1 film). This is not a contradiction: a person announces themselves through their voice; a thing shown announces itself through its picture.
- **No digital silence between two sentences** in a documentary (8 out of 8): the music or the room sound stays underneath.
- **A sound can come before the picture** by 0.5 to 1.5 s to enter a new place (convention, 1 case read in the subtitles).
- **Without music** (convention): cut on action and speech; keep the opening and closing blacks; keep the footage sound under the shots that have some (track A3).

---

## 9. Length, format, color

### 9.1 Observed lengths

| Family, form | Observed length |
|---|---|
| Product without voice | 24 to 51 s (median 31.9 s, 13 films) |
| Product with materials voice-over | 54 to 128 s (3 films) |
| Opening | 65 to 143 s (median 99 s, 8 films) |
| Transition between two places | 11 to 31 s (median 23.9 s, 6 films) |
| Documentary | 78 to 324 s (median 142 s, 8 films) |
| Trailer | 50 to 119 s (median 89.2 s, 6 films) |
| Usage | 60.0 and 93.5 s (2 films) |

A requested length outside these bounds is allowed. It is marked **convention** in the edit plan, and the structure stretches or tightens while keeping the relative positions (reveal around 77%, peak between 60 and 88% depending on the family, name or title at the end).

### 9.2 Formats

- Full-frame 16:9: the rule in all families (product 13 out of 16; documentary 6 out of 7; usage 3 out of 3).
- Widescreen (2.0 to 2.39:1): fiction trailers (4 out of 4), 2 openings out of 8, 1 documentary entirely in black and white. One format per film.
- 9:16 and 1:1: **0 films observed**. Convention: same pacing and structure rules; each shot is reframed on its subject, never shrunk with bars; text inside the safe area.

### 9.3 Color

| Family | Black and white |
|---|---|
| Product | never a desaturated scene (0 out of 16) |
| Opening | 3 films out of 20, all people at work or portraits |
| Documentary | portraits in black and white (4 out of 4); people in black and white, screens in color (2 out of 8) |
| Trailer and usage | never, except an archive (8 out of 8) |

A black-and-white grade is done in the editing software. The skill flags it in the edit plan; it does not set it in the timeline files.

---

## 10. What is never taken

The grammar, never the brand. Even "in the style of":

- no image, sound or excerpt from the measured films;
- no Apple logo, font or icon; the logo is the user's, or nothing; the font is theirs, otherwise a common font (Arial, Inter or DejaVu Sans);
- no signature: no caption naming the camera or software used to shoot, no other brand's logo at the end of the film;
- no line from the films, even translated, nor its exact form;
- no invented figure, opinion, testimonial or name: whatever is missing stays visible and gets asked for;
- no music without rights.

---

## 11. Observed or convention: the summary

| Rule | Status |
|---|---|
| Hard cut: 83 to 98% of changes depending on the family | observed (234, 367, 606, 459 transitions) |
| One cross dissolve at most, at a chosen moment | observed (7 out of 234; 2 out of 367; 1 out of 606; 8 out of 459) |
| Black opens | observed 13 out of 16, 6 out of 8, 6 out of 8, 7 out of 7 |
| Cut on every beat of the music | not shown (1 film out of 11; 16 out of 62 against 16.4; 363 out of 597 against 361.5) |
| Title card length: at least 1.2 s + 0.3 s per word | convention (sister skill), matched by the opening (0.5 s per word, 7 title cards) |
| Product: reveal between 69 and 82% | observed 10 films |
| Product: never the whole object in the first shot of a reveal | observed 0 out of 10 |
| Product: name between 83 and 96% | observed 7 films |
| Product: always write the name with no presenter | convention |
| Product: past 60 s without voice, in chapters | convention |
| Opening: peak between 61 and 79% | observed 5 out of 7 |
| Opening: last shot of at least 5 s, wide | observed 6 out of 8; 5 out of 7 |
| Opening: text never in the middle | observed 0 out of 7 |
| Opening: continue the last shot under the first words | observed 3 out of 8; length of 2 to 5 s: convention |
| Documentary: speech 51 to 88% of the film | observed 8 out of 8 |
| Documentary: face on screen for a third of the speech | observed, median 33%, 6 out of 8 under 55% |
| Documentary: voice before face | observed 13 out of 20 |
| Documentary: interview never wide | observed 0 out of 162 |
| Documentary: edit the speech first | convention |
| Trailer: last third faster than the first | observed 6 out of 6 |
| Trailer: peak between 78 and 88% | observed 6 out of 6 |
| Trailer: spoken line running over a cut | observed 94 out of 108 |
| Trailer: final title or logo | observed 8 out of 8 |
| Usage: the object in one shot out of three | observed 2 out of 2, weak |
| Music: what it carries in product and trailer | convention (no sound in these corpora) |
| 9:16 and 1:1 formats | convention (0 films observed) |
| Length outside the observed bounds | convention |
