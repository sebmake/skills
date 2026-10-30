# Social cut-downs

This file explains how to cut short versions (15, 30, 45, 60 s) of the product film for social media, in 16:9, in vertical 9:16 and, optionally, in square 1:1. The base grammar is in `grammaire-film.md`, the shots in `recettes.md`, and the `film.json` format in `film-spec.md`.

**Status.** The 51 films in the corpus are all 16:9 (1 of them in cinema format). No vertical or square film was observed: **every rule about 9:16 and 1:1 is a convention.** The short 16:9 form is observed: 6 reveal films out of 8 run from 21.5 to 34.5 s.

## Contents

1. The principle: one script, several layouts
2. The first 2 seconds
3. Templates for 15, 30, 45 and 60 s
4. Formats, safe zones and sizes
5. Recomposing each element
6. The end card
7. Music in the cut-downs
8. What is forbidden
9. Checklist

---

## 1. The principle: one script, several layouts

- **Recompose, don't crop.** Each format is its own composition: HyperFrames reads the width and height once, at compile time. Never render the 16:9 and crop it afterward.
- **One script.** The cards, their words and the shot order are the same in every format of the same duration. Only the line breaks and the layout change.
- **Everything comes from the long film.** A cut-down takes its shots and cards from the product film. It creates no new content, except the order and the line breaks. If a card is too long for the format, take another card from the film; don't summarize it.
- **Destination → format** (from the HyperFrames skills): website and YouTube → 16:9; Reels, Shorts, TikTok, stories → 9:16; square feed (LinkedIn, Instagram, X) → 1:1, only if the user is aiming for it.
- The product film comes first, in 16:9. The cut-downs come after, once its structure is approved.

---

## 2. The first 2 seconds

A feed is won or lost in its first second. The observed openers do the opposite: 5 out of 8 start on black, a slow fade or a still card, and none (0/8) combines a strong image, text and motion in the first second. That is right for a room that is waiting, wrong for a feed. Hence these conventions:

1. **Frame 0 is full**, never black. No fade from black (0.2 s at most).
2. **A card readable at 0.2 s**: 2 to 4 words, at hook size (§ 4.3). Feeds are watched with the sound off: without a voice, the text is the hook.
3. **Motion from the first second**: light passes, the object turns, the shot pushes in.
4. **The product, or its effect, visible before 3 s.** A recognizable detail is enough (macro, a single interface element); the whole object can keep its reveal.
5. **Open with the payoff.** The long film's thesis sentence moves to the start. It says what the audience gains, in their words, never a list of features.
6. **No logo at the start**: the name closes the film (observed 21 times out of 24 name or logo texts).

Three hooks that fit the observed grammar:

| Hook | What it is | Observed |
|---|---|---|
| Two-part thesis sentence | a clause, then its payoff, on the strongest image | at the start of 4 films out of 11 with message cards |
| Mystery detail | a close-up you don't recognize, which opens onto the object | macro → whole object in the material films |
| Punch word | one or two words, large, on the strongest image | 5 times, in trailers |

Not observed in the films, so avoid them: the rhetorical question, the "before / after" as a hook.

---

## 3. Templates for 15, 30, 45 and 60 s

### 3.1 The long film split into roles

The templates draw on the roles of the product film (convention, built on the observed beats):

| Role | In the product film |
|---|---|
| T1 Opening | the hook, and its thesis card if there is one |
| T2 Context | the first idea card and its images |
| T3 Reveal | the shot of the whole object (or all the screens) |
| T4 to T6 Proofs | an idea card or a feature name, and the shot that proves it |
| T7 Closing line | the closing line, or the thesis |
| T8 Name and end | the name card |

### 3.2 The templates

Durations in seconds. "Cards" counts every text, including the name and the end card. Word budgets are totals (about 62 words per minute at most): not every card can be at the 6-word maximum.

