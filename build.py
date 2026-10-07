#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WebDesignerPR — static site build.

    python3 build.py            build into dist/
    python3 build.py --serve    build, then serve dist/ on http://localhost:4173

Reads every string and image path from content/ (edited via Sveltia CMS at
/admin/) and writes the finished HTML into dist/, alongside the static assets.

Standard library only. No npm, no pip, no lockfile — `python3 build.py` is the
entire toolchain, which is also the Cloudflare Pages build command.
"""
import os
import shutil
import sys
import time
import json
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from generator.content import LANGS, PAGES
from generator.partials import Ctx
from generator.pages import BUILDERS, render_404

DIST = os.path.join(ROOT, "dist")

# Copied verbatim into dist/. `admin` carries the CMS, which must be served
# from the site itself for the GitHub OAuth redirect to land correctly.
STATIC_DIRS = ["css", "js", "images", "fonts", "admin"]
STATIC_FILES = ["robots.txt", "_headers", "_redirects", "favicon.ico"]


def clean():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)


def copy_static():
    copied = 0
    for name in STATIC_DIRS:
        src = os.path.join(ROOT, name)
        if not os.path.isdir(src):
            continue
        shutil.copytree(src, os.path.join(DIST, name))
        copied += sum(len(f) for _, _, f in os.walk(src))
    for name in STATIC_FILES:
        src = os.path.join(ROOT, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(DIST, name))
            copied += 1
    return copied


def ensure_article_excerpts():
    """Auto-generate excerpts for articles missing them (from Zao Flo sync)."""
    articles_file = os.path.join(ROOT, "content", "articles.json")
    if not os.path.isfile(articles_file):
        return

    def extract_first_paragraph(html):
        if not html:
            return ""
        match = re.search(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
        if match:
            text = match.group(1)
            text = re.sub(r'<[^>]+>', '', text)
            if len(text) > 150:
                text = text[:150] + "..."
            return text.strip()
        return ""

    with open(articles_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated = False
    for lang in list(data.keys()):
        if 'articles' in data[lang]:
            for article in data[lang]['articles']:
                if not article.get('excerpt') and article.get('body'):
                    article['excerpt'] = extract_first_paragraph(article['body'])
                    updated = True

    if updated:
        with open(articles_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def render():
    pages = 0
    for lang in LANGS:
        ctx = Ctx(lang, DIST)
        for builder in BUILDERS:
            builder(ctx)
            pages += 1
        # Build individual article pages
        from generator.pages import build_article_pages
        build_article_pages(ctx)
        # Count article pages (will be counted in the next loop when they actually exist)
    return pages


def write_404():
    """One 404 for the whole site — Cloudflare serves it for any unmatched path."""
    with open(os.path.join(DIST, "404.html"), "w", encoding="utf-8") as f:
        f.write(render_404())


def write_sitemap():
    """A sitemap listing both languages, with hreflang alternates."""
    from generator.content import LANGS, load, page_url

    today = time.strftime("%Y-%m-%d")
    pages = list(PAGES)
    # One landing page per service and per industry — the mega menu targets
    for section in ("services", "industries"):
        pages += [f"{section}/{x['id']}.html"
                  for x in load(section).get("es", {}).get("items", []) if x.get("id")]

    urls = []
    for page in pages:
        alts = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{page_url(page, l)}"/>'
            for l in LANGS)
        alts += (f'\n    <xhtml:link rel="alternate" hreflang="x-default" '
                 f'href="{page_url(page, LANGS[0])}"/>')
        for lang in LANGS:
            urls.append(
                f'  <url>\n    <loc>{page_url(page, lang)}</loc>\n    <lastmod>{today}</lastmod>'
                f'{alts}\n  </url>')

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + "\n".join(urls) + "\n</urlset>\n")
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def write_robots():
    from generator.content import SITE_URL
    path = os.path.join(DIST, "robots.txt")
    if os.path.exists(path):
        return  # a checked-in robots.txt wins
    with open(path, "w", encoding="utf-8") as f:
        f.write("User-agent: *\n"
                "Allow: /\n"
                "Disallow: /admin/\n\n"
                f"Sitemap: {SITE_URL}/sitemap.xml\n")


def main():
    start = time.time()
    ensure_article_excerpts()  # Auto-generate missing excerpts for Zao Flo articles
    clean()
    assets = copy_static()
    pages = render()
    write_404()
    write_sitemap()
    write_robots()
    print(f"built {pages} pages + {assets} assets -> dist/  ({time.time() - start:.2f}s)")


if __name__ == "__main__":
    main()
    if "--serve" in sys.argv:
        import functools, http.server, socketserver

        PORT = 4173

        class Handler(http.server.SimpleHTTPRequestHandler):
            def end_headers(self):
                self.send_header("Cache-Control", "no-store")
                super().end_headers()

        class Server(socketserver.ThreadingTCPServer):
            allow_reuse_address = True
            daemon_threads = True

        handler = functools.partial(Handler, directory=DIST)
        with Server(("127.0.0.1", PORT), handler) as httpd:
            print(f"serving dist/ on http://localhost:{PORT}  (ctrl-c to stop)")
            httpd.serve_forever()
