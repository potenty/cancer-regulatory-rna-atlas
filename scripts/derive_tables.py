#!/usr/bin/env python3
"""Derive database/publications.csv and database/rna_records.csv from the
verification records committed under quality_control/night1_source_checks/.

This script only reshapes data that is already in the repository, retrieved from
PubMed E-utilities and NCBI Gene on 2026-11-19. It adds no record content of its
own. Fields that the verification records do not cover are written empty, which
per documentation/data_dictionary.md means "not recorded".

Run:  python3 scripts/derive_tables.py
"""
import csv, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "quality_control", "night1_source_checks")
DB = os.path.join(ROOT, "database")

METADATA_FILES = ["epmc_batch1.txt", "pubmed_batch2.txt", "pubmed_batch3.txt"]

# Which RNA category each curated symbol belongs to. Assignment is by RNA class,
# which is a property of the gene type, not a claim about any publication.
CATEGORY = {
    "miRNA": re.compile(r"^(MIR|MIRLET)"),
}
LNCRNA = {
    "HOTAIR", "MALAT1", "PVT1", "PCAT1", "SCHLAP1", "CDKN2B-AS1", "MEG3", "H19",
    "NEAT1", "CCAT1", "HULC", "FALEC", "PCA3", "SMIM10L2A",
}
ERNA = {"TMZR1"}
CIRCRNA = {"CDR1-AS"}
PSEUDOGENE = {"PTENP1"}
SNOHOST = {"GAS5"}

# Symbols in the lookup file that are protein-coding targets or upstream
# regulators, not regulatory noncoding RNAs. They belong in the interaction
# table's target columns, never in rna_records.csv.
NOT_AN_NCRNA = {
    "HIPK3", "PDCD4", "PTEN", "TP53", "HOXD10", "RHOC", "TWIST1", "BCL2", "MYC",
    "E2F1", "ZEB1", "ZEB2", "CDH1", "CDKN1B", "SOX4", "TNC", "KRAS", "NRAS",
    "HRAS", "HMGA2", "MYCN", "CD44", "DNMT3A", "DNMT3B", "EZH2", "SUZ12",
    "CBX7", "CDKN2B", "CDKN2A", "MDM2", "GDF15", "ANG", "FGF18", "ESR1", "CTCF",
    "IL11", "BMI1", "CDKN1A", "EGFR", "RAF1", "KLK3", "KLK2", "AR", "MED1",
    "SNAI1", "BRD4", "YEATS2", "IKBKE", "HDAC2", "STAT3", "CCND1", "SNAPC1",
    "RB1", "TGFBR2", "SMARCB1",
}

ALIAS_NOTE = {
    "SMIM10L2A": "Studied as the lncRNA 'LED' (PMID 25813522); NCBI Gene lists it as "
                 "SMIM10L2A with LED and LINC00086 as aliases.",
    "CDKN2B-AS1": "Widely published under the name ANRIL.",
    "PCA3": "Originally reported as DD3 (PMID 10606244).",
    "FALEC": "Published as FAL1 (PMID 25203321).",
    "CDR1-AS": "Published as ciRS-7 / CDR1as.",
    "TMZR1": "Enhancer RNA at the STAT3 locus, published as TMZR1-eRNA (PMID 39889913). "
             "One of the few eRNAs with an NCBI Gene record.",
}


def category_for(symbol):
    if CATEGORY["miRNA"].match(symbol):
        return "miRNA"
    if symbol in LNCRNA:
        return "lncRNA"
    if symbol in ERNA:
        return "eRNA"
    if symbol in CIRCRNA:
        return "circRNA"
    if symbol in PSEUDOGENE:
        return "pseudogene transcript"
    if symbol in SNOHOST:
        return "snoRNA host gene"
    return None


def parse_gene_lookup():
    """Pull SYMBOL -> gene id pairs out of the committed NCBI Gene lookup record."""
    path = os.path.join(SRC, "ncbi_gene_lookup.txt")
    pairs = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or line.startswith("NOT FOUND"):
                continue
            for chunk in line.split("|"):
                m = re.match(r"\s*([A-Za-z0-9_.-]+)\s+(\d+)", chunk)
                if m:
                    pairs[m.group(1)] = m.group(2)
    return pairs


