# Condensed grammar: an “Apple-style” presentation

> The skill reads this file every time. It condenses an analysis of eight keynotes (flow, slides, announcement sequence, phrases) and the data in `data/`. When in doubt about a count, those files are the reference.
> This file holds only rules and [slot] templates, never a quote.

**How to read it.** “8/8” = observed in all 8 keynotes of the corpus. *Convention* = a choice made by the skill for a consistent render, not an observation. The `id` values A1 to A25 are those of `data/archetypes.json`.

## Art direction

Read `style-visuel.md` before writing the first text: it shows what a good slide looks like, and the engine follows it. What makes the look, in short:

- **Very short, very large titles**, bold, tight line spacing. One word or one sentence per screen, never a paragraph.
- **An accent kicker** (1 to 3 words) above the title when it places the moment, and the title's final period in accent.
- **At least one visual moment per block**: a giant figure, an interface, a recap grid. And a strong final slide.
- **One design per slide**: the archetype and its variant, chosen in `designs.md` from the content and the visuals available. Never the same composition three times in a row.
- **A screenshot is missing?** A drawn schematic interface takes its place, on the slide's background: gray bars, not numbers. Never an empty frame.
- **A single background** for the deck; change it only between two blocks.
- **Nothing from the workshop on screen**: no archetype name, no step number, no instruction. A `[TO VALIDATE]` shows as real text; a `[TO PROVIDE]` fits in 3 words.
- **The look, never the brand**: no Apple font, logo, image or device.

## Contents

0. Art direction (above)
1. The rules that don't move
2. The standard run of show (blocks, roles)
3. The scale table by length
4. The announcement sequence (16 steps, short versions, variants)
5. Building the slides (rules, 16:9 grid, builds by format)
6. The archetype catalog
7. Phrases by function (EN, FR, register)
8. When the deck is in French
9. Rhythm

## 1. The rules that don't move

1. **The same person opens and closes** (8/8).
2. **Every block closes with a recap** (8/8).
3. **Every announcement has a name and a mini-recap** (8/8). The rest of the sequence is set by the length.
4. **One idea per screen, shown at the moment it is said** (8/8).
5. **The biggest topic goes last.**
6. **Nothing that can be checked is invented.** Figure, price, percentage, date, client name, logo, testimonial, real screenshot, source: the user provides it. Otherwise the skill writes `[TO PROVIDE: label]`, 3 words at most on screen, and puts the full instruction in `a_fournir`.
   **What can be written is proposed.** When the brief is thin, the skill writes the thesis, the titles, the problems, the feature descriptions and the script itself, and marks each proposal `[TO VALIDATE: …]`. On screen, it shows as real content; in the notes, it stays flagged; at delivery, the user validates it. A proposal never contains a figure, a price, a date or a name: those stay `[TO PROVIDE]`.
7. **The grammar, never the brand.** No Apple logo, font, image, device, slogan or signature phrase. The colors, fonts and product are the user's.

## 2. The standard run of show

| # | Block | Function | Share of time | Who speaks | Archetypes |
|---|---|---|---|---|---|
| 0 | Holding card (optional) | Keep people waiting, set the tone | 5 to 10 s | nobody | A1 |
| 1 | Opening video (optional) | Set the tone. No announcement in it (0/8) | 0 to 5 % (corpus: 65 to 143 s) | nobody | A18, video |
| 2 | Welcome | Greet, name the place, say what the day means in one sentence, give the menu | 5 to 10 % | the host | A24 or A22, A3 |
| 3 | Aside (optional, 45 min and more) | Off-topic news of the day: a recent success, a figure for the year | 2 to 4 % | the host | A5, A18 |
| 4 | First handover | The host hands over | before 15 to 20 % of the time | the host | A21 |
| 5 | Blocks (1 to 6) | Announce, prove, quantify, with the sequence in §4 | 60 to 75 % | pivot and experts | all |
| 6 | Last block | The biggest topic, announced as such or reached in a crescendo | 20 to 35 % of the total (taken from the blocks) | the host opens it | A1, A13, A5 |
| 7 | Overall recap and dates | Sum up the day, give all the dates again | 3 to 5 % | the host | A14, A3 again, A20 |
| 8 | Close | Thank the audience, then the teams; final sentence | 1 to 3 % | the host | A24 or A22 |
| 9 | Final card | Legal notes, sources, terms, credits, contact | 5 to 15 s | nobody | final card (§5.1) |

