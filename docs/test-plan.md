# Test plan

What the automated suite in `tests/` protects, module by module. Run it all with `scripts/run-tests.sh`; CI runs the same suite on every push. Every browser module shares `tests/helpers.py`, which loads the page (from the local files, or from `BASE_URL` in CI), collects every page error and console error, and fails the test if any appear. A silent script error can therefore never pass unnoticed, whatever the module was checking.

## test_static

The owner's standing content rules, checked against the source files with no browser, so this is the fastest and most stable part of the suite. It asserts that the word "Senior" appears nowhere in the site sources, that no portrait file exists or is referenced, that the social preview points at the designed share card, that the charset is declared within the first 1024 bytes, and that the published counts hold: exactly four case files, ten Amazon experience points, 48 skill chips. It also keeps the Karyna Naminas credit line in place and guards that the removed hero-flow diagram stays removed. Copy edits are the most common change to this site, and this module is what makes a careless one fail loudly instead of quietly breaking a rule.

## test_theme

The dual theme system. The default theme renders, the toggle flips `data-theme`, and the choice survives a reload, because the persistence is the part a visitor actually feels: get it wrong and a returning visitor gets a flash of the wrong theme or loses their setting.

## test_palette

The command palette. Ctrl+K opens it with its commands populated, and Escape closes it. The palette is the page's keyboard front door; if it opens empty or traps focus, keyboard visitors lose the fastest route around the site.

## test_cases

The four engineering case files. Each one opens and closes in place, and the `#case=icm` deep link opens only the ICM file. Deep links are shared and bookmarked, so the wrong file opening is a public bug, not a private one.

## test_carousel

The Featured quote carousel. The dots track the active slide, including `aria-current` on the active dot, and the next button advances. The carousel carries the two Label Your Data quotes, and its state is what a screen reader announces; the visible slide and the announced slide must agree.

## test_explorer

The interactive lineage explorer. It has exactly nine nodes, and hovering a stage lights only its connected edges. The explorer is the site's signature interactive piece and the visual form of the owner's research; a wiring mistake here misstates the architecture it exists to explain.

## test_layout

Responsive behaviour at 360px, 768px, and 1400px. At each width there is no horizontal overflow, measured on both the document and the body width (the body check is the one that caught a real bug: a long GitHub link clipped outside its card on phone widths, hidden from the document metric). The data hero figure stays visible and inside the viewport, and the Featured credit line is present at every width.

## test_motion

Motion, and its absence. The cursor bot's pupils move toward the pointer; the animated lineage core keeps drawing new frames; the footer motion toggle puts the bot to sleep; and with reduced motion emulated, the core stills and the bot sleeps. Reduced motion is a promise the site makes in its own copy, and this module is what keeps the promise honest in both directions: things move when they should, and stop when they must.

## test_regressions

Bugs that shipped silently before v5 (November 2026), one test each. A shared `var nodes` let the lineage explorer overwrite the background canvas's particle array, so the background painted nothing until a resize and the explorer threw after one; the scrollspy selector matched no links; Contact never lit up at the bottom of the page; the footer Reduce motion control did not stop the carousel; the hero core stayed frozen after motion was turned back on; and every toggle stacked another canvas loop. Each test was run against the pre-v5 code and failed there before it passed on the fix, so it guards the real failure rather than a guess at it. None of these bugs threw at load or changed how the page looked in a screenshot, which is why they need tests to stay fixed.

## test_query

The Query this page console. Its central promise is that its tables are the page, so the first tests check that against the DOM directly: every table's row count equals the number of cards, slides, spans, roles, case files, and skill chips on the page, and titles and dates read back exactly as published. The rest pin what a reader relies on: grouping and sorting, NULL semantics (IS NULL finds the current role, = NULL never matches and says why), case-insensitive LIKE, and LIMIT; error messages that explain and suggest ("titel" suggests "title"); visitor input that is never rendered as HTML, checked with an image-tag payload; Trace outlining the right element, bringing a quote's carousel slide forward, and Back returning focus to the Trace button; Tab completing a table name and otherwise moving focus so the keyboard is never trapped; history restoring an unsent draft; the palette running SQL; the query kept in the URL; a #q= link running on arrival; and at 360px, wide results scrolling inside their own box with dates kept on one line and the header no taller than 100px.

## test_records

Send a record through the lineage explorer. The feature makes one claim, that a bad record never reaches anything past the quality gate, and the module checks it from the pipeline log rather than from the animation: a clean record's log runs ingest, transform, gate, lake, api, analytics; a bad record's stops at gate then anomaly, with no lake line and both lines marked failed. Two records in flight at once keep their own routes. Under reduced motion the record arrives at once with no moving dot. At 360px the graph's labels stay at least 10px tall and the graph scrolls inside its wrapper without widening the page.

## test_animations

The three v5 animations: the hero intro, the 2026 trace render, and the lineage draw-in. Each must play when motion is allowed, never play when it is not, and leave the page exactly as it would be without it. So the module checks that the hero animates; that the trace arms below the fold, renders on first view, and then drops every class and custom property it added; that the graph arms, draws, and then carries no inline declarations, keeps its dashed anomaly edge, and still traces on hover; that turning motion off mid-draw finishes the drawing at once; that a visitor arriving by a #lineage link always ends with a fully drawn graph (waiting for the outcome, since the browser smooth-scrolls to the anchor first); that the head script applies a stored Reduce motion choice before app.js runs; and that under reduced motion nothing is armed or animated. It also pins the trace's accuracy: every bar width and month label is recomputed from its date on the Jul 1 to Dec 1 axis, because a bar that encodes a date is only worth animating if it ends on the right one.
