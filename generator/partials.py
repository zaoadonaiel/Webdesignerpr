# -*- coding: utf-8 -*-
"""Shared chrome — head, header, drawer, CTA, footer — rendered per language."""
import os
from .content import SITE_URL, DEFAULT_LANG, load

ARROW = ('<svg class="btn__arrow" viewBox="0 0 16 16" fill="none" stroke="currentColor" '
         'stroke-width="1.5" aria-hidden="true"><path d="M4 12L12 4M12 4H5.5M12 4v6.5"/></svg>')
ARROW_R = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" '
           'aria-hidden="true"><path d="M2 8h12M9 3l5 5-5 5"/></svg>')
ARROW_UP = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" '
            'aria-hidden="true"><path d="M8 14V2M3 7l5-5 5 5"/></svg>')
STAR = ('<svg class="marquee__star" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="M12 0c.7 5 2 8.3 4 9.9 1.7 1.4 4.6 2 8 2.1-3.4.1-6.3.7-8 2.1-2 1.6-3.3 4.9-4 '
        '9.9-.7-5-2-8.3-4-9.9-1.7-1.4-4.6-2-8-2.1 3.4-.1 6.3-.7 8-2.1 2-1.6 3.3-4.9 4-9.9Z"/></svg>')
MARK_PATH = ('<path d="M16 0c.9 6.6 2.6 10.9 5.3 13.1C23.6 15 27.4 15.9 32 16c-4.6.1-8.4 1-10.7 '
             '2.9C18.6 21.1 16.9 25.4 16 32c-.9-6.6-2.6-10.9-5.3-13.1C8.4 17 4.6 16.1 0 16c4.6-.1 '
             '8.4-1 10.7-2.9C13.4 10.9 15.1 6.6 16 0Z" fill="currentColor"/>')


class Ctx:
    """Everything that varies by language: paths, URLs and the chrome strings."""

    def __init__(self, lang, out_root):
        self.lang = lang
        self.pre = "" if lang == DEFAULT_LANG else "../"
        self.out = out_root if lang == DEFAULT_LANG else os.path.join(out_root, lang)
        settings = load("settings")
        self.s = settings[lang]
        self.s_default = settings[DEFAULT_LANG]
        # Interface strings are grouped so the CMS can collapse them
        self.ui = self.s["interface"]

    # --- paths ---------------------------------------------------------
    def asset(self, path):
        """Relative path to a site asset from this language's folder."""
        return self.pre + path.lstrip("/")

    def media(self, path):
        """Media paths are stored absolute by the CMS ("/images/…"); the site
        uses relative links so it works from any subfolder."""
        if not path:
            return ""
        if path.startswith(("http://", "https://", "data:")):
            return path
        return self.pre + path.lstrip("/")

    def page_url(self, page, lang=None):
        lang = lang or self.lang
        leaf = "" if page == "index.html" else page
        return SITE_URL + ("/" if lang == DEFAULT_LANG else "/" + lang + "/") + leaf

    def other_href(self, page):
        return ("en/" + page) if self.lang == DEFAULT_LANG else ("../" + page)

    def write(self, page, html):
        os.makedirs(self.out, exist_ok=True)
        with open(os.path.join(self.out, page), "w", encoding="utf-8") as f:
            f.write(html)


# ---------------------------------------------------------------------------
# HEAD
# ---------------------------------------------------------------------------

# CMS field names cannot contain dots, so page metadata is keyed by a plain name
META_KEY = {"index.html": "home", "about.html": "about", "services.html": "services",
            "portfolio.html": "portfolio", "deals.html": "deals", "contact.html": "contact", "articles.html": "articles"}


