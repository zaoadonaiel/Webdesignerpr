# -*- coding: utf-8 -*-
"""Renders the five pages from content/. Every string comes from the CMS."""
import re

from .content import DEFAULT_LANG, load, load_projects, shared, texts
from .partials import (head, chrome, header, footer, scripts, cta, section_head,
                       page_header, themed_img, ARROW, ARROW_R, STAR, MARK_PATH)

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

VIEW = {"es": "Ver", "en": "View"}


def _img(doc, *path):
    """Read an image path from the default locale.

    The CMS keeps these in sync across locales (i18n: duplicate), but reading
    one source means the two languages can never end up pointing at different
    files if a copy is edited by hand.
    """
    node = doc[DEFAULT_LANG]
    for key in path:
        node = node[key]
    return node


# ---------------------------------------------------------------------------
# ARTICLE BYLINE HELPERS
# ---------------------------------------------------------------------------

MONTHS = {
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio",
           "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "en": ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
}


def format_date(iso, lang):
    """2026-09-23 -> '23 de septiembre de 2026' / 'September 23, 2026'.

    Returns the raw string unchanged if it isn't an ISO date, so a hand-typed
    value never breaks the page.
    """
    if not iso:
        return ""
    parts = str(iso).strip()[:10].split("-")
    if len(parts) != 3 or not all(x.isdigit() for x in parts):
        return str(iso)
    year, month, day = (int(x) for x in parts)
    if not 1 <= month <= 12:
        return str(iso)
    name = MONTHS.get(lang, MONTHS["en"])[month - 1]
    return f"{day} de {name} de {year}" if lang == "es" else f"{name} {day}, {year}"


def reading_minutes(html, wpm=200):
    """Rough reading time from the article body, tags stripped."""
    text = re.sub(r"<[^>]+>", " ", html or "")
    words = len(text.split())
    return max(1, round(words / wpm)) if words else 1


def article_author(article, c):
    """Per-article author if the CMS or Zao Flo supplied one, else the site
    default from Settings. Any missing field falls back individually."""
    default = c.s.get("author", {}) or {}
    override = article.get("author") or {}
    if isinstance(override, str):          # a bare name is allowed
        override = {"name": override}
    merged = dict(default)
    merged.update({k: v for k, v in override.items() if v})
    return merged


# ---------------------------------------------------------------------------
# shared section renderers
# ---------------------------------------------------------------------------

def _process_track(c):
    steps = "".join(f"""          <article class="process__step">
            <span class="process__num">{s['index']}</span>
            <h3 class="process__title">{s['title']}</h3>
            <p class="process__text">{s['text']}</p>
            <p class="process__meta label label--plain">{s['meta']}</p>
          </article>""" for s in load("process")[c.lang]["steps"])
    return f"""      <div class="container">
        <div class="process__viewport">
          <div class="process__track">
{steps}
          </div>
        </div>
      </div>"""


def _capabilities(c):
    return "".join(f"""          <li class="tech-item">
            <span class="tech-item__name">{x['name']}</span>
            <span class="tech-item__cat">{x['category']}</span>
          </li>""" for x in load("capabilities")[c.lang]["items"])


def _stats(stats, static):
    out = []
    for s in stats:
        value, suffix, label = s.get("value", ""), s.get("suffix", ""), s.get("label", "")
        if not value:
            val = f'<span class="stat__value">{static}</span>'
        else:
            dec = 1 if "." in value else 0
            zero = "0.0" if dec else "0"
            sup = f"<sup>{suffix}</sup>" if suffix == "+" else ""
            inner = suffix if suffix != "+" else ""
            dec_attr = f' data-decimals="{dec}"' if dec else ""
            val = (f'<span class="stat__value"><span data-counter="{value}"{dec_attr}'
                   f' data-suffix="{inner}">{zero}{inner}</span>{sup}</span>')
        out.append(f"""            <div class="stat">
              {val}
              <span class="stat__label">{label}</span>
            </div>""")
    return "\n".join(out)


def _value_list(items, indent="          "):
    return "".join(f"""{indent}<li class="value-item" data-reveal="up">
{indent}  <span class="index-num">{i['index']}</span>
{indent}  <div>
{indent}    <h3 class="value-item__title">{i['title']}</h3>
{indent}    <p class="value-item__text">{i['text']}</p>
{indent}  </div>
{indent}</li>""" for i in items)


def _plain(kind):
    return kind.replace("&middot;", "—").replace("&#8209;", "-")


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------

