# PROJECT_STATUS

**Version:** v0.1 (Night 1)
**Branch:** `night-1` — not merged into `main`
**Last updated:** 2026-11-22

---

## Record counts

| Table | Rows | State |
|---|---|---|
| `rna_records.csv` | 50 | Populated; every identifier resolved against NCBI Gene |
| `publications.csv` | 49 | Populated; metadata verified against PubMed |
| `interactions.csv` | **0** | Schema in place, no rows entered |
| `cancer_associations.csv` | **0** | Schema in place, no rows entered |

RNA class mix: miRNA 32 · lncRNA 14 · eRNA 1 · circRNA 1 · pseudogene transcript 1 · snoRNA host gene 1.

Literature spans 1999–2026.

## Completed

**Repository and build**
- Structure created; README expanded with the original title and description preserved verbatim.
- `scripts/derive_tables.py` — builds the RNA and publication tables from the committed verification
  records. Reshapes only; adds no record content of its own.
- `scripts/build.py` — CSVs → `website/data/data.js` + `database/master_database.xlsx`.
- `scripts/qc.py` — duplicates, identifier namespaces, symbol/ID conflicts, foreign keys,
  evidence-class vocabulary, required fields, PMID/URL agreement.
- `scripts/recalc.py` — workbook recalculation.

**Curation and verification**
- 60 candidate publications checked against PubMed E-utilities; 49 confirmed, 10 rejected as
  unrelated papers, 1 excluded as retracted (PMID 19524507).
- All 49 re-screened for retraction / expression-of-concern flags: none flagged.
- ~100 gene symbols resolved against NCBI Gene.
- Abstracts read and provisional evidence classes drafted for all 49 (in
  `quality_control/night1_source_checks/abstract_notes.md`).

**Documentation** — `project_overview.md`, `methodology.md`, `data_dictionary.md`,
`source_registry.md`, `limitations.md`, plus `quality_control/verification_report.md`.

**Website** — five sections (Home, RNA Explorer, Interaction Explorer, Publications, Methodology),
working search and filters, evidence badges, resolvable source links, responsive layout. Verified in
a headless browser: no console errors, filters and empty states behave correctly.

**Workbook** — 5 sheets, frozen header rows, autofilter, live summary formulas, 0 formula errors.

## Outstanding problems

1. **Interaction and association tables are empty.** This is the main gap in v0.1. The underlying
   relationship notes exist in `night1_source_checks/abstract_notes.md`; they have not been
   transferred into the CSVs.
2. **`publications.csv` has empty `main_finding`, `cancer_types`, `rna_categories` and
   `pubmed_flags`.** The content exists in the same notes file. The erratum flags identified in
   verification should be written into `pubmed_flags`.
3. **Evidence classes are provisional** — drafted from abstracts, not full texts.
4. **miRNAs are 64% of RNA records.** The brief asked that miRNAs not dominate through convenience
   alone, and currently they do. Partly because most eRNAs have no gene record to resolve against.
5. **Seven eRNAs have no stable identifier anywhere** and will carry empty identifier fields by
   design.
6. **Six of the nine planned databases are unvisited:** miRTarBase, ENCORI/starBase, RNAcentral,
   LncBook, LncRNADisease, GEO. Licence terms unread — this gates any public release.
7. **Retraction Watch not checked.** PubMed flags alone are necessary but not sufficient.

## Methodological decisions made

- **A rejected identifier is discarded, never corrected by guesswork.** Ten candidates were dropped
  under this rule; each would otherwise have become a fabricated citation.
- **The weaker evidence class wins** where a source asserts a relationship without naming the assay.
- **Empty means not recorded** — never zero, never a negative finding. Carried through the CSVs, the
  website (em dash with a "Not recorded" tooltip) and the workbook.
- **Identifiers are namespace-prefixed** (`NCBIGene:7157`) so provenance is never ambiguous.
- **One source per field.** Prompted by the Europe PMC / PubMed author-list discrepancy on
  PMID 20393566; PubMed is authoritative for publication metadata.
- **No bulk database downloads.** Every record came from an individual API response.
- **Retracted papers excluded; errata kept and flagged.**

## Source access notes

| Resource | Status |
|---|---|
| PubMed / NCBI E-utilities | Working via browser. Primary source. |
| NCBI Gene | Working via browser. All identifiers. |
| Europe PMC | Worked initially, then HTTP 503 (rate limited). Superseded by PubMed. |
| miRTarBase, ENCORI, RNAcentral, LncBook, LncRNADisease, GEO | Not yet accessed. |

The workspace shell has **no direct network access** to any of these hosts; the egress allowlist
refuses the connection. All lookups must go through a browser. This is a persistent constraint, not
a transient failure.

## Next session — recommended order

1. **Populate `interactions.csv`** from `abstract_notes.md`. Highest value: it is what makes the
   atlas an atlas rather than a bibliography. Enter in small batches and run `scripts/qc.py` after
   each.
2. **Populate `cancer_associations.csv`** the same way.
3. **Backfill `publications.csv`** — `main_finding`, `cancer_types`, `rna_categories`, and the
   erratum flags found during verification.
4. **Rebuild and re-verify:** `python3 scripts/derive_tables.py` is not needed again; run
   `scripts/build.py`, `scripts/qc.py`, then `scripts/recalc.py`.
5. **Address the miRNA skew** by curating lncRNA and eRNA interactions before adding more miRNAs.
6. **Record licence terms for miRTarBase and ENCORI before importing anything from them.**
7. Spot-check a sample of records against full texts and upgrade evidence classes where the method
   is named.

## File locations

```
README.md                                  Project front page
PROJECT_STATUS.md                          This file

database/rna_records.csv                   50 RNA records
database/publications.csv                  49 publications
database/interactions.csv                  Header only
database/cancer_associations.csv           Header only
database/master_database.xlsx              5-sheet workbook

website/index.html                         Open directly in a browser
website/styles.css
website/script.js
website/data/data.js                       Generated; also data.json

documentation/project_overview.md
documentation/methodology.md               Evidence classes and rules
documentation/data_dictionary.md           Column-by-column schema
documentation/source_registry.md           Per-source status and licence notes
documentation/limitations.md               Read before using the data

quality_control/verification_report.md     What was and was not checked
quality_control/duplicate_audit.csv        Header only = ran, found nothing
quality_control/night1_source_checks/      Raw PubMed / NCBI Gene records
    abstract_notes.md                      Source for the unbuilt interaction rows
    epmc_batch1.txt, pubmed_batch2.txt, pubmed_batch3.txt
    ncbi_gene_lookup.txt, final_pmids.txt

scripts/derive_tables.py                   Verification records -> CSVs
scripts/build.py                           CSVs -> website data + workbook
scripts/qc.py                              Validation; exit 1 on error
scripts/recalc.py                          Workbook recalculation
```

## Rebuilding from scratch

```bash
python3 scripts/derive_tables.py     # only if the CSVs are lost
python3 scripts/build.py
python3 scripts/qc.py
python3 scripts/recalc.py database/master_database.xlsx
open website/index.html
```

## Continuity

Each session starts with an empty workspace. The GitHub repository is the only persistent store —
nothing outside it survives. Start the next session by attaching
`potenty/cancer-regulatory-rna-atlas`, checking out `night-1`, and reading this file.
