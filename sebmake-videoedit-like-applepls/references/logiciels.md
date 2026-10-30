# The software: FilmCraft driven, Premiere Pro and DaVinci Resolve by file

This file says how `montage.json` becomes a timeline in the user's software, and how a timeline comes back to the review. The `montage.json` format and the full FilmCraft command table are in `montage-spec.md`.

## Contents

1. Who gets what
2. FilmCraft, driven through its control channel
3. Premiere Pro, by XML
4. DaVinci Resolve, by XML
5. EDL, as a fallback
6. Bringing a timeline back to the review
7. Known limits

**What was tried, and what was not.** FilmCraft was installed on the machine where the skill was written: building, checking and import were done there. Premiere Pro and DaVinci Resolve were not: their files were checked by reading them back, by an independent reader (`lire_timeline.py`) and by the FilmCraft importer, which reads the same formats. The steps in § 3 and 4 follow what these programs document; they were not replayed here. Tell the user.

---

## 1. Who gets what

| Software | What the skill provides | Command |
|---|---|---|
| FilmCraft | the sequence built in the app, checked, with native editable titles | `python3 filmcraft_build.py montage.json` |
| Premiere Pro | an FCP7 XML ("xmeml") | `python3 export_xml.py montage.json --verifier` |
| DaVinci Resolve | the same FCP7 XML | `python3 export_xml.py montage.json --verifier` |
| Any other editing software | a CMX3600 EDL | `python3 export_edl.py montage.json --verifier` |

These four scripts use only the Python 3.9 standard library (except `--cartons png`, which needs Pillow). `--verifier` reads the written file back and compares it to the edit, frame by frame: code 0 if everything matches, 3 otherwise, 1 if `montage.json` is inconsistent, if a shot runs past its clip, or if a cross dissolve has no frames on both sides of the cut (file length read by ffprobe; a missing file is only a warning). `filmcraft_build.py` refuses the same things, simulation included.

The tracks are always the same: **V1** the shots, **V2** the title cards; **A1** the speech, **A2** the music, **A3** the picture sound. Each title card and each structure beat carries a sequence marker.

Footage paths are written as absolute paths in the XML and the EDL. Don't move the footage between export and import; otherwise the media will need relinking.

---

## 2. FilmCraft, driven through its control channel

FilmCraft is an editing app in the style of Premiere Pro. It is driven through a local channel: TCP `127.0.0.1:9876`, one JSON line per request `{"id", "method", "params"}`, one JSON line in reply. Three methods: `engine.commands` (the command list, 701 in version 0.12.0), `engine.execute` (one command and its parameters), `ui.screenshot`. Inspections (`sequence.inspect`, `project.inspect`, `state.inspect`) are **commands**: they go through `engine.execute`. Times are in "ticks", 254,016,000,000 per second, as in Premiere Pro. `scripts/fc.py` is the client.

### 2.1 Start and check the channel

```bash
python3 "$SKILL/scripts/fc.py" etat          # project, active sequence, selection
```

- Normal reply: the app is listening. Move on.
- "no app listening" (code 3): FilmCraft is not running, or is running without its channel. `filmcraft_build.py` starts it if it is closed (`open -a FilmCraft --args --control 9876`). If it is **already open without the channel**, ask the user to quit it and relaunch it with that command: never quit it yourself, their project may be open.

### 2.2 Build the sequence

First as a dry run, then for real:

```bash
python3 "$SKILL/scripts/filmcraft_build.py" montage.json --simulation          # sends nothing, lists the commands
python3 "$SKILL/scripts/filmcraft_build.py" montage.json --images controle/ --rendre film.mp4 --rapport filmcraft-rapport.json
```

What the script does, one FilmCraft command per step:

1. a **new project** named after the edit (default); or the project already open with `--projet ouvert`;
2. a bin "<name> footage", import of the footage, the music and the logo;
3. a sequence in the edit's format (3 video tracks, 3 audio tracks);
4. V1: each shot in place, in point and length to the frame; the color backgrounds of the title cards;
5. V2: the title cards as **native titles**, editable, at the size and position of the edit;
6. A1 speech, A2 music (level, fade-out), A3 picture sound;
7. the transitions: centered cross dissolves, fades up from black, fades to black, dip to white, push (FilmCraft aligns them itself);
8. the sequence markers;
9. the check through `sequence.inspect`: each shot, each speech clip, the music, each transition;
10. with `--images`: one program frame in the middle of each shot (`file.exportFrame`, title cards included) and a contact sheet.

Options: `--nom NAME` (name of the project and sequence; `TEST-` prefix for a test), `--rendre FILE.mp4` (the H.264 video, to a file that does not exist yet), `--port`, `--rapport`. Exit codes: 0 sequence built and on spec; 1 error; 2 FilmCraft unreachable; 3 deviations in the check.

In the tests run while writing the skill, three sequences (25 and 23.976 frames per second, with music, speech, lower thirds, ten title cards) were built and read back through `sequence.inspect` with no deviation, and each interview shot landed on its speech to the frame.

### 2.2b The composed edit, and the map

`compose_montage.py plan.json` then `filmcraft_build.py montage.json` lay the chapters on V1, one voice line per sentence on A1, the music on A2 (ducked under the voice if `attenuation_db` is set: FilmCraft Essential Sound), the sound effects on A3 and the subtitles on C1; the tracks carry the name of their role. `--carte carte-montage.md` describes each track and what it carries; `--capture capture.png` captures the FilmCraft window (the app comes to the front; the screen must be on, otherwise "no frame was presented"). These are the two things to show to explain the edit before it is changed by hand.

### 2.3 Look at the result

The check compares numbers. Look at the images too: open the contact sheet in the `--images` folder, and check that each title card is readable, that nothing black hides a picture, and that the reveal and the ending land where the plan says.

```bash
python3 "$SKILL/scripts/fc.py" inspecter                           # readable summary of the active sequence
python3 "$SKILL/scripts/fc.py" image 24.5 verif-24s.png            # one program frame at 24.5 s
python3 "$SKILL/scripts/fc.py" capture fenetre.png                 # the app window
```

### 2.4 The user's project

- **Nothing is saved**, except with `--enregistrer PATH.fcproj`, to a file **that does not exist yet**. Never over an existing file. Saving stays the user's call.
- `fc.py` refuses commands that open, save, close, delete or quit (`file.save`, `file.open`, `file.closeProject`, `app.quit`…), unless `--autoriser` is given. Use it only if the user asks.
- `--projet ouvert` adds a bin and a sequence to the user's project, without saving. Prefer the new project (default), unless the user asks otherwise.
- Never quit the app. Touch no sequence that is not yours.

### 2.5 Change by hand, then review again

The user edits by hand in FilmCraft: the titles are native, the shots are real shots. To measure the changed edit, export the active sequence as FCP7 XML, then run the review on it (§ 6):

```bash
python3 "$SKILL/scripts/fc.py" cmd sequence.open '{"item": "<sequence id>"}'
python3 "$SKILL/scripts/fc.py" cmd file.exportFcp7Xml '{"path": "/absolute/path/retouche.xml"}'
```

The sequence id is shown by `fc.py etat` or `fc.py inspecter`. In one test, a FilmCraft title came out of this export as a picture shot named after its text: the review reads it as a picture. Annotate it in `textes` (see `critique.md` § 5).

**The video.** `--rendre film.mp4` goes through `file.exportMedia` (H.264), from 0 to the length of the edit (`range: "custom"`). Tried during the read-back: 45 s rendered as 1,125 frames, final black included, in about ten seconds. Without these bounds, exporting the whole sequence stops at the last item: the final black, which is a gap on V1, disappears (44.04 s instead of 45.00 s in the same test). This is the most complete input for the review: motion, color and sound are measured. A render without music carries a silent audio track: the review reads it as no sound.