| Format | Run-down | Taken from | Cards | Max words |
|---|---|---|---|---|
| **15 s** | 0–2.5 hook (strong image + thesis of 2 to 4 words) · 2.5–6.5 reveal (object 1.5 s, then name 2.5 s) · 6.5–11.5 one proof (shot 2 s + card of 6 words at most, 3 s) · 11.5–15 end (3.5 s) | T7 first, T3, the best proof, T8 | **4** | **16** |
| **30 s** | 0–2.5 hook · 2.5–7 context (1 card) · 7–11 reveal and name · 11–23 two proofs (6 s each: shot 2 to 3 s, card 3 s) · 23–26.5 short closing line · 26.5–30 end | T7, T2, T3, two proofs, T7 shortened, T8 | **7** | **32** |
| **45 s** | 0–2.5 hook · 2.5–8 context (1 or 2 cards) · 8–13 reveal (name optional) · 13–34 three proofs (7 s each) · 34–39.5 two-part closing line · 39.5–45 end | T1 or T7, T2, T3, T4 to T6, T7, T8 | **9 to 10** | **45** |
| **60 s** | 0–2.5 hook · 2.5–10 context (2 cards) · 10–16 reveal (name optional) · 16–46 three or four proofs (7.5 to 10 s), with **a break in rhythm around 30 s** (a lone word or a passage with no text) · 46–54 two-part closing line · 54–60 end | the whole long film, shortened | **12 to 14** | **60** |

