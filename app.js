/*
 * stackhidden.com - app.js
 * =====================================================================
 * Three jobs, in order, all dependency-free and wrapped in one IIFE so
 * nothing leaks into global scope:
 *
 *  1. THEME TOGGLE
 *     The initial theme is chosen by the inline <head> script in
 *     index.html (that ordering prevents a flash of the wrong theme).
 *     This file only handles CHANGES: a click flips data-theme on
 *     <html> and persists the choice to localStorage under "theme".
 *     Storage access is try/caught because private-mode browsers can
 *     throw on localStorage; the toggle must still work for the session
 *     when persistence is unavailable.
 *
 *  2. NEW YORK CLOCK
 *     The owner is based in New York and the hero eyebrow shows the
 *     local time there. Uses Intl with an explicit America/New_York
 *     zone so it is correct for visitors in any timezone, refreshes
 *     every 30 seconds (a minute display needs no faster tick), and
 *     silently blanks on the rare browser without full Intl support.
 *
 *  3. LINEAGE GRAPH (the page background)
 *     A canvas of drifting nodes; an edge is drawn between any two
 *     nodes closer than 140px, fading with distance. It is a visual
 *     metaphor for the owner's research on graph-based data lineage,
 *     not decoration borrowed from a template. Node count scales with
 *     viewport area and is capped at 70 so low-end phones stay smooth.
 *     The palette is re-read from the active theme on every toggle.
 *     prefers-reduced-motion stops the animation loop entirely and
 *     renders one static frame instead.
 *
 * Failure policy throughout: every feature degrades to a static,
 * readable page. If the canvas or storage fails, the content must not.
 */