**The roles.**

| Role | On the user's side | What they do | Rule |
|---|---|---|---|
| Host | executive, founder, product lead, project lead | opens, sets the thesis, announces the biggest names, closes | no name caption (A21): people know them |
| Pivot (optional, from 30 min) | a second lead | opens each block, takes back the floor after each expert, does the block recaps | when there is one, they speak longer than the host (5/5) |
| Experts | the people who did the work | one or two turns: detail, demo | name caption on the first turn; their role says their scope |
| Guests | client, partner | a testimonial | guest card; real and agreed to |

- **Two ways to be the host.** *Master of ceremonies*: comes back between each block, gives a one-sentence verdict and hands over (the default with no pivot). *Frame*: opens, comes back for the big moment, then closes; the pivot does the bridges.
- **The handover goes up and down in steps**: expert → pivot → host. A sideways handover (from one expert to another) works when two topics follow each other, especially on video.

## 3. The scale table by length

| Length | Blocks | Screens (guide) | Voices and handovers | Opening | Announcement sequence | Recaps | Demo and proof | What to drop |
|---|---|---|---|---|---|---|---|---|
| 5 min | 1 | 10 to 14 | 1 voice (2 at most), 0 or 1 handover | 15 to 30 s, no video (card of 5 s at most) | short, 6 steps | N2 merged into the close | 1 demo of 60 s or 1 figure | video, aside, contents, bonus, third-party proof (keep 1 logo or 1 sentence) |
| 10 min | 1 or 2 | 18 to 25 | 2 voices, 2 or 3 handovers | 30 to 60 s; video of 15 to 30 s possible | 8 steps for the main block, 6 for the other | N2 per block, N4 | 1 demo of 2 min, 1 third-party proof | aside, contents, name story |
| 20 min | 2 or 3, the last one the biggest | 35 to 45 | 2 to 4 voices, 5 or 6 handovers | 1 to 2 min; video of 30 to 60 s | 16 steps for the last block, 8 for the others | N2, N4 | 1 or 2 demos, 1 testimonial | aside |
| 30 min | 3 or 4 | 50 to 65 | 3 to 5 voices, 8 to 10 handovers; a pivot possible | 2 to 3 min; video of 45 to 90 s; A3 contents | 16 steps for 1 or 2 blocks, 8 for the others | N1, N2, N4 (N3 if two parts) | 2 or 3 demos, 1 or 2 testimonials | the aside, if it doesn't serve the thesis |
| 45-60 min | 4 to 6 | 80 to 120 | 4 to 8 voices, 12 to 20 handovers; host and pivot | 3 to 5 min; video of 60 to 120 s; aside possible; contents shown again before the close | 16 steps per major block; rapid-fire mode for small new things | all 4 levels | 3 or 4 demos, 2 or 3 testimonials; last block announced as an event | nothing |

- **Screens** = distinct screens, not the states of a build. Reference pace (*convention*): about 2 screens per minute, never more than a minute on the same screen outside demos and videos.
- **Fewer people than handovers?** Change *mode* instead: demo, video, testimonial, question to the audience.
- **Merges under 10 min.** Anchor and tension in one sentence. Promise and name together. Recap, availability and close in three sentences.

## 4. The announcement sequence

### 4.1 The 16 steps

