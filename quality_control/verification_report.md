# Verification report — v0.1 (Night 1)

Date: 2026-11-22 · Branch: `night-1`

This report records what was **actually checked**. Nothing below is described as verified unless a
check was run and its result observed. Raw evidence is in `night1_source_checks/`.

---

## 1. Publication verification

**Method.** Every candidate PMID was submitted to the NCBI E-utilities `esummary` endpoint, and the
returned title, author list, journal and year compared against the paper the record was meant to
describe. Abstracts were then fetched with `efetch` and read.

**Result: 49 of 60 candidates confirmed.**

| Outcome | Count |
|---|---|
| Confirmed — returned record matched the intended paper | 49 |
| **Rejected** — PMID returned an unrelated paper | 10 |
| **Excluded** — flagged by PubMed as retracted | 1 |

**Rejected PMIDs:** 23636332, 19202065, 17241888, 29245010, 26982726, 24486181, 26618866, 16641100,
24843171, 23395004, 20729911.

These were candidate identifiers that proved to belong to unrelated papers — for example 24843171
returned a paper on fluid shear stress and angiogenic sprouting. **No rejected identifier was
"corrected" by guesswork.** Each was discarded and, where the intended paper was still wanted, found
again by author/title search and re-verified. This is the single most important check in the report:
every one of these would have become a fabricated citation had the metadata not been fetched.

**Excluded as retracted:** PMID 19524507 (Valastyan et al., *Cell* 2009, miR-31), carrying the
PubMed publication type `Retracted Publication`. A retraction notice for an unrelated enhancer-RNA
paper was also identified during searching and not entered.

**Not yet done.** Cross-checking against Retraction Watch. PubMed flags can lag publisher notices,
so this screening is necessary but not sufficient.

## 2. Publication-type flag screening

All 49 confirmed PMIDs were re-queried and their `pubtype` arrays scanned for `Retracted
Publication`, `Expression of Concern`, `Erratum` and `Correction`.

**Result: 0 of 49 carry a retraction or expression-of-concern flag.**

Several carry errata or published comments (for example PMID 17898713 has a *Nature* erratum and a
published comment with author reply). These were kept. An erratum is not grounds for exclusion, but
it is something a reader should see, so the `pubmed_flags` column exists to carry it. **Those flags
have not yet been written into `publications.csv`** — see §6.

## 3. Cross-source metadata check

Records retrieved from both Europe PMC and PubMed were compared.

**One discrepancy found.** For PMID 20393566 (Gupta et al., *Nature* 2010) the Europe PMC author
list repeated an author name that PubMed lists once. PubMed was treated as authoritative and the
stored record corrected.

One discrepancy in a small sample is not a verdict on either source. It is the reason for the rule
in `source_registry.md`: one source per field, rather than mixing sources within a record.

## 4. Gene identifier verification

**Method.** Every RNA and target symbol was submitted to NCBI Gene (`esearch` + `esummary`)
restricted to `9606[taxid]` and `alive[prop]`. Returned ID, description, chromosome and aliases were
recorded.

**Result: identifiers resolved for all ~100 symbols submitted.**

Symbols that returned **no** human gene record: `lncRNA-ATB`, `SCREEM2`/`SNAI1e`, `KLK3e`, the MYC
enhancer RNA, `IKBKE-e`, `CCND1e`, `SNAPC1e`. All but one are enhancer RNAs. Those records will
carry an **empty identifier by design**, with the reason in the notes field. No placeholder or
invented accession was used.

Two names required alias resolution and are noted on their records: the lncRNA published as **LED**
is `SMIM10L2A` in NCBI Gene; the eRNA published as **TMZR1-eRNA** does have a record, `TMZR1`.

## 5. Automated checks on the built tables

`scripts/qc.py` was run against the tables as built. Checks performed: duplicate detection (by name
and by identifier), identifier namespace format, symbol↔ID conflict detection, foreign-key
resolution, evidence-class vocabulary, required-field presence, and PMID-to-URL agreement.

**Result on `rna_records.csv` (50 rows) and `publications.csv` (49 rows): 0 errors, 0 warnings.**

- No duplicate RNA records by name or by identifier.
- No symbol mapped to two different gene IDs, and no gene ID shared by two symbols.
- All 50 identifiers are namespace-prefixed with numeric NCBI Gene bodies.
- All 49 publication URLs contain their own PMID.

`duplicate_audit.csv` is header-only, which records that the duplicate check ran and found nothing.

## 6. What is **not** verified

Stated plainly, because the brief asks for records not to be called verified unless they were
checked.

