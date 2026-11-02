# Publisher Logos

Published Writing, Speaking, and the Featured In captions open with a publisher masthead: the publisher's name in the site's own type, a pill for the kind of piece, then the date. Each masthead has a slot for the publisher's official logo.

## Why the slots start empty

A publisher's logo is its trademark. The site does not draw, trace, or copy one. Logos go in only as official files the owner downloads from the publisher, used the way the publisher's guidelines allow. Until then the typographic masthead stands on its own.

## Getting an official file

1. Look for the publisher's media kit, press kit, or brand page. Most publishers have one, often linked from the site footer or an "About" or "Press" page.
2. Read its usage guidelines: clear space, colours, and whether a contributor or speaker may show the logo.
3. If there is no kit, or the guidelines are unclear, ask your editor or event contact before using the logo.
4. Prefer SVG. For PNG, use a file at least 48px tall, so it stays sharp at the 24px display height on high-density screens.

## Adding one

1. Save the file as `assets/logos/<slug>.svg` (or `.png`):

   | Publisher | Slug | Appears in |
   | --- | --- | --- |
   | TDWI Upside | `tdwi` | Published Writing |
   | AI Loves Data | `ailovesdata` | Published Writing |
   | ExchangeWire | `exchangewire` | Published Writing |
   | Marketplace Risk | `marketplacerisk` | Speaking |
   | NICE-TEAS ASIA | `niceteas` | Speaking |
   | Label Your Data | `labelyourdata` | Featured In (two slides) |
   | Informatics Magazine | `informatics` | Featured In |

2. In `index.html`, find that publisher's `<span class="pub-mark">`. It holds an HTML comment with the exact `<img>` to use. Replace the comment with the `<img>`, and change the extension if the file is a PNG. Label Your Data has two slides, so it has two slots.
3. Keep `alt=""`. The publisher's name stays in the page for screen readers, and is hidden only visually once a logo is present. A descriptive alt would make screen readers say the name twice.
4. Run `scripts/run-tests.sh`. `test_publishers` checks that the logo shows and that no slot asks for a missing file; a wrong path fails the suite with a "Failed to load resource" error.
5. Look at the card in both themes. In dark mode the logo sits on a small light plate, because most logos are dark on transparent.
6. If the publisher supplies a version made for dark backgrounds, save it as `assets/logos/<slug>-dark.svg` and put both images in the slot. Each theme then shows its own file, with no plate:

   ```html
   <img class="pub-logo for-light" src="assets/logos/tdwi.svg" alt="" width="120" height="24">
   <img class="pub-logo for-dark" src="assets/logos/tdwi-dark.svg" alt="" width="120" height="24">
   ```

## Removing one

Put the comment back in the slot, or simply delete the `<img>`. An empty slot collapses, and the masthead shows the publisher's name again.
