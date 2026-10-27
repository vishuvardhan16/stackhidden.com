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
    // The manual reduce-motion control (v4) freezes the field in place.
    if (root.getAttribute('data-motion') === 'reduced') { draw(); return; }
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
    function restart() { if (timer) clearInterval(timer); if (!reduced && root.getAttribute('data-motion') !== 'reduced') timer = setInterval(step, 5000); }
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

  // Contact actions: copy email (clipboard API with a textarea fallback
  // for older browsers) and the print-resume button.
  function copyEmail() {
    var note = document.getElementById('copyNote');
    function done() { if (note) note.textContent = ' - email copied to clipboard'; }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText('vishuvardhan16@gmail.com').then(done, done);
    } else {
      var ta = document.createElement('textarea');
      ta.value = 'vishuvardhan16@gmail.com';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); } catch (e) {}
      document.body.removeChild(ta); done();
    }
  }
  var copyBtn = document.getElementById('copyEmail');
  if (copyBtn) copyBtn.addEventListener('click', copyEmail);
  var printBtn = document.getElementById('printBtn');
  if (printBtn) printBtn.addEventListener('click', function () { window.print(); });

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
    if (!off && !reduced) requestAnimationFrame(step);
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
    { label: 'Go to Contact', hint: 'section', run: function () { goTo('#contact'); } },
    { label: 'Copy email address', hint: 'action', run: copyEmail },
    { label: 'Print resume', hint: 'action', run: function () { window.print(); } },
    { label: 'Toggle light / dark theme', hint: 'action', run: function () { if (btn) btn.click(); } },
    { label: 'Reduce motion on / off', hint: 'action', run: function () { if (motionBtn) motionBtn.click(); } },
    { label: 'Open LinkedIn', hint: 'link', run: function () { window.open('https://www.linkedin.com/in/vishnu-vardhan-reddy-kaithapuram/', '_blank'); } },
    { label: 'Open GitHub source', hint: 'link', run: function () { window.open('https://github.com/vishuvardhan16/stackhidden.com', '_blank'); } }
  ];
  var pSel = 0, pItems = [];
  function markSel() {
    Array.prototype.forEach.call(pList.children, function (li, i) { li.classList.toggle('sel', i === pSel); });
  }
  function renderPalette() {
    var q = pInput.value.trim().toLowerCase();
    pItems = commands.filter(function (c) { return !q || c.label.toLowerCase().indexOf(q) !== -1; });
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
    if (t && t.closest && t.closest('a, button, input, li, .lnode, [role="button"]')) return;
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
})();
