# The Cursor Bot

The small terminal bot fixed in the bottom-right corner of the page. It was the owner's idea, and it is the one playful thing on a serious page, kept small on purpose.

## What it does

- Its pupils follow the visitor's cursor around the screen, easing toward it rather than snapping, so the gaze feels weighted.
- The head leans a few degrees toward the cursor.
- It blinks every few seconds, on a random timer, the way a person does rather than on a beat.
- Under reduced motion it does none of this. Its eyes close and it sleeps.

## The face

The bot is drawn as an inline SVG in the site's blue line style. Its warmth came from a second piece of inspiration the owner approved: the Muse avatar, Jolly, whose whole effect is roundness and a simple friendly face. So the shell corners are well rounded, the flat mouth line became a small smile, and there are two faint violet cheeks. The terminal shape and the antenna stayed. It is a nod, not a copy.

## Implementation notes

- The tracking math lives in `app.js`, next to the other pointer work, and shares the page's reduced-motion check.
- The blink uses CSS transforms on the eye groups with the transform origin set so the eyes scale shut in place.
- It is `aria-hidden` and `pointer-events: none`. It never intercepts a click and never announces itself to a screen reader.
- It is hidden in print.
