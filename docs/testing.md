# Testing

Every change is tested locally before it ships and checked live after it lands. The tests use Playwright with a headless Chromium against the local files, then against the real site.

## Before a push

- The page loads with zero JavaScript errors and zero console errors.
- The specific feature changed gets a specific check. Examples from past rounds: case files open and deep links land on the right file; the palette opens with Ctrl+K and lists the right commands; the corner friend leans toward the cursor in both directions; the animated core produces different frames over time; the quote carousel advances and loops.
- Both themes get checked when a visual change lands. Colors and artwork follow the theme; the corner friend's ring takes the theme's accent.
- Reduced motion gets checked when anything animated changes: one still frame, the corner friend asleep, no movement.
- Widths: desktop wide, a medium window, and a 360px phone width. Horizontal overflow must be zero at every width.
- Counts that the copy claims are counted in the DOM, not eyeballed: experience points, chips, case files.
- A visual change gets an accessibility audit: axe-core over the changed sections, in both themes, with no violations.
- A bug fix gets a regression test, and that test is run against the code before the fix to confirm it fails there. A test that passes on the broken code guards nothing.

## After a push

- Confirm both Actions runs for the pushed commit succeeded: `site-checks` and `pages build and deployment`.
- Reload stackhidden.com until the new version serves, then confirm the change is present in the live page, in the owner's terms: the thing he asked for is visible and works. The bare domain can be served from cache for a few minutes after a deploy; `https://stackhidden.com/index.html` shows the new version first.
- Confirm the commit count and the newest summaries on the repo match what was pushed.
- Check the live page the way a returning visitor gets it, not only fresh: open it before the push, then after the deploy reload it normally (not a hard refresh) and check the layout at desktop and phone width. A visitor's browser keeps files for up to 10 minutes, so a page can arrive with an older stylesheet or script. On Nov 8, 2026 that broke the hero for the owner right after a deploy, which every local test had passed. `index.html` now asks for both files by content version, and `scripts/stamp-assets.py` keeps those versions right, but this check is the one that would show a mismatch.
- Confirm no portrait photo appears anywhere on the live page.
- Open a missing address, such as `https://stackhidden.com/nope`, and confirm the site's own 404 page answers.
- Grep the served page for the words that must not appear. The standing one is "Senior", which must be zero everywhere, including comments.

## A note on honesty

If a check fails, the report says so, in plain words, with the failing check named. A fix that follows a failed check gets its own commit that says what went wrong. The history is not cleaned up to hide it.

## The automated suite

The checks above now also live as an automated suite in `tests/`, one module per area, with `docs/test-plan.md` saying what each module protects. Run the whole suite with `scripts/run-tests.sh`. The same suite runs in CI on every push, so a change that breaks a content rule or a behaviour fails before it can be called done.
