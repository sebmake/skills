# The scene breakdown: a UI one-take you can read layer by layer

A scene breakdown shows an interface in motion (a window, a camera that moves from one element to the next, halos, a cursor, a voice and subtitles). It is built so that **each mechanism has its own layer, named after its role**. You open it in EffectCraft or After Effects and you see how it works. You can touch it up by hand. You can read it back in numbers.

It serves three purposes:

- a **demo film** of a piece of software, narrated, from 20 s to a few minutes, chapter by chapter;
- a **UI shot** inside a feature film (`film-fonctionnalites.md`), when the component must stay in its window;
- **taking apart** an animation made elsewhere (an animated HTML page, a render from another tool) to understand it and rebuild it in the tool: you render the window alone, without a camera, and rebuild the camera, the halos and the rest as layers.

Nothing here is measured in the keynote corpus. Everything is a **convention**, tuned on two films made with this method (a 30 s launch film and a 7 min 39 demo in ten chapters). The measured values of the recipes (`elements.md`) remain the reference for what they cover.

## French identifiers used in this file

The JSON keys and values stay in French because the scripts read them. What they mean:

| Identifier | Meaning |
|---|---|
| `comp`, `nom`, `duree` | composition, its name, its duration (s) |
| `theme`, `fond`, `texte`, `secondaire`, `voile`, `police`, `police_titre` | theme: background, text, secondary color, scrim, font, title font |
| `fenetre`, `fichier`, `largeur`, `hauteur`, `apparition` | window: file, width, height, fade-in `[t0, t1]` |
| `camera`, `cles`, `arrivee`, `note`, `flou_de_bouge` | camera, keys, how the camera arrives on a key, what we look at, motion blur |
| `enfants`, `halos`, `curseur` | children of the window: halos, cursor |
| `rect`, `marge`, `epaisseur`, `arrondi`, `couleur` | halo rectangle, margin, stroke width, corner radius, color |
| `points`, `clics` | cursor positions, click times |
| `ecran`, `sous_titres`, `intertitre`, `titre`, `sous_titre`, `etiquette`, `textes`, `corps` | screen layer: subtitles, title card, its title, subtitle, label; fixed texts, font size |
| `caracteres_par_ligne` | characters per subtitle line |
| `son`, `voix`, `sons`, `musique`, `decalage` | sound: voices, one-shot sounds, music, music offset |
| `pose`, `suit`, `fouette`, `lineaire`, `coupe` | arrival values: settles, follows, whip, linear, cut (§ 3) |

---

## 1. The mechanism

```
 Background (solid)
 Window ──────────────── the camera lives here: ANCHOR = the point of the window we look at
   │                                            SCALE = zoom × 100
   │                                            POSITION = always the center of the frame
   ├─ Halo 1, Halo 2 …    children: placed in window px, they follow the camera with no math
   └─ Cursor              child: its positions are those of the clicked elements
 Subtitle N, Text N       fixed on screen, above everything
 Title card · …           on top of everything; the window appears as it fades out
 Voice 1…n, Sound, Music  each at its moment; the music offset to land in the right place
```

- **There is no camera layer.** Moving the anchor slides the image. Raising the scale dives into it. A marker on the window, at each key, gives the arrival, the zoom and what we look at.
- **Children work in window px.** A halo around a button is described by the button's rectangle in the screenshot, not by its place on screen, which changes all the time.
- **Whatever must not move with the camera has no parent**: subtitles, title card, screen texts.
- Why not a "camera" null layer: EffectCraft does not apply a null's scale to a child image (the image stays at 100 %, seen in testing). It also misplaces the children of an image larger than the composition. So the window carries the camera, and it is never larger than the composition.

## 2. `scene.json`

Paths are relative to the file's folder. Times are in seconds. Window coordinates are in px **of the window file**.