(function () {
  // Theme toggle: persisted, falls back to the inline script's initial choice.
  var root = document.documentElement;
  var btn = document.getElementById('theme-toggle');
  function setTheme(t) {
    root.setAttribute('data-theme', t);
    try { localStorage.setItem('theme', t); } catch (e) {}
  }
  if (btn) {
    btn.addEventListener('click', function () {
      setTheme(root.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
      drawColors();
    });
  }

  // New York clock in the hero eyebrow.
  var clock = document.getElementById('clock');
  function tick() {
    if (!clock) return;
    try {
      clock.textContent = new Intl.DateTimeFormat('en-US', {
        hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'America/New_York'
      }).format(new Date());
    } catch (e) { clock.textContent = ''; }
  }
  tick(); setInterval(tick, 30000);

  // Animated lineage graph: drifting nodes, edges between near nodes.
  var canvas = document.getElementById('graph');
  if (!canvas) return;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var ctx = canvas.getContext('2d');
  var W, H, nodes = [], nodeColor = '#6ea8fe', lineColor = '110,168,254';

  function drawColors() {
    var light = root.getAttribute('data-theme') === 'light';
    nodeColor = light ? '#1f5fd0' : '#6ea8fe';
    lineColor = light ? '31,95,208' : '110,168,254';
    if (reduced) draw();
  }
  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    var count = Math.min(70, Math.floor(W * H / 26000));
    nodes = [];
    for (var i = 0; i < count; i++) {
      nodes.push({
        x: Math.random() * W, y: Math.random() * H,
        vx: (Math.random() - .5) * .35, vy: (Math.random() - .5) * .35,
        r: 1.4 + Math.random() * 1.8
      });
    }
    if (reduced) draw();
  }
  function draw() {
    ctx.clearRect(0, 0, W, H);
    var i, j, a, b, dx, dy, d;
    for (i = 0; i < nodes.length; i++) {
      for (j = i + 1; j < nodes.length; j++) {
        a = nodes[i]; b = nodes[j];
        dx = a.x - b.x; dy = a.y - b.y; d = Math.sqrt(dx * dx + dy * dy);
        if (d < 140) {
          ctx.strokeStyle = 'rgba(' + lineColor + ',' + (0.16 * (1 - d / 140)).toFixed(3) + ')';
          ctx.lineWidth = 1;
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
        }
      }
    }
    ctx.fillStyle = nodeColor;
    for (i = 0; i < nodes.length; i++) {
      a = nodes[i];
      ctx.beginPath(); ctx.arc(a.x, a.y, a.r, 0, Math.PI * 2); ctx.fill();
    }
  }
  function step() {
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      n.x += n.vx; n.y += n.vy;
      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H) n.vy *= -1;
    }
    draw();
    requestAnimationFrame(step);
  }
  window.addEventListener('resize', resize);
  drawColors();
  resize();
  if (!reduced) requestAnimationFrame(step);

  /* ---- Interactive lineage explorer (section #lineage) ---------------
     Each stage lists the edges that touch it. Hover, focus, or tap a
     stage and only those edges stay lit; everything else fades, which
     is the upstream/downstream trace a lineage tool performs. Tags are
     illustrative examples, as the section states on the page. */
  var lineageInfo = {
    feed: "Advertiser feeds - upstream source. Example tags: owner, ads data team; contract, data contract v3; contains campaign and spend fields.",
    click: "Clickstream - upstream source. Example tags: high volume event stream; schema checked at ingest; late events expected.",
    ingest: "Ingest - first stage under our control. Example tags: validates schemas, stamps every record with its source and arrival time.",
    transform: "Spark transform - where legacy ETL now runs as Spark jobs. Example tags: joins feeds to events; dedupes; writes partitioned output.",
    gate: "Quality gate - automated checks before anything is served. Example tags: freshness, volume, and distribution checks; failures stop the run and page the owner.",
    lake: "Data lake - the governed store. Example tags: partitioned by date; retention policy applied; every table carries its lineage.",
    api: "Data lake API - the serving layer I designed for real-time audience targeting. Example tags: low latency; access logged; consumers see certified data only.",
    analytics: "Advertiser analytics - what agencies and advertisers actually read. Downstream of everything above, which is why the chain has to be traceable.",
    anomaly: "Flagged anomalies - records the gate stopped or marked. Example tags: held out of serving; routed for review with the failing check attached."
  };
  var lineageEdges = {
    feed: ["e-feed-ingest"], click: ["e-click-ingest"],
    ingest: ["e-feed-ingest", "e-click-ingest", "e-ingest-transform"],
    transform: ["e-ingest-transform", "e-transform-gate"],
    gate: ["e-transform-gate", "e-gate-lake", "e-gate-anomaly"],
    lake: ["e-gate-lake", "e-lake-api"],
    api: ["e-lake-api", "e-api-analytics"],
    analytics: ["e-api-analytics"], anomaly: ["e-gate-anomaly"]
  };
  var svg = document.getElementById("lineageSvg");
  var detail = document.getElementById("lineageDetail");
  if (svg && detail) {
    var paths = svg.querySelectorAll(".edges path");
    var nodes = svg.querySelectorAll(".lnode");
    function highlight(name) {
      var on = lineageEdges[name] || [];
      paths.forEach(function (p) { p.classList.toggle("lit", on.indexOf(p.id) !== -1); p.classList.toggle("dim", on.indexOf(p.id) === -1); });
      nodes.forEach(function (n) { n.classList.toggle("dim", n.getAttribute("data-node") !== name); });
      detail.textContent = lineageInfo[name] || "";
    }
    function clear() {
      paths.forEach(function (p) { p.classList.remove("lit", "dim"); });
      nodes.forEach(function (n) { n.classList.remove("dim"); });
      detail.textContent = "Pick a stage to see its place in the chain.";
    }
    nodes.forEach(function (n) {
      var name = n.getAttribute("data-node");
      n.addEventListener("mouseenter", function () { highlight(name); });
      n.addEventListener("mouseleave", clear);
      n.addEventListener("focus", function () { highlight(name); });
      n.addEventListener("blur", clear);
      n.addEventListener("click", function () { highlight(name); });
    });
  }

  /* ---- Boot log typing (hero) -----------------------------------------
     Types the one-line system log once when the page loads. The full
     line is already in the HTML, so no-JS and reduced-motion visitors
     simply read it; typing is decoration only (aria-hidden). */
  var boot = document.getElementById("bootlog");
  if (boot && !reduced) {
    var full = boot.textContent; boot.textContent = "";
    var bi = 0;
    var bTimer = setInterval(function () {
      bi += 2; boot.textContent = full.slice(0, bi);
      if (bi >= full.length) clearInterval(bTimer);
    }, 24);
  }

  /* ---- Trace case files (section #trace) -------------------------------
     Rows become buttons. Selecting one writes its case file into the
     detail line: date, outlet or venue, and what the piece was. Every
     fact here restates the Writing, Featured, and Speaking sections. */
  var traceDetail = document.getElementById("traceDetail");
  var traceFiles = [
    "Jul 8, 2026 - TDWI Upside. 'From Reactive to Proactive: Automating Data Quality in Petabyte-Scale Analytics Pipelines.' The case for automated quality checks over reactive cleanup, drawn from production pipeline work.",
    "Aug 25, 2026 - AI Loves Data Roundtable. 'Batch to Streaming: What Actually Breaks and When It's Worth It.' A panel conversation on streaming migrations: what breaks first, and when batch is honestly the right answer.",
    "Aug 27, 2026 - ExchangeWire. 'Building Advertiser Analytics in a Post-Identifier World.' How advertiser analytics gets rebuilt when the identifiers it relied on go away.",
    "Sep 16, 2026 - Marketplace Risk, New York. Speaker on automated data quality and data-layer AI governance, in person in New York.",
    "Sep 30, 2026 - Label Your Data, 'EU AI Act: Training Data Requirements in 2026.' Named expert quote on the quality bar the EU AI Act sets for AI training data.",
    "Oct 23, 2026 - Label Your Data, 'Golden Dataset: How to Build Trusted AI Evaluation Data.' Named expert quote: auditable lineage is what makes a golden dataset trustworthy."
  ];
  if (traceDetail) {
    var rows = document.querySelectorAll("#trace .trace-row");
    rows.forEach(function (row, i) {
      row.setAttribute("tabindex", "0");
      row.setAttribute("role", "button");
      function open() { traceDetail.textContent = "Case file " + (i + 1) + " of " + rows.length + " - " + (traceFiles[i] || row.textContent.trim()); }
      row.addEventListener("click", open);
      row.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } });
    });
  }

  /* ---- Scrollspy + pipeline progress -----------------------------------
     The nav link for the section in view gets .active. A thin progress
     track under the header fills as the page scrolls, styled in CSS as
     a pipeline (Ingest, Transform, Govern, Serve light in sequence) -
     a scroll indicator in the site's own language. */
  var spyLinks = document.querySelectorAll(".site-nav a");
  if ("IntersectionObserver" in window && spyLinks.length) {
    var byId = {};
    spyLinks.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && byId[en.target.id]) {
          spyLinks.forEach(function (a) { a.classList.remove("active"); });
          byId[en.target.id].classList.add("active");
        }
      });
    }, { rootMargin: "-40% 0px -55% 0px" });
    document.querySelectorAll("main section[id]").forEach(function (s) { spy.observe(s); });
  }
  var bar = document.getElementById("scrollbarFill");
  if (bar) {
    var onScroll = function () {
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%";
    };
    document.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  }

  /* ---- Featured quotes carousel (section #featured) -------------------
     Slides move left to right: the incoming slide enters from the left
     and the track settles moving rightward, one slide every 5 seconds.
     Implementation: the track is shifted by one slide width with the
     order rotated, so motion is always in the same direction and wraps
     seamlessly. Pauses on hover and on keyboard focus; with
     prefers-reduced-motion there is no auto-advance at all and the
     buttons/dots do the work. Dots and arrows are real buttons. */
  var carousel = document.getElementById("quoteCarousel");
  if (carousel) {
    var slides = Array.prototype.slice.call(carousel.querySelectorAll(".slide"));
    var dotsWrap = carousel.querySelector(".carousel-dots");
    var idx = 0, timer = null;
    slides.forEach(function (_, i) {
      var d = document.createElement("button");
      d.type = "button"; d.className = "carousel-dot";
      d.setAttribute("aria-label", "Show quote " + (i + 1));
      d.addEventListener("click", function () { go(i, true); });
      dotsWrap.appendChild(d);
    });
    var dots = dotsWrap.children;
    function render(prev) {
      slides.forEach(function (s, i) {
        s.classList.toggle("on", i === idx);
        s.classList.toggle("out", i === prev);
        s.setAttribute("aria-hidden", i === idx ? "false" : "true");
      });
      for (var i = 0; i < dots.length; i++) dots[i].classList.toggle("on", i === idx);
    }
    function go(n, manual) {
      var prev = idx;
      idx = ((n % slides.length) + slides.length) % slides.length;
      render(prev);
      if (manual) restart();
    }
    function step() { go(idx + 1); }
    function restart() { if (timer) clearInterval(timer); if (!reduced) timer = setInterval(step, 5000); }
    document.getElementById("quotePrev").addEventListener("click", function () { go(idx - 1, true); });
    document.getElementById("quoteNext").addEventListener("click", function () { go(idx + 1, true); });
    carousel.addEventListener("mouseenter", function () { if (timer) clearInterval(timer); });
    carousel.addEventListener("mouseleave", restart);
    carousel.addEventListener("focusin", function () { if (timer) clearInterval(timer); });
    carousel.addEventListener("focusout", restart);
    slides.forEach(function (s, i) { s.classList.toggle("on", i === 0); s.setAttribute("aria-hidden", i === 0 ? "false" : "true"); });
    for (var i = 0; i < dots.length; i++) dots[i].classList.toggle("on", i === 0);
    restart();
  }
})();
