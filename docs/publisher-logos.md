# Publisher Logos

Published Writing, Speaking, and the Featured In captions open with a publisher masthead: the publisher's logo (or its name in the site's own type), a pill for the kind of piece, then the date. Every publisher on the page now has its logo in place (added by the owner on Nov 2, 2026).

## Where logos come from

A publisher's logo is its trademark. Logos go in as official files the owner downloads from the publisher, used the way the publisher's guidelines allow; the one exception is recorded below. A masthead without a logo shows the publisher's name in the site's own type and stands on its own.

## Getting an official file

1. Look for the publisher's media kit, press kit, or brand page. Most publishers have one, often linked from the site footer or an "About" or "Press" page.
2. Read its usage guidelines: clear space, colours, and whether a contributor or speaker may show the logo.
3. If there is no kit, or the guidelines are unclear, ask your editor or event contact before using the logo.
4. Prefer SVG. For PNG, use a file two to three times the height it will be shown at (see the sizes below): enough to stay sharp on high-density screens, and no heavier. `test_static` fails for a PNG more than about three times its shown height, or any logo file over 24 KB.

## Adding one

1. Save the file as `assets/logos/<slug>.svg` (or `.png`):

   | Publisher | Slug | Appears in |
   | --- | --- | --- |
   | TDWI Upside | `tdwi` | Published Writing |
   | AI Loves Data | `ailovesdata` | Published Writing |
   | ExchangeWire | `exchangewire` | Published Writing |
   | eSecurity Planet | `esecurityplanet` | Published Writing |
   | Foojay | `foojay` | Published Writing |
   | CRM Magazine | `crmmagazine` | Published Writing |
   | Platform Engineering | `platformengineering` | Published Writing |
   | Marketplace Risk | `marketplacerisk` | Speaking |
   | NICE-TEAS ASIA | `niceteas` | Speaking |
   | Label Your Data | `labelyourdata` | Featured In (three slides) |
   | Informatics Magazine | `informatics` | Featured In (eight slides) |
   | CTO Sync | `ctosync` | Featured In (seven slides) |
   | Tech Magazine | `techmagazine` | Featured In (seven slides) |
   | CIO Grid | `ciogrid` | Featured In (nine slides) |
   | AZ Big Media | `azbigmedia` | Featured In |
   | PRAPI | `prapi` | Featured In |
   | Interview Focus | `interviewfocus` | Featured In (two slides) |
   | Block Telegraph | `blocktelegraph` | Featured In (two slides) |
   | Transit Tomorrow | `transittomorrow` | Featured In (two slides) |
   | Grit Daily | `gritdaily` | Featured In |
   | Smartech Daily | `smartechdaily` | Featured In |
   | Customer Relations | `customerrelations` | Featured In (two slides) |

   CTO Sync's logo file is present: `assets/logos/ctosync.svg` is the official file from ctosync.com's site header (black wordmark with a green accent, 175x40 native), added Nov 3, 2026, and its Featured In caption shows it. Do not draw or reproduce one; NICE-TEAS ASIA, below, is the only reproduction on the site. The file carries wide empty canvas either side of its mark, so `style.css` frames it to its artwork; see the exceptions below.

   Tech Magazine's logo file is present: `assets/logos/techmagazine.png` carries the publisher's official header artwork (600x125 native), added Nov 4, 2026, and its Featured In caption shows it. The header file itself is an SVG export of roughly 1 MB carrying an embedded raster image, so the caption uses a transparent PNG rendered from that official file. It was first committed at 1200x250 (72 KB), about nine times its shown height; on Nov 4, 2026 it was scaled to 403x84 (19 KB), three times its shown height, per the PNG route above. The artwork is otherwise unchanged.