def parse_publications():
    """Pull the PubMed-verified metadata rows out of the committed batch files."""
    rows = {}
    for fname in METADATA_FILES:
        path = os.path.join(SRC, fname)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "||" not in line:
                    continue
                parts = [p.strip() for p in line.split("||")]
                if len(parts) < 6 or not parts[0].isdigit():
                    continue
                pmid, doi, year, journal, authors, title = parts[:6]
                rows[pmid] = {
                    "pmid": pmid,
                    "doi": doi,
                    "title": title,
                    "authors": authors,
                    "journal": journal,
                    "year": year,
                }
    return rows


def main():
    keep_path = os.path.join(SRC, "final_pmids.txt")
    keep = open(keep_path, encoding="utf-8").read().split()
    keep = [k for k in keep if k.isdigit()]

    pubs = parse_publications()
    missing = [k for k in keep if k not in pubs]
    if missing:
        print(f"! metadata missing for {len(missing)} PMIDs: {missing}", file=sys.stderr)
        print("  Refusing to write partial publications.csv.", file=sys.stderr)
        return 1

    os.makedirs(DB, exist_ok=True)

    pub_fields = ["pmid", "doi", "title", "authors", "journal", "year",
                  "cancer_types", "rna_categories", "main_finding",
                  "pubmed_flags", "publication_url"]
    with open(os.path.join(DB, "publications.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=pub_fields)
        w.writeheader()
        for pmid in sorted(keep, key=lambda p: (-int(pubs[p]["year"]), pubs[p]["journal"])):
            r = dict(pubs[pmid])
            r["cancer_types"] = ""
            r["rna_categories"] = ""
            r["main_finding"] = ""
            r["pubmed_flags"] = ""
            r["publication_url"] = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            w.writerow(r)
    print(f"publications.csv: {len(keep)} rows")

    genes = parse_gene_lookup()
    rna_fields = ["rna_id", "official_name", "rna_category", "alternative_names",
                  "stable_identifier", "identifier_source", "organism",
                  "source_database", "source_url", "notes"]
    ncrnas = []
    for sym in sorted(genes):
        if sym in NOT_AN_NCRNA:
            continue
        cat = category_for(sym)
        if cat is None:
            print(f"  ? {sym}: no RNA category assigned - skipped", file=sys.stderr)
            continue
        ncrnas.append((sym, cat, genes[sym]))

    with open(os.path.join(DB, "rna_records.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=rna_fields)
        w.writeheader()
        for i, (sym, cat, gid) in enumerate(ncrnas, start=1):
            w.writerow({
                "rna_id": f"CRRA-RNA-{i:04d}",
                "official_name": sym,
                "rna_category": cat,
                "alternative_names": "",
                "stable_identifier": f"NCBIGene:{gid}",
                "identifier_source": "NCBI Gene",
                "organism": "Homo sapiens",
                "source_database": "NCBI Gene",
                "source_url": f"https://www.ncbi.nlm.nih.gov/gene/{gid}",
                "notes": ALIAS_NOTE.get(sym, ""),
            })
    print(f"rna_records.csv: {len(ncrnas)} rows")

    # Interaction and association tables are curated separately; create the
    # headers so the schema and the QC checks are in place.
    for name, fields in (
        ("interactions.csv", ["interaction_id", "rna_id", "rna_name", "target_name",
                              "target_gene_id", "cancer_type", "interaction_type",
                              "regulatory_effect", "evidence_class", "experimental_method",
                              "supporting_pmid", "original_source", "notes"]),
        ("cancer_associations.csv", ["association_id", "rna_id", "rna_name", "cancer_type",
                                     "direction", "clinical_association", "evidence_class",
                                     "cohort_description", "supporting_pmid", "notes"]),
    ):
        path = os.path.join(DB, name)
        if os.path.exists(path):
            print(f"{name}: left as is")
            continue
        with open(path, "w", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=fields).writeheader()
        print(f"{name}: header written (no rows yet)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