def build_home(c):
    doc = load("home")
    d = doc[c.lang]
    projects = load_projects()
    featured = [p for p in projects if shared(p, "featured")]

    out = [head(c, "index.html"), chrome(c), header(c, "index.html")]
    out.append('  <main class="site-main" id="main">\n    <span id="top"></span>\n')

    lines = "\n".join(
        f'          <span class="line{" indent" if i == 1 else ""}"><span>{t}</span></span>'
        for i, t in enumerate(texts(d["hero_lines"])))
    marquee = "\n        ".join(
        f'<span class="service-tag">{t}</span>' for t in texts(d["marquee"]))
    st = d["studio"]

    out.append(f"""
    <!-- ============ HERO ============ -->
    <section class="hero" style="background-image: url('/images/hero/pr-background.jpg'); background-size: cover; background-position: center; background-attachment: fixed;">
      <div class="hero__overlay"></div>
      <canvas class="hero__canvas" aria-hidden="true"></canvas>
      <div class="glow glow--primary hero__glow-a" aria-hidden="true"></div>
      <div class="glow glow--secondary hero__glow-b" aria-hidden="true"></div>

      <div class="container hero__inner">
        <p class="label" data-hero-fade>{d['eyebrow']}</p>

        <div class="hero__content">
          <div class="hero__left">
            <h1 class="hero__title">
{lines}
            </h1>

            <div class="hero__meta">
              <p class="lead" data-hero-fade>{d['hero_lead']}</p>

              <div class="hero__actions" data-hero-fade>
                <a class="btn btn--primary btn--lg" href="contact.html" data-magnetic="0.3">
                  <span>{c.ui['cta_primary']} {ARROW}</span>
                </a>
                <a class="btn btn--ghost btn--lg" href="portfolio.html" data-magnetic="0.3">
                  <span>{c.ui['cta_secondary']} {ARROW}</span>
                </a>
              </div>
            </div>
          </div>

          <div class="hero__right">
          </div>
        </div>

        <p class="hero__scroll" data-hero-fade>
          <span class="hero__scroll-line" aria-hidden="true"></span>
          {d['scroll']}
        </p>
      </div>
    </section>

    <!-- ============ SERVICES TAGS ============ -->
    <section class="services-tags">
      <div class="container">
        <div class="services-tags__grid">
{marquee}
        </div>
      </div>
    </section>

    <!-- ============ 01 — INTRODUCTION ============ -->
    <section class="section" id="studio">
      <div class="container">
{section_head(st['index'], st['eyebrow'], st['title'])}
        <div class="split split--reverse">
          <div class="split__body">
            <div class="prose">
              {"".join(f"<p>{p}</p>" for p in texts(st['paragraphs']))}
            </div>
            <div class="u-mt-lg">
              <a class="link-arrow" href="about.html">{st['link']} {ARROW_R}</a>
            </div>
          </div>

          <div class="split__media" data-reveal-media>
            <div class="media-frame media-frame--tall">
              <img src="/images/hero/agency-workspace.png" alt="Web Designer Puerto Rico agency workspace in San Juan" width="900" height="1125" loading="lazy" decoding="async" data-parallax="0.12" style="width:100%;height:auto;">
            </div>
          </div>
        </div>

        <!-- Standards, not a brag sheet: commitments we build against -->
        <div class="u-mt-xl">
          <p class="label u-mb-lg" data-reveal="fade">{st['standards_label']}</p>
          <div class="stats" data-stagger="0.1">
{_stats(st['stats'], st['stat_static'])}
          </div>
        </div>
      </div>
    </section>
""")

    # --- selected work ----------------------------------------------------
    rows, previews = [], []
    for i, p in enumerate(featured, start=1):
        loc = p[c.lang]
        tags = "".join(f'<span class="tag">{x}</span>' for x in texts(loc["disciplines"]))
        rows.append(f"""        <li class="work-item" data-work-item>
          <a class="work-item__link" href="portfolio.html#{shared(p,'slug')}" data-cursor="view" data-cursor-label="{VIEW[c.lang]}">
            <span class="index-num">{i:02d}</span>
            <h3 class="work-item__title display-3">{shared(p,'name')}</h3>
            <div class="work-item__tags">
              <span class="tag tag--concept">{load('portfolio')[c.lang]['tag_concept']}</span>
              {tags}
            </div>
            <span class="work-item__year">{shared(p,'year')}</span>
          </a>
        </li>""")
        light, dark = c.media(shared(p, "image_light")), c.media(shared(p, "image_dark"))
        previews.append(f'      <img src="{light}" data-src-light="{light}" data-src-dark="{dark}" '
                        f'alt="" aria-hidden="true" width="1200" height="900" loading="lazy" decoding="async">')

    w = d["work"]
    out.append(f"""
    <!-- ============ 02 — SELECTED WORK ============ -->
    <section class="section" id="work">
      <div class="container">
{section_head(w['index'], w['eyebrow'], w['title'], w['aside'])}
        <ul class="work-list" data-work-list>
{chr(10).join(rows)}
        </ul>

        <div class="u-mt-xl" data-reveal="up">
          <a class="btn btn--ghost btn--lg" href="portfolio.html" data-magnetic="0.3">
            <span>{w['button']} {ARROW}</span>
          </a>
        </div>
      </div>
    </section>

    <!-- Cursor-following preview plate for the list above -->
    <div class="work-preview" aria-hidden="true">
{chr(10).join(previews)}
    </div>
""")

    # --- services ---------------------------------------------------------
    sv = d["services"]
    svc_items = load("services")[c.lang]["items"]
    cards = "\n".join(f"""          <article class="card">
            <svg class="card__icon" viewBox="0 0 34 34" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{SVC_ICONS.get(x['id'], FALLBACK_ICON)}</svg>
            <div>
              <h3 class="card__title">{x['title']}</h3>
              <p class="card__text u-mt-sm">{x['summary']}</p>
            </div>
            <a class="link-arrow" href="services.html#{x['id']}">{sv['detail_link']} {ARROW_R}</a>
          </article>""" for x in svc_items)

    why, proc, tst, cap = d["why"], d["process"], d["testimonials"], d["capabilities"]
    quotes = load("testimonials")[c.lang]["items"]

    out.append(f"""
    <!-- ============ 03 — SERVICES ============ -->
    <section class="section" id="services">
      <div class="container">
{section_head(sv['index'], sv['eyebrow'], sv['title'], sv['aside'])}
        <div class="card-grid" data-stagger="0.07">
{cards}
          <article class="card" style="background:var(--color-surface)">
            <div>
              <h3 class="card__title">{sv['card_title']}</h3>
              <p class="card__text u-mt-sm">{sv['card_text']}</p>
            </div>
            <a class="btn btn--primary" href="contact.html" data-magnetic="0.25"><span>{sv['card_cta']} {ARROW}</span></a>
          </article>
        </div>
      </div>
    </section>

    <!-- ============ 04 — WHY US ============ -->
    <section class="section" id="why">
      <div class="container">
{section_head(why['index'], why['eyebrow'], why['title'])}
        <ul class="value-list">
{_value_list(why['items'])}
        </ul>
      </div>
    </section>

    <!-- ============ 05 — PROCESS (horizontal scroll) ============ -->
    <section class="section process" id="process" data-process>
      <div class="container">
{section_head(proc['index'], proc['eyebrow'], proc['title'], proc['aside'])}
      </div>
{_process_track(c)}
    </section>

    <!-- ============ 06 — TESTIMONIALS ============
         Layout placeholders, not real client quotes. The visible notice
         below is deliberate; replace both before launch. See README.md.  -->
    <section class="section" id="testimonials">
      <div class="container">
{section_head(tst['index'], tst['eyebrow'], tst['title'], "",
              f'<p class="sample-note u-mt-md" data-reveal="fade">{tst["sample_note"]}</p>'
              if tst.get("sample_note") else "")}
        <div class="quote-grid" data-stagger="0.1">
{"".join(f'''          <figure class="quote">
            <span class="quote__mark" aria-hidden="true">&ldquo;</span>
            <blockquote class="quote__text">{q['quote']}</blockquote>
            <figcaption class="quote__author">
              <span class="quote__name">{q['name']}</span>
              <span class="quote__role">{q['role']}</span>
            </figcaption>
          </figure>''' for q in quotes)}
        </div>
      </div>
    </section>

    <!-- ============ 07 — CAPABILITIES ============ -->
    <section class="section" id="capabilities">
      <div class="container">
{section_head(cap['index'], cap['eyebrow'], cap['title'], cap['aside'])}
        <ul class="tech-grid" data-stagger="0.03">
{_capabilities(c)}
        </ul>
      </div>
    </section>
""")

    out.append(cta(c, d["cta"]))
    out.append("  </main>\n")
    out.append(footer(c))
    out.append(scripts(c))
    c.write("index.html", "".join(out))