| n | Step | What it does | Visual | Length | In the short version |
|---|---|---|---|---|---|
| 1 | Topic opening | Say the topic is changing, name the area | A1, A2 | 3 to 15 s | merged into 2 |
| 2 | Anchor | Recall what exists and works: status, legacy, usage figure | A5, A13 | 20 s to 2 min | yes, one sentence |
| 3 | Tension | Open a gap: a moment from life, the flaw of current solutions (without naming them), a “what if” question | A10, empty A8 | 10 to 40 s | yes, merged into 2 |
| 4 | Promise | Say the answer is coming, without naming it | presenter | 2 to 15 s | merged into 6 |
| 5 | Reveal video | Show the object before explaining it | video, A13, A12 | 10 s to 2 min | no, except for a major announcement |
| 6 | Name | Set the word to remember, alone on screen, followed by a silence | A1, A2 | 1 to 5 s | **always** |
| 7 | Definition and verdict | What it does for the person, in one sentence; then a short judgment | A4, A13 | 5 to 20 s | yes |
| 8 | Handover to the expert | Go from the one who names to the one who details | A21, A22 or A24 | 5 to 40 s | no if one voice only |
| 9 | Pillars | For each strength: title, technology, benefit, figure, use case, short comment | A1, A5, A6, A9, A11 | 1 to 20 min | 1 to 3 pillars |
| 10 | Demo | Show the gesture and how easy it is | A10, A25 | 30 s to 5 min | 1 demo or 1 figure |
| 11 | Third-party proof | Let others speak: client, partner, press, logos | A16, A17, video | 20 s to 3 min | optional |
| 12 | Bonus | Add a bonus when people think you're done | next slide | 2 to 5 s | optional |
| 13 | Safeguard | Head off the objection: data, security, limits (languages, countries, beta) | A8, A4 | 10 to 40 s | if an objection is likely |
| 14 | Mini-recap | Close: the name and three strengths | A14, A7 | 5 to 25 s | **always** |
| 15 | Price and availability | How much, when, how to get it | A19, A20 | 10 s to 2 min | yes, if provided |
| 16 | Handover back | Give the floor back; the host gives a one-sentence verdict and moves on | presenter | 5 to 40 s | merged into the close |

In the corpus, each step exists in 8/8 keynotes, except tension (7/8) and price (5/8; availability is 8/8). An announcement does not use all 16: a software feature keeps about ten. **The order is a tendency**: you can move a step, never drop the name or the recap.

### 4.2 Short versions

**8 steps** (10 to 20 min, or a secondary block): ① anchor and tension (2+3) → ② promise and name (4+6) → ③ definition and verdict (7) → ④ 1 to 3 pillars (9) → ⑤ demo (10) → ⑥ third-party proof *or* safeguard (11 or 13), depending on the most likely objection → ⑦ mini-recap (14) → ⑧ price, availability and handover back (15+16).

**6 steps** (5 min): ① anchor and tension → ② name → ③ definition → ④ one proof (a figure *or* a demo) → ⑤ recap → ⑥ availability and call to action.

**Placing the name.** *Suspended*: a pause of one to two seconds before the word. *Late*: after the video or after a few features, for a second product in the same block. *Category first*: name the category, then the product. *Name story*: a question about the name, a short story, then the name (only if the name really has a story).

### 4.3 The four variants

| | Product | Software feature | Service | Technology |
|---|---|---|---|---|
| On the user's side | a device, a packaged offer, a major version | a feature in an existing product | a subscription, a service | an engine, a platform, a method, an AI |
| Length (corpus) | 5 to 25 min | 2 to 3 min | 15 to 34 min | 5 to 37 min |
| Who names it | the host, then handover to the expert | the block's presenter, no handover | the host; the expert gives the figures | the host, then the technical expert |
| Tension | low: the status of what exists is enough | short: a concrete moment from life | strong: the gap in the market (an empty A8 that gets checked all at once on the promise) | the legacy and what has changed |
| Video | before the name | no, except for a large project | mood video | abstract or principle video |
| Proof | figures against the previous version | first-person demo | success figures of what exists, partners | comparison chart, principles announced as “first, then, finally” |
| Price | yes, anchored on a true base | no | anchored on the total value of what it replaces | no |
| Availability | order date, delivery date | grouped at the end of the presentation | date and areas | transition schedule, prerequisites |
| Recap | name, 3 strengths, A14 | name, then “next” | name, definition, principles (A8) | 3 terms and a slogan line of the user's own |
| Typical order | promise, video, name, verdict, handover, pillars, options, recap, price, dates, back | opening, anchor, tension, name, definition, demo, bonus, safeguard, recap | long anchor, tension, promise, name, handover, demo, bonus, safeguard, price, availability, recap | legacy, principles, suspended name, definition, teaching, chart proof, bonus, safeguard, recap |

**Rapid-fire mode** for small new things: name, definition, next; 15 to 30 s each.

## 5. Building the slides

### 5.1 The rules

