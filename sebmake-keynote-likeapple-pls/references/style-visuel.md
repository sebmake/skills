# Visual style: the measurements that make it look like a keynote

This file only holds **measurements and rules**, never an image. It comes from 67 images taken from 8 keynotes (2019-2026), looked at one by one and then measured to the pixel (method in Appendix A). The engine (`scripts/build_deck.js`) applies these values. `deck.json` carries none of them.

Each value has a status:
- **measured**: taken from the images, with the number of images;
- **converted**: a measurement translated for a 16:9 pptx canvas;
- **convention**: a choice made by the skill, not observed (this is said each time).

The corpus font was only used as a ruler for the measurements. Using it stays forbidden, like any brand, logo, image or device from the corpus.

---

## 0. Units and conversions

- **Canvas**: 10 × 5.625 in, that is 720 × 405 pt. H = height, W = width. 1 % H = 4.05 pt = 0.056 in; 1 % W = 7.2 pt = 0.1 in.
- We measure the **cap height** (“cap”), never the font size. It is the only size that compares from one font to another.
- **Font size (pt) = cap (% H) × 4.05 / capEm.** capEm (cap height per em): Inter and Inter Tight 0.728; Arial 0.716; Helvetica Neue 0.714; unknown font 0.72. Quick rule: **font size ≈ cap (% H) × 5.6**.
- **Line spacing**: given as a multiple of the cap (it does not depend on the font), then in exact points. The engine sets the exact line spacing (pptxgenjs `lineSpacing`, `a:spcPts`), not `lineSpacingMultiple`: PowerPoint's “1.0” depends on each font's metrics (Arial 1.12 em, Inter 1.21 em). Formula: **line spacing (pt) = k × capEm × font size**. The HTML preview uses `line-height = line spacing / font size`.
- **Tracking**: given in em. **charSpacing (pt, pptxgenjs) = tracking (em) × font size (pt).** For example, 144 pt × −0.035 em = −5 pt.
- **Vertical centering**: with `valign: middle`, the center of the box falls on the center of the cap zone to within 0.01 em, for Inter as for Arial. So the box is placed by its center, at the height wanted for the caps.

---

## 1. The eight measurements that make the look

| # | Rule | Measured | Iteration 1 (for comparison) |
|---|---|---|---|
| 1 | **Very large.** Title card: cap from 14.5 to 19 % H (about 100 pt). Thesis sentence: 9 % H (50 pt). Hero figure: 22 to 26 % H (144 pt). | 4 + 2 + 6 images | title with a cap of 7.1 % H (about 40 pt): twice too small |
| 2 | **Centered on the middle.** The cap zone of the block is centered between 46.5 and 50 % H. Nothing floats in the top third with empty space below. Only the chart, the price and the availability start from the top, because a visual fills the bottom. | 22 images | preview centered at 49 % H: the empty space around it comes from the text size |
| 3 | **Tight.** Negative tracking from 28 pt. Title line spacing from 1.55 to 1.65 cap; quotes and agendas from 1.35 to 1.5 cap. | 19 calibrated strings | zero tracking |
| 4 | **Semibold, not black.** The stem-thickness-to-cap ratio is 0.163 to 0.208 (median 0.18): between medium and semibold. An 800 weight is 40 % too thick. | 17 strings | Arial Bold as fallback: 0.21 to 0.26 |
| 5 | **Two levels of text, no more.** The main text and a secondary one, from 0.15 to 0.45 times its cap, in gray at 53 %. | every image with text | three to four levels |
| 6 | **One accent color per slide**, on few elements: the name, the figure, your own bar, the pictograms. | 67 images (exceptions: agenda, bento, logos) | pink marker accent + yellow |
| 7 | **Solid background, no border or frame around text, no shadow on text.** | 0 cases out of 67 images | dotted boxes, gray frames |
| 8 | **The visual takes the space.** Device over 89 to 100 % H, object over 50 to 60 % W, product over 60 to 86 % H, bento up to the edges (1 % margin). | 15 images | gray “image expected” frames |

---

## 2. Shared typography

### 2.1 Weight

**Measured** on 17 large strings: the observed stem/cap ratio, compared with the same text rendered in each font at the same cap.

| Font | Weight | Rendered stem / observed stem | Verdict |
|---|---|---|---|
| Inter | 500 · 600 · 700 · 800 | 0.95 · 1.08 · 1.24 · 1.40 | **600** |
| Inter Display (opsz 32, close to Inter Tight) | 500 · 600 · 700 | 0.97 · 1.10 · 1.25 | **600** |
| Arial | 400 · 700 | 0.86 · 1.23 | **700** (no semibold) |
| Helvetica Neue | 500 · 700 | 1.02 · 1.26 | **500** |

