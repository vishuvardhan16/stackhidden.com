# Testing

Every change is tested locally before it ships and checked live after it lands. The tests use Playwright with a headless Chromium against the local files, then against the real site.

## Before a push

- The page loads with zero JavaScript errors and zero console errors.
- The specific feature changed gets a specific check. Examples from past rounds: case files open and deep links land on the right file; the palette opens with Ctrl+K and lists the right commands; the bot's pupils move toward the cursor in both directions; the animated core produces different frames over time; the quote carousel advances and loops.
- Both themes get checked when a visual change lands. Colors, artwork, and the bot all follow the theme.
- Reduced motion gets checked when anything animated changes: one still frame, sleeping bot, no movement.
- Widths: desktop wide, a medium window, and a 360px phone width. Horizontal overflow must be zero at every width.
- Counts that the copy claims are counted in the DOM, not eyeballed: experience points, chips, case files.

## After a push

- Reload stackhidden.com until the new version serves, then confirm the change is present in the live page, in the owner's terms: the thing he asked for is visible and works.
- Confirm the commit count and the newest summaries on the repo match what was pushed.
- Confirm no portrait photo appears anywhere on the live page.
- Grep the served page for the words that must not appear. The standing one is "Senior", which must be zero everywhere, including comments.

## A note on honesty

If a check fails, the report says so, in plain words, with the failing check named. A fix that follows a failed check gets its own commit that says what went wrong. The history is not cleaned up to hide it.

## The automated suite

The checks above now also live as an automated suite in `tests/`, one module per area, with `docs/test-plan.md` saying what each module protects. Run the whole suite with `scripts/run-tests.sh`. The same suite runs in CI on every push, so a change that breaks a content rule or a behaviour fails before it can be called done.
