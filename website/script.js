/* Cancer Regulatory RNA Atlas — client-side search and filtering.
   Data is embedded by scripts/build.py into data/data.js, so the site runs from
   the filesystem with no server. */

(function () {
  "use strict";

  var DATA = window.CRRA_DATA || {};
  var rnas = DATA.rnas || [];
  var interactions = DATA.interactions || [];
  var associations = DATA.associations || [];
  var publications = DATA.publications || [];

  var EV_CLASSES = [
    "Direct experimental",
    "Experimental functional",
    "Computational prediction",
    "Literature association"
  ];

  var EV_SLUG = {
    "Direct experimental": "direct",
    "Experimental functional": "functional",
    "Computational prediction": "computational",
    "Literature association": "literature"
  };

  // ---------- helpers ----------

  function el(id) { return document.getElementById(id); }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /* An empty field means "not recorded" — shown as an em dash, never as a zero
     or a negative finding. */
  function cell(v) {
    var s = (v == null ? "" : String(v)).trim();
    return s ? esc(s) : '<span class="empty-cell" title="Not recorded">&mdash;</span>';
  }

  function badge(cls) {
    var s = (cls || "").trim();
    if (!s) return '<span class="ev ev-unknown" title="No evidence class recorded">Unclassified</span>';
    var slug = EV_SLUG[s] || "unknown";
    return '<span class="ev ev-' + slug + '">' + esc(s) + "</span>";
  }

  function haystack(row, fields) {
    var out = [];
    for (var i = 0; i < fields.length; i++) {
      var v = row[fields[i]];
      if (v) out.push(String(v));
    }
    return out.join(" \u0001 ").toLowerCase();
  }

  /* Every term must appear somewhere in the row (AND), so adding words narrows. */
  function matches(hay, query) {
    var terms = query.toLowerCase().split(/\s+/).filter(Boolean);
    for (var i = 0; i < terms.length; i++) {
      if (hay.indexOf(terms[i]) === -1) return false;
    }
    return true;
  }


  /* cancer_group is a normalised term derived from cancer_type, and one row can carry
     several (a paper reporting two cancers). Filters match any of them; tables still
     display the source's own wording. */
  function groupsOf(row) {
    return ((row.cancer_group || row.cancer_type || "").split(";"))
      .map(function (s) { return s.trim(); })
      .filter(Boolean);
  }

  function inGroup(row, g) {
    return groupsOf(row).indexOf(g) !== -1;
  }

  function uniqueGroups(rows) {
    var seen = Object.create(null);
    rows.forEach(function (r) { groupsOf(r).forEach(function (g) { seen[g] = true; }); });
    return Object.keys(seen).sort(function (a, b) {
      if (a === "Not specified") return 1;
      if (b === "Not specified") return -1;
      return a.localeCompare(b);
    });
  }

  function uniqueSorted(rows, field) {
    var seen = Object.create(null);
    rows.forEach(function (r) {
      var v = (r[field] || "").trim();
      if (v) seen[v] = true;
    });
    return Object.keys(seen).sort(function (a, b) { return a.localeCompare(b); });
  }

  function fillSelect(select, values, keepFirst) {
    if (!select) return;
    var first = keepFirst ? select.options[0] : null;
    select.innerHTML = "";
    if (first) select.appendChild(first);
    values.forEach(function (v) {
      var o = document.createElement("option");
      o.value = v;
      o.textContent = v;
      select.appendChild(o);
    });
  }

  function countText(shown, total, noun) {
    if (total === 0) return "No " + noun + " in the database yet.";
    if (shown === total) return "<strong>" + total + "</strong> " + noun;
    return "<strong>" + shown + "</strong> of " + total + " " + noun + " match";
  }

  function emptyState(title, body) {
    return '<div class="empty-state"><strong>' + esc(title) + "</strong>" + esc(body) + "</div>";
  }

  function table(headers, bodyHtml) {
    return '<div class="table-wrap"><table><thead><tr>' +
      headers.map(function (h) { return "<th>" + esc(h) + "</th>"; }).join("") +
      "</tr></thead><tbody>" + bodyHtml + "</tbody></table></div>";
  }

  function pubmedLink(pmid) {
    var p = (pmid || "").trim();
    if (!p) return cell("");
    return '<a href="https://pubmed.ncbi.nlm.nih.gov/' + encodeURIComponent(p) +
      '/" target="_blank" rel="noopener">' + esc(p) + "</a>";
  }

  // ---------- tabs ----------

  var tabs = Array.prototype.slice.call(document.querySelectorAll('nav.tabs button[role="tab"]'));

  function show(name) {
    tabs.forEach(function (t) {
      var on = t.getAttribute("data-panel") === name;
      t.setAttribute("aria-selected", on ? "true" : "false");
      var panel = el("panel-" + t.getAttribute("data-panel"));
      if (panel) panel.hidden = !on;
    });
    if (window.location.hash.slice(1) !== name) {
      history.replaceState(null, "", "#" + name);
    }
    window.scrollTo({ top: 0, behavior: "auto" });
    // The network lays out on first view, not on load, so an unseen tab costs nothing.
    if (name === "network" && !show._net && window.CRRA_initNetwork) {
      show._net = true;
      window.CRRA_initNetwork();
    }
  }

  tabs.forEach(function (t) {
    t.addEventListener("click", function () { show(t.getAttribute("data-panel")); });
  });

  // In-page links that jump to another tab.
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest && ev.target.closest("[data-goto]");
    if (!a) return;
    ev.preventDefault();
    show(a.getAttribute("data-goto"));
  });

  // ---------- home ----------

  function renderHome() {
    /* Rows are not findings: a family result yields one row per member, so the
       count of distinct source publications is shown alongside the row count. */
    var intPubs = {};
    interactions.forEach(function (r) {
      var p = (r.supporting_pmid || "").trim();
      if (p) intPubs[p] = true;
    });
    var nIntPubs = Object.keys(intPubs).length;

    var stats = [
      [rnas.length, "RNA records"],
      [interactions.length, "Interactions"],
      [nIntPubs, "from publications"],
      [associations.length, "Cancer associations"],
      [publications.length, "Publications"]
    ];
    el("home-stats").innerHTML = stats.map(function (s) {
      return '<div class="stat"><span class="n">' + s[0] + '</span><span class="label">' +
        esc(s[1]) + "</span></div>";
    }).join("");

    var counts = Object.create(null);
    rnas.forEach(function (r) {
      var c = (r.rna_category || "unclassified").trim();
      counts[c] = (counts[c] || 0) + 1;
    });
    var keys = Object.keys(counts).sort(function (a, b) { return counts[b] - counts[a]; });
    el("home-categories").innerHTML = keys.length
      ? keys.map(function (k) {
          return '<div class="stat"><span class="n">' + counts[k] + '</span><span class="label">' +
            esc(k) + "</span></div>";
        }).join("")
      : emptyState("No RNA records yet", "Run scripts/build.py once the tables are populated.");

    var gen = [];
    var cancers = {};
    interactions.concat(associations).forEach(function (r) {
      groupsOf(r).forEach(function (g) {
        if (g && g !== "Not specified") cancers[g] = true;
      });
    });
    var nCancer = Object.keys(cancers).length;
    if (nCancer) gen.push(nCancer + " named cancer types");
    var years = publications.map(function (p) { return parseInt(p.year, 10); })
      .filter(function (y) { return !isNaN(y); });
    if (years.length) {
      gen.push("literature spanning " + Math.min.apply(null, years) + "–" + Math.max.apply(null, years));
    }
    if (interactions.length && nIntPubs) {
      gen.unshift(interactions.length + " interaction rows drawn from " + nIntPubs +
                  " publications");
    }
    el("home-generated").innerHTML = gen.length ? esc(gen.join(" · ")) : "";
  }

  // ---------- RNA explorer ----------

  var RNA_SEARCH = ["official_name", "alternative_names", "stable_identifier",
                    "rna_category", "notes", "source_database"];

  function renderRnas() {
    var q = el("rna-q").value.trim();
    var cat = el("rna-cat").value;
    var idState = el("rna-id-state").value;
    var sort = el("rna-sort").value;

    var rows = rnas.filter(function (r) {
      if (cat && (r.rna_category || "").trim() !== cat) return false;
      var hasId = !!(r.stable_identifier || "").trim();
      if (idState === "has" && !hasId) return false;
      if (idState === "none" && hasId) return false;
      if (q && !matches(haystack(r, RNA_SEARCH), q)) return false;
      return true;
    });

    rows.sort(function (a, b) {
      if (sort === "category") {
        var c = (a.rna_category || "").localeCompare(b.rna_category || "");
        if (c) return c;
      }
      return (a.official_name || "").localeCompare(b.official_name || "");
    });

    el("rna-count").innerHTML = countText(rows.length, rnas.length, "RNA records");

    if (!rnas.length) {
      el("rna-results").innerHTML = emptyState("No RNA records yet",
        "Populate database/rna_records.csv and run scripts/build.py.");
      return;
    }
    if (!rows.length) {
      el("rna-results").innerHTML = emptyState("No matches",
        "No RNA record matches these filters. Try clearing the search box or widening the class filter.");
      return;
    }

    var body = rows.map(function (r) {
      var idCell = (r.stable_identifier || "").trim();
      var link = (r.source_url || "").trim();
      var idHtml;
      if (!idCell) {
        idHtml = '<span class="empty-cell" title="No identifier available in any nomenclature database">&mdash;</span>';
      } else if (link) {
        idHtml = '<a href="' + esc(link) + '" target="_blank" rel="noopener">' + esc(idCell) + "</a>";
      } else {
        idHtml = esc(idCell);
      }
      return "<tr>" +
        '<td class="name">' + cell(r.official_name) + "</td>" +
        '<td><span class="cat">' + esc((r.rna_category || "unclassified")) + "</span></td>" +
        "<td>" + cell(r.alternative_names) + "</td>" +
        '<td class="num">' + idHtml + "</td>" +
        "<td>" + cell(r.organism) + "</td>" +
        '<td class="note">' + cell(r.notes) + "</td>" +
        "</tr>";
    }).join("");

    el("rna-results").innerHTML = table(
      ["Name", "Class", "Aliases", "Identifier", "Organism", "Notes"], body);
  }

  // ---------- interaction explorer ----------

  var INT_SEARCH = ["rna_name", "target_name", "target_gene_id", "cancer_type",
                    "interaction_type", "regulatory_effect", "evidence_class",
                    "experimental_method", "supporting_pmid", "notes"];

  function renderInteractions() {
    var q = el("int-q").value.trim();
    var ev = el("int-ev").value;
    var cancer = el("int-cancer").value;
    var type = el("int-type").value;

    var rows = interactions.filter(function (r) {
      if (ev && (r.evidence_class || "").trim() !== ev) return false;
      if (cancer && !inGroup(r, cancer)) return false;
      if (type && (r.interaction_type || "").trim() !== type) return false;
      if (q && !matches(haystack(r, INT_SEARCH), q)) return false;
      return true;
    });

    /* Strongest evidence first, so the best supported records lead. */
    rows.sort(function (a, b) {
      var ia = EV_CLASSES.indexOf((a.evidence_class || "").trim());
      var ib = EV_CLASSES.indexOf((b.evidence_class || "").trim());
      if (ia === -1) ia = 99;
      if (ib === -1) ib = 99;
      if (ia !== ib) return ia - ib;
      return (a.rna_name || "").localeCompare(b.rna_name || "");
    });

    el("int-count").innerHTML = countText(rows.length, interactions.length, "interactions");

    if (!interactions.length) {
      el("int-results").innerHTML = emptyState("No interaction records yet",
        "The interaction table is in place but not yet populated. Curation is tracked in PROJECT_STATUS.md.");
      return;
    }
    if (!rows.length) {
      el("int-results").innerHTML = emptyState("No matches",
        "No interaction matches these filters.");
      return;
    }

    var body = rows.map(function (r) {
      var target = (r.target_name || "").trim();
      var gid = (r.target_gene_id || "").trim();
      var targetHtml = esc(target || "—");
      if (gid.indexOf("NCBIGene:") === 0) {
        targetHtml = '<a href="https://www.ncbi.nlm.nih.gov/gene/' +
          encodeURIComponent(gid.split(":")[1]) + '" target="_blank" rel="noopener">' +
          esc(target) + "</a>";
      }
      return "<tr>" +
        '<td class="name">' + cell(r.rna_name) + "</td>" +
        '<td class="name">' + targetHtml + "</td>" +
        "<td>" + cell(r.cancer_type) + "</td>" +
        "<td>" + cell(r.interaction_type) + "</td>" +
        "<td>" + cell(r.regulatory_effect) + "</td>" +
        "<td>" + badge(r.evidence_class) + "</td>" +
        '<td class="note">' + cell(r.experimental_method) + "</td>" +
        '<td class="num">' + pubmedLink(r.supporting_pmid) + "</td>" +
        '<td class="note">' + cell(r.notes) + "</td>" +
        "</tr>";
    }).join("");

    el("int-results").innerHTML = table(
      ["RNA", "Target", "Cancer type", "Interaction", "Effect", "Evidence",
       "Method", "PMID", "Notes"], body);
  }

  function renderAssociations() {
    el("assoc-count").innerHTML = countText(associations.length, associations.length,
      "cancer associations");

    if (!associations.length) {
      el("assoc-results").innerHTML = emptyState("No cancer association records yet",
        "The table is in place but not yet populated.");
      return;
    }

    var rows = associations.slice().sort(function (a, b) {
      return (a.rna_name || "").localeCompare(b.rna_name || "");
    });

    var body = rows.map(function (r) {
      return "<tr>" +
        '<td class="name">' + cell(r.rna_name) + "</td>" +
        "<td>" + cell(r.cancer_type) + "</td>" +
        "<td>" + cell(r.direction) + "</td>" +
        "<td>" + cell(r.clinical_association) + "</td>" +
        "<td>" + badge(r.evidence_class) + "</td>" +
        '<td class="note">' + cell(r.cohort_description) + "</td>" +
        '<td class="num">' + pubmedLink(r.supporting_pmid) + "</td>" +
        "</tr>";
    }).join("");

    el("assoc-results").innerHTML = table(
      ["RNA", "Cancer type", "Direction", "Clinical association", "Evidence",
       "Cohort", "PMID"], body);
  }

  // ---------- publications ----------

  var PUB_SEARCH = ["title", "authors", "journal", "year", "pmid", "doi",
                    "cancer_types", "rna_categories", "main_finding"];

  function renderPublications() {
    var q = el("pub-q").value.trim();
    var sort = el("pub-sort").value;
    var minY = parseInt(el("pub-year-min").value, 10);
    var maxY = parseInt(el("pub-year-max").value, 10);

    var rows = publications.filter(function (r) {
      var y = parseInt(r.year, 10);
      if (!isNaN(minY) && !isNaN(y) && y < minY) return false;
      if (!isNaN(maxY) && !isNaN(y) && y > maxY) return false;
      if (q && !matches(haystack(r, PUB_SEARCH), q)) return false;
      return true;
    });

    rows.sort(function (a, b) {
      var ya = parseInt(a.year, 10) || 0;
      var yb = parseInt(b.year, 10) || 0;
      if (sort === "year-asc") return ya - yb || (a.journal || "").localeCompare(b.journal || "");
      if (sort === "journal") {
        var c = (a.journal || "").localeCompare(b.journal || "");
        if (c) return c;
        return yb - ya;
      }
      return yb - ya || (a.journal || "").localeCompare(b.journal || "");
    });

    el("pub-count").innerHTML = countText(rows.length, publications.length, "publications");

    if (!publications.length) {
      el("pub-results").innerHTML = emptyState("No publications yet",
        "Populate database/publications.csv and run scripts/build.py.");
      return;
    }
    if (!rows.length) {
      el("pub-results").innerHTML = emptyState("No matches",
        "No publication matches these filters.");
      return;
    }

    var body = rows.map(function (r) {
      var url = (r.publication_url || "").trim();
      var title = esc(r.title || "(untitled)");
      var titleHtml = url
        ? '<a href="' + esc(url) + '" target="_blank" rel="noopener">' + title + "</a>"
        : title;
      var doi = (r.doi || "").trim();
      var doiHtml = doi
        ? '<a href="https://doi.org/' + esc(doi) + '" target="_blank" rel="noopener">' + esc(doi) + "</a>"
        : cell("");
      var flags = (r.pubmed_flags || "").trim();
      return "<tr>" +
        '<td class="title">' + titleHtml +
          (flags ? '<br><span class="cat">' + esc(flags) + "</span>" : "") + "</td>" +
        '<td class="note">' + cell(r.authors) + "</td>" +
        "<td>" + cell(r.journal) + "</td>" +
        '<td class="num">' + cell(r.year) + "</td>" +
        '<td class="num">' + pubmedLink(r.pmid) + "</td>" +
        '<td class="note">' + doiHtml + "</td>" +
        '<td class="note">' + cell(r.main_finding) + "</td>" +
        "</tr>";
    }).join("");

    el("pub-results").innerHTML = table(
      ["Title", "Authors", "Journal", "Year", "PMID", "DOI", "Main finding"], body);
  }

  // ---------- wiring ----------

  function debounce(fn, ms) {
    var t;
    return function () {
      clearTimeout(t);
      t = setTimeout(fn, ms);
    };
  }

  function bind(ids, handler) {
    ids.forEach(function (id) {
      var node = el(id);
      if (!node) return;
      var ev = (node.tagName === "SELECT") ? "change" : "input";
      node.addEventListener(ev, ev === "input" ? debounce(handler, 120) : handler);
    });
  }

  function init() {
    // Filter vocabularies come from the data, so they can never offer a value
    // that matches nothing.
    fillSelect(el("rna-cat"), uniqueSorted(rnas, "rna_category"), true);
    fillSelect(el("int-ev"), EV_CLASSES.filter(function (c) {
      return interactions.some(function (r) { return (r.evidence_class || "").trim() === c; });
    }), true);
    fillSelect(el("int-cancer"), uniqueGroups(interactions), true);
    fillSelect(el("int-type"), uniqueSorted(interactions, "interaction_type"), true);

    bind(["rna-q", "rna-cat", "rna-id-state", "rna-sort"], renderRnas);
    bind(["int-q", "int-ev", "int-cancer", "int-type"], renderInteractions);
    bind(["pub-q", "pub-year-min", "pub-year-max", "pub-sort"], renderPublications);

    Array.prototype.forEach.call(document.querySelectorAll("button.reset"), function (b) {
      b.addEventListener("click", function () {
        var panel = el("panel-" + b.getAttribute("data-reset"));
        if (!panel) return;
        Array.prototype.forEach.call(panel.querySelectorAll("input"), function (i) { i.value = ""; });
        Array.prototype.forEach.call(panel.querySelectorAll("select"), function (s) { s.selectedIndex = 0; });
        renderRnas();
        renderInteractions();
        renderPublications();
      });
    });

    renderHome();
    renderRnas();
    renderInteractions();
    renderAssociations();
    renderPublications();

    var hash = window.location.hash.slice(1);
    var known = tabs.map(function (t) { return t.getAttribute("data-panel"); });
    show(known.indexOf(hash) !== -1 ? hash : "home");
  }

  if (!window.CRRA_DATA) {
    document.addEventListener("DOMContentLoaded", function () {
      var m = document.querySelector("main");
      if (m) {
        m.insertAdjacentHTML("afterbegin",
          '<div class="notice caution"><p><strong>Data file not loaded.</strong> ' +
          "Expected <code>data/data.js</code>. Run <code>python3 scripts/build.py</code> " +
          "to generate it from the CSV tables.</p></div>");
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
