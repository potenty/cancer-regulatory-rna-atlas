#!/usr/bin/env python3
"""Which papers can actually be read in full, for free?

Before spending hours on full-text review it is worth knowing which papers are
reachable. This queries NCBI for a PMCID per PMID and writes
quality_control/fulltext_access.csv, ordered so the highest-value reachable papers
come first.

"Priority" = how many interaction rows that paper currently carries at
Experimental functional. Reviewing one paper can therefore upgrade several rows.

Run this on a machine with network access:  python scripts/check_fulltext_access.py
"""
import csv, json, os, sys, time, urllib.parse, urllib.request
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "database")
OUT = os.path.join(ROOT, "quality_control", "fulltext_access.csv")
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def load(name):
    p = os.path.join(DB, name)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "CRRA-curation/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    inter = load("interactions.csv")
    pubs = {p["pmid"]: p for p in load("publications.csv")}

    # Rows that could be upgraded: provisional classes only.
    upgradable = Counter(
        r["supporting_pmid"] for r in inter
        if r.get("evidence_class") == "Experimental functional"
    )
    # Association rows are reviewable too, and a paper that would fix rows in both
    # tables is worth more per read than the interaction count alone suggests.
    assoc_rows = Counter(
        r["supporting_pmid"] for r in load("cancer_associations.csv")
        if r.get("evidence_class") == "Experimental functional"
    )
    if not upgradable:
        print("No Experimental functional rows to review.")
        return 0

    pmids = sorted(upgradable, key=lambda p: -upgradable[p])
    print(f"{len(pmids)} papers carry {sum(upgradable.values())} provisional rows.")

    # PubMed Central is not the only free route: many publishers release their own
    # back content. PubMed's "free full text" filter catches those too, so a paper
    # outside PMC is not assumed paywalled.
    free_elsewhere = set()
    for i in range(0, len(pmids), 20):
        chunk = pmids[i:i + 20]
        term = "(" + " OR ".join(p + "[pmid]" for p in chunk) + ") AND free full text[filter]"
        try:
            j = fetch(E + "esearch.fcgi?db=pubmed&retmode=json&retmax=50&term=" +
                      urllib.parse.quote(term))
            free_elsewhere.update(j.get("esearchresult", {}).get("idlist", []))
        except Exception as exc:
            print(f"  ! free-text filter failed for {chunk[0]}...: {exc}", file=sys.stderr)
        time.sleep(0.4)

    pmcid = {}
    for i in range(0, len(pmids), 20):
        chunk = pmids[i:i + 20]
        try:
            j = fetch(E + "esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(chunk))
            for pid in chunk:
                rec = j.get("result", {}).get(pid, {})
                ids = rec.get("articleids", [])
                pmc = next((a["value"] for a in ids if a.get("idtype") == "pmc"), "")
                pmcid[pid] = pmc
        except Exception as exc:                      # network hiccup, not fatal
            print(f"  ! lookup failed for {chunk[0]}...: {exc}", file=sys.stderr)
            for pid in chunk:
                pmcid.setdefault(pid, "")
        time.sleep(0.4)

    rows = []
    for pid in pmids:
        p = pubs.get(pid, {})
        pmc = pmcid.get(pid, "")
        rows.append({
            "supporting_pmid": pid,
            "provisional_rows": upgradable[pid] + assoc_rows.get(pid, 0),
            "interaction_rows": upgradable[pid],
            "association_rows": assoc_rows.get(pid, 0),
            "year": p.get("year", ""),
            "journal": p.get("journal", ""),
            "title": p.get("title", ""),
            "pmcid": pmc,
            "full_text_url": ("https://www.ncbi.nlm.nih.gov/pmc/articles/" + pmc + "/") if pmc
                             else "https://pubmed.ncbi.nlm.nih.gov/" + pid + "/",
            "free_full_text": ("yes (PMC)" if pmc
                               else "yes (publisher)" if pid in free_elsewhere
                               else "not free - check library access"),
            "reviewed": "",
        })

    rows.sort(key=lambda r: (not r["free_full_text"].startswith("yes"), -r["provisional_rows"]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, lineterminator="\n", fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    free = [r for r in rows if r["free_full_text"].startswith("yes")]
    print(f"\nfree full text : {len(free)} papers covering "
          f"{sum(r['provisional_rows'] for r in free)} provisional rows")
    print(f"not free       : {len(rows) - len(free)} papers covering "
          f"{sum(r['provisional_rows'] for r in rows if not r['free_full_text'].startswith('yes'))} rows")
    print(f"\nwrote {os.path.relpath(OUT, ROOT)} — work down it from the top.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