# ---------------------------------------------------------------------------
# ABOUT
# ---------------------------------------------------------------------------

def build_about(c):
    doc = load("about")
    d = doc[c.lang]
    out = [head(c, "about.html"), chrome(c), header(c, "about.html")]
    out.append('  <main class="site-main" id="main">\n    <span id="top"></span>\n')

    out.append(page_header(c, d["crumb"], d["title"], d["lead"],
        f"""<div style="display:flex;flex-direction:column;gap:var(--space-sm)" data-reveal="up" data-delay="0.1">
          <p class="label label--plain"><span class="pulse-dot" aria-hidden="true"><i></i></span> {d['est']}</p>
          <p class="muted" style="font-size:var(--fs-sm)">{d['est_note']}</p>
        </div>"""))

    mi, ph, cap, pr = d["mission"], d["philosophy"], d["capabilities"], d["process"]
    home_alt = load("home")[c.lang]["studio"]["image_alt"]

    out.append(f"""
    <!-- ============ 02 — INTRODUCTION ============ -->
    <section class="section section--flush-top">
      <div class="container">
        <div class="split">
          <div class="split__media" data-reveal-media>
            <div class="media-frame media-frame--tall">
              {themed_img(c, _img(doc, 'image_light'), _img(doc, 'image_dark'), home_alt, 900, 1125, 'data-parallax="0.1"')}
            </div>
          </div>
          <div class="split__body">
            <p class="label u-mb-lg" data-reveal="fade">{d['who']}</p>
            <div class="prose">
              {"".join(f"<p>{p}</p>" for p in texts(d['paragraphs']))}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ 03 — MISSION & VISION ============ -->
    <section class="section">
      <div class="container">
{section_head(mi['index'], mi['eyebrow'], mi['title'])}
        <div class="split u-mb-lg">
          <div class="split__media" data-reveal-media>
            <div class="media-frame media-frame--crop">
              {themed_img(c, _img(doc, 'mission', 'system_image_light'), _img(doc, 'mission', 'system_image_dark'), mi['system_alt'], 900, 1125, 'data-parallax="0.09"')}
            </div>
          </div>
          <div class="split__body">
            <p class="prose">{mi['system_text']}</p>
          </div>
        </div>

        <div class="card-grid" data-stagger="0.1">
{"".join(f'''          <article class="card">
            <span class="index-num">{x['kicker']}</span>
            <div>
              <h3 class="card__title">{x['title']}</h3>
              <p class="card__text u-mt-sm">{x['text']}</p>
            </div>
          </article>''' for x in mi['cards'])}
        </div>
      </div>
    </section>

    <!-- ============ 04 — ABOUT DAVID DUARTE ============ -->
    <section class="section">
      <div class="container">
        <div class="split">
          <div class="split__media" data-reveal-media>
            <div class="media-frame media-frame--tall">
              <img src="{d['about_founder']['image']}" alt="{d['about_founder']['image_alt']}" width="400" height="500" style="width:100%;height:auto;border-radius:var(--radius-lg);display:block">
            </div>
          </div>
          <div class="split__body">
            <span class="index-num">{d['about_founder']['index']}</span>
            <h2 class="display-2 u-mb-lg">{d['about_founder']['title']}</h2>
            <div class="prose prose--large">
              {d['about_founder']['bio']}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ 05 — DESIGN PHILOSOPHY ============ -->
    <section class="section">
      <div class="container">
{section_head(ph['index'], ph['eyebrow'], ph['title'], ph['aside'])}
        <div class="split">
          <div class="split__body" style="grid-column:span 4">
            <div class="media-frame" data-reveal-media>
              {themed_img(c, _img(doc, 'philosophy', 'craft_image_light'), _img(doc, 'philosophy', 'craft_image_dark'), ph['craft_alt'], 900, 1125, 'data-parallax="0.08"')}
            </div>
            <div class="u-mt-lg" style="display:flex;justify-content:center">
              <div class="stamp" data-reveal="scale" aria-hidden="true">
                <svg class="stamp__ring" viewBox="0 0 132 132" width="132" height="132">
                  <defs><path id="stamp-path" d="M66,66 m-48,0 a48,48 0 1,1 96,0 a48,48 0 1,1 -96,0"/></defs>
                  <text fill="var(--color-text-muted)" font-family="Google Sans, sans-serif" font-size="11" letter-spacing="3.4">
                    <textPath href="#stamp-path">{ph['stamp']}</textPath>
                  </text>
                </svg>
                <span class="stamp__core">
                  <svg viewBox="0 0 32 32" fill="currentColor"><path d="M16 0c.9 6.6 2.6 10.9 5.3 13.1C23.6 15 27.4 15.9 32 16c-4.6.1-8.4 1-10.7 2.9C18.6 21.1 16.9 25.4 16 32c-.9-6.6-2.6-10.9-5.3-13.1C8.4 17 4.6 16.1 0 16c4.6-.1 8.4-1 10.7-2.9C13.4 10.9 15.1 6.6 16 0Z"/></svg>
                </span>
              </div>
            </div>
          </div>
          <div class="split__media" style="grid-column:span 8">
            <ul class="value-list">
{_value_list(ph['items'], indent="              ")}
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ 06 — CAPABILITIES ============ -->
    <section class="section">
      <div class="container">
{section_head(cap['index'], cap['eyebrow'], cap['title'], cap['aside'])}
        <ul class="tech-grid" data-stagger="0.03">
{_capabilities(c)}
        </ul>

        <div class="u-mt-xl">
          <div class="stats" data-stagger="0.1">
{_stats(cap['stats'], cap['stat_static'])}
          </div>
        </div>
      </div>
    </section>

    <!-- ============ 07 — WORK PROCESS ============ -->
    <section class="section process" data-process>
      <div class="container">
{section_head(pr['index'], pr['eyebrow'], pr['title'], pr['aside'])}
      </div>
{_process_track(c)}
    </section>
""")

    out.append(cta(c, d["cta"], secondary=("services.html", d["cta"]["secondary"])))
    out.append("  </main>\n")
    out.append(footer(c))
    out.append(scripts(c))
    c.write("about.html", "".join(out))