| Role | Weight |
|---|---|
| Titles, names, figures, list lines, quotes, prices | semibold (600); Bold if the font has no semibold |
| Label under a figure, text next to an object, availability word | semibold, or medium |
| Gray kicker, “Starting at”, note under a price, a speaker's role, source, legal notes | regular (400) |
| Forbidden | 800 and 900 |

**Setting semibold in the .pptx.** pptxgenjs only knows `bold: true` (weight 700). For 600, the engine sets the **legacy family name of the semibold face** (nameID 1 of the font file), with `bold: false`, when that face is installed: for example “Inter SemiBold”, “Inter Tight SemiBold” or “Inter 18pt SemiBold” for the static Google Fonts files. The engine already lists the installed font files. If the face is missing, it uses the family with `bold: true`.

### 2.2 Tracking (charSpacing)

**Measured**: the width of 19 strings, compared with their rendering in each font at the same cap. The gap per letter interval is derived from it. Spread from one string to another: about ±0.025 em. Large figures need the most tightening.

| Font (title weight) | ≥ 50 pt | 28 to 50 pt | < 28 pt | Measured (medians ≥ 50 / 28-50 / < 28) |
|---|---|---|---|---|
| Inter (600) | **−0.035 em** | **−0.035** | **−0.02** | −0.035 / −0.039 / −0.021 |
| Inter Tight (600) | **−0.02** | **−0.02** | **0** | estimated from Inter Display: −0.021 / −0.018 / +0.005 |
| Arial (Bold) | **−0.06** | **−0.045** | **−0.015** | −0.068 / −0.052 / −0.016 |
| Helvetica Neue (Medium) | **−0.045** | **−0.03** | **−0.01** | −0.046 / −0.026 / −0.003 |
| Unknown font | **−0.03** | **−0.025** | **−0.01** | convention |

- Never beyond −0.07 em, and no tightening below 14 pt.
- Inter Tight was not installed on the measuring machine: its row is an estimate. Measure it again (Appendix A) as soon as the font is available.
- **Kerning**: pptxgenjs writes `kern="0"` as soon as a `charSpacing` is set, with the comment “disable kerning” in its code. A tight title without kerning leaves gaps between some pairs (To, Av, Te). So the engine replaces `kern="0"` with `kern="1200"` (kerning from 12 pt) in the title XML. Check it on a screenshot after the first pass.

### 2.3 Line spacing

| Use | k (line spacing / cap), measured | Engine value | Inter example |
|---|---|---|---|
| Thesis sentence, two-line title | 1.55 to 1.66 (2 images) | **k = 1.6** | 50 pt → 58 pt |
| Quote | 1.48 (1 image) | **k = 1.5** | 36 pt → 39 pt |
| Stacked agenda | 1.35 to 1.77, median 1.41 (3 images) | **k = 1.4** | 56 pt → 57 pt |
| Short text next to an object | 1.50 (1 image) | **k = 1.5** | 34 pt → 37 pt |
| List of 3 to 6 lines | 1.96 (1 image); 1.75 to 2.2 with pictograms (2 images) | **k = 1.95** | 36 pt → 51 pt |
| List of 2 lines | 3.1 (1 image) | **k = 3.1** | 36 pt → 81 pt |
| Short list next to an icon, price card | 1.8 (1 image) | **k = 1.8** | 24 pt → 31 pt |
| Lower third: name then role | 2.0 (3 images) | **k = 2.0** | 16 pt → 23 pt |

### 2.4 Text colors

| Role | Measured | Engine value |
|---|---|---|
| Light background | #F2F2F2 to #F9F9F9, never pure white (6 images); pure white is kept for tiles | the user's `fond_clair`, as is |
| Dark background | pure black (12 images) | the user's `fond_sombre`, as is |
| Main text | pure black or white at the core of the letters | `texte` (on light) or white (on dark) |
| Secondary text | 51-56 % of the way from the text toward the background (4 images, on light as on dark) | **53 % mix from the text toward the background**, or `texte_secondaire` if it is provided and readable at 4.5:1 |
| Line “not said yet” | same value, 53 % (1 image) | like the secondary |
| The other one, in a chart | gray at about 45 % (1 image measured, 1 seen) | 45 % mix |

---

## 3. Cards by archetype

Positions in inches on the 10 × 5.625 in canvas. “center y” is the target center of the cap zone, so the center of the box placed with `valign: middle`.

### A1 Title card: a name alone, centered