def head(c, page):
    meta = c.s["meta"][META_KEY[page]]
    title, desc = meta["title"], meta["description"]
    es_url, en_url = c.page_url(page, "es"), c.page_url(page, "en")
    og_locale = "es_PR" if c.lang == "es" else "en_US"
    og_alt = "en_US" if c.lang == "es" else "es_PR"

    return f"""<!DOCTYPE html>
<html lang="{c.lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="google" content="notranslate">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{c.page_url(page)}">

  <!-- Both language versions of this page -->
  <link rel="alternate" hreflang="es" href="{es_url}">
  <link rel="alternate" hreflang="en" href="{en_url}">
  <link rel="alternate" hreflang="x-default" href="{es_url}">

  <!-- Matches whichever theme is active, so browser UI follows the page -->
  <meta name="theme-color" content="#faf7f1" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#08090b" media="(prefers-color-scheme: dark)">

  <!-- Open Graph / social -->
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Web Designer Puerto Rico">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{c.page_url(page)}">
  <meta property="og:image" content="{SITE_URL}/images/logo/og-image.jpg">
  <meta property="og:image:type" content="image/jpeg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="{og_locale}">
  <meta property="og:locale:alternate" content="{og_alt}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{SITE_URL}/images/logo/og-image.jpg">

  <link rel="icon" href="{c.asset('favicon.png')}" type="image/png">
  <link rel="apple-touch-icon" href="{c.asset('favicon.png')}">

  <!-- Typography -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&amp;family=Inter+Tight:ital,wght@0,300;0,400;0,500;0,600;1,400&amp;family=Google+Sans:wght@400;500&amp;display=swap">

  <link rel="stylesheet" href="{c.asset('css/style.css')}">
  <link rel="stylesheet" href="{c.asset('css/animations.css')}">
  <link rel="stylesheet" href="{c.asset('css/responsive.css')}">

  <!-- Applies the saved theme and marks the document script-capable BEFORE
       first paint, so a returning dark-mode visitor never sees a flash of
       light and pre-animation states apply cleanly. -->
  <script>(function(){{try{{if(localStorage.getItem("wdpr:theme")==="dark")
document.documentElement.setAttribute("data-theme","dark")}}catch(e){{}}
document.documentElement.classList.add("js-ready")}})();</script>
  <noscript><style>.loader{{display:none!important}}.js-ready [data-reveal]{{opacity:1!important;transform:none!important}}</style></noscript>
  <script src="https://app.zaochat.com/widget/widget.js?v=1788014309" data-client-code="130aa379-9729-46f6-879e-55871e187ca4" async></script>
</head>
<body>
  <a class="skip-link" href="#main">{c.ui['skip']}</a>
"""


# ---------------------------------------------------------------------------
# CHROME
# ---------------------------------------------------------------------------

def chrome(c):
    return f"""
  <!-- Preloader: shown once per session, removed from the DOM afterwards -->
  <div class="loader" role="status" aria-live="polite">
    <div class="loader__inner">
      <p class="loader__word">Web Designer <em>Puerto Rico</em></p>
      <div class="loader__bar"><i></i></div>
      <p class="loader__count">000</p>
    </div>
    <span class="visually-hidden">{c.ui['loading']}</span>
  </div>

  <div class="grain" aria-hidden="true"></div>
  <div class="scroll-progress" aria-hidden="true"></div>
  <div class="column-rules" aria-hidden="true"><span></span><span></span><span></span><span></span></div>

  <!-- Custom cursor: rendered only on fine-pointer, motion-tolerant devices -->
  <div class="cursor" aria-hidden="true">
    <div class="cursor__ring"><span class="cursor__label">{'Ver' if c.lang == 'es' else 'View'}</span></div>
    <div class="cursor__dot"></div>
  </div>
"""


def brand(c):
    label = "Web Designer Puerto Rico &mdash; " + ("inicio" if c.lang == "es" else "home")
    return f"""<a class="brand" href="index.html" aria-label="{label}">
        <picture class="brand__logo">
          <source media="(prefers-color-scheme: dark)" srcset="/images/logo/zao-chat-light.png">
          <img src="/images/logo/zao-chat-light.png" alt="Zao Chat" width="32" height="32">
        </picture>
        <span class="brand__text">Web Designer <em>Puerto Rico</em></span>
      </a>"""


def theme_toggle(c):
    return f"""<button class="theme-toggle" type="button" data-theme-toggle
                aria-pressed="false"
                aria-label="{c.ui['to_dark']}" title="{c.ui['to_dark']}"
                data-label-to-dark="{c.ui['to_dark']}" data-label-to-light="{c.ui['to_light']}">
          <svg class="theme-toggle__moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/>
          </svg>
          <svg class="theme-toggle__sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true">
            <circle cx="12" cy="12" r="4.2"/>
            <path d="M12 2v2.4M12 19.6V22M4.2 4.2l1.7 1.7M18.1 18.1l1.7 1.7M2 12h2.4M19.6 12H22M4.2 19.8l1.7-1.7M18.1 5.9l1.7-1.7"/>
          </svg>
        </button>"""


