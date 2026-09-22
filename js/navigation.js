/* ==========================================================================
   WebDesignerPR — Navigation
   Header states, mobile drawer, scroll progress, footer housekeeping.
   Runs standalone: no dependency on GSAP.
   ========================================================================== */

(function () {
  "use strict";

  var doc = document;
  var root = doc.documentElement;

  /* ------------------------------------------------------------------
     Shared namespace so the other scripts can read shared state.
     ------------------------------------------------------------------ */
  var WDPR = (window.WDPR = window.WDPR || {});
  WDPR.reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  WDPR.finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  /* ------------------------------------------------------------------
     1. HEADER — condense on scroll, hide going down, reveal going up
     ------------------------------------------------------------------ */

  var header = doc.querySelector(".site-header");
  var progress = doc.querySelector(".scroll-progress");
  var lastY = window.scrollY;
  var ticking = false;

  function onScroll() {
    var y = window.scrollY;
    var max = doc.documentElement.scrollHeight - window.innerHeight;

    if (header) {
      header.classList.toggle("is-scrolled", y > 24);

      // Only hide once we're clear of the hero, and never while the menu is open
      var menuOpen = doc.body.classList.contains("is-locked");
      if (!menuOpen && y > 400 && y > lastY + 6) {
        header.classList.add("is-hidden");
      } else if (y < lastY - 6 || y <= 400) {
        header.classList.remove("is-hidden");
      }
    }

    if (progress) {
      progress.style.transform = "scaleX(" + (max > 0 ? Math.min(y / max, 1) : 0) + ")";
    }

    lastY = y;
    ticking = false;
  }

  window.addEventListener(
    "scroll",
    function () {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(onScroll);
      }
    },
    { passive: true }
  );
  onScroll();

  /* ------------------------------------------------------------------
     2. MOBILE DRAWER
     ------------------------------------------------------------------ */

  var toggle = doc.querySelector(".menu-toggle");
  var menu = doc.getElementById("mobile-menu");
  var menuLinks = menu ? menu.querySelectorAll("a, button") : [];
  var lastFocused = null;

  function setMenu(open) {
    if (!menu || !toggle) return;

    menu.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    doc.body.classList.toggle("is-locked", open);
    menu.setAttribute("aria-hidden", String(!open));

    // Stagger the link reveals via transition-delay
    Array.prototype.forEach.call(menu.querySelectorAll(".mobile-menu__link"), function (el, i) {
      el.style.transitionDelay = open ? 0.12 + i * 0.06 + "s" : "0s";
    });

    if (open) {
      lastFocused = doc.activeElement;
      header && header.classList.remove("is-hidden");
      // Move focus into the drawer for keyboard and screen-reader users
      window.setTimeout(function () {
        var first = menu.querySelector("a");
        first && first.focus();
      }, 320);
    } else if (lastFocused) {
      lastFocused.focus();
      lastFocused = null;
    }
  }

  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });

    Array.prototype.forEach.call(menuLinks, function (link) {
      link.addEventListener("click", function () {
        setMenu(false);
      });
    });

    // Escape closes; Tab is trapped inside the drawer while it's open
    doc.addEventListener("keydown", function (e) {
      if (!menu.classList.contains("is-open")) return;

      if (e.key === "Escape") {
        setMenu(false);
        return;
      }

      if (e.key === "Tab") {
        // The close button lives outside the drawer, so splice it into the
        // cycle — otherwise a keyboard user can never reach it.
        var focusables = [toggle].concat(
          Array.prototype.slice.call(menu.querySelectorAll('a[href], button:not([disabled])'))
        );
        if (focusables.length < 2) return;
        var first = focusables[0];
        var last = focusables[focusables.length - 1];

        if (e.shiftKey && doc.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && doc.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    });

    // Leaving the mobile breakpoint mid-session shouldn't strand a locked body
    var mq = window.matchMedia("(min-width: 769px)");
    var onChange = function (e) {
      if (e.matches && menu.classList.contains("is-open")) setMenu(false);
    };
    mq.addEventListener ? mq.addEventListener("change", onChange) : mq.addListener(onChange);
  }

  /* ------------------------------------------------------------------
     3. ACTIVE LINK — marks the current page in both navs
     ------------------------------------------------------------------ */

  (function markCurrent() {
    var here = window.location.pathname.split("/").pop() || "index.html";
    Array.prototype.forEach.call(doc.querySelectorAll("[data-nav-link]"), function (link) {
      var target = link.getAttribute("href");
      if (!target) return;
      if (target === here || (here === "index.html" && target === "index.html")) {
        link.setAttribute("aria-current", "page");
      }
    });
  })();

  /* ------------------------------------------------------------------
     4. SMOOTH IN-PAGE ANCHORS (honours reduced motion)
     ------------------------------------------------------------------ */

  Array.prototype.forEach.call(doc.querySelectorAll('a[href^="#"]'), function (link) {
    link.addEventListener("click", function (e) {
      var id = link.getAttribute("href");
      if (!id || id === "#") return;
      var target = doc.querySelector(id);
      if (!target) return;

      e.preventDefault();
      var top = target.getBoundingClientRect().top + window.scrollY - 100;
      window.scrollTo({ top: top, behavior: WDPR.reducedMotion ? "auto" : "smooth" });

      // Keep the keyboard focus in sync with the visual jump
      target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
    });
  });

  /* ------------------------------------------------------------------
     5. FOOTER HOUSEKEEPING
     ------------------------------------------------------------------ */

  Array.prototype.forEach.call(doc.querySelectorAll("[data-year]"), function (el) {
    el.textContent = new Date().getFullYear();
  });

  Array.prototype.forEach.call(doc.querySelectorAll("[data-to-top]"), function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: WDPR.reducedMotion ? "auto" : "smooth" });
    });
  });
})();