- **Measured (4 images)**: for one word, cap of 14.5, 19.0 and 19.0 % H; for two words, 11.3 % H. Width from 29 to 59 % W. Cap center at 50 % H (±0.5) and at 50 % W. One line. Stem/cap from 0.163 to 0.182. Color: text, or the section's gradient (2 images out of 4).
- **Values**:
  ```
  size 100 pt (cap ≈ 18 % H); adjusted to fit on one line within 6.4 in, floor 64 pt
  beyond that: 2 lines, floor 60 pt, line spacing k = 1.6
  box x 0.6  w 8.8 · center y 2.81 in (50 % H) · align center · valign middle
  tracking: ≥ 50 pt class · weight 600
  color: text, or flat accent (the name then carries the slide's accent)
  ```
- The final period, if there is one, takes the accent color, at the same size and weight. The corpus does not use one: it is a choice of the skill, validated against the control deck. It only appears on A1, A4 and the final slide.

### A4 Thesis sentence: one or two centered lines

- **Measured (2 full-frame images, 1 on a stage screen)**: cap of 8.9 and 9.2 % H; longest line over 66 to 74 % W; two lines, the second at 55-70 % of the first; line spacing from 1.55 to 1.66 cap; block center at 47.2 and 49.9 % H.
- **Values**:
  ```
  size 50 pt (cap ≈ 9 % H), floor 44 pt: below that, the text is too long, cut words
  2 lines at most, balanced · line spacing k = 1.6 (Inter 50 pt → 58 pt)
  box x 1.2  w 7.6 (76 % W) · center y 2.73 in (48.5 % H) · align center
  tracking: ≥ 50 pt class · weight 600 · text color; accent on one word at most
  ```
- **Line break (convention)**: line balancing avoids ending a line on a function word (article, preposition, possessive): “A failure / never gives notice.” rather than “A failure never / gives notice.”. Penalty of 0.25 × the square of the average length, in every balanced text (titles, tiles, A9 columns). A `\n` written in `deck.json` always wins.

### A5 Big figure + label: the hero moment

- **Measured (6 images)**: figure with a cap from 21.6 to 26.1 % H (median 25.4); width from 19 % W (“2×”) to 80 % W (a number followed by a word). Label with a cap from 3.7 to 5.5 % H (median 4.2), that is 0.15 to 0.21 times the figure, in semibold, **in the text color**, not in gray. Two layouts:
  - (a) 4 images: the figure's cap zone is centered on the middle (37 to 63 % H) and the label drops to 72-82 % H;
  - (b) 2 images: the whole block is centered, the label tight under the figure (6 % H gap).
  The figure has a horizontal gradient on 4 images out of 6 (§4.2), otherwise it is in the text color.
- **Values, layout (a) by default**:
  ```
  figure: size 144 pt (cap ≈ 25.6 % H), on one line, no break
          adjusted to fit within 8.0 in, floor 110 pt
          box x 1.0  w 8.0 · center y 2.81 in (50 % H) · align center
          tracking: ≥ 50 pt class (Inter −0.035 em, that is −5 pt) · weight 600
          color: accent → accent2 gradient (§4.2), otherwise flat accent
  label:  size 24 pt (cap ≈ 4.3 % H) · weight 600, or 500 · text color
          box x 0.8  w 8.4 · center y 4.50 in (80 % H) · one line
  ```
- **Layout (b)**, when the label fits on two lines: figure center at 2.56 in (45.5 % H), label cap top at 3.54 in (63 % H), line spacing k = 1.6.
- **Kicker (convention)**: at the label size (24 pt), baseline at 1.73 in, that is 0.25 of the figure's cap above it.
- **Missing figure**: the `[TO PROVIDE: …]` marker takes the figure's place and style (§3.15). Write its label in one word (“gain”, “wait”) so it stays at hero size.

### A7 List without bullets: the line being said lights up

- **Measured (2 full-frame images)**: cap from 6.4 to 6.8 % H; centered lines, from 18 to 85 % W wide; line spacing of 1.96 cap for 3 lines, 3.1 cap for 2; block center at 46.5-47.4 % H. The line being said is full, the next one at 53 %.
- **Values**:
  ```
  size 36 pt (cap ≈ 6.5 % H) · weight 600 · 5 words per line at most
  3 to 6 lines: line spacing k = 1.95 (Inter 36 pt → 51 pt); 2 lines: k = 3.1 (81 pt)
  box x 1.0  w 8.0 · center y 2.64 in (47 % H) · align center
  color: line being said = text; lines to come = secondary at 53 %; no accent
  ```

### A8 Checklist

- **Measured (2 stage images)**: pictogram from 1.1 to 1.15 cap high, sitting on the baseline, 0.6-0.9 cap from the text; line spacing from 1.75 to 2.2 cap; text left-aligned in a centered block; pictograms in accent, text in the text color.
- **Values**:
  ```
  text: size 34 pt · weight 600 · left-aligned · line spacing k = 1.95
  pictogram: height = cap × 1.12, sitting on the baseline · gap 0.75 × cap · accent color
  centered block: width = longest line + pictogram; center y 2.64 in (47 % H)
  ```

