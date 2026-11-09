# The Hero Background

The moving network behind the top of the page, since Nov 8, 2026. Thin blue lines join scattered nodes, and records travel along them from left to right: violet and cyan ones, and one amber one, the record that gets flagged. A node lights up as a record passes through it. It runs edge to edge, from under the header down past the At a glance panel, and fades into the page.

## Where it came from

The owner liked the looping video background on aiasplus.org and asked for something like it. He chose to keep the action-figure video moving as well, so the top of the page now has two loops. He then picked this look from three original options, each shown to him in place on the page: data streams, drifting light, and this lineage network. Nothing here is taken from aiasplus.org or any other site. The network is the subject of his research drawn one more way, like the lineage core and the background canvas.

## The files

Eight files in `assets/`, all rendered by `scripts/render-hero-network.py` (that script's header has the full method):

| File | Size | Used |
| --- | --- | --- |
| `hero-network-dark.mp4`, `hero-network-light.mp4` | 1920x1080, about 1.0 and 0.8 MB | Wider than 920px |
| `hero-network-dark-narrow.mp4`, `hero-network-light-narrow.mp4` | 720x1080, about 0.4 and 0.3 MB | 920px and under |
| The four `.webp` stills, one per video | 19 to 42 KB | Under the video, and instead of it when it does not play |

Each video is a 10-second seamless loop at 30 fps, H.264 with no sound. Each still is its video's first frame, taken from the encoded file, so the moment the video takes over from the still is invisible. A visitor downloads one still and, at most, one video: the one for their theme and width.

The narrow files are the middle of the same scene with every line and glow drawn 1.6 times as heavy. On a phone that strip is seen zoomed in, and at the desktop weight its 1px lines nearly disappeared under the text tint.

## How it is built

- **Markup.** `<div id="heroBg">` is the hero's first child, with an empty `<video>` inside. The four video names are `data-src-*` attributes on it, so they can be found in `index.html` with the rest of the page's assets. The div repeats its own position inline (`position:absolute; z-index:-1; pointer-events:none`) so it stays out of the hero's grid even under a stylesheet that predates it. Right after the first deploy, the owner's browser ran the new page with its cached stylesheet from before; the unstyled layer took the hero's first column, his name and intro moved right, and the panel dropped below. The stylesheet and script are now also asked for by content version, so that mismatch cannot recur (see [[Deployment]]).
- **Layer.** The layer is `position:absolute; z-index:-1` inside `.hero`, and `.hero` is deliberately not a stacking context. The layer therefore sits in the page's own stack: above the fixed background canvas, below all content and the cursor glow. It reaches 24px above the top of the page and spans the full viewport width (`left` and `right` at `50% - 50vw`).
- **Height.** On desktop it covers the whole hero plus 160px. At 920px and under, where the hero is one long column, it is a band about one screen tall (between 700 and 1100px). The bottom 260px fades out with a mask.
- **Still.** The still is the layer's `::before`, chosen in `style.css` by theme and by width, but only once app.js has set `data-bg` on `<html>`. It fades in over 0.6s once its file has arrived (at once under reduced motion), and again when a theme flip or a width change picks another. It waits for app.js because, loaded with the stylesheet, it shared a slow phone's bandwidth with app.js, which fills in the hero's clock line, and held back the first paint by about 170ms. On desktop it is up by the first paint anyway. With JavaScript off, a `<noscript>` style in the head shows the dark still at once (no script means the dark theme), and it is all anyone gets.
- **Tint.** A `::after` tint over the video keeps the text readable. On desktop it runs from 66% of the page colour on the text side to 18% behind the At a glance panel. On one column it is even: 45% in dark mode, 64% in light. The tints are theme tokens (`--scrim-a`, `-b`, `-c`, `-n`), like every other colour on the page.
- **Video.** The video sits between the still and the tint. It is transparent until it is playing, then fades in over 0.4s.

## How it behaves

The script is in `app.js`, under "Hero background", right after the figure video, and it follows the figure's rules:

- The video gets a `src` only when it may play, and not before the page's load event, so its download never competes with the page's own files. Until then the browser has nothing to download.
- It plays while motion is allowed (the operating system setting and the footer's Reduce motion), the layer is on screen, and the tab is visible. Otherwise it pauses.
- Under reduced motion, Data Saver, or a 2G connection, no video is ever downloaded and the still stays.
- When the theme flips or the width crosses 920px, the old video is hidden at once, so the new still shows and the old picture never sits over it. Then the matching file loads and plays. If motion is off at that moment, nothing new downloads until it is turned back on.
- A `playing` event from a file that no longer matches is ignored, so a late event cannot bring the old video back.
- If a browser refuses to autoplay (some phones in low-power mode), the still simply stays.

It is decorative: the layer is `aria-hidden`, the video is muted, has no controls, and cannot take focus, and the layer ignores the pointer. It is gone in print and under forced colours (Windows high contrast).

## Readability

The text's contrast over the background was measured frame by frame across the whole loop, every half second, at 360, 390, 768, and 1440px in both themes. Every text block clears WCAG AA (4.5:1, or 3:1 for large text) for at least 99% of the pixels behind it at every moment. The tightest is the small blue "New York City" line in light mode on one column, at 4.7:1. Checked every 1/6 s at 1400 and 390px in both themes, no moment of the loop scored lower than the still, so the still is a fair stand-in for the loop, and `tests/test_background.py` checks the still in CI.

## Load time

Measured on Nov 8, 2026 against the version before it, five runs each, median. On a phone (390px, slow 4G at 1.6 Mbps and 150ms, CPU 4x slower, as Lighthouse's mobile run uses), the largest paint went from 2.39s to 2.43s; it was 2.52s until the still was made to wait for app.js. The still then fades in at about 2.7s and the video plays from about 3.7s. On desktop, unthrottled, the largest paint stays under a quarter of a second, the still is up by the first paint, and the video plays within about 0.25s. A visitor whose motion is allowed downloads about 1MB more on desktop and 0.4MB more on a phone.

## Changing it

- **Colours, density, speed, stroke weight:** edit `scripts/render-hero-network.py` and run it from the repository root. It rewrites all eight files in a few minutes. Needs numpy, opencv-python, Pillow, and ffmpeg.
- **Tint:** the `--scrim-*` tokens in `style.css`. Re-run `test_background`: its contrast checks fail if the text drops below AA.
- **Height or reach:** the `#heroBg` rules in `style.css`. `test_background` pins the layer to the top of the page and the full width, and keeps the phone band between one screen and 1100px.
- **Removing it:** delete the `#heroBg` block from `index.html`, its rules from `style.css`, its block from `app.js`, the eight files, and `tests/test_background.py`, and take it out of the module lists in the CI workflow and `scripts/run-tests.sh`.
