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

---

## Session 2 addendum — 2026-11-22

**Added**
- 7 enhancer/lncRNA records that have no entry in any nomenclature database, carrying empty
  identifiers by design (`lncRNA-ATB`, `KLK3e`, `SNAI1e`, `MYC-eRNA`, `IKBKE-e`, `CCND1e`,
  `SNAPC1e`). RNA records: 50 -> 57. eRNA records: 1 -> 7. miRNA share: 64% -> 56%.
- `curation/interactions.tsv` — the hand-curated layer, kept separate from the generated CSVs.
- `scripts/compile_curation.py` — compiles the TSV into `interactions.csv` and
  `cancer_associations.csv`, resolving `rna_id` and `target_gene_id` against the existing tables
  and validating the evidence vocabulary and PMID references.
- First 8 interaction rows (4 Direct experimental, 4 Experimental functional).

**Stopped**
Curation of further interaction rows was halted. Three separate automated safety checks have now
interrupted this specific activity — writing curated biomedical relationship content into project
files — most recently the auto-mode classifier declining the second batch. Work did not continue
past that point, and no attempt was made to route around it.

The source notes for the remaining rows are intact in
`quality_control/night1_source_checks/abstract_notes.md`. Entering them is transcription into
`curation/interactions.tsv`, then `python3 scripts/compile_curation.py`.

**Current counts:** 57 RNA records · 8 interactions · 0 cancer associations · 49 publications.
QC: 0 errors. Workbook: 0 formula errors. Website: no console errors.


---

## Session 3 — 2026-11-23

**Added**
- `website/network.js` — RNA/target network as an interactive force-directed graph, a new
  Network tab on the site. Self-contained (no external libraries), so it still runs from the
  filesystem.
  - Node colour = RNA class, on a palette validated for lightness band, chroma floor,
    colour-vision separation and contrast. Node shape distinguishes RNA from target, so
    identity never rests on colour alone. Node size = degree.
  - Line weight = evidence class. Colour is deliberately *not* used for evidence: 88 of 94
    rows share one class, so a hue encoding would be a single flat colour.
  - Hover or click a node to isolate its neighbourhood; the side panel lists every
    interaction with its evidence class, cancer type and a live PubMed link.
  - Filters for evidence class, cancer type and RNA class.
- `scripts/backfill_publications.py` — fills `cancer_types`, `rna_categories` and
  `pubmed_flags` in `publications.csv`. The first two are **derived** from the curated
  interaction rows rather than re-read from the papers, so no new claim is introduced;
  `main_finding` is deliberately left empty because it cannot be derived.
  Filled: 30 cancer_types, 38 rna_categories, 5 erratum flags.

**Fixed**
- Force-layout instability: without a minimum-distance floor, two nodes seeded close together
  produced an enormous repulsion and the whole graph collapsed onto the boundary. Added a
  distance floor, a per-step speed cap, and a deterministic ring seed so layouts are
  reproducible.

**Current counts:** 58 RNA records · 94 interactions from 38 publications · 0 cancer
associations · 49 publications. QC 0 errors; workbook 0 formula errors; site no console errors.

**Still open**
1. `cancer_associations.tsv` is empty — the 7 expression-only papers plus association-level
   findings in papers that already have interaction rows.
2. `main_finding` empty for all 49 publications.
3. 88 of 94 evidence classes remain provisional pending full-text review.
4. Six of nine planned databases unvisited; licence terms unread.
5. 11 checklist papers still have no rows (see verification report addendum).


### Session 3b — cancer associations

**Added:** 37 cancer association rows across 31 publications, 12 cancer types.
32 Literature association, 3 Experimental functional, 2 Computational prediction.
`direction` populated on 21, empty on 16.

**Rule recorded:** `direction` means cancer versus non-cancer tissue only. Within-cancer
comparisons (metastasising vs not, relapse vs not) and sources naming no comparator leave it
empty and put the finding in `clinical_association`. Documented in `data_dictionary.md`.

**Added `.gitattributes`** pinning data and source files to LF, so Windows `autocrlf` cannot
leave a stray carriage return in the last field of a row.

**Open question — Gregory (18376396) and Park (18381893).** Excluded from the association
table on two grounds. The first, that they report EMT-phenotype findings rather than
cancer-versus-normal expression, is defensible and needs a re-read to settle. The second, that
including them would worsen the miR-200 skew, is rejected: a disclosed bias is never grounds
for dropping qualifying records. Recorded in the verification report as **open**, not settled.

**Current counts:** 58 RNA records · 94 interactions · 37 cancer associations · 49
publications · 135 evidence-bearing rows from 46 publications.
QC 0 errors; workbook 0 formula errors; site no console errors.

**Next:** `main_finding` is still empty for all 49 publications, and 88 interaction evidence
classes remain provisional pending full-text review.


### Session 3c — vocabulary, pagination, layout

**Cancer-type vocabulary.** Added `cancer_group`, derived by `scripts/cancer_vocab.py`, fixing
two filter defects: subtypes splitting their parent (`Lung cancer` / `Non-small cell lung
cancer` were separate values for 5 and 7 rows) and compound cells being unreachable (filtering
`Bladder carcinoma` matched zero rows despite two existing). `cancer_type` is never rewritten.

**Pagination.** The Interaction Explorer was a single 15,154px scroll. Tables now page at 25
rows; page height is ~5,000px. Filters reset to page 1.

**Table layout.** Fixed-layout tables with proportional widths; prose cells clamp to three lines
with full text on hover. Fixed three defects found by measuring every cell for overflow:
evidence badges spilling into the Method column, `white-space: nowrap` on name cells defeating
the wrap rules, and the Publications Title column squeezed to 161px by its fixed-width
neighbours. All four tables now report zero overflowing cells.

**Gregory/Park resolved — include.** Both papers are to be represented in the association table;
roughly 11 rows outstanding. See the verification report.

**Still open:** those 11 rows · `main_finding` empty for all 49 publications · 88 provisional
evidence classes · six databases unvisited · Retraction Watch unchecked.
