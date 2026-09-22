/* ==========================================================================
   WebDesignerPR — Main
   Interaction layer: cursor, hero field, accordions, filters, marquee,
   work preview, and form validation. No GSAP dependency — everything here
   works on its own so the site stays usable if the CDN is unreachable.
   ========================================================================== */

(function () {
  "use strict";

  var doc = document;
  var WDPR = (window.WDPR = window.WDPR || {});
  var reduced = WDPR.reducedMotion;
  var fine = WDPR.finePointer;

  /* ==================================================================
     1. CUSTOM CURSOR
     A dot that tracks exactly + a ring that lags behind it.
     ================================================================== */

  (function cursor() {
    var el = doc.querySelector(".cursor");
    if (!el || !fine || reduced) return;

    var dot = el.querySelector(".cursor__dot");
    var ring = el.querySelector(".cursor__ring");
    var label = el.querySelector(".cursor__label");
    if (!dot || !ring) return;

    doc.documentElement.classList.add("has-custom-cursor");

    var mx = window.innerWidth / 2, my = window.innerHeight / 2;
    var rx = mx, ry = my;
    var visible = false;

    window.addEventListener(
      "mousemove",
      function (e) {
        mx = e.clientX;
        my = e.clientY;
        if (!visible) {
          visible = true;
          el.style.opacity = "1";
        }
      },
      { passive: true }
    );

    doc.addEventListener("mouseleave", function () {
      el.style.opacity = "0";
      visible = false;
    });
    doc.addEventListener("mouseenter", function () {
      el.style.opacity = "1";
      visible = true;
    });

    (function loop() {
      rx += (mx - rx) * 0.16;
      ry += (my - ry) * 0.16;
      dot.style.transform = "translate(" + mx + "px," + my + "px) translate(-50%,-50%)";
      ring.style.transform = "translate(" + rx + "px," + ry + "px) translate(-50%,-50%)";
      window.requestAnimationFrame(loop);
    })();

    // Any [data-cursor] element retargets the ring; the value becomes its label
    function bind(node) {
      var mode = node.getAttribute("data-cursor") || "hover";
      var text = node.getAttribute("data-cursor-label") || "";

      node.addEventListener("mouseenter", function () {
        el.classList.add(mode === "view" ? "is-view" : "is-hover");
        if (text && label) label.textContent = text;
      });
      node.addEventListener("mouseleave", function () {
        el.classList.remove("is-view", "is-hover");
      });
    }

    Array.prototype.forEach.call(
      doc.querySelectorAll("a, button, [data-cursor]"),
      bind
    );
  })();

  /* ==================================================================
     2. HERO FIELD
     A pointer-reactive dot lattice on canvas. Density scales with the
     viewport, the loop parks itself when the hero scrolls away, and it
     never starts at all under reduced motion.
     ================================================================== */

  (function heroField() {
    var canvas = doc.querySelector(".hero__canvas");
    if (!canvas || reduced) return;

    var ctx = canvas.getContext("2d", { alpha: true });
    if (!ctx) return;

    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = 0, h = 0, dots = [], raf = null, active = true;
    var pointer = { x: -9999, y: -9999 };

    // Dot colours come from the theme tokens, not from literals, so the
    // lattice re-tints when the visitor switches theme.
    var tint = { base: "20, 18, 14", active: "224, 60, 28" };

    function readTint() {
      var cs = window.getComputedStyle(doc.documentElement);
      var base = cs.getPropertyValue("--canvas-dot").trim();
      var act = cs.getPropertyValue("--canvas-dot-active").trim();
      if (base) tint.base = base;
      if (act) tint.active = act;
    }
    readTint();
    doc.addEventListener("wdpr:themechange", readTint);

    function build() {
      var rect = canvas.getBoundingClientRect();
      w = rect.width;
      h = rect.height;
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      // Coarser lattice on small screens keeps the frame budget sane
      var gap = w < 700 ? 46 : w < 1200 ? 40 : 34;
      dots = [];
      for (var y = gap / 2; y < h; y += gap) {
        for (var x = gap / 2; x < w; x += gap) {
          dots.push({ x: x, y: y, ox: x, oy: y });
        }
      }
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);
      var radius = 190;

      for (var i = 0; i < dots.length; i++) {
        var d = dots[i];
        var dx = d.ox - pointer.x;
        var dy = d.oy - pointer.y;
        var dist = Math.sqrt(dx * dx + dy * dy);

        // Push dots away from the pointer, ease them home when it leaves
        var tx = d.ox, ty = d.oy, boost = 0;
        if (dist < radius) {
          var force = (1 - dist / radius);
          boost = force;
          tx = d.ox + (dx / (dist || 1)) * force * 26;
          ty = d.oy + (dy / (dist || 1)) * force * 26;
        }
        d.x += (tx - d.x) * 0.12;
        d.y += (ty - d.y) * 0.12;

        var alpha = 0.14 + boost * 0.62;
        ctx.beginPath();
        ctx.arc(d.x, d.y, 1 + boost * 1.8, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(" + (boost > 0.42 ? tint.active : tint.base) +
                        ", " + alpha.toFixed(3) + ")";
        ctx.fill();
      }
      raf = window.requestAnimationFrame(draw);
    }

    function start() {
      if (raf === null && active) raf = window.requestAnimationFrame(draw);
    }
    function stop() {
      if (raf !== null) {
        window.cancelAnimationFrame(raf);
        raf = null;
      }
    }

    window.addEventListener("mousemove", function (e) {
      var rect = canvas.getBoundingClientRect();
      pointer.x = e.clientX - rect.left;
      pointer.y = e.clientY - rect.top;
    }, { passive: true });

    window.addEventListener("mouseout", function () {
      pointer.x = pointer.y = -9999;
    }, { passive: true });

    var resizeTimer;
    window.addEventListener("resize", function () {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(build, 180);
    });

    // Stop painting when the hero is off-screen or the tab is hidden
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        active = entries[0].isIntersecting;
        active ? start() : stop();
      }, { threshold: 0 }).observe(canvas);
    }
    doc.addEventListener("visibilitychange", function () {
      doc.hidden ? stop() : start();
    });

    build();
    start();
  })();

  /* ==================================================================
     3. HEADLINE WORD ROTATOR
     ================================================================== */

  (function rotator() {
    var el = doc.querySelector("[data-rotator]");
    if (!el) return;

    var items = el.querySelectorAll(".rotator__item");
    if (items.length < 2) return;

    // Reserve the width of the longest word so the headline never reflows
    var i = 0;
    items[0].style.opacity = "1";
    for (var k = 1; k < items.length; k++) items[k].style.opacity = "0";

    if (reduced) return;

    window.setInterval(function () {
      var current = items[i];
      i = (i + 1) % items.length;
      var next = items[i];

      current.style.transition = "opacity .4s ease, transform .5s cubic-bezier(.16,1,.3,1)";
      next.style.transition = current.style.transition;
      current.style.opacity = "0";
      current.style.transform = "translateY(-60%)";
      next.style.opacity = "1";
      next.style.transform = "translateY(0)";

      window.setTimeout(function () {
        current.style.transition = "none";
        current.style.transform = "translateY(60%)";
      }, 520);
    }, 2800);
  })();

  /* ==================================================================
     4. MARQUEE
     Duplicates its own track, then scrolls with rAF so it survives a
     missing GSAP and pauses when out of view.
     ================================================================== */

  (function marquees() {
    Array.prototype.forEach.call(doc.querySelectorAll("[data-marquee]"), function (wrap) {
      var track = wrap.querySelector(".marquee__track");
      if (!track) return;

      // Under reduced motion the strip stays put — no cloning, no rAF loop.
      if (reduced) return;

      var speed = parseFloat(wrap.getAttribute("data-marquee-speed")) || 0.55;
      var dir = wrap.getAttribute("data-marquee-dir") === "right" ? 1 : -1;

      // Clone until the strip covers at least twice the viewport width
      var original = track.innerHTML;
      var guard = 0;
      while (track.scrollWidth < wrap.offsetWidth * 2 && guard < 8) {
        track.innerHTML += original;
        guard++;
      }
      var half = track.scrollWidth / 2;
      var clone = track.cloneNode(true);
      clone.setAttribute("aria-hidden", "true");
      wrap.appendChild(clone);

      var offset = 0, running = true, raf = null;

      function tick() {
        offset += speed * dir;
        if (offset <= -half) offset += half;
        if (offset >= 0 && dir === 1) offset -= half;
        track.style.transform = "translate3d(" + offset + "px,0,0)";
        clone.style.transform = "translate3d(" + (offset + half) + "px,0,0)";
        raf = running ? window.requestAnimationFrame(tick) : null;
      }

      function play() { if (!raf) { running = true; tick(); } }
      function pause() { running = false; }

      clone.style.position = "absolute";
      clone.style.left = "0";
      clone.style.top = "50%";
      clone.style.transform = "translate3d(" + half + "px,-50%,0)";
      wrap.style.position = "relative";

      wrap.addEventListener("mouseenter", pause);
      wrap.addEventListener("mouseleave", play);

      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (entries) {
          entries[0].isIntersecting ? play() : pause();
        }).observe(wrap);
      } else {
        play();
      }
    });
  })();

  /* ==================================================================
     5. ACCORDIONS — services + FAQ
     ================================================================== */

  (function accordions() {
    Array.prototype.forEach.call(doc.querySelectorAll("[data-accordion]"), function (group) {
      var exclusive = group.getAttribute("data-accordion") === "exclusive";
      var triggers = group.querySelectorAll("[data-accordion-trigger]");

      Array.prototype.forEach.call(triggers, function (trigger) {
        var item = trigger.closest("[data-accordion-item]");
        if (!item) return;

        trigger.addEventListener("click", function () {
          var open = trigger.getAttribute("aria-expanded") === "true";

          if (exclusive && !open) {
            Array.prototype.forEach.call(triggers, function (other) {
              var otherItem = other.closest("[data-accordion-item]");
              other.setAttribute("aria-expanded", "false");
              otherItem && otherItem.classList.remove("is-open");
            });
          }

          trigger.setAttribute("aria-expanded", String(!open));
          item.classList.toggle("is-open", !open);
        });
      });
    });
  })();

  /* ==================================================================
     6. PORTFOLIO FILTERS
     ================================================================== */

  (function filters() {
    var bar = doc.querySelector("[data-filters]");
    var grid = doc.querySelector("[data-project-grid]");
    if (!bar || !grid) return;

    var buttons = bar.querySelectorAll(".filter-btn");
    var cards = grid.querySelectorAll("[data-categories]");
    var empty = doc.querySelector("[data-filter-empty]");
    var live = doc.querySelector("[data-filter-status]");

    function apply(filter) {
      var shown = 0;

      Array.prototype.forEach.call(cards, function (card) {
        var cats = (card.getAttribute("data-categories") || "").split(/\s+/);
        var match = filter === "all" || cats.indexOf(filter) !== -1;
        card.classList.toggle("is-filtered-out", !match);
        if (match) {
          shown++;
          // Re-run the entrance animation so filtering feels deliberate
          card.style.animation = "none";
          void card.offsetWidth;
          card.style.animation = reduced ? "" : "fade-up-in .6s var(--ease-out) both";
        }
      });

      if (empty) empty.hidden = shown !== 0;
      if (live) {
        // Wording comes from the markup so each language ships its own
        var one = bar.getAttribute("data-count-one") || "project shown";
        var many = bar.getAttribute("data-count-many") || "projects shown";
        live.textContent = shown + " " + (shown === 1 ? one : many);
      }
    }

    function select(btn) {
      Array.prototype.forEach.call(buttons, function (b) {
        b.setAttribute("aria-pressed", String(b === btn));
      });
      apply(btn.getAttribute("data-filter") || "all");
    }

    Array.prototype.forEach.call(buttons, function (btn) {
      btn.addEventListener("click", function () { select(btn); });
    });

    // "Show everything" link inside the empty state
    var reset = doc.querySelector("[data-filter-reset]");
    if (reset) {
      reset.addEventListener("click", function () {
        var all = bar.querySelector('[data-filter="all"]');
        if (all) select(all);
      });
    }
  })();

  /* ==================================================================
     7. WORK LIST PREVIEW
     A floating plate that follows the pointer across the index list.
     ================================================================== */

  (function workPreview() {
    var list = doc.querySelector("[data-work-list]");
    var preview = doc.querySelector(".work-preview");
    if (!list || !preview || !fine || reduced) return;

    var slides = preview.querySelectorAll("img");
    var rows = list.querySelectorAll("[data-work-item]");
    var px = 0, py = 0, cx = 0, cy = 0;
    var shown = false;

    Array.prototype.forEach.call(rows, function (row, i) {
      row.addEventListener("mouseenter", function () {
        shown = true;
        preview.style.opacity = "1";
        Array.prototype.forEach.call(slides, function (s, j) {
          s.style.transition = "opacity .45s var(--ease-out), transform .8s var(--ease-out)";
          s.style.opacity = j === i ? "1" : "0";
          s.style.transform = j === i ? "scale(1)" : "scale(1.08)";
        });
      });
      row.addEventListener("mouseleave", function () {
        shown = false;
        preview.style.opacity = "0";
      });
    });

    window.addEventListener("mousemove", function (e) {
      px = e.clientX;
      py = e.clientY;
    }, { passive: true });

    (function loop() {
      cx += (px - cx) * 0.11;
      cy += (py - cy) * 0.11;
      var tilt = Math.max(-12, Math.min(12, (px - cx) * 0.5));
      preview.style.transform =
        "translate(" + cx + "px," + cy + "px) translate(-50%,-50%) rotate(" +
        tilt * 0.4 + "deg) scale(" + (shown ? 1 : 0.85) + ")";
      preview.style.transition = "opacity .4s var(--ease-out)";
      window.requestAnimationFrame(loop);
    })();
  })();

  /* ==================================================================
     8. CONTACT FORM VALIDATION
     Frontend only. There is no backend wired up — see the notice in the
     markup and the README for integration options.
     ================================================================== */

  (function contactForm() {
    var form = doc.querySelector("[data-contact-form]");
    if (!form) return;

    var status = doc.querySelector("[data-form-status]");
    var submit = form.querySelector('button[type="submit"]');

    var EMAIL = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i;

    // Every user-facing string is authored in the markup, so the Spanish and
    // English builds each carry their own without duplicating this script.
    function msg(key, fallback) {
      return form.getAttribute("data-msg-" + key) || fallback;
    }

    function fieldOf(input) {
      return input.closest(".field") || input.closest(".chip-group");
    }

    function setError(input, message) {
      var field = fieldOf(input);
      if (!field) return;
      field.classList.add("has-error");
      var slot = field.querySelector(".field__error");
      if (slot) slot.textContent = message;
      input.setAttribute("aria-invalid", "true");
    }

    function clearError(input) {
      var field = fieldOf(input);
      if (!field) return;
      field.classList.remove("has-error");
      var slot = field.querySelector(".field__error");
      if (slot) slot.textContent = "";
      input.removeAttribute("aria-invalid");
    }

    function validate(input) {
      var value = (input.value || "").trim();
      var name = input.name;

      if (input.hasAttribute("required") && !value) {
        setError(input, name === "email" ? msg("email-required", "We need an email to reply to.")
                                        : msg("required", "This field is required."));
        return false;
      }
      if (name === "name" && value && value.length < 2) {
        setError(input, msg("name", "Please enter your full name."));
        return false;
      }
      if (name === "email" && value && !EMAIL.test(value)) {
        setError(input, msg("email", "That address doesn't look right."));
        return false;
      }
      if (name === "details" && value && value.length < 20) {
        setError(input, msg("details", "A little more detail helps us reply properly — 20 characters minimum."));
        return false;
      }
      clearError(input);
      return true;
    }

    var inputs = form.querySelectorAll("input[name], textarea[name], select[name]");

    Array.prototype.forEach.call(inputs, function (input) {
      if (input.type === "radio") return;
      input.addEventListener("blur", function () { validate(input); });
      input.addEventListener("input", function () {
        if (fieldOf(input) && fieldOf(input).classList.contains("has-error")) validate(input);
      });
    });

    // Budget is a required radio group, validated as a unit
    function validateBudget() {
      var group = form.querySelector("[data-budget-group]");
      if (!group) return true;
      var checked = form.querySelector('input[name="budget"]:checked');
      var slot = group.querySelector(".field__error");

      if (!checked) {
        group.classList.add("has-error");
        if (slot) slot.textContent = msg("budget", "Select a range — an estimate is fine.");
        return false;
      }
      group.classList.remove("has-error");
      if (slot) slot.textContent = "";
      return true;
    }

    Array.prototype.forEach.call(form.querySelectorAll('input[name="budget"]'), function (radio) {
      radio.addEventListener("change", validateBudget);
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      var valid = true;
      var firstBad = null;

      Array.prototype.forEach.call(inputs, function (input) {
        if (input.type === "radio") return;
        if (!validate(input)) {
          valid = false;
          if (!firstBad) firstBad = input;
        }
      });

      if (!validateBudget()) {
        valid = false;
        if (!firstBad) firstBad = form.querySelector('input[name="budget"]');
      }

      if (!valid) {
        if (status) {
          status.className = "form-status form-status--error is-visible";
          status.innerHTML =
            "<strong>" + msg("error-strong", "Almost there.") + "</strong>" +
            msg("error", " Please correct the highlighted fields and send again.");
        }
        firstBad && firstBad.focus();
        return;
      }

      // Everything validates. Simulate the request so the success state is
      // reviewable — swap this block for a real endpoint (see README).
      submit && (submit.disabled = true);
      if (status) {
        status.className = "form-status is-visible";
        status.innerHTML = "<strong>" + msg("sending", "Sending…") + "</strong>";
      }

      window.setTimeout(function () {
        var name = (form.elements.name && form.elements.name.value.trim().split(" ")[0]) || "there";
        if (status) {
          var safeName = name.replace(/[<>&]/g, "");
          var strong = msg("ok-strong", "Validated, {name}.").replace("{name}", safeName);
          status.className = "form-status form-status--success is-visible";
          status.innerHTML =
            "<strong>" + strong + "</strong>" +
            msg("ok", " Your brief passed every check — but this form is not yet connected to a " +
                      "backend, so nothing was actually sent. Connect an endpoint as described in " +
                      "the README, then email ") +
            '<a class="link-underline" href="mailto:hola@webdesignerpr.com">hola@webdesignerpr.com</a>.';
        }
        submit && (submit.disabled = false);
        status && status.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "center" });
      }, 900);
    });
  })();

  /* ==================================================================
     9. LAZY-LOADED IMAGE FADE
     ================================================================== */

  (function imageFade() {
    Array.prototype.forEach.call(doc.querySelectorAll("img[loading='lazy']"), function (img) {
      if (img.complete) return;
      img.style.opacity = "0";
      img.style.transition = "opacity .6s var(--ease-out)";
      img.addEventListener("load", function () { img.style.opacity = "1"; });
      img.addEventListener("error", function () { img.style.opacity = "1"; });
    });
  })();
})();