1. **Evidence classes are not independently verified.** They were drafted from abstracts and have
   not been confirmed against full texts. They are provisional in every case.
2. **`interactions.csv` and `cancer_associations.csv` are empty.** Schema and QC checks are in
   place; no rows have been entered. Every claim in this project about interaction counts is
   therefore currently zero, not small.
3. **`main_finding`, `cancer_types`, `rna_categories` and `pubmed_flags` in `publications.csv` are
   empty.** The underlying notes exist in `night1_source_checks/abstract_notes.md` but have not been
   transferred into the table.
4. **URLs were constructed, not fetched.** PubMed URLs were built from verified PMIDs and NCBI Gene
   URLs from verified gene IDs. The identifiers were confirmed against the respective APIs; the
   resulting URLs were not individually requested.
5. **No database beyond PubMed and NCBI Gene has been accessed.** miRTarBase, ENCORI, RNAcentral,
   LncBook, LncRNADisease and GEO remain unvisited, and their licence terms unread.

## 7. Website check

`website/index.html` was loaded in a headless browser and exercised.

| Check | Result |
|---|---|
| Console / page errors | none |
| Home statistics render from data | yes — 50 / 0 / 0 / 49 |
| RNA search (`HOTAIR`) | 1 of 50 matched, correct row returned |
| RNA class filter (`eRNA`) | 1 of 50 matched |
| Reset control | restored all 50 |
| Publication search (`enhancer`) | 9 of 49 matched |
| Publication year filter (≥ 2020) | 5 of 49 matched |
| No-match query | empty state shown, no error |
| Empty interaction table | explanatory empty state, no error |
| Outbound links | resolve to correct PubMed / DOI targets |
| Mobile layout (390 px) | renders correctly |

## 8. Workbook check

`database/master_database.xlsx` was rebuilt and recalculated via LibreOffice.

- 5 sheets: Summary, RNA Records, Interactions, Cancer Associations, Publications.
- Frozen header row and autofilter on every data sheet.
- 8 formulas, **0 formula errors**.
- Summary counts recomputed to 50 / 0 / 0 / 49, matching the CSVs.

## 9. Sampling bias in the current records

Recorded here because it affects how the data may be used.

| RNA class | Records |
|---|---|
| miRNA | 32 |
| lncRNA | 14 |
| eRNA | 1 |
| circRNA | 1 |
| pseudogene transcript | 1 |
| snoRNA host gene | 1 |

miRNAs are 64% of records. The brief asked that miRNAs not dominate simply because their databases
are easier to access, and **as it stands they do.** The cause is partly real — miRNA nomenclature is
mature and NCBI Gene covers every miRNA — and partly the gap described in `limitations.md`: most
eRNAs have no gene record to resolve, so they cannot be entered the same way.

This is a known deficiency of v0.1, not a finding about biology, and it is carried into
`PROJECT_STATUS.md` as outstanding work.

---

# Addendum — interaction table review, 2026-11-22

94 interaction rows were curated from `abstract_notes.md` in 13 batches, with
`compile_curation.py` and `qc.py` run after each. All batches compiled with 0 errors.

## Corrections made on review

Two rows from the original seed batch were **downgraded from `Direct experimental` to
`Experimental functional`**:

| Row | PMID | Reason |
|---|---|---|
| `MIR21` – `PTEN` | 17681183 | Abstract asserts a direct target but names no binding assay |
| `MIR10B` – `HOXD10` | 17898713 | Reports translational inhibition; no binding assay named |

Both were written as format examples before the rule was applied consistently, then copied as
the pattern for later rows. The rule in `methodology.md` is that a source asserting a direct
target without naming the assay gets the weaker class; these two broke it. The error was found
by re-reading the seed rows against the rule, not by any automated check — **`qc.py` validates
the evidence vocabulary but cannot tell whether a class is correct for its source.** Only
re-reading catches that.

## Evidence distribution after correction

| Class | Rows |
|---|---|
| Direct experimental | 4 |
| Experimental functional | 88 |
| Literature association | 2 |

