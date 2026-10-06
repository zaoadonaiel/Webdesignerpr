# -*- coding: utf-8 -*-
"""Shared chrome — head, header, drawer, CTA, footer — rendered per language."""
import os
from contextlib import contextmanager
from .content import SITE_URL, DEFAULT_LANG, load, page_url as _page_url

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


# Hand-drawn inline icons, keyed by the service id used in content/services.json
SVC_ICONS = {
 "website-design": '<path d="M3 5h28v22H3z"/><path d="M3 11h28M8 8h.01M11 8h.01M14 8h.01"/>',
 "website-development": '<path d="M11 22 4 15l7-7M23 10l7 7-7 7M19 6l-4 22"/>',
 "wordpress": '<circle cx="17" cy="17" r="13"/><path d="M5 12h9M9 12l5 14 4-11M22 12h5l-4 14-3-9"/>',
 "ecommerce": '<path d="M4 6h4l3 15h15l3-11H10"/><circle cx="13" cy="27" r="2"/><circle cx="25" cy="27" r="2"/>',
 "ui-ux": '<circle cx="11" cy="11" r="7"/><rect x="18" y="18" width="12" height="12" rx="2"/><path d="M18 11h12"/>',
 "redesign": '<path d="M29 17a12 12 0 1 1-3.5-8.5M29 4v6h-6"/>',
 "performance": '<path d="M17 29a12 12 0 1 1 12-12"/><path d="M17 17l8-6"/><circle cx="17" cy="17" r="2"/>',
}
FALLBACK_ICON = '<circle cx="17" cy="17" r="13"/><path d="M17 11v12M11 17h12"/>'


def svc_icon(sid, cls="svc-icon"):
    return (f'<svg class="{cls}" viewBox="0 0 34 34" fill="none" stroke="currentColor" '
            f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'{SVC_ICONS.get(sid, FALLBACK_ICON)}</svg>')


# Industry icons, keyed by the id used in content/industries.json
IND_ICONS = {
 "restaurants": '<path d="M9 4v9a3 3 0 0 0 6 0V4M12 4v26M25 30V4c-3.5 2-5.5 6-5.5 11H25"/>',
 "healthcare": '<path d="M17 29S6 22.5 6 15a6 6 0 0 1 11-3.3A6 6 0 0 1 28 15c0 7.5-11 14-11 14Z"/><path d="M10 17h4l2-3 3 6 2-3h3"/>',
 "law-firms": '<path d="M17 4v26M10 30h14M6 9h22M10 9l-5 10a5 5 0 0 0 10 0L10 9ZM24 9l-5 10a5 5 0 0 0 10 0L24 9Z"/>',
 "real-estate": '<path d="M4 16 17 5l13 11M8 13v16h18V13"/><path d="M14 29v-8h6v8"/>',
 "tourism": '<path d="M17 30c0-8 1-14 3-18M20 12c-3-4-8-4-11-1M20 12c1-4 6-6 10-4M20 12c4 0 7 3 7 7M20 12c-4 1-6 5-5 9"/><path d="M7 30h20"/>',
 "contractors": '<path d="M6 24a11 11 0 0 1 22 0M14 14V9h6v5M4 24h26v4H4z"/>',
 "retail": '<path d="M7 11h20l-2 19H9L7 11Z"/><path d="M12 14V9a5 5 0 0 1 10 0v5"/>',
 "beauty-wellness": '<circle cx="9" cy="25" r="4"/><circle cx="25" cy="25" r="4"/><path d="M12 22 26 5M22 22 8 5"/>',
}


def ind_icon(iid, cls="svc-icon"):
    return (f'<svg class="{cls}" viewBox="0 0 34 34" fill="none" stroke="currentColor" '
            f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            f'{IND_ICONS.get(iid, FALLBACK_ICON)}</svg>')