def lang_switch(c, page):
    es_current = c.lang == "es"
    es_href = page if es_current else c.other_href(page)
    en_href = c.other_href(page) if es_current else page
    return f"""<div class="lang-switch" role="group" aria-label="{c.ui['lang_label']}">
          <a class="lang-switch__opt" href="{es_href}" hreflang="es" lang="es"
             data-lang-switch="es"{' aria-current="true"' if es_current else ''}>ES</a>
          <a class="lang-switch__opt" href="{en_href}" hreflang="en" lang="en"
             data-lang-switch="en"{'' if es_current else ' aria-current="true"'}>EN</a>
        </div>"""


def header(c, page):
    s = c.s
    links = "\n".join(
        f'          <a class="nav__link" data-nav-link href="{n["href"]}">{n["label"]}</a>'
        for n in s["nav"])
    drawer_items = "\n".join(f"""      <div class="mobile-menu__item">
        <a class="mobile-menu__link" data-nav-link href="{n['href']}">
          <span class="index-num">{n['index']}</span> {n['label']}
        </a>
      </div>""" for n in s["nav"])

    return f"""
  <header class="site-header">
    <div class="site-header__inner">
      {brand(c)}

      <nav class="nav" aria-label="{'Principal' if c.lang == 'es' else 'Primary'}">
{links}
      </nav>

      <div class="header__actions">
        <div class="controls">
          {lang_switch(c, page)}
          {theme_toggle(c)}
        </div>
        <a class="btn btn--primary" href="tel:+19392299233" data-magnetic="0.25">
          <span>(939) 229-9233</span>
        </a>
        <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="{c.ui['menu_open']}">
          <span class="menu-toggle__bars" aria-hidden="true"><span></span><span></span><span></span></span>
        </button>
      </div>
    </div>
  </header>

  <!-- Full-screen drawer for narrow viewports -->
  <div class="mobile-menu" id="mobile-menu" aria-hidden="true">
    <nav class="mobile-menu__nav" aria-label="{'Móvil' if c.lang == 'es' else 'Mobile'}">
{drawer_items}
    </nav>
    <div class="mobile-menu__foot">
      <div class="mobile-menu__controls">
        <span class="control-label">{c.ui['lang_label']}</span>
        {lang_switch(c, page)}
      </div>
      <p class="label label--plain">{c.ui['drawer_cta']}</p>
      <a class="display-4 link-underline" href="mailto:{c.s_default['contact']['email']}">{c.s_default['contact']['email']}</a>
      <p class="muted" style="font-size:var(--fs-sm)">{c.ui['drawer_note']}</p>
    </div>
  </div>
"""


# ---------------------------------------------------------------------------
# SECTION HELPERS
# ---------------------------------------------------------------------------

def section_head(num, eyebrow, title_html, aside="", extra=""):
    aside_html = (f'<p class="section-head__aside" data-reveal="up" data-delay="0.1">{aside}</p>'
                  if aside else "")
    return f"""      <div class="section-head">
        <div class="section-head__meta">
          <span class="index-num" data-section-index>{num}</span>
          <span class="label">{eyebrow}</span>
        </div>
        <div>
          <h2 class="display-2 section-head__title" data-split="words">{title_html}</h2>
          {aside_html}
          {extra}
        </div>
      </div>
"""


def page_header(c, eyebrow, title_html, lead, meta_html=""):
    return f"""
  <!-- ============ PAGE HEADER ============ -->
  <header class="page-header">
    <div class="glow glow--primary page-header__glow" aria-hidden="true"></div>
    <div class="container">
      <nav class="breadcrumb" aria-label="{'Ruta' if c.lang == 'es' else 'Breadcrumb'}">
        <a class="link-underline" href="index.html">{c.ui['breadcrumb_home']}</a>
        <span aria-hidden="true">/</span>
        <span aria-current="page">{eyebrow}</span>
      </nav>
      <h1 class="display-1 page-header__title" data-split="words">{title_html}</h1>
      <div class="page-header__grid">
        <p class="lead" style="max-width:48ch" data-reveal="up">{lead}</p>
        {meta_html}
      </div>
    </div>
  </header>
"""