# ---------------------------------------------------------------------------
# SERVICES
# ---------------------------------------------------------------------------

def build_services(c):
    doc = load("services")
    d = doc[c.lang]
    out = [head(c, "services.html"), chrome(c), header(c, "services.html")]
    out.append('  <main class="site-main" id="main">\n    <span id="top"></span>\n')

    out.append(page_header(c, d["crumb"], d["title"], d["lead"],
        f"""<div style="display:flex;flex-direction:column;gap:var(--space-sm)" data-reveal="up" data-delay="0.1">
          <p class="label label--plain">{d['meta_a']}</p>
          <p class="muted" style="font-size:var(--fs-sm)">{d['meta_b']}</p>
        </div>"""))

    rows = "\n".join(f"""        <div class="service-row" id="{x['id']}" data-accordion-item>
          <h2>
            <button class="service-row__head" type="button" data-accordion-trigger
                    aria-expanded="false" aria-controls="panel-{x['id']}">
              <span class="index-num">{x['index']}</span>
              <span class="service-row__title display-3">{x['title']}</span>
              <span class="service-row__toggle" aria-hidden="true"></span>
            </button>
          </h2>
          <div class="service-row__panel" id="panel-{x['id']}">
            <div>
              <div class="service-row__content">
                <span class="label label--plain">{d['detail']}</span>
                <div>
                  <p class="lead" style="max-width:36ch;margin-bottom:var(--space-md)">{x['summary']}</p>
                  <p class="prose">{x['body']}</p>
                </div>
                <div>
                  <p class="label u-mb-lg">{d['included']}</p>
                  <ul class="service-row__deliverables">{"".join(f"<li>{t}</li>" for t in texts(x['deliverables']))}</ul>
                  <p class="u-mt-lg">
                  <a class="link-arrow" href="contact.html">{d['enquire']} {ARROW_R}</a>
                  <br>
                  <a class="link-arrow" href="services/{x['id']}.html" style="margin-top:0.5rem;display:inline-block;">Learn more {ARROW_R}</a>
                </p>
                </div>
              </div>
            </div>
          </div>
        </div>""" for x in d["items"])

    en, pf, cm, fq = d["engagements"], d["performance"], d["commerce"], d["faq"]

    out.append(f"""
    <!-- ============ 02 — SERVICE LIST ============
         Exclusive accordion: opening one closes the others.            -->
    <section class="section section--flush-top">
      <div class="container">
        <p class="label u-mb-lg" data-reveal="fade">{d['expand']}</p>
        <div data-accordion="exclusive">
{rows}
        </div>
      </div>
    </section>

    <!-- ============ 03 — ENGAGEMENTS ============ -->
    <section class="section">
      <div class="container">
{section_head(en['index'], en['eyebrow'], en['title'], en['aside'])}
        <div class="card-grid" data-stagger="0.1">
{"".join(f'''          <article class="card">
            <span class="index-num">{x['kicker']}</span>
            <div>
              <h3 class="card__title">{x['title']}</h3>
              <p class="card__text u-mt-sm">{x['text']}</p>
            </div>
            <a class="link-arrow" href="contact.html">{x['link']} {ARROW_R}</a>
          </article>''' for x in en['items'])}
        </div>
      </div>
    </section>

    <!-- ============ 04 — PERFORMANCE FOCUS ============ -->
    <section class="section">
      <div class="container">
        <div class="split split--reverse">
          <div class="split__media" data-reveal-media>
            <div class="media-frame">
              {themed_img(c, _img(doc, 'performance', 'image_light'), _img(doc, 'performance', 'image_dark'), pf['alt'], 1200, 675, 'data-parallax="0.1"')}
            </div>
          </div>
          <div class="split__body">
            <p class="label u-mb-lg" data-reveal="fade">{pf['label']}</p>
            <h2 class="display-3" data-split="words">{pf['title']}</h2>
            <div class="prose u-mt-lg">
              {"".join(f"<p>{p}</p>" for p in texts(pf['paragraphs']))}
            </div>
            <div class="u-mt-lg">
              <a class="btn btn--ghost" href="#performance" data-magnetic="0.25"><span>{pf['link']} {ARROW}</span></a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ 05 — COMMERCE FOCUS ============ -->
    <section class="section">
      <div class="container">
        <div class="split">
          <div class="split__media" data-reveal-media>
            <div class="media-frame">
              {themed_img(c, _img(doc, 'commerce', 'image_light'), _img(doc, 'commerce', 'image_dark'), cm['alt'], 1200, 675, 'data-parallax="0.1"')}
            </div>
          </div>
          <div class="split__body">
            <p class="label u-mb-lg" data-reveal="fade">{cm['label']}</p>
            <h2 class="display-3" data-split="words">{cm['title']}</h2>
            <div class="prose u-mt-lg">
              {"".join(f"<p>{p}</p>" for p in texts(cm['paragraphs']))}
            </div>
            <div class="u-mt-lg">
              <a class="btn btn--ghost" href="#ecommerce" data-magnetic="0.25"><span>{cm['link']} {ARROW}</span></a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ 06 — FAQ ============ -->
    <section class="section">
      <div class="container container--narrow">
{section_head(fq['index'], fq['eyebrow'], fq['title'])}
        <div data-accordion>
{"".join(f'''          <div class="faq-item" data-accordion-item>
            <h3>
              <button class="faq-item__q" type="button" data-accordion-trigger aria-expanded="false" aria-controls="faq-{i}">
                {x['question']}
                <span class="faq-item__icon" aria-hidden="true"></span>
              </button>
            </h3>
            <div class="faq-item__a" id="faq-{i}"><div><p>{x['answer']}</p></div></div>
          </div>''' for i, x in enumerate(fq['items']))}
        </div>
      </div>
    </section>
""")

    out.append(cta(c, d["cta"], secondary=("portfolio.html", d["cta"]["secondary"])))
    out.append("  </main>\n")
    out.append(footer(c))
    out.append(scripts(c))
    c.write("services.html", "".join(out))