**Four rows out of 94 carry direct experimental support.** All four name an actual binding
test: ANRIL–CBX7 (structure-guided disruption), ANRIL–SUZ12 (RIP), miR-21–PDCD4 (reporter with
site mutation), let-7a-1–HMGA2 (3'UTR site dependence with ORF rescue).

This is a result about abstract-level curation, not about the literature. Abstracts routinely
say "directly targets" without naming the method, and under the weaker-class rule that
produces `Experimental functional`. Many of those 88 rows are probably supported by direct
evidence in the full text. **No evidence class should be treated as final until full-text
review.**

## Row counts versus finding counts

94 rows come from **38 distinct publications**. Where a paper reports a result for an RNA
family, each member held in `rna_records.csv` gets a row: two miR-200 papers account for 22
rows between them.

The website now reports both numbers, and `data_dictionary.md` and `limitations.md` record the
convention. Reading rows as independent findings would overstate the evidence by roughly a
factor of two.

## Coverage

32 of the 43 checklist papers now have interaction rows. The remaining 11 do not support one:

- **Expression, prognosis or deletion only** — belong in `cancer_associations.csv`:
  12434020, 21862635, 12970751, 23243023, 17241883, 18836484, 10606244.
- **No assignable RNA–target pair:** 16461460 (Volinia) — the abstract does not say which
  miRNA the confirmed RB1 and TGFBR2 targets belong to.
- **Class-level eRNA findings with no named transcript:** 23728302, 23273978.
- **Resolved this session:** 27050392 (circHIPK3) — an RNA record has now been added, so its
  miR-124 row can be entered.

## Conventions recorded

- **Upstream regulation** reverses the reading direction of a row; `target_name` holds the
  regulator. Documented in `data_dictionary.md`.
- **Protein complexes** (PRC2, SWI/SNF, AR–MED1) and miRNA families carry `-` in the gene ID
  field rather than a guessed gene.
- **`regulatory_effect` left empty** where the source states an interaction without a
  direction. One row (H19–ANG/FGF18) had `activates` entered and then cleared on review,
  because the abstract calls these "potential" targets without stating direction.
- **Cancer type is never inferred from a cell line.** PVT1 was tested in HCT116, which is
  colorectal, but the abstract does not say so; the row reads `Not specified in abstract` with
  the cell line in notes.

---

# Addendum — cancer association table, 2026-11-23

37 rows across 31 publications, curated in 5 batches with `compile_curation.py` and `qc.py`
run after each. All batches compiled with 0 errors.

## Sourcing

Rows were taken from the **PubMed abstracts refetched during this pass**, not from
`abstract_notes.md`. The notes paraphrase in places — "~68%" appears there without its
denominator — and a paraphrase of a paraphrase loses precision at each step. Cohort counts and
wording in these rows come from the abstract text.

## Distribution

| Evidence class | Rows |
|---|---|
| Literature association | 32 |
| Experimental functional | 3 |
| Computational prediction | 2 |

`direction` is populated on 21 rows and empty on 16, under the rule now recorded in
`data_dictionary.md`: it means cancer versus non-cancer tissue, and nothing else.

## Decisions recorded

**`deleted` for Calin 2002 (PMID 12434020).** The abstract says miR15/miR16 are "deleted or
down-regulated" without separating the two. Recorded as `deleted` with the ambiguity in notes
rather than split into two rows that the source does not support.

**Partial cohort counts are labelled.** Where an abstract gives a count for only part of a
study — Kogo's 32, PCAT-1's 102, FAL1's 2,394 — `cohort_description` says which part it covers.
The "~68%" figure has no denominator in the source, so its cohort field is empty and the figure
sits in notes.

## Papers excluded, and on what grounds

- **MEG3 (17569660)** — abstract names no cancer type.
- **Cimmino, Fabbri, Asangani and nine others** — report nothing at association level beyond
  what their interaction rows already carry.
- **Volinia (16461460), circHIPK3 (27050392)** — outside the scope of this pass.

**Gregory (18376396) and Park (18381893) — excluded, and the exclusion is contested.**

Two reasons were given. The first is substantive: these papers tie miR-200 loss to the EMT
phenotype rather than to cancer-versus-normal expression or to outcome. That is a defensible
reading, though both abstracts do report loss of expression in cancer material — invasive breast
cancer lines and metaplastic breast specimens in Gregory, primary ovarian specimens in Park.

The second reason given was that including them would add 11 family-expanded rows to the
miR-200 skew that `limitations.md` already flags. **That reason is rejected.** A disclosed bias
is not grounds for excluding qualifying records. Doing so would mean `limitations.md` describes
a distribution that has been quietly corrected, and no reader could tell which rows were
dropped. Selection decisions must be recorded here, where they can be disagreed with — not
applied silently to improve a summary statistic.

**Status: open.** If these papers are re-read and still judged phenotype-marker findings rather
than cancer associations, the exclusion stands on that ground alone. Until then they are
candidates, not settled exclusions.

## Line endings

A `.gitattributes` file now pins `.tsv`, `.csv` and source files to LF in the repository.
Git's `autocrlf` on Windows was rewriting line endings on checkout, which risks a stray carriage
return inside the last field of a row. The compiler strips them, but other tools reading the
CSVs would not.
