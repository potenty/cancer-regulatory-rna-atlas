/* Cancer Regulatory RNA Atlas — RNA/target network.
   Self-contained force-directed layout in SVG; no external libraries, so the page
   works from the filesystem.

   Encodings
     node colour  : RNA class (validated categorical palette, fixed order)
     node shape   : circle = regulatory RNA, square = target  (identity is never colour-alone)
     node size    : degree, so hubs and convergent targets are visible
     edge weight  : evidence class, which is ordinal — stronger evidence draws heavier.
                    Colour is deliberately NOT used for evidence here: 88 of 94 rows share
                    one class, so a hue encoding would be a single flat colour.
*/
(function () {
  "use strict";

  var DATA = window.CRRA_DATA || {};
  var interactions = DATA.interactions || [];
  var rnas = DATA.rnas || [];

  /* Validated with the dataviz palette checker (light surface): lightness band,
     chroma floor, CVD separation, normal-vision floor and contrast all pass.
     Fixed order — never cycled, never reassigned when a filter changes the set. */
  var CLASS_COLOR = {
    "miRNA": "#1f6fd0",
    "lncRNA": "#d4761a",
    "eRNA": "#0d8a6a",
    "circRNA": "#c0392b",
    "pseudogene transcript": "#8b3fc9",
    "snoRNA host gene": "#7f8c1f"
  };
  var TARGET_COLOR = "#8b97a6";

  var EV_WEIGHT = {
    "Direct experimental": 2.6,
    "Experimental functional": 1.4,
    "Computational prediction": 1.0,
    "Literature association": 1.0
  };
  var EV_DASH = {
    "Computational prediction": "3,3",
    "Literature association": "1,4"
  };

  var catOf = {};
  rnas.forEach(function (r) { catOf[r.official_name] = r.rna_category || ""; });

  var svg, sim = null, nodes = [], links = [], hover = null, pinned = null;
  var W = 900, H = 560;

  function el(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // ---------- graph construction ----------

  function build(filters) {
    var rows = interactions.filter(function (r) {
      if (filters.ev && (r.evidence_class || "").trim() !== filters.ev) return false;
      if (filters.cancer && (r.cancer_type || "").trim() !== filters.cancer) return false;
      if (filters.cls && catOf[(r.rna_name || "").trim()] !== filters.cls) return false;
      return true;
    });

    var byId = {};
    function node(name, isRna) {
      var id = (isRna ? "r:" : "t:") + name;
      if (!byId[id]) {
        byId[id] = {
          id: id, name: name, isRna: isRna,
          cls: isRna ? (catOf[name] || "") : "",
          deg: 0,
          x: W / 2, y: H / 2,
          vx: 0, vy: 0
        };
      }
      return byId[id];
    }

    links = rows.map(function (r) {
      var a = node((r.rna_name || "").trim(), true);
      var b = node((r.target_name || "").trim(), false);
      a.deg++; b.deg++;
      return { source: a, target: b, row: r };
    });
    nodes = Object.keys(byId).map(function (k) { return byId[k]; });
    // Deterministic ring seed: reproducible layouts, and no two nodes coincident.
    nodes.forEach(function (n, i) {
      var a = (i / nodes.length) * Math.PI * 2;
      var rad = 150 + (i % 5) * 26;
      n.x = W / 2 + Math.cos(a) * rad;
      n.y = H / 2 + Math.sin(a) * rad * 0.72;
    });

    // Adjacency, for neighbourhood highlighting on hover.
    nodes.forEach(function (n) { n.adj = {}; });
    links.forEach(function (l) {
      l.source.adj[l.target.id] = true;
      l.target.adj[l.source.id] = true;
    });
    return rows.length;
  }

  // ---------- force layout ----------

  function step() {
    var i, j, a, b, dx, dy, d2, d, f;

    // Repulsion, O(n^2) — fine at this scale (under ~150 nodes).
    for (i = 0; i < nodes.length; i++) {
      a = nodes[i];
      for (j = i + 1; j < nodes.length; j++) {
        b = nodes[j];
        dx = b.x - a.x; dy = b.y - a.y;
        d2 = dx * dx + dy * dy;
        if (d2 > 90000) continue;
        // Floor the distance: without it, two nodes that start near each other
        // produce an enormous force and the whole layout is flung to the bounds.
        if (d2 < 100) {
          d2 = 100;
          if (dx === 0 && dy === 0) { dx = (Math.random() - 0.5); dy = (Math.random() - 0.5); }
        }
        d = Math.sqrt(dx * dx + dy * dy) || 1;
        f = 1700 / d2;
        dx /= d; dy /= d;
        a.vx -= dx * f; a.vy -= dy * f;
        b.vx += dx * f; b.vy += dy * f;
      }
    }

    // Springs.
    links.forEach(function (l) {
      dx = l.target.x - l.source.x; dy = l.target.y - l.source.y;
      d = Math.sqrt(dx * dx + dy * dy) || 0.01;
      f = (d - 70) * 0.012;
      dx /= d; dy /= d;
      l.source.vx += dx * f; l.source.vy += dy * f;
      l.target.vx -= dx * f; l.target.vy -= dy * f;
    });

    // Gentle centring + damping + bounds.
    nodes.forEach(function (n) {
      n.vx += (W / 2 - n.x) * 0.0032;
      n.vy += (H / 2 - n.y) * 0.0032;
      n.vx *= 0.82; n.vy *= 0.82;
      // Cap speed so no single step can throw a node across the canvas.
      var sp = Math.sqrt(n.vx * n.vx + n.vy * n.vy);
      if (sp > 12) { n.vx = n.vx / sp * 12; n.vy = n.vy / sp * 12; }
      n.x += n.vx; n.y += n.vy;
      var m = 26;
      n.x = Math.max(m, Math.min(W - m, n.x));
      n.y = Math.max(m, Math.min(H - m, n.y));
    });
  }

  function radius(n) { return n.isRna ? 5 + Math.min(n.deg, 10) * 1.1 : 4 + Math.min(n.deg, 10) * 0.9; }

  // ---------- rendering ----------

  function render() {
    if (!svg) return;
    var active = pinned || hover;
    var parts = [];

    links.forEach(function (l) {
      var ec = (l.row.evidence_class || "").trim();
      var on = !active || l.source.id === active.id || l.target.id === active.id;
      parts.push('<line x1="' + l.source.x.toFixed(1) + '" y1="' + l.source.y.toFixed(1) +
        '" x2="' + l.target.x.toFixed(1) + '" y2="' + l.target.y.toFixed(1) +
        '" stroke="#9aa6b4" stroke-width="' + (EV_WEIGHT[ec] || 1.2) +
        '" stroke-opacity="' + (on ? (active ? 0.85 : 0.42) : 0.07) + '"' +
        (EV_DASH[ec] ? ' stroke-dasharray="' + EV_DASH[ec] + '"' : "") + "/>");
    });

    nodes.forEach(function (n) {
      var on = !active || n.id === active.id || active.adj[n.id];
      var op = on ? 1 : 0.12;
      var fill = n.isRna ? (CLASS_COLOR[n.cls] || "#5a6878") : TARGET_COLOR;
      var r = radius(n);
      if (n.isRna) {
        parts.push('<circle data-id="' + esc(n.id) + '" cx="' + n.x.toFixed(1) + '" cy="' +
          n.y.toFixed(1) + '" r="' + r.toFixed(1) + '" fill="' + fill +
          '" fill-opacity="' + op + '" stroke="#fff" stroke-width="1.5"/>');
      } else {
        parts.push('<rect data-id="' + esc(n.id) + '" x="' + (n.x - r).toFixed(1) + '" y="' +
          (n.y - r).toFixed(1) + '" width="' + (r * 2).toFixed(1) + '" height="' +
          (r * 2).toFixed(1) + '" fill="' + fill + '" fill-opacity="' + op +
          '" stroke="#fff" stroke-width="1.5"/>');
      }
      // Label hubs always; everything else only when its neighbourhood is active.
      if (n.deg >= 3 || (active && on)) {
        parts.push('<text x="' + n.x.toFixed(1) + '" y="' + (n.y - r - 4).toFixed(1) +
          '" text-anchor="middle" font-size="10" fill="#1c2530" fill-opacity="' +
          (on ? 0.95 : 0.1) + '" paint-order="stroke" stroke="#fff" stroke-width="3">' +
          esc(n.name) + "</text>");
      }
    });

    svg.innerHTML = parts.join("");
  }

  // ---------- detail panel ----------

  function describe(n) {
    if (!n) {
      return '<p class="net-hint">Hover a node to trace its connections. Click to pin.</p>';
    }
    var rows = links.filter(function (l) { return l.source.id === n.id || l.target.id === n.id; });
    var head = '<h4>' + esc(n.name) + "</h4><p class=\"net-sub\">" +
      (n.isRna ? esc(n.cls || "regulatory RNA") : "target") + " &middot; " +
      rows.length + (rows.length === 1 ? " interaction" : " interactions") + "</p>";
    var list = rows.slice(0, 14).map(function (l) {
      var other = l.source.id === n.id ? l.target : l.source;
      var ec = (l.row.evidence_class || "").trim();
      var slug = ec === "Direct experimental" ? "direct"
        : ec === "Experimental functional" ? "functional"
        : ec === "Computational prediction" ? "computational"
        : ec === "Literature association" ? "literature" : "unknown";
      return "<li><strong>" + esc(other.name) + "</strong> " +
        '<span class="ev ev-' + slug + '">' + esc(ec || "unclassified") + "</span><br>" +
        '<span class="net-meta">' + esc(l.row.cancer_type || "") +
        (l.row.supporting_pmid
          ? ' &middot; <a href="https://pubmed.ncbi.nlm.nih.gov/' +
            encodeURIComponent(l.row.supporting_pmid) + '/" target="_blank" rel="noopener">PMID ' +
            esc(l.row.supporting_pmid) + "</a>"
          : "") + "</span></li>";
    }).join("");
    var more = rows.length > 14 ? "<p class=\"net-meta\">and " + (rows.length - 14) + " more</p>" : "";
    return head + '<ul class="net-list">' + list + "</ul>" + more;
  }

  // ---------- wiring ----------

  function run(filters) {
    var n = build(filters);
    hover = pinned = null;
    el("net-detail").innerHTML = describe(null);

    var counts = {};
    nodes.forEach(function (x) {
      if (x.isRna) counts[x.cls || "unclassified"] = (counts[x.cls || "unclassified"] || 0) + 1;
    });
    el("net-count").innerHTML = n
      ? "<strong>" + n + "</strong> interactions &middot; " +
        nodes.filter(function (x) { return x.isRna; }).length + " RNAs &middot; " +
        nodes.filter(function (x) { return !x.isRna; }).length + " targets"
      : "No interactions match these filters.";

    if (sim) { clearInterval(sim); sim = null; }
    if (!n) { svg.innerHTML = ""; return; }

    var ticks = 0;
    sim = setInterval(function () {
      for (var k = 0; k < 2; k++) step();
      render();
      if (++ticks > 240) { clearInterval(sim); sim = null; }
    }, 16);
  }

  function filters() {
    return {
      ev: el("net-ev").value,
      cancer: el("net-cancer").value,
      cls: el("net-class").value
    };
  }

  function uniq(list, fn) {
    var seen = {};
    list.forEach(function (r) { var v = fn(r); if (v) seen[v] = true; });
    return Object.keys(seen).sort(function (a, b) { return a.localeCompare(b); });
  }

  function fill(sel, vals) {
    vals.forEach(function (v) {
      var o = document.createElement("option");
      o.value = v; o.textContent = v;
      sel.appendChild(o);
    });
  }

  window.CRRA_initNetwork = function () {
    svg = el("net-svg");
    if (!svg) return;

    if (!interactions.length) {
      el("net-count").textContent = "";
      el("net-detail").innerHTML = "";
      svg.outerHTML = '<div class="empty-state"><strong>No interactions yet</strong>' +
        "The network draws from database/interactions.csv.</div>";
      return;
    }

    fill(el("net-ev"), ["Direct experimental", "Experimental functional",
                        "Computational prediction", "Literature association"]
      .filter(function (c) {
        return interactions.some(function (r) { return (r.evidence_class || "").trim() === c; });
      }));
    fill(el("net-cancer"), uniq(interactions, function (r) { return (r.cancer_type || "").trim(); }));
    fill(el("net-class"), uniq(interactions, function (r) { return catOf[(r.rna_name || "").trim()]; }));

    // Legend — always present, so identity never rests on colour alone.
    var used = {};
    interactions.forEach(function (r) {
      var c = catOf[(r.rna_name || "").trim()];
      if (c) used[c] = true;
    });
    el("net-legend").innerHTML =
      Object.keys(used).sort().map(function (c) {
        return '<span class="net-key"><svg width="12" height="12" aria-hidden="true">' +
          '<circle cx="6" cy="6" r="5" fill="' + (CLASS_COLOR[c] || "#5a6878") +
          '" stroke="#fff" stroke-width="1.2"/></svg>' + esc(c) + "</span>";
      }).join("") +
      '<span class="net-key"><svg width="12" height="12" aria-hidden="true">' +
      '<rect x="1" y="1" width="10" height="10" fill="' + TARGET_COLOR +
      '" stroke="#fff" stroke-width="1.2"/></svg>target gene</span>' +
      '<span class="net-key net-key-wide">Line weight shows evidence strength; ' +
      'dashed lines are prediction or literature association.</span>';

    ["net-ev", "net-cancer", "net-class"].forEach(function (id) {
      el(id).addEventListener("change", function () { run(filters()); });
    });
    el("net-reset").addEventListener("click", function () {
      ["net-ev", "net-cancer", "net-class"].forEach(function (id) { el(id).selectedIndex = 0; });
      run(filters());
    });

    function nodeAt(ev) {
      var t = ev.target, id = t && t.getAttribute && t.getAttribute("data-id");
      if (!id) return null;
      for (var i = 0; i < nodes.length; i++) if (nodes[i].id === id) return nodes[i];
      return null;
    }
    svg.addEventListener("mousemove", function (ev) {
      if (pinned) return;
      var n = nodeAt(ev);
      if (n !== hover) { hover = n; el("net-detail").innerHTML = describe(n); render(); }
    });
    svg.addEventListener("mouseleave", function () {
      if (pinned) return;
      if (hover) { hover = null; el("net-detail").innerHTML = describe(null); render(); }
    });
    svg.addEventListener("click", function (ev) {
      var n = nodeAt(ev);
      pinned = (pinned && n && pinned.id === n.id) ? null : n;
      hover = pinned;
      el("net-detail").innerHTML = describe(pinned);
      render();
    });

    run(filters());
  };
})();
