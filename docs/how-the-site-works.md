# How the Site Works

## Files

- `index.html`: all the content and structure, plus the small script in the head that sets the theme, and a stored Reduce motion choice, before first paint, so the page never flashes the wrong colors or the first frames of an animation.
- `404.html`: the page GitHub Pages serves, with status 404, for an address with no file. It is self-contained, with inline styles and absolute URLs, because Pages serves it at whatever depth was asked for.
- `robots.txt` and `sitemap.xml`: every crawler may read everything; the sitemap lists the one canonical URL.
- `style.css`: every style, both themes, the print stylesheet, and the reduced-motion rules.
- `app.js`: all behavior: the background graph, the theme toggle, the case files, the command palette, the lineage explorer and its send-a-record buttons, the quote carousel, the animated core, the cursor bot, the query console, and the first-view reveals.
- `assets/`: the six quote images (lossless WebP; the four quote cards come from `scripts/render-quote-card.py`), the favicon and the home-screen icon rendered from it, the hero figure and its video, the share card, the original still versions of the lineage core artwork, and the publisher logos in `assets/logos/`.
- `LICENSE`: MIT, for the code. The words on the page are not part of the license.

## Themes

Two themes, dark and light, driven by CSS variables on the root element. The visitor's choice is stored locally in the browser. Nothing about the visit is sent anywhere. The animated pieces read their colors from the same variables, so a theme switch recolors everything at once, including the artwork and the bot.

## Layout

The page column is 1280px wide. The hero is two columns on a desktop: the story on the left, and an At a glance panel on the right with role, team, base, focus, four headline numbers, and contact links. Under 920px everything stacks into one column. Under 640px the header keeps the brand and the two buttons on one row and puts the section links in a single row below that scrolls sideways. A faint graph-paper grid sits behind the hero, a nod to the lineage work. Every in-page jump stops 12px below the sticky header, at any width: `scroll-padding-top` follows the header's real height, which app.js keeps in a custom property.

## The pieces a visitor can touch

- **Career, as a trace.** The top of Experience: every role since 2019, and the graduate degree, as a span on a year axis that ends at today. app.js places each bar from its start and end months, so nothing needs editing as time passes. Select a row, or move with the arrow keys, and the line under the chart gives its dates, its length (inclusive months, as LinkedIn counts them), its place, and a link to the full entry.
- **Case files.** Four projects written up the same way each time: the situation, the decisions, and the impact in numbers. They open in place, and each one has a deep link, so `#case=icm` opens the custom brands file directly.
- **Command palette.** Ctrl or Cmd + K. Jumps to sections and case files, toggles the theme, copies nothing and prints nothing, because the owner removed those actions. Type a SQL query into it and the first command runs that query in the console below.
- **Lineage explorer.** An SVG diagram of the systems he works on, which draws itself along the data flow the first time it scrolls into view. Hover or tap a stage and the edges light up to show what feeds it and what it feeds. Small packets travel the lit edges; the amber one is flagged traffic and ends in Flagged anomalies. Two buttons send a clean or a bad record through the pipeline: the bad one looks the same until the quality gate stops it, and a log under the graph records each stage. On phones the graph keeps a readable size and scrolls sideways.
- **Query this page.** A SQL console whose eight tables (writing, talks, featured, spans, roles, education, case_files, skills) are built from the page's own HTML when it loads, so they can never disagree with the page. Trace on a result row jumps to the element it came from. The query rides in the address bar as `#q=`, so a query is a link. See [[The Query Console]].
- **2026, as a trace.** Ten spans on a Jul 1 to Dec 1 axis, each bar ending on its date, with a notch at every month start. On first view the bars render in date order. Selecting a row shows that span's details.
- **Publisher mastheads.** Published Writing, Speaking, and the Featured In captions open with the publisher's name, a pill for the kind of piece, and the date. Each carries the publisher's official logo; see [[Publisher Logos]].
- **Background graph.** A canvas behind the page draws a slow lineage graph. It is decoration with a subject: nodes and edges, the shape of the work.
- **Quote carousel.** Screenshots of the two Label Your Data articles that quoted him, with the avatars cropped out on purpose (see [[Content Rules]] on the no-photo rule), and quote cards for the Informatics Magazine, CTO Sync, and Tech Magazine Q&As. The captions link to the articles. The carousel is as tall as its tallest slide, so captions never run under its controls. Its images load together once it comes within a screen of view, so no slide ever slides in blank.
- **The 404 page.** A mistyped or old address gets the site's own page: the path as a SQL query that finds 0 rows, a "Did you mean /?", and links back to each section.
- **Print.** The print stylesheet strips the decoration and interactive pieces and lays the page out as a clean document.

## Motion rules

The site respects reduced motion everywhere. The visitor can switch it off from the footer, and the operating system setting is honored too. Under reduced motion the background stops, the hero video is never downloaded, the animated core draws one still frame, the bot closes its eyes, the carousel holds its slide, the hero intro and the first-view reveals do not play, a sent record arrives without travelling, and nothing on the page moves. [[Motion]] lists every moving piece, and the rules for adding one.