### A9 Object + text

- **Measured (3 images)**:
  - the object fills 59 % W, bleeding off the left edge, over the full height; or a centered device (25 % W × 91 % H) with the text on the right;
  - the statement: cap from 5.8 to 6.1 % H, in semibold, 1 or 2 lines, **centered in the free column** (center at 80-81 % W), line spacing of 1.50 cap, center at 50 % H;
  - the variant with an icon: icon of 21 % W × 38 % H centered at 22 % W; three lines with a cap of 4.2 % H, left-aligned at 45 % W, line spacing of 1.8 cap.
- **Values**:
  ```
  object: x 0 → 5.6 in (may bleed off the left, top and bottom), h up to 5.625 in
  statement: size 34 pt · weight 600 · line spacing k = 1.5
             column x 6.3  w 3.4 (center 8.0 in) · align center · center y 2.81 in
  icon variant: icon 2.1 × 2.1 in centered at (2.2 in, 2.81 in)
                lines: size 24 pt · left-aligned at x 4.5 in · line spacing k = 1.8
  ```

### A10 Full-frame screenshot, A13 Product alone

- **Measured**: device centered over 89 to 100 % H, bleeding off the top and bottom on 1 image out of 3, with no added text (3 images). Product alone centered over 60 to 86 % H, on a solid light background, with no visible shadow (3 images).
- **Values**:
  ```
  screenshot in a generic device: height 5.0 to 5.35 in, centered · no text
  bare screenshot (convention): 82 to 88 % H, rounded corners 0.12 in, no frame
  product alone: height 3.4 to 4.8 in, centered · no shadow on a dark background;
                 on a light background, at most a very soft contact shadow
  ```

### A3 Typographic agenda

- **Measured (3 images)**: 5 or 6 stacked names, with a cap from 7.0 to 13.2 % H depending on the number of lines; line spacing from 1.35 to 1.77 cap (median 1.41); centered, or right-aligned at 70-78 % W; each name in its own color.
- **Values**:
  ```
  size (convention within the measured range): 6 lines → 44 pt; 5 → 56 pt; 4 → 68 pt; 3 → 80 pt
  line spacing k = 1.4 · weight 600 · align center (or align right, right edge at 7.6 in)
  color: the current block in accent, the others in text; when coming back, the others in secondary
  ```

### A14 Bento: the recap grid

- **Measured (5 images)**:
  - gutter of 5 to 6 px on 640, that is 0.8 to 0.95 % W; outer margin of the same order (0.6 to 1.25 % W), or tiles cut by the frame;
  - corner radius from 1.2 to 2.3 % W (median 2 %), **the same for every tile**, small or large;
  - center tile of 32 to 49 % W × 31 to 48 % H, centered on (50 %, 50 %), two to three times larger than the others; 8 to 19 tiles in all;
  - tiles **with no border or shadow**, flat: white on a light gray background (3 images), light gray on a white background (1 image), very dark gray on black (1 image, about 12 % white);
  - name in the center tile: cap from 7.4 to 10.8 % H, in white on a flat color or a color gradient; tile labels: cap from 1.4 to 1.9 % H; tile figures: cap of about 9 % H, in accent.
- **Values**:
  ```
  outer margin 0.09 in · gutter 0.085 in · radius 0.20 in (and at most 25 % of the short side)
  center tile: about 3.9 × 2.25 in, centered · flat accent · name in white (or fond_sombre
               if the contrast requires it), size 48 to 60 pt, weight 600
  other tiles: grid of 4 or 5 columns × 3 or 4 rows, uneven sizes
               flat = fond_clair lightened toward white (on light); text mixed at 12 % (on dark)
  tile label: size 11 to 12 pt, weight 500, secondary, at the bottom of the tile
  tile figure: size 48 pt, weight 600, flat accent
  ```
  The bento is the only slide where text goes below 3 % H: it is looked at, not read.
- **`fragments-logiciel` variant, measured (5 recaps from developer sessions, outside the corpus, to the pixel on 1,920 × 1,080)**:
  - outer margin from 46 to 60 px, that is 2.4 to 3.1 % W, and 4.1 to 5.6 % H at the top and bottom;
  - gutter from 12 to 20 px, that is 0.6 to 1 % W;
  - 5 to 16 tiles. The tiles in framework recaps are flat; those in platform recaps carry gradients, which the skill does not keep.
