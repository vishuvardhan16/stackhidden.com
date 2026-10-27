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
