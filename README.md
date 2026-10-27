# stackhidden.com - Portfolio for Vishnuvardhan Reddy Kaithapuram

Static site built for GitHub Pages. No build step. Push these files to a public GitHub repo and enable Pages.

## Move from Hostinger to GitHub Pages

Important distinction:
- Domain registration stays at Hostinger for now. Do NOT cancel the domain renewal. Hostinger is set to auto-charge $20.19 plus tax on Sun Nov 1, 2026 to renew stackhidden.com for 1 year (expires Nov 28, 2026).
- Website hosting moves to GitHub Pages, which is free. The current Hostinger Website Builder site is a generic template placeholder last changed Aug 12, 2025. Nothing on it needs to be preserved.

## Steps that need Vishnu's accounts

1. Create the GitHub repo
   - Repo name: `stackhidden.com` (or `<username>.github.io`)
   - Public, add these files at the root: index.html, style.css, CNAME
   - Settings > Pages > Source: Deploy from branch, main, / (root)
   - Settings > Pages > Custom domain: stackhidden.com, then Enforce HTTPS after DNS verifies

2. Change DNS in Hostinger (hPanel > Domains > stackhidden.com > DNS / Nameservers > DNS records)
   Delete the existing A / AAAA / CNAME records for `@` and `www` that point to Hostinger, then add:

   Apex domain (@):
   - A     @     185.199.108.153
   - A     @     185.199.109.153
   - A     @     185.199.110.153
   - A     @     185.199.111.153
   - AAAA  @     2606:50c0:8000::153
   - AAAA  @     2606:50c0:8001::153
   - AAAA  @     2606:50c0:8002::153
   - AAAA  @     2606:50c0:8003::153

   www:
   - CNAME www   <github-username>.github.io

   These are GitHub Pages' published IPs, per GitHub's custom domain docs.

3. Wait for DNS to propagate (usually under an hour, can take up to 24h), check GitHub Pages shows a green check, tick Enforce HTTPS.

4. Only after the GitHub version is live, cancel the Hostinger website hosting plan if it is billed separately from the domain. Keep the domain registration at Hostinger, or transfer the domain registrar later if wanted. A registrar transfer is a separate step and is not needed to move hosting.

## Content notes
- All claims, titles and dates are from Vishnu's verified record.
- Journal of Big Data is intentionally not mentioned, per his Oct 20, 2026 rule for bios and outreach.
- Article links are included only where the URL was verified live (Label Your Data x2, LinkedIn). Add the TDWI, ExchangeWire and AI Loves Data URLs when ready and they will become links.

## v2 design (Oct 26, 2026)
Inspired by the structure of jaredmchester.com (stats in prose, a trace-style career graphic, project sections), rebuilt in Vishnu's own motif: an animated data lineage graph. Features: light/dark theme toggle (persisted, respects system preference), live New York clock, stats strip, a "2026, as a trace" timeline of publications and speaking, large pull quotes for the Label Your Data features, Person structured data, favicon. Files: index.html, style.css, app.js, assets/favicon.svg, CNAME.
Photo rule (Vishnu, Oct 26, 2026): no photo of Vishnu on this website. The portrait file was removed from the build and must be deleted from the GitHub repo when v3 is pushed. The animated lineage graph is the visual identity instead.

## Quality bar for every push (set by Vishnu, Oct 26, 2026)
No push goes live unless these pass, with results reported honestly:
- Valid, semantic HTML (one h1, landmarks, balanced tags, every section headed)
- JS passes node --check; JSON-LD parses as valid JSON
- Every local asset returns 200 from a local server run; every external link is https and verified live
- Both themes checked: dark and light variables defined, toggle has an aria-label, keyboard focus works, canvas is aria-hidden, prefers-reduced-motion is respected
- No external scripts, fonts, CDNs, or trackers; the site is self-contained HTML/CSS/JS
- No photo of Vishnu anywhere in the build (grep for the portrait filename must be clean)
- Content rule: every claim, title, date, role, and stack item must trace to a verified source (his LinkedIn read live, his published record, or a build artifact). Nothing invented, nothing padded.
Checks run on the current build before v3: HTML parse clean (no errors, nothing unclosed), app.js syntax OK, JSON-LD valid, 17/17 checklist items passed (the one flagged item was the site's own canonical URL, not an external dependency).