def themed_img(c, light, dark, alt, w, h, extra=""):
    """An <img> whose source swaps with the theme (js/theme.js)."""
    light_rel, dark_rel = c.media(light), c.media(dark or light)
    return (f'<img src="{light_rel}" data-src-light="{light_rel}" data-src-dark="{dark_rel}" '
            f'width="{w}" height="{h}" loading="lazy" decoding="async" alt="{alt}" {extra}>')


def cta(c, block, primary=None, secondary=None):
    p_href, p_label = primary or ("contact.html", c.ui["cta_primary"])
    s_href, s_label = secondary or ("portfolio.html", c.ui["cta_secondary"])
    return f"""
  <!-- ============ CALL TO ACTION ============ -->
  <section class="cta">
    <div class="glow glow--primary cta__glow" aria-hidden="true"></div>
    <img class="cta__orbit float-slow" src="{c.asset('images/hero/orbit.svg')}"
         data-src-light="{c.asset('images/hero/orbit.svg')}" data-src-dark="{c.asset('images/hero/orbit-dark.svg')}"
         alt="" aria-hidden="true" width="720" height="720" loading="lazy" decoding="async" data-parallax="0.08">
    <div class="container">
      <div class="cta__inner">
        <p class="label" data-reveal="fade">{c.ui['next_step']}</p>
        <h2 class="display-2 cta__title" data-split="words">{block['title']}</h2>
        <p class="prose u-center" style="margin-inline:auto" data-reveal="up">{block['body']}</p>
        <div class="cta__actions" data-reveal="up" data-delay="0.1">
          <a class="btn btn--primary btn--lg" href="{p_href}" data-magnetic="0.3"><span>{p_label} {ARROW}</span></a>
          <a class="btn btn--ghost btn--lg" href="{s_href}" data-magnetic="0.3"><span>{s_label} {ARROW}</span></a>
        </div>
        <div class="cta__meta" data-reveal="fade" data-delay="0.2">
          <span class="label label--plain"><span class="pulse-dot" aria-hidden="true"><i></i></span> {c.ui['cta_availability']}</span>
          <span class="label label--plain">{c.ui['cta_reply']}</span>
        </div>
      </div>
    </div>
  </section>
"""


def footer(c):
    s, f = c.s, c.s["footer"]
    contact = c.s_default["contact"]
    svc = "\n          ".join(
        f'<a class="link-underline" href="services.html#{x["anchor"]}">{x["label"]}</a>'
        for x in f["service_links"])
    pages = "\n          ".join(
        f'<a class="link-underline" href="{n["href"]}">{n["label"]}</a>' for n in s["nav"])

    return f"""
  <!-- ============ FOOTER ============ -->
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          {brand(c)}
          <p class="muted" style="font-size:var(--fs-sm)">{f['tagline']}</p>
          <p class="label label--plain"><span class="pulse-dot" aria-hidden="true"><i></i></span> {f['available']}</p>
        </div>

        <nav class="footer-col" aria-label="{'Pie de página' if c.lang == 'es' else 'Footer navigation'}">
          <h2 class="footer-col__title">{f['pages_title']}</h2>
          {pages}
        </nav>

        <div class="footer-col">
          <h2 class="footer-col__title">{f['services_title']}</h2>
          {svc}
        </div>

        <div class="footer-col">
          <h2 class="footer-col__title">{f['contact_title']}</h2>
          <a class="link-underline" href="mailto:{contact['email']}">{contact['email']}</a>
          <a class="link-underline" href="{contact['phone_href']}">{contact['phone_display']}</a>
          <span>{f['location']}</span>
          <span>{f['hours']}</span>
        </div>
      </div>
    </div>

    <div class="container">
      <div class="footer-bottom">
        <span>&copy; <span data-year>2026</span> Web Designer Puerto Rico. {f['rights']}</span>
        <a class="to-top" href="#top" data-to-top>{c.ui['back_to_top']} {ARROW_UP}</a>
      </div>
    </div>
  </footer>
"""


def scripts(c):
    return f"""
  <!-- GSAP from CDN. If either file fails to load, js/animations.js detects the
       absence and the CSS fallback in animations.css reveals all content. -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>

  <script src="{c.asset('js/theme.js')}" defer></script>
  <script src="{c.asset('js/navigation.js')}" defer></script>
  <script src="{c.asset('js/main.js')}" defer></script>
  <script src="{c.asset('js/animations.js')}" defer></script>
</body>
</html>
"""
