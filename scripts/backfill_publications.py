#!/usr/bin/env python3
"""Backfill derivable columns in database/publications.csv.

cancer_types and rna_categories are DERIVED from the interaction and association
tables: a publication's cancer types are the ones its own rows record, and its RNA
categories are the classes of the RNAs in those rows. Nothing is inferred from the
paper itself, so this adds no new claim - it only surfaces what the curated rows
already say.

main_finding is NOT derivable and is left untouched; it is a curator's paraphrase.

pubmed_flags come from the publication-type screening recorded in
quality_control/verification_report.md.
"""
import csv, os, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "database")

# Errata / published comments found during PubMed publication-type screening.
# Retracted papers were excluded entirely and never reached publications.csv.
FLAGS = {
    "17898713": "Erratum (Nature 2008); published comment with author reply (Nature 2008;455:E8-9)",
    "16166262": "Erratum (PNAS 2006)",
    "18381893": "Erratum (Genes Dev 2009)",
    "21862635": "Erratum (Cancer Res 2012)",
    "24662484": "Erratum (Cell Res 2014)",
}


def load(name):
    path = os.path.join(DB, name)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main():
    pubs = load("publications.csv")
    if not pubs:
        print("publications.csv missing or empty", file=sys.stderr)
        return 1

    rnas = {r["official_name"]: r.get("rna_category", "") for r in load("rna_records.csv")}

    cancers = defaultdict(set)
    cats = defaultdict(set)
    for table in ("interactions.csv", "cancer_associations.csv"):
        for row in load(table):
            pmid = (row.get("supporting_pmid") or "").strip()
            if not pmid:
                continue
            ct = (row.get("cancer_type") or "").strip()
            # Semicolons separate multiple types within one cell.
            for part in [c.strip() for c in ct.split(";") if c.strip()]:
                if "not specified" not in part.lower():
                    cancers[pmid].add(part)
            cat = rnas.get((row.get("rna_name") or "").strip(), "")
            if cat:
                cats[pmid].add(cat)

    filled_c = filled_r = filled_f = 0
    for p in pubs:
        pmid = p["pmid"]
        if not p.get("cancer_types") and cancers.get(pmid):
            p["cancer_types"] = "; ".join(sorted(cancers[pmid]))
            filled_c += 1
        if not p.get("rna_categories") and cats.get(pmid):
            p["rna_categories"] = "; ".join(sorted(cats[pmid]))
            filled_r += 1
        if not p.get("pubmed_flags") and pmid in FLAGS:
            p["pubmed_flags"] = FLAGS[pmid]
            filled_f += 1

    with open(os.path.join(DB, "publications.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pubs[0].keys()))
        w.writeheader()
        w.writerows(pubs)

    print(f"cancer_types filled: {filled_c}")
    print(f"rna_categories filled: {filled_r}")
    print(f"pubmed_flags filled: {filled_f}")
    remaining = sum(1 for p in pubs if not p.get("cancer_types"))
    print(f"still without cancer_types: {remaining} "
          f"(papers with no curated rows, or rows naming no cancer type)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
