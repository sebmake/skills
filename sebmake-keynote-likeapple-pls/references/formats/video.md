# Video format (16:9 MP4, or HyperFrames deck)

Always 1920 × 1080. First ask the user what they want:
- **A. An edited video (MP4)**: watched with no presenter, one scene per slide.
- **B. A clickable HyperFrames deck**: presented live in the browser, no MP4.
- **C. A “Motion” Artifact**: only if the session offers it.
- **D. An export from Keynote, PowerPoint or Canva**: no code, with their own voice.

## 1. The voice: say it clearly

The skill writes the script. It produces no voice. Three cases:
- the user records their voice (path D, or an audio file placed in path A);
- a text-to-speech tool is present in the session (for example the one in HyperFrames' `media-use` skill) and the user agrees to use it. Never imitate the voice of a real person;
- otherwise: no voice, the script becomes subtitles.

Subtitle file (.srt) from the `notes` field of `deck.json`: two lines of 42 characters at most per subtitle, timing spread by length over each slide's `duree_s`.

```bash
node "$SKILL/scripts/export_script.js" deck.json --srt sortie.srt
```

Review the line breaks. If the real voice is recorded, re-time on it.

## 2. Path A: edited video with HyperFrames

1. Read the `hyperframes` skill first: it is the required entry point. A linear video made of slides goes to the `general-video` path, not to `slideshow` (which cannot make an MP4).
2. HyperFrames asks its own questions and writes a `BRIEF.md`. Give it what the skill already knows (message, audience, 16:9, length, branding) so the user is not asked again.
3. Update the path, with the user's agreement: `npx hyperframes skills update general-video`.
4. Mapping with `deck.json`:
   - one scene per slide: `data-composition-id` = the slide's `id`, `data-duration` = `duree_s`, `data-width="1920"`, `data-height="1080"`;
   - `data-start` = sum of the lengths of the previous scenes;
   - the builds (`build`) become timed entrances in the scene, at the moment the script (`notes`) says them;
   - colors and fonts come from the `deck.json` theme.
5. If the voice lasts longer than `duree_s`, make the scene longer. Don't speed up the voice.
6. Between scenes: a short fade or a match cut, no hard cut between two sets. No spectacular effect. A21 (name caption) becomes an overlay; A22 to A25 are shots to film, not scenes to invent.
7. Check, then render, after the user approves the preview:

```bash
npx hyperframes check
npx hyperframes render --quality draft                       # tests
npx hyperframes render --quality high --output sortie.mp4    # delivery
```

The MP4 render requires **Node 22 or later** and **FFmpeg** (`node -v`, `ffmpeg -version`). If they are missing, say so. A hosted render exists (`npx hyperframes cloud render`), but it needs an account: the user decides.

## 3. Path B: clickable HyperFrames deck

1. Read `hyperframes`, then `slideshow` and `hyperframes-core`.
2. The `slideshow` skill asks for a yes / no confirmation before writing the deck. Ask the question. Don't skip it.
3. Mapping with `deck.json`:
   - one scene per slide (`data-composition-id`, `data-duration` = `duree_s`);
   - in the `application/hyperframes-slideshow+json` JSON block: `slides[]` with `sceneId`, `notes` = the slide's script (handover and length included), `fragments` = the build times in the scene.
4. Validate: `npx hyperframes lint` (0 errors), then `npx hyperframes check`.
5. Present: `npx hyperframes present <folder>`, then the Present button or the P key. The presenter tab shows the notes, the next slide and the timer. On a video call: share the audience tab (Meet) or its window (Zoom).
6. No MP4 from a deck: `render` keeps only the first slide, without warning. For an MP4, take path A.

## 4. Path C: “Motion” Artifact

Only if the session's Artifact tool lists a “Motion” type (check with the list of types, don't assume it). It makes an animation written in code, which can be scrubbed, commented on and exported as MP4. Give it `deck.json` as the breakdown: one scene per slide, lengths `duree_s`, script as subtitles. For the voice, same rules as in section 1.

## 5. Path D: export without code

From the .pptx (`powerpoint.md`) or the .key (`keynote.md`):
- **PowerPoint**: Slide Show > Record (voice and timing), then File > Export > Create a Video, in 1080p.
- **Keynote**: Play > Record Slideshow (voice), then File > Export To > Movie, in 1080p.
- **Canva**: Present and record, or Share > Download as MP4.

The presenter reads the script from the notes. Builds set by hand are kept in the video.

## 6. Checklist before delivering

- [ ] The path was chosen by the user.
- [ ] Video or deck in 1920 × 1080 (16:9).
- [ ] One scene per slide; each scene lasts at least `duree_s`; total length stated.
- [ ] Voice: recorded by the user, or text-to-speech accepted by them, or subtitles. This is said clearly.
- [ ] Subtitles reviewed: line breaks, spelling, no text over the large titles.
- [ ] No Apple logo, image, font or music; only the user's branding.
- [ ] No invented figure, price, date or testimonial; no `[TO PROVIDE]` in the picture of a delivered MP4.
- [ ] A constant tone (in French, tu or vous), as chosen at the start.
- [ ] Path A: `check` passed, preview approved before the final render. Path B: `lint` at 0 errors.
- [ ] The file or the presentation URL is given to the user.
