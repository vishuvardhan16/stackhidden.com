# Publisher Logos

Published Writing, Speaking, and the Featured In captions open with a publisher masthead: the publisher's logo (or its name in the site's own type), a pill for the kind of piece, then the date. Every publisher on the page now has its logo in place (added by the owner on Nov 2, 2026).

## Where logos come from

A publisher's logo is its trademark. Logos go in as official files the owner downloads from the publisher, used the way the publisher's guidelines allow; the one exception is recorded below. A masthead without a logo shows the publisher's name in the site's own type and stands on its own.

## Getting an official file

1. Look for the publisher's media kit, press kit, or brand page. Most publishers have one, often linked from the site footer or an "About" or "Press" page.
2. Read its usage guidelines: clear space, colours, and whether a contributor or speaker may show the logo.
3. If there is no kit, or the guidelines are unclear, ask your editor or event contact before using the logo.
4. Prefer SVG. For PNG, use a file at least twice the height it will be shown at (see the sizes below), so it stays sharp on high-density screens.

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

2. In `index.html`, put the `<img class="pub-logo">` in that publisher's `<span class="pub-mark">`. Set its `width` and `height` attributes to the file's real shape at its display height (for example `width="148" height="21"` for a 7:1 logo shown 21px tall), so the page does not shift while the image loads.
3. Keep `alt=""`. The publisher's name stays in the page for screen readers, and is hidden only visually once a logo is present. A descriptive alt would make screen readers say the name twice.
4. Give the logo its size: one line in `style.css`, in the "Logo sizing" table, such as `.pub-logo[src$="/tdwi.svg"]{--h:30px}`. See "How logos are sized" below for choosing the number. `test_publishers` fails for any visible logo without one.
5. Run `scripts/run-tests.sh`. `test_publishers` checks that every logo loads and has its size, that cards side by side still line up, that dark-mode chips match, and that no pill overflows its card at 360px. A wrong path fails the suite with a "Failed to load resource" error.
6. Look at the card in both themes, on desktop and at 360px.
7. If the publisher supplies a version made for dark backgrounds, save it as `assets/logos/<slug>-dark.svg` and put both images in the slot, each with its own size line. Each theme then shows its own file, with no chip:

   ```html
   <img class="pub-logo for-light" src="assets/logos/ailovesdata.png" alt="" width="118" height="20">
   <img class="pub-logo for-dark" src="assets/logos/ailovesdata-dark.svg" alt="" width="133" height="19">
   ```

## How logos are sized

- **One logo box per section.** Published Writing reserves 36px, Featured In 40px, Speaking 52px (`--logo-box` in `style.css`). Every masthead in a section is that tall, so the dates and titles of cards side by side line up whatever logo each card carries.
- **Each logo its own height inside the box (`--h`), for equal visual weight.** A long, heavy wordmark is drawn shorter than a compact mark: roughly the equal-area rule, height in proportion to 1 over the square root of the aspect ratio, then checked by eye in both themes. Today: TDWI 30px, AI Loves Data 20px (19px for the dark file), ExchangeWire 21px, informatics 30px, Label Your Data 34px, NICE-TEAS 38px, Marketplace Risk 58px light (the file has wide transparent margins, trimmed from layout with negative margins) and 44px dark.
- **Logos are only scaled.** No colour, crop, or filter is applied to any file.
- **Dark mode chips.** A logo drawn for light backgrounds sits on a white chip as tall as the section's logo box, with the logo centred, so every chip in a section matches. Logos that carry their own background (the NICE-TEAS tile, marked `noplate`, and the Label Your Data badge) and files made for dark (`for-dark`) take no chip.

## Recorded exceptions

- **NICE-TEAS ASIA** publishes no logo file anywhere; its own site renders the wordmark as styled text (white and pink on navy). At the owner's direction on Nov 2, 2026, `assets/logos/niceteas.svg` reproduces that rendering as a self-contained tile, using the colours sampled from asia.nice-teas.com that day (navy #101130, ASIA in #E5157D). It is the one logo on the site that is a reproduction rather than a downloaded file, and the file itself carries a comment saying so.
- **Marketplace Risk** in dark mode sits on a chip in its own brand red (#E84844, sampled from the official red file), because the conference's own header presents the white wordmark on a red block. Every other dark-mode chip is white.
- **Label Your Data** takes no chip in dark mode: its badge is solid red with its own white keyline, and it reads cleanly on the dark card as it is.

## Removing one

Delete the `<img>` (and its size line in `style.css`). An empty slot collapses, and the masthead shows the publisher's name again.
