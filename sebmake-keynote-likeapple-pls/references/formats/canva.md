# Canva format (16:9 presentation)

Two paths: a Canva connector attached to the session, or a manual import of the .pptx. The .pptx is built with `build_deck.js` (see `powerpoint.md`, section 1).

## 1. First: is a Canva connector attached?

Never assume it exists. Check your own list of tools:

- look for a tool whose name contains `canva` (case ignored);
- if some tools are deferred, run a tool search with the word `canva`;
- read the description of each tool found before calling it. Names change from one connector to another.

**If there is one, use it rather than the manual import.**
- Prefer a tool that imports a file or a file URL: give it the .pptx built by `build_deck.js`. The grammar and the script stay those of the skill.
- Avoid a tool that “generates” a design from a prompt: it imposes its own layouts, which don't follow the grammar.
- If the tool asks for a public URL of the .pptx, ask the user where to host the file. Put nothing online without their agreement.
- If the connector lists brand kits (Brand Kit), ask the user which one to use. It is their design system.
- After the import, review the design with the connector's reading tools if there are any (pages, texts): number of pages, notes, `[TO PROVIDE]` markers.
- Give the user the link to the design created.

**If there is none, go to section 2.** Say so in one sentence, without offering to install anything.

## 2. Manual import of the .pptx

1. Build `sortie.pptx` with `build_deck.js`.
2. In Canva, on the home page: Upload button, or drag the file onto the page. Depending on the version, the entry can also be Create a design > Import file.
3. Canva converts the file into an editable presentation.
4. Check the size: the ratio must be 16:9 (1920 × 1080 px for a standard Canva presentation; an import can keep another size with the same ratio). Use the Resize menu to see it.

## 3. Known limits of the import

**Fonts.** Canva uses only its library and the fonts uploaded to the brand kit (paid plans).
- A missing font is replaced by a Canva font.
- To keep yours: upload it to the brand kit (if the license allows it), then import the .pptx again.
- Otherwise: choose with the user the font closest to their design system. Never an Apple font or an imitation.
- After a replacement, review the titles: line breaks change.

**Speaker notes.** Canva has notes per page (Notes button under the page).
- The import usually keeps them, but not always. Check page by page.
- If they are missing: paste them back from the script delivered by the skill.

**Animations and builds.** The .pptx contains fades and on-click builds, but Canva does not always keep them on import: it mostly animates the arrival of a page or an element, with little on-click control.
- For a build (a list line by line, figure then label, name then price): one page per state (duplicate the page, add the next element), linked by the Match & Move transition, otherwise by a fade.
- Canva animations: keep the plainest one (fade). No spectacular effect.

**`[TO PROVIDE]` markers.** The import loses the 40 % opacity that fades the labels: “date” or “gain” would show as real content. With `meta.format` set to `canva`, the engine therefore keeps the brackets on screen (`[date]`, `[gain]`). After the import, check that no label lost its brackets.

**Other points.**
- No slide master: each page is independent.
- Native charts can arrive frozen or distorted. Redo them with Canva's chart tool, without axis ticks if the grammar doesn't want them.
- Heavy file: compress the images before the import.

## 4. Branding

- Colors: add the theme HEX values to the brand kit, or type them in the color picker.
- Don't let Canva propose a “matching” palette instead of the user's.

## 5. Presenting from Canva

- Present button > Presenter view: notes, next page, timer.
- On a video call: share the audience window, not the whole screen.
- Present and record: useful for a video version (see `video.md`).
- Exports: Share > Download, as PPTX, PDF or MP4.

## 6. Checklist before delivering

- [ ] The list of tools was checked; connector used if it exists, manual import otherwise.
- [ ] No file put online without the user's agreement.
- [ ] Presentation in 16:9.
- [ ] Fonts: those of the design system, or a replacement approved by the user.
- [ ] Colors: the theme HEX values, not a palette proposed by Canva.
- [ ] No Apple logo, image or font.
- [ ] Notes on every page that has a script, with handover and length.
- [ ] Builds reproduced (duplicated pages), or listed for the user.
- [ ] No invented figure, price, date or testimonial; the remaining `[TO PROVIDE]` markers are flagged and show in brackets.
- [ ] A constant tone (in French, tu or vous), as chosen at the start.
- [ ] The Canva link, or the import steps, are given to the user.
