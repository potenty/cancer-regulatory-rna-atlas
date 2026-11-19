# cancer-regulatory-rna-atlas
An independent, evidence-based atlas of regulatory noncoding RNA interactions in human cancer.

---

## About

The **Cancer Regulatory RNA Atlas (CRRA)** organizes published research on regulatory noncoding RNAs — microRNAs (miRNAs), long noncoding RNAs (lncRNAs), enhancer RNAs (eRNAs), and other regulatory ncRNAs (circular RNAs, pseudogene transcripts, snoRNAs) — and their relationships to cancer types, target genes, and supporting publications.

CRRA is a curated index of **existing literature**. It does not present original discoveries, and every record links back to its source publication. It is an independent project with no institutional affiliation or endorsement.

### Evidence classes

Every interaction and cancer association carries exactly one evidence class:

| Class | Meaning |
|---|---|
| **Direct experimental** | Physical/direct interaction tested, e.g. reporter assay with binding-site mutation, RNA pulldown, CLIP, RIP |
| **Experimental functional** | RNA perturbed experimentally and target/phenotype changed, without direct-binding proof |
| **Computational prediction** | Inferred by algorithm or sequence analysis only |
| **Literature association** | Expression/correlation or clinical association reported; no causal test |

See [`documentation/methodology.md`](documentation/methodology.md) for the full rules.

## Repository layout

```
website/            Static website prototype (open website/index.html)
  data/             JSON data generated from database/ CSVs
database/           CSV tables + master_database.xlsx
documentation/      Overview, methodology, source registry, data dictionary, limitations
quality_control/    Duplicate audit and verification report
scripts/            Build scripts (CSV -> JSON/XLSX, QC checks)
PROJECT_STATUS.md   Session-by-session status log
```

## Using the website locally

The site is fully static. Open `website/index.html` in a browser — data is embedded via `website/data/data.js`, so no server is required. (Alternatively: `cd website && python3 -m http.server` and visit http://localhost:8000.)

## Rebuilding data

```
python3 scripts/build.py      # CSVs -> website/data/data.js + database/master_database.xlsx
python3 scripts/qc.py         # duplicate / identifier / source checks
```

## Status

See [`PROJECT_STATUS.md`](PROJECT_STATUS.md). This is an early prototype (v0.1, Night 1).
