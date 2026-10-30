# Running the script: After Effects and EffectCraft

The engine writes one script, `motion.jsx`, in ExtendScript (the JavaScript of After Effects scripts). It uses only the After Effects object API, which EffectCraft also implements. The same file runs in both tools.

```bash
SKILL="<folder of this SKILL.md>"   # often ~/.claude/skills/sebmake-motiondesign-likeapplepls
```

**Requirements.** Node (for `build_motion.mjs`; tested with Node 26), Python 3.9 or later (for `check_motion.py` and `ec.py`, no dependencies), ffmpeg and ffprobe (check frames, checking a render). If one is missing, say so and install nothing without the user's agreement.

---

## 1. The pipeline

```bash
python3 "$SKILL/scripts/check_motion.py" motion.json      # 0 errors before going further
node "$SKILL/scripts/build_motion.mjs" motion.json        # writes motion.jsx next to it, then checks ES3
```

`build_motion.mjs` stops with code 2 if the generated script breaks ES3 (`let`, `const`, `=>`, template literal, `JSON`, an ES5 method…). This should never happen. It is an engine defect: report it, don't work around it.

Useful options:
- `--prefixe TEST-`: same script, composition named `TEST-<name>`. For trials: the real composition is left alone.
- `--relatif`: writes no absolute paths to images. Use it to hand the script to someone else, with its images next to it.
- `--plan`: prints the timing plan (what the checker reads).

---

## 2. In After Effects

After Effects was not used to test the skill (it was not installed). The script uses only the shared API and was run in EffectCraft. Tell the user this at delivery.

**The user runs the script themselves.**

1. Put `motion.jsx` and its images in one folder (the script looks for each image next to itself first, then at its absolute path). For another machine: regenerate with `--relatif`, then copy the whole folder.
2. Open a project (new or existing). The script adds a composition. It saves, opens and closes nothing. It only replaces a composition with the same name, and removes with it the solids that only it used (otherwise each rerun would leave an orphan solid in the project).
3. Menu **File > Scripts > Run Script File…**, then pick `motion.jsx`.
4. The script opens no dialog box: it builds the composition and stops. Its report (layers, keys, placeholders) is shown only in EffectCraft. In After Effects, a placeholder (a missing image replaced by a neutral frame) shows in its layer name, `[PLACEHOLDER] …`. The whole script is one undo step: **Edit > Undo** removes the built composition.
5. Render: **Composition > Add to Render Queue**, or to Adobe Media Encoder. H.264, at the composition frame rate.

**What to know.**
- **Fonts**: PostScript names (`Inter-SemiBold`, not "Inter SemiBold"). After Effects 24 and later takes the first installed font in the theme list. Older versions take the first one in the list, installed or not. Put a font installed on the user's machine first.
- **Motion blur**: the script turns on motion blur for fast layers and for the composition, shutter 120°, phase −60°. The timeline "Motion Blur" switch must stay on for the preview.
- **Gaussian blur**: the engine sets "Blurriness" to 2 × σ, a ratio measured in EffectCraft. In After Effects this mapping is not verified: check it on the image (**convention**).
- **An error**: After Effects shows the line. Ask the user for the message and line number, find the recipe in the script (each block has a comment and a layer marker), fix `motion.json` and regenerate. Don't edit the `.jsx` by hand unless asked: the next build overwrites it.
- **Check frames**: the user renders an MP4 and hands it over. You extract frames with ffmpeg (§ 5).

---

## 3. In EffectCraft

EffectCraft is driven through a local control channel (TCP `127.0.0.1:9877`, one JSON line per request). `scripts/ec.py` is its client.

**Start the app with its channel**, if it isn't running that way:

```bash
open -a EffectCraft --args --control 9877
python3 "$SKILL/scripts/ec.py" activer        # bring to front: the app only handles requests when it is in front
```

`activer` is the only allowed use of osascript (`tell application "EffectCraft" to activate`). Don't automate anything else in the interface.

**Run, look, render.**

```bash
python3 "$SKILL/scripts/ec.py" script motion.jsx                                  # builds the composition
python3 "$SKILL/scripts/ec.py" frames "<comp name>" controle/ --pas 0.5 --max 640   # one frame every 0.5 s
python3 "$SKILL/scripts/ec.py" frame "<comp name>" 4.3 image.png 1920       # one specific frame
python3 "$SKILL/scripts/ec.py" render "<comp name>" rendus/motion.mp4      # H.264 render, waits for the end
python3 "$SKILL/scripts/ec.py" capture capture.png "<comp name>"           # the app window, to show the mechanics
python3 "$SKILL/scripts/sonde_ec.py" "<comp name>" --carte carte.md        # the layer map and the markers
```

