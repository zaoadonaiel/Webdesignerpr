/* ==========================================================================
   WebDesignerPR — Theme
   Light is the default. Dark is opt-in, remembered per visitor, and applied
   to <html data-theme="dark">.

   The very first paint is handled by a tiny inline script in each <head>,
   so a returning dark-mode visitor never sees a flash of light. This file
   handles the toggle itself, the control's labels, and swapping any artwork
   that ships in two variants.
   ========================================================================== */

(function () {
  "use strict";

  var KEY = "wdpr:theme";
  var root = document.documentElement;
  var doc = document;

  var WDPR = (window.WDPR = window.WDPR || {});

  /* ------------------------------------------------------------------
     Read / write the stored preference. Private browsing can throw on
     localStorage access, so every call is guarded.
     ------------------------------------------------------------------ */

  function readStored() {
    try {
      return window.localStorage.getItem(KEY);
    } catch (e) {
      return null;
    }
  }

  function writeStored(value) {
    try {
      window.localStorage.setItem(KEY, value);
    } catch (e) {
      /* nothing we can do — the toggle still works for this page view */
    }
  }

  function current() {
    return root.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }

  /* ------------------------------------------------------------------
     Artwork shipped in two variants.
     <img src="…marea.svg" data-src-light="…marea.svg" data-src-dark="…marea-dark.svg">
     ------------------------------------------------------------------ */

  function swapArtwork(theme) {
    var attr = theme === "dark" ? "data-src-dark" : "data-src-light";

    Array.prototype.forEach.call(doc.querySelectorAll("[data-src-dark]"), function (img) {
      var next = img.getAttribute(attr);
      if (!next) return;
      // Compare resolved URLs so we don't reassign the same file
      if (img.getAttribute("src") !== next) img.setAttribute("src", next);
    });
  }

  /* ------------------------------------------------------------------
     Toggle buttons — label and pressed state follow the active theme.
     Strings come from the markup so each language ships its own.
     ------------------------------------------------------------------ */

  function syncControls(theme) {
    Array.prototype.forEach.call(doc.querySelectorAll("[data-theme-toggle]"), function (btn) {
      var toDark = theme !== "dark";
      var label = btn.getAttribute(toDark ? "data-label-to-dark" : "data-label-to-light");

      btn.setAttribute("aria-pressed", String(theme === "dark"));
      if (label) {
        btn.setAttribute("aria-label", label);
        btn.setAttribute("title", label);
      }
    });
  }

  /* ------------------------------------------------------------------
     Apply
     ------------------------------------------------------------------ */

  function apply(theme, persist, animate) {
    // Suppress colour transitions for one frame so the whole page flips at
    // once instead of cross-fading component by component.
    if (animate !== false) {
      root.classList.add("theme-switching");
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          root.classList.remove("theme-switching");
        });
      });
    }

    if (theme === "dark") {
      root.setAttribute("data-theme", "dark");
    } else {
      root.removeAttribute("data-theme");
    }

    swapArtwork(theme);
    syncControls(theme);

    if (persist) writeStored(theme);

    // Anything that samples CSS colours at runtime (the hero canvas) listens
    // for this rather than polling.
    doc.dispatchEvent(new CustomEvent("wdpr:themechange", { detail: { theme: theme } }));
  }

  WDPR.getTheme = current;
  WDPR.setTheme = function (theme) { apply(theme === "dark" ? "dark" : "light", true); };

  /* ------------------------------------------------------------------
     Wire up
     ------------------------------------------------------------------ */

  // The inline head script already set the attribute; this aligns the rest
  // of the UI (labels, artwork) with it without a second paint.
  apply(readStored() === "dark" ? "dark" : current(), false, false);

  Array.prototype.forEach.call(doc.querySelectorAll("[data-theme-toggle]"), function (btn) {
    btn.addEventListener("click", function () {
      apply(current() === "dark" ? "light" : "dark", true);
    });
  });

  /* ------------------------------------------------------------------
     Language: remember the visitor's last choice so the root URL can point
     a returning English reader at /en/ on their next visit. Only ever acts
     on an explicit click — it never auto-redirects on first arrival.
     ------------------------------------------------------------------ */

  Array.prototype.forEach.call(doc.querySelectorAll("[data-lang-switch]"), function (link) {
    link.addEventListener("click", function () {
      try {
        window.localStorage.setItem("wdpr:lang", link.getAttribute("data-lang-switch"));
      } catch (e) {}
    });
  });
})();