```json
{
  "comp":    { "nom": "Demo · chapter 1", "format": "16:9", "fps": 30, "duree": 19.5 },
  "theme":   { "fond": "#1B2420", "texte": "#F4F3EE", "secondaire": "#C9CFC9", "accent": "#E8B44C",
               "voile": "#0E1311", "police": "Inter-Medium", "police_titre": "Inter-Bold" },
  "fenetre": { "fichier": "fenetre.png", "largeur": 1440, "hauteur": 960, "apparition": [2.2, 2.8] },
  "camera":  { "flou_de_bouge": true, "cles": [
      { "t": 0,   "x": 720, "y": 480, "zoom": 1.05 },
      { "t": 3.6, "x": 720, "y": 480, "zoom": 1.05, "arrivee": "coupe", "note": "rest" },
      { "t": 5.0, "x": 160, "y": 60,  "zoom": 2.2,  "arrivee": "fouette", "note": "the New button" } ] },
  "enfants": {
    "halos":   [ { "nom": "New", "rect": [24, 28, 232, 44], "t0": 5.2, "t1": 7.8 } ],
    "curseur": { "points": [ { "t": 3.6, "x": 900, "y": 600 }, { "t": 4.9, "x": 150, "y": 52 } ], "clics": [7.0] } },
  "ecran": {
    "sous_titres": "voix.srt",
    "intertitre": { "t1": 2.6, "titre": "The product", "sous_titre": "A one-line promise", "etiquette": "Demo" },
    "textes": [ { "texte": "…", "x": 960, "y": 120, "corps": 48, "t0": 3, "t1": 6 } ] },
  "son": {
    "voix":    [ { "t": 3.0, "fichier": "voix/v1.mp3", "texte": "start of the sentence" } ],
    "sons":    [ { "t": 7.0, "fichier": "clic.wav", "nom": "click" } ],
    "musique": { "fichier": "musique.wav", "decalage": 0 } }
}
```

| Field | Meaning |
|---|---|
| `comp.format` | `16:9`, `16:9-4k` (3,840 × 2,160: to zoom sharply on a ×2 window), `9:16`, `1:1` |
| `fenetre.fichier` | an image or a video of the interface **alone**, with no camera and no set. Never larger than the composition (the script refuses) |
| `fenetre.apparition` | `[t0, t1]`: fade-in of the window (for example as the title card fades out) |
| `camera.cles[].arrivee` | how the camera **arrives** on this key (§ 3); the first key has none |
| `camera.cles[].note` | what we look at: written in the key's marker, read in the tool and by the probe |
| `camera.flou_de_bouge` | motion blur for the composition, the window and its children (EffectCraft renders it) |
| `enfants.halos[]` | `rect` [x, y, width, height] of the element, `t0` (the outline draws in 0.45 s), `t1` (it fades in 0.3 s); `marge` 8, `epaisseur` 3, `arrondi` 12, `couleur` (the accent) |
| `enfants.curseur` | `points` [{t, x, y}] (the cursor glides from point to point), `clics` [t] (it shrinks to 84 % for 0.14 s) |
| `ecran.sous_titres` | an `.srt` file or a list `[start, end, text]`; split into two lines beyond 64 characters (`caracteres_par_ligne`) |
| `son.musique.decalage` | where the music starts within the whole film: a scene that is chapter 3 of a film picks up the music at its moment |

## 3. The camera: settle, follow, whip, cut

| `arrivee` | Interpolation | When |
|---|---|---|
| `pose` (default) | Bézier, 66 % influence on both sides | a camera move that starts gently and settles |
| `suit` | Bézier, 33 % influence | follow a moving subject, with no jolt |
| `fouette` | Bézier, 88 % influence | go fast from one point to another: almost all the travel in the middle |
| `lineaire` | linear | a dolly at constant speed |
| `coupe` | hold | the image does not move until this key (a rest), or jumps to it |

How to set the keys:

- **A rest is two identical keys**, the second one in `coupe`. A key without `x`, `y` or `zoom` keeps those of the previous key, so a rest is written `{"t": 6.4, "arrivee": "coupe"}`. During a rest, nothing moves: that is what gives gestures their weight. A slow push while the voice speaks is not a rest.
- **Follow**: set the key where the subject will be a tenth of a second later. The camera seems to hold it.
- **Whip**: set the arrival key before the subject gets there. The camera seems to wait for it. A whip is fast (300 px per frame and more): turn on `flou_de_bouge`, or it doubles up.
- **One action, one framing.** Each gesture shown (open, choose, send) gets its tight framing. The wide shot is for setting the scene and for ending.
- **The cursor arrives before the camera, or with it**, never after. Otherwise it leaves the frame during the move (the probe sees it).
- **The halo fades out before the camera leaves**, or it leaves the frame while fading (seen in the 7 min 39 demo; the probe caught it).

## 4. Readability

- The on-screen size of a UI text = its size in the screenshot × the zoom. Everything the voice names must be **at least 26 px on screen** in 1080p: a 13 px label needs a zoom of 2.
- A window meant to be read fills 70 to 80 % of the frame width. The wide shot is not for reading.
- **Sharpness**: the window is an image. Zooming ×2 on a 1:1 screenshot makes it soft. For strong zooms, take the screenshot at ×2 and use the `16:9-4k` format.
- **The window comes from an animated web page?** Render it as an image (a video of the window alone, without a camera), not as HTML filmed up close: the browser snaps text to the pixel grid and it jitters during zooms.

