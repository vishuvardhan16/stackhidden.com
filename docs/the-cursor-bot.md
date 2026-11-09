# The Cursor Bot

The small friend in the bottom-right corner of the page. Since Nov 8, 2026 it is the owner's own drawing: an anime-style boy with messy brown hair and a big smile, in a round frame. Before that it was a small terminal bot drawn in the site's blue line style (Oct 2026, also the owner's idea). It is still the one playful thing on a serious page, kept small on purpose.

The drawing is an illustration, not a photograph. The site's no-photo rule is about photographs of the owner, and it stands.

## What it does

- **Leans toward the pointer.** It tilts up to 5 degrees and shifts up to 4px toward the cursor, easing rather than snapping, so the movement feels weighted.
- **Breathes.** A slow rise and fall of 2px, every 3.4 seconds.
- **Blinks.** Every 2.6 to 5.8 seconds, on a random timer, the way a person does rather than on a beat.
- **Laughs.** Every 11 to 18 seconds, and whenever the pointer comes within 140px, at most once every 4 seconds: the eyes squint into happy crescents, it hops, and the sparkles quicken.
- **Sparkles.** Four small golden sparkles twinkle round the frame, picking up the warm light in the drawing.
- **Sleeps.** Under reduced motion (the operating system setting, or the footer's Reduce motion) none of the above runs. It holds still, dims, and shows "z z".

## How the eyes blink on a painting

The drawing is a single image, so its eyes cannot move by themselves. The closed lids and the happy crescents are painted over them in an SVG laid exactly on top of the image, in the image's own 240-pixel space. Their colours were sampled from the skin right round each eye (a warm, shaded tone near #9b5a41, deepening under the hair) and their edges are softened with a 1.1px blur, so they blend in at the size the friend is shown. The lash lines take the drawing's own dark brown. Between blinks the lids are fully transparent, so the drawing shows exactly as the owner drew it.

The eye positions are fixed to this drawing: left eye at about (96.5, 106.6) and right at about (154.4, 103.6), tilted 4 degrees with the head. A new drawing needs new positions and colours.

## Implementation notes

- **Markup** (`index.html`): four nested layers, so no two motions fight over one transform. `.bot-head` leans (app.js), `.bot-float` breathes, `.bot-hop` hops, and `.bot-frame` holds the image (`assets/corner-drawing.webp`, 240px square, 14KB) and the lids.
- **Behaviour** (`app.js`, "The corner friend"): the pointer loop eases by elapsed time, not per frame, so the glide is the same at 30, 60, or 120 frames a second. Easing per frame made it turn slowly on a slow machine, and a test caught it halfway. The loop runs only while motion is allowed: turning motion off stops it and sets the friend straight, and turning it back on restarts it, never a second copy. The blink and laugh timers do nothing under reduced motion or in a hidden tab.
- **Styles** (`style.css`, "Corner friend"): every animation is gated on motion being allowed, both ways, and the site-wide reduced-motion rule switches off every animation as a second safety net. The frame is 100px on desktop and 76px at 640px and under.
- **Out of the way:** it is `aria-hidden` and `pointer-events: none`, so it never intercepts a click and never announces itself to a screen reader. It is hidden in print.

## Changing the drawing

Replace `assets/corner-drawing.webp` with a square crop, then move the lid ellipses and lash lines in `index.html` onto the new eyes and re-sample their colours. Check a blink and a laugh at real size in both themes before shipping. `tests/test_motion.py` checks the behaviour, not the picture.