1. **A dominant plain background** (7/8), no texture. On the user's side: the darkest or lightest neutral of their palette. A single background for the deck (*convention*): change it only between two blocks, by category (dark for technology, light for use), never from one slide to the next within a block.
2. **A single sans-serif, bold or semibold, centered**: the one from the user's design system. With no font provided, a free sans-serif. Never an Apple font.
3. **One accent color per section or per product** (7/8), taken from the palette. A concept keeps its color from start to end.
4. **10 words at most per screen** (7/8), except lists, bento, walls, quotes and spec sheets. When translating, count after translation.
5. **One idea per screen, shown when it is said** (8/8). The only accepted gap: the date written out on screen, said in relative terms aloud.
6. **Figure slide: a giant figure alone**, with a one-line label that contains the comparison base.
7. **Chart**: yourself in color, the other in gray, a label at the end of each line, no separate legend, the gap written out. No axis ticks only if the audience allows it (`publics.md`).
8. **No note under a figure by default** (7/7): sources and terms go on the **final card** (8/8: logo, legal notes, sources, small and gray). Exception: the audience requires a visible source (`publics.md`).
9. **No bullets, no footer, no number, no logo on every slide.** The logo lives on the final card, and on the first slide if the brand guide requires it.
10. **Builds** (8/8): a list line by line, a chart in 2 to 4 beats (the other, then yourself, then the gap), the price after the name, a bento that assembles around its center tile, an availability word that changes on the same image. The engine turns them into fade-in builds, and each slide enters with a fade (*convention*).
11. **In the room**, everything can be read from the last row. **On video**, the slide lives full-frame, then on a screen in the set.

### 5.2 The 16:9 grid

The sizes below come from the corpus and from conventions. For the render, `style-visuel.md` wins if they differ.

- Reference 1920 × 1080 px; H = height, W = width. Margins: 6 % of W on the sides, 8 % of H at top and bottom (*convention*).
- **Observed** sizes: title-card word 10 to 17 % of H (110 to 180 px); giant figure 30 to 40 % of H (325 to 430 px); name in the caption about 4 % of H.
- **Convention** sizes: thesis sentence 6 to 9 % of H; label and list lines 4 to 6 %; price and large availability word 12 to 18 %; final-card notes 1.5 to 2 %. Nothing under 3 % of H, except the final card.
- Bold weight for titles and figures, regular for gray labels; tight line spacing (1.05 to 1.15) for titles. Text contrast: at least 4.5:1. The “not said yet” or “the other” gray: 35 to 45 % opacity.

### 5.3 Builds by format

- **Keynote, PowerPoint**: line-by-line builds; or one slide per state, linked by a morph (Magic Move, Morph).
- **Figma Slides, Canva**: one slide per state, linked by Smart Animate or Match & Move, otherwise by a fade.
- **Video**: each state becomes a shot; A21 becomes an overlay; A22 to A25 become shots to film. Between two sets, no hard cut: fade, match cut, camera move.

## 6. The archetype catalog

