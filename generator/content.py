# -*- coding: utf-8 -*-
"""Loads the CMS content files and exposes them to the templates.

Every file under content/ is JSON with top-level locale keys, matching
Sveltia CMS's `single_file` i18n structure:

    { "es": { ...Spanish fields... }, "en": { ...English fields... } }

Fields that are not translatable (slugs, years, image paths) are written by
the CMS into the default locale only, so `shared()` always reads from there.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")

SITE_URL = "https://webdesignerpr.com"
LANGS = ("es", "en")
DEFAULT_LANG = "es"
PAGES = ["index.html", "about.html", "services.html", "portfolio.html", "deals.html", "contact.html", "articles.html"]


def _read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load(name):
    """Load content/<name>.json."""
    return _read(os.path.join(CONTENT, name + ".json"))


def load_projects():
    """Every file in content/projects/, ordered by the `order` field.

    Adding a project in the CMS creates a new file here; nothing else needs
    to change for it to appear on the site.
    """
    folder = os.path.join(CONTENT, "projects")
    if not os.path.isdir(folder):
        return []

    items = []
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".json"):
            continue
        doc = _read(os.path.join(folder, filename))
        items.append(doc)

    items.sort(key=lambda d: d.get(DEFAULT_LANG, {}).get("order", 999))
    return items


def shared(doc, key, default=None):
    """Read a non-translatable field — always stored with the default locale."""
    return doc.get(DEFAULT_LANG, {}).get(key, default)


def texts(items, key="text"):
    """Unwrap a CMS list-of-objects into a plain list of strings.

    The CMS stores repeatable strings as [{"text": "…"}] because its list
    widget needs a named field; templates just want the strings.
    """
    out = []
    for item in items or []:
        if isinstance(item, dict):
            out.append(item.get(key, ""))
        else:
            out.append(item)
    return out