# ---------------------------------------------------------------------------
# PORTFOLIO
# ---------------------------------------------------------------------------

def build_portfolio(c):
    d = load("portfolio")[c.lang]
    projects = load_projects()
    out = [head(c, "portfolio.html"), chrome(c), header(c, "portfolio.html")]
    out.append('  <main class="site-main" id="main">\n    <span id="top"></span>\n')

    out.append(page_header(c, d["crumb"], d["title"], d["lead"],
        f"""<div class="notice" data-reveal="up" data-delay="0.1">
          <svg class="notice__icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
            <circle cx="10" cy="10" r="8"/><path d="M10 9v5M10 6h.01"/>
          </svg>
          <p><strong>{d['notice_strong']}</strong> {d['notice']}</p>
        </div>""" if d.get("notice") else ""))

    filters = "".join(
        f'          <button class="filter-btn" type="button" data-filter="{f["key"]}" '
        f'aria-pressed="{"true" if f["key"] == "all" else "false"}">{f["label"]}</button>\n'
        for f in d["filters"])

    cards = []
    for i, p in enumerate(projects, start=1):
        loc = p[c.lang]
        slug, name = shared(p, "slug"), shared(p, "name")
        cats = " ".join(shared(p, "categories") or [])
        plain = _plain(loc["kind"])
        alt = (f"Ilustración conceptual de {name}, un proyecto de {plain}."
               if c.lang == "es" else f"Concept artwork for {name}, a {plain} project.")
        tags = "".join(f'<span class="tag">{x}</span>' for x in texts(loc["disciplines"]))
        cards.append(f"""          <article class="project-card" id="{slug}" data-categories="{cats}" data-reveal="up">
            <a href="{shared(p, 'url')}" target="_blank" rel="noopener noreferrer" class="project-card__media" data-reveal-media data-cursor="view" data-cursor-label="{VIEW[c.lang]}"
               aria-label="{name} — {plain}">
              {themed_img(c, shared(p, 'image_light'), shared(p, 'image_dark'), alt, 1200, 900)}
            </a>
            <div class="project-card__body">
              <div>
                <h2 class="project-card__title">{name}</h2>
                <p class="project-card__desc">{loc['description']}</p>
                <div class="work-item__tags u-mt-md">
                  <span class="tag tag--concept">{d['tag_concept']}</span>
                  {tags}
                </div>
              </div>
              <div class="project-card__meta">
                <span class="index-num">{i:02d}</span>
                <span class="index-num">{shared(p, 'year')}</span>
              </div>
            </div>
          </article>""")

    sh = d["ships"]
    out.append(f"""
    <!-- ============ 02 — PROJECT GRID ============ -->
    <section class="section section--flush-top">
      <div class="container">
        <h2 class="visually-hidden">{d['projects_h2']}</h2>

        <div class="filters" data-filters role="group" aria-label="{d['filter_label']}"
             data-count-one="{d['counter_one']}" data-count-many="{d['counter_many']}">
{filters}        </div>
        <p class="visually-hidden" role="status" aria-live="polite" data-filter-status></p>

        <div class="project-grid" data-project-grid>
{chr(10).join(cards)}
        </div>

        <p class="filter-empty" data-filter-empty hidden>
          {d['empty']} <button class="link-underline" type="button" data-filter-reset>{d['empty_link']}</button>
        </p>
      </div>
    </section>

    <!-- ============ 03 — WHAT SHIPS ============ -->
    <section class="section">
      <div class="container">
{section_head(sh['index'], sh['eyebrow'], sh['title'], sh['aside'])}
        <ul class="value-list">
{_value_list(sh['items'])}
        </ul>
      </div>
    </section>
""")

    out.append(cta(c, d["cta"], secondary=("services.html", d["cta"]["secondary"])))
    out.append("  </main>\n")
    out.append(footer(c))
    out.append(scripts(c))
    c.write("portfolio.html", "".join(out))


# ---------------------------------------------------------------------------
# CONTACT
# ---------------------------------------------------------------------------