## 5. Three concepts, and what crosses each boundary

Before the plan, for a film (not for a single element), propose **three central ideas** that differ in the picture, not in the order of screens: a single shot that wanders through the window; a component that leaves the window and becomes the next one; a side-by-side before/after; a dive from a full screen down to a button… For each one: the hook image, what carries from one beat to the next, what it forbids itself. The user chooses.

Then, in the plan, add a **"what crosses"** column: at each change of beat, what survives and moves to carry into the next. In a scene breakdown, it can be:

- the **camera** itself (the window stays, the framing changes): the boundary is carried;
- the **cursor**, which goes from one element to the next;
- a **halo** that slides from one element to the next instead of disappearing;
- a **component** that grows until it becomes the next screen (two layers, the second a child of the first during the pass).

A change where nothing survives is a slide. That is right in the keynote style, which cuts first (P1). It is not right in a one-take. Choose one or the other and say so in the plan.

## 6. Reading back in numbers: the probe and the measure

**`sonde_ec.py`** reads the open composition (the layers themselves, not the pixels):

- the **map**: each layer, its kind, its parent, its presence, what is animated and how many keys, its markers. This is the page to show when explaining the scene;
- the **boundaries**: moments where most of what we see changes identity within 0.4 s; each one carried, anchored or bare, plus a carry-over score;
- the **speed**: the largest travel of each layer, in px per frame;
- the **frame**: the watched layers (`--cadre "Cursor,Halo"`) that leave the image, and when.

**`mesure_rendu.py`** reads the MP4: energy map (one character per 1/12 s), share of still frames, longest calm, cuts, bursts, shot durations and their variation, sound (peak, clipping, silence, loudness). `--ref` reads a reference alongside.

Benchmarks (conventions: working thresholds from launch motion design, not measured on the corpus):

| Benchmark | Value | What it says |
|---|---|---|
| carry-over score | < 0.5: a series of slides; ≥ 0.7: a shot that holds together | only meaningful for a one-take |
| speed | > 80 px per frame without motion blur | the move doubles into sharp copies |
| frame | a watched layer outside the image | the subject is lost during a move |
| pace | shot variation (standard deviation / mean) ≥ 0.25 | otherwise the film cuts to a metronome |
| rest | ≥ 25 % still frames and a calm of at least 1 s | otherwise everything moves and nothing has weight |
| sound | peak ≤ −3 dBFS, no clipped sample | a continuous voice leaves little silence: that is normal |

No benchmark blocks. Each one is fixed, or kept and stated.

## 7. The continuous work loop

1. **Write** `scene.json` (one scene per chapter for a long film), then `scene_ec.py scene.json --prefixe TEST-`.
2. **Look**: contact sheet (`ec.py frames`), then `sonde_ec.py` (map, boundaries, speed, frame).
3. **Show the mechanism**: the tool screenshot (`ec.py capture`), the map, and a frame of the render next to a reference frame at the same moment. Explain layer by layer: what the anchor does, what the scale does, why the halos follow on their own.
4. **Render** (`ec.py render`), then `mesure_rendu.py`.
5. **Touch up**, in two ways:
   - in `scene.json`, then regenerate (the safe way: nothing is lost);
   - **by hand in the tool** (a moved key, a wider halo): rerun `sonde_ec.py`, whose map shows what changed (keys, presences, markers), and copy the change back into `scene.json` so it survives the next generation. Tell the user each time.
6. **Keep**: only when asked, `ec.py --autoriser garder <new file>.ecproj` saves the project to a new file, never over another one. The project then becomes a working object you reopen, read and evolve.
7. **Edit**: the rendered scenes become the chapters of an edit (skill `sebmake-videoedit-like-applepls`, composed edit: picture, voice, music ducked under the voice, subtitles, sounds).

## 8. Lessons paid for

| Symptom | Cause | Fix |
|---|---|---|
| halos and cursor twice too large, offset | window larger than the composition | window ≤ composition (the script refuses); `16:9-4k` format for a ×2 screenshot |
| the window ignores the zoom | it was the child of a null layer: EffectCraft does not apply the null's scale to an image | the window carries the camera itself |
| all moves linear | the composition was not open in the viewer | the script opens it before any key |
| a halo leaves the frame while fading | the camera leaves before the halo ends | halo `t1` before the departure key |
| the cursor leaves the frame during a whip | it arrives after the camera | cursor point on the element before the arrival key |
| `ec.py capture`: "no frame was presented" | app window hidden or screen asleep | the command brings the app to the front; keep the screen on |
| image softer than the original | the window is an image enlarged by the zoom | ×2 screenshot and `16:9-4k` format |
