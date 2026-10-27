# How the Site Works

## Files

- `index.html` — all the content and structure, plus the small script in the head that sets the theme before first paint so the page never flashes the wrong colors.
- `style.css` — every style, both themes, the print stylesheet, and the reduced-motion rules.
- `app.js` — all behavior: the background graph, the theme toggle, the case files, the command palette, the lineage explorer, the quote carousel, the animated core, and the cursor bot.
- `assets/` — the two quote screenshots, the favicon, and the original still versions of the lineage core artwork.
- `LICENSE` — MIT, for the code. The words on the page are not part of the license.

## Themes

Two themes, dark and light, driven by CSS variables on the root element. The visitor's choice is stored locally in the browser. Nothing about the visit is sent anywhere. The animated pieces read their colors from the same variables, so a theme switch recolors everything at once, including the artwork and the bot.

## Layout

The page column is 1280px wide. The hero is two columns on a desktop: the story on the left, and an At a glance panel on the right with role, team, base, focus, four headline numbers, and contact links. Under 920px everything stacks into one column. A faint graph-paper grid sits behind the hero, a nod to the lineage work.

## The pieces a visitor can touch

- **Case files.** Four projects written up the same way each time: the situation, the decisions, and the impact in numbers. They open in place, and each one has a deep link, so `#case=icm` opens the custom brands file directly.
- **Command palette.** Ctrl or Cmd + K. Jumps to sections and case files, toggles the theme, copies nothing and prints nothing, because the owner removed those actions. It is a navigation tool, nothing more.
- **Lineage explorer.** An SVG diagram of the systems he works on. Hover or tap a stage and the edges light up to show what feeds it and what it feeds. Small packets travel the lit edges.
- **Background graph.** A canvas behind the page draws a slow lineage graph. It is decoration with a subject: nodes and edges, the shape of the work.
- **Quote carousel.** Screenshots of the two Label Your Data articles that quoted him, with the avatars cropped out on purpose (see [[Content Rules]] on the no-photo rule). The captions link to the articles.
- **Print.** The print stylesheet strips the decoration and interactive pieces and lays the page out as a clean document.

## Motion rules

The site respects reduced motion everywhere. The visitor can switch it off from the footer, and the operating system setting is honored too. Under reduced motion the background stops, the animated core draws one still frame, the bot closes its eyes, and nothing on the page moves.