2. In `index.html`, put the `<img class="pub-logo">` in that publisher's `<span class="pub-mark">`. Set its `width` and `height` attributes to the file's real shape at its display height (for example `width="148" height="21"` for a 7:1 logo shown 21px tall), so the page does not shift while the image loads. Add `loading="lazy" decoding="async"` too: every image on the page is below the fold, and `test_static` fails for one without them.
3. Keep `alt=""`. The publisher's name stays in the page for screen readers, and is hidden only visually once a logo is present. A descriptive alt would make screen readers say the name twice.
4. Give the logo its size: one line in `style.css`, in the "Logo sizing" table, such as `.pub-logo[src$="/tdwi.svg"]{--h:30px}`. See "How logos are sized" below for choosing the number. `test_publishers` fails for any visible logo without one.
5. Run `scripts/run-tests.sh`. `test_publishers` checks that every logo loads and has its size, that cards side by side still line up, that dark-mode chips match, and that no pill overflows its card at 360px. A wrong path fails the suite with a "Failed to load resource" error. Logos load lazily, so the hidden file of a light and dark pair is fetched only when its theme is shown.
6. Look at the card in both themes, on desktop and at 360px.
7. If the publisher supplies a version made for dark backgrounds, save it as `assets/logos/<slug>-dark.svg` and put both images in the slot, each with its own size line. Each theme then shows its own file, with no chip:

   ```html
   <img class="pub-logo for-light" src="assets/logos/ailovesdata.png" alt="" width="118" height="20" loading="lazy" decoding="async">
   <img class="pub-logo for-dark" src="assets/logos/ailovesdata-dark.svg" alt="" width="133" height="19" loading="lazy" decoding="async">
   ```

## How logos are sized

- **One logo box per section.** Published Writing reserves 36px, Featured In 40px, Speaking 52px (`--logo-box` in `style.css`). Every masthead in a section is that tall, so the dates and titles of cards side by side line up whatever logo each card carries.
- **Each logo its own height inside the box (`--h`), for equal visual weight.** A long, heavy wordmark is drawn shorter than a compact mark: roughly the equal-area rule, height in proportion to 1 over the square root of the aspect ratio, then checked by eye in both themes. Today: TDWI 30px, AI Loves Data 20px (19px for the dark file), ExchangeWire 21px, eSecurity Planet 27px, Foojay 33px (a compact mark), informatics 30px, CTO Sync 34px (a compact mark), Tech Magazine 28px, Label Your Data 34px, NICE-TEAS 38px, Marketplace Risk 58px light (the file has wide transparent margins, trimmed from layout with negative margins) and 44px dark, CIO Grid 30px, AZ Big Media 27px, PRAPI 36px (a compact mark), Interview Focus 22px, Block Telegraph 31px, Transit Tomorrow 28px, Grit Daily 35px, Smartech Daily 32px, Customer Relations 28px.
- **Logos are only scaled.** No colour, crop, or filter is applied to any file. The one exception to the file's own framing is Smartech Daily, below: its transparent margin was trimmed, not its artwork.
- **Dark mode chips.** A logo drawn for light backgrounds sits on a white chip as tall as the section's logo box, with the logo centred, so every chip in a section matches. Logos that carry their own background (the NICE-TEAS tile, marked `noplate`, and the Label Your Data badge) and files made for dark (`for-dark`) take no chip. **Dark plates:** a logo drawn in white or light colours sits on a dark plate (`class="darkplate"`, slate #0f172a, the full logo-box height) in both themes, because it is invisible on a light page and on the white chip. CIO Grid and Block Telegraph take the dark plate.

## Recorded exceptions