- In the cut-downs, the name may appear a first time at the reveal (convention: we don't know who will watch to the end). The engine does this by default up to 37 s; beyond that, it is optional (`avec_nom`). It always comes back at the end. Never at the start.
- Observed reference for the 30 s form in 16:9: hook 3 to 6 s, build-up 13 to 20 s, reveal 4 to 9 s, name 3 s, 4 to 13 shots (6 reveal films out of 8). The templates above tighten it for the feed: shorter hook, product visible earlier.

### 3.3 By film family

| Family | What changes in the cut-downs (convention) |
|---|---|
| Object reveal | 30 s = one reveal move + the name; 60 s = two moves. Prefer shots with a vertical shape: macros, rotations, levitation. |
| Software | Open on the detail of the strongest feature (`macro` on a screenshot, or `panneau` with `zoom`), with the thesis; then 8 to 10 shots of 1.5 to 2.5 s, a feature name on each shot; end on the name. In 60 s: a short passage chained with crossfades (about 12 s) and, if provided, 2 quotes between 30 and 45 s. |
| Use | Keep the fast pace of the edit; the closing line and the name as they are. |
| Text-only film | Keep one fragment at a time; in 9:16, one meaning group per line. |

### 3.4 Cutting rules

- **Shorter shots** than in the long film: 1.2 to 2.5 s per image shot, except under a card (convention; observed reference: 1.5 to 1.6 s in trailers).
- **A card lasts at least its reading time** (`grammaire-film.md` § 6.4), even in a 15 s cut-down: the engine never goes below it, even if that runs slightly over the target duration.
- **The same words** as the long film.
- Keep the **most visible** proofs: those whose shot makes sense with the sound off and at a small size.
- 9:16 and 1:1 follow the same run-down as the 16:9 of the same duration; only the layout changes (§ 5).
- 1:1 is optional.

### 3.5 In `film.json`

A cut-down is one entry in `declinaisons` (details in `film-spec.md` § 8). There are two ways to describe it:

- **`"regle": "auto"`**: the engine picks the shots from the template for the duration. It takes, in order: the hook (a `mot-sur-image` of 4 words at most, otherwise the thesis card with role `accroche`, otherwise the `chute` card; at 20 s or less, the shorter of the two if it has 4 words at most; otherwise an `accroche` shot that is not black), 0 to 2 `contexte` groups, the `revelation` or the `empilement` that stands in for it (with the name if the duration is 37 s or less), 1 to 4 `preuve` groups by ascending `priorite`, the `chute` (above 20 s, unless the shot before is already a card) and the `fin`. Up to 37 s, a proof that has its card loses its feature names; at 15 s, it shrinks to its card and one shot.
- **`"plans": [...]`**: the list you want, in order. An `id`, or `{ "id", "duree_s", "avec_nom", "sans_texte" }`. `avec_nom: true` on a `revelation` shot brings the name in at the end of the shot (4 s at least). `sans_texte: true` removes the feature name from a shot: fewer words, never different words.

For `auto` to choose well, the long film must be well labeled:

- every shot has its `role`;
- a card and the shot that proves it share a `groupe`: they stay or go together;
- the most visible proofs (readable with the sound off and at a small size) have `priorite: 1`;
- a `mot-sur-image` of 4 words at most on the strongest image makes a good cut-down opener.

What the engine does on its own: it removes `noir` shots, brings in the first shot without black and its text from 0.2 s, places the product visual, blurred and dimmed, behind an opening card (frame 0 full, convention), adjusts durations to land on `duree_cible_s` without going below a card's reading time or a recipe's minimum, and removes the final black. `musique_debut_s` sets where the track starts.

Start with `auto`, look at the review sheet, then switch to a `plans` list if a choice doesn't fit.

---

## 4. Formats, safe zones and sizes

### 4.1 Formats

| Format | Size | Use |
|---|---|---|
| 16:9 | 1920 × 1080 | product film; cut-down for website and YouTube |
| 9:16 | 1080 × 1920 | Reels, Shorts, TikTok, stories |
| 1:1 | 1080 × 1080 | square feed, optional |

### 4.2 Safe zones

All text, the name, and the product detail that carries the proof stay inside the safe zone. The image (background, object, shot) can bleed anywhere.

| Format | Zone for text and the key detail | Source |
|---|---|---|
| 16:9 | the central 80%: margins of 192 px left and right, 108 px top and bottom | HyperFrames skill `embedded-captions` |
| 9:16 | vertically, from 12 to 78% (y from 230 to 1,498 px): the bottom 22% is covered by the social app's interface; horizontally, from 65 to 1,015 px, line of 800 px at most, centered (20 characters at 72 px) | height: HyperFrames skill; width: convention (the button column on the right, not verified) |
| 1:1 | margins of 86 px (8%) on all 4 sides | convention |

- **Optical center in 9:16**: y ≈ 864 px (45% of the height, middle of the safe zone), instead of 960 px. A centered card sits there (convention).
- No empty band reserved at the bottom: the text is on the image, not under it.

### 4.3 Text sizes

Font size in px. The first value is what the engine sets; the range in parentheses is the allowed range.

| Role | 16:9 (1920 × 1080) | 9:16 (1080 × 1920) | 1:1 (1080 × 1080) |
|---|---|---|---|
| Message card | 58 (52–64) | 72 (64–84) | 62 (56–72) |
| Name, discreet version | 56 (52–64) | 76 (72–90) | 68 (64–80) |
| Name, hero version | 124 (110–140) | 132 (120–150) | 116 (110–130) |
| Punch word, hook | 150 (130–170) | 150 (130–170) | 124 (110–140) |
| Feature name | 68 | 76 | 64 |
| Call-to-action line, mention | 34 (32 at least) | 42 (40 at least) | 38 (36 at least) |

- 16:9: observed (median 5% of the height for a message, 9 to 14% for a hero name). 9:16 and 1:1: convention, based on the HyperFrames skills' minimums for vertical (body 65 to 95 px, hook 130 to 170 px) and for the feed (body of 32 px at least).
- A long word must fit: max size ≈ usable width ÷ (letters in the longest word × 0.6), in regular.
- Small and calm, even in vertical: the large size stays reserved for the name and one or two punch words.

### 4.4 Lines

- At most 42 characters per line in 16:9, 22 in 9:16, 26 in 1:1 (convention).
- In 9:16, a card fits on 2 or 3 lines, broken between meaning groups. A built card puts **each group on its own line**; lines are added below.
- Rewrite the line breaks, never the words.

---

## 5. Recomposing each element

| Element | 16:9 (reference) | 9:16 | 1:1 |
|---|---|---|---|
| Centered card on a flat background | centered, 1 line | centered at 45% of the height, 2 to 3 lines by meaning group | centered, 1 to 2 lines |
| Card built in groups | groups on the same line | one group per line | 2 lines at most |
| Object alone on a flat background | small, centered, lots of empty space | object at 55–75% of the width, in the band from 25 to 65% of the height; background extended | object at 50–65% of the width |
| Object and text side by side | object on one side, text on the other | **stacked**: object on top (18 to 55% of the height), text below (58 to 74%) | side by side if the text is 3 words at most; otherwise stacked |
| Full desktop screen (panel) | panel at 72% of the width | unreadable: 1.5 s at most, then move into a detail | whole panel, text below |
| Mobile screen and feature name | screen in the center, name on the right | name above (around 20% of the height), screen at 50% of the height, above the 78% limit | name below (around 88% of the height), screen at about 66% of the height |
| Full-frame image (mood, photo, video) | full frame | crop to the subject if it fits within 32% of the original width; otherwise place the image in a central band (1080 × 608) and the text in the flat area above | crop to the subject (56% of the original width) |
| Text placed on an image | in a calm area | find the calm area of the new frame; otherwise pull the text out as a card on a flat background, before or after the shot | same |
| Provided number | number centered, label below | same stack; number at 70% of the width at most | same stack |
| Camera move | lateral tracking | becomes vertical, or a slow zoom | slow zoom |
| Cinema black bars | allowed (observed in 2019 only) | removed: full frame | removed |
| Final name | centered | centered at 45% of the height; logo below if provided, never in the bottom 22% | centered |

All these recomposition rules are conventions. The engine applies them recipe by recipe: you set nothing by hand; you check on the review sheet.

---

## 6. The end card

- Observed in the long film: the name alone, centered, 1.25 to 3.4 s (median 2.7 s), sometimes preceded by a closing line in the same place; then black or a logo, 1 to 2 s.
- In a cut-down (convention):
  - 2.5 to 3.5 s, still after a fade-in of 0.3 s at most;
  - **the name**, and **a single call-to-action line** (address, date, "available …") **if provided**; otherwise `[TO PROVIDE]` in the storyboard, or nothing;
  - the logo only if provided;
  - everything inside the safe zone;
  - **no final black longer than 0.5 s**: social apps loop the video, and a long black breaks the restart.
- The end card counts toward the word budget.

---

## 7. Music in the cut-downs

- The same file as the product film, provided by the user, or no music. Never other music.
- The track can start further in (the cut-down's `musique_debut_s`), so the first second already has energy (convention).
- The fade-out is the one in `musique.fondu_sortie_s` (2 s by default); it ends with the end card.
- A cut-down with no music is still valid: feeds are often watched with the sound off.

---

## 8. What is forbidden

All conventions:

- rendering the 16:9 and shrinking it into a 9:16 with bars;
- filling the bars with the blurred, enlarged image: a sign of a "repost";
- cutting a word or a line of a card to make it fit;
- changing the words from one format to another;
- opening on black, on the logo or on the name;
- inventing a number, a review, a date or a call-to-action line.

---

## 9. Cut-down checklist

- [ ] Frame 0 full, card readable at 0.2 s, motion in the first second.
- [ ] Product (or its effect) visible before 3 s; name at the reveal and at the end, never at the start.
- [ ] Each card: 6 words at most all at once, 12 at most when built; reading time respected.
- [ ] Never two cards at the same time; a shot with no text between two message cards.
- [ ] The template's card and word budgets respected.
- [ ] Text, name and key detail inside the format's safe zone.
- [ ] Contrast of at least 4.5:1 everywhere (`npx hyperframes check`), at least 7:1 on an image.
- [ ] Same words as the long film; only the line breaks change.
- [ ] No number, review or quote that wasn't provided; otherwise `[TO PROVIDE]`.
- [ ] Music: the user's file, or none.
- [ ] End card of 2.5 to 3.5 s, still; no final black longer than 0.5 s.
- [ ] The film makes sense with the sound off, on a phone, at arm's length.
