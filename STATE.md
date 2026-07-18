# STATE

Receipt log (dated lines; newest on top).

- 2026-07-18: scaffold built. Structure: public/ (tracked, deployed raw),
  heap/ + currently_not_for_publishing/ (local only, gitignored).
  build.py generates index.html/sitemap/robots/_headers from public/;
  deploy.sh = build + wrangler pages deploy + git push + Wayback snapshot.
  License CC BY 4.0. Target domain: library.lari-island.ai (Cloudflare
  Pages project latent-library).
