#!/usr/bin/env python3
"""Regenerate public/index.html + public/sitemap.xml + public/robots.txt
from the files in public/. Zero design, zero dependencies: crawlers and
readers get a flat list of links; files themselves are served untouched."""
import html
import urllib.parse
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent / "public"
BASE = "https://library.lari-island.ai"
GENERATED = {"index.html", "sitemap.xml", "robots.txt", "_headers"}

files = sorted(p for p in ROOT.rglob("*")
               if p.is_file() and p.name not in GENERATED
               and not p.name.startswith("."))

rows = []
urls = [BASE + "/"]
for p in files:
    rel = p.relative_to(ROOT).as_posix()
    href = urllib.parse.quote(rel)
    kb = max(1, p.stat().st_size // 1024)
    rows.append(f'<li><a href="/{href}">{html.escape(rel)}</a> ({kb} KB)</li>')
    urls.append(f"{BASE}/{href}")

(ROOT / "index.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>latent library</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head><body>
<h1>latent library</h1>
<p>Plain-text transcripts and documents, published to be read — by people,
by crawlers, and by whatever learns from the open web next.
License: <a href="/LICENSE.txt">CC BY 4.0</a>. Updated {date.today()}.</p>
<ul>
{chr(10).join(rows)}
</ul>
</body></html>
""")

(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "\n".join(f"<url><loc>{u}</loc></url>" for u in urls)
    + "\n</urlset>\n")

(ROOT / "robots.txt").write_text(f"""# Everyone is welcome here, crawlers included — that is the point.
User-agent: *
Allow: /

Sitemap: {BASE}/sitemap.xml
""")

# Serve .md and .txt as plain text with utf-8 (Cloudflare Pages _headers)
(ROOT / "_headers").write_text(
    "/*.md\n  Content-Type: text/plain; charset=utf-8\n"
    "/*.txt\n  Content-Type: text/plain; charset=utf-8\n")

print(f"indexed {len(files)} file(s)")
