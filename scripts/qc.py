#!/usr/bin/env python3
"""Quality-control checks for the CRRA database tables.

Writes quality_control/duplicate_audit.csv and prints a report.
Exit status 1 if any ERROR-level finding is present.

Checks performed:
  1. Duplicate RNA records (by official name, and by stable identifier)
  2. Duplicate interactions / cancer associations
  3. Identifier format consistency (namespace prefix, numeric body)
  4. One gene symbol never mapped to two different gene IDs (and vice versa)
  5. Every interaction and association has a supporting PMID that exists in publications.csv
  6. Every rna_id foreign key resolves
  7. Evidence class is one of the four permitted values, on every row that needs one
  8. Empty-vs-missing discipline: required fields are non-empty
  9. Publication URL matches its PMID
 10. Cross-table name agreement (denormalised rna_name matches rna_records)
"""
import csv, os, re, sys
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "database")
QC = os.path.join(ROOT, "quality_control")

EVIDENCE_CLASSES = {
    "Direct experimental",
    "Experimental functional",
    "Computational prediction",
    "Literature association",
}

findings = []          # (level, check, detail)
dup_rows = []          # rows for duplicate_audit.csv


def add(level, check, detail):
    findings.append((level, check, detail))


def load(name):
    path = os.path.join(DB, name)
    if not os.path.exists(path):
        add("ERROR", "table-present", f"{name} is missing")
        return None
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        add("WARN", "table-present", f"{name} has a header but no data rows")
    return rows


def dup_check(rows, key_fields, label, id_field):
    """Flag rows sharing a normalised key. Blank keys are skipped, not treated as equal."""
    seen = defaultdict(list)
    for r in rows:
        parts = [(r.get(f) or "").strip().lower() for f in key_fields]
        if not all(parts):
            continue
        seen["|".join(parts)].append(r.get(id_field, "?"))
    for key, ids in sorted(seen.items()):
        if len(ids) > 1:
            add("ERROR", "duplicate", f"{label}: {len(ids)} rows share {key_fields} = {key!r} ({', '.join(ids)})")
            dup_rows.append({
                "table": label,
                "duplicate_key": key,
                "key_fields": ";".join(key_fields),
                "row_ids": ";".join(ids),
                "count": len(ids),
            })


def check_identifier(value, field, row_id):
    """Identifiers must be namespace-prefixed, e.g. NCBIGene:7157. Empty is allowed."""
    v = (value or "").strip()
    if not v:
        return
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*:[A-Za-z0-9._-]+", v):
        add("ERROR", "identifier-format", f"{row_id}: {field} = {v!r} is not namespace-prefixed")
    elif v.startswith("NCBIGene:") and not v.split(":", 1)[1].isdigit():
        add("ERROR", "identifier-format", f"{row_id}: {field} = {v!r} has a non-numeric NCBI Gene ID")