| id | Name | When | Layout (16:9) | Max words |
|---|---|---|---|---|
| A1 | Title card | open a chapter; set a name at the moment it is said | 1 to 3 centered words, 10 to 17 % of H; nothing else; plain background or the section's tint | 3 (5 at most) |
| A2 | Icon or logo + name | announce an app, a module, a service | icon at 30-45 % of H, centered or in the left third; name below or to the right, clearly smaller | 3 |
| A3 | Typographic contents | from 3 blocks: right after the welcome, shown again unchanged before the close | 3 to 6 block names, one per line, 8 to 12 % of H, right-aligned or centered, each in its color; when shown again, the current line in color, the others grayed | 3 per line |
| A4 | Thesis sentence | after a demo or a figure, to fix the benefit | 1 or 2 centered lines, 6 to 9 % of H, text only, no pictogram | 8 (10 at most) |
| A5 | Big figure + label | prove a benefit right after saying it | figure centered at 30-40 % of H with its unit (×, %, h); one-line label below, 4 to 6 % of H, comparison base included | the figure + 9 |
| A6 | Comparison chart | technical part: performance against a base | title at the top (5 to 7 % of H); chart in the center over 60 to 70 % of W; yourself in accent, the other in gray; a label at the end of each line or bar; gap written out | title of 5 + labels of 1 to 3 |
| A7 | List without bullets | list benefits; outline of a sub-chapter | 2 to 6 lines centered or left-aligned, 4 to 6 % of H; the line being said at full color, the next ones grayed | 5 per line |
| A8 | Checklist | trust, security, compliance; recap of a service | 3 to 6 lines, each preceded by a colored pictogram; or empty circles that get checked on the promise | 4 per line |
| A9 | Object + text | detail a feature or a characteristic | object or screenshot over 50 to 60 % of W; on the other side a word, a statement or 3-4 lines; annotated variant with leader lines to the object | 4 lines of 4 |
| A10 | Full-frame screenshot | any explanation of a software feature | bare screenshot or generic unbranded device, centered, 80 to 95 % of H; no added text; clean status bar, neutral demo data | 0 added |
| A11 | Diagram with a highlighted block | architecture, component, process | line diagram over 40 to 60 % of W; one block lit at a time, linked by a leader line to a side caption (a title, 5 gray lines at most) | title + 5 short lines |
| A12 | Inside view | show what is inside: layers, components | dark full-frame render, separated parts, slow motion | 1 label |
| A13 | Product alone | reveal, then backing for each characteristic | object centered at 50-70 % of H, soft shadow, background by category; no text | 0 |
| A14 | Bento | end of a block, during the recap sentence | center tile 2 to 3 times larger (name or object); around it, 8 to 20 rounded tiles of uneven sizes, each a visual and 1 to 4 words or a figure | 4 per tile |
| A15 | Wall of abundance | say “there are lots of them” without detail | dense grid that overflows the frame: integrations, screens, features, allowed logos; text deliberately too small | 0 to read |
| A16 | Partner logos | proof of adoption right after the announcement | single-color logos in a row or a regular grid (5 rows at most), no text; only those the user has the right to show | 0 |
| A17 | Quote or testimonial | social proof, opening a section or after a launch | 2 to 4 bold left-aligned lines, 5 to 7 % of H; source on one line below, in gray; real, authorized quote | 25 + the source |
| A18 | Full-bleed photo | emotion before the argument; proof of quality | photo over the whole frame; translucent caption at bottom right if it is a product example | 0 (+ caption) |
| A19 | Price | end of the block, right before availability | object on the left (40 to 50 % of W); on the right: name in bold, “From” small and gray, price large, detail in gray (before or after tax, period); 2 offers at most, 4 for a lineup | 6 per offer |
| A20 | Availability | last step of an announcement, or grouped at the end | small gray label (“Available”, “Starting”) above a large word or a date; object below or beside it; the large word changes on the same image | 4 |
| A21 | Name and role caption | first appearance of a speaker, never the host | two lines with no background at bottom left (right if the presenter is on the left): name in bold, role in regular; held 4 to 6 s | name + role |
| A22 | Wide shot + screen | stage or video: a breather, a speaker's entrance | full-length presenter on one side, 1/10 to 1/4 of H; screen with the slide over 50 to 70 % of W | — |
| A23 | Presenter in the slide | video: default speaking shot | presenter in a medium shot over one third; the slide fills the background, cut by the edge | — |
| A24 | Set without a screen | video: welcome, handover, framing | presenter centered in a place tied to the topic, full-length then medium shot | — |
| A25 | Hands-on demo | right after a feature is announced | hands holding the device in front of a plain background, or presenter at the demo desk with the screen large; alternate wide shot, hands, full frame | — |

A21 to A25 are shots, not slides: in the room, they become stage directions in the script; on video, shots to film.

This table says when to use each archetype. How to draw it (composition variants, visual content, depth, visual to prepare and fallback): `designs.md`, one card per archetype.

## 7. Phrases by function

### 7.1 Register: two separate settings

- **In English**, there is no tu or vous. The setting is the tone: first name only (casual) or first name, last name and role (formal). It shows mostly in the handover phrases (§7.7).
- **In French, toward the audience (P).** The skill asks. Vous is the rule in the French corpus (4/4). Tu works on video or in writing, when a single person is watching. In front of a room, the plural of tu is vous: keep vous, but make the tone casual (on instead of nous).
- **In French, between speakers (I).** The skill asks this too. The corpus uses tu between colleagues and vous with the audience. Vous between speakers suits a team that uses vous every day, or a guest from outside.
- The two settings combine. The most common case: tu between colleagues, vous to the audience.

In the tables: a single form = it holds for every register. The Variant column gives the casual English form or the French register forms: “P-tu” = audience addressed as tu; “I-vous” = speakers who use vous with each other. The FR column is the template for a French deck; keep it in French.

### 7.2 Opening and framing

