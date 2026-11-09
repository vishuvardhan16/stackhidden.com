# The Cursor Bot

The small friend in the bottom-right corner of the page. Since Nov 8, 2026 it is the owner's own drawing: an anime-style boy with messy brown hair and a big smile, cut out of the drawing's backdrop so he sits on the page itself, with no frame. Before that it was a small terminal bot drawn in the site's blue line style (Oct 2026, also the owner's idea). It is still the one playful thing on a serious page, kept small on purpose.

The drawing is an illustration, not a photograph. The site's no-photo rule is about photographs of the owner, and it stands.

## What it does

- **Leans toward the pointer.** It tilts up to 5 degrees and shifts up to 4px toward the cursor, easing rather than snapping, so the movement feels weighted.
- **Breathes.** A slow rise and fall of 2px, every 3.4 seconds.
- **Blinks.** Every 2.6 to 5.8 seconds, on a random timer, the way a person does rather than on a beat.
- **Laughs.** Every 11 to 18 seconds, and whenever the pointer comes within 140px, at most once every 4 seconds: the eyes squint into happy crescents, it hops, and the sparkles quicken.
- **Sparkles.** Four small golden sparkles twinkle round his head, picking up the warm light on his hair.
- **Sleeps.** Under reduced motion (the operating system setting, or the footer's Reduce motion) none of the above runs. It holds still, dims, and shows "z z".

## How he blends into the page

The drawing came with a golden, sunlit backdrop. In a round frame with a white edge it looked stuck on: the gold was the warmest, brightest thing on a cool blue page. The owner asked for it to blend in, and chose, from four options shown on the real page in both themes, no frame at all (the others: the gold kept with a feathered edge, and a frosted disc like the site's cards).

- **Cut out.** `scripts/cut-corner-friend.py` lifts him out of the backdrop with rembg's isnet-anime model, a segmentation model trained on anime art, which keeps the hair strands. Where a hair edge is part hair and part backdrop, the gold that bled into it is solved back out, so no golden halo rings him on the light theme. Inside him he is fully opaque, so the page never shows through his face. The script's header explains each step.
- **The page's own light.** Behind him is a soft radial glow in the page's accent (`--friend-glow`: the dark theme's blue at 26%, the light theme's at 14%), like the glow that follows the cursor. Under him is a shadow that follows his silhouette (`--friend-shade`), not a box.
- **A pool of the page's own colour.** Under the glow sits a soft radial pool of the page background at 95% (`--friend-pool`), fading to nothing. On bare page it cannot be seen. Where content scrolls past him it fades the text out before it reaches him: at 1280px the text column ends under him, and without the pool lines of text ran straight into his hair and showed through his faded shoulders. It must match `--bg` exactly, or it shows as a smudge; `test_friend` reads it against the live token, so change both together.
- **Soft cuts.** The drawing's edge cuts through his crown and his shoulders. Those two places fade into the page (a mask on `.bot-frame`: the top 6% and the bottom 20%), so no straight line shows.
- **Asleep** he dims, as before. Fading him into the page instead was tried and let the network lines show through his face.
- **A new file name.** The picture is `assets/corner-friend.webp`, not the old `corner-drawing.webp`. GitHub Pages lets browsers reuse a file for 10 minutes, so a returning visitor's cached copy of the old, gold-backed picture could otherwise meet the new frameless style and show as a gold square.

## How the eyes blink on a painting

The drawing is a single image, so its eyes cannot move by themselves. The closed lids and the happy crescents are painted over them in an SVG laid exactly on top of the image, in the image's own 240-pixel space. Their colours were sampled from the skin right round each eye (a warm, shaded tone near #9b5a41, deepening under the hair) and their edges are softened with a 1.1px blur, so they blend in at the size the friend is shown. The lash lines take the drawing's own dark brown. Between blinks the lids are fully transparent, so the drawing shows exactly as the owner drew it. The cut-out keeps every fully opaque pixel exactly as painted, so the lids still match.

The eye positions are fixed to this drawing: left eye at about (96.5, 106.6) and right at about (154.4, 103.6), tilted 4 degrees with the head. A new drawing needs new positions and colours.

## Implementation notes

- **Markup** (`index.html`): four nested layers, so no two motions fight over one transform. `.bot-head` leans (app.js) and carries the glow, `.bot-float` breathes, `.bot-hop` hops and casts the shadow, and `.bot-frame` holds the image (`assets/corner-friend.webp`, 240px square with transparency, 20KB) and the lids, and does the fade.
- **Behaviour** (`app.js`, "The corner friend"): the pointer loop eases by elapsed time, not per frame, so the glide is the same at 30, 60, or 120 frames a second. Easing per frame made it turn slowly on a slow machine, and a test caught it halfway. The loop runs only while motion is allowed: turning motion off stops it and sets the friend straight, and turning it back on restarts it, never a second copy. The blink and laugh timers do nothing under reduced motion or in a hidden tab.
- **Styles** (`style.css`, "Corner friend"): every animation is gated on motion being allowed, both ways, and the site-wide reduced-motion rule switches off every animation as a second safety net. The friend is 100px on desktop and 76px at 640px and under.
- **Out of the way:** it is `aria-hidden` and `pointer-events: none`, so it never intercepts a click and never announces itself to a screen reader. It is hidden in print.
- **Tests:** `tests/test_motion.py` checks how he moves; `tests/test_friend.py` checks how he sits on the page (the page shows wherever the drawing is clear, the glow, the pool, the shadow); `tests/test_static.py` keeps the picture cut out. `docs/test-plan.md` has the details.

## Changing the drawing

1. Run `python3 scripts/cut-corner-friend.py path/to/drawing.png` (it needs `pip install "rembg[cpu]" scipy pillow`; the first run downloads the 176MB model). It writes `assets/corner-friend.webp`. The owner's original is not in the repo; the script names its SHA-256 and says if the file given is a different one.
2. For a new drawing, change the crop box in the script so his head fills the square the same way, then move the lid ellipses and lash lines in `index.html` onto the new eyes and re-sample their colours.
3. Look at it on the page at real size in both themes, asleep, and mid-blink and mid-laugh, before shipping. Look closely at the hair edges on the light theme, where a leftover halo shows first.
4. Run the suite. `test_friend` fails if the new picture has a backdrop or the page does not show round him.
