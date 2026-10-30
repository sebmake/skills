# Figma Slides format (16:9)

Here the .pptx is not used: the deck is built directly in Figma Slides with the `use_figma` tool (Figma MCP server). A Figma Slides slide is 1920 × 1080: it is already 16:9.

## 1. Prerequisites

**The tools.** Check that the session has the Figma tools: `use_figma`, `create_new_file`, `whoami`, `get_screenshot`, and to read a design system `get_design_context`, `get_variable_defs`, `search_design_system`. If they are deferred, load their schemas in a single tool search. If they are missing: tell the user (the Figma connector must be attached), and offer the backup path in section 6.

**The Figma skills, to load before any `use_figma` call.** In this order:
1. `figma-use`: the Plugin API rules (required before every `use_figma`);
2. `figma-use-slides`: the rules specific to Slides;
3. `figma-create-new-file`: before the call to `create_new_file`.

Find them if the exact name is not in the list of skills:

```bash
find ~/.claude/plugins "$HOME/Library/Application Support/Claude" -name SKILL.md -path "*figma-use*" 2>/dev/null
```

They can also come from the Figma MCP server (resource `skill://figma/figma-use/SKILL.md`). In each `use_figma` call, pass `skillNames: "figma-use,figma-use-slides"` (with the `resource:` prefix if they come from an MCP resource).

## 2. Reading the branding

- **Figma link to a Design file** (`figma.com/design/...`): `get_design_context` and `get_variable_defs` for colors, fonts and styles; `get_screenshot` for the look.
- **Link to a Slides file** (`figma.com/slides/...`): `get_metadata` does not work on Slides. Use `use_figma` read-only on that file, plus `get_screenshot`.
- **Published library**: `search_design_system` to find the variables and styles, then import them by key.
- **No link, only HEX values**: create the variables (section 3, step 3).
- Never invent a color or a font the user did not give without telling them.

## 3. The recipe

1. **Plan first** (phase 1 of `figma-use-slides`). For each entry of `deck.json`: archetype, layout described in words, background. Then a shared code preamble: palette `C`, font loading, the `addFrame` / `addText` / `addRect` functions from `references/slide-gotchas.md` (in the `figma-use-slides` skill).
2. **Create the file.** `whoami` for the `planKey` (ask the user if they have several teams), then `create_new_file` with the Slides type. Keep the returned `file_key`. The new file is empty: the first `figma.createSlide()` creates the first row.
3. **Color variables from the theme.** A new Slides file has a light theme by default: don't take it as a model. First read the local collections (`await figma.variables.getLocalVariableCollectionsAsync()`). Overwrite their values with the theme from `deck.json`; otherwise create a “Presentation theme” collection with `fond`, `texte`, `texte-secondaire`, `accent`. Variable value: `{r, g, b, a}` in 0–1 (the HEX divided by 255). Set the `scopes` (FRAME_FILL and SHAPE_FILL for backgrounds, TEXT_FILL for text). Bind each fill with `setBoundVariableForPaint`, which returns a new paint to reassign.
4. **One slide per entry of `deck.json`**, in order, 3 to 5 slides per `use_figma` call. Always `appendChild` before setting `x` / `y`. Load each font before writing (`listAvailableFontsAsync` if the exact style is uncertain; never guess “SemiBold” or “Semi Bold”).
5. **Sections.** Each row of the grid is a section. Name the rows (`SLIDE_ROW.name`) after the blocks of the run of show: opening, each block, recap, close.
6. **Speaker notes.** `slide.speakerNotes = "..."` (markdown text). Put in the full spoken text (`notes` field, each segment preceded by the speaker's name, handovers included), then the builds as a list (`- click: …`, `build` field) and the length (`duree_s`). Accepted formats: lists, bold, italic. No `#` headings, no links, no code: they show as is.
7. **Validate each batch** with the validation script from `slide-gotchas.md` (overlaps, cut-off text, objects outside the frame). Screenshot after the first batch and after the last one only.
8. **Return the IDs** created at each call, and the file link to the user.

## 4. Builds

The API sets neither transitions nor animations (`setSlideTransition` throws “not implemented”). Two options:
- one slide per state (duplicate the slide and add the next element), built by the API;
- then the user links these slides in the interface with the Smart Animate transition, otherwise with a fade. Give them the list of builds: `node "$SKILL/scripts/export_script.js" deck.json --etapes`.

## 5. Limits to point out

- No transitions or animations through the API (see section 4).
- The slide theme is read-only (`slideThemeId`); go through the variables.
- Tables and media (`createTable`, `createGif`) are blocked in Slides by the API: add them in the interface.
- `get_metadata` does not work on a Slides file.
- `figma.createPage()` does not exist in Slides.
- On an existing deck: edit in place, never delete slides to redo them.
- If the session also offers `generate_deck`: don't use it on top. Its templates follow neither the user's branding nor the grammar.

## 6. Backup path with no connector

Build the .pptx with `build_deck.js` (see `powerpoint.md`), then import it into Figma Slides from the interface, if the user's workspace offers PowerPoint import. Same checks as in section 7: fonts, notes, 16:9.

## 7. Checklist before delivering

- [ ] `figma-use` then `figma-use-slides` loaded before the first `use_figma`.
- [ ] One slide per entry of `deck.json`, all 1920 × 1080.
- [ ] Colors bound to the theme variables, not hard-coded.
- [ ] Design system fonts loaded; never an Apple font.
- [ ] No Apple logo or image.
- [ ] Batch validation passed; check screenshots looked at.
- [ ] Notes on each slide: spoken text, clicks, handover, length.
- [ ] Sections named after the run of show.
- [ ] No invented figure, price, date or testimonial; the remaining `[TO PROVIDE]` markers are flagged.
- [ ] A constant tone (in French, tu or vous), as chosen at the start.
- [ ] The limits (animations, tables, media) are told to the user, with the list of builds.