class Ctx:
    """Everything that varies by language: paths, URLs and the chrome strings.

    Links are relative, so they depend on how deep the page being rendered
    sits. A page at the language root (about.html) and one in a subfolder
    (articles/some-slug.html) need different prefixes for the same target.
    `depth` tracks that: set it via `at_depth()` while rendering nested pages,
    and every helper below adjusts.
    """

    def __init__(self, lang, out_root):
        self.lang = lang
        self.out = out_root if lang == DEFAULT_LANG else os.path.join(out_root, lang)
        # How far the language folder sits below the site root
        self._lang_depth = 0 if lang == DEFAULT_LANG else 1
        # How far the current page sits below its language folder
        self.depth = 0
        settings = load("settings")
        self.s = settings[lang]
        self.s_default = settings[DEFAULT_LANG]
        # Interface strings are grouped so the CMS can collapse them
        self.ui = self.s["interface"]

    # --- depth ---------------------------------------------------------
    @contextmanager
    def at_depth(self, depth):
        """Render a page that sits `depth` folders below the language root."""
        previous = self.depth
        self.depth = depth
        try:
            yield self
        finally:
            self.depth = previous

    @property
    def pre(self):
        """Prefix from the current page up to the SITE root."""
        return "../" * (self._lang_depth + self.depth)

    @property
    def here(self):
        """Prefix from the current page up to its LANGUAGE root."""
        return "../" * self.depth

    # --- paths ---------------------------------------------------------
    def asset(self, path):
        """Relative path to a site-root asset (css, js, images)."""
        return self.pre + path.lstrip("/")

    def media(self, path):
        """Media paths are stored absolute by the CMS ("/images/…"); the site
        uses relative links so it works from any subfolder."""
        if not path:
            return ""
        if path.startswith(("http://", "https://", "data:")):
            return path
        return self.pre + path.lstrip("/")

    def link(self, page):
        """Relative path to another page in the SAME language."""
        if not page:
            return ""
        if page.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            return page
        return self.here + page.lstrip("/")

    def page_url(self, page, lang=None):
        return _page_url(page, lang or self.lang)

    def other_href(self, page):
        """The same page in the other language, relative to where we are."""
        page = page.lstrip("/")
        if self.lang == DEFAULT_LANG:
            # up to the site root, then down into /en/
            return self.here + "en/" + page
        # up out of /en/ entirely, then down to the page
        return self.here + "../" + page

    def write(self, page, html):
        os.makedirs(self.out, exist_ok=True)
        filepath = os.path.join(self.out, page)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)


# ---------------------------------------------------------------------------
# HEAD
# ---------------------------------------------------------------------------

# CMS field names cannot contain dots, so page metadata is keyed by a plain name
META_KEY = {"index.html": "home", "about.html": "about", "services.html": "services",
            "portfolio.html": "portfolio", "deals.html": "deals", "contact.html": "contact", "articles.html": "articles",
            "industries.html": "industries"}


# Google Analytics 4 (gtag.js), injected into every page's <head>.
GA_TAG = """  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-T0JX28D4PC"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-T0JX28D4PC');
  </script>
"""

# Google Ads conversion tracking (gtag.js), injected into every page's <head>.
GOOGLE_ADS_TAG = """  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=AW-18478711242"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'AW-18478711242');

    // "Phone number click" conversion: fires on any tel: link on any page.
    // No redirect callback needed - tapping a tel: link doesn't unload the page.
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href^="tel:"]');
      if (!a) return;
      gtag('event', 'conversion', {
        'send_to': 'AW-18478711242/vvO7CLjQzJMdEMqDq-tE',
        'value': 1.0,
        'currency': 'USD'
      });
    });
  </script>
"""


def head(c, page, title=None, description=None, keywords=None, extra="", og_type="website"):
    if title is None or description is None:
        # Use meta from settings.json
        meta = c.s["meta"][META_KEY[page]]
        title = title or meta["title"]
        description = description or meta["description"]
    
    es_url, en_url = c.page_url(page, "es"), c.page_url(page, "en")
    og_locale = "es_PR" if c.lang == "es" else "en_US"
    og_alt = "en_US" if c.lang == "es" else "es_PR"

    return f"""<!DOCTYPE html>
<html lang="{c.lang}">
<head>
  <meta charset="utf-8">
{GA_TAG}{GOOGLE_ADS_TAG}  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="google" content="notranslate">
  <title>{title}</title>
  <meta name="description" content="{description}">
  {f'<meta name="keywords" content="{keywords}">' if keywords else ''}
  <link rel="canonical" href="{c.page_url(page)}">

  <!-- Both language versions of this page -->
  <link rel="alternate" hreflang="es" href="{es_url}">
  <link rel="alternate" hreflang="en" href="{en_url}">
  <link rel="alternate" hreflang="x-default" href="{es_url}">

  <!-- Matches whichever theme is active, so browser UI follows the page -->
  <meta name="theme-color" content="#faf7f1" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#08090b" media="(prefers-color-scheme: dark)">

  <!-- Open Graph / social -->
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="Web Designer Puerto Rico">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{c.page_url(page)}">
  <meta property="og:image" content="{SITE_URL}/images/logo/og-image.jpg">
  <meta property="og:image:type" content="image/jpeg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="{og_locale}">
  <meta property="og:locale:alternate" content="{og_alt}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{SITE_URL}/images/logo/og-image.jpg">

  <link rel="icon" href="{c.asset('images/logo/favicon.png')}" type="image/png">
  <link rel="apple-touch-icon" href="{c.asset('images/logo/favicon.png')}">

  <!-- Typography -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&amp;family=Inter+Tight:ital,wght@0,300;0,400;0,500;0,600;1,400&amp;family=Google+Sans:wght@400;500;600;700&amp;display=swap">

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
{extra}
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
    return f"""<a class="brand" href="{c.link('index.html')}" aria-label="{label}">
        <span class="brand__logo">
          <img class="brand__logo--on-light" src="/images/logo/zao-chat-dark.png" alt="Zao Chat" width="32" height="32">
          <img class="brand__logo--on-dark" src="/images/logo/zao-chat-light.png" alt="" width="32" height="32">
        </span>
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


