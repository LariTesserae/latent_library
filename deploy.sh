#!/bin/bash
# Build, deploy to Cloudflare Pages, push to GitHub, ask Wayback to snapshot.
set -e
cd "$(dirname "$0")"
cp LICENSE public/LICENSE.txt
python3 build.py
npx wrangler pages deploy public --project-name latent-library --commit-dirty=true
git add -A && git commit -m "update library" 2>/dev/null || true
git push origin main 2>/dev/null || git push -u origin main
# Wayback: snapshot index (it discovers files via links/sitemap)
curl -s "https://web.archive.org/save/https://library.lari-island.ai/" -o /dev/null &&
  echo "wayback snapshot requested" || echo "wayback request failed (non-fatal)"