### 2.6 When it does not respond

| What you see | Why | What to do |
|---|---|---|
| "no app listening" (code 3) | FilmCraft closed, or open without `--control 9876` | § 2.1 |
| "timeout" (code 2) | the app is busy (import, render) or waiting in the background | `fc.py activer` (brings the app to the front), then rerun; or `--relance` |
| "unknown method" | an inspection called as a method | `fc.py cmd sequence.inspect` |
| "refused" (code 4) | protected command | only if the user asks: `--autoriser` |
| deviations in the check (code 3 from `filmcraft_build.py`) | a shot, a speech clip or a transition is not where the edit says | read the report (`--rapport`), compare with `montage.json`, rebuild in a new project |
| an unknown command | the app version has changed | `fc.py commandes <filter>` gives the list and the parameters |

---

## 3. Premiere Pro, by XML

Not tested in Premiere Pro (see the note at the top).

**Before import.**

```bash
python3 "$SKILL/scripts/export_xml.py" montage.json -o montage.xml --verifier
python3 "$SKILL/scripts/export_xml.py" montage.json -o montage-png.xml --cartons png --verifier   # title cards as images
```

Choose the title card mode:

| `--cartons` | What the software gets | When |
|---|---|---|
| `texte` (default) | a "Text" generator for a title card on black; text placed over a picture or a color is only a **marker**, to be placed by hand | the user wants editable titles and will place the lower thirds themselves |
| `png` | one PNG image per title card (text and background already drawn), on V2; needs Pillow and the user's font file (`police.fichier`). The export prints the font used; without a file, it warns and falls back to Inter, DejaVu Sans or Arial | the user wants to see all the text right after import |
| `generateurs` | the "Text" generator everywhere | at your own risk: an importer that does not read this generator puts black video in its place and hides the picture underneath (seen in FilmCraft) |

**Step by step** (Premiere Pro menus):

1. **File > Import…**, choose `montage.xml`. Premiere creates a bin named after the file, with the sequence and the media.
2. Open the sequence. Check its frame rate and size in **Sequence > Sequence Settings**: they are those of `montage.json` (`format`).
3. Offline media (red): right-click them, **Link Media…**, and point to the footage folder.
4. Check the tracks (V1, V2, A1 to A3) and the transitions. The cross dissolve is a Cross Dissolve. The dip to white and the push are written as "Dip to White" and "Push": check that they came through, otherwise place them by hand at the marker.
5. Title cards in `texte` mode: open the **Markers** panel; each marker carries the text and its position. Place the title with the Type tool, in the user's font, small and centered (see `grammaire-montage.md` G6).
6. Listen to the music: the level and the documentary's breathing spaces are set by ear (no volume curve is written).
7. What the XML does not carry: the black-and-white grade, the widescreen format (bars), reframing to 9:16 or 1:1 (each shot on its subject, without bars: the shots come in at their own size), the credits of a trailer for a work. These are done in Premiere.

---

## 4. DaVinci Resolve, by XML

Not tested in DaVinci Resolve (see the note at the top).

**Before export.** Resolve starts its timelines at `01:00:00:00` by habit. To match that, build the edit with `assemble.py … --tc-debut 01:00:00:00`, then export as for Premiere. The `--cartons png` mode is the safest: how Resolve converts the "Text" generator has not been checked.

**Step by step** (Resolve menus):

1. In a new project, first set the timeline frame rate to that of `montage.json`: **File > Project Settings > Master Settings**. Resolve often locks this frame rate as soon as media is imported.
2. **File > Import > Timeline…**, choose `montage.xml`. In the next window, leave checked the option that automatically imports the source clips into the Media Pool.
3. Offline media: select them in the Media Pool, right-click, **Relink Selected Clips**, and point to the footage folder.
4. Open the timeline in the Edit page. Check tracks, transitions and markers, as in § 3 (steps 4 to 6).
5. Black-and-white grade, widescreen format, reframing to 9:16 or 1:1 (each shot on its subject, without bars), music level: in Resolve.