- **`fragments-logiciel` values**:
  ```
  margin 0.21 in · gutter 0.094 in · 12-column grid · rows 300 / 352 / 312 (out of 1080)
  center tile: columns 5 to 8, middle row · fond_sombre on a light deck, accent on a dark deck
               title 30 pt (18 at least), weight 600, 3 lines at most · text 9 pt regular
  fragment tile: name 16 pt (11 at least), weight 600, top left · line 9 pt regular, secondary
                 component at interface size (1 px = 1/192 in) × echelle · 0.5 pt rule, no shadow
  figure tile: 96 pt (48 at least), weight 600, text color (the accent stays with the list)
  list tile: kicker 8 pt in capitals · lines 13 pt (8 at least), weight 600, set at the bottom · flat accent
  ```

### A17 Quote or testimonial

- **Measured (1 full-frame image, 2 on stage)**: 2 to 4 lines in semibold, **left-aligned** at 9.2 % W, over 76 % W at most; cap of 6.35 % H; line spacing of 1.48 cap; source in regular secondary, with a cap of 4.7 % H (0.75 times the quote), 9.5 % H below the last baseline; block centered at 50 % H. On stage, the source is sometimes in accent.
- **Values**:
  ```
  quote: size 36 pt · weight 600 · align left · line spacing k = 1.5
         box x 0.92  w 7.6 · block centered at 2.81 in
  source: size 26 pt · regular · secondary (or accent, then the slide's only accent)
          cap top 0.53 in below the last baseline
  ```

### A19 Price

- **Measured (3 images)**: the name and the price have almost the same size (price at 0.82-1.0 times the name); the small “starting at” is 0.36-0.42 times the name, in regular secondary, right above the price.
  - “Top” layout (1 image): name with a cap of 7.4 % H, cap top at 12.8 % H; price with a cap of 6.1 % H; object below, from 50 to 87 % H, over 56 % W.
  - “Right column” layout (1 image): text centered at 70 % W; object on the left, from 12 to 39 % W, over 91 % H; 14 % H between two offers.
  - Hero price (1 image, a service offer): the price is treated like an A5 figure (cap of 27 % H), with the period below with a cap of 3.3 % H.
- **Values**:
  ```
  name: size 40 pt, weight 600 · small “Starting at”: size 16 pt, regular, secondary
  price: size 36 pt, weight 600 · detail (before tax, period, capacity): size 16 pt, regular, secondary
  gaps: name baseline → top of the small line: 0.48 in (“top”) or 0.25 in (“column”);
        small line baseline → price top: 0.16 in;
        price baseline → detail top: 0.16 in; between two offers: 0.79 in
  “top”: name cap top at 0.72 in · object from 2.7 to 4.9 in high, ≤ 6.0 in wide, centered
  “right column”: text centered at x 7.0 in · object x 1.1 → 3.9 in, h ≤ 5.1 in
  price alone for a service: apply A5 (144 pt), period at size 18 pt, regular
  ```

### A20 Availability

- **Measured (4 images)**: small gray label, in regular, with a cap from 2.7 to 3.1 % H, above a semibold word with a cap from 5.8 to 7.9 % H (ratio 0.38-0.46); 2.7 to 3.7 % H between the label baseline and the top of the word; block at the top (label top at 6-12 % H); lineup of objects below, from 27-38 % to 82-90 % H, over 61 to 92 % W, centered.
- **Values**:
  ```
  label: size 16 pt · regular · secondary · cap top at 0.45 in
  word or date: size 40 pt · weight 600 · cap top 0.19 in below the label baseline
  visual: from 1.6 to 5.0 in high, ≤ 9.2 in wide, centered, set at the bottom at 5.0 in
  no visual (convention): label at 24 pt and word at A1 size (100 pt), block centered at 2.81 in
  ```

### A21 Name and role lower third (video and stage shots)

- **Measured (3 images)**: name in bold and role in regular, **at the same size** (cap from 2.8 to 3 % H); left edge at 5.2-5.6 % W (right edge at 94.7 % W in the right-hand variant); baselines at 84.4 and 90.3 % H; white on the image, with no background or shadow.
- **Values**:
  ```
  name: size 16 pt, bold · role: size 16 pt, regular · white · no background
  x 0.54 in (right variant: right edge at 9.47 in, align right)
  baselines at 4.75 in and 5.08 in
  ```

### A6 Comparison chart

- **Measured (2 images)**: title with a cap from 4.5 to 5.5 % H, in semibold, centered at the top (cap top at 7.5-12 % H); thin curves and bars, 1.1 % H thick; tags with a cap from 4.0 to 4.2 % H, at the end of the bars; yourself in color, the other in gray at 45 %; bars from 15 to 85 % W.
- **Values**:
  ```
  title: size 28 pt · weight 600 · cap top at 0.5 in · centered
  chart area: x 1.5 → 8.5 in, y 1.9 → 4.3 in
  bars and curves: thickness 0.06 in (4.5 pt), rounded ends
  tags: size 23 pt, weight 600, at the start and end of the bars; axes: 16 pt, regular, secondary
  yourself: flat accent (the gradient stays with the hero figure) · the other: gray at 45 %
  ```

