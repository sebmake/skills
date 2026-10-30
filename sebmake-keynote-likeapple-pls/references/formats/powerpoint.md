# PowerPoint format (.pptx, 16:9)

The .pptx is the base format. Keynote, Canva and the Figma Slides import also start from it.
It is always 16:9: 10 × 5.625 inches (25.4 × 14.29 cm), PowerPoint's “On-screen Show (16:9)” size.

## 1. Building the file

The shared engine is `scripts/build_deck.js` (Node, pptxgenjs library). It reads `deck.json` and writes the .pptx and an HTML preview.

```bash
SKILL=~/.claude/skills/sebmake-keynote-likeapple-pls
[ -d "$SKILL/scripts/node_modules/pptxgenjs" ] || (cd "$SKILL/scripts" && npm install)
node "$SKILL/scripts/build_deck.js" deck.json sortie.pptx --preview sortie.html
```

- Run the command from the user's working folder, not from the skill.
- If `node` is missing: tell the user and deliver `deck.json` and the script. Don't install anything in their place.
- The script makes one slide per entry of `deck.json`, with the theme colors and fonts, and the spoken text in the notes.
- The .pptx always writes the theme fonts, even if they are missing on the machine that builds it. The console then says so, and the preview shows in the fallback font. Install the font on the machine that presents. `--polices repli` writes the fallback font instead.
- The `[TO PROVIDE]` markers stay visible on the slide, faded so they read as placeholders. Never replace them with an invented value.

## 2. Check the preview before sending

Open `sortie.html` in a browser. It is the fastest check.

- One idea per screen, 10 words at most outside lists.
- The giant texts (title card, big figure) don't overflow.
- The colors are the theme's (HEX given by the user or read from their design system).
- The preview uses the browser's fonts. The render in PowerPoint can differ: see section 3.

## 3. What the user checks on opening

**Fonts.** The .pptx names the fonts, it does not contain them.
- If a font is not installed on the computer, PowerPoint replaces it, often without warning.
- To see the file's fonts: Home > Replace > Replace Fonts (Windows), or Format > Replace Fonts (Mac).
- If a font is missing: install it (design system files), then reopen. Otherwise, replace it with the backup font chosen with the user.
- Never an Apple font (SF, New York) as a backup, even if it is installed.
- For a file that travels: embed the fonts. File > Options > Save > Embed fonts in the file (Windows); PowerPoint > Preferences > Save (Mac, recent versions). Only if the font's license allows it.

**The rest.**
- Size: Design > Slide Size > Custom Slide Size shows 25.4 × 14.29 cm (16:9). Don't choose “Widescreen”: it is also 16:9, but PowerPoint would resize all the content.
- Text that wraps: a replacement font is often wider. Review the titles.
- Colors: select a shape, Fill Color > More Colors, compare the HEX code.
- Markers: search for `[TO PROVIDE]` (Ctrl+F or Cmd+F). None should remain at delivery, or the user must know which ones remain. A French deck uses `[À FOURNIR]`.

## 4. Speaker notes

`build_deck.js` writes the script of each slide in its notes: the spoken text, the clicks (builds), the handover to the next speaker and the target length (`duree_s`).

- Show the notes: Notes button in the status bar, or View > Notes Page.
- Print the script: File > Print > Notes Pages.
- The tone (casual or formal; in French, tu or vous) was chosen by the user at the start. Check that it is the same in all the notes.

## 5. Presenter View

- Start: Slide Show > Use Presenter View, then From Beginning. Windows shortcut: Alt+F5.
- The presenter's screen shows the current slide, the next one, the notes and a timer. The audience sees only the slide.
- On a video call (Teams, Zoom, Meet): share the slide show window, not the whole screen. Otherwise the audience sees the notes.
- Rehearse with timing: Slide Show > Rehearse Timings. Compare with the sum of the `duree_s` values.

## 6. Builds: already set, to be checked

`build_deck.js` itself sets a short fade between slides and fade-in builds, on click, in the order of the `build` field (list lines, figure then label, tiles, price after the name). On opening, check them in Animations > Animation Pane, and adjust them if needed:

- Select the object > Animations > Appear (hard effect) or Fade (soft effect). Start: On Click.
- List: Effect Options > By Paragraph. One line lights up at each click.
- Order: Animations > Animation Pane.
- The large word that changes on the same image (availability) or the figure that transforms: two slides identical except for that word, and the Morph transition on the second one (Microsoft 365, PowerPoint 2019 and later). Otherwise, Fade.
- Transitions between slides: the short fade set by the engine. Nothing more.

The archetype → builds → effect table is in `keynote.md` (section 4). The matching PowerPoint names: Appear = Appear, Dissolve = Fade, Magic Move = Morph.

List the planned builds (`build` field of `deck.json`), slide by slide, with the recommended effect:

```bash
node "$SKILL/scripts/export_script.js" deck.json --etapes
```

## 7. Checklist before delivering

- [ ] The file is 16:9 (25.4 × 14.29 cm).
- [ ] The HTML preview was opened and reviewed slide by slide.
- [ ] No Apple logo, image or font; only the user's branding.
- [ ] No invented figure, price, date or testimonial; the remaining `[TO PROVIDE]` markers are listed for the user.
- [ ] The devices kept (chart without axis ticks, anonymous competitor, “up to”…) fit the declared audience.
- [ ] Each slide has its spoken text in the notes, with the handover and the length.
- [ ] The sum of the lengths fits in the planned time.
- [ ] A constant tone (in French, tu or vous), as chosen by the user.
- [ ] The list of builds to set by hand is given to the user.
- [ ] The user knows which fonts to install or embed.
