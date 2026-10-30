
<a href="https://github.com/sebmake/skills">
<img width="720" alt="Previews from the four skills: slide layouts, a product film, an app walkthrough built in EffectCraft and the same walkthrough assembled in FilmCraft" src="assets/likeapplepls.jpg" />
</a>

# LikeApplePLS

Four Claude skills for people who present, launch, animate and edit, built on the way Apple makes its keynotes.

Everyone can tell an Apple keynote when they see one. Saying what makes it work is harder, and "make it look like Apple" gets you big type on black and not much else.

These skills come from eight public Apple keynotes, March 2019 to September 2026, studied slide by slide, shot by shot and frame by frame. Most rules carry a count, so you know how often Apple actually does it, and anything that couldn't be measured is labeled a convention.

What you make keeps your colors, your fonts, your product and your numbers. Nothing from Apple ends up in it.

The skills' instructions are in French. Decks and films can be in English or French.

## Install

```bash
npx skills@latest add sebmake/skills/LikeApplePLS
```

To install a single skill, add its folder name:

```bash
npx skills@latest add sebmake/skills/LikeApplePLS/sebmake-keynote-likeapple-pls
```

Each skill also has its own repo, with its Claude Code plugin and its releases: [keynote](https://github.com/sebmake/sebmake-keynote-likeapple-pls), [product film](https://github.com/sebmake/sebmake-videopresentation-likeapplepls), [motion design](https://github.com/sebmake/sebmake-motiondesign-likeapplepls), [video edit](https://github.com/sebmake/sebmake-videoedit-like-applepls).

## Why use it?

The look is the easy part.

The rules underneath are less obvious, and some go against common habits. No number ever counts up to its value (0 out of 27). In the films that save the product for the end, it shows up in full between 69% and 82% of the running time, never in the first shot. Music doesn't drive the cuts. Over 95% of shot changes are straight cuts, and a text card stays up 1.2 s plus 0.3 s per word.

An agent left to itself will guess at all of that, and it will make up what's missing too. In a side-by-side test on decks, the agent working without the skill invented amounts to fill the empty slides. These skills don't: a missing figure, price or date stays as a placeholder in a deck or a film, and the editing skill leaves out any name or quote you didn't give it.

## Reference

- **[sebmake-keynote-likeapple-pls](./LikeApplePLS/sebmake-keynote-likeapple-pls/SKILL.md)** — Builds a 16:9 deck the way Apple builds its keynotes, plus the script to read over it, for Keynote, PowerPoint, Figma Slides, Canva or video.
- **[sebmake-videopresentation-likeapplepls](./LikeApplePLS/sebmake-videopresentation-likeapplepls/SKILL.md)** — Makes a silent product film, one to two minutes long, cut like Apple's reveal films, then 15 to 60 second versions in 16:9, 9:16 and 1:1.
- **[sebmake-motiondesign-likeapplepls](./LikeApplePLS/sebmake-motiondesign-likeapplepls/SKILL.md)** — Tells you how to animate a title, a number, a logo or a screenshot, from about 640 measured animations, then writes the After Effects or EffectCraft script. Also builds narrated app walkthroughs, layer by layer.
- **[sebmake-videoedit-like-applepls](./LikeApplePLS/sebmake-videoedit-like-applepls/SKILL.md)** — Cuts your footage like Apple's keynote films, in FilmCraft or as an XML file for DaVinci Resolve and Premiere Pro, assembles rendered chapters with voice, subtitles and ducked music, and reviews an edit you've already made, usually down to the timecode.

---

Not affiliated with, endorsed or sponsored by Apple Inc. Apple, Keynote and Final Cut Pro are trademarks of Apple Inc., registered in the U.S. and other countries. After Effects and Premiere Pro are trademarks of Adobe. DaVinci Resolve is a trademark of Blackmagic Design. MIT License.