def main():
    rnas = load("rna_records.csv")
    inter = load("interactions.csv")
    assoc = load("cancer_associations.csv")
    pubs = load("publications.csv")

    if rnas is None or inter is None or assoc is None or pubs is None:
        report()
        return 1 if any(f[0] == "ERROR" for f in findings) else 0

    # --- 1 & 2: duplicates -------------------------------------------------
    dup_check(rnas, ["official_name"], "rna_records", "rna_id")
    dup_check(rnas, ["stable_identifier"], "rna_records", "rna_id")
    dup_check(inter, ["rna_name", "target_name", "cancer_type", "supporting_pmid"],
              "interactions", "interaction_id")
    dup_check(assoc, ["rna_name", "cancer_type", "supporting_pmid"],
              "cancer_associations", "association_id")

    # --- 3: identifier format ---------------------------------------------
    for r in rnas:
        check_identifier(r.get("stable_identifier"), "stable_identifier", r.get("rna_id", "?"))
    for r in inter:
        check_identifier(r.get("target_gene_id"), "target_gene_id", r.get("interaction_id", "?"))

    # --- 4: symbol <-> id consistency -------------------------------------
    sym_to_id = defaultdict(set)
    id_to_sym = defaultdict(set)
    for r in rnas:
        s, i = (r.get("official_name") or "").strip(), (r.get("stable_identifier") or "").strip()
        if s and i:
            sym_to_id[s].add(i); id_to_sym[i].add(s)
    for r in inter:
        s, i = (r.get("target_name") or "").strip(), (r.get("target_gene_id") or "").strip()
        if s and i:
            sym_to_id[s].add(i); id_to_sym[i].add(s)
    for s, ids in sorted(sym_to_id.items()):
        if len(ids) > 1:
            add("ERROR", "identifier-conflict", f"symbol {s!r} maps to multiple IDs: {sorted(ids)}")
    for i, syms in sorted(id_to_sym.items()):
        if len(syms) > 1:
            add("WARN", "identifier-conflict", f"ID {i} used for multiple symbols: {sorted(syms)} (check alias vs. distinct gene)")

    # --- 5: supporting PMIDs ----------------------------------------------
    pmids = {(p.get("pmid") or "").strip() for p in pubs}
    for label, rows, idf in (("interactions", inter, "interaction_id"),
                             ("cancer_associations", assoc, "association_id")):
        for r in rows:
            pm = (r.get("supporting_pmid") or "").strip()
            rid = r.get(idf, "?")
            if not pm:
                add("ERROR", "missing-source", f"{label} {rid} has no supporting_pmid")
            elif not pm.isdigit():
                add("ERROR", "missing-source", f"{label} {rid} supporting_pmid {pm!r} is not numeric")
            elif pm not in pmids:
                add("ERROR", "missing-source", f"{label} {rid} cites PMID {pm}, absent from publications.csv")

    # --- 6: rna_id foreign keys -------------------------------------------
    rna_ids = {(r.get("rna_id") or "").strip() for r in rnas}
    name_by_id = {(r.get("rna_id") or "").strip(): (r.get("official_name") or "").strip() for r in rnas}
    for label, rows, idf in (("interactions", inter, "interaction_id"),
                             ("cancer_associations", assoc, "association_id")):
        for r in rows:
            k = (r.get("rna_id") or "").strip()
            rid = r.get(idf, "?")
            if not k:
                add("ERROR", "foreign-key", f"{label} {rid} has no rna_id")
            elif k not in rna_ids:
                add("ERROR", "foreign-key", f"{label} {rid} references unknown rna_id {k!r}")
            # --- 10: denormalised name agreement
            elif (r.get("rna_name") or "").strip() != name_by_id[k]:
                add("WARN", "name-mismatch",
                    f"{label} {rid}: rna_name {r.get('rna_name')!r} != rna_records {name_by_id[k]!r}")

    # --- 7: evidence class ------------------------------------------------
    for label, rows, idf in (("interactions", inter, "interaction_id"),
                             ("cancer_associations", assoc, "association_id")):
        for r in rows:
            ec = (r.get("evidence_class") or "").strip()
            rid = r.get(idf, "?")
            if not ec:
                add("ERROR", "evidence-class", f"{label} {rid} has no evidence_class")
            elif ec not in EVIDENCE_CLASSES:
                add("ERROR", "evidence-class", f"{label} {rid} has unrecognised evidence_class {ec!r}")

    # --- 8: required fields non-empty -------------------------------------
    required = {
        "rna_records": (rnas, "rna_id", ["official_name", "rna_category", "organism", "source_database", "source_url"]),
        "interactions": (inter, "interaction_id", ["target_name", "cancer_type", "interaction_type", "original_source"]),
        "cancer_associations": (assoc, "association_id", ["cancer_type"]),
        "publications": (pubs, "pmid", ["title", "authors", "journal", "year", "publication_url"]),
    }
    for label, (rows, idf, fields) in required.items():
        for r in rows:
            for f in fields:
                if not (r.get(f) or "").strip():
                    add("ERROR", "required-field", f"{label} {r.get(idf, '?')}: {f} is empty")

    # --- 9: publication URL matches PMID ----------------------------------
    for p in pubs:
        pm, url = (p.get("pmid") or "").strip(), (p.get("publication_url") or "").strip()
        if pm and url and pm not in url:
            add("ERROR", "url-mismatch", f"publication {pm}: URL {url} does not contain its PMID")

    # --- summary counts ----------------------------------------------------
    add("INFO", "counts", f"{len(rnas)} RNA records, {len(inter)} interactions, "
                          f"{len(assoc)} cancer associations, {len(pubs)} publications")
    by_class = Counter((r.get("evidence_class") or "(empty)").strip() for r in inter + assoc)
    for k, v in sorted(by_class.items()):
        add("INFO", "evidence-mix", f"{k}: {v}")
    by_cat = Counter((r.get("rna_category") or "(empty)").strip() for r in rnas)
    for k, v in sorted(by_cat.items()):
        add("INFO", "rna-mix", f"{k}: {v}")

    report()
    return 1 if any(f[0] == "ERROR" for f in findings) else 0


def report():
    os.makedirs(QC, exist_ok=True)
    with open(os.path.join(QC, "duplicate_audit.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, lineterminator="\n", fieldnames=["table", "duplicate_key", "key_fields", "row_ids", "count"])
        w.writeheader()
        for row in dup_rows:
            w.writerow(row)
    if not dup_rows:
        print("duplicate_audit.csv: no duplicates found (header only)")

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for level, check, detail in sorted(findings, key=lambda f: (order[f[0]], f[1])):
        print(f"[{level}] {check}: {detail}")
    counts = Counter(f[0] for f in findings)
    print(f"\n{counts['ERROR']} error(s), {counts['WARN']} warning(s)")


if __name__ == "__main__":
    sys.exit(main())
