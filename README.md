# WebDesignerPR

A custom website for **webdesignerpr.com** — an independent web design and
development studio. Hand-written HTML5, CSS3 and vanilla JavaScript with GSAP
for motion. No framework, no npm, no lockfile.

**Bilingual** — Spanish at the root, English in `/en/`.
**Two themes** — light by default, dark on a toggle that remembers the choice.
**Editable** — all copy, images and links are managed in Sveltia CMS at `/admin/`.

```bash
python3 build.py --serve     # build into dist/ and preview at localhost:4173
```

The entire toolchain is one standard-library Python script. That same command
is the Cloudflare Pages build command.

---

## Contents

1. [How it fits together](#how-it-fits-together)
2. [Creative direction](#creative-direction)
3. [Pages and languages](#pages-and-languages)
4. [Folder structure](#folder-structure)
5. [Running it locally](#running-it-locally)
6. [Editing content in the CMS](#editing-content-in-the-cms)
7. [Getting into the CMS](#getting-into-the-cms)
8. [Setting up Cloudflare — already done](#setting-up-cloudflare--already-done)
9. [Deployment](#deployment)
10. [Themes — how light and dark work](#themes--how-light-and-dark-work)
11. [Changing the colours](#changing-the-colours)
12. [Changing the typography](#changing-the-typography)
13. [Adding or removing a language](#adding-or-removing-a-language)
14. [Replacing the images](#replacing-the-images)
15. [Connecting the contact form](#connecting-the-contact-form)
16. [Content you must replace before launch](#content-you-must-replace-before-launch)
17. [How the animation layer works](#how-the-animation-layer-works)
18. [Accessibility](#accessibility)
19. [Performance notes](#performance-notes)
20. [Browser support](#browser-support)
21. [Credits and licensing](#credits-and-licensing)

---

## How it fits together

```
  content/*.json  ──►  build.py  ──►  dist/  ──►  Cloudflare Pages
       ▲                                              │
       │                                              ▼
  Sveltia CMS  ◄──────── commits to GitHub ────  webdesignerpr.com/admin/
```

1. Every word, image path and link on the site lives in `content/`, as JSON.
2. `build.py` renders those into the ten HTML pages and copies the static
   assets, producing `dist/`.
3. Cloudflare Pages runs that build on every push and publishes `dist/`.
4. The CMS at `/admin/` edits the files in `content/` and commits them to
   GitHub, which triggers step 3.

So **editing content never touches HTML**. And because the CMS commits to Git,
every change is an ordinary commit you can review, revert or blame.

If a build fails — a malformed edit, a missing field — Cloudflare keeps serving
the previous successful deployment. The site does not go down; the deploy just
shows as failed in the dashboard.

---

## Creative direction

**"Paper & Flamboyán."** The site reads like a printed design annual rather
than a SaaS landing page — in both themes.

| | Light (default) | Dark |
| --- | --- | --- |
| **Canvas** | Warm Paper `#faf7f1` | Midnight Ink `#08090b` |
| **Text** | Warm Ink `#14120e` | Bone `#f2efe9` |
| **Accent** | Flamboyán `#d63a19` | Flamboyán `#ff4d2e` |
| **Counterweight** | Sea Glass `#0c7f63`, Warm Sand `#8a6420` | Sea Glass `#6fe3c4`, Warm Sand `#e8c89a` |

The accent is the flame tree either way; the light theme uses a deeper shade
because the full-strength coral cannot carry white text at AA (see
[Changing the colours](#changing-the-colours)).

**Type** — **Instrument Serif** for display (italics as emphasis, not
decoration), **Inter Tight** for interface text, **JetBrains Mono** for indices,
labels and metadata.

**Structure** — an asymmetric editorial grid with fixed hairline column rules
and a numbered section index (`01 —`, `02 —`) running down every page.

**Motion** — masked line reveals, a pointer-reactive canvas lattice in the hero,
a pinned horizontal process track, magnetic buttons, a labelled custom cursor,
and film grain (which multiplies on light, screens on dark).

---

## Pages and languages

Spanish is the default and lives at the root. English mirrors it in `/en/`.
Filenames are identical in both, so `about.html` ↔ `en/about.html`.

| Page | Spanish | English |
| --- | --- | --- |
| Home | `/` | `/en/` |
| Studio / About | `/about.html` | `/en/about.html` |
| Services | `/services.html` | `/en/services.html` |
| Portfolio | `/portfolio.html` | `/en/portfolio.html` |
| Contact | `/contact.html` | `/en/contact.html` |

Each page declares the right `<html lang>`, a self-referencing `<link
rel="canonical">`, and three `hreflang` alternates (`es`, `en`, `x-default` →
Spanish). The `ES / EN` switch in the header links to **the same page** in the
other language, never back to the homepage.

Section content is the same across languages — only the words change.

---

## Folder structure

```
webdesignerpr/
│
├── content/              ← EVERYTHING EDITABLE. The CMS writes here.
│   ├── settings.json         Nav, footer, contact details, social, SEO titles
│   ├── home.json             Home page copy
│   ├── about.json            About page copy
│   ├── services.json         Services page copy + the seven services + FAQ
│   ├── portfolio.json        Portfolio page copy + filters
│   ├── contact.json          Contact page copy + form labels + messages
│   ├── process.json          The six process steps (used on two pages)
│   ├── capabilities.json     The tool grid
│   ├── testimonials.json     Quotes
│   ├── notfound.json         404 page copy
│   └── projects/             One file per project — add, remove, reorder
│       ├── marea.json
│       └── …
│
├── admin/                ← The CMS itself
│   ├── index.html            Loads Sveltia CMS
│   └── config.yml            Which fields are editable, in both languages
│
├── generator/            ← The build. Standard library only.
│   ├── content.py            Loads and normalises content/
│   ├── partials.py           Head, header, drawer, CTA, footer
│   └── pages.py              The five page templates
├── build.py              ← Entry point. `python3 build.py`
│
├── css/                  Design tokens (both themes), layout, components
│   ├── style.css
│   ├── animations.css
│   └── responsive.css
├── js/
│   ├── theme.js              Light/dark toggle, artwork swapping
│   ├── navigation.js         Header, mobile drawer, scroll progress
│   ├── main.js               Cursor, hero canvas, accordions, filters, form
│   └── animations.js         GSAP + ScrollTrigger
├── images/
│   ├── logo/ hero/ portfolio/ services/ backgrounds/
│   └── uploads/              ← Where CMS image uploads land
├── fonts/                Empty — see fonts/README.md for self-hosting
├── _headers              Cloudflare headers (keeps /admin/ out of search)
├── wrangler.jsonc        Pins the deploy to dist/ — see Deployment
│
└── dist/                 ← BUILD OUTPUT. Git-ignored. Never edit by hand.
```

Every file in `images/` (except uploads) exists twice: `name.svg` for the light
theme and `name-dark.svg` for dark.

**Do not edit anything in `dist/`.** It is deleted and regenerated on every
build. Edit `content/` for words and images, `css/` and `js/` for design and
behaviour, `generator/` for structure.

> There is also a `.claude/` folder with an editor launch config. Delete it if
> you do not want it in the repo; nothing depends on it.

## Running it locally

```bash
python3 build.py --serve
```

Builds into `dist/` and serves it at `http://localhost:4173`. Nothing to
install — Python 3.8+ and the standard library is the whole requirement.

`python3 build.py` on its own just builds. The build is deterministic: the same
content always produces byte-identical HTML.

**Editing content locally.** Open `http://localhost:4173/admin/` and choose
**"Work with Local Repository"**. Sveltia reads and writes the files in
`content/` directly through the browser's File System Access API — no GitHub
round-trip, no auth. Rebuild to see the result. (Chrome, Edge or another
Chromium browser; Firefox and Safari do not support that API yet, so use the
GitHub sign-in there.)

---

## Editing content in the CMS

Go to **https://webdesignerpr.com/admin/** and sign in — see
[Getting into the CMS](#getting-into-the-cms) for the ways to do that. Saving
commits to `main`, and Cloudflare republishes in about a minute.

The sidebar has four sections:

| Section | What's in it |
| --- | --- |
| **Pages** | All copy for Home, About, Services, Portfolio and Contact — headings, paragraphs, buttons, page images, SEO titles |
| **Projects** | One entry per portfolio project. Add, delete and reorder freely |
| **Shared content** | Process steps, the capabilities grid, testimonials — each used on more than one page |
| **Settings** | Navigation labels, footer, contact details, social links, page titles and descriptions, and every interface string |

### Both languages, side by side

Spanish and English live in the same entry. Use the locale switcher at the top
of the editor to move between them. Fields that are not language-specific —
image choices, slugs, years, categories — are shared automatically; change them
once and both languages follow.

### Some fields contain HTML, on purpose

Headings use inline markup for the coral italic accents:

```html
Diseño y código para marcas que se niegan a <em class="italic accent-text">ser una más</em>.
```

and entities like `&mdash;` (—) and `&middot;` (·). Keep those when editing. If
you delete the `<em>` tags the text still works, it just loses the accent.

### Adding a project

**Projects → New Project.** Fill in the name, slug, year, categories and both
artwork images, then the Spanish and English descriptions. `Order` sets the
position; `Show on the home page` decides whether it appears in the home list.

The slug becomes the filename and the anchor link (`portfolio.html#marea`), so
keep it lowercase with hyphens.

### Images

Upload through any image field; files land in `images/uploads/` and are
committed alongside the content. Every image has a **light** and a **dark**
variant — if you only have one, point both fields at the same file.

The existing artwork is SVG. Photographs work equally well; see
[Replacing the images](#replacing-the-images) for the sizes each slot expects.

### Removing the placeholder warnings

Two notices ship visible on purpose and each disappears when you clear its
fields:

- **Portfolio** → clear *Notice — bold lead* and *Notice — body* once the
  projects are real client work.
- **Home** → clear *06 — Testimonials heading → Placeholder badge* once the
  quotes are real. Also **Contact** → clear both *Developer notice* fields once
  the form has a backend.

---

## Getting into the CMS

Three ways in. Pick by how much setup you want.

### A. Locally — works right now, no setup

```bash
python3 build.py --serve
```

Open **http://localhost:4173/admin/** and click **"Work with Local
Repository"**. Pick this repo's folder when prompted. Sveltia reads and writes
`content/` straight off your disk — no GitHub, no sign-in, no tokens.

Rebuild (`python3 build.py`) to see your edits on the local site, then commit
the changed files yourself when you're happy.

Chromium browsers only (Chrome, Edge, Brave, Arc) — it uses the File System
Access API, which Firefox and Safari don't support yet.

### B. Live site with an access token — about five minutes

Open **https://webdesignerpr.com/admin/** and choose **"Sign In Using Access
Token"**. This skips the OAuth client completely.

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens**
   → **Fine-grained tokens** → **Generate new token**.
2. **Repository access**: Only select repositories → `zaoadonaiel/Webdesignerpr`.
3. **Repository permissions**: set **Contents** to **Read and write**. That is
   the only one required.
4. Set an expiry you're comfortable with, generate, and copy the token.
5. Paste it into the CMS when prompted.

The token is stored in your browser only. Treat it like a password — it grants
write access to the repository. Never paste it into a chat, an issue, or a
commit. When it expires, generate a new one and sign in again.

Good for a single editor. Saving commits straight to `main`, and the site
redeploys in about a minute.

### C. Live site with GitHub sign-in — best for a team

Proper OAuth: editors click "Sign In with GitHub" and never handle a token.
Worth doing once you have more than one person editing.

1. Deploy [sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth) to
   Cloudflare Workers (one-click from its README). Note the worker URL.
2. GitHub → **Settings** → **Developer settings** → **OAuth Apps** → **New
   OAuth App**.
   - **Homepage URL**: `https://webdesignerpr.com`
   - **Authorization callback URL**: your worker URL + `/callback`
3. Add `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` to the worker as encrypted
   environment variables.
4. Replace `base_url` in `admin/config.yml` with your worker URL — it currently
   reads `https://REPLACE-ME.workers.dev`, so GitHub sign-in fails until you
   change it.

Anyone with write access to the repository can then sign in.

---

## Setting up Cloudflare — already done

Recorded here in case it ever needs rebuilding.

The site deploys as a **Cloudflare Worker with static assets**, built by
Workers Builds. `wrangler.jsonc` pins the important parts:

```jsonc
"build":  { "command": "python3 build.py" },
"assets": { "directory": "dist", "not_found_handling": "404-page" }
```

Dashboard → Workers & Pages → `webdesignerpr` → Settings → Build:

| Setting | Value |
| --- | --- |
| Build command | `python3 build.py` |
| Deploy command | `npx wrangler deploy` |
| Root directory | *(empty)* |

The Workers build image ships Python 3.13; there is nothing to install.

> **Never delete `wrangler.jsonc`.** Without it, `wrangler deploy` guesses the
> output directory. Since the built HTML lives in git-ignored `dist/`, the only
> `index.html` in the repo is `admin/index.html` — so Wrangler publishes the
> CMS as the entire website. This actually happened once. Pinning
> `assets.directory` removes the guess.

---

## Deployment

Every push to `main` — including commits the CMS makes — triggers Workers
Builds, which runs `python3 build.py` and deploys `dist/` as the Worker's
static assets. Settings are in
[Setting up Cloudflare](#setting-up-cloudflare--already-done).

**Never commit `dist/`.** It is git-ignored and rebuilt on every deploy.
Committing it would let stale HTML shadow real content changes.

**Routing.** `html_handling: "auto-trailing-slash"` means `/about` and
`/about.html` both resolve. `not_found_handling: "404-page"` serves the
bilingual `404.html` for anything unmatched.

**Other hosts.** Anything that can run a command and serve a folder works:

| Host | Build command | Output |
| --- | --- | --- |
| Cloudflare Workers | `python3 build.py` | `dist` (via `wrangler.jsonc`) |
| Cloudflare Pages | `python3 build.py` | `dist` |
| Netlify / Vercel | `python3 build.py` | `dist` |
| Plain static hosting | run locally, upload `dist/` | — |

GitHub Pages needs an Actions workflow, since it will not run Python for you.

**If you change domain**, update `SITE_URL` in `generator/content.py`. It feeds
the canonical tags, `hreflang` alternates, Open Graph URLs and the sitemap in
one place.

---

## Themes — how light and dark work

- **Light is the default.** A first-time visitor always gets light, regardless
  of their operating system setting. That was a deliberate choice; see below to
  change it.
- The toggle writes `light` or `dark` to `localStorage` under `wdpr:theme`.
- A **tiny inline script in every `<head>`** reads that value and sets
  `<html data-theme="dark">` *before first paint*, so a returning dark-mode
  visitor never sees a flash of light.
- `js/theme.js` then syncs the button labels and swaps the artwork.
- During a switch, `theme-switching` is added to `<html>` for one frame to
  suppress colour transitions — otherwise components would cross-fade at
  different speeds and look messy.

### Making the theme follow the operating system instead

Replace the inline script in `head()` in `generator/partials.py` with:

```html
<script>(function(){try{var s=localStorage.getItem("wdpr:theme");
var d=s?s==="dark":matchMedia("(prefers-color-scheme: dark)").matches;
if(d)document.documentElement.setAttribute("data-theme","dark")}catch(e){}
document.documentElement.classList.add("js-ready")}());</script>
```

An explicit choice still wins; the OS preference only decides the first visit.

### Making dark the default instead

Swap the two colour blocks at the top of `css/style.css`: move the dark values
into `:root` and the light values into `:root[data-theme="light"]`, then flip
the attribute name in the inline script and in `js/theme.js`.

---

## Changing the colours

Both palettes live at the top of `css/style.css`. `:root` holds the light theme,
`:root[data-theme="dark"]` holds the dark one. Every colour on every page in
both languages reads from these.

```css
:root {                            /* LIGHT — the default */
  --color-background:   #faf7f1;   /* page canvas                       */
  --color-surface:      #ffffff;   /* cards and raised panels           */
  --color-surface-2:    #f1ebe0;   /* hover states                      */

  --color-text:         #14120e;   /* primary text                      */
  --color-text-muted:   #5f5b53;   /* body copy, captions               */
  --color-text-faint:   #736e64;   /* indices, metadata                 */

  --color-primary:      #d63a19;   /* the accent — fills and marks      */
  --color-primary-on-bg:#c0320f;   /* the accent as TEXT on the canvas  */
  --color-on-primary:   #ffffff;   /* text ON a coral fill              */

  --color-secondary:    #0c7f63;   /* focus rings, button hover fill    */
  --color-accent:       #8a6420;   /* notices, tertiary highlights      */
}
```

**The three brand tokens are separate on purpose.** One accent cannot serve as a
fill, as text on the page, and as a label on top of itself — not at AA. Keeping
`--color-primary`, `--color-primary-on-bg` and `--color-on-primary` distinct is
what lets the same flame-tree red work in both themes without dropping below
4.5:1 anywhere.

Below the palettes sit theme-dependent effect tokens — `--glow-primary`,
`--scrim`, `--grain-opacity`, `--grain-blend`, `--row-hover`, `--canvas-dot` and
friends. If you change the brand colour substantially, update these too; they
carry its RGB values for gradients and the hero canvas.

Two things still need a manual edit after a big colour change:

1. **The SVG artwork** has colours baked in — see
   [Replacing the images](#replacing-the-images).
2. **`<meta name="theme-color">`** in `head()` in `generator/partials.py` —
   there are two, one per colour scheme.

> **Check contrast after any colour change.** As shipped, every page in both
> languages and both themes clears WCAG AA: body text at 17.5:1, muted text at
> 6.3:1, the faintest metadata at 4.7:1, and button labels at 4.7:1. The light
> theme uses `#d63a19` rather than the full-strength `#ff4d2e` precisely
> because white on the brighter coral only reaches 4.35:1.

---

## Changing the typography

Also at the top of `css/style.css`, in the shared token block:

```css
--font-display: "Instrument Serif", "Iowan Old Style", Georgia, serif;
--font-sans:    "Inter Tight", -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono:    "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
```

Update the Google Fonts `<link>` in `head()` in `generator/partials.py` to
match, or self-host — full instructions in **`fonts/README.md`**.

All type sizes are fluid `clamp()` values in the same block (`--fs-mono` through
`--fs-mega`), scaling between a 360px and a 1600px viewport, so there are no
font-size overrides scattered through the breakpoints.

---

## Editing the copy

Use the CMS — see [Editing content in the CMS](#editing-content-in-the-cms).

If you would rather edit the files directly, they are plain JSON in `content/`,
with Spanish under `"es"` and English under `"en"`. Run `python3 build.py`
afterwards. The HTML in `dist/` is generated; editing it does nothing lasting.

Three strings are not in `content/` because they are structural rather than
editorial:

| What | Where |
| --- | --- |
| The `WebDesignerPR` wordmark and logo mark | `generator/partials.py`, `brand()` |
| The oversized footer wordmark | `generator/partials.py`, `footer()` |
| Service icons | `generator/pages.py`, `SVC_ICONS` — keyed by service ID |

---

## Adding or removing a language

**To remove English:** delete `"en"` from `LANGS` in `generator/content.py`,
drop the `en` locale from `admin/config.yml`, and remove the `.lang-switch`
block from `header()` and the drawer in `generator/partials.py`. Rebuild.

**To add a third language,** say Portuguese:

1. Add `"pt"` to `LANGS` in `generator/content.py`.
2. Add `pt` to `locales` in `admin/config.yml`.
3. In each `content/*.json`, add a `"pt"` key alongside `"es"` and `"en"` —
   easiest by copying the `"en"` block and translating it.
4. Add a third link to `lang_switch()` in `generator/partials.py`.

The build writes any non-default language into its own folder (`/pt/`) and
resolves asset paths with `../` automatically, so nothing else changes. The
`hreflang` alternates and the sitemap pick the new locale up on their own.

---

## Replacing the images

Every image is set in the CMS. Upload through any image field and the file is
committed to `images/uploads/` alongside the content change.

Each slot has a **light** and a **dark** variant. If you only have one version,
point both fields at the same file — nothing breaks, the artwork simply does
not change with the theme.

| Slot | Size | Where in the CMS |
| --- | --- | --- |
| Project artwork | 1200 × 900 (4:3) | Projects → *each project* |
| Studio plate | 900 × 1125 (4:5) | Pages → Home → 01 Studio, and Pages → About |
| Design-system plate | 900 × 1125 (4:5) | Pages → About → 03 Mission & vision |
| Typographic plate | 900 × 1125 (4:5) | Pages → About → 04 Design philosophy |
| Performance / Commerce | 1200 × 675 (16:9) | Pages → Services |

Three images are **not** in the CMS because they are brand assets rather than
content — replace the files directly:

- `images/logo/favicon.svg`
- `images/logo/og-image.jpg` — the social share card, 1200 × 630. Its editable
  source is `og-image.svg` beside it; `og-image-dark.svg` is the dark variant.
- `images/hero/orbit.svg` / `orbit-dark.svg` — the rings behind every CTA.

The logo mark itself is inlined into the markup so it can follow the theme
colour. To change it, edit the `<path>` in `MARK_PATH` in
`generator/partials.py`.

**Alt text is a separate field next to each image, and it is translatable.**
Write it. Decorative images (grain, glows, the orbit) are already `aria-hidden`
and correctly have none.

### Why the artwork is SVG

The eight project posters and the editorial plates were drawn for this project
as SVG: a few kilobytes each, sharp at any size, no stock licensing, nothing
that can 404. Photographs work fine in the same slots — they will be cropped to
the ratios above and lazy-loaded the same way.

---

## Connecting the contact form

**The form is frontend-only.** Validation runs fully in the browser — required
fields, email format, minimum message length, budget selection — but **nothing
is delivered anywhere**. A visible notice under the form says exactly that, in
both languages, and the success message repeats it.

Two halves to connecting it: a small template change, and the wording, which
lives in the CMS under **Pages → Contact → Validation messages**. Clear the
*Developer notice* fields there once it is live.

### Option 1 — Formspree (no server needed)

1. Create a form at [formspree.io](https://formspree.io) and copy your form ID.
2. In `generator/pages.py`, find `build_contact` and add the action to the
   `<form>` tag:

   ```python
   <form class="form" data-contact-form novalidate
         action="https://formspree.io/f/YOUR_FORM_ID" method="POST" {msgs}>
   ```

   Keep `{msgs}` — it carries the translated validation messages from the CMS.

3. In `js/main.js`, find the `contactForm` block and replace the simulated
   submission (the `window.setTimeout` near the end) with a real request:

   ```js
   fetch(form.action, {
     method: "POST",
     body: new FormData(form),
     headers: { Accept: "application/json" }
   })
     .then(function (res) {
       if (!res.ok) throw new Error("Request failed");
       form.reset();
       status.className = "form-status form-status--success is-visible";
       status.innerHTML = "<strong>" + msg("sent-strong", "Thank you.") + "</strong>" +
                          msg("sent", " We'll reply within one business day.");
     })
     .catch(function () {
       status.className = "form-status form-status--error is-visible";
       status.innerHTML = "<strong>" + msg("fail-strong", "That didn't send.") + "</strong>" +
                          msg("fail", " Please email hola@webdesignerpr.com instead.");
     })
     .finally(function () { submit.disabled = false; });
   ```

   Then add `data-msg-sent`, `data-msg-sent-strong`, `data-msg-fail` and
   `data-msg-fail-strong` to the `<form>` in each language, the same way the
   existing messages work.

### Option 2 — Netlify Forms

If you host on Netlify, add two attributes and Netlify handles the rest:

```html
<form class="form" data-contact-form novalidate name="enquiry" netlify netlify-honeypot="bot-field">
  <input type="hidden" name="form-name" value="enquiry">
  <p hidden><label>Leave blank: <input name="bot-field"></label></p>
```

Give the Spanish and English forms **different `name` values** — in
`generator/pages.py` use `f'name="enquiry-{c.lang}"'` — so submissions arrive
separated by language. Then remove the
`e.preventDefault()` in `js/main.js` so the browser posts natively once
validation passes.

### Option 3 — your own endpoint

Point `action` at your handler and use the `fetch` snippet from Option 1. The
field names posted are: `name`, `email`, `company`, `projectType`, `budget`,
`details`. Consider also posting the page language so replies go out in the
right one.

**Whichever you choose:** add server-side validation and spam protection.
Browser validation is a courtesy to your visitors, not a security control —
anything posted to your endpoint can be forged.

---

## Content you must replace before launch

All of this is editable in the CMS, in both languages.

| What | Where in the CMS | Why |
| --- | --- | --- |
| **Testimonials** | Shared content → Testimonials | Three placeholders attributed to "Nombre del cliente / Contenido de muestra". Replace them, then clear Pages → Home → *06 Testimonials → Placeholder badge* to remove the visible sample warning. Never publish invented testimonials as real ones. |
| **Portfolio projects** | Projects | All eight are self-initiated concepts using fictional brands. Each shows a `CONCEPTO` / `CONCEPT` tag. Replace with real work, then clear both *Notice* fields on Pages → Portfolio. |
| **Phone number** | Settings → Contact details | `+1 (787) 555-0142` is a reserved fictional number. Also clear the "placeholder" wording in Pages → Contact → Contact details. |
| **Email address** | Settings → Contact details | `hola@webdesignerpr.com` |
| **Street address** | Pages → Contact → Contact details | "Calle Loíza, San Juan" is indicative. |
| **Social links** | Settings → Social links | Three `#` placeholders. |
| **Studio claims** | Pages → About | "Est. 2016", "nine years", and the counters are illustrative. Make them true or change them. |
| **Standards figures** | Pages → Home → 01 Studio → Standards figures | 95+ Lighthouse, 1.5s LCP, 100% custom, WCAG AA. Written as commitments you build against, not past results — keep them that way, or replace with numbers you can evidence. |

---

## How the animation layer works

**Three layers, each degrading into the one below.**

1. **GSAP + ScrollTrigger** (from cdnjs, deferred) drives reveals, parallax, the
   pinned horizontal process track, counters and magnetic buttons.
2. **If GSAP fails to load** — offline, blocked CDN, corporate proxy —
   `js/animations.js` detects it, adds `.no-gsap` to `<html>`, and the CSS
   fallback in `animations.css` reveals all content with a simple fade-up. The
   horizontal process track becomes a native scroll-snap swipe strip.
3. **If JavaScript is off entirely**, a `<noscript>` block in each `<head>`
   neutralises the pre-animation states so nothing is left invisible. (The theme
   toggle needs JavaScript; without it the site stays light, which is the
   default anyway.)

**Content is never hidden behind an animation that might not run.** That is the
single rule the whole layer is built around.

### Reduced motion

`prefers-reduced-motion: reduce` is honoured properly. Everything appears at
once, and these are all disabled: the grain drift, the custom cursor, the hero
canvas, the marquee, the cursor-follow preview, the parallax, the pulsing
availability dot, the rotating stamp, and the pinned horizontal scroll (which
becomes a normal swipe strip). The theme toggle keeps working.

### Adding scroll animations to new markup

```html
<!-- fade and rise on entry; direction: up | down | left | right | scale | fade -->
<div data-reveal="up" data-delay="0.1">…</div>

<!-- cascade every direct child -->
<ul data-stagger="0.08"> <li>…</li> <li>…</li> </ul>

<!-- word-by-word heading reveal -->
<h2 data-split="words">Your heading</h2>

<!-- character reveal; short strings only -->
<span data-split="chars">2026</span>

<!-- masked image reveal -->
<div class="media-frame" data-reveal-media><img src="…" alt="…"></div>

<!-- parallax; 0.1 is subtle, 0.3 is strong. Desktop only, capped at ±140px -->
<img data-parallax="0.12" src="…" alt="…">

<!-- counter -->
<span data-counter="95" data-suffix="+" data-decimals="0">0</span>

<!-- magnetic hover; the value is the pull strength -->
<a class="btn btn--primary" href="#" data-magnetic="0.3"><span>Label</span></a>

<!-- custom cursor label on hover -->
<a href="#" data-cursor="view" data-cursor-label="Ver">…</a>
```

---

## Accessibility

Verified across all ten pages in both themes:

- **Semantic landmarks** — one `<header>`, `<main>` and `<footer>` per page,
  every `<nav>` labelled, exactly one `<h1>` per page, no skipped heading levels.
- **Correct `lang`** on every page, with `hreflang` alternates, and `lang`
  attributes on the individual `ES` / `EN` switch links so screen readers
  pronounce them correctly.
- **Skip link** as the first focusable element on every page.
- **Visible focus** — a 2px Sea Glass outline with 3px offset, never removed.
- **Keyboard** — the mobile drawer traps Tab (including the close button),
  closes on Escape, and returns focus to the button that opened it. No positive
  `tabindex` anywhere.
- **Touch targets** — every interactive element is at least 44px tall on phones,
  including the theme and language controls.
- **Colour contrast** — WCAG AA on every page, in both languages and both
  themes. See the note under [Changing the colours](#changing-the-colours).
- **Theme toggle** — a real `<button>` with `aria-pressed` and a label that
  changes with state ("Cambiar a modo oscuro" / "Switch to light theme").
- **Language switch** — two links, with `aria-current="true"` on the active one.
- **Forms** — real `<label>` elements, `aria-describedby` wired to error
  messages, `aria-invalid` on failure, `role="alert"` on each error slot, focus
  moved to the first invalid field on submit, and a `role="status"` live region
  for the result — all translated.
- **Decorative imagery** — grain, glows, column rules, the orbit, the marquee
  and cursor preview plates are all `aria-hidden`.

---

## Performance notes

- **No framework, no build step, no runtime dependencies** beyond GSAP (~70KB
  gzipped, deferred, from a CDN).
- **All artwork is SVG** — a few kilobytes each, resolution-independent. Both
  theme variants exist, but only the active one is ever fetched.
- **Lazy loading** on every below-the-fold image, with explicit `width`/`height`
  to prevent layout shift.
- **The hero canvas** scales its lattice density to the viewport, stops painting
  when scrolled out of view or when the tab is hidden, and never starts under
  reduced motion. It re-reads its colours from the theme tokens on switch.
- **Scroll handlers** are throttled to one `requestAnimationFrame` per frame and
  registered `{ passive: true }`.
- **Parallax is desktop-only** and capped at ±140px.
- **`font-display: swap`** via Google Fonts, with real system fallbacks.

One known trade-off: a returning **dark-mode** visitor may briefly see the light
version of an above-the-fold image, because `theme.js` swaps `src` after the
HTML parses. The page chrome itself never flashes — that is handled before first
paint by the inline script. Most themed images are below the fold and lazy, so
in practice this is rarely visible.

If you add third-party scripts (chat widgets, tag managers, pixels), load them
`async` or `defer` and re-measure. They are by far the most common cause of a
fast site becoming a slow one.

---

## Browser support

Chrome, Edge, Firefox, Safari — current and previous major versions, desktop and
mobile. The layout relies on CSS Grid, custom properties, `clamp()`,
`aspect-ratio`, `clip-path` and `color-mix()`, all baseline for years.

Internet Explorer is not supported.

---

## Credits and licensing

- **Typefaces** — Instrument Serif, Inter Tight and JetBrains Mono, all under
  the SIL Open Font License 1.1.
- **GSAP + ScrollTrigger** 3.12.5 from cdnjs. Free under GreenSock's standard
  licence for this use; see [gsap.com/licensing](https://gsap.com/licensing/) if
  you resell the site as part of a product.
- **All imagery** was drawn specifically for this project as SVG. No stock
  photos, no external image URLs, nothing to attribute.
- **Icons** are inline SVG, hand-drawn for this project.

Site code © WebDesignerPR.