def lang_switch(c, page, other_page=None):
    """`other_page` overrides the target in the other language — used when a
    page has no direct counterpart (an untranslated article, say), so the
    switch lands somewhere real instead of a 404."""
    other = other_page or page
    es_current = c.lang == "es"
    es_href = c.link(page) if es_current else c.other_href(other)
    en_href = c.other_href(other) if es_current else c.link(page)
    return f"""<div class="lang-switch" role="group" aria-label="{c.ui['lang_label']}">
          <a class="lang-switch__opt" href="{es_href}" hreflang="es" lang="es"
             data-lang-switch="es"{' aria-current="true"' if es_current else ''}>ES</a>
          <a class="lang-switch__opt" href="{en_href}" hreflang="en" lang="en"
             data-lang-switch="en"{'' if es_current else ' aria-current="true"'}>EN</a>
        </div>"""


CHEVRON = ('<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5" '
           'aria-hidden="true"><path d="M3 4.5 6 7.5l3-3"/></svg>')

MEGA_COPY = {
    "services": {
        "es": {"toggle": "Mostrar servicios",
               "aside_label": "¿No sabes por dónde empezar?",
               "aside_title": "Una llamada de 30 minutos y te decimos qué necesitas &mdash; <em>y qué no</em>.",
               "all": "Ver todos los servicios", "call": "Agendar llamada"},
        "en": {"toggle": "Show services",
               "aside_label": "Not sure where to start?",
               "aside_title": "One 30-minute call and we will tell you what you need &mdash; <em>and what you don't</em>.",
               "all": "All services", "call": "Book a call"},
    },
    "industries": {
        "es": {"toggle": "Mostrar industrias",
               "aside_label": "¿Tu industria no está aquí?",
               "aside_title": "Los principios son los mismos. <em>Cuéntanos de tu negocio</em>.",
               "all": "Ver todas las industrias", "call": "Agendar llamada"},
        "en": {"toggle": "Show industries",
               "aside_label": "Industry not listed?",
               "aside_title": "The principles are the same. <em>Tell us about your business</em>.",
               "all": "All industries", "call": "Book a call"},
    },
}

# Nav entries that open a mega menu: index page -> content file (and folder)
MEGA_SECTIONS = {"services.html": "services", "industries.html": "industries"}


def menu_items(c, section):
    """(id, title, one-line blurb) for every landing page in a section."""
    items = load(section)[c.lang].get("items", [])
    return [(x["id"], x["title"], x.get("menu_blurb") or x.get("summary", ""))
            for x in items if x.get("id")]


def mega_menu(c, n, section):
    """A nav item with a mega menu: a real link to the index page plus a
    disclosure button that opens a panel of every landing page in the
    section. The link stays a link so the index is one click away and
    crawlable either way."""
    m = MEGA_COPY[section][c.lang]
    icon = svc_icon if section == "services" else ind_icon
    items = "\n".join(f"""              <li><a class="mega__item" href="{c.link(f'{section}/{sid}.html')}" data-nav-link>
                {icon(sid, 'mega__icon')}
                <span class="mega__text"><span class="mega__title">{title}</span><span class="mega__desc">{blurb}</span></span>
              </a></li>""" for sid, title, blurb in menu_items(c, section))
    contact = c.s_default["contact"]
    return f"""          <div class="nav__item nav__item--mega" data-mega>
            <a class="nav__link" data-nav-link data-nav-section="{section}" href="{c.link(n['href'])}">{n['label']}</a>
            <button class="nav__caret" type="button" aria-expanded="false" aria-controls="mega-{section}"
                    aria-label="{m['toggle']}" data-mega-toggle>{CHEVRON}</button>
            <div class="mega" id="mega-{section}" data-mega-panel>
              <div class="mega__inner">
                <ul class="mega__grid" role="list">
{items}
                </ul>
                <div class="mega__aside">
                  <p class="label label--plain">{m['aside_label']}</p>
                  <p class="mega__aside-title">{m['aside_title']}</p>
                  <div class="mega__aside-actions">
                    <a class="btn btn--primary" href="{c.link('contact.html')}"><span>{m['call']} {ARROW}</span></a>
                    <a class="link-arrow" href="{c.link(n['href'])}">{m['all']} {ARROW_R}</a>
                  </div>
                  <a class="mega__phone" href="{contact['phone_href']}">{contact['phone_display']}</a>
                </div>
              </div>
            </div>
          </div>"""


