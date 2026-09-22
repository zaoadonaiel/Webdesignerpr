# Fonts

This folder is intentionally empty. The site currently loads its three typefaces
from **Google Fonts** via a single stylesheet request in the `<head>` of every page:

| Role | Family | Notes |
| --- | --- | --- |
| Display | **Instrument Serif** | Regular + italic only — that is the whole family |
| Interface | **Inter Tight** | Weights 300, 400, 500, 600 + italic 400 |
| Mono / labels | **JetBrains Mono** | Weights 400, 500 |

All three are licensed under the **SIL Open Font License 1.1**, so they are free for
commercial use and may be self-hosted.

---

## Switching to self-hosted fonts

Self-hosting removes a third-party request, eliminates the Google Fonts DNS lookup,
and is usually required for strict GDPR compliance in the EU.

**1. Download the families**

Grab the `.woff2` files from [google-webfonts-helper](https://gwfh.mranftl.com/fonts)
(select `latin` and `latin-ext` subsets) and drop them in this folder:

```
fonts/
├── instrument-serif-400.woff2
├── instrument-serif-400-italic.woff2
├── inter-tight-300.woff2
├── inter-tight-400.woff2
├── inter-tight-500.woff2
├── inter-tight-600.woff2
└── jetbrains-mono-400.woff2
```

**2. Remove the Google Fonts request**

Delete these three lines from the `<head>` of all **ten** HTML files
(five Spanish at the root, five English in `/en/`):

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif...">
```

**3. Add `@font-face` rules at the top of `css/style.css`**

Place these *above* the `:root` block:

```css
@font-face {
  font-family: "Instrument Serif";
  src: url("../fonts/instrument-serif-400.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "Instrument Serif";
  src: url("../fonts/instrument-serif-400-italic.woff2") format("woff2");
  font-weight: 400;
  font-style: italic;
  font-display: swap;
}
@font-face {
  font-family: "Inter Tight";
  src: url("../fonts/inter-tight-400.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
/* …repeat for 300, 500, 600 and JetBrains Mono 400 */
```

**4. Preload the two fonts used above the fold**

Add to `<head>`, after the favicon links. Note the path differs by language —
English pages sit one level down:

```html
<!-- Spanish pages at the root -->
<link rel="preload" href="fonts/instrument-serif-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/inter-tight-400.woff2" as="font" type="font/woff2" crossorigin>

<!-- English pages in /en/ -->
<link rel="preload" href="../fonts/instrument-serif-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../fonts/inter-tight-400.woff2" as="font" type="font/woff2" crossorigin>
```

Nothing else changes — `--font-display`, `--font-sans` and `--font-mono` in
`css/style.css` already reference these family names.

---

## Swapping in different typefaces entirely

Change the three variables at the top of `css/style.css` and nothing else:

```css
--font-display: "Your Display Face", Georgia, serif;
--font-sans:    "Your UI Face", -apple-system, sans-serif;
--font-mono:    "Your Mono Face", ui-monospace, monospace;
```

Keep a real fallback in each stack. If you replace Instrument Serif with a face of
noticeably different proportions, re-check the `--fs-*` clamp values in the same
block — the display sizes are tuned to a high-contrast serif.