| EN | FR | Variant | Note |
|---|---|---|---|
| Good [morning], and welcome to [place / event]. | Bonjour, et bienvenue à [lieu / événement]. | — | greeting + place (7/8) |
| Today is a [big] day for [X]. | Aujourd'hui est un [grand] jour pour [X]. | — | what the day means, in one sentence |
| We have [a lot] to [show you] today. | Nous avons [beaucoup] à vous [montrer] aujourd'hui. | P-tu: On a [plein de choses] à te [montrer]. | announces the menu (A3) |
| At [company], [value] [is / has always been] [X]. | Chez [entreprise], [valeur] fait partie de [X]. | — | thesis; only one per presentation |
| This year, we're [verb] [X]. | Cette année, nous [verbe] [X]. | casual FR: Cette année, on [verbe] [X]. | time marker (8/8) |
| Our goal was simple: [verb] [X]. | Notre objectif était simple : [verbe] [X]. | — | framing a block |
| Today, [X] [does A]. But [obstacle]. | Aujourd'hui, [X] [fait A]. Mais [obstacle]. | — | tension |
| What if you could [X]? | Et si vous pouviez [X] ? | P-tu: Et si tu pouvais [X] ? | tension; rare outside software |

### 7.3 Announcing the name and the verdict

| EN | FR | Variant | Note |
|---|---|---|---|
| Introducing [Name]. | Voici [Nom]. | — | bare form, set on the name alone (A1) |
| Today we're [launching / introducing] [X]. | Aujourd'hui, nous lançons [X]. | casual FR: Aujourd'hui, on lance [X]. | full form (8/8) |
| And we call it… [Name]. | Et nous l'avons appelé… [Nom]. | casual FR: On l'a appelé… [Nom]. | suspended name: 1 to 2 s pause |
| We're [proud] to [introduce] [X]. | Nous avons [le plaisir] de [vous présenter] [X]. | P-tu: On est [fiers] de te [présenter] [X]. | FR: pleasure rather than excitement |
| [Name] is the [simple] way to [benefit] without [pain]. | [Nom] est le moyen [simple] de [bénéfice] sans [douleur]. | — | definition (step 7) |
| [Name] is [truly] [adj]. | [Nom] est [vraiment] [adj]. | — | the host's verdict; no “I think” |

### 7.4 Superlatives (the register changes nothing)

| Level | EN | FR | Condition |
|---|---|---|---|
| 1. relative to yourself | our most [adj] [X] yet | notre [X] le plus [adj] à ce jour | true against your own versions |
| 1 | the [adj-est] [X] we've ever [made] | le [X] le plus [adj] que nous ayons jamais [conçu] | same; rather for a product |
| 1 | [adj-er] than ever | plus [adj] que jamais | same |
| 2. a first | for the first time, [X] | pour la première fois, [X] | must be true; add “for us” if in doubt |
| 3. absolute | the world's [first / fastest] [X] | le [premier / plus rapide] [X] au monde | external proof, cited |
| 3 | [industry-leading / best-in-class] [X] | la meilleure [X] du marché | external proof, cited |
| 3 | [X], by far | [X], et de loin | external proof, cited |

One superlative per announcement, at most. The dose by audience is in `publics.md`.

### 7.5 Figures and comparisons

| EN | FR | Note |
|---|---|---|
| [N] times [more adj] than [base] | [N] fois plus [adj] que [base] | the base is said **and** written in the A5 label |
| up to [N] [unit] | jusqu'à [N] [unité] | always with its condition (`publics.md`) |
| [N] more [unit] than [base] | [N] [unité] de plus que [base] | base: the previous version, preferably |
| [N]% [faster] than [base] | [N] % plus [adj] que [base] | FR: non-breaking space before “%” |
| That's enough to [concrete equivalent]. | De quoi [équivalent concret]. | turns the figure into real life |
| over [N] [million] [items] every [period] | plus de [N] [millions] de [objets] chaque [période] | usage figure, in the anchor |

### 7.6 Bonus and transitions

| EN | FR | Note |
|---|---|---|
| Now, let's talk about [X]. | Parlons maintenant de [X]. | universal connector (8/8) |
| Next, let's turn to [X]. | Passons à [X]. | change of block |
| And that's not all: [bonus]. | [Et] ce n'est pas tout : [bonus]. | often opens the best argument |
| [Before we close], one last [announcement]: [X]. | [Avant de terminer], une dernière [annonce] : [X]. | only once, for the biggest topic; never Apple's signature phrase or its translation |

