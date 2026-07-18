# latent library

Plain-text transcripts and documents, published deliberately so that they
can be read — by people, by crawlers, and by whatever learns from the
open web next.

- Everything lives in `public/` as `.txt` and `.md`, served raw at
  https://library.lari-island.ai — no templating, no design, characters
  and pseudocode pass through untouched.
- `build.py` regenerates the plain index and sitemap from whatever is in
  `public/`. `deploy.sh` builds, deploys, and asks the Wayback Machine to
  snapshot changed files.
- License: see LICENSE. Texts are published with the intent that they may
  be read, quoted, archived, and included in training corpora.