### A16 Partner logos

- **Measured (2 images)**: single-color logos from 5 to 10 % H high; rows every 17 to 22 % H; grid over 78 to 83 % W, centered; 3 to 5 logos per row, 4 or 5 rows.
- **Values**:
  ```
  logo height 0.28 to 0.56 in · rows every 1.0 to 1.2 in · 8.0 in grid, centered
  color: text (single-color logos) · no added text
  ```

### Final slide

- **Measured (2 images)**: a single centered sign, 27-28 % H high, centered at 47.5 % H; below it, at most one line with a cap of 4 % H, baseline at 89 % H; tiny gray legal notes at the bottom; solid dark background, or a sky photo (1 image).
- **Values**:
  ```
  the user's logo (height 1.55 in) or a word at A1 size (100 to 120 pt, weight 600)
  center y 2.67 in (47.5 % H) · final period in accent for a word
  one line below (optional): size 22 pt, regular, baseline at 5.0 in
  sources and legal notes: size 9 pt, secondary, baseline at 5.29 in
  background: solid fond_sombre; or a full-page accent, the only one in the whole deck, with text
              in fond_sombre if the contrast reaches 4.5:1 (convention, kept from the control deck)
              and if theme.finale_accent is not false (brand guidelines that cap the accent area)
  ```

### Kicker, in every text archetype

- **Measured (6 images)**: 0.36 to 0.46 times the title's cap (median 0.41); placed 0.44-0.48 cap above the title; in regular, secondary gray; same alignment as the title. Only once in accent and in bold capitals (a definition).
- **Values**:
  ```
  size = 0.42 × title size, kept between 16 and 28 pt
  baseline at 0.45 × title cap above the title's cap top
  weight: regular if gray; semibold if in accent (deck-spec choice)
  in accent, it is the slide's accent along with the final period, nothing else
  ```

### Markers on screen (§3.15)

| Marker | On screen |
|---|---|
| `[TO VALIDATE: proposed text]` | The proposed text, without brackets, in its field's normal style: nothing sets it apart. |
| `[TO PROVIDE: label]` | The label alone, 3 words at most, **in the field's style and size** (title, figure, price, date), **faded** at every size (color of the text it replaces, 40 % opacity, never a gradient; a missing figure or accent word switches to the text color, because the accent at 40 % turns brown on a dark background) and underlined with a dotted accent line: it reads as a slot, not as content. Never a box, a pink background or a gray frame. |

French decks use `[À VALIDER : …]` and `[À FOURNIR : …]`, rendered the same way.

- Up to 26 pt: pptx `underline: { style: 'dotted', color: ACCENT }` on the marker's span (pptxgenjs 4 writes `u="dotted"` and `a:uFill`); HTML preview `text-decoration: underline dotted #ACCENT; text-decoration-thickness: max(2px, .05em); text-underline-offset: .12em`.
- Above 26 pt (title, figure, price, date): a font's underline grows with the size (Arial: 0.07 em, that is a row of 10 pt dots under a 144 pt figure, seen in iteration 2). The engine removes it from the text and places a **dotted rule of fixed thickness** below: 1.5 pt, `sysDot`, accent at 70 %, 0.085 em below the baseline (between 3 and 12 pt), over the estimated width of the marker. The same rule in the .pptx (a shape named “Underline”, animated with its text) and in the preview, each placed for the font it shows: the font written for the .pptx, the fallback when the preview does not have it (`STYLE.marqueur.chasse`, measured gap: 0.1 in at most).
- Canva loses the opacity on import: with `meta.format` set to `canva`, the label keeps its brackets (`[date]`), the only slot sign that survives. The dotted rule covers them.
- A `[TO PROVIDE]` written inside an `*accent*` stays a marker: text color at 40 %, never the text in full or the accent. An A8 line that is only a marker keeps its empty box, with no check mark.
- A missing main field (title, lines, figure, quote) gets a label taken from the slide: the start of `textes.attendu` (without an article or “slide of”), otherwise, for an AF slide, its identifier (`s13-garanties` → “Garanties”). Never the field name (“title”, “lines”, “content”): those are workshop words.
- The marker follows its field's fitting (floors included). A missing image is replaced by a schematic interface (§5.2), never by a gray frame.

---

## 4. Color

### 4.1 One accent color per slide

- **Measured**: none of the 67 images carries two accent colors, except agendas, bentos, logo walls, screenshots and photos.
- The accent goes on **one element, two at most**: the name (A1), the figure (A5), your own bar or curve (A6), the pictograms (A8), the current line (A3), one word of the sentence, the kicker and the final period, the source of a quote.
- Never on running text, labels, list lines or legal notes.
- `accent2` is only used for the hero figure gradient: it is not a second accent color.