---

## 5. EDL, as a fallback

The CMX3600 EDL is the oldest and most widely read format. Use it when the XML does not get through.

```bash
python3 "$SKILL/scripts/export_edl.py" montage.json -o montage.edl --verifier
```

- What it carries: a single video track, the blacks (reel `BL`), the dissolves (`D` and their length in frames), the dip to white (`D` and a comment), the speech (`A`), the music (`A2`), the picture sound (`A3`).
- What it does not carry: the title cards (comment lines), the push (a cut and a comment), the music level, the markers (comment lines).
- Each event names its clip (reel = clip id, 8 characters at most) and its file (`* FROM CLIP NAME`, `* SOURCE FILE`). The software finds the clips by that name: import the footage first (in Resolve, into the Media Pool), then the EDL.
- NTSC frame rates (23.976 and 29.97): non-drop-frame timecode, counted at 24 or 30 frames.
- FilmCraft reads the EDL at 24 frames per second, with no setting: for FilmCraft, prefer `filmcraft_build.py` or the XML.
- Footage at a frame rate other than the timeline's (`journal` says "mixed frame rates"): their source in points are written as timecode at the timeline's frame rate. Software that conforms the EDL by the clip's timecode may read them differently (not tried, for lack of Premiere Pro and Resolve): prefer the XML, or check those shots on import.

---

## 6. Bringing a timeline back to the review

The review reads a rendered video, an FCP7 XML or an EDL (`critique.md` § 2).

| Software | Export | Watch out |
|---|---|---|
| Premiere Pro | **File > Export > Final Cut Pro XML…** | not FCPXML: the review does not read it |
| DaVinci Resolve | **File > Export > Timeline…**, format "FCP 7 XML" | same |
| FilmCraft | `fc.py cmd file.exportFcp7Xml '{"path": "…"}'` on the active sequence (§ 2.5) | titles may come out as picture shots: annotate them |
| All three | a rendered video (H.264 is enough) | the video gives motion, color and sound; text placed over a picture is not seen there |

With an XML, add `--mesurer-medias` if the footage is on the machine: otherwise motion and color are not measured. With an EDL, give `--fps`; its in points are in source timecode, and the review subtracts the timecode stamped in each file (10:00:00:00 on many cameras) before measuring. For speech, ask for the subtitles (`.srt` or `.vtt`) the software can export, or write them from `montage.json` (`critique.md` § 3).

---

## 7. Known limits

| Limit | Where | What to do |
|---|---|---|
| Premiere Pro and DaVinci Resolve not installed when the skill was written | XML, EDL | the files are checked by reading back, by `lire_timeline.py` and by import into FilmCraft (each shot, each source in point and each speech clip found to the frame); check on import at the user's end |
| The FCP7 "Text" generator is not read everywhere | XML | default: generator on black only; `--cartons png` to see everything |
| Exact size and position of the text | XML | check by eye after import |
| "Dip to White" and "Push" | XML | names written the Premiere way; their conversion is not checked |
| A single video track, no text or level | EDL | prefer the XML |
| No volume curve | all outputs | breathing spaces and high points marked with markers; set by ear |
| Normal speed only | `montage.json` | no slow motion or speed-up is written |
| A final black is a gap on V1 | FilmCraft, XML, EDL | a "whole sequence" export stops at the last item (seen in FilmCraft); export from 0 to the length of the edit (`--rendre`, or in and out points) |
| Black and white, widescreen format, grading, reframing to 9:16 or 1:1 | all outputs | flagged in the edit plan (reframing in `journal`), done in the software |
| Credits of a trailer for a work, titled chapters of a documentary, narrated fiction | `assemble.py` | to place by hand |
| Match cut on action, cut hidden in the dark, meaning of sentences, story of a sketch | `assemble.py` | the script does not decide them: "to check by eye" notes in `journal` |
