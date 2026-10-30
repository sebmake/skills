# Keynote format (.key, 16:9)

Keynote opens .pptx files. So build the .pptx with `build_deck.js` (see `powerpoint.md`, section 1), then pass it through Keynote.

## 1. Open the .pptx in Keynote

- File > Open > `sortie.pptx` (or drag the file onto the Keynote icon).
- Keynote creates a new document. The original .pptx is not changed.
- Keynote then shows the list of import issues (replaced fonts, unsupported effects). Read it in full. It stays available later from View > Show Document Warnings.
- Save: File > Save. The file becomes a .key.
- Check the size: Document inspector > Slide Size. The ratio must be 16:9. The pixel count depends on the conversion (the .pptx measures 10 × 5.625 inches): don't change it if it is 16:9, because Keynote would resize the content.

## 2. What converts well, what converts badly

| Element | Result | What to do |
|---|---|---|
| 16:9 size, plain backgrounds, shapes, texts | Good | Nothing |
| Theme HEX colors | Good | Check one or two colors |
| Speaker notes | Good: they become the presenter notes | Review the formatting |
| Fonts installed on the Mac | Good | Nothing |
| Fonts missing from the Mac | Replaced on opening | Install the font, then reopen the .pptx (not the .key). Or Format > Font > Replace Fonts |
| PowerPoint animations | Variable: the engine's fades usually become Dissolve, sometimes lost | Check each slide that has a `build`; set the missing ones by hand (section 4) |
| Native charts | Variable | Check that no axis ticks appeared if the grammar doesn't want them |
| SVG images | Sometimes converted to a fixed image | Check the sharpness |

Never an Apple font (SF, New York) as a replacement, even if the Mac offers them.

## 3. Automatic conversion to .key (if Keynote is installed)

Do this only if Keynote is on the user's machine. Check first:

```bash
open -Ra Keynote && echo "Keynote present" || echo "Keynote missing"
```

The classic edition has the identifier `com.apple.iWork.Keynote`. The Creator Studio edition is called “Keynote Creator Studio” (identifier `com.apple.Keynote`). `tell application "Keynote"` finds both.

AppleScript to write in the working folder (`pptx-vers-key.applescript`):

```applescript
-- Usage: osascript pptx-vers-key.applescript /absolute/path/input.pptx /absolute/path/output.key
on run argv
	if (count of argv) < 2 then error "Usage: osascript pptx-vers-key.applescript input.pptx output.key"
	set entree to POSIX file (item 1 of argv)
	set sortie to POSIX file (item 2 of argv)
	tell application "Keynote"
		activate
		set doc to open entree
		set larg to width of doc
		set haut to height of doc
		set nb to count of slides of doc
		set avecNotes to 0
		repeat with s in slides of doc
			if (presenter notes of s as text) is not "" then set avecNotes to avecNotes + 1
		end repeat
		-- Optional, one line per slide concerned:
		-- set transition properties of slide 3 of doc to {transition effect:dissolve, transition duration:0.4}
		-- set transition properties of slide 7 of doc to {transition effect:magic move, transition duration:1.0}
		save doc in sortie
		close doc saving no
	end tell
	return "Slides: " & nb & " | with notes: " & avecNotes & " | size: " & larg & " x " & haut
end run
```

- The script has been neither compiled nor run against Keynote (Keynote was missing on the machine where the skill was written). Run it only with the user's agreement, and read the error if it fails.
- On the first run, macOS asks whether the terminal (or Claude) may control Keynote. The user answers. The skill never touches privacy settings.
- If Keynote shows a window (import warnings, first launch), the script waits. Tell the user they must close it.
- Expected result: a 16:9 size (width ÷ height = 1.78), and as many slides with notes as slides with a script.
- Transitions can be driven by AppleScript. Builds cannot: Keynote's dictionary does not expose them.

## 4. Builds to check in Keynote

The .pptx contains fades between slides and on-click builds (`build` field). Keynote usually converts them to Dissolve. Check slide by slide, and set by hand what is missing:

1. Select the object > Animate inspector > Build In > Add an Effect.
2. Choose Appear (hard) or Dissolve (soft). Duration: 0.3 to 0.5 s.
3. List: set Delivery to By Bullet or By Paragraph.
4. Order and trigger: Build Order button, start On Click.

| Archetype | Builds | Effect |
|---|---|---|
| A1 Title card, A4 Thesis sentence | The text alone, at the moment it is said | Dissolve |
| A5 Big figure | The figure, then the label (or the reverse, chosen once for the whole deck) | Dissolve, then Appear |
| A6 Comparison chart | The other (in gray), then yourself, then the written gap (2 to 4 beats) | Dissolve by element |
| A7 List without bullets | One line per click, at the pace of the voice | Dissolve by bullet |
| A8 Checklist | The checks one by one, or all of them on the promise sentence | Appear |
| A9 Object + text | The object, then the text | Dissolve |
| A11 Diagram with a highlighted block | One block lit at a time | Appear |
| A14 Bento | The center tile, then the others | Dissolve |
| A19 Price | The name, then the price (an anchor price before it, if the user provided one) | Appear |
| A20 Availability | The large word changes on the same image | Two slides and the Magic Move transition |

Transitions between slides: none, or a short Dissolve. No spectacular effect.

List the planned builds (`build` field of `deck.json`), with the effect from the table:

```bash
node "$SKILL/scripts/export_script.js" deck.json --etapes
```

Give this list to the user.

## 5. Presenting

- Start: Play > Play Slideshow.
- Presenter display: Play > Customize Presenter Display. It shows the notes, the next slide and the time.
- Rehearse: Play > Rehearse Slideshow. Compare with the sum of the `duree_s` values.
- On a video call: Play > Play Slideshow in Window, then share only that window.

## 6. Checklist before delivering

- [ ] Slide size is 16:9.
- [ ] The list of import issues was read; no font replaced without agreement.
- [ ] No Apple logo, image or font; only the user's branding.
- [ ] The presenter notes contain the script of each slide, the handover and the length.
- [ ] The builds from the table are set, or their list is given to the user.
- [ ] No invented figure, price, date or testimonial; the remaining `[TO PROVIDE]` markers are flagged.
- [ ] A constant tone (in French, tu or vous), as chosen at the start.
- [ ] A timed rehearsal fits in the planned time.
