#!/usr/bin/env python3
"""Compile curation/*.tsv into database/interactions.csv and
database/cancer_associations.csv.

The TSV files are the hand-curated layer. This script resolves rna_id and
target_gene_id against the existing tables, assigns stable local keys, and
validates the evidence vocabulary. It adds no record content of its own.
"""
import csv, os, sys
sys_path_added = os.path.dirname(os.path.abspath(__file__))
if sys_path_added not in sys.path:
    sys.path.insert(0, sys_path_added)
from cancer_vocab import groups_for

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "database")
CUR = os.path.join(ROOT, "curation")

EVIDENCE = {"Direct experimental", "Experimental functional",
            "Computational prediction", "Literature association"}



def class_sources(root):
    """Map PMID -> how its evidence class was established.

    An evidence class is only as trustworthy as the source it was read from.
    Night 1 classes came from abstracts; the full-text review either confirmed,
    upgraded or downgraded them. Several papers could not be read at all, and
    their rows still rest on an abstract. That distinction belongs in a column,
    not in prose, so a reader filtering on Direct experimental can see which
    rows have actually been checked.
    """
    path = os.path.join(root, "quality_control", "fulltext_access.csv")
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            mark = (r.get("reviewed") or "").strip().lower()
            if not mark:
                out[r["supporting_pmid"]] = "abstract (not yet reviewed)"
            elif mark.startswith("not accessed"):
                out[r["supporting_pmid"]] = "abstract (full text unavailable)"
            else:
                out[r["supporting_pmid"]] = "full text"
    return out


def load_csv(name):
    path = os.path.join(DB, name)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def read_tsv(name):
    path = os.path.join(CUR, name)
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as fh:
        header = None
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            # Accept tab- or pipe-separated rows; pipes are easier to type.
            parts = line.split("|") if ("|" in line and "\t" not in line) else line.split("\t")
            if header is None:
                header = [p.strip() for p in parts]
                continue
            parts += [""] * (len(header) - len(parts))
            rows.append(dict(zip(header, [p.strip() for p in parts])))
    return rows


def main():
    rnas = load_csv("rna_records.csv")
    pubs = load_csv("publications.csv")

    rna_by_name = {r["official_name"]: r for r in rnas}
    gene_id = {}
    for r in rnas:
        if r.get("stable_identifier"):
            gene_id[r["official_name"]] = r["stable_identifier"]
    # Target genes: read the committed NCBI Gene lookup for protein-coding targets.
    lookup = os.path.join(ROOT, "quality_control", "night1_source_checks",
                          "ncbi_gene_lookup.txt")
    import re
    with open(lookup, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or line.startswith("NOT FOUND"):
                continue
            for chunk in line.split("|"):
                m = re.match(r"\s*([A-Za-z0-9_.-]+)\s+(\d+)", chunk)
                if m:
                    gene_id.setdefault(m.group(1), "NCBIGene:" + m.group(2))

    pmids = {p["pmid"] for p in pubs}
    sources = class_sources(ROOT)
    errors = []

    # ---- interactions ----
    rows = read_tsv("interactions.tsv")
    out = []
    for i, r in enumerate(rows, start=1):
        rna = r["rna_name"]
        if rna not in rna_by_name:
            errors.append(f"interactions row {i}: unknown RNA {rna!r}")
            continue
        if r["evidence_class"] not in EVIDENCE:
            errors.append(f"interactions row {i}: bad evidence_class {r['evidence_class']!r}")
        if r["supporting_pmid"] not in pmids:
            errors.append(f"interactions row {i}: PMID {r['supporting_pmid']} not in publications.csv")
        # target_gene_id: explicit "-" means deliberately blank (complex, or not asserted)
        tgt = r.get("target_gene_id", "").strip()
        if tgt == "-":
            tgt = ""
        elif not tgt:
            tgt = gene_id.get(r["target_name"], "")
        out.append({
            "interaction_id": f"CRRA-INT-{i:04d}",
            "rna_id": rna_by_name[rna]["rna_id"],
            "rna_name": rna,
            "target_name": r["target_name"],
            "target_gene_id": tgt,
            "cancer_type": r["cancer_type"],
            "cancer_group": "; ".join(groups_for(r["cancer_type"])),
            "interaction_type": r["interaction_type"],
            "regulatory_effect": r.get("regulatory_effect", ""),
            "evidence_class": r["evidence_class"],
            "experimental_method": r.get("experimental_method", ""),
            "supporting_pmid": r["supporting_pmid"],
            "class_source": sources.get(r["supporting_pmid"], "abstract (not yet reviewed)"),
            "original_source": "PubMed abstract",
            "notes": r.get("notes", ""),
        })

    # ---- cancer associations ----
    arows = read_tsv("cancer_associations.tsv")
    aout = []
    for i, r in enumerate(arows, start=1):
        rna = r["rna_name"]
        if rna not in rna_by_name:
            errors.append(f"associations row {i}: unknown RNA {rna!r}")
            continue
        if r["evidence_class"] not in EVIDENCE:
            errors.append(f"associations row {i}: bad evidence_class {r['evidence_class']!r}")
        if r["supporting_pmid"] not in pmids:
            errors.append(f"associations row {i}: PMID {r['supporting_pmid']} not in publications.csv")
        aout.append({
            "association_id": f"CRRA-CA-{i:04d}",
            "rna_id": rna_by_name[rna]["rna_id"],
            "rna_name": rna,
            "cancer_type": r["cancer_type"],
            "cancer_group": "; ".join(groups_for(r["cancer_type"])),
            "direction": r.get("direction", ""),
            "clinical_association": r.get("clinical_association", ""),
            "evidence_class": r["evidence_class"],
            "cohort_description": r.get("cohort_description", ""),
            "supporting_pmid": r["supporting_pmid"],
            "class_source": sources.get(r["supporting_pmid"], "abstract (not yet reviewed)"),
            "notes": r.get("notes", ""),
        })

    if errors:
        print("\n".join("! " + e for e in errors), file=sys.stderr)
        print(f"{len(errors)} error(s); nothing written.", file=sys.stderr)
        return 1

    if out:
        with open(os.path.join(DB, "interactions.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, lineterminator="\n", fieldnames=list(out[0].keys()))
            w.writeheader(); w.writerows(out)
    print(f"interactions.csv: {len(out)} rows")

    if aout:
        with open(os.path.join(DB, "cancer_associations.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, lineterminator="\n", fieldnames=list(aout[0].keys()))
            w.writeheader(); w.writerows(aout)
    print(f"cancer_associations.csv: {len(aout)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