def build_contact(c):
    d = load("contact")[c.lang]
    out = [head(c, "contact.html"), chrome(c), header(c, "contact.html")]
    out.append('  <main class="site-main" id="main">\n    <span id="top"></span>\n')

    # Hero with chat on right
    out.append(f"""
  <!-- ============ PAGE HEADER WITH CHAT ============ -->
  <header class="page-header" style="background-image: url('/images/hero/pr-background.jpg'); background-size: cover; background-position: center;">
    <div class="page-header__overlay" aria-hidden="true"></div>
    <div class="glow glow--primary page-header__glow" aria-hidden="true"></div>
    <div class="container">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:start;min-height:60vh">
        
        <!-- LEFT: Hero Content -->
        <div style="position:relative;z-index:3">
          <nav class="breadcrumb" aria-label="{'Ruta' if c.lang == 'es' else 'Breadcrumb'}">
            <a class="link-underline" href="index.html">{c.ui['breadcrumb_home']}</a>
            <span aria-hidden="true">/</span>
            <span aria-current="page">{d['crumb']}</span>
          </nav>
          <h1 class="display-1 page-header__title" data-split="words">{d['title']}</h1>
          <div class="page-header__grid" style="grid-template-columns:1fr;gap:var(--space-lg)">
            <p class="lead" style="max-width:48ch" data-reveal="up">{d['lead']}</p>
          </div>
        </div>

        <!-- RIGHT: Chat Widget -->
        <div style="display:flex;justify-content:center;align-items:flex-start;flex-direction:column;gap:1.5rem;position:relative;z-index:3">
          <iframe src="https://app.zaochat.com/widget/iframe/130aa379-9729-46f6-879e-55871e187ca4" title="Chat assistant" width="600" height="640" style="width:100%;max-width:600px;height:640px;border:0;border-radius:16px;overflow:hidden" loading="lazy" referrerpolicy="origin"></iframe>
        </div>

      </div>
    </div>
  </header>
""")
    
    out.append("  </main>\n")
    out.append(footer(c))
    out.append(scripts(c))
    c.write("contact.html", "".join(out))


# ---------------------------------------------------------------------------
# DEALS
# ---------------------------------------------------------------------------

def build_deals(c):
    d = load("deals")[c.lang]
    out = [head(c, "deals.html"), chrome(c), header(c, "deals.html")]
    out.append('  <main class="site-main" id="main">\n    <span id="top"></span>\n')

    # Add pricing to lead
    lead_html = f'{d["lead"]}<div class="deals-pricing" data-reveal="up" data-delay="0.1"><span class="deals-price-label">{d["price_label"]}</span> <span class="deals-price">{d["price"]}</span></div>'
    out.append(page_header(c, d["eyebrow"], d["title"], lead_html))

    # Build template cards with 2 columns
    cards = []
    for i, template in enumerate(d["templates"], start=1):
        cards.append(f"""          <article class="deal-card" data-reveal="up">
            <a href="{template['preview_url']}" target="_blank" rel="noopener noreferrer" class="deal-card__media">
              <img src="{template['image']}" alt="{template['title']}" width="600" height="400" loading="lazy"/>
            </a>
            <div class="deal-card__body">
              <span class="tag">{template['label']}</span>
              <h2 class="deal-card__title">{template['title']}</h2>
              <p class="deal-card__desc">{template['description']}</p>
              <a href="{template['preview_url']}" target="_blank" rel="noopener noreferrer" class="btn btn--small btn--ghost u-mt-md">
                <span>{"Ver sitio" if c.lang == "es" else "View Site"} →</span>
              </a>
            </div>
          </article>""")

    out.append(f"""
    <!-- ============ 02 — TEMPLATE GRID ============ -->
    <section class="section section--flush-top">
      <div class="container">
        <div class="deal-grid" data-reveal-group>
{chr(10).join(cards)}
        </div>
      </div>
    </section>
""")

    out.append(cta(c, d["cta"], primary=("tel:+19392299233", "Llamar ahora" if c.lang == "es" else "Call now"), 
                   secondary=("services.html", d["cta"]["secondary"])))
    out.append("  </main>\n")
    out.append(footer(c))
    out.append(scripts(c))
    c.write("deals.html", "".join(out))


# ---------------------------------------------------------------------------
# ARTICLES / BLOG
# ---------------------------------------------------------------------------

def build_articles(c):
    d = load("articles")[c.lang]
    out = [head(c, "articles.html"), chrome(c), header(c, "articles.html")]
    out.append('  <main class="site-main" id="main">\n    <span id="top"></span>\n')

    # Hero header
    out.append(page_header(c, d["crumb"], d["title"], d["lead"],
        f"""<div style="display:flex;flex-direction:column;gap:var(--space-sm)" data-reveal="up" data-delay="0.1">
          <p class="label label--plain"><span class="pulse-dot" aria-hidden="true"><i></i></span> {d['est']}</p>
          <p class="muted" style="font-size:var(--fs-sm)">{d['est_note']}</p>
        </div>"""))

    # Articles section
    articles = d.get("articles", [])
    
    if articles:
        out.append(f"""
    <!-- ============ ARTICLES GRID ============ -->
    <section class="section">
      <div class="container">
        <div class="article-grid">
""")
        for article in articles:
            pub_date = article.get("published_date", "")
            formatted_date = format_date(pub_date, c.lang)
            out.append(f"""          <article class="article-card" data-reveal="up">
            <a class="article-card__link" href="articles/{article.get('slug', '#')}.html">
              <h3 class="article-card__title">{article.get('title', '')}</h3>
              <p class="article-card__excerpt">{article.get('excerpt', '')}</p>
              <div class="article-card__meta">
                <span class="article-card__date">{formatted_date}</span>
                <span class="article-card__arrow">{ARROW}</span>
              </div>
            </a>
          </article>
""")
        out.append("""        </div>
      </div>
    </section>
""")
    else:
        out.append(f"""
    <!-- ============ NO ARTICLES YET ============ -->
    <section class="section">
      <div class="container container--narrow">
        <div style="text-align:center;padding:4rem 2rem">
          <p class="muted" style="font-size:var(--fs-lg);margin-bottom:2rem">{d['no_articles']}</p>
          <p class="muted">Check back soon for our first piece.</p>
        </div>
      </div>
    </section>
""")

    out.append("  </main>\n")
    out.append(footer(c))
    out.append(scripts(c))
    c.write("articles.html", "".join(out))