- The composition name is `comp.nom` from `motion.json` (prefixed if `--prefixe`).
- `render` removes the rendered item from the queue (unless `--garder 1`) and waits up to 1,800 s.
- Each request has a timeout (`--delai`, 180 s by default): a stuck app does not block the terminal.
- Exit codes: 0 success; 1 app error; 2 timeout; 3 no app listening; 4 refused.

**The user's project.** `ec.py` refuses commands that save, open, replace or close the project (`file.save`, `file.open`, `app.quit`…), unless `--autoriser` is given. Use it only if the user asks. For a trial, prefix the composition (`--prefixe TEST-`). Saving the project is the user's job.

---

## 4. Known traps and fixes

| symptom | cause | fix |
|---|---|---|
| "timeout", no answer | the EffectCraft window is not in front | `ec.py activer`, or `--relance` (brings it to front and resends the request once) |
| "no app listening" | the app runs without a control channel, or not at all | ask the user to restart it with `--args --control 9877` (don't quit it yourself: their project is open) |
| the app at 100% CPU after a request | a request on an animated mask froze the app | the engine uses no masks; don't add one by hand. If the app is frozen, tell the user, who decides whether to restart it |
| all moves are linear | EffectCraft ignores interpolation and eases if the composition is not active | the script calls `comp.openInViewer()` before any key; keep this in any hand-written script |
| a curve has no effect | a `KeyframeEase` set on a linear key changes nothing | set `KeyframeInterpolationType.BEZIER` before the ease (the engine does this) |
| two keys become one | keys snap to frames; two keys less than one frame apart merge | times snapped to frames, at least one frame apart (the engine does this) |
| an expanded mask changes nothing in the render | mask expansion (`ADBE Mask Offset`) is not rendered | offset groups or track mattes; the engine uses no masks |
| a shape is offset | a shape layer counts its vertices from its anchor point | draw around the anchor (0, 0) and place with position; or anchor = position = composition center |
| a layer disappears | a layer that is too wide (about 27,000 px) is no longer drawn | no layer wider than the frame or than the element diagonal × 1.2 |
| an existing image becomes a placeholder | `File.exists` returns false in EffectCraft | the import is tried anyway; if it really fails, check the absolute path (regenerate without `--relatif`) |
| an image next to the script is not found in EffectCraft | `$.fileName` is the name passed at run time, not the file path | the script also keeps the absolute paths from generation: regenerate on the machine that runs it |
| `editor.state` refused as a method | it is a command | `ec.py cmd editor.state` |
| the blur looks twice too strong or too weak | the Gaussian blur "Blurriness" setting equals 2 σ in EffectCraft | the engine converts it (`md_sigma`); check by eye in After Effects |
| the font is wrong | a missing font raises no warning | a font list with fallbacks in the theme; EffectCraft ships Inter (Regular, Medium, SemiBold, Bold) |
| the render is removed from, or stays in, the queue | the render queue keeps rendered items | `ec.py render` removes them, unless `--garder 1` |
| an image parented to a null ignores its zoom | EffectCraft does not apply a null's scale to a child image (it does apply position) | put the scale on the image itself; its shape children follow correctly (`scene-demontee.md` § 1) |
| an image's children are twice too big and offset | the parent image is larger than the composition | image ≤ composition; 4K format for a ×2 screenshot |
| `ui.screenshot`: "no frame was presented" | app window hidden or screen asleep | `ec.py capture` brings the app to front; the screen must be on |
| the move goes the wrong way | the ease speed does not have the sign of the change | see `courbes.md` § 8 |

---

## 5. Check frames and checking a render

**A contact sheet from the check frames** (EffectCraft, `ec.py frames`):

```bash
ffmpeg -v error -y -pattern_type glob -i 'controle/t*.png' -vf "scale=480:-1,tile=6x7:padding=4" -frames:v 1 planche.jpg
```

With a 0.5 s step, 6 × 7 frames cover 21 s. Adjust the grid to the duration.

**A rendered MP4** (After Effects or EffectCraft):

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of csv=p=0 rendu.mp4
ffmpeg -v error -y -i rendu.mp4 -vf "fps=2,scale=480:-1,tile=6x7:padding=4" -frames:v 1 planche.jpg
ffmpeg -v error -y -ss 4.3 -i rendu.mp4 -frames:v 1 image-4s3.png
```

To judge a curve, extract the frames of one move at full frame rate (`-ss <start> -t <duration> -vf fps=30`) and look at them in sequence: the start, the braking, no overshoot.

**What to look for** (read the frames with the image-reading tool):
- every text whole, readable, with no box behind it;
- the empty background for a moment after each cut, then the element;
- one major move at a time; the label after its number;
- no overshoot, no bounce, nothing floating in a loop;
- gray placeholders (missing images) and `[TO PROVIDE]` on screen;
- nothing that recalls a brand: no device, font, logo or signature.
