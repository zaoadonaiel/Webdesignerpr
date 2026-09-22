/* ==========================================================================
   WebDesignerPR — Animations
   GSAP + ScrollTrigger choreography.

   Graceful degradation is the rule here: if GSAP is unavailable or the
   visitor prefers reduced motion, <html> gets `.no-gsap` and the CSS in
   animations.css takes over. Content is never left hidden.
   ========================================================================== */

(function () {
  "use strict";

  var doc = document;
  var root = doc.documentElement;
  var WDPR = (window.WDPR = window.WDPR || {});
  var reduced = WDPR.reducedMotion;

  var hasGSAP = typeof window.gsap !== "undefined";
  var hasST = hasGSAP && typeof window.ScrollTrigger !== "undefined";

  /* ------------------------------------------------------------------
     BAIL-OUT PATH
     ------------------------------------------------------------------ */
  if (!hasGSAP || !hasST || reduced) {
    root.classList.add("no-gsap");
    var loaderEl = doc.querySelector(".loader");
    if (loaderEl) loaderEl.remove();
    doc.body.classList.remove("is-locked");
    return;
  }

  var gsap = window.gsap;
  var ScrollTrigger = window.ScrollTrigger;
  gsap.registerPlugin(ScrollTrigger);

  gsap.defaults({ ease: "power3.out", duration: 1 });
  ScrollTrigger.config({ ignoreMobileResize: true });

  /* ==================================================================
     1. TEXT SPLITTING
     Wraps every word in a span so headings can cascade. Inline markup
     (<em>, <span>) survives because we only ever rewrite text nodes.
     ================================================================== */

  function splitWords(el) {
    if (el.dataset.splitDone === "true") return el.querySelectorAll(".split-word");

    var walker = doc.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
    var textNodes = [];
    var node;
    while ((node = walker.nextNode())) {
      if (node.nodeValue.trim()) textNodes.push(node);
    }

    textNodes.forEach(function (text) {
      var frag = doc.createDocumentFragment();
      var parts = text.nodeValue.split(/(\s+)/);

      parts.forEach(function (part) {
        if (!part) return;
        if (/^\s+$/.test(part)) {
          frag.appendChild(doc.createTextNode(part));
        } else {
          var span = doc.createElement("span");
          span.className = "split-word";
          span.textContent = part;
          frag.appendChild(span);
        }
      });

      text.parentNode.replaceChild(frag, text);
    });

    el.dataset.splitDone = "true";
    return el.querySelectorAll(".split-word");
  }

  function splitChars(el) {
    if (el.dataset.splitDone === "true") return el.querySelectorAll(".split-char");

    var source = el.textContent;
    el.textContent = "";
    // Keep the original string available to screen readers as one label
    el.setAttribute("aria-label", source);

    source.split("").forEach(function (ch) {
      var span = doc.createElement("span");
      span.className = "split-char";
      span.setAttribute("aria-hidden", "true");
      span.textContent = ch === " " ? " " : ch;
      el.appendChild(span);
    });

    el.dataset.splitDone = "true";
    return el.querySelectorAll(".split-char");
  }

  /* ==================================================================
     2. PRELOADER
     Short by design — a beat of intent, not a gate. Skipped entirely on
     in-session navigation so moving between pages stays instant.
     ================================================================== */

  function runLoader(onDone) {
    var loader = doc.querySelector(".loader");
    if (!loader) return onDone();

    doc.body.classList.add("is-locked");

    var seen = false;
    try {
      seen = window.sessionStorage.getItem("wdpr:visited") === "1";
      window.sessionStorage.setItem("wdpr:visited", "1");
    } catch (e) {
      /* private mode — just show the loader */
    }

    if (seen) {
      loader.remove();
      doc.body.classList.remove("is-locked");
      return onDone();
    }

    var bar = loader.querySelector(".loader__bar i");
    var count = loader.querySelector(".loader__count");
    var word = loader.querySelector(".loader__word");
    var counter = { v: 0 };

    var tl = gsap.timeline({
      onComplete: function () {
        loader.remove();
        doc.body.classList.remove("is-locked");
        ScrollTrigger.refresh();
      }
    });

    tl.from(word, { yPercent: 110, opacity: 0, duration: 0.6, ease: "power4.out" })
      .to(bar, { width: "100%", duration: 0.85, ease: "power2.inOut" }, 0.1)
      .to(counter, {
        v: 100,
        duration: 0.85,
        ease: "power2.inOut",
        onUpdate: function () {
          if (count) count.textContent = String(Math.round(counter.v)).padStart(3, "0");
        }
      }, 0.1)
      .to(loader.querySelector(".loader__inner"), { opacity: 0, duration: 0.3 }, "+=0.05")
      .to(loader, { yPercent: -100, duration: 0.7, ease: "expo.inOut" }, "-=0.1")
      // Start the hero while the curtain is still lifting — the two overlap
      .call(onDone, null, "-=0.45");
  }

  /* ==================================================================
     3. ENTRANCE — header, hero

     The "from" state is set immediately, before the loader ever runs, so
     the hero can't flash in its final position while the curtain lifts.
     ================================================================== */

  /* Inner pages have no hero, so every intro target is resolved first and
     skipped when empty — otherwise GSAP logs a warning per missing selector. */
  function find(sel) {
    var els = doc.querySelectorAll(sel);
    return els.length ? els : null;
  }

  function setIf(sel, vars) {
    var els = find(sel);
    if (els) gsap.set(els, vars);
  }

  function toIf(tl, sel, vars, position) {
    var els = find(sel);
    if (els) tl.to(els, vars, position);
  }

  function prepIntro() {
    setIf(".site-header__inner > *", { y: -24, opacity: 0 });
    setIf(".hero__title .line > span", { yPercent: 108 });
    setIf(".hero [data-hero-fade]", { y: 30, opacity: 0 });
    setIf(".hero__canvas", { opacity: 0 });
    setIf(".hero__glow-a, .hero__glow-b", { scale: 0.6, opacity: 0 });
  }

  function playIntro() {
    var tl = gsap.timeline({ defaults: { ease: "expo.out" } });

    toIf(tl, ".site-header__inner > *", { y: 0, opacity: 1, duration: 1, stagger: 0.1 });
    toIf(tl, ".hero__title .line > span",
         { yPercent: 0, duration: 1.25, stagger: 0.09, ease: "expo.out" }, 0.1);
    toIf(tl, ".hero [data-hero-fade]",
         { y: 0, opacity: 1, duration: 1.1, stagger: 0.09 }, 0.45);
    toIf(tl, ".hero__canvas", { opacity: 0.85, duration: 1.6, ease: "power2.out" }, 0);
    toIf(tl, ".hero__glow-a, .hero__glow-b",
         { scale: 1, opacity: 0.4, duration: 1.8, stagger: 0.12, ease: "power2.out" }, 0);
  }

  /* ==================================================================
     4. SCROLL REVEALS
     ================================================================== */

  function buildReveals() {
    /* -- Generic [data-reveal] blocks -------------------------------- */
    gsap.utils.toArray("[data-reveal]").forEach(function (el) {
      var delay = parseFloat(el.getAttribute("data-delay")) || 0;
      var from = { opacity: 0 };
      switch (el.getAttribute("data-reveal")) {
        case "down":  from.y = -32; break;
        case "left":  from.x = 48; break;
        case "right": from.x = -48; break;
        case "scale": from.scale = 0.94; break;
        case "fade":  break;
        default:      from.y = 42;
      }

      gsap.set(el, from);
      gsap.to(el, {
        opacity: 1, x: 0, y: 0, scale: 1,
        duration: 1.1,
        delay: delay,
        ease: "expo.out",
        scrollTrigger: { trigger: el, start: "top 88%", once: true }
      });
    });

    /* -- Staggered groups -------------------------------------------- */
    gsap.utils.toArray("[data-stagger]").forEach(function (group) {
      var children = group.children;
      if (!children.length) return;
      gsap.set(children, { opacity: 0, y: 40 });
      gsap.to(children, {
        opacity: 1, y: 0,
        duration: 1,
        stagger: parseFloat(group.getAttribute("data-stagger")) || 0.09,
        ease: "expo.out",
        scrollTrigger: { trigger: group, start: "top 85%", once: true }
      });
    });

    /* -- Word-cascade headings --------------------------------------- */
    gsap.utils.toArray('[data-split="words"]').forEach(function (el) {
      var words = splitWords(el);
      if (!words.length) return;
      gsap.set(words, { yPercent: 105, opacity: 0 });
      gsap.to(words, {
        yPercent: 0, opacity: 1,
        duration: 1.15,
        stagger: 0.035,
        ease: "expo.out",
        scrollTrigger: { trigger: el, start: "top 88%", once: true }
      });
    });

    /* -- Character-cascade (short strings only) ----------------------- */
    gsap.utils.toArray('[data-split="chars"]').forEach(function (el) {
      var chars = splitChars(el);
      if (!chars.length) return;
      gsap.set(chars, { yPercent: 110, opacity: 0 });
      gsap.to(chars, {
        yPercent: 0, opacity: 1,
        duration: 0.9,
        stagger: 0.022,
        ease: "expo.out",
        scrollTrigger: { trigger: el, start: "top 90%", once: true }
      });
    });

    /* -- Masked media reveals ---------------------------------------- */
    gsap.utils.toArray("[data-reveal-media]").forEach(function (frame) {
      var img = frame.querySelector("img");
      var tl = gsap.timeline({
        scrollTrigger: { trigger: frame, start: "top 85%", once: true }
      });

      // Hand the reveal to GSAP and retire the CSS curtain
      frame.classList.add("is-gsap-masked");

      tl.fromTo(
          frame,
          { clipPath: "inset(0% 0% 100% 0%)" },
          { clipPath: "inset(0% 0% 0% 0%)", duration: 1.3, ease: "expo.inOut" }
        );

      if (img) {
        tl.fromTo(img, { scale: 1.18 }, { scale: 1, duration: 1.6, ease: "expo.out" }, 0.05);
      }
    });

    /* -- Section hairlines draw in ------------------------------------ */
    gsap.utils.toArray("[data-draw-line]").forEach(function (line) {
      gsap.fromTo(
        line,
        { scaleX: 0, transformOrigin: "left center" },
        {
          scaleX: 1, duration: 1.4, ease: "expo.inOut",
          scrollTrigger: { trigger: line, start: "top 92%", once: true }
        }
      );
    });
  }

  /* ==================================================================
     5. PARALLAX
     Small, layered offsets. Capped so nothing drifts far enough to
     feel queasy, and disabled below the tablet breakpoint.
     ================================================================== */

  function buildParallax() {
    ScrollTrigger.matchMedia({
      "(min-width: 769px)": function () {
        gsap.utils.toArray("[data-parallax]").forEach(function (el) {
          var speed = parseFloat(el.getAttribute("data-parallax")) || 0.15;
          var shift = Math.max(-140, Math.min(140, speed * 220));

          gsap.fromTo(
            el,
            { y: -shift / 2 },
            {
              y: shift / 2,
              ease: "none",
              scrollTrigger: {
                trigger: el.getAttribute("data-parallax-trigger")
                  ? el.closest(el.getAttribute("data-parallax-trigger"))
                  : el,
                start: "top bottom",
                end: "bottom top",
                scrub: 1
              }
            }
          );
        });
      }
    });

    /* Hero content fades as it leaves — home page only */
    var heroInner = doc.querySelector(".hero__inner");
    if (heroInner && doc.querySelector(".hero")) {
      gsap.to(heroInner, {
        opacity: 0.15,
        y: -60,
        ease: "none",
        scrollTrigger: { trigger: ".hero", start: "60% top", end: "bottom top", scrub: true }
      });
    }
  }

  /* ==================================================================
     6. HORIZONTAL PROCESS TRACK
     Pinned and scrubbed on desktop; a native swipe strip on touch.
     ================================================================== */

  function buildProcess() {
    var section = doc.querySelector("[data-process]");
    if (!section) return;

    var track = section.querySelector(".process__track");
    var viewport = section.querySelector(".process__viewport");
    if (!track || !viewport) return;

    ScrollTrigger.matchMedia({
      "(min-width: 769px)": function () {
        var steps = track.querySelectorAll(".process__step");

        var tween = gsap.to(track, {
          x: function () {
            return -(track.scrollWidth - viewport.offsetWidth);
          },
          ease: "none",
          scrollTrigger: {
            trigger: section,
            pin: true,
            scrub: 1,
            invalidateOnRefresh: true,
            anticipatePin: 1,
            end: function () {
              return "+=" + (track.scrollWidth - viewport.offsetWidth + window.innerHeight * 0.5);
            }
          }
        });

        // Each card lifts as it enters the frame
        steps.forEach(function (step) {
          gsap.from(step, {
            opacity: 0.25,
            y: 40,
            duration: 0.6,
            ease: "power2.out",
            scrollTrigger: {
              trigger: step,
              containerAnimation: tween,
              start: "left 92%",
              end: "left 55%",
              scrub: true
            }
          });
        });
      },

      "(max-width: 768px)": function () {
        // Let the browser handle it: scroll-snap strip, no pinning
        viewport.style.overflowX = "auto";
        viewport.style.scrollSnapType = "x mandatory";
        viewport.style.paddingBottom = "1rem";
        gsap.set(track, { x: 0 });
        Array.prototype.forEach.call(track.children, function (step) {
          step.style.scrollSnapAlign = "start";
        });
      }
    });
  }

  /* ==================================================================
     7. COUNTERS
     Only on numbers that actually mean something.
     ================================================================== */

  function buildCounters() {
    gsap.utils.toArray("[data-counter]").forEach(function (el) {
      var target = parseFloat(el.getAttribute("data-counter"));
      if (isNaN(target)) return;

      var decimals = parseInt(el.getAttribute("data-decimals"), 10) || 0;
      var prefix = el.getAttribute("data-prefix") || "";
      var suffix = el.getAttribute("data-suffix") || "";
      var obj = { v: 0 };

      el.textContent = prefix + (0).toFixed(decimals) + suffix;

      gsap.to(obj, {
        v: target,
        duration: 1.9,
        ease: "power2.out",
        scrollTrigger: { trigger: el, start: "top 90%", once: true },
        onUpdate: function () {
          el.textContent = prefix + obj.v.toFixed(decimals) + suffix;
        }
      });
    });
  }

  /* ==================================================================
     8. MAGNETIC BUTTONS
     ================================================================== */

  function buildMagnetic() {
    if (!WDPR.finePointer) return;

    gsap.utils.toArray("[data-magnetic]").forEach(function (el) {
      var strength = parseFloat(el.getAttribute("data-magnetic")) || 0.3;
      var inner = el.firstElementChild;

      el.addEventListener("mousemove", function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) * strength;
        var y = (e.clientY - r.top - r.height / 2) * strength;

        gsap.to(el, { x: x, y: y, duration: 0.6, ease: "power3.out" });
        if (inner) gsap.to(inner, { x: x * 0.35, y: y * 0.35, duration: 0.6, ease: "power3.out" });
      });

      el.addEventListener("mouseleave", function () {
        gsap.to(el, { x: 0, y: 0, duration: 0.8, ease: "elastic.out(1, 0.4)" });
        if (inner) gsap.to(inner, { x: 0, y: 0, duration: 0.8, ease: "elastic.out(1, 0.4)" });
      });
    });
  }

  /* ==================================================================
     9. MISC FLOURISHES
     ================================================================== */

  function buildFlourishes() {
    /* Footer wordmark rises as the footer arrives */
    var wordmark = doc.querySelector(".footer-wordmark");
    if (wordmark) {
      gsap.fromTo(
        wordmark,
        { yPercent: 28, opacity: 0 },
        {
          yPercent: 0, opacity: 1, ease: "none",
          scrollTrigger: {
            trigger: ".site-footer",
            start: "top 85%",
            end: "bottom bottom",
            scrub: 1
          }
        }
      );
    }

    /* Work rows slide in from the left edge */
    gsap.utils.toArray("[data-work-item]").forEach(function (row, i) {
      gsap.from(row, {
        opacity: 0,
        x: -40,
        duration: 0.9,
        ease: "expo.out",
        scrollTrigger: { trigger: row, start: "top 92%", once: true }
      });
    });

    /* Section index numbers tick over as you pass them */
    gsap.utils.toArray("[data-section-index]").forEach(function (el) {
      gsap.from(el, {
        opacity: 0,
        letterSpacing: "0.6em",
        duration: 1.2,
        ease: "expo.out",
        scrollTrigger: { trigger: el, start: "top 92%", once: true }
      });
    });
  }

  /* ==================================================================
     BOOT
     ================================================================== */

  function init() {
    buildReveals();
    buildParallax();
    buildProcess();
    buildCounters();
    buildMagnetic();
    buildFlourishes();

    // Late-loading images change page height; keep triggers honest
    window.addEventListener("load", function () { ScrollTrigger.refresh(); });
  }

  prepIntro();
  runLoader(playIntro);
  init();
})();
