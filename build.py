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

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from generator.content import LANGS, PAGES
from generator.partials import Ctx
from generator.pages import BUILDERS

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


def render():
    pages = 0
    for lang in LANGS:
        ctx = Ctx(lang, DIST)
        for builder in BUILDERS:
            builder(ctx)
            pages += 1
    return pages


def write_sitemap():
    """A sitemap listing both languages, with hreflang alternates."""
    from generator.content import SITE_URL, DEFAULT_LANG

    today = time.strftime("%Y-%m-%d")
    urls = []
    for page in PAGES:
        leaf = "" if page == "index.html" else page
        alts = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{l}" '
            f'href="{SITE_URL}{"/" if l == DEFAULT_LANG else "/" + l + "/"}{leaf}"/>'
            for l in LANGS)
        for lang in LANGS:
            loc = f'{SITE_URL}{"/" if lang == DEFAULT_LANG else "/" + lang + "/"}{leaf}'
            urls.append(
                f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today}</lastmod>'
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
    clean()
    assets = copy_static()
    pages = render()
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