def build_article_pages(c):
    """Generate individual article detail pages for each article in articles.json.

    These live one folder below the language root (articles/<slug>.html), so
    everything is rendered inside `at_depth(1)` — that is what makes the
    stylesheet, the scripts and every nav link resolve from down there.
    """
    articles_data = load("articles")
    articles = articles_data[c.lang].get("articles", [])

    # Slugs that exist in the other language, so the language switch can fall
    # back to the articles index rather than a 404 for untranslated posts.
    other_lang = "en" if c.lang == "es" else "es"
    translated = {
        a.get("slug") for a in articles_data.get(other_lang, {}).get("articles", [])
        if a.get("slug")
    }

    for article in articles:
        slug = article.get("slug", "")
        if not slug:
            continue
        
        with c.at_depth(1):
            title = article.get("title", "")
            published_date = article.get("published_date", "")
            body = article.get("body", "")
            excerpt = article.get("excerpt", "")
        
            # Use Zao Flo's SEO fields if available; fallback to title/excerpt
            seo_title = article.get("seo_title", f"{title} — Web Designer Puerto Rico")
            seo_description = article.get("seo_description", excerpt if excerpt else title)
            seo_keywords = article.get("seo_keywords", "")
        
            page_path = f"articles/{slug}.html"
            other_path = page_path if slug in translated else "articles.html"

            out = [head(c, page_path, title=seo_title, description=seo_description, keywords=seo_keywords),
                   chrome(c),
                   header(c, page_path, other_page=other_path)]
            out.append('  <main class="site-main" id="main">\n    <span id="top"></span>\n')
        
            # Article header
            author = article_author(article, c)
            # The breadcrumb already ends in "Articles"; showing a category
            # label that says the same thing reads as a mistake.
            category = article.get("category", "")
            if category.strip().lower() == str(articles_data[c.lang]["crumb"]).strip().lower():
                category = ""
            date_display = format_date(published_date, c.lang)
            minutes = reading_minutes(body)

            avatar = c.media(author.get("avatar", ""))
            avatar_html = (
                f'<img class="byline__avatar" src="{avatar}" alt="{author.get("avatar_alt", "")}"'
                f' width="96" height="96" loading="eager" decoding="async">'
                if avatar else "")

            meta_bits = []
            if date_display:
                meta_bits.append(
                    f'<time datetime="{published_date}">{date_display}</time>')
            if minutes:
                meta_bits.append(f'<span>{minutes} {c.s.get("author", {}).get("read_label", "min read")}</span>')
            meta_html = '<span aria-hidden="true">&middot;</span>'.join(
                f'<span class="byline__meta-item">{b}</span>' for b in meta_bits)

            out.append(f"""
      <!-- ============ ARTICLE HERO ============ -->
      <header class="article-hero" style="background-image: url('{c.media('/images/hero/pr-background.jpg')}');">
        <div class="page-header__overlay" aria-hidden="true"></div>
        <div class="glow glow--primary page-header__glow" aria-hidden="true"></div>
        <div class="container container--narrow">
          <nav class="breadcrumb" aria-label="{c.ui.get('breadcrumb', 'Breadcrumb')}">
            <a class="link-underline" href="{c.link('index.html')}">{c.ui['breadcrumb_home']}</a>
            <span aria-hidden="true">/</span>
            <a class="link-underline" href="{c.link('articles.html')}">{articles_data[c.lang]['crumb']}</a>
          </nav>

          {f'<p class="label article-hero__category">{category}</p>' if category else ''}

          <h1 class="article-hero__title" data-split="words">{title}</h1>

          <div class="byline">
            {avatar_html}
            <div class="byline__text">
              <p class="byline__name">{author.get('name', '')}</p>
              {f'<p class="byline__role">{author.get("role", "")}</p>' if author.get("role") else ''}
              <p class="byline__meta">{meta_html}</p>
            </div>
          </div>
        </div>
      </header>

        <!-- ============ ARTICLE CONTENT ============ -->
        <section class="section section--flush-top" style="margin-top: 50px;">
          <div class="container" style="max-width: 1200px;">
            <div style="display: grid; grid-template-columns: 1fr 280px; gap: 3rem; align-items: start;">
              <!-- Main article -->
              <article class="prose">
                {f'<p style="font-size: 1.1rem; font-style: italic; color: var(--color-text-muted); margin-bottom: 2rem;">{excerpt}</p>' if excerpt else ''}
                {body}
              
                <div style="margin-top:4rem;padding-top:2rem;border-top:1px solid var(--color-line)">
                  <a class="btn btn--ghost" href="{c.link('articles.html')}"><span>{c.ui['back_to_top']} {ARROW}</span></a>
                </div>
              </article>

              <!-- Right sidebar -->
              <aside style="display: none; @media (min-width: 1024px) {{ display: block; }}">
                <div style="position: sticky; top: 2rem;">
                  <div style="margin-bottom: 2rem;">
                    <h3 style="font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: var(--color-text);">What We Do</h3>
                    <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.75rem;">
                      <li><a href="{c.link('services.html')}" class="link-underline" style="font-size: 0.95rem;">Web Design</a></li>
                      <li><a href="{c.link('services.html')}" class="link-underline" style="font-size: 0.95rem;">SEO Optimization</a></li>
                      <li><a href="{c.link('services.html')}" class="link-underline" style="font-size: 0.95rem;">WordPress Hosting</a></li>
                      <li><a href="{c.link('services.html')}" class="link-underline" style="font-size: 0.95rem;">Digital Marketing</a></li>
                      <li><a href="{c.link('services.html')}" class="link-underline" style="font-size: 0.95rem;">Content Strategy</a></li>
                    </ul>
                  </div>

                  <!-- Zao Chat Widget -->
                  <div style="border-radius: 8px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.1);">
                    <iframe src="https://flo.thexdigital.com/webdesignerpr" style="width: 100%; height: 500px; border: none; border-radius: 8px;" title="Chat with us"></iframe>
                  </div>
                </div>
              </aside>
            </div>
          </div>
        </section>
    """)
        
            out.append("  </main>\n")
            out.append(footer(c))
            out.append(scripts(c))
            c.write(f"articles/{slug}.html", "".join(out))



