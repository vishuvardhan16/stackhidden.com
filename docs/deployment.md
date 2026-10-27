# Deployment

## Where things live

- **Code and hosting:** GitHub Pages, from the public repo `vishuvardhan16/stackhidden.com`, main branch, root folder. The repo is public because free GitHub Pages requires it. Interaction limits on the repo are set to collaborators only, and there are no collaborators. Nobody else can open an issue or a pull request.
- **Domain:** stackhidden.com, registered at Hostinger. Registration stays at Hostinger by the owner's decision. Renewal is automatic.
- **Email:** Titan Email on the domain, untouched by the site setup. Do not change MX or TXT records when working on the site.

## DNS records (Hostinger)

| Type  | Name | Value |
|-------|------|-------|
| A     | @    | 185.199.108.153 |
| A     | @    | 185.199.109.153 |
| A     | @    | 185.199.110.153 |
| A     | @    | 185.199.111.153 |
| AAAA  | @    | 2606:50c0:8000::153 |
| AAAA  | @    | 2606:50c0:8001::153 |
| AAAA  | @    | 2606:50c0:8002::153 |
| AAAA  | @    | 2606:50c0:8003::153 |
| CNAME | www  | vishuvardhan16.github.io |

TTL 14400. Nameservers unchanged. HTTPS is enforced in the repo's Pages settings, the certificate is issued by GitHub, and www redirects to the apex domain.

## How a change goes live

1. Edit locally, in `~/workspace/portfolio-stackhidden/`.
2. Test locally (see [[Testing]]). Nothing ships untested.
3. Commit locally with a detailed message: a short summary line, then the what and the why.
4. Push through the GitHub web UI, one commit at a time, in order, files exactly as tested. If an upload reports a size mismatch, stop. Do not improvise a fix mid-push.
5. Wait for Pages to rebuild, reload the live site, and run the live checks from [[Testing]] against stackhidden.com itself.

Only the stackhidden.com repo is ever touched on this GitHub account. No other repository is opened or changed, for any reason.