### 4.2 The gradient, reserved for the hero figure

- **Measured (4 figure slides out of 6)**: the gradient is **horizontal, from left to right**, with two stops. It goes from a deeper hue on the left to a lighter or neighboring hue on the right: purple to magenta, navy to blue, pink to orange, graphite to gray. The two stops are less than 65° of hue apart, or of the same hue with 15 to 22 points of luminance between them.
- The corpus also uses it on some names, on the agenda, on your own curve and on the bento center tile. The skill keeps it **for the A5 figure only**: it stays rare, so it stays strong.
- It goes from `accent` to `accent2`. Without `accent2`, the figure is a flat accent. Each stop must keep a contrast of at least 3:1 with the background (text above 24 pt).
- pptx (pptxgenjs cannot do a text gradient): in post-processing, the engine replaces the `a:solidFill` of the figure's `a:rPr` with
  ```xml
  <a:gradFill rotWithShape="1"><a:gsLst>
    <a:gs pos="0"><a:srgbClr val="ACCENT"/></a:gs>
    <a:gs pos="100000"><a:srgbClr val="ACCENT2"/></a:gs>
  </a:gsLst><a:lin ang="0" scaled="0"/></a:gradFill>
  ```
  HTML preview: `background: linear-gradient(90deg, #ACCENT, #ACCENT2); -webkit-background-clip: text; background-clip: text; color: transparent`.
- Keynote and Canva read a text gradient from a .pptx badly. So the `keynote` or `canva` format uses the flat accent.

### 4.3 Backgrounds

- **Solid background, never a pattern, a texture or a gradient.** The blurry, colored backgrounds of the corpus (1 keynote out of 8) are not reused: keep the flat color.
- One background per block. It only changes between two blocks, and never for a single slide in the middle of a block (iteration 1 switched to white for 6 slides).
- Full-bleed photo (A18): edge to edge, with no frame or rounded corners.

---

## 5. Images, shapes and interfaces

### 5.1 Rules

- **Never a frame or border around text** (0 cases out of 67). Tiles stand out by their flat color, with no line.
- **No shadow on text.** No drop shadow on a dark background. On a light background, at most a very soft contact shadow, under an object.
- Objects may run off the frame (A9, A10: 2 cases out of 6). A whole object, centered, floating in the middle of an empty area, looks less like a keynote than an object cut by the edge.
- Rounded corners: 0.20 in for tiles, 0.12 in for a bare screenshot (convention), 0 for a full-bleed photo.

### 5.2 Schematic interface, when a screenshot is missing (convention)

The engine draws it from `image.attendu`. It says “a screen goes here”, without inventing anything.

```
card: a screen in light mode, whatever the slide's background
      on a dark background: fond_clair (white if it does not reach 7:1); inner fills gray at 4.5 %
      on a light background: white; on a pure white background: gray at 5 %, white inner fills
      radius 0.12 in · no line
content: gray bars (text mixed at 22-38 %), height 0.08 in, round ends,
         lengths 100 / 72 / 48 % of the usable width, one every 0.16 in
only one thing in accent (the thing being talked about): the highlighted row, tinted with accent at 22 %,
         with its status dot in accent; an accent bar, or a solid dot with a dark
         outline if the accent is too light on the card (below 1.8:1: yellow on white)
no text, no figure, no amount, no date, no customer name, no logo
shadow: none on dark; on light: blur 0.3 in, offset 0.08 in, 12 % black
generic device (if needed): rectangle with corners at 13 % of the width, border at 3 %, black glass
         and a light edge of 0.75 to 1.75 pt, no notch, no buttons: nothing that suggests a real device
photo: flat color slightly lighter than the background, two neutral glows; no accent reflection (it turned khaki)
image tile (wall, bento): flat color close to the tiles, never a light screen in the middle of the wall
```

Iteration 2, first version: a dark card at 8 % and bars at 25-35 % read as a loading screen, and the yellow accent bar disappeared on a white background. The control deck made without the skill, judged more “keynote”, placed light screens on a dark background.