# ---------------------------------------------------------------------------
# SERVICE DETAIL PAGES
# ---------------------------------------------------------------------------

def build_service_pages(c):
    """Build individual service detail pages for each service."""
    doc = load("services")
    services = doc[c.lang].get("items", [])
    
    for service in services:
        service_id = service.get("id", "")
        if not service_id:
            continue
        
        out = [head(c, "services.html", title=service.get("title")), 
               chrome(c), 
               header(c, "services.html")]
        out.append('  <main class="site-main" id="main">\n    <span id="top"></span>\n')
        
        # Page header with service title
        out.append(page_header(c, 
            doc[c.lang]['crumb'], 
            service['title'], 
            service['summary']))
        
        # Service details section
        out.append(f"""
    <!-- ============ SERVICE DETAIL ============ -->
    <section class="section">
      <div class="container container--narrow">
        <div class="prose u-mb-lg">
          {service['body']}
        </div>
        
        <div>
          <p class="label u-mb-lg">{doc[c.lang]['included']}</p>
          <ul class="service-row__deliverables">
            {"".join(f"<li>{item['text']}</li>" for item in service['deliverables'])}
          </ul>
        </div>
        
        <div class="u-mt-lg">
          <a class="btn btn--primary" href="{c.link('contact.html')}"><span>{doc[c.lang]['enquire']} {ARROW}</span></a>
        </div>
      </div>
    </section>

    <!-- ============ RELATED SERVICES ============ -->
    <section class="section">
      <div class="container">
        <h2 class="display-3 u-mb-lg">{c.ui.get('related_services', 'Other Services')}</h2>
        <div class="card-grid">
          {"".join(f'''          <article class="card">
            <span class="index-num">{s['index']}</span>
            <div>
              <h3 class="card__title">{s['title']}</h3>
              <p class="card__text u-mt-sm">{s['summary']}</p>
            </div>
            <a class="link-arrow" href="{c.link(f'services/{s["id"]}.html')}">{c.ui.get('learn_more', 'Learn more')} {ARROW_R}</a>
          </article>''' for s in services if s.get('id') != service_id)}
        </div>
      </div>
    </section>
""")
        
        out.append(cta(c, doc[c.lang]['cta']))
        out.append("  </main>\n")
        out.append(footer(c))
        out.append(scripts(c))
        c.write(f"services/{service_id}.html", "".join(out))


BUILDERS = [build_home, build_about, build_services, build_portfolio, build_deals, build_contact, build_articles, build_service_pages]


# ---------------------------------------------------------------------------
# 404
#
# Served for any unmatched path, at any depth, so every URL here must be
# root-absolute rather than relative. Shows both languages because we cannot
# know which one the visitor was after.
# ---------------------------------------------------------------------------

def render_404():
    from .content import SITE_URL
    d = load("notfound")
    es, en = d["es"], d["en"]
    settings = load("settings")

    def block(loc, lang, home, work):
        return f"""        <div class="notfound__block" lang="{lang}">
          <h2 class="display-3">{loc['title']}</h2>
          <p class="prose u-mt-md">{loc['body']}</p>
          <div class="hero__actions u-mt-lg">
            <a class="btn btn--primary" href="{home}"><span>{loc['home']} {ARROW}</span></a>
            <a class="btn btn--ghost" href="{work}"><span>{loc['work']} {ARROW}</span></a>
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>404 &mdash; Web Designer Puerto Rico</title>
  <meta name="robots" content="noindex">
  <meta name="theme-color" content="#faf7f1" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#08090b" media="(prefers-color-scheme: dark)">
  <link rel="icon" href="/images/logo/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&amp;family=Inter+Tight:ital,wght@0,300;0,400;0,500;0,600;1,400&amp;family=JetBrains+Mono:wght@400;500&amp;display=swap">
  <link rel="stylesheet" href="/css/style.css">
  <link rel="stylesheet" href="/css/animations.css">
  <link rel="stylesheet" href="/css/responsive.css">
  <script>(function(){{try{{if(localStorage.getItem("wdpr:theme")==="dark")
document.documentElement.setAttribute("data-theme","dark")}}catch(e){{}}}})();</script>
</head>
<body>
  <div class="grain" aria-hidden="true"></div>

  <main class="notfound" id="main">
    <div class="glow glow--primary notfound__glow" aria-hidden="true"></div>
    <div class="container">
      <a class="brand" href="/" aria-label="Web Designer Puerto Rico">
        <svg class="brand__mark" viewBox="0 0 32 32" aria-hidden="true" style="color:var(--color-primary)">
          {MARK_PATH}
          <circle cx="16" cy="16" r="2.4" fill="var(--color-background)"/>
        </svg>
        <span class="brand__text">WebDesigner<em>PR</em></span>
      </a>

      <p class="display-mega notfound__code" aria-hidden="true">{es['code']}</p>
      <h1 class="visually-hidden">404 &mdash; {es['title']} / {en['title']}</h1>

      <div class="notfound__grid">
{block(es, 'es', '/', '/portfolio.html')}
{block(en, 'en', '/en/', '/en/portfolio.html')}
      </div>
    </div>
  </main>
</body>
</html>
"""
