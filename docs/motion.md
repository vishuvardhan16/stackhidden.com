# Motion

Every moving thing on the page: what starts it, how long it runs, and what happens under reduced motion. Reduced motion means either the operating system setting or the footer's Reduce motion control. The control's choice is stored in the visitor's browser, and the inline script in the head applies it before first paint, so a visitor who turned motion off never sees the first frames of anything.

## Inventory

| Piece | Starts | Runs | Under reduced motion |
| --- | --- | --- | --- |
| Background lineage canvas | Page load | Slow drift, loops | One still frame |
| Lineage core (At a glance panel) | Page load, while on screen and the tab is visible | A ring takes 22 to 39 seconds to go round (twice as fast since Nov 8, 2026), loops | One still frame |
| Hero figure | Page load, while on screen | 10-second muted video, loops | The poster still. The video is never downloaded (v5), and Data Saver or a 2G connection gets the poster too |
| Hero background (Nov 8, 2026) | Page load, while the layer is on screen and the tab is visible | 10-second muted network video behind the top of the page, loops; the file follows the theme and the width | The network still. No video is downloaded, and Data Saver or a 2G connection gets the still too. See [[The Hero Background]] |
| Hero intro (v5) | Page load | Once, about 1.2s: the hero's lines rise in reading order, 70ms apart | Not played |
| Cursor bot, the corner friend (Nov 8, 2026) | Page load, and pointer movement | The owner's drawing: leans toward the pointer, breathes every 3.4s, blinks every 2.6 to 5.8s, laughs every 11 to 18s and when the pointer comes within 140px, sparkles twinkle round it. See [[The Cursor Bot]] | Still and dimmed, with "z z" |
| Cursor glow | Pointer movement, fine pointers only | Follows the pointer | Hidden |
| Click burst | A click on the page background | Once, about 0.55s | Not played |
| Section reveal | A section below the fold enters view | Once, 0.7s | Shown in place |
| Lineage packets | Page load | 7-second loops along the edges | Hidden |
| Lineage draw-in (v5) | The graph enters view, if it started below the fold | Once, about 2.7s, in the order data flows | Drawn in place |
| 2026 trace render (v5) | The trace enters view, if it started below the fold | Once, about 1.6s, bars in date order | Drawn in place |
| Career render (v5) | The career chart enters view, if it started below the fold | Once, about 1.6s, spans in date order | Drawn in place |
| Sent records (v5) | Send a clean or a bad record | About 4s for a clean record, 3s for a bad one | Arrive at once; the log, counter, and announcement are identical |
| Quote carousel | Page load | Advances every 5s; pauses on hover and keyboard focus, and holds while a quote is open | Holds its slide; arrows and dots still work |
| Read my quote chevron | Opening or closing a quote | Turns over, 0.2s | Turns at once |
| Trace highlight (query console) | The Trace button | Outline pulses twice; removed after 2.8s | Outline only |
| Smooth scrolling | Links and jumps | The browser's smooth scroll | Instant |

The scroll progress bar under the header follows the scroll position. It has no animation of its own, so it behaves the same either way.

## Rules for adding motion

These come from the v5 pass, and every v5 animation follows them.

- **Prefer motion that answers a person.** Opening a case file, sending a record, tracing a row: motion that shows what changed after someone acted is welcome.
- **No new loops.** The ambient loops above predate v5. New animations run once. One exception, by the owner's decision on Nov 8, 2026: the hero background, a looping video he asked for after seeing one on aiasplus.org, with the action-figure video kept moving beside it. It plays under the figure video's rules and stops with everything else. Any further loop needs the owner's word too. The same day he asked for the corner friend to be animated ("blinking, smiling"), so its breathing, blinking, laughing, and sparkles are his word as well; they stop with everything else.
- **One load moment.** The hero intro is the page's single orchestrated load sequence. Do not add a second.
- **Reveals must teach.** A first-view reveal should show something true about what it reveals: the trace and the career chart render in date order, the graph draws in the order data flows.
- **Never hide what is visible, never hide without script.** Reveals arm only from app.js, only when motion is allowed, and only when the element starts below the fold. With JavaScript off, nothing is hidden.
- **Clean up.** When a reveal finishes, it removes every class, custom property, and inline style it added, so the page is exactly what it would have been without it. `tests/test_animations.py` checks this.
- **Respect both reduced-motion paths.** Check `motionOff()` in app.js, and gate CSS animations on `prefers-reduced-motion: no-preference` and the absence of `data-motion="reduced"`.

## Where the code lives

- Hero intro: `style.css`, "V5 motion", part 1. Pure CSS.
- Trace render and lineage draw-in: `app.js`, "First-view reveals", sharing `revealOnce()`. Their CSS is in `style.css`, "V5 motion", parts 2 and 3.
- Career render: `app.js`, "Career, as a trace", also through `revealOnce()`. Its CSS is in `style.css`, "Career, as a trace".
- Sent records: `app.js`, "Send a record through the lineage explorer".
- Hero background: `app.js`, "Hero background", right after the figure video; its layer, stills, and tint are in `style.css` under the same name, and its files come from `scripts/render-hero-network.py`. See [[The Hero Background]].
- Everything older: see [[How the Site Works]], [[The Lineage Core]], and [[The Cursor Bot]].