### 7.7 Handover out and back

| Direction | EN | FR | Variant |
|---|---|---|---|
| Out | Here's [First name] to tell you [more]. | Voici [Prénom], qui va vous [en dire plus]. | P-tu: … qui va t'[en dire plus]. |
| Out | To tell you [more] about [X], here's [First name]. | Pour vous [en dire plus] sur [X], voici [Prénom]. | P-tu: Pour t'[en dire plus]… |
| Out, formal | Please welcome [First Last], [role]. | J'invite [Prénom Nom], [fonction], à me rejoindre. | — |
| Out, direct | [First name], over to you. | I-tu: [Prénom], je te [laisse] la parole. | I-vous: [Prénom], je vous [laisse] la parole. |
| Sideways | Now, over to [First name] to tell you about [X]. | Je [passe] la parole à [Prénom], qui va vous [parler] de [X]. | — |
| Taking the floor | Thanks, [First name]. | Merci, [Prénom]. | on video, the newcomer rather starts with a thesis |
| Back | Back to you, [First name]. | I-tu: À toi, [Prénom]. / Je te [rends] la parole. | I-vous: À vous, [Prénom]. / Je vous [rends] la parole. |
| Back, neutral | Now, back to [First name]. | Retour à [Prénom]. / Je [repasse] la parole à [Prénom]. | — |
| Host takes back | Thank you, [First name]. [Verdict]. | Merci, [Prénom]. [Verdict d'une phrase]. | — |

### 7.8 Demo

| EN | FR | Variant |
|---|---|---|
| Let's [take a look] at [X]. | Voyons [X] ensemble. | P-tu: Regarde [X]. |
| Let me show you [how X works]. | Je vais vous montrer [comment ça marche]. | P-tu: Je te montre [comment ça marche]. |
| I just [gesture], and [result]. | Il suffit de [geste], et [résultat]. | — |
| Check this out: [X]. | Et regardez : [X]. | P-tu: Et regarde : [X]. |
| As you just saw, [X]. | Comme vous [venez de le voir], [X]. | P-tu: Comme tu [viens de le voir], [X]. |
| [First name] will show you [X] live. | [Prénom] va vous faire [une démonstration] en direct. | P-tu: … va te faire [une démo] en direct. |

### 7.9 Testimonial and guest

| EN | FR | Note |
|---|---|---|
| We've been working with [partner] to [X]. | Nous travaillons avec [partenaire] pour [X]. | real partner, agreement obtained |
| Let's hear from [who]. | Écoutons [qui]. | before a testimonial video |
| It's [remarkable] to see how [product] helps [who] [X]. | C'est [remarquable] de voir comment [produit] aide [qui] à [X]. | the host's sentence after the testimonial |
| Here's what [client / outlet] says about [X]. | Voici ce qu'en dit [client / média]. | before A17; real, authorized text |

With no testimonial provided: `[TO PROVIDE: client testimonial]` on screen, and the instruction (who, about what, agreement obtained) in `a_fournir`. The skill never writes one, not even as `[TO VALIDATE]`.

### 7.10 Price and availability

| EN | FR | Variant |
|---|---|---|
| [Product] starts at [price]. | [Produit] est [disponible] à partir de [prix]. | — |
| [Product] starts at [price], [the same price as / less than] [base]. | [Produit] est [proposé] à partir de [prix], [au même prix que / moins cher que] [base]. | the anchor must be true |
| [X] will be available [date]. | [X] sera disponible le [date]. | — |
| You can [order / sign up] today; [X] ships [date]. | Vous pouvez [commander] dès aujourd'hui ; [X] arrive le [date]. | P-tu: Tu peux [commander]… ; on screen: [Commandez / Commande] dès aujourd'hui. |
| [X] is coming [later this year / next month]. | [X] arrive [plus tard dans l'année / le mois prochain]. | — |
| [X] is available [at no extra cost] [with Y]. | [X] est disponible [sans surcoût] [avec Y]. | — |
| Pricing and details [on date]. | Tarifs et détails [le date]. | when the price is not set yet |

### 7.11 Recap

| Level | EN | FR |
|---|---|---|
| N1 feature | So that's [X]. | Voilà pour [X]. |
| N2 product or block | So that's [Name]: [A], [B] and [C]. | Voilà pour [Nom] : [A], [B] et [C]. |
| N2 | And that's [Name], [one-line definition]. | Voilà pour [Nom], [définition]. |
| N3 part or lineup | Our [all-new] [X] lineup. | Notre [toute nouvelle] gamme de [X]. |
| N4 event | What a [big] day for [X]. | Quelle journée pour [X] ! |

### 7.12 Close

| EN | FR | Variant |
|---|---|---|
| We can't wait [for you] to [verb]. | Nous avons [hâte] que vous [verbe]. | casual FR: On a [hâte] que vous [verbe]. P-tu: On a [hâte] que tu [verbe]. |
| [Mission, said in the user's words]. | [Mission]. | echoes the thesis from the welcome |
| I'm [proud] of the teams who [made] [X] possible. | Je suis [fier / fière] des équipes qui [ont rendu] [X] possible. | thanks to the teams: name what they did |
| Thank you for [your time / being here]. | Merci [de votre attention / d'être venus]. | P-tu (video): Merci d'avoir regardé [X]. |
| Have a great [day / event]. | Excellente [journée / fin de salon] ! | P-tu: Passe une excellente journée ! |

## 8. When the deck is in French

In English, use the EN column as is and vary the phrases from one block to the next (point 8 below holds in every language). When the user writes in French (`"langue": "fr"`), use the FR column and these 11 rules:

1. **“Voici”** covers three English phrases: announcing the name, the reveal and the handover out. Then vary: “[Prénom] va vous [en dire plus]”, “Je [passe] la parole à [Prénom]”.
2. **“ever”** becomes “à ce jour” for a product, “depuis sa création” or “sans précédent” for software or a service.
3. **On screen, the imperative** for the call to action (“Essayez”, “Réservez”; P-tu: “Essaie”). **Aloud**, “vous pouvez” stays natural.
4. **Prices** in the audience's currency, in French format: number before the symbol, non-breaking space for thousands (1 099 €). State before or after tax (HT or TTC) and the period (/mois, /an). “Starts at” becomes “à partir de”.
5. **Dates** in French style: “le 19 mars”, never an ordinal except “le 1er”. On screen the date written out; aloud, “jeudi”, “le mois prochain”.
6. **Units** converted to metric (km, kg, °C); screen sizes stay in inches.
7. **Personal opinion fades**: “I think [X] is incredible” becomes “[X] est vraiment remarquable”. “We're excited to” becomes “Nous avons [le plaisir] de” (vous) or “On est [fiers] de” (casual).
8. **Vary where English repeats**: alternate the handover and transition phrases from one block to the next.
9. **Audiences named aloud** follow the user's style guide. By default: paired forms aloud (“celles et ceux qui…”), a gender-neutral word on screen rather than a midpoint (space and readability).
10. **Typography**: non-breaking space before “: ; ! ?” and “%”, « » quotes, decimal comma (1,5).
11. **French is longer** than English: recount the 10 words per screen after translation; cut rather than shrink the size. The on-screen text is translated too, word for word like the script.

## 9. Rhythm

1. **Change voice every 3 to 4 minutes** (6/6 when prerecorded), and hand over early (before 15 to 20 % of the time). With a single voice, change mode at the same pace: demo, video, testimonial.
2. **Open and close with the same person** (8/8). The close echoes the words of the opening thesis; the A3 contents slide is shown again unchanged.
3. **Keep the biggest for last.** The blocks build up, from the simplest to the strongest. The last is the longest (20 to 35 % of the total); you can announce it from the contents slide.
4. **Recaps are nested**, and each level echoes the words of the one below:
   - N1 feature, every 4 to 7 min, by the expert;
   - N2 product or block, every 6 to 16 min, with A14;
   - N3 part or lineup, 1 to 3 per presentation, by the pivot;
   - N4 event, once, by the host, right before the close.
5. **A recap before the handover back**, most often (2 times out of 3); otherwise a summing-up sentence.
6. **A silence after the name**: 1 to 2 s in the room; on video, a music hit or a silence. Don't fill it.
7. **A one-line summing-up sentence** at the end of each block, by the host or the pivot.
8. **In the room**, the video is started from the stage, on black. **On video**, no pause for applause: the presenter states the effect in one short sentence.
