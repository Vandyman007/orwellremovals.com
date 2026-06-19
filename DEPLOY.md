# Deploying Orwell Removals & Storage

Static site (HTML + Tailwind CSS) with one Cloudflare Pages Function for the enquiry form.

## Build

```bash
python3 tools/build.py     # renders all HTML + sitemap.xml + llms.txt
npm run build:css          # compiles css/site.min.css from Tailwind
python3 tools/audit.py     # must print: RESULT: PASS
```

Commit the generated output (HTML, `css/site.min.css`, `sitemap.xml`, `llms.txt`).

## Recommended host: Cloudflare Pages

Chosen because the site uses `functions/` (the form backend), `_headers` and `_redirects`,
which Cloudflare Pages supports natively. (GitHub Pages is static-only — it would serve the
pages but the `/api/quote` form would not work and `_headers` would be ignored.)

- **Custom domain:** add `orwellremovals.com` in the Pages project (the `CNAME`
  file is also present for GitHub Pages compatibility).
- **Build command:** none needed if you commit the built output; otherwise
  `python3 tools/build.py && npm run build:css`.
- **Output directory:** repository root.

## Form backend — environment variables

Set these in **Cloudflare Pages → Settings → Environment variables**:

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `RESEND_API_KEY` | **Yes** | — | Resend API key (server-side secret). |
| `QUOTE_TO` | No | `sales@orwellremovals.com` | Where enquiries are delivered. |
| `QUOTE_FROM` | No | `Orwell Removals Website <website@orwellremovals.com>` | Must be on a verified Resend domain. |

### Resend / DNS

1. Add and **verify `orwellremovals.com`** in Resend (add the SPF + DKIM DNS records it provides).
2. The form (`functions/api/quote.js`) emails the enquiry to `QUOTE_TO` with `reply-to` set to the
   customer's address, then 303-redirects the visitor to `/thank-you/`.
3. All three site forms (home quote band, `/get-a-quote/`, `/contact-us/`) post to `/api/quote`.

## Notes

- `robots.txt` points to `https://orwellremovals.com/sitemap.xml`.
- `_headers` sets a tight CSP (only `https://www.google.com` is allowed in frames, for the maps embeds).
- `/thank-you/` is `noindex` by design.