- **NICE-TEAS ASIA** publishes no logo file anywhere; its own site renders the wordmark as styled text (white and pink on navy). At the owner's direction on Nov 2, 2026, `assets/logos/niceteas.svg` reproduces that rendering as a self-contained tile, using the colours sampled from asia.nice-teas.com that day (navy #101130, ASIA in #E5157D). It is the one logo on the site that is a reproduction rather than a downloaded file, and the file itself carries a comment saying so.
- **Marketplace Risk** in dark mode sits on a chip in its own brand red (#E84844, sampled from the official red file), because the conference's own header presents the white wordmark on a red block. Every other dark-mode chip is white.
- **Label Your Data** takes no chip in dark mode: its badge is solid red with its own white keyline, and it reads cleanly on the dark card as it is.
- **Foojay** takes no chip in dark mode: its sky-blue letters with a white outline read cleanly on the dark card as they are. Its file is the official header file from foojay.io, scaled Nov 20, 2026 from 1022x352 (65 KB) to 260x90 (23 KB), about 2.7 times its shown height, per the PNG route above; the artwork is otherwise unchanged.
- **eSecurity Planet**'s file is the official header PNG from esecurityplanet.com (300x70 native, 17 KB), added Nov 20, 2026; it is drawn for light backgrounds, so in dark mode it sits on the usual white chip.
- **CRM Magazine**'s file is the official desktop header SVG from destinationcrm.com (`logo_desktop.svg`, 235x137, 17 KB), added Nov 20, 2026. It is the full stacked lockup (destination / CRM / FROM THE EDITORS OF CRM MAGAZINE), shown at the full 36px logo-box height; drawn for light backgrounds, so in dark mode it sits on the usual white chip.
- **Platform Engineering** has no clean wordmark: its only wordmark file carries a "Founding Sponsor Checkmarx" line, so that file is not used. The masthead instead carries the site's official diamond mark (`favicon-32x32-1.png` from platformengineering.com, 32x32, 2 KB), shown at 28px beside the publisher name in type — a mark-only logo (class `.mark`) never hides the name, because the mark alone does not name the publisher. Do not use the sponsored file, and do not crop it — logos are only scaled.
- **CTO Sync**'s official file has empty canvas around its mark: 31% of its width on the left and 27% on the right. Shown as is, the mark sat about 40px in from the caption under it. `style.css` shows it in a 2:1 box with `object-fit: cover`, centred on the artwork, so the mark starts at the caption's edge and the dark chip fits it. The file itself is untouched. `test_publishers` checks, for every logo, that its artwork starts within 4px of its box's left edge.
- **CIO Grid**'s file is the official SVG from the publisher's featured-image host (525x120, 23 KB), added Nov 20, 2026. Its wordmark text is white, so it takes the dark plate (class `darkplate`) in both themes; the green accent (#00faa8) reads on the slate plate.
- **Block Telegraph**'s file is the official SVG from blocktelegraph.io's uploads (`BT-Logo.svg_.txt` — the `.txt` suffix is WordPress's storage quirk; the content is valid SVG, saved as `.svg`), added Nov 20, 2026. Its letters are light blue (#73d0ee) with white icon details, so it takes the dark plate in both themes.
- **AZ Big Media**'s file is the official PNG from azbigmedia.com's uploads (1600x306, 35 KB), added Nov 20, 2026, scaled to 423x81 (18 KB), three times its shown height, per the PNG route above; the artwork is otherwise unchanged.
- **Interview Focus**'s file is the official PNG from interviewfocus.com's uploads (1000x128, 82 KB), added Nov 20, 2026, scaled to 516x66 and saved as a 256-colour palette PNG (12 KB), three times its shown height, per the PNG route above; the artwork is otherwise unchanged.
- **Transit Tomorrow**'s file is the official PNG from transittomorrow.com's uploads (327x82, 9 KB), added Nov 20, 2026. The file carries 9px of transparent canvas on its left, which read as 5px at display size, outside the 4px pin; the transparent margin was trimmed (content 305x65), then the file was scaled to 394x84 and saved as a 256-colour palette PNG (12 KB), three times its shown height of 28px. No artwork was removed.
- **Grit Daily**'s file is the official PNG from gritdaily.com's uploads (600x189, 6 KB), added Nov 20, 2026, scaled to 333x105 (22 KB), three times its shown height, per the PNG route above; the artwork is otherwise unchanged. Its tagline ("The Premier Startup News Hub.") is baked into the image and reads tiny at masthead size; logos are never cropped, so it stays.
- **Smartech Daily**'s file is the official PNG from smartechdaily.com's uploads (450x100, 10 KB), added Nov 20, 2026. The file carries 42px of transparent canvas on its left, which would have put its artwork 12px in at display size, outside the 4px pin; the transparent margin was trimmed (content 363x89), then the file was scaled to 393x96 (23 KB), three times its shown height of 32px. No artwork was removed.
- **PRAPI**'s file is the official SVG from prapi.dev's brand page (`prapi-logo-mark.svg`, 696 bytes), added Nov 20, 2026. It is the full "prapi.dev" wordmark in near-black (#0F0F0F), so it takes the usual white chip in dark mode.
- **Customer Relations**' file is the official SVG from the publisher's featured-image host (525x120, 16 KB), added Nov 26, 2026. It is the full wordmark in black (#000000) with a mint-green mark (#4ffbce), so it takes the usual white chip in dark mode.

## Removing one

Delete the `<img>` (and its size line in `style.css`). An empty slot collapses, and the masthead shows the publisher's name again.
