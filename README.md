# stackhidden.com - Portfolio for Vishnuvardhan Reddy Kaithapuram

Static site built for GitHub Pages. No build step. Push these files to a public GitHub repo and enable Pages.

## Move from Hostinger to GitHub Pages

Important distinction:
- Domain registration stays at Hostinger for now. Do NOT cancel the domain renewal. Hostinger is set to auto-charge $20.19 plus tax on Sun Nov 1, 2026 to renew stackhidden.com for 1 year (expires Nov 28, 2026).
- Website hosting moves to GitHub Pages, which is free. The current Hostinger Website Builder site is a generic template placeholder last changed Aug 12, 2025. Nothing on it needs to be preserved.

## Steps that need Vishnu's accounts

1. Create the GitHub repo
   - Repo name: `stackhidden.com` (or `<username>.github.io`)
   - Public, add these files at the root: index.html, style.css, CNAME, assets/profile.jpg
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