Position and size: those of the image it replaces (A9: the object's area, but the screen stays whole, 0.5 in from the edge, while an object may run off the frame; A10: 82 to 88 % H, centered).

---

## 6. Motion

Durations cannot be measured on still images: they are conventions. The manner, though, is observed (the corpus analysis).

| Moment | Observed | Engine value |
|---|---|---|
| Between two slides | fade (title cards, sentences) | fade transition, 0.5 s (convention) |
| The same screen changing (availability word, next line, a figure that transforms) | change on the same image | Morph (PowerPoint) between two slides with objects of the same name; fade as fallback |
| Hero figure | it comes in blurred and zoomed, then settles; or the label first | Zoom or Fade entrance, 0.4 s, on click |
| List | line by line | one Fade entrance per paragraph |
| Bento | the center tile first, then the others | center tile on click, the others after it |
| Price | the name, then the price | two beats |

pptx: pptxgenjs sets no transition and no animation. In post-processing, the engine inserts `<p:transition spd="med"><p:fade/></p:transition>` after each slide's `</p:clrMapOvr>`. The Morph goes through an `mc:AlternateContent` that contains `p159:morph` and a `p:fade` fallback. Validate the file with `validate.py` after this post-processing.

---

## 7. Visual check: what to verify on the screenshots

1. The main text reaches its size: cap ≥ 14 % H in A1, ≥ 8 % in A4, ≥ 20 % for the A5 figure.
2. The block center falls between 44 and 56 % H, except for A6, A19, A20 and A21.
3. Two levels of text at most. Nothing below a 3 % H cap, except bento and legal notes.
4. One accent color; a gradient only on an A5 figure.
5. No frame, no border, no dotted box, no pink background, no gray frame.
6. Titles are no bolder than semibold (except Arial Bold, for lack of anything better).
7. The same background from one end of the block to the other.
8. Nothing from the workshop on screen: no archetype, no step, no instruction.

---

## Appendix A. Measurement method (to redo it)

1. Each image (640 × 360, or 960 × 540 scaled to 640) is converted to luminance with ffmpeg. The background is the median of the border. A pixel is “ink” if it differs from the background by more than 30 to 60 levels (or by an absolute threshold, for white text on a photo).
2. Text lines are the bands of rows that contain ink. For each band: the top (first inked row), the baseline (last row inked at 25 % or more of the maximum, which drops descenders), the width and the center.
3. The height measured this way is 5.5 % above the true cap (antialiasing and ascenders). The factor was calibrated on 19 renders of known cap. Every cap in this file is corrected.
4. Stem: the median of the horizontal ink runs in the middle zone of the letters, divided by the cap.
5. Weight and tracking: the same text is rendered in each candidate font, at the same cap and the same scale, with Playwright, then measured by the same script. The stem ratio gives the weight. The width gap, divided by the number of intervals between letters, gives the tracking in em. A second render, at 1.5 times and then scaled down like the corpus images, gives the same values to within ±0.005 em above 28 pt. Below 28 pt, the gap reaches 0.025 em (two strings only): it is the least reliable column of §2.2.
6. Bento: gutters are the background runs between two tile fills (classified at the median threshold between background and tile); the radius is derived from the number of rows where the tile edge pulls into the corner (r − √r = n).
7. Limits: 1 px is 0.28 % H; stage images are only used for ratios (weight, color, alignment), not for sizes.

## Appendix B. Measured images, by archetype

Paths relative to the analysis image folder (`fr/vN/…`, as in `data/archetypes.json`). They are not copied into the skill.

| Archetype | Images |
|---|---|
| A1 | v1 frame_0321 · v3 frame_0075 · v7 frame_0162 · v8 frame_0339 |
| A4 | v3 frame_0543 · v2 t1641 · v2 t1562 (stage) · v4 t3120 |
| A5 | v1 t3420 · v3 t355 · v2 t1940 · v2 t738 · v7 t420 · v4 t556 · v6 t1751 (stage) · v2 t2310 (stage) |
| A7, A8 | v2 t995 · v4 t472 · v7 t4420 (stage) · v5 t1605 (stage) |
| A9 | v3 t1325 · v8 t262 · v8 frame_0132 · v5 t2270 (stage) |
| A10, A13 | v1 frame_0054 · v2 frame_0328 · v3 frame_0282 · v3 frame_0134 · v4 frame_0354 · v2 t1420 |
| A3 | v7 t320 · v8 t785 · v1 t338 |
| A14 | v1 t1900 · v2 t1735 · v3 t1372 · v7 t2550 · v8 t2924 |
| A17 | v1 t1505 · v6 t6960 (stage) · v5 t435 (stage) |
| A19 | v2 t1721 · v4 t1753 · v5 t1296 (stage) · v6 t6080 (stage) |
| A20 | v2 t2493 · v3 t1750 · v7 t3852 · v8 t5344 · v6 t8105 (stage) |
| A21 | v2 t330 · v3 t304 · v7 frame_0232 |
| A6 | v2 t606 · v1 t4795 · v2 t683 |
| A16 | v1 t3660 · v8 t1990 · v5 t3255 (stage) |
| Final slide | v7 t6200 · v8 t5539 |
| A2 (seen, not measured) | v7 frame_0791 · v8 t1097 · v6 t2450 |
