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
  // graphRunning guards against a second animation loop. Before v5 the
  // motion control's applyMotion() started a fresh loop on every call
  // (including once at load), so the field drifted at double speed and
  // each toggle added another loop.
  var graphRunning = false;
  function step() {
    // The manual reduce-motion control (v4) freezes the field in place.
    if (root.getAttribute('data-motion') === 'reduced') { graphRunning = false; draw(); return; }
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      n.x += n.vx; n.y += n.vy;
      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H) n.vy *= -1;
    }
    draw();
    requestAnimationFrame(step);
  }
  function startGraph() {
    if (reduced || graphRunning) return;
    graphRunning = true;
    requestAnimationFrame(step);
  }
  window.addEventListener('resize', resize);
  drawColors();
  resize();
  startGraph();

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
    // Named lnodes, not nodes: this IIFE shares one function scope, and
    // the background canvas above keeps its particle array in `nodes`.
    // Reusing the name swapped the canvas array for these SVG elements,
    // so the background painted nothing until a resize, and after a
    // resize these handlers threw on plain particle objects.
    var lnodes = svg.querySelectorAll(".lnode");
    function highlight(name) {
      var on = lineageEdges[name] || [];
      paths.forEach(function (p) { p.classList.toggle("lit", on.indexOf(p.id) !== -1); p.classList.toggle("dim", on.indexOf(p.id) === -1); });
      lnodes.forEach(function (n) { n.classList.toggle("dim", n.getAttribute("data-node") !== name); });
      detail.textContent = lineageInfo[name] || "";
    }
    function clear() {
      paths.forEach(function (p) { p.classList.remove("lit", "dim"); });
      lnodes.forEach(function (n) { n.classList.remove("dim"); });
      detail.textContent = "Pick a stage to see its place in the chain.";
    }
    lnodes.forEach(function (n) {
      var name = n.getAttribute("data-node");
      n.addEventListener("mouseenter", function () { highlight(name); });
      n.addEventListener("mouseleave", clear);
      n.addEventListener("focus", function () { highlight(name); });
      n.addEventListener("blur", clear);
      n.addEventListener("click", function () { highlight(name); });
    });
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
    "Oct 23, 2026 - Label Your Data, 'Golden Dataset: How to Build Trusted AI Evaluation Data.' Named expert quote: auditable lineage is what makes a golden dataset trustworthy.",
    "Nov 2, 2026 - Informatics Magazine, 'How Data Teams Balance Access and Privacy.' Named expert quote under 'Validate Pipelines at Ingestion,' on balancing timely access to business data with protecting sensitive information."
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
  // The header nav has no .site-nav class; the old ".site-nav a"
  // selector matched nothing, so scrollspy never ran.
  var spyLinks = document.querySelectorAll('.site-header nav a[href^="#"]');
  if ("IntersectionObserver" in window && spyLinks.length) {
    var byId = {};
    spyLinks.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var markActive = function (id) {
      var link = byId[id];
      if (!link || link.classList.contains("active")) return;
      spyLinks.forEach(function (a) { a.classList.remove("active"); });
      link.classList.add("active");
      // On phones the links scroll sideways in one row; keep the active
      // one in view. Direct scrollLeft math, not scrollIntoView, which
      // could also nudge the page.
      var row = link.parentElement;
      if (row.scrollWidth > row.clientWidth + 1) {
        var left = link.offsetLeft - row.offsetLeft, right = left + link.offsetWidth;
        if (left < row.scrollLeft || right > row.scrollLeft + row.clientWidth - 28) {
          row.scrollTo({ left: Math.max(0, left - 16), behavior: motionOff() ? "auto" : "smooth" });
        }
      }
    };
    // The last section is often too short to reach the band below, so
    // at the bottom of the page the last nav link wins. Both paths check
    // it: observer callbacks land after the scroll event and would
    // otherwise hand the highlight back to the section above.
    var lastId = spyLinks[spyLinks.length - 1].getAttribute("href").slice(1);
    var atBottom = function () {
      var h = document.documentElement;
      return h.scrollTop + h.clientHeight >= h.scrollHeight - 2;
    };
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) markActive(atBottom() ? lastId : en.target.id); });
    }, { rootMargin: "-40% 0px -55% 0px" });
    document.querySelectorAll("main section[id]").forEach(function (s) { spy.observe(s); });
    document.addEventListener("scroll", function () { if (atBottom()) markActive(lastId); }, { passive: true });
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
        // Only a slide that is leaving gets "out". Choosing the slide that
        // is already showing (its own dot, or a Trace from the query
        // console) used to mark it both "on" and "out", and "out" won in
        // the stylesheet, so the visible quote slid away and left the
        // stage empty.
        s.classList.toggle("out", i === prev && i !== idx);
        s.setAttribute("aria-hidden", i === idx ? "false" : "true");
      });
      for (var i = 0; i < dots.length; i++) { dots[i].classList.toggle("on", i === idx); if (i === idx) dots[i].setAttribute("aria-current", "true"); else dots[i].removeAttribute("aria-current"); }
    }
    function go(n, manual) {
      var prev = idx;
      idx = ((n % slides.length) + slides.length) % slides.length;
      render(prev);
      if (manual) restart();
    }
    /* Named cstep, not step: the canvas animation in this same IIFE
       also defines a step(), and the shared name let animation-frame
       calls advance the carousel twice at load. With two slides that
       wrapped back to the first slide and hid the bug; with three
       slides (Nov 2, 2026) the carousel opened on the wrong slide and
       its 5-second timer never fired. Keep this name unique. */
    // The timer keeps ticking but skips while the footer Reduce motion
    // control is on, so the carousel holds still and resumes when motion
    // is turned back on. Before v5 only the OS setting stopped it.
    function cstep() { if (!motionOff()) go(idx + 1); }
    function restart() { if (timer) clearInterval(timer); if (!reduced && root.getAttribute('data-motion') !== 'reduced') timer = setInterval(cstep, 5000); }
    document.getElementById("quotePrev").addEventListener("click", function () { go(idx - 1, true); });
    document.getElementById("quoteNext").addEventListener("click", function () { go(idx + 1, true); });
    carousel.addEventListener("mouseenter", function () { if (timer) clearInterval(timer); });
    carousel.addEventListener("mouseleave", restart);
    carousel.addEventListener("focusin", function () { if (timer) clearInterval(timer); });
    carousel.addEventListener("focusout", restart);
    slides.forEach(function (s, i) { s.classList.toggle("on", i === 0); s.setAttribute("aria-hidden", i === 0 ? "false" : "true"); });
    for (var i = 0; i < dots.length; i++) { dots[i].classList.toggle("on", i === 0); if (i === 0) dots[i].setAttribute("aria-current", "true"); }
    restart();
  }

  /* ---- V4: case files, command palette, contact actions, motion
     control, and pointer/scroll/click graphics --------------------------
     motionOff() is the single test every v4 animation consults: the OS
     preference captured at load, OR the manual footer control, which
     persists in localStorage under "motion". The canvas loop and the
     carousel also read data-motion directly (see their gates above). */
  function motionOff() {
    return reduced || root.getAttribute('data-motion') === 'reduced';
  }

  // Case files: the toggle buttons open and close the file bodies, and
  // #case=<slug> deep links open one on arrival (used by the palette).
  function setCase(id, open) {
    var art = document.getElementById(id);
    if (!art) return;
    var body = art.querySelector('.case-body');
    var b = art.querySelector('.case-toggle');
    if (!body || !b) return;
    body.hidden = !open;
    b.setAttribute('aria-expanded', open ? 'true' : 'false');
    b.textContent = open ? 'Close case file' : 'Open case file';
  }
  document.querySelectorAll('.case-toggle').forEach(function (b) {
    b.addEventListener('click', function () {
      var art = b.closest('.case');
      var body = art && art.querySelector('.case-body');
      if (art && body) setCase(art.id, body.hidden);
    });
  });
  function openCase(id) {
    setCase(id, true);
    var art = document.getElementById(id);
    if (art) art.scrollIntoView();
  }
  if (location.hash.indexOf('#case=') === 0) {
    var slugPart = location.hash.slice(6);
    if (slugPart.indexOf('case-') === 0) slugPart = slugPart.slice(5);
    var wantCase = 'case-' + slugPart;
    if (document.getElementById(wantCase)) setTimeout(function () { openCase(wantCase); }, 80);
  }

  // The animated lineage core in the hero panel: a halftone sphere of
  // governed data with dataset nodes travelling lineage orbits around
  // it. Inspiration: living centerpieces on the best portfolio sites;
  // the execution is this site's own, drawn on canvas in the theme
  // accent. Polite loop, per the standard canvas-hero pattern found in
  // research: the dot field is precomputed once, the loop pauses when
  // the panel is off screen or the tab is hidden, and reduced motion
  // gets a single still frame.
  var coreCv = document.getElementById('coreAnim');
  if (coreCv) {
    var cctx = coreCv.getContext('2d');
    var CCX = 440, CCY = 420, CR = 215;
    function hexRgb(hex) { hex = (hex || '').trim(); var n = parseInt(hex.slice(1), 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; }
    function coreColors() {
      var cs = getComputedStyle(document.documentElement);
      return { a: hexRgb(cs.getPropertyValue('--accent')), v: hexRgb(cs.getPropertyValue('--accent2')), bg: cs.getPropertyValue('--bg').trim() || '#0d1017' };
    }
    var coreCols = coreColors();
    var coreDots = [], cstep = 17;
    for (var yy = -CR; yy <= CR; yy += cstep) for (var xx = -CR; xx <= CR; xx += cstep) {
      var d2 = xx * xx + yy * yy; if (d2 > CR * CR) continue;
      var nz = Math.sqrt(1 - d2 / (CR * CR));
      var lx = -0.55, ly = -0.75, lz = 0.6, ll = Math.sqrt(lx * lx + ly * ly + lz * lz);
      coreDots.push({ x: xx, y: yy, b: Math.max(0, (xx / CR * lx + yy / CR * ly + nz * lz) / ll) });
    }
    var coreOrbits = [
      { rx: 385, ry: 120, rot: -0.30, speed: 0.14, nodes: [{ p: 0.3, r: 15 }, { p: 3.6, r: 11 }] },
      { rx: 340, ry: 95, rot: 0.22, speed: -0.10, nodes: [{ p: 1.8, r: 12 }] },
      { rx: 410, ry: 150, rot: -0.62, speed: 0.08, nodes: [{ p: 5.2, r: 13 }, { p: 2.2, r: 9 }] }
    ];
    function corePt(o, a) {
      var x = Math.cos(a) * o.rx, y = Math.sin(a) * o.ry;
      var c = Math.cos(o.rot), s = Math.sin(o.rot);
      return [CCX + x * c - y * s, CCY + x * s + y * c];
    }
    function rgba(c, al) { return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + al + ')'; }
    function coreFrame(t) {
      cctx.clearRect(0, 0, 880, 880);
      coreOrbits.forEach(function (o) {
        cctx.beginPath();
        for (var a = 0; a <= Math.PI * 2 + 0.01; a += 0.05) { var p = corePt(o, a); a === 0 ? cctx.moveTo(p[0], p[1]) : cctx.lineTo(p[0], p[1]); }
        cctx.strokeStyle = rgba(coreCols.a, 0.35); cctx.lineWidth = 2.5; cctx.stroke();
      });
      var shimmer = 0.06 * Math.sin(t * 0.0007);
      coreDots.forEach(function (d) {
        var b = Math.min(1, d.b + shimmer + 0.08);
        cctx.beginPath(); cctx.arc(CCX + d.x, CCY + d.y, 1 + 5.2 * b, 0, 7);
        cctx.fillStyle = rgba(coreCols.a, (0.13 + 0.8 * b).toFixed(3)); cctx.fill();
      });
      coreOrbits.forEach(function (o) {
        o.nodes.forEach(function (n) {
          var a = n.p + t * 0.001 * o.speed;
          for (var k = 5; k >= 1; k--) { var tp = corePt(o, a - k * 0.045 * Math.sign(o.speed)); cctx.beginPath(); cctx.arc(tp[0], tp[1], n.r * 0.32 * (1 - k / 7), 0, 7); cctx.fillStyle = rgba(coreCols.v, 0.10 + 0.05 * (6 - k)); cctx.fill(); }
          var p = corePt(o, a);
          cctx.beginPath(); cctx.arc(p[0], p[1], n.r, 0, 7); cctx.fillStyle = coreCols.bg; cctx.fill();
          cctx.lineWidth = 4; cctx.strokeStyle = rgba(coreCols.a, 1); cctx.stroke();
          cctx.beginPath(); cctx.arc(p[0], p[1], n.r * 0.36, 0, 7); cctx.fillStyle = rgba(coreCols.a, 1); cctx.fill();
        });
      });
      cctx.fillStyle = rgba(coreCols.a, 0.5);
      [[120, 150], [760, 180], [180, 700], [720, 690], [90, 430], [800, 450]].forEach(function (s) { cctx.fillRect(s[0], s[1], 4, 4); });
    }
    var coreVisible = true, coreRunning = false;
    function coreLoop(t) {
      if (!coreVisible || document.hidden || motionOff()) { coreRunning = false; return; }
      coreFrame(t); requestAnimationFrame(coreLoop);
    }
    function coreStart() {
      if (motionOff()) { coreFrame(1200); return; }
      if (!coreRunning) { coreRunning = true; requestAnimationFrame(coreLoop); }
    }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { coreVisible = es[0].isIntersecting; if (coreVisible) coreStart(); }).observe(coreCv);
    }
    // A theme flip repaints with the new colours. Turning motion back on
    // restarts the loop: before v5 this only drew a still frame, so the
    // core stayed frozen until it scrolled off screen and back.
    new MutationObserver(function () {
      coreCols = coreColors();
      if (motionOff()) coreFrame(1200); else coreStart();
    }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'data-motion'] });
    // The loop stops itself while the tab is hidden; resume on return.
    document.addEventListener('visibilitychange', function () { if (!document.hidden) coreStart(); });
    coreStart();
  }

  // Hero video: the data-hero action figure as a muted 10-second loop.
  // It plays only while motion is allowed (OS setting and the footer
  // toggle, via motionOff), the hero is on screen, and the tab is
  // visible. Otherwise the poster still shows, which is the same
  // illustration unanimated. The play() promise is caught because a
  // browser may still refuse; a refused autoplay just leaves the still.
  var heroVideo = document.getElementById('heroVideo');
  if (heroVideo) {
    heroVideo.muted = true;
    var hvVisible = true;
    function hvSync() {
      if (!motionOff() && hvVisible && !document.hidden) {
        var promise = heroVideo.play();
        if (promise && promise.catch) promise.catch(function () {});
      } else {
        heroVideo.pause();
      }
    }
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { hvVisible = es[0].isIntersecting; hvSync(); }).observe(heroVideo);
    document.addEventListener('visibilitychange', hvSync);
    new MutationObserver(hvSync).observe(document.documentElement, { attributes: true, attributeFilter: ['data-motion', 'data-theme'] });
    hvSync();
  }

  // The cursor bot (owner's idea, Oct 2026): a small terminal bot fixed
  // in the corner. Its pupils ease toward the pointer, the head leans a
  // few degrees that way, and it blinks on a random timer. Under
  // reduced motion the block never starts and CSS closes its eyes: the
  // sleeping state. Hidden in print via style.css.
  var bot = document.getElementById('cursorBot');
  if (bot && !motionOff()) {
    var bHead = bot.querySelector('.bot-head');
    var bPupils = bot.querySelectorAll('.bot-pupil');
    var bEyes = bot.querySelectorAll('.bot-eye-g');
    var bTx = window.innerWidth / 2, bTy = window.innerHeight / 2, bPx = 0, bPy = 0, bLean = 0;
    document.addEventListener('pointermove', function (e) { bTx = e.clientX; bTy = e.clientY; }, { passive: true });
    (function bLoop() {
      if (!motionOff()) {
        var r = bot.getBoundingClientRect();
        var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
        var dx = bTx - cx, dy = bTy - cy;
        var d = Math.sqrt(dx * dx + dy * dy) || 1;
        var gx = (dx / d) * Math.min(2.8, d / 40), gy = (dy / d) * Math.min(2.8, d / 40);
        bPx += (gx - bPx) * 0.12; bPy += (gy - bPy) * 0.12;
        for (var i = 0; i < bPupils.length; i++) bPupils[i].setAttribute('transform', 'translate(' + bPx.toFixed(2) + ',' + bPy.toFixed(2) + ')');
        var targetLean = Math.max(-4, Math.min(4, dx / 90));
        bLean += (targetLean - bLean) * 0.06;
        if (bHead) bHead.style.transform = 'rotate(' + bLean.toFixed(2) + 'deg)';
      }
      requestAnimationFrame(bLoop);
    })();
    (function bBlink() {
      setTimeout(function () {
        if (!motionOff()) {
          for (var i = 0; i < bEyes.length; i++) bEyes[i].style.transform = 'scaleY(0.08)';
          setTimeout(function () { for (var j = 0; j < bEyes.length; j++) bEyes[j].style.transform = 'scaleY(1)'; }, 130);
        }
        bBlink();
      }, 2400 + Math.random() * 3200);
    })();
  }

  // Contact is links only (Email me, LinkedIn). The copy-email and
  // print-resume buttons were removed at the owner's direction in
  // Oct 2026, here and in the palette below. The print stylesheet in
  // style.css stays, so a visitor's own browser print still works.

  // Reduce-motion control in the footer. Pauses the SVG packets via
  // pauseAnimations; the canvas and carousel check data-motion in
  // their own loops; CSS handles transitions and the reveal states.
  var motionBtn = document.getElementById('motionBtn');
  function applyMotion() {
    var off = motionOff();
    if (motionBtn) {
      motionBtn.setAttribute('aria-pressed', off ? 'true' : 'false');
      motionBtn.textContent = off ? 'Motion reduced (on)' : 'Reduce motion';
    }
    var svgEl = document.getElementById('lineageSvg');
    if (svgEl && svgEl.pauseAnimations) { if (off) svgEl.pauseAnimations(); else svgEl.unpauseAnimations(); }
    if (!off) startGraph();
  }
  try { if (localStorage.getItem('motion') === 'reduced') root.setAttribute('data-motion', 'reduced'); } catch (e) {}
  if (motionBtn) {
    motionBtn.addEventListener('click', function () {
      if (root.getAttribute('data-motion') === 'reduced') {
        root.removeAttribute('data-motion');
        try { localStorage.removeItem('motion'); } catch (e) {}
      } else {
        root.setAttribute('data-motion', 'reduced');
        try { localStorage.setItem('motion', 'reduced'); } catch (e) {}
      }
      applyMotion();
    });
  }
  applyMotion();

  // Command palette: Ctrl or Cmd + K, the header button, or a tap on
  // the scrim to close. Commands are a static table; filtering is a
  // substring match on the label, arrow keys move, Enter runs.
  var palette = document.getElementById('palette');
  var pInput = document.getElementById('paletteInput');
  var pList = document.getElementById('paletteList');
  function goTo(sel) { var el = document.querySelector(sel); if (el) el.scrollIntoView(); }
  var commands = [
    { label: 'Go to About', hint: 'section', run: function () { goTo('#about'); } },
    { label: 'Go to Experience', hint: 'section', run: function () { goTo('#experience'); } },
    { label: 'Go to Engineering Work', hint: 'section', run: function () { goTo('#engineering'); } },
    { label: 'Case file: Insight Ingestion Orchestration', hint: 'open', run: function () { openCase('case-orchestration'); } },
    { label: 'Case file: Insights API', hint: 'open', run: function () { openCase('case-insights-api'); } },
    { label: 'Case file: Custom Brands (ICM)', hint: 'open', run: function () { openCase('case-icm'); } },
    { label: 'Case file: Mosaic and Kaleidoscope Agents', hint: 'open', run: function () { openCase('case-mosaic'); } },
    { label: 'Go to Lineage, drawn out', hint: 'section', run: function () { goTo('#lineage'); } },
    { label: 'Go to 2026, as a trace', hint: 'section', run: function () { goTo('#trace'); } },
    { label: 'Go to Published Writing', hint: 'section', run: function () { goTo('#writing'); } },
    { label: 'Go to Featured In', hint: 'section', run: function () { goTo('#featured'); } },
    { label: 'Go to Query this page', hint: 'section', run: function () { goTo('#query'); } },
    { label: 'Go to Contact', hint: 'section', run: function () { goTo('#contact'); } },
    { label: 'Toggle light / dark theme', hint: 'action', run: function () { if (btn) btn.click(); } },
    { label: 'Reduce motion on / off', hint: 'action', run: function () { if (motionBtn) motionBtn.click(); } },
    { label: 'Open LinkedIn', hint: 'link', run: function () { window.open('https://www.linkedin.com/in/vishnu-vardhan-reddy-kaithapuram/', '_blank'); } },
    { label: 'Open GitHub source', hint: 'link', run: function () { window.open('https://github.com/vishuvardhan16/stackhidden.com', '_blank'); } }
  ];
  // Set by the query console further down. The palette checks it at
  // run time, so the order of the two blocks does not matter.
  var querySql = null;
  function looksLikeSql(s) { return /^\s*(select\s|show\s+tables\b|describe\s|desc\s|help\s*;?\s*$)/i.test(s); }
  var pSel = 0, pItems = [];
  function markSel() {
    Array.prototype.forEach.call(pList.children, function (li, i) { li.classList.toggle('sel', i === pSel); });
  }
  function renderPalette() {
    var q = pInput.value.trim().toLowerCase();
    pItems = commands.filter(function (c) { return !q || c.label.toLowerCase().indexOf(q) !== -1; });
    // SQL typed into the palette becomes the first command: run it in
    // the query console.
    var raw = pInput.value.trim();
    if (querySql && looksLikeSql(raw)) pItems.unshift({ label: 'Run SQL: ' + raw, hint: 'query', run: function () { querySql(raw); } });
    pSel = 0;
    pList.innerHTML = '';
    if (!pItems.length) {
      var none = document.createElement('li');
      none.textContent = 'No matching command';
      pList.appendChild(none);
      return;
    }
    pItems.forEach(function (c, i) {
      var li = document.createElement('li');
      li.setAttribute('role', 'option');
      var s = document.createElement('span'); s.textContent = c.label;
      var h = document.createElement('small'); h.textContent = c.hint;
      li.appendChild(s); li.appendChild(h);
      li.addEventListener('click', function () { closePalette(); c.run(); });
      li.addEventListener('mousemove', function () { pSel = i; markSel(); });
      pList.appendChild(li);
    });
    markSel();
  }
  function openPalette() { if (!palette) return; palette.hidden = false; pInput.value = ''; renderPalette(); pInput.focus(); }
  function closePalette() { if (palette) palette.hidden = true; }
  var paletteBtn = document.getElementById('paletteBtn');
  if (paletteBtn) paletteBtn.addEventListener('click', openPalette);
  if (pInput) pInput.addEventListener('input', renderPalette);
  if (palette) palette.addEventListener('click', function (e) { if (e.target === palette) closePalette(); });
  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
      e.preventDefault();
      if (palette && palette.hidden) openPalette(); else closePalette();
      return;
    }
    if (!palette || palette.hidden) return;
    if (e.key === 'Escape') closePalette();
    else if (e.key === 'ArrowDown') { e.preventDefault(); pSel = Math.min(pSel + 1, pItems.length - 1); markSel(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); pSel = Math.max(pSel - 1, 0); markSel(); }
    else if (e.key === 'Enter' && document.activeElement === pInput) { var c = pItems[pSel]; if (c) { closePalette(); c.run(); } }
  });

  // Scroll reveal: sections and case files rise and fade in the first
  // time they enter the viewport. Only elements that start below the
  // fold get the hidden state, so nothing flashes or stays invisible
  // if the observer never fires.
  if ('IntersectionObserver' in window && !motionOff()) {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); ro.unobserve(en.target); } });
    }, { threshold: 0.08 });
    document.querySelectorAll('main section, #engineering .case').forEach(function (el) {
      if (el.getBoundingClientRect().top > window.innerHeight * 0.92) { el.classList.add('reveal'); ro.observe(el); }
    });
  }

  // A jump into a section that has not revealed yet shows that section at
  // once. Otherwise the browser aims at the section while it still sits
  // 22px low, the rise then carries the target up, and it ends under the
  // header. Used by in-page links (below) and the query console's Trace.
  function revealNow(el) {
    for (var n = el; n && n.classList; n = n.parentElement) {
      if (n.classList.contains('reveal') && !n.classList.contains('in')) {
        n.style.transition = 'none';
        n.classList.add('in');
        void n.offsetWidth;
        n.style.removeProperty('transition');
        if (!n.style.length) n.removeAttribute('style');
      }
    }
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute('href').slice(1), target = null;
    try { target = id && document.getElementById(decodeURIComponent(id)); } catch (err) {}
    if (target) revealNow(target);
  }, true);

  // Keep scroll-padding-top (style.css) equal to the sticky header's real
  // height, which changes with width and wrapping.
  var siteHeader = document.querySelector('.site-header');
  function setHeaderHeight() {
    if (siteHeader) document.documentElement.style.setProperty('--header-h', siteHeader.offsetHeight + 'px');
  }
  setHeaderHeight();
  if (siteHeader && 'ResizeObserver' in window) new ResizeObserver(setHeaderHeight).observe(siteHeader);
  else window.addEventListener('resize', setHeaderHeight);

  // Cursor glow: a soft accent halo that trails the pointer with a lag
  // (lerp), so it feels like light following the hand, not a sticker.
  // Fine pointers only; touch devices never see it.
  var glow = document.getElementById('cursorGlow');
  if (glow && window.matchMedia('(pointer: fine)').matches && !motionOff()) {
    var gx = -500, gy = -500, tx = -500, ty = -500, glowOn = false;
    document.addEventListener('pointermove', function (e) {
      tx = e.clientX; ty = e.clientY;
      if (!glowOn) { glowOn = true; glow.style.opacity = '1'; }
    }, { passive: true });
    (function glowStep() {
      if (!motionOff()) {
        gx += (tx - gx) * 0.08; gy += (ty - gy) * 0.08;
        glow.style.transform = 'translate(' + gx + 'px,' + gy + 'px)';
      }
      requestAnimationFrame(glowStep);
    })();
  }

  // Click burst: a ring and six sparks at the press point, in the
  // accent colours. Skipped on interactive elements (they have their
  // own feedback) and under reduced motion. Pure decoration, spawned
  // and removed per click; nothing accumulates in the DOM.
  document.addEventListener('pointerdown', function (e) {
    if (motionOff()) return;
    var t = e.target;
    if (t && t.closest && t.closest('a, button, input, textarea, table, li, .lnode, [role="button"]')) return;
    var b = document.createElement('div');
    b.className = 'burst'; b.setAttribute('aria-hidden', 'true');
    b.style.left = e.clientX + 'px'; b.style.top = e.clientY + 'px';
    var ring = document.createElement('span'); ring.className = 'ring'; b.appendChild(ring);
    ring.animate(
      [{ transform: 'scale(1)', opacity: 0.9 }, { transform: 'scale(6)', opacity: 0 }],
      { duration: 550, easing: 'ease-out' }
    );
    for (var i = 0; i < 6; i++) {
      var s = document.createElement('span'); s.className = 'spark'; b.appendChild(s);
      var ang = (Math.PI * 2 * i) / 6 + Math.random() * 0.5;
      var dist = 26 + Math.random() * 22;
      s.animate(
        [{ transform: 'translate(0,0)', opacity: 1 },
         { transform: 'translate(' + (Math.cos(ang) * dist).toFixed(1) + 'px,' + (Math.sin(ang) * dist).toFixed(1) + 'px)', opacity: 0 }],
        { duration: 520, easing: 'ease-out' }
      );
    }
    document.body.appendChild(b);
    setTimeout(function () { b.remove(); }, 640);
  });

  /* ---- Query this page (v5, Nov 2026) ------------------------------------
     A small SQL console over the page's own records. Four parts, in order:

       1. TABLES   Built from the HTML above when the page loads, never
                   typed in twice. A copy edit to a card changes the table
                   with it. Each row keeps the element it was read from
                   (row._src), which is what Trace follows.
       2. LEXER    Strings in single quotes ('' escapes a quote), numbers,
                   identifiers, and operators.
       3. PARSER   Recursive descent over a deliberately small grammar:
                     SELECT [DISTINCT] cols FROM t [WHERE e] [GROUP BY e,...]
                       [ORDER BY e [ASC|DESC],...] [LIMIT n]
                     SHOW TABLES | DESCRIBE t | HELP
                   Expressions: = != <> < <= > >=, [NOT] LIKE, [NOT] IN,
                   IS [NOT] NULL, AND, OR, NOT, parentheses; aggregates
                   COUNT(*), COUNT([DISTINCT] x), MIN, MAX, SUM, AVG; and
                   LOWER, UPPER, LENGTH, YEAR.
       4. EXECUTOR scan -> filter -> group -> project -> distinct -> sort
                   -> limit, recording each step as the plan line shown
                   under the editor.

     Semantics follow SQL where it matters to a reader: NULL compares as
     unknown, so it never matches = or LIKE; text comparison ignores case;
     NULLs sort last in both directions. Errors name what went wrong and
     suggest the nearest table or column when the name is a typo.

     Everything renders through textContent and createElement, so nothing
     a visitor types is ever parsed as HTML. */
  (function () {
    var form = document.getElementById('sqlForm');
    var input = document.getElementById('sqlInput');
    var statusEl = document.getElementById('sqlStatus');
    var resultEl = document.getElementById('sqlResult');
    var examplesEl = document.getElementById('sqlExamples');
    var tablesEl = document.getElementById('sqlTables');
    var completeEl = document.getElementById('sqlComplete');
    var backBtn = document.getElementById('backToQuery');
    var section = document.getElementById('query');
    if (!form || !input || !statusEl || !resultEl || !section) return;
    if (!completeEl) completeEl = document.createElement('p');

    /* 1. Tables ---------------------------------------------------------- */
    var MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
    function pad2(n) { return (n < 10 ? '0' : '') + n; }
    function monthOf(word) { return MONTHS.indexOf(String(word).slice(0, 3).toLowerCase()) + 1; }
    function txt(el) { return el ? el.textContent.replace(/\s+/g, ' ').trim() : ''; }
    function parts(el) { return txt(el).split(/\s*·\s*/); }
    function all(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
    var now = new Date();
    var today = now.getFullYear() + '-' + pad2(now.getMonth() + 1) + '-' + pad2(now.getDate());

    // First real date in a string, as ISO: "July 8, 2026" -> 2026-07-08,
    // "Sep 2022" -> 2022-09, and "Jul 8" -> 2026-07-08 given a year.
    // Words that are not months ("ASIA 2026") are skipped, not misread.
    function isoDate(text, year) {
      var m, re = /([A-Za-z]{3,9})\.?\s+(\d{1,2}),\s*(\d{4})/g;
      while ((m = re.exec(text))) if (monthOf(m[1])) return m[3] + '-' + pad2(monthOf(m[1])) + '-' + pad2(+m[2]);
      re = /([A-Za-z]{3,9})\s+(\d{4})\b/g;
      while ((m = re.exec(text))) if (monthOf(m[1])) return m[2] + '-' + pad2(monthOf(m[1]));
      if (year) {
        re = /([A-Za-z]{3,9})\.?\s+(\d{1,2})\b/g;
        while ((m = re.exec(text))) if (monthOf(m[1])) return year + '-' + pad2(monthOf(m[1])) + '-' + pad2(+m[2]);
      }
      return null;
    }
    // Inclusive month count between two YYYY-MM values, as LinkedIn counts.
    function monthsBetween(a, b) {
      if (!a || !b) return null;
      return (+b.slice(0, 4) - +a.slice(0, 4)) * 12 + (+b.slice(5, 7) - +a.slice(5, 7)) + 1;
    }

    var TABLES = {};
    function defineTable(name, about, cols, build) {
      var rows;
      // One broken section must not take the console down with it.
      try { rows = build(); } catch (e) { rows = []; }
      TABLES[name] = { name: name, about: about, cols: cols, rows: rows };
    }

    // Writing, talks, and featured quotes all open with the same publisher
    // masthead (.pub-name, .pub-kind, then the date), so they read alike.
    function masthead(el) {
      return {
        name: txt(el.querySelector('.pub-name')) || null,
        kind: txt(el.querySelector('.pub-kind')).toLowerCase() || null
      };
    }
    defineTable('writing', 'Articles, the roundtable, and the build log', ['outlet', 'kind', 'title', 'date', 'url'], function () {
      return all('#writing .card').map(function (card) {
        var m = masthead(card);
        var link = card.querySelector('a[href^="http"]');
        return { outlet: m.name, kind: m.kind, title: txt(card.querySelector('h3')) || null, date: isoDate(txt(card.querySelector('.pub-date'))), url: link ? link.href : null, _src: [card] };
      });
    });
    defineTable('talks', 'Conference talks and papers, past and upcoming', ['venue', 'kind', 'title', 'date', 'status'], function () {
      return all('#speaking .talk').map(function (card) {
        var m = masthead(card);
        var d = isoDate(txt(card.querySelector('.pub-date')));
        return { venue: m.name, kind: m.kind, title: txt(card.querySelector('h3')) || null, date: d, status: d ? (d < today ? 'delivered' : 'upcoming') : null, _src: [card] };
      });
    });
    defineTable('featured', 'Expert quotes in the press', ['outlet', 'kind', 'title', 'date', 'url'], function () {
      return all('#featured .slide').map(function (fig) {
        var cap = fig.querySelector('figcaption');
        var m = cap ? masthead(cap) : { name: null, kind: null };
        var link = cap && cap.querySelector('a[href^="http"]');
        return { outlet: m.name, kind: m.kind, title: txt(link) || null, date: isoDate(txt(cap)), url: link ? link.href : null, _src: [fig] };
      });
    });
    defineTable('spans', 'The 2026 trace, one row per span', ['label', 'result', 'date', 'kind'], function () {
      var year = (/\d{4}/.exec(txt(document.querySelector('#trace h2'))) || [])[0];
      return all('#trace .trace-row').map(function (row) {
        var when = parts(row.querySelector('.trace-date'));
        return { label: txt(row.querySelector('.trace-label')) || null, result: txt(row.querySelector('.trace-result')) || null, date: isoDate(when[0], year), kind: when[1] ? when[1].toLowerCase() : null, _src: [row] };
      });
    });
    defineTable('roles', 'Experience, one row per role', ['company', 'title', 'start', 'end', 'months', 'location'], function () {
      var thisMonth = today.slice(0, 7);
      return all('#experience .role-block').map(function (block) {
        var m = parts(block.querySelector('.meta'));
        var h = parts(block.querySelector('h3'));
        var range = (h[1] || '').split(/\s+to\s+/i);
        var start = isoDate(range[0]);
        var end = range.length > 1 ? (/present/i.test(range[1]) ? null : isoDate(range[1])) : start;
        return { company: m[0] || null, title: h[0] || null, start: start, end: end, months: monthsBetween(start, end || thisMonth), location: m[1] || null, _src: [block] };
      });
    });
    defineTable('education', 'Degrees', ['school', 'degree', 'start', 'end'], function () {
      return all('#education .role-block').map(function (block) {
        var p = parts(block.querySelector('p'));
        var range = (p[1] || '').split(/\s+to\s+/i);
        return { school: txt(block.querySelector('h3')) || null, degree: p[0] || null, start: isoDate(range[0]), end: range[1] ? isoDate(range[1]) : null, _src: [block] };
      });
    });
    defineTable('case_files', 'Engineering case files at Amazon', ['slug', 'title', 'area', 'years', 'headline'], function () {
      return all('#engineering .case').map(function (art) {
        var m = parts(art.querySelector('.meta'));
        var first = art.querySelector('.impact-row div');
        return { slug: art.id.replace(/^case-/, ''), title: txt(art.querySelector('h3')) || null, area: m[1] || null, years: m[2] || null, headline: first ? txt(first.querySelector('strong')) + ' ' + txt(first.querySelector('span')) : null, _src: [art] };
      });
    });
    defineTable('skills', 'What I work on, one row per skill', ['name'], function () {
      return all('#work .chips li').map(function (li) { return { name: txt(li), _src: [li] }; });
    });
    var TABLE_NAMES = Object.keys(TABLES);

    function typeOf(table, col) {
      var t = null;
      for (var i = 0; i < table.rows.length; i++) {
        var v = table.rows[i][col];
        if (v == null) continue;
        var k = typeof v === 'number' ? 'int' : (/^\d{4}-\d{2}(-\d{2})?$/.test(v) ? 'date' : 'text');
        if (t && t !== k) return 'text';
        t = k;
      }
      return t || 'text';
    }

    /* 2. Lexer ----------------------------------------------------------- */
    function SqlError(message) { this.message = message; }
    var TOKEN = /\s+|--[^\n]*|'((?:[^']|'')*)'|(\d+(?:\.\d+)?)|([A-Za-z_][A-Za-z0-9_]*)|(<=|>=|<>|!=|[=<>*,();.-])/y;
    function lex(src) {
      var toks = [], pos = 0, m;
      while (pos < src.length) {
        TOKEN.lastIndex = pos;
        m = TOKEN.exec(src);
        if (!m) {
          if (src.charAt(pos) === "'") throw new SqlError('The text that starts at character ' + (pos + 1) + ' never closes. Add a closing single quote.');
          if (src.charAt(pos) === '"') throw new SqlError('Use single quotes for text, like \'upcoming\'. Double quotes are not supported here.');
          throw new SqlError('Unexpected character "' + src.charAt(pos) + '" at position ' + (pos + 1) + '.');
        }
        pos = TOKEN.lastIndex;
        if (m[1] !== undefined) toks.push({ t: 'str', v: m[1].replace(/''/g, "'") });
        else if (m[2] !== undefined) toks.push({ t: 'num', v: parseFloat(m[2]) });
        else if (m[3] !== undefined) toks.push({ t: 'id', v: m[3], u: m[3].toUpperCase() });
        else if (m[4] !== undefined) toks.push({ t: 'op', v: m[4] });
      }
      toks.push({ t: 'eof' });
      return toks;
    }

    /* 3. Parser ---------------------------------------------------------- */
    var RESERVED = ['SELECT', 'DISTINCT', 'FROM', 'WHERE', 'GROUP', 'BY', 'ORDER', 'LIMIT', 'AND', 'OR', 'NOT', 'LIKE', 'IN', 'IS', 'NULL', 'AS', 'ASC', 'DESC'];
    var AGGREGATES = ['COUNT', 'MIN', 'MAX', 'SUM', 'AVG'];
    var FUNCTIONS = ['LOWER', 'UPPER', 'LENGTH', 'YEAR'];

    function parse(src) {
      var toks = lex(src), i = 0;
      function peek(k) { return toks[Math.min(i + (k || 0), toks.length - 1)]; }
      function isKw(word, k) { var t = peek(k); return t.t === 'id' && t.u === word; }
      function accept(word) { if (isKw(word)) { i++; return true; } return false; }
      function isOp(v) { var t = peek(); return t.t === 'op' && t.v === v; }
      function acceptOp(v) { if (isOp(v)) { i++; return true; } return false; }
      function near() {
        var t = peek();
        if (t.t === 'eof') return 'at the end of the query';
        return 'near ' + (t.t === 'str' ? "'" + t.v + "'" : '"' + t.v + '"');
      }
      function expectKw(word, tip) { if (!accept(word)) throw new SqlError('Expected ' + word + ' ' + near() + '.' + (tip ? ' ' + tip : '')); }
      function expectOp(v) { if (!acceptOp(v)) throw new SqlError('Expected "' + v + '" ' + near() + '.'); }
      function name(what) {
        var t = peek();
        if (t.t !== 'id' || RESERVED.indexOf(t.u) !== -1) throw new SqlError('Expected ' + what + ' ' + near() + '.');
        i++;
        return t.v;
      }
      function end() {
        acceptOp(';');
        if (peek().t !== 'eof') throw new SqlError('Unexpected ' + near().replace(/^near /, '') + ' after the end of the query.');
      }

      function expr() { return orExpr(); }
      function orExpr() { var a = andExpr(); while (accept('OR')) a = { k: 'or', a: a, b: andExpr() }; return a; }
      function andExpr() { var a = notExpr(); while (accept('AND')) a = { k: 'and', a: a, b: notExpr() }; return a; }
      function notExpr() { return accept('NOT') ? { k: 'not', a: notExpr() } : compare(); }
      function compare() {
        var a = primary(), t = peek();
        if (t.t === 'op' && /^(=|!=|<>|<|<=|>|>=)$/.test(t.v)) {
          i++;
          return { k: 'cmp', op: t.v === '<>' ? '!=' : t.v, a: a, b: primary() };
        }
        var neg = false;
        if (isKw('NOT') && (isKw('LIKE', 1) || isKw('IN', 1))) { i++; neg = true; }
        if (accept('LIKE')) return { k: 'like', a: a, b: primary(), neg: neg };
        if (accept('IN')) {
          expectOp('(');
          var list = [];
          do { list.push(primary()); } while (acceptOp(','));
          expectOp(')');
          return { k: 'in', a: a, list: list, neg: neg };
        }
        if (accept('IS')) { var not = accept('NOT'); expectKw('NULL'); return { k: 'isnull', a: a, neg: not }; }
        return a;
      }
      function primary() {
        var t = peek();
        if (t.t === 'num' || t.t === 'str') { i++; return { k: 'lit', v: t.v }; }
        if (t.t === 'op' && t.v === '-' && peek(1).t === 'num') { i += 2; return { k: 'lit', v: -toks[i - 1].v }; }
        if (acceptOp('(')) { var inner = expr(); expectOp(')'); return inner; }
        if (t.t === 'id' && t.u === 'NULL') { i++; return { k: 'lit', v: null }; }
        if (t.t === 'id' && peek(1).t === 'op' && peek(1).v === '(') {
          i += 2;
          if (AGGREGATES.indexOf(t.u) !== -1) {
            var node = { k: 'agg', fn: t.u, arg: null, distinct: false };
            if (!(t.u === 'COUNT' && acceptOp('*'))) { node.distinct = accept('DISTINCT'); node.arg = expr(); }
            expectOp(')');
            return node;
          }
          if (FUNCTIONS.indexOf(t.u) !== -1) {
            var arg = expr();
            expectOp(')');
            return { k: 'fn', fn: t.u, arg: arg };
          }
          throw new SqlError(t.v + '() is not a function here. Available: ' + AGGREGATES.concat(FUNCTIONS).join(', ') + '.');
        }
        if (t.t === 'id' && RESERVED.indexOf(t.u) === -1) { i++; return { k: 'col', name: t.v }; }
        throw new SqlError('Expected a column name or a value ' + near() + '.');
      }

      if (peek().t === 'eof') throw new SqlError('The query is empty. Try SELECT * FROM writing.');
      if (accept('HELP')) { end(); return { type: 'help' }; }
      if (accept('SHOW')) {
        if (!accept('TABLES')) throw new SqlError('Did you mean SHOW TABLES?');
        end();
        return { type: 'show' };
      }
      if (accept('DESCRIBE') || accept('DESC')) { var tn = name('a table name'); end(); return { type: 'describe', table: tn }; }

      expectKw('SELECT', 'A query starts with SELECT, SHOW TABLES, DESCRIBE, or HELP.');
      var q = { type: 'select', distinct: accept('DISTINCT'), star: false, cols: [] };
      if (acceptOp('*')) q.star = true;
      else {
        do {
          var e = expr(), alias = null;
          if (accept('AS')) alias = name('a column alias');
          else if (peek().t === 'id' && RESERVED.indexOf(peek().u) === -1) alias = toks[i++].v;
          q.cols.push({ e: e, alias: alias });
        } while (acceptOp(','));
      }
      expectKw('FROM', 'Every query reads FROM a table. SHOW TABLES lists them.');
      q.from = name('a table name');
      if (accept('WHERE')) q.where = expr();
      if (accept('GROUP')) { expectKw('BY'); q.group = []; do { q.group.push(expr()); } while (acceptOp(',')); }
      if (accept('ORDER')) {
        expectKw('BY');
        q.order = [];
        do {
          var oe = expr(), desc = false;
          if (accept('DESC')) desc = true; else accept('ASC');
          q.order.push({ e: oe, desc: desc });
        } while (acceptOp(','));
      }
      if (accept('LIMIT')) {
        var lt = peek();
        if (lt.t !== 'num' || lt.v % 1 !== 0) throw new SqlError('LIMIT takes a whole number, like LIMIT 5.');
        i++;
        q.limit = lt.v;
      }
      end();
      return q;
    }

    /* 4. Executor -------------------------------------------------------- */
    // Text for an expression: the column header when there is no alias,
    // and how ORDER BY COUNT(*) finds the matching output column.
    function show(e) {
      switch (e.k) {
        case 'col': return e.name.toLowerCase();
        case 'lit': return e.v === null ? 'NULL' : (typeof e.v === 'string' ? "'" + e.v + "'" : String(e.v));
        case 'agg': return e.fn + '(' + (e.arg ? (e.distinct ? 'DISTINCT ' : '') + show(e.arg) : '*') + ')';
        case 'fn': return e.fn + '(' + show(e.arg) + ')';
        case 'cmp': return show(e.a) + ' ' + e.op + ' ' + show(e.b);
        case 'like': return show(e.a) + (e.neg ? ' NOT' : '') + ' LIKE ' + show(e.b);
        case 'in': return show(e.a) + (e.neg ? ' NOT' : '') + ' IN (' + e.list.map(show).join(', ') + ')';
        case 'isnull': return show(e.a) + ' IS ' + (e.neg ? 'NOT ' : '') + 'NULL';
        case 'and': return show(e.a) + ' AND ' + show(e.b);
        case 'or': return show(e.a) + ' OR ' + show(e.b);
        case 'not': return 'NOT ' + show(e.a);
      }
      return '?';
    }
    function walk(e, fn, inAgg) {
      if (!e) return;
      fn(e, inAgg);
      var inside = inAgg || e.k === 'agg';
      walk(e.a, fn, inside); walk(e.b, fn, inside); walk(e.arg, fn, inside);
      if (e.list) e.list.forEach(function (x) { walk(x, fn, inside); });
    }
    function hasAggregate(e) { var found = false; walk(e, function (n) { if (n.k === 'agg') found = true; }); return found; }

    // Edit distance that counts a swap of two neighbouring letters as one
    // edit (optimal string alignment), so "titel" is one step from
    // "title". Plain Levenshtein scores that typo as two and misses it.
    function distance(a, b) {
      var d = [], i, j;
      for (i = 0; i <= a.length; i++) { d[i] = [i]; }
      for (j = 0; j <= b.length; j++) d[0][j] = j;
      for (i = 1; i <= a.length; i++) {
        for (j = 1; j <= b.length; j++) {
          var cost = a.charAt(i - 1) === b.charAt(j - 1) ? 0 : 1;
          d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost);
          if (i > 1 && j > 1 && a.charAt(i - 1) === b.charAt(j - 2) && a.charAt(i - 2) === b.charAt(j - 1)) d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + 1);
        }
      }
      return d[a.length][b.length];
    }
    function didYouMean(word, options) {
      var best = null, bestD = Infinity, w = word.toLowerCase();
      options.forEach(function (o) { var d = distance(w, o); if (d < bestD) { bestD = d; best = o; } });
      return best && bestD <= Math.max(1, Math.floor(w.length / 3)) ? ' Did you mean ' + best + '?' : '';
    }
    function tableFor(nameRaw) {
      var t = TABLES[nameRaw.toLowerCase()];
      if (!t) throw new SqlError('There is no table named ' + nameRaw + '.' + (didYouMean(nameRaw, TABLE_NAMES) || ' Tables: ' + TABLE_NAMES.join(', ') + '.'));
      return t;
    }
    function checkColumns(e, table) {
      walk(e, function (n) {
        if (n.k === 'col' && table.cols.indexOf(n.name.toLowerCase()) === -1) {
          throw new SqlError('Table ' + table.name + ' has no column ' + n.name + '.' + (didYouMean(n.name, table.cols) || ' Its columns: ' + table.cols.join(', ') + '.'));
        }
      });
    }

    // Text compares without case; numbers compare as numbers, including
    // a number against numeric text; NULL sorts after everything.
    function order(a, b) {
      if (a == null || b == null) return a == null ? (b == null ? 0 : 1) : -1;
      if (typeof a === 'number' && typeof b === 'number') return a - b;
      if ((typeof a === 'number' || typeof b === 'number') && !isNaN(+a) && !isNaN(+b) && a !== '' && b !== '') return +a - +b;
      var x = String(a).toLowerCase(), y = String(b).toLowerCase();
      return x < y ? -1 : (x > y ? 1 : 0);
    }
    function truthy(v) { return v === true || (typeof v === 'number' && v !== 0); }
    function likeToRegex(pattern) {
      var out = '';
      String(pattern).split('').forEach(function (c) {
        out += c === '%' ? '[\\s\\S]*' : (c === '_' ? '[\\s\\S]' : c.replace(/[.*+?^${}()|[\]\\\/]/g, '\\$&'));
      });
      return new RegExp('^' + out + '$', 'i');
    }

    function evaluate(e, row, aggs) {
      var a, b;
      switch (e.k) {
        case 'lit': return e.v;
        case 'col': a = row[e.name.toLowerCase()]; return a === undefined ? null : a;
        case 'agg': return aggs ? aggs[e.id] : null;
        case 'fn':
          a = evaluate(e.arg, row, aggs);
          if (a == null) return null;
          if (e.fn === 'LOWER') return String(a).toLowerCase();
          if (e.fn === 'UPPER') return String(a).toUpperCase();
          if (e.fn === 'LENGTH') return String(a).length;
          b = parseInt(String(a).slice(0, 4), 10);
          return isNaN(b) ? null : b;
        case 'cmp':
          a = evaluate(e.a, row, aggs); b = evaluate(e.b, row, aggs);
          if (a == null || b == null) return null;
          var c = order(a, b);
          return e.op === '=' ? c === 0 : e.op === '!=' ? c !== 0 : e.op === '<' ? c < 0 : e.op === '<=' ? c <= 0 : e.op === '>' ? c > 0 : c >= 0;
        case 'like':
          a = evaluate(e.a, row, aggs); b = evaluate(e.b, row, aggs);
          if (a == null || b == null) return null;
          return likeToRegex(b).test(String(a)) !== e.neg;
        case 'in':
          a = evaluate(e.a, row, aggs);
          if (a == null) return null;
          var hit = e.list.some(function (x) { var v = evaluate(x, row, aggs); return v != null && order(a, v) === 0; });
          return hit !== e.neg;
        case 'isnull': return (evaluate(e.a, row, aggs) == null) !== e.neg;
        case 'not': a = evaluate(e.a, row, aggs); return a == null ? null : !truthy(a);
        case 'and':
          a = evaluate(e.a, row, aggs); b = evaluate(e.b, row, aggs);
          if (a === false || b === false) return false;
          return a == null || b == null ? null : truthy(a) && truthy(b);
        case 'or':
          a = evaluate(e.a, row, aggs); b = evaluate(e.b, row, aggs);
          if (truthy(a) || truthy(b)) return true;
          return a == null || b == null ? null : false;
      }
      return null;
    }

    function aggregate(node, rows) {
      var vals = node.arg ? rows.map(function (r) { return evaluate(node.arg, r); }).filter(function (v) { return v != null; }) : rows;
      if (node.distinct) {
        var seen = {};
        vals = vals.filter(function (v) { var key = typeof v + ':' + String(v).toLowerCase(); if (seen[key]) return false; seen[key] = true; return true; });
      }
      if (node.fn === 'COUNT') return vals.length;
      if (!vals.length) return null;
      if (node.fn === 'MIN') return vals.reduce(function (m, v) { return order(v, m) < 0 ? v : m; });
      if (node.fn === 'MAX') return vals.reduce(function (m, v) { return order(v, m) > 0 ? v : m; });
      var nums = vals.map(Number);
      if (nums.some(isNaN)) throw new SqlError(node.fn + '() needs a number column, such as months in roles.');
      var sum = nums.reduce(function (s, v) { return s + v; }, 0);
      return node.fn === 'SUM' ? sum : Math.round((sum / nums.length) * 100) / 100;
    }

    function plural(n, word) { return n + ' ' + word + (n === 1 ? '' : 's'); }

    function runSelect(q) {
      var table = tableFor(q.from);
      var cols = q.star ? table.cols.map(function (c) { return { e: { k: 'col', name: c }, alias: null }; }) : q.cols;
      cols.forEach(function (c) { checkColumns(c.e, table); });
      if (q.where) {
        checkColumns(q.where, table);
        if (hasAggregate(q.where)) throw new SqlError('Aggregates like COUNT() belong in SELECT, not WHERE.');
      }
      (q.group || []).forEach(function (g) {
        checkColumns(g, table);
        if (hasAggregate(g)) throw new SqlError('GROUP BY takes columns, not aggregates.');
      });
      var labels = cols.map(function (c) { return c.alias || show(c.e); });
      var plan = ['scan ' + table.name + ' (' + plural(table.rows.length, 'row') + ')'];

      var rows = table.rows;
      if (q.where) {
        rows = rows.filter(function (r) { return truthy(evaluate(q.where, r)); });
        plan.push('filter (' + rows.length + ' kept)');
      }

      // Resolve ORDER BY keys before grouping: a key may name an output
      // column (by alias, header, or position) or be its own expression.
      var orderKeys = (q.order || []).map(function (o) {
        if (o.e.k === 'lit' && typeof o.e.v === 'number') {
          if (o.e.v < 1 || o.e.v > cols.length || o.e.v % 1) throw new SqlError('ORDER BY ' + o.e.v + ' points past the ' + plural(cols.length, 'selected column') + '.');
          return { index: o.e.v - 1, desc: o.desc, label: labels[o.e.v - 1] };
        }
        var wanted = show(o.e).toLowerCase();
        for (var li = 0; li < labels.length; li++) if (labels[li].toLowerCase() === wanted) return { index: li, desc: o.desc, label: labels[li] };
        checkColumns(o.e, table);
        return { e: o.e, desc: o.desc, label: show(o.e) };
      });

      var aggNodes = [];
      function collect(e) { walk(e, function (n) { if (n.k === 'agg' && aggNodes.indexOf(n) === -1) { n.id = aggNodes.length; aggNodes.push(n); } }); }
      cols.forEach(function (c) { collect(c.e); });
      orderKeys.forEach(function (k) { if (k.e) collect(k.e); });

      var grouped = !!q.group || aggNodes.length > 0;
      var out = [];
      if (grouped) {
        // In a grouped query a bare column must be one of the groups:
        // otherwise its value would come from an arbitrary row.
        var groupShows = (q.group || []).map(function (g) { return show(g).toLowerCase(); });
        var checkBare = function (e, where) {
          if (groupShows.indexOf(show(e).toLowerCase()) !== -1) return;
          walk(e, function (n, inAgg) {
            if (n.k === 'col' && !inAgg && groupShows.indexOf(show(n)) === -1) {
              throw new SqlError(n.name + ' in ' + where + ' needs to be in GROUP BY, or inside an aggregate like MIN(' + n.name + ').');
            }
          });
        };
        cols.forEach(function (c) { checkBare(c.e, 'SELECT'); });
        orderKeys.forEach(function (k) { if (k.e) checkBare(k.e, 'ORDER BY'); });

        var groups = {}, keys = [];
        rows.forEach(function (r) {
          var key = JSON.stringify((q.group || []).map(function (g) { var v = evaluate(g, r); return typeof v === 'string' ? v.toLowerCase() : v; }));
          if (!groups[key]) { groups[key] = []; keys.push(key); }
          groups[key].push(r);
        });
        if (!q.group && !keys.length) { groups['[]'] = []; keys.push('[]'); }
        plan.push(q.group ? 'group by ' + q.group.map(show).join(', ') + ' (' + plural(keys.length, 'group') + ')' : 'aggregate');
        keys.forEach(function (key) {
          var members = groups[key], aggs = {};
          aggNodes.forEach(function (n) { aggs[n.id] = aggregate(n, members); });
          var base = members[0] || {};
          out.push({
            vals: cols.map(function (c) { return evaluate(c.e, base, aggs); }),
            base: base, aggs: aggs,
            src: members.reduce(function (acc, r) { return acc.concat(r._src || []); }, [])
          });
        });
      } else {
        out = rows.map(function (r) { return { vals: cols.map(function (c) { return evaluate(c.e, r); }), base: r, src: r._src || [] }; });
      }

      if (q.distinct) {
        var seen = {}, kept = [];
        out.forEach(function (r) {
          var key = JSON.stringify(r.vals.map(function (v) { return typeof v === 'string' ? v.toLowerCase() : v; }));
          if (seen[key]) { seen[key].src = seen[key].src.concat(r.src); return; }
          seen[key] = r; kept.push(r);
        });
        out = kept;
        plan.push('distinct (' + plural(out.length, 'row') + ')');
      }

      if (orderKeys.length) {
        var keyOf = function (k, r) { return k.e ? evaluate(k.e, r.base, r.aggs) : r.vals[k.index]; };
        out.sort(function (x, y) {
          for (var ki = 0; ki < orderKeys.length; ki++) {
            var k = orderKeys[ki], a = keyOf(k, x), b = keyOf(k, y);
            if (a == null || b == null) { if (a == null && b == null) continue; return a == null ? 1 : -1; }
            var c = order(a, b);
            if (c) return k.desc ? -c : c;
          }
          return 0;
        });
        plan.push('sort by ' + orderKeys.map(function (k) { return k.label + (k.desc ? ' desc' : ''); }).join(', '));
      }
      if (q.limit != null) { out = out.slice(0, q.limit); plan.push('limit ' + q.limit); }

      // "= NULL" is the classic SQL slip: it is never true, so it quietly
      // returns nothing. When that is why a result is empty, say so.
      var hint = null;
      if (!out.length && q.where) {
        walk(q.where, function (n) {
          if (n.k === 'cmp' && ((n.a.k === 'lit' && n.a.v === null) || (n.b.k === 'lit' && n.b.v === null))) {
            hint = 'No rows matched. A comparison with NULL is never true; use IS NULL or IS NOT NULL instead.';
          }
        });
      }
      return { cols: labels, rows: out.map(function (r) { return { vals: r.vals, src: r.src }; }), plan: plan, hint: hint };
    }

    function runMeta(q) {
      if (q.type === 'show') {
        return {
          cols: ['table', 'rows', 'columns', 'holds'],
          rows: TABLE_NAMES.map(function (n) {
            var t = TABLES[n];
            return { vals: [n, t.rows.length, t.cols.join(', '), t.about], run: { label: 'Browse', sql: 'SELECT * FROM ' + n } };
          }),
          plan: ['list ' + plural(TABLE_NAMES.length, 'table')]
        };
      }
      if (q.type === 'describe') {
        var t = tableFor(q.table);
        return {
          cols: ['column', 'type', 'example'],
          rows: t.cols.map(function (c) {
            var ex = null;
            for (var r = 0; r < t.rows.length && ex == null; r++) ex = t.rows[r][c];
            return { vals: [c, typeOf(t, c), ex] };
          }),
          plan: ['describe ' + t.name + ' (' + plural(t.rows.length, 'row') + ')']
        };
      }
      var help = [
        ['Pick columns', 'SELECT title, date FROM writing'],
        ['Filter rows', "SELECT * FROM writing WHERE date >= '2026-08-01'"],
        ['Match text', "SELECT name FROM skills WHERE name LIKE '%aws%'"],
        ['Sets and blanks', 'SELECT company, title FROM roles WHERE end IS NULL'],
        ['Count by group', 'SELECT kind, COUNT(*) AS spans FROM spans GROUP BY kind'],
        ['Sort and trim', 'SELECT company, months FROM roles ORDER BY months DESC LIMIT 2'],
        ['Unique values', 'SELECT DISTINCT kind FROM spans'],
        ['Functions', 'SELECT UPPER(slug), LENGTH(title) FROM case_files'],
        ['Explore', 'DESCRIBE roles']
      ];
      return {
        cols: ['to', 'try'],
        rows: help.map(function (h) { return { vals: h, run: { label: 'Run', sql: h[1] } }; }),
        plan: ['aggregates: ' + AGGREGATES.join(', ') + '; functions: ' + FUNCTIONS.join(', ')]
      };
    }

    function run(sql) {
      var t0 = performance.now();
      var q = parse(sql);
      var res = q.type === 'select' ? runSelect(q) : runMeta(q);
      res.ms = performance.now() - t0;
      return res;
    }

    /* Rendering ---------------------------------------------------------- */
    function cell(td, v) {
      if (v == null) { td.textContent = 'NULL'; td.className = 'sql-null'; return; }
      if (typeof v === 'string' && /^https?:\/\//.test(v)) {
        var a = document.createElement('a');
        a.href = v; a.target = '_blank'; a.rel = 'noopener'; a.title = v;
        try { a.textContent = new URL(v).hostname.replace(/^www\./, ''); } catch (e) { a.textContent = v; }
        td.className = 'sql-link';
        td.appendChild(a);
        return;
      }
      if (typeof v === 'number') td.className = 'sql-num';
      else if (/^\d{4}-\d{2}(-\d{2})?$/.test(v)) td.className = 'sql-date';
      td.textContent = String(v);
    }

    function render(res) {
      resultEl.textContent = '';
      var table = document.createElement('table');
      table.className = 'sql-table';
      var head = table.createTHead().insertRow();
      res.cols.forEach(function (c) { var th = document.createElement('th'); th.scope = 'col'; th.textContent = c; head.appendChild(th); });
      var actions = res.rows.some(function (r) { return r.run || (r.src && r.src.length); });
      if (actions) {
        var th = document.createElement('th');
        th.scope = 'col';
        var sr = document.createElement('span'); sr.className = 'sr-only'; sr.textContent = 'Action';
        th.appendChild(sr);
        head.appendChild(th);
      }
      var body = table.createTBody();
      res.rows.forEach(function (r, ri) {
        var tr = body.insertRow();
        r.vals.forEach(function (v) { cell(tr.insertCell(), v); });
        if (!actions) return;
        var td = tr.insertCell();
        td.className = 'sql-action';
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'sql-row-btn';
        if (r.run) {
          b.textContent = r.run.label;
          b.setAttribute('aria-label', r.run.label + ': ' + r.run.sql);
          b.addEventListener('click', function () { execute(r.run.sql); input.focus(); });
        } else if (r.src && r.src.length) {
          b.textContent = 'Trace';
          b.setAttribute('aria-label', 'Trace row ' + (ri + 1) + ' to where it appears on the page');
          b.addEventListener('click', function () { traceTo(r.src, b); });
        } else return;
        td.appendChild(b);
      });
      if (!res.rows.length) {
        var empty = body.insertRow().insertCell();
        empty.colSpan = res.cols.length;
        empty.className = 'sql-empty';
        empty.textContent = res.hint || 'No rows matched. Loosen the WHERE clause, or run SHOW TABLES to see what is here.';
      }
      resultEl.appendChild(table);
      resultEl.scrollTop = 0;
    }

    function setStatus(res) {
      statusEl.className = 'sql-status';
      statusEl.textContent = '';
      var count = document.createElement('strong');
      count.textContent = plural(res.rows.length, 'row');
      statusEl.appendChild(count);
      // Browsers coarsen performance.now() (to 0.1 ms or worse), so a
      // fast query can measure as zero. Say so plainly instead of "0.00".
      var ms = res.ms < 0.1 ? '<0.1' : (res.ms < 10 ? res.ms.toFixed(1) : String(Math.round(res.ms)));
      statusEl.appendChild(document.createTextNode(' in ' + ms + ' ms'));
      var plan = document.createElement('span');
      plan.className = 'sql-plan';
      plan.textContent = res.plan.join(' → ');
      statusEl.appendChild(plan);
    }

    function fail(message) {
      resultEl.textContent = '';
      statusEl.className = 'sql-status sql-error';
      statusEl.textContent = message;
    }

    var history_ = [], hpos = 0, draft = '';
    function execute(sql, opts) {
      opts = opts || {};
      sql = String(sql || '').trim();
      input.value = sql;
      fit();
      completeEl.textContent = '';
      if (!sql) { fail('The query is empty. Try SELECT * FROM writing.'); return; }
      if (!opts.silent && history_[history_.length - 1] !== sql) history_.push(sql);
      hpos = history_.length; draft = '';
      var res;
      try { res = run(sql); }
      catch (e) {
        fail(e instanceof SqlError ? e.message : 'That query hit an error this console does not handle. Try a simpler form, or type HELP.');
        return;
      }
      render(res);
      setStatus(res);
      // The query rides in the URL, so the address bar is always a link
      // to what is on screen. replaceState, not pushState: running ten
      // queries should not trap the Back button on this page.
      if (!opts.silent) { try { history.replaceState(null, '', '#q=' + encodeURIComponent(sql)); } catch (e) {} }
    }

    /* Tracing a row back to the page -------------------------------------- */
    var traceTimer = null, lastTraceBtn = null;
    function traceTo(els, fromBtn) {
      els = els.filter(function (el) { return el && el.isConnected; });
      if (!els.length) return;
      var first = els[0];
      // A quote lives in the carousel: bring its slide forward first.
      var slide = first.closest && first.closest('#quoteCarousel .slide');
      if (slide) {
        var idx = all('#quoteCarousel .slide').indexOf(slide);
        var dot = all('#quoteCarousel .carousel-dot')[idx];
        if (dot) dot.click();
      }
      all('.traced').forEach(function (el) { el.classList.remove('traced'); });
      els.forEach(function (el) { void el.offsetWidth; el.classList.add('traced'); });
      revealNow(first);
      first.scrollIntoView({ block: 'center', behavior: motionOff() ? 'auto' : 'smooth' });
      if (!first.hasAttribute('tabindex')) first.setAttribute('tabindex', '-1');
      try { first.focus({ preventScroll: true }); } catch (e) {}
      clearTimeout(traceTimer);
      traceTimer = setTimeout(function () { all('.traced').forEach(function (el) { el.classList.remove('traced'); }); }, 2800);
      lastTraceBtn = fromBtn || null;
      if (backBtn) backBtn.hidden = false;
    }
    if (backBtn) {
      backBtn.addEventListener('click', function () {
        backBtn.hidden = true;
        section.scrollIntoView({ block: 'start', behavior: motionOff() ? 'auto' : 'smooth' });
        var target = lastTraceBtn && lastTraceBtn.isConnected ? lastTraceBtn : input;
        try { target.focus({ preventScroll: true }); } catch (e) {}
      });
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (es) {
          if (es[0].intersectionRatio >= 0.3) backBtn.hidden = true;
        }, { threshold: [0, 0.3] }).observe(section);
      }
    }

    /* Editor: Enter runs, history, Tab completion, auto-height ------------- */
    function fit() { input.style.height = 'auto'; input.style.height = input.scrollHeight + 'px'; }
    var WORDS = RESERVED.concat(AGGREGATES, FUNCTIONS, ['SHOW', 'TABLES', 'DESCRIBE', 'HELP']);
    function complete() {
      var caret = input.selectionStart;
      if (caret !== input.selectionEnd) return false;
      var before = input.value.slice(0, caret);
      var m = /[A-Za-z_][A-Za-z0-9_]*$/.exec(before);
      if (!m) return false;
      var word = m[0], low = word.toLowerCase();
      var prev = (/([A-Za-z_]+)\s+$/.exec(before.slice(0, before.length - word.length)) || [])[1];
      var wantsTable = prev && /^(from|describe|desc)$/i.test(prev);
      var fromMatch = /\bfrom\s+([A-Za-z_][A-Za-z0-9_]*)/i.exec(input.value);
      var table = fromMatch && TABLES[fromMatch[1].toLowerCase()];
      var pool = [];
      if (wantsTable) pool = TABLE_NAMES.map(function (n) { return { w: n, space: true }; });
      else {
        var colPool = table ? table.cols : TABLE_NAMES.reduce(function (acc, n) { return acc.concat(TABLES[n].cols); }, []);
        colPool.forEach(function (c) { pool.push({ w: c, space: false }); });
        if (!table) TABLE_NAMES.forEach(function (n) { pool.push({ w: n, space: true }); });
        var upper = word === word.toUpperCase();
        WORDS.forEach(function (k) { pool.push({ w: upper ? k : k.toLowerCase(), space: AGGREGATES.indexOf(k) === -1 && FUNCTIONS.indexOf(k) === -1 }); });
      }
      var seen = {};
      var hits = pool.filter(function (p) {
        var key = p.w.toLowerCase();
        if (seen[key] || key.indexOf(low) !== 0 || key === low) return false;
        seen[key] = true;
        return true;
      });
      if (!hits.length) return false;
      var insert;
      if (hits.length === 1) insert = hits[0].w + (hits[0].space ? ' ' : '');
      else {
        // Extend to the longest prefix every candidate shares.
        insert = hits[0].w;
        hits.forEach(function (h) { while (h.w.toLowerCase().indexOf(insert.toLowerCase()) !== 0) insert = insert.slice(0, -1); });
        if (insert.length < word.length) insert = word;
      }
      input.value = before.slice(0, before.length - word.length) + insert + input.value.slice(caret);
      var pos = caret - word.length + insert.length;
      input.setSelectionRange(pos, pos);
      completeEl.textContent = hits.length > 1 ? 'Matches: ' + hits.slice(0, 8).map(function (h) { return h.w; }).join(', ') + (hits.length > 8 ? ', and ' + (hits.length - 8) + ' more' : '') : '';
      fit();
      return true;
    }

    form.addEventListener('submit', function (e) { e.preventDefault(); execute(input.value); });
    window.addEventListener('resize', fit);
    input.addEventListener('input', function () { fit(); completeEl.textContent = ''; });
    input.addEventListener('keydown', function (e) {
      if (e.isComposing) return;
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); execute(input.value); return; }
      // Tab completes when there is a word to complete. Otherwise it
      // moves focus as usual, so keyboard users are never trapped here.
      if (e.key === 'Tab' && !e.shiftKey && !e.altKey && !e.ctrlKey && !e.metaKey) { if (complete()) e.preventDefault(); return; }
      var caret = input.selectionStart, v = input.value;
      if (e.key === 'ArrowUp' && history_.length && v.lastIndexOf('\n', caret - 1) === -1) {
        e.preventDefault();
        if (hpos === history_.length) draft = v;
        hpos = Math.max(0, hpos - 1);
        input.value = history_[hpos];
        fit();
      } else if (e.key === 'ArrowDown' && hpos < history_.length && v.indexOf('\n', caret) === -1) {
        e.preventDefault();
        hpos++;
        input.value = hpos === history_.length ? draft : history_[hpos];
        fit();
      }
    });

    /* Examples and the table list ------------------------------------------ */
    // Canned queries with a plain title, after Datasette: the title says
    // what you will learn, and the SQL is one hover or tap away.
    var EXAMPLES = [
      ['Writing, newest first', 'SELECT outlet, title, date FROM writing ORDER BY date DESC'],
      ['2026 by kind', 'SELECT kind, COUNT(*) AS spans FROM spans GROUP BY kind ORDER BY spans DESC'],
      ['Longest roles', 'SELECT company, title, months FROM roles ORDER BY months DESC LIMIT 3'],
      ['Skills about data', "SELECT name FROM skills WHERE name LIKE '%data%'"],
      ['Upcoming talks', "SELECT venue, title, date FROM talks WHERE status = 'upcoming'"],
      ['Every table', 'SHOW TABLES']
    ];
    if (examplesEl) {
      EXAMPLES.forEach(function (ex) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'sql-chip';
        b.textContent = ex[0];
        b.title = ex[1];
        b.addEventListener('click', function () { execute(ex[1]); });
        examplesEl.appendChild(b);
      });
    }
    if (tablesEl) {
      tablesEl.appendChild(document.createTextNode('Tables: '));
      TABLE_NAMES.forEach(function (n, i) {
        var b = document.createElement('button');
        b.type = 'button';
        b.textContent = n;
        b.setAttribute('aria-label', 'Browse the ' + n + ' table');
        b.addEventListener('click', function () { execute('SELECT * FROM ' + n); });
        tablesEl.appendChild(b);
        if (i < TABLE_NAMES.length - 1) tablesEl.appendChild(document.createTextNode(' '));
      });
    }

    // The palette hands SQL typed into it to this console.
    querySql = function (sql) {
      section.scrollIntoView({ block: 'start', behavior: motionOff() ? 'auto' : 'smooth' });
      execute(sql);
    };

    // Arrive on #q=... and that query runs; otherwise show the first
    // example so the section never opens empty.
    function hashQuery() {
      if (location.hash.indexOf('#q=') !== 0) return '';
      try { return decodeURIComponent(location.hash.slice(3)); } catch (e) { return ''; }
    }
    var deep = hashQuery();
    if (deep) {
      execute(deep);
      setTimeout(function () { section.scrollIntoView({ block: 'start' }); }, 80);
    } else {
      execute(EXAMPLES[0][1], { silent: true });
    }
    // A #q= link opened while already on the page only changes the hash,
    // so there is no reload to pick it up. replaceState above never
    // fires hashchange, so this only reacts to links and the address bar.
    window.addEventListener('hashchange', function () {
      var sql = hashQuery();
      if (!sql || sql === input.value.trim()) return;
      execute(sql);
      section.scrollIntoView({ block: 'start', behavior: motionOff() ? 'auto' : 'smooth' });
    });
  })();

  /* ---- Send a record through the lineage explorer (v5, Nov 2026) -------
     Two buttons under the graph send one record each. The record leaves
     a source (advertiser feeds or clickstream, at random), passes ingest
     and the Spark transform, and pauses at the quality gate while it is
     checked. A clean record continues to the data lake, the API, and
     advertiser analytics. A bad record is indistinguishable until the
     gate: there it turns amber and is routed to Flagged anomalies, and
     nothing downstream sees it.

     Each stage it reaches pulses and writes a line to the pipeline log
     below the graph; the outcome is announced through the existing
     aria-live detail line. Motion is a moving dot following route
     segments with getPointAtLength, so it needs no animation library.
     Under reduced motion the record arrives at once: the log and the
     outcome are the same, there is just no travel. */
  (function () {
    var svg = document.getElementById('lineageSvg');
    var cleanBtn = document.getElementById('sendClean');
    var badBtn = document.getElementById('sendBad');
    var log = document.getElementById('linLog');
    var count = document.getElementById('linCount');
    var detail = document.getElementById('lineageDetail');
    if (!svg || !cleanBtn || !badBtn || !log || !count || !detail || !svg.createSVGPoint) return;
    var NS = 'http://www.w3.org/2000/svg';

    // Route segments, each ending at the stage it delivers to. They trace
    // the drawn edges, passing through each stage box's centre.
    var SEGMENTS = {
      fromFeed: ['M85,70 L150,70 C240,70 240,120 330,120 L400,135', 'ingest'],
      fromClick: ['M85,200 L150,200 C240,200 240,150 330,150 L400,135', 'ingest'],
      toTransform: ['M400,135 L625,135', 'transform'],
      toGate: ['M625,135 L690,120 C750,120 740,110 800,110 L870,110', 'gate'],
      toLake: ['M870,110 C910,110 900,150 880,185 L810,225', 'lake'],
      toApi: ['M810,225 L555,225', 'api'],
      toAnalytics: ['M555,225 L245,225', 'analytics'],
      toAnomaly: ['M870,110 L830,118 L830,140 C830,200 830,215 830,240 L830,261', 'anomaly']
    };
    // Geometry only: invisible paths used to measure the routes.
    var guides = document.createElementNS(NS, 'g');
    guides.setAttribute('class', 'rec-guides');
    guides.setAttribute('aria-hidden', 'true');
    svg.appendChild(guides);
    var layer = document.createElementNS(NS, 'g');
    layer.setAttribute('class', 'rec-layer');
    layer.setAttribute('aria-hidden', 'true');
    svg.appendChild(layer);
    Object.keys(SEGMENTS).forEach(function (key) {
      var p = document.createElementNS(NS, 'path');
      p.setAttribute('d', SEGMENTS[key][0]);
      guides.appendChild(p);
      SEGMENTS[key].path = p;
      SEGMENTS[key].len = p.getTotalLength();
    });

    var CHECKS = ['null campaign_id', 'schema drift: spend arrived as text', 'event time three days late', 'duplicate event_id'];
    var now = new Date();
    var partition = now.getFullYear() + '-' + ('0' + (now.getMonth() + 1)).slice(-2) + '-' + ('0' + now.getDate()).slice(-2);
    var SAY = {
      ingest: function (r) { return 'arrived from ' + r.source + ', stamped with source and arrival time'; },
      transform: function () { return 'joined to its campaign and deduplicated'; },
      gate: function (r) { return r.bad ? 'failed check: ' + r.check : 'passed freshness, volume, and schema checks'; },
      lake: function () { return 'written to partition dt=' + partition; },
      api: function () { return 'available to certified consumers'; },
      analytics: function () { return 'counted in advertiser analytics'; },
      anomaly: function () { return 'held for review with the failing check attached'; }
    };
    var passed = 0, flagged = 0, seq = 0;

    function clock() {
      var d = new Date();
      function two(n) { return ('0' + n).slice(-2); }
      return two(d.getHours()) + ':' + two(d.getMinutes()) + ':' + two(d.getSeconds()) + '.' + ('00' + d.getMilliseconds()).slice(-3);
    }
    function writeLog(r, stage, failed) {
      var li = document.createElement('li');
      if (failed) li.className = 'fail';
      var t = document.createElement('time'); t.textContent = clock();
      var s = document.createElement('b'); s.textContent = stage;
      var m = document.createElement('span'); m.textContent = r.id + ' ' + SAY[stage](r);
      li.appendChild(t); li.appendChild(s); li.appendChild(m);
      log.appendChild(li);
      while (log.children.length > 8) log.removeChild(log.firstChild);
      log.hidden = false;
    }
    function pulse(stage, cls) {
      var n = svg.querySelector('.lnode[data-node="' + stage + '"]');
      if (!n) return;
      n.classList.remove('hit', 'fail');
      n.getBoundingClientRect();
      n.classList.add(cls);
      clearTimeout(n._pulse);
      n._pulse = setTimeout(function () { n.classList.remove(cls); }, 650);
    }
    function arrive(r, stage) {
      var failed = r.bad && (stage === 'gate' || stage === 'anomaly');
      if (!motionOff()) pulse(stage, failed ? 'fail' : 'hit');
      writeLog(r, stage, failed);
    }
    function finish(r) {
      if (r.bad) flagged++; else passed++;
      count.textContent = 'Passed ' + passed + ' · Flagged ' + flagged;
      detail.textContent = r.bad
        ? 'Record ' + r.id + ' failed the quality gate (' + r.check + ') and was held in Flagged anomalies. Nothing downstream received it.'
        : 'Record ' + r.id + ' passed the quality gate and reached Advertiser analytics.';
    }
    function place(dot, pt) { dot.setAttribute('cx', pt.x.toFixed(1)); dot.setAttribute('cy', pt.y.toFixed(1)); }

    function send(bad) {
      seq++;
      var r = {
        id: 'evt_' + (4800 + seq * 7 + Math.floor(Math.random() * 7)),
        bad: bad,
        check: bad ? CHECKS[Math.floor(Math.random() * CHECKS.length)] : null,
        source: Math.random() < 0.5 ? 'clickstream' : 'advertiser feeds'
      };
      var route = [r.source === 'clickstream' ? 'fromClick' : 'fromFeed', 'toTransform', 'toGate']
        .concat(bad ? ['toAnomaly'] : ['toLake', 'toApi', 'toAnalytics']);

      if (motionOff()) {
        route.forEach(function (k) { arrive(r, SEGMENTS[k][1]); });
        finish(r);
        return;
      }
      var dot = document.createElementNS(NS, 'circle');
      dot.setAttribute('r', '7');
      dot.setAttribute('class', 'rec');
      layer.appendChild(dot);
      place(dot, SEGMENTS[route[0]].path.getPointAtLength(0));

      var SPEED = 0.42;  // px per ms: the clean route takes about 4 s
      var si = 0, along = 0, last = null, hold = 0;
      (function frame(t) {
        // Cap each step so a backgrounded tab does not teleport the dot.
        var dt = last === null ? 16 : Math.min(48, t - last);
        last = t;
        if (hold > 0) { hold -= dt; requestAnimationFrame(frame); return; }
        var seg = SEGMENTS[route[si]];
        along += dt * SPEED;
        if (along < seg.len) { place(dot, seg.path.getPointAtLength(along)); requestAnimationFrame(frame); return; }
        place(dot, seg.path.getPointAtLength(seg.len));
        var stage = seg[1];
        arrive(r, stage);
        if (stage === 'gate') { hold = 420; if (bad) dot.classList.add('caught'); }
        si++; along = 0;
        if (si < route.length) { requestAnimationFrame(frame); return; }
        finish(r);
        dot.classList.add('done');
        setTimeout(function () { dot.remove(); }, 450);
      })(performance.now());
    }

    cleanBtn.addEventListener('click', function () { send(false); });
    badBtn.addEventListener('click', function () { send(true); });
  })();

  /* ---- First-view reveals (v5, Nov 2026) --------------------------------
     Two one-shot reveals that teach something about what they reveal:
     the 2026 trace renders its spans in date order, and the lineage
     graph draws itself in the order data flows through it. The hero
     intro is the third v5 animation and is pure CSS (style.css).

     Rules both follow:
       - Skipped when motion is off (OS setting or footer control) or
         IntersectionObserver is missing: the content is simply drawn.
       - Skipped when the element is already on screen when this code
         runs, so nothing visible vanishes and redraws. A deep link
         (#lineage) or scroll restoration moves the page only after this
         code runs, so those arrivals see the reveal play as they land,
         the same as scrolling there.
       - Armed (hidden) only by script, so with JavaScript off nothing is
         ever hidden.
       - Run once, then clean up after themselves. */
  function revealOnce(el, threshold, run) {
    if (!el || motionOff() || !('IntersectionObserver' in window)) return false;
    if (el.getBoundingClientRect().top < window.innerHeight * 0.92) return false;
    var io = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting) return;
      io.disconnect();
      requestAnimationFrame(run);
    }, { threshold: threshold });
    io.observe(el);
    return true;
  }

  // 2026 trace: bars render left to right, one after another, 110ms apart.
  (function () {
    var trace = document.querySelector('#trace .trace');
    if (!trace) return;
    var bars = trace.querySelectorAll('.trace-bar');
    var armed = revealOnce(trace, 0.35, function () {
      trace.classList.add('trace-drawn');
      // Leave the page as if it had never animated once the last bar lands.
      setTimeout(function () {
        trace.classList.remove('trace-armed', 'trace-drawn');
        bars.forEach(function (b) { b.style.removeProperty('--i'); });
      }, 900 + bars.length * 110 + 100);
    });
    if (!armed) return;
    bars.forEach(function (b, i) { b.style.setProperty('--i', i); });
    trace.classList.add('trace-armed');
  })();

  // Lineage graph: draws itself along the data flow. Each step is one hop
  // of the pipeline; edges in a step stroke in from their source end, and
  // each stage fades up as the edge reaching it arrives.
  (function () {
    var graph = document.getElementById('lineageSvg');
    if (!graph) return;
    // A stage appears when its incoming edge is 70% drawn; the next edge
    // leaves 44ms after that, so the drawing reads as data moving.
    var STEP = 380, STROKE = 480, ARRIVE = Math.round(STROKE * 0.7);
    var EDGE_STEPS = [
      ['e-feed-ingest', 'e-click-ingest'],
      ['e-ingest-transform'],
      ['e-transform-gate'],
      ['e-gate-lake', 'e-gate-anomaly'],
      ['e-lake-api'],
      ['e-api-analytics']
    ];
    var NODE_STEP = { feed: 0, click: 0, ingest: 1, transform: 2, gate: 3, lake: 4, anomaly: 4, api: 5, analytics: 6 };
    var edges = [], stageNodes = graph.querySelectorAll('.lnode');
    EDGE_STEPS.forEach(function (ids, step) {
      ids.forEach(function (id) {
        var p = document.getElementById(id);
        if (p) edges.push({ p: p, step: step, dashed: p.hasAttribute('stroke-dasharray') });
      });
    });
    function cleanUp() {
      graph.classList.remove('pre-draw');
      edges.forEach(function (e) { e.p.removeAttribute('style'); e.p.classList.remove('dashed-in'); });
      stageNodes.forEach(function (n) { n.removeAttribute('style'); });
    }
    var armed = revealOnce(graph, 0.4, function () {
      edges.forEach(function (e) {
        var delay = e.step * STEP;
        if (e.dashed) {
          e.p.style.transition = 'opacity 400ms ease ' + delay + 'ms';
          e.p.classList.remove('dashed-in');
        } else {
          e.p.style.transition = 'stroke-dashoffset ' + STROKE + 'ms cubic-bezier(.4,0,.2,1) ' + delay + 'ms';
          e.p.style.strokeDashoffset = '0';
        }
      });
      stageNodes.forEach(function (n) {
        // NODE_STEP k is reached by the edges of step k - 1.
        var k = NODE_STEP[n.getAttribute('data-node')] || 0;
        var delay = k === 0 ? 0 : (k - 1) * STEP + ARRIVE;
        n.style.transition = 'opacity 420ms ease ' + delay + 'ms, transform 420ms cubic-bezier(.2,.7,.2,1) ' + delay + 'ms';
      });
      graph.classList.remove('pre-draw');
      setTimeout(cleanUp, (EDGE_STEPS.length - 1) * STEP + ARRIVE + 420 + 300);
    });
    if (!armed) return;
    edges.forEach(function (e) {
      if (e.dashed) { e.p.classList.add('dashed-in'); return; }
      var len = Math.ceil(e.p.getTotalLength()) + 1;
      e.p.style.strokeDasharray = len + ' ' + len;
      e.p.style.strokeDashoffset = String(len);
    });
    graph.classList.add('pre-draw');
    // Turning motion off mid-draw finishes the drawing at once.
    new MutationObserver(function () { if (motionOff()) cleanUp(); })
      .observe(document.documentElement, { attributes: true, attributeFilter: ['data-motion'] });
  })();
})();