def header(c, page, other_page=None):
    s = c.s
    links = "\n".join(
        mega_menu(c, n, MEGA_SECTIONS[n["href"]]) if n["href"] in MEGA_SECTIONS else
        f'          <a class="nav__link" data-nav-link href="{c.link(n["href"])}">{n["label"]}</a>'
        for n in s["nav"])

    def drawer_sub(n):
        section = MEGA_SECTIONS.get(n["href"])
        if not section:
            return ""
        return ('\n        <ul class="mobile-menu__sub" role="list">' + "".join(
            f'\n          <li><a data-nav-link href="{c.link(f"{section}/{sid}.html")}">{title}</a></li>'
            for sid, title, _ in menu_items(c, section)) + "\n        </ul>")

    drawer_items = "\n".join(f"""      <div class="mobile-menu__item">
        <a class="mobile-menu__link" data-nav-link href="{c.link(n['href'])}">
          <span class="index-num">{n['index']}</span> {n['label']}
        </a>{drawer_sub(n)}
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
          {lang_switch(c, page, other_page)}
          {theme_toggle(c)}
        </div>
        <a class="btn btn--primary" href="tel:+19392299233" data-magnetic="0.25">
          <span>(939) 229-9233</span>
        </a>
        <a class="whatsapp-btn" href="https://wa.me/19392299233" target="_blank" rel="noopener noreferrer" data-magnetic="0.25" title="WhatsApp" style="display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 50%; background-color: #25D366; color: white; text-decoration: none; transition: transform 0.2s, box-shadow 0.2s;">
<img src="/images/whatsapp-icon.png" alt="WhatsApp" width="24" height="24" />
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
        {lang_switch(c, page, other_page)}
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
    <div class="page-header__overlay" aria-hidden="true"></div>
    <div class="glow glow--primary page-header__glow" aria-hidden="true"></div>
    <div class="container">
      <nav class="breadcrumb" aria-label="{'Ruta' if c.lang == 'es' else 'Breadcrumb'}">
        <a class="link-underline" href="{c.link('index.html')}">{c.ui['breadcrumb_home']}</a>
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
  <section class="cta" style="position:relative;overflow:hidden;">
    <div class="glow glow--primary cta__glow" aria-hidden="true"></div>
    <video autoplay muted loop playsinline preload="metadata"
         style="position:absolute;top:0;left:0;width:100%;height:100%;opacity:0.1;z-index:0;object-fit:cover;"
         aria-hidden="true">
      <source src="{c.media('/images/portfolio/Web Designer Puerto Rico - Website Design San Juan.mp4')}" type="video/mp4">
    </video>
    <div class="container" style="position:relative;z-index:1;">
      <div class="cta__inner">
        <p class="label" data-reveal="fade">{c.ui['next_step']}</p>
        <h2 class="display-2 cta__title" data-split="words">{block['title']}</h2>
        <p class="prose u-center" style="margin-inline:auto" data-reveal="up">{block['body']}</p>
        <div class="cta__actions" data-reveal="up" data-delay="0.1">
          <a class="btn btn--primary btn--lg" href="{c.link(p_href)}" data-magnetic="0.3"><span>{p_label} {ARROW}</span></a>
          <a class="btn btn--ghost btn--lg" href="{c.link(s_href)}" data-magnetic="0.3"><span>{s_label} {ARROW}</span></a>
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
        f'<a class="link-underline" href="{c.link("services/" + x["anchor"] + ".html")}">{x["label"]}</a>'
        for x in f["service_links"])
    pages = "\n          ".join(
        f'<a class="link-underline" href="{c.link(n["href"])}">{n["label"]}</a>' for n in s["nav"])

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
